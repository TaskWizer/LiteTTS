#!/usr/bin/env python3
"""
Minimal OpenWebUI integration test
Tests the most basic functionality to isolate any issues
"""

import requests
import json
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:8354"

def test_minimal_request():
    """Test the most minimal possible request"""
    print("🧪 Testing minimal OpenWebUI request...")
    
    # Absolute minimal payload
    payload = {
        "input": "Hello",
        "voice": "af_heart"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "OpenWebUI-Test/1.0"
            },
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"   Content-Length: {response.headers.get('content-length', 'Not set')}")
        print(f"   Response Size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Save the audio file
            with open("minimal_test.mp3", "wb") as f:
                f.write(response.content)
            print(f"   ✅ SUCCESS: Audio saved to minimal_test.mp3")
            return True
        else:
            print(f"   ❌ FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False

def test_openwebui_headers():
    """Test with various OpenWebUI-like headers"""
    print("\n🧪 Testing with OpenWebUI-like headers...")

    headers_to_test = [
        {"User-Agent": "Mozilla/5.0 OpenWebUI"},
        {"User-Agent": "OpenWebUI/1.0"},
        {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"},
        {"User-Agent": "Mozilla/5.0 (Android 12; Mobile; rv:109.0) Gecko/109.0 Firefox/109.0"}
    ]

    payload = {
        "input": "Testing headers",
        "voice": "af_heart",
        "response_format": "mp3"
    }

    success_count = 0

    for i, headers in enumerate(headers_to_test):
        print(f"   Test {i+1}: {headers['User-Agent'][:50]}...")

        try:
            response = requests.post(
                f"{BASE_URL}/v1/audio/speech",
                json=payload,
                headers={**headers, "Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200:
                print(f"      ✅ SUCCESS: {len(response.content)} bytes")
                success_count += 1
            else:
                print(f"      ❌ FAILED: {response.status_code}")

        except Exception as e:
            print(f"      ❌ EXCEPTION: {e}")

    return success_count == len(headers_to_test)

def test_edge_cases():
    """Test edge cases that might cause issues"""
    print("\n🧪 Testing edge cases...")

    test_cases = [
        {
            "name": "Empty optional fields",
            "payload": {
                "input": "Test",
                "voice": "af_heart",
                "model": None,
                "response_format": None,
                "speed": None
            }
        },
        {
            "name": "String speed",
            "payload": {
                "input": "Test",
                "voice": "af_heart",
                "speed": "1.0"
            }
        },
        {
            "name": "Very short text",
            "payload": {
                "input": "Hi",
                "voice": "af_heart"
            }
        },
        {
            "name": "Long text",
            "payload": {
                "input": "This is a longer text that should test the system's ability to handle more substantial content without any issues or truncation problems.",
                "voice": "af_heart"
            }
        }
    ]

    success_count = 0

    for test_case in test_cases:
        print(f"   {test_case['name']}...")

        try:
            response = requests.post(
                f"{BASE_URL}/v1/audio/speech",
                json=test_case["payload"],
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "OpenWebUI-EdgeCase-Test/1.0"
                },
                timeout=30
            )

            if response.status_code == 200:
                print(f"      ✅ SUCCESS: {len(response.content)} bytes")
                success_count += 1
            else:
                print(f"      ❌ FAILED: {response.status_code} - {response.text[:100]}")

        except Exception as e:
            print(f"      ❌ EXCEPTION: {e}")

    return success_count == len(test_cases)

def test_streaming_endpoint():
    """Test the streaming endpoint"""
    print("\n🧪 Testing streaming endpoint...")
    
    payload = {
        "input": "Testing streaming endpoint",
        "voice": "af_heart",
        "response_format": "mp3"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/audio/stream",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "OpenWebUI-Stream-Test/1.0"
            },
            timeout=30,
            stream=True
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Transfer-Encoding: {response.headers.get('transfer-encoding', 'Not set')}")
        
        if response.status_code == 200:
            # Collect streaming data
            chunks = []
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    chunks.append(chunk)
            
            total_size = sum(len(chunk) for chunk in chunks)
            print(f"   ✅ SUCCESS: {len(chunks)} chunks, {total_size} total bytes")
            
            # Save streamed audio
            with open("stream_test.mp3", "wb") as f:
                for chunk in chunks:
                    f.write(chunk)
            print(f"   💾 Saved to stream_test.mp3")
            return True
        else:
            print(f"   ❌ FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False

def test_compatibility_routes():
    """Test OpenWebUI compatibility routes"""
    print("\n🧪 Testing compatibility routes...")

    routes_to_test = [
        "/v1/audio/stream/audio/speech",
        "/v1/audio/speech/audio/speech"
    ]

    payload = {
        "input": "Testing compatibility",
        "voice": "af_heart"
    }

    success_count = 0

    for route in routes_to_test:
        print(f"   Route: {route}")

        try:
            response = requests.post(
                f"{BASE_URL}{route}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "OpenWebUI-Compat-Test/1.0"
                },
                timeout=30
            )

            if response.status_code == 200:
                print(f"      ✅ SUCCESS: {len(response.content)} bytes")
                success_count += 1
            else:
                print(f"      ❌ FAILED: {response.status_code}")

        except Exception as e:
            print(f"      ❌ EXCEPTION: {e}")

    return success_count == len(routes_to_test)

def main():
    """Run all minimal tests"""
    print("🌐 OpenWebUI Minimal Integration Test")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            sys.exit(1)
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        sys.exit(1)
    
    # Run tests
    tests = [
        test_minimal_request,
        test_openwebui_headers,
        test_edge_cases,
        test_streaming_endpoint,
        test_compatibility_routes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
    
    print(f"\n📊 Results: {passed}/{total} test categories passed")
    
    if passed == total:
        print("🎉 All minimal tests passed! OpenWebUI integration is working.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
