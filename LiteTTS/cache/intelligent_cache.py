"""
Intelligent Caching System for RTF Optimization
"""

import hashlib
import time
import json
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import threading

class IntelligentCache:
    """Intelligent caching system with RTF optimization"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.RLock()
        
        # Performance tracking
        self.performance_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_hit_time': 0.0,
            'avg_miss_time': 0.0,
            'cache_size': 0,
            'hit_rate': 0.0
        }
    
    def get_cache_key(self, text: str, voice: str, **kwargs) -> str:
        """Generate cache key for text and voice combination"""
        # Create deterministic hash from text, voice, and parameters
        cache_data = {
            'text': text.strip().lower(),
            'voice': voice,
            'params': sorted(kwargs.items())
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[bytes]:
        """Get cached audio data"""
        start_time = time.time()
        
        with self.lock:
            if cache_key in self.cache:
                # Check TTL
                cached_time, audio_data = self.cache[cache_key]
                if time.time() - cached_time < self.ttl_seconds:
                    # Update access time for LRU
                    self.access_times[cache_key] = time.time()
                    
                    # Update stats
                    hit_time = time.time() - start_time
                    self._update_hit_stats(hit_time)
                    
                    return audio_data
                else:
                    # Expired, remove from cache
                    del self.cache[cache_key]
                    del self.access_times[cache_key]
            
            # Cache miss
            miss_time = time.time() - start_time
            self._update_miss_stats(miss_time)
            return None
    
    def put(self, cache_key: str, audio_data: bytes):
        """Store audio data in cache"""
        with self.lock:
            # Check if we need to evict items
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            # Store with timestamp
            self.cache[cache_key] = (time.time(), audio_data)
            self.access_times[cache_key] = time.time()
            
            # Update stats
            self.performance_stats['cache_size'] = len(self.cache)
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if not self.access_times:
            return
        
        # Find LRU item
        lru_key = min(self.access_times.keys(), 
                     key=lambda k: self.access_times[k])
        
        # Remove from cache
        if lru_key in self.cache:
            del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def _update_hit_stats(self, hit_time: float):
        """Update cache hit statistics"""
        self.performance_stats['cache_hits'] += 1
        
        # Running average
        hits = self.performance_stats['cache_hits']
        current_avg = self.performance_stats['avg_hit_time']
        self.performance_stats['avg_hit_time'] = (
            (current_avg * (hits - 1) + hit_time) / hits
        )
        
        self._update_hit_rate()
    
    def _update_miss_stats(self, miss_time: float):
        """Update cache miss statistics"""
        self.performance_stats['cache_misses'] += 1
        
        # Running average
        misses = self.performance_stats['cache_misses']
        current_avg = self.performance_stats['avg_miss_time']
        self.performance_stats['avg_miss_time'] = (
            (current_avg * (misses - 1) + miss_time) / misses
        )
        
        self._update_hit_rate()
    
    def _update_hit_rate(self):
        """Update cache hit rate"""
        total = self.performance_stats['cache_hits'] + self.performance_stats['cache_misses']
        if total > 0:
            self.performance_stats['hit_rate'] = (
                self.performance_stats['cache_hits'] / total
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        with self.lock:
            return self.performance_stats.copy()
    
    def clear(self):
        """Clear all cached data"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.performance_stats['cache_size'] = 0

# Global cache instance
_intelligent_cache = IntelligentCache()

def get_intelligent_cache():
    """Get the global intelligent cache instance"""
    return _intelligent_cache
