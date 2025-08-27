#!/usr/bin/env python3
"""
Test the clean text normalizer
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.nlp.clean_text_normalizer import CleanTextNormalizer

def test_clean_normalizer():
    """Test the clean normalizer with critical pronunciation issues"""
    normalizer = CleanTextNormalizer()
    
    test_cases = [
        # Contractions
        ("I'll be there", "I will be there"),
        ("wasn't ready", "was not ready"), 
        ("you'll see", "you will see"),
        ("I'd like that", "I would like that"),
        ("I'm here", "I am here"),
        
        # Symbols
        ("The * symbol", "The asterisk symbol"),
        ("Use & for and", "Use and for and"),
        
        # Currency
        ("$568.91", "five hundred sixty eight dollars and ninety one cents"),
        ("$5,681.52", "five thousand six hundred eighty one dollars and fifty two cents"),
        ("~$100.50", "approximately one hundred dollars and fifty cents"),
        
        # Dates (the critical ISO format issue)
        ("2023-05-12", "May twelfth, two thousand twenty three"),
        ("12/18/2013", "December eighteenth, two thousand thirteen"),
        ("05/06/19", "May sixth, two thousand nineteen"),
        
        # Abbreviations
        ("FAQ section", "F-A-Q section"),
        ("ASAP please", "A-S-A-P please"),
        ("e.g. this example", "for example this example"),
        
        # Pronunciations
        ("Asterisk pronunciation", "AS-ter-isk pronunciation"),
        ("TSLA stock", "T-S-L-A stock"),  # Corrected: spell out ticker symbols
        ("AAPL shares", "A-A-P-L shares"),  # Additional ticker test
        ("Elon Musk", "EE-lahn Musk"),
        ("hmm, let me think", "hum, let me think"),
        
        # HTML entities
        ("John&#x27;s car", "John's car"),
        ("&quot;Hello&quot;", "Hello"),
        ("&amp; symbol", "and symbol"),
    ]
    
    print("=== Testing Clean Text Normalizer ===\n")
    
    for input_text, expected in test_cases:
        try:
            result = normalizer.normalize_text(input_text)
            output = result.processed_text
            
            print(f"Input:    {input_text}")
            print(f"Expected: {expected}")
            print(f"Output:   {output}")
            
            if expected.lower() in output.lower() or output.lower() == expected.lower():
                print("✅ PASS")
            else:
                print("❌ FAIL")
            
            if result.changes_made:
                print(f"Changes:  {', '.join(result.changes_made)}")
            
            print(f"Time:     {result.processing_time:.4f}s")
            print("-" * 60)
            
        except Exception as e:
            print(f"❌ ERROR processing '{input_text}': {e}")
            print("-" * 60)

if __name__ == '__main__':
    test_clean_normalizer()
