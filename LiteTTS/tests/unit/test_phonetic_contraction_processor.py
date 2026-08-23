#!/usr/bin/env python3
"""
Unit tests for phonetic contraction processor
"""

import pytest

from LiteTTS.nlp.phonetic_contraction_processor import PhoneticContractionProcessor


class TestPhoneticContractionProcessor:
    """Test cases for PhoneticContractionProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return PhoneticContractionProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_contractions(self, processor):
        """Test processing contractions"""
        result = processor.process_contractions("I'm happy")
        assert isinstance(result, str)


class TestPhoneticContractionProcessorEdgeCases:
    """Edge case tests for PhoneticContractionProcessor"""

    @pytest.fixture
    def processor(self):
        return PhoneticContractionProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_contractions("")
        assert isinstance(result, str)
