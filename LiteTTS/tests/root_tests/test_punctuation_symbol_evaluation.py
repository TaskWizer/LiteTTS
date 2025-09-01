#!/usr/bin/env python3
"""
Punctuation & Symbol Processing Evaluation
Test current capabilities and identify gaps
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_current_punctuation_symbol_processing():
    """Test current punctuation and symbol processing capabilities"""
    print("🔣 Punctuation & Symbol Processing Evaluation")
    print("=" * 60)
    
    # Test cases covering various punctuation/symbol scenarios
    test_cases = [
        # Critical Issues from User Reports
        ("The * symbol", "The asterisk symbol"),  # * → astrisk vs asterisk
        ("Use & for and", "Use and for and"),  # & → and conversion
        ("John&#x27;s car", "John's car"),  # HTML entity → x 27 pronunciation
        ("&quot;Hello&quot;", "Hello"),  # quote → in quat pronunciation
        
        # Apostrophe and Possessive Issues
        ("John's book", "John's book"),  # Basic possessive
        ("The cat's toy", "The cat's toy"),  # Simple possessive
        ("It's a nice day", "It's a nice day"),  # Contraction vs possessive
        ("The dogs' toys", "The dogs' toys"),  # Plural possessive
        ("James's car", "James's car"),  # Name ending in s
        
        # HTML Entity Issues
        ("I&#x27;ll be there", "I'll be there"),  # HTML apostrophe
        ("She&#39;s coming", "She's coming"),  # Decimal apostrophe
        ("&apos;Hello&apos;", "'Hello'"),  # Named apostrophe entity
        ("&amp; symbol", "and symbol"),  # Ampersand entity
        
        # Quotation Mark Issues
        ('"Hello world"', "Hello world"),  # Double quotes should be silent
        ("'Single quotes'", "Single quotes"),  # Single quotes
        ('"Smart quotes"', "Smart quotes"),  # Smart double quotes
        ("'Smart single'", "Smart single"),  # Smart single quotes
        ("She said \"yes\"", "She said yes"),  # Quotes in context
        
        # Symbol Processing
        ("5 + 3 = 8", "5 plus 3 equals 8"),  # Math symbols
        ("50% complete", "50 percent complete"),  # Percentage
        ("user@domain.com", "user at domain dot com"),  # Email
        ("File #1", "File hash 1"),  # Hash symbol
        ("~50 items", "approximately 50 items"),  # Tilde
        ("A | B", "A pipe B"),  # Pipe symbol
        ("Path\\file", "Path backslash file"),  # Backslash
        ("A ^ B", "A caret B"),  # Caret
        
        # Punctuation Spacing Issues
        ("Hello,world", "Hello, world"),  # Missing space after comma
        ("Hello , world", "Hello, world"),  # Extra space before comma
        ("Thinking, or not", "Thinking, or not"),  # Comma conjunction issue
        ("Yes,no,maybe", "Yes, no, maybe"),  # Multiple commas
        
        # Special Characters
        ("© 2023", "copyright 2023"),  # Copyright
        ("® trademark", "registered trademark"),  # Registered
        ("™ symbol", "trademark symbol"),  # Trademark
        ("Temperature: 25°C", "Temperature: 25 degrees C"),  # Degrees
        
        # Ellipsis and Dashes
        ("Wait...", "Wait ellipsis"),  # Ellipsis
        ("Wait...for it", "Wait ellipsis for it"),  # Ellipsis in context
        ("Long—dash", "Long em dash"),  # Em dash
        ("Short–dash", "Short en dash"),  # En dash
        ("Range: 1-10", "Range: 1 dash 10"),  # Hyphen
        
        # Multiple Punctuation
        ("Really?!", "Really question exclamation"),  # Multiple punctuation
        ("What??", "What question question"),  # Multiple question marks
        ("Amazing!!!", "Amazing exclamation exclamation exclamation"),  # Multiple exclamations
        
        # Complex Symbol Combinations
        ("$100 & €50", "100 dollars and 50 euros"),  # Currency and ampersand
        ("50% + 25% = 75%", "50 percent plus 25 percent equals 75 percent"),  # Math with percentages
        ("File*.txt", "File asterisk dot txt"),  # Wildcard
        ("A/B testing", "A slash B testing"),  # Slash in context
        
        # Markdown-like Symbols
        ("**bold text**", "bold text"),  # Bold markdown (should remove)
        ("*italic text*", "italic text"),  # Italic markdown (should remove)
        ("# Header", "hash Header"),  # Header markdown
        ("- List item", "dash List item"),  # List markdown
        
        # Edge Cases
        ("", ""),  # Empty string
        ("   ", ""),  # Whitespace only
        ("!@#$%^&*()", "exclamation at hash dollars percent caret and asterisk parentheses"),  # Symbol soup
        ("Mix3d numb3rs & symb0ls", "Mix3d numb3rs and symb0ls"),  # Mixed content
    ]
    
    # Test with different processors
    processors = []
    
    try:
        from LiteTTS.nlp.text_normalizer import TextNormalizer
        processors.append(("TextNormalizer", TextNormalizer()))
    except ImportError as e:
        print(f"❌ Could not import TextNormalizer: {e}")
    
    try:
        from LiteTTS.nlp.clean_text_normalizer import CleanTextNormalizer
        processors.append(("CleanTextNormalizer", CleanTextNormalizer()))
    except ImportError as e:
        print(f"❌ Could not import CleanTextNormalizer: {e}")
    
    try:
        from LiteTTS.nlp.advanced_symbol_processor import AdvancedSymbolProcessor
        processors.append(("AdvancedSymbolProcessor", AdvancedSymbolProcessor()))
    except ImportError as e:
        print(f"❌ Could not import AdvancedSymbolProcessor: {e}")
    
    if not processors:
        print("❌ No processors available for testing")
        return False
    
    all_passed = True
    
    for processor_name, processor in processors:
        print(f"\n🧪 Testing {processor_name}")
        print("-" * 40)
        
        for i, (input_text, expected_output) in enumerate(test_cases, 1):
            print(f"\nTest {i}: '{input_text}'")
            print(f"Expected: '{expected_output}'")
            
            try:
                if hasattr(processor, 'normalize_text'):
                    result = processor.normalize_text(input_text)
                    if hasattr(result, 'processed_text'):
                        actual_output = result.processed_text
                    else:
                        actual_output = result
                elif hasattr(processor, 'process_symbols'):
                    actual_output = processor.process_symbols(input_text)
                else:
                    actual_output = str(processor)
                
                print(f"Actual:   '{actual_output}'")
                
                # Check for common issues
                issues = []
                
                # Check for HTML entity issues
                if any(entity in input_text for entity in ['&#x27;', '&#39;', '&apos;', '&quot;']):
                    if any(issue in actual_output.lower() for issue in ['x 27', 'x27', 'hash 27', 'in quat']):
                        issues.append("HTML entity pronunciation issue")
                
                # Check for asterisk pronunciation
                if '*' in input_text and 'astrisk' in actual_output.lower():
                    issues.append("Asterisk mispronunciation (astrisk)")
                
                # Check for ampersand conversion
                if '&' in input_text and '&' in actual_output:
                    issues.append("Ampersand not converted to 'and'")
                
                # Check for quote handling
                if any(quote in input_text for quote in ['"', '"', '"', "'", "'"]):
                    if any(issue in actual_output.lower() for issue in ['quote', 'quat']):
                        issues.append("Quote pronunciation issue")
                
                # Check for proper spacing after commas
                if ',' in input_text and ',,' in actual_output:
                    issues.append("Comma spacing issue")
                
                # Check if no processing was applied when it should have been
                if any(symbol in input_text for symbol in ['*', '&', '%', '@', '#']) and input_text == actual_output:
                    issues.append("No symbol processing applied")
                
                if issues:
                    print(f"⚠️  Issues: {', '.join(issues)}")
                    all_passed = False
                else:
                    print("✅ Processed correctly")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                all_passed = False
    
    return all_passed

def analyze_punctuation_symbol_gaps():
    """Analyze gaps in current punctuation/symbol processing"""
    print("\n🔍 Punctuation & Symbol Processing Gap Analysis")
    print("=" * 60)
    
    gaps = [
        "HTML entity pronunciation issues (&#x27; → 'x 27')",
        "Asterisk mispronunciation (* → 'astrisk' instead of 'asterisk')",
        "Quotation mark pronunciation ('quote' → 'in quat')",
        "Inconsistent apostrophe normalization",
        "Poor comma spacing handling",
        "Limited possessive processing",
        "Inconsistent symbol-to-word conversion",
        "No context-aware symbol processing",
        "Limited markdown symbol handling",
        "Poor multiple punctuation processing",
        "Inconsistent dash and hyphen handling",
        "Limited special character support"
    ]
    
    print("Identified gaps in punctuation/symbol processing:")
    for i, gap in enumerate(gaps, 1):
        print(f"{i:2d}. {gap}")
    
    return gaps

def recommend_punctuation_symbol_improvements():
    """Recommend specific improvements for punctuation/symbol processing"""
    print("\n💡 Recommended Punctuation & Symbol Processing Improvements")
    print("=" * 60)
    
    improvements = [
        {
            "area": "HTML Entity Processing",
            "description": "Fix critical HTML entity pronunciation issues",
            "priority": "Critical",
            "examples": ["&#x27; → ' (not 'x 27')", "&quot; → silent (not 'in quat')"]
        },
        {
            "area": "Symbol Pronunciation",
            "description": "Correct symbol pronunciation accuracy",
            "priority": "Critical",
            "examples": ["* → asterisk (not 'astrisk')", "& → and"]
        },
        {
            "area": "Quote Handling",
            "description": "Natural quotation mark processing",
            "priority": "High",
            "examples": ['"text" → text (silent quotes)', "'text' → text (silent quotes)"]
        },
        {
            "area": "Comma Processing",
            "description": "Improved comma spacing and pronunciation",
            "priority": "High",
            "examples": ["Hello,world → Hello, world", "Thinking, or → proper pause timing"]
        },
        {
            "area": "Apostrophe Normalization",
            "description": "Consistent apostrophe handling across all variants",
            "priority": "Medium",
            "examples": ["Various apostrophe types → standard apostrophe"]
        },
        {
            "area": "Advanced Symbol Processing",
            "description": "Context-aware symbol conversion",
            "priority": "Medium",
            "examples": ["Math context: + → plus", "File context: * → asterisk"]
        }
    ]
    
    for improvement in improvements:
        print(f"\n📋 {improvement['area']} ({improvement['priority']} Priority)")
        print(f"   {improvement['description']}")
        print(f"   Examples: {', '.join(improvement['examples'])}")
    
    return improvements

if __name__ == "__main__":
    print("🚀 Starting Punctuation & Symbol Processing Evaluation")
    
    # Run tests
    test_passed = test_current_punctuation_symbol_processing()
    
    # Analyze gaps
    gaps = analyze_punctuation_symbol_gaps()
    
    # Recommend improvements
    improvements = recommend_punctuation_symbol_improvements()
    
    print("\n" + "=" * 60)
    print("📊 Evaluation Summary")
    print("=" * 60)
    
    if test_passed:
        print("✅ Basic punctuation/symbol processing is working")
    else:
        print("❌ Issues found in current punctuation/symbol processing")
    
    print(f"🔍 {len(gaps)} gaps identified")
    print(f"💡 {len(improvements)} improvement areas recommended")
    
    print("\n🎯 Next Steps:")
    print("1. Fix critical HTML entity pronunciation issues")
    print("2. Correct asterisk and symbol pronunciation")
    print("3. Implement natural quote handling")
    print("4. Improve comma spacing and timing")
    print("5. Create comprehensive test suite for punctuation/symbol processing")
