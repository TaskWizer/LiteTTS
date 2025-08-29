#!/usr/bin/env python3
"""
Specialized audio cache for TTS generated audio
"""

import hashlib
from typing import Dict, List, Optional, Any
import logging

from .manager import EnhancedCacheManager
from ..audio.audio_segment import AudioSegment
from ..models import generate_cache_key
from .cache_utils import CacheKeyGenerator, cache_metrics

logger = logging.getLogger(__name__)

class AudioCache:
    """Specialized cache for TTS generated audio"""
    
    def __init__(self, cache_dir: str = "LiteTTS/cache/audio",
                 max_memory_size: int = None,  # Will use config default
                 max_disk_size: int = None,    # Will use config default
                 config=None):

        # Use config values or fallback to defaults
        if config and hasattr(config, 'cache'):
            memory_size = max_memory_size or (config.cache.audio_memory_cache_mb * 1024 * 1024)
            disk_size = max_disk_size or (config.cache.audio_disk_cache_mb * 1024 * 1024)
            self.default_ttl = config.cache.ttl
        else:
            # Fallback defaults
            memory_size = max_memory_size or (50 * 1024 * 1024)   # 50MB
            disk_size = max_disk_size or (500 * 1024 * 1024)     # 500MB
            self.default_ttl = 3600  # 1 hour

        self.cache_manager = EnhancedCacheManager(
            cache_dir=cache_dir,
            max_memory_size=memory_size,
            max_disk_size=disk_size,
            config=config
        )
        
        logger.info("Audio cache initialized")
    
    def get_cached_audio(self, text: str, voice: str, speed: float = 1.0,
                        format: str = "wav", emotion: str = None,
                        emotion_strength: float = 1.0) -> Optional[AudioSegment]:
        """Get cached audio segment"""
        cache_key = self._generate_audio_cache_key(
            text, voice, speed, format, emotion, emotion_strength
        )
        
        cached_data = self.cache_manager.get(cache_key)
        
        if cached_data and isinstance(cached_data, AudioSegment):
            cache_metrics.record_hit("audio")
            logger.debug(f"Audio cache hit: {cache_key[:16]}...")
            return cached_data

        cache_metrics.record_miss("audio")
        return None
    
    def cache_audio(self, audio_segment: AudioSegment, text: str, voice: str,
                   speed: float = 1.0, format: str = "wav", emotion: str = None,
                   emotion_strength: float = 1.0, ttl: int = None) -> bool:
        """Cache audio segment"""
        cache_key = self._generate_audio_cache_key(
            text, voice, speed, format, emotion, emotion_strength
        )
        
        if ttl is None:
            ttl = self.default_ttl
        
        # Add tags for better cache management
        tags = ['audio', f'voice:{voice}', f'format:{format}']
        if emotion:
            tags.append(f'emotion:{emotion}')
        
        success = self.cache_manager.put(
            cache_key, audio_segment, ttl_seconds=ttl, tags=tags
        )
        
        if success:
            logger.debug(f"Cached audio: {cache_key[:16]}... ({audio_segment.duration:.2f}s)")
        
        return success
    
    def _generate_audio_cache_key(self, text: str, voice: str, speed: float,
                                 format: str, emotion: str = None,
                                 emotion_strength: float = 1.0) -> str:
        """Generate standardized cache key for audio using CacheKeyGenerator"""
        return CacheKeyGenerator.generate_audio_cache_key(
            text=text,
            voice=voice,
            speed=speed,
            format=format,
            emotion=emotion,
            emotion_strength=emotion_strength
        )
    
    def preload_common_phrases(self, phrases: List[str], voice: str) -> Dict[str, bool]:
        """Preload common phrases into cache"""
        results = {}
        
        for phrase in phrases:
            # This would typically be called after synthesis
            # For now, we just mark the intent to cache these phrases
            cache_key = self._generate_audio_cache_key(phrase, voice, 1.0, "wav")
            results[phrase] = True  # Placeholder
        
        logger.info(f"Marked {len(phrases)} phrases for preloading")
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get audio cache statistics"""
        base_stats = self.cache_manager.get_stats()
        
        # Add audio-specific stats
        audio_stats = {
            'audio_cache': base_stats,
            'cache_type': 'audio',
            'default_ttl_seconds': self.default_ttl
        }
        
        return audio_stats
    
    def clear_voice_cache(self, voice: str):
        """Clear cache for specific voice"""
        self.cache_manager.clear(tags=[f'voice:{voice}'])
        logger.info(f"Cleared cache for voice: {voice}")
    
    def clear_format_cache(self, format: str):
        """Clear cache for specific format"""
        self.cache_manager.clear(tags=[f'format:{format}'])
        logger.info(f"Cleared cache for format: {format}")
    
    def clear_emotion_cache(self, emotion: str):
        """Clear cache for specific emotion"""
        self.cache_manager.clear(tags=[f'emotion:{emotion}'])
        logger.info(f"Cleared cache for emotion: {emotion}")
    
    def optimize(self):
        """Optimize audio cache"""
        self.cache_manager.optimize()
    
    def cleanup_expired(self) -> int:
        """Clean up expired audio cache entries"""
        return self.cache_manager.cleanup_expired()
    
    def shutdown(self):
        """Shutdown audio cache"""
        self.cache_manager.shutdown()

class TextCache:
    """Cache for processed text (NLP results)"""
    
    def __init__(self, cache_dir: str = "LiteTTS/cache/text",
                 max_memory_size: int = None,   # Will use config default
                 max_disk_size: int = None,     # Will use config default
                 config=None):

        # Use config values or fallback to defaults
        if config and hasattr(config, 'cache'):
            memory_size = max_memory_size or (config.cache.text_memory_cache_mb * 1024 * 1024)
            disk_size = max_disk_size or (config.cache.text_disk_cache_mb * 1024 * 1024)
            self.default_ttl = config.cache.text_cache_ttl
        else:
            # Fallback defaults
            memory_size = max_memory_size or (10 * 1024 * 1024)   # 10MB
            disk_size = max_disk_size or (50 * 1024 * 1024)      # 50MB
            self.default_ttl = 86400  # 24 hours

        self.cache_manager = EnhancedCacheManager(
            cache_dir=cache_dir,
            max_memory_size=memory_size,
            max_disk_size=disk_size,
            config=config
        )
        
        logger.info("Text cache initialized")
    
    def get_processed_text(self, original_text: str, 
                          normalization_options: Dict[str, Any]) -> Optional[str]:
        """Get cached processed text"""
        cache_key = self._generate_text_cache_key(original_text, normalization_options)
        
        cached_text = self.cache_manager.get(cache_key)
        
        if cached_text and isinstance(cached_text, str):
            logger.debug(f"Text cache hit: {cache_key[:16]}...")
            return cached_text
        
        return None
    
    def cache_processed_text(self, original_text: str, processed_text: str,
                           normalization_options: Dict[str, Any], ttl: int = None) -> bool:
        """Cache processed text"""
        cache_key = self._generate_text_cache_key(original_text, normalization_options)
        
        if ttl is None:
            ttl = self.default_ttl
        
        tags = ['text', 'nlp_processed']
        
        success = self.cache_manager.put(
            cache_key, processed_text, ttl_seconds=ttl, tags=tags
        )
        
        if success:
            logger.debug(f"Cached processed text: {cache_key[:16]}...")
        
        return success
    
    def _generate_text_cache_key(self, text: str, 
                                normalization_options: Dict[str, Any]) -> str:
        """Generate cache key for processed text"""
        # Create a stable key from text and options
        options_str = str(sorted(normalization_options.items()))
        key_string = f"{text}:{options_str}"
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get text cache statistics"""
        base_stats = self.cache_manager.get_stats()
        
        text_stats = {
            'text_cache': base_stats,
            'cache_type': 'text',
            'default_ttl_seconds': self.default_ttl
        }
        
        return text_stats
    
    def clear_all(self):
        """Clear all text cache"""
        self.cache_manager.clear()
        logger.info("Cleared all text cache")
    
    def optimize(self):
        """Optimize text cache"""
        self.cache_manager.optimize()
    
    def cleanup_expired(self) -> int:
        """Clean up expired text cache entries"""
        return self.cache_manager.cleanup_expired()
    
    def shutdown(self):
        """Shutdown text cache"""
        self.cache_manager.shutdown()

