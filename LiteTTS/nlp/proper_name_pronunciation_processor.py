#!/usr/bin/env python3
"""
Proper Name and Word Pronunciation Processor for TTS
Fixes specific word mispronunciations like Elon→alon, Joy→joie, acquisition→ek-wah-zi·shn
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Set
import logging

logger = logging.getLogger(__name__)

class ProperNamePronunciationProcessor:
    """Processor for fixing specific proper name and word pronunciation issues"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.proper_name_fixes = self._load_proper_name_fixes()
        self.word_pronunciation_fixes = self._load_word_pronunciation_fixes()
        self.context_sensitive_fixes = self._load_context_sensitive_fixes()
        self.enabled = self._is_enabled()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from config.json"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load config from {config_path}: {e}")
            return {}
    
    def _is_enabled(self) -> bool:
        """Check if proper name pronunciation fixes are enabled"""
        return (self.config.get('text_processing', {})
                .get('proper_name_handling', {})
                .get('enabled', True))
    
    def _load_proper_name_fixes(self) -> Dict[str, str]:
        """Load proper name pronunciation fixes"""
        default_fixes = {
            # Names with specific pronunciation issues
            "Elon": "EE-lawn",  # Fix Elon→alon to EE-lawn
            "Tesla": "TESS-lah",  # Ensure correct pronunciation
            "Bezos": "BAY-zohss",  # Jeff Bezos
            "Musk": "MUHSK",  # Elon Musk
            "Zuckerberg": "ZUHK-er-berg",  # Mark Zuckerberg
            "Pichai": "pih-CHIGH",  # Sundar Pichai
            "Nadella": "nah-DELL-ah",  # Satya Nadella
            "Cook": "KOOK",  # Tim Cook (when referring to Apple CEO)
            "Wojcicki": "woh-JIT-skee",  # Susan Wojcicki
            "Dorsey": "DOR-see",  # Jack Dorsey
            
            # Geographic names
            "Nevada": "neh-VAD-ah",
            "Oregon": "OR-eh-gun", 
            "Illinois": "ill-ih-NOY",
            "Arkansas": "AR-kan-saw",
            "Qatar": "KAH-tar",
            "Dubai": "doo-BYE",
            
            # Brand names
            "Nike": "NYE-kee",
            "Adidas": "ah-DEE-dahs",
            "Porsche": "POR-shuh",
            "Hyundai": "HUN-day",
            "Xiaomi": "SHAO-mee",
            
            # Common name fixes
            "Joy": "JOI",  # Fix Joy→joie to JOI (phonetic spelling)
            "Sean": "SHAWN",
            "Siobhan": "shih-VAWN",
            "Niamh": "NEEV",
            "Aoife": "EE-fah"
        }
        
        # Get fixes from config, fall back to defaults
        config_fixes = (self.config.get('text_processing', {})
                       .get('proper_name_handling', {})
                       .get('name_pronunciations', {}))
        
        # Merge config fixes with defaults
        fixes = default_fixes.copy()
        fixes.update(config_fixes)
        
        return fixes
    
    def _load_word_pronunciation_fixes(self) -> Dict[str, str]:
        """Load general word pronunciation fixes"""
        default_fixes = {
            # Business/technical terms
            "acquisition": "ak-wih-ZISH-un",  # Fix acquisition→ek-wah-zi·shn to a·kwuh·zi·shn
            "merger": "MUR-jer",
            "synergy": "SIN-er-jee",
            "paradigm": "PAIR-ah-dime",
            "epitome": "ih-PIT-oh-mee",
            "hyperbole": "hy-PUR-boh-lee",
            "cache": "KASH",
            "niche": "NEESH",
            "suite": "SWEET",
            "segue": "SEG-way",
            
            # Financial terms
            "finance": "fye-NANS",
            "economic": "ee-kah-NOM-ik",
            "fiscal": "FIS-kal",
            "revenue": "REV-eh-noo",
            "dividend": "DIV-ih-dend",
            
            # Technology terms
            "algorithm": "AL-goh-rith-um",
            "API": "A-P-I",
            "GUI": "GOO-ee",
            "SQL": "SEE-kwel",
            "JSON": "JAY-sahn",
            "XML": "X-M-L",
            "HTTP": "H-T-T-P",
            "URL": "U-R-L",
            
            # Common mispronunciations
            "often": "OF-en",  # Not "OF-ten"
            "nuclear": "NOO-klee-er",  # Not "NOO-kyuh-ler"
            "library": "LYE-brer-ee",  # Not "LYE-berry"
            "February": "FEB-roo-er-ee",  # Not "FEB-yoo-er-ee"
            "comfortable": "KUMF-ter-bul",
            "vegetable": "VEJ-tah-bul",
            "temperature": "TEM-per-ah-chur"
        }
        
        # Get fixes from config
        config_fixes = (self.config.get('text_processing', {})
                       .get('proper_name_handling', {})
                       .get('word_pronunciations', {}))
        
        # Merge config fixes with defaults
        fixes = default_fixes.copy()
        fixes.update(config_fixes)
        
        return fixes
    
    def _load_context_sensitive_fixes(self) -> List[Tuple[str, str, str, str]]:
        """Load context-sensitive pronunciation fixes"""
        return [
            # (word, context_pattern, pronunciation, description)
            ("resume", r"\b(my|your|his|her|their)\s+resume\b", "REZ-oo-may", "Resume document context"),
            ("resume", r"\bresume\s+(work|working|operations|activities)", "rih-ZOOM", "Resume activity context"),
            ("live", r"\blive\s+(stream|broadcast|show|event)", "LYVE", "Live event context"),
            ("live", r"\bwhere\s+do\s+you\s+live", "LIV", "Live residence context"),
            ("read", r"\b(I|you|we|they)\s+read\s+(yesterday|last)", "RED", "Past tense read"),
            ("read", r"\b(will|going\s+to|plan\s+to)\s+read", "REED", "Future tense read"),
            ("lead", r"\blead\s+(singer|guitarist|developer|engineer)", "LEED", "Lead role context"),
            ("lead", r"\blead\s+(pipe|paint|poisoning|metal)", "LED", "Lead metal context"),
        ]
    
    def process_proper_name_pronunciation(self, text: str) -> str:
        """Apply proper name and word pronunciation fixes"""
        if not self.enabled:
            return text
            
        logger.debug(f"Applying proper name pronunciation fixes to: {text[:100]}...")
        
        original_text = text
        
        # Apply proper name fixes
        text = self._apply_proper_name_fixes(text)
        
        # Apply word pronunciation fixes
        text = self._apply_word_pronunciation_fixes(text)
        
        # Apply context-sensitive fixes
        text = self._apply_context_sensitive_fixes(text)
        
        if text != original_text:
            logger.debug(f"Proper name pronunciation fixes applied: '{original_text}' → '{text}'")
        
        return text
    
    def _apply_proper_name_fixes(self, text: str) -> str:
        """Apply proper name pronunciation fixes"""
        for name, pronunciation in self.proper_name_fixes.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(name) + r'\b'
            
            # Apply case-insensitive replacement while preserving original case
            def replace_with_case_preservation(match):
                original = match.group(0)
                
                # If original is all caps, make pronunciation all caps
                if original.isupper():
                    return pronunciation.upper()
                # If original starts with capital, capitalize pronunciation
                elif original[0].isupper():
                    return pronunciation.capitalize()
                # Otherwise, keep pronunciation as-is
                else:
                    return pronunciation.lower()
            
            text = re.sub(pattern, replace_with_case_preservation, text, flags=re.IGNORECASE)
        
        return text
    
    def _apply_word_pronunciation_fixes(self, text: str) -> str:
        """Apply general word pronunciation fixes"""
        for word, pronunciation in self.word_pronunciation_fixes.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(word) + r'\b'
            
            # Apply case-insensitive replacement while preserving original case
            def replace_with_case_preservation(match):
                original = match.group(0)
                
                # If original is all caps, make pronunciation all caps
                if original.isupper():
                    return pronunciation.upper()
                # If original starts with capital, capitalize pronunciation
                elif original[0].isupper():
                    return pronunciation.capitalize()
                # Otherwise, keep pronunciation as-is
                else:
                    return pronunciation.lower()
            
            text = re.sub(pattern, replace_with_case_preservation, text, flags=re.IGNORECASE)
        
        return text
    
    def _apply_context_sensitive_fixes(self, text: str) -> str:
        """Apply context-sensitive pronunciation fixes"""
        for word, context_pattern, pronunciation, description in self.context_sensitive_fixes:
            # Check if the context pattern matches
            if re.search(context_pattern, text, re.IGNORECASE):
                # Apply the pronunciation fix within the context
                word_pattern = r'\b' + re.escape(word) + r'\b'
                
                def replace_with_case_preservation(match):
                    original = match.group(0)
                    
                    # If original is all caps, make pronunciation all caps
                    if original.isupper():
                        return pronunciation.upper()
                    # If original starts with capital, capitalize pronunciation
                    elif original[0].isupper():
                        return pronunciation.capitalize()
                    # Otherwise, keep pronunciation as-is
                    else:
                        return pronunciation.lower()
                
                text = re.sub(word_pattern, replace_with_case_preservation, text, flags=re.IGNORECASE)
                logger.debug(f"Applied context-sensitive fix: {description}")
        
        return text
    
    def analyze_pronunciation_issues(self, text: str) -> Dict:
        """Analyze potential pronunciation issues in text"""
        analysis = {
            'proper_names_found': [],
            'words_with_fixes': [],
            'context_sensitive_matches': [],
            'potential_issues': [],
            'suggestions': []
        }
        
        # Check for proper names
        for name in self.proper_name_fixes.keys():
            if re.search(r'\b' + re.escape(name) + r'\b', text, re.IGNORECASE):
                analysis['proper_names_found'].append(name)
        
        # Check for words with fixes
        for word in self.word_pronunciation_fixes.keys():
            if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
                analysis['words_with_fixes'].append(word)
        
        # Check for context-sensitive matches
        for word, context_pattern, pronunciation, description in self.context_sensitive_fixes:
            if re.search(context_pattern, text, re.IGNORECASE):
                analysis['context_sensitive_matches'].append({
                    'word': word,
                    'context': description,
                    'pronunciation': pronunciation
                })
        
        return analysis
    
    def add_pronunciation_fix(self, word: str, pronunciation: str, is_proper_name: bool = False):
        """Add a new pronunciation fix"""
        if is_proper_name:
            self.proper_name_fixes[word] = pronunciation
            logger.info(f"Added proper name pronunciation: {word} → {pronunciation}")
        else:
            self.word_pronunciation_fixes[word] = pronunciation
            logger.info(f"Added word pronunciation: {word} → {pronunciation}")
    
    def get_all_fixes(self) -> Dict:
        """Get all pronunciation fixes"""
        return {
            'proper_names': self.proper_name_fixes.copy(),
            'words': self.word_pronunciation_fixes.copy(),
            'context_sensitive': self.context_sensitive_fixes.copy()
        }

