#!/usr/bin/env python3
"""
OpenWebUI Integration Testing for Kokoro ONNX TTS API
Tests all endpoints and compatibility routes for OpenWebUI integration
"""

import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class OpenWebUIIntegrationTester:
    """Comprehensive OpenWebUI integration testing class"""
    
    def __init__(self, base_url: str = "http://localhost:8354"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
    
    def test_standard_speech_endpoint(self) -> bool:
        """Test standard OpenAI-compatible /v1/audio/speech endpoint"""
        print("🎵 Testing standard speech endpoint...")
        try:
            payload = {
                "model": "tts-1",
                "input": "Testing standard OpenAI compatible speech endpoint",
                "voice": "af_heart",
                "response_format": "mp3",
                "speed": 1.0
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/v1/audio/speech",
                json=payload,
                timeout=30
            )
            request_time = time.time() - start_time
            
            success = response.status_code == 200
            
            if success:
                audio_size = len(response.content)
                print(f"   ✅ Standard endpoint: {audio_size} bytes in {request_time:.2f}s")
                
                # Save test file
                test_file = Path("test_standard_speech.mp3")
                test_file.write_bytes(response.content)
                print(f"   💾 Saved to {test_file}")
                
            else:
                print(f"   ❌ Standard endpoint failed: {response.status_code}")
                print(f"      Error: {response.text[:200]}")
            
            self.test_results.append(("Standard Speech Endpoint", success))
            return success
            
        except Exception as e:
            print(f"   ❌ Standard endpoint error: {e}")
            self.test_results.append(("Standard Speech Endpoint", False))
            return False
    
    def test_streaming_endpoint(self) -> bool:
        """Test streaming /v1/audio/stream endpoint"""
        print("🌊 Testing streaming endpoint...")
        try:
            payload = {
                "model": "tts-1",
                "input": "Testing streaming audio endpoint for real-time generation",
                "voice": "af_heart",
                "response_format": "mp3",
                "speed": 1.0
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/v1/audio/stream",
                json=payload,
                timeout=30,
                stream=True
            )
            
            success = response.status_code == 200
            
            if success:
                # Collect streaming data
                audio_data = b""
                chunk_count = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        audio_data += chunk
                        chunk_count += 1
                
                request_time = time.time() - start_time
                audio_size = len(audio_data)
                
                print(f"   ✅ Streaming endpoint: {audio_size} bytes in {chunk_count} chunks over {request_time:.2f}s")
                
                # Save test file
                test_file = Path("test_streaming.mp3")
                test_file.write_bytes(audio_data)
                print(f"   💾 Saved to {test_file}")
                
            else:
                print(f"   ❌ Streaming endpoint failed: {response.status_code}")
                print(f"      Error: {response.text[:200]}")
            
            self.test_results.append(("Streaming Endpoint", success))
            return success
            
        except Exception as e:
            print(f"   ❌ Streaming endpoint error: {e}")
            self.test_results.append(("Streaming Endpoint", False))
            return False
    
    def test_openwebui_compatibility_route(self) -> bool:
        """Test OpenWebUI compatibility route /v1/audio/stream/audio/speech"""
        print("🔧 Testing OpenWebUI compatibility route...")
        try:
            payload = {
                "model": "tts-1",
                "input": "Testing OpenWebUI compatibility route for malformed URL handling",
                "voice": "af_heart",
                "response_format": "mp3",
                "speed": 1.0
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/v1/audio/stream/audio/speech",
                json=payload,
                timeout=30,
                stream=True
            )
            
            success = response.status_code == 200
            
            if success:
                # Collect streaming data
                audio_data = b""
                chunk_count = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        audio_data += chunk
                        chunk_count += 1
                
                request_time = time.time() - start_time
                audio_size = len(audio_data)
                
                print(f"   ✅ Compatibility route: {audio_size} bytes in {chunk_count} chunks over {request_time:.2f}s")
                print(f"   🎯 This route handles OpenWebUI's malformed URL construction")
                
                # Save test file
                test_file = Path("test_openwebui_compat.mp3")
                test_file.write_bytes(audio_data)
                print(f"   💾 Saved to {test_file}")
                
            else:
                print(f"   ❌ Compatibility route failed: {response.status_code}")
                print(f"      Error: {response.text[:200]}")
            
            self.test_results.append(("OpenWebUI Compatibility Route", success))
            return success
            
        except Exception as e:
            print(f"   ❌ Compatibility route error: {e}")
            self.test_results.append(("OpenWebUI Compatibility Route", False))
            return False
    
    def test_voices_endpoint(self) -> bool:
        """Test voices listing endpoint"""
        print("🎭 Testing voices endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/v1/audio/voices")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                voices = data.get('data', [])
                print(f"   ✅ Found {len(voices)} voices available")
                
                # Show sample voices
                for i, voice in enumerate(voices[:3]):
                    print(f"      {i+1}. {voice['id']} ({voice['name']})")
                
                if len(voices) > 3:
                    print(f"      ... and {len(voices) - 3} more")
                    
            else:
                print(f"   ❌ Voices endpoint failed: {response.status_code}")
            
            self.test_results.append(("Voices Endpoint", success))
            return success
            
        except Exception as e:
            print(f"   ❌ Voices endpoint error: {e}")
            self.test_results.append(("Voices Endpoint", False))
            return False
    
    def test_different_voices(self) -> bool:
        """Test different voice options"""
        print("🎤 Testing different voices...")
        
        test_voices = ["af_heart", "af_alloy", "am_puck", "bf_alice"]
        all_success = True
        
        for voice in test_voices:
            try:
                payload = {
                    "model": "tts-1",
                    "input": f"Testing voice {voice}",
                    "voice": voice,
                    "response_format": "mp3",
                    "speed": 1.0
                }
                
                response = self.session.post(
                    f"{self.base_url}/v1/audio/speech",
                    json=payload,
                    timeout=30
                )
                
                success = response.status_code == 200
                
                if success:
                    audio_size = len(response.content)
                    print(f"   ✅ Voice '{voice}': {audio_size} bytes")
                    
                    # Save test file
                    test_file = Path(f"test_voice_{voice}.mp3")
                    test_file.write_bytes(response.content)
                    
                else:
                    print(f"   ❌ Voice '{voice}': Failed ({response.status_code})")
                    all_success = False
                    
            except Exception as e:
                print(f"   ❌ Voice '{voice}': Error - {e}")
                all_success = False
        
        self.test_results.append(("Different Voices", all_success))
        return all_success
    
    def test_openwebui_configuration_scenarios(self) -> bool:
        """Test different OpenWebUI configuration scenarios"""
        print("⚙️ Testing OpenWebUI configuration scenarios...")
        
        # Scenario 1: User configures full endpoint (causes malformed URL)
        print("   📋 Scenario 1: User configures 'http://host/v1/audio/stream'")
        print("      → OpenWebUI tries: 'http://host/v1/audio/stream/audio/speech'")
        compat_success = self.test_openwebui_compatibility_route()
        
        # Scenario 2: User configures base URL (standard behavior)
        print("   📋 Scenario 2: User configures 'http://host/v1'")
        print("      → OpenWebUI tries: 'http://host/v1/audio/speech'")
        standard_success = self.test_standard_speech_endpoint()
        
        overall_success = compat_success and standard_success
        self.test_results.append(("OpenWebUI Configuration Scenarios", overall_success))
        return overall_success
    
    def run_comprehensive_test(self) -> bool:
        """Run all OpenWebUI integration tests"""
        print("🧪 Running Comprehensive OpenWebUI Integration Tests")
        print("=" * 60)
        
        # Core endpoint tests
        standard_ok = self.test_standard_speech_endpoint()
        print()
        
        streaming_ok = self.test_streaming_endpoint()
        print()
        
        compat_ok = self.test_openwebui_compatibility_route()
        print()
        
        voices_ok = self.test_voices_endpoint()
        print()
        
        voices_test_ok = self.test_different_voices()
        print()
        
        # Configuration scenario tests
        config_ok = self.test_openwebui_configuration_scenarios()
        print()
        
        # Summary
        self.print_summary()
        
        # Overall success
        all_passed = all(result[1] for result in self.test_results)
        return all_passed
    
    def print_summary(self):
        """Print test summary"""
        print("📊 OpenWebUI Integration Test Summary")
        print("-" * 50)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, success in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if success:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All OpenWebUI integration tests passed!")
            print("\n🚀 Ready for OpenWebUI integration:")
            print("   • Use: http://your-server:8001/v1")
            print("   • Or:  http://your-server:8001/v1/audio/stream")
            print("   • Both configurations will work!")
        else:
            print(f"❌ {total - passed} tests failed")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test OpenWebUI integration with Kokoro ONNX TTS API")
    parser.add_argument("--url", default="http://localhost:8001", 
                       help="Base URL for API (default: http://localhost:8001)")
    
    args = parser.parse_args()
    
    tester = OpenWebUIIntegrationTester(args.url)
    success = tester.run_comprehensive_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
