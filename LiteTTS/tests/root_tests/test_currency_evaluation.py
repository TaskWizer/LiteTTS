#!/usr/bin/env python3
"""
Currency and Financial Data Processing Evaluation
Test current capabilities and identify gaps
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_current_currency_processing():
    """Test current currency processing capabilities"""
    print("💰 Currency & Financial Data Processing Evaluation")
    print("=" * 60)
    
    # Test cases covering various currency scenarios
    test_cases = [
        # Basic currency amounts
        ("$100", "one hundred dollars"),
        ("$1", "one dollar"),
        ("$25.50", "twenty five dollars and fifty cents"),
        
        # Large amounts with commas
        ("$1,000", "one thousand dollars"),
        ("$5,681.52", "five thousand six hundred eighty one dollars and fifty two cents"),
        ("$1,234,567.89", "one million two hundred thirty four thousand five hundred sixty seven dollars and eighty nine cents"),
        
        # Approximate amounts
        ("~$568.91", "approximately five hundred sixty eight dollars and ninety one cents"),
        ("approximately $1,000", "approximately one thousand dollars"),
        
        # Different currencies
        ("€100.50", "one hundred euros and fifty cents"),
        ("£75.25", "seventy five pounds and twenty five cents"),
        ("¥1000", "one thousand yen"),
        
        # Edge cases
        ("$0.01", "one cent"),
        ("$0.99", "ninety nine cents"),
        ("$1000000", "one million dollars"),
        
        # Financial context
        ("The stock price is $45.67", "The stock price is forty five dollars and sixty seven cents"),
        ("Revenue of $2.5M", "Revenue of two point five M"),  # May not handle M suffix
        ("Market cap: $1.2B", "Market cap: one point two B"),  # May not handle B suffix
        
        # Multiple currencies in text
        ("$100 USD vs €85 EUR", "one hundred dollars USD vs eighty five euros EUR"),
        
        # Decimal precision variations
        ("$123.4", "one hundred twenty three dollars and forty cents"),
        ("$123.40", "one hundred twenty three dollars and forty cents"),
        
        # Negative amounts (if supported)
        ("-$50", "negative fifty dollars"),
        
        # Percentage and financial terms
        ("5.25% interest rate", "five point two five percent interest rate"),
        ("basis points", "basis points"),  # Should remain unchanged
    ]
    
    # Test with different normalizers
    normalizers = []
    
    try:
        from LiteTTS.nlp.text_normalizer import TextNormalizer
        normalizers.append(("TextNormalizer", TextNormalizer()))
    except ImportError as e:
        print(f"❌ Could not import TextNormalizer: {e}")
    
    try:
        from LiteTTS.nlp.clean_text_normalizer import CleanTextNormalizer
        normalizers.append(("CleanTextNormalizer", CleanTextNormalizer()))
    except ImportError as e:
        print(f"❌ Could not import CleanTextNormalizer: {e}")
    
    if not normalizers:
        print("❌ No normalizers available for testing")
        return False
    
    all_passed = True
    
    for normalizer_name, normalizer in normalizers:
        print(f"\n🧪 Testing {normalizer_name}")
        print("-" * 40)
        
        for i, (input_text, expected_output) in enumerate(test_cases, 1):
            print(f"\nTest {i}: '{input_text}'")
            print(f"Expected: '{expected_output}'")
            
            try:
                if hasattr(normalizer, 'normalize_text'):
                    result = normalizer.normalize_text(input_text)
                    if hasattr(result, 'processed_text'):
                        actual_output = result.processed_text
                    else:
                        actual_output = result
                else:
                    # Fallback for different interface
                    actual_output = str(normalizer)
                
                print(f"Actual:   '{actual_output}'")
                
                # Check if output is reasonable (contains currency words)
                currency_words = ['dollar', 'dollars', 'cent', 'cents', 'euro', 'euros', 'pound', 'pounds', 'yen']
                has_currency = any(word in actual_output.lower() for word in currency_words)
                
                if has_currency or '$' not in input_text:
                    print("✅ Contains currency words or no currency in input")
                else:
                    print("❌ Missing currency words in output")
                    all_passed = False
                
                # Check for common issues
                issues = []
                if 'x27' in actual_output or 'hashtag' in actual_output:
                    issues.append("HTML entity encoding")
                if actual_output == input_text and '$' in input_text:
                    issues.append("No processing applied")
                
                if issues:
                    print(f"⚠️  Issues: {', '.join(issues)}")
                    all_passed = False
                
            except Exception as e:
                print(f"❌ Error: {e}")
                all_passed = False
    
    return all_passed

def analyze_currency_gaps():
    """Analyze gaps in current currency processing"""
    print("\n🔍 Currency Processing Gap Analysis")
    print("=" * 60)
    
    gaps = [
        "Limited support for currency suffixes (M, B, K)",
        "No handling of financial abbreviations (bps, bp)",
        "Limited international currency format support",
        "No context-aware currency processing",
        "Limited support for very large numbers (trillions+)",
        "No handling of currency ranges ($100-$200)",
        "Limited support for fractional currency expressions",
        "No handling of currency conversion expressions",
        "Limited support for financial market terminology",
        "No handling of percentage with currency context"
    ]
    
    print("Identified gaps in currency processing:")
    for i, gap in enumerate(gaps, 1):
        print(f"{i:2d}. {gap}")
    
    return gaps

def recommend_improvements():
    """Recommend specific improvements for currency processing"""
    print("\n💡 Recommended Currency Processing Improvements")
    print("=" * 60)
    
    improvements = [
        {
            "area": "Large Number Handling",
            "description": "Extend number-to-words for billions, trillions",
            "priority": "High",
            "examples": ["$1.2B → one point two billion dollars"]
        },
        {
            "area": "Currency Suffixes",
            "description": "Handle M, B, K suffixes in financial context",
            "priority": "High", 
            "examples": ["$2.5M → two point five million dollars"]
        },
        {
            "area": "Approximate Values",
            "description": "Better handling of approximate financial expressions",
            "priority": "Medium",
            "examples": ["~$500 → approximately five hundred dollars"]
        },
        {
            "area": "International Formats",
            "description": "Support for different currency formatting conventions",
            "priority": "Medium",
            "examples": ["1.234,56 € → one thousand two hundred thirty four euros and fifty six cents"]
        },
        {
            "area": "Financial Context",
            "description": "Context-aware processing for financial terms",
            "priority": "Medium",
            "examples": ["25 bps → twenty five basis points"]
        },
        {
            "area": "Currency Ranges",
            "description": "Handle currency ranges and comparisons",
            "priority": "Low",
            "examples": ["$100-$200 → one hundred to two hundred dollars"]
        }
    ]
    
    for improvement in improvements:
        print(f"\n📋 {improvement['area']} ({improvement['priority']} Priority)")
        print(f"   {improvement['description']}")
        print(f"   Examples: {', '.join(improvement['examples'])}")
    
    return improvements

if __name__ == "__main__":
    print("🚀 Starting Currency & Financial Data Processing Evaluation")
    
    # Run tests
    test_passed = test_current_currency_processing()
    
    # Analyze gaps
    gaps = analyze_currency_gaps()
    
    # Recommend improvements
    improvements = recommend_improvements()
    
    print("\n" + "=" * 60)
    print("📊 Evaluation Summary")
    print("=" * 60)
    
    if test_passed:
        print("✅ Basic currency processing is working")
    else:
        print("❌ Issues found in current currency processing")
    
    print(f"🔍 {len(gaps)} gaps identified")
    print(f"💡 {len(improvements)} improvement areas recommended")
    
    print("\n🎯 Next Steps:")
    print("1. Implement enhanced currency processing system")
    print("2. Add support for large number suffixes (M, B, K)")
    print("3. Improve international currency format support")
    print("4. Add financial context awareness")
    print("5. Create comprehensive test suite for currency processing")
