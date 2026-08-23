#!/usr/bin/env python3
"""
Unit tests for phonetic processor
"""

import pytest

from LiteTTS.nlp.phonetic_processor import PhoneticProcessor


class TestPhoneticProcessor:
    """Test cases for PhoneticProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return PhoneticProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_phonetics(self, processor):
        """Test processing phonetics"""
        result = processor.process_phonetics("Hello")
        assert isinstance(result, str)


class TestPhoneticProcessorEdgeCases:
    """Edge case tests for PhoneticProcessor"""

    @pytest.fixture
    def processor(self):
        return PhoneticProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_phonetics("")
        assert isinstance(result, str)

    def test_process_unicode(self, processor):
        """Test processing unicode"""
        result = processor.process_phonetics("Hello 世界")
        assert isinstance(result, str)
