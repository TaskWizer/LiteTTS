#!/usr/bin/env python3
"""
Unit tests for advanced phonetic mapping
"""

import pytest

from LiteTTS.nlp.advanced_phonetic_mapping import AdvancedPhoneticMapper


class TestAdvancedPhoneticMapper:
    """Test cases for AdvancedPhoneticMapper"""

    @pytest.fixture
    def mapper(self):
        """Create mapper instance"""
        return AdvancedPhoneticMapper()

    def test_initialization(self, mapper):
        """Test mapper initializes correctly"""
        assert mapper is not None

    def test_map_to_ipa(self, mapper):
        """Test mapping text to IPA"""
        result = mapper.map_to_ipa("hello")
        assert isinstance(result, str)

    def test_get_phoneme_alternatives(self, mapper):
        """Test getting phoneme alternatives"""
        result = mapper.get_phoneme_alternatives("h")
        assert isinstance(result, list)

    def test_validate_ipa_string(self, mapper):
        """Test validating IPA string"""
        result = mapper.validate_ipa_string("həˈloʊ")
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestAdvancedPhoneticMapperEdgeCases:
    """Edge case tests for AdvancedPhoneticMapper"""

    @pytest.fixture
    def mapper(self):
        return AdvancedPhoneticMapper()

    def test_map_empty_string(self, mapper):
        """Test mapping empty string"""
        result = mapper.map_to_ipa("")
        assert isinstance(result, str)

    def test_map_unicode(self, mapper):
        """Test mapping unicode text"""
        result = mapper.map_to_ipa("hello world")
        assert isinstance(result, str)

    def test_validate_invalid_ipa(self, mapper):
        """Test validating invalid IPA string"""
        result = mapper.validate_ipa_string("not ipa")
        assert isinstance(result, tuple)
