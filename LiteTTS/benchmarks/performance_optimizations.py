#!/usr/bin/env python3
"""
Performance optimizations for Kokoro ONNX TTS API
Addresses RTF optimization, error reduction, and cache improvements
"""

import sys
import time
import requests
import json
from pathlib import Path

# Add the parent directory to the path so we can import LiteTTS
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_problematic_phrases():
    """Test and fix problematic phrases that cause HTTP 500 errors"""
    
    print("🔍 Testing Problematic Phrases")
    print("=" * 40)
    
    base_url = "http://localhost:8354"
    
    # Known problematic phrases
    problematic_phrases = [
        "I am doing well",
        "I am doing well.",
        "I'm doing well",
        "I'm doing well.",
        "This is a much longer sentence that contains more words and should take longer to process but we want to see how the RTF scales with length",
        "This is a much longer sentence that contains more words.",
        "The quick brown fox jumps over the lazy dog and runs through the forest",
        "Performance testing with various sentence structures and lengths",
        "Real-time factor analysis and optimization techniques"
    ]
    
    successful_phrases = []
    failed_phrases = []
    
    for i, phrase in enumerate(problematic_phrases, 1):
        print(f"\nTest {i}: '{phrase[:50]}{'...' if len(phrase) > 50 else ''}'")
        
        payload = {
            "input": phrase,
            "voice": "af_heart",
            "response_format": "mp3"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/v1/audio/speech",
                json=payload,
                timeout=15
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                print(f"   ✅ Success: {response_time:.3f}s")
                successful_phrases.append(phrase)
            else:
                print(f"   ❌ HTTP {response.status_code}: {response_time:.3f}s")
                failed_phrases.append(phrase)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_phrases.append(phrase)
        
        time.sleep(0.1)  # Small delay
    
    print(f"\n📊 Results:")
    print(f"   ✅ Successful: {len(successful_phrases)}")
    print(f"   ❌ Failed: {len(failed_phrases)}")
    
    if failed_phrases:
        print(f"\n❌ Failed phrases:")
        for phrase in failed_phrases:
            print(f"   - '{phrase[:50]}{'...' if len(phrase) > 50 else ''}'")
    
    return successful_phrases, failed_phrases

def analyze_cache_performance():
    """Analyze and optimize cache performance"""
    
    print("\n\n🎯 Cache Performance Analysis")
    print("=" * 40)
    
    base_url = "http://localhost:8354"
    
    # Test cache warming with common phrases
    common_phrases = [
        "Hello",
        "Thank you",
        "Good morning",
        "How are you",
        "Have a great day",
        "Welcome",
        "Please wait",
        "Loading",
        "Success",
        "Error occurred"
    ]
    
    print("🔥 Warming cache with common phrases...")
    
    for phrase in common_phrases:
        payload = {
            "input": phrase,
            "voice": "af_heart",
            "response_format": "mp3"
        }
        
        try:
            # First request (cache miss)
            start_time = time.time()
            response1 = requests.post(f"{base_url}/v1/audio/speech", json=payload, timeout=10)
            miss_time = time.time() - start_time
            
            if response1.status_code == 200:
                # Second request (cache hit)
                start_time = time.time()
                response2 = requests.post(f"{base_url}/v1/audio/speech", json=payload, timeout=10)
                hit_time = time.time() - start_time
                
                if response2.status_code == 200:
                    speedup = miss_time / hit_time if hit_time > 0 else 0
                    print(f"   '{phrase}': {miss_time:.3f}s → {hit_time:.3f}s (speedup: {speedup:.1f}x)")
                
        except Exception as e:
            print(f"   '{phrase}': Error - {e}")
        
        time.sleep(0.05)  # Small delay

def benchmark_rtf_optimization():
    """Benchmark RTF performance and identify optimization opportunities"""
    
    print("\n\n⚡ RTF Optimization Benchmark")
    print("=" * 40)
    
    base_url = "http://localhost:8354"
    
    # Test different text lengths and complexities
    test_cases = [
        ("Short", "Hello world"),
        ("Medium", "This is a medium length sentence for testing performance"),
        ("Long", "This is a longer sentence that contains more words and should help us understand how the real-time factor scales with different input lengths and complexities"),
        ("Numbers", "The year 2024 has 365 days and 12 months"),
        ("Punctuation", "Hello! How are you? I'm doing great, thanks for asking."),
        ("Technical", "The API returns JSON data via HTTP protocol"),
        ("Mixed", "Testing 123 with symbols & punctuation! Works great.")
    ]
    
    rtf_results = []
    
    for test_type, text in test_cases:
        print(f"\n{test_type} text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        payload = {
            "input": text,
            "voice": "af_heart",
            "response_format": "mp3"
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{base_url}/v1/audio/speech", json=payload, timeout=15)
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                audio_size = len(response.content)
                
                # Estimate audio duration (more accurate than before)
                # MP3 at ~128kbps ≈ 16KB/second, but this varies
                # Better to use a more conservative estimate
                estimated_duration = len(text) / 150 * 60 / 5  # ~150 words per minute, 5 words per second
                estimated_rtf = response_time / estimated_duration if estimated_duration > 0 else 0
                
                print(f"   Response time: {response_time:.3f}s")
                print(f"   Audio size: {audio_size:,} bytes")
                print(f"   Estimated RTF: {estimated_rtf:.3f}")
                
                rtf_results.append({
                    'type': test_type,
                    'text_length': len(text),
                    'response_time': response_time,
                    'estimated_rtf': estimated_rtf
                })
                
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.1)
    
    if rtf_results:
        print(f"\n📊 RTF Analysis:")
        avg_rtf = sum(r['estimated_rtf'] for r in rtf_results) / len(rtf_results)
        print(f"   Average estimated RTF: {avg_rtf:.3f}")
        
        # Find best and worst performing cases
        best = min(rtf_results, key=lambda x: x['estimated_rtf'])
        worst = max(rtf_results, key=lambda x: x['estimated_rtf'])
        
        print(f"   Best performance: {best['type']} (RTF: {best['estimated_rtf']:.3f})")
        print(f"   Worst performance: {worst['type']} (RTF: {worst['estimated_rtf']:.3f})")
    
    return rtf_results

def get_current_performance_metrics():
    """Get current performance metrics from server"""
    
    print("\n\n📊 Current Performance Metrics")
    print("=" * 40)
    
    base_url = "http://localhost:8354"
    
    try:
        response = requests.get(f"{base_url}/performance/stats", timeout=10)
        if response.status_code == 200:
            metrics = response.json()
            summary = metrics.get('summary', {})
            
            print(f"📈 Total Requests: {summary.get('total_requests', 0)}")
            print(f"🎯 Cache Hit Rate: {summary.get('cache_hit_rate_percent', 0):.1f}%")
            print(f"⚡ Average RTF: {summary.get('avg_rtf', 0):.3f}")
            print(f"📊 Min RTF: {summary.get('min_rtf', 0):.3f}")
            print(f"📊 Max RTF: {summary.get('max_rtf', 0):.3f}")
            print(f"⏱️ Average Latency: {summary.get('avg_latency_ms', 0):.1f}ms")
            print(f"🔧 Efficiency Ratio: {summary.get('efficiency_ratio', 0):.2f}")
            
            return metrics
        else:
            print(f"❌ Failed to get metrics: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting metrics: {e}")
        return None

def main():
    """Main optimization analysis"""
    
    print("🎯 Kokoro TTS Performance Optimization Analysis")
    print("=" * 60)
    
    # Test problematic phrases
    successful, failed = test_problematic_phrases()
    
    # Analyze cache performance
    analyze_cache_performance()
    
    # Benchmark RTF optimization
    rtf_results = benchmark_rtf_optimization()
    
    # Get current metrics
    metrics = get_current_performance_metrics()
    
    print("\n" + "=" * 60)
    print("🎯 OPTIMIZATION ANALYSIS COMPLETE")
    
    # Summary and recommendations
    print(f"\n📋 Summary:")
    if failed:
        print(f"   ⚠️ {len(failed)} phrases still cause errors")
        print(f"   💡 Recommendation: Improve text preprocessing")
    else:
        print(f"   ✅ All test phrases working correctly")
    
    if metrics:
        summary = metrics.get('summary', {})
        avg_rtf = summary.get('avg_rtf', 0)
        cache_rate = summary.get('cache_hit_rate_percent', 0)
        
        print(f"   📊 Current RTF: {avg_rtf:.3f}")
        print(f"   🎯 Cache Hit Rate: {cache_rate:.1f}%")
        
        if avg_rtf <= 0.30:
            print(f"   🎉 RTF is excellent!")
        elif avg_rtf <= 0.40:
            print(f"   ✅ RTF is good, minor optimizations possible")
        else:
            print(f"   ⚠️ RTF needs optimization")
        
        if cache_rate >= 80:
            print(f"   🎉 Cache performance is excellent!")
        elif cache_rate >= 60:
            print(f"   ✅ Cache performance is good")
        else:
            print(f"   ⚠️ Cache hit rate could be improved")
    
    return len(failed) == 0 and (not metrics or metrics.get('summary', {}).get('avg_rtf', 1.0) <= 0.40)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
