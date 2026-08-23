#!/usr/bin/env python3
"""
Unit tests for performance profiler module
"""

import time

from LiteTTS.performance.profiler import PerformanceMetrics, PerformanceProfiler, ProfilingSession


class TestPerformanceMetrics:
    """Test cases for PerformanceMetrics"""

    def test_creation(self):
        """Test creating performance metrics"""
        metrics = PerformanceMetrics(
            operation_name="test_op",
            execution_time=0.5,
            memory_usage_mb=100.0,
            cpu_percent=25.0
        )
        assert metrics.operation_name == "test_op"
        assert metrics.execution_time == 0.5

    def test_creation_with_defaults(self):
        """Test creating metrics with defaults"""
        metrics = PerformanceMetrics(
            operation_name="test_op",
            execution_time=0.5,
            memory_usage_mb=100.0,
            cpu_percent=25.0
        )
        assert metrics.rtf == 0.0
        assert metrics.text_length == 0


class TestProfilingSession:
    """Test cases for ProfilingSession"""

    def test_creation(self):
        """Test creating profiling session"""
        session = ProfilingSession(
            session_id="test_001",
            start_time=time.time(),
            end_time=time.time() + 10.0,
            total_duration=10.0
        )
        assert session.session_id == "test_001"
        assert session.total_duration == 10.0


class TestPerformanceProfiler:
    """Test cases for PerformanceProfiler"""

    def test_initialization(self):
        """Test profiler initializes correctly"""
        profiler = PerformanceProfiler()
        assert profiler is not None
        assert profiler.enable_memory_tracking is True
        assert profiler.enable_cpu_tracking is True

    def test_initialization_custom(self):
        """Test profiler with custom settings"""
        profiler = PerformanceProfiler(enable_memory_tracking=False)
        assert profiler.enable_memory_tracking is False

    def test_operation_metrics_initialized(self):
        """Test operation metrics is initialized"""
        profiler = PerformanceProfiler()
        assert profiler.operation_metrics is not None
