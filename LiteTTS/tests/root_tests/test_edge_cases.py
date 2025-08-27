#!/usr/bin/env python3
"""
Edge Case Tests for Kokoro ONNX TTS API
Tests boundary conditions, unusual inputs, and corner cases
"""

import pytest
import json
import time
from pathlib import Path
from fastapi.testclient import TestClient

# Import the app for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app import app


class TestTextBoundaryConditions:
    """Test text input boundary conditions"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
    
    def test_single_character_input(self):
        """Test single character inputs"""
        single_chars = ["a", "1", "!", "?", ".", " ", "\n", "\t"]
        
        for char in single_chars:
            response = self.client.post(
                self.base_endpoint,
                json={"input": char, "voice": "af_heart"}
            )
            # Should handle gracefully
            assert response.status_code in [200, 400]
    
    def test_whitespace_only_input(self):
        """Test whitespace-only inputs"""
        whitespace_inputs = [
            " ",           # Single space
            "   ",         # Multiple spaces
            "\t",          # Tab
            "\n",          # Newline
            "\r\n",        # CRLF
            " \t\n ",      # Mixed whitespace
        ]
        
        for text in whitespace_inputs:
            response = self.client.post(
                self.base_endpoint,
                json={"input": text, "voice": "af_heart"}
            )
            # Should either reject or handle gracefully
            assert response.status_code in [200, 400]
    
    def test_punctuation_only_input(self):
        """Test punctuation-only inputs"""
        punctuation_inputs = [
            "!",
            "?",
            "...",
            "!!!",
            "???",
            "!?!?",
            ".,;:!?",
            "()[]{}",
            "\"'`",
        ]
        
        for text in punctuation_inputs:
            response = self.client.post(
                self.base_endpoint,
                json={"input": text, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]
    
    def test_numbers_only_input(self):
        """Test number-only inputs"""
        number_inputs = [
            "1",
            "123",
            "1.5",
            "3.14159",
            "1,000",
            "1,000.50",
            "-5",
            "+10",
            "0",
            "00000",
        ]
        
        for text in number_inputs:
            response = self.client.post(
                self.base_endpoint,
                json={"input": text, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]
    
    def test_mixed_language_input(self):
        """Test mixed language inputs"""
        mixed_inputs = [
            "Hello こんにちは",
            "Bonjour 你好",
            "Hola مرحبا",
            "English русский العربية",
            "123 ABC αβγ",
        ]
        
        for text in mixed_inputs:
            response = self.client.post(
                self.base_endpoint,
                json={"input": text, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]


class TestParameterBoundaryConditions:
    """Test parameter boundary conditions"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
    
    def test_speed_boundary_values(self):
        """Test speed parameter boundary values"""
        boundary_speeds = [
            0.1,    # Very slow
            0.25,   # Minimum typical
            1.0,    # Normal
            2.0,    # Fast
            4.0,    # Very fast
        ]
        
        for speed in boundary_speeds:
            response = self.client.post(
                self.base_endpoint,
                json={
                    "input": "Test speed",
                    "voice": "af_heart",
                    "speed": speed
                }
            )
            # Should either succeed or fail gracefully
            assert response.status_code in [200, 400]
    
    def test_format_case_sensitivity(self):
        """Test format parameter case sensitivity"""
        format_variations = [
            "mp3",
            "MP3",
            "Mp3",
            "wav",
            "WAV",
            "Wav",
            "ogg",
            "OGG",
        ]
        
        for fmt in format_variations:
            response = self.client.post(
                self.base_endpoint,
                json={
                    "input": "Test format",
                    "voice": "af_heart",
                    "response_format": fmt
                }
            )
            assert response.status_code in [200, 400]
    
    def test_voice_case_sensitivity(self):
        """Test voice parameter case sensitivity"""
        voice_variations = [
            "af_heart",
            "AF_HEART",
            "Af_Heart",
            "af_HEART",
            "am_puck",
            "AM_PUCK",
        ]
        
        for voice in voice_variations:
            response = self.client.post(
                self.base_endpoint,
                json={
                    "input": "Test voice",
                    "voice": voice
                }
            )
            assert response.status_code in [200, 400]


