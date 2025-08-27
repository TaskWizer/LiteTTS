#!/usr/bin/env python3
"""
OpenWebUI Real Integration Test
Test exactly how OpenWebUI calls the TTS API to identify audio truncation issues
"""

import requests
import json
import time
import os
from pathlib import Path

def test_openwebui_real_scenario():
    """Test the exact scenario that OpenWebUI uses"""
    base_url = "http://localhost:8000"
    
    print("🔧 OpenWebUI Real Integration Test")
    print("=" * 50)
    
    # Test 1: Standard OpenWebUI request (what OpenWebUI actually sends)
    print("\n1. Testing Standard OpenWebUI Request")
    payload = {
        "model": "tts-1",
        "input": "Hello, this is a test of the OpenWebUI text-to-speech integration. The system should generate complete audio without truncation.",
        "voice": "alloy",
        "response_format": "mp3"
    }
    
    try:
        print(f"   Sending request to: {base_url}/v1/audio/speech")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{base_url}/v1/audio/speech",
            json=payload,
            timeout=30,
            stream=False  # OpenWebUI doesn't use streaming
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"   Content-Length: {response.headers.get('content-length', 'Not set')}")
        print(f"   Audio Size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Save audio file
            with open("openwebui_test_standard.mp3", "wb") as f:
                f.write(response.content)
            print(f"   ✅ Audio saved to: openwebui_test_standard.mp3")
            
            # Check if audio is valid MP3
            if response.content.startswith(b'\xff\xf3') or response.content.startswith(b'\xff\xfb') or response.content.startswith(b'ID3'):
                print(f"   ✅ Valid MP3 format detected")
            else:
                print(f"   ⚠️ Invalid MP3 format - first bytes: {response.content[:10].hex()}")
        else:
            print(f"   ❌ Request failed: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: OpenWebUI with streaming (if it uses this)
    print("\n2. Testing OpenWebUI Streaming Request")
    try:
        print(f"   Sending request to: {base_url}/v1/audio/stream")
        
        response = requests.post(
            f"{base_url}/v1/audio/stream",
            json=payload,
            timeout=30,
            stream=True  # Test streaming
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"   Transfer-Encoding: {response.headers.get('transfer-encoding', 'Not set')}")
        
        if response.status_code == 200:
            # Collect streaming data
            audio_data = b""
            chunk_count = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    audio_data += chunk
                    chunk_count += 1
            
            print(f"   Audio Size: {len(audio_data)} bytes from {chunk_count} chunks")
            
            # Save audio file
            with open("openwebui_test_streaming.mp3", "wb") as f:
                f.write(audio_data)
            print(f"   ✅ Streaming audio saved to: openwebui_test_streaming.mp3")
            
            # Check if audio is valid MP3
            if audio_data.startswith(b'\xff\xf3') or audio_data.startswith(b'\xff\xfb') or audio_data.startswith(b'ID3'):
                print(f"   ✅ Valid MP3 format detected")
            else:
                print(f"   ⚠️ Invalid MP3 format - first bytes: {audio_data[:10].hex()}")
        else:
            print(f"   ❌ Streaming request failed: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Streaming exception: {e}")
    
    # Test 3: Test with different response formats
    print("\n3. Testing Different Response Formats")
    formats = ["mp3", "wav", "opus"]
    
    for fmt in formats:
        print(f"   Testing format: {fmt}")
        test_payload = payload.copy()
        test_payload["response_format"] = fmt
        
        try:
            response = requests.post(
                f"{base_url}/v1/audio/speech",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"     ✅ {fmt}: {len(response.content)} bytes")
                
                # Save file
                with open(f"openwebui_test_{fmt}.{fmt}", "wb") as f:
                    f.write(response.content)
            else:
                print(f"     ❌ {fmt}: HTTP {response.status_code}")
        
        except Exception as e:
            print(f"     ❌ {fmt}: Exception - {e}")
    
    # Test 4: Test with speed parameter
    print("\n4. Testing Speed Parameter Handling")
    speed_tests = [
        {"speed": None, "name": "No speed"},
        {"speed": 1.0, "name": "Speed 1.0"},
        {"speed": 0.5, "name": "Speed 0.5"},
        {"speed": 2.0, "name": "Speed 2.0"},
        {"speed": "1.0", "name": "Speed as string"},
    ]
    
    for test in speed_tests:
        print(f"   Testing: {test['name']}")
        test_payload = payload.copy()
        if test["speed"] is not None:
            test_payload["speed"] = test["speed"]
        
        try:
            response = requests.post(
                f"{base_url}/v1/audio/speech",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"     ✅ {len(response.content)} bytes")
            else:
                print(f"     ❌ HTTP {response.status_code}: {response.text[:100]}")
        
        except Exception as e:
            print(f"     ❌ Exception: {e}")
    
    # Test 5: Test audio playback compatibility
    print("\n5. Testing Audio Playback Compatibility")
    
    # Check if we can analyze the generated audio
    try:
        import wave
        import struct
        
        # Test the standard MP3 file
        if os.path.exists("openwebui_test_standard.mp3"):
            print("   Analyzing standard MP3 file...")
            
            # Convert MP3 to WAV for analysis (simplified)
            # In a real scenario, you'd use a proper audio library
            with open("openwebui_test_standard.mp3", "rb") as f:
                mp3_data = f.read()
            
            print(f"     File size: {len(mp3_data)} bytes")
            print(f"     First 20 bytes: {mp3_data[:20].hex()}")
            
            # Check for common MP3 issues
            if len(mp3_data) < 1000:
                print("     ⚠️ File is very small - possible truncation")
            elif mp3_data[:2] == b'\xff\xf3':
                print("     ✅ Valid MP3 header detected")
            elif mp3_data[:3] == b'ID3':
                print("     ✅ Valid MP3 with ID3 tag detected")
            else:
                print("     ⚠️ Unexpected file format")
    
    except ImportError:
        print("   ⚠️ Wave module not available for audio analysis")
    except Exception as e:
        print(f"   ⚠️ Audio analysis failed: {e}")
    
    print("\n📊 Test Summary")
    print("=" * 30)
    print("Check the generated audio files:")
    for filename in ["openwebui_test_standard.mp3", "openwebui_test_streaming.mp3", "openwebui_test_wav.wav", "openwebui_test_opus.opus"]:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  {filename}: {size} bytes")
    
    print("\n💡 Recommendations:")
    print("1. Test the generated MP3 files in a media player")
    print("2. Check if OpenWebUI is using the correct endpoint")
    print("3. Verify that OpenWebUI is not expecting streaming responses")
    print("4. Ensure proper Content-Type headers are set")

if __name__ == "__main__":
    test_openwebui_real_scenario()
