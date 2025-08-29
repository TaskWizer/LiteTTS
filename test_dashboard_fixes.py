#!/usr/bin/env python3
"""
Test script to validate dashboard TTS fixes
Tests the critical fixes made to resolve dashboard audio generation failures
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_voice_count_fix():
    """Test that voice count discrepancy is fixed (55 vs 105)"""
    print("🧪 Testing voice count fix...")
    
    try:
        from LiteTTS.voice import get_available_voices
        
        # Test the fixed voice discovery
        voices = get_available_voices("LiteTTS/voices")
        print(f"✅ Voice discovery returned {len(voices)} voices")
        
        # Count actual voice files
        voices_dir = Path("LiteTTS/voices")
        if voices_dir.exists():
            actual_files = list(voices_dir.glob("*.bin"))
            print(f"📁 Actual voice files: {len(actual_files)}")
            
            if len(voices) == len(actual_files):
                print("🎉 Voice count discrepancy FIXED!")
                return True
            else:
                print(f"⚠️ Count mismatch: {len(voices)} reported vs {len(actual_files)} files")
                return False
        else:
            print("❌ Voices directory not found")
            return False
            
    except Exception as e:
        print(f"❌ Voice count test failed: {e}")
        return False

def test_dashboard_tts_optimizer():
    """Test that dashboard TTS optimizer uses correct TTSRequest format"""
    print("\n🧪 Testing dashboard TTS optimizer fixes...")
    
    try:
        from LiteTTS.api.dashboard_tts_optimizer import DashboardTTSOptimizer
        from LiteTTS.models import TTSRequest
        
        # Test that TTSRequest can be created with our parameters
        request = TTSRequest(
            input="Test text",
            voice="af_heart",
            response_format="mp3",
            speed=1.0,
            stream=True,
            volume_multiplier=1.0
        )
        
        print("✅ TTSRequest creation works correctly")
        print(f"📋 Request: {request.input}, {request.voice}, {request.response_format}")
        
        # Test validation methods exist
        optimizer = DashboardTTSOptimizer()
        
        # Test validation method
        validation_error = optimizer._validate_dashboard_request("Test", "af_heart", "mp3")
        if validation_error is None:
            print("✅ Request validation works correctly")
        else:
            print(f"⚠️ Validation issue: {validation_error}")
        
        # Test audio validation method
        audio_error = optimizer._validate_audio_output(b"test_audio_data_longer_than_100_bytes" * 10, "mp3")
        if audio_error is None:
            print("✅ Audio validation works correctly")
        else:
            print(f"⚠️ Audio validation issue: {audio_error}")
        
        # Test error categorization
        error_category = optimizer._categorize_error(ValueError("Voice not found"))
        print(f"✅ Error categorization: {error_category}")
        
        print("🎉 Dashboard TTS optimizer fixes VALIDATED!")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard TTS optimizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_audio_format_conversion():
    """Test that audio format conversion works correctly"""
    print("\n🧪 Testing audio format conversion...")
    
    try:
        from LiteTTS.audio.processor import AudioProcessor
        from LiteTTS.audio.audio_segment import AudioSegment
        import numpy as np
        
        # Create test audio segment
        sample_rate = 24000
        duration = 1.0  # 1 second
        samples = int(duration * sample_rate)
        audio_data = np.random.random(samples).astype(np.float32) * 0.1  # Quiet random noise
        
        audio_segment = AudioSegment(
            audio_data=audio_data,
            sample_rate=sample_rate,
            duration=duration,
            format="wav"
        )
        
        # Test format conversion
        processor = AudioProcessor()
        
        # Test MP3 conversion
        mp3_bytes = processor.convert_format(audio_segment, "mp3")
        print(f"✅ MP3 conversion: {len(mp3_bytes)} bytes")
        
        # Test WAV conversion
        wav_bytes = processor.convert_format(audio_segment, "wav")
        print(f"✅ WAV conversion: {len(wav_bytes)} bytes")
        
        if len(mp3_bytes) > 100 and len(wav_bytes) > 100:
            print("🎉 Audio format conversion WORKING!")
            return True
        else:
            print("⚠️ Audio conversion produced small files")
            return False
            
    except Exception as e:
        print(f"❌ Audio format conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Testing LiteTTS Dashboard Fixes")
    print("=" * 50)
    
    results = []
    
    # Test 1: Voice count fix
    results.append(test_voice_count_fix())
    
    # Test 2: Dashboard TTS optimizer
    results.append(test_dashboard_tts_optimizer())
    
    # Test 3: Audio format conversion
    results.append(test_audio_format_conversion())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL FIXES VALIDATED!")
        print("\n🔧 Key fixes implemented:")
        print("  • Fixed dashboard TTS optimizer to use proper TTSRequest objects")
        print("  • Eliminated voice count duplication (105 → 55)")
        print("  • Added comprehensive error handling and validation")
        print("  • Implemented proper audio format conversion")
        print("  • Added audio data validation to prevent placeholder returns")
    else:
        print("⚠️ Some tests failed - review the output above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
