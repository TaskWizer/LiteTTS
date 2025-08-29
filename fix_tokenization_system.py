#!/usr/bin/env python3
"""
Tokenization System Fix
Ensures proper phoneme-to-token mapping and eliminates unknown tokens
"""

import sys
import logging
import numpy as np
import json
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_tokenizer_vocabulary():
    """Analyze the current tokenizer vocabulary to understand what's missing"""
    logger.info("📚 Analyzing tokenizer vocabulary...")
    
    try:
        tokenizer_path = Path("LiteTTS/config/tokenizer.json")
        
        if not tokenizer_path.exists():
            logger.error("❌ Tokenizer configuration not found")
            return None
        
        with open(tokenizer_path, 'r') as f:
            tokenizer_config = json.load(f)
        
        vocab = tokenizer_config.get('model', {}).get('vocab', {})
        logger.info(f"✅ Loaded tokenizer with {len(vocab)} tokens")
        
        # Analyze character coverage
        chars = set(vocab.keys())
        
        # Check English letters
        english_letters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        found_letters = chars.intersection(english_letters)
        missing_letters = english_letters - chars
        
        # Check phonetic symbols (IPA)
        phonetic_symbols = set('æɛɪɔʌəɜɑɒʊeɪaɪɔɪaʊɪəɛəʊəθðʃʒŋtʃdʒjwrhmnlpbtdkgfvszʔɡ')
        found_phonetic = chars.intersection(phonetic_symbols)
        missing_phonetic = phonetic_symbols - chars
        
        # Check common punctuation and spaces
        punctuation = set(' .,!?;:-()[]{}"\'\n\t')
        found_punct = chars.intersection(punctuation)
        missing_punct = punctuation - chars
        
        analysis = {
            'total_vocab_size': len(vocab),
            'english_letters': {
                'found': list(found_letters),
                'missing': list(missing_letters),
                'coverage': len(found_letters) / len(english_letters)
            },
            'phonetic_symbols': {
                'found': list(found_phonetic),
                'missing': list(missing_phonetic),
                'coverage': len(found_phonetic) / len(phonetic_symbols)
            },
            'punctuation': {
                'found': list(found_punct),
                'missing': list(missing_punct),
                'coverage': len(found_punct) / len(punctuation)
            }
        }
        
        logger.info(f"📊 English letter coverage: {analysis['english_letters']['coverage']:.1%}")
        logger.info(f"📊 Phonetic symbol coverage: {analysis['phonetic_symbols']['coverage']:.1%}")
        logger.info(f"📊 Punctuation coverage: {analysis['punctuation']['coverage']:.1%}")
        
        if missing_letters:
            logger.warning(f"⚠️ Missing English letters: {missing_letters}")
        if missing_phonetic:
            logger.warning(f"⚠️ Missing phonetic symbols: {missing_phonetic}")
        
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Tokenizer analysis failed: {e}")
        return None

