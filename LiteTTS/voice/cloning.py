#!/usr/bin/env python3
"""
Voice cloning system for LiteTTS
Extracts speaker embeddings from audio samples and generates BIN voice files
"""

import numpy as np
import logging
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import hashlib
import json
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class VoiceCloneResult:
    """Result of voice cloning operation"""
    success: bool
    voice_name: str
    voice_file_path: Optional[str] = None
    embedding_data: Optional[np.ndarray] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    similarity_score: Optional[float] = None

@dataclass
class AudioAnalysisResult:
    """Result of audio analysis for voice cloning"""
    success: bool
    duration: float
    sample_rate: int
    channels: int
    quality_score: float
    voice_characteristics: Dict[str, Any]
    error_message: Optional[str] = None

class VoiceCloner:
    """Voice cloning system that extracts speaker embeddings from audio samples"""
    
    def __init__(self, voices_dir: str = "LiteTTS/voices"):
        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(exist_ok=True)
        
        # Voice cloning configuration
        self.min_audio_duration = 3.0  # Minimum 3 seconds
        self.max_audio_duration = 120.0  # Maximum 120 seconds (extended from 30s)
        self.target_sample_rate = 24000
        self.embedding_dim = 256
        self.num_style_vectors = 510

        # Enhanced mode support (backward compatibility)
        self.enhanced_mode_enabled = os.environ.get('VOICE_CLONING_ENHANCED_MODE', 'true').lower() == 'true'
        if not self.enhanced_mode_enabled:
            self.max_audio_duration = 30.0  # Fallback to original limit
            logger.info("Enhanced voice cloning mode disabled, using 30s limit")
        
        logger.info(f"VoiceCloner initialized with voices directory: {self.voices_dir}")
    
    def analyze_audio(self, audio_file_path: str) -> AudioAnalysisResult:
        """
        Analyze uploaded audio file for voice cloning suitability
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            AudioAnalysisResult with analysis information
        """
        try:
            import soundfile as sf
            
            # Load audio file
            audio_data, sample_rate = sf.read(audio_file_path)
            
            # Basic audio properties
            duration = len(audio_data) / sample_rate
            channels = 1 if audio_data.ndim == 1 else audio_data.shape[1]
            
            # Convert to mono if stereo
            if audio_data.ndim == 2:
                audio_data = np.mean(audio_data, axis=1)
            
            # Quality assessment
            quality_score = self._assess_audio_quality(audio_data, sample_rate)
            
            # Voice characteristics analysis
            voice_characteristics = self._analyze_voice_characteristics(audio_data, sample_rate)
            
            return AudioAnalysisResult(
                success=True,
                duration=duration,
                sample_rate=sample_rate,
                channels=channels,
                quality_score=quality_score,
                voice_characteristics=voice_characteristics
            )
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return AudioAnalysisResult(
                success=False,
                duration=0.0,
                sample_rate=0,
                channels=0,
                quality_score=0.0,
                voice_characteristics={},
                error_message=str(e)
            )
    
    def clone_voice(self, audio_file_path: str, voice_name: str, 
                   description: str = "") -> VoiceCloneResult:
        """
        Clone a voice from an audio sample
        
        Args:
            audio_file_path: Path to the audio file
            voice_name: Name for the cloned voice
            description: Optional description
            
        Returns:
            VoiceCloneResult with cloning information
        """
        try:
            # First analyze the audio
            analysis = self.analyze_audio(audio_file_path)
            if not analysis.success:
                return VoiceCloneResult(
                    success=False,
                    voice_name=voice_name,
                    error_message=f"Audio analysis failed: {analysis.error_message}"
                )
            
            # Validate audio quality
            if analysis.duration < self.min_audio_duration:
                return VoiceCloneResult(
                    success=False,
                    voice_name=voice_name,
                    error_message=f"Audio too short: {analysis.duration:.1f}s (minimum: {self.min_audio_duration}s)"
                )
            
            if analysis.duration > self.max_audio_duration:
                return VoiceCloneResult(
                    success=False,
                    voice_name=voice_name,
                    error_message=f"Audio too long: {analysis.duration:.1f}s (maximum: {self.max_audio_duration}s)"
                )
            
            if analysis.quality_score < 0.5:
                return VoiceCloneResult(
                    success=False,
                    voice_name=voice_name,
                    error_message=f"Audio quality too low: {analysis.quality_score:.2f} (minimum: 0.5)"
                )
            
            # Extract voice embedding
            embedding_data = self._extract_voice_embedding(audio_file_path)
            if embedding_data is None:
                return VoiceCloneResult(
                    success=False,
                    voice_name=voice_name,
                    error_message="Failed to extract voice embedding"
                )
            
            # Generate BIN file
            voice_file_path = self._generate_bin_file(voice_name, embedding_data)
            if not voice_file_path:
                return VoiceCloneResult(
                    success=False,
                    voice_name=voice_name,
                    error_message="Failed to generate BIN voice file"
                )
            
            # Create metadata
            metadata = {
                'voice_name': voice_name,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'source_audio': {
                    'duration': analysis.duration,
                    'sample_rate': analysis.sample_rate,
                    'quality_score': analysis.quality_score,
                    'characteristics': analysis.voice_characteristics
                },
                'embedding_shape': embedding_data.shape,
                'cloning_method': 'simple_speaker_embedding'
            }
            
            # Calculate similarity score (placeholder for now)
            similarity_score = min(analysis.quality_score + 0.2, 1.0)
            
            return VoiceCloneResult(
                success=True,
                voice_name=voice_name,
                voice_file_path=voice_file_path,
                embedding_data=embedding_data,
                metadata=metadata,
                similarity_score=similarity_score
            )
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return VoiceCloneResult(
                success=False,
                voice_name=voice_name,
                error_message=str(e)
            )
    
    def _assess_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """
        Assess audio quality for voice cloning
        
        Returns:
            Quality score between 0.0 and 1.0
        """
        try:
            # Signal-to-noise ratio estimation
            signal_power = np.mean(audio_data ** 2)
            if signal_power == 0:
                return 0.0
            
            # Dynamic range assessment
            dynamic_range = np.max(audio_data) - np.min(audio_data)
            
            # Clipping detection
            clipping_ratio = np.sum(np.abs(audio_data) > 0.95) / len(audio_data)
            
            # Silence detection
            silence_threshold = 0.01
            silence_ratio = np.sum(np.abs(audio_data) < silence_threshold) / len(audio_data)
            
            # Calculate quality score
            quality_score = 1.0
            
            # Penalize clipping
            quality_score -= clipping_ratio * 0.5
            
            # Penalize excessive silence
            if silence_ratio > 0.3:
                quality_score -= (silence_ratio - 0.3) * 0.5
            
            # Penalize low dynamic range
            if dynamic_range < 0.1:
                quality_score -= (0.1 - dynamic_range) * 2.0
            
            # Ensure score is between 0 and 1
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
            return 0.5  # Default moderate quality
    
    def _analyze_voice_characteristics(self, audio_data: np.ndarray, 
                                     sample_rate: int) -> Dict[str, Any]:
        """
        Analyze voice characteristics from audio
        
        Returns:
            Dictionary with voice characteristics
        """
        try:
            # Basic spectral analysis
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
            magnitude = np.abs(fft)
            
            # Find dominant frequencies
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = magnitude[:len(magnitude)//2]
            
            # Fundamental frequency estimation (very basic)
            peak_idx = np.argmax(positive_magnitude[1:]) + 1  # Skip DC component
            fundamental_freq = positive_freqs[peak_idx]
            
            # Voice characteristics
            characteristics = {
                'fundamental_frequency': float(fundamental_freq),
                'spectral_centroid': float(np.sum(positive_freqs * positive_magnitude) / np.sum(positive_magnitude)),
                'spectral_bandwidth': float(np.sqrt(np.sum(((positive_freqs - fundamental_freq) ** 2) * positive_magnitude) / np.sum(positive_magnitude))),
                'energy': float(np.mean(audio_data ** 2)),
                'zero_crossing_rate': float(np.sum(np.diff(np.sign(audio_data)) != 0) / len(audio_data))
            }
            
            return characteristics
            
        except Exception as e:
            logger.warning(f"Voice characteristics analysis failed: {e}")
            return {
                'fundamental_frequency': 150.0,  # Default values
                'spectral_centroid': 1000.0,
                'spectral_bandwidth': 500.0,
                'energy': 0.1,
                'zero_crossing_rate': 0.1
            }
    
    def _extract_voice_embedding(self, audio_file_path: str) -> Optional[np.ndarray]:
        """
        Extract voice embedding from audio file
        
        This is a simplified implementation. In a production system,
        you would use a pre-trained speaker encoder like resemblyzer.
        
        Returns:
            Voice embedding array with shape (510, 256) or None if failed
        """
        try:
            import soundfile as sf
            
            # Load and preprocess audio
            audio_data, sample_rate = sf.read(audio_file_path)
            
            # Convert to mono if stereo
            if audio_data.ndim == 2:
                audio_data = np.mean(audio_data, axis=1)
            
            # Resample to target sample rate if needed
            if sample_rate != self.target_sample_rate:
                # Simple resampling (in production, use proper resampling)
                ratio = self.target_sample_rate / sample_rate
                new_length = int(len(audio_data) * ratio)
                audio_data = np.interp(
                    np.linspace(0, len(audio_data), new_length),
                    np.arange(len(audio_data)),
                    audio_data
                )
            
            # Extract features (simplified approach)
            # In production, use a proper speaker encoder
            embedding = self._simple_speaker_embedding(audio_data)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Voice embedding extraction failed: {e}")
            return None
    
    def _simple_speaker_embedding(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Simple speaker embedding extraction (placeholder implementation)
        
        In production, replace this with a proper speaker encoder like:
        - resemblyzer
        - SpeechBrain speaker verification models
        - wav2vec2-based speaker encoders
        
        Returns:
            Embedding array with shape (510, 256)
        """
        # Create a deterministic but unique embedding based on audio characteristics
        # This is a simplified approach for demonstration
        
        # Calculate spectral features
        fft = np.fft.fft(audio_data)
        magnitude = np.abs(fft)
        
        # Extract mel-scale features (simplified)
        n_mels = 128
        mel_features = self._extract_mel_features(audio_data, n_mels)
        
        # Create base embedding from audio characteristics
        base_embedding = np.zeros(256)
        
        # Fill embedding with spectral and temporal features
        if len(mel_features) >= 128:
            base_embedding[:128] = mel_features[:128]
        else:
            base_embedding[:len(mel_features)] = mel_features
        
        # Add temporal features
        temporal_features = self._extract_temporal_features(audio_data)
        base_embedding[128:128+len(temporal_features)] = temporal_features[:128]
        
        # Normalize embedding
        base_embedding = base_embedding / (np.linalg.norm(base_embedding) + 1e-8)
        
        # Create 510 style vectors with variations
        # Each style vector represents different speaking styles/contexts
        style_vectors = np.zeros((self.num_style_vectors, self.embedding_dim))
        
        for i in range(self.num_style_vectors):
            # Add controlled variation to create different style vectors
            variation = np.random.RandomState(i).normal(0, 0.05, self.embedding_dim)
            style_vectors[i] = base_embedding + variation
            
            # Normalize each style vector
            style_vectors[i] = style_vectors[i] / (np.linalg.norm(style_vectors[i]) + 1e-8)
        
        return style_vectors.astype(np.float32)
    
    def _extract_mel_features(self, audio_data: np.ndarray, n_mels: int) -> np.ndarray:
        """Extract mel-scale features (simplified implementation)"""
        # Simple spectral features as placeholder for mel features
        fft = np.fft.fft(audio_data)
        magnitude = np.abs(fft[:len(fft)//2])
        
        # Downsample to n_mels features
        if len(magnitude) > n_mels:
            step = len(magnitude) // n_mels
            mel_features = magnitude[::step][:n_mels]
        else:
            mel_features = np.pad(magnitude, (0, n_mels - len(magnitude)))
        
        # Log scale and normalize
        mel_features = np.log(mel_features + 1e-8)
        mel_features = (mel_features - np.mean(mel_features)) / (np.std(mel_features) + 1e-8)
        
        return mel_features
    
    def _extract_temporal_features(self, audio_data: np.ndarray) -> np.ndarray:
        """Extract temporal features from audio"""
        features = []
        
        # Energy features
        frame_size = 1024
        hop_size = 512
        
        for i in range(0, len(audio_data) - frame_size, hop_size):
            frame = audio_data[i:i + frame_size]
            
            # Frame energy
            energy = np.sum(frame ** 2)
            features.append(energy)
            
            # Zero crossing rate
            zcr = np.sum(np.diff(np.sign(frame)) != 0) / len(frame)
            features.append(zcr)
            
            if len(features) >= 128:
                break
        
        # Pad if necessary
        while len(features) < 128:
            features.append(0.0)
        
        features = np.array(features[:128])
        
        # Normalize
        features = (features - np.mean(features)) / (np.std(features) + 1e-8)
        
        return features
    
    def _generate_bin_file(self, voice_name: str, embedding_data: np.ndarray) -> Optional[str]:
        """
        Generate BIN voice file compatible with LiteTTS
        
        Args:
            voice_name: Name of the voice
            embedding_data: Voice embedding with shape (510, 256)
            
        Returns:
            Path to generated BIN file or None if failed
        """
        try:
            # Ensure embedding has correct shape
            if embedding_data.shape != (self.num_style_vectors, self.embedding_dim):
                logger.error(f"Invalid embedding shape: {embedding_data.shape}, expected: ({self.num_style_vectors}, {self.embedding_dim})")
                return None
            
            # Generate file path
            voice_file_path = self.voices_dir / f"{voice_name}.bin"
            
            # Save as binary file (float32)
            embedding_data.astype(np.float32).tofile(voice_file_path)
            
            logger.info(f"Generated BIN voice file: {voice_file_path}")
            return str(voice_file_path)
            
        except Exception as e:
            logger.error(f"BIN file generation failed: {e}")
            return None
    
    def list_custom_voices(self) -> Dict[str, Dict[str, Any]]:
        """
        List all custom voices created through cloning
        
        Returns:
            Dictionary of custom voice information
        """
        custom_voices = {}
        
        try:
            # Look for custom voice files (those not in the standard set)
            standard_voices = {
                'af_heart', 'af_alloy', 'af_aoede', 'af_bella', 'af_jessica',
                'af_kore', 'af_nicole', 'af_nova', 'af_river', 'af_sarah', 'af_sky',
                'am_adam', 'am_echo', 'am_eric', 'am_fenrir', 'am_liam',
                'am_michael', 'am_onyx', 'am_puck', 'am_santa'
            }
            
            for bin_file in self.voices_dir.glob("*.bin"):
                voice_name = bin_file.stem
                
                # Skip standard voices
                if voice_name in standard_voices:
                    continue
                
                # Get file info
                stat = bin_file.stat()
                
                custom_voices[voice_name] = {
                    'name': voice_name,
                    'file_path': str(bin_file),
                    'file_size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'is_custom': True
                }
            
            return custom_voices
            
        except Exception as e:
            logger.error(f"Failed to list custom voices: {e}")
            return {}
    
    def delete_custom_voice(self, voice_name: str) -> bool:
        """
        Delete a custom voice
        
        Args:
            voice_name: Name of the voice to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            voice_file_path = self.voices_dir / f"{voice_name}.bin"
            
            if voice_file_path.exists():
                voice_file_path.unlink()
                logger.info(f"Deleted custom voice: {voice_name}")
                return True
            else:
                logger.warning(f"Voice file not found: {voice_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete custom voice {voice_name}: {e}")
            return False
