#!/usr/bin/env python3
"""
Performance monitoring system for TTS optimization
Tracks RTF, latency, cache performance, and system metrics
"""

import time
import threading
import psutil
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    timestamp: datetime
    metric_type: str  # 'tts_generation', 'cache_hit', 'cache_miss', 'system'
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TTSPerformanceData:
    """TTS-specific performance data"""
    text_length: int
    voice: str
    audio_duration: float
    generation_time: float
    rtf: float  # Real-time factor
    cache_hit: bool
    format: str
    speed: float = 1.0

@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float

class PerformanceMonitor:
    """
    Comprehensive performance monitoring for TTS API
    Tracks RTF, latency, cache performance, and system resources
    """
    
    def __init__(self, max_history: int = None, enable_system_monitoring: bool = None, config=None):
        # Use config values or fallback to defaults
        if config and hasattr(config, 'monitoring'):
            self.max_history = max_history or config.monitoring.max_history
            self.enable_system_monitoring = enable_system_monitoring if enable_system_monitoring is not None else config.monitoring.system_monitoring
            self.monitoring_interval = config.monitoring.monitoring_interval
            self.join_timeout = config.monitoring.join_timeout
        else:
            # Fallback defaults
            self.max_history = max_history or 1000
            self.enable_system_monitoring = enable_system_monitoring if enable_system_monitoring is not None else True
            self.monitoring_interval = 1.0
            self.join_timeout = 5.0
        
        # Performance data storage
        self.metrics: deque = deque(maxlen=max_history)
        self.tts_metrics: deque = deque(maxlen=max_history)
        self.system_metrics: deque = deque(maxlen=max_history)
        
        # Real-time statistics
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_generation_time': 0.0,
            'total_audio_duration': 0.0,
            'avg_rtf': 0.0,
            'min_rtf': None,  # Use None instead of inf for uninitialized values
            'max_rtf': 0.0,
            'avg_latency': 0.0,
            'min_latency': None,  # Use None instead of inf for uninitialized values
            'max_latency': 0.0
        }
        
        # Voice-specific statistics
        self.voice_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'requests': 0,
            'total_generation_time': 0.0,
            'total_audio_duration': 0.0,
            'avg_rtf': 0.0,
            'cache_hits': 0
        })
        
        # Text length analysis
        self.length_buckets = {
            'short': {'range': (0, 50), 'count': 0, 'total_time': 0.0},
            'medium': {'range': (51, 200), 'count': 0, 'total_time': 0.0},
            'long': {'range': (201, 500), 'count': 0, 'total_time': 0.0},
            'very_long': {'range': (501, float('inf')), 'count': 0, 'total_time': 0.0}
        }
        
        # System monitoring
        self.system_monitor_thread: Optional[threading.Thread] = None
        self.stop_monitoring_event = threading.Event()
        self.monitoring_interval = 5.0  # seconds
        
        # Thread safety
        self.stats_lock = threading.RLock()
        
        logger.info("Performance monitor initialized")
    
    def start_monitoring(self):
        """Start system monitoring thread"""
        if not self.enable_system_monitoring:
            return
        
        if self.system_monitor_thread and self.system_monitor_thread.is_alive():
            logger.warning("System monitoring already running")
            return
        
        self.stop_monitoring_event.clear()
        self.system_monitor_thread = threading.Thread(target=self._system_monitor_worker, daemon=True)
        self.system_monitor_thread.start()
        
        logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.stop_monitoring_event.set()
        if self.system_monitor_thread:
            self.system_monitor_thread.join(timeout=self.join_timeout)
        logger.info("System monitoring stopped")
    
    def record_tts_performance(self, tts_data: TTSPerformanceData):
        """Record TTS performance metrics"""
        with self.stats_lock:
            # Create performance metric
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                metric_type='cache_hit' if tts_data.cache_hit else 'tts_generation',
                value=tts_data.generation_time,
                metadata={
                    'text_length': tts_data.text_length,
                    'voice': tts_data.voice,
                    'audio_duration': tts_data.audio_duration,
                    'rtf': tts_data.rtf,
                    'format': tts_data.format,
                    'speed': tts_data.speed
                }
            )
            
            self.metrics.append(metric)
            self.tts_metrics.append(tts_data)
            
            # Update global statistics
            self.stats['total_requests'] += 1
            
            if tts_data.cache_hit:
                self.stats['cache_hits'] += 1
            else:
                self.stats['cache_misses'] += 1
                self.stats['total_generation_time'] += tts_data.generation_time
                self.stats['total_audio_duration'] += tts_data.audio_duration
                
                # Update RTF statistics
                self._update_rtf_stats(tts_data.rtf)
                
                # Update latency statistics
                self._update_latency_stats(tts_data.generation_time)
            
            # Update voice-specific statistics
            self._update_voice_stats(tts_data)
            
            # Update text length analysis
            self._update_length_analysis(tts_data)
    
    def _update_rtf_stats(self, rtf: float):
        """Update RTF statistics with safe calculations"""
        # Import safe division utility
        from LiteTTS.utils.json_sanitizer import safe_division, sanitize_float

        # Sanitize input RTF value
        rtf = sanitize_float(rtf, 0.0)

        # Update min/max RTF with proper None handling
        if self.stats['min_rtf'] is None:
            self.stats['min_rtf'] = rtf
        else:
            self.stats['min_rtf'] = min(self.stats['min_rtf'], rtf)

        self.stats['max_rtf'] = max(self.stats['max_rtf'], rtf)

        # Calculate running average RTF with safe division
        non_cached_requests = self.stats['cache_misses']
        if non_cached_requests > 0:
            total_rtf = self.stats['avg_rtf'] * (non_cached_requests - 1) + rtf
            self.stats['avg_rtf'] = safe_division(total_rtf, non_cached_requests, 0.0)
    
    def _update_latency_stats(self, latency: float):
        """Update latency statistics with safe calculations"""
        # Import safe division utility
        from LiteTTS.utils.json_sanitizer import safe_division, sanitize_float

        # Sanitize input latency value
        latency = sanitize_float(latency, 0.0)

        # Update min/max latency with proper None handling
        if self.stats['min_latency'] is None:
            self.stats['min_latency'] = latency
        else:
            self.stats['min_latency'] = min(self.stats['min_latency'], latency)

        self.stats['max_latency'] = max(self.stats['max_latency'], latency)

        # Calculate running average latency with safe division
        non_cached_requests = self.stats['cache_misses']
        if non_cached_requests > 0:
            total_latency = self.stats['avg_latency'] * (non_cached_requests - 1) + latency
            self.stats['avg_latency'] = safe_division(total_latency, non_cached_requests, 0.0)
    
    def _update_voice_stats(self, tts_data: TTSPerformanceData):
        """Update voice-specific statistics with safe calculations"""
        # Import safe division utility
        from LiteTTS.utils.json_sanitizer import safe_division, sanitize_float

        voice_stat = self.voice_stats[tts_data.voice]
        voice_stat['requests'] += 1

        if tts_data.cache_hit:
            voice_stat['cache_hits'] += 1
        else:
            voice_stat['total_generation_time'] += sanitize_float(tts_data.generation_time, 0.0)
            voice_stat['total_audio_duration'] += sanitize_float(tts_data.audio_duration, 0.0)

            # Update voice RTF with safe division
            non_cached = voice_stat['requests'] - voice_stat['cache_hits']
            if non_cached > 0:
                total_rtf = voice_stat['avg_rtf'] * (non_cached - 1) + sanitize_float(tts_data.rtf, 0.0)
                voice_stat['avg_rtf'] = safe_division(total_rtf, non_cached, 0.0)
    
    def _update_length_analysis(self, tts_data: TTSPerformanceData):
        """Update text length analysis"""
        if tts_data.cache_hit:
            return  # Don't include cached requests in length analysis
        
        text_length = tts_data.text_length
        
        for bucket_name, bucket_data in self.length_buckets.items():
            min_len, max_len = bucket_data['range']
            if min_len <= text_length <= max_len:
                bucket_data['count'] += 1
                bucket_data['total_time'] += tts_data.generation_time
                break
    
    def _system_monitor_worker(self):
        """Background worker for system monitoring"""
        logger.info("System monitoring worker started")
        
        while not self.stop_monitoring_event.is_set():
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                network_io = psutil.net_io_counters()
                
                system_metric = SystemMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_used_mb=memory.used / (1024 * 1024),
                    disk_io_read_mb=disk_io.read_bytes / (1024 * 1024) if disk_io else 0,
                    disk_io_write_mb=disk_io.write_bytes / (1024 * 1024) if disk_io else 0,
                    network_sent_mb=network_io.bytes_sent / (1024 * 1024) if network_io else 0,
                    network_recv_mb=network_io.bytes_recv / (1024 * 1024) if network_io else 0
                )
                
                with self.stats_lock:
                    self.system_metrics.append(system_metric)
                
                # Wait for next interval
                self.stop_monitoring_event.wait(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                self.stop_monitoring_event.wait(self.join_timeout)
        
        logger.info("System monitoring worker stopped")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary with safe calculations"""
        # Import safe division utilities
        from LiteTTS.utils.json_sanitizer import safe_percentage, safe_division, sanitize_float

        with self.stats_lock:
            # Calculate cache hit rate with safe percentage calculation
            total_requests = self.stats['total_requests']
            cache_hit_rate = safe_percentage(self.stats['cache_hits'], total_requests, 0.0)

            # Calculate average generation time per second of audio with safe division
            total_audio = self.stats['total_audio_duration']
            total_gen_time = self.stats['total_generation_time']
            efficiency = safe_division(total_audio, total_gen_time, 0.0)
            
            # Get recent system metrics
            recent_system = None
            if self.system_metrics:
                recent_system = {
                    'cpu_percent': self.system_metrics[-1].cpu_percent,
                    'memory_percent': self.system_metrics[-1].memory_percent,
                    'memory_used_mb': self.system_metrics[-1].memory_used_mb
                }
            
            # Text length analysis with safe division
            length_analysis = {}
            for bucket_name, bucket_data in self.length_buckets.items():
                if bucket_data['count'] > 0:
                    avg_time = safe_division(bucket_data['total_time'], bucket_data['count'], 0.0)
                    length_analysis[bucket_name] = {
                        'range': bucket_data['range'],
                        'count': bucket_data['count'],
                        'avg_generation_time': avg_time
                    }
            
            return {
                'summary': {
                    'total_requests': total_requests,
                    'cache_hit_rate_percent': round(sanitize_float(cache_hit_rate, 0.0), 2),
                    'avg_rtf': round(sanitize_float(self.stats['avg_rtf'], 0.0), 3),
                    'min_rtf': round(self.stats['min_rtf'], 3) if self.stats['min_rtf'] is not None else None,
                    'max_rtf': round(sanitize_float(self.stats['max_rtf'], 0.0), 3),
                    'avg_latency_ms': round(sanitize_float(self.stats['avg_latency'] * 1000, 0.0), 1),
                    'min_latency_ms': round(self.stats['min_latency'] * 1000, 1) if self.stats['min_latency'] is not None else None,
                    'max_latency_ms': round(sanitize_float(self.stats['max_latency'] * 1000, 0.0), 1),
                    'efficiency_ratio': round(sanitize_float(efficiency, 0.0), 2)
                },
                'voice_performance': {
                    voice: {
                        'requests': stats['requests'],
                        'cache_hit_rate_percent': round(safe_percentage(stats['cache_hits'], stats['requests'], 0.0), 2),
                        'avg_rtf': round(sanitize_float(stats['avg_rtf'], 0.0), 3)
                    }
                    for voice, stats in self.voice_stats.items()
                },
                'text_length_analysis': length_analysis,
                'system_metrics': recent_system,
                'monitoring_period': {
                    'start_time': self.metrics[0].timestamp.isoformat() if self.metrics else None,
                    'end_time': self.metrics[-1].timestamp.isoformat() if self.metrics else None,
                    'total_metrics': len(self.metrics)
                }
            }
    
    def get_rtf_trend(self, minutes: int = 30) -> List[Tuple[datetime, float]]:
        """Get RTF trend over specified time period"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.stats_lock:
            trend_data = []
            for tts_data in self.tts_metrics:
                if hasattr(tts_data, 'timestamp'):
                    timestamp = tts_data.timestamp
                else:
                    # Estimate timestamp from metrics
                    for metric in reversed(self.metrics):
                        if (metric.metadata.get('voice') == tts_data.voice and 
                            metric.metadata.get('text_length') == tts_data.text_length):
                            timestamp = metric.timestamp
                            break
                    else:
                        continue
                
                if timestamp >= cutoff_time and not tts_data.cache_hit:
                    trend_data.append((timestamp, tts_data.rtf))
            
            return sorted(trend_data, key=lambda x: x[0])
    
    def export_metrics(self, filepath: str):
        """Export performance metrics to JSON file"""
        with self.stats_lock:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'summary': self.get_performance_summary(),
                'raw_metrics': [
                    {
                        'timestamp': metric.timestamp.isoformat(),
                        'type': metric.metric_type,
                        'value': metric.value,
                        'metadata': metric.metadata
                    }
                    for metric in self.metrics
                ]
            }
            
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Performance metrics exported to {filepath}")
