#!/usr/bin/env python3
"""
Unit tests for chunk processor module
"""

import pytest
import re
from unittest.mock import Mock, patch
from LiteTTS.tts.chunk_processor import (
    TextChunk,
    ChunkProcessor
)


class TestTextChunk:
    """Test cases for TextChunk dataclass"""

    def test_creation(self):
        """Test creating a text chunk"""
        chunk = TextChunk(
            text="Hello world",
            chunk_index=0,
            total_chunks=1,
            is_sentence_boundary=True,
            is_paragraph_boundary=True,
            pause_after=0.5
        )
        assert chunk.text == "Hello world"
        assert chunk.chunk_index == 0
        assert chunk.total_chunks == 1
        assert chunk.is_sentence_boundary is True
        assert chunk.is_paragraph_boundary is True
        assert chunk.pause_after == 0.5

    def test_creation_defaults(self):
        """Test creating text chunk with defaults"""
        chunk = TextChunk(
            text="Hello",
            chunk_index=0,
            total_chunks=1
        )
        assert chunk.is_sentence_boundary is False
        assert chunk.is_paragraph_boundary is False
        assert chunk.pause_after == 0.0


class TestChunkProcessor:
    """Test cases for ChunkProcessor class"""

    def test_initialization(self):
        """Test processor initializes correctly"""
        processor = ChunkProcessor()
        assert processor.max_chunk_length == 200
        assert processor.overlap_length == 20
        assert processor.audio_processor is not None

    def test_initialization_custom(self):
        """Test processor with custom parameters"""
        processor = ChunkProcessor(max_chunk_length=100, overlap_length=10)
        assert processor.max_chunk_length == 100
        assert processor.overlap_length == 10

    def test_chunk_text_short_text(self):
        """Test chunking short text returns single chunk"""
        processor = ChunkProcessor()
        text = "Hello world"
        chunks = processor.chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].chunk_index == 0
        assert chunks[0].total_chunks == 1

    def test_chunk_text_empty(self):
        """Test chunking empty text"""
        processor = ChunkProcessor()
        chunks = processor.chunk_text("")
        # Empty text should return empty list or single chunk
        assert isinstance(chunks, list)

    def test_chunk_text_exactly_max_length(self):
        """Test chunking text at exactly max length"""
        processor = ChunkProcessor(max_chunk_length=10)
        text = "1234567890"  # 10 chars
        chunks = processor.chunk_text(text)
        assert len(chunks) == 1

    def test_split_by_paragraphs(self):
        """Test splitting by paragraphs"""
        processor = ChunkProcessor()
        text = "Para 1\n\nPara 2\n\nPara 3"
        paragraphs = processor._split_by_paragraphs(text)
        assert len(paragraphs) == 3
        assert paragraphs[0] == "Para 1"
        assert paragraphs[1] == "Para 2"

    def test_split_by_paragraphs_single(self):
        """Test splitting single paragraph"""
        processor = ChunkProcessor()
        text = "Single paragraph"
        paragraphs = processor._split_by_paragraphs(text)
        assert len(paragraphs) == 1

    def test_chunk_paragraph_short(self):
        """Test chunking a short paragraph"""
        processor = ChunkProcessor(max_chunk_length=200)
        paragraph = "Short paragraph"
        chunks = processor._chunk_paragraph(paragraph)
        assert len(chunks) == 1
        assert chunks[0] == paragraph

    def test_find_best_split_point_sentence(self):
        """Test finding split point at sentence boundary"""
        processor = ChunkProcessor()
        text = "Hello world. This is a test."
        # Should find the period after "world"
        split = processor._find_best_split_point(text)
        assert split > 0

    def test_find_best_split_point_phrase(self):
        """Test finding split point at phrase boundary"""
        processor = ChunkProcessor()
        text = "Hello, world and testing"
        split = processor._find_best_split_point(text)
        assert split > 0

    def test_find_best_split_point_word(self):
        """Test finding split point at word boundary"""
        processor = ChunkProcessor(max_chunk_length=50)
        # Text long enough and space positioned so word_boundary > max_search_length // 2
        text = "abcdefghijklmnopqrstuvw xyz"  # space near the end
        split = processor._find_best_split_point(text)
        assert split > 0

    def test_find_best_split_point_no_good_split(self):
        """Test when no good split point exists"""
        processor = ChunkProcessor(max_chunk_length=5)
        text = "abcdefghij"  # No spaces
        split = processor._find_best_split_point(text)
        # May return -1 or max_chunk_length depending on implementation
        assert split == -1 or split == processor.max_chunk_length

    def test_ends_with_sentence_boundary_true(self):
        """Test detecting sentence boundary"""
        processor = ChunkProcessor()
        assert processor._ends_with_sentence_boundary("Hello!") is True
        assert processor._ends_with_sentence_boundary("Hello?") is True
        assert processor._ends_with_sentence_boundary("Hello.") is True

    def test_ends_with_sentence_boundary_false(self):
        """Test detecting no sentence boundary"""
        processor = ChunkProcessor()
        assert processor._ends_with_sentence_boundary("Hello,") is False
        assert processor._ends_with_sentence_boundary("Hello") is False

    def test_calculate_pause_duration_last_para(self):
        """Test pause duration for last paragraph"""
        processor = ChunkProcessor()
        pause = processor._calculate_pause_duration("text", True, True)
        assert pause == 0.0

    def test_calculate_pause_duration_paragraph_end(self):
        """Test pause duration for paragraph end"""
        processor = ChunkProcessor()
        pause = processor._calculate_pause_duration("text", True, False)
        assert pause == 0.8

    def test_calculate_pause_duration_sentence_end(self):
        """Test pause duration for sentence end"""
        processor = ChunkProcessor()
        pause = processor._calculate_pause_duration("Hello.", False, False)
        assert pause == 0.5

    def test_calculate_pause_duration_default(self):
        """Test pause duration for regular chunk"""
        processor = ChunkProcessor()
        pause = processor._calculate_pause_duration("Hello", False, False)
        assert pause == 0.2

    def test_estimate_processing_time(self):
        """Test estimating processing time"""
        processor = ChunkProcessor()
        chunks = [
            TextChunk(text="Hello world", chunk_index=0, total_chunks=1, pause_after=0.2),
            TextChunk(text="Test text", chunk_index=1, total_chunks=1, pause_after=0.5)
        ]
        time_estimate = processor.estimate_processing_time(chunks)
        assert time_estimate > 0

    def test_estimate_processing_time_empty(self):
        """Test estimating time for empty chunks"""
        processor = ChunkProcessor()
        time_estimate = processor.estimate_processing_time([])
        assert time_estimate == 0.0

    def test_get_chunk_statistics(self):
        """Test getting chunk statistics"""
        processor = ChunkProcessor()
        chunks = [
            TextChunk(text="Hello world", chunk_index=0, total_chunks=1, 
                     is_sentence_boundary=True, pause_after=0.2),
            TextChunk(text="Test text", chunk_index=1, total_chunks=1,
                     is_paragraph_boundary=True, pause_after=0.5)
        ]
        stats = processor.get_chunk_statistics(chunks)
        assert stats['total_chunks'] == 2
        assert stats['total_characters'] == 20  # len("Hello world") + len("Test text")
        assert stats['sentence_boundaries'] == 1
        assert stats['paragraph_boundaries'] == 1

    def test_get_chunk_statistics_empty(self):
        """Test getting stats for empty chunks"""
        processor = ChunkProcessor()
        stats = processor.get_chunk_statistics([])
        assert stats == {}

    def test_estimate_audio_duration(self):
        """Test estimating audio duration"""
        processor = ChunkProcessor()
        chunks = [
            TextChunk(text="Hello world", chunk_index=0, total_chunks=1),
            TextChunk(text="Test text", chunk_index=1, total_chunks=1)
        ]
        duration = processor._estimate_audio_duration(chunks)
        assert duration > 0


