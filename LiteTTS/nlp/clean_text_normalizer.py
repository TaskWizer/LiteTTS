#!/usr/bin/env python3
"""
Clean Text Normalizer for TTS
A systematic, reliable text normalization pipeline that addresses all identified pronunciation issues
without generating malformed markup or corrupted output.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class NormalizationResult:
    """Result of text normalization"""
    processed_text: str
    original_text: str
    changes_made: List[str]
    issues_found: List[str]
    processing_time: float

class CleanTextNormalizer:
    """Clean, systematic text normalizer for TTS pronunciation fixes"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}

        # Load all normalization rules
        self.contraction_fixes = self._load_contraction_fixes()
        self.symbol_mappings = self._load_symbol_mappings()
        self.currency_patterns = self._load_currency_patterns()
        self.date_patterns = self._load_date_patterns()
        self.abbreviation_mappings = self._load_abbreviation_mappings()
        self.pronunciation_fixes = self._load_pronunciation_fixes()

        # Configuration
        self.fix_contractions = True
        self.fix_symbols = True
        self.fix_currency = True
        self.fix_dates = True
        self.fix_abbreviations = True
        self.fix_pronunciations = True

    def _should_expand_contractions(self) -> bool:
        """Check if contractions should be expanded based on config"""
        # Check the main expand_contractions setting
        expand_contractions = self.config.get('text_processing', {}).get('expand_contractions', False)

        # If expand_contractions is explicitly False, don't expand
        if expand_contractions is False:
            logger.debug("Contraction expansion disabled in config - preserving contractions")
            return False

        return True
        
    def _load_contraction_fixes(self) -> Dict[str, str]:
        """Load contraction pronunciation fixes - ONLY truly problematic contractions"""
        # CRITICAL FIX: Only include contractions that are truly problematic for TTS
        # Natural contractions like "won't", "we'll", "I'm" should be preserved
        return {
            # Only include contractions that cause actual TTS pronunciation issues
            # Most W/I contractions are now preserved for natural speech
            "that'll": "that will",  # Can be problematic
            "who'll": "who will",    # Can be problematic
            "what'll": "what will",  # Can be problematic
            "where'll": "where will", # Can be problematic
            "when'll": "when will",  # Can be problematic
            "how'll": "how will",    # Can be problematic
            "that'd": "that would",  # Can be problematic
            "who'd": "who would",    # Can be problematic
            "what'd": "what would",  # Can be problematic
            "where'd": "where would", # Can be problematic
            "when'd": "when would",  # Can be problematic
            "how'd": "how would",    # Can be problematic
            "wouldn't": "would not",
            "mustn't": "must not",
            "needn't": "need not",
            "didn't": "did not",
            "doesn't": "does not",
        }
    
    def _load_symbol_mappings(self) -> Dict[str, str]:
        """Load symbol-to-word mappings"""
        return {
            # Critical fixes from conversation history
            '*': ' asterisk ',  # Not "astrisk" - but this conflicts with pronunciation dict
            '&': ' and ',       # Not "ampersand"
            '%': ' percent ',
            '@': ' at ',
            '#': ' hash ',
            '+': ' plus ',
            '=': ' equals ',
            '~': ' approximately ',
            '^': ' caret ',
            '|': ' pipe ',
            '\\': ' backslash ',
            '/': ' slash ',
            '<': ' less than ',
            '>': ' greater than ',
            
            # Currency symbols are handled separately in currency processing
            # '$': ' dollars ',  # Handled in currency processing
            # '€': ' euros ',    # Handled in currency processing
            # '£': ' pounds ',   # Handled in currency processing
            # '¥': ' yen ',      # Handled in currency processing
        }
    
    def _load_currency_patterns(self) -> List[Tuple[str, callable]]:
        """Load currency processing patterns"""
        return [
            # Dollar amounts with cents
            (r'\$(\d{1,3}(?:,\d{3})*\.\d{2})', self._format_dollar_amount),
            # Dollar amounts without cents
            (r'\$(\d{1,3}(?:,\d{3})*)', self._format_dollar_amount_no_cents),
            # Approximate amounts
            (r'~\$(\d+(?:\.\d{2})?)', self._format_approximate_amount),
            # Euro amounts
            (r'€(\d+(?:\.\d{2})?)', self._format_euro_amount),
        ]
    
    def _load_date_patterns(self) -> List[Tuple[str, callable]]:
        """Load date processing patterns"""
        return [
            # ISO format (the problematic one)
            (r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b', self._format_iso_date),
            # US format MM/DD/YYYY
            (r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', self._format_us_date),
            # Short year format MM/DD/YY
            (r'\b(\d{1,2})/(\d{1,2})/(\d{2})\b', self._format_short_year_date),
        ]
    
    def _load_abbreviation_mappings(self) -> Dict[str, str]:
        """Load abbreviation mappings"""
        return {
            # Critical fixes from conversation history
            'FAQ': 'F-A-Q',
            'ASAP': 'A-S-A-P',  # Not "a sap"
            'Dr.': 'Doctor',
            'Mr.': 'Mister',
            'Mrs.': 'Missus',
            'Ms.': 'Miss',
            'Prof.': 'Professor',
            'e.g.': 'for example',  # Not "e g"
            'E.g.': 'For example',  # Capitalized version
            'i.e.': 'that is',
            'etc.': 'etcetera',
            'vs.': 'versus',
            'Inc.': 'Incorporated',
            'Corp.': 'Corporation',
            'Ltd.': 'Limited',
            'LLC': 'L-L-C',
            # Executive titles - keep as natural words, not spelled out
            # 'CEO': 'C-E-O',  # Keep as "CEO"
            # 'CFO': 'C-F-O',  # Keep as "CFO"
            # 'CTO': 'C-T-O',  # Keep as "CTO"
            'HR': 'H-R',
            # 'IT': 'I-T',  # DISABLED: Causes "it" → "I-T" conversion bug
            'AI': 'A-I',
            'API': 'A-P-I',
            'URL': 'U-R-L',
            'HTML': 'H-T-M-L',
            'CSS': 'C-S-S',
            'SQL': 'S-Q-L',
            'PDF': 'P-D-F',
            'GPS': 'G-P-S',
            'USB': 'U-S-B',
            'WiFi': 'Wi-Fi',
            'DVD': 'D-V-D',
            'CD': 'C-D',
            'TV': 'T-V',
            'PC': 'P-C',
            'Mac': 'Mac',
            'iOS': 'i-O-S',
            'Android': 'Android',
        }
    
    def _load_pronunciation_fixes(self) -> Dict[str, str]:
        """Load specific pronunciation fixes"""
        return {
            # From conversation history
            # 'Asterisk': 'AS-ter-isk',  # DISABLED: Conflicts with symbol processing
            'Hedonism': 'HEE-duh-niz-um',  # /ˈhiːdənɪzəm/
            'Inherently': 'in-HAIR-ent-lee',  # proper /ɛnt/ ending
            'acquisition': 'ak-wih-ZIH-shuhn',  # Not "equisition"
            'Elon': 'EE-lahn',  # Not "alon"
            'resume': 'REZ-oo-may',  # Document context (default)
            'joy': 'JOY',  # Not "ju-ie"
            'hmm': 'hum',  # Interjection handling
            'umm': 'um',
            'ahh': 'ah',
            'ohh': 'oh',

            # NEW CRITICAL PRONUNCIATION FIXES
            'religions': 'ri-LIJ-uhns',  # Not "really-gram-ions"
            'existentialism': 'eg-zi-STEN-shuhl-iz-uhm',  # Not "Exi-stential-ism"

            # Proper name pronunciation - systematic surname spelling
            'Carl Sagan': 'Carl S-A-gan',  # Apply letter-by-letter spelling to surnames
            'Sagan': 'S-A-gan',  # Standalone surname

            # Additional complex pronunciations
            'philosophy': 'fi-LOS-uh-fee',
            'psychology': 'sy-KOL-uh-jee',
            'sociology': 'so-see-OL-uh-jee',
            'anthropology': 'an-thruh-POL-uh-jee',
            
            # Stock symbols - spell out letter-by-letter for universal compatibility
            # Only include major, commonly referenced ticker symbols to avoid over-processing
            'TSLA': 'T-S-L-A',
            'AAPL': 'A-A-P-L',
            'MSFT': 'M-S-F-T',
            'GOOGL': 'G-O-O-G-L',
            'AMZN': 'A-M-Z-N',
            'NVDA': 'N-V-D-A',
            'META': 'M-E-T-A',
            'NFLX': 'N-F-L-X',
            'GOOG': 'G-O-O-G',
            'COIN': 'C-O-I-N',
            'VTI': 'V-T-I',
            # Note: Removed less common tickers to avoid conflicts with common words
        }
    
    def normalize_text(self, text: str) -> NormalizationResult:
        """Main normalization function"""
        import time
        start_time = time.perf_counter()
        
        original_text = text
        changes_made = []
        issues_found = []
        
        logger.debug(f"Starting clean normalization: {text[:100]}...")
        
        try:
            # Step 1: Fix HTML entities and encoding issues
            if '&#x27;' in text or '&quot;' in text:
                text = self._fix_html_entities(text)
                changes_made.append("Fixed HTML entities")
            
            # Step 2: Fix contractions
            if self.fix_contractions:
                old_text = text
                text = self._fix_contractions(text)
                if text != old_text:
                    changes_made.append("Fixed contractions")

            # Step 3: Fix currency amounts BEFORE symbols to avoid conflicts
            if self.fix_currency:
                old_text = text
                text = self._fix_currency(text)
                if text != old_text:
                    changes_made.append("Fixed currency")

            # Step 4: Fix dates BEFORE symbols to avoid "/" conflicts
            if self.fix_dates:
                old_text = text
                text = self._fix_dates(text)
                if text != old_text:
                    changes_made.append("Fixed dates")

            # Step 5: Fix symbols and punctuation
            if self.fix_symbols:
                old_text = text
                text = self._fix_symbols(text)
                if text != old_text:
                    changes_made.append("Fixed symbols")
            
            # Step 6: Fix abbreviations
            if self.fix_abbreviations:
                old_text = text
                text = self._fix_abbreviations(text)
                if text != old_text:
                    changes_made.append("Fixed abbreviations")

            # Step 6.5: Fix contextual units
            old_text = text
            text = self._fix_contextual_units(text)
            if text != old_text:
                changes_made.append("Fixed contextual units")
            
            # Step 7: Fix specific pronunciations
            if self.fix_pronunciations:
                old_text = text
                text = self._fix_pronunciations(text)
                if text != old_text:
                    changes_made.append("Fixed pronunciations")
            
            # Step 8: Clean up whitespace
            text = self._clean_whitespace(text)
            
            processing_time = time.perf_counter() - start_time
            
            logger.debug(f"Clean normalization complete: {text[:100]}...")
            
            return NormalizationResult(
                processed_text=text,
                original_text=original_text,
                changes_made=changes_made,
                issues_found=issues_found,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in clean normalization: {e}")
            issues_found.append(f"Processing error: {e}")
            processing_time = time.perf_counter() - start_time
            
            return NormalizationResult(
                processed_text=original_text,  # Return original on error
                original_text=original_text,
                changes_made=changes_made,
                issues_found=issues_found,
                processing_time=processing_time
            )
    
    def _fix_html_entities(self, text: str) -> str:
        """Fix HTML entities that cause pronunciation issues"""
        # Critical fixes from conversation history
        html_fixes = {
            '&#x27;': "'",  # Apostrophe that causes "x 27" pronunciation
            '&#39;': "'",   # Apostrophe
            '&apos;': "'",  # Apostrophe
            '&quot;': '',   # Quote - remove to prevent "in quat"
            '&#34;': '',    # Quote - remove to prevent "in quat"
            '&#x22;': '',   # Quote - remove to prevent "in quat"
            '&amp;': ' and ',  # Ampersand
            '&lt;': ' less than ',
            '&gt;': ' greater than ',
            '&nbsp;': ' ',  # Non-breaking space
        }
        
        for entity, replacement in html_fixes.items():
            text = text.replace(entity, replacement)
        
        return text
    
    def _fix_contractions(self, text: str) -> str:
        """Fix contraction pronunciations"""
        # Check if contraction expansion is disabled in config
        if not self._should_expand_contractions():
            logger.debug("Contraction expansion disabled - skipping contraction fixes")
            return text

        for contraction, expansion in self.contraction_fixes.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(contraction) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)

        return text
    
    def _fix_symbols(self, text: str) -> str:
        """Fix symbol pronunciations"""
        for symbol, replacement in self.symbol_mappings.items():
            if symbol == '*':
                # Special handling for asterisk - only standalone ones
                text = re.sub(r'(?<!\*)\*(?!\*)', replacement, text)
            else:
                text = text.replace(symbol, replacement)
        
        return text

    def _fix_currency(self, text: str) -> str:
        """Fix currency amount pronunciations"""
        for pattern, formatter in self.currency_patterns:
            if callable(formatter):
                # Use a lambda to capture the formatter function
                text = re.sub(pattern, lambda m: formatter(m), text)
            else:
                text = re.sub(pattern, formatter, text)

        return text

    def _format_dollar_amount(self, match) -> str:
        """Format dollar amounts with cents"""
        amount_str = match.group(1)
        # Remove commas for processing
        amount_str = amount_str.replace(',', '')

        if '.' in amount_str:
            dollars, cents = amount_str.split('.')
            dollars = int(dollars)
            cents = int(cents)

            dollar_text = self._number_to_words(dollars)
            cent_text = self._number_to_words(cents)

            if dollars == 1:
                dollar_word = "dollar"
            else:
                dollar_word = "dollars"

            if cents == 1:
                cent_word = "cent"
            else:
                cent_word = "cents"

            return f"{dollar_text} {dollar_word} and {cent_text} {cent_word}"
        else:
            dollars = int(amount_str)
            dollar_text = self._number_to_words(dollars)
            dollar_word = "dollar" if dollars == 1 else "dollars"
            return f"{dollar_text} {dollar_word}"

    def _format_dollar_amount_no_cents(self, match) -> str:
        """Format dollar amounts without cents"""
        amount_str = match.group(1).replace(',', '')
        dollars = int(amount_str)
        dollar_text = self._number_to_words(dollars)
        dollar_word = "dollar" if dollars == 1 else "dollars"
        return f"{dollar_text} {dollar_word}"

    def _format_approximate_amount(self, match) -> str:
        """Format approximate amounts"""
        amount_str = match.group(1)
        formatted = self._format_dollar_amount(re.match(r'(\d+(?:\.\d{2})?)', amount_str))
        return f"approximately {formatted}"

    def _format_euro_amount(self, match) -> str:
        """Format euro amounts"""
        amount_str = match.group(1)
        if '.' in amount_str:
            euros, cents = amount_str.split('.')
            euros = int(euros)
            cents = int(cents)

            euro_text = self._number_to_words(euros)
            cent_text = self._number_to_words(cents)

            euro_word = "euro" if euros == 1 else "euros"
            cent_word = "cent" if cents == 1 else "cents"

            return f"{euro_text} {euro_word} and {cent_text} {cent_word}"
        else:
            euros = int(amount_str)
            euro_text = self._number_to_words(euros)
            euro_word = "euro" if euros == 1 else "euros"
            return f"{euro_text} {euro_word}"

    def _fix_dates(self, text: str) -> str:
        """Fix date pronunciations"""
        for pattern, formatter in self.date_patterns:
            if callable(formatter):
                text = re.sub(pattern, lambda m: formatter(m), text)
            else:
                text = re.sub(pattern, formatter, text)

        return text

    def _format_iso_date(self, match) -> str:
        """Format ISO dates (YYYY-MM-DD) to prevent 'dash' pronunciation"""
        year, month, day = match.groups()
        year = int(year)
        month = int(month)
        day = int(day)

        month_names = [
            '', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        month_name = month_names[month] if 1 <= month <= 12 else str(month)
        day_ordinal = self._number_to_ordinal(day)
        year_text = self._number_to_words(year)

        return f"{month_name} {day_ordinal}, {year_text}"

    def _format_us_date(self, match) -> str:
        """Format US dates (MM/DD/YYYY)"""
        month, day, year = match.groups()
        month = int(month)
        day = int(day)
        year = int(year)

        month_names = [
            '', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        month_name = month_names[month] if 1 <= month <= 12 else str(month)
        day_ordinal = self._number_to_ordinal(day)
        year_text = self._number_to_words(year)

        return f"{month_name} {day_ordinal}, {year_text}"

    def _format_short_year_date(self, match) -> str:
        """Format short year dates (MM/DD/YY)"""
        month, day, year = match.groups()
        month = int(month)
        day = int(day)
        year = int(year)

        # Assume 20xx for years 00-30, 19xx for years 31-99
        if year <= 30:
            full_year = 2000 + year
        else:
            full_year = 1900 + year

        month_names = [
            '', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        month_name = month_names[month] if 1 <= month <= 12 else str(month)
        day_ordinal = self._number_to_ordinal(day)
        year_text = self._number_to_words(full_year)

        return f"{month_name} {day_ordinal}, {year_text}"

    def _fix_abbreviations(self, text: str) -> str:
        """Fix abbreviation pronunciations"""
        for abbrev, replacement in self.abbreviation_mappings.items():
            if abbrev.endswith('.'):
                # Handle abbreviations with periods more carefully
                pattern = r'(?<!\w)' + re.escape(abbrev) + r'(?!\w)'
            else:
                # Use word boundaries for regular abbreviations
                pattern = r'\b' + re.escape(abbrev) + r'\b'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _fix_pronunciations(self, text: str) -> str:
        """Fix specific pronunciation issues"""
        # First, handle systematic ticker symbol processing
        text = self._process_ticker_symbols(text)

        # Then handle specific pronunciation fixes
        for word, pronunciation in self.pronunciation_fixes.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(word) + r'\b'
            text = re.sub(pattern, pronunciation, text, flags=re.IGNORECASE)

        return text

    def _process_ticker_symbols(self, text: str) -> str:
        """Process potential ticker symbols systematically"""
        # Disable contextual processing in the clean normalizer to avoid over-processing
        # Only process explicitly known ticker symbols from the pronunciation dictionary
        return text

    def _clean_whitespace(self, text: str) -> str:
        """Clean up whitespace"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Fix spacing around punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([,.!?;:])\s*', r'\1 ', text)  # Ensure space after punctuation

        return text

    def _number_to_words(self, num: int) -> str:
        """Convert numbers to words (simplified implementation)"""
        if num == 0:
            return "zero"

        ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                "seventeen", "eighteen", "nineteen"]

        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        if num < 20:
            return ones[num]
        elif num < 100:
            return tens[num // 10] + ("" if num % 10 == 0 else " " + ones[num % 10])
        elif num < 1000:
            return ones[num // 100] + " hundred" + ("" if num % 100 == 0 else " " + self._number_to_words(num % 100))
        elif num < 1000000:
            return self._number_to_words(num // 1000) + " thousand" + ("" if num % 1000 == 0 else " " + self._number_to_words(num % 1000))
        else:
            # For larger numbers, use a simplified approach
            return str(num)  # Fallback to digits for very large numbers

    def _number_to_ordinal(self, num: int) -> str:
        """Convert numbers to ordinal words"""
        if num == 1:
            return "first"
        elif num == 2:
            return "second"
        elif num == 3:
            return "third"
        elif num == 4:
            return "fourth"
        elif num == 5:
            return "fifth"
        elif num == 6:
            return "sixth"
        elif num == 7:
            return "seventh"
        elif num == 8:
            return "eighth"
        elif num == 9:
            return "ninth"
        elif num == 10:
            return "tenth"
        elif num == 11:
            return "eleventh"
        elif num == 12:
            return "twelfth"
        elif num == 13:
            return "thirteenth"
        elif num == 14:
            return "fourteenth"
        elif num == 15:
            return "fifteenth"
        elif num == 16:
            return "sixteenth"
        elif num == 17:
            return "seventeenth"
        elif num == 18:
            return "eighteenth"
        elif num == 19:
            return "nineteenth"
        elif num == 20:
            return "twentieth"
        elif num == 21:
            return "twenty-first"
        elif num == 22:
            return "twenty-second"
        elif num == 23:
            return "twenty-third"
        elif num == 30:
            return "thirtieth"
        elif num == 31:
            return "thirty-first"
        else:
            # For other numbers, add appropriate suffix
            if 10 <= num % 100 <= 20:
                suffix = "th"
            else:
                last_digit = num % 10
                if last_digit == 1:
                    suffix = "st"
                elif last_digit == 2:
                    suffix = "nd"
                elif last_digit == 3:
                    suffix = "rd"
                else:
                    suffix = "th"

            return self._number_to_words(num) + suffix

    def _fix_contextual_units(self, text: str) -> str:
        """Process single-letter units only in proper measurement contexts"""
        # Define unit patterns that should only be processed in measurement contexts
        contextual_units = {
            'm': 'meters',
            'g': 'grams',
            'in': 'inches'
        }

        # Pattern to match numbers followed by units
        # This ensures we only process units that follow numbers
        for unit, expansion in contextual_units.items():
            # Match: number + space + unit + word boundary
            # Examples: "5 m tall", "10 g of", "3 in wide"
            pattern = r'(\d+(?:\.\d+)?)\s+' + re.escape(unit) + r'\b'
            replacement = r'\1 ' + expansion
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

            # Also match: number + unit (no space)
            # Examples: "5m", "10g", "3in"
            pattern = r'(\d+(?:\.\d+)?)' + re.escape(unit) + r'\b'
            replacement = r'\1 ' + expansion
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text
