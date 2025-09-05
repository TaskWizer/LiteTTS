#!/usr/bin/env python3
"""
Uvicorn Worker Manager
Provides stable worker process management with proper resource monitoring and graceful shutdown
"""

import os
import signal
import logging
import threading
import time
import psutil
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import multiprocessing
import sys
from threading import Lock

logger = logging.getLogger(__name__)

@dataclass
class WorkerConfig:
    """Configuration for worker management"""
    # Worker settings
    max_workers: int = 1
    worker_timeout: float = 30.0
    worker_memory_limit_mb: int = 2048
    worker_cpu_limit_percent: float = 90.0
    
    # Health monitoring
    health_check_interval: float = 10.0
    memory_check_interval: float = 5.0
    restart_threshold_failures: int = 3
    
    # Graceful shutdown
    graceful_shutdown_timeout: float = 30.0
    force_shutdown_timeout: float = 10.0
    
    # Resource management
    enable_memory_monitoring: bool = True
    enable_cpu_monitoring: bool = True
    enable_auto_restart: bool = True
    
    # Uvicorn specific
    uvicorn_backlog: int = 2048
    uvicorn_limit_concurrency: int = 1000
    uvicorn_limit_max_requests: int = 10000
    uvicorn_timeout_keep_alive: int = 5
    uvicorn_timeout_graceful_shutdown: int = 30

