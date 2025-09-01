#!/usr/bin/env python3
"""
Final comprehensive test to verify OpenWebUI TTS integration is working correctly
This simulates the exact request patterns that OpenWebUI sends
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8354"

def test_openwebui_typical_request():
    """Test the most common OpenWebUI request pattern"""
    print("🧪 Testing typical OpenWebUI request...")
    
    # This is what OpenWebUI typically sends
    payload = {
        "input": "Hello, this is a test from OpenWebUI. The integration should work seamlessly now.",
        "voice": "af_heart",
        "response_format": None,  # OpenWebUI often sends null
        "speed": 1.0,
        "model": None  # OpenWebUI includes this field
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json=payload,
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            audio_size = len(response.content)
            generation_time = end_time - start_time
            print(f"✅ SUCCESS: Generated {audio_size} bytes in {generation_time:.2f}s")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_openwebui_minimal_request():
    """Test minimal OpenWebUI request (only required fields)"""
    print("\n🧪 Testing minimal OpenWebUI request...")
    
    payload = {
        "input": "Minimal test",
        "voice": "af_heart"
        # No optional fields - should use defaults
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            audio_size = len(response.content)
            print(f"✅ SUCCESS: Generated {audio_size} bytes with defaults")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_openwebui_edge_cases():
    """Test edge cases that might occur with OpenWebUI"""
    print("\n🧪 Testing OpenWebUI edge cases...")
    
    edge_cases = [
        {
            "name": "Empty string format",
            "payload": {"input": "Test empty format", "voice": "af_heart", "response_format": ""}
        },
        {
            "name": "Null speed",
            "payload": {"input": "Test null speed", "voice": "af_heart", "speed": None}
        },
        {
            "name": "String speed",
            "payload": {"input": "Test string speed", "voice": "af_heart", "speed": "1.2"}
        },
        {
            "name": "All nulls",
            "payload": {"input": "Test all nulls", "voice": "af_heart", "response_format": None, "speed": None, "model": None}
        }
    ]
    
    success_count = 0
    for case in edge_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/v1/audio/speech",
                json=case["payload"],
                timeout=30
            )
            
            if response.status_code == 200:
                audio_size = len(response.content)
                print(f"✅ {case['name']}: Generated {audio_size} bytes")
                success_count += 1
            else:
                print(f"❌ {case['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {case['name']}: Exception {e}")
    
    print(f"\n📊 Edge cases: {success_count}/{len(edge_cases)} passed")
    return success_count == len(edge_cases)

def test_openwebui_error_handling():
    """Test that error handling works correctly for OpenWebUI"""
    print("\n🧪 Testing OpenWebUI error handling...")
    
    error_cases = [
        {
            "name": "Empty text",
            "payload": {"input": "", "voice": "af_heart"},
            "expected_status": 400
        },
        {
            "name": "Invalid voice",
            "payload": {"input": "Test", "voice": "nonexistent_voice"},
            "expected_status": 400
        },
        {
            "name": "Invalid format",
            "payload": {"input": "Test", "voice": "af_heart", "response_format": "invalid"},
            "expected_status": 400
        }
    ]
    
    success_count = 0
    for case in error_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/v1/audio/speech",
                json=case["payload"],
                timeout=30
            )
            
            if response.status_code == case["expected_status"]:
                try:
                    error_data = response.json()
                    if "error" in error_data.get("detail", {}):
                        print(f"✅ {case['name']}: Proper error message")
                        success_count += 1
                    else:
                        print(f"❌ {case['name']}: No error message in response")
                except:
                    print(f"❌ {case['name']}: Invalid JSON response")
            else:
                print(f"❌ {case['name']}: Expected {case['expected_status']}, got {response.status_code}")
                
        except Exception as e:
            print(f"❌ {case['name']}: Exception {e}")
    
    print(f"\n📊 Error handling: {success_count}/{len(error_cases)} passed")
    return success_count == len(error_cases)

def test_openwebui_performance():
    """Test performance characteristics important for OpenWebUI"""
    print("\n🧪 Testing OpenWebUI performance...")
    
    # Test cache performance (important for OpenWebUI responsiveness)
    test_text = "Performance test for OpenWebUI integration"
    payload = {"input": test_text, "voice": "af_heart"}
    
    try:
        # First request (cold)
        start_time = time.time()
        response1 = requests.post(f"{BASE_URL}/v1/audio/speech", json=payload, timeout=30)
        cold_time = time.time() - start_time
        
        if response1.status_code != 200:
            print(f"❌ Cold request failed: {response1.status_code}")
            return False
        
        # Second request (should be cached)
        start_time = time.time()
        response2 = requests.post(f"{BASE_URL}/v1/audio/speech", json=payload, timeout=30)
        cache_time = time.time() - start_time
        
        if response2.status_code != 200:
            print(f"❌ Cache request failed: {response2.status_code}")
            return False
        
        # Verify performance improvement
        if cache_time < cold_time and cache_time < 0.1:
            speedup = cold_time / cache_time
            print(f"✅ Cache performance: {speedup:.1f}x speedup ({cache_time:.3f}s vs {cold_time:.3f}s)")
            return True
        else:
            print(f"❌ Cache not working: {cache_time:.3f}s vs {cold_time:.3f}s")
            return False
            
    except Exception as e:
        print(f"❌ Performance test exception: {e}")
        return False

def main():
    """Run all OpenWebUI integration tests"""
    print("🌐 Final OpenWebUI TTS Integration Verification")
    print("=" * 60)
    print("This test simulates real OpenWebUI request patterns")
    print("=" * 60)
    
    tests = [
        ("Typical Request", test_openwebui_typical_request),
        ("Minimal Request", test_openwebui_minimal_request),
        ("Edge Cases", test_openwebui_edge_cases),
        ("Error Handling", test_openwebui_error_handling),
        ("Performance", test_openwebui_performance)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS:")
    print(f"✅ Passed: {passed}/{total} test categories")
    
    if passed == total:
        print("\n🎉 EXCELLENT! OpenWebUI integration is fully working!")
        print("💡 OpenWebUI users can now:")
        print("   • Send TTS requests with null/missing optional fields")
        print("   • Get clear error messages for invalid requests")
        print("   • Experience fast cache performance")
        print("   • Use any supported voice and format")
        print("\n🔧 Configuration for OpenWebUI:")
        print(f"   Base URL: {BASE_URL}/v1")
        print("   Model: Any voice name (e.g., 'af_heart', 'am_puck')")
        return 0
    else:
        print(f"\n❌ {total - passed} test categories failed")
        print("🔧 OpenWebUI integration may have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
