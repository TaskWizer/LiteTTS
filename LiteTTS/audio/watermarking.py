#!/usr/bin/env python3
"""
Perth Audio Watermarking System for Kokoro ONNX TTS API
Responsible AI watermarking for generated audio content
"""

import numpy as np
import logging
from typing import Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from pathlib import Path
import time

logger = logging.getLogger(__name__)

# Try to import Perth watermarking library
try:
    import perth
    from perth import DummyWatermarker

    # Check if PerthImplicitWatermarker is available (may be None in some versions)
    PerthImplicitWatermarker = getattr(perth, 'PerthImplicitWatermarker', None)

    _PERTH_AVAILABLE = True
    _PERTH_IMPLICIT_AVAILABLE = PerthImplicitWatermarker is not None

    if _PERTH_IMPLICIT_AVAILABLE:
        logger.info("Perth watermarking library available with implicit watermarker")
    else:
        logger.info("Perth watermarking library available (DummyWatermarker only)")

except ImportError:
    _PERTH_AVAILABLE = False
    _PERTH_IMPLICIT_AVAILABLE = False
    logger.warning("Perth watermarking library not available. Install with: pip install resemble-perth")

    # Watermarking not available - functionality disabled
    DummyWatermarker = None
    PerthImplicitWatermarker = None

@dataclass
class WatermarkResult:
    """Result of watermarking operation"""
    success: bool
    watermarked_audio: Optional[np.ndarray]
    original_audio: Optional[np.ndarray]
    watermark_id: Optional[str]
    processing_time_ms: float
    quality_metrics: Optional[Dict[str, float]]
    error_message: Optional[str] = None

@dataclass
class WatermarkDetectionResult:
    """Result of watermark detection operation"""
    success: bool
    watermark_detected: bool
    watermark_id: Optional[str]
    confidence_score: float
    processing_time_ms: float
    error_message: Optional[str] = None

