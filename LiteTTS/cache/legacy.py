#!/usr/bin/env python3
"""
Caching system for Kokoro ONNX TTS API
"""

import hashlib
import time
import threading
from typing import Optional, Any, Dict, Tuple
from dataclasses import dataclass
from collections import OrderedDict
import logging

from ..exceptions import CacheError

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """Update access metadata"""
        self.last_accessed = time.time()
        self.access_count += 1

class LRUCache:
    """Thread-safe LRU cache implementation"""
    
    def __init__(self, max_size: int = 100, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            self._hits += 1
            
            return entry.value
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put value in cache"""
        with self._lock:
            now = time.time()
            ttl = ttl or self.default_ttl
            
            entry = CacheEntry(
                value=value,
                created_at=now,
                last_accessed=now,
                ttl=ttl
            )
            
            self._cache[key] = entry
            self._cache.move_to_end(key)
            
            # Evict oldest entries if over capacity
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }

class AudioCache(LRUCache):
    """Specialized cache for audio data"""
    
    def __init__(self, max_size: int = 50, default_ttl: float = 3600):
        super().__init__(max_size, default_ttl)
    
    def get_audio(self, text: str, voice: str, speed: float = 1.0, 
                  response_format: str = "mp3") -> Optional[bytes]:
        """Get cached audio data"""
        key = self._generate_key(text, voice, speed, response_format)
        return self.get(key)
    
    def put_audio(self, text: str, voice: str, audio_data: bytes, 
                  speed: float = 1.0, response_format: str = "mp3", 
                  ttl: Optional[float] = None) -> None:
        """Cache audio data"""
        key = self._generate_key(text, voice, speed, response_format)
        self.put(key, audio_data, ttl)
        
        logger.debug(f"Cached audio: text_len={len(text)}, voice={voice}, "
                    f"audio_size={len(audio_data)}, key={key[:8]}...")

class VoiceCache(LRUCache):
    """Specialized cache for voice embeddings"""
    
    def __init__(self, max_size: int = 10):
        super().__init__(max_size, default_ttl=None)  # Voice embeddings don't expire
    
    def get_voice(self, voice_name: str) -> Optional[Any]:
        """Get cached voice embedding"""
        return self.get(voice_name)
    
    def put_voice(self, voice_name: str, voice_embedding: Any) -> None:
        """Cache voice embedding"""
        self.put(voice_name, voice_embedding)
        logger.debug(f"Cached voice embedding: {voice_name}")

class CacheManager:
    """Central cache management"""
    
    def __init__(self, audio_cache_size: int = 50, voice_cache_size: int = 10,
                 audio_ttl: float = 3600):
        self.audio_cache = AudioCache(audio_cache_size, audio_ttl)
        self.voice_cache = VoiceCache(voice_cache_size)
        self._enabled = True
    
    def enable(self):
        """Enable caching"""
        self._enabled = True
        logger.info("🔄 Cache enabled")
    
    def disable(self):
        """Disable caching"""
        self._enabled = False
        logger.info("⏸️ Cache disabled")
    
    def is_enabled(self) -> bool:
        """Check if caching is enabled"""
        return self._enabled
    
    def clear_all(self):
        """Clear all caches"""
        self.audio_cache.clear()
        self.voice_cache.clear()
        logger.info("🧹 All caches cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            "enabled": self._enabled,
            "audio_cache": self.audio_cache.stats(),
            "voice_cache": self.voice_cache.stats()
        }

# Global cache manager instance
cache_manager = CacheManager()