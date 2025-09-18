#!/usr/bin/env python3
"""
Whisper Performance Monitoring and Optimization Framework
Provides comprehensive monitoring, alerting, and continuous optimization for Whisper alternatives in production
"""

import time
import json
import logging
import threading
import psutil
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for Whisper inference"""
    timestamp: datetime
    model_name: str
    audio_duration: float
    processing_time: float
    rtf: float
    memory_usage_mb: float
    cpu_usage_percent: float
    queue_size: int
    concurrent_requests: int
    error_occurred: bool = False
    error_message: Optional[str] = None

@dataclass
class AlertThresholds:
    """Alert thresholds for performance monitoring"""
    max_rtf: float = 1.0
    max_memory_mb: float = 3000
    max_cpu_percent: float = 90
    max_queue_size: int = 10
    max_error_rate: float = 0.05  # 5% error rate
    max_response_time_ms: float = 30000  # 30 seconds

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    priority: str  # 'high', 'medium', 'low'
    category: str  # 'model', 'hardware', 'configuration'
    description: str
    action: str
    expected_improvement: str
    implementation_effort: str

class PerformanceDatabase:
    """SQLite database for performance metrics storage"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize performance database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    audio_duration REAL NOT NULL,
                    processing_time REAL NOT NULL,
                    rtf REAL NOT NULL,
                    memory_usage_mb REAL NOT NULL,
                    cpu_usage_percent REAL NOT NULL,
                    queue_size INTEGER NOT NULL,
                    concurrent_requests INTEGER NOT NULL,
                    error_occurred BOOLEAN NOT NULL,
                    error_message TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON performance_metrics(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_name ON performance_metrics(model_name)
            """)
            
    def store_metrics(self, metrics: PerformanceMetrics):
        """Store performance metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO performance_metrics (
                    timestamp, model_name, audio_duration, processing_time, rtf,
                    memory_usage_mb, cpu_usage_percent, queue_size, concurrent_requests,
                    error_occurred, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp.isoformat(),
                metrics.model_name,
                metrics.audio_duration,
                metrics.processing_time,
                metrics.rtf,
                metrics.memory_usage_mb,
                metrics.cpu_usage_percent,
                metrics.queue_size,
                metrics.concurrent_requests,
                metrics.error_occurred,
                metrics.error_message
            ))
            
    def get_metrics(self, start_time: datetime, end_time: datetime, 
                   model_name: Optional[str] = None) -> List[PerformanceMetrics]:
        """Retrieve performance metrics for time range"""
        query = """
            SELECT * FROM performance_metrics 
            WHERE timestamp >= ? AND timestamp <= ?
        """
        params = [start_time.isoformat(), end_time.isoformat()]
        
        if model_name:
            query += " AND model_name = ?"
            params.append(model_name)
            
        query += " ORDER BY timestamp"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_metrics(row) for row in rows]
            
    def _row_to_metrics(self, row) -> PerformanceMetrics:
        """Convert database row to PerformanceMetrics"""
        return PerformanceMetrics(
            timestamp=datetime.fromisoformat(row[1]),
            model_name=row[2],
            audio_duration=row[3],
            processing_time=row[4],
            rtf=row[5],
            memory_usage_mb=row[6],
            cpu_usage_percent=row[7],
            queue_size=row[8],
            concurrent_requests=row[9],
            error_occurred=bool(row[10]),
            error_message=row[11]
        )

