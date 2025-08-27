#!/usr/bin/env python3
"""
Phonetic processing and spell function handling for TTS
"""

import re
from typing import Dict, List, Tuple, Optional
import logging
from .phonetic_dictionary_manager import PhoneticDictionaryManager, DictionaryEntry

logger = logging.getLogger(__name__)

class PhoneticProcessor:
    """Handles custom pronunciation markers and phonetic processing"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        # Check beta features first, then fallback to legacy location
        beta_features = self.config.get("beta_features", {})
        self.phonetic_config = beta_features.get("phonetic_processing", {})

        # Fallback to legacy location if not found in beta features
        if not self.phonetic_config:
            self.phonetic_config = self.config.get("phonetic_processing", {})

        # Initialize dictionary manager
        self.dictionary_manager = PhoneticDictionaryManager(self.phonetic_config)

        # Load traditional mappings for fallback
        self.phonetic_alphabet = self._load_phonetic_alphabet()
        self.ipa_mappings = self._load_ipa_mappings()

        # Auto-load dictionaries if enabled
        if self.phonetic_config.get("auto_load_dictionaries", True):
            self._load_configured_dictionaries()
        
    def _load_phonetic_alphabet(self) -> Dict[str, str]:
        """Load phonetic alphabet mappings"""
        return {
            # NATO phonetic alphabet
            'a': 'alpha', 'b': 'bravo', 'c': 'charlie', 'd': 'delta',
            'e': 'echo', 'f': 'foxtrot', 'g': 'golf', 'h': 'hotel',
            'i': 'india', 'j': 'juliet', 'k': 'kilo', 'l': 'lima',
            'm': 'mike', 'n': 'november', 'o': 'oscar', 'p': 'papa',
            'q': 'quebec', 'r': 'romeo', 's': 'sierra', 't': 'tango',
            'u': 'uniform', 'v': 'victor', 'w': 'whiskey', 'x': 'x-ray',
            'y': 'yankee', 'z': 'zulu'
        }
    
    def _load_ipa_mappings(self) -> Dict[str, str]:
        """Load IPA (International Phonetic Alphabet) to readable mappings - Enhanced with RIME AI inspired phonetic alphabet"""
        return {
            # Vowels - Enhanced mapping based on RIME AI phonetic alphabet
            'ɪ': 'I', 'i': 'i', 'ɛ': 'E', 'æ': '@', 'ʌ': 'A', 'ə': 'x',
            'ɑ': 'a', 'ɔ': 'O', 'ʊ': 'U', 'u': 'u',
            # Diphthongs - RIME AI style
            'eɪ': 'e', 'aɪ': 'Y', 'ɔɪ': 'O', 'aʊ': 'W', 'oʊ': 'o',
            'ɝ': 'R', 'ɚ': 'R', 'ɜ': 'R',  # R-colored vowels
            # Consonants - Enhanced mapping
            'θ': 'T', 'ð': 'D', 'ʃ': 'S', 'ʒ': 'Z', 'ŋ': 'G',
            'tʃ': 'C', 'dʒ': 'J',
            'p': 'p', 'b': 'b', 't': 't', 'd': 'd', 'k': 'k', 'g': 'g',
            'f': 'f', 'v': 'v', 's': 's', 'z': 'z', 'h': 'h', 'm': 'm', 'n': 'n',
            'j': 'y', 'w': 'w', 'r': 'r', 'l': 'l',
            # Stress markers - RIME AI style with numbers
            'ˈ': '1', 'ˌ': '2', '.': '0', 'ː': '',  # Length marker
            # Additional IPA symbols
            'x': 'h', 'ɣ': 'g', 'ɲ': 'n', 'ɭ': 'l', 'ɻ': 'r'
        }

    def _load_configured_dictionaries(self):
        """Load dictionaries based on configuration"""
        dictionary_sources = self.phonetic_config.get("dictionary_sources", {})

        for notation, file_path in dictionary_sources.items():
            if file_path:
                success = self.dictionary_manager.load_dictionary(notation, file_path)
                if success:
                    logger.info(f"Successfully loaded {notation} dictionary from {file_path}")
                else:
                    logger.warning(f"Failed to load {notation} dictionary from {file_path}")

        # Load custom dictionary if specified
        custom_dict_path = self.phonetic_config.get("custom_dictionary_path")
        if custom_dict_path:
            success = self.dictionary_manager.load_dictionary("custom", custom_dict_path)
            if success:
                logger.info(f"Successfully loaded custom dictionary from {custom_dict_path}")
            else:
                logger.warning(f"Failed to load custom dictionary from {custom_dict_path}")

    def process_phonetics(self, text: str) -> str:
        """Process custom pronunciation markers in text"""
        logger.debug(f"Processing phonetics in: {text[:100]}...")

        # First, apply dictionary-based phonetic corrections
        if self.phonetic_config.get("enabled", True):
            text = self._apply_dictionary_phonetics(text)
            logger.debug(f"After dictionary phonetics: {text}")

        # Process different types of phonetic markers
        pronunciation_markers = self.phonetic_config.get("pronunciation_markers", {})

        if pronunciation_markers.get("rime_ai_style", True):
            text = self._process_rime_style_phonetics(text)  # Enhanced RIME AI processing
            logger.debug(f"After RIME AI processing: {text}")
        if pronunciation_markers.get("custom_markers", True):
            text = self._process_curly_braces(text)  # RIME AI style {phonetic}
            logger.debug(f"After curly braces processing: {text}")
        if pronunciation_markers.get("ipa_notation", True):
            text = self._process_ipa_notation(text)  # IPA style /phonetic/
            logger.debug(f"After IPA notation processing: {text}")
        if pronunciation_markers.get("nato_phonetic", True):
            text = self._process_phonetic_alphabet(text)  # NATO style [letters]
            logger.debug(f"After NATO phonetic processing: {text}")

        logger.debug(f"Phonetic processing result: {text[:100] if text else 'None'}...")
        return text

    def _apply_dictionary_phonetics(self, text: str) -> str:
        """Apply phonetic corrections using loaded dictionaries"""
        if not self.dictionary_manager.dictionaries:
            return text

        # Check if dictionary-based phonetics is enabled
        processing_options = self.phonetic_config.get("processing_options", {})
        if not processing_options.get("dictionary_phonetics", True):
            return text

        # Split text into words while preserving punctuation and spacing
        words = re.findall(r'\b\w+\b|\W+', text)
        result_words = []

        primary_notation = self.phonetic_config.get("primary_notation", "arpabet")
        accent_variant = self.phonetic_config.get("accent_variant", "american")
        confidence_threshold = self.phonetic_config.get("confidence_threshold", 0.8)

        # Only apply to words that are likely to benefit from phonetic correction
        # Skip very common words to improve performance
        skip_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}

        for word in words:
            if re.match(r'\b\w+\b', word):  # Only process actual words
                word_lower = word.lower()

                # Skip very common words for performance
                if word_lower in skip_words:
                    result_words.append(word)
                    continue

                # Look up phonetic representation
                entry = self.dictionary_manager.lookup(
                    word_lower,
                    notation=primary_notation,
                    accent_variant=accent_variant
                )

                if entry and entry.confidence >= confidence_threshold:
                    # Convert phonetic representation to readable form
                    phonetic_word = self._convert_phonetic_to_speech(entry.phonetic, entry.notation)
                    result_words.append(phonetic_word)
                    logger.debug(f"Applied phonetic correction: {word} -> {phonetic_word}")
                else:
                    # Fallback to original word
                    result_words.append(word)
            else:
                # Preserve punctuation and spacing
                result_words.append(word)

        return ''.join(result_words)

    def _convert_phonetic_to_speech(self, phonetic: str, notation: str) -> str:
        """Convert phonetic representation to speech-friendly text"""
        if notation == "arpabet":
            return self._convert_arpabet_to_speech(phonetic)
        elif notation == "ipa":
            return self._convert_ipa_to_speech(phonetic)
        else:
            return phonetic  # Return as-is for unknown notations

    def _convert_arpabet_to_speech(self, arpabet: str) -> str:
        """Convert Arpabet phonemes to speech-friendly text"""
        # This is a simplified conversion - in practice, this would be more sophisticated
        # For now, we'll use the phonetic representation directly as it's already optimized for TTS
        return arpabet.lower().replace(' ', '')

    def _convert_ipa_to_speech(self, ipa: str) -> str:
        """Convert IPA phonemes to speech-friendly text"""
        # Convert IPA symbols to readable equivalents
        result = ipa
        for ipa_symbol, readable in self.ipa_mappings.items():
            result = result.replace(ipa_symbol, readable)
        return result
    
    def _process_curly_braces(self, text: str) -> str:
        """Process phonetic markers in curly braces {pronunciation}"""
        # Pattern: {phonetic_pronunciation}
        pattern = re.compile(r'\{([^}]+)\}')
        
        def replace_phonetic(match):
            phonetic = match.group(1)
            return self._convert_phonetic_to_readable(phonetic)
        
        return pattern.sub(replace_phonetic, text)  
  
    def _process_ipa_notation(self, text: str) -> str:
        """Process IPA notation markers"""
        # Pattern: /ipa_notation/
        pattern = re.compile(r'/([^/]+)/')
        
        def replace_ipa(match):
            ipa = match.group(1)
            return self._convert_ipa_to_readable(ipa)
        
        return pattern.sub(replace_ipa, text)
    
    def _process_phonetic_alphabet(self, text: str) -> str:
        """Process NATO phonetic alphabet markers"""
        # Pattern: [phonetic_letters]
        pattern = re.compile(r'\[([a-zA-Z\s]+)\]')

        def replace_phonetic_alphabet(match):
            letters = match.group(1).lower().replace(' ', '')
            result = []
            for letter in letters:
                if letter in self.phonetic_alphabet:
                    result.append(self.phonetic_alphabet[letter])
                else:
                    result.append(letter)
            return ' '.join(result)

        return pattern.sub(replace_phonetic_alphabet, text)

    def add_custom_pronunciation(self, word: str, phonetic: str, notation: str = "custom",
                                confidence: float = 1.0, accent_variant: str = "general"):
        """Add a custom pronunciation to the dictionary"""
        self.dictionary_manager.add_custom_entry(word, phonetic, notation, confidence, accent_variant)

    def remove_pronunciation(self, word: str, notation: str = None):
        """Remove a pronunciation from the dictionary"""
        self.dictionary_manager.remove_entry(word, notation)

    def get_pronunciation(self, word: str, notation: str = None, accent_variant: str = None) -> Optional[DictionaryEntry]:
        """Get the phonetic representation for a word"""
        return self.dictionary_manager.lookup(word, notation, accent_variant)

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about phonetic processing"""
        base_stats = self.dictionary_manager.get_statistics()

        # Add phonetic processor specific stats
        base_stats.update({
            "phonetic_processor": {
                "config_enabled": self.phonetic_config.get("enabled", True),
                "primary_notation": self.phonetic_config.get("primary_notation", "arpabet"),
                "accent_variant": self.phonetic_config.get("accent_variant", "american"),
                "pronunciation_markers_enabled": self.phonetic_config.get("pronunciation_markers", {}),
                "processing_options": self.phonetic_config.get("processing_options", {}),
                "performance_limits": self.phonetic_config.get("performance_limits", {})
            }
        })

        return base_stats

    def reload_dictionaries(self):
        """Reload all configured dictionaries"""
        self._load_configured_dictionaries()

    def clear_cache(self):
        """Clear the phonetic processing cache"""
        self.dictionary_manager.clear_cache()

    def save_cache(self):
        """Save the phonetic processing cache to disk"""
        self.dictionary_manager.save_cache()

    def load_cache(self):
        """Load the phonetic processing cache from disk"""
        self.dictionary_manager.load_cache()

    def export_dictionary(self, notation: str, file_path: str, format: str = "json"):
        """Export a dictionary to file"""
        return self.dictionary_manager.export_dictionary(notation, file_path, format)

    def _process_rime_style_phonetics(self, text: str) -> str:
        """Process RIME AI-style phonetic notation with stress markers"""
        # Enhanced processing for RIME AI-style phonetics
        # Look for patterns like {k1Ast0xm} (custom with stress markers)
        pattern = re.compile(r'\{([^}]+)\}')

        def replace_rime_phonetic(match):
            phonetic = match.group(1)
            return self._convert_rime_to_readable(phonetic)

        return pattern.sub(replace_rime_phonetic, text)

    def _convert_rime_to_readable(self, phonetic: str) -> str:
        """Convert RIME AI-style phonetic notation to readable text"""
        # Handle RIME AI phonetic alphabet with stress markers
        result = []
        i = 0

        while i < len(phonetic):
            # Check for stress markers (numbers)
            if phonetic[i].isdigit():
                stress_level = phonetic[i]
                if stress_level == '1':
                    result.append("'")  # Primary stress
                elif stress_level == '2':
                    result.append(",")  # Secondary stress
                # Skip '0' (no stress)
                i += 1
                continue

            # Check for RIME AI phonetic symbols
            char = phonetic[i]
            if char in self.ipa_mappings:
                result.append(self.ipa_mappings[char])
            else:
                result.append(char)

            i += 1

        return ''.join(result)
    
    def _convert_phonetic_to_readable(self, phonetic: str) -> str:
        """Convert custom phonetic notation to readable text"""
        # Handle common phonetic patterns
        phonetic = phonetic.lower()
        
        # Replace numbers with stress markers
        phonetic = re.sub(r'0', '', phonetic)  # No stress
        phonetic = re.sub(r'1', "'", phonetic)  # Primary stress
        phonetic = re.sub(r'2', ",", phonetic)  # Secondary stress
        
        # Convert common phonetic symbols
        conversions = {
            'aa': 'ah', 'ae': 'a', 'ah': 'ah', 'ao': 'aw', 'aw': 'aw',
            'ay': 'eye', 'eh': 'eh', 'er': 'er', 'ey': 'ay', 'ih': 'ih',
            'iy': 'ee', 'ow': 'oh', 'oy': 'oy', 'uh': 'uh', 'uw': 'oo',
            'ch': 'ch', 'dh': 'th', 'jh': 'j', 'ng': 'ng', 'sh': 'sh',
            'th': 'th', 'zh': 'zh'
        }
        
        # Apply conversions
        for phonetic_symbol, readable in conversions.items():
            phonetic = phonetic.replace(phonetic_symbol, readable)
        
        return phonetic
    
    def _convert_ipa_to_readable(self, ipa: str) -> str:
        """Convert IPA notation to readable pronunciation"""
        result = []
        i = 0
        
        while i < len(ipa):
            # Check for two-character IPA symbols first
            if i < len(ipa) - 1:
                two_char = ipa[i:i+2]
                if two_char in self.ipa_mappings:
                    result.append(self.ipa_mappings[two_char])
                    i += 2
                    continue
            
            # Check for single-character IPA symbols
            char = ipa[i]
            if char in self.ipa_mappings:
                result.append(self.ipa_mappings[char])
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result)