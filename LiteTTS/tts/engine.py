#!/usr/bin/env python3
"""
Kokoro TTS engine wrapper with ONNX runtime integration
"""

import torch
import onnxruntime as ort
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..models import VoiceEmbedding, TTSConfiguration
from ..audio.audio_segment import AudioSegment
from ..voice.manager import VoiceManager
from ..voice.blender import VoiceBlender, BlendConfig
from ..audio.processor import AudioProcessor
from ..audio.progressive_generator import ProgressiveAudioGenerator, ProgressiveGenerationConfig, GenerationMode
from ..audio.chunking import ChunkingConfig, ChunkingStrategy
from ..audio.voice_consistency import VoiceConsistencyManager, ConsistencyLevel
from ..monitoring.chunked_performance import ChunkedPerformanceMonitor, GenerationType
from ..metrics import performance_logger

logger = logging.getLogger(__name__)

class KokoroTTSEngine:
    """Main TTS engine using Kokoro model with ONNX runtime"""
    
    def __init__(self, config: TTSConfiguration):
        self.config = config
        self.device = config.device
        self.sample_rate = config.sample_rate
        
        # Initialize components
        self.voice_manager = VoiceManager()
        self.voice_blender = VoiceBlender(self.voice_manager)
        self.audio_processor = AudioProcessor()

        # Initialize chunked generation components
        self._initialize_chunked_generation()
        
        # ONNX session
        self.onnx_session = None
        self.tokenizer = None
        
        # Model state
        self.model_loaded = False
        self.available_voices = []
        
        # Initialize the engine
        self._initialize_engine()
    
    def _initialize_chunked_generation(self):
        """Initialize chunked generation components"""
        try:
            # Get chunked generation config
            chunked_config = getattr(self.config, 'chunked_generation', None)

            if chunked_config and chunked_config.enabled:
                # Create chunking configuration
                chunking_config = ChunkingConfig(
                    enabled=chunked_config.enabled,
                    strategy=ChunkingStrategy(chunked_config.strategy),
                    max_chunk_size=chunked_config.max_chunk_size,
                    min_chunk_size=chunked_config.min_chunk_size,
                    overlap_size=chunked_config.overlap_size,
                    respect_sentence_boundaries=chunked_config.respect_sentence_boundaries,
                    respect_paragraph_boundaries=chunked_config.respect_paragraph_boundaries,
                    preserve_punctuation=chunked_config.preserve_punctuation
                )

                # Create progressive generation configuration
                progressive_config = ProgressiveGenerationConfig(
                    mode=GenerationMode.CHUNKED,
                    chunking_config=chunking_config,
                    enable_voice_consistency=True,
                    enable_prosody_continuity=True
                )

                # Initialize components
                self.progressive_generator = ProgressiveAudioGenerator(self, progressive_config)
                self.voice_consistency_manager = VoiceConsistencyManager(ConsistencyLevel.ENHANCED)
                self.performance_monitor = ChunkedPerformanceMonitor()

                logger.info("Chunked generation initialized successfully")
            else:
                # Chunked generation disabled
                self.progressive_generator = None
                self.voice_consistency_manager = None
                self.performance_monitor = None

                logger.info("Chunked generation disabled")

        except Exception as e:
            logger.error(f"Failed to initialize chunked generation: {e}")
            # Fallback to disabled state
            self.progressive_generator = None
            self.voice_consistency_manager = None
            self.performance_monitor = None

    def _initialize_engine(self):
        """Initialize the TTS engine"""
        logger.info("Initializing Kokoro TTS engine")
        
        try:
            # Load ONNX model
            self._load_onnx_model()
            
            # Load tokenizer
            self._load_tokenizer()
            
            # Setup voice system
            self._setup_voice_system()
            
            self.model_loaded = True
            logger.info("Kokoro TTS engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.model_loaded = False
    
    def _load_onnx_model(self):
        """Load the ONNX model"""
        model_path = Path(self.config.model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"ONNX model not found: {model_path}")
        
        # Configure ONNX runtime providers
        providers = []
        if self.device == "cuda" and "CUDAExecutionProvider" in ort.get_available_providers():
            providers.append("CUDAExecutionProvider")
        providers.append("CPUExecutionProvider")
        
        # Create ONNX session
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        self.onnx_session = ort.InferenceSession(
            str(model_path),
            sess_options=session_options,
            providers=providers
        )
        
        logger.info(f"Loaded ONNX model from {model_path}")
        logger.info(f"Using providers: {self.onnx_session.get_providers()}")
    
    def _load_tokenizer(self):
        """Load the tokenizer"""
        try:
            # Try to load tokenizer from the same directory as the model
            model_dir = Path(self.config.model_path).parent
            tokenizer_path = model_dir / "tokenizer.json"
            
            if tokenizer_path.exists():
                import json
                with open(tokenizer_path, 'r') as f:
                    self.tokenizer = json.load(f)
                logger.info(f"Loaded tokenizer from {tokenizer_path}")
            else:
                # Use a simple character-based tokenizer as fallback
                self.tokenizer = self._create_simple_tokenizer()
                logger.warning("Using simple character-based tokenizer")
                
        except Exception as e:
            logger.error(f"Failed to load tokenizer: {e}")
            self.tokenizer = self._create_simple_tokenizer()
    
    def _create_simple_tokenizer(self) -> Dict[str, Any]:
        """Create a simple character-based tokenizer"""
        # Get character set from config if available
        from ..config import config
        if hasattr(config, 'tokenizer'):
            chars = config.tokenizer.character_set
            pad_token_id = config.tokenizer.pad_token_id
            unk_token_id = config.tokenizer.unk_token_id
            tokenizer_type = config.tokenizer.type
        else:
            # Fallback defaults
            chars = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?;:-'"
            pad_token_id = 0
            unk_token_id = 0
            tokenizer_type = "character"

        char_to_id = {char: i for i, char in enumerate(chars)}
        id_to_char = {i: char for i, char in enumerate(chars)}

        return {
            'type': tokenizer_type,
            'vocab_size': len(chars),
            'char_to_id': char_to_id,
            'id_to_char': id_to_char,
            'pad_token_id': pad_token_id,
            'unk_token_id': unk_token_id
        }
    
    def _setup_voice_system(self):
        """Setup the voice management system"""
        # Ensure default voices are available
        setup_results = self.voice_manager.setup_system(download_all=False)
        
        if not setup_results['success']:
            logger.warning("Voice system setup had issues, some voices may not be available")
        
        # Get available voices
        self.available_voices = self.voice_manager.get_available_voices()
        logger.info(f"Available voices: {self.available_voices}")
    
    def synthesize(self, text: str, voice: str, speed: float = 1.0, 
                  emotion: Optional[str] = None, emotion_strength: float = 1.0) -> AudioSegment:
        """Synthesize text to audio"""
        if not self.model_loaded:
            raise RuntimeError("TTS engine not properly initialized")
        
        if voice not in self.available_voices:
            raise ValueError(f"Voice '{voice}' not available. Available voices: {self.available_voices}")
        
        logger.debug(f"Synthesizing text: '{text[:50]}...' with voice: {voice}")
        
        try:
            # Get voice embedding
            voice_embedding = self.voice_manager.get_voice_embedding(voice)
            if not voice_embedding:
                raise RuntimeError(f"Failed to load voice embedding: {voice}")
            
            # CRITICAL FIX: Convert text to phonemes before tokenization
            # The tokenizer expects phonetic input, not raw text
            phonemes = self._text_to_phonemes(text)
            logger.debug(f"Converted text to phonemes: '{text}' -> '{phonemes}'")
            
            # Tokenize phonemes (not raw text)
            tokens = self._tokenize_text(phonemes)
            
            # Prepare inputs for ONNX model
            model_inputs = self._prepare_model_inputs(tokens, voice_embedding, speed, emotion, emotion_strength)
            
            # Run inference
            audio_data = self._run_inference(model_inputs)
            
            # Post-process audio
            audio_segment = self._post_process_audio(audio_data, speed)
            
            # Update voice usage statistics
            self.voice_manager.metadata_manager.update_voice_stats(
                voice, audio_segment.duration, success=True
            )
            
            logger.debug(f"Synthesis completed: {audio_segment.duration:.2f}s audio generated")
            return audio_segment
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            # Update error statistics
            self.voice_manager.metadata_manager.update_voice_stats(voice, 0.0, success=False)
            raise    

    def _tokenize_text(self, text: str) -> np.ndarray:
        """Tokenize input text"""
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided for tokenization")
            # Return a minimal token sequence for empty text
            return np.array([0], dtype=np.int64)  # Just the pad token

        if self.tokenizer['type'] == 'character':
            # Character-based tokenization
            char_to_id = self.tokenizer['char_to_id']
            unk_id = self.tokenizer['unk_token_id']

            token_ids = []
            for char in text:
                token_ids.append(char_to_id.get(char, unk_id))

            # Ensure we have at least one token
            if not token_ids:
                logger.warning("No valid tokens generated from text, using unknown token")
                token_ids = [unk_id]

            tokens = np.array(token_ids, dtype=np.int64)
            logger.debug(f"Tokenized '{text[:50]}...' to {len(tokens)} tokens")
            return tokens
        else:
            # Fallback to character-based tokenization for unknown types
            logger.warning(f"Unknown tokenizer type '{self.tokenizer['type']}', falling back to character-based")
            char_to_id = self.tokenizer.get('char_to_id', {})
            unk_id = self.tokenizer.get('unk_token_id', 0)

            token_ids = []
            for char in text:
                token_ids.append(char_to_id.get(char, unk_id))

            if not token_ids:
                logger.warning("No valid tokens generated from text, using unknown token")
                token_ids = [unk_id]

            tokens = np.array(token_ids, dtype=np.int64)
            logger.debug(f"Tokenized '{text[:50]}...' to {len(tokens)} tokens (fallback)")
            return tokens
    
    def _prepare_model_inputs(self, tokens: np.ndarray, voice_embedding: VoiceEmbedding,
                            speed: float, emotion: Optional[str] = None, emotion_strength: float = 1.0) -> Dict[str, np.ndarray]:
        """Prepare inputs for the ONNX model"""
        # Handle default emotion parameters
        if emotion is None:
            emotion = "neutral"
        if emotion_strength is None:
            emotion_strength = 1.0
            
        # Get voice embedding data
        voice_data = voice_embedding.embedding_data

        # Handle different voice data formats
        if hasattr(voice_data, 'numpy'):
            voice_data = voice_data.numpy()

        # Ensure voice data is the right shape for the model
        # Model expects style input with shape [1, 256]
        if voice_data.shape == (510, 256):
            # Use the first style vector (or could be averaged/selected differently)
            style_vector = voice_data[0:1, :]  # Shape: (1, 256)
        elif voice_data.shape == (256,):
            # Single style vector, add batch dimension
            style_vector = voice_data.reshape(1, 256)
        elif voice_data.shape == (1, 256):
            # Already correct shape
            style_vector = voice_data
        else:
            # Try to reshape to expected format
            logger.warning(f"Unexpected voice data shape: {voice_data.shape}, attempting to reshape")
            if voice_data.size >= 256:
                style_vector = voice_data.flatten()[:256].reshape(1, 256)
            else:
                raise ValueError(f"Voice data too small: {voice_data.shape}, need at least 256 elements")

        # Basic input preparation with correct input names for ONNX model
        inputs = {
            'input_ids': tokens.reshape(1, -1).astype(np.int64),  # Add batch dimension, ensure int64
            'style': style_vector.astype(np.float32),  # Ensure float32
            'speed': np.array([speed], dtype=np.float32)  # Shape: [1]
        }

        logger.debug(f"Model inputs prepared: input_ids shape={inputs['input_ids'].shape}, "
                    f"style shape={inputs['style'].shape}, speed shape={inputs['speed'].shape}")

        return inputs
    
    def _run_inference(self, model_inputs: Dict[str, np.ndarray]) -> np.ndarray:
        """Run ONNX model inference"""
        try:
            # Get input names from the model
            input_names = [input.name for input in self.onnx_session.get_inputs()]
            logger.debug(f"Model expects inputs: {input_names}")
            logger.debug(f"Provided inputs: {list(model_inputs.keys())}")

            # Prepare inputs for ONNX session
            onnx_inputs = {}
            missing_inputs = []

            for name in input_names:
                if name in model_inputs:
                    onnx_inputs[name] = model_inputs[name]
                    logger.debug(f"Input '{name}' shape: {model_inputs[name].shape}, dtype: {model_inputs[name].dtype}")
                else:
                    missing_inputs.append(name)
                    logger.warning(f"Missing required input: {name}")

            if missing_inputs:
                raise ValueError(f"Missing required model inputs: {missing_inputs}")

            # Run inference
            logger.debug("Running ONNX inference...")
            outputs = self.onnx_session.run(None, onnx_inputs)

            # Check output
            if not outputs or len(outputs) == 0:
                raise RuntimeError("ONNX model returned no outputs")

            audio_output = outputs[0]
            logger.debug(f"ONNX output shape: {audio_output.shape}, dtype: {audio_output.dtype}")

            # Validate output
            if audio_output.size == 0:
                raise RuntimeError("ONNX model returned empty audio output")

            return audio_output

        except Exception as e:
            logger.error(f"ONNX inference failed: {e}")
            logger.error(f"Model inputs were: {[(k, v.shape, v.dtype) for k, v in model_inputs.items()]}")
            raise
    
    def _post_process_audio(self, audio_data: np.ndarray, speed: float) -> AudioSegment:
        """Post-process the generated audio"""
        logger.debug(f"Post-processing audio: shape={audio_data.shape}, dtype={audio_data.dtype}")

        # Check for empty audio
        if audio_data.size == 0:
            raise ValueError("Cannot post-process empty audio data")

        # Ensure audio is in the right format
        if audio_data.ndim > 1:
            audio_data = audio_data.flatten()

        # Convert to float32 if needed
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Check for invalid values
        if np.any(np.isnan(audio_data)):
            logger.warning("Audio contains NaN values, replacing with zeros")
            audio_data = np.nan_to_num(audio_data, nan=0.0)

        if np.any(np.isinf(audio_data)):
            logger.warning("Audio contains infinite values, clipping")
            audio_data = np.clip(audio_data, -1.0, 1.0)

        # Apply speed adjustment if needed (simple time-stretching)
        if speed != 1.0:
            audio_data = self._apply_speed_adjustment(audio_data, speed)

        # Final validation of audio data
        if len(audio_data) == 0:
            raise ValueError("Audio data became empty after processing")

        # Create audio segment
        audio_segment = AudioSegment(
            audio_data=audio_data,
            sample_rate=self.sample_rate,
            format="wav"
        )

        # Validate the audio
        if not audio_segment.validate():
            logger.warning("Generated audio failed validation")
            # Try to provide more details about why validation failed
            logger.warning(f"Audio details: length={len(audio_data)}, "
                          f"sample_rate={self.sample_rate}, "
                          f"duration={len(audio_data)/self.sample_rate:.3f}s")

        logger.debug(f"Post-processing complete: {len(audio_data)} samples, "
                    f"{len(audio_data)/self.sample_rate:.3f}s duration")

        return audio_segment
    
    def _apply_speed_adjustment(self, audio_data: np.ndarray, speed: float) -> np.ndarray:
        """Apply speed adjustment to audio data"""
        if speed == 1.0:
            return audio_data

    def should_use_chunked_generation(self, text: str, streaming: bool = False) -> bool:
        """
        Determine if chunked generation should be used

        Args:
            text: Input text
            streaming: Whether streaming is requested

        Returns:
            True if chunked generation should be used
        """
        if not self.progressive_generator:
            return False

        # Get chunked generation config
        chunked_config = getattr(self.config, 'chunked_generation', None)
        if not chunked_config or not chunked_config.enabled:
            return False

        # Check if streaming is enabled for chunked generation
        if streaming and not chunked_config.enable_for_streaming:
            return False

        # Check minimum text length
        min_length = getattr(chunked_config, 'min_text_length_for_chunking', 100)
        if len(text) < min_length:
            return False

        return True

    async def synthesize_progressive(
        self,
        text: str,
        voice: str,
        response_format: str = "mp3",
        speed: float = 1.0,
        streaming: bool = True,
        generation_id: Optional[str] = None
    ):
        """
        Synthesize audio using progressive/chunked generation

        Args:
            text: Text to synthesize
            voice: Voice to use
            response_format: Audio format
            speed: Speech speed
            streaming: Whether to stream chunks
            generation_id: Optional generation ID

        Yields:
            Audio chunks as they become available
        """
        if not self.progressive_generator:
            raise ValueError("Progressive generation not available")

        # Start performance monitoring
        if self.performance_monitor:
            generation_type = GenerationType.STREAMING if streaming else GenerationType.CHUNKED
            self.performance_monitor.start_generation_tracking(
                generation_id or f"prog_{int(time.time() * 1000)}",
                generation_type,
                text,
                voice
            )

        # Use progressive generator
        async for chunk_result in self.progressive_generator.generate_progressive(
            text=text,
            voice=voice,
            response_format=response_format,
            speed=speed,
            generation_id=generation_id
        ):
            # Record chunk completion for monitoring
            if self.performance_monitor and generation_id:
                self.performance_monitor.record_chunk_completion(
                    generation_id,
                    chunk_result.chunk_id,
                    chunk_result.generation_time,
                    len(chunk_result.audio_data)
                )

            yield chunk_result

        # Complete performance tracking
        if self.performance_monitor and generation_id:
            total_audio_size = sum(len(chunk.audio_data) for chunk in [chunk_result])
            estimated_duration = chunk_result.duration if 'chunk_result' in locals() else 1.0

            self.performance_monitor.complete_generation_tracking(
                generation_id,
                total_audio_size,
                estimated_duration
            )

    def get_chunked_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about chunked generation performance"""
        if not self.performance_monitor:
            return {"error": "Performance monitoring not available"}

        return {
            "real_time_stats": self.performance_monitor.get_real_time_stats(),
            "active_generations": len(self.performance_monitor.active_generations),
            "total_metrics": len(self.performance_monitor.metrics_history)
        }

    def get_performance_comparison(self, hours: Optional[float] = None) -> Dict[str, Any]:
        """Get performance comparison between generation types"""
        if not self.performance_monitor:
            return {"error": "Performance monitoring not available"}

        comparison = self.performance_monitor.get_performance_comparison(hours)

        return {
            "comparison_report": {
                "avg_rtf": comparison.avg_rtf_comparison,
                "avg_latency": comparison.avg_latency_comparison,
                "avg_memory": comparison.avg_memory_comparison,
                "time_to_first_audio": comparison.time_to_first_audio_comparison,
                "perceived_responsiveness": comparison.perceived_responsiveness
            },
            "sample_counts": {
                "standard": len(comparison.standard_metrics),
                "chunked": len(comparison.chunked_metrics),
                "streaming": len(comparison.streaming_metrics)
            }
        }
        
        # Simple linear interpolation for speed adjustment
        original_length = len(audio_data)
        new_length = int(original_length / speed)
        
        # Create new time indices
        old_indices = np.linspace(0, original_length - 1, new_length)
        
        # Interpolate
        adjusted_audio = np.interp(old_indices, np.arange(original_length), audio_data)
        
        return adjusted_audio.astype(np.float32)
    
    def load_voice(self, voice_name: str) -> VoiceEmbedding:
        """Load a voice embedding"""
        return self.voice_manager.get_voice_embedding(voice_name)
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voices"""
        return self.available_voices.copy()
    
    def is_voice_available(self, voice_name: str) -> bool:
        """Check if a voice is available"""
        return voice_name in self.available_voices
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information"""
        return {
            'model_loaded': self.model_loaded,
            'device': self.device,
            'sample_rate': self.sample_rate,
            'available_voices': self.available_voices,
            'voice_count': len(self.available_voices),
            'onnx_providers': self.onnx_session.get_providers() if self.onnx_session else [],
            'tokenizer_type': self.tokenizer['type'] if self.tokenizer else None,
            'vocab_size': self.tokenizer['vocab_size'] if self.tokenizer else 0
        }
    
    def preload_voice(self, voice_name: str) -> bool:
        """Preload a voice into cache"""
        return self.voice_manager.preload_voice(voice_name)
    
    def preload_voices(self, voice_names: List[str]) -> Dict[str, bool]:
        """Preload multiple voices into cache"""
        return self.voice_manager.preload_voices(voice_names)
    
    def get_voice_info(self, voice_name: str) -> Dict[str, Any]:
        """Get detailed information about a voice"""
        return self.voice_manager.get_voice_info(voice_name)
    
    def estimate_synthesis_time(self, text: str, voice: str) -> float:
        """Estimate synthesis time for given text"""
        # Rough estimation based on text length and model performance
        char_count = len(text)

        # Get configurable values
        from ..config import config
        if hasattr(config, 'performance'):
            base_time_per_char = config.performance.base_time_per_char
            cache_multiplier = config.performance.cache_multiplier
            no_cache_multiplier = config.performance.no_cache_multiplier
            cpu_multiplier = config.performance.cpu_device_multiplier
            cuda_multiplier = config.performance.cuda_device_multiplier
            min_time = config.performance.min_synthesis_time
        else:
            # Fallback defaults
            base_time_per_char = 0.01
            cache_multiplier = 1.0
            no_cache_multiplier = 1.5
            cpu_multiplier = 2.0
            cuda_multiplier = 1.0
            min_time = 0.1

        # Adjust based on voice availability (cached vs not cached)
        if self.voice_manager.is_voice_cached(voice):
            voice_multiplier = cache_multiplier
        else:
            voice_multiplier = no_cache_multiplier

        # Device multiplier
        device_multiplier = cuda_multiplier if self.device == "cuda" else cpu_multiplier

        estimated_time = char_count * base_time_per_char * voice_multiplier * device_multiplier

        return max(estimated_time, min_time)

    def synthesize_with_blended_voice(self, text: str, blend_config: BlendConfig,
                                    speed: float = 1.0, emotion: Optional[str] = None,
                                    emotion_strength: float = 1.0) -> AudioSegment:
        """Synthesize text using a blended voice"""
        if not self.model_loaded:
            raise RuntimeError("TTS engine not properly initialized")

        logger.debug(f"Synthesizing with blended voice: {[v[0] for v in blend_config.voices]}")

        try:
            # Create blended voice
            blended_voice = self.voice_blender.blend_voices(blend_config)
            if not blended_voice:
                raise RuntimeError("Failed to create blended voice")

            # CRITICAL FIX: Convert text to phonemes before tokenization
            # The tokenizer expects phonetic input, not raw text
            phonemes = self._text_to_phonemes(text)
            logger.debug(f"Converted text to phonemes: '{text}' -> '{phonemes}'")
            
            # Tokenize phonemes (not raw text)
            tokens = self._tokenize_text(phonemes)

            # Prepare inputs for ONNX model using blended voice
            model_inputs = self._prepare_model_inputs(tokens, blended_voice, speed, emotion, emotion_strength)

            # Run inference
            audio_data = self._run_inference(model_inputs)

            # Post-process audio
            audio_segment = self._post_process_audio(audio_data, speed)

            logger.debug(f"Blended voice synthesis completed: {audio_segment.duration:.2f}s audio generated")
            return audio_segment

        except Exception as e:
            logger.error(f"Blended voice synthesis failed: {e}")
            raise

    def create_voice_blend(self, voices_and_weights: List[Tuple[str, float]],
                          blend_method: str = "weighted_average") -> Optional[VoiceEmbedding]:
        """Create a blended voice from multiple voices"""
        try:
            blend_config = BlendConfig(
                voices=voices_and_weights,
                blend_method=blend_method,
                normalize_weights=True,
                preserve_energy=True
            )

            return self.voice_blender.blend_voices(blend_config)

        except Exception as e:
            logger.error(f"Voice blend creation failed: {e}")
            return None

    def get_blend_presets(self) -> List[str]:
        """Get available voice blend presets"""
        return ["warm_friendly", "professional_calm", "energetic_mix"]

    def synthesize_with_preset_blend(self, text: str, preset_name: str,
                                   speed: float = 1.0, emotion: Optional[str] = None,
                                   emotion_strength: float = 1.0) -> AudioSegment:
        """Synthesize text using a preset voice blend"""
        blend_config = self.voice_blender.create_preset_blend(preset_name)
        if not blend_config:
            raise ValueError(f"Unknown preset: {preset_name}")

        return self.synthesize_with_blended_voice(text, blend_config, speed, emotion, emotion_strength)

    def synthesize_batch(self, requests: List[Dict[str, Any]], max_workers: int = None) -> List[AudioSegment]:
        """
        Synthesize multiple TTS requests in parallel for improved throughput

        Args:
            requests: List of synthesis requests, each containing:
                     {'text': str, 'voice': str, 'speed': float, 'emotion': str, 'emotion_strength': float}
            max_workers: Maximum number of worker threads (auto-detected if None)

        Returns:
            List of AudioSegment objects in the same order as requests
        """
        if not requests:
            return []

        if max_workers is None:
            # Auto-detect optimal worker count based on CPU cores
            import os
            cpu_count = os.cpu_count() or 4
            max_workers = min(len(requests), max(2, cpu_count // 2))

        logger.info(f"Processing batch of {len(requests)} requests with {max_workers} workers")

        results = [None] * len(requests)  # Preserve order

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_index = {}
            for i, request in enumerate(requests):
                future = executor.submit(self._synthesize_single_request, request)
                future_to_index[future] = i

            # Collect results as they complete
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    logger.error(f"Batch request {index} failed: {e}")
                    # Create error audio segment
                    results[index] = AudioSegment(
                        audio_data=np.zeros(1024, dtype=np.float32),
                        sample_rate=self.sample_rate,
                        metadata={'error': str(e), 'request_index': index}
                    )

        return results

    def _synthesize_single_request(self, request: Dict[str, Any]) -> AudioSegment:
        """Helper method to synthesize a single request for batch processing"""
        text = request.get('text', '')
        voice = request.get('voice', self.config.default_voice)
        speed = request.get('speed', 1.0)
        emotion = request.get('emotion', None)
        emotion_strength = request.get('emotion_strength', 1.0)

        return self.synthesize(text, voice, speed, emotion, emotion_strength)

    def synthesize_streaming_batch(self, requests: List[Dict[str, Any]],
                                 chunk_callback=None, max_workers: int = None) -> List[AudioSegment]:
        """
        Synthesize batch with streaming callback for real-time processing

        Args:
            requests: List of synthesis requests
            chunk_callback: Callback function called when each request completes
            max_workers: Maximum number of worker threads

        Returns:
            List of completed AudioSegment objects
        """
        if not requests:
            return []

        if max_workers is None:
            import os
            cpu_count = os.cpu_count() or 4
            max_workers = min(len(requests), max(2, cpu_count // 2))

        logger.info(f"Processing streaming batch of {len(requests)} requests")

        results = [None] * len(requests)
        completed_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {}
            for i, request in enumerate(requests):
                future = executor.submit(self._synthesize_single_request, request)
                future_to_index[future] = i

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results[index] = result
                    completed_count += 1

                    # Call streaming callback if provided
                    if chunk_callback:
                        chunk_callback(result, index, completed_count, len(requests))

                except Exception as e:
                    logger.error(f"Streaming batch request {index} failed: {e}")
                    error_segment = AudioSegment(
                        audio_data=np.zeros(1024, dtype=np.float32),
                        sample_rate=self.sample_rate,
                        metadata={'error': str(e), 'request_index': index}
                    )
                    results[index] = error_segment
                    completed_count += 1

                    if chunk_callback:
                        chunk_callback(error_segment, index, completed_count, len(requests))

        return results

    def synthesize_with_pipeline_parallelism(self, text: str, voice: str, speed: float = 1.0,
                                           emotion: Optional[str] = None,
                                           emotion_strength: float = 1.0) -> AudioSegment:
        """
        Synthesize with pipeline parallelism for maximum performance
        Overlaps phonemization, inference, and audio processing stages
        """
        try:
            from concurrent.futures import ThreadPoolExecutor
            import queue

            # Pipeline stages
            phoneme_queue = queue.Queue(maxsize=2)
            inference_queue = queue.Queue(maxsize=2)

            def phonemization_stage():
                """Stage 1: Text to phonemes"""
                try:
                    # Apply model optimizations for phonemization
                    from LiteTTS.performance.model_optimizer import get_model_optimizer
                    model_optimizer = get_model_optimizer()

                    # Check cache first
                    cached_phonemes = model_optimizer.optimize_phoneme_processing(text, voice)
                    if cached_phonemes:
                        phoneme_queue.put(cached_phonemes)
                        return

                    # Phonemize text
                    phonemes = self.phonemizer.phonemize(text)

                    # Cache result
                    model_optimizer.cache_phoneme_result(text, voice, phonemes)

                    phoneme_queue.put(phonemes)

                except Exception as e:
                    phoneme_queue.put(e)

            def inference_stage():
                """Stage 2: Phonemes to mel-spectrogram"""
                try:
                    phonemes = phoneme_queue.get(timeout=5.0)
                    if isinstance(phonemes, Exception):
                        raise phonemes

                    # Convert to tokens
                    tokens = self.phonemizer.phonemes_to_tokens(phonemes)

                    # Get voice embedding
                    voice_embedding = self.voice_manager.get_voice_embedding(voice)

                    # Apply model optimizations
                    from LiteTTS.performance.model_optimizer import get_model_optimizer
                    model_optimizer = get_model_optimizer()

                    # Optimize inputs
                    inputs = model_optimizer.optimize_input_preparation(
                        tokens, voice_embedding.data, speed
                    )

                    # Run inference
                    outputs = self.model.run(None, inputs)
                    mel_spectrogram = outputs[0]

                    inference_queue.put(mel_spectrogram)

                except Exception as e:
                    inference_queue.put(e)

            def audio_processing_stage():
                """Stage 3: Mel-spectrogram to audio"""
                try:
                    mel_spectrogram = inference_queue.get(timeout=10.0)
                    if isinstance(mel_spectrogram, Exception):
                        raise mel_spectrogram

                    # Convert to audio
                    audio_data = self.vocoder.mel_to_audio(mel_spectrogram)

                    # Apply post-processing
                    if emotion and emotion != "neutral":
                        audio_data = self._apply_emotion_processing(audio_data, emotion, emotion_strength)

                    return AudioSegment(
                        audio_data=audio_data,
                        sample_rate=self.sample_rate,
                        metadata={
                            'voice': voice,
                            'speed': speed,
                            'emotion': emotion,
                            'emotion_strength': emotion_strength,
                            'pipeline_mode': 'parallel'
                        }
                    )

                except Exception as e:
                    raise e

            # Execute pipeline stages in parallel
            with ThreadPoolExecutor(max_workers=3) as executor:
                # Start all stages
                phoneme_future = executor.submit(phonemization_stage)
                inference_future = executor.submit(inference_stage)
                audio_future = executor.submit(audio_processing_stage)

                # Wait for completion
                result = audio_future.result(timeout=15.0)

                return result

        except Exception as e:
            logger.error(f"Pipeline parallelism failed, falling back to sequential: {e}")
            # Fallback to regular synthesis
            return self.synthesize(text, voice, speed, emotion, emotion_strength)

    def cleanup(self):
        """Clean up engine resources"""
        logger.info("Cleaning up TTS engine")
        
        if self.onnx_session:
            # ONNX sessions don't need explicit cleanup, but we can clear the reference
            self.onnx_session = None
        
        if self.voice_manager:
            self.voice_manager.cleanup_system()
        
        self.model_loaded = False
        logger.info("TTS engine cleanup completed")

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
        """Fallback phonemization using only vocabulary-compatible characters"""
        # Simple mapping for basic English sounds using available characters
        phoneme_map = {
            'hello': 'hɛlo',
            'world': 'wɔrld',
            'test': 'tɛst',
            'testing': 'tɛstɪŋ',
            'one': 'wʌn',
            'two': 'tu',
            'three': 'θri',
            'the': 'ðɛ',
            'quick': 'kwɪk',
            'brown': 'braʊn',
            'fox': 'fɑks',
            'jumps': 'dʒʌmps',
            'over': 'ovɛr',
            'lazy': 'leɪzi',
            'dog': 'dɔɡ',
            'good': 'ɡʊd',
            'morning': 'mɔrnɪŋ',
            'how': 'haʊ',
            'are': 'ɑr',
            'you': 'ju'
        }

        words = text.lower().split()
        phoneme_words = []

        for word in words:
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalpha())
            if clean_word in phoneme_map:
                phoneme_words.append(phoneme_map[clean_word])
            else:
                # Use simple character mapping for unknown words
                phoneme_words.append(self._char_to_vocab_phoneme(clean_word))

        result = ' '.join(phoneme_words)
        logger.debug(f"Fallback phonemization: '{text}' -> '{result}'")
        return result

    def _char_to_vocab_phoneme(self, word: str) -> str:
        """Map characters to phonemes that exist in tokenizer vocabulary"""
        # Only use characters confirmed to be in the vocabulary
        char_map = {
            'a': 'æ', 'e': 'ɛ', 'i': 'ɪ', 'o': 'ɔ', 'u': 'ʌ',
            'b': 'b', 'c': 'k', 'd': 'd', 'f': 'f', 'g': 'ɡ',
            'h': 'h', 'j': 'dʒ', 'k': 'k', 'l': 'l', 'm': 'm',
            'n': 'n', 'p': 'p', 'q': 'k', 'r': 'r', 's': 's',
            't': 't', 'v': 'v', 'w': 'w', 'x': 'ks', 'y': 'j', 'z': 'z'
        }
        
        result = ''.join(char_map.get(c, c) for c in word.lower())
        return result if result else word.lower()

    def _char_to_vocab_phoneme(self, word: str) -> str:
        """Map characters to phonemes that exist in tokenizer vocabulary"""
        # Only use characters confirmed to be in the vocabulary
        char_map = {
            'a': 'æ', 'e': 'ɛ', 'i': 'ɪ', 'o': 'ɔ', 'u': 'ʌ',
            'b': 'b', 'c': 'k', 'd': 'd', 'f': 'f', 'g': 'ɡ',
            'h': 'h', 'j': 'dʒ', 'k': 'k', 'l': 'l', 'm': 'm',
            'n': 'n', 'p': 'p', 'q': 'k', 'r': 'r', 's': 's',
            't': 't', 'v': 'v', 'w': 'w', 'x': 'ks', 'y': 'j', 'z': 'z'
        }

        result = ''.join(char_map.get(c, c) for c in word.lower())
        return result if result else word.lower()