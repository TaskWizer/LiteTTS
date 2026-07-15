#!/usr/bin/env python3
"""
Unit tests for audio processor
"""

import pytest
import numpy as np
from LiteTTS.audio.processor import AudioProcessor


class TestAudioProcessor:
    """Test cases for AudioProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return AudioProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_get_supported_formats(self, processor):
        """Test getting supported formats"""
        formats = processor.get_supported_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0

    def test_get_format_info(self, processor):
        """Test getting format info"""
        formats = processor.get_supported_formats()
        if formats:
            info = processor.get_format_info(formats[0])
            assert isinstance(info, dict)

    def test_validate_audio(self, processor):
        """Test validating audio"""
        # Create mock audio segment
        audio_data = np.random.randn(24000).astype(np.float32)
        class MockSegment:
            def __init__(self):
                self.audio_data = audio_data
                self.sample_rate = 24000
                self.duration = 1.0
        result = processor.validate_audio(MockSegment())
        assert isinstance(result, dict)

    def test_estimate_processing_time(self, processor):
        """Test estimating processing time"""
        result = processor.estimate_processing_time(10.0, "mp3")
        assert isinstance(result, float)
        assert result >= 0


class TestAudioProcessorEdgeCases:
    """Edge case tests for AudioProcessor"""

    @pytest.fixture
    def processor(self):
        return AudioProcessor()

    def test_get_format_info_invalid(self, processor):
        """Test getting info for invalid format returns Unknown"""
        info = processor.get_format_info("invalid_format_xyz")
        assert "name" in info
        assert info["name"] == "Unknown"

    def test_validate_audio_empty(self, processor):
        """Test validating empty audio"""
        class EmptySegment:
            def __init__(self):
                self.audio_data = np.array([], dtype=np.float32)
                self.sample_rate = 24000
                self.duration = 0.0
        result = processor.validate_audio(EmptySegment())
        assert isinstance(result, dict)

    def test_estimate_processing_time_zero_duration(self, processor):
        """Test estimating time for zero duration"""
        result = processor.estimate_processing_time(0.0, "mp3")
        assert result == 0.0
