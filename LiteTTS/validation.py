#!/usr/bin/env python3
"""
Input validation and sanitization for Kokoro ONNX TTS API
Comprehensive validation for all user inputs and system parameters
"""

import re
import html
import unicodedata
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    sanitized_value: Any = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Supported audio formats
    SUPPORTED_FORMATS = {"mp3", "wav", "flac", "ogg", "aac"}
    
    # Text limits
    MIN_TEXT_LENGTH = 1
    MAX_TEXT_LENGTH = 5000
    
    # Speed limits
    MIN_SPEED = 0.1
    MAX_SPEED = 3.0
    
    # Dangerous patterns to filter
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'data:.*base64',             # Data URLs
        r'vbscript:',                 # VBScript
        r'on\w+\s*=',                 # Event handlers
    ]
    
    # Text cleaning patterns
    CONTROL_CHARS = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]')
    EXCESSIVE_WHITESPACE = re.compile(r'\s{3,}')
    REPEATED_PUNCTUATION = re.compile(r'([.!?]){4,}')
    
    @classmethod
    def validate_text(cls, text: str) -> ValidationResult:
        """Validate and sanitize text input"""
        if not isinstance(text, str):
            return ValidationResult(
                is_valid=False,
                error_message="Text must be a string"
            )
        
        # Check for empty or whitespace-only text
        if not text or not text.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Text cannot be empty"
            )
        
        # Check length limits
        if len(text) < cls.MIN_TEXT_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Text too short (minimum {cls.MIN_TEXT_LENGTH} characters)"
            )
        
        if len(text) > cls.MAX_TEXT_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Text too long (maximum {cls.MAX_TEXT_LENGTH} characters)"
            )
        
        warnings = []
        sanitized_text = text
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, sanitized_text, re.IGNORECASE):
                warnings.append("Potentially dangerous content detected and removed")
                sanitized_text = re.sub(pattern, '', sanitized_text, flags=re.IGNORECASE)
        
        # HTML escape for safety
        sanitized_text = html.escape(sanitized_text)
        
        # Normalize Unicode
        sanitized_text = unicodedata.normalize('NFKC', sanitized_text)
        
        # Remove control characters
        sanitized_text = cls.CONTROL_CHARS.sub('', sanitized_text)
        
        # Clean up excessive whitespace
        sanitized_text = cls.EXCESSIVE_WHITESPACE.sub('  ', sanitized_text)
        
        # Limit repeated punctuation
        sanitized_text = cls.REPEATED_PUNCTUATION.sub(r'\1\1\1', sanitized_text)
        
        # Final cleanup
        sanitized_text = sanitized_text.strip()
        
        # Check if sanitization left us with empty text
        if not sanitized_text:
            return ValidationResult(
                is_valid=False,
                error_message="Text became empty after sanitization"
            )
        
        # Check for problematic patterns that might cause phonemizer issues
        if cls._has_phonemizer_issues(sanitized_text):
            warnings.append("Text may cause phonemizer issues - consider simplifying")
        
        return ValidationResult(
            is_valid=True,
            sanitized_value=sanitized_text,
            warnings=warnings
        )
    
    @classmethod
    def validate_voice(cls, voice: str, available_voices: List[str]) -> ValidationResult:
        """Validate voice selection"""
        if not isinstance(voice, str):
            return ValidationResult(
                is_valid=False,
                error_message="Voice must be a string"
            )
        
        if not voice or not voice.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Voice cannot be empty"
            )
        
        # Sanitize voice name
        sanitized_voice = voice.strip().lower()
        
        # Remove any dangerous characters
        sanitized_voice = re.sub(r'[^a-z0-9_-]', '', sanitized_voice)
        
        if not sanitized_voice:
            return ValidationResult(
                is_valid=False,
                error_message="Voice name became empty after sanitization"
            )
        
        # Check if voice exists
        if sanitized_voice not in [v.lower() for v in available_voices]:
            return ValidationResult(
                is_valid=False,
                error_message=f"Voice '{voice}' not found. Available voices: {', '.join(available_voices[:10])}{'...' if len(available_voices) > 10 else ''}"
            )
        
        # Find the actual voice name (preserve case)
        actual_voice = None
        for v in available_voices:
            if v.lower() == sanitized_voice:
                actual_voice = v
                break
        
        return ValidationResult(
            is_valid=True,
            sanitized_value=actual_voice or sanitized_voice
        )
    
    @classmethod
    def validate_format(cls, format_str) -> ValidationResult:
        """Validate audio format with OpenWebUI compatibility"""
        # Handle None/null values (OpenWebUI compatibility)
        if format_str is None:
            return ValidationResult(
                is_valid=True,
                sanitized_value="mp3",  # Default format
                warnings=["response_format was null, defaulting to mp3"]
            )

        # Convert to string if not already (handle numbers, etc.)
        if not isinstance(format_str, str):
            try:
                format_str = str(format_str)
            except (ValueError, TypeError):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Format must be a string or convertible to string, got {type(format_str).__name__}"
                )

        if not format_str or not format_str.strip():
            return ValidationResult(
                is_valid=True,
                sanitized_value="mp3",  # Default for empty string
                warnings=["response_format was empty, defaulting to mp3"]
            )

        # Sanitize format
        sanitized_format = format_str.strip().lower()
        sanitized_format = re.sub(r'[^a-z0-9]', '', sanitized_format)

        if sanitized_format not in cls.SUPPORTED_FORMATS:
            return ValidationResult(
                is_valid=False,
                error_message=f"Unsupported format '{format_str}'. Supported formats: {', '.join(cls.SUPPORTED_FORMATS)}"
            )

        return ValidationResult(
            is_valid=True,
            sanitized_value=sanitized_format
        )
    
    @classmethod
    def validate_speed(cls, speed) -> ValidationResult:
        """Validate speech speed with OpenWebUI compatibility"""
        # Handle None values (OpenWebUI compatibility)
        if speed is None:
            return ValidationResult(
                is_valid=True,
                sanitized_value=1.0,  # Default speed
                warnings=["speed was null, defaulting to 1.0"]
            )

        # Convert string to float if needed (OpenWebUI compatibility)
        if isinstance(speed, str):
            try:
                speed = float(speed.strip())
            except (ValueError, AttributeError):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Speed must be a valid number, got '{speed}'"
                )

        # Check if it's a number
        if not isinstance(speed, (int, float)):
            return ValidationResult(
                is_valid=False,
                error_message=f"Speed must be a number, got {type(speed).__name__}"
            )

        if speed < cls.MIN_SPEED or speed > cls.MAX_SPEED:
            return ValidationResult(
                is_valid=False,
                error_message=f"Speed must be between {cls.MIN_SPEED} and {cls.MAX_SPEED}"
            )

        # Clamp to reasonable precision
        sanitized_speed = round(float(speed), 2)

        warnings = []
        if sanitized_speed < 0.5:
            warnings.append("Very slow speed may result in poor quality")
        elif sanitized_speed > 2.0:
            warnings.append("Very fast speed may result in poor quality")

        return ValidationResult(
            is_valid=True,
            sanitized_value=sanitized_speed,
            warnings=warnings
        )
    
    @classmethod
    def validate_tts_request(cls, request_data: Dict[str, Any], available_voices: List[str]) -> ValidationResult:
        """Validate complete TTS request"""
        if not isinstance(request_data, dict):
            return ValidationResult(
                is_valid=False,
                error_message="Request must be a JSON object"
            )
        
        # Required fields
        required_fields = ["input", "voice"]
        for field in required_fields:
            if field not in request_data:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Missing required field: {field}"
                )
        
        sanitized_request = {}
        all_warnings = []
        
        # Validate text
        text_result = cls.validate_text(request_data["input"])
        if not text_result.is_valid:
            return text_result
        sanitized_request["input"] = text_result.sanitized_value
        all_warnings.extend(text_result.warnings)
        
        # Validate voice
        voice_result = cls.validate_voice(request_data["voice"], available_voices)
        if not voice_result.is_valid:
            return voice_result
        sanitized_request["voice"] = voice_result.sanitized_value
        all_warnings.extend(voice_result.warnings)
        
        # Validate optional fields
        if "response_format" in request_data and request_data["response_format"] is not None:
            format_result = cls.validate_format(request_data["response_format"])
            if not format_result.is_valid:
                return format_result
            sanitized_request["response_format"] = format_result.sanitized_value
            all_warnings.extend(format_result.warnings)
        else:
            # Default to mp3 if field is missing or null (OpenWebUI compatibility)
            sanitized_request["response_format"] = "mp3"
        
        if "speed" in request_data and request_data["speed"] is not None:
            speed_result = cls.validate_speed(request_data["speed"])
            if not speed_result.is_valid:
                return speed_result
            sanitized_request["speed"] = speed_result.sanitized_value
            all_warnings.extend(speed_result.warnings)
        else:
            # Default to 1.0 if field is missing or null (OpenWebUI compatibility)
            sanitized_request["speed"] = 1.0
        
        return ValidationResult(
            is_valid=True,
            sanitized_value=sanitized_request,
            warnings=all_warnings
        )
    
    @classmethod
    def _has_phonemizer_issues(cls, text: str) -> bool:
        """Check if text might cause phonemizer issues"""
        # Patterns that commonly cause phonemizer problems
        problematic_patterns = [
            r'\b\w{20,}\b',           # Very long words
            r'[^\w\s\.,!?;:\'"()-]{3,}',  # Long sequences of special chars
            r'\d{10,}',               # Very long numbers
            r'[A-Z]{10,}',            # Long sequences of capitals
            r'[.!?]{4,}',             # Excessive punctuation
            r'\s{5,}',                # Excessive whitespace
        ]
        
        for pattern in problematic_patterns:
            if re.search(pattern, text):
                return True
        
        return False