class AlertManager:
    """Manages performance alerts and notifications"""
    
    def __init__(self, thresholds: AlertThresholds):
        self.thresholds = thresholds
        self.alert_callbacks: List[Callable[[str, str, Dict[str, Any]], None]] = []
        self.alert_history = deque(maxlen=1000)
        
    def add_alert_callback(self, callback: Callable[[str, str, Dict[str, Any]], None]):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
        
    def check_metrics(self, metrics: PerformanceMetrics):
        """Check metrics against thresholds and trigger alerts"""
        alerts = []
        
        # RTF threshold
        if metrics.rtf > self.thresholds.max_rtf:
            alerts.append({
                'type': 'rtf_exceeded',
                'severity': 'high',
                'message': f"RTF {metrics.rtf:.3f} exceeds threshold {self.thresholds.max_rtf}",
                'value': metrics.rtf,
                'threshold': self.thresholds.max_rtf
            })
            
        # Memory threshold
        if metrics.memory_usage_mb > self.thresholds.max_memory_mb:
            alerts.append({
                'type': 'memory_exceeded',
                'severity': 'high',
                'message': f"Memory usage {metrics.memory_usage_mb:.1f}MB exceeds threshold {self.thresholds.max_memory_mb}MB",
                'value': metrics.memory_usage_mb,
                'threshold': self.thresholds.max_memory_mb
            })
            
        # CPU threshold
        if metrics.cpu_usage_percent > self.thresholds.max_cpu_percent:
            alerts.append({
                'type': 'cpu_exceeded',
                'severity': 'medium',
                'message': f"CPU usage {metrics.cpu_usage_percent:.1f}% exceeds threshold {self.thresholds.max_cpu_percent}%",
                'value': metrics.cpu_usage_percent,
                'threshold': self.thresholds.max_cpu_percent
            })
            
        # Queue size threshold
        if metrics.queue_size > self.thresholds.max_queue_size:
            alerts.append({
                'type': 'queue_exceeded',
                'severity': 'medium',
                'message': f"Queue size {metrics.queue_size} exceeds threshold {self.thresholds.max_queue_size}",
                'value': metrics.queue_size,
                'threshold': self.thresholds.max_queue_size
            })
            
        # Process alerts
        for alert in alerts:
            self._trigger_alert(alert, metrics)
            
    def _trigger_alert(self, alert: Dict[str, Any], metrics: PerformanceMetrics):
        """Trigger alert notifications"""
        alert_data = {
            'timestamp': metrics.timestamp.isoformat(),
            'model_name': metrics.model_name,
            'alert': alert,
            'metrics': asdict(metrics)
        }
        
        self.alert_history.append(alert_data)
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert['type'], alert['severity'], alert_data)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

class OptimizationEngine:
    """Analyzes performance data and provides optimization recommendations"""
    
    def __init__(self, db: PerformanceDatabase):
        self.db = db
        
    def analyze_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze performance over specified time period"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        metrics = self.db.get_metrics(start_time, end_time)
        
        if not metrics:
            return {'error': 'No metrics available for analysis'}
            
        # Calculate statistics
        rtfs = [m.rtf for m in metrics if not m.error_occurred]
        memory_usage = [m.memory_usage_mb for m in metrics if not m.error_occurred]
        processing_times = [m.processing_time for m in metrics if not m.error_occurred]
        
        error_rate = sum(1 for m in metrics if m.error_occurred) / len(metrics)
        
        analysis = {
            'time_period': f"{hours} hours",
            'total_requests': len(metrics),
            'error_rate': error_rate,
            'rtf_stats': {
                'mean': np.mean(rtfs) if rtfs else 0,
                'median': np.median(rtfs) if rtfs else 0,
                'p95': np.percentile(rtfs, 95) if rtfs else 0,
                'p99': np.percentile(rtfs, 99) if rtfs else 0,
                'max': np.max(rtfs) if rtfs else 0
            },
            'memory_stats': {
                'mean': np.mean(memory_usage) if memory_usage else 0,
                'median': np.median(memory_usage) if memory_usage else 0,
                'p95': np.percentile(memory_usage, 95) if memory_usage else 0,
                'max': np.max(memory_usage) if memory_usage else 0
            },
            'processing_time_stats': {
                'mean': np.mean(processing_times) if processing_times else 0,
                'median': np.median(processing_times) if processing_times else 0,
                'p95': np.percentile(processing_times, 95) if processing_times else 0
            }
        }
        
        return analysis
        
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []
        
        # RTF recommendations
        if analysis.get('rtf_stats', {}).get('p95', 0) > 1.0:
            recommendations.append(OptimizationRecommendation(
                priority='high',
                category='model',
                description='RTF P95 exceeds 1.0, indicating performance issues',
                action='Consider switching to faster model variant or enable quantization',
                expected_improvement='30-50% RTF reduction',
                implementation_effort='medium'
            ))
            
        # Memory recommendations
        if analysis.get('memory_stats', {}).get('p95', 0) > 2500:
            recommendations.append(OptimizationRecommendation(
                priority='high',
                category='model',
                description='Memory usage approaching limits',
                action='Enable INT8 quantization or use smaller model',
                expected_improvement='40-60% memory reduction',
                implementation_effort='low'
            ))
            
        # Error rate recommendations
        if analysis.get('error_rate', 0) > 0.02:
            recommendations.append(OptimizationRecommendation(
                priority='high',
                category='configuration',
                description='Error rate above acceptable threshold',
                action='Investigate error patterns and adjust timeout/retry settings',
                expected_improvement='Reduce error rate to <1%',
                implementation_effort='medium'
            ))
            
        # Processing time recommendations
        if analysis.get('processing_time_stats', {}).get('p95', 0) > 20:
            recommendations.append(OptimizationRecommendation(
                priority='medium',
                category='hardware',
                description='Processing times indicate potential CPU bottleneck',
                action='Consider CPU upgrade or enable multi-threading',
                expected_improvement='20-40% processing time reduction',
                implementation_effort='high'
            ))
            
        return recommendations

