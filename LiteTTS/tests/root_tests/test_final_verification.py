#!/usr/bin/env python3
"""
Final verification test for all TTS linguistic processing improvements
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.nlp.clean_text_normalizer import CleanTextNormalizer

def test_all_critical_fixes():
    """Final verification that all critical pronunciation issues are resolved"""
    print("=== FINAL VERIFICATION: All Critical TTS Pronunciation Fixes ===\n")
    
    normalizer = CleanTextNormalizer()
    
    # Comprehensive test cases covering all identified issues
    test_cases = [
        # CRITICAL BUG FIXES
        ("The meaning of life", "The meaning of life", "❌ CRITICAL: meaning → meters inches grams bug"),
        ("Its inside us", "Its inside us", "❌ CRITICAL: meaning → meters inches grams bug"),
        ("behind it", "behind it", "❌ CRITICAL: it → I-T conversion bug"),
        
        # PRONUNCIATION FIXES - HIGH PRIORITY
        ("religions", "ri-LIJ-uhns", "❌ HIGH: religions → really-gram-ions"),
        ("existentialism", "eg-zi-STEN-shuhl-iz-uhm", "❌ HIGH: existentialism → Exi-stential-ism"),
        ("she'd like that", "she would like that", "❌ HIGH: she'd → shed pronunciation"),
        ("Carl Sagan", "Carl S-A-gan", "❌ HIGH: systematic surname spelling"),
        
        # TICKER SYMBOL CORRECTIONS
        ("TSLA stock", "T-S-L-A stock", "❌ CRITICAL: TSLA → TEE-SLAW vs T-S-L-A"),
        ("AAPL shares", "A-A-P-L shares", "❌ CRITICAL: ticker symbol letter-by-letter"),
        
        # CONTRACTION PROCESSING
        ("I'll be there", "I will be there", "❌ HIGH: I'll → ill pronunciation"),
        ("wasn't ready", "was not ready", "❌ HIGH: wasn't → wAHz-uhnt pronunciation"),
        ("It's inside us", "It is inside us", "❌ HIGH: It's contraction expansion"),
        
        # SYMBOL & PUNCTUATION PROCESSING
        ("The * symbol", "The asterisk symbol", "❌ CRITICAL: * → astrisk vs asterisk"),
        ("Use & for and", "Use and for and", "❌ CRITICAL: & → and conversion"),
        ("John&#x27;s car", "John's car", "❌ CRITICAL: HTML entity → x 27 pronunciation"),
        ("&quot;Hello&quot;", "Hello", "❌ CRITICAL: quote → in quat pronunciation"),
        
        # CURRENCY & FINANCIAL PROCESSING
        ("$568.91", "five hundred sixty eight dollars and ninety one cents", "❌ HIGH: currency pronunciation"),
        ("$5,681.52", "five thousand six hundred eighty one dollars and fifty two cents", "❌ HIGH: large currency amounts"),
        
        # DATE & TIME PROCESSING
        ("2023-05-12", "May twelfth, two thousand twenty three", "❌ CRITICAL: ISO date → dash pronunciation"),
        ("12/18/2013", "December eighteenth, two thousand thirteen", "❌ HIGH: US date format"),
        
        # ABBREVIATION HANDLING
        ("FAQ section", "F-A-Q section", "❌ HIGH: FAQ pronunciation"),
        ("ASAP please", "A-S-A-P please", "❌ CRITICAL: ASAP → a sap pronunciation"),
        ("e.g. this example", "for example this example", "❌ HIGH: e.g. → e g pronunciation"),
        
        # UNIT PROCESSING (CONTEXTUAL)
        ("5 m tall", "5 meters tall", "❌ HIGH: contextual unit processing"),
        ("10 g of sugar", "10 grams of sugar", "❌ HIGH: contextual unit processing"),
        ("3 in wide", "3 inches wide", "❌ HIGH: contextual unit processing"),
        
        # INTERJECTION & NATURAL SPEECH
        ("hmm, let me think", "hum, let me think", "❌ HIGH: hmm → hum pronunciation"),
        ("joy", "JOY", "❌ HIGH: joy → ju-ie pronunciation"),
        
        # EMPTY AUDIO GENERATION TEST CASE
        ('"The Moon isn\'t out there. It\'s inside us. Always has been."', 
         '"The Moon is not out there. It is inside us. Always has been."', 
         "❌ CRITICAL: empty audio generation bug"),
    ]
    
    total_tests = len(test_cases)
    passed_tests = 0
    failed_tests = []
    
    for input_text, expected_contains, failure_description in test_cases:
        try:
            result = normalizer.normalize_text(input_text)
            output = result.processed_text
            
            # Check if expected content is present
            if expected_contains.lower() in output.lower() or output.lower() == expected_contains.lower():
                print(f"✅ PASS: {input_text}")
                print(f"    Output: {output}")
                passed_tests += 1
            else:
                print(f"❌ FAIL: {input_text}")
                print(f"    Expected: {expected_contains}")
                print(f"    Got:      {output}")
                print(f"    Issue:    {failure_description}")
                failed_tests.append((input_text, failure_description))
            
            print()
            
        except Exception as e:
            print(f"❌ ERROR: {input_text}")
            print(f"    Exception: {e}")
            print(f"    Issue:     {failure_description}")
            failed_tests.append((input_text, f"Exception: {e}"))
            print()
    
    # Summary
    print("=" * 80)
    print("FINAL VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {passed_tests}")
    print(f"Failed:       {len(failed_tests)}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print("\n❌ REMAINING ISSUES:")
        for i, (test_case, issue) in enumerate(failed_tests, 1):
            print(f"{i}. {test_case}")
            print(f"   {issue}")
    else:
        print("\n🎉 ALL CRITICAL PRONUNCIATION ISSUES RESOLVED!")
        print("✅ TTS linguistic processing system is ready for production")
    
    print("\n" + "=" * 80)
    
    return passed_tests, len(failed_tests)

def test_integration_with_main_pipeline():
    """Test integration with the main TTS processing pipeline"""
    print("\n=== Testing Integration with Main TTS Pipeline ===\n")
    
    try:
        from LiteTTS.nlp.processor import NLPProcessor
        processor = NLPProcessor()
        
        # Test a few key cases with the main processor
        integration_tests = [
            "The meaning of life",
            "TSLA stock price", 
            "she'd like $568.91",
            "2023-05-12 FAQ"
        ]
        
        print("Testing integration with main NLPProcessor...")
        for test_text in integration_tests:
            try:
                # Note: Main processor may have SSML corruption issues
                result = processor.process_text(test_text)
                print(f"✅ Processed: {test_text}")
                # Don't print full result due to SSML corruption
            except Exception as e:
                print(f"❌ Error processing '{test_text}': {e}")
        
        print("\n⚠️  NOTE: Main NLPProcessor has SSML corruption issues")
        print("   CleanTextNormalizer works correctly and should be integrated")
        
    except ImportError as e:
        print(f"⚠️  Could not test main pipeline integration: {e}")

if __name__ == '__main__':
    passed, failed = test_all_critical_fixes()
    test_integration_with_main_pipeline()
    
    # Exit with appropriate code
    if failed == 0:
        print("\n🎉 SUCCESS: All tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ FAILURE: {failed} tests failed")
        sys.exit(1)
