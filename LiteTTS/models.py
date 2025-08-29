#!/usr/bin/env python3
"""
Core data models and type definitions for Kokoro ONNX TTS API
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Protocol
from datetime import datetime
from pathlib import Path
import numpy as np
from pydantic import BaseModel, Field
from enum import Enum

# Configuration Models
@dataclass
class TTSConfiguration:
    """System configuration settings"""
    model_path: str
    voices_path: str
    device: str = "cpu"
    sample_rate: int = 24000
    chunk_size: int = 100
    cache_size: int = 1000
    max_text_length: int = 1000
    default_voice: str = "af_heart"

# Voice and Audio Models
@dataclass
class VoiceMetadata:
    """Voice metadata and categorization"""
    name: str
    gender: str
    accent: str = "american"
    voice_type: str = "neural"
    quality_rating: float = 4.0
    language: str = "en-us"
    file_size: int = 0
    description: str = ""

@dataclass
class VoiceEmbedding:
    """Voice embedding data structure"""
    name: str
    embedding_data: Optional[np.ndarray] = None
    metadata: Optional[VoiceMetadata] = None
    loaded_at: Optional[datetime] = None
    file_hash: str = ""
    
    @property
    def shape(self):
        """Compatibility property for accessing embedding data shape"""
        if self.embedding_data is not None:
            return self.embedding_data.shape
        return None
    
    @property
    def dtype(self):
        """Compatibility property for accessing embedding data dtype"""
        if self.embedding_data is not None:
            return self.embedding_data.dtype
        return None
    
    def __array__(self):
        """Allow numpy operations directly on VoiceEmbedding object"""
        if self.embedding_data is not None:
            return self.embedding_data
        raise ValueError("No embedding data available")
    
    def numpy(self):
        """Return numpy array of embedding data"""
        if self.embedding_data is not None:
            return self.embedding_data
        raise ValueError("No embedding data available")

@dataclass
class AudioSegment:
    """Audio data structure"""
    audio_data: np.ndarray
    sample_rate: int
    duration: float
    format: str = "wav"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.duration == 0 and len(self.audio_data) > 0:
            self.duration = len(self.audio_data) / self.sample_rate

# Request/Response Models
class NormalizationOptions(BaseModel):
    """Text normalization configuration"""
    normalize: bool = True
    unit_normalization: bool = False
    url_normalization: bool = True
    email_normalization: bool = True
    optional_pluralization_normalization: bool = True
    phone_normalization: bool = True
    replace_remaining_symbols: bool = True

class TTSRequest(BaseModel):
    """Comprehensive TTS request model"""
    model: str = "kokoro"
    input: str = Field(..., description="Text to synthesize")
    voice: str = "af_heart"
    response_format: str = "mp3"
    download_format: str = "mp3"
    speed: float = Field(default=1.0, ge=0.1, le=3.0)
    stream: bool = True
    return_download_link: bool = False
    lang_code: str = "en-us"
    volume_multiplier: float = Field(default=1.0, ge=0.1, le=5.0)
    normalization_options: NormalizationOptions = Field(default_factory=NormalizationOptions)

    # Time-stretching optimization parameters (beta feature)
    time_stretching_enabled: Optional[bool] = Field(default=None, description="Enable time-stretching optimization (beta)")
    time_stretching_rate: Optional[int] = Field(default=None, ge=10, le=100, description="Time-stretching compression rate (10-100%)")
    time_stretching_quality: Optional[str] = Field(default=None, description="Time-stretching quality: low, medium, high")

class TTSResponse(BaseModel):
    """TTS response metadata"""
    audio_data: bytes
    content_type: str
    duration: float
    processing_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Processing Models
@dataclass
class ProcessingMetrics:
    """Performance and processing metrics"""
    request_id: str
    text_length: int
    processing_time: float
    audio_duration: float
    voice_used: str
    cache_hit: bool = False
    error_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ProsodyInfo:
    """Prosody analysis information"""
    pauses: List[Dict[str, Any]] = field(default_factory=list)
    emphasis: List[Dict[str, Any]] = field(default_factory=list)
    intonation: List[Dict[str, Any]] = field(default_factory=list)

# Protocol Interfaces
class TTSEngineProtocol(Protocol):
    """Interface for TTS engines"""
    
    def synthesize(self, text: str, voice: str, speed: float) -> AudioSegment:
        """Synthesize text to audio"""
        ...
    
    def load_voice(self, voice_name: str) -> VoiceEmbedding:
        """Load a voice embedding"""
        ...
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voices"""
        ...

class NLPProcessorProtocol(Protocol):
    """Interface for NLP processors"""
    
    def normalize_text(self, text: str) -> str:
        """Normalize input text"""
        ...
    
    def resolve_homographs(self, text: str) -> str:
        """Resolve homograph pronunciations"""
        ...
    
    def process_phonetics(self, text: str) -> str:
        """Process phonetic markers"""
        ...
    
    def analyze_prosody(self, text: str) -> ProsodyInfo:
        """Analyze text for prosody information"""
        ...

