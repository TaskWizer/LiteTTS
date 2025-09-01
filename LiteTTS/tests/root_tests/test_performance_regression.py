#!/usr/bin/env python3
"""
Performance regression testing for TTS pronunciation fixes
Ensures that new fixes don't break existing functionality or degrade performance
"""

import sys
import os
import unittest
import time
import memory_profiler
from pathlib import Path
from typing import Dict, List, Tuple
import statistics

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.nlp.enhanced_contraction_processor import EnhancedContractionProcessor
from LiteTTS.nlp.advanced_symbol_processor import AdvancedSymbolProcessor
from LiteTTS.nlp.extended_pronunciation_dictionary import ExtendedPronunciationDictionary
from LiteTTS.nlp.voice_modulation_system import VoiceModulationSystem
from LiteTTS.nlp.enhanced_datetime_processor import EnhancedDateTimeProcessor
from LiteTTS.nlp.advanced_abbreviation_handler import AdvancedAbbreviationHandler
from LiteTTS.nlp.dynamic_emotion_intonation import DynamicEmotionIntonationSystem

# Try to import existing components for comparison
try:
    from LiteTTS.nlp.text_normalizer import TextNormalizer
    from LiteTTS.nlp.processor import NLPProcessor
    EXISTING_COMPONENTS_AVAILABLE = True
except ImportError:
    EXISTING_COMPONENTS_AVAILABLE = False

class PerformanceBenchmark:
    """Performance benchmarking utility"""
    
    def __init__(self):
        self.results = {}
    
    def time_function(self, func, *args, iterations=100, **kwargs):
        """Time a function execution"""
        times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'result': result
        }
    
    def memory_usage(self, func, *args, **kwargs):
        """Measure memory usage of a function"""
        def wrapper():
            return func(*args, **kwargs)
        
        mem_usage = memory_profiler.memory_usage(wrapper, interval=0.1)
        return {
            'peak_memory': max(mem_usage),
            'memory_increase': max(mem_usage) - min(mem_usage),
            'average_memory': statistics.mean(mem_usage)
        }

