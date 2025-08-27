#!/usr/bin/env python3
"""
Voice caching system with preloading capabilities
"""

import threading
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

try:
    from ..models import VoiceEmbedding, VoiceMetadata
except ImportError:
    # Fallback import from models.py file
    import sys
    from pathlib import Path
    models_path = Path(__file__).parent.parent / "models.py"
    if models_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("models", models_path)
        models_module = importlib.util.module_from_spec(spec)
        sys.modules["models"] = models_module
        spec.loader.exec_module(models_module)
        VoiceEmbedding = models_module.VoiceEmbedding
        VoiceMetadata = models_module.VoiceMetadata
    else:
        # Final fallback - define minimal classes
        from dataclasses import dataclass
        from typing import Optional
        from datetime import datetime

        @dataclass
        class VoiceMetadata:
            name: str
            gender: str = "unknown"
            accent: str = "american"
            voice_type: str = "neural"
            quality_rating: float = 4.0
            language: str = "en-us"
            description: str = ""

        @dataclass
        class VoiceEmbedding:
            name: str
            embedding_data: Optional[np.ndarray] = None
            metadata: Optional[VoiceMetadata] = None
            loaded_at: Optional[datetime] = None
            file_hash: str = ""
from .loader import get_voice_loader, VoiceLoader

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry for voice embeddings"""
    embedding: VoiceEmbedding
    loaded_at: datetime
    last_accessed: datetime
    access_count: int = 0
    memory_size: int = 0
    priority: int = 0  # Added for individual loading optimization

class VoiceCache:
    """Manages voice embedding caching with preloading"""

    def __init__(self, voices_dir: str = None,
                 max_cache_size: int = 5, preload_voices: List[str] = None,
                 enable_mock: bool = False):
        # Use configuration if voices_dir not provided
        if voices_dir is None:
            try:
                from ..config import config
                voices_dir = config.paths.voices_dir
                # Check if mock mode should be enabled from config
                if hasattr(config, 'testing') and hasattr(config.testing, 'enable_mock_voices'):
                    enable_mock = config.testing.enable_mock_voices
            except ImportError:
                voices_dir = "LiteTTS/voices"  # Fallback

        self.voices_dir = Path(voices_dir)
        self.max_cache_size = max_cache_size
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.RLock()
        self.enable_mock = enable_mock

        # Initialize voice loader
        self.voice_loader = get_voice_loader(str(self.voices_dir), enable_mock)

        # Default voices to preload
        self.preload_voices = preload_voices or ["af_heart", "am_puck"]

        # Cache statistics
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_loads = 0

        # Initialize cache
        self._initialize_cache()
    
    def _initialize_cache(self):
        """Initialize cache with preloaded voices"""
        logger.info("Initializing voice cache")

        # Preload default voices
        successful_preloads = 0
        for voice_name in self.preload_voices:
            try:
                self._load_voice_to_cache(voice_name)
                successful_preloads += 1
            except Exception as e:
                logger.warning(f"Failed to preload voice {voice_name}: {e}")

        logger.info(f"Voice cache initialized with {successful_preloads}/{len(self.preload_voices)} voices preloaded")
    
    def get_voice_embedding(self, voice_name: str) -> Optional[VoiceEmbedding]:
        """Get voice embedding from cache or load if not cached"""
        with self.cache_lock:
            # Check if voice is in cache
            if voice_name in self.cache:
                entry = self.cache[voice_name]
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                self.cache_hits += 1
                
                logger.debug(f"Cache hit for voice: {voice_name}")
                return entry.embedding
            
            # Cache miss - try to load voice
            self.cache_misses += 1
            logger.debug(f"Cache miss for voice: {voice_name}")
            
            try:
                return self._load_voice_to_cache(voice_name)
            except Exception as e:
                logger.error(f"Failed to load voice {voice_name}: {e}")
                return None
    
    def _load_voice_to_cache(self, voice_name: str) -> Optional[VoiceEmbedding]:
        """Load voice embedding to cache using robust loader"""
        try:
            # Use the voice loader with fallback mechanisms
            load_result = self.voice_loader.load_voice(voice_name)
            self.total_loads += 1

            if not load_result.success:
                logger.error(f"Failed to load voice {voice_name}: {load_result.error_message}")
                return None

            # Extract embedding data and metadata
            embedding_data = load_result.embedding_data
            metadata = load_result.metadata or {}

            # Validate embedding data
            if embedding_data is None:
                logger.error(f"No embedding data loaded for voice: {voice_name}")
                return None

            # Ensure embedding data is numpy array
            if not isinstance(embedding_data, np.ndarray):
                logger.error(f"Embedding data is not numpy array for voice: {voice_name}")
                return None

            # Add loader information to metadata
            metadata['loader_used'] = load_result.loader_used
            metadata['voice_name'] = voice_name

            # Convert metadata dict to VoiceMetadata if needed
            if isinstance(metadata, dict) and not isinstance(metadata, VoiceMetadata):
                voice_metadata = VoiceMetadata(
                    name=metadata.get('name', voice_name),
                    gender=metadata.get('gender', 'unknown'),
                    accent=metadata.get('accent', 'american'),
                    voice_type=metadata.get('voice_type', 'neural'),
                    quality_rating=metadata.get('quality_rating', 4.0),
                    language=metadata.get('language', 'en-us'),
                    description=metadata.get('description', f'Voice loaded with {load_result.loader_used}')
                )
            else:
                voice_metadata = metadata
            
            # Create voice embedding
            voice_embedding = VoiceEmbedding(
                name=voice_name,
                embedding_data=embedding_data,
                metadata=voice_metadata,
                loaded_at=datetime.now(),
                file_hash=self._calculate_file_hash_safe(voice_name, metadata)
            )

            # Calculate memory size
            memory_size = embedding_data.nbytes if hasattr(embedding_data, 'nbytes') else embedding_data.size * 4

            # Add to cache
            cache_entry = CacheEntry(
                embedding=voice_embedding,
                loaded_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                memory_size=memory_size,
                priority=1 if voice_name in ["af_heart", "am_puck", "af_nicole"] else 0
            )
            
            # Manage cache size
            self._manage_cache_size()
            
            # Add new entry
            self.cache[voice_name] = cache_entry
            
            logger.info(f"Loaded voice to cache: {voice_name} ({memory_size} bytes)")
            return voice_embedding
            
        except Exception as e:
            logger.error(f"Failed to load voice {voice_name}: {e}")
            return None    

    def _manage_cache_size(self):
        """Manage cache size by evicting least recently used entries"""
        if len(self.cache) >= self.max_cache_size:
            # Find least recently used entry
            lru_voice = min(
                self.cache.keys(),
                key=lambda v: self.cache[v].last_accessed
            )
            
            # Don't evict preloaded voices unless absolutely necessary
            if lru_voice in self.preload_voices and len(self.cache) < self.max_cache_size * 2:
                # Find next LRU that's not preloaded
                non_preloaded = [v for v in self.cache.keys() if v not in self.preload_voices]
                if non_preloaded:
                    lru_voice = min(
                        non_preloaded,
                        key=lambda v: self.cache[v].last_accessed
                    )
            
            # Evict the LRU entry
            evicted_entry = self.cache.pop(lru_voice)
            logger.info(f"Evicted voice from cache: {lru_voice} "
                       f"(accessed {evicted_entry.access_count} times)")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate file hash for integrity checking"""
        import hashlib
        
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def preload_voice(self, voice_name: str) -> bool:
        """Preload a specific voice into cache"""
        with self.cache_lock:
            if voice_name in self.cache:
                logger.debug(f"Voice already cached: {voice_name}")
                return True
            
            try:
                embedding = self._load_voice_to_cache(voice_name)
                if embedding:
                    # Add to preload list if not already there
                    if voice_name not in self.preload_voices:
                        self.preload_voices.append(voice_name)
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to preload voice {voice_name}: {e}")
                return False
    
    def preload_voices_batch(self, voice_names: List[str]) -> Dict[str, bool]:
        """Preload multiple voices"""
        results = {}
        
        for voice_name in voice_names:
            results[voice_name] = self.preload_voice(voice_name)
        
        successful = sum(1 for success in results.values() if success)
        logger.info(f"Preloaded {successful}/{len(voice_names)} voices")
        
        return results
    
    def is_voice_cached(self, voice_name: str) -> bool:
        """Check if voice is currently cached"""
        with self.cache_lock:
            return voice_name in self.cache
    
    def get_cached_voices(self) -> List[str]:
        """Get list of currently cached voices"""
        with self.cache_lock:
            return list(self.cache.keys())
    
    def evict_voice(self, voice_name: str) -> bool:
        """Manually evict a voice from cache"""
        with self.cache_lock:
            if voice_name in self.cache:
                evicted_entry = self.cache.pop(voice_name)
                logger.info(f"Manually evicted voice: {voice_name}")
                return True
            return False
    
    def clear_cache(self, keep_preloaded: bool = True):
        """Clear cache, optionally keeping preloaded voices"""
        with self.cache_lock:
            if keep_preloaded:
                # Keep only preloaded voices
                voices_to_remove = [
                    v for v in self.cache.keys() 
                    if v not in self.preload_voices
                ]
                for voice_name in voices_to_remove:
                    self.cache.pop(voice_name)
                logger.info(f"Cleared cache, kept {len(self.cache)} preloaded voices")
            else:
                # Clear everything
                cleared_count = len(self.cache)
                self.cache.clear()
                logger.info(f"Cleared entire cache ({cleared_count} voices)")
    
    def get_cache_stats(self) -> Dict[str, any]:
        """Get cache statistics"""
        with self.cache_lock:
            total_memory = sum(entry.memory_size for entry in self.cache.values())
            total_accesses = sum(entry.access_count for entry in self.cache.values())
            
            hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
            
            return {
                'cached_voices': len(self.cache),
                'max_cache_size': self.max_cache_size,
                'cache_utilization': len(self.cache) / self.max_cache_size,
                'total_memory_bytes': total_memory,
                'total_memory_mb': total_memory / (1024 * 1024),
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'hit_rate': hit_rate,
                'total_loads': self.total_loads,
                'total_accesses': total_accesses,
                'preloaded_voices': self.preload_voices.copy(),
                'voice_details': {
                    voice_name: {
                        'loaded_at': entry.loaded_at.isoformat(),
                        'last_accessed': entry.last_accessed.isoformat(),
                        'access_count': entry.access_count,
                        'memory_size': entry.memory_size
                    }
                    for voice_name, entry in self.cache.items()
                }
            }
    
    def optimize_cache(self):
        """Optimize cache by reloading frequently used voices"""
        with self.cache_lock:
            # Get access frequency for each voice
            voice_frequencies = {
                voice_name: entry.access_count
                for voice_name, entry in self.cache.items()
            }
            
            # Sort by frequency
            sorted_voices = sorted(
                voice_frequencies.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Update preload list with most frequently used voices
            top_voices = [voice for voice, freq in sorted_voices[:self.max_cache_size]]
            
            # Add to preload list if not already there
            for voice_name in top_voices:
                if voice_name not in self.preload_voices:
                    self.preload_voices.append(voice_name)
            
            logger.info(f"Optimized cache preload list: {self.preload_voices}")
    
    def validate_cache_integrity(self) -> Dict[str, bool]:
        """Validate integrity of cached voice embeddings"""
        results = {}
        
        with self.cache_lock:
            for voice_name, entry in self.cache.items():
                try:
                    # Check if embedding data is valid
                    embedding = entry.embedding
                    
                    if embedding.embedding_data is None:
                        results[voice_name] = False
                        continue
                    
                    # Check for NaN or infinite values
                    if torch.any(torch.isnan(embedding.embedding_data)):
                        results[voice_name] = False
                        continue
                    
                    if torch.any(torch.isinf(embedding.embedding_data)):
                        results[voice_name] = False
                        continue
                    
                    # Check file hash if available
                    if embedding.file_hash:
                        voice_file = self.voices_dir / f"{voice_name}.pt"
                        if voice_file.exists():
                            current_hash = self._calculate_file_hash(voice_file)
                            if current_hash != embedding.file_hash:
                                results[voice_name] = False
                                continue
                    
                    results[voice_name] = True
                    
                except Exception as e:
                    logger.error(f"Cache validation failed for {voice_name}: {e}")
                    results[voice_name] = False
        
        # Remove invalid entries
        invalid_voices = [voice for voice, valid in results.items() if not valid]
        for voice_name in invalid_voices:
            self.evict_voice(voice_name)
            logger.warning(f"Evicted invalid voice from cache: {voice_name}")
        
        return results

    def optimize_for_individual_files(self):
        """Optimize cache for individual file loading strategy"""
        logger.info("Optimizing voice cache for individual file loading")

        # Clear any combined file references
        if hasattr(self, 'combined_data'):
            delattr(self, 'combined_data')

        # Optimize cache eviction for individual files
        # Prioritize recently used voices and default voices
        with self.cache_lock:
            # Sort cache entries by access time and priority
            default_voices = ["af_heart", "am_puck", "af_nicole"]

            # Mark default voices as high priority
            for voice_name in default_voices:
                if voice_name in self.cache:
                    entry = self.cache[voice_name]
                    entry.priority = 1  # High priority

            # Adjust cache size if needed for individual loading
            if self.max_cache_size < 5:
                logger.info(f"Increasing cache size from {self.max_cache_size} to 10 for individual loading")
                self.max_cache_size = 10

        logger.info("Individual file optimization complete")

    def _calculate_file_hash_safe(self, voice_name: str, metadata: Dict[str, Any]) -> str:
        """Calculate file hash safely, with fallback for missing files"""
        try:
            # Try to find actual file
            for ext in ['.pt', '.bin']:
                voice_file = self.voices_dir / f"{voice_name}{ext}"
                if voice_file.exists():
                    return self._calculate_file_hash(voice_file)

            # Fallback: use voice name and metadata for hash
            import hashlib
            hash_input = f"{voice_name}_{metadata.get('loader_used', 'unknown')}"
            return hashlib.md5(hash_input.encode()).hexdigest()

        except Exception as e:
            logger.warning(f"Could not calculate file hash for {voice_name}: {e}")
            # Final fallback: use voice name
            import hashlib
            return hashlib.md5(voice_name.encode()).hexdigest()

    def get_loader_statistics(self) -> Dict[str, Any]:
        """Get voice loader statistics"""
        if hasattr(self.voice_loader, 'get_load_statistics'):
            return self.voice_loader.get_load_statistics()
        return {}