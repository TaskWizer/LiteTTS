#!/usr/bin/env python3
"""
Hardware Detection and System Optimization for Kokoro TTS
Automatically detects system capabilities and optimizes configuration
"""

import os
import platform
import psutil
import hashlib
import json
import time
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class HardwareDetector:
    """Detects system hardware capabilities for optimization"""
    
    def __init__(self):
        self.system_info = self._detect_system_info()
        self.cpu_info = self._detect_cpu_info()
        self.memory_info = self._detect_memory_info()
        self.gpu_info = self._detect_gpu_info()
        self.storage_info = self._detect_storage_info()
        self.system_fingerprint = self._generate_system_fingerprint()
        
    def _detect_system_info(self) -> Dict[str, Any]:
        """Detect basic system information"""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'python_version': platform.python_version()
        }
    
    def _detect_cpu_info(self) -> Dict[str, Any]:
        """Detect CPU information and capabilities"""
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'max_frequency': 0,
            'min_frequency': 0,
            'current_frequency': 0,
            'cpu_usage_percent': psutil.cpu_percent(interval=1),
            'load_average': None
        }
        
        try:
            # Get CPU frequency information
            freq_info = psutil.cpu_freq()
            if freq_info:
                cpu_info['max_frequency'] = freq_info.max
                cpu_info['min_frequency'] = freq_info.min
                cpu_info['current_frequency'] = freq_info.current
        except Exception as e:
            logger.debug(f"Could not get CPU frequency info: {e}")
        
        try:
            # Get load average (Unix-like systems)
            if hasattr(os, 'getloadavg'):
                cpu_info['load_average'] = os.getloadavg()
        except Exception as e:
            logger.debug(f"Could not get load average: {e}")
        
        return cpu_info
    
    def _detect_memory_info(self) -> Dict[str, Any]:
        """Detect memory information"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_ram_gb': round(memory.total / (1024**3), 2),
            'available_ram_gb': round(memory.available / (1024**3), 2),
            'used_ram_gb': round(memory.used / (1024**3), 2),
            'ram_usage_percent': memory.percent,
            'total_swap_gb': round(swap.total / (1024**3), 2),
            'used_swap_gb': round(swap.used / (1024**3), 2),
            'swap_usage_percent': swap.percent
        }
    
    def _detect_gpu_info(self) -> Dict[str, Any]:
        """Detect GPU information"""
        gpu_info = {
            'cuda_available': False,
            'gpu_count': 0,
            'gpu_names': [],
            'total_vram_gb': 0,
            'available_vram_gb': 0
        }
        
        try:
            # Try to detect NVIDIA GPUs
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.free', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                gpu_info['cuda_available'] = True
                lines = result.stdout.strip().split('\n')
                
                for line in lines:
                    if line.strip():
                        parts = line.split(', ')
                        if len(parts) >= 3:
                            name = parts[0].strip()
                            total_vram = int(parts[1].strip())
                            free_vram = int(parts[2].strip())
                            
                            gpu_info['gpu_names'].append(name)
                            gpu_info['total_vram_gb'] += total_vram / 1024
                            gpu_info['available_vram_gb'] += free_vram / 1024
                
                gpu_info['gpu_count'] = len(gpu_info['gpu_names'])
                gpu_info['total_vram_gb'] = round(gpu_info['total_vram_gb'], 2)
                gpu_info['available_vram_gb'] = round(gpu_info['available_vram_gb'], 2)
                
        except Exception as e:
            logger.debug(f"Could not detect NVIDIA GPUs: {e}")
        
        try:
            # Try to detect other GPU types (AMD, Intel)
            if not gpu_info['cuda_available']:
                # This is a simplified detection - could be expanded
                if platform.system() == 'Linux':
                    result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
                    if 'VGA' in result.stdout or 'Display' in result.stdout:
                        gpu_info['gpu_count'] = 1
                        gpu_info['gpu_names'] = ['Integrated/Other GPU']
                        
        except Exception as e:
            logger.debug(f"Could not detect other GPUs: {e}")
        
        return gpu_info
    
    def _detect_storage_info(self) -> Dict[str, Any]:
        """Detect storage information"""
        storage_info = {
            'total_storage_gb': 0,
            'free_storage_gb': 0,
            'storage_type': 'unknown',
            'read_speed_mbps': 0,
            'write_speed_mbps': 0
        }
        
        try:
            # Get disk usage for current directory
            disk_usage = psutil.disk_usage('.')
            storage_info['total_storage_gb'] = round(disk_usage.total / (1024**3), 2)
            storage_info['free_storage_gb'] = round(disk_usage.free / (1024**3), 2)
            
            # Try to determine storage type (SSD vs HDD)
            storage_info['storage_type'] = self._detect_storage_type()
            
            # Perform simple speed test
            read_speed, write_speed = self._test_storage_speed()
            storage_info['read_speed_mbps'] = read_speed
            storage_info['write_speed_mbps'] = write_speed
            
        except Exception as e:
            logger.debug(f"Could not detect storage info: {e}")
        
        return storage_info
    
    def _detect_storage_type(self) -> str:
        """Detect if storage is SSD or HDD"""
        try:
            if platform.system() == 'Linux':
                # Check if the device is rotational
                import subprocess
                result = subprocess.run(['lsblk', '-d', '-o', 'name,rota'], 
                                      capture_output=True, text=True, timeout=5)
                if '0' in result.stdout:  # 0 means non-rotational (SSD)
                    return 'SSD'
                elif '1' in result.stdout:  # 1 means rotational (HDD)
                    return 'HDD'
            elif platform.system() == 'Windows':
                # Windows detection would require WMI queries
                return 'unknown'
            elif platform.system() == 'Darwin':  # macOS
                # macOS detection would require system_profiler
                return 'unknown'
        except Exception as e:
            logger.debug(f"Could not detect storage type: {e}")
        
        return 'unknown'
    
    def _test_storage_speed(self) -> Tuple[float, float]:
        """Test storage read/write speed (simple test)"""
        try:
            test_file = 'temp_speed_test.dat'
            test_size = 10 * 1024 * 1024  # 10MB test
            test_data = b'0' * test_size
            
            # Test write speed
            start_time = time.time()
            with open(test_file, 'wb') as f:
                f.write(test_data)
                f.flush()
                os.fsync(f.fileno())
            write_time = time.time() - start_time
            write_speed = (test_size / (1024 * 1024)) / write_time  # MB/s
            
            # Test read speed
            start_time = time.time()
            with open(test_file, 'rb') as f:
                data = f.read()
            read_time = time.time() - start_time
            read_speed = (test_size / (1024 * 1024)) / read_time  # MB/s
            
            # Clean up
            os.remove(test_file)
            
            return round(read_speed, 2), round(write_speed, 2)
            
        except Exception as e:
            logger.debug(f"Could not test storage speed: {e}")
            return 0.0, 0.0
    
    def _generate_system_fingerprint(self) -> str:
        """Generate a unique system fingerprint"""
        fingerprint_data = {
            'hostname': self.system_info.get('hostname', ''),
            'platform': self.system_info.get('platform', ''),
            'architecture': self.system_info.get('architecture', ''),
            'physical_cores': self.cpu_info.get('physical_cores', 0),
            'total_ram_gb': self.memory_info.get('total_ram_gb', 0),
            'gpu_count': self.gpu_info.get('gpu_count', 0)
        }
        
        # Create hash of system characteristics
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """Get system capabilities summary"""
        return {
            'cpu_score': self._calculate_cpu_score(),
            'memory_score': self._calculate_memory_score(),
            'gpu_score': self._calculate_gpu_score(),
            'storage_score': self._calculate_storage_score(),
            'overall_score': self._calculate_overall_score()
        }
    
    def _calculate_cpu_score(self) -> int:
        """Calculate CPU performance score (0-100)"""
        cores = self.cpu_info.get('logical_cores', 1)
        frequency = self.cpu_info.get('max_frequency', 2000) / 1000  # Convert to GHz
        
        # Simple scoring based on cores and frequency
        score = min(100, (cores * 10) + (frequency * 15))
        return int(score)
    
    def _calculate_memory_score(self) -> int:
        """Calculate memory score (0-100)"""
        total_ram = self.memory_info.get('total_ram_gb', 1)
        
        # Score based on available RAM
        if total_ram >= 32:
            return 100
        elif total_ram >= 16:
            return 80
        elif total_ram >= 8:
            return 60
        elif total_ram >= 4:
            return 40
        else:
            return 20
    
    def _calculate_gpu_score(self) -> int:
        """Calculate GPU score (0-100)"""
        if not self.gpu_info.get('cuda_available', False):
            return 20  # Basic score for integrated/other GPUs
        
        vram = self.gpu_info.get('total_vram_gb', 0)
        gpu_count = self.gpu_info.get('gpu_count', 0)
        
        # Score based on VRAM and GPU count
        score = min(100, (vram * 10) + (gpu_count * 20))
        return int(score)
    
    def _calculate_storage_score(self) -> int:
        """Calculate storage score (0-100)"""
        storage_type = self.storage_info.get('storage_type', 'unknown')
        read_speed = self.storage_info.get('read_speed_mbps', 0)
        write_speed = self.storage_info.get('write_speed_mbps', 0)
        
        base_score = 50
        if storage_type == 'SSD':
            base_score = 80
        elif storage_type == 'HDD':
            base_score = 40
        
        # Adjust based on speed
        avg_speed = (read_speed + write_speed) / 2
        if avg_speed > 500:  # Very fast SSD
            base_score = min(100, base_score + 20)
        elif avg_speed > 100:  # Good SSD/fast HDD
            base_score = min(100, base_score + 10)
        
        return int(base_score)
    
    def _calculate_overall_score(self) -> int:
        """Calculate overall system performance score (0-100)"""
        cpu_score = self._calculate_cpu_score()
        memory_score = self._calculate_memory_score()
        gpu_score = self._calculate_gpu_score()
        storage_score = self._calculate_storage_score()
        
        # Weighted average
        overall = (cpu_score * 0.3 + memory_score * 0.3 + gpu_score * 0.2 + storage_score * 0.2)
        return int(overall)
    
    def get_all_info(self) -> Dict[str, Any]:
        """Get all detected hardware information"""
        return {
            'system_info': self.system_info,
            'cpu_info': self.cpu_info,
            'memory_info': self.memory_info,
            'gpu_info': self.gpu_info,
            'storage_info': self.storage_info,
            'system_fingerprint': self.system_fingerprint,
            'capabilities': self.get_system_capabilities()
        }

# Example usage
if __name__ == "__main__":
    detector = HardwareDetector()
    
    print("🔧 Hardware Detection Results")
    print("=" * 40)
    
    info = detector.get_all_info()
    
    print(f"\n💻 System Info:")
    print(f"  Platform: {info['system_info']['platform']} {info['system_info']['architecture']}")
    print(f"  Hostname: {info['system_info']['hostname']}")
    print(f"  Fingerprint: {info['system_fingerprint']}")
    
    print(f"\n🔥 CPU Info:")
    print(f"  Cores: {info['cpu_info']['physical_cores']} physical, {info['cpu_info']['logical_cores']} logical")
    print(f"  Frequency: {info['cpu_info']['max_frequency']:.0f} MHz")
    print(f"  Usage: {info['cpu_info']['cpu_usage_percent']:.1f}%")
    
    print(f"\n💾 Memory Info:")
    print(f"  Total RAM: {info['memory_info']['total_ram_gb']} GB")
    print(f"  Available: {info['memory_info']['available_ram_gb']} GB")
    print(f"  Usage: {info['memory_info']['ram_usage_percent']:.1f}%")
    
    print(f"\n🎮 GPU Info:")
    print(f"  CUDA Available: {info['gpu_info']['cuda_available']}")
    print(f"  GPU Count: {info['gpu_info']['gpu_count']}")
    if info['gpu_info']['gpu_names']:
        print(f"  GPUs: {', '.join(info['gpu_info']['gpu_names'])}")
    if info['gpu_info']['total_vram_gb'] > 0:
        print(f"  VRAM: {info['gpu_info']['total_vram_gb']} GB total, {info['gpu_info']['available_vram_gb']} GB available")
    
    print(f"\n💿 Storage Info:")
    print(f"  Type: {info['storage_info']['storage_type']}")
    print(f"  Total: {info['storage_info']['total_storage_gb']} GB")
    print(f"  Free: {info['storage_info']['free_storage_gb']} GB")
    print(f"  Speed: {info['storage_info']['read_speed_mbps']} MB/s read, {info['storage_info']['write_speed_mbps']} MB/s write")
    
    print(f"\n📊 Performance Scores:")
    caps = info['capabilities']
    print(f"  CPU Score: {caps['cpu_score']}/100")
    print(f"  Memory Score: {caps['memory_score']}/100")
    print(f"  GPU Score: {caps['gpu_score']}/100")
    print(f"  Storage Score: {caps['storage_score']}/100")
    print(f"  Overall Score: {caps['overall_score']}/100")
