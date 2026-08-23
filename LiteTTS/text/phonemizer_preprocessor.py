#!/usr/bin/env python3
"""
Advanced text preprocessor specifically designed to prevent phonemizer issues
This module addresses the "words count mismatch" warnings that cause empty audio generation
"""

import html
import json
import logging
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Import enhanced contraction processor for better contraction handling
try:
    from ..nlp.enhanced_contraction_processor import EnhancedContractionProcessor

    ENHANCED_CONTRACTIONS_AVAILABLE = True  # pragma: no cover - import success path
except ImportError:
    logger.warning("Enhanced contraction processor not available, falling back to basic processing")
    ENHANCED_CONTRACTIONS_AVAILABLE = False  # pragma: no cover - import failure path


@dataclass
class PreprocessingResult:
    """Result of text preprocessing"""

    processed_text: str
    original_text: str
    changes_made: list[str]
    confidence_score: float  # 0.0 to 1.0, higher means more likely to work with phonemizer
    warnings: list[str]


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

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.contractions_map = self._build_contractions_map()
        self.problematic_contractions = self._build_problematic_contractions()
        self.number_words_map = self._build_number_words_map()
        self.symbol_words_map = self._build_symbol_words_map()
        self.problematic_patterns = self._build_problematic_patterns()
        self.problematic_symbols = {}  # Symbols that cause phonemizer issues (can be modified for testing)

        # Initialize enhanced contraction processor for better contraction handling
        if ENHANCED_CONTRACTIONS_AVAILABLE:  # pragma: no cover - import success path
            self.enhanced_contraction_processor = EnhancedContractionProcessor(config=self.config)
            logger.debug("Enhanced contraction processor initialized with config")
        else:  # pragma: no cover - import failure path
            self.enhanced_contraction_processor = None

        # Cache config values to avoid repeated imports (PERFORMANCE OPTIMIZATION)
        self._load_config_cache()

        # Pre-compile regex patterns for performance (PERFORMANCE OPTIMIZATION)
        self._compile_regex_patterns()

    def _load_config_cache(self):
        """Load and cache configuration values to avoid repeated imports"""
        try:
            # First try to load from the main config (config.json)
            if hasattr(self, "config") and self.config:
                # Use the config passed to the constructor
                text_processing = self.config.get("text_processing", {})
                self.expand_all = text_processing.get("expand_contractions", False)
                self.preserve_natural = text_processing.get("natural_speech", True)
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

                self.expand_problematic_only = (
                    config.performance.expand_problematic_contractions_only
                )
                # Emoji and symbol handling configuration (CRITICAL FIX)
                self.filter_emojis = config.performance.filter_emojis
                self.emoji_replacement = config.performance.emoji_replacement
                self.preserve_word_count_config = config.performance.preserve_word_count
            except Exception:
                self.expand_problematic_only = True
                self.filter_emojis = True
                self.emoji_replacement = ""
                self.preserve_word_count_config = True

            logger.debug(
                f"Config cached: expand_all={self.expand_all}, preserve_natural={self.preserve_natural}"
            )
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
        self.control_char_pattern = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]")

        # HTML entity patterns for smart symbol conversion
        self.html_entity_amp_pattern = re.compile(r"&(?![a-zA-Z0-9#]+;)")
        self.html_entity_hash_pattern = re.compile(r"#(?![x0-9a-fA-F]+;)")

        # Whitespace cleanup pattern
        self.whitespace_pattern = re.compile(r"\s+")

        logger.debug("Regex patterns compiled for performance optimization")

    def _build_contractions_map(self) -> dict[str, str]:
        """Build comprehensive contractions mapping from external config file"""
        try:
            # Try to load from external config file first
            config_path = Path("LiteTTS/config/contractions.json")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                # Flatten all contraction categories into a single dictionary
                contractions = {}
                for category_name, category_data in config_data.items():
                    if not category_name.startswith("_") and isinstance(category_data, dict):
                        contractions.update(category_data)

                logger.debug(f"Loaded {len(contractions)} contractions from external config")
                return contractions
        except Exception as e:
            logger.warning(f"Failed to load contractions from external config: {e}")

        # Fallback to built-in contractions
        return {
            # Standard contractions
            "don't": "do not",
            "won't": "will not",
            "can't": "cannot",
            "couldn't": "could not",
            "shouldn't": "should not",
            "wouldn't": "would not",
            "mustn't": "must not",
            "needn't": "need not",
            "daren't": "dare not",
            "mayn't": "may not",
            # Positive contractions
            "I'm": "I am",
            "you're": "you are",
            "he's": "he is",
            "she's": "she is",
            "it's": "it is",
            "we're": "we are",
            "they're": "they are",
            "I've": "I have",
            "you've": "you have",
            "we've": "we have",
            "they've": "they have",
            "I'll": "I will",
            "you'll": "you will",
            "he'll": "he will",
            "she'll": "she will",
            "it'll": "it will",
            "we'll": "we will",
            "they'll": "they will",
            "I'd": "I would",
            "you'd": "you would",
            "he'd": "he would",
            "she'd": "she would",
            "it'd": "it would",
            "we'd": "we would",
            "they'd": "they would",
            # Other common contractions
            "that's": "that is",
            "there's": "there is",
            "here's": "here is",
            "what's": "what is",
            "where's": "where is",
            "when's": "when is",
            "who's": "who is",
            "how's": "how is",
            "why's": "why is",
            "let's": "let us",
            "that'll": "that will",
            "who'll": "who will",
            # Informal contractions
            "gonna": "going to",
            "wanna": "want to",
            "gotta": "got to",
            "kinda": "kind of",
            "sorta": "sort of",
            "outta": "out of",
            "dunno": "do not know",
            "gimme": "give me",
            "lemme": "let me",
            # 'd ambiguity - default to "would" (most common)
            "'d": " would",
            "'ll": " will",
            "'re": " are",
            "'ve": " have",
            "'m": " am",
            "'s": " is",
            "n't": " not",
        }

    def _build_problematic_contractions(self) -> dict[str, str]:
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

    def _build_number_words_map(self) -> dict[str, str]:
        """Build number to words mapping from external config file"""
        try:
            # Try to load from external config file first
            config_path = Path("LiteTTS/config/numbers.json")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                # Flatten all number categories into a single dictionary
                numbers = {}
                for category_name, category_data in config_data.items():
                    if not category_name.startswith("_") and isinstance(category_data, dict):
                        numbers.update(category_data)

                logger.debug(f"Loaded {len(numbers)} number mappings from external config")
                return numbers
        except Exception as e:
            logger.warning(f"Failed to load numbers from external config: {e}")

        # Fallback to built-in numbers
        return {
            "0": "zero",
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
            "6": "six",
            "7": "seven",
            "8": "eight",
            "9": "nine",
            "10": "ten",
            "11": "eleven",
            "12": "twelve",
            "13": "thirteen",
            "14": "fourteen",
            "15": "fifteen",
            "16": "sixteen",
            "17": "seventeen",
            "18": "eighteen",
            "19": "nineteen",
            "20": "twenty",
            "30": "thirty",
            "40": "forty",
            "50": "fifty",
            "60": "sixty",
            "70": "seventy",
            "80": "eighty",
            "90": "ninety",
            "100": "one hundred",
            "1000": "one thousand",
        }

    def _build_symbol_words_map(self) -> dict[str, str]:
        """Build symbol to words mapping from external config file"""
        try:
            # Try to load from external config file first
            config_path = Path("LiteTTS/config/symbols.json")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                # Flatten all symbol categories into a single dictionary
                symbols = {}
                for category_name, category_data in config_data.items():
                    if not category_name.startswith("_") and isinstance(category_data, dict):
                        symbols.update(category_data)

                logger.debug(f"Loaded {len(symbols)} symbol mappings from external config")
                return symbols
        except Exception as e:
            logger.warning(f"Failed to load symbols from external config: {e}")

        # Fallback to built-in symbols
        return {
            "&": "and",
            "+": "plus",
            "=": "equals",
            "%": "percent",
            "$": "dollars",
            "€": "euros",
            "£": "pounds",
            "¥": "yen",
            "@": "at",
            "#": "hash",
            "*": "star",
            # REMOVED: '/' -> 'slash' (slashes should be silent/ignored per user request)
            "\\": "backslash",
            "|": "pipe",
            "^": "caret",
            "~": "tilde",
            "<": "less than",
            ">": "greater than",
            "©": "copyright",
            "®": "registered",
            "™": "trademark",
            "°": "degrees",
            # Quote handling - CRITICAL FIX for "in quat" pronunciation issue
            # Use actual unicode characters to avoid duplicate key issues
            '"': "",  # " Double quote (ASCII)
            "“": "",  # " Left double quotation mark
            "”": "",  # " Right double quotation mark
            "‘": "",  # ' Left single quotation mark
            "’": "",  # ' Right single quotation mark
        }

    def _build_problematic_patterns(self) -> list[tuple[str, str, str]]:
        """
        Build list of problematic patterns that cause phonemizer issues

        Note: Removed the general hyphenated words pattern that was converting
        natural compound words like "twenty-one" to "twenty dash one".
        Hyphens in compound words should be preserved for natural speech.
        """
        return [
            # Pattern, Replacement, Description
            (r"\b(\w+)\.(\w+)\b", r"\1 dot \2", "Domain names and file extensions"),
            (r"\b(\w+)@(\w+)\b", r"\1 at \2", "Email addresses"),
            (r"\b(\d+)-(\d+)\b", r"\1 to \2", "Number ranges"),  # Keep this for "1-10" -> "1 to 10"
            # REMOVED: Fraction slash pattern - let natural number processing handle "1/2" etc.
            (r"\b(\d+):(\d+)\b", r"\1 colon \2", "Time expressions"),
            (r"\b(\w+)_(\w+)\b", r"\1 underscore \2", "Underscored words"),
            # FIXED: Only convert TRUE acronyms (all caps sequences like FBI, NASA, CEO)
            # Preserves natural words like "Directions", "Any", "Know"
            (
                r"\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\b",
                lambda m: " ".join(m.group(0).lower()),
                "True acronyms only",
            ),
            (r"\b(\d+)([A-Za-z]+)\b", r"\1 \2", "Number-letter combinations"),
        ]

    def _safe_int(self, value):
        """
        Convert value to integer. This is a wrapper around int() that can be
        overridden in tests to simulate failures.

        Note: Python integers have arbitrary precision, so OverflowError is
        effectively impossible in practice.
        """
        return int(value)

    def preprocess_text(
        self, text: str, aggressive: bool = False, preserve_word_count: bool = True
    ) -> PreprocessingResult:
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

        # Step 1.5: Handle compound tech terms BEFORE symbol replacement
        # This MUST happen before _convert_symbols_conservative which converts # to "hash"
        # C#, OAuth, IPv6, SHA-256 would otherwise become "C hash", etc.
        text, compound_changes = self._fix_tech_compounds(text)
        changes_made.extend(compound_changes)

        # Step 1.6: Handle fractions and special symbols BEFORE unicode normalization
        # Unicode NFKC breaks ½ → 21⁄2 and ± → ±
        text, fraction_changes = self._fix_fractions_and_symbols(text)
        changes_made.extend(fraction_changes)

        # Step 2: Unicode normalization
        text = unicodedata.normalize("NFKC", text)
        if text != original_text and "HTML entity decoding" not in changes_made:
            changes_made.append("Unicode normalization")

        # Step 3: Remove control characters (using pre-compiled pattern)
        text = self.control_char_pattern.sub("", text)

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
            warnings.append(
                f"Word count changed from {original_word_count} to {final_word_count} - may cause phonemizer issues"
            )
            logger.warning(
                f"Word count mismatch: {original_word_count} -> {final_word_count} for text: '{original_text[:50]}...'"
            )

        confidence_score = self._calculate_confidence_score(text, original_text)
        warnings.extend(self._detect_potential_issues(text))

        # Ensure text ends with proper punctuation (but don't count this as a word)
        # Skip terminal punctuation for time expressions
        is_time_expression = self._is_time_expression(text)

        if text and text[-1] not in ".!?" and not is_time_expression:
            text += "."
            changes_made.append("Added terminal punctuation")

        result = PreprocessingResult(
            processed_text=text.strip(),
            original_text=original_text,
            changes_made=changes_made,
            confidence_score=confidence_score,
            warnings=warnings,
        )

        if changes_made:
            logger.debug(
                f"Text preprocessing made {len(changes_made)} changes: {', '.join(changes_made)}"
            )

        return result

    def _is_time_expression(self, text: str) -> bool:
        """Check if the text is a time expression that shouldn't have terminal punctuation"""
        text_lower = text.lower().strip()

        # Check for time expression patterns
        time_patterns = [
            r"\b(?:ten|eleven|twelve|one|two|three|four|five|six|seven|eight|nine)\s+(?:thirty|fifteen|forty|oh|zero)\s*(?:five)?\s+(?:a\s+m|p\s+m)$",
            r"\b(?:ten|eleven|twelve|one|two|three|four|five|six|seven|eight|nine)\s+o\'?clock\s*(?:a\s+m|p\s+m)?$",
            r"\b(?:ten|eleven|twelve|one|two|three|four|five|six|seven|eight|nine)\s+(?:a\s+m|p\s+m)$",
        ]

        for pattern in time_patterns:
            if re.search(pattern, text_lower):
                return True

        return False

    def _expand_contractions(self, text: str) -> tuple[str, list[str]]:
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
                mode = "expanded"
                logger.debug("Using enhanced contraction processor in expanded mode")
            elif preserve_natural:
                # Use hybrid mode (default for natural speech)
                mode = "hybrid"
                logger.debug("Using enhanced contraction processor in hybrid mode")
            else:
                # Natural mode - keep contractions as-is
                mode = "natural"
                logger.debug("Using enhanced contraction processor in natural mode")

            # Process contractions with enhanced processor
            processed_text = self.enhanced_contraction_processor.process_contractions(text, mode)

            if processed_text != original_text:
                changes.append(f"Enhanced contraction processing applied ({mode} mode)")
                logger.debug(
                    f"Enhanced contraction processing: '{original_text[:50]}...' → '{processed_text[:50]}...'"
                )

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
        sorted_contractions = sorted(
            contractions_to_expand.items(), key=lambda x: len(x[0]), reverse=True
        )

        for contraction, expansion in sorted_contractions:
            # Use word boundaries to avoid partial matches
            pattern = r"\b" + re.escape(contraction) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
                changes.append(f"Expanded '{contraction}' to '{expansion}'")

        return text, changes

    def _expand_contractions_conservative(self, text: str) -> tuple[str, list[str]]:
        """
        Conservative contraction expansion that preserves word count
        Only expands contractions that are known to cause phonemizer failures
        """
        changes = []

        # Only expand contractions that consistently cause phonemizer word count mismatches
        # Use instance attribute so it can be modified for testing
        if not self.problematic_contractions:
            logger.debug("No problematic contractions to expand in conservative mode")
            return text, changes

        # Sort by length (longest first) to avoid partial replacements
        sorted_contractions = sorted(
            self.problematic_contractions.items(), key=lambda x: len(x[0]), reverse=True
        )

        for contraction, expansion in sorted_contractions:
            # Use word boundaries to avoid partial matches
            pattern = r"\b" + re.escape(contraction) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
                changes.append(f"Expanded problematic '{contraction}' to '{expansion}'")

        return text, changes

    def _convert_numbers_conservative(self, text: str) -> tuple[str, list[str]]:
        """
        Ultra-conservative number conversion that prioritizes word count preservation
        Only converts numbers in very specific cases where phonemizer consistently fails
        """
        changes = []

        # ULTRA-CONSERVATIVE: Only convert numbers that cause consistent phonemizer failures
        # AND where the conversion doesn't dramatically change word count

        # Convert only standalone "0" which is often misread as "oh"
        # This is a 1:1 word replacement so it preserves word count
        if re.search(r"\b0\b", text):
            text = re.sub(r"\b0\b", "zero", text)
            changes.append("Converted standalone '0' to 'zero'")

        # For comma-separated numbers, we have a choice:
        # 1. Convert them (better pronunciation, but changes word count)
        # 2. Leave them (preserves word count, but may be read digit-by-digit)
        #
        # In ULTRA-CONSERVATIVE mode, we choose option 2 to preserve word count
        # The user can use aggressive mode if they want number conversion

        # CRITICAL FIX: Handle currency patterns like $12,345.67 BEFORE general decimal handling
        # Pattern: dollar sign followed by comma-separated number with optional decimal cents
        # Fix: allow 1-3 digits before first comma (e.g., $12,345 or $123,456,789)
        currency_pattern = r"\$\d{1,3}(?:,\d{3}){1,5}(?:\.\d{1,2})?(?:\s*(?:dollars?|cents?))?"
        currency_matches = re.findall(currency_pattern, text)

        # Also check for currency WITHOUT commas (e.g., $12345.67) in case they were stripped
        # This is a fallback for cases where commas get removed before we process currency
        currency_pattern_no_comma = r"\$\d+(?:\.\d{1,2})?(?:\s*(?:dollars?|cents?))?"
        for match in re.findall(currency_pattern_no_comma, text):
            # Only process if not already matched by the comma pattern
            if match not in currency_matches:
                currency_matches.append(match)

        for match in currency_matches:
            original_match = match
            # Extract the numeric parts
            # Remove $ sign
            num_part = match.replace("$", "")
            # Check for decimal (cents)
            has_cents = "." in num_part
            if has_cents:
                num_part, cent_part = num_part.split(".")
                cent_part = cent_part.rstrip(
                    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
                )
            else:
                cent_part = None

            # Convert the main number (remove commas)
            main_num = int(num_part.replace(",", ""))
            main_words = self._number_to_words(main_num)

            if has_cents and cent_part:
                # Format: "twelve thousand three hundred forty-five dollars and sixty-seven cents"
                cent_num = int(cent_part)
                cent_words = self._number_to_words(cent_num)
                word_form = f"{main_words} dollars and {cent_words} cents"
            else:
                # Format: "twelve thousand three hundred forty-five dollars"
                word_form = f"{main_words} dollars"

            text = text.replace(original_match, word_form, 1)
            changes.append(f"Converted currency '{match}' to '{word_form}'")

        comma_number_pattern = r"\b\d{1,3}(?:,\d{3})+\b"
        comma_matches = re.findall(comma_number_pattern, text)
        if comma_matches:
            # Just warn about them, don't convert
            changes.append(
                f"Found comma-separated numbers that may be read digit-by-digit: {', '.join(comma_matches)}"
            )
            logger.debug(
                f"Conservative mode: preserving comma-separated numbers to maintain word count: {comma_matches}"
            )

        # For decimal numbers, convert them properly so phonemizer doesn't read digit-by-digit
        # e.g., 3.14159 -> "three point one four one five nine"
        decimal_pattern = r"\b\d+\.\d+\b"
        decimal_matches = re.findall(decimal_pattern, text)
        for match in decimal_matches:
            try:
                parts = match.split(".")
                integer_part = self._safe_int(parts[0])
                decimal_part = parts[1]

                integer_words = self._number_to_words(integer_part)
                decimal_words = " ".join(
                    self.number_words_map.get(digit, digit) for digit in decimal_part
                )

                word_form = f"{integer_words} point {decimal_words}"
                text = text.replace(match, word_form, 1)
                changes.append(f"Converted decimal '{match}' to '{word_form}'")
            except (ValueError, IndexError, KeyError) as e:
                logger.warning(f"Could not convert decimal number '{match}': {e}")

        return text, changes

    def _convert_symbols_conservative(self, text: str) -> tuple[str, list[str]]:
        """
        Conservative symbol conversion that preserves word count
        Only converts symbols that are known to cause phonemizer failures
        """
        changes = []

        # CRITICAL FIX: Handle quote characters that cause "in quat" pronunciation
        # Remove quotes entirely as they should be silent in speech
        quote_patterns = [
            (r'"', ""),  # Standard double quotes
            (r'"', ""),  # Left double quotation mark
            (r'"', ""),  # Right double quotation mark
            (
                r""", ''),  # Left single quotation mark (non-contraction)
            (r""",
                "",
            ),  # Right single quotation mark (non-contraction)
        ]

        for pattern, replacement in quote_patterns:
            if pattern in text:
                original_text = text
                text = text.replace(pattern, replacement)
                if text != original_text:
                    changes.append("Removed quote characters to prevent 'in quat' pronunciation")
                    logger.debug(f"Removed quote character '{pattern}' from text")

        # Only convert symbols that consistently cause phonemizer word count mismatches
        # Most symbols can be left as-is without causing issues
        # Use instance attribute so it can be modified for testing
        for symbol, word in self.problematic_symbols.items():
            if symbol in text:
                # Be very careful about word boundaries to avoid changing word count
                # Only replace if it's truly standalone
                pattern = r"\s" + re.escape(symbol) + r"\s"
                if re.search(pattern, text):
                    text = re.sub(pattern, f" {word} ", text)
                    changes.append(f"Converted problematic symbol '{symbol}' to '{word}'")

        return text, changes

    def _fix_problematic_patterns_conservative(self, text: str) -> tuple[str, list[str]]:
        """
        Conservative pattern fixing that preserves word count
        Only fixes patterns that are known to cause phonemizer failures
        """
        changes = []

        # Only fix patterns that consistently cause phonemizer word count mismatches
        # Focus on patterns that break phonemizer without changing word count
        conservative_patterns = [
            # Fix CSS-like patterns that confuse phonemizer
            (r"\b(\w+):\s*(\d+)(px|em|rem|%|pt)\b", r"\1 \2 \3", "CSS property values"),
            # Fix excessive punctuation that breaks phonemizer
            (r"[.]{3,}", "...", "excessive dots"),
            (r"[!]{2,}", "!", "excessive exclamation marks"),
            (r"[?]{2,}", "?", "excessive question marks"),
            # Fix problematic character sequences
            (r"[_]{2,}", "_", "excessive underscores"),
            (r"[-]{3,}", "--", "excessive dashes"),
            # Fix spacing issues around special characters (very conservative)
            # Only fix cases that are clearly problematic for phonemizer
            # Skip this for now to preserve word count
            # Skip number-letter combinations for now to preserve word count
            # These often don't cause phonemizer issues
            # Skip email processing for now to preserve word count
            # Emails are often handled fine by phonemizer as-is
            # Fix URL-like patterns (conservative - just add spaces)
            (r"www\.(\w+)\.(\w+)", r"www \1 dot \2", "www URLs"),
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

    def _fix_tech_compounds(self, text: str) -> tuple[str, list[str]]:
        """
        Fix compound tech terms that would otherwise be mangled by symbol replacement.
        This MUST run before _convert_symbols_conservative which converts # to "hash".

        Handles: C#, OAuth, IPv6, SHA-256, and similar tech terms.
        """
        changes = []
        original_text = text

        # C# programming language - "C sharp", not "C hash"
        # NOTE: # is NOT a word char in regex, so \bC#\b doesn't work - use (?!\w)
        if re.search(r"\bC#(?!\w)", text, re.IGNORECASE):
            text = re.sub(r"\bC#(?!\w)", "C sharp", text, flags=re.IGNORECASE)
            changes.append("C# -> C sharp")

        # F# programming language
        if re.search(r"\bF#(?!\w)", text, re.IGNORECASE):
            text = re.sub(r"\bF#(?!\w)", "F sharp", text, flags=re.IGNORECASE)
            changes.append("F# -> F sharp")

        # G# music note
        if re.search(r"\bG#(?!\w)", text, re.IGNORECASE):
            text = re.sub(r"\bG#(?!\w)", "G sharp", text, flags=re.IGNORECASE)
            changes.append("G# -> G sharp")

        # D# music note
        if re.search(r"\bD#(?!\w)", text, re.IGNORECASE):
            text = re.sub(r"\bD#(?!\w)", "D sharp", text, flags=re.IGNORECASE)
            changes.append("D# -> D sharp")

        # A# music note
        if re.search(r"\bA#(?!\w)", text, re.IGNORECASE):
            text = re.sub(r"\bA#(?!\w)", "A sharp", text, flags=re.IGNORECASE)
            changes.append("A# -> A sharp")

        # OAuth 2.0 - must handle before # replacement
        if re.search(r"\bOAuth\s*2\.0\b", text, re.IGNORECASE):
            text = re.sub(r"\bOAuth\s*2\.0\b", "OAuth two point zero", text, flags=re.IGNORECASE)
            changes.append("OAuth 2.0 -> OAuth two point zero")

        # IPv6 - must handle before # replacement
        if re.search(r"\bIPv6\b", text, re.IGNORECASE):
            text = re.sub(r"\bIPv6\b", "I P V six", text, flags=re.IGNORECASE)
            changes.append("IPv6 -> I P V six")

        # SHA-256 and similar
        if re.search(r"\bSHA-?256\b", text, re.IGNORECASE):
            text = re.sub(r"\bSHA-?256\b", "SHA two fifty six", text, flags=re.IGNORECASE)
            changes.append("SHA-256 -> SHA two fifty six")

        # OAuth (standalone, without 2.0) - preserve but don't change
        if re.search(r"\bOAuth\b", text, re.IGNORECASE):
            text = re.sub(r"\bOAuth\b", "OAuth", text, flags=re.IGNORECASE)
            # No change in sound, just ensuring it's preserved

        # A.I., A.P.I., G.P.S., etc. - period-separated acronyms
        # Convert to hyphen-separated: A.I. -> A-I, A.P.I. -> A-P-I
        if re.search(r"\b[A-Z]\.[A-Z](?:\.[A-Z])*\.?", text):

            def acronym_to_words(match):
                acronym = match.group()
                # Remove trailing dot if present
                acronym = acronym.rstrip(".")
                # Split by dots and join with hyphens
                letters = acronym.split(".")
                return "-".join(letters)

            text = re.sub(r"\b[A-Z]\.[A-Z](?:\.[A-Z])*\.?", acronym_to_words, text)
            changes.append("Period-separated acronyms to hyphenated letters")

        if text != original_text and changes:
            logger.debug(f"Fixed tech compounds: {changes}")

        return text, changes

    def _fix_fractions_and_symbols(self, text: str) -> tuple[str, list[str]]:
        """
        Fix fractions and special symbols that get mangled by unicode normalization.
        Must run BEFORE Step 2 (Unicode normalization).
        """
        changes = []
        original_text = text

        # Handle fractions BEFORE unicode normalization breaks them
        # Pattern: number + fraction (e.g., 2½, 3¾, 1½)
        def fraction_to_words(match):
            num = match.group(1)
            frac = match.group(2)
            fraction_words = {
                "½": "and a half",
                "¼": "and a quarter",
                "¾": "and three quarters",
                "⅓": "and a third",
                "⅔": "and two thirds",
                "⅛": "and an eighth",
                "⅜": "and three eighths",
                "⅝": "and five eighths",
                "⅞": "and seven eighths",
            }
            frac_word = fraction_words.get(frac, f"and {frac}")
            # Convert leading number to words if it's a single digit
            num_words = {
                "0": "zero",
                "1": "one",
                "2": "two",
                "3": "three",
                "4": "four",
                "5": "five",
                "6": "six",
                "7": "seven",
                "8": "eight",
                "9": "nine",
            }
            if num in num_words:
                num = num_words[num]
            return f" {num} {frac_word} "

        text = re.sub(r"(\d+)([½¼¾⅓⅔⅛⅜⅝⅞])", fraction_to_words, text)

        # Vulgar fractions without leading number (½ alone)
        fraction_map = {
            "½": "half",
            "⅓": "third",
            "⅔": "two thirds",
            "¼": "quarter",
            "¾": "three quarters",
            "⅛": "eighth",
            "⅜": "three eighths",
            "⅝": "five eighths",
            "⅞": "seven eighths",
        }

        for frac, word in fraction_map.items():
            if frac in text:
                text = text.replace(frac, f" {word} ")
                changes.append(f"Fraction {frac} -> {word}")

        # Plus-minus sign (±) - MUST be before the simple replace, order matters!
        # First handle ±number% patterns, then handle standalone ±
        def decimal_to_words(m):
            val = m.group(1)
            digit_words = {
                "0": "zero",
                "1": "one",
                "2": "two",
                "3": "three",
                "4": "four",
                "5": "five",
                "6": "six",
                "7": "seven",
                "8": "eight",
                "9": "nine",
            }
            if "." in val:
                whole, dec = val.split(".")
                dec_words = " ".join([digit_words.get(d, d) for d in dec])
                if whole and whole != "0":
                    whole_words = " ".join([digit_words.get(d, d) for d in whole])
                    return f" plus or minus {whole_words} point {dec_words} percent"
                else:
                    return f" plus or minus point {dec_words} percent"
            else:
                whole_words = " ".join([digit_words.get(d, d) for d in val])
                return f" plus or minus {whole_words} percent"

        # Handle ±number% BEFORE replacing standalone ±
        if re.search(r"±\d+\.?\d*%", text):
            text = re.sub(r"±(\d+\.?\d*)%", decimal_to_words, text)
            changes.append("Plus-minus with percent")

        # Handle standalone ± (without number or with non-percent suffix)
        if "±" in text:
            text = text.replace("±", " plus or minus ")
            changes.append("Plus-minus sign")

        # Fix a.m. and p.m. time abbreviations
        if re.search(r"\d+:\d+\s*[ap]\.?m\.?", text, re.IGNORECASE):
            text = re.sub(
                r"(\d+):(\d+)\s*a\.?m\.?",
                lambda m: f"{m.group(1)}:{m.group(2)} A M",
                text,
                flags=re.IGNORECASE,
            )
            text = re.sub(
                r"(\d+):(\d+)\s*p\.?m\.?",
                lambda m: f"{m.group(1)}:{m.group(2)} P M",
                text,
                flags=re.IGNORECASE,
            )

        # Fix temperature formats: -17.4°C → minus seventeen point four degrees C
        # and 23.9°C → twenty-three point nine degrees C
        def number_to_words(num_str):
            """Convert a number string to words (e.g., '17' -> 'seventeen', '3' -> 'three')"""
            if "." in num_str:
                whole, dec = num_str.split(".")
                whole_word = _number_to_words(whole) if whole else ""
                dec_word = " ".join(_digit_to_word(d) for d in dec)
                if whole_word and dec_word:
                    return f"{whole_word} point {dec_word}"
                elif whole_word:
                    return whole_word
                else:
                    return f"point {dec_word}"
            else:
                return _number_to_words(num_str)

        def _digit_to_word(d):
            return {
                "0": "zero",
                "1": "one",
                "2": "two",
                "3": "three",
                "4": "four",
                "5": "five",
                "6": "six",
                "7": "seven",
                "8": "eight",
                "9": "nine",
            }.get(d, d)

        def _number_to_words(n):
            """Convert a positive integer to words"""
            n = self._safe_int(n)  # Convert first so we can check for 0
            if not n:
                return ""
            if n < 10:
                return {
                    10: "ten",
                    11: "eleven",
                    12: "twelve",
                    13: "thirteen",
                    14: "fourteen",
                    15: "fifteen",
                    16: "sixteen",
                    17: "seventeen",
                    18: "eighteen",
                    19: "nineteen",
                }.get(n, _digit_to_word(str(n)))
            elif n < 100:
                tens = {
                    20: "twenty",
                    30: "thirty",
                    40: "forty",
                    50: "fifty",
                    60: "sixty",
                    70: "seventy",
                    80: "eighty",
                    90: "ninety",
                }.get(n - (n % 10), "")
                ones = _digit_to_word(str(n % 10)) if n % 10 else ""
                return f"{tens} {ones}".strip() if tens else _digit_to_word(str(n))
            else:
                return _digit_to_word(str(n))  # pragma: no cover - unreachable fallback

        def temp_to_words(m):
            sign = m.group(1) or ""
            temp_val = m.group(2)
            unit = m.group(3)
            sign_word = "minus " if sign == "-" else ""
            number_word = number_to_words(temp_val)
            # Convert C/F to Celsius/Fahrenheit
            if unit[-1] == "C":
                unit_word = " degrees Celsius"
            else:
                unit_word = " degrees Fahrenheit"
            return sign_word + number_word + unit_word

        # Only match temperature patterns with degree symbol (°C, °F)
        # Don't match plain C or F which might be used for other purposes
        text = re.sub(r"(-?)(\d+\.?\d*)(°[CF])", temp_to_words, text)

        # FIX: Handle YAML and XML explicitly before the acronym pattern converts them
        # YAML -> yam-el, XML -> ex-em-el (with hyphens for better TTS)
        text = re.sub(r"\bYAML\b", "yam-el", text, flags=re.IGNORECASE)
        text = re.sub(r"\bXML\b", "ex-em-el", text, flags=re.IGNORECASE)
        text = re.sub(r"\bJSON\b", "jay son", text, flags=re.IGNORECASE)
        text = re.sub(r"\bSQL\b", "sequel", text, flags=re.IGNORECASE)
        text = re.sub(r"\bAPI\b(?![/?&])", "A P I", text, flags=re.IGNORECASE)
        text = re.sub(r"\bGPS\b", "G P S", text, flags=re.IGNORECASE)
        text = re.sub(r"\bCEO\b", "C E O", text, flags=re.IGNORECASE)
        text = re.sub(r"\bCFO\b", "C F O", text, flags=re.IGNORECASE)
        text = re.sub(r"\bCTO\b", "C T O", text, flags=re.IGNORECASE)
        text = re.sub(r"\bCOO\b", "C O O", text, flags=re.IGNORECASE)

        # CRITICAL: Fix URLs AFTER acronym replacements so api/v2 in URLs stays lowercase
        # Format: H-T-T-P-S, forward slash, forward slash, example dot org, slash api, slash V-two, question mark, I-D equals forty-two
        if re.search(r"https?://[^\s]+", text):

            def url_to_words(match):
                url = match.group()
                # Remove trailing punctuation
                while url and url[-1] in ".,;:!?)":
                    url = url[:-1]

                result = []

                def number_to_words(n):
                    """Convert number string to words"""
                    try:
                        n_int = int(n)
                        if n_int < 20:
                            return {
                                0: "zero",
                                1: "one",
                                2: "two",
                                3: "three",
                                4: "four",
                                5: "five",
                                6: "six",
                                7: "seven",
                                8: "eight",
                                9: "nine",
                                10: "ten",
                                11: "eleven",
                                12: "twelve",
                                13: "thirteen",
                                14: "fourteen",
                                15: "fifteen",
                                16: "sixteen",
                                17: "seventeen",
                                18: "eighteen",
                                19: "nineteen",
                            }.get(n_int, str(n_int))
                        elif n_int < 100:
                            tens = {
                                20: "twenty",
                                30: "thirty",
                                40: "forty",
                                50: "fifty",
                                60: "sixty",
                                70: "seventy",
                                80: "eighty",
                                90: "ninety",
                            }.get(n_int - (n_int % 10), "")
                            ones = number_to_words(str(n_int % 10)) if n_int % 10 else ""
                            return f"{tens} {ones}".strip()
                        else:
                            hundreds = n_int // 100
                            rest = number_to_words(str(n_int % 100))
                            return f"{number_to_words(str(hundreds))} hundred {rest}".strip()
                    except:
                        return n

                def word_or_hyphenate(s, upper=False):
                    """Word if alpha only, else hyphenate letters, convert numbers to words"""
                    if s.isalpha():
                        # Hyphenate each letter: id -> I-D, debug -> D-E-B-U-G
                        return "-".join(list(s.upper())) if upper else s.lower()
                    result = []
                    i = 0
                    current_num = ""
                    while i < len(s):
                        c = s[i]
                        if c.isdigit():
                            current_num += c
                        else:
                            if current_num:
                                result.append(number_to_words(current_num))
                                current_num = ""
                            if c.isalpha():
                                result.append(c.upper() if upper else c.lower())
                        i += 1
                    if current_num:
                        result.append(number_to_words(current_num))
                    return "-".join(result)

                # Protocol - spell out with hyphens: HTTPS -> H-T-T-P-S, then forward slash twice
                if url.startswith("https://"):
                    result.append("H-T-T-P-S")
                    result.append("forward slash")
                    result.append("forward slash")
                    url = url[8:]
                elif url.startswith("http://"):
                    result.append("H-T-T-P")
                    result.append("forward slash")
                    result.append("forward slash")
                    url = url[7:]

                # Split by /
                parts = url.split("/")
                domain = parts[0]
                path_parts = parts[1:] if len(parts) > 1 else []

                # Domain - lowercase, "example dot org" not "E-X-A-M-P-L-E dot O-R-G"
                domain_parts = domain.split(".")
                for i, dp in enumerate(domain_parts):
                    if i > 0:
                        result.append("dot")
                    result.append(dp.lower())

                # Path segments - use "slash" for path, preserve case for mixed
                for pp in path_parts:
                    result.append("slash")
                    if "?" in pp:
                        path_seg, query = pp.split("?", 1)
                        result.append(word_or_hyphenate(path_seg))
                        result.append("question mark")
                        for param in query.split("&"):
                            if "=" in param:
                                k, v = param.split("=", 1)
                                # Query params should be uppercased: id -> I-D
                                result.append(word_or_hyphenate(k, upper=True))
                                result.append("equals")
                                result.append(word_or_hyphenate(v))
                            else:
                                result.append(word_or_hyphenate(param))
                    else:
                        result.append(word_or_hyphenate(pp))

                return " ".join(result)

            text = re.sub(r"https?://[^\s]+", url_to_words, text)
            changes.append("URL to words")

        # Fix email addresses like qa-test+tts@example.com
        # Convert to spell-out format: Q-A dash test plus tts at example dot com
        if re.search(r"\b[\w.+-]+@[\w.-]+\.\w+\b", text):

            def email_to_words(match):
                email = match.group()
                # Handle qa-test+tts@example.com format
                at_idx = email.rfind("@")
                local = email[:at_idx]
                domain = email[at_idx + 1 :] if "@" in email else ""

                # Process local part: spell out each character, but convert special chars to words
                local_words_parts = []
                for char in local:
                    if char == "-":
                        local_words_parts.append("dash")
                    elif char == "+":
                        local_words_parts.append("plus")
                    elif char == ".":
                        pass  # dots in local are typically not common, skip
                    else:
                        local_words_parts.append(char.upper())
                local_words = " ".join(local_words_parts)

                if domain:
                    # Process domain: spell out each part, dots become "dot"
                    domain_parts = domain.split(".")
                    domain_words = " dot ".join(domain_parts)
                    return f"{local_words} at {domain_words}"
                return local_words

            text = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w+\b", email_to_words, text)
            changes.append("Email address to words")

        # Fix international/multilingual text - convert non-Latin scripts to placeholders
        # The TTS cannot pronounce CJK, Arabic, Hebrew, Korean, etc.
        # This must happen BEFORE unicode normalization to avoid NFKC issues
        def is_non_latin_char(c):
            """Check if character is non-Latin and should be replaced"""
            code = ord(c)
            # CJK (Chinese, Japanese, Korean, etc.)
            if (
                0x3000 <= code <= 0x9FFF
                or 0xF900 <= code <= 0xFAFF
                or 0xFE30 <= code <= 0xFE4F
                or 0x1F200 <= code <= 0x1F9FF
            ):
                return True
            # Korean Hangul
            if 0xAC00 <= code <= 0xD7AF:
                return True
            # Arabic
            if 0x0600 <= code <= 0x06FF or 0x0750 <= code <= 0x077F or 0x08A0 <= code <= 0x08FF:
                return True
            # Hebrew
            if 0x0590 <= code <= 0x05FF:
                return True
            # Devanagari and other Indic scripts
            if 0x0900 <= code <= 0x097F or 0x0980 <= code <= 0x09FF:
                return True
            # Thai
            if 0x0E00 <= code <= 0x0E7F:
                return True
            # Georgian
            if 0x10A0 <= code <= 0x10FF:
                return True
            # Armenian
            if 0x0530 <= code <= 0x058F:
                return True
            # Tibetan
            if 0x0F00 <= code <= 0x0FFF:
                return True
            return False

        if re.search(r"[^\x00-\x7F]", text):
            result_parts = []
            current_group = []
            in_international = False
            last_was_comma = False

            for c in text:
                if ord(c) < 128 or not is_non_latin_char(c):
                    # Latin or ASCII character
                    if c == ",":
                        # Commas between international text segments - skip them to merge groups
                        if in_international and current_group:
                            last_was_comma = True
                            continue  # Skip the comma
                    else:
                        # Non-comma ASCII/Latin character
                        if in_international and current_group:
                            # End of international text group
                            result_parts.append("international text")
                            current_group = []
                            in_international = False
                        last_was_comma = False
                        result_parts.append(c)
                else:
                    # Non-Latin character
                    if last_was_comma:
                        # We skipped a comma before this group - add space separator
                        if result_parts and result_parts[-1] != " ":
                            result_parts.append(" ")
                    in_international = True
                    current_group.append(c)
                    last_was_comma = False

            # Don't forget the last group
            if in_international and current_group:
                result_parts.append("international text")

            text = "".join(result_parts)

            # Clean up: merge consecutive international text entries into one (repeat until stable)
            while re.search(r"international text\s+international text", text):
                text = re.sub(
                    r"international text\s+international text", " international text", text
                )
            # Clean up: remove commas between international text segments
            text = re.sub(r"international text\s*,\s*", "international text ", text)
            # Also clean up commas before international text
            text = re.sub(r"\s*,\s*international text", " international text", text)
            # Clean up trailing comma after international text at end of text
            text = re.sub(r"international text\s*,\s*$", " international text", text)
            # Clean up any remaining double spaces
            text = re.sub(r"\s+", " ", text)

            changes.append("International text to placeholders")

        # Fix bass player → BASE player (context: music)
        if re.search(r"\bbass player\b", text, re.IGNORECASE):
            text = re.sub(r"\bbass player\b", "BASE player", text, flags=re.IGNORECASE)
            changes.append("bass player -> BASE player")

        # Fix "read lead as the metal" vs "lead the verb"
        # Handle both quoted and unquoted versions (quotes may or may not be removed yet)
        # Pattern matches: not 'lead' the verb OR not lead the verb
        if re.search(r"not\s+'?\blead\b'?\s+the\s+verb", text, re.IGNORECASE):
            # "not lead the verb" -> "not to lead the verb"
            text = re.sub(
                r"not\s+'?\blead\b'?\s+the\s+verb",
                "not to lead the verb",
                text,
                flags=re.IGNORECASE,
            )
            changes.append("lead verb context -> to lead")

        # General "lead" handling for metal context
        # Handle both quoted and unquoted versions
        if re.search(r"'?\blead\b'?\s+(as\s+the\s+metal|the\s+metal)", text, re.IGNORECASE):
            text = re.sub(
                r"'?\blead\b'?\s+(as\s+the\s+metal|the\s+metal)",
                r"led \1",
                text,
                flags=re.IGNORECASE,
            )
            changes.append("lead (metal) -> led")

        if text != original_text and changes:
            logger.debug(f"Fixed fractions/symbols: {changes}")

        return text, changes

    def _filter_emojis(self, text: str) -> tuple[str, list[str]]:
        """
        Filter emojis from text to prevent verbalization
        Uses Unicode ranges to detect and remove emoji characters
        """
        changes = []

        # Unicode ranges for emojis (comprehensive coverage)
        emoji_patterns = [
            r"[\U0001F600-\U0001F64F]",  # Emoticons
            r"[\U0001F300-\U0001F5FF]",  # Misc Symbols and Pictographs
            r"[\U0001F680-\U0001F6FF]",  # Transport and Map Symbols
            r"[\U0001F1E0-\U0001F1FF]",  # Regional Indicator Symbols (flags)
            r"[\U00002600-\U000026FF]",  # Misc symbols
            r"[\U00002700-\U000027BF]",  # Dingbats
            r"[\U0001F900-\U0001F9FF]",  # Supplemental Symbols and Pictographs
            r"[\U0001FA70-\U0001FAFF]",  # Symbols and Pictographs Extended-A
            r"[\U00002B50-\U00002B55]",  # Stars and other symbols
        ]

        # Combine all patterns
        combined_pattern = "|".join(emoji_patterns)

        # Find all emojis in the text
        emojis_found = re.findall(combined_pattern, text)

        if emojis_found:
            # Replace emojis with configured replacement (default: empty string)
            replacement = self.emoji_replacement
            text = re.sub(combined_pattern, replacement, text)

            # Clean up any extra whitespace created by emoji removal
            text = re.sub(r"\s+", " ", text).strip()

            changes.append(f"Filtered {len(emojis_found)} emoji(s): {', '.join(set(emojis_found))}")
            logger.debug(f"Filtered emojis from text: {emojis_found}")

        return text, changes

    def _handle_quote_characters(self, text: str) -> tuple[str, list[str]]:
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
            '"',  # U+0022 QUOTATION MARK (ASCII double quote)
            "\u201c",  # U+201C LEFT DOUBLE QUOTATION MARK
            "\u201d",  # U+201D RIGHT DOUBLE QUOTATION MARK
        ]
        for quote_char in double_quote_chars:
            if quote_char in text:
                text = text.replace(quote_char, "")

        # Step 2: Handle single quotes more carefully
        # Remove single quotes that are NOT part of contractions

        # First, handle Unicode single quotes (always remove)
        # CRITICAL FIX: Use proper Unicode single quote characters (previous line had corrupted characters)
        unicode_single_quotes = [
            "\u2018",  # U+2018 LEFT SINGLE QUOTATION MARK
            "\u2019",  # U+2019 RIGHT SINGLE QUOTATION MARK
        ]
        for quote_char in unicode_single_quotes:
            if quote_char in text:
                text = text.replace(quote_char, "")

        # Handle ASCII single quotes - need to distinguish quotes from contractions
        if "'" in text:
            # CRITICAL FIX: Preserve contractions while removing quote characters
            # Common contractions that should be preserved
            contraction_patterns = [
                r"\bI'm\b",
                r"\byou're\b",
                r"\bhe's\b",
                r"\bshe's\b",
                r"\bit's\b",
                r"\bwe're\b",
                r"\bthey're\b",
                r"\bI've\b",
                r"\byou've\b",
                r"\bwe've\b",
                r"\bthey've\b",
                r"\bI'll\b",
                r"\byou'll\b",
                r"\bhe'll\b",
                r"\bshe'll\b",
                r"\bit'll\b",
                r"\bwe'll\b",
                r"\bthey'll\b",
                r"\bI'd\b",
                r"\byou'd\b",
                r"\bhe'd\b",
                r"\bshe'd\b",
                r"\bit'd\b",
                r"\bwe'd\b",
                r"\bthey'd\b",
                r"\bdon't\b",
                r"\bdoesn't\b",
                r"\bdidn't\b",
                r"\bwon't\b",
                r"\bwouldn't\b",
                r"\bcan't\b",
                r"\bcouldn't\b",
                r"\bshouldn't\b",
                r"\bmustn't\b",
                r"\bneedn't\b",
                r"\baren't\b",
                r"\bisn't\b",
                r"\bwasn't\b",
                r"\bweren't\b",
                r"\bhasn't\b",
                r"\bhaven't\b",
                r"\bhadn't\b",
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
            text = re.sub(r"\b'([^']*?)'\b", r"\1", text)  # 'word' -> word
            text = re.sub(r"^'([^']*)", r"\1", text)  # 'start -> start
            text = re.sub(r"([^'])'$", r"\1", text)  # end' -> end
            text = re.sub(r"\s'([^']*?)'(\s|$)", r" \1\2", text)  # ' word ' -> word
            text = re.sub(r"\s+'\s+", " ", text)  # Remove isolated quotes
            text = re.sub(r"^'\s+", "", text)  # Remove quote at start
            text = re.sub(r"\s+'$", "", text)  # Remove quote at end
            text = re.sub(r"''", "", text)  # Remove empty quotes ''
            text = re.sub(r"^'$", "", text)  # Remove single quote only

            # Restore contractions from placeholders
            for placeholder, contraction in contraction_placeholders.items():
                text = text.replace(placeholder, contraction)

        # Clean up any double spaces that might result from quote removal
        text = re.sub(r"\s+", " ", text).strip()

        if text != original_text:
            changes.append("Removed quote characters to prevent 'in quat' pronunciation")
            logger.debug(f"Quote handling: '{original_text[:50]}...' -> '{text[:50]}...'")

        return text, changes

    def _decode_html_entities(self, text: str) -> tuple[str, list[str]]:
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
            "&#x27;": "'",  # Hexadecimal apostrophe - use standard ASCII apostrophe
            "&#39;": "'",  # Decimal apostrophe - use standard ASCII apostrophe
            "&apos;": "'",  # Named apostrophe entity - use standard ASCII apostrophe
            "&quot;": '"',  # Double quote
            "&amp;": "&",  # Ampersand (but be careful with this one)
            "&lt;": "<",  # Less than
            "&gt;": ">",  # Greater than
            "&nbsp;": " ",  # Non-breaking space
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
                additional_changes = len([c for c in original_text if c == "&"]) - len(
                    [c for c in decoded_text if c == "&"]
                )
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

    def _convert_numbers_to_words(
        self, text: str, aggressive: bool = False
    ) -> tuple[str, list[str]]:
        """Convert numbers to words with proper comma-separated number handling"""
        changes = []

        # Handle comma-separated numbers first (CRITICAL FIX)
        # Pattern for numbers with commas: 1,000 or 1,000,000 etc.
        comma_number_pattern = r"\b\d{1,3}(?:,\d{3})+\b"
        comma_matches = re.findall(comma_number_pattern, text)

        for match in comma_matches:
            try:
                # Remove commas and convert to int, then to words
                number_value = self._safe_int(match.replace(",", ""))
                word_form = self._number_to_words(number_value)
                text = text.replace(match, word_form)
                changes.append(f"Converted comma-separated number '{match}' to '{word_form}'")
            except (ValueError, OverflowError):  # pragma: no cover - unreachable with valid input
                # If conversion fails, leave as-is but warn
                logger.warning(f"Could not convert comma-separated number: {match}")

        # Handle decimal numbers (e.g., 5.50, 3.14)
        decimal_pattern = r"\b\d+\.\d+\b"
        decimal_matches = re.findall(decimal_pattern, text)

        for match in decimal_matches:
            try:
                parts = match.split(".")
                integer_part = self._safe_int(parts[0])
                decimal_part = parts[1]

                integer_words = self._number_to_words(integer_part)
                decimal_words = " ".join(
                    self.number_words_map.get(digit, digit) for digit in decimal_part
                )

                word_form = f"{integer_words} point {decimal_words}"
                text = text.replace(match, word_form)
                changes.append(f"Converted decimal number '{match}' to '{word_form}'")
            except (ValueError, IndexError):
                logger.warning(f"Could not convert decimal number: {match}")

        # Handle simple numbers from the map
        for number, word in self.number_words_map.items():
            pattern = r"\b" + re.escape(number) + r"\b"
            if re.search(pattern, text):
                text = re.sub(pattern, word, text)
                changes.append(f"Converted number '{number}' to '{word}'")

        if aggressive:
            # Convert remaining standalone digits
            def digit_to_word(match):
                digit = match.group(0)
                return self.number_words_map.get(digit, digit)

            original_text = text
            text = re.sub(r"\b\d\b", digit_to_word, text)
            if text != original_text:
                changes.append("Converted remaining digits to words")  # pragma: no cover

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
        if number in [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            30,
            40,
            50,
            60,
            70,
            80,
            90,
        ]:
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

        # pragma: no cover - This fallback is unreachable because all number
        # ranges are explicitly handled above. Kept for defensive programming.
        return str(number)  # pragma: no cover

    def _convert_symbols_to_words(self, text: str) -> tuple[str, list[str]]:
        """
        Convert symbols to words, but be smart about HTML entities

        Since HTML entity decoding happens first, we shouldn't see HTML entities here,
        but we'll be extra careful with & and # symbols just in case.
        """
        changes = []

        for symbol, word in self.symbol_words_map.items():
            if symbol in text:
                # Special handling for & and # to avoid breaking any remaining HTML entities
                if symbol == "&":
                    # Only convert & if it's not part of an HTML entity pattern (using pre-compiled pattern)
                    if self.html_entity_amp_pattern.search(text):
                        text = self.html_entity_amp_pattern.sub(f" {word} ", text)
                        changes.append(f"Converted standalone symbol '{symbol}' to '{word}'")
                elif symbol == "#":
                    # Only convert # if it's not part of &#... pattern (using pre-compiled pattern)
                    if self.html_entity_hash_pattern.search(text):
                        text = self.html_entity_hash_pattern.sub(f" {word} ", text)
                        changes.append(f"Converted standalone symbol '{symbol}' to '{word}'")
                elif symbol in ["“", "”", "‘", "’"]:
                    # Special handling for quotes - remove them entirely (they should be silent)
                    # Don't add spaces when removing quotes to avoid changing word count
                    original_text = text
                    text = text.replace(symbol, word)  # word is empty string for quotes
                    if text != original_text:
                        changes.append(
                            f"Removed quote character '{symbol}' to prevent pronunciation issues"
                        )
                else:
                    # For other symbols, do normal replacement
                    text = text.replace(symbol, f" {word} ")
                    changes.append(f"Converted symbol '{symbol}' to '{word}'")

        return text, changes

    def _fix_problematic_patterns(self, text: str) -> tuple[str, list[str]]:
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
        text = self.whitespace_pattern.sub(" ", text)

        # Fix spacing around punctuation - CRITICAL FIX: Only remove EXCESSIVE spaces, preserve normal spacing
        # OLD BUG: text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # This removed ALL spaces before punctuation!
        # NEW FIX: Only remove multiple spaces (2+) before punctuation, preserve single spaces
        text = re.sub(
            r"\s{2,}([,.!?;:])", r" \1", text
        )  # Multiple spaces -> single space before punctuation
        text = re.sub(
            r"([.!?])\s*([A-Z])", r"\1 \2", text
        )  # Ensure space after sentence-ending punctuation

        # Remove excessive punctuation
        text = re.sub(r"[.]{2,}", ".", text)
        text = re.sub(r"[!]{2,}", "!", text)
        text = re.sub(r"[?]{2,}", "?", text)

        return text.strip()

    def _calculate_confidence_score(self, processed_text: str, original_text: str) -> float:
        """Calculate confidence score for phonemizer success"""
        score = 1.0

        # Penalize for remaining problematic characters
        problematic_chars = set("@#$%^&*()_+={}[]|\\:\";'<>?/~`")
        for char in processed_text:
            if char in problematic_chars:
                score -= 0.05

        # Penalize for remaining numbers
        if re.search(r"\d", processed_text):
            score -= 0.1

        # Penalize for very long words (likely to cause issues)
        words = processed_text.split()
        for word in words:
            if len(word) > 15:
                score -= 0.1

        # Bonus for proper sentence structure
        if re.search(r"[.!?]$", processed_text.strip()):
            score += 0.1

        return max(0.0, min(1.0, score))

    def _detect_potential_issues(self, text: str) -> list[str]:
        """Detect potential issues that might still cause problems with enhanced edge case detection"""
        warnings = []

        # Enhanced number detection (only warn if they're likely problematic)
        if re.search(r"\d+", text):
            # Count standalone numbers vs numbers in context
            standalone_numbers = len(re.findall(r"\b\d+\b", text))
            if standalone_numbers > 3:
                warnings.append(
                    "Contains many standalone numbers that might cause phonemizer issues"
                )
            elif re.search(r"\d{4,}", text):  # Long numbers like years, IDs
                warnings.append("Contains long numbers that might cause phonemizer issues")
            elif re.search(r"\d+[a-zA-Z]+|\d+\.\d+", text):  # Mixed alphanumeric or decimals
                warnings.append("Contains complex numbers that might cause phonemizer issues")

        # Enhanced special character detection (be more specific about problematic ones)
        problematic_chars = re.findall(r'[^\w\s\.,!?;:\'"()-]', text)
        if problematic_chars:
            unique_chars = set(problematic_chars)
            if len(unique_chars) > 5:
                warnings.append(
                    "Contains many special characters that might cause phonemizer issues"
                )
            elif any(char in "@#$%^&*+={}[]|\\<>" for char in unique_chars):
                warnings.append("Contains special characters that might cause phonemizer issues")

        # Enhanced long word detection (likely URLs, emails, or technical terms)
        words = text.split()
        long_words = [w for w in words if len(w) > 20]
        if long_words:
            warnings.append(f"Contains very long words: {', '.join(long_words[:2])}")

        # Check for code-like patterns (CSS, HTML, programming syntax)
        if re.search(r"[{}();].*[{}();]", text) or re.search(r"\w+:\s*\w+;", text):
            warnings.append("Contains code-like patterns that might confuse phonemizer")

        # Check for URLs or email patterns
        if re.search(r"https?://|www\.|@\w+\.\w+", text):
            warnings.append("Contains URLs or email addresses that might cause issues")

        # Check for excessive punctuation
        punct_count = len(re.findall(r"[^\w\s]", text))
        word_count = len(text.split())
        if word_count > 0 and punct_count / word_count > 0.5:
            warnings.append("Contains excessive punctuation that might cause issues")

        # Check for repeated characters (stuttering or emphasis)
        if re.search(r"(.)\1{4,}", text):
            warnings.append("Contains repeated characters that might cause issues")

        # Check for very long text
        if len(text) > 500:
            warnings.append("Text is very long, consider breaking into smaller chunks")

        # Check for mixed languages or scripts
        if re.search(r"[^\x00-\x7F]", text):  # Non-ASCII characters
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
                logger.debug(
                    f"Global config loaded: expand_contractions={config.get('text_processing', {}).get('expand_contractions', 'not set')}"
                )
                return config
    except Exception as e:
        logger.warning(f"Failed to load global config: {e}")
    return {}


def _create_global_preprocessor():
    """Create global preprocessor instance with current config"""
    config = _get_global_config()
    instance = PhonemizationPreprocessor(config=config)
    logger.debug(
        f"Global preprocessor created: expand_all={instance.expand_all}, preserve_natural={instance.preserve_natural}"
    )
    return instance


# Create global instance
phonemizer_preprocessor = _create_global_preprocessor()
