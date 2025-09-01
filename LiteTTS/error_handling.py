#!/usr/bin/env python3
"""
Comprehensive error handling and graceful degradation for Kokoro ONNX TTS API
"""

import logging
import traceback
import time
from typing import Optional, Dict, Any, Callable
from functools import wraps
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorContext:
    """Context information for error handling"""
    operation: str
    user_input: Optional[str] = None
    voice: Optional[str] = None
    format: Optional[str] = None
    timestamp: float = None
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class TTSError(Exception):
    """Base TTS error with context"""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 context: Optional[ErrorContext] = None, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.severity = severity
        self.context = context
        self.original_error = original_error
        self.timestamp = time.time()

class ModelLoadError(TTSError):
    """Error loading TTS model"""
    pass

class VoiceNotFoundError(TTSError):
    """Voice not available"""
    pass

class AudioGenerationError(TTSError):
    """Error generating audio"""
    pass

class ValidationError(TTSError):
    """Input validation error"""
    pass

class SystemResourceError(TTSError):
    """System resource exhaustion"""
    pass

class ErrorHandler:
    """Comprehensive error handling system"""
    
    def __init__(self):
        self.error_counts = {}
        self.last_errors = {}
        self.circuit_breakers = {}
        
    def handle_error(self, error: Exception, context: Optional[ErrorContext] = None) -> Dict[str, Any]:
        """Handle error with appropriate response"""
        
        # Wrap in TTSError if needed
        if not isinstance(error, TTSError):
            tts_error = TTSError(
                message=str(error),
                severity=self._determine_severity(error),
                context=context,
                original_error=error
            )
        else:
            tts_error = error
        
        # Log error
        self._log_error(tts_error)
        
        # Update error tracking
        self._track_error(tts_error)
        
        # Check circuit breaker
        if self._should_circuit_break(tts_error):
            return self._circuit_breaker_response(tts_error)
        
        # Generate appropriate response
        return self._generate_error_response(tts_error)
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity"""
        error_type = type(error).__name__
        
        critical_errors = [
            "MemoryError", "SystemExit", "KeyboardInterrupt",
            "OSError", "IOError"
        ]
        
        high_errors = [
            "ModelLoadError", "SystemResourceError",
            "FileNotFoundError", "PermissionError"
        ]
        
        medium_errors = [
            "AudioGenerationError", "VoiceNotFoundError",
            "ValueError", "RuntimeError"
        ]
        
        if error_type in critical_errors:
            return ErrorSeverity.CRITICAL
        elif error_type in high_errors:
            return ErrorSeverity.HIGH
        elif error_type in medium_errors:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _log_error(self, error: TTSError):
        """Log error with appropriate level"""
        error_msg = f"Error in {error.context.operation if error.context else 'unknown'}: {error}"
        
        if error.context:
            error_msg += f" | Context: {error.context.__dict__}"
        
        if error.original_error:
            error_msg += f" | Original: {error.original_error}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(error_msg)
            logger.critical(f"Stack trace: {traceback.format_exc()}")
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(error_msg)
            logger.error(f"Stack trace: {traceback.format_exc()}")
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(error_msg)
        else:
            logger.info(error_msg)
    
    def _track_error(self, error: TTSError):
        """Track error for pattern analysis"""
        error_key = f"{type(error).__name__}:{error.context.operation if error.context else 'unknown'}"
        
        if error_key not in self.error_counts:
            self.error_counts[error_key] = 0
        
        self.error_counts[error_key] += 1
        self.last_errors[error_key] = error.timestamp
    
    def _should_circuit_break(self, error: TTSError) -> bool:
        """Check if circuit breaker should activate"""
        if error.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
            error_key = f"{type(error).__name__}:{error.context.operation if error.context else 'unknown'}"
            
            # Circuit break if too many errors in short time
            if self.error_counts.get(error_key, 0) > 5:
                last_error_time = self.last_errors.get(error_key, 0)
                if time.time() - last_error_time < 300:  # 5 minutes
                    return True
        
        return False
    
    def _circuit_breaker_response(self, error: TTSError) -> Dict[str, Any]:
        """Generate circuit breaker response"""
        return {
            "error": "Service temporarily unavailable",
            "message": "The service is experiencing issues and has been temporarily disabled for recovery",
            "severity": "high",
            "retry_after": 300,  # 5 minutes
            "error_code": "CIRCUIT_BREAKER_ACTIVE"
        }
    
    def _generate_error_response(self, error: TTSError) -> Dict[str, Any]:
        """Generate appropriate error response"""
        base_response = {
            "error": str(error),
            "severity": error.severity.value,
            "timestamp": error.timestamp
        }
        
        # Add context if available
        if error.context:
            base_response["operation"] = error.context.operation
            if error.context.request_id:
                base_response["request_id"] = error.context.request_id
        
        # Add specific handling based on error type
        if isinstance(error, ValidationError):
            base_response["error_code"] = "VALIDATION_ERROR"
            base_response["message"] = "Please check your input and try again"
        
        elif isinstance(error, VoiceNotFoundError):
            base_response["error_code"] = "VOICE_NOT_FOUND"
            base_response["message"] = "The requested voice is not available"
        
        elif isinstance(error, AudioGenerationError):
            base_response["error_code"] = "GENERATION_ERROR"
            base_response["message"] = "Failed to generate audio. Please try again"
        
        elif isinstance(error, ModelLoadError):
            base_response["error_code"] = "MODEL_ERROR"
            base_response["message"] = "TTS model is not available"
        
        elif isinstance(error, SystemResourceError):
            base_response["error_code"] = "RESOURCE_ERROR"
            base_response["message"] = "System resources are temporarily unavailable"
        
        else:
            base_response["error_code"] = "UNKNOWN_ERROR"
            base_response["message"] = "An unexpected error occurred"
        
        return base_response

def error_handler(operation: str):
    """Decorator for automatic error handling"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(operation=operation)
                handler = ErrorHandler()
                error_response = handler.handle_error(e, context)
                
                # Convert to appropriate HTTP exception
                from fastapi import HTTPException
                
                if error_response.get("error_code") == "CIRCUIT_BREAKER_ACTIVE":
                    raise HTTPException(status_code=503, detail=error_response)
                elif error_response.get("error_code") == "VALIDATION_ERROR":
                    raise HTTPException(status_code=400, detail=error_response)
                elif error_response.get("error_code") in ["VOICE_NOT_FOUND", "MODEL_ERROR"]:
                    raise HTTPException(status_code=404, detail=error_response)
                elif error_response.get("error_code") == "RESOURCE_ERROR":
                    raise HTTPException(status_code=503, detail=error_response)
                else:
                    raise HTTPException(status_code=500, detail=error_response)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(operation=operation)
                handler = ErrorHandler()
                error_response = handler.handle_error(e, context)
                raise TTSError(
                    message=error_response["error"],
                    severity=ErrorSeverity(error_response["severity"]),
                    context=context,
                    original_error=e
                )
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and 'async' in str(func.__code__):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class GracefulDegradation:
    """Graceful degradation strategies"""
    
    @staticmethod
    def fallback_voice(requested_voice: str, available_voices: list) -> str:
        """Find fallback voice if requested voice unavailable"""
        if not available_voices:
            raise VoiceNotFoundError("No voices available")
        
        # Try to find similar voice
        requested_lower = requested_voice.lower()
        
        # Same gender fallback
        if requested_lower.startswith('af_'):  # American female
            fallbacks = [v for v in available_voices if v.lower().startswith('af_')]
        elif requested_lower.startswith('am_'):  # American male
            fallbacks = [v for v in available_voices if v.lower().startswith('am_')]
        elif requested_lower.startswith('bf_'):  # British female
            fallbacks = [v for v in available_voices if v.lower().startswith('bf_')]
        elif requested_lower.startswith('bm_'):  # British male
            fallbacks = [v for v in available_voices if v.lower().startswith('bm_')]
        else:
            fallbacks = available_voices
        
        if fallbacks:
            return fallbacks[0]
        
        # Last resort - any available voice
        return available_voices[0]
    
    @staticmethod
    def fallback_format(requested_format: str) -> str:
        """Find fallback audio format"""
        format_priority = ["mp3", "wav", "flac", "ogg"]
        
        if requested_format in format_priority:
            return requested_format
        
        # Return most compatible format
        return "mp3"
    
    @staticmethod
    def simplify_text(text: str) -> str:
        """Simplify text if generation fails"""
        import re
        
        # Remove complex punctuation
        simplified = re.sub(r'[^\w\s\.,!?;:\'"()-]', '', text)
        
        # Limit sentence length
        sentences = simplified.split('.')
        if len(sentences) > 3:
            simplified = '. '.join(sentences[:3]) + '.'
        
        # Fallback to very simple text
        if len(simplified) > 200:
            simplified = "I'm sorry, the text was too complex to process."
        
        return simplified
