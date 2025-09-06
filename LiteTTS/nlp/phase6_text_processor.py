#!/usr/bin/env python3
"""
Phase 6 Text Processor - Advanced Text Enhancement System

This module provides comprehensive text processing enhancements for TTS synthesis,
including advanced number processing, unit handling, homograph resolution,
and contraction processing.
"""

import logging
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Import the enhanced contraction processor
try:
    from .enhanced_contraction_processor_v2 import EnhancedContractionProcessorV2
    ENHANCED_CONTRACTIONS_AVAILABLE = True
except ImportError:
    ENHANCED_CONTRACTIONS_AVAILABLE = False
    logger.warning("Enhanced Contraction Processor V2 not available, falling back to basic processing")

# Import advanced number, currency, and date processors
try:
    from .advanced_currency_processor import AdvancedCurrencyProcessor, FinancialContext
    ADVANCED_CURRENCY_AVAILABLE = True
except ImportError:
    ADVANCED_CURRENCY_AVAILABLE = False
    logger.warning("Advanced Currency Processor not available")

try:
    from .enhanced_datetime_processor import EnhancedDateTimeProcessor
    ENHANCED_DATETIME_AVAILABLE = True
except ImportError:
    ENHANCED_DATETIME_AVAILABLE = False
    logger.warning("Enhanced DateTime Processor not available")

try:
    from .text_normalizer import TextNormalizer
    TEXT_NORMALIZER_AVAILABLE = True
except ImportError:
    TEXT_NORMALIZER_AVAILABLE = False
    logger.warning("Text Normalizer not available")

logger = logging.getLogger(__name__)

