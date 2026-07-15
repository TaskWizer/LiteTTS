#!/usr/bin/env python3
"""
Unit tests for context adapter
"""

import pytest
from LiteTTS.nlp.context_adapter import ContextAdapter, SpeechContext


class TestContextAdapter:
    """Test cases for ContextAdapter"""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance"""
        return ContextAdapter()

    def test_initialization(self, adapter):
        """Test adapter initializes correctly"""
        assert adapter is not None

    def test_analyze_context(self, adapter):
        """Test analyzing context"""
        result = adapter.analyze_context("Hello world")
        assert isinstance(result, SpeechContext)

    def test_analyze_context_with_metadata(self, adapter):
        """Test analyzing context with metadata"""
        metadata = {"audience": "technical"}
        result = adapter.analyze_context("Hello world", metadata)
        assert isinstance(result, SpeechContext)


class TestContextAdapterEdgeCases:
    """Edge case tests for ContextAdapter"""

    @pytest.fixture
    def adapter(self):
        return ContextAdapter()

    def test_analyze_empty_string(self, adapter):
        """Test analyzing empty string"""
        result = adapter.analyze_context("")
        assert isinstance(result, SpeechContext)

    def test_analyze_unicode(self, adapter):
        """Test analyzing unicode text"""
        result = adapter.analyze_context("Hello 世界")
        assert isinstance(result, SpeechContext)

    def test_analyze_long_text(self, adapter):
        """Test analyzing long text"""
        long_text = "Hello world. " * 100
        result = adapter.analyze_context(long_text)
        assert isinstance(result, SpeechContext)
