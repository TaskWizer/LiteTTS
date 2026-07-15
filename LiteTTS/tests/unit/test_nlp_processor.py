#!/usr/bin/env python3
"""
Unit tests for NLP processor
"""

import pytest
from LiteTTS.nlp.processor import NLPProcessor


class TestNLPProcessor:
    """Test cases for NLPProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return NLPProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_text(self, processor):
        """Test processing text"""
        result = processor.process_text("Hello world")
        assert isinstance(result, str)

    def test_normalize_text(self, processor):
        """Test normalizing text"""
        result = processor.normalize_text("Hello  world")
        assert isinstance(result, str)

    def test_get_processing_stats(self, processor):
        """Test getting processing stats"""
        result = processor.get_processing_stats()
        assert isinstance(result, dict)


class TestNLPProcessorEdgeCases:
    """Edge case tests for NLPProcessor"""

    @pytest.fixture
    def processor(self):
        return NLPProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_text("")
        assert isinstance(result, str)
