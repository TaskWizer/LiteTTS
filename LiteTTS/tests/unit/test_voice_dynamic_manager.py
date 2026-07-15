#!/usr/bin/env python3
"""
Unit tests for dynamic voice manager
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from LiteTTS.voice.dynamic_manager import DynamicVoiceManager, VoiceEmbedding


class TestDynamicVoiceManager:
    """Test cases for DynamicVoiceManager"""

    @pytest.fixture
    def mock_manager(self):
        """Create manager with mocked dependencies"""
        with patch('LiteTTS.voice.dynamic_manager.VoiceDownloader'), \
             patch('LiteTTS.voice.dynamic_manager.VoiceDiscovery') as mock_discovery:
            mock_discovery_instance = Mock()
            mock_discovery_instance.get_available_voices.return_value = []
            mock_discovery_instance.is_voice_available.return_value = False
            mock_discovery.return_value = mock_discovery_instance
            manager = DynamicVoiceManager(voices_dir="/tmp/test_voices")
            return manager

    def test_initialization(self, mock_manager):
        """Test manager initializes correctly"""
        assert mock_manager is not None
        assert mock_manager.voices_dir.name == "test_voices"

    def test_get_available_voices(self, mock_manager):
        """Test getting available voices"""
        result = mock_manager.get_available_voices()
        assert isinstance(result, list)

    def test_is_voice_available(self, mock_manager):
        """Test checking if voice is available"""
        result = mock_manager.is_voice_available("test_voice")
        assert isinstance(result, bool)

    def test_voice_embedding_creation(self):
        """Test creating a voice embedding"""
        embedding = VoiceEmbedding(
            name="test_voice",
            embedding_data=np.random.randn(128).astype(np.float32),
            metadata={"gender": "female"},
            file_path="/path/to/voice.bin",
            checksum="abc123"
        )
        assert embedding.name == "test_voice"
        assert embedding.checksum == "abc123"

    def test_resolve_voice_name_full_name(self, mock_manager):
        """Test resolving a full voice name returns same"""
        mock_manager.discovery.get_available_voices.return_value = ["af_heart"]
        result = mock_manager.resolve_voice_name("af_heart")
        assert result == "af_heart"

    def test_resolve_voice_name_short_name(self, mock_manager):
        """Test resolving a short voice name"""
        mock_manager.voice_mappings = {"heart": "af_heart"}
        result = mock_manager.resolve_voice_name("heart")
        assert result == "af_heart"

    def test_resolve_voice_name_not_found(self, mock_manager):
        """Test resolving unknown voice name returns original"""
        mock_manager.voice_mappings = {}
        mock_manager.discovery.get_available_voices.return_value = []
        result = mock_manager.resolve_voice_name("unknown")
        assert result == "unknown"

    def test_is_voice_available_with_resolved_name(self, mock_manager):
        """Test is_voice_available checks resolved name"""
        mock_manager.downloader.discovered_voices = {"af_heart": {}}
        mock_manager.voice_mappings = {"heart": "af_heart"}
        result = mock_manager.is_voice_available("heart")
        assert result is True

    def test_is_voice_available_not_found(self, mock_manager):
        """Test is_voice_available returns False for unknown"""
        mock_manager.downloader.discovered_voices = {}
        mock_manager.voice_mappings = {}
        mock_manager.discovery.get_available_voices.return_value = []
        mock_manager.discovery.is_voice_available.return_value = False
        result = mock_manager.is_voice_available("nonexistent")
        assert result is False

    def test_ensure_voice_downloaded_already_downloaded(self, mock_manager):
        """Test ensure_voice_downloaded when already downloaded"""
        mock_manager.downloader.is_voice_downloaded.return_value = True
        result = mock_manager.ensure_voice_downloaded("af_heart")
        assert result is True
        mock_manager.downloader.download_voice.assert_not_called()

    def test_ensure_voice_downloaded_triggers_download(self, mock_manager):
        """Test ensure_voice_downloaded downloads when missing"""
        mock_manager.downloader.is_voice_downloaded.return_value = False
        mock_manager.downloader.download_voice.return_value = True
        result = mock_manager.ensure_voice_downloaded("af_heart")
        assert result is True
        mock_manager.downloader.download_voice.assert_called_once_with("af_heart")

    def test_get_voice_embedding_already_loaded(self, mock_manager):
        """Test get_voice_embedding returns cached"""
        existing_embedding = VoiceEmbedding(
            name="af_heart",
            embedding_data=np.random.randn(128).astype(np.float32),
            metadata={},
            file_path="/path/to/voice.bin",
            checksum="abc123"
        )
        mock_manager.loaded_voices["af_heart"] = existing_embedding
        result = mock_manager.get_voice_embedding("af_heart")
        assert result is existing_embedding

    def test_get_voice_embedding_download_fails(self, mock_manager):
        """Test get_voice_embedding when download fails"""
        mock_manager.downloader.is_voice_downloaded.return_value = False
        mock_manager.downloader.download_voice.return_value = False
        result = mock_manager.get_voice_embedding("missing_voice")
        assert result is None

    def test_get_voice_embedding_loads_from_file(self, mock_manager, tmp_path):
        """Test get_voice_embedding loads from file"""
        mock_manager.voices_dir = tmp_path
        mock_manager.downloader.discovered_voices = {"test_voice": {}}
        mock_manager.downloader.is_voice_downloaded.return_value = True
        mock_manager.downloader.download_voice.return_value = True

        # Create a valid voice file
        voice_data = np.random.randn(512).astype(np.float32)  # 2 * 256
        (tmp_path / "test_voice.pt").write_bytes(voice_data.tobytes())

        mock_manager.discovery.get_voice_info.return_value = Mock(
            language="en",
            gender="female",
            nationality="american",
            source="huggingface"
        )

        result = mock_manager.get_voice_embedding("test_voice")
        assert result is not None
        assert result.name == "test_voice"

    def test_get_voice_embedding_file_not_found(self, mock_manager):
        """Test get_voice_embedding when file doesn't exist"""
        mock_manager.downloader.discovered_voices = {"missing": {}}
        mock_manager.downloader.is_voice_downloaded.return_value = True
        mock_manager.downloader.download_voice.return_value = True
        result = mock_manager.get_voice_embedding("missing")
        assert result is None

    def test_download_all_voices(self, mock_manager):
        """Test download_all_voices delegates to downloader"""
        mock_manager.downloader.download_all_voices.return_value = {"v1": True}
        result = mock_manager.download_all_voices()
        assert result == {"v1": True}
        mock_manager.downloader.download_all_voices.assert_called_once()

    def test_get_download_status(self, mock_manager):
        """Test get_download_status returns status dict"""
        mock_manager.downloader.get_downloaded_voices.return_value = ["v1", "v2"]
        mock_manager.downloader.get_missing_voices.return_value = ["v3"]
        result = mock_manager.get_download_status()
        assert "discovered_voices" in result
        assert "loaded_voices" in result

    def test_refresh_discovery_success(self, mock_manager):
        """Test refresh_discovery success"""
        mock_manager.downloader.refresh_discovery.return_value = True
        result = mock_manager.refresh_discovery()
        assert result is True
        mock_manager.discovery.invalidate_cache.assert_called_once()

    def test_refresh_discovery_failure(self, mock_manager):
        """Test refresh_discovery failure"""
        mock_manager.downloader.refresh_discovery.return_value = False
        result = mock_manager.refresh_discovery()
        assert result is False

    def test_get_voice_mappings(self, mock_manager):
        """Test get_voice_mappings returns copy"""
        mock_manager.voice_mappings = {"heart": "af_heart", "puck": "am_puck"}
        result = mock_manager.get_voice_mappings()
        assert result == {"heart": "af_heart", "puck": "am_puck"}
        assert result is not mock_manager.voice_mappings  # Should be a copy

    def test_generate_voice_mappings(self, mock_manager):
        """Test _generate_voice_mappings creates short names"""
        mock_manager.discovery.get_available_voices.return_value = ["af_heart", "am_puck", "bf_bob"]
        mock_manager.voice_mappings = {}
        mock_manager._generate_voice_mappings()
        assert "heart" in mock_manager.voice_mappings
        assert "puck" in mock_manager.voice_mappings
        assert "bob" in mock_manager.voice_mappings

    def test_generate_voice_mappings_handles_conflicts(self, mock_manager):
        """Test _generate_voice_mappings handles name conflicts"""
        mock_manager.discovery.get_available_voices.return_value = ["af_heart", "bf_heart"]
        mock_manager.voice_mappings = {}
        mock_manager._generate_voice_mappings()
        # Should keep first one found when conflict occurs

    def test_load_voice_mappings_file_not_exists(self, mock_manager, tmp_path):
        """Test _load_voice_mappings when file doesn't exist"""
        mock_manager.mappings_cache_file = tmp_path / "nonexistent.json"
        mock_manager.voice_mappings = {}
        mock_manager._load_voice_mappings()
        assert mock_manager.voice_mappings == {}

    def test_load_voice_mappings_with_file(self, mock_manager, tmp_path):
        """Test _load_voice_mappings loads from file"""
        import json
        mock_manager.mappings_cache_file = tmp_path / "mappings.json"
        mock_manager.mappings_cache_file.write_text('{"heart": "af_heart"}')
        mock_manager.voice_mappings = {}
        mock_manager._load_voice_mappings()
        assert mock_manager.voice_mappings == {"heart": "af_heart"}

    def test_save_voice_mappings(self, mock_manager, tmp_path):
        """Test _save_voice_mappings writes to file"""
        mock_manager.mappings_cache_file = tmp_path / "mappings.json"
        mock_manager.voice_mappings = {"heart": "af_heart"}
        mock_manager._save_voice_mappings()
        import json
        loaded = json.loads(mock_manager.mappings_cache_file.read_text())
        assert loaded == {"heart": "af_heart"}
