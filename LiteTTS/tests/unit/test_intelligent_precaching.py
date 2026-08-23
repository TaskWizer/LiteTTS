#!/usr/bin/env python3
"""
Unit tests for intelligent precaching module
"""

import pytest

from LiteTTS.cache.intelligent_precaching import IntelligentPreCaching


class TestIntelligentPreCaching:
    """Test cases for IntelligentPreCaching"""

    @pytest.fixture
    def precaching(self):
        """Create precaching instance"""
        return IntelligentPreCaching()

    def test_initialization(self, precaching):
        """Test precaching initializes correctly"""
        assert precaching is not None
        assert precaching.min_phrase_length == 3
        assert precaching.max_phrase_length == 10
        assert precaching.min_frequency == 2

    def test_essential_phrases_exist(self, precaching):
        """Test essential phrases are defined"""
        assert len(precaching.essential_phrases) > 0
        assert "Hello there! How can I" in precaching.essential_phrases

    def test_phrase_frequencies_initialized(self, precaching):
        """Test phrase frequencies is initialized"""
        assert precaching.phrase_frequencies is not None

    def test_get_analysis_summary(self, precaching):
        """Test getting analysis summary"""
        result = precaching._get_analysis_summary()
        assert isinstance(result, dict)
