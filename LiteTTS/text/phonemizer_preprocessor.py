#!/usr/bin/env python3
"""
Advanced text preprocessor specifically designed to prevent phonemizer issues
This module addresses the "words count mismatch" warnings that cause empty audio generation
"""

import re
import unicodedata
import html
import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Import enhanced contraction processor for better contraction handling
try:
    from ..nlp.enhanced_contraction_processor import EnhancedContractionProcessor
    ENHANCED_CONTRACTIONS_AVAILABLE = True
except ImportError:
    logger.warning("Enhanced contraction processor not available, falling back to basic processing")
    ENHANCED_CONTRACTIONS_AVAILABLE = False

@dataclass
class PreprocessingResult:
    """Result of text preprocessing"""
    processed_text: str
    original_text: str
    changes_made: List[str]
    confidence_score: float  # 0.0 to 1.0, higher means more likely to work with phonemizer
    warnings: List[str]

class PhonemizationPreprocessor:
    """
    Advanced text preprocessor designed to prevent phonemizer word count mismatches
    
    The phonemizer often fails when:
    1. Word boundaries don't align with phoneme boundaries
    2. Special characters confuse tokenization
    3. Contractions aren't handled properly
    4. Numbers and symbols aren't converted to words
    5. Unicode normalization issues
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.contractions_map = self._build_contractions_map()
        self.problematic_contractions = self._build_problematic_contractions()
        self.number_words_map = self._build_number_words_map()
        self.symbol_words_map = self._build_symbol_words_map()
        self.problematic_patterns = self._build_problematic_patterns()

        # Initialize enhanced contraction processor for better contraction handling
        if ENHANCED_CONTRACTIONS_AVAILABLE:
            self.enhanced_contraction_processor = EnhancedContractionProcessor(config=self.config)
            logger.debug("Enhanced contraction processor initialized with config")
        else:
            self.enhanced_contraction_processor = None

        # Cache config values to avoid repeated imports (PERFORMANCE OPTIMIZATION)
        self._load_config_cache()

        # Pre-compile regex patterns for performance (PERFORMANCE OPTIMIZATION)
        self._compile_regex_patterns()

    def _load_config_cache(self):
        """Load and cache configuration values to avoid repeated imports"""
        try:
            # First try to load from the main config (config.json)
            if hasattr(self, 'config') and self.config:
                # Use the config passed to the constructor
                text_processing = self.config.get('text_processing', {})
                self.expand_all = text_processing.get('expand_contractions', False)
                self.preserve_natural = text_processing.get('natural_speech', True)
                logger.debug("Config loaded from constructor config")
            else:
                # Fallback to kokoro.config
                from LiteTTS.config import config
                self.expand_all = config.performance.expand_contractions
                self.preserve_natural = config.performance.preserve_natural_speech
                logger.debug("Config loaded from LiteTTS.config")

            # These settings are still from performance config
            try:
                from LiteTTS.config import config
                self.expand_problematic_only = config.performance.expand_problematic_contractions_only
                # Emoji and symbol handling configuration (CRITICAL FIX)
                self.filter_emojis = config.performance.filter_emojis
                self.emoji_replacement = config.performance.emoji_replacement
                self.preserve_word_count_config = config.performance.preserve_word_count
            except:
                self.expand_problematic_only = True
                self.filter_emojis = True
                self.emoji_replacement = ""
                self.preserve_word_count_config = True

            logger.debug(f"Config cached: expand_all={self.expand_all}, preserve_natural={self.preserve_natural}")
        except Exception as e:
            # Fallback to conservative defaults if config unavailable
            self.expand_all = False
            self.expand_problematic_only = True
            self.preserve_natural = True

            # Emoji and symbol handling defaults (CRITICAL FIX)
            self.filter_emojis = True  # Default: filter emojis
            self.emoji_replacement = ""  # Default: remove emojis
            self.preserve_word_count_config = True  # Default: preserve word count

            logger.warning(f"Could not load config, using defaults: {e}")

    def _compile_regex_patterns(self):
        """Pre-compile regex patterns for performance optimization"""
        # Control character removal pattern
        self.control_char_pattern = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]')

        # HTML entity patterns for smart symbol conversion
        self.html_entity_amp_pattern = re.compile(r'&(?![a-zA-Z0-9#]+;)')
        self.html_entity_hash_pattern = re.compile(r'#(?![x0-9a-fA-F]+;)')

        # Whitespace cleanup pattern
        self.whitespace_pattern = re.compile(r'\s+')

        logger.debug("Regex patterns compiled for performance optimization")

    def _build_contractions_map(self) -> Dict[str, str]:
        """Build comprehensive contractions mapping from external config file"""
        try:
            # Try to load from external config file first
            config_path = Path("LiteTTS/config/contractions.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                # Flatten all contraction categories into a single dictionary
                contractions = {}
                for category_name, category_data in config_data.items():
                    if not category_name.startswith('_') and isinstance(category_data, dict):
                        contractions.update(category_data)

                logger.debug(f"Loaded {len(contractions)} contractions from external config")
                return contractions
        except Exception as e:
            logger.warning(f"Failed to load contractions from external config: {e}")

        # Fallback to built-in contractions
        return {
            # Standard contractions
            "don't": "do not", "won't": "will not", "can't": "cannot", "couldn't": "could not",
            "shouldn't": "should not", "wouldn't": "would not", "mustn't": "must not",
            "needn't": "need not", "daren't": "dare not", "mayn't": "may not",

            # Positive contractions
            "I'm": "I am", "you're": "you are", "he's": "he is", "she's": "she is",
            "it's": "it is", "we're": "we are", "they're": "they are",
            "I've": "I have", "you've": "you have", "we've": "we have", "they've": "they have",
            "I'll": "I will", "you'll": "you will", "he'll": "he will", "she'll": "she will",
            "it'll": "it will", "we'll": "we will", "they'll": "they will",
            "I'd": "I would", "you'd": "you would", "he'd": "he would", "she'd": "she would",
            "it'd": "it would", "we'd": "we would", "they'd": "they would",

            # Other common contractions
            "that's": "that is", "there's": "there is", "here's": "here is",
            "what's": "what is", "where's": "where is", "when's": "when is",
            "who's": "who is", "how's": "how is", "why's": "why is",
            "let's": "let us", "that'll": "that will", "who'll": "who will",

            # Informal contractions
            "gonna": "going to", "wanna": "want to", "gotta": "got to",
            "kinda": "kind of", "sorta": "sort of", "outta": "out of",
            "dunno": "do not know", "gimme": "give me", "lemme": "let me",

            # 'd ambiguity - default to "would" (most common)
            "'d": " would", "'ll": " will", "'re": " are", "'ve": " have",
            "'m": " am", "'s": " is", "n't": " not"
        }

    def _build_problematic_contractions(self) -> Dict[str, str]:
        """
        Build a mapping of contractions that are known to cause phonemizer issues

        These are contractions that consistently cause "words count mismatch" warnings
        and should be expanded even when preserve_natural_speech is True.

        Currently using a conservative approach - only expand when absolutely necessary.
        """
        return {
            # Based on empirical testing, most contractions work fine with the phonemizer
            # Only add contractions here if they consistently cause issues

            # Placeholder for future problematic contractions discovered through usage
            # Example format:
            # "specific_problematic_contraction": "expansion"

            # Note: The generic patterns like 'n't, 'd, 's are too broad and affect
            # natural speech quality. Only add specific full contractions that cause issues.
        }

    def _build_number_words_map(self) -> Dict[str, str]:
        """Build number to words mapping from external config file"""
        try:
            # Try to load from external config file first
            config_path = Path("LiteTTS/config/numbers.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                # Flatten all number categories into a single dictionary
                numbers = {}
                for category_name, category_data in config_data.items():
                    if not category_name.startswith('_') and isinstance(category_data, dict):
                        numbers.update(category_data)

                logger.debug(f"Loaded {len(numbers)} number mappings from external config")
                return numbers
        except Exception as e:
            logger.warning(f"Failed to load numbers from external config: {e}")

        # Fallback to built-in numbers
        return {
            '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
            '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine',
            '10': 'ten', '11': 'eleven', '12': 'twelve', '13': 'thirteen',
            '14': 'fourteen', '15': 'fifteen', '16': 'sixteen', '17': 'seventeen',
            '18': 'eighteen', '19': 'nineteen', '20': 'twenty', '30': 'thirty',
            '40': 'forty', '50': 'fifty', '60': 'sixty', '70': 'seventy',
            '80': 'eighty', '90': 'ninety', '100': 'one hundred', '1000': 'one thousand'
        }
    
    def _build_symbol_words_map(self) -> Dict[str, str]:
        """Build symbol to words mapping from external config file"""
        try:
            # Try to load from external config file first
            config_path = Path("LiteTTS/config/symbols.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                # Flatten all symbol categories into a single dictionary
                symbols = {}
                for category_name, category_data in config_data.items():
                    if not category_name.startswith('_') and isinstance(category_data, dict):
                        symbols.update(category_data)

                logger.debug(f"Loaded {len(symbols)} symbol mappings from external config")
                return symbols
        except Exception as e:
            logger.warning(f"Failed to load symbols from external config: {e}")

        # Fallback to built-in symbols
        return {
            '&': 'and', '+': 'plus', '=': 'equals', '%': 'percent',
            '$': 'dollars', '€': 'euros', '£': 'pounds', '¥': 'yen',
            '@': 'at', '#': 'hash', '*': 'star', '/': 'slash',
            '\\': 'backslash', '|': 'pipe', '^': 'caret', '~': 'tilde',
            '<': 'less than', '>': 'greater than', '©': 'copyright',
            '®': 'registered', '™': 'trademark', '°': 'degrees',
            # Quote handling - CRITICAL FIX for "in quat" pronunciation issue
            '"': '',  # Double quotes should be silent (empty string)
            '"': '',  # Left double quotation mark
            '"': '',  # Right double quotation mark
            ''': '',  # Left single quotation mark (for non-contraction quotes)
            ''': '',  # Right single quotation mark (for non-contraction quotes)
        }
    
    def _build_problematic_patterns(self) -> List[Tuple[str, str, str]]:
        """
        Build list of problematic patterns that cause phonemizer issues

        Note: Removed the general hyphenated words pattern that was converting
        natural compound words like "twenty-one" to "twenty dash one".
        Hyphens in compound words should be preserved for natural speech.
        """
        return [
            # Pattern, Replacement, Description
            (r'\b(\w+)\.(\w+)\b', r'\1 dot \2', 'Domain names and file extensions'),
            (r'\b(\w+)@(\w+)\b', r'\1 at \2', 'Email addresses'),
            (r'\b(\d+)-(\d+)\b', r'\1 to \2', 'Number ranges'),  # Keep this for "1-10" -> "1 to 10"
            (r'\b(\d+)/(\d+)\b', r'\1 slash \2', 'Fractions and dates'),
            (r'\b(\d+):(\d+)\b', r'\1 colon \2', 'Time expressions'),
            (r'\b(\w+)_(\w+)\b', r'\1 underscore \2', 'Underscored words'),
            # REMOVED: (r'\b(\w+)-(\w+)\b', r'\1 dash \2', 'Hyphenated words') - breaks natural speech
            (r'([A-Z]{2,})', lambda m: ' '.join(m.group(1).lower()), 'Acronyms'),
            (r'\b(\d+)([A-Za-z]+)\b', r'\1 \2', 'Number-letter combinations'),
        ]
    
    def preprocess_text(self, text: str, aggressive: bool = False, preserve_word_count: bool = True) -> PreprocessingResult:
        """
        Main preprocessing function with multiple strategies

        Args:
            text: Input text to preprocess
            aggressive: If True, applies more aggressive preprocessing
            preserve_word_count: If True, tries to preserve word count to avoid phonemizer mismatches

        Returns:
            PreprocessingResult with processed text and metadata
        """
        original_text = text
        changes_made = []
        warnings = []
        original_word_count = len(text.split())

        # Step 1: HTML entity decoding (CRITICAL: Must be first!)
        text, html_changes = self._decode_html_entities(text)
        changes_made.extend(html_changes)

        # Step 2: Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        if text != original_text and "HTML entity decoding" not in changes_made:
            changes_made.append("Unicode normalization")

        # Step 3: Remove control characters (using pre-compiled pattern)
        text = self.control_char_pattern.sub('', text)

        # Step 3.1: Handle quote characters (CRITICAL FIX for "in quat" pronunciation)
        text, quote_changes = self._handle_quote_characters(text)
        changes_made.extend(quote_changes)

        # Step 3.5: Handle emojis (CRITICAL FIX for emoji verbalization)
        if preserve_word_count and self.filter_emojis:
            text, emoji_changes = self._filter_emojis(text)
            changes_made.extend(emoji_changes)

        # Step 4: Handle contractions (CONSERVATIVE MODE for word count preservation)
        if preserve_word_count:
            # Only expand contractions that are known to cause phonemizer failures
            text, contraction_changes = self._expand_contractions_conservative(text)
        else:
            # Full contraction expansion (legacy mode)
            text, contraction_changes = self._expand_contractions(text)
        changes_made.extend(contraction_changes)

        # Step 5: Handle numbers (CONSERVATIVE MODE for word count preservation)
        if preserve_word_count:
            text, number_changes = self._convert_numbers_conservative(text)
        else:
            text, number_changes = self._convert_numbers_to_words(text, aggressive)
        changes_made.extend(number_changes)

        # Step 6: Handle symbols (CONSERVATIVE MODE for word count preservation)
        if preserve_word_count:
            text, symbol_changes = self._convert_symbols_conservative(text)
        else:
            text, symbol_changes = self._convert_symbols_to_words(text)
        changes_made.extend(symbol_changes)

        # Step 7: Handle problematic patterns (CONSERVATIVE MODE)
        if preserve_word_count:
            text, pattern_changes = self._fix_problematic_patterns_conservative(text)
        else:
            text, pattern_changes = self._fix_problematic_patterns(text)
        changes_made.extend(pattern_changes)

        # Step 8: Clean up whitespace and punctuation
        text = self._clean_whitespace_and_punctuation(text)

        # Step 9: Validate word count and score
        final_word_count = len(text.split())
        if preserve_word_count and final_word_count != original_word_count:
            warnings.append(f"Word count changed from {original_word_count} to {final_word_count} - may cause phonemizer issues")
            logger.warning(f"Word count mismatch: {original_word_count} -> {final_word_count} for text: '{original_text[:50]}...'")

        confidence_score = self._calculate_confidence_score(text, original_text)
        warnings.extend(self._detect_potential_issues(text))

        # Ensure text ends with proper punctuation (but don't count this as a word)
        # Skip terminal punctuation for time expressions
        is_time_expression = self._is_time_expression(text)

        if text and not text[-1] in '.!?' and not is_time_expression:
            text += '.'
            changes_made.append("Added terminal punctuation")

        result = PreprocessingResult(
            processed_text=text.strip(),
            original_text=original_text,
            changes_made=changes_made,
            confidence_score=confidence_score,
            warnings=warnings
        )

        if changes_made:
            logger.debug(f"Text preprocessing made {len(changes_made)} changes: {', '.join(changes_made)}")

        return result

    def _is_time_expression(self, text: str) -> bool:
        """Check if the text is a time expression that shouldn't have terminal punctuation"""
        text_lower = text.lower().strip()

        # Check for time expression patterns
        time_patterns = [
            r'\b(?:ten|eleven|twelve|one|two|three|four|five|six|seven|eight|nine)\s+(?:thirty|fifteen|forty|oh|zero)\s*(?:five)?\s+(?:a\s+m|p\s+m)$',
            r'\b(?:ten|eleven|twelve|one|two|three|four|five|six|seven|eight|nine)\s+o\'?clock\s*(?:a\s+m|p\s+m)?$',
            r'\b(?:ten|eleven|twelve|one|two|three|four|five|six|seven|eight|nine)\s+(?:a\s+m|p\s+m)$'
        ]

        for pattern in time_patterns:
            if re.search(pattern, text_lower):
                return True

        return False

    def _expand_contractions(self, text: str) -> Tuple[str, List[str]]:
        """
        Process contractions using enhanced contraction processor or fallback to legacy method

        Behavior depends on configuration settings:
        - expand_contractions=False: Use hybrid mode (expand problematic, keep natural)
        - expand_contractions=True: Expand all contractions
        - expand_problematic_contractions_only=True: Smart selective expansion
        """
        changes = []
        original_text = text

        # Use enhanced contraction processor if available
        if self.enhanced_contraction_processor is not None:
            # Use cached config values (PERFORMANCE OPTIMIZATION)
            expand_all = self.expand_all
            preserve_natural = self.preserve_natural

            # Determine contraction processing mode
            if expand_all and not preserve_natural:
                # Expand all contractions (legacy behavior)
                mode = 'expanded'
                logger.debug("Using enhanced contraction processor in expanded mode")
            elif preserve_natural:
                # Use hybrid mode (default for natural speech)
                mode = 'hybrid'
                logger.debug("Using enhanced contraction processor in hybrid mode")
            else:
                # Natural mode - keep contractions as-is
                mode = 'natural'
                logger.debug("Using enhanced contraction processor in natural mode")

            # Process contractions with enhanced processor
            processed_text = self.enhanced_contraction_processor.process_contractions(text, mode)

            if processed_text != original_text:
                changes.append(f"Enhanced contraction processing applied ({mode} mode)")
                logger.debug(f"Enhanced contraction processing: '{original_text[:50]}...' → '{processed_text[:50]}...'")

            return processed_text, changes

        # Fallback to legacy contraction processing
        logger.debug("Using legacy contraction processing")

        # Use cached config values (PERFORMANCE OPTIMIZATION)
        expand_all = self.expand_all
        expand_problematic_only = self.expand_problematic_only
        preserve_natural = self.preserve_natural

        # Determine which contractions to expand
        if expand_all:
            # Expand all contractions (legacy behavior)
            contractions_to_expand = self.contractions_map
            logger.debug("Expanding all contractions (expand_contractions=True)")
        elif expand_problematic_only and preserve_natural:
            # Only expand contractions known to cause phonemizer issues
            contractions_to_expand = self.problematic_contractions
            logger.debug("Expanding only problematic contractions (selective mode)")
        elif not preserve_natural:
            # Expand all for compatibility
            contractions_to_expand = self.contractions_map
            logger.debug("Expanding all contractions (preserve_natural_speech=False)")
        else:
            # Preserve all contractions
            contractions_to_expand = {}
            logger.debug("Preserving all contractions (expand_contractions=False)")

        if not contractions_to_expand:
            logger.debug("No contractions to expand, preserving natural speech")
            return text, changes

        # Sort by length (longest first) to avoid partial replacements
        sorted_contractions = sorted(contractions_to_expand.items(), key=lambda x: len(x[0]), reverse=True)

        for contraction, expansion in sorted_contractions:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(contraction) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
                changes.append(f"Expanded '{contraction}' to '{expansion}'")

        return text, changes

    def _expand_contractions_conservative(self, text: str) -> Tuple[str, List[str]]:
        """
        Conservative contraction expansion that preserves word count
        Only expands contractions that are known to cause phonemizer failures
        """
        changes = []

        # Only expand contractions that consistently cause phonemizer word count mismatches
        problematic_contractions = {
            # Add specific contractions here that cause issues
            # Currently keeping this minimal to preserve natural speech
        }

        if not problematic_contractions:
            logger.debug("No problematic contractions to expand in conservative mode")
            return text, changes

        # Sort by length (longest first) to avoid partial replacements
        sorted_contractions = sorted(problematic_contractions.items(), key=lambda x: len(x[0]), reverse=True)

        for contraction, expansion in sorted_contractions:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(contraction) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
                changes.append(f"Expanded problematic '{contraction}' to '{expansion}'")

        return text, changes

    def _convert_numbers_conservative(self, text: str) -> Tuple[str, List[str]]:
        """
        Ultra-conservative number conversion that prioritizes word count preservation
        Only converts numbers in very specific cases where phonemizer consistently fails
        """
        changes = []

        # ULTRA-CONSERVATIVE: Only convert numbers that cause consistent phonemizer failures
        # AND where the conversion doesn't dramatically change word count

        # Convert only standalone "0" which is often misread as "oh"
        # This is a 1:1 word replacement so it preserves word count
        if re.search(r'\b0\b', text):
            text = re.sub(r'\b0\b', 'zero', text)
            changes.append("Converted standalone '0' to 'zero'")

        # For comma-separated numbers, we have a choice:
        # 1. Convert them (better pronunciation, but changes word count)
        # 2. Leave them (preserves word count, but may be read digit-by-digit)
        #
        # In ULTRA-CONSERVATIVE mode, we choose option 2 to preserve word count
        # The user can use aggressive mode if they want number conversion

        comma_number_pattern = r'\b\d{1,3}(?:,\d{3})+\b'
        comma_matches = re.findall(comma_number_pattern, text)
        if comma_matches:
            # Just warn about them, don't convert
            changes.append(f"Found comma-separated numbers that may be read digit-by-digit: {', '.join(comma_matches)}")
            logger.debug(f"Conservative mode: preserving comma-separated numbers to maintain word count: {comma_matches}")

        # For decimal numbers, same approach - preserve word count
        decimal_pattern = r'\b\d+\.\d+\b'
        decimal_matches = re.findall(decimal_pattern, text)
        if decimal_matches:
            # Just warn about them, don't convert
            changes.append(f"Found decimal numbers that may be read digit-by-digit: {', '.join(decimal_matches)}")
            logger.debug(f"Conservative mode: preserving decimal numbers to maintain word count: {decimal_matches}")

        return text, changes

    def _convert_symbols_conservative(self, text: str) -> Tuple[str, List[str]]:
        """
        Conservative symbol conversion that preserves word count
        Only converts symbols that are known to cause phonemizer failures
        """
        changes = []

        # CRITICAL FIX: Handle quote characters that cause "in quat" pronunciation
        # Remove quotes entirely as they should be silent in speech
        quote_patterns = [
            (r'"', ''),  # Standard double quotes
            (r'"', ''),  # Left double quotation mark
            (r'"', ''),  # Right double quotation mark
            (r''', ''),  # Left single quotation mark (non-contraction)
            (r''', ''),  # Right single quotation mark (non-contraction)
        ]

        for pattern, replacement in quote_patterns:
            if pattern in text:
                original_text = text
                text = text.replace(pattern, replacement)
                if text != original_text:
                    changes.append(f"Removed quote characters to prevent 'in quat' pronunciation")
                    logger.debug(f"Removed quote character '{pattern}' from text")

        # Only convert symbols that consistently cause phonemizer word count mismatches
        # Most symbols can be left as-is without causing issues
        problematic_symbols = {
            # Add specific symbols here that cause issues
            # Currently keeping this minimal to preserve natural speech
        }

        for symbol, word in problematic_symbols.items():
            if symbol in text:
                # Be very careful about word boundaries to avoid changing word count
                # Only replace if it's truly standalone
                pattern = r'\s' + re.escape(symbol) + r'\s'
                if re.search(pattern, text):
                    text = re.sub(pattern, f' {word} ', text)
                    changes.append(f"Converted problematic symbol '{symbol}' to '{word}'")

        return text, changes

    def _fix_problematic_patterns_conservative(self, text: str) -> Tuple[str, List[str]]:
        """
        Conservative pattern fixing that preserves word count
        Only fixes patterns that are known to cause phonemizer failures
        """
        changes = []

        # Only fix patterns that consistently cause phonemizer word count mismatches
        # Focus on patterns that break phonemizer without changing word count
        conservative_patterns = [
            # Fix CSS-like patterns that confuse phonemizer
            (r'\b(\w+):\s*(\d+)(px|em|rem|%|pt)\b', r'\1 \2 \3', 'CSS property values'),

            # Fix excessive punctuation that breaks phonemizer
            (r'[.]{3,}', '...', 'excessive dots'),
            (r'[!]{2,}', '!', 'excessive exclamation marks'),
            (r'[?]{2,}', '?', 'excessive question marks'),

            # Fix problematic character sequences
            (r'[_]{2,}', '_', 'excessive underscores'),
            (r'[-]{3,}', '--', 'excessive dashes'),

            # Fix spacing issues around special characters (very conservative)
            # Only fix cases that are clearly problematic for phonemizer
            # Skip this for now to preserve word count

            # Skip number-letter combinations for now to preserve word count
            # These often don't cause phonemizer issues

            # Skip email processing for now to preserve word count
            # Emails are often handled fine by phonemizer as-is

            # Fix URL-like patterns (conservative - just add spaces)
            (r'www\.(\w+)\.(\w+)', r'www \1 dot \2', 'www URLs'),
        ]

        for pattern, replacement, description in conservative_patterns:
            if re.search(pattern, text):
                original_words = len(text.split())
                original_text = text
                text = re.sub(pattern, replacement, text)
                new_words = len(text.split())

                # Only apply if word count doesn't change dramatically
                if abs(new_words - original_words) <= 2:  # Allow small changes
                    changes.append(f"Fixed problematic {description.lower()}")
                else:
                    # Revert if word count changed too much
                    text = original_text
                    logger.debug(f"Skipped fixing {description} to preserve word count")

        return text, changes

    def _filter_emojis(self, text: str) -> Tuple[str, List[str]]:
        """
        Filter emojis from text to prevent verbalization
        Uses Unicode ranges to detect and remove emoji characters
        """
        changes = []
        original_text = text

        # Unicode ranges for emojis (comprehensive coverage)
        emoji_patterns = [
            r'[\U0001F600-\U0001F64F]',  # Emoticons
            r'[\U0001F300-\U0001F5FF]',  # Misc Symbols and Pictographs
            r'[\U0001F680-\U0001F6FF]',  # Transport and Map Symbols
            r'[\U0001F1E0-\U0001F1FF]',  # Regional Indicator Symbols (flags)
            r'[\U00002600-\U000026FF]',  # Misc symbols
            r'[\U00002700-\U000027BF]',  # Dingbats
            r'[\U0001F900-\U0001F9FF]',  # Supplemental Symbols and Pictographs
            r'[\U0001FA70-\U0001FAFF]',  # Symbols and Pictographs Extended-A
            r'[\U00002B50-\U00002B55]',  # Stars and other symbols
        ]

        # Combine all patterns
        combined_pattern = '|'.join(emoji_patterns)

        # Find all emojis in the text
        emojis_found = re.findall(combined_pattern, text)

        if emojis_found:
            # Replace emojis with configured replacement (default: empty string)
            replacement = self.emoji_replacement
            text = re.sub(combined_pattern, replacement, text)

            # Clean up any extra whitespace created by emoji removal
            text = re.sub(r'\s+', ' ', text).strip()

            changes.append(f"Filtered {len(emojis_found)} emoji(s): {', '.join(set(emojis_found))}")
            logger.debug(f"Filtered emojis from text: {emojis_found}")

        return text, changes

    def _handle_quote_characters(self, text: str) -> Tuple[str, List[str]]:
        """
        Handle quote characters to prevent "in quat" pronunciation

        This is a critical fix that removes quote characters entirely since they
        should be silent in speech synthesis. This prevents the phonemizer from
        interpreting quotes as "in quat" or similar pronunciations.

        IMPORTANT: We need to distinguish between quotes and contractions.
        - Remove quotes: 'Hello' -> Hello
        - Preserve contractions: I'm, don't, can't, etc.
        """
        changes = []
        original_text = text

        # Step 1: Handle double quotes (always remove)
        # CRITICAL FIX: Use proper Unicode quote characters (previous line had corrupted characters)
        double_quote_chars = [
            '"',      # U+0022 QUOTATION MARK (ASCII double quote)
            '\u201C', # U+201C LEFT DOUBLE QUOTATION MARK
            '\u201D'  # U+201D RIGHT DOUBLE QUOTATION MARK
        ]
        for quote_char in double_quote_chars:
            if quote_char in text:
                text = text.replace(quote_char, '')

        # Step 2: Handle single quotes more carefully
        # Remove single quotes that are NOT part of contractions

        # First, handle Unicode single quotes (always remove)
        # CRITICAL FIX: Use proper Unicode single quote characters (previous line had corrupted characters)
        unicode_single_quotes = [
            '\u2018',  # U+2018 LEFT SINGLE QUOTATION MARK
            '\u2019'   # U+2019 RIGHT SINGLE QUOTATION MARK
        ]
        for quote_char in unicode_single_quotes:
            if quote_char in text:
                text = text.replace(quote_char, '')

        # Handle ASCII single quotes - need to distinguish quotes from contractions
        if "'" in text:
            # CRITICAL FIX: Preserve contractions while removing quote characters
            # Common contractions that should be preserved
            contraction_patterns = [
                r"\bI'm\b", r"\byou're\b", r"\bhe's\b", r"\bshe's\b", r"\bit's\b",
                r"\bwe're\b", r"\bthey're\b", r"\bI've\b", r"\byou've\b", r"\bwe've\b",
                r"\bthey've\b", r"\bI'll\b", r"\byou'll\b", r"\bhe'll\b", r"\bshe'll\b",
                r"\bit'll\b", r"\bwe'll\b", r"\bthey'll\b", r"\bI'd\b", r"\byou'd\b",
                r"\bhe'd\b", r"\bshe'd\b", r"\bit'd\b", r"\bwe'd\b", r"\bthey'd\b",
                r"\bdon't\b", r"\bdoesn't\b", r"\bdidn't\b", r"\bwon't\b", r"\bwouldn't\b",
                r"\bcan't\b", r"\bcouldn't\b", r"\bshouldn't\b", r"\bmustn't\b",
                r"\bneedn't\b", r"\baren't\b", r"\bisn't\b", r"\bwasn't\b", r"\bweren't\b",
                r"\bhasn't\b", r"\bhaven't\b", r"\bhadn't\b"
            ]

            # Temporarily replace contractions with placeholders to protect them
            contraction_placeholders = {}
            placeholder_counter = 0

            for pattern in contraction_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    placeholder = f"__CONTRACTION_{placeholder_counter}__"
                    contraction_placeholders[placeholder] = match.group(0)
                    text = text.replace(match.group(0), placeholder, 1)
                    placeholder_counter += 1

            # Now remove quotes safely (contractions are protected)
            text = re.sub(r"\b'([^']*?)'\b", r'\1', text)  # 'word' -> word
            text = re.sub(r"^'([^']*)", r'\1', text)       # 'start -> start
            text = re.sub(r"([^'])'$", r'\1', text)        # end' -> end
            text = re.sub(r"\s'([^']*?)'(\s|$)", r' \1\2', text)  # ' word ' -> word
            text = re.sub(r"\s+'\s+", ' ', text)           # Remove isolated quotes
            text = re.sub(r"^'\s+", '', text)              # Remove quote at start
            text = re.sub(r"\s+'$", '', text)              # Remove quote at end
            text = re.sub(r"''", '', text)                 # Remove empty quotes ''
            text = re.sub(r"^'$", '', text)                # Remove single quote only

            # Restore contractions from placeholders
            for placeholder, contraction in contraction_placeholders.items():
                text = text.replace(placeholder, contraction)

        # Clean up any double spaces that might result from quote removal
        text = re.sub(r'\s+', ' ', text).strip()

        if text != original_text:
            changes.append("Removed quote characters to prevent 'in quat' pronunciation")
            logger.debug(f"Quote handling: '{original_text[:50]}...' -> '{text[:50]}...'")

        return text, changes

    def _decode_html_entities(self, text: str) -> Tuple[str, List[str]]:
        """
        Decode HTML entities to their actual characters

        This is critical for fixing the apostrophe issue where &#x27; should become '
        Must be done BEFORE any other text processing to avoid incorrect symbol conversion.
        """
        changes = []
        original_text = text

        # First, handle common HTML entities that might be causing issues
        # CRITICAL FIX: Use the same apostrophe character that TextNormalizer expects
        html_entities = {
            '&#x27;': "'",  # Hexadecimal apostrophe - use standard ASCII apostrophe
            '&#39;': "'",   # Decimal apostrophe - use standard ASCII apostrophe
            '&apos;': "'",  # Named apostrophe entity - use standard ASCII apostrophe
            '&quot;': '"',  # Double quote
            '&amp;': '&',   # Ampersand (but be careful with this one)
            '&lt;': '<',    # Less than
            '&gt;': '>',    # Greater than
            '&nbsp;': ' ',  # Non-breaking space
        }

        # Apply manual replacements for common problematic entities first
        for entity, replacement in html_entities.items():
            if entity in text:
                text = text.replace(entity, replacement)
                changes.append(f"Decoded HTML entity '{entity}' to '{replacement}'")

        # Use Python's html.unescape for any remaining entities
        try:
            decoded_text = html.unescape(text)
            if decoded_text != text:
                # Check if html.unescape found additional entities we didn't handle manually
                additional_changes = len([c for c in original_text if c == '&']) - len([c for c in decoded_text if c == '&'])
                if additional_changes > 0:
                    changes.append(f"Decoded {additional_changes} additional HTML entities")
                text = decoded_text
        except Exception as e:
            logger.warning(f"HTML entity decoding failed: {e}")
            # Continue with manual replacements only

        # Log the transformation for debugging
        if changes:
            logger.debug(f"HTML entity decoding: '{original_text[:50]}...' -> '{text[:50]}...'")

        return text, changes

    def _convert_numbers_to_words(self, text: str, aggressive: bool = False) -> Tuple[str, List[str]]:
        """Convert numbers to words with proper comma-separated number handling"""
        changes = []

        # Handle comma-separated numbers first (CRITICAL FIX)
        # Pattern for numbers with commas: 1,000 or 1,000,000 etc.
        comma_number_pattern = r'\b\d{1,3}(?:,\d{3})+\b'
        comma_matches = re.findall(comma_number_pattern, text)

        for match in comma_matches:
            try:
                # Remove commas and convert to int, then to words
                number_value = int(match.replace(',', ''))
                word_form = self._number_to_words(number_value)
                text = text.replace(match, word_form)
                changes.append(f"Converted comma-separated number '{match}' to '{word_form}'")
            except (ValueError, OverflowError):
                # If conversion fails, leave as-is but warn
                logger.warning(f"Could not convert comma-separated number: {match}")

        # Handle decimal numbers (e.g., 5.50, 3.14)
        decimal_pattern = r'\b\d+\.\d+\b'
        decimal_matches = re.findall(decimal_pattern, text)

        for match in decimal_matches:
            try:
                parts = match.split('.')
                integer_part = int(parts[0])
                decimal_part = parts[1]

                integer_words = self._number_to_words(integer_part)
                decimal_words = ' '.join(self.number_words_map.get(digit, digit) for digit in decimal_part)

                word_form = f"{integer_words} point {decimal_words}"
                text = text.replace(match, word_form)
                changes.append(f"Converted decimal number '{match}' to '{word_form}'")
            except (ValueError, IndexError):
                logger.warning(f"Could not convert decimal number: {match}")

        # Handle simple numbers from the map
        for number, word in self.number_words_map.items():
            pattern = r'\b' + re.escape(number) + r'\b'
            if re.search(pattern, text):
                text = re.sub(pattern, word, text)
                changes.append(f"Converted number '{number}' to '{word}'")

        if aggressive:
            # Convert remaining standalone digits
            def digit_to_word(match):
                digit = match.group(0)
                return self.number_words_map.get(digit, digit)

            original_text = text
            text = re.sub(r'\b\d\b', digit_to_word, text)
            if text != original_text:
                changes.append("Converted remaining digits to words")

        return text, changes

    def _number_to_words(self, number: int) -> str:
        """Convert an integer to its word representation"""
        if number == 0:
            return "zero"

        # Handle negative numbers
        if number < 0:
            return "negative " + self._number_to_words(-number)

        # Handle large numbers
        if number >= 1000000000:
            billions = number // 1000000000
            remainder = number % 1000000000
            result = self._number_to_words(billions) + " billion"
            if remainder > 0:
                result += " " + self._number_to_words(remainder)
            return result

        if number >= 1000000:
            millions = number // 1000000
            remainder = number % 1000000
            result = self._number_to_words(millions) + " million"
            if remainder > 0:
                result += " " + self._number_to_words(remainder)
            return result

        if number >= 1000:
            thousands = number // 1000
            remainder = number % 1000
            result = self._number_to_words(thousands) + " thousand"
            if remainder > 0:
                result += " " + self._number_to_words(remainder)
            return result

        if number >= 100:
            hundreds = number // 100
            remainder = number % 100
            result = self._number_to_words(hundreds) + " hundred"
            if remainder > 0:
                result += " " + self._number_to_words(remainder)
            return result

        # Handle numbers 0-99
        if number in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 30, 40, 50, 60, 70, 80, 90]:
            # Use the mapping for these numbers
            for num_str, word in self.number_words_map.items():
                if int(num_str) == number:
                    return word

        # Handle 21-99 that aren't in the map
        if number >= 21 and number <= 99:
            tens = (number // 10) * 10
            ones = number % 10
            tens_word = self.number_words_map.get(str(tens), str(tens))
            if ones == 0:
                return tens_word
            else:
                ones_word = self.number_words_map.get(str(ones), str(ones))
                return f"{tens_word} {ones_word}"

        # Fallback to string representation
        return str(number)

    def _convert_symbols_to_words(self, text: str) -> Tuple[str, List[str]]:
        """
        Convert symbols to words, but be smart about HTML entities

        Since HTML entity decoding happens first, we shouldn't see HTML entities here,
        but we'll be extra careful with & and # symbols just in case.
        """
        changes = []

        for symbol, word in self.symbol_words_map.items():
            if symbol in text:
                # Special handling for & and # to avoid breaking any remaining HTML entities
                if symbol == '&':
                    # Only convert & if it's not part of an HTML entity pattern (using pre-compiled pattern)
                    if self.html_entity_amp_pattern.search(text):
                        text = self.html_entity_amp_pattern.sub(f' {word} ', text)
                        changes.append(f"Converted standalone symbol '{symbol}' to '{word}'")
                elif symbol == '#':
                    # Only convert # if it's not part of &#... pattern (using pre-compiled pattern)
                    if self.html_entity_hash_pattern.search(text):
                        text = self.html_entity_hash_pattern.sub(f' {word} ', text)
                        changes.append(f"Converted standalone symbol '{symbol}' to '{word}'")
                elif symbol in ['"', '"', '"', ''', ''']:
                    # Special handling for quotes - remove them entirely (they should be silent)
                    # Don't add spaces when removing quotes to avoid changing word count
                    original_text = text
                    text = text.replace(symbol, word)  # word is empty string for quotes
                    if text != original_text:
                        changes.append(f"Removed quote character '{symbol}' to prevent pronunciation issues")
                else:
                    # For other symbols, do normal replacement
                    text = text.replace(symbol, f' {word} ')
                    changes.append(f"Converted symbol '{symbol}' to '{word}'")

        return text, changes
    
    def _fix_problematic_patterns(self, text: str) -> Tuple[str, List[str]]:
        """Fix patterns known to cause phonemizer issues"""
        changes = []
        
        for pattern, replacement, description in self.problematic_patterns:
            if re.search(pattern, text):
                text = re.sub(pattern, replacement, text)
                changes.append(f"Fixed {description.lower()}")
        
        return text, changes
    
    def _clean_whitespace_and_punctuation(self, text: str) -> str:
        """Clean up whitespace and punctuation (using pre-compiled patterns)"""
        # Remove multiple spaces (using pre-compiled pattern)
        text = self.whitespace_pattern.sub(' ', text)

        # Fix spacing around punctuation - CRITICAL FIX: Only remove EXCESSIVE spaces, preserve normal spacing
        # OLD BUG: text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # This removed ALL spaces before punctuation!
        # NEW FIX: Only remove multiple spaces (2+) before punctuation, preserve single spaces
        text = re.sub(r'\s{2,}([,.!?;:])', r' \1', text)  # Multiple spaces -> single space before punctuation
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)  # Ensure space after sentence-ending punctuation

        # Remove excessive punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)

        return text.strip()
    
    def _calculate_confidence_score(self, processed_text: str, original_text: str) -> float:
        """Calculate confidence score for phonemizer success"""
        score = 1.0
        
        # Penalize for remaining problematic characters
        problematic_chars = set('@#$%^&*()_+={}[]|\\:";\'<>?/~`')
        for char in processed_text:
            if char in problematic_chars:
                score -= 0.05
        
        # Penalize for remaining numbers
        if re.search(r'\d', processed_text):
            score -= 0.1
        
        # Penalize for very long words (likely to cause issues)
        words = processed_text.split()
        for word in words:
            if len(word) > 15:
                score -= 0.1
        
        # Bonus for proper sentence structure
        if re.search(r'[.!?]$', processed_text.strip()):
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _detect_potential_issues(self, text: str) -> List[str]:
        """Detect potential issues that might still cause problems with enhanced edge case detection"""
        warnings = []

        # Enhanced number detection (only warn if they're likely problematic)
        if re.search(r'\d+', text):
            # Count standalone numbers vs numbers in context
            standalone_numbers = len(re.findall(r'\b\d+\b', text))
            if standalone_numbers > 3:
                warnings.append("Contains many standalone numbers that might cause phonemizer issues")
            elif re.search(r'\d{4,}', text):  # Long numbers like years, IDs
                warnings.append("Contains long numbers that might cause phonemizer issues")
            elif re.search(r'\d+[a-zA-Z]+|\d+\.\d+', text):  # Mixed alphanumeric or decimals
                warnings.append("Contains complex numbers that might cause phonemizer issues")

        # Enhanced special character detection (be more specific about problematic ones)
        problematic_chars = re.findall(r'[^\w\s\.,!?;:\'"()-]', text)
        if problematic_chars:
            unique_chars = set(problematic_chars)
            if len(unique_chars) > 5:
                warnings.append("Contains many special characters that might cause phonemizer issues")
            elif any(char in '@#$%^&*+={}[]|\\<>' for char in unique_chars):
                warnings.append("Contains special characters that might cause phonemizer issues")

        # Enhanced long word detection (likely URLs, emails, or technical terms)
        words = text.split()
        long_words = [w for w in words if len(w) > 20]
        if long_words:
            warnings.append(f"Contains very long words: {', '.join(long_words[:2])}")

        # Check for code-like patterns (CSS, HTML, programming syntax)
        if re.search(r'[{}();].*[{}();]', text) or re.search(r'\w+:\s*\w+;', text):
            warnings.append("Contains code-like patterns that might confuse phonemizer")

        # Check for URLs or email patterns
        if re.search(r'https?://|www\.|@\w+\.\w+', text):
            warnings.append("Contains URLs or email addresses that might cause issues")

        # Check for excessive punctuation
        punct_count = len(re.findall(r'[^\w\s]', text))
        word_count = len(text.split())
        if word_count > 0 and punct_count / word_count > 0.5:
            warnings.append("Contains excessive punctuation that might cause issues")

        # Check for repeated characters (stuttering or emphasis)
        if re.search(r'(.)\1{4,}', text):
            warnings.append("Contains repeated characters that might cause issues")

        # Check for very long text
        if len(text) > 500:
            warnings.append("Text is very long, consider breaking into smaller chunks")

        # Check for mixed languages or scripts
        if re.search(r'[^\x00-\x7F]', text):  # Non-ASCII characters
            warnings.append("Contains non-ASCII characters that might need special handling")

        return warnings

# Global preprocessor instance - load config
def _get_global_config():
    """Get global configuration for phonemizer preprocessor"""
    try:
        import json
        from pathlib import Path
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                logger.debug(f"Global config loaded: expand_contractions={config.get('text_processing', {}).get('expand_contractions', 'not set')}")
                return config
    except Exception as e:
        logger.warning(f"Failed to load global config: {e}")
    return {}

def _create_global_preprocessor():
    """Create global preprocessor instance with current config"""
    config = _get_global_config()
    instance = PhonemizationPreprocessor(config=config)
    logger.debug(f"Global preprocessor created: expand_all={instance.expand_all}, preserve_natural={instance.preserve_natural}")
    return instance

# Create global instance
phonemizer_preprocessor = _create_global_preprocessor()
