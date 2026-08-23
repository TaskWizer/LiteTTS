#!/usr/bin/env python3
"""
Unit tests for chunked performance monitor
"""

import pytest

from LiteTTS.monitoring.chunked_performance import ChunkedPerformanceMonitor, GenerationType


class TestChunkedPerformanceMonitor:
    """Test cases for ChunkedPerformanceMonitor"""

    @pytest.fixture
    def monitor(self):
        """Create monitor instance"""
        return ChunkedPerformanceMonitor(max_history=100)

    def test_initialization(self, monitor):
        """Test monitor initializes correctly"""
        assert monitor is not None
        assert monitor.max_history == 100

    def test_start_generation_tracking(self, monitor):
        """Test starting generation tracking"""
        result = monitor.start_generation_tracking(
            "gen1", GenerationType.STANDARD, "Hello world", "voice1"
        )
        assert isinstance(result, str)

    def test_record_chunk_completion(self, monitor):
        """Test recording chunk completion"""
        gen_id = monitor.start_generation_tracking(
            "gen1", GenerationType.CHUNKED, "Hello world", "voice1", 5
        )
        monitor.record_chunk_completion(gen_id, 1, 0.5, 1000)
        result = monitor.get_real_time_stats()
        assert isinstance(result, dict)

    def test_record_resource_usage(self, monitor):
        """Test recording resource usage"""
        gen_id = monitor.start_generation_tracking(
            "gen1", GenerationType.STANDARD, "Hello world", "voice1"
        )
        monitor.record_resource_usage(gen_id, 100.0, 25.0)
        result = monitor.get_real_time_stats()
        assert isinstance(result, dict)

    def test_complete_generation_tracking(self, monitor):
        """Test completing generation tracking"""
        gen_id = monitor.start_generation_tracking(
            "gen1", GenerationType.CHUNKED, "Hello world", "voice1", 3
        )
        monitor.record_chunk_completion(gen_id, 1, 0.5, 1000)
        monitor.complete_generation_tracking(gen_id, 5000, 2.0)
        result = monitor.get_real_time_stats()
        assert isinstance(result, dict)

    def test_get_real_time_stats(self, monitor):
        """Test getting real-time stats"""
        result = monitor.get_real_time_stats()
        assert isinstance(result, dict)


class TestChunkedPerformanceEdgeCases:
    """Edge case tests for ChunkedPerformanceMonitor"""

    @pytest.fixture
    def monitor(self):
        return ChunkedPerformanceMonitor(max_history=50)

    def test_get_stats_with_no_data(self, monitor):
        """Test getting stats with no recorded data"""
        result = monitor.get_real_time_stats()
        assert isinstance(result, dict)

    def test_complete_nonexistent_generation(self, monitor):
        """Test completing a nonexistent generation raises error"""
        with pytest.raises(ValueError):
            monitor.complete_generation_tracking("nonexistent_id", 1000, 1.0)

    def test_record_chunk_for_nonexistent_generation(self, monitor):
        """Test recording chunk for nonexistent generation returns None"""
        result = monitor.record_chunk_completion("nonexistent_id", 1, 0.5, 1000)
        assert result is None

    def test_cleanup_old_metrics(self, monitor):
        """Test cleaning up old metrics"""
        result = monitor.cleanup_old_metrics(max_age_hours=24)
        assert isinstance(result, int)
