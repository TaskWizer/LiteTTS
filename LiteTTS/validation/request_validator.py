"""
Request Validation for LiteTTS

This module provides request validation functionality for TTS requests,
ensuring data integrity and proper parameter validation.
"""

import logging
from typing import Dict, Any, List, Tuple, Union, Optional

logger = logging.getLogger(__name__)


def validate_request(request_data: Dict[str, Any], available_voices: List[str]) -> Tuple[bool, Union[Dict[str, Any], str], List[str]]:
    """
    Validate and sanitize a TTS request.
    
    Args:
        request_data: Dictionary containing request parameters
        available_voices: List of available voice names
        
    Returns:
        Tuple of (is_valid, data_or_error, warnings)
        - is_valid: Boolean indicating if request is valid
        - data_or_error: Validated data dict if valid, error message if invalid
        - warnings: List of warning messages
    """
    warnings = []
    validated_data = {}
    
    try:
        # Validate required input field
        if "input" not in request_data:
            return False, "Missing required field: 'input'", warnings
        
        input_text = request_data["input"]
        if not isinstance(input_text, str):
            return False, "Field 'input' must be a string", warnings
        
        if not input_text.strip():
            return False, "Field 'input' cannot be empty", warnings
        
        # Validate input length (reasonable limits)
        if len(input_text) > 10000:  # 10k character limit
            return False, "Input text too long (maximum 10,000 characters)", warnings
        
        validated_data["input"] = input_text.strip()
        
        # Validate voice field
        voice = request_data.get("voice")
        if voice is not None:
            if not isinstance(voice, str):
                return False, "Field 'voice' must be a string", warnings
            
            if voice not in available_voices:
                # Try to find a close match
                voice_lower = voice.lower()
                close_matches = [v for v in available_voices if v.lower() == voice_lower]
                
                if close_matches:
                    validated_data["voice"] = close_matches[0]
                    warnings.append(f"Voice '{voice}' not found, using '{close_matches[0]}' instead")
                else:
                    return False, f"Voice '{voice}' not available. Available voices: {', '.join(available_voices[:10])}{'...' if len(available_voices) > 10 else ''}", warnings
            else:
                validated_data["voice"] = voice
        else:
            # Voice will be set to default by the application
            validated_data["voice"] = None
        
        # Validate response_format field
        response_format = request_data.get("response_format")
        if response_format is not None:
            # Convert to string and validate
            if isinstance(response_format, (int, bool)):
                response_format = str(response_format).lower()
            elif not isinstance(response_format, str):
                return False, "Field 'response_format' must be a string", warnings
            
            # Normalize format
            response_format = response_format.lower().strip()
            
            # Valid audio formats
            valid_formats = ["mp3", "wav", "ogg", "flac", "aac", "opus"]
            
            if response_format and response_format not in valid_formats:
                warnings.append(f"Unknown response format '{response_format}', will use default")
                validated_data["response_format"] = None
            else:
                validated_data["response_format"] = response_format if response_format else None
        else:
            validated_data["response_format"] = None
        
        # Validate speed field
        speed = request_data.get("speed")
        if speed is not None:
            try:
                if isinstance(speed, str):
                    speed = float(speed)
                elif not isinstance(speed, (int, float)):
                    return False, "Field 'speed' must be a number", warnings
                
                # Reasonable speed limits (0.25x to 4.0x)
                if speed < 0.25 or speed > 4.0:
                    return False, "Field 'speed' must be between 0.25 and 4.0", warnings
                
                validated_data["speed"] = float(speed)
            except (ValueError, TypeError):
                return False, "Field 'speed' must be a valid number", warnings
        else:
            validated_data["speed"] = None
        
        # Validate model field (OpenWebUI compatibility - accept but ignore)
        model = request_data.get("model")
        if model is not None:
            if not isinstance(model, str):
                warnings.append("Field 'model' should be a string, ignoring")
            else:
                warnings.append(f"Model field '{model}' ignored (using configured model)")
        
        # Additional validation for other fields
        for key, value in request_data.items():
            if key not in ["input", "voice", "response_format", "speed", "model"]:
                warnings.append(f"Unknown field '{key}' ignored")
        
        # Validate text content for potential issues
        if len(validated_data["input"]) < 3:
            warnings.append("Very short input text may not produce good audio quality")
        
        # Check for potentially problematic characters
        problematic_chars = set(validated_data["input"]) & set("[]{}()<>|\\")
        if problematic_chars:
            warnings.append(f"Input contains potentially problematic characters: {', '.join(problematic_chars)}")
        
        return True, validated_data, warnings
        
    except Exception as e:
        logger.error(f"Unexpected error during request validation: {e}")
        return False, f"Internal validation error: {str(e)}", warnings


