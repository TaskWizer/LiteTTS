#!/usr/bin/env python3
"""
Unit tests for validation module
"""

import pytest
from LiteTTS.validation import InputValidator, ValidationResult, SecurityValidator


class TestInputValidator:
    """Test cases for InputValidator"""

    def test_initialization(self):
        """Test validator initializes correctly"""
        validator = InputValidator()
        assert validator is not None

    def test_validate_text_valid(self):
        """Test validating valid text"""
        result = InputValidator.validate_text("Hello world")
        assert isinstance(result, ValidationResult)
        assert result.is_valid is not None

    def test_validate_text_empty(self):
        """Test validating empty text"""
        result = InputValidator.validate_text("")
        assert isinstance(result, ValidationResult)

    def test_validate_text_too_long(self):
        """Test validating text that is too long"""
        long_text = "a" * 6000
        result = InputValidator.validate_text(long_text)
        assert isinstance(result, ValidationResult)

    def test_validate_format(self):
        """Test validating audio format"""
        result = InputValidator.validate_format("mp3")
        assert isinstance(result, ValidationResult)

    def test_validate_format_invalid(self):
        """Test validating invalid audio format"""
        result = InputValidator.validate_format("xyz")
        assert isinstance(result, ValidationResult)

    def test_validate_speed(self):
        """Test validating speed"""
        result = InputValidator.validate_speed(1.0)
        assert isinstance(result, ValidationResult)

    def test_validate_speed_invalid(self):
        """Test validating invalid speed"""
        result = InputValidator.validate_speed(10.0)
        assert isinstance(result, ValidationResult)

    def test_validate_voice(self):
        """Test validating voice name"""
        result = InputValidator.validate_voice("af_heart", ["af_heart", "am_puck"])
        assert isinstance(result, ValidationResult)

    def test_validate_tts_request(self):
        """Test validating TTS request"""
        request_data = {"text": "Hello", "voice": "af_heart"}
        result = InputValidator.validate_tts_request(request_data, ["af_heart"])
        assert isinstance(result, ValidationResult)

    def test_validate_file_path(self):
        """Test validating file path"""
        result = SecurityValidator.validate_file_path("/tmp/test.mp3")
        assert isinstance(result, ValidationResult)

    def test_validate_api_key(self):
        """Test validating API key"""
        result = SecurityValidator.validate_api_key("sk-test123")
        assert isinstance(result, ValidationResult)


class TestValidationResult:
    """Test cases for ValidationResult"""

    def test_validation_result_creation(self):
        """Test creating validation result"""
        result = ValidationResult(is_valid=True, sanitized_value="test")
        assert result.is_valid is True
        assert result.sanitized_value == "test"

    def test_validation_result_with_error(self):
        """Test creating validation result with error"""
        result = ValidationResult(is_valid=False, error_message="Error occurred")
        assert result.is_valid is False
        assert result.error_message == "Error occurred"

    def test_validation_result_with_warnings(self):
        """Test creating validation result with warnings"""
        result = ValidationResult(is_valid=True, warnings=["Warning 1"])
        assert len(result.warnings) == 1
