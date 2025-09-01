#!/usr/bin/env python3
"""
Validate RTF Performance Improvements
Tests the optimized system to ensure RTF < 0.25 target is achieved
"""

import time
import requests
import statistics
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class RTFTestResult:
    """Results from RTF performance test"""
    text: str
    voice: str
    rtf: float
    latency_ms: float
    audio_duration_est: float
    success: bool
    error_message: str = ""

class RTFPerformanceValidator:
    """Validates RTF performance against targets"""
    
    def __init__(self, base_url: str = "http://localhost:8354"):
        self.base_url = base_url
        self.target_rtf = 0.25
        self.test_cases = [
            # Ultra-short text (< 20 chars)
            "Hello world.",
            "Test.",
            "Hi there!",
            
            # Short text (20-50 chars)
            "This is a short test sentence.",
            "How are you doing today?",
            "The weather is nice outside.",
            
            # Medium text (50-100 chars)
            "This is a medium length sentence that should test the system's performance.",
            "The quick brown fox jumps over the lazy dog in the beautiful garden.",
            
            # Long text (100+ chars)
            "This is a longer text that will test the system's ability to handle more complex synthesis tasks while maintaining good performance metrics.",
            "In the heart of the bustling city, where skyscrapers touched the clouds and the streets hummed with endless activity, there lived a small community of artists who found inspiration in the urban chaos."
        ]
        self.voices_to_test = ["af_heart", "am_puck"]  # Test with different voices
    
    def estimate_audio_duration(self, text: str) -> float:
        """Estimate audio duration based on text length"""
        # Rough estimate: ~150 words per minute, ~5 characters per word
        words = len(text) / 5
        duration_seconds = (words / 150) * 60
        return max(0.5, duration_seconds)  # Minimum 0.5 seconds
    
    def test_single_request(self, text: str, voice: str) -> RTFTestResult:
        """Test a single TTS request and measure RTF"""
        try:
            start_time = time.perf_counter()
            
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json={
                    "input": text,
                    "voice": voice,
                    "response_format": "mp3"
                },
                timeout=30
            )
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                audio_duration = self.estimate_audio_duration(text)
                rtf = (latency_ms / 1000) / audio_duration
                
                return RTFTestResult(
                    text=text,
                    voice=voice,
                    rtf=rtf,
                    latency_ms=latency_ms,
                    audio_duration_est=audio_duration,
                    success=True
                )
            else:
                return RTFTestResult(
                    text=text,
                    voice=voice,
                    rtf=999.0,
                    latency_ms=latency_ms,
                    audio_duration_est=0,
                    success=False,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return RTFTestResult(
                text=text,
                voice=voice,
                rtf=999.0,
                latency_ms=0,
                audio_duration_est=0,
                success=False,
                error_message=str(e)
            )
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run comprehensive RTF performance tests"""
        print("🎯 Running RTF Performance Validation")
        print("=" * 50)
        print(f"Target RTF: < {self.target_rtf}")
        print(f"Testing {len(self.test_cases)} text samples with {len(self.voices_to_test)} voices")
        print()
        
        all_results = []
        
        for voice in self.voices_to_test:
            print(f"Testing voice: {voice}")
            voice_results = []
            
            for i, text in enumerate(self.test_cases, 1):
                print(f"  Test {i}/{len(self.test_cases)}: {text[:50]}{'...' if len(text) > 50 else ''}")
                
                result = self.test_single_request(text, voice)
                voice_results.append(result)
                all_results.append(result)
                
                if result.success:
                    status = "✅" if result.rtf < self.target_rtf else "❌"
                    print(f"    {status} RTF: {result.rtf:.3f}, Latency: {result.latency_ms:.0f}ms")
                else:
                    print(f"    ❌ FAILED: {result.error_message}")
                
                # Small delay between requests
                time.sleep(0.5)
            
            print()
        
        return self.analyze_results(all_results)
    
    def analyze_results(self, results: List[RTFTestResult]) -> Dict[str, Any]:
        """Analyze test results and generate report"""
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        if not successful_results:
            return {
                "success": False,
                "error": "All tests failed",
                "total_tests": len(results),
                "failed_tests": len(failed_results)
            }
        
        rtf_values = [r.rtf for r in successful_results]
        latency_values = [r.latency_ms for r in successful_results]
        
        # Calculate statistics
        avg_rtf = statistics.mean(rtf_values)
        min_rtf = min(rtf_values)
        max_rtf = max(rtf_values)
        p95_rtf = sorted(rtf_values)[int(len(rtf_values) * 0.95)] if len(rtf_values) > 1 else rtf_values[0]
        
        avg_latency = statistics.mean(latency_values)
        
        # Check if target is met
        target_met = avg_rtf < self.target_rtf and p95_rtf < (self.target_rtf * 1.5)
        
        # Categorize by text length
        ultra_short = [r for r in successful_results if len(r.text) < 20]
        short = [r for r in successful_results if 20 <= len(r.text) < 50]
        medium = [r for r in successful_results if 50 <= len(r.text) < 100]
        long = [r for r in successful_results if len(r.text) >= 100]
        
        analysis = {
            "success": True,
            "target_met": target_met,
            "total_tests": len(results),
            "successful_tests": len(successful_results),
            "failed_tests": len(failed_results),
            "performance_metrics": {
                "avg_rtf": avg_rtf,
                "min_rtf": min_rtf,
                "max_rtf": max_rtf,
                "p95_rtf": p95_rtf,
                "avg_latency_ms": avg_latency,
                "target_rtf": self.target_rtf
            },
            "by_text_length": {
                "ultra_short": {
                    "count": len(ultra_short),
                    "avg_rtf": statistics.mean([r.rtf for r in ultra_short]) if ultra_short else 0
                },
                "short": {
                    "count": len(short),
                    "avg_rtf": statistics.mean([r.rtf for r in short]) if short else 0
                },
                "medium": {
                    "count": len(medium),
                    "avg_rtf": statistics.mean([r.rtf for r in medium]) if medium else 0
                },
                "long": {
                    "count": len(long),
                    "avg_rtf": statistics.mean([r.rtf for r in long]) if long else 0
                }
            }
        }
        
        return analysis
    
    def print_report(self, analysis: Dict[str, Any]):
        """Print detailed performance report"""
        print("📊 Performance Analysis Report")
        print("=" * 50)
        
        if not analysis["success"]:
            print(f"❌ Tests failed: {analysis.get('error', 'Unknown error')}")
            return
        
        metrics = analysis["performance_metrics"]
        
        print(f"Tests: {analysis['successful_tests']}/{analysis['total_tests']} successful")
        print(f"Target RTF: < {metrics['target_rtf']}")
        print(f"Average RTF: {metrics['avg_rtf']:.3f}")
        print(f"P95 RTF: {metrics['p95_rtf']:.3f}")
        print(f"RTF Range: {metrics['min_rtf']:.3f} - {metrics['max_rtf']:.3f}")
        print(f"Average Latency: {metrics['avg_latency_ms']:.0f}ms")
        print()
        
        # Overall result
        if analysis["target_met"]:
            print("🎉 SUCCESS: RTF target achieved!")
        else:
            print("⚠️  WARNING: RTF target not fully met")
        
        print()
        print("Performance by Text Length:")
        for category, data in analysis["by_text_length"].items():
            if data["count"] > 0:
                status = "✅" if data["avg_rtf"] < metrics["target_rtf"] else "❌"
                print(f"  {category.replace('_', ' ').title()}: {status} {data['avg_rtf']:.3f} RTF ({data['count']} tests)")

def main():
    """Run RTF performance validation"""
    logging.basicConfig(level=logging.INFO)
    
    validator = RTFPerformanceValidator()
    
    # Check if service is running
    try:
        response = requests.get(f"{validator.base_url}/v1/health", timeout=5)
        if response.status_code != 200:
            print("❌ LiteTTS service is not running or not healthy")
            return
    except Exception as e:
        print(f"❌ Cannot connect to LiteTTS service: {e}")
        print("Please ensure the service is running on http://localhost:8354")
        return
    
    # Run tests
    analysis = validator.run_performance_tests()
    validator.print_report(analysis)

if __name__ == "__main__":
    main()
