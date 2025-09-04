#!/usr/bin/env python3
"""
Test imports for LiteTTS Docker build
Validates that all required modules can be imported successfully
"""

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_core_imports():
    """Test core Python imports"""
    try:
        import os
        import json
        import time
        import asyncio
        import pathlib
        logger.info("✅ Core Python modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Core Python import failed: {e}")
        return False

def test_web_framework_imports():
    """Test web framework imports"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        logger.info("✅ Web framework modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Web framework import failed: {e}")
        return False

def test_audio_processing_imports():
    """Test audio processing imports"""
    try:
        import numpy
        import soundfile
        logger.info("✅ Audio processing modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Audio processing import failed: {e}")
        return False

def test_ml_framework_imports():
    """Test ML framework imports"""
    try:
        import onnxruntime
        logger.info("✅ ONNX Runtime imported successfully")
        
        # Test optional imports
        try:
            import torch
            logger.info("✅ PyTorch imported successfully")
        except ImportError:
            logger.info("ℹ️ PyTorch not available (optional)")
        
        return True
    except ImportError as e:
        logger.error(f"❌ ML framework import failed: {e}")
        return False

def test_litetts_imports():
    """Test LiteTTS module imports"""
    try:
        # Test basic LiteTTS imports
        from LiteTTS.config import config
        from LiteTTS.logging_config import setup_logging
        logger.info("✅ LiteTTS core modules imported successfully")
        
        # Test performance modules
        try:
            from LiteTTS.performance.memory_optimization import MemoryOptimizer
            from LiteTTS.performance.cpu_optimizer import CPUOptimizer
            logger.info("✅ LiteTTS performance modules imported successfully")
        except ImportError as e:
            logger.warning(f"⚠️ Some LiteTTS performance modules not available: {e}")
        
        return True
    except ImportError as e:
        logger.error(f"❌ LiteTTS import failed: {e}")
        return False

def main():
    """Run all import tests"""
    logger.info("🧪 Starting import tests...")
    
    tests = [
        ("Core Python modules", test_core_imports),
        ("Web framework modules", test_web_framework_imports),
        ("Audio processing modules", test_audio_processing_imports),
        ("ML framework modules", test_ml_framework_imports),
        ("LiteTTS modules", test_litetts_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            logger.error(f"Test failed: {test_name}")
    
    logger.info(f"Import tests completed: {passed}/{total} passed")
    
    if passed == total:
        logger.info("🎉 All import tests passed!")
        return 0
    else:
        logger.error(f"❌ {total - passed} import tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
