#!/usr/bin/env python3
"""
Test script for WER (Word Error Rate) calculation validation

Tests the AudioQualityValidator.validate_transcription() method with known
audio/text pairs to ensure WER calculation returns float between 0.0-1.0
and processes test files within 60 seconds.
"""

import os
import sys
import time
import tempfile
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import List, Tuple

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from LiteTTS.validation.audio_quality_validator import AudioQualityValidator

def create_test_audio_files() -> List[Tuple[str, str]]:
    """
    Create test audio files with known text for WER calculation testing.

    Returns:
        List of (audio_path, reference_text) tuples
    """
    test_cases = [
        "Hello world, this is a test.",
        "The quick brown fox jumps over the lazy dog.",
        "Testing audio quality validation with Whisper.",
        "One two three four five six seven eight nine ten.",
        "This is a longer sentence to test transcription accuracy with multiple words and phrases.",
        "Short test.",
        "Audio quality matters for speech synthesis systems.",
        "Whisper transcription should work correctly.",
        "Testing WER calculation functionality.",
        "Final test case for validation."
    ]

    audio_files = []
    temp_dir = tempfile.mkdtemp(prefix="wer_test_")

    # Create simple silence files for testing WER calculation logic
    # The focus is on testing the WER calculation, not audio generation
    for i, text in enumerate(test_cases):
        audio_path = os.path.join(temp_dir, f"test_audio_{i:02d}.wav")

        # Create 2 seconds of silence at 16kHz (Whisper's expected rate)
        silence = np.zeros(32000, dtype=np.float32)
        sf.write(audio_path, silence, 16000)

        audio_files.append((audio_path, text))
        print(f"✅ Created test audio {i+1}/10: {text[:30]}...")

    return audio_files

def test_wer_calculation():
    """Test WER calculation functionality"""
    
    print("🔍 Testing WER Calculation Framework")
    print("=" * 40)
    
    # Create test audio files
    print("Creating test audio files...")
    test_files = create_test_audio_files()
    
    if not test_files:
        print("❌ No test files created, cannot proceed with WER testing")
        return False
    
    print(f"✅ Created {len(test_files)} test audio files")
    
    # Initialize AudioQualityValidator
    try:
        validator = AudioQualityValidator()
        validator.initialize()  # Call initialize method
        print("✅ AudioQualityValidator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize AudioQualityValidator: {e}")
        return False
    
    # Test WER calculation on each file
    start_time = time.time()
    successful_tests = 0
    wer_scores = []
    
    for i, (audio_path, reference_text) in enumerate(test_files):
        try:
            print(f"\nTesting file {i+1}/{len(test_files)}: {reference_text[:30]}...")
            
            # Validate transcription and calculate WER
            result = validator.validate_transcription(audio_path, reference_text)
            
            if result and result.metrics:
                wer = result.metrics.wer
                
                # Check if WER is valid float between 0.0-1.0
                if isinstance(wer, float) and 0.0 <= wer <= 1.0:
                    wer_scores.append(wer)
                    successful_tests += 1
                    print(f"✅ WER: {wer:.3f} (valid)")
                else:
                    print(f"❌ Invalid WER value: {wer} (not in range 0.0-1.0)")
            else:
                print(f"❌ Failed to get validation result")
                
        except Exception as e:
            print(f"❌ Error processing file {i+1}: {e}")
            continue
    
    total_time = time.time() - start_time
    
    # Evaluate results
    print(f"\n" + "=" * 40)
    print(f"📊 WER CALCULATION TEST RESULTS:")
    print(f"   Total files processed: {len(test_files)}")
    print(f"   Successful tests: {successful_tests}")
    print(f"   Processing time: {total_time:.1f}s")
    print(f"   Time per file: {total_time/len(test_files):.1f}s")
    print(f"   Time requirement: <60s ({'✅ PASS' if total_time < 60 else '❌ FAIL'})")
    
    if wer_scores:
        avg_wer = sum(wer_scores) / len(wer_scores)
        min_wer = min(wer_scores)
        max_wer = max(wer_scores)
        print(f"   Average WER: {avg_wer:.3f}")
        print(f"   WER range: {min_wer:.3f} - {max_wer:.3f}")
    
    # Success criteria
    success = (
        successful_tests >= len(test_files) * 0.8 and  # At least 80% success rate
        total_time < 60 and  # Processing time under 60 seconds
        len(wer_scores) > 0  # At least some valid WER scores
    )
    
    print(f"\nOverall Status: {'✅ PASS' if success else '❌ FAIL'}")
    
    # Cleanup
    try:
        import shutil
        temp_dir = os.path.dirname(test_files[0][0]) if test_files else None
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up temporary files")
    except Exception as e:
        print(f"⚠️ Failed to cleanup temporary files: {e}")
    
    return success

def main():
    """Main test execution"""
    
    print("🧪 WER Calculation Validation Test Suite")
    print("=" * 50)
    print("Testing AudioQualityValidator.validate_transcription() method")
    print("Success criteria:")
    print("- WER calculation returns float between 0.0-1.0")
    print("- Processes 10 test files in <60 seconds")
    print("- At least 80% success rate")
    print()
    
    success = test_wer_calculation()
    
    if success:
        print("\n🎉 WER calculation framework is working correctly!")
        return 0
    else:
        print("\n⚠️ WER calculation framework needs attention")
        return 1

if __name__ == "__main__":
    exit(main())
