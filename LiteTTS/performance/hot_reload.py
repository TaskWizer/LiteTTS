#!/usr/bin/env python3
"""
Hot reload system for models and voices without server restart
"""

import asyncio
import time
import logging
from pathlib import Path
from typing import Dict, Optional, Callable, Any
import threading

# Optional dependency for file watching
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None

logger = logging.getLogger(__name__)

class ModelReloadHandler:
    """File system event handler for model hot reloading"""

    def __init__(self, reload_callback: Callable[[str], None]):
        if WATCHDOG_AVAILABLE:
            # Initialize as FileSystemEventHandler if watchdog is available
            super().__init__() if hasattr(FileSystemEventHandler, '__init__') else None
        self.reload_callback = reload_callback
        self.last_reload = {}
        self.reload_delay = 2.0  # Seconds to wait before reloading
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Only reload for model files
        if file_path.suffix in ['.onnx', '.bin']:
            current_time = time.time()
            
            # Debounce rapid file changes
            if (file_path in self.last_reload and 
                current_time - self.last_reload[file_path] < self.reload_delay):
                return
                
            self.last_reload[file_path] = current_time
            
            logger.info(f"🔄 Detected change in {file_path.name}, scheduling reload...")
            
            # Schedule reload after delay
            threading.Timer(self.reload_delay, self._delayed_reload, [str(file_path)]).start()
    
    def _delayed_reload(self, file_path: str):
        """Perform delayed reload to avoid rapid reloads"""
        try:
            self.reload_callback(file_path)
        except Exception as e:
            logger.error(f"❌ Hot reload failed for {file_path}: {e}")

class HotReloadManager:
    """Manages hot reloading of models and voices"""
    
    def __init__(self, config=None):
        self.config = config
        self.observers = []
        self.reload_callbacks = {}
        self.enabled = config.performance.hot_reload if config else True

        if not self.enabled:
            logger.info("🔄 Hot reload disabled by configuration")
            return

        if not WATCHDOG_AVAILABLE:
            logger.warning("🔄 Hot reload disabled - watchdog package not available")
            logger.info("💡 Install watchdog for hot reload: pip install watchdog")
            self.enabled = False
            return

        logger.info("🔄 Hot reload manager initialized")
    
    def register_model_reload(self, model_path: str, reload_callback: Callable[[str], None]):
        """Register a model for hot reloading"""
        if not self.enabled or not WATCHDOG_AVAILABLE:
            return

        model_dir = Path(model_path).parent

        if not model_dir.exists():
            logger.warning(f"⚠️ Model directory does not exist: {model_dir}")
            return

        handler = ModelReloadHandler(reload_callback)
        observer = Observer()
        observer.schedule(handler, str(model_dir), recursive=False)

        self.observers.append(observer)
        self.reload_callbacks[str(model_path)] = reload_callback

        observer.start()
        logger.info(f"🔄 Hot reload enabled for model: {model_path}")
    
    def register_voice_reload(self, voices_dir: str, reload_callback: Callable[[str], None]):
        """Register voices directory for hot reloading"""
        if not self.enabled or not WATCHDOG_AVAILABLE:
            return

        voices_path = Path(voices_dir)

        if not voices_path.exists():
            logger.warning(f"⚠️ Voices directory does not exist: {voices_path}")
            return

        handler = ModelReloadHandler(reload_callback)
        observer = Observer()
        observer.schedule(handler, str(voices_path), recursive=False)

        self.observers.append(observer)
        self.reload_callbacks[str(voices_path)] = reload_callback

        observer.start()
        logger.info(f"🔄 Hot reload enabled for voices: {voices_dir}")
    
    def manual_reload(self, file_path: str) -> bool:
        """Manually trigger a reload for a specific file"""
        if not self.enabled:
            logger.warning("🔄 Hot reload is disabled")
            return False
            
        try:
            # Find appropriate callback
            callback = None
            for registered_path, cb in self.reload_callbacks.items():
                if file_path.startswith(registered_path) or registered_path in file_path:
                    callback = cb
                    break
            
            if callback:
                logger.info(f"🔄 Manual reload triggered for: {file_path}")
                callback(file_path)
                return True
            else:
                logger.warning(f"⚠️ No reload callback found for: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Manual reload failed for {file_path}: {e}")
            return False
    
    def reload_all(self) -> Dict[str, bool]:
        """Reload all registered files"""
        if not self.enabled:
            logger.warning("🔄 Hot reload is disabled")
            return {}
            
        results = {}
        
        for file_path, callback in self.reload_callbacks.items():
            try:
                logger.info(f"🔄 Reloading: {file_path}")
                callback(file_path)
                results[file_path] = True
            except Exception as e:
                logger.error(f"❌ Failed to reload {file_path}: {e}")
                results[file_path] = False
        
        return results
    
    def stop(self):
        """Stop all file watchers"""
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        self.observers.clear()
        self.reload_callbacks.clear()
        logger.info("🔄 Hot reload manager stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get hot reload status"""
        return {
            "enabled": self.enabled,
            "active_watchers": len(self.observers),
            "registered_paths": list(self.reload_callbacks.keys()),
            "observer_status": [obs.is_alive() for obs in self.observers]
        }

class PerformanceMonitor:
    """Monitor performance metrics for optimization"""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "model_loads": 0,
            "voice_loads": 0
        }
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def record_request(self, response_time: float, success: bool = True):
        """Record a request with its response time"""
        with self.lock:
            self.metrics["requests_total"] += 1
            
            if success:
                self.metrics["requests_successful"] += 1
            else:
                self.metrics["requests_failed"] += 1
            
            self.metrics["total_response_time"] += response_time
            self.metrics["average_response_time"] = (
                self.metrics["total_response_time"] / self.metrics["requests_total"]
            )
    
    def record_cache_hit(self):
        """Record a cache hit"""
        with self.lock:
            self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """Record a cache miss"""
        with self.lock:
            self.metrics["cache_misses"] += 1
    
    def record_model_load(self):
        """Record a model load"""
        with self.lock:
            self.metrics["model_loads"] += 1
    
    def record_voice_load(self):
        """Record a voice load"""
        with self.lock:
            self.metrics["voice_loads"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        with self.lock:
            uptime = time.time() - self.start_time
            cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
            cache_hit_rate = (
                self.metrics["cache_hits"] / cache_total if cache_total > 0 else 0.0
            )
            
            return {
                **self.metrics,
                "uptime_seconds": uptime,
                "requests_per_second": self.metrics["requests_total"] / uptime if uptime > 0 else 0.0,
                "success_rate": (
                    self.metrics["requests_successful"] / self.metrics["requests_total"] 
                    if self.metrics["requests_total"] > 0 else 0.0
                ),
                "cache_hit_rate": cache_hit_rate
            }
    
    def reset_metrics(self):
        """Reset all metrics"""
        with self.lock:
            for key in self.metrics:
                if isinstance(self.metrics[key], (int, float)):
                    self.metrics[key] = 0 if isinstance(self.metrics[key], int) else 0.0
            self.start_time = time.time()

# Global instances
hot_reload_manager = None
performance_monitor = PerformanceMonitor()

def get_hot_reload_manager(config=None):
    """Get or create hot reload manager"""
    global hot_reload_manager
    if hot_reload_manager is None:
        hot_reload_manager = HotReloadManager(config)
    return hot_reload_manager

def get_performance_monitor():
    """Get performance monitor"""
    return performance_monitor
