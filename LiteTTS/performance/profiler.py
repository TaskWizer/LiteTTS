#!/usr/bin/env python3
"""
Comprehensive Performance Profiling Infrastructure for LiteTTS

This module provides systematic performance profiling tools including:
- cProfile for function-level analysis
- Memory profiling for memory usage tracking
- Custom timing decorators for TTS pipeline measurement
- Real-Time Factor (RTF) calculation
- Bottleneck identification and reporting
"""

import cProfile
import pstats
import io
import time
import psutil
import threading
import functools
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
from contextlib import contextmanager
from collections import defaultdict
import tracemalloc

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for TTS operations"""
    operation_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_percent: float
    text_length: int = 0
    audio_duration: float = 0.0
    rtf: float = 0.0  # Real-Time Factor
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProfilingSession:
    """Complete profiling session data"""
    session_id: str
    start_time: float
    end_time: float
    total_duration: float
    operations: List[PerformanceMetrics] = field(default_factory=list)
    memory_snapshots: List[Dict] = field(default_factory=list)
    cpu_snapshots: List[float] = field(default_factory=list)
    bottlenecks: List[Dict] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

class PerformanceProfiler:
    """Comprehensive performance profiler for LiteTTS"""
    
    def __init__(self, enable_memory_tracking: bool = True, enable_cpu_tracking: bool = True):
        """Initialize performance profiler
        
        Args:
            enable_memory_tracking: Enable memory usage tracking
            enable_cpu_tracking: Enable CPU usage tracking
        """
        self.enable_memory_tracking = enable_memory_tracking
        self.enable_cpu_tracking = enable_cpu_tracking
        
        # Profiling data storage
        self.current_session: Optional[ProfilingSession] = None
        self.sessions: List[ProfilingSession] = []
        self.operation_metrics: Dict[str, List[PerformanceMetrics]] = defaultdict(list)
        
        # Monitoring threads
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Results directory
        self.results_dir = Path("performance_results")
        self.results_dir.mkdir(exist_ok=True)
        
        logger.info("Performance profiler initialized")
    
    def start_session(self, session_id: str = None) -> str:
        """Start a new profiling session
        
        Args:
            session_id: Optional session identifier
            
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = f"session_{int(time.time())}"
        
        self.current_session = ProfilingSession(
            session_id=session_id,
            start_time=time.time(),
            end_time=0.0,
            total_duration=0.0
        )
        
        # Start memory tracking
        if self.enable_memory_tracking:
            tracemalloc.start()
        
        # Start monitoring thread
        self._start_monitoring()
        
        logger.info(f"Started profiling session: {session_id}")
        return session_id
    
    def end_session(self) -> ProfilingSession:
        """End the current profiling session
        
        Returns:
            Completed profiling session
        """
        if not self.current_session:
            raise RuntimeError("No active profiling session")
        
        # Stop monitoring
        self._stop_monitoring()
        
        # Stop memory tracking
        if self.enable_memory_tracking and tracemalloc.is_tracing():
            tracemalloc.stop()
        
        # Finalize session
        self.current_session.end_time = time.time()
        self.current_session.total_duration = (
            self.current_session.end_time - self.current_session.start_time
        )
        
        # Generate summary
        self.current_session.summary = self._generate_session_summary()
        
        # Store session
        self.sessions.append(self.current_session)
        session = self.current_session
        self.current_session = None
        
        logger.info(f"Ended profiling session: {session.session_id}")
        return session
    
    def _start_monitoring(self):
        """Start background monitoring thread"""
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self._monitor_thread.start()
    
    def _stop_monitoring(self):
        """Stop background monitoring thread"""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
    
    def _monitor_system(self):
        """Background system monitoring"""
        while self._monitoring_active:
            try:
                # CPU monitoring
                if self.enable_cpu_tracking and self.current_session:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    self.current_session.cpu_snapshots.append(cpu_percent)
                
                # Memory monitoring
                if self.enable_memory_tracking and self.current_session:
                    memory_info = psutil.virtual_memory()
                    self.current_session.memory_snapshots.append({
                        'timestamp': time.time(),
                        'used_mb': memory_info.used / 1024 / 1024,
                        'available_mb': memory_info.available / 1024 / 1024,
                        'percent': memory_info.percent
                    })
                
                time.sleep(0.5)  # Monitor every 500ms
                
            except Exception as e:
                logger.warning(f"Monitoring error: {e}")
    
    def profile_operation(self, operation_name: str):
        """Decorator for profiling individual operations
        
        Args:
            operation_name: Name of the operation being profiled
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self._profile_function(func, operation_name, *args, **kwargs)
            return wrapper
        return decorator
    
    def _profile_function(self, func: Callable, operation_name: str, *args, **kwargs):
        """Profile a function execution"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        start_cpu = psutil.cpu_percent()
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            logger.error(f"Error in profiled function {operation_name}: {e}")
            result = None
            success = False
        
        # Calculate metrics
        end_time = time.time()
        execution_time = end_time - start_time
        end_memory = self._get_memory_usage()
        memory_usage = end_memory - start_memory
        
        # Extract text and audio information if available
        text_length = 0
        audio_duration = 0.0
        rtf = 0.0
        
        # Try to extract text length from arguments
        for arg in args:
            if isinstance(arg, str) and len(arg) > 0:
                text_length = len(arg)
                break
        
        # Try to extract audio duration from result
        if hasattr(result, 'duration'):
            audio_duration = result.duration
        elif isinstance(result, dict) and 'duration' in result:
            audio_duration = result['duration']
        
        # Calculate RTF if we have audio duration
        if audio_duration > 0:
            rtf = execution_time / audio_duration
        
        # Create metrics
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            execution_time=execution_time,
            memory_usage_mb=memory_usage,
            cpu_percent=psutil.cpu_percent() - start_cpu,
            text_length=text_length,
            audio_duration=audio_duration,
            rtf=rtf,
            metadata={
                'success': success,
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            }
        )
        
        # Store metrics
        self.operation_metrics[operation_name].append(metrics)
        if self.current_session:
            self.current_session.operations.append(metrics)
        
        logger.debug(f"Profiled {operation_name}: {execution_time:.3f}s, RTF: {rtf:.3f}")
        
        return result
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
    
    @contextmanager
    def profile_context(self, operation_name: str):
        """Context manager for profiling code blocks
        
        Args:
            operation_name: Name of the operation being profiled
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            memory_usage = self._get_memory_usage() - start_memory
            
            metrics = PerformanceMetrics(
                operation_name=operation_name,
                execution_time=execution_time,
                memory_usage_mb=memory_usage,
                cpu_percent=psutil.cpu_percent(),
                metadata={'context_manager': True}
            )
            
            self.operation_metrics[operation_name].append(metrics)
            if self.current_session:
                self.current_session.operations.append(metrics)
    
    def profile_with_cprofile(self, func: Callable, *args, **kwargs) -> Tuple[Any, pstats.Stats]:
        """Profile function with cProfile for detailed analysis
        
        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Tuple of (function_result, profiling_stats)
        """
        profiler = cProfile.Profile()
        
        profiler.enable()
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
        
        # Create stats object
        stats_stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        
        return result, stats
    
    def _generate_session_summary(self) -> Dict[str, Any]:
        """Generate summary for current session"""
        if not self.current_session:
            return {}
        
        operations = self.current_session.operations
        if not operations:
            return {'total_operations': 0}
        
        # Calculate aggregated metrics
        total_time = sum(op.execution_time for op in operations)
        total_memory = sum(op.memory_usage_mb for op in operations)
        avg_rtf = sum(op.rtf for op in operations if op.rtf > 0) / max(1, len([op for op in operations if op.rtf > 0]))
        
        # Find slowest operations
        slowest_ops = sorted(operations, key=lambda x: x.execution_time, reverse=True)[:5]
        
        # Find memory-intensive operations
        memory_intensive = sorted(operations, key=lambda x: x.memory_usage_mb, reverse=True)[:5]
        
        return {
            'total_operations': len(operations),
            'total_execution_time': total_time,
            'total_memory_usage_mb': total_memory,
            'average_rtf': avg_rtf,
            'slowest_operations': [
                {'name': op.operation_name, 'time': op.execution_time, 'rtf': op.rtf}
                for op in slowest_ops
            ],
            'memory_intensive_operations': [
                {'name': op.operation_name, 'memory_mb': op.memory_usage_mb}
                for op in memory_intensive
            ],
            'cpu_usage_avg': sum(self.current_session.cpu_snapshots) / max(1, len(self.current_session.cpu_snapshots)),
            'memory_snapshots_count': len(self.current_session.memory_snapshots)
        }
    
    def save_session_report(self, session: ProfilingSession, filename: str = None) -> Path:
        """Save session report to file
        
        Args:
            session: Profiling session to save
            filename: Optional filename (defaults to session_id.json)
            
        Returns:
            Path to saved report
        """
        if filename is None:
            filename = f"{session.session_id}_report.json"
        
        report_path = self.results_dir / filename
        
        # Convert session to serializable format
        report_data = {
            'session_id': session.session_id,
            'start_time': session.start_time,
            'end_time': session.end_time,
            'total_duration': session.total_duration,
            'operations': [
                {
                    'operation_name': op.operation_name,
                    'execution_time': op.execution_time,
                    'memory_usage_mb': op.memory_usage_mb,
                    'cpu_percent': op.cpu_percent,
                    'text_length': op.text_length,
                    'audio_duration': op.audio_duration,
                    'rtf': op.rtf,
                    'timestamp': op.timestamp,
                    'metadata': op.metadata
                }
                for op in session.operations
            ],
            'memory_snapshots': session.memory_snapshots,
            'cpu_snapshots': session.cpu_snapshots,
            'summary': session.summary
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved profiling report: {report_path}")
        return report_path
    
    def get_operation_statistics(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for a specific operation
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Statistics dictionary
        """
        metrics = self.operation_metrics.get(operation_name, [])
        if not metrics:
            return {'operation_name': operation_name, 'count': 0}
        
        execution_times = [m.execution_time for m in metrics]
        memory_usages = [m.memory_usage_mb for m in metrics]
        rtfs = [m.rtf for m in metrics if m.rtf > 0]
        
        return {
            'operation_name': operation_name,
            'count': len(metrics),
            'execution_time': {
                'min': min(execution_times),
                'max': max(execution_times),
                'avg': sum(execution_times) / len(execution_times),
                'total': sum(execution_times)
            },
            'memory_usage_mb': {
                'min': min(memory_usages),
                'max': max(memory_usages),
                'avg': sum(memory_usages) / len(memory_usages),
                'total': sum(memory_usages)
            },
            'rtf': {
                'min': min(rtfs) if rtfs else 0,
                'max': max(rtfs) if rtfs else 0,
                'avg': sum(rtfs) / len(rtfs) if rtfs else 0,
                'count': len(rtfs)
            }
        }

