#!/usr/bin/env python3
"""
Unit tests for format converter
"""

import pytest

from LiteTTS.audio.format_converter import AudioFormatConverter


class TestFormatConverter:
    """Test cases for AudioFormatConverter"""

    @pytest.fixture
    def converter(self):
        """Create converter instance"""
        return AudioFormatConverter()

    def test_initialization(self, converter):
        """Test converter initializes correctly"""
        assert converter is not None

    def test_is_format_supported(self, converter):
        """Test checking format support"""
        result = converter.is_format_supported("mp3")
        assert isinstance(result, bool)

    def test_get_content_type(self, converter):
        """Test getting content type"""
        result = converter.get_content_type("mp3")
        assert isinstance(result, str)

    def test_get_file_extension(self, converter):
        """Test getting file extension"""
        result = converter.get_file_extension("mp3")
        assert isinstance(result, str)

    def test_get_format_info(self, converter):
        """Test getting format info"""
        result = converter.get_format_info("mp3")
        assert isinstance(result, dict)


class TestFormatConverterEdgeCases:
    """Edge case tests for AudioFormatConverter"""

    @pytest.fixture
    def converter(self):
        return AudioFormatConverter()

    def test_is_format_supported_invalid(self, converter):
        """Test with invalid format"""
        result = converter.is_format_supported("invalid_format_xyz")
        assert result is False

    def test_get_content_type_invalid(self, converter):
        """Test with invalid format"""
        result = converter.get_content_type("invalid")
        assert isinstance(result, str)

    def test_get_format_info_invalid(self, converter):
        """Test getting format info for invalid"""
        result = converter.get_format_info("invalid_format_xyz")
        assert isinstance(result, dict)
