#!/usr/bin/env python3
"""
Enhanced AudioSegment class with format conversion and streaming support
"""

import numpy as np
import io
from typing import Dict, Any, Optional, Union, Iterator
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class AudioSegment:
    """Enhanced audio data structure with processing capabilities"""
    audio_data: np.ndarray
    sample_rate: int
    duration: float = 0.0
    format: str = "wav"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.duration == 0.0 and len(self.audio_data) > 0:
            self.duration = len(self.audio_data) / self.sample_rate
        
        # Ensure audio data is float32
        if self.audio_data.dtype != np.float32:
            self.audio_data = self.audio_data.astype(np.float32)
    
    @classmethod
    def from_bytes(cls, audio_bytes: bytes, sample_rate: int, format: str = "wav") -> 'AudioSegment':
        """Create AudioSegment from raw audio bytes"""
        # Convert bytes to numpy array (assuming 16-bit PCM)
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        return cls(audio_data=audio_data, sample_rate=sample_rate, format=format)
    
    @classmethod
    def silence(cls, duration: float, sample_rate: int = 24000) -> 'AudioSegment':
        """Create a silent audio segment"""
        samples = int(duration * sample_rate)
        audio_data = np.zeros(samples, dtype=np.float32)
        return cls(audio_data=audio_data, sample_rate=sample_rate, duration=duration)
    
    def to_bytes(self, format: str = None) -> bytes:
        """Convert audio data to bytes"""
        if format is None:
            format = self.format
            
        # Convert float32 to int16 for most formats
        if format.lower() in ['wav', 'mp3', 'ogg']:
            audio_int16 = (self.audio_data * 32767).astype(np.int16)
            return audio_int16.tobytes()
        else:
            return self.audio_data.tobytes()
    
    def concatenate(self, other: 'AudioSegment') -> 'AudioSegment':
        """Concatenate with another audio segment"""
        if self.sample_rate != other.sample_rate:
            raise ValueError(f"Sample rates don't match: {self.sample_rate} vs {other.sample_rate}")
        
        combined_audio = np.concatenate([self.audio_data, other.audio_data])
        combined_duration = self.duration + other.duration
        
        # Merge metadata
        combined_metadata = {**self.metadata, **other.metadata}
        
        return AudioSegment(
            audio_data=combined_audio,
            sample_rate=self.sample_rate,
            duration=combined_duration,
            format=self.format,
            metadata=combined_metadata
        )
    
    def trim(self, start_time: float = 0.0, end_time: Optional[float] = None) -> 'AudioSegment':
        """Trim audio segment to specified time range"""
        start_sample = int(start_time * self.sample_rate)
        end_sample = int(end_time * self.sample_rate) if end_time else len(self.audio_data)
        
        # Ensure bounds
        start_sample = max(0, start_sample)
        end_sample = min(len(self.audio_data), end_sample)
        
        trimmed_audio = self.audio_data[start_sample:end_sample]
        trimmed_duration = len(trimmed_audio) / self.sample_rate
        
        return AudioSegment(
            audio_data=trimmed_audio,
            sample_rate=self.sample_rate,
            duration=trimmed_duration,
            format=self.format,
            metadata=self.metadata.copy()
        )    

    def fade_in(self, duration: float) -> 'AudioSegment':
        """Apply fade-in effect"""
        fade_samples = int(duration * self.sample_rate)
        fade_samples = min(fade_samples, len(self.audio_data))
        
        audio_copy = self.audio_data.copy()
        fade_curve = np.linspace(0, 1, fade_samples)
        audio_copy[:fade_samples] *= fade_curve
        
        return AudioSegment(
            audio_data=audio_copy,
            sample_rate=self.sample_rate,
            duration=self.duration,
            format=self.format,
            metadata=self.metadata.copy()
        )
    
    def fade_out(self, duration: float) -> 'AudioSegment':
        """Apply fade-out effect"""
        fade_samples = int(duration * self.sample_rate)
        fade_samples = min(fade_samples, len(self.audio_data))
        
        audio_copy = self.audio_data.copy()
        fade_curve = np.linspace(1, 0, fade_samples)
        audio_copy[-fade_samples:] *= fade_curve
        
        return AudioSegment(
            audio_data=audio_copy,
            sample_rate=self.sample_rate,
            duration=self.duration,
            format=self.format,
            metadata=self.metadata.copy()
        )
    
    def adjust_volume(self, volume_multiplier: float) -> 'AudioSegment':
        """Adjust volume by multiplier"""
        # Clamp volume multiplier to reasonable range
        volume_multiplier = max(0.0, min(5.0, volume_multiplier))
        
        adjusted_audio = self.audio_data * volume_multiplier
        
        # Prevent clipping
        max_val = np.max(np.abs(adjusted_audio))
        if max_val > 1.0:
            adjusted_audio = adjusted_audio / max_val
        
        return AudioSegment(
            audio_data=adjusted_audio,
            sample_rate=self.sample_rate,
            duration=self.duration,
            format=self.format,
            metadata=self.metadata.copy()
        )
    
    def resample(self, target_sample_rate: int) -> 'AudioSegment':
        """Resample audio to target sample rate"""
        if self.sample_rate == target_sample_rate:
            return self
        
        # Simple linear interpolation resampling
        ratio = target_sample_rate / self.sample_rate
        new_length = int(len(self.audio_data) * ratio)
        
        # Create new time indices
        old_indices = np.linspace(0, len(self.audio_data) - 1, new_length)
        resampled_audio = np.interp(old_indices, np.arange(len(self.audio_data)), self.audio_data)
        
        return AudioSegment(
            audio_data=resampled_audio.astype(np.float32),
            sample_rate=target_sample_rate,
            duration=self.duration,  # Duration stays the same
            format=self.format,
            metadata=self.metadata.copy()
        )
    
    def get_chunks(self, chunk_duration: float) -> Iterator['AudioSegment']:
        """Split audio into chunks of specified duration"""
        chunk_samples = int(chunk_duration * self.sample_rate)
        
        for start in range(0, len(self.audio_data), chunk_samples):
            end = min(start + chunk_samples, len(self.audio_data))
            chunk_audio = self.audio_data[start:end]
            chunk_dur = len(chunk_audio) / self.sample_rate
            
            yield AudioSegment(
                audio_data=chunk_audio,
                sample_rate=self.sample_rate,
                duration=chunk_dur,
                format=self.format,
                metadata=self.metadata.copy()
            )
    
    def validate(self) -> bool:
        """Validate audio segment data"""
        try:
            # Check if audio data is valid
            if self.audio_data is None or len(self.audio_data) == 0:
                return False
            
            # Check sample rate
            if self.sample_rate <= 0:
                return False
            
            # Check for NaN or infinite values
            if np.any(np.isnan(self.audio_data)) or np.any(np.isinf(self.audio_data)):
                return False
            
            # Check duration consistency
            expected_duration = len(self.audio_data) / self.sample_rate
            if abs(self.duration - expected_duration) > 0.01:  # 10ms tolerance
                logger.warning(f"Duration mismatch: {self.duration} vs {expected_duration}")
            
            return True
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get audio segment information"""
        return {
            'duration': self.duration,
            'sample_rate': self.sample_rate,
            'samples': len(self.audio_data),
            'format': self.format,
            'channels': 1,  # Mono audio
            'bit_depth': 32,  # float32
            'size_bytes': self.audio_data.nbytes,
            'max_amplitude': float(np.max(np.abs(self.audio_data))),
            'rms_level': float(np.sqrt(np.mean(self.audio_data ** 2))),
            'metadata': self.metadata
        }