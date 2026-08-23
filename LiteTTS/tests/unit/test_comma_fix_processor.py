#!/usr/bin/env python3
"""
Unit tests for comma fix processor
"""

import pytest

from LiteTTS.nlp.comma_fix_processor import CommaFixProcessor


class TestCommaFixProcessor:
    """Test cases for CommaFixProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return CommaFixProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_fix_comma_pronunciation(self, processor):
        """Test fixing comma pronunciation"""
        result = processor.fix_comma_pronunciation("Hello, world")
        assert isinstance(result, str)

    def test_analyze_comma_issues(self, processor):
        """Test analyzing comma issues"""
        result = processor.analyze_comma_issues("Hello, world")
        assert isinstance(result, dict)


class TestCommaFixProcessorEdgeCases:
    """Edge case tests for CommaFixProcessor"""

    @pytest.fixture
    def processor(self):
        return CommaFixProcessor()

    def test_fix_empty_string(self, processor):
        """Test fixing empty string"""
        result = processor.fix_comma_pronunciation("")
        assert isinstance(result, str)

    def test_fix_no_commas(self, processor):
        """Test fixing text without commas"""
        result = processor.fix_comma_pronunciation("Hello world")
        assert isinstance(result, str)

    def test_analyze_no_commas(self, processor):
        """Test analyzing text without commas"""
        result = processor.analyze_comma_issues("Hello world")
        assert isinstance(result, dict)
