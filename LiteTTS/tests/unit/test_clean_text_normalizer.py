#!/usr/bin/env python3
"""
Unit tests for clean text normalizer
"""

import pytest

from LiteTTS.nlp.clean_text_normalizer import CleanTextNormalizer, NormalizationResult


class TestCleanTextNormalizer:
    """Test cases for CleanTextNormalizer"""

    @pytest.fixture
    def normalizer(self):
        """Create normalizer instance"""
        return CleanTextNormalizer()

    def test_initialization(self, normalizer):
        """Test normalizer initializes correctly"""
        assert normalizer is not None

    def test_normalize_text(self, normalizer):
        """Test normalizing text"""
        result = normalizer.normalize_text("Hello world")
        assert isinstance(result, NormalizationResult)


class TestCleanTextNormalizerEdgeCases:
    """Edge case tests for CleanTextNormalizer"""

    @pytest.fixture
    def normalizer(self):
        return CleanTextNormalizer()

    def test_normalize_empty_string(self, normalizer):
        """Test normalizing empty string"""
        result = normalizer.normalize_text("")
        assert isinstance(result, NormalizationResult)
