#!/usr/bin/env python3
"""
Comprehensive API endpoint testing script
"""

import json
import time

import requests


def test_health_endpoint():
    """Test the health endpoint"""
    print("🏥 Testing Health Endpoint")
    print("-" * 30)

    try:
        response = requests.get("http://localhost:8354/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health endpoint accessible")
            try:
                data = response.json()
                print(f"   📊 Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   📊 Response: {response.text}")
        else:
            print(f"   ❌ Health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health endpoint error: {e}")

def test_voices_endpoint():
    """Test the voices endpoint"""
    print("\n🎭 Testing Voices Endpoint")
    print("-" * 30)

    try:
        response = requests.get("http://localhost:8354/v1/voices", timeout=10)
        if response.status_code == 200:
            print("   ✅ Voices endpoint accessible")
            try:
                data = response.json()
                if isinstance(data, dict) and 'data' in data:
                    voices = data['data']
                    print(f"   📊 Found {len(voices)} voices")
                    if voices:
                        print(f"   🎤 Sample voice: {voices[0].get('id', 'unknown')}")
                elif isinstance(data, list):
                    print(f"   📊 Found {len(data)} voices")
                    if data:
                        print(f"   🎤 Sample voice: {data[0]}")
                else:
                    print(f"   📊 Response: {data}")
            except Exception as e:
                print(f"   ⚠️ Could not parse JSON: {e}")
                print(f"   📊 Raw response: {response.text[:200]}...")
        else:
            print(f"   ❌ Voices endpoint returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Voices endpoint error: {e}")

def test_models_endpoint():
    """Test the models endpoint"""
    print("\n🤖 Testing Models Endpoint")
    print("-" * 30)

    try:
        response = requests.get("http://localhost:8354/v1/models", timeout=10)
        if response.status_code == 200:
            print("   ✅ Models endpoint accessible")
            try:
                data = response.json()
                if isinstance(data, dict) and 'data' in data:
                    models = data['data']
                    print(f"   📊 Found {len(models)} models")
                    if models:
                        print(f"   🤖 Sample model: {models[0].get('id', 'unknown')}")
                else:
                    print(f"   📊 Response: {data}")
            except Exception as e:
                print(f"   ⚠️ Could not parse JSON: {e}")
                print(f"   📊 Raw response: {response.text[:200]}...")
        else:
            print(f"   ❌ Models endpoint returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Models endpoint error: {e}")

def test_tts_endpoint():
    """Test the main TTS endpoint"""
    print("\n🗣️ Testing TTS Endpoint")
    print("-" * 30)

    test_cases = [
        {
            "name": "Basic TTS",
            "payload": {
                "model": "kokoro",
                "input": "Hello, this is a test.",
                "voice": "af_heart",
                "response_format": "mp3"
            }
        },
        {
            "name": "Different Voice",
            "payload": {
                "model": "kokoro",
                "input": "Testing with a different voice.",
                "voice": "am_puck",
                "response_format": "wav"
            }
        },
        {
            "name": "Speed Control",
            "payload": {
                "model": "kokoro",
                "input": "Testing speed control.",
                "voice": "af_heart",
                "speed": 1.5,
                "response_format": "mp3"
            }
        }
    ]

    for test_case in test_cases:
        print(f"\n   🧪 {test_case['name']}")
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8354/v1/audio/speech",
                json=test_case["payload"],
                timeout=30
            )
            end_time = time.time()

            if response.status_code == 200:
                audio_size = len(response.content)
                generation_time = end_time - start_time
                print(f"      ✅ SUCCESS: {audio_size:,} bytes in {generation_time:.3f}s")

                # Check content type
                content_type = response.headers.get('content-type', 'unknown')
                print(f"      📋 Content-Type: {content_type}")

            else:
                print(f"      ❌ FAILED: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"      📋 Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"      📋 Error: {response.text[:200]}")

        except requests.exceptions.Timeout:
            print("      ⏰ TIMEOUT: Request took too long")
        except Exception as e:
            print(f"      ❌ ERROR: {e}")

def test_error_handling():
    """Test error handling"""
    print("\n🚨 Testing Error Handling")
    print("-" * 30)

    error_test_cases = [
        {
            "name": "Invalid Voice",
            "payload": {
                "model": "kokoro",
                "input": "Test with invalid voice",
                "voice": "invalid_voice",
                "response_format": "mp3"
            },
            "expected_status": [400, 422]
        },
        {
            "name": "Empty Text",
            "payload": {
                "model": "kokoro",
                "input": "",
                "voice": "af_heart",
                "response_format": "mp3"
            },
            "expected_status": [400, 422]
        },
        {
            "name": "Invalid Format",
            "payload": {
                "model": "kokoro",
                "input": "Test with invalid format",
                "voice": "af_heart",
                "response_format": "invalid_format"
            },
            "expected_status": [400, 422]
        },
        {
            "name": "Invalid Speed",
            "payload": {
                "model": "kokoro",
                "input": "Test with invalid speed",
                "voice": "af_heart",
                "speed": -1.0,
                "response_format": "mp3"
            },
            "expected_status": [400, 422]
        }
    ]

    for test_case in error_test_cases:
        print(f"\n   🧪 {test_case['name']}")
        try:
            response = requests.post(
                "http://localhost:8354/v1/audio/speech",
                json=test_case["payload"],
                timeout=15
            )

            if response.status_code in test_case["expected_status"]:
                print(f"      ✅ Correctly returned {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"      📋 Error message: {error_data.get('detail', 'No detail')}")
                except:
                    pass
            else:
                print(f"      ⚠️ Unexpected status: {response.status_code} (expected {test_case['expected_status']})")

        except Exception as e:
            print(f"      ❌ ERROR: {e}")

def test_server_status():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Starting API Endpoint Testing")
    print("=" * 50)

    if not test_server_status():
        print("❌ Server not accessible at http://localhost:8080")
        print("💡 Please start the server first:")
        print("   python LiteTTS/start_server.py")
        exit(1)

    print("✅ Server is accessible")

    # Run all tests
    test_health_endpoint()
    test_voices_endpoint()
    test_models_endpoint()
    test_tts_endpoint()
    test_error_handling()

    print("\n" + "=" * 50)
    print("✅ API endpoint testing complete!")
