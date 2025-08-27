#!/usr/bin/env python3
"""
Audio Quality Enhancement System for TTS
Implements state-of-the-art prosodic modeling and emotional speech synthesis
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class EmotionType(Enum):
    """Supported emotion types for speech synthesis"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    ANGRY = "angry"
    SURPRISED = "surprised"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    EMPATHETIC = "empathetic"

class ProsodyLevel(Enum):
    """Prosodic emphasis levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class ProsodyMarker:
    """Prosodic marker for text segments"""
    start_pos: int
    end_pos: int
    emotion: EmotionType
    emphasis: ProsodyLevel
    pause_before: float = 0.0  # seconds
    pause_after: float = 0.0   # seconds
    pitch_shift: float = 0.0   # semitones
    speed_factor: float = 1.0  # relative speed

@dataclass
class AudioQualityProfile:
    """Audio quality enhancement profile"""
    enable_emotional_analysis: bool = True
    enable_prosodic_modeling: bool = True
    enable_natural_pauses: bool = True
    enable_context_adaptation: bool = True
    enable_dynamic_intonation: bool = True
    emotional_intensity: float = 0.7  # 0.0-1.0
    prosodic_variation: float = 0.8   # 0.0-1.0
    naturalness_level: float = 0.9    # 0.0-1.0

class AudioQualityEnhancer:
    """Advanced audio quality enhancement system"""
    
    def __init__(self, profile: AudioQualityProfile = None):
        self.profile = profile or AudioQualityProfile()
        self.emotion_patterns = self._load_emotion_patterns()
        self.prosody_rules = self._load_prosody_rules()
        self.context_patterns = self._load_context_patterns()
        
    def _load_emotion_patterns(self) -> Dict[str, EmotionType]:
        """Load patterns for emotion detection"""
        return {
            # Positive emotions
            r'\b(great|wonderful|amazing|fantastic|excellent|perfect|love|adore|excited|thrilled|delighted)\b': EmotionType.HAPPY,
            r'\b(yay|hooray|awesome|brilliant|superb|marvelous|incredible)\b': EmotionType.EXCITED,
            r'\b(calm|peaceful|serene|relaxed|tranquil|gentle|soothing)\b': EmotionType.CALM,
            r'\b(confident|sure|certain|determined|strong|powerful)\b': EmotionType.CONFIDENT,
            
            # Negative emotions
            r'\b(sad|sorry|disappointed|upset|hurt|heartbroken|devastated)\b': EmotionType.SAD,
            r'\b(angry|mad|furious|irritated|annoyed|frustrated|outraged)\b': EmotionType.ANGRY,
            r'\b(surprised|shocked|amazed|astonished|stunned|bewildered)\b': EmotionType.SURPRISED,
            
            # Uncertain emotions
            r'\b(maybe|perhaps|possibly|might|could|uncertain|unsure|confused)\b': EmotionType.UNCERTAIN,
            r'\b(hmm|uh|um|well|I think|I guess|I suppose)\b': EmotionType.UNCERTAIN,
            
            # Empathetic emotions
            r'\b(understand|feel|empathize|sympathize|care|support|comfort)\b': EmotionType.EMPATHETIC,
            r'\b(I\'m sorry|my condolences|I feel for you|that must be hard)\b': EmotionType.EMPATHETIC,
        }
    
    def _load_prosody_rules(self) -> List[Tuple[str, ProsodyLevel, float, float]]:
        """Load prosodic emphasis rules"""
        return [
            # Pattern, Emphasis Level, Pause Before, Pause After
            (r'[.!?]\s+', ProsodyLevel.NORMAL, 0.0, 0.5),  # Sentence endings
            (r'[,;]\s+', ProsodyLevel.LOW, 0.0, 0.2),      # Clause boundaries
            (r':\s+', ProsodyLevel.NORMAL, 0.0, 0.3),      # Colons
            (r'\b(however|therefore|moreover|furthermore|nevertheless|consequently)\b', ProsodyLevel.HIGH, 0.2, 0.2),
            (r'\b(but|and|or|yet|so|for|nor)\b', ProsodyLevel.LOW, 0.1, 0.1),
            (r'\b(very|extremely|incredibly|absolutely|completely|totally)\b', ProsodyLevel.HIGH, 0.0, 0.0),
            (r'\b(please|thank you|excuse me|pardon me|sorry)\b', ProsodyLevel.NORMAL, 0.1, 0.1),
            (r'[A-Z]{2,}', ProsodyLevel.HIGH, 0.0, 0.0),   # Acronyms
            (r'\b[A-Z][a-z]*\b', ProsodyLevel.NORMAL, 0.0, 0.0),  # Proper nouns
        ]
    
    def _load_context_patterns(self) -> Dict[str, Dict[str, float]]:
        """Load context-aware adaptation patterns"""
        return {
            'question': {
                'pattern': r'\?',
                'pitch_shift': 2.0,  # Higher pitch for questions
                'speed_factor': 0.95,  # Slightly slower
                'pause_after': 0.3
            },
            'exclamation': {
                'pattern': r'!',
                'pitch_shift': 1.5,  # Elevated pitch
                'speed_factor': 1.1,  # Slightly faster
                'pause_after': 0.4
            },
            'parenthetical': {
                'pattern': r'\([^)]+\)',
                'pitch_shift': -1.0,  # Lower pitch
                'speed_factor': 0.9,  # Slower
                'pause_before': 0.1,
                'pause_after': 0.1
            },
            'quotation': {
                'pattern': r'"[^"]*"',
                'pitch_shift': 0.5,  # Slight pitch change
                'speed_factor': 0.95,  # Slightly slower
                'pause_before': 0.1,
                'pause_after': 0.1
            },
            'emphasis': {
                'pattern': r'\*[^*]+\*|_[^_]+_',
                'pitch_shift': 1.0,  # Emphasized pitch
                'speed_factor': 0.9,  # Slower for emphasis
                'pause_before': 0.05,
                'pause_after': 0.05
            }
        }
    
    def enhance_audio_quality(self, text: str) -> str:
        """Apply comprehensive audio quality enhancements"""
        logger.debug(f"Enhancing audio quality for: {text[:100]}...")
        
        original_text = text
        
        # Step 1: Analyze emotional content
        if self.profile.enable_emotional_analysis:
            text = self._apply_emotional_markers(text)
        
        # Step 2: Apply prosodic modeling
        if self.profile.enable_prosodic_modeling:
            text = self._apply_prosodic_markers(text)
        
        # Step 3: Add natural pauses
        if self.profile.enable_natural_pauses:
            text = self._add_natural_pauses(text)
        
        # Step 4: Context-aware adaptation
        if self.profile.enable_context_adaptation:
            text = self._apply_context_adaptation(text)
        
        # Step 5: Dynamic intonation
        if self.profile.enable_dynamic_intonation:
            text = self._apply_dynamic_intonation(text)
        
        if text != original_text:
            logger.debug(f"Audio quality enhancements applied: '{original_text}' → '{text}'")
        
        return text
    
    def _apply_emotional_markers(self, text: str) -> str:
        """Apply emotional markers based on content analysis - DISABLED to prevent SSML corruption"""
        # CRITICAL FIX: Disable emotional SSML generation that was causing malformed output
        # The system was generating nested prosody tags that created broken SSML
        # This was a major cause of the text processing corruption

        # For now, return text unchanged to fix the core processing issues
        # TODO: Implement proper emotional processing without SSML corruption
        logger.debug("Emotional markers disabled to prevent SSML corruption")
        return text
    
    def _apply_prosodic_markers(self, text: str) -> str:
        """Apply prosodic emphasis markers - DISABLED to prevent SSML corruption"""
        # CRITICAL FIX: Disable SSML generation that was causing malformed output
        # The system was generating nested and broken SSML tags like:
        # <<emphasis level=<break time="0.1s"/><prosody rate="-5%">...
        # This was causing complete text processing failure

        # For now, return text unchanged to fix the core processing issues
        # TODO: Implement proper prosody handling without SSML corruption
        logger.debug("Prosodic markers disabled to prevent SSML corruption")
        return text
    
    def _add_natural_pauses(self, text: str) -> str:
        """Add natural pauses for better speech flow"""
        naturalness = self.profile.naturalness_level
        
        # Add pauses after conjunctions in longer sentences
        if len(text.split()) > 10:
            text = re.sub(r'\b(and|but|or|so|yet|for|nor)\b', r'<break time="0.1s"/>\1<break time="0.1s"/>', text)
        
        # Add pauses before important transitions
        text = re.sub(r'\b(however|therefore|moreover|furthermore|nevertheless|consequently)\b', 
                     r'<break time="0.2s"/>\1<break time="0.2s"/>', text)
        
        # Add breathing pauses in very long sentences
        if len(text) > 100:
            # Add subtle pauses every 15-20 words
            words = text.split()
            if len(words) > 15:
                for i in range(15, len(words), 20):
                    words[i] = f'<break time="{0.1*naturalness:.1f}s"/>{words[i]}'
                text = ' '.join(words)
        
        return text
    
    def _apply_context_adaptation(self, text: str) -> str:
        """Apply context-aware speech adaptations"""
        for context_type, context_config in self.context_patterns.items():
            pattern = context_config['pattern']
            matches = list(re.finditer(pattern, text))
            
            for match in reversed(matches):
                matched_text = match.group()
                start, end = match.span()
                
                # Build enhanced text with context adaptations
                enhanced_text = matched_text
                
                if 'pitch_shift' in context_config:
                    pitch = context_config['pitch_shift']
                    if pitch > 0:
                        enhanced_text = f'<prosody pitch="+{pitch:.1f}st">{enhanced_text}</prosody>'
                    elif pitch < 0:
                        enhanced_text = f'<prosody pitch="{pitch:.1f}st">{enhanced_text}</prosody>'
                
                if 'speed_factor' in context_config:
                    speed = context_config['speed_factor']
                    if speed != 1.0:
                        rate_change = (speed - 1.0) * 100
                        if rate_change > 0:
                            enhanced_text = f'<prosody rate="+{rate_change:.0f}%">{enhanced_text}</prosody>'
                        else:
                            enhanced_text = f'<prosody rate="{rate_change:.0f}%">{enhanced_text}</prosody>'
                
                if 'pause_before' in context_config and context_config['pause_before'] > 0:
                    enhanced_text = f'<break time="{context_config["pause_before"]:.1f}s"/>{enhanced_text}'
                
                if 'pause_after' in context_config and context_config['pause_after'] > 0:
                    enhanced_text = f'{enhanced_text}<break time="{context_config["pause_after"]:.1f}s"/>'
                
                text = text[:start] + enhanced_text + text[end:]
        
        return text
    
    def _apply_dynamic_intonation(self, text: str) -> str:
        """Apply dynamic intonation patterns"""
        # Enhanced question intonation
        text = re.sub(r'(\w+)\?', r'<prosody pitch="+15%">\1</prosody>?', text)
        
        # Enhanced exclamation intonation
        text = re.sub(r'(\w+)!', r'<prosody pitch="+10%" volume="+10%">\1</prosody>!', text)
        
        # List intonation (rising pitch for items except the last)
        list_pattern = r'(\w+),\s*(\w+),\s*and\s+(\w+)'
        def list_replacer(match):
            item1, item2, item3 = match.groups()
            return f'<prosody pitch="+5%">{item1}</prosody>, <prosody pitch="+3%">{item2}</prosody>, and <prosody pitch="-2%">{item3}</prosody>'
        
        text = re.sub(list_pattern, list_replacer, text)
        
        return text
    
    def analyze_quality_potential(self, text: str) -> Dict[str, any]:
        """Analyze text for quality enhancement potential"""
        analysis = {
            'emotional_content': [],
            'prosodic_opportunities': [],
            'context_adaptations': [],
            'naturalness_score': 0.0,
            'enhancement_potential': 'low'
        }
        
        # Analyze emotional content
        for pattern, emotion in self.emotion_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                analysis['emotional_content'].append(emotion.value)
        
        # Analyze prosodic opportunities
        for pattern, emphasis, _, _ in self.prosody_rules:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                analysis['prosodic_opportunities'].extend(matches)
        
        # Analyze context adaptations
        for context_type, context_config in self.context_patterns.items():
            if re.search(context_config['pattern'], text):
                analysis['context_adaptations'].append(context_type)
        
        # Calculate naturalness score
        word_count = len(text.split())
        sentence_count = len(re.findall(r'[.!?]+', text))
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Score based on various factors
        naturalness_score = 0.5  # Base score
        
        if avg_sentence_length < 20:  # Good sentence length
            naturalness_score += 0.2
        if len(analysis['emotional_content']) > 0:  # Has emotional content
            naturalness_score += 0.1
        if len(analysis['prosodic_opportunities']) > 0:  # Has prosodic markers
            naturalness_score += 0.1
        if len(analysis['context_adaptations']) > 0:  # Has context markers
            naturalness_score += 0.1
        
        analysis['naturalness_score'] = min(naturalness_score, 1.0)
        
        # Determine enhancement potential
        total_opportunities = (len(analysis['emotional_content']) + 
                             len(analysis['prosodic_opportunities']) + 
                             len(analysis['context_adaptations']))
        
        if total_opportunities >= 5:
            analysis['enhancement_potential'] = 'high'
        elif total_opportunities >= 2:
            analysis['enhancement_potential'] = 'medium'
        else:
            analysis['enhancement_potential'] = 'low'
        
        return analysis

# Global instance for easy access
audio_quality_enhancer = AudioQualityEnhancer()
