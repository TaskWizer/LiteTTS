#!/usr/bin/env python3
"""
Unit tests for voice validator
"""

import pytest
from pathlib import Path
from LiteTTS.voice.validator import VoiceValidator, ValidationResult


class TestVoiceValidator:
    """Test cases for VoiceValidator"""

    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return VoiceValidator()

    def test_initialization(self, validator):
        """Test validator initializes correctly"""
        assert validator is not None
        assert validator.expected_properties is not None

    def test_validate_nonexistent_voice(self, validator):
        """Test validating a voice that doesn't exist"""
        result = validator.validate_voice("nonexistent", Path("/tmp/nonexistent.bin"))
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.errors) > 0


class TestValidationResult:
    """Test cases for ValidationResult"""

    def test_validation_result_creation(self):
        """Test creating validation result"""
        result = ValidationResult(
            is_valid=False,
            voice_name="test_voice",
            file_path="/path/to/voice.bin",
            file_size=1024,
            errors=["File too small"],
            warnings=[],
            metadata={}
        )
        assert result.is_valid is False
        assert result.voice_name == "test_voice"
