#!/usr/bin/env python3
"""
Memory Profiler for LiteTTS

Specialized memory profiling tools for TTS operations including:
- Memory usage tracking during synthesis
- Memory leak detection
- Voice model memory optimization
- Cache memory management
- Memory pressure monitoring
"""

import gc
import tracemalloc
import psutil
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
import logging
from collections import defaultdict
import weakref

logger = logging.getLogger(__name__)

@dataclass
class MemorySnapshot:
    """Memory usage snapshot"""
    timestamp: float
    rss_mb: float  # Resident Set Size
    vms_mb: float  # Virtual Memory Size
    percent: float  # Memory percentage
    available_mb: float
    tracemalloc_current_mb: float = 0.0
    tracemalloc_peak_mb: float = 0.0
    gc_objects: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MemoryLeak:
    """Memory leak detection result"""
    component: str
    leak_rate_mb_per_sec: float
    total_leaked_mb: float
    confidence: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class MemoryProfiler:
    """Specialized memory profiler for TTS operations"""
    
    def __init__(self, enable_tracemalloc: bool = True, snapshot_interval: float = 1.0):
        """Initialize memory profiler
        
        Args:
            enable_tracemalloc: Enable detailed memory tracking
            snapshot_interval: Interval between memory snapshots (seconds)
        """
        self.enable_tracemalloc = enable_tracemalloc
        self.snapshot_interval = snapshot_interval
        
        # Memory tracking data
        self.snapshots: List[MemorySnapshot] = []
        self.component_memory: Dict[str, List[float]] = defaultdict(list)
        self.voice_model_memory: Dict[str, float] = {}
        self.cache_memory: Dict[str, float] = {}
        
        # Monitoring state
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._baseline_memory: Optional[float] = None
        
        # Leak detection
        self._leak_detection_data: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
        self._object_refs: Dict[str, List[weakref.ref]] = defaultdict(list)
        
        # Results directory
        self.results_dir = Path("performance_results/memory")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Memory profiler initialized")
    
    def start_monitoring(self):
        """Start memory monitoring"""
        if self._monitoring_active:
            logger.warning("Memory monitoring already active")
            return
        
        # Start tracemalloc if enabled
        if self.enable_tracemalloc and not tracemalloc.is_tracing():
            tracemalloc.start()
            logger.debug("Started tracemalloc")
        
        # Record baseline memory
        self._baseline_memory = self._get_current_memory_usage()
        
        # Start monitoring thread
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self._monitor_thread.start()
        
        logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop memory monitoring"""
        if not self._monitoring_active:
            return
        
        self._monitoring_active = False
        
        # Stop monitoring thread
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        
        # Stop tracemalloc
        if self.enable_tracemalloc and tracemalloc.is_tracing():
            tracemalloc.stop()
            logger.debug("Stopped tracemalloc")
        
        logger.info("Memory monitoring stopped")
    
    def _monitor_memory(self):
        """Background memory monitoring thread"""
        while self._monitoring_active:
            try:
                snapshot = self._take_memory_snapshot()
                self.snapshots.append(snapshot)
                
                # Check for memory leaks
                self._check_for_leaks(snapshot)
                
                time.sleep(self.snapshot_interval)
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(self.snapshot_interval)
    
    def _take_memory_snapshot(self) -> MemorySnapshot:
        """Take a memory usage snapshot"""
        # Get process memory info
        process = psutil.Process()
        memory_info = process.memory_info()
        system_memory = psutil.virtual_memory()
        
        # Get tracemalloc info if available
        tracemalloc_current = 0.0
        tracemalloc_peak = 0.0
        
        if self.enable_tracemalloc and tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc_current = current / (1024 * 1024)  # Convert to MB
            tracemalloc_peak = peak / (1024 * 1024)
        
        # Get garbage collection info
        gc_objects = len(gc.get_objects())
        
        return MemorySnapshot(
            timestamp=time.time(),
            rss_mb=memory_info.rss / (1024 * 1024),
            vms_mb=memory_info.vms / (1024 * 1024),
            percent=system_memory.percent,
            available_mb=system_memory.available / (1024 * 1024),
            tracemalloc_current_mb=tracemalloc_current,
            tracemalloc_peak_mb=tracemalloc_peak,
            gc_objects=gc_objects
        )
    
    def _get_current_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0
    
    def track_component_memory(self, component_name: str, memory_mb: float):
        """Track memory usage for a specific component
        
        Args:
            component_name: Name of the component
            memory_mb: Memory usage in MB
        """
        self.component_memory[component_name].append(memory_mb)
        
        # Store for leak detection
        self._leak_detection_data[component_name].append((time.time(), memory_mb))
        
        # Keep only recent data (last 100 measurements)
        if len(self._leak_detection_data[component_name]) > 100:
            self._leak_detection_data[component_name] = self._leak_detection_data[component_name][-100:]
    
    def track_voice_model_memory(self, voice_name: str, memory_mb: float):
        """Track memory usage for voice models
        
        Args:
            voice_name: Name of the voice
            memory_mb: Memory usage in MB
        """
        self.voice_model_memory[voice_name] = memory_mb
        logger.debug(f"Voice model {voice_name}: {memory_mb:.2f} MB")
    
    def track_cache_memory(self, cache_name: str, memory_mb: float):
        """Track memory usage for caches
        
        Args:
            cache_name: Name of the cache
            memory_mb: Memory usage in MB
        """
        self.cache_memory[cache_name] = memory_mb
        logger.debug(f"Cache {cache_name}: {memory_mb:.2f} MB")
    
    def _check_for_leaks(self, snapshot: MemorySnapshot):
        """Check for potential memory leaks"""
        if not self.snapshots or len(self.snapshots) < 10:
            return  # Need more data
        
        # Check for consistent memory growth
        recent_snapshots = self.snapshots[-10:]
        memory_values = [s.rss_mb for s in recent_snapshots]
        
        # Simple linear regression to detect growth trend
        if len(memory_values) >= 5:
            x_values = list(range(len(memory_values)))
            n = len(memory_values)
            
            sum_x = sum(x_values)
            sum_y = sum(memory_values)
            sum_xy = sum(x * y for x, y in zip(x_values, memory_values))
            sum_x2 = sum(x * x for x in x_values)
            
            # Calculate slope (memory growth rate)
            if n * sum_x2 - sum_x * sum_x != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                
                # Convert slope to MB per second
                slope_mb_per_sec = slope / self.snapshot_interval
                
                # Flag potential leak if growth > 1 MB per minute
                if slope_mb_per_sec > 1.0 / 60:
                    logger.warning(f"Potential memory leak detected: {slope_mb_per_sec:.3f} MB/sec growth")
    
    def detect_memory_leaks(self) -> List[MemoryLeak]:
        """Detect memory leaks in tracked components
        
        Returns:
            List of detected memory leaks
        """
        leaks = []
        
        for component, data_points in self._leak_detection_data.items():
            if len(data_points) < 10:
                continue  # Need more data
            
            # Analyze memory growth trend
            timestamps = [dp[0] for dp in data_points]
            memory_values = [dp[1] for dp in data_points]
            
            # Calculate growth rate
            if len(data_points) >= 5:
                time_span = timestamps[-1] - timestamps[0]
                memory_growth = memory_values[-1] - memory_values[0]
                
                if time_span > 0:
                    growth_rate = memory_growth / time_span  # MB per second
                    
                    # Flag as leak if growth > 0.1 MB per minute
                    if growth_rate > 0.1 / 60:
                        confidence = min(1.0, growth_rate * 600)  # Scale confidence
                        
                        leak = MemoryLeak(
                            component=component,
                            leak_rate_mb_per_sec=growth_rate,
                            total_leaked_mb=memory_growth,
                            confidence=confidence,
                            evidence=[
                                f"Memory growth: {memory_growth:.2f} MB over {time_span:.1f} seconds",
                                f"Growth rate: {growth_rate * 60:.3f} MB/minute"
                            ],
                            recommendations=[
                                f"Review {component} for unreleased resources",
                                "Check for circular references or unclosed files",
                                "Implement proper cleanup in {component}"
                            ]
                        )
                        
                        leaks.append(leak)
        
        return leaks
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get comprehensive memory usage summary
        
        Returns:
            Memory usage summary
        """
        if not self.snapshots:
            return {'error': 'No memory snapshots available'}
        
        # Calculate statistics from snapshots
        rss_values = [s.rss_mb for s in self.snapshots]
        
        summary = {
            'monitoring_duration_sec': self.snapshots[-1].timestamp - self.snapshots[0].timestamp if len(self.snapshots) > 1 else 0,
            'snapshot_count': len(self.snapshots),
            'baseline_memory_mb': self._baseline_memory or 0,
            'current_memory_mb': rss_values[-1] if rss_values else 0,
            'peak_memory_mb': max(rss_values) if rss_values else 0,
            'min_memory_mb': min(rss_values) if rss_values else 0,
            'avg_memory_mb': sum(rss_values) / len(rss_values) if rss_values else 0,
            'memory_growth_mb': (rss_values[-1] - rss_values[0]) if len(rss_values) > 1 else 0,
            'voice_models': dict(self.voice_model_memory),
            'caches': dict(self.cache_memory),
            'component_memory': {
                component: {
                    'current_mb': values[-1] if values else 0,
                    'peak_mb': max(values) if values else 0,
                    'avg_mb': sum(values) / len(values) if values else 0
                }
                for component, values in self.component_memory.items()
            },
            'detected_leaks': len(self.detect_memory_leaks())
        }
        
        return summary
    
    def save_memory_report(self, filename: str = None) -> Path:
        """Save memory profiling report
        
        Args:
            filename: Optional filename
            
        Returns:
            Path to saved report
        """
        if filename is None:
            timestamp = int(time.time())
            filename = f"memory_report_{timestamp}.json"
        
        report_path = self.results_dir / filename
        
        # Prepare report data
        report_data = {
            'summary': self.get_memory_summary(),
            'snapshots': [
                {
                    'timestamp': s.timestamp,
                    'rss_mb': s.rss_mb,
                    'vms_mb': s.vms_mb,
                    'percent': s.percent,
                    'available_mb': s.available_mb,
                    'tracemalloc_current_mb': s.tracemalloc_current_mb,
                    'tracemalloc_peak_mb': s.tracemalloc_peak_mb,
                    'gc_objects': s.gc_objects
                }
                for s in self.snapshots
            ],
            'detected_leaks': [
                {
                    'component': leak.component,
                    'leak_rate_mb_per_sec': leak.leak_rate_mb_per_sec,
                    'total_leaked_mb': leak.total_leaked_mb,
                    'confidence': leak.confidence,
                    'evidence': leak.evidence,
                    'recommendations': leak.recommendations
                }
                for leak in self.detect_memory_leaks()
            ],
            'component_memory': dict(self.component_memory),
            'voice_model_memory': self.voice_model_memory,
            'cache_memory': self.cache_memory
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Memory report saved: {report_path}")
        return report_path
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """Force garbage collection and return statistics
        
        Returns:
            Garbage collection statistics
        """
        # Get pre-GC object count
        pre_gc_objects = len(gc.get_objects())
        
        # Force garbage collection
        collected = gc.collect()
        
        # Get post-GC object count
        post_gc_objects = len(gc.get_objects())
        
        stats = {
            'objects_before': pre_gc_objects,
            'objects_after': post_gc_objects,
            'objects_collected': collected,
            'objects_freed': pre_gc_objects - post_gc_objects
        }
        
        logger.info(f"Garbage collection: {stats}")
        return stats

# Global memory profiler instance
_memory_profiler: Optional[MemoryProfiler] = None

def get_memory_profiler() -> MemoryProfiler:
    """Get the global memory profiler instance"""
    global _memory_profiler
    if _memory_profiler is None:
        _memory_profiler = MemoryProfiler()
    return _memory_profiler

def track_component_memory(component_name: str, memory_mb: float):
    """Track memory usage for a component"""
    get_memory_profiler().track_component_memory(component_name, memory_mb)

def track_voice_memory(voice_name: str, memory_mb: float):
    """Track memory usage for a voice model"""
    get_memory_profiler().track_voice_model_memory(voice_name, memory_mb)

def track_cache_memory(cache_name: str, memory_mb: float):
    """Track memory usage for a cache"""
    get_memory_profiler().track_cache_memory(cache_name, memory_mb)

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_memory_profiler():
        """Test the memory profiler"""
        profiler = get_memory_profiler()
        
        # Start monitoring
        profiler.start_monitoring()
        
        # Simulate some memory usage
        data = []
        for i in range(10):
            # Simulate memory allocation
            chunk = [0] * (100000 + i * 10000)  # Growing memory usage
            data.append(chunk)
            
            # Track component memory
            profiler.track_component_memory("test_component", len(data) * 0.1)
            
            await asyncio.sleep(0.5)
        
        # Stop monitoring
        profiler.stop_monitoring()
        
        # Generate report
        summary = profiler.get_memory_summary()
        print(f"Memory summary: {summary}")
        
        # Save report
        report_path = profiler.save_memory_report()
        print(f"Memory report saved: {report_path}")
        
        # Check for leaks
        leaks = profiler.detect_memory_leaks()
        if leaks:
            print(f"Detected {len(leaks)} potential memory leaks")
            for leak in leaks:
                print(f"  - {leak.component}: {leak.leak_rate_mb_per_sec:.3f} MB/sec")
    
    # Run the test
    asyncio.run(test_memory_profiler())
