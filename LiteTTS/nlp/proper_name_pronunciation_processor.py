#!/usr/bin/env python3
"""
Proper Name and Word Pronunciation Processor for TTS
Fixes specific word mispronunciations like Elon→alon, Joy→joie, acquisition→ek-wah-zi·shn
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Set
import logging

logger = logging.getLogger(__name__)

class ProperNamePronunciationProcessor:
    """Processor for fixing specific proper name and word pronunciation issues"""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize proper name pronunciation processor

        Args:
            config: Configuration dictionary (uses centralized config system)
        """
        self.config = config or self._load_default_config()
        self.proper_name_fixes = self._load_proper_name_fixes()
        self.word_pronunciation_fixes = self._load_word_pronunciation_fixes()
        self.context_sensitive_fixes = self._load_context_sensitive_fixes()
        self.enabled = self._is_enabled()

    def _load_default_config(self) -> Dict:
        """Load default configuration from centralized config system"""
        try:
            # Try to import and use the centralized config system
            from ..config import config as app_config
            return app_config.to_dict()
        except ImportError:
            logger.warning("Could not load centralized config, using defaults")
            return self._get_fallback_config()

    def _get_fallback_config(self) -> Dict:
        """Get fallback configuration if centralized config is not available"""
        return {
            'text_processing': {
                'proper_name_pronunciation': {
                    'enabled': True
                }
            }
        }

    def _is_enabled(self) -> bool:
        """Check if proper name pronunciation fixes are enabled"""
        return (self.config.get('text_processing', {})
                .get('proper_name_handling', {})
                .get('enabled', True))

    def _load_proper_name_fixes(self) -> Dict[str, str]:
        """Load proper name pronunciation fixes

        NOTE: These phonetic spellings use non-IPA notation and interfere with
        kokoro's character-based tokenizer. Only ALL CAPS entries (like stock tickers)
        and entries verified to work with the ONNX model should be added here.
        """
        default_fixes = {
            # Stock tickers - ALL CAPS so kokoro's tokenizer spells them out
            "TSLA": "T S L A",
            "AAPL": "A A P L",
            "MSFT": "M S F T",
            "GOOGL": "G O O G L",
            "AMZN": "A M Z N",
            "NVDA": "N V D A",
            "META": "M E T A",
            "NFLX": "N F L X",
            "COIN": "C O I N",
        }

        # Get fixes from config, fall back to defaults
        config_fixes = (self.config.get('text_processing', {})
                       .get('proper_name_handling', {})
                       .get('name_pronunciations', {}))

        # Merge config fixes with defaults
        fixes = default_fixes.copy()
        fixes.update(config_fixes)

        return fixes

    def _load_word_pronunciation_fixes(self) -> Dict[str, str]:
        """Load general word pronunciation fixes

        NOTE: These phonetic spellings use non-IPA notation and interfere with
        kokoro's character-based tokenizer. Only ALL CAPS entries (like ticker symbols)
        and entries verified to work with the ONNX model should be added here.
        """
        default_fixes = {
            # Technology terms - ALL CAPS so they're clearly abbreviations
            "API": "A P I",
            "GUI": "G U I",
            "SQL": "sequel",  # Pronounced "sequel", not S-Q-L
            "JSON": "Jason",  # Pronounced "Jason", not J-S-O-N
            "XML": "X M L",
            "HTTP": "H T T P",
            "URL": "U R L",
            "PDF": "P D F",
            "CSS": "C S S",
            "HTML": "H T M L",
        }

        # Get fixes from config
        config_fixes = (self.config.get('text_processing', {})
                       .get('proper_name_handling', {})
                       .get('word_pronunciations', {}))

        # Merge config fixes with defaults
        fixes = default_fixes.copy()
        fixes.update(config_fixes)

        return fixes

    def _load_context_sensitive_fixes(self) -> List[Tuple[str, str, str, str]]:
        """Load context-sensitive pronunciation fixes

        NOTE: These phonetic spellings use non-IPA notation and interfere with
        kokoro's character-based tokenizer. Kokoro handles homographs through its
        built-in grapheme-to-phoneme system, so context-sensitive fixes are disabled.
        """
        return []

    def process_proper_name_pronunciation(self, text: str) -> str:
        """Apply proper name and word pronunciation fixes"""
        if not self.enabled:
            return text

        logger.debug(f"Applying proper name pronunciation fixes to: {text[:100]}...")

        original_text = text

        # Apply proper name fixes
        text = self._apply_proper_name_fixes(text)

        # Apply word pronunciation fixes
        text = self._apply_word_pronunciation_fixes(text)

        # Apply context-sensitive fixes
        text = self._apply_context_sensitive_fixes(text)

        if text != original_text:
            logger.debug(f"Proper name pronunciation fixes applied: '{original_text}' → '{text}'")

        return text

    def _apply_proper_name_fixes(self, text: str) -> str:
        """Apply proper name pronunciation fixes"""
        for name, pronunciation in self.proper_name_fixes.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(name) + r'\b'

            # Apply case-insensitive replacement while preserving original case
            def replace_with_case_preservation(match):
                original = match.group(0)

                # If original is all caps, make pronunciation all caps
                if original.isupper():
                    return pronunciation.upper()
                # If original starts with capital, capitalize pronunciation
                elif original[0].isupper():
                    return pronunciation.capitalize()
                # Otherwise, keep pronunciation as-is
                else:
                    return pronunciation.lower()

            text = re.sub(pattern, replace_with_case_preservation, text, flags=re.IGNORECASE)

        return text

    def _apply_word_pronunciation_fixes(self, text: str) -> str:
        """Apply general word pronunciation fixes"""
        for word, pronunciation in self.word_pronunciation_fixes.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(word) + r'\b'

            # Apply case-insensitive replacement while preserving original case
            def replace_with_case_preservation(match):
                original = match.group(0)

                # If original is all caps, make pronunciation all caps
                if original.isupper():
                    return pronunciation.upper()
                # If original starts with capital, capitalize pronunciation
                elif original[0].isupper():
                    return pronunciation.capitalize()
                # Otherwise, keep pronunciation as-is
                else:
                    return pronunciation.lower()

            text = re.sub(pattern, replace_with_case_preservation, text, flags=re.IGNORECASE)

        return text

    def _apply_context_sensitive_fixes(self, text: str) -> str:
        """Apply context-sensitive pronunciation fixes"""
        for word, context_pattern, pronunciation, description in self.context_sensitive_fixes:
            # Check if the context pattern matches
            if re.search(context_pattern, text, re.IGNORECASE):
                # Apply the pronunciation fix within the context
                word_pattern = r'\b' + re.escape(word) + r'\b'

                def replace_with_case_preservation(match):
                    original = match.group(0)

                    # If original is all caps, make pronunciation all caps
                    if original.isupper():
                        return pronunciation.upper()
                    # If original starts with capital, capitalize pronunciation
                    elif original[0].isupper():
                        return pronunciation.capitalize()
                    # Otherwise, keep pronunciation as-is
                    else:
                        return pronunciation.lower()

                text = re.sub(word_pattern, replace_with_case_preservation, text, flags=re.IGNORECASE)
                logger.debug(f"Applied context-sensitive fix: {description}")

        return text

    def analyze_pronunciation_issues(self, text: str) -> Dict:
        """Analyze potential pronunciation issues in text"""
        analysis = {
            'proper_names_found': [],
            'words_with_fixes': [],
            'context_sensitive_matches': [],
            'potential_issues': [],
            'suggestions': []
        }

        # Check for proper names
        for name in self.proper_name_fixes.keys():
            if re.search(r'\b' + re.escape(name) + r'\b', text, re.IGNORECASE):
                analysis['proper_names_found'].append(name)

        # Check for words with fixes
        for word in self.word_pronunciation_fixes.keys():
            if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
                analysis['words_with_fixes'].append(word)

        # Check for context-sensitive matches
        for word, context_pattern, pronunciation, description in self.context_sensitive_fixes:
            if re.search(context_pattern, text, re.IGNORECASE):
                analysis['context_sensitive_matches'].append({
                    'word': word,
                    'context': description,
                    'pronunciation': pronunciation
                })

        return analysis

    def add_pronunciation_fix(self, word: str, pronunciation: str, is_proper_name: bool = False):
        """Add a new pronunciation fix"""
        if is_proper_name:
            self.proper_name_fixes[word] = pronunciation
            logger.info(f"Added proper name pronunciation: {word} → {pronunciation}")
        else:
            self.word_pronunciation_fixes[word] = pronunciation
            logger.info(f"Added word pronunciation: {word} → {pronunciation}")

    def get_all_fixes(self) -> Dict:
        """Get all pronunciation fixes"""
        return {
            'proper_names': self.proper_name_fixes.copy(),
            'words': self.word_pronunciation_fixes.copy(),
            'context_sensitive': self.context_sensitive_fixes.copy()
        }

