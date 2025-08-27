#!/usr/bin/env python3
"""
Debug script to trace the possessive contraction issue step by step
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
from LiteTTS.nlp.text_normalizer import TextNormalizer
from LiteTTS.nlp.processor import NLPProcessor

def debug_step_by_step():
    """Debug the possessive contraction issue step by step"""
    
    print("🔬 Step-by-Step Debug of Possessive Contraction Issue")
    print("=" * 60)
    
    test_input = "John&#x27;s book"
    print(f"Original Input: '{test_input}'")
    
    # Step 1: Test HTML entity decoding only
    print("\n📋 Step 1: HTML Entity Decoding")
    decoded_text, changes = phonemizer_preprocessor._decode_html_entities(test_input)
    print(f"After HTML decoding: '{decoded_text}'")
    print(f"Changes: {changes}")
    
    # Step 2: Test TextNormalizer on the decoded text
    print("\n📋 Step 2: TextNormalizer Processing")
    normalizer = TextNormalizer()
    
    # Test each normalization step individually
    print("\n  2a: Currency normalization")
    currency_result = normalizer._normalize_currency(decoded_text)
    print(f"    Result: '{currency_result}'")
    
    print("\n  2b: Number normalization")
    number_result = normalizer._normalize_numbers(currency_result)
    print(f"    Result: '{number_result}'")
    
    print("\n  2c: Contraction normalization")
    contraction_result = normalizer._normalize_contractions(number_result)
    print(f"    Result: '{contraction_result}'")
    
    print("\n  2d: Abbreviation normalization")
    abbrev_result = normalizer._normalize_abbreviations(contraction_result)
    print(f"    Result: '{abbrev_result}'")
    
    print("\n  2e: Symbol normalization")
    symbol_result = normalizer._normalize_symbols(abbrev_result)
    print(f"    Result: '{symbol_result}'")
    
    print("\n  2f: Possessive normalization")
    possessive_result = normalizer._normalize_possessives(symbol_result)
    print(f"    Result: '{possessive_result}'")
    
    print("\n  2g: URL/Email normalization")
    url_result = normalizer._normalize_urls_emails(possessive_result)
    print(f"    Result: '{url_result}'")
    
    print("\n  2h: Punctuation normalization")
    punct_result = normalizer._normalize_punctuation(url_result)
    print(f"    Result: '{punct_result}'")
    
    print("\n  2i: Whitespace cleanup")
    final_result = normalizer._clean_whitespace(punct_result)
    print(f"    Final Result: '{final_result}'")
    
    # Step 3: Compare with full normalization
    print("\n📋 Step 3: Full TextNormalizer")
    full_normalized = normalizer.normalize_text(decoded_text)
    print(f"Full normalization result: '{full_normalized}'")
    
    # Step 4: Test symbol patterns individually
    print("\n📋 Step 4: Individual Symbol Pattern Testing")
    for i, (pattern, replacement) in enumerate(normalizer.symbol_patterns):
        import re
        if re.search(pattern, decoded_text):
            print(f"  Pattern {i+1}: '{pattern}' -> '{replacement}'")
            test_result = re.sub(pattern, replacement, decoded_text)
            print(f"    Applied to '{decoded_text}' -> '{test_result}'")

def debug_symbol_mapping():
    """Debug the symbol mapping from external config"""
    
    print("\n🔧 Symbol Mapping Debug")
    print("=" * 30)
    
    # Test the symbol words map from phonemizer preprocessor
    symbol_map = phonemizer_preprocessor.symbol_words_map
    print(f"Symbol words map has {len(symbol_map)} entries")
    
    # Check for apostrophe-related mappings
    apostrophe_mappings = {}
    for symbol, word in symbol_map.items():
        if "'" in symbol or 'apostrophe' in word.lower() or 'hash' in word.lower():
            apostrophe_mappings[symbol] = word
    
    print("\nApostrophe-related mappings:")
    for symbol, word in apostrophe_mappings.items():
        print(f"  '{symbol}' -> '{word}'")
    
    # Test specific symbol conversion
    test_text = "John's book"
    print(f"\nTesting symbol conversion on: '{test_text}'")
    
    result, changes = phonemizer_preprocessor._convert_symbols_to_words(test_text)
    print(f"Result: '{result}'")
    print(f"Changes: {changes}")

def debug_html_entity_patterns():
    """Debug HTML entity patterns that might be causing issues"""
    
    print("\n🔍 HTML Entity Pattern Debug")
    print("=" * 35)
    
    # Check the HTML entity patterns
    print("HTML entity patterns:")
    print(f"  Amp pattern: {phonemizer_preprocessor.html_entity_amp_pattern.pattern}")
    print(f"  Hash pattern: {phonemizer_preprocessor.html_entity_hash_pattern.pattern}")
    
    # Test these patterns
    test_cases = [
        "John's book",
        "John&amp;Mary",
        "John&#x27;s book",
        "Price: $100 &amp; more"
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: '{test_case}'")
        
        # Test amp pattern
        amp_matches = phonemizer_preprocessor.html_entity_amp_pattern.findall(test_case)
        if amp_matches:
            print(f"  Amp pattern matches: {amp_matches}")
        
        # Test hash pattern
        hash_matches = phonemizer_preprocessor.html_entity_hash_pattern.findall(test_case)
        if hash_matches:
            print(f"  Hash pattern matches: {hash_matches}")

def main():
    """Run comprehensive debug analysis"""
    
    print("🐛 Possessive Contractions Debug Analysis")
    print("=" * 50)
    
    # Step-by-step debugging
    debug_step_by_step()
    
    # Symbol mapping debugging
    debug_symbol_mapping()
    
    # HTML entity pattern debugging
    debug_html_entity_patterns()
    
    print("\n" + "=" * 50)
    print("🎯 DEBUG COMPLETE")
    print("Check the step-by-step output to identify where 'and hash x27' is introduced")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
