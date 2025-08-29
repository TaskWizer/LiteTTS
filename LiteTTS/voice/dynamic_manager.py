#!/usr/bin/env python3
"""
Dynamic voice manager with HuggingFace integration and smart caching
"""

import numpy as np
import logging
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass

from .downloader import VoiceDownloader
from .discovery import VoiceDiscovery

logger = logging.getLogger(__name__)

@dataclass
class VoiceEmbedding:
    """Voice embedding data structure"""
    name: str
    embedding_data: np.ndarray
    metadata: Dict[str, Any]
    file_path: str
    checksum: str

class DynamicVoiceManager:
    """Dynamic voice manager with HuggingFace integration and smart caching"""
    
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
        
        # Initialize components
        self.downloader = VoiceDownloader(str(self.voices_dir))
        self.discovery = VoiceDiscovery(str(self.voices_dir))
        
        # Voice storage
        self.loaded_voices: Dict[str, VoiceEmbedding] = {}
        self.voice_mappings: Dict[str, str] = {}  # short name -> full name
        
        # Cache file for voice mappings
        self.mappings_cache_file = self.voices_dir / "voice_mappings.json"
        
        # Initialize voice system
        self._initialize_voice_system()
        
        logger.info(f"Dynamic voice manager initialized with {len(self.get_available_voices())} voices")
    
    def _initialize_voice_system(self) -> None:
        """Initialize the voice system with discovery and mapping generation"""
        # Load cached mappings if available
        self._load_voice_mappings()
        
        # Generate mappings for all discovered voices
        self._generate_voice_mappings()
        
        # Save updated mappings
        self._save_voice_mappings()
    
    def _generate_voice_mappings(self) -> None:
        """Generate short name mappings for all available voices"""
        available_voices = self.discovery.get_available_voices()
        
        # Clear existing mappings
        self.voice_mappings = {}
        
        # Generate mappings based on voice naming patterns
        for voice_name in available_voices:
            # Extract short name from full voice name
            # Examples: af_heart -> heart, am_puck -> puck, bf_alice -> alice
            if '_' in voice_name:
                parts = voice_name.split('_', 1)
                if len(parts) == 2:
                    prefix, short_name = parts
                    
                    # Only create mapping if short name doesn't conflict
                    if short_name not in self.voice_mappings:
                        self.voice_mappings[short_name] = voice_name
                    else:
                        # Handle conflicts by using the first one found
                        logger.debug(f"Short name conflict for '{short_name}': keeping {self.voice_mappings[short_name]}")
        
        logger.info(f"Generated {len(self.voice_mappings)} voice mappings")
    
    def _load_voice_mappings(self) -> None:
        """Load voice mappings from cache"""
        if not self.mappings_cache_file.exists():
            return
            
        try:
            with open(self.mappings_cache_file, 'r') as f:
                self.voice_mappings = json.load(f)
            logger.debug(f"Loaded {len(self.voice_mappings)} voice mappings from cache")
        except Exception as e:
            logger.warning(f"Failed to load voice mappings cache: {e}")
            self.voice_mappings = {}
    
    def _save_voice_mappings(self) -> None:
        """Save voice mappings to cache"""
        try:
            with open(self.mappings_cache_file, 'w') as f:
                json.dump(self.voice_mappings, f, indent=2)
            logger.debug(f"Saved {len(self.voice_mappings)} voice mappings to cache")
        except Exception as e:
            logger.error(f"Failed to save voice mappings cache: {e}")
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voice names - returns only actual voice files to prevent count duplication"""
        discovered_voices = self.discovery.get_available_voices()

        # Return only the discovered voices (actual files), not short name mappings
        # This prevents the voice count discrepancy (105 vs 55 issue)
        # Short name resolution is handled at synthesis time, not discovery time
        return sorted(list(set(discovered_voices)))
    
    def resolve_voice_name(self, voice_name: str) -> str:
        """Resolve a voice name (short or full) to the full voice name"""
        # If it's already a full name and exists, return it
        if voice_name in self.discovery.get_available_voices():
            return voice_name
        
        # If it's a short name, resolve it
        if voice_name in self.voice_mappings:
            return self.voice_mappings[voice_name]
        
        # If not found, return original name (will fail later with proper error)
        return voice_name
    
    def is_voice_available(self, voice_name: str) -> bool:
        """Check if a voice is available (either downloaded or can be downloaded)"""
        resolved_name = self.resolve_voice_name(voice_name)
        
        # Check if it's in discovered voices (from HuggingFace)
        if resolved_name in self.downloader.discovered_voices:
            return True
        
        # Check if it's locally available
        return self.discovery.is_voice_available(resolved_name)
    
    def ensure_voice_downloaded(self, voice_name: str) -> bool:
        """Ensure a voice is downloaded, downloading if necessary"""
        resolved_name = self.resolve_voice_name(voice_name)
        
        # Check if already downloaded
        if self.downloader.is_voice_downloaded(resolved_name):
            return True
        
        # Try to download
        logger.info(f"Downloading voice: {resolved_name}")
        return self.downloader.download_voice(resolved_name)
    
    def get_voice_embedding(self, voice_name: str) -> Optional[VoiceEmbedding]:
        """Get voice embedding, downloading if necessary"""
        resolved_name = self.resolve_voice_name(voice_name)
        
        # Check if already loaded
        if resolved_name in self.loaded_voices:
            return self.loaded_voices[resolved_name]
        
        # Ensure voice is downloaded
        if not self.ensure_voice_downloaded(resolved_name):
            logger.error(f"Failed to download voice: {resolved_name}")
            return None
        
        # Load voice data
        return self._load_voice_data(resolved_name)
    
    def _load_voice_data(self, voice_name: str) -> Optional[VoiceEmbedding]:
        """Load voice data from file"""
        voice_file = self.voices_dir / f"{voice_name}.pt"
        
        if not voice_file.exists():
            logger.error(f"Voice file not found: {voice_file}")
            return None
        
        try:
            # Load voice data
            voice_data = np.fromfile(voice_file, dtype=np.float32)
            
            # Reshape voice data (assuming 256-dimensional embeddings)
            if len(voice_data) % 256 == 0:
                voice_data = voice_data.reshape(-1, 1, 256)
            else:
                logger.warning(f"Voice '{voice_name}' has unexpected dimensions: {len(voice_data)}")
                # Try to use as-is
                voice_data = voice_data.reshape(1, -1)
            
            # Get metadata
            voice_info = self.discovery.get_voice_info(voice_name)
            metadata = {}
            if voice_info:
                metadata = {
                    'language': voice_info.language,
                    'gender': voice_info.gender,
                    'nationality': voice_info.nationality,
                    'source': voice_info.source
                }
            
            # Calculate checksum
            import hashlib
            checksum = hashlib.sha256(voice_data.tobytes()).hexdigest()
            
            # Create voice embedding
            voice_embedding = VoiceEmbedding(
                name=voice_name,
                embedding_data=voice_data,
                metadata=metadata,
                file_path=str(voice_file),
                checksum=checksum
            )
            
            self.loaded_voices[voice_name] = voice_embedding
            logger.debug(f"Loaded voice '{voice_name}' with shape {voice_data.shape}")
            
            return voice_embedding
            
        except Exception as e:
            logger.error(f"Failed to load voice '{voice_name}': {e}")
            return None
    
    def download_all_voices(self, progress_callback=None) -> Dict[str, bool]:
        """Download all available voices from HuggingFace"""
        return self.downloader.download_all_voices(progress_callback)
    
    def get_download_status(self) -> Dict[str, Any]:
        """Get download status for all voices"""
        return {
            'discovered_voices': len(self.downloader.discovered_voices),
            'downloaded_voices': len(self.downloader.get_downloaded_voices()),
            'missing_voices': len(self.downloader.get_missing_voices()),
            'voice_mappings': len(self.voice_mappings),
            'loaded_voices': len(self.loaded_voices)
        }
    
    def refresh_discovery(self) -> bool:
        """Refresh voice discovery from HuggingFace"""
        success = self.downloader.refresh_discovery()
        if success:
            self.discovery.invalidate_cache()
            self._generate_voice_mappings()
            self._save_voice_mappings()
        return success
    
    def get_voice_mappings(self) -> Dict[str, str]:
        """Get current voice mappings (short -> full name)"""
        return self.voice_mappings.copy()


# Global instance for easy access
dynamic_voice_manager = DynamicVoiceManager()