# Example usage and testing
if __name__ == "__main__":
    # Create processor
    processor = ProperNamePronunciationProcessor()

    # Test critical pronunciation fixes
    test_cases = [
        "Elon Musk announced new Tesla features",
        "The acquisition was completed successfully",
        "Joy is working on the project",
        "I need to update my resume for the job",
        "We will resume work tomorrow",
        "The live stream starts at 8 PM",
        "Where do you live?",
        "I read the book yesterday",
        "I will read it tomorrow",
        "She's the lead developer",
        "Lead pipes are dangerous"
    ]

    print("🔧 Testing Proper Name & Word Pronunciation Processor")
    print("=" * 60)

    for text in test_cases:
        result = processor.process_proper_name_pronunciation(text)
        if result != text:
            print(f"✅ '{text}' → '{result}'")
        else:
            print(f"⚪ '{text}' (no changes)")

    # Analyze sample text
    sample_text = "Elon announced the acquisition of a company. Joy will resume work on the live project."
    analysis = processor.analyze_pronunciation_issues(sample_text)
    print(f"\n🔍 Analysis of: {sample_text}")
    print("=" * 40)
    print(f"Proper names: {analysis['proper_names_found']}")
    print(f"Words with fixes: {analysis['words_with_fixes']}")
    print(f"Context matches: {len(analysis['context_sensitive_matches'])}")
