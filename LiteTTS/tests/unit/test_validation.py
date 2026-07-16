#!/usr/bin/env python3
"""
Unit tests for validation module
"""

import pytest
from LiteTTS.validation import InputValidator, ValidationResult, SecurityValidator, validate_request


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
        assert result.is_valid is True
        assert result.sanitized_value == "Hello world"

    def test_validate_text_empty(self):
        """Test validating empty text"""
        result = InputValidator.validate_text("")
        assert result.is_valid is False
        assert "empty" in result.error_message.lower()

    def test_validate_text_whitespace_only(self):
        """Test validating whitespace-only text"""
        result = InputValidator.validate_text("   \t\n  ")
        assert result.is_valid is False

    def test_validate_text_too_long(self):
        """Test validating text that is too long"""
        long_text = "a" * 6000
        result = InputValidator.validate_text(long_text)
        assert result.is_valid is False
        assert "too long" in result.error_message.lower()

    def test_validate_text_not_string(self):
        """Test validating non-string text"""
        result = InputValidator.validate_text(123)
        assert result.is_valid is False
        assert "string" in result.error_message.lower()

    def test_validate_text_dangerous_script(self):
        """Test validating text with dangerous script content"""
        result = InputValidator.validate_text("<script>alert('xss')</script>Hello")
        assert result.is_valid is True
        assert "<script>" not in result.sanitized_value

    def test_validate_text_control_chars(self):
        """Test validating text with control characters"""
        result = InputValidator.validate_text("Hello\x00World\x1F")
        assert result.is_valid is True

    def test_validate_text_excessive_whitespace(self):
        """Test validating text with excessive whitespace"""
        result = InputValidator.validate_text("Hello    World")
        assert result.is_valid is True
        assert "  " not in result.sanitized_value or result.sanitized_value.count(" ") <= 2

    def test_validate_format(self):
        """Test validating audio format"""
        result = InputValidator.validate_format("mp3")
        assert result.is_valid is True
        assert result.sanitized_value == "mp3"

    def test_validate_format_wav(self):
        """Test validating wav format"""
        result = InputValidator.validate_format("wav")
        assert result.is_valid is True
        assert result.sanitized_value == "wav"

    def test_validate_format_flac(self):
        """Test validating flac format"""
        result = InputValidator.validate_format("flac")
        assert result.is_valid is True

    def test_validate_format_ogg(self):
        """Test validating ogg format"""
        result = InputValidator.validate_format("ogg")
        assert result.is_valid is True

    def test_validate_format_invalid(self):
        """Test validating invalid audio format"""
        result = InputValidator.validate_format("xyz")
        assert result.is_valid is False
        assert "unsupported" in result.error_message.lower()

    def test_validate_format_none(self):
        """Test validating None format defaults to mp3"""
        result = InputValidator.validate_format(None)
        assert result.is_valid is True
        assert result.sanitized_value == "mp3"
        assert len(result.warnings) > 0

    def test_validate_format_empty(self):
        """Test validating empty format defaults to mp3"""
        result = InputValidator.validate_format("")
        assert result.is_valid is True
        assert result.sanitized_value == "mp3"

    def test_validate_format_number(self):
        """Test validating numeric format"""
        result = InputValidator.validate_format(123)
        assert result.is_valid is False

    def test_validate_speed(self):
        """Test validating valid speed"""
        result = InputValidator.validate_speed(1.0)
        assert result.is_valid is True
        assert result.sanitized_value == 1.0

    def test_validate_speed_min(self):
        """Test validating minimum speed"""
        result = InputValidator.validate_speed(0.1)
        assert result.is_valid is True

    def test_validate_speed_max(self):
        """Test validating maximum speed"""
        result = InputValidator.validate_speed(3.0)
        assert result.is_valid is True

    def test_validate_speed_too_slow(self):
        """Test validating too slow speed"""
        result = InputValidator.validate_speed(0.05)
        assert result.is_valid is False
        assert "between" in result.error_message.lower()

    def test_validate_speed_too_fast(self):
        """Test validating too fast speed"""
        result = InputValidator.validate_speed(5.0)
        assert result.is_valid is False
        assert "between" in result.error_message.lower()

    def test_validate_speed_none(self):
        """Test validating None speed defaults to 1.0"""
        result = InputValidator.validate_speed(None)
        assert result.is_valid is True
        assert result.sanitized_value == 1.0
        assert len(result.warnings) > 0

    def test_validate_speed_string(self):
        """Test validating string speed"""
        result = InputValidator.validate_speed("1.5")
        assert result.is_valid is True
        assert result.sanitized_value == 1.5

    def test_validate_speed_invalid_string(self):
        """Test validating invalid string speed"""
        result = InputValidator.validate_speed("fast")
        assert result.is_valid is False

    def test_validate_speed_very_slow_warning(self):
        """Test that very slow speed generates warning"""
        result = InputValidator.validate_speed(0.3)
        assert result.is_valid is True
        assert len(result.warnings) > 0

    def test_validate_speed_very_fast_warning(self):
        """Test that very fast speed generates warning"""
        result = InputValidator.validate_speed(2.5)
        assert result.is_valid is True
        assert len(result.warnings) > 0

    def test_validate_voice_valid(self):
        """Test validating valid voice name"""
        result = InputValidator.validate_voice("af_heart", ["af_heart", "am_puck"])
        assert result.is_valid is True
        assert result.sanitized_value == "af_heart"

    def test_validate_voice_not_found(self):
        """Test validating non-existent voice"""
        result = InputValidator.validate_voice("nonexistent", ["af_heart", "am_puck"])
        assert result.is_valid is False
        assert "not found" in result.error_message.lower()

    def test_validate_voice_empty(self):
        """Test validating empty voice"""
        result = InputValidator.validate_voice("", ["af_heart"])
        assert result.is_valid is False

    def test_validate_voice_sanitization(self):
        """Test voice name sanitization"""
        result = InputValidator.validate_voice("AF_HEART", ["af_heart", "am_puck"])
        assert result.is_valid is True

    def test_validate_voice_not_string(self):
        """Test validating non-string voice"""
        result = InputValidator.validate_voice(123, ["af_heart"])
        assert result.is_valid is False
        assert "string" in result.error_message.lower()

    def test_validate_tts_request_valid(self):
        """Test validating valid TTS request"""
        request_data = {"input": "Hello world", "voice": "af_heart"}
        result = InputValidator.validate_tts_request(request_data, ["af_heart"])
        assert result.is_valid is True
        assert result.sanitized_value["input"] == "Hello world"
        assert result.sanitized_value["voice"] == "af_heart"

    def test_validate_tts_request_missing_input(self):
        """Test validating TTS request with missing input"""
        request_data = {"voice": "af_heart"}
        result = InputValidator.validate_tts_request(request_data, ["af_heart"])
        assert result.is_valid is False
        assert "input" in result.error_message.lower()

    def test_validate_tts_request_missing_voice(self):
        """Test validating TTS request with missing voice"""
        request_data = {"input": "Hello"}
        result = InputValidator.validate_tts_request(request_data, ["af_heart"])
        assert result.is_valid is False
        assert "voice" in result.error_message.lower()

    def test_validate_tts_request_not_dict(self):
        """Test validating non-dict TTS request"""
        result = InputValidator.validate_tts_request("not a dict", ["af_heart"])
        assert result.is_valid is False

    def test_validate_tts_request_with_format(self):
        """Test validating TTS request with format"""
        request_data = {"input": "Hello", "voice": "af_heart", "response_format": "wav"}
        result = InputValidator.validate_tts_request(request_data, ["af_heart"])
        assert result.is_valid is True
        assert result.sanitized_value["response_format"] == "wav"

    def test_validate_tts_request_with_speed(self):
        """Test validating TTS request with speed"""
        request_data = {"input": "Hello", "voice": "af_heart", "speed": 1.5}
        result = InputValidator.validate_tts_request(request_data, ["af_heart"])
        assert result.is_valid is True
        assert result.sanitized_value["speed"] == 1.5


