#!/usr/bin/env python3
"""
OpenWebUI Integration Diagnosis
Comprehensive testing to identify OpenWebUI TTS integration issues
"""

import requests
import json
import time
import os
import wave
import struct
from pathlib import Path
from typing import Dict, List, Any, Tuple

class OpenWebUIIntegrationDiagnosis:
    """OpenWebUI integration diagnosis and testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
        # OpenWebUI-specific test scenarios
        self.openwebui_scenarios = [
            {
                "name": "Standard OpenWebUI Request",
                "endpoint": "/v1/audio/speech",
                "payload": {
                    "model": "tts-1",
                    "input": "Hello, this is a test of the OpenWebUI text-to-speech integration.",
                    "voice": "alloy",  # OpenWebUI default voice
                    "response_format": "mp3"
                }
            },
            {
                "name": "OpenWebUI with Speed",
                "endpoint": "/v1/audio/speech", 
                "payload": {
                    "model": "tts-1",
                    "input": "Testing speed parameter with OpenWebUI integration.",
                    "voice": "alloy",
                    "response_format": "mp3",
                    "speed": 1.0
                }
            },
            {
                "name": "OpenWebUI Streaming",
                "endpoint": "/v1/audio/stream",
                "payload": {
                    "model": "tts-1",
                    "input": "Testing streaming audio with OpenWebUI compatibility.",
                    "voice": "alloy",
                    "response_format": "mp3"
                }
            },
            {
                "name": "OpenWebUI Compatibility Route",
                "endpoint": "/v1/audio/stream/audio/speech",
                "payload": {
                    "model": "tts-1",
                    "input": "Testing OpenWebUI compatibility route for malformed URLs.",
                    "voice": "alloy",
                    "response_format": "mp3"
                }
            },
            {
                "name": "Legacy Direct Route",
                "endpoint": "/audio/speech",
                "payload": {
                    "input": "Testing legacy direct audio speech endpoint.",
                    "voice": "af_heart",
                    "response_format": "mp3"
                }
            }
        ]
        
        # Test different voice mappings
        self.voice_mappings = [
            ("alloy", "af_heart"),
            ("echo", "af_bella"), 
            ("fable", "am_onyx"),
            ("onyx", "am_onyx"),
            ("nova", "af_nicole"),
            ("shimmer", "af_sarah")
        ]
    
    def run_openwebui_diagnosis(self) -> Dict[str, Any]:
        """Run comprehensive OpenWebUI integration diagnosis"""
        print("🔧 OPENWEBUI INTEGRATION DIAGNOSIS")
        print("=" * 60)
        
        # Check system health first
        if not self._check_system_health():
            return {"status": "SYSTEM_UNAVAILABLE", "error": "TTS system is not responding"}
        
        print("✅ System is responding")
        
        results = {
            "system_status": "UNKNOWN",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "critical_failures": [],
            "test_details": [],
            "voice_mapping_results": {},
            "endpoint_compatibility": {},
            "audio_analysis": {}
        }
        
        # Test OpenWebUI scenarios
        for scenario in self.openwebui_scenarios:
            test_result = self._test_openwebui_scenario(scenario)
            results["test_details"].append(test_result)
            results["total_tests"] += 1
            
            if test_result["status"] == "PASSED":
                results["passed_tests"] += 1
            else:
                results["failed_tests"] += 1
                if test_result["severity"] == "CRITICAL":
                    results["critical_failures"].append(test_result)
        
        # Test voice mappings
        results["voice_mapping_results"] = self._test_voice_mappings()
        
        # Test endpoint compatibility
        results["endpoint_compatibility"] = self._test_endpoint_compatibility()
        
        # Analyze audio quality
        results["audio_analysis"] = self._analyze_audio_responses()
        
        # Calculate success rate
        results["success_rate"] = (results["passed_tests"] / results["total_tests"]) * 100 if results["total_tests"] > 0 else 0
        
        if results["success_rate"] >= 95:
            results["system_status"] = "HEALTHY"
        elif results["success_rate"] >= 80:
            results["system_status"] = "DEGRADED"
        else:
            results["system_status"] = "CRITICAL"
        
        # Print summary
        self._print_diagnosis_summary(results)
        
        return results
    
    def _check_system_health(self) -> bool:
        """Check if TTS system is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                return health_data.get("status") == "healthy" and health_data.get("model_loaded", False)
            return False
        except:
            return False
    
    def _test_openwebui_scenario(self, scenario: Dict) -> Dict[str, Any]:
        """Test a specific OpenWebUI scenario"""
        test_name = scenario["name"]
        endpoint = scenario["endpoint"]
        payload = scenario["payload"]
        
        print(f"  Testing: {test_name}")
        
        result = {
            "test_name": test_name,
            "endpoint": endpoint,
            "payload": payload,
            "status": "UNKNOWN",
            "severity": "NORMAL",
            "audio_size": 0,
            "response_time": 0,
            "content_type": None,
            "headers": {},
            "issues": [],
            "error_message": None,
            "audio_analysis": {}
        }
        
        try:
            # Make request
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                timeout=30,
                stream=True if "stream" in endpoint else False
            )
            end_time = time.time()
            
            result["response_time"] = end_time - start_time
            result["status_code"] = response.status_code
            result["content_type"] = response.headers.get("content-type", "")
            result["headers"] = dict(response.headers)
            
            if response.status_code != 200:
                result["status"] = "FAILED"
                result["severity"] = "CRITICAL"
                result["error_message"] = f"HTTP {response.status_code}: {response.text[:200]}"
                result["issues"].append("HTTP_ERROR")
                print(f"    ❌ HTTP Error: {response.status_code}")
                return result
            
            # Collect audio data
            if "stream" in endpoint:
                # Handle streaming response
                audio_data = b""
                chunk_count = 0
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        audio_data += chunk
                        chunk_count += 1
                result["audio_analysis"]["chunk_count"] = chunk_count
            else:
                # Handle regular response
                audio_data = response.content
            
            result["audio_size"] = len(audio_data)
            
            # Analyze audio data
            audio_analysis = self._analyze_audio_data(audio_data, payload.get("response_format", "mp3"))
            result["audio_analysis"].update(audio_analysis)
            
            # Check for issues
            if result["audio_size"] < 1000:
                result["issues"].append("AUDIO_TOO_SMALL")
                result["severity"] = "CRITICAL"
            
            if result["audio_size"] < 100:
                result["issues"].append("AUDIO_EMPTY")
                result["severity"] = "CRITICAL"
            
            if result["response_time"] > 10.0:
                result["issues"].append("SLOW_RESPONSE")
            
            if not self._validate_audio_format(audio_data, payload.get("response_format", "mp3")):
                result["issues"].append("INVALID_AUDIO_FORMAT")
            
            # Check for truncation indicators
            if self._detect_audio_truncation(audio_data, payload.get("input", "")):
                result["issues"].append("AUDIO_TRUNCATED")
                result["severity"] = "CRITICAL"
            
            # Determine status
            if not result["issues"]:
                result["status"] = "PASSED"
                print(f"    ✅ {result['audio_size']} bytes, {result['response_time']:.2f}s")
            elif result["severity"] == "CRITICAL":
                result["status"] = "CRITICAL_FAILURE"
                print(f"    🚨 CRITICAL: {', '.join(result['issues'])}")
            else:
                result["status"] = "FAILED"
                print(f"    ⚠️ Issues: {', '.join(result['issues'])}")
        
        except Exception as e:
            result["status"] = "ERROR"
            result["severity"] = "CRITICAL"
            result["error_message"] = str(e)
            result["issues"].append("EXCEPTION")
            print(f"    ❌ Exception: {e}")
        
        return result
    
    def _test_voice_mappings(self) -> Dict[str, Any]:
        """Test OpenWebUI voice mappings"""
        print("\n🎤 Testing Voice Mappings")
        print("-" * 30)
        
        mapping_results = {}
        
        for openwebui_voice, expected_kokoro_voice in self.voice_mappings:
            print(f"  Testing: {openwebui_voice} → {expected_kokoro_voice}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json={
                        "model": "tts-1",
                        "input": f"Testing voice {openwebui_voice}",
                        "voice": openwebui_voice,
                        "response_format": "mp3"
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    audio_size = len(response.content)
                    mapping_results[openwebui_voice] = {
                        "status": "PASSED",
                        "audio_size": audio_size,
                        "expected_voice": expected_kokoro_voice
                    }
                    print(f"    ✅ {audio_size} bytes")
                else:
                    mapping_results[openwebui_voice] = {
                        "status": "FAILED",
                        "error": f"HTTP {response.status_code}",
                        "expected_voice": expected_kokoro_voice
                    }
                    print(f"    ❌ HTTP {response.status_code}")
            
            except Exception as e:
                mapping_results[openwebui_voice] = {
                    "status": "ERROR",
                    "error": str(e),
                    "expected_voice": expected_kokoro_voice
                }
                print(f"    ❌ Error: {e}")
        
        return mapping_results
    
    def _test_endpoint_compatibility(self) -> Dict[str, Any]:
        """Test endpoint compatibility"""
        print("\n🔗 Testing Endpoint Compatibility")
        print("-" * 35)
        
        endpoints = [
            "/v1/audio/speech",
            "/v1/audio/stream", 
            "/audio/speech",
            "/v1/audio/stream/audio/speech",
            "/v1/audio/speech/audio/speech"
        ]
        
        compatibility_results = {}
        
        for endpoint in endpoints:
            print(f"  Testing: {endpoint}")
            
            try:
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json={
                        "input": "Endpoint compatibility test",
                        "voice": "af_heart",
                        "response_format": "mp3"
                    },
                    timeout=10
                )
                
                compatibility_results[endpoint] = {
                    "status_code": response.status_code,
                    "accessible": response.status_code == 200,
                    "audio_size": len(response.content) if response.status_code == 200 else 0
                }
                
                if response.status_code == 200:
                    print(f"    ✅ {len(response.content)} bytes")
                else:
                    print(f"    ❌ HTTP {response.status_code}")
            
            except Exception as e:
                compatibility_results[endpoint] = {
                    "status_code": 0,
                    "accessible": False,
                    "error": str(e)
                }
                print(f"    ❌ Error: {e}")
        
        return compatibility_results
    
    def _analyze_audio_data(self, audio_data: bytes, format: str) -> Dict[str, Any]:
        """Analyze audio data for quality indicators"""
        analysis = {
            "size_bytes": len(audio_data),
            "format_valid": False,
            "estimated_duration": 0.0,
            "quality_indicators": {}
        }
        
        if len(audio_data) > 0:
            # Validate format
            analysis["format_valid"] = self._validate_audio_format(audio_data, format)
            
            # Estimate duration
            if format == "mp3":
                analysis["estimated_duration"] = len(audio_data) / (16000 * 0.125)
            elif format == "wav":
                analysis["estimated_duration"] = len(audio_data) / (24000 * 2)
            
            # Check for quality indicators
            if len(audio_data) < 100:
                analysis["quality_indicators"]["empty_file"] = True
            elif len(audio_data) < 1000:
                analysis["quality_indicators"]["very_small"] = True
            
            # Check for truncation patterns
            if self._has_truncation_pattern(audio_data):
                analysis["quality_indicators"]["truncation_detected"] = True
        
        return analysis
    
    def _validate_audio_format(self, audio_data: bytes, expected_format: str) -> bool:
        """Validate audio format"""
        if len(audio_data) < 10:
            return False
        
        try:
            if expected_format == 'mp3':
                # MP3 files can start with various sync patterns
                return (audio_data.startswith(b'\xff\xfb') or
                        audio_data.startswith(b'\xff\xf3') or
                        audio_data.startswith(b'\xff\xf2') or
                        audio_data.startswith(b'ID3'))
            elif expected_format == 'wav':
                return audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:12]
            elif expected_format == 'flac':
                return audio_data.startswith(b'fLaC')
            else:
                return len(audio_data) > 0
        except:
            return False
    
    def _detect_audio_truncation(self, audio_data: bytes, input_text: str) -> bool:
        """Detect if audio appears to be truncated"""
        if len(audio_data) < 100:
            return True
        
        # Estimate expected size based on text length
        expected_min_size = len(input_text) * 100  # Rough estimate
        if len(audio_data) < expected_min_size:
            return True
        
        return False
    
    def _has_truncation_pattern(self, audio_data: bytes) -> bool:
        """Check for patterns that indicate truncation"""
        if len(audio_data) < 100:
            return True
        
        # Check for abrupt ending (simplified check)
        # Real implementation would analyze audio waveform
        return False
    
    def _analyze_audio_responses(self) -> Dict[str, Any]:
        """Analyze overall audio response quality"""
        return {
            "total_responses": len(self.test_results),
            "empty_responses": len([r for r in self.test_results if r.get("audio_size", 0) < 100]),
            "small_responses": len([r for r in self.test_results if 100 <= r.get("audio_size", 0) < 1000]),
            "normal_responses": len([r for r in self.test_results if r.get("audio_size", 0) >= 1000])
        }
    
    def _print_diagnosis_summary(self, results: Dict[str, Any]):
        """Print diagnosis summary"""
        print(f"\n🔍 OPENWEBUI INTEGRATION SUMMARY")
        print("=" * 45)
        print(f"System Status: {results['system_status']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Tests: {results['passed_tests']}/{results['total_tests']} passed")
        
        if results["critical_failures"]:
            print(f"\n🚨 CRITICAL FAILURES ({len(results['critical_failures'])}):")
            for failure in results["critical_failures"]:
                print(f"  - {failure['test_name']}: {', '.join(failure['issues'])}")
        
        # Voice mapping summary
        voice_results = results["voice_mapping_results"]
        if voice_results:
            passed_voices = len([v for v in voice_results.values() if v["status"] == "PASSED"])
            total_voices = len(voice_results)
            print(f"\n🎤 VOICE MAPPINGS: {passed_voices}/{total_voices} working")
        
        # Endpoint compatibility summary
        endpoint_results = results["endpoint_compatibility"]
        if endpoint_results:
            accessible_endpoints = len([e for e in endpoint_results.values() if e["accessible"]])
            total_endpoints = len(endpoint_results)
            print(f"🔗 ENDPOINTS: {accessible_endpoints}/{total_endpoints} accessible")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if results["system_status"] == "HEALTHY":
            print("  ✅ OpenWebUI integration is working correctly")
        elif results["system_status"] == "DEGRADED":
            print("  ⚠️ Some OpenWebUI features may not work properly")
        else:
            print("  🚨 OpenWebUI integration has critical issues")
            print("  🔧 Check voice mappings and endpoint configurations")
            print("  📝 Verify request format compatibility")

def main():
    """Main diagnosis function"""
    diagnosis = OpenWebUIIntegrationDiagnosis()
    results = diagnosis.run_openwebui_diagnosis()
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"openwebui_integration_diagnosis_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Diagnosis results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    main()
