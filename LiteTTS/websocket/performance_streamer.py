"""
Performance Streamer for LiteTTS WebSocket

This module provides real-time performance metrics streaming to WebSocket
clients, including RTF, memory usage, processing metrics, and system status.
"""

import asyncio
import logging
import time
import psutil
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import deque

from .websocket_manager import WebSocketManager, WebSocketMessage, MessageType

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: float
    rtf: float
    memory_usage_mb: float
    memory_percent: float
    cpu_percent: float
    active_requests: int
    total_requests: int
    cache_hit_rate: float
    processing_time_ms: float
    queue_size: int
    uptime_seconds: float
    voices_loaded: int
    system_load: List[float]  # 1, 5, 15 minute load averages


@dataclass
class SystemStatus:
    """System status information"""
    timestamp: float
    status: str  # "healthy", "warning", "error"
    server_uptime: float
    total_memory_gb: float
    available_memory_gb: float
    disk_usage_percent: float
    temperature_celsius: Optional[float]
    gpu_available: bool
    gpu_memory_mb: Optional[float]
    active_connections: int
    error_rate: float
    last_error: Optional[str]


class PerformanceStreamer:
    """
    Real-time performance metrics streamer for WebSocket clients.
    
    Collects system and application performance metrics and streams
    them to connected dashboard clients via WebSocket.
    """
    
    def __init__(self, 
                 websocket_manager: WebSocketManager,
                 update_interval: float = 1.0,
                 history_size: int = 300):
        """
        Initialize PerformanceStreamer.
        
        Args:
            websocket_manager: WebSocket manager instance
            update_interval: Metrics update interval in seconds
            history_size: Number of historical metrics to keep
        """
        self.websocket_manager = websocket_manager
        self.update_interval = update_interval
        self.history_size = history_size
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Metrics storage
        self.metrics_history: deque = deque(maxlen=history_size)
        self.current_metrics: Optional[PerformanceMetrics] = None
        self.current_status: Optional[SystemStatus] = None
        
        # Application metrics (to be updated by TTS system)
        self.app_metrics = {
            "rtf": 0.0,
            "active_requests": 0,
            "total_requests": 0,
            "cache_hit_rate": 0.0,
            "processing_time_ms": 0.0,
            "queue_size": 0,
            "voices_loaded": 0,
            "error_rate": 0.0,
            "last_error": None
        }
        
        # System info
        self.start_time = time.time()
        self.last_cpu_times = None
        
        # Background tasks
        self._streaming_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Thread-safe lock for metrics updates
        self._metrics_lock = threading.Lock()
    
    async def start(self):
        """Start the performance streamer."""
        if self._running:
            return
        
        self._running = True
        self.logger.info("Starting PerformanceStreamer...")
        
        # Start streaming task
        self._streaming_task = asyncio.create_task(self._streaming_loop())
        
        self.logger.info("✅ PerformanceStreamer started")
    
    async def stop(self):
        """Stop the performance streamer."""
        if not self._running:
            return
        
        self._running = False
        self.logger.info("Stopping PerformanceStreamer...")
        
        # Cancel streaming task
        if self._streaming_task:
            self._streaming_task.cancel()
            try:
                await self._streaming_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("PerformanceStreamer stopped")
    
    def update_app_metrics(self, **metrics):
        """
        Update application-specific metrics.
        
        Args:
            **metrics: Metric name-value pairs to update
        """
        with self._metrics_lock:
            for key, value in metrics.items():
                if key in self.app_metrics:
                    self.app_metrics[key] = value
    
    def increment_requests(self):
        """Increment total request counter."""
        with self._metrics_lock:
            self.app_metrics["total_requests"] += 1
    
    def set_active_requests(self, count: int):
        """Set current active request count."""
        with self._metrics_lock:
            self.app_metrics["active_requests"] = count
    
    def update_rtf(self, rtf: float):
        """Update current RTF (Real-Time Factor)."""
        with self._metrics_lock:
            self.app_metrics["rtf"] = rtf
    
    def update_processing_time(self, time_ms: float):
        """Update last processing time."""
        with self._metrics_lock:
            self.app_metrics["processing_time_ms"] = time_ms
    
    def report_error(self, error_message: str):
        """Report an error for metrics tracking."""
        with self._metrics_lock:
            self.app_metrics["last_error"] = error_message
            # Simple error rate calculation with safe division
            if self.app_metrics["total_requests"] > 0:
                from LiteTTS.utils.json_sanitizer import safe_division
                error_count = getattr(self, '_error_count', 0) + 1
                self._error_count = error_count
                self.app_metrics["error_rate"] = safe_division(error_count, self.app_metrics["total_requests"], 0.0)
    
    def _collect_system_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics."""
        current_time = time.time()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_usage_mb = (memory.total - memory.available) / (1024 * 1024)
        memory_percent = memory.percent
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        
        # System load (Unix-like systems)
        try:
            system_load = list(psutil.getloadavg())
        except (AttributeError, OSError):
            system_load = [0.0, 0.0, 0.0]
        
        # Application metrics (thread-safe copy)
        with self._metrics_lock:
            app_metrics_copy = self.app_metrics.copy()
        
        # Create metrics snapshot
        metrics = PerformanceMetrics(
            timestamp=current_time,
            rtf=app_metrics_copy["rtf"],
            memory_usage_mb=memory_usage_mb,
            memory_percent=memory_percent,
            cpu_percent=cpu_percent,
            active_requests=app_metrics_copy["active_requests"],
            total_requests=app_metrics_copy["total_requests"],
            cache_hit_rate=app_metrics_copy["cache_hit_rate"],
            processing_time_ms=app_metrics_copy["processing_time_ms"],
            queue_size=app_metrics_copy["queue_size"],
            uptime_seconds=current_time - self.start_time,
            voices_loaded=app_metrics_copy["voices_loaded"],
            system_load=system_load
        )
        
        return metrics
    
    def _collect_system_status(self) -> SystemStatus:
        """Collect current system status information."""
        current_time = time.time()
        
        # Memory info
        memory = psutil.virtual_memory()
        total_memory_gb = memory.total / (1024**3)
        available_memory_gb = memory.available / (1024**3)
        
        # Disk usage
        try:
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
        except:
            disk_usage_percent = 0.0
        
        # Temperature (if available)
        temperature = None
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Get first available temperature sensor
                for sensor_name, sensor_list in temps.items():
                    if sensor_list:
                        temperature = sensor_list[0].current
                        break
        except:
            pass
        
        # GPU info (basic check)
        gpu_available = False
        gpu_memory_mb = None
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_available = True
                gpu_memory_mb = gpus[0].memoryUsed
        except ImportError:
            pass
        
        # Application status
        with self._metrics_lock:
            error_rate = self.app_metrics["error_rate"]
            last_error = self.app_metrics["last_error"]
        
        # Determine overall status
        status = "healthy"
        if error_rate > 0.1:  # 10% error rate
            status = "error"
        elif memory.percent > 90 or disk_usage_percent > 90:
            status = "warning"
        elif cpu_percent > 90:
            status = "warning"
        
        # WebSocket connections
        active_connections = self.websocket_manager.get_client_count()
        
        status_info = SystemStatus(
            timestamp=current_time,
            status=status,
            server_uptime=current_time - self.start_time,
            total_memory_gb=total_memory_gb,
            available_memory_gb=available_memory_gb,
            disk_usage_percent=disk_usage_percent,
            temperature_celsius=temperature,
            gpu_available=gpu_available,
            gpu_memory_mb=gpu_memory_mb,
            active_connections=active_connections,
            error_rate=error_rate,
            last_error=last_error
        )
        
        return status_info
    
    async def _streaming_loop(self):
        """Main streaming loop for performance metrics."""
        while self._running:
            try:
                # Collect metrics
                metrics = self._collect_system_metrics()
                status = self._collect_system_status()
                
                # Store current metrics
                self.current_metrics = metrics
                self.current_status = status
                self.metrics_history.append(metrics)
                
                # Create WebSocket messages
                performance_message = WebSocketMessage(
                    type=MessageType.PERFORMANCE_UPDATE,
                    data=asdict(metrics),
                    timestamp=metrics.timestamp
                )
                
                status_message = WebSocketMessage(
                    type=MessageType.SYSTEM_STATUS,
                    data=asdict(status),
                    timestamp=status.timestamp
                )
                
                # Broadcast to dashboard clients
                await self.websocket_manager.broadcast(performance_message, client_type="dashboard")
                await self.websocket_manager.broadcast(status_message, client_type="dashboard")
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Streaming loop error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics."""
        return self.current_metrics
    
    def get_current_status(self) -> Optional[SystemStatus]:
        """Get current system status."""
        return self.current_status
    
    def get_metrics_history(self, limit: Optional[int] = None) -> List[PerformanceMetrics]:
        """
        Get historical performance metrics.
        
        Args:
            limit: Maximum number of metrics to return
            
        Returns:
            List of PerformanceMetrics in chronological order
        """
        history = list(self.metrics_history)
        if limit:
            history = history[-limit:]
        return history
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data.
        
        Returns:
            Dictionary with current metrics, status, and recent history
        """
        return {
            "current_metrics": asdict(self.current_metrics) if self.current_metrics else None,
            "current_status": asdict(self.current_status) if self.current_status else None,
            "recent_history": [asdict(m) for m in self.get_metrics_history(60)],  # Last 60 data points
            "websocket_stats": self.websocket_manager.get_stats(),
            "update_interval": self.update_interval,
            "history_size": self.history_size
        }


def create_performance_streamer(websocket_manager: WebSocketManager, 
                              update_interval: float = 1.0) -> PerformanceStreamer:
    """
    Factory function to create PerformanceStreamer instance.
    
    Args:
        websocket_manager: WebSocket manager instance
        update_interval: Metrics update interval in seconds
        
    Returns:
        Configured PerformanceStreamer instance
    """
    return PerformanceStreamer(websocket_manager, update_interval)
