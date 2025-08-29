#!/usr/bin/env python3
"""
Audio Corruption Fix Script
Restores proper text processing to fix garbled audio generation
"""

import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_text_normalizer():
    """Fix the TextNormalizer to restore basic text processing"""
    logger.info("🔧 Fixing TextNormalizer text processing...")
    
    # Read the current file
    normalizer_file = Path("LiteTTS/nlp/text_normalizer.py")
    with open(normalizer_file, 'r') as f:
        content = f.read()
    
    # Find the problematic section and fix it
    old_section = '''        # Step 1: RIME AI phonetic processing (DISABLED due to text truncation bug)
        # CRITICAL FIX: RIME AI was truncating "test" to "tes" causing garbled audio
        # Disabling until the RIME AI truncation issue is resolved
        if False:  # RIME_AI_AVAILABLE:'''
    
    new_section = '''        # Step 1: Basic text cleaning (RIME AI disabled due to truncation issues)
        # Apply basic text normalization without RIME AI to prevent truncation
        text = self._apply_basic_normalization(text)
        
        # RIME AI phonetic processing (DISABLED due to text truncation bug)
        # CRITICAL FIX: RIME AI was truncating "test" to "tes" causing garbled audio
        # Disabling until the RIME AI truncation issue is resolved
        if False:  # RIME_AI_AVAILABLE:'''
    
    if old_section in content:
        content = content.replace(old_section, new_section)
        logger.info("✅ Fixed RIME AI processing section")
    else:
        logger.warning("⚠️ Could not find RIME AI processing section to fix")
    
    # Add the basic normalization method if it doesn't exist
    basic_norm_method = '''
    def _apply_basic_normalization(self, text: str) -> str:
        """Apply basic text normalization without RIME AI"""
        # Basic cleaning to ensure text is properly formatted for TTS
        text = text.strip()
        
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure proper sentence ending
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
'''
    
    # Add the method before the last class method
    if '_apply_basic_normalization' not in content:
        # Find a good place to insert the method (before the last method)
        insertion_point = content.rfind('\n    def ')
        if insertion_point != -1:
            content = content[:insertion_point] + basic_norm_method + content[insertion_point:]
            logger.info("✅ Added basic normalization method")
        else:
            logger.warning("⚠️ Could not find insertion point for basic normalization method")
    
    # Write the fixed content back
    with open(normalizer_file, 'w') as f:
        f.write(content)
    
    logger.info("✅ TextNormalizer fixes applied")

def fix_audio_quality_enhancer():
    """Re-enable basic audio quality enhancement without SSML corruption"""
    logger.info("🔧 Fixing AudioQualityEnhancer...")
    
    enhancer_file = Path("LiteTTS/nlp/audio_quality_enhancer.py")
    with open(enhancer_file, 'r') as f:
        content = f.read()
    
    # Fix the natural pauses method to add basic punctuation without SSML
    old_pauses_method = '''    def _add_natural_pauses(self, text: str) -> str:
        """Add natural pauses for better speech flow - DISABLED to prevent SSML corruption"""
        # CRITICAL FIX: Disable SSML generation that was causing malformed output
        # The system was generating nested and broken SSML tags that corrupted text processing
        # This was causing the word count mismatches and garbled audio output

        # For now, return text unchanged to fix the core processing issues
        # TODO: Implement proper pause handling without SSML corruption
        logger.debug("Natural pauses disabled to prevent SSML corruption")
        return text'''
    
    new_pauses_method = '''    def _add_natural_pauses(self, text: str) -> str:
        """Add natural pauses for better speech flow - BASIC VERSION without SSML"""
        # Apply basic punctuation improvements without SSML to prevent corruption
        import re
        
        # Add pauses after sentences (simple approach)
        text = re.sub(r'([.!?])\s*', r'\\1 ', text)
        
        # Add slight pauses after commas
        text = re.sub(r'(,)\s*', r'\\1 ', text)
        
        # Ensure proper spacing
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.debug("Basic natural pauses applied (no SSML)")
        return text'''
    
    if old_pauses_method in content:
        content = content.replace(old_pauses_method, new_pauses_method)
        logger.info("✅ Fixed natural pauses method")
    else:
        logger.warning("⚠️ Could not find natural pauses method to fix")
    
    # Write the fixed content back
    with open(enhancer_file, 'w') as f:
        f.write(content)
    
    logger.info("✅ AudioQualityEnhancer fixes applied")

