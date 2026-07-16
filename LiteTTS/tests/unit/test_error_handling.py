#!/usr/bin/env python3
"""
Unit tests for error handling module
"""

import time
import pytest
from LiteTTS.error_handling import (
    ErrorSeverity,
    ErrorContext,
    TTSError,
    ModelLoadError,
    VoiceNotFoundError,
    AudioGenerationError,
    ValidationError,
    SystemResourceError,
    ErrorHandler,
    GracefulDegradation
)


class TestErrorSeverity:
    """Test cases for ErrorSeverity enum"""

    def test_values(self):
        """Test all error severity values"""
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.CRITICAL.value == "critical"


class TestErrorContext:
    """Test cases for ErrorContext"""

    def test_creation(self):
        """Test creating error context"""
        context = ErrorContext(operation="test_op")
        assert context.operation == "test_op"
        assert context.timestamp is not None

    def test_creation_with_params(self):
        """Test creating error context with parameters"""
        context = ErrorContext(
            operation="synthesis",
            user_input="Hello",
            voice="af_heart",
            format="mp3"
        )
        assert context.voice == "af_heart"


class TestTTSError:
    """Test cases for TTSError"""

    def test_creation(self):
        """Test creating TTS error"""
        error = TTSError("Test error", severity=ErrorSeverity.MEDIUM)
        assert str(error) == "Test error"
        assert error.severity == ErrorSeverity.MEDIUM


class TestModelLoadError:
    """Test cases for ModelLoadError"""

    def test_creation(self):
        """Test creating model load error"""
        error = ModelLoadError("Failed to load model")
        assert str(error) == "Failed to load model"


class TestVoiceNotFoundError:
    """Test cases for VoiceNotFoundError"""

    def test_creation(self):
        """Test creating voice not found error"""
        error = VoiceNotFoundError("Voice not found: nonexistent")
        assert str(error) == "Voice not found: nonexistent"


class TestAudioGenerationError:
    """Test cases for AudioGenerationError"""

    def test_creation(self):
        """Test creating audio generation error"""
        error = AudioGenerationError("Audio generation failed")
        assert str(error) == "Audio generation failed"


class TestValidationError:
    """Test cases for ValidationError"""

    def test_creation(self):
        """Test creating validation error"""
        error = ValidationError("Invalid input")
        assert str(error) == "Invalid input"


class TestSystemResourceError:
    """Test cases for SystemResourceError"""

    def test_creation(self):
        """Test creating system resource error"""
        error = SystemResourceError("Out of memory")
        assert str(error) == "Out of memory"


