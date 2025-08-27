#!/usr/bin/env python3
"""
Test script to investigate word truncation/phonetic mapping issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
from LiteTTS.nlp.processor import NLPProcessor
import requests
import time

def test_word_truncation():
    """Test words that are losing final consonants or getting incorrect phonetic mapping"""
    
    print("🔍 Testing Word Truncation/Phonetic Mapping Issues")
    print("=" * 55)
    
    # Test cases for word truncation/phonetic mapping bugs
    test_cases = [
        {
            "name": "Boy pronunciation",
            "input": "Boy",
            "expected_phonetic": "/bɔɪ/",
            "issue": "Should not be pronounced as 'bo'"
        },
        {
            "name": "June pronunciation", 
            "input": "June",
            "expected_phonetic": "/dʒuːn/",
            "issue": "Should not be pronounced as 'jaun'"
        },
        {
            "name": "Jan pronunciation",
            "input": "Jan",
            "expected_phonetic": "/dʒæn/",
            "issue": "Verify pronunciation accuracy"
        },
        {
            "name": "Similar short words - toy",
            "input": "toy",
            "expected_phonetic": "/tɔɪ/",
            "issue": "Should preserve final consonant sound"
        },
        {
            "name": "Similar short words - joy",
            "input": "joy",
            "expected_phonetic": "/dʒɔɪ/",
            "issue": "Should preserve final consonant sound"
        },
        {
            "name": "Similar short words - tune",
            "input": "tune",
            "expected_phonetic": "/tuːn/",
            "issue": "Should preserve final consonant"
        },
        {
            "name": "Similar short words - done",
            "input": "done",
            "expected_phonetic": "/dʌn/",
            "issue": "Should preserve final consonant"
        },
        {
            "name": "Boy in sentence",
            "input": "The boy is here",
            "expected_phonetic": "Boy should be /bɔɪ/",
            "issue": "Check if context affects pronunciation"
        },
        {
            "name": "June in sentence",
            "input": "June is coming",
            "expected_phonetic": "June should be /dʒuːn/",
            "issue": "Check if context affects pronunciation"
        },
        {
            "name": "Multiple problematic words",
            "input": "The boy and June",
            "expected_phonetic": "Both words should be correct",
            "issue": "Check multiple word handling"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        print(f"Expected: {test_case['expected_phonetic']}")
        print(f"Issue: {test_case['issue']}")
        
        # Test phonemizer preprocessor
        result = phonemizer_preprocessor.preprocess_text(test_case['input'])
        print(f"Preprocessor Output: '{result.processed_text}'")
        print(f"Changes: {result.changes_made}")
        
        # Test NLP processor
        nlp_processor = NLPProcessor()
        processed = nlp_processor.process_text(test_case['input'])
        print(f"NLP Processor Output: '{processed}'")
        
        # Check for potential issues
        input_words = test_case['input'].lower().split()
        output_words = processed.lower().split()
        
        # Check if any words were significantly altered
        for input_word in input_words:
            # Remove punctuation for comparison
            clean_input = input_word.strip('.,!?;:')
            found_similar = False
            
            for output_word in output_words:
                clean_output = output_word.strip('.,!?;:')
                # Check if the word is preserved or reasonably similar
                if clean_input == clean_output or clean_input in clean_output or clean_output in clean_input:
                    found_similar = True
                    break
            
            if not found_similar and clean_input not in ['the', 'is', 'and', 'a', 'an']:
                print(f"⚠️ WARNING: Word '{clean_input}' may have been significantly altered")
                all_passed = False
        
        # Check for specific known issues
        if 'boy' in test_case['input'].lower() and 'bo ' in processed.lower():
            print("❌ FAIL: 'Boy' truncated to 'bo'")
            all_passed = False
        elif 'boy' in test_case['input'].lower():
            print("✅ 'Boy' appears to be preserved")
            
        if 'june' in test_case['input'].lower() and 'jaun' in processed.lower():
            print("❌ FAIL: 'June' mispronounced as 'jaun'")
            all_passed = False
        elif 'june' in test_case['input'].lower():
            print("✅ 'June' appears to be preserved")
    
    print("\n" + "=" * 55)
    if all_passed:
        print("✅ No obvious word truncation issues found")
    else:
        print("❌ Word truncation/phonetic mapping issues detected")
    
    return all_passed

def test_consonant_clusters():
    """Test words with consonant clusters that might be problematic"""
    
    print("\n🔍 Testing Consonant Cluster Handling")
    print("=" * 40)
    
    # Test words with various consonant clusters
    test_words = [
        # Final consonant clusters
        "boy", "toy", "joy", "coy",  # -oy endings
        "tune", "June", "dune", "prune",  # -une endings  
        "done", "gone", "bone", "tone",  # -one endings
        "Jan", "can", "man", "plan",  # -an endings
        # Initial consonant clusters
        "blue", "true", "grew", "threw",  # bl-, tr-, gr-, thr-
        "play", "stay", "clay", "gray",  # pl-, st-, cl-, gr-
        # Complex clusters
        "strength", "through", "splash", "spring"
    ]
    
    issues_found = []
    
    for word in test_words:
        print(f"\n🔍 Testing: '{word}'")
        
        # Test processing
        result = phonemizer_preprocessor.preprocess_text(word)
        nlp_result = NLPProcessor().process_text(word)
        
        print(f"  Preprocessor: '{result.processed_text}'")
        print(f"  NLP: '{nlp_result}'")
        
        # Check if the word is preserved
        clean_input = word.lower().strip('.,!?;:')
        clean_output = nlp_result.lower().strip('.,!?;:')
        
        if clean_input != clean_output and clean_input not in clean_output:
            print(f"  ⚠️ Word changed: '{clean_input}' → '{clean_output}'")
            issues_found.append((word, clean_output))
        else:
            print(f"  ✅ Word preserved")
    
    if issues_found:
        print(f"\n❌ Found {len(issues_found)} consonant cluster issues:")
        for original, changed in issues_found:
            print(f"  '{original}' → '{changed}'")
    else:
        print("\n✅ No consonant cluster issues found")
    
    return len(issues_found) == 0

def test_api_word_pronunciation():
    """Test word pronunciation through the API"""
    
    print("\n🌐 Testing Word Pronunciation via API")
    print("=" * 40)
    
    base_url = "http://localhost:8354"
    
    # Test cases that should reveal word truncation issues
    test_cases = [
        "Boy",
        "June", 
        "Jan",
        "The boy is here",
        "June is coming"
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
                filename = f"word_test_{i}.mp3"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"   Audio saved as: {filename}")
                print("   🎧 Listen to check for word truncation issues")
                
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
    """Run comprehensive word truncation investigation"""
    
    print("🔧 Word Truncation/Phonetic Mapping Bug Investigation")
    print("=" * 60)
    print("Investigating word truncation and phonetic mapping issues")
    print()
    
    # Test word truncation behavior
    truncation_ok = test_word_truncation()
    
    # Test consonant cluster handling
    consonant_ok = test_consonant_clusters()
    
    # Test API behavior
    test_api_word_pronunciation()
    
    print("\n" + "=" * 60)
    print("📊 INVESTIGATION SUMMARY:")
    print(f"   Word Truncation Tests: {'✅ PASS' if truncation_ok else '❌ FAIL'}")
    print(f"   Consonant Cluster Tests: {'✅ PASS' if consonant_ok else '❌ FAIL'}")
    print("\nNext steps:")
    print("- Check generated audio files for pronunciation accuracy")
    print("- If words are truncated, investigate phonetic dictionary")
    print("- If consonant clusters are problematic, check phonemizer settings")
    print("- Consider adding pronunciation overrides for problematic words")
    
    return 0 if (truncation_ok and consonant_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
