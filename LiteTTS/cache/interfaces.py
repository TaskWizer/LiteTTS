#!/usr/bin/env python3
"""
Cache interfaces for LiteTTS.

This module defines the common interfaces that all cache implementations must follow.
Consolidating cache implementations reduces code duplication and ensures consistent behavior.

Interface Hierarchy:
- ICache[T] - Base cache interface (get, set, delete, clear)
- ILRUCache[T] - LRU cache interface (with eviction policy)
- ITypedCache[T] - Typed cache with key generation
"""

from abc import ABC, abstractmethod
from collections import OrderedDict
from threading import RLock
from typing import Any, Generic, TypeVar

T = TypeVar("T")

logger = __import__("logging").getLogger(__name__)


class ICache(ABC, Generic[T]):
    """Base interface for all cache implementations"""

    @abstractmethod
    def get(self, key: str) -> T | None:
        """Get value from cache"""
        pass

    @abstractmethod
    def set(self, key: str, value: T) -> None:
        """Set value in cache"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all values from cache"""
        pass

    @abstractmethod
    def size(self) -> int:
        """Get number of items in cache"""
        pass

    @abstractmethod
    def stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        pass


class ILRUCache(ICache[T]):
    """LRU (Least Recently Used) cache interface with eviction"""

    @abstractmethod
    def set_max_size(self, max_size: int) -> None:
        """Set maximum cache size"""
        pass

    @abstractmethod
    def get_max_size(self) -> int:
        """Get maximum cache size"""
        pass


class LRUCache(ILRUCache[T]):
    """
    Thread-safe LRU cache implementation using OrderedDict.

    This provides a base implementation that can be specialized for different
    cache types (voice, tokenization, audio, etc.).

    Architecture Note:
    Three cache implementations exist in LiteTTS:
    1. EnhancedCacheManager (LiteTTS/cache/manager.py) - multi-layer with disk backing
    2. VoiceCache (LiteTTS/voice/cache.py) - voice-specific with file backing
    3. synthesis_optimizer caches - in-memory performance caches

    All three follow the same LRU pattern but have different backends.
    This class provides the in-memory LRU foundation that each can extend.
    """

    def __init__(self, max_size: int = 100):
        self._max_size = max_size
        self._cache: OrderedDict[str, T] = OrderedDict()
        self._lock = RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> T | None:
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                self._hits += 1
                return self._cache[key]
            self._misses += 1
            return None

    def set(self, key: str, value: T) -> None:
        with self._lock:
            if key in self._cache:
                # Update existing and move to end
                self._cache.move_to_end(key)
                self._cache[key] = value
            else:
                # Add new entry
                self._cache[key] = value
                # Evict oldest if over capacity
                while len(self._cache) > self._max_size:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                    logger.debug(f"LRU evicted: {oldest_key}")

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    def set_max_size(self, max_size: int) -> None:
        with self._lock:
            self._max_size = max_size
            # Evict if current size exceeds new max
            while len(self._cache) > self._max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

    def get_max_size(self) -> int:
        return self._max_size

    def stats(self) -> dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
            }

    def reset_stats(self) -> None:
        with self._lock:
            self._hits = 0
            self._misses = 0
