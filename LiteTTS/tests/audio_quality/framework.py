#!/usr/bin/env python3
"""
Comprehensive Audio Quality Test Suite Framework
Provides technical validation, content validation, and quality metrics for TTS output
"""

import numpy as np
import soundfile as sf
import librosa
import json
import time
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import subprocess

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TestResult(Enum):
    """Test result status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class QualityThresholds:
    """Configurable quality thresholds"""
    min_mos_score: float = 3.0
    max_wer: float = 0.1
    min_pronunciation_accuracy: float = 0.9
    max_rtf: float = 0.25
    min_prosody_score: float = 0.7
    min_amplitude: float = 0.01
    max_amplitude: float = 0.95
    min_duration_ms: float = 100.0
    max_duration_variance: float = 0.3
    expected_sample_rate: int = 24000

@dataclass
class TechnicalMetrics:
    """Technical audio validation metrics"""
    amplitude_range: Tuple[float, float]
    duration_ms: float
    sample_rate: int
    format_valid: bool
    silence_ratio: float
    dynamic_range: float
    spectral_centroid: float
    zero_crossing_rate: float

@dataclass
class ContentMetrics:
    """Content validation metrics"""
    transcription: str
    wer_score: float
    pronunciation_accuracy: float
    word_count: int
    character_count: int
    confidence_score: float

@dataclass
class QualityMetrics:
    """Quality assessment metrics"""
    mos_prediction: float
    prosody_score: float
    naturalness_score: float
    intelligibility_score: float
    emotional_consistency: float

@dataclass
class PerformanceMetrics:
    """Performance measurement metrics"""
    rtf: float
    generation_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float

@dataclass
class AudioQualityReport:
    """Comprehensive audio quality assessment report"""
    test_id: str
    timestamp: str
    input_text: str
    model_type: str
    voice_name: str
    technical_metrics: TechnicalMetrics
    content_metrics: ContentMetrics
    quality_metrics: QualityMetrics
    performance_metrics: PerformanceMetrics
    overall_result: TestResult
    validation_errors: List[str]
    warnings: List[str]
    score: float

class AudioQualityValidator:
    """Comprehensive audio quality validation system"""
    
    def __init__(self, thresholds: Optional[QualityThresholds] = None):
        self.thresholds = thresholds or QualityThresholds()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="audio_quality_"))
        self.whisper_model = None
        self._initialize_asr()
    
    def _initialize_asr(self):
        """Initialize ASR system for content validation"""
        try:
            import whisper
            self.whisper_model = whisper.load_model("base")
            logger.info("Whisper ASR model loaded successfully")
        except ImportError:
            logger.warning("Whisper not available, content validation will be limited")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
    
    def validate_audio(self, audio_file: Union[str, Path], 
                      input_text: str, model_type: str, 
                      voice_name: str, test_id: str) -> AudioQualityReport:
        """
        Perform comprehensive audio quality validation
        
        Args:
            audio_file: Path to generated audio file
            input_text: Original input text
            model_type: Model type used (GGUF/ONNX)
            voice_name: Voice used for generation
            test_id: Unique test identifier
            
        Returns:
            AudioQualityReport: Comprehensive validation report
        """
        start_time = time.time()
        validation_errors = []
        warnings = []
        
        try:
            # Load audio data
            audio_data, sample_rate = sf.read(audio_file)
            
            # Technical validation
            technical_metrics = self._validate_technical(audio_data, sample_rate, validation_errors, warnings)
            
            # Content validation
            content_metrics = self._validate_content(audio_file, input_text, validation_errors, warnings)
            
            # Quality metrics
            quality_metrics = self._assess_quality(audio_data, sample_rate, validation_errors, warnings)
            
            # Performance metrics (placeholder - would be populated by caller)
            performance_metrics = PerformanceMetrics(
                rtf=0.0,
                generation_time_ms=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0
            )
            
            # Calculate overall score and result
            overall_score = self._calculate_overall_score(
                technical_metrics, content_metrics, quality_metrics
            )
            overall_result = self._determine_overall_result(validation_errors, warnings, overall_score)
            
            return AudioQualityReport(
                test_id=test_id,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                input_text=input_text,
                model_type=model_type,
                voice_name=voice_name,
                technical_metrics=technical_metrics,
                content_metrics=content_metrics,
                quality_metrics=quality_metrics,
                performance_metrics=performance_metrics,
                overall_result=overall_result,
                validation_errors=validation_errors,
                warnings=warnings,
                score=overall_score
            )
            
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return self._create_error_report(test_id, input_text, model_type, voice_name, str(e))
    
    def _validate_technical(self, audio_data: np.ndarray, sample_rate: int,
                           errors: List[str], warnings: List[str]) -> TechnicalMetrics:
        """Perform technical audio validation"""
        try:
            # Amplitude analysis
            amplitude_min, amplitude_max = float(np.min(audio_data)), float(np.max(audio_data))
            amplitude_range = (amplitude_min, amplitude_max)
            
            if amplitude_max < self.thresholds.min_amplitude:
                errors.append(f"Audio too quiet: max amplitude {amplitude_max:.3f} < {self.thresholds.min_amplitude}")
            if amplitude_max > self.thresholds.max_amplitude:
                warnings.append(f"Audio may be clipping: max amplitude {amplitude_max:.3f} > {self.thresholds.max_amplitude}")
            
            # Duration analysis
            duration_ms = len(audio_data) / sample_rate * 1000
            if duration_ms < self.thresholds.min_duration_ms:
                errors.append(f"Audio too short: {duration_ms:.1f}ms < {self.thresholds.min_duration_ms}ms")
            
            # Sample rate validation
            format_valid = sample_rate == self.thresholds.expected_sample_rate
            if not format_valid:
                warnings.append(f"Unexpected sample rate: {sample_rate} != {self.thresholds.expected_sample_rate}")
            
            # Silence analysis
            silence_threshold = 0.01
            silence_samples = np.sum(np.abs(audio_data) < silence_threshold)
            silence_ratio = silence_samples / len(audio_data)
            
            # Dynamic range
            dynamic_range = amplitude_max - amplitude_min
            
            # Spectral features
            spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)))
            zero_crossing_rate = float(np.mean(librosa.feature.zero_crossing_rate(audio_data)))
            
            return TechnicalMetrics(
                amplitude_range=amplitude_range,
                duration_ms=duration_ms,
                sample_rate=sample_rate,
                format_valid=format_valid,
                silence_ratio=silence_ratio,
                dynamic_range=dynamic_range,
                spectral_centroid=spectral_centroid,
                zero_crossing_rate=zero_crossing_rate
            )
            
        except Exception as e:
            errors.append(f"Technical validation failed: {e}")
            return TechnicalMetrics(
                amplitude_range=(0.0, 0.0),
                duration_ms=0.0,
                sample_rate=0,
                format_valid=False,
                silence_ratio=1.0,
                dynamic_range=0.0,
                spectral_centroid=0.0,
                zero_crossing_rate=0.0
            )
    
    def _validate_content(self, audio_file: Path, input_text: str,
                         errors: List[str], warnings: List[str]) -> ContentMetrics:
        """Perform content validation using ASR"""
        try:
            if not self.whisper_model:
                warnings.append("ASR not available, content validation skipped")
                return ContentMetrics(
                    transcription="",
                    wer_score=0.0,
                    pronunciation_accuracy=0.0,
                    word_count=0,
                    character_count=0,
                    confidence_score=0.0
                )
            
            # Transcribe audio
            result = self.whisper_model.transcribe(str(audio_file))
            transcription = result["text"].strip()
            
            # Calculate WER
            wer_score = self._calculate_wer(input_text, transcription)
            if wer_score > self.thresholds.max_wer:
                errors.append(f"High WER: {wer_score:.3f} > {self.thresholds.max_wer}")
            
            # Pronunciation accuracy (simplified)
            pronunciation_accuracy = max(0.0, 1.0 - wer_score)
            if pronunciation_accuracy < self.thresholds.min_pronunciation_accuracy:
                errors.append(f"Low pronunciation accuracy: {pronunciation_accuracy:.3f}")
            
            return ContentMetrics(
                transcription=transcription,
                wer_score=wer_score,
                pronunciation_accuracy=pronunciation_accuracy,
                word_count=len(transcription.split()),
                character_count=len(transcription),
                confidence_score=0.8  # Placeholder
            )
            
        except Exception as e:
            errors.append(f"Content validation failed: {e}")
            return ContentMetrics(
                transcription="",
                wer_score=1.0,
                pronunciation_accuracy=0.0,
                word_count=0,
                character_count=0,
                confidence_score=0.0
            )
    
    def _assess_quality(self, audio_data: np.ndarray, sample_rate: int,
                       errors: List[str], warnings: List[str]) -> QualityMetrics:
        """Assess audio quality metrics"""
        try:
            # MOS prediction (simplified heuristic)
            mos_prediction = self._predict_mos(audio_data, sample_rate)
            if mos_prediction < self.thresholds.min_mos_score:
                warnings.append(f"Low predicted MOS: {mos_prediction:.2f}")
            
            # Prosody analysis (simplified)
            prosody_score = self._analyze_prosody(audio_data, sample_rate)
            if prosody_score < self.thresholds.min_prosody_score:
                warnings.append(f"Low prosody score: {prosody_score:.2f}")
            
            return QualityMetrics(
                mos_prediction=mos_prediction,
                prosody_score=prosody_score,
                naturalness_score=0.8,  # Placeholder
                intelligibility_score=0.85,  # Placeholder
                emotional_consistency=0.75  # Placeholder
            )
            
        except Exception as e:
            warnings.append(f"Quality assessment failed: {e}")
            return QualityMetrics(
                mos_prediction=2.5,
                prosody_score=0.5,
                naturalness_score=0.5,
                intelligibility_score=0.5,
                emotional_consistency=0.5
            )
    
    def _calculate_wer(self, reference: str, hypothesis: str) -> float:
        """Calculate Word Error Rate"""
        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()
        
        if len(ref_words) == 0:
            return 1.0 if len(hyp_words) > 0 else 0.0
        
        # Simple edit distance calculation
        d = np.zeros((len(ref_words) + 1, len(hyp_words) + 1))
        
        for i in range(len(ref_words) + 1):
            d[i][0] = i
        for j in range(len(hyp_words) + 1):
            d[0][j] = j
        
        for i in range(1, len(ref_words) + 1):
            for j in range(1, len(hyp_words) + 1):
                if ref_words[i-1] == hyp_words[j-1]:
                    d[i][j] = d[i-1][j-1]
                else:
                    d[i][j] = min(d[i-1][j], d[i][j-1], d[i-1][j-1]) + 1
        
        return d[len(ref_words)][len(hyp_words)] / len(ref_words)
    
    def _predict_mos(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Predict MOS score using heuristics"""
        # Simplified MOS prediction based on audio characteristics
        snr = self._estimate_snr(audio_data)
        spectral_quality = self._assess_spectral_quality(audio_data, sample_rate)
        
        # Combine metrics (simplified)
        mos = 2.5 + (snr / 40.0) * 2.0 + spectral_quality * 0.5
        return min(5.0, max(1.0, mos))
    
    def _analyze_prosody(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Analyze prosodic features"""
        try:
            # Extract pitch and energy contours
            f0 = librosa.yin(audio_data, fmin=80, fmax=400, sr=sample_rate)
            energy = librosa.feature.rms(y=audio_data)[0]
            
            # Analyze variation (simplified prosody measure)
            f0_var = np.var(f0[f0 > 0]) if np.any(f0 > 0) else 0
            energy_var = np.var(energy)
            
            # Normalize and combine
            prosody_score = min(1.0, (f0_var / 1000 + energy_var) * 10)
            return prosody_score
            
        except Exception:
            return 0.5  # Default moderate score
    
    def _estimate_snr(self, audio_data: np.ndarray) -> float:
        """Estimate Signal-to-Noise Ratio"""
        # Simple SNR estimation
        signal_power = np.mean(audio_data ** 2)
        noise_power = np.mean((audio_data - np.mean(audio_data)) ** 2) * 0.1  # Simplified
        
        if noise_power > 0:
            snr_db = 10 * np.log10(signal_power / noise_power)
            return max(0, min(60, snr_db))
        return 30.0  # Default reasonable SNR
    
    def _assess_spectral_quality(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Assess spectral quality"""
        try:
            # Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate))
            spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate))
            
            # Normalize to 0-1 range (simplified)
            quality = min(1.0, (spectral_centroid / 4000 + spectral_bandwidth / 8000) / 2)
            return quality
            
        except Exception:
            return 0.5
    
    def _calculate_overall_score(self, technical: TechnicalMetrics, 
                                content: ContentMetrics, quality: QualityMetrics) -> float:
        """Calculate overall quality score"""
        # Weighted combination of metrics
        technical_score = 1.0 if technical.format_valid else 0.5
        technical_score *= min(1.0, technical.dynamic_range * 2)
        
        content_score = content.pronunciation_accuracy
        quality_score = (quality.mos_prediction / 5.0 + quality.prosody_score) / 2
        
        # Weighted average
        overall = (technical_score * 0.3 + content_score * 0.4 + quality_score * 0.3)
        return min(1.0, max(0.0, overall))
    
    def _determine_overall_result(self, errors: List[str], warnings: List[str], score: float) -> TestResult:
        """Determine overall test result"""
        if errors:
            return TestResult.FAIL
        elif warnings and score < 0.7:
            return TestResult.WARNING
        elif score >= 0.8:
            return TestResult.PASS
        else:
            return TestResult.WARNING
    
    def _create_error_report(self, test_id: str, input_text: str, 
                           model_type: str, voice_name: str, error: str) -> AudioQualityReport:
        """Create error report for failed validation"""
        return AudioQualityReport(
            test_id=test_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            input_text=input_text,
            model_type=model_type,
            voice_name=voice_name,
            technical_metrics=TechnicalMetrics((0,0), 0, 0, False, 1.0, 0, 0, 0),
            content_metrics=ContentMetrics("", 1.0, 0.0, 0, 0, 0.0),
            quality_metrics=QualityMetrics(1.0, 0.0, 0.0, 0.0, 0.0),
            performance_metrics=PerformanceMetrics(0.0, 0.0, 0.0, 0.0),
            overall_result=TestResult.ERROR,
            validation_errors=[error],
            warnings=[],
            score=0.0
        )
    
    def cleanup(self):
        """Clean up temporary resources"""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")
