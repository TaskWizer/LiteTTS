#!/usr/bin/env python3
"""
End-to-end integration test for LiteTTS with TTSCppBackend
Tests the complete LiteTTS system using the new GGUF backend
"""

import sys
import os
import numpy as np
import logging
import time
import tempfile
from pathlib import Path

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent / "LiteTTS"))

from LiteTTS.inference.factory import InferenceBackendFactory
from LiteTTS.inference.base import InferenceConfig, ModelInputs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LiteTTSIntegrationTester:
    """End-to-end integration test for LiteTTS with TTSCppBackend"""
    
    def __init__(self):
        self.test_results = {}
        self.model_path = None
        self.ttscpp_executable = None
        
    def setup_test_environment(self):
        """Setup test environment and locate required files"""
        logger.info("Setting up LiteTTS integration test environment...")
        
        # Find TTS.cpp executable
        ttscpp_paths = [
            "TTS.cpp/build/bin/tts-cli",
            "../TTS.cpp/build/bin/tts-cli",
            "./build/bin/tts-cli"
        ]
        
        for path in ttscpp_paths:
            if Path(path).exists():
                self.ttscpp_executable = str(Path(path).resolve())
                logger.info(f"Found TTS.cpp executable: {self.ttscpp_executable}")
                break
        
        if not self.ttscpp_executable:
            raise RuntimeError("TTS.cpp executable not found")
        
        # Find compatible GGUF model
        model_paths = [
            "TTS.cpp/Kokoro_no_espeak_Q4.gguf",
            "../TTS.cpp/Kokoro_no_espeak_Q4.gguf",
            "LiteTTS/models/Kokoro_espeak_Q4.gguf"
        ]
        
        for path in model_paths:
            if Path(path).exists():
                self.model_path = str(Path(path).resolve())
                logger.info(f"Found GGUF model: {self.model_path}")
                break
        
        if not self.model_path:
            raise RuntimeError("Compatible GGUF model not found")
    
    def test_backend_auto_detection(self):
        """Test automatic backend detection for GGUF models"""
        logger.info("Testing backend auto-detection...")
        
        try:
            detected_backend = InferenceBackendFactory.auto_detect_backend(self.model_path)
            assert detected_backend == "gguf", f"Expected 'gguf', got '{detected_backend}'"
            
            self.test_results['backend_auto_detection'] = 'PASS'
            logger.info("✅ Backend auto-detection test passed")
            
        except Exception as e:
            self.test_results['backend_auto_detection'] = f'FAIL: {e}'
            logger.error(f"❌ Backend auto-detection test failed: {e}")
    
    def test_backend_creation_via_factory(self):
        """Test backend creation through the factory system"""
        logger.info("Testing backend creation via factory...")
        
        try:
            config = InferenceConfig(
                backend_type="gguf",
                model_path=self.model_path,
                device="cpu",
                backend_specific_options={
                    'ttscpp_executable': self.ttscpp_executable,
                    'timeout': 30
                }
            )
            
            backend = InferenceBackendFactory.create_backend(config)
            
            # Verify it's our TTSCppBackend
            assert hasattr(backend, '_run_ttscpp_subprocess'), "Backend should be TTSCppBackend"
            assert backend.get_backend_type() == "gguf", "Backend type should be 'gguf'"
            
            # Test model loading
            load_success = backend.load_model()
            assert load_success, "Model loading should succeed"
            
            # Test model info
            model_info = backend.get_model_info()
            assert isinstance(model_info, dict), "Model info should be a dictionary"
            assert 'backend' in model_info, "Model info should contain backend type"
            
            # Clean up
            backend.unload_model()
            
            self.test_results['backend_creation_via_factory'] = 'PASS'
            logger.info("✅ Backend creation via factory test passed")
            
        except Exception as e:
            self.test_results['backend_creation_via_factory'] = f'FAIL: {e}'
            logger.error(f"❌ Backend creation via factory test failed: {e}")
    
    def test_end_to_end_inference(self):
        """Test complete end-to-end inference through LiteTTS system"""
        logger.info("Testing end-to-end inference...")
        
        try:
            # Create backend through factory
            config = InferenceConfig(
                backend_type="gguf",
                model_path=self.model_path,
                device="cpu",
                backend_specific_options={
                    'ttscpp_executable': self.ttscpp_executable,
                    'timeout': 30
                }
            )
            
            backend = InferenceBackendFactory.create_backend(config)
            backend.load_model()
            
            # Create test inputs
            test_text = "Hello, this is a comprehensive test of the LiteTTS system with GGUF backend integration."
            inputs = ModelInputs(
                input_ids=np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.int32),
                style=np.random.randn(512).astype(np.float32),
                speed=np.array([1.0], dtype=np.float32),
                additional_inputs={'text': test_text}
            )
            
            # Run inference
            start_time = time.time()
            outputs = backend.run_inference(inputs)
            inference_time = time.time() - start_time
            
            # Validate outputs
            assert outputs.audio is not None, "Audio output should not be None"
            assert isinstance(outputs.audio, np.ndarray), "Audio should be numpy array"
            assert outputs.audio.dtype == np.float32, "Audio should be float32"
            assert outputs.sample_rate == 24000, "Sample rate should be 24000 Hz"
            assert len(outputs.audio) > 0, "Audio should not be empty"
            
            # Check audio quality
            max_amplitude = np.max(np.abs(outputs.audio))
            assert max_amplitude > 0, "Audio should not be silent"
            assert max_amplitude <= 1.0, "Audio should not clip"
            
            # Calculate performance metrics
            audio_duration = len(outputs.audio) / outputs.sample_rate
            rtf = inference_time / audio_duration if audio_duration > 0 else float('inf')
            
            # Performance validation
            assert rtf < 2.0, f"RTF should be reasonable: {rtf}"
            
            logger.info(f"End-to-end inference metrics:")
            logger.info(f"  Text length: {len(test_text)} characters")
            logger.info(f"  Inference time: {inference_time:.2f}s")
            logger.info(f"  Audio duration: {audio_duration:.2f}s")
            logger.info(f"  Real-Time Factor: {rtf:.3f}")
            logger.info(f"  Audio samples: {len(outputs.audio)}")
            logger.info(f"  Max amplitude: {max_amplitude:.3f}")
            
            # Save test audio for manual verification
            import soundfile as sf
            test_output_path = "test_litetts_integration_output.wav"
            sf.write(test_output_path, outputs.audio, outputs.sample_rate)
            logger.info(f"Test audio saved to: {test_output_path}")
            
            # Clean up
            backend.unload_model()
            
            self.test_results['end_to_end_inference'] = 'PASS'
            self.test_results['inference_rtf'] = rtf
            self.test_results['audio_duration'] = audio_duration
            logger.info("✅ End-to-end inference test passed")
            
        except Exception as e:
            self.test_results['end_to_end_inference'] = f'FAIL: {e}'
            logger.error(f"❌ End-to-end inference test failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def test_backend_compatibility_check(self):
        """Test backend compatibility validation"""
        logger.info("Testing backend compatibility check...")
        
        try:
            # Test with valid GGUF model
            available_backends = InferenceBackendFactory.get_available_backends()
            assert 'gguf' in available_backends, "GGUF backend should be available"
            
            gguf_info = available_backends['gguf']
            assert gguf_info.get('supports_cpu', False), "GGUF backend should support CPU"
            
            # Test benchmark functionality
            benchmark_results = InferenceBackendFactory.benchmark_backends(self.model_path)
            assert 'gguf' in benchmark_results, "GGUF backend should be benchmarked"
            
            gguf_benchmark = benchmark_results['gguf']
            assert gguf_benchmark.get('compatible', False), "GGUF backend should be compatible"
            
            self.test_results['backend_compatibility_check'] = 'PASS'
            logger.info("✅ Backend compatibility check test passed")
            
        except Exception as e:
            self.test_results['backend_compatibility_check'] = f'FAIL: {e}'
            logger.error(f"❌ Backend compatibility check test failed: {e}")
    
    def test_error_handling_integration(self):
        """Test error handling in integrated system"""
        logger.info("Testing error handling integration...")
        
        try:
            # Test with invalid model path
            try:
                config = InferenceConfig(
                    backend_type="gguf",
                    model_path="/nonexistent/model.gguf",
                    device="cpu"
                )
                backend = InferenceBackendFactory.create_backend(config)
                backend.load_model()
                assert False, "Should fail with nonexistent model"
            except Exception:
                pass  # Expected
            
            # Test with invalid backend type
            try:
                config = InferenceConfig(
                    backend_type="invalid_backend",
                    model_path=self.model_path,
                    device="cpu"
                )
                backend = InferenceBackendFactory.create_backend(config)
                assert False, "Should fail with invalid backend type"
            except ValueError:
                pass  # Expected
            
            self.test_results['error_handling_integration'] = 'PASS'
            logger.info("✅ Error handling integration test passed")
            
        except Exception as e:
            self.test_results['error_handling_integration'] = f'FAIL: {e}'
            logger.error(f"❌ Error handling integration test failed: {e}")
    
    def run_all_tests(self):
        """Run all integration tests"""
        logger.info("🚀 Starting LiteTTS integration test suite...")
        
        try:
            self.setup_test_environment()
            
            # Run all test methods
            test_methods = [
                self.test_backend_auto_detection,
                self.test_backend_creation_via_factory,
                self.test_backend_compatibility_check,
                self.test_end_to_end_inference,
                self.test_error_handling_integration
            ]
            
            for test_method in test_methods:
                try:
                    test_method()
                except Exception as e:
                    logger.error(f"Test method {test_method.__name__} failed: {e}")
            
            # Report results
            self.report_results()
            
        except Exception as e:
            logger.error(f"Integration test setup failed: {e}")
            return False
        
        return self.all_tests_passed()
    
    def report_results(self):
        """Report test results summary"""
        logger.info("\n" + "="*70)
        logger.info("📊 LITETTS INTEGRATION TEST RESULTS")
        logger.info("="*70)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.test_results.items():
            if test_name in ['inference_rtf', 'audio_duration']:
                continue  # Skip metrics in pass/fail count
                
            status = "✅ PASS" if result == 'PASS' else f"❌ FAIL"
            logger.info(f"{test_name:35} : {status}")
            
            if result == 'PASS':
                passed += 1
            else:
                failed += 1
                logger.info(f"                                    {result}")
        
        # Report performance metrics
        if 'inference_rtf' in self.test_results:
            rtf = self.test_results['inference_rtf']
            rtf_status = "🚀 EXCELLENT" if rtf < 0.25 else "✅ GOOD" if rtf < 1.0 else "⚠️  SLOW"
            logger.info(f"{'Real-Time Factor':35} : {rtf:.3f} ({rtf_status})")
        
        if 'audio_duration' in self.test_results:
            duration = self.test_results['audio_duration']
            logger.info(f"{'Audio Duration':35} : {duration:.2f}s")
        
        logger.info("="*70)
        logger.info(f"TOTAL: {passed} passed, {failed} failed")
        
        if failed == 0:
            logger.info("🎉 ALL INTEGRATION TESTS PASSED!")
            logger.info("✅ LiteTTS GGUF backend integration is successful!")
        else:
            logger.error(f"💥 {failed} integration tests failed.")
    
    def all_tests_passed(self):
        """Check if all tests passed"""
        for test_name, result in self.test_results.items():
            if test_name in ['inference_rtf', 'audio_duration']:
                continue
            if result != 'PASS':
                return False
        return True

def main():
    """Main test execution"""
    tester = LiteTTSIntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("✅ LiteTTS integration testing completed successfully!")
        return 0
    else:
        logger.error("❌ LiteTTS integration testing failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
