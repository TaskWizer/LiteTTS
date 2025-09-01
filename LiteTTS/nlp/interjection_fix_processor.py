#!/usr/bin/env python3
"""
Interjection pronunciation fix processor for TTS
Fixes "hmm" → "hum" and similar interjection pronunciation issues
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class InterjectionFixProcessor:
    """Processor to fix interjection pronunciation issues in TTS"""
    
    def __init__(self):
        self.interjection_fixes = self._load_interjection_fixes()
        self.phonetic_interjections = self._load_phonetic_interjections()
        self.context_patterns = self._load_context_patterns()
        
    def _load_interjection_fixes(self) -> Dict[str, str]:
        """Load interjection pronunciation fixes"""
        return {
            # Thinking/pondering sounds
            "hmm": "hmm",  # Keep as-is but ensure proper processing
            "Hmm": "Hmm",
            "hm": "hmm",   # Expand short form
            "Hm": "Hmm",
            "mmm": "mmm",  # Thinking sound
            "Mmm": "Mmm",
            "mm": "mmm",   # Expand short form
            "Mm": "Mmm",
            
            # Agreement/acknowledgment
            "uh-huh": "uh-huh",
            "Uh-huh": "Uh-huh", 
            "mm-hmm": "mm-hmm",
            "Mm-hmm": "Mm-hmm",
            "mhm": "mm-hmm",  # Expand
            "Mhm": "Mm-hmm",
            "yeah": "yeah",
            "Yeah": "Yeah",
            "yep": "yep",
            "Yep": "Yep",
            "yup": "yup",
            "Yup": "Yup",
            
            # Disagreement/negative
            "uh-uh": "uh-uh",
            "Uh-uh": "Uh-uh",
            "nah": "nah", 
            "Nah": "Nah",
            "nope": "nope",
            "Nope": "Nope",
            
            # Hesitation/filler
            "uh": "uh",
            "Uh": "Uh",
            "um": "um",
            "Um": "Um",
            "er": "er",
            "Er": "Er",
            "ah": "ah",
            "Ah": "Ah",
            "oh": "oh",
            "Oh": "Oh",
            
            # Surprise/realization
            "ooh": "ooh",
            "Ooh": "Ooh",
            "aah": "aah",
            "Aah": "Aah",
            "wow": "wow",
            "Wow": "Wow",
            "whoa": "whoa",
            "Whoa": "Whoa",
            
            # Pain/discomfort
            "ow": "ow",
            "Ow": "Ow",
            "ouch": "ouch",
            "Ouch": "Ouch",
            "oof": "oof",
            "Oof": "Oof",
            
            # Disgust/disapproval
            "ew": "ew",
            "Ew": "Ew",
            "eww": "eww",
            "Eww": "Eww",
            "ugh": "ugh",
            "Ugh": "Ugh",
            "bleh": "bleh",
            "Bleh": "Bleh",
            
            # Laughter
            "haha": "ha-ha",
            "Haha": "Ha-ha",
            "hehe": "he-he", 
            "Hehe": "He-he",
            "hihi": "hi-hi",
            "Hihi": "Hi-hi",
            
            # Shushing
            "shh": "shh",
            "Shh": "Shh",
            "shhh": "shhh",
            "Shhh": "Shhh",
            
            # Calling attention
            "hey": "hey",
            "Hey": "Hey",
            "psst": "psst",
            "Psst": "Psst",
            "ahem": "ahem",
            "Ahem": "Ahem",
        }
    
    def _load_phonetic_interjections(self) -> Dict[str, str]:
        """Load phonetic representations for interjections"""
        return {
            # Correct phonetic approach - lengthen for natural pronunciation
            "hmm": "hmmm",  # Lengthen to ensure proper pronunciation (NOT H-M-M)
            "Hmm": "Hmmm",
            "hm": "hmmm",   # Expand and lengthen
            "Hm": "Hmmm",

            # Nasal sounds - lengthen for natural pronunciation
            "mm": "mmmm",
            "Mm": "Mmmm",
            "mmm": "mmmm",
            "Mmm": "Mmmm",
            
            # Ensure proper vowel sounds
            "uh": "uhh",
            "Uh": "Uhh",
            "um": "umm", 
            "Um": "Umm",
            "ah": "ahh",
            "Ah": "Ahh",
            "oh": "ohh",
            "Oh": "Ohh",
            
            # Laughter with proper separation
            "haha": "ha ha",
            "Haha": "Ha ha",
            "hehe": "he he",
            "Hehe": "He he",
        }
    
    def _load_context_patterns(self) -> List[Tuple[str, str, str]]:
        """Load context-based interjection patterns"""
        return [
            # Pattern, Replacement, Description
            # COMPOUND INTERJECTIONS FIRST (to prevent individual processing)
            (r'\bmm-hmm\b', 'mm-hmm', 'Preserve mm-hmm compound'),
            (r'\bMm-hmm\b', 'Mm-hmm', 'Preserve Mm-hmm compound'),
            (r'\bMM-HMM\b', 'MM-HMM', 'Preserve MM-HMM compound'),
            (r'\buh-huh\b', 'uh-huh', 'Preserve uh-huh compound'),
            (r'\bUh-huh\b', 'Uh-huh', 'Preserve Uh-huh compound'),
            (r'\bUH-HUH\b', 'UH-HUH', 'Preserve UH-HUH compound'),

            # INDIVIDUAL INTERJECTIONS (after compounds, with compound exclusions)
            (r'(?<!-)\bhmm\b(?!-)', 'hmmm', 'Fix hmm pronunciation (not in compounds)'),
            (r'(?<!-)\bHmm\b(?!-)', 'Hmmm', 'Fix Hmm pronunciation (not in compounds)'),
            (r'(?<!-)\bhm\b(?!-)', 'hmmm', 'Expand hm to hmmm (not in compounds)'),
            (r'(?<!-)\bHm\b(?!-)', 'Hmmm', 'Expand Hm to Hmmm (not in compounds)'),
            (r'(?<!-)\bmmm\b(?!-)', 'mmmm', 'Fix mmm pronunciation (not in compounds)'),
            (r'(?<!-)\bMmm\b(?!-)', 'Mmmm', 'Fix Mmm pronunciation (not in compounds)'),
            (r'(?<!-)\bmm\b(?!-)', 'mmmm', 'Expand mm to mmmm (not in compounds)'),
            (r'(?<!-)\bMm\b(?!-)', 'Mmmm', 'Expand Mm to Mmmm (not in compounds)'),
            
            # Hesitation sounds
            (r'\buh\b', 'uhh', 'Fix uh pronunciation'),
            (r'\bUh\b', 'Uhh', 'Fix Uh pronunciation'),
            (r'\bum\b', 'umm', 'Fix um pronunciation'),
            (r'\bUm\b', 'Umm', 'Fix Um pronunciation'),
            (r'\ber\b', 'err', 'Fix er pronunciation'),
            (r'\bEr\b', 'Err', 'Fix Er pronunciation'),
            
            # Vowel sounds
            (r'\bah\b', 'ahh', 'Fix ah pronunciation'),
            (r'\bAh\b', 'Ahh', 'Fix Ah pronunciation'),
            (r'\boh\b', 'ohh', 'Fix oh pronunciation'),
            (r'\bOh\b', 'Ohh', 'Fix Oh pronunciation'),
            
            # Agreement sounds
            (r'\bmhm\b', 'mm-hmm', 'Expand mhm to mm-hmm'),
            (r'\bMhm\b', 'Mm-hmm', 'Expand Mhm to Mm-hmm'),
            
            # Laughter
            (r'\bhaha\b', 'ha ha', 'Fix haha pronunciation'),
            (r'\bHaha\b', 'Ha ha', 'Fix Haha pronunciation'),
            (r'\bhehe\b', 'he he', 'Fix hehe pronunciation'),
            (r'\bHehe\b', 'He he', 'Fix Hehe pronunciation'),
            (r'\bhihi\b', 'hi hi', 'Fix hihi pronunciation'),
            (r'\bHihi\b', 'Hi hi', 'Fix Hihi pronunciation'),
        ]
    
    def fix_interjection_pronunciation(self, text: str) -> str:
        """Fix interjection pronunciation issues in text"""
        logger.debug(f"Fixing interjection pronunciation in: {text[:100]}...")
        
        original_text = text
        
        # Step 1: Apply context-based patterns
        text = self._apply_context_patterns(text)
        
        # Step 2: Handle special cases
        text = self._handle_special_cases(text)
        
        # Step 3: Ensure proper spacing around interjections
        text = self._fix_interjection_spacing(text)
        
        if text != original_text:
            logger.debug(f"Interjection fixes applied: '{original_text}' → '{text}'")
        
        return text
    
    def _apply_context_patterns(self, text: str) -> str:
        """Apply context-based interjection patterns"""
        # First, protect compound interjections by temporarily replacing them
        protected_compounds = {}
        compound_patterns = [
            (r'\bmm-hmm\b', 'mm-hmm'),
            (r'\bMm-hmm\b', 'Mm-hmm'),
            (r'\bMM-HMM\b', 'MM-HMM'),
            (r'\buh-huh\b', 'uh-huh'),
            (r'\bUh-huh\b', 'Uh-huh'),
            (r'\bUH-HUH\b', 'UH-HUH'),
        ]

        # Replace compounds with placeholders (exact case matching)
        for i, (pattern, replacement) in enumerate(compound_patterns):
            placeholder = f"__COMPOUND_{i}__"
            if re.search(pattern, text):  # No case-insensitive flag
                protected_compounds[placeholder] = replacement
                text = re.sub(pattern, placeholder, text)  # No case-insensitive flag

        # Apply individual interjection patterns (skipping compound patterns)
        for pattern, replacement, description in self.context_patterns:
            # Skip compound preservation patterns since we handled them above
            if 'preserve' in description.lower() and 'compound' in description.lower():
                continue

            if re.search(pattern, text):  # Exact case matching
                old_text = text
                text = re.sub(pattern, replacement, text)  # Exact case matching
                if text != old_text:
                    logger.debug(f"Applied {description}")

        # Restore protected compounds
        for placeholder, original in protected_compounds.items():
            text = text.replace(placeholder, original)

        return text
    
    def _handle_special_cases(self, text: str) -> str:
        """Handle special interjection cases"""
        # Handle interjections at sentence start (avoid compounds)
        text = re.sub(r'^(?<!-)hmm(?!-)\b', r'Hmmm', text, flags=re.IGNORECASE)
        text = re.sub(r'^(?<!-)mm(?!-)\b', r'Mmmm', text, flags=re.IGNORECASE)
        text = re.sub(r'^(?<!-)uh(?!-)\b', r'Uhh', text, flags=re.IGNORECASE)
        text = re.sub(r'^(?<!-)um(?!-)\b', r'Umm', text, flags=re.IGNORECASE)
        
        # Handle interjections after punctuation (avoid compounds)
        text = re.sub(r'\. (?<!-)hmm(?!-)\b', r'. Hmmm', text, flags=re.IGNORECASE)
        text = re.sub(r'\. (?<!-)mm(?!-)\b', r'. Mmmm', text, flags=re.IGNORECASE)
        text = re.sub(r'\. (?<!-)uh(?!-)\b', r'. Uhh', text, flags=re.IGNORECASE)
        text = re.sub(r'\. (?<!-)um(?!-)\b', r'. Umm', text, flags=re.IGNORECASE)

        # Handle interjections with punctuation (avoid compounds) - PRESERVE SPACING
        text = re.sub(r'(?<!-)hmm(?!-)(,\s*)', r'hmmm\1', text, flags=re.IGNORECASE)
        text = re.sub(r'(?<!-)hmm(?!-)(\.)', r'hmmm\1', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(hmm)(\?)', r'hmmm\2', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(hmm)(!)', r'hmmm\2', text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_interjection_spacing(self, text: str) -> str:
        """Fix spacing around interjections"""
        # Ensure space after interjections when followed by words
        interjections = ['hmmm', 'mmmm', 'uhh', 'umm', 'ahh', 'ohh', 'err']
        
        for interjection in interjections:
            # Add space after interjection if missing
            pattern = r'\b(' + re.escape(interjection) + r')([a-zA-Z])'
            replacement = r'\1 \2'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def analyze_interjection_issues(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for interjection pronunciation issues"""
        issues = {
            'short_interjections': [],
            'nasal_sounds': [],
            'hesitation_markers': [],
            'potential_fixes': []
        }
        
        # Find short interjections that might need expansion
        short_patterns = [r'\bhm\b', r'\bmm\b', r'\buh\b', r'\bum\b', r'\ber\b', r'\bah\b', r'\boh\b']
        for pattern in short_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues['short_interjections'].extend(matches)
        
        # Find nasal sounds
        nasal_patterns = [r'\bhmm\b', r'\bmmm\b', r'\bmhm\b']
        for pattern in nasal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues['nasal_sounds'].extend(matches)
        
        # Find hesitation markers
        hesitation_patterns = [r'\buh\b', r'\bum\b', r'\ber\b', r'\bwell\b']
        for pattern in hesitation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues['hesitation_markers'].extend(matches)
        
        # Check for potential fixes
        for interjection, fix in self.interjection_fixes.items():
            if interjection.lower() in text.lower() and interjection != fix:
                issues['potential_fixes'].append(f"{interjection} → {fix}")
        
        return issues

# Global instance for easy access
interjection_fix_processor = InterjectionFixProcessor()
