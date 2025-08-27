#!/usr/bin/env python3
"""
SSML Processor for Kokoro TTS

Processes SSML markup and integrates background noise with speech synthesis.
"""

import logging
import numpy as np
from typing import Optional, Dict, Any

from ..audio.audio_segment import AudioSegment
from ..audio.processor import AudioProcessor
from .parser import SSMLParser, ParsedSSML, BackgroundConfig
from .background_generator import BackgroundGenerator

logger = logging.getLogger(__name__)

class SSMLProcessor:
    """
    SSML Processor that handles background noise integration
    
    Processes SSML markup, generates background audio, and mixes it with speech.
    """
    
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate
        self.parser = SSMLParser()
        self.background_generator = BackgroundGenerator(sample_rate)
        self.audio_processor = AudioProcessor()
    
    def process_ssml(self, ssml_text: str) -> tuple[str, Optional[BackgroundConfig], Dict[str, Any]]:
        """
        Process SSML text and extract components
        
        Args:
            ssml_text: SSML markup text
            
        Returns:
            Tuple of (plain_text, background_config, processing_metadata)
        """
        parsed = self.parser.parse(ssml_text)
        
        metadata = {
            'has_background': parsed.background_config is not None,
            'prosody_changes': parsed.prosody_changes,
            'emphasis_spans': parsed.emphasis_spans,
            'break_positions': parsed.break_positions,
            'parsing_errors': parsed.errors
        }
        
        return parsed.plain_text, parsed.background_config, metadata
    
    def synthesize_with_background(self, speech_audio: AudioSegment, 
                                 background_config: BackgroundConfig) -> AudioSegment:
        """
        Mix speech audio with background noise
        
        Args:
            speech_audio: Primary speech audio
            background_config: Background noise configuration
            
        Returns:
            Mixed audio with background
        """
        try:
            # Generate background audio matching speech duration
            background_audio = self.background_generator.generate_background(
                background_config, speech_audio.duration
            )
            
            # Mix speech and background
            mixed_audio = self._mix_audio_with_background(
                speech_audio, background_audio, background_config
            )
            
            return mixed_audio
            
        except Exception as e:
            logger.error(f"Failed to synthesize with background: {e}")
            # Return original speech audio as fallback
            return speech_audio
    
    def _mix_audio_with_background(self, speech: AudioSegment, background: AudioSegment,
                                 config: BackgroundConfig) -> AudioSegment:
        """
        Mix speech and background audio with proper level balancing
        
        Args:
            speech: Primary speech audio
            background: Background ambient audio
            config: Background configuration
            
        Returns:
            Mixed audio segment
        """
        # Ensure both audio segments have the same sample rate
        if speech.sample_rate != background.sample_rate:
            logger.warning(f"Sample rate mismatch: speech={speech.sample_rate}, background={background.sample_rate}")
            # For now, assume they match; in production, you'd resample
        
        # Get audio data
        speech_data = speech.audio_data
        background_data = background.audio_data
        
        # Ensure same length
        min_length = min(len(speech_data), len(background_data))
        speech_data = speech_data[:min_length]
        background_data = background_data[:min_length]
        
        # Apply dynamic range compression to background to avoid masking speech
        background_data = self._apply_background_compression(background_data)
        
        # Apply speech-aware ducking (reduce background when speech is loud)
        background_data = self._apply_speech_ducking(speech_data, background_data)
        
        # Mix with proper levels
        # Speech typically at full level, background at configured volume
        mixed_data = speech_data + (background_data * config.volume)
        
        # Apply gentle limiting to prevent clipping
        mixed_data = self._apply_soft_limiting(mixed_data)
        
        return AudioSegment(
            audio_data=mixed_data,
            sample_rate=speech.sample_rate,
            format=speech.format
        )
    
    def _apply_background_compression(self, background_data: np.ndarray) -> np.ndarray:
        """Apply compression to background audio to maintain speech clarity"""
        
        # Simple RMS-based compression
        window_size = int(0.1 * self.sample_rate)  # 100ms windows
        compressed = np.copy(background_data)
        
        for i in range(0, len(background_data), window_size):
            end = min(i + window_size, len(background_data))
            window = background_data[i:end]
            
            # Calculate RMS
            rms = np.sqrt(np.mean(window ** 2))
            
            # Apply compression if RMS is above threshold
            threshold = 0.1
            ratio = 3.0
            
            if rms > threshold:
                # Compress the window
                gain_reduction = 1.0 - (rms - threshold) / ratio
                gain_reduction = max(0.3, gain_reduction)  # Minimum 30% of original
                compressed[i:end] = window * gain_reduction
        
        return compressed
    
    def _apply_speech_ducking(self, speech_data: np.ndarray, background_data: np.ndarray) -> np.ndarray:
        """Apply speech-aware ducking to background audio"""
        
        # Calculate speech energy in overlapping windows
        window_size = int(0.05 * self.sample_rate)  # 50ms windows
        hop_size = window_size // 2
        ducked = np.copy(background_data)
        
        for i in range(0, len(speech_data) - window_size, hop_size):
            speech_window = speech_data[i:i + window_size]
            
            # Calculate speech energy
            speech_energy = np.sqrt(np.mean(speech_window ** 2))
            
            # Calculate ducking amount based on speech energy
            if speech_energy > 0.05:  # Speech present
                # Reduce background proportionally to speech energy
                duck_amount = min(0.7, speech_energy * 2)  # Max 70% reduction
                gain = 1.0 - duck_amount
            else:
                gain = 1.0  # No ducking when no speech
            
            # Apply ducking with smooth transitions
            end = min(i + window_size, len(ducked))
            ducked[i:end] *= gain
        
        return ducked
    
    def _apply_soft_limiting(self, audio_data: np.ndarray, threshold: float = 0.95) -> np.ndarray:
        """Apply soft limiting to prevent clipping"""
        
        # Find peaks above threshold
        peaks = np.abs(audio_data) > threshold
        
        if np.any(peaks):
            # Apply soft limiting using tanh
            limited = np.copy(audio_data)
            limited[peaks] = np.tanh(audio_data[peaks] / threshold) * threshold
            return limited
        
        return audio_data
    
    def validate_ssml(self, ssml_text: str) -> Dict[str, Any]:
        """
        Validate SSML markup
        
        Args:
            ssml_text: SSML markup to validate
            
        Returns:
            Validation result with errors and warnings
        """
        errors = self.parser.validate_ssml(ssml_text)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
    
    def get_supported_background_types(self) -> list[str]:
        """Get list of supported background types"""
        return [
            'coffee_shop', 'cafe',
            'office', 'workplace', 
            'nature', 'forest',
            'rain', 'rainfall',
            'wind', 'windy',
            'white_noise', 'pink_noise', 'brown_noise',
            'custom'
        ]
    
    def create_background_example(self, bg_type: str, duration: float = 5.0) -> Optional[AudioSegment]:
        """
        Create an example of a background type for testing/preview
        
        Args:
            bg_type: Background type name
            duration: Duration in seconds
            
        Returns:
            AudioSegment with example background audio
        """
        try:
            from .parser import BackgroundConfig, BackgroundType
            
            # Map string to enum
            type_mapping = {
                'coffee_shop': BackgroundType.COFFEE_SHOP,
                'cafe': BackgroundType.COFFEE_SHOP,
                'office': BackgroundType.OFFICE,
                'workplace': BackgroundType.OFFICE,
                'nature': BackgroundType.NATURE,
                'forest': BackgroundType.NATURE,
                'rain': BackgroundType.RAIN,
                'rainfall': BackgroundType.RAIN,
                'wind': BackgroundType.WIND,
                'windy': BackgroundType.WIND,
                'white_noise': BackgroundType.WHITE_NOISE,
                'pink_noise': BackgroundType.PINK_NOISE,
                'brown_noise': BackgroundType.BROWN_NOISE
            }
            
            if bg_type not in type_mapping:
                logger.error(f"Unknown background type: {bg_type}")
                return None
            
            config = BackgroundConfig(
                type=type_mapping[bg_type],
                volume=0.5,
                fade_in=0.5,
                fade_out=0.5
            )
            
            return self.background_generator.generate_background(config, duration)
            
        except Exception as e:
            logger.error(f"Failed to create background example: {e}")
            return None
