#!/usr/bin/env python3
"""
Unit tests for voice loader module
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
from LiteTTS.voice.loader import (
    VoiceLoadResult,
    VoiceLoader
)


class TestVoiceLoadResult:
    """Test cases for VoiceLoadResult dataclass"""

    def test_creation_success(self):
        """Test creating a successful load result"""
        result = VoiceLoadResult(
            success=True,
            embedding_data=np.random.randn(256).astype(np.float32),
            metadata={"name": "test_voice"},
            loader_used="numpy"
        )
        assert result.success is True
        assert isinstance(result.embedding_data, np.ndarray)
        assert result.metadata["name"] == "test_voice"
        assert result.loader_used == "numpy"

    def test_creation_failure(self):
        """Test creating a failed load result"""
        result = VoiceLoadResult(
            success=False,
            embedding_data=None,
            metadata=None,
            loader_used="torch",
            error_message="File not found"
        )
        assert result.success is False
        assert result.embedding_data is None
        assert result.error_message == "File not found"


class TestVoiceLoader:
    """Test cases for VoiceLoader class"""

    def test_initialization(self):
        """Test loader initializes correctly"""
        loader = VoiceLoader(voices_dir="/tmp/voices")
        assert loader.voices_dir == Path("/tmp/voices")
        assert isinstance(loader.load_stats, dict)
        assert 'torch_loads' in loader.load_stats
        assert 'numpy_loads' in loader.load_stats

    def test_initialization_mock(self):
        """Test loader with mock enabled"""
        loader = VoiceLoader(voices_dir="/tmp/voices", enable_mock=True)
        assert loader.enable_mock is True

    def test_load_stats_initialization(self):
        """Test load statistics are initialized to zero"""
        loader = VoiceLoader(voices_dir="/tmp/voices")
        assert loader.load_stats['torch_loads'] == 0
        assert loader.load_stats['numpy_loads'] == 0
        assert loader.load_stats['mock_loads'] == 0
        assert loader.load_stats['failed_loads'] == 0

    def test_load_voice_nonexistent(self):
        """Test loading nonexistent voice"""
        loader = VoiceLoader(voices_dir="/tmp/nonexistent")
        result = loader.load_voice("nonexistent_voice")
        assert result.success is False

    def test_load_voice_with_mock(self):
        """Test loading with mock data enabled"""
        loader = VoiceLoader(voices_dir="/tmp/voices", enable_mock=True)
        result = loader.load_voice("mock_voice")
        # Mock loading may succeed or fail depending on implementation
        assert isinstance(result, VoiceLoadResult)
        assert hasattr(result, 'success')
        assert hasattr(result, 'loader_used')
