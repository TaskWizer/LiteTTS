#!/usr/bin/env python3
"""
Unit tests for model optimizer module
"""

import numpy as np
import pytest

from LiteTTS.performance.model_optimizer import (
    ModelOptimizationConfig,
    ModelOptimizer,
    get_model_optimizer,
)


class TestModelOptimizationConfig:
    """Test cases for ModelOptimizationConfig"""

    def test_creation_defaults(self):
        """Test creating config with defaults"""
        config = ModelOptimizationConfig()
        assert config.reduce_mel_bins is True
        assert config.target_mel_bins == 64
        assert config.enable_quantization is True
        assert config.prefer_q4_model is True
        assert config.enable_warm_up is True
        assert config.short_text_fast_path is True
        assert config.short_text_threshold == 20
        assert config.cache_phonemizer is True
        assert config.pipeline_parallelism is True

    def test_creation_custom(self):
        """Test creating config with custom values"""
        config = ModelOptimizationConfig(
            target_mel_bins=80,
            enable_quantization=False,
            short_text_threshold=30,
            reduce_precision=True,
        )
        assert config.target_mel_bins == 80
        assert config.enable_quantization is False
        assert config.short_text_threshold == 30
        assert config.reduce_precision is True


class TestModelOptimizer:
    """Test cases for ModelOptimizer"""

    def test_initialization(self):
        """Test optimizer initializes correctly"""
        optimizer = ModelOptimizer()
        assert optimizer is not None
        assert optimizer.warm_up_completed is False
        assert isinstance(optimizer.phonemizer_cache, dict)
        assert isinstance(optimizer.short_text_cache, dict)

    def test_initialization_with_config(self):
        """Test optimizer with custom config"""
        config = ModelOptimizationConfig(target_mel_bins=80)
        optimizer = ModelOptimizer(config)
        assert optimizer.config.target_mel_bins == 80

    def test_phonemizer_cache_initialized(self):
        """Test phonemizer cache is initialized"""
        optimizer = ModelOptimizer()
        assert optimizer.phonemizer_cache is not None
        assert isinstance(optimizer.phonemizer_cache, dict)

    def test_short_text_cache_initialized(self):
        """Test short text cache is initialized"""
        optimizer = ModelOptimizer()
        assert optimizer.short_text_cache is not None
        assert isinstance(optimizer.short_text_cache, dict)

    def test_optimize_phoneme_processing_disabled(self):
        """Test phoneme processing when disabled"""
        config = ModelOptimizationConfig(cache_phonemizer=False)
        optimizer = ModelOptimizer(config)
        result = optimizer.optimize_phoneme_processing("test", "af_heart")
        assert result is None

    def test_optimize_phoneme_processing_caching(self):
        """Test phoneme processing caching"""
        config = ModelOptimizationConfig(cache_phonemizer=True)
        optimizer = ModelOptimizer(config)

        # First call should return None (no cache)
        result1 = optimizer.optimize_phoneme_processing("hello world", "af_heart")
        assert result1 is None

        # Cache the result
        optimizer.cache_phoneme_result("hello world", "af_heart", "HH AH L OW W ER LD")

        # Now should return cached result
        result2 = optimizer.optimize_phoneme_processing("hello world", "af_heart")
        assert result2 == "HH AH L OW W ER LD"

    def test_cache_phoneme_result_short_text(self):
        """Test caching short text uses short_text_cache"""
        config = ModelOptimizationConfig(cache_phonemizer=True, short_text_threshold=50)
        optimizer = ModelOptimizer(config)

        optimizer.cache_phoneme_result("short", "af_heart", "SH OR T")
        cache_key = "short:af_heart"

        assert cache_key in optimizer.short_text_cache
        assert optimizer.short_text_cache[cache_key] == "SH OR T"

    def test_cache_phoneme_result_long_text(self):
        """Test caching long text uses main cache"""
        config = ModelOptimizationConfig(cache_phonemizer=True, short_text_threshold=5)
        optimizer = ModelOptimizer(config)

        long_text = "This is a longer text that exceeds the threshold"
        optimizer.cache_phoneme_result(long_text, "af_heart", "RESULT")
        cache_key = f"{long_text}:af_heart"

        assert cache_key in optimizer.phonemizer_cache

    def test_optimize_input_preparation(self):
        """Test input preparation optimization"""
        optimizer = ModelOptimizer()
        tokens = np.array([0, 1, 2, 3, 0], dtype=np.int64)
        voice_data = np.zeros((510, 256), dtype=np.float32)
        speed = 1.0

        result = optimizer.optimize_input_preparation(tokens, voice_data, speed)

        assert "input_ids" in result
        assert "style" in result
        assert "speed" in result
        assert result["input_ids"].shape[0] == 1  # batch dimension

    def test_optimize_input_preparation_1d_voice(self):
        """Test input preparation with 1D voice data"""
        optimizer = ModelOptimizer()
        tokens = np.array([0, 1, 2, 0], dtype=np.int64)
        voice_data = np.zeros(256, dtype=np.float32)
        speed = 1.0

        result = optimizer.optimize_input_preparation(tokens, voice_data, speed)
        assert result["style"].shape == (1, 256)

    def test_optimize_input_preparation_voice_510_256(self):
        """Test input preparation with 510x256 voice data"""
        optimizer = ModelOptimizer()
        tokens = np.array([0, 1, 2, 0], dtype=np.int64)
        voice_data = np.zeros((510, 256), dtype=np.float32)
        speed = 1.0

        result = optimizer.optimize_input_preparation(tokens, voice_data, speed)
        assert result["style"].shape == (1, 256)

    def test_warm_up_not_completed_initially(self):
        """Test warm_up_completed is False initially"""
        optimizer = ModelOptimizer()
        assert optimizer.warm_up_completed is False

    def test_get_performance_stats(self):
        """Test getting performance statistics"""
        optimizer = ModelOptimizer()
        stats = optimizer.get_performance_stats()

        assert "warm_up_completed" in stats
        assert "phonemizer_cache_size" in stats
        assert "short_text_cache_size" in stats
        assert "config" in stats
        assert stats["warm_up_completed"] is False
        assert stats["phonemizer_cache_size"] == 0

    def test_optimize_for_text_length_short(self):
        """Test optimization for short text"""
        optimizer = ModelOptimizer()
        opts = optimizer.optimize_for_text_length(10)

        assert opts["use_fast_path"] is True
        assert opts["skip_advanced_processing"] is True
        assert opts["priority_cache"] is True

    def test_optimize_for_text_length_medium(self):
        """Test optimization for medium text"""
        optimizer = ModelOptimizer()
        opts = optimizer.optimize_for_text_length(50)

        assert opts["use_fast_path"] is False
        assert opts["skip_advanced_processing"] is False
        assert opts["priority_cache"] is True

    def test_optimize_for_text_length_long(self):
        """Test optimization for long text"""
        optimizer = ModelOptimizer()
        opts = optimizer.optimize_for_text_length(200)

        assert opts["use_fast_path"] is False
        assert opts["skip_advanced_processing"] is False
        assert opts["priority_cache"] is False
        assert opts["enable_chunking"] is True


class TestGetModelOptimizer:
    """Test get_model_optimizer function"""

    def test_returns_model_optimizer(self):
        """Test get_model_optimizer returns ModelOptimizer"""
        optimizer = get_model_optimizer()
        assert isinstance(optimizer, ModelOptimizer)

    def test_returns_same_instance(self):
        """Test get_model_optimizer returns singleton"""
        optimizer1 = get_model_optimizer()
        optimizer2 = get_model_optimizer()
        assert optimizer1 is optimizer2
