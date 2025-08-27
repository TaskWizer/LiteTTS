#!/usr/bin/env python3
"""
Diagnose the 500 error by testing components individually
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_server_endpoints():
    """Test all server endpoints"""
    base_url = "http://192.168.1.139:8000"
    
    endpoints = [
        ("Root", "/"),
        ("Health", "/health"),
        ("Debug", "/debug"),
        ("Voices", "/voices"),
        ("Models", "/v1/models"),
        ("Test TTS", "/test-tts")
    ]
    
    print("🌐 Testing server endpoints...")
    for name, endpoint in endpoints:
        try:
            if endpoint == "/test-tts":
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name} ({endpoint}): OK")
                if endpoint in ["/debug", "/health"]:
                    data = response.json()
                    if "model_loaded" in data:
                        print(f"   Model loaded: {data['model_loaded']}")
                    if "available_voices" in data:
                        print(f"   Voices: {len(data.get('available_voices', []))}")
            else:
                print(f"❌ {name} ({endpoint}): Status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"❌ {name} ({endpoint}): Error - {e}")

def test_tts_request():
    """Test a simple TTS request"""
    base_url = "http://192.168.1.139:8000"
    
    test_data = {
        "input": "Hello world",
        "model": "kokoro",
        "voice": "af_heart",
        "response_format": "mp3",
        "speed": 1.0
    }
    
    print("\n🎤 Testing TTS request...")
    
    for endpoint in ["/audio/speech", "/v1/audio/speech"]:
        try:
            print(f"   Testing {endpoint}...")
            response = requests.post(
                f"{base_url}{endpoint}",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: Success! Audio generated ({len(response.content)} bytes)")
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
                print(f"   Error: {response.text[:500]}")
                
        except Exception as e:
            print(f"❌ {endpoint}: Exception - {e}")

def check_local_setup():
    """Check local file setup"""
    print("\n📁 Checking local setup...")
    
    files_to_check = [
        "app.py",
        "LiteTTS/downloader.py",
        "LiteTTS/models/model_q8f16.onnx",
        "LiteTTS/voices/voices-v1.0.bin"
    ]
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file_path}: {size:,} bytes")
        else:
            print(f"❌ {file_path}: Missing")

def main():
    print("🔍 Kokoro ONNX TTS API Diagnostics")
    print("=" * 50)
    
    # Check local setup first
    check_local_setup()
    
    # Test server endpoints
    test_server_endpoints()
    
    # Test TTS requests
    test_tts_request()
    
    print("\n💡 Next steps:")
    print("1. Check server logs for detailed error messages")
    print("2. If model not loaded, check internet connection")
    print("3. If endpoints fail, restart the server")
    print("4. Check server console output for initialization errors")

if __name__ == "__main__":
    main()