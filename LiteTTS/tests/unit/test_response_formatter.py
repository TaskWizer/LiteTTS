#!/usr/bin/env python3
"""
Unit tests for API response formatter
"""

import pytest
from unittest.mock import MagicMock
from LiteTTS.api.response_formatter import ResponseFormatter


class MockAudioSegment:
    """Mock audio segment for testing"""
    def __init__(self):
        self.audio_data = b"mock_audio_data"
        self.duration = 1.5
        self.sample_rate = 24000


class TestResponseFormatter:
    """Test cases for ResponseFormatter"""

    @pytest.fixture
    def formatter(self):
        """Create response formatter instance"""
        return ResponseFormatter()

    def test_initialization(self, formatter):
        """Test formatter initializes correctly"""
        assert formatter is not None

    def test_format_audio_response_mp3(self, formatter):
        """Test formatting MP3 response"""
        audio = MockAudioSegment()
        result = formatter.format_audio_response(
            audio, "mp3", 0.5, False
        )
        assert result is not None

    def test_format_audio_response_wav(self, formatter):
        """Test formatting WAV response"""
        audio = MockAudioSegment()
        result = formatter.format_audio_response(
            audio, "wav", 0.5, False
        )
        assert result is not None

    def test_format_audio_response_ogg(self, formatter):
        """Test formatting OGG response"""
        audio = MockAudioSegment()
        result = formatter.format_audio_response(
            audio, "ogg", 0.5, False
        )
        assert result is not None

    def test_format_audio_response_flac(self, formatter):
        """Test formatting FLAC response"""
        audio = MockAudioSegment()
        result = formatter.format_audio_response(
            audio, "flac", 0.5, False
        )
        assert result is not None

    def test_format_audio_response_streaming(self, formatter):
        """Test formatting streaming response"""
        audio = MockAudioSegment()
        result = formatter.format_audio_response(
            audio, "mp3", 0.5, True
        )
        assert result is not None


class TestResponseFormatterEdgeCases:
    """Edge case tests for ResponseFormatter"""

    @pytest.fixture
    def formatter(self):
        return ResponseFormatter()

    def test_format_with_zero_processing_time(self, formatter):
        """Test formatting with zero processing time"""
        audio = MockAudioSegment()
        result = formatter.format_audio_response(
            audio, "mp3", 0.0, False
        )
        assert result is not None

    def test_format_with_none_duration(self, formatter):
        """Test formatting with None duration"""
        audio = MockAudioSegment()
        audio.duration = None
        result = formatter.format_audio_response(
            audio, "mp3", 0.5, False
        )
        assert result is not None

    def test_format_with_empty_audio_data(self, formatter):
        """Test formatting with empty audio data"""
        audio = MockAudioSegment()
        audio.audio_data = b""
        result = formatter.format_audio_response(
            audio, "mp3", 0.5, False
        )
        assert result is not None
