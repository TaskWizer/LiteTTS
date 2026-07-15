#!/usr/bin/env python3
"""
Patches for kokoro_onnx library to fix tensor rank issues
and replace the broken TTS.cpp phonemizer with misaki
"""

import numpy as np
import logging
import re

logger = logging.getLogger(__name__)

# Global misaki G2P instance (lazy initialized)
_misaki_g2p = None

# Global pre-processor instances for pronunciation fixes (lazy initialized)
_symbol_processor_instance = None
_text_normalizer_instance = None

def _get_symbol_processor():
    """Lazy load symbol processor"""
    global _symbol_processor_instance
    if _symbol_processor_instance is None:
        try:
            from LiteTTS.nlp.advanced_symbol_processor import AdvancedSymbolProcessor
            _symbol_processor_instance = AdvancedSymbolProcessor()
        except ImportError:
            pass
    return _symbol_processor_instance

def _get_text_normalizer():
    """Lazy load text normalizer"""
    global _text_normalizer_instance
    if _text_normalizer_instance is None:
        try:
            from LiteTTS.nlp.text_normalizer import TextNormalizer
            _text_normalizer_instance = TextNormalizer()
        except ImportError:
            pass
    return _text_normalizer_instance

def _get_misaki_g2p():
    """Get or create the misaki G2P instance"""
    global _misaki_g2p
    if _misaki_g2p is None:
        try:
            from misaki import en
            # Use British=False for American English (Kokoro default)
            # trf=False uses rule-based mode (faster, no neural overhead)
            _misaki_g2p = en.G2P(trf=False, british=False)
            logger.info("✅ Misaki G2P initialized for phonemizer patch")
        except ImportError as e:
            logger.warning(f"⚠️ Misaki not available for phonemizer patch: {e}")
            return None
    return _misaki_g2p

