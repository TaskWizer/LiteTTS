"""
Enhanced Contraction Processor V2
Research-based contraction handling with context awareness and phonetic guidance
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ContractionPriority(Enum):
    """Priority levels for contraction processing"""
    CRITICAL = 10  # Most commonly mispronounced
    HIGH = 8      # Frequently mispronounced
    MEDIUM = 6    # Occasionally mispronounced
    LOW = 4       # Rarely mispronounced
    MINIMAL = 2   # Seldom causes issues


@dataclass
class ContractionRule:
    """Enhanced contraction rule with context awareness and phonetic guidance"""
    contraction: str
    primary_expansion: str
    alternative_expansion: Optional[str] = None
    context_patterns: Optional[List[Tuple[str, str]]] = None  # (pattern, expansion)
    phonetic_hint: Optional[str] = None
    stress_pattern: Optional[str] = None
    priority: ContractionPriority = ContractionPriority.MEDIUM
    syllable_boundary: Optional[str] = None
    notes: Optional[str] = None


class EnhancedContractionProcessorV2:
    """
    Research-based contraction processor with context awareness and phonetic guidance.
    
    Features:
    - Priority-based processing for high-impact contractions
    - Context-aware expansion for ambiguous contractions
    - Phonetic hints and stress patterns for natural pronunciation
    - Comprehensive logging and debugging support
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the enhanced contraction processor"""
        self.config = config or {}
        self.debug_mode = self.config.get('debug', False)

        # Load pronunciation configuration to respect natural/problematic classification
        self._load_pronunciation_config()

        # Initialize contraction rules
        self._init_contraction_rules()

        # Compile regex patterns for performance
        self._compile_patterns()

        logger.info("Enhanced Contraction Processor V2 initialized with %d rules",
                   len(self.contraction_rules))

    def _load_pronunciation_config(self):
        """Load pronunciation configuration to respect natural/problematic contraction classification"""
        try:
            import json
            import os

            # Try to load enhanced pronunciation config
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'enhanced_pronunciation_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    pronunciation_config = json.load(f)

                contraction_config = pronunciation_config.get('contraction_processing', {})
                # Convert to lowercase for case-insensitive matching
                self.natural_contractions = set(c.lower() for c in contraction_config.get('natural_contractions', []))
                self.problematic_contractions = set(c.lower() for c in contraction_config.get('problematic_contractions', []))
                self.preserve_natural_speech = contraction_config.get('preserve_natural_speech', True)

                logger.info(f"Loaded pronunciation config: {len(self.natural_contractions)} natural, {len(self.problematic_contractions)} problematic contractions")
            else:
                # Fallback to default behavior
                self.natural_contractions = set()
                self.problematic_contractions = set()
                self.preserve_natural_speech = True
                logger.warning("Enhanced pronunciation config not found, using default behavior")

        except Exception as e:
            logger.warning(f"Failed to load pronunciation config: {e}, using default behavior")
            self.natural_contractions = set()
            self.problematic_contractions = set()
            self.preserve_natural_speech = True

    def _init_contraction_rules(self):
        """Initialize comprehensive contraction rules based on research"""
        self.contraction_rules = {
            # CRITICAL PRIORITY - Most commonly mispronounced W/I contractions
            "won't": ContractionRule(
                contraction="won't",
                primary_expansion="will not",
                phonetic_hint="/wɪl nɑt/",
                stress_pattern="WILL not",
                priority=ContractionPriority.CRITICAL,
                syllable_boundary="will|not",
                notes="Often mispronounced as /wont/ instead of /wɪl nɑt/"
            ),
            
            "I'll": ContractionRule(
                contraction="I'll",
                primary_expansion="I will",
                phonetic_hint="/aɪ wɪl/",
                stress_pattern="I WILL",
                priority=ContractionPriority.CRITICAL,
                syllable_boundary="I|will",
                notes="Critical for natural first-person speech"
            ),
            
            "I'm": ContractionRule(
                contraction="I'm",
                primary_expansion="I am",
                phonetic_hint="/aɪ æm/",
                stress_pattern="I AM",
                priority=ContractionPriority.CRITICAL,
                syllable_boundary="I|am",
                notes="Most common first-person contraction"
            ),
            
            "isn't": ContractionRule(
                contraction="isn't",
                primary_expansion="is not",
                phonetic_hint="/ɪz nɑt/",
                stress_pattern="is NOT",
                priority=ContractionPriority.CRITICAL,
                syllable_boundary="is|not",
                notes="Common negative contraction"
            ),
            
            "it's": ContractionRule(
                contraction="it's",
                primary_expansion="it is",
                alternative_expansion="it has",
                context_patterns=[
                    (r"it's\s+(been|done|gone|come|become|gotten|taken|given|seen|heard)", "it has"),
                    (r"it's\s+(a|an|the|very|quite|really|so|too|pretty|rather)", "it is"),
                    (r"it's\s+(good|bad|nice|great|terrible|awful|beautiful|ugly)", "it is"),
                    (r"it's\s+(time|important|necessary|possible|impossible)", "it is"),
                ],
                phonetic_hint="/ɪt ɪz/ or /ɪt hæz/",
                stress_pattern="it IS / it HAS",
                priority=ContractionPriority.CRITICAL,
                syllable_boundary="it|is or it|has",
                notes="Context-sensitive: 'it is' vs 'it has'"
            ),
            
            # HIGH PRIORITY - Frequently mispronounced
            "wouldn't": ContractionRule(
                contraction="wouldn't",
                primary_expansion="would not",
                phonetic_hint="/wʊd nɑt/",
                stress_pattern="would NOT",
                priority=ContractionPriority.HIGH,
                syllable_boundary="would|not"
            ),
            
            "we'll": ContractionRule(
                contraction="we'll",
                primary_expansion="we will",
                phonetic_hint="/wi wɪl/",
                stress_pattern="we WILL",
                priority=ContractionPriority.HIGH,
                syllable_boundary="we|will"
            ),
            
            "we're": ContractionRule(
                contraction="we're",
                primary_expansion="we are",
                phonetic_hint="/wi ɑr/",
                stress_pattern="we ARE",
                priority=ContractionPriority.HIGH,
                syllable_boundary="we|are"
            ),
            
            "I've": ContractionRule(
                contraction="I've",
                primary_expansion="I have",
                phonetic_hint="/aɪ hæv/",
                stress_pattern="I HAVE",
                priority=ContractionPriority.HIGH,
                syllable_boundary="I|have"
            ),
            
            "I'd": ContractionRule(
                contraction="I'd",
                primary_expansion="I would",
                alternative_expansion="I had",
                context_patterns=[
                    (r"I'd\s+(seen|done|been|gone|come|taken|given|heard|said|thought)", "I had"),
                    (r"I'd\s+(like|love|prefer|want|rather|better|sooner)", "I would"),
                    (r"I'd\s+(go|do|say|think|try|help|work|play)", "I would"),
                ],
                phonetic_hint="/aɪ wʊd/ or /aɪ hæd/",
                stress_pattern="I WOULD / I HAD",
                priority=ContractionPriority.HIGH,
                syllable_boundary="I|would or I|had",
                notes="Context-sensitive: 'I would' vs 'I had'"
            ),
            
            # MEDIUM PRIORITY - Occasionally mispronounced
            "wasn't": ContractionRule(
                contraction="wasn't",
                primary_expansion="was not",
                phonetic_hint="/wʌz nɑt/",
                stress_pattern="was NOT",
                priority=ContractionPriority.MEDIUM,
                syllable_boundary="was|not"
            ),
            
            "weren't": ContractionRule(
                contraction="weren't",
                primary_expansion="were not",
                phonetic_hint="/wɜr nɑt/",
                stress_pattern="were NOT",
                priority=ContractionPriority.MEDIUM,
                syllable_boundary="were|not"
            ),
            
            "we've": ContractionRule(
                contraction="we've",
                primary_expansion="we have",
                phonetic_hint="/wi hæv/",
                stress_pattern="we HAVE",
                priority=ContractionPriority.MEDIUM,
                syllable_boundary="we|have"
            ),
            
            "we'd": ContractionRule(
                contraction="we'd",
                primary_expansion="we would",
                alternative_expansion="we had",
                context_patterns=[
                    (r"we'd\s+(seen|done|been|gone|come|taken|given)", "we had"),
                    (r"we'd\s+(like|love|prefer|want|rather|better)", "we would"),
                ],
                phonetic_hint="/wi wʊd/ or /wi hæd/",
                stress_pattern="we WOULD / we HAD",
                priority=ContractionPriority.MEDIUM,
                syllable_boundary="we|would or we|had"
            ),
            
            "it'll": ContractionRule(
                contraction="it'll",
                primary_expansion="it will",
                phonetic_hint="/ɪt wɪl/",
                stress_pattern="it WILL",
                priority=ContractionPriority.MEDIUM,
                syllable_boundary="it|will"
            ),
        }
    
    def _compile_patterns(self):
        """Compile regex patterns for performance optimization"""
        self.compiled_patterns = {}

        for contraction, rule in self.contraction_rules.items():
            # Main contraction pattern with word boundaries (case-insensitive)
            main_pattern = rf'\b{re.escape(contraction)}\b'
            self.compiled_patterns[contraction.lower()] = re.compile(main_pattern, re.IGNORECASE)

            # Context patterns if available
            if rule.context_patterns:
                context_compiled = []
                for pattern, expansion in rule.context_patterns:
                    context_compiled.append((re.compile(pattern, re.IGNORECASE), expansion))
                self.compiled_patterns[f"{contraction.lower()}_context"] = context_compiled
    
    def process_contractions(self, text: str, mode: str = "enhanced") -> str:
        """
        Process contractions with enhanced context awareness and phonetic guidance
        
        Args:
            text: Input text containing contractions
            mode: Processing mode ("enhanced", "basic", "phonetic_only")
            
        Returns:
            Processed text with improved contraction handling
        """
        if not text or not text.strip():
            return text
        
        original_text = text
        processed_text = text
        changes_made = []
        
        # Sort rules by priority (highest first)
        sorted_rules = sorted(
            self.contraction_rules.items(),
            key=lambda x: x[1].priority.value,
            reverse=True
        )
        
        # Process each contraction rule
        for contraction, rule in sorted_rules:
            contraction_lower = contraction.lower()
            if contraction_lower not in processed_text.lower():
                continue

            # CRITICAL FIX: Skip natural contractions when preserve_natural_speech is True
            if self.preserve_natural_speech and contraction_lower in self.natural_contractions:
                if self.debug_mode:
                    logger.debug(f"Preserving natural contraction: {contraction}")
                continue

            # Check for context-sensitive contractions first
            if rule.context_patterns and f"{contraction_lower}_context" in self.compiled_patterns:
                context_patterns = self.compiled_patterns[f"{contraction_lower}_context"]

                for context_pattern, context_expansion in context_patterns:
                    if context_pattern.search(processed_text):
                        # Apply context-specific expansion with case preservation
                        main_pattern = self.compiled_patterns[contraction_lower]
                        if main_pattern.search(processed_text):
                            old_text = processed_text
                            processed_text = main_pattern.sub(
                                lambda m: self._preserve_case(m.group(0), context_expansion),
                                processed_text
                            )
                            if processed_text != old_text:
                                changes_made.append(f"{contraction} → {context_expansion} (context-aware)")
                                if self.debug_mode:
                                    logger.debug(f"Context-aware expansion: {contraction} → {context_expansion}")
                            break
                else:
                    # No context match, use primary expansion with case preservation
                    main_pattern = self.compiled_patterns[contraction_lower]
                    if main_pattern.search(processed_text):
                        old_text = processed_text
                        processed_text = main_pattern.sub(
                            lambda m: self._preserve_case(m.group(0), rule.primary_expansion),
                            processed_text
                        )
                        if processed_text != old_text:
                            changes_made.append(f"{contraction} → {rule.primary_expansion} (primary)")
                            if self.debug_mode:
                                logger.debug(f"Primary expansion: {contraction} → {rule.primary_expansion}")
            else:
                # Simple contraction without context sensitivity with case preservation
                main_pattern = self.compiled_patterns[contraction_lower]
                if main_pattern.search(processed_text):
                    old_text = processed_text
                    processed_text = main_pattern.sub(
                        lambda m: self._preserve_case(m.group(0), rule.primary_expansion),
                        processed_text
                    )
                    if processed_text != old_text:
                        changes_made.append(f"{contraction} → {rule.primary_expansion}")
                        if self.debug_mode:
                            logger.debug(f"Standard expansion: {contraction} → {rule.primary_expansion}")
        
        # Log summary if changes were made
        if changes_made and self.debug_mode:
            logger.info(f"Enhanced contraction processing: {len(changes_made)} changes made")
            for change in changes_made:
                logger.debug(f"  - {change}")
        
        return processed_text

    def _preserve_case(self, original: str, replacement: str) -> str:
        """Preserve the case pattern of the original text in the replacement"""
        if not original or not replacement:
            return replacement

        # If original is all uppercase, make replacement all uppercase
        if original.isupper():
            return replacement.upper()

        # If original starts with uppercase, capitalize replacement
        elif original[0].isupper():
            return replacement[0].upper() + replacement[1:].lower()

        # Otherwise, keep replacement as lowercase
        else:
            return replacement.lower()

    def analyze_contractions(self, text: str) -> Dict[str, any]:
        """
        Analyze text for contraction processing opportunities and issues

        Args:
            text: Input text to analyze

        Returns:
            Analysis report with findings and recommendations
        """
        analysis = {
            'contractions_found': [],
            'high_priority_contractions': [],
            'context_sensitive_contractions': [],
            'phonetic_guidance_available': [],
            'processing_recommendations': []
        }

        # Find all contractions in text
        for contraction, rule in self.contraction_rules.items():
            contraction_lower = contraction.lower()
            pattern = self.compiled_patterns[contraction_lower]
            matches = pattern.findall(text)

            if matches:
                analysis['contractions_found'].append({
                    'contraction': contraction,
                    'count': len(matches),
                    'priority': rule.priority.name,
                    'has_context_patterns': bool(rule.context_patterns),
                    'has_phonetic_hint': bool(rule.phonetic_hint)
                })

                # Categorize by priority
                if rule.priority in [ContractionPriority.CRITICAL, ContractionPriority.HIGH]:
                    analysis['high_priority_contractions'].append(contraction)

                # Check for context sensitivity
                if rule.context_patterns:
                    analysis['context_sensitive_contractions'].append(contraction)

                # Check for phonetic guidance
                if rule.phonetic_hint:
                    analysis['phonetic_guidance_available'].append({
                        'contraction': contraction,
                        'phonetic_hint': rule.phonetic_hint,
                        'stress_pattern': rule.stress_pattern
                    })

        # Generate recommendations
        if analysis['high_priority_contractions']:
            analysis['processing_recommendations'].append(
                f"Found {len(analysis['high_priority_contractions'])} high-priority contractions that should be processed"
            )

        if analysis['context_sensitive_contractions']:
            analysis['processing_recommendations'].append(
                f"Found {len(analysis['context_sensitive_contractions'])} context-sensitive contractions requiring careful handling"
            )

        return analysis

    def get_phonetic_guidance(self, contraction: str) -> Optional[Dict[str, str]]:
        """
        Get phonetic guidance for a specific contraction

        Args:
            contraction: The contraction to get guidance for

        Returns:
            Dictionary with phonetic information or None if not available
        """
        if contraction.lower() in self.contraction_rules:
            rule = self.contraction_rules[contraction.lower()]
            return {
                'contraction': contraction,
                'primary_expansion': rule.primary_expansion,
                'alternative_expansion': rule.alternative_expansion,
                'phonetic_hint': rule.phonetic_hint,
                'stress_pattern': rule.stress_pattern,
                'syllable_boundary': rule.syllable_boundary,
                'priority': rule.priority.name,
                'notes': rule.notes
            }
        return None

    def validate_processing(self, original_text: str, processed_text: str) -> Dict[str, any]:
        """
        Validate contraction processing results

        Args:
            original_text: Original text before processing
            processed_text: Text after contraction processing

        Returns:
            Validation report with quality metrics
        """
        validation = {
            'original_contractions': 0,
            'processed_contractions': 0,
            'processing_rate': 0.0,
            'quality_score': 0.0,
            'issues_found': [],
            'recommendations': []
        }

        # Count contractions in original text
        original_analysis = self.analyze_contractions(original_text)
        validation['original_contractions'] = len(original_analysis['contractions_found'])

        # Count remaining contractions in processed text
        processed_analysis = self.analyze_contractions(processed_text)
        validation['processed_contractions'] = len(processed_analysis['contractions_found'])

        # Calculate processing rate
        if validation['original_contractions'] > 0:
            validation['processing_rate'] = (
                (validation['original_contractions'] - validation['processed_contractions'])
                / validation['original_contractions']
            ) * 100

        # Calculate quality score based on high-priority contractions processed
        high_priority_original = len(original_analysis['high_priority_contractions'])
        high_priority_remaining = len(processed_analysis['high_priority_contractions'])

        if high_priority_original > 0:
            high_priority_processed = high_priority_original - high_priority_remaining
            validation['quality_score'] = (high_priority_processed / high_priority_original) * 100
        else:
            validation['quality_score'] = 100.0  # No high-priority contractions to process

        # Identify issues
        if validation['processing_rate'] < 80:
            validation['issues_found'].append("Low processing rate - many contractions remain unexpanded")

        if validation['quality_score'] < 95:
            validation['issues_found'].append("High-priority contractions not fully processed")

        # Generate recommendations
        if high_priority_remaining > 0:
            validation['recommendations'].append(
                f"Consider reviewing {high_priority_remaining} remaining high-priority contractions"
            )

        if validation['processing_rate'] > 0:
            validation['recommendations'].append(
                f"Successfully processed {validation['processing_rate']:.1f}% of contractions"
            )

        return validation

    def get_statistics(self) -> Dict[str, any]:
        """Get processor statistics and configuration info"""
        priority_counts = {}
        for priority in ContractionPriority:
            priority_counts[priority.name] = sum(
                1 for rule in self.contraction_rules.values()
                if rule.priority == priority
            )

        context_sensitive_count = sum(
            1 for rule in self.contraction_rules.values()
            if rule.context_patterns
        )

        phonetic_guidance_count = sum(
            1 for rule in self.contraction_rules.values()
            if rule.phonetic_hint
        )

        return {
            'total_rules': len(self.contraction_rules),
            'priority_distribution': priority_counts,
            'context_sensitive_rules': context_sensitive_count,
            'rules_with_phonetic_guidance': phonetic_guidance_count,
            'debug_mode': self.debug_mode,
            'version': "2.0"
        }
