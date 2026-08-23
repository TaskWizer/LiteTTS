#!/usr/bin/env python3
"""
Unit tests for ticker symbol processor
"""

import pytest

from LiteTTS.nlp.ticker_symbol_processor import TickerProcessingResult, TickerSymbolProcessor


class TestTickerSymbolProcessor:
    """Test cases for TickerSymbolProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return TickerSymbolProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_ticker_symbols(self, processor):
        """Test processing ticker symbols"""
        result = processor.process_ticker_symbols("AAPL went up today")
        assert isinstance(result, TickerProcessingResult)

    def test_analyze_potential_tickers(self, processor):
        """Test analyzing potential tickers"""
        result = processor.analyze_potential_tickers("AAPL MSFT GOOG")
        assert isinstance(result, dict)


class TestTickerSymbolProcessorEdgeCases:
    """Edge case tests for TickerSymbolProcessor"""

    @pytest.fixture
    def processor(self):
        return TickerSymbolProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_ticker_symbols("")
        assert isinstance(result, TickerProcessingResult)

    def test_process_no_tickers(self, processor):
        """Test processing text without tickers"""
        result = processor.process_ticker_symbols("Hello world")
        assert isinstance(result, TickerProcessingResult)
