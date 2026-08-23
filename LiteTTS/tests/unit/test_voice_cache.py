#!/usr/bin/env python3
"""
Unit tests for voice cache module
"""

from datetime import datetime
from unittest.mock import Mock, patch

import numpy as np

from LiteTTS.voice.cache import CacheEntry, VoiceCache, VoiceEmbedding, VoiceMetadata


class TestCacheEntry:
    """Test cases for CacheEntry dataclass"""

    def test_creation(self):
        """Test creating a cache entry"""
        metadata = VoiceMetadata(name="test_voice", gender="female")
        embedding = VoiceEmbedding(
            name="test_voice",
            embedding_data=np.array([1.0, 2.0, 3.0]),
            metadata=metadata
        )
        entry = CacheEntry(
            embedding=embedding,
            loaded_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=5,
            memory_size=1024,
            priority=1
        )
        assert entry.embedding.name == "test_voice"
        assert entry.access_count == 5
        assert entry.memory_size == 1024
        assert entry.priority == 1

    def test_creation_defaults(self):
        """Test creating cache entry with defaults"""
        metadata = VoiceMetadata(name="test_voice", gender="female")
        embedding = VoiceEmbedding(name="test_voice", embedding_data=np.array([1.0]))
        entry = CacheEntry(
            embedding=embedding,
            loaded_at=datetime.now(),
            last_accessed=datetime.now()
        )
        assert entry.access_count == 0
        assert entry.memory_size == 0
        assert entry.priority == 0


