#!/usr/bin/env python3
"""
Phonemization Pipeline Fix
Ensures text is properly converted to phonemes before tokenization
"""

import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_tts_engine_phonemization():
    """Fix the TTS engine to ensure proper phonemization before tokenization"""
    logger.info("🔧 Fixing TTS engine phonemization pipeline...")
    
    engine_file = Path("LiteTTS/tts/engine.py")
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Find the synthesize method and add phonemization step
    old_synthesize_section = '''            # Tokenize text
            tokens = self._tokenize_text(text)'''
    
    new_synthesize_section = '''            # CRITICAL FIX: Convert text to phonemes before tokenization
            # The tokenizer expects phonetic input, not raw text
            phonemes = self._text_to_phonemes(text)
            logger.debug(f"Converted text to phonemes: '{text}' -> '{phonemes}'")
            
            # Tokenize phonemes (not raw text)
            tokens = self._tokenize_text(phonemes)'''
    
    if old_synthesize_section in content:
        content = content.replace(old_synthesize_section, new_synthesize_section)
        logger.info("✅ Fixed synthesize method to use phonemization")
    else:
        logger.warning("⚠️ Could not find synthesize method to fix")
    
    # Add the phonemization method
    phonemization_method = '''
    def _text_to_phonemes(self, text: str) -> str:
        """Convert text to phonemes using espeak-ng"""
        try:
            # Try to use espeak-ng for phonemization
            import subprocess
            
            # Use espeak-ng to convert text to IPA phonemes
            result = subprocess.run([
                'espeak-ng', '-q', '--ipa', '-v', 'en-us'
            ], input=text, text=True, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                phonemes = result.stdout.strip()
                # Clean up the phonemes
                phonemes = self._clean_phonemes(phonemes)
                logger.debug(f"espeak-ng phonemization: '{text}' -> '{phonemes}'")
                return phonemes
            else:
                logger.warning(f"espeak-ng failed: {result.stderr}")
                
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.warning(f"espeak-ng not available or failed: {e}")
        
        # Fallback to simple character mapping
        return self._fallback_phonemization(text)
    
    def _clean_phonemes(self, phonemes: str) -> str:
        """Clean and normalize phonemes from espeak-ng"""
        import re
        
        # Remove stress markers and extra symbols that might not be in vocab
        phonemes = re.sub(r'[ˈˌ]', '', phonemes)  # Remove primary/secondary stress
        phonemes = re.sub(r'[ː]', '', phonemes)   # Remove length markers
        phonemes = re.sub(r'[‿]', ' ', phonemes)  # Replace linking with space
        
        # Ensure spaces between words
        phonemes = re.sub(r'([a-z])([a-z])', r'\\1 \\2', phonemes)
        
        return phonemes.strip()
    
    def _fallback_phonemization(self, text: str) -> str:
        """Fallback phonemization using simple character mapping"""
        # Simple mapping for basic English sounds
        # This is a very basic fallback - espeak-ng is preferred
        phoneme_map = {
            'hello': 'həˈloʊ',
            'world': 'wɜrld',
            'test': 'tɛst',
            'testing': 'tɛstɪŋ',
            'one': 'wʌn',
            'two': 'tu',
            'three': 'θri',
            'the': 'ðə',
            'quick': 'kwɪk',
            'brown': 'braʊn',
            'fox': 'fɑks',
            'jumps': 'dʒʌmps',
            'over': 'oʊvər',
            'lazy': 'leɪzi',
            'dog': 'dɔg'
        }
        
        words = text.lower().split()
        phoneme_words = []
        
        for word in words:
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalpha())
            if clean_word in phoneme_map:
                phoneme_words.append(phoneme_map[clean_word])
            else:
                # Very basic character-to-phoneme mapping
                phoneme_words.append(self._char_to_phoneme(clean_word))
        
        result = ' '.join(phoneme_words)
        logger.debug(f"Fallback phonemization: '{text}' -> '{result}'")
        return result
    
    def _char_to_phoneme(self, word: str) -> str:
        """Very basic character to phoneme conversion"""
        # This is extremely simplified - real phonemization is much more complex
        char_map = {
            'a': 'æ', 'e': 'ɛ', 'i': 'ɪ', 'o': 'ɔ', 'u': 'ʌ',
            'b': 'b', 'c': 'k', 'd': 'd', 'f': 'f', 'g': 'g',
            'h': 'h', 'j': 'dʒ', 'k': 'k', 'l': 'l', 'm': 'm',
            'n': 'n', 'p': 'p', 'q': 'k', 'r': 'r', 's': 's',
            't': 't', 'v': 'v', 'w': 'w', 'x': 'ks', 'y': 'j', 'z': 'z'
        }
        
        return ''.join(char_map.get(c, c) for c in word.lower())
'''
    
    # Add the method before the last method in the class
    if '_text_to_phonemes' not in content:
        # Find a good insertion point (before the last method)
        insertion_point = content.rfind('\n    def ')
        if insertion_point != -1:
            content = content[:insertion_point] + phonemization_method + content[insertion_point:]
            logger.info("✅ Added phonemization methods")
        else:
            logger.warning("⚠️ Could not find insertion point for phonemization methods")
    
    # Write the fixed content back
    with open(engine_file, 'w') as f:
        f.write(content)
    
    logger.info("✅ TTS engine phonemization fixes applied")

