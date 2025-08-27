#!/usr/bin/env python3
"""
Dynamic CPU utilization monitoring and core allocation system for Kokoro TTS API.
Provides real-time CPU monitoring with configurable thresholds for optimal performance.
"""

import os
import time
import threading
import logging
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from collections import deque
import psutil

logger = logging.getLogger(__name__)

@dataclass
class CPUThresholds:
    """CPU utilization thresholds for dynamic allocation"""
    cpu_target: float = 75.0  # Target maximum CPU utilization (%)
    hysteresis_factor: float = 0.6  # Scale-down threshold = cpu_target * hysteresis_factor
    monitoring_interval: float = 1.0  # Monitoring interval in seconds
    history_window: int = 10  # Number of samples to keep for averaging
    allocation_cooldown: float = 5.0  # Minimum time between allocation changes

    # Legacy support for backward compatibility
    min_threshold: Optional[float] = None  # Deprecated: use cpu_target instead
    max_threshold: Optional[float] = None  # Deprecated: use cpu_target instead

@dataclass
class CPUAllocation:
    """Current CPU core allocation state"""
    total_cores: int
    allocated_cores: int
    utilization_percent: float
    timestamp: float
    inter_op_threads: int
    intra_op_threads: int
    allocation_reason: str

class CPUUtilizationMonitor:
    """Real-time CPU utilization monitoring with dynamic core allocation"""
    
    def __init__(self, thresholds: Optional[CPUThresholds] = None):
        self.thresholds = thresholds or CPUThresholds()
        self.total_cores = os.cpu_count() or 4
        self.current_allocation = CPUAllocation(
            total_cores=self.total_cores,
            allocated_cores=1,
            utilization_percent=0.0,
            timestamp=time.time(),
            inter_op_threads=1,
            intra_op_threads=1,
            allocation_reason="initial"
        )
        
        # Monitoring state
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._utilization_history = deque(maxlen=self.thresholds.history_window)
        self._last_allocation_change = 0.0
        self._allocation_callbacks: List[Callable[[CPUAllocation], None]] = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info(f"CPU Monitor initialized: {self.total_cores} cores available")
    
    def add_allocation_callback(self, callback: Callable[[CPUAllocation], None]):
        """Add callback to be called when CPU allocation changes"""
        with self._lock:
            self._allocation_callbacks.append(callback)
    
    def get_current_utilization(self) -> float:
        """Get current CPU utilization percentage"""
        try:
            # Get CPU utilization over a short interval for accuracy
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            logger.warning(f"Failed to get CPU utilization: {e}")
            return 50.0  # Default fallback
    
    def get_average_utilization(self) -> float:
        """Get average CPU utilization from history"""
        with self._lock:
            if not self._utilization_history:
                return self.get_current_utilization()
            return sum(self._utilization_history) / len(self._utilization_history)
    
    def calculate_optimal_cores(self, utilization: float) -> Tuple[int, str]:
        """Calculate optimal core count based on single CPU target threshold with hysteresis"""
        min_cores = 1
        max_cores = max(1, self.total_cores - 1)  # Leave at least 1 core for system

        # Calculate thresholds with hysteresis to prevent oscillation
        scale_up_threshold = self.thresholds.cpu_target
        scale_down_threshold = self.thresholds.cpu_target * self.thresholds.hysteresis_factor

        if utilization > scale_up_threshold:
            # High utilization: increase cores to reduce load per core
            optimal_cores = min(max_cores, self.current_allocation.allocated_cores + 1)
            reason = f"high_utilization_{utilization:.1f}%_target_{scale_up_threshold:.1f}%"
        elif utilization < scale_down_threshold:
            # Low utilization: decrease cores when significantly underutilized
            optimal_cores = max(min_cores, self.current_allocation.allocated_cores - 1)
            reason = f"low_utilization_{utilization:.1f}%_target_{scale_down_threshold:.1f}%"
        else:
            # Stable zone: maintain current allocation
            optimal_cores = self.current_allocation.allocated_cores
            reason = f"stable_zone_{utilization:.1f}%_target_{scale_up_threshold:.1f}%"

        return optimal_cores, reason
    
    def calculate_thread_allocation(self, cores: int) -> Tuple[int, int]:
        """Calculate optimal inter_op and intra_op thread counts for given cores"""
        # Based on existing CPU optimizer logic but simplified for dynamic allocation
        if cores >= 8:
            inter_op = min(6, cores // 2)
            intra_op = min(cores * 2, cores + 4)  # Allow some hyperthreading
        elif cores >= 4:
            inter_op = min(4, cores // 2)
            intra_op = min(cores * 2, cores + 2)
        else:
            inter_op = max(1, cores // 2)
            intra_op = cores
        
        return inter_op, intra_op
    
    def update_allocation(self, utilization: float) -> bool:
        """Update CPU allocation based on utilization. Returns True if changed."""
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self._last_allocation_change < self.thresholds.allocation_cooldown:
            return False
        
        optimal_cores, reason = self.calculate_optimal_cores(utilization)
        
        # Only update if allocation actually changes
        if optimal_cores == self.current_allocation.allocated_cores:
            return False
        
        inter_op, intra_op = self.calculate_thread_allocation(optimal_cores)
        
        with self._lock:
            old_allocation = self.current_allocation
            self.current_allocation = CPUAllocation(
                total_cores=self.total_cores,
                allocated_cores=optimal_cores,
                utilization_percent=utilization,
                timestamp=current_time,
                inter_op_threads=inter_op,
                intra_op_threads=intra_op,
                allocation_reason=reason
            )
            self._last_allocation_change = current_time
        
        logger.info(f"CPU allocation changed: {old_allocation.allocated_cores} → {optimal_cores} cores "
                   f"(utilization: {utilization:.1f}%, reason: {reason})")
        
        # Notify callbacks
        for callback in self._allocation_callbacks:
            try:
                callback(self.current_allocation)
            except Exception as e:
                logger.error(f"CPU allocation callback failed: {e}")
        
        return True
    
    def _monitor_loop(self):
        """Main monitoring loop (runs in separate thread)"""
        logger.info("CPU utilization monitoring started")
        
        while self._monitoring:
            try:
                # Get current utilization
                utilization = self.get_current_utilization()
                
                # Update history
                with self._lock:
                    self._utilization_history.append(utilization)
                
                # Use average utilization for allocation decisions to reduce noise
                avg_utilization = self.get_average_utilization()
                
                # Update allocation if needed
                self.update_allocation(avg_utilization)
                
                # Sleep until next monitoring interval
                time.sleep(self.thresholds.monitoring_interval)
                
            except Exception as e:
                logger.error(f"CPU monitoring error: {e}")
                time.sleep(self.thresholds.monitoring_interval)
    
    def start_monitoring(self):
        """Start CPU utilization monitoring"""
        if self._monitoring:
            logger.warning("CPU monitoring already running")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("CPU utilization monitoring started")
    
    def stop_monitoring(self):
        """Stop CPU utilization monitoring"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        logger.info("CPU utilization monitoring stopped")
    
    def get_current_allocation(self) -> CPUAllocation:
        """Get current CPU allocation state"""
        with self._lock:
            return self.current_allocation
    
    def get_monitoring_stats(self) -> Dict:
        """Get monitoring statistics"""
        with self._lock:
            return {
                "monitoring_active": self._monitoring,
                "total_cores": self.total_cores,
                "current_allocation": {
                    "allocated_cores": self.current_allocation.allocated_cores,
                    "inter_op_threads": self.current_allocation.inter_op_threads,
                    "intra_op_threads": self.current_allocation.intra_op_threads,
                    "utilization_percent": self.current_allocation.utilization_percent,
                    "allocation_reason": self.current_allocation.allocation_reason,
                    "timestamp": self.current_allocation.timestamp
                },
                "thresholds": {
                    "cpu_target": self.thresholds.cpu_target,
                    "scale_up_threshold": self.thresholds.cpu_target,
                    "scale_down_threshold": self.thresholds.cpu_target * self.thresholds.hysteresis_factor,
                    "hysteresis_factor": self.thresholds.hysteresis_factor,
                    "monitoring_interval": self.thresholds.monitoring_interval
                },
                "utilization_history": list(self._utilization_history),
                "average_utilization": self.get_average_utilization() if self._utilization_history else 0.0
            }

# Global monitor instance
_cpu_monitor: Optional[CPUUtilizationMonitor] = None

def get_cpu_monitor(thresholds: Optional[CPUThresholds] = None) -> CPUUtilizationMonitor:
    """Get or create global CPU monitor instance"""
    global _cpu_monitor
    if _cpu_monitor is None:
        _cpu_monitor = CPUUtilizationMonitor(thresholds)
    return _cpu_monitor

def initialize_cpu_monitoring(config: Optional[Dict] = None) -> CPUUtilizationMonitor:
    """Initialize CPU monitoring with configuration (supports both new and legacy formats)"""
    thresholds = CPUThresholds()

    if config:
        # New single-threshold format (preferred)
        if "cpu_target" in config:
            thresholds.cpu_target = config.get("cpu_target", 75.0)
            thresholds.hysteresis_factor = config.get("hysteresis_factor", 0.6)
        # Legacy dual-threshold format (auto-migrate)
        elif "min_threshold" in config or "max_threshold" in config:
            # Auto-migrate: use max_threshold as cpu_target
            legacy_max = config.get("max_threshold", 80.0)
            thresholds.cpu_target = legacy_max
            thresholds.hysteresis_factor = 0.6  # Default hysteresis
            logger.warning(f"Legacy CPU threshold configuration detected. "
                          f"Auto-migrated to cpu_target={legacy_max}%. "
                          f"Consider updating config to use 'cpu_target' instead of 'min_threshold'/'max_threshold'.")

        # Common settings
        thresholds.monitoring_interval = config.get("monitoring_interval", 1.0)
        thresholds.history_window = config.get("history_window", 10)
        thresholds.allocation_cooldown = config.get("allocation_cooldown", 5.0)

    monitor = get_cpu_monitor(thresholds)
    monitor.start_monitoring()
    return monitor
