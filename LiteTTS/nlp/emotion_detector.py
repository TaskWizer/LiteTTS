#!/usr/bin/env python3
"""
Real-time emotional state analysis for TTS synthesis

This module provides context-aware emotion detection and analysis for
human-like speech synthesis with appropriate emotional expression.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class EmotionCategory(Enum):
    """Primary emotion categories based on research"""
    NEUTRAL = "neutral"
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    EXCITEMENT = "excitement"
    CONTENTMENT = "contentment"
    FRUSTRATION = "frustration"
    CURIOSITY = "curiosity"
    CONFIDENCE = "confidence"
    UNCERTAINTY = "uncertainty"

@dataclass
class EmotionProfile:
    """Comprehensive emotion analysis result"""
    primary_emotion: EmotionCategory
    intensity: float  # 0.0 to 1.0
    secondary_emotions: Dict[EmotionCategory, float]
    confidence: float  # 0.0 to 1.0
    context_factors: Dict[str, Any]
    prosodic_parameters: Dict[str, float]

@dataclass
class DialogueTurn:
    """Single turn in a conversation"""
    speaker: str
    text: str
    timestamp: float
    emotion: Optional[EmotionProfile] = None

@dataclass
class DialogueState:
    """Current state of the conversation"""
    emotional_arc: List[EmotionCategory]
    conversation_phase: str
    emotional_contagion: float
    topic_sentiment: float

class EmotionDetector:
    """Advanced emotion detection and analysis system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize emotion detector with configuration"""
        self.emotion_lexicon = self._load_emotion_lexicon()
        self.context_patterns = self._load_context_patterns()
        self.prosody_mappings = self._load_prosody_mappings()
        self.conversation_history: List[DialogueTurn] = []
        
    def _load_emotion_lexicon(self) -> Dict[str, Dict[str, float]]:
        """Load emotion word lexicon with intensity scores"""
        # Basic emotion lexicon - in production, load from external file
        return {
            # Joy/Happiness words
            "happy": {"joy": 0.8, "excitement": 0.3},
            "excited": {"excitement": 0.9, "joy": 0.6},
            "thrilled": {"excitement": 0.95, "joy": 0.8},
            "delighted": {"joy": 0.85, "contentment": 0.4},
            "wonderful": {"joy": 0.7, "contentment": 0.5},
            "amazing": {"surprise": 0.6, "joy": 0.7},
            "fantastic": {"excitement": 0.8, "joy": 0.8},
            
            # Sadness words
            "sad": {"sadness": 0.8},
            "depressed": {"sadness": 0.9},
            "disappointed": {"sadness": 0.6, "frustration": 0.4},
            "heartbroken": {"sadness": 0.95},
            "terrible": {"sadness": 0.7, "anger": 0.3},
            
            # Anger words
            "angry": {"anger": 0.8},
            "furious": {"anger": 0.95},
            "frustrated": {"frustration": 0.8, "anger": 0.5},
            "annoyed": {"frustration": 0.6, "anger": 0.4},
            "outraged": {"anger": 0.9, "surprise": 0.3},
            
            # Fear words
            "scared": {"fear": 0.8},
            "terrified": {"fear": 0.95},
            "worried": {"fear": 0.6, "uncertainty": 0.5},
            "anxious": {"fear": 0.7, "uncertainty": 0.6},
            "nervous": {"fear": 0.5, "uncertainty": 0.7},
            
            # Surprise words
            "surprised": {"surprise": 0.8},
            "shocked": {"surprise": 0.9, "fear": 0.3},
            "astonished": {"surprise": 0.85},
            "unexpected": {"surprise": 0.6},
            
            # Confidence words
            "confident": {"confidence": 0.8},
            "certain": {"confidence": 0.7},
            "sure": {"confidence": 0.6},
            "determined": {"confidence": 0.8, "anger": 0.2},
            
            # Uncertainty words
            "uncertain": {"uncertainty": 0.8},
            "confused": {"uncertainty": 0.7, "frustration": 0.3},
            "unsure": {"uncertainty": 0.6},
            "maybe": {"uncertainty": 0.4},
            "perhaps": {"uncertainty": 0.3},
        }
    
    def _load_context_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load contextual emotion patterns"""
        return {
            # Punctuation patterns
            "exclamation": {
                "pattern": r"!+",
                "emotions": {"excitement": 0.6, "joy": 0.4, "anger": 0.3},
                "intensity_multiplier": 1.5
            },
            "multiple_exclamation": {
                "pattern": r"!{2,}",
                "emotions": {"excitement": 0.8, "joy": 0.6, "anger": 0.5},
                "intensity_multiplier": 2.0
            },
            "question_uncertainty": {
                "pattern": r"\?+",
                "emotions": {"uncertainty": 0.5, "curiosity": 0.6},
                "intensity_multiplier": 1.2
            },
            "ellipsis": {
                "pattern": r"\.{3,}",
                "emotions": {"uncertainty": 0.4, "sadness": 0.3},
                "intensity_multiplier": 1.1
            },
            
            # Capitalization patterns
            "all_caps": {
                "pattern": r"\b[A-Z]{3,}\b",
                "emotions": {"anger": 0.7, "excitement": 0.6},
                "intensity_multiplier": 1.8
            },
            
            # Repetition patterns
            "letter_repetition": {
                "pattern": r"(.)\1{2,}",
                "emotions": {"excitement": 0.5, "frustration": 0.4},
                "intensity_multiplier": 1.3
            }
        }
    
    def _load_prosody_mappings(self) -> Dict[EmotionCategory, Dict[str, float]]:
        """Load emotion to prosody parameter mappings"""
        return {
            EmotionCategory.JOY: {
                "pitch_shift": 0.15,      # Higher pitch
                "pitch_range": 1.3,       # Wider range
                "rate_change": 1.1,       # Slightly faster
                "voice_brightness": 1.2,   # Brighter timbre
                "energy": 1.2             # More energetic
            },
            EmotionCategory.SADNESS: {
                "pitch_shift": -0.2,      # Lower pitch
                "pitch_range": 0.7,       # Narrower range
                "rate_change": 0.8,       # Slower
                "voice_brightness": 0.8,   # Darker timbre
                "energy": 0.7             # Less energetic
            },
            EmotionCategory.ANGER: {
                "pitch_shift": 0.1,       # Slightly higher
                "pitch_range": 1.5,       # Much wider range
                "rate_change": 1.2,       # Faster
                "voice_brightness": 1.1,   # Slightly brighter
                "energy": 1.5,            # Much more energetic
                "tension": 1.4            # Increased tension
            },
            EmotionCategory.FEAR: {
                "pitch_shift": 0.25,      # Higher pitch
                "pitch_range": 0.9,       # Slightly narrower
                "rate_change": 1.3,       # Faster
                "voice_brightness": 1.1,   # Slightly brighter
                "energy": 1.1,            # Slightly more energetic
                "tremolo": 0.3            # Voice trembling
            },
            EmotionCategory.EXCITEMENT: {
                "pitch_shift": 0.2,       # Higher pitch
                "pitch_range": 1.4,       # Wider range
                "rate_change": 1.25,      # Faster
                "voice_brightness": 1.3,   # Brighter timbre
                "energy": 1.4             # More energetic
            },
            EmotionCategory.CONFIDENCE: {
                "pitch_shift": 0.0,       # Neutral pitch
                "pitch_range": 1.1,       # Slightly wider
                "rate_change": 1.0,       # Normal rate
                "voice_brightness": 1.1,   # Clear timbre
                "energy": 1.1,            # Slightly more energetic
                "stability": 1.2          # More stable
            },
            EmotionCategory.UNCERTAINTY: {
                "pitch_shift": 0.05,      # Slightly higher
                "pitch_range": 0.9,       # Narrower range
                "rate_change": 0.9,       # Slightly slower
                "voice_brightness": 0.95,  # Slightly darker
                "energy": 0.9,            # Less energetic
                "hesitation": 0.3         # Add hesitation
            }
        }
    
    def detect_emotional_context(self, text: str, 
                                conversation_history: Optional[List[DialogueTurn]] = None) -> EmotionProfile:
        """Comprehensive emotion detection from text and context"""
        
        # Multi-level emotion analysis
        lexical_emotions = self._analyze_emotion_words(text)
        syntactic_emotions = self._analyze_sentence_structure(text)
        contextual_emotions = self._analyze_conversation_context(text, conversation_history)
        
        # Combine emotion signals
        combined_emotions = self._combine_emotion_signals(
            lexical_emotions, syntactic_emotions, contextual_emotions
        )
        
        # Determine primary emotion and intensity
        primary_emotion, intensity = self._determine_primary_emotion(combined_emotions)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(combined_emotions, text)
        
        # Generate prosodic parameters
        prosodic_params = self._generate_prosodic_parameters(primary_emotion, intensity)
        
        return EmotionProfile(
            primary_emotion=primary_emotion,
            intensity=intensity,
            secondary_emotions=combined_emotions,
            confidence=confidence,
            context_factors={
                "text_length": len(text),
                "has_punctuation": bool(re.search(r"[!?.]", text)),
                "has_caps": bool(re.search(r"[A-Z]", text))
            },
            prosodic_parameters=prosodic_params
        )
    
    def _analyze_emotion_words(self, text: str) -> Dict[EmotionCategory, float]:
        """Analyze emotion words in text"""
        emotions = {}
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            if word in self.emotion_lexicon:
                word_emotions = self.emotion_lexicon[word]
                for emotion_str, intensity in word_emotions.items():
                    emotion = EmotionCategory(emotion_str)
                    emotions[emotion] = emotions.get(emotion, 0) + intensity
        
        # Normalize by text length
        if words:
            for emotion in emotions:
                emotions[emotion] /= len(words)
        
        return emotions
    
    def _analyze_sentence_structure(self, text: str) -> Dict[EmotionCategory, float]:
        """Analyze syntactic patterns for emotional cues"""
        emotions = {}
        
        for pattern_name, pattern_info in self.context_patterns.items():
            matches = re.findall(pattern_info["pattern"], text)
            if matches:
                multiplier = pattern_info["intensity_multiplier"]
                for emotion_str, base_intensity in pattern_info["emotions"].items():
                    emotion = EmotionCategory(emotion_str)
                    intensity = base_intensity * multiplier * len(matches)
                    emotions[emotion] = emotions.get(emotion, 0) + intensity
        
        return emotions
    
    def _analyze_conversation_context(self, text: str, 
                                    history: Optional[List[DialogueTurn]]) -> Dict[EmotionCategory, float]:
        """Analyze conversation context for emotional cues"""
        emotions = {}
        
        if not history:
            return emotions
        
        # Analyze emotional trajectory
        recent_emotions = [turn.emotion.primary_emotion for turn in history[-3:] 
                          if turn.emotion]
        
        if recent_emotions:
            # Emotional persistence - recent emotions influence current
            for emotion in recent_emotions:
                emotions[emotion] = emotions.get(emotion, 0) + 0.2
            
            # Emotional contrast - detect emotional shifts
            if len(recent_emotions) >= 2:
                if recent_emotions[-1] != recent_emotions[-2]:
                    # Emotional shift detected
                    emotions[EmotionCategory.SURPRISE] = emotions.get(
                        EmotionCategory.SURPRISE, 0) + 0.1
        
        return emotions
    
    def _combine_emotion_signals(self, *emotion_dicts) -> Dict[EmotionCategory, float]:
        """Combine multiple emotion signal sources"""
        combined = {}
        
        for emotion_dict in emotion_dicts:
            for emotion, intensity in emotion_dict.items():
                combined[emotion] = combined.get(emotion, 0) + intensity
        
        return combined
    
    def _determine_primary_emotion(self, emotions: Dict[EmotionCategory, float]) -> Tuple[EmotionCategory, float]:
        """Determine primary emotion and overall intensity"""
        if not emotions:
            return EmotionCategory.NEUTRAL, 0.0
        
        # Find emotion with highest intensity
        primary_emotion = max(emotions.keys(), key=lambda e: emotions[e])
        max_intensity = emotions[primary_emotion]
        
        # Normalize intensity to 0-1 range
        normalized_intensity = min(max_intensity, 1.0)
        
        return primary_emotion, normalized_intensity
    
    def _calculate_confidence(self, emotions: Dict[EmotionCategory, float], text: str) -> float:
        """Calculate confidence in emotion detection"""
        if not emotions:
            return 0.0
        
        # Base confidence on emotion signal strength
        total_intensity = sum(emotions.values())
        max_intensity = max(emotions.values())
        
        # Higher confidence for stronger, more focused emotions
        focus_score = max_intensity / total_intensity if total_intensity > 0 else 0
        strength_score = min(total_intensity, 1.0)
        
        # Text length factor - longer text generally more reliable
        length_factor = min(len(text) / 100, 1.0)
        
        confidence = (focus_score * 0.4 + strength_score * 0.4 + length_factor * 0.2)
        return min(confidence, 1.0)
    
    def _generate_prosodic_parameters(self, emotion: EmotionCategory, 
                                    intensity: float) -> Dict[str, float]:
        """Generate prosodic parameters for emotion expression"""
        if emotion not in self.prosody_mappings:
            return {}
        
        base_params = self.prosody_mappings[emotion]
        
        # Scale parameters by intensity
        scaled_params = {}
        for param, value in base_params.items():
            if param.endswith("_shift") or param.endswith("_change"):
                # Additive parameters
                scaled_params[param] = value * intensity
            else:
                # Multiplicative parameters
                scaled_params[param] = 1.0 + (value - 1.0) * intensity
        
        return scaled_params
    
    def update_conversation_history(self, speaker: str, text: str, 
                                  emotion: EmotionProfile, timestamp: float):
        """Update conversation history with new turn"""
        turn = DialogueTurn(
            speaker=speaker,
            text=text,
            timestamp=timestamp,
            emotion=emotion
        )
        
        self.conversation_history.append(turn)
        
        # Keep only recent history (last 10 turns)
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_dialogue_state(self) -> DialogueState:
        """Get current dialogue state analysis"""
        if not self.conversation_history:
            return DialogueState(
                emotional_arc=[],
                conversation_phase="opening",
                emotional_contagion=0.0,
                topic_sentiment=0.0
            )
        
        # Extract emotional arc
        emotional_arc = [turn.emotion.primary_emotion for turn in self.conversation_history 
                        if turn.emotion]
        
        # Determine conversation phase
        phase = self._determine_conversation_phase()
        
        # Calculate emotional contagion
        contagion = self._calculate_emotional_contagion()
        
        # Calculate topic sentiment
        sentiment = self._calculate_topic_sentiment()
        
        return DialogueState(
            emotional_arc=emotional_arc,
            conversation_phase=phase,
            emotional_contagion=contagion,
            topic_sentiment=sentiment
        )
    
    def _determine_conversation_phase(self) -> str:
        """Determine current phase of conversation"""
        turn_count = len(self.conversation_history)
        
        if turn_count <= 2:
            return "opening"
        elif turn_count <= 5:
            return "development"
        elif turn_count <= 8:
            return "engagement"
        else:
            return "conclusion"
    
    def _calculate_emotional_contagion(self) -> float:
        """Calculate emotional contagion between speakers"""
        if len(self.conversation_history) < 2:
            return 0.0
        
        # Compare emotions between recent turns from different speakers
        recent_turns = self.conversation_history[-4:]
        contagion_score = 0.0
        comparisons = 0
        
        for i in range(len(recent_turns) - 1):
            turn1, turn2 = recent_turns[i], recent_turns[i + 1]
            if (turn1.speaker != turn2.speaker and 
                turn1.emotion and turn2.emotion):
                
                # Calculate emotional similarity
                if turn1.emotion.primary_emotion == turn2.emotion.primary_emotion:
                    contagion_score += 1.0
                elif turn1.emotion.primary_emotion in turn2.emotion.secondary_emotions:
                    contagion_score += 0.5
                
                comparisons += 1
        
        return contagion_score / comparisons if comparisons > 0 else 0.0
    
    def _calculate_topic_sentiment(self) -> float:
        """Calculate overall sentiment of conversation topic"""
        if not self.conversation_history:
            return 0.0
        
        positive_emotions = {EmotionCategory.JOY, EmotionCategory.EXCITEMENT, 
                           EmotionCategory.CONTENTMENT, EmotionCategory.CONFIDENCE}
        negative_emotions = {EmotionCategory.SADNESS, EmotionCategory.ANGER, 
                           EmotionCategory.FEAR, EmotionCategory.FRUSTRATION}
        
        positive_score = 0.0
        negative_score = 0.0
        
        for turn in self.conversation_history:
            if turn.emotion:
                if turn.emotion.primary_emotion in positive_emotions:
                    positive_score += turn.emotion.intensity
                elif turn.emotion.primary_emotion in negative_emotions:
                    negative_score += turn.emotion.intensity
        
        total_score = positive_score + negative_score
        if total_score == 0:
            return 0.0
        
        return (positive_score - negative_score) / total_score
