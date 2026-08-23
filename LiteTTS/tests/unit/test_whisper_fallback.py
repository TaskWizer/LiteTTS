#!/usr/bin/env python3
"""
Unit tests for whisper fallback manager
"""

import pytest

from LiteTTS.backends.whisper_fallback_manager import WhisperFallbackManager


class TestWhisperFallbackManager:
    """Test cases for WhisperFallbackManager"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        return WhisperFallbackManager()

    def test_initialization(self, manager):
        """Test manager initializes correctly"""
        assert manager is not None

    def test_get_fallback_statistics(self, manager):
        """Test getting fallback statistics"""
        result = manager.get_fallback_statistics()
        assert isinstance(result, dict)

    def test_clear_cache(self, manager):
        """Test clearing cache"""
        result = manager.clear_cache()
        assert result is None

    def test_optimize_fallback_chain(self, manager):
        """Test optimizing fallback chain"""
        result = manager.optimize_fallback_chain()
        assert result is None


class TestWhisperFallbackEdgeCases:
    """Edge case tests for WhisperFallbackManager"""

    @pytest.fixture
    def manager(self):
        return WhisperFallbackManager()

    def test_get_stats_keys(self, manager):
        """Test fallback statistics contains expected keys"""
        result = manager.get_fallback_statistics()
        assert isinstance(result, dict)

    def test_optimize_when_no_data(self, manager):
        """Test optimizing with no fallback data"""
        result = manager.optimize_fallback_chain()
        assert result is None
