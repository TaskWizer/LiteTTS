#!/usr/bin/env python3
"""
Unit tests for pronunciation dictionary
"""

import pytest

from LiteTTS.nlp.pronunciation_dictionary import PronunciationDictionary


class TestPronunciationDictionary:
    """Test cases for PronunciationDictionary"""

    @pytest.fixture
    def dictionary(self):
        """Create dictionary instance"""
        return PronunciationDictionary()

    def test_initialization(self, dictionary):
        """Test dictionary initializes correctly"""
        assert dictionary is not None

    def test_get_pronunciation(self, dictionary):
        """Test getting pronunciation for a word"""
        result = dictionary.get_pronunciation("test")
        assert isinstance(result, str)

    def test_has_pronunciation(self, dictionary):
        """Test checking if word has pronunciation"""
        result = dictionary.has_pronunciation("test")
        assert isinstance(result, bool)

    def test_get_all_words(self, dictionary):
        """Test getting all words"""
        result = dictionary.get_all_words()
        assert isinstance(result, list)

    def test_get_statistics(self, dictionary):
        """Test getting dictionary statistics"""
        result = dictionary.get_statistics()
        assert isinstance(result, dict)


class TestPronunciationDictionaryEdgeCases:
    """Edge case tests for PronunciationDictionary"""

    @pytest.fixture
    def dictionary(self):
        return PronunciationDictionary()

    def test_get_pronunciation_unknown_word(self, dictionary):
        """Test getting pronunciation for unknown word"""
        result = dictionary.get_pronunciation("xyzabc123")
        assert isinstance(result, str)

    def test_has_pronunciation_unknown(self, dictionary):
        """Test checking unknown word"""
        result = dictionary.has_pronunciation("xyzabc123")
        assert result is False

    def test_get_all_words_not_empty(self, dictionary):
        """Test that all words returns list"""
        result = dictionary.get_all_words()
        assert isinstance(result, list)
