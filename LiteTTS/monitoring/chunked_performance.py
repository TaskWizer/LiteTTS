#!/usr/bin/env python3
"""
Performance Monitoring for Chunked Audio Generation
Tracks and compares performance metrics between chunked and non-chunked generation
"""

import time
import logging
import statistics
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class GenerationType(Enum):
    """Types of audio generation"""
    STANDARD = "standard"
    CHUNKED = "chunked"
    STREAMING = "streaming"

@dataclass
class PerformanceMetrics:
    """Performance metrics for a single generation"""
    generation_id: str
    generation_type: GenerationType
    text_length: int
    voice_id: str
    
    # Timing metrics
    total_time: float
    synthesis_time: float
    processing_time: float

    # Quality metrics
    audio_size: int
    estimated_duration: float
    rtf: float  # Real-time factor

    # Optional timing metrics
    first_chunk_time: Optional[float] = None
    
    # Chunking metrics (for chunked generation)
    chunk_count: Optional[int] = None
    avg_chunk_time: Optional[float] = None
    chunk_times: Optional[List[float]] = None
    
    # Resource metrics
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    
    # User experience metrics
    time_to_first_audio: float = 0.0
    perceived_latency: float = 0.0
    
    timestamp: float = field(default_factory=time.time)

@dataclass
class ComparisonReport:
    """Comparison report between generation types"""
    standard_metrics: List[PerformanceMetrics]
    chunked_metrics: List[PerformanceMetrics]
    streaming_metrics: List[PerformanceMetrics]
    
    # Aggregated comparisons
    avg_rtf_comparison: Dict[str, float]
    avg_latency_comparison: Dict[str, float]
    avg_memory_comparison: Dict[str, float]
    
    # User experience comparison
    time_to_first_audio_comparison: Dict[str, float]
    perceived_responsiveness: Dict[str, float]
    
    generation_time: float = field(default_factory=time.time)

