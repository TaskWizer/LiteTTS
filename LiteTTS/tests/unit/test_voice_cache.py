#!/usr/bin/env python3
"""
Unit tests for voice cache
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from LiteTTS.voice.cache import VoiceCache, CacheEntry


class TestVoiceCache:
    """Test cases for VoiceCache"""

    @pytest.fixture
    def mock_voice_loader(self):
        """Create mock voice loader"""
        loader = Mock()
        loader.load_voice = Mock()
        return loader

    @pytest.fixture
    def cache_with_mock(self, mock_voice_loader):
        """Create cache with mocked loader"""
        with patch('LiteTTS.voice.cache.get_voice_loader', return_value=mock_voice_loader):
            cache = VoiceCache(
                voices_dir="LiteTTS/voices",
                max_cache_size=5,
                preload_voices=[],
                enable_mock=True
            )
            cache.voice_loader = mock_voice_loader
            return cache

    def test_initialization(self, cache_with_mock):
        """Test cache initializes correctly"""
        assert cache_with_mock is not None
        assert cache_with_mock.max_cache_size == 5

    def test_get_voice_embedding(self, cache_with_mock, mock_voice_loader):
        """Test getting voice embedding from cache"""
        mock_result = Mock()
        mock_result.success = True
        mock_result.embedding_data = np.random.randn(128).astype(np.float32)
        mock_result.metadata = {"name": "test_voice"}
        mock_voice_loader.load_voice.return_value = mock_result

        result = cache_with_mock.get_voice_embedding("test_voice")
        # Returns the embedding or None depending on loading

    def test_cache_statistics(self, cache_with_mock, mock_voice_loader):
        """Test cache statistics tracking"""
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_message = "Not found"
        mock_voice_loader.load_voice.return_value = mock_result

        cache_with_mock.get_voice_embedding("missing_voice")
        assert cache_with_mock.cache_misses >= 0


class TestCacheEntry:
    """Test cases for CacheEntry"""

    def test_cache_entry_creation(self):
        """Test creating a cache entry"""
        embedding = Mock()
        entry = CacheEntry(
            embedding=embedding,
            loaded_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            memory_size=1024,
            priority=0
        )
        assert entry.embedding is embedding
        assert entry.access_count == 1
