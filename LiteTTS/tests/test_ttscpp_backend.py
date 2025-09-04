#!/usr/bin/env python3
"""
Standalone test script for TTSCppBackend
Tests all interface methods independently before LiteTTS integration
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

from LiteTTS.inference.ttscpp_backend import TTSCppBackend
from LiteTTS.inference.base import InferenceConfig, ModelInputs, ModelOutputs

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TTSCppBackendTester:
    """Comprehensive test suite for TTSCppBackend"""
    
    def __init__(self):
        self.backend = None
        self.test_results = {}
        self.model_path = None
        self.ttscpp_executable = None
        
    def setup_test_environment(self):
        """Setup test environment and locate required files"""
        logger.info("Setting up test environment...")
        
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
    
    def create_backend(self):
        """Create TTSCppBackend instance with test configuration"""
        logger.info("Creating TTSCppBackend instance...")
        
        config = InferenceConfig(
            backend_type="ttscpp",
            model_path=self.model_path,
            device="cpu",
            backend_specific_options={
                'ttscpp_executable': self.ttscpp_executable,
                'timeout': 30
            }
        )
        
        self.backend = TTSCppBackend(config)
        logger.info("TTSCppBackend created successfully")
    
    def test_model_validation(self):
        """Test model validation functionality"""
        logger.info("Testing model validation...")
        
        try:
            # Test valid model
            result = self.backend.validate_model()
            assert result == True, "Valid model should pass validation"
            
            # Test invalid model path
            original_path = self.backend.model_path
            self.backend.model_path = Path("/nonexistent/model.gguf")
            result = self.backend.validate_model()
            assert result == False, "Nonexistent model should fail validation"
            
            # Restore original path
            self.backend.model_path = original_path
            
            self.test_results['model_validation'] = 'PASS'
            logger.info("✅ Model validation test passed")
            
        except Exception as e:
            self.test_results['model_validation'] = f'FAIL: {e}'
            logger.error(f"❌ Model validation test failed: {e}")
    
    def test_model_loading(self):
        """Test model loading and unloading"""
        logger.info("Testing model loading...")
        
        try:
            # Test model loading
            assert not self.backend.is_model_loaded(), "Model should not be loaded initially"
            
            result = self.backend.load_model()
            assert result == True, "Model loading should succeed"
            assert self.backend.is_model_loaded(), "Model should be loaded after load_model()"
            
            # Test model info
            model_info = self.backend.get_model_info()
            assert isinstance(model_info, dict), "Model info should be a dictionary"
            assert 'model_path' in model_info, "Model info should contain model_path"
            
            # Test model unloading
            result = self.backend.unload_model()
            assert result == True, "Model unloading should succeed"
            assert not self.backend.is_model_loaded(), "Model should not be loaded after unload_model()"
            
            self.test_results['model_loading'] = 'PASS'
            logger.info("✅ Model loading test passed")
            
        except Exception as e:
            self.test_results['model_loading'] = f'FAIL: {e}'
            logger.error(f"❌ Model loading test failed: {e}")
    
    def test_input_output_specs(self):
        """Test input and output specifications"""
        logger.info("Testing input/output specifications...")
        
        try:
            input_specs = self.backend.get_input_specs()
            assert isinstance(input_specs, dict), "Input specs should be a dictionary"
            assert 'input_ids' in input_specs, "Input specs should contain input_ids"
            assert 'text' in input_specs, "Input specs should contain text"
            
            output_specs = self.backend.get_output_specs()
            assert isinstance(output_specs, dict), "Output specs should be a dictionary"
            assert 'audio' in output_specs, "Output specs should contain audio"
            assert 'sample_rate' in output_specs, "Output specs should contain sample_rate"
            
            self.test_results['input_output_specs'] = 'PASS'
            logger.info("✅ Input/output specs test passed")
            
        except Exception as e:
            self.test_results['input_output_specs'] = f'FAIL: {e}'
            logger.error(f"❌ Input/output specs test failed: {e}")
    
    def test_inference_basic(self):
        """Test basic inference functionality"""
        logger.info("Testing basic inference...")
        
        try:
            # Load model first
            self.backend.load_model()
            
            # Create test inputs
            test_text = "Hello, this is a test of the TTS system."
            inputs = ModelInputs(
                input_ids=np.array([1, 2, 3, 4, 5], dtype=np.int32),
                style=np.random.randn(512).astype(np.float32),
                speed=np.array([1.0], dtype=np.float32),
                additional_inputs={'text': test_text}
            )
            
            # Run inference
            start_time = time.time()
            outputs = self.backend.run_inference(inputs)
            inference_time = time.time() - start_time
            
            # Validate outputs
            assert isinstance(outputs, ModelOutputs), "Output should be ModelOutputs instance"
            assert isinstance(outputs.audio, np.ndarray), "Audio should be numpy array"
            assert outputs.audio.dtype == np.float32, "Audio should be float32"
            assert outputs.sample_rate == 24000, "Sample rate should be 24000 Hz"
            assert len(outputs.audio) > 0, "Audio should not be empty"
            
            # Calculate performance metrics
            audio_duration = len(outputs.audio) / outputs.sample_rate
            rtf = inference_time / audio_duration if audio_duration > 0 else float('inf')
            
            logger.info(f"Inference metrics: time={inference_time:.2f}s, "
                       f"audio_duration={audio_duration:.2f}s, RTF={rtf:.3f}")
            
            self.test_results['inference_basic'] = 'PASS'
            self.test_results['inference_rtf'] = rtf
            logger.info("✅ Basic inference test passed")
            
        except Exception as e:
            self.test_results['inference_basic'] = f'FAIL: {e}'
            logger.error(f"❌ Basic inference test failed: {e}")
        finally:
            self.backend.unload_model()
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        logger.info("Testing error handling...")
        
        try:
            # Test inference without loaded model
            inputs = ModelInputs(
                input_ids=np.array([1, 2, 3], dtype=np.int32),
                style=np.random.randn(512).astype(np.float32),
                speed=np.array([1.0], dtype=np.float32),
                additional_inputs={'text': 'test'}
            )
            
            try:
                self.backend.run_inference(inputs)
                assert False, "Should raise RuntimeError for unloaded model"
            except RuntimeError:
                pass  # Expected
            
            # Test invalid inputs
            self.backend.load_model()
            
            invalid_inputs = ModelInputs(
                input_ids=None,
                style=None,
                speed=None
            )
            
            try:
                self.backend.run_inference(invalid_inputs)
                assert False, "Should raise ValueError for invalid inputs"
            except ValueError:
                pass  # Expected
            
            self.test_results['error_handling'] = 'PASS'
            logger.info("✅ Error handling test passed")
            
        except Exception as e:
            self.test_results['error_handling'] = f'FAIL: {e}'
            logger.error(f"❌ Error handling test failed: {e}")
        finally:
            if self.backend.is_model_loaded():
                self.backend.unload_model()
    
    def test_performance_info(self):
        """Test performance information methods"""
        logger.info("Testing performance information...")
        
        try:
            perf_info = self.backend.get_performance_info()
            assert isinstance(perf_info, dict), "Performance info should be a dictionary"
            assert 'backend_type' in perf_info, "Should contain backend_type"
            assert 'ttscpp_executable' in perf_info, "Should contain ttscpp_executable"
            
            memory_usage = self.backend.estimate_memory_usage()
            assert isinstance(memory_usage, dict), "Memory usage should be a dictionary"
            assert 'model_size' in memory_usage, "Should contain model_size"
            
            device_support = self.backend.supports_device('cpu')
            assert device_support == True, "Should support CPU"
            
            device_support = self.backend.supports_device('cuda')
            assert device_support == False, "Should not support CUDA"
            
            self.test_results['performance_info'] = 'PASS'
            logger.info("✅ Performance information test passed")
            
        except Exception as e:
            self.test_results['performance_info'] = f'FAIL: {e}'
            logger.error(f"❌ Performance information test failed: {e}")
    
    def run_all_tests(self):
        """Run all tests and report results"""
        logger.info("🚀 Starting TTSCppBackend comprehensive test suite...")
        
        try:
            self.setup_test_environment()
            self.create_backend()
            
            # Run all test methods
            test_methods = [
                self.test_model_validation,
                self.test_model_loading,
                self.test_input_output_specs,
                self.test_inference_basic,
                self.test_error_handling,
                self.test_performance_info
            ]
            
            for test_method in test_methods:
                try:
                    test_method()
                except Exception as e:
                    logger.error(f"Test method {test_method.__name__} failed: {e}")
            
            # Report results
            self.report_results()
            
        except Exception as e:
            logger.error(f"Test setup failed: {e}")
            return False
        
        return self.all_tests_passed()
    
    def report_results(self):
        """Report test results summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("="*60)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.test_results.items():
            if test_name == 'inference_rtf':
                continue  # Skip RTF metric in pass/fail count
                
            status = "✅ PASS" if result == 'PASS' else f"❌ FAIL"
            logger.info(f"{test_name:25} : {status}")
            
            if result == 'PASS':
                passed += 1
            else:
                failed += 1
                logger.info(f"                          {result}")
        
        # Report RTF if available
        if 'inference_rtf' in self.test_results:
            rtf = self.test_results['inference_rtf']
            rtf_status = "🚀 EXCELLENT" if rtf < 0.25 else "✅ GOOD" if rtf < 1.0 else "⚠️  SLOW"
            logger.info(f"{'Real-Time Factor':25} : {rtf:.3f} ({rtf_status})")
        
        logger.info("="*60)
        logger.info(f"TOTAL: {passed} passed, {failed} failed")
        
        if failed == 0:
            logger.info("🎉 ALL TESTS PASSED! TTSCppBackend is ready for integration.")
        else:
            logger.error(f"💥 {failed} tests failed. Please fix issues before integration.")
    
    def all_tests_passed(self):
        """Check if all tests passed"""
        for test_name, result in self.test_results.items():
            if test_name == 'inference_rtf':
                continue
            if result != 'PASS':
                return False
        return True

def main():
    """Main test execution"""
    tester = TTSCppBackendTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("✅ Standalone testing completed successfully!")
        return 0
    else:
        logger.error("❌ Standalone testing failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