class WorkerManager:
    """
    Manages Uvicorn worker processes with stability monitoring
    """
    
    def __init__(self, config: Optional[WorkerConfig] = None):
        self.config = config or WorkerConfig()
        self.workers: Dict[int, Dict[str, Any]] = {}
        self.monitoring_thread: Optional[threading.Thread] = None
        self.shutdown_event = threading.Event()
        self.lock = threading.RLock()

        # Shutdown state protection
        self._shutdown_in_progress = False
        self._shutdown_start_time: Optional[float] = None
        self._shutdown_lock = Lock()
        self._force_shutdown_requested = False

        # Worker statistics
        self.stats = {
            'total_workers_started': 0,
            'total_workers_restarted': 0,
            'total_workers_failed': 0,
            'current_workers': 0,
            'last_restart_time': None
        }

        # Setup signal handlers
        self._setup_signal_handlers()

        logger.info("Worker manager initialized")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown with protection against recursive calls"""
        def signal_handler(signum, frame):
            with self._shutdown_lock:
                if self._shutdown_in_progress:
                    if not self._force_shutdown_requested:
                        logger.warning(f"Received signal {signum} during shutdown. Press CTRL+C again to force terminate.")
                        self._force_shutdown_requested = True
                        return
                    else:
                        logger.error("Force shutdown requested. Terminating immediately.")
                        os._exit(1)

                logger.info(f"Received signal {signum}, initiating graceful shutdown...")
                self._shutdown_in_progress = True
                self._shutdown_start_time = time.time()

            # Start shutdown in a separate thread to avoid blocking signal handler
            shutdown_thread = threading.Thread(target=self._shutdown_with_timeout, daemon=True)
            shutdown_thread.start()

        # Handle common shutdown signals
        for sig in [signal.SIGTERM, signal.SIGINT]:
            try:
                signal.signal(sig, signal_handler)
            except (OSError, ValueError):
                # Some signals may not be available on all platforms
                pass
    
    def get_optimal_worker_count(self) -> int:
        """Calculate optimal worker count based on system resources"""
        try:
            # Get system information
            cpu_count = os.cpu_count() or 1
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
            # Conservative worker calculation
            # - Leave at least 1 CPU core for system
            # - Ensure each worker has enough memory
            max_workers_by_cpu = max(1, cpu_count - 1)
            max_workers_by_memory = max(1, int(memory_gb * 1024 / self.config.worker_memory_limit_mb))
            
            # Use the more conservative limit
            optimal_workers = min(max_workers_by_cpu, max_workers_by_memory, self.config.max_workers)
            
            logger.info(f"Optimal worker count: {optimal_workers} "
                       f"(CPU: {max_workers_by_cpu}, Memory: {max_workers_by_memory}, "
                       f"Config limit: {self.config.max_workers})")
            
            return optimal_workers
            
        except Exception as e:
            logger.warning(f"Failed to calculate optimal worker count: {e}")
            return 1
    
    def get_uvicorn_config(self) -> Dict[str, Any]:
        """Get optimized Uvicorn configuration for stable workers"""
        return {
            # Worker configuration
            "workers": self.get_optimal_worker_count(),
            "worker_class": "uvicorn.workers.UvicornWorker",
            "max_requests": self.config.uvicorn_limit_max_requests,
            "max_requests_jitter": self.config.uvicorn_limit_max_requests // 10,
            
            # Connection settings
            "backlog": self.config.uvicorn_backlog,
            "limit_concurrency": self.config.uvicorn_limit_concurrency,
            
            # Timeout settings
            "timeout": self.config.worker_timeout,
            "keep_alive": self.config.uvicorn_timeout_keep_alive,
            "graceful_timeout": self.config.uvicorn_timeout_graceful_shutdown,
            
            # Performance settings
            "preload_app": True,  # Preload for better memory efficiency
            "worker_connections": 1000,
            "max_worker_connections": 1000,
            
            # Logging
            "access_log": True,
            "error_log": True,
            "capture_output": True,
            
            # Security
            "server_header": False,
            "date_header": False,
        }
    
    def apply_worker_environment_variables(self):
        """Apply environment variables for worker stability"""
        worker_env_vars = {
            # Uvicorn worker settings
            "UVICORN_BACKLOG": str(self.config.uvicorn_backlog),
            "UVICORN_LIMIT_CONCURRENCY": str(self.config.uvicorn_limit_concurrency),
            "UVICORN_LIMIT_MAX_REQUESTS": str(self.config.uvicorn_limit_max_requests),
            "UVICORN_TIMEOUT_KEEP_ALIVE": str(self.config.uvicorn_timeout_keep_alive),
            "UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN": str(self.config.uvicorn_timeout_graceful_shutdown),
            
            # Memory management
            "MALLOC_ARENA_MAX": "4",
            "MALLOC_MMAP_THRESHOLD_": "131072",
            "MALLOC_TRIM_THRESHOLD_": "131072",
            
            # Python optimization
            "PYTHONOPTIMIZE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUNBUFFERED": "1",
            
            # Process management
            "WORKER_MEMORY_LIMIT_MB": str(self.config.worker_memory_limit_mb),
            "WORKER_CPU_LIMIT_PERCENT": str(self.config.worker_cpu_limit_percent),
        }
        
        # Apply environment variables
        for key, value in worker_env_vars.items():
            if key not in os.environ:
                os.environ[key] = value
        
        logger.info(f"Applied {len(worker_env_vars)} worker environment variables")
    
    def start_monitoring(self):
        """Start worker monitoring thread"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logger.warning("Worker monitoring already running")
            return
        
        self.shutdown_event.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Worker monitoring started")
    
    def _monitoring_worker(self):
        """Background worker monitoring thread"""
        logger.info("Worker monitoring thread started")
        
        while not self.shutdown_event.is_set():
            try:
                if self.config.enable_memory_monitoring or self.config.enable_cpu_monitoring:
                    self._check_worker_health()
                
                # Sleep until next check
                self.shutdown_event.wait(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"Worker monitoring error: {e}")
                self.shutdown_event.wait(5.0)  # Wait before retrying
        
        logger.info("Worker monitoring thread stopped")
    
    def _check_worker_health(self):
        """Check health of all workers"""
        try:
            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            
            with self.lock:
                self.stats['current_workers'] = len(children)
            
            for child in children:
                try:
                    # Check memory usage
                    if self.config.enable_memory_monitoring:
                        memory_mb = child.memory_info().rss / (1024 * 1024)
                        if memory_mb > self.config.worker_memory_limit_mb:
                            logger.warning(f"Worker {child.pid} exceeds memory limit: "
                                         f"{memory_mb:.1f}MB > {self.config.worker_memory_limit_mb}MB")
                            
                            if self.config.enable_auto_restart:
                                self._restart_worker(child.pid, "memory_limit_exceeded")
                    
                    # Check CPU usage
                    if self.config.enable_cpu_monitoring:
                        cpu_percent = child.cpu_percent()
                        if cpu_percent > self.config.worker_cpu_limit_percent:
                            logger.warning(f"Worker {child.pid} high CPU usage: {cpu_percent:.1f}%")
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Worker already terminated
                    continue
                    
        except Exception as e:
            logger.error(f"Worker health check failed: {e}")
    
    def _restart_worker(self, worker_pid: int, reason: str):
        """Restart a specific worker"""
        try:
            logger.info(f"Restarting worker {worker_pid} (reason: {reason})")
            
            # Terminate the worker gracefully
            worker_process = psutil.Process(worker_pid)
            worker_process.terminate()
            
            # Wait for graceful shutdown
            try:
                worker_process.wait(timeout=self.config.graceful_shutdown_timeout)
            except psutil.TimeoutExpired:
                # Force kill if graceful shutdown failed
                logger.warning(f"Force killing worker {worker_pid}")
                worker_process.kill()
            
            with self.lock:
                self.stats['total_workers_restarted'] += 1
                self.stats['last_restart_time'] = time.time()
            
            logger.info(f"Worker {worker_pid} restarted successfully")
            
        except Exception as e:
            logger.error(f"Failed to restart worker {worker_pid}: {e}")
    
    def _shutdown_with_timeout(self):
        """Shutdown with timeout protection to prevent infinite loops"""
        max_shutdown_time = 10.0  # Maximum 10 seconds for shutdown

        try:
            self.shutdown_gracefully()
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {e}")
        finally:
            # Check if we exceeded the timeout
            if self._shutdown_start_time:
                elapsed = time.time() - self._shutdown_start_time
                if elapsed > max_shutdown_time:
                    logger.error(f"Shutdown timeout exceeded ({elapsed:.1f}s > {max_shutdown_time}s). Force terminating.")
                    os._exit(1)
                else:
                    logger.info(f"Shutdown completed in {elapsed:.1f}s")

            # Exit the process
            sys.exit(0)

    def shutdown_gracefully(self):
        """Shutdown all workers gracefully with improved timeouts"""
        logger.info("Initiating graceful worker shutdown...")

        # Stop monitoring with shorter timeout
        self.shutdown_event.set()
        if self.monitoring_thread:
            logger.debug("Stopping monitoring thread...")
            self.monitoring_thread.join(timeout=2.0)  # Reduced from 5.0
            if self.monitoring_thread.is_alive():
                logger.warning("Monitoring thread did not stop gracefully")

        try:
            # Get all child processes
            current_process = psutil.Process()
            children = current_process.children(recursive=True)

            if children:
                logger.info(f"Shutting down {len(children)} worker processes...")

                # Send SIGTERM to all children
                for child in children:
                    try:
                        child.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                # Wait for graceful shutdown with reduced timeout
                graceful_timeout = min(5.0, self.config.graceful_shutdown_timeout)  # Max 5 seconds
                logger.debug(f"Waiting up to {graceful_timeout}s for graceful shutdown...")
                gone, alive = psutil.wait_procs(children, timeout=graceful_timeout)

                # Force kill any remaining processes
                if alive:
                    logger.warning(f"Force killing {len(alive)} remaining workers")
                    for child in alive:
                        try:
                            child.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue

                    # Wait a bit for force kill to complete
                    time.sleep(0.5)

                logger.info("All workers shutdown completed")
            else:
                logger.info("No worker processes to shutdown")

        except Exception as e:
            logger.error(f"Error during worker shutdown: {e}")
            # Don't re-raise, let the timeout mechanism handle it
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        with self.lock:
            stats = self.stats.copy()
        
        # Add current system information
        try:
            current_process = psutil.Process()
            stats['system_memory_mb'] = psutil.virtual_memory().used / (1024 * 1024)
            stats['process_memory_mb'] = current_process.memory_info().rss / (1024 * 1024)
            stats['cpu_percent'] = current_process.cpu_percent()
        except Exception:
            pass
        
        return stats

# Global worker manager instance
_worker_manager: Optional[WorkerManager] = None

def get_worker_manager() -> WorkerManager:
    """Get or create global worker manager"""
    global _worker_manager
    if _worker_manager is None:
        _worker_manager = WorkerManager()
    return _worker_manager

def initialize_worker_manager(config: Optional[WorkerConfig] = None) -> WorkerManager:
    """Initialize global worker manager with configuration"""
    global _worker_manager
    _worker_manager = WorkerManager(config)
    return _worker_manager
