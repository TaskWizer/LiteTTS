#!/usr/bin/env python3
"""
Unit tests for optimized audio processor
"""

import pytest
import numpy as np
from LiteTTS.audio.optimized_processor import OptimizedAudioProcessor


class TestOptimizedAudioProcessor:
    """Test cases for OptimizedAudioProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return OptimizedAudioProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None
        assert processor.audio_cache is not None

    def test_process_audio_optimized(self, processor):
        """Test processing audio with optimizations"""
        audio_data = np.random.randn(24000).astype(np.float32)
        result = processor.process_audio_optimized(audio_data)
        assert isinstance(result, np.ndarray)

    def test_fast_normalize(self, processor):
        """Test fast normalization"""
        audio_data = np.array([0.5, 1.0, -0.5], dtype=np.float32)
        result = processor._fast_normalize(audio_data)
        assert isinstance(result, np.ndarray)

    def test_fast_normalize_empty(self, processor):
        """Test fast normalize with empty array"""
        audio_data = np.array([], dtype=np.float32)
        result = processor._fast_normalize(audio_data)
        assert len(result) == 0

    def test_processing_stats_initialized(self, processor):
        """Test processing stats are initialized"""
        assert processor.processing_stats is not None
        assert 'total_requests' in processor.processing_stats
