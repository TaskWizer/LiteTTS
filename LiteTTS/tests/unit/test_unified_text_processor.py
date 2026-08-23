#!/usr/bin/env python3
"""
Unit tests for unified text processor
"""

import pytest

from LiteTTS.nlp.unified_text_processor import (
    ProcessingMode,
    ProcessingOptions,
    ProcessingResult,
    UnifiedTextProcessor,
)


class TestUnifiedTextProcessor:
    """Test cases for UnifiedTextProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return UnifiedTextProcessor(enable_advanced_features=False)

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_text_basic(self, processor):
        """Test basic text processing"""
        result = processor.process_text("Hello world")
        assert isinstance(result, ProcessingResult)
        assert isinstance(result.processed_text, str)

    def test_process_text_with_options(self, processor):
        """Test processing with options"""
        options = processor.create_processing_options("basic")
        result = processor.process_text("Hello world", options)
        assert isinstance(result, ProcessingResult)

    def test_processing_options(self, processor):
        """Test creating processing options"""
        options = processor.create_processing_options(ProcessingMode.BASIC)
        assert isinstance(options, ProcessingOptions)

    def test_get_processing_capabilities(self, processor):
        """Test getting processing capabilities"""
        caps = processor.get_processing_capabilities()
        assert isinstance(caps, dict)


class TestUnifiedTextProcessorEdgeCases:
    """Edge case tests for UnifiedTextProcessor"""

    @pytest.fixture
    def processor(self):
        return UnifiedTextProcessor(enable_advanced_features=False)

    def test_process_empty_string(self, processor):
        """Test processing empty string"""
        result = processor.process_text("")
        assert isinstance(result, ProcessingResult)

    def test_process_unicode_text(self, processor):
        """Test processing unicode text"""
        result = processor.process_text("Hello 世界 🌍")
        assert isinstance(result, ProcessingResult)

    def test_process_long_text(self, processor):
        """Test processing long text"""
        long_text = "Hello world. " * 100
        result = processor.process_text(long_text)
        assert isinstance(result, ProcessingResult)

    def test_analyze_text_complexity(self, processor):
        """Test analyzing text complexity"""
        result = processor.analyze_text_complexity("Hello world")
        assert isinstance(result, dict)
