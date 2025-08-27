#!/usr/bin/env python3
"""
Comprehensive server startup test and dependency checker
"""

import sys
import traceback
import importlib
import subprocess
import os
from pathlib import Path

# Add the project root to the path so we can import modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check if we're running in the correct uv environment"""
    print("🔍 Checking Python environment...")

    # Check if we're in a uv environment
    in_uv_env = os.environ.get('VIRTUAL_ENV') or 'uv' in sys.executable

    if not in_uv_env:
        print("⚠️  Not running in uv environment!")
        print("   Current Python:", sys.executable)
        print("   To run with correct environment:")
        print("   uv run python LiteTTS/tests/test_server_startup.py")
        print()
        return False
    else:
        print("✅ Running in uv environment")
        print(f"   Python: {sys.executable}")
        return True

def test_core_imports():
    """Test importing core modules"""
    print("🔍 Testing core infrastructure...")
    
    core_modules = [
        ("kokoro.config", "Configuration system"),
        ("kokoro.exceptions", "Exception handling"),
        ("kokoro.logging_config", "Logging system"),
        ("kokoro.startup", "Startup validation"),
        ("kokoro.cache", "Cache system (with legacy support)")
    ]
    
    for module_name, description in core_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {description}")
        except Exception as e:
            print(f"❌ {description}: {e}")
            return False
    
    return True

def test_cache_manager():
    """Test cache manager specifically"""
    try:
        from LiteTTS.cache import cache_manager
        print("✅ Cache manager import")
        
        # Test basic functionality
        cache_manager.enable()
        stats = cache_manager.get_stats()
        print(f"✅ Cache manager functionality (enabled: {stats['enabled']})")
        return True
    except Exception as e:
        print(f"❌ Cache manager: {e}")
        return False

def check_dependencies():
    """Check required dependencies"""
    print("\n🔍 Checking dependencies...")
    
    required_deps = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("numpy", "Numerical computing"),
        ("soundfile", "Audio file I/O"),
        ("onnxruntime", "ONNX model runtime")
    ]
    
    optional_deps = [
        ("torch", "PyTorch (for CUDA support)"),
        ("psutil", "System monitoring")
    ]
    
    missing_required = []
    missing_optional = []
    
    for dep, description in required_deps:
        try:
            importlib.import_module(dep)
            print(f"✅ {description}")
        except ImportError:
            missing_required.append((dep, description))
            print(f"❌ {description}")
    
    for dep, description in optional_deps:
        try:
            importlib.import_module(dep)
            print(f"✅ {description}")
        except ImportError:
            missing_optional.append((dep, description))
            print(f"⚠️  {description} (optional)")
    
    return missing_required, missing_optional

def test_app_import():
    """Test importing the main app"""
    print("\n🔍 Testing main application...")
    
    try:
        import app
        print("✅ Main app imports successfully")
        
        # Test if the app can be created
        if hasattr(app, 'app'):
            print("✅ FastAPI app instance available")
        
        return True, []
        
    except ImportError as e:
        missing_dep = str(e).split("'")[1] if "'" in str(e) else "unknown"
        print(f"❌ App import failed: missing {missing_dep}")
        return False, [missing_dep]
    except Exception as e:
        print(f"❌ App import failed: {e}")
        traceback.print_exc()
        return False, []

def main():
    """Main test function"""
    print("🚀 Kokoro ONNX TTS API - Comprehensive Startup Test")
    print("=" * 50)

    # Check environment first
    env_ok = check_environment()
    if not env_ok:
        print("\n" + "=" * 50)
        print("❌ ENVIRONMENT ISSUE")
        print("=" * 50)
        print("Please run with: uv run python test_server_startup.py")
        return 1

    # Test core infrastructure
    core_success = test_core_imports()
    cache_success = test_cache_manager()
    
    # Check dependencies
    missing_required, missing_optional = check_dependencies()
    
    # Test app import
    app_success, app_missing = test_app_import()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if core_success and cache_success:
        print("✅ Core infrastructure: WORKING")
        print("✅ Cache system: WORKING")
        print("✅ Configuration system: WORKING")
    else:
        print("❌ Core infrastructure: FAILED")
        return 1
    
    if not missing_required and app_success:
        print("✅ All dependencies: INSTALLED")
        print("✅ Server ready to start!")
        
        print("\n🚀 Start the server with:")
        print("   uv run uvicorn app:app --host 0.0.0.0 --port 8000 --reload")
        
    else:
        print("⚠️  Missing dependencies detected")
        
        if missing_required:
            print("\n📦 Install required dependencies:")
            deps = " ".join([dep for dep, _ in missing_required])
            print(f"   uv add {deps}")
        
        if missing_optional:
            print("\n📦 Optional dependencies (recommended):")
            deps = " ".join([dep for dep, _ in missing_optional])
            print(f"   uv add {deps}")
        
        print("\n🔧 After installing dependencies, test again:")
        print("   uv run python LiteTTS/tests/test_server_startup.py")
    
    return 0 if (core_success and cache_success) else 1

if __name__ == "__main__":
    sys.exit(main())