#!/usr/bin/env python3
"""
Unit tests for advanced symbol processor
"""

import pytest

from LiteTTS.nlp.advanced_symbol_processor import AdvancedSymbolProcessor


class TestAdvancedSymbolProcessor:
    """Test cases for AdvancedSymbolProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return AdvancedSymbolProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_symbols(self, processor):
        """Test processing symbols"""
        result = processor.process_symbols("Hello @user #topic")
        assert isinstance(result, str)

    def test_analyze_symbols(self, processor):
        """Test analyzing symbols"""
        result = processor.analyze_symbols("Hello @user #topic")
        assert isinstance(result, dict)

    def test_process_context_aware_symbols(self, processor):
        """Test processing context-aware symbols"""
        result = processor.process_context_aware_symbols("Email: test@example.com")
        assert isinstance(result, str)


class TestAdvancedSymbolProcessorEdgeCases:
    """Edge case tests for AdvancedSymbolProcessor"""

    @pytest.fixture
    def processor(self):
        return AdvancedSymbolProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_symbols("")
        assert isinstance(result, str)

    def test_process_no_symbols(self, processor):
        """Test processing text with no symbols"""
        result = processor.process_symbols("Hello world")
        assert isinstance(result, str)

    def test_process_unicode_symbols(self, processor):
        """Test processing unicode symbols"""
        result = processor.process_symbols("Hello © 2024")
        assert isinstance(result, str)

    def test_analyze_empty_string(self, processor):
        """Test analyzing empty string"""
        result = processor.analyze_symbols("")
        assert isinstance(result, dict)
