"""
Enhanced Performance Monitoring for RTF Optimization
"""

import time
import threading
from typing import Dict, List, Any, Optional
from collections import deque
import statistics

class RTFPerformanceMonitor:
    """Enhanced performance monitoring for RTF optimization"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.rtf_history = deque(maxlen=window_size)
        self.response_times = deque(maxlen=window_size)
        self.audio_durations = deque(maxlen=window_size)
        
        self.lock = threading.RLock()
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'avg_rtf': 0.0,
            'min_rtf': float('inf'),
            'max_rtf': 0.0,
            'rtf_p95': 0.0,
            'rtf_p99': 0.0,
            'avg_response_time': 0.0,
            'throughput_rps': 0.0,
            'performance_grade': 'A+'
        }
        
        # Request tracking
        self.request_timestamps = deque(maxlen=window_size)
    
    def record_request(self, rtf: float, response_time: float, 
                      audio_duration: float):
        """Record a TTS request for performance analysis"""
        with self.lock:
            # Record metrics
            self.rtf_history.append(rtf)
            self.response_times.append(response_time)
            self.audio_durations.append(audio_duration)
            self.request_timestamps.append(time.time())
            
            # Update counters
            self.metrics['total_requests'] += 1
            
            # Update statistics
            self._update_metrics()
    
    def _update_metrics(self):
        """Update performance metrics"""
        if not self.rtf_history:
            return
        
        rtf_values = list(self.rtf_history)
        response_values = list(self.response_times)
        
        # RTF statistics
        self.metrics['avg_rtf'] = statistics.mean(rtf_values)
        self.metrics['min_rtf'] = min(rtf_values)
        self.metrics['max_rtf'] = max(rtf_values)
        
        # Percentiles
        if len(rtf_values) >= 2:
            sorted_rtf = sorted(rtf_values)
            self.metrics['rtf_p95'] = sorted_rtf[int(len(sorted_rtf) * 0.95)]
            self.metrics['rtf_p99'] = sorted_rtf[int(len(sorted_rtf) * 0.99)]
        
        # Response time
        self.metrics['avg_response_time'] = statistics.mean(response_values)
        
        # Throughput (requests per second)
        if len(self.request_timestamps) >= 2:
            time_span = self.request_timestamps[-1] - self.request_timestamps[0]
            if time_span > 0:
                self.metrics['throughput_rps'] = len(self.request_timestamps) / time_span
        
        # Performance grade
        self.metrics['performance_grade'] = self._calculate_grade()
    
    def _calculate_grade(self) -> str:
        """Calculate performance grade based on RTF"""
        avg_rtf = self.metrics['avg_rtf']
        
        if avg_rtf < 0.1:
            return 'A+'
        elif avg_rtf < 0.2:
            return 'A'
        elif avg_rtf < 0.3:
            return 'B+'
        elif avg_rtf < 0.5:
            return 'B'
        elif avg_rtf < 0.8:
            return 'C'
        else:
            return 'D'
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        with self.lock:
            return self.metrics.copy()
    
    def get_rtf_trend(self) -> List[float]:
        """Get recent RTF trend"""
        with self.lock:
            return list(self.rtf_history)
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        with self.lock:
            self.rtf_history.clear()
            self.response_times.clear()
            self.audio_durations.clear()
            self.request_timestamps.clear()
            
            self.metrics = {
                'total_requests': 0,
                'avg_rtf': 0.0,
                'min_rtf': float('inf'),
                'max_rtf': 0.0,
                'rtf_p95': 0.0,
                'rtf_p99': 0.0,
                'avg_response_time': 0.0,
                'throughput_rps': 0.0,
                'performance_grade': 'A+'
            }

# Global monitor instance
_performance_monitor = RTFPerformanceMonitor()

def get_performance_monitor():
    """Get the global performance monitor instance"""
    return _performance_monitor
