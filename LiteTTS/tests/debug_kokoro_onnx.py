#!/usr/bin/env python3
"""
Debug script to examine kokoro_onnx internal processing
"""

import numpy as np
from pathlib import Path
import sys

def debug_kokoro_onnx_internals():
    """Debug kokoro_onnx internal processing"""
    print("🔍 Debugging kokoro_onnx Internal Processing")
    print("=" * 60)
    
    try:
        from kokoro_onnx import Kokoro
        
        model_path = "LiteTTS/models/model_q8f16.onnx"
        npz_path = "LiteTTS/voices/combined_voices.npz"
        
        print(f"🚀 Loading model...")
        model = Kokoro(model_path, npz_path)
        print(f"✅ Model loaded successfully")
        
        # Examine the model's internal structure
        print(f"\n🔍 Model attributes:")
        for attr in dir(model):
            if not attr.startswith('_'):
                try:
                    value = getattr(model, attr)
                    if not callable(value):
                        print(f"   {attr}: {type(value)} - {str(value)[:100]}")
                except:
                    print(f"   {attr}: <unable to access>")
        
        # Check the ONNX session inputs
        print(f"\n🔍 ONNX Session inputs:")
        if hasattr(model, 'sess'):
            for input_info in model.sess.get_inputs():
                print(f"   Input: {input_info.name}")
                print(f"     Shape: {input_info.shape}")
                print(f"     Type: {input_info.type}")
        
        # Try to trace what happens during voice processing
        print(f"\n🧪 Testing voice processing...")
        test_voice = "af_heart"
        
        # Check if voice exists
        if test_voice in model.voices.files:
            voice_data = model.voices[test_voice]
            print(f"✅ Voice {test_voice} found: {voice_data.shape}")
            
            # Try to understand how kokoro_onnx processes the voice
            # Let's examine the _create_audio method more closely
            print(f"\n🔍 Attempting to trace voice processing...")
            
            # First, let's see what phonemes look like
            try:
                # This might fail, but let's see what we can learn
                text = "test"
                print(f"📝 Processing text: '{text}'")
                
                # Try to access the phonemizer if available
                if hasattr(model, 'phonemizer'):
                    print(f"   Phonemizer available: {type(model.phonemizer)}")
                
                # Try to get phonemes
                if hasattr(model, '_phonemize'):
                    phonemes = model._phonemize(text)
                    print(f"   Phonemes shape: {phonemes.shape if hasattr(phonemes, 'shape') else type(phonemes)}")
                    print(f"   Phonemes: {phonemes}")
                
            except Exception as e:
                print(f"   ❌ Error in phoneme processing: {e}")
            
        else:
            print(f"❌ Voice {test_voice} not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def debug_onnx_model_directly():
    """Debug the ONNX model directly"""
    print(f"\n🔍 Debugging ONNX Model Directly")
    print("=" * 60)
    
    try:
        import onnxruntime as ort
        
        model_path = "LiteTTS/models/model_q8f16.onnx"
        
        print(f"🚀 Loading ONNX session...")
        session = ort.InferenceSession(model_path)
        print(f"✅ ONNX session loaded")
        
        print(f"\n📊 Model inputs:")
        for input_info in session.get_inputs():
            print(f"   Name: {input_info.name}")
            print(f"   Shape: {input_info.shape}")
            print(f"   Type: {input_info.type}")
        
        print(f"\n📊 Model outputs:")
        for output_info in session.get_outputs():
            print(f"   Name: {output_info.name}")
            print(f"   Shape: {output_info.shape}")
            print(f"   Type: {output_info.type}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_voice_tensor_shapes():
    """Test different voice tensor shapes"""
    print(f"\n🧪 Testing Voice Tensor Shapes")
    print("=" * 60)
    
    # Load a voice and test different shapes
    npz_path = "LiteTTS/voices/combined_voices.npz"
    
    try:
        npz_data = np.load(npz_path)
        voice_name = "af_heart"
        
        if voice_name in npz_data:
            voice_data = npz_data[voice_name]
            print(f"📊 Original voice data: {voice_data.shape}")
            
            # Test different reshaping scenarios
            print(f"\n🔄 Testing different shapes:")
            
            # Current shape (510, 256)
            print(f"   Current: {voice_data.shape}")
            
            # Flattened (130560,)
            flattened = voice_data.flatten()
            print(f"   Flattened: {flattened.shape}")
            
            # Add batch dimension (1, 510, 256)
            batched = voice_data.reshape(1, 510, 256)
            print(f"   Batched: {batched.shape}")
            
            # Different arrangements
            print(f"   Transposed: {voice_data.T.shape}")
            print(f"   Reshaped (256, 510): {voice_data.reshape(256, 510).shape}")
            
            # Test what happens if we select a single style vector
            single_style = voice_data[0]  # First style vector
            print(f"   Single style vector: {single_style.shape}")
            
            # Add dimension to single style
            single_style_2d = single_style.reshape(1, -1)
            print(f"   Single style 2D: {single_style_2d.shape}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main debug function"""
    print("🐛 Kokoro ONNX Debug Tool")
    print("=" * 60)
    
    debug_onnx_model_directly()
    debug_kokoro_onnx_internals()
    test_voice_tensor_shapes()

if __name__ == "__main__":
    main()
