#!/usr/bin/env python3
"""
Main NLP processor that combines all text processing components
"""

from typing import Dict, Any
import logging

from .text_normalizer import TextNormalizer
from .homograph_resolver import HomographResolver
from .phonetic_processor import PhoneticProcessor
from .spell_processor import SpellProcessor
from .prosody_analyzer import ProsodyAnalyzer
from .emotion_detector import EmotionDetector, EmotionProfile
from .context_adapter import ContextAdapter, SpeechContext
from .naturalness_enhancer import NaturalnessEnhancer, NaturalnessProfile
from ..text.phonemizer_preprocessor import phonemizer_preprocessor
from .unified_pronunciation_fix import unified_pronunciation_fix
from .audio_quality_enhancer import audio_quality_enhancer, AudioQualityProfile
from .interjection_processor import InterjectionProcessor
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Local model definitions for NLP processing
@dataclass
class ProsodyInfo:
    """Prosody analysis information"""
    pauses: List[Dict[str, Any]] = field(default_factory=list)
    emphasis: List[Dict[str, Any]] = field(default_factory=list)
    intonation: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class NormalizationOptions:
    """Text normalization configuration"""
    normalize: bool = True
    unit_normalization: bool = False
    url_normalization: bool = True
    email_normalization: bool = True

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Main NLP processor that orchestrates all text processing"""
    
    def __init__(self, enable_advanced_features: bool = True, config: Optional[Dict] = None):
        """Initialize NLP processor with all components

        Args:
            enable_advanced_features: Enable emotion detection, context adaptation, and naturalness enhancement
            config: Configuration dictionary for all processors
        """
        self.config = config or {}
        self.text_normalizer = TextNormalizer()
        self.homograph_resolver = HomographResolver()
        self.phonetic_processor = PhoneticProcessor(self.config)
        self.spell_processor = SpellProcessor()
        self.prosody_analyzer = ProsodyAnalyzer()

        # Advanced human-likeness features
        self.enable_advanced_features = enable_advanced_features
        if enable_advanced_features:
            self.emotion_detector = EmotionDetector()
            self.context_adapter = ContextAdapter()
            self.naturalness_enhancer = NaturalnessEnhancer()
        else:
            self.emotion_detector = None
            self.context_adapter = None
            self.naturalness_enhancer = None
        
    def process_text(self, text: str, options: NormalizationOptions = None) -> str:
        """Process text through the complete NLP pipeline"""
        if options is None:
            options = NormalizationOptions()

        logger.info(f"Processing text: {text[:100]}...")

        # Step 0: Phonemizer preprocessing (CRITICAL FIX for HTML entities and pronunciation issues)
        # This handles HTML entity decoding, quote character removal, and other preprocessing
        preprocessing_result = phonemizer_preprocessor.preprocess_text(text, preserve_word_count=True)
        text = preprocessing_result.processed_text
        if preprocessing_result.changes_made:
            logger.debug(f"Phonemizer preprocessing changes: {preprocessing_result.changes_made}")

        # Step 0.5: Apply unified pronunciation fixes (NEW - HIGH PRIORITY)
        # This fixes comma handling, diphthongs, contractions, and interjections
        try:
            pronunciation_result = unified_pronunciation_fix.process_pronunciation_fixes(text)
            text = pronunciation_result.processed_text
            if pronunciation_result.fixes_applied:
                logger.debug(f"Pronunciation fixes applied: {pronunciation_result.fixes_applied}")
        except Exception as e:
            logger.error(f"Pronunciation fix processing failed: {e}")

        # Step 1: Handle spell functions
        text = self.spell_processor.handle_spell_functions(text)

        # Step 2: Process phonetic markers (if enabled in beta features)
        beta_features = self.config.get("beta_features", {})
        phonetic_config = beta_features.get("phonetic_processing", {})
        if phonetic_config.get("enabled", False):
            text = self.phonetic_processor.process_phonetics(text)
            logger.debug("Applied beta phonetic processing")
        else:
            logger.debug("Phonetic processing disabled (beta feature not enabled)")

        # Step 3: Resolve homographs
        text = self.homograph_resolver.resolve_homographs(text)

        # Step 4: Text normalization (if enabled)
        if options.normalize:
            text = self.text_normalizer.normalize_text(text)

        # Step 5: Process conversational features
        text = self.prosody_analyzer.process_conversational_features(text)

        # Step 6: Enhanced intonation processing for questions and exclamations
        text = self.prosody_analyzer.enhance_intonation_markers(text)
        text = self.prosody_analyzer.process_conversational_intonation(text)

        # Step 7: Audio quality enhancement (NEW - HIGH PRIORITY)
        # Apply advanced prosodic modeling and emotional speech synthesis
        try:
            text = audio_quality_enhancer.enhance_audio_quality(text)
            logger.debug("Applied audio quality enhancements")
        except Exception as e:
            logger.error(f"Audio quality enhancement failed: {e}")

        logger.info(f"Text processing complete: {text[:100]}...")
        return text
    
    def normalize_text(self, text: str) -> str:
        """Normalize input text"""
        return self.text_normalizer.normalize_text(text)
    
    def resolve_homographs(self, text: str) -> str:
        """Resolve homograph pronunciations"""
        return self.homograph_resolver.resolve_homographs(text)
    
    def process_phonetics(self, text: str) -> str:
        """Process phonetic markers"""
        return self.phonetic_processor.process_phonetics(text)
    
    def analyze_prosody(self, text: str) -> ProsodyInfo:
        """Analyze text for prosody information"""
        prosody_data = self.prosody_analyzer.get_prosody_info(text)
        return ProsodyInfo(
            pauses=prosody_data['pauses'],
            emphasis=prosody_data['emphasis'],
            intonation=prosody_data['intonation']
        )
    
    def spell_word(self, word: str) -> str:
        """Spell out a word letter by letter"""
        return self.spell_processor.spell_word_direct(word)
    
    def add_homograph(self, word: str, pronunciations: Dict[str, str]):
        """Add a custom homograph"""
        self.homograph_resolver.add_homograph(word, pronunciations)

    def process_text_enhanced(self, text: str, context_metadata: Optional[Dict[str, Any]] = None,
                            options: NormalizationOptions = None) -> Dict[str, Any]:
        """Enhanced text processing with human-likeness features

        Args:
            text: Input text to process
            context_metadata: Optional context information (audience, register, etc.)
            options: Text normalization options

        Returns:
            Dictionary containing processed text and enhancement data
        """
        if not self.enable_advanced_features:
            # Fall back to basic processing
            processed_text = self.process_text(text, options)
            return {"text": processed_text, "enhancements": None}

        logger.info(f"Enhanced processing for text: {text[:100]}...")

        # Step 1: Analyze context
        speech_context = self.context_adapter.analyze_context(text, context_metadata)

        # Step 2: Detect emotions
        emotion_profile = self.emotion_detector.detect_emotional_context(text)
        speech_context.emotional_state = emotion_profile

        # Step 3: Basic text processing
        processed_text = self.process_text(text, options)

        # Step 4: Context-aware parameter adaptation
        adaptation_params = self.context_adapter.adapt_synthesis_parameters(speech_context)

        # Step 5: Naturalness enhancement
        naturalness_context = {
            "register": speech_context.register.value,
            "content_type": speech_context.content_type.value,
            "emotional_intensity": emotion_profile.intensity,
            "emotion": emotion_profile.primary_emotion.value
        }
        naturalness_profile = self.naturalness_enhancer.enhance_naturalness(
            processed_text, naturalness_context
        )

        # Step 6: Apply naturalness to text
        enhanced_text = self.naturalness_enhancer.apply_naturalness_to_text(
            processed_text, naturalness_profile
        )

        return {
            "text": enhanced_text,
            "original_text": text,
            "processed_text": processed_text,
            "speech_context": speech_context,
            "emotion_profile": emotion_profile,
            "adaptation_parameters": adaptation_params,
            "naturalness_profile": naturalness_profile
        }

    def detect_emotion(self, text: str, conversation_history: Optional[List] = None) -> Optional[EmotionProfile]:
        """Detect emotional context in text

        Args:
            text: Text to analyze
            conversation_history: Optional conversation history for context

        Returns:
            Emotion profile or None if advanced features disabled
        """
        if not self.enable_advanced_features or not self.emotion_detector:
            return None

        return self.emotion_detector.detect_emotional_context(text, conversation_history)

    def adapt_for_context(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[SpeechContext]:
        """Analyze and adapt for speech context

        Args:
            text: Text to analyze
            metadata: Optional context metadata

        Returns:
            Speech context or None if advanced features disabled
        """
        if not self.enable_advanced_features or not self.context_adapter:
            return None

        return self.context_adapter.analyze_context(text, metadata)

    def enhance_naturalness(self, text: str, context: Optional[Dict[str, Any]] = None) -> Optional[NaturalnessProfile]:
        """Apply naturalness enhancements to text

        Args:
            text: Text to enhance
            context: Optional context information

        Returns:
            Naturalness profile or None if advanced features disabled
        """
        if not self.enable_advanced_features or not self.naturalness_enhancer:
            return None

        return self.naturalness_enhancer.enhance_naturalness(text, context)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = {
            'homographs_loaded': len(self.homograph_resolver.list_homographs()),
            'abbreviations_loaded': len(self.text_normalizer.abbreviation_dict),
            'phonetic_mappings': len(self.phonetic_processor.ipa_mappings),
            'conversational_patterns': len(self.prosody_analyzer.conversational_patterns)
        }

        # Add phonetic processing statistics
        try:
            phonetic_stats = self.phonetic_processor.get_statistics()
            stats['phonetic_processing'] = phonetic_stats
        except Exception as e:
            logger.warning(f"Could not get phonetic processing stats: {e}")
            stats['phonetic_processing'] = {'error': str(e)}

        return stats