#!/usr/bin/env python3
"""
Background Noise Generator for SSML

Generates ambient background sounds for speech synthesis enhancement.
Supports various predefined ambient sounds and custom audio files.
"""

import numpy as np
import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from ..audio.audio_segment import AudioSegment
from .parser import BackgroundType, BackgroundConfig

logger = logging.getLogger(__name__)

@dataclass
class NoiseParameters:
    """Parameters for procedural noise generation"""
    frequency_range: tuple  # (min_freq, max_freq) in Hz
    amplitude_variation: float  # 0.0 to 1.0
    spectral_shape: str  # 'white', 'pink', 'brown'
    modulation_freq: Optional[float] = None  # For amplitude modulation
    filter_cutoff: Optional[float] = None  # Low-pass filter cutoff

class BackgroundGenerator:
    """
    Generates background ambient sounds for TTS enhancement
    
    Supports both procedural generation and custom audio file loading.
    """
    
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate
        
        # Predefined noise parameters for different environments
        self.noise_profiles = {
            BackgroundType.COFFEE_SHOP: NoiseParameters(
                frequency_range=(100, 4000),
                amplitude_variation=0.3,
                spectral_shape='pink',
                modulation_freq=0.1,
                filter_cutoff=3000
            ),
            BackgroundType.OFFICE: NoiseParameters(
                frequency_range=(200, 2000),
                amplitude_variation=0.2,
                spectral_shape='pink',
                modulation_freq=0.05,
                filter_cutoff=1500
            ),
            BackgroundType.NATURE: NoiseParameters(
                frequency_range=(50, 8000),
                amplitude_variation=0.4,
                spectral_shape='pink',
                modulation_freq=0.2,
                filter_cutoff=6000
            ),
            BackgroundType.RAIN: NoiseParameters(
                frequency_range=(1000, 12000),
                amplitude_variation=0.5,
                spectral_shape='white',
                modulation_freq=0.3,
                filter_cutoff=8000
            ),
            BackgroundType.WIND: NoiseParameters(
                frequency_range=(20, 2000),
                amplitude_variation=0.6,
                spectral_shape='brown',
                modulation_freq=0.15,
                filter_cutoff=1000
            ),
            BackgroundType.WHITE_NOISE: NoiseParameters(
                frequency_range=(20, 20000),
                amplitude_variation=0.1,
                spectral_shape='white'
            ),
            BackgroundType.PINK_NOISE: NoiseParameters(
                frequency_range=(20, 20000),
                amplitude_variation=0.1,
                spectral_shape='pink'
            ),
            BackgroundType.BROWN_NOISE: NoiseParameters(
                frequency_range=(20, 20000),
                amplitude_variation=0.1,
                spectral_shape='brown'
            )
        }
    
    def generate_background(self, config: BackgroundConfig, duration: float) -> AudioSegment:
        """
        Generate background audio based on configuration
        
        Args:
            config: Background configuration
            duration: Duration in seconds
            
        Returns:
            AudioSegment with background audio
        """
        try:
            if config.type == BackgroundType.CUSTOM and config.custom_file:
                return self._load_custom_background(config, duration)
            else:
                return self._generate_procedural_background(config, duration)
        
        except Exception as e:
            logger.error(f"Failed to generate background audio: {e}")
            # Return silence as fallback
            return self._generate_silence(duration)
    
    def _generate_procedural_background(self, config: BackgroundConfig, duration: float) -> AudioSegment:
        """Generate procedural background noise"""
        
        if config.type not in self.noise_profiles:
            logger.warning(f"Unknown background type: {config.type}, using nature")
            profile = self.noise_profiles[BackgroundType.NATURE]
        else:
            profile = self.noise_profiles[config.type]
        
        # Calculate number of samples
        num_samples = int(duration * self.sample_rate)
        
        # Generate base noise
        if profile.spectral_shape == 'white':
            noise = self._generate_white_noise(num_samples)
        elif profile.spectral_shape == 'pink':
            noise = self._generate_pink_noise(num_samples)
        elif profile.spectral_shape == 'brown':
            noise = self._generate_brown_noise(num_samples)
        else:
            noise = self._generate_white_noise(num_samples)
        
        # Apply frequency filtering
        if profile.filter_cutoff:
            noise = self._apply_lowpass_filter(noise, profile.filter_cutoff)
        
        # Apply amplitude modulation for natural variation
        if profile.modulation_freq and profile.amplitude_variation > 0:
            noise = self._apply_amplitude_modulation(
                noise, profile.modulation_freq, profile.amplitude_variation
            )
        
        # Add environment-specific characteristics
        noise = self._add_environment_characteristics(noise, config.type)
        
        # Apply volume scaling
        noise = noise * config.volume
        
        # Apply fade in/out
        noise = self._apply_fades(noise, config.fade_in, config.fade_out)
        
        return AudioSegment(
            audio_data=noise,
            sample_rate=self.sample_rate,
            format="wav"
        )
    
    def _generate_white_noise(self, num_samples: int) -> np.ndarray:
        """Generate white noise"""
        return np.random.normal(0, 0.1, num_samples).astype(np.float32)
    
    def _generate_pink_noise(self, num_samples: int) -> np.ndarray:
        """Generate pink noise (1/f noise)"""
        # Generate white noise
        white = np.random.normal(0, 1, num_samples)
        
        # Apply 1/f filter in frequency domain
        fft = np.fft.fft(white)
        freqs = np.fft.fftfreq(num_samples, 1/self.sample_rate)
        
        # Avoid division by zero
        freqs[0] = 1
        
        # Apply 1/sqrt(f) scaling
        pink_filter = 1 / np.sqrt(np.abs(freqs))
        pink_fft = fft * pink_filter
        
        # Convert back to time domain
        pink = np.real(np.fft.ifft(pink_fft))
        
        # Normalize
        pink = pink / np.max(np.abs(pink)) * 0.1
        
        return pink.astype(np.float32)
    
    def _generate_brown_noise(self, num_samples: int) -> np.ndarray:
        """Generate brown noise (1/f² noise)"""
        # Generate white noise
        white = np.random.normal(0, 1, num_samples)
        
        # Apply 1/f² filter in frequency domain
        fft = np.fft.fft(white)
        freqs = np.fft.fftfreq(num_samples, 1/self.sample_rate)
        
        # Avoid division by zero
        freqs[0] = 1
        
        # Apply 1/f scaling
        brown_filter = 1 / np.abs(freqs)
        brown_fft = fft * brown_filter
        
        # Convert back to time domain
        brown = np.real(np.fft.ifft(brown_fft))
        
        # Normalize
        brown = brown / np.max(np.abs(brown)) * 0.1
        
        return brown.astype(np.float32)
    
    def _apply_lowpass_filter(self, audio: np.ndarray, cutoff_freq: float) -> np.ndarray:
        """Apply simple lowpass filter"""
        # Simple first-order lowpass filter
        alpha = cutoff_freq / (cutoff_freq + self.sample_rate / (2 * np.pi))
        
        filtered = np.zeros_like(audio)
        filtered[0] = audio[0]
        
        for i in range(1, len(audio)):
            filtered[i] = alpha * audio[i] + (1 - alpha) * filtered[i-1]
        
        return filtered
    
    def _apply_amplitude_modulation(self, audio: np.ndarray, mod_freq: float, depth: float) -> np.ndarray:
        """Apply amplitude modulation for natural variation"""
        t = np.arange(len(audio)) / self.sample_rate
        modulation = 1 + depth * np.sin(2 * np.pi * mod_freq * t)
        return audio * modulation
    
    def _add_environment_characteristics(self, noise: np.ndarray, bg_type: BackgroundType) -> np.ndarray:
        """Add environment-specific characteristics"""
        
        if bg_type == BackgroundType.COFFEE_SHOP:
            # Add occasional "clinks" and murmur-like patterns
            noise = self._add_occasional_impulses(noise, rate=0.1, amplitude=0.05)
            
        elif bg_type == BackgroundType.OFFICE:
            # Add subtle periodic patterns (like air conditioning)
            t = np.arange(len(noise)) / self.sample_rate
            ac_hum = 0.02 * np.sin(2 * np.pi * 60 * t)  # 60Hz hum
            noise += ac_hum
            
        elif bg_type == BackgroundType.RAIN:
            # Add droplet-like impulses
            noise = self._add_occasional_impulses(noise, rate=2.0, amplitude=0.1)
            
        elif bg_type == BackgroundType.WIND:
            # Add gusty variations
            noise = self._add_wind_gusts(noise)
        
        return noise
    
    def _add_occasional_impulses(self, noise: np.ndarray, rate: float, amplitude: float) -> np.ndarray:
        """Add occasional impulse sounds"""
        num_impulses = int(len(noise) / self.sample_rate * rate)
        
        for _ in range(num_impulses):
            pos = np.random.randint(0, len(noise) - 100)
            impulse = amplitude * np.exp(-np.arange(100) / 20) * np.random.normal(0, 1, 100)
            noise[pos:pos+100] += impulse
        
        return noise
    
    def _add_wind_gusts(self, noise: np.ndarray) -> np.ndarray:
        """Add wind gust patterns"""
        # Create random gust envelope
        gust_length = int(self.sample_rate * 2)  # 2-second gusts
        num_gusts = len(noise) // gust_length
        
        for i in range(num_gusts):
            start = i * gust_length
            end = min(start + gust_length, len(noise))
            
            # Random gust strength
            gust_strength = 0.5 + 0.5 * np.random.random()
            
            # Apply gust envelope
            gust_env = np.linspace(1, gust_strength, end - start)
            noise[start:end] *= gust_env
        
        return noise
    
    def _apply_fades(self, audio: np.ndarray, fade_in: float, fade_out: float) -> np.ndarray:
        """Apply fade in/out to audio"""
        fade_in_samples = int(fade_in * self.sample_rate)
        fade_out_samples = int(fade_out * self.sample_rate)
        
        # Apply fade in
        if fade_in_samples > 0 and fade_in_samples < len(audio):
            fade_in_curve = np.linspace(0, 1, fade_in_samples)
            audio[:fade_in_samples] *= fade_in_curve
        
        # Apply fade out
        if fade_out_samples > 0 and fade_out_samples < len(audio):
            fade_out_curve = np.linspace(1, 0, fade_out_samples)
            audio[-fade_out_samples:] *= fade_out_curve
        
        return audio
    
    def _load_custom_background(self, config: BackgroundConfig, duration: float) -> AudioSegment:
        """Load custom background audio file"""
        try:
            # This would load from the custom file
            # For now, return procedural nature sound as fallback
            logger.warning(f"Custom background files not yet implemented, using nature sound")
            return self._generate_procedural_background(
                BackgroundConfig(type=BackgroundType.NATURE, volume=config.volume), 
                duration
            )
        except Exception as e:
            logger.error(f"Failed to load custom background: {e}")
            return self._generate_silence(duration)
    
    def _generate_silence(self, duration: float) -> AudioSegment:
        """Generate silence as fallback"""
        num_samples = int(duration * self.sample_rate)
        silence = np.zeros(num_samples, dtype=np.float32)
        
        return AudioSegment(
            audio_data=silence,
            sample_rate=self.sample_rate,
            format="wav"
        )
