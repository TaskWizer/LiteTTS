#!/usr/bin/env python3
"""
Comprehensive test script to verify all debug fixes for Kokoro ONNX TTS API
Tests validation, error handling, audio generation, and cache integrity
"""

import requests
import time
import json
import sys
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8354"
TEST_RESULTS = []

def log_test(test_name, success, details=""):
    """Log test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")
    
    TEST_RESULTS.append({
        "test": test_name,
        "success": success,
        "details": details
    })

def test_validation_empty_text():
    """Test validation with empty text"""
    try:
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json={"input": "", "voice": "af_heart", "response_format": "mp3"},
            timeout=10
        )
        
        if response.status_code == 400:
            error_data = response.json()
            if "error" in error_data.get("detail", {}) and "empty" in error_data["detail"]["error"].lower():
                log_test("Validation: Empty Text", True, f"Correct error: {error_data['detail']['error']}")
                return True
        
        log_test("Validation: Empty Text", False, f"Unexpected response: {response.status_code}")
        return False
        
    except Exception as e:
        log_test("Validation: Empty Text", False, f"Exception: {e}")
        return False

def test_validation_invalid_voice():
    """Test validation with invalid voice"""
    try:
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json={"input": "Test", "voice": "invalid_voice", "response_format": "mp3"},
            timeout=10
        )
        
        if response.status_code == 400:
            error_data = response.json()
            if "error" in error_data.get("detail", {}) and "not found" in error_data["detail"]["error"].lower():
                log_test("Validation: Invalid Voice", True, f"Correct error with voice list")
                return True
        
        log_test("Validation: Invalid Voice", False, f"Unexpected response: {response.status_code}")
        return False
        
    except Exception as e:
        log_test("Validation: Invalid Voice", False, f"Exception: {e}")
        return False

def test_validation_invalid_format():
    """Test validation with invalid format"""
    try:
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json={"input": "Test", "voice": "af_heart", "response_format": "invalid_format"},
            timeout=10
        )
        
        if response.status_code == 400:
            error_data = response.json()
            if "error" in error_data.get("detail", {}) and "unsupported format" in error_data["detail"]["error"].lower():
                log_test("Validation: Invalid Format", True, f"Correct error with format list")
                return True
        
        log_test("Validation: Invalid Format", False, f"Unexpected response: {response.status_code}")
        return False
        
    except Exception as e:
        log_test("Validation: Invalid Format", False, f"Exception: {e}")
        return False

def test_audio_generation_basic():
    """Test basic audio generation"""
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json={"input": "Hello, world! This is a basic test.", "voice": "af_heart", "response_format": "mp3"},
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            audio_size = len(response.content)
            generation_time = end_time - start_time
            
            if audio_size > 1000:  # Should have substantial audio data
                log_test("Audio Generation: Basic", True, f"Generated {audio_size} bytes in {generation_time:.2f}s")
                return True, generation_time, audio_size
            else:
                log_test("Audio Generation: Basic", False, f"Audio too small: {audio_size} bytes")
                return False, generation_time, audio_size
        
        log_test("Audio Generation: Basic", False, f"HTTP {response.status_code}")
        return False, 0, 0
        
    except Exception as e:
        log_test("Audio Generation: Basic", False, f"Exception: {e}")
        return False, 0, 0

def test_audio_generation_problematic_text():
    """Test audio generation with previously problematic text"""
    try:
        problematic_text = "This is a longer test sentence to see if we can reproduce the empty audio generation error that was mentioned in the requirements. Let me make it even longer to increase the chance of triggering the phonemizer issue."
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json={"input": problematic_text, "voice": "af_heart", "response_format": "mp3"},
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            audio_size = len(response.content)
            generation_time = end_time - start_time
            
            if audio_size > 5000:  # Should have substantial audio for long text
                log_test("Audio Generation: Problematic Text", True, f"Generated {audio_size} bytes in {generation_time:.2f}s")
                return True
            else:
                log_test("Audio Generation: Problematic Text", False, f"Audio too small: {audio_size} bytes")
                return False
        
        log_test("Audio Generation: Problematic Text", False, f"HTTP {response.status_code}")
        return False
        
    except Exception as e:
        log_test("Audio Generation: Problematic Text", False, f"Exception: {e}")
        return False

def test_cache_integrity():
    """Test cache hit performance and integrity"""
    try:
        test_text = "Cache integrity test with unique text for testing purposes."
        
        # First request (cold start)
        start_time = time.time()
        response1 = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json={"input": test_text, "voice": "af_heart", "response_format": "mp3"},
            timeout=30
        )
        cold_time = time.time() - start_time
        
        if response1.status_code != 200:
            log_test("Cache Integrity: Cold Start", False, f"HTTP {response1.status_code}")
            return False
        
        cold_audio = response1.content
        
        # Second request (should be cached)
        start_time = time.time()
        response2 = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json={"input": test_text, "voice": "af_heart", "response_format": "mp3"},
            timeout=30
        )
        cache_time = time.time() - start_time
        
        if response2.status_code != 200:
            log_test("Cache Integrity: Cache Hit", False, f"HTTP {response2.status_code}")
            return False
        
        cache_audio = response2.content
        
        # Verify cache performance and integrity
        if cache_time < cold_time and cache_time < 0.1:  # Cache should be much faster
            if cold_audio == cache_audio:  # Audio should be identical
                speedup = cold_time / cache_time
                log_test("Cache Integrity", True, f"Cache hit {speedup:.1f}x faster ({cache_time:.3f}s vs {cold_time:.3f}s), audio identical")
                return True
            else:
                log_test("Cache Integrity", False, f"Audio mismatch: {len(cold_audio)} vs {len(cache_audio)} bytes")
                return False
        else:
            log_test("Cache Integrity", False, f"Cache not faster: {cache_time:.3f}s vs {cold_time:.3f}s")
            return False
        
    except Exception as e:
        log_test("Cache Integrity", False, f"Exception: {e}")
        return False

def test_special_characters():
    """Test handling of special characters and numbers"""
    try:
        special_text = "Test with special chars: @#$%^&*()_+ and numbers 123456789!"
        
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json={"input": special_text, "voice": "af_heart", "response_format": "mp3"},
            timeout=30
        )
        
        if response.status_code == 200:
            audio_size = len(response.content)
            if audio_size > 1000:
                log_test("Special Characters", True, f"Generated {audio_size} bytes")
                return True
            else:
                log_test("Special Characters", False, f"Audio too small: {audio_size} bytes")
                return False
        
        log_test("Special Characters", False, f"HTTP {response.status_code}")
        return False
        
    except Exception as e:
        log_test("Special Characters", False, f"Exception: {e}")
        return False

def test_different_voices():
    """Test multiple voices work correctly"""
    voices_to_test = ["af_heart", "am_puck", "af_sarah"]
    success_count = 0
    
    for voice in voices_to_test:
        try:
            response = requests.post(
                f"{BASE_URL}/v1/audio/speech",
                json={"input": f"Testing voice {voice}", "voice": voice, "response_format": "mp3"},
                timeout=30
            )
            
            if response.status_code == 200 and len(response.content) > 1000:
                success_count += 1
            
        except Exception:
            pass
    
    if success_count == len(voices_to_test):
        log_test("Multiple Voices", True, f"All {success_count} voices working")
        return True
    else:
        log_test("Multiple Voices", False, f"Only {success_count}/{len(voices_to_test)} voices working")
        return False

def run_all_tests():
    """Run all debug fix tests"""
    print("🧪 Running Kokoro ONNX TTS API Debug Fix Tests")
    print("=" * 50)
    
    # Test validation fixes
    print("\n📋 Testing Input Validation Fixes:")
    test_validation_empty_text()
    test_validation_invalid_voice()
    test_validation_invalid_format()
    
    # Test audio generation fixes
    print("\n🎵 Testing Audio Generation Fixes:")
    basic_success, gen_time, audio_size = test_audio_generation_basic()
    test_audio_generation_problematic_text()
    test_special_characters()
    
    # Test cache integrity
    print("\n💾 Testing Cache Integrity:")
    test_cache_integrity()
    
    # Test multiple voices
    print("\n🎭 Testing Voice Support:")
    test_different_voices()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = sum(1 for result in TEST_RESULTS if result["success"])
    total = len(TEST_RESULTS)
    
    print(f"✅ Passed: {passed}/{total} tests")
    
    if passed == total:
        print("🎉 All tests passed! Debug fixes are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
