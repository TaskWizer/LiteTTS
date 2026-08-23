#!/usr/bin/env python3
"""
Unit tests for interjection fix processor
"""

import pytest

from LiteTTS.nlp.interjection_fix_processor import InterjectionFixProcessor


class TestInterjectionFixProcessor:
    """Test cases for InterjectionFixProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return InterjectionFixProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_fix_interjection_pronunciation(self, processor):
        """Test fixing interjection pronunciation"""
        result = processor.fix_interjection_pronunciation("Wow, that's amazing!")
        assert isinstance(result, str)

    def test_analyze_interjection_issues(self, processor):
        """Test analyzing interjection issues"""
        result = processor.analyze_interjection_issues("Wow, that's amazing!")
        assert isinstance(result, dict)


class TestInterjectionFixProcessorEdgeCases:
    """Edge case tests for InterjectionFixProcessor"""

    @pytest.fixture
    def processor(self):
        return InterjectionFixProcessor()

    def test_fix_empty_string(self, processor):
        """Test fixing empty string"""
        result = processor.fix_interjection_pronunciation("")
        assert isinstance(result, str)