# Global profiler instance
_profiler: Optional[PerformanceProfiler] = None

def get_profiler() -> PerformanceProfiler:
    """Get the global profiler instance"""
    global _profiler
    if _profiler is None:
        _profiler = PerformanceProfiler()
    return _profiler

def profile_tts_operation(operation_name: str):
    """Decorator for profiling TTS operations"""
    return get_profiler().profile_operation(operation_name)

# Convenience functions
def start_profiling_session(session_id: str = None) -> str:
    """Start a profiling session"""
    return get_profiler().start_session(session_id)

def end_profiling_session() -> ProfilingSession:
    """End the current profiling session"""
    return get_profiler().end_session()

def profile_context(operation_name: str):
    """Context manager for profiling"""
    return get_profiler().profile_context(operation_name)

# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def test_profiler():
        """Test the performance profiler"""
        profiler = get_profiler()

        # Start profiling session
        session_id = profiler.start_session("test_session")
        print(f"Started profiling session: {session_id}")

        # Test operation profiling
        @profile_tts_operation("test_text_processing")
        def process_text(text: str) -> str:
            time.sleep(0.1)  # Simulate processing
            return text.upper()

        # Test context profiling
        with profile_context("test_context_operation"):
            time.sleep(0.05)
            print("Context operation completed")

        # Run some test operations
        for i in range(5):
            result = process_text(f"Test text {i}")
            print(f"Processed: {result}")

        # End session and save report
        session = profiler.end_session()
        report_path = profiler.save_session_report(session)

        print(f"Session completed. Report saved to: {report_path}")
        print(f"Session summary: {session.summary}")

        # Show operation statistics
        stats = profiler.get_operation_statistics("test_text_processing")
        print(f"Operation statistics: {stats}")

    # Run the test
    asyncio.run(test_profiler())