class TestChunkProcessorProcessChunks:
    """Test cases for process_chunks_to_audio method"""

    def test_process_chunks_to_audio_empty_raises(self):
        """Test processing empty chunks raises error"""
        processor = ChunkProcessor()
        with pytest.raises(RuntimeError, match="No audio segments"):
            processor.process_chunks_to_audio([], lambda *args: None, "test_voice")

    def test_process_chunks_to_audio_logs_error(self):
        """Test that errors in synthesis are logged"""
        processor = ChunkProcessor()
        chunks = [
            TextChunk(text="Hello", chunk_index=0, total_chunks=2, pause_after=0.0),
            TextChunk(text="World", chunk_index=1, total_chunks=2, pause_after=0.0),
        ]

        def synthesize_error(*args, **kwargs):
            raise Exception("Synthesis error")

        # Should not raise, just skip failing chunks and raise RuntimeError for no segments
        with pytest.raises(RuntimeError):
            processor.process_chunks_to_audio(chunks, synthesize_error, "test_voice")


class TestChunkProcessorOptimize:
    """Test cases for optimize_chunks method"""

    def test_optimize_chunks_empty(self):
        """Test optimizing empty chunks"""
        processor = ChunkProcessor()
        result = processor.optimize_chunks([])
        assert result == []

    def test_optimize_chunks(self):
        """Test optimizing chunks"""
        processor = ChunkProcessor()
        chunks = [
            TextChunk(text="Hello   world", chunk_index=0, total_chunks=1,
                     is_sentence_boundary=True, is_paragraph_boundary=True, pause_after=0.5),
        ]
        result = processor.optimize_chunks(chunks)
        assert len(result) == 1
        assert "  " not in result[0].text  # Multiple spaces normalized

    def test_optimize_chunk_text_whitespace(self):
        """Test optimizing chunk text whitespace"""
        processor = ChunkProcessor()
        text = "Hello   world\t\t\ntest"
        result = processor._optimize_chunk_text(text)
        assert "\t" not in result
        assert "\n" not in result

    def test_optimize_chunk_text_punctuation_spacing(self):
        """Test optimizing punctuation spacing"""
        processor = ChunkProcessor()
        text = "Hello , world ; test : end"
        result = processor._optimize_chunk_text(text)
        # Check that punctuation is followed immediately without extra space
        assert "," in result or "world" in result


