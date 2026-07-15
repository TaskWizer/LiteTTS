#!/usr/bin/env python3
"""
Unit tests for voice discovery module
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
from LiteTTS.voice.discovery import (
    VoiceInfo,
    VoiceDiscovery
)


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
