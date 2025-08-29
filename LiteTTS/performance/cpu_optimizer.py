#!/usr/bin/env python3
"""
CPU optimization utilities for Kokoro TTS
Provides CPU affinity, thread management, and performance tuning
"""

import os
import logging
import platform
import threading
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CPUInfo:
    """CPU information and capabilities"""
    total_cores: int
    physical_cores: int
    logical_cores: int
    has_hyperthreading: bool
    architecture: str
    model_name: str
    supports_avx2: bool = False
    supports_avx512: bool = False
    has_hybrid_architecture: bool = False
    performance_cores: int = 0
    efficiency_cores: int = 0
    numa_nodes: int = 1
    base_frequency: float = 0.0
    max_frequency: float = 0.0

class CPUOptimizer:
    """CPU optimization and affinity management"""
    
    def __init__(self):
        self.cpu_info = self._detect_cpu_info()
        self.affinity_set = False
        self.original_affinity = None
        
    def _detect_cpu_info(self) -> CPUInfo:
        """Detect CPU information and capabilities"""
        try:
            import psutil

            # Get CPU count information
            logical_cores = psutil.cpu_count(logical=True)
            physical_cores = psutil.cpu_count(logical=False)

            # Detect hyperthreading
            has_hyperthreading = logical_cores > physical_cores

            # Initialize default values
            model_name = "Unknown"
            supports_avx2 = False
            supports_avx512 = False
            has_hybrid_architecture = False
            performance_cores = physical_cores
            efficiency_cores = 0
            numa_nodes = 1
            base_frequency = 0.0
            max_frequency = 0.0

            # Get CPU info
            if platform.system() == "Linux":
                try:
                    with open("/proc/cpuinfo", "r") as f:
                        cpuinfo = f.read()

                    # Extract model name
                    for line in cpuinfo.split("\n"):
                        if "model name" in line:
                            model_name = line.split(":")[1].strip()
                            break

                    # Check for AVX support
                    supports_avx2 = "avx2" in cpuinfo
                    supports_avx512 = "avx512" in cpuinfo

                    # Detect Intel hybrid architecture (12th gen and later)
                    if "13th Gen Intel" in model_name or "12th Gen Intel" in model_name:
                        has_hybrid_architecture = True
                        # Intel i5-13600K has 6 P-cores + 8 E-cores = 14 physical cores
                        # But shows as 20 logical cores (6P*2 + 8E*1)
                        if "i5-13600K" in model_name:
                            performance_cores = 6  # P-cores with hyperthreading
                            efficiency_cores = 8   # E-cores without hyperthreading
                        elif "i7-13700K" in model_name:
                            performance_cores = 8  # P-cores with hyperthreading
                            efficiency_cores = 8   # E-cores without hyperthreading
                        elif "i9-13900K" in model_name:
                            performance_cores = 8  # P-cores with hyperthreading
                            efficiency_cores = 16  # E-cores without hyperthreading

                    # Get frequency information
                    try:
                        cpu_freq = psutil.cpu_freq()
                        if cpu_freq:
                            base_frequency = cpu_freq.current
                            max_frequency = cpu_freq.max
                    except Exception:
                        pass

                    # Get NUMA information
                    try:
                        import os
                        numa_path = "/sys/devices/system/node"
                        if os.path.exists(numa_path):
                            numa_nodes = len([d for d in os.listdir(numa_path) if d.startswith("node")])
                    except Exception:
                        numa_nodes = 1

                except Exception:
                    pass
            else:
                model_name = platform.processor()

            return CPUInfo(
                total_cores=logical_cores,
                physical_cores=physical_cores,
                logical_cores=logical_cores,
                has_hyperthreading=has_hyperthreading,
                architecture=platform.machine(),
                model_name=model_name,
                supports_avx2=supports_avx2,
                supports_avx512=supports_avx512,
                has_hybrid_architecture=has_hybrid_architecture,
                performance_cores=performance_cores,
                efficiency_cores=efficiency_cores,
                numa_nodes=numa_nodes,
                base_frequency=base_frequency,
                max_frequency=max_frequency
            )
            
        except ImportError:
            # Fallback without psutil
            logical_cores = os.cpu_count() or 4
            return CPUInfo(
                total_cores=logical_cores,
                physical_cores=logical_cores,
                logical_cores=logical_cores,
                has_hyperthreading=False,
                architecture=platform.machine(),
                model_name=platform.processor(),
                supports_avx2=False,
                supports_avx512=False
            )
    
    def set_cpu_affinity(self, core_list: Optional[List[int]] = None) -> bool:
        """
        Set CPU affinity for the current process
        
        Args:
            core_list: List of CPU cores to bind to. If None, auto-select optimal cores
        
        Returns:
            True if affinity was set successfully
        """
        try:
            import psutil
            
            if core_list is None:
                core_list = self._get_optimal_cores()
            
            # Store original affinity for restoration
            if not self.affinity_set:
                self.original_affinity = psutil.Process().cpu_affinity()
            
            # Set new affinity
            psutil.Process().cpu_affinity(core_list)
            self.affinity_set = True
            
            logger.info(f"Set CPU affinity to cores: {core_list}")
            return True
            
        except ImportError:
            logger.warning("psutil not available, cannot set CPU affinity")
            return False
        except Exception as e:
            logger.error(f"Failed to set CPU affinity: {e}")
            return False
    
    def _get_optimal_cores(self, aggressive: bool = False) -> List[int]:
        """Get optimal CPU cores for TTS processing"""
        total_cores = self.cpu_info.total_cores

        if aggressive:
            # Aggressive mode: use 90-95% of cores for maximum performance
            if total_cores >= 16:
                # High-end CPU: use almost all cores (leave 1-2 for system)
                return list(range(0, total_cores - 1))
            elif total_cores >= 8:
                # Mid-range CPU: use 85-90% of cores
                return list(range(0, max(6, int(total_cores * 0.9))))
            else:
                # Low-end CPU: use all but one core
                return list(range(0, max(1, total_cores - 1)))
        else:
            # Conservative mode (original behavior)
            if total_cores >= 16:
                # High-end CPU: use 75% of cores, prefer physical cores
                if self.cpu_info.has_hyperthreading:
                    # Use physical cores first, then some logical cores
                    physical_cores = list(range(0, self.cpu_info.physical_cores, 2))
                    logical_cores = list(range(1, min(total_cores, 12), 2))
                    return physical_cores + logical_cores[:4]
                else:
                    return list(range(0, min(12, total_cores)))

            elif total_cores >= 8:
                # Mid-range CPU: use 50-75% of cores
                return list(range(0, min(6, total_cores)))

            else:
                # Low-end CPU: use most cores but leave one for system
                return list(range(0, max(1, total_cores - 1)))
    
    def restore_cpu_affinity(self) -> bool:
        """Restore original CPU affinity"""
        try:
            import psutil
            
            if self.affinity_set and self.original_affinity:
                psutil.Process().cpu_affinity(self.original_affinity)
                self.affinity_set = False
                logger.info("Restored original CPU affinity")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to restore CPU affinity: {e}")
            return False
    
    def optimize_environment_variables(self, aggressive: bool = False) -> Dict[str, str]:
        """Get optimized environment variables for current CPU"""
        env_vars = {}

        total_cores = self.cpu_info.total_cores

        if aggressive:
            # Aggressive mode: use 90-95% of threads
            if total_cores >= 16:
                omp_threads = min(18, total_cores - 2)  # Leave 2 cores for system
            elif total_cores >= 8:
                omp_threads = min(12, int(total_cores * 0.9))
            else:
                omp_threads = min(6, total_cores - 1)
        else:
            # Conservative mode (original behavior)
            if total_cores >= 16:
                omp_threads = min(12, total_cores // 2)
            elif total_cores >= 8:
                omp_threads = min(8, total_cores)
            else:
                omp_threads = min(4, total_cores)

        env_vars.update({
            "OMP_NUM_THREADS": str(omp_threads),
            "OPENBLAS_NUM_THREADS": str(omp_threads),
            "MKL_NUM_THREADS": str(omp_threads),
            "NUMEXPR_NUM_THREADS": str(min(6, total_cores // 3)),
            "ONNX_DISABLE_SPARSE_TENSORS": "1"
        })

        # Aggressive optimizations
        if aggressive:
            env_vars.update({
                "OMP_SCHEDULE": "dynamic",
                "OMP_PROC_BIND": "spread",
                "OMP_PLACES": "cores",
                "GOMP_CPU_AFFINITY": f"0-{total_cores-1}",
                "KMP_AFFINITY": "granularity=fine,compact,1,0",
                "KMP_BLOCKTIME": "0",
                "KMP_SETTINGS": "1" if aggressive else "0"
            })

        # CPU-specific optimizations
        if self.cpu_info.supports_avx512:
            env_vars["ONNX_ENABLE_AVX512"] = "1"
        elif self.cpu_info.supports_avx2:
            env_vars["ONNX_ENABLE_AVX2"] = "1"
            if aggressive:
                env_vars["ONNX_OPTIMIZE_FOR_AVX2"] = "1"

        # Intel-specific optimizations
        if "Intel" in self.cpu_info.model_name:
            env_vars["INTEL_NUM_THREADS"] = str(omp_threads)
            if aggressive:
                env_vars["MKL_DYNAMIC"] = "FALSE"
                env_vars["MKL_NUM_THREADS"] = str(omp_threads)

        return env_vars
    
    def get_cpu_info(self) -> CPUInfo:
        """Get CPU information - compatibility method for integrated optimizer"""
        return self.cpu_info

    def get_aggressive_performance_config(self) -> Dict[str, Any]:
        """Get aggressive performance configuration - compatibility method for integrated optimizer"""
        return self.get_recommended_settings(aggressive=True)

    def apply_optimizations(self, enable_affinity: bool = False) -> bool:
        """Apply all CPU optimizations"""
        success = True

        # Set environment variables
        env_vars = self.optimize_environment_variables()
        for key, value in env_vars.items():
            os.environ.setdefault(key, value)

        logger.info(f"Applied CPU environment optimizations: {env_vars}")

        # Set CPU affinity if requested
        if enable_affinity:
            success &= self.set_cpu_affinity()

        return success
    
    def get_recommended_settings(self, aggressive: bool = False) -> Dict[str, Any]:
        """Get recommended settings for current CPU"""
        total_cores = self.cpu_info.total_cores

        if aggressive:
            # Aggressive mode: maximize CPU utilization (90-95%)
            if total_cores >= 16:
                if self.cpu_info.has_hybrid_architecture:
                    # Intel hybrid architecture optimization
                    p_cores = self.cpu_info.performance_cores
                    e_cores = self.cpu_info.efficiency_cores

                    return {
                        "workers": min(6, total_cores // 3),  # More workers for parallel processing
                        "onnx_inter_op_threads": min(8, p_cores + e_cores // 2),  # Use P-cores + some E-cores
                        "onnx_intra_op_threads": min(18, total_cores - 2),  # Use almost all threads
                        "batch_size": 6,  # Larger batches
                        "concurrent_requests": 12,  # More concurrent requests
                        "phonemizer_threads": min(4, e_cores // 2),  # Use E-cores for I/O
                        "audio_processing_threads": min(6, p_cores),  # Use P-cores for compute
                        "pipeline_parallelism": True,
                        "warm_up_enabled": True,
                        "short_text_optimization": True
                    }
                else:
                    return {
                        "workers": min(6, total_cores // 3),
                        "onnx_inter_op_threads": min(8, total_cores // 2),
                        "onnx_intra_op_threads": min(18, total_cores - 2),
                        "batch_size": 6,
                        "concurrent_requests": 12,
                        "pipeline_parallelism": True,
                        "warm_up_enabled": True
                    }
            elif total_cores >= 8:
                return {
                    "workers": 3,
                    "onnx_inter_op_threads": min(6, total_cores // 2),
                    "onnx_intra_op_threads": min(12, int(total_cores * 0.9)),
                    "batch_size": 4,
                    "concurrent_requests": 8,
                    "pipeline_parallelism": True
                }
            else:
                return {
                    "workers": 2,
                    "onnx_inter_op_threads": min(3, total_cores // 2),
                    "onnx_intra_op_threads": min(6, total_cores - 1),
                    "batch_size": 2,
                    "concurrent_requests": 4
                }
        else:
            # Conservative mode (original behavior)
            if total_cores >= 16:
                return {
                    "workers": min(4, total_cores // 4),
                    "onnx_inter_op_threads": min(6, total_cores // 3),
                    "onnx_intra_op_threads": min(12, total_cores // 2),
                    "batch_size": 4,
                    "concurrent_requests": 8
                }
            elif total_cores >= 8:
                return {
                    "workers": 2,
                    "onnx_inter_op_threads": min(4, total_cores // 2),
                    "onnx_intra_op_threads": min(8, total_cores),
                    "batch_size": 2,
                    "concurrent_requests": 4
                }
            else:
                return {
                    "workers": 1,
                    "onnx_inter_op_threads": min(2, total_cores // 2),
                    "onnx_intra_op_threads": min(4, total_cores),
                    "batch_size": 1,
                    "concurrent_requests": 2
                }

    def get_thermal_status(self) -> Dict[str, Any]:
        """Get CPU thermal status and temperature information"""
        thermal_info = {
            "temperature": 0.0,
            "throttling": False,
            "safe_for_aggressive": True,
            "recommended_threads": self.cpu_info.total_cores
        }

        try:
            import psutil

            # Get CPU temperature if available
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Look for CPU temperature
                    cpu_temps = []
                    for name, entries in temps.items():
                        if "cpu" in name.lower() or "core" in name.lower():
                            for entry in entries:
                                if entry.current:
                                    cpu_temps.append(entry.current)

                    if cpu_temps:
                        avg_temp = sum(cpu_temps) / len(cpu_temps)
                        thermal_info["temperature"] = avg_temp

                        # Check for thermal throttling (>85°C is concerning)
                        if avg_temp > 85:
                            thermal_info["throttling"] = True
                            thermal_info["safe_for_aggressive"] = False
                            # Reduce thread count if overheating
                            thermal_info["recommended_threads"] = max(4, self.cpu_info.total_cores // 2)
                        elif avg_temp > 75:
                            thermal_info["safe_for_aggressive"] = False
                            thermal_info["recommended_threads"] = max(8, int(self.cpu_info.total_cores * 0.8))

        except Exception as e:
            logger.debug(f"Could not get thermal information: {e}")

        return thermal_info

    def set_hybrid_cpu_affinity(self, enable_aggressive: bool = False) -> bool:
        """Set CPU affinity optimized for Intel hybrid architecture"""
        if not self.cpu_info.has_hybrid_architecture:
            return self.set_cpu_affinity()

        try:
            import psutil

            # Intel hybrid architecture: P-cores first, then E-cores
            p_cores = self.cpu_info.performance_cores
            e_cores = self.cpu_info.efficiency_cores

            if enable_aggressive:
                # Use all P-cores and most E-cores
                p_core_threads = list(range(0, p_cores * 2))  # P-cores with hyperthreading
                e_core_threads = list(range(p_cores * 2, p_cores * 2 + e_cores - 1))  # Most E-cores
                core_list = p_core_threads + e_core_threads
            else:
                # Use P-cores and some E-cores
                p_core_threads = list(range(0, p_cores * 2))  # All P-core threads
                e_core_threads = list(range(p_cores * 2, p_cores * 2 + e_cores // 2))  # Half E-cores
                core_list = p_core_threads + e_core_threads

            # Store original affinity for restoration
            if not self.affinity_set:
                self.original_affinity = psutil.Process().cpu_affinity()

            # Set new affinity
            psutil.Process().cpu_affinity(core_list)
            self.affinity_set = True

            logger.info(f"Set hybrid CPU affinity: P-cores={p_cores}, E-cores={e_cores}, using cores={core_list}")
            return True

        except Exception as e:
            logger.error(f"Failed to set hybrid CPU affinity: {e}")
            return False

# Global CPU optimizer instance
_cpu_optimizer = None

def get_cpu_optimizer() -> CPUOptimizer:
    """Get global CPU optimizer instance"""
    global _cpu_optimizer
    if _cpu_optimizer is None:
        _cpu_optimizer = CPUOptimizer()
    return _cpu_optimizer
