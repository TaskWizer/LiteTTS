#!/usr/bin/env python3
"""
Unit tests for unified pronunciation fix
"""

import pytest

from LiteTTS.nlp.unified_pronunciation_fix import PronunciationFixResult, UnifiedPronunciationFix


class TestUnifiedPronunciationFix:
    """Test cases for UnifiedPronunciationFix"""

    @pytest.fixture
    def fixer(self):
        """Create fixer instance"""
        return UnifiedPronunciationFix()

    def test_initialization(self, fixer):
        """Test fixer initializes correctly"""
        assert fixer is not None

    def test_process_pronunciation_fixes(self, fixer):
        """Test processing pronunciation fixes"""
        result = fixer.process_pronunciation_fixes("Hello world")
        assert isinstance(result, PronunciationFixResult)

    def test_analyze_all_issues(self, fixer):
        """Test analyzing all issues"""
        result = fixer.analyze_all_issues("Hello world")
        assert isinstance(result, dict)

    def test_get_fix_statistics(self, fixer):
        """Test getting fix statistics"""
        result = fixer.get_fix_statistics("Hello world")
        assert isinstance(result, dict)


class TestUnifiedPronunciationFixEdgeCases:
    """Edge case tests for UnifiedPronunciationFix"""

    @pytest.fixture
    def fixer(self):
        return UnifiedPronunciationFix()

    def test_process_empty_string(self, fixer):
        """Test processing empty string"""
        result = fixer.process_pronunciation_fixes("")
        assert isinstance(result, PronunciationFixResult)
