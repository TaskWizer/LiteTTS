#!/usr/bin/env python3
"""
Kokoro ONNX TTS API Package

A lightweight, high-performance text-to-speech API service built around the Kokoro ONNX runtime.
Provides advanced linguistic processing, emotion control, and seamless integration options.
"""

__version__ = "1.0.0"
__author__ = "Kokoro TTS Team"
__description__ = "Lightweight TTS API with advanced linguistic features"

# Core configuration and exceptions
from .config import ConfigManager, config
from .exceptions import (
    KokoroError,
    ModelError,
    VoiceError,
    AudioError,
    ValidationError,
    CacheError,
    ConfigurationError,
    DownloadError
)
from .logging_config import setup_logging, get_request_logger

# Conditional imports to avoid dependency issues during structure validation
try:
    # Main API components
    from .api import TTSAPIRouter, RequestValidator, ErrorHandler, ResponseFormatter
    _API_AVAILABLE = True
except ImportError:
    _API_AVAILABLE = False

try:
    # Core processing engines
    from .tts import KokoroTTSEngine, EmotionController, ChunkProcessor, TTSSynthesizer
    _TTS_AVAILABLE = True
except ImportError:
    _TTS_AVAILABLE = False

try:
    from .nlp import NLPProcessor, TextNormalizer, HomographResolver, PhoneticProcessor
    _NLP_AVAILABLE = True
except ImportError:
    _NLP_AVAILABLE = False

try:
    from .voice import VoiceManager, VoiceDownloader, VoiceValidator, VoiceMetadataManager
    _VOICE_AVAILABLE = True
except ImportError:
    _VOICE_AVAILABLE = False

try:
    from .audio import AudioProcessor, AudioSegment, AudioFormatConverter, AudioStreamer
    _AUDIO_AVAILABLE = True
except ImportError:
    _AUDIO_AVAILABLE = False

try:
    from .cache import EnhancedCacheManager, AudioCache, TextCache
    _CACHE_AVAILABLE = True
except ImportError:
    _CACHE_AVAILABLE = False

# Build __all__ dynamically based on available imports
__all__ = [
    # Version and metadata
    "__version__",
    "__author__", 
    "__description__",
    
    # Configuration (always available)
    "ConfigManager",
    "config",
    "setup_logging",
    "get_request_logger",
    
    # Exceptions (always available)
    "KokoroError",
    "ModelError",
    "VoiceError", 
    "AudioError",
    "ValidationError",
    "CacheError",
    "ConfigurationError",
    "DownloadError",
]

# Add conditional exports
if _API_AVAILABLE:
    __all__.extend([
        "TTSAPIRouter",
        "RequestValidator", 
        "ErrorHandler",
        "ResponseFormatter",
    ])

if _TTS_AVAILABLE:
    __all__.extend([
        "KokoroTTSEngine",
        "EmotionController",
        "ChunkProcessor",
        "TTSSynthesizer",
    ])

if _NLP_AVAILABLE:
    __all__.extend([
        "NLPProcessor",
        "TextNormalizer",
        "HomographResolver",
        "PhoneticProcessor",
    ])

if _VOICE_AVAILABLE:
    __all__.extend([
        "VoiceManager",
        "VoiceDownloader",
        "VoiceValidator",
        "VoiceMetadataManager",
    ])

if _AUDIO_AVAILABLE:
    __all__.extend([
        "AudioProcessor",
        "AudioSegment", 
        "AudioFormatConverter",
        "AudioStreamer",
    ])

if _CACHE_AVAILABLE:
    __all__.extend([
        "EnhancedCacheManager",
        "AudioCache",
        "TextCache",
    ])