#!/usr/bin/env python3
"""
Unit tests for performance streamer
"""

from LiteTTS.websocket.performance_streamer import PerformanceMetrics, SystemStatus


class TestPerformanceMetrics:
    """Test cases for PerformanceMetrics"""

    def test_creation(self):
        """Test creating performance metrics"""
        metrics = PerformanceMetrics(
            timestamp=1234567890.0,
            rtf=0.5,
            memory_usage_mb=1024.0,
            memory_percent=50.0,
            cpu_percent=25.0,
            active_requests=2,
            total_requests=100,
            cache_hit_rate=0.85,
            processing_time_ms=150.0,
            queue_size=5,
            uptime_seconds=3600.0,
            voices_loaded=3,
            system_load=[1.0, 1.5, 2.0],
        )
        assert metrics.rtf == 0.5
        assert metrics.total_requests == 100


class TestSystemStatus:
    """Test cases for SystemStatus"""

    def test_creation(self):
        """Test creating system status"""
        status = SystemStatus(
            timestamp=1234567890.0,
            status="healthy",
            server_uptime=3600.0,
            total_memory_gb=16.0,
            available_memory_gb=8.0,
            disk_usage_percent=45.0,
            temperature_celsius=65.0,
            gpu_available=False,
            gpu_memory_mb=None,
            active_connections=2,
            error_rate=0.01,
            last_error=None,
        )
        assert status.status == "healthy"
