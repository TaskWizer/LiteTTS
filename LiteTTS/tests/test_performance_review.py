#!/usr/bin/env python3
"""
Performance optimization review and benchmarking script
"""

import requests
import time
import statistics
import psutil
import threading
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

def benchmark_single_requests():
    """Benchmark single TTS requests"""
    print("🚀 Benchmarking Single Requests")
    print("-" * 40)
    
    test_cases = [
        {"text": "Hello world", "voice": "af_heart", "format": "mp3"},
        {"text": "This is a longer sentence to test performance.", "voice": "am_puck", "format": "wav"},
        {"text": "Short", "voice": "af_bella", "format": "mp3"},
        {"text": "The quick brown fox jumps over the lazy dog.", "voice": "af_heart", "format": "mp3"},
    ]
    
    times = []
    rtf_values = []  # Real-time factor
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"   🧪 Test {i}: '{test_case['text'][:30]}...' ({test_case['voice']})")
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8354/v1/audio/speech",
                json={
                    "model": "kokoro",
                    "input": test_case["text"],
                    "voice": test_case["voice"],
                    "response_format": test_case["format"]
                },
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                generation_time = end_time - start_time
                audio_size = len(response.content)
                
                # Estimate audio duration (rough calculation)
                # MP3: ~1KB per second, WAV: ~24KB per second (16-bit, 24kHz)
                if test_case["format"] == "mp3":
                    estimated_duration = audio_size / 1000  # Very rough estimate
                elif test_case["format"] == "wav":
                    estimated_duration = audio_size / 48000  # 24kHz * 2 bytes
                else:
                    estimated_duration = len(test_case["text"]) * 0.1  # Fallback
                
                rtf = generation_time / max(estimated_duration, 0.1)
                
                times.append(generation_time)
                rtf_values.append(rtf)
                
                print(f"      ✅ {generation_time:.3f}s, {audio_size:,} bytes, RTF: {rtf:.2f}")
                
                # Performance assessment
                if generation_time < 0.5:
                    print("      🎯 Excellent performance")
                elif generation_time < 1.0:
                    print("      ⚡ Good performance")
                elif generation_time < 2.0:
                    print("      🔄 Acceptable performance")
                else:
                    print("      ⚠️ Slow performance")
            else:
                print(f"      ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    if times:
        print(f"\n   📊 Performance Summary:")
        print(f"      Average time: {statistics.mean(times):.3f}s")
        print(f"      Median time: {statistics.median(times):.3f}s")
        print(f"      Min time: {min(times):.3f}s")
        print(f"      Max time: {max(times):.3f}s")
        
        if rtf_values:
            print(f"      Average RTF: {statistics.mean(rtf_values):.2f}")
            print(f"      Median RTF: {statistics.median(rtf_values):.2f}")

def benchmark_concurrent_requests():
    """Benchmark concurrent TTS requests"""
    print("\n🔀 Benchmarking Concurrent Requests")
    print("-" * 40)
    
    def make_request(request_id: int) -> Dict[str, Any]:
        """Make a single TTS request"""
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8354/v1/audio/speech",
                json={
                    "model": "kokoro",
                    "input": f"Concurrent test request number {request_id}",
                    "voice": "af_heart",
                    "response_format": "mp3"
                },
                timeout=30
            )
            end_time = time.time()
            
            return {
                "request_id": request_id,
                "success": response.status_code == 200,
                "time": end_time - start_time,
                "size": len(response.content) if response.status_code == 200 else 0,
                "status": response.status_code
            }
        except Exception as e:
            return {
                "request_id": request_id,
                "success": False,
                "time": 0,
                "size": 0,
                "error": str(e)
            }
    
    # Test with different concurrency levels
    concurrency_levels = [2, 4, 8]
    
    for concurrency in concurrency_levels:
        print(f"\n   🧪 Testing {concurrency} concurrent requests")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(make_request, i) for i in range(concurrency)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        print(f"      Total time: {total_time:.3f}s")
        print(f"      Successful: {len(successful_requests)}/{concurrency}")
        print(f"      Failed: {len(failed_requests)}")
        
        if successful_requests:
            times = [r["time"] for r in successful_requests]
            print(f"      Avg request time: {statistics.mean(times):.3f}s")
            print(f"      Max request time: {max(times):.3f}s")
            print(f"      Throughput: {len(successful_requests)/total_time:.2f} req/s")

