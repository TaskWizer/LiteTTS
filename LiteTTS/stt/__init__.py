"""
LiteTTS Speech-to-Text (STT) Module
Provides faster-whisper integration for high-performance speech recognition
"""

from .faster_whisper_stt import FasterWhisperSTT
from .stt_models import STTRequest, STTResponse, STTConfiguration

__all__ = [
    "FasterWhisperSTT",
    "STTRequest", 
    "STTResponse",
    "STTConfiguration"
]
