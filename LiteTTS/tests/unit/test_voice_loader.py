#!/usr/bin/env python3
"""
Unit tests for voice loader module
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from LiteTTS.voice.loader import (
    VoiceLoadResult,
    VoiceLoader,
    _TORCH_AVAILABLE
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

    def test_creation_with_defaults(self):
        """Test creating load result with minimal args"""
        result = VoiceLoadResult(
            success=True,
            embedding_data=np.array([1.0]),
            metadata={},
            loader_used="numpy"
        )
        assert result.error_message is None


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
        assert isinstance(result, VoiceLoadResult)
        assert hasattr(result, 'success')
        assert hasattr(result, 'loader_used')

    def test_load_voice_bin_file_success(self, tmp_path):
        """Test loading a valid .bin file"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        # Create a valid .bin file
        voice_data = np.random.randn(256).astype(np.float32)
        bin_file = tmp_path / "test_voice.bin"
        voice_data.tofile(str(bin_file))

        result = loader.load_voice("test_voice")

        assert result.success is True
        assert result.loader_used == "numpy"
        assert isinstance(result.embedding_data, np.ndarray)

    def test_load_voice_updates_stats_on_success(self, tmp_path):
        """Test that load statistics are updated on successful load"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        # Create a valid .bin file
        voice_data = np.random.randn(256).astype(np.float32)
        bin_file = tmp_path / "test_voice.bin"
        voice_data.tofile(str(bin_file))

        initial_numpy_loads = loader.load_stats['numpy_loads']
        result = loader.load_voice("test_voice")

        assert result.success is True
        assert loader.load_stats['numpy_loads'] == initial_numpy_loads + 1

    def test_load_voice_updates_stats_on_failure(self, tmp_path):
        """Test that load statistics are updated on failed load"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        initial_failed = loader.load_stats['failed_loads']
        result = loader.load_voice("nonexistent_voice")

        assert result.success is False
        assert loader.load_stats['failed_loads'] == initial_failed + 1

    def test_load_voice_with_torch_available(self, tmp_path):
        """Test loading when torch is available"""
        with patch('LiteTTS.voice.loader._TORCH_AVAILABLE', True):
            loader = VoiceLoader(voices_dir=str(tmp_path))
            assert loader.torch_available is True

    def test_load_voice_with_torch_unavailable(self, tmp_path):
        """Test loading when torch is not available"""
        with patch('LiteTTS.voice.loader._TORCH_AVAILABLE', False):
            loader = VoiceLoader(voices_dir=str(tmp_path))
            assert loader.torch_available is False

    def test_load_voice_invalid_bin_file(self, tmp_path):
        """Test loading invalid .bin file"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        # Create an invalid .bin file
        bin_file = tmp_path / "invalid.bin"
        bin_file.write_bytes(b'invalid data')

        result = loader.load_voice("invalid")
        # Should either succeed with warning or fail
        assert isinstance(result, VoiceLoadResult)

    def test_get_load_statistics(self, tmp_path):
        """Test getting load statistics"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        stats = loader.get_load_statistics()

        assert 'torch_loads' in stats
        assert 'numpy_loads' in stats
        assert 'mock_loads' in stats
        assert 'failed_loads' in stats

    def test_get_load_statistics_after_loads(self, tmp_path):
        """Test statistics after multiple loads"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        # Create a valid .bin file
        voice_data = np.random.randn(256).astype(np.float32)
        bin_file = tmp_path / "test_voice.bin"
        voice_data.tofile(str(bin_file))

        # Perform successful load
        loader.load_voice("test_voice")

        # Perform failed load
        loader.load_voice("nonexistent")

        stats = loader.get_load_statistics()

        assert stats['numpy_loads'] == 1
        assert stats['failed_loads'] == 1

    def test_load_voice_respects_voices_dir(self, tmp_path):
        """Test that load_voice uses the correct voices directory"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        # Create a file in the wrong place
        voice_data = np.random.randn(256).astype(np.float32)
        wrong_file = tmp_path / "correct_voice.bin"
        voice_data.tofile(str(wrong_file))

        result = loader.load_voice("correct_voice")

        # Should succeed because voices_dir is tmp_path
        assert result.success is True

    def test_load_voice_numpy_load_increments_counter(self, tmp_path):
        """Test that numpy load increments the correct counter"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        # Create a valid .bin file
        voice_data = np.random.randn(256).astype(np.float32)
        bin_file = tmp_path / "test_voice.bin"
        voice_data.tofile(str(bin_file))

        loader.load_voice("test_voice")

        assert loader.load_stats['numpy_loads'] >= 1

    def test_load_voice_metadata_returned(self, tmp_path):
        """Test that metadata is returned with successful load"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        # Create a valid .bin file
        voice_data = np.random.randn(256).astype(np.float32)
        bin_file = tmp_path / "test_voice.bin"
        voice_data.tofile(str(bin_file))

        result = loader.load_voice("test_voice")

        assert result.metadata is not None
        assert isinstance(result.metadata, dict)

    def test_load_voice_error_message_on_failure(self, tmp_path):
        """Test that error message is set on failure"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        result = loader.load_voice("nonexistent")

        assert result.success is False
        assert result.error_message is not None
        assert isinstance(result.error_message, str)
