#!/usr/bin/env python3
"""
Debug Tokenization Script
Investigates the tokenization process to identify why audio is still corrupted
"""

import sys
import logging
import numpy as np
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_tokenization_process():
    """Debug the tokenization process step by step"""
    logger.info("🔍 Debugging tokenization process...")
    
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
        
        # Test text
        test_text = "Hello world"
        logger.info(f"🧪 Testing with text: '{test_text}'")
        
        # Step 1: Test phonemization
        logger.info("\n📝 STEP 1: Testing phonemization")
        phonemes = engine._text_to_phonemes(test_text)
        logger.info(f"✅ Phonemes: '{phonemes}'")
        
        # Step 2: Test tokenization
        logger.info("\n🔢 STEP 2: Testing tokenization")
        tokens = engine._tokenize_text(phonemes)
        logger.info(f"✅ Tokens shape: {tokens.shape}")
        logger.info(f"✅ Tokens: {tokens}")
        
        # Step 3: Check tokenizer vocabulary
        logger.info("\n📚 STEP 3: Checking tokenizer vocabulary")
        tokenizer = engine.tokenizer
        logger.info(f"✅ Tokenizer type: {tokenizer.get('type', 'unknown')}")
        
        if 'char_to_id' in tokenizer:
            char_to_id = tokenizer['char_to_id']
            logger.info(f"✅ Vocabulary size: {len(char_to_id)}")
            logger.info(f"✅ Sample vocab: {list(char_to_id.items())[:10]}")
            
            # Check if phoneme characters are in vocab
            phoneme_chars = set(phonemes)
            missing_chars = phoneme_chars - set(char_to_id.keys())
            if missing_chars:
                logger.warning(f"⚠️ Missing characters in vocab: {missing_chars}")
            else:
                logger.info("✅ All phoneme characters found in vocabulary")
        
        # Step 4: Test with raw text (original broken approach)
        logger.info("\n🔤 STEP 4: Testing with raw text (for comparison)")
        raw_tokens = engine._tokenize_text(test_text)
        logger.info(f"✅ Raw text tokens shape: {raw_tokens.shape}")
        logger.info(f"✅ Raw text tokens: {raw_tokens}")
        
        # Step 5: Compare token sequences
        logger.info("\n🔍 STEP 5: Comparing token sequences")
        logger.info(f"Phoneme tokens: {tokens}")
        logger.info(f"Raw text tokens: {raw_tokens}")
        logger.info(f"Tokens are different: {not np.array_equal(tokens, raw_tokens)}")
        
        return {
            'phonemes': phonemes,
            'phoneme_tokens': tokens,
            'raw_tokens': raw_tokens,
            'tokenizer_vocab_size': len(tokenizer.get('char_to_id', {}))
        }
        
    except Exception as e:
        logger.error(f"❌ Tokenization debugging failed: {e}")
        return None

def test_direct_model_inference():
    """Test direct model inference with different token inputs"""
    logger.info("🧪 Testing direct model inference...")
    
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
        
        # Get voice embedding
        voice = "af_heart"
        voice_embedding = engine.voice_manager.get_voice_embedding(voice)
        
        # Test different token inputs
        test_cases = [
            ("Hello world", "phonemes"),
            ("Hello world", "raw_text"),
            ("həˈloʊ wɜrld", "manual_phonemes")
        ]
        
        results = {}
        
        for text, case_type in test_cases:
            logger.info(f"\n🔊 Testing case: {case_type} - '{text}'")
            
            try:
                if case_type == "phonemes":
                    phonemes = engine._text_to_phonemes(text)
                    tokens = engine._tokenize_text(phonemes)
                elif case_type == "raw_text":
                    tokens = engine._tokenize_text(text)
                else:  # manual_phonemes
                    tokens = engine._tokenize_text(text)
                
                logger.info(f"✅ Tokens: {tokens}")
                
                # Prepare model inputs
                model_inputs = engine._prepare_model_inputs(tokens, voice_embedding, 1.0)
                logger.info(f"✅ Model inputs prepared")
                
                # Run inference
                audio_data = engine._run_inference(model_inputs)
                logger.info(f"✅ Audio data shape: {audio_data.shape}")
                logger.info(f"✅ Audio data range: [{np.min(audio_data):.6f}, {np.max(audio_data):.6f}]")
                logger.info(f"✅ Audio data std: {np.std(audio_data):.6f}")
                
                # Check if audio is silent
                is_silent = np.std(audio_data) < 1e-6
                logger.info(f"✅ Audio is silent: {is_silent}")
                
                results[case_type] = {
                    'tokens': tokens,
                    'audio_shape': audio_data.shape,
                    'audio_range': [float(np.min(audio_data)), float(np.max(audio_data))],
                    'audio_std': float(np.std(audio_data)),
                    'is_silent': is_silent
                }
                
            except Exception as e:
                logger.error(f"❌ Failed for case {case_type}: {e}")
                results[case_type] = {'error': str(e)}
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Direct model inference test failed: {e}")
        return None

