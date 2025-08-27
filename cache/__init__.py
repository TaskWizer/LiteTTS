import os
import json
import logging
from pathlib import Path
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache = {}
        
    def get(self, key: str, default: Any = None) -> Any:
        # First check memory cache
        if key in self.memory_cache:
            return self.memory_cache[key]
            
        # Check file cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to read cache file {cache_file}: {e}")
                
        return default
        
    def set(self, key: str, value: Any, persistent: bool = True) -> None:
        # Always set in memory
        self.memory_cache[key] = value
        
        # Optionally persist to disk
        if persistent:
            cache_file = self.cache_dir / f"{key}.json"
            try:
                with open(cache_file, 'w') as f:
                    json.dump(value, f)
            except IOError as e:
                logger.warning(f"Failed to write cache file {cache_file}: {e}")
                
    def clear(self, key: Optional[str] = None) -> None:
        if key is None:
            # Clear all
            self.memory_cache.clear()
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink(missing_ok=True)
        else:
            # Clear specific key
            self.memory_cache.pop(key, None)
            cache_file = self.cache_dir / f"{key}.json"
            cache_file.unlink(missing_ok=True)

# Create global cache manager instance
cache_manager = CacheManager()