#!/usr/bin/env python3
"""
Quick Model Performance Test for LiteTTS
Tests the current model performance and provides baseline metrics.
"""

import os
import sys
import time
import json
import psutil
import requests
from pathlib import Path
from typing import Dict, List, Any

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_current_model_performance():
    """Test the current model performance via API"""
    
    # Test phrases of different lengths
    test_phrases = [
        ("Hello world", "short"),
        ("The quick brown fox jumps over the lazy dog", "medium"), 
        ("This is a longer sentence designed to test the performance of the text-to-speech system with more complex phonetic patterns and varied intonation.", "long"),
        ("Testing numbers: 1, 2, 3, 4, 5 and punctuation! How does it sound?", "mixed")
    ]
    
    # Test voices
    test_voices = ["af_heart", "am_puck", "am_liam"]
    
    print("🔬 LiteTTS Performance Test")
    print("=" * 50)
    
    # Get baseline memory
    process = psutil.Process()
    baseline_memory = process.memory_info().rss / 1024 / 1024
    print(f"📊 Baseline Memory: {baseline_memory:.1f} MB")
    
    results = []
    
    for voice in test_voices:
        print(f"\n🎭 Testing voice: {voice}")
        
        for text, category in test_phrases:
            print(f"  📝 {category}: {text[:30]}...")
            
            # Test via API
            start_time = time.time()
            cpu_start = psutil.cpu_percent()
            
            try:
                response = requests.post(
                    "http://localhost:8366/api/tts",
                    json={
                        "text": text,
                        "voice": voice,
                        "format": "wav"
                    },
                    timeout=30
                )
                
                generation_time = time.time() - start_time
                cpu_end = psutil.cpu_percent()
                current_memory = process.memory_info().rss / 1024 / 1024
                
                if response.status_code == 200:
                    # Estimate audio length (assuming 24kHz, 16-bit)
                    audio_size = len(response.content)
                    estimated_audio_length = audio_size / (24000 * 2)  # seconds
                    rtf = generation_time / estimated_audio_length if estimated_audio_length > 0 else 0
                    
                    result = {
                        "voice": voice,
                        "text_category": category,
                        "text_length": len(text),
                        "generation_time_ms": generation_time * 1000,
                        "estimated_audio_length_ms": estimated_audio_length * 1000,
                        "rtf": rtf,
                        "audio_size_bytes": audio_size,
                        "memory_mb": current_memory,
                        "memory_overhead_mb": current_memory - baseline_memory,
                        "cpu_usage_percent": (cpu_start + cpu_end) / 2,
                        "success": True
                    }
                    
                    print(f"    ✅ RTF: {rtf:.3f}, Time: {generation_time*1000:.0f}ms, Memory: +{current_memory-baseline_memory:.1f}MB")
                    
                else:
                    result = {
                        "voice": voice,
                        "text_category": category,
                        "error": f"HTTP {response.status_code}",
                        "success": False
                    }
                    print(f"    ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                result = {
                    "voice": voice,
                    "text_category": category,
                    "error": str(e),
                    "success": False
                }
                print(f"    ❌ Error: {e}")
            
            results.append(result)
            time.sleep(0.5)  # Brief pause between tests
    
    return results

def analyze_results(results: List[Dict]) -> Dict[str, Any]:
    """Analyze test results and generate report"""
    successful_results = [r for r in results if r.get("success", False)]
    failed_results = [r for r in results if not r.get("success", False)]
    
    if not successful_results:
        return {
            "summary": "No successful tests",
            "total_tests": len(results),
            "failed_tests": len(failed_results)
        }
    
    # Calculate statistics
    rtf_values = [r["rtf"] for r in successful_results]
    memory_values = [r["memory_overhead_mb"] for r in successful_results]
    generation_times = [r["generation_time_ms"] for r in successful_results]
    
    import statistics
    
    analysis = {
        "summary": {
            "total_tests": len(results),
            "successful_tests": len(successful_results),
            "failed_tests": len(failed_results),
            "success_rate": len(successful_results) / len(results) * 100
        },
        "performance_metrics": {
            "rtf": {
                "mean": statistics.mean(rtf_values),
                "median": statistics.median(rtf_values),
                "min": min(rtf_values),
                "max": max(rtf_values),
                "std": statistics.stdev(rtf_values) if len(rtf_values) > 1 else 0
            },
            "memory_overhead_mb": {
                "mean": statistics.mean(memory_values),
                "median": statistics.median(memory_values),
                "min": min(memory_values),
                "max": max(memory_values)
            },
            "generation_time_ms": {
                "mean": statistics.mean(generation_times),
                "median": statistics.median(generation_times),
                "min": min(generation_times),
                "max": max(generation_times)
            }
        },
        "current_model_assessment": {
            "rtf_target_met": statistics.mean(rtf_values) < 0.25,
            "memory_target_met": statistics.mean(memory_values) < 150,
            "performance_grade": "A" if statistics.mean(rtf_values) < 0.2 else "B" if statistics.mean(rtf_values) < 0.25 else "C"
        },
        "detailed_results": results
    }
    
    return analysis

