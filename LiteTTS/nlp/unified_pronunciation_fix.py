#!/usr/bin/env python3
"""
Unified pronunciation fix processor for TTS
Integrates all pronunciation fixes: comma handling, diphthongs, contractions, and interjections
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass

from .comma_fix_processor import comma_fix_processor
from .diphthong_fix_processor import diphthong_fix_processor
from .contraction_pronunciation_fix import contraction_pronunciation_fix
from .interjection_fix_processor import interjection_fix_processor

logger = logging.getLogger(__name__)

@dataclass
class PronunciationFixResult:
    """Result of pronunciation fix processing"""
    processed_text: str
    original_text: str
    fixes_applied: List[str]
    issues_found: Dict[str, Any]
    processing_time: float

class UnifiedPronunciationFix:
    """Unified processor for all pronunciation fixes"""
    
    def __init__(self):
        self.comma_processor = comma_fix_processor
        self.diphthong_processor = diphthong_fix_processor
        self.contraction_processor = contraction_pronunciation_fix
        self.interjection_processor = interjection_fix_processor
        
        # Configuration
        self.enable_comma_fixes = True
        self.enable_diphthong_fixes = True
        self.enable_contraction_fixes = True
        self.enable_interjection_fixes = True
        self.contraction_mode = "expand"  # "expand", "phonetic", or "hybrid"
        
    def process_pronunciation_fixes(self, text: str, 
                                  enable_comma: bool = None,
                                  enable_diphthong: bool = None,
                                  enable_contraction: bool = None,
                                  enable_interjection: bool = None,
                                  contraction_mode: str = None) -> PronunciationFixResult:
        """
        Apply all pronunciation fixes to text
        
        Args:
            text: Input text to process
            enable_comma: Override comma fix setting
            enable_diphthong: Override diphthong fix setting
            enable_contraction: Override contraction fix setting
            enable_interjection: Override interjection fix setting
            contraction_mode: Override contraction processing mode
        """
        import time
        start_time = time.time()
        
        original_text = text
        fixes_applied = []
        issues_found = {}
        
        logger.info(f"Starting unified pronunciation fixes for: {text[:100]}...")
        
        # Use provided settings or defaults
        comma_enabled = enable_comma if enable_comma is not None else self.enable_comma_fixes
        diphthong_enabled = enable_diphthong if enable_diphthong is not None else self.enable_diphthong_fixes
        contraction_enabled = enable_contraction if enable_contraction is not None else self.enable_contraction_fixes
        interjection_enabled = enable_interjection if enable_interjection is not None else self.enable_interjection_fixes
        c_mode = contraction_mode if contraction_mode is not None else self.contraction_mode
        
        # Step 1: Fix comma handling issues (highest priority)
        if comma_enabled:
            try:
                old_text = text
                text = self.comma_processor.fix_comma_pronunciation(text)
                if text != old_text:
                    fixes_applied.append("comma_fixes")
                    logger.debug("Applied comma pronunciation fixes")
                
                # Analyze comma issues
                comma_issues = self.comma_processor.analyze_comma_issues(text)
                if any(comma_issues.values()):
                    issues_found['comma_issues'] = comma_issues
                    
            except Exception as e:
                logger.error(f"Comma fix processing failed: {e}")
                fixes_applied.append("comma_fixes_failed")
        
        # Step 2: Fix diphthong pronunciation issues
        if diphthong_enabled:
            try:
                old_text = text
                text = self.diphthong_processor.fix_diphthong_pronunciation(text)
                if text != old_text:
                    fixes_applied.append("diphthong_fixes")
                    logger.debug("Applied diphthong pronunciation fixes")
                
                # Analyze diphthong issues
                diphthong_issues = self.diphthong_processor.analyze_diphthong_issues(text)
                if any(diphthong_issues.values()):
                    issues_found['diphthong_issues'] = diphthong_issues
                    
            except Exception as e:
                logger.error(f"Diphthong fix processing failed: {e}")
                fixes_applied.append("diphthong_fixes_failed")
        
        # Step 3: Fix contraction pronunciation issues
        if contraction_enabled:
            try:
                old_text = text
                # First normalize apostrophes
                text = self.contraction_processor.normalize_apostrophes(text)
                # Then apply contraction fixes
                text = self.contraction_processor.fix_contraction_pronunciation(text, mode=c_mode)
                if text != old_text:
                    fixes_applied.append(f"contraction_fixes_{c_mode}")
                    logger.debug(f"Applied contraction pronunciation fixes in {c_mode} mode")
                
                # Analyze contraction issues
                contraction_issues = self.contraction_processor.analyze_contraction_issues(text)
                if any(contraction_issues.values()):
                    issues_found['contraction_issues'] = contraction_issues
                    
            except Exception as e:
                logger.error(f"Contraction fix processing failed: {e}")
                fixes_applied.append("contraction_fixes_failed")
        
        # Step 4: Fix interjection pronunciation issues
        if interjection_enabled:
            try:
                old_text = text
                text = self.interjection_processor.fix_interjection_pronunciation(text)
                if text != old_text:
                    fixes_applied.append("interjection_fixes")
                    logger.debug("Applied interjection pronunciation fixes")
                
                # Analyze interjection issues
                interjection_issues = self.interjection_processor.analyze_interjection_issues(text)
                if any(interjection_issues.values()):
                    issues_found['interjection_issues'] = interjection_issues
                    
            except Exception as e:
                logger.error(f"Interjection fix processing failed: {e}")
                fixes_applied.append("interjection_fixes_failed")
        
        processing_time = time.time() - start_time
        
        result = PronunciationFixResult(
            processed_text=text,
            original_text=original_text,
            fixes_applied=fixes_applied,
            issues_found=issues_found,
            processing_time=processing_time
        )
        
        if text != original_text:
            logger.info(f"Pronunciation fixes completed: {len(fixes_applied)} fixes applied in {processing_time:.3f}s")
            logger.debug(f"Original: '{original_text}'")
            logger.debug(f"Fixed: '{text}'")
        else:
            logger.debug("No pronunciation fixes needed")
        
        return result
    
    def analyze_all_issues(self, text: str) -> Dict[str, Any]:
        """Analyze text for all types of pronunciation issues"""
        all_issues = {}
        
        try:
            all_issues['comma_issues'] = self.comma_processor.analyze_comma_issues(text)
        except Exception as e:
            logger.error(f"Comma analysis failed: {e}")
            all_issues['comma_issues'] = {'error': str(e)}
        
        try:
            all_issues['diphthong_issues'] = self.diphthong_processor.analyze_diphthong_issues(text)
        except Exception as e:
            logger.error(f"Diphthong analysis failed: {e}")
            all_issues['diphthong_issues'] = {'error': str(e)}
        
        try:
            all_issues['contraction_issues'] = self.contraction_processor.analyze_contraction_issues(text)
        except Exception as e:
            logger.error(f"Contraction analysis failed: {e}")
            all_issues['contraction_issues'] = {'error': str(e)}
        
        try:
            all_issues['interjection_issues'] = self.interjection_processor.analyze_interjection_issues(text)
        except Exception as e:
            logger.error(f"Interjection analysis failed: {e}")
            all_issues['interjection_issues'] = {'error': str(e)}
        
        return all_issues
    
    def configure_fixes(self, 
                       enable_comma: bool = True,
                       enable_diphthong: bool = True,
                       enable_contraction: bool = True,
                       enable_interjection: bool = True,
                       contraction_mode: str = "expand"):
        """Configure which fixes to apply"""
        self.enable_comma_fixes = enable_comma
        self.enable_diphthong_fixes = enable_diphthong
        self.enable_contraction_fixes = enable_contraction
        self.enable_interjection_fixes = enable_interjection
        self.contraction_mode = contraction_mode
        
        logger.info(f"Pronunciation fix configuration updated:")
        logger.info(f"  Comma fixes: {enable_comma}")
        logger.info(f"  Diphthong fixes: {enable_diphthong}")
        logger.info(f"  Contraction fixes: {enable_contraction} (mode: {contraction_mode})")
        logger.info(f"  Interjection fixes: {enable_interjection}")
    
    def get_fix_statistics(self, text: str) -> Dict[str, Any]:
        """Get statistics about potential fixes for text"""
        issues = self.analyze_all_issues(text)
        
        stats = {
            'total_words': len(text.split()),
            'total_characters': len(text),
            'potential_fixes': 0,
            'fix_categories': {}
        }
        
        for category, category_issues in issues.items():
            if isinstance(category_issues, dict) and 'error' not in category_issues:
                category_count = sum(len(v) if isinstance(v, list) else 1 for v in category_issues.values())
                stats['fix_categories'][category] = category_count
                stats['potential_fixes'] += category_count
        
        return stats

# Global instance for easy access
unified_pronunciation_fix = UnifiedPronunciationFix()