class CacheWarmer:
    """Cache warming service for predictive caching"""
    
    def __init__(self, audio_cache: AudioCache, text_cache: TextCache):
        self.audio_cache = audio_cache
        self.text_cache = text_cache
        
        # Common phrases to preload
        self.common_phrases = [
            "Hello, how are you?",
            "Thank you very much.",
            "Please wait a moment.",
            "I'm sorry, I don't understand.",
            "Have a great day!",
            "Welcome to our service.",
            "Is there anything else I can help you with?",
            "Please try again later.",
            "Your request has been processed.",
            "Loading, please wait..."
        ]
        
        logger.info("Cache warmer initialized")
    
    def warm_common_phrases(self, voices: List[str]) -> Dict[str, Dict[str, bool]]:
        """Warm cache with common phrases for given voices"""
        results = {}
        
        for voice in voices:
            voice_results = self.audio_cache.preload_common_phrases(
                self.common_phrases, voice
            )
            results[voice] = voice_results
        
        logger.info(f"Warmed cache for {len(voices)} voices with {len(self.common_phrases)} phrases")
        return results
    
    def warm_user_patterns(self, user_texts: List[str], voice: str) -> Dict[str, bool]:
        """Warm cache based on user usage patterns"""
        # This would analyze user patterns and preload likely requests
        # For now, just mark the texts for caching
        results = {}
        
        for text in user_texts:
            cache_key = self.audio_cache._generate_audio_cache_key(text, voice, 1.0, "wav")
            results[text] = True  # Placeholder
        
        logger.info(f"Warmed cache with {len(user_texts)} user pattern texts")
        return results
    
    def get_warming_stats(self) -> Dict[str, Any]:
        """Get cache warming statistics"""
        return {
            'common_phrases_count': len(self.common_phrases),
            'audio_cache_stats': self.audio_cache.get_cache_stats(),
            'text_cache_stats': self.text_cache.get_cache_stats()
        }