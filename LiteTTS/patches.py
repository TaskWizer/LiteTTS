#!/usr/bin/env python3
"""
Patches for kokoro_onnx library to fix tensor rank issues
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)

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
            try:
                from LiteTTS.performance.dynamic_allocator import get_dynamic_allocator
                dynamic_allocator = get_dynamic_allocator()

                # Try to apply dynamic allocation first
                if dynamic_allocator.apply_to_onnx_session_options(session_options):
                    logger.info("Applied dynamic CPU allocation to ONNX session")
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

def apply_all_patches():
    """Apply all necessary patches"""
    logger.info("🔧 Applying kokoro_onnx patches...")
    
    success = patch_kokoro_onnx()
    
    if success:
        logger.info("✅ All patches applied successfully")
    else:
        logger.error("❌ Some patches failed to apply")
    
    return success
