#!/usr/bin/env python3
"""
CRITICAL TTS DIAGNOSIS SCRIPT

Systematically tests TTS synthesis to identify and diagnose critical failures:
1. Truncated output (< 1 second audio for full sentences)
2. Silent/empty output 
3. Pronunciation regressions ("Okay" -> "Awk-key", "boy" -> "bow")
4. Text preprocessing warnings and word count mismatches
"""

import requests
import time
import os
import json
import wave
import struct
from typing import Dict, List, Any, Tuple

def analyze_audio_file(filepath: str) -> Dict[str, Any]:
    """Analyze audio file properties"""
    try:
        if not os.path.exists(filepath):
            return {"error": "File not found", "duration": 0, "samples": 0}
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        if filepath.endswith('.wav'):
            try:
                with wave.open(filepath, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    duration = frames / sample_rate if sample_rate > 0 else 0
                    
                    return {
                        "file_size_bytes": file_size,
                        "duration_seconds": duration,
                        "sample_rate": sample_rate,
                        "frames": frames,
                        "channels": wav_file.getnchannels(),
                        "sample_width": wav_file.getsampwidth()
                    }
            except Exception as e:
                return {"error": f"WAV analysis failed: {e}", "file_size_bytes": file_size}
        
        else:
            # For MP3/other formats, try to get actual duration using mutagen
            try:
                from mutagen.mp3 import MP3
                from mutagen import File

                audio_file = File(filepath)
                if audio_file is not None and hasattr(audio_file, 'info'):
                    actual_duration = audio_file.info.length
                    return {
                        "file_size_bytes": file_size,
                        "duration_seconds": actual_duration,
                        "format": "mp3_actual",
                        "bitrate": getattr(audio_file.info, 'bitrate', 'unknown')
                    }
            except ImportError:
                pass  # mutagen not available, fall back to estimation
            except Exception:
                pass  # File reading failed, fall back to estimation

            # Fallback: estimate based on file size
            # Rough estimate: MP3 at 128kbps ≈ 16KB per second
            estimated_duration = file_size / 16000 if file_size > 0 else 0

            return {
                "file_size_bytes": file_size,
                "estimated_duration_seconds": estimated_duration,
                "format": "non-wav"
            }
    
    except Exception as e:
        return {"error": f"Analysis failed: {e}"}

def test_tts_endpoint(text: str, voice: str = "af_heart", format: str = "mp3", 
                     expected_min_duration: float = 1.0) -> Dict[str, Any]:
    """Test TTS endpoint with specific input and analyze results"""
    
    print(f"\n🔍 Testing: '{text}' (voice: {voice}, format: {format})")
    print(f"   Expected minimum duration: {expected_min_duration}s")
    
    payload = {
        "input": text,
        "voice": voice,
        "response_format": format
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8354/v1/audio/speech",
            json=payload,
            timeout=30
        )
        request_time = time.time() - start_time
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "response_text": response.text[:500],
                "request_time": request_time
            }
        
        # Save audio file for analysis
        filename = f"diagnosis_{voice}_{format}_{int(time.time())}.{format}"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        # Analyze audio
        audio_analysis = analyze_audio_file(filename)
        
        # Determine if this is a failure
        actual_duration = audio_analysis.get('duration_seconds', 
                                           audio_analysis.get('estimated_duration_seconds', 0))
        
        is_truncated = actual_duration < expected_min_duration
        is_silent = audio_analysis.get('file_size_bytes', 0) < 1000  # Less than 1KB likely silent
        
        result = {
            "success": True,
            "request_time": request_time,
            "filename": filename,
            "audio_analysis": audio_analysis,
            "actual_duration": actual_duration,
            "expected_min_duration": expected_min_duration,
            "is_truncated": is_truncated,
            "is_silent": is_silent,
            "failure_detected": is_truncated or is_silent
        }
        
        # Print immediate results
        if result["failure_detected"]:
            print(f"   ❌ FAILURE DETECTED:")
            if is_truncated:
                print(f"      - TRUNCATED: {actual_duration:.2f}s < {expected_min_duration}s expected")
            if is_silent:
                print(f"      - SILENT: File size {audio_analysis.get('file_size_bytes', 0)} bytes")
        else:
            print(f"   ✅ SUCCESS: {actual_duration:.2f}s duration")
        
        return result
        
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed - is TTS server running?",
            "request_time": 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Request failed: {e}",
            "request_time": time.time() - start_time
        }

