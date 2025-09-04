#!/usr/bin/env python3
"""
Kokoro TTS Models Package

This package provides model management functionality for the Kokoro ONNX TTS API,
including support for multiple ONNX model variants with dynamic discovery
and caching capabilities.

Features:
- Multi-model support (base, quantized, half-precision variants)
- Dynamic model discovery from HuggingFace repository
- Model integrity validation and caching
- Automatic model downloading and management

Available modules:
- manager: ModelManager class for comprehensive model management
"""

from .manager import ModelManager, ModelInfo, DownloadProgress

# Import TTS models from the parent models.py file
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import TTSRequest, TTSResponse, TTSConfiguration, AudioSegment, VoiceEmbedding, validate_tts_request

__all__ = [
    'ModelManager',
    'ModelInfo',
    'DownloadProgress',
    'TTSRequest',
    'TTSResponse',
    'TTSConfiguration',
    'AudioSegment',
    'VoiceEmbedding',
    'validate_tts_request'
]

__version__ = '1.0.0'
