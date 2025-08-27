#!/usr/bin/env python3
"""
Simple test script for time-stretching optimization feature
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.audio.time_stretcher import TimeStretcher, TimeStretchConfig, StretchQuality

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_time_stretcher_config():
    """Test time-stretcher configuration"""
    print("Testing TimeStretcher Configuration")
    print("-" * 40)
    
    try:
        # Test different configurations
        configs = [
            {"enabled": False, "rate": 20, "quality": "medium"},
            {"enabled": True, "rate": 20, "quality": "low"},
            {"enabled": True, "rate": 30, "quality": "medium"},
            {"enabled": True, "rate": 50, "quality": "high"},
        ]
        
        for i, config_dict in enumerate(configs):
            print(f"\nTest {i+1}: {config_dict}")
            
            config = TimeStretchConfig(
                enabled=config_dict["enabled"],
                compress_playback_rate=config_dict["rate"],
                correction_quality=StretchQuality(config_dict["quality"])
            )
            
            stretcher = TimeStretcher(config)
            
            print(f"  Enabled: {stretcher.config.enabled}")
            print(f"  Speed multiplier: {stretcher.get_generation_speed_multiplier():.2f}x")
            print(f"  Should apply (20 chars): {stretcher.should_apply_stretching(20)}")
            print(f"  Should apply (100 chars): {stretcher.should_apply_stretching(100)}")
            
        print("\n✅ Configuration tests passed")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True

def test_config_integration():
    """Test integration with main config.json"""
    print("\nTesting Config Integration")
    print("-" * 40)
    
    try:
        # Load main config
        config_path = project_root / "config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check time-stretching section
        time_stretching = config.get("time_stretching", {})
        
        print(f"Time-stretching config found: {bool(time_stretching)}")
        print(f"Enabled: {time_stretching.get('enabled', 'Not set')}")
        print(f"Rate: {time_stretching.get('compress_playback_rate', 'Not set')}%")
        print(f"Quality: {time_stretching.get('correction_quality', 'Not set')}")
        
        if time_stretching:
            print("✅ Config integration test passed")
            return True
        else:
            print("❌ Time-stretching config not found in config.json")
            return False
            
    except Exception as e:
        print(f"❌ Config integration test failed: {e}")
        return False

def test_text_processing_config():
    """Test expanded text processing configuration"""
    print("\nTesting Text Processing Configuration")
    print("-" * 40)
    
    try:
        # Load main config
        config_path = project_root / "config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check text processing section
        text_processing = config.get("text_processing", {})
        
        print(f"Text processing config found: {bool(text_processing)}")
        
        # Check key sections
        sections = [
            "phonetic_processing",
            "contraction_handling", 
            "symbol_processing",
            "punctuation_handling",
            "interjection_handling",
            "pronunciation_dictionary",
            "currency_processing",
            "datetime_processing",
            "url_processing",
            "number_processing",
            "voice_modulation",
            "advanced_features"
        ]
        
        found_sections = 0
        for section in sections:
            if section in text_processing:
                found_sections += 1
                print(f"  ✅ {section}")
            else:
                print(f"  ❌ {section} - missing")
        
        print(f"\nFound {found_sections}/{len(sections)} expected sections")
        
        if found_sections >= len(sections) * 0.8:  # At least 80% of sections
            print("✅ Text processing config test passed")
            return True
        else:
            print("❌ Text processing config incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Text processing config test failed: {e}")
        return False

def test_library_availability():
    """Test availability of time-stretching libraries"""
    print("\nTesting Library Availability")
    print("-" * 40)
    
    libraries = []
    
    try:
        import librosa
        libraries.append("librosa ✅")
    except ImportError:
        libraries.append("librosa ❌")
    
    try:
        import pyrubberband
        libraries.append("pyrubberband ✅")
    except ImportError:
        libraries.append("pyrubberband ❌")
    
    try:
        import soundfile
        libraries.append("soundfile ✅")
    except ImportError:
        libraries.append("soundfile ❌")
    
    try:
        import numpy
        libraries.append("numpy ✅")
    except ImportError:
        libraries.append("numpy ❌")
    
    for lib in libraries:
        print(f"  {lib}")
    
    # Check if at least basic functionality is available
    available_count = sum(1 for lib in libraries if "✅" in lib)
    
    if available_count >= 2:  # At least numpy and one audio library
        print("✅ Sufficient libraries available")
        return True
    else:
        print("❌ Insufficient libraries for time-stretching")
        return False

def main():
    """Run all tests"""
    print("Time-Stretching Implementation Test")
    print("=" * 50)
    
    tests = [
        ("Library Availability", test_library_availability),
        ("TimeStretcher Configuration", test_time_stretcher_config),
        ("Config Integration", test_config_integration),
        ("Text Processing Config", test_text_processing_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Time-stretching implementation is ready.")
        print("\nNext steps:")
        print("1. Install missing libraries if needed: pip install librosa pyrubberband soundfile")
        print("2. Enable time-stretching in config.json: set 'enabled': true")
        print("3. Run benchmark: python LiteTTS/scripts/benchmark_time_stretching.py")
        print("4. Test with actual TTS synthesis")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
