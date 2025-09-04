#!/usr/bin/env python3
"""
Performance Test Script for LiteTTS Docker Container
Tests RTF (Real-Time Factor) performance and compares with target metrics
"""

import time
import requests
import json
import statistics
from typing import List, Dict, Any
import argparse

class PerformanceTest:
    def __init__(self, base_url: str = "http://localhost:8354"):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
    
    def test_health(self) -> bool:
        """Test if the API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def test_single_synthesis(self, text: str, voice: str = "af_heart") -> Dict[str, Any]:
        """Test a single TTS synthesis and measure performance"""
        start_time = time.time()
        
        try:
            # Make TTS request
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json={
                    "input": text,
                    "voice": voice,
                    "response_format": "mp3",
                    "speed": 1.0
                },
                timeout=30
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                # Calculate metrics
                synthesis_time = end_time - start_time
                audio_length = len(response.content)
                
                # Estimate audio duration (rough calculation for MP3)
                # Assuming ~1KB per second for MP3 at 96kbps
                estimated_audio_duration = audio_length / 1024  # seconds
                
                # Calculate RTF (Real-Time Factor)
                rtf = synthesis_time / max(estimated_audio_duration, 0.1)
                
                result = {
                    "success": True,
                    "text": text,
                    "voice": voice,
                    "text_length": len(text),
                    "synthesis_time": synthesis_time,
                    "audio_size_bytes": audio_length,
                    "estimated_audio_duration": estimated_audio_duration,
                    "rtf": rtf,
                    "status_code": response.status_code
                }
                
                print(f"✅ Synthesis successful: {len(text)} chars, {synthesis_time:.3f}s, RTF: {rtf:.3f}")
                return result
            else:
                print(f"❌ Synthesis failed: HTTP {response.status_code}")
                return {
                    "success": False,
                    "text": text,
                    "voice": voice,
                    "error": f"HTTP {response.status_code}",
                    "synthesis_time": synthesis_time
                }
                
        except Exception as e:
            end_time = time.time()
            synthesis_time = end_time - start_time
            print(f"❌ Synthesis error: {e}")
            return {
                "success": False,
                "text": text,
                "voice": voice,
                "error": str(e),
                "synthesis_time": synthesis_time
            }
    
    def run_performance_test(self, test_cases: List[str], voice: str = "af_heart", iterations: int = 3) -> Dict[str, Any]:
        """Run comprehensive performance test"""
        print(f"🧪 Running performance test with {len(test_cases)} test cases, {iterations} iterations each")
        print(f"🎭 Using voice: {voice}")
        print(f"🎯 Target RTF: < 0.5 (Docker optimization goal)")
        print("-" * 60)
        
        all_results = []
        
        for i, text in enumerate(test_cases, 1):
            print(f"\nTest Case {i}/{len(test_cases)}: {len(text)} characters")
            case_results = []
            
            for iteration in range(iterations):
                print(f"  Iteration {iteration + 1}/{iterations}...", end=" ")
                result = self.test_single_synthesis(text, voice)
                case_results.append(result)
                all_results.append(result)
                
                if not result["success"]:
                    print(f"    ❌ Failed: {result.get('error', 'Unknown error')}")
                    break
            
            # Calculate case statistics
            if case_results and all(r["success"] for r in case_results):
                rtfs = [r["rtf"] for r in case_results]
                times = [r["synthesis_time"] for r in case_results]
                
                print(f"  📊 Case {i} Summary:")
                print(f"    RTF: avg={statistics.mean(rtfs):.3f}, min={min(rtfs):.3f}, max={max(rtfs):.3f}")
                print(f"    Time: avg={statistics.mean(times):.3f}s, min={min(times):.3f}s, max={max(times):.3f}s")
        
        # Calculate overall statistics
        successful_results = [r for r in all_results if r["success"]]
        
        if successful_results:
            rtfs = [r["rtf"] for r in successful_results]
            times = [r["synthesis_time"] for r in successful_results]
            
            summary = {
                "total_tests": len(all_results),
                "successful_tests": len(successful_results),
                "success_rate": len(successful_results) / len(all_results),
                "rtf_stats": {
                    "mean": statistics.mean(rtfs),
                    "median": statistics.median(rtfs),
                    "min": min(rtfs),
                    "max": max(rtfs),
                    "stdev": statistics.stdev(rtfs) if len(rtfs) > 1 else 0
                },
                "time_stats": {
                    "mean": statistics.mean(times),
                    "median": statistics.median(times),
                    "min": min(times),
                    "max": max(times),
                    "stdev": statistics.stdev(times) if len(times) > 1 else 0
                },
                "performance_assessment": self._assess_performance(rtfs)
            }
            
            return summary
        else:
            return {
                "total_tests": len(all_results),
                "successful_tests": 0,
                "success_rate": 0,
                "error": "No successful tests"
            }
    
    def _assess_performance(self, rtfs: List[float]) -> Dict[str, Any]:
        """Assess performance against targets"""
        mean_rtf = statistics.mean(rtfs)
        target_rtf = 0.5
        
        assessment = {
            "target_rtf": target_rtf,
            "achieved_rtf": mean_rtf,
            "target_met": mean_rtf < target_rtf,
            "improvement_needed": max(0, mean_rtf - target_rtf),
            "performance_grade": "A" if mean_rtf < 0.3 else "B" if mean_rtf < 0.5 else "C" if mean_rtf < 1.0 else "D"
        }
        
        return assessment
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        if "error" in summary:
            print(f"❌ Test failed: {summary['error']}")
            return
        
        print(f"📊 Tests: {summary['successful_tests']}/{summary['total_tests']} successful ({summary['success_rate']:.1%})")
        
        rtf_stats = summary["rtf_stats"]
        time_stats = summary["time_stats"]
        assessment = summary["performance_assessment"]
        
        print(f"\n⚡ RTF Performance:")
        print(f"   Mean RTF: {rtf_stats['mean']:.3f}")
        print(f"   Median RTF: {rtf_stats['median']:.3f}")
        print(f"   Range: {rtf_stats['min']:.3f} - {rtf_stats['max']:.3f}")
        print(f"   Std Dev: {rtf_stats['stdev']:.3f}")
        
        print(f"\n⏱️  Synthesis Time:")
        print(f"   Mean: {time_stats['mean']:.3f}s")
        print(f"   Median: {time_stats['median']:.3f}s")
        print(f"   Range: {time_stats['min']:.3f}s - {time_stats['max']:.3f}s")
        
        print(f"\n🎯 Performance Assessment:")
        print(f"   Target RTF: < {assessment['target_rtf']}")
        print(f"   Achieved RTF: {assessment['achieved_rtf']:.3f}")
        print(f"   Target Met: {'✅ YES' if assessment['target_met'] else '❌ NO'}")
        print(f"   Grade: {assessment['performance_grade']}")
        
        if not assessment['target_met']:
            print(f"   Improvement Needed: {assessment['improvement_needed']:.3f} RTF reduction")

def main():
    parser = argparse.ArgumentParser(description="Test LiteTTS Docker performance")
    parser.add_argument("--url", default="http://localhost:8354", help="Base URL for LiteTTS API")
    parser.add_argument("--voice", default="af_heart", help="Voice to use for testing")
    parser.add_argument("--iterations", type=int, default=3, help="Number of iterations per test case")
    
    args = parser.parse_args()
    
    # Test cases of varying lengths
    test_cases = [
        "Hello world!",
        "This is a medium length sentence to test the performance of the TTS system.",
        "This is a longer paragraph that contains multiple sentences and should provide a good test of the text-to-speech system's performance under more realistic conditions. It includes various punctuation marks and should give us a better understanding of how the system performs with longer inputs.",
        "The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet and is commonly used for testing purposes. It's a classic example that helps evaluate the quality and performance of text processing systems.",
        "In the realm of artificial intelligence and machine learning, text-to-speech synthesis has become an increasingly important technology. Modern TTS systems leverage deep neural networks and advanced signal processing techniques to generate natural-sounding speech from written text. The quality of these systems has improved dramatically over the past decade, with some achieving near-human levels of naturalness and intelligibility."
    ]
    
    tester = PerformanceTest(args.url)
    
    # Check if API is healthy
    print("🔍 Checking API health...")
    if not tester.test_health():
        print("❌ API health check failed. Make sure the LiteTTS container is running.")
        return 1
    
    print("✅ API is healthy")
    
    # Run performance test
    summary = tester.run_performance_test(test_cases, args.voice, args.iterations)
    
    # Print results
    tester.print_summary(summary)
    
    # Return appropriate exit code
    if "error" in summary:
        return 1
    elif summary["performance_assessment"]["target_met"]:
        print("\n🎉 Performance target achieved!")
        return 0
    else:
        print("\n⚠️ Performance target not met")
        return 1

if __name__ == "__main__":
    exit(main())
