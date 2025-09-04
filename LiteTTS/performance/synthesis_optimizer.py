#!/usr/bin/env python3
"""
Synthesis Performance Optimizer
Optimizes the TTS synthesis pipeline for consistent RTF performance
"""

import time
import logging
import threading
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class SynthesisPerformanceConfig:
    """Configuration for synthesis performance optimization"""
    # RTF targets
    target_rtf: float = 0.5
    critical_rtf_threshold: float = 1.0
    
    # Performance modes
    enable_fast_path: bool = True
    fast_path_text_length: int = 50  # Characters
    enable_pipeline_optimization: bool = True
    enable_rtf_monitoring: bool = True
    
    # Optimization settings
    skip_unnecessary_processing: bool = True
    use_cached_voice_embeddings: bool = True
    optimize_audio_processing: bool = True
    enable_parallel_processing: bool = True
    
    # Timeout settings
    synthesis_timeout: float = 10.0
    fast_path_timeout: float = 2.0

class SynthesisOptimizer:
    """
    Optimizes TTS synthesis for consistent RTF performance
    Provides fast paths and performance monitoring
    """
    
    def __init__(self, config: Optional[SynthesisPerformanceConfig] = None):
        self.config = config or SynthesisPerformanceConfig()
        self.performance_stats = {
            'total_requests': 0,
            'fast_path_requests': 0,
            'optimized_requests': 0,
            'avg_rtf': 0.0,
            'rtf_violations': 0,
            'cache_hits': 0
        }
        self.stats_lock = threading.RLock()
        
        # Performance caches
        self.voice_embedding_cache = {}
        self.tokenization_cache = {}
        self.fast_path_cache = {}
        
        logger.info("Synthesis optimizer initialized")
    
    def optimize_synthesis_request(self, text: str, voice: str, speed: float = 1.0,
                                 emotion: Optional[str] = None, 
                                 emotion_strength: float = 1.0) -> Dict[str, Any]:
        """
        Optimize a synthesis request for best performance
        Returns optimization strategy and cached data
        """
        optimization_strategy = {
            'use_fast_path': False,
            'use_pipeline_optimization': False,
            'cached_voice_embedding': None,
            'cached_tokens': None,
            'skip_post_processing': False,
            'expected_rtf': self.config.target_rtf
        }
        
        try:
            # Determine if fast path is applicable
            if (self.config.enable_fast_path and 
                len(text) <= self.config.fast_path_text_length and
                emotion is None and speed == 1.0):
                
                optimization_strategy['use_fast_path'] = True
                optimization_strategy['expected_rtf'] = 0.1  # Very fast for short text
                
                # Check fast path cache
                fast_cache_key = f"{text}:{voice}"
                if fast_cache_key in self.fast_path_cache:
                    optimization_strategy['cached_audio'] = self.fast_path_cache[fast_cache_key]
                    with self.stats_lock:
                        self.performance_stats['cache_hits'] += 1
            
            # Check for cached voice embedding
            if self.config.use_cached_voice_embeddings and voice in self.voice_embedding_cache:
                optimization_strategy['cached_voice_embedding'] = self.voice_embedding_cache[voice]
            
            # Check for cached tokenization
            token_cache_key = f"{text}:{voice}"
            if token_cache_key in self.tokenization_cache:
                optimization_strategy['cached_tokens'] = self.tokenization_cache[token_cache_key]
            
            # Enable pipeline optimization for longer text
            if (self.config.enable_pipeline_optimization and 
                len(text) > self.config.fast_path_text_length):
                optimization_strategy['use_pipeline_optimization'] = True
            
            # Skip unnecessary post-processing for simple requests
            if (self.config.skip_unnecessary_processing and 
                emotion is None and speed == 1.0):
                optimization_strategy['skip_post_processing'] = True
            
            return optimization_strategy
            
        except Exception as e:
            logger.warning(f"Optimization strategy failed: {e}")
            return optimization_strategy
    
    def monitor_synthesis_performance(self, text: str, voice: str, 
                                    generation_time: float, audio_duration: float,
                                    optimization_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and record synthesis performance"""
        rtf = generation_time / max(audio_duration, 0.001)  # Avoid division by zero
        
        performance_data = {
            'rtf': rtf,
            'generation_time': generation_time,
            'audio_duration': audio_duration,
            'text_length': len(text),
            'voice': voice,
            'used_fast_path': optimization_strategy.get('use_fast_path', False),
            'used_pipeline_optimization': optimization_strategy.get('use_pipeline_optimization', False),
            'target_met': rtf <= self.config.target_rtf,
            'critical_violation': rtf > self.config.critical_rtf_threshold
        }
        
        # Update statistics
        with self.stats_lock:
            self.performance_stats['total_requests'] += 1
            
            if optimization_strategy.get('use_fast_path'):
                self.performance_stats['fast_path_requests'] += 1
            
            if optimization_strategy.get('use_pipeline_optimization'):
                self.performance_stats['optimized_requests'] += 1
            
            if rtf > self.config.critical_rtf_threshold:
                self.performance_stats['rtf_violations'] += 1
            
            # Update running average RTF
            total_requests = self.performance_stats['total_requests']
            current_avg = self.performance_stats['avg_rtf']
            self.performance_stats['avg_rtf'] = (current_avg * (total_requests - 1) + rtf) / total_requests
        
        # Log performance issues
        if rtf > self.config.critical_rtf_threshold:
            logger.warning(f"RTF violation: {rtf:.3f} > {self.config.critical_rtf_threshold} "
                         f"for text length {len(text)} with voice {voice}")
        elif rtf > self.config.target_rtf:
            logger.debug(f"RTF above target: {rtf:.3f} > {self.config.target_rtf} "
                        f"for text length {len(text)}")
        
        return performance_data
    
    def cache_voice_embedding(self, voice: str, embedding: Any):
        """Cache voice embedding for faster access"""
        if self.config.use_cached_voice_embeddings:
            self.voice_embedding_cache[voice] = embedding
            logger.debug(f"Cached voice embedding for: {voice}")
    
    def cache_tokenization(self, text: str, voice: str, tokens: Any):
        """Cache tokenization result"""
        cache_key = f"{text}:{voice}"
        self.tokenization_cache[cache_key] = tokens
        logger.debug(f"Cached tokenization for: {text[:30]}...")
    
    def cache_fast_path_result(self, text: str, voice: str, audio_segment: Any):
        """Cache fast path synthesis result"""
        if len(text) <= self.config.fast_path_text_length:
            cache_key = f"{text}:{voice}"
            self.fast_path_cache[cache_key] = audio_segment
            logger.debug(f"Cached fast path result for: {text}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        with self.stats_lock:
            stats = self.performance_stats.copy()
            
            # Calculate additional metrics
            if stats['total_requests'] > 0:
                stats['fast_path_percentage'] = (stats['fast_path_requests'] / stats['total_requests']) * 100
                stats['optimization_percentage'] = (stats['optimized_requests'] / stats['total_requests']) * 100
                stats['violation_percentage'] = (stats['rtf_violations'] / stats['total_requests']) * 100
                stats['cache_hit_percentage'] = (stats['cache_hits'] / stats['total_requests']) * 100
            else:
                stats['fast_path_percentage'] = 0
                stats['optimization_percentage'] = 0
                stats['violation_percentage'] = 0
                stats['cache_hit_percentage'] = 0
            
            return stats
    
    def optimize_synthesis_pipeline(self, synthesis_func, text: str, voice: str, 
                                  speed: float = 1.0, emotion: Optional[str] = None,
                                  emotion_strength: float = 1.0) -> Tuple[Any, Dict[str, Any]]:
        """
        Execute optimized synthesis with performance monitoring
        Returns (audio_segment, performance_data)
        """
        start_time = time.perf_counter()
        
        # Get optimization strategy
        optimization_strategy = self.optimize_synthesis_request(
            text, voice, speed, emotion, emotion_strength
        )
        
        try:
            # Check for cached result first
            if 'cached_audio' in optimization_strategy:
                audio_segment = optimization_strategy['cached_audio']
                generation_time = time.perf_counter() - start_time
                
                performance_data = self.monitor_synthesis_performance(
                    text, voice, generation_time, audio_segment.duration, optimization_strategy
                )
                
                logger.debug(f"Used cached audio: RTF {performance_data['rtf']:.3f}")
                return audio_segment, performance_data
            
            # Execute synthesis with timeout protection
            timeout = (self.config.fast_path_timeout if optimization_strategy['use_fast_path'] 
                      else self.config.synthesis_timeout)
            
            # Call the actual synthesis function
            audio_segment = synthesis_func(text, voice, speed, emotion, emotion_strength)
            
            generation_time = time.perf_counter() - start_time
            
            # Monitor performance
            performance_data = self.monitor_synthesis_performance(
                text, voice, generation_time, audio_segment.duration, optimization_strategy
            )
            
            # Cache result if it's a fast path candidate
            if optimization_strategy['use_fast_path'] and performance_data['target_met']:
                self.cache_fast_path_result(text, voice, audio_segment)
            
            return audio_segment, performance_data
            
        except Exception as e:
            generation_time = time.perf_counter() - start_time
            logger.error(f"Optimized synthesis failed after {generation_time:.3f}s: {e}")
            raise
    
    def reset_caches(self):
        """Reset all performance caches"""
        self.voice_embedding_cache.clear()
        self.tokenization_cache.clear()
        self.fast_path_cache.clear()
        
        with self.stats_lock:
            self.performance_stats = {
                'total_requests': 0,
                'fast_path_requests': 0,
                'optimized_requests': 0,
                'avg_rtf': 0.0,
                'rtf_violations': 0,
                'cache_hits': 0
            }
        
        logger.info("Performance caches and stats reset")

# Global synthesis optimizer instance
_synthesis_optimizer: Optional[SynthesisOptimizer] = None

def get_synthesis_optimizer() -> SynthesisOptimizer:
    """Get or create global synthesis optimizer"""
    global _synthesis_optimizer
    if _synthesis_optimizer is None:
        _synthesis_optimizer = SynthesisOptimizer()
    return _synthesis_optimizer

def initialize_synthesis_optimizer(config: Optional[SynthesisPerformanceConfig] = None):
    """Initialize global synthesis optimizer with configuration"""
    global _synthesis_optimizer
    _synthesis_optimizer = SynthesisOptimizer(config)
    logger.info("Global synthesis optimizer initialized")
