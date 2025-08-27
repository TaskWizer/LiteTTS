#!/usr/bin/env python3
"""
Critical TTS System Diagnosis
Comprehensive testing to identify synthesis failures and audio truncation issues
"""

import requests
import json
import time
import os
import wave
import struct
from pathlib import Path
from typing import Dict, List, Any, Tuple

class CriticalTTSDiagnosis:
    """Critical TTS system diagnosis and testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
        # Test cases designed to identify synthesis failures
        self.test_cases = [
            {
                "name": "Short Simple Text",
                "text": "Hello world",
                "expected_min_duration": 0.5,
                "expected_min_size": 5000
            },
            {
                "name": "Medium Sentence",
                "text": "This is a test of the text-to-speech system functionality.",
                "expected_min_duration": 2.0,
                "expected_min_size": 15000
            },
            {
                "name": "Long Complex Text",
                "text": "This is a comprehensive test of the text-to-speech system to verify that it can generate complete audio output for longer sentences without truncation or failure. The system should produce natural-sounding speech that includes all words from the input text, maintaining proper pronunciation and intonation throughout the entire synthesis process.",
                "expected_min_duration": 8.0,
                "expected_min_size": 60000
            },
            {
                "name": "Punctuation Test",
                "text": "Hello! How are you today? I'm doing well, thank you. This tests punctuation handling.",
                "expected_min_duration": 3.0,
                "expected_min_size": 25000
            },
            {
                "name": "Numbers and Symbols",
                "text": "The price is $50.99 and the date is 2024-01-15. Call (555) 123-4567 for more info.",
                "expected_min_duration": 4.0,
                "expected_min_size": 35000
            },
            {
                "name": "Challenging Pronunciation",
                "text": "The colonel's comfortable nuclear resume was thoroughly reviewed by the lieutenant.",
                "expected_min_duration": 3.5,
                "expected_min_size": 30000
            }
        ]
        
        self.test_voices = ["af_heart", "af_bella", "am_onyx", "af_nicole"]
        self.test_formats = ["mp3", "wav"]
    
    def run_critical_diagnosis(self) -> Dict[str, Any]:
        """Run critical TTS diagnosis"""
        print("🚨 CRITICAL TTS SYSTEM DIAGNOSIS")
        print("=" * 60)
        
        # Check system health first
        if not self._check_system_health():
            return {"status": "SYSTEM_UNAVAILABLE", "error": "TTS system is not responding"}
        
        print("✅ System is responding")
        
        # Run comprehensive tests
        results = {
            "system_status": "UNKNOWN",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "critical_failures": [],
            "test_details": [],
            "synthesis_performance": {},
            "audio_quality_analysis": {}
        }
        
        # Test each case with multiple voices and formats
        for test_case in self.test_cases:
            for voice in self.test_voices:
                for format in self.test_formats:
                    test_result = self._run_single_test(test_case, voice, format)
                    results["test_details"].append(test_result)
                    results["total_tests"] += 1
                    
                    if test_result["status"] == "PASSED":
                        results["passed_tests"] += 1
                    else:
                        results["failed_tests"] += 1
                        if test_result["severity"] == "CRITICAL":
                            results["critical_failures"].append(test_result)
        
        # Analyze results
        results["success_rate"] = (results["passed_tests"] / results["total_tests"]) * 100
        
        if results["success_rate"] >= 95:
            results["system_status"] = "HEALTHY"
        elif results["success_rate"] >= 80:
            results["system_status"] = "DEGRADED"
        elif results["success_rate"] >= 50:
            results["system_status"] = "CRITICAL"
        else:
            results["system_status"] = "FAILED"
        
        # Generate performance analysis
        results["synthesis_performance"] = self._analyze_performance()
        results["audio_quality_analysis"] = self._analyze_audio_quality()
        
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
    
    def _run_single_test(self, test_case: Dict, voice: str, format: str) -> Dict[str, Any]:
        """Run a single TTS test"""
        test_name = f"{test_case['name']} - {voice} - {format.upper()}"
        print(f"  Testing: {test_name}")
        
        result = {
            "test_name": test_name,
            "test_case": test_case["name"],
            "voice": voice,
            "format": format,
            "text": test_case["text"],
            "status": "UNKNOWN",
            "severity": "NORMAL",
            "audio_size": 0,
            "estimated_duration": 0,
            "response_time": 0,
            "issues": [],
            "error_message": None
        }
        
        try:
            # Make TTS request
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json={
                    "input": test_case["text"],
                    "voice": voice,
                    "response_format": format
                },
                timeout=30
            )
            end_time = time.time()
            
            result["response_time"] = end_time - start_time
            
            if response.status_code != 200:
                result["status"] = "FAILED"
                result["severity"] = "CRITICAL"
                result["error_message"] = f"HTTP {response.status_code}: {response.text[:200]}"
                result["issues"].append("HTTP_ERROR")
                print(f"    ❌ HTTP Error: {response.status_code}")
                return result
            
            # Analyze audio response
            audio_data = response.content
            result["audio_size"] = len(audio_data)
            
            # Check for empty or too small audio
            if result["audio_size"] < test_case["expected_min_size"]:
                result["issues"].append("AUDIO_TOO_SMALL")
                if result["audio_size"] < 1000:  # Less than 1KB is critical
                    result["severity"] = "CRITICAL"
                    result["issues"].append("AUDIO_EMPTY_OR_TRUNCATED")
            
            # Estimate duration and check for truncation
            estimated_duration = self._estimate_audio_duration(audio_data, format)
            result["estimated_duration"] = estimated_duration
            
            if estimated_duration < test_case["expected_min_duration"]:
                result["issues"].append("AUDIO_TRUNCATED")
                if estimated_duration < 0.5:  # Less than 0.5s is critical
                    result["severity"] = "CRITICAL"
            
            # Check response time
            if result["response_time"] > 10.0:
                result["issues"].append("SLOW_RESPONSE")
            
            # Determine overall status
            if not result["issues"]:
                result["status"] = "PASSED"
                print(f"    ✅ {result['audio_size']} bytes, ~{estimated_duration:.1f}s, {result['response_time']:.2f}s")
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
    
    def _estimate_audio_duration(self, audio_data: bytes, format: str) -> float:
        """Estimate audio duration from file size"""
        try:
            if format == "wav":
                # Try to parse WAV header for accurate duration
                if len(audio_data) > 44:  # Minimum WAV header size
                    # WAV files have duration info in header
                    # This is a simplified estimation
                    return len(audio_data) / (24000 * 2)  # 24kHz, 16-bit
                else:
                    return 0.0
            elif format == "mp3":
                # MP3 estimation based on typical compression ratios
                return len(audio_data) / (16000 * 0.125)  # Rough MP3 estimation
            else:
                # Generic estimation
                return len(audio_data) / (24000 * 2)
        except:
            return 0.0
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze synthesis performance"""
        if not self.test_results:
            return {}
        
        response_times = [r["response_time"] for r in self.test_results if r["response_time"] > 0]
        audio_sizes = [r["audio_size"] for r in self.test_results if r["audio_size"] > 0]
        
        if not response_times:
            return {}
        
        return {
            "avg_response_time": sum(response_times) / len(response_times),
            "max_response_time": max(response_times),
            "min_response_time": min(response_times),
            "avg_audio_size": sum(audio_sizes) / len(audio_sizes) if audio_sizes else 0,
            "total_tests": len(self.test_results)
        }
    
    def _analyze_audio_quality(self) -> Dict[str, Any]:
        """Analyze audio quality indicators"""
        if not self.test_results:
            return {}
        
        empty_audio_count = len([r for r in self.test_results if r["audio_size"] < 1000])
        truncated_count = len([r for r in self.test_results if "AUDIO_TRUNCATED" in r["issues"]])
        error_count = len([r for r in self.test_results if r["status"] in ["FAILED", "ERROR", "CRITICAL_FAILURE"]])
        
        return {
            "empty_audio_files": empty_audio_count,
            "truncated_audio_files": truncated_count,
            "synthesis_errors": error_count,
            "quality_score": max(0, 100 - (empty_audio_count * 20) - (truncated_count * 10) - (error_count * 5))
        }
    
    def _print_diagnosis_summary(self, results: Dict[str, Any]):
        """Print diagnosis summary"""
        print(f"\n🔍 DIAGNOSIS SUMMARY")
        print("=" * 40)
        print(f"System Status: {results['system_status']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Tests: {results['passed_tests']}/{results['total_tests']} passed")
        
        if results["critical_failures"]:
            print(f"\n🚨 CRITICAL FAILURES ({len(results['critical_failures'])}):")
            for failure in results["critical_failures"]:
                print(f"  - {failure['test_name']}: {', '.join(failure['issues'])}")
        
        perf = results["synthesis_performance"]
        if perf:
            print(f"\n⚡ PERFORMANCE:")
            print(f"  Average Response Time: {perf['avg_response_time']:.2f}s")
            print(f"  Response Time Range: {perf['min_response_time']:.2f}s - {perf['max_response_time']:.2f}s")
            print(f"  Average Audio Size: {perf['avg_audio_size']:.0f} bytes")
        
        quality = results["audio_quality_analysis"]
        if quality:
            print(f"\n🎵 AUDIO QUALITY:")
            print(f"  Quality Score: {quality['quality_score']:.0f}/100")
            print(f"  Empty Audio Files: {quality['empty_audio_files']}")
            print(f"  Truncated Audio Files: {quality['truncated_audio_files']}")
            print(f"  Synthesis Errors: {quality['synthesis_errors']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if results["system_status"] == "HEALTHY":
            print("  ✅ System is functioning normally")
        elif results["system_status"] == "DEGRADED":
            print("  ⚠️ System has minor issues - monitor performance")
        elif results["system_status"] == "CRITICAL":
            print("  🚨 System has significant issues - immediate attention required")
        else:
            print("  💥 System is failing - critical intervention needed")

def main():
    """Main diagnosis function"""
    diagnosis = CriticalTTSDiagnosis()
    results = diagnosis.run_critical_diagnosis()
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"critical_tts_diagnosis_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Diagnosis results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    main()
