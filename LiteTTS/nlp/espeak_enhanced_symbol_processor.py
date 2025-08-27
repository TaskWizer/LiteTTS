#!/usr/bin/env python3
"""
eSpeak-enhanced symbol processor for Kokoro TTS
Integrates eSpeak's symbol handling techniques to fix pronunciation issues
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SymbolProcessingResult:
    """Result of symbol processing"""
    processed_text: str
    changes_made: List[str]
    symbols_processed: int
    processing_time: float = 0.0

class EspeakEnhancedSymbolProcessor:
    """
    Enhanced symbol processor using eSpeak-inspired techniques

    This processor addresses specific symbol pronunciation issues
    like "?" being pronounced as "right up arrow" by implementing
    eSpeak's symbol handling strategies.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.symbol_mappings = self._load_espeak_symbol_mappings()
        self.punctuation_mappings = self._load_punctuation_mappings()
        self.context_patterns = self._load_context_patterns()

    def _load_espeak_symbol_mappings(self) -> Dict[str, str]:
        """Load eSpeak-inspired symbol mappings"""
        return {
            # Critical fixes for known issues - QUESTION MARKS AND EXCLAMATIONS SHOULD NOT BE VOCALIZED
            # "?": "question mark",  # REMOVED - question marks should create natural intonation, not be vocalized
            # "!": "exclamation mark",  # REMOVED - exclamation marks should create natural emphasis, not be vocalized
            ".": "period",
            ",": "comma",
            ";": "semicolon",
            ":": "colon",

            # Mathematical symbols
            "+": "plus",
            "-": "minus",
            "=": "equals",
            "*": "asterisk",  # Fix "astrisk" pronunciation
            "/": "slash",
            "\\": "backslash",
            "%": "percent",

            # Currency symbols
            "$": "dollar",
            "€": "euro",
            "£": "pound",
            "¥": "yen",

            # Other symbols
            "&": "and",  # Natural ampersand pronunciation
            "@": "at",
            "#": "hash",
            "^": "caret",
            "_": "underscore",
            "|": "pipe",
            "~": "tilde",
            "`": "backtick",

            # Brackets and parentheses
            "(": "open parenthesis",
            ")": "close parenthesis",
            "[": "open bracket",
            "]": "close bracket",
            "{": "open brace",
            "}": "close brace",
            "<": "less than",
            ">": "greater than",

            # Quotes (fix "in quat" issues)
            '"': "",  # Remove quotes to prevent pronunciation
            "'": "",  # Remove apostrophes in quote context
            """: "",  # Smart quotes
            """: "",
            "'": "",
            "'": "",
        }

    def _load_punctuation_mappings(self) -> Dict[str, str]:
        """Load punctuation-specific mappings based on eSpeak modes"""
        return {
            # Sentence-ending punctuation - QUESTION MARKS AND EXCLAMATIONS SHOULD NOT BE VOCALIZED
            # "?": "question mark",  # REMOVED - question marks should create natural intonation
            # "!": "exclamation mark",  # REMOVED - exclamation marks should create natural emphasis
            ".": "period",

            # Clause punctuation (context-dependent)
            ",": "comma",
            ";": "semicolon",
            ":": "colon",

            # Grouping punctuation (usually silent)
            "(": "",
            ")": "",
            "[": "",
            "]": "",
            "{": "",
            "}": "",

            # Quote punctuation (usually silent)
            '"': "",
            "'": "",
        }

    def _load_context_patterns(self) -> Dict[str, Dict[str, str]]:
        """Load context-aware symbol processing patterns"""
        return {
            # URL context - don't pronounce symbols
            "url": {
                "pattern": r"https?://[^\s]+",
                "symbols": {".", "/", ":", "?", "&", "=", "-", "_"},
                "replacement": ""
            },

            # Email context - don't pronounce symbols
            "email": {
                "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "symbols": {"@", ".", "-", "_"},
                "replacement": ""
            },

            # Mathematical context - pronounce symbols
            "math": {
                "pattern": r"\b\d+\s*[+\-*/=]\s*\d+\b",
                "symbols": {"+", "-", "*", "/", "="},
                "replacement": "symbol"  # Use symbol mapping
            },

            # File path context - minimal pronunciation
            "filepath": {
                "pattern": r"[A-Za-z]:\\[^\\/:*?\"<>|]+|/[^\\/:*?\"<>|]+",
                "symbols": {"\\", "/", ".", "-", "_"},
                "replacement": ""
            },

            # Programming context - selective pronunciation
            "code": {
                "pattern": r"`[^`]+`|```[^`]+```",
                "symbols": {"(", ")", "[", "]", "{", "}", ";", ":", "="},
                "replacement": ""
            }
        }

    def process_symbols(self, text: str) -> SymbolProcessingResult:
        """
        Process symbols in text using eSpeak-enhanced techniques

        Args:
            text: Input text to process

        Returns:
            SymbolProcessingResult with processed text and metadata
        """
        import time
        start_time = time.perf_counter()

        original_text = text
        changes_made = []
        symbols_processed = 0

        # Step 1: Handle context-aware symbol processing
        text, context_changes = self._process_context_aware_symbols(text)
        changes_made.extend(context_changes)

        # Step 2: Fix critical symbol pronunciation issues
        text, critical_changes = self._fix_critical_symbols(text)
        changes_made.extend(critical_changes)
        symbols_processed += len(critical_changes)

        # Step 3: Handle punctuation based on eSpeak modes
        text, punct_changes = self._process_punctuation(text)
        changes_made.extend(punct_changes)

        # Step 4: Clean up quote characters to prevent "in quat" issues
        text, quote_changes = self._clean_quote_characters(text)
        changes_made.extend(quote_changes)

        processing_time = time.perf_counter() - start_time

        if changes_made:
            logger.debug(f"Symbol processing applied {len(changes_made)} changes: {', '.join(changes_made[:3])}")

        return SymbolProcessingResult(
            processed_text=text,
            changes_made=changes_made,
            symbols_processed=symbols_processed,
            processing_time=processing_time
        )

    def _process_context_aware_symbols(self, text: str) -> Tuple[str, List[str]]:
        """Process symbols based on context (URLs, emails, etc.)"""
        changes_made = []

        for context_name, context_info in self.context_patterns.items():
            pattern = context_info["pattern"]
            symbols = context_info["symbols"]
            replacement = context_info["replacement"]

            # Find all matches for this context
            matches = list(re.finditer(pattern, text))

            for match in reversed(matches):  # Process in reverse to maintain indices
                match_text = match.group()
                processed_text = match_text

                # Process symbols within this context
                for symbol in symbols:
                    if symbol in processed_text:
                        if replacement == "symbol":
                            # Use symbol mapping
                            processed_text = processed_text.replace(symbol, f" {self.symbol_mappings.get(symbol, symbol)} ")
                        elif replacement == "":
                            # Remove symbol
                            processed_text = processed_text.replace(symbol, " ")
                        else:
                            # Use custom replacement
                            processed_text = processed_text.replace(symbol, f" {replacement} ")

                # Clean up extra spaces
                processed_text = re.sub(r'\s+', ' ', processed_text).strip()

                if processed_text != match_text:
                    text = text[:match.start()] + processed_text + text[match.end():]
                    changes_made.append(f"context_{context_name}_symbols")

        return text, changes_made

    def _fix_critical_symbols(self, text: str) -> Tuple[str, List[str]]:
        """Fix critical symbol pronunciation issues"""
        changes_made = []

        # Critical fixes for known issues - QUESTION MARKS SHOULD NOT BE VOCALIZED
        critical_fixes = {
            # "?": "question mark",  # REMOVED - question marks should create natural intonation, not be vocalized
            "*": "asterisk",       # Fix "astrisk" pronunciation
        }

        for symbol, replacement in critical_fixes.items():
            if symbol in text:
                # Only replace standalone symbols, not those in words
                pattern = rf'\b{re.escape(symbol)}\b|\s{re.escape(symbol)}\s|{re.escape(symbol)}\s|\s{re.escape(symbol)}'
                if re.search(pattern, text):
                    text = re.sub(pattern, f' {replacement} ', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    changes_made.append(f"critical_fix_{symbol}")

        return text, changes_made

    def _process_punctuation(self, text: str) -> Tuple[str, List[str]]:
        """Process punctuation based on eSpeak punctuation modes"""
        changes_made = []

        # Get punctuation mode from config
        punct_mode = self.config.get("punctuation_mode", "some")

        if punct_mode == "none":
            # Remove all punctuation
            for punct in self.punctuation_mappings:
                if punct in text:
                    text = text.replace(punct, " ")
                    changes_made.append(f"removed_{punct}")
        elif punct_mode == "some":
            # Only pronounce important punctuation - QUESTION MARKS SHOULD NOT BE VOCALIZED
            important_punct = {"!"}  # REMOVED "?" - question marks should create natural intonation, not be vocalized
            for punct, replacement in self.punctuation_mappings.items():
                if punct in text and punct in important_punct and replacement:
                    text = text.replace(punct, f" {replacement} ")
                    changes_made.append(f"pronounced_{punct}")
        elif punct_mode == "all":
            # Pronounce all punctuation except periods (natural pause handling)
            for punct, replacement in self.punctuation_mappings.items():
                if punct in text and replacement and punct != ".":  # Exclude periods from vocalization
                    text = text.replace(punct, f" {replacement} ")
                    changes_made.append(f"pronounced_{punct}")

        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text, changes_made

    def _clean_quote_characters(self, text: str) -> Tuple[str, List[str]]:
        """Clean quote characters to prevent 'in quat' pronunciation issues"""
        changes_made = []

        quote_chars = ['"', "'", "\u201c", "\u201d", "\u2018", "\u2019"]

        for quote in quote_chars:
            if quote in text:
                # Remove quotes that are not part of contractions
                # Keep apostrophes in contractions like "don't", "can't"
                if quote == "'":
                    # Only remove apostrophes that are not in contractions
                    text = re.sub(r"(?<!\w)'(?!\w)|(?<!\w)'(?=\s)|(?<=\s)'(?!\w)", "", text)
                else:
                    # Remove other quote characters
                    text = text.replace(quote, "")
                changes_made.append(f"cleaned_quotes_{quote}")

        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text, changes_made

    def test_symbol_processing(self, test_cases: Optional[List[str]] = None) -> Dict[str, Any]:
        """Test symbol processing with various cases"""
        if test_cases is None:
            test_cases = [
                "Hello? How are you!",  # Question mark test
                "The cost is $50.99.",  # Currency and decimal
                "Visit https://example.com for more info.",  # URL
                "Email me at test@example.com",  # Email
                "Calculate 5 + 3 = 8",  # Math
                'She said "Hello world"',  # Quotes
                "The file is located at C:\\Users\\test.txt",  # File path
                "Use the * symbol carefully",  # Asterisk
            ]

        results = {}

        for i, test_case in enumerate(test_cases):
            result = self.process_symbols(test_case)
            results[f"test_{i+1}"] = {
                "input": test_case,
                "output": result.processed_text,
                "changes": result.changes_made,
                "symbols_processed": result.symbols_processed,
                "processing_time": result.processing_time
            }

        return results

# Factory function for easy integration
def create_espeak_enhanced_symbol_processor(config: Optional[Dict[str, Any]] = None) -> EspeakEnhancedSymbolProcessor:
    """Create eSpeak-enhanced symbol processor"""
    return EspeakEnhancedSymbolProcessor(config)