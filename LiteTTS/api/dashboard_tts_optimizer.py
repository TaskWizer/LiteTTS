#!/usr/bin/env python3
"""
Dashboard TTS Optimizer for LiteTTS
Ensures dashboard TTS requests use the same optimized processing pipeline as API requests
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DashboardTTSMetrics:
    """Metrics for dashboard TTS requests"""
    request_id: str
    start_time: float
    end_time: float
    total_latency_ms: float
    processing_latency_ms: float
    optimization_applied: bool
    rtf: float
    text_length: int
    voice: str
    success: bool
    error_message: Optional[str] = None

class DashboardTTSOptimizer:
    """
    Optimizer specifically for dashboard TTS requests to ensure they use
    the same optimized processing pipeline as API requests
    """
    
    def __init__(self, app_instance=None):
        self.app_instance = app_instance
        self.metrics_history = []
        self.optimization_enabled = True
        
        # Performance targets for dashboard
        self.target_latency_ms = 500
        self.target_rtf = 0.25
        
        logger.info("Dashboard TTS Optimizer initialized")
    
    def optimize_dashboard_tts_request(self,
                                     text: str,
                                     voice: str,
                                     response_format: str = "mp3") -> Tuple[bytes, DashboardTTSMetrics]:
        """
        Process a dashboard TTS request using the optimized pipeline with comprehensive error handling
        """
        request_id = f"dashboard_{int(time.time() * 1000)}"
        start_time = time.time()

        logger.info(f"🎯 Processing optimized dashboard TTS request: {request_id}")

        # Validate inputs before processing
        validation_error = self._validate_dashboard_request(text, voice, response_format)
        if validation_error:
            end_time = time.time()
            total_latency_ms = (end_time - start_time) * 1000

            metrics = DashboardTTSMetrics(
                request_id=request_id,
                start_time=start_time,
                end_time=end_time,
                total_latency_ms=total_latency_ms,
                processing_latency_ms=total_latency_ms,
                optimization_applied=False,
                rtf=0.0,
                text_length=len(text),
                voice=voice,
                success=False,
                error_message=f"Validation failed: {validation_error}"
            )

            self.metrics_history.append(metrics)
            logger.error(f"❌ Dashboard TTS validation failed: {validation_error}")
            raise ValueError(f"Dashboard TTS validation failed: {validation_error}")

        try:
            # Apply the same optimizations as the main API
            audio_data = self._process_with_optimizations(text, voice, response_format)

            # Validate audio output before considering it successful
            audio_validation_error = self._validate_audio_output(audio_data, response_format)
            if audio_validation_error:
                raise ValueError(f"Audio validation failed: {audio_validation_error}")

            end_time = time.time()
            total_latency_ms = (end_time - start_time) * 1000

            # Calculate RTF (rough estimation)
            estimated_duration = len(text.split()) / 150 * 60  # ~150 words per minute
            rtf = (total_latency_ms / 1000) / max(estimated_duration, 0.1)

            # Create metrics
            metrics = DashboardTTSMetrics(
                request_id=request_id,
                start_time=start_time,
                end_time=end_time,
                total_latency_ms=total_latency_ms,
                processing_latency_ms=total_latency_ms,  # Simplified for dashboard
                optimization_applied=self.optimization_enabled,
                rtf=rtf,
                text_length=len(text),
                voice=voice,
                success=True
            )

            # Store metrics
            self.metrics_history.append(metrics)

            # Log performance
            status = "✅ MEETS TARGET" if total_latency_ms < self.target_latency_ms else "⚠️ EXCEEDS TARGET"
            logger.info(f"🎯 Dashboard TTS completed: {total_latency_ms:.1f}ms, RTF: {rtf:.3f} {status}")

            return audio_data, metrics

        except Exception as e:
            end_time = time.time()
            total_latency_ms = (end_time - start_time) * 1000

            # Categorize the error for better reporting
            error_category = self._categorize_error(e)
            detailed_error = f"[{error_category}] {str(e)}"

            metrics = DashboardTTSMetrics(
                request_id=request_id,
                start_time=start_time,
                end_time=end_time,
                total_latency_ms=total_latency_ms,
                processing_latency_ms=total_latency_ms,
                optimization_applied=False,
                rtf=0.0,
                text_length=len(text),
                voice=voice,
                success=False,
                error_message=detailed_error
            )

            self.metrics_history.append(metrics)
            logger.error(f"❌ Dashboard TTS failed: {detailed_error}")

            # Re-raise with more context for dashboard UI
            raise RuntimeError(f"Dashboard TTS generation failed: {detailed_error}")
    
    def _process_with_optimizations(self, text: str, voice: str, response_format: str) -> bytes:
        """
        Process TTS request using the same optimizations as the main API
        """
        if not self.app_instance:
            raise ValueError("App instance not available for optimization")

        # CRITICAL FIX: Always use the app's main synthesizer, never create a separate one
        try:
            # Access the app's TTS synthesizer with all optimizations
            if hasattr(self.app_instance, 'synthesizer'):
                synthesizer = self.app_instance.synthesizer
                logger.debug("Using main app synthesizer (optimized path)")
            else:
                # This should never happen in normal operation
                raise ValueError("Main app synthesizer not available - this indicates a serious initialization problem")

            # Apply performance optimizations
            if hasattr(self.app_instance, 'performance_optimizer'):
                # Ensure performance optimizations are applied
                self.app_instance.performance_optimizer.optimize_for_request()

            # Apply SIMD optimizations
            if hasattr(self.app_instance, 'simd_optimizer'):
                self.app_instance.simd_optimizer.apply_optimizations()

            # Create proper TTSRequest object - this is the critical fix!
            from LiteTTS.models import TTSRequest
            request = TTSRequest(
                input=text,
                voice=voice,
                response_format=response_format,
                speed=1.0,  # Default speed for dashboard
                stream=True,  # Enable streaming for better performance
                volume_multiplier=1.0
            )

            # Process the request with proper TTSRequest object
            audio_segment = synthesizer.synthesize(request)

            # Convert AudioSegment to bytes for dashboard response
            if hasattr(audio_segment, 'audio_data'):
                # Convert to proper audio format using AudioProcessor
                from LiteTTS.audio.processor import AudioProcessor
                audio_processor = AudioProcessor()
                audio_bytes = audio_processor.convert_format(audio_segment, response_format)

                # Validate that we got actual audio data, not placeholder
                if len(audio_bytes) < 100:  # Minimum reasonable audio file size
                    raise ValueError(f"Generated audio too small ({len(audio_bytes)} bytes), likely invalid")

                logger.info(f"Successfully generated {len(audio_bytes)} bytes of {response_format} audio")
                return audio_bytes
            else:
                raise ValueError("Invalid audio segment returned from synthesizer")

        except Exception as e:
            logger.error(f"Optimized processing failed: {e}")
            # Fallback to basic processing
            return self._basic_tts_processing(text, voice, response_format)
    
    def _basic_tts_processing(self, text: str, voice: str, response_format: str) -> bytes:
        """
        Fallback basic TTS processing - CRITICAL FIX: Use main app synthesizer
        """
        logger.warning("Using fallback basic TTS processing")

        try:
            # CRITICAL FIX: Use the main app's synthesizer instead of creating a separate one
            # This ensures we use the same optimized, patched synthesizer as the main API
            if self.app_instance and hasattr(self.app_instance, 'synthesizer'):
                synthesizer = self.app_instance.synthesizer
                logger.info("Using main app synthesizer (fallback path)")
            else:
                # This should be extremely rare - only if app_instance is not available
                logger.error("Main app synthesizer not available in fallback - this indicates a serious problem")
                raise ValueError("Cannot access main app synthesizer for fallback processing")

            from LiteTTS.models import TTSRequest

            # Create proper TTSRequest object for fallback too
            request = TTSRequest(
                input=text,
                voice=voice,
                response_format=response_format,
                speed=1.0,
                stream=False,  # Disable streaming for fallback
                volume_multiplier=1.0
            )

            # Process the request
            audio_segment = synthesizer.synthesize(request)

            # Convert AudioSegment to bytes using the same method as optimized path
            if hasattr(audio_segment, 'audio_data'):
                from LiteTTS.audio.processor import AudioProcessor
                audio_processor = AudioProcessor()
                audio_bytes = audio_processor.convert_format(audio_segment, response_format)

                # Validate that we got actual audio data
                if len(audio_bytes) < 100:  # Minimum reasonable audio file size
                    raise ValueError(f"Fallback generated audio too small ({len(audio_bytes)} bytes), likely invalid")

                logger.info(f"Fallback successfully generated {len(audio_bytes)} bytes of {response_format} audio")
                return audio_bytes
            else:
                raise ValueError("Invalid audio segment returned from fallback synthesizer")

        except Exception as e:
            logger.error(f"Fallback TTS processing also failed: {e}")
            # Only as last resort, raise the error instead of returning placeholder
            raise RuntimeError(f"Both optimized and fallback TTS processing failed: {e}")

    def _validate_dashboard_request(self, text: str, voice: str, response_format: str) -> Optional[str]:
        """
        Validate dashboard TTS request parameters
        Returns error message if validation fails, None if valid
        """
        if not text or not text.strip():
            return "Text input is required and cannot be empty"

        if len(text) > 10000:  # Reasonable limit for dashboard
            return f"Text too long ({len(text)} characters, max 10000)"

        if not voice or not voice.strip():
            return "Voice parameter is required"

        # Check if voice is available (if we have access to voice manager)
        if hasattr(self.app_instance, 'voice_manager'):
            try:
                available_voices = self.app_instance.voice_manager.get_available_voices()
                if voice not in available_voices:
                    return f"Voice '{voice}' not available. Available voices: {', '.join(available_voices[:5])}..."
            except Exception as e:
                logger.warning(f"Could not validate voice availability: {e}")

        if response_format not in ['mp3', 'wav', 'ogg', 'flac']:
            return f"Unsupported response format '{response_format}'. Supported: mp3, wav, ogg, flac"

        return None

    def _validate_audio_output(self, audio_data: bytes, expected_format: str) -> Optional[str]:
        """
        Validate generated audio data
        Returns error message if validation fails, None if valid
        """
        if not audio_data:
            return "No audio data generated"

        if len(audio_data) < 100:  # Minimum reasonable audio file size
            return f"Audio data too small ({len(audio_data)} bytes), likely invalid"

        # Check for placeholder data patterns
        if audio_data == b"placeholder_audio_data":
            return "Placeholder audio data detected - synthesis failed"

        # Basic format validation for common formats
        if expected_format.lower() == 'mp3':
            if not audio_data.startswith(b'ID3') and not audio_data.startswith(b'\xff\xfb'):
                logger.warning("Audio data doesn't appear to be valid MP3 format")
        elif expected_format.lower() == 'wav':
            if not audio_data.startswith(b'RIFF'):
                logger.warning("Audio data doesn't appear to be valid WAV format")

        return None

    def _categorize_error(self, error: Exception) -> str:
        """
        Categorize errors for better reporting and debugging
        """
        error_str = str(error).lower()
        error_type = type(error).__name__

        if 'voice' in error_str and ('not found' in error_str or 'not available' in error_str):
            return "VOICE_ERROR"
        elif 'audio' in error_str and ('validation' in error_str or 'invalid' in error_str):
            return "AUDIO_ERROR"
        elif 'synthesizer' in error_str or 'synthesis' in error_str:
            return "SYNTHESIS_ERROR"
        elif 'format' in error_str or 'conversion' in error_str:
            return "FORMAT_ERROR"
        elif 'timeout' in error_str or error_type == 'TimeoutError':
            return "TIMEOUT_ERROR"
        elif 'memory' in error_str or 'out of memory' in error_str:
            return "MEMORY_ERROR"
        elif 'permission' in error_str or 'access' in error_str:
            return "PERMISSION_ERROR"
        elif error_type in ['ValueError', 'TypeError']:
            return "VALIDATION_ERROR"
        elif error_type in ['ConnectionError', 'NetworkError']:
            return "NETWORK_ERROR"
        else:
            return "UNKNOWN_ERROR"
    
    def get_dashboard_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary for dashboard TTS requests
        """
        if not self.metrics_history:
            return {
                "total_requests": 0,
                "avg_latency_ms": 0,
                "avg_rtf": 0,
                "success_rate": 0,
                "target_compliance": 0
            }

        recent_metrics = self.metrics_history[-100:]  # Last 100 requests

        successful_metrics = [m for m in recent_metrics if m.success]

        if not successful_metrics:
            return {
                "total_requests": len(recent_metrics),
                "avg_latency_ms": 0,
                "avg_rtf": 0,
                "success_rate": 0,
                "target_compliance": 0
            }

        avg_latency = sum(m.total_latency_ms for m in successful_metrics) / len(successful_metrics)
        avg_rtf = sum(m.rtf for m in successful_metrics) / len(successful_metrics)
        success_rate = len(successful_metrics) / len(recent_metrics) * 100

        # Calculate target compliance
        compliant_requests = sum(1 for m in successful_metrics if m.total_latency_ms < self.target_latency_ms)
        target_compliance = compliant_requests / len(successful_metrics) * 100

        return {
            "total_requests": len(recent_metrics),
            "avg_latency_ms": round(avg_latency, 1),
            "avg_rtf": round(avg_rtf, 3),
            "success_rate": round(success_rate, 1),
            "target_compliance": round(target_compliance, 1),
            "optimization_enabled": self.optimization_enabled
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Alias for get_dashboard_performance_summary() for backward compatibility
        """
        return self.get_dashboard_performance_summary()
    
    def enable_optimization(self):
        """Enable dashboard TTS optimization"""
        self.optimization_enabled = True
        logger.info("✅ Dashboard TTS optimization enabled")
    
    def disable_optimization(self):
        """Disable dashboard TTS optimization"""
        self.optimization_enabled = False
        logger.warning("⚠️ Dashboard TTS optimization disabled")
    
    def get_recent_metrics(self, count: int = 10) -> list:
        """Get recent dashboard TTS metrics"""
        return self.metrics_history[-count:] if self.metrics_history else []
    
    def clear_metrics_history(self):
        """Clear metrics history"""
        self.metrics_history.clear()
        logger.info("Dashboard TTS metrics history cleared")

# Global dashboard TTS optimizer instance
_dashboard_tts_optimizer: Optional[DashboardTTSOptimizer] = None

def get_dashboard_tts_optimizer(app_instance=None) -> DashboardTTSOptimizer:
    """Get or create the global dashboard TTS optimizer"""
    global _dashboard_tts_optimizer
    if _dashboard_tts_optimizer is None:
        _dashboard_tts_optimizer = DashboardTTSOptimizer(app_instance)
    elif app_instance and not _dashboard_tts_optimizer.app_instance:
        _dashboard_tts_optimizer.app_instance = app_instance
    return _dashboard_tts_optimizer

def optimize_dashboard_tts_endpoint(app_instance):
    """
    Decorator/function to optimize dashboard TTS endpoints
    """
    optimizer = get_dashboard_tts_optimizer(app_instance)
    
    def process_dashboard_tts(text: str, voice: str, response_format: str = "mp3"):
        """Process dashboard TTS with optimizations"""
        return optimizer.optimize_dashboard_tts_request(text, voice, response_format)
    
    return process_dashboard_tts

def main():
    """Test the dashboard TTS optimizer"""
    optimizer = DashboardTTSOptimizer()
    
    print("🎯 Dashboard TTS Optimizer Test")
    print("=" * 40)
    
    # Test basic functionality
    try:
        # This would normally process with the app instance
        print("✅ Dashboard TTS Optimizer initialized successfully")
        
        # Get performance summary
        summary = optimizer.get_dashboard_performance_summary()
        print(f"Performance Summary: {summary}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()
