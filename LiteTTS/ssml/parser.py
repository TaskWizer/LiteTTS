#!/usr/bin/env python3
"""
SSML Parser for Kokoro TTS

Handles parsing and processing of Speech Synthesis Markup Language (SSML) tags,
with special support for background noise enhancement.
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class BackgroundType(Enum):
    """Supported background noise types"""
    COFFEE_SHOP = "coffee_shop"
    OFFICE = "office"
    NATURE = "nature"
    RAIN = "rain"
    WIND = "wind"
    WHITE_NOISE = "white_noise"
    PINK_NOISE = "pink_noise"
    BROWN_NOISE = "brown_noise"
    CUSTOM = "custom"

@dataclass
class BackgroundConfig:
    """Configuration for background noise"""
    type: BackgroundType
    volume: float = 0.3  # 0.0 to 1.0
    fade_in: float = 0.5  # seconds
    fade_out: float = 0.5  # seconds
    loop: bool = True
    custom_file: Optional[str] = None

@dataclass
class SSMLElement:
    """Represents a parsed SSML element"""
    tag: str
    text: str
    attributes: Dict[str, str]
    children: List['SSMLElement']
    start_pos: int = 0
    end_pos: int = 0

@dataclass
class ParsedSSML:
    """Result of SSML parsing"""
    plain_text: str
    background_config: Optional[BackgroundConfig]
    prosody_changes: List[Dict[str, Any]]
    emphasis_spans: List[Tuple[int, int, str]]  # start, end, level
    break_positions: List[Tuple[int, float]]  # position, duration
    errors: List[str]

class SSMLParser:
    """
    SSML Parser with background noise support
    
    Supports standard SSML tags plus custom <background> tag for ambient audio.
    """
    
    def __init__(self):
        self.supported_tags = {
            'speak', 'background', 'prosody', 'emphasis', 'break', 
            'say-as', 'sub', 'phoneme', 'voice', 'lang'
        }
        
        # Background noise mappings
        self.background_types = {
            'coffee-shop': BackgroundType.COFFEE_SHOP,
            'coffee_shop': BackgroundType.COFFEE_SHOP,
            'cafe': BackgroundType.COFFEE_SHOP,
            'office': BackgroundType.OFFICE,
            'workplace': BackgroundType.OFFICE,
            'nature': BackgroundType.NATURE,
            'forest': BackgroundType.NATURE,
            'rain': BackgroundType.RAIN,
            'rainfall': BackgroundType.RAIN,
            'wind': BackgroundType.WIND,
            'windy': BackgroundType.WIND,
            'white-noise': BackgroundType.WHITE_NOISE,
            'white_noise': BackgroundType.WHITE_NOISE,
            'pink-noise': BackgroundType.PINK_NOISE,
            'pink_noise': BackgroundType.PINK_NOISE,
            'brown-noise': BackgroundType.BROWN_NOISE,
            'brown_noise': BackgroundType.BROWN_NOISE,
            'custom': BackgroundType.CUSTOM
        }
    
    def parse(self, ssml_text: str) -> ParsedSSML:
        """
        Parse SSML text and extract components

        Args:
            ssml_text: SSML markup text

        Returns:
            ParsedSSML object with extracted components
        """
        errors = []

        try:
            # Step 1: Decode HTML entities if present
            import html
            decoded_text = html.unescape(ssml_text)

            # Check if input contains SSML tags (after decoding)
            if not self._contains_ssml(decoded_text):
                # Plain text input
                return ParsedSSML(
                    plain_text=decoded_text,
                    background_config=None,
                    prosody_changes=[],
                    emphasis_spans=[],
                    break_positions=[],
                    errors=[]
                )

            # Use decoded text for further processing
            ssml_text = decoded_text
            
            # Wrap in speak tag if not already wrapped
            if not ssml_text.strip().startswith('<speak'):
                ssml_text = f'<speak>{ssml_text}</speak>'
            
            # Parse XML
            try:
                root = ET.fromstring(ssml_text)
            except ET.ParseError as e:
                # Try to fix common SSML issues
                fixed_ssml = self._fix_common_ssml_issues(ssml_text)
                try:
                    root = ET.fromstring(fixed_ssml)
                except ET.ParseError:
                    errors.append(f"SSML parsing failed: {e}")
                    # Return plain text fallback
                    plain_text = re.sub(r'<[^>]+>', '', ssml_text)
                    return ParsedSSML(
                        plain_text=plain_text,
                        background_config=None,
                        prosody_changes=[],
                        emphasis_spans=[],
                        break_positions=[],
                        errors=errors
                    )
            
            # Extract components
            plain_text = self._extract_text(root)
            background_config = self._extract_background_config(root)
            prosody_changes = self._extract_prosody_changes(root)
            emphasis_spans = self._extract_emphasis_spans(root, plain_text)
            break_positions = self._extract_break_positions(root, plain_text)
            
            return ParsedSSML(
                plain_text=plain_text,
                background_config=background_config,
                prosody_changes=prosody_changes,
                emphasis_spans=emphasis_spans,
                break_positions=break_positions,
                errors=errors
            )
            
        except Exception as e:
            errors.append(f"Unexpected parsing error: {e}")
            logger.error(f"SSML parsing error: {e}")
            
            # Fallback to plain text
            plain_text = re.sub(r'<[^>]+>', '', ssml_text)
            return ParsedSSML(
                plain_text=plain_text,
                background_config=None,
                prosody_changes=[],
                emphasis_spans=[],
                break_positions=[],
                errors=errors
            )
    
    def _contains_ssml(self, text: str) -> bool:
        """Check if text contains SSML tags"""
        return bool(re.search(r'<[^>]+>', text))
    
    def _fix_common_ssml_issues(self, ssml_text: str) -> str:
        """Fix common SSML formatting issues"""
        # Escape unescaped ampersands
        ssml_text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', ssml_text)
        
        # Fix unclosed self-closing tags
        ssml_text = re.sub(r'<(break|phoneme)([^>]*[^/])>', r'<\1\2/>', ssml_text)
        
        return ssml_text
    
    def _extract_text(self, element: ET.Element) -> str:
        """Extract plain text from SSML element tree"""
        text_parts = []
        
        if element.text:
            text_parts.append(element.text)
        
        for child in element:
            if child.tag == 'break':
                # Add space for breaks
                text_parts.append(' ')
            else:
                text_parts.append(self._extract_text(child))
            
            if child.tail:
                text_parts.append(child.tail)
        
        return ''.join(text_parts).strip()
    
    def _extract_background_config(self, root: ET.Element) -> Optional[BackgroundConfig]:
        """Extract background configuration from SSML"""
        background_elem = root.find('.//background')
        if background_elem is None:
            return None
        
        # Get background type
        bg_type_str = background_elem.get('type', 'nature').lower()
        bg_type = self.background_types.get(bg_type_str, BackgroundType.NATURE)
        
        # Get volume (0-100 or 0.0-1.0)
        volume_str = background_elem.get('volume', '30')
        try:
            volume = float(volume_str)
            if volume > 1.0:
                volume = volume / 100.0  # Convert percentage to decimal
            volume = max(0.0, min(1.0, volume))  # Clamp to valid range
        except ValueError:
            volume = 0.3
        
        # Get fade settings
        fade_in = float(background_elem.get('fade-in', '0.5'))
        fade_out = float(background_elem.get('fade-out', '0.5'))
        
        # Get loop setting
        loop = background_elem.get('loop', 'true').lower() == 'true'
        
        # Get custom file if specified
        custom_file = background_elem.get('src') or background_elem.get('file')
        
        return BackgroundConfig(
            type=bg_type,
            volume=volume,
            fade_in=fade_in,
            fade_out=fade_out,
            loop=loop,
            custom_file=custom_file
        )
    
    def _extract_prosody_changes(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract prosody changes from SSML"""
        prosody_changes = []
        
        for prosody_elem in root.findall('.//prosody'):
            change = {}
            
            # Extract prosody attributes
            if 'rate' in prosody_elem.attrib:
                change['rate'] = prosody_elem.get('rate')
            if 'pitch' in prosody_elem.attrib:
                change['pitch'] = prosody_elem.get('pitch')
            if 'volume' in prosody_elem.attrib:
                change['volume'] = prosody_elem.get('volume')
            
            if change:
                change['text'] = self._extract_text(prosody_elem)
                prosody_changes.append(change)
        
        return prosody_changes
    
    def _extract_emphasis_spans(self, root: ET.Element, plain_text: str) -> List[Tuple[int, int, str]]:
        """Extract emphasis spans from SSML"""
        emphasis_spans = []
        
        for emphasis_elem in root.findall('.//emphasis'):
            level = emphasis_elem.get('level', 'moderate')
            text = self._extract_text(emphasis_elem)
            
            # Find position in plain text (simplified)
            start_pos = plain_text.find(text)
            if start_pos >= 0:
                end_pos = start_pos + len(text)
                emphasis_spans.append((start_pos, end_pos, level))
        
        return emphasis_spans
    
    def _extract_break_positions(self, root: ET.Element, plain_text: str) -> List[Tuple[int, float]]:
        """Extract break positions from SSML"""
        break_positions = []
        
        # This is a simplified implementation
        # In practice, you'd need to track positions more carefully
        for break_elem in root.findall('.//break'):
            time_str = break_elem.get('time', '0.5s')
            
            # Parse time value
            if time_str.endswith('s'):
                duration = float(time_str[:-1])
            elif time_str.endswith('ms'):
                duration = float(time_str[:-2]) / 1000.0
            else:
                duration = 0.5
            
            # For now, just add to end of current text
            # In practice, you'd track the exact position
            break_positions.append((len(plain_text), duration))
        
        return break_positions
    
    def validate_ssml(self, ssml_text: str) -> List[str]:
        """Validate SSML markup and return list of errors"""
        errors = []
        
        try:
            parsed = self.parse(ssml_text)
            errors.extend(parsed.errors)
            
            # Additional validation
            if parsed.background_config:
                bg = parsed.background_config
                if bg.type == BackgroundType.CUSTOM and not bg.custom_file:
                    errors.append("Custom background type requires 'src' or 'file' attribute")
                
                if not (0.0 <= bg.volume <= 1.0):
                    errors.append(f"Background volume must be between 0.0 and 1.0, got {bg.volume}")
        
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return errors
