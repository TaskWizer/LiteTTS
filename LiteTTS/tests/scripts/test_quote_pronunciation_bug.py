#!/usr/bin/env python3
"""
Test script to investigate and fix quote character pronunciation bug
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
from LiteTTS.nlp.text_normalizer import TextNormalizer
from LiteTTS.nlp.processor import NLPProcessor
import requests
import time

def test_quote_preprocessing():
    """Test how quotes are handled in preprocessing"""
    
    print("🔍 Testing Quote Character Preprocessing")
    print("=" * 50)
    
    # Test cases for quote pronunciation bug
    test_cases = [
        {
            "name": "Simple quoted text",
            "input": '"Hello world"',
            "expected_behavior": "Quotes should be silent or handled as natural pauses"
        },
        {
            "name": "Mid-sentence quotes",
            "input": 'She said "yes" to the proposal',
            "expected_behavior": "Quotes should not be pronounced as 'in quat'"
        },
        {
            "name": "Quotes with following text",
            "input": '"quoted text" and more',
            "expected_behavior": "Quotes should be silent, not pronounced"
        },
        {
            "name": "Embedded quotes",
            "input": 'The word "example" here',
            "expected_behavior": "Quotes should be silent or natural pauses"
        },
        {
            "name": "Multiple quoted sections",
            "input": 'He said "hello" and she replied "goodbye"',
            "expected_behavior": "All quotes should be handled consistently"
        },
        {
            "name": "Single quotes",
            "input": "It's a 'special' case",
            "expected_behavior": "Single quotes should be handled differently from contractions"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        print(f"Expected: {test_case['expected_behavior']}")
        
        # Test phonemizer preprocessor
        result = phonemizer_preprocessor.preprocess_text(test_case['input'])
        print(f"Preprocessor Output: '{result.processed_text}'")
        print(f"Changes: {result.changes_made}")
        
        # Test text normalizer
        normalizer = TextNormalizer()
        normalized = normalizer.normalize_text(test_case['input'])
        print(f"Normalizer Output: '{normalized}'")
        
        # Test full NLP processor
        nlp_processor = NLPProcessor()
        processed = nlp_processor.process_text(test_case['input'])
        print(f"NLP Processor Output: '{processed}'")
        
        # Check for problematic patterns
        if '"' in result.processed_text:
            print("⚠️ WARNING: Double quotes still present in preprocessed text")
        
        if 'in quat' in result.processed_text.lower():
            print("❌ FAIL: Found 'in quat' pronunciation issue")
            all_passed = False
        elif 'quat' in result.processed_text.lower():
            print("❌ FAIL: Found 'quat' in output - potential pronunciation issue")
            all_passed = False
        else:
            print("✅ No obvious 'in quat' issue detected in preprocessing")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ No obvious quote pronunciation issues found in preprocessing")
    else:
        print("❌ Quote pronunciation issues detected")
    
    return all_passed

def test_api_quote_pronunciation():
    """Test quote pronunciation through the API"""
    
    print("\n🌐 Testing Quote Pronunciation via API")
    print("=" * 40)
    
    base_url = "http://localhost:8354"
    
    # Test cases that should reveal the quote pronunciation bug
    test_cases = [
        '"Hello world"',
        'She said "yes"',
        '"quoted text" and more',
        'The word "example" here'
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n🔍 API Test {i}: '{test_text}'")
        
        payload = {
            "input": test_text,
            "voice": "af_heart",
            "response_format": "mp3"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/v1/audio/speech",
                json=payload,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                audio_size = len(response.content)
                generation_time = end_time - start_time
                print(f"✅ SUCCESS: {audio_size:,} bytes in {generation_time:.3f}s")
                
                # Save audio for manual inspection
                filename = f"quote_test_{i}.mp3"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"   Audio saved as: {filename}")
                print("   🎧 Listen to check if quotes are pronounced as 'in quat'")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Response: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("⚠️ Could not connect to API server (not running?)")
            print("   Skipping API test")
            break
        except Exception as e:
            print(f"❌ API test failed: {e}")

def analyze_quote_handling():
    """Analyze how quotes are currently handled in the codebase"""
    
    print("\n🔬 Analyzing Quote Handling in Codebase")
    print("=" * 45)
    
    # Check HTML entity handling
    print("1. HTML Entity Handling:")
    test_html = '&quot;Hello&quot;'
    result = phonemizer_preprocessor.preprocess_text(test_html)
    print(f"   Input: '{test_html}'")
    print(f"   Output: '{result.processed_text}'")
    print(f"   Changes: {result.changes_made}")
    
    # Check symbol patterns in TextNormalizer
    print("\n2. Symbol Pattern Analysis:")
    normalizer = TextNormalizer()
    print("   Symbol patterns in TextNormalizer:")
    for pattern, replacement in normalizer.symbol_patterns:
        if '"' in pattern or 'quot' in pattern.lower():
            print(f"     Pattern: {pattern} -> {replacement}")
    
    # Check if quotes are handled in punctuation normalization
    print("\n3. Punctuation Normalization:")
    test_punct = '"Hello" and "world"'
    normalized = normalizer._normalize_punctuation(test_punct)
    print(f"   Input: '{test_punct}'")
    print(f"   After punctuation normalization: '{normalized}'")
    
    # Check if quotes are handled in whitespace cleanup
    print("\n4. Whitespace and Punctuation Cleanup:")
    cleaned = phonemizer_preprocessor._clean_whitespace_and_punctuation(test_punct)
    print(f"   Input: '{test_punct}'")
    print(f"   After cleanup: '{cleaned}'")

def test_quote_fix():
    """Test the implemented quote pronunciation fix"""

    print("\n🔧 Testing Quote Pronunciation Fix")
    print("=" * 40)

    # Test cases to verify the fix
    test_cases = [
        '"Hello world"',
        'She said "yes" to the proposal',
        '"quoted text" and more',
        'The word "example" here',
        'He said "hello" and she replied "goodbye"',
        '"First quote" then "second quote"'
    ]

    all_passed = True

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n🔍 Fix Test {i}: '{test_input}'")

        # Test with conservative mode (preserve_word_count=True)
        result = phonemizer_preprocessor.preprocess_text(test_input, preserve_word_count=True)
        print(f"Conservative Output: '{result.processed_text}'")
        print(f"Changes: {result.changes_made}")

        # Check if quotes were removed
        if '"' in result.processed_text or '"' in result.processed_text or '"' in result.processed_text:
            print("❌ FAIL: Quotes still present in output")
            all_passed = False
        else:
            print("✅ PASS: Quotes successfully removed")

        # Test with aggressive mode (preserve_word_count=False)
        result_aggressive = phonemizer_preprocessor.preprocess_text(test_input, preserve_word_count=False)
        print(f"Aggressive Output: '{result_aggressive.processed_text}'")

        if '"' in result_aggressive.processed_text or '"' in result_aggressive.processed_text or '"' in result_aggressive.processed_text:
            print("❌ FAIL: Quotes still present in aggressive mode")
            all_passed = False
        else:
            print("✅ PASS: Quotes successfully removed in aggressive mode")

    return all_passed

def main():
    """Run comprehensive quote pronunciation investigation and fix testing"""

    print("🔧 Quote Character Pronunciation Bug Investigation & Fix")
    print("=" * 65)
    print("Testing the implemented fix for 'in quat' pronunciation issue")
    print()

    # Test preprocessing behavior
    preprocessing_ok = test_quote_preprocessing()

    # Test the implemented fix
    fix_ok = test_quote_fix()

    # Analyze current quote handling
    analyze_quote_handling()

    # Test API behavior
    test_api_quote_pronunciation()

    print("\n" + "=" * 65)
    print("📊 FINAL RESULTS:")
    print(f"   Quote Fix Implementation: {'✅ PASS' if fix_ok else '❌ FAIL'}")
    print(f"   Preprocessing Tests: {'✅ PASS' if preprocessing_ok else '❌ FAIL'}")

    if fix_ok:
        print("\n🎉 Quote pronunciation fix implemented successfully!")
        print("   Quotes should now be silent instead of pronounced as 'in quat'")
    else:
        print("\n❌ Quote pronunciation fix needs more work")

    return 0 if fix_ok else 1

if __name__ == "__main__":
    sys.exit(main())
