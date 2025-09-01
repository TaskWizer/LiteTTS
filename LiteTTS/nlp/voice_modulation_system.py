#!/usr/bin/env python3
"""
Voice modulation system for TTS
Implements whisper/quiet mode for parenthetical text and other voice effects
"""

import re
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class VoiceModulation:
    """Voice modulation parameters"""
    voice_name: str
    volume_multiplier: float = 1.0
    speed_multiplier: float = 1.0
    pitch_adjustment: float = 0.0
    tone: str = "normal"  # normal, whisper, emphasis, soft, etc.
    blend_ratio: float = 1.0  # For voice blending

@dataclass
class ModulationSegment:
    """Text segment with voice modulation"""
    text: str
    start_pos: int
    end_pos: int
    modulation: VoiceModulation
    original_text: str

class VoiceModulationSystem:
    """Advanced voice modulation system for natural TTS expression"""
    
    def __init__(self):
        self.modulation_patterns = self._load_modulation_patterns()
        self.voice_profiles = self._load_voice_profiles()
        self.ssml_markers = self._load_ssml_markers()
        
        # Configuration
        self.enable_parenthetical_whisper = True
        self.enable_emphasis_detection = True
        self.enable_voice_blending = True
        self.default_whisper_voice = "af_nicole"
        
    def _load_modulation_patterns(self) -> List[Tuple[str, str, Dict]]:
        """Load text patterns that trigger voice modulation"""
        return [
            # Parenthetical text - enhanced whisper mode with af_nicole blend
            (r'\(([^)]+)\)', 'parenthetical_whisper', {
                'voice_name': 'af_nicole',
                'volume_multiplier': 0.55,  # Quieter for better whisper effect
                'speed_multiplier': 0.85,   # Slower for more intimate delivery
                'pitch_adjustment': -0.15,  # Lower pitch for whisper
                'tone': 'whisper',
                'blend_ratio': 0.8,         # Higher blend ratio for more af_nicole
                'breathing_pause': 0.1,     # Add slight pause before/after
                'intimacy_level': 'high'    # Enhanced intimacy for parenthetical content
            }),

            # Nested parenthetical - even quieter
            (r'\(\(([^)]+)\)\)', 'nested_parenthetical', {
                'voice_name': 'af_nicole',
                'volume_multiplier': 0.4,
                'speed_multiplier': 0.8,
                'pitch_adjustment': -0.2,
                'tone': 'deep_whisper',
                'blend_ratio': 0.9
            }),

            # Aside text - similar to parenthetical but different pattern
            (r'\[aside\]([^[]+)\[/aside\]', 'aside_whisper', {
                'voice_name': 'af_nicole',
                'volume_multiplier': 0.6,
                'speed_multiplier': 0.9,
                'pitch_adjustment': -0.1,
                'tone': 'aside',
                'blend_ratio': 0.75
            }),
            
            # Italicized text - emphasis
            (r'\*([^*]+)\*', 'emphasis', {
                'volume_multiplier': 1.2,
                'speed_multiplier': 0.95,
                'pitch_adjustment': 0.05,
                'tone': 'emphasis'
            }),
            
            # Bold text - strong emphasis
            (r'\*\*([^*]+)\*\*', 'strong_emphasis', {
                'volume_multiplier': 1.3,
                'speed_multiplier': 0.9,
                'pitch_adjustment': 0.1,
                'tone': 'strong_emphasis'
            }),
            
            # Quoted text - different tone
            (r'"([^"]+)"', 'quoted', {
                'volume_multiplier': 1.1,
                'speed_multiplier': 1.0,
                'pitch_adjustment': 0.02,
                'tone': 'quoted'
            }),
            
            # Whispered text (explicit)
            (r'\[whisper\]([^[]+)\[/whisper\]', 'explicit_whisper', {
                'voice_name': 'af_nicole',
                'volume_multiplier': 0.5,
                'speed_multiplier': 0.85,
                'pitch_adjustment': -0.15,
                'tone': 'whisper',
                'blend_ratio': 0.8
            }),
            
            # Soft text
            (r'\[soft\]([^[]+)\[/soft\]', 'soft', {
                'volume_multiplier': 0.8,
                'speed_multiplier': 0.95,
                'pitch_adjustment': -0.05,
                'tone': 'soft'
            }),
            
            # Loud text
            (r'\[loud\]([^[]+)\[/loud\]', 'loud', {
                'volume_multiplier': 1.4,
                'speed_multiplier': 1.05,
                'pitch_adjustment': 0.1,
                'tone': 'loud'
            }),
            
            # Fast text
            (r'\[fast\]([^[]+)\[/fast\]', 'fast', {
                'speed_multiplier': 1.3,
                'tone': 'fast'
            }),
            
            # Slow text
            (r'\[slow\]([^[]+)\[/slow\]', 'slow', {
                'speed_multiplier': 0.7,
                'tone': 'slow'
            }),
            
            # Aside text (similar to parenthetical but different marker)
            (r'\[aside\]([^[]+)\[/aside\]', 'aside', {
                'voice_name': 'af_nicole',
                'volume_multiplier': 0.7,
                'speed_multiplier': 0.9,
                'pitch_adjustment': -0.08,
                'tone': 'aside',
                'blend_ratio': 0.6
            }),
        ]
    
    def _load_voice_profiles(self) -> Dict[str, VoiceModulation]:
        """Load predefined voice profiles"""
        return {
            'whisper': VoiceModulation(
                voice_name='af_nicole',
                volume_multiplier=0.55,  # Enhanced quieter whisper
                speed_multiplier=0.85,   # Slower for intimacy
                pitch_adjustment=-0.15,  # Lower pitch for better whisper
                tone='whisper',
                blend_ratio=0.8          # Higher af_nicole blend
            ),
            'parenthetical_whisper': VoiceModulation(
                voice_name='af_nicole',
                volume_multiplier=0.55,
                speed_multiplier=0.85,
                pitch_adjustment=-0.15,
                tone='parenthetical_whisper',
                blend_ratio=0.8
            ),
            'deep_whisper': VoiceModulation(
                voice_name='af_nicole',
                volume_multiplier=0.4,   # Even quieter for nested parenthetical
                speed_multiplier=0.8,
                pitch_adjustment=-0.2,
                tone='deep_whisper',
                blend_ratio=0.9
            ),
            'aside': VoiceModulation(
                voice_name='af_nicole',
                volume_multiplier=0.6,
                speed_multiplier=0.9,
                pitch_adjustment=-0.1,
                tone='aside',
                blend_ratio=0.75
            ),
            'emphasis': VoiceModulation(
                voice_name='default',
                volume_multiplier=1.2,
                speed_multiplier=0.95,
                pitch_adjustment=0.05,
                tone='emphasis'
            ),
            'soft': VoiceModulation(
                voice_name='default',
                volume_multiplier=0.8,
                speed_multiplier=0.95,
                pitch_adjustment=-0.05,
                tone='soft'
            ),
            'excited': VoiceModulation(
                voice_name='default',
                volume_multiplier=1.3,
                speed_multiplier=1.1,
                pitch_adjustment=0.15,
                tone='excited'
            ),
            'calm': VoiceModulation(
                voice_name='default',
                volume_multiplier=0.9,
                speed_multiplier=0.85,
                pitch_adjustment=-0.05,
                tone='calm'
            ),
        }
    
    def _load_ssml_markers(self) -> Dict[str, str]:
        """Load SSML-like markers for voice modulation"""
        return {
            # Volume markers
            '<volume level="soft">': '[soft]',
            '</volume>': '[/soft]',
            '<volume level="loud">': '[loud]',
            
            # Speed markers
            '<prosody rate="slow">': '[slow]',
            '</prosody>': '[/slow]',
            '<prosody rate="fast">': '[fast]',
            
            # Voice markers
            '<voice name="whisper">': '[whisper]',
            '</voice>': '[/whisper]',
            
            # Emphasis markers
            '<emphasis level="strong">': '**',
            '</emphasis>': '**',
            '<emphasis level="moderate">': '*',
        }
    
    def process_voice_modulation(self, text: str, base_voice: str = "default") -> Tuple[str, List[ModulationSegment]]:
        """Process text for voice modulation and return processed text with modulation segments"""
        logger.debug(f"Processing voice modulation in: {text[:100]}...")

        # Convert SSML-like markers to internal format
        text = self._convert_ssml_markers(text)

        # Find all modulation segments
        modulation_segments = self._find_modulation_segments(text, base_voice)

        # Process the text and remove modulation markers
        processed_text = self._remove_modulation_markers(text)

        # Add breathing pauses for parenthetical content
        processed_text, modulation_segments = self._add_breathing_pauses(processed_text, modulation_segments)

        logger.debug(f"Found {len(modulation_segments)} modulation segments")
        logger.debug(f"Voice modulation result: {processed_text[:100]}...")

        return processed_text, modulation_segments
    
    def _convert_ssml_markers(self, text: str) -> str:
        """Convert SSML-like markers to internal format"""
        for ssml_marker, internal_marker in self.ssml_markers.items():
            text = text.replace(ssml_marker, internal_marker)
        return text
    
    def _find_modulation_segments(self, text: str, base_voice: str) -> List[ModulationSegment]:
        """Find all text segments that need voice modulation"""
        segments = []
        
        for pattern, modulation_type, params in self.modulation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                # Create modulation object
                modulation = VoiceModulation(
                    voice_name=params.get('voice_name', base_voice),
                    volume_multiplier=params.get('volume_multiplier', 1.0),
                    speed_multiplier=params.get('speed_multiplier', 1.0),
                    pitch_adjustment=params.get('pitch_adjustment', 0.0),
                    tone=params.get('tone', 'normal'),
                    blend_ratio=params.get('blend_ratio', 1.0)
                )
                
                # Create segment
                segment = ModulationSegment(
                    text=match.group(1),  # The content inside the markers
                    start_pos=match.start(),
                    end_pos=match.end(),
                    modulation=modulation,
                    original_text=match.group(0)  # The full match including markers
                )
                
                segments.append(segment)
        
        # Sort segments by position
        segments.sort(key=lambda x: x.start_pos)
        
        return segments
    
    def _remove_modulation_markers(self, text: str) -> str:
        """Remove modulation markers from text, leaving only the content"""
        # Remove markers but keep the content
        for pattern, _, _ in self.modulation_patterns:
            text = re.sub(pattern, r'\1', text)
        
        # Clean up any remaining markers
        text = re.sub(r'\[/?[a-zA-Z_]+\]', '', text)
        
        return text
    
    def generate_ssml_with_modulation(self, text: str, segments: List[ModulationSegment], 
                                    base_voice: str = "default") -> str:
        """Generate SSML with voice modulation markers"""
        if not segments:
            return text
        
        # Build SSML with modulation
        ssml_parts = []
        last_pos = 0
        
        for segment in segments:
            # Add text before this segment
            if segment.start_pos > last_pos:
                before_text = text[last_pos:segment.start_pos]
                ssml_parts.append(before_text)
            
            # Add modulated segment
            ssml_segment = self._create_ssml_segment(segment)
            ssml_parts.append(ssml_segment)
            
            last_pos = segment.end_pos
        
        # Add remaining text
        if last_pos < len(text):
            ssml_parts.append(text[last_pos:])
        
        return ''.join(ssml_parts)
    
    def _create_ssml_segment(self, segment: ModulationSegment) -> str:
        """Create SSML for a modulated segment"""
        modulation = segment.modulation
        content = segment.text
        
        # Build SSML tags
        tags = []
        
        # Voice change
        if modulation.voice_name != "default":
            tags.append(f'<voice name="{modulation.voice_name}">')
        
        # Volume
        if modulation.volume_multiplier != 1.0:
            if modulation.volume_multiplier < 0.7:
                volume_level = "soft"
            elif modulation.volume_multiplier > 1.2:
                volume_level = "loud"
            else:
                volume_level = f"{modulation.volume_multiplier:.1f}"
            tags.append(f'<prosody volume="{volume_level}">')
        
        # Speed
        if modulation.speed_multiplier != 1.0:
            if modulation.speed_multiplier < 0.8:
                rate = "slow"
            elif modulation.speed_multiplier > 1.2:
                rate = "fast"
            else:
                rate = f"{modulation.speed_multiplier:.1f}"
            tags.append(f'<prosody rate="{rate}">')
        
        # Pitch
        if modulation.pitch_adjustment != 0.0:
            pitch_change = f"{modulation.pitch_adjustment:+.1f}st"
            tags.append(f'<prosody pitch="{pitch_change}">')
        
        # Emphasis
        if modulation.tone in ['emphasis', 'strong_emphasis']:
            level = "strong" if modulation.tone == 'strong_emphasis' else "moderate"
            tags.append(f'<emphasis level="{level}">')
        
        # Build the complete SSML segment
        opening_tags = ''.join(tags)
        closing_tags = ''.join(f'</{tag.split()[0][1:]}>' for tag in reversed(tags))
        
        return f"{opening_tags}{content}{closing_tags}"
    
    def analyze_modulation_opportunities(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for potential voice modulation opportunities"""
        info = {
            'parenthetical_text': [],
            'emphasized_text': [],
            'quoted_text': [],
            'explicit_markers': [],
            'potential_whispers': []
        }
        
        # Find parenthetical text
        parenthetical = re.findall(r'\(([^)]+)\)', text)
        info['parenthetical_text'] = parenthetical
        
        # Find emphasized text (markdown style)
        emphasized = re.findall(r'\*([^*]+)\*', text)
        info['emphasized_text'] = emphasized
        
        # Find quoted text
        quoted = re.findall(r'"([^"]+)"', text)
        info['quoted_text'] = quoted
        
        # Find explicit markers
        explicit_markers = re.findall(r'\[([a-zA-Z_]+)\]', text)
        info['explicit_markers'] = explicit_markers
        
        # Find potential whisper opportunities (words that suggest quiet speech)
        whisper_indicators = ['whisper', 'quietly', 'softly', 'murmur', 'aside', 'secretly']
        for indicator in whisper_indicators:
            if indicator in text.lower():
                info['potential_whispers'].append(indicator)
        
        return info

    def _add_breathing_pauses(self, text: str, segments: List[ModulationSegment]) -> Tuple[str, List[ModulationSegment]]:
        """Add breathing pauses before and after parenthetical content"""
        if not segments:
            return text, segments

        # Sort segments by position (reverse order for text modification)
        sorted_segments = sorted(segments, key=lambda s: s.start_pos, reverse=True)
        modified_text = text
        updated_segments = []

        for segment in sorted_segments:
            # Check if this segment needs breathing pauses
            needs_breathing = (
                hasattr(segment.modulation, 'tone') and
                segment.modulation.tone in ['parenthetical_whisper', 'deep_whisper', 'aside']
            )

            if needs_breathing:
                # Add slight pause before parenthetical content
                pause_before = "... "  # Natural pause marker
                pause_after = " ..."   # Natural pause marker

                # Find the actual position in the processed text
                # (This is simplified - in a full implementation, you'd track position changes)
                start_pos = segment.start_pos
                end_pos = segment.end_pos

                # Add pauses around the content
                before_text = modified_text[:start_pos]
                segment_text = modified_text[start_pos:end_pos]
                after_text = modified_text[end_pos:]

                # Only add pauses if not already present
                if not before_text.endswith(('...', '. ', ', ')):
                    before_text += pause_before

                if not after_text.startswith(('...', ' .', ' ,')):
                    after_text = pause_after + after_text

                modified_text = before_text + segment_text + after_text

                # Update segment position
                segment.start_pos = len(before_text)
                segment.end_pos = segment.start_pos + len(segment_text)

            updated_segments.append(segment)

        # Reverse back to original order
        updated_segments.reverse()

        return modified_text, updated_segments

    def enhance_parenthetical_processing(self, text: str) -> str:
        """Enhanced processing specifically for parenthetical content"""
        # Detect different types of parenthetical content
        patterns = [
            (r'\(([Ii]magine[^)]*)\)', 'imagination'),
            (r'\(([Ff]or example[^)]*)\)', 'example'),
            (r'\(([Nn]ote[^)]*)\)', 'note'),
            (r'\(([Tt]hink[^)]*)\)', 'thought'),
            (r'\(([Ww]hisper[^)]*)\)', 'whisper_explicit'),
            (r'\(([^)]{1,20})\)', 'short_aside'),
            (r'\(([^)]{21,})\)', 'long_aside')
        ]

        processed_text = text

        for pattern, content_type in patterns:
            matches = re.finditer(pattern, processed_text)
            for match in matches:
                original = match.group(0)
                content = match.group(1)

                # Apply content-type specific processing
                if content_type == 'imagination':
                    # Extra soft for imagination prompts
                    replacement = f"[whisper]{content}[/whisper]"
                elif content_type == 'whisper_explicit':
                    # Deep whisper for explicit whisper requests
                    replacement = f"[deep_whisper]{content}[/deep_whisper]"
                elif content_type == 'long_aside':
                    # Slower pace for longer asides
                    replacement = f"[aside]{content}[/aside]"
                else:
                    # Standard parenthetical processing
                    replacement = f"[parenthetical]{content}[/parenthetical]"

                processed_text = processed_text.replace(original, replacement, 1)

        return processed_text
    
    def create_voice_profile(self, name: str, voice_name: str = "default",
                           volume_multiplier: float = 1.0, speed_multiplier: float = 1.0,
                           pitch_adjustment: float = 0.0, tone: str = "normal",
                           blend_ratio: float = 1.0):
        """Create a custom voice profile"""
        profile = VoiceModulation(
            voice_name=voice_name,
            volume_multiplier=volume_multiplier,
            speed_multiplier=speed_multiplier,
            pitch_adjustment=pitch_adjustment,
            tone=tone,
            blend_ratio=blend_ratio
        )
        
        self.voice_profiles[name] = profile
        logger.info(f"Created voice profile: {name}")
    
    def set_configuration(self, enable_parenthetical_whisper: bool = None,
                         enable_emphasis_detection: bool = None,
                         enable_voice_blending: bool = None,
                         default_whisper_voice: str = None):
        """Set configuration options"""
        if enable_parenthetical_whisper is not None:
            self.enable_parenthetical_whisper = enable_parenthetical_whisper
        if enable_emphasis_detection is not None:
            self.enable_emphasis_detection = enable_emphasis_detection
        if enable_voice_blending is not None:
            self.enable_voice_blending = enable_voice_blending
        if default_whisper_voice is not None:
            self.default_whisper_voice = default_whisper_voice
        
        logger.info(f"Voice modulation configuration updated: "
                   f"parenthetical_whisper={self.enable_parenthetical_whisper}, "
                   f"emphasis_detection={self.enable_emphasis_detection}, "
                   f"voice_blending={self.enable_voice_blending}, "
                   f"default_whisper_voice={self.default_whisper_voice}")
    
    def get_voice_profiles(self) -> Dict[str, VoiceModulation]:
        """Get all available voice profiles"""
        return self.voice_profiles.copy()
