#!/usr/bin/env python3
"""
Unit tests for simple combiner module
"""

import warnings
from pathlib import Path
from unittest.mock import Mock

import numpy as np

from LiteTTS.voice.simple_combiner import SimplifiedVoiceCombiner


class TestSimplifiedVoiceCombiner:
    """Test cases for SimplifiedVoiceCombiner class"""

    def test_initialization_deprecation_warning(self, tmp_path):
        """Test that initialization issues deprecation warning"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()

    def test_initialization_disabled_by_config(self, tmp_path):
        """Test initialization when disabled by config"""
        mock_config = Mock()
        mock_config.voice.use_combined_file = False

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path), config=mock_config)
            assert combiner.disabled is True

    def test_initialization_enabled(self, tmp_path):
        """Test initialization when enabled"""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            assert combiner.disabled is False
            assert isinstance(combiner.voices_dir, Path)

    def test_load_individual_voice_file_not_found(self, tmp_path):
        """Test loading a voice that doesn't exist"""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            result = combiner._load_individual_voice("nonexistent_voice")
            assert result is None

    def test_load_individual_voice_standard_format(self, tmp_path):
        """Test loading voice with standard 510x256 format"""
        voice_file = tmp_path / "test_voice.bin"
        # Create standard format: 510 * 256 = 130560 float32 values
        voice_data = np.random.randn(510 * 256).astype(np.float32)
        voice_data.tofile(str(voice_file))

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            result = combiner._load_individual_voice("test_voice")
            assert result is not None
            assert result.shape == (510, 256)

    def test_load_individual_voice_512_format(self, tmp_path):
        """Test loading voice with 512x256 format"""
        voice_file = tmp_path / "test_voice2.bin"
        # Create 512x256 format: 512 * 256 = 131072 float32 values
        voice_data = np.random.randn(512 * 256).astype(np.float32)
        voice_data.tofile(str(voice_file))

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            result = combiner._load_individual_voice("test_voice2")
            assert result is not None
            assert result.shape == (512, 256)

    def test_load_individual_voice_single_vector(self, tmp_path):
        """Test loading voice with single 256-dim vector"""
        voice_file = tmp_path / "test_voice3.bin"
        # Single vector: 256 float32 values
        voice_data = np.random.randn(256).astype(np.float32)
        voice_data.tofile(str(voice_file))

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            result = combiner._load_individual_voice("test_voice3")
            assert result is not None
            assert result.shape == (510, 256)  # Expanded to 510 vectors

    def test_get_available_voices(self, tmp_path):
        """Test getting list of available voices"""
        # Create some voice files
        (tmp_path / "voice1.bin").write_bytes(b"\x00" * 100)
        (tmp_path / "voice2.bin").write_bytes(b"\x00" * 100)

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            voices = combiner._get_available_voices()
            assert "voice1" in voices
            assert "voice2" in voices

    def test_create_combined_file_disabled(self, tmp_path):
        """Test create_combined_file when disabled"""
        mock_config = Mock()
        mock_config.voice.use_combined_file = False

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path), config=mock_config)
            result = combiner.create_combined_file()
            assert result is True

    def test_create_combined_file_no_voices(self, tmp_path):
        """Test create_combined_file with no voice files"""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            result = combiner.create_combined_file()
            assert result is False

    def test_create_combined_file_success(self, tmp_path):
        """Test successful combined file creation"""
        # Create a valid voice file
        voice_file = tmp_path / "test_voice.bin"
        voice_data = np.random.randn(510 * 256).astype(np.float32)
        voice_data.tofile(str(voice_file))

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            result = combiner.create_combined_file()
            assert result is True
            assert combiner.combined_file.exists()
            assert combiner.voice_index_file.exists()

    def test_ensure_combined_file_creates_when_missing(self, tmp_path):
        """Test ensure_combined_file creates file when missing"""
        voice_file = tmp_path / "test_voice.bin"
        voice_data = np.random.randn(510 * 256).astype(np.float32)
        voice_data.tofile(str(voice_file))

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            path = combiner.ensure_combined_file()
            assert Path(path).exists()

    def test_get_voice_list_from_index(self, tmp_path):
        """Test getting voice list from index file"""
        # Create voice index file
        index_file = tmp_path / "voice_index.json"
        index_file.write_text('{"voice1": 0, "voice2": 1}')

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            voices = combiner.get_voice_list()
            assert "voice1" in voices
            assert "voice2" in voices

    def test_get_voice_count(self, tmp_path):
        """Test getting voice count"""
        # Create voice index file
        index_file = tmp_path / "voice_index.json"
        index_file.write_text('{"voice1": 0, "voice2": 1, "voice3": 2}')

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            combiner = SimplifiedVoiceCombiner(voices_dir=str(tmp_path))
            count = combiner.get_voice_count()
            assert count == 3
