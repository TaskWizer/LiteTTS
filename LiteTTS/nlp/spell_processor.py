#!/usr/bin/env python3
"""
Spell processor for handling spell() function calls
"""

import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class SpellProcessor:
    """Handles spell() function calls for letter-by-letter pronunciation"""
    
    def __init__(self):
        self.letter_names = self._load_letter_names()
        
    def _load_letter_names(self) -> Dict[str, str]:
        """Load letter names for spelling"""
        return {
            'a': 'ay', 'b': 'bee', 'c': 'see', 'd': 'dee', 'e': 'ee',
            'f': 'eff', 'g': 'gee', 'h': 'aitch', 'i': 'eye', 'j': 'jay',
            'k': 'kay', 'l': 'ell', 'm': 'em', 'n': 'en', 'o': 'oh',
            'p': 'pee', 'q': 'cue', 'r': 'are', 's': 'ess', 't': 'tee',
            'u': 'you', 'v': 'vee', 'w': 'double-you', 'x': 'ex',
            'y': 'why', 'z': 'zee'
        }
    
    def handle_spell_functions(self, text: str) -> str:
        """Process spell() function calls in text"""
        logger.debug(f"Processing spell functions in: {text[:100]}...")
        
        # Pattern: spell(word) or spell("word") or spell('word')
        pattern = re.compile(r'spell\s*\(\s*["\']?([^"\')\s]+)["\']?\s*\)', re.IGNORECASE)
        
        def replace_spell(match):
            word = match.group(1).strip()
            return self._spell_word(word)
        
        result = pattern.sub(replace_spell, text)
        logger.debug(f"Spell processing result: {result[:100]}...")
        return result
    
    def _spell_word(self, word: str) -> str:
        """Convert word to spelled-out letters with natural pauses"""
        letters = []
        
        for char in word.lower():
            if char.isalpha():
                if char in self.letter_names:
                    letters.append(self.letter_names[char])
                else:
                    letters.append(char)
            elif char.isdigit():
                # Handle numbers in spelled words
                digit_names = {
                    '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
                    '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
                }
                letters.append(digit_names.get(char, char))
            else:
                # Handle special characters
                special_chars = {
                    '-': 'dash', '_': 'underscore', '.': 'dot', '@': 'at',
                    '#': 'hash', '$': 'dollar', '%': 'percent', '&': 'and',
                    '*': 'star', '+': 'plus', '=': 'equals', '!': 'exclamation',
                    '?': 'question', '/': 'slash', '\\': 'backslash',
                    '(': 'open paren', ')': 'close paren', '[': 'open bracket',
                    ']': 'close bracket', '{': 'open brace', '}': 'close brace'
                }
                letters.append(special_chars.get(char, char))
        
        # Join with natural pauses (commas create brief pauses in TTS)
        return ', '.join(letters)
    
    def spell_word_direct(self, word: str) -> str:
        """Direct method to spell a word (for API use)"""
        return self._spell_word(word)