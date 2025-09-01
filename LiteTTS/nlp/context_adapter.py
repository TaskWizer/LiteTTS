#!/usr/bin/env python3
"""
Dynamic synthesis parameter adaptation based on context

This module provides context-aware adaptation of TTS synthesis parameters
for optimal speech quality and appropriateness in different situations.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .emotion_detector import EmotionProfile, EmotionCategory

logger = logging.getLogger(__name__)

class SpeechRegister(Enum):
    """Speech register types for different contexts"""
    FORMAL = "formal"
    CASUAL = "casual"
    INTIMATE = "intimate"
    PUBLIC = "public"
    PROFESSIONAL = "professional"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"

class ContentType(Enum):
    """Content type categories"""
    CONVERSATIONAL = "conversational"
    NARRATIVE = "narrative"
    INSTRUCTIONAL = "instructional"
    PRESENTATIONAL = "presentational"
    INFORMATIONAL = "informational"
    EXPRESSIVE = "expressive"

class AudienceType(Enum):
    """Target audience categories"""
    GENERAL = "general"
    CHILDREN = "children"
    ELDERLY = "elderly"
    PROFESSIONALS = "professionals"
    STUDENTS = "students"
    CUSTOMERS = "customers"

@dataclass
class SpeechContext:
    """Comprehensive speech context information"""
    register: SpeechRegister
    content_type: ContentType
    audience: AudienceType
    emotional_state: Optional[EmotionProfile]
    urgency_level: float  # 0.0 to 1.0
    formality_level: float  # 0.0 to 1.0
    intimacy_level: float  # 0.0 to 1.0
    technical_complexity: float  # 0.0 to 1.0
    time_constraints: Optional[float]  # seconds available
    environment: str  # "quiet", "noisy", "public", "private"

@dataclass
class AdaptationParameters:
    """Synthesis parameters adapted for context"""
    speech_rate: float  # Multiplier for base rate
    pitch_adjustment: float  # Semitones adjustment
    pitch_range: float  # Multiplier for pitch range
    volume_level: float  # Multiplier for volume
    articulation_clarity: float  # 0.0 to 1.0
    emotional_expressiveness: float  # 0.0 to 1.0
    pause_duration_multiplier: float
    emphasis_strength: float  # 0.0 to 1.0
    voice_quality_adjustments: Dict[str, float]

class ContextAdapter:
    """Dynamic context-aware synthesis parameter adaptation"""
    
    def __init__(self):
        """Initialize context adapter with adaptation rules"""
        self.register_adaptations = self._load_register_adaptations()
        self.content_adaptations = self._load_content_adaptations()
        self.audience_adaptations = self._load_audience_adaptations()
        self.environment_adaptations = self._load_environment_adaptations()
        
    def _load_register_adaptations(self) -> Dict[SpeechRegister, Dict[str, float]]:
        """Load speech register adaptation parameters"""
        return {
            SpeechRegister.FORMAL: {
                "speech_rate": 0.95,  # Slightly slower
                "pitch_adjustment": 0.0,  # Neutral pitch
                "pitch_range": 0.9,  # Narrower range
                "articulation_clarity": 1.0,  # Maximum clarity
                "emotional_expressiveness": 0.6,  # Reduced expression
                "pause_duration_multiplier": 1.2,  # Longer pauses
                "emphasis_strength": 0.8  # Moderate emphasis
            },
            SpeechRegister.CASUAL: {
                "speech_rate": 1.05,  # Slightly faster
                "pitch_adjustment": 0.0,
                "pitch_range": 1.1,  # Wider range
                "articulation_clarity": 0.8,  # Relaxed articulation
                "emotional_expressiveness": 1.0,  # Full expression
                "pause_duration_multiplier": 0.9,  # Shorter pauses
                "emphasis_strength": 1.0  # Natural emphasis
            },
            SpeechRegister.INTIMATE: {
                "speech_rate": 0.9,  # Slower, more personal
                "pitch_adjustment": -1.0,  # Slightly lower
                "pitch_range": 0.8,  # Narrower, softer
                "articulation_clarity": 0.7,  # Softer articulation
                "emotional_expressiveness": 1.2,  # Enhanced expression
                "pause_duration_multiplier": 1.3,  # Longer, meaningful pauses
                "emphasis_strength": 0.9  # Gentle emphasis
            },
            SpeechRegister.PUBLIC: {
                "speech_rate": 0.85,  # Slower for clarity
                "pitch_adjustment": 1.0,  # Slightly higher
                "pitch_range": 1.3,  # Wider for projection
                "articulation_clarity": 1.0,  # Maximum clarity
                "emotional_expressiveness": 1.1,  # Enhanced for audience
                "pause_duration_multiplier": 1.4,  # Strategic pauses
                "emphasis_strength": 1.2  # Strong emphasis
            },
            SpeechRegister.PROFESSIONAL: {
                "speech_rate": 1.0,  # Standard rate
                "pitch_adjustment": 0.5,  # Slightly authoritative
                "pitch_range": 1.0,  # Standard range
                "articulation_clarity": 0.95,  # High clarity
                "emotional_expressiveness": 0.7,  # Controlled expression
                "pause_duration_multiplier": 1.1,  # Thoughtful pauses
                "emphasis_strength": 0.9  # Professional emphasis
            }
        }
    
    def _load_content_adaptations(self) -> Dict[ContentType, Dict[str, float]]:
        """Load content type adaptation parameters"""
        return {
            ContentType.CONVERSATIONAL: {
                "speech_rate": 1.0,
                "emotional_expressiveness": 1.0,
                "pause_duration_multiplier": 1.0,
                "emphasis_strength": 1.0,
                "naturalness_enhancement": 1.2  # Enhanced naturalness
            },
            ContentType.NARRATIVE: {
                "speech_rate": 0.95,  # Storytelling pace
                "emotional_expressiveness": 1.3,  # Enhanced for story
                "pause_duration_multiplier": 1.2,  # Dramatic pauses
                "emphasis_strength": 1.1,  # Character emphasis
                "voice_variation": 1.2  # Character voices
            },
            ContentType.INSTRUCTIONAL: {
                "speech_rate": 0.9,  # Clear instruction pace
                "articulation_clarity": 1.0,  # Maximum clarity
                "pause_duration_multiplier": 1.3,  # Processing time
                "emphasis_strength": 1.2,  # Key point emphasis
                "repetition_tolerance": 1.0  # Allow repetition
            },
            ContentType.PRESENTATIONAL: {
                "speech_rate": 0.85,  # Presentation pace
                "pitch_range": 1.2,  # Engaging variation
                "emotional_expressiveness": 1.1,  # Engaging delivery
                "pause_duration_multiplier": 1.4,  # Strategic pauses
                "emphasis_strength": 1.3  # Strong key points
            },
            ContentType.INFORMATIONAL: {
                "speech_rate": 1.0,  # Standard pace
                "articulation_clarity": 0.95,  # High clarity
                "emotional_expressiveness": 0.8,  # Neutral delivery
                "pause_duration_multiplier": 1.1,  # Processing pauses
                "emphasis_strength": 1.0  # Factual emphasis
            }
        }
    
    def _load_audience_adaptations(self) -> Dict[AudienceType, Dict[str, float]]:
        """Load audience-specific adaptation parameters"""
        return {
            AudienceType.CHILDREN: {
                "speech_rate": 0.8,  # Slower for comprehension
                "pitch_adjustment": 2.0,  # Higher, friendlier pitch
                "pitch_range": 1.4,  # More animated
                "emotional_expressiveness": 1.4,  # Very expressive
                "articulation_clarity": 1.0,  # Very clear
                "enthusiasm_boost": 1.3  # More enthusiastic
            },
            AudienceType.ELDERLY: {
                "speech_rate": 0.75,  # Slower for processing
                "pitch_adjustment": 0.0,  # Comfortable pitch
                "articulation_clarity": 1.0,  # Maximum clarity
                "volume_boost": 1.1,  # Slightly louder
                "pause_duration_multiplier": 1.5,  # Longer pauses
                "emphasis_strength": 1.1  # Clear emphasis
            },
            AudienceType.PROFESSIONALS: {
                "speech_rate": 1.1,  # Efficient pace
                "articulation_clarity": 0.9,  # Professional clarity
                "emotional_expressiveness": 0.7,  # Controlled
                "technical_precision": 1.0,  # Accurate pronunciation
                "confidence_boost": 1.1  # Authoritative
            },
            AudienceType.STUDENTS: {
                "speech_rate": 0.9,  # Learning pace
                "articulation_clarity": 0.95,  # Clear for learning
                "pause_duration_multiplier": 1.2,  # Processing time
                "emphasis_strength": 1.2,  # Educational emphasis
                "encouragement_tone": 1.1  # Supportive
            }
        }
    
    def _load_environment_adaptations(self) -> Dict[str, Dict[str, float]]:
        """Load environment-specific adaptations"""
        return {
            "quiet": {
                "volume_level": 0.9,  # Softer in quiet environments
                "articulation_clarity": 0.8,  # Can be more relaxed
                "intimacy_boost": 1.1  # More personal
            },
            "noisy": {
                "volume_level": 1.2,  # Louder to overcome noise
                "articulation_clarity": 1.0,  # Maximum clarity
                "pitch_adjustment": 1.0,  # Higher to cut through
                "emphasis_strength": 1.2  # Stronger emphasis
            },
            "public": {
                "volume_level": 1.1,  # Projected voice
                "articulation_clarity": 1.0,  # Very clear
                "speech_rate": 0.9,  # Slower for audience
                "pause_duration_multiplier": 1.3  # Strategic pauses
            },
            "private": {
                "volume_level": 0.9,  # Softer, more intimate
                "emotional_expressiveness": 1.1,  # More personal
                "intimacy_boost": 1.2  # Enhanced intimacy
            }
        }
    
    def analyze_context(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> SpeechContext:
        """Analyze text and metadata to determine speech context"""
        
        # Extract context clues from text
        register = self._detect_speech_register(text)
        content_type = self._detect_content_type(text)
        audience = self._detect_audience_type(text, metadata)
        
        # Analyze contextual factors
        urgency = self._analyze_urgency(text)
        formality = self._analyze_formality(text)
        intimacy = self._analyze_intimacy(text)
        complexity = self._analyze_technical_complexity(text)
        
        # Extract metadata
        time_constraints = metadata.get("time_limit") if metadata else None
        environment = metadata.get("environment", "quiet") if metadata else "quiet"
        
        return SpeechContext(
            register=register,
            content_type=content_type,
            audience=audience,
            emotional_state=None,  # Set externally
            urgency_level=urgency,
            formality_level=formality,
            intimacy_level=intimacy,
            technical_complexity=complexity,
            time_constraints=time_constraints,
            environment=environment
        )
    
    def _detect_speech_register(self, text: str) -> SpeechRegister:
        """Detect speech register from text content"""
        text_lower = text.lower()
        
        # Formal indicators
        formal_indicators = [
            r'\b(therefore|furthermore|consequently|nevertheless)\b',
            r'\b(shall|would|could|might)\b',
            r'\b(regarding|concerning|pursuant)\b',
            r'\b(ladies and gentlemen|distinguished)\b'
        ]
        
        # Casual indicators
        casual_indicators = [
            r'\b(yeah|yep|nope|gonna|wanna|gotta)\b',
            r'\b(hey|hi|sup|cool|awesome)\b',
            r'\b(like|you know|I mean)\b'
        ]
        
        # Professional indicators
        professional_indicators = [
            r'\b(analysis|strategy|implementation|optimization)\b',
            r'\b(meeting|presentation|report|proposal)\b',
            r'\b(client|customer|stakeholder)\b'
        ]
        
        formal_score = sum(len(re.findall(pattern, text_lower)) for pattern in formal_indicators)
        casual_score = sum(len(re.findall(pattern, text_lower)) for pattern in casual_indicators)
        professional_score = sum(len(re.findall(pattern, text_lower)) for pattern in professional_indicators)
        
        if professional_score > max(formal_score, casual_score):
            return SpeechRegister.PROFESSIONAL
        elif formal_score > casual_score:
            return SpeechRegister.FORMAL
        else:
            return SpeechRegister.CASUAL
    
    def _detect_content_type(self, text: str) -> ContentType:
        """Detect content type from text structure and content"""
        text_lower = text.lower()
        
        # Conversational indicators
        if re.search(r'\b(how are you|what do you think|tell me)\b', text_lower):
            return ContentType.CONVERSATIONAL
        
        # Narrative indicators
        if re.search(r'\b(once upon|story|character|plot)\b', text_lower):
            return ContentType.NARRATIVE
        
        # Instructional indicators
        if re.search(r'\b(step|first|next|then|finally|how to)\b', text_lower):
            return ContentType.INSTRUCTIONAL
        
        # Presentational indicators
        if re.search(r'\b(today|presentation|agenda|overview)\b', text_lower):
            return ContentType.PRESENTATIONAL
        
        return ContentType.INFORMATIONAL
    
    def _detect_audience_type(self, text: str, metadata: Optional[Dict[str, Any]]) -> AudienceType:
        """Detect target audience from text and metadata"""
        if metadata and "audience" in metadata:
            audience_str = metadata["audience"].lower()
            for audience_type in AudienceType:
                if audience_type.value in audience_str:
                    return audience_type
        
        text_lower = text.lower()
        
        # Children indicators
        if re.search(r'\b(kids|children|fun|play|learn)\b', text_lower):
            return AudienceType.CHILDREN
        
        # Professional indicators
        if re.search(r'\b(business|corporate|professional|industry)\b', text_lower):
            return AudienceType.PROFESSIONALS
        
        return AudienceType.GENERAL
    
    def _analyze_urgency(self, text: str) -> float:
        """Analyze urgency level from text"""
        urgency_indicators = [
            (r'\b(urgent|emergency|immediately|asap|now)\b', 1.0),
            (r'\b(quickly|soon|fast|hurry)\b', 0.7),
            (r'\b(when you can|at your convenience)\b', 0.2),
            (r'!{2,}', 0.8),
            (r'\b(deadline|time-sensitive)\b', 0.9)
        ]
        
        max_urgency = 0.0
        for pattern, urgency in urgency_indicators:
            if re.search(pattern, text.lower()):
                max_urgency = max(max_urgency, urgency)
        
        return max_urgency
    
    def _analyze_formality(self, text: str) -> float:
        """Analyze formality level from text"""
        formal_score = 0.0
        informal_score = 0.0
        
        # Formal indicators
        formal_patterns = [
            r'\b(please|thank you|sincerely|respectfully)\b',
            r'\b(Mr\.|Mrs\.|Dr\.|Professor)\b',
            r'\b(would|could|might|shall)\b'
        ]
        
        # Informal indicators
        informal_patterns = [
            r'\b(hey|hi|yeah|nope|gonna)\b',
            r'\b(cool|awesome|great|nice)\b',
            r"[.!?]{2,}"  # Multiple punctuation
        ]
        
        for pattern in formal_patterns:
            formal_score += len(re.findall(pattern, text.lower()))
        
        for pattern in informal_patterns:
            informal_score += len(re.findall(pattern, text.lower()))
        
        total_score = formal_score + informal_score
        if total_score == 0:
            return 0.5  # Neutral
        
        return formal_score / total_score
    
    def _analyze_intimacy(self, text: str) -> float:
        """Analyze intimacy level from text"""
        intimate_indicators = [
            r'\b(love|dear|honey|sweetheart)\b',
            r'\b(personal|private|between us)\b',
            r'\b(feel|emotion|heart)\b'
        ]
        
        intimacy_score = 0.0
        for pattern in intimate_indicators:
            intimacy_score += len(re.findall(pattern, text.lower()))
        
        # Normalize by text length
        words = len(text.split())
        return min(intimacy_score / max(words, 1) * 10, 1.0)
    
    def _analyze_technical_complexity(self, text: str) -> float:
        """Analyze technical complexity from text"""
        technical_indicators = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w{12,}\b',    # Long technical words
            r'\d+\.\d+',       # Numbers with decimals
            r'\b(algorithm|implementation|optimization|configuration)\b'
        ]
        
        complexity_score = 0.0
        for pattern in technical_indicators:
            complexity_score += len(re.findall(pattern, text))
        
        # Normalize by text length
        words = len(text.split())
        return min(complexity_score / max(words, 1) * 5, 1.0)
    
    def adapt_synthesis_parameters(self, context: SpeechContext) -> AdaptationParameters:
        """Generate adapted synthesis parameters for given context"""
        
        # Start with base parameters
        params = AdaptationParameters(
            speech_rate=1.0,
            pitch_adjustment=0.0,
            pitch_range=1.0,
            volume_level=1.0,
            articulation_clarity=0.9,
            emotional_expressiveness=1.0,
            pause_duration_multiplier=1.0,
            emphasis_strength=1.0,
            voice_quality_adjustments={}
        )
        
        # Apply register adaptations
        if context.register in self.register_adaptations:
            self._apply_adaptations(params, self.register_adaptations[context.register])
        
        # Apply content type adaptations
        if context.content_type in self.content_adaptations:
            self._apply_adaptations(params, self.content_adaptations[context.content_type])
        
        # Apply audience adaptations
        if context.audience in self.audience_adaptations:
            self._apply_adaptations(params, self.audience_adaptations[context.audience])
        
        # Apply environment adaptations
        if context.environment in self.environment_adaptations:
            self._apply_adaptations(params, self.environment_adaptations[context.environment])
        
        # Apply emotional adaptations
        if context.emotional_state:
            self._apply_emotional_adaptations(params, context.emotional_state)
        
        # Apply contextual factor adjustments
        self._apply_contextual_adjustments(params, context)
        
        return params
    
    def _apply_adaptations(self, params: AdaptationParameters, adaptations: Dict[str, float]):
        """Apply adaptation values to parameters"""
        for key, value in adaptations.items():
            if hasattr(params, key):
                current_value = getattr(params, key)
                if isinstance(current_value, float):
                    # Multiplicative adaptation for most parameters
                    if key in ["speech_rate", "pitch_range", "volume_level", 
                              "pause_duration_multiplier", "emphasis_strength"]:
                        setattr(params, key, current_value * value)
                    # Additive adaptation for adjustments
                    elif key.endswith("_adjustment"):
                        setattr(params, key, current_value + value)
                    # Direct assignment for others
                    else:
                        setattr(params, key, value)
    
    def _apply_emotional_adaptations(self, params: AdaptationParameters, 
                                   emotion: EmotionProfile):
        """Apply emotional adaptations to parameters"""
        if emotion.prosodic_parameters:
            for key, value in emotion.prosodic_parameters.items():
                if key == "pitch_shift":
                    params.pitch_adjustment += value * emotion.intensity
                elif key == "pitch_range":
                    params.pitch_range *= (1.0 + (value - 1.0) * emotion.intensity)
                elif key == "rate_change":
                    params.speech_rate *= (1.0 + (value - 1.0) * emotion.intensity)
                elif key == "energy":
                    params.volume_level *= (1.0 + (value - 1.0) * emotion.intensity)
    
    def _apply_contextual_adjustments(self, params: AdaptationParameters, 
                                    context: SpeechContext):
        """Apply contextual factor adjustments"""
        
        # Urgency adjustments
        if context.urgency_level > 0.5:
            params.speech_rate *= (1.0 + context.urgency_level * 0.2)
            params.emphasis_strength *= (1.0 + context.urgency_level * 0.3)
        
        # Formality adjustments
        formality_factor = context.formality_level
        params.articulation_clarity = max(params.articulation_clarity, 
                                        0.8 + formality_factor * 0.2)
        params.emotional_expressiveness *= (1.0 - formality_factor * 0.3)
        
        # Intimacy adjustments
        if context.intimacy_level > 0.5:
            params.volume_level *= (1.0 - context.intimacy_level * 0.2)
            params.emotional_expressiveness *= (1.0 + context.intimacy_level * 0.3)
        
        # Technical complexity adjustments
        if context.technical_complexity > 0.5:
            params.speech_rate *= (1.0 - context.technical_complexity * 0.2)
            params.pause_duration_multiplier *= (1.0 + context.technical_complexity * 0.3)
            params.articulation_clarity = max(params.articulation_clarity, 0.95)
        
        # Time constraint adjustments
        if context.time_constraints and context.time_constraints < 30:
            # Speed up for time constraints
            time_pressure = max(0, (30 - context.time_constraints) / 30)
            params.speech_rate *= (1.0 + time_pressure * 0.3)
            params.pause_duration_multiplier *= (1.0 - time_pressure * 0.2)

        return params
