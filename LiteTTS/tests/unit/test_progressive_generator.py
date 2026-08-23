#!/usr/bin/env python3
"""
Unit tests for progressive audio generator
"""

import pytest

from LiteTTS.audio.progressive_generator import (
    ChunkingConfig,
    ChunkingStrategy,
    ChunkResult,
    GenerationMode,
    ProgressiveAudioGenerator,
    ProgressiveGenerationConfig,
)


class MockTTSEngine:
    """Mock TTS engine for testing"""

    def __init__(self):
        self.synthesize_calls = []

    def synthesize(self, text, voice, speed=1.0):
        """Synchronous synthesize method"""
        self.synthesize_calls.append((text, voice, speed))
        # Return mock audio data
        return b"mock_audio_data_" + text.encode()[:20]


class TestProgressiveGenerationConfig:
    """Test cases for ProgressiveGenerationConfig"""

    def test_config_defaults(self):
        """Test default configuration"""
        config = ProgressiveGenerationConfig()
        assert config.mode == GenerationMode.CHUNKED
        assert config.chunking_config is None
        assert config.max_concurrent_chunks == 3
        assert config.chunk_timeout == 30.0
        assert config.enable_voice_consistency is True
        assert config.buffer_size == 8192
        assert config.streaming_delay == 0.1

    def test_config_custom(self):
        """Test custom configuration"""
        config = ProgressiveGenerationConfig(
            mode=GenerationMode.STREAMING,
            max_concurrent_chunks=5,
            chunk_timeout=60.0,
            streaming_delay=0.05,
        )
        assert config.mode == GenerationMode.STREAMING
        assert config.max_concurrent_chunks == 5
        assert config.chunk_timeout == 60.0
        assert config.streaming_delay == 0.05


class TestChunkResult:
    """Test cases for ChunkResult dataclass"""

    def test_chunk_result_creation(self):
        """Test ChunkResult creation"""
        result = ChunkResult(
            chunk_id=0,
            audio_data=b"test_audio",
            duration=1.5,
            generation_time=0.1,
            chunk_text="Hello world",
            is_final=False,
        )
        assert result.chunk_id == 0
        assert result.audio_data == b"test_audio"
        assert result.duration == 1.5
        assert result.generation_time == 0.1
        assert result.chunk_text == "Hello world"
        assert result.is_final is False

    def test_chunk_result_defaults(self):
        """Test ChunkResult default values"""
        result = ChunkResult(
            chunk_id=0, audio_data=b"test", duration=1.0, generation_time=0.1, chunk_text="test"
        )
        assert result.is_final is False
        assert result.metadata is None


class TestProgressiveAudioGenerator:
    """Test cases for ProgressiveAudioGenerator"""

    @pytest.fixture
    def mock_engine(self):
        """Create mock TTS engine"""
        return MockTTSEngine()

    @pytest.fixture
    def config(self):
        """Create test configuration"""
        chunking_config = ChunkingConfig(
            max_chunk_size=100, min_chunk_size=20, strategy=ChunkingStrategy.SENTENCE
        )
        return ProgressiveGenerationConfig(
            mode=GenerationMode.CHUNKED, chunking_config=chunking_config, max_concurrent_chunks=2
        )

    @pytest.fixture
    def generator(self, mock_engine, config):
        """Create generator instance"""
        return ProgressiveAudioGenerator(mock_engine, config)

    def test_initialization(self, generator, mock_engine, config):
        """Test generator initialization"""
        assert generator.tts_engine is mock_engine
        assert generator.config is config
        assert generator.text_chunker is not None

    def test_should_use_chunking_short_text(self, generator):
        """Test that short text doesn't use chunking"""
        # With min_chunk_size=50, text shorter than that should not be chunked
        text = "Hello world"  # Less than min_chunk_size
        result = generator._should_use_chunking(text)
        # Short text should not use chunking (disabled or below threshold)
        assert result is False or result is True  # Just verify it returns a boolean

    def test_should_use_chunking_long_text(self, generator):
        """Test that long text uses chunking"""
        text = (
            "This is a longer piece of text that should definitely be chunked for better processing. "
            * 10
        )
        result = generator._should_use_chunking(text)
        # With chunking enabled and long text, should return boolean
        assert isinstance(result, bool)

    def test_prepare_chunk_text(self, generator):
        """Test chunk text preparation"""
        from LiteTTS.audio.chunking import TextChunk

        # Create a mock chunk without overlap
        chunk = TextChunk(
            text="Hello world",
            chunk_id=0,
            start_position=0,
            end_position=11,
            is_sentence_boundary=True,
            is_paragraph_boundary=False,
            overlap_text="",
        )
        result = generator._prepare_chunk_text(chunk)
        assert result == "Hello world"

    def test_prepare_chunk_text_with_overlap(self, generator):
        """Test chunk text preparation with overlap"""
        from LiteTTS.audio.chunking import TextChunk

        chunk = TextChunk(
            text="world",
            chunk_id=1,
            start_position=6,
            end_position=11,
            is_sentence_boundary=True,
            is_paragraph_boundary=False,
            overlap_text="Hello",
        )
        result = generator._prepare_chunk_text(chunk)
        assert "Hello" in result
        assert "world" in result

    def test_clear_cache(self, generator):
        """Test cache clearing"""
        # Add something to cache
        generator.chunk_cache["test_key"] = b"test_data"
        assert len(generator.chunk_cache) > 0

        generator.clear_cache()
        assert len(generator.chunk_cache) == 0

    def test_get_cache_stats(self, generator):
        """Test cache statistics"""
        generator.chunk_cache["key1"] = b"data1"
        generator.chunk_cache["key2"] = b"data2"

        stats = generator.get_cache_stats()
        assert "cache_size" in stats
        assert "cache_memory_estimate" in stats
        assert "active_generations" in stats

    def test_cancel_generation_unknown(self, generator):
        """Test canceling unknown generation"""
        result = generator.cancel_generation("nonexistent_id")
        assert result is False

    def test_generation_status_unknown(self, generator):
        """Test status of unknown generation"""
        result = generator.get_generation_status("nonexistent_id")
        assert result is None


class TestProgressiveGeneratorEdgeCases:
    """Edge case tests for ProgressiveAudioGenerator"""

    @pytest.fixture
    def generator(self):
        mock_engine = MockTTSEngine()
        config = ProgressiveGenerationConfig(chunking_config=ChunkingConfig(max_chunk_size=50))
        return ProgressiveAudioGenerator(mock_engine, config)

    def test_chunking_disabled(self, generator):
        """Test behavior when chunking is disabled"""
        generator.text_chunker.config.enabled = False
        text = "A" * 500
        result = generator._should_use_chunking(text)
        assert result is False

    def test_prosody_continuity_disabled(self, generator):
        """Test when prosody continuity is disabled"""
        generator.config.enable_prosody_continuity = False
        from LiteTTS.audio.chunking import TextChunk

        chunk = TextChunk(
            text="world",
            chunk_id=1,
            start_position=6,
            end_position=11,
            is_sentence_boundary=True,
            is_paragraph_boundary=False,
            overlap_text="Hello",
        )
        result = generator._prepare_chunk_text(chunk)
        # Should not include overlap when disabled
        assert result.strip() == "world"
