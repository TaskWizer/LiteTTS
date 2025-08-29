#!/usr/bin/env python3
"""
Audio Quality Validation System
Uses faster-whisper STT to validate that generated audio is intelligible English
"""

import sys
import time
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_wer(reference: str, hypothesis: str) -> float:
    """Calculate Word Error Rate (WER) between reference and hypothesis"""
    ref_words = reference.lower().split()
    hyp_words = hypothesis.lower().split()
    
    # Simple WER calculation using edit distance
    def edit_distance(s1, s2):
        if len(s1) < len(s2):
            return edit_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    if len(ref_words) == 0:
        return 1.0 if len(hyp_words) > 0 else 0.0
    
    distance = edit_distance(ref_words, hyp_words)
    return distance / len(ref_words)

def test_audio_transcription_quality():
    """Test audio quality by transcribing generated files with faster-whisper"""
    try:
        logger.info("🧪 Testing audio transcription quality with faster-whisper...")
        
        # Import STT components
        from LiteTTS.stt.faster_whisper_stt import FasterWhisperSTT
        from LiteTTS.stt.stt_models import STTRequest, STTConfiguration
        
        # Initialize STT with small model for speed
        stt_config = STTConfiguration(
            model="tiny.en",  # Fast English model
            device="cpu",
            compute_type="int8"
        )
        
        stt_engine = FasterWhisperSTT(stt_config)
        logger.info("✅ Faster-whisper STT initialized")
        
        # Test phrases and their expected transcriptions
        test_cases = [
            {
                'file': 'test_audio_output/diagnosis_test_1.wav',
                'expected': 'Hello world',
                'description': 'Simple greeting'
            },
            {
                'file': 'test_audio_output/diagnosis_test_2.wav', 
                'expected': 'The quick brown fox jumps over the lazy dog',
                'description': 'Pangram sentence'
            },
            {
                'file': 'test_audio_output/diagnosis_test_3.wav',
                'expected': 'Testing one two three',
                'description': 'Number sequence'
            }
        ]
        
        results = {}
        total_wer = 0.0
        successful_transcriptions = 0
        
        for test_case in test_cases:
            file_path = test_case['file']
            expected_text = test_case['expected']
            description = test_case['description']
            
            logger.info(f"🎧 Transcribing: {file_path}")
            logger.info(f"📝 Expected: '{expected_text}'")
            
            if not Path(file_path).exists():
                logger.warning(f"⚠️ Audio file not found: {file_path}")
                results[file_path] = {
                    'success': False,
                    'error': 'File not found'
                }
                continue
            
            try:
                # Create STT request
                stt_request = STTRequest(
                    audio=file_path,
                    language="en"
                )
                
                # Transcribe audio
                start_time = time.time()
                stt_response = stt_engine.transcribe(stt_request)
                transcription_time = time.time() - start_time
                
                transcribed_text = stt_response.text.strip()
                confidence = stt_response.confidence
                
                # Calculate WER
                wer = calculate_wer(expected_text, transcribed_text)
                accuracy = max(0.0, 1.0 - wer) * 100
                
                # Determine if transcription is acceptable
                is_acceptable = accuracy >= 80.0  # 80% accuracy threshold
                
                results[file_path] = {
                    'success': True,
                    'expected': expected_text,
                    'transcribed': transcribed_text,
                    'confidence': confidence,
                    'wer': wer,
                    'accuracy': accuracy,
                    'transcription_time': transcription_time,
                    'is_acceptable': is_acceptable,
                    'description': description
                }
                
                total_wer += wer
                successful_transcriptions += 1
                
                # Log results
                status = "✅ PASS" if is_acceptable else "❌ FAIL"
                logger.info(f"🔤 Transcribed: '{transcribed_text}'")
                logger.info(f"📊 Accuracy: {accuracy:.1f}% | WER: {wer:.3f} | Confidence: {confidence:.3f}")
                logger.info(f"⏱️ Transcription time: {transcription_time:.2f}s")
                logger.info(f"🎯 Result: {status}")
                
            except Exception as e:
                logger.error(f"❌ Transcription failed for {file_path}: {e}")
                results[file_path] = {
                    'success': False,
                    'error': str(e),
                    'expected': expected_text,
                    'description': description
                }
        
        # Calculate overall metrics
        if successful_transcriptions > 0:
            average_wer = total_wer / successful_transcriptions
            average_accuracy = max(0.0, 1.0 - average_wer) * 100
            
            # Determine overall system quality
            system_acceptable = average_accuracy >= 80.0
            
            results['_summary'] = {
                'total_tests': len(test_cases),
                'successful_transcriptions': successful_transcriptions,
                'average_wer': average_wer,
                'average_accuracy': average_accuracy,
                'system_acceptable': system_acceptable,
                'threshold': 80.0
            }
            
            logger.info("\n" + "="*60)
            logger.info("📊 AUDIO QUALITY VALIDATION SUMMARY")
            logger.info("="*60)
            logger.info(f"Total Tests: {len(test_cases)}")
            logger.info(f"Successful Transcriptions: {successful_transcriptions}")
            logger.info(f"Average Accuracy: {average_accuracy:.1f}%")
            logger.info(f"Average WER: {average_wer:.3f}")
            logger.info(f"Quality Threshold: 80.0%")
            
            if system_acceptable:
                logger.info("🎉 SYSTEM QUALITY: ✅ ACCEPTABLE")
                logger.info("💡 Audio generation is producing intelligible English speech")
            else:
                logger.error("🚨 SYSTEM QUALITY: ❌ UNACCEPTABLE")
                logger.error("💡 Audio generation may be producing garbled or unintelligible speech")
                logger.error("🔧 Investigation required: Check model loading, voice selection, or processing pipeline")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Audio quality validation failed: {e}")
        return None

