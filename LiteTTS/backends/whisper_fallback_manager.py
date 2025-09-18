#!/usr/bin/env python3
"""
Whisper Fallback Manager for LiteTTS
Implements comprehensive fallback mechanisms with multi-tier support and intelligent error handling
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from .whisper_optimized import OptimizedWhisperProcessor, WhisperConfig, WhisperImplementation, TranscriptionResult
    from ..config.whisper_config_loader import get_whisper_config
except ImportError:
    # Handle direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from backends.whisper_optimized import OptimizedWhisperProcessor, WhisperConfig, WhisperImplementation, TranscriptionResult
    from LiteTTS.config.whisper_config_loader import get_whisper_config

logger = logging.getLogger(__name__)

class FallbackTrigger(Enum):
    """Reasons for triggering fallback"""
    RTF_EXCEEDED = "rtf_exceeded"
    MEMORY_EXCEEDED = "memory_exceeded"
    ERROR_OCCURRED = "error_occurred"
    TIMEOUT = "timeout"
    MODEL_UNAVAILABLE = "model_unavailable"

@dataclass
class FallbackAttempt:
    """Record of a fallback attempt"""
    trigger: FallbackTrigger
    original_config: Dict[str, Any]
    fallback_config: Dict[str, Any]
    success: bool
    processing_time: float
    error_message: Optional[str] = None

class WhisperFallbackManager:
    """
    Manages fallback strategies for Whisper implementations with intelligent decision making
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_loader = get_whisper_config(config_file)
        self.settings = self.config_loader.get_settings()
        self.fallback_chain = self.config_loader.get_fallback_chain()
        
        # Fallback statistics
        self.fallback_attempts = []
        self.success_rates = {}
        self.performance_history = {}
        
        # Primary processor
        self.primary_processor = None
        self.fallback_processors = {}
        
        logger.info("WhisperFallbackManager initialized")
        
    def transcribe_with_fallback(self, audio_path: str, audio_duration: Optional[float] = None) -> TranscriptionResult:
        """
        Transcribe audio with comprehensive fallback support
        
        Args:
            audio_path: Path to audio file
            audio_duration: Duration of audio in seconds
            
        Returns:
            TranscriptionResult with fallback information
        """
        # Try primary processor first
        primary_result = self._try_primary_processor(audio_path, audio_duration)
        
        if primary_result.success and self._meets_performance_criteria(primary_result):
            return primary_result
            
        # Determine fallback trigger
        trigger = self._determine_fallback_trigger(primary_result)
        
        logger.warning(f"Primary processor failed or underperformed, trigger: {trigger.value}")
        
        # Try fallback chain
        for i, fallback_config in enumerate(self.fallback_chain):
            try:
                logger.info(f"Attempting fallback {i+1}/{len(self.fallback_chain)}: {fallback_config}")
                
                fallback_result = self._try_fallback_processor(
                    audio_path, 
                    audio_duration, 
                    fallback_config,
                    trigger
                )
                
                if fallback_result.success and self._meets_performance_criteria(fallback_result):
                    # Record successful fallback
                    self._record_fallback_attempt(
                        trigger, 
                        self._get_primary_config(), 
                        fallback_config, 
                        True, 
                        fallback_result.processing_time
                    )
                    
                    # Update model name to indicate fallback was used
                    fallback_result.model_used = f"fallback-{fallback_result.model_used}"
                    
                    logger.info(f"Fallback successful: {fallback_result.model_used}")
                    return fallback_result
                    
            except Exception as e:
                logger.warning(f"Fallback {i+1} failed: {e}")
                self._record_fallback_attempt(
                    trigger,
                    self._get_primary_config(),
                    fallback_config,
                    False,
                    0,
                    str(e)
                )
                continue
                
        # All fallbacks failed
        logger.error("All fallback attempts failed")
        
        # Return the best result we got (primary or last fallback attempt)
        if primary_result.success:
            primary_result.model_used = f"degraded-{primary_result.model_used}"
            return primary_result
        else:
            return TranscriptionResult(
                text="",
                processing_time=0,
                rtf=float('inf'),
                memory_usage_mb=0,
                model_used="all-fallbacks-failed",
                success=False,
                error_message="All transcription attempts failed"
            )
            
    def _try_primary_processor(self, audio_path: str, audio_duration: Optional[float]) -> TranscriptionResult:
        """Try the primary Whisper processor"""
        if self.primary_processor is None:
            primary_config = WhisperConfig(
                implementation=WhisperImplementation.FASTER_WHISPER,
                model_name=self.settings.default_model,
                compute_type=self.settings.quantization,
                cpu_threads=self.settings.cpu_threads,
                device=self.settings.device,
                enable_fallback=False  # We handle fallback here
            )
            self.primary_processor = OptimizedWhisperProcessor(primary_config)
            
        return self.primary_processor.transcribe(audio_path, audio_duration)
        
    def _try_fallback_processor(self, audio_path: str, audio_duration: Optional[float], 
                               fallback_config: Dict[str, Any], trigger: FallbackTrigger) -> TranscriptionResult:
        """Try a specific fallback processor configuration"""
        
        # Create processor key for caching
        processor_key = f"{fallback_config['implementation']}_{fallback_config['model']}_{fallback_config.get('compute_type', 'default')}"
        
        if processor_key not in self.fallback_processors:
            # Map implementation string to enum
            implementation_map = {
                "faster-whisper": WhisperImplementation.FASTER_WHISPER,
                "openai-whisper": WhisperImplementation.OPENAI_WHISPER,
                "distil-whisper": WhisperImplementation.DISTIL_WHISPER
            }
            
            implementation = implementation_map.get(
                fallback_config['implementation'], 
                WhisperImplementation.FASTER_WHISPER
            )
            
            config = WhisperConfig(
                implementation=implementation,
                model_name=fallback_config['model'],
                compute_type=fallback_config.get('compute_type', 'int8'),
                cpu_threads=self.settings.cpu_threads,
                device=self.settings.device,
                enable_fallback=False
            )
            
            self.fallback_processors[processor_key] = OptimizedWhisperProcessor(config)
            
        processor = self.fallback_processors[processor_key]
        return processor.transcribe(audio_path, audio_duration)
        
    def _meets_performance_criteria(self, result: TranscriptionResult) -> bool:
        """Check if result meets performance criteria"""
        if not result.success:
            return False
            
        # Check RTF threshold
        if result.rtf > self.settings.rtf_threshold:
            logger.debug(f"RTF {result.rtf:.3f} exceeds threshold {self.settings.rtf_threshold}")
            return False
            
        # Check memory threshold
        if result.memory_usage_mb > self.settings.memory_threshold_mb:
            logger.debug(f"Memory {result.memory_usage_mb:.1f}MB exceeds threshold {self.settings.memory_threshold_mb}MB")
            return False
            
        return True
        
    def _determine_fallback_trigger(self, result: TranscriptionResult) -> FallbackTrigger:
        """Determine why fallback is needed"""
        if not result.success:
            if "timeout" in (result.error_message or "").lower():
                return FallbackTrigger.TIMEOUT
            elif "memory" in (result.error_message or "").lower():
                return FallbackTrigger.MEMORY_EXCEEDED
            elif "model" in (result.error_message or "").lower():
                return FallbackTrigger.MODEL_UNAVAILABLE
            else:
                return FallbackTrigger.ERROR_OCCURRED
                
        if result.rtf > self.settings.rtf_threshold:
            return FallbackTrigger.RTF_EXCEEDED
            
        if result.memory_usage_mb > self.settings.memory_threshold_mb:
            return FallbackTrigger.MEMORY_EXCEEDED
            
        return FallbackTrigger.ERROR_OCCURRED
        
    def _get_primary_config(self) -> Dict[str, Any]:
        """Get primary processor configuration"""
        return {
            "implementation": "faster-whisper",
            "model": self.settings.default_model,
            "compute_type": self.settings.quantization
        }
        
    def _record_fallback_attempt(self, trigger: FallbackTrigger, original_config: Dict[str, Any],
                                fallback_config: Dict[str, Any], success: bool, 
                                processing_time: float, error_message: Optional[str] = None):
        """Record fallback attempt for analysis"""
        attempt = FallbackAttempt(
            trigger=trigger,
            original_config=original_config,
            fallback_config=fallback_config,
            success=success,
            processing_time=processing_time,
            error_message=error_message
        )
        
        self.fallback_attempts.append(attempt)
        
        # Update success rates
        config_key = f"{fallback_config['implementation']}_{fallback_config['model']}"
        if config_key not in self.success_rates:
            self.success_rates[config_key] = {"attempts": 0, "successes": 0}
            
        self.success_rates[config_key]["attempts"] += 1
        if success:
            self.success_rates[config_key]["successes"] += 1
            
        # Limit history size
        if len(self.fallback_attempts) > 1000:
            self.fallback_attempts = self.fallback_attempts[-500:]
            
    def get_fallback_statistics(self) -> Dict[str, Any]:
        """Get fallback usage statistics"""
        if not self.fallback_attempts:
            return {"total_attempts": 0, "success_rate": 0.0, "common_triggers": []}
            
        total_attempts = len(self.fallback_attempts)
        successful_attempts = sum(1 for attempt in self.fallback_attempts if attempt.success)
        
        # Count triggers
        trigger_counts = {}
        for attempt in self.fallback_attempts:
            trigger = attempt.trigger.value
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
            
        # Sort triggers by frequency
        common_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_attempts": total_attempts,
            "successful_attempts": successful_attempts,
            "success_rate": successful_attempts / total_attempts if total_attempts > 0 else 0.0,
            "common_triggers": common_triggers,
            "model_success_rates": {
                model: {
                    "success_rate": stats["successes"] / stats["attempts"] if stats["attempts"] > 0 else 0.0,
                    "attempts": stats["attempts"]
                }
                for model, stats in self.success_rates.items()
            }
        }
        
    def optimize_fallback_chain(self):
        """Optimize fallback chain based on historical performance"""
        if len(self.fallback_attempts) < 10:
            logger.info("Insufficient data for fallback optimization")
            return
            
        # Analyze success rates and performance
        model_performance = {}
        
        for attempt in self.fallback_attempts:
            if attempt.success:
                config_key = f"{attempt.fallback_config['implementation']}_{attempt.fallback_config['model']}"
                
                if config_key not in model_performance:
                    model_performance[config_key] = {
                        "times": [],
                        "successes": 0,
                        "attempts": 0
                    }
                    
                model_performance[config_key]["times"].append(attempt.processing_time)
                model_performance[config_key]["successes"] += 1
                
            # Count all attempts
            config_key = f"{attempt.fallback_config['implementation']}_{attempt.fallback_config['model']}"
            if config_key in model_performance:
                model_performance[config_key]["attempts"] += 1
                
        # Sort by success rate and average processing time
        optimized_order = []
        for config_key, perf in model_performance.items():
            if perf["attempts"] > 0:
                success_rate = perf["successes"] / perf["attempts"]
                avg_time = sum(perf["times"]) / len(perf["times"]) if perf["times"] else float('inf')
                
                # Score combines success rate and speed (lower time is better)
                score = success_rate * (1.0 / (avg_time + 0.1))  # Add small constant to avoid division by zero
                
                optimized_order.append((config_key, score, success_rate, avg_time))
                
        # Sort by score (higher is better)
        optimized_order.sort(key=lambda x: x[1], reverse=True)
        
        logger.info("Fallback optimization analysis:")
        for config_key, score, success_rate, avg_time in optimized_order[:5]:
            logger.info(f"  {config_key}: score={score:.3f}, success_rate={success_rate:.3f}, avg_time={avg_time:.2f}s")
            
    def clear_cache(self):
        """Clear processor cache to free memory"""
        if self.primary_processor:
            self.primary_processor.clear_cache()
            
        for processor in self.fallback_processors.values():
            processor.clear_cache()
            
        self.fallback_processors.clear()
        logger.info("Fallback manager cache cleared")

