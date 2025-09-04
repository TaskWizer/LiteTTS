#!/usr/bin/env python3
"""
Phase 6 Enhanced Contraction Processing for Advanced Text Processing
Handles problematic contractions with context-aware disambiguation and natural pronunciation
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ContractionType(Enum):
    """Types of contractions for disambiguation"""
    WOULD = "would"
    HAD = "had"
    IS = "is"
    HAS = "has"
    WILL = "will"
    HAVE = "have"
    AM = "am"
    ARE = "are"
    NOT = "not"

@dataclass
class ContractionMatch:
    """Information about a contraction match"""
    original: str
    expanded: str
    contraction_type: ContractionType
    position: int
    context: str
    confidence: float

@dataclass
class ContractionProcessingResult:
    """Result of contraction processing"""
    processed_text: str
    original_text: str
    contractions_processed: List[ContractionMatch]
    changes_made: List[str]

class Phase6ContractionProcessor:
    """Phase 6 enhanced processor for natural contraction handling"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize Phase 6 contraction processor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.ambiguous_contractions = self._load_ambiguous_contractions()
        self.context_patterns = self._compile_context_patterns()
        self.natural_pronunciations = self._load_natural_pronunciations()
        
        # Load configuration
        self._load_config()
        
        logger.info("Phase 6 Contraction Processor initialized")
    
    def _load_config(self):
        """Load configuration settings"""
        try:
            import json
            from pathlib import Path
            config_path = Path("config.json")
            if config_path.exists():
                with open(config_path) as f:
                    main_config = json.load(f)
                    text_processing = main_config.get('text_processing', {})
                    
                    self.natural_speech = text_processing.get('natural_speech', True)
                    self.expand_contractions = text_processing.get('expand_contractions', False)
                    
            else:
                self.natural_speech = True
                self.expand_contractions = False
                
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}")
            self.natural_speech = True
            self.expand_contractions = False
    
    def _load_ambiguous_contractions(self) -> Dict[str, List[Tuple[str, ContractionType]]]:
        """Load ambiguous contractions that need context-based disambiguation"""
        return {
            "he'd": [
                ("he had", ContractionType.HAD),
                ("he would", ContractionType.WOULD)
            ],
            "she'd": [
                ("she had", ContractionType.HAD),
                ("she would", ContractionType.WOULD)
            ],
            "we'd": [
                ("we had", ContractionType.HAD),
                ("we would", ContractionType.WOULD)
            ],
            "i'd": [
                ("I had", ContractionType.HAD),
                ("I would", ContractionType.WOULD)
            ],
            "they'd": [
                ("they had", ContractionType.HAD),
                ("they would", ContractionType.WOULD)
            ],
            "you'd": [
                ("you had", ContractionType.HAD),
                ("you would", ContractionType.WOULD)
            ],
            "it'd": [
                ("it had", ContractionType.HAD),
                ("it would", ContractionType.WOULD)
            ],
            "that'd": [
                ("that had", ContractionType.HAD),
                ("that would", ContractionType.WOULD)
            ],
            "there'd": [
                ("there had", ContractionType.HAD),
                ("there would", ContractionType.WOULD)
            ],
            "who'd": [
                ("who had", ContractionType.HAD),
                ("who would", ContractionType.WOULD)
            ],
            "what'd": [
                ("what had", ContractionType.HAD),
                ("what would", ContractionType.WOULD)
            ]
        }
    
    def _compile_context_patterns(self) -> Dict[ContractionType, List[Tuple[re.Pattern, float]]]:
        """Compile context patterns for disambiguation"""
        patterns = {}
        
        # Patterns that indicate "had" (past perfect)
        patterns[ContractionType.HAD] = [
            # Past participle indicators
            (re.compile(r"'d\s+(been|done|gone|seen|taken|given|written|spoken|eaten|drunk|run|come|become)", re.IGNORECASE), 0.95),
            (re.compile(r"'d\s+(already|just|never|ever|recently|previously|earlier)", re.IGNORECASE), 0.90),
            (re.compile(r"'d\s+\w+ed\b", re.IGNORECASE), 0.85),  # Past participle ending in -ed
            (re.compile(r"'d\s+(not|n't)\s+(been|done|gone|seen)", re.IGNORECASE), 0.90),
            # Time indicators suggesting past perfect
            (re.compile(r"\b(before|after|when|since|until|by the time)\b.*'d", re.IGNORECASE), 0.80),
            (re.compile(r"'d.*\b(before|after|when|since|until|by then)\b", re.IGNORECASE), 0.80),
        ]
        
        # Patterns that indicate "would" (conditional)
        patterns[ContractionType.WOULD] = [
            # Conditional indicators
            (re.compile(r"'d\s+(like|love|prefer|rather|want|need|hope)", re.IGNORECASE), 0.95),
            (re.compile(r"'d\s+(be|go|do|say|think|feel|try|help)", re.IGNORECASE), 0.85),
            (re.compile(r"\b(if|when|unless|suppose|imagine)\b.*'d", re.IGNORECASE), 0.90),
            (re.compile(r"'d.*\b(if|when|unless|probably|maybe|perhaps)\b", re.IGNORECASE), 0.85),
            # Future in the past
            (re.compile(r"\b(said|thought|believed|knew|hoped)\b.*'d", re.IGNORECASE), 0.80),
            # Polite requests
            (re.compile(r"'d\s+(you|please)", re.IGNORECASE), 0.90),
        ]
        
        return patterns
    
    def _load_natural_pronunciations(self) -> Dict[str, str]:
        """Load natural pronunciation fixes for problematic contractions"""
        return {
            # Fix "wasn't" pronunciation (not "waaasant")
            "wasn't": "wuznt",
            "weren't": "wernt",
            "wouldn't": "woodnt",
            "couldn't": "coodnt",
            "shouldn't": "shoodnt",
            "didn't": "didnt",
            "don't": "dont",
            "won't": "wont",
            "can't": "cant",
            "isn't": "iznt",
            "aren't": "arnt",
            "haven't": "havnt",
            "hasn't": "haznt",
            "hadn't": "hadnt",
            
            # Improve flow for common contractions
            "i'm": "im",
            "i'll": "ile",
            "i've": "ive",
            "i'd": "id",
            "you're": "yoor",
            "you'll": "yool",
            "you've": "yoov",
            "we're": "weer",
            "we'll": "weel",
            "we've": "weev",
            "they're": "thair",
            "they'll": "thail",
            "they've": "thaiv",
            "he's": "heez",
            "he'll": "heel",
            "she's": "sheez",
            "she'll": "sheel",
            "it's": "its",
            "it'll": "itl",
            "that's": "thats",
            "that'll": "thatl",
            "there's": "thairs",
            "there'll": "thairl",
            "here's": "hairs",
            "where's": "wairs",
            "what's": "whats",
            "who's": "hooz",
            "how's": "howz",
            "when's": "whenz",
            "why's": "whyz"
        }
    
    def process_contractions(self, text: str) -> ContractionProcessingResult:
        """Main contraction processing method
        
        Args:
            text: Input text to process
            
        Returns:
            ContractionProcessingResult with processed contractions
        """
        logger.debug(f"Processing contractions in text: {text[:100]}...")
        
        original_text = text
        contractions_processed = []
        changes_made = []
        
        # If natural speech is enabled, use natural pronunciation approach
        if self.natural_speech and not self.expand_contractions:
            text, natural_changes = self._apply_natural_pronunciations(text)
            if natural_changes:
                contractions_processed.extend(natural_changes)
                changes_made.extend([f"Natural pronunciation: {match.original} → {match.expanded}" for match in natural_changes])
        
        # Process ambiguous contractions (always do this for accuracy)
        text, ambiguous_changes = self._process_ambiguous_contractions(text)
        if ambiguous_changes:
            contractions_processed.extend(ambiguous_changes)
            changes_made.extend([f"Disambiguated: {match.original} → {match.expanded}" for match in ambiguous_changes])
        
        # If full expansion is enabled, expand remaining contractions
        if self.expand_contractions:
            text, expansion_changes = self._expand_remaining_contractions(text)
            if expansion_changes:
                contractions_processed.extend(expansion_changes)
                changes_made.extend([f"Expanded: {match.original} → {match.expanded}" for match in expansion_changes])
        
        result = ContractionProcessingResult(
            processed_text=text,
            original_text=original_text,
            contractions_processed=contractions_processed,
            changes_made=changes_made
        )
        
        logger.debug(f"Contraction processing complete: {len(contractions_processed)} contractions processed")
        return result

    def _apply_natural_pronunciations(self, text: str) -> Tuple[str, List[ContractionMatch]]:
        """Apply natural pronunciation fixes for problematic contractions"""
        matches = []

        for contraction, pronunciation in self.natural_pronunciations.items():
            pattern = re.compile(r'\b' + re.escape(contraction) + r'\b', re.IGNORECASE)

            def replace_contraction(match):
                position = match.start()
                context = self._extract_context(text, position, match.end())

                contraction_match = ContractionMatch(
                    original=match.group(),
                    expanded=pronunciation,
                    contraction_type=ContractionType.NOT,  # Default type
                    position=position,
                    context=context,
                    confidence=0.9
                )
                matches.append(contraction_match)
                return pronunciation

            text = pattern.sub(replace_contraction, text)

        return text, matches

    def _process_ambiguous_contractions(self, text: str) -> Tuple[str, List[ContractionMatch]]:
        """Process ambiguous contractions using context analysis"""
        matches = []

        for contraction, expansions in self.ambiguous_contractions.items():
            pattern = re.compile(r'\b' + re.escape(contraction) + r'\b', re.IGNORECASE)

            def replace_ambiguous(match):
                position = match.start()
                context = self._extract_context(text, position, match.end())

                # Determine the correct expansion based on context
                expansion, contraction_type, confidence = self._disambiguate_contraction(context, expansions)

                contraction_match = ContractionMatch(
                    original=match.group(),
                    expanded=expansion,
                    contraction_type=contraction_type,
                    position=position,
                    context=context,
                    confidence=confidence
                )
                matches.append(contraction_match)

                return expansion

            text = pattern.sub(replace_ambiguous, text)

        return text, matches

    def _disambiguate_contraction(self, context: str, expansions: List[Tuple[str, ContractionType]]) -> Tuple[str, ContractionType, float]:
        """Disambiguate between possible contraction expansions"""
        best_expansion = expansions[0][0]  # Default to first option
        best_type = expansions[0][1]
        best_confidence = 0.5

        # Check context patterns for each possible type
        for expansion, contraction_type in expansions:
            if contraction_type in self.context_patterns:
                for pattern, confidence in self.context_patterns[contraction_type]:
                    if pattern.search(context):
                        if confidence > best_confidence:
                            best_expansion = expansion
                            best_type = contraction_type
                            best_confidence = confidence
                            break

        return best_expansion, best_type, best_confidence

    def _expand_remaining_contractions(self, text: str) -> Tuple[str, List[ContractionMatch]]:
        """Expand remaining contractions if full expansion is enabled"""
        matches = []

        # Standard contractions to expand
        standard_contractions = {
            "don't": "do not",
            "doesn't": "does not",
            "didn't": "did not",
            "won't": "will not",
            "wouldn't": "would not",
            "shouldn't": "should not",
            "couldn't": "could not",
            "can't": "cannot",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not",
            "haven't": "have not",
            "hasn't": "has not",
            "hadn't": "had not",
            "i'll": "I will",
            "you'll": "you will",
            "he'll": "he will",
            "she'll": "she will",
            "we'll": "we will",
            "they'll": "they will",
            "i've": "I have",
            "you've": "you have",
            "we've": "we have",
            "they've": "they have",
            "i'm": "I am",
            "you're": "you are",
            "we're": "we are",
            "they're": "they are",
            "he's": "he is",
            "she's": "she is",
            "it's": "it is",
            "that's": "that is",
            "there's": "there is",
            "here's": "here is",
            "where's": "where is",
            "what's": "what is",
            "who's": "who is",
            "how's": "how is",
            "when's": "when is",
            "why's": "why is",
            "let's": "let us",
            "that'll": "that will",
            "there'll": "there will"
        }

        for contraction, expansion in standard_contractions.items():
            pattern = re.compile(r'\b' + re.escape(contraction) + r'\b', re.IGNORECASE)

            def replace_standard(match):
                position = match.start()
                context = self._extract_context(text, position, match.end())

                contraction_match = ContractionMatch(
                    original=match.group(),
                    expanded=expansion,
                    contraction_type=ContractionType.NOT,  # Default type
                    position=position,
                    context=context,
                    confidence=0.8
                )
                matches.append(contraction_match)
                return expansion

            text = pattern.sub(replace_standard, text)

        return text, matches

    def _extract_context(self, text: str, start_pos: int, end_pos: int, context_size: int = 50) -> str:
        """Extract context around a contraction position"""
        context_start = max(0, start_pos - context_size)
        context_end = min(len(text), end_pos + context_size)
        return text[context_start:context_end]

    def get_contraction_statistics(self) -> Dict[str, int]:
        """Get statistics about available contractions"""
        return {
            'ambiguous_contractions': len(self.ambiguous_contractions),
            'natural_pronunciations': len(self.natural_pronunciations),
            'context_patterns': sum(len(patterns) for patterns in self.context_patterns.values())
        }
