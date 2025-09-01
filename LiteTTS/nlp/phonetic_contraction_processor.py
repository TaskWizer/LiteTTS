#!/usr/bin/env python3
"""
Phonetic Contraction Processor
Handles contraction pronunciation issues with proper phonetic mapping
Fixes issues like wasn't→wAHz-uhnt, I'll→ill, you'll→yaw-wl, etc.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContractionFix:
    """Represents a contraction pronunciation fix"""
    original: str
    expanded: str
    phonetic: str
    context_sensitive: bool = False
    priority: int = 1  # Higher priority = processed first

class PhoneticContractionProcessor:
    """Advanced contraction processor with phonetic awareness"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.contraction_fixes = self._load_contraction_fixes()
        self.phonetic_mappings = self._load_phonetic_mappings()
        self.context_patterns = self._load_context_patterns()

        # Compile regex patterns for efficiency
        self._compile_patterns()

    def _should_expand_contractions(self) -> bool:
        """Check if contractions should be expanded based on config"""
        # Check the main expand_contractions setting
        expand_contractions = self.config.get('text_processing', {}).get('expand_contractions', False)

        # If expand_contractions is explicitly False, don't expand
        if expand_contractions is False:
            logger.debug("Contraction expansion disabled in config - preserving contractions")
            return False

        return True
    
    def _load_contraction_fixes(self) -> Dict[str, ContractionFix]:
        """Load comprehensive contraction fixes with phonetic mappings"""
        return {
            # Critical pronunciation fixes from user feedback
            "wasn't": ContractionFix(
                original="wasn't",
                expanded="was not",
                phonetic="wʌz nɑt",  # IPA: /wʌz nɑt/
                priority=10
            ),
            "weren't": ContractionFix(
                original="weren't", 
                expanded="were not",
                phonetic="wɜr nɑt",
                priority=10
            ),
            "isn't": ContractionFix(
                original="isn't",
                expanded="is not", 
                phonetic="ɪz nɑt",
                priority=10
            ),
            "aren't": ContractionFix(
                original="aren't",
                expanded="are not",
                phonetic="ɑr nɑt", 
                priority=10
            ),
            
            # Problematic 'll contractions
            "i'll": ContractionFix(
                original="i'll",
                expanded="I will",
                phonetic="aɪ wɪl",  # Not "ill"
                priority=10
            ),
            "you'll": ContractionFix(
                original="you'll", 
                expanded="you will",
                phonetic="ju wɪl",  # Not "yaw-wl"
                priority=10
            ),
            "he'll": ContractionFix(
                original="he'll",
                expanded="he will",
                phonetic="hi wɪl",
                priority=10
            ),
            "she'll": ContractionFix(
                original="she'll",
                expanded="she will", 
                phonetic="ʃi wɪl",
                priority=10
            ),
            "it'll": ContractionFix(
                original="it'll",
                expanded="it will",
                phonetic="ɪt wɪl",
                priority=10
            ),
            "we'll": ContractionFix(
                original="we'll",
                expanded="we will",
                phonetic="wi wɪl",
                priority=10
            ),
            "they'll": ContractionFix(
                original="they'll",
                expanded="they will",
                phonetic="ðeɪ wɪl",
                priority=10
            ),
            
            # Problematic 'd contractions
            "i'd": ContractionFix(
                original="i'd",
                expanded="I would",  # Context: usually "would", sometimes "had"
                phonetic="aɪ wʊd",  # Not "I-D"
                priority=10,
                context_sensitive=True
            ),
            "you'd": ContractionFix(
                original="you'd",
                expanded="you would",
                phonetic="ju wʊd",
                priority=10,
                context_sensitive=True
            ),
            "he'd": ContractionFix(
                original="he'd", 
                expanded="he would",
                phonetic="hi wʊd",
                priority=10,
                context_sensitive=True
            ),
            "she'd": ContractionFix(
                original="she'd",
                expanded="she would",
                phonetic="ʃi wʊd", 
                priority=10,
                context_sensitive=True
            ),
            
            # Problematic 'm contractions
            "i'm": ContractionFix(
                original="i'm",
                expanded="I am",
                phonetic="aɪ æm",  # Not "im"
                priority=10
            ),
            
            # Problematic 's contractions (context-sensitive)
            "that's": ContractionFix(
                original="that's",
                expanded="that is",  # Context: usually "is", sometimes "has"
                phonetic="ðæt ɪz",  # Not "hit that"
                priority=10,
                context_sensitive=True
            ),
            "what's": ContractionFix(
                original="what's",
                expanded="what is",
                phonetic="wʌt ɪz",
                priority=10,
                context_sensitive=True
            ),
            "it's": ContractionFix(
                original="it's",
                expanded="it is",
                phonetic="ɪt ɪz",
                priority=10,
                context_sensitive=True
            ),
            "there's": ContractionFix(
                original="there's",
                expanded="there is",
                phonetic="ðɛr ɪz",
                priority=10,
                context_sensitive=True
            ),
            
            # Additional common contractions
            "don't": ContractionFix(
                original="don't",
                expanded="do not",
                phonetic="du nɑt",
                priority=5
            ),
            "won't": ContractionFix(
                original="won't",
                expanded="will not",
                phonetic="wɪl nɑt",
                priority=5
            ),
            "can't": ContractionFix(
                original="can't",
                expanded="cannot",
                phonetic="kænɑt",
                priority=5
            ),
            "couldn't": ContractionFix(
                original="couldn't",
                expanded="could not",
                phonetic="kʊd nɑt",
                priority=5
            ),
            "shouldn't": ContractionFix(
                original="shouldn't",
                expanded="should not",
                phonetic="ʃʊd nɑt",
                priority=5
            ),
            "wouldn't": ContractionFix(
                original="wouldn't",
                expanded="would not",
                phonetic="wʊd nɑt",
                priority=5
            ),

            # Missing contractions from test failures
            "hasn't": ContractionFix(
                original="hasn't",
                expanded="has not",
                phonetic="hæz nɑt",
                priority=5
            ),
            "haven't": ContractionFix(
                original="haven't",
                expanded="have not",
                phonetic="hæv nɑt",
                priority=5
            ),
            "hadn't": ContractionFix(
                original="hadn't",
                expanded="had not",
                phonetic="hæd nɑt",
                priority=5
            ),
            "doesn't": ContractionFix(
                original="doesn't",
                expanded="does not",
                phonetic="dʌz nɑt",
                priority=5
            ),
            "didn't": ContractionFix(
                original="didn't",
                expanded="did not",
                phonetic="dɪd nɑt",
                priority=5
            ),
            "that'll": ContractionFix(
                original="that'll",
                expanded="that will",
                phonetic="ðæt wɪl",
                priority=5
            ),
            "we'd": ContractionFix(
                original="we'd",
                expanded="we would",
                phonetic="wi wʊd",
                priority=10,
                context_sensitive=True
            ),
            "they'd": ContractionFix(
                original="they'd",
                expanded="they would",
                phonetic="ðeɪ wʊd",
                priority=10,
                context_sensitive=True
            ),
            "he's": ContractionFix(
                original="he's",
                expanded="he is",
                phonetic="hi ɪz",
                priority=10,
                context_sensitive=True
            ),
            "she's": ContractionFix(
                original="she's",
                expanded="she is",
                phonetic="ʃi ɪz",
                priority=10,
                context_sensitive=True
            ),
            "we're": ContractionFix(
                original="we're",
                expanded="we are",
                phonetic="wi ɑr",
                priority=5
            ),
            "they're": ContractionFix(
                original="they're",
                expanded="they are",
                phonetic="ðeɪ ɑr",
                priority=5
            ),
            "you're": ContractionFix(
                original="you're",
                expanded="you are",
                phonetic="ju ɑr",
                priority=5
            ),
        }
    
    def _load_phonetic_mappings(self) -> Dict[str, str]:
        """Load IPA to readable phonetic mappings"""
        return {
            # Vowels
            'ɪ': 'ih', 'i': 'ee', 'ɛ': 'eh', 'æ': 'ae', 'ɑ': 'ah', 'ɔ': 'aw',
            'ʊ': 'uh', 'u': 'oo', 'ʌ': 'uh', 'ə': 'uh', 'ɜ': 'er', 'aɪ': 'eye',
            'aʊ': 'ow', 'ɔɪ': 'oy', 'eɪ': 'ay', 'oʊ': 'oh',
            
            # Consonants  
            'p': 'p', 'b': 'b', 't': 't', 'd': 'd', 'k': 'k', 'g': 'g',
            'f': 'f', 'v': 'v', 'θ': 'th', 'ð': 'th', 's': 's', 'z': 'z',
            'ʃ': 'sh', 'ʒ': 'zh', 'h': 'h', 'm': 'm', 'n': 'n', 'ŋ': 'ng',
            'l': 'l', 'r': 'r', 'w': 'w', 'j': 'y',
            
            # Affricates
            'tʃ': 'ch', 'dʒ': 'j'
        }
    
    def _load_context_patterns(self) -> Dict[str, List[str]]:
        """Load context patterns for context-sensitive contractions"""
        return {
            # Patterns that suggest 'd = "had" vs "would"
            'had_context': [
                r'\b\w+\'d\s+(been|done|seen|gone|come|taken|given|written|spoken)',
                r'\b\w+\'d\s+(already|just|never|ever|once|twice)',
                r'\b\w+\'d\s+(not|n\'t)',
            ],
            
            # Patterns that suggest 's = "has" vs "is"  
            'has_context': [
                r'\b\w+\'s\s+(been|done|seen|gone|come|taken|given|written|spoken)',
                r'\b\w+\'s\s+(already|just|never|ever|once|twice)',
                r'\b\w+\'s\s+(not|n\'t)',
            ]
        }
    
    def _compile_patterns(self):
        """Compile regex patterns for efficiency"""
        # Create pattern for all contractions (case-insensitive) with capturing group
        contraction_words = '|'.join(re.escape(word) for word in self.contraction_fixes.keys())
        self.contraction_pattern = re.compile(rf'\b({contraction_words})\b', re.IGNORECASE)
        
        # Compile context patterns
        self.compiled_context_patterns = {}
        for context_type, patterns in self.context_patterns.items():
            self.compiled_context_patterns[context_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def process_contractions(self, text: str, mode: str = "phonetic_expansion") -> str:
        """
        Process contractions with phonetic awareness

        Args:
            text: Input text with contractions
            mode: "phonetic_expansion" (default), "simple_expansion", "phonetic_only"
        """
        logger.debug(f"Processing contractions in {mode} mode: {text[:100]}...")

        # Check if contraction expansion is disabled in config
        if not self._should_expand_contractions():
            logger.debug("Contraction expansion disabled - returning original text")
            return text

        if mode == "phonetic_expansion":
            return self._phonetic_expansion(text)
        elif mode == "simple_expansion":
            return self._simple_expansion(text)
        elif mode == "phonetic_only":
            return self._phonetic_only(text)
        else:
            logger.warning(f"Unknown mode {mode}, using phonetic_expansion")
            return self._phonetic_expansion(text)
    
    def _phonetic_expansion(self, text: str) -> str:
        """Expand contractions with phonetic guidance"""
        # Sort by priority (higher first) to handle overlapping patterns
        sorted_fixes = sorted(self.contraction_fixes.items(),
                            key=lambda x: x[1].priority, reverse=True)

        # Process each contraction type
        for contraction, fix in sorted_fixes:
            pattern = re.compile(rf'\b({re.escape(contraction)})\b', re.IGNORECASE)

            # Create a closure that captures the current contraction and fix
            def make_replacer(current_contraction, current_fix):
                def replace_contraction(match):
                    matched_contraction = match.group(1).lower()

                    # Handle context-sensitive contractions
                    if current_fix.context_sensitive:
                        expanded = self._resolve_context_sensitive(match.group(0), text, current_fix)
                    else:
                        expanded = current_fix.expanded

                    # Preserve original case
                    original_text = match.group(1)
                    if original_text.isupper():
                        # All uppercase
                        expanded = expanded.upper()
                    elif original_text[0].isupper():
                        # Title case
                        expanded = expanded[0].upper() + expanded[1:]

                    logger.debug(f"Expanded contraction: {match.group(0)} → {expanded}")
                    return expanded
                return replace_contraction

            replacer = make_replacer(contraction, fix)
            text = pattern.sub(replacer, text)

        return text
    
    def _simple_expansion(self, text: str) -> str:
        """Simple contraction expansion without phonetic processing"""
        def replace_contraction(match):
            contraction = match.group(1).lower()

            if contraction not in self.contraction_fixes:
                return match.group(0)

            fix = self.contraction_fixes[contraction]
            expanded = fix.expanded

            # Preserve original case
            original_text = match.group(1)
            if original_text.isupper():
                # All uppercase
                expanded = expanded.upper()
            elif original_text[0].isupper():
                # Title case
                expanded = expanded[0].upper() + expanded[1:]

            return expanded

        return self.contraction_pattern.sub(replace_contraction, text)
    
    def _phonetic_only(self, text: str) -> str:
        """Apply phonetic representations without expansion"""
        def replace_contraction(match):
            contraction = match.group(1).lower()

            if contraction not in self.contraction_fixes:
                return match.group(0)

            fix = self.contraction_fixes[contraction]

            # Convert IPA to readable phonetics
            phonetic = fix.phonetic
            for ipa, readable in self.phonetic_mappings.items():
                phonetic = phonetic.replace(ipa, readable)

            return phonetic

        return self.contraction_pattern.sub(replace_contraction, text)
    
    def _resolve_context_sensitive(self, contraction: str, full_text: str, fix: ContractionFix) -> str:
        """Resolve context-sensitive contractions like 'd and 's"""
        contraction_lower = contraction.lower()
        
        # Handle 'd contractions (had vs would)
        if contraction_lower.endswith("'d"):
            for pattern in self.compiled_context_patterns.get('had_context', []):
                if pattern.search(full_text):
                    # Context suggests "had"
                    base = contraction_lower[:-2]  # Remove 'd
                    return f"{base} had"
            
            # Default to "would"
            return fix.expanded
        
        # Handle 's contractions (has vs is)
        elif contraction_lower.endswith("'s"):
            for pattern in self.compiled_context_patterns.get('has_context', []):
                if pattern.search(full_text):
                    # Context suggests "has"
                    base = contraction_lower[:-2]  # Remove 's
                    return f"{base} has"
            
            # Default to "is"
            return fix.expanded
        
        return fix.expanded
    
    def analyze_contractions(self, text: str) -> Dict[str, any]:
        """Analyze text for contraction processing opportunities"""
        analysis = {
            'contractions_found': [],
            'problematic_contractions': [],
            'context_sensitive_contractions': [],
            'phonetic_issues': []
        }
        
        # Find all contractions
        matches = self.contraction_pattern.finditer(text)
        for match in matches:
            contraction = match.group(1).lower()
            analysis['contractions_found'].append(contraction)
            
            if contraction in self.contraction_fixes:
                fix = self.contraction_fixes[contraction]
                
                if fix.priority >= 10:
                    analysis['problematic_contractions'].append(contraction)
                
                if fix.context_sensitive:
                    analysis['context_sensitive_contractions'].append(contraction)
        
        return analysis
    
    def get_phonetic_representation(self, contraction: str) -> Optional[str]:
        """Get phonetic representation of a contraction"""
        contraction_lower = contraction.lower()
        
        if contraction_lower not in self.contraction_fixes:
            return None
        
        fix = self.contraction_fixes[contraction_lower]
        
        # Convert IPA to readable phonetics
        phonetic = fix.phonetic
        for ipa, readable in self.phonetic_mappings.items():
            phonetic = phonetic.replace(ipa, readable)
        
        return phonetic
