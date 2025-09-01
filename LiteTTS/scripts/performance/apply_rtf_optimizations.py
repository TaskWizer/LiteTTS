#!/usr/bin/env python3
"""
Apply RTF Performance Optimizations
Implements CPU optimization techniques to achieve RTF < 0.25 target
"""

import os
import sys
import json
import logging
import psutil
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)

def get_system_info() -> Dict[str, Any]:
    """Get system information for optimization"""
    cpu_count = psutil.cpu_count(logical=True)
    cpu_count_physical = psutil.cpu_count(logical=False)
    memory = psutil.virtual_memory()
    
    return {
        "cpu_count_logical": cpu_count,
        "cpu_count_physical": cpu_count_physical,
        "memory_total_gb": memory.total / (1024**3),
        "memory_available_gb": memory.available / (1024**3)
    }

def apply_environment_optimizations():
    """Apply environment variable optimizations for ONNX Runtime"""
    system_info = get_system_info()
    cpu_count = system_info["cpu_count_logical"]
    
    # Calculate optimal thread counts
    onnx_inter_op_threads = min(8, cpu_count // 2)
    onnx_intra_op_threads = min(16, cpu_count - 2)
    omp_threads = min(12, cpu_count - 1)
    
    env_vars = {
        # ONNX Runtime optimizations
        "ORT_ENABLE_CPU_FP16_OPS": "1",
        "ORT_DISABLE_SPARSE_TENSORS": "1",
        "ORT_ENABLE_EXTENDED_NORMALIZATION_OPS": "1",
        
        # Threading optimizations
        "OMP_NUM_THREADS": str(omp_threads),
        "OPENBLAS_NUM_THREADS": str(omp_threads),
        "MKL_NUM_THREADS": str(omp_threads),
        "NUMEXPR_NUM_THREADS": str(min(6, cpu_count // 3)),
        
        # Aggressive CPU optimizations
        "OMP_SCHEDULE": "dynamic",
        "OMP_PROC_BIND": "spread",
        "OMP_PLACES": "cores",
        "KMP_AFFINITY": "granularity=fine,compact,1,0",
        "KMP_BLOCKTIME": "0",
        "KMP_SETTINGS": "1",
        
        # Memory optimizations
        "MALLOC_TRIM_THRESHOLD_": "100000",
        "MALLOC_MMAP_THRESHOLD_": "131072",
    }
    
    # Apply environment variables
    for key, value in env_vars.items():
        os.environ[key] = value
        logger.info(f"Set {key}={value}")
    
    return env_vars

def update_config_for_performance():
    """Update config.json with performance optimizations"""
    config_path = Path("config.json")
    
    if not config_path.exists():
        logger.error("config.json not found")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    system_info = get_system_info()
    cpu_count = system_info["cpu_count_logical"]
    
    # Update performance settings
    performance_updates = {
        "concurrent_requests": min(12, cpu_count),
        "memory_optimization": True,
        "dynamic_cpu_allocation": {
            "enabled": True,
            "cpu_target": 95.0,
            "aggressive_mode": True,
            "thermal_protection": True,
            "onnx_integration": True,
            "update_environment": True
        }
    }
    
    # Update model settings for performance
    model_updates = {
        "default_variant": "model_q4.onnx",  # Use quantized model
        "performance_mode": "speed",
        "cache_models": True,
        "preload_models": True
    }
    
    # Apply updates
    config["performance"].update(performance_updates)
    config["model"].update(model_updates)
    
    # Write updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info("Updated config.json with performance optimizations")
    return True

def create_performance_startup_script():
    """Create a startup script to apply optimizations"""
    script_content = '''#!/bin/bash
# Performance optimization startup script

echo "Applying CPU performance optimizations..."

# Set CPU governor to performance mode (if available)
if [ -d "/sys/devices/system/cpu/cpu0/cpufreq" ]; then
    echo "Setting CPU governor to performance mode..."
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        if [ -w "$cpu" ]; then
            echo performance > "$cpu" 2>/dev/null || true
        fi
    done
fi

# Disable CPU frequency scaling (if available)
if command -v cpupower >/dev/null 2>&1; then
    echo "Configuring CPU power settings..."
    cpupower frequency-set -g performance 2>/dev/null || true
fi

# Set process priority
echo "Setting process priority..."
renice -n -10 $$ 2>/dev/null || true

# Apply memory optimizations
echo "Applying memory optimizations..."
echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || true

echo "Performance optimizations applied!"
'''
    
    script_path = Path("scripts/performance/optimize_system.sh")
    script_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    script_path.chmod(0o755)
    logger.info(f"Created performance startup script: {script_path}")

def main():
    """Apply all RTF performance optimizations"""
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Applying RTF Performance Optimizations")
    print("=" * 50)
    
    # Get system information
    system_info = get_system_info()
    print(f"System Info:")
    print(f"  CPU Cores (logical): {system_info['cpu_count_logical']}")
    print(f"  CPU Cores (physical): {system_info['cpu_count_physical']}")
    print(f"  Memory Total: {system_info['memory_total_gb']:.1f} GB")
    print(f"  Memory Available: {system_info['memory_available_gb']:.1f} GB")
    print()
    
    # Apply optimizations
    print("1. Applying environment variable optimizations...")
    env_vars = apply_environment_optimizations()
    print(f"   Applied {len(env_vars)} environment variables")
    
    print("2. Updating configuration for performance...")
    if update_config_for_performance():
        print("   ✅ Configuration updated successfully")
    else:
        print("   ❌ Failed to update configuration")
    
    print("3. Creating performance startup script...")
    create_performance_startup_script()
    print("   ✅ Startup script created")
    
    print()
    print("🎯 Performance Optimization Summary:")
    print("   - Enabled aggressive CPU allocation")
    print("   - Increased concurrent requests")
    print("   - Applied ONNX Runtime optimizations")
    print("   - Configured threading for optimal performance")
    print("   - Created system optimization script")
    print()
    print("📋 Next Steps:")
    print("   1. Restart the LiteTTS service to apply changes")
    print("   2. Run performance benchmarks to verify RTF < 0.25")
    print("   3. Monitor system resources during operation")
    print("   4. Use the dashboard to track real-time performance")

if __name__ == "__main__":
    main()
