#!/usr/bin/env python3
"""
ONNX inference backend for LiteTTS
Wraps existing ONNX functionality in the new backend interface
"""

import numpy as np
import onnxruntime as ort
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from .base import BaseInferenceBackend, InferenceConfig, ModelInputs, ModelOutputs

logger = logging.getLogger(__name__)

class ONNXInferenceBackend(BaseInferenceBackend):
    """ONNX inference backend implementation"""
    
    def __init__(self, config: InferenceConfig):
        super().__init__(config)
        self.session = None
        self.input_names = []
        self.output_names = []
        self.providers = config.providers or self._get_default_providers()
        
    def _get_default_providers(self) -> List[str]:
        """Get default ONNX providers based on device and availability"""
        providers = []
        
        if self.device == "cuda" and "CUDAExecutionProvider" in ort.get_available_providers():
            providers.append("CUDAExecutionProvider")
        
        providers.append("CPUExecutionProvider")
        return providers
    
    def load_model(self) -> bool:
        """Load the ONNX model"""
        try:
            if not self.model_path.exists():
                logger.error(f"ONNX model not found: {self.model_path}")
                return False
            
            if not self.validate_model():
                logger.error(f"ONNX model validation failed: {self.model_path}")
                return False
            
            # Configure session options
            session_options = ort.SessionOptions()
            session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            
            # Apply custom session options if provided
            if self.config.session_options:
                for key, value in self.config.session_options.items():
                    if hasattr(session_options, key):
                        # Handle special case for graph_optimization_level
                        if key == 'graph_optimization_level' and isinstance(value, str):
                            # Convert string to proper enum value
                            if value == 'ORT_ENABLE_ALL':
                                value = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                            elif value == 'ORT_ENABLE_BASIC':
                                value = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
                            elif value == 'ORT_ENABLE_EXTENDED':
                                value = ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
                            elif value == 'ORT_DISABLE_ALL':
                                value = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
                        setattr(session_options, key, value)
            
            # Create ONNX session
            self.session = ort.InferenceSession(
                str(self.model_path),
                sess_options=session_options,
                providers=self.providers
            )
            
            # Cache input/output names
            self.input_names = [input.name for input in self.session.get_inputs()]
            self.output_names = [output.name for output in self.session.get_outputs()]
            
            # Update model info
            self.model_info = {
                "model_path": str(self.model_path),
                "providers": self.session.get_providers(),
                "input_names": self.input_names,
                "output_names": self.output_names,
                "input_specs": self.get_input_specs(),
                "output_specs": self.get_output_specs()
            }
            
            self.is_loaded = True
            logger.info(f"ONNX model loaded successfully: {self.model_path}")
            logger.info(f"Using providers: {self.session.get_providers()}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")
            self.session = None
            self.is_loaded = False
            return False
    
    def unload_model(self) -> bool:
        """Unload the ONNX model"""
        try:
            if self.session:
                # ONNX sessions don't need explicit cleanup, just clear reference
                self.session = None
            
            self.input_names = []
            self.output_names = []
            self.model_info = {}
            self.is_loaded = False
            
            logger.info("ONNX model unloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload ONNX model: {e}")
            return False
    
    def run_inference(self, inputs: ModelInputs) -> ModelOutputs:
        """Run ONNX inference"""
        if not self.is_loaded or not self.session:
            raise RuntimeError("ONNX model not loaded")
        
        if not self.validate_inputs(inputs):
            raise ValueError("Invalid inputs for ONNX inference")
        
        try:
            # Prepare ONNX inputs
            onnx_inputs = self._prepare_onnx_inputs(inputs)
            
            # Run inference
            logger.debug("Running ONNX inference...")
            raw_outputs = self.session.run(None, onnx_inputs)
            
            # Validate outputs
            if not raw_outputs or len(raw_outputs) == 0:
                raise RuntimeError("ONNX model returned no outputs")
            
            # Post-process outputs
            outputs = self._process_onnx_outputs(raw_outputs)
            
            logger.debug(f"ONNX inference completed: output shape={outputs.audio.shape}")
            return outputs
            
        except Exception as e:
            logger.error(f"ONNX inference failed: {e}")
            raise
    
    def _prepare_onnx_inputs(self, inputs: ModelInputs) -> Dict[str, np.ndarray]:
        """Prepare inputs for ONNX session"""
        onnx_inputs = {}
        
        # Map standardized inputs to ONNX input names
        input_mapping = {
            "input_ids": inputs.input_ids,
            "style": inputs.style,
            "speed": inputs.speed
        }
        
        # Add additional inputs if provided
        if inputs.additional_inputs:
            input_mapping.update(inputs.additional_inputs)
        
        # Match inputs to expected ONNX input names
        for name in self.input_names:
            if name in input_mapping:
                onnx_inputs[name] = input_mapping[name]
                logger.debug(f"ONNX input '{name}' shape: {input_mapping[name].shape}, "
                           f"dtype: {input_mapping[name].dtype}")
            else:
                logger.warning(f"Missing ONNX input: {name}")
        
        # Validate all required inputs are present
        missing_inputs = set(self.input_names) - set(onnx_inputs.keys())
        if missing_inputs:
            raise ValueError(f"Missing required ONNX inputs: {missing_inputs}")
        
        return onnx_inputs
    
    def _process_onnx_outputs(self, raw_outputs: List[np.ndarray]) -> ModelOutputs:
        """Process ONNX outputs into standardized format"""
        # Assume first output is audio data
        audio_output = raw_outputs[0]
        
        # Validate output
        if audio_output.size == 0:
            raise RuntimeError("ONNX model returned empty audio output")
        
        # Ensure audio is in the right format
        if audio_output.ndim > 1:
            audio_output = audio_output.flatten()
        
        # Convert to float32 if needed
        if audio_output.dtype != np.float32:
            audio_output = audio_output.astype(np.float32)
        
        # Handle invalid values
        if np.any(np.isnan(audio_output)):
            logger.warning("ONNX output contains NaN values, replacing with zeros")
            audio_output = np.nan_to_num(audio_output, nan=0.0)
        
        if np.any(np.isinf(audio_output)):
            logger.warning("ONNX output contains infinite values, clipping")
            audio_output = np.clip(audio_output, -1.0, 1.0)
        
        return ModelOutputs(
            audio=audio_output,
            sample_rate=24000,  # Default sample rate for Kokoro
            metadata={
                "backend": "onnx",
                "providers": self.session.get_providers(),
                "output_shape": audio_output.shape,
                "output_dtype": str(audio_output.dtype)
            }
        )
    
    def validate_model(self) -> bool:
        """Validate ONNX model file"""
        try:
            if not self.model_path.exists():
                return False
            
            if not self.model_path.suffix.lower() == '.onnx':
                return False
            
            # Try to create a session to validate the model
            test_session = ort.InferenceSession(str(self.model_path), providers=["CPUExecutionProvider"])
            test_session = None  # Clean up
            
            return True
            
        except Exception as e:
            logger.error(f"ONNX model validation failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get ONNX model information"""
        return self.model_info.copy()
    
    def get_input_specs(self) -> Dict[str, Dict[str, Any]]:
        """Get ONNX input specifications"""
        if not self.session:
            return {}
        
        specs = {}
        for input_meta in self.session.get_inputs():
            specs[input_meta.name] = {
                "shape": input_meta.shape,
                "dtype": input_meta.type,
                "name": input_meta.name
            }
        
        return specs
    
    def get_output_specs(self) -> Dict[str, Dict[str, Any]]:
        """Get ONNX output specifications"""
        if not self.session:
            return {}
        
        specs = {}
        for output_meta in self.session.get_outputs():
            specs[output_meta.name] = {
                "shape": output_meta.shape,
                "dtype": output_meta.type,
                "name": output_meta.name
            }
        
        return specs
    
    def supports_device(self, device: str) -> bool:
        """Check if ONNX backend supports the device"""
        device_lower = device.lower()
        
        if device_lower == "cpu":
            return True
        elif device_lower == "cuda":
            return "CUDAExecutionProvider" in ort.get_available_providers()
        else:
            return False
    
    def estimate_memory_usage(self) -> Dict[str, int]:
        """Estimate ONNX model memory usage"""
        if not self.model_path.exists():
            return {"model_size": 0, "runtime_overhead": 0, "peak_inference": 0}
        
        model_size = self.model_path.stat().st_size
        
        # Rough estimates based on typical ONNX runtime overhead
        runtime_overhead = int(model_size * 0.2)  # 20% overhead
        peak_inference = int(model_size * 0.5)    # 50% for inference buffers
        
        return {
            "model_size": model_size,
            "runtime_overhead": runtime_overhead,
            "peak_inference": peak_inference
        }
    
    def get_performance_info(self) -> Dict[str, Any]:
        """Get ONNX performance information"""
        base_info = super().get_performance_info()
        base_info.update({
            "providers": self.session.get_providers() if self.session else [],
            "supports_batching": True,
            "supports_streaming": False,
            "optimization_level": "ORT_ENABLE_ALL"
        })
        return base_info
