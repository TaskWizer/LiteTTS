#!/usr/bin/env python3
"""
Unit tests for advanced abbreviation handler
"""

import pytest

from LiteTTS.nlp.advanced_abbreviation_handler import AdvancedAbbreviationHandler


class TestAdvancedAbbreviationHandler:
    """Test cases for AdvancedAbbreviationHandler"""

    @pytest.fixture
    def handler(self):
        """Create handler instance"""
        return AdvancedAbbreviationHandler()

    def test_initialization(self, handler):
        """Test handler initializes correctly"""
        assert handler is not None

    def test_process_abbreviations(self, handler):
        """Test processing abbreviations"""
        result = handler.process_abbreviations("Dr. Smith works at IBM")
        assert isinstance(result, str)

    def test_analyze_abbreviations(self, handler):
        """Test analyzing abbreviations"""
        result = handler.analyze_abbreviations("Dr. Smith")
        assert isinstance(result, dict)

    def test_get_supported_modes(self, handler):
        """Test getting supported modes"""
        result = handler.get_supported_modes()
        assert isinstance(result, list)


class TestAdvancedAbbreviationHandlerEdgeCases:
    """Edge case tests for AdvancedAbbreviationHandler"""

    @pytest.fixture
    def handler(self):
        return AdvancedAbbreviationHandler()

    def test_process_empty_string(self, handler):
        """Test processing empty string"""
        result = handler.process_abbreviations("")
        assert isinstance(result, str)

    def test_process_no_abbreviations(self, handler):
        """Test processing text without abbreviations"""
        result = handler.process_abbreviations("Hello world")
        assert isinstance(result, str)
