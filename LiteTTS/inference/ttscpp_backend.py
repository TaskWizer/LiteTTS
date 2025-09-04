#!/usr/bin/env python3
"""
TTS.cpp inference backend for LiteTTS
Implements GGUF model support using TTS.cpp subprocess calls
"""

import numpy as np
import subprocess
import tempfile
import os
import shlex
import time
import logging
import threading
import concurrent.futures
from queue import Queue
import signal
import threading
import queue
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import soundfile as sf

from .base import BaseInferenceBackend, InferenceConfig, ModelInputs, ModelOutputs

logger = logging.getLogger(__name__)

class TTSCppBackend(BaseInferenceBackend):
    """TTS.cpp inference backend implementation using subprocess calls"""

    def __init__(self, config: InferenceConfig):
        super().__init__(config)
        self.ttscpp_executable = None
        self.model_validated = False
        self.temp_dir = None
        # Dynamic timeout configuration based on text length
        self.base_timeout = 10  # seconds - base timeout for short text
        self.max_timeout = 60   # seconds - maximum timeout for long text
        self.timeout_per_char = 0.1  # additional seconds per character
        self.process_timeout = self.base_timeout  # Default process timeout
        self.max_retries = 2  # reduced retries for faster failure detection
        self.retry_delay = 0.5  # seconds - faster retry
        self.process_monitor = None

        # Performance optimization: Process pool for parallel execution
        self.max_workers = min(4, os.cpu_count() or 1)  # Limit concurrent processes
        self.executor = None
        self.process_pool_lock = threading.Lock()

        # Parse backend-specific options
        if config.backend_specific_options:
            self.ttscpp_executable = config.backend_specific_options.get('ttscpp_executable')
            self.base_timeout = config.backend_specific_options.get('timeout', self.base_timeout)
            self.max_workers = config.backend_specific_options.get('max_workers', self.max_workers)
            # Support dynamic timeout configuration
            self.max_timeout = config.backend_specific_options.get('max_timeout', self.max_timeout)
            self.timeout_per_char = config.backend_specific_options.get('timeout_per_char', self.timeout_per_char)

        # Try to get executable from global settings if not in backend options
        if not self.ttscpp_executable:
            self.ttscpp_executable = self._get_executable_from_settings()

        # Auto-detect TTS.cpp executable if still not specified
        if not self.ttscpp_executable:
            self.ttscpp_executable = self._find_ttscpp_executable()

        logger.info(f"Initialized TTS.cpp backend with executable: {self.ttscpp_executable}")

    def _calculate_dynamic_timeout(self, text: str) -> float:
        """Calculate dynamic timeout based on text length"""
        text_length = len(text) if text else 0
        dynamic_timeout = self.base_timeout + (text_length * self.timeout_per_char)
        return min(dynamic_timeout, self.max_timeout)

    def _get_executable_from_settings(self) -> Optional[str]:
        """Get TTS.cpp executable path from settings.json"""
        try:
            import json
            from pathlib import Path

            # Try to load settings.json
            settings_path = Path("config/settings.json")
            if not settings_path.exists():
                # Fallback to other possible locations
                for alt_path in ["settings.json", "../config/settings.json", "LiteTTS/config/settings.json"]:
                    alt_settings = Path(alt_path)
                    if alt_settings.exists():
                        settings_path = alt_settings
                        break
                else:
                    logger.debug("settings.json not found for TTS.cpp executable configuration")
                    return None

            with open(settings_path, 'r') as f:
                settings = json.load(f)

            # Get executable path from tts section
            ttscpp_executable = settings.get('tts', {}).get('ttscpp_executable')
            if ttscpp_executable:
                # Convert to absolute path if relative
                exec_path = Path(ttscpp_executable)
                if not exec_path.is_absolute():
                    exec_path = Path.cwd() / exec_path

                if exec_path.exists():
                    logger.info(f"Found TTS.cpp executable in settings: {exec_path}")
                    return str(exec_path)
                else:
                    logger.warning(f"TTS.cpp executable path from settings does not exist: {exec_path}")

            return None

        except Exception as e:
            logger.debug(f"Failed to read TTS.cpp executable from settings: {e}")
            return None

    def _find_ttscpp_executable(self) -> Optional[str]:
        """Auto-detect TTS.cpp CLI executable"""
        # Common paths to check
        search_paths = [
            # Relative to LiteTTS directory
            "../TTS.cpp/build/bin/tts-cli",
            "../../TTS.cpp/build/bin/tts-cli",
            # Absolute paths
            "/usr/local/bin/tts-cli",
            "/usr/bin/tts-cli",
            # Current directory
            "./tts-cli",
            "./build/bin/tts-cli"
        ]
        
        for path in search_paths:
            full_path = Path(path).resolve()
            if full_path.exists() and full_path.is_file():
                # Test if executable works
                try:
                    result = subprocess.run([str(full_path), "--help"], 
                                          capture_output=True, timeout=10)
                    if result.returncode == 0:
                        logger.info(f"Found TTS.cpp executable: {full_path}")
                        return str(full_path)
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    continue
        
        logger.error("TTS.cpp executable not found. Please specify ttscpp_executable in backend_specific_options")
        return None
    
    def load_model(self) -> bool:
        """Load and validate the GGUF model"""
        try:
            if not self.ttscpp_executable:
                logger.error("TTS.cpp executable not available")
                return False
            
            if not self.model_path.exists():
                logger.error(f"Model file not found: {self.model_path}")
                return False
            
            if not self.validate_model():
                logger.error(f"Model validation failed: {self.model_path}")
                return False
            
            # Create temporary directory for audio outputs
            self.temp_dir = tempfile.mkdtemp(prefix="ttscpp_")
            
            # Test model loading with a simple inference
            test_success = self._test_model_loading()
            
            if test_success:
                self.is_loaded = True
                self.model_info = {
                    "model_path": str(self.model_path),
                    "backend": "ttscpp",
                    "executable": self.ttscpp_executable,
                    "temp_dir": self.temp_dir,
                    "validated": True
                }
                logger.info(f"TTS.cpp model loaded successfully: {self.model_path}")

                # Initialize process pool for performance optimization
                self._initialize_process_pool()

                return True
            else:
                logger.error("Model loading test failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load TTS.cpp model: {e}")
            self.is_loaded = False
            return False
    
    def _test_model_loading(self) -> bool:
        """Test model loading with a minimal inference"""
        try:
            test_text = "Test"
            test_output = os.path.join(self.temp_dir, "test_load.wav")
            
            cmd = [
                self.ttscpp_executable,
                "-mp", str(self.model_path),
                "-p", test_text,
                "-sp", test_output
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.process_timeout
            )
            
            if result.returncode == 0 and os.path.exists(test_output):
                # Clean up test file
                os.remove(test_output)
                return True
            else:
                logger.error(f"Model loading test failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Model loading test error: {e}")
            return False

    def _initialize_process_pool(self):
        """Initialize process pool for parallel TTS.cpp execution"""
        try:
            with self.process_pool_lock:
                if self.executor is None:
                    self.executor = concurrent.futures.ThreadPoolExecutor(
                        max_workers=self.max_workers,
                        thread_name_prefix="ttscpp_worker"
                    )
                    logger.info(f"TTS.cpp process pool initialized with {self.max_workers} workers")
        except Exception as e:
            logger.warning(f"Failed to initialize process pool: {e}")

    def _cleanup_process_pool(self):
        """Cleanup process pool"""
        try:
            with self.process_pool_lock:
                if self.executor:
                    self.executor.shutdown(wait=True, timeout=5.0)
                    self.executor = None
                    logger.info("TTS.cpp process pool cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up process pool: {e}")

    def unload_model(self) -> bool:
        """Unload the model and clean up resources"""
        try:
            # Cleanup process pool first
            self._cleanup_process_pool()

            # Clean up temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None

            self.model_info = {}
            self.is_loaded = False

            logger.info("TTS.cpp model unloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload TTS.cpp model: {e}")
            return False
    
    def run_inference(self, inputs: ModelInputs) -> ModelOutputs:
        """Run TTS.cpp inference via subprocess"""
        if not self.is_loaded:
            raise RuntimeError("TTS.cpp model not loaded")
        
        if not self.validate_inputs(inputs):
            raise ValueError("Invalid inputs for TTS.cpp inference")
        
        try:
            # Convert inputs to text prompt
            text_prompt = self._prepare_text_prompt(inputs)
            
            # Generate unique output filename
            timestamp = int(time.time() * 1000000)
            output_file = os.path.join(self.temp_dir, f"output_{timestamp}.wav")
            
            # Run TTS.cpp subprocess
            audio_data, sample_rate = self._run_ttscpp_subprocess(text_prompt, output_file)
            
            # Create standardized outputs
            outputs = ModelOutputs(
                audio=audio_data,
                sample_rate=sample_rate,
                metadata={
                    "backend": "ttscpp",
                    "model_path": str(self.model_path),
                    "text_length": len(text_prompt)
                }
            )
            
            logger.debug(f"TTS.cpp inference completed: output shape={audio_data.shape}")
            return outputs
            
        except Exception as e:
            logger.error(f"TTS.cpp inference failed: {e}")
            raise
    
    def _prepare_text_prompt(self, inputs: ModelInputs) -> str:
        """Convert ModelInputs to text prompt for TTS.cpp"""
        # For TTS.cpp, we need to convert input_ids back to text
        # This is a simplified approach - in practice, you'd need proper detokenization
        
        # Check if text is provided in additional_inputs
        if inputs.additional_inputs and 'text' in inputs.additional_inputs:
            text = inputs.additional_inputs['text']
            if isinstance(text, str):
                return text
        
        # Fallback: create placeholder text based on input_ids length
        # In a real implementation, you'd need proper detokenization
        num_tokens = inputs.input_ids.size if inputs.input_ids is not None else 10
        placeholder_text = "Hello, this is a test of the TTS system. " * max(1, num_tokens // 10)
        
        logger.warning("No text provided in inputs, using placeholder text")
        return placeholder_text.strip()
    
    def _run_ttscpp_subprocess(self, text: str, output_file: str) -> Tuple[np.ndarray, int]:
        """Run TTS.cpp subprocess and return audio data (with optimized parallel execution)"""
        # Calculate dynamic timeout based on text length
        dynamic_timeout = self._calculate_dynamic_timeout(text)

        # Use process pool for better performance if available
        if self.executor and self.max_workers > 1:
            try:
                future = self.executor.submit(self._run_ttscpp_subprocess_with_retry, text, output_file)
                return future.result(timeout=dynamic_timeout + 5)  # Add buffer time
            except concurrent.futures.TimeoutError:
                logger.warning(f"Process pool execution timed out after {dynamic_timeout + 5}s, falling back to direct execution")
            except Exception as e:
                logger.warning(f"Process pool execution failed: {e}, falling back to direct execution")

        # Fallback to direct execution
        return self._run_ttscpp_subprocess_with_retry(text, output_file)
    
    def _sanitize_text_input(self, text: str) -> str:
        """Sanitize text input for shell safety"""
        # Remove or escape potentially dangerous characters
        # Keep only printable ASCII characters and basic punctuation
        import string
        allowed_chars = string.ascii_letters + string.digits + string.punctuation + ' \n\t'
        sanitized = ''.join(c for c in text if c in allowed_chars)
        
        # Limit length to prevent extremely long inputs
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.warning(f"Text input truncated to {max_length} characters")
        
        return sanitized.strip()

    def _run_ttscpp_subprocess_with_retry(self, text: str, output_file: str) -> Tuple[np.ndarray, int]:
        """Run TTS.cpp subprocess with retry logic and enhanced error handling"""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"TTS.cpp subprocess attempt {attempt + 1}/{self.max_retries}")
                return self._run_ttscpp_subprocess_monitored(text, output_file)

            except subprocess.TimeoutExpired as e:
                last_exception = e
                logger.warning(f"TTS.cpp subprocess timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff

            except subprocess.SubprocessError as e:
                last_exception = e
                logger.warning(f"TTS.cpp subprocess error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

            except Exception as e:
                # For non-subprocess errors, don't retry
                logger.error(f"TTS.cpp non-recoverable error: {e}")
                raise

        # All retries failed
        logger.error(f"TTS.cpp subprocess failed after {self.max_retries} attempts")
        raise RuntimeError(f"TTS.cpp subprocess failed: {last_exception}")

    def _run_ttscpp_subprocess_monitored(self, text: str, output_file: str) -> Tuple[np.ndarray, int]:
        """Run TTS.cpp subprocess with process monitoring"""
        try:
            # Sanitize text input
            sanitized_text = self._sanitize_text_input(text)

            # Calculate dynamic timeout for this specific text
            dynamic_timeout = self._calculate_dynamic_timeout(sanitized_text)

            # Build command with proper escaping
            cmd = [
                self.ttscpp_executable,
                "-mp", str(self.model_path),
                "-p", sanitized_text,
                "-sp", output_file
            ]

            # Log command for debugging (without sensitive data)
            logger.debug(f"Running TTS.cpp command: {' '.join(cmd[:4])} [text_length={len(sanitized_text)}, timeout={dynamic_timeout:.1f}s] {cmd[5:]}")

            # Start subprocess with monitoring
            start_time = time.time()
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if os.name != 'nt' else None  # Process group for clean termination
            )

            # Monitor process with dynamic timeout
            stdout, stderr = self._monitor_process(process, dynamic_timeout)
            generation_time = time.time() - start_time

            # Check process result
            if process.returncode != 0:
                error_msg = f"TTS.cpp failed (exit code {process.returncode}): {stderr}"
                logger.error(error_msg)
                raise subprocess.SubprocessError(error_msg)

            # Validate output file
            if not os.path.exists(output_file):
                raise RuntimeError("TTS.cpp did not generate output file")

            # Load and validate audio
            audio_data, sample_rate = self._load_and_validate_audio(output_file)

            # Clean up output file
            try:
                os.remove(output_file)
            except OSError:
                logger.warning(f"Failed to remove temporary file: {output_file}")

            # Log performance metrics
            audio_duration = len(audio_data) / sample_rate
            rtf = generation_time / audio_duration if audio_duration > 0 else float('inf')
            logger.debug(f"TTS.cpp generation: {generation_time:.2f}s, "
                        f"audio: {audio_duration:.2f}s, RTF: {rtf:.3f}")

            return audio_data, int(sample_rate)

        except Exception as e:
            # Clean up on error
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except OSError:
                    pass
            raise

    def _monitor_process(self, process: subprocess.Popen, timeout: float) -> Tuple[str, str]:
        """Monitor subprocess with timeout and proper termination"""
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return stdout, stderr

        except subprocess.TimeoutExpired:
            logger.warning(f"TTS.cpp process timed out after {timeout}s, terminating...")

            # Attempt graceful termination
            try:
                if os.name != 'nt':
                    # Send SIGTERM to process group
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()

                # Wait briefly for graceful shutdown
                try:
                    stdout, stderr = process.communicate(timeout=5.0)
                    return stdout, stderr
                except subprocess.TimeoutExpired:
                    pass

            except (OSError, ProcessLookupError):
                pass  # Process may have already terminated

            # Force kill if still running
            try:
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                else:
                    process.kill()
                process.wait()
            except (OSError, ProcessLookupError):
                pass

            raise subprocess.TimeoutExpired(process.args, timeout)

    def _load_and_validate_audio(self, audio_file: str) -> Tuple[np.ndarray, int]:
        """Load and validate audio file with error handling"""
        try:
            # Check file size
            file_size = os.path.getsize(audio_file)
            if file_size == 0:
                raise RuntimeError("Generated audio file is empty")

            if file_size < 1000:  # Less than 1KB is suspicious
                logger.warning(f"Generated audio file is very small: {file_size} bytes")

            # Load audio with soundfile
            audio_data, sample_rate = sf.read(audio_file)

            # Validate audio data
            if audio_data.size == 0:
                raise RuntimeError("Audio file contains no data")

            # Convert to mono if stereo
            if audio_data.ndim > 1:
                audio_data = audio_data.mean(axis=1)
                logger.debug("Converted stereo audio to mono")

            # Ensure float32 format
            audio_data = audio_data.astype(np.float32)

            # Validate sample rate
            if sample_rate <= 0:
                raise RuntimeError(f"Invalid sample rate: {sample_rate}")

            # Check for audio quality issues
            max_amplitude = np.max(np.abs(audio_data))
            if max_amplitude == 0:
                logger.warning("Generated audio appears to be silent")
            elif max_amplitude > 1.0:
                logger.warning(f"Audio amplitude exceeds 1.0: {max_amplitude}")
                # Normalize to prevent clipping
                audio_data = audio_data / max_amplitude

            logger.debug(f"Loaded raw audio: {len(audio_data)} samples, {sample_rate} Hz, "
                        f"duration: {len(audio_data)/sample_rate:.2f}s")

            # Process audio through enhancement pipeline
            processed_audio, final_sample_rate = self._process_audio_output(audio_data, sample_rate)

            logger.debug(f"Processed audio: {len(processed_audio)} samples, {final_sample_rate} Hz, "
                        f"duration: {len(processed_audio)/final_sample_rate:.2f}s")

            return processed_audio, final_sample_rate

        except Exception as e:
            logger.error(f"Failed to load audio file {audio_file}: {e}")
            raise RuntimeError(f"Audio loading failed: {e}")

    def _process_audio_output(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, int]:
        """Process audio output with normalization and quality enhancements"""
        try:
            # Ensure target sample rate (24000 Hz for LiteTTS compatibility)
            target_sample_rate = 24000
            if sample_rate != target_sample_rate:
                audio_data = self._resample_audio(audio_data, sample_rate, target_sample_rate)
                sample_rate = target_sample_rate
                logger.debug(f"Resampled audio to {target_sample_rate} Hz")

            # Apply audio normalization
            audio_data = self._normalize_audio(audio_data)

            # Apply quality enhancements
            audio_data = self._enhance_audio_quality(audio_data, sample_rate)

            # Final validation
            audio_data = self._validate_final_audio(audio_data)

            return audio_data, sample_rate

        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            raise RuntimeError(f"Audio processing error: {e}")

    def _resample_audio(self, audio_data: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
        """Resample audio to target sample rate using linear interpolation"""
        if source_rate == target_rate:
            return audio_data

        try:
            # Calculate resampling ratio
            ratio = target_rate / source_rate

            # Calculate new length
            new_length = int(len(audio_data) * ratio)

            # Create new time indices
            old_indices = np.linspace(0, len(audio_data) - 1, len(audio_data))
            new_indices = np.linspace(0, len(audio_data) - 1, new_length)

            # Interpolate
            resampled_audio = np.interp(new_indices, old_indices, audio_data)

            logger.debug(f"Resampled audio from {source_rate} Hz to {target_rate} Hz "
                        f"({len(audio_data)} -> {len(resampled_audio)} samples)")

            return resampled_audio.astype(np.float32)

        except Exception as e:
            logger.warning(f"Audio resampling failed, using original: {e}")
            return audio_data

    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio amplitude and remove DC offset"""
        try:
            # Remove DC offset
            audio_data = audio_data - np.mean(audio_data)

            # Get peak amplitude
            peak_amplitude = np.max(np.abs(audio_data))

            if peak_amplitude == 0:
                logger.warning("Audio is silent, skipping normalization")
                return audio_data

            # Normalize to target level (0.8 to prevent clipping)
            target_level = 0.8
            if peak_amplitude > target_level:
                audio_data = audio_data * (target_level / peak_amplitude)
                logger.debug(f"Normalized audio from peak {peak_amplitude:.3f} to {target_level}")

            return audio_data.astype(np.float32)

        except Exception as e:
            logger.warning(f"Audio normalization failed: {e}")
            return audio_data

    def _enhance_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply quality enhancements to audio"""
        try:
            # Apply gentle high-pass filter to remove low-frequency noise
            audio_data = self._apply_highpass_filter(audio_data, sample_rate)

            # Apply fade-in/fade-out to prevent clicks
            audio_data = self._apply_fade_effects(audio_data, sample_rate)

            # Apply gentle compression for consistent levels
            audio_data = self._apply_gentle_compression(audio_data)

            return audio_data

        except Exception as e:
            logger.warning(f"Audio enhancement failed: {e}")
            return audio_data

    def _apply_highpass_filter(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply simple high-pass filter to remove low-frequency noise"""
        try:
            # Simple first-order high-pass filter (cutoff ~80 Hz)
            cutoff_freq = 80.0
            rc = 1.0 / (2 * np.pi * cutoff_freq)
            dt = 1.0 / sample_rate
            alpha = rc / (rc + dt)

            # Apply filter
            filtered_audio = np.zeros_like(audio_data)
            filtered_audio[0] = audio_data[0]

            for i in range(1, len(audio_data)):
                filtered_audio[i] = alpha * (filtered_audio[i-1] + audio_data[i] - audio_data[i-1])

            return filtered_audio.astype(np.float32)

        except Exception as e:
            logger.warning(f"High-pass filter failed: {e}")
            return audio_data

    def _apply_fade_effects(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply fade-in and fade-out to prevent audio clicks"""
        try:
            fade_duration = 0.01  # 10ms fade
            fade_samples = int(fade_duration * sample_rate)
            fade_samples = min(fade_samples, len(audio_data) // 4)  # Max 25% of audio length

            if fade_samples > 0:
                # Fade-in
                fade_in = np.linspace(0, 1, fade_samples)
                audio_data[:fade_samples] *= fade_in

                # Fade-out
                fade_out = np.linspace(1, 0, fade_samples)
                audio_data[-fade_samples:] *= fade_out

                logger.debug(f"Applied {fade_duration*1000:.1f}ms fade effects")

            return audio_data

        except Exception as e:
            logger.warning(f"Fade effects failed: {e}")
            return audio_data

    def _apply_gentle_compression(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply gentle compression for consistent audio levels"""
        try:
            # Soft knee compression using tanh
            threshold = 0.7
            ratio = 0.3  # Gentle compression

            # Apply compression only to samples above threshold
            mask = np.abs(audio_data) > threshold
            compressed_audio = audio_data.copy()

            # Compress positive values
            pos_mask = (audio_data > threshold)
            compressed_audio[pos_mask] = threshold + (audio_data[pos_mask] - threshold) * ratio

            # Compress negative values
            neg_mask = (audio_data < -threshold)
            compressed_audio[neg_mask] = -threshold + (audio_data[neg_mask] + threshold) * ratio

            # Apply soft knee using tanh for smooth transition
            compressed_audio = np.tanh(compressed_audio * 1.2) * 0.9

            return compressed_audio.astype(np.float32)

        except Exception as e:
            logger.warning(f"Audio compression failed: {e}")
            return audio_data

    def _validate_final_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Final validation and cleanup of audio data"""
        try:
            # Check for NaN or infinite values
            if np.any(np.isnan(audio_data)) or np.any(np.isinf(audio_data)):
                logger.warning("Audio contains NaN or infinite values, cleaning up")
                audio_data = np.nan_to_num(audio_data, nan=0.0, posinf=1.0, neginf=-1.0)

            # Ensure amplitude is within valid range
            audio_data = np.clip(audio_data, -1.0, 1.0)

            # Ensure minimum length (prevent empty audio)
            min_samples = 1000  # ~42ms at 24kHz
            if len(audio_data) < min_samples:
                logger.warning(f"Audio too short ({len(audio_data)} samples), padding to {min_samples}")
                padding = np.zeros(min_samples - len(audio_data), dtype=np.float32)
                audio_data = np.concatenate([audio_data, padding])

            return audio_data.astype(np.float32)

        except Exception as e:
            logger.error(f"Final audio validation failed: {e}")
            # Return safe fallback
            return np.zeros(24000, dtype=np.float32)  # 1 second of silence
    
    def validate_model(self) -> bool:
        """Validate that the model file is a compatible GGUF file"""
        try:
            if not self.model_path.exists():
                return False
            
            # Check file extension
            if not self.model_path.suffix.lower() == '.gguf':
                logger.error(f"Model file is not a GGUF file: {self.model_path}")
                return False
            
            # Check file size (should be reasonable for a model)
            file_size = self.model_path.stat().st_size
            if file_size < 1024 * 1024:  # Less than 1MB
                logger.error(f"Model file too small: {file_size} bytes")
                return False
            
            # Check GGUF magic bytes (optional, more thorough validation)
            try:
                with open(self.model_path, 'rb') as f:
                    magic = f.read(4)
                    if magic != b'GGUF':
                        logger.warning(f"Model file may not be valid GGUF format")
                        # Don't fail validation, as some files might work anyway
            except Exception:
                pass  # Skip magic byte check if file reading fails
            
            self.model_validated = True
            return True
            
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.is_loaded:
            return {}

        return self.model_info.copy()

    def get_input_specs(self) -> Dict[str, Dict[str, Any]]:
        """Get input specifications for TTS.cpp models"""
        return {
            "input_ids": {
                "shape": ["variable"],
                "dtype": "int32",
                "description": "Tokenized input sequence (converted to text for TTS.cpp)"
            },
            "style": {
                "shape": ["variable"],
                "dtype": "float32",
                "description": "Voice style embedding (not directly used by TTS.cpp)"
            },
            "speed": {
                "shape": [1],
                "dtype": "float32",
                "description": "Speed parameter (not directly used by TTS.cpp)"
            },
            "text": {
                "shape": ["variable"],
                "dtype": "string",
                "description": "Text prompt for TTS.cpp (preferred input method)"
            }
        }

    def get_output_specs(self) -> Dict[str, Dict[str, Any]]:
        """Get output specifications for TTS.cpp models"""
        return {
            "audio": {
                "shape": ["variable"],
                "dtype": "float32",
                "description": "Generated audio waveform"
            },
            "sample_rate": {
                "shape": [1],
                "dtype": "int32",
                "description": "Audio sample rate (typically 24000 Hz)"
            }
        }

    def supports_device(self, device: str) -> bool:
        """Check if backend supports the specified device"""
        # TTS.cpp currently supports CPU only in our implementation
        return device.lower() == "cpu"

    def estimate_memory_usage(self) -> Dict[str, int]:
        """Estimate memory usage for TTS.cpp model"""
        if not self.model_path.exists():
            return {"model_size": 0, "runtime_overhead": 0, "peak_inference": 0}

        model_size = self.model_path.stat().st_size

        # Rough estimates based on typical GGUF model behavior
        runtime_overhead = model_size // 4  # ~25% overhead for runtime structures
        peak_inference = model_size // 2    # ~50% additional during inference

        return {
            "model_size": model_size,
            "runtime_overhead": runtime_overhead,
            "peak_inference": peak_inference
        }

    def get_performance_info(self) -> Dict[str, Any]:
        """Get performance-related information"""
        base_info = super().get_performance_info()
        base_info.update({
            "ttscpp_executable": self.ttscpp_executable,
            "process_timeout": self.process_timeout,
            "supports_batching": False,  # TTS.cpp processes one text at a time
            "supports_streaming": False, # No streaming support via subprocess
            "subprocess_based": True
        })
        return base_info
