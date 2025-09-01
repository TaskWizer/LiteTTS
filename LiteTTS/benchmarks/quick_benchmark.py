#!/usr/bin/env python3
"""
Quick benchmark script to test TTS performance
"""

import time
import requests
import json
import statistics
import argparse
from typing import List, Dict, Any

def benchmark_tts(base_url: str, num_requests: int = 10, voice: str = "af_heart") -> Dict[str, Any]:
    """Run a quick benchmark of the TTS API"""
    
    test_texts = [
        "Hello, world!",
        "This is a test of the text-to-speech system.",
        "The quick brown fox jumps over the lazy dog.",
        "Performance testing with various text lengths and complexity.",
        "Kokoro ONNX TTS API benchmark test with longer text to measure performance under different conditions."
    ]
    
    results = []
    cache_hits = 0
    
    print(f"🔬 Running benchmark with {num_requests} requests...")
    print(f"📍 Target URL: {base_url}")
    print(f"🎤 Voice: {voice}")
    
    for i in range(num_requests):
        text = test_texts[i % len(test_texts)]
        
        payload = {
            "input": text,
            "voice": voice,
            "response_format": "mp3"
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/v1/audio/speech",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                audio_size = len(response.content)
                results.append({
                    "text_length": len(text),
                    "response_time": response_time,
                    "audio_size": audio_size,
                    "success": True
                })
                
                # Estimate if this was a cache hit (very fast response)
                if response_time < 0.1:
                    cache_hits += 1
                    
                print(f"✅ Request {i+1}: {response_time:.3f}s ({len(text)} chars, {audio_size} bytes)")
            else:
                print(f"❌ Request {i+1}: HTTP {response.status_code}")
                results.append({
                    "text_length": len(text),
                    "response_time": response_time,
                    "audio_size": 0,
                    "success": False
                })
                
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"❌ Request {i+1}: Error - {e}")
            results.append({
                "text_length": len(text),
                "response_time": response_time,
                "audio_size": 0,
                "success": False
            })
    
    # Calculate statistics
    successful_results = [r for r in results if r["success"]]
    
    if not successful_results:
        return {"error": "No successful requests"}
    
    response_times = [r["response_time"] for r in successful_results]
    
    stats = {
        "total_requests": num_requests,
        "successful_requests": len(successful_results),
        "success_rate": len(successful_results) / num_requests * 100,
        "estimated_cache_hits": cache_hits,
        "cache_hit_rate": cache_hits / len(successful_results) * 100 if successful_results else 0,
        "response_times": {
            "min": min(response_times),
            "max": max(response_times),
            "mean": statistics.mean(response_times),
            "median": statistics.median(response_times),
            "stdev": statistics.stdev(response_times) if len(response_times) > 1 else 0
        },
        "audio_sizes": {
            "min": min(r["audio_size"] for r in successful_results),
            "max": max(r["audio_size"] for r in successful_results),
            "mean": statistics.mean(r["audio_size"] for r in successful_results)
        }
    }
    
    return stats

def main():
    parser = argparse.ArgumentParser(description="Quick TTS API benchmark")
    parser.add_argument("--url", default="http://localhost:8354", help="Base URL of TTS API")
    parser.add_argument("--requests", type=int, default=10, help="Number of requests to make")
    parser.add_argument("--voice", default="af_heart", help="Voice to use for testing")
    
    args = parser.parse_args()
    
    print("🚀 Kokoro ONNX TTS API Quick Benchmark")
    print("=" * 50)
    
    # Test server availability
    try:
        response = requests.get(f"{args.url}/v1/voices", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding properly: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Run benchmark
    results = benchmark_tts(args.url, args.requests, args.voice)
    
    if "error" in results:
        print(f"❌ Benchmark failed: {results['error']}")
        return
    
    # Print results
    print("\n📊 Benchmark Results")
    print("=" * 50)
    print(f"Total Requests: {results['total_requests']}")
    print(f"Successful: {results['successful_requests']} ({results['success_rate']:.1f}%)")
    print(f"Estimated Cache Hits: {results['estimated_cache_hits']} ({results['cache_hit_rate']:.1f}%)")
    print()
    print("Response Times:")
    print(f"  Min: {results['response_times']['min']:.3f}s")
    print(f"  Max: {results['response_times']['max']:.3f}s")
    print(f"  Mean: {results['response_times']['mean']:.3f}s")
    print(f"  Median: {results['response_times']['median']:.3f}s")
    print(f"  Std Dev: {results['response_times']['stdev']:.3f}s")
    print()
    print("Audio Sizes:")
    print(f"  Min: {results['audio_sizes']['min']:,} bytes")
    print(f"  Max: {results['audio_sizes']['max']:,} bytes")
    print(f"  Mean: {results['audio_sizes']['mean']:,.0f} bytes")
    
    # Performance assessment
    mean_time = results['response_times']['mean']
    if mean_time < 0.1:
        rating = "🟢 Excellent (mostly cached)"
    elif mean_time < 0.5:
        rating = "🟢 Excellent"
    elif mean_time < 1.0:
        rating = "🟡 Good"
    elif mean_time < 2.0:
        rating = "🟠 Fair"
    else:
        rating = "🔴 Needs Optimization"
    
    print(f"\n🎯 Performance Rating: {rating}")
    print(f"📈 Estimated RTF: ~{mean_time / 2.0:.2f} (assuming 2s audio average)")

if __name__ == "__main__":
    main()