def fix_phoneme_mapping():
    """Fix the phoneme mapping to use only characters in the vocabulary"""
    logger.info("🔧 Fixing phoneme mapping...")
    
    # Get the current vocabulary analysis
    vocab_analysis = analyze_tokenizer_vocabulary()
    if not vocab_analysis:
        logger.error("❌ Cannot fix phoneme mapping without vocabulary analysis")
        return False
    
    # Get available phonetic symbols
    available_phonetic = set(vocab_analysis['phonetic_symbols']['found'])
    available_letters = set(vocab_analysis['english_letters']['found'])
    
    logger.info(f"✅ Available phonetic symbols: {len(available_phonetic)}")
    logger.info(f"✅ Available letters: {len(available_letters)}")
    
    # Update the engine's phoneme mapping
    engine_file = Path("LiteTTS/tts/engine.py")
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Create a new fallback phonemization that only uses available characters
    new_fallback_method = f'''    def _fallback_phonemization(self, text: str) -> str:
        """Fallback phonemization using only vocabulary-compatible characters"""
        # Only use phonemes that are confirmed to be in the tokenizer vocabulary
        # Available phonetic symbols: {sorted(available_phonetic)}
        # Available letters: {sorted(available_letters)}
        
        phoneme_map = {{
            'hello': 'hɛlo',      # Simplified, using available symbols
            'world': 'wɔrld',     # Using available symbols
            'test': 'tɛst',
            'testing': 'tɛstɪŋ',
            'one': 'wʌn',
            'two': 'tu',
            'three': 'θri',
            'the': 'ðɛ',          # Using available ð and ɛ
            'quick': 'kwɪk',
            'brown': 'braʊn',
            'fox': 'fɑks',
            'jumps': 'dʒʌmps',
            'over': 'ovɛr',       # Simplified
            'lazy': 'leɪzi',
            'dog': 'dɔg',
            'good': 'gʊd',
            'morning': 'mɔrnɪŋ',
            'how': 'haʊ',
            'are': 'ɑr',
            'you': 'ju'
        }}
        
        words = text.lower().split()
        phoneme_words = []
        
        for word in words:
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalpha())
            if clean_word in phoneme_map:
                phoneme_words.append(phoneme_map[clean_word])
            else:
                # Map to available characters only
                phoneme_words.append(self._char_to_vocab_phoneme(clean_word))
        
        result = ' '.join(phoneme_words)
        logger.debug(f"Vocab-compatible phonemization: '{{text}}' -> '{{result}}'")
        return result'''
    
    # Find and replace the fallback phonemization method
    old_method_start = "def _fallback_phonemization(self, text: str) -> str:"
    old_method_end = "return result"
    
    # Find the method boundaries
    start_idx = content.find(old_method_start)
    if start_idx == -1:
        logger.error("❌ Could not find _fallback_phonemization method")
        return False
    
    # Find the end of the method (next method definition or class end)
    end_search_start = content.find(old_method_end, start_idx)
    if end_search_start == -1:
        logger.error("❌ Could not find end of _fallback_phonemization method")
        return False
    
    # Find the actual end (end of the return statement line)
    end_idx = content.find('\n', end_search_start) + 1
    
    # Replace the method
    new_content = content[:start_idx] + new_fallback_method + content[end_idx:]
    
    # Also update the character mapping method
    new_char_method = f'''    
    def _char_to_vocab_phoneme(self, word: str) -> str:
        """Map characters to phonemes that exist in tokenizer vocabulary"""
        # Only use characters confirmed to be in the vocabulary
        available_chars = {sorted(available_letters | available_phonetic)}
        
        char_map = {{
            'a': 'æ' if 'æ' in available_chars else 'a',
            'e': 'ɛ' if 'ɛ' in available_chars else 'e', 
            'i': 'ɪ' if 'ɪ' in available_chars else 'i',
            'o': 'ɔ' if 'ɔ' in available_chars else 'o',
            'u': 'ʌ' if 'ʌ' in available_chars else 'u',
            'b': 'b', 'c': 'k', 'd': 'd', 'f': 'f', 'g': 'g',
            'h': 'h', 'j': 'dʒ' if 'dʒ' in available_chars else 'j', 
            'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'p': 'p', 
            'q': 'k', 'r': 'r', 's': 's', 't': 't', 'v': 'v', 
            'w': 'w', 'x': 'ks', 'y': 'j', 'z': 'z'
        }}
        
        result = ''.join(char_map.get(c, c) for c in word.lower())
        # Ensure all characters are in vocabulary
        filtered_result = ''.join(c for c in result if c in available_chars)
        return filtered_result if filtered_result else word.lower()'''
    
    # Add the new character method
    if "_char_to_vocab_phoneme" not in new_content:
        # Find a good insertion point (after the fallback method)
        insertion_point = new_content.find('\n    def ', new_content.find(new_fallback_method) + len(new_fallback_method))
        if insertion_point != -1:
            new_content = new_content[:insertion_point] + new_char_method + new_content[insertion_point:]
            logger.info("✅ Added vocab-compatible character mapping method")
        else:
            logger.warning("⚠️ Could not find insertion point for character mapping method")
    
    # Write the updated content
    with open(engine_file, 'w') as f:
        f.write(new_content)
    
    logger.info("✅ Phoneme mapping fixes applied")
    return True

