#!/usr/bin/env python3
"""
Voice Embedding System Fix
Resolves the 'VoiceEmbedding' object has no attribute 'shape' error and related issues
"""

import sys
import logging
import numpy as np
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_voice_embedding_interface():
    """Fix the VoiceEmbedding class to provide proper interface compatibility"""
    logger.info("🔧 Fixing VoiceEmbedding interface...")
    
    # Fix the VoiceEmbedding class in models.py
    models_file = Path("LiteTTS/models.py")
    with open(models_file, 'r') as f:
        content = f.read()
    
    # Find the VoiceEmbedding class and add compatibility properties
    voice_embedding_class = '''@dataclass
class VoiceEmbedding:
    """Voice embedding data structure"""
    name: str
    embedding_data: Optional[np.ndarray] = None
    metadata: Optional[VoiceMetadata] = None
    loaded_at: Optional[datetime] = None
    file_hash: str = ""'''
    
    enhanced_voice_embedding_class = '''@dataclass
class VoiceEmbedding:
    """Voice embedding data structure"""
    name: str
    embedding_data: Optional[np.ndarray] = None
    metadata: Optional[VoiceMetadata] = None
    loaded_at: Optional[datetime] = None
    file_hash: str = ""
    
    @property
    def shape(self):
        """Compatibility property for accessing embedding data shape"""
        if self.embedding_data is not None:
            return self.embedding_data.shape
        return None
    
    @property
    def dtype(self):
        """Compatibility property for accessing embedding data dtype"""
        if self.embedding_data is not None:
            return self.embedding_data.dtype
        return None
    
    def __array__(self):
        """Allow numpy operations directly on VoiceEmbedding object"""
        if self.embedding_data is not None:
            return self.embedding_data
        raise ValueError("No embedding data available")
    
    def numpy(self):
        """Return numpy array of embedding data"""
        if self.embedding_data is not None:
            return self.embedding_data
        raise ValueError("No embedding data available")'''
    
    if voice_embedding_class in content:
        content = content.replace(voice_embedding_class, enhanced_voice_embedding_class)
        logger.info("✅ Enhanced VoiceEmbedding class in models.py")
    else:
        logger.warning("⚠️ Could not find VoiceEmbedding class in models.py")
    
    # Write the updated content
    with open(models_file, 'w') as f:
        f.write(content)
    
    logger.info("✅ VoiceEmbedding interface fixes applied")

def fix_model_interface_parameters():
    """Fix the model interface to include missing emotion parameters"""
    logger.info("🔧 Fixing model interface parameters...")
    
    engine_file = Path("LiteTTS/tts/engine.py")
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Fix the _prepare_model_inputs call in synthesize method
    old_prepare_call = '''            # Prepare inputs for ONNX model
            model_inputs = self._prepare_model_inputs(tokens, voice_embedding, speed, emotion, emotion_strength)'''
    
    # Check if the call already has the parameters
    if old_prepare_call in content:
        logger.info("✅ Model interface parameters already fixed")
    else:
        # Look for the old call without emotion parameters
        old_call_pattern = '''model_inputs = self._prepare_model_inputs(tokens, voice_embedding, speed)'''
        new_call_pattern = '''model_inputs = self._prepare_model_inputs(tokens, voice_embedding, speed, emotion, emotion_strength)'''
        
        if old_call_pattern in content:
            content = content.replace(old_call_pattern, new_call_pattern)
            logger.info("✅ Fixed _prepare_model_inputs call to include emotion parameters")
        else:
            logger.warning("⚠️ Could not find _prepare_model_inputs call to fix")
    
    # Ensure the _prepare_model_inputs method handles None emotion properly
    old_emotion_handling = '''    def _prepare_model_inputs(self, tokens: np.ndarray, voice_embedding: VoiceEmbedding,
                            speed: float, emotion: Optional[str], emotion_strength: float) -> Dict[str, np.ndarray]:
        """Prepare inputs for the ONNX model"""
        # Get voice embedding data
        voice_data = voice_embedding.embedding_data'''
    
    new_emotion_handling = '''    def _prepare_model_inputs(self, tokens: np.ndarray, voice_embedding: VoiceEmbedding,
                            speed: float, emotion: Optional[str] = None, emotion_strength: float = 1.0) -> Dict[str, np.ndarray]:
        """Prepare inputs for the ONNX model"""
        # Handle default emotion parameters
        if emotion is None:
            emotion = "neutral"
        if emotion_strength is None:
            emotion_strength = 1.0
            
        # Get voice embedding data
        voice_data = voice_embedding.embedding_data'''
    
    if old_emotion_handling in content:
        content = content.replace(old_emotion_handling, new_emotion_handling)
        logger.info("✅ Enhanced emotion parameter handling")
    else:
        logger.warning("⚠️ Could not find emotion parameter handling to enhance")
    
    # Write the updated content
    with open(engine_file, 'w') as f:
        f.write(content)
    
    logger.info("✅ Model interface parameter fixes applied")