def generate_report(analysis: Dict[str, Any]):
    """Generate and save performance report"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Save JSON report
    json_file = f"performance_test_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Generate markdown report
    md_file = f"performance_test_{timestamp}.md"
    with open(md_file, 'w') as f:
        f.write("# LiteTTS Current Model Performance Test\n\n")
        
        summary = analysis["summary"]
        f.write("## Test Summary\n\n")
        f.write(f"- **Total Tests**: {summary['total_tests']}\n")
        f.write(f"- **Successful**: {summary['successful_tests']}\n")
        f.write(f"- **Failed**: {summary['failed_tests']}\n")
        f.write(f"- **Success Rate**: {summary['success_rate']:.1f}%\n\n")
        
        if "performance_metrics" in analysis:
            metrics = analysis["performance_metrics"]
            f.write("## Performance Metrics\n\n")
            
            f.write("### Real-Time Factor (RTF)\n")
            rtf = metrics["rtf"]
            f.write(f"- **Mean**: {rtf['mean']:.3f}\n")
            f.write(f"- **Median**: {rtf['median']:.3f}\n")
            f.write(f"- **Range**: {rtf['min']:.3f} - {rtf['max']:.3f}\n")
            f.write(f"- **Std Dev**: {rtf['std']:.3f}\n\n")
            
            f.write("### Memory Usage\n")
            memory = metrics["memory_overhead_mb"]
            f.write(f"- **Mean Overhead**: {memory['mean']:.1f} MB\n")
            f.write(f"- **Range**: {memory['min']:.1f} - {memory['max']:.1f} MB\n\n")
            
            f.write("### Generation Time\n")
            gen_time = metrics["generation_time_ms"]
            f.write(f"- **Mean**: {gen_time['mean']:.0f} ms\n")
            f.write(f"- **Range**: {gen_time['min']:.0f} - {gen_time['max']:.0f} ms\n\n")
            
            assessment = analysis["current_model_assessment"]
            f.write("## Current Model Assessment\n\n")
            f.write(f"- **RTF Target (<0.25)**: {'✅ Met' if assessment['rtf_target_met'] else '❌ Not Met'}\n")
            f.write(f"- **Memory Target (<150MB)**: {'✅ Met' if assessment['memory_target_met'] else '❌ Not Met'}\n")
            f.write(f"- **Performance Grade**: {assessment['performance_grade']}\n\n")
    
    print(f"\n📄 Reports saved:")
    print(f"  - JSON: {json_file}")
    print(f"  - Markdown: {md_file}")
    
    return analysis

def main():
    """Run the performance test"""
    print("🚀 Starting LiteTTS Performance Test...")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8366/health", timeout=5)
        if response.status_code != 200:
            print("❌ LiteTTS server not responding properly")
            return
    except:
        print("❌ LiteTTS server not accessible at localhost:8366")
        print("   Please start the server first: python app.py --port 8366")
        return
    
    # Run tests
    results = test_current_model_performance()
    
    # Analyze results
    analysis = analyze_results(results)
    
    # Generate report
    final_analysis = generate_report(analysis)
    
    # Print summary
    print("\n" + "="*60)
    print("🎯 PERFORMANCE TEST COMPLETE")
    print("="*60)
    
    if "performance_metrics" in final_analysis:
        metrics = final_analysis["performance_metrics"]
        assessment = final_analysis["current_model_assessment"]
        
        print(f"📊 Current Model (model_q4.onnx) Performance:")
        print(f"   RTF: {metrics['rtf']['mean']:.3f} (target: <0.25)")
        print(f"   Memory: {metrics['memory_overhead_mb']['mean']:.1f}MB (target: <150MB)")
        print(f"   Grade: {assessment['performance_grade']}")
        print(f"   Targets Met: RTF {'✅' if assessment['rtf_target_met'] else '❌'}, Memory {'✅' if assessment['memory_target_met'] else '❌'}")
    
    print("="*60)

if __name__ == "__main__":
    main()
