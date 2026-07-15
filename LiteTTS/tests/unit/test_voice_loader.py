#!/usr/bin/env python3
"""
Unit tests for voice loader
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from LiteTTS.voice.loader import VoiceLoader, VoiceLoadResult, get_voice_loader


class TestVoiceLoader:
    """Test cases for VoiceLoader"""

    @pytest.fixture
    def loader(self):
        """Create loader instance"""
        return VoiceLoader(voices_dir="LiteTTS/voices", enable_mock=True)

    def test_initialization(self, loader):
        """Test loader initializes correctly"""
        assert loader is not None
        assert loader.voices_dir == Path("LiteTTS/voices")
        assert loader.enable_mock is True

    def test_load_stats_initialization(self, loader):
        """Test load statistics are initialized"""
        assert 'torch_loads' in loader.load_stats
        assert 'numpy_loads' in loader.load_stats
        assert 'mock_loads' in loader.load_stats
        assert 'failed_loads' in loader.load_stats

    def test_load_voice_returns_result(self, loader):
        """Test load_voice returns VoiceLoadResult"""
        result = loader.load_voice("test_voice")
        assert isinstance(result, VoiceLoadResult)


class TestVoiceLoadResult:
    """Test cases for VoiceLoadResult"""

    def test_successful_result(self):
        """Test creating a successful load result"""
        result = VoiceLoadResult(
            success=True,
            embedding_data=np.random.randn(128).astype(np.float32),
            metadata={"name": "test_voice"},
            loader_used="numpy"
        )
        assert result.success is True
        assert result.embedding_data is not None
        assert result.loader_used == "numpy"

    def test_failed_result(self):
        """Test creating a failed load result"""
        result = VoiceLoadResult(
            success=False,
            embedding_data=None,
            metadata=None,
            loader_used="none",
            error_message="File not found"
        )
        assert result.success is False
        assert result.error_message == "File not found"


class TestGetVoiceLoader:
    """Test cases for get_voice_loader factory function"""

    def test_get_voice_loader_returns_loader(self):
        """Test factory returns VoiceLoader instance"""
        loader = get_voice_loader("LiteTTS/voices", enable_mock=True)
        assert isinstance(loader, VoiceLoader)
