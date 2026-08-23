#!/usr/bin/env python3
"""
Unit tests for enhanced contraction processor
"""

import pytest

from LiteTTS.nlp.enhanced_contraction_processor import EnhancedContractionProcessor


class TestEnhancedContractionProcessor:
    """Test cases for EnhancedContractionProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return EnhancedContractionProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_contractions(self, processor):
        """Test processing contractions"""
        result = processor.process_contractions("I'm happy")
        assert isinstance(result, str)

    def test_get_contraction_info(self, processor):
        """Test getting contraction info"""
        result = processor.get_contraction_info("I'm happy")
        assert isinstance(result, dict)

    def test_get_supported_modes(self, processor):
        """Test getting supported modes"""
        result = processor.get_supported_modes()
        assert isinstance(result, list)


class TestEnhancedContractionProcessorEdgeCases:
    """Edge case tests for EnhancedContractionProcessor"""

    @pytest.fixture
    def processor(self):
        return EnhancedContractionProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_contractions("")
        assert isinstance(result, str)

    def test_process_no_contractions(self, processor):
        """Test processing text without contractions"""
        result = processor.process_contractions("Hello world")
        assert isinstance(result, str)

    def test_process_unicode(self, processor):
        """Test processing unicode text"""
        result = processor.process_contractions("I'm 世界")
        assert isinstance(result, str)
