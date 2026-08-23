#!/usr/bin/env python3
"""
Unit tests for voice discovery module
"""

import json
from pathlib import Path

import numpy as np

from LiteTTS.voice.discovery import VoiceDiscovery, VoiceInfo


class TestVoiceInfo:
    """Test cases for VoiceInfo dataclass"""

    def test_creation(self):
        """Test creating voice info"""
        info = VoiceInfo(
            name="test_voice",
            file_path="/path/to/voice.bin",
            file_size=1024,
            checksum="abc123",
            last_modified=1234567890.0,
            source="local"
        )
        assert info.name == "test_voice"
        assert info.file_path == "/path/to/voice.bin"
        assert info.file_size == 1024
        assert info.source == "local"

    def test_creation_with_optional(self):
        """Test creating voice info with optional fields"""
        info = VoiceInfo(
            name="test_voice",
            file_path="/path/to/voice.bin",
            file_size=1024,
            checksum="abc123",
            last_modified=1234567890.0,
            source="huggingface",
            language="en-us",
            gender="female"
        )
        assert info.language == "en-us"
        assert info.gender == "female"


class TestVoiceDiscovery:
    """Test cases for VoiceDiscovery class"""

    def test_initialization_default(self):
        """Test initialization with default directory"""
        discovery = VoiceDiscovery()
        assert discovery.voices_dir is not None
        assert isinstance(discovery.voices_dir, Path)
        assert isinstance(discovery.voice_cache, dict)

    def test_initialization_custom_dir(self, tmp_path):
        """Test initialization with custom directory"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        assert discovery.voices_dir == tmp_path

    def test_known_voices_loaded(self):
        """Test that known voices are loaded"""
        discovery = VoiceDiscovery()
        assert len(discovery.known_voices) > 0
        assert "af_heart" in discovery.known_voices

    def test_discover_voices_no_files(self, tmp_path):
        """Test discovering voices when no files exist"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovered, updated = discovery.discover_voices()
        assert isinstance(discovered, int)
        assert isinstance(updated, int)

    def test_discover_voices_with_files(self, tmp_path):
        """Test discovering voices with .bin files present"""
        # Create a voice cache file
        cache_file = tmp_path / "voice_cache.json"
        cache_data = {
            "test_voice": {
                "name": "test_voice",
                "file_path": str(tmp_path / "test_voice.bin"),
                "file_size": 1024,
                "checksum": "abc123",
                "last_modified": 1234567890.0,
                "source": "local"
            }
        }
        cache_file.write_text(json.dumps(cache_data))

        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        # The discover_voices returns discovered, updated counts
        assert isinstance(discovery.voice_cache, dict)

    def test_load_voice_cache(self, tmp_path):
        """Test loading voice cache from file"""
        cache_file = tmp_path / "voice_cache.json"
        cache_data = {
            "voice1": {
                "name": "voice1",
                "file_path": str(tmp_path / "voice1.bin"),
                "file_size": 1024,
                "checksum": "abc",
                "last_modified": 123.0,
                "source": "local"
            }
        }
        cache_file.write_text(json.dumps(cache_data))

        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        # The cache should be loaded
        assert isinstance(discovery.voice_cache, dict)

    def test_get_voice_info_existing(self, tmp_path):
        """Test getting voice info for existing voice"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovery.voice_cache["af_heart"] = VoiceInfo(
            name="af_heart",
            file_path="/path/to/af_heart.bin",
            file_size=1024,
            checksum="abc",
            last_modified=123.0,
            source="local"
        )
        info = discovery.get_voice_info("af_heart")
        assert info is not None
        assert info.name == "af_heart"

    def test_get_voice_info_nonexistent(self, tmp_path):
        """Test getting voice info for nonexistent voice"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        info = discovery.get_voice_info("nonexistent_voice")
        assert info is None

    def test_is_voice_available(self, tmp_path):
        """Test checking if voice is available"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovery.voice_cache["af_heart"] = VoiceInfo(
            name="af_heart",
            file_path="/path/to/af_heart.bin",
            file_size=1024,
            checksum="abc",
            last_modified=123.0,
            source="local"
        )
        assert discovery.is_voice_available("af_heart") is True
        assert discovery.is_voice_available("nonexistent") is False

    def test_get_available_voices(self, tmp_path):
        """Test getting list of available voices"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovery.voice_cache["voice1"] = VoiceInfo(
            name="voice1", file_path="/p1", file_size=1,
            checksum="a", last_modified=1.0, source="local"
        )
        discovery.voice_cache["voice2"] = VoiceInfo(
            name="voice2", file_path="/p2", file_size=1,
            checksum="b", last_modified=1.0, source="local"
        )
        voices = discovery.get_available_voices()
        assert "voice1" in voices
        assert "voice2" in voices

    def test_load_voice_data_file_not_found(self, tmp_path):
        """Test loading voice data when file doesn't exist"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovery.voice_cache["ghost_voice"] = VoiceInfo(
            name="ghost_voice",
            file_path="/nonexistent/path.bin",
            file_size=1024,
            checksum="abc",
            last_modified=123.0,
            source="local"
        )
        result = discovery.load_voice_data("ghost_voice")
        assert result is None

    def test_load_voice_data_success(self, tmp_path):
        """Test loading voice data successfully"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))

        # Create a valid voice file
        voice_file = tmp_path / "test_voice.bin"
        voice_data = np.random.randn(512).astype(np.float32)  # 2 * 256
        voice_data.tofile(str(voice_file))

        discovery.voice_cache["test_voice"] = VoiceInfo(
            name="test_voice",
            file_path=str(voice_file),
            file_size=voice_file.stat().st_size,
            checksum="abc",
            last_modified=voice_file.stat().st_mtime,
            source="local"
        )

        result = discovery.load_voice_data("test_voice")
        assert result is not None
        assert isinstance(result, np.ndarray)

    def test_load_voice_data_cached(self, tmp_path):
        """Test that load_voice_data returns cached data"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))

        # Create a valid voice file
        voice_file = tmp_path / "test_voice.bin"
        voice_data = np.random.randn(512).astype(np.float32)
        voice_data.tofile(str(voice_file))

        discovery.voice_cache["test_voice"] = VoiceInfo(
            name="test_voice",
            file_path=str(voice_file),
            file_size=voice_file.stat().st_size,
            checksum="abc",
            last_modified=voice_file.stat().st_mtime,
            source="local"
        )

        # First load
        result1 = discovery.load_voice_data("test_voice")
        # Second load should use cache
        result2 = discovery.load_voice_data("test_voice")
        assert result2 is result1  # Same object from cache

    def test_get_voice_stats(self, tmp_path):
        """Test getting voice statistics"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovery.voice_cache["v1"] = VoiceInfo(
            name="v1", file_path="/p1", file_size=1024,
            checksum="a", last_modified=1.0, source="huggingface",
            language="en-us", gender="female", nationality="american"
        )
        discovery.voice_cache["v2"] = VoiceInfo(
            name="v2", file_path="/p2", file_size=1024,
            checksum="b", last_modified=1.0, source="local",
            language="ja-jp", gender="male", nationality="japanese"
        )

        stats = discovery.get_voice_stats()
        assert stats["total_voices"] == 2
        assert stats["loaded_voices"] == 0
        assert "en-us" in stats["by_language"]
        assert "ja-jp" in stats["by_language"]

    def test_filter_voices_by_language(self, tmp_path):
        """Test filtering voices by language"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovery.voice_cache["v1"] = VoiceInfo(
            name="v1", file_path="/p1", file_size=1,
            checksum="a", last_modified=1.0, source="local",
            language="en-us"
        )
        discovery.voice_cache["v2"] = VoiceInfo(
            name="v2", file_path="/p2", file_size=1,
            checksum="b", last_modified=1.0, source="local",
            language="ja-jp"
        )

        result = discovery.filter_voices(language="en-us")
        assert "v1" in result
        assert "v2" not in result

    def test_filter_voices_by_gender(self, tmp_path):
        """Test filtering voices by gender"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovery.voice_cache["v1"] = VoiceInfo(
            name="v1", file_path="/p1", file_size=1,
            checksum="a", last_modified=1.0, source="local",
            gender="female"
        )
        discovery.voice_cache["v2"] = VoiceInfo(
            name="v2", file_path="/p2", file_size=1,
            checksum="b", last_modified=1.0, source="local",
            gender="male"
        )

        result = discovery.filter_voices(gender="male")
        assert "v2" in result
        assert "v1" not in result

    def test_filter_voices_by_nationality(self, tmp_path):
        """Test filtering voices by nationality"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovery.voice_cache["v1"] = VoiceInfo(
            name="v1", file_path="/p1", file_size=1,
            checksum="a", last_modified=1.0, source="local",
            nationality="american"
        )
        discovery.voice_cache["v2"] = VoiceInfo(
            name="v2", file_path="/p2", file_size=1,
            checksum="b", last_modified=1.0, source="local",
            nationality="japanese"
        )

        result = discovery.filter_voices(nationality="japanese")
        assert "v2" in result
        assert "v1" not in result

    def test_filter_voices_by_source(self, tmp_path):
        """Test filtering voices by source"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovery.voice_cache["v1"] = VoiceInfo(
            name="v1", file_path="/p1", file_size=1,
            checksum="a", last_modified=1.0, source="huggingface"
        )
        discovery.voice_cache["v2"] = VoiceInfo(
            name="v2", file_path="/p2", file_size=1,
            checksum="b", last_modified=1.0, source="local"
        )

        result = discovery.filter_voices(source="huggingface")
        assert "v1" in result
        assert "v2" not in result

    def test_filter_voices_no_match(self, tmp_path):
        """Test filtering voices with no matches"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovery.voice_cache["v1"] = VoiceInfo(
            name="v1", file_path="/p1", file_size=1,
            checksum="a", last_modified=1.0, source="local",
            language="en-us"
        )

        result = discovery.filter_voices(language="ja-jp")
        assert len(result) == 0

    def test_clear_loaded_voices(self, tmp_path):
        """Test clearing loaded voices"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))

        # Create a valid voice file and load it
        voice_file = tmp_path / "test_voice.bin"
        voice_data = np.random.randn(512).astype(np.float32)
        voice_data.tofile(str(voice_file))

        discovery.voice_cache["test_voice"] = VoiceInfo(
            name="test_voice",
            file_path=str(voice_file),
            file_size=voice_file.stat().st_size,
            checksum="abc",
            last_modified=voice_file.stat().st_mtime,
            source="local"
        )

        # Load the voice
        discovery.load_voice_data("test_voice")
        assert len(discovery.loaded_voices) == 1

        # Clear
        discovery.clear_loaded_voices()
        assert len(discovery.loaded_voices) == 0

    def test_invalidate_cache(self, tmp_path):
        """Test invalidating cache"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))
        discovery.voice_cache["v1"] = VoiceInfo(
            name="v1", file_path="/p1", file_size=1,
            checksum="a", last_modified=1.0, source="local"
        )
        discovery.loaded_voices["v1"] = np.array([1.0])

        # Create a cache file
        discovery._save_cache()
        assert discovery.cache_file.exists()

        discovery.invalidate_cache()
        assert len(discovery.voice_cache) == 0
        assert len(discovery.loaded_voices) == 0
        assert not discovery.cache_file.exists()

    def test_discover_voices_with_updates(self, tmp_path):
        """Test discovering voices when files have been updated"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))

        # Create a voice file
        voice_file = tmp_path / "test_voice.bin"
        voice_file.write_bytes(b'\x00' * 100)

        # First discovery
        d1, u1 = discovery.discover_voices()
        assert d1 >= 1

        # Modify the file
        voice_file.write_bytes(b'\x00' * 200)

        # Second discovery should detect update
        d2, u2 = discovery.discover_voices()
        assert u2 >= 1

    def test_discover_voices_removes_deleted(self, tmp_path):
        """Test that discover_voices removes deleted voices from cache"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))

        # Create a voice file and discover it
        voice_file = tmp_path / "test_voice.bin"
        voice_file.write_bytes(b'\x00' * 100)

        discovery.discover_voices()
        assert "test_voice" in discovery.voice_cache

        # Delete the file
        voice_file.unlink()

        # Rediscover
        discovery.discover_voices()
        assert "test_voice" not in discovery.voice_cache

    def test_calculate_checksum(self, tmp_path):
        """Test checksum calculation"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))

        # Create a file
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b'\x00' * 100)

        checksum = discovery._calculate_checksum(test_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 produces 64 char hex

    def test_calculate_checksum_consistency(self, tmp_path):
        """Test that checksum is consistent"""
        discovery = VoiceDiscovery(voices_dir=str(tmp_path))

        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b'\x00' * 100)

        checksum1 = discovery._calculate_checksum(test_file)
        checksum2 = discovery._calculate_checksum(test_file)
        assert checksum1 == checksum2
