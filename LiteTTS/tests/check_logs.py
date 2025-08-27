#!/usr/bin/env python3
"""
Check what's in the server logs by making a test request
"""

import requests
import json
import time

def make_test_request():
    """Make a test request and show what should appear in logs"""
    base_url = "http://192.168.1.139:8000"
    
    test_data = {
        "input": "Test message",
        "model": "kokoro", 
        "voice": "af_heart",
        "response_format": "mp3",
        "speed": 1.0
    }
    
    print("🧪 Making test request to trigger logging...")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    print("\n📋 Check your server console for these log messages:")
    print("   🎤 TTS request: text='Test message', voice='af_heart'...")
    print("   📝 Processing text: 'Test message' (length: 12)")
    print("   🎭 Using voice: af_heart")
    print("   🔊 Generating audio...")
    print("   ✅ Audio generated: XXXX samples at 24000Hz")
    print("   OR")
    print("   ❌ Generation failed: [ERROR MESSAGE]")
    
    print(f"\n🌐 Making request to {base_url}/audio/speech...")
    
    try:
        response = requests.post(
            f"{base_url}/audio/speech",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Success! Audio size: {len(response.content)} bytes")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n💡 Look at your server console now for the detailed logs!")

if __name__ == "__main__":
    make_test_request()