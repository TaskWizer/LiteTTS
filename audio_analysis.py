#!/usr/bin/env python3
"""
Audio Analysis Script for LiteTTS Testing
Analyzes generated audio files for corruption detection
"""

import wave
import numpy as np
import os
import sys
from pathlib import Path

def analyze_audio_file(filepath):
    """Analyze a WAV file for basic properties and potential corruption"""
    try:
        with wave.open(str(filepath), 'rb') as wav_file:
            # Get basic properties
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            duration = frames / sample_rate
            
            # Read audio data
            audio_data = wav_file.readframes(frames)
            
            # Convert to numpy array for analysis
            if sample_width == 1:
                dtype = np.uint8
            elif sample_width == 2:
                dtype = np.int16
            elif sample_width == 4:
                dtype = np.int32
            else:
                dtype = np.float32
                
            audio_array = np.frombuffer(audio_data, dtype=dtype)
            
            # Basic corruption detection
            corruption_indicators = []
            
            # Check for silence (all zeros or very low amplitude)
            max_amplitude = np.max(np.abs(audio_array))
            if max_amplitude < 100:  # Very low amplitude threshold
                corruption_indicators.append("Very low amplitude (possible silence)")
            
            # Check for clipping (maximum values)
            if dtype == np.int16:
                max_val = 32767
                if np.any(np.abs(audio_array) >= max_val * 0.99):
                    corruption_indicators.append("Possible clipping detected")
            
            # Check for unusual patterns
            zero_count = np.count_nonzero(audio_array == 0)
            zero_percentage = (zero_count / len(audio_array)) * 100
            if zero_percentage > 50:
                corruption_indicators.append(f"High percentage of zeros: {zero_percentage:.1f}%")
            
            # Check for repeated patterns (simple check)
            if len(audio_array) > 1000:
                chunk_size = 100
                first_chunk = audio_array[:chunk_size]
                repeated_chunks = 0
                for i in range(chunk_size, len(audio_array) - chunk_size, chunk_size):
                    chunk = audio_array[i:i+chunk_size]
                    if np.array_equal(first_chunk, chunk):
                        repeated_chunks += 1
                
                if repeated_chunks > len(audio_array) // (chunk_size * 4):
                    corruption_indicators.append("Possible repeated pattern detected")
            
            return {
                'filepath': filepath,
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': channels,
                'sample_width': sample_width,
                'frames': frames,
                'max_amplitude': max_amplitude,
                'zero_percentage': zero_percentage,
                'corruption_indicators': corruption_indicators,
                'file_size': os.path.getsize(filepath),
                'analysis_status': 'SUCCESS'
            }
            
    except Exception as e:
        return {
            'filepath': filepath,
            'analysis_status': 'ERROR',
            'error': str(e)
        }

def main():
    """Analyze all test audio files"""
    test_files = [
        'test1_hello_af_heart.wav',
        'test2_fox_am_puck.wav', 
        'test3_numbers_af_nova.wav'
    ]
    
    expected_texts = [
        'Hello world',
        'The quick brown fox jumps over the lazy dog',
        'Testing one two three four five'
    ]
    
    print("=" * 80)
    print("LITETTS AUDIO CORRUPTION ANALYSIS")
    print("=" * 80)
    print()
    
    all_results = []
    
    for i, (filename, expected_text) in enumerate(zip(test_files, expected_texts), 1):
        print(f"TEST {i}: {filename}")
        print(f"Expected Text: '{expected_text}'")
        print("-" * 60)
        
        if not os.path.exists(filename):
            print(f"❌ ERROR: File {filename} not found!")
            print()
            continue
            
        result = analyze_audio_file(filename)
        all_results.append(result)
        
        if result['analysis_status'] == 'ERROR':
            print(f"❌ ERROR: {result['error']}")
        else:
            print(f"✅ File Size: {result['file_size']:,} bytes")
            print(f"✅ Duration: {result['duration']:.2f} seconds")
            print(f"✅ Sample Rate: {result['sample_rate']} Hz")
            print(f"✅ Channels: {result['channels']}")
            print(f"✅ Sample Width: {result['sample_width']} bytes")
            print(f"✅ Max Amplitude: {result['max_amplitude']}")
            print(f"✅ Zero Percentage: {result['zero_percentage']:.1f}%")
            
            if result['corruption_indicators']:
                print("⚠️  CORRUPTION INDICATORS:")
                for indicator in result['corruption_indicators']:
                    print(f"   - {indicator}")
            else:
                print("✅ No obvious corruption indicators detected")
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    successful_analyses = [r for r in all_results if r['analysis_status'] == 'SUCCESS']
    
    if successful_analyses:
        total_duration = sum(r['duration'] for r in successful_analyses)
        avg_sample_rate = sum(r['sample_rate'] for r in successful_analyses) / len(successful_analyses)
        total_corruption_indicators = sum(len(r['corruption_indicators']) for r in successful_analyses)
        
        print(f"✅ Successfully analyzed {len(successful_analyses)}/{len(test_files)} files")
        print(f"✅ Total audio duration: {total_duration:.2f} seconds")
        print(f"✅ Average sample rate: {avg_sample_rate:.0f} Hz")
        print(f"⚠️  Total corruption indicators: {total_corruption_indicators}")
        
        if total_corruption_indicators == 0:
            print("🎉 NO CORRUPTION DETECTED - Audio generation appears to be working correctly!")
        else:
            print("❌ CORRUPTION DETECTED - Audio generation has issues that need investigation")
    else:
        print("❌ No files could be analyzed successfully")
    
    print()
    print("FILE PATHS FOR MANUAL INSPECTION:")
    for filename in test_files:
        if os.path.exists(filename):
            full_path = os.path.abspath(filename)
            print(f"  {full_path}")
    
    return len(successful_analyses), total_corruption_indicators if successful_analyses else -1

if __name__ == "__main__":
    success_count, corruption_count = main()
    sys.exit(0 if corruption_count == 0 else 1)