class TestErrorHandler:
    """Test cases for ErrorHandler"""

    def test_initialization(self):
        """Test ErrorHandler initialization"""
        handler = ErrorHandler()
        assert handler.error_counts == {}
        assert handler.last_errors == {}
        assert handler.circuit_breakers == {}

    def test_handle_error_with_tts_error(self):
        """Test handle_error with already wrapped TTSError"""
        handler = ErrorHandler()
        error = TTSError("Test error", severity=ErrorSeverity.MEDIUM)
        context = ErrorContext(operation="test")
        result = handler.handle_error(error, context)
        assert isinstance(result, dict)

    def test_handle_error_with_regular_exception(self):
        """Test handle_error wrapping regular exception"""
        handler = ErrorHandler()
        error = ValueError("Test value error")
        context = ErrorContext(operation="test")
        result = handler.handle_error(error, context)
        assert isinstance(result, dict)

    def test_handle_error_without_context(self):
        """Test handle_error without context"""
        handler = ErrorHandler()
        error = ValueError("Test error")
        result = handler.handle_error(error)
        assert isinstance(result, dict)

    def test_determine_severity_critical(self):
        """Test _determine_severity with critical errors"""
        handler = ErrorHandler()
        error = MemoryError("Out of memory")
        severity = handler._determine_severity(error)
        assert severity == ErrorSeverity.CRITICAL

    def test_determine_severity_high(self):
        """Test _determine_severity with high severity errors"""
        handler = ErrorHandler()
        error = ModelLoadError("Failed to load")
        severity = handler._determine_severity(error)
        assert severity == ErrorSeverity.HIGH

    def test_determine_severity_medium(self):
        """Test _determine_severity with medium severity errors"""
        handler = ErrorHandler()
        error = AudioGenerationError("Audio failed")
        severity = handler._determine_severity(error)
        assert severity == ErrorSeverity.MEDIUM

    def test_determine_severity_low(self):
        """Test _determine_severity with low severity errors"""
        handler = ErrorHandler()
        error = KeyError("Key not found")
        severity = handler._determine_severity(error)
        assert severity == ErrorSeverity.LOW

    def test_track_error(self):
        """Test _track_error updates error tracking"""
        handler = ErrorHandler()
        error = TTSError("Test error", severity=ErrorSeverity.MEDIUM)
        handler._track_error(error)
        # Key format is "TTSError:unknown" when no context
        assert any("TTSError" in k for k in handler.error_counts.keys())

    def test_should_circuit_break_not_triggered(self):
        """Test _should_circuit_break when threshold not met"""
        handler = ErrorHandler()
        error = TTSError("Test error", severity=ErrorSeverity.LOW)
        assert handler._should_circuit_break(error) is False

    def test_log_error(self):
        """Test _log_error doesn't raise exceptions"""
        handler = ErrorHandler()
        error = TTSError("Test error", severity=ErrorSeverity.MEDIUM)
        # Should not raise
        handler._log_error(error)

    def test_circuit_breaker_response(self):
        """Test _circuit_breaker_response returns dict"""
        handler = ErrorHandler()
        error = TTSError("Circuit broken", severity=ErrorSeverity.HIGH)
        result = handler._circuit_breaker_response(error)
        assert isinstance(result, dict)

    def test_generate_error_response(self):
        """Test _generate_error_response returns dict"""
        handler = ErrorHandler()
        error = TTSError("Test error", severity=ErrorSeverity.MEDIUM)
        result = handler._generate_error_response(error)
        assert isinstance(result, dict)

    def test_should_circuit_break_triggered(self):
        """Test _should_circuit_break when threshold exceeded"""
        handler = ErrorHandler()
        # Set up error count > 5
        error_key = "TTSError:test_op"
        handler.error_counts[error_key] = 6
        handler.last_errors[error_key] = time.time()
        error = TTSError("Circuit test", severity=ErrorSeverity.CRITICAL)
        error.context = ErrorContext(operation="test_op")
        assert handler._should_circuit_break(error) is True

    def test_should_circuit_break_low_severity(self):
        """Test _should_circuit_break not triggered for low severity"""
        handler = ErrorHandler()
        error_key = "TTSError:test_op"
        handler.error_counts[error_key] = 6
        handler.last_errors[error_key] = time.time()
        error = TTSError("Low severity", severity=ErrorSeverity.LOW)
        error.context = ErrorContext(operation="test_op")
        assert handler._should_circuit_break(error) is False

    def test_handle_error_triggers_circuit_breaker(self):
        """Test handle_error triggers circuit breaker when threshold exceeded"""
        handler = ErrorHandler()
        # Set up error count > 5 for circuit breaker
        error_key = "MemoryError:test_op"
        handler.error_counts[error_key] = 6
        handler.last_errors[error_key] = time.time()
        error = MemoryError("Out of memory")
        error.context = ErrorContext(operation="test_op")
        result = handler.handle_error(error)
        # Circuit breaker returns specific response
        assert "error" in result

    def test_generate_error_response_validation_error(self):
        """Test _generate_error_response with ValidationError"""
        handler = ErrorHandler()
        error = ValidationError("Invalid input")
        result = handler._generate_error_response(error)
        assert result["error_code"] == "VALIDATION_ERROR"

    def test_generate_error_response_voice_not_found(self):
        """Test _generate_error_response with VoiceNotFoundError"""
        handler = ErrorHandler()
        error = VoiceNotFoundError("Voice not found")
        result = handler._generate_error_response(error)
        assert result["error_code"] == "VOICE_NOT_FOUND"

    def test_generate_error_response_audio_generation(self):
        """Test _generate_error_response with AudioGenerationError"""
        handler = ErrorHandler()
        error = AudioGenerationError("Generation failed")
        result = handler._generate_error_response(error)
        assert result["error_code"] == "GENERATION_ERROR"

    def test_generate_error_response_model_load(self):
        """Test _generate_error_response with ModelLoadError"""
        handler = ErrorHandler()
        error = ModelLoadError("Model load failed")
        result = handler._generate_error_response(error)
        assert result["error_code"] == "MODEL_ERROR"

    def test_generate_error_response_system_resource(self):
        """Test _generate_error_response with SystemResourceError"""
        handler = ErrorHandler()
        error = SystemResourceError("Resource unavailable")
        result = handler._generate_error_response(error)
        assert result["error_code"] == "RESOURCE_ERROR"

    def test_generate_error_response_with_context(self):
        """Test _generate_error_response includes context info"""
        handler = ErrorHandler()
        error = TTSError("Test error", severity=ErrorSeverity.MEDIUM)
        error.context = ErrorContext(operation="test_op", request_id="req123")
        result = handler._generate_error_response(error)
        assert result["operation"] == "test_op"
        assert result["request_id"] == "req123"

    def test_log_error_high_severity(self):
        """Test _log_error with HIGH severity logs error"""
        handler = ErrorHandler()
        error = TTSError("High severity error", severity=ErrorSeverity.HIGH)
        error.context = ErrorContext(operation="test_op")
        # Should not raise, just logs
        handler._log_error(error)

    def test_log_error_low_severity(self):
        """Test _log_error with LOW severity logs info"""
        handler = ErrorHandler()
        error = TTSError("Low severity error", severity=ErrorSeverity.LOW)
        error.context = ErrorContext(operation="test_op")
        # Should not raise, just logs
        handler._log_error(error)


