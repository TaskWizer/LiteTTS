#!/usr/bin/env python3
"""
Enhanced Voice Cloning System for LiteTTS
Extends voice cloning to support 120s audio clips, intelligent segmentation,
multiple reference audio support, and enhanced workflow management.
"""

import numpy as np
import logging
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass, field
import hashlib
import json
from datetime import datetime
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class EnhancedVoiceCloneConfig:
    """Enhanced configuration for voice cloning"""
    min_audio_duration: float = 3.0
    max_audio_duration: float = 120.0  # Extended from 30s to 120s
    max_segment_duration: float = 30.0  # Maximum duration per segment
    segment_overlap: float = 2.0  # Overlap between segments in seconds
    target_sample_rate: int = 24000
    embedding_dim: int = 256
    num_style_vectors: int = 510
    max_reference_clips: int = 5  # Support multiple reference clips
    max_total_reference_duration: float = 600.0  # 10 minutes total
    quality_threshold: float = 0.5
    enable_noise_reduction: bool = True
    enable_normalization: bool = True
    enable_silence_trimming: bool = True

@dataclass
class AudioSegment:
    """Audio segment with metadata"""
    audio_data: np.ndarray
    start_time: float
    end_time: float
    duration: float
    quality_score: float
    segment_id: str
    overlap_start: bool = False
    overlap_end: bool = False

@dataclass
class MultiClipVoiceProfile:
    """Voice profile from multiple audio clips"""
    voice_name: str
    clips: List[Dict[str, Any]]
    combined_embedding: np.ndarray
    quality_metrics: Dict[str, float]
    processing_metadata: Dict[str, Any]
    created_at: str
    total_duration: float
    clip_count: int

@dataclass
class VoiceQualityMetrics:
    """Comprehensive voice quality metrics"""
    snr_db: float  # Signal-to-noise ratio
    silence_ratio: float  # Ratio of silence in audio
    clipping_ratio: float  # Ratio of clipped samples
    frequency_range_hz: Tuple[float, float]  # Frequency range
    dynamic_range_db: float  # Dynamic range
    spectral_centroid: float  # Spectral centroid
    voice_activity_ratio: float  # Ratio of voice activity
    overall_quality_score: float  # Combined quality score

