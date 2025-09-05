#!/usr/bin/env python3
"""
Unified Text Processing Pipeline
Integrates all enhanced text processors for comprehensive TTS text processing
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# Import existing processors
from .text_normalizer import TextNormalizer
from .clean_text_normalizer import CleanTextNormalizer
from .homograph_resolver import HomographResolver
from .phonetic_processor import PhoneticProcessor
from .spell_processor import SpellProcessor
from .prosody_analyzer import ProsodyAnalyzer
from .emotion_detector import EmotionDetector
from .context_adapter import ContextAdapter
from .naturalness_enhancer import NaturalnessEnhancer

# Import our enhanced processors
from .advanced_currency_processor import AdvancedCurrencyProcessor, FinancialContext
from .enhanced_datetime_processor import EnhancedDateTimeProcessor
from .advanced_symbol_processor import AdvancedSymbolProcessor
from .espeak_enhanced_symbol_processor import EspeakEnhancedSymbolProcessor
from .phonetic_contraction_processor import PhoneticContractionProcessor
from .interjection_fix_processor import InterjectionFixProcessor
from .pronunciation_rules_processor import PronunciationRulesProcessor
from .ticker_symbol_processor import TickerSymbolProcessor
from .proper_name_pronunciation_processor import ProperNamePronunciationProcessor

# Import audio quality enhancers
from .audio_quality_enhancer import audio_quality_enhancer
from .voice_modulation_system import VoiceModulationSystem
from .dynamic_emotion_intonation import DynamicEmotionIntonationSystem

# Import Phase 6 enhancements (optional)
try:
    from .phase6_text_processor import Phase6TextProcessor, Phase6ProcessingResult
    PHASE6_AVAILABLE = True
except ImportError:
    PHASE6_AVAILABLE = False
    Phase6TextProcessor = None
    Phase6ProcessingResult = None

# Import preprocessing
from ..text.phonemizer_preprocessor import phonemizer_preprocessor

logger = logging.getLogger(__name__)

# Log Phase 6 availability after logger is initialized
if not PHASE6_AVAILABLE:
    logger.warning("Phase 6 text processor not available, advanced text processing will be limited")

class ProcessingMode(Enum):
    """Text processing modes"""
    BASIC = "basic"                    # Basic normalization only
    STANDARD = "standard"              # Standard TTS processing
    ENHANCED = "enhanced"              # Enhanced with advanced processors
    PREMIUM = "premium"                # Full pipeline with all enhancements

@dataclass
class ProcessingOptions:
    """Unified processing options"""
    mode: ProcessingMode = ProcessingMode.ENHANCED
    
    # Core processing options
    normalize_text: bool = True
    resolve_homographs: bool = True
    process_phonetics: bool = True
    handle_spell_functions: bool = True
    
    # Enhanced processing options
    use_advanced_currency: bool = True
    use_enhanced_datetime: bool = True
    use_advanced_symbols: bool = True
    use_espeak_enhanced_symbols: bool = True  # eSpeak-enhanced symbol processing (fixes "?" pronunciation)
    use_clean_normalizer: bool = True
    use_phonetic_contractions: bool = False  # Legacy expansion mode (disabled by default)
    use_interjection_fixes: bool = True     # Fix interjection pronunciation (Hmm→hmmm)
    use_pronunciation_rules: bool = True    # Natural contraction pronunciation rules (NEW DEFAULT)
    use_ticker_symbol_processing: bool = True  # Fix TSLA→TEE-SLAW to T-S-L-A
    use_proper_name_pronunciation: bool = True  # Fix Elon→alon, Joy→joie, acquisition→ek-wah-zi·shn
    
    # Audio quality options
    enhance_audio_quality: bool = True
    apply_voice_modulation: bool = True
    use_dynamic_emotion: bool = True

    # Phase 6 options
    use_phase6_processing: bool = True
    use_enhanced_numbers: bool = True
    use_enhanced_units: bool = True
    use_enhanced_homographs: bool = True
    use_enhanced_contractions: bool = True

    # Context options
    financial_context: Optional[FinancialContext] = None
    preserve_original_on_error: bool = True

    # Performance options
    enable_parallel_processing: bool = False
    max_processing_time: float = 30.0  # seconds

@dataclass
class ProcessingResult:
    """Result of unified text processing"""
    processed_text: str
    original_text: str
    processing_time: float
    mode_used: ProcessingMode
    
    # Processing stages completed
    stages_completed: List[str] = field(default_factory=list)
    changes_made: List[str] = field(default_factory=list)
    issues_found: List[str] = field(default_factory=list)
    
    # Enhancement data
    currency_enhancements: int = 0
    datetime_enhancements: int = 0
    audio_enhancements: int = 0

    # Phase 6 enhancement data
    phase6_result: Optional[Phase6ProcessingResult] = None
    phase6_enhancements: int = 0

    # Performance metrics
    stage_timings: Dict[str, float] = field(default_factory=dict)

class UnifiedTextProcessor:
    """Unified text processing pipeline integrating all processors"""
    
    def __init__(self, enable_advanced_features: bool = True, config: Optional[Dict] = None):
        """Initialize unified text processor

        Args:
            enable_advanced_features: Enable advanced processing features
            config: Configuration dictionary
        """
        self.enable_advanced_features = enable_advanced_features
        self.config = config or {}

        # Load configuration if not provided
        if not self.config:
            self.config = self._load_config()

        # Initialize core processors
        self._init_core_processors()

        # Initialize enhanced processors
        self._init_enhanced_processors()

        # Initialize audio quality processors
        self._init_audio_processors()

        # Initialize Phase 6 processors
        self._init_phase6_processors()

        logger.info("Unified Text Processor initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        try:
            import json
            from pathlib import Path
            config_path = Path("config.json")
            if config_path.exists():
                with open(config_path) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config.json: {e}")
        return {}

    def _is_section_enabled(self, section_name: str) -> bool:
        """Check if a configuration section is enabled

        Args:
            section_name: Name of the configuration section (e.g., 'text_processing')

        Returns:
            bool: True if section is enabled, False otherwise
        """
        section = self.config.get(section_name, {})
        return section.get("enabled", True)  # Default to enabled if not specified

    def _is_feature_enabled(self, section_name: str, feature_name: str) -> bool:
        """Check if a specific feature within a section is enabled

        Args:
            section_name: Name of the configuration section
            feature_name: Name of the feature within the section

        Returns:
            bool: True if both section and feature are enabled, False otherwise
        """
        # First check if parent section is enabled
        if not self._is_section_enabled(section_name):
            return False

        # Then check if specific feature is enabled
        section = self.config.get(section_name, {})
        return section.get(feature_name, True)  # Default to enabled if not specified
    
    def _init_core_processors(self):
        """Initialize core text processors"""
        self.text_normalizer = TextNormalizer()
        self.clean_normalizer = CleanTextNormalizer(config=self.config)
        self.homograph_resolver = HomographResolver()
        self.phonetic_processor = PhoneticProcessor(config=self.config)
        self.spell_processor = SpellProcessor()
        self.prosody_analyzer = ProsodyAnalyzer()
        
        if self.enable_advanced_features:
            self.emotion_detector = EmotionDetector()
            self.context_adapter = ContextAdapter()
            self.naturalness_enhancer = NaturalnessEnhancer()
    
    def _init_enhanced_processors(self):
        """Initialize enhanced processors"""
        self.currency_processor = AdvancedCurrencyProcessor()
        self.datetime_processor = EnhancedDateTimeProcessor()
        self.symbol_processor = AdvancedSymbolProcessor()

        # Initialize eSpeak-enhanced symbol processor
        espeak_config = self.config.get("symbol_processing", {}).get("espeak_enhanced_processing", {})
        self.espeak_symbol_processor = EspeakEnhancedSymbolProcessor(espeak_config)

        self.phonetic_contraction_processor = PhoneticContractionProcessor(config=self.config)
        self.interjection_processor = InterjectionFixProcessor()
        self.pronunciation_rules_processor = PronunciationRulesProcessor(config=self.config)
        self.ticker_symbol_processor = TickerSymbolProcessor()
        self.proper_name_processor = ProperNamePronunciationProcessor(config=self.config)

        logger.debug("Enhanced processors initialized")
    
    def _init_audio_processors(self):
        """Initialize audio quality processors"""
        try:
            self.voice_modulation = VoiceModulationSystem()
            self.dynamic_emotion = DynamicEmotionIntonationSystem()
            logger.debug("Audio quality processors initialized")
        except Exception as e:
            logger.warning(f"Some audio processors failed to initialize: {e}")
            self.voice_modulation = None
            self.dynamic_emotion = None

    def _init_phase6_processors(self):
        """Initialize Phase 6 processors"""
        if not PHASE6_AVAILABLE:
            logger.info("Phase 6 text processor not available, skipping initialization")
            self.phase6_processor = None
            return

        try:
            self.phase6_processor = Phase6TextProcessor(self.config)
            logger.debug("Phase 6 processors initialized")
        except Exception as e:
            logger.warning(f"Phase 6 processors failed to initialize: {e}")
            self.phase6_processor = None
    
    def process_text(self, text: str, options: Optional[ProcessingOptions] = None) -> ProcessingResult:
        """Main text processing method

        Args:
            text: Input text to process
            options: Processing options

        Returns:
            ProcessingResult with processed text and metadata
        """
        if options is None:
            options = ProcessingOptions()

        # Reload configuration for hot reload support
        self.config = self._load_config()

        start_time = time.perf_counter()
        original_text = text

        logger.info(f"Processing text with mode: {options.mode.value}")
        logger.debug(f"Input text: {text[:100]}...")

        result = ProcessingResult(
            processed_text=text,
            original_text=original_text,
            processing_time=0.0,
            mode_used=options.mode
        )
        
        try:
            # Route to appropriate processing pipeline
            if options.mode == ProcessingMode.BASIC:
                text = self._process_basic(text, options, result)
            elif options.mode == ProcessingMode.STANDARD:
                text = self._process_standard(text, options, result)
            elif options.mode == ProcessingMode.ENHANCED:
                text = self._process_enhanced(text, options, result)
            elif options.mode == ProcessingMode.PREMIUM:
                text = self._process_premium(text, options, result)
            
            result.processed_text = text
            result.processing_time = time.perf_counter() - start_time
            
            logger.info(f"Text processing complete in {result.processing_time:.3f}s")
            logger.debug(f"Output text: {text[:100]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            result.issues_found.append(f"Processing error: {e}")
            result.processing_time = time.perf_counter() - start_time
            
            if options.preserve_original_on_error:
                result.processed_text = original_text
                logger.warning("Returning original text due to processing error")
            
            return result
    
    def _process_basic(self, text: str, options: ProcessingOptions, result: ProcessingResult) -> str:
        """Basic processing pipeline"""
        stage_start = time.perf_counter()

        # Only basic normalization (minimal processing)
        if options.normalize_text:
            # For basic mode, only do minimal normalization to preserve original text
            # Don't use the full text normalizer which would convert currency/dates
            result.stages_completed.append("basic_normalization")
            result.changes_made.append("Applied basic text normalization")

        result.stage_timings["basic"] = time.perf_counter() - stage_start
        return text
    
    def _process_standard(self, text: str, options: ProcessingOptions, result: ProcessingResult) -> str:
        """Standard processing pipeline"""
        stage_start = time.perf_counter()
        
        # Phonemizer preprocessing
        preprocessing_result = phonemizer_preprocessor.preprocess_text(text, preserve_word_count=True)
        text = preprocessing_result.processed_text
        if preprocessing_result.changes_made:
            result.changes_made.extend(preprocessing_result.changes_made)
            result.stages_completed.append("phonemizer_preprocessing")
        
        # Core processing steps
        if options.handle_spell_functions:
            text = self.spell_processor.handle_spell_functions(text)
            result.stages_completed.append("spell_processing")
        
        if options.process_phonetics:
            # Check if phonetic processing is enabled in beta features
            beta_features = self.config.get("beta_features", {})
            phonetic_config = beta_features.get("phonetic_processing", {})
            if phonetic_config.get("enabled", False):
                text = self.phonetic_processor.process_phonetics(text)
                result.stages_completed.append("phonetic_processing")
                logger.debug("Applied beta phonetic processing")
            else:
                logger.debug("Phonetic processing disabled (beta feature not enabled)")
                result.stages_completed.append("phonetic_processing_skipped")
        
        if options.resolve_homographs:
            text = self.homograph_resolver.resolve_homographs(text)
            result.stages_completed.append("homograph_resolution")
        
        if options.normalize_text:
            text = self.text_normalizer.normalize_text(text)
            result.stages_completed.append("text_normalization")
        
        # Prosody processing
        text = self.prosody_analyzer.process_conversational_features(text)
        text = self.prosody_analyzer.enhance_intonation_markers(text)
        result.stages_completed.append("prosody_analysis")
        
        result.stage_timings["standard"] = time.perf_counter() - stage_start
        return text

    def _process_enhanced(self, text: str, options: ProcessingOptions, result: ProcessingResult) -> str:
        """Enhanced processing pipeline with advanced processors"""
        stage_start = time.perf_counter()

        # Check if text processing is enabled at all
        if not self._is_section_enabled("text_processing"):
            logger.debug("Text processing disabled - skipping all text processing stages")
            result.stages_completed.append("text_processing_disabled")
            result.stage_timings["enhanced"] = time.perf_counter() - stage_start
            return text

        # Phase 6 processing (FIRST - comprehensive text enhancement)
        if (hasattr(options, 'use_phase6_processing') and options.use_phase6_processing and
            self.phase6_processor and self._is_section_enabled("text_processing")):
            phase6_start = time.perf_counter()
            original_text = text
            phase6_result = self.phase6_processor.process_text(text)
            text = phase6_result.processed_text
            result.phase6_result = phase6_result
            result.phase6_enhancements = phase6_result.total_changes

            if phase6_result.total_changes > 0:
                result.changes_made.append(f"Applied Phase 6 enhancements: {phase6_result.total_changes} total changes")
                result.stages_completed.append("phase6_processing")
                logger.debug(f"Phase 6 processing: {phase6_result.total_changes} enhancements applied in {phase6_result.processing_time:.3f}s")

                # Add detailed changes by category
                for category, count in phase6_result.changes_by_category.items():
                    if count > 0:
                        result.changes_made.append(f"Phase 6 {category}: {count} changes")
            else:
                result.stages_completed.append("phase6_no_changes")

            result.stage_timings["phase6_processing"] = time.perf_counter() - phase6_start

        # Pronunciation rules processing (FIRST - natural contraction pronunciation)
        if (hasattr(options, 'use_pronunciation_rules') and options.use_pronunciation_rules and
            self._is_feature_enabled("text_processing", "pronunciation_fixes")):
            original_text = text
            text = self.pronunciation_rules_processor.process_pronunciation_rules(text)
            if text != original_text:
                result.changes_made.append("Applied natural pronunciation rules")
                result.stages_completed.append("pronunciation_rules")
                logger.debug(f"Pronunciation rules processing: {len(text) - len(original_text)} character change")

        # Legacy phonetic contraction processing (OPTIONAL - only if explicitly enabled)
        if (hasattr(options, 'use_phonetic_contractions') and options.use_phonetic_contractions and
            self._is_feature_enabled("text_processing", "expand_contractions")):
            original_text = text
            text = self.phonetic_contraction_processor.process_contractions(text, mode="phonetic_expansion")
            if text != original_text:
                result.changes_made.append("Applied legacy contraction expansion")
                result.stages_completed.append("phonetic_contractions")
                logger.debug(f"Legacy contraction processing: {len(text) - len(original_text)} character change")

        # Interjection pronunciation fixes (SECOND - after contractions)
        if (hasattr(options, 'use_interjection_fixes') and options.use_interjection_fixes and
            self._is_section_enabled("interjection_handling")):
            original_text = text
            text = self.interjection_processor.fix_interjection_pronunciation(text)
            if text != original_text:
                result.changes_made.append("Applied interjection pronunciation fixes")
                result.stages_completed.append("interjection_fixes")
                logger.debug(f"Interjection processing: {len(text) - len(original_text)} character change")

        # Ticker symbol processing (THIRD - fix TSLA→TEE-SLAW to T-S-L-A)
        if (hasattr(options, 'use_ticker_symbol_processing') and options.use_ticker_symbol_processing and
            self._is_section_enabled("pronunciation_dictionary")):
            original_text = text
            ticker_result = self.ticker_symbol_processor.process_ticker_symbols(text)
            text = ticker_result.processed_text
            if text != original_text:
                result.changes_made.append(f"Applied ticker symbol processing: {', '.join(ticker_result.tickers_found)}")
                result.stages_completed.append("ticker_symbols")
                logger.debug(f"Ticker symbol processing: {len(ticker_result.tickers_found)} symbols processed")

        # Proper name pronunciation processing (FOURTH - fix Elon→alon, Joy→joie, etc.)
        if (hasattr(options, 'use_proper_name_pronunciation') and options.use_proper_name_pronunciation and
            self._is_section_enabled("pronunciation_dictionary")):
            original_text = text
            text = self.proper_name_processor.process_proper_name_pronunciation(text)
            if text != original_text:
                result.changes_made.append("Applied proper name pronunciation fixes")
                result.stages_completed.append("proper_name_pronunciation")
                logger.debug(f"Proper name pronunciation processing: {len(text) - len(original_text)} character change")

        # Phonemizer preprocessing (second step) - only if text processing enabled
        if self._is_section_enabled("text_processing"):
            preprocessing_result = phonemizer_preprocessor.preprocess_text(text, preserve_word_count=True)
            text = preprocessing_result.processed_text
            if preprocessing_result.changes_made:
                result.changes_made.extend(preprocessing_result.changes_made)
                result.stages_completed.append("phonemizer_preprocessing")

        # ENHANCED PROCESSORS FIRST (before standard normalization)

        # Enhanced currency processing (BEFORE standard normalization)
        if options.use_advanced_currency and self._is_section_enabled("symbol_processing"):
            original_text = text
            financial_context = options.financial_context or FinancialContext()
            text = self.currency_processor.process_currency_text(text, financial_context)
            if text != original_text:
                result.currency_enhancements += 1
                result.changes_made.append("Applied advanced currency processing")
                result.stages_completed.append("advanced_currency")

        # Enhanced datetime processing (BEFORE standard normalization)
        if options.use_enhanced_datetime and self._is_section_enabled("text_processing"):
            original_text = text
            text = self.datetime_processor.process_dates_and_times(text)
            if text != original_text:
                result.datetime_enhancements += 1
                result.changes_made.append("Applied enhanced datetime processing")
                result.stages_completed.append("enhanced_datetime")

        # Advanced symbol processing (BEFORE standard normalization)
        if options.use_advanced_symbols and self._is_section_enabled("symbol_processing"):
            original_text = text
            text = self.symbol_processor.process_symbols(text)
            if text != original_text:
                result.changes_made.append("Applied advanced symbol processing")
                result.stages_completed.append("advanced_symbols")

        # eSpeak-enhanced symbol processing (CRITICAL FIX for "?" pronunciation)
        if (hasattr(options, 'use_espeak_enhanced_symbols') and options.use_espeak_enhanced_symbols and
            self._is_feature_enabled("symbol_processing", "espeak_enhanced_processing")):
            # Check if espeak_enhanced_processing subsection is enabled
            espeak_config = self.config.get("symbol_processing", {}).get("espeak_enhanced_processing", {})
            if espeak_config.get("enabled", False):
                original_text = text
                espeak_result = self.espeak_symbol_processor.process_symbols(text)
                text = espeak_result.processed_text
                if text != original_text:
                    result.changes_made.append(f"Applied eSpeak-enhanced symbol processing: {', '.join(espeak_result.changes_made[:3])}")
                    result.stages_completed.append("espeak_enhanced_symbols")
                    logger.debug(f"eSpeak symbol processing: {espeak_result.symbols_processed} symbols processed")



        # Core processing steps (AFTER enhanced processors)
        if options.handle_spell_functions:
            text = self.spell_processor.handle_spell_functions(text)
            result.stages_completed.append("spell_processing")

        if options.process_phonetics:
            # Check if phonetic processing is enabled in beta features
            beta_features = self.config.get("beta_features", {})
            phonetic_config = beta_features.get("phonetic_processing", {})
            if phonetic_config.get("enabled", False):
                text = self.phonetic_processor.process_phonetics(text)
                result.stages_completed.append("phonetic_processing")
                logger.debug("Applied beta phonetic processing")
            else:
                logger.debug("Phonetic processing disabled (beta feature not enabled)")
                result.stages_completed.append("phonetic_processing_skipped")

        if options.resolve_homographs:
            text = self.homograph_resolver.resolve_homographs(text)
            result.stages_completed.append("homograph_resolution")

        # Standard text normalization (AFTER enhanced processors)
        if options.normalize_text:
            text = self.text_normalizer.normalize_text(text)
            result.stages_completed.append("text_normalization")

        # Prosody processing - only if punctuation handling is enabled
        if self._is_section_enabled("punctuation_handling"):
            text = self.prosody_analyzer.process_conversational_features(text)
            text = self.prosody_analyzer.enhance_intonation_markers(text)
            result.stages_completed.append("prosody_analysis")
        else:
            logger.debug("Prosody processing disabled - punctuation_handling section disabled")
            result.stages_completed.append("prosody_analysis_skipped")

        # Clean normalization (additional fixes)
        if options.use_clean_normalizer:
            clean_result = self.clean_normalizer.normalize_text(text)
            if clean_result.changes_made:
                text = clean_result.processed_text
                result.changes_made.extend(clean_result.changes_made)
                result.stages_completed.append("clean_normalization")

        result.stage_timings["enhanced"] = time.perf_counter() - stage_start
        return text

    def _process_premium(self, text: str, options: ProcessingOptions, result: ProcessingResult) -> str:
        """Premium processing pipeline with all enhancements"""
        # Start with enhanced processing
        text = self._process_enhanced(text, options, result)

        stage_start = time.perf_counter()

        # Voice modulation processing
        if options.apply_voice_modulation and self.voice_modulation:
            try:
                original_text = text
                modulation_result, segments = self.voice_modulation.process_voice_modulation(text)
                if modulation_result != original_text:
                    text = modulation_result
                    result.audio_enhancements += 1
                    result.changes_made.append("Applied voice modulation")
                    result.stages_completed.append("voice_modulation")
            except Exception as e:
                logger.warning(f"Voice modulation failed: {e}")
                result.issues_found.append(f"Voice modulation error: {e}")

        # Audio quality enhancement
        if options.enhance_audio_quality:
            try:
                original_text = text
                enhanced_text = audio_quality_enhancer.enhance_audio_quality(text)
                if enhanced_text != original_text:
                    text = enhanced_text
                    result.audio_enhancements += 1
                    result.changes_made.append("Applied audio quality enhancement")
                    result.stages_completed.append("audio_quality_enhancement")
            except Exception as e:
                logger.warning(f"Audio quality enhancement failed: {e}")
                result.issues_found.append(f"Audio quality enhancement error: {e}")

        # Dynamic emotion processing
        if options.use_dynamic_emotion and self.dynamic_emotion:
            try:
                original_text = text
                processed_text, intonation_markers = self.dynamic_emotion.process_emotion_intonation(text)
                if processed_text != original_text:
                    text = processed_text
                    result.audio_enhancements += 1
                    result.changes_made.append(f"Applied dynamic emotion processing with {len(intonation_markers)} markers")
                    result.stages_completed.append("dynamic_emotion_processing")
                    logger.debug(f"Dynamic emotion processing applied {len(intonation_markers)} intonation markers")
                else:
                    result.stages_completed.append("dynamic_emotion_no_changes")
            except Exception as e:
                logger.warning(f"Dynamic emotion processing failed: {e}")
                result.issues_found.append(f"Dynamic emotion error: {e}")

        result.stage_timings["premium"] = time.perf_counter() - stage_start
        return text

    def analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze text to determine optimal processing mode"""
        analysis = {
            'recommended_mode': ProcessingMode.STANDARD,
            'complexity_score': 0,
            'features_detected': [],
            'processing_estimates': {}
        }

        # Currency analysis
        currency_analysis = self.currency_processor.analyze_currency_content(text)
        if currency_analysis['currency_amounts']:
            analysis['features_detected'].append('currency_amounts')
            analysis['complexity_score'] += currency_analysis['complexity_score']

        # Datetime analysis
        datetime_patterns = ['\\d{4}-\\d{2}-\\d{2}', '\\d{1,2}:\\d{2}', 'January|February|March']
        for pattern in datetime_patterns:
            import re
            if re.search(pattern, text, re.IGNORECASE):
                analysis['features_detected'].append('datetime_patterns')
                analysis['complexity_score'] += 2
                break

        # Audio enhancement indicators
        audio_indicators = ['(', ')', '*', '!', '?', 'AM', 'PM']
        for indicator in audio_indicators:
            if indicator in text:
                analysis['features_detected'].append('audio_enhancement_candidates')
                analysis['complexity_score'] += 1
                break

        # Recommend processing mode based on complexity
        if analysis['complexity_score'] >= 10:
            analysis['recommended_mode'] = ProcessingMode.PREMIUM
        elif analysis['complexity_score'] >= 5:
            analysis['recommended_mode'] = ProcessingMode.ENHANCED
        elif analysis['complexity_score'] >= 2:
            analysis['recommended_mode'] = ProcessingMode.STANDARD
        else:
            analysis['recommended_mode'] = ProcessingMode.BASIC

        return analysis

    def get_processing_capabilities(self) -> Dict[str, bool]:
        """Get current processing capabilities"""
        return {
            'basic_normalization': True,
            'standard_processing': True,
            'advanced_currency': True,
            'enhanced_datetime': True,
            'advanced_symbols': True,
            'espeak_enhanced_symbols': True,  # NEW: eSpeak-enhanced symbol processing
            'clean_normalization': True,
            'voice_modulation': self.voice_modulation is not None,
            'audio_quality_enhancement': True,
            'dynamic_emotion': self.dynamic_emotion is not None,
            'parallel_processing': False,  # Not implemented yet
            # Phase 6 capabilities
            'phase6_processing': self.phase6_processor is not None,
            'enhanced_numbers': self.phase6_processor is not None,
            'enhanced_units': self.phase6_processor is not None,
            'enhanced_homographs': self.phase6_processor is not None,
            'enhanced_contractions': self.phase6_processor is not None,
        }

    def create_processing_options(self, mode: Union[str, ProcessingMode], **kwargs) -> ProcessingOptions:
        """Create processing options with sensible defaults"""
        if isinstance(mode, str):
            mode = ProcessingMode(mode)

        options = ProcessingOptions(mode=mode)

        # Apply mode-specific defaults
        if mode == ProcessingMode.BASIC:
            options.use_advanced_currency = False
            options.use_enhanced_datetime = False
            options.use_advanced_symbols = False
            options.enhance_audio_quality = False
            options.apply_voice_modulation = False
            options.use_dynamic_emotion = False
        elif mode == ProcessingMode.STANDARD:
            options.use_advanced_currency = False
            options.use_enhanced_datetime = False
            options.use_advanced_symbols = True  # Enable symbols in standard mode
            options.enhance_audio_quality = False
            options.apply_voice_modulation = False
            options.use_dynamic_emotion = False
        elif mode == ProcessingMode.ENHANCED:
            options.use_advanced_currency = True
            options.use_enhanced_datetime = True
            options.use_advanced_symbols = True
            options.enhance_audio_quality = False
            options.apply_voice_modulation = False
            options.use_dynamic_emotion = False
        elif mode == ProcessingMode.PREMIUM:
            options.use_advanced_currency = True
            options.use_enhanced_datetime = True
            options.use_advanced_symbols = True
            options.enhance_audio_quality = True
            options.apply_voice_modulation = True
            options.use_dynamic_emotion = True

        # Apply any custom overrides
        for key, value in kwargs.items():
            if hasattr(options, key):
                setattr(options, key, value)

        return options
