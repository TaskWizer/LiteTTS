"""
STT Models and Data Classes for LiteTTS
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import io

@dataclass
class STTConfiguration:
    """Configuration for Speech-to-Text processing"""
    model: str = "turbo"
    device: str = "cpu"
    compute_type: str = "int8"
    language: Optional[str] = "auto"
    beam_size: int = 5
    best_of: int = 5
    patience: float = 1.0
    length_penalty: float = 1.0
    repetition_penalty: float = 1.0
    no_repeat_ngram_size: int = 0
    temperature: float = 0.0
    compression_ratio_threshold: float = 2.4
    log_prob_threshold: float = -1.0
    no_speech_threshold: float = 0.6
    condition_on_previous_text: bool = True
    prompt_reset_on_temperature: float = 0.5
    initial_prompt: Optional[str] = None
    prefix: Optional[str] = None
    suppress_blank: bool = True
    suppress_tokens: List[int] = field(default_factory=lambda: [-1])
    without_timestamps: bool = False
    max_initial_timestamp: float = 1.0
    word_timestamps: bool = False
    prepend_punctuations: str = "\"'¿([{-"
    append_punctuations: str = "\"'.。,，!！?？:：\")]}、"
    vad_filter: bool = True
    vad_parameters: Dict[str, Any] = field(default_factory=dict)
    supported_formats: List[str] = field(default_factory=list)
    max_file_size_mb: int = 25
    timeout_seconds: int = 30
    
    def __post_init__(self):
        if self.suppress_tokens is None:
            self.suppress_tokens = [-1]
        
        if self.vad_parameters is None:
            self.vad_parameters = {
                "threshold": 0.5,
                "min_speech_duration_ms": 250,
                "max_speech_duration_s": 30,
                "min_silence_duration_ms": 2000,
                "window_size_samples": 1024,
                "speech_pad_ms": 400
            }
        
        if self.supported_formats is None:
            self.supported_formats = ["wav", "mp3", "flac", "m4a", "ogg", "opus"]

@dataclass
class STTRequest:
    """Request for Speech-to-Text processing"""
    audio: Union[str, Path, bytes, io.BytesIO]
    language: Optional[str] = None
    model: Optional[str] = None
    response_format: str = "json"  # json, text, srt, vtt
    temperature: Optional[float] = None
    timestamp_granularities: List[str] = field(default_factory=lambda: ["segment"])

@dataclass 
class STTSegment:
    """A segment of transcribed speech"""
    id: int
    seek: float
    start: float
    end: float
    text: str
    tokens: List[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float
    words: Optional[List[Dict[str, Any]]] = None

@dataclass
class STTResponse:
    """Response from Speech-to-Text processing"""
    text: str
    language: str
    duration: float
    segments: List[STTSegment]
    words: Optional[List[Dict[str, Any]]] = None
    
    # Processing metadata
    processing_time: float = 0.0
    model_used: str = ""
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "text": self.text,
            "language": self.language,
            "duration": self.duration,
            "segments": [
                {
                    "id": seg.id,
                    "seek": seg.seek,
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text,
                    "tokens": seg.tokens,
                    "temperature": seg.temperature,
                    "avg_logprob": seg.avg_logprob,
                    "compression_ratio": seg.compression_ratio,
                    "no_speech_prob": seg.no_speech_prob,
                    "words": seg.words
                }
                for seg in self.segments
            ],
            "words": self.words,
            "processing_time": self.processing_time,
            "model_used": self.model_used,
            "confidence": self.confidence
        }
    
    def to_text(self) -> str:
        """Get plain text transcription"""
        return self.text
    
    def to_srt(self) -> str:
        """Convert to SRT subtitle format"""
        srt_content = []
        for i, segment in enumerate(self.segments, 1):
            start_time = self._format_timestamp(segment.start)
            end_time = self._format_timestamp(segment.end)
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(segment.text.strip())
            srt_content.append("")
        return "\n".join(srt_content)
    
    def to_vtt(self) -> str:
        """Convert to WebVTT format"""
        vtt_content = ["WEBVTT", ""]
        for segment in self.segments:
            start_time = self._format_timestamp(segment.start, vtt=True)
            end_time = self._format_timestamp(segment.end, vtt=True)
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(segment.text.strip())
            vtt_content.append("")
        return "\n".join(vtt_content)
    
    def _format_timestamp(self, seconds: float, vtt: bool = False) -> str:
        """Format timestamp for subtitle formats"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        if vtt:
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
        else:
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")

@dataclass
class STTError:
    """STT processing error"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
