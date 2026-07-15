#!/usr/bin/env python3
"""
Unit tests for phonetic dictionary manager
"""

import pytest
from LiteTTS.nlp.phonetic_dictionary_manager import PhoneticDictionaryManager


class TestPhoneticDictionaryManager:
    """Test cases for PhoneticDictionaryManager"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        return PhoneticDictionaryManager()

    def test_initialization(self, manager):
        """Test manager initializes correctly"""
        assert manager is not None

    def test_lookup(self, manager):
        """Test looking up a word"""
        result = manager.lookup("hello")
        # Result can be None or DictionaryEntry
        assert result is None or hasattr(result, 'word')

    def test_get_statistics(self, manager):
        """Test getting statistics"""
        result = manager.get_statistics()
        assert isinstance(result, dict)


class TestPhoneticDictionaryManagerEdgeCases:
    """Edge case tests for PhoneticDictionaryManager"""

    @pytest.fixture
    def manager(self):
        return PhoneticDictionaryManager()

    def test_lookup_unknown_word(self, manager):
        """Test looking up unknown word"""
        result = manager.lookup("xyzabc123")
        assert result is None
