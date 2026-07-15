#!/usr/bin/env python3
"""
Unit tests for phase6 text processor
"""

import pytest
from LiteTTS.nlp.phase6_text_processor import Phase6TextProcessor, Phase6ProcessingMode, Phase6ProcessingResult


class TestPhase6TextProcessor:
    """Test cases for Phase6TextProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return Phase6TextProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_text(self, processor):
        """Test processing text"""
        result = processor.process_text("Hello world")
        assert isinstance(result, Phase6ProcessingResult)

    def test_process_text_with_mode(self, processor):
        """Test processing text with specific mode"""
        result = processor.process_text("Hello world", Phase6ProcessingMode.ADVANCED)
        assert isinstance(result, Phase6ProcessingResult)


class TestPhase6TextProcessorEdgeCases:
    """Edge case tests for Phase6TextProcessor"""

    @pytest.fixture
    def processor(self):
        return Phase6TextProcessor()

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_text("")
        assert isinstance(result, Phase6ProcessingResult)
