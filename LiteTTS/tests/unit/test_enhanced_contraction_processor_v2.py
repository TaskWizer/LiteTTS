#!/usr/bin/env python3
"""
Unit tests for enhanced contraction processor v2
"""

import pytest

from LiteTTS.nlp.enhanced_contraction_processor_v2 import EnhancedContractionProcessorV2


class TestEnhancedContractionProcessorV2:
    """Test cases for EnhancedContractionProcessorV2"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return EnhancedContractionProcessorV2()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_contractions(self, processor):
        """Test processing contractions"""
        result = processor.process_contractions("I'm happy")
        assert isinstance(result, str)

    def test_analyze_contractions(self, processor):
        """Test analyzing contractions"""
        result = processor.analyze_contractions("I'm happy")
        assert isinstance(result, dict)

    def test_get_phonetic_guidance(self, processor):
        """Test getting phonetic guidance"""
        result = processor.get_phonetic_guidance("I'm")
        # Result can be None or dict
        assert result is None or isinstance(result, dict)

    def test_get_statistics(self, processor):
        """Test getting statistics"""
        result = processor.get_statistics()
        assert isinstance(result, dict)


class TestEnhancedContractionProcessorV2EdgeCases:
    """Edge case tests for EnhancedContractionProcessorV2"""

    @pytest.fixture
    def processor(self):
        return EnhancedContractionProcessorV2()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_contractions("")
        assert isinstance(result, str)

    def test_process_no_contractions(self, processor):
        """Test processing text without contractions"""
        result = processor.process_contractions("Hello world")
        assert isinstance(result, str)
