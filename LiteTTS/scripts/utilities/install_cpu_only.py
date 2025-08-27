#!/usr/bin/env python3
"""
CPU-only installation script for Kokoro ONNX TTS API
Ensures no GPU/CUDA dependencies are installed
"""

import subprocess
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status"""
    try:
        logger.info(f"🔧 {description}")
        logger.info(f"   Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.stdout:
            logger.info(f"   Output: {result.stdout.strip()}")
        
        logger.info(f"✅ {description} - Success")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - Failed")
        logger.error(f"   Error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ {description} - Exception: {e}")
        return False

def check_gpu_packages():
    """Check for and warn about GPU packages"""
    gpu_packages = [
        "onnxruntime-gpu",
        "torch",
        "tensorflow-gpu",
        "cupy",
        "nvidia-ml-py",
        "pycuda"
    ]
    
    installed_gpu_packages = []
    
    for package in gpu_packages:
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "show", package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                installed_gpu_packages.append(package)
        except:
            pass
    
    if installed_gpu_packages:
        logger.warning(f"⚠️ GPU packages detected: {', '.join(installed_gpu_packages)}")
        logger.warning("   These may cause conflicts with CPU-only operation")
        logger.warning("   Consider uninstalling them if you encounter issues")
        return False
    else:
        logger.info("✅ No conflicting GPU packages detected")
        return True

def install_cpu_dependencies():
    """Install CPU-only dependencies"""
    logger.info("🚀 Installing CPU-only dependencies for Kokoro ONNX TTS API")
    
    # Core dependencies (CPU-only)
    dependencies = [
        "fastapi>=0.95.0",
        "uvicorn>=0.21.0", 
        "soundfile>=0.12.0",
        "numpy>=1.24.0",
        "requests>=2.25.0",
        "pydantic>=2.0.0",
        # Explicitly install CPU-only ONNX Runtime
        "onnxruntime>=1.22.1",
        # Kokoro ONNX (should be CPU-only)
        "kokoro-onnx>=0.4.9"
    ]
    
    success = True
    
    # Install each dependency
    for dep in dependencies:
        cmd = [sys.executable, "-m", "pip", "install", dep]
        if not run_command(cmd, f"Installing {dep}"):
            success = False
    
    return success

def verify_installation():
    """Verify the installation works correctly"""
    logger.info("🧪 Verifying installation...")
    
    try:
        # Test imports
        import fastapi
        import uvicorn
        import soundfile
        import numpy
        import requests
        import pydantic
        import onnxruntime
        
        logger.info("✅ Core dependencies imported successfully")
        
        # Test ONNX Runtime providers (should be CPU only)
        providers = onnxruntime.get_available_providers()
        logger.info(f"📋 ONNX Runtime providers: {providers}")
        
        # Check for GPU providers
        gpu_providers = [p for p in providers if 'CUDA' in p or 'GPU' in p]
        if gpu_providers:
            logger.warning(f"⚠️ GPU providers detected: {gpu_providers}")
            logger.warning("   This may indicate GPU dependencies are installed")
        else:
            logger.info("✅ CPU-only ONNX Runtime confirmed")
        
        # Try to import kokoro-onnx
        try:
            import kokoro_onnx
            logger.info(f"✅ kokoro-onnx imported successfully (version: {getattr(kokoro_onnx, '__version__', 'unknown')})")
        except ImportError as e:
            logger.error(f"❌ Failed to import kokoro-onnx: {e}")
            return False
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False

def main():
    """Main installation function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🎯 Kokoro ONNX TTS API - CPU-Only Installation")
    logger.info("=" * 50)
    
    # Check for existing GPU packages
    logger.info("🔍 Checking for conflicting GPU packages...")
    check_gpu_packages()
    
    # Install dependencies
    logger.info("📦 Installing CPU-only dependencies...")
    if not install_cpu_dependencies():
        logger.error("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Verify installation
    logger.info("🧪 Verifying installation...")
    if not verify_installation():
        logger.error("❌ Installation verification failed")
        sys.exit(1)
    
    logger.info("🎉 CPU-only installation completed successfully!")
    logger.info("💡 You can now run: uv run python app.py")

if __name__ == "__main__":
    main()
