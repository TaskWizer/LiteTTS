#!/usr/bin/env python3
"""
Comma handling fix processor for TTS pronunciation issues
Fixes "thinking, or" → "thinkinger" pronunciation problem
"""

import re
import logging
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

class CommaFixProcessor:
    """Processor to fix comma-related pronunciation issues in TTS"""
    
    def __init__(self):
        self.problematic_patterns = self._load_problematic_patterns()
        self.comma_context_patterns = self._load_comma_context_patterns()
        
    def _load_problematic_patterns(self) -> List[Tuple[str, str, str]]:
        """Load patterns that cause comma pronunciation issues"""
        return [
            # Pattern, Replacement, Description
            (r'(\w+),\s*(or|and|but|yet|so|nor|for)\b', r'\1, \2', 'Comma conjunction spacing'),
            (r'(\w+),\s*(if|when|while|because|since|although|though|unless|until)\b', r'\1, \2', 'Comma subordinate clause spacing'),
            (r'(\w+),\s*(however|therefore|moreover|furthermore|nevertheless|consequently)\b', r'\1, \2', 'Comma adverbial spacing'),
            (r'(\w+),\s*(which|who|that|where|when)\b', r'\1, \2', 'Comma relative clause spacing'),
            (r'(\w+),\s*(please|thanks|sorry|excuse me|pardon)\b', r'\1, \2', 'Comma politeness marker spacing'),
        ]
    
    def _load_comma_context_patterns(self) -> Dict[str, str]:
        """Load specific comma context fixes"""
        return {
            # Specific problematic phrases
            "thinking, or": "thinking, or",  # Ensure proper spacing
            "walking, and": "walking, and",
            "running, but": "running, but",
            "talking, so": "talking, so",
            "working, yet": "working, yet",
            "reading, for": "reading, for",
            "writing, nor": "writing, nor",
            
            # Common patterns that get mispronounced
            "going, or not": "going, or not",
            "coming, and then": "coming, and then",
            "looking, but seeing": "looking, but seeing",
            
            # Interjections with commas
            "hmm, let me think": "hmm, let me think",
            "well, I suppose": "well, I suppose",
            "oh, I see": "oh, I see",
            "ah, yes": "ah, yes",
        }
    
    def fix_comma_pronunciation(self, text: str) -> str:
        """Fix comma-related pronunciation issues"""
        logger.debug(f"Fixing comma pronunciation in: {text[:100]}...")
        
        original_text = text
        
        # Step 1: Fix specific problematic patterns
        text = self._fix_problematic_patterns(text)
        
        # Step 2: Fix comma spacing issues
        text = self._fix_comma_spacing(text)
        
        # Step 3: Handle comma-conjunction combinations
        text = self._fix_comma_conjunctions(text)
        
        # Step 4: Fix comma-interjection combinations
        text = self._fix_comma_interjections(text)
        
        if text != original_text:
            logger.debug(f"Comma fixes applied: '{original_text}' → '{text}'")
        
        return text
    
    def _fix_problematic_patterns(self, text: str) -> str:
        """Fix known problematic comma patterns"""
        for pattern, replacement, description in self.problematic_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                old_text = text
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                if text != old_text:
                    logger.debug(f"Applied {description}: '{old_text}' → '{text}'")
        
        return text
    
    def _fix_comma_spacing(self, text: str) -> str:
        """Ensure proper comma spacing to prevent pronunciation issues"""
        # Fix missing space after comma (but preserve existing correct spacing)
        text = re.sub(r',([^\s\d])', r', \1', text)
        
        # Fix multiple spaces after comma
        text = re.sub(r',\s{2,}', ', ', text)
        
        # Fix space before comma (remove it)
        text = re.sub(r'\s+,', ',', text)
        
        # Special handling for comma + conjunction to prevent "thinkinger" issue
        # Ensure there's exactly one space after comma before conjunctions
        conjunctions = ['or', 'and', 'but', 'yet', 'so', 'nor', 'for']
        for conj in conjunctions:
            # Pattern: word + comma + optional spaces + conjunction
            pattern = r'(\w+),\s*(' + re.escape(conj) + r')\b'
            replacement = r'\1, \2'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_comma_conjunctions(self, text: str) -> str:
        """Fix comma-conjunction combinations that cause pronunciation issues"""
        # Handle specific cases where comma + conjunction gets mispronounced
        
        # "thinking, or" type patterns - ensure clear separation
        thinking_verbs = ['thinking', 'walking', 'running', 'talking', 'working', 
                         'reading', 'writing', 'looking', 'going', 'coming']
        
        for verb in thinking_verbs:
            # Pattern: verb + comma + or/and/but
            for conj in ['or', 'and', 'but']:
                pattern = r'\b(' + re.escape(verb) + r'),\s*(' + re.escape(conj) + r')\b'
                replacement = r'\1, \2'
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_comma_interjections(self, text: str) -> str:
        """Fix comma-interjection combinations"""
        interjections = ['hmm', 'well', 'oh', 'ah', 'um', 'uh', 'er']
        
        for interjection in interjections:
            # Pattern: interjection + comma + word
            pattern = r'\b(' + re.escape(interjection) + r'),\s*(\w+)'
            replacement = r'\1, \2'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def analyze_comma_issues(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for potential comma pronunciation issues"""
        issues = {
            'missing_space_after_comma': [],
            'space_before_comma': [],
            'problematic_conjunctions': [],
            'potential_mispronunciations': []
        }
        
        # Check for missing space after comma
        missing_space_matches = re.findall(r',([^\s\d])', text)
        if missing_space_matches:
            issues['missing_space_after_comma'] = missing_space_matches
        
        # Check for space before comma
        space_before_matches = re.findall(r'(\w+)\s+,', text)
        if space_before_matches:
            issues['space_before_comma'] = space_before_matches
        
        # Check for problematic conjunction patterns
        for pattern, _, description in self.problematic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues['problematic_conjunctions'].extend([f"{description}: {match}" for match in matches])
        
        # Check for potential mispronunciations
        potential_issues = [
            r'(\w+ing),\s*(or|and|but)',  # -ing verbs with conjunctions
            r'(\w+),\s*(or|and|but)\s*(\w+ing)',  # conjunctions with -ing verbs
        ]
        
        for pattern in potential_issues:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues['potential_mispronunciations'].extend([str(match) for match in matches])
        
        return issues

# Global instance for easy access
comma_fix_processor = CommaFixProcessor()
