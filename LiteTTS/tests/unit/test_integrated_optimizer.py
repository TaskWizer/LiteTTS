#!/usr/bin/env python3
"""
Unit tests for integrated optimizer module
"""

from LiteTTS.performance.integrated_optimizer import OptimizationResults, PerformanceTargets


class TestPerformanceTargets:
    """Test cases for PerformanceTargets"""

    def test_creation_defaults(self):
        """Test creating performance targets with defaults"""
        targets = PerformanceTargets()
        assert targets.max_memory_mb == 150
        assert targets.target_rtf == 0.25
        assert targets.max_cpu_usage == 85.0

    def test_creation_custom(self):
        """Test creating performance targets with custom values"""
        targets = PerformanceTargets(
            max_memory_mb=200,
            target_rtf=0.3,
            max_startup_time=15.0
        )
        assert targets.max_memory_mb == 200
        assert targets.target_rtf == 0.3
        assert targets.max_startup_time == 15.0


class TestOptimizationResults:
    """Test cases for OptimizationResults"""

    def test_creation_defaults(self):
        """Test creating optimization results with defaults"""
        results = OptimizationResults()
        assert results.memory_optimized is False
        assert results.cpu_optimized is False
        assert results.memory_reduction_percent == 0.0
        assert results.errors == []

    def test_creation_custom(self):
        """Test creating optimization results with custom values"""
        results = OptimizationResults(
            memory_optimized=True,
            cpu_optimized=True,
            baseline_memory_mb=500.0,
            optimized_memory_mb=350.0,
            memory_reduction_mb=150.0,
            memory_reduction_percent=30.0
        )
        assert results.memory_optimized is True
        assert results.optimized_memory_mb == 350.0
        assert results.memory_reduction_percent == 30.0
