#!/usr/bin/env python3
"""
Test suite for Enhanced DateTime Processor
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from LiteTTS.nlp.enhanced_datetime_processor import EnhancedDateTimeProcessor

class TestEnhancedDateTimeProcessor(unittest.TestCase):
    """Test cases for Enhanced DateTime Processor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = EnhancedDateTimeProcessor()
    
    def test_iso_date_processing(self):
        """Test ISO date format processing (critical fix)"""
        test_cases = [
            ("2023-05-12", "May twelfth, twenty twenty-three"),
            ("2024-01-01", "January first, twenty twenty-four"),
            ("2023-12-25", "December twenty-fifth, twenty twenty-three"),
            ("2000-02-29", "February twenty-ninth, two thousand"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_dates_and_times(input_text)
                self.assertEqual(result, expected)
    
    def test_written_dates_with_ordinals(self):
        """Test written dates with ordinal indicators"""
        test_cases = [
            ("January 1st, 2024", "January first, twenty twenty-four"),
            ("March 22nd, 2023", "March twenty-second, twenty twenty-three"),
            ("April 3rd, 2024", "April third, twenty twenty-four"),
            ("December 15th, 2023", "December fifteenth, twenty twenty-three"),
            ("Feb. 29th, 2024", "February twenty-ninth, twenty twenty-four"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_dates_and_times(input_text)
                self.assertEqual(result, expected)
    
    def test_time_range_processing(self):
        """Test enhanced time range processing"""
        test_cases = [
            ("9:00-17:00", "nine o'clock AM to five o'clock PM"),
            ("14:30-16:45", "half past two PM to quarter to five PM"),
            ("9:00 AM - 5:00 PM", "nine o'clock AM to five o'clock PM"),
            ("2 PM - 6 PM", "two o'clock PM to six o'clock PM"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_dates_and_times(input_text)
                self.assertEqual(result, expected)
    
    def test_24_hour_time_conversion(self):
        """Test 24-hour time format conversion"""
        test_cases = [
            ("14:30", "half past two PM"),
            ("09:00", "nine o'clock AM"),
            ("23:45", "quarter to twelve PM"),
            ("00:15", "quarter past twelve AM"),
            ("12:00", "twelve o'clock PM"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_dates_and_times(input_text)
                self.assertEqual(result, expected)
    
    def test_12_hour_time_processing(self):
        """Test 12-hour time format processing"""
        test_cases = [
            ("3:30 PM", "half past three PM"),
            ("9:00 AM", "nine o'clock AM"),
            ("11:45 PM", "quarter to twelve PM"),
            ("12:15 AM", "quarter past twelve AM"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_dates_and_times(input_text)
                self.assertEqual(result, expected)
    
    def test_various_date_formats(self):
        """Test various date format processing"""
        test_cases = [
            ("12/25/2023", "December twenty-fifth, twenty twenty-three"),
            ("25.12.2023", "December twenty-fifth, twenty twenty-three"),
            ("12-25-2023", "December twenty-fifth, twenty twenty-three"),
            ("12/25/23", "December twenty-fifth, twenty twenty-three"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_dates_and_times(input_text)
                self.assertEqual(result, expected)
    
    def test_mixed_content(self):
        """Test mixed date and time content"""
        test_cases = [
            ("Meeting on 2023-05-12 at 14:30", "Meeting on May twelfth, twenty twenty-three at half past two PM"),
            ("Event: January 1st, 2024 from 9:00-17:00", "Event: January first, twenty twenty-four from nine o'clock AM to five o'clock PM"),
            ("Deadline: March 15th, 2024 by 23:59", "Deadline: March fifteenth, twenty twenty-four by eleven fifty-nine PM"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_dates_and_times(input_text)
                self.assertEqual(result, expected)
    
    def test_ordinal_conversion(self):
        """Test ordinal number conversion"""
        test_cases = [
            ("1", "first"),
            ("2", "second"),
            ("3", "third"),
            ("21", "twenty-first"),
            ("22", "twenty-second"),
            ("31", "thirty-first"),
        ]
        
        for day, expected in test_cases:
            with self.subTest(day=day):
                result = self.processor._get_ordinal_day(day)
                self.assertEqual(result, expected)
    
    def test_year_formatting(self):
        """Test year formatting"""
        test_cases = [
            ("1995", "nineteen ninety-five"),
            ("2005", "two thousand five"),
            ("2023", "twenty twenty-three"),
            ("2000", "two thousand"),
        ]
        
        for year, expected in test_cases:
            with self.subTest(year=year):
                result = self.processor._format_year(year)
                self.assertEqual(result, expected)
    
    def test_edge_cases(self):
        """Test edge cases and special scenarios"""
        test_cases = [
            ("2024-02-29", "February twenty-ninth, twenty twenty-four"),  # Leap year
            ("2023-02-28", "February twenty-eighth, twenty twenty-three"),  # Non-leap year
            ("00:00", "twelve o'clock AM"),  # Midnight
            ("12:00", "twelve o'clock PM"),  # Noon
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.processor.process_dates_and_times(input_text)
                self.assertEqual(result, expected)

def run_comprehensive_test():
    """Run comprehensive test with detailed output"""
    print("🧪 Enhanced DateTime Processor Comprehensive Test")
    print("=" * 60)
    
    processor = EnhancedDateTimeProcessor()
    
    # Test cases from the original assessment
    test_cases = [
        # Critical ISO date fixes
        ("2023-05-12", "May twelfth, twenty twenty-three"),
        ("2024-01-01", "January first, twenty twenty-four"),
        
        # Ordinal date processing (major improvement)
        ("January 1st, 2024", "January first, twenty twenty-four"),
        ("March 22nd, 2023", "March twenty-second, twenty twenty-three"),
        
        # Enhanced time range processing
        ("9:00-17:00", "nine o'clock AM to five o'clock PM"),
        ("14:30-16:45", "half past two PM to quarter to five PM"),
        
        # 24-hour time conversion
        ("14:30", "half past two PM"),
        ("09:00", "nine o'clock AM"),
        ("23:45", "quarter to twelve PM"),
        
        # Mixed content
        ("Meeting on 2023-05-12 at 14:30", "Meeting on May twelfth, twenty twenty-three at half past two PM"),
        ("Deadline: March 15th, 2024 by 23:59", "Deadline: March fifteenth, twenty twenty-four by eleven fifty-nine PM"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{input_text}'")
        print(f"Expected: '{expected}'")
        
        try:
            result = processor.process_dates_and_times(input_text)
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
    
    print(f"\n🎯 Enhanced DateTime Processor: {'✅ READY' if success else '❌ NEEDS FIXES'}")
    
    # Run unit tests
    print("\n" + "=" * 60)
    print("Running Unit Tests...")
    unittest.main(verbosity=2, exit=False)
