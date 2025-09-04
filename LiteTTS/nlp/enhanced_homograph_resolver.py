#!/usr/bin/env python3
"""
Enhanced Homograph Disambiguation System for Phase 6: Advanced Text Processing
Addresses critical homograph pairs with improved contextual analysis and part-of-speech tagging
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PartOfSpeech(Enum):
    """Part of speech categories for homograph disambiguation"""
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PREPOSITION = "preposition"
    UNKNOWN = "unknown"

@dataclass
class HomographMatch:
    """Information about a homograph match"""
    word: str
    position: int
    context: str
    predicted_pos: PartOfSpeech
    pronunciation: str
    confidence: float

@dataclass
class HomographProcessingResult:
    """Result of homograph processing"""
    processed_text: str
    original_text: str
    homographs_resolved: List[HomographMatch]
    changes_made: List[str]

class EnhancedHomographResolver:
    """Enhanced homograph resolver with improved contextual analysis"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize enhanced homograph resolver
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.homograph_dict = self._load_enhanced_homograph_dictionary()
        self.context_patterns = self._compile_enhanced_context_patterns()
        self.pos_indicators = self._load_pos_indicators()
        
        logger.info("Enhanced Homograph Resolver initialized")
    
    def _load_enhanced_homograph_dictionary(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Load enhanced homograph dictionary with pronunciation variants"""
        return {
            'lead': {
                'metal': {
                    'pronunciation': 'led',
                    'pos': 'noun',
                    'definition': 'heavy metal element'
                },
                'verb': {
                    'pronunciation': 'leed',
                    'pos': 'verb',
                    'definition': 'to guide or direct'
                }
            },
            'wind': {
                'air': {
                    'pronunciation': 'wind',
                    'pos': 'noun',
                    'definition': 'moving air'
                },
                'coil': {
                    'pronunciation': 'wynd',
                    'pos': 'verb',
                    'definition': 'to turn or twist'
                }
            },
            'tear': {
                'rip': {
                    'pronunciation': 'tair',
                    'pos': 'verb',
                    'definition': 'to rip or damage'
                },
                'cry': {
                    'pronunciation': 'teer',
                    'pos': 'noun',
                    'definition': 'drop of liquid from eye'
                }
            },
            'desert': {
                'abandon': {
                    'pronunciation': 'dih-zurt',
                    'pos': 'verb',
                    'definition': 'to abandon or leave'
                },
                'arid': {
                    'pronunciation': 'dez-urt',
                    'pos': 'noun',
                    'definition': 'dry sandy region'
                }
            },
            'resume': {
                'continue': {
                    'pronunciation': 'ri-zoom',
                    'pos': 'verb',
                    'definition': 'to continue after pause'
                },
                'document': {
                    'pronunciation': 'rez-oo-may',
                    'pos': 'noun',
                    'definition': 'curriculum vitae'
                }
            },
            'wound': {
                'injury': {
                    'pronunciation': 'woond',
                    'pos': 'noun',
                    'definition': 'bodily injury'
                },
                'past_wind': {
                    'pronunciation': 'wownd',
                    'pos': 'verb',
                    'definition': 'past tense of wind'
                }
            },
            'bass': {
                'fish': {
                    'pronunciation': 'bas',
                    'pos': 'noun',
                    'definition': 'type of fish'
                },
                'music': {
                    'pronunciation': 'bayss',
                    'pos': 'noun',
                    'definition': 'low musical notes'
                }
            },
            'row': {
                'line': {
                    'pronunciation': 'roh',
                    'pos': 'noun',
                    'definition': 'line of things'
                },
                'argue': {
                    'pronunciation': 'row',
                    'pos': 'verb',
                    'definition': 'to argue or quarrel'
                },
                'boat': {
                    'pronunciation': 'roh',
                    'pos': 'verb',
                    'definition': 'to propel a boat'
                }
            },
            'record': {
                'document': {
                    'pronunciation': 'rek-ord',
                    'pos': 'noun',
                    'definition': 'written account'
                },
                'capture': {
                    'pronunciation': 'ri-kord',
                    'pos': 'verb',
                    'definition': 'to capture sound/video'
                }
            },
            'object': {
                'thing': {
                    'pronunciation': 'ob-jekt',
                    'pos': 'noun',
                    'definition': 'physical thing'
                },
                'oppose': {
                    'pronunciation': 'ob-jekt',
                    'pos': 'verb',
                    'definition': 'to oppose or disagree'
                }
            },
            'present': {
                'gift': {
                    'pronunciation': 'prez-ent',
                    'pos': 'noun',
                    'definition': 'gift or offering'
                },
                'current': {
                    'pronunciation': 'prez-ent',
                    'pos': 'adjective',
                    'definition': 'current or existing now'
                },
                'show': {
                    'pronunciation': 'pri-zent',
                    'pos': 'verb',
                    'definition': 'to show or give'
                }
            },
            'refuse': {
                'decline': {
                    'pronunciation': 'ri-fyooz',
                    'pos': 'verb',
                    'definition': 'to decline or reject'
                },
                'garbage': {
                    'pronunciation': 'ref-yoos',
                    'pos': 'noun',
                    'definition': 'waste or garbage'
                }
            },
            'contract': {
                'agreement': {
                    'pronunciation': 'kon-trakt',
                    'pos': 'noun',
                    'definition': 'legal agreement'
                },
                'shrink': {
                    'pronunciation': 'kon-trakt',
                    'pos': 'verb',
                    'definition': 'to shrink or reduce'
                }
            },
            'project': {
                'task': {
                    'pronunciation': 'proj-ekt',
                    'pos': 'noun',
                    'definition': 'planned task or work'
                },
                'extend': {
                    'pronunciation': 'pro-jekt',
                    'pos': 'verb',
                    'definition': 'to extend or display'
                }
            },
            'invalid': {
                'disabled': {
                    'pronunciation': 'in-vuh-lid',
                    'pos': 'noun',
                    'definition': 'disabled person'
                },
                'not_valid': {
                    'pronunciation': 'in-val-id',
                    'pos': 'adjective',
                    'definition': 'not valid or legal'
                }
            },
            'minute': {
                'time': {
                    'pronunciation': 'min-it',
                    'pos': 'noun',
                    'definition': 'unit of time'
                },
                'tiny': {
                    'pronunciation': 'my-noot',
                    'pos': 'adjective',
                    'definition': 'very small'
                }
            },
            'close': {
                'shut': {
                    'pronunciation': 'kloze',
                    'pos': 'verb',
                    'definition': 'to shut or seal'
                },
                'near': {
                    'pronunciation': 'klohs',
                    'pos': 'adjective',
                    'definition': 'near in distance'
                }
            },
            'live': {
                'alive': {
                    'pronunciation': 'liv',
                    'pos': 'adjective',
                    'definition': 'alive or living'
                },
                'broadcast': {
                    'pronunciation': 'lyv',
                    'pos': 'adjective',
                    'definition': 'broadcast in real time'
                },
                'reside': {
                    'pronunciation': 'liv',
                    'pos': 'verb',
                    'definition': 'to reside or dwell'
                }
            },
            'sow': {
                'plant': {
                    'pronunciation': 'soh',
                    'pos': 'verb',
                    'definition': 'to plant seeds'
                },
                'pig': {
                    'pronunciation': 'sow',
                    'pos': 'noun',
                    'definition': 'female pig'
                }
            },
            'does': {
                'performs': {
                    'pronunciation': 'duz',
                    'pos': 'verb',
                    'definition': 'third person singular of do'
                },
                'deer': {
                    'pronunciation': 'dohs',
                    'pos': 'noun',
                    'definition': 'female deer (plural)'
                }
            },
            'read': {
                'present': {
                    'pronunciation': 'reed',
                    'pos': 'verb',
                    'definition': 'to read (present tense)'
                },
                'past': {
                    'pronunciation': 'red',
                    'pos': 'verb',
                    'definition': 'to read (past tense)'
                }
            },
            'bow': {
                'bend': {
                    'pronunciation': 'bow',
                    'pos': 'verb',
                    'definition': 'to bend forward'
                },
                'weapon': {
                    'pronunciation': 'boh',
                    'pos': 'noun',
                    'definition': 'archery weapon'
                },
                'ship': {
                    'pronunciation': 'bow',
                    'pos': 'noun',
                    'definition': 'front of ship'
                }
            },
            'produce': {
                'create': {
                    'pronunciation': 'pro-doos',
                    'pos': 'verb',
                    'definition': 'to create or make'
                },
                'food': {
                    'pronunciation': 'proh-doos',
                    'pos': 'noun',
                    'definition': 'fresh fruits and vegetables'
                }
            }
        }
    
    def _compile_enhanced_context_patterns(self) -> Dict[str, List[Tuple[re.Pattern, str, float]]]:
        """Compile enhanced context patterns with confidence scores"""
        patterns = {}
        
        # Lead patterns with confidence scores
        patterns['lead'] = [
            (re.compile(r'\blead\s+(pipe|paint|poisoning|bullet|shot|weight)\b', re.IGNORECASE), 'metal', 0.95),
            (re.compile(r'\b(heavy|toxic|dangerous)\s+lead\b', re.IGNORECASE), 'metal', 0.90),
            (re.compile(r'\blead\s+(the|a|an)\s+(way|team|group|charge|effort)\b', re.IGNORECASE), 'verb', 0.95),
            (re.compile(r'\b(will|can|should|must|to)\s+lead\b', re.IGNORECASE), 'verb', 0.90),
            (re.compile(r'\blead\s+(by|with|through)\b', re.IGNORECASE), 'verb', 0.85),
        ]
        
        # Wind patterns
        patterns['wind'] = [
            (re.compile(r'\bwind\s+(speed|direction|storm|gust|chill)\b', re.IGNORECASE), 'air', 0.95),
            (re.compile(r'\b(strong|cold|warm|gentle|fierce)\s+wind\b', re.IGNORECASE), 'air', 0.90),
            (re.compile(r'\bwind\s+(up|down|around)\s+(the|a)\s+(clock|watch|toy|rope)\b', re.IGNORECASE), 'coil', 0.95),
            (re.compile(r'\b(will|can|should|must|to)\s+wind\b', re.IGNORECASE), 'coil', 0.85),
        ]
        
        # Tear patterns
        patterns['tear'] = [
            (re.compile(r'\btear\s+(up|down|apart|off|open)\b', re.IGNORECASE), 'rip', 0.95),
            (re.compile(r'\b(will|can|should|must|to)\s+tear\b', re.IGNORECASE), 'rip', 0.90),
            (re.compile(r'\b(shed|wipe|dry|single)\s+(a\s+)?tears?\b', re.IGNORECASE), 'cry', 0.95),
            (re.compile(r'\btears?\s+(of|from|in|down)\b', re.IGNORECASE), 'cry', 0.90),
        ]
        
        return patterns

    def _load_pos_indicators(self) -> Dict[PartOfSpeech, List[str]]:
        """Load part-of-speech indicator words"""
        return {
            PartOfSpeech.NOUN: [
                'the', 'a', 'an', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
                'some', 'any', 'many', 'few', 'several', 'each', 'every', 'all', 'both', 'either', 'neither'
            ],
            PartOfSpeech.VERB: [
                'will', 'would', 'can', 'could', 'should', 'shall', 'may', 'might', 'must', 'ought',
                'to', 'do', 'does', 'did', 'have', 'has', 'had', 'be', 'am', 'is', 'are', 'was', 'were'
            ],
            PartOfSpeech.ADJECTIVE: [
                'very', 'quite', 'rather', 'extremely', 'incredibly', 'really', 'truly', 'fairly', 'pretty',
                'more', 'most', 'less', 'least', 'too', 'so', 'such'
            ],
            PartOfSpeech.ADVERB: [
                'very', 'quite', 'rather', 'extremely', 'incredibly', 'really', 'truly', 'fairly', 'pretty'
            ]
        }

    def resolve_homographs(self, text: str) -> HomographProcessingResult:
        """Main homograph resolution method

        Args:
            text: Input text to process

        Returns:
            HomographProcessingResult with resolved homographs
        """
        logger.debug(f"Resolving homographs in text: {text[:100]}...")

        original_text = text
        homographs_resolved = []
        changes_made = []

        # Process each homograph word
        for word in self.homograph_dict.keys():
            if word.lower() in text.lower():
                text, word_matches = self._resolve_word_homographs(text, word)
                if word_matches:
                    homographs_resolved.extend(word_matches)
                    changes_made.extend([f"Resolved {match.word}: {match.pronunciation}" for match in word_matches])

        result = HomographProcessingResult(
            processed_text=text,
            original_text=original_text,
            homographs_resolved=homographs_resolved,
            changes_made=changes_made
        )

        logger.debug(f"Homograph resolution complete: {len(homographs_resolved)} homographs resolved")
        return result

    def _resolve_word_homographs(self, text: str, word: str) -> Tuple[str, List[HomographMatch]]:
        """Resolve all instances of a specific homograph word"""
        matches = []

        # Find all instances of the word
        word_pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)

        def replace_homograph(match):
            position = match.start()
            context = self._extract_context(text, position, match.end())

            # Determine the correct pronunciation
            pronunciation_key, confidence = self._determine_pronunciation(word, context)

            if pronunciation_key and word in self.homograph_dict:
                pronunciation_info = self.homograph_dict[word].get(pronunciation_key, {})
                pronunciation = pronunciation_info.get('pronunciation', word)

                # Create match record
                homograph_match = HomographMatch(
                    word=word,
                    position=position,
                    context=context,
                    predicted_pos=PartOfSpeech(pronunciation_info.get('pos', 'unknown')),
                    pronunciation=pronunciation,
                    confidence=confidence
                )
                matches.append(homograph_match)

                return pronunciation

            return match.group()  # Return original if no match

        processed_text = word_pattern.sub(replace_homograph, text)
        return processed_text, matches

    def _extract_context(self, text: str, start_pos: int, end_pos: int, context_size: int = 50) -> str:
        """Extract context around a word position"""
        context_start = max(0, start_pos - context_size)
        context_end = min(len(text), end_pos + context_size)
        return text[context_start:context_end]

    def _determine_pronunciation(self, word: str, context: str) -> Tuple[Optional[str], float]:
        """Determine the correct pronunciation based on context"""
        word_lower = word.lower()

        # Check context patterns first
        if word_lower in self.context_patterns:
            for pattern, pronunciation_key, confidence in self.context_patterns[word_lower]:
                if pattern.search(context):
                    return pronunciation_key, confidence

        # Use part-of-speech analysis as fallback
        predicted_pos = self._predict_part_of_speech(context, word)
        pronunciation_key = self._find_pronunciation_by_pos(word_lower, predicted_pos)

        if pronunciation_key:
            return pronunciation_key, 0.7  # Lower confidence for POS-based prediction

        # Default to first pronunciation if no match
        if word_lower in self.homograph_dict:
            first_key = list(self.homograph_dict[word_lower].keys())[0]
            return first_key, 0.5  # Low confidence for default

        return None, 0.0

    def _predict_part_of_speech(self, context: str, target_word: str) -> PartOfSpeech:
        """Predict part of speech based on surrounding words"""
        context_lower = context.lower()
        target_lower = target_word.lower()

        # Find the target word position in context
        word_match = re.search(r'\b' + re.escape(target_lower) + r'\b', context_lower)
        if not word_match:
            return PartOfSpeech.UNKNOWN

        word_start = word_match.start()
        word_end = word_match.end()

        # Get words before and after
        before_context = context_lower[:word_start].strip()
        after_context = context_lower[word_end:].strip()

        before_words = before_context.split()[-3:] if before_context else []
        after_words = after_context.split()[:3] if after_context else []

        # Check for noun indicators
        for indicator in self.pos_indicators[PartOfSpeech.NOUN]:
            if indicator in before_words:
                return PartOfSpeech.NOUN

        # Check for verb indicators
        for indicator in self.pos_indicators[PartOfSpeech.VERB]:
            if indicator in before_words:
                return PartOfSpeech.VERB

        # Check for adjective indicators
        for indicator in self.pos_indicators[PartOfSpeech.ADJECTIVE]:
            if indicator in before_words:
                return PartOfSpeech.ADJECTIVE

        # Check patterns in following words
        if after_words:
            first_after = after_words[0]
            # If followed by a noun, likely an adjective
            if first_after in ['the', 'a', 'an'] or first_after.endswith('s'):
                return PartOfSpeech.ADJECTIVE
            # If followed by preposition, likely a verb
            if first_after in ['to', 'from', 'with', 'by', 'in', 'on', 'at']:
                return PartOfSpeech.VERB

        return PartOfSpeech.UNKNOWN

    def _find_pronunciation_by_pos(self, word: str, pos: PartOfSpeech) -> Optional[str]:
        """Find pronunciation key based on part of speech"""
        if word not in self.homograph_dict:
            return None

        # Look for matching part of speech
        for key, info in self.homograph_dict[word].items():
            if info.get('pos') == pos.value:
                return key

        return None

    def get_homograph_statistics(self) -> Dict[str, int]:
        """Get statistics about available homographs"""
        stats = {
            'total_homographs': len(self.homograph_dict),
            'total_pronunciations': sum(len(variants) for variants in self.homograph_dict.values()),
            'words_with_context_patterns': len(self.context_patterns)
        }

        # Count by part of speech
        pos_counts = {}
        for word_variants in self.homograph_dict.values():
            for variant_info in word_variants.values():
                pos = variant_info.get('pos', 'unknown')
                pos_counts[pos] = pos_counts.get(pos, 0) + 1

        stats.update(pos_counts)
        return stats