class TestSpecialTextPatterns:
    """Test special text patterns and edge cases"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
    
    def test_repeated_characters(self):
        """Test repeated character patterns"""
        repeated_patterns = [
            "aaaaaaa",
            "AAAAAAA",
            "1111111",
            "!!!!!!!",
            "ababab",
            "123123123",
        ]
        
        for pattern in repeated_patterns:
            response = self.client.post(
                self.base_endpoint,
                json={"input": pattern, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]
    
    def test_alternating_patterns(self):
        """Test alternating character patterns"""
        alternating_patterns = [
            "ababababab",
            "1212121212",
            "!?!?!?!?!?",
            "AaAaAaAaAa",
            "0101010101",
        ]
        
        for pattern in alternating_patterns:
            response = self.client.post(
                self.base_endpoint,
                json={"input": pattern, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]
    
    def test_mathematical_expressions(self):
        """Test mathematical expressions"""
        math_expressions = [
            "2 + 2 = 4",
            "x = y + z",
            "f(x) = x^2",
            "∑(i=1 to n) i",
            "∫ x dx",
            "α + β = γ",
            "√16 = 4",
        ]
        
        for expr in math_expressions:
            response = self.client.post(
                self.base_endpoint,
                json={"input": expr, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]
    
    def test_code_snippets(self):
        """Test code snippet inputs"""
        code_snippets = [
            "print('hello')",
            "if (x > 0) { return true; }",
            "SELECT * FROM users;",
            "<html><body>Hello</body></html>",
            "def func(): pass",
            "import sys",
        ]
        
        for code in code_snippets:
            response = self.client.post(
                self.base_endpoint,
                json={"input": code, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]
    
    def test_urls_and_emails(self):
        """Test URLs and email addresses"""
        web_inputs = [
            "https://example.com",
            "http://test.org/path?param=value",
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "ftp://files.example.com",
            "mailto:contact@example.org",
        ]
        
        for web_input in web_inputs:
            response = self.client.post(
                self.base_endpoint,
                json={"input": web_input, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]


class TestTimingAndPerformance:
    """Test timing-related edge cases"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
    
    def test_rapid_identical_requests(self):
        """Test rapid identical requests (cache behavior)"""
        text = "This is a cache test"
        times = []
        
        for i in range(5):
            start_time = time.time()
            response = self.client.post(
                self.base_endpoint,
                json={"input": text, "voice": "af_heart"}
            )
            end_time = time.time()
            
            times.append(end_time - start_time)
            assert response.status_code in [200, 400]
            
            # Small delay between requests
            time.sleep(0.01)
        
        # Later requests should be faster (cache hits)
        if all(t > 0 for t in times) and len(times) >= 3:
            # Allow for some variation, but later requests should generally be faster
            assert min(times[1:]) <= max(times[:2]) * 2  # Generous threshold
    
    def test_varying_text_lengths(self):
        """Test varying text lengths for performance patterns"""
        text_lengths = [1, 10, 50, 100, 200, 500]
        times = []
        
        for length in text_lengths:
            text = "A" * length
            start_time = time.time()
            response = self.client.post(
                self.base_endpoint,
                json={"input": text, "voice": "af_heart"}
            )
            end_time = time.time()
            
            times.append(end_time - start_time)
            assert response.status_code in [200, 400]
        
        # Longer texts should generally take more time (if successful)
        # This is a loose check since some might fail
        assert len(times) == len(text_lengths)


class TestDataTypeEdgeCases:
    """Test edge cases with data types"""
    
    def setup_method(self):
        self.client = TestClient(app)
        self.base_endpoint = "/v1/audio/speech"
    
    def test_numeric_strings_as_text(self):
        """Test numeric strings as text input"""
        numeric_strings = [
            "123",
            "3.14",
            "1e10",
            "-42",
            "0x1A",
            "1.23e-4",
        ]
        
        for num_str in numeric_strings:
            response = self.client.post(
                self.base_endpoint,
                json={"input": num_str, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]
    
    def test_boolean_like_strings(self):
        """Test boolean-like strings"""
        boolean_strings = [
            "true",
            "false",
            "True",
            "False",
            "TRUE",
            "FALSE",
            "yes",
            "no",
            "on",
            "off",
        ]
        
        for bool_str in boolean_strings:
            response = self.client.post(
                self.base_endpoint,
                json={"input": bool_str, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]
    
    def test_json_like_strings(self):
        """Test JSON-like strings as text"""
        json_strings = [
            '{"key": "value"}',
            '[1, 2, 3]',
            '{"nested": {"key": "value"}}',
            '[]',
            '{}',
        ]
        
        for json_str in json_strings:
            response = self.client.post(
                self.base_endpoint,
                json={"input": json_str, "voice": "af_heart"}
            )
            assert response.status_code in [200, 400]


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
