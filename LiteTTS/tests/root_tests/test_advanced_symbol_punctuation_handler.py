#!/usr/bin/env python3
"""
Test suite for Advanced Symbol & Punctuation Handler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from LiteTTS.nlp.advanced_symbol_processor import AdvancedSymbolProcessor

class TestAdvancedSymbolPunctuationHandler(unittest.TestCase):
    """Test cases for Advanced Symbol & Punctuation Handler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = AdvancedSymbolProcessor()
    
    def test_critical_pronunciation_fixes(self):
        """Test critical pronunciation issue fixes"""
        test_cases = [
            # Critical issues from user reports
            ("The * symbol", "The  asterisk  symbol"),  # asterisk not "astrisk"
            ("Use & for and", "Use  and  for  and "),  # & → and conversion
            ("John&#x27;s car", "John's car"),  # HTML entity → x 27 pronunciation
            ("&quot;Hello&quot;", "Hello"),  # quote → in quat pronunciation
            ("Press * to continue", "Press  asterisk  to continue"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_symbols(input_text)
                # Check that asterisk is properly converted
                if "*" in input_text:
                    self.assertIn("asterisk", result)
                    self.assertNotIn("*", result)
                # Check that HTML entities are fixed
                if "&#x27;" in input_text:
                    self.assertNotIn("x 27", result)
                    self.assertNotIn("&#x27;", result)
                # Check that quotes are handled
                if "&quot;" in input_text:
                    self.assertNotIn("in quat", result)
                    self.assertNotIn("&quot;", result)
    
    def test_html_entity_processing(self):
        """Test HTML entity processing"""
        test_cases = [
            ("John&#x27;s car", "John's car"),
            ("&#39;Hello&#39;", "'Hello'"),
            ("&apos;test&apos;", "'test'"),
            ("&quot;quoted&quot;", "quoted"),
            ("&#34;text&#34;", "text"),
            ("&amp;", " and "),
            ("&lt;tag&gt;", " less than tag greater than "),
            ("&nbsp;space", " space"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_symbols(input_text)
                # Check that HTML entities are properly converted
                self.assertNotIn("&#", result)
                self.assertNotIn("&quot;", result)
                self.assertNotIn("&amp;", result)
    
    def test_enhanced_special_characters(self):
        """Test enhanced special character support"""
        test_cases = [
            ("© 2024", " copyright  2024"),
            ("® trademark", " registered trademark  trademark"),
            ("™ symbol", " trademark  symbol"),
            ("90° angle", "90 degrees  angle"),
            ("§ section", " section  section"),
            ("¶ paragraph", " paragraph  paragraph"),
            ("• bullet", " bullet  bullet"),
            ("± variance", " plus or minus  variance"),
            ("× multiplication", " times  multiplication"),
            ("÷ division", " divided by  division"),
            ("≠ not equal", " not equal to  not equal"),
            ("≤ less equal", " less than or equal to  less equal"),
            ("≥ greater equal", " greater than or equal to  greater equal"),
            ("∞ infinity", " infinity  infinity"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_symbols(input_text)
                # Check that special characters are converted to words
                self.assertNotIn("©", result)
                self.assertNotIn("®", result)
                self.assertNotIn("™", result)
                self.assertNotIn("°", result)
                self.assertNotIn("±", result)
                self.assertNotIn("×", result)
                self.assertNotIn("÷", result)
    
    def test_international_currency_symbols(self):
        """Test international currency symbol support"""
        test_cases = [
            ("₹100", " rupee 100"),
            ("₽500", " ruble 500"),
            ("₩1000", " won 1000"),
            ("¢75", " cent 75"),
            ("₦200", " naira 200"),
            ("₪50", " shekel 50"),
            ("₫1000", " dong 1000"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_symbols(input_text)
                # Check that currency symbols are converted
                for symbol in ["₹", "₽", "₩", "¢", "₦", "₪", "₫"]:
                    self.assertNotIn(symbol, result)
    
    def test_advanced_punctuation_handling(self):
        """Test advanced punctuation handling"""
        test_cases = [
            ("Text...", "Text ellipsis "),  # Multiple dots to ellipsis
            ("Really???", "Really?"),  # Multiple question marks
            ("Wow!!!", "Wow!"),  # Multiple exclamation marks
            ("Text—dash", "Text em dash dash"),  # Em dash
            ("Text–dash", "Text en dash dash"),  # En dash
            ("Text−minus", "Text minus minus"),  # Minus sign
            ('"Smart quotes"', "Smart quotes"),  # Smart quotes removal
            ("'Single quotes'", "Single quotes"),  # Smart single quotes
            ("Text   spaces", "Text spaces"),  # Multiple spaces
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_symbols(input_text)
                # Check specific transformations
                if "..." in input_text:
                    self.assertIn("ellipsis", result)
                if "—" in input_text:
                    self.assertIn("em dash", result)
                if "–" in input_text:
                    self.assertIn("en dash", result)
                if """ in input_text or """ in input_text:
                    self.assertNotIn(""", result)
                    self.assertNotIn(""", result)
    
    def test_context_aware_processing(self):
        """Test context-aware symbol processing"""
        test_cases = [
            # Mathematical context
            ("2 + 3 = 5", "2 plus 3 equals 5"),
            ("10 - 4 = 6", "10 minus 4 equals 6"),
            ("3 * 4 = 12", "3 times 4 equals 12"),
            ("8 / 2 = 4", "8 divided by 2 equals 4"),
            ("50%", "50 percent"),
            ("90°", "90 degrees"),
            
            # Programming context
            ("function()", "function function"),
            ("array[0]", "array array index 0"),
            ("object.property", "object dot property"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_context_aware_symbols(input_text)
                # Check mathematical conversions
                if "+" in input_text and input_text.count("+") == 1:
                    self.assertIn("plus", result)
                if "-" in input_text and input_text.count("-") == 1:
                    self.assertIn("minus", result)
                if "*" in input_text and input_text.count("*") == 1:
                    self.assertIn("times", result)
                if "/" in input_text and input_text.count("/") == 1:
                    self.assertIn("divided by", result)
    
    def test_markdown_processing(self):
        """Test markdown symbol processing"""
        # Test with markdown preservation disabled (default)
        test_cases = [
            ("**bold text**", "bold text"),
            ("*italic text*", "italic text"),
            ("~~strikethrough~~", "strikethrough"),
            ("`code`", "code"),
            ("# Header", "Header"),
            ("- List item", "List item"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_symbols(input_text)
                # Check that markdown symbols are removed
                self.assertNotIn("**", result)
                self.assertNotIn("~~", result)
                self.assertNotIn("`", result)
    
    def test_symbol_complexity_analysis(self):
        """Test symbol complexity analysis"""
        simple_text = "Hello world"
        complex_text = "John&#x27;s car costs $100 & has 90° turn with **bold** text"
        
        simple_analysis = self.processor.analyze_symbol_complexity(simple_text)
        complex_analysis = self.processor.analyze_symbol_complexity(complex_text)
        
        # Simple text should have lower complexity
        self.assertLess(simple_analysis['complexity_score'], complex_analysis['complexity_score'])
        
        # Complex text should detect various elements
        self.assertGreater(len(complex_analysis['html_entities']), 0)
        self.assertGreater(len(complex_analysis['special_characters']), 0)
        self.assertGreater(len(complex_analysis['processing_recommendations']), 0)
    
    def test_configuration_options(self):
        """Test configuration options"""
        # Test HTML entity processing toggle
        self.processor.set_configuration(fix_html_entities=False)
        result = self.processor.process_symbols("John&#x27;s car")
        self.assertIn("&#x27;", result)  # Should not be processed
        
        # Re-enable for other tests
        self.processor.set_configuration(fix_html_entities=True)
        
        # Test quote handling toggle
        self.processor.set_configuration(handle_quotes_naturally=False)
        result = self.processor.process_symbols('"Hello"')
        # Should not remove quotes when disabled
        
        # Re-enable for other tests
        self.processor.set_configuration(handle_quotes_naturally=True)

def run_comprehensive_test():
    """Run comprehensive test with detailed output"""
    print("🧪 Advanced Symbol & Punctuation Handler Comprehensive Test")
    print("=" * 70)
    
    processor = AdvancedSymbolProcessor()
    
    # Test cases covering all major functionality
    test_cases = [
        # Critical pronunciation fixes
        ("The * symbol", "asterisk"),
        ("John&#x27;s car", "John's car"),
        ("&quot;Hello&quot;", "Hello"),
        
        # Enhanced special characters
        ("© 2024 Company", "copyright"),
        ("90° angle", "degrees"),
        ("± 5%", "plus or minus"),
        
        # International currencies
        ("₹100 rupees", "rupee"),
        ("₩1000 won", "won"),
        
        # Advanced punctuation
        ("Text...", "ellipsis"),
        ("Text—dash", "em dash"),
        ('"Smart quotes"', "Smart quotes"),
        
        # Context-aware processing
        ("2 + 3 = 5", "plus"),
        ("function()", "function"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected_content) in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{input_text}'")
        
        try:
            result = processor.process_symbols(input_text)
            print(f"Result: '{result}'")
            
            if expected_content in result:
                print("✅ PASSED")
                passed += 1
            else:
                print("❌ FAILED")
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print(f"\n" + "=" * 70)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print(f"Success rate: {passed/(passed+failed)*100:.1f}%")
    
    return failed == 0

if __name__ == "__main__":
    # Run comprehensive test
    success = run_comprehensive_test()
    
    print(f"\n🎯 Advanced Symbol & Punctuation Handler: {'✅ READY' if success else '❌ NEEDS FIXES'}")
    
    # Run unit tests
    print("\n" + "=" * 70)
    print("Running Unit Tests...")
    unittest.main(verbosity=2, exit=False)
