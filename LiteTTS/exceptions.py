#!/usr/bin/env python3
"""
Custom exceptions for Kokoro ONNX TTS API with enhanced error handling
"""

from typing import Optional, Dict, Any, Union
import traceback
from datetime import datetime

class KokoroError(Exception):
    """Base exception for Kokoro ONNX TTS API with enhanced error context"""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        http_status: int = 500,
        request_id: Optional[str] = None
    ):
        self.message = message
        self.details = details or {}
        self.error_code = error_code or self.__class__.__name__.lower().replace('error', '')
        self.http_status = http_status
        self.request_id = request_id
        self.timestamp = datetime.utcnow().isoformat()
        self.traceback = traceback.format_exc()
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "request_id": self.request_id,
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class ModelError(KokoroError):
    """Raised when there are issues with the TTS model"""
    
    def __init__(self, message: str, model_path: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if model_path:
            details['model_path'] = model_path
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'model_error')
        kwargs.setdefault('http_status', 500)
        super().__init__(message, **kwargs)


class VoiceError(KokoroError):
    """Raised when there are issues with voice processing"""
    
    def __init__(self, message: str, voice_name: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if voice_name:
            details['voice_name'] = voice_name
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'voice_error')
        kwargs.setdefault('http_status', 400)
        super().__init__(message, **kwargs)


class AudioError(KokoroError):
    """Raised when there are issues with audio processing"""
    
    def __init__(self, message: str, audio_format: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if audio_format:
            details['audio_format'] = audio_format
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'audio_error')
        kwargs.setdefault('http_status', 500)
        super().__init__(message, **kwargs)


class ValidationError(KokoroError):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, **kwargs):
        details = kwargs.get('details', {})
        if field:
            details['field'] = field
        if value is not None:
            details['invalid_value'] = str(value)
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'validation_error')
        kwargs.setdefault('http_status', 400)
        super().__init__(message, **kwargs)


class CacheError(KokoroError):
    """Raised when there are caching issues"""
    
    def __init__(self, message: str, cache_key: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if cache_key:
            details['cache_key'] = cache_key
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'cache_error')
        kwargs.setdefault('http_status', 500)
        super().__init__(message, **kwargs)


class ConfigurationError(KokoroError):
    """Raised when there are configuration issues"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'configuration_error')
        kwargs.setdefault('http_status', 500)
        super().__init__(message, **kwargs)


class DownloadError(KokoroError):
    """Raised when model/voice downloads fail"""
    
    def __init__(self, message: str, url: Optional[str] = None, file_path: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if url:
            details['url'] = url
        if file_path:
            details['file_path'] = file_path
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'download_error')
        kwargs.setdefault('http_status', 500)
        super().__init__(message, **kwargs)


class RateLimitError(KokoroError):
    """Raised when rate limits are exceeded"""
    
    def __init__(self, message: str, limit: Optional[int] = None, window: Optional[int] = None, **kwargs):
        details = kwargs.get('details', {})
        if limit:
            details['rate_limit'] = limit
        if window:
            details['window_seconds'] = window
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'rate_limit_exceeded')
        kwargs.setdefault('http_status', 429)
        super().__init__(message, **kwargs)


class AuthenticationError(KokoroError):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication required", **kwargs):
        kwargs.setdefault('error_code', 'authentication_required')
        kwargs.setdefault('http_status', 401)
        super().__init__(message, **kwargs)


class TextProcessingError(KokoroError):
    """Raised when text processing fails"""
    
    def __init__(self, message: str, text_length: Optional[int] = None, **kwargs):
        details = kwargs.get('details', {})
        if text_length:
            details['text_length'] = text_length
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'text_processing_error')
        kwargs.setdefault('http_status', 400)
        super().__init__(message, **kwargs)


# Exception mapping for HTTP status codes
EXCEPTION_STATUS_MAP = {
    ValidationError: 400,
    VoiceError: 400,
    TextProcessingError: 400,
    AuthenticationError: 401,
    RateLimitError: 429,
    ModelError: 500,
    AudioError: 500,
    CacheError: 500,
    ConfigurationError: 500,
    DownloadError: 500,
    KokoroError: 500,
}


def get_http_status(exception: Exception) -> int:
    """Get appropriate HTTP status code for an exception"""
    if isinstance(exception, KokoroError):
        return exception.http_status
    
    for exc_type, status in EXCEPTION_STATUS_MAP.items():
        if isinstance(exception, exc_type):
            return status
    
    return 500  # Default to internal server error