#!/usr/bin/env python3
"""
Debug script to examine voice data format and kokoro_onnx expectations
"""

import numpy as np
from pathlib import Path
import sys

def debug_voice_files():
    """Debug individual voice files"""
    voices_dir = Path("LiteTTS/voices")
    
    print("🔍 Debugging Voice Files")
    print("=" * 50)
    
    # Check individual .bin files
    bin_files = list(voices_dir.glob("*.bin"))
    print(f"📁 Found {len(bin_files)} .bin files")
    
    if bin_files:
        # Examine first few voice files
        for i, voice_file in enumerate(bin_files[:3]):
            print(f"\n📄 Voice file: {voice_file.name}")
            try:
                voice_data = np.fromfile(voice_file, dtype=np.float32)
                print(f"   Raw shape: {voice_data.shape}")
                print(f"   Raw size: {len(voice_data)}")
                print(f"   Expected size (510*256): {510*256}")
                print(f"   Size match: {len(voice_data) == 510*256}")
                
                if len(voice_data) == 510 * 256:
                    reshaped = voice_data.reshape(510, 256)
                    print(f"   Reshaped: {reshaped.shape}")
                    print(f"   Data type: {reshaped.dtype}")
                    print(f"   Min/Max: {reshaped.min():.4f} / {reshaped.max():.4f}")
                
            except Exception as e:
                print(f"   ❌ Error loading: {e}")

def debug_npz_file():
    """Debug the combined NPZ file"""
    npz_file = Path("LiteTTS/voices/combined_voices.npz")
    
    print(f"\n🔍 Debugging NPZ File: {npz_file}")
    print("=" * 50)
    
    if not npz_file.exists():
        print("❌ NPZ file not found")
        return
    
    try:
        npz_data = np.load(npz_file)
        print(f"📦 NPZ keys: {list(npz_data.keys())}")
        print(f"📊 Total voices in NPZ: {len(npz_data.keys())}")
        
        # Examine first few voices
        for i, voice_name in enumerate(list(npz_data.keys())[:3]):
            voice_data = npz_data[voice_name]
            print(f"\n🎭 Voice: {voice_name}")
            print(f"   Shape: {voice_data.shape}")
            print(f"   Data type: {voice_data.dtype}")
            print(f"   Min/Max: {voice_data.min():.4f} / {voice_data.max():.4f}")
            print(f"   Is contiguous: {voice_data.flags.c_contiguous}")
            
    except Exception as e:
        print(f"❌ Error loading NPZ: {e}")

def debug_kokoro_onnx_expectations():
    """Debug what kokoro_onnx expects"""
    print(f"\n🔍 Debugging kokoro_onnx Expectations")
    print("=" * 50)
    
    try:
        from kokoro_onnx import Kokoro
        
        # Try to load the model and examine its voice loading
        model_path = "LiteTTS/models/model_q8f16.onnx"
        npz_path = "LiteTTS/voices/combined_voices.npz"
        
        if not Path(model_path).exists():
            print(f"❌ Model not found: {model_path}")
            return
            
        if not Path(npz_path).exists():
            print(f"❌ NPZ file not found: {npz_path}")
            return
        
        print(f"🚀 Loading model...")
        print(f"   Model: {model_path}")
        print(f"   Voices: {npz_path}")
        
        model = Kokoro(model_path, npz_path)
        print(f"✅ Model loaded successfully")
        
        # Examine the voices attribute
        print(f"\n🎭 Model voices attribute:")
        print(f"   Type: {type(model.voices)}")
        print(f"   Shape: {model.voices.shape if hasattr(model.voices, 'shape') else 'No shape'}")
        
        # Check available voices
        if hasattr(model.voices, 'files'):
            available_voices = list(model.voices.files)
            print(f"   Available voices: {len(available_voices)}")
            print(f"   First few: {available_voices[:5]}")
            
            # Examine voice data format
            if available_voices:
                first_voice = available_voices[0]
                voice_data = model.voices[first_voice]
                print(f"\n🔍 First voice ({first_voice}):")
                print(f"   Shape: {voice_data.shape}")
                print(f"   Data type: {voice_data.dtype}")
                
        return model
        
    except Exception as e:
        print(f"❌ Error with kokoro_onnx: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main debug function"""
    print("🐛 Voice Data Format Debug Tool")
    print("=" * 60)
    
    debug_voice_files()
    debug_npz_file()
    model = debug_kokoro_onnx_expectations()
    
    if model:
        print(f"\n🧪 Testing voice access...")
        try:
            # Test accessing a specific voice
            test_voice = "af_heart"
            if hasattr(model.voices, 'files') and test_voice in model.voices.files:
                voice_data = model.voices[test_voice]
                print(f"✅ Successfully accessed {test_voice}: {voice_data.shape}")
            else:
                print(f"❌ Voice {test_voice} not found in model.voices")
                
        except Exception as e:
            print(f"❌ Error accessing voice: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
