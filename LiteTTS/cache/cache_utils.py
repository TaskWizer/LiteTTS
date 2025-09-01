#!/usr/bin/env python3
"""
Standardized cache utilities for Kokoro ONNX TTS API
This module provides consistent cache key generation across all components
"""

import hashlib
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class CacheKeyGenerator:
    """Standardized cache key generator for consistent caching across the application"""
    
    @staticmethod
    def generate_audio_cache_key(
        text: str,
        voice: str,
        speed: float = 1.0,
        format: str = "mp3",
        language: str = "en-us",
        emotion: Optional[str] = None,
        emotion_strength: float = 1.0
    ) -> str:
        """
        Generate standardized cache key for audio generation
        
        This is the canonical cache key format used throughout the application.
        All other cache key generation should use this method to ensure consistency.
        """
        # Normalize inputs to ensure consistent keys
        text = text.strip()
        voice = voice.lower().strip()
        format = format.lower().strip()
        language = language.lower().strip()
        
        # Round speed to 2 decimal places to avoid floating point precision issues
        speed = round(float(speed), 2)
        emotion_strength = round(float(emotion_strength), 2)
        
        # Build key components in a consistent order
        key_components = {
            "text": text,
            "voice": voice,
            "speed": speed,
            "format": format,
            "language": language
        }
        
        # Add optional components if present
        if emotion:
            key_components["emotion"] = emotion.lower().strip()
            key_components["emotion_strength"] = emotion_strength
        
        # Create deterministic JSON string (sorted keys)
        key_string = json.dumps(key_components, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA256 hash for consistent, collision-resistant keys
        cache_key = hashlib.sha256(key_string.encode('utf-8')).hexdigest()
        
        logger.debug(f"Generated cache key: {cache_key[:16]}... for text: '{text[:50]}...'")
        return cache_key
    
    @staticmethod
    def generate_voice_cache_key(voice: str) -> str:
        """Generate cache key for voice data"""
        voice = voice.lower().strip()
        key_string = f"voice:{voice}"
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_model_cache_key(model_path: str, variant: str = "") -> str:
        """Generate cache key for model data"""
        key_string = f"model:{model_path}:{variant}"
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_text_preprocessing_cache_key(text: str, preprocessing_level: str = "standard") -> str:
        """Generate cache key for preprocessed text"""
        text = text.strip()
        key_string = f"text_preprocess:{preprocessing_level}:{text}"
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_phoneme_cache_key(text: str, language: str = "en-us") -> str:
        """Generate cache key for phonemized text"""
        text = text.strip()
        language = language.lower().strip()
        key_string = f"phonemes:{language}:{text}"
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()

class CacheMetrics:
    """Cache performance metrics tracking"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.errors = 0
        self.total_requests = 0
        self.cache_sizes = {}
    
    def record_hit(self, cache_type: str = "audio"):
        """Record a cache hit"""
        self.hits += 1
        self.total_requests += 1
        logger.debug(f"Cache hit recorded for {cache_type}")
    
    def record_miss(self, cache_type: str = "audio"):
        """Record a cache miss"""
        self.misses += 1
        self.total_requests += 1
        logger.debug(f"Cache miss recorded for {cache_type}")
    
    def record_error(self, cache_type: str = "audio", error: str = ""):
        """Record a cache error"""
        self.errors += 1
        self.total_requests += 1
        logger.warning(f"Cache error recorded for {cache_type}: {error}")
    
    def update_cache_size(self, cache_type: str, size: int):
        """Update cache size metrics"""
        self.cache_sizes[cache_type] = size
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests
    
    def get_miss_rate(self) -> float:
        """Calculate cache miss rate"""
        if self.total_requests == 0:
            return 0.0
        return self.misses / self.total_requests
    
    def get_error_rate(self) -> float:
        """Calculate cache error rate"""
        if self.total_requests == 0:
            return 0.0
        return self.errors / self.total_requests
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            "total_requests": self.total_requests,
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "hit_rate": self.get_hit_rate(),
            "miss_rate": self.get_miss_rate(),
            "error_rate": self.get_error_rate(),
            "cache_sizes": self.cache_sizes.copy()
        }
    
    def reset(self):
        """Reset all metrics"""
        self.hits = 0
        self.misses = 0
        self.errors = 0
        self.total_requests = 0
        self.cache_sizes.clear()
        logger.info("Cache metrics reset")

# Global cache metrics instance
cache_metrics = CacheMetrics()

def validate_cache_key(cache_key: str) -> bool:
    """Validate that a cache key is properly formatted"""
    if not cache_key:
        return False
    
    # Should be a 64-character hex string (SHA256)
    if len(cache_key) != 64:
        return False
    
    try:
        int(cache_key, 16)  # Verify it's valid hex
        return True
    except ValueError:
        return False

def normalize_cache_parameters(
    text: str,
    voice: str,
    speed: float,
    format: str,
    language: str = "en-us"
) -> Dict[str, Any]:
    """
    Normalize cache parameters to ensure consistency
    
    This function ensures that equivalent requests generate the same cache key
    regardless of minor variations in input formatting.
    """
    return {
        "text": text.strip(),
        "voice": voice.lower().strip(),
        "speed": round(float(speed), 2),
        "format": format.lower().strip(),
        "language": language.lower().strip()
    }

def debug_cache_key_generation(
    text: str,
    voice: str,
    speed: float = 1.0,
    format: str = "mp3",
    language: str = "en-us"
) -> Dict[str, str]:
    """
    Debug cache key generation by showing intermediate steps
    Useful for troubleshooting cache key inconsistencies
    """
    normalized = normalize_cache_parameters(text, voice, speed, format, language)
    
    key_components = {
        "text": normalized["text"],
        "voice": normalized["voice"],
        "speed": normalized["speed"],
        "format": normalized["format"],
        "language": normalized["language"]
    }
    
    key_string = json.dumps(key_components, sort_keys=True, separators=(',', ':'))
    cache_key = hashlib.sha256(key_string.encode('utf-8')).hexdigest()
    
    return {
        "normalized_params": str(normalized),
        "key_string": key_string,
        "cache_key": cache_key,
        "cache_key_short": cache_key[:16] + "..."
    }