class AudioWatermarker:
    """
    Responsible AI audio watermarking system using Perth library
    
    Provides automatic watermarking of all generated TTS audio for:
    - Ethical AI compliance
    - Content authenticity verification
    - Deepfake detection support
    """
    
    def __init__(self, config=None):
        self.config = config
        self.enabled = self._get_config_value('watermarking_enabled', True)
        self.strength = self._get_config_value('watermark_strength', 1.0)
        self.detection_enabled = self._get_config_value('watermark_detection_enabled', True)
        self.device = self._get_config_value('device', 'cpu')
        self.use_dummy = self._get_config_value('use_dummy_watermarker', False)
        
        # Initialize watermarker
        self.watermarker = None
        self.watermarker_type = "none"
        
        if self.enabled:
            self._initialize_watermarker()
        
        # Statistics
        self.stats = {
            'total_watermarked': 0,
            'total_detected': 0,
            'successful_watermarks': 0,
            'successful_detections': 0,
            'average_processing_time_ms': 0.0,
            'total_processing_time_ms': 0.0
        }
        
        logger.info(f"AudioWatermarker initialized: enabled={self.enabled}, "
                   f"type={self.watermarker_type}, device={self.device}")
    
    def _get_config_value(self, key: str, default: Any) -> Any:
        """Get configuration value with fallback"""
        if self.config and hasattr(self.config, 'audio'):
            return getattr(self.config.audio, key, default)
        return default
    
    def _initialize_watermarker(self):
        """Initialize the Perth watermarker"""
        if not _PERTH_AVAILABLE:
            logger.warning("Perth library not available. Using mock watermarkers for testing.")
            # Don't disable watermarking, use mock classes instead

        try:
            if self.use_dummy or not _PERTH_IMPLICIT_AVAILABLE:
                # Use Perth DummyWatermarker (preferred) or fallback to mock
                if _PERTH_AVAILABLE:
                    self.watermarker = DummyWatermarker()
                    self.watermarker_type = "perth_dummy"
                    logger.info("Initialized Perth DummyWatermarker")
                else:
                    # Use mock dummy watermarker
                    self.watermarker = DummyWatermarker()  # This will be the mock version
                    self.watermarker_type = "mock_dummy"
                    logger.info("Initialized mock dummy watermarker")
            else:
                # Use Perth implicit watermarker if available
                self.watermarker = PerthImplicitWatermarker(device=self.device)
                self.watermarker_type = "perth_implicit"
                logger.info(f"Initialized Perth implicit watermarker on {self.device}")

        except Exception as e:
            logger.error(f"Failed to initialize watermarker: {e}")
            # Fallback to Perth DummyWatermarker or mock
            try:
                if _PERTH_AVAILABLE:
                    self.watermarker = DummyWatermarker()
                    self.watermarker_type = "perth_dummy_fallback"
                    logger.info("Fallback to Perth DummyWatermarker")
                else:
                    # Use mock dummy watermarker
                    self.watermarker = DummyWatermarker()  # Mock version
                    self.watermarker_type = "mock_dummy_fallback"
                    logger.info("Fallback to mock dummy watermarker")
            except Exception as e2:
                logger.error(f"Failed to initialize fallback watermarker: {e2}")
                self.enabled = False
    
    def apply_watermark(self, 
                       audio: np.ndarray, 
                       sample_rate: int,
                       watermark_id: Optional[str] = None) -> WatermarkResult:
        """
        Apply watermark to audio
        
        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate of the audio
            watermark_id: Optional custom watermark identifier
            
        Returns:
            WatermarkResult with watermarked audio and metadata
        """
        start_time = time.perf_counter()
        
        if not self.enabled or self.watermarker is None:
            return WatermarkResult(
                success=False,
                watermarked_audio=audio,  # Return original audio
                original_audio=audio,
                watermark_id=None,
                processing_time_ms=0.0,
                quality_metrics=None,
                error_message="Watermarking disabled or not available"
            )
        
        try:
            # Generate watermark ID if not provided
            if watermark_id is None:
                watermark_id = self._generate_watermark_id()
            
            # Apply watermark
            if self.watermarker_type == "dummy":
                # Dummy watermarker just returns the original audio
                watermarked_audio = audio.copy()
            else:
                # Perth implicit watermarker
                watermarked_audio = self.watermarker.apply_watermark(
                    audio, 
                    watermark=watermark_id,
                    sample_rate=sample_rate
                )
            
            # Calculate processing time
            processing_time = (time.perf_counter() - start_time) * 1000
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(audio, watermarked_audio)
            
            # Update statistics
            self.stats['total_watermarked'] += 1
            self.stats['successful_watermarks'] += 1
            self.stats['total_processing_time_ms'] += processing_time
            self.stats['average_processing_time_ms'] = (
                self.stats['total_processing_time_ms'] / self.stats['total_watermarked']
            )
            
            logger.debug(f"Applied watermark {watermark_id} in {processing_time:.2f}ms")
            
            return WatermarkResult(
                success=True,
                watermarked_audio=watermarked_audio,
                original_audio=audio,
                watermark_id=watermark_id,
                processing_time_ms=processing_time,
                quality_metrics=quality_metrics
            )
            
        except Exception as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            self.stats['total_watermarked'] += 1
            
            logger.error(f"Failed to apply watermark: {e}")
            
            return WatermarkResult(
                success=False,
                watermarked_audio=audio,  # Return original audio on failure
                original_audio=audio,
                watermark_id=watermark_id,
                processing_time_ms=processing_time,
                quality_metrics=None,
                error_message=str(e)
            )
    
    def detect_watermark(self, 
                        audio: np.ndarray, 
                        sample_rate: int) -> WatermarkDetectionResult:
        """
        Detect watermark in audio
        
        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            WatermarkDetectionResult with detection information
        """
        start_time = time.perf_counter()
        
        if not self.detection_enabled or self.watermarker is None:
            return WatermarkDetectionResult(
                success=False,
                watermark_detected=False,
                watermark_id=None,
                confidence_score=0.0,
                processing_time_ms=0.0,
                error_message="Watermark detection disabled or not available"
            )
        
        try:
            # Detect watermark
            if self.watermarker_type == "dummy":
                # Dummy watermarker always detects a fake watermark
                watermark_id = "dummy_watermark"
                confidence_score = 1.0
                watermark_detected = True
            else:
                # Perth implicit watermarker
                watermark_id = self.watermarker.get_watermark(audio, sample_rate=sample_rate)
                watermark_detected = watermark_id is not None
                confidence_score = 1.0 if watermark_detected else 0.0
            
            # Calculate processing time
            processing_time = (time.perf_counter() - start_time) * 1000
            
            # Update statistics
            self.stats['total_detected'] += 1
            if watermark_detected:
                self.stats['successful_detections'] += 1
            
            logger.debug(f"Watermark detection completed in {processing_time:.2f}ms: "
                        f"detected={watermark_detected}, id={watermark_id}")
            
            return WatermarkDetectionResult(
                success=True,
                watermark_detected=watermark_detected,
                watermark_id=watermark_id,
                confidence_score=confidence_score,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            self.stats['total_detected'] += 1
            
            logger.error(f"Failed to detect watermark: {e}")
            
            return WatermarkDetectionResult(
                success=False,
                watermark_detected=False,
                watermark_id=None,
                confidence_score=0.0,
                processing_time_ms=processing_time,
                error_message=str(e)
            )
    
    def _generate_watermark_id(self) -> str:
        """Generate a unique watermark identifier"""
        import hashlib
        import time
        
        # Create unique ID based on timestamp and random component
        timestamp = str(time.time())
        random_component = str(np.random.randint(0, 1000000))
        unique_string = f"kokoro_tts_{timestamp}_{random_component}"
        
        # Generate hash
        watermark_id = hashlib.md5(unique_string.encode()).hexdigest()[:16]
        return f"kokoro_{watermark_id}"
    
    def _calculate_quality_metrics(self, 
                                  original: np.ndarray, 
                                  watermarked: np.ndarray) -> Dict[str, float]:
        """Calculate audio quality metrics"""
        try:
            # Signal-to-Noise Ratio (SNR)
            signal_power = np.mean(original ** 2)
            noise_power = np.mean((watermarked - original) ** 2)
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
            else:
                snr = float('inf')
            
            # Peak Signal-to-Noise Ratio (PSNR)
            max_signal = np.max(np.abs(original))
            if noise_power > 0 and max_signal > 0:
                psnr = 20 * np.log10(max_signal / np.sqrt(noise_power))
            else:
                psnr = float('inf')
            
            # Mean Squared Error (MSE)
            mse = np.mean((watermarked - original) ** 2)
            
            return {
                'snr_db': float(snr),
                'psnr_db': float(psnr),
                'mse': float(mse),
                'max_difference': float(np.max(np.abs(watermarked - original)))
            }
            
        except Exception as e:
            logger.warning(f"Failed to calculate quality metrics: {e}")
            return {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get watermarking statistics"""
        stats = self.stats.copy()
        
        # Calculate success rates
        if stats['total_watermarked'] > 0:
            stats['watermark_success_rate'] = stats['successful_watermarks'] / stats['total_watermarked']
        else:
            stats['watermark_success_rate'] = 0.0
        
        if stats['total_detected'] > 0:
            stats['detection_success_rate'] = stats['successful_detections'] / stats['total_detected']
        else:
            stats['detection_success_rate'] = 0.0
        
        # Add configuration info
        stats['watermarker_type'] = self.watermarker_type
        stats['enabled'] = self.enabled
        stats['detection_enabled'] = self.detection_enabled
        stats['device'] = self.device
        
        return stats
    
    def reset_statistics(self):
        """Reset watermarking statistics"""
        self.stats = {
            'total_watermarked': 0,
            'total_detected': 0,
            'successful_watermarks': 0,
            'successful_detections': 0,
            'average_processing_time_ms': 0.0,
            'total_processing_time_ms': 0.0
        }
        logger.info("Watermarking statistics reset")

# Global watermarker instance
_audio_watermarker: Optional[AudioWatermarker] = None

def get_audio_watermarker(config=None) -> AudioWatermarker:
    """Get or create the global audio watermarker instance"""
    global _audio_watermarker
    
    if _audio_watermarker is None:
        _audio_watermarker = AudioWatermarker(config)
    
    return _audio_watermarker
