#!/usr/bin/env python3
"""
Unit tests for interjection processor
"""

import pytest
from LiteTTS.nlp.interjection_processor import InterjectionProcessor, process_interjections, analyze_interjections


class TestInterjectionProcessor:
    """Test cases for InterjectionProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return InterjectionProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_interjections(self, processor):
        """Test processing interjections"""
        result = processor.process_interjections("Wow, that's amazing!")
        assert isinstance(result, str)

    def test_analyze_interjections(self, processor):
        """Test analyzing interjections"""
        result = processor.analyze_interjections("Wow, that's amazing!")
        assert isinstance(result, dict)

    def test_is_interjection(self, processor):
        """Test checking if word is interjection"""
        result = processor.is_interjection("wow")
        assert isinstance(result, bool)

    def test_get_interjection_fix(self, processor):
        """Test getting interjection fix"""
        result = processor.get_interjection_fix("wow")
        assert isinstance(result, str)


class TestInterjectionProcessorEdgeCases:
    """Edge case tests for InterjectionProcessor"""

    @pytest.fixture
    def processor(self):
        return InterjectionProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_interjections("")
        assert isinstance(result, str)

    def test_process_no_interjections(self, processor):
        """Test processing text without interjections"""
        result = processor.process_interjections("Hello world")
        assert isinstance(result, str)

    def test_is_interjection_false(self, processor):
        """Test checking non-interjection"""
        result = processor.is_interjection("hello")
        assert result is False


class TestInterjectionProcessorModuleFunctions:
    """Test module-level functions"""

    def test_process_interjections_function(self):
        """Test module-level process_interjections function"""
        result = process_interjections("Wow!")
        assert isinstance(result, str)

    def test_analyze_interjections_function(self):
        """Test module-level analyze_interjections function"""
        result = analyze_interjections("Wow!")
        assert isinstance(result, dict)
