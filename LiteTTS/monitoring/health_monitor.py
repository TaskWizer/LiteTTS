#!/usr/bin/env python3
"""
Comprehensive health monitoring system for Kokoro ONNX TTS API
"""

import time
import psutil
import logging
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class HealthStatus:
    """Health status for a component"""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    last_check: datetime
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class SystemHealth:
    """Overall system health status"""
    overall_status: str
    timestamp: datetime
    components: List[HealthStatus]
    system_metrics: Dict[str, Any]
    uptime_seconds: float

class HealthMonitor:
    """Comprehensive health monitoring system"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.start_time = time.time()
        self.last_health_check = None
        self.health_history: List[SystemHealth] = []
        self.max_history = 100
        
        # Component health checkers
        self.health_checkers = {}
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # System metrics
        self.process = psutil.Process()
        
    def register_health_checker(self, name: str, checker_func):
        """Register a health checker function"""
        self.health_checkers[name] = checker_func
        logger.info(f"Registered health checker: {name}")
    
    def start_monitoring(self):
        """Start background health monitoring"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logger.warning("Health monitoring already running")
            return
        
        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Health monitoring started")
    
    def stop_monitoring_service(self):
        """Stop background health monitoring"""
        self.stop_monitoring.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while not self.stop_monitoring.is_set():
            try:
                self.perform_health_check()
                self.stop_monitoring.wait(self.check_interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                self.stop_monitoring.wait(self.check_interval)
    
    def perform_health_check(self) -> SystemHealth:
        """Perform comprehensive health check"""
        check_start = time.time()
        component_statuses = []
        
        # Check each registered component
        for name, checker_func in self.health_checkers.items():
            try:
                component_start = time.time()
                status = checker_func()
                response_time = (time.time() - component_start) * 1000
                
                if isinstance(status, dict):
                    health_status = HealthStatus(
                        name=name,
                        status=status.get('status', 'unknown'),
                        message=status.get('message', ''),
                        last_check=datetime.now(),
                        response_time_ms=response_time,
                        details=status.get('details')
                    )
                else:
                    health_status = HealthStatus(
                        name=name,
                        status='healthy' if status else 'unhealthy',
                        message='OK' if status else 'Check failed',
                        last_check=datetime.now(),
                        response_time_ms=response_time
                    )
                
                component_statuses.append(health_status)
                
            except Exception as e:
                component_statuses.append(HealthStatus(
                    name=name,
                    status='unhealthy',
                    message=f'Health check failed: {str(e)}',
                    last_check=datetime.now(),
                    response_time_ms=(time.time() - component_start) * 1000 if 'component_start' in locals() else None
                ))
        
        # Get system metrics
        system_metrics = self._get_system_metrics()
        
        # Determine overall status
        overall_status = self._determine_overall_status(component_statuses, system_metrics)
        
        # Create system health object
        system_health = SystemHealth(
            overall_status=overall_status,
            timestamp=datetime.now(),
            components=component_statuses,
            system_metrics=system_metrics,
            uptime_seconds=time.time() - self.start_time
        )
        
        # Store in history
        self.health_history.append(system_health)
        if len(self.health_history) > self.max_history:
            self.health_history.pop(0)
        
        self.last_health_check = system_health
        
        # Log health status
        check_duration = (time.time() - check_start) * 1000
        logger.debug(f"Health check completed in {check_duration:.1f}ms - Status: {overall_status}")
        
        return system_health
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU and memory
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            # System-wide metrics
            system_cpu = psutil.cpu_percent(interval=0.1)
            system_memory = psutil.virtual_memory()
            disk_usage = psutil.disk_usage('/')
            
            # Network stats (if available)
            try:
                network_io = psutil.net_io_counters()
                network_stats = {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv
                }
            except:
                network_stats = None
            
            return {
                'process': {
                    'cpu_percent': cpu_percent,
                    'memory_rss_mb': memory_info.rss / 1024 / 1024,
                    'memory_vms_mb': memory_info.vms / 1024 / 1024,
                    'memory_percent': memory_percent,
                    'num_threads': self.process.num_threads(),
                    'num_fds': self.process.num_fds() if hasattr(self.process, 'num_fds') else None
                },
                'system': {
                    'cpu_percent': system_cpu,
                    'memory_total_gb': system_memory.total / 1024 / 1024 / 1024,
                    'memory_available_gb': system_memory.available / 1024 / 1024 / 1024,
                    'memory_percent': system_memory.percent,
                    'disk_total_gb': disk_usage.total / 1024 / 1024 / 1024,
                    'disk_free_gb': disk_usage.free / 1024 / 1024 / 1024,
                    'disk_percent': (disk_usage.used / disk_usage.total) * 100
                },
                'network': network_stats,
                'uptime_seconds': time.time() - self.start_time
            }
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {'error': str(e)}
    
    def _determine_overall_status(self, components: List[HealthStatus], 
                                 system_metrics: Dict[str, Any]) -> str:
        """Determine overall system health status"""
        # Check component health
        unhealthy_components = [c for c in components if c.status == 'unhealthy']
        degraded_components = [c for c in components if c.status == 'degraded']
        
        # Check system resource thresholds
        system_issues = []
        
        try:
            process_metrics = system_metrics.get('process', {})
            system_wide = system_metrics.get('system', {})
            
            # Memory thresholds
            if process_metrics.get('memory_percent', 0) > 90:
                system_issues.append('High process memory usage')
            if system_wide.get('memory_percent', 0) > 95:
                system_issues.append('High system memory usage')
            
            # CPU thresholds
            if process_metrics.get('cpu_percent', 0) > 80:
                system_issues.append('High process CPU usage')
            if system_wide.get('cpu_percent', 0) > 90:
                system_issues.append('High system CPU usage')
            
            # Disk thresholds
            if system_wide.get('disk_percent', 0) > 90:
                system_issues.append('Low disk space')
                
        except Exception as e:
            logger.error(f"Error checking system thresholds: {e}")
        
        # Determine status
        if unhealthy_components or system_issues:
            return 'unhealthy'
        elif degraded_components:
            return 'degraded'
        else:
            return 'healthy'
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        if not self.last_health_check:
            # Perform immediate health check
            self.last_health_check = self.perform_health_check()
        
        return {
            'status': self.last_health_check.overall_status,
            'timestamp': self.last_health_check.timestamp.isoformat(),
            'uptime_seconds': self.last_health_check.uptime_seconds,
            'components': [asdict(c) for c in self.last_health_check.components],
            'system_metrics': self.last_health_check.system_metrics
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get simplified health summary"""
        if not self.last_health_check:
            self.last_health_check = self.perform_health_check()
        
        return {
            'status': self.last_health_check.overall_status,
            'timestamp': self.last_health_check.timestamp.isoformat(),
            'uptime_seconds': self.last_health_check.uptime_seconds,
            'components_healthy': len([c for c in self.last_health_check.components if c.status == 'healthy']),
            'components_total': len(self.last_health_check.components),
            'memory_usage_mb': self.last_health_check.system_metrics.get('process', {}).get('memory_rss_mb', 0),
            'cpu_usage_percent': self.last_health_check.system_metrics.get('process', {}).get('cpu_percent', 0)
        }
    
    def export_health_history(self, filename: str):
        """Export health history to file"""
        try:
            with open(filename, 'w') as f:
                json.dump([asdict(h) for h in self.health_history], f, default=str, indent=2)
            logger.info(f"Exported health history to {filename}")
        except Exception as e:
            logger.error(f"Failed to export health history: {e}")

# Global health monitor instance
health_monitor = HealthMonitor()

# Default health checkers
def check_model_health():
    """Check if TTS model is loaded and functional"""
    try:
        # This would be called from the main app with access to the model
        # For now, return a basic check
        return {
            'status': 'healthy',
            'message': 'Model health check not implemented',
            'details': {'note': 'Requires integration with main app'}
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Model check failed: {str(e)}'
        }

def check_disk_space():
    """Check available disk space"""
    try:
        disk_usage = psutil.disk_usage('/')
        free_percent = (disk_usage.free / disk_usage.total) * 100
        
        if free_percent < 5:
            status = 'unhealthy'
            message = f'Critical: Only {free_percent:.1f}% disk space remaining'
        elif free_percent < 15:
            status = 'degraded'
            message = f'Warning: Only {free_percent:.1f}% disk space remaining'
        else:
            status = 'healthy'
            message = f'Disk space OK: {free_percent:.1f}% free'
        
        return {
            'status': status,
            'message': message,
            'details': {
                'free_gb': disk_usage.free / 1024 / 1024 / 1024,
                'total_gb': disk_usage.total / 1024 / 1024 / 1024,
                'free_percent': free_percent
            }
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Disk check failed: {str(e)}'
        }

# Register default health checkers
health_monitor.register_health_checker('model', check_model_health)
health_monitor.register_health_checker('disk_space', check_disk_space)