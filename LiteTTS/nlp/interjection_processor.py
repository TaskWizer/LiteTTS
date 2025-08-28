#!/usr/bin/env python3
"""
Interjection processor for natural TTS pronunciation
Fixes issues like "hmm" → "hum" by extending interjections for natural pronunciation
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class InterjectionProcessor:
    """Processor to fix interjection pronunciation issues in TTS"""
    
    def __init__(self):
        self.interjection_fixes = self._load_interjection_fixes()
        self.hesitation_sounds = self._load_hesitation_sounds()
        
    def _load_interjection_fixes(self) -> Dict[str, str]:
        """Load interjection pronunciation fixes"""
        return {
            # Critical issue from user feedback
            "hmm": "hmmm",      # User reported: "hmm" → "hum", should be "hmmm"
            "Hmm": "Hmmm",      # Capitalized version
            "HMM": "HMMM",      # All caps version
            
            # Other common interjections that benefit from extension
            "mm": "mmm",        # Thinking sound
            "Mm": "Mmm",        # Capitalized
            "MM": "MMM",        # All caps
            
            # Hesitation sounds
            "uh": "uhh",        # Hesitation
            "Uh": "Uhh",        # Capitalized
            "UH": "UHH",        # All caps
            
            "um": "umm",        # Hesitation
            "Um": "Umm",        # Capitalized
            "UM": "UMM",        # All caps
            
            "er": "err",        # Hesitation
            "Er": "Err",        # Capitalized
            "ER": "ERR",        # All caps
            
            "ah": "ahh",        # Realization/understanding
            "Ah": "Ahh",        # Capitalized
            "AH": "AHH",        # All caps
            
            "oh": "ohh",        # Surprise/realization
            "Oh": "Ohh",        # Capitalized
            "OH": "OHH",        # All caps
        }
    
    def _load_hesitation_sounds(self) -> List[str]:
        """Load list of hesitation sounds for detection"""
        return [
            "hmm", "mm", "uh", "um", "er", "ah", "oh",
            "Hmm", "Mm", "Uh", "Um", "Er", "Ah", "Oh",
            "HMM", "MM", "UH", "UM", "ER", "AH", "OH"
        ]
    
    def process_interjections(self, text: str) -> str:
        """Process interjections for better TTS pronunciation"""
        logger.debug(f"Processing interjections in: {text[:100]}...")
        
        original_text = text
        
        # Apply interjection fixes with word boundaries
        for interjection, fix in self.interjection_fixes.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(interjection) + r'\b'
            text = re.sub(pattern, fix, text)
        
        if text != original_text:
            logger.debug(f"Interjection fixes applied: '{original_text}' → '{text}'")
        
        return text
    
    def analyze_interjections(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for interjection processing opportunities"""
        analysis = {
            'interjections_found': [],
            'hesitation_sounds': [],
            'potential_fixes': []
        }
        
        # Find all interjections
        for interjection in self.interjection_fixes.keys():
            pattern = r'\b' + re.escape(interjection) + r'\b'
            matches = re.finditer(pattern, text)
            for match in matches:
                analysis['interjections_found'].append(interjection)
                
                if interjection.lower() in [h.lower() for h in self.hesitation_sounds]:
                    analysis['hesitation_sounds'].append(interjection)
                
                fix = self.interjection_fixes[interjection]
                analysis['potential_fixes'].append(f"{interjection} → {fix}")
        
        return analysis
    
    def is_interjection(self, word: str) -> bool:
        """Check if a word is an interjection"""
        return word in self.interjection_fixes
    
    def get_interjection_fix(self, word: str) -> str:
        """Get the pronunciation fix for an interjection"""
        return self.interjection_fixes.get(word, word)

# Global instance for easy access
interjection_processor = InterjectionProcessor()

def process_interjections(text: str) -> str:
    """Convenience function to process interjections"""
    return interjection_processor.process_interjections(text)

def analyze_interjections(text: str) -> Dict[str, List[str]]:
    """Convenience function to analyze interjections"""
    return interjection_processor.analyze_interjections(text)
