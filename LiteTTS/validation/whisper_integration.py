"""
Whisper STT Integration for Audio Quality Validation

This module provides Whisper model configuration and selection for automated
audio quality validation in the LiteTTS system.
"""

import logging
import time
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    WhisperModel = None

logger = logging.getLogger(__name__)


@dataclass
class WhisperConfig:
    """Configuration for Whisper model"""
    model_size: str = "base"
    device: str = "auto"  # "auto", "cpu", "cuda"
    compute_type: str = "auto"  # "auto", "float16", "int8", "float32"
    cpu_threads: int = 0  # 0 = auto
    num_workers: int = 1
    download_root: Optional[str] = None
    local_files_only: bool = False


@dataclass
class ModelLoadResult:
    """Result of model loading operation"""
    success: bool
    model_size: str
    load_time_seconds: float
    device: str
    compute_type: str
    error_message: Optional[str] = None
    model_path: Optional[str] = None


class WhisperValidator:
    """
    Whisper model validator for audio quality assessment.
    
    Provides model configuration, loading, and validation capabilities
    for automated audio quality testing in LiteTTS.
    """
    
    def __init__(self, model_size: str = "base", config: Optional[WhisperConfig] = None, auto_load: bool = True):
        """
        Initialize WhisperValidator.

        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            config: Optional WhisperConfig for advanced configuration
            auto_load: Whether to automatically load the model during initialization
        """
        if not FASTER_WHISPER_AVAILABLE:
            raise ImportError(
                "faster-whisper is not available. Please install it with: "
                "pip install faster-whisper"
            )

        self.config = config or WhisperConfig(model_size=model_size)
        self.model: Optional[WhisperModel] = None
        self.model_info: Optional[ModelLoadResult] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Validate model size
        valid_sizes = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
        if self.config.model_size not in valid_sizes:
            raise ValueError(f"Invalid model size: {self.config.model_size}. Valid sizes: {valid_sizes}")

        # Automatically load model if requested
        if auto_load:
            try:
                self.load_model()
                self.logger.info(f"WhisperValidator initialized with {model_size} model")
            except Exception as e:
                self.logger.error(f"Failed to auto-load model during initialization: {e}")
                raise
    
    def load_model(self, timeout_seconds: float = 30.0) -> ModelLoadResult:
        """
        Load Whisper model with timeout and error handling.
        
        Args:
            timeout_seconds: Maximum time to wait for model loading
            
        Returns:
            ModelLoadResult with loading status and details
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Loading Whisper model: {self.config.model_size}")
            
            # Determine device
            device = self._determine_device()
            compute_type = self._determine_compute_type(device)
            
            # Create model with timeout handling
            # Use correct parameter names for faster-whisper
            model_kwargs = {
                "model_size_or_path": self.config.model_size,
                "device": device,
                "compute_type": compute_type,
                "download_root": self.config.download_root,
                "local_files_only": self.config.local_files_only
            }

            # Add CPU thread configuration if specified
            if self.config.cpu_threads > 0:
                model_kwargs["intra_threads"] = self.config.cpu_threads

            # Remove None values to avoid parameter conflicts
            model_kwargs = {k: v for k, v in model_kwargs.items() if v is not None}

            # Load model with timeout check
            self.model = WhisperModel(**model_kwargs)
            
            load_time = time.time() - start_time
            
            # Verify model loaded successfully
            if load_time > timeout_seconds:
                error_msg = f"Model loading exceeded timeout of {timeout_seconds}s (took {load_time:.1f}s)"
                self.logger.error(error_msg)
                return ModelLoadResult(
                    success=False,
                    model_size=self.config.model_size,
                    load_time_seconds=load_time,
                    device=device,
                    compute_type=compute_type,
                    error_message=error_msg
                )
            
            # Test model with a simple transcription
            test_success = self._test_model_functionality()
            
            if not test_success:
                error_msg = "Model loaded but failed functionality test"
                self.logger.error(error_msg)
                return ModelLoadResult(
                    success=False,
                    model_size=self.config.model_size,
                    load_time_seconds=load_time,
                    device=device,
                    compute_type=compute_type,
                    error_message=error_msg
                )
            
            self.model_info = ModelLoadResult(
                success=True,
                model_size=self.config.model_size,
                load_time_seconds=load_time,
                device=device,
                compute_type=compute_type,
                model_path=str(self.model.model_path) if hasattr(self.model, 'model_path') else None
            )
            
            self.logger.info(f"✅ Whisper model loaded successfully in {load_time:.1f}s")
            self.logger.info(f"   Model: {self.config.model_size}, Device: {device}, Compute: {compute_type}")
            
            return self.model_info
            
        except Exception as e:
            load_time = time.time() - start_time
            error_msg = f"Failed to load Whisper model: {str(e)}"
            self.logger.error(error_msg)
            
            return ModelLoadResult(
                success=False,
                model_size=self.config.model_size,
                load_time_seconds=load_time,
                device=self.config.device,
                compute_type=self.config.compute_type,
                error_message=error_msg
            )
    
    def _determine_device(self) -> str:
        """Determine the best device for model execution."""
        if self.config.device != "auto":
            return self.config.device
        
        # Auto-detect best device
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
        except ImportError:
            pass
        
        return "cpu"
    
    def _determine_compute_type(self, device: str) -> str:
        """Determine the best compute type for the device."""
        if self.config.compute_type != "auto":
            return self.config.compute_type
        
        # Auto-select compute type based on device
        if device == "cuda":
            return "float16"  # Faster on GPU
        else:
            return "int8"  # More efficient on CPU
    
    def _test_model_functionality(self) -> bool:
        """Test model functionality with a simple operation."""
        try:
            if self.model is None:
                return False
            
            # Create a simple test audio (silence) to verify model works
            import numpy as np
            
            # Generate 1 second of silence at 16kHz (Whisper's expected sample rate)
            test_audio = np.zeros(16000, dtype=np.float32)
            
            # Attempt transcription
            segments, info = self.model.transcribe(test_audio, beam_size=1)
            
            # Convert generator to list to actually execute transcription
            list(segments)
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Model functionality test failed: {e}")
            return False
    
    def get_model_info(self) -> Optional[ModelLoadResult]:
        """Get information about the loaded model."""
        return self.model_info
    
    def is_model_loaded(self) -> bool:
        """Check if model is successfully loaded."""
        return self.model is not None and self.model_info is not None and self.model_info.success
    
    def transcribe_audio(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            **kwargs: Additional transcription parameters
            
        Returns:
            Dictionary with transcription results
        """
        if not self.is_model_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            start_time = time.time()
            
            # Transcribe audio
            segments, info = self.model.transcribe(audio_path, **kwargs)
            
            # Extract text from segments
            text_segments = []
            for segment in segments:
                text_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                })
            
            transcription_time = time.time() - start_time
            
            # Combine all text
            full_text = " ".join([seg["text"] for seg in text_segments]).strip()
            
            return {
                "text": full_text,
                "segments": text_segments,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "transcription_time": transcription_time,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return {
                "text": "",
                "segments": [],
                "language": "unknown",
                "language_probability": 0.0,
                "duration": 0.0,
                "transcription_time": 0.0,
                "success": False,
                "error": str(e)
            }


def create_whisper_validator(model_size: str = "base", **config_kwargs) -> WhisperValidator:
    """
    Factory function to create WhisperValidator with configuration.
    
    Args:
        model_size: Whisper model size
        **config_kwargs: Additional configuration parameters
        
    Returns:
        Configured WhisperValidator instance
    """
    config = WhisperConfig(model_size=model_size, **config_kwargs)
    return WhisperValidator(model_size=model_size, config=config)


def validate_whisper_installation() -> Dict[str, Any]:
    """
    Validate Whisper installation and capabilities.
    
    Returns:
        Dictionary with validation results
    """
    result = {
        "faster_whisper_available": FASTER_WHISPER_AVAILABLE,
        "installation_valid": False,
        "supported_models": [],
        "recommended_model": "base",
        "error_message": None
    }
    
    if not FASTER_WHISPER_AVAILABLE:
        result["error_message"] = "faster-whisper not installed"
        return result
    
    try:
        # Test basic model loading
        validator = WhisperValidator("tiny")  # Use smallest model for quick test
        load_result = validator.load_model(timeout_seconds=30.0)
        
        if load_result.success:
            result["installation_valid"] = True
            result["supported_models"] = ["tiny", "base", "small", "medium", "large"]
            result["test_load_time"] = load_result.load_time_seconds
            result["test_device"] = load_result.device
            result["test_compute_type"] = load_result.compute_type
        else:
            result["error_message"] = load_result.error_message
            
    except Exception as e:
        result["error_message"] = f"Validation failed: {str(e)}"
    
    return result