class SecurityValidator:
    """Security-focused validation"""
    
    @classmethod
    def validate_file_path(cls, path: str) -> ValidationResult:
        """Validate file paths to prevent directory traversal"""
        if not isinstance(path, str):
            return ValidationResult(
                is_valid=False,
                error_message="Path must be a string"
            )
        
        # Check for directory traversal attempts
        if '..' in path or path.startswith('/'):
            return ValidationResult(
                is_valid=False,
                error_message="Invalid path: directory traversal not allowed"
            )
        
        # Sanitize path
        sanitized_path = re.sub(r'[^a-zA-Z0-9._/-]', '', path)
        
        return ValidationResult(
            is_valid=True,
            sanitized_value=sanitized_path
        )
    
    @classmethod
    def validate_api_key(cls, api_key: str) -> ValidationResult:
        """Validate API key format"""
        if not isinstance(api_key, str):
            return ValidationResult(
                is_valid=False,
                error_message="API key must be a string"
            )
        
        # Basic format validation
        if len(api_key) < 10 or len(api_key) > 100:
            return ValidationResult(
                is_valid=False,
                error_message="Invalid API key format"
            )
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9._-]+$', api_key):
            return ValidationResult(
                is_valid=False,
                error_message="API key contains invalid characters"
            )
        
        return ValidationResult(
            is_valid=True,
            sanitized_value=api_key
        )

def validate_request(request_data: Dict[str, Any], available_voices: List[str]) -> Tuple[bool, Any, List[str]]:
    """
    Convenience function for request validation
    Returns: (is_valid, sanitized_data_or_error_message, warnings)
    """
    result = InputValidator.validate_tts_request(request_data, available_voices)

    if result.is_valid:
        return True, result.sanitized_value, result.warnings or []
    else:
        # Return error message instead of empty dict when validation fails
        error_message = result.error_message or "Validation failed"
        return False, error_message, result.warnings or []
