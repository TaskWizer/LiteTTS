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

    def test_normalize_basic_text(self, normalizer):
        """Test normalizing basic text"""
        text = "Hello world"
        result = normalizer.normalize_text(text)
        assert result is not None

    def test_normalize_empty_string(self, normalizer):
        """Test normalizing empty string"""
        text = ""
        result = normalizer.normalize_text(text)
        assert result == ""

    def test_normalize_whitespace(self, normalizer):
        """Test normalizing whitespace"""
        text = "   \t\n  "
        result = normalizer.normalize_text(text)
        assert result is not None

    def test_normalize_unicode(self, normalizer):
        """Test normalizing unicode text"""
        text = "Hello 世界"
        result = normalizer.normalize_text(text)
        assert result is not None

    def test_normalize_numbers(self, normalizer):
        """Test normalizing numbers in text"""
        text = "The price is $19.99"
        result = normalizer.normalize_text(text)
        assert result is not None


class TestTextNormalizerEdgeCases:
    """Edge case tests for TextNormalizer"""

    @pytest.fixture
    def normalizer(self):
        return TextNormalizer()

    def test_normalize_very_long_text(self, normalizer):
        """Test normalizing very long text"""
        text = "A" * 10000
        result = normalizer.normalize_text(text)
        assert result is not None

    def test_normalize_mixed_case(self, normalizer):
        """Test normalizing mixed case"""
        text = "HeLLo WoRLD"
        result = normalizer.normalize_text(text)
        assert result is not None