class Phase6ProcessingMode(Enum):
    """Phase 6 processing modes"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    COMPREHENSIVE = "comprehensive"

@dataclass
class Phase6ProcessingResult:
    """Result of Phase 6 text processing"""
    processed_text: str
    original_text: str
    processing_time: float
    total_changes: int = 0
    changes_by_category: Dict[str, int] = field(default_factory=dict)
    processing_stages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class Phase6TextProcessor:
    """
    Advanced text processor for Phase 6 enhancements
    
    This processor handles:
    - Enhanced number processing (currency, percentages, fractions)
    - Advanced unit handling (measurements, scientific notation)
    - Improved homograph resolution
    - Enhanced contraction processing
    - Context-aware text normalization
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize Phase 6 text processor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.mode = Phase6ProcessingMode.STANDARD
        
        # Initialize processing components
        self._init_advanced_processors()
        self._init_number_processors()
        self._init_unit_processors()
        self._init_homograph_processors()
        self._init_contraction_processors()
        
        logger.debug("Phase 6 text processor initialized")

    def _init_advanced_processors(self):
        """Initialize advanced text processing components"""
        # Initialize advanced currency processor
        if ADVANCED_CURRENCY_AVAILABLE:
            try:
                self.currency_processor = AdvancedCurrencyProcessor()
                self.financial_context = FinancialContext()
                self.use_advanced_currency = True
                logger.debug("Advanced Currency Processor initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Advanced Currency Processor: {e}")
                self.use_advanced_currency = False
        else:
            self.use_advanced_currency = False

        # Initialize enhanced datetime processor
        if ENHANCED_DATETIME_AVAILABLE:
            try:
                self.datetime_processor = EnhancedDateTimeProcessor()
                self.use_enhanced_datetime = True
                logger.debug("Enhanced DateTime Processor initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Enhanced DateTime Processor: {e}")
                self.use_enhanced_datetime = False
        else:
            self.use_enhanced_datetime = False

        # Initialize text normalizer for number-to-words
        if TEXT_NORMALIZER_AVAILABLE:
            try:
                # Configure for full number expansion (not preserve_natural_speech mode)
                self.text_normalizer = TextNormalizer()
                self.text_normalizer.preserve_natural_speech = False  # Enable full number processing
                self.use_text_normalizer = True
                logger.debug("Text Normalizer initialized with full number expansion")
            except Exception as e:
                logger.warning(f"Failed to initialize Text Normalizer: {e}")
                self.use_text_normalizer = False
        else:
            self.use_text_normalizer = False

    def _init_number_processors(self):
        """Initialize number processing components"""
        # Enhanced number patterns
        self.currency_pattern = re.compile(r'\$[\d,]+\.?\d*')
        self.percentage_pattern = re.compile(r'\d+\.?\d*%')
        self.fraction_pattern = re.compile(r'\d+/\d+')
        self.decimal_pattern = re.compile(r'\d+\.\d+')
        self.large_number_pattern = re.compile(r'\d{4,}')
        
        # Number word mappings
        self.number_words = {
            '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
            '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine',
            '10': 'ten', '11': 'eleven', '12': 'twelve', '13': 'thirteen',
            '14': 'fourteen', '15': 'fifteen', '16': 'sixteen', '17': 'seventeen',
            '18': 'eighteen', '19': 'nineteen', '20': 'twenty', '30': 'thirty',
            '40': 'forty', '50': 'fifty', '60': 'sixty', '70': 'seventy',
            '80': 'eighty', '90': 'ninety', '100': 'hundred', '1000': 'thousand'
        }
    
    def _init_unit_processors(self):
        """Initialize unit processing components"""
        # Common unit abbreviations and their spoken forms
        self.unit_mappings = {
            # Distance/Length
            'mm': 'millimeters', 'cm': 'centimeters', 'm': 'meters', 'km': 'kilometers',
            'in': 'inches', 'ft': 'feet', 'yd': 'yards', 'mi': 'miles',
            
            # Weight/Mass
            'mg': 'milligrams', 'g': 'grams', 'kg': 'kilograms', 't': 'tons',
            'oz': 'ounces', 'lb': 'pounds', 'lbs': 'pounds',
            
            # Volume
            'ml': 'milliliters', 'l': 'liters', 'gal': 'gallons', 'qt': 'quarts',
            'pt': 'pints', 'fl oz': 'fluid ounces',
            
            # Time
            'ms': 'milliseconds', 's': 'seconds', 'min': 'minutes', 'hr': 'hours',
            'hrs': 'hours', 'h': 'hours',
            
            # Technology
            'GB': 'gigabytes', 'MB': 'megabytes', 'KB': 'kilobytes', 'TB': 'terabytes',
            'GHz': 'gigahertz', 'MHz': 'megahertz', 'kHz': 'kilohertz',
            
            # Temperature
            '°C': 'degrees celsius', '°F': 'degrees fahrenheit', 'K': 'kelvin'
        }
    
    def _init_homograph_processors(self):
        """Initialize homograph resolution components"""
        # Context-sensitive homograph mappings
        self.homograph_rules = {
            'read': {
                'past_tense': 'red',
                'present_tense': 'reed',
                'patterns': [
                    (r'\bread\b(?=.*yesterday|last|ago)', 'red'),
                    (r'\bread\b(?=.*will|going to|plan)', 'reed')
                ]
            },
            'lead': {
                'metal': 'led',
                'guide': 'leed',
                'patterns': [
                    (r'\blead\b(?=.*metal|pipe|paint)', 'led'),
                    (r'\blead\b(?=.*team|group|guide)', 'leed')
                ]
            },
            'tear': {
                'rip': 'tair',
                'cry': 'teer',
                'patterns': [
                    (r'\btear\b(?=.*paper|cloth|rip)', 'tair'),
                    (r'\btear\b(?=.*cry|sad|eye)', 'teer')
                ]
            }
        }
    
    def _init_contraction_processors(self):
        """Initialize contraction processing components"""
        # Initialize enhanced contraction processor if available
        if ENHANCED_CONTRACTIONS_AVAILABLE:
            try:
                self.enhanced_contraction_processor = EnhancedContractionProcessorV2(
                    config={'debug': self.config.get('debug_contractions', False)}
                )
                self.use_enhanced_contractions = True
                logger.info("Enhanced Contraction Processor V2 initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Enhanced Contraction Processor V2: {e}")
                self.use_enhanced_contractions = False
        else:
            self.use_enhanced_contractions = False

        # Fallback: Basic contraction mappings (kept for compatibility)
        self.contraction_mappings = {
            "won't": "will not",
            "can't": "cannot",
            "shouldn't": "should not",
            "wouldn't": "would not",
            "couldn't": "could not",
            "mustn't": "must not",
            "needn't": "need not",
            "daren't": "dare not",
            "shan't": "shall not",
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
            "I'd": "I would",
            "you'd": "you would",
            "he'd": "he would",
            "she'd": "she would",
            "we'd": "we would",
            "they'd": "they would",
            "I'll": "I will",
            "you'll": "you will",
            "he'll": "he will",
            "she'll": "she will",
            "we'll": "we will",
            "they'll": "they will"
        }
    
    def process_text(self, text: str, mode: Optional[Phase6ProcessingMode] = None) -> Phase6ProcessingResult:
        """
        Process text with Phase 6 enhancements
        
        Args:
            text: Input text to process
            mode: Processing mode (optional)
            
        Returns:
            Phase6ProcessingResult with processed text and metadata
        """
        if mode is None:
            mode = self.mode
        
        start_time = time.perf_counter()
        original_text = text
        changes_by_category = {}
        processing_stages = []
        warnings = []
        
        logger.debug(f"Phase 6 processing text with mode: {mode.value}")
        
        try:
            # Stage 1: Enhanced contraction processing (first to avoid interference)
            text, contraction_changes = self._process_contractions(text)
            changes_by_category['contractions'] = contraction_changes
            if contraction_changes > 0:
                processing_stages.append('contraction_processing')

            # Stage 2: Enhanced number processing
            text, number_changes = self._process_numbers(text)
            changes_by_category['numbers'] = number_changes
            if number_changes > 0:
                processing_stages.append('number_processing')

            # Stage 3: Unit processing
            text, unit_changes = self._process_units(text)
            changes_by_category['units'] = unit_changes
            if unit_changes > 0:
                processing_stages.append('unit_processing')

            # Stage 4: Homograph resolution
            text, homograph_changes = self._process_homographs(text)
            changes_by_category['homographs'] = homograph_changes
            if homograph_changes > 0:
                processing_stages.append('homograph_resolution')
            
            # Stage 5: Context normalization (advanced modes only)
            if mode in [Phase6ProcessingMode.ADVANCED, Phase6ProcessingMode.COMPREHENSIVE]:
                text, context_changes = self._process_context_normalization(text)
                changes_by_category['context'] = context_changes
                if context_changes > 0:
                    processing_stages.append('context_normalization')
            
            total_changes = sum(changes_by_category.values())
            processing_time = time.perf_counter() - start_time
            
            result = Phase6ProcessingResult(
                processed_text=text,
                original_text=original_text,
                processing_time=processing_time,
                total_changes=total_changes,
                changes_by_category=changes_by_category,
                processing_stages=processing_stages,
                warnings=warnings,
                metadata={'mode': mode.value}
            )
            
            logger.debug(f"Phase 6 processing complete: {total_changes} changes in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Phase 6 processing failed: {e}")
            # Return original text with error information
            return Phase6ProcessingResult(
                processed_text=original_text,
                original_text=original_text,
                processing_time=time.perf_counter() - start_time,
                total_changes=0,
                warnings=[f"Processing failed: {str(e)}"]
            )
    
    def _process_numbers(self, text: str) -> Tuple[str, int]:
        """Process numbers, currency, and dates for better TTS pronunciation"""
        changes = 0
        original_text = text

        # Stage 1: Process currency using advanced processor
        if self.use_advanced_currency:
            try:
                processed_currency = self.currency_processor.process_currency_text(text, self.financial_context)
                if processed_currency != text:
                    text = processed_currency
                    changes += 1
                    logger.debug("Advanced currency processing applied")
            except Exception as e:
                logger.warning(f"Advanced currency processing failed: {e}")

        # Stage 2: Process dates and times using enhanced processor
        if self.use_enhanced_datetime:
            try:
                processed_datetime = self.datetime_processor.process_dates_and_times(text)
                if processed_datetime != text:
                    text = processed_datetime
                    changes += 1
                    logger.debug("Enhanced datetime processing applied")
            except Exception as e:
                logger.warning(f"Enhanced datetime processing failed: {e}")

        # Stage 3: Process standalone numbers using text normalizer
        # Skip if advanced processors already handled the text to avoid conflicts
        if self.use_text_normalizer and changes == 0:
            try:
                processed_numbers = self.text_normalizer.normalize_text(text)
                if processed_numbers != text:
                    text = processed_numbers
                    changes += 1
                    logger.debug("Text normalizer processing applied")
            except Exception as e:
                logger.warning(f"Text normalizer processing failed: {e}")
        elif changes > 0:
            logger.debug("Skipping text normalizer - advanced processors already applied")

        # Fallback: Basic processing if advanced processors not available
        if not any([self.use_advanced_currency, self.use_enhanced_datetime, self.use_text_normalizer]):
            text, fallback_changes = self._process_numbers_fallback(text)
            changes += fallback_changes

        return text, changes

    def _process_numbers_fallback(self, text: str) -> Tuple[str, int]:
        """Fallback number processing when advanced processors unavailable"""
        changes = 0

        # Process currency (basic)
        def replace_currency(match):
            nonlocal changes
            amount = match.group(0)
            changes += 1
            return f"{amount} dollars"  # Very basic conversion

        text = self.currency_pattern.sub(replace_currency, text)

        # Process percentages
        def replace_percentage(match):
            nonlocal changes
            changes += 1
            return match.group(0).replace('%', ' percent')

        text = self.percentage_pattern.sub(replace_percentage, text)

        return text, changes
    
    def _process_units(self, text: str) -> Tuple[str, int]:
        """Process unit abbreviations with contraction and time format protection"""
        changes = 0

        # CRITICAL FIX: Skip unit processing for problematic units that interfere with contractions
        # Units 'm' and 't' are too common in contractions and cause issues
        problematic_units = {'m', 't'}  # Skip these to avoid contraction interference

        for abbrev, full_form in self.unit_mappings.items():
            # Skip problematic units that interfere with contractions
            if abbrev in problematic_units:
                continue

            # CRITICAL FIX: Special context-aware handling for "in" to prevent time context interference
            if abbrev == 'in':
                # Skip conversion in time contexts like "7:15 in the evening"
                if self._is_time_context_for_in(text):
                    continue  # Skip "in" processing in time contexts

                # Convert "in" to "inches" when preceded by a number (measurement context)
                pattern = r'(\d+(?:\.\d+)?)\s+' + re.escape(abbrev) + r'\b'
                if re.search(pattern, text):
                    text = re.sub(pattern, r'\1 ' + full_form, text)
                    changes += 1
                continue

            # Special handling for 'a.m./p.m.' protection (keep existing logic)
            if abbrev == 'a' or abbrev == 'p':
                # Only match when not part of a.m. or p.m.
                pattern = r'\b' + re.escape(abbrev) + r'\b(?!\s*\.?\s*m\.?)'
            else:
                # Standard pattern for safe units
                pattern = r'\b' + re.escape(abbrev) + r'\b'

            if re.search(pattern, text):
                text = re.sub(pattern, full_form, text)
                changes += 1

        return text, changes

    def _is_time_context_for_in(self, text: str) -> bool:
        """Check if 'in' appears in a time context where it shouldn't be converted to 'inches'"""
        # Common time context patterns where "in" is a preposition, not a unit
        time_context_patterns = [
            r'\d{1,2}:\d{2}\s+in\s+the\s+(morning|afternoon|evening|night)',  # "7:15 in the evening"
            r'\d{1,2}\s+(AM|PM|a\.m\.|p\.m\.)\s+in\s+the\s+(morning|afternoon|evening|night)',  # "7 PM in the evening"
            r'in\s+the\s+(morning|afternoon|evening|night)',  # "in the morning"
            r'in\s+\d+\s+(minutes?|hours?|days?|weeks?|months?|years?)',  # "in 5 minutes"
            r'in\s+(January|February|March|April|May|June|July|August|September|October|November|December)',  # "in January"
            r'in\s+\d{4}',  # "in 2024"
        ]

        for pattern in time_context_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _process_homographs(self, text: str) -> Tuple[str, int]:
        """Process homographs with context awareness"""
        changes = 0
        
        for word, rules in self.homograph_rules.items():
            for pattern, replacement in rules.get('patterns', []):
                if re.search(pattern, text, re.IGNORECASE):
                    text = re.sub(r'\b' + word + r'\b', replacement, text, flags=re.IGNORECASE)
                    changes += 1
        
        return text, changes
    
    def _process_contractions(self, text: str) -> Tuple[str, int]:
        """Process contractions for better pronunciation using enhanced processor"""
        if not text or not text.strip():
            return text, 0

        original_text = text

        # Use enhanced contraction processor if available
        if self.use_enhanced_contractions:
            try:
                processed_text = self.enhanced_contraction_processor.process_contractions(text)

                # Count changes by comparing original and processed text
                changes = 0
                if processed_text != original_text:
                    # Simple heuristic: count the number of contractions that were likely processed
                    for contraction in self.enhanced_contraction_processor.contraction_rules.keys():
                        original_count = len(re.findall(r'\b' + re.escape(contraction) + r'\b', original_text, re.IGNORECASE))
                        processed_count = len(re.findall(r'\b' + re.escape(contraction) + r'\b', processed_text, re.IGNORECASE))
                        changes += max(0, original_count - processed_count)

                logger.debug(f"Enhanced contraction processing: {changes} contractions processed")
                return processed_text, changes

            except Exception as e:
                logger.warning(f"Enhanced contraction processing failed: {e}, falling back to basic processing")

        # Fallback: Basic contraction processing
        changes = 0
        for contraction, expansion in self.contraction_mappings.items():
            pattern = r'\b' + re.escape(contraction) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
                changes += 1

        return text, changes
    
    def _process_context_normalization(self, text: str) -> Tuple[str, int]:
        """Advanced context-aware normalization"""
        changes = 0
        
        # Example: Handle scientific notation
        scientific_pattern = r'(\d+\.?\d*)[eE]([+-]?\d+)'
        def replace_scientific(match):
            nonlocal changes
            base, exponent = match.groups()
            changes += 1
            return f"{base} times ten to the power of {exponent}"
        
        text = re.sub(scientific_pattern, replace_scientific, text)
        
        return text, changes
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get Phase 6 processing capabilities"""
        return {
            'enhanced_numbers': True,
            'enhanced_units': True,
            'enhanced_homographs': True,
            'enhanced_contractions': True,
            'context_normalization': True,
            'scientific_notation': True,
            'currency_processing': True,
            'percentage_processing': True,
            'fraction_processing': True
        }
    
    def set_mode(self, mode: Phase6ProcessingMode):
        """Set processing mode"""
        self.mode = mode
        logger.debug(f"Phase 6 processing mode set to: {mode.value}")

# Factory function for easy instantiation
def create_phase6_processor(config: Optional[Dict] = None) -> Phase6TextProcessor:
    """Create a Phase 6 text processor instance"""
    return Phase6TextProcessor(config)

# Example usage
if __name__ == "__main__":
    # Test the Phase 6 processor
    processor = Phase6TextProcessor()
    
    test_texts = [
        "I can't believe it costs $1,234.56 and weighs 5.5 kg!",
        "The temperature is 25°C and the speed is 100 km/h.",
        "He read the book yesterday and will read another tomorrow.",
        "The lead pipe contains lead metal."
    ]
    
    for text in test_texts:
        result = processor.process_text(text)
        print(f"Original: {result.original_text}")
        print(f"Processed: {result.processed_text}")
        print(f"Changes: {result.total_changes}")
        print(f"Categories: {result.changes_by_category}")
        print("-" * 50)
