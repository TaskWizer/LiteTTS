#!/usr/bin/env python3
"""
Audio Pipeline Diagnosis Script
Systematically tests each stage of the TTS pipeline to identify corruption source
"""

import sys
import time
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_audio_generation():
    """Test basic audio generation using the current pipeline"""
    try:
        logger.info("🧪 Testing basic audio generation...")
        
        # Test phrases
        test_phrases = [
            "Hello world",
            "The quick brown fox jumps over the lazy dog",
            "Testing one two three"
        ]
        
        # Import TTS components
        from LiteTTS.tts.synthesizer import TTSSynthesizer
        from LiteTTS.models import TTSConfiguration, TTSRequest
        from LiteTTS.config import config
        
        # Initialize synthesizer
        tts_config = TTSConfiguration(
            model_path="LiteTTS/models/model_q4.onnx",
            voices_path="LiteTTS/voices",
            device="cpu",
            sample_rate=24000
        )
        
        synthesizer = TTSSynthesizer(tts_config)
        logger.info("✅ TTS Synthesizer initialized")
        
        results = {}
        
        for i, phrase in enumerate(test_phrases):
            logger.info(f"🔊 Generating audio for: '{phrase}'")
            
            try:
                # Create TTS request
                request = TTSRequest(
                    input=phrase,
                    voice="af_heart",
                    speed=1.0
                )
                
                # Generate audio
                start_time = time.time()
                audio_segment = synthesizer.synthesize(request)
                generation_time = time.time() - start_time
                
                # Save audio file for inspection
                output_file = f"test_audio_output/diagnosis_test_{i+1}.wav"
                Path("test_audio_output").mkdir(exist_ok=True)
                
                # Convert to WAV bytes and save
                audio_bytes = audio_segment.to_wav_bytes()
                with open(output_file, 'wb') as f:
                    f.write(audio_bytes)
                
                # Calculate RTF
                rtf = generation_time / audio_segment.duration if audio_segment.duration > 0 else float('inf')
                
                results[phrase] = {
                    'success': True,
                    'duration': audio_segment.duration,
                    'generation_time': generation_time,
                    'rtf': rtf,
                    'output_file': output_file,
                    'sample_rate': audio_segment.sample_rate,
                    'audio_shape': audio_segment.audio_data.shape,
                    'audio_dtype': str(audio_segment.audio_data.dtype),
                    'audio_range': [float(np.min(audio_segment.audio_data)), float(np.max(audio_segment.audio_data))]
                }
                
                logger.info(f"✅ Generated {audio_segment.duration:.2f}s audio in {generation_time:.2f}s (RTF: {rtf:.3f})")
                logger.info(f"📁 Saved to: {output_file}")
                
            except Exception as e:
                logger.error(f"❌ Failed to generate audio for '{phrase}': {e}")
                results[phrase] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Basic audio generation test failed: {e}")
        return None

def test_direct_kokoro_onnx():
    """Test audio generation using direct kokoro_onnx library"""
    try:
        logger.info("🧪 Testing direct kokoro_onnx audio generation...")
        
        # Apply patches first
        from LiteTTS.patches import apply_all_patches
        apply_all_patches()
        
        import kokoro_onnx
        
        # Initialize model
        model_path = "LiteTTS/models/model_q4.onnx"
        voices_path = "LiteTTS/voices/combined_voices.npz"

        logger.info(f"Loading kokoro_onnx model: {model_path}")
        logger.info(f"Loading kokoro_onnx voices: {voices_path}")
        kokoro = kokoro_onnx.Kokoro(model_path, voices_path)
        
        test_phrases = [
            "Hello world",
            "The quick brown fox jumps over the lazy dog",
            "Testing one two three"
        ]
        
        results = {}
        
        for i, phrase in enumerate(test_phrases):
            logger.info(f"🔊 Direct kokoro_onnx generation for: '{phrase}'")
            
            try:
                start_time = time.time()
                audio, sample_rate = kokoro.create(phrase, voice="af_heart", speed=1.0)
                generation_time = time.time() - start_time
                
                # Save audio file
                output_file = f"test_audio_output/direct_kokoro_{i+1}.wav"
                Path("test_audio_output").mkdir(exist_ok=True)
                
                # Convert to WAV and save
                import scipy.io.wavfile as wavfile
                # Ensure audio is in correct format for WAV
                if audio.dtype != np.int16:
                    audio_int16 = (audio * 32767).astype(np.int16)
                else:
                    audio_int16 = audio
                
                wavfile.write(output_file, sample_rate, audio_int16)
                
                # Calculate metrics
                duration = len(audio) / sample_rate
                rtf = generation_time / duration if duration > 0 else float('inf')
                
                results[phrase] = {
                    'success': True,
                    'duration': duration,
                    'generation_time': generation_time,
                    'rtf': rtf,
                    'output_file': output_file,
                    'sample_rate': sample_rate,
                    'audio_shape': audio.shape,
                    'audio_dtype': str(audio.dtype),
                    'audio_range': [float(np.min(audio)), float(np.max(audio))]
                }
                
                logger.info(f"✅ Direct generation: {duration:.2f}s audio in {generation_time:.2f}s (RTF: {rtf:.3f})")
                logger.info(f"📁 Saved to: {output_file}")
                
            except Exception as e:
                logger.error(f"❌ Direct kokoro_onnx failed for '{phrase}': {e}")
                results[phrase] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Direct kokoro_onnx test failed: {e}")
        return None

