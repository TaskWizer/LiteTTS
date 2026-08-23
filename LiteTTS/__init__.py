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
# Conditional imports to avoid dependency issues during structure validation
import importlib.util

from .config import ConfigManager, config
from .exceptions import (
    AudioError,
    CacheError,
    ConfigurationError,
    DownloadError,
    KokoroError,
    ModelError,
    ValidationError,
    VoiceError,
)
from .logging_config import get_request_logger, setup_logging


def _is_available(module_name: str) -> bool:
    """Check if a module is available without importing it."""
    # Handle both relative (".api") and absolute ("LiteTTS.api") module names
    if module_name.startswith('.'):
        # Relative import - resolve from this package
        return importlib.util.find_spec(module_name, package="LiteTTS") is not None
    else:
        return importlib.util.find_spec(module_name) is not None

# Main API components
_API_AVAILABLE = _is_available(".api")

# Core processing engines
_TTS_AVAILABLE = _is_available(".tts")

# NLP components
_NLP_AVAILABLE = _is_available(".nlp")

# Voice components
_VOICE_AVAILABLE = _is_available(".voice")

# Audio components
_AUDIO_AVAILABLE = _is_available(".audio")

# Cache components
_CACHE_AVAILABLE = _is_available(".cache")

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