def validate_voice_name(voice: str, available_voices: List[str]) -> Tuple[bool, Optional[str], List[str]]:
    """
    Validate a voice name against available voices.
    
    Args:
        voice: Voice name to validate
        available_voices: List of available voice names
        
    Returns:
        Tuple of (is_valid, validated_voice, warnings)
    """
    warnings = []
    
    if not isinstance(voice, str):
        return False, None, ["Voice must be a string"]
    
    if voice in available_voices:
        return True, voice, warnings
    
    # Try case-insensitive match
    voice_lower = voice.lower()
    for available_voice in available_voices:
        if available_voice.lower() == voice_lower:
            warnings.append(f"Voice name case corrected: '{voice}' -> '{available_voice}'")
            return True, available_voice, warnings
    
    # Try partial matches
    partial_matches = [v for v in available_voices if voice_lower in v.lower() or v.lower() in voice_lower]
    if partial_matches:
        best_match = partial_matches[0]
        warnings.append(f"Voice '{voice}' not found, suggesting '{best_match}'")
        return False, best_match, warnings
    
    return False, None, [f"Voice '{voice}' not available"]


def validate_audio_format(format_str: str) -> Tuple[bool, Optional[str], List[str]]:
    """
    Validate audio format string.
    
    Args:
        format_str: Audio format string to validate
        
    Returns:
        Tuple of (is_valid, normalized_format, warnings)
    """
    warnings = []
    
    if not isinstance(format_str, str):
        return False, None, ["Audio format must be a string"]
    
    # Normalize format
    normalized = format_str.lower().strip()
    
    # Remove common prefixes/suffixes
    if normalized.startswith("audio/"):
        normalized = normalized[6:]
    if normalized.startswith("."):
        normalized = normalized[1:]
    
    # Valid formats
    valid_formats = {
        "mp3": "mp3",
        "mpeg": "mp3",
        "wav": "wav",
        "wave": "wav",
        "ogg": "ogg",
        "flac": "flac",
        "aac": "aac",
        "opus": "opus",
        "m4a": "aac"
    }
    
    if normalized in valid_formats:
        return True, valid_formats[normalized], warnings
    
    # Check for common misspellings
    if normalized in ["mp4", "m4v"]:
        warnings.append(f"Format '{format_str}' is video format, using 'mp3' instead")
        return True, "mp3", warnings
    
    return False, None, [f"Unsupported audio format: '{format_str}'"]


def validate_speed_value(speed: Union[str, int, float]) -> Tuple[bool, Optional[float], List[str]]:
    """
    Validate speed value.
    
    Args:
        speed: Speed value to validate
        
    Returns:
        Tuple of (is_valid, validated_speed, warnings)
    """
    warnings = []
    
    try:
        if isinstance(speed, str):
            speed_float = float(speed)
        elif isinstance(speed, (int, float)):
            speed_float = float(speed)
        else:
            return False, None, ["Speed must be a number"]
        
        # Validate range
        if speed_float < 0.1:
            return False, None, ["Speed too slow (minimum 0.1)"]
        if speed_float > 5.0:
            return False, None, ["Speed too fast (maximum 5.0)"]
        
        # Warn about extreme values
        if speed_float < 0.5:
            warnings.append("Very slow speed may affect audio quality")
        elif speed_float > 2.0:
            warnings.append("Very fast speed may affect audio quality")
        
        return True, speed_float, warnings
        
    except (ValueError, TypeError):
        return False, None, ["Invalid speed value"]


def sanitize_input_text(text: str) -> Tuple[str, List[str]]:
    """
    Sanitize input text for TTS processing.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Tuple of (sanitized_text, warnings)
    """
    warnings = []
    
    if not isinstance(text, str):
        return "", ["Input must be a string"]
    
    # Remove excessive whitespace
    sanitized = " ".join(text.split())
    
    # Check for length
    if len(sanitized) != len(text):
        warnings.append("Excessive whitespace removed")
    
    # Check for very long text
    if len(sanitized) > 5000:
        warnings.append("Very long text may take significant time to process")
    
    # Check for special characters that might cause issues
    if any(ord(c) > 127 for c in sanitized):
        warnings.append("Non-ASCII characters detected - ensure proper pronunciation")
    
    return sanitized, warnings
