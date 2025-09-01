#!/usr/bin/env python3
"""
Dynamic emotion and intonation system for TTS
Enhances question/exclamation intonation, italics emphasis, and context analysis
"""

import re
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Import LLM context analyzer
try:
    from .llm_context_analyzer import LLMContextAnalyzer, LLMContextAnalysis, EmotionalContext, ProsodyContext
    LLM_ANALYZER_AVAILABLE = True
except ImportError:
    LLM_ANALYZER_AVAILABLE = False
    logger.warning("LLM context analyzer not available - using basic emotion detection")

logger = logging.getLogger(__name__)

class IntonationType(Enum):
    """Types of intonation patterns"""
    RISING = "rising"           # Questions, uncertainty
    FALLING = "falling"         # Statements, certainty
    RISING_FALLING = "rising_falling"  # Emphasis, surprise
    FLAT = "flat"              # Monotone, listing
    EMPHATIC = "emphatic"      # Strong emphasis
    QUESTIONING = "questioning" # Question intonation
    EXCLAMATORY = "exclamatory" # Exclamation intonation

class EmotionIntensity(Enum):
    """Emotion intensity levels"""
    SUBTLE = 1
    MODERATE = 2
    STRONG = 3
    INTENSE = 4

@dataclass
class IntonationMarker:
    """Intonation marker for text segments"""
    position: int
    length: int
    intonation_type: IntonationType
    intensity: EmotionIntensity
    text_segment: str
    context: str = ""

@dataclass
class EmotionContext:
    """Emotion context for text analysis"""
    primary_emotion: str
    secondary_emotions: List[str]
    intensity: EmotionIntensity
    confidence: float
    triggers: List[str]

