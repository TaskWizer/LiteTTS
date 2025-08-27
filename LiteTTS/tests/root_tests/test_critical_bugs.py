#!/usr/bin/env python3
"""
Test critical pronunciation bugs identified through testing
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.nlp.processor import NLPProcessor
from LiteTTS.nlp.clean_text_normalizer import CleanTextNormalizer
from LiteTTS.nlp.advanced_abbreviation_handler import AdvancedAbbreviationHandler

def test_meaning_bug():
    """Test the critical 'meaning' → 'meters inches grams' bug"""
    print("=== Testing Critical 'meaning' → 'meters inches grams' Bug ===\n")
    
    # Test cases that should NOT be converted to units
    test_cases = [
        "The meaning of life",
        "Its inside us",
        "meaning something important",
        "The meaning behind it",
        "What is the meaning?",
        "meaning and purpose",
        "meaning in context",
        "meaning to say",
        "meaning well",
        "meaning business",
    ]
    
    # Test with different processors
    processors = {
        'NLPProcessor': NLPProcessor(),
        'CleanTextNormalizer': CleanTextNormalizer(),
        'AdvancedAbbreviationHandler': AdvancedAbbreviationHandler()
    }
    
    for processor_name, processor in processors.items():
        print(f"--- Testing {processor_name} ---")
        
        for test_text in test_cases:
            try:
                if processor_name == 'NLPProcessor':
                    result = processor.process_text(test_text)
                elif processor_name == 'CleanTextNormalizer':
                    result_obj = processor.normalize_text(test_text)
                    result = result_obj.processed_text
                elif processor_name == 'AdvancedAbbreviationHandler':
                    result = processor.process_abbreviations(test_text)
                
                print(f"Input:  {test_text}")
                print(f"Output: {result}")
                
                # Check for the bug
                if any(unit in result.lower() for unit in ['meters', 'inches', 'grams']):
                    print("❌ BUG DETECTED: Unit conversion in 'meaning'")
                else:
                    print("✅ OK: No unit conversion")
                
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ ERROR processing '{test_text}': {e}")
                print("-" * 50)
        
        print()

def test_unit_abbreviations_proper_context():
    """Test that unit abbreviations work correctly in proper contexts"""
    print("=== Testing Unit Abbreviations in Proper Context ===\n")
    
    # Test cases where unit conversion SHOULD happen
    proper_unit_cases = [
        "5 m tall",
        "10 g of sugar", 
        "3 in wide",
        "The distance is 100 m",
        "Weight: 50 g",
        "Length: 12 in",
        "Height: 2 m",
        "Mass: 500 g",
    ]
    
    # Test cases where unit conversion should NOT happen
    improper_unit_cases = [
        "meaning",
        "something", 
        "incoming",
        "program",
        "diagram",
        "telegram",
        "anagram",
        "Instagram",
    ]
    
    processor = AdvancedAbbreviationHandler()
    
    print("--- Cases where unit conversion SHOULD happen ---")
    for test_text in proper_unit_cases:
        try:
            result = processor.process_abbreviations(test_text)
            print(f"Input:  {test_text}")
            print(f"Output: {result}")
            
            if any(unit in result.lower() for unit in ['meters', 'inches', 'grams']):
                print("✅ CORRECT: Unit conversion applied")
            else:
                print("❌ MISSING: Unit conversion not applied")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            print("-" * 40)
    
    print("\n--- Cases where unit conversion should NOT happen ---")
    for test_text in improper_unit_cases:
        try:
            result = processor.process_abbreviations(test_text)
            print(f"Input:  {test_text}")
            print(f"Output: {result}")
            
            if any(unit in result.lower() for unit in ['meters', 'inches', 'grams']):
                print("❌ BUG: Incorrect unit conversion")
            else:
                print("✅ CORRECT: No unit conversion")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            print("-" * 40)

def test_other_critical_bugs():
    """Test other critical pronunciation issues"""
    print("\n=== Testing Other Critical Pronunciation Issues ===\n")
    
    normalizer = CleanTextNormalizer()
    
    critical_tests = [
        # Complex word pronunciations
        ("religions", "should not become 'really-gram-ions'"),
        ("existentialism", "should not become 'Exi-stential-ism'"),
        
        # Contraction processing
        ("she'd like that", "should become 'she would like that'"),
        
        # Proper name pronunciation
        ("Carl Sagan", "should become 'Carl S-A-gan'"),
        
        # Verify existing fixes
        ("joy", "should remain 'JOY'"),
        ("TSLA stock", "should become 'T-S-L-A stock'"),
        
        # Empty audio generation test case
        ('"The Moon isn\'t out there. It\'s inside us. Always has been."', "should process without errors"),
    ]
    
    for test_text, expected_behavior in critical_tests:
        try:
            result = normalizer.normalize_text(test_text)
            print(f"Input:     {test_text}")
            print(f"Output:    {result.processed_text}")
            print(f"Expected:  {expected_behavior}")
            print(f"Changes:   {result.changes_made}")
            print("-" * 60)
            
        except Exception as e:
            print(f"❌ ERROR processing '{test_text}': {e}")
            print("-" * 60)

if __name__ == '__main__':
    test_meaning_bug()
    test_unit_abbreviations_proper_context()
    test_other_critical_bugs()