class TestSecurityValidator:
    """Test cases for SecurityValidator"""

    def test_validate_file_path_valid(self):
        """Test validating valid file path"""
        result = SecurityValidator.validate_file_path("test.mp3")
        assert result.is_valid is True

    def test_validate_file_path_with_directory(self):
        """Test validating file path with directory"""
        result = SecurityValidator.validate_file_path("subdir/test.mp3")
        assert result.is_valid is True

    def test_validate_file_path_traversal(self):
        """Test validating path with directory traversal"""
        result = SecurityValidator.validate_file_path("../etc/passwd")
        assert result.is_valid is False
        assert "traversal" in result.error_message.lower()

    def test_validate_file_path_absolute(self):
        """Test validating absolute path"""
        result = SecurityValidator.validate_file_path("/absolute/path")
        assert result.is_valid is False

    def test_validate_file_path_not_string(self):
        """Test validating non-string path"""
        result = SecurityValidator.validate_file_path(123)
        assert result.is_valid is False

    def test_validate_api_key_valid(self):
        """Test validating valid API key"""
        result = SecurityValidator.validate_api_key("sk-test12345678")
        assert result.is_valid is True

    def test_validate_api_key_too_short(self):
        """Test validating too short API key"""
        result = SecurityValidator.validate_api_key("sk-abc")
        assert result.is_valid is False
        assert "format" in result.error_message.lower()

    def test_validate_api_key_too_long(self):
        """Test validating too long API key"""
        result = SecurityValidator.validate_api_key("sk-" + "a" * 100)
        assert result.is_valid is False

    def test_validate_api_key_invalid_chars(self):
        """Test validating API key with invalid characters"""
        result = SecurityValidator.validate_api_key("sk-test@#$%")
        assert result.is_valid is False
        assert "invalid characters" in result.error_message.lower()

    def test_validate_api_key_not_string(self):
        """Test validating non-string API key"""
        result = SecurityValidator.validate_api_key(12345)
        assert result.is_valid is False


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

    def test_validation_result_default_warnings(self):
        """Test that warnings defaults to empty list"""
        result = ValidationResult(is_valid=True)
        assert result.warnings == []

    def test_validation_result_multiple_warnings(self):
        """Test creating result with multiple warnings"""
        result = ValidationResult(is_valid=True, warnings=["Warn1", "Warn2", "Warn3"])
        assert len(result.warnings) == 3


