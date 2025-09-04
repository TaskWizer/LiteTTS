#!/usr/bin/env python3
"""
GGUF inference backend for LiteTTS
This module provides GGUF model support using TTS.cpp integration
"""

# Import the working TTSCppBackend implementation
from .ttscpp_backend import TTSCppBackend

# Alias TTSCppBackend as GGUFInferenceBackend for backward compatibility
GGUFInferenceBackend = TTSCppBackend

# Export the main class
__all__ = ['GGUFInferenceBackend']
