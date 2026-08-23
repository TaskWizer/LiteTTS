#!/usr/bin/env python3
"""
Unit tests for cold start optimizer
"""

from LiteTTS.performance.cold_start_optimizer import ColdStartOptimizationConfig, ColdStartOptimizer


class TestColdStartOptimizationConfig:
    """Test cases for ColdStartOptimizationConfig"""

    def test_creation_defaults(self):
        """Test creating config with defaults"""
        config = ColdStartOptimizationConfig()
        assert config.enable_aggressive_preloading is True
        assert config.enable_model_caching is True
        assert config.enable_background_warmup is True
        assert config.cache_size_mb == 64

    def test_creation_custom(self):
        """Test creating config with custom values"""
        config = ColdStartOptimizationConfig(
            enable_aggressive_preloading=False,
            cache_size_mb=128,
            warmup_delay_seconds=2.0
        )
        assert config.enable_aggressive_preloading is False
        assert config.cache_size_mb == 128


class TestColdStartOptimizer:
    """Test cases for ColdStartOptimizer"""

    def test_initialization(self):
        """Test optimizer initializes correctly"""
        optimizer = ColdStartOptimizer()
        assert optimizer is not None
        assert optimizer.warmup_completed is False
        assert optimizer.preload_completed is False

    def test_initialization_with_config(self):
        """Test optimizer with custom config"""
        config = ColdStartOptimizationConfig(cache_size_mb=256)
        optimizer = ColdStartOptimizer(config)
        assert optimizer.config.cache_size_mb == 256

    def test_default_warmup_texts(self):
        """Test default warmup texts are set"""
        optimizer = ColdStartOptimizer()
        assert len(optimizer.config.warmup_texts) > 0
        assert "Hello world." in optimizer.config.warmup_texts

    def test_default_preload_voices(self):
        """Test default preload voices are set"""
        optimizer = ColdStartOptimizer()
        assert len(optimizer.config.preload_voices) > 0
        assert "af_heart" in optimizer.config.preload_voices
