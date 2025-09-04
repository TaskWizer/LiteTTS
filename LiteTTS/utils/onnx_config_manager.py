#!/usr/bin/env python3
"""
ONNX Runtime Configuration Manager
Centralized management of ONNX session options to prevent duplicate configuration warnings
"""

import logging
from typing import Dict, Any, Optional, Set
import threading

logger = logging.getLogger(__name__)

class ONNXConfigManager:
    """Centralized ONNX Runtime configuration manager to prevent duplicate entries"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._applied_configs: Dict[str, Set[str]] = {}
    
    def create_session_options(self, session_id: str = "default") -> Any:
        """Create ONNX session options with safe configuration"""
        try:
            import onnxruntime as ort
        except ImportError:
            logger.warning("ONNX Runtime not available")
            return None
        
        with self._lock:
            session_options = ort.SessionOptions()
            
            # Track applied configurations for this session
            if session_id not in self._applied_configs:
                self._applied_configs[session_id] = set()
            
            applied = self._applied_configs[session_id]
            
            # Basic optimizations (always safe to set)
            session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            session_options.execution_mode = ort.ExecutionMode.ORT_PARALLEL
            session_options.enable_mem_pattern = True
            session_options.enable_cpu_mem_arena = True
            session_options.enable_mem_reuse = True
            
            # Advanced configurations (check for duplicates)
            self._safe_add_config_entry(session_options, applied, "session.use_env_allocators", "1")
            self._safe_add_config_entry(session_options, applied, "session.use_deterministic_compute", "0")
            self._safe_add_config_entry(session_options, applied, "session.disable_prepacking", "0")
            
            logger.debug(f"Created ONNX session options for session '{session_id}'")
            return session_options
    
    def _safe_add_config_entry(self, session_options: Any, applied: Set[str], key: str, value: str):
        """Safely add configuration entry without duplicates"""
        if key not in applied:
            try:
                session_options.add_session_config_entry(key, value)
                applied.add(key)
                logger.debug(f"Added ONNX config: {key}={value}")
            except Exception as e:
                logger.debug(f"Failed to add ONNX config {key}={value}: {e}")
                applied.add(key)  # Mark as attempted to avoid retries
    
    def apply_cpu_optimizations(self, session_options: Any, session_id: str = "default", 
                               cpu_info: Optional[Dict] = None):
        """Apply CPU-specific optimizations"""
        with self._lock:
            if session_id not in self._applied_configs:
                self._applied_configs[session_id] = set()
            
            applied = self._applied_configs[session_id]
            
            # Intel-specific optimizations
            if cpu_info and "Intel" in cpu_info.get("model_name", ""):
                self._safe_add_config_entry(session_options, applied, "session.use_intel_optimizations", "1")
                
                if cpu_info.get("supports_avx2", False):
                    self._safe_add_config_entry(session_options, applied, "session.use_avx2", "1")
    
    def apply_memory_optimizations(self, session_options: Any, session_id: str = "default",
                                  memory_limit_mb: Optional[int] = None):
        """Apply memory-specific optimizations"""
        with self._lock:
            if session_id not in self._applied_configs:
                self._applied_configs[session_id] = set()
            
            applied = self._applied_configs[session_id]
            
            if memory_limit_mb:
                self._safe_add_config_entry(session_options, applied, "session.memory_limit_mb", str(memory_limit_mb))
            
            # Memory arena optimizations
            self._safe_add_config_entry(session_options, applied, "session.enable_memory_arena", "1")
            self._safe_add_config_entry(session_options, applied, "session.arena_extend_strategy", "kSameAsRequested")
    
    def apply_performance_optimizations(self, session_options: Any, session_id: str = "default",
                                      inter_op_threads: Optional[int] = None,
                                      intra_op_threads: Optional[int] = None):
        """Apply performance-specific optimizations"""
        if inter_op_threads:
            session_options.inter_op_num_threads = inter_op_threads
        
        if intra_op_threads:
            session_options.intra_op_num_threads = intra_op_threads
        
        logger.debug(f"Applied performance optimizations: inter_op={inter_op_threads}, intra_op={intra_op_threads}")
    
    def clear_session_config(self, session_id: str):
        """Clear configuration tracking for a session"""
        with self._lock:
            if session_id in self._applied_configs:
                del self._applied_configs[session_id]
                logger.debug(f"Cleared ONNX config tracking for session '{session_id}'")

# Global instance
_onnx_config_manager = None
_manager_lock = threading.Lock()

def get_onnx_config_manager() -> ONNXConfigManager:
    """Get the global ONNX configuration manager instance"""
    global _onnx_config_manager
    
    if _onnx_config_manager is None:
        with _manager_lock:
            if _onnx_config_manager is None:
                _onnx_config_manager = ONNXConfigManager()
    
    return _onnx_config_manager

def create_optimized_session_options(session_id: str = "default", 
                                   cpu_info: Optional[Dict] = None,
                                   memory_limit_mb: Optional[int] = None,
                                   inter_op_threads: Optional[int] = None,
                                   intra_op_threads: Optional[int] = None) -> Any:
    """Create fully optimized ONNX session options"""
    manager = get_onnx_config_manager()
    session_options = manager.create_session_options(session_id)
    
    if session_options is None:
        return None
    
    # Apply all optimizations
    if cpu_info:
        manager.apply_cpu_optimizations(session_options, session_id, cpu_info)
    
    if memory_limit_mb:
        manager.apply_memory_optimizations(session_options, session_id, memory_limit_mb)
    
    if inter_op_threads or intra_op_threads:
        manager.apply_performance_optimizations(session_options, session_id, inter_op_threads, intra_op_threads)
    
    return session_options