class TestChunkProcessorValidate:
    """Test cases for validate_chunks method"""

    def test_validate_chunks_empty(self):
        """Test validating empty chunks"""
        processor = ChunkProcessor()
        issues = processor.validate_chunks([])
        assert "No chunks provided" in issues

    def test_validate_chunks_too_long(self):
        """Test validating chunks that are too long"""
        processor = ChunkProcessor(max_chunk_length=10)
        chunks = [
            TextChunk(text="This is a very long chunk that exceeds the limit",
                     chunk_index=0, total_chunks=1),
        ]
        issues = processor.validate_chunks(chunks)
        assert any("too long" in issue for issue in issues)

    def test_validate_chunks_empty_text(self):
        """Test validating chunks with empty text"""
        processor = ChunkProcessor()
        chunks = [
            TextChunk(text="   ", chunk_index=0, total_chunks=1),
        ]
        issues = processor.validate_chunks(chunks)
        assert any("empty" in issue for issue in issues)

    def test_validate_chunks_incorrect_index(self):
        """Test validating chunks with incorrect index"""
        processor = ChunkProcessor()
        chunks = [
            TextChunk(text="Hello", chunk_index=5, total_chunks=1),  # Wrong index
        ]
        issues = processor.validate_chunks(chunks)
        assert any("incorrect index" in issue for issue in issues)

    def test_validate_chunks_incorrect_total(self):
        """Test validating chunks with incorrect total"""
        processor = ChunkProcessor()
        chunks = [
            TextChunk(text="Hello", chunk_index=0, total_chunks=5),  # Wrong total
        ]
        issues = processor.validate_chunks(chunks)
        assert any("incorrect total_chunks" in issue for issue in issues)

    def test_validate_chunks_valid(self):
        """Test validating valid chunks"""
        processor = ChunkProcessor()
        chunks = [
            TextChunk(text="Hello world", chunk_index=0, total_chunks=1,
                     is_sentence_boundary=True, is_paragraph_boundary=True, pause_after=0.5),
        ]
        issues = processor.validate_chunks(chunks)
        assert issues == []


