#!/usr/bin/env python3
"""
Simple test script for the Kokoro ONNX TTS API
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Kokoro ONNX TTS API")
    print("=" * 40)
    
    # Check if server is running
    print("\n0. Checking if server is running...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Server is running!")
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        print("   Please start the server first: python start_server.py")
        return
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test models endpoint
    print("\n2. Testing models endpoint...")
    try:
        response = requests.get(f"{base_url}/v1/models")
        print(f"   Status: {response.status_code}")
        print(f"   Models: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test voices endpoint
    print("\n3. Testing voices endpoint...")
    try:
        response = requests.get(f"{base_url}/voices")
        print(f"   Status: {response.status_code}")
        voices_data = response.json()
        print(f"   Available voices: {voices_data.get('voices', [])}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test TTS generation
    print("\n4. Testing TTS generation...")
    try:
        tts_request = {
            "input": "Hello, this is a test of the Kokoro ONNX TTS API.",
            "model": "kokoro",
            "voice": "af_heart",
            "response_format": "mp3",
            "speed": 1.0
        }
        
        response = requests.post(
            f"{base_url}/v1/audio/speech",
            json=tts_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            # Save audio file
            with open("test_output.mp3", "wb") as f:
                f.write(response.content)
            print(f"   Audio saved to test_output.mp3")
            print(f"   Audio duration: {response.headers.get('X-Audio-Duration', 'unknown')}s")
            print(f"   Processing time: {response.headers.get('X-Processing-Time', 'unknown')}s")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ API test complete!")

if __name__ == "__main__":
    test_api()