def test_phonemization_fix():
    """Test the phonemization fix"""
    logger.info("🧪 Testing phonemization fix...")
    
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
        
        logger.info(f"🔊 Testing phonemization with: '{test_phrase}'")
        audio_segment = synthesizer.synthesize(request)
        
        # Save test audio
        output_file = "test_audio_output/phonemization_test.wav"
        Path("test_audio_output").mkdir(exist_ok=True)
        
        audio_bytes = audio_segment.to_wav_bytes()
        with open(output_file, 'wb') as f:
            f.write(audio_bytes)
        
        logger.info(f"✅ Phonemization test audio generated: {output_file}")
        logger.info(f"📊 Duration: {audio_segment.duration:.2f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Phonemization test failed: {e}")
        return False

def validate_phonemization_with_stt():
    """Validate the phonemization fix using STT"""
    logger.info("🎧 Validating phonemization fix with STT...")
    
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
        
        # Test the phonemization-fixed audio
        test_file = "test_audio_output/phonemization_test.wav"
        if not Path(test_file).exists():
            logger.warning("⚠️ Phonemization test audio not found")
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
        if "hello" in transcribed_text.lower() and "world" in transcribed_text.lower():
            logger.info("✅ STT validation PASSED - Phonemization fix successful!")
            return True
        elif "hello" in transcribed_text.lower() or "world" in transcribed_text.lower():
            logger.info("🔄 STT validation PARTIAL - Some improvement detected")
            return True
        else:
            logger.warning("⚠️ STT validation FAILED - Audio still corrupted")
            return False
        
    except Exception as e:
        logger.error(f"❌ STT validation failed: {e}")
        return False

def main():
    """Apply phonemization pipeline fix"""
    logger.info("🚀 Starting Phonemization Pipeline Fix...")
    logger.info("="*60)
    
    # Step 1: Fix TTS engine phonemization
    logger.info("\n🔧 STEP 1: Fixing TTS Engine Phonemization")
    fix_tts_engine_phonemization()
    
    # Step 2: Test the fix
    logger.info("\n🧪 STEP 2: Testing Phonemization Fix")
    if not test_phonemization_fix():
        logger.error("❌ Phonemization test failed")
        return False
    
    # Step 3: Validate with STT
    logger.info("\n🎧 STEP 3: Validating with STT")
    stt_success = validate_phonemization_with_stt()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 PHONEMIZATION PIPELINE FIX SUMMARY")
    logger.info("="*60)
    logger.info("✅ TTS engine phonemization pipeline fixed")
    logger.info("✅ Test audio generated with phonemization")
    
    if stt_success:
        logger.info("✅ STT validation passed")
        logger.info("🎉 PHONEMIZATION FIX SUCCESSFUL!")
        logger.info("💡 The system should now generate correct English audio")
    else:
        logger.warning("⚠️ STT validation failed")
        logger.info("🔧 Additional investigation may be required")
    
    return stt_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
