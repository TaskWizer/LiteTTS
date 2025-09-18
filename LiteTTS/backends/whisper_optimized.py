#!/usr/bin/env python3
"""
Optimized Whisper Backend for LiteTTS
Implements faster-whisper with distil-small.en and INT8 quantization for edge hardware deployment
"""

import os
import time
import logging
import psutil
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class WhisperImplementation(Enum):
    """Available Whisper implementations"""
    FASTER_WHISPER = "faster-whisper"
    OPENAI_WHISPER = "openai-whisper"
    DISTIL_WHISPER = "distil-whisper"

@dataclass
class WhisperConfig:
    """Configuration for Whisper processor"""
    implementation: WhisperImplementation = WhisperImplementation.FASTER_WHISPER
    model_name: str = "distil-small.en"
    compute_type: str = "int8"
    device: str = "cpu"
    cpu_threads: int = 4
    beam_size: int = 5
    language: str = "en"
    condition_on_previous_text: bool = False
    model_cache_dir: Optional[str] = None
    enable_fallback: bool = True
    rtf_threshold: float = 1.0
    memory_threshold_mb: float = 2000

@dataclass
class TranscriptionResult:
    """Result of transcription operation"""
    text: str
    processing_time: float
    rtf: float
    memory_usage_mb: float
    model_used: str
    success: bool
    error_message: Optional[str] = None
    confidence: Optional[float] = None

