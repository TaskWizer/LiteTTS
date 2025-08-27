#!/usr/bin/env python3
"""
Time-Stretching Optimization Module
Implements beta time-stretching feature for improved TTS latency
"""

import logging
import time
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import os

try:
    import librosa
    import soundfile as sf
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logging.warning("librosa not available - time-stretching will use basic implementation")

try:
    import pyrubberband as pyrb
    PYRUBBERBAND_AVAILABLE = True
except ImportError:
    PYRUBBERBAND_AVAILABLE = False
    logging.warning("pyrubberband not available - using librosa for time-stretching")

from .audio_segment import AudioSegment

logger = logging.getLogger(__name__)

class StretchQuality(Enum):
    """Time-stretching quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class TimeStretchConfig:
    """Configuration for time-stretching optimization"""
    enabled: bool = False
    compress_playback_rate: int = 20  # 0-100% speed increase during generation
    correction_quality: StretchQuality = StretchQuality.MEDIUM
    max_rate: int = 100  # Maximum allowed rate (100% = 2x speed)
    min_rate: int = 10   # Minimum allowed rate (10% = 1.1x speed)
    auto_enable_threshold: int = 50  # Auto-enable for texts longer than this
    quality_fallback: bool = True  # Fallback to lower quality if high quality fails
    benchmark_mode: bool = False  # Enable comprehensive benchmarking

    def __post_init__(self):
        """Validate configuration"""
        if not (self.min_rate <= self.compress_playback_rate <= self.max_rate):
            raise ValueError(f"compress_playback_rate must be between {self.min_rate} and {self.max_rate}")
        if self.auto_enable_threshold < 0:
            raise ValueError("auto_enable_threshold must be non-negative")

@dataclass
class StretchMetrics:
    """Metrics for time-stretching performance"""
    original_duration: float
    stretched_duration: float
    generation_time: float
    stretch_time: float
    total_time: float
    rtf_original: float
    rtf_stretched: float
    quality_score: Optional[float] = None

class TimeStretcher:
    """Time-stretching processor for TTS optimization"""
    
    def __init__(self, config: TimeStretchConfig):
        self.config = config
        self.metrics_history: List[StretchMetrics] = []
        
        # Check available libraries
        self.use_pyrubberband = PYRUBBERBAND_AVAILABLE and config.correction_quality == StretchQuality.HIGH
        self.use_librosa = LIBROSA_AVAILABLE
        
        if not self.use_librosa and not self.use_pyrubberband:
            logger.warning("No time-stretching libraries available - feature disabled")
            self.config.enabled = False
        
        logger.info(f"TimeStretcher initialized: enabled={self.config.enabled}, "
                   f"rate={self.config.compress_playback_rate}%, "
                   f"quality={self.config.correction_quality.value}")
    
    def should_apply_stretching(self, text_length: int) -> bool:
        """Determine if time-stretching should be applied"""
        if not self.config.enabled:
            return False
        
        # Don't apply to very short texts (overhead not worth it)
        if text_length < 20:
            return False
        
        return True
    
    def get_generation_speed_multiplier(self) -> float:
        """Get the speed multiplier for generation"""
        if not self.config.enabled:
            return 1.0
        
        return 1.0 + (self.config.compress_playback_rate / 100.0)
    
    def stretch_audio_to_normal_speed(self, audio_segment: AudioSegment, 
                                    generation_speed: float) -> Tuple[AudioSegment, StretchMetrics]:
        """Stretch audio back to normal speed after fast generation"""
        start_time = time.perf_counter()
        
        # Calculate stretch ratio (inverse of generation speed)
        stretch_ratio = generation_speed
        
        logger.debug(f"Stretching audio: {audio_segment.duration:.2f}s at ratio {stretch_ratio:.2f}")
        
        try:
            # Perform time-stretching
            stretched_audio_data = self._apply_time_stretch(
                audio_segment.audio_data,
                audio_segment.sample_rate,
                stretch_ratio
            )
            
            # Create new audio segment
            stretched_segment = AudioSegment(
                audio_data=stretched_audio_data,
                sample_rate=audio_segment.sample_rate,
                format=audio_segment.format
            )
            
            stretch_time = time.perf_counter() - start_time
            
            # Calculate metrics
            metrics = StretchMetrics(
                original_duration=audio_segment.duration,
                stretched_duration=stretched_segment.duration,
                generation_time=0.0,  # Will be set by caller
                stretch_time=stretch_time,
                total_time=0.0,  # Will be set by caller
                rtf_original=0.0,  # Will be set by caller
                rtf_stretched=0.0  # Will be set by caller
            )
            
            self.metrics_history.append(metrics)
            
            logger.debug(f"Time-stretching completed: {stretched_segment.duration:.2f}s "
                        f"(stretch time: {stretch_time:.3f}s)")
            
            return stretched_segment, metrics
            
        except Exception as e:
            logger.error(f"Time-stretching failed: {e}")
            # Return original audio if stretching fails
            metrics = StretchMetrics(
                original_duration=audio_segment.duration,
                stretched_duration=audio_segment.duration,
                generation_time=0.0,
                stretch_time=0.0,
                total_time=0.0,
                rtf_original=0.0,
                rtf_stretched=0.0
            )
            return audio_segment, metrics
    
    def _apply_time_stretch(self, audio_data: np.ndarray, sample_rate: int, 
                           stretch_ratio: float) -> np.ndarray:
        """Apply time-stretching using the best available method"""
        
        if self.use_pyrubberband and self.config.correction_quality == StretchQuality.HIGH:
            return self._stretch_with_pyrubberband(audio_data, sample_rate, stretch_ratio)
        elif self.use_librosa:
            return self._stretch_with_librosa(audio_data, sample_rate, stretch_ratio)
        else:
            # Fallback to basic interpolation (not recommended for production)
            return self._stretch_basic(audio_data, stretch_ratio)
    
    def _stretch_with_pyrubberband(self, audio_data: np.ndarray, sample_rate: int,
                                  stretch_ratio: float) -> np.ndarray:
        """High-quality time-stretching using pyrubberband"""
        try:
            # pyrubberband expects time_ratio (duration multiplier)
            time_ratio = stretch_ratio
            
            # Apply time-stretching
            stretched = pyrb.time_stretch(audio_data, sample_rate, time_ratio)
            
            return stretched.astype(np.float32)
            
        except Exception as e:
            logger.warning(f"pyrubberband stretching failed: {e}, falling back to librosa")
            return self._stretch_with_librosa(audio_data, sample_rate, stretch_ratio)
    
    def _stretch_with_librosa(self, audio_data: np.ndarray, sample_rate: int,
                             stretch_ratio: float) -> np.ndarray:
        """Medium-quality time-stretching using librosa"""
        try:
            # librosa.effects.time_stretch expects rate (speed multiplier, inverse of time ratio)
            rate = 1.0 / stretch_ratio
            
            # Apply time-stretching
            stretched = librosa.effects.time_stretch(audio_data, rate=rate)
            
            return stretched.astype(np.float32)
            
        except Exception as e:
            logger.warning(f"librosa stretching failed: {e}, falling back to basic method")
            return self._stretch_basic(audio_data, stretch_ratio)
    
    def _stretch_basic(self, audio_data: np.ndarray, stretch_ratio: float) -> np.ndarray:
        """Basic time-stretching using linear interpolation (low quality)"""
        logger.warning("Using basic time-stretching - quality may be poor")
        
        # Calculate new length
        new_length = int(len(audio_data) * stretch_ratio)
        
        # Create new time indices
        old_indices = np.linspace(0, len(audio_data) - 1, new_length)
        
        # Interpolate
        stretched = np.interp(old_indices, np.arange(len(audio_data)), audio_data)
        
        return stretched.astype(np.float32)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of time-stretching metrics"""
        if not self.metrics_history:
            return {"message": "No time-stretching metrics available"}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 operations
        
        avg_stretch_time = np.mean([m.stretch_time for m in recent_metrics])
        avg_rtf_improvement = np.mean([
            m.rtf_stretched - m.rtf_original for m in recent_metrics 
            if m.rtf_original > 0 and m.rtf_stretched > 0
        ])
        
        return {
            "total_operations": len(self.metrics_history),
            "recent_operations": len(recent_metrics),
            "average_stretch_time": avg_stretch_time,
            "average_rtf_improvement": avg_rtf_improvement,
            "config": {
                "enabled": self.config.enabled,
                "rate": self.config.compress_playback_rate,
                "quality": self.config.correction_quality.value
            }
        }
    
    def benchmark_rates(self, test_audio: AudioSegment, rates: List[int],
                       save_samples: bool = True) -> Dict[int, StretchMetrics]:
        """Benchmark different stretch rates for testing"""
        results = {}

        # Create samples directory if saving
        if save_samples:
            samples_dir = "samples/time-stretched"
            os.makedirs(samples_dir, exist_ok=True)

            # Save original audio for reference
            original_path = os.path.join(samples_dir, "original.wav")
            sf.write(original_path, test_audio.audio_data, test_audio.sample_rate)
            logger.info(f"Saved original audio to {original_path}")

        for rate in rates:
            logger.info(f"Benchmarking rate: {rate}%")

            # Temporarily set rate
            original_rate = self.config.compress_playback_rate
            self.config.compress_playback_rate = rate

            try:
                # Simulate faster generation (for testing, we'll speed up the audio)
                generation_speed = self.get_generation_speed_multiplier()

                # Create "fast" audio by speeding up original
                fast_audio = self._simulate_fast_generation(test_audio, generation_speed)

                # Save fast audio sample
                if save_samples:
                    fast_path = os.path.join(samples_dir, f"raw_{rate}p.wav")
                    sf.write(fast_path, fast_audio.audio_data, fast_audio.sample_rate)

                # Apply time-stretching to restore normal speed
                stretched_audio, metrics = self.stretch_audio_to_normal_speed(
                    fast_audio, generation_speed
                )

                # Save corrected audio sample
                if save_samples:
                    corrected_path = os.path.join(samples_dir, f"corrected_{rate}p.wav")
                    sf.write(corrected_path, stretched_audio.audio_data, stretched_audio.sample_rate)

                results[rate] = metrics
                logger.info(f"Rate {rate}%: RTF {metrics.rtf_original:.3f} → {metrics.rtf_stretched:.3f}")

            except Exception as e:
                logger.error(f"Benchmark failed for rate {rate}%: {e}")

            finally:
                # Restore original rate
                self.config.compress_playback_rate = original_rate

        return results

    def _simulate_fast_generation(self, audio: AudioSegment, speed_multiplier: float) -> AudioSegment:
        """Simulate faster TTS generation by speeding up audio"""
        # Use librosa to speed up audio (inverse of time-stretching)
        if LIBROSA_AVAILABLE:
            fast_audio_data = librosa.effects.time_stretch(audio.audio_data, rate=speed_multiplier)
        else:
            # Basic speed-up using resampling
            new_length = int(len(audio.audio_data) / speed_multiplier)
            indices = np.linspace(0, len(audio.audio_data) - 1, new_length)
            fast_audio_data = np.interp(indices, np.arange(len(audio.audio_data)), audio.audio_data)

        return AudioSegment(
            audio_data=fast_audio_data.astype(np.float32),
            sample_rate=audio.sample_rate,
            format=audio.format
        )

    def generate_benchmark_report(self, results: Dict[int, StretchMetrics]) -> str:
        """Generate a comprehensive benchmark report"""
        report = []
        report.append("# Time-Stretching Benchmark Report")
        report.append("=" * 50)
        report.append("")

        # Summary table
        report.append("## Performance Summary")
        report.append("")
        report.append("| Rate % | RTF Original | RTF Stretched | Generation Time (ms) | Stretch Time (ms) | Total Time (ms) |")
        report.append("|--------|--------------|---------------|---------------------|-------------------|-----------------|")

        for rate in sorted(results.keys()):
            metrics = results[rate]
            report.append(f"| {rate:6d} | {metrics.rtf_original:12.3f} | {metrics.rtf_stretched:13.3f} | "
                         f"{metrics.generation_time*1000:19.1f} | {metrics.stretch_time*1000:17.1f} | "
                         f"{metrics.total_time*1000:15.1f} |")

        report.append("")

        # Analysis
        report.append("## Analysis")
        report.append("")

        best_rate = min(results.keys(), key=lambda r: results[r].rtf_stretched)
        best_metrics = results[best_rate]

        report.append(f"**Best Rate:** {best_rate}% (RTF: {best_metrics.rtf_stretched:.3f})")
        report.append("")

        # Quality recommendations
        report.append("## Recommendations")
        report.append("")

        if best_metrics.rtf_stretched < 0.8:
            report.append("✅ **Recommended:** Time-stretching shows significant latency improvement")
            report.append(f"   - Use rate: {best_rate}%")
            report.append(f"   - Expected RTF improvement: {best_metrics.rtf_original:.3f} → {best_metrics.rtf_stretched:.3f}")
        elif best_metrics.rtf_stretched < 1.0:
            report.append("⚠️  **Marginal:** Time-stretching shows modest improvement")
            report.append("   - Consider enabling for longer texts only")
        else:
            report.append("❌ **Not Recommended:** Time-stretching adds overhead without benefit")
            report.append("   - Keep feature disabled")

        report.append("")
        report.append("## Audio Samples")
        report.append("")
        report.append("Generated audio samples are available in `samples/time-stretched/`:")
        report.append("- `original.wav` - Original audio")

        for rate in sorted(results.keys()):
            report.append(f"- `raw_{rate}p.wav` - Audio generated at {1 + rate/100:.1f}x speed")
            report.append(f"- `corrected_{rate}p.wav` - Time-stretched back to normal speed")

        return "\n".join(report)
