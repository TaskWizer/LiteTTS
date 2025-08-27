#!/usr/bin/env python3
"""
Human-likeness optimization for TTS synthesis

This module provides advanced naturalness enhancement techniques including
coarticulation effects, natural disfluencies, breathing patterns, and
micro-prosodic variations for human-like speech synthesis.
"""

import re
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DisfluencyType(Enum):
    """Types of natural speech disfluencies"""
    FILLED_PAUSE = "filled_pause"  # um, uh, er
    SILENT_PAUSE = "silent_pause"  # strategic hesitations
    REPETITION = "repetition"      # word repetitions
    FALSE_START = "false_start"    # incomplete phrases
    PROLONGATION = "prolongation"  # lengthened sounds

class BreathType(Enum):
    """Types of breathing patterns"""
    INTAKE = "intake"      # breath before speaking
    EXHALE = "exhale"      # breath during pauses
    SIGH = "sigh"          # emotional breathing
    SUBTLE = "subtle"      # barely audible breathing

@dataclass
class DisfluencyMarker:
    """Represents a natural disfluency in speech"""
    position: int
    disfluency_type: DisfluencyType
    content: str
    duration: float
    intensity: float  # 0.0 to 1.0

@dataclass
class BreathMarker:
    """Represents a breathing pattern marker"""
    position: int
    breath_type: BreathType
    duration: float
    volume: float  # 0.0 to 1.0

@dataclass
class MicroProsodyAdjustment:
    """Micro-prosodic timing and pitch adjustments"""
    position: int
    timing_jitter: float  # milliseconds
    pitch_perturbation: float  # cents
    amplitude_variation: float  # dB

@dataclass
class NaturalnessProfile:
    """Complete naturalness enhancement profile"""
    disfluencies: List[DisfluencyMarker]
    breathing_patterns: List[BreathMarker]
    micro_prosody: List[MicroProsodyAdjustment]
    coarticulation_strength: float
    voice_quality_variation: float
    overall_naturalness_level: float

