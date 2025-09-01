#!/usr/bin/env python3
"""
Extended pronunciation dictionary for TTS accuracy
Includes word-specific pronunciation fixes and context-aware pronunciations
"""

import re
from typing import Dict, List, Tuple, Optional, Union
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ExtendedPronunciationDictionary:
    """Extended pronunciation dictionary with context-aware pronunciations"""
    
    def __init__(self):
        self.word_pronunciations = self._load_word_pronunciations()
        self.context_pronunciations = self._load_context_pronunciations()
        self.homograph_rules = self._load_homograph_rules()
        self.phonetic_overrides = self._load_phonetic_overrides()
        
        # Configuration
        self.use_context_awareness = True
        self.use_phonetic_spelling = True
        
    def _load_word_pronunciations(self) -> Dict[str, str]:
        """Load word-specific pronunciation fixes"""
        return {
            # Specific pronunciation issues identified
            'resume': 'rez-uh-may',  # Not "re-zoom"
            'résumé': 'rez-uh-may',  # French accent version
            
            # Common mispronunciations
            'asterisk': 'AS-ter-isk',  # Not "astrisk"
            'nuclear': 'NEW-klee-er',  # Not "NEW-kyuh-ler"
            'library': 'LY-brer-ee',  # Not "LY-berry"
            'february': 'FEB-roo-er-ee',  # Not "FEB-yoo-ary"
            'wednesday': 'WENZ-day',  # Not "WED-nes-day"
            'colonel': 'KER-nel',  # Not "ko-lo-NEL"
            'comfortable': 'KUMF-ter-bul',  # Not "com-FOR-table"
            'often': 'OF-en',  # Not "OF-ten"
            
            # Words with silent letters
            'salmon': 'SAM-un',  # Silent 'l'
            'almond': 'AH-mund',  # Silent 'l'
            'palm': 'PAHM',  # Silent 'l'
            'calm': 'KAHM',  # Silent 'l'
            'half': 'HAF',  # Silent 'l'
            'walk': 'WAWK',  # Silent 'l'
            'talk': 'TAWK',  # Silent 'l'
            'chalk': 'CHAWK',  # Silent 'l'
            'folk': 'FOHK',  # Silent 'l'
            'yolk': 'YOHK',  # Silent 'l'
            'debt': 'DET',  # Silent 'b'
            'doubt': 'DOWT',  # Silent 'b'
            'lamb': 'LAM',  # Silent 'b'
            'thumb': 'THUM',  # Silent 'b'
            'comb': 'KOHM',  # Silent 'b'
            'tomb': 'TOOM',  # Silent 'b'
            'womb': 'WOOM',  # Silent 'b'
            'knee': 'NEE',  # Silent 'k'
            'knife': 'NYFE',  # Silent 'k'
            'knight': 'NYGHT',  # Silent 'k'
            'know': 'NOH',  # Silent 'k'
            'known': 'NOHN',  # Silent 'k'
            
            # Technical terms
            'cache': 'KASH',  # Not "kay-shay"
            'suite': 'SWEET',  # Not "suit"
            'segue': 'SEG-way',  # Not "seg-you"
            'epitome': 'ih-PIT-uh-mee',  # Not "EP-ih-tohm"
            'hyperbole': 'hy-PER-buh-lee',  # Not "HY-per-bowl"
            'facade': 'fuh-SAHD',  # Not "fay-KAYD"
            'niche': 'NEESH',  # Not "NITCH"
            'genre': 'ZHAHN-ruh',  # Not "JEN-er"
            'rendezvous': 'RAHN-day-voo',  # Not "ren-DEZ-vous"
            'entrepreneur': 'ahn-truh-pruh-NUR',  # Not "en-tre-pre-NOOR"
            
            # Names and proper nouns
            'worcestershire': 'WOOS-ter-sher',  # Not "wor-SES-ter-shy-er"
            'leicester': 'LES-ter',  # Not "ly-SES-ter"
            'gloucester': 'GLOS-ter',  # Not "glow-SES-ter"
            
            # Foreign words commonly used in English
            'croissant': 'kwah-SAHN',  # Not "KROY-sant"
            'bruschetta': 'broo-SKET-tah',  # Not "broo-SHET-tah"
            'gnocchi': 'NYOH-kee',  # Not "noh-CHEE"
            'quinoa': 'KEEN-wah',  # Not "kwin-OH-ah"
            'acai': 'ah-sah-EE',  # Not "ah-KAI"
            'chipotle': 'chih-POHT-lay',  # Not "chip-OT-el"
            
            # Scientific terms
            'alzheimer': 'AHLTS-hy-mer',  # Not "alz-HY-mer"
            'diabetes': 'dy-uh-BEE-teez',  # Not "dy-uh-BEE-tis"
            'pneumonia': 'noo-MOHN-yah',  # Not "pneu-MOHN-ee-ah"
            'mnemonic': 'nih-MON-ik',  # Not "muh-MON-ik"
            
            # Common words with tricky pronunciations
            'mischievous': 'MIS-chuh-vus',  # Not "mis-CHEE-vee-us"
            'jewelry': 'JOO-ul-ree',  # Not "JOO-uh-ler-ee"
            'realtor': 'REE-ul-ter',  # Not "REE-lah-ter"
            'sherbet': 'SHER-bit',  # Not "SHER-bert"
            'supposedly': 'suh-POHZ-id-lee',  # Not "suh-POHZ-uh-blee"
            'espresso': 'eh-SPRES-oh',  # Not "ex-PRES-oh"
            'prescription': 'prih-SKRIP-shun',  # Not "per-SKRIP-shun"
            'arctic': 'ARK-tik',  # Not "AR-tik"
            'athlete': 'ATH-leet',  # Not "ATH-uh-leet"
            'height': 'HYGHT',  # Not "HYGHT-th"
            'length': 'LENGTH',  # Not "LENG-th"
            'strength': 'STRENGTH',  # Not "STRENG-th"
        }
    
    def _load_context_pronunciations(self) -> Dict[str, Dict[str, str]]:
        """Load context-dependent pronunciations for homographs"""
        return {
            'read': {
                'present': 'REED',  # "I read books"
                'past': 'RED',      # "I read the book yesterday"
            },
            'lead': {
                'verb': 'LEED',     # "to lead"
                'noun': 'LED',      # "lead pipe"
            },
            'tear': {
                'cry': 'TEER',      # "tear from crying"
                'rip': 'TAIR',      # "tear the paper"
            },
            'wind': {
                'air': 'WIND',      # "the wind blows"
                'coil': 'WYND',     # "wind the clock"
            },
            'bow': {
                'bend': 'BOW',      # "bow down"
                'weapon': 'BOH',    # "bow and arrow"
                'ribbon': 'BOH',    # "tie a bow"
            },
            'close': {
                'near': 'KLOHS',    # "close to me"
                'shut': 'KLOHZ',    # "close the door"
            },
            'desert': {
                'dry': 'DEZ-ert',   # "Sahara desert"
                'abandon': 'dih-ZERT',  # "desert the army"
            },
            'object': {
                'thing': 'OB-jekt', # "an object"
                'protest': 'ob-JEKT',  # "I object"
            },
            'present': {
                'gift': 'PREZ-ent', # "a present"
                'now': 'PREZ-ent',  # "present time"
                'give': 'prih-ZENT', # "present the award"
            },
            'record': {
                'document': 'REK-ord',  # "a record"
                'capture': 'rih-KORD',  # "record the song"
            },
            'refuse': {
                'decline': 'rih-FYOOZ',  # "refuse to go"
                'garbage': 'REF-yoos',   # "refuse collection"
            },
            'subject': {
                'topic': 'SUB-jekt',    # "school subject"
                'expose': 'sub-JEKT',   # "subject to criticism"
            },
            'suspect': {
                'doubt': 'suh-SPEKT',   # "I suspect"
                'person': 'SUS-pekt',   # "the suspect"
            },
        }
    
    def _load_homograph_rules(self) -> List[Tuple[str, str, str]]:
        """Load rules for detecting homograph context"""
        return [
            # (word, context_pattern, pronunciation_key)
            ('read', r'\b(will|going to|always|usually|often)\s+read\b', 'present'),
            ('read', r'\bread\s+(yesterday|last|ago|before)\b', 'past'),
            ('lead', r'\b(to|will|can|should)\s+lead\b', 'verb'),
            ('lead', r'\b(a|the|some)\s+lead\s+(pipe|paint|pencil)\b', 'noun'),
            ('tear', r'\b(shed|cry|wipe)\s+tear\b', 'cry'),
            ('tear', r'\b(rip|tear)\s+(up|apart|down)\b', 'rip'),
            ('wind', r'\b(strong|gentle|cold)\s+wind\b', 'air'),
            ('wind', r'\b(wind)\s+(up|down|the)\b', 'coil'),
        ]
    
    def _load_phonetic_overrides(self) -> Dict[str, str]:
        """Load phonetic spelling overrides for difficult words"""
        return {
            # Use phonetic spelling for words that are consistently mispronounced
            'colonel': 'kernel',  # Phonetic spelling
            'worcestershire': 'wooster-sher',  # Phonetic spelling
            'leicester': 'lester',  # Phonetic spelling
            'gloucester': 'gloster',  # Phonetic spelling
        }
    
    def get_pronunciation(self, word: str, context: str = "") -> str:
        """Get the correct pronunciation for a word, considering context"""
        word_lower = word.lower()
        
        # Check for context-dependent pronunciations first
        if self.use_context_awareness and word_lower in self.context_pronunciations:
            context_pronunciation = self._get_context_pronunciation(word_lower, context)
            if context_pronunciation:
                return context_pronunciation
        
        # Check for phonetic overrides
        if self.use_phonetic_spelling and word_lower in self.phonetic_overrides:
            return self.phonetic_overrides[word_lower]
        
        # Check for direct word pronunciations
        if word_lower in self.word_pronunciations:
            return self.word_pronunciations[word_lower]
        
        # Return original word if no pronunciation found
        return word
    
    def _get_context_pronunciation(self, word: str, context: str) -> Optional[str]:
        """Get context-dependent pronunciation using rules"""
        if word not in self.context_pronunciations:
            return None
        
        # Apply homograph rules
        for rule_word, pattern, pronunciation_key in self.homograph_rules:
            if rule_word == word and re.search(pattern, context, re.IGNORECASE):
                pronunciations = self.context_pronunciations[word]
                if pronunciation_key in pronunciations:
                    return pronunciations[pronunciation_key]
        
        # Default to first pronunciation if no context match
        pronunciations = self.context_pronunciations[word]
        return list(pronunciations.values())[0]
    
    def process_text_pronunciations(self, text: str) -> str:
        """Process entire text for pronunciation fixes"""
        logger.debug(f"Processing pronunciations in: {text[:100]}...")
        
        # Split text into words while preserving punctuation
        words = re.findall(r'\b\w+\b|\W+', text)
        
        processed_words = []
        for i, word in enumerate(words):
            if re.match(r'\b\w+\b', word):  # It's a word
                # Get context (surrounding words)
                context_start = max(0, i - 5)
                context_end = min(len(words), i + 6)
                context = ''.join(words[context_start:context_end])
                
                # Get pronunciation
                pronunciation = self.get_pronunciation(word, context)
                processed_words.append(pronunciation)
            else:
                # It's punctuation or whitespace
                processed_words.append(word)
        
        result = ''.join(processed_words)
        logger.debug(f"Pronunciation processing result: {result[:100]}...")
        return result
    
    def add_pronunciation(self, word: str, pronunciation: str, context: str = None):
        """Add a new pronunciation to the dictionary"""
        word_lower = word.lower()
        
        if context:
            if word_lower not in self.context_pronunciations:
                self.context_pronunciations[word_lower] = {}
            self.context_pronunciations[word_lower][context] = pronunciation
        else:
            self.word_pronunciations[word_lower] = pronunciation
        
        logger.info(f"Added pronunciation: {word} -> {pronunciation}" + 
                   (f" (context: {context})" if context else ""))
    
    def analyze_pronunciations(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for words with known pronunciation issues"""
        info = {
            'known_pronunciations': [],
            'context_dependent': [],
            'potential_issues': []
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            if word in self.word_pronunciations:
                info['known_pronunciations'].append(word)
            if word in self.context_pronunciations:
                info['context_dependent'].append(word)
        
        # Check for potential issues (words that commonly cause problems)
        potential_issues = [
            'nuclear', 'library', 'february', 'wednesday', 'comfortable',
            'mischievous', 'jewelry', 'realtor', 'sherbet', 'supposedly',
            'espresso', 'prescription', 'arctic', 'athlete'
        ]
        
        for word in words:
            if word in potential_issues and word not in self.word_pronunciations:
                info['potential_issues'].append(word)
        
        return info
    
    def export_pronunciations(self, filepath: str):
        """Export pronunciations to JSON file"""
        data = {
            'word_pronunciations': self.word_pronunciations,
            'context_pronunciations': self.context_pronunciations,
            'phonetic_overrides': self.phonetic_overrides,
            'metadata': {
                'version': '1.0',
                'description': 'Extended pronunciation dictionary for TTS accuracy'
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Pronunciations exported to: {filepath}")
    
    def import_pronunciations(self, filepath: str):
        """Import pronunciations from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'word_pronunciations' in data:
                self.word_pronunciations.update(data['word_pronunciations'])
            if 'context_pronunciations' in data:
                self.context_pronunciations.update(data['context_pronunciations'])
            if 'phonetic_overrides' in data:
                self.phonetic_overrides.update(data['phonetic_overrides'])
            
            logger.info(f"Pronunciations imported from: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to import pronunciations from {filepath}: {e}")
    
    def set_configuration(self, use_context_awareness: bool = None,
                         use_phonetic_spelling: bool = None):
        """Set configuration options"""
        if use_context_awareness is not None:
            self.use_context_awareness = use_context_awareness
        if use_phonetic_spelling is not None:
            self.use_phonetic_spelling = use_phonetic_spelling
        
        logger.info(f"Pronunciation dictionary configuration updated: "
                   f"use_context_awareness={self.use_context_awareness}, "
                   f"use_phonetic_spelling={self.use_phonetic_spelling}")
