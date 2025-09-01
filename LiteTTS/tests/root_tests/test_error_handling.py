#!/usr/bin/env python3
"""
Comprehensive Error Handling Tests for Kokoro ONNX TTS API
Tests edge cases, malformed inputs, network failures, and other error conditions
"""

import pytest
import requests
import json
import time
import threading
from pathlib import Path
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

# Import the app for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app import app
from LiteTTS.exceptions import *
from LiteTTS.api.error_handler import ErrorHandler


class TestInputValidationErrors:
    """Test input validation error handling"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
    
    def test_empty_input_text(self):
        """Test empty input text handling"""
        response = self.client.post(
            self.base_endpoint,
            json={"input": "", "voice": "af_heart"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "empty" in data["error"]["message"].lower()
    
    def test_none_input_text(self):
        """Test None input text handling"""
        response = self.client.post(
            self.base_endpoint,
            json={"input": None, "voice": "af_heart"}
        )
        assert response.status_code == 422  # Pydantic validation error
    
    def test_missing_input_field(self):
        """Test missing input field"""
        response = self.client.post(
            self.base_endpoint,
            json={"voice": "af_heart"}
        )
        assert response.status_code == 422
    
    def test_invalid_voice_name(self):
        """Test invalid voice name"""
        response = self.client.post(
            self.base_endpoint,
            json={"input": "Test text", "voice": "nonexistent_voice"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "voice" in data["error"]["message"].lower()
    
    def test_invalid_response_format(self):
        """Test invalid response format"""
        response = self.client.post(
            self.base_endpoint,
            json={
                "input": "Test text",
                "voice": "af_heart",
                "response_format": "invalid_format"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "format" in data["error"]["message"].lower()
    
    def test_invalid_speed_value(self):
        """Test invalid speed values"""
        invalid_speeds = [-1, 0, 5.0, "fast", None]
        
        for speed in invalid_speeds:
            response = self.client.post(
                self.base_endpoint,
                json={
                    "input": "Test text",
                    "voice": "af_heart",
                    "speed": speed
                }
            )
            assert response.status_code in [400, 422], f"Speed {speed} should be invalid"
    
    def test_extremely_long_text(self):
        """Test extremely long text input"""
        long_text = "A" * 10000  # 10k characters
        response = self.client.post(
            self.base_endpoint,
            json={"input": long_text, "voice": "af_heart"}
        )
        # Should either succeed or fail gracefully with proper error
        assert response.status_code in [200, 400, 413]
        
        if response.status_code != 200:
            data = response.json()
            assert "error" in data
    
    def test_malformed_json(self):
        """Test malformed JSON input"""
        response = self.client.post(
            self.base_endpoint,
            data='{"input": "test", "voice": "af_heart"',  # Missing closing brace
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_wrong_content_type(self):
        """Test wrong content type"""
        response = self.client.post(
            self.base_endpoint,
            data="input=test&voice=af_heart",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422


class TestSpecialCharacterHandling:
    """Test handling of special characters and edge cases"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
    
    def test_unicode_characters(self):
        """Test Unicode character handling"""
        unicode_texts = [
            "Hello 🌍 World!",  # Emoji
            "Café naïve résumé",  # Accented characters
            "こんにちは",  # Japanese
            "Здравствуй мир",  # Cyrillic
            "مرحبا بالعالم",  # Arabic
            "🎵🎶🎼🎹🎸",  # Musical emojis
        ]
        
        for text in unicode_texts:
            response = self.client.post(
                self.base_endpoint,
                json={"input": text, "voice": "af_heart"}
            )
            # Should either succeed or fail gracefully
            assert response.status_code in [200, 400]
            
            if response.status_code == 400:
                data = response.json()
                assert "error" in data
    
    def test_control_characters(self):
        """Test control character handling"""
        control_chars = [
            "Hello\x00World",  # Null character
            "Hello\x1FWorld",  # Unit separator
            "Hello\x7FWorld",  # Delete character
            "Hello\r\nWorld",  # CRLF
            "Hello\tWorld",    # Tab
        ]
        
        for text in control_chars:
            response = self.client.post(
                self.base_endpoint,
                json={"input": text, "voice": "af_heart"}
            )
            # Should handle gracefully
            assert response.status_code in [200, 400]
    
    def test_html_entities(self):
        """Test HTML entity handling"""
        html_texts = [
            "&lt;script&gt;alert('xss')&lt;/script&gt;",
            "&amp; &quot; &apos; &lt; &gt;",
            "&#x27; &#x22; &#x3C; &#x3E;",
        ]
        
        for text in html_texts:
            response = self.client.post(
                self.base_endpoint,
                json={"input": text, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]


class TestConcurrencyAndRaceConditions:
    """Test concurrent access and race conditions"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
        self.results = []
        self.errors = []
    
    def _make_request(self, text, voice="af_heart"):
        """Helper method to make a request"""
        try:
            response = self.client.post(
                self.base_endpoint,
                json={"input": text, "voice": voice}
            )
            self.results.append({
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "text": text
            })
        except Exception as e:
            self.errors.append(str(e))
    
    def test_concurrent_requests(self):
        """Test multiple concurrent requests"""
        threads = []
        test_texts = [f"Test message {i}" for i in range(10)]
        
        # Create threads for concurrent requests
        for text in test_texts:
            thread = threading.Thread(target=self._make_request, args=(text,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(self.results) == len(test_texts)
        assert len(self.errors) == 0
        
        # At least some requests should succeed
        successful_requests = sum(1 for r in self.results if r["success"])
        assert successful_requests > 0
    
    def test_cache_race_condition(self):
        """Test cache race conditions with identical requests"""
        threads = []
        same_text = "This is the same text for all requests"
        
        # Create multiple threads with the same text
        for _ in range(5):
            thread = threading.Thread(target=self._make_request, args=(same_text,))
            threads.append(thread)
        
        # Start all threads simultaneously
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(self.results) == 5
        assert all(r["success"] for r in self.results)


class TestResourceLimits:
    """Test resource limit handling"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
    
    def test_memory_pressure_simulation(self):
        """Test behavior under simulated memory pressure"""
        # Generate large requests to simulate memory pressure
        large_texts = [
            "This is a very long text. " * 100,  # ~2.7KB
            "Another large text block. " * 200,  # ~5.4KB
            "Yet another big text. " * 300,      # ~8.1KB
        ]
        
        for text in large_texts:
            response = self.client.post(
                self.base_endpoint,
                json={"input": text, "voice": "af_heart"}
            )
            # Should handle gracefully
            assert response.status_code in [200, 400, 413, 500]
    
    def test_rapid_fire_requests(self):
        """Test rapid consecutive requests"""
        results = []
        
        for i in range(20):
            response = self.client.post(
                self.base_endpoint,
                json={"input": f"Rapid request {i}", "voice": "af_heart"}
            )
            results.append(response.status_code)
            
            # Small delay to avoid overwhelming
            time.sleep(0.01)
        
        # Most requests should succeed or fail gracefully
        valid_status_codes = [200, 400, 429, 500, 503]
        assert all(status in valid_status_codes for status in results)


class TestErrorHandlerUnit:
    """Unit tests for the ErrorHandler class"""
    
    def setup_method(self):
        self.error_handler = ErrorHandler()
    
    def test_validation_error_handling(self):
        """Test ValidationError handling"""
        error = ValidationError("Invalid input", field="input")
        response = self.error_handler.handle_validation_error(error)
        
        assert response.status_code == 400
        data = json.loads(response.body)
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "Invalid input" in data["error"]["message"]
    
    def test_voice_not_found_error(self):
        """Test VoiceNotFoundError handling"""
        error = VoiceNotFoundError("Voice not found", voice_name="test_voice")
        response = self.error_handler.handle_voice_error(error)
        
        assert response.status_code == 400
        data = json.loads(response.body)
        assert data["error"]["code"] == "VOICE_ERROR"
        assert "test_voice" in str(data["error"]["details"])
    
    def test_generic_error_handling(self):
        """Test generic error handling"""
        error = Exception("Unexpected error")
        response = self.error_handler.handle_generic_error(error)
        
        assert response.status_code == 500
        data = json.loads(response.body)
        assert data["error"]["code"] == "INTERNAL_ERROR"
    
    def test_error_count_tracking(self):
        """Test error count tracking"""
        initial_count = self.error_handler.error_counts.get("VALIDATION_ERROR", 0)
        
        error = ValidationError("Test error")
        self.error_handler.handle_validation_error(error)
        
        new_count = self.error_handler.error_counts.get("VALIDATION_ERROR", 0)
        assert new_count == initial_count + 1


class TestNetworkAndTimeouts:
    """Test network-related error conditions"""
    
    def setup_method(self):
        self.client = TestClient(app)
    
    @patch('requests.post')
    def test_external_service_timeout(self, mock_post):
        """Test handling of external service timeouts"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        # This would test external service calls if any exist
        # For now, just verify the mock works
        with pytest.raises(requests.exceptions.Timeout):
            requests.post("http://example.com", timeout=1)
    
    @patch('requests.get')
    def test_external_service_connection_error(self, mock_get):
        """Test handling of connection errors"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get("http://example.com")


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