class TestVoiceCache:
    """Test cases for VoiceCache class"""

    def test_initialization_default(self, tmp_path):
        """Test initialization with defaults"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader
            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)
            assert cache.voices_dir == tmp_path
            assert cache.max_cache_size == 5
            assert isinstance(cache.cache, dict)

    def test_initialization_custom_max_size(self, tmp_path):
        """Test initialization with custom max cache size"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader
            cache = VoiceCache(voices_dir=str(tmp_path), max_cache_size=10, enable_mock=True)
            assert cache.max_cache_size == 10

    def test_initialization_custom_preload_voices(self, tmp_path):
        """Test initialization with custom preload voices"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader
            cache = VoiceCache(
                voices_dir=str(tmp_path),
                preload_voices=["voice1", "voice2"],
                enable_mock=True
            )
            assert "voice1" in cache.preload_voices
            assert "voice2" in cache.preload_voices

    def test_initialization_fallback_voices_dir(self, tmp_path):
        """Test initialization uses fallback voices_dir when not provided"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader
            with patch('LiteTTS.config.config') as mock_config:
                mock_config.paths.voices_dir = str(tmp_path)
                with patch.object(VoiceCache, '_initialize_cache'):
                    cache = VoiceCache(enable_mock=True)
                    assert cache.voices_dir == tmp_path

    def test_cache_lock_exists(self, tmp_path):
        """Test that cache lock is initialized"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader
            with patch.object(VoiceCache, '_initialize_cache'):
                cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)
                assert cache.cache_lock is not None

    def test_cache_statistics_initialized(self, tmp_path):
        """Test that cache statistics are initialized"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader
            with patch.object(VoiceCache, '_initialize_cache'):
                cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)
                assert cache.cache_hits == 0
                assert cache.cache_misses == 0
                assert cache.total_loads == 0

    def test_get_voice_embedding_cache_hit(self, tmp_path):
        """Test getting voice embedding from cache (cache hit)"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            metadata = VoiceMetadata(name="test_voice", gender="female")
            embedding = VoiceEmbedding(
                name="test_voice",
                embedding_data=np.array([1.0, 2.0, 3.0]),
                metadata=metadata
            )
            entry = CacheEntry(
                embedding=embedding,
                loaded_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                memory_size=100,
                priority=0
            )
            cache.cache["test_voice"] = entry

            result = cache.get_voice_embedding("test_voice")

            assert result is not None
            assert result.name == "test_voice"
            assert cache.cache_hits == 1

    def test_get_voice_embedding_cache_miss(self, tmp_path):
        """Test getting voice embedding when not in cache (cache miss)"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            mock_load_result = Mock()
            mock_load_result.success = True
            mock_load_result.embedding_data = np.array([1.0, 2.0, 3.0])
            mock_load_result.metadata = {"name": "new_voice"}
            mock_load_result.loader_used = "mock"
            mock_loader.load_voice.return_value = mock_load_result

            with patch.object(VoiceCache, '_initialize_cache'):
                cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            result = cache.get_voice_embedding("new_voice")

            assert result is not None
            assert cache.cache_misses == 1
            mock_loader.load_voice.assert_called_with("new_voice")

    def test_get_voice_embedding_load_failure(self, tmp_path):
        """Test getting voice when load fails"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            mock_load_result = Mock()
            mock_load_result.success = False
            mock_load_result.error_message = "File not found"
            mock_loader.load_voice.return_value = mock_load_result

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            result = cache.get_voice_embedding("missing_voice")

            assert result is None

    def test_get_voice_embedding_no_embedding_data(self, tmp_path):
        """Test getting voice when no embedding data returned"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            mock_load_result = Mock()
            mock_load_result.success = True
            mock_load_result.embedding_data = None
            mock_load_result.metadata = {}
            mock_load_result.loader_used = "mock"
            mock_loader.load_voice.return_value = mock_load_result

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            result = cache.get_voice_embedding("empty_voice")

            assert result is None

    def test_preload_voice_success(self, tmp_path):
        """Test preloading a voice successfully"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            mock_load_result = Mock()
            mock_load_result.success = True
            mock_load_result.embedding_data = np.array([1.0, 2.0, 3.0])
            mock_load_result.metadata = {"name": "new_voice"}
            mock_load_result.loader_used = "mock"
            mock_loader.load_voice.return_value = mock_load_result

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            result = cache.preload_voice("new_voice")

            assert result is True
            assert "new_voice" in cache.cache
            assert "new_voice" in cache.preload_voices

    def test_preload_voice_already_cached(self, tmp_path):
        """Test preloading voice that's already cached"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            with patch.object(VoiceCache, '_initialize_cache'):
                cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            metadata = VoiceMetadata(name="cached_voice", gender="female")
            embedding = VoiceEmbedding(name="cached_voice", embedding_data=np.array([1.0]))
            entry = CacheEntry(
                embedding=embedding,
                loaded_at=datetime.now(),
                last_accessed=datetime.now()
            )
            cache.cache["cached_voice"] = entry

            result = cache.preload_voice("cached_voice")

            assert result is True
            mock_loader.load_voice.assert_not_called()

    def test_preload_voice_failure(self, tmp_path):
        """Test preloading voice that fails to load"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            mock_load_result = Mock()
            mock_load_result.success = False
            mock_load_result.error_message = "Load failed"
            mock_loader.load_voice.return_value = mock_load_result

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            result = cache.preload_voice("failing_voice")

            assert result is False

    def test_preload_voices_batch(self, tmp_path):
        """Test batch preloading multiple voices"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            mock_load_result = Mock()
            mock_load_result.success = True
            mock_load_result.embedding_data = np.array([1.0, 2.0, 3.0])
            mock_load_result.metadata = {}
            mock_load_result.loader_used = "mock"
            mock_loader.load_voice.return_value = mock_load_result

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            results = cache.preload_voices_batch(["voice1", "voice2"])

            assert "voice1" in results
            assert "voice2" in results

    def test_is_voice_cached(self, tmp_path):
        """Test checking if voice is cached"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            metadata = VoiceMetadata(name="cached_voice", gender="female")
            embedding = VoiceEmbedding(name="cached_voice", embedding_data=np.array([1.0]))
            entry = CacheEntry(
                embedding=embedding,
                loaded_at=datetime.now(),
                last_accessed=datetime.now()
            )
            cache.cache["cached_voice"] = entry

            assert cache.is_voice_cached("cached_voice") is True
            assert cache.is_voice_cached("uncached_voice") is False

    def test_get_cached_voices(self, tmp_path):
        """Test getting list of cached voices"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            for name in ["voice1", "voice2", "voice3"]:
                metadata = VoiceMetadata(name=name, gender="female")
                embedding = VoiceEmbedding(name=name, embedding_data=np.array([1.0]))
                entry = CacheEntry(
                    embedding=embedding,
                    loaded_at=datetime.now(),
                    last_accessed=datetime.now()
                )
                cache.cache[name] = entry

            voices = cache.get_cached_voices()

            assert len(voices) == 3
            assert "voice1" in voices
            assert "voice2" in voices
            assert "voice3" in voices

    def test_evict_voice(self, tmp_path):
        """Test manually evicting a voice"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            metadata = VoiceMetadata(name="evict_me", gender="female")
            embedding = VoiceEmbedding(name="evict_me", embedding_data=np.array([1.0]))
            entry = CacheEntry(
                embedding=embedding,
                loaded_at=datetime.now(),
                last_accessed=datetime.now()
            )
            cache.cache["evict_me"] = entry

            result = cache.evict_voice("evict_me")

            assert result is True
            assert "evict_me" not in cache.cache

    def test_evict_voice_not_cached(self, tmp_path):
        """Test evicting voice that's not cached"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            result = cache.evict_voice("nonexistent")

            assert result is False

    def test_clear_cache_keep_preloaded(self, tmp_path):
        """Test clearing cache while keeping preloaded voices"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), preload_voices=["preloaded1"], enable_mock=True)

            metadata1 = VoiceMetadata(name="preloaded1", gender="female")
            embedding1 = VoiceEmbedding(name="preloaded1", embedding_data=np.array([1.0]))
            entry1 = CacheEntry(
                embedding=embedding1,
                loaded_at=datetime.now(),
                last_accessed=datetime.now()
            )
            cache.cache["preloaded1"] = entry1

            metadata2 = VoiceMetadata(name="non_preloaded", gender="female")
            embedding2 = VoiceEmbedding(name="non_preloaded", embedding_data=np.array([1.0]))
            entry2 = CacheEntry(
                embedding=embedding2,
                loaded_at=datetime.now(),
                last_accessed=datetime.now()
            )
            cache.cache["non_preloaded"] = entry2

            cache.clear_cache(keep_preloaded=True)

            assert "preloaded1" in cache.cache
            assert "non_preloaded" not in cache.cache

    def test_clear_cache_no_keep(self, tmp_path):
        """Test clearing entire cache"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            for name in ["voice1", "voice2"]:
                metadata = VoiceMetadata(name=name, gender="female")
                embedding = VoiceEmbedding(name=name, embedding_data=np.array([1.0]))
                entry = CacheEntry(
                    embedding=embedding,
                    loaded_at=datetime.now(),
                    last_accessed=datetime.now()
                )
                cache.cache[name] = entry

            cache.clear_cache(keep_preloaded=False)

            assert len(cache.cache) == 0

    def test_get_cache_stats(self, tmp_path):
        """Test getting cache statistics"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), max_cache_size=10, enable_mock=True)

            metadata = VoiceMetadata(name="test_voice", gender="female")
            embedding = VoiceEmbedding(name="test_voice", embedding_data=np.array([1.0, 2.0, 3.0]))
            entry = CacheEntry(
                embedding=embedding,
                loaded_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=5,
                memory_size=1024
            )
            cache.cache["test_voice"] = entry
            cache.cache_hits = 10
            cache.cache_misses = 2

            stats = cache.get_cache_stats()

            assert stats['cached_voices'] == 1
            assert stats['max_cache_size'] == 10
            assert stats['cache_hits'] == 10
            assert stats['cache_misses'] == 2
            assert 'test_voice' in stats['voice_details']

    def test_optimize_cache(self, tmp_path):
        """Test optimizing cache preload list"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            for name, count in [("low", 1), ("med", 5), ("high", 10)]:
                metadata = VoiceMetadata(name=name, gender="female")
                embedding = VoiceEmbedding(name=name, embedding_data=np.array([1.0]))
                entry = CacheEntry(
                    embedding=embedding,
                    loaded_at=datetime.now(),
                    last_accessed=datetime.now(),
                    access_count=count
                )
                cache.cache[name] = entry

            cache.optimize_cache()

            assert "high" in cache.preload_voices

    def test_validate_cache_integrity_all_valid(self, tmp_path):
        """Test validating cache integrity when all entries are valid"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            valid_data = np.array([1.0, 2.0, 3.0], dtype=np.float32)
            metadata = VoiceMetadata(name="valid_voice", gender="female")
            embedding = VoiceEmbedding(
                name="valid_voice",
                embedding_data=valid_data,
                metadata=metadata,
                file_hash="abc123"
            )
            entry = CacheEntry(
                embedding=embedding,
                loaded_at=datetime.now(),
                last_accessed=datetime.now()
            )
            cache.cache["valid_voice"] = entry

            # Mock torch.isnan and torch.isinf to return False for both calls
            with patch('torch.isnan', return_value=False), \
                 patch('torch.isinf', return_value=False), \
                 patch('torch.any', return_value=False):
                results = cache.validate_cache_integrity()

            assert results["valid_voice"] is True

    def test_validate_cache_integrity_with_nan(self, tmp_path):
        """Test validating cache detects NaN values"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            nan_data = np.array([float('nan'), 2.0, 3.0], dtype=np.float32)
            metadata = VoiceMetadata(name="nan_voice", gender="female")
            embedding = VoiceEmbedding(
                name="nan_voice",
                embedding_data=nan_data,
                metadata=metadata
            )
            entry = CacheEntry(
                embedding=embedding,
                loaded_at=datetime.now(),
                last_accessed=datetime.now()
            )
            cache.cache["nan_voice"] = entry

            with patch('torch.any', return_value=True):
                results = cache.validate_cache_integrity()

            assert results["nan_voice"] is False
            assert "nan_voice" not in cache.cache

    def test_optimize_for_individual_files(self, tmp_path):
        """Test optimizing cache for individual file loading"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), max_cache_size=3, enable_mock=True)

            for name in ["voice1", "voice2"]:
                metadata = VoiceMetadata(name=name, gender="female")
                embedding = VoiceEmbedding(name=name, embedding_data=np.array([1.0]))
                entry = CacheEntry(
                    embedding=embedding,
                    loaded_at=datetime.now(),
                    last_accessed=datetime.now()
                )
                cache.cache[name] = entry

            cache.optimize_for_individual_files()

            assert cache.max_cache_size >= 5

    def test_calculate_file_hash_safe_with_existing_file(self, tmp_path):
        """Test calculating file hash for existing file"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            voice_file = tmp_path / "test_voice.pt"
            voice_file.write_bytes(b'\x00' * 100)

            hash_result = cache._calculate_file_hash_safe("test_voice", {})

            assert hash_result is not None
            assert len(hash_result) > 0

    def test_calculate_file_hash_safe_fallback(self, tmp_path):
        """Test calculating file hash falls back to voice name"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            hash_result = cache._calculate_file_hash_safe("no_file_voice", {"loader_used": "mock"})

            assert hash_result is not None
            assert len(hash_result) > 0

    def test_get_loader_statistics(self, tmp_path):
        """Test getting loader statistics"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_loader.get_load_statistics.return_value = {"total_loads": 5}
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            stats = cache.get_loader_statistics()

            assert stats["total_loads"] == 5

    def test_get_loader_statistics_no_method(self, tmp_path):
        """Test getting loader statistics when method doesn't exist"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            del mock_loader.get_load_statistics
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), enable_mock=True)

            stats = cache.get_loader_statistics()

            assert stats == {}

    def test_manage_cache_size_eviction(self, tmp_path):
        """Test that cache size management evicts LRU entries"""
        with patch('LiteTTS.voice.cache.get_voice_loader') as mock_get_loader:
            mock_loader = Mock()
            mock_get_loader.return_value = mock_loader

            cache = VoiceCache(voices_dir=str(tmp_path), max_cache_size=2, enable_mock=True)

            for name in ["voice1", "voice2", "voice3"]:
                metadata = VoiceMetadata(name=name, gender="female")
                embedding = VoiceEmbedding(name=name, embedding_data=np.array([1.0]))
                entry = CacheEntry(
                    embedding=embedding,
                    loaded_at=datetime.now(),
                    last_accessed=datetime.now(),
                    priority=0
                )
                cache.cache[name] = entry

            cache._manage_cache_size()

            assert len(cache.cache) <= 2
