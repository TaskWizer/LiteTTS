#!/usr/bin/env python3
"""
Prosody analysis system for natural speech patterns
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProsodyMarker:
    """Represents a prosody marker in text"""
    position: int
    marker_type: str
    intensity: float = 1.0
    duration: float = 0.5

class ProsodyAnalyzer:
    """Analyzes text for prosody control based on punctuation and conversational markers"""
    
    def __init__(self):
        self.punctuation_patterns = self._compile_punctuation_patterns()
        self.conversational_patterns = self._compile_conversational_patterns()
        
    def _compile_punctuation_patterns(self) -> Dict[str, Tuple[re.Pattern, float, float]]:
        """Compile punctuation patterns with pause durations and intonation markers"""
        return {
            'period': (re.compile(r'\.(?!\d)'), 0.8, 0.6),  # Period (not in decimals)
            'comma': (re.compile(r','), 0.4, 0.3),          # Comma
            'semicolon': (re.compile(r';'), 0.6, 0.4),      # Semicolon
            'colon': (re.compile(r':(?!\d)'), 0.5, 0.4),    # Colon (not in time)
            'question': (re.compile(r'\?'), 0.8, 0.6),      # Question mark - rising intonation
            'exclamation': (re.compile(r'!'), 0.8, 0.6),    # Exclamation - emphatic tone
            'ellipsis': (re.compile(r'\.{3,}'), 1.2, 0.8),  # Ellipsis
            'dash': (re.compile(r'—|--'), 0.6, 0.4),        # Em dash
            'parentheses': (re.compile(r'[()]'), 0.3, 0.2), # Parentheses
            'quotes': (re.compile(r'["\']'), 0.2, 0.1)      # Quotes
        }
    
    def _compile_conversational_patterns(self) -> Dict[str, Tuple[re.Pattern, str, float]]:
        """Compile conversational marker patterns"""
        return {
            'false_start': (
                re.compile(r'\b(I|we|you|they|he|she|it)\s+(uh|um|er|ah)\s+\1\b', re.IGNORECASE),
                'false_start', 0.3
            ),
            'filler_words': (
                re.compile(r'\b(uh|um|er|ah|like|you know|I mean|well|so)\b', re.IGNORECASE),
                'filler', 0.2
            ),
            'breathing': (
                re.compile(r'\*breathes?\*|\*inhales?\*|\*exhales?\*|\*sighs?\*', re.IGNORECASE),
                'breathing', 0.8
            ),
            'laughter': (
                re.compile(r'\*laughs?\*|\*chuckles?\*|\*giggles?\*|haha|hehe|lol', re.IGNORECASE),
                'laughter', 0.5
            ),
            'hesitation': (
                re.compile(r'\b(well|uh|um|let me see|hmm)\b', re.IGNORECASE),
                'hesitation', 0.4
            )
        }
    
    def analyze_prosody(self, text: str) -> List[ProsodyMarker]:
        """Analyze text and return prosody markers"""
        logger.debug(f"Analyzing prosody in: {text[:100]}...")
        
        markers = []
        
        # Analyze punctuation-based prosody
        markers.extend(self._analyze_punctuation(text))
        
        # Analyze conversational markers
        markers.extend(self._analyze_conversational_markers(text))
        
        # Sort markers by position
        markers.sort(key=lambda x: x.position)
        
        logger.debug(f"Found {len(markers)} prosody markers")
        return markers
    
    def _analyze_punctuation(self, text: str) -> List[ProsodyMarker]:
        """Analyze punctuation for prosody markers with enhanced intonation handling"""
        markers = []

        for punct_type, (pattern, intensity, duration) in self.punctuation_patterns.items():
            for match in pattern.finditer(text):
                # Enhanced handling for questions and exclamations
                if punct_type == 'question':
                    # Add rising intonation marker for questions
                    markers.append(ProsodyMarker(
                        position=match.start(),
                        marker_type="intonation_rising",
                        intensity=1.2,  # Stronger for question intonation
                        duration=duration
                    ))
                    # Also add pause marker
                    markers.append(ProsodyMarker(
                        position=match.start(),
                        marker_type=f"pause_{punct_type}",
                        intensity=intensity,
                        duration=duration
                    ))
                elif punct_type == 'exclamation':
                    # Add emphatic tone marker for exclamations
                    markers.append(ProsodyMarker(
                        position=match.start(),
                        marker_type="emphasis_exclamation",
                        intensity=1.3,  # Strong emphasis for exclamations
                        duration=duration
                    ))
                    # Also add pause marker
                    markers.append(ProsodyMarker(
                        position=match.start(),
                        marker_type=f"pause_{punct_type}",
                        intensity=intensity,
                        duration=duration
                    ))
                else:
                    # Standard pause marker for other punctuation
                    markers.append(ProsodyMarker(
                        position=match.start(),
                        marker_type=f"pause_{punct_type}",
                        intensity=intensity,
                        duration=duration
                    ))

        return markers
  
    def _analyze_conversational_markers(self, text: str) -> List[ProsodyMarker]:
        """Analyze conversational markers"""
        markers = []
        
        for marker_type, (pattern, marker_name, intensity) in self.conversational_patterns.items():
            for match in pattern.finditer(text):
                # Determine duration based on marker type
                duration = self._get_marker_duration(marker_name)
                
                markers.append(ProsodyMarker(
                    position=match.start(),
                    marker_type=marker_name,
                    intensity=intensity,
                    duration=duration
                ))
        
        return markers
    
    def _get_marker_duration(self, marker_name: str) -> float:
        """Get duration for different marker types"""
        durations = {
            'false_start': 0.3,
            'filler': 0.2,
            'breathing': 0.8,
            'laughter': 0.5,
            'hesitation': 0.4
        }
        return durations.get(marker_name, 0.3)
    
    def process_conversational_features(self, text: str) -> str:
        """Process and enhance conversational features in text"""
        logger.debug(f"Processing conversational features in: {text[:100]}...")
        
        # Process false starts
        text = self._process_false_starts(text)
        
        # Process filler words
        text = self._process_filler_words(text)
        
        # Process breathing and laughter tokens
        text = self._process_action_tokens(text)
        
        logger.debug(f"Conversational processing result: {text[:100]}...")
        return text
    
    def _process_false_starts(self, text: str) -> str:
        """Process false starts for natural speech"""
        # Pattern: "I uh I think" -> "I... uh... I think"
        false_start_pattern = re.compile(
            r'\b(I|we|you|they|he|she|it)\s+(uh|um|er|ah)\s+\1\b',
            re.IGNORECASE
        )
        
        def replace_false_start(match):
            pronoun1 = match.group(1)
            filler = match.group(2)
            pronoun2 = match.group(3)
            return f"{pronoun1}... {filler}... {pronoun2}"
        
        return false_start_pattern.sub(replace_false_start, text)
    
    def _process_filler_words(self, text: str) -> str:
        """Add natural pauses around filler words"""
        # FIXED: Exclude filler processing for pronunciation guides (words with hyphens or mixed case)
        # Skip processing if text looks like a pronunciation guide
        if re.search(r'[A-Z]-[a-z]|[a-z]-[A-Z]|[A-Z]{2,}', text):
            return text

        filler_pattern = re.compile(
            r'\b(uh|um|er|ah|like|you know|I mean|well|so)\b',
            re.IGNORECASE
        )
        
        def replace_filler(match):
            filler = match.group(1)
            # Add slight pauses around filler words
            return f"... {filler} ..."
        
        return filler_pattern.sub(replace_filler, text)
    
    def _process_action_tokens(self, text: str) -> str:
        """Process action tokens like *breathes*, *laughs*"""
        # Breathing tokens
        breathing_pattern = re.compile(
            r'\*\s*(breathes?|inhales?|exhales?|sighs?)\s*\*',
            re.IGNORECASE
        )
        text = breathing_pattern.sub(r'... \1 ...', text)
        
        # Laughter tokens
        laughter_pattern = re.compile(
            r'\*\s*(laughs?|chuckles?|giggles?)\s*\*',
            re.IGNORECASE
        )
        text = laughter_pattern.sub(r'... \1 ...', text)
        
        # Generic action tokens
        action_pattern = re.compile(r'\*([^*]+)\*')
        text = action_pattern.sub(r'... \1 ...', text)
        
        return text
    
    def get_prosody_info(self, text: str) -> Dict[str, List[Dict]]:
        """Get detailed prosody information"""
        markers = self.analyze_prosody(text)
        
        prosody_info = {
            'pauses': [],
            'emphasis': [],
            'intonation': []
        }
        
        for marker in markers:
            marker_info = {
                'position': marker.position,
                'type': marker.marker_type,
                'intensity': marker.intensity,
                'duration': marker.duration
            }
            
            if 'pause' in marker.marker_type:
                prosody_info['pauses'].append(marker_info)
            elif marker.marker_type in ['false_start', 'hesitation']:
                prosody_info['emphasis'].append(marker_info)
            else:
                prosody_info['intonation'].append(marker_info)
        
        return prosody_info

    def enhance_intonation_markers(self, text: str) -> str:
        """Add intonation markers to text for better TTS processing"""
        # FIXED: Remove visual arrow symbols that get converted to spoken words
        # Instead, preserve natural punctuation for TTS engines to handle

        # Handle multiple question/exclamation marks by normalizing them
        text = re.sub(r'\?{2,}', '?', text)  # Multiple questions -> single question mark
        text = re.sub(r'!{2,}', '!', text)   # Multiple exclamations -> single exclamation mark

        # Note: Removed visual arrows (↗, ‼) as they were being converted to spoken words
        # TTS engines handle question marks and exclamation marks naturally for intonation

        return text

    def process_conversational_intonation(self, text: str) -> str:
        """Process text to enhance conversational intonation patterns"""
        # FIXED: Remove visual arrow symbols that get converted to spoken words
        # TTS engines can handle natural question intonation without visual markers

        # Note: Removed arrow symbols (↗) from question words and tag questions
        # as they were being converted to "up right arrow" in speech output
        # Modern TTS engines handle question intonation naturally from punctuation

        return text