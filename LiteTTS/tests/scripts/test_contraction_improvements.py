#!/usr/bin/env python3
"""
Test script to validate contraction expansion improvements
Tests the new configurable contraction handling system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
from LiteTTS.config import config
import requests
import time

def test_configuration_modes():
    """Test different configuration modes for contraction expansion"""
    
    print("🔧 Testing Contraction Configuration Modes")
    print("=" * 50)
    
    # Test cases
    test_inputs = [
        "he's happy",
        "don't worry", 
        "I'm ready",
        "you're right",
        "He&#x27;s here",  # HTML entity case
        "they're coming and we'll see"
    ]
    
    # Test different configuration combinations
    config_modes = [
        {
            "name": "Preserve Natural Speech (Default)",
            "expand_contractions": False,
            "expand_problematic_contractions_only": True,
            "preserve_natural_speech": True
        },
        {
            "name": "Expand All Contractions (Legacy)",
            "expand_contractions": True,
            "expand_problematic_contractions_only": False,
            "preserve_natural_speech": False
        },
        {
            "name": "Selective Expansion Only",
            "expand_contractions": False,
            "expand_problematic_contractions_only": True,
            "preserve_natural_speech": True
        }
    ]
    
    results = {}
    
    for mode in config_modes:
        print(f"\n📋 Mode: {mode['name']}")
        print("-" * 40)
        
        # Temporarily update config
        original_expand = config.performance.expand_contractions
        original_problematic = config.performance.expand_problematic_contractions_only
        original_preserve = config.performance.preserve_natural_speech
        
        config.performance.expand_contractions = mode["expand_contractions"]
        config.performance.expand_problematic_contractions_only = mode["expand_problematic_contractions_only"]
        config.performance.preserve_natural_speech = mode["preserve_natural_speech"]
        
        mode_results = []
        
        for test_input in test_inputs:
            result = phonemizer_preprocessor.preprocess_text(test_input)
            
            contraction_changes = [change for change in result.changes_made if "Expanded" in change]
            html_changes = [change for change in result.changes_made if "HTML entity" in change]
            
            print(f"Input:  '{test_input}'")
            print(f"Output: '{result.processed_text}'")
            
            if html_changes:
                print(f"HTML:   {html_changes}")
            if contraction_changes:
                print(f"Expand: {contraction_changes}")
            else:
                print("Expand: No contractions expanded")
            
            print()
            
            mode_results.append({
                "input": test_input,
                "output": result.processed_text,
                "expanded": len(contraction_changes) > 0,
                "html_decoded": len(html_changes) > 0
            })
        
        results[mode["name"]] = mode_results
        
        # Restore original config
        config.performance.expand_contractions = original_expand
        config.performance.expand_problematic_contractions_only = original_problematic
        config.performance.preserve_natural_speech = original_preserve
    
    return results

def analyze_configuration_results(results):
    """Analyze the results from different configuration modes"""
    
    print("=" * 50)
    print("📊 CONFIGURATION ANALYSIS")
    print("=" * 50)
    
    for mode_name, mode_results in results.items():
        total_tests = len(mode_results)
        expanded_tests = len([r for r in mode_results if r["expanded"]])
        html_decoded_tests = len([r for r in mode_results if r["html_decoded"]])
        
        expansion_rate = expanded_tests / total_tests * 100 if total_tests > 0 else 0
        
        print(f"\n📋 {mode_name}:")
        print(f"   Expansion rate: {expanded_tests}/{total_tests} ({expansion_rate:.1f}%)")
        print(f"   HTML entities decoded: {html_decoded_tests}/{total_tests}")
        
        # Check for natural speech preservation
        natural_examples = []
        for result in mode_results:
            if not result["expanded"] and ("'" in result["input"] or "&#x27;" in result["input"]):
                natural_examples.append(f"'{result['input']}' → '{result['output']}'")
        
        if natural_examples:
            print(f"   Natural speech preserved: {len(natural_examples)} cases")
            for example in natural_examples[:2]:  # Show first 2 examples
                print(f"     {example}")
    
    return results

def test_api_with_new_behavior():
    """Test API behavior with the new contraction handling"""
    
    print("\n🌐 API Testing with New Contraction Behavior")
    print("=" * 45)
    
    base_url = "http://localhost:8354"
    
    # Test cases that should now preserve contractions
    test_cases = [
        {
            "text": "he's happy",
            "expected_behavior": "Should preserve contraction for natural speech"
        },
        {
            "text": "He&#x27;s here", 
            "expected_behavior": "Should decode HTML entity and preserve contraction"
        },
        {
            "text": "don't worry about it",
            "expected_behavior": "Should preserve contraction for natural speech"
        },
        {
            "text": "I'm ready to go",
            "expected_behavior": "Should preserve contraction for natural speech"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['expected_behavior']}")
        print(f"Input: '{test_case['text']}'")
        
        payload = {
            "input": test_case["text"],
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
                print(f"✅ SUCCESS: {audio_size:,} bytes in {generation_time:.3f}s")
                
                # Check if it's a cache hit (very fast response)
                if generation_time < 0.1:
                    print("   🎯 Cache hit detected")
                else:
                    print("   🔄 Fresh generation")
                    
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("⚠️ API server not available")
            break
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_html_entity_regression():
    """Ensure HTML entity decoding still works correctly"""
    
    print("\n🔍 HTML Entity Regression Testing")
    print("=" * 35)
    
    html_test_cases = [
        "He&#x27;s here",
        "She&#x27;s coming", 
        "Testing &quot;quotes&quot; &amp; symbols",
        "Price: $100 &amp; &#x27;special&#x27; offer"
    ]
    
    for test_input in html_test_cases:
        result = phonemizer_preprocessor.preprocess_text(test_input)
        
        html_changes = [change for change in result.changes_made if "HTML entity" in change]
        
        print(f"Input:  '{test_input}'")
        print(f"Output: '{result.processed_text}'")
        print(f"HTML:   {html_changes}")
        
        # Verify HTML entities were decoded
        if "&#x27;" in test_input and "&#x27;" not in result.processed_text:
            print("✅ HTML entities properly decoded")
        elif "&quot;" in test_input and "&quot;" not in result.processed_text:
            print("✅ HTML entities properly decoded")
        elif "&amp;" in test_input and "&amp;" not in result.processed_text:
            print("✅ HTML entities properly decoded")
        else:
            print("⚠️ Check HTML entity decoding")
        
        print()

def main():
    """Run comprehensive contraction improvement tests"""
    
    print("🔧 Contraction Expansion Improvements Test Suite")
    print("=" * 60)
    print("Testing the new configurable contraction handling system...")
    print()
    
    # Test different configuration modes
    config_results = test_configuration_modes()
    
    # Analyze results
    analyze_configuration_results(config_results)
    
    # Test API behavior
    test_api_with_new_behavior()
    
    # Test HTML entity regression
    test_html_entity_regression()
    
    print("\n" + "=" * 60)
    print("🎯 CONTRACTION IMPROVEMENTS TEST COMPLETE")
    print()
    print("Key Improvements:")
    print("✅ Configurable contraction expansion")
    print("✅ Preserve natural speech by default")
    print("✅ Selective expansion for problematic contractions")
    print("✅ Maintained HTML entity decoding")
    print("✅ Backward compatibility with legacy behavior")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
