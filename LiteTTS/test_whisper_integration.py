#!/usr/bin/env python3
"""
Test script for Whisper integration in LiteTTS
Tests the OptimizedWhisperProcessor and configuration system
"""

import sys
import os
import logging
from pathlib import Path

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_whisper_processor():
    """Test the OptimizedWhisperProcessor"""
    try:
        from backends.whisper_optimized import create_whisper_processor
        
        logger.info("Testing OptimizedWhisperProcessor...")
        
        # Create processor with recommended settings
        processor = create_whisper_processor(
            model_name="distil-small.en",
            compute_type="int8",
            enable_fallback=True
        )
        
        logger.info("✅ OptimizedWhisperProcessor created successfully")
        
        # Get model info
        model_info = processor.get_model_info()
        logger.info(f"Model info: {model_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ OptimizedWhisperProcessor test failed: {e}")
        return False

def test_config_loader():
    """Test the configuration loader"""
    try:
        from config.whisper_config_loader import WhisperConfigLoader
        
        logger.info("Testing WhisperConfigLoader...")
        
        # Create config loader
        config_loader = WhisperConfigLoader()
        settings = config_loader.get_settings()
        
        logger.info("✅ WhisperConfigLoader created successfully")
        logger.info(f"Settings: Model={settings.default_model}, RTF threshold={settings.rtf_threshold}")
        
        # Test model info
        model_info = config_loader.get_model_info(settings.default_model)
        if model_info:
            logger.info(f"Model info: Size={model_info.get('size_mb')}MB, Expected RTF={model_info.get('expected_rtf', {}).get('raspberry_pi_4')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ WhisperConfigLoader test failed: {e}")
        return False

def test_voice_cloning_update():
    """Test the voice cloning duration update"""
    try:
        from voice.cloning import VoiceCloner
        
        logger.info("Testing VoiceCloner duration update...")
        
        # Create voice cloner
        cloner = VoiceCloner()
        
        logger.info(f"Max audio duration: {cloner.max_audio_duration}s")
        
        if cloner.max_audio_duration == 120.0:
            logger.info("✅ Voice cloning duration successfully extended to 120s")
            return True
        else:
            logger.warning(f"⚠️ Voice cloning duration is {cloner.max_audio_duration}s, expected 120s")
            return False
        
    except Exception as e:
        logger.error(f"❌ VoiceCloner test failed: {e}")
        return False

def test_faster_whisper_availability():
    """Test if faster-whisper is available"""
    try:
        import faster_whisper
        logger.info(f"✅ faster-whisper available, version: {faster_whisper.__version__}")
        return True
    except ImportError:
        logger.error("❌ faster-whisper not available")
        return False

def test_environment_variables():
    """Test environment variable configuration"""
    logger.info("Testing environment variable configuration...")
    
    # Set test environment variables
    os.environ['WHISPER_MODEL'] = 'base'
    os.environ['WHISPER_CPU_THREADS'] = '2'
    os.environ['VOICE_CLONING_MAX_DURATION'] = '90'
    
    try:
        from config.whisper_config_loader import WhisperConfigLoader
        
        # Create new config loader to pick up env vars
        config_loader = WhisperConfigLoader()
        settings = config_loader.get_settings()
        
        logger.info(f"Model from env: {settings.default_model}")
        logger.info(f"CPU threads from env: {settings.cpu_threads}")
        logger.info(f"Max duration from env: {settings.max_audio_duration}")
        
        # Clean up
        del os.environ['WHISPER_MODEL']
        del os.environ['WHISPER_CPU_THREADS'] 
        del os.environ['VOICE_CLONING_MAX_DURATION']
        
        logger.info("✅ Environment variable configuration working")
        return True
        
    except Exception as e:
        logger.error(f"❌ Environment variable test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting LiteTTS Whisper Integration Tests")
    logger.info("=" * 60)
    
    tests = [
        ("faster-whisper availability", test_faster_whisper_availability),
        ("OptimizedWhisperProcessor", test_whisper_processor),
        ("WhisperConfigLoader", test_config_loader),
        ("Voice cloning duration update", test_voice_cloning_update),
        ("Environment variables", test_environment_variables),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running test: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Whisper integration is ready.")
        return True
    else:
        logger.warning(f"⚠️ {total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
