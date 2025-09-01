#!/usr/bin/env python3
"""
Enhanced multi-level cache manager for TTS system
"""

import hashlib
import pickle
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging

from ..models import AudioSegment, VoiceEmbedding

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Enhanced cache entry with metadata"""
    key: str
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    ttl_seconds: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl_seconds is None:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl_seconds)
    
    def touch(self):
        """Update last accessed time and increment access count"""
        self.last_accessed = datetime.now()
        self.access_count += 1

class EnhancedCacheManager:
    """Multi-level cache manager with LRU eviction and persistence"""
    
    def __init__(self, cache_dir: str = "LiteTTS/cache",
                 max_memory_size: int = None,  # Will use config default
                 max_disk_size: int = None,    # Will use config default
                 config=None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Use config values or fallback to defaults
        if config and hasattr(config, 'cache'):
            self.max_memory_size = max_memory_size or (config.cache.memory_cache_size_mb * 1024 * 1024)
            self.max_disk_size = max_disk_size or (config.cache.disk_cache_size_mb * 1024 * 1024)
        else:
            # Fallback defaults
            self.max_memory_size = max_memory_size or (100 * 1024 * 1024)  # 100MB
            self.max_disk_size = max_disk_size or (1024 * 1024 * 1024)     # 1GB
        
        # Memory cache
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.memory_size = 0
        
        # Disk cache tracking
        self.disk_cache_index: Dict[str, Dict[str, Any]] = {}
        self.disk_size = 0
        
        # Thread safety
        self.cache_lock = threading.RLock()
        
        # Cache statistics
        self.stats = {
            'memory_hits': 0,
            'disk_hits': 0,
            'misses': 0,
            'evictions': 0,
            'disk_writes': 0,
            'disk_reads': 0
        }
        
        # Initialize cache
        self._load_disk_index()
        self._calculate_disk_size()
        
        logger.info(f"Enhanced cache manager initialized: {self.cache_dir}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache (memory first, then disk)"""
        with self.cache_lock:
            # Check memory cache first
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                
                if entry.is_expired():
                    self._remove_from_memory(key)
                    return None
                
                entry.touch()
                self.stats['memory_hits'] += 1
                logger.debug(f"Memory cache hit: {key}")
                return entry.data
            
            # Check disk cache
            if key in self.disk_cache_index:
                disk_entry_info = self.disk_cache_index[key]
                
                # Check if disk entry is expired
                if disk_entry_info.get('ttl_seconds'):
                    created_at = datetime.fromisoformat(disk_entry_info['created_at'])
                    if datetime.now() > created_at + timedelta(seconds=disk_entry_info['ttl_seconds']):
                        self._remove_from_disk(key)
                        return None
                
                # Load from disk
                data = self._load_from_disk(key)
                if data is not None:
                    # Add to memory cache
                    self._add_to_memory(key, data, 
                                      ttl_seconds=disk_entry_info.get('ttl_seconds'),
                                      tags=disk_entry_info.get('tags', []))
                    
                    self.stats['disk_hits'] += 1
                    logger.debug(f"Disk cache hit: {key}")
                    return data
            
            # Cache miss
            self.stats['misses'] += 1
            logger.debug(f"Cache miss: {key}")
            return None
    
    def put(self, key: str, data: Any, ttl_seconds: Optional[int] = None, 
            tags: List[str] = None, persist_to_disk: bool = True) -> bool:
        """Put item in cache"""
        with self.cache_lock:
            if tags is None:
                tags = []
            
            # Calculate data size
            try:
                data_size = self._calculate_size(data)
            except Exception as e:
                logger.error(f"Failed to calculate size for cache key {key}: {e}")
                return False
            
            # Add to memory cache
            success = self._add_to_memory(key, data, ttl_seconds, tags, data_size)
            
            # Persist to disk if requested and successful
            if success and persist_to_disk:
                self._save_to_disk(key, data, ttl_seconds, tags, data_size)
            
            return success
    
    def _add_to_memory(self, key: str, data: Any, ttl_seconds: Optional[int] = None,
                      tags: List[str] = None, data_size: int = None) -> bool:
        """Add item to memory cache"""
        if tags is None:
            tags = []
        
        if data_size is None:
            try:
                data_size = self._calculate_size(data)
            except Exception:
                data_size = 1024  # Default size estimate
        
        # Check if we need to evict items
        while (self.memory_size + data_size > self.max_memory_size and 
               len(self.memory_cache) > 0):
            self._evict_lru_memory()
        
        # Create cache entry
        entry = CacheEntry(
            key=key,
            data=data,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            size_bytes=data_size,
            ttl_seconds=ttl_seconds,
            tags=tags
        )
        
        # Remove existing entry if present
        if key in self.memory_cache:
            self._remove_from_memory(key)
        
        # Add new entry
        self.memory_cache[key] = entry
        self.memory_size += data_size
        
        logger.debug(f"Added to memory cache: {key} ({data_size} bytes)")
        return True    
    
    def _remove_from_memory(self, key: str):
        """Remove item from memory cache"""
        if key in self.memory_cache:
            entry = self.memory_cache.pop(key)
            self.memory_size -= entry.size_bytes
            logger.debug(f"Removed from memory cache: {key}")
    
    def _evict_lru_memory(self):
        """Evict least recently used item from memory cache"""
        if not self.memory_cache:
            return
        
        # Find LRU entry
        lru_key = min(self.memory_cache.keys(), 
                     key=lambda k: self.memory_cache[k].last_accessed)
        
        self._remove_from_memory(lru_key)
        self.stats['evictions'] += 1
        logger.debug(f"Evicted from memory cache: {lru_key}")
    
    def _save_to_disk(self, key: str, data: Any, ttl_seconds: Optional[int] = None,
                     tags: List[str] = None, data_size: int = None):
        """Save item to disk cache"""
        try:
            # Check disk space
            while self.disk_size + data_size > self.max_disk_size and len(self.disk_cache_index) > 0:
                self._evict_lru_disk()
            
            # Create file path
            safe_key = hashlib.md5(key.encode()).hexdigest()
            cache_file = self.cache_dir / f"{safe_key}.cache"
            
            # Save data
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            # Update index
            self.disk_cache_index[key] = {
                'file_path': str(cache_file),
                'created_at': datetime.now().isoformat(),
                'size_bytes': data_size or cache_file.stat().st_size,
                'ttl_seconds': ttl_seconds,
                'tags': tags or []
            }
            
            self.disk_size += self.disk_cache_index[key]['size_bytes']
            self.stats['disk_writes'] += 1
            
            # Save index
            self._save_disk_index()
            
            logger.debug(f"Saved to disk cache: {key}")
            
        except Exception as e:
            logger.error(f"Failed to save to disk cache {key}: {e}")
    
    def _load_from_disk(self, key: str) -> Optional[Any]:
        """Load item from disk cache"""
        try:
            if key not in self.disk_cache_index:
                return None
            
            file_path = self.disk_cache_index[key]['file_path']
            
            if not Path(file_path).exists():
                # Clean up stale index entry
                self._remove_from_disk(key)
                return None
            
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            self.stats['disk_reads'] += 1
            logger.debug(f"Loaded from disk cache: {key}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load from disk cache {key}: {e}")
            # Clean up corrupted entry
            self._remove_from_disk(key)
            return None
    
    def _remove_from_disk(self, key: str):
        """Remove item from disk cache"""
        try:
            if key in self.disk_cache_index:
                entry_info = self.disk_cache_index.pop(key)
                file_path = Path(entry_info['file_path'])
                
                if file_path.exists():
                    file_path.unlink()
                
                self.disk_size -= entry_info['size_bytes']
                self._save_disk_index()
                
                logger.debug(f"Removed from disk cache: {key}")
                
        except Exception as e:
            logger.error(f"Failed to remove from disk cache {key}: {e}")
    
    def _evict_lru_disk(self):
        """Evict least recently used item from disk cache"""
        if not self.disk_cache_index:
            return
        
        # Find LRU entry (based on creation time since we don't track access for disk)
        lru_key = min(self.disk_cache_index.keys(),
                     key=lambda k: self.disk_cache_index[k]['created_at'])
        
        self._remove_from_disk(lru_key)
        self.stats['evictions'] += 1
        logger.debug(f"Evicted from disk cache: {lru_key}")
    
    def _load_disk_index(self):
        """Load disk cache index"""
        index_file = self.cache_dir / "cache_index.json"
        
        try:
            if index_file.exists():
                import json
                with open(index_file, 'r') as f:
                    self.disk_cache_index = json.load(f)
                logger.debug(f"Loaded disk cache index: {len(self.disk_cache_index)} entries")
        except Exception as e:
            logger.error(f"Failed to load disk cache index: {e}")
            self.disk_cache_index = {}
    
    def _save_disk_index(self):
        """Save disk cache index"""
        index_file = self.cache_dir / "cache_index.json"
        
        try:
            import json
            with open(index_file, 'w') as f:
                json.dump(self.disk_cache_index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save disk cache index: {e}")
    
    def _calculate_disk_size(self):
        """Calculate total disk cache size"""
        self.disk_size = sum(
            entry['size_bytes'] for entry in self.disk_cache_index.values()
        )
    
    def _calculate_size(self, data: Any) -> int:
        """Calculate approximate size of data"""
        try:
            if isinstance(data, AudioSegment):
                return data.audio_data.nbytes + 1024  # Add overhead
            elif isinstance(data, VoiceEmbedding):
                if data.embedding_data is not None:
                    return data.embedding_data.nbytes + 1024
                return 1024
            else:
                # Use pickle size as approximation
                return len(pickle.dumps(data))
        except Exception:
            return 1024  # Default estimate
    
    def delete(self, key: str) -> bool:
        """Delete item from cache"""
        with self.cache_lock:
            deleted = False
            
            # Remove from memory
            if key in self.memory_cache:
                self._remove_from_memory(key)
                deleted = True
            
            # Remove from disk
            if key in self.disk_cache_index:
                self._remove_from_disk(key)
                deleted = True
            
            return deleted
    
    def clear(self, tags: List[str] = None):
        """Clear cache (optionally by tags)"""
        with self.cache_lock:
            if tags is None:
                # Clear everything
                self.memory_cache.clear()
                self.memory_size = 0
                
                # Clear disk cache
                for key in list(self.disk_cache_index.keys()):
                    self._remove_from_disk(key)
                
                logger.info("Cleared entire cache")
            else:
                # Clear by tags
                keys_to_remove = []
                
                # Check memory cache
                for key, entry in self.memory_cache.items():
                    if any(tag in entry.tags for tag in tags):
                        keys_to_remove.append(key)
                
                # Check disk cache
                for key, entry_info in self.disk_cache_index.items():
                    if any(tag in entry_info.get('tags', []) for tag in tags):
                        keys_to_remove.append(key)
                
                # Remove tagged entries
                for key in set(keys_to_remove):
                    self.delete(key)
                
                logger.info(f"Cleared cache entries with tags: {tags}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.cache_lock:
            total_requests = self.stats['memory_hits'] + self.stats['disk_hits'] + self.stats['misses']
            hit_rate = (self.stats['memory_hits'] + self.stats['disk_hits']) / total_requests if total_requests > 0 else 0
            
            return {
                'memory_cache': {
                    'entries': len(self.memory_cache),
                    'size_bytes': self.memory_size,
                    'size_mb': self.memory_size / (1024 * 1024),
                    'max_size_mb': self.max_memory_size / (1024 * 1024),
                    'utilization': self.memory_size / self.max_memory_size
                },
                'disk_cache': {
                    'entries': len(self.disk_cache_index),
                    'size_bytes': self.disk_size,
                    'size_mb': self.disk_size / (1024 * 1024),
                    'max_size_mb': self.max_disk_size / (1024 * 1024),
                    'utilization': self.disk_size / self.max_disk_size
                },
                'performance': {
                    'memory_hits': self.stats['memory_hits'],
                    'disk_hits': self.stats['disk_hits'],
                    'misses': self.stats['misses'],
                    'hit_rate': hit_rate,
                    'evictions': self.stats['evictions']
                },
                'io_stats': {
                    'disk_writes': self.stats['disk_writes'],
                    'disk_reads': self.stats['disk_reads']
                }
            }
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        with self.cache_lock:
            expired_count = 0
            
            # Clean memory cache
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                self._remove_from_memory(key)
                expired_count += 1
            
            # Clean disk cache
            now = datetime.now()
            expired_disk_keys = []
            
            for key, entry_info in self.disk_cache_index.items():
                if entry_info.get('ttl_seconds'):
                    created_at = datetime.fromisoformat(entry_info['created_at'])
                    if now > created_at + timedelta(seconds=entry_info['ttl_seconds']):
                        expired_disk_keys.append(key)
            
            for key in expired_disk_keys:
                self._remove_from_disk(key)
                expired_count += 1
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired cache entries")
            
            return expired_count
    
    def optimize(self):
        """Optimize cache performance"""
        with self.cache_lock:
            logger.info("Optimizing cache")
            
            # Clean up expired entries
            self.cleanup_expired()
            
            # Validate disk cache integrity
            invalid_keys = []
            for key, entry_info in self.disk_cache_index.items():
                file_path = Path(entry_info['file_path'])
                if not file_path.exists():
                    invalid_keys.append(key)
            
            for key in invalid_keys:
                del self.disk_cache_index[key]
            
            if invalid_keys:
                self._save_disk_index()
                logger.info(f"Removed {len(invalid_keys)} invalid disk cache entries")
            
            # Recalculate disk size
            self._calculate_disk_size()
            
            logger.info("Cache optimization completed")
    
    def shutdown(self):
        """Shutdown cache manager"""
        with self.cache_lock:
            logger.info("Shutting down cache manager")
            
            # Save disk index
            self._save_disk_index()
            
            # Clear memory cache
            self.memory_cache.clear()
            self.memory_size = 0
            
            logger.info("Cache manager shutdown completed")