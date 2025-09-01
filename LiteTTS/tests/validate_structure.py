#!/usr/bin/env python3
"""
Validate project structure and core configuration without requiring all dependencies
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def validate_structure():
    """Validate the project structure"""
    print("🔍 Validating Kokoro ONNX TTS API project structure...")
    
    # Check core files
    core_files = [
        "LiteTTS/__init__.py",
        "LiteTTS/config.py", 
        "LiteTTS/exceptions.py",
        "LiteTTS/logging_config.py",
        "LiteTTS/startup.py",
        ".env.example",
        "docs/PROJECT_STRUCTURE.md"
    ]
    
    # Check directories
    directories = [
        "LiteTTS/api",
        "LiteTTS/audio", 
        "LiteTTS/cache",
        "LiteTTS/nlp",
        "LiteTTS/tts",
        "LiteTTS/voice",
        "LiteTTS/models",
        "LiteTTS/voices",
        "docs",
        "LiteTTS/scripts",
        "LiteTTS/tests"
    ]
    
    missing_files = []
    missing_dirs = []
    
    # Check files
    for file_path in core_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    # Check directories
    for dir_path in directories:
        if not Path(dir_path).is_dir():
            missing_dirs.append(dir_path)
        else:
            print(f"✅ {dir_path}/")
    
    # Test core imports individually to isolate issues
    try:
        import LiteTTS.config
        print("✅ Configuration module")
    except Exception as e:
        print(f"❌ Configuration module: {e}")
        return False
    
    try:
        import LiteTTS.exceptions
        print("✅ Exception module")
    except Exception as e:
        print(f"❌ Exception module: {e}")
        return False
    
    try:
        import LiteTTS.logging_config
        print("✅ Logging module")
    except Exception as e:
        print(f"❌ Logging module: {e}")
        return False
    
    try:
        import LiteTTS.startup
        print("✅ Startup module")
    except Exception as e:
        print(f"❌ Startup module: {e}")
        return False
    
    # Report results
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    if missing_dirs:
        print(f"\n❌ Missing directories: {missing_dirs}")
        return False
    
    print("\n✅ Project structure validation completed successfully!")
    print("✅ Core configuration system is ready!")
    return True

if __name__ == "__main__":
    success = validate_structure()
    sys.exit(0 if success else 1)