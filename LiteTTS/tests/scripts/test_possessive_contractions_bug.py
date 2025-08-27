#!/usr/bin/env python3
"""
Test script to investigate possessive contractions HTML entity issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
from LiteTTS.nlp.text_normalizer import TextNormalizer
from LiteTTS.nlp.processor import NLPProcessor
import requests
import time

def test_possessive_contractions():
    """Test how possessive contractions with HTML entities are handled"""
    
    print("🔍 Testing Possessive Contractions HTML Entity Issue")
    print("=" * 55)
    
    # Test cases for possessive contractions HTML entity bug
    test_cases = [
        {
            "name": "John's with HTML entity",
            "input": "John&#x27;s book",
            "expected_behavior": "Should be pronounced as 'Johns book', not 's and hash tag 27'"
        },
        {
            "name": "it's with HTML entity",
            "input": "it&#x27;s working",
            "expected_behavior": "Should be pronounced naturally, not 's and hash tag 27'"
        },
        {
            "name": "that's with HTML entity",
            "input": "that&#x27;s correct",
            "expected_behavior": "Should be pronounced naturally, not 's and hash tag 27'"
        },
        {
            "name": "what's with HTML entity",
            "input": "what&#x27;s happening",
            "expected_behavior": "Should preserve natural contraction pronunciation"
        },
        {
            "name": "Multiple possessives",
            "input": "John&#x27;s and Mary&#x27;s books",
            "expected_behavior": "Both possessives should be handled correctly"
        },
        {
            "name": "Mixed HTML entities",
            "input": "He&#x27;s got Mary&#x27;s book",
            "expected_behavior": "Both contractions should be handled correctly"
        },
        {
            "name": "Regular apostrophe (control)",
            "input": "John's book",
            "expected_behavior": "Should work correctly as baseline"
        },
        {
            "name": "Regular contraction (control)",
            "input": "it's working",
            "expected_behavior": "Should work correctly as baseline"
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
        
        # Test text normalizer (on preprocessed text)
        normalizer = TextNormalizer()
        normalized = normalizer.normalize_text(result.processed_text)
        print(f"Normalizer Output: '{normalized}'")
        
        # Test full NLP processor
        nlp_processor = NLPProcessor()
        processed = nlp_processor.process_text(test_case['input'])
        print(f"NLP Processor Output: '{processed}'")
        
        # Check for problematic patterns
        problematic_patterns = [
            'and hash',
            'hash tag',
            'x27',
            '&#x27;',
            's and hash',
            's x27'
        ]
        
        found_issues = []
        for pattern in problematic_patterns:
            if pattern in result.processed_text.lower():
                found_issues.append(pattern)
        
        if found_issues:
            print(f"❌ FAIL: Found problematic patterns: {found_issues}")
            all_passed = False
        else:
            print("✅ PASS: No problematic patterns detected")
        
        # Check if HTML entities were properly decoded
        if '&#x27;' in test_case['input'] and '&#x27;' not in result.processed_text:
            print("✅ HTML entity properly decoded")
        elif '&#x27;' in test_case['input'] and '&#x27;' in result.processed_text:
            print("❌ HTML entity not decoded")
            all_passed = False
    
    print("\n" + "=" * 55)
    if all_passed:
        print("✅ No possessive contraction issues found")
    else:
        print("❌ Possessive contraction issues detected")
    
    return all_passed

def test_html_entity_decoding_details():
    """Test HTML entity decoding in detail"""
    
    print("\n🔬 Detailed HTML Entity Decoding Analysis")
    print("=" * 45)
    
    # Test specific HTML entity patterns
    test_patterns = [
        "&#x27;",  # Hexadecimal apostrophe
        "&#39;",   # Decimal apostrophe
        "&apos;",  # Named apostrophe entity
    ]
    
    for pattern in test_patterns:
        test_input = f"John{pattern}s book"
        print(f"\n🔍 Testing pattern: {pattern}")
        print(f"Input: '{test_input}'")
        
        result = phonemizer_preprocessor.preprocess_text(test_input)
        print(f"Output: '{result.processed_text}'")
        print(f"Changes: {result.changes_made}")
        
        # Check if the entity was properly decoded
        if pattern not in result.processed_text:
            print("✅ HTML entity properly decoded")
        else:
            print("❌ HTML entity not decoded")

def test_contraction_handling_modes():
    """Test different contraction handling modes"""
    
    print("\n⚙️ Testing Contraction Handling Modes")
    print("=" * 40)
    
    test_input = "John&#x27;s book and it&#x27;s working"
    
    # Test conservative mode (preserve_word_count=True)
    print("\n📋 Conservative Mode (preserve_word_count=True):")
    result_conservative = phonemizer_preprocessor.preprocess_text(test_input, preserve_word_count=True)
    print(f"Input: '{test_input}'")
    print(f"Output: '{result_conservative.processed_text}'")
    print(f"Changes: {result_conservative.changes_made}")
    
    # Test aggressive mode (preserve_word_count=False)
    print("\n📋 Aggressive Mode (preserve_word_count=False):")
    result_aggressive = phonemizer_preprocessor.preprocess_text(test_input, preserve_word_count=False)
    print(f"Input: '{test_input}'")
    print(f"Output: '{result_aggressive.processed_text}'")
    print(f"Changes: {result_aggressive.changes_made}")

def test_api_possessive_contractions():
    """Test possessive contractions through the API"""
    
    print("\n🌐 Testing Possessive Contractions via API")
    print("=" * 45)
    
    base_url = "http://localhost:8354"
    
    # Test cases that should reveal the possessive contraction bug
    test_cases = [
        "John&#x27;s book",
        "it&#x27;s working",
        "that&#x27;s correct",
        "what&#x27;s happening"
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
                filename = f"possessive_test_{i}.mp3"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"   Audio saved as: {filename}")
                print("   🎧 Listen to check for 's and hash tag 27' pronunciation")
                
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

def main():
    """Run comprehensive possessive contractions investigation"""
    
    print("🔧 Possessive Contractions HTML Entity Bug Investigation")
    print("=" * 65)
    print("Investigating 's and hash tag 27' pronunciation issue")
    print()
    
    # Test possessive contractions behavior
    contractions_ok = test_possessive_contractions()
    
    # Test HTML entity decoding details
    test_html_entity_decoding_details()
    
    # Test different contraction handling modes
    test_contraction_handling_modes()
    
    # Test API behavior
    test_api_possessive_contractions()
    
    print("\n" + "=" * 65)
    print("📊 INVESTIGATION SUMMARY:")
    print("1. Check if HTML entities are being properly decoded")
    print("2. Verify contraction handling preserves natural speech")
    print("3. Listen to generated audio for 's and hash tag 27' issues")
    print("\nNext steps:")
    print("- If HTML entities aren't decoded, fix the decoding process")
    print("- If contractions are over-expanded, adjust contraction handling")
    print("- Ensure apostrophe normalization works correctly")
    
    return 0 if contractions_ok else 1

if __name__ == "__main__":
    sys.exit(main())