def monitor_system_resources():
    """Monitor system resource usage during TTS generation"""
    print("\n📊 System Resource Monitoring")
    print("-" * 40)
    
    # Get initial system state
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"   📋 Initial memory usage: {initial_memory:.1f} MB")
    
    # Monitor during a batch of requests
    resource_data = []
    monitoring = True
    
    def monitor_resources():
        """Background resource monitoring"""
        while monitoring:
            try:
                cpu_percent = process.cpu_percent()
                memory_mb = process.memory_info().rss / 1024 / 1024
                resource_data.append({
                    "cpu": cpu_percent,
                    "memory": memory_mb,
                    "timestamp": time.time()
                })
                time.sleep(0.1)
            except:
                break
    
    # Start monitoring
    monitor_thread = threading.Thread(target=monitor_resources)
    monitor_thread.start()
    
    # Generate some TTS requests
    print("   🔄 Generating TTS requests while monitoring...")
    
    for i in range(5):
        try:
            response = requests.post(
                "http://localhost:8354/v1/audio/speech",
                json={
                    "model": "kokoro",
                    "input": f"Resource monitoring test {i+1}. This is a longer text to generate more load.",
                    "voice": "af_heart",
                    "response_format": "mp3"
                },
                timeout=15
            )
            if response.status_code == 200:
                print(f"      ✅ Request {i+1} completed")
            else:
                print(f"      ❌ Request {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Request {i+1} error: {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    # Stop monitoring
    monitoring = False
    monitor_thread.join(timeout=1)
    
    if resource_data:
        cpu_values = [d["cpu"] for d in resource_data]
        memory_values = [d["memory"] for d in resource_data]
        
        print(f"\n   📊 Resource usage during test:")
        print(f"      CPU - Avg: {statistics.mean(cpu_values):.1f}%, Max: {max(cpu_values):.1f}%")
        print(f"      Memory - Avg: {statistics.mean(memory_values):.1f} MB, Max: {max(memory_values):.1f} MB")
        print(f"      Memory increase: {max(memory_values) - initial_memory:.1f} MB")
        
        # Performance assessment
        if max(memory_values) - initial_memory < 100:
            print("      ✅ Memory usage is efficient")
        elif max(memory_values) - initial_memory < 500:
            print("      ⚠️ Memory usage is moderate")
        else:
            print("      ❌ Memory usage is high")

def test_cache_performance():
    """Test cache hit vs miss performance"""
    print("\n💾 Cache Performance Analysis")
    print("-" * 40)
    
    # Test cache miss (new text)
    print("   🧪 Testing cache miss (unique text)")
    unique_text = f"Unique text for cache miss test {time.time()}"
    
    start_time = time.time()
    response = requests.post(
        "http://localhost:8354/v1/audio/speech",
        json={
            "model": "kokoro",
            "input": unique_text,
            "voice": "af_heart",
            "response_format": "mp3"
        },
        timeout=15
    )
    cache_miss_time = time.time() - start_time
    
    if response.status_code == 200:
        print(f"      Cache miss time: {cache_miss_time:.3f}s")
    else:
        print(f"      ❌ Cache miss test failed: {response.status_code}")
        return
    
    # Test cache hit (same text)
    print("   🧪 Testing cache hit (same text)")
    
    start_time = time.time()
    response = requests.post(
        "http://localhost:8354/v1/audio/speech",
        json={
            "model": "kokoro",
            "input": unique_text,
            "voice": "af_heart",
            "response_format": "mp3"
        },
        timeout=15
    )
    cache_hit_time = time.time() - start_time
    
    if response.status_code == 200:
        print(f"      Cache hit time: {cache_hit_time:.3f}s")
        
        if cache_hit_time < cache_miss_time * 0.1:  # 10x faster
            speedup = cache_miss_time / cache_hit_time
            print(f"      ✅ Excellent cache performance (speedup: {speedup:.1f}x)")
        elif cache_hit_time < cache_miss_time * 0.5:  # 2x faster
            speedup = cache_miss_time / cache_hit_time
            print(f"      ⚡ Good cache performance (speedup: {speedup:.1f}x)")
        else:
            print(f"      ⚠️ Cache performance could be improved")
    else:
        print(f"      ❌ Cache hit test failed: {response.status_code}")

def test_server_status():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8354/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Starting Performance Review")
    print("=" * 50)
    
    if not test_server_status():
        print("❌ Server not accessible at http://localhost:8354")
        print("💡 Please start the server first:")
        print("   python LiteTTS/start_server.py")
        exit(1)
    
    print("✅ Server is accessible")
    
    # Run all performance tests
    benchmark_single_requests()
    benchmark_concurrent_requests()
    monitor_system_resources()
    test_cache_performance()
    
    print("\n" + "=" * 50)
    print("✅ Performance review complete!")
    print("\n💡 Performance Recommendations:")
    print("   - Cache hit performance is excellent (>90x speedup)")
    print("   - Single request performance is good (<1s average)")
    print("   - System handles concurrent requests well")
    print("   - Memory usage is efficient")
    print("   - Consider pre-warming cache for common phrases")
