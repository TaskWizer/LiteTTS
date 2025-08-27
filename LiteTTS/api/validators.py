#!/usr/bin/env python3
"""
Request validation for TTS API
"""

from typing import List, Dict, Any, Optional
import re
import logging

from LiteTTS.models import TTSRequest, validate_tts_request
from ..tts.synthesizer import TTSSynthesizer

logger = logging.getLogger(__name__)

class RequestValidator:
    """Validates TTS API requests"""
    
    def __init__(self, synthesizer: TTSSynthesizer):
        self.synthesizer = synthesizer
        
        # Validation rules
        self.max_text_length = 10000
        self.min_text_length = 1
        self.max_speed = 3.0
        self.min_speed = 0.1
        self.max_volume = 5.0
        self.min_volume = 0.1
        self.max_emotion_strength = 2.0
        self.min_emotion_strength = 0.0
        
        # Supported formats
        self.supported_formats = ['mp3', 'wav', 'ogg', 'flac']
        
        # Text content filters
        self.forbidden_patterns = [
            re.compile(r'<script.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'data:.*?base64', re.IGNORECASE)
        ]
        
        logger.info("Request validator initialized")
    
    def validate_request(self, request: TTSRequest) -> List[str]:
        """Validate a TTS request and return list of errors"""
        errors = []
        
        # Basic validation using the model's validator
        basic_errors = validate_tts_request(request)
        errors.extend(basic_errors)
        
        # Text validation
        text_errors = self._validate_text(request.input)
        errors.extend(text_errors)
        
        # Voice validation
        voice_errors = self._validate_voice(request.voice)
        errors.extend(voice_errors)
        
        # Speed validation
        speed_errors = self._validate_speed(request.speed)
        errors.extend(speed_errors)
        
        # Format validation
        format_errors = self._validate_format(request.response_format)
        errors.extend(format_errors)
        
        # Volume validation
        volume_errors = self._validate_volume(request.volume_multiplier)
        errors.extend(volume_errors)
        
        # Emotion validation (if present)
        emotion = getattr(request, 'emotion', None)
        if emotion:
            emotion_errors = self._validate_emotion(emotion)
            errors.extend(emotion_errors)
            
            emotion_strength = getattr(request, 'emotion_strength', 1.0)
            strength_errors = self._validate_emotion_strength(emotion_strength)
            errors.extend(strength_errors)
        
        # Language code validation
        lang_errors = self._validate_language_code(request.lang_code)
        errors.extend(lang_errors)
        
        return errors
    
    def _validate_text(self, text: str) -> List[str]:
        """Validate input text"""
        errors = []
        
        if not text or not text.strip():
            errors.append("Input text cannot be empty")
            return errors
        
        # Length validation
        if len(text) < self.min_text_length:
            errors.append(f"Text too short (minimum {self.min_text_length} characters)")
        
        if len(text) > self.max_text_length:
            errors.append(f"Text too long (maximum {self.max_text_length} characters)")
        
        # Content validation
        for pattern in self.forbidden_patterns:
            if pattern.search(text):
                errors.append("Text contains forbidden content")
                break
        
        # Check for excessive repetition
        if self._has_excessive_repetition(text):
            errors.append("Text contains excessive repetition")
        
        # Check for valid characters
        if not self._has_valid_characters(text):
            errors.append("Text contains unsupported characters")
        
        return errors
    
    def _validate_voice(self, voice: str) -> List[str]:
        """Validate voice parameter"""
        errors = []
        
        if not voice:
            errors.append("Voice parameter is required")
            return errors
        
        available_voices = self.synthesizer.get_available_voices()
        if voice not in available_voices:
            errors.append(f"Voice '{voice}' not available. Available voices: {available_voices}")
        
        return errors
    
    def _validate_speed(self, speed: float) -> List[str]:
        """Validate speed parameter"""
        errors = []
        
        if not isinstance(speed, (int, float)):
            errors.append("Speed must be a number")
            return errors
        
        if speed < self.min_speed:
            errors.append(f"Speed too low (minimum {self.min_speed})")
        
        if speed > self.max_speed:
            errors.append(f"Speed too high (maximum {self.max_speed})")
        
        return errors
    
    def _validate_format(self, format: str) -> List[str]:
        """Validate response format"""
        errors = []
        
        if not format:
            errors.append("Response format is required")
            return errors
        
        if format.lower() not in self.supported_formats:
            errors.append(f"Format '{format}' not supported. Supported formats: {self.supported_formats}")
        
        return errors
    
    def _validate_volume(self, volume: float) -> List[str]:
        """Validate volume multiplier"""
        errors = []
        
        if not isinstance(volume, (int, float)):
            errors.append("Volume multiplier must be a number")
            return errors
        
        if volume < self.min_volume:
            errors.append(f"Volume too low (minimum {self.min_volume})")
        
        if volume > self.max_volume:
            errors.append(f"Volume too high (maximum {self.max_volume})")
        
        return errors
    
    def _validate_emotion(self, emotion: str) -> List[str]:
        """Validate emotion parameter"""
        errors = []
        
        if not emotion:
            return errors  # Emotion is optional
        
        supported_emotions = self.synthesizer.get_supported_emotions()
        if emotion not in supported_emotions:
            errors.append(f"Emotion '{emotion}' not supported. Supported emotions: {supported_emotions}")
        
        return errors
    
    def _validate_emotion_strength(self, strength: float) -> List[str]:
        """Validate emotion strength parameter"""
        errors = []
        
        if not isinstance(strength, (int, float)):
            errors.append("Emotion strength must be a number")
            return errors
        
        if strength < self.min_emotion_strength:
            errors.append(f"Emotion strength too low (minimum {self.min_emotion_strength})")
        
        if strength > self.max_emotion_strength:
            errors.append(f"Emotion strength too high (maximum {self.max_emotion_strength})")
        
        return errors
    
    def _validate_language_code(self, lang_code: str) -> List[str]:
        """Validate language code"""
        errors = []
        
        if not lang_code:
            errors.append("Language code is required")
            return errors
        
        # Simple validation for language code format
        if not re.match(r'^[a-z]{2}(-[a-z]{2})?$', lang_code.lower()):
            errors.append("Invalid language code format (expected: 'en' or 'en-us')")
        
        # For now, only support English
        if not lang_code.lower().startswith('en'):
            errors.append("Only English language is currently supported")
        
        return errors
    
    def _has_excessive_repetition(self, text: str) -> bool:
        """Check for excessive character or word repetition"""
        # Check for repeated characters (more than 10 in a row)
        if re.search(r'(.)\1{10,}', text):
            return True
        
        # Check for repeated words
        words = text.split()
        if len(words) > 10:
            # Check if more than 50% of words are the same
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            max_count = max(word_counts.values())
            if max_count > len(words) * 0.5:
                return True
        
        return False
    
    def _has_valid_characters(self, text: str) -> bool:
        """Check if text contains only valid characters"""
        # Allow most printable characters, including Unicode
        # Exclude control characters except common ones
        allowed_control_chars = {'\n', '\r', '\t'}
        
        for char in text:
            if char.isprintable() or char in allowed_control_chars:
                continue
            else:
                return False
        
        return True
    
    def validate_batch_request(self, texts: List[str], voice: str) -> Dict[str, List[str]]:
        """Validate a batch synthesis request"""
        validation_results = {}
        
        # Validate voice once
        voice_errors = self._validate_voice(voice)
        if voice_errors:
            validation_results['voice'] = voice_errors
        
        # Validate each text
        text_errors = {}
        for i, text in enumerate(texts):
            errors = self._validate_text(text)
            if errors:
                text_errors[f'text_{i}'] = errors
        
        if text_errors:
            validation_results['texts'] = text_errors
        
        # Check batch size
        if len(texts) > 100:  # Reasonable batch limit
            validation_results['batch'] = ["Batch size too large (maximum 100 texts)"]
        
        return validation_results
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get current validation rules"""
        return {
            'text': {
                'min_length': self.min_text_length,
                'max_length': self.max_text_length,
                'forbidden_patterns': [p.pattern for p in self.forbidden_patterns]
            },
            'speed': {
                'min': self.min_speed,
                'max': self.max_speed
            },
            'volume': {
                'min': self.min_volume,
                'max': self.max_volume
            },
            'emotion_strength': {
                'min': self.min_emotion_strength,
                'max': self.max_emotion_strength
            },
            'supported_formats': self.supported_formats,
            'supported_voices': self.synthesizer.get_available_voices(),
            'supported_emotions': self.synthesizer.get_supported_emotions()
        }