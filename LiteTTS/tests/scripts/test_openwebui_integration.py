#!/usr/bin/env python3
"""
Test script to simulate OpenWebUI TTS requests and verify integration fixes
Tests various request patterns that OpenWebUI might send
"""

import requests
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

def test_openwebui_null_format():
    """Test OpenWebUI request with null response_format"""
    try:
        # This simulates what OpenWebUI might send
        payload = {
            "input": "Hello from OpenWebUI test",
            "voice": "af_heart",
            "response_format": None  # This is the problematic case
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            audio_size = len(response.content)
            if audio_size > 1000:
                log_test("OpenWebUI: Null Format", True, f"Generated {audio_size} bytes, defaulted to mp3")
                return True
            else:
                log_test("OpenWebUI: Null Format", False, f"Audio too small: {audio_size} bytes")
                return False
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            log_test("OpenWebUI: Null Format", False, f"HTTP {response.status_code}: {error_data}")
            return False
        
    except Exception as e:
        log_test("OpenWebUI: Null Format", False, f"Exception: {e}")
        return False

def test_openwebui_missing_format():
    """Test OpenWebUI request with missing response_format field"""
    try:
        payload = {
            "input": "Hello from OpenWebUI test without format",
            "voice": "af_heart"
            # response_format field completely missing
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            audio_size = len(response.content)
            if audio_size > 1000:
                log_test("OpenWebUI: Missing Format", True, f"Generated {audio_size} bytes, defaulted to mp3")
                return True
            else:
                log_test("OpenWebUI: Missing Format", False, f"Audio too small: {audio_size} bytes")
                return False
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            log_test("OpenWebUI: Missing Format", False, f"HTTP {response.status_code}: {error_data}")
            return False
        
    except Exception as e:
        log_test("OpenWebUI: Missing Format", False, f"Exception: {e}")
        return False

def test_openwebui_empty_format():
    """Test OpenWebUI request with empty string response_format"""
    try:
        payload = {
            "input": "Hello from OpenWebUI test with empty format",
            "voice": "af_heart",
            "response_format": ""  # Empty string
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            audio_size = len(response.content)
            if audio_size > 1000:
                log_test("OpenWebUI: Empty Format", True, f"Generated {audio_size} bytes, defaulted to mp3")
                return True
            else:
                log_test("OpenWebUI: Empty Format", False, f"Audio too small: {audio_size} bytes")
                return False
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            log_test("OpenWebUI: Empty Format", False, f"HTTP {response.status_code}: {error_data}")
            return False
        
    except Exception as e:
        log_test("OpenWebUI: Empty Format", False, f"Exception: {e}")
        return False

def test_openwebui_null_speed():
    """Test OpenWebUI request with null speed"""
    try:
        payload = {
            "input": "Hello from OpenWebUI test with null speed",
            "voice": "af_heart",
            "response_format": "mp3",
            "speed": None  # Null speed
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            audio_size = len(response.content)
            if audio_size > 1000:
                log_test("OpenWebUI: Null Speed", True, f"Generated {audio_size} bytes, defaulted speed")
                return True
            else:
                log_test("OpenWebUI: Null Speed", False, f"Audio too small: {audio_size} bytes")
                return False
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            log_test("OpenWebUI: Null Speed", False, f"HTTP {response.status_code}: {error_data}")
            return False
        
    except Exception as e:
        log_test("OpenWebUI: Null Speed", False, f"Exception: {e}")
        return False

def test_openwebui_all_nulls():
    """Test OpenWebUI request with all optional fields as null"""
    try:
        payload = {
            "input": "Hello from OpenWebUI test with all nulls",
            "voice": "af_heart",
            "response_format": None,
            "speed": None
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            audio_size = len(response.content)
            if audio_size > 1000:
                log_test("OpenWebUI: All Nulls", True, f"Generated {audio_size} bytes, all defaults applied")
                return True
            else:
                log_test("OpenWebUI: All Nulls", False, f"Audio too small: {audio_size} bytes")
                return False
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            log_test("OpenWebUI: All Nulls", False, f"HTTP {response.status_code}: {error_data}")
            return False
        
    except Exception as e:
        log_test("OpenWebUI: All Nulls", False, f"Exception: {e}")
        return False

def test_openwebui_valid_request():
    """Test normal OpenWebUI request with valid values"""
    try:
        payload = {
            "input": "Hello from OpenWebUI test with valid values",
            "voice": "af_heart",
            "response_format": "mp3",
            "speed": 1.0
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            audio_size = len(response.content)
            if audio_size > 1000:
                log_test("OpenWebUI: Valid Request", True, f"Generated {audio_size} bytes")
                return True
            else:
                log_test("OpenWebUI: Valid Request", False, f"Audio too small: {audio_size} bytes")
                return False
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            log_test("OpenWebUI: Valid Request", False, f"HTTP {response.status_code}: {error_data}")
            return False
        
    except Exception as e:
        log_test("OpenWebUI: Valid Request", False, f"Exception: {e}")
        return False

def test_openwebui_edge_cases():
    """Test various edge cases that might occur with OpenWebUI"""
    edge_cases = [
        {"name": "Number Format", "payload": {"input": "Test", "voice": "af_heart", "response_format": 123}},
        {"name": "Boolean Format", "payload": {"input": "Test", "voice": "af_heart", "response_format": True}},
        {"name": "String Speed", "payload": {"input": "Test", "voice": "af_heart", "speed": "1.0"}},
    ]
    
    success_count = 0
    for case in edge_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/v1/audio/speech",
                json=case["payload"],
                timeout=30
            )
            
            # These should either succeed with conversion or fail gracefully
            if response.status_code in [200, 400]:
                success_count += 1
                if response.status_code == 200:
                    log_test(f"Edge Case: {case['name']}", True, "Converted and succeeded")
                else:
                    log_test(f"Edge Case: {case['name']}", True, "Failed gracefully with clear error")
            else:
                log_test(f"Edge Case: {case['name']}", False, f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            log_test(f"Edge Case: {case['name']}", False, f"Exception: {e}")
    
    return success_count == len(edge_cases)

def run_openwebui_tests():
    """Run all OpenWebUI integration tests"""
    print("🌐 Running OpenWebUI TTS Integration Tests")
    print("=" * 50)
    
    # Test null/missing field handling
    print("\n🔧 Testing Null/Missing Field Handling:")
    test_openwebui_null_format()
    test_openwebui_missing_format()
    test_openwebui_empty_format()
    test_openwebui_null_speed()
    test_openwebui_all_nulls()
    
    # Test valid requests
    print("\n✅ Testing Valid Requests:")
    test_openwebui_valid_request()
    
    # Test edge cases
    print("\n🎯 Testing Edge Cases:")
    test_openwebui_edge_cases()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 OpenWebUI Integration Test Summary:")
    
    passed = sum(1 for result in TEST_RESULTS if result["success"])
    total = len(TEST_RESULTS)
    
    print(f"✅ Passed: {passed}/{total} tests")
    
    if passed == total:
        print("🎉 All OpenWebUI integration tests passed!")
        print("💡 OpenWebUI should now work correctly with the Kokoro ONNX TTS API")
        return 0
    else:
        print("❌ Some tests failed. OpenWebUI integration may have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(run_openwebui_tests())
