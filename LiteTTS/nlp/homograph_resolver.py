#!/usr/bin/env python3
"""
Homograph resolution system for disambiguating word pronunciations
"""

import re
from typing import Dict, List, Tuple, Optional
import logging
from .pronunciation_dictionary import PronunciationDictionary

logger = logging.getLogger(__name__)

class HomographResolver:
    """Resolves homograph pronunciations based on context and explicit markers"""
    
    def __init__(self):
        self.homograph_dict = self._load_homograph_dictionary()
        self.context_patterns = self._compile_context_patterns()
        self.pronunciation_dict = PronunciationDictionary()  # Enhanced pronunciation dictionary
        
    def _load_homograph_dictionary(self) -> Dict[str, Dict[str, str]]:
        """Load homograph dictionary with different pronunciations"""
        return {
            # Removed problematic pronunciation overrides for natural speech
            # Only keep actual homographs that need disambiguation
            'read': {
                'present': 'reed',  # I read books
                'past': 'red'       # I read the book yesterday
            },
            'lead': {
                'metal': 'led',     # Lead pipe
                'verb': 'leed'      # Lead the way
            },
            'tear': {
                'rip': 'tair',      # Tear the paper
                'cry': 'teer'       # Shed a tear
            },
            'wind': {
                'air': 'wind',      # The wind blows
                'coil': 'wynd'      # Wind the clock
            },
            'bow': {
                'bend': 'bow',      # Bow your head
                'weapon': 'boh'     # Bow and arrow
            },
            'close': {
                'shut': 'kloze',    # Close the door
                'near': 'klohs'     # Close to home
            },
            'desert': {
                'abandon': 'dih-zurt',  # Desert the army
                'arid': 'dez-urt'       # Sahara desert
            },
            'live': {
                'alive': 'liv',     # Live animals
                'broadcast': 'lyv'  # Live TV
            },
            'minute': {
                'time': 'min-it',   # One minute
                'tiny': 'my-noot'   # Minute details
            },
            'present': {
                'gift': 'prez-ent', # Birthday present
                'current': 'prez-ent', # Present time
                'show': 'pri-zent'  # Present the award
            },
            'produce': {
                'create': 'pro-doos',   # Produce goods
                'food': 'proh-doos'     # Fresh produce
            },
            'record': {
                'document': 'rek-ord',  # Keep a record
                'capture': 'ri-kord'    # Record a song
            }
        }    

    def _compile_context_patterns(self) -> Dict[str, List[Tuple[re.Pattern, str]]]:
        """Compile context patterns for automatic disambiguation"""
        patterns = {}
        
        # Read patterns - FIXED: better past tense detection
        patterns['read'] = [
            (re.compile(r'\b(will|can|should|must|to)\s+read\b', re.IGNORECASE), 'present'),
            (re.compile(r'\bread\s+(books?|newspapers?|articles?|stories?)\b', re.IGNORECASE), 'present'),
            (re.compile(r'\b(yesterday|last|already|had|have)\s+read\b', re.IGNORECASE), 'past'),
            (re.compile(r'\bread\s+(it|that|this)\s+(yesterday|before|already)\b', re.IGNORECASE), 'past'),
            (re.compile(r'\bread\s+yesterday\b', re.IGNORECASE), 'past'),  # More specific pattern
            (re.compile(r'\bI\s+read\s+yesterday\b', re.IGNORECASE), 'past')  # Very specific pattern
        ]
        
        # Lead patterns
        patterns['lead'] = [
            (re.compile(r'\blead\s+(pipe|paint|poisoning|bullet)\b', re.IGNORECASE), 'metal'),
            (re.compile(r'\b(will|can|should|must|to)\s+lead\b', re.IGNORECASE), 'verb'),
            (re.compile(r'\blead\s+(the|a|an)\s+(way|team|group|charge)\b', re.IGNORECASE), 'verb')
        ]
        
        # Tear patterns
        patterns['tear'] = [
            (re.compile(r'\btear\s+(up|down|apart|off)\b', re.IGNORECASE), 'rip'),
            (re.compile(r'\b(shed|wipe|dry)\s+(a\s+)?tear\b', re.IGNORECASE), 'cry'),
            (re.compile(r'\btears?\s+(of|from|in)\b', re.IGNORECASE), 'cry')
        ]
        
        # Wind patterns
        patterns['wind'] = [
            (re.compile(r'\bwind\s+(blows?|speed|direction|storm)\b', re.IGNORECASE), 'air'),
            (re.compile(r'\bwind\s+(up|down|the|a)\s+(clock|watch|toy)\b', re.IGNORECASE), 'coil'),
            (re.compile(r'\b(strong|cold|warm|gentle)\s+wind\b', re.IGNORECASE), 'air')
        ]
        
        # Close patterns
        patterns['close'] = [
            (re.compile(r'\bclose\s+(the|a|an)\s+(door|window|book|eyes?)\b', re.IGNORECASE), 'shut'),
            (re.compile(r'\b(very|too|so|quite)\s+close\b', re.IGNORECASE), 'near'),
            (re.compile(r'\bclose\s+(to|by|together)\b', re.IGNORECASE), 'near')
        ]
        
        # Produce patterns
        patterns['produce'] = [
            (re.compile(r'\bproduce\s+(goods|results|energy|music)\b', re.IGNORECASE), 'create'),
            (re.compile(r'\b(fresh|organic|local)\s+produce\b', re.IGNORECASE), 'food'),
            (re.compile(r'\bproduce\s+(section|aisle|department)\b', re.IGNORECASE), 'food')
        ]
        
        # Record patterns
        patterns['record'] = [
            (re.compile(r'\brecord\s+(a|the)\s+(song|album|video|sound)\b', re.IGNORECASE), 'capture'),
            (re.compile(r'\b(keep|maintain|check)\s+(a\s+)?record\b', re.IGNORECASE), 'document'),
            (re.compile(r'\brecord\s+(book|keeping|player)\b', re.IGNORECASE), 'document')
        ]
        
        return patterns    

    def resolve_homographs(self, text: str) -> str:
        """Main function to resolve homographs in text"""
        logger.debug(f"Resolving homographs in: {text[:100]}...")
        
        # First, handle explicit markers
        text = self._process_explicit_markers(text)

        # Then, handle simple word replacements for consistent pronunciation
        text = self._process_simple_replacements(text)

        # Apply comprehensive pronunciation dictionary
        text = self._apply_pronunciation_dictionary(text)

        # Then, use context-based resolution
        text = self._resolve_by_context(text)
        
        logger.debug(f"Homograph resolution result: {text[:100]}...")
        return text
    
    def _process_explicit_markers(self, text: str) -> str:
        """Process explicit homograph markers like 'produce_noun'"""
        # Pattern for explicit markers: word_type
        marker_pattern = re.compile(r'\b(\w+)_(\w+)\b')
        
        def replace_marker(match):
            word = match.group(1).lower()
            marker = match.group(2).lower()
            
            if word in self.homograph_dict:
                pronunciations = self.homograph_dict[word]
                
                # Map common markers to pronunciation keys
                marker_map = {
                    'noun': self._find_noun_pronunciation(word, pronunciations),
                    'verb': self._find_verb_pronunciation(word, pronunciations),
                    'past': 'past',
                    'present': 'present',
                    'metal': 'metal',
                    'food': 'food',
                    'create': 'create',
                    'document': 'document',
                    'capture': 'capture'
                }
                
                if marker in marker_map and marker_map[marker] in pronunciations:
                    return pronunciations[marker_map[marker]]
                elif marker in pronunciations:
                    return pronunciations[marker]
            
            # If no match found, return original word without marker
            return word
        
        return marker_pattern.sub(replace_marker, text)

    def _process_simple_replacements(self, text: str) -> str:
        """Process simple word replacements for consistent pronunciation"""
        # FIXED: Only apply replacements for words that actually need phonetic help
        # Removed hedonism and inherently as they should be pronounced naturally
        replacements = {
            # Only keep asterisk as it's a symbol that needs pronunciation help
            # 'asterisk': 'AS-ter-isk',  # Commented out - let natural pronunciation handle it
        }

        for word, pronunciation in replacements.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(word) + r'\b'
            text = re.sub(pattern, pronunciation, text, flags=re.IGNORECASE)

        return text
    
    def _resolve_by_context(self, text: str) -> str:
        """Resolve homographs using context patterns"""
        for word, patterns in self.context_patterns.items():
            if word in text.lower():
                for pattern, pronunciation_key in patterns:
                    if pattern.search(text):
                        # Replace the word with its pronunciation
                        if word in self.homograph_dict and pronunciation_key in self.homograph_dict[word]:
                            pronunciation = self.homograph_dict[word][pronunciation_key]
                            # Replace all instances of the word in the matched context
                            word_pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                            text = word_pattern.sub(pronunciation, text)
                            break  # Use first matching pattern
        
        return text    
 
    def _find_noun_pronunciation(self, word: str, pronunciations: Dict[str, str]) -> Optional[str]:
        """Find the noun pronunciation for a word"""
        # Common noun keys
        noun_keys = ['noun', 'thing', 'document', 'food', 'metal', 'person', 'agreement', 'product']
        for key in noun_keys:
            if key in pronunciations:
                return key
        return None
    
    def _find_verb_pronunciation(self, word: str, pronunciations: Dict[str, str]) -> Optional[str]:
        """Find the verb pronunciation for a word"""
        # Common verb keys
        verb_keys = ['verb', 'create', 'capture', 'shut', 'change', 'allow', 'advance']
        for key in verb_keys:
            if key in pronunciations:
                return key
        return None
    
    def add_homograph(self, word: str, pronunciations: Dict[str, str]):
        """Add a new homograph to the dictionary"""
        self.homograph_dict[word] = pronunciations
        logger.info(f"Added homograph: {word} with pronunciations: {list(pronunciations.keys())}")
    
    def get_homograph_info(self, word: str) -> Optional[Dict[str, str]]:
        """Get pronunciation options for a homograph"""
        return self.homograph_dict.get(word.lower())
    
    def list_homographs(self) -> List[str]:
        """Get list of all known homographs"""
        return list(self.homograph_dict.keys())

    def _apply_pronunciation_dictionary(self, text: str) -> str:
        """Apply comprehensive pronunciation dictionary to improve accuracy"""
        words = text.split()
        result_words = []

        for word in words:
            # Clean word of punctuation for lookup
            clean_word = re.sub(r'[^\w\'-]', '', word)

            if self.pronunciation_dict.has_pronunciation(clean_word):
                # Get the correct pronunciation
                pronunciation = self.pronunciation_dict.get_pronunciation(clean_word)

                # Preserve original punctuation
                if clean_word != word:
                    # Find punctuation and preserve it
                    prefix = word[:word.find(clean_word)] if clean_word in word else ''
                    suffix = word[word.find(clean_word) + len(clean_word):] if clean_word in word else ''
                    result_words.append(prefix + pronunciation + suffix)
                else:
                    result_words.append(pronunciation)
            else:
                result_words.append(word)

        return ' '.join(result_words)