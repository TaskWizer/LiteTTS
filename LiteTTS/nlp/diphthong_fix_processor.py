#!/usr/bin/env python3
"""
Diphthong pronunciation fix processor for TTS
Fixes "joy" → "ju-ie" and similar diphthong pronunciation issues
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class DiphthongFixProcessor:
    """Processor to fix diphthong pronunciation issues in TTS"""
    
    def __init__(self):
        self.diphthong_fixes = self._load_diphthong_fixes()
        self.phonetic_overrides = self._load_phonetic_overrides()
        self.context_patterns = self._load_context_patterns()
        
    def _load_diphthong_fixes(self) -> Dict[str, str]:
        """Load diphthong pronunciation fixes"""
        return {
            # /ɔɪ/ diphthong words (oy sound)
            "joy": "JOY",  # Emphasize proper pronunciation
            "Joy": "JOY",
            "boy": "BOY", 
            "Boy": "BOY",
            "toy": "TOY",
            "Toy": "TOY",
            "coy": "COY",
            "Coy": "COY",
            "soy": "SOY",
            "Soy": "SOY",
            "ploy": "PLOY",
            "Ploy": "PLOY",
            "troy": "TROY",
            "Troy": "TROY",
            "ahoy": "ah-HOY",
            "Ahoy": "ah-HOY",
            "annoy": "an-NOY",
            "Annoy": "an-NOY",
            "enjoy": "en-JOY",
            "Enjoy": "en-JOY",
            "employ": "em-PLOY",
            "Employ": "em-PLOY",
            "deploy": "de-PLOY",
            "Deploy": "de-PLOY",
            "destroy": "de-STROY",
            "Destroy": "de-STROY",
            
            # /aɪ/ diphthong words (ai/ay sound)
            "buy": "BUY",
            "Buy": "BUY",
            "guy": "GUY",
            "Guy": "GUY",
            "shy": "SHY",
            "Shy": "SHY",
            "try": "TRY",
            "Try": "TRY",
            "cry": "CRY",
            "Cry": "CRY",
            "dry": "DRY",
            "Dry": "DRY",
            "fly": "FLY",
            "Fly": "FLY",
            "sky": "SKY",
            "Sky": "SKY",
            "why": "WHY",
            "Why": "WHY",
            "my": "MY",
            "My": "MY",
            "by": "BY",
            "By": "BY",
            "eye": "EYE",
            "Eye": "EYE",
            "die": "DIE",
            "Die": "DIE",
            "lie": "LIE",
            "Lie": "LIE",
            "pie": "PIE",
            "Pie": "PIE",
            "tie": "TIE",
            "Tie": "TIE",
            
            # /aʊ/ diphthong words (ow sound)
            "how": "HOW",
            "How": "HOW",
            "now": "NOW",
            "Now": "NOW",
            "cow": "COW",
            "Cow": "COW",
            "bow": "BOW",  # as in bow down
            "Bow": "BOW",
            "wow": "WOW",
            "Wow": "WOW",
            "vow": "VOW",
            "Vow": "VOW",
            "plow": "PLOW",
            "Plow": "PLOW",
            "brow": "BROW",
            "Brow": "BROW",
            "allow": "al-LOW",
            "Allow": "al-LOW",
        }
    
    def _load_phonetic_overrides(self) -> Dict[str, str]:
        """Load phonetic spelling overrides for problematic words"""
        return {
            # Words that need phonetic spelling to fix pronunciation
            "joy": "j-oy",  # Ensure the diphthong is pronounced correctly
            "Joy": "J-oy",
            "boy": "b-oy",
            "Boy": "B-oy", 
            "toy": "t-oy",
            "Toy": "T-oy",
            
            # Alternative phonetic representations
            "enjoy": "en-j-oy",
            "Enjoy": "En-j-oy",
            "annoy": "an-n-oy", 
            "Annoy": "An-n-oy",
            
            # Words with /aɪ/ that might be mispronounced
            "buy": "b-uy",
            "Buy": "B-uy",
            "guy": "g-uy", 
            "Guy": "G-uy",
            "try": "tr-y",
            "Try": "Tr-y",
            
            # Words with /aʊ/ that might be mispronounced  
            "how": "h-ow",
            "How": "H-ow",
            "now": "n-ow",
            "Now": "N-ow",
            "cow": "c-ow",
            "Cow": "C-ow",
        }
    
    def _load_context_patterns(self) -> List[Tuple[str, str, str]]:
        """Load context-based pronunciation patterns"""
        return [
            # Pattern, Replacement, Description
            (r'\b(joy)\b', r'j-oy', 'Fix joy diphthong pronunciation'),
            (r'\b(Joy)\b', r'J-oy', 'Fix Joy diphthong pronunciation'),
            (r'\b(boy)\b', r'b-oy', 'Fix boy diphthong pronunciation'),
            (r'\b(Boy)\b', r'B-oy', 'Fix Boy diphthong pronunciation'),
            (r'\b(toy)\b', r't-oy', 'Fix toy diphthong pronunciation'),
            (r'\b(Toy)\b', r'T-oy', 'Fix Toy diphthong pronunciation'),
            
            # Compound words and phrases
            (r'\b(enjoy)\b', r'en-j-oy', 'Fix enjoy diphthong pronunciation'),
            (r'\b(Enjoy)\b', r'En-j-oy', 'Fix Enjoy diphthong pronunciation'),
            (r'\b(annoy)\b', r'an-n-oy', 'Fix annoy diphthong pronunciation'),
            (r'\b(Annoy)\b', r'An-n-oy', 'Fix Annoy diphthong pronunciation'),
            
            # Common phrases where diphthongs are mispronounced
            (r'\b(oh joy)\b', r'oh j-oy', 'Fix "oh joy" phrase'),
            (r'\b(Oh joy)\b', r'Oh j-oy', 'Fix "Oh joy" phrase'),
            (r'\b(good boy)\b', r'good b-oy', 'Fix "good boy" phrase'),
            (r'\b(Good boy)\b', r'Good b-oy', 'Fix "Good boy" phrase'),
            (r'\b(new toy)\b', r'new t-oy', 'Fix "new toy" phrase'),
            (r'\b(New toy)\b', r'New t-oy', 'Fix "New toy" phrase'),
        ]
    
    def fix_diphthong_pronunciation(self, text: str) -> str:
        """Fix diphthong pronunciation issues in text"""
        logger.debug(f"Fixing diphthong pronunciation in: {text[:100]}...")
        
        original_text = text
        
        # Step 1: Apply context-based patterns
        text = self._apply_context_patterns(text)
        
        # Step 2: Apply direct word replacements
        text = self._apply_word_replacements(text)
        
        # Step 3: Handle special cases
        text = self._handle_special_cases(text)
        
        if text != original_text:
            logger.debug(f"Diphthong fixes applied: '{original_text}' → '{text}'")
        
        return text
    
    def _apply_context_patterns(self, text: str) -> str:
        """Apply context-based pronunciation patterns"""
        for pattern, replacement, description in self.context_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                old_text = text
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                if text != old_text:
                    logger.debug(f"Applied {description}: pattern matched")
        
        return text
    
    def _apply_word_replacements(self, text: str) -> str:
        """Apply direct word-to-phonetic replacements"""
        words = text.split()
        modified = False
        
        for i, word in enumerate(words):
            # Remove punctuation for matching
            clean_word = re.sub(r'[^\w]', '', word)
            
            if clean_word in self.phonetic_overrides:
                # Preserve punctuation
                punctuation = re.findall(r'[^\w]', word)
                replacement = self.phonetic_overrides[clean_word]
                
                # Add back punctuation
                if punctuation:
                    replacement += ''.join(punctuation)
                
                words[i] = replacement
                modified = True
                logger.debug(f"Replaced '{word}' with '{replacement}'")
        
        return ' '.join(words) if modified else text
    
    def _handle_special_cases(self, text: str) -> str:
        """Handle special pronunciation cases"""
        # Handle words at sentence boundaries
        text = re.sub(r'\. (joy)\b', r'. j-oy', text, flags=re.IGNORECASE)
        text = re.sub(r'\. (Joy)\b', r'. J-oy', text, flags=re.IGNORECASE)
        text = re.sub(r'\. (boy)\b', r'. b-oy', text, flags=re.IGNORECASE)
        text = re.sub(r'\. (Boy)\b', r'. B-oy', text, flags=re.IGNORECASE)
        
        # Handle words after commas
        text = re.sub(r', (joy)\b', r', j-oy', text, flags=re.IGNORECASE)
        text = re.sub(r', (Joy)\b', r', J-oy', text, flags=re.IGNORECASE)
        text = re.sub(r', (boy)\b', r', b-oy', text, flags=re.IGNORECASE)
        text = re.sub(r', (Boy)\b', r', B-oy', text, flags=re.IGNORECASE)
        
        # Handle exclamations
        text = re.sub(r'\b(joy)!', r'j-oy!', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(Joy)!', r'J-oy!', text, flags=re.IGNORECASE)
        
        return text
    
    def analyze_diphthong_issues(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for potential diphthong pronunciation issues"""
        issues = {
            'oy_diphthongs': [],
            'ay_diphthongs': [],
            'ow_diphthongs': [],
            'potential_fixes': []
        }
        
        # Find /ɔɪ/ diphthong words
        oy_pattern = r'\b\w*oy\w*\b'
        oy_matches = re.findall(oy_pattern, text, re.IGNORECASE)
        issues['oy_diphthongs'] = oy_matches
        
        # Find /aɪ/ diphthong words  
        ay_pattern = r'\b\w*[aeiou]y\b|\b\w*ie\b|\b\w*uy\b'
        ay_matches = re.findall(ay_pattern, text, re.IGNORECASE)
        issues['ay_diphthongs'] = ay_matches
        
        # Find /aʊ/ diphthong words
        ow_pattern = r'\b\w*ow\w*\b'
        ow_matches = re.findall(ow_pattern, text, re.IGNORECASE)
        issues['ow_diphthongs'] = ow_matches
        
        # Check for words that have fixes available
        for word in text.split():
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.phonetic_overrides:
                issues['potential_fixes'].append(f"{clean_word} → {self.phonetic_overrides[clean_word]}")
        
        return issues

# Global instance for easy access
diphthong_fix_processor = DiphthongFixProcessor()
