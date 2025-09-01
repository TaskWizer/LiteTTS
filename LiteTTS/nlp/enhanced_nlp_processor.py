#!/usr/bin/env python3
"""
Enhanced NLP processor that integrates all pronunciation fixes and improvements
Provides a unified interface for all text processing enhancements
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field

from .enhanced_contraction_processor import EnhancedContractionProcessor
from .advanced_symbol_processor import AdvancedSymbolProcessor
from .extended_pronunciation_dictionary import ExtendedPronunciationDictionary
from .voice_modulation_system import VoiceModulationSystem, ModulationSegment
from .enhanced_datetime_processor import EnhancedDateTimeProcessor
from .advanced_abbreviation_handler import AdvancedAbbreviationHandler, AbbreviationMode
from .dynamic_emotion_intonation import DynamicEmotionIntonationSystem, IntonationMarker

# Import existing components for fallback
try:
    from .text_normalizer import TextNormalizer
    from .homograph_resolver import HomographResolver
    from .phonetic_processor import PhoneticProcessor
    from .spell_processor import SpellProcessor
    from .prosody_analyzer import ProsodyAnalyzer
    from .emotion_detector import EmotionDetector
    from ..text.phonemizer_preprocessor import phonemizer_preprocessor
    EXISTING_COMPONENTS_AVAILABLE = True
except ImportError:
    EXISTING_COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class EnhancedProcessingOptions:
    """Configuration options for enhanced text processing"""
    
    # Contraction processing
    contraction_mode: str = 'hybrid'  # natural, phonetic, expanded, hybrid
    preserve_natural_speech: bool = True
    
    # Symbol processing
    fix_html_entities: bool = True
    handle_quotes_naturally: bool = True
    preserve_markdown: bool = False
    
    # Pronunciation dictionary
    use_context_awareness: bool = True
    use_phonetic_spelling: bool = True
    
    # Voice modulation
    enable_parenthetical_whisper: bool = True
    enable_emphasis_detection: bool = True
    default_whisper_voice: str = "af_nicole"
    
    # Date/time processing
    use_ordinal_dates: bool = True
    use_natural_time_format: bool = True
    
    # Abbreviation handling
    abbreviation_mode: str = 'hybrid'  # spell_out, expand, natural, hybrid
    preserve_technical_terms: bool = True
    
    # Emotion/intonation
    enable_question_intonation: bool = True
    enable_exclamation_handling: bool = True
    enable_context_analysis: bool = True
    
    # Integration options
    use_enhanced_processing: bool = True
    fallback_to_existing: bool = True
    enable_performance_monitoring: bool = False

@dataclass
class ProcessingResult:
    """Result of enhanced text processing"""
    processed_text: str
    original_text: str
    processing_time: float
    components_used: List[str]
    modulation_segments: List[ModulationSegment] = field(default_factory=list)
    intonation_markers: List[IntonationMarker] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class EnhancedNLPProcessor:
    """Enhanced NLP processor with comprehensive pronunciation fixes"""
    
    def __init__(self, options: Optional[EnhancedProcessingOptions] = None):
        self.options = options or EnhancedProcessingOptions()
        
        # Initialize enhanced components
        self._init_enhanced_components()
        
        # Initialize existing components if available and needed
        if EXISTING_COMPONENTS_AVAILABLE and self.options.fallback_to_existing:
            self._init_existing_components()
        
        # Performance monitoring
        self.processing_stats = {
            'total_processed': 0,
            'total_time': 0.0,
            'component_times': {},
            'error_count': 0
        }
    
    def _init_enhanced_components(self):
        """Initialize all enhanced processing components"""
        try:
            # Contraction processing
            self.contraction_processor = EnhancedContractionProcessor()
            self.contraction_processor.set_mode(self.options.contraction_mode)
            
            # Symbol processing
            self.symbol_processor = AdvancedSymbolProcessor()
            self.symbol_processor.set_configuration(
                preserve_markdown=self.options.preserve_markdown,
                handle_quotes_naturally=self.options.handle_quotes_naturally,
                fix_html_entities=self.options.fix_html_entities
            )
            
            # Pronunciation dictionary
            self.pronunciation_dict = ExtendedPronunciationDictionary()
            self.pronunciation_dict.set_configuration(
                use_context_awareness=self.options.use_context_awareness,
                use_phonetic_spelling=self.options.use_phonetic_spelling
            )
            
            # Voice modulation
            self.voice_modulation = VoiceModulationSystem()
            self.voice_modulation.set_configuration(
                enable_parenthetical_whisper=self.options.enable_parenthetical_whisper,
                enable_emphasis_detection=self.options.enable_emphasis_detection,
                default_whisper_voice=self.options.default_whisper_voice
            )
            
            # Date/time processing
            self.datetime_processor = EnhancedDateTimeProcessor()
            self.datetime_processor.set_configuration(
                use_ordinal_dates=self.options.use_ordinal_dates,
                use_natural_time_format=self.options.use_natural_time_format
            )
            
            # Abbreviation handling
            self.abbreviation_handler = AdvancedAbbreviationHandler()
            abbrev_mode = AbbreviationMode(self.options.abbreviation_mode)
            self.abbreviation_handler.set_configuration(
                default_mode=abbrev_mode,
                preserve_technical_terms=self.options.preserve_technical_terms
            )
            
            # Emotion/intonation
            self.emotion_system = DynamicEmotionIntonationSystem()
            self.emotion_system.set_configuration(
                enable_question_intonation=self.options.enable_question_intonation,
                enable_exclamation_handling=self.options.enable_exclamation_handling,
                enable_context_analysis=self.options.enable_context_analysis
            )
            
            logger.info("Enhanced NLP components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced components: {e}")
            if not self.options.fallback_to_existing:
                raise
    
    def _init_existing_components(self):
        """Initialize existing components for fallback"""
        try:
            self.text_normalizer = TextNormalizer()
            self.homograph_resolver = HomographResolver()
            self.phonetic_processor = PhoneticProcessor()
            self.spell_processor = SpellProcessor()
            self.prosody_analyzer = ProsodyAnalyzer()
            self.emotion_detector = EmotionDetector()
            
            logger.info("Existing NLP components initialized for fallback")
            
        except Exception as e:
            logger.warning(f"Failed to initialize existing components: {e}")
            self.options.fallback_to_existing = False
    
    def process_text_enhanced(self, text: str, 
                            custom_options: Optional[EnhancedProcessingOptions] = None) -> ProcessingResult:
        """Process text with all enhanced components"""
        import time
        
        start_time = time.perf_counter()
        original_text = text
        components_used = []
        warnings = []
        modulation_segments = []
        intonation_markers = []
        
        # Use custom options if provided
        options = custom_options or self.options
        
        try:
            logger.debug(f"Enhanced processing started for text: {text[:100]}...")
            
            # Step 1: Phonemizer preprocessing (if available)
            if EXISTING_COMPONENTS_AVAILABLE:
                try:
                    preprocessing_result = phonemizer_preprocessor.preprocess_text(text, preserve_word_count=True)
                    text = preprocessing_result.processed_text
                    if preprocessing_result.changes_made:
                        components_used.append("phonemizer_preprocessor")
                        logger.debug(f"Phonemizer preprocessing: {preprocessing_result.changes_made}")
                except Exception as e:
                    warnings.append(f"Phonemizer preprocessing failed: {e}")
            
            # Step 2: HTML entity and symbol processing
            if options.use_enhanced_processing:
                try:
                    text = self.symbol_processor.process_symbols(text)
                    components_used.append("advanced_symbol_processor")
                except Exception as e:
                    warnings.append(f"Symbol processing failed: {e}")
                    logger.warning(f"Symbol processing error: {e}")
            
            # Step 3: Contraction processing
            if options.use_enhanced_processing:
                try:
                    text = self.contraction_processor.process_contractions(text, mode=options.contraction_mode)
                    components_used.append("enhanced_contraction_processor")
                except Exception as e:
                    warnings.append(f"Contraction processing failed: {e}")
                    logger.warning(f"Contraction processing error: {e}")
            
            # Step 4: Pronunciation fixes
            if options.use_enhanced_processing:
                try:
                    text = self.pronunciation_dict.process_text_pronunciations(text)
                    components_used.append("extended_pronunciation_dictionary")
                except Exception as e:
                    warnings.append(f"Pronunciation processing failed: {e}")
                    logger.warning(f"Pronunciation processing error: {e}")
            
            # Step 5: Date/time processing
            if options.use_enhanced_processing:
                try:
                    text = self.datetime_processor.process_dates_and_times(text)
                    components_used.append("enhanced_datetime_processor")
                except Exception as e:
                    warnings.append(f"DateTime processing failed: {e}")
                    logger.warning(f"DateTime processing error: {e}")
            
            # Step 6: Abbreviation handling
            if options.use_enhanced_processing:
                try:
                    abbrev_mode = AbbreviationMode(options.abbreviation_mode)
                    text = self.abbreviation_handler.process_abbreviations(text, mode=abbrev_mode)
                    components_used.append("advanced_abbreviation_handler")
                except Exception as e:
                    warnings.append(f"Abbreviation processing failed: {e}")
                    logger.warning(f"Abbreviation processing error: {e}")
            
            # Step 7: Voice modulation analysis
            if options.use_enhanced_processing:
                try:
                    processed_text, segments = self.voice_modulation.process_voice_modulation(text)
                    text = processed_text
                    modulation_segments = segments
                    components_used.append("voice_modulation_system")
                except Exception as e:
                    warnings.append(f"Voice modulation failed: {e}")
                    logger.warning(f"Voice modulation error: {e}")
            
            # Step 8: Emotion and intonation processing
            if options.use_enhanced_processing:
                try:
                    processed_text, markers = self.emotion_system.process_emotion_intonation(text)
                    text = processed_text
                    intonation_markers = markers
                    components_used.append("dynamic_emotion_intonation")
                except Exception as e:
                    warnings.append(f"Emotion/intonation processing failed: {e}")
                    logger.warning(f"Emotion/intonation processing error: {e}")
            
            # Step 9: Existing component processing (if enabled and available)
            if options.fallback_to_existing and EXISTING_COMPONENTS_AVAILABLE:
                try:
                    # Apply existing spell processing
                    text = self.spell_processor.handle_spell_functions(text)
                    components_used.append("spell_processor")
                    
                    # Apply existing phonetic processing
                    text = self.phonetic_processor.process_phonetics(text)
                    components_used.append("phonetic_processor")
                    
                    # Apply existing homograph resolution
                    text = self.homograph_resolver.resolve_homographs(text)
                    components_used.append("homograph_resolver")
                    
                    # Apply existing prosody analysis
                    text = self.prosody_analyzer.process_conversational_features(text)
                    text = self.prosody_analyzer.enhance_intonation_markers(text)
                    text = self.prosody_analyzer.process_conversational_intonation(text)
                    components_used.append("prosody_analyzer")
                    
                except Exception as e:
                    warnings.append(f"Existing component processing failed: {e}")
                    logger.warning(f"Existing component processing error: {e}")
            
            processing_time = time.perf_counter() - start_time
            
            # Update statistics
            if options.enable_performance_monitoring:
                self._update_stats(processing_time, components_used, len(warnings) > 0)
            
            logger.debug(f"Enhanced processing completed in {processing_time:.4f}s")
            logger.debug(f"Components used: {', '.join(components_used)}")
            logger.debug(f"Result: {text[:100]}...")
            
            return ProcessingResult(
                processed_text=text,
                original_text=original_text,
                processing_time=processing_time,
                components_used=components_used,
                modulation_segments=modulation_segments,
                intonation_markers=intonation_markers,
                warnings=warnings,
                metadata={
                    'text_length': len(original_text),
                    'processed_length': len(text),
                    'modulation_count': len(modulation_segments),
                    'intonation_count': len(intonation_markers)
                }
            )
            
        except Exception as e:
            processing_time = time.perf_counter() - start_time
            logger.error(f"Enhanced processing failed: {e}")
            
            # Fallback to basic processing if available
            if options.fallback_to_existing and EXISTING_COMPONENTS_AVAILABLE:
                try:
                    logger.info("Falling back to existing text normalizer")
                    fallback_text = self.text_normalizer.normalize_text(original_text)
                    components_used = ["text_normalizer_fallback"]
                    warnings.append(f"Enhanced processing failed, used fallback: {e}")
                    
                    return ProcessingResult(
                        processed_text=fallback_text,
                        original_text=original_text,
                        processing_time=processing_time,
                        components_used=components_used,
                        warnings=warnings,
                        metadata={'fallback_used': True}
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback processing also failed: {fallback_error}")
            
            # If all else fails, return original text
            return ProcessingResult(
                processed_text=original_text,
                original_text=original_text,
                processing_time=processing_time,
                components_used=[],
                warnings=[f"All processing failed: {e}"],
                metadata={'processing_failed': True}
            )
    
    def _update_stats(self, processing_time: float, components_used: List[str], had_errors: bool):
        """Update processing statistics"""
        self.processing_stats['total_processed'] += 1
        self.processing_stats['total_time'] += processing_time
        
        if had_errors:
            self.processing_stats['error_count'] += 1
        
        for component in components_used:
            if component not in self.processing_stats['component_times']:
                self.processing_stats['component_times'][component] = []
            self.processing_stats['component_times'][component].append(processing_time)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self.processing_stats.copy()
        
        if stats['total_processed'] > 0:
            stats['average_time'] = stats['total_time'] / stats['total_processed']
            stats['error_rate'] = stats['error_count'] / stats['total_processed']
        else:
            stats['average_time'] = 0.0
            stats['error_rate'] = 0.0
        
        return stats
    
    def analyze_text_issues(self, text: str) -> Dict[str, Any]:
        """Analyze text for potential pronunciation issues"""
        issues = {
            'contractions': self.contraction_processor.get_contraction_info(text),
            'symbols': self.symbol_processor.analyze_symbols(text),
            'pronunciations': self.pronunciation_dict.analyze_pronunciations(text),
            'datetime': self.datetime_processor.analyze_datetime_patterns(text),
            'abbreviations': self.abbreviation_handler.analyze_abbreviations(text),
            'intonation': self.emotion_system.analyze_intonation_opportunities(text),
            'voice_modulation': self.voice_modulation.analyze_modulation_opportunities(text)
        }
        
        return issues
    
    def update_configuration(self, new_options: EnhancedProcessingOptions):
        """Update processing configuration"""
        self.options = new_options
        
        # Update component configurations
        try:
            self.contraction_processor.set_mode(new_options.contraction_mode)
            self.symbol_processor.set_configuration(
                preserve_markdown=new_options.preserve_markdown,
                handle_quotes_naturally=new_options.handle_quotes_naturally,
                fix_html_entities=new_options.fix_html_entities
            )
            self.pronunciation_dict.set_configuration(
                use_context_awareness=new_options.use_context_awareness,
                use_phonetic_spelling=new_options.use_phonetic_spelling
            )
            self.voice_modulation.set_configuration(
                enable_parenthetical_whisper=new_options.enable_parenthetical_whisper,
                enable_emphasis_detection=new_options.enable_emphasis_detection,
                default_whisper_voice=new_options.default_whisper_voice
            )
            self.datetime_processor.set_configuration(
                use_ordinal_dates=new_options.use_ordinal_dates,
                use_natural_time_format=new_options.use_natural_time_format
            )
            abbrev_mode = AbbreviationMode(new_options.abbreviation_mode)
            self.abbreviation_handler.set_configuration(
                default_mode=abbrev_mode,
                preserve_technical_terms=new_options.preserve_technical_terms
            )
            self.emotion_system.set_configuration(
                enable_question_intonation=new_options.enable_question_intonation,
                enable_exclamation_handling=new_options.enable_exclamation_handling,
                enable_context_analysis=new_options.enable_context_analysis
            )
            
            logger.info("Enhanced NLP processor configuration updated")
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            raise
    
    def reset_stats(self):
        """Reset processing statistics"""
        self.processing_stats = {
            'total_processed': 0,
            'total_time': 0.0,
            'component_times': {},
            'error_count': 0
        }
        logger.info("Processing statistics reset")

    # Convenience methods for backward compatibility
    def process_text(self, text: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Process text and return just the processed text (backward compatibility)"""
        if options:
            # Convert dict options to EnhancedProcessingOptions
            enhanced_options = EnhancedProcessingOptions(**options)
            result = self.process_text_enhanced(text, enhanced_options)
        else:
            result = self.process_text_enhanced(text)

        return result.processed_text

    def normalize_text(self, text: str) -> str:
        """Normalize text (backward compatibility)"""
        return self.process_text(text)

    def get_component_versions(self) -> Dict[str, str]:
        """Get version information for all components"""
        return {
            'enhanced_nlp_processor': '1.0.0',
            'enhanced_contraction_processor': '1.0.0',
            'advanced_symbol_processor': '1.0.0',
            'extended_pronunciation_dictionary': '1.0.0',
            'voice_modulation_system': '1.0.0',
            'enhanced_datetime_processor': '1.0.0',
            'advanced_abbreviation_handler': '1.0.0',
            'dynamic_emotion_intonation': '1.0.0'
        }
