#!/usr/bin/env python3
"""
Load Testing for Kokoro ONNX TTS API
Tests system behavior under various load conditions and stress scenarios
"""

import pytest
import time
import threading
import statistics
from pathlib import Path
from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the app for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app import app


class TestBasicLoadHandling:
    """Test basic load handling capabilities"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
        self.results = []
        self.errors = []
    
    def _make_request(self, text, request_id):
        """Helper method for load testing requests"""
        try:
            start_time = time.time()
            response = self.client.post(
                self.base_endpoint,
                json={"input": f"{text} {request_id}", "voice": "af_heart"}
            )
            duration = time.time() - start_time
            
            self.results.append({
                "id": request_id,
                "duration": duration,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "audio_size": len(response.content) if response.status_code == 200 else 0
            })
        except Exception as e:
            self.errors.append(f"Request {request_id}: {str(e)}")
    
    def test_light_load_5_concurrent(self):
        """Test light load with 5 concurrent requests"""
        num_requests = 5
        text = "Light load test"
        
        threads = []
        start_time = time.time()
        
        for i in range(num_requests):
            thread = threading.Thread(target=self._make_request, args=(text, i))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Verify all requests completed
        assert len(self.results) == num_requests
        assert len(self.errors) == 0
        
        # Analyze results
        successful_requests = [r for r in self.results if r["success"]]
        success_rate = len(successful_requests) / num_requests
        
        print(f"✅ Light load: {len(successful_requests)}/{num_requests} successful ({success_rate:.1%})")
        print(f"   Total time: {total_time:.3f}s")
        
        # Should handle light load well
        assert success_rate >= 0.8, f"Success rate {success_rate:.1%} too low for light load"
    
    def test_medium_load_10_concurrent(self):
        """Test medium load with 10 concurrent requests"""
        self.results = []
        self.errors = []
        
        num_requests = 10
        text = "Medium load test"
        
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            start_time = time.time()
            
            futures = [
                executor.submit(self._make_request, text, i)
                for i in range(num_requests)
            ]
            
            for future in as_completed(futures):
                future.result()
            
            total_time = time.time() - start_time
        
        # Analysis
        successful_requests = [r for r in self.results if r["success"]]
        success_rate = len(successful_requests) / num_requests
        
        if successful_requests:
            avg_duration = statistics.mean(r["duration"] for r in successful_requests)
            max_duration = max(r["duration"] for r in successful_requests)
            
            print(f"✅ Medium load: {len(successful_requests)}/{num_requests} successful ({success_rate:.1%})")
            print(f"   Total: {total_time:.3f}s, Avg: {avg_duration:.3f}s, Max: {max_duration:.3f}s")
        
        # Should handle medium load reasonably
        assert success_rate >= 0.6, f"Success rate {success_rate:.1%} too low for medium load"
    
    def test_heavy_load_20_concurrent(self):
        """Test heavy load with 20 concurrent requests"""
        self.results = []
        self.errors = []
        
        num_requests = 20
        text = "Heavy load test"
        
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            start_time = time.time()
            
            futures = [
                executor.submit(self._make_request, text, i)
                for i in range(num_requests)
            ]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.errors.append(str(e))
            
            total_time = time.time() - start_time
        
        # Analysis
        successful_requests = [r for r in self.results if r["success"]]
        success_rate = len(successful_requests) / num_requests if num_requests > 0 else 0
        
        print(f"✅ Heavy load: {len(successful_requests)}/{num_requests} successful ({success_rate:.1%})")
        print(f"   Total time: {total_time:.3f}s, Errors: {len(self.errors)}")
        
        # Heavy load may have lower success rate, but should not crash
        assert success_rate >= 0.3, f"Success rate {success_rate:.1%} too low even for heavy load"
        assert len(self.errors) < num_requests // 2, "Too many execution errors"


class TestStressScenarios:
    """Test stress scenarios and edge cases"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
    
    def test_rapid_fire_requests(self):
        """Test rapid consecutive requests without delay"""
        num_requests = 15
        text = "Rapid fire test"
        results = []
        
        start_time = time.time()
        
        for i in range(num_requests):
            try:
                response = self.client.post(
                    self.base_endpoint,
                    json={"input": f"{text} {i}", "voice": "af_heart"}
                )
                results.append({
                    "success": response.status_code == 200,
                    "status": response.status_code
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e)
                })
        
        total_time = time.time() - start_time
        successful = sum(1 for r in results if r["success"])
        
        print(f"✅ Rapid fire: {successful}/{num_requests} successful in {total_time:.3f}s")
        
        # Should handle rapid requests without crashing
        assert successful >= num_requests // 3, "Too few successful rapid requests"
    
    def test_mixed_load_different_voices(self):
        """Test mixed load with different voices"""
        voices = ["af_heart", "am_puck"]
        num_requests_per_voice = 5
        results = []
        
        def make_voice_request(voice, request_id):
            try:
                response = self.client.post(
                    self.base_endpoint,
                    json={
                        "input": f"Mixed voice test {request_id}",
                        "voice": voice
                    }
                )
                return {
                    "voice": voice,
                    "success": response.status_code == 200,
                    "status": response.status_code
                }
            except Exception as e:
                return {
                    "voice": voice,
                    "success": False,
                    "error": str(e)
                }
        
        with ThreadPoolExecutor(max_workers=len(voices) * num_requests_per_voice) as executor:
            futures = []
            
            for voice in voices:
                for i in range(num_requests_per_voice):
                    future = executor.submit(make_voice_request, voice, i)
                    futures.append(future)
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # Analyze by voice
        for voice in voices:
            voice_results = [r for r in results if r["voice"] == voice]
            successful = sum(1 for r in voice_results if r["success"])
            
            print(f"✅ Voice {voice}: {successful}/{len(voice_results)} successful")
            
            # Each voice should handle some requests
            assert successful >= len(voice_results) // 3, f"Voice {voice} handled too few requests"
    
    def test_varying_text_lengths_under_load(self):
        """Test varying text lengths under concurrent load"""
        text_templates = [
            "Short",
            "This is a medium length text for testing purposes.",
            "This is a much longer text that we're using to test how the system handles longer inputs under concurrent load conditions. " * 2,
            "Very long text. " * 20
        ]
        
        results = []
        
        def make_length_request(text, length_category, request_id):
            try:
                start_time = time.time()
                response = self.client.post(
                    self.base_endpoint,
                    json={"input": f"{text} {request_id}", "voice": "af_heart"}
                )
                duration = time.time() - start_time
                
                return {
                    "category": length_category,
                    "length": len(text),
                    "duration": duration,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "category": length_category,
                    "success": False,
                    "error": str(e)
                }
        
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = []
            
            for i, text in enumerate(text_templates):
                for j in range(3):  # 3 requests per text length
                    future = executor.submit(
                        make_length_request, 
                        text, 
                        f"length_{i}", 
                        j
                    )
                    futures.append(future)
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # Analyze by text length category
        categories = set(r["category"] for r in results if "category" in r)
        
        for category in categories:
            category_results = [r for r in results if r.get("category") == category]
            successful = sum(1 for r in category_results if r["success"])
            
            print(f"✅ {category}: {successful}/{len(category_results)} successful")
            
            # Each category should handle some requests
            assert successful >= len(category_results) // 3, f"Category {category} handled too few requests"