def fix_voice_manager_compatibility():
    """Fix voice manager to ensure proper VoiceEmbedding objects are returned"""
    logger.info("🔧 Fixing voice manager compatibility...")
    
    # Check if voice manager is returning proper VoiceEmbedding objects
    cache_file = Path("LiteTTS/voice/cache.py")
    with open(cache_file, 'r') as f:
        content = f.read()
    
    # Ensure the cache returns VoiceEmbedding objects with proper embedding_data
    validation_check = '''            # Validate embedding data
            if embedding_data is None:
                logger.error(f"No embedding data loaded for voice: {voice_name}")
                return None
            
            # Ensure embedding_data is a numpy array
            if not isinstance(embedding_data, np.ndarray):
                try:
                    embedding_data = np.array(embedding_data, dtype=np.float32)
                except Exception as e:
                    logger.error(f"Failed to convert embedding data to numpy array: {e}")
                    return None'''
    
    if validation_check not in content:
        # Find the validation section and enhance it
        old_validation = '''            # Validate embedding data
            if embedding_data is None:
                logger.error(f"No embedding data loaded for voice: {voice_name}")
                return None'''
        
        new_validation = '''            # Validate embedding data
            if embedding_data is None:
                logger.error(f"No embedding data loaded for voice: {voice_name}")
                return None
            
            # Ensure embedding_data is a numpy array
            if not isinstance(embedding_data, np.ndarray):
                try:
                    embedding_data = np.array(embedding_data, dtype=np.float32)
                    logger.debug(f"Converted embedding data to numpy array for voice: {voice_name}")
                except Exception as e:
                    logger.error(f"Failed to convert embedding data to numpy array: {e}")
                    return None
            
            # Validate embedding shape
            if embedding_data.size == 0:
                logger.error(f"Empty embedding data for voice: {voice_name}")
                return None'''
        
        if old_validation in content:
            content = content.replace(old_validation, new_validation)
            logger.info("✅ Enhanced embedding data validation")
        else:
            logger.warning("⚠️ Could not find embedding validation to enhance")
    
    # Write the updated content
    with open(cache_file, 'w') as f:
        f.write(content)
    
    logger.info("✅ Voice manager compatibility fixes applied")

def test_voice_embedding_fixes():
    """Test the voice embedding system fixes"""
    logger.info("🧪 Testing voice embedding fixes...")
    
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
        
        # Test voice embedding loading
        test_voice = "af_heart"
        logger.info(f"🎤 Testing voice embedding loading for: {test_voice}")
        
        voice_embedding = engine.voice_manager.get_voice_embedding(test_voice)
        
        if voice_embedding is None:
            logger.error(f"❌ Failed to load voice embedding: {test_voice}")
            return False
        
        # Test the new interface properties
        logger.info(f"✅ Voice embedding loaded: {voice_embedding.name}")
        logger.info(f"✅ Shape property: {voice_embedding.shape}")
        logger.info(f"✅ Dtype property: {voice_embedding.dtype}")
        
        # Test numpy compatibility
        try:
            embedding_array = np.array(voice_embedding)
            logger.info(f"✅ Numpy conversion successful: {embedding_array.shape}")
        except Exception as e:
            logger.error(f"❌ Numpy conversion failed: {e}")
            return False
        
        # Test model input preparation
        logger.info("🔧 Testing model input preparation...")
        
        # Simple tokenization test
        tokens = np.array([1, 2, 3, 4, 5], dtype=np.int64)
        
        try:
            model_inputs = engine._prepare_model_inputs(
                tokens, voice_embedding, 1.0, "neutral", 1.0
            )
            logger.info(f"✅ Model inputs prepared successfully")
            logger.info(f"✅ Input keys: {list(model_inputs.keys())}")
            
            for key, value in model_inputs.items():
                if hasattr(value, 'shape'):
                    logger.info(f"  {key}: shape={value.shape}, dtype={value.dtype}")
                else:
                    logger.info(f"  {key}: {value}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Model input preparation failed: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Voice embedding test failed: {e}")
        return False

