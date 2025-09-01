#!/usr/bin/env python3
"""
Advanced Phonetic Mapping System
Sophisticated phonetic mapping system with IPA support and context-aware pronunciation rules
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from pathlib import Path
import unicodedata

logger = logging.getLogger(__name__)

@dataclass
class PhoneticMapping:
    """Individual phonetic mapping entry"""
    grapheme: str          # Written form
    phoneme: str           # IPA phonetic representation
    context_before: str    # Context before the grapheme
    context_after: str     # Context after the grapheme
    language: str          # Language code (en, en-US, etc.)
    frequency: float       # Usage frequency (0.0-1.0)
    confidence: float      # Mapping confidence (0.0-1.0)
    
@dataclass
class PhoneticRule:
    """Context-aware phonetic rule"""
    pattern: str           # Regex pattern to match
    replacement: str       # IPA replacement
    context: str           # Context description
    priority: int          # Rule priority (higher = applied first)
    conditions: List[str]  # Additional conditions

class AdvancedPhoneticMapper:
    """Advanced phonetic mapping system with IPA support"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        
        # Core phonetic mappings
        self.ipa_mappings = self._initialize_ipa_mappings()
        self.context_rules = self._initialize_context_rules()
        self.homograph_rules = self._initialize_homograph_rules()
        
        # Language-specific mappings
        self.language_mappings = self._initialize_language_mappings()
        
        # Phoneme similarity mappings for error correction
        self.phoneme_similarities = self._initialize_phoneme_similarities()
        
        # Stress and prosodic patterns
        self.stress_patterns = self._initialize_stress_patterns()
        
        logger.info("Advanced phonetic mapping system initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load phonetic mapping configuration"""
        default_config = {
            "default_language": "en-US",
            "enable_context_rules": True,
            "enable_homograph_resolution": True,
            "enable_stress_prediction": True,
            "ipa_notation_style": "standard",  # standard, simplified, custom
            "phoneme_similarity_threshold": 0.8,
            "context_window_size": 3,
            "stress_prediction_method": "syllable_based"
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load phonetic config: {e}")
        
        return default_config
    
    def _initialize_ipa_mappings(self) -> Dict[str, PhoneticMapping]:
        """Initialize comprehensive IPA phonetic mappings"""
        mappings = {}
        
        # Vowel mappings (American English)
        vowel_mappings = [
            # Monophthongs
            ("a", "æ", "", "", "en-US", 0.9, 0.95),  # cat, bat
            ("e", "ɛ", "", "", "en-US", 0.8, 0.9),   # bed, red
            ("i", "ɪ", "", "", "en-US", 0.85, 0.9),  # bit, sit
            ("o", "ɑ", "", "", "en-US", 0.7, 0.85),  # hot, cot
            ("u", "ʌ", "", "", "en-US", 0.75, 0.85), # but, cut
            
            # Long vowels
            ("ee", "iː", "", "", "en-US", 0.9, 0.95), # see, tree
            ("oo", "uː", "", "", "en-US", 0.85, 0.9), # food, mood
            ("ar", "ɑr", "", "", "en-US", 0.9, 0.95), # car, far
            ("or", "ɔr", "", "", "en-US", 0.85, 0.9), # for, more
            ("er", "ɝ", "", "", "en-US", 0.9, 0.95),  # her, bird
            
            # Diphthongs
            ("ai", "eɪ", "", "", "en-US", 0.8, 0.9),  # rain, pain
            ("ay", "eɪ", "", "", "en-US", 0.85, 0.9), # day, say
            ("oi", "ɔɪ", "", "", "en-US", 0.9, 0.95), # boy, toy
            ("oy", "ɔɪ", "", "", "en-US", 0.9, 0.95), # joy, employ
            ("ou", "aʊ", "", "", "en-US", 0.8, 0.9),  # house, mouse
            ("ow", "aʊ", "", "", "en-US", 0.75, 0.85), # cow, how (context-dependent)
        ]
        
        for grapheme, phoneme, ctx_before, ctx_after, lang, freq, conf in vowel_mappings:
            mappings[grapheme] = PhoneticMapping(
                grapheme, phoneme, ctx_before, ctx_after, lang, freq, conf
            )
        
        # Consonant mappings
        consonant_mappings = [
            # Single consonants
            ("b", "b", "", "", "en-US", 0.95, 0.98),
            ("d", "d", "", "", "en-US", 0.95, 0.98),
            ("f", "f", "", "", "en-US", 0.95, 0.98),
            ("g", "g", "", "", "en-US", 0.9, 0.95),
            ("h", "h", "", "", "en-US", 0.9, 0.95),
            ("j", "dʒ", "", "", "en-US", 0.95, 0.98),
            ("k", "k", "", "", "en-US", 0.95, 0.98),
            ("l", "l", "", "", "en-US", 0.95, 0.98),
            ("m", "m", "", "", "en-US", 0.95, 0.98),
            ("n", "n", "", "", "en-US", 0.95, 0.98),
            ("p", "p", "", "", "en-US", 0.95, 0.98),
            ("r", "r", "", "", "en-US", 0.9, 0.95),
            ("s", "s", "", "", "en-US", 0.95, 0.98),
            ("t", "t", "", "", "en-US", 0.95, 0.98),
            ("v", "v", "", "", "en-US", 0.95, 0.98),
            ("w", "w", "", "", "en-US", 0.95, 0.98),
            ("y", "j", "", "", "en-US", 0.9, 0.95),
            ("z", "z", "", "", "en-US", 0.95, 0.98),
            
            # Digraphs and special combinations
            ("ch", "tʃ", "", "", "en-US", 0.95, 0.98),
            ("sh", "ʃ", "", "", "en-US", 0.95, 0.98),
            ("th", "θ", "", "", "en-US", 0.8, 0.85),  # thin (voiceless)
            ("th", "ð", "", "", "en-US", 0.8, 0.85),  # this (voiced) - context-dependent
            ("ng", "ŋ", "", "", "en-US", 0.95, 0.98),
            ("ph", "f", "", "", "en-US", 0.9, 0.95),
            ("gh", "f", "", "", "en-US", 0.7, 0.8),   # laugh, rough
            ("ck", "k", "", "", "en-US", 0.95, 0.98),
            ("qu", "kw", "", "", "en-US", 0.95, 0.98),
        ]
        
        for grapheme, phoneme, ctx_before, ctx_after, lang, freq, conf in consonant_mappings:
            mappings[f"cons_{grapheme}"] = PhoneticMapping(
                grapheme, phoneme, ctx_before, ctx_after, lang, freq, conf
            )
        
        return mappings
    
    def _initialize_context_rules(self) -> List[PhoneticRule]:
        """Initialize context-aware phonetic rules"""
        return [
            # Vowel context rules
            PhoneticRule(
                pattern=r"a(?=r)",
                replacement="ɑ",
                context="'a' before 'r'",
                priority=100,
                conditions=["not_in_unstressed_syllable"]
            ),
            PhoneticRule(
                pattern=r"e(?=r)",
                replacement="ɝ",
                context="'e' before 'r'",
                priority=100,
                conditions=[]
            ),
            PhoneticRule(
                pattern=r"i(?=r)",
                replacement="ɪr",
                context="'i' before 'r'",
                priority=100,
                conditions=[]
            ),
            
            # Consonant context rules
            PhoneticRule(
                pattern=r"c(?=[eiy])",
                replacement="s",
                context="'c' before front vowels",
                priority=90,
                conditions=[]
            ),
            PhoneticRule(
                pattern=r"c(?=[aou])",
                replacement="k",
                context="'c' before back vowels",
                priority=90,
                conditions=[]
            ),
            PhoneticRule(
                pattern=r"g(?=[eiy])",
                replacement="dʒ",
                context="'g' before front vowels (soft g)",
                priority=85,
                conditions=["not_germanic_origin"]
            ),
            
            # Silent letter rules
            PhoneticRule(
                pattern=r"(?<=\w)b$",
                replacement="",
                context="silent 'b' at word end",
                priority=95,
                conditions=["preceded_by_m"]
            ),
            PhoneticRule(
                pattern=r"k(?=n)",
                replacement="",
                context="silent 'k' before 'n'",
                priority=95,
                conditions=["word_initial"]
            ),
            PhoneticRule(
                pattern=r"w(?=r)",
                replacement="",
                context="silent 'w' before 'r'",
                priority=95,
                conditions=["word_initial"]
            ),
            
            # Stress-dependent rules
            PhoneticRule(
                pattern=r"a(?=\w*[aeiou]\w*$)",
                replacement="ə",
                context="'a' in unstressed syllable",
                priority=80,
                conditions=["unstressed_syllable"]
            ),
            PhoneticRule(
                pattern=r"e(?=\w*[aeiou]\w*$)",
                replacement="ə",
                context="'e' in unstressed syllable",
                priority=80,
                conditions=["unstressed_syllable"]
            ),
        ]
    
    def _initialize_homograph_rules(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Initialize homograph disambiguation rules"""
        return {
            # Word -> [(pronunciation1, context1, frequency1), ...]
            "read": [
                ("riːd", "present_tense", "0.6"),
                ("rɛd", "past_tense", "0.4")
            ],
            "lead": [
                ("liːd", "verb_or_metal", "0.7"),
                ("lɛd", "past_tense_of_lead", "0.3")
            ],
            "tear": [
                ("tɪr", "crying", "0.6"),
                ("tɛr", "rip_apart", "0.4")
            ],
            "wind": [
                ("wɪnd", "air_movement", "0.7"),
                ("waɪnd", "to_twist", "0.3")
            ],
            "bow": [
                ("boʊ", "archery_or_greeting", "0.6"),
                ("baʊ", "front_of_ship", "0.4")
            ],
            "close": [
                ("kloʊs", "near", "0.6"),
                ("kloʊz", "to_shut", "0.4")
            ],
            "live": [
                ("lɪv", "to_be_alive", "0.7"),
                ("laɪv", "not_recorded", "0.3")
            ],
            "object": [
                ("ˈɑbdʒɛkt", "noun", "0.6"),
                ("əbˈdʒɛkt", "verb", "0.4")
            ],
            "present": [
                ("ˈprɛzənt", "noun_or_adjective", "0.7"),
                ("prɪˈzɛnt", "verb", "0.3")
            ],
            "record": [
                ("ˈrɛkɔrd", "noun", "0.6"),
                ("rɪˈkɔrd", "verb", "0.4")
            ]
        }
    
    def _initialize_language_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize language-specific phonetic mappings"""
        return {
            "en-US": {
                # American English specific
                "r": "r",      # Rhotic
                "a": "æ",      # Flat 'a'
                "o": "ɑ",      # Open 'o'
            },
            "en-GB": {
                # British English specific
                "r": "",       # Non-rhotic (context-dependent)
                "a": "ɑː",     # Long 'a'
                "o": "ɒ",      # Rounded 'o'
            },
            "en-AU": {
                # Australian English specific
                "a": "æ",      # Similar to American
                "i": "ɪ",      # Centralized
                "o": "ɔ",      # Rounded
            }
        }
    
    def _initialize_phoneme_similarities(self) -> Dict[str, List[str]]:
        """Initialize phoneme similarity mappings for error correction"""
        return {
            # Vowel similarities
            "ɪ": ["i", "ɛ", "e"],
            "i": ["ɪ", "iː", "e"],
            "ɛ": ["e", "æ", "ɪ"],
            "æ": ["ɛ", "a", "ʌ"],
            "ʌ": ["ə", "a", "ɑ"],
            "ə": ["ʌ", "ɪ", "ɛ"],
            "ɑ": ["a", "ɔ", "ʌ"],
            "ɔ": ["o", "ɑ", "ʊ"],
            "ʊ": ["u", "o", "ɔ"],
            "u": ["ʊ", "uː", "o"],
            
            # Consonant similarities
            "p": ["b", "f"],
            "b": ["p", "v", "m"],
            "t": ["d", "θ"],
            "d": ["t", "ð", "n"],
            "k": ["g", "x"],
            "g": ["k", "ɣ"],
            "f": ["v", "p", "θ"],
            "v": ["f", "b", "ð"],
            "θ": ["f", "s", "t"],
            "ð": ["v", "z", "d"],
            "s": ["z", "ʃ", "θ"],
            "z": ["s", "ʒ", "ð"],
            "ʃ": ["ʒ", "s", "tʃ"],
            "ʒ": ["ʃ", "z", "dʒ"],
            "tʃ": ["ʃ", "dʒ", "t"],
            "dʒ": ["tʃ", "ʒ", "d"],
            "m": ["n", "b"],
            "n": ["m", "d", "ŋ"],
            "ŋ": ["n", "g"],
            "l": ["r", "ɭ"],
            "r": ["l", "ɻ"],
            "j": ["i", "ɪ"],
            "w": ["u", "ʊ"],
            "h": ["x", "ʔ"]
        }
    
    def _initialize_stress_patterns(self) -> Dict[str, List[str]]:
        """Initialize stress pattern rules"""
        return {
            "compound_words": ["first_element_primary"],
            "prefixed_words": ["root_primary", "prefix_secondary"],
            "suffixed_words": {
                "-tion": ["penultimate_primary"],
                "-sion": ["penultimate_primary"],
                "-ment": ["root_primary"],
                "-ness": ["root_primary"],
                "-able": ["root_primary"],
                "-ible": ["root_primary"],
                "-ful": ["root_primary"],
                "-less": ["root_primary"],
                "-ly": ["root_primary"],
                "-ing": ["root_primary"],
                "-ed": ["root_primary"]
            },
            "word_length": {
                "1_syllable": ["primary"],
                "2_syllables": ["first_primary"],
                "3_syllables": ["first_or_second_primary"],
                "4+_syllables": ["antepenultimate_or_penultimate_primary"]
            }
        }
    
    def map_to_ipa(self, text: str, language: str = "en-US") -> str:
        """Map text to IPA phonetic representation"""
        logger.debug(f"Mapping to IPA: {text[:50]}...")
        
        # Normalize text
        text = self._normalize_text(text)
        
        # Apply context rules
        if self.config["enable_context_rules"]:
            text = self._apply_context_rules(text)
        
        # Resolve homographs
        if self.config["enable_homograph_resolution"]:
            text = self._resolve_homographs(text)
        
        # Apply phonetic mappings
        ipa_text = self._apply_phonetic_mappings(text, language)
        
        # Add stress markers
        if self.config["enable_stress_prediction"]:
            ipa_text = self._add_stress_markers(ipa_text)
        
        logger.debug(f"IPA result: {ipa_text[:50]}...")
        return ipa_text
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for phonetic processing"""
        # Convert to lowercase
        text = text.lower()
        
        # Normalize Unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove non-alphabetic characters (keep spaces and hyphens)
        text = re.sub(r'[^a-z\s\-]', '', text)
        
        return text.strip()
    
    def _apply_context_rules(self, text: str) -> str:
        """Apply context-aware phonetic rules"""
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self.context_rules, key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            # Check conditions
            if self._check_rule_conditions(text, rule):
                text = re.sub(rule.pattern, rule.replacement, text)
        
        return text
    
    def _check_rule_conditions(self, text: str, rule: PhoneticRule) -> bool:
        """Check if rule conditions are met"""
        # Simplified condition checking
        for condition in rule.conditions:
            if condition == "word_initial" and not re.search(r'\b' + rule.pattern, text):
                return False
            elif condition == "word_final" and not re.search(rule.pattern + r'\b', text):
                return False
            # Add more condition checks as needed
        
        return True
    
    def _resolve_homographs(self, text: str) -> str:
        """Resolve homograph pronunciations based on context"""
        words = text.split()
        resolved_words = []
        
        for i, word in enumerate(words):
            if word in self.homograph_rules:
                # Simple context-based resolution (can be enhanced with ML)
                pronunciations = self.homograph_rules[word]
                
                # Default to most frequent pronunciation
                best_pronunciation = max(pronunciations, key=lambda x: float(x[2]))
                resolved_words.append(best_pronunciation[0])
            else:
                resolved_words.append(word)
        
        return ' '.join(resolved_words)
    
    def _apply_phonetic_mappings(self, text: str, language: str) -> str:
        """Apply phonetic mappings to convert text to IPA"""
        # This is a simplified implementation
        # In a full system, this would use more sophisticated algorithms
        
        result = text
        
        # Apply language-specific mappings
        if language in self.language_mappings:
            lang_mappings = self.language_mappings[language]
            for grapheme, phoneme in lang_mappings.items():
                result = result.replace(grapheme, phoneme)
        
        # Apply general IPA mappings
        for mapping_key, mapping in self.ipa_mappings.items():
            if mapping.language == language or mapping.language.startswith(language[:2]):
                result = result.replace(mapping.grapheme, mapping.phoneme)
        
        return result
    
    def _add_stress_markers(self, ipa_text: str) -> str:
        """Add stress markers to IPA text"""
        # Simplified stress prediction
        words = ipa_text.split()
        stressed_words = []
        
        for word in words:
            if len(word) > 1:  # Only add stress to multi-character words
                # Simple rule: primary stress on first syllable for most words
                stressed_word = "ˈ" + word
                stressed_words.append(stressed_word)
            else:
                stressed_words.append(word)
        
        return ' '.join(stressed_words)
    
    def get_phoneme_alternatives(self, phoneme: str) -> List[str]:
        """Get alternative phonemes for error correction"""
        return self.phoneme_similarities.get(phoneme, [])
    
    def validate_ipa_string(self, ipa_string: str) -> Tuple[bool, List[str]]:
        """Validate IPA string and return errors if any"""
        errors = []
        
        # Check for valid IPA characters
        valid_ipa_chars = set("abcdefghijklmnopqrstuvwxyzæɑɒɔəɛɪʊʌaeiouɜɝɞɘɵɤɯɨʉɶœøɪ̈ʏɐɶ̃ɑ̃ɔ̃ə̃ɛ̃ɪ̃ʊ̃ʌ̃pbtkgfvθðszʃʒhmnŋlrjwʔˈˌːˑ̆ʰʷʲ. ")
        
        for char in ipa_string:
            if char not in valid_ipa_chars:
                errors.append(f"Invalid IPA character: '{char}'")
        
        # Check stress marker placement
        if re.search(r'ˈˈ|ˌˌ', ipa_string):
            errors.append("Consecutive stress markers found")
        
        return len(errors) == 0, errors

# Global instance for easy access
advanced_phonetic_mapper = AdvancedPhoneticMapper()

def main():
    """Test the advanced phonetic mapping system"""
    print("Advanced Phonetic Mapping System Test")
    print("=" * 40)

    # Test cases
    test_cases = [
        "hello world",
        "the quick brown fox",
        "read the book",  # homograph
        "I'll be there",  # contraction
        "photograph",     # complex phonetics
        "psychology",     # silent letters
        "knight knows",   # silent letters
        "through tough",  # irregular spellings
        "record a record", # homograph pair
        "wind the wind"    # homograph pair
    ]

    mapper = AdvancedPhoneticMapper()

    print("\nTesting IPA mappings:")
    for test_text in test_cases:
        try:
            ipa_result = mapper.map_to_ipa(test_text)
            is_valid, errors = mapper.validate_ipa_string(ipa_result)

            print(f"Input:  '{test_text}'")
            print(f"IPA:    '{ipa_result}'")
            print(f"Valid:  {'✅' if is_valid else '❌'}")
            if errors:
                print(f"Errors: {', '.join(errors)}")
            print()

        except Exception as e:
            print(f"Error processing '{test_text}': {e}")
            print()

    # Test phoneme alternatives
    print("Testing phoneme alternatives:")
    test_phonemes = ["ɪ", "æ", "θ", "r"]
    for phoneme in test_phonemes:
        alternatives = mapper.get_phoneme_alternatives(phoneme)
        print(f"/{phoneme}/ alternatives: {alternatives}")

    print("\n✅ Advanced phonetic mapping system test completed!")

if __name__ == "__main__":
    main()
