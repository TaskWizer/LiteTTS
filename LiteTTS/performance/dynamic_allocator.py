#!/usr/bin/env python3
"""
Dynamic CPU core allocation system that integrates with existing CPU optimizer
and ONNX Runtime threading configuration for optimal TTS performance.
"""

import os
import time
import logging
import threading
from typing import Dict, Optional, Any
from dataclasses import dataclass

from .cpu_monitor import CPUUtilizationMonitor, CPUAllocation, get_cpu_monitor
from .cpu_optimizer import get_cpu_optimizer

logger = logging.getLogger(__name__)

@dataclass
class DynamicAllocationConfig:
    """Configuration for dynamic CPU allocation"""
    enabled: bool = True
    min_cores: int = 1
    max_cores: Optional[int] = None  # None = auto-detect (total_cores - 1)
    aggressive_mode: bool = False
    thermal_protection: bool = True
    onnx_integration: bool = True
    update_environment: bool = True

class DynamicCPUAllocator:
    """Dynamic CPU core allocator that integrates with existing systems"""
    
    def __init__(self, config: Optional[DynamicAllocationConfig] = None):
        self.config = config or DynamicAllocationConfig()
        self.cpu_optimizer = get_cpu_optimizer()
        self.cpu_monitor: Optional[CPUUtilizationMonitor] = None
        self._current_onnx_session = None
        self._lock = threading.RLock()
        
        # Auto-detect max cores if not specified
        total_cores = os.cpu_count() or 4
        if self.config.max_cores is None:
            self.config.max_cores = max(1, total_cores - 1)
        
        logger.info(f"Dynamic CPU Allocator initialized: "
                   f"cores={self.config.min_cores}-{self.config.max_cores}, "
                   f"aggressive={self.config.aggressive_mode}")
    
    def initialize_monitoring(self, monitor_config: Optional[Dict] = None):
        """Initialize CPU monitoring with allocation callbacks"""
        from .cpu_monitor import initialize_cpu_monitoring
        
        self.cpu_monitor = initialize_cpu_monitoring(monitor_config)
        self.cpu_monitor.add_allocation_callback(self._on_allocation_change)
        logger.info("Dynamic CPU allocation monitoring initialized")
    
    def _on_allocation_change(self, allocation: CPUAllocation):
        """Callback when CPU allocation changes"""
        try:
            with self._lock:
                # Validate allocation bounds
                bounded_cores = max(self.config.min_cores, 
                                  min(self.config.max_cores, allocation.allocated_cores))
                
                if bounded_cores != allocation.allocated_cores:
                    logger.info(f"Bounded core allocation: {allocation.allocated_cores} → {bounded_cores}")
                    allocation.allocated_cores = bounded_cores
                    allocation.inter_op_threads, allocation.intra_op_threads = \
                        self.cpu_monitor.calculate_thread_allocation(bounded_cores)
                
                # Apply thermal protection if enabled
                if self.config.thermal_protection:
                    thermal_status = self.cpu_optimizer.get_thermal_status()
                    if not thermal_status.get("safe_for_aggressive", True):
                        # Reduce allocation under thermal stress
                        safe_cores = max(self.config.min_cores, bounded_cores // 2)
                        if safe_cores != bounded_cores:
                            logger.warning(f"Thermal protection: reducing cores {bounded_cores} → {safe_cores}")
                            allocation.allocated_cores = safe_cores
                            allocation.inter_op_threads, allocation.intra_op_threads = \
                                self.cpu_monitor.calculate_thread_allocation(safe_cores)
                
                # Update ONNX Runtime configuration if enabled
                if self.config.onnx_integration:
                    self._update_onnx_configuration(allocation)
                
                # Update environment variables if enabled
                if self.config.update_environment:
                    self._update_environment_variables(allocation)
                
                logger.info(f"Applied dynamic CPU allocation: "
                           f"cores={allocation.allocated_cores}, "
                           f"inter_op={allocation.inter_op_threads}, "
                           f"intra_op={allocation.intra_op_threads}, "
                           f"reason={allocation.allocation_reason}")
                
        except Exception as e:
            logger.error(f"Failed to apply CPU allocation change: {e}")
    
    def _update_onnx_configuration(self, allocation: CPUAllocation):
        """Update ONNX Runtime session configuration"""
        try:
            # This will be applied to new ONNX sessions
            # Store the configuration for the next session creation
            self._current_onnx_config = {
                "inter_op_num_threads": allocation.inter_op_threads,
                "intra_op_num_threads": allocation.intra_op_threads,
                "allocated_cores": allocation.allocated_cores
            }
            
            logger.debug(f"Updated ONNX configuration: {self._current_onnx_config}")
            
        except Exception as e:
            logger.error(f"Failed to update ONNX configuration: {e}")
    
    def _update_environment_variables(self, allocation: CPUAllocation):
        """Update environment variables for threading libraries"""
        try:
            # Calculate environment variable values based on allocation
            omp_threads = allocation.intra_op_threads
            
            env_updates = {
                "OMP_NUM_THREADS": str(omp_threads),
                "OPENBLAS_NUM_THREADS": str(omp_threads),
                "MKL_NUM_THREADS": str(omp_threads),
                "NUMEXPR_NUM_THREADS": str(max(1, allocation.allocated_cores // 3)),
            }
            
            # Apply aggressive settings if enabled
            if self.config.aggressive_mode:
                env_updates.update({
                    "OMP_SCHEDULE": "dynamic",
                    "OMP_PROC_BIND": "spread",
                    "OMP_PLACES": "cores",
                    "KMP_AFFINITY": "granularity=fine,compact,1,0",
                    "KMP_BLOCKTIME": "0"
                })
            
            # Update environment
            for key, value in env_updates.items():
                os.environ[key] = value
            
            logger.debug(f"Updated environment variables: {env_updates}")
            
        except Exception as e:
            logger.error(f"Failed to update environment variables: {e}")
    
    def get_current_onnx_config(self) -> Optional[Dict]:
        """Get current ONNX configuration for new sessions"""
        with self._lock:
            return getattr(self, '_current_onnx_config', None)
    
    def apply_to_onnx_session_options(self, session_options) -> bool:
        """Apply current allocation to ONNX session options"""
        try:
            config = self.get_current_onnx_config()
            if not config:
                return False
            
            session_options.inter_op_num_threads = config["inter_op_num_threads"]
            session_options.intra_op_num_threads = config["intra_op_num_threads"]
            
            logger.debug(f"Applied dynamic allocation to ONNX session: "
                        f"inter_op={config['inter_op_num_threads']}, "
                        f"intra_op={config['intra_op_num_threads']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply allocation to ONNX session: {e}")
            return False
    
    def get_recommended_settings(self) -> Dict[str, Any]:
        """Get recommended settings based on current allocation"""
        if not self.cpu_monitor:
            return {}
        
        allocation = self.cpu_monitor.get_current_allocation()
        
        return {
            "workers": min(3, max(1, allocation.allocated_cores // 3)),
            "onnx_inter_op_threads": allocation.inter_op_threads,
            "onnx_intra_op_threads": allocation.intra_op_threads,
            "batch_size": min(6, max(1, allocation.allocated_cores // 2)),
            "concurrent_requests": min(12, max(2, allocation.allocated_cores)),
            "allocated_cores": allocation.allocated_cores,
            "utilization_percent": allocation.utilization_percent,
            "allocation_reason": allocation.allocation_reason
        }
    
    def get_allocation_stats(self) -> Dict:
        """Get comprehensive allocation statistics"""
        stats = {
            "dynamic_allocation_enabled": self.config.enabled,
            "config": {
                "min_cores": self.config.min_cores,
                "max_cores": self.config.max_cores,
                "aggressive_mode": self.config.aggressive_mode,
                "thermal_protection": self.config.thermal_protection,
                "onnx_integration": self.config.onnx_integration
            }
        }
        
        if self.cpu_monitor:
            stats.update(self.cpu_monitor.get_monitoring_stats())
        
        current_config = self.get_current_onnx_config()
        if current_config:
            stats["current_onnx_config"] = current_config
        
        return stats
    
    def force_allocation_update(self, cores: int, reason: str = "manual") -> bool:
        """Force a specific core allocation (for testing/debugging)"""
        if not self.cpu_monitor:
            logger.error("CPU monitor not initialized")
            return False
        
        # Validate bounds
        cores = max(self.config.min_cores, min(self.config.max_cores, cores))
        
        # Create allocation
        inter_op, intra_op = self.cpu_monitor.calculate_thread_allocation(cores)
        allocation = CPUAllocation(
            total_cores=self.cpu_monitor.total_cores,
            allocated_cores=cores,
            utilization_percent=self.cpu_monitor.get_current_utilization(),
            timestamp=time.time(),
            inter_op_threads=inter_op,
            intra_op_threads=intra_op,
            allocation_reason=reason
        )
        
        # Apply the allocation
        self._on_allocation_change(allocation)
        return True
    
    def shutdown(self):
        """Shutdown dynamic allocation system"""
        if self.cpu_monitor:
            self.cpu_monitor.stop_monitoring()
        logger.info("Dynamic CPU allocator shutdown")

# Global allocator instance
_dynamic_allocator: Optional[DynamicCPUAllocator] = None

def get_dynamic_allocator(config: Optional[DynamicAllocationConfig] = None) -> DynamicCPUAllocator:
    """Get or create global dynamic allocator instance"""
    global _dynamic_allocator
    if _dynamic_allocator is None:
        _dynamic_allocator = DynamicCPUAllocator(config)
    return _dynamic_allocator

def initialize_dynamic_allocation(
    allocation_config: Optional[DynamicAllocationConfig] = None,
    monitor_config: Optional[Dict] = None
) -> DynamicCPUAllocator:
    """Initialize dynamic CPU allocation system"""
    allocator = get_dynamic_allocator(allocation_config)
    if allocation_config and allocation_config.enabled:
        allocator.initialize_monitoring(monitor_config)
    return allocator
