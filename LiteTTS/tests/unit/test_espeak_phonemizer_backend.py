#!/usr/bin/env python3
"""
Unit tests for espeak phonemizer backend
"""

import pytest
from LiteTTS.nlp.espeak_phonemizer_backend import EspeakPhonemizerBackend, EspeakConfig


class TestEspeakPhonemizerBackend:
    """Test cases for EspeakPhonemizerBackend"""

    @pytest.fixture
    def backend(self):
        """Create backend instance"""
        config = EspeakConfig()
        return EspeakPhonemizerBackend(config)

    def test_initialization(self, backend):
        """Test backend initializes correctly"""
        assert backend is not None

    def test_is_available(self, backend):
        """Test checking if espeak is available"""
        result = backend.is_available()
        assert isinstance(result, bool)

    def test_get_statistics(self, backend):
        """Test getting statistics"""
        result = backend.get_statistics()
        assert isinstance(result, dict)


class TestEspeakPhonemizerBackendEdgeCases:
    """Edge case tests for EspeakPhonemizerBackend"""

    @pytest.fixture
    def backend(self):
        config = EspeakConfig()
        return EspeakPhonemizerBackend(config)

    def test_clear_cache(self, backend):
        """Test clearing cache"""
        result = backend.clear_cache()
        assert result is None
