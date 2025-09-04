#!/usr/bin/env python3
"""
Memory Usage and Pre-allocation Optimization System
Implement memory pre-allocation strategies, optimize caching mechanisms, target <150MB additional memory usage
"""

import os
import sys
import json
import logging
import psutil
import time
import gc
import tracemalloc
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import threading

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MemoryProfile:
    """Memory usage profile"""
    total_memory_mb: float
    available_memory_mb: float
    used_memory_mb: float
    process_memory_mb: float
    process_memory_percent: float
    peak_memory_mb: float
    memory_growth_mb: float
    gc_collections: Dict[str, int]
    largest_objects: List[Dict[str, Any]]

@dataclass
class MemoryOptimizationConfig:
    """Memory optimization configuration"""
    enable_pre_allocation: bool
    pre_allocation_size_mb: int
    enable_memory_pooling: bool
    pool_size_mb: int
    enable_aggressive_gc: bool
    gc_threshold_mb: int
    enable_memory_mapping: bool
    cache_size_limit_mb: int
    enable_lazy_loading: bool
    memory_monitoring_interval: float

class MemoryOptimizer:
    """Memory usage and pre-allocation optimization system"""
    
    def __init__(self):
        self.results_dir = Path("test_results/memory_optimization")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory monitoring
        self.baseline_memory = None
        self.peak_memory = 0
        self.memory_history = []
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Pre-allocated memory pools
        self.memory_pools = {}
        self.allocated_buffers = []
        
        # Start memory tracking
        tracemalloc.start()
        
    def get_current_memory_profile(self) -> MemoryProfile:
        """Get current memory usage profile"""
        # System memory
        memory = psutil.virtual_memory()
        
        # Process memory
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # Peak memory tracking
        current_memory_mb = process_memory.rss / (1024 * 1024)
        if current_memory_mb > self.peak_memory:
            self.peak_memory = current_memory_mb
        
        # Memory growth calculation
        memory_growth = 0
        if self.baseline_memory:
            memory_growth = current_memory_mb - self.baseline_memory
        
        # Garbage collection stats
        gc_stats = {
            f"generation_{i}": gc.get_count()[i] for i in range(len(gc.get_count()))
        }
        
        # Get largest objects (top 10)
        largest_objects = []
        try:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')[:10]
            
            for stat in top_stats:
                largest_objects.append({
                    "size_mb": stat.size / (1024 * 1024),
                    "count": stat.count,
                    "filename": stat.traceback.format()[-1] if stat.traceback else "unknown"
                })
        except Exception as e:
            logger.warning(f"Could not get memory traceback: {e}")
        
        profile = MemoryProfile(
            total_memory_mb=memory.total / (1024 * 1024),
            available_memory_mb=memory.available / (1024 * 1024),
            used_memory_mb=memory.used / (1024 * 1024),
            process_memory_mb=current_memory_mb,
            process_memory_percent=process_memory.rss / memory.total * 100,
            peak_memory_mb=self.peak_memory,
            memory_growth_mb=memory_growth,
            gc_collections=gc_stats,
            largest_objects=largest_objects
        )
        
        return profile
    
    def set_baseline_memory(self):
        """Set baseline memory usage"""
        profile = self.get_current_memory_profile()
        self.baseline_memory = profile.process_memory_mb
        logger.info(f"Baseline memory set to: {self.baseline_memory:.2f} MB")
    
    def start_memory_monitoring(self, interval: float = 1.0):
        """Start continuous memory monitoring"""
        self.monitoring_active = True
        self.memory_history = []
        
        def monitor_loop():
            while self.monitoring_active:
                try:
                    profile = self.get_current_memory_profile()
                    self.memory_history.append({
                        "timestamp": time.time(),
                        "memory_mb": profile.process_memory_mb,
                        "memory_percent": profile.process_memory_percent
                    })
                    time.sleep(interval)
                except Exception as e:
                    logger.warning(f"Memory monitoring error: {e}")
        
        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.start()
        logger.info("Memory monitoring started")
    
    def stop_memory_monitoring(self) -> Dict[str, Any]:
        """Stop memory monitoring and return statistics"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        if not self.memory_history:
            return {"error": "No monitoring data collected"}
        
        memory_values = [entry["memory_mb"] for entry in self.memory_history]
        
        stats = {
            "duration_seconds": self.memory_history[-1]["timestamp"] - self.memory_history[0]["timestamp"],
            "samples_collected": len(self.memory_history),
            "min_memory_mb": min(memory_values),
            "max_memory_mb": max(memory_values),
            "avg_memory_mb": sum(memory_values) / len(memory_values),
            "memory_variance": self._calculate_variance(memory_values),
            "peak_growth_mb": max(memory_values) - min(memory_values)
        }
        
        logger.info("Memory monitoring stopped")
        return stats
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of memory values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def implement_memory_pre_allocation(self, config: MemoryOptimizationConfig) -> bool:
        """Implement memory pre-allocation strategies"""
        logger.info("Implementing memory pre-allocation...")
        
        try:
            if config.enable_pre_allocation:
                # Pre-allocate memory buffers for common operations
                buffer_sizes = [
                    1024 * 1024,      # 1MB buffer
                    4 * 1024 * 1024,  # 4MB buffer
                    16 * 1024 * 1024, # 16MB buffer
                    32 * 1024 * 1024  # 32MB buffer
                ]
                
                total_allocated = 0
                for size in buffer_sizes:
                    if total_allocated + size / (1024 * 1024) <= config.pre_allocation_size_mb:
                        buffer = bytearray(size)
                        self.allocated_buffers.append(buffer)
                        total_allocated += size / (1024 * 1024)
                        logger.info(f"Pre-allocated {size / (1024 * 1024):.1f}MB buffer")
                
                logger.info(f"Total pre-allocated memory: {total_allocated:.1f}MB")
            
            if config.enable_memory_pooling:
                # Create memory pools for different object types
                self.memory_pools = {
                    "audio_buffers": [],
                    "text_buffers": [],
                    "tensor_buffers": []
                }
                logger.info("Memory pools initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"Memory pre-allocation failed: {e}")
            return False
    
    def optimize_garbage_collection(self, config: MemoryOptimizationConfig):
        """Optimize garbage collection settings with improved thresholds"""
        logger.info("Optimizing garbage collection...")

        if config.enable_aggressive_gc:
            # Set aggressive GC thresholds for memory-constrained environments
            # More frequent collection for generation 0 (short-lived objects)
            # Less frequent for generation 1 and 2 (long-lived objects)
            gc.set_threshold(500, 8, 8)  # More aggressive than default (700, 10, 10)
            logger.info("⚡ Set AGGRESSIVE GC thresholds: (500, 8, 8)")

            # Set up periodic forced collection for aggressive mode
            self._setup_periodic_gc(interval=30.0)  # Every 30 seconds

        else:
            # Set conservative GC thresholds for performance-focused environments
            # Less frequent collection to reduce GC overhead
            gc.set_threshold(1000, 15, 15)  # Less aggressive than default
            logger.info("🔒 Set CONSERVATIVE GC thresholds: (1000, 15, 15)")

            # Set up periodic forced collection for conservative mode
            self._setup_periodic_gc(interval=120.0)  # Every 2 minutes

        # Enable automatic garbage collection
        gc.enable()

        # Force initial collection and log statistics
        collected_gen0 = gc.collect(0)  # Collect generation 0
        collected_gen1 = gc.collect(1)  # Collect generation 1
        collected_gen2 = gc.collect(2)  # Collect generation 2

        total_collected = collected_gen0 + collected_gen1 + collected_gen2
        logger.info(f"Initial GC collected {total_collected} objects "
                   f"(Gen0: {collected_gen0}, Gen1: {collected_gen1}, Gen2: {collected_gen2})")

        # Log current GC statistics
        gc_stats = gc.get_stats()
        logger.info(f"GC statistics: {gc_stats}")

    def _setup_periodic_gc(self, interval: float):
        """Setup periodic garbage collection"""
        def periodic_gc():
            while self.monitoring_active:
                try:
                    time.sleep(interval)
                    if self.monitoring_active:
                        # Perform full garbage collection
                        collected = gc.collect()
                        if collected > 0:
                            logger.debug(f"Periodic GC collected {collected} objects")

                        # Check for memory pressure and adjust if needed
                        self._check_memory_pressure()

                except Exception as e:
                    logger.warning(f"Periodic GC error: {e}")

        if not hasattr(self, 'gc_thread') or not self.gc_thread.is_alive():
            self.gc_thread = threading.Thread(target=periodic_gc, daemon=True)
            self.gc_thread.start()
            logger.info(f"Started periodic GC with {interval}s interval")

    def _check_memory_pressure(self):
        """Check for memory pressure and take action if needed"""
        try:
            current_profile = self.get_current_memory_profile()

            # Check if memory usage is high
            if current_profile.process_memory_percent > 15:  # > 15% of system memory
                logger.warning(f"High memory usage detected: {current_profile.process_memory_mb:.1f}MB "
                             f"({current_profile.process_memory_percent:.1f}%)")

                # Force aggressive garbage collection
                collected = gc.collect()
                logger.info(f"Memory pressure GC collected {collected} objects")

                # Clear any cached data if memory pressure is severe
                if current_profile.process_memory_percent > 20:  # > 20% of system memory
                    self._emergency_memory_cleanup()

        except Exception as e:
            logger.warning(f"Memory pressure check failed: {e}")

    def _emergency_memory_cleanup(self):
        """Emergency memory cleanup under severe memory pressure"""
        logger.warning("🚨 Emergency memory cleanup triggered")

        try:
            # Clear synthesis optimizer caches
            try:
                from LiteTTS.performance.synthesis_optimizer import get_synthesis_optimizer
                synthesis_optimizer = get_synthesis_optimizer()
                synthesis_optimizer.reset_caches()
                logger.info("Cleared synthesis optimizer caches")
            except Exception:
                pass

            # Clear preloader caches
            try:
                from LiteTTS.cache.preloader import get_preloader
                preloader = get_preloader()
                if hasattr(preloader, 'clear_cache'):
                    preloader.clear_cache()
                    logger.info("Cleared preloader caches")
            except Exception:
                pass

            # Force full garbage collection
            collected = gc.collect()
            logger.info(f"Emergency GC collected {collected} objects")

            # Log memory status after cleanup
            post_cleanup_profile = self.get_current_memory_profile()
            logger.info(f"Memory after cleanup: {post_cleanup_profile.process_memory_mb:.1f}MB "
                       f"({post_cleanup_profile.process_memory_percent:.1f}%)")

        except Exception as e:
            logger.error(f"Emergency memory cleanup failed: {e}")
    
    def implement_caching_optimization(self, config: MemoryOptimizationConfig) -> Dict[str, Any]:
        """Implement optimized caching mechanisms"""
        logger.info("Implementing caching optimization...")
        
        cache_config = {
            "voice_cache": {
                "enabled": True,
                "max_size_mb": min(50, config.cache_size_limit_mb // 4),
                "ttl_seconds": 3600,
                "eviction_policy": "lru"
            },
            "model_cache": {
                "enabled": True,
                "max_size_mb": min(100, config.cache_size_limit_mb // 2),
                "ttl_seconds": 7200,
                "eviction_policy": "lru"
            },
            "text_processing_cache": {
                "enabled": True,
                "max_size_mb": min(25, config.cache_size_limit_mb // 8),
                "ttl_seconds": 1800,
                "eviction_policy": "lru"
            },
            "audio_cache": {
                "enabled": config.cache_size_limit_mb > 50,
                "max_size_mb": min(25, config.cache_size_limit_mb // 8),
                "ttl_seconds": 900,
                "eviction_policy": "lru"
            }
        }
        
        logger.info(f"Cache configuration: {cache_config}")
        return cache_config
    
    def monitor_memory_leaks(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """Monitor for memory leaks"""
        logger.info(f"Monitoring for memory leaks for {duration_seconds} seconds...")
        
        # Take initial snapshot
        initial_snapshot = tracemalloc.take_snapshot()
        initial_profile = self.get_current_memory_profile()
        
        # Wait and monitor
        time.sleep(duration_seconds)
        
        # Take final snapshot
        final_snapshot = tracemalloc.take_snapshot()
        final_profile = self.get_current_memory_profile()
        
        # Compare snapshots
        top_stats = final_snapshot.compare_to(initial_snapshot, 'lineno')
        
        leak_analysis = {
            "memory_growth_mb": final_profile.process_memory_mb - initial_profile.process_memory_mb,
            "monitoring_duration": duration_seconds,
            "potential_leaks": [],
            "top_memory_increases": []
        }
        
        # Analyze top memory increases
        for stat in top_stats[:10]:
            if stat.size_diff > 1024 * 1024:  # > 1MB increase
                leak_analysis["top_memory_increases"].append({
                    "size_diff_mb": stat.size_diff / (1024 * 1024),
                    "count_diff": stat.count_diff,
                    "filename": stat.traceback.format()[-1] if stat.traceback else "unknown"
                })
        
        # Identify potential leaks (significant growth without corresponding decrease)
        if leak_analysis["memory_growth_mb"] > 50:  # > 50MB growth
            leak_analysis["potential_leaks"].append("Significant memory growth detected")
        
        logger.info(f"Memory leak analysis completed. Growth: {leak_analysis['memory_growth_mb']:.2f}MB")
        return leak_analysis
    
    def calculate_optimal_config(self, target_memory_mb: int = 1024) -> MemoryOptimizationConfig:
        """Calculate optimal memory configuration with realistic targets"""
        logger.info(f"Calculating optimal memory configuration for {target_memory_mb}MB target...")

        # Get current system memory
        system_memory = psutil.virtual_memory()
        total_memory_gb = system_memory.total / (1024**3)
        available_mb = system_memory.available / (1024 * 1024)

        # Adjust target based on system memory
        if total_memory_gb < 4:
            # Low memory system - be conservative
            adjusted_target = min(target_memory_mb, 512)
            enable_aggressive_gc = True
            logger.info(f"Low memory system detected ({total_memory_gb:.1f}GB), using conservative target: {adjusted_target}MB")
        elif total_memory_gb < 8:
            # Medium memory system - balanced approach
            adjusted_target = min(target_memory_mb, 1024)
            enable_aggressive_gc = target_memory_mb < 800
            logger.info(f"Medium memory system detected ({total_memory_gb:.1f}GB), using balanced target: {adjusted_target}MB")
        else:
            # High memory system - allow more memory usage
            adjusted_target = target_memory_mb
            enable_aggressive_gc = False
            logger.info(f"High memory system detected ({total_memory_gb:.1f}GB), using full target: {adjusted_target}MB")

        # Calculate allocations based on adjusted target
        pre_allocation_size = min(64, adjusted_target // 8)   # 12.5% for pre-allocation
        pool_size = min(32, adjusted_target // 16)            # 6.25% for pooling
        cache_size = min(256, adjusted_target // 2)           # 50% for caching

        # Ensure minimum viable sizes
        pre_allocation_size = max(16, pre_allocation_size)
        pool_size = max(8, pool_size)
        cache_size = max(64, cache_size)

        config = MemoryOptimizationConfig(
            enable_pre_allocation=True,
            pre_allocation_size_mb=pre_allocation_size,
            enable_memory_pooling=True,
            pool_size_mb=pool_size,
            enable_aggressive_gc=enable_aggressive_gc,
            gc_threshold_mb=adjusted_target // 20,  # 5% of target for GC threshold
            enable_memory_mapping=available_mb > 2048,  # Only if >2GB available
            cache_size_limit_mb=cache_size,
            enable_lazy_loading=True,
            memory_monitoring_interval=2.0 if enable_aggressive_gc else 5.0
        )

        logger.info(f"🎯 Optimal config calculated:")
        logger.info(f"   Pre-allocation: {pre_allocation_size}MB")
        logger.info(f"   Memory pooling: {pool_size}MB")
        logger.info(f"   Cache limit: {cache_size}MB")
        logger.info(f"   Aggressive GC: {enable_aggressive_gc}")
        logger.info(f"   Memory mapping: {config.enable_memory_mapping}")

        return config
    
    def run_comprehensive_optimization(self, target_memory_mb: int = 1024) -> Dict[str, Any]:
        """Run comprehensive memory optimization"""
        logger.info("Starting comprehensive memory optimization...")
        
        # Set baseline
        self.set_baseline_memory()
        baseline_profile = self.get_current_memory_profile()
        
        # Calculate optimal configuration
        config = self.calculate_optimal_config(target_memory_mb)
        
        # Start monitoring
        self.start_memory_monitoring()
        
        # Implement optimizations
        logger.info("Implementing memory optimizations...")
        
        # Pre-allocation
        pre_allocation_success = self.implement_memory_pre_allocation(config)
        
        # GC optimization
        self.optimize_garbage_collection(config)
        
        # Cache optimization
        cache_config = self.implement_caching_optimization(config)
        
        # Monitor for a period
        time.sleep(30)  # Monitor for 30 seconds
        
        # Stop monitoring
        monitoring_stats = self.stop_memory_monitoring()
        
        # Get final profile
        final_profile = self.get_current_memory_profile()
        
        # Memory leak analysis
        leak_analysis = self.monitor_memory_leaks(30)
        
        # Compile results
        results = {
            "optimization_timestamp": time.time(),
            "target_memory_mb": target_memory_mb,
            "optimization_config": asdict(config),
            "baseline_profile": asdict(baseline_profile),
            "final_profile": asdict(final_profile),
            "memory_improvement": {
                "baseline_memory_mb": baseline_profile.process_memory_mb,
                "final_memory_mb": final_profile.process_memory_mb,
                "memory_change_mb": final_profile.process_memory_mb - baseline_profile.process_memory_mb,
                "target_achieved": final_profile.memory_growth_mb <= target_memory_mb
            },
            "pre_allocation_success": pre_allocation_success,
            "cache_configuration": cache_config,
            "monitoring_statistics": monitoring_stats,
            "leak_analysis": leak_analysis,
            "recommendations": self._generate_memory_recommendations(config, baseline_profile, final_profile, target_memory_mb)
        }
        
        # Save results
        results_file = self.results_dir / f"memory_optimization_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Memory optimization completed. Results saved to: {results_file}")
        return results
    
    def _generate_memory_recommendations(self, config: MemoryOptimizationConfig, 
                                       baseline: MemoryProfile, 
                                       final: MemoryProfile, 
                                       target_mb: int) -> List[str]:
        """Generate memory optimization recommendations"""
        recommendations = []
        
        memory_change = final.process_memory_mb - baseline.process_memory_mb
        
        # Target achievement
        if memory_change > target_mb:
            recommendations.append(f"Memory usage exceeded target by {memory_change - target_mb:.1f}MB")
            recommendations.append("Consider reducing cache sizes or implementing more aggressive optimization")
        else:
            recommendations.append(f"Memory target achieved with {target_mb - memory_change:.1f}MB headroom")
        
        # Memory growth analysis
        if final.memory_growth_mb > 100:
            recommendations.append("High memory growth detected - investigate potential memory leaks")
        
        # GC recommendations
        if final.gc_collections.get("generation_0", 0) > baseline.gc_collections.get("generation_0", 0) * 2:
            recommendations.append("High GC activity - consider optimizing object allocation patterns")
        
        # Cache recommendations
        if config.cache_size_limit_mb > 100:
            recommendations.append("Large cache size may impact memory usage - monitor cache hit rates")
        
        # System recommendations
        if final.process_memory_percent > 10:
            recommendations.append("Process using significant system memory - consider system memory upgrade")
        
        return recommendations

def main():
    """Main function to run memory optimization"""
    optimizer = MemoryOptimizer()
    
    try:
        results = optimizer.run_comprehensive_optimization(target_memory_mb=150)
        
        print("\n" + "="*80)
        print("MEMORY OPTIMIZATION SUMMARY")
        print("="*80)
        
        baseline = results["baseline_profile"]
        final = results["final_profile"]
        improvement = results["memory_improvement"]
        
        print(f"Target Memory: {results['target_memory_mb']} MB")
        print(f"Baseline Memory: {baseline['process_memory_mb']:.2f} MB")
        print(f"Final Memory: {final['process_memory_mb']:.2f} MB")
        print(f"Memory Change: {improvement['memory_change_mb']:.2f} MB")
        print(f"Target Achieved: {'✅' if improvement['target_achieved'] else '❌'}")
        
        print(f"\nOptimization Results:")
        print(f"  Pre-allocation Success: {'✅' if results['pre_allocation_success'] else '❌'}")
        print(f"  Peak Memory: {final['peak_memory_mb']:.2f} MB")
        print(f"  Memory Growth: {final['memory_growth_mb']:.2f} MB")
        
        monitoring = results["monitoring_statistics"]
        if "avg_memory_mb" in monitoring:
            print(f"  Average Memory: {monitoring['avg_memory_mb']:.2f} MB")
            print(f"  Memory Variance: {monitoring['memory_variance']:.2f}")
        
        leak_analysis = results["leak_analysis"]
        print(f"\nLeak Analysis:")
        print(f"  Memory Growth in Test: {leak_analysis['memory_growth_mb']:.2f} MB")
        print(f"  Potential Leaks: {len(leak_analysis['potential_leaks'])}")
        
        print(f"\nRecommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"Memory optimization failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
