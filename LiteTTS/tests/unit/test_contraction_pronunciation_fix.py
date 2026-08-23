#!/usr/bin/env python3
"""
Unit tests for contraction pronunciation fix
"""

import pytest

from LiteTTS.nlp.contraction_pronunciation_fix import ContractionPronunciationFix


class TestContractionPronunciationFix:
    """Test cases for ContractionPronunciationFix"""

    @pytest.fixture
    def fixer(self):
        """Create fixer instance"""
        return ContractionPronunciationFix()

    def test_initialization(self, fixer):
        """Test fixer initializes correctly"""
        assert fixer is not None

    def test_fix_contraction_pronunciation(self, fixer):
        """Test fixing contraction pronunciation"""
        result = fixer.fix_contraction_pronunciation("I'm happy")
        assert isinstance(result, str)

    def test_analyze_contraction_issues(self, fixer):
        """Test analyzing contraction issues"""
        result = fixer.analyze_contraction_issues("I'm happy")
        assert isinstance(result, dict)

    def test_normalize_apostrophes(self, fixer):
        """Test normalizing apostrophes"""
        result = fixer.normalize_apostrophes("I'm happy")
        assert isinstance(result, str)


class TestContractionPronunciationFixEdgeCases:
    """Edge case tests for ContractionPronunciationFix"""

    @pytest.fixture
    def fixer(self):
        return ContractionPronunciationFix()

    def test_fix_empty_string(self, fixer):
        """Test fixing empty string"""
        result = fixer.fix_contraction_pronunciation("")
        assert isinstance(result, str)
