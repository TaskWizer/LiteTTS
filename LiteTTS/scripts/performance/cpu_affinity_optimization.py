#!/usr/bin/env python3
"""
CPU Affinity and Multi-core Optimization System
Configure CPU affinity pinning across P-cores and E-cores, optimize ONNX Runtime for multi-core inference
"""

import os
import sys
import json
import logging
import psutil
import time
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import platform

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CPUTopology:
    """CPU topology information"""
    total_cores: int
    physical_cores: int
    logical_cores: int
    p_cores: List[int]
    e_cores: List[int]
    numa_nodes: List[int]
    cache_levels: Dict[str, Any]
    frequency_info: Dict[str, float]
    architecture: str

@dataclass
class AffinityConfiguration:
    """CPU affinity configuration"""
    onnx_cores: List[int]
    system_cores: List[int]
    io_cores: List[int]
    monitoring_cores: List[int]
    thread_pool_size: int
    inter_op_threads: int
    intra_op_threads: int
    optimization_level: str

class CPUAffinityOptimizer:
    """CPU affinity and multi-core optimization system"""
    
    def __init__(self):
        self.results_dir = Path("test_results/cpu_optimization")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # CPU topology detection
        self.topology = self._detect_cpu_topology()
        
        # Current process
        self.current_process = psutil.Process()
        
    def _detect_cpu_topology(self) -> CPUTopology:
        """Detect CPU topology and core types"""
        logger.info("Detecting CPU topology...")
        
        # Basic CPU information
        total_cores = psutil.cpu_count(logical=True)
        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = total_cores
        
        # Try to detect P-cores and E-cores (Intel 12th gen+)
        p_cores = []
        e_cores = []
        
        try:
            # On Linux, try to read CPU frequency info to distinguish core types
            if platform.system() == "Linux":
                p_cores, e_cores = self._detect_core_types_linux()
            else:
                # Fallback: assume first half are P-cores, second half are E-cores
                # This is a heuristic and may not be accurate
                mid_point = physical_cores // 2
                p_cores = list(range(0, mid_point))
                e_cores = list(range(mid_point, physical_cores))
        except Exception as e:
            logger.warning(f"Could not detect core types: {e}")
            # Fallback: treat all cores as P-cores
            p_cores = list(range(physical_cores))
            e_cores = []
        
        # NUMA nodes detection
        numa_nodes = []
        try:
            if hasattr(psutil, 'cpu_affinity'):
                # Try to detect NUMA topology
                numa_nodes = [0]  # Default single NUMA node
        except:
            numa_nodes = [0]
        
        # Cache information
        cache_levels = self._detect_cache_info()
        
        # Frequency information
        frequency_info = self._get_frequency_info()
        
        # Architecture detection
        architecture = platform.machine()
        
        topology = CPUTopology(
            total_cores=total_cores,
            physical_cores=physical_cores,
            logical_cores=logical_cores,
            p_cores=p_cores,
            e_cores=e_cores,
            numa_nodes=numa_nodes,
            cache_levels=cache_levels,
            frequency_info=frequency_info,
            architecture=architecture
        )
        
        logger.info(f"Detected topology: {total_cores} total cores, {len(p_cores)} P-cores, {len(e_cores)} E-cores")
        return topology
    
    def _detect_core_types_linux(self) -> Tuple[List[int], List[int]]:
        """Detect P-cores and E-cores on Linux systems"""
        p_cores = []
        e_cores = []
        
        try:
            # Read CPU frequency information
            cpu_freqs = psutil.cpu_freq(percpu=True)
            if cpu_freqs:
                # Sort cores by maximum frequency
                core_freqs = [(i, freq.max) for i, freq in enumerate(cpu_freqs) if freq.max]
                core_freqs.sort(key=lambda x: x[1], reverse=True)
                
                # Assume cores with higher max frequency are P-cores
                # This is a heuristic and may need adjustment
                total_physical = self.topology.physical_cores if hasattr(self, 'topology') else psutil.cpu_count(logical=False)
                p_core_count = max(1, total_physical // 2)
                
                p_cores = [core[0] for core in core_freqs[:p_core_count]]
                e_cores = [core[0] for core in core_freqs[p_core_count:]]
            else:
                # Fallback
                total_cores = psutil.cpu_count(logical=False)
                mid_point = total_cores // 2
                p_cores = list(range(0, mid_point))
                e_cores = list(range(mid_point, total_cores))
                
        except Exception as e:
            logger.warning(f"Error detecting core types on Linux: {e}")
            # Final fallback
            total_cores = psutil.cpu_count(logical=False)
            p_cores = list(range(total_cores))
            e_cores = []
        
        return p_cores, e_cores
    
    def _detect_cache_info(self) -> Dict[str, Any]:
        """Detect CPU cache information"""
        cache_info = {
            "l1_data": "unknown",
            "l1_instruction": "unknown",
            "l2": "unknown",
            "l3": "unknown"
        }
        
        try:
            if platform.system() == "Linux":
                # Try to read cache info from /proc/cpuinfo
                with open("/proc/cpuinfo", "r") as f:
                    content = f.read()
                    if "cache size" in content:
                        # Extract cache size information
                        for line in content.split('\n'):
                            if "cache size" in line:
                                cache_info["l2"] = line.split(':')[1].strip()
                                break
        except Exception as e:
            logger.warning(f"Could not detect cache info: {e}")
        
        return cache_info
    
    def _get_frequency_info(self) -> Dict[str, float]:
        """Get CPU frequency information"""
        freq_info = {
            "current": 0.0,
            "min": 0.0,
            "max": 0.0
        }
        
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                freq_info["current"] = cpu_freq.current
                freq_info["min"] = cpu_freq.min
                freq_info["max"] = cpu_freq.max
        except Exception as e:
            logger.warning(f"Could not get frequency info: {e}")
        
        return freq_info
    
    def calculate_optimal_affinity(self, workload_type: str = "inference") -> AffinityConfiguration:
        """Calculate optimal CPU affinity configuration"""
        logger.info(f"Calculating optimal affinity for {workload_type} workload...")
        
        total_cores = self.topology.total_cores
        p_cores = self.topology.p_cores
        e_cores = self.topology.e_cores
        
        if workload_type == "inference":
            # For TTS inference, prioritize P-cores for ONNX Runtime
            # Reserve some cores for system tasks
            
            if len(p_cores) >= 4:
                # Use most P-cores for ONNX, reserve 1-2 for system
                onnx_cores = p_cores[:-1]  # All but last P-core
                system_cores = [p_cores[-1]]  # Last P-core for system
                io_cores = e_cores[:2] if len(e_cores) >= 2 else e_cores  # First 2 E-cores for I/O
                monitoring_cores = e_cores[2:3] if len(e_cores) > 2 else []  # One E-core for monitoring
            elif len(p_cores) >= 2:
                # Limited P-cores, use half for ONNX
                mid_point = len(p_cores) // 2
                onnx_cores = p_cores[:mid_point]
                system_cores = p_cores[mid_point:]
                io_cores = e_cores[:1] if e_cores else []
                monitoring_cores = e_cores[1:2] if len(e_cores) > 1 else []
            else:
                # Very limited cores, use all available
                onnx_cores = p_cores if p_cores else list(range(min(4, total_cores)))
                system_cores = e_cores[:1] if e_cores else [total_cores - 1]
                io_cores = []
                monitoring_cores = []
            
            # Thread pool configuration
            thread_pool_size = len(onnx_cores)
            inter_op_threads = max(1, len(onnx_cores) // 2)
            intra_op_threads = len(onnx_cores)
            
        else:
            # Default configuration
            onnx_cores = list(range(min(4, total_cores)))
            system_cores = list(range(min(4, total_cores), total_cores))
            io_cores = []
            monitoring_cores = []
            thread_pool_size = min(4, total_cores)
            inter_op_threads = 2
            intra_op_threads = min(4, total_cores)
        
        config = AffinityConfiguration(
            onnx_cores=onnx_cores,
            system_cores=system_cores,
            io_cores=io_cores,
            monitoring_cores=monitoring_cores,
            thread_pool_size=thread_pool_size,
            inter_op_threads=inter_op_threads,
            intra_op_threads=intra_op_threads,
            optimization_level="aggressive"
        )
        
        logger.info(f"Optimal configuration: ONNX cores: {onnx_cores}, System cores: {system_cores}")
        return config
    
    def apply_cpu_affinity(self, config: AffinityConfiguration) -> bool:
        """Apply CPU affinity configuration"""
        logger.info("Applying CPU affinity configuration...")
        
        try:
            # Set process affinity to ONNX cores
            if hasattr(self.current_process, 'cpu_affinity'):
                all_assigned_cores = config.onnx_cores + config.system_cores + config.io_cores
                if all_assigned_cores:
                    self.current_process.cpu_affinity(all_assigned_cores)
                    logger.info(f"Set process affinity to cores: {all_assigned_cores}")
                else:
                    logger.warning("No cores assigned, skipping affinity setting")
            else:
                logger.warning("CPU affinity not supported on this platform")
            
            # Set environment variables for ONNX Runtime
            os.environ['OMP_NUM_THREADS'] = str(config.intra_op_threads)
            os.environ['MKL_NUM_THREADS'] = str(config.intra_op_threads)
            os.environ['OPENBLAS_NUM_THREADS'] = str(config.intra_op_threads)
            os.environ['VECLIB_MAXIMUM_THREADS'] = str(config.intra_op_threads)
            os.environ['NUMEXPR_NUM_THREADS'] = str(config.intra_op_threads)
            
            # ONNX Runtime specific settings
            os.environ['ORT_NUM_THREADS'] = str(config.intra_op_threads)
            
            logger.info(f"Set threading environment variables: OMP_NUM_THREADS={config.intra_op_threads}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply CPU affinity: {e}")
            return False
    
    def optimize_onnx_runtime_config(self, config: AffinityConfiguration) -> Dict[str, Any]:
        """Generate optimized ONNX Runtime configuration"""
        logger.info("Generating optimized ONNX Runtime configuration...")
        
        onnx_config = {
            "providers": ["CPUExecutionProvider"],
            "provider_options": [{
                "use_arena": True,
                "arena_extend_strategy": "kSameAsRequested",
                "enable_cpu_mem_arena": True,
                "enable_memory_pattern": True,
                "enable_mem_reuse": True
            }],
            "session_options": {
                "enable_cpu_mem_arena": True,
                "enable_mem_pattern": True,
                "enable_mem_reuse": True,
                "execution_mode": "ORT_SEQUENTIAL",  # or ORT_PARALLEL for some models
                "graph_optimization_level": "ORT_ENABLE_ALL",
                "inter_op_num_threads": config.inter_op_threads,
                "intra_op_num_threads": config.intra_op_threads,
                "use_deterministic_compute": False,  # Allow non-deterministic for performance
                "enable_profiling": False  # Disable for production
            },
            "threading": {
                "thread_pool_size": config.thread_pool_size,
                "spin_control": True,
                "allow_spinning": True,
                "thread_affinity": config.onnx_cores
            }
        }
        
        return onnx_config
    
    def benchmark_affinity_performance(self, config: AffinityConfiguration) -> Dict[str, Any]:
        """Benchmark performance with affinity configuration"""
        logger.info("Benchmarking affinity performance...")
        
        # Apply configuration
        self.apply_cpu_affinity(config)
        
        # Run performance tests
        test_results = {
            "cpu_utilization": [],
            "memory_usage": [],
            "context_switches": [],
            "cache_misses": []
        }
        
        # Monitor for 30 seconds
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                # CPU utilization per core
                cpu_percent = psutil.cpu_percent(percpu=True, interval=1)
                test_results["cpu_utilization"].append(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                test_results["memory_usage"].append(memory.percent)
                
                # Context switches
                ctx_switches = psutil.cpu_stats().ctx_switches
                test_results["context_switches"].append(ctx_switches)
                
            except Exception as e:
                logger.warning(f"Monitoring error: {e}")
                break
        
        # Calculate statistics
        if test_results["cpu_utilization"]:
            avg_cpu = [sum(cores) / len(test_results["cpu_utilization"]) 
                      for cores in zip(*test_results["cpu_utilization"])]
            
            performance_stats = {
                "avg_cpu_per_core": avg_cpu,
                "avg_memory_usage": sum(test_results["memory_usage"]) / len(test_results["memory_usage"]),
                "total_context_switches": test_results["context_switches"][-1] - test_results["context_switches"][0] if len(test_results["context_switches"]) > 1 else 0,
                "onnx_core_utilization": [avg_cpu[i] for i in config.onnx_cores if i < len(avg_cpu)],
                "system_core_utilization": [avg_cpu[i] for i in config.system_cores if i < len(avg_cpu)]
            }
        else:
            performance_stats = {
                "error": "No performance data collected"
            }
        
        return performance_stats
    
    def generate_configuration_file(self, config: AffinityConfiguration) -> str:
        """Generate configuration file for CPU optimization"""
        logger.info("Generating CPU optimization configuration file...")
        
        config_data = {
            "cpu_optimization": {
                "enabled": True,
                "affinity_configuration": asdict(config),
                "topology_info": asdict(self.topology),
                "onnx_runtime_config": self.optimize_onnx_runtime_config(config),
                "environment_variables": {
                    "OMP_NUM_THREADS": config.intra_op_threads,
                    "MKL_NUM_THREADS": config.intra_op_threads,
                    "OPENBLAS_NUM_THREADS": config.intra_op_threads,
                    "ORT_NUM_THREADS": config.intra_op_threads
                },
                "performance_tuning": {
                    "cpu_governor": "performance",
                    "scaling_driver": "intel_pstate",
                    "turbo_boost": True,
                    "hyperthreading": True
                }
            }
        }
        
        config_file = self.results_dir / "cpu_optimization_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logger.info(f"Configuration saved to: {config_file}")
        return str(config_file)
    
    def run_comprehensive_optimization(self) -> Dict[str, Any]:
        """Run comprehensive CPU affinity and multi-core optimization"""
        logger.info("Starting comprehensive CPU optimization...")
        
        # Calculate optimal configuration
        config = self.calculate_optimal_affinity("inference")
        
        # Benchmark current performance (before optimization)
        logger.info("Benchmarking baseline performance...")
        baseline_performance = self.benchmark_affinity_performance(config)
        
        # Apply optimizations
        logger.info("Applying CPU optimizations...")
        affinity_applied = self.apply_cpu_affinity(config)
        
        # Generate ONNX Runtime configuration
        onnx_config = self.optimize_onnx_runtime_config(config)
        
        # Benchmark optimized performance
        logger.info("Benchmarking optimized performance...")
        optimized_performance = self.benchmark_affinity_performance(config)
        
        # Generate configuration file
        config_file = self.generate_configuration_file(config)
        
        # Compile results
        results = {
            "optimization_timestamp": time.time(),
            "cpu_topology": asdict(self.topology),
            "affinity_configuration": asdict(config),
            "affinity_applied": affinity_applied,
            "onnx_runtime_config": onnx_config,
            "baseline_performance": baseline_performance,
            "optimized_performance": optimized_performance,
            "configuration_file": config_file,
            "recommendations": self._generate_optimization_recommendations(config, baseline_performance, optimized_performance)
        }
        
        # Save results
        results_file = self.results_dir / f"cpu_optimization_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"CPU optimization completed. Results saved to: {results_file}")
        return results
    
    def _generate_optimization_recommendations(self, config: AffinityConfiguration, 
                                             baseline: Dict[str, Any], 
                                             optimized: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Core allocation recommendations
        if len(config.onnx_cores) < 4:
            recommendations.append("Consider upgrading to a CPU with more cores for better TTS performance")
        
        # Thread configuration recommendations
        if config.intra_op_threads < 4:
            recommendations.append("Limited thread count may impact performance on complex models")
        
        # Performance comparison recommendations
        if "onnx_core_utilization" in optimized and optimized["onnx_core_utilization"]:
            avg_onnx_util = sum(optimized["onnx_core_utilization"]) / len(optimized["onnx_core_utilization"])
            if avg_onnx_util < 50:
                recommendations.append("ONNX cores are underutilized, consider increasing workload or reducing core count")
            elif avg_onnx_util > 90:
                recommendations.append("ONNX cores are highly utilized, consider adding more cores or optimizing workload")
        
        # System recommendations
        recommendations.append("Enable CPU performance governor for optimal TTS performance")
        recommendations.append("Ensure adequate cooling for sustained high CPU utilization")
        recommendations.append("Monitor thermal throttling during production workloads")
        
        return recommendations

def main():
    """Main function to run CPU affinity optimization"""
    optimizer = CPUAffinityOptimizer()
    
    try:
        results = optimizer.run_comprehensive_optimization()
        
        print("\n" + "="*80)
        print("CPU AFFINITY AND MULTI-CORE OPTIMIZATION SUMMARY")
        print("="*80)
        
        topology = results["cpu_topology"]
        config = results["affinity_configuration"]
        
        print(f"CPU Topology:")
        print(f"  Total Cores: {topology['total_cores']}")
        print(f"  Physical Cores: {topology['physical_cores']}")
        print(f"  P-Cores: {len(topology['p_cores'])} {topology['p_cores']}")
        print(f"  E-Cores: {len(topology['e_cores'])} {topology['e_cores']}")
        print(f"  Architecture: {topology['architecture']}")
        
        print(f"\nOptimal Configuration:")
        print(f"  ONNX Cores: {config['onnx_cores']}")
        print(f"  System Cores: {config['system_cores']}")
        print(f"  Thread Pool Size: {config['thread_pool_size']}")
        print(f"  Inter-op Threads: {config['inter_op_threads']}")
        print(f"  Intra-op Threads: {config['intra_op_threads']}")
        
        print(f"\nAffinity Applied: {'✅' if results['affinity_applied'] else '❌'}")
        
        print(f"\nRecommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        print(f"\nConfiguration File: {results['configuration_file']}")
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"CPU optimization failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
