#!/usr/bin/env python3
"""
Unit tests for chunk processor
"""

import pytest
from LiteTTS.tts.chunk_processor import ChunkProcessor, TextChunk


class TestChunkProcessor:
    """Test cases for ChunkProcessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return ChunkProcessor(max_chunk_length=100, overlap_length=10)

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None
        assert processor.max_chunk_length == 100
        assert processor.overlap_length == 10

    def test_chunk_text(self, processor):
        """Test chunking text"""
        result = processor.chunk_text("Hello world. This is a test.")
        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], TextChunk)

    def test_find_best_split_point(self, processor):
        """Test finding best split point"""
        result = processor._find_best_split_point("Hello world. This is a test.")
        assert isinstance(result, int)
        assert result >= 0

    def test_ends_with_sentence_boundary(self, processor):
        """Test sentence boundary detection"""
        result = processor._ends_with_sentence_boundary("Hello world.")
        assert isinstance(result, bool)

    def test_calculate_pause_duration(self, processor):
        """Test pause duration calculation"""
        result = processor._calculate_pause_duration("Hello world.", True, False)
        assert isinstance(result, float)
        assert result >= 0

    def test_get_chunk_statistics(self, processor):
        """Test getting chunk statistics"""
        chunks = processor.chunk_text("Hello world. This is a test.")
        if chunks:
            result = processor.get_chunk_statistics(chunks)
            assert isinstance(result, dict)


class TestChunkProcessorEdgeCases:
    """Edge case tests for ChunkProcessor"""

    @pytest.fixture
    def processor(self):
        return ChunkProcessor(max_chunk_length=50, overlap_length=5)

    def test_chunk_empty_string(self, processor):
        """Test chunking empty string"""
        result = processor.chunk_text("")
        assert isinstance(result, list)

    def test_chunk_short_text(self, processor):
        """Test chunking short text"""
        result = processor.chunk_text("Hi")
        assert isinstance(result, list)

    def test_chunk_long_text(self, processor):
        """Test chunking long text"""
        long_text = "Hello world. " * 50
        result = processor.chunk_text(long_text)
        assert isinstance(result, list)

    def test_chunk_text_with_newlines(self, processor):
        """Test chunking text with newlines"""
        result = processor.chunk_text("Hello world.\n\nThis is a test.")
        assert isinstance(result, list)

    def test_get_stats_with_empty_chunks(self, processor):
        """Test getting stats with empty chunk list"""
        result = processor.get_chunk_statistics([])
        assert isinstance(result, dict)
