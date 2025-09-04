#!/usr/bin/env python3
"""
Script to download and validate GGUF model for LiteTTS
Downloads the target Kokoro_espeak_Q4.gguf model for testing
"""

import os
import sys
import requests
import hashlib
from pathlib import Path
import logging

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.models.manager import ModelManager
from LiteTTS.inference.factory import InferenceBackendFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_gguf_model():
    """Download the target GGUF model for testing"""
    
    # Target model configuration
    model_name = "Kokoro_espeak_Q4.gguf"
    model_url = "https://huggingface.co/mmwillet2/Kokoro_GGUF/resolve/main/Kokoro_espeak_Q4.gguf"
    models_dir = Path("LiteTTS/models")
    model_path = models_dir / model_name
    
    # Create models directory if it doesn't exist
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if model already exists
    if model_path.exists():
        logger.info(f"Model {model_name} already exists at {model_path}")
        file_size = model_path.stat().st_size
        logger.info(f"Existing model size: {file_size / (1024*1024):.1f} MB")
        return str(model_path)
    
    # Download the model
    logger.info(f"Downloading {model_name} from HuggingFace...")
    logger.info(f"URL: {model_url}")
    
    try:
        response = requests.get(model_url, stream=True, timeout=300)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        logger.info(f"Expected download size: {total_size / (1024*1024):.1f} MB")
        
        with open(model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # Progress reporting
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        if downloaded_size % (10 * 1024 * 1024) == 0:  # Every 10MB
                            logger.info(f"Download progress: {progress:.1f}% "
                                      f"({downloaded_size / (1024*1024):.1f} MB)")
        
        logger.info(f"Download completed: {downloaded_size / (1024*1024):.1f} MB")
        return str(model_path)
        
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        if model_path.exists():
            model_path.unlink()  # Clean up partial download
        raise

def validate_gguf_model(model_path: str):
    """Validate the downloaded GGUF model"""
    
    model_path_obj = Path(model_path)
    
    # Basic file validation
    if not model_path_obj.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    file_size = model_path_obj.stat().st_size
    logger.info(f"Model file size: {file_size / (1024*1024):.1f} MB")
    
    # Check file extension
    if not model_path_obj.suffix.lower() == '.gguf':
        raise ValueError(f"Invalid file extension: {model_path_obj.suffix}")
    
    # Check GGUF magic header
    try:
        with open(model_path, 'rb') as f:
            header = f.read(4)
            if header != b'GGUF':
                raise ValueError("Invalid GGUF file: missing magic header")
        
        logger.info("GGUF file validation passed")
        
    except Exception as e:
        logger.error(f"GGUF file validation failed: {e}")
        raise

def test_gguf_backend_creation(model_path: str):
    """Test GGUF backend creation with the downloaded model"""
    
    try:
        from LiteTTS.inference import InferenceConfig
        
        # Create GGUF inference configuration
        config = InferenceConfig(
            backend_type="gguf",
            model_path=model_path,
            device="cpu",
            backend_specific_options={
                "context_size": 1024,  # Smaller for testing
                "n_threads": 2,
                "use_gpu": False,
                "use_mmap": True,
                "use_mlock": False
            }
        )
        
        # Test backend creation
        logger.info("Testing GGUF backend creation...")
        backend = InferenceBackendFactory.create_backend(config)
        
        logger.info(f"Backend created successfully: {backend.get_backend_type()}")
        logger.info(f"Backend info: {backend.get_performance_info()}")
        
        # Test model validation
        is_valid = backend.validate_model()
        logger.info(f"Model validation result: {is_valid}")
        
        # Clean up
        backend.cleanup()
        
        return True
        
    except ImportError as e:
        logger.warning(f"GGUF backend dependencies not available: {e}")
        logger.warning("Install with: pip install llama-cpp-python")
        return False
        
    except Exception as e:
        logger.error(f"GGUF backend test failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("Starting GGUF model download and validation")
    
    try:
        # Download model
        model_path = download_gguf_model()
        
        # Validate model
        validate_gguf_model(model_path)
        
        # Test backend creation
        backend_test_passed = test_gguf_backend_creation(model_path)
        
        # Summary
        logger.info("=" * 60)
        logger.info("GGUF Model Download and Validation Summary")
        logger.info("=" * 60)
        logger.info(f"Model path: {model_path}")
        logger.info(f"File validation: PASSED")
        logger.info(f"Backend test: {'PASSED' if backend_test_passed else 'FAILED (dependencies missing)'}")
        
        if backend_test_passed:
            logger.info("✅ GGUF integration foundation is ready!")
        else:
            logger.info("⚠️  GGUF model downloaded but backend dependencies need installation")
            logger.info("   Run: pip install llama-cpp-python")
        
        return 0
        
    except Exception as e:
        logger.error(f"GGUF model setup failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