class TestPerformanceRegression(unittest.TestCase):
    """Test performance regression for all new components"""
    
    def setUp(self):
        self.benchmark = PerformanceBenchmark()
        
        # Initialize new components
        self.contraction_processor = EnhancedContractionProcessor()
        self.symbol_processor = AdvancedSymbolProcessor()
        self.pronunciation_dict = ExtendedPronunciationDictionary()
        self.voice_modulation = VoiceModulationSystem()
        self.datetime_processor = EnhancedDateTimeProcessor()
        self.abbreviation_handler = AdvancedAbbreviationHandler()
        self.emotion_system = DynamicEmotionIntonationSystem()
        
        # Initialize existing components if available
        if EXISTING_COMPONENTS_AVAILABLE:
            self.text_normalizer = TextNormalizer()
            self.nlp_processor = NLPProcessor()
        
        # Test data sets
        self.test_texts = self._load_test_texts()
    
    def _load_test_texts(self) -> Dict[str, List[str]]:
        """Load test texts of various sizes and complexities"""
        return {
            'short': [
                "Hello world!",
                "I'll be there.",
                "What time is it?",
                "That's amazing!",
                "Call me ASAP.",
            ],
            'medium': [
                "I'll update my resume by 2023-10-27. The FAQ says to contact Dr. Smith ASAP.",
                "What do you think about the new API? It's really amazing!",
                "The * symbol represents multiplication & the % symbol represents percentage.",
                "Please read the documentation (it's very important) before proceeding.",
                "We'll meet at 14:30 on 2024-01-15 to discuss the project.",
            ],
            'long': [
                """I'll update my resume by 2023-10-27. The FAQ says to contact Dr. Smith ASAP.
                "That's amazing!" she said (imagine this whispered). What do you think?
                The * symbol represents multiplication & the % symbol represents percentage.
                We'll meet at 14:30 on 2024-01-15 to discuss the new API documentation.
                It's really incredible how much progress we've made! Don't you agree?
                Please review the HTML & CSS files before the meeting. The URL is in the email.""",
                
                """Dr. Johnson won't be available until 2024-02-15 at 09:00 AM.
                The CEO said "We'll achieve our goals ASAP" during the meeting.
                What's the status of the SQL database? It's been running slowly.
                The FAQ mentions that you'll need to update your password (very important).
                I'd recommend checking the API documentation & the XML configuration files.
                That's absolutely fantastic! How did you manage to fix the bug so quickly?""",
                
                """The nuclear power plant's safety protocols are extremely important.
                Dr. Smith's resume includes experience with asterisk (*) notation systems.
                We'll schedule the meeting for Wednesday, February 14th, 2024 at 3:30 PM.
                "I can't believe it's working!" she exclaimed (with obvious excitement).
                The HTML parser couldn't handle the & symbol in the XML document.
                What's your opinion on the new UI? It's really user-friendly, isn't it?""",
            ]
        }
    
    def test_contraction_processing_performance(self):
        """Test contraction processing performance"""
        print("\n=== Contraction Processing Performance ===")
        
        for size, texts in self.test_texts.items():
            for i, text in enumerate(texts):
                # Test new enhanced processor
                new_result = self.benchmark.time_function(
                    self.contraction_processor.process_contractions, 
                    text, iterations=50
                )
                
                print(f"{size.capitalize()} text {i+1}:")
                print(f"  Enhanced processor: {new_result['mean']:.4f}s ± {new_result['std_dev']:.4f}s")
                
                # Ensure reasonable performance (should be under 10ms for short texts)
                if size == 'short':
                    self.assertLess(new_result['mean'], 0.01, 
                                  f"Contraction processing too slow for short text: {new_result['mean']:.4f}s")
                elif size == 'medium':
                    self.assertLess(new_result['mean'], 0.05,
                                  f"Contraction processing too slow for medium text: {new_result['mean']:.4f}s")
                elif size == 'long':
                    self.assertLess(new_result['mean'], 0.1,
                                  f"Contraction processing too slow for long text: {new_result['mean']:.4f}s")
    
    def test_symbol_processing_performance(self):
        """Test symbol processing performance"""
        print("\n=== Symbol Processing Performance ===")
        
        for size, texts in self.test_texts.items():
            for i, text in enumerate(texts):
                # Test new advanced processor
                new_result = self.benchmark.time_function(
                    self.symbol_processor.process_symbols, 
                    text, iterations=50
                )
                
                print(f"{size.capitalize()} text {i+1}:")
                print(f"  Advanced processor: {new_result['mean']:.4f}s ± {new_result['std_dev']:.4f}s")
                
                # Ensure reasonable performance
                if size == 'short':
                    self.assertLess(new_result['mean'], 0.01)
                elif size == 'medium':
                    self.assertLess(new_result['mean'], 0.05)
                elif size == 'long':
                    self.assertLess(new_result['mean'], 0.1)
    
    def test_pronunciation_dictionary_performance(self):
        """Test pronunciation dictionary performance"""
        print("\n=== Pronunciation Dictionary Performance ===")
        
        for size, texts in self.test_texts.items():
            for i, text in enumerate(texts):
                # Test new extended dictionary
                new_result = self.benchmark.time_function(
                    self.pronunciation_dict.process_text_pronunciations, 
                    text, iterations=50
                )
                
                print(f"{size.capitalize()} text {i+1}:")
                print(f"  Extended dictionary: {new_result['mean']:.4f}s ± {new_result['std_dev']:.4f}s")
                
                # Ensure reasonable performance
                if size == 'short':
                    self.assertLess(new_result['mean'], 0.02)
                elif size == 'medium':
                    self.assertLess(new_result['mean'], 0.1)
                elif size == 'long':
                    self.assertLess(new_result['mean'], 0.2)
    
    def test_datetime_processing_performance(self):
        """Test date/time processing performance"""
        print("\n=== Date/Time Processing Performance ===")
        
        for size, texts in self.test_texts.items():
            for i, text in enumerate(texts):
                # Test new enhanced processor
                new_result = self.benchmark.time_function(
                    self.datetime_processor.process_dates_and_times, 
                    text, iterations=50
                )
                
                print(f"{size.capitalize()} text {i+1}:")
                print(f"  Enhanced processor: {new_result['mean']:.4f}s ± {new_result['std_dev']:.4f}s")
                
                # Ensure reasonable performance
                if size == 'short':
                    self.assertLess(new_result['mean'], 0.01)
                elif size == 'medium':
                    self.assertLess(new_result['mean'], 0.05)
                elif size == 'long':
                    self.assertLess(new_result['mean'], 0.1)
    
    def test_abbreviation_handling_performance(self):
        """Test abbreviation handling performance"""
        print("\n=== Abbreviation Handling Performance ===")
        
        for size, texts in self.test_texts.items():
            for i, text in enumerate(texts):
                # Test new advanced handler
                new_result = self.benchmark.time_function(
                    self.abbreviation_handler.process_abbreviations, 
                    text, iterations=50
                )
                
                print(f"{size.capitalize()} text {i+1}:")
                print(f"  Advanced handler: {new_result['mean']:.4f}s ± {new_result['std_dev']:.4f}s")
                
                # Ensure reasonable performance
                if size == 'short':
                    self.assertLess(new_result['mean'], 0.01)
                elif size == 'medium':
                    self.assertLess(new_result['mean'], 0.05)
                elif size == 'long':
                    self.assertLess(new_result['mean'], 0.1)
    
    def test_emotion_intonation_performance(self):
        """Test emotion/intonation processing performance"""
        print("\n=== Emotion/Intonation Processing Performance ===")
        
        for size, texts in self.test_texts.items():
            for i, text in enumerate(texts):
                # Test new dynamic system
                new_result = self.benchmark.time_function(
                    self.emotion_system.process_emotion_intonation, 
                    text, iterations=50
                )
                
                print(f"{size.capitalize()} text {i+1}:")
                print(f"  Dynamic system: {new_result['mean']:.4f}s ± {new_result['std_dev']:.4f}s")
                
                # Ensure reasonable performance
                if size == 'short':
                    self.assertLess(new_result['mean'], 0.02)
                elif size == 'medium':
                    self.assertLess(new_result['mean'], 0.1)
                elif size == 'long':
                    self.assertLess(new_result['mean'], 0.2)
    
    def test_voice_modulation_performance(self):
        """Test voice modulation performance"""
        print("\n=== Voice Modulation Performance ===")
        
        for size, texts in self.test_texts.items():
            for i, text in enumerate(texts):
                # Test new voice modulation system
                new_result = self.benchmark.time_function(
                    self.voice_modulation.process_voice_modulation, 
                    text, iterations=50
                )
                
                print(f"{size.capitalize()} text {i+1}:")
                print(f"  Voice modulation: {new_result['mean']:.4f}s ± {new_result['std_dev']:.4f}s")
                
                # Ensure reasonable performance
                if size == 'short':
                    self.assertLess(new_result['mean'], 0.01)
                elif size == 'medium':
                    self.assertLess(new_result['mean'], 0.05)
                elif size == 'long':
                    self.assertLess(new_result['mean'], 0.1)
    
    def test_integrated_processing_performance(self):
        """Test integrated processing performance"""
        print("\n=== Integrated Processing Performance ===")
        
        def process_with_all_components(text):
            """Process text through all new components"""
            # Process through all components in order
            text = self.symbol_processor.process_symbols(text)
            text = self.contraction_processor.process_contractions(text)
            text = self.pronunciation_dict.process_text_pronunciations(text)
            text = self.datetime_processor.process_dates_and_times(text)
            text = self.abbreviation_handler.process_abbreviations(text)
            processed_text, markers = self.emotion_system.process_emotion_intonation(text)
            return processed_text
        
        for size, texts in self.test_texts.items():
            for i, text in enumerate(texts):
                # Test integrated processing
                integrated_result = self.benchmark.time_function(
                    process_with_all_components, 
                    text, iterations=20
                )
                
                print(f"{size.capitalize()} text {i+1}:")
                print(f"  Integrated processing: {integrated_result['mean']:.4f}s ± {integrated_result['std_dev']:.4f}s")
                
                # Ensure reasonable performance for integrated processing
                if size == 'short':
                    self.assertLess(integrated_result['mean'], 0.1,
                                  f"Integrated processing too slow for short text: {integrated_result['mean']:.4f}s")
                elif size == 'medium':
                    self.assertLess(integrated_result['mean'], 0.5,
                                  f"Integrated processing too slow for medium text: {integrated_result['mean']:.4f}s")
                elif size == 'long':
                    self.assertLess(integrated_result['mean'], 1.0,
                                  f"Integrated processing too slow for long text: {integrated_result['mean']:.4f}s")
    
    @unittest.skipUnless(EXISTING_COMPONENTS_AVAILABLE, "Existing components not available for comparison")
    def test_comparison_with_existing_components(self):
        """Compare performance with existing components"""
        print("\n=== Comparison with Existing Components ===")
        
        for size, texts in self.test_texts.items():
            for i, text in enumerate(texts):
                # Test existing text normalizer
                existing_result = self.benchmark.time_function(
                    self.text_normalizer.normalize_text, 
                    text, iterations=50
                )
                
                # Test new integrated processing
                def new_processing(text):
                    text = self.symbol_processor.process_symbols(text)
                    text = self.contraction_processor.process_contractions(text)
                    return text
                
                new_result = self.benchmark.time_function(
                    new_processing, 
                    text, iterations=50
                )
                
                print(f"{size.capitalize()} text {i+1}:")
                print(f"  Existing normalizer: {existing_result['mean']:.4f}s ± {existing_result['std_dev']:.4f}s")
                print(f"  New processing: {new_result['mean']:.4f}s ± {new_result['std_dev']:.4f}s")
                print(f"  Performance ratio: {new_result['mean'] / existing_result['mean']:.2f}x")
                
                # Ensure new processing isn't more than 3x slower than existing
                self.assertLess(new_result['mean'] / existing_result['mean'], 3.0,
                              f"New processing significantly slower than existing: {new_result['mean'] / existing_result['mean']:.2f}x")
    
    def test_memory_usage(self):
        """Test memory usage of new components"""
        print("\n=== Memory Usage Testing ===")
        
        # Test memory usage for each component
        components = [
            ("Contraction Processor", self.contraction_processor.process_contractions),
            ("Symbol Processor", self.symbol_processor.process_symbols),
            ("Pronunciation Dictionary", self.pronunciation_dict.process_text_pronunciations),
            ("DateTime Processor", self.datetime_processor.process_dates_and_times),
            ("Abbreviation Handler", self.abbreviation_handler.process_abbreviations),
        ]
        
        test_text = self.test_texts['long'][0]
        
        for name, func in components:
            try:
                mem_usage = self.benchmark.memory_usage(func, test_text)
                print(f"{name}:")
                print(f"  Peak memory: {mem_usage['peak_memory']:.2f} MB")
                print(f"  Memory increase: {mem_usage['memory_increase']:.2f} MB")
                
                # Ensure reasonable memory usage (should not increase by more than 50MB)
                self.assertLess(mem_usage['memory_increase'], 50.0,
                              f"{name} uses too much memory: {mem_usage['memory_increase']:.2f} MB")
            except Exception as e:
                print(f"{name}: Memory profiling failed - {e}")
    
    def test_correctness_preservation(self):
        """Test that new components preserve correctness of existing functionality"""
        print("\n=== Correctness Preservation Testing ===")
        
        # Test cases that should work the same way
        test_cases = [
            ("Hello world", "Hello world"),  # No changes expected
            ("5 + 3 = 8", "5  plus  3  equals  8"),  # Symbol processing
            ("It's a beautiful day", "It's a beautiful day"),  # Natural contractions preserved
        ]
        
        for input_text, expected_pattern in test_cases:
            # Process with new components
            result = input_text
            result = self.symbol_processor.process_symbols(result)
            result = self.contraction_processor.process_contractions(result, mode='natural')
            
            # Clean up whitespace for comparison
            result_clean = ' '.join(result.split())
            expected_clean = ' '.join(expected_pattern.split())
            
            print(f"Input: '{input_text}'")
            print(f"Expected pattern: '{expected_clean}'")
            print(f"Actual result: '{result_clean}'")
            
            # For exact matches
            if expected_pattern == input_text:
                self.assertEqual(result_clean, expected_clean)
            else:
                # For pattern matches, check that key transformations occurred
                if "plus" in expected_pattern:
                    self.assertIn("plus", result_clean)
                if "equals" in expected_pattern:
                    self.assertIn("equals", result_clean)

if __name__ == '__main__':
    # Run performance tests
    unittest.main(verbosity=2)
