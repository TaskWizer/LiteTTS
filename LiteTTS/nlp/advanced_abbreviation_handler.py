#!/usr/bin/env python3
"""
Advanced abbreviation handler for TTS
Fixes ASAP pronunciation and implements configurable abbreviation processing
"""

import re
from typing import Dict, List, Tuple, Optional, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AbbreviationMode(Enum):
    """Abbreviation processing modes"""
    SPELL_OUT = "spell_out"  # A-S-A-P
    EXPAND = "expand"        # As soon as possible
    NATURAL = "natural"      # Context-dependent choice
    HYBRID = "hybrid"        # Mix of spell-out and expansion based on common usage

class AdvancedAbbreviationHandler:
    """Advanced abbreviation processing for natural TTS pronunciation"""
    
    def __init__(self):
        self.spell_out_abbreviations = self._load_spell_out_abbreviations()
        self.expansion_abbreviations = self._load_expansion_abbreviations()
        self.context_abbreviations = self._load_context_abbreviations()
        self.natural_abbreviations = self._load_natural_abbreviations()
        
        # Configuration
        self.default_mode = AbbreviationMode.HYBRID
        self.use_context_analysis = True
        self.preserve_technical_terms = True
        
    def _load_spell_out_abbreviations(self) -> Dict[str, str]:
        """Load abbreviations that should be spelled out"""
        return {
            # Common acronyms that are typically spelled out
            'ASAP': 'A S A P',  # Not "a sap"
            'FAQ': 'F A Q',
            'CEO': 'C E O',
            'CFO': 'C F O',
            'CTO': 'C T O',
            'COO': 'C O O',
            'HR': 'H R',
            'IT': 'I T',
            'AI': 'A I',
            'API': 'A P I',
            'URL': 'U R L',
            'HTML': 'H T M L',
            'CSS': 'C S S',
            'SQL': 'S Q L',
            'XML': 'X M L',
            'JSON': 'J S O N',
            'HTTP': 'H T T P',
            'HTTPS': 'H T T P S',
            'FTP': 'F T P',
            'SSH': 'S S H',
            'VPN': 'V P N',
            'DNS': 'D N S',
            'IP': 'I P',
            'TCP': 'T C P',
            'UDP': 'U D P',
            'USB': 'U S B',
            'CPU': 'C P U',
            'GPU': 'G P U',
            'RAM': 'R A M',
            'ROM': 'R O M',
            'SSD': 'S S D',
            'HDD': 'H D D',
            'DVD': 'D V D',
            'CD': 'C D',
            'TV': 'T V',
            'PC': 'P C',
            'OS': 'O S',
            'UI': 'U I',
            'UX': 'U X',
            'PDF': 'P D F',
            'JPG': 'J P G',
            'JPEG': 'J P E G',
            'PNG': 'P N G',
            'GIF': 'G I F',
            'MP3': 'M P three',
            'MP4': 'M P four',
            'AVI': 'A V I',
            'MOV': 'M O V',
            'ZIP': 'Z I P',
            'RAR': 'R A R',
            'EXE': 'E X E',
            'DLL': 'D L L',
            
            # Business and finance
            'LLC': 'L L C',
            'Inc': 'I N C',
            'Corp': 'C O R P',
            'Ltd': 'L T D',
            'IPO': 'I P O',
            'ROI': 'R O I',
            'KPI': 'K P I',
            'B2B': 'B two B',
            'B2C': 'B two C',
            'SaaS': 'S A A S',
            'CRM': 'C R M',
            'ERP': 'E R P',
            
            # Medical and scientific
            'DNA': 'D N A',
            'RNA': 'R N A',
            'MRI': 'M R I',
            'CT': 'C T',
            'EKG': 'E K G',
            'ECG': 'E C G',
            'IV': 'I V',
            'ER': 'E R',
            'ICU': 'I C U',
            'CDC': 'C D C',
            'FDA': 'F D A',
            'WHO': 'W H O',
            
            # Government and organizations
            'FBI': 'F B I',
            'CIA': 'C I A',
            'NASA': 'N A S A',
            'CEO': 'C E O',
            'TSLA': 'T S L A',  # Tesla stock ticker
            'NSA': 'N S A',
            'IRS': 'I R S',
            'DMV': 'D M V',
            'DOT': 'D O T',
            'EPA': 'E P A',
            'OSHA': 'O S H A',
            'UN': 'U N',
            'EU': 'E U',
            'NATO': 'N A T O',
            'UNICEF': 'U N I C E F',
        }
    
    def _load_expansion_abbreviations(self) -> Dict[str, str]:
        """Load abbreviations that should be expanded"""
        return {
            # Common abbreviations that sound better when expanded
            'ASAP': 'as soon as possible',  # Alternative to spelling out
            'FYI': 'for your information',
            'BTW': 'by the way',
            'IMO': 'in my opinion',
            'IMHO': 'in my humble opinion',
            'TBH': 'to be honest',
            'AFAIK': 'as far as I know',
            'IIRC': 'if I recall correctly',
            'YMMV': 'your mileage may vary',
            'RTFM': 'read the manual',
            'DIY': 'do it yourself',
            'FAQ': 'frequently asked questions',  # Alternative to spelling out
            
            # Time and dates
            'AM': 'A M',  # Keep as letters for time
            'PM': 'P M',  # Keep as letters for time
            'EST': 'Eastern Standard Time',
            'PST': 'Pacific Standard Time',
            'GMT': 'Greenwich Mean Time',
            'UTC': 'Coordinated Universal Time',
            
            # Titles and honorifics
            'Dr.': 'Doctor',
            'Mr.': 'Mister',
            'Mrs.': 'Missus',
            'Ms.': 'Miss',
            'Prof.': 'Professor',
            'Rev.': 'Reverend',
            'Gen.': 'General',
            'Col.': 'Colonel',
            'Capt.': 'Captain',
            'Lt.': 'Lieutenant',
            'Sgt.': 'Sergeant',
            
            # Common Latin abbreviations
            'etc.': 'etcetera',
            'vs.': 'versus',
            'e.g.': 'for example',
            'i.e.': 'that is',
            'cf.': 'compare',
            'et al.': 'and others',
            'viz.': 'namely',
            'ibid.': 'in the same place',
            'op. cit.': 'in the work cited',
            'loc. cit.': 'in the place cited',
            
            # Units and measurements - CAREFUL with single letters to avoid false matches
            'ft.': 'feet',
            'in.': 'inches',
            'yd.': 'yards',
            'mi.': 'miles',
            'lb.': 'pounds',
            'oz.': 'ounces',
            'kg': 'kilograms',
            # 'g': 'grams',  # DISABLED: Too aggressive, causes false matches in words like "meaning"
            'mg': 'milligrams',
            'km': 'kilometers',
            # 'm': 'meters',  # DISABLED: Too aggressive, causes false matches in words like "meaning"
            'cm': 'centimeters',
            'mm': 'millimeters',
            'L': 'liters',
            'ml': 'milliliters',
            'mph': 'miles per hour',
            'kph': 'kilometers per hour',
            'rpm': 'revolutions per minute',
            'psi': 'pounds per square inch',
            'dpi': 'dots per inch',
            'fps': 'frames per second',
            'bps': 'bits per second',
            'kbps': 'kilobits per second',
            'mbps': 'megabits per second',
            'gbps': 'gigabits per second',
            
            # Common abbreviations
            'w/': 'with',
            'w/o': 'without',
            'b/c': 'because',
            'b/w': 'between',
            'aka': 'also known as',
            'a.k.a.': 'also known as',
            'approx.': 'approximately',
            'max.': 'maximum',
            'min.': 'minimum',
            'avg.': 'average',
            'temp.': 'temperature',
            'dept.': 'department',
            'govt.': 'government',
            'intl.': 'international',
            'natl.': 'national',
            'assoc.': 'association',
            'corp.': 'corporation',
            'inc.': 'incorporated',
            'ltd.': 'limited',
            'co.': 'company',
        }
    
    def _load_context_abbreviations(self) -> Dict[str, Dict[str, str]]:
        """Load context-dependent abbreviations"""
        return {
            'US': {
                'country': 'United States',
                'pronoun': 'us',
            },
            'IT': {
                'technology': 'I T',
                'pronoun': 'it',
            },
            'AI': {
                'technology': 'A I',
                'name': 'Ai',  # Japanese name
            },
            'TV': {
                'device': 'T V',
                'abbreviation': 'television',
            },
            'PC': {
                'computer': 'P C',
                'abbreviation': 'personal computer',
            },
        }
    
    def _load_natural_abbreviations(self) -> Dict[str, str]:
        """Load abbreviations that are naturally pronounced as words"""
        return {
            # Abbreviations that are pronounced as words, not spelled out
            'NASA': 'NASA',
            'LASER': 'laser',
            'RADAR': 'radar',
            'SCUBA': 'scuba',
            'AWOL': 'AWOL',
            'JPEG': 'jay-peg',  # Alternative pronunciation
            'GIF': 'gif',       # Alternative pronunciation
            'WIFI': 'wifi',
            'BLUETOOTH': 'bluetooth',
            'ETHERNET': 'ethernet',
        }
    
    def process_abbreviations(self, text: str, mode: Optional[AbbreviationMode] = None) -> str:
        """Process abbreviations based on the specified mode"""
        if mode is None:
            mode = self.default_mode
        
        logger.debug(f"Processing abbreviations in {mode.value} mode: {text[:100]}...")
        
        if mode == AbbreviationMode.SPELL_OUT:
            text = self._process_spell_out_mode(text)
        elif mode == AbbreviationMode.EXPAND:
            text = self._process_expansion_mode(text)
        elif mode == AbbreviationMode.NATURAL:
            text = self._process_natural_mode(text)
        elif mode == AbbreviationMode.HYBRID:
            text = self._process_hybrid_mode(text)
        
        logger.debug(f"Abbreviation processing result: {text[:100]}...")
        return text
    
    def _process_spell_out_mode(self, text: str) -> str:
        """Process abbreviations by spelling them out"""
        for abbrev, spelled_out in self.spell_out_abbreviations.items():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            text = re.sub(pattern, spelled_out, text, flags=re.IGNORECASE)
        return text
    
    def _process_expansion_mode(self, text: str) -> str:
        """Process abbreviations by expanding them"""
        for abbrev, expansion in self.expansion_abbreviations.items():
            if abbrev.endswith('.'):
                # Handle abbreviations with periods
                pattern = r'(?<!\w)' + re.escape(abbrev) + r'(?!\w)'
            else:
                pattern = r'\b' + re.escape(abbrev) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
        return text
    
    def _process_natural_mode(self, text: str) -> str:
        """Process abbreviations using natural pronunciations"""
        for abbrev, natural in self.natural_abbreviations.items():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            text = re.sub(pattern, natural, text, flags=re.IGNORECASE)
        return text
    
    def _process_hybrid_mode(self, text: str) -> str:
        """Process abbreviations using a hybrid approach"""
        # Priority order: natural > spell_out > expansion > contextual units

        # First, apply natural pronunciations
        for abbrev, natural in self.natural_abbreviations.items():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            text = re.sub(pattern, natural, text, flags=re.IGNORECASE)

        # Then, apply spell-out for technical terms
        for abbrev, spelled_out in self.spell_out_abbreviations.items():
            if abbrev not in self.natural_abbreviations:
                pattern = r'\b' + re.escape(abbrev) + r'\b'
                text = re.sub(pattern, spelled_out, text, flags=re.IGNORECASE)

        # Process contextual units (single letters in measurement contexts)
        text = self._process_contextual_units(text)
        
        # Finally, apply expansions for remaining abbreviations
        for abbrev, expansion in self.expansion_abbreviations.items():
            if abbrev not in self.natural_abbreviations and abbrev not in self.spell_out_abbreviations:
                if abbrev.endswith('.'):
                    pattern = r'(?<!\w)' + re.escape(abbrev) + r'(?!\w)'
                else:
                    pattern = r'\b' + re.escape(abbrev) + r'\b'
                text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
        
        return text
    
    def _get_context_pronunciation(self, abbrev: str, context: str) -> Optional[str]:
        """Get context-dependent pronunciation"""
        if abbrev not in self.context_abbreviations:
            return None
        
        context_options = self.context_abbreviations[abbrev]
        
        # Simple context analysis (could be enhanced with ML)
        context_lower = context.lower()
        
        for context_key, pronunciation in context_options.items():
            if context_key in context_lower:
                return pronunciation
        
        # Return first option if no context match
        return list(context_options.values())[0]
    
    def analyze_abbreviations(self, text: str) -> Dict[str, List[str]]:
        """Analyze abbreviations in text"""
        info = {
            'spell_out_candidates': [],
            'expansion_candidates': [],
            'natural_candidates': [],
            'context_dependent': [],
            'unknown_abbreviations': []
        }
        
        # Find potential abbreviations (all caps words)
        abbreviations = re.findall(r'\b[A-Z]{2,}\b', text)
        
        for abbrev in abbreviations:
            if abbrev in self.spell_out_abbreviations:
                info['spell_out_candidates'].append(abbrev)
            elif abbrev in self.expansion_abbreviations:
                info['expansion_candidates'].append(abbrev)
            elif abbrev in self.natural_abbreviations:
                info['natural_candidates'].append(abbrev)
            elif abbrev in self.context_abbreviations:
                info['context_dependent'].append(abbrev)
            else:
                info['unknown_abbreviations'].append(abbrev)
        
        return info
    
    def add_abbreviation(self, abbrev: str, pronunciation: str, mode: AbbreviationMode):
        """Add a new abbreviation to the appropriate dictionary"""
        if mode == AbbreviationMode.SPELL_OUT:
            self.spell_out_abbreviations[abbrev] = pronunciation
        elif mode == AbbreviationMode.EXPAND:
            self.expansion_abbreviations[abbrev] = pronunciation
        elif mode == AbbreviationMode.NATURAL:
            self.natural_abbreviations[abbrev] = pronunciation
        
        logger.info(f"Added abbreviation: {abbrev} -> {pronunciation} ({mode.value})")
    
    def set_configuration(self, default_mode: AbbreviationMode = None,
                         use_context_analysis: bool = None,
                         preserve_technical_terms: bool = None):
        """Set configuration options"""
        if default_mode is not None:
            self.default_mode = default_mode
        if use_context_analysis is not None:
            self.use_context_analysis = use_context_analysis
        if preserve_technical_terms is not None:
            self.preserve_technical_terms = preserve_technical_terms
        
        logger.info(f"Abbreviation handler configuration updated: "
                   f"default_mode={self.default_mode.value}, "
                   f"use_context_analysis={self.use_context_analysis}, "
                   f"preserve_technical_terms={self.preserve_technical_terms}")
    
    def _process_contextual_units(self, text: str) -> str:
        """Process single-letter units only in proper measurement contexts"""
        # Define unit patterns that should only be processed in measurement contexts
        contextual_units = {
            'm': 'meters',
            'g': 'grams',
            'in': 'inches'
        }

        # Pattern to match numbers followed by units
        # This ensures we only process units that follow numbers
        for unit, expansion in contextual_units.items():
            # Match: number + space + unit + word boundary
            # Examples: "5 m tall", "10 g of", "3 in wide"
            pattern = r'(\d+(?:\.\d+)?)\s+' + re.escape(unit) + r'\b'
            replacement = r'\1 ' + expansion
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

            # Also match: number + unit (no space)
            # Examples: "5m", "10g", "3in"
            pattern = r'(\d+(?:\.\d+)?)' + re.escape(unit) + r'\b'
            replacement = r'\1 ' + expansion
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def get_supported_modes(self) -> List[str]:
        """Get list of supported abbreviation processing modes"""
        return [mode.value for mode in AbbreviationMode]
