#!/usr/bin/env python3
"""
Model Inference Diagnosis
Deep investigation of model inference to identify why audio content is wrong
"""

import sys
import logging
import numpy as np
from pathlib import Path
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_model_inputs():
    """Analyze the inputs being fed to the ONNX model"""
    logger.info("🔍 Analyzing model inputs...")
    
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
        
        # Test with simple text
        test_text = "Hello world"
        voice = "af_heart"
        speed = 1.0
        
        logger.info(f"🧪 Testing model inputs for: '{test_text}'")
        
        # Step 1: Get phonemes
        phonemes = engine._text_to_phonemes(test_text)
        logger.info(f"📝 Phonemes: '{phonemes}'")
        
        # Step 2: Tokenize
        tokens = engine._tokenize_text(phonemes)
        logger.info(f"🔢 Tokens shape: {tokens.shape}")
        logger.info(f"🔢 Tokens: {tokens}")
        
        # Step 3: Get voice embedding
        voice_embedding = engine.voice_manager.get_voice_embedding(voice)
        logger.info(f"🎤 Voice embedding shape: {voice_embedding.shape}")
        logger.info(f"🎤 Voice embedding range: [{np.min(voice_embedding):.6f}, {np.max(voice_embedding):.6f}]")
        
        # Step 4: Prepare model inputs
        model_inputs = engine._prepare_model_inputs(tokens, voice_embedding, speed)
        logger.info(f"🔧 Model inputs prepared:")
        for key, value in model_inputs.items():
            if hasattr(value, 'shape'):
                logger.info(f"  {key}: shape={value.shape}, dtype={value.dtype}")
                logger.info(f"    range=[{np.min(value):.6f}, {np.max(value):.6f}]")
            else:
                logger.info(f"  {key}: {value}")
        
        # Step 5: Run inference and analyze output
        logger.info("🧠 Running model inference...")
        audio_output = engine._run_inference(model_inputs)
        logger.info(f"🔊 Audio output shape: {audio_output.shape}")
        logger.info(f"🔊 Audio output range: [{np.min(audio_output):.6f}, {np.max(audio_output):.6f}]")
        logger.info(f"🔊 Audio output std: {np.std(audio_output):.6f}")
        
        # Check for patterns in the audio
        is_silent = np.std(audio_output) < 1e-6
        is_clipped = np.any(np.abs(audio_output) > 0.99)
        has_dc_offset = abs(np.mean(audio_output)) > 0.1
        
        logger.info(f"🔍 Audio analysis:")
        logger.info(f"  Silent: {is_silent}")
        logger.info(f"  Clipped: {is_clipped}")
        logger.info(f"  DC offset: {has_dc_offset}")
        
        return {
            'phonemes': phonemes,
            'tokens': tokens,
            'voice_embedding': voice_embedding,
            'model_inputs': model_inputs,
            'audio_output': audio_output,
            'audio_stats': {
                'silent': is_silent,
                'clipped': is_clipped,
                'dc_offset': has_dc_offset,
                'std': float(np.std(audio_output)),
                'mean': float(np.mean(audio_output))
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Model input analysis failed: {e}")
        return None

def compare_voice_embeddings():
    """Compare voice embeddings to see if they're corrupted"""
    logger.info("🎤 Comparing voice embeddings...")
    
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
        
        # Test multiple voices
        test_voices = ["af_heart", "am_puck", "af_bella"]
        voice_data = {}
        
        for voice in test_voices:
            try:
                embedding = engine.voice_manager.get_voice_embedding(voice)
                voice_data[voice] = {
                    'shape': embedding.shape,
                    'mean': float(np.mean(embedding)),
                    'std': float(np.std(embedding)),
                    'min': float(np.min(embedding)),
                    'max': float(np.max(embedding)),
                    'norm': float(np.linalg.norm(embedding))
                }
                logger.info(f"✅ Voice {voice}: shape={embedding.shape}, norm={voice_data[voice]['norm']:.6f}")
            except Exception as e:
                logger.error(f"❌ Failed to load voice {voice}: {e}")
                voice_data[voice] = {'error': str(e)}
        
        # Check if all voices have similar characteristics
        norms = [data['norm'] for data in voice_data.values() if 'norm' in data]
        if len(norms) > 1:
            norm_std = np.std(norms)
            logger.info(f"🔍 Voice embedding norm variation: {norm_std:.6f}")
            if norm_std < 0.1:
                logger.warning("⚠️ Voice embeddings may be too similar (possible corruption)")
        
        return voice_data
        
    except Exception as e:
        logger.error(f"❌ Voice embedding comparison failed: {e}")
        return None

def test_model_with_known_good_inputs():
    """Test the model with inputs that should produce known results"""
    logger.info("🧪 Testing model with known good inputs...")
    
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
        
        # Test with very simple, known phonemes
        test_cases = [
            {
                'name': 'simple_a',
                'phonemes': 'a',
                'description': 'Single vowel sound'
            },
            {
                'name': 'simple_hello',
                'phonemes': 'hɛloʊ',
                'description': 'Simple hello phonemes'
            },
            {
                'name': 'silence',
                'phonemes': ' ',
                'description': 'Just space (should be silent)'
            }
        ]
        
        results = {}
        voice = "af_heart"
        
        for test_case in test_cases:
            name = test_case['name']
            phonemes = test_case['phonemes']
            description = test_case['description']
            
            logger.info(f"🔊 Testing {name}: '{phonemes}' ({description})")
            
            try:
                # Tokenize the phonemes directly
                tokens = engine._tokenize_text(phonemes)
                logger.info(f"  Tokens: {tokens}")
                
                # Get voice embedding
                voice_embedding = engine.voice_manager.get_voice_embedding(voice)
                
                # Prepare inputs
                model_inputs = engine._prepare_model_inputs(tokens, voice_embedding, 1.0)
                
                # Run inference
                audio_output = engine._run_inference(model_inputs)
                
                # Analyze output
                audio_stats = {
                    'shape': audio_output.shape,
                    'std': float(np.std(audio_output)),
                    'mean': float(np.mean(audio_output)),
                    'max_abs': float(np.max(np.abs(audio_output))),
                    'is_silent': np.std(audio_output) < 1e-6
                }
                
                results[name] = {
                    'phonemes': phonemes,
                    'tokens': tokens.tolist(),
                    'audio_stats': audio_stats,
                    'success': True
                }
                
                logger.info(f"  ✅ Audio std: {audio_stats['std']:.6f}, Silent: {audio_stats['is_silent']}")
                
            except Exception as e:
                logger.error(f"  ❌ Failed: {e}")
                results[name] = {
                    'phonemes': phonemes,
                    'error': str(e),
                    'success': False
                }
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Known good inputs test failed: {e}")
        return None

def analyze_tokenizer_behavior():
    """Analyze how the tokenizer behaves with different inputs"""
    logger.info("📚 Analyzing tokenizer behavior...")
    
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
        
        # Test different input types
        test_inputs = [
            "hello",           # lowercase English
            "Hello",           # mixed case English
            "hɛloʊ",          # phonemes
            "a",              # single letter
            "æ",              # single phoneme
            " ",              # space
            "",               # empty
            "123",            # numbers
            "hello world",    # multiple words
            "hɛloʊ wɔrld"     # multiple phoneme words
        ]
        
        results = {}
        
        for test_input in test_inputs:
            logger.info(f"🔤 Testing tokenization: '{test_input}'")
            
            try:
                tokens = engine._tokenize_text(test_input)
                
                # Analyze tokens
                unique_tokens = np.unique(tokens)
                token_stats = {
                    'shape': tokens.shape,
                    'tokens': tokens.tolist(),
                    'unique_tokens': unique_tokens.tolist(),
                    'num_unique': len(unique_tokens),
                    'has_unknown': 0 in tokens,  # Assuming 0 is unknown token
                    'max_token': int(np.max(tokens)),
                    'min_token': int(np.min(tokens))
                }
                
                results[test_input] = token_stats
                
                logger.info(f"  ✅ Tokens: {tokens.tolist()}")
                logger.info(f"  📊 Unique: {len(unique_tokens)}, Unknown: {token_stats['has_unknown']}")
                
            except Exception as e:
                logger.error(f"  ❌ Tokenization failed: {e}")
                results[test_input] = {'error': str(e)}
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Tokenizer behavior analysis failed: {e}")
        return None

def main():
    """Run comprehensive model inference diagnosis"""
    logger.info("🚀 Starting Model Inference Diagnosis...")
    logger.info("="*60)
    
    # Phase 1: Analyze model inputs
    logger.info("\n🔍 PHASE 1: Model Input Analysis")
    input_analysis = analyze_model_inputs()
    
    # Phase 2: Compare voice embeddings
    logger.info("\n🎤 PHASE 2: Voice Embedding Analysis")
    voice_analysis = compare_voice_embeddings()
    
    # Phase 3: Test with known good inputs
    logger.info("\n🧪 PHASE 3: Known Good Inputs Test")
    known_good_test = test_model_with_known_good_inputs()
    
    # Phase 4: Analyze tokenizer behavior
    logger.info("\n📚 PHASE 4: Tokenizer Behavior Analysis")
    tokenizer_analysis = analyze_tokenizer_behavior()
    
    # Summary and diagnosis
    logger.info("\n" + "="*60)
    logger.info("📊 MODEL INFERENCE DIAGNOSIS SUMMARY")
    logger.info("="*60)
    
    # Save detailed report
    report = {
        'input_analysis': input_analysis,
        'voice_analysis': voice_analysis,
        'known_good_test': known_good_test,
        'tokenizer_analysis': tokenizer_analysis
    }
    
    try:
        with open('model_inference_diagnosis_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info("📄 Detailed report saved to: model_inference_diagnosis_report.json")
    except Exception as e:
        logger.error(f"❌ Failed to save report: {e}")
    
    # Key findings
    if input_analysis and input_analysis['audio_stats']['silent']:
        logger.error("❌ CRITICAL: Model is producing silent audio")
    elif input_analysis and input_analysis['audio_stats']['std'] < 0.01:
        logger.warning("⚠️ WARNING: Model audio has very low variation")
    
    if voice_analysis:
        successful_voices = [v for v in voice_analysis.values() if 'error' not in v]
        logger.info(f"✅ Successfully loaded {len(successful_voices)} voice embeddings")
    
    if tokenizer_analysis:
        unknown_inputs = [inp for inp, data in tokenizer_analysis.items() 
                         if isinstance(data, dict) and data.get('has_unknown', False)]
        if unknown_inputs:
            logger.warning(f"⚠️ Inputs with unknown tokens: {unknown_inputs}")
    
    logger.info("\n🔧 NEXT STEPS:")
    logger.info("1. Review the detailed report for specific issues")
    logger.info("2. Compare model inputs against working baseline")
    logger.info("3. Check if model file is corrupted")
    logger.info("4. Verify voice embeddings are loading correctly")
    
    return report

if __name__ == "__main__":
    main()
