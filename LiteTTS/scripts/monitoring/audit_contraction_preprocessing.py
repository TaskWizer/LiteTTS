#!/usr/bin/env python3
"""
Comprehensive audit of contraction preprocessing behavior
Analyzes how contractions are handled in the text preprocessing pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
import requests
import time

def test_contraction_preprocessing():
    """Test contraction preprocessing behavior"""
    
    print("🔍 Comprehensive Contraction Preprocessing Audit")
    print("=" * 60)
    
    # Test cases covering different contraction types
    test_cases = [
        {
            "category": "Basic Contractions",
            "inputs": [
                "he's happy",
                "she's here", 
                "it's working",
                "I'm ready",
                "you're right",
                "we're going",
                "they're coming"
            ]
        },
        {
            "category": "Negative Contractions", 
            "inputs": [
                "don't worry",
                "won't work",
                "can't do it",
                "shouldn't go",
                "wouldn't say"
            ]
        },
        {
            "category": "Have Contractions",
            "inputs": [
                "I've been there",
                "you've seen it",
                "we've finished",
                "they've arrived"
            ]
        },
        {
            "category": "Will Contractions",
            "inputs": [
                "I'll go",
                "you'll see",
                "he'll come",
                "we'll try"
            ]
        },
        {
            "category": "Would Contractions",
            "inputs": [
                "I'd like that",
                "you'd better",
                "he'd prefer",
                "we'd rather"
            ]
        },
        {
            "category": "HTML Entity + Contractions",
            "inputs": [
                "He&#x27;s here",
                "She&#x27;s coming", 
                "It&#x27;s working",
                "They&#x27;re ready"
            ]
        },
        {
            "category": "Mixed Context",
            "inputs": [
                "He's here, she's there, and they're coming",
                "I don't think you're right about what he's saying",
                "We'll see if they've finished what we're doing"
            ]
        }
    ]
    
    all_results = []
    
    for category_data in test_cases:
        category = category_data["category"]
        inputs = category_data["inputs"]
        
        print(f"\n📋 {category}")
        print("-" * 40)
        
        for input_text in inputs:
            # Test preprocessing
            result = phonemizer_preprocessor.preprocess_text(input_text)
            
            # Analyze changes
            contraction_changes = [change for change in result.changes_made if "Expanded" in change]
            html_changes = [change for change in result.changes_made if "HTML entity" in change]
            
            print(f"Input:  '{input_text}'")
            print(f"Output: '{result.processed_text}'")
            
            if html_changes:
                print(f"HTML:   {html_changes}")
            if contraction_changes:
                print(f"Expand: {contraction_changes}")
            else:
                print("Expand: No contractions expanded")
            
            print(f"Score:  {result.confidence_score:.2f}")
            
            if result.warnings:
                print(f"Warn:   {result.warnings}")
            
            print()
            
            # Store for analysis
            all_results.append({
                "category": category,
                "input": input_text,
                "output": result.processed_text,
                "html_changes": html_changes,
                "contraction_changes": contraction_changes,
                "confidence": result.confidence_score,
                "warnings": result.warnings
            })
    
    return all_results

def analyze_contraction_behavior(results):
    """Analyze the contraction preprocessing behavior"""
    
    print("=" * 60)
    print("📊 CONTRACTION BEHAVIOR ANALYSIS")
    print("=" * 60)
    
    # Count expansion patterns
    total_tests = len(results)
    html_entity_tests = len([r for r in results if "&#x27;" in r["input"]])
    expanded_tests = len([r for r in results if r["contraction_changes"]])
    preserved_tests = len([r for r in results if not r["contraction_changes"] and ("'" in r["input"] or "&#x27;" in r["input"])])
    
    print(f"📈 Statistics:")
    print(f"   Total tests: {total_tests}")
    print(f"   HTML entity tests: {html_entity_tests}")
    print(f"   Tests with contractions expanded: {expanded_tests}")
    print(f"   Tests with contractions preserved: {preserved_tests}")
    print(f"   Expansion rate: {expanded_tests/total_tests*100:.1f}%")
    
    # Analyze by category
    print(f"\n📋 By Category:")
    categories = {}
    for result in results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "expanded": 0, "html": 0}
        categories[cat]["total"] += 1
        if result["contraction_changes"]:
            categories[cat]["expanded"] += 1
        if result["html_changes"]:
            categories[cat]["html"] += 1
    
    for cat, stats in categories.items():
        expansion_rate = stats["expanded"] / stats["total"] * 100
        print(f"   {cat}: {stats['expanded']}/{stats['total']} expanded ({expansion_rate:.1f}%)")
    
    # Check for patterns
    print(f"\n🔍 Pattern Analysis:")
    
    # HTML entity handling
    html_results = [r for r in results if "&#x27;" in r["input"]]
    if html_results:
        html_decoded = len([r for r in html_results if "Decoded HTML entity" in str(r["html_changes"])])
        print(f"   HTML entities decoded: {html_decoded}/{len(html_results)} ({html_decoded/len(html_results)*100:.1f}%)")
    
    # Common contractions
    common_contractions = ["he's", "she's", "it's", "I'm", "you're", "don't", "won't"]
    for contraction in common_contractions:
        contraction_results = [r for r in results if contraction.lower() in r["input"].lower()]
        if contraction_results:
            expanded = len([r for r in contraction_results if any(contraction.lower() in change.lower() for change in r["contraction_changes"])])
            print(f"   '{contraction}' expanded: {expanded}/{len(contraction_results)} times")
    
    return categories

def test_api_behavior(test_cases):
    """Test how the API handles contractions in actual TTS generation"""
    
    print("\n🌐 API Behavior Testing")
    print("=" * 30)
    
    base_url = "http://localhost:8354"
    
    # Test a few key cases
    api_test_cases = [
        "he's happy",
        "He&#x27;s here", 
        "don't worry",
        "I'm ready"
    ]
    
    for test_text in api_test_cases:
        print(f"\nTesting: '{test_text}'")
        
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
                print(f"✅ SUCCESS: {audio_size:,} bytes in {generation_time:.3f}s")
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

def recommend_improvements(analysis_results):
    """Provide recommendations based on analysis"""
    
    print("\n💡 RECOMMENDATIONS")
    print("=" * 30)
    
    # Calculate overall expansion rate
    total_tests = sum(stats["total"] for stats in analysis_results.values())
    total_expanded = sum(stats["expanded"] for stats in analysis_results.values())
    expansion_rate = total_expanded / total_tests * 100 if total_tests > 0 else 0
    
    print(f"Current expansion rate: {expansion_rate:.1f}%")
    
    if expansion_rate > 80:
        print("\n🚨 HIGH EXPANSION RATE DETECTED")
        print("   Issue: Most contractions are being expanded")
        print("   Impact: Unnatural speech output")
        print("   Recommendation: Add configuration to control expansion")
    elif expansion_rate > 50:
        print("\n⚠️ MODERATE EXPANSION RATE")
        print("   Issue: Many contractions are being expanded")
        print("   Recommendation: Selective expansion for problematic cases only")
    else:
        print("\n✅ REASONABLE EXPANSION RATE")
        print("   Current behavior may be acceptable")
    
    print("\n🔧 Suggested Improvements:")
    print("   1. Add configuration option: 'expand_contractions' (default: false)")
    print("   2. Implement selective expansion for phonemizer-problematic contractions")
    print("   3. Preserve natural contractions for better speech quality")
    print("   4. Maintain HTML entity decoding functionality")
    
    print("\n📋 Implementation Plan:")
    print("   1. Add contraction expansion control to config")
    print("   2. Modify _expand_contractions method to be conditional")
    print("   3. Create whitelist of problematic contractions that need expansion")
    print("   4. Test with both expanded and preserved contractions")
    print("   5. Validate no regression in HTML entity handling")

def main():
    """Run comprehensive contraction audit"""
    
    print("🔍 Contraction Preprocessing Comprehensive Audit")
    print("=" * 70)
    print("Analyzing how contractions are handled in text preprocessing...")
    print()
    
    # Test preprocessing behavior
    results = test_contraction_preprocessing()
    
    # Analyze results
    analysis = analyze_contraction_behavior(results)
    
    # Test API behavior
    test_api_behavior(results)
    
    # Provide recommendations
    recommend_improvements(analysis)
    
    print("\n" + "=" * 70)
    print("🎯 AUDIT COMPLETE")
    print("Review the analysis above to understand current contraction handling")
    print("and implement the recommended improvements.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