# Example usage and testing
if __name__ == "__main__":
    # Create processor
    processor = ProperNamePronunciationProcessor()
    
    # Test critical pronunciation fixes
    test_cases = [
        "Elon Musk announced new Tesla features",
        "The acquisition was completed successfully", 
        "Joy is working on the project",
        "I need to update my resume for the job",
        "We will resume work tomorrow",
        "The live stream starts at 8 PM",
        "Where do you live?",
        "I read the book yesterday",
        "I will read it tomorrow",
        "She's the lead developer",
        "Lead pipes are dangerous"
    ]
    
    print("🔧 Testing Proper Name & Word Pronunciation Processor")
    print("=" * 60)
    
    for text in test_cases:
        result = processor.process_proper_name_pronunciation(text)
        if result != text:
            print(f"✅ '{text}' → '{result}'")
        else:
            print(f"⚪ '{text}' (no changes)")
    
    # Analyze sample text
    sample_text = "Elon announced the acquisition of a company. Joy will resume work on the live project."
    analysis = processor.analyze_pronunciation_issues(sample_text)
    print(f"\n🔍 Analysis of: {sample_text}")
    print("=" * 40)
    print(f"Proper names: {analysis['proper_names_found']}")
    print(f"Words with fixes: {analysis['words_with_fixes']}")
    print(f"Context matches: {len(analysis['context_sensitive_matches'])}")
