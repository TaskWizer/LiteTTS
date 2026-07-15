#!/usr/bin/env python3
"""
Unit tests for text normalizer
"""

import pytest
from LiteTTS.nlp.text_normalizer import TextNormalizer


class TestTextNormalizer:
    """Test cases for TextNormalizer"""

    @pytest.fixture
    def normalizer(self):
        """Create normalizer instance"""
        return TextNormalizer()

    def test_initialization(self, normalizer):
        """Test normalizer initializes correctly"""
        assert normalizer is not None

    def test_normalize_text(self, normalizer):
        """Test normalizing text"""
        result = normalizer.normalize_text("Hello world")
        assert isinstance(result, str)

    def test_normalize_numbers(self, normalizer):
        """Test normalizing numbers"""
        result = normalizer._normalize_numbers("123")
        assert isinstance(result, str)

    def test_normalize_contractions(self, normalizer):
        """Test normalizing contractions"""
        result = normalizer._normalize_contractions("can't")
        assert isinstance(result, str)

    def test_normalize_punctuation(self, normalizer):
        """Test normalizing punctuation"""
        result = normalizer._normalize_punctuation("Hello...")
        assert isinstance(result, str)


class TestTextNormalizerEdgeCases:
    """Edge case tests for TextNormalizer"""

    @pytest.fixture
    def normalizer(self):
        return TextNormalizer()

    def test_normalize_empty_string(self, normalizer):
        """Test normalizing empty string"""
        result = normalizer.normalize_text("")
        assert isinstance(result, str)

    def test_normalize_unicode(self, normalizer):
        """Test normalizing unicode text"""
        result = normalizer.normalize_text("Hello 世界 🌍")
        assert isinstance(result, str)

    def test_normalize_already_normal(self, normalizer):
        """Test normalizing already normal text"""
        result = normalizer.normalize_text("Hello world, how are you?")
        assert isinstance(result, str)

    def test_normalize_currency(self, normalizer):
        """Test normalizing currency"""
        result = normalizer._normalize_currency("$123.45")
        assert isinstance(result, str)