class PerformanceMonitor:
    """Monitor performance metrics during transcription"""
    
    def __init__(self):
        self.start_memory = 0
        self.peak_memory = 0
        self.monitoring = False
        self.memory_samples = []
        
    def start(self):
        """Start performance monitoring"""
        process = psutil.Process()
        self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.start_memory
        self.memory_samples = []
        self.monitoring = True
        
        # Start memory monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_memory)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop(self) -> float:
        """Stop monitoring and return peak memory usage"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1.0)
        return self.peak_memory - self.start_memory
        
    def _monitor_memory(self):
        """Monitor memory usage in background thread"""
        process = psutil.Process()
        while self.monitoring:
            try:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                self.memory_samples.append(current_memory)
                self.peak_memory = max(self.peak_memory, current_memory)
                time.sleep(0.1)  # Sample every 100ms
            except:
                break

class OptimizedWhisperProcessor:
    """
    Optimized Whisper processor with multiple implementation support and fallback mechanisms
    """
    
    def __init__(self, config: Optional[WhisperConfig] = None):
        self.config = config or WhisperConfig()
        self.models = {}  # Cache for loaded models
        self.performance_monitor = PerformanceMonitor()
        
        # Configure CPU threads from environment or config
        cpu_threads = int(os.environ.get('WHISPER_CPU_THREADS', self.config.cpu_threads))
        self.config.cpu_threads = min(cpu_threads, psutil.cpu_count(logical=False))
        
        # Set model cache directory
        if not self.config.model_cache_dir:
            self.config.model_cache_dir = os.path.join(
                os.path.expanduser("~"), ".cache", "whisper"
            )
        
        logger.info(f"OptimizedWhisperProcessor initialized with {self.config.implementation.value}")
        logger.info(f"Model: {self.config.model_name}, Compute: {self.config.compute_type}")
        logger.info(f"CPU threads: {self.config.cpu_threads}")
        
    def transcribe(self, audio_path: str, audio_duration: Optional[float] = None) -> TranscriptionResult:
        """
        Transcribe audio file with performance monitoring and fallback support
        
        Args:
            audio_path: Path to audio file
            audio_duration: Duration of audio in seconds (for RTF calculation)
            
        Returns:
            TranscriptionResult with text, performance metrics, and metadata
        """
        start_time = time.time()
        
        # Calculate audio duration if not provided
        if audio_duration is None:
            audio_duration = self._get_audio_duration(audio_path)
            
        # Start performance monitoring
        self.performance_monitor.start()
        
        try:
            # Try primary implementation
            result = self._transcribe_with_implementation(
                audio_path, 
                self.config.implementation,
                self.config.model_name
            )
            
            processing_time = time.time() - start_time
            memory_usage = self.performance_monitor.stop()
            rtf = processing_time / audio_duration if audio_duration > 0 else float('inf')
            
            # Check if performance meets thresholds
            if rtf > self.config.rtf_threshold or memory_usage > self.config.memory_threshold_mb:
                logger.warning(f"Performance threshold exceeded: RTF={rtf:.3f}, Memory={memory_usage:.1f}MB")
                
                # Try fallback if enabled and thresholds exceeded
                if self.config.enable_fallback and rtf > self.config.rtf_threshold:
                    logger.info("Attempting fallback to faster model...")
                    fallback_result = self._try_fallback(audio_path, audio_duration)
                    if fallback_result.success:
                        return fallback_result
            
            return TranscriptionResult(
                text=result,
                processing_time=processing_time,
                rtf=rtf,
                memory_usage_mb=memory_usage,
                model_used=f"{self.config.implementation.value}-{self.config.model_name}",
                success=True
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            memory_usage = self.performance_monitor.stop()
            
            logger.error(f"Transcription failed with {self.config.implementation.value}: {e}")
            
            # Try fallback on error
            if self.config.enable_fallback:
                logger.info("Attempting fallback due to error...")
                fallback_result = self._try_fallback(audio_path, audio_duration)
                if fallback_result.success:
                    return fallback_result
            
            return TranscriptionResult(
                text="",
                processing_time=processing_time,
                rtf=float('inf'),
                memory_usage_mb=memory_usage,
                model_used=f"{self.config.implementation.value}-{self.config.model_name}",
                success=False,
                error_message=str(e)
            )
            
    def _transcribe_with_implementation(self, audio_path: str, implementation: WhisperImplementation, model_name: str) -> str:
        """Transcribe using specific implementation"""
        
        if implementation == WhisperImplementation.FASTER_WHISPER:
            return self._transcribe_faster_whisper(audio_path, model_name)
        elif implementation == WhisperImplementation.OPENAI_WHISPER:
            return self._transcribe_openai_whisper(audio_path, model_name)
        elif implementation == WhisperImplementation.DISTIL_WHISPER:
            return self._transcribe_distil_whisper(audio_path, model_name)
        else:
            raise ValueError(f"Unsupported implementation: {implementation}")
            
    def _transcribe_faster_whisper(self, audio_path: str, model_name: str) -> str:
        """Transcribe using faster-whisper"""
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise ImportError("faster-whisper not installed. Install with: pip install faster-whisper")
            
        model_key = f"faster_whisper_{model_name}_{self.config.compute_type}"
        
        if model_key not in self.models:
            logger.info(f"Loading faster-whisper model: {model_name}")
            self.models[model_key] = WhisperModel(
                model_name,
                device=self.config.device,
                compute_type=self.config.compute_type,
                cpu_threads=self.config.cpu_threads,
                download_root=self.config.model_cache_dir
            )
            
        model = self.models[model_key]
        
        segments, info = model.transcribe(
            audio_path,
            beam_size=self.config.beam_size,
            language=self.config.language,
            condition_on_previous_text=self.config.condition_on_previous_text
        )
        
        return " ".join([segment.text for segment in segments]).strip()
        
    def _transcribe_openai_whisper(self, audio_path: str, model_name: str) -> str:
        """Transcribe using OpenAI Whisper (fallback)"""
        try:
            import whisper
        except ImportError:
            raise ImportError("openai-whisper not installed. Install with: pip install openai-whisper")
            
        model_key = f"openai_whisper_{model_name}"
        
        if model_key not in self.models:
            logger.info(f"Loading OpenAI Whisper model: {model_name}")
            self.models[model_key] = whisper.load_model(model_name)
            
        model = self.models[model_key]
        result = model.transcribe(audio_path)
        
        return result["text"].strip()
        
    def _transcribe_distil_whisper(self, audio_path: str, model_name: str) -> str:
        """Transcribe using Distil-Whisper"""
        try:
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
            import torch
            import soundfile as sf
        except ImportError:
            raise ImportError("transformers and torch not installed for Distil-Whisper")
            
        model_key = f"distil_whisper_{model_name}"
        
        if model_key not in self.models:
            logger.info(f"Loading Distil-Whisper model: {model_name}")
            
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                f"distil-whisper/{model_name}",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                use_safetensors=True
            )
            processor = AutoProcessor.from_pretrained(f"distil-whisper/{model_name}")
            
            self.models[model_key] = (model, processor)
            
        model, processor = self.models[model_key]
        
        # Load and process audio
        audio_array, sample_rate = sf.read(audio_path)
        inputs = processor(audio_array, sampling_rate=sample_rate, return_tensors="pt")
        
        with torch.no_grad():
            predicted_ids = model.generate(
                inputs["input_features"],
                max_new_tokens=128,
                do_sample=False
            )
            
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        return transcription.strip()
        
    def _try_fallback(self, audio_path: str, audio_duration: float) -> TranscriptionResult:
        """Try fallback implementations"""
        fallback_configs = [
            (WhisperImplementation.FASTER_WHISPER, "base"),
            (WhisperImplementation.OPENAI_WHISPER, "base"),
            (WhisperImplementation.OPENAI_WHISPER, "tiny")
        ]
        
        for implementation, model_name in fallback_configs:
            try:
                logger.info(f"Trying fallback: {implementation.value} with {model_name}")
                
                start_time = time.time()
                self.performance_monitor.start()
                
                result = self._transcribe_with_implementation(audio_path, implementation, model_name)
                
                processing_time = time.time() - start_time
                memory_usage = self.performance_monitor.stop()
                rtf = processing_time / audio_duration if audio_duration > 0 else float('inf')
                
                return TranscriptionResult(
                    text=result,
                    processing_time=processing_time,
                    rtf=rtf,
                    memory_usage_mb=memory_usage,
                    model_used=f"{implementation.value}-{model_name}",
                    success=True
                )
                
            except Exception as e:
                logger.warning(f"Fallback {implementation.value}-{model_name} failed: {e}")
                continue
                
        # All fallbacks failed
        return TranscriptionResult(
            text="",
            processing_time=0,
            rtf=float('inf'),
            memory_usage_mb=0,
            model_used="fallback-failed",
            success=False,
            error_message="All fallback implementations failed"
        )
        
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds"""
        try:
            import soundfile as sf
            with sf.SoundFile(audio_path) as f:
                return len(f) / f.samplerate
        except:
            try:
                import librosa
                y, sr = librosa.load(audio_path, sr=None)
                return len(y) / sr
            except:
                logger.warning(f"Could not determine audio duration for {audio_path}")
                return 1.0  # Default fallback
                
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "config": {
                "implementation": self.config.implementation.value,
                "model_name": self.config.model_name,
                "compute_type": self.config.compute_type,
                "cpu_threads": self.config.cpu_threads,
                "device": self.config.device
            },
            "loaded_models": list(self.models.keys()),
            "cache_dir": self.config.model_cache_dir
        }
        
    def clear_cache(self):
        """Clear model cache to free memory"""
        self.models.clear()
        logger.info("Model cache cleared")