def test_text_processing_pipeline():
    """Test the text processing pipeline separately"""
    try:
        logger.info("🧪 Testing text processing pipeline...")
        
        from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode
        
        processor = UnifiedTextProcessor()
        
        test_phrases = [
            "Hello world",
            "The quick brown fox jumps over the lazy dog", 
            "Testing one two three"
        ]
        
        results = {}
        
        for phrase in test_phrases:
            logger.info(f"📝 Processing text: '{phrase}'")
            
            try:
                # Test different processing modes
                options = ProcessingOptions(
                    mode=ProcessingMode.ENHANCED,
                    use_pronunciation_rules=True,
                    use_advanced_symbols=True,
                    use_natural_pauses=True
                )
                
                processed_text = processor.process_text(phrase, options)
                
                results[phrase] = {
                    'success': True,
                    'original': phrase,
                    'processed': processed_text,
                    'length_change': len(processed_text) - len(phrase)
                }
                
                logger.info(f"✅ '{phrase}' -> '{processed_text}'")
                
            except Exception as e:
                logger.error(f"❌ Text processing failed for '{phrase}': {e}")
                results[phrase] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Text processing pipeline test failed: {e}")
        return None

def main():
    """Run comprehensive audio pipeline diagnosis"""
    logger.info("🚀 Starting Audio Pipeline Diagnosis...")
    logger.info("="*60)
    
    # Create output directory
    Path("test_audio_output").mkdir(exist_ok=True)
    
    # Test 1: Text Processing Pipeline
    logger.info("\n📝 PHASE 1: Text Processing Pipeline")
    logger.info("-" * 40)
    text_results = test_text_processing_pipeline()
    
    # Test 2: Direct kokoro_onnx Generation
    logger.info("\n🔊 PHASE 2: Direct kokoro_onnx Generation")
    logger.info("-" * 40)
    direct_results = test_direct_kokoro_onnx()
    
    # Test 3: LiteTTS Pipeline Generation
    logger.info("\n🎵 PHASE 3: LiteTTS Pipeline Generation")
    logger.info("-" * 40)
    pipeline_results = test_basic_audio_generation()
    
    # Summary Report
    logger.info("\n" + "="*60)
    logger.info("📊 DIAGNOSIS SUMMARY")
    logger.info("="*60)
    
    if text_results:
        logger.info("📝 Text Processing: ✅ WORKING")
        for phrase, result in text_results.items():
            if result['success']:
                logger.info(f"  '{phrase}' -> '{result['processed']}'")
    else:
        logger.error("📝 Text Processing: ❌ FAILED")
    
    if direct_results:
        logger.info("🔊 Direct kokoro_onnx: ✅ WORKING")
        for phrase, result in direct_results.items():
            if result['success']:
                logger.info(f"  '{phrase}': {result['duration']:.2f}s (RTF: {result['rtf']:.3f})")
    else:
        logger.error("🔊 Direct kokoro_onnx: ❌ FAILED")
    
    if pipeline_results:
        logger.info("🎵 LiteTTS Pipeline: ✅ WORKING")
        for phrase, result in pipeline_results.items():
            if result['success']:
                logger.info(f"  '{phrase}': {result['duration']:.2f}s (RTF: {result['rtf']:.3f})")
    else:
        logger.error("🎵 LiteTTS Pipeline: ❌ FAILED")
    
    # Check for audio files
    audio_files = list(Path("test_audio_output").glob("*.wav"))
    if audio_files:
        logger.info(f"\n📁 Generated {len(audio_files)} audio files in test_audio_output/")
        logger.info("💡 Listen to these files to check for audio quality issues")
        for file in sorted(audio_files):
            logger.info(f"  - {file.name}")
    else:
        logger.warning("⚠️ No audio files generated")
    
    return text_results, direct_results, pipeline_results

if __name__ == "__main__":
    main()
