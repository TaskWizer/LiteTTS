#!/usr/bin/env python3
"""
Advanced Currency & Financial Processing System
Implements robust currency amount processing with natural language output
"""

import re
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CurrencyAmount:
    """Represents a currency amount with metadata"""
    value: float
    currency: str
    is_approximate: bool = False
    has_suffix: bool = False
    suffix_type: str = ""  # M, B, K, etc.
    original_text: str = ""

@dataclass
class FinancialContext:
    """Context information for financial processing"""
    is_financial_document: bool = False
    currency_preference: str = "USD"
    decimal_precision: int = 2
    use_natural_language: bool = True

class AdvancedCurrencyProcessor:
    """Advanced currency and financial data processing system"""
    
    def __init__(self):
        self.currency_symbols = self._load_currency_symbols()
        self.currency_patterns = self._compile_currency_patterns()
        self.financial_suffixes = self._load_financial_suffixes()
        self.number_words = self._load_number_words()
        self.ordinal_words = self._load_ordinal_words()
        
        # Configuration
        self.max_number_size = 1_000_000_000_000  # 1 trillion
        self.enable_suffix_processing = True
        self.enable_approximate_processing = True
        self.enable_international_currencies = True
        
    def _load_currency_symbols(self) -> Dict[str, Dict[str, str]]:
        """Load comprehensive currency symbol mappings"""
        return {
            '$': {
                'name': 'dollar',
                'plural': 'dollars',
                'subunit': 'cent',
                'subunit_plural': 'cents',
                'code': 'USD'
            },
            '€': {
                'name': 'euro',
                'plural': 'euros', 
                'subunit': 'cent',
                'subunit_plural': 'cents',
                'code': 'EUR'
            },
            '£': {
                'name': 'pound',
                'plural': 'pounds',
                'subunit': 'pence',
                'subunit_plural': 'pence',
                'code': 'GBP'
            },
            '¥': {
                'name': 'yen',
                'plural': 'yen',
                'subunit': 'sen',
                'subunit_plural': 'sen',
                'code': 'JPY'
            },
            '₹': {
                'name': 'rupee',
                'plural': 'rupees',
                'subunit': 'paisa',
                'subunit_plural': 'paise',
                'code': 'INR'
            },
            '₽': {
                'name': 'ruble',
                'plural': 'rubles',
                'subunit': 'kopeck',
                'subunit_plural': 'kopecks',
                'code': 'RUB'
            },
            '₩': {
                'name': 'won',
                'plural': 'won',
                'subunit': 'jeon',
                'subunit_plural': 'jeon',
                'code': 'KRW'
            },
            '¢': {
                'name': 'cent',
                'plural': 'cents',
                'subunit': '',
                'subunit_plural': '',
                'code': 'USD'
            }
        }
    
    def _load_financial_suffixes(self) -> Dict[str, Dict[str, Union[int, str]]]:
        """Load financial suffix mappings (M, B, K, etc.)"""
        return {
            'K': {'multiplier': 1_000, 'name': 'thousand'},
            'M': {'multiplier': 1_000_000, 'name': 'million'},
            'B': {'multiplier': 1_000_000_000, 'name': 'billion'},
            'T': {'multiplier': 1_000_000_000_000, 'name': 'trillion'},
            'k': {'multiplier': 1_000, 'name': 'thousand'},
            'm': {'multiplier': 1_000_000, 'name': 'million'},
            'b': {'multiplier': 1_000_000_000, 'name': 'billion'},
            't': {'multiplier': 1_000_000_000_000, 'name': 'trillion'}
        }
    
    def _compile_currency_patterns(self) -> List[Tuple[str, str]]:
        """Compile regex patterns for currency detection"""
        # Note: This method is for reference only
        # Actual pattern matching is done in individual processing methods
        return []
    
    def _load_number_words(self) -> Dict[int, str]:
        """Load number-to-words mappings"""
        return {
            0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
            6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
            11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
            16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty",
            30: "thirty", 40: "forty", 50: "fifty", 60: "sixty", 70: "seventy",
            80: "eighty", 90: "ninety"
        }
    
    def _load_ordinal_words(self) -> Dict[int, str]:
        """Load ordinal number mappings"""
        return {
            1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
            6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
            11: "eleventh", 12: "twelfth", 13: "thirteenth", 14: "fourteenth", 15: "fifteenth",
            16: "sixteenth", 17: "seventeenth", 18: "eighteenth", 19: "nineteenth", 20: "twentieth",
            30: "thirtieth", 40: "fortieth", 50: "fiftieth", 60: "sixtieth", 70: "seventieth",
            80: "eightieth", 90: "ninetieth"
        }
    
    def process_currency_text(self, text: str, context: Optional[FinancialContext] = None) -> str:
        """Main method to process currency and financial text"""
        if context is None:
            context = FinancialContext()
        
        logger.debug(f"Processing currency text: {text[:100]}...")
        
        # Process in order of complexity (most specific first)
        text = self._process_negative_currencies(text, context)  # Process negative first
        text = self._process_currency_with_suffixes(text, context)
        text = self._process_approximate_currencies(text, context)
        text = self._process_large_currency_amounts(text, context)
        text = self._process_basic_currencies(text, context)
        text = self._process_financial_terms(text, context)
        
        logger.debug(f"Currency processing result: {text[:100]}...")
        return text
    
    def _process_currency_with_suffixes(self, text: str, context: FinancialContext) -> str:
        """Process currency amounts with financial suffixes (M, B, K)"""
        if not self.enable_suffix_processing:
            return text

        for symbol, currency_info in self.currency_symbols.items():
            escaped_symbol = re.escape(symbol)

            # Pattern: $2.5M, €1.2B (case insensitive)
            pattern = rf'{escaped_symbol}(\d+(?:\.\d+)?)\s*([KMBTkmbt])\b'

            def replace_suffix(match):
                amount_str = match.group(1)
                suffix = match.group(2).upper()

                try:
                    amount = float(amount_str)
                    suffix_info = self.financial_suffixes[suffix]

                    # Convert to natural language
                    if amount == int(amount):
                        amount_words = self._number_to_words(int(amount))
                    else:
                        amount_words = self._decimal_to_words(amount)

                    suffix_name = suffix_info['name']
                    currency_name = currency_info['plural'] if amount != 1 else currency_info['name']

                    return f"{amount_words} {suffix_name} {currency_name}"

                except (ValueError, KeyError):
                    return match.group(0)  # Return original if parsing fails

            text = re.sub(pattern, replace_suffix, text, flags=re.IGNORECASE)

        return text
    
    def _process_approximate_currencies(self, text: str, context: FinancialContext) -> str:
        """Process approximate currency amounts (~$500)"""
        if not self.enable_approximate_processing:
            return text

        for symbol, currency_info in self.currency_symbols.items():
            escaped_symbol = re.escape(symbol)

            # Pattern: ~$568.91 or ~ $1,000 (with or without commas)
            pattern = rf'~\s*{escaped_symbol}(\d{{1,3}}(?:,\d{{3}})*(?:\.\d{{1,4}})?|\d+(?:\.\d{{1,4}})?)\b'

            def replace_approximate(match):
                amount_str = match.group(1).replace(',', '')  # Remove commas
                try:
                    amount = float(amount_str)
                    amount_words = self._currency_amount_to_words(amount, currency_info)
                    return f"approximately {amount_words}"
                except ValueError:
                    return match.group(0)

            text = re.sub(pattern, replace_approximate, text)

        return text
    
    def _process_large_currency_amounts(self, text: str, context: FinancialContext) -> str:
        """Process large currency amounts with commas ($1,234,567.89)"""
        for symbol, currency_info in self.currency_symbols.items():
            escaped_symbol = re.escape(symbol)

            # Pattern: $1,234,567.89 (ONLY numbers WITH commas)
            pattern = rf'{escaped_symbol}(\d{{1,3}}(?:,\d{{3}})+(?:\.\d{{1,4}})?)\b'

            def replace_large_amount(match):
                amount_str = match.group(1).replace(',', '')  # Remove commas
                try:
                    amount = float(amount_str)
                    return self._currency_amount_to_words(amount, currency_info)
                except ValueError:
                    return match.group(0)

            text = re.sub(pattern, replace_large_amount, text)

        return text
    
    def _process_negative_currencies(self, text: str, context: FinancialContext) -> str:
        """Process negative currency amounts"""
        # Process all currency symbols for negative amounts
        for symbol, currency_info in self.currency_symbols.items():
            escaped_symbol = re.escape(symbol)

            # Pattern: -$50 (basic negative)
            pattern1 = rf'-\s*{escaped_symbol}(\d+(?:\.\d{{1,4}})?)\b'
            def replace_negative(match):
                amount_str = match.group(1)
                try:
                    amount = float(amount_str)
                    amount_words = self._currency_amount_to_words(amount, currency_info)
                    return f"negative {amount_words}"
                except ValueError:
                    return match.group(0)

            text = re.sub(pattern1, replace_negative, text)

            # Pattern: ($50) - parenthetical negative (basic)
            pattern2 = rf'\({escaped_symbol}(\d+(?:\.\d{{1,4}})?)\)'
            def replace_parenthetical_negative(match):
                amount_str = match.group(1)
                try:
                    amount = float(amount_str)
                    amount_words = self._currency_amount_to_words(amount, currency_info)
                    return f"negative {amount_words}"
                except ValueError:
                    return match.group(0)

            text = re.sub(pattern2, replace_parenthetical_negative, text)

            # Pattern: ($500K) - parenthetical negative with suffix
            pattern3 = rf'\({escaped_symbol}(\d+(?:\.\d+)?)\s*([KMBTkmbt])\)'
            def replace_parenthetical_negative_suffix(match):
                amount_str = match.group(1)
                suffix = match.group(2).upper()
                try:
                    amount = float(amount_str)
                    suffix_info = self.financial_suffixes[suffix]

                    # Convert to natural language
                    if amount == int(amount):
                        amount_words = self._number_to_words(int(amount))
                    else:
                        amount_words = self._decimal_to_words(amount)

                    suffix_name = suffix_info['name']
                    currency_name = currency_info['plural'] if amount != 1 else currency_info['name']

                    return f"negative {amount_words} {suffix_name} {currency_name}"
                except (ValueError, KeyError):
                    return match.group(0)

            text = re.sub(pattern3, replace_parenthetical_negative_suffix, text)

        return text
    
    def _process_basic_currencies(self, text: str, context: FinancialContext) -> str:
        """Process basic currency amounts ($100, €50.25)"""
        for symbol, currency_info in self.currency_symbols.items():
            escaped_symbol = re.escape(symbol)

            # Pattern: $100, €50.25, $1000000 (including large numbers without commas)
            # Use word boundary at the end to ensure we capture the full number
            pattern = rf'{escaped_symbol}(\d+(?:\.\d{{1,4}})?)\b'

            def replace_basic(match):
                amount_str = match.group(1)
                try:
                    amount = float(amount_str)
                    return self._currency_amount_to_words(amount, currency_info)
                except ValueError:
                    return match.group(0)

            text = re.sub(pattern, replace_basic, text)

        return text
    
    def _process_financial_terms(self, text: str, context: FinancialContext) -> str:
        """Process financial terminology and abbreviations"""
        financial_terms = {
            r'\bbps\b': 'basis points',
            r'\bbp\b': 'basis point',
            r'\bQ1\b': 'first quarter',
            r'\bQ2\b': 'second quarter', 
            r'\bQ3\b': 'third quarter',
            r'\bQ4\b': 'fourth quarter',
            r'\bYoY\b': 'year over year',
            r'\bMoM\b': 'month over month',
            r'\bP/E\b': 'price to earnings',
            r'\bROI\b': 'return on investment',
            r'\bEBITDA\b': 'E B I T D A'
        }
        
        for pattern, replacement in financial_terms.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text

    def _currency_amount_to_words(self, amount: float, currency_info: Dict[str, str]) -> str:
        """Convert currency amount to natural language"""
        if amount == 0:
            return f"zero {currency_info['plural']}"

        # Handle decimal amounts
        if amount != int(amount):
            integer_part = int(amount)
            decimal_part = round((amount - integer_part) * 100)

            # Main currency unit
            if integer_part == 0:
                main_text = ""
            elif integer_part == 1:
                main_text = f"one {currency_info['name']}"
            else:
                main_text = f"{self._number_to_words(integer_part)} {currency_info['plural']}"

            # Subunit (cents, pence, etc.)
            if decimal_part > 0:
                if currency_info['subunit']:
                    if decimal_part == 1:
                        sub_text = f"one {currency_info['subunit']}"
                    else:
                        sub_text = f"{self._number_to_words(decimal_part)} {currency_info['subunit_plural']}"

                    if main_text:
                        return f"{main_text} and {sub_text}"
                    else:
                        return sub_text
                else:
                    # For currencies without subunits, use decimal format
                    return f"{self._decimal_to_words(amount)} {currency_info['plural']}"
            else:
                return main_text if main_text else f"zero {currency_info['plural']}"
        else:
            # Whole number amounts
            integer_amount = int(amount)
            if integer_amount == 1:
                return f"one {currency_info['name']}"
            else:
                return f"{self._number_to_words(integer_amount)} {currency_info['plural']}"

    def _number_to_words(self, num: int) -> str:
        """Convert integer to words with support for large numbers"""
        if num == 0:
            return "zero"

        if num < 0:
            return f"negative {self._number_to_words(-num)}"

        # Handle very large numbers
        if num >= self.max_number_size:
            return str(num)  # Fallback to digits for extremely large numbers

        # Break down into groups of thousands
        groups = []
        group_names = ["", "thousand", "million", "billion", "trillion"]

        group_index = 0
        while num > 0 and group_index < len(group_names):
            group = num % 1000
            if group > 0:
                group_words = self._convert_hundreds(group)
                if group_names[group_index]:
                    group_words += f" {group_names[group_index]}"
                groups.append(group_words)
            num //= 1000
            group_index += 1

        return " ".join(reversed(groups))

    def _convert_hundreds(self, num: int) -> str:
        """Convert a number less than 1000 to words"""
        if num == 0:
            return ""

        result = []

        # Hundreds place
        if num >= 100:
            hundreds = num // 100
            result.append(f"{self.number_words[hundreds]} hundred")
            num %= 100

        # Tens and ones place
        if num >= 20:
            tens = (num // 10) * 10
            ones = num % 10
            if ones > 0:
                result.append(f"{self.number_words[tens]} {self.number_words[ones]}")
            else:
                result.append(self.number_words[tens])
        elif num > 0:
            result.append(self.number_words[num])

        return " ".join(result)

    def _decimal_to_words(self, num: float) -> str:
        """Convert decimal number to words"""
        integer_part = int(num)
        decimal_part = num - integer_part

        if integer_part == 0:
            integer_words = ""
        else:
            integer_words = self._number_to_words(integer_part)

        if decimal_part == 0:
            return integer_words if integer_words else "zero"

        # Convert decimal part to words
        decimal_str = f"{decimal_part:.10f}".split('.')[1].rstrip('0')
        decimal_words = " ".join([self.number_words[int(d)] for d in decimal_str])

        if integer_words:
            return f"{integer_words} point {decimal_words}"
        else:
            return f"zero point {decimal_words}"

    def analyze_currency_content(self, text: str) -> Dict[str, any]:
        """Analyze text for currency processing opportunities"""
        analysis = {
            'currency_amounts': [],
            'financial_terms': [],
            'processing_opportunities': [],
            'complexity_score': 0
        }

        # Find currency amounts
        for symbol in self.currency_symbols.keys():
            escaped_symbol = re.escape(symbol)
            pattern = rf'{escaped_symbol}[\d,.]+'
            matches = re.findall(pattern, text)
            analysis['currency_amounts'].extend(matches)

        # Find financial terms
        financial_patterns = [
            r'\b\d+(?:\.\d+)?\s*[KMBT]\b',  # Suffixes
            r'\bbps\b', r'\bQ[1-4]\b', r'\bYoY\b', r'\bMoM\b'  # Financial abbreviations
        ]

        for pattern in financial_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            analysis['financial_terms'].extend(matches)

        # Calculate complexity score
        analysis['complexity_score'] = (
            len(analysis['currency_amounts']) * 2 +
            len(analysis['financial_terms']) * 1
        )

        # Identify processing opportunities
        if analysis['currency_amounts']:
            analysis['processing_opportunities'].append('Currency amount normalization')
        if analysis['financial_terms']:
            analysis['processing_opportunities'].append('Financial terminology expansion')

        return analysis

    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currency codes"""
        return [info['code'] for info in self.currency_symbols.values()]

    def set_configuration(self, **kwargs):
        """Update processor configuration"""
        if 'enable_suffix_processing' in kwargs:
            self.enable_suffix_processing = kwargs['enable_suffix_processing']
        if 'enable_approximate_processing' in kwargs:
            self.enable_approximate_processing = kwargs['enable_approximate_processing']
        if 'enable_international_currencies' in kwargs:
            self.enable_international_currencies = kwargs['enable_international_currencies']
        if 'max_number_size' in kwargs:
            self.max_number_size = kwargs['max_number_size']
