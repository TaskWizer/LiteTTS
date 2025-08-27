#!/usr/bin/env python3
"""
Test the TTS API directly to see what's failing
"""

import requests
import json
import sys

def test_endpoints():
    """Test all endpoints to isolate the issue"""
    base_url = "http://192.168.1.139:8000"
    
    print("🔍 Testing Kokoro ONNX TTS API Endpoints")
    print("=" * 50)
    
    # Test basic endpoints first
    endpoints = [
        ("Health Check", "GET", "/health"),
        ("Debug Info", "GET", "/debug"),
        ("Root Info", "GET", "/"),
        ("Models", "GET", "/v1/models"),
        ("Voices V1", "GET", "/v1/audio/voices"),
        ("Test TTS", "POST", "/test-tts")
    ]
    
    for name, method, endpoint in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            print(f"{'✅' if response.status_code == 200 else '❌'} {name}: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   Error: {response.text[:200]}")
            elif endpoint == "/debug":
                data = response.json()
                print(f"   Model loaded: {data.get('model_loaded', 'unknown')}")
                print(f"   Model exists: {data.get('model_exists', 'unknown')}")
                print(f"   Voices exists: {data.get('voices_exists', 'unknown')}")
                
        except Exception as e:
            print(f"❌ {name}: Exception - {e}")
    
    # Test the actual TTS endpoints
    print(f"\n🎤 Testing TTS Endpoints")
    print("-" * 30)
    
    # Simple request data
    simple_data = {
        "input": "Hello world",
        "model": "kokoro",
        "voice": "af_heart"
    }
    
    # Full request data matching the schema
    full_data = {
        "model": "kokoro",
        "input": "Hello world",
        "voice": "af_heart",
        "response_format": "mp3",
        "download_format": "mp3",
        "speed": 1.0,
        "stream": True,
        "return_download_link": False,
        "lang_code": "en-us",
        "volume_multiplier": 1.0,
        "normalization_options": {
            "normalize": True,
            "unit_normalization": False,
            "url_normalization": True,
            "email_normalization": True,
            "optional_pluralization_normalization": True,
            "phone_normalization": True,
            "replace_remaining_symbols": True
        }
    }
    
    test_cases = [
        ("Simple Request to /audio/speech", "/audio/speech", simple_data),
        ("Simple Request to /v1/audio/speech", "/v1/audio/speech", simple_data),
        ("Full Request to /v1/audio/speech", "/v1/audio/speech", full_data)
    ]
    
    for name, endpoint, data in test_cases:
        print(f"\n🧪 {name}")
        print(f"   Endpoint: {endpoint}")
        print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            response = requests.post(
                f"{base_url}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Success! Audio size: {len(response.content)} bytes")
                print(f"   Content-Type: {response.headers.get('content-type')}")
            else:
                print(f"❌ Failed: Status {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def main():
    print("🚨 IMPORTANT: Check your server console for detailed error logs!")
    print("Look for lines starting with ❌ or 'Generation failed'")
    print()
    
    test_endpoints()
    
    print(f"\n💡 Next Steps:")
    print("1. Check your server console output for detailed errors")
    print("2. If model not loaded, check if kokoro_onnx is installed: uv run pip list | grep kokoro")
    print("3. If Docker/container issue, try running both services natively")
    print("4. Check if OpenWebUI and TTS API can reach each other")

if __name__ == "__main__":
    main()