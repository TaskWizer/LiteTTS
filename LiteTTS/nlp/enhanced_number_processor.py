#!/usr/bin/env python3
"""
Enhanced Number Processing for Phase 6: Advanced Text Processing
Addresses specific issues with comma-separated numbers, large numbers, and sequential digits
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NumberProcessingResult:
    """Result of number processing"""
    processed_text: str
    original_text: str
    changes_made: List[str]
    numbers_processed: int
    processing_mode: str

class EnhancedNumberProcessor:
    """Enhanced number processor for natural speech synthesis"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize enhanced number processor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.number_patterns = self._compile_enhanced_patterns()
        self.context_patterns = self._compile_context_patterns()
        
        # Load configuration settings
        self._load_config()
        
        logger.info("Enhanced Number Processor initialized")
    
    def _load_config(self):
        """Load configuration settings"""
        try:
            # Load from main config if available
            import json
            from pathlib import Path

            # Try multiple config paths
            config_paths = [
                Path("config.json"),
                Path("../config.json"),
                Path("../../config.json")
            ]

            config_loaded = False
            for config_path in config_paths:
                if config_path.exists():
                    with open(config_path) as f:
                        main_config = json.load(f)
                        text_processing = main_config.get('text_processing', {})

                        self.natural_speech = text_processing.get('natural_speech', True)
                        self.sequential_digit_threshold = text_processing.get('sequential_digit_threshold', 4)
                        config_loaded = True
                        break

            if not config_loaded:
                # Fallback defaults
                self.natural_speech = True
                self.sequential_digit_threshold = 4
                
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}")
            self.natural_speech = True
            self.sequential_digit_threshold = 4
    
    def _compile_enhanced_patterns(self) -> Dict[str, re.Pattern]:
        """Compile enhanced regex patterns for number processing"""
        return {
            # Comma-separated numbers: 10,000 or 1,001
            'comma_separated': re.compile(r'\b\d{1,3}(?:,\d{3})+\b'),
            
            # Large numbers without commas: 10000, 1001
            'large_numbers': re.compile(r'\b\d{4,}\b'),
            
            # Sequential digits that might need individual pronunciation: 1718, 2024
            'sequential_digits': re.compile(r'\b\d{4,6}\b'),
            
            # Decimal numbers: 3.14, 10.5
            'decimal': re.compile(r'\b\d+\.\d+\b'),
            
            # Percentages: 50%, 3.14%
            'percentage': re.compile(r'\b\d+(?:\.\d+)?%\b'),
            
            # Ordinals: 1st, 2nd, 3rd, 4th
            'ordinal': re.compile(r'\b(\d+)(?:st|nd|rd|th)\b', re.IGNORECASE),
            
            # Years: 1990, 2024
            'year': re.compile(r'\b(19|20)\d{2}\b'),
            
            # Phone numbers: (555) 123-4567, 555-123-4567
            'phone': re.compile(r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'),
            
            # Time: 3:30, 15:45
            'time': re.compile(r'\b([0-1]?[0-9]|2[0-3]):([0-5][0-9])(?::([0-5][0-9]))?\s*(AM|PM)?\b', re.IGNORECASE),
            
            # Currency: $100, $1,000.50
            'currency': re.compile(r'\$([0-9,]+(?:\.[0-9]{2})?)')
        }
    
    def _compile_context_patterns(self) -> Dict[str, List[Tuple[re.Pattern, str]]]:
        """Compile context patterns for intelligent number processing"""
        patterns = {}
        
        # Sequential digit contexts (when to pronounce as individual digits)
        patterns['sequential_digits'] = [
            # Years should be pronounced as years, not individual digits
            (re.compile(r'\b(in|year|since|from|until|by)\s+\d{4}\b', re.IGNORECASE), 'year'),
            
            # Model numbers, product codes should be individual digits
            (re.compile(r'\b(model|part|code|serial|version|build)\s*#?\s*\d{4,}\b', re.IGNORECASE), 'individual'),
            
            # Flight numbers should be individual digits
            (re.compile(r'\b(flight|gate|terminal)\s*#?\s*\d{4,}\b', re.IGNORECASE), 'individual'),
            
            # Room numbers, addresses might be individual
            (re.compile(r'\b(room|suite|apartment|apt)\s*#?\s*\d{4,}\b', re.IGNORECASE), 'individual'),
            
            # Phone number contexts
            (re.compile(r'\b(phone|call|dial|number)\s*:?\s*\d{4,}\b', re.IGNORECASE), 'individual'),
        ]
        
        # Large number contexts
        patterns['large_numbers'] = [
            # Population, statistics should be full numbers
            (re.compile(r'\b(population|people|users|customers|sales|revenue)\s*:?\s*\d{4,}\b', re.IGNORECASE), 'full_number'),
            
            # Measurements, quantities should be full numbers
            (re.compile(r'\b\d{4,}\s*(feet|meters|miles|kilometers|pounds|kilograms|dollars)\b', re.IGNORECASE), 'full_number'),
        ]
        
        return patterns
    
    def process_numbers(self, text: str) -> NumberProcessingResult:
        """Main number processing method
        
        Args:
            text: Input text to process
            
        Returns:
            NumberProcessingResult with processed text and metadata
        """
        logger.debug(f"Processing numbers in text: {text[:100]}...")
        
        original_text = text
        changes_made = []
        numbers_processed = 0
        
        # Process in order of specificity (most specific first)
        
        # 1. Currency (before other number processing)
        text, currency_changes = self._process_currency(text)
        if currency_changes:
            changes_made.extend(currency_changes)
            numbers_processed += len(currency_changes)
        
        # 2. Percentages
        text, percentage_changes = self._process_percentages(text)
        if percentage_changes:
            changes_made.extend(percentage_changes)
            numbers_processed += len(percentage_changes)
        
        # 3. Time expressions
        text, time_changes = self._process_time(text)
        if time_changes:
            changes_made.extend(time_changes)
            numbers_processed += len(time_changes)
        
        # 4. Phone numbers
        text, phone_changes = self._process_phone_numbers(text)
        if phone_changes:
            changes_made.extend(phone_changes)
            numbers_processed += len(phone_changes)
        
        # 5. Ordinals
        text, ordinal_changes = self._process_ordinals(text)
        if ordinal_changes:
            changes_made.extend(ordinal_changes)
            numbers_processed += len(ordinal_changes)
        
        # 6. Comma-separated numbers (CRITICAL FIX)
        text, comma_changes = self._process_comma_separated_numbers(text)
        if comma_changes:
            changes_made.extend(comma_changes)
            numbers_processed += len(comma_changes)
        
        # 7. Sequential digits (context-aware)
        text, sequential_changes = self._process_sequential_digits(text)
        if sequential_changes:
            changes_made.extend(sequential_changes)
            numbers_processed += len(sequential_changes)
        
        # 8. Decimal numbers
        text, decimal_changes = self._process_decimal_numbers(text)
        if decimal_changes:
            changes_made.extend(decimal_changes)
            numbers_processed += len(decimal_changes)
        
        # 9. Years (special handling)
        text, year_changes = self._process_years(text)
        if year_changes:
            changes_made.extend(year_changes)
            numbers_processed += len(year_changes)
        
        # 10. Remaining large numbers
        text, large_changes = self._process_large_numbers(text)
        if large_changes:
            changes_made.extend(large_changes)
            numbers_processed += len(large_changes)
        
        processing_mode = "natural_speech" if self.natural_speech else "full_expansion"
        
        result = NumberProcessingResult(
            processed_text=text,
            original_text=original_text,
            changes_made=changes_made,
            numbers_processed=numbers_processed,
            processing_mode=processing_mode
        )
        
        logger.debug(f"Number processing complete: {numbers_processed} numbers processed")
        return result
    
    def _process_comma_separated_numbers(self, text: str) -> Tuple[str, List[str]]:
        """Process comma-separated numbers: 10,000 → ten thousand (not ten, zero zero zero)"""
        changes = []
        
        def replace_comma_number(match):
            number_str = match.group()
            # Remove commas and convert to integer
            clean_number = number_str.replace(',', '')
            try:
                number = int(clean_number)
                words = self._integer_to_words(number)
                changes.append(f"Comma-separated number: {number_str} → {words}")
                return words
            except ValueError:
                return number_str
        
        processed_text = self.number_patterns['comma_separated'].sub(replace_comma_number, text)
        return processed_text, changes
    
    def _process_sequential_digits(self, text: str) -> Tuple[str, List[str]]:
        """Process sequential digits with context awareness"""
        changes = []
        
        def replace_sequential(match):
            number_str = match.group()
            
            # Skip if it's a year (handled separately)
            if self.number_patterns['year'].match(number_str):
                return number_str
            
            # Check context to determine processing mode
            context_mode = self._determine_sequential_context(text, match.start(), match.end())
            
            if context_mode == 'individual':
                # Pronounce as individual digits: 1718 → one seven one eight
                digits = [self._digit_to_word(d) for d in number_str]
                result = ' '.join(digits)
                changes.append(f"Sequential digits (individual): {number_str} → {result}")
                return result
            elif context_mode == 'year':
                # Process as year
                result = self._year_to_words(number_str)
                changes.append(f"Sequential digits (year): {number_str} → {result}")
                return result
            else:
                # Process as regular number if context suggests it
                try:
                    number = int(number_str)
                    if number >= 1000:
                        result = self._integer_to_words(number)
                        changes.append(f"Sequential digits (number): {number_str} → {result}")
                        return result
                except ValueError:
                    pass
                
                return number_str
        
        processed_text = self.number_patterns['sequential_digits'].sub(replace_sequential, text)
        return processed_text, changes

    def _determine_sequential_context(self, text: str, start_pos: int, end_pos: int) -> str:
        """Determine how to process sequential digits based on context"""
        # Get surrounding context (50 characters before and after)
        context_start = max(0, start_pos - 50)
        context_end = min(len(text), end_pos + 50)
        context = text[context_start:context_end].lower()

        # Check against context patterns
        for pattern, mode in self.context_patterns.get('sequential_digits', []):
            if pattern.search(context):
                return mode

        # Default behavior based on length and natural speech setting
        number_str = text[start_pos:end_pos]
        if len(number_str) >= self.sequential_digit_threshold:
            return 'individual' if self.natural_speech else 'number'

        return 'number'

    def _process_large_numbers(self, text: str) -> Tuple[str, List[str]]:
        """Process large numbers (4+ digits) with context awareness"""
        changes = []

        def replace_large_number(match):
            number_str = match.group()

            # Skip if already processed by other patterns
            if ',' in number_str or '.' in number_str:
                return number_str

            # Check context
            context_mode = self._determine_large_number_context(text, match.start(), match.end())

            try:
                number = int(number_str)

                if context_mode == 'full_number' or not self.natural_speech:
                    # Convert to full words: 1001 → one thousand one
                    result = self._integer_to_words(number)
                    changes.append(f"Large number: {number_str} → {result}")
                    return result
                else:
                    # In natural speech mode, preserve some large numbers
                    return number_str

            except ValueError:
                return number_str

        processed_text = self.number_patterns['large_numbers'].sub(replace_large_number, text)
        return processed_text, changes

    def _determine_large_number_context(self, text: str, start_pos: int, end_pos: int) -> str:
        """Determine how to process large numbers based on context"""
        # Get surrounding context
        context_start = max(0, start_pos - 50)
        context_end = min(len(text), end_pos + 50)
        context = text[context_start:context_end].lower()

        # Check against context patterns
        for pattern, mode in self.context_patterns.get('large_numbers', []):
            if pattern.search(context):
                return mode

        return 'preserve'

    def _process_currency(self, text: str) -> Tuple[str, List[str]]:
        """Process currency amounts"""
        changes = []

        def replace_currency(match):
            amount = match.group(1)
            result = self._currency_to_words(amount)
            changes.append(f"Currency: ${amount} → {result}")
            return result

        processed_text = self.number_patterns['currency'].sub(replace_currency, text)
        return processed_text, changes

    def _process_percentages(self, text: str) -> Tuple[str, List[str]]:
        """Process percentage values"""
        changes = []

        def replace_percentage(match):
            percent_str = match.group()
            number_part = percent_str.rstrip('%')
            number_words = self._number_to_words(number_part)
            result = f"{number_words} percent"
            changes.append(f"Percentage: {percent_str} → {result}")
            return result

        processed_text = self.number_patterns['percentage'].sub(replace_percentage, text)
        return processed_text, changes

    def _process_time(self, text: str) -> Tuple[str, List[str]]:
        """Process time expressions"""
        changes = []

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
                result += f" {ampm.upper()}"

            original = f"{hour}:{minute}"
            if ampm:
                original += f" {ampm}"
            changes.append(f"Time: {original} → {result}")
            return result

        processed_text = self.number_patterns['time'].sub(replace_time, text)
        return processed_text, changes

    def _process_phone_numbers(self, text: str) -> Tuple[str, List[str]]:
        """Process phone numbers as individual digits"""
        changes = []

        def replace_phone(match):
            area_code, exchange, number = match.group(1), match.group(2), match.group(3)

            # Convert each part to individual digits
            area_digits = ' '.join([self._digit_to_word(d) for d in area_code])
            exchange_digits = ' '.join([self._digit_to_word(d) for d in exchange])
            number_digits = ' '.join([self._digit_to_word(d) for d in number])

            result = f"{area_digits} {exchange_digits} {number_digits}"
            original = match.group()
            changes.append(f"Phone: {original} → {result}")
            return result

        processed_text = self.number_patterns['phone'].sub(replace_phone, text)
        return processed_text, changes

    def _process_ordinals(self, text: str) -> Tuple[str, List[str]]:
        """Process ordinal numbers"""
        changes = []

        def replace_ordinal(match):
            number_str = match.group(1)
            result = self._ordinal_to_words(number_str)
            original = match.group()
            changes.append(f"Ordinal: {original} → {result}")
            return result

        processed_text = self.number_patterns['ordinal'].sub(replace_ordinal, text)
        return processed_text, changes

    def _process_decimal_numbers(self, text: str) -> Tuple[str, List[str]]:
        """Process decimal numbers"""
        changes = []

        def replace_decimal(match):
            decimal_str = match.group()
            result = self._number_to_words(decimal_str)
            changes.append(f"Decimal: {decimal_str} → {result}")
            return result

        processed_text = self.number_patterns['decimal'].sub(replace_decimal, text)
        return processed_text, changes

    def _process_years(self, text: str) -> Tuple[str, List[str]]:
        """Process year numbers with special pronunciation"""
        changes = []

        def replace_year(match):
            year_str = match.group()
            result = self._year_to_words(year_str)
            changes.append(f"Year: {year_str} → {result}")
            return result

        processed_text = self.number_patterns['year'].sub(replace_year, text)
        return processed_text, changes

    # Core conversion methods
    def _number_to_words(self, number_str: str) -> str:
        """Convert number to words with enhanced comma handling"""
        try:
            # Remove commas for processing
            clean_number = number_str.replace(',', '')

            # Handle decimals
            if '.' in clean_number:
                integer_part, decimal_part = clean_number.split('.')
                integer_words = self._integer_to_words(int(integer_part))
                decimal_words = ' '.join([self._digit_to_word(d) for d in decimal_part])
                return f"{integer_words} point {decimal_words}"
            else:
                return self._integer_to_words(int(clean_number))
        except ValueError:
            return number_str

    def _integer_to_words(self, num: int) -> str:
        """Convert integer to words with enhanced large number support"""
        if num == 0:
            return "zero"

        if num < 0:
            return "negative " + self._integer_to_words(-num)

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
            thousands = self._integer_to_words(num // 1000)
            remainder = num % 1000
            if remainder == 0:
                return thousands + " thousand"
            else:
                return thousands + " thousand " + self._integer_to_words(remainder)
        elif num < 1000000000:
            millions = self._integer_to_words(num // 1000000)
            remainder = num % 1000000
            if remainder == 0:
                return millions + " million"
            else:
                return millions + " million " + self._integer_to_words(remainder)
        elif num < 1000000000000:
            billions = self._integer_to_words(num // 1000000000)
            remainder = num % 1000000000
            if remainder == 0:
                return billions + " billion"
            else:
                return billions + " billion " + self._integer_to_words(remainder)
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

            # Special cases for ordinals
            if base_word.endswith("one"):
                return base_word[:-3] + "first"
            elif base_word.endswith("two"):
                return base_word[:-3] + "second"
            elif base_word.endswith("three"):
                return base_word[:-5] + "third"
            elif base_word.endswith("five"):
                return base_word[:-4] + "fifth"
            elif base_word.endswith("eight"):
                return base_word[:-5] + "eighth"
            elif base_word.endswith("nine"):
                return base_word[:-4] + "ninth"
            elif base_word.endswith("twelve"):
                return base_word[:-6] + "twelfth"
            elif base_word.endswith("y"):
                return base_word[:-1] + "ieth"
            else:
                return base_word + "th"
        except ValueError:
            return number_str

    def _year_to_words(self, year_str: str) -> str:
        """Convert year to words with special pronunciation rules"""
        try:
            year = int(year_str)

            # Years 2000-2009: "two thousand", "two thousand one", etc.
            if 2000 <= year <= 2009:
                if year == 2000:
                    return "two thousand"
                else:
                    return f"two thousand {self._integer_to_words(year - 2000)}"

            # Years 2010-2099: "twenty ten", "twenty eleven", etc.
            elif 2010 <= year <= 2099:
                return f"twenty {self._integer_to_words(year - 2000)}"

            # Years 1900-1999: "nineteen hundred", "nineteen ninety", etc.
            elif 1900 <= year <= 1999:
                if year % 100 == 0:
                    return "nineteen hundred"
                else:
                    return f"nineteen {self._integer_to_words(year % 100)}"

            # Years 1800-1899: "eighteen hundred", "eighteen ninety", etc.
            elif 1800 <= year <= 1899:
                if year % 100 == 0:
                    return "eighteen hundred"
                else:
                    return f"eighteen {self._integer_to_words(year % 100)}"

            # Other years: use standard number conversion
            else:
                return self._integer_to_words(year)

        except ValueError:
            return year_str

    def _currency_to_words(self, amount_str: str) -> str:
        """Convert currency amount to words"""
        try:
            # Remove commas
            clean_amount = amount_str.replace(',', '')

            if '.' in clean_amount:
                dollars, cents = clean_amount.split('.')
                dollar_words = self._integer_to_words(int(dollars))
                cent_words = self._integer_to_words(int(cents))

                dollar_unit = "dollar" if int(dollars) == 1 else "dollars"
                cent_unit = "cent" if int(cents) == 1 else "cents"

                if int(cents) == 0:
                    return f"{dollar_words} {dollar_unit}"
                else:
                    return f"{dollar_words} {dollar_unit} and {cent_words} {cent_unit}"
            else:
                dollar_words = self._integer_to_words(int(clean_amount))
                dollar_unit = "dollar" if int(clean_amount) == 1 else "dollars"
                return f"{dollar_words} {dollar_unit}"
        except ValueError:
            return amount_str
