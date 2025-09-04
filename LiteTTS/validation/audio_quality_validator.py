"""
Audio Quality Validator for LiteTTS

This module provides comprehensive audio quality validation capabilities
including transcription accuracy measurement using Word Error Rate (WER)
and other quality metrics.
"""

import logging
import time
import os
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import difflib

from .whisper_integration import WhisperValidator, create_whisper_validator

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Audio quality metrics container"""
    wer: float  # Word Error Rate (0.0 = perfect, 1.0 = completely wrong)
    cer: float  # Character Error Rate
    bleu_score: float  # BLEU score (0.0-1.0, higher is better)
    transcription_time: float  # Time taken for transcription
    audio_duration: float  # Duration of audio file
    rtf: float  # Real-time factor (transcription_time / audio_duration)
    confidence_score: float  # Average confidence from Whisper
    word_count: int  # Number of words in reference text
    success: bool  # Whether validation was successful
    error_message: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result for an audio file"""
    audio_path: str
    reference_text: str
    transcribed_text: str
    metrics: QualityMetrics
    voice_name: str
    timestamp: float
    details: Dict[str, Any]


class AudioQualityValidator:
    """
    Comprehensive audio quality validator using Whisper STT.
    
    Provides transcription accuracy measurement, WER calculation,
    and other quality metrics for TTS-generated audio.
    """
    
    def __init__(self, whisper_model_size: str = "base", whisper_config: Optional[Dict] = None):
        """
        Initialize AudioQualityValidator.
        
        Args:
            whisper_model_size: Whisper model size for transcription
            whisper_config: Optional configuration for Whisper model
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize Whisper validator
        config_kwargs = whisper_config or {}
        self.whisper_validator = create_whisper_validator(
            model_size=whisper_model_size,
            **config_kwargs
        )
        
        self.model_loaded = False
        self.validation_cache = {}  # Cache for repeated validations
        
    def initialize(self) -> bool:
        """
        Initialize the validator by loading the Whisper model.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing AudioQualityValidator...")
            
            # Load Whisper model
            load_result = self.whisper_validator.load_model(timeout_seconds=30.0)
            
            if load_result.success:
                self.model_loaded = True
                self.logger.info(f"✅ AudioQualityValidator initialized successfully")
                self.logger.info(f"   Whisper model: {load_result.model_size}")
                self.logger.info(f"   Load time: {load_result.load_time_seconds:.1f}s")
                self.logger.info(f"   Device: {load_result.device}")
                return True
            else:
                self.logger.error(f"Failed to initialize: {load_result.error_message}")
                return False
                
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    def validate_transcription(self, audio_path: str, reference_text: str, 
                             voice_name: str = "unknown") -> ValidationResult:
        """
        Validate transcription accuracy of an audio file.
        
        Args:
            audio_path: Path to audio file to validate
            reference_text: Expected text content
            voice_name: Name of the voice used for generation
            
        Returns:
            ValidationResult with comprehensive quality metrics
        """
        if not self.model_loaded:
            raise RuntimeError("Validator not initialized. Call initialize() first.")
        
        start_time = time.time()
        
        try:
            # Check if audio file exists
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Get audio duration
            audio_duration = self._get_audio_duration(audio_path)
            
            # Transcribe audio using Whisper
            transcription_result = self.whisper_validator.transcribe_audio(
                audio_path,
                beam_size=5,  # Higher beam size for better accuracy
                best_of=5,    # Multiple candidates for better results
                temperature=0.0  # Deterministic output
            )
            
            if not transcription_result["success"]:
                raise RuntimeError(f"Transcription failed: {transcription_result.get('error', 'Unknown error')}")
            
            transcribed_text = transcription_result["text"]
            transcription_time = transcription_result["transcription_time"]
            
            # Calculate quality metrics
            metrics = self._calculate_quality_metrics(
                reference_text=reference_text,
                transcribed_text=transcribed_text,
                transcription_time=transcription_time,
                audio_duration=audio_duration,
                language_probability=transcription_result.get("language_probability", 0.0)
            )
            
            # Create detailed result
            validation_time = time.time() - start_time
            
            result = ValidationResult(
                audio_path=audio_path,
                reference_text=reference_text,
                transcribed_text=transcribed_text,
                metrics=metrics,
                voice_name=voice_name,
                timestamp=start_time,
                details={
                    "validation_time": validation_time,
                    "whisper_language": transcription_result.get("language", "unknown"),
                    "whisper_language_probability": transcription_result.get("language_probability", 0.0),
                    "whisper_duration": transcription_result.get("duration", 0.0),
                    "segments": transcription_result.get("segments", []),
                    "audio_file_size": os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
                }
            )
            
            self.logger.info(f"✅ Validation completed for {voice_name}")
            self.logger.info(f"   WER: {metrics.wer:.3f}, RTF: {metrics.rtf:.3f}")
            
            return result
            
        except Exception as e:
            error_msg = f"Validation failed for {audio_path}: {str(e)}"
            self.logger.error(error_msg)
            
            # Return failed result
            failed_metrics = QualityMetrics(
                wer=1.0,
                cer=1.0,
                bleu_score=0.0,
                transcription_time=0.0,
                audio_duration=0.0,
                rtf=0.0,
                confidence_score=0.0,
                word_count=len(reference_text.split()),
                success=False,
                error_message=str(e)
            )
            
            return ValidationResult(
                audio_path=audio_path,
                reference_text=reference_text,
                transcribed_text="",
                metrics=failed_metrics,
                voice_name=voice_name,
                timestamp=start_time,
                details={"error": str(e)}
            )
    
    def _calculate_quality_metrics(self, reference_text: str, transcribed_text: str,
                                 transcription_time: float, audio_duration: float,
                                 language_probability: float) -> QualityMetrics:
        """Calculate comprehensive quality metrics."""
        
        # Normalize texts for comparison
        ref_normalized = self._normalize_text(reference_text)
        trans_normalized = self._normalize_text(transcribed_text)
        
        # Calculate WER (Word Error Rate)
        wer = self._calculate_wer(ref_normalized, trans_normalized)
        
        # Calculate CER (Character Error Rate)
        cer = self._calculate_cer(ref_normalized, trans_normalized)
        
        # Calculate BLEU score
        bleu_score = self._calculate_bleu_score(ref_normalized, trans_normalized)
        
        # Calculate RTF (Real-Time Factor)
        rtf = transcription_time / audio_duration if audio_duration > 0 else 0.0
        
        # Use language probability as confidence score
        confidence_score = language_probability
        
        return QualityMetrics(
            wer=wer,
            cer=cer,
            bleu_score=bleu_score,
            transcription_time=transcription_time,
            audio_duration=audio_duration,
            rtf=rtf,
            confidence_score=confidence_score,
            word_count=len(ref_normalized.split()),
            success=True
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        import re
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and extra whitespace
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _calculate_wer(self, reference: str, hypothesis: str) -> float:
        """Calculate Word Error Rate."""
        ref_words = reference.split()
        hyp_words = hypothesis.split()
        
        if len(ref_words) == 0:
            return 1.0 if len(hyp_words) > 0 else 0.0
        
        # Use difflib to calculate edit distance
        matcher = difflib.SequenceMatcher(None, ref_words, hyp_words)
        
        # Count operations
        substitutions = 0
        deletions = 0
        insertions = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                substitutions += max(i2 - i1, j2 - j1)
            elif tag == 'delete':
                deletions += i2 - i1
            elif tag == 'insert':
                insertions += j2 - j1
        
        total_errors = substitutions + deletions + insertions
        wer = total_errors / len(ref_words)
        
        return min(wer, 1.0)  # Cap at 1.0
    
    def _calculate_cer(self, reference: str, hypothesis: str) -> float:
        """Calculate Character Error Rate."""
        if len(reference) == 0:
            return 1.0 if len(hypothesis) > 0 else 0.0
        
        # Use difflib for character-level comparison
        matcher = difflib.SequenceMatcher(None, reference, hypothesis)
        
        # Count character-level operations
        total_errors = 0
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                total_errors += max(i2 - i1, j2 - j1)
        
        cer = total_errors / len(reference)
        return min(cer, 1.0)  # Cap at 1.0
    
    def _calculate_bleu_score(self, reference: str, hypothesis: str) -> float:
        """Calculate simplified BLEU score."""
        ref_words = reference.split()
        hyp_words = hypothesis.split()
        
        if len(ref_words) == 0 or len(hyp_words) == 0:
            return 0.0
        
        # Calculate 1-gram precision
        ref_counts = {}
        for word in ref_words:
            ref_counts[word] = ref_counts.get(word, 0) + 1
        
        hyp_counts = {}
        for word in hyp_words:
            hyp_counts[word] = hyp_counts.get(word, 0) + 1
        
        # Count matches
        matches = 0
        for word, count in hyp_counts.items():
            if word in ref_counts:
                matches += min(count, ref_counts[word])
        
        precision = matches / len(hyp_words) if len(hyp_words) > 0 else 0.0
        
        # Brevity penalty
        bp = min(1.0, len(hyp_words) / len(ref_words)) if len(ref_words) > 0 else 0.0
        
        # Simplified BLEU (1-gram only)
        bleu = bp * precision
        
        return bleu
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio file duration in seconds."""
        try:
            # Try using librosa if available
            try:
                import librosa
                duration = librosa.get_duration(path=audio_path)
                return duration
            except ImportError:
                pass
            
            # Fallback: estimate from file size (rough approximation)
            # This is very rough and should be replaced with proper audio analysis
            file_size = os.path.getsize(audio_path)
            # Assume ~128kbps MP3 encoding: 16KB/s
            estimated_duration = file_size / 16000
            
            self.logger.warning(f"Using estimated duration for {audio_path}: {estimated_duration:.1f}s")
            return estimated_duration
            
        except Exception as e:
            self.logger.warning(f"Could not determine audio duration for {audio_path}: {e}")
            return 1.0  # Default fallback
    
    def batch_validate(self, audio_files: List[Tuple[str, str, str]]) -> List[ValidationResult]:
        """
        Validate multiple audio files in batch.
        
        Args:
            audio_files: List of (audio_path, reference_text, voice_name) tuples
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        
        self.logger.info(f"Starting batch validation of {len(audio_files)} files")
        
        for i, (audio_path, reference_text, voice_name) in enumerate(audio_files):
            self.logger.info(f"Validating {i+1}/{len(audio_files)}: {voice_name}")
            
            result = self.validate_transcription(audio_path, reference_text, voice_name)
            results.append(result)
            
            # Log progress
            if result.metrics.success:
                self.logger.info(f"   ✅ WER: {result.metrics.wer:.3f}")
            else:
                self.logger.error(f"   ❌ Failed: {result.metrics.error_message}")
        
        self.logger.info(f"Batch validation completed: {len(results)} results")
        return results
    
    def get_summary_statistics(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Calculate summary statistics from validation results."""
        successful_results = [r for r in results if r.metrics.success]
        
        if not successful_results:
            return {
                "total_files": len(results),
                "successful_validations": 0,
                "success_rate": 0.0,
                "error": "No successful validations"
            }
        
        wer_values = [r.metrics.wer for r in successful_results]
        rtf_values = [r.metrics.rtf for r in successful_results]
        
        return {
            "total_files": len(results),
            "successful_validations": len(successful_results),
            "success_rate": len(successful_results) / len(results),
            "average_wer": sum(wer_values) / len(wer_values),
            "min_wer": min(wer_values),
            "max_wer": max(wer_values),
            "average_rtf": sum(rtf_values) / len(rtf_values),
            "min_rtf": min(rtf_values),
            "max_rtf": max(rtf_values),
            "voices_tested": len(set(r.voice_name for r in results))
        }
