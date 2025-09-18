#!/usr/bin/env python3
"""
Real-time Monitoring Demo for LiteTTS
Demonstrates performance monitoring, filesystem watching, and alerting
"""

import sys
import os
import time
import json
import threading
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PerformanceAlert:
    """Performance alert data"""
    timestamp: datetime
    alert_type: str
    message: str
    severity: str
    metrics: Dict[str, Any]

class RealTimeMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self):
        self.monitoring = False
        self.alerts = []
        self.metrics_history = []
        self.alert_thresholds = {
            "rtf_warning": 0.8,
            "rtf_critical": 1.2,
            "memory_warning": 1500,  # MB
            "memory_critical": 2500,  # MB
            "processing_time_warning": 30,  # seconds
            "processing_time_critical": 60   # seconds
        }
        
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.monitoring = True
        logger.info("🔍 Real-time monitoring started")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring = False
        logger.info("⏹️ Real-time monitoring stopped")
        
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                
                # Check for alerts
                self._check_alerts(metrics)
                
                # Store metrics
                self.metrics_history.append({
                    "timestamp": datetime.now(),
                    "metrics": metrics
                })
                
                # Limit history size
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-500:]
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(10)
                
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            import psutil
            
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / 1024**3,
                "disk_percent": disk.percent,
                "process_memory_mb": process_memory,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return {}
            
    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check metrics against alert thresholds"""
        if not metrics:
            return
            
        alerts = []
        
        # Memory alerts
        process_memory = metrics.get("process_memory_mb", 0)
        if process_memory > self.alert_thresholds["memory_critical"]:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now(),
                alert_type="memory",
                message=f"Critical memory usage: {process_memory:.1f}MB",
                severity="critical",
                metrics=metrics
            ))
        elif process_memory > self.alert_thresholds["memory_warning"]:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now(),
                alert_type="memory",
                message=f"High memory usage: {process_memory:.1f}MB",
                severity="warning",
                metrics=metrics
            ))
        
        # CPU alerts
        cpu_percent = metrics.get("cpu_percent", 0)
        if cpu_percent > 90:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now(),
                alert_type="cpu",
                message=f"High CPU usage: {cpu_percent:.1f}%",
                severity="warning",
                metrics=metrics
            ))
        
        # Disk alerts
        disk_percent = metrics.get("disk_percent", 0)
        if disk_percent > 90:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now(),
                alert_type="disk",
                message=f"Low disk space: {disk_percent:.1f}% used",
                severity="warning",
                metrics=metrics
            ))
        
        # Log and store alerts
        for alert in alerts:
            self.alerts.append(alert)
            logger.warning(f"🚨 {alert.severity.upper()}: {alert.message}")
            
        # Limit alerts history
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-50:]
            
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        if not self.metrics_history:
            return {"status": "no_data"}
            
        latest_metrics = self.metrics_history[-1]["metrics"]
        recent_alerts = [a for a in self.alerts if (datetime.now() - a.timestamp).seconds < 300]  # Last 5 minutes
        
        return {
            "status": "monitoring" if self.monitoring else "stopped",
            "latest_metrics": latest_metrics,
            "recent_alerts": len(recent_alerts),
            "total_alerts": len(self.alerts),
            "uptime_minutes": len(self.metrics_history) * 5 / 60  # Approximate
        }

class FileSystemWatcher:
    """File system monitoring for voice files and audio processing"""
    
    def __init__(self, watch_directory: str = "LiteTTS/voices"):
        self.watch_directory = Path(watch_directory)
        self.watch_directory.mkdir(exist_ok=True)
        self.watching = False
        self.file_events = []
        
    def start_watching(self):
        """Start file system monitoring"""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class VoiceFileHandler(FileSystemEventHandler):
                def __init__(self, watcher):
                    self.watcher = watcher
                    
                def on_created(self, event):
                    if not event.is_directory and event.src_path.endswith(('.wav', '.mp3', '.bin')):
                        self.watcher._handle_file_event("created", event.src_path)
                        
                def on_modified(self, event):
                    if not event.is_directory and event.src_path.endswith(('.wav', '.mp3', '.bin')):
                        self.watcher._handle_file_event("modified", event.src_path)
                        
                def on_deleted(self, event):
                    if not event.is_directory and event.src_path.endswith(('.wav', '.mp3', '.bin')):
                        self.watcher._handle_file_event("deleted", event.src_path)
            
            self.observer = Observer()
            self.observer.schedule(VoiceFileHandler(self), str(self.watch_directory), recursive=True)
            self.observer.start()
            self.watching = True
            
            logger.info(f"👁️ File system monitoring started for {self.watch_directory}")
            
        except ImportError:
            logger.warning("watchdog library not available, file system monitoring disabled")
        except Exception as e:
            logger.error(f"Failed to start file system monitoring: {e}")
            
    def stop_watching(self):
        """Stop file system monitoring"""
        if hasattr(self, 'observer') and self.watching:
            self.observer.stop()
            self.observer.join()
            self.watching = False
            logger.info("⏹️ File system monitoring stopped")
            
    def _handle_file_event(self, event_type: str, file_path: str):
        """Handle file system events"""
        event = {
            "timestamp": datetime.now(),
            "event_type": event_type,
            "file_path": file_path,
            "file_name": Path(file_path).name
        }
        
        self.file_events.append(event)
        logger.info(f"📁 File {event_type}: {Path(file_path).name}")
        
        # Limit events history
        if len(self.file_events) > 100:
            self.file_events = self.file_events[-50:]

def demo_performance_monitoring():
    """Demonstrate performance monitoring"""
    logger.info("📊 Demo: Performance Monitoring")
    logger.info("-" * 40)
    
    monitor = RealTimeMonitor()
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
        # Simulate some processing load
        logger.info("Simulating processing load...")
        
        for i in range(5):
            # Simulate CPU/memory intensive task
            start_time = time.time()
            
            # Create some memory load
            data = [list(range(10000)) for _ in range(100)]
            
            # Simulate processing time
            time.sleep(2)
            
            processing_time = time.time() - start_time
            
            # Get current status
            status = monitor.get_current_status()
            
            logger.info(f"  Iteration {i+1}: Processing time {processing_time:.2f}s")
            if status.get("latest_metrics"):
                metrics = status["latest_metrics"]
                logger.info(f"    CPU: {metrics.get('cpu_percent', 0):.1f}%, Memory: {metrics.get('process_memory_mb', 0):.1f}MB")
            
            # Clean up memory
            del data
            
        # Show final status
        final_status = monitor.get_current_status()
        logger.info(f"\nMonitoring Summary:")
        logger.info(f"  Recent alerts: {final_status.get('recent_alerts', 0)}")
        logger.info(f"  Total alerts: {final_status.get('total_alerts', 0)}")
        logger.info(f"  Uptime: {final_status.get('uptime_minutes', 0):.1f} minutes")
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        logger.info("✅ Performance monitoring demo completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Performance monitoring demo failed: {e}")
        monitor.stop_monitoring()
        return False

def demo_filesystem_monitoring():
    """Demonstrate file system monitoring"""
    logger.info("\n📁 Demo: File System Monitoring")
    logger.info("-" * 40)
    
    # Create temporary directory for demo
    temp_dir = tempfile.mkdtemp(prefix="litetts_demo_")
    logger.info(f"Using temporary directory: {temp_dir}")
    
    watcher = FileSystemWatcher(temp_dir)
    
    try:
        # Start watching
        watcher.start_watching()
        
        if watcher.watching:
            # Simulate file operations
            logger.info("Simulating file operations...")
            
            # Create some test files
            test_files = []
            for i in range(3):
                file_path = Path(temp_dir) / f"test_voice_{i}.wav"
                with open(file_path, 'w') as f:
                    f.write(f"dummy audio data {i}")
                test_files.append(file_path)
                time.sleep(1)
            
            # Modify files
            for file_path in test_files:
                with open(file_path, 'a') as f:
                    f.write(" - modified")
                time.sleep(1)
            
            # Delete files
            for file_path in test_files:
                file_path.unlink()
                time.sleep(1)
            
            # Show events
            logger.info(f"\nFile Events Summary:")
            for event in watcher.file_events:
                logger.info(f"  {event['timestamp'].strftime('%H:%M:%S')} - {event['event_type']}: {event['file_name']}")
        else:
            logger.warning("File system monitoring not available")
        
        # Stop watching
        watcher.stop_watching()
        
        logger.info("✅ File system monitoring demo completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ File system monitoring demo failed: {e}")
        watcher.stop_watching()
        return False
    finally:
        # Cleanup
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def demo_integrated_monitoring():
    """Demonstrate integrated monitoring with Whisper processing"""
    logger.info("\n🔬 Demo: Integrated Monitoring with Whisper")
    logger.info("-" * 50)
    
    monitor = RealTimeMonitor()
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
        # Test Whisper processing with monitoring
        from backends.whisper_optimized import create_whisper_processor
        
        processor = create_whisper_processor(
            model_name="distil-small.en",
            compute_type="int8"
        )
        
        logger.info("Testing Whisper processing with real-time monitoring...")
        
        # Generate test audio
        import numpy as np
        import tempfile
        try:
            import soundfile as sf
            
            # Create test audio
            duration = 10
            sample_rate = 16000
            t = np.linspace(0, duration, int(duration * sample_rate))
            audio = 0.5 * np.sin(2 * np.pi * 440 * t)
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            sf.write(temp_file.name, audio.astype(np.float32), sample_rate)
            
            # Process with monitoring
            start_time = time.time()
            result = processor.transcribe(temp_file.name, duration)
            processing_time = time.time() - start_time
            
            # Get monitoring data
            status = monitor.get_current_status()
            
            logger.info(f"Processing Results:")
            logger.info(f"  Success: {result.success}")
            logger.info(f"  Processing time: {processing_time:.3f}s")
            logger.info(f"  RTF: {result.rtf:.3f}")
            logger.info(f"  Memory usage: {result.memory_usage_mb:.1f}MB")
            
            if status.get("latest_metrics"):
                metrics = status["latest_metrics"]
                logger.info(f"System Metrics:")
                logger.info(f"  CPU: {metrics.get('cpu_percent', 0):.1f}%")
                logger.info(f"  Process Memory: {metrics.get('process_memory_mb', 0):.1f}MB")
            
            # Cleanup
            os.unlink(temp_file.name)
            
        except ImportError:
            logger.warning("soundfile not available, skipping audio generation")
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        logger.info("✅ Integrated monitoring demo completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integrated monitoring demo failed: {e}")
        monitor.stop_monitoring()
        return False

def main():
    """Run all monitoring demos"""
    logger.info("🚀 Real-time Monitoring Demo for LiteTTS")
    logger.info("=" * 60)
    
    demos = [
        ("Performance Monitoring", demo_performance_monitoring),
        ("File System Monitoring", demo_filesystem_monitoring),
        ("Integrated Monitoring", demo_integrated_monitoring),
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            result = demo_func()
            results.append((demo_name, result))
        except Exception as e:
            logger.error(f"❌ Demo {demo_name} crashed: {e}")
            results.append((demo_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 MONITORING DEMO SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for demo_name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        logger.info(f"{status}: {demo_name}")
        if result:
            passed += 1
    
    logger.info(f"\nResults: {passed}/{total} demos completed successfully")
    
    if passed == total:
        logger.info("🎉 All monitoring demos completed successfully!")
        logger.info("\nMonitoring capabilities demonstrated:")
        logger.info("• Real-time performance monitoring with alerts")
        logger.info("• File system monitoring for voice files")
        logger.info("• Integrated monitoring with Whisper processing")
        logger.info("• Automatic threshold-based alerting")
        logger.info("• Historical metrics collection")
    else:
        logger.warning(f"⚠️ {total - passed} demos failed. Check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
