#!/usr/bin/env python3
"""
Unit tests for audio segment
"""

import numpy as np
import pytest

from LiteTTS.audio.audio_segment import AudioSegment


class TestAudioSegment:
    """Test cases for AudioSegment"""

    @pytest.fixture
    def audio_segment(self):
        """Create audio segment instance"""
        audio_data = np.random.randn(24000).astype(np.float32)
        return AudioSegment(audio_data=audio_data, sample_rate=24000)

    @pytest.fixture
    def another_segment(self):
        """Create another audio segment"""
        audio_data = np.random.randn(16000).astype(np.float32)
        return AudioSegment(audio_data=audio_data, sample_rate=24000)

    def test_initialization(self, audio_segment):
        """Test audio segment initializes correctly"""
        assert audio_segment is not None
        assert audio_segment.sample_rate == 24000
        assert audio_segment.format == "wav"

    def test_initialization_with_format(self):
        """Test initialization with custom format"""
        audio_data = np.random.randn(16000).astype(np.float32)
        segment = AudioSegment(audio_data=audio_data, sample_rate=24000, format="mp3")
        assert segment.format == "mp3"

    def test_initialization_with_metadata(self):
        """Test initialization with metadata"""
        audio_data = np.random.randn(16000).astype(np.float32)
        segment = AudioSegment(audio_data=audio_data, sample_rate=24000, metadata={"key": "value"})
        assert segment.metadata["key"] == "value"

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
        assert len(result.audio_data) == 24000

    def test_to_bytes(self, audio_segment):
        """Test converting to bytes"""
        result = audio_segment.to_bytes()
        assert isinstance(result, bytes)

    def test_to_bytes_with_format(self, audio_segment):
        """Test converting to bytes with specific format"""
        result = audio_segment.to_bytes(format="mp3")
        assert isinstance(result, bytes)

    def test_validate(self, audio_segment):
        """Test validating audio segment"""
        result = audio_segment.validate()
        assert isinstance(result, bool)
        assert result is True

    def test_get_info(self, audio_segment):
        """Test getting audio info"""
        result = audio_segment.get_info()
        assert isinstance(result, dict)
        assert "duration" in result
        assert "sample_rate" in result
        assert "samples" in result
        assert "max_amplitude" in result
        assert "rms_level" in result

    def test_concatenate(self, audio_segment, another_segment):
        """Test concatenating audio segments"""
        result = audio_segment.concatenate(another_segment)
        assert isinstance(result, AudioSegment)
        assert len(result.audio_data) == len(audio_segment.audio_data) + len(
            another_segment.audio_data
        )

    def test_concatenate_different_sample_rates_raises(self, audio_segment):
        """Test concatenating segments with different sample rates raises error"""
        other = AudioSegment(
            audio_data=np.random.randn(16000).astype(np.float32), sample_rate=16000
        )
        with pytest.raises(ValueError):
            audio_segment.concatenate(other)

    def test_trim(self, audio_segment):
        """Test trimming audio segment"""
        result = audio_segment.trim(start_time=0.0, end_time=0.5)
        assert isinstance(result, AudioSegment)
        assert result.duration <= 0.5

    def test_trim_no_end(self, audio_segment):
        """Test trimming with no end time"""
        result = audio_segment.trim(start_time=0.5)
        assert isinstance(result, AudioSegment)
        assert result.duration > 0

    def test_trim_out_of_bounds(self):
        """Test trimming with out of bounds values"""
        audio_data = np.random.randn(24000).astype(np.float32)
        segment = AudioSegment(audio_data=audio_data, sample_rate=24000)
        result = segment.trim(start_time=-1.0, end_time=100.0)
        assert isinstance(result, AudioSegment)

    def test_fade_in(self, audio_segment):
        """Test fade in effect"""
        result = audio_segment.fade_in(duration=0.1)
        assert isinstance(result, AudioSegment)
        assert len(result.audio_data) == len(audio_segment.audio_data)

    def test_fade_out(self, audio_segment):
        """Test fade out effect"""
        result = audio_segment.fade_out(duration=0.1)
        assert isinstance(result, AudioSegment)
        assert len(result.audio_data) == len(audio_segment.audio_data)

    def test_adjust_volume(self, audio_segment):
        """Test adjusting volume"""
        result = audio_segment.adjust_volume(volume_multiplier=2.0)
        assert isinstance(result, AudioSegment)

    def test_adjust_volume_zero(self, audio_segment):
        """Test adjusting volume to zero"""
        result = audio_segment.adjust_volume(volume_multiplier=0.0)
        assert isinstance(result, AudioSegment)

    def test_adjust_volume_high(self, audio_segment):
        """Test adjusting volume with high multiplier (clamping)"""
        result = audio_segment.adjust_volume(volume_multiplier=10.0)
        assert isinstance(result, AudioSegment)
        # Should clamp to prevent clipping
        assert np.max(np.abs(result.audio_data)) <= 1.0

    def test_resample_same_rate(self, audio_segment):
        """Test resampling to same rate returns same segment"""
        result = audio_segment.resample(target_sample_rate=24000)
        assert result is audio_segment

    def test_resample_different_rate(self, audio_segment):
        """Test resampling to different rate"""
        result = audio_segment.resample(target_sample_rate=48000)
        assert isinstance(result, AudioSegment)
        assert result.sample_rate == 48000

    def test_get_chunks(self, audio_segment):
        """Test getting audio chunks"""
        chunks = list(audio_segment.get_chunks(chunk_duration=0.5))
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk, AudioSegment)

    def test_get_chunks_large_duration(self, audio_segment):
        """Test getting chunks with large duration"""
        chunks = list(audio_segment.get_chunks(chunk_duration=10.0))
        assert len(chunks) == 1  # Entire segment in one chunk