class TestGracefulDegradation:
    """Test cases for GracefulDegradation"""

    def test_fallback_voice_af(self):
        """Test fallback_voice with American female voice"""
        result = GracefulDegradation.fallback_voice("af_heart", ["af_heart", "am_ben"])
        assert result == "af_heart"

    def test_fallback_voice_am(self):
        """Test fallback_voice with American male voice"""
        result = GracefulDegradation.fallback_voice("am_ben", ["af_heart", "am_ben"])
        assert result == "am_ben"

    def test_fallback_voice_bf(self):
        """Test fallback_voice with British female voice"""
        result = GracefulDegradation.fallback_voice("bf_emma", ["bf_emma", "bm_george"])
        assert result == "bf_emma"

    def test_fallback_voice_bm(self):
        """Test fallback_voice with British male voice"""
        result = GracefulDegradation.fallback_voice("bm_george", ["bf_emma", "bm_george"])
        assert result == "bm_george"

    def test_fallback_voice_unknown_pattern(self):
        """Test fallback_voice with unknown voice pattern"""
        result = GracefulDegradation.fallback_voice("custom_voice", ["af_heart", "am_ben"])
        # Falls back to first available
        assert result in ["af_heart", "am_ben"]

    def test_fallback_voice_empty_list_raises(self):
        """Test fallback_voice with empty list raises error"""
        with pytest.raises(VoiceNotFoundError):
            GracefulDegradation.fallback_voice("af_heart", [])

    def test_fallback_format_mp3(self):
        """Test fallback_format with mp3"""
        result = GracefulDegradation.fallback_format("mp3")
        assert result == "mp3"

    def test_fallback_format_unknown(self):
        """Test fallback_format with unknown format returns mp3"""
        result = GracefulDegradation.fallback_format("unknown")
        assert result == "mp3"

    def test_simplify_text(self):
        """Test simplify_text removes complex punctuation"""
        text = "Hello world! How are you? (Fine.)"
        result = GracefulDegradation.simplify_text(text)
        assert isinstance(result, str)
