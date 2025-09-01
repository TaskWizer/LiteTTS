#!/usr/bin/env python3
"""
Investigation script for remaining pronunciation issues:
1. Quote characters occasionally pronounced as "in quat"
2. "Boy" pronounced as "boi" (missing final consonant)
"""

import sys
import os
import requests
import time
import json
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
from LiteTTS.nlp.processor import NLPProcessor

def test_quote_edge_cases():
    """Test edge cases for quote pronunciation that might still cause issues"""
    
    print("🔍 Testing Quote Edge Cases")
    print("=" * 30)
    
    # More comprehensive quote test cases
    edge_cases = [
        # Different quote types and contexts
        '"Hello world"',
        "'Hello world'",
        '"Hello" and "world"',
        'She said "Hello" loudly',
        'The "special" case',
        '"First" then "second" then "third"',
        # Mixed quote types
        'He said "I\'m fine" today',
        '"What\'s happening?" she asked',
        # Unicode quotes
        '"Hello" and "goodbye"',
        "'Hello' and 'goodbye'",
        # Quotes with punctuation
        '"Hello!"',
        '"What?"',
        '"Yes," she said.',
        # Empty quotes
        '""',
        "''",
        # Quotes with numbers
        '"123"',
        'Version "2.0"',
        # Quotes in different positions
        'Start "middle" end',
        '"Beginning of sentence',
        'End of sentence"',
    ]
    
    nlp_processor = NLPProcessor()
    issues_found = []
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n🔍 Test {i}: '{test_case}'")
        
        # Test text processing
        preprocessed = phonemizer_preprocessor.preprocess_text(test_case)
        nlp_result = nlp_processor.process_text(test_case)
        
        print(f"  Preprocessed: '{preprocessed.processed_text}'")
        print(f"  NLP Result: '{nlp_result}'")
        
        # Check for remaining quotes (but distinguish from contractions)
        quote_chars = ['"', '"', '"', "'", "'"]  # Removed ASCII ' from this list
        found_quotes = [q for q in quote_chars if q in nlp_result]

        # Check for ASCII single quotes that are NOT contractions
        import re
        # Find single quotes that are not part of contractions (letter + ' + letter)
        non_contraction_quotes = re.findall(r"(?<![a-zA-Z])'(?![a-zA-Z])|'(?=[^a-zA-Z])|(?<=[^a-zA-Z])'", nlp_result)

        if found_quotes or non_contraction_quotes:
            if non_contraction_quotes:
                print(f"  ⚠️ WARNING: Found non-contraction quotes: {non_contraction_quotes}")
            if found_quotes:
                print(f"  ⚠️ WARNING: Found Unicode quotes: {found_quotes}")
            issues_found.append({
                'input': test_case,
                'output': nlp_result,
                'quotes_found': found_quotes + non_contraction_quotes
            })
        else:
            print(f"  ✅ No problematic quotes in output")
    
    if issues_found:
        print(f"\n❌ Found {len(issues_found)} quote processing issues:")
        for issue in issues_found:
            print(f"  Input: '{issue['input']}'")
            print(f"  Output: '{issue['output']}'")
            print(f"  Quotes: {issue['quotes_found']}")
    else:
        print("\n✅ No quote processing issues found")
    
    return len(issues_found) == 0

def test_boy_pronunciation_contexts():
    """Test 'Boy' pronunciation in various contexts"""
    
    print("\n🔍 Testing 'Boy' Pronunciation Contexts")
    print("=" * 40)
    
    test_cases = [
        # Different contexts for "Boy"
        "Boy",
        "The boy",
        "A boy",
        "Boy and girl",
        "Good boy",
        "Boy, that's great!",
        "The boy is here",
        "I saw a boy",
        "Boy oh boy",
        # Similar words for comparison
        "Joy",
        "Toy", 
        "Coy",
        "Roy",
        "Soy",
        # Phonetically similar
        "Boil",
        "Void",
        "Point",
        # In sentences
        "The joy of the boy",
        "Boy with toy",
        "Roy the boy",
    ]
    
    nlp_processor = NLPProcessor()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: '{test_case}'")
        
        # Test text processing
        nlp_result = nlp_processor.process_text(test_case)
        print(f"  NLP Result: '{nlp_result}'")
        
        # Check if "Boy" is preserved correctly
        if 'boy' in test_case.lower():
            if 'boy' in nlp_result.lower():
                print(f"  ✅ 'Boy' preserved in text processing")
            else:
                print(f"  ❌ 'Boy' not found in output")
        
        # Check for any unexpected transformations
        original_words = test_case.lower().split()
        result_words = nlp_result.lower().split()
        
        for word in original_words:
            clean_word = word.strip('.,!?;:')
            if clean_word and not any(clean_word in result_word for result_word in result_words):
                print(f"  ⚠️ Word '{clean_word}' may have been altered")

