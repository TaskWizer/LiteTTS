#!/usr/bin/env python3
"""
Unit tests for voice validator module
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
from LiteTTS.voice.validator import (
    ValidationResult,
    VoiceValidator
)


class TestValidationResult:
    """Test cases for ValidationResult dataclass"""

    def test_creation(self):
        """Test creating a validation result"""
        result = ValidationResult(
            is_valid=True,
            voice_name="test_voice",
            file_path="/path/to/voice.bin",
            file_size=1024,
            errors=[],
            warnings=[],
            metadata={"embedding_dim": 256}
        )
        assert result.is_valid is True
        assert result.voice_name == "test_voice"
        assert result.file_path == "/path/to/voice.bin"
        assert result.file_size == 1024
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata["embedding_dim"] == 256

    def test_creation_with_errors(self):
        """Test creating validation result with errors"""
        result = ValidationResult(
            is_valid=False,
            voice_name="bad_voice",
            file_path="/path/to/bad.bin",
            file_size=100,
            errors=["File too small"],
            warnings=["Unusual format"],
            metadata={}
        )
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "File too small" in result.errors


class TestVoiceValidator:
    """Test cases for VoiceValidator class"""

    def test_initialization(self):
        """Test validator initializes correctly"""
        validator = VoiceValidator()
        assert validator.expected_properties is not None
        assert validator.expected_properties['embedding_dim'] == 256
        assert validator.expected_properties['min_file_size'] == 1024 * 1024

    def test_validate_voice_file_not_found(self, tmp_path):
        """Test validating non-existent voice file"""
        validator = VoiceValidator()
        result = validator.validate_voice("nonexistent", tmp_path / "nonexistent.bin")
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "does not exist" in result.errors[0]

    def test_validate_voice_bin_file_too_small(self, tmp_path):
        """Test validating .bin file that is too small"""
        validator = VoiceValidator()
        voice_file = tmp_path / "tiny.bin"
        voice_file.write_bytes(b'\x00' * 50)  # 50 bytes is too small even for .bin

        result = validator.validate_voice("tiny", voice_file)
        assert result.is_valid is False
        assert any("too small" in err for err in result.errors)

    def test_validate_voice_bin_file_valid(self, tmp_path):
        """Test validating valid .bin file"""
        validator = VoiceValidator()
        voice_file = tmp_path / "valid.bin"
        # Create valid .bin file: 510 * 256 = 130560 float32 values
        voice_data = np.random.randn(510 * 256).astype(np.float32)
        voice_data.tofile(str(voice_file))

        result = validator.validate_voice("valid", voice_file)
        assert result.is_valid is True
        assert result.file_size > 0
        assert result.metadata.get('loaded_successfully') is True
        assert result.metadata.get('embedding_dim') == 256

    def test_validate_voice_bin_file_unusual_size(self, tmp_path):
        """Test validating .bin file with unusual (but valid) size"""
        validator = VoiceValidator()
        voice_file = tmp_path / "unusual.bin"
        # Size not divisible by 256 - should be unusual but still valid
        voice_data = np.random.randn(1000).astype(np.float32)  # 1000 not divisible by 256
        voice_data.tofile(str(voice_file))

        result = validator.validate_voice("unusual", voice_file)
        assert result.warnings
        assert any("Unexpected" in w for w in result.warnings)

    def test_validate_all_voices(self, tmp_path):
        """Test validating all voices in directory"""
        validator = VoiceValidator()
        # Create some voice files
        voice_data = np.random.randn(510 * 256).astype(np.float32)
        (tmp_path / "voice1.bin").write_bytes(voice_data.tobytes())
        (tmp_path / "voice2.bin").write_bytes(voice_data.tobytes())

        results = validator.validate_all_voices(tmp_path)
        # Both .bin files should be validated
        assert len(results) == 2
        assert "voice1" in results
        assert "voice2" in results

    def test_get_validation_summary_empty(self):
        """Test getting validation summary with no results"""
        validator = VoiceValidator()
        summary = validator.get_validation_summary({})
        assert summary['total_voices'] == 0
        assert summary['valid_voices'] == 0
        assert summary['invalid_voices'] == 0
        assert summary['validation_rate'] == 0

    def test_get_validation_summary_mixed(self):
        """Test getting validation summary with mixed results"""
        validator = VoiceValidator()
        results = {
            "voice1": ValidationResult(True, "voice1", "/v1.bin", 1024, [], [], {}),
            "voice2": ValidationResult(False, "voice2", "/v2.bin", 100, ["Error"], [], {}),
        }
        summary = validator.get_validation_summary(results)
        assert summary['total_voices'] == 2
        assert summary['valid_voices'] == 1
        assert summary['invalid_voices'] == 1
        assert summary['total_errors'] == 1

    def test_get_validation_summary_all_valid(self):
        """Test getting validation summary with all valid results"""
        validator = VoiceValidator()
        results = {
            "voice1": ValidationResult(True, "voice1", "/v1.bin", 1024, [], [], {}),
            "voice2": ValidationResult(True, "voice2", "/v2.bin", 1024, [], [], {}),
        }
        summary = validator.get_validation_summary(results)
        assert summary['validation_rate'] == 1.0
        assert summary['total_errors'] == 0
        assert summary['total_warnings'] == 0
