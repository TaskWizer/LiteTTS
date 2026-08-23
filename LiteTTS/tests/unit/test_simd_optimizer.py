#!/usr/bin/env python3
"""
Unit tests for SIMD optimizer module
"""

from LiteTTS.performance.simd_optimizer import (
    SIMDCapabilities,
    SIMDOptimizationConfig,
    SIMDOptimizer,
)


class TestSIMDCapabilities:
    """Test cases for SIMDCapabilities"""

    def test_creation_defaults(self):
        """Test creating capabilities with defaults"""
        caps = SIMDCapabilities()
        assert caps.sse is False
        assert caps.avx is False
        assert caps.vector_width == 1
        assert caps.optimal_instruction_set == "scalar"

    def test_creation_custom(self):
        """Test creating capabilities with custom values"""
        caps = SIMDCapabilities(sse=True, sse2=True, avx=True, avx2=True, vector_width=256)
        assert caps.sse is True
        assert caps.avx2 is True
        assert caps.vector_width == 256


class TestSIMDOptimizationConfig:
    """Test cases for SIMDOptimizationConfig"""

    def test_creation_defaults(self):
        """Test creating config with defaults"""
        config = SIMDOptimizationConfig()
        assert config.enable_vectorization is True
        assert config.vector_chunk_size == 1024
        assert config.alignment_bytes == 32

    def test_creation_custom(self):
        """Test creating config with custom values"""
        config = SIMDOptimizationConfig(
            enable_vectorization=False, vector_chunk_size=2048, force_instruction_set="avx2"
        )
        assert config.enable_vectorization is False
        assert config.vector_chunk_size == 2048


class TestSIMDOptimizer:
    """Test cases for SIMDOptimizer"""

    def test_initialization(self):
        """Test optimizer initializes correctly"""
        optimizer = SIMDOptimizer()
        assert optimizer is not None
        assert optimizer.capabilities is not None

    def test_initialization_custom_config(self):
        """Test optimizer with custom config"""
        config = SIMDOptimizationConfig(vector_chunk_size=2048)
        optimizer = SIMDOptimizer(config)
        assert optimizer.config.vector_chunk_size == 2048