class ChunkedPerformanceMonitor:
    """Performance monitoring system for chunked audio generation"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.active_generations = {}
        
        # Performance aggregations
        self.metrics_by_type = defaultdict(list)
        self.metrics_by_voice = defaultdict(list)
        self.metrics_by_text_length = defaultdict(list)
        
        # Real-time statistics
        self.current_stats = {
            "total_generations": 0,
            "chunked_generations": 0,
            "standard_generations": 0,
            "streaming_generations": 0,
            "avg_rtf_last_100": 0.0,
            "avg_latency_last_100": 0.0
        }
        
        logger.info("ChunkedPerformanceMonitor initialized")
    
    def start_generation_tracking(
        self, 
        generation_id: str, 
        generation_type: GenerationType,
        text: str,
        voice_id: str,
        chunk_count: Optional[int] = None
    ) -> str:
        """
        Start tracking a generation
        
        Args:
            generation_id: Unique generation identifier
            generation_type: Type of generation
            text: Input text
            voice_id: Voice being used
            chunk_count: Number of chunks (for chunked generation)
            
        Returns:
            Generation ID
        """
        start_time = time.time()
        
        tracking_info = {
            "generation_id": generation_id,
            "generation_type": generation_type,
            "text": text,
            "text_length": len(text),
            "voice_id": voice_id,
            "chunk_count": chunk_count,
            "start_time": start_time,
            "chunk_times": [],
            "first_chunk_time": None,
            "memory_snapshots": [],
            "cpu_snapshots": []
        }
        
        self.active_generations[generation_id] = tracking_info
        
        logger.debug(f"Started tracking generation {generation_id} ({generation_type.value})")
        return generation_id
    
    def record_chunk_completion(
        self, 
        generation_id: str, 
        chunk_id: int, 
        chunk_time: float,
        audio_size: int
    ):
        """Record completion of a chunk"""
        if generation_id not in self.active_generations:
            logger.warning(f"Generation {generation_id} not found for chunk recording")
            return
        
        tracking_info = self.active_generations[generation_id]
        tracking_info["chunk_times"].append(chunk_time)
        
        # Record first chunk time for latency measurement
        if tracking_info["first_chunk_time"] is None:
            tracking_info["first_chunk_time"] = time.time() - tracking_info["start_time"]
        
        logger.debug(f"Recorded chunk {chunk_id} completion for generation {generation_id}")
    
    def record_resource_usage(self, generation_id: str, memory_mb: float, cpu_percent: float):
        """Record resource usage snapshot"""
        if generation_id not in self.active_generations:
            return
        
        tracking_info = self.active_generations[generation_id]
        tracking_info["memory_snapshots"].append(memory_mb)
        tracking_info["cpu_snapshots"].append(cpu_percent)
    
    def complete_generation_tracking(
        self, 
        generation_id: str, 
        audio_size: int,
        estimated_duration: float
    ) -> PerformanceMetrics:
        """
        Complete tracking and calculate metrics
        
        Args:
            generation_id: Generation to complete
            audio_size: Size of generated audio in bytes
            estimated_duration: Estimated audio duration in seconds
            
        Returns:
            PerformanceMetrics object
        """
        if generation_id not in self.active_generations:
            raise ValueError(f"Generation {generation_id} not found")
        
        tracking_info = self.active_generations[generation_id]
        end_time = time.time()
        
        # Calculate timing metrics
        total_time = end_time - tracking_info["start_time"]
        synthesis_time = sum(tracking_info["chunk_times"]) if tracking_info["chunk_times"] else total_time
        processing_time = total_time - synthesis_time
        
        # Calculate RTF (Real-Time Factor)
        rtf = total_time / max(estimated_duration, 0.1)
        
        # Calculate chunk metrics
        chunk_count = tracking_info.get("chunk_count")
        avg_chunk_time = None
        if tracking_info["chunk_times"]:
            avg_chunk_time = statistics.mean(tracking_info["chunk_times"])
        
        # Calculate resource metrics
        memory_usage = None
        cpu_usage = None
        if tracking_info["memory_snapshots"]:
            memory_usage = statistics.mean(tracking_info["memory_snapshots"])
        if tracking_info["cpu_snapshots"]:
            cpu_usage = statistics.mean(tracking_info["cpu_snapshots"])
        
        # Calculate user experience metrics
        time_to_first_audio = tracking_info.get("first_chunk_time", total_time)
        perceived_latency = self._calculate_perceived_latency(
            tracking_info["generation_type"], 
            time_to_first_audio, 
            total_time
        )
        
        # Create metrics object
        metrics = PerformanceMetrics(
            generation_id=generation_id,
            generation_type=tracking_info["generation_type"],
            text_length=tracking_info["text_length"],
            voice_id=tracking_info["voice_id"],
            total_time=total_time,
            synthesis_time=synthesis_time,
            processing_time=processing_time,
            first_chunk_time=tracking_info.get("first_chunk_time"),
            audio_size=audio_size,
            estimated_duration=estimated_duration,
            rtf=rtf,
            chunk_count=chunk_count,
            avg_chunk_time=avg_chunk_time,
            chunk_times=tracking_info["chunk_times"].copy() if tracking_info["chunk_times"] else None,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            time_to_first_audio=time_to_first_audio,
            perceived_latency=perceived_latency
        )
        
        # Store metrics
        self.metrics_history.append(metrics)
        self.metrics_by_type[tracking_info["generation_type"]].append(metrics)
        self.metrics_by_voice[tracking_info["voice_id"]].append(metrics)
        
        # Categorize by text length
        text_length_category = self._categorize_text_length(tracking_info["text_length"])
        self.metrics_by_text_length[text_length_category].append(metrics)
        
        # Update real-time statistics
        self._update_current_stats(metrics)
        
        # Cleanup
        del self.active_generations[generation_id]
        
        logger.info(f"Completed tracking for generation {generation_id}: RTF={rtf:.3f}, Latency={time_to_first_audio:.3f}s")
        return metrics
    
    def get_performance_comparison(
        self, 
        time_window_hours: Optional[float] = None
    ) -> ComparisonReport:
        """
        Generate performance comparison report
        
        Args:
            time_window_hours: Time window for analysis (None for all data)
            
        Returns:
            ComparisonReport with detailed comparisons
        """
        # Filter metrics by time window if specified
        if time_window_hours:
            cutoff_time = time.time() - (time_window_hours * 3600)
            filtered_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        else:
            filtered_metrics = list(self.metrics_history)
        
        # Separate by generation type
        standard_metrics = [m for m in filtered_metrics if m.generation_type == GenerationType.STANDARD]
        chunked_metrics = [m for m in filtered_metrics if m.generation_type == GenerationType.CHUNKED]
        streaming_metrics = [m for m in filtered_metrics if m.generation_type == GenerationType.STREAMING]
        
        # Calculate comparisons
        avg_rtf_comparison = self._calculate_avg_comparison(
            [standard_metrics, chunked_metrics, streaming_metrics],
            ["standard", "chunked", "streaming"],
            lambda m: m.rtf
        )
        
        avg_latency_comparison = self._calculate_avg_comparison(
            [standard_metrics, chunked_metrics, streaming_metrics],
            ["standard", "chunked", "streaming"],
            lambda m: m.time_to_first_audio
        )
        
        avg_memory_comparison = self._calculate_avg_comparison(
            [standard_metrics, chunked_metrics, streaming_metrics],
            ["standard", "chunked", "streaming"],
            lambda m: m.memory_usage or 0
        )
        
        time_to_first_audio_comparison = self._calculate_avg_comparison(
            [standard_metrics, chunked_metrics, streaming_metrics],
            ["standard", "chunked", "streaming"],
            lambda m: m.time_to_first_audio
        )
        
        perceived_responsiveness = self._calculate_avg_comparison(
            [standard_metrics, chunked_metrics, streaming_metrics],
            ["standard", "chunked", "streaming"],
            lambda m: 1.0 / max(m.perceived_latency, 0.1)  # Inverse of perceived latency
        )
        
        return ComparisonReport(
            standard_metrics=standard_metrics,
            chunked_metrics=chunked_metrics,
            streaming_metrics=streaming_metrics,
            avg_rtf_comparison=avg_rtf_comparison,
            avg_latency_comparison=avg_latency_comparison,
            avg_memory_comparison=avg_memory_comparison,
            time_to_first_audio_comparison=time_to_first_audio_comparison,
            perceived_responsiveness=perceived_responsiveness
        )
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time performance statistics"""
        return self.current_stats.copy()
    
    def get_metrics_by_voice(self, voice_id: str) -> List[PerformanceMetrics]:
        """Get metrics for a specific voice"""
        return self.metrics_by_voice.get(voice_id, [])
    
    def get_metrics_by_text_length(self, category: str) -> List[PerformanceMetrics]:
        """Get metrics by text length category"""
        return self.metrics_by_text_length.get(category, [])
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        export_data = {
            "metrics": [
                {
                    "generation_id": m.generation_id,
                    "generation_type": m.generation_type.value,
                    "text_length": m.text_length,
                    "voice_id": m.voice_id,
                    "total_time": m.total_time,
                    "rtf": m.rtf,
                    "time_to_first_audio": m.time_to_first_audio,
                    "perceived_latency": m.perceived_latency,
                    "chunk_count": m.chunk_count,
                    "timestamp": m.timestamp
                }
                for m in self.metrics_history
            ],
            "current_stats": self.current_stats,
            "export_time": time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported {len(self.metrics_history)} metrics to {filepath}")
    
    def _calculate_perceived_latency(
        self, 
        generation_type: GenerationType, 
        time_to_first_audio: float, 
        total_time: float
    ) -> float:
        """Calculate perceived latency based on generation type"""
        
        if generation_type == GenerationType.STREAMING:
            # For streaming, perceived latency is just time to first audio
            return time_to_first_audio
        elif generation_type == GenerationType.CHUNKED:
            # For chunked, it's a weighted average
            return (time_to_first_audio * 0.7) + (total_time * 0.3)
        else:
            # For standard, it's the total time
            return total_time
    
    def _categorize_text_length(self, length: int) -> str:
        """Categorize text by length"""
        if length < 50:
            return "short"
        elif length < 200:
            return "medium"
        elif length < 500:
            return "long"
        else:
            return "very_long"
    
    def _calculate_avg_comparison(
        self, 
        metric_lists: List[List[PerformanceMetrics]], 
        labels: List[str],
        value_func
    ) -> Dict[str, float]:
        """Calculate average comparison between metric lists"""
        comparison = {}
        
        for metrics_list, label in zip(metric_lists, labels):
            if metrics_list:
                values = [value_func(m) for m in metrics_list if value_func(m) is not None]
                if values:
                    comparison[label] = statistics.mean(values)
                else:
                    comparison[label] = 0.0
            else:
                comparison[label] = 0.0
        
        return comparison
    
    def _update_current_stats(self, metrics: PerformanceMetrics):
        """Update real-time statistics"""
        self.current_stats["total_generations"] += 1
        
        if metrics.generation_type == GenerationType.CHUNKED:
            self.current_stats["chunked_generations"] += 1
        elif metrics.generation_type == GenerationType.STREAMING:
            self.current_stats["streaming_generations"] += 1
        else:
            self.current_stats["standard_generations"] += 1
        
        # Update rolling averages (last 100 generations)
        recent_metrics = list(self.metrics_history)[-100:]
        
        if recent_metrics:
            rtf_values = [m.rtf for m in recent_metrics]
            latency_values = [m.time_to_first_audio for m in recent_metrics]
            
            self.current_stats["avg_rtf_last_100"] = statistics.mean(rtf_values)
            self.current_stats["avg_latency_last_100"] = statistics.mean(latency_values)
    
    def cleanup_old_metrics(self, max_age_hours: int = 24):
        """Clean up old metrics to prevent memory bloat"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        # Clean main history
        original_count = len(self.metrics_history)
        self.metrics_history = deque(
            [m for m in self.metrics_history if m.timestamp >= cutoff_time],
            maxlen=self.max_history
        )
        
        # Clean categorized metrics
        for category in self.metrics_by_type:
            self.metrics_by_type[category] = [
                m for m in self.metrics_by_type[category] if m.timestamp >= cutoff_time
            ]
        
        for voice_id in self.metrics_by_voice:
            self.metrics_by_voice[voice_id] = [
                m for m in self.metrics_by_voice[voice_id] if m.timestamp >= cutoff_time
            ]
        
        for length_category in self.metrics_by_text_length:
            self.metrics_by_text_length[length_category] = [
                m for m in self.metrics_by_text_length[length_category] if m.timestamp >= cutoff_time
            ]
        
        cleaned_count = original_count - len(self.metrics_history)
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old metrics")
        
        return cleaned_count
