#!/usr/bin/env python3
"""
Verify the setup is working correctly
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def check_files():
    """Check if required files exist"""
    model_path = Path("LiteTTS/models/model_q8f16.onnx")
    voices_path = Path("LiteTTS/voices/voices-v1.0.bin")
    
    print("📁 Checking files...")
    print(f"   Model: {'✅' if model_path.exists() else '❌'} {model_path}")
    print(f"   Voices: {'✅' if voices_path.exists() else '❌'} {voices_path}")
    
    return model_path.exists() and voices_path.exists()

def test_downloader():
    """Test the downloader"""
    try:
        from LiteTTS.downloader import ensure_model_files
        print("📦 Testing downloader...")
        result = ensure_model_files()
        print(f"   Result: {'✅' if result else '❌'}")
        return result
    except Exception as e:
        print(f"   Error: ❌ {e}")
        return False

def test_imports():
    """Test that all imports work"""
    try:
        print("📚 Testing imports...")
        import app
        print("   app.py: ✅")
        
        from LiteTTS.downloader import ensure_model_files, get_available_voices
        print("   downloader: ✅")
        
        voices = get_available_voices()
        print(f"   Available voices: {voices}")
        
        return True
    except Exception as e:
        print(f"   Import error: ❌ {e}")
        return False

def main():
    print("🧪 Kokoro ONNX TTS API Setup Verification")
    print("=" * 40)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import test failed")
        return False
    
    # Test downloader
    if not test_downloader():
        print("\n❌ Downloader test failed")
        return False
    
    # Check files
    if not check_files():
        print("\n❌ File check failed")
        return False
    
    print("\n✅ All tests passed!")
    print("\n🚀 Ready to run:")
    print("   uv run uvicorn app:app --host 0.0.0.0 --port 8000 --reload")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)