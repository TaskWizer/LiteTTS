#!/usr/bin/env python3
"""
Unit tests for audio streaming
"""


import numpy as np
import pytest

from LiteTTS.audio.streaming import AudioStreamer, RealTimeStreamer, StreamChunk


class TestAudioStreamer:
    """Test cases for AudioStreamer"""

    @pytest.fixture
    def streamer(self):
        """Create streamer instance"""
        return AudioStreamer(chunk_duration=1.0)

    @pytest.fixture
    def audio_segment(self):
        """Create sample audio segment"""
        from LiteTTS.audio.audio_segment import AudioSegment
        audio_data = np.random.randn(24000).astype(np.float32)
        return AudioSegment(audio_data=audio_data, sample_rate=24000)

    def test_initialization(self, streamer):
        """Test streamer initializes correctly"""
        assert streamer is not None
        assert streamer.chunk_duration == 1.0

    def test_initialization_default(self):
        """Test streamer with default chunk duration"""
        streamer = AudioStreamer()
        assert streamer.chunk_duration == 1.0  # default

    def test_create_streaming_response_headers(self, streamer):
        """Test creating streaming response headers"""
        result = streamer.create_streaming_response_headers("mp3")
        assert isinstance(result, dict)
        assert "Content-Type" in result

    def test_create_streaming_response_headers_wav(self, streamer):
        """Test creating streaming response headers for wav"""
        result = streamer.create_streaming_response_headers("wav")
        assert isinstance(result, dict)

    def test_estimate_stream_size(self, streamer, audio_segment):
        """Test estimating stream size"""
        result = streamer.estimate_stream_size(audio_segment, "mp3")
        assert isinstance(result, int)
        assert result >= 0

    def test_estimate_stream_size_zero(self, streamer):
        """Test estimating stream size for empty segment"""
        from LiteTTS.audio.audio_segment import AudioSegment
        empty_segment = AudioSegment(audio_data=np.array([], dtype=np.float32), sample_rate=24000)
        result = streamer.estimate_stream_size(empty_segment, "mp3")
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

    def test_initialization_default(self):
        """Test real-time streamer with defaults"""
        streamer = RealTimeStreamer()
        assert streamer.buffer_size == 4096  # default

    def test_is_buffer_empty(self, rt_streamer):
        """Test checking if buffer is empty"""
        result = rt_streamer.is_buffer_empty()
        assert isinstance(result, bool)
        assert result is True

    def test_flush_buffer(self, rt_streamer):
        """Test flushing buffer"""
        rt_streamer.flush_buffer()
        assert rt_streamer.is_buffer_empty() is True


class TestStreamChunk:
    """Test cases for StreamChunk dataclass"""

    def test_creation(self):
        """Test creating stream chunk"""
        chunk = StreamChunk(
            data=b'\x00\x01\x02\x03',
            chunk_index=0,
            total_chunks=10,
            is_final=False
        )
        assert chunk.data == b'\x00\x01\x02\x03'
        assert chunk.chunk_index == 0
        assert chunk.total_chunks == 10
        assert chunk.is_final is False

    def test_creation_defaults(self):
        """Test stream chunk with defaults"""
        chunk = StreamChunk(data=b'test', chunk_index=0, total_chunks=1)
        assert chunk.is_final is False
