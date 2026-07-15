#!/usr/bin/env python3
"""
Unit tests for diphthong fix processor
"""

import pytest
from LiteTTS.nlp.diphthong_fix_processor import DiphthongFixProcessor


class TestDiphthongFixProcessor:
    """Test cases for DiphthongFixProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return DiphthongFixProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_fix_diphthong_pronunciation(self, processor):
        """Test fixing diphthong pronunciation"""
        result = processor.fix_diphthong_pronunciation("Hello")
        assert isinstance(result, str)

    def test_analyze_diphthong_issues(self, processor):
        """Test analyzing diphthong issues"""
        result = processor.analyze_diphthong_issues("Hello")
        assert isinstance(result, dict)


class TestDiphthongFixProcessorEdgeCases:
    """Edge case tests for DiphthongFixProcessor"""

    @pytest.fixture
    def processor(self):
        return DiphthongFixProcessor()

    def test_fix_empty_string(self, processor):
        """Test fixing empty string"""
        result = processor.fix_diphthong_pronunciation("")
        assert isinstance(result, str)

    def test_fix_unicode(self, processor):
        """Test fixing unicode text"""
        result = processor.fix_diphthong_pronunciation("Hello 世界")
        assert isinstance(result, str)
