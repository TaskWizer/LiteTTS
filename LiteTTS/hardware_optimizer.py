#!/usr/bin/env python3
"""
Hardware Optimization System for Kokoro ONNX TTS API

Automatically detects hardware capabilities and optimizes configuration settings
for the best performance on the user's system.
"""

import os
import json
import time
import psutil
import platform
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HardwareProfile:
    """Hardware profile information"""
    cpu_cores: int
    cpu_threads: int
    cpu_frequency: float
    total_memory_gb: float
    available_memory_gb: float
    has_gpu: bool
    gpu_memory_gb: Optional[float]
    platform_system: str
    architecture: str

@dataclass
class OptimizedSettings:
    """Optimized configuration settings"""
    workers: int
    chunk_size: int
    cache_enabled: bool
    cache_size: int
    preload_models: bool
    max_text_length: int
    timeout_seconds: int
    device: str

class HardwareOptimizer:
    """Automatic hardware optimization system"""
    
    def __init__(self):
        self.hardware_profile: Optional[HardwareProfile] = None
        self.optimized_settings: Optional[OptimizedSettings] = None
        self.benchmark_results: Dict[str, float] = {}
        
    def detect_hardware(self) -> HardwareProfile:
        """Detect hardware capabilities"""
        logger.info("🔍 Detecting hardware capabilities...")
        
        # CPU information
        cpu_cores = psutil.cpu_count(logical=False)
        cpu_threads = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_frequency = cpu_freq.current if cpu_freq else 0.0
        
        # Memory information
        memory = psutil.virtual_memory()
        total_memory_gb = memory.total / (1024**3)
        available_memory_gb = memory.available / (1024**3)
        
        # GPU detection
        has_gpu = False
        gpu_memory_gb = None
        
        try:
            import torch
            if torch.cuda.is_available():
                has_gpu = True
                gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                logger.info(f"✅ CUDA GPU detected: {torch.cuda.get_device_name(0)} ({gpu_memory_gb:.1f}GB)")
        except ImportError:
            logger.info("ℹ️  PyTorch not available, GPU detection skipped")
        except Exception as e:
            logger.warning(f"⚠️  GPU detection failed: {e}")
        
        # Platform information
        platform_system = platform.system()
        architecture = platform.machine()
        
        profile = HardwareProfile(
            cpu_cores=cpu_cores,
            cpu_threads=cpu_threads,
            cpu_frequency=cpu_frequency,
            total_memory_gb=total_memory_gb,
            available_memory_gb=available_memory_gb,
            has_gpu=has_gpu,
            gpu_memory_gb=gpu_memory_gb,
            platform_system=platform_system,
            architecture=architecture
        )
        
        logger.info(f"📊 Hardware Profile:")
        logger.info(f"   CPU: {cpu_cores} cores, {cpu_threads} threads @ {cpu_frequency:.0f}MHz")
        logger.info(f"   Memory: {total_memory_gb:.1f}GB total, {available_memory_gb:.1f}GB available")
        logger.info(f"   GPU: {'Yes' if has_gpu else 'No'}{f' ({gpu_memory_gb:.1f}GB)' if gpu_memory_gb else ''}")
        logger.info(f"   Platform: {platform_system} {architecture}")
        
        self.hardware_profile = profile
        return profile
    
    def run_benchmarks(self) -> Dict[str, float]:
        """Run performance benchmarks to determine optimal settings"""
        logger.info("🏃 Running performance benchmarks...")
        
        if not self.hardware_profile:
            raise ValueError("Hardware profile not detected. Run detect_hardware() first.")
        
        benchmarks = {}
        
        # CPU benchmark
        logger.info("   📈 CPU performance test...")
        cpu_start = time.time()
        # Simple CPU-intensive task
        result = sum(i * i for i in range(100000))
        cpu_time = time.time() - cpu_start
        benchmarks['cpu_performance'] = 1.0 / cpu_time  # Higher is better
        
        # Memory benchmark
        logger.info("   💾 Memory performance test...")
        memory_start = time.time()
        # Memory allocation test
        test_data = [i for i in range(50000)]
        memory_time = time.time() - memory_start
        benchmarks['memory_performance'] = 1.0 / memory_time
        del test_data
        
        # I/O benchmark
        logger.info("   💿 I/O performance test...")
        io_start = time.time()
        test_file = Path("temp_benchmark_file.tmp")
        try:
            with open(test_file, 'w') as f:
                for i in range(1000):
                    f.write(f"benchmark line {i}\n")
            with open(test_file, 'r') as f:
                content = f.read()
            test_file.unlink()
        except Exception as e:
            logger.warning(f"I/O benchmark failed: {e}")
        io_time = time.time() - io_start
        benchmarks['io_performance'] = 1.0 / io_time
        
        logger.info(f"📊 Benchmark Results:")
        logger.info(f"   CPU: {benchmarks['cpu_performance']:.2f}")
        logger.info(f"   Memory: {benchmarks['memory_performance']:.2f}")
        logger.info(f"   I/O: {benchmarks['io_performance']:.2f}")
        
        self.benchmark_results = benchmarks
        return benchmarks
    
    def calculate_optimal_settings(self) -> OptimizedSettings:
        """Calculate optimal settings based on hardware profile and benchmarks"""
        logger.info("⚙️  Calculating optimal settings...")
        
        if not self.hardware_profile or not self.benchmark_results:
            raise ValueError("Hardware profile and benchmarks required")
        
        hw = self.hardware_profile
        bench = self.benchmark_results
        
        # Determine optimal workers
        if hw.cpu_cores >= 8:
            workers = min(4, hw.cpu_cores // 2)
        elif hw.cpu_cores >= 4:
            workers = 2
        else:
            workers = 1
        
        # Determine optimal chunk size based on memory and CPU
        if hw.total_memory_gb >= 16 and hw.cpu_cores >= 8:
            chunk_size = 200
        elif hw.total_memory_gb >= 8 and hw.cpu_cores >= 4:
            chunk_size = 150
        elif hw.total_memory_gb >= 4:
            chunk_size = 100
        else:
            chunk_size = 50
        
        # Cache settings based on available memory
        cache_enabled = hw.available_memory_gb >= 2.0
        if hw.available_memory_gb >= 8:
            cache_size = 200
        elif hw.available_memory_gb >= 4:
            cache_size = 100
        else:
            cache_size = 50
        
        # Preload models if we have enough memory
        preload_models = hw.available_memory_gb >= 4.0
        
        # Text length limits based on memory
        if hw.total_memory_gb >= 16:
            max_text_length = 8000
        elif hw.total_memory_gb >= 8:
            max_text_length = 5000
        else:
            max_text_length = 3000
        
        # Timeout based on CPU performance
        cpu_perf = bench.get('cpu_performance', 1.0)
        if cpu_perf > 2.0:  # Fast CPU
            timeout_seconds = 30
        elif cpu_perf > 1.0:  # Medium CPU
            timeout_seconds = 45
        else:  # Slow CPU
            timeout_seconds = 60
        
        # Device selection
        device = "cuda" if hw.has_gpu and hw.gpu_memory_gb and hw.gpu_memory_gb >= 2.0 else "cpu"
        
        settings = OptimizedSettings(
            workers=workers,
            chunk_size=chunk_size,
            cache_enabled=cache_enabled,
            cache_size=cache_size,
            preload_models=preload_models,
            max_text_length=max_text_length,
            timeout_seconds=timeout_seconds,
            device=device
        )
        
        logger.info(f"🎯 Optimal Settings:")
        logger.info(f"   Workers: {workers}")
        logger.info(f"   Chunk Size: {chunk_size}")
        logger.info(f"   Cache: {'Enabled' if cache_enabled else 'Disabled'} ({cache_size} items)")
        logger.info(f"   Preload Models: {'Yes' if preload_models else 'No'}")
        logger.info(f"   Max Text Length: {max_text_length}")
        logger.info(f"   Timeout: {timeout_seconds}s")
        logger.info(f"   Device: {device}")
        
        self.optimized_settings = settings
        return settings
    
    def generate_override_config(self) -> Dict[str, Any]:
        """Generate override.json configuration"""
        if not self.optimized_settings:
            raise ValueError("Optimal settings not calculated")
        
        settings = self.optimized_settings
        
        config = {
            "_comment": "Auto-generated hardware-optimized configuration",
            "_generated_by": "Kokoro Hardware Optimizer",
            "_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "_hardware_profile": {
                "cpu_cores": self.hardware_profile.cpu_cores,
                "total_memory_gb": round(self.hardware_profile.total_memory_gb, 1),
                "has_gpu": self.hardware_profile.has_gpu,
                "platform": self.hardware_profile.platform_system
            },
            "server": {
                "workers": settings.workers
            },
            "performance": {
                "cache_enabled": settings.cache_enabled,
                "chunk_size": settings.chunk_size,
                "max_text_length": settings.max_text_length,
                "timeout_seconds": settings.timeout_seconds,
                "preload_models": settings.preload_models
            },
            "cache": {
                "enabled": settings.cache_enabled,
                "max_size": settings.cache_size
            }
        }
        
        # Add device setting if GPU is available
        if settings.device == "cuda":
            config["tts"] = {"device": "cuda"}
        
        return config
    
    def save_override_config(self, config: Dict[str, Any], backup_existing: bool = True) -> bool:
        """Save override configuration to file"""
        override_path = Path("override.json")
        
        # Backup existing override.json if it exists
        if backup_existing and override_path.exists():
            backup_path = Path(f"override.json.backup.{int(time.time())}")
            override_path.rename(backup_path)
            logger.info(f"📁 Backed up existing override.json to {backup_path}")
        
        try:
            with open(override_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"✅ Saved optimized configuration to {override_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save override.json: {e}")
            return False
    
    def optimize_system(self, force: bool = False) -> bool:
        """Run complete hardware optimization process"""
        override_path = Path("override.json")
        
        # Check if optimization already exists
        if not force and override_path.exists():
            try:
                with open(override_path, 'r') as f:
                    existing_config = json.load(f)
                if "_generated_by" in existing_config and existing_config["_generated_by"] == "Kokoro Hardware Optimizer":
                    logger.info("✅ Hardware optimization already completed")
                    logger.info("💡 Use --force to re-run optimization")
                    return True
            except Exception:
                pass  # Continue with optimization if we can't read existing config
        
        try:
            logger.info("🚀 Starting automatic hardware optimization...")
            
            # Step 1: Detect hardware
            self.detect_hardware()
            
            # Step 2: Run benchmarks
            self.run_benchmarks()
            
            # Step 3: Calculate optimal settings
            self.calculate_optimal_settings()
            
            # Step 4: Generate and save configuration
            config = self.generate_override_config()
            success = self.save_override_config(config)
            
            if success:
                logger.info("🎉 Hardware optimization completed successfully!")
                logger.info("💡 Restart the server to apply optimized settings")
                return True
            else:
                logger.error("❌ Hardware optimization failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Hardware optimization failed: {e}")
            return False

def run_hardware_optimization(force: bool = False) -> bool:
    """Convenience function to run hardware optimization"""
    optimizer = HardwareOptimizer()
    return optimizer.optimize_system(force=force)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Kokoro Hardware Optimizer")
    parser.add_argument("--force", action="store_true", help="Force re-optimization even if already done")
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
    
    success = run_hardware_optimization(force=args.force)
    exit(0 if success else 1)