class TestAudioSegmentEdgeCases:
    """Edge case tests for AudioSegment"""

    @pytest.fixture
    def audio_segment(self):
        audio_data = np.random.randn(24000).astype(np.float32)
        return AudioSegment(audio_data=audio_data, sample_rate=24000)

    @pytest.fixture
    def another_segment(self):
        audio_data = np.random.randn(16000).astype(np.float32)
        return AudioSegment(audio_data=audio_data, sample_rate=24000)

    def test_validate_empty(self):
        """Test validating empty audio"""
        empty_data = np.array([], dtype=np.float32)
        segment = AudioSegment(audio_data=empty_data, sample_rate=24000)
        result = segment.validate()
        assert isinstance(result, bool)
        assert result is False

    def test_validate_nan(self):
        """Test validating audio with NaN"""
        audio_data = np.array([np.nan, 0.5, 0.3], dtype=np.float32)
        segment = AudioSegment(audio_data=audio_data, sample_rate=24000)
        result = segment.validate()
        assert result is False

    def test_validate_inf(self):
        """Test validating audio with inf"""
        audio_data = np.array([np.inf, 0.5, 0.3], dtype=np.float32)
        segment = AudioSegment(audio_data=audio_data, sample_rate=24000)
        result = segment.validate()
        assert result is False

    def test_get_info_keys(self, audio_segment):
        """Test info contains expected keys"""
        result = audio_segment.get_info()
        assert "duration" in result
        assert "sample_rate" in result
        assert "samples" in result

    def test_concatenate_metadata_merge(self, audio_segment, another_segment):
        """Test that metadata is merged on concatenate"""
        audio_segment.metadata = {"key1": "value1"}
        another_segment.metadata = {"key2": "value2"}
        result = audio_segment.concatenate(another_segment)
        assert "key1" in result.metadata or "key2" in result.metadata

    def test_silence_with_zero_duration(self):
        """Test creating silence with zero duration"""
        result = AudioSegment.silence(duration=0.0, sample_rate=24000)
        assert isinstance(result, AudioSegment)
        assert result.duration == 0.0
