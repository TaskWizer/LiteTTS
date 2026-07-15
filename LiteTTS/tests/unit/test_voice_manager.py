#!/usr/bin/env python3
"""
Unit tests for voice manager module
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from LiteTTS.voice.manager import VoiceManager


class TestVoiceManager:
    """Test cases for VoiceManager class"""

    def test_initialization(self, tmp_path):
        """Test manager initializes correctly"""
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path))
            assert manager.voices_dir == tmp_path
            assert isinstance(manager.performance_stats, dict)

    def test_initialization_with_custom_cache_size(self, tmp_path):
        """Test initialization with custom cache size"""
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path), max_cache_size=20)
            assert manager is not None

    def test_initialization_default_strategy(self, tmp_path):
        """Test initialization uses loading strategy from config"""
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path))
            # Strategy comes from config, verify it's a valid string
            assert isinstance(manager.loading_strategy, str)
            assert manager.loading_strategy in ["individual", "batch", "combined"]

    def test_get_voice_embedding_from_cache(self, tmp_path):
        """Test getting voice embedding from cache"""
        mock_cache = Mock()
        mock_cache.get_voice_embedding.return_value = Mock()
        mock_cache.get_voice_embedding.return_value.name = "test_voice"
        
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache', return_value=mock_cache):
            manager = VoiceManager(voices_dir=str(tmp_path))
            manager.performance_monitoring = False
            result = manager.get_voice_embedding("test_voice")
            assert result is not None

    def test_get_voice_embedding_cache_miss_hf_voice(self, tmp_path):
        """Test cache miss for HuggingFace voice"""
        mock_downloader = Mock()
        mock_downloader.discovered_voices = {"hf_voice": {}}
        mock_downloader.is_voice_downloaded.return_value = False
        
        mock_cache = Mock()
        mock_cache.get_voice_embedding.return_value = None  # Cache miss
        
        with patch('LiteTTS.voice.manager.VoiceDownloader', return_value=mock_downloader), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache', return_value=mock_cache):
            manager = VoiceManager(voices_dir=str(tmp_path))
            manager.performance_monitoring = False
            result = manager.get_voice_embedding("hf_voice")
            # Should try to download since not in cache and not downloaded
            mock_downloader.download_voice.assert_called()

    def test_get_voice_embedding_custom_voice(self, tmp_path):
        """Test getting custom voice (non-HuggingFace)"""
        mock_downloader = Mock()
        mock_downloader.discovered_voices = {}
        
        mock_cache = Mock()
        mock_cache.get_voice_embedding.return_value = None
        
        with patch('LiteTTS.voice.manager.VoiceDownloader', return_value=mock_downloader), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache', return_value=mock_cache):
            manager = VoiceManager(voices_dir=str(tmp_path))
            manager.performance_monitoring = False
            # Create a fake voice file
            (tmp_path / "custom_voice.bin").write_bytes(b'\x00' * 1000)
            result = manager.get_voice_embedding("custom_voice")
            # Cache miss, HF voice not found, but custom voice exists

    def test_download_voice_success(self, tmp_path):
        """Test successful voice download"""
        mock_downloader = Mock()
        mock_downloader.download_voice.return_value = True
        
        mock_validator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validator.validate_voice.return_value = mock_validation_result
        
        mock_cache = Mock()
        mock_cache.preload_voice.return_value = True
        
        with patch('LiteTTS.voice.manager.VoiceDownloader', return_value=mock_downloader), \
             patch('LiteTTS.voice.manager.VoiceValidator', return_value=mock_validator), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache', return_value=mock_cache):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.download_voice("test_voice")
            assert result is True

    def test_download_voice_validation_failure(self, tmp_path):
        """Test voice download with validation failure"""
        mock_downloader = Mock()
        mock_downloader.download_voice.return_value = True
        
        mock_validator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.errors = ["Invalid voice file"]
        mock_validator.validate_voice.return_value = mock_validation_result
        
        with patch('LiteTTS.voice.manager.VoiceDownloader', return_value=mock_downloader), \
             patch('LiteTTS.voice.manager.VoiceValidator', return_value=mock_validator), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.download_voice("test_voice")
            assert result is False

    def test_validate_voice(self, tmp_path):
        """Test voice validation"""
        mock_validator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validator.validate_voice.return_value = mock_validation_result
        
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator', return_value=mock_validator), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.validate_voice("test_voice")
            assert result.is_valid is True

    def test_validate_all_voices(self, tmp_path):
        """Test validating all voices"""
        mock_validator = Mock()
        mock_validator.validate_all_voices.return_value = {"voice1": Mock(is_valid=True)}
        
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator', return_value=mock_validator), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path))
            results = manager.validate_all_voices()
            assert "voice1" in results

    def test_get_available_voices(self, tmp_path):
        """Test getting available voices"""
        mock_downloader = Mock()
        mock_downloader.discovered_voices = {"hf_voice": {}}
        mock_downloader.is_voice_downloaded.return_value = True
        
        with patch('LiteTTS.voice.manager.VoiceDownloader', return_value=mock_downloader), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path))
            manager.is_voice_ready = Mock(return_value=True)
            voices = manager.get_available_voices()
            assert isinstance(voices, list)

    def test_is_voice_ready_hf_voice(self, tmp_path):
        """Test checking if HuggingFace voice is ready"""
        mock_downloader = Mock()
        mock_downloader.discovered_voices = {"hf_voice": {}}
        mock_downloader.is_voice_downloaded.return_value = True
        
        mock_validator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validator.validate_voice.return_value = mock_validation_result
        
        with patch('LiteTTS.voice.manager.VoiceDownloader', return_value=mock_downloader), \
             patch('LiteTTS.voice.manager.VoiceValidator', return_value=mock_validator), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.is_voice_ready("hf_voice")
            assert result is True

    def test_is_voice_ready_not_downloaded(self, tmp_path):
        """Test checking voice that's not downloaded"""
        mock_downloader = Mock()
        mock_downloader.discovered_voices = {"hf_voice": {}}
        mock_downloader.is_voice_downloaded.return_value = False
        
        with patch('LiteTTS.voice.manager.VoiceDownloader', return_value=mock_downloader), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.is_voice_ready("hf_voice")
            assert result is False

    def test_get_voice_metadata(self, tmp_path):
        """Test getting voice metadata"""
        mock_metadata_manager = Mock()
        mock_metadata_manager.get_voice_metadata.return_value = Mock()
        
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager', return_value=mock_metadata_manager), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.get_voice_metadata("test_voice")
            assert result is not None

    def test_filter_voices(self, tmp_path):
        """Test filtering voices"""
        mock_metadata_manager = Mock()
        mock_metadata_manager.filter_voices.return_value = []
        
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager', return_value=mock_metadata_manager), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.filter_voices(gender="female")
            assert isinstance(result, list)

    def test_get_recommended_voices(self, tmp_path):
        """Test getting recommended voices"""
        mock_metadata_manager = Mock()
        mock_metadata_manager.get_recommended_voices.return_value = []
        
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager', return_value=mock_metadata_manager), \
             patch('LiteTTS.voice.manager.VoiceCache'):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.get_recommended_voices(count=3)
            assert isinstance(result, list)

    def test_preload_voice(self, tmp_path):
        """Test preloading a voice"""
        mock_cache = Mock()
        mock_cache.preload_voice.return_value = True
        
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache', return_value=mock_cache):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.preload_voice("test_voice")
            assert result is True

    def test_preload_voices_batch(self, tmp_path):
        """Test preloading multiple voices"""
        mock_cache = Mock()
        mock_cache.preload_voices_batch.return_value = {"v1": True, "v2": True}
        
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache', return_value=mock_cache):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.preload_voices(["v1", "v2"])
            assert result["v1"] is True

    def test_is_voice_cached(self, tmp_path):
        """Test checking if voice is cached"""
        mock_cache = Mock()
        mock_cache.is_voice_cached.return_value = True
        
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache', return_value=mock_cache):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.is_voice_cached("test_voice")
            assert result is True

    def test_get_cached_voices(self, tmp_path):
        """Test getting list of cached voices"""
        mock_cache = Mock()
        mock_cache.get_cached_voices.return_value = ["voice1", "voice2"]
        
        with patch('LiteTTS.voice.manager.VoiceDownloader'), \
             patch('LiteTTS.voice.manager.VoiceValidator'), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager'), \
             patch('LiteTTS.voice.manager.VoiceCache', return_value=mock_cache):
            manager = VoiceManager(voices_dir=str(tmp_path))
            result = manager.get_cached_voices()
            assert len(result) == 2

    def test_get_system_status(self, tmp_path):
        """Test getting system status"""
        mock_downloader = Mock()
        mock_downloader.discovered_voices = {"v1": {}, "v2": {}}
        mock_downloader.get_download_info.return_value = {"v1": {"downloaded": True}, "v2": {"downloaded": False}}
        
        mock_validator = Mock()
        mock_validator.validate_all_voices.return_value = {
            "v1": Mock(is_valid=True),
            "v2": Mock(is_valid=False)
        }
        
        mock_cache = Mock()
        mock_cache.get_cache_stats.return_value = {
            "size": 5, "max_size": 10,
            "cached_voices": ["v1", "v2"],
            "cache_hits": 10, "hit_rate": 0.8
        }

        mock_metadata_manager = Mock()
        mock_metadata_manager.get_usage_summary.return_value = {"total_requests": 100}

        with patch('LiteTTS.voice.manager.VoiceDownloader', return_value=mock_downloader), \
             patch('LiteTTS.voice.manager.VoiceValidator', return_value=mock_validator), \
             patch('LiteTTS.voice.manager.VoiceMetadataManager', return_value=mock_metadata_manager), \
             patch('LiteTTS.voice.manager.VoiceCache', return_value=mock_cache):
            manager = VoiceManager(voices_dir=str(tmp_path))
            status = manager.get_system_status()
            assert 'voices' in status
            assert 'cache_stats' in status
            assert 'usage_stats' in status
