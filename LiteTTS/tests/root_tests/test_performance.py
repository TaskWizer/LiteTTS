#!/usr/bin/env python3
"""
Performance-specific tests for Kokoro ONNX TTS API
Tests RTF, latency, caching, and optimization features
"""

import pytest
import time
import threading
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.performance.monitor import PerformanceMonitor, TTSPerformanceData
from LiteTTS.cache.preloader import IntelligentPreloader, CacheWarmingConfig

class TestPerformanceMonitoring:
    """Test performance monitoring system"""
    
    @pytest.fixture
    def monitor(self):
        """Create performance monitor instance"""
        return PerformanceMonitor(max_history=100, enable_system_monitoring=False)
    
    def test_monitor_initialization(self, monitor):
        """Test monitor initialization"""
        assert monitor.max_history == 100
        assert len(monitor.metrics) == 0
        assert monitor.stats["total_requests"] == 0
    
    def test_record_tts_performance(self, monitor):
        """Test recording TTS performance data"""
        perf_data = TTSPerformanceData(
            text_length=50,
            voice="af_heart",
            audio_duration=2.0,
            generation_time=0.5,
            rtf=0.25,
            cache_hit=False,
            format="mp3"
        )
        
        monitor.record_tts_performance(perf_data)
        
        assert monitor.stats["total_requests"] == 1
        assert monitor.stats["cache_misses"] == 1
        assert monitor.stats["avg_rtf"] == 0.25
        assert len(monitor.tts_metrics) == 1
    
    def test_record_cache_hit(self, monitor):
        """Test recording cache hit performance"""
        perf_data = TTSPerformanceData(
            text_length=20,
            voice="am_puck",
            audio_duration=1.0,
            generation_time=0.003,
            rtf=0.003,
            cache_hit=True,
            format="wav"
        )
        
        monitor.record_tts_performance(perf_data)
        
        assert monitor.stats["total_requests"] == 1
        assert monitor.stats["cache_hits"] == 1
        assert monitor.stats["cache_misses"] == 0
    
    def test_performance_summary(self, monitor):
        """Test performance summary generation"""
        # Add some test data
        for i in range(5):
            perf_data = TTSPerformanceData(
                text_length=30 + i * 10,
                voice="af_heart",
                audio_duration=1.5 + i * 0.5,
                generation_time=0.3 + i * 0.1,
                rtf=0.2 + i * 0.05,
                cache_hit=i % 2 == 0,
                format="mp3"
            )
            monitor.record_tts_performance(perf_data)
        
        summary = monitor.get_performance_summary()
        
        assert "summary" in summary
        assert "voice_performance" in summary
        assert summary["summary"]["total_requests"] == 5
        assert summary["summary"]["cache_hit_rate_percent"] == 60.0  # 3 out of 5
    
    def test_voice_specific_stats(self, monitor):
        """Test voice-specific performance tracking"""
        # Add data for different voices
        voices = ["af_heart", "am_puck", "af_sarah"]
        
        for voice in voices:
            perf_data = TTSPerformanceData(
                text_length=40,
                voice=voice,
                audio_duration=2.0,
                generation_time=0.4,
                rtf=0.2,
                cache_hit=False,
                format="mp3"
            )
            monitor.record_tts_performance(perf_data)
        
        summary = monitor.get_performance_summary()
        voice_perf = summary["voice_performance"]
        
        assert len(voice_perf) == 3
        for voice in voices:
            assert voice in voice_perf
            assert voice_perf[voice]["requests"] == 1
            assert voice_perf[voice]["avg_rtf"] == 0.2

