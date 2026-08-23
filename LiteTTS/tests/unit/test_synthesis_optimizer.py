#!/usr/bin/env python3
"""
Unit tests for synthesis optimizer module
"""

from LiteTTS.performance.synthesis_optimizer import SynthesisOptimizer, SynthesisPerformanceConfig


class TestSynthesisPerformanceConfig:
    """Test cases for SynthesisPerformanceConfig"""

    def test_creation_defaults(self):
        """Test creating config with defaults"""
        config = SynthesisPerformanceConfig()
        assert config.target_rtf == 0.5
        assert config.critical_rtf_threshold == 1.0
        assert config.enable_fast_path is True
        assert config.fast_path_text_length == 50

    def test_creation_custom(self):
        """Test creating config with custom values"""
        config = SynthesisPerformanceConfig(
            target_rtf=0.3,
            enable_fast_path=False,
            fast_path_text_length=100
        )
        assert config.target_rtf == 0.3
        assert config.enable_fast_path is False


class TestSynthesisOptimizer:
    """Test cases for SynthesisOptimizer"""

    def test_initialization(self):
        """Test optimizer initializes correctly"""
        optimizer = SynthesisOptimizer()
        assert optimizer is not None
        assert optimizer.config.target_rtf == 0.5

    def test_initialization_custom_config(self):
        """Test optimizer with custom config"""
        config = SynthesisPerformanceConfig(target_rtf=0.3)
        optimizer = SynthesisOptimizer(config)
        assert optimizer.config.target_rtf == 0.3

    def test_performance_stats_initialized(self):
        """Test performance stats is initialized"""
        optimizer = SynthesisOptimizer()
        assert optimizer.performance_stats is not None
        assert 'total_requests' in optimizer.performance_stats
        assert 'cache_hits' in optimizer.performance_stats

    def test_caches_initialized(self):
        """Test caches are initialized"""
        optimizer = SynthesisOptimizer()
        assert optimizer.voice_embedding_cache is not None
        assert optimizer.tokenization_cache is not None
        assert optimizer.fast_path_cache is not None
