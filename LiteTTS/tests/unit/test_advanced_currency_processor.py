#!/usr/bin/env python3
"""
Unit tests for advanced currency processor
"""

import pytest
from LiteTTS.nlp.advanced_currency_processor import AdvancedCurrencyProcessor


class TestAdvancedCurrencyProcessor:
    """Test cases for AdvancedCurrencyProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return AdvancedCurrencyProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_currency_text(self, processor):
        """Test processing currency text"""
        result = processor.process_currency_text("The price is $100")
        assert isinstance(result, str)


class TestAdvancedCurrencyProcessorEdgeCases:
    """Edge case tests for AdvancedCurrencyProcessor"""

    @pytest.fixture
    def processor(self):
        return AdvancedCurrencyProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_currency_text("")
        assert isinstance(result, str)
