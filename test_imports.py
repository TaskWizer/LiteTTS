#!/usr/bin/env python3
"""
Test critical imports for LiteTTS Docker container
"""

import sys
import traceback

def test_imports():
    """Test critical imports for LiteTTS"""
    print("Testing critical imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import onnxruntime
        print("✅ ONNX Runtime imported successfully")
    except ImportError as e:
        print(f"❌ ONNX Runtime import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
        import torch
        print("✅ PyTorch imported successfully")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    print("✅ All critical imports successful")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
