#!/usr/bin/env python3
"""
Unit tests for text chunking module
"""

import pytest
from LiteTTS.audio.chunking import TextChunker, TextChunk, ChunkingConfig, ChunkingStrategy


class TestTextChunker:
    """Test cases for TextChunker"""

    @pytest.fixture
    def chunker(self):
        """Create chunker instance"""
        config = ChunkingConfig(
            max_chunk_size=300,
            min_chunk_size=50,
            overlap_size=20,
            strategy=ChunkingStrategy.SENTENCE,
            enabled=True
        )
        return TextChunker(config)

    def test_initialization(self, chunker):
        """Test chunker initializes correctly"""
        assert chunker is not None
        assert chunker.config.max_chunk_size == 300

    def test_chunk_text_basic(self, chunker):
        """Test basic text chunking"""
        text = "Hello world. This is a test. How are you?"
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
        assert all(isinstance(c, TextChunk) for c in chunks)

    def test_chunk_text_short(self, chunker):
        """Test chunking of short text"""
        text = "Hello."
        chunks = chunker.chunk_text(text)
        assert len(chunks) == 1

    def test_chunk_text_empty(self, chunker):
        """Test chunking of empty string"""
        text = ""
        chunks = chunker.chunk_text(text)
        assert len(chunks) == 0

    def test_chunk_text_whitespace(self, chunker):
        """Test chunking of whitespace-only string"""
        text = "   \t\n  "
        chunks = chunker.chunk_text(text)
        assert len(chunks) == 0

    def test_chunk_boundaries(self, chunker):
        """Test that chunk boundaries are respected"""
        text = "First sentence. Second sentence. Third sentence."
        chunks = chunker.chunk_text(text)
        # All chunks should have valid boundaries
        for chunk in chunks:
            assert chunk.start_position >= 0
            assert chunk.end_position <= len(text)
            assert chunk.start_position <= chunk.end_position

    def test_chunk_ids_unique(self, chunker):
        """Test that chunk IDs are unique"""
        text = "One. Two. Three. Four. Five."
        chunks = chunker.chunk_text(text)
        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))


class TestTextChunk:
    """Test cases for TextChunk dataclass"""

    def test_text_chunk_creation(self):
        """Test TextChunk creation"""
        chunk = TextChunk(
            text="Hello world",
            chunk_id=0,
            start_position=0,
            end_position=11,
            is_sentence_boundary=True,
            is_paragraph_boundary=False
        )
        assert chunk.text == "Hello world"
        assert chunk.chunk_id == 0
        assert chunk.start_position == 0
        assert chunk.end_position == 11
        assert chunk.is_sentence_boundary is True

    def test_text_chunk_defaults(self):
        """Test TextChunk default values"""
        chunk = TextChunk(
            text="Test",
            chunk_id=0,
            start_position=0,
            end_position=4,
            is_sentence_boundary=False,
            is_paragraph_boundary=False
        )
        assert chunk.overlap_text is None or chunk.overlap_text == ""


class TestChunkingConfig:
    """Test cases for ChunkingConfig"""

    def test_config_defaults(self):
        """Test ChunkingConfig default values"""
        config = ChunkingConfig()
        assert config.enabled is True
        assert config.max_chunk_size == 200
        assert config.min_chunk_size == 50
        assert config.overlap_size == 20

    def test_config_custom(self):
        """Test ChunkingConfig with custom values"""
        config = ChunkingConfig(
            max_chunk_size=500,
            min_chunk_size=100,
            overlap_size=50,
            strategy=ChunkingStrategy.PHRASE
        )
        assert config.max_chunk_size == 500
        assert config.min_chunk_size == 100
        assert config.overlap_size == 50
        assert config.strategy == ChunkingStrategy.PHRASE

    def test_config_strategies(self):
        """Test different chunking strategies"""
        for strategy in ChunkingStrategy:
            config = ChunkingConfig(strategy=strategy)
            assert config.strategy == strategy


class TestChunkingEdgeCases:
    """Edge case tests for chunking"""

    @pytest.fixture
    def chunker(self):
        config = ChunkingConfig(max_chunk_size=100, enabled=True)
        return TextChunker(config)

    def test_very_long_sentence(self, chunker):
        """Test chunking of very long single sentence"""
        text = "A" * 500 + "."
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 1

    def test_many_short_sentences(self, chunker):
        """Test chunking of many short sentences"""
        text = "One. Two. Three. Four. Five. Six. Seven. Eight."
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0

    def test_sentence_without_period(self, chunker):
        """Test chunking of sentence without period"""
        text = "Hello world"
        chunks = chunker.chunk_text(text)
        assert len(chunks) >= 1

    def test_only_overlap_marks_sentence_boundary(self, chunker):
        """Test that overlap doesn't incorrectly mark boundaries"""
        text = "Hello. World."
        chunks = chunker.chunk_text(text)
        # At least one chunk should be marked as sentence boundary
        assert any(c.is_sentence_boundary for c in chunks)