# Factory function for easy instantiation
def create_whisper_processor(
    model_name: str = "distil-small.en",
    compute_type: str = "int8",
    cpu_threads: Optional[int] = None,
    enable_fallback: bool = True
) -> OptimizedWhisperProcessor:
    """
    Create an optimized Whisper processor with recommended settings
    
    Args:
        model_name: Model to use (distil-small.en, base, tiny, etc.)
        compute_type: Quantization type (int8, int4, float16, float32)
        cpu_threads: Number of CPU threads (auto-detected if None)
        enable_fallback: Enable fallback to other models on failure
        
    Returns:
        Configured OptimizedWhisperProcessor
    """
    config = WhisperConfig(
        model_name=model_name,
        compute_type=compute_type,
        cpu_threads=cpu_threads or psutil.cpu_count(logical=False),
        enable_fallback=enable_fallback
    )
    
    return OptimizedWhisperProcessor(config)

# Example usage
if __name__ == "__main__":
    # Create processor with recommended settings for edge hardware
    processor = create_whisper_processor(
        model_name="distil-small.en",
        compute_type="int8",
        enable_fallback=True
    )
    
    # Example transcription (would need actual audio file)
    # result = processor.transcribe("test_audio.wav")
    # print(f"Transcription: {result.text}")
    # print(f"RTF: {result.rtf:.3f}")
    # print(f"Memory: {result.memory_usage_mb:.1f}MB")
    
    print("OptimizedWhisperProcessor initialized successfully")
    print(f"Model info: {processor.get_model_info()}")