# Global fallback manager instance
_fallback_manager = None

def get_fallback_manager(config_file: Optional[str] = None) -> WhisperFallbackManager:
    """Get the global fallback manager instance"""
    global _fallback_manager
    
    if _fallback_manager is None:
        _fallback_manager = WhisperFallbackManager(config_file)
        
    return _fallback_manager

# Convenience function for easy transcription with fallback
def transcribe_with_fallback(audio_path: str, audio_duration: Optional[float] = None) -> TranscriptionResult:
    """
    Transcribe audio with automatic fallback support
    
    Args:
        audio_path: Path to audio file
        audio_duration: Duration of audio in seconds
        
    Returns:
        TranscriptionResult with fallback information
    """
    manager = get_fallback_manager()
    return manager.transcribe_with_fallback(audio_path, audio_duration)

# Example usage
if __name__ == "__main__":
    # Create fallback manager
    manager = WhisperFallbackManager()
    
    # Example transcription (would need actual audio file)
    # result = manager.transcribe_with_fallback("test_audio.wav")
    # print(f"Transcription: {result.text}")
    # print(f"Model used: {result.model_used}")
    # print(f"RTF: {result.rtf:.3f}")
    
    # Get statistics
    stats = manager.get_fallback_statistics()
    print(f"Fallback statistics: {stats}")
    
    print("WhisperFallbackManager initialized successfully")
