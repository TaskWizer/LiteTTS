#!/usr/bin/env python3
"""
Test comprehensive pronunciation fixes and critical bug resolutions
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.nlp.clean_text_normalizer import CleanTextNormalizer
from LiteTTS.nlp.advanced_abbreviation_handler import AdvancedAbbreviationHandler

def test_critical_bug_fixes():
    """Test that critical bugs have been resolved"""
    print("=== Testing Critical Bug Fixes ===\n")
    
    normalizer = CleanTextNormalizer()
    
    # Test cases for critical bugs
    critical_tests = [
        # 1. "meaning" bug - should NOT convert to units
        ("The meaning of life", "The meaning of life", "No unit conversion"),
        ("meaning something", "meaning something", "No unit conversion"),
        ("Its inside us", "Its inside us", "No unit conversion"),
        
        # 2. "it" → "I-T" bug - should remain "it"
        ("behind it", "behind it", "Should not become 'behind I-T'"),
        ("with it", "with it", "Should not become 'with I-T'"),
        ("about it", "about it", "Should not become 'about I-T'"),
        
        # 3. Complex word pronunciations
        ("religions", "ri-LIJ-uhns", "Should not become 'really-gram-ions'"),
        ("existentialism", "eg-zi-STEN-shuhl-iz-uhm", "Should not become 'Exi-stential-ism'"),
        
        # 4. Contraction processing improvements
        ("she'd like that", "she would like that", "Should expand correctly"),
        
        # 5. Proper name pronunciation
        ("Carl Sagan", "Carl S-A-gan", "Systematic surname spelling"),
        
        # 6. Verify existing fixes remain functional
        ("joy", "JOY", "Should remain 'JOY'"),
        ("TSLA stock", "T-S-L-A stock", "Ticker symbol fix"),
        ("hmm, let me think", "hum, let me think", "Interjection handling"),
        
        # 7. HTML entity fixes
        ("John&#x27;s car", "John's car", "HTML entity decoding"),
        ("&quot;Hello&quot;", "Hello", "Quote removal"),
        
        # 8. Empty audio generation test case
        ('"The Moon isn\'t out there. It\'s inside us."', 
         '"The Moon is not out there. It is inside us."', 
         "Should process without errors"),
    ]
    
    for input_text, expected_contains, description in critical_tests:
        try:
            result = normalizer.normalize_text(input_text)
            output = result.processed_text
            
            print(f"Input:       {input_text}")
            print(f"Output:      {output}")
            print(f"Expected:    {expected_contains}")
            print(f"Description: {description}")
            
            # Check if expected content is present
            if expected_contains.lower() in output.lower():
                print("✅ PASS")
            else:
                print("❌ FAIL")
            
            if result.changes_made:
                print(f"Changes:     {', '.join(result.changes_made)}")
            
            print("-" * 70)
            
        except Exception as e:
            print(f"❌ ERROR processing '{input_text}': {e}")
            print("-" * 70)

def test_unit_processing_improvements():
    """Test improved unit processing with contextual awareness"""
    print("\n=== Testing Unit Processing Improvements ===\n")
    
    handler = AdvancedAbbreviationHandler()
    
    # Test cases for unit processing
    unit_tests = [
        # Should process units in measurement contexts
        ("5 m tall", "5 meters tall", "Contextual unit processing"),
        ("10 g of sugar", "10 grams of sugar", "Contextual unit processing"),
        ("3 in wide", "3 inches wide", "Contextual unit processing"),
        ("Height: 2m", "Height: 2 meters", "No-space unit processing"),
        ("Weight: 50g", "Weight: 50 grams", "No-space unit processing"),
        ("Length: 12in", "Length: 12 inches", "No-space unit processing"),
        
        # Should NOT process units in non-measurement contexts
        ("meaning", "meaning", "No false unit conversion"),
        ("something", "something", "No false unit conversion"),
        ("incoming", "incoming", "No false unit conversion"),
        ("program", "program", "No false unit conversion"),
        ("diagram", "diagram", "No false unit conversion"),
        ("Instagram", "Instagram", "No false unit conversion"),
        
        # Edge cases
        ("The meaning is 5 m", "The meaning is 5 meters", "Mixed context"),
        ("programming in Python", "programming in Python", "Should not convert 'in'"),
    ]
    
    for input_text, expected, description in unit_tests:
        try:
            result = handler.process_abbreviations(input_text)
            
            print(f"Input:       {input_text}")
            print(f"Output:      {result}")
            print(f"Expected:    {expected}")
            print(f"Description: {description}")
            
            if expected.lower() == result.lower():
                print("✅ PASS")
            else:
                print("❌ FAIL")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ ERROR processing '{input_text}': {e}")
            print("-" * 50)

def test_pronunciation_dictionary_additions():
    """Test new pronunciation dictionary additions"""
    print("\n=== Testing Pronunciation Dictionary Additions ===\n")
    
    normalizer = CleanTextNormalizer()
    
    # Test new pronunciation fixes
    pronunciation_tests = [
        ("religions", "ri-LIJ-uhns"),
        ("existentialism", "eg-zi-STEN-shuhl-iz-uhm"),
        ("Carl Sagan", "Carl S-A-gan"),
        ("philosophy", "fi-LOS-uh-fee"),
        ("psychology", "sy-KOL-uh-jee"),
        ("sociology", "so-see-OL-uh-jee"),
        ("anthropology", "an-thruh-POL-uh-jee"),
    ]
    
    for input_text, expected_pronunciation in pronunciation_tests:
        try:
            result = normalizer.normalize_text(input_text)
            output = result.processed_text
            
            print(f"Input:  {input_text}")
            print(f"Output: {output}")
            print(f"Expected: {expected_pronunciation}")
            
            if expected_pronunciation.lower() in output.lower():
                print("✅ PASS - Pronunciation applied")
            else:
                print("❌ FAIL - Pronunciation not applied")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            print("-" * 40)

def test_regression_prevention():
    """Test that previous fixes remain functional"""
    print("\n=== Testing Regression Prevention ===\n")
    
    normalizer = CleanTextNormalizer()
    
    # Regression tests for previously fixed issues
    regression_tests = [
        # Ticker symbols
        ("TSLA stock", "T-S-L-A stock"),
        ("AAPL shares", "A-A-P-L shares"),
        
        # Contractions
        ("I'll be there", "I will be there"),
        ("wasn't ready", "was not ready"),
        ("you'll see", "you will see"),
        
        # Currency
        ("$568.91", "five hundred sixty eight dollars and ninety one cents"),
        ("$5,681.52", "five thousand six hundred eighty one dollars and fifty two cents"),
        
        # Dates
        ("2023-05-12", "May twelfth, two thousand twenty three"),
        
        # Symbols
        ("Use & for and", "Use and for and"),
        ("The * symbol", "The asterisk symbol"),
        
        # Abbreviations
        ("FAQ section", "F-A-Q section"),
        ("ASAP please", "A-S-A-P please"),
        ("e.g. this example", "for example this example"),
        
        # Pronunciations
        ("joy", "JOY"),
        ("hmm, let me think", "hum, let me think"),
    ]
    
    for input_text, expected_contains in regression_tests:
        try:
            result = normalizer.normalize_text(input_text)
            output = result.processed_text
            
            print(f"Input:  {input_text}")
            print(f"Output: {output}")
            
            if expected_contains.lower() in output.lower():
                print("✅ REGRESSION TEST PASS")
            else:
                print("❌ REGRESSION DETECTED")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            print("-" * 50)

if __name__ == '__main__':
    test_critical_bug_fixes()
    test_unit_processing_improvements()
    test_pronunciation_dictionary_additions()
    test_regression_prevention()
