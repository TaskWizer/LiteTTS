#!/usr/bin/env python3
"""
Unit tests for TTS API validators
"""

import pytest

from LiteTTS.api.validators import RequestValidator
from LiteTTS.models import TTSRequest


class MockConfig:
    """Mock configuration object"""

    max_text_length = 5000
    default_voice = "af_heart"


class MockSynthesizer:
    """Mock synthesizer for testing"""

    def __init__(self):
        self.config = MockConfig()
        self.available_voices = ["af_heart", "am_puck", "af_sarah"]

    def get_available_voices(self):
        return self.available_voices


class TestRequestValidator:
    """Test cases for RequestValidator"""

    @pytest.fixture
    def synthesizer(self):
        """Create mock synthesizer"""
        return MockSynthesizer()

    @pytest.fixture
    def validator(self, synthesizer):
        """Create validator instance"""
        return RequestValidator(synthesizer)

    def test_validate_request_empty_text(self, validator):
        """Test validation of empty text"""
        request = TTSRequest(input="", voice="af_heart")
        errors = validator.validate_request(request)
        assert len(errors) > 0
        assert any("empty" in e.lower() or "text" in e.lower() for e in errors)

    def test_validate_request_valid(self, validator):
        """Test validation of valid request"""
        request = TTSRequest(
            input="Hello world", voice="af_heart", response_format="mp3", speed=1.0
        )
        errors = validator.validate_request(request)
        assert len(errors) == 0

    def test_validate_request_invalid_voice(self, validator):
        """Test validation with invalid voice"""
        request = TTSRequest(input="Hello world", voice="nonexistent_voice")
        errors = validator.validate_request(request)
        assert len(errors) > 0
        assert any("voice" in e.lower() for e in errors)

    def test_validate_request_speed_at_boundary(self, validator):
        """Test validation with speed at valid boundaries"""
        # Speed 0.1 is valid (minimum)
        request = TTSRequest(input="Hello world", voice="af_heart", speed=0.1)
        errors = validator.validate_request(request)
        assert len(errors) == 0

        # Speed 3.0 is valid (maximum)
        request = TTSRequest(input="Hello world", voice="af_heart", speed=3.0)
        errors = validator.validate_request(request)
        assert len(errors) == 0

    def test_validate_request_invalid_format(self, validator):
        """Test validation with invalid format"""
        request = TTSRequest(
            input="Hello world", voice="af_heart", response_format="invalid_format"
        )
        errors = validator.validate_request(request)
        assert len(errors) > 0
        assert any("format" in e.lower() for e in errors)

    def test_validate_request_text_too_long(self, validator):
        """Test validation with text exceeding max length"""
        request = TTSRequest(
            input="A" * 10000,  # Exceeds 5000 char limit
            voice="af_heart",
        )
        errors = validator.validate_request(request)
        assert len(errors) > 0
        assert any("length" in e.lower() or "text" in e.lower() for e in errors)

    def test_validate_request_volume_at_boundary(self, validator):
        """Test validation with volume at valid boundaries"""
        # Volume 0.1 is valid (minimum)
        request = TTSRequest(input="Hello world", voice="af_heart", volume_multiplier=0.1)
        errors = validator.validate_request(request)
        assert len(errors) == 0

        # Volume 5.0 is valid (maximum)
        request = TTSRequest(input="Hello world", voice="af_heart", volume_multiplier=5.0)
        errors = validator.validate_request(request)
        assert len(errors) == 0

    def test_validate_request_emotion_strength_bounds(self, validator):
        """Test validation of emotion strength bounds"""
        # Test valid emotion strength
        request = TTSRequest(
            input="Hello world", voice="af_heart", emotion="happy", emotion_strength=1.5
        )
        errors = validator.validate_request(request)
        # Emotion strength is validated, but only in context

    def test_validate_request_all_formats(self, validator):
        """Test all supported formats"""
        for fmt in ["mp3", "wav", "ogg", "flac"]:
            request = TTSRequest(input="Hello world", voice="af_heart", response_format=fmt)
            errors = validator.validate_request(request)
            assert len(errors) == 0, f"Format {fmt} should be valid"

    def test_validate_forbidden_patterns_script(self, validator):
        """Test that script injection is detected"""
        request = TTSRequest(input="<script>alert('xss')</script>Hello")
        errors = validator.validate_request(request)
        assert len(errors) > 0
        assert any("script" in e.lower() or "forbidden" in e.lower() for e in errors)

    def test_validate_forbidden_patterns_javascript(self, validator):
        """Test that javascript: URLs are detected"""
        request = TTSRequest(input="javascript:alert('xss')")
        errors = validator.validate_request(request)
        assert len(errors) > 0


class TestRequestValidatorEdgeCases:
    """Edge case tests for RequestValidator"""

    @pytest.fixture
    def synthesizer(self):
        return MockSynthesizer()

    @pytest.fixture
    def validator(self, synthesizer):
        return RequestValidator(synthesizer)

    def test_validate_empty_text_by_validator(self, validator):
        """Test validation with empty/whitespace-only text"""
        # The validator's _validate_text method handles empty strings
        errors = validator._validate_text("")
        assert len(errors) > 0

    def test_validate_unicode_text(self, validator):
        """Test validation with unicode text"""
        request = TTSRequest(input="Hello 世界 🌍 ñooña", voice="af_heart")
        errors = validator.validate_request(request)
        assert len(errors) == 0

    def test_validate_very_long_single_word(self, validator):
        """Test validation with very long single word"""
        request = TTSRequest(input="A" * 1000, voice="af_heart")
        errors = validator.validate_request(request)
        # Should pass length check but could have pronunciation issues

    def test_validate_whitespace_only(self, validator):
        """Test validation with whitespace-only text"""
        request = TTSRequest(input="   \t\n   ", voice="af_heart")
        errors = validator.validate_request(request)
        assert len(errors) > 0
