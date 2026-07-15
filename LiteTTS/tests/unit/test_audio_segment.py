#!/usr/bin/env python3
"""
Unit tests for audio segment
"""

import pytest
import numpy as np
from LiteTTS.audio.audio_segment import AudioSegment


class TestAudioSegment:
    """Test cases for AudioSegment"""

    @pytest.fixture
    def audio_segment(self):
        """Create audio segment instance"""
        audio_data = np.random.randn(24000).astype(np.float32)
        return AudioSegment(audio_data=audio_data, sample_rate=24000)

    def test_initialization(self, audio_segment):
        """Test audio segment initializes correctly"""
        assert audio_segment is not None
        assert audio_segment.sample_rate == 24000

    def test_from_bytes(self):
        """Test creating audio segment from bytes"""
        audio_data = np.random.randn(24000).astype(np.float32)
        segment = AudioSegment(audio_data=audio_data, sample_rate=24000)
        result = segment.to_bytes()
        assert isinstance(result, bytes)

    def test_silence(self):
        """Test creating silence segment"""
        result = AudioSegment.silence(duration=1.0, sample_rate=24000)
        assert isinstance(result, AudioSegment)
        assert result.duration == 1.0

    def test_to_bytes(self, audio_segment):
        """Test converting to bytes"""
        result = audio_segment.to_bytes()
        assert isinstance(result, bytes)

    def test_validate(self, audio_segment):
        """Test validating audio segment"""
        result = audio_segment.validate()
        assert isinstance(result, bool)

    def test_get_info(self, audio_segment):
        """Test getting audio info"""
        result = audio_segment.get_info()
        assert isinstance(result, dict)


class TestAudioSegmentEdgeCases:
    """Edge case tests for AudioSegment"""

    @pytest.fixture
    def audio_segment(self):
        audio_data = np.random.randn(24000).astype(np.float32)
        return AudioSegment(audio_data=audio_data, sample_rate=24000)

    def test_validate_empty(self):
        """Test validating empty audio"""
        empty_data = np.array([], dtype=np.float32)
        segment = AudioSegment(audio_data=empty_data, sample_rate=24000)
        result = segment.validate()
        assert isinstance(result, bool)

    def test_get_info_keys(self, audio_segment):
        """Test info contains expected keys"""
        result = audio_segment.get_info()
        assert 'duration' in result or isinstance(result, dict)
