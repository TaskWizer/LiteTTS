#!/usr/bin/env python3
"""
Setup and test the Kokoro ONNX TTS API
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - Timed out")
        return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def test_api_when_ready():
    """Test the API once it's running"""
    print("\n🧪 Testing API endpoints...")
    base_url = "http://localhost:8000"
    
    # Wait for server to be ready
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except:
            print(f"   Waiting for server... ({i+1}/10)")
            time.sleep(2)
    else:
        print("❌ Server not responding")
        return False
    
    # Test endpoints
    tests = [
        ("Health check", "GET", "/health"),
        ("Models list", "GET", "/v1/models"),
        ("Voices list", "GET", "/voices"),
    ]
    
    for name, method, endpoint in tests:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name} - OK")
                if endpoint == "/voices":
                    data = response.json()
                    print(f"   Available voices: {data.get('voices', [])}")
            else:
                print(f"❌ {name} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name} - Error: {e}")
    
    # Test TTS generation
    print("\n🎵 Testing TTS generation...")
    try:
        tts_request = {
            "input": "Hello, this is a test.",
            "model": "kokoro",
            "voice": "af_heart",
            "response_format": "mp3",
            "speed": 1.0
        }
        
        response = requests.post(
            f"{base_url}/v1/audio/speech",
            json=tts_request,
            timeout=30
        )
        
        if response.status_code == 200:
            with open("test_output.mp3", "wb") as f:
                f.write(response.content)
            print("✅ TTS generation - Success! Audio saved to test_output.mp3")
        else:
            print(f"❌ TTS generation - Status {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ TTS generation - Error: {e}")

def main():
    print("🚀 Kokoro ONNX TTS API Setup and Test")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this from the project root directory.")
        sys.exit(1)
    
    # Test downloader
    print("\n📦 Testing downloader...")
    success = run_command("python test_downloader.py", "Downloader test")
    if not success:
        print("❌ Downloader test failed. Please check the error above.")
        return
    
    print("\n🎯 Setup complete! You can now:")
    print("1. Start the server: python start_server.py")
    print("2. Or with UV: uv run python start_server.py")
    print("3. Test the API: python test_api.py")
    print("\n📋 For OpenWebUI integration:")
    print("- TTS Engine: OpenAI")
    print("- API Base URL: http://localhost:8000/v1")
    print("- API Key: dummy")
    print("- TTS Model: kokoro")
    print("- TTS Voice: af_heart")

if __name__ == "__main__":
    main()