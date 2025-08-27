#!/usr/bin/env python3
"""
API Analytics & Concurrency Dashboard

Provides real-time monitoring and analytics for the TTS API including:
- Request metrics (requests per minute/hour, response times)
- Concurrency metrics (active connections, queue status)
- Performance statistics (latency, RTF)
- Voice usage statistics
- Error rates and status codes
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import threading
import asyncio

@dataclass
class RequestMetric:
    """Individual request metric"""
    timestamp: datetime
    method: str
    path: str
    status_code: int
    response_time: float
    client_ip: str
    user_agent: str
    voice: Optional[str] = None
    text_length: Optional[int] = None
    cache_hit: bool = False

@dataclass
class ConcurrencyMetric:
    """Concurrency tracking metric"""
    timestamp: datetime
    active_connections: int
    queue_size: int
    processing_requests: int

class DashboardAnalytics:
    """
    Real-time analytics collector for the dashboard
    
    Tracks all API requests, performance metrics, and system status
    for display in the web dashboard.
    """
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        
        # Request tracking
        self.request_metrics: deque = deque(maxlen=max_history)
        self.concurrency_metrics: deque = deque(maxlen=max_history)
        
        # Real-time counters
        self.active_connections = 0
        self.processing_requests = 0
        self.queue_size = 0
        
        # Error tracking
        self.error_counts = defaultdict(int)
        self.status_code_counts = defaultdict(int)
        
        # Voice usage tracking
        self.voice_usage = defaultdict(int)
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Start background cleanup task
        self._start_cleanup_task()
    
    def record_request(self, 
                      method: str,
                      path: str, 
                      status_code: int,
                      response_time: float,
                      client_ip: str,
                      user_agent: str,
                      voice: Optional[str] = None,
                      text_length: Optional[int] = None,
                      cache_hit: bool = False):
        """Record a completed request"""
        
        with self.lock:
            metric = RequestMetric(
                timestamp=datetime.now(),
                method=method,
                path=path,
                status_code=status_code,
                response_time=response_time,
                client_ip=client_ip,
                user_agent=user_agent,
                voice=voice,
                text_length=text_length,
                cache_hit=cache_hit
            )
            
            self.request_metrics.append(metric)
            
            # Update counters
            self.status_code_counts[status_code] += 1
            
            if status_code >= 400:
                self.error_counts[status_code] += 1
            
            if voice:
                self.voice_usage[voice] += 1
    
    def update_concurrency(self, active_connections: int, queue_size: int, processing_requests: int):
        """Update concurrency metrics"""
        
        with self.lock:
            self.active_connections = active_connections
            self.queue_size = queue_size
            self.processing_requests = processing_requests
            
            metric = ConcurrencyMetric(
                timestamp=datetime.now(),
                active_connections=active_connections,
                queue_size=queue_size,
                processing_requests=processing_requests
            )
            
            self.concurrency_metrics.append(metric)
    
    def get_requests_per_minute(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get requests per minute for the last N minutes"""
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            # Group requests by minute
            minute_counts = defaultdict(int)
            
            for metric in self.request_metrics:
                if metric.timestamp >= cutoff_time:
                    minute_key = metric.timestamp.replace(second=0, microsecond=0)
                    minute_counts[minute_key] += 1
            
            # Convert to list format
            result = []
            for minute in sorted(minute_counts.keys()):
                result.append({
                    'timestamp': minute.isoformat(),
                    'requests': minute_counts[minute]
                })
            
            return result
    
    def get_response_time_stats(self, minutes: int = 60) -> Dict[str, float]:
        """Get response time statistics"""
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            response_times = [
                metric.response_time 
                for metric in self.request_metrics 
                if metric.timestamp >= cutoff_time
            ]
            
            if not response_times:
                return {
                    'avg': 0.0,
                    'min': 0.0,
                    'max': 0.0,
                    'p50': 0.0,
                    'p95': 0.0,
                    'p99': 0.0
                }
            
            response_times.sort()
            count = len(response_times)
            
            return {
                'avg': sum(response_times) / count,
                'min': response_times[0],
                'max': response_times[-1],
                'p50': response_times[int(count * 0.5)],
                'p95': response_times[int(count * 0.95)],
                'p99': response_times[int(count * 0.99)]
            }
    
    def get_error_rates(self, minutes: int = 60) -> Dict[str, Any]:
        """Get error rates and status code distribution"""
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            total_requests = 0
            error_requests = 0
            status_counts = defaultdict(int)
            
            for metric in self.request_metrics:
                if metric.timestamp >= cutoff_time:
                    total_requests += 1
                    status_counts[metric.status_code] += 1
                    
                    if metric.status_code >= 400:
                        error_requests += 1
            
            error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'total_requests': total_requests,
                'error_requests': error_requests,
                'error_rate_percent': round(error_rate, 2),
                'status_code_distribution': dict(status_counts)
            }
    
    def get_voice_usage_stats(self, minutes: int = 60) -> Dict[str, int]:
        """Get voice usage statistics"""
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            voice_counts = defaultdict(int)
            
            for metric in self.request_metrics:
                if metric.timestamp >= cutoff_time and metric.voice:
                    voice_counts[metric.voice] += 1
            
            return dict(voice_counts)
    
    def get_concurrency_stats(self) -> Dict[str, Any]:
        """Get current concurrency statistics"""
        
        with self.lock:
            return {
                'current': {
                    'active_connections': self.active_connections,
                    'queue_size': self.queue_size,
                    'processing_requests': self.processing_requests
                },
                'history': [
                    {
                        'timestamp': metric.timestamp.isoformat(),
                        'active_connections': metric.active_connections,
                        'queue_size': metric.queue_size,
                        'processing_requests': metric.processing_requests
                    }
                    for metric in list(self.concurrency_metrics)[-100:]  # Last 100 data points
                ]
            }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'requests_per_minute': self.get_requests_per_minute(60),
            'response_time_stats': self.get_response_time_stats(60),
            'error_rates': self.get_error_rates(60),
            'voice_usage': self.get_voice_usage_stats(60),
            'concurrency': self.get_concurrency_stats(),
            'system_status': {
                'uptime_seconds': time.time() - getattr(self, 'start_time', time.time()),
                'total_requests_all_time': len(self.request_metrics),
                'total_errors_all_time': sum(self.error_counts.values())
            }
        }
    
    def _start_cleanup_task(self):
        """Start background task to clean up old metrics"""
        self.start_time = time.time()
        
        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # Clean up every 5 minutes
                    
                    cutoff_time = datetime.now() - timedelta(hours=24)
                    
                    with self.lock:
                        # Clean up old request metrics
                        while (self.request_metrics and 
                               self.request_metrics[0].timestamp < cutoff_time):
                            self.request_metrics.popleft()
                        
                        # Clean up old concurrency metrics
                        while (self.concurrency_metrics and 
                               self.concurrency_metrics[0].timestamp < cutoff_time):
                            self.concurrency_metrics.popleft()
                
                except Exception as e:
                    print(f"Error in dashboard cleanup: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

# Global analytics instance
dashboard_analytics = DashboardAnalytics()