class AudioPreprocessor:
    """Advanced audio preprocessing for voice cloning"""
    
    def __init__(self, config: EnhancedVoiceCloneConfig):
        self.config = config
        
    def preprocess_audio(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, VoiceQualityMetrics]:
        """Comprehensive audio preprocessing"""
        processed_audio = audio_data.copy()
        
        # Convert to mono if stereo
        if processed_audio.ndim == 2:
            processed_audio = np.mean(processed_audio, axis=1)
            
        # Resample if needed
        if sample_rate != self.config.target_sample_rate:
            processed_audio = self._resample_audio(processed_audio, sample_rate, self.config.target_sample_rate)
            sample_rate = self.config.target_sample_rate
            
        # Noise reduction
        if self.config.enable_noise_reduction:
            processed_audio = self._reduce_noise(processed_audio)
            
        # Silence trimming
        if self.config.enable_silence_trimming:
            processed_audio = self._trim_silence(processed_audio)
            
        # Normalization
        if self.config.enable_normalization:
            processed_audio = self._normalize_audio(processed_audio)
            
        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(processed_audio, sample_rate)
        
        return processed_audio, quality_metrics
        
    def _resample_audio(self, audio_data: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        if original_rate == target_rate:
            return audio_data
            
        # Simple linear interpolation resampling
        ratio = target_rate / original_rate
        new_length = int(len(audio_data) * ratio)
        indices = np.linspace(0, len(audio_data) - 1, new_length)
        return np.interp(indices, np.arange(len(audio_data)), audio_data)
        
    def _reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """Basic noise reduction using spectral subtraction"""
        # Simple noise reduction - estimate noise from first 0.5 seconds
        noise_duration = min(0.5 * self.config.target_sample_rate, len(audio_data) // 4)
        noise_sample = audio_data[:int(noise_duration)]
        noise_level = np.std(noise_sample)
        
        # Apply gentle noise gate
        threshold = noise_level * 2
        mask = np.abs(audio_data) > threshold
        return audio_data * mask
        
    def _trim_silence(self, audio_data: np.ndarray) -> np.ndarray:
        """Trim silence from beginning and end"""
        # Simple energy-based silence detection
        frame_length = int(0.025 * self.config.target_sample_rate)  # 25ms frames
        energy_threshold = 0.01
        
        # Calculate frame energies
        energies = []
        for i in range(0, len(audio_data) - frame_length, frame_length):
            frame = audio_data[i:i + frame_length]
            energy = np.sum(frame ** 2)
            energies.append(energy)
            
        energies = np.array(energies)
        
        # Find start and end of speech
        speech_frames = energies > energy_threshold
        if not np.any(speech_frames):
            return audio_data  # No speech detected, return original
            
        start_frame = np.argmax(speech_frames)
        end_frame = len(speech_frames) - np.argmax(speech_frames[::-1]) - 1
        
        start_sample = start_frame * frame_length
        end_sample = min((end_frame + 1) * frame_length, len(audio_data))
        
        return audio_data[start_sample:end_sample]
        
    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio amplitude"""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val * 0.95  # Normalize to 95% to avoid clipping
        return audio_data
        
    def _calculate_quality_metrics(self, audio_data: np.ndarray, sample_rate: int) -> VoiceQualityMetrics:
        """Calculate comprehensive quality metrics"""
        # Signal-to-noise ratio estimation
        signal_power = np.mean(audio_data ** 2)
        noise_power = np.var(audio_data[:int(0.1 * sample_rate)])  # Estimate from first 0.1s
        snr_db = 10 * np.log10(signal_power / (noise_power + 1e-10)) if noise_power > 0 else 60.0
        
        # Silence ratio
        silence_threshold = 0.01
        silence_ratio = np.sum(np.abs(audio_data) < silence_threshold) / len(audio_data)
        
        # Clipping ratio
        clipping_ratio = np.sum(np.abs(audio_data) > 0.95) / len(audio_data)
        
        # Frequency analysis
        fft = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
        magnitude = np.abs(fft[:len(fft)//2])
        
        # Find frequency range (where magnitude > 10% of max)
        threshold = 0.1 * np.max(magnitude)
        active_freqs = freqs[:len(freqs)//2][magnitude > threshold]
        freq_range = (np.min(active_freqs), np.max(active_freqs)) if len(active_freqs) > 0 else (0, sample_rate/2)
        
        # Dynamic range
        dynamic_range_db = 20 * np.log10(np.max(np.abs(audio_data)) / (np.min(np.abs(audio_data[audio_data != 0])) + 1e-10))
        
        # Spectral centroid
        spectral_centroid = np.sum(freqs[:len(freqs)//2] * magnitude) / np.sum(magnitude)
        
        # Voice activity detection (simple energy-based)
        frame_length = int(0.025 * sample_rate)
        voice_frames = 0
        total_frames = 0
        
        for i in range(0, len(audio_data) - frame_length, frame_length):
            frame = audio_data[i:i + frame_length]
            energy = np.sum(frame ** 2)
            total_frames += 1
            if energy > 0.001:  # Voice activity threshold
                voice_frames += 1
                
        voice_activity_ratio = voice_frames / total_frames if total_frames > 0 else 0
        
        # Overall quality score (weighted combination)
        quality_score = (
            min(snr_db / 30, 1.0) * 0.3 +  # SNR component (max 30dB)
            (1 - silence_ratio) * 0.2 +      # Less silence is better
            (1 - clipping_ratio) * 0.2 +     # Less clipping is better
            voice_activity_ratio * 0.3       # More voice activity is better
        )
        
        return VoiceQualityMetrics(
            snr_db=snr_db,
            silence_ratio=silence_ratio,
            clipping_ratio=clipping_ratio,
            frequency_range_hz=freq_range,
            dynamic_range_db=dynamic_range_db,
            spectral_centroid=spectral_centroid,
            voice_activity_ratio=voice_activity_ratio,
            overall_quality_score=quality_score
        )

class IntelligentAudioSegmenter:
    """Intelligent audio segmentation for long clips"""
    
    def __init__(self, config: EnhancedVoiceCloneConfig):
        self.config = config
        
    def segment_audio(self, audio_data: np.ndarray, sample_rate: int) -> List[AudioSegment]:
        """Segment long audio into optimal chunks"""
        duration = len(audio_data) / sample_rate
        
        if duration <= self.config.max_segment_duration:
            # No segmentation needed
            return [AudioSegment(
                audio_data=audio_data,
                start_time=0.0,
                end_time=duration,
                duration=duration,
                quality_score=1.0,
                segment_id="single"
            )]
            
        segments = []
        overlap_samples = int(self.config.segment_overlap * sample_rate)
        segment_samples = int(self.config.max_segment_duration * sample_rate)
        
        start_idx = 0
        segment_count = 0
        
        while start_idx < len(audio_data):
            end_idx = min(start_idx + segment_samples, len(audio_data))
            
            # Extract segment
            segment_audio = audio_data[start_idx:end_idx]
            segment_duration = len(segment_audio) / sample_rate
            
            # Find optimal cut points to avoid cutting mid-word
            if end_idx < len(audio_data):  # Not the last segment
                cut_point = self._find_optimal_cut_point(
                    audio_data[end_idx - overlap_samples:end_idx + overlap_samples],
                    sample_rate
                )
                end_idx = end_idx - overlap_samples + cut_point
                segment_audio = audio_data[start_idx:end_idx]
                segment_duration = len(segment_audio) / sample_rate
                
            segment = AudioSegment(
                audio_data=segment_audio,
                start_time=start_idx / sample_rate,
                end_time=end_idx / sample_rate,
                duration=segment_duration,
                quality_score=self._assess_segment_quality(segment_audio),
                segment_id=f"seg_{segment_count:03d}",
                overlap_start=start_idx > 0,
                overlap_end=end_idx < len(audio_data)
            )
            
            segments.append(segment)
            
            # Move to next segment with overlap
            start_idx = end_idx - overlap_samples
            segment_count += 1
            
        return segments
        
    def _find_optimal_cut_point(self, audio_window: np.ndarray, sample_rate: int) -> int:
        """Find optimal cut point in audio window to avoid cutting mid-word"""
        # Simple approach: find point with lowest energy (likely silence or pause)
        frame_length = int(0.01 * sample_rate)  # 10ms frames
        energies = []
        
        for i in range(0, len(audio_window) - frame_length, frame_length):
            frame = audio_window[i:i + frame_length]
            energy = np.sum(frame ** 2)
            energies.append(energy)
            
        if energies:
            min_energy_idx = np.argmin(energies)
            return min_energy_idx * frame_length
        else:
            return len(audio_window) // 2  # Fallback to middle
            
    def _assess_segment_quality(self, segment_audio: np.ndarray) -> float:
        """Assess quality of an audio segment"""
        # Simple quality assessment based on energy distribution
        energy = np.sum(segment_audio ** 2)
        length = len(segment_audio)
        
        if length == 0:
            return 0.0
            
        # Normalize by length
        normalized_energy = energy / length
        
        # Quality score based on energy (more energy generally means better quality)
        quality_score = min(normalized_energy * 1000, 1.0)  # Scale and cap at 1.0
        
        return quality_score

class EnhancedVoiceCloner:
    """Enhanced voice cloning system with extended capabilities"""
    
    def __init__(self, voices_dir: str = "LiteTTS/voices", config: Optional[EnhancedVoiceCloneConfig] = None):
        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(exist_ok=True)
        self.config = config or EnhancedVoiceCloneConfig()
        
        # Initialize components
        self.preprocessor = AudioPreprocessor(self.config)
        self.segmenter = IntelligentAudioSegmenter(self.config)
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info(f"EnhancedVoiceCloner initialized with max duration: {self.config.max_audio_duration}s")
        
    def clone_voice_from_multiple_clips(self, audio_files: List[str], voice_name: str, 
                                      description: str = "") -> MultiClipVoiceProfile:
        """Clone voice from multiple audio clips"""
        if len(audio_files) > self.config.max_reference_clips:
            raise ValueError(f"Too many clips: {len(audio_files)} (max: {self.config.max_reference_clips})")
            
        clips_data = []
        total_duration = 0.0
        
        # Process each clip
        for i, audio_file in enumerate(audio_files):
            try:
                clip_data = self._process_single_clip(audio_file, f"clip_{i:02d}")
                clips_data.append(clip_data)
                total_duration += clip_data['duration']
                
                if total_duration > self.config.max_total_reference_duration:
                    raise ValueError(f"Total duration exceeds limit: {total_duration:.1f}s > {self.config.max_total_reference_duration}s")
                    
            except Exception as e:
                logger.error(f"Failed to process clip {audio_file}: {e}")
                raise
                
        # Combine embeddings from all clips
        combined_embedding = self._combine_clip_embeddings(clips_data)
        
        # Calculate overall quality metrics
        quality_metrics = self._calculate_combined_quality_metrics(clips_data)
        
        # Generate voice profile
        profile = MultiClipVoiceProfile(
            voice_name=voice_name,
            clips=clips_data,
            combined_embedding=combined_embedding,
            quality_metrics=quality_metrics,
            processing_metadata={
                'config': self.config.__dict__,
                'processing_time': datetime.now().isoformat(),
                'total_segments': sum(len(clip['segments']) for clip in clips_data)
            },
            created_at=datetime.now().isoformat(),
            total_duration=total_duration,
            clip_count=len(clips_data)
        )
        
        # Save voice profile
        self._save_voice_profile(profile)
        
        return profile

    def _process_single_clip(self, audio_file: str, clip_id: str) -> Dict[str, Any]:
        """Process a single audio clip"""
        import soundfile as sf

        # Load audio
        audio_data, sample_rate = sf.read(audio_file)
        duration = len(audio_data) / sample_rate

        # Validate duration
        if duration > self.config.max_audio_duration:
            raise ValueError(f"Clip too long: {duration:.1f}s > {self.config.max_audio_duration}s")

        # Preprocess audio
        processed_audio, quality_metrics = self.preprocessor.preprocess_audio(audio_data, sample_rate)

        # Segment if needed
        segments = self.segmenter.segment_audio(processed_audio, self.config.target_sample_rate)

        # Extract embeddings from segments
        segment_embeddings = []
        for segment in segments:
            embedding = self._extract_segment_embedding(segment.audio_data)
            segment_embeddings.append(embedding)

        return {
            'clip_id': clip_id,
            'file_path': audio_file,
            'duration': duration,
            'quality_metrics': quality_metrics.__dict__,
            'segments': [self._segment_to_dict(seg) for seg in segments],
            'embeddings': segment_embeddings,
            'processed_audio_shape': processed_audio.shape
        }

    def _segment_to_dict(self, segment: AudioSegment) -> Dict[str, Any]:
        """Convert AudioSegment to dictionary"""
        return {
            'segment_id': segment.segment_id,
            'start_time': segment.start_time,
            'end_time': segment.end_time,
            'duration': segment.duration,
            'quality_score': segment.quality_score,
            'overlap_start': segment.overlap_start,
            'overlap_end': segment.overlap_end,
            'audio_shape': segment.audio_data.shape
        }

    def _extract_segment_embedding(self, audio_data: np.ndarray) -> np.ndarray:
        """Extract embedding from audio segment"""
        # Simplified embedding extraction (same as original cloning.py)
        # In production, use proper speaker encoder

        # Calculate spectral features
        fft = np.fft.fft(audio_data)
        magnitude = np.abs(fft)

        # Extract mel-scale features (simplified)
        n_mels = 128
        mel_features = self._extract_mel_features(audio_data, n_mels)

        # Create base embedding
        base_embedding = np.zeros(self.config.embedding_dim)

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

        return base_embedding.astype(np.float32)

    def _extract_mel_features(self, audio_data: np.ndarray, n_mels: int) -> np.ndarray:
        """Extract mel-scale features (simplified implementation)"""
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

    def _combine_clip_embeddings(self, clips_data: List[Dict[str, Any]]) -> np.ndarray:
        """Combine embeddings from multiple clips"""
        all_embeddings = []

        # Collect all segment embeddings
        for clip in clips_data:
            all_embeddings.extend(clip['embeddings'])

        if not all_embeddings:
            raise ValueError("No embeddings extracted from clips")

        # Calculate weighted average (weight by segment quality)
        weights = []
        for clip in clips_data:
            for segment in clip['segments']:
                weights.append(segment['quality_score'])

        weights = np.array(weights)
        weights = weights / np.sum(weights)  # Normalize weights

        # Weighted average of embeddings
        combined_embedding = np.zeros_like(all_embeddings[0])
        for embedding, weight in zip(all_embeddings, weights):
            combined_embedding += embedding * weight

        # Normalize final embedding
        combined_embedding = combined_embedding / (np.linalg.norm(combined_embedding) + 1e-8)

        # Create style vectors (same approach as original)
        style_vectors = np.zeros((self.config.num_style_vectors, self.config.embedding_dim))

        for i in range(self.config.num_style_vectors):
            # Add controlled variation
            variation = np.random.RandomState(i).normal(0, 0.05, self.config.embedding_dim)
            style_vectors[i] = combined_embedding + variation

            # Normalize each style vector
            style_vectors[i] = style_vectors[i] / (np.linalg.norm(style_vectors[i]) + 1e-8)

        return style_vectors.astype(np.float32)

    def _calculate_combined_quality_metrics(self, clips_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate combined quality metrics from all clips"""
        all_metrics = []

        for clip in clips_data:
            all_metrics.append(clip['quality_metrics'])

        # Average metrics across clips
        combined_metrics = {}
        for key in all_metrics[0].keys():
            values = [metrics[key] for metrics in all_metrics]
            combined_metrics[key] = np.mean(values)

        return combined_metrics

    def _save_voice_profile(self, profile: MultiClipVoiceProfile):
        """Save voice profile to disk"""
        # Save embedding as BIN file (compatible with existing system)
        voice_file_path = self.voices_dir / f"{profile.voice_name}.bin"
        profile.combined_embedding.astype(np.float32).tofile(voice_file_path)

        # Save metadata as JSON
        metadata_file_path = self.voices_dir / f"{profile.voice_name}_metadata.json"
        metadata = {
            'voice_name': profile.voice_name,
            'created_at': profile.created_at,
            'total_duration': profile.total_duration,
            'clip_count': profile.clip_count,
            'quality_metrics': profile.quality_metrics,
            'processing_metadata': profile.processing_metadata,
            'clips_info': [
                {
                    'clip_id': clip['clip_id'],
                    'file_path': clip['file_path'],
                    'duration': clip['duration'],
                    'segment_count': len(clip['segments'])
                }
                for clip in profile.clips
            ]
        }

        with open(metadata_file_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Voice profile saved: {voice_file_path}")
        logger.info(f"Metadata saved: {metadata_file_path}")

# Example usage and testing
async def test_enhanced_cloning():
    """Test the enhanced voice cloning system"""
    cloner = EnhancedVoiceCloner()

    # Test with multiple clips (placeholder paths)
    test_clips = [
        "test_audio_1.wav",
        "test_audio_2.wav",
        "test_audio_3.wav"
    ]

    try:
        profile = cloner.clone_voice_from_multiple_clips(
            test_clips,
            "test_enhanced_voice",
            "Test voice created with enhanced cloning system"
        )

        print(f"✅ Enhanced voice cloning successful!")
        print(f"   Voice: {profile.voice_name}")
        print(f"   Clips: {profile.clip_count}")
        print(f"   Duration: {profile.total_duration:.1f}s")
        print(f"   Quality: {profile.quality_metrics.get('overall_quality_score', 0):.2f}")

    except Exception as e:
        print(f"❌ Enhanced voice cloning failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_cloning())
