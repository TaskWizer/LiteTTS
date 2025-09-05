#!/usr/bin/env python3
"""
Advanced text normalization for TTS processing
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime
import logging

try:
    from .rime_ai_integration import rime_ai_processor
    RIME_AI_AVAILABLE = True
except ImportError:
    RIME_AI_AVAILABLE = False
    logging.warning("RIME AI integration not available")

logger = logging.getLogger(__name__)

class TextNormalizer:
    """Advanced text normalization for natural TTS output"""

    def __init__(self):
        self.number_patterns = self._compile_number_patterns()
        self.abbreviation_dict = self._load_abbreviations()
        self.currency_symbols = self._load_currency_symbols()
        self.symbol_patterns = self._load_symbol_patterns()
        self.contractions = self._load_contractions()

        # Load configuration for contraction handling
        self._load_config()

    def _load_config(self):
        """Load configuration settings for text normalization"""
        try:
            # First try to load from main config.json
            import json
            from pathlib import Path
            config_path = Path("config.json")
            if config_path.exists():
                with open(config_path) as f:
                    main_config = json.load(f)
                    text_processing = main_config.get('text_processing', {})

                    # Use main config settings if available
                    self.expand_contractions = text_processing.get('expand_contractions', False)
                    self.preserve_natural_speech = text_processing.get('natural_speech', True)

                    logger.debug(f"TextNormalizer config loaded from config.json: expand_contractions={self.expand_contractions}")
            else:
                # Fallback to performance config
                from ..config import config
                self.expand_contractions = config.performance.expand_contractions
                self.preserve_natural_speech = config.performance.preserve_natural_speech
                logger.debug("TextNormalizer config loaded from performance config")

            # These settings are still from performance config
            try:
                from ..config import config
                self.expand_problematic_only = config.performance.expand_problematic_contractions_only
            except:
                self.expand_problematic_only = True

        except Exception as e:
            logger.warning(f"Failed to load configuration, using defaults: {e}")
            # Default to natural speech preservation
            self.expand_contractions = False
            self.expand_problematic_only = True
            self.preserve_natural_speech = True

    def _compile_number_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for number processing"""
        return {
            'cardinal': re.compile(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b'),
            'ordinal': re.compile(r'\b(\d+)(?:st|nd|rd|th)\b', re.IGNORECASE),
            'decimal': re.compile(r'\b\d+\.\d+\b'),
            'percentage': re.compile(r'\b\d+(?:\.\d+)?%\b'),
            'fraction': re.compile(r'\b\d+/\d+\b'),
            'phone': re.compile(r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'),
            'time': re.compile(r'\b([0-1]?[0-9]|2[0-3]):([0-5][0-9])(?::([0-5][0-9]))?\s*(AM|PM|a\.m\.|p\.m\.)?(?=\s|$|[^\w.])', re.IGNORECASE),
            'date': re.compile(r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b'),
            'year': re.compile(r'\b(19|20)\d{2}\b'),
            'currency': re.compile(r'\$([0-9,]+(?:\.[0-9]{2})?)')
        }
    
    def _load_abbreviations(self) -> Dict[str, str]:
        """Load common abbreviations and their expansions"""
        return {
            # Titles
            'Dr.': 'Doctor', 'Mr.': 'Mister', 'Mrs.': 'Missus', 'Ms.': 'Miss',
            'Prof.': 'Professor', 'Rev.': 'Reverend',
            # Common abbreviations - FIXED: e.g. should work properly
            'etc.': 'etcetera', 'vs.': 'versus', 'e.g.': 'for example',
            'i.e.': 'that is', 'cf.': 'compare', 'et al.': 'and others',
            # Additional common abbreviations
            'w/': 'with', 'w/o': 'without', 'b/c': 'because', 'b/w': 'between',
            'aka': 'also known as', 'a.k.a.': 'also known as',
            # 'FAQ': 'frequently asked questions', 'F.A.Q.': 'frequently asked questions',  # Preserve FAQ as natural acronym
            'CEO': 'C E O', 'CFO': 'C F O', 'CTO': 'C T O',
            # Units
            'ft.': 'feet', 'in.': 'inches', 'lb.': 'pounds', 'oz.': 'ounces',
            'kg.': 'kilograms', 'cm.': 'centimeters', 'mm.': 'millimeters',
            'mph': 'miles per hour', 'km/h': 'kilometers per hour',
            # Technology - preserve common acronyms as they are naturally pronounced
            # Removed API, HTTP, etc. to preserve natural pronunciation
            # Only expand acronyms that are commonly spelled out
            'CPU.': 'C P U', 'GPU.': 'G P U', 'USB.': 'U S B',
            'CPU': 'C P U', 'GPU': 'G P U', 'USB': 'U S B',
            'URL': 'U R L', 'HTML': 'H T M L', 'CSS': 'C S S', 'JS': 'J S'
        }
    
    def _load_currency_symbols(self) -> Dict[str, str]:
        """Load currency symbols and their names"""
        return {
            '$': 'dollars', '€': 'euros', '£': 'pounds', '¥': 'yen',
            '₹': 'rupees', '₽': 'rubles', '₩': 'won', '¢': 'cents'
        }

    def _load_symbol_patterns(self) -> List[Tuple[str, str]]:
        """Load symbol normalization patterns"""
        return [
            # Mathematical and logical symbols - FIXED: & symbol to "and"
            (r'\s*&\s*', ' and '),    # & symbol with optional spaces
            (r'\s*\+\s*', ' plus '),  # Plus sign with optional spaces
            (r'\s*=\s*', ' equals '), # Equals sign with optional spaces
            (r'%', ' percent'),       # Percent sign - FIXED: no trailing space
            (r'\s*@\s*', ' at '),     # At symbol with optional spaces
            (r'\s*#\s*', ' hash '),   # Hash/pound symbol with optional spaces
            # Asterisk handling - FIXED: asterisk pronunciation
            (r'\s*\*\s*', ' asterisk '),    # Asterisk symbol with optional spaces
            # Other symbols - FIXED: avoid processing abbreviations like w/
            (r'(?<!w)\s*/\s*', ' slash '), # Slash with optional spaces, but not after 'w'
            (r'\s*\|\s*', ' pipe '), # Pipe symbol with optional spaces
            (r'\s*\^\s*', ' caret '), # Caret symbol with optional spaces
            (r'~', ' tilde '),        # Tilde symbol
            # Copyright and trademark symbols - FIXED: no trailing spaces
            (r'©', ' copyright'),     # Copyright symbol
            (r'®', ' registered'),    # Registered trademark
            (r'™', ' trademark'),     # Trademark symbol
            (r'°', ' degrees'),       # Degree symbol
        ]

    def _load_contractions(self) -> Dict[str, str]:
        """Load common contractions and their expansions"""
        return {
            # Common contractions - FIXED: Handle What's, John's, etc.
            "what's": "what is", "that's": "that is", "it's": "it is",
            "he's": "he is", "she's": "she is", "there's": "there is",
            "here's": "here is", "where's": "where is", "who's": "who is",
            "how's": "how is", "when's": "when is", "why's": "why is",

            # Negative contractions
            "don't": "do not", "doesn't": "does not", "didn't": "did not",
            "won't": "will not", "wouldn't": "would not", "shouldn't": "should not",
            "couldn't": "could not", "can't": "cannot", "isn't": "is not",
            "aren't": "are not", "wasn't": "was not", "weren't": "were not",
            "haven't": "have not", "hasn't": "has not", "hadn't": "had not",

            # Modal contractions
            "i'll": "I will", "you'll": "you will", "he'll": "he will",
            "she'll": "she will", "we'll": "we will", "they'll": "they will",
            "i'd": "I would", "you'd": "you would", "he'd": "he would",
            "she'd": "she would", "we'd": "we would", "they'd": "they would",
            "i've": "I have", "you've": "you have", "we've": "we have",
            "they've": "they have", "i'm": "I am", "you're": "you are",
            "we're": "we are", "they're": "they are",

            # Other common contractions
            "let's": "let us", "that'll": "that will", "there'll": "there will",
            "y'all": "you all", "ain't": "is not"
        }

    def normalize_text(self, text: str) -> str:
        """Main text normalization function with RIME AI integration"""
        logger.debug(f"Normalizing text: {text[:100]}...")

        # Step 1: Apply RIME AI phonetic processing if available
        if RIME_AI_AVAILABLE:
            try:
                rime_analysis = rime_ai_processor.process_text_with_rime_ai(text)
                if rime_analysis.confidence_score > 0.7:
                    text = rime_analysis.processed_text
                    logger.debug(f"RIME AI processing applied with confidence {rime_analysis.confidence_score:.2f}")
            except Exception as e:
                logger.warning(f"RIME AI processing failed: {e}")

        # Step 2: Apply standard normalizations in order - URLs/emails before symbols to preserve protocols
        text = self._normalize_urls_emails(text)  # MOVED: Process URLs before symbols
        text = self._normalize_currency(text)
        text = self._normalize_numbers(text)
        text = self._normalize_dates_times(text)
        text = self._normalize_contractions(text)  # ADDED: Process contractions first
        text = self._normalize_abbreviations(text)  # Process abbreviations
        text = self._normalize_symbols(text)  # Then symbols (to avoid conflicts)
        text = self._normalize_possessives(text)  # ADDED: Possessive normalization
        text = self._normalize_punctuation(text)
        text = self._clean_whitespace(text)
        
        logger.debug(f"Normalized result: {text[:100]}...")
        return text
    
    def _normalize_currency(self, text: str) -> str:
        """Normalize currency expressions with improved handling"""
        def replace_currency(match):
            amount = match.group(1)
            return self._number_to_words_currency(amount)

        text = self.number_patterns['currency'].sub(replace_currency, text)

        # Handle currency symbols with amounts - "$XXX" → "XXX dollars" (not "dollar XXX")
        for symbol, name in self.currency_symbols.items():
            # Pattern: $100 -> 100 dollars
            pattern = rf'\{re.escape(symbol)}(\d+(?:\.\d{{1,2}})?)'
            replacement = rf'\1 {name}'
            text = re.sub(pattern, replacement, text)

            # Handle standalone currency symbols
            if symbol in text:
                text = text.replace(symbol, f" {name} ")

        # Handle tilde symbol specifically - "~" → "approximately" (not "tildy")
        text = re.sub(r'~', ' approximately ', text)
        text = re.sub(r'≈', ' approximately ', text)

        return text

    def _normalize_contractions(self, text: str) -> str:
        """Handle contractions based on configuration"""

        # If preserve_natural_speech is True, don't expand contractions
        if self.preserve_natural_speech and not self.expand_contractions:
            # Only normalize apostrophes for consistency
            text = re.sub(r"'", "'", text)  # Normalize apostrophe type
            return text

        # If expand_problematic_only is True, only expand known problematic contractions
        if self.expand_problematic_only and not self.expand_contractions:
            # CRITICAL FIX: Define only truly problematic contractions that cause TTS issues
            # Natural contractions like "won't", "we'll", "I'm" should be preserved
            problematic_contractions = {
                # Only include contractions that cause actual pronunciation issues
                # Most W/I contractions are now preserved for natural speech
                "that'll": "that will",
                "who'll": "who will",
                "what'll": "what will",
                "where'll": "where will",
                "when'll": "when will",
                "how'll": "how will",
                "that'd": "that would",
                "who'd": "who would",
                "what'd": "what would",
                "where'd": "where would",
                "when'd": "when would",
                "how'd": "how would",
            }

            for contraction, expansion in problematic_contractions.items():
                pattern = r'\b' + re.escape(contraction) + r'\b'
                text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)

            # Normalize apostrophes for non-problematic contractions
            text = re.sub(r"'", "'", text)
            return text

        # Full expansion mode (legacy behavior)
        if self.expand_contractions:
            # Sort by length (longest first) to avoid partial matches
            sorted_contractions = sorted(self.contractions.items(), key=lambda x: len(x[0]), reverse=True)

            for contraction, expansion in sorted_contractions:
                # Use case-insensitive matching with word boundaries
                pattern = r'\b' + re.escape(contraction) + r'\b'
                text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)

        # Handle possessives that aren't contractions (like "John's")
        # For possessives that aren't in the contraction dictionary, keep them as-is
        # but ensure proper apostrophe formatting
        text = re.sub(r"(\w+)'s\b", r"\1's", text)  # Normalize apostrophe

        return text

    def _normalize_symbols(self, text: str) -> str:
        """Normalize symbols to their spoken equivalents"""
        for pattern, replacement in self.symbol_patterns:
            text = re.sub(pattern, replacement, text)
        return text

    def _normalize_possessives(self, text: str) -> str:
        """Normalize possessive forms to avoid 's x27' pronunciation issues"""
        # FIXED: Handle possessive 's properly
        # Replace 's with 's (using proper apostrophe)
        text = re.sub(r"'s\b", "'s", text)
        # Ensure possessives are pronounced correctly
        text = re.sub(r"(\w+)'s\b", r"\1's", text)
        return text

    def _normalize_numbers(self, text: str) -> str:
        """Normalize various number formats with natural speech preservation"""

        # If preserve_natural_speech is True, be more conservative with number expansion
        if self.preserve_natural_speech:
            # Only expand percentages, currency, and decimals - preserve years and other numbers
            # Percentages
            text = self.number_patterns['percentage'].sub(
                lambda m: f"{self._number_to_words(m.group().rstrip('%'))} percent", text
            )

            # Decimal numbers (always expand for clarity, even in natural speech mode)
            text = self.number_patterns['decimal'].sub(
                lambda m: self._number_to_words(m.group()), text
            )

            # Don't expand years in natural speech mode (1990's should stay as 1990's)
            # Don't expand cardinal numbers in natural speech mode
            # Don't expand fractions and ordinals in natural speech mode

            return text

        # Full expansion mode (legacy behavior)
        # Percentages
        text = self.number_patterns['percentage'].sub(
            lambda m: f"{self._number_to_words(m.group().rstrip('%'))} percent", text
        )

        # Fractions
        text = self.number_patterns['fraction'].sub(
            lambda m: self._fraction_to_words(m.group()), text
        )

        # Ordinals
        text = self.number_patterns['ordinal'].sub(
            lambda m: self._ordinal_to_words(m.group(1)), text
        )

        # Decimal numbers (before cardinal to avoid conflicts)
        text = self.number_patterns['decimal'].sub(
            lambda m: self._number_to_words(m.group()), text
        )

        # Years (special handling)
        text = self.number_patterns['year'].sub(
            lambda m: self._year_to_words(m.group()), text
        )

        # Cardinal numbers (integers only, decimals handled above)
        text = self.number_patterns['cardinal'].sub(
            lambda m: self._number_to_words(m.group()) if '.' not in m.group() else m.group(), text
        )

        return text
   
    def _normalize_dates_times(self, text: str) -> str:
        """Normalize date and time expressions"""
        # Time format (HH:MM)
        def replace_time(match):
            hour, minute = match.group(1), match.group(2)
            ampm = match.group(4) or ""

            hour_word = self._number_to_words(hour)
            if minute == "00":
                result = f"{hour_word} o'clock"
            else:
                minute_word = self._number_to_words(minute)
                result = f"{hour_word} {minute_word}"

            if ampm:
                # Convert all AM/PM formats to "a m"/"p m" format (no periods, single space)
                ampm_lower = ampm.lower()
                if ampm_lower in ["a.m.", "am"]:
                    result += " a m"
                elif ampm_lower in ["p.m.", "pm"]:
                    result += " p m"
                else:
                    # Fallback for any other format
                    result += f" {ampm}"

            return result

        text = self.number_patterns['time'].sub(replace_time, text)
        return text
    
    def _normalize_abbreviations(self, text: str) -> str:
        """Expand abbreviations"""
        # Sort by length (longest first) to avoid partial matches
        sorted_abbrevs = sorted(self.abbreviation_dict.items(), key=lambda x: len(x[0]), reverse=True)

        for abbrev, expansion in sorted_abbrevs:
            # FIXED: Handle abbreviations with periods properly
            if abbrev.endswith('.'):
                # For abbreviations ending with period, match at word boundaries or sentence boundaries
                pattern = r'(?<!\w)' + re.escape(abbrev) + r'(?!\w)'
            elif '/' in abbrev:
                # For abbreviations with slashes like w/, w/o - use non-word boundaries
                pattern = r'(?<!\w)' + re.escape(abbrev) + r'(?!\w)'
            else:
                # For regular abbreviations without periods, use strict word boundaries
                pattern = r'\b' + re.escape(abbrev) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)

        return text
    
    def _normalize_urls_emails(self, text: str) -> str:
        """Normalize URLs and email addresses"""
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        text = re.sub(email_pattern, lambda m: self._email_to_words(m.group()), text)

        # Full URLs with protocols - skip the protocol entirely
        url_pattern = r'https?://([^\s]+)'
        text = re.sub(url_pattern, lambda m: self._url_to_words(m.group(1)), text)

        # Domain names without protocols (e.g., example.com, domain.org)
        domain_pattern = r'\b[A-Za-z0-9.-]+\.(com|org|net|edu|gov|mil|int|co|uk|de|fr|jp|cn|au|ca|br|in|ru|it|es|nl|se|no|dk|fi|pl|cz|hu|gr|pt|ie|be|at|ch|lu|li|is|mt|cy|lv|lt|ee|sk|si|bg|ro|hr|rs|ba|mk|al|me|md|ua|by|kz|uz|kg|tj|tm|az|ge|am|tr|il|jo|lb|sy|iq|ir|af|pk|bd|lk|mv|np|bt|mm|th|la|kh|vn|my|sg|id|ph|bn|tl|pg|sb|vu|fj|to|ws|tv|nr|ki|mh|fm|pw|ck|nu|tk|pf|nc|wf|as|gu|mp|vi|pr|um|aq)\b'
        text = re.sub(domain_pattern, lambda m: self._domain_to_words(m.group()), text, flags=re.IGNORECASE)

        return text
    
    def _normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation for better prosody and pronunciation"""
        # Multiple exclamation marks
        text = re.sub(r'!{2,}', '!', text)
        # Multiple question marks
        text = re.sub(r'\?{2,}', '?', text)
        # Ellipsis
        text = re.sub(r'\.{3,}', '...', text)
        # Em dashes
        text = re.sub(r'—', ' -- ', text)
        text = re.sub(r'–', ' -- ', text)

        # Fix comma spacing issues that can cause pronunciation problems
        # Ensure proper spacing after commas (but not before)
        text = re.sub(r',(\S)', r', \1', text)  # Add space after comma if missing
        text = re.sub(r'\s+,', ',', text)       # Remove space before comma

        # Fix spacing around other punctuation
        text = re.sub(r'\.(\S)', r'. \1', text)  # Space after period
        text = re.sub(r'\?(\S)', r'? \1', text)  # Space after question mark
        text = re.sub(r'!(\S)', r'! \1', text)   # Space after exclamation

        # Handle contractions more carefully to prevent "Gir" issues
        # Ensure contractions are properly spaced
        text = re.sub(r"(\w)'(\w)", r"\1'\2", text)  # Normalize apostrophes in contractions

        return text
   
    def _clean_whitespace(self, text: str) -> str:
        """Clean up whitespace"""
        # Multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Trim
        text = text.strip()
        return text
    
    def _number_to_words(self, number_str: str) -> str:
        """Convert number to words (simplified implementation)"""
        try:
            # Remove commas
            number_str = number_str.replace(',', '')
            
            # Handle decimals
            if '.' in number_str:
                integer_part, decimal_part = number_str.split('.')
                integer_words = self._integer_to_words(int(integer_part))
                decimal_words = ' '.join([self._digit_to_word(d) for d in decimal_part])
                return f"{integer_words} point {decimal_words}"
            else:
                return self._integer_to_words(int(number_str))
        except ValueError:
            return number_str
    
    def _integer_to_words(self, num: int) -> str:
        """Convert integer to words"""
        if num == 0:
            return "zero"
        
        ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                "seventeen", "eighteen", "nineteen"]
        
        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
        
        if num < 20:
            return ones[num]
        elif num < 100:
            return tens[num // 10] + (" " + ones[num % 10] if num % 10 != 0 else "")
        elif num < 1000:
            return ones[num // 100] + " hundred" + (" " + self._integer_to_words(num % 100) if num % 100 != 0 else "")
        elif num < 1000000:
            return self._integer_to_words(num // 1000) + " thousand" + (" " + self._integer_to_words(num % 1000) if num % 1000 != 0 else "")
        elif num < 1000000000:
            return self._integer_to_words(num // 1000000) + " million" + (" " + self._integer_to_words(num % 1000000) if num % 1000000 != 0 else "")
        else:
            return str(num)  # Fallback for very large numbers  
  
    def _digit_to_word(self, digit: str) -> str:
        """Convert single digit to word"""
        digits = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        try:
            return digits[int(digit)]
        except (ValueError, IndexError):
            return digit
    
    def _ordinal_to_words(self, number_str: str) -> str:
        """Convert ordinal number to words"""
        try:
            num = int(number_str)
            base_word = self._integer_to_words(num)
            
            # Special cases
            if base_word.endswith("one"):
                return base_word[:-3] + "first"
            elif base_word.endswith("two"):
                return base_word[:-3] + "second"
            elif base_word.endswith("three"):
                return base_word[:-5] + "third"
            elif base_word.endswith("y"):
                return base_word[:-1] + "ieth"
            else:
                return base_word + "th"
        except ValueError:
            return number_str
    
    def _year_to_words(self, year_str: str) -> str:
        """Convert year to words with special pronunciation"""
        try:
            year = int(year_str)
            
            # Years 2000-2009
            if 2000 <= year <= 2009:
                return f"two thousand {self._integer_to_words(year - 2000)}" if year > 2000 else "two thousand"
            
            # Years 2010-2099
            elif 2010 <= year <= 2099:
                return f"twenty {self._integer_to_words(year - 2000)}"
            
            # Years 1900-1999
            elif 1900 <= year <= 1999:
                if year % 100 == 0:
                    return f"nineteen hundred"
                else:
                    return f"nineteen {self._integer_to_words(year % 100)}"
            
            # Other years
            else:
                return self._integer_to_words(year)
        except ValueError:
            return year_str    
  
    def _fraction_to_words(self, fraction_str: str) -> str:
        """Convert fraction to words"""
        try:
            numerator, denominator = fraction_str.split('/')
            num_word = self._integer_to_words(int(numerator))
            
            # Special denominators
            if denominator == "2":
                denom_word = "half" if numerator == "1" else "halves"
            elif denominator == "3":
                denom_word = "third" if numerator == "1" else "thirds"
            elif denominator == "4":
                denom_word = "quarter" if numerator == "1" else "quarters"
            else:
                denom_word = self._ordinal_to_words(denominator)
                if numerator != "1":
                    denom_word += "s"
            
            return f"{num_word} {denom_word}"
        except ValueError:
            return fraction_str
    
    def _number_to_words_currency(self, amount_str: str) -> str:
        """Convert currency amount to words"""
        try:
            if '.' in amount_str:
                dollars, cents = amount_str.split('.')
                dollar_words = self._integer_to_words(int(dollars))
                cent_words = self._integer_to_words(int(cents))
                
                dollar_unit = "dollar" if int(dollars) == 1 else "dollars"
                cent_unit = "cent" if int(cents) == 1 else "cents"
                
                if int(cents) == 0:
                    return f"{dollar_words} {dollar_unit}"
                else:
                    return f"{dollar_words} {dollar_unit} and {cent_words} {cent_unit}"
            else:
                dollar_words = self._integer_to_words(int(amount_str))
                dollar_unit = "dollar" if int(amount_str) == 1 else "dollars"
                return f"{dollar_words} {dollar_unit}"
        except ValueError:
            return amount_str
    
    def _email_to_words(self, email: str) -> str:
        """Convert email to speakable format"""
        email = email.replace('@', ' at ')
        email = email.replace('.', ' dot ')
        return email
    
    def _url_to_words(self, url: str) -> str:
        """Convert URL to speakable format - skip protocol, just read domain"""
        # Remove protocol entirely (https:// → skip entirely, just read domain)
        url = re.sub(r'^https?://', '', url)

        # For URLs like "example.com/path" → "example dot com slash path"
        # Replace common elements
        url = url.replace('www.', 'w w w dot ')
        url = url.replace('.com', ' dot com')
        url = url.replace('.org', ' dot org')
        url = url.replace('.net', ' dot net')
        url = url.replace('.edu', ' dot edu')
        url = url.replace('.gov', ' dot gov')
        url = url.replace('/', ' slash ')
        url = url.replace('?', ' question ')
        url = url.replace('&', ' and ')
        url = url.replace('=', ' equals ')

        return url

    def _domain_to_words(self, domain: str) -> str:
        """Convert domain name to speakable format"""
        # Replace common TLDs
        domain = domain.replace('.com', ' dot com')
        domain = domain.replace('.org', ' dot org')
        domain = domain.replace('.net', ' dot net')
        domain = domain.replace('.edu', ' dot edu')
        domain = domain.replace('.gov', ' dot gov')
        domain = domain.replace('.mil', ' dot mil')
        domain = domain.replace('.int', ' dot int')
        domain = domain.replace('.co', ' dot co')
        domain = domain.replace('.uk', ' dot uk')
        domain = domain.replace('.de', ' dot de')
        domain = domain.replace('.fr', ' dot fr')
        domain = domain.replace('.jp', ' dot jp')
        domain = domain.replace('.cn', ' dot cn')
        domain = domain.replace('.au', ' dot au')
        domain = domain.replace('.ca', ' dot ca')
        domain = domain.replace('.br', ' dot br')
        domain = domain.replace('.in', ' dot in')
        domain = domain.replace('.ru', ' dot ru')
        domain = domain.replace('.it', ' dot it')
        domain = domain.replace('.es', ' dot es')
        domain = domain.replace('.nl', ' dot nl')

        return domain