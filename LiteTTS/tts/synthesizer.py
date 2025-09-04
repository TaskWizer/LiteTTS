#!/usr/bin/env python3
"""
Main TTS synthesizer that orchestrates all TTS components
"""

from typing import Dict, List, Optional, Any, Callable
import logging
import time

from .engine import KokoroTTSEngine
from .emotion_controller import EmotionController
from .chunk_processor import ChunkProcessor
from ..models import AudioSegment, TTSConfiguration, TTSRequest
from ..nlp.processor import NLPProcessor
from ..nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode
from ..audio.processor import AudioProcessor
from ..audio.time_stretcher import TimeStretcher, TimeStretchConfig, StretchQuality
from ..ssml.processor import SSMLProcessor

logger = logging.getLogger(__name__)

class TTSSynthesizer:
    """Main TTS synthesizer that coordinates all components"""
    
    def __init__(self, config: TTSConfiguration):
        self.config = config
        
        # Initialize components
        self.engine = KokoroTTSEngine(config)
        self.emotion_controller = EmotionController()
        self.chunk_processor = ChunkProcessor(
            max_chunk_length=config.chunk_size,
            overlap_length=20
        )
        # Get global configuration for NLP processor
        try:
            from ..config import config as global_config
            config_dict = global_config.to_dict() if hasattr(global_config, 'to_dict') else {}
        except ImportError:
            # Fallback to loading config files directly
            import json
            try:
                # Try settings.json first, then config.json
                config_path = 'config/settings.json' if Path('config/settings.json').exists() else 'config.json'
                with open(config_path, 'r') as f:
                    config_dict = json.load(f)
            except Exception:
                config_dict = {}

        # Initialize both processors for compatibility and advanced features
        self.nlp_processor = NLPProcessor(config=config_dict)

        # Initialize UnifiedTextProcessor for advanced text processing features
        # This handles advanced abbreviations, currency, symbols, and custom phonetic dictionaries
        self.unified_processor = UnifiedTextProcessor()

        # Configure processing options based on config
        text_config = config_dict.get('text_processing', {})
        pronunciation_dict_config = config_dict.get('pronunciation_dictionary', {})
        symbol_config = config_dict.get('symbol_processing', {})
        espeak_config = symbol_config.get('espeak_enhanced_processing', {})
        interjection_config = config_dict.get('interjection_handling', {})
        voice_modulation_config = config_dict.get('voice_modulation', {})

        # Respect pronunciation_dictionary.enabled setting for ticker symbol processing
        pronunciation_dict_enabled = pronunciation_dict_config.get('enabled', False)
        ticker_processing_enabled = (pronunciation_dict_enabled and
                                   pronunciation_dict_config.get('ticker_symbol_processing', True))

        # Respect pronunciation_dictionary.enabled setting for proper name processing
        proper_name_enabled = (pronunciation_dict_enabled and
                             pronunciation_dict_config.get('proper_name_pronunciation', True))

        # Respect espeak_enhanced_processing.enabled setting
        espeak_enhanced_enabled = espeak_config.get('enabled', False)

        # Get individual configuration settings
        interjection_enabled = interjection_config.get('enabled', False)
        voice_modulation_enabled = voice_modulation_config.get('enabled', False)

        self.processing_options = ProcessingOptions(
            mode=ProcessingMode.ENHANCED,  # Use enhanced mode for production
            use_advanced_currency=text_config.get('natural_speech', True),
            use_enhanced_datetime=text_config.get('natural_speech', True),
            # Respect symbol_processing configuration
            use_advanced_symbols=symbol_config.get('enabled', False),
            # Respect espeak_enhanced_processing configuration for question mark fixes
            use_espeak_enhanced_symbols=espeak_enhanced_enabled and espeak_config.get('fix_question_mark_pronunciation', False),
            use_ticker_symbol_processing=ticker_processing_enabled,  # Respect config setting
            use_proper_name_pronunciation=proper_name_enabled,  # Respect config setting
            use_pronunciation_rules=text_config.get('pronunciation_fixes', True),
            # Respect interjection_handling configuration for hmm fixes
            use_interjection_fixes=interjection_enabled and interjection_config.get('fix_hmm_pronunciation', False),
            # Respect pronunciation_dictionary configuration
            use_clean_normalizer=pronunciation_dict_enabled,
            # Respect text_processing configuration for normalization
            normalize_text=text_config.get('enabled', False),
            # Respect pronunciation_dictionary configuration for homograph resolution
            resolve_homographs=pronunciation_dict_enabled and pronunciation_dict_config.get('use_context_awareness', True),
            # Respect pronunciation_dictionary configuration for phonetic processing
            process_phonetics=pronunciation_dict_enabled and pronunciation_dict_config.get('use_phonetic_spelling', True),
            handle_spell_functions=True
        )
        self.audio_processor = AudioProcessor()
        self.ssml_processor = SSMLProcessor(config.sample_rate)

        # Initialize time-stretching (beta feature)
        self.time_stretcher = self._initialize_time_stretcher(config)
        
        logger.info("TTS Synthesizer initialized")

    def _initialize_time_stretcher(self, config: TTSConfiguration) -> TimeStretcher:
        """Initialize time-stretching feature from configuration"""
        try:
            # Get time-stretching config from main config or global config
            stretch_config = getattr(config, 'time_stretching', {})

            # If not in TTSConfiguration, try to get from global config
            if not stretch_config:
                try:
                    from ..config import config as global_config
                    stretch_config = global_config.get('time_stretching', {})
                except ImportError:
                    stretch_config = {}

            # Also check text_processing.time_stretching_optimization
            if not stretch_config:
                try:
                    from ..config import config as global_config
                    text_processing = global_config.get('text_processing', {})
                    stretch_config = text_processing.get('time_stretching_optimization', {})
                except ImportError:
                    stretch_config = {}

            # Create time-stretch configuration with all new options
            time_stretch_config = TimeStretchConfig(
                enabled=stretch_config.get('enabled', False),
                compress_playback_rate=stretch_config.get('compress_playback_rate', 20),
                correction_quality=StretchQuality(stretch_config.get('correction_quality', 'medium')),
                max_rate=stretch_config.get('max_rate', 100),
                min_rate=stretch_config.get('min_rate', 10),
                auto_enable_threshold=stretch_config.get('auto_enable_threshold', 50),
                quality_fallback=stretch_config.get('quality_fallback', True),
                benchmark_mode=stretch_config.get('benchmark_mode', False)
            )

            return TimeStretcher(time_stretch_config)

        except Exception as e:
            logger.warning(f"Failed to initialize time-stretcher: {e}")
            # Return disabled time-stretcher as fallback
            return TimeStretcher(TimeStretchConfig(enabled=False))
    
    def synthesize(self, request: TTSRequest, 
                  progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> AudioSegment:
        """Main synthesis method"""
        logger.info(f"Starting synthesis: '{request.input[:50]}...' with voice '{request.voice}'")
        
        try:
            # Step 1: SSML processing and text preprocessing
            if progress_callback:
                progress_callback({'stage': 'ssml_processing', 'progress': 0.05})

            # Check if input contains SSML and process it
            plain_text, background_config, ssml_metadata = self.ssml_processor.process_ssml(request.input)

            if progress_callback:
                progress_callback({'stage': 'preprocessing', 'progress': 0.1})

            # Use UnifiedTextProcessor for advanced text processing
            # This handles TSLA→T-S-L-A, $5,678.89→currency words, ~$568.91→symbol words, custom phonetics
            try:
                processing_result = self.unified_processor.process_text(plain_text, self.processing_options)
                processed_text = processing_result.processed_text

                # Log processing details for debugging
                if processing_result.changes_made:
                    logger.info(f"Advanced text processing applied: {', '.join(processing_result.changes_made[:3])}")
                if processing_result.currency_enhancements > 0:
                    logger.debug(f"Currency processing: {processing_result.currency_enhancements} enhancements")
                if processing_result.datetime_enhancements > 0:
                    logger.debug(f"DateTime processing: {processing_result.datetime_enhancements} enhancements")

            except Exception as e:
                logger.warning(f"Advanced text processing failed, falling back to basic: {e}")
                # Fallback to basic NLP processor
                processed_text = self.nlp_processor.process_text(
                    plain_text,
                    request.normalization_options
                )
            
            # Step 2: Text chunking (if needed)
            if progress_callback:
                progress_callback({'stage': 'chunking', 'progress': 0.2})
            
            chunks = self.chunk_processor.chunk_text(processed_text)
            
            # Step 3: Voice and emotion preparation
            if progress_callback:
                progress_callback({'stage': 'voice_preparation', 'progress': 0.3})
            
            voice_embedding = self.engine.load_voice(request.voice)
            if not voice_embedding:
                raise RuntimeError(f"Failed to load voice: {request.voice}")
            
            # Apply emotion if specified
            emotion = getattr(request, 'emotion', None)
            emotion_strength = getattr(request, 'emotion_strength', 1.0)
            
            if emotion and emotion in self.emotion_controller.get_supported_emotions():
                voice_embedding.embedding_data = self.emotion_controller.apply_emotion(
                    voice_embedding.embedding_data, emotion, emotion_strength
                )
            
            # Step 4: Synthesis (with optional time-stretching optimization)
            if progress_callback:
                progress_callback({'stage': 'synthesis', 'progress': 0.4})

            # Check if time-stretching should be applied (API parameters override config)
            use_time_stretching = False
            if request.time_stretching_enabled is not None:
                # API parameter overrides config
                use_time_stretching = request.time_stretching_enabled
            else:
                # Use config-based decision
                use_time_stretching = self.time_stretcher.should_apply_stretching(len(processed_text))

            synthesis_speed = request.speed
            generation_start_time = None

            if use_time_stretching:
                # Create temporary time-stretcher with API parameters if provided
                active_time_stretcher = self.time_stretcher
                if request.time_stretching_rate is not None or request.time_stretching_quality is not None:
                    # Create temporary config with API overrides
                    from ..audio.time_stretcher import TimeStretchConfig, StretchQuality
                    temp_config = TimeStretchConfig(
                        enabled=True,
                        compress_playback_rate=request.time_stretching_rate or self.time_stretcher.config.compress_playback_rate,
                        correction_quality=StretchQuality(request.time_stretching_quality) if request.time_stretching_quality else self.time_stretcher.config.correction_quality,
                        max_rate=self.time_stretcher.config.max_rate,
                        min_rate=self.time_stretcher.config.min_rate,
                        auto_enable_threshold=self.time_stretcher.config.auto_enable_threshold,
                        quality_fallback=self.time_stretcher.config.quality_fallback,
                        benchmark_mode=self.time_stretcher.config.benchmark_mode
                    )
                    from ..audio.time_stretcher import TimeStretcher
                    active_time_stretcher = TimeStretcher(temp_config)

                # Generate at faster speed for time-stretching optimization
                generation_speed_multiplier = active_time_stretcher.get_generation_speed_multiplier()
                synthesis_speed = request.speed * generation_speed_multiplier
                generation_start_time = time.perf_counter()
                logger.debug(f"Time-stretching enabled: generating at {synthesis_speed:.2f}x speed")

            def synthesis_func(text: str, voice: str, speed: float, **kwargs):
                return self.engine.synthesize(text, voice, speed, emotion, emotion_strength)

            audio_segment = self.chunk_processor.process_chunks_to_audio(
                chunks, synthesis_func, request.voice, synthesis_speed
            )

            # Apply time-stretching correction if enabled
            if use_time_stretching:
                if progress_callback:
                    progress_callback({'stage': 'time_stretching', 'progress': 0.45})

                generation_time = time.perf_counter() - generation_start_time
                generation_speed_multiplier = active_time_stretcher.get_generation_speed_multiplier()

                audio_segment, stretch_metrics = active_time_stretcher.stretch_audio_to_normal_speed(
                    audio_segment, generation_speed_multiplier
                )

                # Update metrics
                stretch_metrics.generation_time = generation_time
                stretch_metrics.total_time = generation_time + stretch_metrics.stretch_time
                stretch_metrics.rtf_original = generation_time / stretch_metrics.original_duration
                stretch_metrics.rtf_stretched = stretch_metrics.total_time / stretch_metrics.stretched_duration

                logger.debug(f"Time-stretching metrics: RTF {stretch_metrics.rtf_original:.3f} → {stretch_metrics.rtf_stretched:.3f}")

            
            # Step 5: Background audio mixing (if SSML background specified)
            if background_config:
                if progress_callback:
                    progress_callback({'stage': 'background_mixing', 'progress': 0.75})

                audio_segment = self.ssml_processor.synthesize_with_background(
                    audio_segment, background_config
                )

            # Step 6: Post-processing
            if progress_callback:
                progress_callback({'stage': 'post_processing', 'progress': 0.8})

            # Apply volume adjustment
            if request.volume_multiplier != 1.0:
                audio_segment = audio_segment.adjust_volume(request.volume_multiplier)

            # Optimize for streaming if needed
            if request.stream:
                audio_segment = self.audio_processor.optimize_for_streaming(audio_segment)
            
            # Step 6: Format conversion
            if progress_callback:
                progress_callback({'stage': 'format_conversion', 'progress': 0.9})
            
            # The format conversion will be handled by the API layer
            # Here we just ensure the audio is in the right format
            audio_segment.format = request.response_format
            
            if progress_callback:
                progress_callback({'stage': 'complete', 'progress': 1.0})
            
            logger.info(f"Synthesis completed: {audio_segment.duration:.2f}s audio generated")
            return audio_segment
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            if progress_callback:
                progress_callback({'stage': 'error', 'progress': 0.0, 'error': str(e)})
            raise
    
    def synthesize_simple(self, text: str, voice: str = None, 
                         speed: float = 1.0, emotion: str = None) -> AudioSegment:
        """Simple synthesis method with minimal parameters"""
        if voice is None:
            voice = self.config.default_voice
        
        request = TTSRequest(
            input=text,
            voice=voice,
            speed=speed
        )
        
        # Add emotion if specified
        if emotion:
            request.emotion = emotion
            request.emotion_strength = 1.0
        
        return self.synthesize(request)
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voices"""
        return self.engine.get_available_voices()

    def get_time_stretching_metrics(self) -> Dict[str, Any]:
        """Get time-stretching performance metrics"""
        return self.time_stretcher.get_metrics_summary()

    def benchmark_time_stretching_rates(self, test_text: str, rates: List[int]) -> Dict[int, Any]:
        """Benchmark different time-stretching rates"""
        # Generate test audio
        test_audio = self.synthesize_simple(test_text)
        return self.time_stretcher.benchmark_rates(test_audio, rates)
    
    def get_supported_emotions(self) -> List[str]:
        """Get list of supported emotions"""
        return self.emotion_controller.get_supported_emotions()
    
    def get_voice_info(self, voice_name: str) -> Dict[str, Any]:
        """Get detailed information about a voice"""
        return self.engine.get_voice_info(voice_name)
    
    def get_emotion_info(self, emotion: str) -> Optional[Dict[str, Any]]:
        """Get information about an emotion"""
        return self.emotion_controller.get_emotion_info(emotion)
    
    def estimate_synthesis_time(self, text: str, voice: str) -> float:
        """Estimate synthesis time"""
        # Process text to get accurate length
        processed_text = self.nlp_processor.process_text(text)
        chunks = self.chunk_processor.chunk_text(processed_text)
        
        # Get base estimate from engine
        base_estimate = self.engine.estimate_synthesis_time(processed_text, voice)
        
        # Add chunk processing overhead
        chunk_estimate = self.chunk_processor.estimate_processing_time(chunks)
        
        return base_estimate + chunk_estimate
    
    def validate_request(self, request: TTSRequest) -> List[str]:
        """Validate synthesis request"""
        errors = []
        
        # Check voice availability
        if request.voice not in self.get_available_voices():
            errors.append(f"Voice '{request.voice}' not available")
        
        # Check emotion if specified
        emotion = getattr(request, 'emotion', None)
        if emotion and emotion not in self.get_supported_emotions():
            errors.append(f"Emotion '{emotion}' not supported")
        
        # Check emotion strength
        emotion_strength = getattr(request, 'emotion_strength', 1.0)
        is_valid, msg = self.emotion_controller.validate_emotion_strength(emotion_strength)
        if not is_valid:
            errors.append(msg)
        
        # Check text length
        if len(request.input) > self.config.max_text_length:
            errors.append(f"Text too long: {len(request.input)} > {self.config.max_text_length}")
        
        return errors    

    def preload_voice(self, voice_name: str) -> bool:
        """Preload a voice for faster synthesis"""
        return self.engine.preload_voice(voice_name)
    
    def preload_voices(self, voice_names: List[str]) -> Dict[str, bool]:
        """Preload multiple voices"""
        return self.engine.preload_voices(voice_names)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        engine_info = self.engine.get_engine_info()
        voice_system_status = self.engine.voice_manager.get_system_status()
        
        return {
            'engine': engine_info,
            'voices': voice_system_status,
            'emotions': {
                'supported_emotions': self.get_supported_emotions(),
                'total_emotions': len(self.get_supported_emotions())
            },
            'nlp': self.nlp_processor.get_processing_stats(),
            'configuration': {
                'max_text_length': self.config.max_text_length,
                'chunk_size': self.config.chunk_size,
                'sample_rate': self.config.sample_rate,
                'device': self.config.device
            }
        }
    
    def suggest_voice_for_text(self, text: str) -> str:
        """Suggest an appropriate voice based on text content"""
        # Simple heuristics for voice selection
        text_lower = text.lower()
        
        # Check for gender-specific content
        if any(word in text_lower for word in ['she', 'her', 'woman', 'girl', 'female']):
            # Prefer female voices
            female_voices = [v for v in self.get_available_voices() if v.startswith('af_')]
            if female_voices:
                return female_voices[0]  # Default to first available female voice
        
        if any(word in text_lower for word in ['he', 'him', 'man', 'boy', 'male']):
            # Prefer male voices
            male_voices = [v for v in self.get_available_voices() if v.startswith('am_')]
            if male_voices:
                return male_voices[0]  # Default to first available male voice
        
        # Check for content type
        if any(word in text_lower for word in ['professional', 'business', 'formal']):
            # Prefer professional voices
            professional_voices = ['af_alloy', 'am_liam', 'af_nicole']
            for voice in professional_voices:
                if voice in self.get_available_voices():
                    return voice
        
        if any(word in text_lower for word in ['story', 'tale', 'narrative']):
            # Prefer narrative voices
            narrative_voices = ['af_heart', 'am_puck']
            for voice in narrative_voices:
                if voice in self.get_available_voices():
                    return voice
        
        # Default to configured default voice
        return self.config.default_voice
    
    def suggest_emotion_for_text(self, text: str) -> str:
        """Suggest an appropriate emotion based on text content"""
        return self.emotion_controller.suggest_emotion_for_text(text)
    
    def create_synthesis_profile(self, name: str, voice: str, speed: float = 1.0,
                               emotion: str = None, emotion_strength: float = 1.0,
                               volume_multiplier: float = 1.0) -> Dict[str, Any]:
        """Create a reusable synthesis profile"""
        profile = {
            'name': name,
            'voice': voice,
            'speed': speed,
            'volume_multiplier': volume_multiplier
        }
        
        if emotion:
            profile['emotion'] = emotion
            profile['emotion_strength'] = emotion_strength
        
        # Validate profile
        test_request = TTSRequest(
            input="Test",
            voice=voice,
            speed=speed,
            volume_multiplier=volume_multiplier
        )
        
        if emotion:
            test_request.emotion = emotion
            test_request.emotion_strength = emotion_strength
        
        validation_errors = self.validate_request(test_request)
        if validation_errors:
            raise ValueError(f"Invalid profile: {validation_errors}")
        
        return profile
    
    def synthesize_with_profile(self, text: str, profile: Dict[str, Any]) -> AudioSegment:
        """Synthesize using a predefined profile"""
        request = TTSRequest(
            input=text,
            voice=profile['voice'],
            speed=profile.get('speed', 1.0),
            volume_multiplier=profile.get('volume_multiplier', 1.0)
        )
        
        if 'emotion' in profile:
            request.emotion = profile['emotion']
            request.emotion_strength = profile.get('emotion_strength', 1.0)
        
        return self.synthesize(request)
    
    def batch_synthesize(self, texts: List[str], voice: str, 
                        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> List[AudioSegment]:
        """Synthesize multiple texts in batch"""
        results = []
        total_texts = len(texts)
        
        for i, text in enumerate(texts):
            try:
                if progress_callback:
                    progress_callback({
                        'stage': 'batch_synthesis',
                        'progress': i / total_texts,
                        'current_item': i + 1,
                        'total_items': total_texts
                    })
                
                audio = self.synthesize_simple(text, voice)
                results.append(audio)
                
            except Exception as e:
                logger.error(f"Failed to synthesize text {i}: {e}")
                # Add empty audio segment as placeholder
                results.append(AudioSegment.silence(0.1))
        
        if progress_callback:
            progress_callback({
                'stage': 'batch_complete',
                'progress': 1.0,
                'total_items': total_texts,
                'successful_items': len([r for r in results if r.duration > 0.1])
            })
        
        return results
    
    def cleanup(self):
        """Clean up synthesizer resources"""
        logger.info("Cleaning up TTS synthesizer")
        
        if self.engine:
            self.engine.cleanup()
        
        logger.info("TTS synthesizer cleanup completed")
    
    def get_synthesis_stats(self) -> Dict[str, Any]:
        """Get synthesis statistics"""
        voice_stats = self.engine.voice_manager.metadata_manager.get_usage_summary()
        cache_stats = self.engine.voice_manager.cache.get_cache_stats()
        
        return {
            'voice_usage': voice_stats,
            'cache_performance': {
                'hit_rate': cache_stats['hit_rate'],
                'total_hits': cache_stats['cache_hits'],
                'total_misses': cache_stats['cache_misses']
            },
            'system_health': {
                'engine_loaded': self.engine.model_loaded,
                'available_voices': len(self.get_available_voices()),
                'cached_voices': cache_stats['cached_voices']
            }
        }