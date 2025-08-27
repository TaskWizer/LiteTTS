#!/usr/bin/env python3
"""
Debug script to trace the NLP pipeline step by step
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
from LiteTTS.nlp.processor import NLPProcessor, NormalizationOptions

def debug_nlp_pipeline():
    """Debug the NLP pipeline step by step"""
    
    print("🔬 Step-by-Step Debug of NLP Pipeline")
    print("=" * 45)
    
    # Start with preprocessed text (after HTML entity decoding)
    test_input = "John's book"  # This is what we get after preprocessing
    print(f"Input to NLP Pipeline: '{test_input}'")
    
    # Create NLP processor
    nlp_processor = NLPProcessor()
    
    # Test each step individually
    print("\n📋 Step 1: Spell Processor")
    spell_result = nlp_processor.spell_processor.handle_spell_functions(test_input)
    print(f"After spell processing: '{spell_result}'")
    
    print("\n📋 Step 2: Phonetic Processor")
    phonetic_result = nlp_processor.phonetic_processor.process_phonetics(spell_result)
    print(f"After phonetic processing: '{phonetic_result}'")
    
    print("\n📋 Step 3: Homograph Resolver")
    homograph_result = nlp_processor.homograph_resolver.resolve_homographs(phonetic_result)
    print(f"After homograph resolution: '{homograph_result}'")
    
    print("\n📋 Step 4: Text Normalizer")
    options = NormalizationOptions()
    if options.normalize:
        normalizer_result = nlp_processor.text_normalizer.normalize_text(homograph_result)
        print(f"After text normalization: '{normalizer_result}'")
    else:
        normalizer_result = homograph_result
        print(f"Text normalization skipped: '{normalizer_result}'")
    
    print("\n📋 Step 5: Prosody Analyzer")
    prosody_result = nlp_processor.prosody_analyzer.process_conversational_features(normalizer_result)
    print(f"After prosody analysis: '{prosody_result}'")
    
    print("\n📋 Full NLP Pipeline")
    full_result = nlp_processor.process_text(test_input)
    print(f"Full pipeline result: '{full_result}'")
    
    # Compare results
    print("\n📊 Comparison:")
    print(f"Step-by-step final: '{prosody_result}'")
    print(f"Full pipeline final: '{full_result}'")
    
    if prosody_result != full_result:
        print("❌ MISMATCH: Step-by-step and full pipeline produce different results!")
    else:
        print("✅ MATCH: Step-by-step and full pipeline produce same results")

def debug_with_html_entity_input():
    """Debug with the original HTML entity input"""
    
    print("\n🔬 Debug with HTML Entity Input")
    print("=" * 35)
    
    # Original input with HTML entity
    original_input = "John&#x27;s book"
    print(f"Original input: '{original_input}'")
    
    # Step 1: Preprocess
    preprocessed = phonemizer_preprocessor.preprocess_text(original_input)
    print(f"After preprocessing: '{preprocessed.processed_text}'")
    print(f"Preprocessing changes: {preprocessed.changes_made}")
    
    # Step 2: NLP processing
    nlp_processor = NLPProcessor()
    nlp_result = nlp_processor.process_text(preprocessed.processed_text)
    print(f"After NLP processing: '{nlp_result}'")
    
    # Check for the problematic pattern
    if "and hash" in nlp_result.lower() or "x27" in nlp_result:
        print("❌ PROBLEM: Found 'and hash' or 'x27' in NLP result")
    else:
        print("✅ GOOD: No problematic patterns found")

def debug_prosody_analyzer():
    """Debug the prosody analyzer specifically"""
    
    print("\n🔬 Debug Prosody Analyzer")
    print("=" * 30)
    
    nlp_processor = NLPProcessor()
    
    test_cases = [
        "John's book",
        "it's working",
        "that's correct"
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: '{test_case}'")
        
        # Test prosody analyzer directly
        prosody_result = nlp_processor.prosody_analyzer.process_conversational_features(test_case)
        print(f"Prosody result: '{prosody_result}'")
        
        # Check if prosody analyzer is causing the issue
        if test_case != prosody_result:
            print(f"⚠️ Prosody analyzer changed the text!")
            print(f"  Input:  '{test_case}'")
            print(f"  Output: '{prosody_result}'")
        else:
            print("✅ Prosody analyzer preserved the text")

def main():
    """Run comprehensive NLP pipeline debug"""
    
    print("🐛 NLP Pipeline Debug Analysis")
    print("=" * 35)
    
    # Debug the NLP pipeline step by step
    debug_nlp_pipeline()
    
    # Debug with HTML entity input
    debug_with_html_entity_input()
    
    # Debug prosody analyzer specifically
    debug_prosody_analyzer()
    
    print("\n" + "=" * 35)
    print("🎯 DEBUG COMPLETE")
    print("Check which step is introducing the 'and hash x27' issue")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
