#!/usr/bin/env python3
"""
Model-level optimizations for Kokoro TTS
Implements aggressive model optimizations for maximum performance
"""

import os
import logging
import numpy as np
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ModelOptimizationConfig:
    """Configuration for model optimizations"""
    reduce_mel_bins: bool = True
    target_mel_bins: int = 64  # Reduce from 80 to 64
    max_phoneme_duration: Optional[int] = 510  # Limit phoneme sequence length
    enable_quantization: bool = True
    prefer_q4_model: bool = True
    enable_warm_up: bool = True
    short_text_fast_path: bool = True
    short_text_threshold: int = 20  # Characters
    cache_phonemizer: bool = True
    reduce_precision: bool = False  # Keep quality high
    pipeline_parallelism: bool = True

class ModelOptimizer:
    """Model-level optimizations for maximum performance"""
    
    def __init__(self, config: Optional[ModelOptimizationConfig] = None):
        self.config = config or ModelOptimizationConfig()
        self.warm_up_completed = False
        self.phonemizer_cache = {}
        self.short_text_cache = {}
        
    def optimize_model_loading(self, model_path: str) -> str:
        """Optimize model selection and loading"""
        model_path = Path(model_path)
        
        # Prefer quantized models for speed
        if self.config.prefer_q4_model:
            q4_path = model_path.parent / "model_q4.onnx"
            if q4_path.exists():
                logger.info(f"Using Q4 quantized model for optimal performance: {q4_path}")
                return str(q4_path)
        
        # Fallback to original model
        logger.info(f"Using original model: {model_path}")
        return str(model_path)
    
    def get_optimized_session_options(self) -> Dict[str, Any]:
        """Get ONNX session options optimized for aggressive performance"""
        try:
            import onnxruntime as ort
            
            session_options = ort.SessionOptions()
            
            # Aggressive graph optimizations
            session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            session_options.execution_mode = ort.ExecutionMode.ORT_PARALLEL
            
            # Memory optimizations
            session_options.enable_mem_pattern = True
            session_options.enable_cpu_mem_arena = True
            session_options.enable_mem_reuse = True
            
            # Aggressive performance settings
            session_options.add_session_config_entry("session.use_env_allocators", "1")
            session_options.add_session_config_entry("session.use_deterministic_compute", "0")
            session_options.add_session_config_entry("session.disable_prepacking", "0")
            
            # Intel-specific optimizations
            try:
                from LiteTTS.performance.cpu_optimizer import get_cpu_optimizer
                cpu_optimizer = get_cpu_optimizer()
                
                if "Intel" in cpu_optimizer.cpu_info.model_name:
                    session_options.add_session_config_entry("session.use_intel_optimizations", "1")
                    
                    # AVX optimizations
                    if cpu_optimizer.cpu_info.supports_avx2:
                        session_options.add_session_config_entry("session.use_avx2", "1")
                        
            except ImportError:
                pass
            
            return {"session_options": session_options}
            
        except ImportError:
            logger.warning("ONNX Runtime not available for session optimization")
            return {}
    
    def optimize_phoneme_processing(self, text: str, voice: str) -> Optional[str]:
        """Optimize phoneme processing with caching and fast paths"""
        if not self.config.cache_phonemizer:
            return None
        
        # Check cache first
        cache_key = f"{text}:{voice}"
        if cache_key in self.phonemizer_cache:
            logger.debug(f"Phonemizer cache hit for: {text[:30]}...")
            return self.phonemizer_cache[cache_key]
        
        # Short text fast path
        if self.config.short_text_fast_path and len(text) <= self.config.short_text_threshold:
            if cache_key in self.short_text_cache:
                logger.debug(f"Short text cache hit for: {text}")
                return self.short_text_cache[cache_key]
        
        return None
    
    def cache_phoneme_result(self, text: str, voice: str, phonemes: str):
        """Cache phoneme processing result"""
        if not self.config.cache_phonemizer:
            return
        
        cache_key = f"{text}:{voice}"
        
        # Use different caches for short vs long text
        if len(text) <= self.config.short_text_threshold:
            self.short_text_cache[cache_key] = phonemes
            # Keep short text cache small
            if len(self.short_text_cache) > 100:
                # Remove oldest entries
                keys = list(self.short_text_cache.keys())
                for key in keys[:20]:
                    del self.short_text_cache[key]
        else:
            self.phonemizer_cache[cache_key] = phonemes
            # Keep main cache reasonable size
            if len(self.phonemizer_cache) > 500:
                keys = list(self.phonemizer_cache.keys())
                for key in keys[:100]:
                    del self.phonemizer_cache[key]
    
    def optimize_input_preparation(self, tokens: np.ndarray, voice_data: np.ndarray, 
                                 speed: float) -> Dict[str, np.ndarray]:
        """Optimize model input preparation"""
        # Limit phoneme sequence length for faster processing
        if self.config.max_phoneme_duration and len(tokens) > self.config.max_phoneme_duration:
            logger.warning(f"Truncating phonemes from {len(tokens)} to {self.config.max_phoneme_duration}")
            tokens = tokens[:self.config.max_phoneme_duration]
        
        # Optimize voice vector shape
        if voice_data.shape == (510, 256):
            # Use first style vector for speed
            style_vector = voice_data[0:1, :]
        elif voice_data.shape == (256,):
            style_vector = voice_data.reshape(1, 256)
        elif voice_data.shape == (1, 256):
            style_vector = voice_data
        else:
            if voice_data.size >= 256:
                style_vector = voice_data.flatten()[:256].reshape(1, 256)
            else:
                raise ValueError(f"Voice data too small: {voice_data.shape}")
        
        # Prepare optimized inputs
        inputs = {
            'input_ids': tokens.reshape(1, -1).astype(np.int64),
            'style': style_vector.astype(np.float32),
            'speed': np.array([speed], dtype=np.float32)
        }
        
        return inputs
    
    def warm_up_model(self, model_session, voice_data: np.ndarray):
        """Warm up model with dummy inference to reduce cold start"""
        if self.warm_up_completed or not self.config.enable_warm_up:
            return
        
        try:
            logger.info("Warming up model for optimal performance...")
            
            # Create dummy inputs for warm-up
            dummy_tokens = np.array([0, 1, 2, 3, 0], dtype=np.int64)
            dummy_inputs = self.optimize_input_preparation(dummy_tokens, voice_data, 1.0)
            
            # Run dummy inference
            _ = model_session.run(None, dummy_inputs)
            
            self.warm_up_completed = True
            logger.info("Model warm-up completed")
            
        except Exception as e:
            logger.warning(f"Model warm-up failed: {e}")
    
    def optimize_for_text_length(self, text_length: int) -> Dict[str, Any]:
        """Get optimizations based on text length"""
        optimizations = {}
        
        if text_length <= self.config.short_text_threshold:
            # Short text optimizations
            optimizations.update({
                "use_fast_path": True,
                "reduce_precision": self.config.reduce_precision,
                "skip_advanced_processing": True,
                "priority_cache": True
            })
        elif text_length <= 100:
            # Medium text optimizations
            optimizations.update({
                "use_fast_path": False,
                "reduce_precision": False,
                "skip_advanced_processing": False,
                "priority_cache": True
            })
        else:
            # Long text optimizations
            optimizations.update({
                "use_fast_path": False,
                "reduce_precision": False,
                "skip_advanced_processing": False,
                "priority_cache": False,
                "enable_chunking": True
            })
        
        return optimizations
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            "warm_up_completed": self.warm_up_completed,
            "phonemizer_cache_size": len(self.phonemizer_cache),
            "short_text_cache_size": len(self.short_text_cache),
            "config": {
                "reduce_mel_bins": self.config.reduce_mel_bins,
                "target_mel_bins": self.config.target_mel_bins,
                "max_phoneme_duration": self.config.max_phoneme_duration,
                "short_text_threshold": self.config.short_text_threshold,
                "cache_phonemizer": self.config.cache_phonemizer
            }
        }

# Global model optimizer instance
_model_optimizer = None

def get_model_optimizer() -> ModelOptimizer:
    """Get global model optimizer instance"""
    global _model_optimizer
    if _model_optimizer is None:
        _model_optimizer = ModelOptimizer()
    return _model_optimizer
