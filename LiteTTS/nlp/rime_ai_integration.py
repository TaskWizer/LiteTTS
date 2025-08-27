#!/usr/bin/env python3
"""
RIME AI Research Integration Module
Implements advanced phonetic processing based on RIME AI research findings
"""

import logging
import re
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PhoneticAnalysis:
    """Result of phonetic analysis"""
    original_text: str
    processed_text: str
    phonetic_mappings: Dict[str, str]
    stress_patterns: List[Tuple[int, str]]
    confidence_score: float
    processing_notes: List[str]

class RIMEAIIntegration:
    """Advanced phonetic processing based on RIME AI research"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        
        # RIME AI phonetic alphabet with enhanced mappings
        self.rime_phonetic_alphabet = self._initialize_rime_alphabet()
        
        # Stress pattern recognition
        self.stress_patterns = self._initialize_stress_patterns()
        
        # Phoneme similarity mappings (inspired by RIME AI multi-task learning)
        self.phoneme_similarities = self._initialize_phoneme_similarities()
        
        # Context-aware pronunciation rules
        self.context_rules = self._initialize_context_rules()
        
        logger.info("RIME AI integration initialized with enhanced phonetic processing")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load RIME AI configuration"""
        default_config = {
            "enable_stress_detection": True,
            "enable_phoneme_similarity": True,
            "enable_context_awareness": True,
            "confidence_threshold": 0.8,
            "max_phonetic_length": 50,
            "stress_marker_style": "numeric",  # "numeric" or "ipa"
            "phonetic_notation_style": "rime",  # "rime", "ipa", or "hybrid"
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load RIME AI config: {e}")
        
        return default_config
    
    def _initialize_rime_alphabet(self) -> Dict[str, str]:
        """Initialize RIME AI-style phonetic alphabet"""
        return {
            # Enhanced vowel mappings with RIME AI notation
            'ɪ': 'I', 'i': 'i', 'ɛ': 'E', 'æ': '@', 'ʌ': 'A', 'ə': 'x',
            'ɑ': 'a', 'ɔ': 'O', 'ʊ': 'U', 'u': 'u', 'ɝ': 'R', 'ɚ': 'R',
            
            # Diphthongs with RIME AI style
            'eɪ': 'e', 'aɪ': 'Y', 'ɔɪ': 'O', 'aʊ': 'W', 'oʊ': 'o',
            
            # Consonants with enhanced mapping
            'θ': 'T', 'ð': 'D', 'ʃ': 'S', 'ʒ': 'Z', 'ŋ': 'G',
            'tʃ': 'C', 'dʒ': 'J', 'p': 'p', 'b': 'b', 't': 't', 'd': 'd',
            'k': 'k', 'g': 'g', 'f': 'f', 'v': 'v', 's': 's', 'z': 'z',
            'h': 'h', 'm': 'm', 'n': 'n', 'j': 'y', 'w': 'w', 'r': 'r', 'l': 'l',
            
            # Stress and timing markers (RIME AI style)
            'ˈ': '1', 'ˌ': '2', '.': '0', 'ː': '', '̆': '',
            
            # Additional RIME AI phonetic symbols
            'x': 'h', 'ɣ': 'g', 'ɲ': 'n', 'ɭ': 'l', 'ɻ': 'r',
            'ɾ': 'r', 'ʔ': '', 'ʰ': 'h', 'ʷ': 'w', 'ʲ': 'y'
        }
    
    def _initialize_stress_patterns(self) -> Dict[str, List[str]]:
        """Initialize stress pattern recognition rules"""
        return {
            "primary_stress": ["1", "ˈ", "'"],
            "secondary_stress": ["2", "ˌ", ","],
            "unstressed": ["0", ".", ""],
            "long_vowel": ["ː", ":"],
            "short_vowel": ["̆", "˘"]
        }
    
    def _initialize_phoneme_similarities(self) -> Dict[str, List[str]]:
        """Initialize phoneme similarity mappings for error correction"""
        return {
            # Vowel similarities
            'i': ['ɪ', 'iː', 'e'],
            'ɪ': ['i', 'e', 'ɛ'],
            'e': ['ɛ', 'eɪ', 'i'],
            'ɛ': ['e', 'æ', 'ɪ'],
            'æ': ['ɛ', 'a', 'ʌ'],
            'a': ['æ', 'ɑ', 'ʌ'],
            'ɑ': ['a', 'ɔ', 'ʌ'],
            'ɔ': ['ɑ', 'o', 'ʊ'],
            'o': ['ɔ', 'oʊ', 'ʊ'],
            'ʊ': ['o', 'u', 'ɔ'],
            'u': ['ʊ', 'uː', 'o'],
            'ʌ': ['a', 'ɑ', 'ə'],
            'ə': ['ʌ', 'ɪ', 'ɛ'],
            
            # Consonant similarities
            'p': ['b', 'f', 'pʰ'],
            'b': ['p', 'v', 'm'],
            't': ['d', 'θ', 'tʰ'],
            'd': ['t', 'ð', 'n'],
            'k': ['g', 'x', 'kʰ'],
            'g': ['k', 'ɣ', 'ŋ'],
            'f': ['v', 'p', 'θ'],
            'v': ['f', 'b', 'ð'],
            's': ['z', 'ʃ', 'θ'],
            'z': ['s', 'ʒ', 'ð'],
            'ʃ': ['ʒ', 's', 'tʃ'],
            'ʒ': ['ʃ', 'z', 'dʒ'],
            'θ': ['f', 's', 't'],
            'ð': ['v', 'z', 'd'],
            'tʃ': ['ʃ', 'dʒ', 't'],
            'dʒ': ['tʃ', 'ʒ', 'd'],
            'm': ['n', 'b', 'p'],
            'n': ['m', 'd', 't'],
            'ŋ': ['n', 'g', 'k'],
            'l': ['r', 'ɭ', 'ɾ'],
            'r': ['l', 'ɻ', 'ɾ'],
            'j': ['i', 'ʲ', 'ɪ'],
            'w': ['u', 'ʷ', 'ʊ'],
            'h': ['x', 'ʰ', 'ʔ']
        }
    
    def _initialize_context_rules(self) -> Dict[str, Dict[str, str]]:
        """Initialize context-aware pronunciation rules"""
        return {
            "word_initial": {
                "kn": "n",  # knee, know
                "gn": "n",  # gnome, gnu
                "wr": "r",  # write, wrong
                "ps": "s",  # psychology, psalm
                "pt": "t",  # pterodactyl, ptarmigan
            },
            "word_final": {
                "mb": "m",  # lamb, thumb
                "bt": "t",  # debt, doubt
                "mn": "m",  # autumn, column
                "gn": "n",  # sign, design
                "st": "s",  # castle, listen (in some contexts)
            },
            "vowel_clusters": {
                "ough": ["ʌf", "oʊ", "ɔf", "uː", "ɑf"],  # tough, though, cough, through, trough
                "augh": ["ɔf", "æf"],  # laugh, caught
                "eigh": ["eɪ", "aɪ"],  # eight, height
                "tion": ["ʃən", "tʃən"],  # nation, question
                "sion": ["ʃən", "ʒən"],  # mission, vision
            },
            "stress_patterns": {
                "compound_words": "first_element",
                "prefixed_words": "root",
                "suffixed_words": "depends_on_suffix",
            }
        }
    
    def process_text_with_rime_ai(self, text: str) -> PhoneticAnalysis:
        """Process text using RIME AI-inspired techniques"""
        logger.debug(f"Processing text with RIME AI: {text[:100]}...")
        
        original_text = text
        processing_notes = []
        phonetic_mappings = {}
        stress_patterns = []
        
        # Step 1: Detect and process RIME AI notation
        text, rime_mappings = self._process_rime_notation(text)
        phonetic_mappings.update(rime_mappings)
        if rime_mappings:
            processing_notes.append("RIME AI notation detected and processed")
        
        # Step 2: Apply context-aware pronunciation rules
        text, context_mappings = self._apply_context_rules(text)
        phonetic_mappings.update(context_mappings)
        if context_mappings:
            processing_notes.append("Context-aware rules applied")
        
        # Step 3: Detect stress patterns
        stress_patterns = self._detect_stress_patterns(text)
        if stress_patterns:
            processing_notes.append("Stress patterns detected")
        
        # Step 4: Apply phoneme similarity corrections
        text, similarity_corrections = self._apply_phoneme_similarities(text)
        if similarity_corrections:
            phonetic_mappings.update(similarity_corrections)
            processing_notes.append("Phoneme similarity corrections applied")
        
        # Step 5: Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            original_text, text, phonetic_mappings, stress_patterns
        )
        
        return PhoneticAnalysis(
            original_text=original_text,
            processed_text=text,
            phonetic_mappings=phonetic_mappings,
            stress_patterns=stress_patterns,
            confidence_score=confidence_score,
            processing_notes=processing_notes
        )
    
    def _process_rime_notation(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Process RIME AI-style phonetic notation"""
        mappings = {}
        
        # Pattern for RIME AI notation: {phonetic_string}
        pattern = re.compile(r'\{([^}]+)\}')
        
        def replace_rime_notation(match):
            phonetic = match.group(1)
            original = match.group(0)
            readable = self._convert_rime_to_readable(phonetic)
            mappings[original] = readable
            return readable
        
        processed_text = pattern.sub(replace_rime_notation, text)
        return processed_text, mappings
    
    def _convert_rime_to_readable(self, phonetic: str) -> str:
        """Convert RIME AI phonetic notation to readable text"""
        result = []
        i = 0
        
        while i < len(phonetic):
            # Handle stress markers (numbers)
            if phonetic[i].isdigit():
                stress_level = phonetic[i]
                if stress_level == '1' and self.config["stress_marker_style"] == "readable":
                    result.append("'")  # Primary stress marker
                elif stress_level == '2' and self.config["stress_marker_style"] == "readable":
                    result.append(",")  # Secondary stress marker
                # Skip stress markers in phonetic output
                i += 1
                continue
            
            # Handle multi-character phonemes
            if i < len(phonetic) - 1:
                two_char = phonetic[i:i+2]
                if two_char in self.rime_phonetic_alphabet:
                    result.append(self.rime_phonetic_alphabet[two_char])
                    i += 2
                    continue
            
            # Handle single character phonemes
            char = phonetic[i]
            if char in self.rime_phonetic_alphabet:
                result.append(self.rime_phonetic_alphabet[char])
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    def _apply_context_rules(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Apply context-aware pronunciation rules"""
        mappings = {}
        words = text.split()
        processed_words = []
        
        for word in words:
            original_word = word
            
            # Apply word-initial rules
            for pattern, replacement in self.context_rules["word_initial"].items():
                if word.lower().startswith(pattern):
                    new_word = replacement + word[len(pattern):]
                    if new_word != word:
                        mappings[f"initial_{pattern}"] = f"{pattern} → {replacement}"
                        word = new_word
                    break
            
            # Apply word-final rules
            for pattern, replacement in self.context_rules["word_final"].items():
                if word.lower().endswith(pattern):
                    new_word = word[:-len(pattern)] + replacement
                    if new_word != word:
                        mappings[f"final_{pattern}"] = f"{pattern} → {replacement}"
                        word = new_word
                    break
            
            # Apply vowel cluster rules
            for cluster, pronunciations in self.context_rules["vowel_clusters"].items():
                if cluster in word.lower():
                    # Use first pronunciation as default
                    pronunciation = pronunciations[0] if pronunciations else cluster
                    new_word = word.lower().replace(cluster, pronunciation)
                    if new_word != word.lower():
                        mappings[f"cluster_{cluster}"] = f"{cluster} → {pronunciation}"
                        word = new_word
            
            processed_words.append(word)
        
        return ' '.join(processed_words), mappings
    
    def _detect_stress_patterns(self, text: str) -> List[Tuple[int, str]]:
        """Detect stress patterns in text"""
        stress_patterns = []
        
        # Simple stress detection based on syllable patterns
        words = text.split()
        
        for word_idx, word in enumerate(words):
            # Count syllables (simple vowel counting)
            vowels = 'aeiouAEIOU'
            syllable_count = sum(1 for char in word if char in vowels)
            
            if syllable_count > 1:
                # Apply basic stress rules
                if len(word) > 6:  # Longer words often have secondary stress
                    stress_patterns.append((word_idx, "primary_secondary"))
                elif word.endswith(('tion', 'sion', 'ment', 'ness')):
                    stress_patterns.append((word_idx, "penultimate"))
                else:
                    stress_patterns.append((word_idx, "initial"))
        
        return stress_patterns
    
    def _apply_phoneme_similarities(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Apply phoneme similarity corrections"""
        # This is a placeholder for more advanced phoneme similarity processing
        # In a full implementation, this would use machine learning models
        # to detect and correct phoneme confusions
        
        corrections = {}
        
        # Simple example: common mispronunciations
        common_fixes = {
            "nucular": "nuclear",
            "expresso": "espresso", 
            "supposably": "supposedly",
            "irregardless": "regardless",
            "pacifically": "specifically"
        }
        
        processed_text = text
        for wrong, correct in common_fixes.items():
            if wrong in processed_text.lower():
                processed_text = re.sub(re.escape(wrong), correct, processed_text, flags=re.IGNORECASE)
                corrections[wrong] = correct
        
        return processed_text, corrections
    
    def _calculate_confidence_score(self, original: str, processed: str, 
                                  mappings: Dict[str, str], 
                                  stress_patterns: List[Tuple[int, str]]) -> float:
        """Calculate confidence score for phonetic processing"""
        base_score = 0.8
        
        # Increase confidence for successful mappings
        if mappings:
            base_score += min(0.15, len(mappings) * 0.03)
        
        # Increase confidence for detected stress patterns
        if stress_patterns:
            base_score += min(0.1, len(stress_patterns) * 0.02)
        
        # Decrease confidence for very long texts (harder to process accurately)
        if len(original) > 200:
            base_score -= 0.1
        
        # Ensure score is within valid range
        return max(0.0, min(1.0, base_score))
    
    def get_phonetic_analysis_summary(self, analysis: PhoneticAnalysis) -> str:
        """Generate a human-readable summary of phonetic analysis"""
        summary = f"RIME AI Phonetic Analysis Summary:\n"
        summary += f"Original: {analysis.original_text[:100]}...\n"
        summary += f"Processed: {analysis.processed_text[:100]}...\n"
        summary += f"Confidence: {analysis.confidence_score:.2f}\n"
        summary += f"Mappings Applied: {len(analysis.phonetic_mappings)}\n"
        summary += f"Stress Patterns: {len(analysis.stress_patterns)}\n"
        summary += f"Processing Notes: {', '.join(analysis.processing_notes)}\n"
        
        return summary

# Global instance for easy access
rime_ai_processor = RIMEAIIntegration()
