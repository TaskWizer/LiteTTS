#!/usr/bin/env python3
"""
Unit tests for pronunciation rules processor
"""

import pytest

from LiteTTS.nlp.pronunciation_rules_processor import PronunciationRulesProcessor


class TestPronunciationRulesProcessor:
    """Test cases for PronunciationRulesProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return PronunciationRulesProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_pronunciation_rules(self, processor):
        """Test processing pronunciation rules"""
        result = processor.process_pronunciation_rules("I'm happy")
        assert isinstance(result, str)

    def test_get_pronunciation_rules(self, processor):
        """Test getting pronunciation rules"""
        result = processor.get_pronunciation_rules()
        assert isinstance(result, dict)

    def test_analyze_contractions(self, processor):
        """Test analyzing contractions"""
        result = processor.analyze_contractions("I'm happy")
        assert isinstance(result, dict)


class TestPronunciationRulesProcessorEdgeCases:
    """Edge case tests for PronunciationRulesProcessor"""

    @pytest.fixture
    def processor(self):
        return PronunciationRulesProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_pronunciation_rules("")
        assert isinstance(result, str)
