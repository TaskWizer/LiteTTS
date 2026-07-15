#!/usr/bin/env python3
"""
Unit tests for error handling module
"""

import pytest
from LiteTTS.error_handling import (
    ErrorSeverity,
    ErrorContext,
    TTSError,
    ModelLoadError,
    VoiceNotFoundError,
    AudioGenerationError,
    ValidationError,
    SystemResourceError
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