def analyze_transcription_patterns(results: Dict[str, Any]):
    """Analyze transcription patterns to identify specific issues"""
    logger.info("\n🔍 ANALYZING TRANSCRIPTION PATTERNS...")
    
    patterns = {
        'chinese_characters': 0,
        'gibberish_words': 0,
        'missing_words': 0,
        'extra_words': 0,
        'pronunciation_errors': 0
    }
    
    for file_path, result in results.items():
        if file_path.startswith('_') or not result.get('success'):
            continue
            
        expected = result.get('expected', '').lower()
        transcribed = result.get('transcribed', '').lower()
        
        # Check for Chinese characters or non-English patterns
        if any(ord(char) > 127 for char in transcribed):
            patterns['chinese_characters'] += 1
            logger.warning(f"⚠️ Non-ASCII characters detected in: {file_path}")
        
        # Check for completely different words (potential gibberish)
        expected_words = set(expected.split())
        transcribed_words = set(transcribed.split())
        
        if len(expected_words.intersection(transcribed_words)) == 0 and len(expected_words) > 0:
            patterns['gibberish_words'] += 1
            logger.warning(f"⚠️ No matching words detected in: {file_path}")
            logger.warning(f"   Expected: {expected}")
            logger.warning(f"   Got: {transcribed}")
    
    # Report pattern analysis
    logger.info("📋 Pattern Analysis Results:")
    for pattern, count in patterns.items():
        if count > 0:
            logger.warning(f"  {pattern.replace('_', ' ').title()}: {count} occurrences")
    
    if sum(patterns.values()) == 0:
        logger.info("  ✅ No concerning patterns detected")
    
    return patterns

def save_validation_report(results: Dict[str, Any], patterns: Dict[str, int]):
    """Save detailed validation report to file"""
    report_file = "audio_quality_validation_report.json"
    
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'validation_results': results,
        'pattern_analysis': patterns,
        'recommendations': []
    }
    
    # Add recommendations based on results
    if results and '_summary' in results:
        summary = results['_summary']
        if not summary['system_acceptable']:
            report['recommendations'].extend([
                "Audio quality below acceptable threshold (80%)",
                "Check model loading and voice file integrity",
                "Verify text processing pipeline is not corrupting input",
                "Test with different voices to isolate voice-specific issues",
                "Compare against known working baseline commit"
            ])
        else:
            report['recommendations'].append("Audio quality meets production standards")
    
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"📄 Validation report saved to: {report_file}")
    except Exception as e:
        logger.error(f"❌ Failed to save validation report: {e}")

def main():
    """Run comprehensive audio quality validation"""
    logger.info("🚀 Starting Audio Quality Validation System...")
    logger.info("="*60)
    
    # Test audio transcription quality
    results = test_audio_transcription_quality()
    
    if results:
        # Analyze transcription patterns
        patterns = analyze_transcription_patterns(results)
        
        # Save detailed report
        save_validation_report(results, patterns)
        
        # Final assessment
        if '_summary' in results:
            summary = results['_summary']
            if summary['system_acceptable']:
                logger.info("\n🎉 VALIDATION COMPLETE: Audio quality is ACCEPTABLE")
                logger.info("💡 The system is generating intelligible English speech")
                return True
            else:
                logger.error("\n🚨 VALIDATION COMPLETE: Audio quality is UNACCEPTABLE")
                logger.error("💡 The system may be generating garbled or unintelligible speech")
                return False
        else:
            logger.error("\n❌ VALIDATION INCOMPLETE: Unable to assess audio quality")
            return False
    else:
        logger.error("\n❌ VALIDATION FAILED: Could not test audio quality")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
