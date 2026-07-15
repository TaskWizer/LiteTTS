#!/usr/bin/env python3
"""
Unit tests for proper name pronunciation processor
"""

import pytest
from LiteTTS.nlp.proper_name_pronunciation_processor import ProperNamePronunciationProcessor


class TestProperNamePronunciationProcessor:
    """Test cases for ProperNamePronunciationProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return ProperNamePronunciationProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_proper_name_pronunciation(self, processor):
        """Test processing proper name pronunciation"""
        result = processor.process_proper_name_pronunciation("Hello John")
        assert isinstance(result, str)


class TestProperNamePronunciationProcessorEdgeCases:
    """Edge case tests for ProperNamePronunciationProcessor"""

    @pytest.fixture
    def processor(self):
        return ProperNamePronunciationProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_proper_name_pronunciation("")
        assert isinstance(result, str)