class CacheManagerProtocol(Protocol):
    """Interface for cache management"""
    
    def get_cached_audio(self, cache_key: str) -> Optional[AudioSegment]:
        """Get cached audio segment"""
        ...
    
    def cache_audio(self, cache_key: str, audio: AudioSegment, ttl: int = 3600):
        """Cache audio segment"""
        ...
    
    def get_voice_embedding(self, voice_name: str) -> Optional[VoiceEmbedding]:
        """Get cached voice embedding"""
        ...
    
    def preload_voices(self, voice_names: List[str]):
        """Preload voice embeddings"""
        ...

# Error Models
class TTSError(Exception):
    """Base TTS error"""
    def __init__(self, message: str, error_code: str = "TTS_ERROR", details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

class VoiceNotFoundError(TTSError):
    """Voice not found error"""
    def __init__(self, voice_name: str, available_voices: List[str] = None):
        super().__init__(
            f"Voice '{voice_name}' not found",
            "VOICE_NOT_FOUND",
            {"requested_voice": voice_name, "available_voices": available_voices or []}
        )

class ModelLoadError(TTSError):
    """Model loading error"""
    def __init__(self, model_path: str, original_error: str):
        super().__init__(
            f"Failed to load model from {model_path}",
            "MODEL_LOAD_ERROR",
            {"model_path": model_path, "original_error": original_error}
        )

class AudioGenerationError(TTSError):
    """Audio generation error"""
    def __init__(self, text: str, voice: str, original_error: str):
        super().__init__(
            f"Failed to generate audio for text '{text[:50]}...' with voice '{voice}'",
            "AUDIO_GENERATION_ERROR",
            {"text_length": len(text), "voice": voice, "original_error": original_error}
        )

# Utility Functions
def parse_voice_attributes(voice_name: str) -> Dict[str, str]:
    """Parse voice attributes from voice name using naming convention.

    Voice naming convention: [region][gender]_[name]
    - First character: region (A=American, B=British, J=Japanese, Z=Chinese, S=Spanish, F=French, H=Hindi, I=Italian, P=Portuguese)
    - Second character: gender (f=female, m=male)

    Examples:
    - af_heart → American Female
    - am_adam → American Male
    - bf_alice → British Female
    - bm_daniel → British Male
    """
    if len(voice_name) < 2 or '_' not in voice_name:
        return {"gender": "unknown", "region": "unknown", "language": "en-us"}

    prefix = voice_name.split('_')[0]
    if len(prefix) < 2:
        return {"gender": "unknown", "region": "unknown", "language": "en-us"}

    region_char = prefix[0].upper()
    gender_char = prefix[1].lower()

    # Gender mapping
    gender = "female" if gender_char == 'f' else "male" if gender_char == 'm' else "unknown"

    # Region and language mapping
    region_mapping = {
        'A': {"region": "american", "language": "en-us", "flag": "🇺🇸"},
        'B': {"region": "british", "language": "en-gb", "flag": "🇬🇧"},
        'J': {"region": "japanese", "language": "ja-jp", "flag": "🇯🇵"},
        'Z': {"region": "chinese", "language": "zh-cn", "flag": "🇨🇳"},
        'S': {"region": "spanish", "language": "es-es", "flag": "🇪🇸"},
        'F': {"region": "french", "language": "fr-fr", "flag": "🇫🇷"},
        'H': {"region": "hindi", "language": "hi-in", "flag": "🇮🇳"},
        'I': {"region": "italian", "language": "it-it", "flag": "🇮🇹"},
        'P': {"region": "portuguese", "language": "pt-br", "flag": "🇧🇷"}
    }

    region_info = region_mapping.get(region_char, {"region": "unknown", "language": "en-us", "flag": "🌍"})

    return {
        "gender": gender,
        "region": region_info["region"],
        "language": region_info["language"],
        "flag": region_info["flag"]
    }

def create_voice_metadata(voice_name: str) -> VoiceMetadata:
    """Create voice metadata from voice name"""
    attributes = parse_voice_attributes(voice_name)

    # Voice descriptions
    descriptions = {
        "af_heart": "Warm, natural female voice",
        "af_bella": "Clear, articulate female voice",
        "af_alloy": "Smooth, professional female voice",
        "af_aoede": "Expressive female voice",
        "af_jessica": "Friendly female voice",
        "af_nicole": "Confident female voice",
        "af_sky": "Light, airy female voice",
        "am_puck": "Natural, conversational male voice",
        "am_liam": "Deep, authoritative male voice"
    }

    return VoiceMetadata(
        name=voice_name,
        gender=attributes["gender"],
        accent=attributes["region"],
        language=attributes["language"],
        description=descriptions.get(voice_name, f"{attributes['region'].title()} {attributes['gender']} voice")
    )

def generate_cache_key(text: str, voice: str, speed: float, format: str) -> str:
    """Generate cache key for audio segments"""
    import hashlib
    key_string = f"{text}:{voice}:{speed}:{format}"
    return hashlib.md5(key_string.encode()).hexdigest()

def validate_tts_request(request: TTSRequest) -> List[str]:
    """Validate TTS request and return list of errors"""
    errors = []
    
    if not request.input or not request.input.strip():
        errors.append("Input text cannot be empty")
    
    if len(request.input) > 10000:  # Reasonable limit
        errors.append("Input text too long (max 10000 characters)")
    
    if request.response_format not in ["mp3", "wav", "ogg", "flac"]:
        errors.append("Invalid response format")
    
    return errors