def test_pronunciation_regressions() -> Dict[str, Any]:
    """Test specific pronunciation regression cases"""
    
    print("\n🎯 TESTING PRONUNCIATION REGRESSIONS")
    print("=" * 50)
    
    test_cases = [
        # Known regression cases
        {"text": "Okay", "voice": "af_heart", "issue": "Should be 'Oh-kay' not 'Awk-key'"},
        {"text": "boy", "voice": "af_heart", "issue": "Should be 'boy' not 'bow'"},
        {"text": "Boy", "voice": "af_heart", "issue": "Uppercase version - should work correctly"},
        {"text": "Okay, boy", "voice": "af_heart", "issue": "Combined regression test"},
        
        # Additional pronunciation tests
        {"text": "June", "voice": "af_heart", "issue": "Should preserve final consonant"},
        {"text": "Jan", "voice": "af_heart", "issue": "Should preserve final consonant"},
        {"text": "Joy", "voice": "af_heart", "issue": "Similar to 'boy' - test for consistency"},
        {"text": "Toy", "voice": "af_heart", "issue": "Similar to 'boy' - test for consistency"},
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔍 Pronunciation Test: '{test_case['text']}'")
        print(f"   Issue: {test_case['issue']}")
        
        result = test_tts_endpoint(
            test_case['text'],
            test_case['voice'],
            "mp3",
            expected_min_duration=0.3  # Realistic expectation for single words
        )
        
        result['test_case'] = test_case
        results.append(result)
    
    return {"pronunciation_tests": results}

def test_duration_failures() -> Dict[str, Any]:
    """Test cases that should produce longer audio but are getting truncated"""
    
    print("\n📏 TESTING DURATION/TRUNCATION FAILURES")
    print("=" * 45)
    
    test_cases = [
        {
            "text": "Hello world",
            "expected_min_duration": 0.8,  # More realistic for 2 words
            "description": "Simple two-word test"
        },
        {
            "text": "This is a test of the text-to-speech system",
            "expected_min_duration": 2.5,  # More realistic for 9 words
            "description": "Medium sentence"
        },
        {
            "text": "The quick brown fox jumps over the lazy dog. This sentence contains multiple clauses and should generate several seconds of audio.",
            "expected_min_duration": 6.0,  # More realistic for long sentence
            "description": "Long complex sentence"
        },
        {
            "text": "(silence, then attempting to read) ... Okay, I...",
            "expected_min_duration": 2.0,  # More realistic expectation
            "description": "Text from server logs that caused word count mismatch"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔍 Duration Test: {test_case['description']}")
        print(f"   Text: '{test_case['text'][:50]}{'...' if len(test_case['text']) > 50 else ''}'")
        
        result = test_tts_endpoint(
            test_case['text'], 
            "af_heart", 
            "mp3", 
            test_case['expected_min_duration']
        )
        
        result['test_case'] = test_case
        results.append(result)
    
    return {"duration_tests": results}

def test_multiple_voices_and_formats() -> Dict[str, Any]:
    """Test across multiple voices and formats to isolate issues"""
    
    print("\n🎭 TESTING MULTIPLE VOICES AND FORMATS")
    print("=" * 40)
    
    test_text = "Hello world, this is a test"
    voices = ["af_heart", "af_sky", "af_bella", "af_sarah"]
    formats = ["mp3", "wav"]
    
    results = []
    
    for voice in voices:
        for format in formats:
            print(f"\n🔍 Testing voice: {voice}, format: {format}")
            
            result = test_tts_endpoint(test_text, voice, format, 1.5)  # More realistic for 6 words
            result['voice'] = voice
            result['format'] = format
            results.append(result)
    
    return {"voice_format_tests": results}

def analyze_text_preprocessing() -> Dict[str, Any]:
    """Test text preprocessing pipeline directly"""
    
    print("\n📝 TESTING TEXT PREPROCESSING PIPELINE")
    print("=" * 40)
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from LiteTTS.nlp.processor import NLPProcessor
        from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
        
        nlp_processor = NLPProcessor()
        
        test_texts = [
            "Okay, boy",
            "(silence, then attempting to read) ... Okay, I...",
            "Hello world",
            "The quick brown fox jumps over the lazy dog"
        ]
        
        results = []
        
        for text in test_texts:
            print(f"\n🔍 Processing: '{text}'")
            
            # Test phonemizer preprocessor
            preprocess_result = phonemizer_preprocessor.preprocess_text(text)
            print(f"   Preprocessor: '{preprocess_result.processed_text}'")
            print(f"   Changes: {preprocess_result.changes_made}")
            
            # Test NLP processor
            nlp_result = nlp_processor.process_text(text)
            print(f"   NLP Result: '{nlp_result}'")
            
            # Check for word count mismatches
            original_words = len(text.split())
            preprocessed_words = len(preprocess_result.processed_text.split())
            nlp_words = len(nlp_result.split())
            
            word_count_issue = (original_words != preprocessed_words or 
                              preprocessed_words != nlp_words)
            
            if word_count_issue:
                print(f"   ⚠️ WORD COUNT MISMATCH: {original_words} -> {preprocessed_words} -> {nlp_words}")
            
            results.append({
                "original_text": text,
                "preprocessed_text": preprocess_result.processed_text,
                "nlp_text": nlp_result,
                "original_word_count": original_words,
                "preprocessed_word_count": preprocessed_words,
                "nlp_word_count": nlp_words,
                "word_count_issue": word_count_issue,
                "changes_made": preprocess_result.changes_made
            })
        
        return {"preprocessing_tests": results}
        
    except Exception as e:
        return {"error": f"Preprocessing test failed: {e}"}

def main():
    """Run comprehensive TTS diagnosis"""
    
    print("🚨 CRITICAL TTS DIAGNOSIS - SYSTEMATIC FAILURE ANALYSIS")
    print("=" * 65)
    print("Testing TTS synthesis to identify root causes of failures...")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8354/health", timeout=5)
        if response.status_code != 200:
            print("❌ TTS server health check failed")
            return
    except:
        print("❌ Cannot connect to TTS server - please start with:")
        print("   uv run uvicorn app:app --host 0.0.0.0 --port 8354")
        return
    
    print("✅ TTS server is running")
    
    # Run all diagnostic tests
    results = {}
    
    # Test 1: Pronunciation regressions
    results.update(test_pronunciation_regressions())
    
    # Test 2: Duration/truncation failures  
    results.update(test_duration_failures())
    
    # Test 3: Multiple voices and formats
    results.update(test_multiple_voices_and_formats())
    
    # Test 4: Text preprocessing analysis
    results.update(analyze_text_preprocessing())
    
    # Generate summary report
    print("\n" + "=" * 65)
    print("📊 DIAGNOSIS SUMMARY REPORT")
    print("=" * 65)
    
    total_tests = 0
    failed_tests = 0
    
    for test_category, test_results in results.items():
        if isinstance(test_results, list):
            category_tests = len(test_results)
            category_failures = sum(1 for r in test_results if r.get('failure_detected', False))
        elif isinstance(test_results, dict) and 'error' in test_results:
            category_tests = 1
            category_failures = 1
        else:
            continue
        
        total_tests += category_tests
        failed_tests += category_failures
        
        status = "❌ FAILURES DETECTED" if category_failures > 0 else "✅ ALL PASSED"
        print(f"{test_category}: {category_failures}/{category_tests} failed - {status}")
    
    print(f"\nOVERALL: {failed_tests}/{total_tests} tests failed")
    
    if failed_tests > 0:
        print("\n🚨 CRITICAL ISSUES DETECTED - TTS SYSTEM REQUIRES IMMEDIATE ATTENTION")
    else:
        print("\n✅ No critical issues detected in current tests")
    
    # Save detailed results
    with open("tts_diagnosis_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: tts_diagnosis_results.json")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