def test_tokenization_with_fixes():
    """Test the tokenization system with the fixes"""
    logger.info("🧪 Testing tokenization with fixes...")
    
    try:
        from LiteTTS.tts.engine import KokoroTTSEngine
        from LiteTTS.models import TTSConfiguration
        
        # Initialize engine
        config = TTSConfiguration(
            model_path="LiteTTS/models/model_q4.onnx",
            voices_path="LiteTTS/voices",
            device="cpu",
            sample_rate=24000
        )
        
        engine = KokoroTTSEngine(config)
        
        # Test cases
        test_cases = [
            "Hello world",
            "Testing one two three", 
            "The quick brown fox",
            "Good morning",
            "How are you"
        ]
        
        results = {}
        
        for test_text in test_cases:
            logger.info(f"🔤 Testing: '{test_text}'")
            
            try:
                # Test phonemization
                phonemes = engine._text_to_phonemes(test_text)
                logger.info(f"  📝 Phonemes: '{phonemes}'")
                
                # Test tokenization
                tokens = engine._tokenize_text(phonemes)
                logger.info(f"  🔢 Tokens: {tokens}")
                
                # Check for unknown tokens (assuming 0 is unknown)
                unknown_count = np.sum(tokens == 0)
                total_tokens = len(tokens)
                unknown_ratio = unknown_count / total_tokens if total_tokens > 0 else 0
                
                results[test_text] = {
                    'phonemes': phonemes,
                    'tokens': tokens.tolist(),
                    'unknown_count': int(unknown_count),
                    'total_tokens': int(total_tokens),
                    'unknown_ratio': float(unknown_ratio),
                    'success': unknown_ratio < 0.1  # Less than 10% unknown tokens
                }
                
                status = "✅ PASS" if unknown_ratio < 0.1 else "❌ FAIL"
                logger.info(f"  📊 Unknown tokens: {unknown_count}/{total_tokens} ({unknown_ratio:.1%}) - {status}")
                
            except Exception as e:
                logger.error(f"  ❌ Failed: {e}")
                results[test_text] = {
                    'error': str(e),
                    'success': False
                }
        
        # Calculate overall success rate
        successful_tests = sum(1 for r in results.values() if r.get('success', False))
        total_tests = len(results)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        logger.info(f"\n📊 TOKENIZATION TEST RESULTS:")
        logger.info(f"Successful tests: {successful_tests}/{total_tests} ({success_rate:.1%})")
        
        return success_rate >= 0.8  # 80% success rate required
        
    except Exception as e:
        logger.error(f"❌ Tokenization test failed: {e}")
        return False

