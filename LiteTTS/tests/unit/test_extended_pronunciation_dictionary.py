#!/usr/bin/env python3
"""
Unit tests for extended pronunciation dictionary
"""

import pytest
from LiteTTS.nlp.extended_pronunciation_dictionary import ExtendedPronunciationDictionary


class TestExtendedPronunciationDictionary:
    """Test cases for ExtendedPronunciationDictionary"""

    @pytest.fixture
    def dictionary(self):
        """Create dictionary instance"""
        return ExtendedPronunciationDictionary()

    def test_initialization(self, dictionary):
        """Test dictionary initializes correctly"""
        assert dictionary is not None

    def test_get_pronunciation(self, dictionary):
        """Test getting pronunciation"""
        result = dictionary.get_pronunciation("hello")
        assert isinstance(result, str)

    def test_process_text_pronunciations(self, dictionary):
        """Test processing text pronunciations"""
        result = dictionary.process_text_pronunciations("hello world")
        assert isinstance(result, str)

    def test_analyze_pronunciations(self, dictionary):
        """Test analyzing pronunciations"""
        result = dictionary.analyze_pronunciations("hello world")
        assert isinstance(result, dict)


class TestExtendedPronunciationDictionaryEdgeCases:
    """Edge case tests for ExtendedPronunciationDictionary"""

    @pytest.fixture
    def dictionary(self):
        return ExtendedPronunciationDictionary()

    def test_get_pronunciation_empty(self, dictionary):
        """Test getting pronunciation for empty string"""
        result = dictionary.get_pronunciation("")
        assert isinstance(result, str)
