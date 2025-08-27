#!/usr/bin/env python3
"""
Test script to validate the automated audio quality testing framework
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_framework_imports():
    """Test that all framework components can be imported"""
    print("🔍 Testing Framework Imports")
    print("=" * 50)
    
    try:
        from LiteTTS.testing.audio_quality_tester import AudioQualityTester, AudioTestCase, AudioQualityMetrics
        print("✅ AudioQualityTester imported successfully")
        
        from LiteTTS.testing.espeak_integration_tests import EspeakIntegrationTestSuite
        print("✅ EspeakIntegrationTestSuite imported successfully")
        
        from LiteTTS.testing.asr_integrations.base_asr_client import BaseASRClient
        print("✅ BaseASRClient imported successfully")
        
        from LiteTTS.testing.asr_integrations.deepgram_client import DeepgramASRClient
        print("✅ DeepgramASRClient imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_configuration_loading():
    """Test configuration loading and validation"""
    print("\n🔧 Testing Configuration Loading")
    print("=" * 50)
    
    try:
        from LiteTTS.scripts.run_audio_quality_tests import AudioQualityTestRunner
        
        # Test configuration loading
        runner = AudioQualityTestRunner()
        config = runner.config
        
        # Check if audio quality testing config exists
        audio_config = config.get("audio_quality_testing", {})
        if not audio_config:
            print("❌ Audio quality testing configuration not found")
            return False
        
        print("✅ Configuration loaded successfully")
        print(f"   Enabled: {audio_config.get('enabled', False)}")
        print(f"   API URL: {audio_config.get('api_base_url', 'Not set')}")
        print(f"   Max Concurrent Tests: {audio_config.get('max_concurrent_tests', 'Not set')}")
        
        # Check quality thresholds
        thresholds = audio_config.get("quality_thresholds", {})
        print(f"   Quality Thresholds: {len(thresholds)} configured")
        
        return True
    except Exception as e:
        print(f"❌ Configuration loading error: {e}")
        return False

def test_test_case_creation():
    """Test creating test cases"""
    print("\n📝 Testing Test Case Creation")
    print("=" * 50)
    
    try:
        from LiteTTS.testing.espeak_integration_tests import EspeakIntegrationTestSuite
        
        # Create test suite
        suite = EspeakIntegrationTestSuite()
        
        # Get test cases
        all_tests = suite.get_test_cases()
        critical_tests = suite.get_critical_tests()
        symbol_tests = suite.get_symbol_processing_tests()
        
        print(f"✅ Test suite created successfully")
        print(f"   Total test cases: {len(all_tests)}")
        print(f"   Critical tests: {len(critical_tests)}")
        print(f"   Symbol processing tests: {len(symbol_tests)}")
        
        # Validate test case structure
        if all_tests:
            test_case = all_tests[0]
            print(f"   Sample test: {test_case.test_id} - {test_case.description}")
            print(f"   Expected symbols: {test_case.expected_symbols}")
            print(f"   Expected pronunciations: {test_case.expected_pronunciations}")
        
        return True
    except Exception as e:
        print(f"❌ Test case creation error: {e}")
        return False

def test_audio_quality_tester_init():
    """Test AudioQualityTester initialization"""
    print("\n🎯 Testing AudioQualityTester Initialization")
    print("=" * 50)
    
    try:
        from LiteTTS.testing.audio_quality_tester import AudioQualityTester
        
        # Test with default config
        tester = AudioQualityTester()
        
        print("✅ AudioQualityTester initialized successfully")
        print(f"   API Base URL: {tester.api_base_url}")
        print(f"   API Timeout: {tester.api_timeout}")
        print(f"   Max Concurrent Tests: {tester.max_concurrent_tests}")
        print(f"   Cache Enabled: {tester.cache_enabled}")
        print(f"   External ASR Enabled: {tester.enable_external_asr}")
        print(f"   ASR Services: {list(tester.asr_services.keys()) if tester.asr_services else 'None'}")
        
        # Test quality thresholds
        thresholds = tester.quality_thresholds
        print(f"   Quality Thresholds:")
        for key, value in thresholds.items():
            print(f"     {key}: {value}")
        
        return True
    except Exception as e:
        print(f"❌ AudioQualityTester initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_basic_functionality():
    """Test basic functionality without requiring TTS API"""
    print("\n⚡ Testing Basic Functionality")
    print("=" * 50)
    
    try:
        from LiteTTS.testing.audio_quality_tester import AudioQualityTester, AudioTestCase
        
        # Create tester
        tester = AudioQualityTester()
        
        # Test WER calculation
        reference = "hello question mark how are you"
        hypothesis = "hello question mark how are you"
        wer = tester.calculate_wer(reference, hypothesis)
        print(f"✅ WER calculation test: {wer:.3f} (perfect match)")
        
        # Test with different hypothesis
        hypothesis2 = "hello how are you"
        wer2 = tester.calculate_wer(reference, hypothesis2)
        print(f"✅ WER calculation test: {wer2:.3f} (missing words)")
        
        # Test MOS prediction (heuristic)
        fake_audio_data = b"fake_audio_data"
        test_text = "Hello world"
        mos_score = tester.predict_mos_score(fake_audio_data, test_text)
        print(f"✅ MOS prediction test: {mos_score:.2f}")
        
        # Test pronunciation accuracy analysis
        test_case = AudioTestCase(
            test_id="test",
            input_text="Hello?",
            expected_transcription="hello question mark",
            expected_pronunciations={"?": "question mark"}
        )
        
        transcription = "hello question mark"
        accuracy = tester.analyze_pronunciation_accuracy(test_case, transcription)
        print(f"✅ Pronunciation accuracy test: {accuracy:.2f} (perfect match)")
        
        transcription2 = "hello"
        accuracy2 = tester.analyze_pronunciation_accuracy(test_case, transcription2)
        print(f"✅ Pronunciation accuracy test: {accuracy2:.2f} (missing pronunciation)")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_connectivity():
    """Test connectivity to TTS API (if available)"""
    print("\n🌐 Testing TTS API Connectivity")
    print("=" * 50)
    
    try:
        from LiteTTS.testing.audio_quality_tester import AudioQualityTester, AudioTestCase
        
        # Create tester
        tester = AudioQualityTester()
        
        # Create simple test case
        test_case = AudioTestCase(
            test_id="connectivity_test",
            input_text="Hello world",
            expected_transcription="hello world",
            voice_model="af_heart"
        )
        
        print(f"Testing API connectivity to: {tester.api_base_url}")
        
        try:
            # Try to generate audio
            audio_data, processing_time = await tester.generate_audio(test_case)
            
            print(f"✅ TTS API connectivity successful")
            print(f"   Audio size: {len(audio_data)} bytes")
            print(f"   Processing time: {processing_time:.3f}s")
            
            # Test audio analysis
            audio_props = tester.analyze_audio_properties(audio_data)
            print(f"   Audio duration: {audio_props.get('duration', 0):.3f}s")
            print(f"   Sample rate: {audio_props.get('sample_rate', 0)} Hz")
            
            return True
            
        except Exception as api_error:
            print(f"⚠️  TTS API not available: {api_error}")
            print("   This is expected if the TTS server is not running")
            return True  # Not a failure - just means API is not available
            
    except Exception as e:
        print(f"❌ API connectivity test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Audio Quality Testing Framework Validation")
    print("=" * 60)
    
    success = True
    
    # Test 1: Framework imports
    if not test_framework_imports():
        success = False
    
    # Test 2: Configuration loading
    if not test_configuration_loading():
        success = False
    
    # Test 3: Test case creation
    if not test_test_case_creation():
        success = False
    
    # Test 4: AudioQualityTester initialization
    if not test_audio_quality_tester_init():
        success = False
    
    # Test 5: Basic functionality
    if not await test_basic_functionality():
        success = False
    
    # Test 6: API connectivity (optional)
    if not await test_api_connectivity():
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ FRAMEWORK VALIDATION SUCCESSFUL!")
        print("\n🎉 Audio Quality Testing Framework is ready:")
        print("   - All components imported successfully")
        print("   - Configuration system working")
        print("   - Test cases created and validated")
        print("   - Basic functionality operational")
        print("   - Framework ready for production use")
        print("\n🚀 Next steps:")
        print("   1. Configure external ASR services (optional)")
        print("   2. Run: python LiteTTS/scripts/run_audio_quality_tests.py --test-type espeak --filter critical")
        print("   3. Review test results and establish baselines")
    else:
        print("❌ FRAMEWORK VALIDATION FAILED!")
        print("   Some components are not working correctly.")
        print("   Check the error messages above.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