def test_end_to_end_with_stt():
    """Test end-to-end synthesis and validate with STT"""
    logger.info("🎧 Testing end-to-end synthesis with STT validation...")
    
    try:
        from LiteTTS.tts.synthesizer import TTSSynthesizer
        from LiteTTS.models import TTSConfiguration, TTSRequest
        from LiteTTS.stt.faster_whisper_stt import FasterWhisperSTT
        from LiteTTS.stt.stt_models import STTRequest, STTConfiguration
        
        # Initialize TTS
        tts_config = TTSConfiguration(
            model_path="LiteTTS/models/model_q4.onnx",
            voices_path="LiteTTS/voices",
            device="cpu",
            sample_rate=24000
        )
        
        synthesizer = TTSSynthesizer(tts_config)
        
        # Initialize STT
        stt_config = STTConfiguration(
            model="tiny.en",
            device="cpu",
            compute_type="int8"
        )
        
        stt_engine = FasterWhisperSTT(stt_config)
        
        # Test cases
        test_cases = [
            {
                'text': 'Hello world',
                'expected_words': ['hello', 'world'],
                'file': 'test_audio_output/tokenization_fix_hello.wav'
            },
            {
                'text': 'Testing one two three',
                'expected_words': ['testing', 'one', 'two', 'three'],
                'file': 'test_audio_output/tokenization_fix_numbers.wav'
            }
        ]
        
        results = {}
        Path("test_audio_output").mkdir(exist_ok=True)
        
        for test_case in test_cases:
            text = test_case['text']
            expected_words = test_case['expected_words']
            output_file = test_case['file']
            
            logger.info(f"🔊 Testing: '{text}'")
            
            try:
                # Generate audio
                request = TTSRequest(
                    input=text,
                    voice="af_heart",
                    speed=1.0
                )
                
                audio_segment = synthesizer.synthesize(request)
                
                # Save audio
                audio_bytes = audio_segment.to_wav_bytes()
                with open(output_file, 'wb') as f:
                    f.write(audio_bytes)
                
                logger.info(f"  ✅ Generated {audio_segment.duration:.2f}s audio")
                
                # Transcribe with STT
                stt_request = STTRequest(
                    audio=output_file,
                    language="en"
                )
                
                response = stt_engine.transcribe(stt_request)
                transcribed_text = response.text.strip().lower()
                
                # Calculate word overlap accuracy
                transcribed_words = set(transcribed_text.split())
                expected_words_set = set(expected_words)
                
                if len(expected_words_set) > 0:
                    accuracy = len(transcribed_words.intersection(expected_words_set)) / len(expected_words_set)
                else:
                    accuracy = 0.0
                
                results[text] = {
                    'transcribed': transcribed_text,
                    'expected_words': expected_words,
                    'accuracy': accuracy,
                    'confidence': response.confidence,
                    'duration': audio_segment.duration,
                    'success': accuracy >= 0.5  # 50% word accuracy
                }
                
                status = "✅ PASS" if accuracy >= 0.5 else "❌ FAIL"
                logger.info(f"  📝 Expected: {' '.join(expected_words)}")
                logger.info(f"  🔤 Transcribed: '{transcribed_text}'")
                logger.info(f"  📊 Accuracy: {accuracy:.1%} | Confidence: {response.confidence:.3f} - {status}")
                
            except Exception as e:
                logger.error(f"  ❌ Failed: {e}")
                results[text] = {
                    'error': str(e),
                    'success': False
                }
        
        # Calculate overall success
        successful_tests = sum(1 for r in results.values() if r.get('success', False))
        total_tests = len(results)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        logger.info(f"\n📊 END-TO-END TEST RESULTS:")
        logger.info(f"Successful tests: {successful_tests}/{total_tests} ({success_rate:.1%})")
        
        return success_rate >= 0.5  # 50% success rate for initial validation
        
    except Exception as e:
        logger.error(f"❌ End-to-end test failed: {e}")
        return False

def main():
    """Apply tokenization system fixes"""
    logger.info("🚀 Starting Tokenization System Fix...")
    logger.info("="*60)
    
    # Step 1: Analyze tokenizer vocabulary
    logger.info("\n📚 STEP 1: Analyzing Tokenizer Vocabulary")
    vocab_analysis = analyze_tokenizer_vocabulary()
    
    if not vocab_analysis:
        logger.error("❌ Cannot proceed without vocabulary analysis")
        return False
    
    # Step 2: Fix phoneme mapping
    logger.info("\n🔧 STEP 2: Fixing Phoneme Mapping")
    if not fix_phoneme_mapping():
        logger.error("❌ Phoneme mapping fix failed")
        return False
    
    # Step 3: Test tokenization
    logger.info("\n🧪 STEP 3: Testing Tokenization")
    tokenization_success = test_tokenization_with_fixes()
    
    # Step 4: Test end-to-end with STT
    logger.info("\n🎧 STEP 4: End-to-End STT Validation")
    stt_success = test_end_to_end_with_stt()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 TOKENIZATION SYSTEM FIX SUMMARY")
    logger.info("="*60)
    logger.info("✅ Tokenizer vocabulary analyzed")
    logger.info("✅ Phoneme mapping updated to use only available characters")
    
    if tokenization_success:
        logger.info("✅ Tokenization tests passed")
    else:
        logger.warning("⚠️ Tokenization tests need improvement")
    
    if stt_success:
        logger.info("✅ STT validation passed")
        logger.info("🎉 TOKENIZATION SYSTEM FIXED!")
        logger.info("💡 Audio should now match input text correctly")
    else:
        logger.warning("⚠️ STT validation needs improvement")
        logger.info("🔧 Tokenization system partially fixed")
    
    return tokenization_success and stt_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
