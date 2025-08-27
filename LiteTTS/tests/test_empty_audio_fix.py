#!/usr/bin/env python3
"""
Test script to verify the empty audio generation fix
"""

import requests
import json
import time

def test_empty_audio_fix():
    """Test the fix for empty audio generation"""
    print("🧪 Testing Empty Audio Generation Fix")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test cases that previously caused empty audio
    test_cases = [
        "But true!",
        "But true!...",
        "Hello!",
        "Test.",
        "Short text",
        "A",
        "!",
        "...",
        "But true! This is a longer sentence to test.",
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: '{text}'")
        
        payload = {
            "model": "kokoro",
            "input": text,
            "voice": "af_heart",
            "response_format": "mp3",
            "speed": 1.0
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/v1/audio/speech",
                json=payload,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                audio_size = len(response.content)
                generation_time = end_time - start_time
                
                if audio_size > 0:
                    print(f"   ✅ SUCCESS: {audio_size:,} bytes in {generation_time:.3f}s")
                    
                    # Check performance
                    if generation_time < 0.5:
                        print("   🎯 Excellent performance")
                    elif generation_time < 2.0:
                        print("   ⚡ Good performance")
                    else:
                        print("   🔄 Normal performance")
                else:
                    print("   ❌ FAILED: Empty audio generated")
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Error: {response.text[:200]}")
                    
        except requests.exceptions.Timeout:
            print("   ⏰ TIMEOUT: Request took too long")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

def test_server_status():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Empty Audio Fix Test")
    
    if test_server_status():
        test_empty_audio_fix()
    else:
        print("\n💡 Please start the server first:")
        print("   python LiteTTS/start_server.py")
