#!/usr/bin/env python3
"""
Main audio processor that orchestrates all audio processing
"""

import numpy as np
from typing import List, Dict, Any, Optional, Iterator, AsyncIterator
import logging

from .audio_segment import AudioSegment
from .format_converter import AudioFormatConverter
from .streaming import AudioStreamer, StreamChunk

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Main audio processor that handles all audio operations"""
    
    def __init__(self, chunk_duration: float = 1.0):
        self.format_converter = AudioFormatConverter()
        self.streamer = AudioStreamer(chunk_duration)
        
    def create_audio_segment(self, audio_data: np.ndarray, sample_rate: int,
                           format: str = "wav") -> AudioSegment:
        """Create an AudioSegment from raw audio data"""
        return AudioSegment(
            audio_data=audio_data,
            sample_rate=sample_rate,
            format=format
        )
    
    def concatenate_segments(self, segments: List[AudioSegment]) -> AudioSegment:
        """Concatenate multiple audio segments"""
        if not segments:
            raise ValueError("No segments to concatenate")
        
        if len(segments) == 1:
            return segments[0]
        
        result = segments[0]
        for segment in segments[1:]:
            result = result.concatenate(segment)
        
        return result
    
    def apply_crossfade(self, segments: List[AudioSegment], 
                       fade_duration: float = 0.1) -> AudioSegment:
        """Concatenate segments with crossfade transitions"""
        if not segments:
            raise ValueError("No segments to concatenate")
        
        if len(segments) == 1:
            return segments[0]
        
        result = segments[0]
        
        for segment in segments[1:]:
            # Apply fade out to current result
            fade_out_result = result.fade_out(fade_duration)
            
            # Apply fade in to next segment
            fade_in_segment = segment.fade_in(fade_duration)
            
            # Calculate overlap
            overlap_samples = int(fade_duration * result.sample_rate)
            
            if len(fade_out_result.audio_data) > overlap_samples:
                # Split the fade-out result
                pre_overlap = fade_out_result.audio_data[:-overlap_samples]
                overlap_part1 = fade_out_result.audio_data[-overlap_samples:]
                
                # Get overlap part from fade-in segment
                overlap_part2 = fade_in_segment.audio_data[:overlap_samples]
                post_overlap = fade_in_segment.audio_data[overlap_samples:]
                
                # Mix the overlapping parts
                mixed_overlap = overlap_part1 + overlap_part2
                
                # Combine all parts
                combined_audio = np.concatenate([pre_overlap, mixed_overlap, post_overlap])
                
                result = AudioSegment(
                    audio_data=combined_audio,
                    sample_rate=result.sample_rate,
                    format=result.format
                )
            else:
                # Fallback to simple concatenation
                result = result.concatenate(segment)
        
        return result    
    
    def process_for_streaming(self, audio_segment: AudioSegment, 
                            format: str = "mp3") -> Iterator[StreamChunk]:
        """Process audio for streaming"""
        return self.streamer.stream_audio_sync(audio_segment, format)
    
    async def process_for_async_streaming(self, audio_segment: AudioSegment,
                                        format: str = "mp3") -> AsyncIterator[StreamChunk]:
        """Process audio for async streaming"""
        async for chunk in self.streamer.stream_audio_async(audio_segment, format):
            yield chunk
    
    def convert_format(self, audio_segment: AudioSegment, target_format: str,
                      **kwargs) -> bytes:
        """Convert audio segment to target format"""
        return self.format_converter.convert_format(
            audio_segment.audio_data,
            audio_segment.sample_rate,
            target_format,
            **kwargs
        )
    
    def validate_audio(self, audio_segment: AudioSegment) -> Dict[str, Any]:
        """Validate audio segment and return validation results"""
        validation_result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        try:
            # Basic validation
            if audio_segment.audio_data is None:
                validation_result['errors'].append("Audio data is None")
                return validation_result
            
            if len(audio_segment.audio_data) == 0:
                validation_result['errors'].append("Audio data is empty")
                return validation_result
            
            if audio_segment.sample_rate <= 0:
                validation_result['errors'].append(f"Invalid sample rate: {audio_segment.sample_rate}")
                return validation_result
            
            # Check for NaN or infinite values
            if np.any(np.isnan(audio_segment.audio_data)):
                validation_result['errors'].append("Audio data contains NaN values")
            
            if np.any(np.isinf(audio_segment.audio_data)):
                validation_result['errors'].append("Audio data contains infinite values")
            
            # Check amplitude range
            max_amplitude = np.max(np.abs(audio_segment.audio_data))
            if max_amplitude > 1.0:
                validation_result['warnings'].append(f"Audio amplitude exceeds 1.0: {max_amplitude}")
            
            if max_amplitude < 0.001:
                validation_result['warnings'].append(f"Audio amplitude very low: {max_amplitude}")
            
            # Check duration consistency
            expected_duration = len(audio_segment.audio_data) / audio_segment.sample_rate
            if abs(audio_segment.duration - expected_duration) > 0.01:
                validation_result['warnings'].append(
                    f"Duration mismatch: {audio_segment.duration} vs {expected_duration}"
                )
            
            # Add info
            validation_result['info'] = audio_segment.get_info()
            
            # Set valid if no errors
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
        except Exception as e:
            validation_result['errors'].append(f"Validation exception: {str(e)}")
        
        return validation_result
    
    def optimize_for_streaming(self, audio_segment: AudioSegment) -> AudioSegment:
        """Optimize audio segment for streaming"""
        # Get configurable values
        from ..config import config
        if hasattr(config, 'audio'):
            normalization_threshold = config.audio.normalization_threshold
        else:
            normalization_threshold = 0.95

        # Apply gentle compression to reduce dynamic range
        compressed_audio = self._apply_compression(audio_segment.audio_data)

        # Normalize to prevent clipping
        max_val = np.max(np.abs(compressed_audio))
        if max_val > normalization_threshold:
            compressed_audio = compressed_audio * (normalization_threshold / max_val)

        return AudioSegment(
            audio_data=compressed_audio,
            sample_rate=audio_segment.sample_rate,
            duration=audio_segment.duration,
            format=audio_segment.format,
            metadata={**audio_segment.metadata, 'optimized_for_streaming': True}
        )
    
    def _apply_compression(self, audio_data: np.ndarray,
                          threshold: float = None, ratio: float = None) -> np.ndarray:
        """Apply simple compression to audio data"""
        # Get configurable values
        from ..config import config
        if hasattr(config, 'audio'):
            threshold = threshold or config.audio.compression_threshold
            ratio = ratio or config.audio.compression_ratio
        else:
            threshold = threshold or 0.7
            ratio = ratio or 4.0

        compressed = audio_data.copy()

        # Find samples above threshold
        above_threshold = np.abs(compressed) > threshold

        # Apply compression to samples above threshold
        compressed[above_threshold] = np.sign(compressed[above_threshold]) * (
            threshold + (np.abs(compressed[above_threshold]) - threshold) / ratio
        )

        return compressed
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return self.format_converter.supported_formats
    
    def get_format_info(self, format: str) -> Dict[str, Any]:
        """Get information about an audio format"""
        return self.format_converter.get_format_info(format)
    
    def estimate_processing_time(self, audio_duration: float, format: str) -> float:
        """Estimate processing time for audio conversion"""
        # Base processing time (rough estimates)
        base_times = {
            'wav': 0.01,    # Very fast, no compression
            'mp3': 0.1,     # Moderate, lossy compression
            'ogg': 0.08,    # Moderate, lossy compression
            'flac': 0.15    # Slower, lossless compression
        }
        
        base_time = base_times.get(format.lower(), 0.1)
        return audio_duration * base_time