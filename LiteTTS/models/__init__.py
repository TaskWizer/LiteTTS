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

# Import TTS models from the sibling models.py file
# Note: models.py is at LiteTTS/models.py (sibling to this directory)
import importlib.util
import sys
from pathlib import Path

# Load models.py directly to avoid circular import
_models_path = Path(__file__).parent.parent / "models.py"
_spec = importlib.util.spec_from_file_location("LiteTTS.models_tts", _models_path)
_models_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_models_module)

# Now import from the loaded module
TTSRequest = _models_module.TTSRequest
TTSResponse = _models_module.TTSResponse
TTSConfiguration = _models_module.TTSConfiguration
AudioSegment = _models_module.AudioSegment
VoiceEmbedding = _models_module.VoiceEmbedding
validate_tts_request = _models_module.validate_tts_request
generate_cache_key = _models_module.generate_cache_key
TTSError = _models_module.TTSError
VoiceNotFoundError = _models_module.VoiceNotFoundError
ModelLoadError = _models_module.ModelLoadError
AudioGenerationError = _models_module.AudioGenerationError

__all__ = [
    'ModelManager',
    'ModelInfo',
    'DownloadProgress',
    'TTSRequest',
    'TTSResponse',
    'TTSConfiguration',
    'AudioSegment',
    'VoiceEmbedding',
    'validate_tts_request',
    'generate_cache_key',
    'TTSError',
    'VoiceNotFoundError',
    'ModelLoadError',
    'AudioGenerationError'
]

__version__ = '1.0.0'
