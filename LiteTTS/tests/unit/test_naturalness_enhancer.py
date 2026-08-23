#!/usr/bin/env python3
"""
Unit tests for naturalness enhancer
"""

import pytest

from LiteTTS.nlp.naturalness_enhancer import NaturalnessEnhancer, NaturalnessProfile


class TestNaturalnessEnhancer:
    """Test cases for NaturalnessEnhancer"""

    @pytest.fixture
    def enhancer(self):
        """Create enhancer instance"""
        return NaturalnessEnhancer(naturalness_level=0.8)

    def test_initialization(self, enhancer):
        """Test enhancer initializes correctly"""
        assert enhancer is not None

    def test_enhance_naturalness(self, enhancer):
        """Test enhancing naturalness"""
        result = enhancer.enhance_naturalness("Hello world")
        assert isinstance(result, NaturalnessProfile)

    def test_apply_naturalness_to_text(self, enhancer):
        """Test applying naturalness to text"""
        profile = enhancer.enhance_naturalness("Hello world")
        result = enhancer.apply_naturalness_to_text("Hello world", profile)
        assert isinstance(result, str)


class TestNaturalnessEnhancerEdgeCases:
    """Edge case tests for NaturalnessEnhancer"""

    @pytest.fixture
    def enhancer(self):
        return NaturalnessEnhancer(naturalness_level=0.5)

    def test_enhance_empty_string(self, enhancer):
        """Test enhancing empty string"""
        result = enhancer.enhance_naturalness("")
        assert isinstance(result, NaturalnessProfile)

    def test_enhance_unicode(self, enhancer):
        """Test enhancing unicode text"""
        result = enhancer.enhance_naturalness("Hello 世界")
        assert isinstance(result, NaturalnessProfile)

    def test_enhance_long_text(self, enhancer):
        """Test enhancing long text"""
        long_text = "Hello world. " * 50
        result = enhancer.enhance_naturalness(long_text)
        assert isinstance(result, NaturalnessProfile)
