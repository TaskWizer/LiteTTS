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
    ErrorHandler
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