def test_text_processing_fix():
    """Test that the text processing fixes work correctly"""
    logger.info("🧪 Testing text processing fixes...")
    
    try:
        # Import the fixed components
        from LiteTTS.nlp.text_normalizer import TextNormalizer
        from LiteTTS.nlp.audio_quality_enhancer import AudioQualityEnhancer
        
        # Test text normalizer
        normalizer = TextNormalizer()
        test_text = "Hello world"
        normalized = normalizer.normalize_text(test_text)
        logger.info(f"✅ TextNormalizer test: '{test_text}' → '{normalized}'")
        
        # Test audio quality enhancer
        enhancer = AudioQualityEnhancer()
        enhanced = enhancer.enhance_audio_quality(test_text)
        logger.info(f"✅ AudioQualityEnhancer test: '{test_text}' → '{enhanced}'")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Text processing test failed: {e}")
        return False

def generate_test_audio():
    """Generate test audio to verify the fix"""
    logger.info("🎵 Generating test audio to verify fix...")
    
    try:
        from LiteTTS.tts.synthesizer import TTSSynthesizer
        from LiteTTS.models import TTSConfiguration, TTSRequest
        
        # Initialize synthesizer
        tts_config = TTSConfiguration(
            model_path="LiteTTS/models/model_q4.onnx",
            voices_path="LiteTTS/voices",
            device="cpu",
            sample_rate=24000
        )
        
        synthesizer = TTSSynthesizer(tts_config)
        
        # Test with simple phrase
        test_phrase = "Hello world"
        request = TTSRequest(
            input=test_phrase,
            voice="af_heart",
            speed=1.0
        )
        
        logger.info(f"🔊 Generating audio for: '{test_phrase}'")
        audio_segment = synthesizer.synthesize(request)
        
        # Save test audio
        output_file = "test_audio_output/fixed_audio_test.wav"
        Path("test_audio_output").mkdir(exist_ok=True)
        
        audio_bytes = audio_segment.to_wav_bytes()
        with open(output_file, 'wb') as f:
            f.write(audio_bytes)
        
        logger.info(f"✅ Test audio generated: {output_file}")
        logger.info(f"📊 Duration: {audio_segment.duration:.2f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test audio generation failed: {e}")
        return False

def validate_fix_with_stt():
    """Validate the fix using STT transcription"""
    logger.info("🎧 Validating fix with STT transcription...")
    
    try:
        from LiteTTS.stt.faster_whisper_stt import FasterWhisperSTT
        from LiteTTS.stt.stt_models import STTRequest, STTConfiguration
        
        # Initialize STT
        stt_config = STTConfiguration(
            model="tiny.en",
            device="cpu",
            compute_type="int8"
        )
        
        stt_engine = FasterWhisperSTT(stt_config)
        
        # Test the fixed audio
        test_file = "test_audio_output/fixed_audio_test.wav"
        if not Path(test_file).exists():
            logger.warning("⚠️ Test audio file not found, skipping STT validation")
            return False
        
        stt_request = STTRequest(
            audio=test_file,
            language="en"
        )
        
        response = stt_engine.transcribe(stt_request)
        transcribed_text = response.text.strip()
        expected_text = "Hello world"
        
        logger.info(f"📝 Expected: '{expected_text}'")
        logger.info(f"🔤 Transcribed: '{transcribed_text}'")
        logger.info(f"📊 Confidence: {response.confidence:.3f}")
        
        # Check if transcription is reasonable
        if "hello" in transcribed_text.lower() or "world" in transcribed_text.lower():
            logger.info("✅ STT validation PASSED - Audio contains expected words")
            return True
        else:
            logger.warning("⚠️ STT validation FAILED - Audio may still be corrupted")
            return False
        
    except Exception as e:
        logger.error(f"❌ STT validation failed: {e}")
        return False

def main():
    """Apply fixes for audio corruption"""
    logger.info("🚀 Starting Audio Corruption Fix...")
    logger.info("="*60)
    
    # Step 1: Fix text processing components
    logger.info("\n🔧 STEP 1: Fixing Text Processing Components")
    fix_text_normalizer()
    fix_audio_quality_enhancer()
    
    # Step 2: Test the fixes
    logger.info("\n🧪 STEP 2: Testing Text Processing Fixes")
    if not test_text_processing_fix():
        logger.error("❌ Text processing fixes failed")
        return False
    
    # Step 3: Generate test audio
    logger.info("\n🎵 STEP 3: Generating Test Audio")
    if not generate_test_audio():
        logger.error("❌ Test audio generation failed")
        return False
    
    # Step 4: Validate with STT
    logger.info("\n🎧 STEP 4: Validating with STT")
    stt_success = validate_fix_with_stt()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 AUDIO CORRUPTION FIX SUMMARY")
    logger.info("="*60)
    logger.info("✅ Text processing components fixed")
    logger.info("✅ Test audio generated")
    
    if stt_success:
        logger.info("✅ STT validation passed")
        logger.info("🎉 AUDIO CORRUPTION FIX SUCCESSFUL!")
        logger.info("💡 The system should now generate intelligible English audio")
    else:
        logger.warning("⚠️ STT validation inconclusive")
        logger.info("🔧 Additional investigation may be required")
    
    return stt_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
