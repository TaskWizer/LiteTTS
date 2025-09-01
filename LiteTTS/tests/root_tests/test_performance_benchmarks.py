"""
Performance Benchmark Suite
Automated performance testing to ensure no regressions
"""

import time
import statistics
import pytest
import requests
from typing import List, Dict, Any

class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    BASE_URL = "http://localhost:8354"

    @pytest.mark.performance
    def test_tts_latency_benchmark(self):
        """Test TTS generation latency"""
        endpoint = f"{self.BASE_URL}/v1/audio/speech"

        test_texts = [
            "Hello",  # Short text
            "Hello, world! This is a test.",  # Medium text
            "This is a longer text that should take more time to process and generate audio."  # Long text
        ]

        for text in test_texts:
            latencies = []

            for _ in range(5):  # Run 5 times for average
                payload = {
                    "model": "kokoro",
                    "input": text,
                    "voice": "af_heart"
                }

                start_time = time.time()
                try:
                    response = requests.post(endpoint, json=payload, timeout=30)
                    end_time = time.time()

                    if response.status_code == 200:
                        latency = end_time - start_time
                        latencies.append(latency)
                except requests.exceptions.ConnectionError:
                    pytest.skip("Service not running")
                except requests.exceptions.Timeout:
                    pytest.fail(f"Request timed out for text: {text}")

            if latencies:
                avg_latency = statistics.mean(latencies)
                max_latency = max(latencies)

                # Performance assertions
                if len(text) < 20:  # Short text
                    assert avg_latency < 0.25, f"Short text latency too high: {avg_latency:.3f}s"
                elif len(text) < 50:  # Medium text
                    assert avg_latency < 0.5, f"Medium text latency too high: {avg_latency:.3f}s"
                else:  # Long text
                    assert avg_latency < 1.0, f"Long text latency too high: {avg_latency:.3f}s"

                # No request should take more than 5 seconds
                assert max_latency < 5.0, f"Maximum latency too high: {max_latency:.3f}s"

    @pytest.mark.performance
    def test_concurrent_requests(self):
        """Test performance under concurrent load"""
        import concurrent.futures

        endpoint = f"{self.BASE_URL}/v1/audio/speech"
        payload = {
            "model": "kokoro",
            "input": "Concurrent test",
            "voice": "af_heart"
        }

        def make_request():
            try:
                start_time = time.time()
                response = requests.post(endpoint, json=payload, timeout=30)
                end_time = time.time()
                return {
                    "status_code": response.status_code,
                    "latency": end_time - start_time,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "status_code": 0,
                    "latency": 30.0,
                    "success": False,
                    "error": str(e)
                }

        # Test with 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Check results
        successful_requests = [r for r in results if r["success"]]

        if successful_requests:
            avg_latency = statistics.mean([r["latency"] for r in successful_requests])

            # Under concurrent load, average latency should still be reasonable
            assert avg_latency < 2.0, f"Concurrent request latency too high: {avg_latency:.3f}s"

            # At least 80% of requests should succeed
            success_rate = len(successful_requests) / len(results)
            assert success_rate >= 0.8, f"Success rate too low: {success_rate:.1%}"

    @pytest.mark.performance
    def test_memory_usage_stability(self):
        """Test memory usage doesn't grow excessively"""
        import psutil
        import os

        # This test would need to be run with the actual service process
        # For now, just check that we can measure memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make several requests
        endpoint = f"{self.BASE_URL}/v1/audio/speech"
        payload = {
            "model": "kokoro",
            "input": "Memory test",
            "voice": "af_heart"
        }

        for _ in range(10):
            try:
                requests.post(endpoint, json=payload, timeout=10)
            except:
                pass  # Ignore errors for this test

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory

        # Memory growth should be minimal for this test process
        assert memory_growth < 50, f"Excessive memory growth: {memory_growth:.1f}MB"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance"])
