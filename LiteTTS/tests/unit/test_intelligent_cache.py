#!/usr/bin/env python3
"""
Unit tests for intelligent cache
"""

import pytest

from LiteTTS.cache.intelligent_cache import IntelligentCache


class TestIntelligentCache:
    """Test cases for IntelligentCache"""

    @pytest.fixture
    def cache(self):
        """Create intelligent cache instance"""
        return IntelligentCache(max_size=100, ttl_seconds=3600)

    def test_initialization(self, cache):
        """Test cache initializes correctly"""
        assert cache.max_size == 100
        assert cache.ttl_seconds == 3600
        assert cache.hit_count == 0
        assert cache.miss_count == 0

    def test_get_cache_key(self, cache):
        """Test generating cache key"""
        key1 = cache.get_cache_key("Hello world", "af_heart")
        key2 = cache.get_cache_key("Hello world", "af_heart")
        key3 = cache.get_cache_key("hello world", "af_heart")  # Different case
        assert key1 == key2  # Same text/voice = same key
        assert isinstance(key1, str)

    def test_get_nonexistent(self, cache):
        """Test getting nonexistent key"""
        result = cache.get("nonexistent_key")
        assert result is None

    def test_put_and_get(self, cache):
        """Test putting and getting data"""
        key = cache.get_cache_key("Test", "af_heart")
        cache.put(key, b"audio_data")
        result = cache.get(key)
        assert result == b"audio_data"

    def test_stats_initialization(self, cache):
        """Test performance stats are initialized"""
        stats = cache.performance_stats
        assert stats['cache_hits'] == 0
        assert stats['cache_misses'] == 0
        assert stats['hit_rate'] == 0.0