def test_api_pronunciation_issues():
    """Test pronunciation issues through the API with actual audio generation"""
    
    print("\n🌐 Testing Pronunciation Issues via API")
    print("=" * 45)
    
    base_url = "http://localhost:8354"
    
    # Critical test cases
    test_cases = [
        {
            "name": "Quote pronunciation test",
            "input": '"Hello world" she said',
            "expected": "Should not contain 'in quat' pronunciation"
        },
        {
            "name": "Boy pronunciation test",
            "input": "The boy is here",
            "expected": "Should pronounce 'boy' with full /bɔɪ/ sound, not 'boi'"
        },
        {
            "name": "Multiple quotes test",
            "input": '"First" and "second" quotes',
            "expected": "No quote pronunciations"
        },
        {
            "name": "Boy in context test",
            "input": "Good boy, that's right",
            "expected": "Clear 'boy' pronunciation"
        },
        {
            "name": "Mixed pronunciation test",
            "input": 'The boy said "Hello" to everyone',
            "expected": "Both issues should be resolved"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 API Test {i}: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        print(f"Expected: {test_case['expected']}")
        
        payload = {
            "input": test_case['input'],
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
                filename = f"pronunciation_issue_test_{i}.mp3"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"   Audio saved as: {filename}")
                print(f"   🎧 MANUAL CHECK REQUIRED: Listen for pronunciation issues")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Response: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("⚠️ Could not connect to API server")
            print("   Please start the server with: uv run uvicorn app:app --host 0.0.0.0 --port 8354")
            return False
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
    
    print("\n📋 MANUAL VERIFICATION REQUIRED:")
    print("Please listen to the generated audio files and check for:")
    print("1. Any occurrence of 'in quat' when quotes should be silent")
    print("2. 'Boy' pronounced as 'boi' instead of full /bɔɪ/ sound")
    print("3. Report findings for further investigation")
    
    return True

def investigate_phonemizer_configuration():
    """Investigate phonemizer configuration that might affect pronunciation"""
    
    print("\n🔬 Investigating Phonemizer Configuration")
    print("=" * 45)
    
    # Check current phonemizer settings
    print("Current phonemizer preprocessor settings:")
    print(f"  Filter emojis: {phonemizer_preprocessor.filter_emojis}")
    print(f"  Emoji replacement: '{phonemizer_preprocessor.emoji_replacement}'")
    
    # Test phonemizer preprocessing with problematic cases
    test_cases = [
        '"Hello world"',
        'Boy',
        'The boy said "Hello"'
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: '{test_case}'")
        
        # Test both conservative and aggressive modes
        conservative_result = phonemizer_preprocessor.preprocess_text(test_case, preserve_word_count=True)
        aggressive_result = phonemizer_preprocessor.preprocess_text(test_case, preserve_word_count=False)
        
        print(f"  Conservative: '{conservative_result.processed_text}'")
        print(f"  Aggressive: '{aggressive_result.processed_text}'")
        print(f"  Conservative changes: {conservative_result.changes_made}")
        print(f"  Aggressive changes: {aggressive_result.changes_made}")

def check_different_processing_paths():
    """Check if different processing paths might cause inconsistent behavior"""
    
    print("\n🔍 Checking Different Processing Paths")
    print("=" * 40)
    
    test_input = '"Hello world" said the boy'
    
    print(f"Testing input: '{test_input}'")
    
    # Path 1: Direct NLP processor
    nlp_processor = NLPProcessor()
    nlp_result = nlp_processor.process_text(test_input)
    print(f"1. Direct NLP: '{nlp_result}'")
    
    # Path 2: Preprocessor then NLP
    preprocessed = phonemizer_preprocessor.preprocess_text(test_input)
    nlp_after_preprocess = nlp_processor.process_text(preprocessed.processed_text)
    print(f"2. Preprocess + NLP: '{nlp_after_preprocess}'")
    
    # Path 3: Check if there are any other processing components
    from LiteTTS.nlp.text_normalizer import TextNormalizer
    normalizer = TextNormalizer()
    normalized = normalizer.normalize_text(test_input)
    print(f"3. Direct normalizer: '{normalized}'")
    
    # Compare results
    if nlp_result == nlp_after_preprocess:
        print("✅ Processing paths are consistent")
    else:
        print("❌ Processing paths produce different results!")
        print(f"   Difference detected between direct NLP and preprocess+NLP")

def main():
    """Run comprehensive investigation of remaining pronunciation issues"""
    
    print("🔧 Investigating Remaining Pronunciation Issues")
    print("=" * 55)
    print("1. Quote characters occasionally pronounced as 'in quat'")
    print("2. 'Boy' pronounced as 'boi' (missing final consonant)")
    print()
    
    # Run investigations
    quotes_ok = test_quote_edge_cases()
    test_boy_pronunciation_contexts()
    investigate_phonemizer_configuration()
    check_different_processing_paths()
    api_ok = test_api_pronunciation_issues()
    
    print("\n" + "=" * 55)
    print("📊 INVESTIGATION SUMMARY:")
    print(f"   Quote Edge Cases: {'✅ PASS' if quotes_ok else '❌ ISSUES FOUND'}")
    print(f"   API Tests: {'✅ COMPLETED' if api_ok else '❌ FAILED'}")
    print("\n🎯 NEXT STEPS:")
    print("1. Listen to generated audio files for pronunciation verification")
    print("2. If issues persist, investigate phonemizer backend configuration")
    print("3. Consider phonetic dictionary overrides for problematic words")
    print("4. Check TTS model-specific pronunciation handling")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
