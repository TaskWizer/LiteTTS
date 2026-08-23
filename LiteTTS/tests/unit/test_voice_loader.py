#!/usr/bin/env python3
"""
Unit tests for voice loader module
"""

from pathlib import Path
from unittest.mock import patch

import numpy as np

from LiteTTS.voice.loader import VoiceLoader, VoiceLoadResult


class TestVoiceLoadResult:
    """Test cases for VoiceLoadResult dataclass"""

    def test_creation_success(self):
        """Test creating a successful load result"""
        result = VoiceLoadResult(
            success=True,
            embedding_data=np.random.randn(256).astype(np.float32),
            metadata={"name": "test_voice"},
            loader_used="numpy",
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
            error_message="File not found",
        )
        assert result.success is False
        assert result.embedding_data is None
        assert result.error_message == "File not found"

    def test_creation_with_defaults(self):
        """Test creating load result with minimal args"""
        result = VoiceLoadResult(
            success=True, embedding_data=np.array([1.0]), metadata={}, loader_used="numpy"
        )
        assert result.error_message is None


class TestVoiceLoader:
    """Test cases for VoiceLoader class"""

    def test_initialization(self):
        """Test loader initializes correctly"""
        loader = VoiceLoader(voices_dir="/tmp/voices")
        assert loader.voices_dir == Path("/tmp/voices")
        assert isinstance(loader.load_stats, dict)
        assert "torch_loads" in loader.load_stats
        assert "numpy_loads" in loader.load_stats

    def test_initialization_mock(self):
        """Test loader with mock enabled"""
        loader = VoiceLoader(voices_dir="/tmp/voices", enable_mock=True)
        assert loader.enable_mock is True

    def test_load_stats_initialization(self):
        """Test load statistics are initialized to zero"""
        loader = VoiceLoader(voices_dir="/tmp/voices")
        assert loader.load_stats["torch_loads"] == 0
        assert loader.load_stats["numpy_loads"] == 0
        assert loader.load_stats["mock_loads"] == 0
        assert loader.load_stats["failed_loads"] == 0

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
        assert hasattr(result, "success")
        assert hasattr(result, "loader_used")

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

        initial_numpy_loads = loader.load_stats["numpy_loads"]
        result = loader.load_voice("test_voice")

        assert result.success is True
        assert loader.load_stats["numpy_loads"] == initial_numpy_loads + 1

    def test_load_voice_updates_stats_on_failure(self, tmp_path):
        """Test that load statistics are updated on failed load"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        initial_failed = loader.load_stats["failed_loads"]
        result = loader.load_voice("nonexistent_voice")

        assert result.success is False
        assert loader.load_stats["failed_loads"] == initial_failed + 1

    def test_load_voice_with_torch_available(self, tmp_path):
        """Test loading when torch is available"""
        with patch("LiteTTS.voice.loader._TORCH_AVAILABLE", True):
            loader = VoiceLoader(voices_dir=str(tmp_path))
            assert loader.torch_available is True

    def test_load_voice_with_torch_unavailable(self, tmp_path):
        """Test loading when torch is not available"""
        with patch("LiteTTS.voice.loader._TORCH_AVAILABLE", False):
            loader = VoiceLoader(voices_dir=str(tmp_path))
            assert loader.torch_available is False

    def test_load_voice_invalid_bin_file(self, tmp_path):
        """Test loading invalid .bin file"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        # Create an invalid .bin file
        bin_file = tmp_path / "invalid.bin"
        bin_file.write_bytes(b"invalid data")

        result = loader.load_voice("invalid")
        # Should either succeed with warning or fail
        assert isinstance(result, VoiceLoadResult)

    def test_get_load_statistics(self, tmp_path):
        """Test getting load statistics"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        stats = loader.get_load_statistics()

        assert "torch_loads" in stats
        assert "numpy_loads" in stats
        assert "mock_loads" in stats
        assert "failed_loads" in stats

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

        assert stats["numpy_loads"] == 1
        assert stats["failed_loads"] == 1

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

        assert loader.load_stats["numpy_loads"] >= 1

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

    def test_load_with_torch_file_not_found(self, tmp_path):
        """Test _load_with_torch when file doesn't exist"""
        loader = VoiceLoader(voices_dir=str(tmp_path))
        loader.torch_available = True

        result = loader._load_with_torch("nonexistent")

        assert result.success is False
        assert "not found" in result.error_message.lower()

    def test_load_with_torch_torch_unavailable(self, tmp_path):
        """Test _load_with_torch when torch is unavailable"""
        loader = VoiceLoader(voices_dir=str(tmp_path))
        loader.torch_available = False

        result = loader._load_with_torch("any_voice")

        assert result.success is False
        assert "not available" in result.error_message.lower()

    def test_load_with_torch_success(self, tmp_path):
        """Test _load_with_torch successful loading"""
        import torch

        loader = VoiceLoader(voices_dir=str(tmp_path))
        loader.torch_available = True

        # Create a valid .pt file
        pt_file = tmp_path / "test_voice.pt"
        embedding_data = torch.randn(10, 256)
        torch.save({"embedding": embedding_data}, pt_file)

        result = loader._load_with_torch("test_voice")

        assert result.success is True
        assert result.loader_used == "torch"

    def test_load_with_torch_dict_format(self, tmp_path):
        """Test _load_with_torch with dictionary format"""
        import torch

        loader = VoiceLoader(voices_dir=str(tmp_path))
        loader.torch_available = True

        # Create a .pt file with dict format containing style_vector
        pt_file = tmp_path / "test_voice.pt"
        embedding_data = torch.randn(10, 256)
        torch.save({"style_vector": embedding_data, "name": "test"}, pt_file)

        result = loader._load_with_torch("test_voice")

        assert result.success is True

    def test_load_with_torch_no_tensor_found(self, tmp_path):
        """Test _load_with_torch when no tensor key is found"""
        import torch

        loader = VoiceLoader(voices_dir=str(tmp_path))
        loader.torch_available = True

        # Create a .pt file with no tensor data - just strings
        pt_file = tmp_path / "test_voice.pt"
        torch.save({"name": "test", "description": "no tensor here"}, pt_file)

        result = loader._load_with_torch("test_voice")

        # No embedding, style_vector, or tensor data -> should fail
        assert result.success is False

    def test_load_with_torch_exception(self, tmp_path):
        """Test _load_with_torch handles exceptions"""
        loader = VoiceLoader(voices_dir=str(tmp_path))
        loader.torch_available = True

        # Create a corrupt .pt file
        pt_file = tmp_path / "test_voice.pt"
        pt_file.write_bytes(b"corrupt data")

        result = loader._load_with_torch("test_voice")

        assert result.success is False
        assert result.loader_used == "torch"

    def test_load_with_numpy_file_not_found(self, tmp_path):
        """Test _load_with_numpy when file doesn't exist"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        result = loader._load_with_numpy("nonexistent")

        assert result.success is False
        assert "not found" in result.error_message.lower()

    def test_load_with_numpy_success(self, tmp_path):
        """Test _load_with_numpy successful loading"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        # Create a valid .bin file
        bin_file = tmp_path / "test_voice.bin"
        voice_data = np.random.randn(512).astype(np.float32)  # 512 = 2 * 256
        voice_data.tofile(str(bin_file))

        result = loader._load_with_numpy("test_voice")

        assert result.success is True
        assert result.loader_used == "numpy"
        assert isinstance(result.embedding_data, np.ndarray)

    def test_load_with_numpy_unusual_size(self, tmp_path):
        """Test _load_with_numpy with unusual size"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        # Create a .bin file with size not divisible by 256
        bin_file = tmp_path / "test_voice.bin"
        voice_data = np.random.randn(500).astype(np.float32)  # Not divisible by 256
        voice_data.tofile(str(bin_file))

        result = loader._load_with_numpy("test_voice")

        # Should still succeed but with warning
        assert result.success is True

    def test_load_with_numpy_exception(self, tmp_path):
        """Test _load_with_numpy handles exceptions"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        # Create a file that will cause an error when loading
        bin_file = tmp_path / "test_voice.bin"
        bin_file.write_bytes(b"partial")

        # Override to make numpy fail
        with patch("numpy.fromfile", side_effect=Exception("Test error")):
            result = loader._load_with_numpy("test_voice")

        assert result.success is False

    def test_load_mock_data_success(self, tmp_path):
        """Test _load_mock_data successful generation"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        result = loader._load_mock_data("test_voice")

        assert result.success is True
        assert result.loader_used == "mock"
        assert isinstance(result.embedding_data, np.ndarray)

    def test_load_mock_data_returns_consistent(self, tmp_path):
        """Test _load_mock_data returns consistent data for same voice"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        result1 = loader._load_mock_data("test_voice")
        result2 = loader._load_mock_data("test_voice")

        assert result1.success is True
        assert result2.success is True
        assert np.array_equal(result1.embedding_data, result2.embedding_data)

    def test_load_mock_data_different_for_different_voices(self, tmp_path):
        """Test _load_mock_data returns different data for different voices"""
        loader = VoiceLoader(voices_dir=str(tmp_path))

        result1 = loader._load_mock_data("voice1")
        result2 = loader._load_mock_data("voice2")

        assert result1.success is True
        assert result2.success is True
        assert not np.array_equal(result1.embedding_data, result2.embedding_data)

    def test_load_voice_numpy_fallback_after_torch_fails(self, tmp_path):
        """Test loading falls back to numpy after torch fails"""
        with patch("LiteTTS.voice.loader._TORCH_AVAILABLE", True):
            loader = VoiceLoader(voices_dir=str(tmp_path))

            # Create only a .bin file, no .pt file
            bin_file = tmp_path / "test_voice.bin"
            voice_data = np.random.randn(256).astype(np.float32)
            voice_data.tofile(str(bin_file))

            result = loader.load_voice("test_voice")

            assert result.success is True
            assert result.loader_used == "numpy"

    def test_load_voice_uses_mock_when_enabled(self, tmp_path):
        """Test loading uses mock data when enabled and no file exists"""
        loader = VoiceLoader(voices_dir=str(tmp_path), enable_mock=True)

        result = loader.load_voice("nonexistent_voice")

        assert result.success is True
        assert result.loader_used == "mock"

    def test_load_voice_all_methods_fail(self, tmp_path):
        """Test loading when all methods fail"""
        loader = VoiceLoader(voices_dir=str(tmp_path), enable_mock=False)
        loader.torch_available = False

        result = loader.load_voice("nonexistent")

        assert result.success is False
        assert "failed" in result.error_message.lower()

    def test_load_voice_with_pt_file_dict_with_data_key(self, tmp_path):
        """Test loading .pt file with 'data' key"""
        import torch

        loader = VoiceLoader(voices_dir=str(tmp_path))
        loader.torch_available = True

        # Create a .pt file with 'data' key
        pt_file = tmp_path / "test_voice.pt"
        embedding_data = torch.randn(10, 256)
        torch.save({"data": embedding_data}, pt_file)

        result = loader._load_with_torch("test_voice")

        assert result.success is True

    def test_load_voice_with_pt_file_multiple_tensors(self, tmp_path):
        """Test loading .pt file with multiple tensors"""
        import torch

        loader = VoiceLoader(voices_dir=str(tmp_path))
        loader.torch_available = True

        # Create a .pt file with multiple tensors
        pt_file = tmp_path / "test_voice.pt"
        embedding_data = torch.randn(10, 256)
        torch.save(
            {"embedding": embedding_data, "style_vector": torch.randn(10, 256), "name": "test"},
            pt_file,
        )

        result = loader._load_with_torch("test_voice")

        assert result.success is True
