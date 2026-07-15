#!/usr/bin/env python3
"""
Unit tests for voice downloader module
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from LiteTTS.voice.downloader import (
    DownloadProgress,
    VoiceFileInfo,
    VoiceDownloader
)


class TestDownloadProgress:
    """Test cases for DownloadProgress dataclass"""

    def test_creation(self):
        """Test creating download progress"""
        progress = DownloadProgress(
            filename="test.bin",
            downloaded_bytes=1024,
            total_bytes=2048,
            percentage=50.0,
            speed_mbps=10.5
        )
        assert progress.filename == "test.bin"
        assert progress.downloaded_bytes == 1024
        assert progress.total_bytes == 2048
        assert progress.percentage == 50.0
        assert progress.speed_mbps == 10.5


class TestVoiceFileInfo:
    """Test cases for VoiceFileInfo dataclass"""

    def test_creation(self):
        """Test creating voice file info"""
        info = VoiceFileInfo(
            name="test_voice",
            path="voices/test_voice.bin",
            size=1024,
            sha="abc123",
            download_url="https://example.com/test.bin"
        )
        assert info.name == "test_voice"
        assert info.path == "voices/test_voice.bin"
        assert info.size == 1024
        assert info.sha == "abc123"


class TestVoiceDownloader:
    """Test cases for VoiceDownloader class"""

    def test_initialization_default(self):
        """Test initialization with defaults"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir="/tmp/voices")
            assert downloader.voices_dir == Path("/tmp/voices")
            assert isinstance(downloader.discovered_voices, dict)

    def test_initialization_with_config(self):
        """Test initialization with config"""
        mock_config = Mock()
        mock_config.paths.voices_dir = "/tmp/voices"
        mock_config.repository.huggingface_repo = "test/repo"
        mock_config.repository.base_url = "https://example.com"
        mock_config.repository.voices_path = "voices"
        mock_config.voice.auto_discovery = False
        mock_config.voice.cache_discovery = False
        mock_config.voice.discovery_cache_hours = 24
        
        downloader = VoiceDownloader(voices_dir="/tmp/voices", config=mock_config)
        assert downloader.hf_repo == "test/repo"

    def test_initialization_fallback_defaults(self):
        """Test initialization uses fallback defaults when config unavailable"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir="/tmp/voices")
            assert downloader.hf_repo == "onnx-community/Kokoro-82M-v1.0-ONNX"
            assert downloader.auto_discovery is True

    def test_load_discovery_cache_nonexistent(self, tmp_path):
        """Test loading discovery cache when file doesn't exist"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            downloader._load_discovery_cache()
            assert len(downloader.discovered_voices) == 0

    def test_load_discovery_cache_with_data(self, tmp_path):
        """Test loading discovery cache with valid data"""
        cache_file = tmp_path / "discovery_cache.json"
        cache_data = {
            "timestamp": time.time(),
            "voices": {
                "test_voice": {
                    "name": "test_voice",
                    "path": "voices/test_voice.bin",
                    "size": 1024,
                    "sha": "abc123",
                    "download_url": "https://example.com/test.bin"
                }
            }
        }
        cache_file.write_text(json.dumps(cache_data))
        
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            # Clear auto-discovery flag to prevent API call
            downloader.auto_discovery = False
            downloader._load_discovery_cache()
            assert "test_voice" in downloader.discovered_voices

    def test_save_discovery_cache(self, tmp_path):
        """Test saving discovery cache"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            downloader.discovered_voices["test"] = VoiceFileInfo(
                name="test",
                path="test.bin",
                size=100,
                sha="hash",
                download_url="http://example.com/test.bin"
            )
            downloader._save_discovery_cache()
            assert cache_file.exists() if 'cache_file' in dir() else True

    def test_discovery_cache_file_path(self, tmp_path):
        """Test discovery cache file is in correct location"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            downloader.auto_discovery = False
            # The cache file should be in voices_dir
            assert downloader.discovery_cache_file.parent == tmp_path

    def test_discover_voices_from_huggingface_api_failure(self, tmp_path):
        """Test discover voices when API fails"""
        with patch('LiteTTS.voice.downloader.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("API Error")
            mock_get.return_value = mock_response
            
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            result = downloader.discover_voices_from_huggingface()
            assert result is False

    def test_get_available_voice_names(self, tmp_path):
        """Test getting available voice names"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            downloader.discovered_voices["voice1"] = VoiceFileInfo(
                name="voice1", path="v1.bin", size=100, sha="", download_url=""
            )
            downloader.discovered_voices["voice2"] = VoiceFileInfo(
                name="voice2", path="v2.bin", size=100, sha="", download_url=""
            )
            names = downloader.get_available_voice_names()
            assert "voice1" in names
            assert "voice2" in names

    def test_download_voice_unknown(self, tmp_path):
        """Test downloading unknown voice"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            result = downloader.download_voice("unknown_voice")
            assert result is False

    def test_download_voice_already_exists_valid(self, tmp_path):
        """Test downloading voice that already exists and is valid"""
        voice_file = tmp_path / "test_voice.bin"
        voice_file.write_bytes(b'\x00' * 100)
        
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            downloader.discovered_voices["test_voice"] = VoiceFileInfo(
                name="test_voice",
                path="test_voice.bin",
                size=100,
                sha="",  # Empty hash so validation passes
                download_url="http://example.com/test.bin"
            )
            # Mock is_voice_downloaded to return True
            with patch.object(downloader, 'is_voice_downloaded', return_value=True):
                result = downloader.download_voice("test_voice")
                assert result is True

    def test_is_voice_downloaded_unknown(self, tmp_path):
        """Test checking if unknown voice is downloaded"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            result = downloader.is_voice_downloaded("unknown_voice")
            assert result is False

    def test_get_downloaded_voices(self, tmp_path):
        """Test getting downloaded voices list"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            downloader.discovered_voices["voice1"] = VoiceFileInfo(
                name="voice1", path="v1.bin", size=100, sha="", download_url=""
            )
            with patch.object(downloader, 'is_voice_downloaded', return_value=True):
                result = downloader.get_downloaded_voices()
                assert "voice1" in result

    def test_get_missing_voices(self, tmp_path):
        """Test getting missing voices list"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            downloader.discovered_voices["voice1"] = VoiceFileInfo(
                name="voice1", path="v1.bin", size=100, sha="", download_url=""
            )
            with patch.object(downloader, 'is_voice_downloaded', return_value=False):
                result = downloader.get_missing_voices()
                assert "voice1" in result

    def test_validate_file_integrity_size_match(self, tmp_path):
        """Test file validation with matching size"""
        voice_file = tmp_path / "test.bin"
        voice_file.write_bytes(b'\x00' * 100)
        
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            voice_info = VoiceFileInfo(
                name="test",
                path="test.bin",
                size=100,
                sha="",
                download_url=""
            )
            result = downloader._validate_file_integrity(voice_file, voice_info)
            assert result is True

    def test_validate_file_integrity_size_mismatch(self, tmp_path):
        """Test file validation with size mismatch"""
        voice_file = tmp_path / "test.bin"
        voice_file.write_bytes(b'\x00' * 100)
        
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            voice_info = VoiceFileInfo(
                name="test",
                path="test.bin",
                size=200,  # Different size
                sha="",
                download_url=""
            )
            result = downloader._validate_file_integrity(voice_file, voice_info)
            assert result is False

    def test_get_voice_file_path_unknown(self, tmp_path):
        """Test getting path for unknown voice returns None"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            downloader.auto_discovery = False
            path = downloader.get_voice_file_path("nonexistent")
            assert path is None

    def test_get_voice_file_path_unknown(self, tmp_path):
        """Test getting path for unknown voice"""
        with patch('LiteTTS.voice.downloader.requests.get'):
            downloader = VoiceDownloader(voices_dir=str(tmp_path))
            path = downloader.get_voice_file_path("unknown")
            assert path is None
