#!/usr/bin/env python3
"""
Unit tests for memory optimization module
"""

from LiteTTS.performance.memory_optimization import MemoryOptimizationConfig, MemoryProfile


class TestMemoryProfile:
    """Test cases for MemoryProfile"""

    def test_creation(self):
        """Test creating memory profile"""
        profile = MemoryProfile(
            total_memory_mb=16384.0,
            available_memory_mb=8192.0,
            used_memory_mb=8192.0,
            process_memory_mb=512.0,
            process_memory_percent=3.1,
            peak_memory_mb=600.0,
            memory_growth_mb=10.0,
            gc_collections={"gen0": 100, "gen1": 10, "gen2": 1},
            largest_objects=[],
        )
        assert profile.total_memory_mb == 16384.0
        assert profile.process_memory_mb == 512.0

    def test_creation_defaults(self):
        """Test creating memory profile with defaults"""
        profile = MemoryProfile(
            total_memory_mb=16384.0,
            available_memory_mb=8192.0,
            used_memory_mb=8192.0,
            process_memory_mb=512.0,
            process_memory_percent=3.1,
            peak_memory_mb=600.0,
            memory_growth_mb=10.0,
            gc_collections={},
            largest_objects=[],
        )
        assert profile.gc_collections == {}


class TestMemoryOptimizationConfig:
    """Test cases for MemoryOptimizationConfig"""

    def test_creation(self):
        """Test creating memory optimization config"""
        config = MemoryOptimizationConfig(
            enable_pre_allocation=True,
            pre_allocation_size_mb=256,
            enable_memory_pooling=True,
            pool_size_mb=512,
            enable_aggressive_gc=True,
            gc_threshold_mb=100,
            enable_memory_mapping=False,
            cache_size_limit_mb=1024,
            enable_lazy_loading=True,
            memory_monitoring_interval=1.0,
        )
        assert config.enable_pre_allocation is True
        assert config.pre_allocation_size_mb == 256
        assert config.pool_size_mb == 512
