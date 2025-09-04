#!/usr/bin/env python3
"""
Comprehensive validation test for native GGUF implementation
Ensures no fallback mechanisms are used and GGUF works natively
"""

import sys
import os
import logging
import numpy as np
from pathlib import Path

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.inference.factory import InferenceBackendFactory
from LiteTTS.inference.base import InferenceConfig, ModelInputs
from LiteTTS.tts.engine import KokoroTTSEngine
from LiteTTS.config import TTSConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GGUFValidationTest:
    """Comprehensive GGUF validation test suite"""
    
    def __init__(self):
        self.model_path = Path("LiteTTS/models/Kokoro_espeak_Q4.gguf")
        self.test_results = {}
        
    def run_all_tests(self):
        """Run all validation tests"""
        logger.info("Starting comprehensive GGUF validation tests")
        logger.info("=" * 60)
        
        tests = [
            ("test_gguf_model_exists", self.test_gguf_model_exists),
            ("test_native_gguf_backend_creation", self.test_native_gguf_backend_creation),
            ("test_tensor_name_mapping", self.test_tensor_name_mapping),
            ("test_no_fallback_mechanisms", self.test_no_fallback_mechanisms),
            ("test_gguf_model_loading", self.test_gguf_model_loading),
            ("test_gguf_inference_pipeline", self.test_gguf_inference_pipeline),
            ("test_tts_engine_gguf_only", self.test_tts_engine_gguf_only),
            ("test_audio_generation", self.test_audio_generation),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                logger.info(f"\n--- Running {test_name} ---")
                result = test_func()
                if result:
                    logger.info(f"✅ {test_name} PASSED")
                    self.test_results[test_name] = "PASSED"
                    passed += 1
                else:
                    logger.error(f"❌ {test_name} FAILED")
                    self.test_results[test_name] = "FAILED"
                    failed += 1
            except Exception as e:
                logger.error(f"❌ {test_name} FAILED with exception: {e}")
                self.test_results[test_name] = f"FAILED: {e}"
                failed += 1
        
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total tests: {len(tests)}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        
        if failed == 0:
            logger.info("🎉 ALL TESTS PASSED - Native GGUF implementation is working!")
            return True
        else:
            logger.error(f"💥 {failed} tests failed - Native GGUF implementation needs fixes")
            return False
    
    def test_gguf_model_exists(self):
        """Test that the GGUF model file exists"""
        if not self.model_path.exists():
            logger.error(f"GGUF model not found: {self.model_path}")
            return False
        
        file_size = self.model_path.stat().st_size
        logger.info(f"GGUF model found: {self.model_path} ({file_size:,} bytes)")
        return True
    
    def test_native_gguf_backend_creation(self):
        """Test that native GGUF backend can be created"""
        try:
            config = InferenceConfig(
                backend_type="gguf",
                model_path=str(self.model_path)
            )
            
            backend = InferenceBackendFactory.create_backend_strict(config)
            
            # Verify it's using native GGUF implementation
            if not hasattr(backend, 'gguf_reader'):
                logger.error("Backend doesn't have gguf_reader - not using native implementation")
                return False
            
            if hasattr(backend, 'model') and backend.model is not None:
                logger.error("Backend has llama-cpp-python model - using fallback implementation")
                return False
            
            logger.info("Native GGUF backend created successfully")
            backend.cleanup()
            return True
            
        except Exception as e:
            logger.error(f"Failed to create native GGUF backend: {e}")
            return False
    
    def test_tensor_name_mapping(self):
        """Test that 64-character tensor names are properly mapped"""
        try:
            config = InferenceConfig(
                backend_type="gguf",
                model_path=str(self.model_path)
            )
            
            backend = InferenceBackendFactory.create_backend_strict(config)
            
            if not backend.load_model():
                logger.error("Failed to load GGUF model")
                return False
            
            # Check that tensor name mapping was created
            if not backend.tensor_name_mapping:
                logger.error("No tensor name mapping found")
                return False
            
            logger.info(f"Tensor name mapping created for {len(backend.tensor_name_mapping)} long names")
            
            # Verify that 64-character names are mapped
            for short_name, original_name in backend.tensor_name_mapping.items():
                if len(original_name) != 64:
                    logger.error(f"Mapped tensor {original_name} is not 64 characters")
                    return False
                if not short_name.startswith("t64_"):
                    logger.error(f"Short name {short_name} doesn't follow expected pattern")
                    return False
            
            logger.info("All 64-character tensor names properly mapped")
            backend.cleanup()
            return True
            
        except Exception as e:
            logger.error(f"Tensor name mapping test failed: {e}")
            return False
    
    def test_no_fallback_mechanisms(self):
        """Test that no fallback mechanisms are present in the code"""
        try:
            # Test that create_with_fallback method doesn't exist or isn't used
            if hasattr(InferenceBackendFactory, 'create_with_fallback'):
                logger.error("create_with_fallback method still exists in factory")
                return False
            
            # Test that backend creation fails explicitly without fallback
            config = InferenceConfig(
                backend_type="nonexistent",
                model_path=str(self.model_path)
            )
            
            try:
                backend = InferenceBackendFactory.create_backend_strict(config)
                logger.error("Backend creation should have failed for nonexistent backend")
                return False
            except ValueError as e:
                if "No fallback" not in str(e):
                    logger.error("Error message doesn't mention no fallback")
                    return False
            
            logger.info("No fallback mechanisms detected - system fails explicitly")
            return True
            
        except Exception as e:
            logger.error(f"Fallback mechanism test failed: {e}")
            return False
    
    def test_gguf_model_loading(self):
        """Test that GGUF model loads successfully with native loader"""
        try:
            config = InferenceConfig(
                backend_type="gguf",
                model_path=str(self.model_path)
            )
            
            backend = InferenceBackendFactory.create_backend_strict(config)
            
            if not backend.load_model():
                logger.error("GGUF model failed to load")
                return False
            
            # Verify model is loaded
            if not backend.is_loaded:
                logger.error("Backend reports model not loaded")
                return False
            
            # Verify tensors are loaded
            if not backend.model_tensors:
                logger.error("No tensors loaded")
                return False
            
            logger.info(f"GGUF model loaded successfully with {len(backend.model_tensors)} tensors")
            backend.cleanup()
            return True
            
        except Exception as e:
            logger.error(f"GGUF model loading test failed: {e}")
            return False
    
    def test_gguf_inference_pipeline(self):
        """Test that GGUF inference pipeline works"""
        try:
            config = InferenceConfig(
                backend_type="gguf",
                model_path=str(self.model_path)
            )
            
            backend = InferenceBackendFactory.create_backend_strict(config)
            
            if not backend.load_model():
                logger.error("Failed to load GGUF model for inference test")
                return False
            
            # Create test inputs
            test_inputs = ModelInputs(
                input_ids=np.array([1, 2, 3, 4, 5], dtype=np.int64),
                style=np.random.randn(1, 256).astype(np.float32),
                speed=np.array([1.0], dtype=np.float32)
            )
            
            # Run inference
            outputs = backend.run_inference(test_inputs)
            
            # Verify outputs
            if outputs.audio is None:
                logger.error("No audio output generated")
                return False
            
            if len(outputs.audio) == 0:
                logger.error("Empty audio output")
                return False
            
            if outputs.metadata.get('backend') != 'gguf':
                logger.error("Output metadata doesn't indicate GGUF backend")
                return False
            
            logger.info(f"GGUF inference successful - generated {len(outputs.audio)} audio samples")
            backend.cleanup()
            return True
            
        except Exception as e:
            logger.error(f"GGUF inference pipeline test failed: {e}")
            return False
    
    def test_tts_engine_gguf_only(self):
        """Test that TTS engine works with GGUF only (no fallback)"""
        try:
            # Create config that forces GGUF
            config = TTSConfig()
            config.model.backend = "gguf"
            config.model.path = str(self.model_path)
            
            # Initialize TTS engine
            engine = KokoroTTSEngine(config)
            
            # Verify backend type
            if engine.inference_backend is None:
                logger.error("TTS engine has no inference backend")
                return False
            
            backend_info = engine.inference_backend.get_model_info()
            if backend_info.get('backend') != 'native_gguf':
                logger.error(f"TTS engine not using native GGUF backend: {backend_info.get('backend')}")
                return False
            
            logger.info("TTS engine successfully initialized with native GGUF backend")
            engine.cleanup()
            return True
            
        except Exception as e:
            logger.error(f"TTS engine GGUF-only test failed: {e}")
            return False
    
    def test_audio_generation(self):
        """Test end-to-end audio generation with GGUF"""
        try:
            # Create config
            config = TTSConfig()
            config.model.backend = "gguf"
            config.model.path = str(self.model_path)
            
            # Initialize TTS engine
            engine = KokoroTTSEngine(config)
            
            # Generate audio
            test_text = "Hello world, this is a test."
            audio_result = engine.synthesize(
                text=test_text,
                voice="af",  # Use a simple voice
                speed=1.0
            )
            
            # Verify audio was generated
            if audio_result is None:
                logger.error("No audio result returned")
                return False
            
            if len(audio_result.audio) == 0:
                logger.error("Empty audio generated")
                return False
            
            logger.info(f"Audio generation successful - {len(audio_result.audio)} samples for '{test_text}'")
            engine.cleanup()
            return True
            
        except Exception as e:
            logger.error(f"Audio generation test failed: {e}")
            return False

def main():
    """Run the validation tests"""
    print("🚀 Starting Native GGUF Validation Tests")
    print("This will verify that GGUF works natively without any fallback mechanisms")
    print()
    
    validator = GGUFValidationTest()
    success = validator.run_all_tests()
    
    if success:
        print("\n🎉 SUCCESS: Native GGUF implementation is fully functional!")
        print("✅ No fallback mechanisms detected")
        print("✅ Tensor name length limitations bypassed")
        print("✅ End-to-end audio generation working")
        return 0
    else:
        print("\n💥 FAILURE: Native GGUF implementation has issues")
        print("❌ Check the test results above for specific failures")
        return 1

if __name__ == "__main__":
    sys.exit(main())
