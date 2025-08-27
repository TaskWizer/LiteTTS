#!/usr/bin/env python3
"""
Contraction pronunciation fix processor for TTS
Fixes "I'm" → "im" instead of "I-m" and similar contraction issues
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class ContractionPronunciationFix:
    """Processor to fix contraction pronunciation issues in TTS"""
    
    def __init__(self):
        self.contraction_fixes = self._load_contraction_fixes()
        self.phonetic_contractions = self._load_phonetic_contractions()
        self.problematic_patterns = self._load_problematic_patterns()
        
    def _load_contraction_fixes(self) -> Dict[str, str]:
        """Load contraction pronunciation fixes"""
        return {
            # First person contractions
            "I'm": "I am",  # Expand to ensure proper pronunciation
            "I'll": "I will",
            "I'd": "I would", 
            "I've": "I have",
            "I're": "I are",  # Non-standard but sometimes used
            
            # Alternative phonetic approach for problematic contractions
            "I'm": "I-am",  # Hyphenated to ensure separation
            "you're": "you-are",
            "we're": "we-are", 
            "they're": "they-are",
            "you'll": "you-will",
            "we'll": "we-will",
            "they'll": "they-will",
            "you'd": "you-would",
            "we'd": "we-would", 
            "they'd": "they-would",
            "you've": "you-have",
            "we've": "we-have",
            "they've": "they-have",
            
            # Problematic contractions that lose pronunciation clarity
            "he'll": "he-will",
            "she'll": "she-will", 
            "it'll": "it-will",
            "he'd": "he-would",
            "she'd": "she-would",
            "it'd": "it-would",
            "he's": "he-is",
            "she's": "she-is",
            "it's": "it-is",
            
            # Modal contractions
            "won't": "will not",  # Irregular contraction
            "can't": "cannot",
            "couldn't": "could not",
            "shouldn't": "should not", 
            "wouldn't": "would not",
            "mustn't": "must not",
            "needn't": "need not",
            
            # Negative contractions (keep some natural ones)
            "don't": "don't",  # Keep natural
            "doesn't": "doesn't",  # Keep natural
            "didn't": "didn't",  # Keep natural
            "isn't": "isn't",  # Keep natural
            "aren't": "aren't",  # Keep natural
            "wasn't": "wasn't",  # Keep natural
            "weren't": "weren't",  # Keep natural
            "hasn't": "hasn't",  # Keep natural
            "haven't": "haven't",  # Keep natural
            "hadn't": "hadn't",  # Keep natural
        }
    
    def _load_phonetic_contractions(self) -> Dict[str, str]:
        """Load phonetic representations for contractions"""
        return {
            # Phonetic spellings to ensure proper pronunciation
            "I'm": "I-M",  # Emphasize both parts
            "you're": "YOU-R",
            "we're": "WE-R", 
            "they're": "THEY-R",
            "he's": "HE-Z",
            "she's": "SHE-Z",
            "it's": "IT-S",
            
            # Alternative approach: spell out the sounds
            "I'm": "eye-m",
            "you're": "you-r",
            "we're": "we-r",
            "they're": "they-r",
            
            # For very problematic cases, use full expansion
            "I'll": "I will",
            "you'll": "you will", 
            "he'll": "he will",
            "she'll": "she will",
            "we'll": "we will",
            "they'll": "they will",
            "it'll": "it will",
        }
    
    def _load_problematic_patterns(self) -> List[Tuple[str, str, str]]:
        """Load patterns for problematic contractions"""
        return [
            # Pattern, Replacement, Description
            (r"\bI'm\b", "I am", "Fix I'm pronunciation"),
            (r"\bI'll\b", "I will", "Fix I'll pronunciation"),
            (r"\bI'd\b", "I would", "Fix I'd pronunciation"),
            (r"\bI've\b", "I have", "Fix I've pronunciation"),
            
            # You contractions
            (r"\byou're\b", "you are", "Fix you're pronunciation"),
            (r"\byou'll\b", "you will", "Fix you'll pronunciation"),
            (r"\byou'd\b", "you would", "Fix you'd pronunciation"),
            (r"\byou've\b", "you have", "Fix you've pronunciation"),
            
            # Third person contractions
            (r"\bhe's\b", "he is", "Fix he's pronunciation"),
            (r"\bshe's\b", "she is", "Fix she's pronunciation"),
            (r"\bit's\b", "it is", "Fix it's pronunciation"),
            (r"\bhe'll\b", "he will", "Fix he'll pronunciation"),
            (r"\bshe'll\b", "she will", "Fix she'll pronunciation"),
            (r"\bit'll\b", "it will", "Fix it'll pronunciation"),
            
            # Plural contractions
            (r"\bwe're\b", "we are", "Fix we're pronunciation"),
            (r"\bthey're\b", "they are", "Fix they're pronunciation"),
            (r"\bwe'll\b", "we will", "Fix we'll pronunciation"),
            (r"\bthey'll\b", "they will", "Fix they'll pronunciation"),
            (r"\bwe'd\b", "we would", "Fix we'd pronunciation"),
            (r"\bthey'd\b", "they would", "Fix they'd pronunciation"),
            (r"\bwe've\b", "we have", "Fix we've pronunciation"),
            (r"\bthey've\b", "they have", "Fix they've pronunciation"),
            
            # Modal contractions
            (r"\bwon't\b", "will not", "Fix won't pronunciation"),
            (r"\bcan't\b", "cannot", "Fix can't pronunciation"),
            (r"\bcouldn't\b", "could not", "Fix couldn't pronunciation"),
            (r"\bshouldn't\b", "should not", "Fix shouldn't pronunciation"),
            (r"\bwouldn't\b", "would not", "Fix wouldn't pronunciation"),
            (r"\bmustn't\b", "must not", "Fix mustn't pronunciation"),
            (r"\bneedn't\b", "need not", "Fix needn't pronunciation"),
        ]
    
    def fix_contraction_pronunciation(self, text: str, mode: str = "expand") -> str:
        """
        Fix contraction pronunciation issues
        
        Args:
            text: Input text with contractions
            mode: "expand" (full expansion) or "phonetic" (phonetic spelling)
        """
        logger.debug(f"Fixing contraction pronunciation in {mode} mode: {text[:100]}...")
        
        original_text = text
        
        if mode == "expand":
            text = self._expand_problematic_contractions(text)
        elif mode == "phonetic":
            text = self._apply_phonetic_contractions(text)
        else:
            # Default: expand problematic ones, keep natural ones
            text = self._hybrid_contraction_processing(text)
        
        if text != original_text:
            logger.debug(f"Contraction fixes applied: '{original_text}' → '{text}'")
        
        return text
    
    def _expand_problematic_contractions(self, text: str) -> str:
        """Expand contractions that cause pronunciation issues"""
        for pattern, replacement, description in self.problematic_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                old_text = text
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                if text != old_text:
                    logger.debug(f"Applied {description}")
        
        return text
    
    def _apply_phonetic_contractions(self, text: str) -> str:
        """Apply phonetic spelling for contractions"""
        for contraction, phonetic in self.phonetic_contractions.items():
            pattern = r'\b' + re.escape(contraction) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, phonetic, text, flags=re.IGNORECASE)
                logger.debug(f"Applied phonetic fix: {contraction} → {phonetic}")
        
        return text
    
    def _hybrid_contraction_processing(self, text: str) -> str:
        """Hybrid approach: expand problematic, keep natural"""
        # Expand only the most problematic contractions
        problematic_contractions = [
            (r"\bI'm\b", "I am"),
            (r"\bI'll\b", "I will"), 
            (r"\bI'd\b", "I would"),
            (r"\byou'll\b", "you will"),
            (r"\bhe'll\b", "he will"),
            (r"\bshe'll\b", "she will"),
            (r"\bit'll\b", "it will"),
            (r"\bwe'll\b", "we will"),
            (r"\bthey'll\b", "they will"),
            (r"\bwon't\b", "will not"),
        ]
        
        for pattern, replacement in problematic_contractions:
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                logger.debug(f"Expanded problematic contraction: {pattern} → {replacement}")
        
        # Keep natural contractions as-is
        natural_contractions = [
            "don't", "doesn't", "didn't", "isn't", "aren't", 
            "wasn't", "weren't", "hasn't", "haven't", "hadn't",
            "can't", "couldn't", "shouldn't", "wouldn't"
        ]
        
        # These stay unchanged for natural speech
        
        return text
    
    def analyze_contraction_issues(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for contraction pronunciation issues"""
        issues = {
            'problematic_contractions': [],
            'natural_contractions': [],
            'potential_fixes': [],
            'apostrophe_issues': []
        }
        
        # Find all contractions
        contraction_pattern = r"\b\w+'\w+\b"
        contractions = re.findall(contraction_pattern, text)
        
        for contraction in contractions:
            if contraction.lower() in [p[0].replace(r'\b', '').replace(r'\b', '') for p, _, _ in self.problematic_patterns]:
                issues['problematic_contractions'].append(contraction)
            else:
                issues['natural_contractions'].append(contraction)
        
        # Check for potential fixes
        for contraction, fix in self.contraction_fixes.items():
            if contraction.lower() in text.lower():
                issues['potential_fixes'].append(f"{contraction} → {fix}")
        
        # Check for apostrophe issues
        apostrophe_issues = re.findall(r"\w+&#x27;\w+|\w+&apos;\w+", text)
        if apostrophe_issues:
            issues['apostrophe_issues'] = apostrophe_issues
        
        return issues
    
    def normalize_apostrophes(self, text: str) -> str:
        """Normalize apostrophes to prevent HTML entity pronunciation"""
        # Replace HTML entities
        text = re.sub(r"&#x27;", "'", text)
        text = re.sub(r"&#39;", "'", text) 
        text = re.sub(r"&apos;", "'", text)
        
        # Replace various apostrophe types
        apostrophe_variants = ["'", "'", "`", "´", "ʼ", "ʻ", "′"]
        for variant in apostrophe_variants:
            text = text.replace(variant, "'")
        
        return text

# Global instance for easy access
contraction_pronunciation_fix = ContractionPronunciationFix()
