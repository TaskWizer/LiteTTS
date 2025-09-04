#!/usr/bin/env python3
"""
Environment Variable Bridge for LiteTTS Configuration
Bridges environment variables to application configuration for Docker deployments
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EnvironmentConfig:
    """Configuration loaded from environment variables"""
    # Performance settings
    enable_performance_optimization: bool = True
    max_memory_mb: int = 4096
    target_rtf: float = 0.25
    
    # Dynamic CPU allocation settings
    dynamic_cpu_allocation_enabled: bool = True
    cpu_target: float = 75.0
    aggressive_mode: bool = True
    thermal_protection: bool = True
    onnx_integration: bool = True
    update_environment: bool = True
    
    # Threading settings
    omp_num_threads: Optional[int] = None
    mkl_num_threads: Optional[int] = None
    openblas_num_threads: Optional[int] = None
    veclib_maximum_threads: Optional[int] = None
    
    # ONNX Runtime settings
    ort_disable_all_optimization: bool = False
    ort_enable_cpu_fp16_ops: bool = True
    ort_graph_optimization_level: str = "all"
    ort_execution_mode: str = "parallel"
    ort_enable_mem_pattern: bool = True
    ort_enable_cpu_mem_arena: bool = True
    ort_enable_mem_reuse: bool = True
    
    # Memory allocation settings
    malloc_arena_max: int = 4
    malloc_mmap_threshold: int = 131072
    malloc_trim_threshold: int = 131072
    malloc_top_pad: int = 131072
    malloc_mmap_max: int = 65536

class EnvironmentConfigLoader:
    """Loads configuration from environment variables"""
    
    def __init__(self):
        self.config = EnvironmentConfig()
        self._load_from_environment()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        try:
            # Performance settings
            self.config.enable_performance_optimization = self._get_bool_env(
                "ENABLE_PERFORMANCE_OPTIMIZATION", True
            )
            self.config.max_memory_mb = self._get_int_env("MAX_MEMORY_MB", 4096)
            self.config.target_rtf = self._get_float_env("TARGET_RTF", 0.25)
            
            # Dynamic CPU allocation settings
            self.config.dynamic_cpu_allocation_enabled = self._get_bool_env(
                "DYNAMIC_CPU_ALLOCATION_ENABLED", True
            )
            self.config.cpu_target = self._get_float_env("CPU_TARGET", 75.0)
            self.config.aggressive_mode = self._get_bool_env("AGGRESSIVE_MODE", True)
            self.config.thermal_protection = self._get_bool_env("THERMAL_PROTECTION", True)
            self.config.onnx_integration = self._get_bool_env("ONNX_INTEGRATION", True)
            self.config.update_environment = self._get_bool_env("UPDATE_ENVIRONMENT", True)
            
            # Threading settings
            self.config.omp_num_threads = self._get_int_env("OMP_NUM_THREADS")
            self.config.mkl_num_threads = self._get_int_env("MKL_NUM_THREADS")
            self.config.openblas_num_threads = self._get_int_env("OPENBLAS_NUM_THREADS")
            self.config.veclib_maximum_threads = self._get_int_env("VECLIB_MAXIMUM_THREADS")
            
            # ONNX Runtime settings
            self.config.ort_disable_all_optimization = self._get_bool_env(
                "ORT_DISABLE_ALL_OPTIMIZATION", False
            )
            self.config.ort_enable_cpu_fp16_ops = self._get_bool_env(
                "ORT_ENABLE_CPU_FP16_OPS", True
            )
            self.config.ort_graph_optimization_level = os.getenv(
                "ORT_GRAPH_OPTIMIZATION_LEVEL", "all"
            )
            self.config.ort_execution_mode = os.getenv("ORT_EXECUTION_MODE", "parallel")
            self.config.ort_enable_mem_pattern = self._get_bool_env(
                "ORT_ENABLE_MEM_PATTERN", True
            )
            self.config.ort_enable_cpu_mem_arena = self._get_bool_env(
                "ORT_ENABLE_CPU_MEM_ARENA", True
            )
            self.config.ort_enable_mem_reuse = self._get_bool_env(
                "ORT_ENABLE_MEM_REUSE", True
            )
            
            # Memory allocation settings
            self.config.malloc_arena_max = self._get_int_env("MALLOC_ARENA_MAX", 4)
            self.config.malloc_mmap_threshold = self._get_int_env("MALLOC_MMAP_THRESHOLD_", 131072)
            self.config.malloc_trim_threshold = self._get_int_env("MALLOC_TRIM_THRESHOLD_", 131072)
            self.config.malloc_top_pad = self._get_int_env("MALLOC_TOP_PAD_", 131072)
            self.config.malloc_mmap_max = self._get_int_env("MALLOC_MMAP_MAX_", 65536)
            
            logger.info("Environment configuration loaded successfully")
            logger.info(f"CPU target: {self.config.cpu_target}%, "
                       f"Aggressive mode: {self.config.aggressive_mode}, "
                       f"Memory limit: {self.config.max_memory_mb}MB")
            
        except Exception as e:
            logger.error(f"Failed to load environment configuration: {e}")
    
    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")
    
    def _get_int_env(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Get integer environment variable"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
            return default
    
    def _get_float_env(self, key: str, default: float = 0.0) -> float:
        """Get float environment variable"""
        value = os.getenv(key, str(default))
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid float value for {key}: {value}, using default: {default}")
            return default
    
    def get_dynamic_cpu_allocation_config(self) -> Dict[str, Any]:
        """Get dynamic CPU allocation configuration"""
        return {
            "enabled": self.config.dynamic_cpu_allocation_enabled,
            "cpu_target": self.config.cpu_target,
            "aggressive_mode": self.config.aggressive_mode,
            "thermal_protection": self.config.thermal_protection,
            "onnx_integration": self.config.onnx_integration,
            "update_environment": self.config.update_environment
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return {
            "memory_optimization": self.config.enable_performance_optimization,
            "max_memory_mb": self.config.max_memory_mb,
            "target_rtf": self.config.target_rtf,
            "dynamic_cpu_allocation": self.get_dynamic_cpu_allocation_config()
        }
    
    def apply_onnx_environment_variables(self):
        """Apply ONNX Runtime environment variables"""
        try:
            onnx_env_vars = {
                "ORT_DISABLE_ALL_OPTIMIZATION": "0" if not self.config.ort_disable_all_optimization else "1",
                "ORT_ENABLE_CPU_FP16_OPS": "1" if self.config.ort_enable_cpu_fp16_ops else "0",
                "ORT_GRAPH_OPTIMIZATION_LEVEL": self.config.ort_graph_optimization_level,
                "ORT_EXECUTION_MODE": self.config.ort_execution_mode,
                "ORT_ENABLE_MEM_PATTERN": "1" if self.config.ort_enable_mem_pattern else "0",
                "ORT_ENABLE_CPU_MEM_ARENA": "1" if self.config.ort_enable_cpu_mem_arena else "0",
                "ORT_ENABLE_MEM_REUSE": "1" if self.config.ort_enable_mem_reuse else "0",
            }
            
            for key, value in onnx_env_vars.items():
                if key not in os.environ:
                    os.environ[key] = value
            
            logger.info("Applied ONNX Runtime environment variables")
            
        except Exception as e:
            logger.error(f"Failed to apply ONNX environment variables: {e}")
    
    def apply_memory_allocation_variables(self):
        """Apply memory allocation environment variables"""
        try:
            malloc_env_vars = {
                "MALLOC_ARENA_MAX": str(self.config.malloc_arena_max),
                "MALLOC_MMAP_THRESHOLD_": str(self.config.malloc_mmap_threshold),
                "MALLOC_TRIM_THRESHOLD_": str(self.config.malloc_trim_threshold),
                "MALLOC_TOP_PAD_": str(self.config.malloc_top_pad),
                "MALLOC_MMAP_MAX_": str(self.config.malloc_mmap_max),
            }
            
            for key, value in malloc_env_vars.items():
                if key not in os.environ:
                    os.environ[key] = value
            
            logger.info("Applied memory allocation environment variables")
            
        except Exception as e:
            logger.error(f"Failed to apply memory allocation variables: {e}")
    
    def apply_threading_variables(self):
        """Apply threading environment variables"""
        try:
            threading_vars = {}
            
            if self.config.omp_num_threads is not None:
                threading_vars["OMP_NUM_THREADS"] = str(self.config.omp_num_threads)
            if self.config.mkl_num_threads is not None:
                threading_vars["MKL_NUM_THREADS"] = str(self.config.mkl_num_threads)
            if self.config.openblas_num_threads is not None:
                threading_vars["OPENBLAS_NUM_THREADS"] = str(self.config.openblas_num_threads)
            if self.config.veclib_maximum_threads is not None:
                threading_vars["VECLIB_MAXIMUM_THREADS"] = str(self.config.veclib_maximum_threads)
            
            for key, value in threading_vars.items():
                if key not in os.environ:
                    os.environ[key] = value
            
            if threading_vars:
                logger.info(f"Applied threading environment variables: {list(threading_vars.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to apply threading variables: {e}")
    
    def apply_all_environment_variables(self):
        """Apply all environment variables"""
        self.apply_onnx_environment_variables()
        self.apply_memory_allocation_variables()
        self.apply_threading_variables()

# Global environment config loader
_env_config_loader: Optional[EnvironmentConfigLoader] = None

def get_environment_config() -> EnvironmentConfigLoader:
    """Get or create global environment config loader"""
    global _env_config_loader
    if _env_config_loader is None:
        _env_config_loader = EnvironmentConfigLoader()
    return _env_config_loader

def initialize_environment_config():
    """Initialize environment configuration and apply variables"""
    try:
        env_config = get_environment_config()
        env_config.apply_all_environment_variables()
        logger.info("Environment configuration initialized successfully")
        return env_config
    except Exception as e:
        logger.error(f"Failed to initialize environment configuration: {e}")
        return None