class WhisperPerformanceMonitor:
    """Main performance monitoring system for Whisper alternatives"""
    
    def __init__(self, db_path: str = "whisper_performance.db", 
                 thresholds: Optional[AlertThresholds] = None):
        self.db = PerformanceDatabase(db_path)
        self.thresholds = thresholds or AlertThresholds()
        self.alert_manager = AlertManager(self.thresholds)
        self.optimization_engine = OptimizationEngine(self.db)
        
        # Monitoring state
        self.monitoring = False
        self.current_requests = 0
        self.request_queue_size = 0
        
        # Background tasks
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        logger.info("WhisperPerformanceMonitor initialized")
        
    def record_inference(self, model_name: str, audio_duration: float, 
                        processing_time: float, memory_usage_mb: float,
                        error_occurred: bool = False, error_message: Optional[str] = None):
        """Record inference performance metrics"""
        rtf = processing_time / audio_duration if audio_duration > 0 else float('inf')
        
        # Get current system metrics
        cpu_usage = psutil.cpu_percent()
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            model_name=model_name,
            audio_duration=audio_duration,
            processing_time=processing_time,
            rtf=rtf,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage,
            queue_size=self.request_queue_size,
            concurrent_requests=self.current_requests,
            error_occurred=error_occurred,
            error_message=error_message
        )
        
        # Store metrics
        self.db.store_metrics(metrics)
        
        # Check for alerts
        self.alert_manager.check_metrics(metrics)
        
        logger.debug(f"Recorded metrics: {model_name}, RTF={rtf:.3f}, Memory={memory_usage_mb:.1f}MB")
        
    def start_request(self):
        """Mark start of a new request"""
        self.current_requests += 1
        
    def end_request(self):
        """Mark end of a request"""
        self.current_requests = max(0, self.current_requests - 1)
        
    def set_queue_size(self, size: int):
        """Update current queue size"""
        self.request_queue_size = size
        
    def add_alert_callback(self, callback: Callable[[str, str, Dict[str, Any]], None]):
        """Add alert notification callback"""
        self.alert_manager.add_alert_callback(callback)
        
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        analysis = self.optimization_engine.analyze_performance(hours)
        recommendations = self.optimization_engine.generate_recommendations(analysis)
        
        return {
            'analysis': analysis,
            'recommendations': [asdict(rec) for rec in recommendations],
            'current_status': {
                'active_requests': self.current_requests,
                'queue_size': self.request_queue_size,
                'monitoring_active': self.monitoring
            },
            'thresholds': asdict(self.thresholds),
            'generated_at': datetime.now().isoformat()
        }
        
    def start_continuous_monitoring(self, interval_seconds: int = 60):
        """Start continuous performance monitoring"""
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    # Generate periodic reports
                    report = self.get_performance_report(hours=1)
                    
                    # Log summary
                    analysis = report['analysis']
                    if 'rtf_stats' in analysis:
                        logger.info(f"Performance summary - RTF P95: {analysis['rtf_stats']['p95']:.3f}, "
                                  f"Memory P95: {analysis['memory_stats']['p95']:.1f}MB, "
                                  f"Error rate: {analysis['error_rate']:.3f}")
                        
                    time.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"Monitoring loop error: {e}")
                    time.sleep(interval_seconds)
                    
        self.executor.submit(monitor_loop)
        logger.info("Continuous monitoring started")
        
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring = False
        logger.info("Continuous monitoring stopped")

# Example alert callback
def log_alert(alert_type: str, severity: str, alert_data: Dict[str, Any]):
    """Example alert callback that logs alerts"""
    logger.warning(f"ALERT [{severity.upper()}] {alert_type}: {alert_data['alert']['message']}")

# Example usage
def example_usage():
    """Example usage of the performance monitoring system"""
    monitor = WhisperPerformanceMonitor()
    
    # Add alert callback
    monitor.add_alert_callback(log_alert)
    
    # Start continuous monitoring
    monitor.start_continuous_monitoring()
    
    # Simulate some inference recordings
    monitor.record_inference("distil-small.en", 10.0, 4.5, 800.0)
    monitor.record_inference("faster-whisper-base-int8", 10.0, 3.2, 600.0)
    
    # Generate report
    report = monitor.get_performance_report()
    print(json.dumps(report, indent=2))
    
    # Stop monitoring
    monitor.stop_monitoring()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    example_usage()
