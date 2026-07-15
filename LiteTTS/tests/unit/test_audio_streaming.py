#!/usr/bin/env python3
"""
Unit tests for audio streaming
"""

import pytest
import numpy as np
from LiteTTS.audio.streaming import AudioStreamer, RealTimeStreamer


class TestAudioStreamer:
    """Test cases for AudioStreamer"""

    @pytest.fixture
    def streamer(self):
        """Create streamer instance"""
        return AudioStreamer(chunk_duration=1.0)

    def test_initialization(self, streamer):
        """Test streamer initializes correctly"""
        assert streamer is not None
        assert streamer.chunk_duration == 1.0

    def test_create_streaming_response_headers(self, streamer):
        """Test creating streaming response headers"""
        result = streamer.create_streaming_response_headers("mp3")
        assert isinstance(result, dict)

    def test_estimate_stream_size(self, streamer):
        """Test estimating stream size"""
        from LiteTTS.audio.audio_segment import AudioSegment
        audio_data = np.random.randn(24000).astype(np.float32)
        segment = AudioSegment(audio_data=audio_data, sample_rate=24000)
        result = streamer.estimate_stream_size(segment, "mp3")
        assert isinstance(result, int)


class TestRealTimeStreamer:
    """Test cases for RealTimeStreamer"""

    @pytest.fixture
    def rt_streamer(self):
        """Create real-time streamer instance"""
        return RealTimeStreamer(buffer_size=4096)

    def test_initialization(self, rt_streamer):
        """Test real-time streamer initializes correctly"""
        assert rt_streamer is not None
        assert rt_streamer.buffer_size == 4096

    def test_is_buffer_empty(self, rt_streamer):
        """Test checking if buffer is empty"""
        result = rt_streamer.is_buffer_empty()
        assert isinstance(result, bool)
