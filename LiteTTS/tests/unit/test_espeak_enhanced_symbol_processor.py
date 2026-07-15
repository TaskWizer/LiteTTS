#!/usr/bin/env python3
"""
Unit tests for espeak enhanced symbol processor
"""

import pytest
from LiteTTS.nlp.espeak_enhanced_symbol_processor import EspeakEnhancedSymbolProcessor, SymbolProcessingResult


class TestEspeakEnhancedSymbolProcessor:
    """Test cases for EspeakEnhancedSymbolProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return EspeakEnhancedSymbolProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_symbols(self, processor):
        """Test processing symbols"""
        result = processor.process_symbols("Hello @user")
        assert isinstance(result, SymbolProcessingResult)


class TestEspeakEnhancedSymbolProcessorEdgeCases:
    """Edge case tests for EspeakEnhancedSymbolProcessor"""

    @pytest.fixture
    def processor(self):
        return EspeakEnhancedSymbolProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_symbols("")
        assert isinstance(result, SymbolProcessingResult)