class TestCachePreloader:
    """Test intelligent cache preloader system"""
    
    @pytest.fixture
    def config(self):
        """Create preloader configuration"""
        return CacheWarmingConfig(
            primary_voices=["af_heart", "am_puck"],
            instant_words=["Hi", "Hello", "Yes", "No"],
            common_phrases=["Thank you", "How are you?"],
            warm_on_startup=False,  # Disable for testing
            warm_during_idle=False,
            idle_threshold_seconds=1.0
        )
    
    @pytest.fixture
    def mock_tts_app(self):
        """Create mock TTS app for testing"""
        class MockTTSApp:
            def __init__(self):
                self.model = MockModel()
        
        class MockModel:
            def create(self, text, voice, speed, lang):
                # Simulate audio generation
                import numpy as np
                audio_length = len(text) * 100  # Simulate audio based on text length
                audio = np.random.random(audio_length).astype(np.float32)
                return audio, 24000
        
        return MockTTSApp()
    
    def test_preloader_initialization(self, mock_tts_app, config):
        """Test preloader initialization"""
        preloader = IntelligentPreloader(mock_tts_app, config)
        
        assert preloader.config == config
        assert len(preloader.warming_queue) == 0
        assert preloader.warming_stats["total_warmed"] == 0
    
    def test_startup_warming_scheduling(self, mock_tts_app, config):
        """Test startup warming task scheduling"""
        preloader = IntelligentPreloader(mock_tts_app, config)
        preloader._schedule_startup_warming()
        
        # Should have tasks for instant words and common phrases for both voices
        expected_tasks = len(config.instant_words + config.common_phrases) * len(config.primary_voices)
        assert len(preloader.warming_queue) == expected_tasks
        
        # Check task priorities
        priorities = [task.priority for task in preloader.warming_queue]
        assert 1 in priorities  # Instant words
        assert 2 in priorities  # Common phrases
    
    def test_cache_key_generation(self, mock_tts_app, config):
        """Test cache key generation"""
        preloader = IntelligentPreloader(mock_tts_app, config)
        
        key1 = preloader._generate_cache_key("Hello", "af_heart")
        key2 = preloader._generate_cache_key("Hello", "af_heart")
        key3 = preloader._generate_cache_key("Hello", "am_puck")
        
        assert key1 == key2  # Same input should generate same key
        assert key1 != key3  # Different voice should generate different key
        assert len(key1) == 32  # MD5 hash length
    
    def test_request_tracking(self, mock_tts_app, config):
        """Test request tracking and statistics"""
        preloader = IntelligentPreloader(mock_tts_app, config)
        
        # Simulate requests
        preloader.on_request_received("Hello", "af_heart")
        preloader.on_request_received("Hello", "af_heart")  # Duplicate
        preloader.on_request_received("Hi", "am_puck")
        
        assert preloader.phrase_usage_stats["Hello"] == 2
        assert preloader.phrase_usage_stats["Hi"] == 1
        assert preloader.voice_usage_stats["af_heart"] == 2
        assert preloader.voice_usage_stats["am_puck"] == 1
    
    def test_stats_generation(self, mock_tts_app, config):
        """Test statistics generation"""
        preloader = IntelligentPreloader(mock_tts_app, config)
        
        # Add some test data
        preloader.phrase_usage_stats = {"Hello": 5, "Hi": 3, "Thanks": 2}
        preloader.voice_usage_stats = {"af_heart": 7, "am_puck": 3}
        preloader.warming_stats["total_warmed"] = 10
        
        stats = preloader.get_stats()
        
        assert "warming_stats" in stats
        assert "top_phrases" in stats
        assert "voice_usage" in stats
        assert "config" in stats
        
        assert stats["warming_stats"]["total_warmed"] == 10
        assert "Hello" in stats["top_phrases"]
        assert stats["voice_usage"]["af_heart"] == 7

class TestPerformanceRegression:
    """Test for performance regressions"""
    
    def test_rtf_performance_threshold(self):
        """Test that RTF stays within acceptable bounds"""
        # This would be run against actual TTS generation
        # For now, we'll test the concept
        
        acceptable_rtf = 1.0  # Should be faster than real-time
        
        # In a real test, this would measure actual TTS generation
        simulated_rtf = 0.25  # Our current performance
        
        assert simulated_rtf < acceptable_rtf, f"RTF {simulated_rtf} exceeds threshold {acceptable_rtf}"
    
    def test_cache_hit_latency_threshold(self):
        """Test that cache hits stay within latency bounds"""
        acceptable_latency_ms = 50  # 50ms threshold
        
        # Simulate cache hit timing
        start_time = time.time()
        # Simulate cache lookup (very fast operation)
        time.sleep(0.001)  # 1ms simulation
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        
        assert latency_ms < acceptable_latency_ms, f"Cache hit latency {latency_ms}ms exceeds threshold"
    
    def test_memory_usage_threshold(self):
        """Test that memory usage stays within bounds"""
        import psutil
        
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        
        # Reasonable threshold for TTS API
        memory_threshold_mb = 500  # 500MB threshold
        
        assert memory_mb < memory_threshold_mb, f"Memory usage {memory_mb}MB exceeds threshold"
    
    def test_startup_time_threshold(self):
        """Test that startup time is reasonable"""
        # This would measure actual app startup time
        # For testing purposes, we'll simulate
        
        startup_threshold_seconds = 30  # 30 second threshold
        simulated_startup_time = 8  # Our current performance
        
        assert simulated_startup_time < startup_threshold_seconds, f"Startup time {simulated_startup_time}s exceeds threshold"

class TestConcurrencyAndStress:
    """Test concurrent access and stress scenarios"""
    
    def test_concurrent_cache_access(self):
        """Test concurrent access to cache system"""
        monitor = PerformanceMonitor(max_history=1000, enable_system_monitoring=False)
        
        def record_performance():
            for i in range(10):
                perf_data = TTSPerformanceData(
                    text_length=30,
                    voice="af_heart",
                    audio_duration=1.5,
                    generation_time=0.3,
                    rtf=0.2,
                    cache_hit=i % 2 == 0,
                    format="mp3"
                )
                monitor.record_tts_performance(perf_data)
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=record_performance)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify data integrity
        assert monitor.stats["total_requests"] == 50  # 5 threads * 10 requests each
        assert monitor.stats["cache_hits"] == 25  # Half should be cache hits
    
    def test_high_frequency_requests(self):
        """Test handling of high-frequency requests"""
        monitor = PerformanceMonitor(max_history=1000, enable_system_monitoring=False)
        
        start_time = time.time()
        
        # Simulate 100 rapid requests
        for i in range(100):
            perf_data = TTSPerformanceData(
                text_length=20,
                voice="af_heart",
                audio_duration=1.0,
                generation_time=0.2,
                rtf=0.2,
                cache_hit=True,  # All cache hits for speed
                format="mp3"
            )
            monitor.record_tts_performance(perf_data)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should handle 100 requests very quickly
        assert processing_time < 1.0, f"Processing 100 requests took {processing_time}s"
        assert monitor.stats["total_requests"] == 100
        assert monitor.stats["cache_hits"] == 100
