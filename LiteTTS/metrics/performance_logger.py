#!/usr/bin/env python3
"""
Performance metrics logging system for Kokoro TTS
Tracks token usage, latency, time to first token, and other performance metrics
"""

import time
import logging
import json
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from collections import defaultdict, deque
import statistics
import psutil
import os

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a single TTS request"""
    request_id: str
    timestamp: datetime
    
    # Input metrics
    text_length: int
    token_count: Optional[int] = None
    voice_name: str = ""
    
    # Timing metrics (in seconds)
    total_time: float = 0.0
    preprocessing_time: float = 0.0
    inference_time: float = 0.0
    postprocessing_time: float = 0.0
    time_to_first_token: float = 0.0
    
    # Audio metrics
    audio_duration: float = 0.0
    audio_format: str = ""
    audio_size_bytes: int = 0
    
    # Performance ratios
    real_time_factor: float = 0.0  # inference_time / audio_duration
    throughput_ratio: float = 0.0  # audio_duration / total_time
    
    # System metrics
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_memory_usage_mb: Optional[float] = None
    
    # Quality metrics
    error_occurred: bool = False
    error_message: str = ""
    
    # Additional metadata
    model_name: str = ""
    batch_size: int = 1
    concurrent_requests: int = 1

class PerformanceLogger:
    """Centralized performance metrics logging and analysis"""
    
    def __init__(self, log_file: Optional[str] = None, max_history: int = 10000):
        self.log_file = log_file
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        
        # Performance aggregates
        self.hourly_stats = defaultdict(list)
        self.daily_stats = defaultdict(list)
        
        # System monitoring
        self.process = psutil.Process()
        
    def start_request(self, request_id: str, text: str, voice_name: str = "", 
                     model_name: str = "") -> Dict[str, Any]:
        """Start tracking a new request"""
        with self.lock:
            start_time = time.time()
            request_data = {
                'request_id': request_id,
                'start_time': start_time,
                'text': text,
                'text_length': len(text),
                'voice_name': voice_name,
                'model_name': model_name,
                'stages': {},
                'concurrent_requests': len(self.active_requests) + 1
            }
            self.active_requests[request_id] = request_data
            
            logger.debug(f"Started tracking request {request_id} (concurrent: {request_data['concurrent_requests']})")
            return request_data
    
    def log_stage(self, request_id: str, stage_name: str, duration: float = None):
        """Log completion of a processing stage"""
        with self.lock:
            if request_id not in self.active_requests:
                logger.warning(f"Request {request_id} not found for stage logging")
                return
                
            current_time = time.time()
            request_data = self.active_requests[request_id]
            
            if duration is None:
                # Calculate duration from last stage or start
                last_time = request_data.get('last_stage_time', request_data['start_time'])
                duration = current_time - last_time
            
            request_data['stages'][stage_name] = duration
            request_data['last_stage_time'] = current_time
            
            logger.debug(f"Request {request_id} - {stage_name}: {duration:.3f}s")
    
    def log_token_metrics(self, request_id: str, token_count: int, time_to_first_token: float):
        """Log token-related metrics"""
        with self.lock:
            if request_id in self.active_requests:
                self.active_requests[request_id]['token_count'] = token_count
                self.active_requests[request_id]['time_to_first_token'] = time_to_first_token
                logger.debug(f"Request {request_id} - Tokens: {token_count}, TTFT: {time_to_first_token:.3f}s")
    
    def log_audio_metrics(self, request_id: str, duration: float, format_type: str, 
                         size_bytes: int):
        """Log audio output metrics"""
        with self.lock:
            if request_id in self.active_requests:
                request_data = self.active_requests[request_id]
                request_data['audio_duration'] = duration
                request_data['audio_format'] = format_type
                request_data['audio_size_bytes'] = size_bytes
                logger.debug(f"Request {request_id} - Audio: {duration:.2f}s, {size_bytes} bytes")
    
    def finish_request(self, request_id: str, error_message: str = "") -> Optional[PerformanceMetrics]:
        """Complete tracking and generate final metrics"""
        with self.lock:
            if request_id not in self.active_requests:
                logger.warning(f"Request {request_id} not found for completion")
                return None
                
            request_data = self.active_requests.pop(request_id)
            end_time = time.time()
            
            # Calculate total time
            total_time = end_time - request_data['start_time']
            
            # Extract stage timings
            stages = request_data.get('stages', {})
            preprocessing_time = stages.get('preprocessing', 0.0)
            inference_time = stages.get('inference', 0.0)
            postprocessing_time = stages.get('postprocessing', 0.0)
            
            # Calculate performance ratios
            audio_duration = request_data.get('audio_duration', 0.0)
            real_time_factor = inference_time / audio_duration if audio_duration > 0 else 0.0
            throughput_ratio = audio_duration / total_time if total_time > 0 else 0.0
            
            # Get system metrics
            cpu_usage = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_usage_mb = memory_info.rss / 1024 / 1024
            
            # Try to get GPU memory usage (if available)
            gpu_memory_mb = self._get_gpu_memory_usage()
            
            # Create metrics object
            metrics = PerformanceMetrics(
                request_id=request_id,
                timestamp=datetime.now(timezone.utc),
                text_length=request_data['text_length'],
                token_count=request_data.get('token_count'),
                voice_name=request_data.get('voice_name', ''),
                total_time=total_time,
                preprocessing_time=preprocessing_time,
                inference_time=inference_time,
                postprocessing_time=postprocessing_time,
                time_to_first_token=request_data.get('time_to_first_token', 0.0),
                audio_duration=audio_duration,
                audio_format=request_data.get('audio_format', ''),
                audio_size_bytes=request_data.get('audio_size_bytes', 0),
                real_time_factor=real_time_factor,
                throughput_ratio=throughput_ratio,
                cpu_usage_percent=cpu_usage,
                memory_usage_mb=memory_usage_mb,
                gpu_memory_usage_mb=gpu_memory_mb,
                error_occurred=bool(error_message),
                error_message=error_message,
                model_name=request_data.get('model_name', ''),
                concurrent_requests=request_data.get('concurrent_requests', 1)
            )
            
            # Store in history
            self.metrics_history.append(metrics)
            
            # Update aggregates
            self._update_aggregates(metrics)
            
            # Log to file if configured
            if self.log_file:
                self._write_to_file(metrics)
            
            logger.info(f"Request {request_id} completed - RTF: {real_time_factor:.3f}, "
                       f"Total: {total_time:.3f}s, Audio: {audio_duration:.2f}s")
            
            return metrics
    
    def _get_gpu_memory_usage(self) -> Optional[float]:
        """Get GPU memory usage if available"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].memoryUsed
        except ImportError:
            pass
        return None
    
    def _update_aggregates(self, metrics: PerformanceMetrics):
        """Update hourly and daily aggregates"""
        hour_key = metrics.timestamp.strftime('%Y-%m-%d-%H')
        day_key = metrics.timestamp.strftime('%Y-%m-%d')
        
        self.hourly_stats[hour_key].append(metrics)
        self.daily_stats[day_key].append(metrics)
    
    def _write_to_file(self, metrics: PerformanceMetrics):
        """Write metrics to log file"""
        try:
            with open(self.log_file, 'a') as f:
                json.dump(asdict(metrics), f, default=str)
                f.write('\n')
        except Exception as e:
            logger.error(f"Failed to write metrics to file: {e}")
    
    def get_recent_stats(self, minutes: int = 60) -> Dict[str, Any]:
        """Get statistics for recent requests"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (minutes * 60)
        
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp.timestamp() > cutoff_time
        ]
        
        if not recent_metrics:
            return {"message": "No recent requests"}
        
        # Calculate statistics
        rtf_values = [m.real_time_factor for m in recent_metrics if m.real_time_factor > 0]
        total_times = [m.total_time for m in recent_metrics]
        ttft_values = [m.time_to_first_token for m in recent_metrics if m.time_to_first_token > 0]
        
        stats = {
            "period_minutes": minutes,
            "total_requests": len(recent_metrics),
            "successful_requests": len([m for m in recent_metrics if not m.error_occurred]),
            "error_rate": len([m for m in recent_metrics if m.error_occurred]) / len(recent_metrics),
            "performance": {
                "avg_rtf": statistics.mean(rtf_values) if rtf_values else 0,
                "median_rtf": statistics.median(rtf_values) if rtf_values else 0,
                "avg_total_time": statistics.mean(total_times),
                "median_total_time": statistics.median(total_times),
                "avg_ttft": statistics.mean(ttft_values) if ttft_values else 0,
                "p95_total_time": statistics.quantiles(total_times, n=20)[18] if len(total_times) >= 20 else max(total_times) if total_times else 0
            },
            "system": {
                "avg_cpu_usage": statistics.mean([m.cpu_usage_percent for m in recent_metrics]),
                "avg_memory_mb": statistics.mean([m.memory_usage_mb for m in recent_metrics]),
                "max_concurrent": max([m.concurrent_requests for m in recent_metrics])
            }
        }
        
        return stats
    
    def export_metrics(self, filename: str, format_type: str = "json"):
        """Export all metrics to file"""
        try:
            if format_type == "json":
                with open(filename, 'w') as f:
                    json.dump([asdict(m) for m in self.metrics_history], f, default=str, indent=2)
            elif format_type == "csv":
                import csv
                with open(filename, 'w', newline='') as f:
                    if self.metrics_history:
                        writer = csv.DictWriter(f, fieldnames=asdict(self.metrics_history[0]).keys())
                        writer.writeheader()
                        for metrics in self.metrics_history:
                            writer.writerow(asdict(metrics))
            
            logger.info(f"Exported {len(self.metrics_history)} metrics to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")

# Global performance logger instance
performance_logger = PerformanceLogger()