class NaturalnessEnhancer:
    """Advanced naturalness enhancement for human-like speech"""
    
    def __init__(self, naturalness_level: float = 0.8):
        """Initialize naturalness enhancer
        
        Args:
            naturalness_level: Overall naturalness strength (0.0 to 1.0)
        """
        self.naturalness_level = naturalness_level
        self.disfluency_patterns = self._load_disfluency_patterns()
        self.breathing_rules = self._load_breathing_rules()
        self.coarticulation_rules = self._load_coarticulation_rules()
        
        # Randomization for natural variation
        random.seed()  # Use system time for true randomness
    
    def _load_disfluency_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load natural disfluency patterns and insertion rules"""
        return {
            "sentence_start": {
                "probability": 0.15,
                "types": [DisfluencyType.FILLED_PAUSE, DisfluencyType.SILENT_PAUSE],
                "content_options": {
                    DisfluencyType.FILLED_PAUSE: ["um", "uh", "er", "well"],
                    DisfluencyType.SILENT_PAUSE: ["<pause:0.3>"]
                }
            },
            "clause_boundary": {
                "probability": 0.25,
                "types": [DisfluencyType.FILLED_PAUSE, DisfluencyType.SILENT_PAUSE],
                "content_options": {
                    DisfluencyType.FILLED_PAUSE: ["um", "uh", "you know"],
                    DisfluencyType.SILENT_PAUSE: ["<pause:0.2>", "<pause:0.4>"]
                }
            },
            "complex_word": {
                "probability": 0.1,
                "types": [DisfluencyType.FALSE_START, DisfluencyType.PROLONGATION],
                "content_options": {
                    DisfluencyType.FALSE_START: ["the... the", "I... I mean"],
                    DisfluencyType.PROLONGATION: ["<prolong:0.2>"]
                }
            },
            "emotional_context": {
                "probability": 0.2,
                "types": [DisfluencyType.REPETITION, DisfluencyType.FILLED_PAUSE],
                "content_options": {
                    DisfluencyType.REPETITION: ["<repeat_word>"],
                    DisfluencyType.FILLED_PAUSE: ["um", "uh", "hmm"]
                }
            }
        }
    
    def _load_breathing_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load natural breathing pattern rules"""
        return {
            "long_utterance": {
                "min_length": 50,  # characters
                "breath_type": BreathType.INTAKE,
                "position": "before",
                "duration": 0.8,
                "volume": 0.3
            },
            "emotional_pause": {
                "emotion_triggers": ["sadness", "contemplation", "relief"],
                "breath_type": BreathType.SIGH,
                "duration": 1.2,
                "volume": 0.4
            },
            "natural_pause": {
                "min_pause_duration": 0.5,
                "breath_type": BreathType.SUBTLE,
                "probability": 0.3,
                "duration": 0.4,
                "volume": 0.2
            },
            "sentence_end": {
                "probability": 0.15,
                "breath_type": BreathType.EXHALE,
                "duration": 0.6,
                "volume": 0.25
            }
        }
    
    def _load_coarticulation_rules(self) -> Dict[str, Dict[str, float]]:
        """Load coarticulation effect rules"""
        return {
            # Anticipatory coarticulation (influence of following sounds)
            "anticipatory": {
                "vowel_to_nasal": 0.3,    # Vowels before nasals become nasalized
                "stop_to_fricative": 0.2,  # Stops before fricatives
                "vowel_rounding": 0.4      # Vowel rounding anticipation
            },
            # Carryover coarticulation (influence of preceding sounds)
            "carryover": {
                "nasal_to_vowel": 0.25,   # Nasal influence on following vowels
                "fricative_to_stop": 0.15, # Fricative influence on stops
                "vowel_quality": 0.3       # Vowel quality carryover
            },
            # Connected speech phenomena
            "connected_speech": {
                "elision_strength": 0.4,   # Sound deletion in fast speech
                "assimilation_strength": 0.3, # Sound similarity changes
                "liaison_strength": 0.5    # Cross-word boundary linking
            }
        }
    
    def enhance_naturalness(self, text: str, context: Optional[Dict[str, Any]] = None) -> NaturalnessProfile:
        """Apply comprehensive naturalness enhancements to text
        
        Args:
            text: Input text to enhance
            context: Optional context information (emotion, register, etc.)
            
        Returns:
            Complete naturalness enhancement profile
        """
        
        # Analyze text for enhancement opportunities
        enhancement_points = self._analyze_enhancement_points(text)
        
        # Generate disfluencies
        disfluencies = self._generate_disfluencies(text, enhancement_points, context)
        
        # Generate breathing patterns
        breathing_patterns = self._generate_breathing_patterns(text, context)
        
        # Generate micro-prosodic adjustments
        micro_prosody = self._generate_micro_prosody(text, context)
        
        # Calculate coarticulation strength
        coarticulation_strength = self._calculate_coarticulation_strength(context)
        
        # Calculate voice quality variation
        voice_variation = self._calculate_voice_variation(context)
        
        return NaturalnessProfile(
            disfluencies=disfluencies,
            breathing_patterns=breathing_patterns,
            micro_prosody=micro_prosody,
            coarticulation_strength=coarticulation_strength,
            voice_quality_variation=voice_variation,
            overall_naturalness_level=self.naturalness_level
        )
    
    def _analyze_enhancement_points(self, text: str) -> Dict[str, List[int]]:
        """Analyze text to identify naturalness enhancement points"""
        points = {
            "sentence_starts": [],
            "clause_boundaries": [],
            "complex_words": [],
            "emotional_words": [],
            "long_pauses": []
        }
        
        # Find sentence starts
        sentences = re.split(r'[.!?]+', text)
        position = 0
        for sentence in sentences[:-1]:  # Exclude last empty split
            points["sentence_starts"].append(position)
            position += len(sentence) + 1
        
        # Find clause boundaries (commas, semicolons)
        for match in re.finditer(r'[,;]', text):
            points["clause_boundaries"].append(match.start())
        
        # Find complex words (long or technical)
        for match in re.finditer(r'\b\w{8,}\b', text):
            points["complex_words"].append(match.start())
        
        # Find emotional words
        emotional_patterns = [
            r'\b(amazing|wonderful|terrible|awful|incredible)\b',
            r'\b(love|hate|fear|joy|anger|sadness)\b',
            r'\b(excited|worried|happy|sad|angry)\b'
        ]
        for pattern in emotional_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                points["emotional_words"].append(match.start())
        
        # Find potential long pause locations
        for match in re.finditer(r'[.!?]\s+', text):
            points["long_pauses"].append(match.end())
        
        return points
    
    def _generate_disfluencies(self, text: str, enhancement_points: Dict[str, List[int]], 
                             context: Optional[Dict[str, Any]]) -> List[DisfluencyMarker]:
        """Generate natural disfluencies based on text analysis"""
        disfluencies = []
        
        # Adjust probability based on context
        base_probability = self.naturalness_level * 0.3
        if context:
            # Increase disfluencies for casual/emotional contexts
            if context.get("register") == "casual":
                base_probability *= 1.5
            if context.get("emotional_intensity", 0) > 0.5:
                base_probability *= 1.3
        
        # Generate disfluencies at sentence starts
        for position in enhancement_points["sentence_starts"]:
            if random.random() < base_probability * 0.5:  # Lower probability at starts
                disfluency = self._create_disfluency(
                    position, "sentence_start", context
                )
                if disfluency:
                    disfluencies.append(disfluency)
        
        # Generate disfluencies at clause boundaries
        for position in enhancement_points["clause_boundaries"]:
            if random.random() < base_probability:
                disfluency = self._create_disfluency(
                    position, "clause_boundary", context
                )
                if disfluency:
                    disfluencies.append(disfluency)
        
        # Generate disfluencies at complex words
        for position in enhancement_points["complex_words"]:
            if random.random() < base_probability * 0.3:  # Lower for complex words
                disfluency = self._create_disfluency(
                    position, "complex_word", context
                )
                if disfluency:
                    disfluencies.append(disfluency)
        
        # Generate emotional disfluencies
        for position in enhancement_points["emotional_words"]:
            if random.random() < base_probability * 1.5:  # Higher for emotional content
                disfluency = self._create_disfluency(
                    position, "emotional_context", context
                )
                if disfluency:
                    disfluencies.append(disfluency)
        
        return sorted(disfluencies, key=lambda x: x.position)
    
    def _create_disfluency(self, position: int, pattern_type: str, 
                          context: Optional[Dict[str, Any]]) -> Optional[DisfluencyMarker]:
        """Create a specific disfluency marker"""
        if pattern_type not in self.disfluency_patterns:
            return None
        
        pattern = self.disfluency_patterns[pattern_type]
        
        # Select disfluency type
        disfluency_type = random.choice(pattern["types"])
        
        # Select content
        content_options = pattern["content_options"][disfluency_type]
        content = random.choice(content_options)
        
        # Calculate duration based on type
        duration_map = {
            DisfluencyType.FILLED_PAUSE: 0.3,
            DisfluencyType.SILENT_PAUSE: 0.2,
            DisfluencyType.REPETITION: 0.4,
            DisfluencyType.FALSE_START: 0.5,
            DisfluencyType.PROLONGATION: 0.2
        }
        base_duration = duration_map.get(disfluency_type, 0.3)
        
        # Add natural variation
        duration = base_duration * (0.8 + random.random() * 0.4)
        
        # Calculate intensity based on context
        intensity = self.naturalness_level
        if context and context.get("emotional_intensity"):
            intensity *= (1.0 + context["emotional_intensity"] * 0.5)
        
        return DisfluencyMarker(
            position=position,
            disfluency_type=disfluency_type,
            content=content,
            duration=duration,
            intensity=min(intensity, 1.0)
        )
    
    def _generate_breathing_patterns(self, text: str, 
                                   context: Optional[Dict[str, Any]]) -> List[BreathMarker]:
        """Generate natural breathing patterns"""
        breathing_patterns = []
        
        # Long utterance breathing
        if len(text) > self.breathing_rules["long_utterance"]["min_length"]:
            rule = self.breathing_rules["long_utterance"]
            breath = BreathMarker(
                position=0,  # Before utterance
                breath_type=rule["breath_type"],
                duration=rule["duration"] * self.naturalness_level,
                volume=rule["volume"] * self.naturalness_level
            )
            breathing_patterns.append(breath)
        
        # Natural pauses with breathing
        pause_rule = self.breathing_rules["natural_pause"]
        for match in re.finditer(r'[.!?]\s+', text):
            if random.random() < pause_rule["probability"] * self.naturalness_level:
                breath = BreathMarker(
                    position=match.end(),
                    breath_type=pause_rule["breath_type"],
                    duration=pause_rule["duration"],
                    volume=pause_rule["volume"]
                )
                breathing_patterns.append(breath)
        
        # Emotional breathing
        if context and context.get("emotion") in self.breathing_rules["emotional_pause"]["emotion_triggers"]:
            rule = self.breathing_rules["emotional_pause"]
            # Add emotional breathing at appropriate points
            emotional_positions = [len(text) // 2]  # Middle of text
            for position in emotional_positions:
                breath = BreathMarker(
                    position=position,
                    breath_type=rule["breath_type"],
                    duration=rule["duration"],
                    volume=rule["volume"]
                )
                breathing_patterns.append(breath)
        
        return sorted(breathing_patterns, key=lambda x: x.position)
    
    def _generate_micro_prosody(self, text: str, 
                              context: Optional[Dict[str, Any]]) -> List[MicroProsodyAdjustment]:
        """Generate micro-prosodic timing and pitch adjustments"""
        adjustments = []
        
        # Generate adjustments for each word
        words = re.finditer(r'\b\w+\b', text)
        for match in words:
            if random.random() < self.naturalness_level * 0.7:
                # Timing jitter (±20ms)
                timing_jitter = (random.random() - 0.5) * 40 * self.naturalness_level
                
                # Pitch perturbation (±10 cents)
                pitch_perturbation = (random.random() - 0.5) * 20 * self.naturalness_level
                
                # Amplitude variation (±2 dB)
                amplitude_variation = (random.random() - 0.5) * 4 * self.naturalness_level
                
                adjustment = MicroProsodyAdjustment(
                    position=match.start(),
                    timing_jitter=timing_jitter,
                    pitch_perturbation=pitch_perturbation,
                    amplitude_variation=amplitude_variation
                )
                adjustments.append(adjustment)
        
        return adjustments
    
    def _calculate_coarticulation_strength(self, context: Optional[Dict[str, Any]]) -> float:
        """Calculate appropriate coarticulation strength"""
        base_strength = self.naturalness_level * 0.8
        
        if context:
            # Increase for casual speech
            if context.get("register") == "casual":
                base_strength *= 1.2
            # Decrease for formal speech
            elif context.get("register") == "formal":
                base_strength *= 0.8
            # Adjust for speech rate
            if context.get("speech_rate", 1.0) > 1.1:
                base_strength *= 1.3  # More coarticulation in fast speech
        
        return min(base_strength, 1.0)
    
    def _calculate_voice_variation(self, context: Optional[Dict[str, Any]]) -> float:
        """Calculate voice quality variation amount"""
        base_variation = self.naturalness_level * 0.6
        
        if context:
            # Increase for emotional content
            emotional_intensity = context.get("emotional_intensity", 0)
            base_variation *= (1.0 + emotional_intensity * 0.5)
            
            # Adjust for content type
            if context.get("content_type") == "narrative":
                base_variation *= 1.3  # More variation for storytelling
            elif context.get("content_type") == "formal":
                base_variation *= 0.7  # Less variation for formal content
        
        return min(base_variation, 1.0)
    
    def apply_naturalness_to_text(self, text: str, profile: NaturalnessProfile) -> str:
        """Apply naturalness enhancements to text string
        
        This method inserts disfluency markers and breathing cues into the text
        for processing by the TTS engine.
        """
        enhanced_text = text
        offset = 0
        
        # Sort all markers by position
        all_markers = []
        
        # Add disfluencies
        for disfluency in profile.disfluencies:
            all_markers.append(("disfluency", disfluency.position, disfluency.content))
        
        # Add breathing patterns
        for breath in profile.breathing_patterns:
            breath_marker = f"<breath:{breath.breath_type.value}:{breath.duration:.2f}>"
            all_markers.append(("breath", breath.position, breath_marker))
        
        # Sort by position
        all_markers.sort(key=lambda x: x[1])
        
        # Insert markers into text
        for marker_type, position, content in all_markers:
            insert_pos = position + offset
            enhanced_text = enhanced_text[:insert_pos] + " " + content + " " + enhanced_text[insert_pos:]
            offset += len(content) + 2  # Account for added spaces
        
        return enhanced_text