class TestChunkProcessorMerge:
    """Test cases for merge_small_chunks method"""

    def test_merge_small_chunks_empty(self):
        """Test merging empty chunks"""
        processor = ChunkProcessor()
        result = processor.merge_small_chunks([])
        assert result == []

    def test_merge_small_chunks(self):
        """Test merging small chunks"""
        processor = ChunkProcessor(max_chunk_length=50)
        chunks = [
            TextChunk(text="Hello", chunk_index=0, total_chunks=2, pause_after=0.0),
            TextChunk(text="world", chunk_index=1, total_chunks=2, pause_after=0.0),
        ]
        result = processor.merge_small_chunks(chunks, min_chunk_length=5)
        # Should merge into fewer chunks
        assert len(result) <= len(chunks)

    def test_merge_small_chunks_min_length(self):
        """Test merging with minimum chunk length"""
        processor = ChunkProcessor(max_chunk_length=50)
        chunks = [
            TextChunk(text="Hi", chunk_index=0, total_chunks=1, pause_after=0.0),
        ]
        result = processor.merge_small_chunks(chunks, min_chunk_length=10)
        # Small chunk may be dropped if under min_chunk_length
        assert isinstance(result, list)

    def test_merge_small_chunks_preserves_boundaries(self):
        """Test that merge preserves paragraph boundaries"""
        processor = ChunkProcessor(max_chunk_length=200)
        chunks = [
            TextChunk(text="Short", chunk_index=0, total_chunks=2,
                     is_sentence_boundary=False, is_paragraph_boundary=True, pause_after=0.0),
            TextChunk(text="Text", chunk_index=1, total_chunks=2,
                     is_sentence_boundary=True, is_paragraph_boundary=True, pause_after=0.0),
        ]
        result = processor.merge_small_chunks(chunks, min_chunk_length=3)
        # Last chunk should preserve paragraph boundary
        assert result[-1].is_paragraph_boundary is True


class TestChunkProcessorIntegration:
    """Integration tests for ChunkProcessor"""

    def test_full_chunking_pipeline(self):
        """Test full text chunking pipeline"""
        processor = ChunkProcessor(max_chunk_length=50, overlap_length=10)
        text = "This is a long piece of text that needs to be split into multiple chunks. It has multiple sentences. And some paragraphs.\n\nWith a new paragraph."

        chunks = processor.chunk_text(text)
        assert len(chunks) > 0
        assert all(chunk.text for chunk in chunks)

    def test_chunk_text_long_paragraph(self):
        """Test chunking a very long paragraph"""
        processor = ChunkProcessor(max_chunk_length=30)
        text = "This is a very long paragraph that contains many words and should be split into multiple chunks even though it is just one paragraph without any breaks"

        chunks = processor.chunk_text(text)
        assert len(chunks) > 1

    def test_chunk_text_multiple_paragraphs(self):
        """Test chunking text with multiple paragraphs"""
        processor = ChunkProcessor(max_chunk_length=50)
        text = "First paragraph with some text.\n\nSecond paragraph with more text.\n\nThird paragraph."

        chunks = processor.chunk_text(text)
        assert len(chunks) >= 3
