#!/usr/bin/env python3
"""
Voice module with dynamic voice management
"""

import logging
from typing import List, Dict, Optional, Any
from pathlib import Path

# Core imports
from .downloader import VoiceDownloader
from .discovery import VoiceDiscovery

# Optional imports that may require additional dependencies
try:
    from .validator import VoiceValidator
    _has_validator = True
except ImportError:
    _has_validator = False

try:
    from .metadata import VoiceMetadataManager
    _has_metadata = True
except ImportError:
    _has_metadata = False

try:
    from .cache import VoiceCache
    _has_cache = True
except ImportError:
    _has_cache = False

try:
    from .manager import VoiceManager
    _has_manager = True
except ImportError:
    _has_manager = False

try:
    from .dynamic_manager import DynamicVoiceManager
    _has_dynamic_manager = True
except ImportError:
    _has_dynamic_manager = False

try:
    from .blender import VoiceBlender, BlendConfig
    _has_blender = True
except ImportError:
    _has_blender = False

logger = logging.getLogger(__name__)

# Global voice manager instance
_voice_manager: Optional['DynamicVoiceManager'] = None

def get_voice_manager(voices_dir: str = None) -> Optional['DynamicVoiceManager']:
    """Get or create the global voice manager instance"""
    global _voice_manager

    if not _has_dynamic_manager:
        logger.warning("DynamicVoiceManager not available")
        return None

    if _voice_manager is None:
        # Use configuration if voices_dir not provided
        if voices_dir is None:
            try:
                from ..config import config
                voices_dir = getattr(config.paths, 'voices_dir', 'LiteTTS/voices') if config.paths else 'LiteTTS/voices'
            except (ImportError, AttributeError):
                voices_dir = "LiteTTS/voices"  # Fallback

        _voice_manager = DynamicVoiceManager(voices_dir)

    return _voice_manager

def get_available_voices(voices_dir: str = "LiteTTS/voices") -> List[str]:
    """Get list of all available voices (both full and short names)"""
    try:
        voice_manager = get_voice_manager(voices_dir)
        if voice_manager:
            return voice_manager.get_available_voices()
    except Exception as e:
        logger.error(f"Failed to get available voices: {e}")

    # Fallback to local discovery
    return _fallback_voice_discovery(voices_dir)

def _fallback_voice_discovery(voices_dir: str) -> List[str]:
    """Fallback voice discovery for local files only"""
    try:
        voices_path = Path(voices_dir)
        if not voices_path.exists():
            return []

        voice_files = list(voices_path.glob("*.pt")) + list(voices_path.glob("*.bin"))
        voices = [f.stem for f in voice_files]

        # Add common short name mappings
        short_mappings = {}
        for voice in voices:
            if '_' in voice:
                parts = voice.split('_', 1)
                if len(parts) == 2:
                    prefix, short_name = parts
                    if short_name not in short_mappings:
                        short_mappings[short_name] = voice

        all_voices = voices + list(short_mappings.keys())
        return sorted(list(set(all_voices)))

    except Exception as e:
        logger.error(f"Fallback voice discovery failed: {e}")
        return ["af_heart", "am_puck"]  # Minimal fallback

def resolve_voice_name(voice_name: str, voices_dir: str = None) -> str:
    """Resolve a voice name (short or full) to the full voice name"""
    try:
        voice_manager = get_voice_manager(voices_dir)
        if voice_manager:
            return voice_manager.resolve_voice_name(voice_name)
    except Exception as e:
        logger.error(f"Failed to resolve voice name '{voice_name}': {e}")

    return voice_name

def ensure_voice_downloaded(voice_name: str, voices_dir: str = None) -> bool:
    """Ensure a voice is downloaded"""
    try:
        voice_manager = get_voice_manager(voices_dir)
        if voice_manager:
            return voice_manager.ensure_voice_downloaded(voice_name)
    except Exception as e:
        logger.error(f"Failed to ensure voice downloaded '{voice_name}': {e}")

    return False

__all__ = ['VoiceDownloader', 'VoiceDiscovery', 'get_available_voices', 'resolve_voice_name', 'ensure_voice_downloaded']

if _has_validator:
    __all__.append('VoiceValidator')
if _has_metadata:
    __all__.append('VoiceMetadataManager')
if _has_cache:
    __all__.append('VoiceCache')
if _has_manager:
    __all__.append('VoiceManager')
if _has_dynamic_manager:
    __all__.append('DynamicVoiceManager')
if _has_blender:
    __all__.extend(['VoiceBlender', 'BlendConfig'])