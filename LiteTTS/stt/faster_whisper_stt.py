"""
Faster-Whisper STT Implementation for LiteTTS
High-performance speech-to-text using faster-whisper with turbo model support
"""

import time
import logging
import tempfile
import io
from pathlib import Path
from typing import Optional, Union, List, Dict, Any

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    WhisperModel = None

from .stt_models import STTConfiguration, STTRequest, STTResponse, STTSegment, STTError

logger = logging.getLogger(__name__)

class FasterWhisperSTT:
    """High-performance STT using faster-whisper"""
    
    def __init__(self, config: STTConfiguration):
        """Initialize faster-whisper STT"""
        if not FASTER_WHISPER_AVAILABLE:
            raise ImportError("faster-whisper is not installed. Install with: pip install faster-whisper")
        
        self.config = config
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the faster-whisper model"""
        try:
            logger.info(f"🔄 Loading faster-whisper model: {self.config.model}")
            start_time = time.time()
            
            self.model = WhisperModel(
                self.config.model,
                device=self.config.device,
                compute_type=self.config.compute_type
            )
            
            load_time = time.time() - start_time
            logger.info(f"✅ Faster-whisper model loaded in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to load faster-whisper model: {e}")
            raise
    
    def transcribe(self, request: STTRequest) -> STTResponse:
        """Transcribe audio using faster-whisper"""
        if not self.model:
            raise RuntimeError("Model not initialized")
        
        start_time = time.time()
        
        try:
            # Prepare audio input
            audio_path = self._prepare_audio_input(request.audio)
            
            # Set transcription parameters
            language = request.language if request.language != "auto" else None
            temperature = request.temperature if request.temperature is not None else self.config.temperature
            
            # Perform transcription
            logger.debug(f"🎤 Transcribing audio with model: {self.config.model}")
            
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=self.config.beam_size,
                best_of=self.config.best_of,
                patience=self.config.patience,
                length_penalty=self.config.length_penalty,
                repetition_penalty=self.config.repetition_penalty,
                no_repeat_ngram_size=self.config.no_repeat_ngram_size,
                temperature=temperature,
                compression_ratio_threshold=self.config.compression_ratio_threshold,
                log_prob_threshold=self.config.log_prob_threshold,
                no_speech_threshold=self.config.no_speech_threshold,
                condition_on_previous_text=self.config.condition_on_previous_text,
                prompt_reset_on_temperature=self.config.prompt_reset_on_temperature,
                initial_prompt=self.config.initial_prompt,
                prefix=self.config.prefix,
                suppress_blank=self.config.suppress_blank,
                suppress_tokens=self.config.suppress_tokens,
                without_timestamps=self.config.without_timestamps,
                max_initial_timestamp=self.config.max_initial_timestamp,
                word_timestamps=self.config.word_timestamps,
                prepend_punctuations=self.config.prepend_punctuations,
                append_punctuations=self.config.append_punctuations,
                vad_filter=self.config.vad_filter,
                vad_parameters=self.config.vad_parameters
            )
            
            # Convert segments to our format
            stt_segments = []
            full_text = ""
            
            for segment in segments:
                stt_segment = STTSegment(
                    id=segment.id,
                    seek=segment.seek,
                    start=segment.start,
                    end=segment.end,
                    text=segment.text,
                    tokens=segment.tokens,
                    temperature=segment.temperature,
                    avg_logprob=segment.avg_logprob,
                    compression_ratio=segment.compression_ratio,
                    no_speech_prob=segment.no_speech_prob,
                    words=getattr(segment, 'words', None)
                )
                stt_segments.append(stt_segment)
                full_text += segment.text
            
            processing_time = time.time() - start_time
            
            # Calculate confidence score (average of segment probabilities)
            if stt_segments:
                confidence = 1.0 - sum(seg.no_speech_prob for seg in stt_segments) / len(stt_segments)
            else:
                confidence = 0.0
            
            response = STTResponse(
                text=full_text.strip(),
                language=info.language,
                duration=info.duration,
                segments=stt_segments,
                words=None,  # Could be extracted from segments if needed
                processing_time=processing_time,
                model_used=self.config.model,
                confidence=confidence
            )
            
            logger.info(f"✅ Transcription completed in {processing_time:.2f}s")
            logger.info(f"📝 Text: '{response.text[:100]}{'...' if len(response.text) > 100 else ''}'")
            logger.info(f"🌍 Language: {response.language}")
            logger.info(f"📊 Confidence: {confidence:.3f}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            raise
        
        finally:
            # Clean up temporary files
            if isinstance(audio_path, str) and audio_path.startswith(tempfile.gettempdir()):
                try:
                    Path(audio_path).unlink(missing_ok=True)
                except:
                    pass
    
    def _prepare_audio_input(self, audio: Union[str, Path, bytes, io.BytesIO]) -> str:
        """Prepare audio input for faster-whisper"""
        if isinstance(audio, (str, Path)):
            # File path
            audio_path = Path(audio)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            return str(audio_path)
        
        elif isinstance(audio, bytes):
            # Raw bytes - save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio)
                return tmp_file.name
        
        elif isinstance(audio, io.BytesIO):
            # BytesIO object - save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                audio.seek(0)
                tmp_file.write(audio.read())
                return tmp_file.name
        
        else:
            raise ValueError(f"Unsupported audio input type: {type(audio)}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        # faster-whisper supports the same languages as OpenAI Whisper
        return [
            "af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs", "ca", "cs", "cy", "da", "de", "el", "en", "es", "et", "eu", "fa", "fi", "fo", "fr", "gl", "gu", "ha", "haw", "he", "hi", "hr", "ht", "hu", "hy", "id", "is", "it", "ja", "jw", "ka", "kk", "km", "kn", "ko", "la", "lb", "ln", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "nn", "no", "oc", "pa", "pl", "ps", "pt", "ro", "ru", "sa", "sd", "si", "sk", "sl", "sn", "so", "sq", "sr", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "uk", "ur", "uz", "vi", "yi", "yo", "zh"
        ]
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return [
            "tiny", "tiny.en", "base", "base.en", "small", "small.en", 
            "medium", "medium.en", "large", "large-v1", "large-v2", "large-v3", "turbo"
        ]
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the STT system"""
        try:
            if not self.model:
                return {
                    "status": "error",
                    "message": "Model not initialized",
                    "model": self.config.model,
                    "device": self.config.device
                }
            
            # Test with a short silence (should be very fast)
            import numpy as np
            
            # Create 1 second of silence
            sample_rate = 16000
            silence = np.zeros(sample_rate, dtype=np.float32)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                import wave
                with wave.open(tmp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes((silence * 32767).astype(np.int16).tobytes())
                
                # Test transcription
                start_time = time.time()
                request = STTRequest(audio=tmp_file.name)
                response = self.transcribe(request)
                test_time = time.time() - start_time
                
                # Clean up
                Path(tmp_file.name).unlink(missing_ok=True)
                
                return {
                    "status": "healthy",
                    "model": self.config.model,
                    "device": self.config.device,
                    "test_time": test_time,
                    "test_result": response.text,
                    "confidence": response.confidence
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "model": self.config.model,
                "device": self.config.device
            }

def create_stt_from_config(config_dict: Dict[str, Any]) -> FasterWhisperSTT:
    """Create STT instance from configuration dictionary"""
    config = STTConfiguration(**config_dict)
    return FasterWhisperSTT(config)