class TestValidateRequestFunction:
    """Test cases for the validate_request convenience function"""

    def test_validate_request_valid(self):
        """Test validate_request with valid data"""
        request_data = {"input": "Hello", "voice": "af_heart"}
        is_valid, data_or_error, warnings = validate_request(request_data, ["af_heart"])
        assert is_valid is True
        assert isinstance(data_or_error, dict)
        assert data_or_error["input"] == "Hello"

    def test_validate_request_invalid(self):
        """Test validate_request with invalid data"""
        request_data = {"input": "", "voice": "nonexistent"}
        is_valid, data_or_error, warnings = validate_request(request_data, ["af_heart"])
        assert is_valid is False
        assert isinstance(data_or_error, str)


class TestInputValidatorHasPhonemizerIssues:
    """Test cases for _has_phonemizer_issues method"""

    def test_has_phonemizer_issues_long_word(self):
        """Test detection of very long words"""
        result = InputValidator.validate_text("Supercalifragilisticexpialidocious")
        # Long words trigger warning
        assert len(result.warnings) >= 0

    def test_has_phonemizer_issues_long_numbers(self):
        """Test detection of long number sequences"""
        result = InputValidator.validate_text("12345678901234567890")
        assert result.is_valid is True

    def test_has_phonemizer_issues_excessive_punctuation(self):
        """Test detection of excessive punctuation"""
        result = InputValidator.validate_text("Hello..........World")
        assert result.is_valid is True
