#!/usr/bin/env python3
"""
Comprehensive gap analysis for TTS pronunciation issues
Tests the current system against all identified pronunciation problems
"""

import sys
import os
import unittest
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import existing components
try:
    from LiteTTS.nlp.processor import NLPProcessor
    from LiteTTS.nlp.enhanced_nlp_processor import EnhancedNLPProcessor, EnhancedProcessingOptions
    from LiteTTS.nlp.enhanced_contraction_processor import EnhancedContractionProcessor
    from LiteTTS.nlp.advanced_symbol_processor import AdvancedSymbolProcessor
    from LiteTTS.nlp.extended_pronunciation_dictionary import ExtendedPronunciationDictionary
    from LiteTTS.nlp.enhanced_datetime_processor import EnhancedDateTimeProcessor
    from LiteTTS.nlp.advanced_abbreviation_handler import AdvancedAbbreviationHandler
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import components: {e}")
    COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class PronunciationGapAnalysis(unittest.TestCase):
    """Comprehensive analysis of pronunciation gaps in the current system"""
    
    def setUp(self):
        """Set up test components"""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Required components not available")
        
        # Initialize processors
        self.nlp_processor = NLPProcessor()
        self.enhanced_processor = EnhancedNLPProcessor()
        
        # Test cases from conversation history
        self.critical_issues = self._load_critical_test_cases()
        self.systematic_issues = self._load_systematic_test_cases()
        self.advanced_issues = self._load_advanced_test_cases()
    
    def _load_critical_test_cases(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Load critical pronunciation issues that need immediate fixing"""
        return {
            'contractions': [
                ("I wasn't ready", "I was not ready", "wasn't should expand to 'was not', not 'wAHz-uhnt'"),
                ("I'll be there", "I will be there", "I'll should expand to 'I will', not sound like 'ill'"),
                ("you'll see", "you will see", "you'll should expand to 'you will', not 'yaw-wl'"),
                ("I'd like that", "I would like that", "I'd should expand to 'I would', not 'I-D'"),
                ("I'm here", "I am here", "I'm should expand to 'I am', not sound like 'im'"),
                ("hi, that's great", "hi, that is great", "that's should not become 'hit that'"),
            ],
            'symbols_punctuation': [
                ("The * symbol", "The asterisk symbol", "* should be 'asterisk', not 'astrisk'"),
                ("Use & for and", "Use and for and", "& should be 'and'"),
                ("John's car", "John's car", "possessive 's should not become 's x27'"),
                ('"Hello world"', 'Hello world', 'quotation marks should not become "in quat"'),
                ("I'll go", "I will go", "apostrophe should not become 'x 27'"),
            ],
            'comma_processing': [
                ("Thinking, or maybe not", "Thinking, or maybe not", "should not become 'thinkinger'"),
                ("Yes, I agree", "Yes, I agree", "comma should create proper pause"),
                ("Hello, world", "Hello, world", "comma spacing should be natural"),
            ],
            'interjections': [
                ("Hmm, let me think", "Hum, let me think", "hmm should become 'hum' with proper duration"),
                ("Umm, I'm not sure", "Um, I'm not sure", "umm should be natural"),
                ("Ahh, I see", "Ah, I see", "ahh should be natural"),
            ]
        }
    
    def _load_systematic_test_cases(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Load systematic processing issues"""
        return {
            'currency': [
                ("$568.91", "five hundred sixty eight dollars and ninety one cents", "currency should be spelled out"),
                ("$5,681.52", "five thousand, six hundred eighty one dollars and fifty two cents", "large amounts with commas"),
                ("~$568.91", "approximately five hundred sixty eight dollars and ninety one cents", "approximate values"),
                ("€100.50", "one hundred euros and fifty cents", "euro currency"),
            ],
            'dates_times': [
                ("12/18/2013", "December eighteenth, two thousand thirteen", "slash format dates"),
                ("05/06/19", "May sixth, two thousand nineteen", "short year format"),
                ("2023-05-12", "May twelfth, two thousand twenty three", "ISO format should not say 'dash'"),
                ("November 21, 2025", "November twenty-first, two thousand twenty five", "ordinal dates"),
            ],
            'urls': [
                ("https://www.google.com", "W-W-W Google dot com", "protocol stripping"),
                ("https://www.somesite.com/somepage", "W-W-W some site dot com forward slash some page", "path handling"),
                ("www.example.org", "W-W-W example dot org", "simple URL"),
            ],
            'abbreviations': [
                ("FAQ section", "F-A-Q section", "FAQ should be spelled out"),
                ("ASAP please", "A-S-A-P please", "ASAP should not be 'a sap'"),
                ("Dr. Smith", "Doctor Smith", "Dr. should expand"),
                ("e.g. this example", "for example this example", "e.g. should be 'for example'"),
            ]
        }
    
    def _load_advanced_test_cases(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Load advanced feature test cases"""
        return {
            'context_aware': [
                ("Update my resume", "Update my resume", "resume should be 'REZ-oo-mey' (document)"),
                ("Resume the meeting", "Resume the meeting", "resume should be 're-ZOOM' (continue)"),
                ("TSLA stock", "Tesla stock", "TSLA should be 'Tesla' in stock context"),
                ("The acquisition", "The acquisition", "should be 'ak-wih-ZIH-shuhn'"),
                ("Elon Musk", "Elon Musk", "Elon should be 'EE-lahn'"),
            ],
            'emotional_prosodic': [
                ("What do you think?", "What do you think?", "should have question intonation"),
                ("That's amazing!", "That's amazing!", "should have exclamation emphasis"),
                ("(whispered) secret", "(whispered) secret", "parentheses should trigger voice modulation"),
                ("Inherently good", "Inherently good", "should end with proper /ɛnt/ sound"),
                ("Hedonism philosophy", "Hedonism philosophy", "should be /ˈhiːdənɪzəm/"),
            ]
        }
    
    def test_critical_contraction_issues(self):
        """Test critical contraction pronunciation issues"""
        print("\n=== Testing Critical Contraction Issues ===")
        
        for input_text, expected_output, description in self.critical_issues['contractions']:
            with self.subTest(input_text=input_text):
                # Test with basic processor
                basic_result = self.nlp_processor.process_text(input_text)
                
                # Test with enhanced processor
                enhanced_result = self.enhanced_processor.process_text_enhanced(input_text)
                enhanced_text = enhanced_result.processed_text if isinstance(enhanced_result, dict) else enhanced_result
                
                print(f"\nInput: {input_text}")
                print(f"Expected: {expected_output}")
                print(f"Basic: {basic_result}")
                print(f"Enhanced: {enhanced_text}")
                print(f"Issue: {description}")
                
                # Check if the issue is resolved
                if expected_output.lower() in enhanced_text.lower():
                    print("✅ FIXED")
                else:
                    print("❌ STILL BROKEN")
    
    def test_critical_symbol_issues(self):
        """Test critical symbol and punctuation issues"""
        print("\n=== Testing Critical Symbol & Punctuation Issues ===")
        
        for input_text, expected_output, description in self.critical_issues['symbols_punctuation']:
            with self.subTest(input_text=input_text):
                # Test with enhanced processor
                enhanced_result = self.enhanced_processor.process_text_enhanced(input_text)
                enhanced_text = enhanced_result.processed_text if isinstance(enhanced_result, dict) else enhanced_result
                
                print(f"\nInput: {input_text}")
                print(f"Expected: {expected_output}")
                print(f"Enhanced: {enhanced_text}")
                print(f"Issue: {description}")
                
                # Check for specific issues
                if 'x27' in enhanced_text or 'in quat' in enhanced_text.lower():
                    print("❌ SYMBOL ENCODING ISSUE DETECTED")
                elif expected_output.lower() in enhanced_text.lower():
                    print("✅ FIXED")
                else:
                    print("❌ STILL BROKEN")
    
    def test_systematic_currency_processing(self):
        """Test systematic currency processing"""
        print("\n=== Testing Currency Processing ===")
        
        for input_text, expected_output, description in self.systematic_issues['currency']:
            with self.subTest(input_text=input_text):
                enhanced_result = self.enhanced_processor.process_text_enhanced(input_text)
                enhanced_text = enhanced_result.processed_text if isinstance(enhanced_result, dict) else enhanced_result
                
                print(f"\nInput: {input_text}")
                print(f"Expected: {expected_output}")
                print(f"Enhanced: {enhanced_text}")
                print(f"Issue: {description}")
                
                # Check if currency is properly processed
                if any(word in enhanced_text.lower() for word in ['dollars', 'cents', 'euros']):
                    print("✅ CURRENCY PROCESSED")
                else:
                    print("❌ CURRENCY NOT PROCESSED")
    
    def test_systematic_date_processing(self):
        """Test systematic date and time processing"""
        print("\n=== Testing Date & Time Processing ===")
        
        for input_text, expected_output, description in self.systematic_issues['dates_times']:
            with self.subTest(input_text=input_text):
                enhanced_result = self.enhanced_processor.process_text_enhanced(input_text)
                enhanced_text = enhanced_result.processed_text if isinstance(enhanced_result, dict) else enhanced_result
                
                print(f"\nInput: {input_text}")
                print(f"Expected: {expected_output}")
                print(f"Enhanced: {enhanced_text}")
                print(f"Issue: {description}")
                
                # Check for dash issues in ISO dates
                if 'dash' in enhanced_text.lower() and '2023' in input_text:
                    print("❌ ISO DATE DASH ISSUE DETECTED")
                elif any(month in enhanced_text.lower() for month in ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']):
                    print("✅ DATE PROCESSED NATURALLY")
                else:
                    print("❌ DATE NOT PROCESSED")
    
    def test_advanced_context_awareness(self):
        """Test advanced context-aware processing"""
        print("\n=== Testing Context-Aware Processing ===")
        
        for input_text, expected_output, description in self.advanced_issues['context_aware']:
            with self.subTest(input_text=input_text):
                enhanced_result = self.enhanced_processor.process_text_enhanced(input_text)
                enhanced_text = enhanced_result.processed_text if isinstance(enhanced_result, dict) else enhanced_result
                
                print(f"\nInput: {input_text}")
                print(f"Expected: {expected_output}")
                print(f"Enhanced: {enhanced_text}")
                print(f"Issue: {description}")
                
                # Check for specific improvements
                if 'tesla' in enhanced_text.lower() and 'tsla' in input_text.lower():
                    print("✅ TICKER SYMBOL CONTEXT AWARE")
                elif 'ee-lahn' in enhanced_text.lower() and 'elon' in input_text.lower():
                    print("✅ PROPER NAME PRONUNCIATION")
                else:
                    print("❌ CONTEXT AWARENESS NEEDED")
    
    def generate_gap_analysis_report(self):
        """Generate a comprehensive gap analysis report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE GAP ANALYSIS REPORT")
        print("="*60)
        
        # This would be called after running all tests
        # For now, just print a summary structure
        print("\n1. CRITICAL ISSUES (Immediate Fix Required):")
        print("   - Contraction processing gaps")
        print("   - Symbol & punctuation encoding issues")
        print("   - Comma processing problems")
        
        print("\n2. SYSTEMATIC ISSUES (Enhancement Required):")
        print("   - Currency processing coverage")
        print("   - Date/time format handling")
        print("   - URL processing improvements")
        
        print("\n3. ADVANCED FEATURES (Future Enhancement):")
        print("   - Context-aware pronunciation")
        print("   - Emotional & prosodic enhancement")
        print("   - Voice modulation integration")

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Run the gap analysis
    unittest.main(verbosity=2)
