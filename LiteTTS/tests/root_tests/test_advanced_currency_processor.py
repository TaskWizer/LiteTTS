#!/usr/bin/env python3
"""
Test suite for Advanced Currency Processor
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from LiteTTS.nlp.advanced_currency_processor import AdvancedCurrencyProcessor, FinancialContext

class TestAdvancedCurrencyProcessor(unittest.TestCase):
    """Test cases for Advanced Currency Processor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = AdvancedCurrencyProcessor()
        self.context = FinancialContext()
    
    def test_basic_currency_amounts(self):
        """Test basic currency amount processing"""
        test_cases = [
            ("$100", "one hundred dollars"),
            ("$1", "one dollar"),
            ("$25.50", "twenty five dollars and fifty cents"),
            ("€100", "one hundred euros"),
            ("£75.25", "seventy five pounds and twenty five pence"),
            ("¥1000", "one thousand yen"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_currency_text(input_text, self.context)
                self.assertEqual(result, expected)
    
    def test_large_amounts_with_commas(self):
        """Test large currency amounts with commas"""
        test_cases = [
            ("$1,000", "one thousand dollars"),
            ("$5,681.52", "five thousand six hundred eighty one dollars and fifty two cents"),
            ("$1,234,567.89", "one million two hundred thirty four thousand five hundred sixty seven dollars and eighty nine cents"),
            ("€2,500.75", "two thousand five hundred euros and seventy five cents"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_currency_text(input_text, self.context)
                self.assertEqual(result, expected)
    
    def test_currency_with_suffixes(self):
        """Test currency amounts with financial suffixes"""
        test_cases = [
            ("$2.5M", "two point five million dollars"),
            ("$1.2B", "one point two billion dollars"),
            ("€500K", "five hundred thousand euros"),
            ("£3.7T", "three point seven trillion pounds"),
            ("$10m", "ten million dollars"),  # lowercase
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_currency_text(input_text, self.context)
                self.assertEqual(result, expected)
    
    def test_approximate_amounts(self):
        """Test approximate currency amounts"""
        test_cases = [
            ("~$568.91", "approximately five hundred sixty eight dollars and ninety one cents"),
            ("~ $1,000", "approximately one thousand dollars"),
            ("~€250.50", "approximately two hundred fifty euros and fifty cents"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_currency_text(input_text, self.context)
                self.assertEqual(result, expected)
    
    def test_negative_amounts(self):
        """Test negative currency amounts"""
        test_cases = [
            ("-$50", "negative fifty dollars"),
            ("($100)", "negative one hundred dollars"),
            ("-$25.75", "negative twenty five dollars and seventy five cents"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_currency_text(input_text, self.context)
                self.assertEqual(result, expected)
    
    def test_financial_terms(self):
        """Test financial terminology processing"""
        test_cases = [
            ("25 bps increase", "25 basis points increase"),
            ("Q1 results", "first quarter results"),
            ("YoY growth", "year over year growth"),
            ("P/E ratio", "price to earnings ratio"),
            ("EBITDA margin", "E B I T D A margin"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_currency_text(input_text, self.context)
                self.assertEqual(result, expected)
    
    def test_mixed_content(self):
        """Test mixed currency and text content"""
        test_cases = [
            ("The stock price is $45.67", "The stock price is forty five dollars and sixty seven cents"),
            ("Revenue of $2.5M vs $1.8M", "Revenue of two point five million dollars vs one point eight million dollars"),
            ("Market cap: $1.2B", "Market cap: one point two billion dollars"),
            ("Loss of ($500K)", "Loss of negative five hundred thousand dollars"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_currency_text(input_text, self.context)
                self.assertEqual(result, expected)
    
    def test_edge_cases(self):
        """Test edge cases and special scenarios"""
        test_cases = [
            ("$0.01", "one cent"),
            ("$0.99", "ninety nine cents"),
            ("$1000000", "one million dollars"),
            ("€0", "zero euros"),
            ("$123.4", "one hundred twenty three dollars and forty cents"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_currency_text(input_text, self.context)
                self.assertEqual(result, expected)
    
    def test_international_currencies(self):
        """Test various international currencies"""
        test_cases = [
            ("₹500", "five hundred rupees"),
            ("₽1000", "one thousand rubles"),
            ("₩50000", "fifty thousand won"),
            ("¢75", "seventy five cents"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_currency_text(input_text, self.context)
                self.assertEqual(result, expected)
    
    def test_number_to_words(self):
        """Test number-to-words conversion"""
        test_cases = [
            (0, "zero"),
            (1, "one"),
            (21, "twenty one"),
            (100, "one hundred"),
            (1000, "one thousand"),
            (1234567, "one million two hundred thirty four thousand five hundred sixty seven"),
        ]
        
        for num, expected in test_cases:
            with self.subTest(number=num):
                result = self.processor._number_to_words(num)
                self.assertEqual(result, expected)
    
    def test_currency_analysis(self):
        """Test currency content analysis"""
        text = "The company reported $2.5M revenue and €1.2B market cap with 25 bps margin."
        analysis = self.processor.analyze_currency_content(text)
        
        self.assertGreater(len(analysis['currency_amounts']), 0)
        self.assertGreater(len(analysis['financial_terms']), 0)
        self.assertGreater(analysis['complexity_score'], 0)
        self.assertIn('Currency amount normalization', analysis['processing_opportunities'])
    
    def test_configuration(self):
        """Test processor configuration"""
        # Test disabling suffix processing
        self.processor.set_configuration(enable_suffix_processing=False)
        result = self.processor.process_currency_text("$2.5M", self.context)
        # Should not process suffix when disabled
        self.assertIn("M", result)
        
        # Re-enable for other tests
        self.processor.set_configuration(enable_suffix_processing=True)
    
    def test_supported_currencies(self):
        """Test supported currency list"""
        currencies = self.processor.get_supported_currencies()
        expected_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'RUB', 'KRW']
        
        for currency in expected_currencies:
            self.assertIn(currency, currencies)

def run_comprehensive_test():
    """Run comprehensive test with detailed output"""
    print("🧪 Advanced Currency Processor Comprehensive Test")
    print("=" * 60)
    
    processor = AdvancedCurrencyProcessor()
    context = FinancialContext()
    
    # Test cases from the original assessment
    test_cases = [
        # Critical fixes from assessment
        ("$568.91", "five hundred sixty eight dollars and ninety one cents"),
        ("$5,681.52", "five thousand six hundred eighty one dollars and fifty two cents"),
        ("$1,234,567.89", "one million two hundred thirty four thousand five hundred sixty seven dollars and eighty nine cents"),
        
        # Currency suffixes (major improvement)
        ("$2.5M", "two point five million dollars"),
        ("Revenue of $2.5M", "Revenue of two point five million dollars"),
        ("$1.2B market cap", "one point two billion dollars market cap"),
        
        # International currencies
        ("€100.50", "one hundred euros and fifty cents"),
        ("£75.25", "seventy five pounds and twenty five pence"),
        ("¥1000", "one thousand yen"),
        
        # Approximate values
        ("~$568.91", "approximately five hundred sixty eight dollars and ninety one cents"),
        
        # Negative amounts
        ("-$50", "negative fifty dollars"),
        ("($100)", "negative one hundred dollars"),
        
        # Financial terms
        ("25 bps", "25 basis points"),
        ("Q1 results", "first quarter results"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{input_text}'")
        print(f"Expected: '{expected}'")
        
        try:
            result = processor.process_currency_text(input_text, context)
            print(f"Actual:   '{result}'")
            
            if result == expected:
                print("✅ PASSED")
                passed += 1
            else:
                print("❌ FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print(f"\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print(f"Success rate: {passed/(passed+failed)*100:.1f}%")
    
    return failed == 0

if __name__ == "__main__":
    # Run comprehensive test
    success = run_comprehensive_test()
    
    print(f"\n🎯 Advanced Currency Processor: {'✅ READY' if success else '❌ NEEDS FIXES'}")
    
    # Run unit tests
    print("\n" + "=" * 60)
    print("Running Unit Tests...")
    unittest.main(verbosity=2, exit=False)
