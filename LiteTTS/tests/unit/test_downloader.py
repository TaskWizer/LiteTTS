#!/usr/bin/env python3
"""
Unit tests for downloader module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from LiteTTS.downloader import download_file, ensure_model_files, get_available_voices


class TestDownloadFile:
    """Test cases for download_file function"""

    def test_download_file_success(self, tmp_path):
        """Test successful file download with mocked requests"""
        url = "https://example.com/file.bin"
        filepath = tmp_path / "file.bin"

        with patch('LiteTTS.downloader.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.headers.get.return_value = '100'
            mock_response.iter_content.return_value = [b'test data' * 100]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = download_file(url, filepath, "test file")
            assert result is True
            assert filepath.exists()

    def test_download_file_already_exists(self, tmp_path):
        """Test download when file already exists"""
        url = "https://example.com/file.bin"
        filepath = tmp_path / "file.bin"
        filepath.write_bytes(b'existing data')

        with patch('LiteTTS.downloader.requests.get') as mock_get:
            result = download_file(url, filepath, "test file")
            assert result is True
            mock_get.assert_not_called()

    def test_download_file_network_error(self, tmp_path):
        """Test download with network error"""
        url = "https://example.com/file.bin"
        filepath = tmp_path / "file.bin"

        with patch('LiteTTS.downloader.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")

            result = download_file(url, filepath, "test file")
            assert result is False
            assert not filepath.exists()

    def test_download_file_http_error(self, tmp_path):
        """Test download with HTTP error"""
        url = "https://example.com/file.bin"
        filepath = tmp_path / "file.bin"

        with patch('LiteTTS.downloader.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")
            mock_get.return_value = mock_response

            result = download_file(url, filepath, "test file")
            assert result is False

    def test_download_file_creates_parent_dirs(self, tmp_path):
        """Test that download creates parent directories"""
        url = "https://example.com/file.bin"
        filepath = tmp_path / "subdir" / "nested" / "file.bin"

        with patch('LiteTTS.downloader.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.headers.get.return_value = '10'
            mock_response.iter_content.return_value = [b'test']
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = download_file(url, filepath, "test file")
            assert result is True
            assert filepath.exists()
            assert filepath.parent.exists()


class TestEnsureModelFiles:
    """Test cases for ensure_model_files function"""

    def test_ensure_model_files_success(self):
        """Test ensure_model_files with mocked dependencies"""
        with patch('LiteTTS.models.manager.ModelManager') as mock_model_mgr_class, \
             patch('LiteTTS.voice.downloader.VoiceDownloader') as mock_voice_dl_class, \
             patch('LiteTTS.config.config') as mock_config:

            # Setup config mock
            mock_config.paths.models_dir = "/tmp/models"
            mock_config.paths.voices_dir = "/tmp/voices"
            mock_config.model.default_variant = "base"

            # Setup model manager mock
            mock_model_instance = Mock()
            mock_model_instance.get_model_path.return_value = Path("/tmp/models/base")
            mock_model_instance.download_model.return_value = True
            mock_model_mgr_class.return_value = mock_model_instance

            # Setup voice downloader mock
            mock_voice_instance = Mock()
            mock_voice_instance.download_all_voices.return_value = {"af_heart": True, "am_puck": True}
            mock_voice_dl_class.return_value = mock_voice_instance

            result = ensure_model_files()
            assert result is True

    def test_ensure_model_files_model_download_fails(self):
        """Test ensure_model_files when model download fails"""
        with patch('LiteTTS.models.manager.ModelManager') as mock_model_mgr_class, \
             patch('LiteTTS.voice.downloader.VoiceDownloader') as mock_voice_dl_class, \
             patch('LiteTTS.config.config') as mock_config:

            mock_config.paths.models_dir = "/tmp/models"
            mock_config.paths.voices_dir = "/tmp/voices"
            mock_config.model.default_variant = "base"

            mock_model_instance = Mock()
            mock_model_instance.get_model_path.return_value = Path("/tmp/models/base")
            mock_model_instance.download_model.return_value = False
            mock_model_mgr_class.return_value = mock_model_instance

            mock_voice_instance = Mock()
            mock_voice_instance.download_all_voices.return_value = {"af_heart": True}
            mock_voice_dl_class.return_value = mock_voice_instance

            result = ensure_model_files()
            assert result is False

    def test_ensure_model_files_no_voices(self):
        """Test ensure_model_files when no voices downloaded"""
        with patch('LiteTTS.models.manager.ModelManager') as mock_model_mgr_class, \
             patch('LiteTTS.voice.downloader.VoiceDownloader') as mock_voice_dl_class, \
             patch('LiteTTS.config.config') as mock_config:

            mock_config.paths.models_dir = "/tmp/models"
            mock_config.paths.voices_dir = "/tmp/voices"
            mock_config.model.default_variant = "base"

            mock_model_instance = Mock()
            mock_model_instance.get_model_path.return_value = Path("/tmp/models/base")
            mock_model_instance.download_model.return_value = True
            mock_model_mgr_class.return_value = mock_model_instance

            mock_voice_instance = Mock()
            mock_voice_instance.download_all_voices.return_value = {}
            mock_voice_dl_class.return_value = mock_voice_instance

            result = ensure_model_files()
            assert result is False


class TestGetAvailableVoices:
    """Test cases for get_available_voices function"""

    def test_get_available_voices_success(self):
        """Test get_available_voices with mocked dependencies"""
        with patch('LiteTTS.voice.downloader.VoiceDownloader') as mock_voice_dl_class:
            mock_instance = Mock()
            mock_instance.get_available_voice_names.return_value = ["af_heart", "am_puck"]
            mock_voice_dl_class.return_value = mock_instance

            result = get_available_voices()
            assert result == ["af_heart", "am_puck"]

    def test_get_available_voices_handles_error(self):
        """Test get_available_voices handles errors gracefully"""
        with patch('LiteTTS.voice.downloader.VoiceDownloader', side_effect=Exception("Test error")):
            result = get_available_voices()
            assert result == []

    def test_get_available_voices_returns_list(self):
        """Test get_available_voices returns a list"""
        with patch('LiteTTS.voice.downloader.VoiceDownloader') as mock_voice_dl_class:
            mock_instance = Mock()
            mock_instance.get_available_voice_names.return_value = []
            mock_voice_dl_class.return_value = mock_instance

            result = get_available_voices()
            assert isinstance(result, list)
            assert result == []
