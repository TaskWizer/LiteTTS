#!/usr/bin/env python3
"""
Unit tests for cache manager
"""

import pytest

from LiteTTS.cache.manager import EnhancedCacheManager


class TestCacheManager:
    """Test cases for EnhancedCacheManager"""

    @pytest.fixture
    def cache(self):
        """Create cache manager instance"""
        return EnhancedCacheManager(cache_dir="/tmp/test_cache")

    def test_initialization(self, cache):
        """Test cache initializes correctly"""
        assert cache is not None
        assert hasattr(cache, 'memory_cache')
        assert hasattr(cache, 'stats')

    def test_put_and_get(self, cache):
        """Test basic put and get"""
        cache.put("key1", "value1")
        result = cache.get("key1")
        assert result == "value1"

    def test_get_nonexistent(self, cache):
        """Test getting nonexistent key"""
        result = cache.get("nonexistent")
        assert result is None

    def test_delete(self, cache):
        """Test deleting a key"""
        cache.put("key1", "value1")
        cache.delete("key1")
        result = cache.get("key1")
        assert result is None

    def test_stats_initial(self, cache):
        """Test initial cache statistics"""
        stats = cache.get_stats()
        assert 'memory_cache' in stats
        assert 'disk_cache' in stats


class TestCacheManagerEdgeCases:
    """Edge case tests for EnhancedCacheManager"""

    @pytest.fixture
    def cache(self):
        return EnhancedCacheManager(cache_dir="/tmp/test_cache_edge")

    def test_put_none_value(self, cache):
        """Test putting None value"""
        cache.put("key1", None)
        result = cache.get("key1")
        assert result is None

    def test_put_empty_string(self, cache):
        """Test putting empty string"""
        cache.put("key1", "")
        result = cache.get("key1")
        assert result == ""

    def test_update_existing_key(self, cache):
        """Test updating existing key"""
        cache.put("key1", "value1")
        cache.put("key1", "value2")
        result = cache.get("key1")
        assert result == "value2"

    def test_delete_nonexistent_key(self, cache):
        """Test deleting nonexistent key doesn't error"""
        cache.delete("nonexistent")  # Should not raise

    def test_clear(self, cache):
        """Test clearing cache"""
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
