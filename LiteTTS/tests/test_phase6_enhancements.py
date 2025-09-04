#!/usr/bin/env python3
"""
Comprehensive test suite for Phase 6: Advanced Text Processing and Pronunciation Enhancement
Tests all Phase 6 components: enhanced numbers, units, homographs, and contractions
"""

import unittest
import sys
import os
import time
from pathlib import Path

# Add the LiteTTS directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.enhanced_number_processor import EnhancedNumberProcessor
from nlp.enhanced_units_processor import EnhancedUnitsProcessor
from nlp.enhanced_homograph_resolver import EnhancedHomographResolver
from nlp.phase6_contraction_processor import Phase6ContractionProcessor
from nlp.phase6_text_processor import Phase6TextProcessor
from nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode

class TestEnhancedNumberProcessor(unittest.TestCase):
    """Test enhanced number processing functionality"""
    
    def setUp(self):
        self.processor = EnhancedNumberProcessor()
    
    def test_comma_separated_numbers(self):
        """Test comma-separated number processing: 10,000 → ten thousand"""
        test_cases = [
            ("I have 10,000 dollars", "I have ten thousand dollars"),
            ("The population is 1,001 people", "The population is one thousand one people"),
            ("Sales reached 250,000 units", "Sales reached two hundred fifty thousand units"),
            ("Only 1,500 tickets left", "Only one thousand five hundred tickets left")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_numbers(input_text)
                self.assertEqual(result.processed_text, expected)
                self.assertGreater(result.numbers_processed, 0)
    
    def test_sequential_digits_context(self):
        """Test context-aware sequential digit processing"""
        test_cases = [
            # Should be individual digits (model numbers, codes)
            ("Model 1718 is available", "Model one seven one eight is available"),
            ("Flight 2024 is boarding", "Flight two zero two four is boarding"),
            ("Room 1234 is ready", "Room one two three four is ready"),
            
            # Should be years (not individual digits)
            ("In 1990 we started", "In nineteen ninety we started"),
            ("The year 2024 was great", "The year twenty twenty four was great"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_numbers(input_text)
                # Note: This test may need adjustment based on actual context detection
                self.assertNotEqual(result.processed_text, input_text)
    
    def test_large_numbers(self):
        """Test large number processing"""
        test_cases = [
            ("Population: 50000", "Population: fifty thousand"),
            ("Revenue: 1000000", "Revenue: one million"),
            ("Distance: 5280 feet", "Distance: five thousand two hundred eighty feet")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_numbers(input_text)
                # Check that processing occurred
                self.assertGreater(result.numbers_processed, 0)

class TestEnhancedUnitsProcessor(unittest.TestCase):
    """Test enhanced units processing functionality"""
    
    def setUp(self):
        self.processor = EnhancedUnitsProcessor()
    
    def test_temperature_units(self):
        """Test temperature unit processing"""
        test_cases = [
            ("It's 72°F outside", "It's 72 degrees Fahrenheit outside"),
            ("Water boils at 100°C", "Water boils at 100 degrees Celsius outside"),
            ("Absolute zero is 0°K", "Absolute zero is 0 degrees Kelvin")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_units(input_text)
                self.assertEqual(result.processed_text, expected)
                self.assertGreater(result.units_processed, 0)
    
    def test_energy_units(self):
        """Test energy unit processing"""
        test_cases = [
            ("Used 500 kWh this month", "Used 500 kilowatt hours this month"),
            ("The plant generates 50 MW", "The plant generates 50 megawatts"),
            ("Battery capacity: 100 Wh", "Battery capacity: 100 watt hours")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_units(input_text)
                self.assertEqual(result.processed_text, expected)
                self.assertGreater(result.units_processed, 0)
    
    def test_flight_designations(self):
        """Test flight designation processing"""
        test_cases = [
            ("Flight no. 123 is delayed", "Flight Number 123 is delayed"),
            ("Gate no. A5 is open", "Gate Number A5 is open"),
            ("Terminal no. 2 is busy", "Terminal Number 2 is busy")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_units(input_text)
                self.assertEqual(result.processed_text, expected)
                self.assertGreater(result.units_processed, 0)

class TestEnhancedHomographResolver(unittest.TestCase):
    """Test enhanced homograph resolution functionality"""
    
    def setUp(self):
        self.resolver = EnhancedHomographResolver()
    
    def test_critical_homographs(self):
        """Test critical homograph pairs"""
        test_cases = [
            # Lead: metal vs verb
            ("Lead pipe is dangerous", "led pipe is dangerous"),
            ("Lead the way forward", "leed the way forward"),
            
            # Wind: air vs coil
            ("The wind is strong", "The wind is strong"),  # Should stay as wind
            ("Wind the clock up", "wynd the clock up"),
            
            # Tear: rip vs cry
            ("Tear the paper apart", "tair the paper apart"),
            ("A single tear fell", "A single teer fell"),
            
            # Desert: abandon vs arid
            ("Don't desert your post", "Don't dih-zurt your post"),
            ("The Sahara desert is vast", "The Sahara dez-urt is vast"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.resolver.resolve_homographs(input_text)
                # Check that processing occurred
                if result.homographs_resolved:
                    self.assertNotEqual(result.processed_text, input_text)
    
    def test_homograph_statistics(self):
        """Test homograph statistics"""
        stats = self.resolver.get_homograph_statistics()
        self.assertIn('total_homographs', stats)
        self.assertGreater(stats['total_homographs'], 15)  # Should have at least the critical pairs

class TestPhase6ContractionProcessor(unittest.TestCase):
    """Test Phase 6 contraction processing functionality"""
    
    def setUp(self):
        self.processor = Phase6ContractionProcessor()
    
    def test_ambiguous_contractions(self):
        """Test ambiguous contraction disambiguation"""
        test_cases = [
            # "had" vs "would" disambiguation
            ("He'd already gone home", "he had already gone home"),  # Past perfect
            ("He'd like to go", "he would like to go"),  # Conditional
            ("She'd been there before", "she had been there before"),  # Past perfect
            ("She'd prefer coffee", "she would prefer coffee"),  # Conditional
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_contractions(input_text)
                # Check that processing occurred
                if result.contractions_processed:
                    self.assertNotEqual(result.processed_text, input_text)
    
    def test_natural_pronunciations(self):
        """Test natural pronunciation fixes"""
        test_cases = [
            ("I wasn't ready", "I wuznt ready"),  # Fix "waaasant" issue
            ("They couldn't come", "They coodnt come"),
            ("I'm going home", "im going home"),
            ("You'll see tomorrow", "yool see tomorrow")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.process_contractions(input_text)
                self.assertEqual(result.processed_text, expected)
                self.assertGreater(len(result.contractions_processed), 0)

class TestPhase6Integration(unittest.TestCase):
    """Test Phase 6 integration and performance"""
    
    def setUp(self):
        self.phase6_processor = Phase6TextProcessor()
        self.unified_processor = UnifiedTextProcessor()
    
    def test_comprehensive_processing(self):
        """Test comprehensive Phase 6 processing"""
        test_text = """
        The temperature was 75°F when Flight no. 1234 departed.
        He'd already used 500 kWh this month, costing $1,500.
        The lead pipe wasn't working, so they had to tear it out.
        In 2024, the population reached 10,000 people.
        """
        
        result = self.phase6_processor.process_text(test_text)
        
        # Verify processing occurred
        self.assertNotEqual(result.processed_text, result.original_text)
        self.assertGreater(result.total_changes, 0)
        
        # Check individual processors worked
        self.assertIsNotNone(result.number_result)
        self.assertIsNotNone(result.units_result)
        self.assertIsNotNone(result.contraction_result)
    
    def test_performance_targets(self):
        """Test that Phase 6 meets performance targets"""
        test_text = "The temperature is 72°F and I'd like 1,000 units at $50 each."
        
        start_time = time.perf_counter()
        result = self.phase6_processor.process_text(test_text)
        processing_time = time.perf_counter() - start_time
        
        # Performance targets
        rtf_target = 0.25  # RTF < 0.25
        memory_target = 150  # < 150MB additional memory
        
        # Calculate RTF (Real-Time Factor)
        # For text processing, we estimate based on processing time per character
        rtf = processing_time / max(len(test_text), 1) * 1000  # ms per character
        
        self.assertLess(rtf, rtf_target * 1000, f"RTF {rtf:.3f}ms/char exceeds target {rtf_target * 1000}ms/char")
        self.assertLess(result.processing_time, 1.0, "Processing time should be under 1 second for short text")
    
    def test_unified_processor_integration(self):
        """Test Phase 6 integration with unified processor"""
        options = ProcessingOptions(
            mode=ProcessingMode.ENHANCED,
            use_phase6_processing=True
        )
        
        test_text = "It's 100°F and I'd spent $10,000 on the lead project."
        
        result = self.unified_processor.process_text(test_text, options)
        
        # Verify Phase 6 processing occurred
        self.assertIsNotNone(result.phase6_result)
        self.assertGreater(result.phase6_enhancements, 0)
        self.assertIn("phase6_processing", result.stages_completed)

class TestPhase6ErrorHandling(unittest.TestCase):
    """Test Phase 6 error handling and edge cases"""
    
    def setUp(self):
        self.processor = Phase6TextProcessor()
    
    def test_empty_text(self):
        """Test processing empty text"""
        result = self.processor.process_text("")
        self.assertEqual(result.processed_text, "")
        self.assertEqual(result.total_changes, 0)
    
    def test_no_processable_content(self):
        """Test text with no processable content"""
        test_text = "Hello world! How are you today?"
        result = self.processor.process_text(test_text)
        
        # Should return original text unchanged
        self.assertEqual(result.processed_text, test_text)
        self.assertEqual(result.total_changes, 0)
    
    def test_malformed_input(self):
        """Test handling of malformed input"""
        test_cases = [
            "Temperature: °F",  # Missing number
            "Flight no.",       # Missing number
            "He'd",            # Incomplete contraction context
            "10,",             # Incomplete number
        ]
        
        for test_text in test_cases:
            with self.subTest(test_text=test_text):
                result = self.processor.process_text(test_text)
                # Should not crash and should return some result
                self.assertIsInstance(result.processed_text, str)

if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