class TestResourceExhaustion:
    """Test behavior under resource exhaustion scenarios"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
    
    def test_sustained_load_over_time(self):
        """Test sustained load over a longer period"""
        duration_seconds = 10  # 10 second test
        request_interval = 0.2  # Request every 200ms
        
        results = []
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                response = self.client.post(
                    self.base_endpoint,
                    json={
                        "input": f"Sustained load test {request_count}",
                        "voice": "af_heart"
                    }
                )
                results.append({
                    "timestamp": time.time() - start_time,
                    "success": response.status_code == 200,
                    "status": response.status_code
                })
                request_count += 1
                
            except Exception as e:
                results.append({
                    "timestamp": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                })
            
            time.sleep(request_interval)
        
        total_time = time.time() - start_time
        successful = sum(1 for r in results if r["success"])
        
        print(f"✅ Sustained load: {successful}/{len(results)} successful over {total_time:.1f}s")
        
        # Should maintain some level of service
        success_rate = successful / len(results) if results else 0
        assert success_rate >= 0.4, f"Sustained load success rate {success_rate:.1%} too low"
    
    def test_memory_pressure_simulation(self):
        """Test behavior under simulated memory pressure"""
        # Create requests with larger text to simulate memory pressure
        large_text = "This is a large text block for memory pressure testing. " * 50
        
        results = []
        num_requests = 8
        
        for i in range(num_requests):
            try:
                start_time = time.time()
                response = self.client.post(
                    self.base_endpoint,
                    json={
                        "input": f"{large_text} Request {i}",
                        "voice": "af_heart"
                    }
                )
                duration = time.time() - start_time
                
                results.append({
                    "request_id": i,
                    "duration": duration,
                    "success": response.status_code == 200,
                    "status": response.status_code
                })
                
                # Brief pause between large requests
                time.sleep(0.1)
                
            except Exception as e:
                results.append({
                    "request_id": i,
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r["success"])
        
        print(f"✅ Memory pressure: {successful}/{num_requests} successful")
        
        # Should handle some large requests
        assert successful >= num_requests // 3, "Too few successful requests under memory pressure"


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v", "-s"])  # -s to see print output