def patch_kokoro_onnx():
    """Apply patches to kokoro_onnx library to fix tensor rank issues and optimize performance"""
    try:
        import kokoro_onnx
        import onnxruntime as ort
        
        # Store original __init__ method to add ONNX optimizations
        original_init = kokoro_onnx.Kokoro.__init__
        
        def patched_init(self, model_path, voices_path):
            """Patched __init__ with aggressive ONNX Runtime optimizations"""
            # Apply model-level optimizations
            try:
                from LiteTTS.performance.model_optimizer import get_model_optimizer
                model_optimizer = get_model_optimizer()

                # Optimize model path selection
                model_path = model_optimizer.optimize_model_loading(model_path)

                # Get optimized session options
                optimization_config = model_optimizer.get_optimized_session_options()
                session_options = optimization_config.get("session_options")

                if session_options is None:
                    # Fallback to manual session options
                    session_options = ort.SessionOptions()
                    session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                    session_options.execution_mode = ort.ExecutionMode.ORT_PARALLEL

            except ImportError:
                # Fallback if model optimizer not available
                session_options = ort.SessionOptions()
                session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                session_options.execution_mode = ort.ExecutionMode.ORT_PARALLEL

            # Optimize thread usage with dynamic CPU allocation
            enable_aggressive = False  # Default to conservative mode
            try:
                from LiteTTS.performance.dynamic_allocator import get_dynamic_allocator
                dynamic_allocator = get_dynamic_allocator()

                # Try to apply dynamic allocation first
                if dynamic_allocator.apply_to_onnx_session_options(session_options):
                    logger.info("Applied dynamic CPU allocation to ONNX session")
                    # Check if dynamic allocator supports aggressive mode
                    enable_aggressive = getattr(dynamic_allocator, 'aggressive_mode', False)
                else:
                    # Fallback to static CPU optimizer
                    from LiteTTS.performance.cpu_optimizer import get_cpu_optimizer
                    cpu_optimizer = get_cpu_optimizer()

                    # Check thermal status for aggressive optimization safety
                    thermal_status = cpu_optimizer.get_thermal_status()
                    enable_aggressive = thermal_status["safe_for_aggressive"]

                    settings = cpu_optimizer.get_recommended_settings(aggressive=enable_aggressive)

                    session_options.inter_op_num_threads = settings["onnx_inter_op_threads"]
                    session_options.intra_op_num_threads = settings["onnx_intra_op_threads"]

                # Additional aggressive optimizations
                if enable_aggressive:
                    session_options.execution_mode = ort.ExecutionMode.ORT_PARALLEL
                    session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

                    # Use centralized ONNX configuration to avoid duplicate warnings
                    try:
                        from LiteTTS.utils.onnx_config_manager import get_onnx_config_manager
                        onnx_manager = get_onnx_config_manager()

                        cpu_info = {
                            "model_name": cpu_optimizer.cpu_info.model_name,
                            "supports_avx2": cpu_optimizer.cpu_info.supports_avx2
                        }
                        onnx_manager.apply_cpu_optimizations(session_options, "kokoro_patches", cpu_info)

                    except ImportError:
                        logger.debug("ONNX config manager not available, skipping advanced optimizations")

                    mode = "aggressive" if enable_aggressive else "conservative"
                    temp = thermal_status.get("temperature", 0)
                    logger.info(f"Applied {mode} CPU-optimized ONNX settings: "
                              f"inter_op={settings['onnx_inter_op_threads']}, "
                              f"intra_op={settings['onnx_intra_op_threads']}, "
                              f"temp={temp:.1f}°C")

            except ImportError:
                # Fallback to aggressive manual detection
                import os
                cpu_count = os.cpu_count() or 4

                if cpu_count >= 16:
                    # Aggressive settings for high-core CPUs
                    session_options.inter_op_num_threads = min(8, cpu_count // 2)
                    session_options.intra_op_num_threads = min(18, cpu_count - 2)
                elif cpu_count >= 8:
                    session_options.inter_op_num_threads = min(6, cpu_count // 2)
                    session_options.intra_op_num_threads = min(12, int(cpu_count * 0.9))
                else:
                    session_options.inter_op_num_threads = min(3, cpu_count // 2)
                    session_options.intra_op_num_threads = min(6, cpu_count - 1)

            # Enable memory pattern optimization
            session_options.enable_mem_pattern = True
            session_options.enable_cpu_mem_arena = True

            # Disable memory growth for consistent performance
            session_options.enable_mem_reuse = True

            # Store session options for use in model loading
            self._session_options = session_options

            # Call original init
            original_init(self, model_path, voices_path)

            # Perform model warm-up for optimal performance
            try:
                if hasattr(self, 'voices') and model_optimizer:
                    # Get first available voice for warm-up
                    voice_names = list(self.voices.keys())
                    if voice_names:
                        first_voice = self.voices[voice_names[0]]
                        model_optimizer.warm_up_model(self.sess, first_voice)
            except Exception as e:
                logger.warning(f"Model warm-up failed: {e}")
        
        # Store original _create_audio method
        original_create_audio = kokoro_onnx.Kokoro._create_audio

        # Note: MAX_PHONEME_LENGTH is kept at kokoro's default 510
        # Voice vectors are sized for 510 phonemes, so we keep chunks small (30 chars)
        # to ensure phoneme expansion stays under the limit

        def patched_create_audio(self, phonemes, voice, speed):
            """Patched version of _create_audio with aggressive performance optimizations"""
            log = logging.getLogger('kokoro_onnx')
            log.debug(f"Phonemes: {phonemes}")

            # Apply model-level optimizations
            try:
                from LiteTTS.performance.model_optimizer import get_model_optimizer
                model_optimizer = get_model_optimizer()

                # Get text length optimizations
                text_length = len(phonemes) if isinstance(phonemes, str) else len(str(phonemes))
                optimizations = model_optimizer.optimize_for_text_length(text_length)

                # Use optimized phoneme length limit
                MAX_PHONEME_LENGTH = model_optimizer.config.max_phoneme_duration or 510

            except ImportError:
                MAX_PHONEME_LENGTH = 510
                optimizations = {}

            if len(phonemes) > MAX_PHONEME_LENGTH:
                log.warning(f"Phonemes are too long, truncating to {MAX_PHONEME_LENGTH} phonemes")
            phonemes = phonemes[:MAX_PHONEME_LENGTH]
            
            import time
            start_t = time.time()
            tokens = np.array(self.tokenizer.tokenize(phonemes), dtype=np.int64)
            assert len(tokens) <= MAX_PHONEME_LENGTH, (
                f"Context length is {MAX_PHONEME_LENGTH}, but leave room for the pad token 0 at the start & end"
            )

            # Select the appropriate style vector with bounds checking
            token_length = len(tokens)
            voice_size = len(voice)

            # Ensure we don't exceed voice vector bounds
            if token_length >= voice_size:
                logger.warning(f"Token length {token_length} exceeds voice vector size {voice_size}, using last available index")
                style_vector = voice[voice_size - 1]  # Use the last available style vector
            else:
                style_vector = voice[token_length]
            
            # FIX: Ensure style vector has correct shape [1, 256] for ONNX model
            if style_vector.ndim == 1:
                style_vector = style_vector.reshape(1, -1)  # Add batch dimension
            
            tokens = [[0, *tokens, 0]]
            
            # Optimize input preparation
            if "input_ids" in [i.name for i in self.sess.get_inputs()]:
                # Newer export versions
                inputs = {
                    "input_ids": np.array(tokens, dtype=np.int64),
                    "style": style_vector.astype(np.float32),
                    "speed": np.array([speed], dtype=np.float32),
                }
            else:
                inputs = {
                    "tokens": np.array(tokens, dtype=np.int64),
                    "style": style_vector.astype(np.float32),
                    "speed": np.array([speed], dtype=np.float32),
                }

            # Run inference with optimized session
            audio = self.sess.run(None, inputs)[0]
            
            # Ensure audio is properly flattened for quantized models
            if audio.ndim > 1:
                audio = audio.flatten()
            
            # Ensure audio is contiguous in memory for better performance
            if not audio.flags['C_CONTIGUOUS']:
                audio = np.ascontiguousarray(audio)
                
            SAMPLE_RATE = 24000  # From kokoro_onnx constants
            audio_duration = len(audio) / SAMPLE_RATE
            create_duration = time.time() - start_t
            rtf = create_duration / audio_duration
            log.debug(
                f"Created audio in length of {audio_duration:.2f}s for {len(phonemes)} phonemes in {create_duration:.2f}s (RTF: {rtf:.2f})"
            )
            return audio, SAMPLE_RATE
        
        # Apply the patches
        kokoro_onnx.Kokoro.__init__ = patched_init
        kokoro_onnx.Kokoro._create_audio = patched_create_audio
        
        logger.info("✅ Applied kokoro_onnx performance optimization patches")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to apply kokoro_onnx patches: {e}")
        return False

def patch_kokoro_onnx_phonemizer():
    """Patch kokoro_onnx to use misaki instead of the broken TTS.cpp phonemizer

    This replaces the rule-based TTS.cpp phonemizer (which has broken vocabulary
    for common English patterns like -tion, -sion, etc.) with misaki's neural G2P.

    If text already contains IPA phoneme characters (ʃ, ʒ, etc.), skip phonemization
    and use the existing phonemes directly since they came from phonetic dictionaries.
    """
    try:
        import kokoro_onnx

        # Characters that indicate text is already phonemized with IPA
        IPA_CHARS = set('ʃʒʔʜʢʡɕɧɑɐɒæβɔɕçɖðʤəɚɛɜɟɡɥɨɪʝɯɰŋɳɲɴøɸθœɹɾɻʁɽʂʃʈʧʊʋʌɣɤχʎʒθðŋɱ')

        def contains_ipa(text: str) -> bool:
            """Check if text contains IPA phoneme characters"""
            return any(c in IPA_CHARS for c in text)

        def _preprocess_for_misaki(text: str) -> str:
            """Pre-process text before misaki phonemization to fix known issues"""
            original_text = text
            logger.info(f"_preprocess_for_misaki INPUT: '{text[:60]}...'")

            # Fix JSON → Jason FIRST (pronounce as word, not spell out)
            # This must happen before any other processing
            # Handle all case variations: JSON, Jason, json, JASON
            import re
            if re.search(r'\bJSON\b', text, re.IGNORECASE):
                text = re.sub(r'\bJSON\b', 'Jason', text, flags=re.IGNORECASE)
                logger.info(f"Fixed JSON -> Jason in: '{text[:50]}...'")

            # Fix C# programming language - "C sharp", not "C hash"
            # NOTE: # is NOT a word char, so use (?!\w) instead of \b at end
            if re.search(r'\bC#(?!\w)', text, re.IGNORECASE):
                text = re.sub(r'\bC#(?!\w)', 'C sharp', text, flags=re.IGNORECASE)
                logger.info(f"Fixed C# -> C sharp in: '{text[:50]}...'")

            # ALSO fix "C hash" -> "C sharp" (in case # was already converted)
            if re.search(r'\bC hash\b', text, re.IGNORECASE):
                text = re.sub(r'\bC hash\b', 'C sharp', text, flags=re.IGNORECASE)
                logger.info(f"Fixed C hash -> C sharp in: '{text[:50]}...'")

            # Fix F# -> F sharp (if already mangled)
            if re.search(r'\bF hash\b', text, re.IGNORECASE):
                text = re.sub(r'\bF hash\b', 'F sharp', text, flags=re.IGNORECASE)

            # OAuth authentication
            if re.search(r'\bOAuth\b', text, re.IGNORECASE):
                text = re.sub(r'OAuth\s*2\.0', 'OAuth two point zero', text, flags=re.IGNORECASE)
                logger.info(f"Fixed OAuth 2.0 in: '{text[:50]}...'")

            # IPv6
            if re.search(r'\bIPv6\b', text, re.IGNORECASE):
                text = re.sub(r'\bIPv6\b', 'I P V six', text, flags=re.IGNORECASE)
                logger.info(f"Fixed IPv6 in: '{text[:50]}...'")

            # SHA-256
            if re.search(r'\bSHA-?256\b', text, re.IGNORECASE):
                text = re.sub(r'\bSHA-?256\b', 'SHA two fifty six', text, flags=re.IGNORECASE)
                logger.info(f"Fixed SHA-256 in: '{text[:50]}...'")

            # Fix SQL pronunciation - default to "sequel"
            if re.search(r'\bSQL\b', text, re.IGNORECASE):
                text = re.sub(r'\bSQL\b', 'sequel', text, flags=re.IGNORECASE)
                logger.info(f"Fixed SQL -> sequel in: '{text[:50]}...'")

            if text != original_text:
                logger.debug(f"Preprocessed: '{original_text[:50]}...' -> '{text[:50]}...'")

            return text

        # Store original create method
        original_create = kokoro_onnx.Kokoro.create

        def patched_create(self, text, voice, speed=1.0, lang='en-us'):
            """Patched create method that uses misaki for phonemization"""
            log = logging.getLogger('kokoro_onnx')

            # Check if text already contains IPA phonemes
            if contains_ipa(text):
                logger.info(f"Text already contains IPA phonemes, using directly: '{text[:50]}...'")
                phonemes = text
            else:
                # Pre-process text to fix JSON→Jason, C#→C sharp, etc.
                processed_text = _preprocess_for_misaki(text)

                # Try to use misaki for phonemization
                g2p = _get_misaki_g2p()
                if g2p is not None:
                    try:
                        # Use misaki to phonemize the PRE-PROCESSED text
                        phonemes, _ = g2p(processed_text)
                        logger.info(f"Misaki phonemized: '{processed_text[:50]}...' -> '{phonemes[:50]}...'")
                    except Exception as e:
                        logger.warning(f"Misaki phonemization failed: {e}, falling back to internal")
                        # Fall back to internal phonemizer
                        return original_create(self, text, voice, speed, lang)
                else:
                    # Misaki not available, use internal phonemizer
                    return original_create(self, text, voice, speed, lang)

            # Resolve voice name to voice array if needed
            voice_array = voice
            if isinstance(voice, str):
                if hasattr(self, 'voices') and voice in self.voices:
                    voice_array = self.voices[voice]
                else:
                    log.warning(f"Voice '{voice}' not found, falling back to internal")
                    return original_create(self, text, voice, speed, lang)

            # Use the phonemes to generate audio
            return self._create_audio(phonemes, voice_array, speed)

        # Apply the patch
        kokoro_onnx.Kokoro.create = patched_create

        logger.info("✅ Applied misaki phonemizer patch")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to apply misaki phonemizer patch: {e}")
        return False

def apply_all_patches():
    """Apply all necessary patches"""
    logger.info("🔧 Applying kokoro_onnx patches...")

    success = patch_kokoro_onnx()

    if success:
        logger.info("✅ Performance patches applied successfully")
    else:
        logger.error("❌ Some patches failed to apply")

    # Also apply the misaki phonemizer patch
    logger.info("🔧 Applying misaki phonemizer patch...")
    phonemizer_success = patch_kokoro_onnx_phonemizer()
    if phonemizer_success:
        logger.info("✅ Misaki phonemizer patch applied successfully")
    else:
        logger.warning("⚠️ Misaki phonemizer patch failed (will use internal phonemizer)")

    return success and phonemizer_success
