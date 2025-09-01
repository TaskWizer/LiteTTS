#!/usr/bin/env python3
"""
Fault tolerance and resilience features for Kokoro ONNX TTS API
"""

import asyncio
import time
import logging
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                if self.state == "OPEN":
                    if self._should_attempt_reset():
                        self.state = "HALF_OPEN"
                        logger.info(f"🔄 Circuit breaker HALF_OPEN for {func.__name__}")
                    else:
                        raise Exception(f"Circuit breaker OPEN for {func.__name__}")
                
                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except self.expected_exception as e:
                    self._on_failure()
                    raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            logger.info("✅ Circuit breaker CLOSED (recovered)")
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"⚠️ Circuit breaker OPEN (failure threshold reached)")

class RetryManager:
    """Retry logic with exponential backoff"""
    
    @staticmethod
    def retry_with_backoff(
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        """Decorator for retry with exponential backoff"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt == max_retries:
                            logger.error(f"❌ {func.__name__} failed after {max_retries} retries: {e}")
                            raise e
                        
                        delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                        logger.warning(f"⚠️ {func.__name__} attempt {attempt + 1} failed: {e}")
                        logger.info(f"🔄 Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                
                raise last_exception
            
            return wrapper
        return decorator

class HealthChecker:
    """Health checking system for components"""
    
    def __init__(self):
        self.checks = {}
        self.last_results = {}
        self.lock = threading.Lock()
    
    def register_check(self, name: str, check_func: Callable[[], bool], interval: int = 60):
        """Register a health check"""
        with self.lock:
            self.checks[name] = {
                "func": check_func,
                "interval": interval,
                "last_check": 0,
                "enabled": True
            }
            logger.info(f"🏥 Registered health check: {name}")
    
    def run_check(self, name: str) -> bool:
        """Run a specific health check"""
        if name not in self.checks:
            logger.warning(f"⚠️ Unknown health check: {name}")
            return False
        
        check = self.checks[name]
        if not check["enabled"]:
            return True
        
        try:
            result = check["func"]()
            with self.lock:
                self.last_results[name] = {
                    "status": result,
                    "timestamp": time.time(),
                    "error": None
                }
            return result
        except Exception as e:
            logger.error(f"❌ Health check {name} failed: {e}")
            with self.lock:
                self.last_results[name] = {
                    "status": False,
                    "timestamp": time.time(),
                    "error": str(e)
                }
            return False
    
    def run_all_checks(self) -> Dict[str, bool]:
        """Run all health checks"""
        results = {}
        current_time = time.time()
        
        for name, check in self.checks.items():
            if not check["enabled"]:
                results[name] = True
                continue
            
            # Check if it's time to run this check
            if current_time - check["last_check"] >= check["interval"]:
                results[name] = self.run_check(name)
                self.checks[name]["last_check"] = current_time
            else:
                # Use last result if available
                if name in self.last_results:
                    results[name] = self.last_results[name]["status"]
                else:
                    results[name] = True
        
        return results
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        results = self.run_all_checks()
        
        return {
            "healthy": all(results.values()),
            "checks": results,
            "details": self.last_results.copy()
        }
    
    def enable_check(self, name: str):
        """Enable a health check"""
        if name in self.checks:
            self.checks[name]["enabled"] = True
            logger.info(f"✅ Enabled health check: {name}")
    
    def disable_check(self, name: str):
        """Disable a health check"""
        if name in self.checks:
            self.checks[name]["enabled"] = False
            logger.info(f"⏸️ Disabled health check: {name}")

class GracefulDegradation:
    """Graceful degradation when components fail"""
    
    def __init__(self):
        self.fallback_handlers = {}
        self.component_status = {}
        self.lock = threading.Lock()
    
    def register_fallback(self, component: str, fallback_func: Callable):
        """Register a fallback function for a component"""
        with self.lock:
            self.fallback_handlers[component] = fallback_func
            self.component_status[component] = True
            logger.info(f"🛡️ Registered fallback for component: {component}")
    
    def mark_component_failed(self, component: str):
        """Mark a component as failed"""
        with self.lock:
            self.component_status[component] = False
            logger.warning(f"⚠️ Component marked as failed: {component}")
    
    def mark_component_healthy(self, component: str):
        """Mark a component as healthy"""
        with self.lock:
            self.component_status[component] = True
            logger.info(f"✅ Component marked as healthy: {component}")
    
    def is_component_healthy(self, component: str) -> bool:
        """Check if a component is healthy"""
        with self.lock:
            return self.component_status.get(component, True)
    
    def get_fallback(self, component: str) -> Optional[Callable]:
        """Get fallback function for a component"""
        with self.lock:
            return self.fallback_handlers.get(component)
    
    def execute_with_fallback(self, component: str, primary_func: Callable, *args, **kwargs):
        """Execute function with fallback if component is unhealthy"""
        if self.is_component_healthy(component):
            try:
                return primary_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"❌ Primary function failed for {component}: {e}")
                self.mark_component_failed(component)
                # Fall through to fallback
        
        fallback = self.get_fallback(component)
        if fallback:
            logger.info(f"🛡️ Using fallback for component: {component}")
            return fallback(*args, **kwargs)
        else:
            raise Exception(f"No fallback available for failed component: {component}")

# Global instances
health_checker = HealthChecker()
graceful_degradation = GracefulDegradation()

def get_health_checker():
    """Get health checker instance"""
    return health_checker

def get_graceful_degradation():
    """Get graceful degradation instance"""
    return graceful_degradation

# Common health checks
def check_model_file_exists(model_path: str) -> bool:
    """Health check for model file existence"""
    return Path(model_path).exists()

def check_voices_directory(voices_dir: str) -> bool:
    """Health check for voices directory"""
    voices_path = Path(voices_dir)
    return voices_path.exists() and any(voices_path.glob("*.bin"))

def check_disk_space(path: str, min_gb: float = 1.0) -> bool:
    """Health check for available disk space"""
    try:
        import shutil
        free_bytes = shutil.disk_usage(path).free
        free_gb = free_bytes / (1024 ** 3)
        return free_gb >= min_gb
    except Exception:
        return False

def check_memory_usage(max_percent: float = 90.0) -> bool:
    """Health check for memory usage"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        return memory.percent <= max_percent
    except ImportError:
        # psutil not available, skip memory check
        return True
    except Exception:
        return True  # Assume OK if can't check
