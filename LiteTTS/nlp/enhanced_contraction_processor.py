#!/usr/bin/env python3
"""
Enhanced contraction processor for natural TTS pronunciation
Addresses specific contraction pronunciation issues like I'll→ill, you'll→yaw-wl, I'd→I-D
"""

import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class EnhancedContractionProcessor:
    """Advanced contraction processing for natural TTS pronunciation"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.natural_contractions = self._load_natural_contractions()
        self.problematic_contractions = self._load_problematic_contractions()
        self.phonetic_contractions = self._load_phonetic_contractions()
        self.contraction_modes = {
            'natural': self._process_natural_mode,
            'phonetic': self._process_phonetic_mode,
            'expanded': self._process_expanded_mode,
            'hybrid': self._process_hybrid_mode
        }

        # Configuration
        self.mode = 'hybrid'  # Default to hybrid mode
        self.preserve_natural_speech = True

    def _should_expand_contractions(self) -> bool:
        """Check if contractions should be expanded based on config"""
        # Check the main expand_contractions setting
        expand_contractions = self.config.get('text_processing', {}).get('expand_contractions', False)

        # If expand_contractions is explicitly False, don't expand
        if expand_contractions is False:
            logger.debug("Contraction expansion disabled in config - preserving contractions")
            return False

        return True
        
    def _load_natural_contractions(self) -> Dict[str, str]:
        """Load contractions that should be kept in natural form"""
        return {
            # These contractions sound natural when pronounced as-is
            "don't": "don't",
            "won't": "won't", 
            "can't": "can't",
            "couldn't": "couldn't",
            "shouldn't": "shouldn't",
            "wouldn't": "wouldn't",
            "mustn't": "mustn't",
            "needn't": "needn't",
            "aren't": "aren't",
            "isn't": "isn't",
            "wasn't": "wasn't",
            "weren't": "weren't",
            "hasn't": "hasn't",
            "haven't": "haven't",
            "hadn't": "hadn't",
            "didn't": "didn't",
            "doesn't": "doesn't",
            # Natural sounding contractions
            "we're": "we're",
            "they're": "they're",
            "you're": "you're",
            "we've": "we've",
            "they've": "they've",
            "you've": "you've",
            "we'll": "we'll",
            "they'll": "they'll",
        }
    
    def _load_problematic_contractions(self) -> Dict[str, str]:
        """Load contractions that cause TTS pronunciation issues"""
        return {
            # These contractions cause specific pronunciation problems
            "I'll": "I will",  # Pronounced as "ill" instead of "I'll"
            "you'll": "you will",  # Pronounced as "yaw-wl" instead of "you'll"
            "I'd": "I would",  # Pronounced as "I-D" instead of "I'd"
            "he'll": "he will",  # Similar issues
            "she'll": "she will",  # Similar issues
            "it'll": "it will",  # Similar issues
            "that'll": "that will",  # Similar issues
            "who'll": "who will",  # Similar issues
            "what'll": "what will",  # Similar issues
            "where'll": "where will",  # Similar issues
            "when'll": "when will",  # Similar issues
            "how'll": "how will",  # Similar issues
            # Possessive contractions that get mispronounced
            "he'd": "he would",
            "she'd": "she would",
            "it'd": "it would",
            "we'd": "we would",
            "they'd": "they would",
            "you'd": "you would",
            "that'd": "that would",
            "who'd": "who would",
            "what'd": "what would",
            "where'd": "where would",
            "when'd": "when would",
            "how'd": "how would",
            # CRITICAL FIX: Negative contractions that cause pronunciation issues
            "wasn't": "was not",  # FIXED: was pronounced as "wawsnt", now "wAHz not"
            "isn't": "is not",    # Ensure proper pronunciation
            "aren't": "are not",  # Ensure proper pronunciation
            "weren't": "were not", # Ensure proper pronunciation
            "haven't": "have not", # Ensure proper pronunciation
            "hasn't": "has not",   # Ensure proper pronunciation
            "hadn't": "had not",   # Ensure proper pronunciation
            "don't": "do not",     # Ensure proper pronunciation
            "doesn't": "does not", # Ensure proper pronunciation
            "didn't": "did not",   # Ensure proper pronunciation
            "won't": "will not",   # Ensure proper pronunciation
            "wouldn't": "would not", # Ensure proper pronunciation
            "can't": "cannot",     # Ensure proper pronunciation
            "couldn't": "could not", # Ensure proper pronunciation
            "shouldn't": "should not", # Ensure proper pronunciation
        }
    
    def _load_phonetic_contractions(self) -> Dict[str, str]:
        """Load phonetic representations for natural-sounding contractions"""
        return {
            # Phonetic spellings that sound more natural
            "I'll": "I'll",  # Keep as-is but ensure proper pronunciation
            "you'll": "you'll",  # Keep as-is but ensure proper pronunciation  
            "I'd": "I'd",  # Keep as-is but ensure proper pronunciation
            "he'll": "he'll",
            "she'll": "she'll",
            "it'll": "it'll",
            "we'll": "we'll",
            "they'll": "they'll",
            "that'll": "that'll",
            # Alternative phonetic representations
            "I'll": "I-will",  # Hyphenated to preserve natural flow
            "you'll": "you-will",  # Hyphenated to preserve natural flow
            "I'd": "I-would",  # Hyphenated to preserve natural flow
        }
    
    def process_contractions(self, text: str, mode: Optional[str] = None) -> str:
        """Process contractions based on the specified mode"""
        if mode is None:
            mode = self.mode
            
        if mode not in self.contraction_modes:
            logger.warning(f"Unknown contraction mode: {mode}, using hybrid")
            mode = 'hybrid'
            
        logger.debug(f"Processing contractions in {mode} mode: {text[:100]}...")
        
        # First, normalize apostrophes to prevent HTML entity issues
        text = self._normalize_apostrophes(text)
        
        # Apply the selected processing mode
        processed_text = self.contraction_modes[mode](text)
        
        logger.debug(f"Contraction processing result: {processed_text[:100]}...")
        return processed_text
    
    def _normalize_apostrophes(self, text: str) -> str:
        """Normalize different apostrophe types to prevent pronunciation issues"""
        # Replace various apostrophe types with standard apostrophe
        apostrophe_variants = [
            "'", "'", "`", "´", "ʼ", "ʻ", "′"
        ]
        
        for variant in apostrophe_variants:
            text = text.replace(variant, "'")
            
        # Handle HTML entities that cause "x 27" pronunciation
        text = re.sub(r"&#x27;", "'", text)
        text = re.sub(r"&#39;", "'", text)
        text = re.sub(r"&apos;", "'", text)
        
        return text
    
    def _process_natural_mode(self, text: str) -> str:
        """Keep contractions in natural form"""
        # Just normalize apostrophes, keep contractions as-is
        return text
    
    def _process_phonetic_mode(self, text: str) -> str:
        """Use phonetic representations for better pronunciation"""
        for contraction, phonetic in self.phonetic_contractions.items():
            pattern = r'\b' + re.escape(contraction) + r'\b'
            text = re.sub(pattern, phonetic, text, flags=re.IGNORECASE)
        return text
    
    def _process_expanded_mode(self, text: str) -> str:
        """Expand all contractions to full forms"""
        # Combine all contraction dictionaries for full expansion
        all_contractions = {**self.natural_contractions, **self.problematic_contractions}
        
        # Convert natural contractions to expanded forms
        expanded_contractions = {}
        for contraction in self.natural_contractions:
            if contraction.endswith("n't"):
                base = contraction[:-3]
                expanded_contractions[contraction] = f"{base} not"
            elif contraction.endswith("'re"):
                base = contraction[:-3]
                expanded_contractions[contraction] = f"{base} are"
            elif contraction.endswith("'ve"):
                base = contraction[:-3]
                expanded_contractions[contraction] = f"{base} have"
            elif contraction.endswith("'ll"):
                base = contraction[:-3]
                expanded_contractions[contraction] = f"{base} will"
            # Add other patterns as needed
        
        # Apply expansions
        all_expansions = {**expanded_contractions, **self.problematic_contractions}
        
        for contraction, expansion in all_expansions.items():
            pattern = r'\b' + re.escape(contraction) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
            
        return text
    
    def _process_hybrid_mode(self, text: str) -> str:
        """Hybrid approach: expand problematic contractions, keep natural ones"""
        # Check if contraction expansion is disabled in config
        if not self._should_expand_contractions():
            # If expansion is disabled, just normalize apostrophes and return
            return self._normalize_apostrophes(text)

        # First, expand only the problematic contractions
        for contraction, expansion in self.problematic_contractions.items():
            pattern = r'\b' + re.escape(contraction) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)

        # Keep natural contractions as-is (they're already normalized)
        return text
    
    def get_contraction_info(self, text: str) -> Dict[str, List[str]]:
        """Analyze contractions in text and return information"""
        info = {
            'natural_contractions': [],
            'problematic_contractions': [],
            'unknown_contractions': []
        }
        
        # Find all contractions in text
        contraction_pattern = r"\b\w+'\w+\b"
        contractions = re.findall(contraction_pattern, text, re.IGNORECASE)
        
        for contraction in contractions:
            contraction_lower = contraction.lower()
            if contraction_lower in self.natural_contractions:
                info['natural_contractions'].append(contraction)
            elif contraction_lower in self.problematic_contractions:
                info['problematic_contractions'].append(contraction)
            else:
                info['unknown_contractions'].append(contraction)
        
        return info
    
    def set_mode(self, mode: str):
        """Set the contraction processing mode"""
        if mode in self.contraction_modes:
            self.mode = mode
            logger.info(f"Contraction processing mode set to: {mode}")
        else:
            logger.warning(f"Invalid mode: {mode}. Available modes: {list(self.contraction_modes.keys())}")
    
    def get_supported_modes(self) -> List[str]:
        """Get list of supported contraction processing modes"""
        return list(self.contraction_modes.keys())
