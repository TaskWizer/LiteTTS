#!/usr/bin/env python3
"""
Unit tests for model optimizer module
"""

from LiteTTS.performance.model_optimizer import ModelOptimizationConfig, ModelOptimizer


class TestModelOptimizationConfig:
    """Test cases for ModelOptimizationConfig"""

    def test_creation_defaults(self):
        """Test creating config with defaults"""
        config = ModelOptimizationConfig()
        assert config.reduce_mel_bins is True
        assert config.target_mel_bins == 64
        assert config.enable_quantization is True
        assert config.prefer_q4_model is True

    def test_creation_custom(self):
        """Test creating config with custom values"""
        config = ModelOptimizationConfig(
            target_mel_bins=80, enable_quantization=False, short_text_threshold=30
        )
        assert config.target_mel_bins == 80
        assert config.enable_quantization is False


class TestModelOptimizer:
    """Test cases for ModelOptimizer"""

    def test_initialization(self):
        """Test optimizer initializes correctly"""
        optimizer = ModelOptimizer()
        assert optimizer is not None
        assert optimizer.warm_up_completed is False

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
