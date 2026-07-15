#!/usr/bin/env python3
"""
Unit tests for audio processor
"""

import pytest
import numpy as np
from LiteTTS.audio.processor import AudioProcessor
from LiteTTS.audio.audio_segment import AudioSegment


class TestAudioProcessor:
    """Test cases for AudioProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return AudioProcessor()

    @pytest.fixture
    def sample_segment(self):
        """Create a sample audio segment"""
        audio_data = np.random.randn(24000).astype(np.float32)
        return AudioSegment(audio_data=audio_data, sample_rate=24000, format="wav")

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

    def test_validate_audio(self, processor, sample_segment):
        """Test validating audio"""
        result = processor.validate_audio(sample_segment)
        assert isinstance(result, dict)
        assert "is_valid" in result

    def test_estimate_processing_time(self, processor):
        """Test estimating processing time"""
        result = processor.estimate_processing_time(10.0, "mp3")
        assert isinstance(result, float)
        assert result >= 0

    def test_create_audio_segment(self, processor):
        """Test creating audio segment"""
        audio_data = np.random.randn(16000).astype(np.float32)
        segment = processor.create_audio_segment(audio_data, 16000, "wav")
        assert segment is not None
        assert isinstance(segment, AudioSegment)
        assert len(segment.audio_data) == len(audio_data)

    def test_concatenate_segments_empty_raises(self, processor):
        """Test concatenating empty list raises error"""
        with pytest.raises(ValueError):
            processor.concatenate_segments([])

    def test_concatenate_segments_single(self, processor, sample_segment):
        """Test concatenating single segment returns same"""
        result = processor.concatenate_segments([sample_segment])
        assert result is sample_segment

    def test_concatenate_segments_multiple(self, processor):
        """Test concatenating multiple segments"""
        seg1 = AudioSegment(audio_data=np.random.randn(8000).astype(np.float32), sample_rate=16000, format="wav")
        seg2 = AudioSegment(audio_data=np.random.randn(8000).astype(np.float32), sample_rate=16000, format="wav")
        result = processor.concatenate_segments([seg1, seg2])
        assert len(result.audio_data) == len(seg1.audio_data) + len(seg2.audio_data)

    def test_apply_crossfade_empty_raises(self, processor):
        """Test crossfade with empty list raises error"""
        with pytest.raises(ValueError):
            processor.apply_crossfade([])

    def test_apply_crossfade_single(self, processor, sample_segment):
        """Test crossfade with single segment returns same"""
        result = processor.apply_crossfade([sample_segment])
        assert result is sample_segment

    def test_apply_crossfade_multiple(self, processor):
        """Test crossfade with multiple segments"""
        seg1 = AudioSegment(audio_data=np.random.randn(8000).astype(np.float32), sample_rate=16000, format="wav")
        seg2 = AudioSegment(audio_data=np.random.randn(8000).astype(np.float32), sample_rate=16000, format="wav")
        result = processor.apply_crossfade([seg1, seg2])
        assert result is not None

    def test_process_for_streaming(self, processor, sample_segment):
        """Test processing for streaming"""
        chunks = list(processor.process_for_streaming(sample_segment, "wav"))
        assert isinstance(chunks, list)

    def test_convert_format(self, processor, sample_segment):
        """Test format conversion"""
        result = processor.convert_format(sample_segment, "mp3")
        assert isinstance(result, bytes)

    def test_optimize_for_streaming(self, processor, sample_segment):
        """Test optimizing for streaming"""
        result = processor.optimize_for_streaming(sample_segment)
        assert isinstance(result, AudioSegment)


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
        empty_segment = AudioSegment(audio_data=np.array([], dtype=np.float32), sample_rate=24000, format="wav")
        result = processor.validate_audio(empty_segment)
        assert isinstance(result, dict)
        assert result["is_valid"] is False

    def test_validate_audio_none_data(self, processor):
        """Test validating audio with None data"""
        class NoneSegment:
            audio_data = None
            sample_rate = 24000
            duration = 0.0
        result = processor.validate_audio(NoneSegment())
        assert isinstance(result, dict)
        assert result["is_valid"] is False

    def test_validate_audio_nan_values(self, processor):
        """Test validating audio with NaN values"""
        audio_data = np.array([np.nan, 0.5, 0.3], dtype=np.float32)
        segment = AudioSegment(audio_data=audio_data, sample_rate=24000, format="wav")
        result = processor.validate_audio(segment)
        assert isinstance(result, dict)
        assert any("NaN" in err for err in result["errors"])

    def test_validate_audio_inf_values(self, processor):
        """Test validating audio with infinite values"""
        audio_data = np.array([np.inf, 0.5, 0.3], dtype=np.float32)
        segment = AudioSegment(audio_data=audio_data, sample_rate=24000, format="wav")
        result = processor.validate_audio(segment)
        assert isinstance(result, dict)
        assert any("infinite" in err.lower() for err in result["errors"])

    def test_validate_audio_high_amplitude(self, processor):
        """Test validating audio with high amplitude"""
        audio_data = np.array([2.0, 1.5, 1.2], dtype=np.float32)
        segment = AudioSegment(audio_data=audio_data, sample_rate=24000, format="wav")
        result = processor.validate_audio(segment)
        assert isinstance(result, dict)
        assert any("amplitude" in warn.lower() for warn in result["warnings"])

    def test_validate_audio_low_amplitude(self, processor):
        """Test validating audio with low amplitude"""
        audio_data = np.array([0.0001, 0.0002, 0.0001], dtype=np.float32)
        segment = AudioSegment(audio_data=audio_data, sample_rate=24000, format="wav")
        result = processor.validate_audio(segment)
        assert isinstance(result, dict)
        assert any("low" in warn.lower() for warn in result["warnings"])

    def test_validate_audio_invalid_sample_rate(self, processor):
        """Test validating audio with invalid sample rate"""
        # Create a custom segment class to avoid the post_init check
        audio_data = np.random.randn(24000).astype(np.float32)
        class InvalidSegment:
            def __init__(self):
                self.audio_data = audio_data
                self.sample_rate = 0
                self.duration = 1.0
        result = processor.validate_audio(InvalidSegment())
        assert isinstance(result, dict)
        assert result["is_valid"] is False

    def test_estimate_processing_time_zero_duration(self, processor):
        """Test estimating time for zero duration"""
        result = processor.estimate_processing_time(0.0, "mp3")
        assert result == 0.0

    def test_estimate_processing_time_unknown_format(self, processor):
        """Test estimating time for unknown format"""
        result = processor.estimate_processing_time(10.0, "unknown")
        assert isinstance(result, float)
        assert result >= 0
