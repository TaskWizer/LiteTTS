#!/usr/bin/env python3
"""
Comprehensive validation test for question mark fix
Ensures that question marks are not converted to "up right arrow" or similar
"""

import json
from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions
from LiteTTS.nlp.prosody_analyzer import ProsodyAnalyzer
from LiteTTS.nlp.advanced_symbol_processor import AdvancedSymbolProcessor


class TestQuestionMarkFixValidation:
    """Comprehensive validation of question mark processing fix"""
    
    def test_prosody_analyzer_no_arrows(self):
        """Test that prosody analyzer doesn't add arrow symbols"""
        prosody = ProsodyAnalyzer()
        
        test_cases = [
            "What is this?",
            "How are you?", 
            "Are you sure?",
            "What??? Why???",
            "Hello? Anyone there?"
        ]
        
        print("🔍 TESTING PROSODY ANALYZER (NO ARROWS)")
        print("=" * 50)
        
        for test_text in test_cases:
            # Test enhance_intonation_markers
            after_intonation = prosody.enhance_intonation_markers(test_text)
            
            # Test conversational intonation
            after_conversational = prosody.process_conversational_intonation(test_text)
            
            # Check for arrow symbols
            arrow_symbols = ['↗', '↘', '↑', '↓', '→', '←', '‼']
            has_arrows_intonation = any(arrow in after_intonation for arrow in arrow_symbols)
            has_arrows_conversational = any(arrow in after_conversational for arrow in arrow_symbols)
            
            print(f"Input: '{test_text}'")
            print(f"  After intonation: '{after_intonation}' (arrows: {has_arrows_intonation})")
            print(f"  After conversational: '{after_conversational}' (arrows: {has_arrows_conversational})")
            
            assert not has_arrows_intonation, f"Intonation processing added arrows: {after_intonation}"
            assert not has_arrows_conversational, f"Conversational processing added arrows: {after_conversational}"
            
        print("✅ Prosody analyzer correctly avoids adding arrow symbols")
    
    def test_symbol_processor_arrow_handling(self):
        """Test that symbol processor correctly handles arrow symbols if they exist"""
        symbol_processor = AdvancedSymbolProcessor()
        
        # Test cases with arrow symbols (should be converted to words)
        arrow_test_cases = [
            ("Text with ↗ arrow", "Text with up right arrow arrow"),
            ("Text with ↑ arrow", "Text with up arrow arrow"),
            ("Text with → arrow", "Text with right arrow arrow"),
        ]
        
        print("\n🔍 TESTING SYMBOL PROCESSOR ARROW CONVERSION")
        print("=" * 50)
        
        for input_text, expected_pattern in arrow_test_cases:
            result = symbol_processor.process_symbols(input_text)
            print(f"Input: '{input_text}' → Output: '{result}'")
            
            # Check that arrows are converted to words
            arrow_symbols = ['↗', '↘', '↑', '↓', '→', '←']
            has_arrows = any(arrow in result for arrow in arrow_symbols)
            assert not has_arrows, f"Arrow symbols not converted: {result}"
            
        print("✅ Symbol processor correctly converts arrow symbols to words")
    
    def test_complete_pipeline_no_arrows(self):
        """Test complete text processing pipeline doesn't produce arrows"""
        # Load config
        with open('config.json', 'r') as f:
            config_data = json.load(f)
        
        processor = UnifiedTextProcessor(config=config_data)
        
        test_cases = [
            "What is this?",
            "How much does it cost?",
            "Are you coming? Really?",
            "What??? Why??? Help!!!",
            "Hello! How are you? That's great!",
            "Question? Answer! Another question?",
        ]
        
        print("\n🔍 TESTING COMPLETE PIPELINE (NO ARROW CONVERSION)")
        print("=" * 60)
        
        for test_text in test_cases:
            options = ProcessingOptions()
            result = processor.process_text(test_text, options)
            
            # Check for arrow symbols in output
            arrow_symbols = ['↗', '↘', '↑', '↓', '→', '←', '‼']
            has_arrows = any(arrow in result.processed_text for arrow in arrow_symbols)
            
            # Check for "arrow" words in output (which would indicate conversion)
            has_arrow_words = 'arrow' in result.processed_text.lower()
            
            print(f"Input: '{test_text}'")
            print(f"Output: '{result.processed_text}'")
            print(f"Stages: {result.stages_completed}")
            print(f"Has arrows: {has_arrows}, Has 'arrow' words: {has_arrow_words}")
            print()
            
            assert not has_arrows, f"Pipeline output contains arrow symbols: {result.processed_text}"
            assert not has_arrow_words, f"Pipeline output contains 'arrow' words: {result.processed_text}"
            
        print("✅ Complete pipeline correctly processes questions without arrow conversion")
    
    def test_punctuation_normalization(self):
        """Test that multiple punctuation marks are normalized correctly"""
        with open('config.json', 'r') as f:
            config_data = json.load(f)
        
        processor = UnifiedTextProcessor(config=config_data)
        
        normalization_cases = [
            ("What???", "What?"),
            ("Help!!!", "Help!"),
            ("Really????", "Really?"),
            ("Wow!!!!!", "Wow!"),
        ]
        
        print("\n🔍 TESTING PUNCTUATION NORMALIZATION")
        print("=" * 50)
        
        for input_text, expected_pattern in normalization_cases:
            options = ProcessingOptions()
            result = processor.process_text(input_text, options)
            
            print(f"Input: '{input_text}' → Output: '{result.processed_text}'")
            
            # Check that multiple punctuation is normalized
            assert '???' not in result.processed_text, f"Multiple question marks not normalized: {result.processed_text}"
            assert '!!!' not in result.processed_text, f"Multiple exclamation marks not normalized: {result.processed_text}"
            
        print("✅ Multiple punctuation marks correctly normalized")
    
    def test_question_mark_preservation(self):
        """Test that question marks are preserved as question marks"""
        with open('config.json', 'r') as f:
            config_data = json.load(f)
        
        processor = UnifiedTextProcessor(config=config_data)
        
        question_cases = [
            "What is this?",
            "How are you?",
            "Are you sure?",
            "Why not?",
            "When will you arrive?",
        ]
        
        print("\n🔍 TESTING QUESTION MARK PRESERVATION")
        print("=" * 50)
        
        for test_text in question_cases:
            options = ProcessingOptions()
            result = processor.process_text(test_text, options)
            
            print(f"Input: '{test_text}' → Output: '{result.processed_text}'")
            
            # Check that question mark is preserved
            assert '?' in result.processed_text, f"Question mark not preserved: {result.processed_text}"
            
            # Check that no arrow-related words appear
            arrow_words = ['arrow', 'up right', 'right up']
            has_arrow_words = any(word in result.processed_text.lower() for word in arrow_words)
            assert not has_arrow_words, f"Arrow-related words found: {result.processed_text}"
            
        print("✅ Question marks correctly preserved without arrow conversion")


if __name__ == "__main__":
    # Run comprehensive validation
    test = TestQuestionMarkFixValidation()
    
    print("🧪 COMPREHENSIVE QUESTION MARK FIX VALIDATION")
    print("=" * 60)
    
    try:
        test.test_prosody_analyzer_no_arrows()
        test.test_symbol_processor_arrow_handling()
        test.test_complete_pipeline_no_arrows()
        test.test_punctuation_normalization()
        test.test_question_mark_preservation()
        
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        print("✅ Question mark fix is working correctly")
        print("✅ No arrow symbols are being added to text")
        print("✅ Question marks are preserved as punctuation")
        print("✅ Multiple punctuation is normalized properly")
        print("✅ Complete text processing pipeline is working correctly")
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        raise