def analyze_tokenizer_compatibility():
    """Analyze tokenizer compatibility with phonemes"""
    logger.info("🔍 Analyzing tokenizer compatibility...")
    
    try:
        # Load tokenizer configuration
        import json
        tokenizer_path = Path("LiteTTS/config/tokenizer.json")
        
        if tokenizer_path.exists():
            with open(tokenizer_path, 'r') as f:
                tokenizer_config = json.load(f)
            
            vocab = tokenizer_config.get('model', {}).get('vocab', {})
            logger.info(f"✅ Loaded tokenizer with {len(vocab)} tokens")
            
            # Analyze vocabulary
            chars = set(vocab.keys())
            logger.info(f"✅ Character set size: {len(chars)}")
            
            # Check for phonetic symbols
            phonetic_symbols = set('æɛɪɔʌəɜɑɒʊeɪaɪɔɪaʊɪəɛəʊəθðʃʒŋtʃdʒjwrhmnlpbtdkgfvszʔ')
            found_phonetic = chars.intersection(phonetic_symbols)
            missing_phonetic = phonetic_symbols - chars
            
            logger.info(f"✅ Found phonetic symbols: {len(found_phonetic)}")
            logger.info(f"✅ Sample found: {list(found_phonetic)[:10]}")
            logger.info(f"⚠️ Missing phonetic symbols: {len(missing_phonetic)}")
            logger.info(f"⚠️ Sample missing: {list(missing_phonetic)[:10]}")
            
            # Check for basic English letters
            english_letters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
            found_letters = chars.intersection(english_letters)
            missing_letters = english_letters - chars
            
            logger.info(f"✅ Found English letters: {len(found_letters)}")
            logger.info(f"⚠️ Missing English letters: {missing_letters}")
            
            return {
                'vocab_size': len(vocab),
                'phonetic_coverage': len(found_phonetic) / len(phonetic_symbols),
                'english_coverage': len(found_letters) / len(english_letters),
                'missing_letters': list(missing_letters),
                'found_phonetic': list(found_phonetic)
            }
        else:
            logger.error("❌ Tokenizer configuration not found")
            return None
            
    except Exception as e:
        logger.error(f"❌ Tokenizer analysis failed: {e}")
        return None

def main():
    """Run comprehensive tokenization debugging"""
    logger.info("🚀 Starting Tokenization Debugging...")
    logger.info("="*60)
    
    # Step 1: Debug tokenization process
    logger.info("\n🔍 PHASE 1: Tokenization Process Debugging")
    tokenization_results = debug_tokenization_process()
    
    # Step 2: Analyze tokenizer compatibility
    logger.info("\n📚 PHASE 2: Tokenizer Compatibility Analysis")
    compatibility_results = analyze_tokenizer_compatibility()
    
    # Step 3: Test direct model inference
    logger.info("\n🧪 PHASE 3: Direct Model Inference Testing")
    inference_results = test_direct_model_inference()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 TOKENIZATION DEBUGGING SUMMARY")
    logger.info("="*60)
    
    if tokenization_results:
        logger.info("✅ Tokenization process completed")
        logger.info(f"📝 Phonemes generated: '{tokenization_results['phonemes']}'")
        logger.info(f"🔢 Phoneme tokens: {tokenization_results['phoneme_tokens']}")
        logger.info(f"🔤 Raw text tokens: {tokenization_results['raw_tokens']}")
    
    if compatibility_results:
        logger.info(f"📚 Tokenizer vocabulary size: {compatibility_results['vocab_size']}")
        logger.info(f"🔤 English letter coverage: {compatibility_results['english_coverage']:.1%}")
        logger.info(f"🗣️ Phonetic symbol coverage: {compatibility_results['phonetic_coverage']:.1%}")
        
        if compatibility_results['missing_letters']:
            logger.warning(f"⚠️ Missing English letters: {compatibility_results['missing_letters']}")
    
    if inference_results:
        logger.info("🧪 Model inference tests completed")
        for case_type, result in inference_results.items():
            if 'error' not in result:
                logger.info(f"  {case_type}: Audio std={result['audio_std']:.6f}, Silent={result['is_silent']}")
            else:
                logger.error(f"  {case_type}: {result['error']}")
    
    # Diagnosis
    logger.info("\n🔧 DIAGNOSIS:")
    if compatibility_results and compatibility_results['english_coverage'] < 1.0:
        logger.error("❌ CRITICAL: Tokenizer missing English letters - this explains the corruption!")
        logger.error("💡 The tokenizer expects phonetic input but English letters are missing from vocabulary")
    
    if inference_results:
        silent_cases = [case for case, result in inference_results.items() 
                       if 'is_silent' in result and result['is_silent']]
        if silent_cases:
            logger.error(f"❌ CRITICAL: Silent audio generated for cases: {silent_cases}")
    
    return tokenization_results, compatibility_results, inference_results

if __name__ == "__main__":
    main()
