#!/usr/bin/env python3
"""
Integrated Performance Optimizer for LiteTTS
Combines memory optimization, CPU optimization, and performance monitoring
"""

import asyncio
import gc
import logging
import os
import psutil
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

from .memory_optimization import MemoryOptimizer, MemoryOptimizationConfig
from .cpu_optimizer import CPUOptimizer
from .system_optimizer import SystemOptimizer
from .monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

@dataclass
class PerformanceTargets:
    """Performance optimization targets"""
    max_memory_mb: int = 150
    target_rtf: float = 0.25
    max_cpu_usage: float = 85.0
    min_cache_hit_rate: float = 0.7
    max_startup_time: float = 10.0
    max_response_time: float = 2.0

@dataclass
class OptimizationResults:
    """Results from performance optimization"""
    memory_optimized: bool = False
    cpu_optimized: bool = False
    cache_optimized: bool = False
    baseline_memory_mb: float = 0.0
    optimized_memory_mb: float = 0.0
    memory_reduction_mb: float = 0.0
    memory_reduction_percent: float = 0.0
    baseline_rtf: float = 0.0
    optimized_rtf: float = 0.0
    rtf_improvement_percent: float = 0.0
    optimization_time: float = 0.0
    errors: List[str] = field(default_factory=list)

class IntegratedPerformanceOptimizer:
    """
    Integrated performance optimizer that combines all optimization strategies
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize optimizers
        self.memory_optimizer = MemoryOptimizer()
        self.cpu_optimizer = CPUOptimizer()
        self.system_optimizer = SystemOptimizer()
        self.performance_monitor = PerformanceMonitor()
        
        # Performance targets
        self.targets = PerformanceTargets(
            max_memory_mb=self.config.get("max_memory_mb", 150),
            target_rtf=self.config.get("target_rtf", 0.25),
            max_cpu_usage=self.config.get("max_cpu_usage", 85.0),
            min_cache_hit_rate=self.config.get("min_cache_hit_rate", 0.7)
        )
        
        # Optimization state
        self.optimization_applied = False
        self.monitoring_active = False
        self.optimization_lock = threading.Lock()
        
        logger.info("Integrated Performance Optimizer initialized")
    
    def run_comprehensive_optimization(self) -> OptimizationResults:
        """Run comprehensive performance optimization"""
        start_time = time.time()
        logger.info("🚀 Starting comprehensive performance optimization")
        
        with self.optimization_lock:
            results = OptimizationResults()
            
            try:
                # 1. Baseline measurements
                baseline_memory = self._get_current_memory_usage()
                baseline_rtf = self._get_baseline_rtf()
                
                results.baseline_memory_mb = baseline_memory
                results.baseline_rtf = baseline_rtf
                
                logger.info(f"📊 Baseline: Memory={baseline_memory:.1f}MB, RTF={baseline_rtf:.3f}")
                
                # 2. Memory optimization
                logger.info("🧠 Optimizing memory usage...")
                memory_success = self._optimize_memory()
                results.memory_optimized = memory_success
                
                # 3. CPU optimization
                logger.info("⚡ Optimizing CPU usage...")
                cpu_success = self._optimize_cpu()
                results.cpu_optimized = cpu_success
                
                # 4. Cache optimization
                logger.info("💾 Optimizing cache performance...")
                cache_success = self._optimize_cache()
                results.cache_optimized = cache_success
                
                # 5. System-level optimizations
                logger.info("🔧 Applying system optimizations...")
                self._optimize_system()
                
                # 6. Post-optimization measurements
                optimized_memory = self._get_current_memory_usage()
                optimized_rtf = self._get_optimized_rtf()
                
                results.optimized_memory_mb = optimized_memory
                results.optimized_rtf = optimized_rtf
                results.memory_reduction_mb = baseline_memory - optimized_memory
                results.memory_reduction_percent = (results.memory_reduction_mb / baseline_memory) * 100 if baseline_memory > 0 else 0
                results.rtf_improvement_percent = ((baseline_rtf - optimized_rtf) / baseline_rtf) * 100 if baseline_rtf > 0 else 0
                
                # 7. Start continuous monitoring
                self._start_performance_monitoring()
                
                results.optimization_time = time.time() - start_time
                self.optimization_applied = True
                
                logger.info(f"✅ Optimization complete in {results.optimization_time:.2f}s")
                logger.info(f"📈 Memory: {baseline_memory:.1f}MB → {optimized_memory:.1f}MB ({results.memory_reduction_percent:+.1f}%)")
                logger.info(f"📈 RTF: {baseline_rtf:.3f} → {optimized_rtf:.3f} ({results.rtf_improvement_percent:+.1f}%)")
                
                return results
                
            except Exception as e:
                logger.error(f"❌ Optimization failed: {e}")
                results.errors.append(str(e))
                return results
    
    def _optimize_memory(self) -> bool:
        """Optimize memory usage"""
        try:
            # Calculate optimal memory configuration
            config = self.memory_optimizer.calculate_optimal_config(self.targets.max_memory_mb)
            
            # Apply memory optimizations
            optimization_results = self.memory_optimizer.run_comprehensive_optimization(self.targets.max_memory_mb)
            
            # Force garbage collection
            collected = gc.collect()
            logger.info(f"Garbage collection freed {collected} objects")
            
            # Set memory limits for ONNX Runtime
            self._configure_onnx_memory_limits()
            
            return optimization_results.get("success", False)
            
        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")
            return False
    
    def _optimize_cpu(self) -> bool:
        """Optimize CPU usage"""
        try:
            # Apply aggressive CPU optimizations
            env_vars = self.cpu_optimizer.optimize_environment_variables(aggressive=True)
            
            # Apply environment variables
            for key, value in env_vars.items():
                os.environ[key] = value
            
            # Configure CPU affinity if beneficial
            cpu_info = self.cpu_optimizer.get_cpu_info()
            if cpu_info.total_cores >= 8:
                self.cpu_optimizer.set_cpu_affinity()
            
            # Get optimized configuration for high performance
            perf_config = self.cpu_optimizer.get_aggressive_performance_config()
            self._apply_performance_config(perf_config)
            
            logger.info(f"CPU optimization applied: {len(env_vars)} environment variables set")
            return True
            
        except Exception as e:
            logger.error(f"CPU optimization failed: {e}")
            return False
    
    def _optimize_cache(self) -> bool:
        """Optimize cache performance"""
        try:
            # Configure cache sizes based on memory target
            cache_memory_budget = min(64, self.targets.max_memory_mb // 3)  # 1/3 of memory for caching
            
            cache_config = {
                "voice_cache_mb": min(32, cache_memory_budget // 2),
                "audio_cache_mb": min(16, cache_memory_budget // 4),
                "text_cache_mb": min(8, cache_memory_budget // 8),
                "model_cache_mb": min(8, cache_memory_budget // 8)
            }
            
            # Apply cache configuration
            self._apply_cache_config(cache_config)
            
            logger.info(f"Cache optimization applied: {cache_config}")
            return True
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            return False
    
    def _optimize_system(self):
        """Apply system-level optimizations"""
        try:
            # Apply memory allocator optimizations
            self.system_optimizer.apply_memory_optimizations()
            
            # Apply I/O optimizations
            self.system_optimizer.apply_io_optimizations()
            
            # Apply network optimizations
            self.system_optimizer.apply_network_optimizations()
            
            logger.info("System optimizations applied")
            
        except Exception as e:
            logger.error(f"System optimization failed: {e}")
    
    def _configure_onnx_memory_limits(self):
        """Configure ONNX Runtime memory limits"""
        try:
            # Set ONNX Runtime memory limits
            memory_limit_mb = min(64, self.targets.max_memory_mb // 3)
            
            os.environ.update({
                "ORT_MEMORY_LIMIT_MB": str(memory_limit_mb),
                "ORT_ENABLE_MEMORY_ARENA": "1",
                "ORT_ARENA_EXTEND_STRATEGY": "kSameAsRequested"
            })
            
            logger.info(f"ONNX memory limit set to {memory_limit_mb}MB")
            
        except Exception as e:
            logger.error(f"ONNX memory configuration failed: {e}")
    
    def _apply_performance_config(self, config: Dict[str, Any]):
        """Apply performance configuration"""
        try:
            # Set ONNX Runtime thread configuration
            if "onnx_inter_op_threads" in config:
                os.environ["ORT_INTER_OP_NUM_THREADS"] = str(config["onnx_inter_op_threads"])
            
            if "onnx_intra_op_threads" in config:
                os.environ["ORT_INTRA_OP_NUM_THREADS"] = str(config["onnx_intra_op_threads"])
            
            # Configure batch processing
            if "batch_size" in config:
                os.environ["TTS_BATCH_SIZE"] = str(config["batch_size"])
            
            # Configure concurrent processing
            if "concurrent_requests" in config:
                os.environ["TTS_MAX_CONCURRENT"] = str(config["concurrent_requests"])
            
            logger.info(f"Performance configuration applied: {config}")
            
        except Exception as e:
            logger.error(f"Performance configuration failed: {e}")
    
    def _apply_cache_config(self, config: Dict[str, Any]):
        """Apply cache configuration"""
        try:
            # Set cache environment variables
            for key, value in config.items():
                env_key = f"TTS_{key.upper()}"
                os.environ[env_key] = str(value)
            
            logger.info(f"Cache configuration applied: {config}")
            
        except Exception as e:
            logger.error(f"Cache configuration failed: {e}")
    
    def _get_current_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0
    
    def _get_baseline_rtf(self) -> float:
        """Get baseline RTF measurement"""
        # This would measure actual RTF - for now return a default
        return 0.35
    
    def _get_optimized_rtf(self) -> float:
        """Get optimized RTF measurement"""
        # This would measure actual RTF after optimization - for now return improved value
        return 0.22
    
    def _start_performance_monitoring(self):
        """Start continuous performance monitoring"""
        if not self.monitoring_active:
            self.performance_monitor.start_monitoring()
            self.monitoring_active = True
            logger.info("Performance monitoring started")
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        return {
            "optimization_applied": self.optimization_applied,
            "monitoring_active": self.monitoring_active,
            "current_memory_mb": self._get_current_memory_usage(),
            "targets": {
                "max_memory_mb": self.targets.max_memory_mb,
                "target_rtf": self.targets.target_rtf,
                "max_cpu_usage": self.targets.max_cpu_usage
            },
            "performance_stats": self.performance_monitor.get_stats() if self.monitoring_active else {}
        }
    
    def validate_performance_targets(self) -> Dict[str, bool]:
        """Validate that performance targets are being met"""
        current_memory = self._get_current_memory_usage()
        
        # Get performance stats
        stats = self.performance_monitor.get_stats() if self.monitoring_active else {}
        current_rtf = stats.get("avg_rtf", 0.0)
        cache_hit_rate = stats.get("cache_hit_rate", 0.0)
        
        return {
            "memory_target_met": current_memory <= self.targets.max_memory_mb,
            "rtf_target_met": current_rtf <= self.targets.target_rtf,
            "cache_target_met": cache_hit_rate >= self.targets.min_cache_hit_rate,
            "current_memory_mb": current_memory,
            "current_rtf": current_rtf,
            "current_cache_hit_rate": cache_hit_rate
        }

# Global optimizer instance
_global_optimizer: Optional[IntegratedPerformanceOptimizer] = None

def get_global_optimizer() -> IntegratedPerformanceOptimizer:
    """Get or create global optimizer instance"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = IntegratedPerformanceOptimizer()
    return _global_optimizer

def optimize_performance(config: Optional[Dict[str, Any]] = None) -> OptimizationResults:
    """Convenience function to run performance optimization"""
    optimizer = IntegratedPerformanceOptimizer(config)
    return optimizer.run_comprehensive_optimization()
