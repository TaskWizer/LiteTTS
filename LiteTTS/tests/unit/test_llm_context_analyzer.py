#!/usr/bin/env python3
"""
Unit tests for LLM context analyzer
"""

import pytest

from LiteTTS.nlp.llm_context_analyzer import LLMContextAnalysis, LLMContextAnalyzer


class TestLLMContextAnalyzer:
    """Test cases for LLMContextAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return LLMContextAnalyzer(enable_llm=False)

    def test_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer is not None

    def test_analyze_context(self, analyzer):
        """Test analyzing context"""
        result = analyzer.analyze_context("Hello world")
        assert isinstance(result, LLMContextAnalysis)


class TestLLMContextAnalyzerEdgeCases:
    """Edge case tests for LLMContextAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        return LLMContextAnalyzer(enable_llm=False)

    def test_analyze_empty_string(self, analyzer):
        """Test analyzing empty string"""
        result = analyzer.analyze_context("")
        assert isinstance(result, LLMContextAnalysis)
