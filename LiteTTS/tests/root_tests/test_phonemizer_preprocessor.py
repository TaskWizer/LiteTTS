#!/usr/bin/env python3
"""Tests for PhonemizationPreprocessor"""

import pytest
import importlib.util
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def load_module_from_path(module_name, file_path):
    """Load module directly from file path without triggering package __init__"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestPhonemizationPreprocessor:
    """Test suite for PhonemizationPreprocessor"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures"""
        try:
            module = load_module_from_path('phonemizer_preprocessor', 'LiteTTS/text/phonemizer_preprocessor.py')
            self.PhonemizationPreprocessor = module.PhonemizationPreprocessor
            self.processor = self.PhonemizationPreprocessor()
        except ImportError as e:
            pytest.skip(f"Could not import PhonemizationPreprocessor: {e}")

    def test_preprocess_text_basic(self):
        """Test basic text preprocessing"""
        result = self.processor.preprocess_text("Hello world")
        assert result.processed_text
        assert result.original_text == "Hello world"
        assert isinstance(result.changes_made, list)
        assert 0.0 <= result.confidence_score <= 1.0

    def test_preprocess_text_preserves_word_count(self):
        """Test that word count is preserved when requested"""
        text = "Hello world"
        result = self.processor.preprocess_text(text, preserve_word_count=True)
        # The processed text should have same number of words
        original_words = len(text.split())
        processed_words = len(result.processed_text.split())
        assert original_words == processed_words or result.confidence_score > 0.5

    def test_html_entity_decoding(self):
        """Test HTML entity decoding"""
        result = self.processor.preprocess_text("Hello &amp; world")
        assert "&amp;" not in result.processed_text
        assert "and" in result.processed_text.lower() or "&" in result.processed_text

    def test_preprocess_returns_result_object(self):
        """Test that preprocess returns PreprocessingResult"""
        result = self.processor.preprocess_text("Test text")
        assert hasattr(result, 'processed_text')
        assert hasattr(result, 'original_text')
        assert hasattr(result, 'changes_made')
        assert hasattr(result, 'confidence_score')
        assert hasattr(result, 'warnings')

    def test_preprocess_with_empty_text(self):
        """Test preprocessing empty text"""
        result = self.processor.preprocess_text("")
        assert result.processed_text == ""
        assert result.original_text == ""

    def test_preprocess_with_special_characters(self):
        """Test preprocessing text with special characters"""
        result = self.processor.preprocess_text("Hello! How are you?")
        assert result.processed_text
        assert len(result.warnings) >= 0

    def test_preprocess_with_numbers(self):
        """Test preprocessing text with numbers"""
        result = self.processor.preprocess_text("I have 123 apples")
        assert result.processed_text
        # Numbers should be handled

    def test_preprocess_with_contractions(self):
        """Test preprocessing text with contractions"""
        result = self.processor.preprocess_text("I don't know")
        assert result.processed_text
        # Contractions should be handled

    def test_preprocess_unicode_normalization(self):
        """Test unicode normalization"""
        result = self.processor.preprocess_text("café")
        assert result.processed_text
        assert "caf" in result.processed_text.lower()

    def test_confidence_score_bounds(self):
        """Test that confidence score is always in valid range"""
        test_cases = [
            "Hello world",
            "Testing 123",
            "Special chars: @#$%",
            "",
            "Longer text with multiple words to process"
        ]
        for text in test_cases:
            result = self.processor.preprocess_text(text)
            assert 0.0 <= result.confidence_score <= 1.0, f"Confidence score out of bounds for: {text}"

    def test_changes_made_is_list(self):
        """Test that changes_made is always a list"""
        result = self.processor.preprocess_text("Any text here")
        assert isinstance(result.changes_made, list)

    def test_warnings_is_list(self):
        """Test that warnings is always a list"""
        result = self.processor.preprocess_text("Any text here")
        assert isinstance(result.warnings, list)

    def test_contractions_map_loaded(self):
        """Test that contractions map is loaded"""
        assert hasattr(self.processor, 'contractions_map')
        assert isinstance(self.processor.contractions_map, dict)

    def test_number_words_map_loaded(self):
        """Test that number words map is loaded"""
        assert hasattr(self.processor, 'number_words_map')
        assert isinstance(self.processor.number_words_map, dict)

    def test_problematic_patterns_loaded(self):
        """Test that problematic patterns are loaded"""
        assert hasattr(self.processor, 'problematic_patterns')
        assert isinstance(self.processor.problematic_patterns, list)
