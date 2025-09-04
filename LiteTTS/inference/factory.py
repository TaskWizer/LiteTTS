#!/usr/bin/env python3
"""
Inference backend factory for LiteTTS
Handles creation and selection of appropriate inference backends
"""

from typing import Dict, Type, Optional, Any
from pathlib import Path
import logging

from .base import BaseInferenceBackend, InferenceConfig
from .onnx_backend import ONNXInferenceBackend
from .ttscpp_backend import TTSCppBackend

logger = logging.getLogger(__name__)

class InferenceBackendFactory:
    """Factory for creating inference backends"""
    
    # Registry of available backends
    _backends: Dict[str, Type[BaseInferenceBackend]] = {
        "onnx": ONNXInferenceBackend,
        "gguf": TTSCppBackend
    }
    
    @classmethod
    def create_backend(cls, config: InferenceConfig) -> BaseInferenceBackend:
        """
        Create an inference backend based on configuration (no fallback mechanisms)

        Args:
            config: Inference configuration

        Returns:
            BaseInferenceBackend: Configured backend instance

        Raises:
            ValueError: If backend type is not supported
            RuntimeError: If backend creation fails
        """
        return cls.create_backend_strict(config)
    
    @classmethod
    def auto_detect_backend(cls, model_path: str, preferred_backend: Optional[str] = None) -> str:
        """
        Automatically detect the appropriate backend for a model

        Args:
            model_path: Path to the model file
            preferred_backend: Preferred backend type (if any)

        Returns:
            str: Detected backend type
        """
        logger.info(f"🔍 Auto-detecting backend for model: {model_path}")
        logger.info(f"🎯 Preferred backend: {preferred_backend}")

        model_path_obj = Path(model_path)
        logger.info(f"📁 Model path object: {model_path_obj.absolute()}")

        if not model_path_obj.exists():
            logger.error(f"❌ Model file not found: {model_path_obj.absolute()}")
            raise FileNotFoundError(f"Model file not found: {model_path}")
        else:
            logger.info(f"✅ Model file exists: {model_path_obj.absolute()}")

        # Check file extension
        extension = model_path_obj.suffix.lower()
        logger.info(f"📋 File extension: '{extension}'")

        if extension == ".onnx":
            detected_backend = "onnx"
            logger.info(f"🎯 Detected ONNX backend based on extension")
        elif extension == ".gguf":
            detected_backend = "gguf"
            logger.info(f"🎯 Detected GGUF backend based on extension")
        else:
            # Try to detect based on file content or other heuristics
            logger.info(f"🔍 Unknown extension, detecting by content...")
            detected_backend = cls._detect_by_content(model_path_obj)
            logger.info(f"🎯 Content-based detection result: {detected_backend}")

        # Use preferred backend if specified and compatible
        if preferred_backend:
            preferred_backend = preferred_backend.lower()
            logger.info(f"🔄 Checking preferred backend: {preferred_backend}")
            if preferred_backend in cls._backends:
                # Validate that preferred backend can handle the model
                logger.info(f"🔍 Validating backend compatibility...")
                if cls._validate_backend_compatibility(model_path_obj, preferred_backend):
                    logger.info(f"✅ Using preferred backend '{preferred_backend}' for {model_path}")
                    return preferred_backend
                else:
                    logger.warning(f"❌ Preferred backend '{preferred_backend}' not compatible with {model_path}, "
                                 f"using detected backend '{detected_backend}'")
            else:
                logger.warning(f"❌ Preferred backend '{preferred_backend}' not available in registry")

        logger.info(f"✅ Auto-detected backend '{detected_backend}' for {model_path}")
        return detected_backend
    
    @classmethod
    def _detect_by_content(cls, model_path: Path) -> str:
        """
        Detect backend by examining file content

        Args:
            model_path: Path to model file

        Returns:
            str: Detected backend type
        """
        logger.info(f"🔍 Content-based detection for: {model_path}")
        try:
            # Read first few bytes to detect file format
            with open(model_path, 'rb') as f:
                header = f.read(16)

            logger.info(f"📋 File header (first 16 bytes): {header}")

            # ONNX files typically start with specific magic bytes
            if header.startswith(b'\x08\x01\x12'):  # ONNX protobuf header
                logger.info(f"✅ Detected ONNX format by header")
                return "onnx"

            # GGUF files have a specific magic number
            if header.startswith(b'GGUF'):
                logger.info(f"✅ Detected GGUF format by header")
                return "gguf"

            # Default fallback based on file size and extension guessing
            file_size = model_path.stat().st_size
            logger.info(f"📊 File size: {file_size / (1024*1024):.1f} MB")

            # Heuristic: GGUF files are often smaller due to quantization
            if file_size < 200 * 1024 * 1024:  # Less than 200MB
                logger.info(f"🎯 Small file size, assuming GGUF")
                return "gguf"
            else:
                logger.info(f"🎯 Large file size, assuming ONNX")
                return "onnx"

        except Exception as e:
            logger.warning(f"❌ Content-based detection failed for {model_path}: {e}")
            return "onnx"  # Default fallback
    
    @classmethod
    def _validate_backend_compatibility(cls, model_path: Path, backend_type: str) -> bool:
        """
        Validate that a backend can handle a specific model
        
        Args:
            model_path: Path to model file
            backend_type: Backend type to validate
            
        Returns:
            bool: True if backend is compatible
        """
        try:
            if backend_type not in cls._backends:
                return False
            
            # Create a temporary config for validation
            temp_config = InferenceConfig(
                backend_type=backend_type,
                model_path=str(model_path)
            )
            
            # Create backend instance and validate model
            backend_class = cls._backends[backend_type]
            backend = backend_class(temp_config)
            
            is_valid = backend.validate_model()
            
            # Clean up
            del backend
            
            return is_valid
            
        except Exception as e:
            logger.debug(f"Backend compatibility check failed for {backend_type}: {e}")
            return False
    
    @classmethod
    def get_available_backends(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available backends
        
        Returns:
            Dict mapping backend names to their information
        """
        backend_info = {}
        
        for name, backend_class in cls._backends.items():
            try:
                # Create a dummy config to get backend info
                dummy_config = InferenceConfig(
                    backend_type=name,
                    model_path="/dummy/path"
                )
                
                # Get basic info without loading a model
                backend = backend_class(dummy_config)
                
                backend_info[name] = {
                    "class": backend_class.__name__,
                    "supports_cpu": backend.supports_device("cpu"),
                    "supports_cuda": backend.supports_device("cuda"),
                    "description": backend_class.__doc__ or f"{name.upper()} inference backend"
                }
                
                # Clean up
                del backend
                
            except Exception as e:
                backend_info[name] = {
                    "class": backend_class.__name__,
                    "error": str(e),
                    "available": False
                }
        
        return backend_info
    
    @classmethod
    def register_backend(cls, name: str, backend_class: Type[BaseInferenceBackend]):
        """
        Register a new backend type
        
        Args:
            name: Backend name
            backend_class: Backend implementation class
        """
        if not issubclass(backend_class, BaseInferenceBackend):
            raise ValueError(f"Backend class must inherit from BaseInferenceBackend")
        
        cls._backends[name.lower()] = backend_class
        logger.info(f"Registered new backend: {name}")
    
    @classmethod
    def create_backend_strict(cls, config: InferenceConfig) -> BaseInferenceBackend:
        """
        Create backend without any fallback mechanisms - fails explicitly on errors

        Args:
            config: Backend configuration

        Returns:
            BaseInferenceBackend: Configured backend instance

        Raises:
            ValueError: If backend type is not supported
            RuntimeError: If backend creation fails
        """
        backend_type = config.backend_type.lower()

        if backend_type not in cls._backends:
            available_backends = list(cls._backends.keys())
            raise ValueError(f"Unsupported backend type: {backend_type}. "
                           f"Available backends: {available_backends}. "
                           f"No fallback mechanisms available.")

        try:
            backend_class = cls._backends[backend_type]
            backend = backend_class(config)

            logger.info(f"Created {backend_type} backend for model: {config.model_path}")
            logger.info("No fallback mechanisms enabled - backend must work or fail explicitly")
            return backend

        except Exception as e:
            logger.error(f"Failed to create {backend_type} backend: {e}")
            logger.error("No fallback mechanisms available. Fix the underlying issue.")
            raise RuntimeError(f"Backend creation failed: {e}. No fallback available.")
    
    @classmethod
    def benchmark_backends(cls, model_path: str, test_inputs: Optional[Any] = None) -> Dict[str, Dict[str, Any]]:
        """
        Benchmark available backends for a specific model
        
        Args:
            model_path: Path to model file
            test_inputs: Optional test inputs for benchmarking
            
        Returns:
            Dict with benchmark results for each backend
        """
        results = {}
        
        # Detect compatible backends
        compatible_backends = []
        for backend_name in cls._backends.keys():
            if cls._validate_backend_compatibility(Path(model_path), backend_name):
                compatible_backends.append(backend_name)
        
        logger.info(f"Benchmarking compatible backends: {compatible_backends}")
        
        for backend_name in compatible_backends:
            try:
                config = InferenceConfig(
                    backend_type=backend_name,
                    model_path=model_path
                )
                
                backend = cls.create_backend(config)
                
                # Basic performance info
                results[backend_name] = {
                    "compatible": True,
                    "memory_estimate": backend.estimate_memory_usage(),
                    "performance_info": backend.get_performance_info(),
                    "model_info": backend.get_model_info() if backend.is_model_loaded() else {}
                }
                
                backend.cleanup()
                
            except Exception as e:
                results[backend_name] = {
                    "compatible": False,
                    "error": str(e)
                }
        
        return results
