#!/usr/bin/env python3
"""
Comprehensive Test Suite for Kokoro ONNX TTS API
Tests all API endpoints, performance optimizations, and production features
"""

import pytest
import asyncio
import time
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
import httpx
from fastapi.testclient import TestClient

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app import TTSApp

class TestKokoroTTSAPI:
    """Comprehensive test suite for Kokoro ONNX TTS API"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Create TTS app instance for testing"""
        tts_app = TTSApp()
        tts_app.initialize()
        return tts_app.app
    
    @pytest.fixture(scope="class")
    def client(self, app):
        """Create test client"""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health endpoint functionality"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "model_loaded" in data
        assert "available_voices" in data
        assert isinstance(data["available_voices"], int)
        assert data["available_voices"] > 0
    
    def test_v1_health_endpoint(self, client):
        """Test v1 health endpoint compatibility"""
        response = client.get("/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_voices_endpoint(self, client):
        """Test voices listing endpoint"""
        response = client.get("/voices")
        assert response.status_code == 200
        
        data = response.json()
        assert "voices" in data
        assert isinstance(data["voices"], list)
        assert len(data["voices"]) > 0
        
        # Check voice structure
        voice = data["voices"][0]
        assert "id" in voice
        assert "name" in voice
        assert "gender" in voice
        assert "region" in voice
    
    def test_v1_voices_endpoint(self, client):
        """Test v1 voices endpoint compatibility"""
        response = client.get("/v1/voices")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
    
    def test_models_endpoint(self, client):
        """Test models listing endpoint"""
        response = client.get("/v1/models")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        
        # Check model structure
        model = data["data"][0]
        assert "id" in model
        assert "object" in model
        assert model["object"] == "model"
    
    def test_tts_generation_basic(self, client):
        """Test basic TTS generation"""
        response = client.post(
            "/v1/audio/speech",
            json={
                "input": "Hello, world!",
                "voice": "af_heart",
                "response_format": "mp3"
            }
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("audio/")
        assert len(response.content) > 1000  # Should have substantial audio data
    
    def test_tts_generation_different_voices(self, client):
        """Test TTS generation with different voices"""
        voices = ["af_heart", "am_puck"]
        
        for voice in voices:
            response = client.post(
                "/v1/audio/speech",
                json={
                    "input": "Testing voice generation",
                    "voice": voice,
                    "response_format": "mp3"
                }
            )
            assert response.status_code == 200
            assert len(response.content) > 1000
    
    def test_tts_generation_different_formats(self, client):
        """Test TTS generation with different audio formats"""
        formats = ["mp3", "wav", "flac"]
        
        for fmt in formats:
            response = client.post(
                "/v1/audio/speech",
                json={
                    "input": "Testing audio format",
                    "voice": "af_heart",
                    "response_format": fmt
                }
            )
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("audio/")
    
    def test_tts_generation_speed_control(self, client):
        """Test TTS generation with different speeds"""
        speeds = [0.5, 1.0, 1.5, 2.0]
        
        for speed in speeds:
            response = client.post(
                "/v1/audio/speech",
                json={
                    "input": "Testing speed control",
                    "voice": "af_heart",
                    "response_format": "mp3",
                    "speed": speed
                }
            )
            assert response.status_code == 200
            assert len(response.content) > 500
    
    def test_cache_performance(self, client):
        """Test cache hit performance"""
        text = "Cache performance test"
        
        # First request (cold start)
        start_time = time.time()
        response1 = client.post(
            "/v1/audio/speech",
            json={
                "input": text,
                "voice": "af_heart",
                "response_format": "mp3"
            }
        )
        cold_time = time.time() - start_time
        
        assert response1.status_code == 200
        
        # Second request (should be cached)
        start_time = time.time()
        response2 = client.post(
            "/v1/audio/speech",
            json={
                "input": text,
                "voice": "af_heart",
                "response_format": "mp3"
            }
        )
        cache_time = time.time() - start_time
        
        assert response2.status_code == 200
        assert response1.content == response2.content
        assert cache_time < cold_time  # Cache should be faster
        assert cache_time < 0.1  # Should be very fast (< 100ms)
    
    def test_performance_stats_endpoint(self, client):
        """Test performance monitoring endpoint"""
        response = client.get("/performance/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "summary" in data
        assert "voice_performance" in data
        assert "monitoring_period" in data
        
        summary = data["summary"]
        assert "total_requests" in summary
        assert "cache_hit_rate_percent" in summary
        assert "avg_rtf" in summary
    
    def test_preloader_stats_endpoint(self, client):
        """Test preloader statistics endpoint"""
        response = client.get("/performance/preloader")
        assert response.status_code == 200
        
        data = response.json()
        assert "warming_stats" in data
        assert "warmed_entries" in data
        assert "config" in data
        
        # Should have warmed some entries
        assert data["warmed_entries"] > 0
    
    def test_rtf_trend_endpoint(self, client):
        """Test RTF trend monitoring endpoint"""
        response = client.get("/performance/rtf-trend?minutes=30")
        assert response.status_code == 200
        
        data = response.json()
        assert "trend_data" in data
        assert "period_minutes" in data
        assert "data_points" in data
        assert data["period_minutes"] == 30
    
    def test_performance_export_endpoint(self, client):
        """Test performance metrics export"""
        response = client.post("/performance/export")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "filepath" in data
        
        # Check if file was created
        filepath = Path(data["filepath"])
        assert filepath.exists()
        
        # Cleanup
        filepath.unlink()
    
    def test_error_handling_invalid_voice(self, client):
        """Test error handling for invalid voice"""
        response = client.post(
            "/v1/audio/speech",
            json={
                "input": "Test text",
                "voice": "invalid_voice",
                "response_format": "mp3"
            }
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
    
    def test_error_handling_empty_text(self, client):
        """Test error handling for empty text"""
        response = client.post(
            "/v1/audio/speech",
            json={
                "input": "",
                "voice": "af_heart",
                "response_format": "mp3"
            }
        )
        assert response.status_code == 400
    
    def test_error_handling_invalid_format(self, client):
        """Test error handling for invalid audio format"""
        response = client.post(
            "/v1/audio/speech",
            json={
                "input": "Test text",
                "voice": "af_heart",
                "response_format": "invalid_format"
            }
        )
        assert response.status_code == 400
    
    def test_error_handling_invalid_speed(self, client):
        """Test error handling for invalid speed"""
        response = client.post(
            "/v1/audio/speech",
            json={
                "input": "Test text",
                "voice": "af_heart",
                "response_format": "mp3",
                "speed": -1.0  # Invalid speed
            }
        )
        assert response.status_code == 400
    
    def test_long_text_generation(self, client):
        """Test generation with long text"""
        long_text = "This is a very long text that should test the system's ability to handle extended input. " * 10
        
        response = client.post(
            "/v1/audio/speech",
            json={
                "input": long_text,
                "voice": "af_heart",
                "response_format": "mp3"
            }
        )
        assert response.status_code == 200
        assert len(response.content) > 5000  # Should generate substantial audio
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            response = client.post(
                "/v1/audio/speech",
                json={
                    "input": "Concurrent test",
                    "voice": "af_heart",
                    "response_format": "mp3"
                }
            )
            results.put(response.status_code)
        
        # Start multiple concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # Check all succeeded
        while not results.empty():
            status_code = results.get()
            assert status_code == 200
    
    def test_cache_endpoints(self, client):
        """Test cache management endpoints"""
        # Test cache status
        response = client.get("/cache/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "audio_cache" in data
        assert "text_cache" in data
        
        # Test cache clear
        response = client.post("/cache/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