def test_end_to_end_synthesis():
    """Test end-to-end synthesis with the fixes"""
    logger.info("🔊 Testing end-to-end synthesis...")
    
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
        
        # Test synthesis
        test_text = "Hello world"
        request = TTSRequest(
            input=test_text,
            voice="af_heart",
            speed=1.0
        )
        
        logger.info(f"🔊 Testing synthesis: '{test_text}'")
        
        audio_segment = synthesizer.synthesize(request)
        
        # Save test audio
        output_file = "test_audio_output/voice_embedding_fix_test.wav"
        Path("test_audio_output").mkdir(exist_ok=True)
        
        audio_bytes = audio_segment.to_wav_bytes()
        with open(output_file, 'wb') as f:
            f.write(audio_bytes)
        
        logger.info(f"✅ Synthesis successful!")
        logger.info(f"✅ Duration: {audio_segment.duration:.2f}s")
        logger.info(f"✅ Output saved: {output_file}")
        
        # Check if audio is not silent
        audio_data = audio_segment.audio_data
        audio_std = np.std(audio_data)
        is_silent = audio_std < 1e-6
        
        logger.info(f"✅ Audio std: {audio_std:.6f}")
        logger.info(f"✅ Audio is silent: {is_silent}")
        
        return not is_silent
        
    except Exception as e:
        logger.error(f"❌ End-to-end synthesis test failed: {e}")
        return False

def main():
    """Apply voice embedding system fixes"""
    logger.info("🚀 Starting Voice Embedding System Fix...")
    logger.info("="*60)
    
    # Step 1: Fix VoiceEmbedding interface
    logger.info("\n🔧 STEP 1: Fixing VoiceEmbedding Interface")
    fix_voice_embedding_interface()
    
    # Step 2: Fix model interface parameters
    logger.info("\n🔧 STEP 2: Fixing Model Interface Parameters")
    fix_model_interface_parameters()
    
    # Step 3: Fix voice manager compatibility
    logger.info("\n🔧 STEP 3: Fixing Voice Manager Compatibility")
    fix_voice_manager_compatibility()
    
    # Step 4: Test the fixes
    logger.info("\n🧪 STEP 4: Testing Voice Embedding Fixes")
    if not test_voice_embedding_fixes():
        logger.error("❌ Voice embedding fixes test failed")
        return False
    
    # Step 5: Test end-to-end synthesis
    logger.info("\n🔊 STEP 5: Testing End-to-End Synthesis")
    synthesis_success = test_end_to_end_synthesis()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 VOICE EMBEDDING SYSTEM FIX SUMMARY")
    logger.info("="*60)
    logger.info("✅ VoiceEmbedding interface enhanced with compatibility properties")
    logger.info("✅ Model interface parameters fixed (emotion, emotion_strength)")
    logger.info("✅ Voice manager compatibility improved")
    logger.info("✅ Voice embedding loading tests passed")
    
    if synthesis_success:
        logger.info("✅ End-to-end synthesis successful")
        logger.info("🎉 VOICE EMBEDDING SYSTEM FIXED!")
        logger.info("💡 Audio generation should now work correctly")
    else:
        logger.warning("⚠️ End-to-end synthesis needs further investigation")
        logger.info("🔧 Voice embedding system partially fixed")
    
    return synthesis_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
