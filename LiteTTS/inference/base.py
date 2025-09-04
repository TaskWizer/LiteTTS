#!/usr/bin/env python3
"""
Base inference backend interface for LiteTTS
Provides abstract interface for different model inference backends
"""

import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class InferenceConfig:
    """Configuration for inference backend"""
    backend_type: str  # "onnx", "gguf"
    model_path: str
    device: str = "cpu"
    providers: Optional[List[str]] = None
    session_options: Optional[Dict[str, Any]] = None
    backend_specific_options: Optional[Dict[str, Any]] = None

@dataclass
class ModelInputs:
    """Standardized model inputs across backends"""
    input_ids: np.ndarray
    style: np.ndarray
    speed: np.ndarray
    attention_mask: Optional[np.ndarray] = None
    additional_inputs: Optional[Dict[str, np.ndarray]] = None

@dataclass
class ModelOutputs:
    """Standardized model outputs across backends"""
    audio: np.ndarray
    sample_rate: int
    metadata: Optional[Dict[str, Any]] = None

class BaseInferenceBackend(ABC):
    """Abstract base class for inference backends"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.model_path = Path(config.model_path)
        self.device = config.device
        self.is_loaded = False
        self.model_info = {}
        
    @abstractmethod
    def load_model(self) -> bool:
        """
        Load the model for inference
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def unload_model(self) -> bool:
        """
        Unload the model and free resources
        
        Returns:
            bool: True if model unloaded successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def run_inference(self, inputs: ModelInputs) -> ModelOutputs:
        """
        Run inference on the model
        
        Args:
            inputs: Standardized model inputs
            
        Returns:
            ModelOutputs: Standardized model outputs
            
        Raises:
            RuntimeError: If model is not loaded or inference fails
        """
        pass
    
    @abstractmethod
    def validate_model(self) -> bool:
        """
        Validate that the model file is compatible with this backend
        
        Returns:
            bool: True if model is valid for this backend
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        
        Returns:
            Dict containing model metadata
        """
        pass
    
    @abstractmethod
    def get_input_specs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get input specifications for the model
        
        Returns:
            Dict mapping input names to their specifications (shape, dtype, etc.)
        """
        pass
    
    @abstractmethod
    def get_output_specs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get output specifications for the model
        
        Returns:
            Dict mapping output names to their specifications (shape, dtype, etc.)
        """
        pass
    
    def is_model_loaded(self) -> bool:
        """Check if model is currently loaded"""
        return self.is_loaded
    
    def get_backend_type(self) -> str:
        """Get the backend type identifier"""
        return self.config.backend_type
    
    def supports_device(self, device: str) -> bool:
        """
        Check if backend supports the specified device
        
        Args:
            device: Device identifier (cpu, cuda, etc.)
            
        Returns:
            bool: True if device is supported
        """
        # Default implementation - subclasses should override
        return device.lower() == "cpu"
    
    def estimate_memory_usage(self) -> Dict[str, int]:
        """
        Estimate memory usage for the model
        
        Returns:
            Dict with memory estimates in bytes
        """
        # Default implementation - subclasses should override
        return {
            "model_size": 0,
            "runtime_overhead": 0,
            "peak_inference": 0
        }
    
    def get_performance_info(self) -> Dict[str, Any]:
        """
        Get performance-related information
        
        Returns:
            Dict with performance metrics and capabilities
        """
        return {
            "backend_type": self.get_backend_type(),
            "device": self.device,
            "model_loaded": self.is_loaded,
            "supports_batching": False,
            "supports_streaming": False,
            "memory_usage": self.estimate_memory_usage()
        }
    
    def prepare_inputs(self, input_ids: np.ndarray, style: np.ndarray, 
                      speed: np.ndarray, **kwargs) -> ModelInputs:
        """
        Prepare standardized inputs for inference
        
        Args:
            input_ids: Tokenized input sequence
            style: Voice style embedding
            speed: Speed parameter
            **kwargs: Additional backend-specific inputs
            
        Returns:
            ModelInputs: Standardized input structure
        """
        return ModelInputs(
            input_ids=input_ids,
            style=style,
            speed=speed,
            additional_inputs=kwargs
        )
    
    def validate_inputs(self, inputs: ModelInputs) -> bool:
        """
        Validate that inputs are compatible with the model
        
        Args:
            inputs: Model inputs to validate
            
        Returns:
            bool: True if inputs are valid
        """
        try:
            # Basic validation - subclasses can override for specific checks
            if inputs.input_ids is None or inputs.input_ids.size == 0:
                logger.error("Invalid input_ids: empty or None")
                return False
                
            if inputs.style is None or inputs.style.size == 0:
                logger.error("Invalid style: empty or None")
                return False
                
            if inputs.speed is None or inputs.speed.size == 0:
                logger.error("Invalid speed: empty or None")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return False
    
    def post_process_outputs(self, raw_outputs: Any) -> ModelOutputs:
        """
        Post-process raw model outputs into standardized format
        
        Args:
            raw_outputs: Raw outputs from model inference
            
        Returns:
            ModelOutputs: Standardized output structure
        """
        # Default implementation - subclasses should override
        if isinstance(raw_outputs, np.ndarray):
            return ModelOutputs(
                audio=raw_outputs,
                sample_rate=24000,  # Default sample rate
                metadata={"backend": self.get_backend_type()}
            )
        else:
            raise ValueError(f"Unsupported output type: {type(raw_outputs)}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.is_loaded:
            self.unload_model()
    
    def __enter__(self):
        """Context manager entry"""
        self.load_model()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
    
    def __del__(self):
        """Destructor"""
        self.cleanup()
