#!/usr/bin/env python3
"""
Voice discovery and caching system for individual .bin files
"""

import json
import hashlib
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class VoiceInfo:
    """Information about a discovered voice"""
    name: str
    file_path: str
    file_size: int
    checksum: str
    last_modified: float
    source: str  # 'local', 'huggingface', 'custom'
    language: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    discovered_at: Optional[str] = None

class VoiceDiscovery:
    """Discovers and manages individual voice files with caching"""
    
    def __init__(self, voices_dir: str = None):
        # Use configuration if voices_dir not provided
        if voices_dir is None:
            try:
                from ..config import config
                voices_dir = config.paths.voices_dir
            except ImportError:
                voices_dir = "LiteTTS/voices"  # Fallback

        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.voices_dir / "voice_cache.json"
        self.voice_cache: Dict[str, VoiceInfo] = {}
        self.loaded_voices: Dict[str, np.ndarray] = {}
        
        # Voice metadata from HuggingFace repository
        self.known_voices = {
            # American Female
            "af_heart": {"language": "en-us", "gender": "female", "nationality": "american"},
            "af_alloy": {"language": "en-us", "gender": "female", "nationality": "american"},
            "af_aoede": {"language": "en-us", "gender": "female", "nationality": "american"},
            "af_bella": {"language": "en-us", "gender": "female", "nationality": "american"},
            "af_jessica": {"language": "en-us", "gender": "female", "nationality": "american"},
            "af_kore": {"language": "en-us", "gender": "female", "nationality": "american"},
            "af_nicole": {"language": "en-us", "gender": "female", "nationality": "american"},
            "af_nova": {"language": "en-us", "gender": "female", "nationality": "american"},
            "af_river": {"language": "en-us", "gender": "female", "nationality": "american"},
            "af_sarah": {"language": "en-us", "gender": "female", "nationality": "american"},
            "af_sky": {"language": "en-us", "gender": "female", "nationality": "american"},
            
            # American Male
            "am_adam": {"language": "en-us", "gender": "male", "nationality": "american"},
            "am_echo": {"language": "en-us", "gender": "male", "nationality": "american"},
            "am_eric": {"language": "en-us", "gender": "male", "nationality": "american"},
            "am_fenrir": {"language": "en-us", "gender": "male", "nationality": "american"},
            "am_liam": {"language": "en-us", "gender": "male", "nationality": "american"},
            "am_michael": {"language": "en-us", "gender": "male", "nationality": "american"},
            "am_onyx": {"language": "en-us", "gender": "male", "nationality": "american"},
            "am_puck": {"language": "en-us", "gender": "male", "nationality": "american"},
            "am_santa": {"language": "en-us", "gender": "male", "nationality": "american"},
            
            # British Female
            "bf_alice": {"language": "en-gb", "gender": "female", "nationality": "british"},
            "bf_emma": {"language": "en-gb", "gender": "female", "nationality": "british"},
            "bf_isabella": {"language": "en-gb", "gender": "female", "nationality": "british"},
            "bf_lily": {"language": "en-gb", "gender": "female", "nationality": "british"},
            
            # British Male
            "bm_daniel": {"language": "en-gb", "gender": "male", "nationality": "british"},
            "bm_fable": {"language": "en-gb", "gender": "male", "nationality": "british"},
            "bm_george": {"language": "en-gb", "gender": "male", "nationality": "british"},
            "bm_lewis": {"language": "en-gb", "gender": "male", "nationality": "british"},
            
            # Other languages (partial list for common voices)
            "jf_alpha": {"language": "ja-jp", "gender": "female", "nationality": "japanese"},
            "jm_kumo": {"language": "ja-jp", "gender": "male", "nationality": "japanese"},
            "zf_xiaobei": {"language": "zh-cn", "gender": "female", "nationality": "chinese"},
            "ff_siwis": {"language": "fr-fr", "gender": "female", "nationality": "french"},
        }
        
        # Load cache and discover voices
        self._load_cache()
        self.discover_voices()
    
    def _load_cache(self) -> None:
        """Load voice cache from JSON file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                self.voice_cache = {
                    name: VoiceInfo(**data) 
                    for name, data in cache_data.items()
                }
                logger.info(f"Loaded voice cache with {len(self.voice_cache)} voices")
            except Exception as e:
                logger.warning(f"Failed to load voice cache: {e}")
                self.voice_cache = {}
    
    def _save_cache(self) -> None:
        """Save voice cache to JSON file"""
        try:
            cache_data = {
                name: asdict(info) 
                for name, info in self.voice_cache.items()
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"Saved voice cache with {len(self.voice_cache)} voices")
        except Exception as e:
            logger.error(f"Failed to save voice cache: {e}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def discover_voices(self) -> Tuple[int, int]:
        """Discover voice files in the voices directory"""
        discovered = 0
        updated = 0
        removed = 0

        # Get current voice files on disk
        current_voice_files = set()
        for voice_file in self.voices_dir.glob("*.bin"):
            current_voice_files.add(voice_file.stem)

        # Remove voices from cache that no longer exist on disk
        voices_to_remove = []
        for voice_name in self.voice_cache.keys():
            if voice_name not in current_voice_files:
                voices_to_remove.append(voice_name)

        for voice_name in voices_to_remove:
            del self.voice_cache[voice_name]
            removed += 1
            logger.info(f"Removed deleted voice from cache: {voice_name}")

        # Process current voice files
        for voice_file in self.voices_dir.glob("*.bin"):
            voice_name = voice_file.stem

            # Get file stats
            stat = voice_file.stat()
            file_size = stat.st_size
            last_modified = stat.st_mtime

            # Check if voice is in cache and up to date
            if voice_name in self.voice_cache:
                cached = self.voice_cache[voice_name]
                if (cached.file_size == file_size and
                    cached.last_modified == last_modified):
                    continue  # Voice is up to date
                updated += 1
            else:
                discovered += 1

            # Calculate checksum for new/changed files
            checksum = self._calculate_checksum(voice_file)

            # Determine source and metadata
            source = "custom"
            metadata = {}
            if voice_name in self.known_voices:
                source = "huggingface"
                metadata = self.known_voices[voice_name]

            # Create voice info
            voice_info = VoiceInfo(
                name=voice_name,
                file_path=str(voice_file),
                file_size=file_size,
                checksum=checksum,
                last_modified=last_modified,
                source=source,
                language=metadata.get("language"),
                gender=metadata.get("gender"),
                nationality=metadata.get("nationality"),
                discovered_at=datetime.now().isoformat()
            )

            self.voice_cache[voice_name] = voice_info

        if discovered > 0 or updated > 0 or removed > 0:
            logger.info(f"Voice discovery: {discovered} new, {updated} updated, {removed} removed")
            self._save_cache()

        return discovered, updated
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voice names"""
        return sorted(list(self.voice_cache.keys()))
    
    def get_voice_info(self, voice_name: str) -> Optional[VoiceInfo]:
        """Get information for a specific voice"""
        return self.voice_cache.get(voice_name)
    
    def is_voice_available(self, voice_name: str) -> bool:
        """Check if a voice is available locally"""
        return voice_name in self.voice_cache
    
    def load_voice_data(self, voice_name: str) -> Optional[np.ndarray]:
        """Load a voice file into memory"""
        if voice_name in self.loaded_voices:
            return self.loaded_voices[voice_name]
        
        if voice_name not in self.voice_cache:
            logger.warning(f"Voice '{voice_name}' not found in cache")
            return None
        
        try:
            voice_info = self.voice_cache[voice_name]
            voice_path = Path(voice_info.file_path)
            
            if not voice_path.exists():
                logger.error(f"Voice file not found: {voice_path}")
                return None
            
            # Load voice data as numpy array
            voice_data = np.fromfile(voice_path, dtype=np.float32)
            
            # Reshape based on expected format (style vectors are typically 256-dimensional)
            # The file contains multiple style vectors for different text lengths
            if len(voice_data) % 256 == 0:
                voice_data = voice_data.reshape(-1, 1, 256)
            else:
                logger.warning(f"Voice '{voice_name}' has unexpected size: {len(voice_data)}")
                # Try to use as-is, might be a different format
                voice_data = voice_data.reshape(-1, 1, len(voice_data))
            
            self.loaded_voices[voice_name] = voice_data
            logger.debug(f"Loaded voice '{voice_name}': {voice_data.shape}")
            
            return voice_data
            
        except Exception as e:
            logger.error(f"Failed to load voice '{voice_name}': {e}")
            return None
    
    def get_voice_stats(self) -> Dict:
        """Get statistics about available voices"""
        stats = {
            "total_voices": len(self.voice_cache),
            "loaded_voices": len(self.loaded_voices),
            "by_language": {},
            "by_gender": {},
            "by_nationality": {},
            "by_source": {}
        }
        
        for voice_info in self.voice_cache.values():
            # Count by language
            lang = voice_info.language or "unknown"
            stats["by_language"][lang] = stats["by_language"].get(lang, 0) + 1
            
            # Count by gender
            gender = voice_info.gender or "unknown"
            stats["by_gender"][gender] = stats["by_gender"].get(gender, 0) + 1
            
            # Count by nationality
            nationality = voice_info.nationality or "unknown"
            stats["by_nationality"][nationality] = stats["by_nationality"].get(nationality, 0) + 1
            
            # Count by source
            source = voice_info.source
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
        
        return stats
    
    def filter_voices(self, language: Optional[str] = None, 
                     gender: Optional[str] = None,
                     nationality: Optional[str] = None,
                     source: Optional[str] = None) -> List[str]:
        """Filter voices by criteria"""
        filtered = []
        
        for voice_name, voice_info in self.voice_cache.items():
            if language and voice_info.language != language:
                continue
            if gender and voice_info.gender != gender:
                continue
            if nationality and voice_info.nationality != nationality:
                continue
            if source and voice_info.source != source:
                continue
            
            filtered.append(voice_name)
        
        return sorted(filtered)
    
    def clear_loaded_voices(self) -> None:
        """Clear all loaded voice data from memory"""
        self.loaded_voices.clear()
        logger.info("Cleared all loaded voice data from memory")
    
    def invalidate_cache(self) -> None:
        """Invalidate the cache and rediscover voices"""
        self.voice_cache.clear()
        self.loaded_voices.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("Voice cache invalidated")
        self.discover_voices()
