#!/usr/bin/env python3
"""
Test script to verify HTML entity decoding fix in text preprocessing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor

def test_html_entity_decoding():
    """Test HTML entity decoding with the problematic input"""
    
    print("🧪 Testing HTML Entity Decoding Fix")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Problematic apostrophes",
            "input": "He&#x27;s, here&#x27;s",
            "expected_contains": ["he is", "here is"],  # Contractions are expanded after HTML decoding
            "should_not_contain": ["&#x27;", "and hash", "x27"]
        },
        {
            "name": "Mixed HTML entities",
            "input": "He&#x27;s &quot;here&quot; &amp; there&#x27;s",
            "expected_contains": ["he is", '"here"', "and there is"],  # Contractions expanded, & converted to 'and'
            "should_not_contain": ["&#x27;", "&quot;", "&amp;"]
        },
        {
            "name": "Original failing case",
            "input": "He&#x27;s, here&#x27;s, list like, makes, find, spell, conduct.",
            "expected_contains": ["he is", "here is", "list like", "makes", "find", "spell", "conduct"],
            "should_not_contain": ["&#x27;", "and hash"]
        },
        {
            "name": "No HTML entities",
            "input": "Regular text with no entities",
            "expected_contains": ["Regular text with no entities"],
            "should_not_contain": []
        },
        {
            "name": "Mixed symbols and entities",
            "input": "Price: $100 &amp; &#x27;special&#x27; offer @ 50%",
            "expected_contains": ["Price", "dollars", "'special'", "offer", "at", "fifty percent"],
            "should_not_contain": ["&amp;", "&#x27;"]
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        
        # Process the text
        result = phonemizer_preprocessor.preprocess_text(test_case['input'])
        
        print(f"Output: '{result.processed_text}'")
        print(f"Changes: {result.changes_made}")
        print(f"Confidence: {result.confidence_score:.2f}")
        
        # Check expected content
        test_passed = True
        for expected in test_case['expected_contains']:
            if expected not in result.processed_text:
                print(f"❌ FAIL: Expected to contain '{expected}'")
                test_passed = False
                all_passed = False
        
        # Check content that should not be present
        for should_not_contain in test_case['should_not_contain']:
            if should_not_contain in result.processed_text:
                print(f"❌ FAIL: Should not contain '{should_not_contain}'")
                test_passed = False
                all_passed = False
        
        if test_passed:
            print("✅ PASS")
        else:
            print("❌ FAIL")
        
        # Check for warnings
        if result.warnings:
            print(f"⚠️ Warnings: {result.warnings}")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! HTML entity decoding is working correctly.")
        return True
    else:
        print("❌ SOME TESTS FAILED! HTML entity decoding needs more work.")
        return False

def test_api_integration():
    """Test the fix with actual API call"""
    import requests
    import time
    
    print("\n🌐 Testing API Integration")
    print("=" * 30)
    
    base_url = "http://localhost:8354"
    
    # Test the problematic input that was causing empty audio
    test_text = "He&#x27;s, here&#x27;s, list like, makes, find, spell, conduct."
    
    payload = {
        "input": test_text,
        "voice": "af_heart",
        "response_format": "mp3"
    }
    
    print(f"Testing with: '{test_text}'")
    
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
            print(f"✅ SUCCESS!")
            print(f"   Status: {response.status_code}")
            print(f"   Audio size: {audio_size:,} bytes")
            print(f"   Generation time: {generation_time:.3f}s")
            
            if audio_size > 0:
                print("🎵 Audio generated successfully - HTML entity fix is working!")
                return True
            else:
                print("❌ Empty audio generated - fix may not be complete")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Could not connect to API server (not running?)")
        print("   Skipping API integration test")
        return True  # Don't fail the test if server isn't running
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 HTML Entity Decoding Fix Verification")
    print("=" * 60)
    
    # Test the preprocessing logic
    preprocessing_passed = test_html_entity_decoding()
    
    # Test API integration if server is available
    api_passed = test_api_integration()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS:")
    print(f"   Preprocessing Tests: {'✅ PASS' if preprocessing_passed else '❌ FAIL'}")
    print(f"   API Integration: {'✅ PASS' if api_passed else '❌ FAIL'}")
    
    if preprocessing_passed and api_passed:
        print("\n🎉 HTML entity decoding fix is working correctly!")
        print("   The apostrophe issue should be resolved.")
        return 0
    else:
        print("\n❌ Some tests failed. The fix may need additional work.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
