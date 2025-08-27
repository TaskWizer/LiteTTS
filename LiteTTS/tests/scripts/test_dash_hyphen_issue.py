#!/usr/bin/env python3
"""
Test script to identify and validate the dash/hyphen verbalization issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
import requests
import time

def test_dash_hyphen_issue():
    """Test the dash/hyphen verbalization issue"""
    
    print("🔍 Dash/Hyphen Verbalization Issue Analysis")
    print("=" * 50)
    
    # Test cases that should NOT have hyphens converted to "dash"
    test_cases = [
        {
            "input": "twenty-one",
            "expected_behavior": "Should preserve hyphen for natural pronunciation",
            "should_not_contain": "dash"
        },
        {
            "input": "state-of-the-art",
            "expected_behavior": "Should preserve hyphens in compound adjectives",
            "should_not_contain": "dash"
        },
        {
            "input": "well-known",
            "expected_behavior": "Should preserve hyphen in compound words",
            "should_not_contain": "dash"
        },
        {
            "input": "co-author",
            "expected_behavior": "Should preserve hyphen in prefixed words",
            "should_not_contain": "dash"
        },
        {
            "input": "mother-in-law",
            "expected_behavior": "Should preserve hyphens in family terms",
            "should_not_contain": "dash"
        },
        {
            "input": "self-driving",
            "expected_behavior": "Should preserve hyphen in compound adjectives",
            "should_not_contain": "dash"
        },
        {
            "input": "real-time",
            "expected_behavior": "Should preserve hyphen in technical terms",
            "should_not_contain": "dash"
        },
        {
            "input": "user-friendly",
            "expected_behavior": "Should preserve hyphen in descriptive terms",
            "should_not_contain": "dash"
        }
    ]
    
    print("📋 Testing Current Behavior:")
    print("-" * 30)
    
    issues_found = []
    
    for i, test_case in enumerate(test_cases, 1):
        result = phonemizer_preprocessor.preprocess_text(test_case["input"])
        
        # Check if "dash" appears in the output
        contains_dash = "dash" in result.processed_text.lower()
        
        print(f"{i}. {test_case['expected_behavior']}")
        print(f"   Input:  '{test_case['input']}'")
        print(f"   Output: '{result.processed_text}'")
        
        if contains_dash:
            print(f"   ❌ ISSUE: Contains 'dash' - breaks natural speech")
            issues_found.append(test_case["input"])
        else:
            print(f"   ✅ OK: No 'dash' verbalization")
        
        # Show what changes were made
        pattern_changes = [change for change in result.changes_made if "problematic patterns" in change.lower() or "hyphenated" in change.lower()]
        if pattern_changes:
            print(f"   Changes: {pattern_changes}")
        
        print()
    
    return issues_found

def test_api_speech_quality():
    """Test API speech quality with hyphenated words"""
    
    print("🎵 API Speech Quality Test with Hyphens")
    print("=" * 40)
    
    base_url = "http://localhost:8354"
    
    test_cases = [
        "I need twenty-one items",
        "This is a state-of-the-art system",
        "She's a well-known author",
        "The co-author will join us"
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"{i}. Testing: '{test_text}'")
        
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
                timeout=15
            )
            end_time = time.time()
            
            if response.status_code == 200:
                audio_size = len(response.content)
                generation_time = end_time - start_time
                print(f"   ✅ SUCCESS: {audio_size:,} bytes in {generation_time:.3f}s")
                
                # Note: We can't automatically detect if "dash" is spoken,
                # but we can check the preprocessing
                from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
                result = phonemizer_preprocessor.preprocess_text(test_text)
                if "dash" in result.processed_text.lower():
                    print(f"   ⚠️ WARNING: Preprocessed text contains 'dash': '{result.processed_text}'")
                else:
                    print(f"   ✅ Preprocessed text looks good: '{result.processed_text}'")
                    
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ⚠️ API server not available")
            break
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print()

def analyze_problematic_patterns():
    """Analyze the problematic patterns that might be causing issues"""
    
    print("🔍 Analyzing Problematic Patterns")
    print("=" * 35)
    
    # Get the patterns from the preprocessor
    patterns = phonemizer_preprocessor.problematic_patterns
    
    print("Current problematic patterns:")
    for i, (pattern, replacement, description) in enumerate(patterns, 1):
        print(f"{i}. {description}")
        print(f"   Pattern: {pattern}")
        print(f"   Replacement: {replacement}")
        
        # Check if this pattern affects hyphens
        if "-" in pattern or "dash" in replacement:
            print(f"   ⚠️ AFFECTS HYPHENS - This may be causing the issue!")
        
        print()

def main():
    """Run comprehensive dash/hyphen issue analysis"""
    
    print("🔍 Comprehensive Dash/Hyphen Issue Analysis")
    print("=" * 55)
    print("Investigating why hyphens are being verbalized as 'dash'")
    print()
    
    # Analyze the problematic patterns
    analyze_problematic_patterns()
    
    # Test current behavior
    issues = test_dash_hyphen_issue()
    
    # Test API behavior
    test_api_speech_quality()
    
    # Summary
    print("=" * 55)
    print("🎯 ANALYSIS SUMMARY")
    print("=" * 55)
    
    if issues:
        print(f"❌ ISSUES FOUND: {len(issues)} test cases have dash verbalization")
        print("   Affected inputs:")
        for issue in issues:
            print(f"     - '{issue}'")
        print()
        print("🔧 RECOMMENDED FIX:")
        print("   Remove or modify the hyphenated words pattern in _build_problematic_patterns()")
        print("   Pattern: r'\\b(\\w+)-(\\w+)\\b' -> r'\\1 dash \\2'")
        print("   This pattern is converting natural hyphens to 'dash' words")
    else:
        print("✅ NO ISSUES FOUND: Hyphens are being handled correctly")
    
    print()
    print("📋 NEXT STEPS:")
    print("1. Fix the problematic pattern for hyphenated words")
    print("2. Test that compound words sound natural")
    print("3. Ensure no regression in other text processing")
    print("4. Validate with comprehensive benchmark")
    
    return len(issues)

if __name__ == "__main__":
    sys.exit(main())
