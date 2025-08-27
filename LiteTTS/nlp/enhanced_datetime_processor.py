#!/usr/bin/env python3
"""
Enhanced date and time processor for natural TTS pronunciation
Fixes dash-separated dates and improves natural date/time reading
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, date
import calendar
import logging

logger = logging.getLogger(__name__)

class EnhancedDateTimeProcessor:
    """Enhanced date and time processing for natural TTS pronunciation"""
    
    def __init__(self):
        self.date_patterns = self._load_date_patterns()
        self.time_patterns = self._load_time_patterns()
        self.month_names = self._load_month_names()
        self.ordinal_suffixes = self._load_ordinal_suffixes()
        self.weekday_names = self._load_weekday_names()
        
        # Configuration
        self.use_ordinal_dates = True
        self.use_full_month_names = True
        self.use_natural_time_format = True
        self.handle_relative_dates = True
        
    def _load_date_patterns(self) -> List[Tuple[str, str]]:
        """Load date pattern matching rules"""
        return [
            # Written dates with ordinals (PRIORITY: Handle first)
            (r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(st|nd|rd|th),?\s+(\d{4})\b', 'written_date_ordinal'),
            (r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{1,2})(st|nd|rd|th),?\s+(\d{4})\b', 'written_date_abbrev_ordinal'),

            # ISO format: YYYY-MM-DD (the problematic one)
            (r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b', 'iso_date'),

            # US format: MM/DD/YYYY
            (r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', 'us_date'),

            # European format: DD/MM/YYYY
            (r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b', 'eu_date'),

            # Alternative dash format: MM-DD-YYYY
            (r'\b(\d{1,2})-(\d{1,2})-(\d{4})\b', 'us_dash_date'),

            # Short year formats
            (r'\b(\d{1,2})/(\d{1,2})/(\d{2})\b', 'short_us_date'),
            (r'\b(\d{1,2})-(\d{1,2})-(\d{2})\b', 'short_dash_date'),

            # Month-day format: MM-DD or MM/DD (avoid matching time ranges)
            (r'(?<!\d:)(?<!\d\d:)\b(\d{1,2})-(\d{1,2})\b(?!\d)(?!:)', 'month_day_dash'),
            (r'(?<!\d:)(?<!\d\d:)\b(\d{1,2})/(\d{1,2})\b(?!\d)(?!:)', 'month_day_slash'),
            
            # Year only
            (r'\b(19|20)\d{2}\b', 'year_only'),
            
            # Relative dates
            (r'\b(today|tomorrow|yesterday)\b', 'relative_date'),
            (r'\b(next|last)\s+(week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', 'relative_period'),
            
            # Written dates: January 1, 2023 or 1 January 2023
            (r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b', 'written_date_us'),
            (r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b', 'written_date_eu'),
            
            # Abbreviated months
            (r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{1,2}),?\s+(\d{4})\b', 'abbrev_date'),
        ]
    
    def _load_time_patterns(self) -> List[Tuple[str, str]]:
        """Load time pattern matching rules"""
        return [
            # Enhanced time ranges (PRIORITY: Handle first)
            (r'\b([0-2]?\d):([0-5]\d)\s*-\s*([0-2]?\d):([0-5]\d)\b', 'time_range_24'),
            (r'\b([0-1]?\d):([0-5]\d)\s*(AM|PM|am|pm)\s*-\s*([0-1]?\d):([0-5]\d)\s*(AM|PM|am|pm)\b', 'time_range_12_ampm'),
            (r'\b([0-1]?\d)\s*(AM|PM|am|pm)\s*-\s*([0-1]?\d)\s*(AM|PM|am|pm)\b', 'time_range_hour_ampm'),

            # 24-hour format: HH:MM:SS (not followed by AM/PM)
            (r'\b([0-2]?\d):([0-5]\d):([0-5]\d)\b(?!\s*(?:AM|PM|am|pm|a\.m\.|p\.m\.))', 'time_24_seconds'),

            # 24-hour format: HH:MM (not followed by AM/PM)
            (r'\b([0-2]?\d):([0-5]\d)\b(?!\s*(?:AM|PM|am|pm|a\.m\.|p\.m\.))', 'time_24'),

            # 12-hour format with AM/PM
            (r'\b([0-1]?\d):([0-5]\d)\s*(AM|PM|am|pm|a\.m\.|p\.m\.)\b', 'time_12_ampm'),

            # Time with seconds and AM/PM
            (r'\b([0-1]?\d):([0-5]\d):([0-5]\d)\s*(AM|PM|am|pm|a\.m\.|p\.m\.)\b', 'time_12_seconds_ampm'),

            # Casual time expressions
            (r'\b(noon|midnight|midday)\b', 'casual_time'),
            (r'\b(\d{1,2})\s*o\'?clock\b', 'oclock_time'),
        ]
    
    def _load_month_names(self) -> Dict[str, str]:
        """Load month number to name mappings"""
        return {
            '1': 'January', '01': 'January',
            '2': 'February', '02': 'February',
            '3': 'March', '03': 'March',
            '4': 'April', '04': 'April',
            '5': 'May', '05': 'May',
            '6': 'June', '06': 'June',
            '7': 'July', '07': 'July',
            '8': 'August', '08': 'August',
            '9': 'September', '09': 'September',
            '10': 'October',
            '11': 'November',
            '12': 'December'
        }
    
    def _load_ordinal_suffixes(self) -> Dict[str, str]:
        """Load ordinal number suffixes"""
        return {
            '1': 'first', '21': 'twenty-first', '31': 'thirty-first',
            '2': 'second', '22': 'twenty-second',
            '3': 'third', '23': 'twenty-third',
            '4': 'fourth', '24': 'twenty-fourth',
            '5': 'fifth', '25': 'twenty-fifth',
            '6': 'sixth', '26': 'twenty-sixth',
            '7': 'seventh', '27': 'twenty-seventh',
            '8': 'eighth', '28': 'twenty-eighth',
            '9': 'ninth', '29': 'twenty-ninth',
            '10': 'tenth', '30': 'thirtieth',
            '11': 'eleventh',
            '12': 'twelfth',
            '13': 'thirteenth',
            '14': 'fourteenth',
            '15': 'fifteenth',
            '16': 'sixteenth',
            '17': 'seventeenth',
            '18': 'eighteenth',
            '19': 'nineteenth',
            '20': 'twentieth'
        }
    
    def _load_weekday_names(self) -> Dict[int, str]:
        """Load weekday names"""
        return {
            0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
            4: 'Friday', 5: 'Saturday', 6: 'Sunday'
        }
    
    def process_dates_and_times(self, text: str) -> str:
        """Process all dates and times in text for natural pronunciation"""
        logger.debug(f"Processing dates and times in: {text[:100]}...")
        
        # Process dates first
        text = self._process_dates(text)
        
        # Then process times
        text = self._process_times(text)
        
        logger.debug(f"Date/time processing result: {text[:100]}...")
        return text
    
    def _process_dates(self, text: str) -> str:
        """Process date expressions"""
        for pattern, date_type in self.date_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            
            # Process matches in reverse order to maintain positions
            for match in reversed(matches):
                natural_date = self._convert_date_to_natural(match, date_type)
                if natural_date:
                    text = text[:match.start()] + natural_date + text[match.end():]
        
        return text
    
    def _process_times(self, text: str) -> str:
        """Process time expressions"""
        processed_ranges = []  # Track processed character ranges

        for pattern, time_type in self.time_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))

            # Process matches in reverse order to maintain positions
            for match in reversed(matches):
                # Check if this match overlaps with already processed ranges
                match_start, match_end = match.start(), match.end()
                overlaps = any(start <= match_start < end or start < match_end <= end or
                             (match_start <= start and match_end >= end)
                             for start, end in processed_ranges)

                if not overlaps:
                    natural_time = self._convert_time_to_natural(match, time_type)
                    if natural_time:
                        text = text[:match_start] + natural_time + text[match_end:]
                        # Update processed ranges (adjust for text length change)
                        length_change = len(natural_time) - (match_end - match_start)
                        processed_ranges = [(s + length_change if s >= match_start else s,
                                           e + length_change if e > match_start else e)
                                          for s, e in processed_ranges]
                        processed_ranges.append((match_start, match_start + len(natural_time)))

        return text
    
    def _convert_date_to_natural(self, match, date_type: str) -> Optional[str]:
        """Convert a date match to natural language"""
        try:
            if date_type == 'written_date_ordinal':
                # January 1st, 2024 format
                month_name, day, ordinal_suffix, year = match.groups()
                return self._format_written_date(month_name, day, year)

            elif date_type == 'written_date_abbrev_ordinal':
                # Jan. 1st, 2024 format
                month_abbrev, day, ordinal_suffix, year = match.groups()
                month_name = self._expand_month_abbreviation(month_abbrev)
                return self._format_written_date(month_name, day, year)

            elif date_type == 'iso_date':
                # YYYY-MM-DD format (the problematic one)
                year, month, day = match.groups()
                return self._format_natural_date(year, month, day)

            elif date_type == 'us_date':
                # MM/DD/YYYY format
                month, day, year = match.groups()
                return self._format_natural_date(year, month, day)

            elif date_type == 'eu_date':
                # DD.MM.YYYY format
                day, month, year = match.groups()
                return self._format_natural_date(year, month, day)

            elif date_type == 'us_dash_date':
                # MM-DD-YYYY format
                month, day, year = match.groups()
                return self._format_natural_date(year, month, day)
            
            elif date_type == 'short_us_date':
                # MM/DD/YY format
                month, day, year = match.groups()
                full_year = f"20{year}" if int(year) < 50 else f"19{year}"
                return self._format_natural_date(full_year, month, day)
            
            elif date_type == 'short_dash_date':
                # MM-DD-YY format
                month, day, year = match.groups()
                full_year = f"20{year}" if int(year) < 50 else f"19{year}"
                return self._format_natural_date(full_year, month, day)
            
            elif date_type == 'month_day_dash' or date_type == 'month_day_slash':
                # MM-DD or MM/DD format
                month, day = match.groups()
                return self._format_natural_date(None, month, day)
            
            elif date_type == 'year_only':
                # Just a year
                year = match.group(0)
                return self._format_year(year)
            
            elif date_type == 'relative_date':
                # today, tomorrow, yesterday
                return match.group(0)  # Keep as-is, they're already natural
            
            elif date_type == 'relative_period':
                # next week, last month, etc.
                return match.group(0)  # Keep as-is, they're already natural
            
            elif date_type == 'written_date_us':
                # January 1, 2023
                month_name, day, year = match.groups()
                return self._format_written_date(month_name, day, year)
            
            elif date_type == 'written_date_eu':
                # 1 January 2023
                day, month_name, year = match.groups()
                return self._format_written_date(month_name, day, year)
            
            elif date_type == 'abbrev_date':
                # Jan 1, 2023
                month_abbrev, day, year = match.groups()
                month_name = self._expand_month_abbreviation(month_abbrev)
                return self._format_written_date(month_name, day, year)
            
        except Exception as e:
            logger.warning(f"Failed to convert date {match.group(0)}: {e}")
            return None
        
        return None
    
    def _convert_time_to_natural(self, match, time_type: str) -> Optional[str]:
        """Convert a time match to natural language"""
        try:
            if time_type == 'time_range_24':
                # 24-hour time range: 09:00-17:00
                groups = match.groups()
                start_hour, start_minute, end_hour, end_minute = [int(g) for g in groups]
                start_time = self._format_natural_time(start_hour, start_minute, is_24_hour=True)
                end_time = self._format_natural_time(end_hour, end_minute, is_24_hour=True)
                return f"{start_time} to {end_time}"

            elif time_type == 'time_range_12_ampm':
                # 12-hour time range with AM/PM: 9:00 AM - 5:00 PM
                groups = match.groups()
                start_hour, start_minute, start_ampm, end_hour, end_minute, end_ampm = groups
                start_time = self._format_natural_time(int(start_hour), int(start_minute), ampm=start_ampm.upper())
                end_time = self._format_natural_time(int(end_hour), int(end_minute), ampm=end_ampm.upper())
                return f"{start_time} to {end_time}"

            elif time_type == 'time_range_hour_ampm':
                # Hour-only time range: 9 AM - 5 PM
                groups = match.groups()
                start_hour, start_ampm, end_hour, end_ampm = groups
                start_time = self._format_natural_time(int(start_hour), 0, ampm=start_ampm.upper())
                end_time = self._format_natural_time(int(end_hour), 0, ampm=end_ampm.upper())
                return f"{start_time} to {end_time}"

            elif time_type == 'time_24' or time_type == 'time_24_seconds':
                # 24-hour format
                groups = match.groups()
                hour = int(groups[0])
                minute = int(groups[1])
                seconds = int(groups[2]) if len(groups) > 2 else None

                return self._format_natural_time(hour, minute, seconds, is_24_hour=True)

            elif time_type == 'time_12_ampm' or time_type == 'time_12_seconds_ampm':
                # 12-hour format with AM/PM
                groups = match.groups()
                hour = int(groups[0])
                minute = int(groups[1])
                seconds = int(groups[2]) if len(groups) > 3 else None
                ampm = groups[-1].upper()

                return self._format_natural_time(hour, minute, seconds, ampm=ampm)

            elif time_type == 'casual_time':
                # noon, midnight, etc.
                return match.group(0)  # Keep as-is

            elif time_type == 'oclock_time':
                # 3 o'clock
                hour = match.group(1)
                return f"{self._number_to_words(hour)} o'clock"
            
        except Exception as e:
            logger.warning(f"Failed to convert time {match.group(0)}: {e}")
            return None
        
        return None
    
    def _format_natural_date(self, year: Optional[str], month: str, day: str) -> str:
        """Format a date in natural language"""
        month_name = self.month_names.get(month, month)
        
        if self.use_ordinal_dates:
            day_ordinal = self._get_ordinal_day(day)
        else:
            day_ordinal = day
        
        if year:
            return f"{month_name} {day_ordinal}, {year}"
        else:
            return f"{month_name} {day_ordinal}"
    
    def _format_written_date(self, month_name: str, day: str, year: str) -> str:
        """Format an already written date"""
        if self.use_ordinal_dates:
            day_ordinal = self._get_ordinal_day(day)
        else:
            day_ordinal = day
        
        return f"{month_name} {day_ordinal}, {year}"
    
    def _format_year(self, year: str) -> str:
        """Format a year for natural pronunciation"""
        year_int = int(year)

        if 1000 <= year_int <= 1999:
            # e.g., 1995 -> "nineteen ninety-five"
            first_part = self._number_to_words(str(year_int // 100))
            second_part = self._number_to_words(str(year_int % 100))
            return f"{first_part} {second_part}"
        elif year_int == 2000:
            # Special case: 2000 -> "two thousand"
            return "two thousand"
        elif 2001 <= year_int <= 2009:
            # e.g., 2005 -> "two thousand five"
            remainder = year_int % 10
            if remainder == 0:
                return "two thousand"
            else:
                return f"two thousand {self._number_to_words(str(remainder))}"
        elif 2010 <= year_int <= 2099:
            # e.g., 2023 -> "twenty twenty-three"
            first_part = self._number_to_words(str(year_int // 100))
            second_part = self._number_to_words(str(year_int % 100))
            return f"{first_part} {second_part}"
        else:
            # Default to reading as a regular number
            return self._number_to_words(year)
    
    def _format_natural_time(self, hour: int, minute: int, seconds: Optional[int] = None,
                           ampm: Optional[str] = None, is_24_hour: bool = False) -> str:
        """Format time in natural language"""
        if is_24_hour and not ampm:
            # Convert 24-hour to 12-hour for natural speech
            if hour == 0:
                hour_12 = 12
                ampm = "AM"
            elif hour < 12:
                hour_12 = hour
                ampm = "AM"
            elif hour == 12:
                hour_12 = 12
                ampm = "PM"
            else:
                hour_12 = hour - 12
                ampm = "PM"
        elif ampm:
            # 12-hour format with provided AM/PM
            hour_12 = hour
            # ampm is already provided, don't modify it
        else:
            # Default case - assume 12-hour format without AM/PM
            hour_12 = hour
        
        # Format the time naturally
        if minute == 0 and not seconds:
            # e.g., "3 o'clock"
            time_str = f"{self._number_to_words(str(hour_12))} o'clock"
        elif minute == 15:
            time_str = f"quarter past {self._number_to_words(str(hour_12))}"
        elif minute == 30:
            time_str = f"half past {self._number_to_words(str(hour_12))}"
        elif minute == 45:
            next_hour = hour_12 + 1 if hour_12 < 12 else 1
            time_str = f"quarter to {self._number_to_words(str(next_hour))}"
        else:
            hour_word = self._number_to_words(str(hour_12))
            minute_word = self._number_to_words(str(minute))
            time_str = f"{hour_word} {minute_word}"
        
        if ampm:
            time_str += f" {ampm}"
        
        if seconds:
            seconds_word = self._number_to_words(str(seconds))
            time_str += f" and {seconds_word} seconds"
        
        return time_str
    
    def _get_ordinal_day(self, day: str) -> str:
        """Convert day number to ordinal word"""
        day_str = str(int(day))  # Remove leading zeros

        # Use predefined ordinal mappings
        if day_str in self.ordinal_suffixes:
            return self.ordinal_suffixes[day_str]

        # Handle other days by converting to words + ordinal suffix
        day_int = int(day)
        day_words = self._number_to_words(str(day_int))

        # Add appropriate ordinal suffix
        if 10 <= day_int % 100 <= 20:
            return f"{day_words}th"
        else:
            suffix_map = {1: "st", 2: "nd", 3: "rd"}
            suffix = suffix_map.get(day_int % 10, "th")
            return f"{day_words}{suffix}"
    
    def _expand_month_abbreviation(self, abbrev: str) -> str:
        """Expand month abbreviation to full name"""
        abbrev_map = {
            'Jan': 'January', 'Feb': 'February', 'Mar': 'March',
            'Apr': 'April', 'May': 'May', 'Jun': 'June',
            'Jul': 'July', 'Aug': 'August', 'Sep': 'September',
            'Oct': 'October', 'Nov': 'November', 'Dec': 'December'
        }
        return abbrev_map.get(abbrev, abbrev)
    
    def _number_to_words(self, number_str: str) -> str:
        """Convert number to words (simplified version)"""
        # This is a simplified implementation
        # In a full implementation, you'd want a more comprehensive number-to-words converter

        try:
            num = int(number_str)

            if num == 0:
                return 'zero'
            elif 1 <= num <= 31:
                number_map = {
                    1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
                    6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
                    11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen',
                    15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen',
                    19: 'nineteen', 20: 'twenty', 21: 'twenty-one', 22: 'twenty-two',
                    23: 'twenty-three', 24: 'twenty-four', 25: 'twenty-five',
                    26: 'twenty-six', 27: 'twenty-seven', 28: 'twenty-eight',
                    29: 'twenty-nine', 30: 'thirty', 31: 'thirty-one'
                }
                return number_map.get(num, number_str)
            elif 32 <= num <= 99:
                tens = num // 10
                ones = num % 10
                tens_map = {3: 'thirty', 4: 'forty', 5: 'fifty', 6: 'sixty',
                           7: 'seventy', 8: 'eighty', 9: 'ninety'}
                ones_map = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
                           6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}

                if ones == 0:
                    return tens_map.get(tens, number_str)
                else:
                    return f"{tens_map.get(tens, str(tens))}-{ones_map.get(ones, str(ones))}"
            else:
                return number_str
        except ValueError:
            return number_str
    
    def analyze_datetime_patterns(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for date and time patterns"""
        info = {
            'iso_dates': [],
            'us_dates': [],
            'times': [],
            'relative_dates': [],
            'problematic_patterns': []
        }
        
        # Find ISO dates (the problematic ones)
        iso_dates = re.findall(r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b', text)
        info['iso_dates'] = [f"{y}-{m}-{d}" for y, m, d in iso_dates]
        
        # Find US dates
        us_dates = re.findall(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', text)
        info['us_dates'] = [f"{m}/{d}/{y}" for m, d, y in us_dates]
        
        # Find times
        times = re.findall(r'\b(\d{1,2}):(\d{2})\b', text)
        info['times'] = [f"{h}:{m}" for h, m in times]
        
        # Find relative dates
        relative_dates = re.findall(r'\b(today|tomorrow|yesterday|next|last)\b', text, re.IGNORECASE)
        info['relative_dates'] = relative_dates
        
        # Check for problematic patterns
        if re.search(r'\d{4}-\d{1,2}-\d{1,2}', text):
            info['problematic_patterns'].append('ISO date format (causes dash pronunciation)')
        
        return info
    
    def set_configuration(self, use_ordinal_dates: bool = None,
                         use_full_month_names: bool = None,
                         use_natural_time_format: bool = None,
                         handle_relative_dates: bool = None):
        """Set configuration options"""
        if use_ordinal_dates is not None:
            self.use_ordinal_dates = use_ordinal_dates
        if use_full_month_names is not None:
            self.use_full_month_names = use_full_month_names
        if use_natural_time_format is not None:
            self.use_natural_time_format = use_natural_time_format
        if handle_relative_dates is not None:
            self.handle_relative_dates = handle_relative_dates
        
        logger.info(f"DateTime processor configuration updated: "
                   f"use_ordinal_dates={self.use_ordinal_dates}, "
                   f"use_full_month_names={self.use_full_month_names}, "
                   f"use_natural_time_format={self.use_natural_time_format}, "
                   f"handle_relative_dates={self.handle_relative_dates}")