class DynamicEmotionIntonationSystem:
    """Advanced emotion and intonation system for natural TTS expression with LLM-based context analysis"""

    def __init__(self):
        self.punctuation_patterns = self._load_punctuation_patterns()
        self.emotion_indicators = self._load_emotion_indicators()
        self.intonation_rules = self._load_intonation_rules()
        self.emphasis_patterns = self._load_emphasis_patterns()
        self.question_patterns = self._load_question_patterns()

        # Configuration
        self.enable_question_intonation = True
        self.enable_exclamation_handling = True
        self.enable_emphasis_detection = True
        self.enable_context_analysis = True
        self.use_llm_enhancement = False  # LLM integration

        # Initialize LLM context analyzer
        self.llm_analyzer = None
        if LLM_ANALYZER_AVAILABLE:
            self.llm_analyzer = LLMContextAnalyzer(enable_llm=False)  # Start with rule-based
            logger.info("LLM context analyzer initialized")
        else:
            logger.warning("LLM context analyzer not available")
        
    def _load_punctuation_patterns(self) -> Dict[str, IntonationType]:
        """Load punctuation-based intonation patterns"""
        return {
            '?': IntonationType.QUESTIONING,
            '!': IntonationType.EXCLAMATORY,
            '.': IntonationType.FALLING,
            ',': IntonationType.FLAT,
            ';': IntonationType.FLAT,
            ':': IntonationType.RISING,
            '...': IntonationType.RISING_FALLING,
            '?!': IntonationType.EXCLAMATORY,
            '!!': IntonationType.EXCLAMATORY,
            '???': IntonationType.QUESTIONING,
        }
    
    def _load_emotion_indicators(self) -> Dict[str, Tuple[str, EmotionIntensity]]:
        """Load emotion indicator words and phrases"""
        return {
            # Excitement indicators
            'amazing': ('excitement', EmotionIntensity.STRONG),
            'incredible': ('excitement', EmotionIntensity.STRONG),
            'fantastic': ('excitement', EmotionIntensity.STRONG),
            'wonderful': ('excitement', EmotionIntensity.MODERATE),
            'great': ('excitement', EmotionIntensity.MODERATE),
            'awesome': ('excitement', EmotionIntensity.STRONG),
            'brilliant': ('excitement', EmotionIntensity.STRONG),
            'excellent': ('excitement', EmotionIntensity.MODERATE),
            'perfect': ('excitement', EmotionIntensity.STRONG),
            'wow': ('excitement', EmotionIntensity.STRONG),
            'yay': ('excitement', EmotionIntensity.STRONG),
            'hooray': ('excitement', EmotionIntensity.STRONG),
            
            # Surprise indicators
            'surprising': ('surprise', EmotionIntensity.MODERATE),
            'unexpected': ('surprise', EmotionIntensity.MODERATE),
            'shocking': ('surprise', EmotionIntensity.STRONG),
            'unbelievable': ('surprise', EmotionIntensity.STRONG),
            'oh': ('surprise', EmotionIntensity.SUBTLE),
            'whoa': ('surprise', EmotionIntensity.MODERATE),
            'really': ('surprise', EmotionIntensity.SUBTLE),
            'seriously': ('surprise', EmotionIntensity.MODERATE),
            
            # Concern/worry indicators
            'worried': ('concern', EmotionIntensity.MODERATE),
            'concerned': ('concern', EmotionIntensity.MODERATE),
            'anxious': ('concern', EmotionIntensity.STRONG),
            'nervous': ('concern', EmotionIntensity.MODERATE),
            'afraid': ('concern', EmotionIntensity.STRONG),
            'scared': ('concern', EmotionIntensity.STRONG),
            'troubling': ('concern', EmotionIntensity.MODERATE),
            'disturbing': ('concern', EmotionIntensity.STRONG),
            
            # Sadness indicators
            'sad': ('sadness', EmotionIntensity.MODERATE),
            'disappointed': ('sadness', EmotionIntensity.MODERATE),
            'heartbroken': ('sadness', EmotionIntensity.STRONG),
            'devastated': ('sadness', EmotionIntensity.INTENSE),
            'tragic': ('sadness', EmotionIntensity.STRONG),
            'unfortunate': ('sadness', EmotionIntensity.MODERATE),
            'terrible': ('sadness', EmotionIntensity.STRONG),
            'awful': ('sadness', EmotionIntensity.STRONG),
            
            # Anger indicators
            'angry': ('anger', EmotionIntensity.STRONG),
            'furious': ('anger', EmotionIntensity.INTENSE),
            'outraged': ('anger', EmotionIntensity.INTENSE),
            'annoyed': ('anger', EmotionIntensity.MODERATE),
            'frustrated': ('anger', EmotionIntensity.MODERATE),
            'irritated': ('anger', EmotionIntensity.MODERATE),
            'ridiculous': ('anger', EmotionIntensity.MODERATE),
            'unacceptable': ('anger', EmotionIntensity.STRONG),
            
            # Calm/peaceful indicators
            'calm': ('calm', EmotionIntensity.MODERATE),
            'peaceful': ('calm', EmotionIntensity.MODERATE),
            'serene': ('calm', EmotionIntensity.STRONG),
            'relaxed': ('calm', EmotionIntensity.MODERATE),
            'tranquil': ('calm', EmotionIntensity.STRONG),
            'gentle': ('calm', EmotionIntensity.MODERATE),
            'soothing': ('calm', EmotionIntensity.MODERATE),
            
            # Uncertainty indicators
            'maybe': ('uncertainty', EmotionIntensity.SUBTLE),
            'perhaps': ('uncertainty', EmotionIntensity.SUBTLE),
            'possibly': ('uncertainty', EmotionIntensity.SUBTLE),
            'uncertain': ('uncertainty', EmotionIntensity.MODERATE),
            'unsure': ('uncertainty', EmotionIntensity.MODERATE),
            'confused': ('uncertainty', EmotionIntensity.MODERATE),
            'puzzled': ('uncertainty', EmotionIntensity.MODERATE),
        }
    
    def _load_intonation_rules(self) -> List[Tuple[str, IntonationType, EmotionIntensity]]:
        """Load intonation rules based on text patterns"""
        return [
            # Question patterns
            (r'\b(what|where|when|who|why|how|which|whose)\b.*\?', IntonationType.QUESTIONING, EmotionIntensity.MODERATE),
            (r'\b(is|are|was|were|do|does|did|can|could|will|would|should|shall)\b.*\?', IntonationType.RISING, EmotionIntensity.MODERATE),
            (r'\b(really|seriously|honestly)\?', IntonationType.QUESTIONING, EmotionIntensity.STRONG),
            
            # Exclamation patterns
            (r'\b(wow|amazing|incredible|fantastic|awesome|brilliant)\b.*!', IntonationType.EXCLAMATORY, EmotionIntensity.STRONG),
            (r'\b(oh no|oh my|good grief|for crying out loud)\b.*!', IntonationType.EXCLAMATORY, EmotionIntensity.STRONG),
            (r'\b(yes|no|absolutely|definitely|certainly)\b.*!', IntonationType.EMPHATIC, EmotionIntensity.STRONG),
            
            # Emphasis patterns
            (r'\*([^*]+)\*', IntonationType.EMPHATIC, EmotionIntensity.MODERATE),  # *italic*
            (r'\*\*([^*]+)\*\*', IntonationType.EMPHATIC, EmotionIntensity.STRONG),  # **bold**
            (r'\b(very|really|extremely|incredibly|absolutely|totally|completely)\b', IntonationType.EMPHATIC, EmotionIntensity.MODERATE),
            
            # Listing patterns
            (r'\b(first|second|third|next|then|finally|lastly)\b', IntonationType.FLAT, EmotionIntensity.SUBTLE),
            (r'\b(and|or|but|however|therefore|moreover)\b', IntonationType.FLAT, EmotionIntensity.SUBTLE),
            
            # Parenthetical patterns (should be softer)
            (r'\(([^)]+)\)', IntonationType.FLAT, EmotionIntensity.SUBTLE),
            
            # Quotation patterns
            (r'"([^"]+)"', IntonationType.RISING_FALLING, EmotionIntensity.MODERATE),
            
            # Uncertainty patterns
            (r'\b(maybe|perhaps|possibly|probably|likely)\b', IntonationType.RISING, EmotionIntensity.SUBTLE),
            (r'\b(I think|I believe|I suppose|I guess)\b', IntonationType.RISING, EmotionIntensity.SUBTLE),
            
            # Contrast patterns
            (r'\b(but|however|although|though|nevertheless|nonetheless)\b', IntonationType.RISING_FALLING, EmotionIntensity.MODERATE),
            
            # Conclusion patterns
            (r'\b(therefore|thus|consequently|in conclusion|finally)\b', IntonationType.FALLING, EmotionIntensity.MODERATE),
        ]
    
    def _load_emphasis_patterns(self) -> List[Tuple[str, EmotionIntensity]]:
        """Load emphasis detection patterns"""
        return [
            # Markdown-style emphasis
            (r'\*([^*]+)\*', EmotionIntensity.MODERATE),  # *italic*
            (r'\*\*([^*]+)\*\*', EmotionIntensity.STRONG),  # **bold**
            (r'_([^_]+)_', EmotionIntensity.MODERATE),  # _italic_
            (r'__([^_]+)__', EmotionIntensity.STRONG),  # __bold__
            
            # ALL CAPS (but not acronyms)
            (r'\b[A-Z]{3,}\b(?![A-Z])', EmotionIntensity.STRONG),
            
            # Repeated punctuation
            (r'[!]{2,}', EmotionIntensity.STRONG),
            (r'[?]{2,}', EmotionIntensity.STRONG),
            (r'\.{3,}', EmotionIntensity.MODERATE),
            
            # Intensifier words
            (r'\b(very|really|extremely|incredibly|absolutely|totally|completely|utterly|quite|rather|fairly|somewhat)\b', EmotionIntensity.MODERATE),
        ]
    
    def _load_question_patterns(self) -> List[Tuple[str, IntonationType]]:
        """Load question detection patterns"""
        return [
            # Wh-questions
            (r'\b(what|where|when|who|why|how|which|whose)\b.*\?', IntonationType.QUESTIONING),
            
            # Yes/no questions
            (r'\b(is|are|was|were|do|does|did|can|could|will|would|should|shall|have|has|had)\b.*\?', IntonationType.RISING),
            
            # Tag questions
            (r'.*,\s*(right|okay|yeah|no|yes|isn\'t it|aren\'t they|don\'t you|won\'t you)\?', IntonationType.RISING),
            
            # Rhetorical questions
            (r'\b(really|seriously|honestly|come on)\?', IntonationType.QUESTIONING),
            
            # Question without question mark (rising intonation)
            (r'\b(I wonder|do you think|could you tell me)\b', IntonationType.RISING),
        ]
    
    def process_emotion_intonation(self, text: str, conversation_history: Optional[List[str]] = None) -> Tuple[str, List[IntonationMarker]]:
        """Process text for emotion and intonation markers with enhanced LLM context analysis"""
        logger.debug(f"Processing emotion and intonation in: {text[:100]}...")

        # Enhanced context analysis using LLM analyzer if available
        llm_analysis = None
        if self.use_llm_enhancement and self.llm_analyzer:
            try:
                llm_analysis = self.llm_analyzer.analyze_context(text, conversation_history)
                logger.debug(f"LLM analysis completed with confidence {llm_analysis.confidence_score:.2f}")
            except Exception as e:
                logger.warning(f"LLM analysis failed, falling back to basic detection: {e}")

        # Detect intonation markers (enhanced with LLM context)
        intonation_markers = self._detect_intonation_markers(text, llm_analysis)

        # Detect emotion context (enhanced with LLM context)
        emotion_context = self._detect_emotion_context(text, llm_analysis)

        # Apply intonation markers to text
        processed_text = self._apply_intonation_markers(text, intonation_markers, emotion_context)

        logger.debug(f"Found {len(intonation_markers)} intonation markers")
        logger.debug(f"Emotion intonation result: {processed_text[:100]}...")

        return processed_text, intonation_markers
    
    def _detect_intonation_markers(self, text: str, llm_analysis: Optional[LLMContextAnalysis] = None) -> List[IntonationMarker]:
        """Detect intonation markers in text with enhanced LLM context"""
        markers = []

        # Use LLM analysis for enhanced detection if available
        if llm_analysis and llm_analysis.prosody_context:
            prosody = llm_analysis.prosody_context

            # Add emphasis markers from LLM analysis
            for start, end, strength in prosody.emphasis_points:
                marker = IntonationMarker(
                    position=start,
                    length=end - start,
                    intonation_type=IntonationType.EMPHATIC,
                    intensity=self._strength_to_intensity(strength),
                    text_segment=text[start:end] if end <= len(text) else text[start:],
                    context=text[max(0, start-20):min(len(text), end+20)]
                )
                markers.append(marker)

        # Apply traditional intonation rules
        for pattern, intonation_type, intensity in self.intonation_rules:
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                marker = IntonationMarker(
                    position=match.start(),
                    length=match.end() - match.start(),
                    intonation_type=intonation_type,
                    intensity=intensity,
                    text_segment=match.group(0),
                    context=text[max(0, match.start()-20):match.end()+20]
                )
                markers.append(marker)
        
        # Detect punctuation-based intonation
        for punct, intonation_type in self.punctuation_patterns.items():
            pattern = re.escape(punct)
            matches = re.finditer(pattern, text)
            
            for match in matches:
                # Check if this punctuation is already covered by a rule
                covered = any(
                    marker.position <= match.start() <= marker.position + marker.length
                    for marker in markers
                )
                
                if not covered:
                    marker = IntonationMarker(
                        position=match.start(),
                        length=len(punct),
                        intonation_type=intonation_type,
                        intensity=EmotionIntensity.MODERATE,
                        text_segment=punct,
                        context=text[max(0, match.start()-10):match.end()+10]
                    )
                    markers.append(marker)
        
        # Sort markers by position
        markers.sort(key=lambda x: x.position)
        
        return markers
    
    def _detect_emotion_context(self, text: str, llm_analysis: Optional[LLMContextAnalysis] = None) -> EmotionContext:
        """Detect overall emotion context of the text"""
        emotions = {}
        triggers = []
        
        # Analyze emotion indicator words
        for word, (emotion, intensity) in self.emotion_indicators.items():
            if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
                if emotion not in emotions:
                    emotions[emotion] = []
                emotions[emotion].append(intensity)
                triggers.append(word)
        
        # Determine primary emotion
        if emotions:
            # Weight emotions by intensity
            emotion_scores = {}
            for emotion, intensities in emotions.items():
                score = sum(intensity.value for intensity in intensities)
                emotion_scores[emotion] = score
            
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            secondary_emotions = [e for e in emotion_scores.keys() if e != primary_emotion]
            
            # Determine overall intensity
            primary_intensities = emotions[primary_emotion]
            avg_intensity = sum(intensity.value for intensity in primary_intensities) / len(primary_intensities)
            
            if avg_intensity >= 3:
                overall_intensity = EmotionIntensity.INTENSE
            elif avg_intensity >= 2:
                overall_intensity = EmotionIntensity.STRONG
            elif avg_intensity >= 1:
                overall_intensity = EmotionIntensity.MODERATE
            else:
                overall_intensity = EmotionIntensity.SUBTLE
            
            confidence = min(1.0, len(triggers) * 0.2)
        else:
            primary_emotion = "neutral"
            secondary_emotions = []
            overall_intensity = EmotionIntensity.SUBTLE
            confidence = 0.0
        
        return EmotionContext(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            intensity=overall_intensity,
            confidence=confidence,
            triggers=triggers
        )
    
    def _apply_intonation_markers(self, text: str, markers: List[IntonationMarker], 
                                emotion_context: EmotionContext) -> str:
        """Apply intonation markers to text"""
        # For now, we'll add simple markers that can be interpreted by the TTS engine
        # In a full implementation, this would generate SSML or other markup
        
        processed_text = text
        offset = 0
        
        for marker in markers:
            # Create intonation marker based on type
            if marker.intonation_type == IntonationType.QUESTIONING:
                intonation_marker = "↗"  # Rising intonation
            elif marker.intonation_type == IntonationType.EXCLAMATORY:
                intonation_marker = "↑"   # High emphasis
            elif marker.intonation_type == IntonationType.EMPHATIC:
                intonation_marker = "↑"   # Emphasis
            elif marker.intonation_type == IntonationType.RISING:
                intonation_marker = "↗"   # Rising
            elif marker.intonation_type == IntonationType.FALLING:
                intonation_marker = "↘"   # Falling
            elif marker.intonation_type == IntonationType.RISING_FALLING:
                intonation_marker = "↗↘"  # Rising then falling
            else:
                intonation_marker = ""
            
            # Insert marker at the end of the segment
            insert_pos = marker.position + marker.length + offset
            processed_text = processed_text[:insert_pos] + intonation_marker + processed_text[insert_pos:]
            offset += len(intonation_marker)
        
        return processed_text
    
    def analyze_intonation_opportunities(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for intonation opportunities"""
        info = {
            'questions': [],
            'exclamations': [],
            'emphasis_candidates': [],
            'emotion_indicators': [],
            'intonation_patterns': []
        }
        
        # Find questions
        questions = re.findall(r'[^.!]*\?', text)
        info['questions'] = questions
        
        # Find exclamations
        exclamations = re.findall(r'[^.?]*!', text)
        info['exclamations'] = exclamations
        
        # Find emphasis patterns
        emphasis = re.findall(r'\*([^*]+)\*|\*\*([^*]+)\*\*', text)
        info['emphasis_candidates'] = [match[0] or match[1] for match in emphasis]
        
        # Find emotion indicators
        for word in self.emotion_indicators:
            if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
                info['emotion_indicators'].append(word)
        
        # Find intonation patterns
        for pattern, intonation_type, intensity in self.intonation_rules:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                info['intonation_patterns'].extend(matches)
        
        return info
    
    def set_configuration(self, enable_question_intonation: bool = None,
                         enable_exclamation_handling: bool = None,
                         enable_emphasis_detection: bool = None,
                         enable_context_analysis: bool = None,
                         use_llm_enhancement: bool = None):
        """Set configuration options"""
        if enable_question_intonation is not None:
            self.enable_question_intonation = enable_question_intonation
        if enable_exclamation_handling is not None:
            self.enable_exclamation_handling = enable_exclamation_handling
        if enable_emphasis_detection is not None:
            self.enable_emphasis_detection = enable_emphasis_detection
        if enable_context_analysis is not None:
            self.enable_context_analysis = enable_context_analysis
        if use_llm_enhancement is not None:
            self.use_llm_enhancement = use_llm_enhancement
            # Update LLM analyzer if available
            if self.llm_analyzer:
                self.llm_analyzer.enable_llm = use_llm_enhancement

        logger.info(f"Dynamic emotion intonation configuration updated: "
                   f"question_intonation={self.enable_question_intonation}, "
                   f"exclamation_handling={self.enable_exclamation_handling}, "
                   f"emphasis_detection={self.enable_emphasis_detection}, "
                   f"context_analysis={self.enable_context_analysis}, "
                   f"llm_enhancement={self.use_llm_enhancement}")

    def _strength_to_intensity(self, strength: float) -> EmotionIntensity:
        """Convert strength value to EmotionIntensity"""
        if strength >= 0.8:
            return EmotionIntensity.INTENSE
        elif strength >= 0.6:
            return EmotionIntensity.STRONG
        elif strength >= 0.4:
            return EmotionIntensity.MODERATE
        else:
            return EmotionIntensity.SUBTLE

    def _duration_to_intensity(self, duration: float) -> EmotionIntensity:
        """Convert pause duration to EmotionIntensity"""
        if duration >= 0.8:
            return EmotionIntensity.STRONG
        elif duration >= 0.5:
            return EmotionIntensity.MODERATE
        else:
            return EmotionIntensity.SUBTLE

    def get_llm_analysis_info(self, text: str) -> Dict[str, Any]:
        """Get LLM analysis information for debugging"""
        if not self.llm_analyzer:
            return {"available": False, "reason": "LLM analyzer not initialized"}

        try:
            analysis = self.llm_analyzer.analyze_context(text)
            return {
                "available": True,
                "confidence": analysis.confidence_score,
                "primary_emotion": analysis.emotional_context.primary_emotion.value,
                "processing_time": analysis.processing_time,
                "method": analysis.analysis_method,
                "prosody_suggestions": analysis.emotional_context.prosodic_suggestions
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
