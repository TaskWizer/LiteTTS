#!/usr/bin/env python3
"""
LLM-based context analyzer for enhanced emotional and prosodic analysis
Provides deep contextual understanding for TTS emotional enhancement
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import time

logger = logging.getLogger(__name__)

class EmotionalIntensity(Enum):
    """Emotional intensity levels"""
    VERY_LOW = 0.1
    LOW = 0.3
    MODERATE = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9

class ContextualEmotion(Enum):
    """Contextual emotion categories"""
    NEUTRAL = "neutral"
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    EXCITEMENT = "excitement"
    CALM = "calm"
    ANXIETY = "anxiety"
    CONFIDENCE = "confidence"
    UNCERTAINTY = "uncertainty"
    EMPATHY = "empathy"
    SARCASM = "sarcasm"
    HUMOR = "humor"

@dataclass
class EmotionalContext:
    """Comprehensive emotional context analysis"""
    primary_emotion: ContextualEmotion
    secondary_emotions: List[Tuple[ContextualEmotion, float]] = field(default_factory=list)
    intensity: EmotionalIntensity = EmotionalIntensity.MODERATE
    confidence: float = 0.5
    emotional_trajectory: List[ContextualEmotion] = field(default_factory=list)
    contextual_factors: Dict[str, Any] = field(default_factory=dict)
    prosodic_suggestions: Dict[str, float] = field(default_factory=dict)

@dataclass
class ProsodyContext:
    """Prosodic context analysis"""
    speech_rate_modifier: float = 1.0
    pitch_range_modifier: float = 1.0
    volume_modifier: float = 1.0
    pause_patterns: List[Tuple[int, float]] = field(default_factory=list)  # (position, duration)
    emphasis_points: List[Tuple[int, int, float]] = field(default_factory=list)  # (start, end, strength)
    intonation_contour: str = "neutral"  # rising, falling, rising-falling, etc.

@dataclass
class LLMContextAnalysis:
    """Complete LLM-based context analysis"""
    emotional_context: EmotionalContext
    prosody_context: ProsodyContext
    confidence_score: float
    processing_time: float
    analysis_method: str = "rule_based"  # rule_based, llm_enhanced, hybrid

class LLMContextAnalyzer:
    """LLM-based context analyzer for emotional and prosodic enhancement"""
    
    def __init__(self, enable_llm: bool = False):
        self.enable_llm = enable_llm
        self.emotional_patterns = self._load_emotional_patterns()
        self.prosodic_patterns = self._load_prosodic_patterns()
        self.contextual_rules = self._load_contextual_rules()
        
        # LLM integration (placeholder for future implementation)
        self.llm_client = None
        if enable_llm:
            self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize LLM client (placeholder for future implementation)"""
        # This would initialize an actual LLM client (OpenAI, Anthropic, etc.)
        # For now, we'll use enhanced rule-based analysis
        logger.info("LLM enhancement requested but not implemented - using enhanced rule-based analysis")
        self.llm_client = None
    
    def _load_emotional_patterns(self) -> Dict[str, Any]:
        """Load emotional pattern recognition rules"""
        return {
            'joy_patterns': [
                r'\b(happy|joy|joyful|delighted|cheerful|bright|sunny)\b',
                r'\b(love|adore|enjoy|celebrate)\b',
                r'\b(wonderful|amazing|fantastic)\b.*\b(happy|joy|excited)\b',
                r'\b(haha|hehe|lol|yay|woohoo)\b'
            ],
            'sadness_patterns': [
                r'\b(sad|depressed|disappointed|heartbroken|grief|sorrow|melancholy)\b',
                r'\b(cry|tears|weep|mourn|devastated|tragic|unfortunate)\b',
                r'\b(miss|lost|gone|empty|lonely|isolated)\b'
            ],
            'anger_patterns': [
                r'\b(angry|furious|rage|mad|irritated|annoyed|frustrated)\b',
                r'\b(hate|despise|outraged|livid|infuriated|disgusted)\b',
                r'\b(terrible|awful|horrible|disgusting|outrageous)\b.*\b(angry|mad|furious)\b',
                r'\b(damn|hell|stupid|ridiculous|absurd)\b'
            ],
            'fear_patterns': [
                r'\b(afraid|scared|terrified|frightened|anxious|worried|nervous)\b',
                r'\b(panic|dread|horror|alarmed|concerned|uneasy)\b',
                r'\b(dangerous|threat|risk|unsafe|vulnerable)\b'
            ],
            'surprise_patterns': [
                r'\b(surprised|shocked|amazed|astonished|stunned|bewildered)\b',
                r'\b(wow|whoa|oh my|incredible|unbelievable|unexpected)\b',
                r'\?{2,}',  # Multiple question marks
                r'\b(suddenly|abruptly|out of nowhere)\b'
            ],
            'excitement_patterns': [
                r'\b(excited|thrilled|pumped|energized|enthusiastic|eager)\b',
                r'\b(can\'t wait|looking forward|anticipate|ready)\b',
                r'[!]+\s*[!]+',  # Multiple exclamation patterns
            ],
            'calm_patterns': [
                r'\b(calm|peaceful|serene|tranquil|relaxed|composed)\b',
                r'\b(gentle|soft|quiet|still|steady|balanced)\b',
                r'\b(breathe|meditate|rest|pause|slow)\b'
            ],
            'confidence_patterns': [
                r'\b(confident|sure|certain|positive|determined|strong)\b',
                r'\b(will|shall|definitely|absolutely|certainly|undoubtedly)\b',
                r'\b(know|believe|trust|convinced|assured)\b'
            ],
            'uncertainty_patterns': [
                r'\b(maybe|perhaps|possibly|might|could|uncertain|unsure)\b',
                r'\b(think|guess|suppose|wonder|doubt|question)\b',
                r'\?',  # Question marks
                r'\b(probably|likely|seems|appears|looks like)\b'
            ],
            'sarcasm_patterns': [
                r'\b(oh really|sure thing|right|obviously|clearly|of course)\b',
                r'\b(great|wonderful|fantastic|perfect)\b.*\b(not|hardly|barely)\b',
                r'\"[^\"]*\"',  # Quoted text often sarcastic
            ]
        }
    
    def _load_prosodic_patterns(self) -> Dict[str, Any]:
        """Load prosodic pattern recognition rules"""
        return {
            'question_patterns': [
                r'\?',
                r'\b(what|who|when|where|why|how|which|whose)\b',
                r'\b(is|are|was|were|do|does|did|can|could|will|would|should)\b.*\?',
                r'\b(do you|are you|can you|will you|would you)\b'
            ],
            'exclamation_patterns': [
                r'!',
                r'\b(wow|amazing|incredible|fantastic|wonderful|terrible|awful)\b',
                r'\b(stop|wait|help|look|listen)\b'
            ],
            'emphasis_patterns': [
                r'\b[A-Z]{2,}\b',  # ALL CAPS
                r'\*[^*]+\*',  # *emphasized*
                r'\b(very|really|extremely|incredibly|absolutely|totally)\b',
                r'\b(never|always|everyone|everything|nothing|nobody)\b'
            ],
            'pause_patterns': [
                r'[,;:]',  # Commas, semicolons, colons
                r'\.{2,}',  # Ellipses
                r'\s-\s',  # Dashes
                r'\([^)]*\)',  # Parenthetical content
                r'\b(um|uh|er|ah|well|so|now|then)\b'  # Filler words
            ]
        }
    
    def _load_contextual_rules(self) -> Dict[str, Any]:
        """Load contextual analysis rules"""
        return {
            'sentence_types': {
                'declarative': r'^[A-Z][^.!?]*\.$',
                'interrogative': r'^[A-Z][^.!?]*\?$',
                'exclamatory': r'^[A-Z][^.!?]*!$',
                'imperative': r'^[A-Z]*\b(please|go|come|stop|wait|look|listen|do|don\'t)\b'
            },
            'emotional_modifiers': {
                'intensifiers': r'\b(very|really|extremely|incredibly|absolutely|totally|completely)\b',
                'diminishers': r'\b(slightly|somewhat|rather|quite|fairly|pretty|kind of|sort of)\b',
                'negations': r'\b(not|no|never|nothing|nobody|nowhere|neither|nor)\b'
            },
            'contextual_cues': {
                'time_pressure': r'\b(urgent|hurry|quick|fast|immediately|now|asap)\b',
                'formality': r'\b(please|thank you|sir|madam|respectfully|sincerely)\b',
                'intimacy': r'\b(dear|honey|sweetheart|love|buddy|pal|friend)\b',
                'uncertainty': r'\b(maybe|perhaps|possibly|might|could|seems|appears)\b'
            }
        }
    
    def analyze_context(self, text: str, conversation_history: Optional[List[str]] = None) -> LLMContextAnalysis:
        """Perform comprehensive context analysis"""
        start_time = time.perf_counter()
        
        # Analyze emotional context
        emotional_context = self._analyze_emotional_context(text, conversation_history)
        
        # Analyze prosodic context
        prosody_context = self._analyze_prosodic_context(text)
        
        # Calculate overall confidence
        confidence_score = self._calculate_confidence(emotional_context, prosody_context)
        
        processing_time = time.perf_counter() - start_time
        
        analysis = LLMContextAnalysis(
            emotional_context=emotional_context,
            prosody_context=prosody_context,
            confidence_score=confidence_score,
            processing_time=processing_time,
            analysis_method="enhanced_rule_based" if not self.enable_llm else "llm_enhanced"
        )
        
        logger.debug(f"Context analysis completed in {processing_time:.3f}s with confidence {confidence_score:.2f}")
        return analysis
    
    def _analyze_emotional_context(self, text: str, history: Optional[List[str]] = None) -> EmotionalContext:
        """Analyze emotional context of the text"""
        emotion_scores = {}
        
        # Analyze each emotion pattern
        for emotion_type, patterns in self.emotional_patterns.items():
            emotion_name = emotion_type.replace('_patterns', '')
            score = 0.0
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches) * 0.2
            
            if score > 0:
                emotion_scores[emotion_name] = min(score, 1.0)
        
        # Determine primary emotion
        if emotion_scores:
            primary_emotion_name = max(emotion_scores, key=emotion_scores.get)
            primary_emotion = self._map_to_contextual_emotion(primary_emotion_name)
            intensity = self._calculate_intensity(emotion_scores[primary_emotion_name])
        else:
            primary_emotion_name = "neutral"
            primary_emotion = ContextualEmotion.NEUTRAL
            intensity = EmotionalIntensity.LOW

        # Calculate secondary emotions
        secondary_emotions = []
        for emotion_name, score in emotion_scores.items():
            if emotion_name != primary_emotion_name and score > 0.1:
                emotion = self._map_to_contextual_emotion(emotion_name)
                secondary_emotions.append((emotion, score))
        
        # Sort secondary emotions by score
        secondary_emotions.sort(key=lambda x: x[1], reverse=True)
        secondary_emotions = secondary_emotions[:3]  # Keep top 3
        
        # Analyze conversation history for emotional trajectory
        trajectory = []
        if history:
            for hist_text in history[-3:]:  # Last 3 messages
                hist_analysis = self._analyze_emotional_context(hist_text)
                trajectory.append(hist_analysis.primary_emotion)
        
        # Generate prosodic suggestions
        prosodic_suggestions = self._generate_prosodic_suggestions(primary_emotion, intensity)
        
        return EmotionalContext(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            intensity=intensity,
            confidence=min(max(emotion_scores.get(primary_emotion_name, 0), 0.1), 0.9),
            emotional_trajectory=trajectory,
            contextual_factors={
                'text_length': len(text),
                'sentence_count': len(re.findall(r'[.!?]+', text)),
                'exclamation_count': len(re.findall(r'!', text)),
                'question_count': len(re.findall(r'\?', text))
            },
            prosodic_suggestions=prosodic_suggestions
        )
    
    def _analyze_prosodic_context(self, text: str) -> ProsodyContext:
        """Analyze prosodic context of the text"""
        # Detect pause patterns
        pause_patterns = []
        for match in re.finditer(r'[,;:.]|\s-\s|\.{2,}', text):
            pause_duration = 0.3 if match.group() in ',;:' else 0.5
            pause_patterns.append((match.start(), pause_duration))
        
        # Detect emphasis points
        emphasis_points = []
        for match in re.finditer(r'\b[A-Z]{2,}\b|\*[^*]+\*', text):
            emphasis_points.append((match.start(), match.end(), 0.7))
        
        # Determine speech rate modifier
        speech_rate_modifier = 1.0
        if re.search(r'\b(urgent|hurry|quick|fast)\b', text, re.IGNORECASE):
            speech_rate_modifier = 1.2
        elif re.search(r'\b(slow|calm|peaceful|gentle)\b', text, re.IGNORECASE):
            speech_rate_modifier = 0.8
        
        # Determine pitch range modifier
        pitch_range_modifier = 1.0
        if re.search(r'[!]{2,}', text):
            pitch_range_modifier = 1.3
        elif re.search(r'\b(whisper|quiet|soft)\b', text, re.IGNORECASE):
            pitch_range_modifier = 0.7
        
        # Determine intonation contour
        intonation_contour = "neutral"
        if re.search(r'\?', text):
            intonation_contour = "rising"
        elif re.search(r'!', text):
            intonation_contour = "emphatic"
        elif re.search(r'\.{2,}', text):
            intonation_contour = "trailing"
        
        return ProsodyContext(
            speech_rate_modifier=speech_rate_modifier,
            pitch_range_modifier=pitch_range_modifier,
            volume_modifier=1.0,
            pause_patterns=pause_patterns,
            emphasis_points=emphasis_points,
            intonation_contour=intonation_contour
        )
    
    def _map_to_contextual_emotion(self, emotion_name: str) -> ContextualEmotion:
        """Map emotion name to ContextualEmotion enum"""
        mapping = {
            'joy': ContextualEmotion.JOY,
            'sadness': ContextualEmotion.SADNESS,
            'anger': ContextualEmotion.ANGER,
            'fear': ContextualEmotion.FEAR,
            'surprise': ContextualEmotion.SURPRISE,
            'excitement': ContextualEmotion.EXCITEMENT,
            'calm': ContextualEmotion.CALM,
            'confidence': ContextualEmotion.CONFIDENCE,
            'uncertainty': ContextualEmotion.UNCERTAINTY,
            'sarcasm': ContextualEmotion.SARCASM
        }
        return mapping.get(emotion_name, ContextualEmotion.NEUTRAL)
    
    def _calculate_intensity(self, score: float) -> EmotionalIntensity:
        """Calculate emotional intensity from score"""
        if score >= 0.8:
            return EmotionalIntensity.VERY_HIGH
        elif score >= 0.6:
            return EmotionalIntensity.HIGH
        elif score >= 0.4:
            return EmotionalIntensity.MODERATE
        elif score >= 0.2:
            return EmotionalIntensity.LOW
        else:
            return EmotionalIntensity.VERY_LOW
    
    def _generate_prosodic_suggestions(self, emotion: ContextualEmotion, intensity: EmotionalIntensity) -> Dict[str, float]:
        """Generate prosodic parameter suggestions based on emotion and intensity"""
        base_suggestions = {
            'speech_rate': 1.0,
            'pitch_adjustment': 0.0,
            'volume_adjustment': 1.0,
            'emphasis_strength': 1.0
        }
        
        intensity_factor = intensity.value
        
        if emotion == ContextualEmotion.JOY:
            base_suggestions.update({
                'speech_rate': 1.0 + (intensity_factor * 0.2),
                'pitch_adjustment': intensity_factor * 0.3,
                'volume_adjustment': 1.0 + (intensity_factor * 0.1),
                'emphasis_strength': 1.0 + (intensity_factor * 0.2)
            })
        elif emotion == ContextualEmotion.SADNESS:
            base_suggestions.update({
                'speech_rate': 1.0 - (intensity_factor * 0.3),
                'pitch_adjustment': -(intensity_factor * 0.2),
                'volume_adjustment': 1.0 - (intensity_factor * 0.2),
                'emphasis_strength': 1.0 - (intensity_factor * 0.1)
            })
        elif emotion == ContextualEmotion.ANGER:
            base_suggestions.update({
                'speech_rate': 1.0 + (intensity_factor * 0.3),
                'pitch_adjustment': intensity_factor * 0.2,
                'volume_adjustment': 1.0 + (intensity_factor * 0.3),
                'emphasis_strength': 1.0 + (intensity_factor * 0.4)
            })
        elif emotion == ContextualEmotion.FEAR:
            base_suggestions.update({
                'speech_rate': 1.0 + (intensity_factor * 0.4),
                'pitch_adjustment': intensity_factor * 0.4,
                'volume_adjustment': 1.0 - (intensity_factor * 0.1),
                'emphasis_strength': 1.0 + (intensity_factor * 0.2)
            })
        elif emotion == ContextualEmotion.EXCITEMENT:
            base_suggestions.update({
                'speech_rate': 1.0 + (intensity_factor * 0.3),
                'pitch_adjustment': intensity_factor * 0.4,
                'volume_adjustment': 1.0 + (intensity_factor * 0.2),
                'emphasis_strength': 1.0 + (intensity_factor * 0.3)
            })
        elif emotion == ContextualEmotion.CALM:
            base_suggestions.update({
                'speech_rate': 1.0 - (intensity_factor * 0.2),
                'pitch_adjustment': 0.0,
                'volume_adjustment': 1.0 - (intensity_factor * 0.1),
                'emphasis_strength': 1.0 - (intensity_factor * 0.2)
            })
        
        return base_suggestions
    
    def _calculate_confidence(self, emotional_context: EmotionalContext, prosody_context: ProsodyContext) -> float:
        """Calculate overall confidence score"""
        # Base confidence from emotional analysis
        emotional_confidence = emotional_context.confidence
        
        # Prosodic confidence based on clear patterns
        prosodic_confidence = 0.5
        if prosody_context.emphasis_points:
            prosodic_confidence += 0.2
        if prosody_context.pause_patterns:
            prosodic_confidence += 0.1
        if prosody_context.intonation_contour != "neutral":
            prosodic_confidence += 0.2
        
        # Combined confidence
        return min((emotional_confidence + prosodic_confidence) / 2, 0.95)
