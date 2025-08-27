#!/usr/bin/env python3
"""
Check kokoro_onnx installation and compatibility
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def check_kokoro_installation():
    """Check kokoro_onnx installation and version"""
    print("🔍 Kokoro ONNX Installation Check")
    print("=" * 40)
    
    try:
        import kokoro_onnx
        print("✅ kokoro_onnx imported successfully")
        
        # Check version
        version = getattr(kokoro_onnx, '__version__', 'unknown')
        print(f"📦 Version: {version}")
        
        # Check available attributes
        attrs = [attr for attr in dir(kokoro_onnx) if not attr.startswith('_')]
        print(f"📋 Available attributes: {attrs}")
        
        return True
        
    except ImportError as e:
        print(f"❌ kokoro_onnx not installed: {e}")
        print("💡 Install with: uv add kokoro-onnx")
        return False
    except Exception as e:
        print(f"❌ Error importing kokoro_onnx: {e}")
        return False

def check_model_files():
    """Check if model files exist and are valid"""
    print(f"\n📁 Model Files Check")
    print("-" * 25)
    
    model_path = Path("LiteTTS/models/model_q8f16.onnx")
    voices_path = Path("LiteTTS/voices/voices-v1.0.bin")
    
    files_to_check = [
        (model_path, "ONNX Model", 80_000_000, 90_000_000),  # ~86MB
        (voices_path, "Voices File", 400_000, 600_000)       # ~500KB
    ]
    
    all_good = True
    
    for file_path, name, min_size, max_size in files_to_check:
        if file_path.exists():
            size = file_path.stat().st_size
            if min_size <= size <= max_size:
                print(f"✅ {name}: {size:,} bytes (OK)")
            else:
                print(f"⚠️  {name}: {size:,} bytes (unexpected size)")
                all_good = False
        else:
            print(f"❌ {name}: Missing")
            all_good = False
    
    return all_good

def test_model_creation():
    """Test creating the Kokoro model"""
    print(f"\n🧪 Model Creation Test")
    print("-" * 25)
    
    try:
        from kokoro_onnx import Kokoro
        
        model_path = "LiteTTS/models/model_q8f16.onnx"
        voices_path = "LiteTTS/voices/voices-v1.0.bin"
        
        print(f"🚀 Creating Kokoro model...")
        print(f"   Model: {model_path}")
        print(f"   Voices: {voices_path}")
        
        model = Kokoro(model_path, voices_path)
        print("✅ Model created successfully")
        
        # Test simple generation
        print("🎤 Testing simple generation...")
        audio, sample_rate = model.create("hello", voice="af_heart")
        print(f"✅ Generation successful: {len(audio)} samples at {sample_rate}Hz")
        
        return True
        
    except Exception as e:
        print(f"❌ Model creation/test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Check if it's the tensor type error
        if "tensor" in str(e).lower() and "int32" in str(e):
            print("🔧 This is the tensor type error we're trying to fix!")
            print("   The model expects float tensors but is receiving int32")
            
        return False

def suggest_fixes():
    """Suggest potential fixes"""
    print(f"\n💡 Potential Fixes")
    print("-" * 20)
    
    print("1. **Update kokoro_onnx**:")
    print("   uv add kokoro-onnx@latest")
    
    print("\n2. **Try different model files**:")
    print("   - The model_q8f16.onnx might be incompatible")
    print("   - Try downloading the original model")
    
    print("\n3. **Check ONNX Runtime**:")
    print("   uv add onnxruntime")
    
    print("\n4. **Alternative kokoro packages**:")
    print("   - Try: uv add kokoro-tts")
    print("   - Or: uv add kokoro")

def main():
    kokoro_ok = check_kokoro_installation()
    files_ok = check_model_files()
    
    if kokoro_ok and files_ok:
        model_ok = test_model_creation()
        if not model_ok:
            suggest_fixes()
    else:
        print("\n❌ Prerequisites not met")
        if not kokoro_ok:
            print("   Install kokoro_onnx first")
        if not files_ok:
            print("   Download model files first")

if __name__ == "__main__":
    main()