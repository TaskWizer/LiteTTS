"""
Audio Processing Optimizations for RTF Improvement
"""

import numpy as np
import torch
from typing import Optional, Tuple
import time

class OptimizedAudioProcessor:
    """Optimized audio processor with RTF improvements"""
    
    def __init__(self):
        self.audio_cache = {}
        self.processing_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'avg_processing_time': 0.0
        }
    
    def process_audio_optimized(self, audio_data: np.ndarray, 
                              sample_rate: int = 24000,
                              optimize_for_rtf: bool = True) -> np.ndarray:
        """
        Process audio with RTF optimizations
        
        Args:
            audio_data: Raw audio data
            sample_rate: Audio sample rate
            optimize_for_rtf: Enable RTF optimizations
            
        Returns:
            Processed audio data
        """
        start_time = time.time()
        
        try:
            # 1. Fast normalization using vectorized operations
            if optimize_for_rtf:
                audio_data = self._fast_normalize(audio_data)
            
            # 2. Efficient resampling if needed
            if sample_rate != 24000:
                audio_data = self._efficient_resample(audio_data, sample_rate, 24000)
            
            # 3. Apply minimal necessary processing
            audio_data = self._minimal_processing(audio_data)
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time)
            
            return audio_data
            
        except Exception as e:
            print(f"Audio processing error: {e}")
            return audio_data
    
    def _fast_normalize(self, audio: np.ndarray) -> np.ndarray:
        """Fast audio normalization using numpy vectorization"""
        if len(audio) == 0:
            return audio
        
        # Use numpy's built-in functions for speed
        max_val = np.abs(audio).max()
        if max_val > 0:
            return audio / max_val * 0.95
        return audio
    
    def _efficient_resample(self, audio: np.ndarray, 
                          source_rate: int, target_rate: int) -> np.ndarray:
        """Efficient resampling with minimal quality loss"""
        if source_rate == target_rate:
            return audio
        
        # Use simple linear interpolation for speed
        ratio = target_rate / source_rate
        new_length = int(len(audio) * ratio)
        
        # Fast resampling using numpy interpolation
        old_indices = np.linspace(0, len(audio) - 1, new_length)
        return np.interp(old_indices, np.arange(len(audio)), audio)
    
    def _minimal_processing(self, audio: np.ndarray) -> np.ndarray:
        """Apply only essential audio processing"""
        # Remove DC offset efficiently
        audio = audio - np.mean(audio)
        
        # Simple high-pass filter to remove low-frequency noise
        if len(audio) > 1:
            audio[1:] = audio[1:] - 0.95 * audio[:-1]
        
        return audio
    
    def _update_processing_stats(self, processing_time: float):
        """Update processing statistics"""
        self.processing_stats['total_requests'] += 1
        
        # Running average of processing time
        total = self.processing_stats['total_requests']
        current_avg = self.processing_stats['avg_processing_time']
        self.processing_stats['avg_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    def get_performance_stats(self) -> dict:
        """Get current performance statistics"""
        return self.processing_stats.copy()

# Global instance for reuse
_audio_processor = OptimizedAudioProcessor()

def get_optimized_audio_processor():
    """Get the global optimized audio processor instance"""
    return _audio_processor
