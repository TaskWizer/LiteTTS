#!/usr/bin/env python3
"""
Test script to verify that beta features are properly disabled
and the system works correctly without them
"""

import sys
import json
import time
import requests
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_beta_features_disabled():
    """Test that beta features are properly disabled"""
    print("🔍 Testing Beta Features Disabled State")
    print("=" * 50)

    # Load configuration
    config_path = Path(__file__).parent.parent.parent / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Check beta features configuration
    beta_features = config.get("beta_features", {})
    beta_enabled = beta_features.get("enabled", True)

    print(f"📊 Beta features enabled: {beta_enabled}")

    if beta_enabled:
        print("❌ ERROR: Beta features are enabled but should be disabled!")
        return False
    else:
        print("✅ Beta features are correctly disabled")

    # Check specific beta features
    phonetic_enabled = beta_features.get("phonetic_processing", {}).get("enabled", False)
    time_stretch_enabled = beta_features.get("time_stretching_optimization", {}).get("enabled", False)
    voice_mod_enabled = beta_features.get("voice_modulation", {}).get("enabled", False)

    print(f"📊 Phonetic processing: {phonetic_enabled}")
    print(f"📊 Time stretching: {time_stretch_enabled}")
    print(f"📊 Voice modulation: {voice_mod_enabled}")

    # Check pronunciation dictionary
    dict_enabled = config.get("pronunciation_dictionary", {}).get("enabled", True)
    print(f"📊 Pronunciation dictionary: {dict_enabled}")

    if dict_enabled:
        print("⚠️  WARNING: Pronunciation dictionary is enabled - this might cause issues")
    else:
        print("✅ Pronunciation dictionary is disabled")

    return True

def test_text_processing_without_beta():
    """Test text processing pipeline without beta features"""
    print("\n🔧 Testing Text Processing Without Beta Features")
    print("=" * 50)

    try:
        from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode

        # Create processor
        processor = UnifiedTextProcessor(enable_advanced_features=True)

        # Test cases
        test_cases = [
            "Hello? How are you?",  # Question mark test
            "The cost is $50.99",   # Currency test
            "Use the * symbol",     # Asterisk test
            "Visit example.com",    # URL test
            "Email test@example.com" # Email test
        ]

        options = ProcessingOptions(mode=ProcessingMode.ENHANCED)

        print("📝 Testing text processing:")

        for i, test_text in enumerate(test_cases, 1):
            print(f"\n{i}. Input: '{test_text}'")

            try:
                start_time = time.perf_counter()
                result = processor.process_text(test_text, options)
                processing_time = time.perf_counter() - start_time

                print(f"   ✅ Output: '{result.processed_text}'")
                print(f"   ⏱️  Time: {processing_time:.3f}s")
                print(f"   📊 Stages: {', '.join(result.stages_completed)}")

                # Check for phonetic processing (should be skipped)
                if "phonetic_processing_skipped" in result.stages_completed:
                    print("   ✅ Phonetic processing correctly skipped")
                elif "phonetic_processing" in result.stages_completed:
                    print("   ⚠️  WARNING: Phonetic processing was executed (should be disabled)")

            except Exception as e:
                print(f"   ❌ Error: {e}")
                return False

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_api_without_beta():
    """Test TTS API without beta features"""
    print("\n🎯 Testing TTS API Without Beta Features")
    print("=" * 50)

    # Test cases
    test_cases = [
        "Hello? How are you?",
        "The cost is $50.99",
        "Use the * symbol carefully"
    ]

    api_url = "http://localhost:8354/v1/audio/speech"

    print("📝 Testing TTS API:")

    success_count = 0

    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. Input: '{test_text}'")

        payload = {
            "model": "kokoro",
            "input": test_text,
            "voice": "af_heart",
            "response_format": "mp3",
            "speed": 1.0
        }

        try:
            start_time = time.time()
            response = requests.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            processing_time = time.time() - start_time

            if response.status_code == 200:
                content_length = len(response.content)
                print(f"   ✅ Success: {content_length} bytes")
                print(f"   ⏱️  Time: {processing_time:.2f}s")

                if processing_time < 5.0:  # Should be fast without beta features
                    print("   🚀 Performance: Good")
                    success_count += 1
                else:
                    print("   ⚠️  Performance: Slow")

            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

    print(f"\n📊 API Test Summary: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)

def main():
    """Main test function"""
    print("🚀 Beta Features Disabled Validation")
    print("=" * 60)

    success = True

    # Test 1: Verify beta features are disabled
    if not test_beta_features_disabled():
        success = False

    # Test 2: Test text processing without beta features
    if not test_text_processing_without_beta():
        success = False

    # Test 3: Test TTS API without beta features
    try:
        if not test_api_without_beta():
            success = False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        success = False

    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ VALIDATION SUCCESSFUL!")
        print("\n🎉 System is working correctly with beta features disabled:")
        print("   - Beta features are properly disabled")
        print("   - Text processing pipeline works without beta features")
        print("   - TTS API generates audio successfully")
        print("   - Performance is good without experimental features")
        print("\n🔒 The system is stable and production-ready in this configuration.")
    else:
        print("❌ VALIDATION FAILED!")
        print("   Some components are not working correctly.")
        print("   Check the error messages above.")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)