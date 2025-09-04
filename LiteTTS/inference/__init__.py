#!/usr/bin/env python3
"""
Inference backend abstraction for LiteTTS
Supports multiple inference backends: ONNX, GGUF, etc.
"""

from .base import BaseInferenceBackend, InferenceConfig, ModelInputs, ModelOutputs
from .onnx_backend import ONNXInferenceBackend
from .gguf_backend import GGUFInferenceBackend
from .factory import InferenceBackendFactory

__all__ = [
    'BaseInferenceBackend',
    'InferenceConfig', 
    'ModelInputs',
    'ModelOutputs',
    'ONNXInferenceBackend',
    'GGUFInferenceBackend',
    'InferenceBackendFactory'
]
