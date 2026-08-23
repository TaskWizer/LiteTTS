#!/usr/bin/env python3
"""
Unit tests for RTF performance monitor
"""

import pytest

from LiteTTS.monitoring.rtf_monitor import RTFPerformanceMonitor


class TestRTFMonitor:
    """Test cases for RTFPerformanceMonitor"""

    @pytest.fixture
    def monitor(self):
        """Create RTF monitor instance"""
        return RTFPerformanceMonitor(window_size=50)

    def test_initialization(self, monitor):
        """Test monitor initializes correctly"""
        assert monitor is not None
        assert monitor.window_size == 50

    def test_record_request(self, monitor):
        """Test recording a request"""
        monitor.record_request(rtf=0.5, response_time=1.0, audio_duration=2.0)
        assert monitor.metrics["total_requests"] == 1

    def test_record_multiple_requests(self, monitor):
        """Test recording multiple requests"""
        for i in range(10):
            monitor.record_request(rtf=0.5, response_time=1.0, audio_duration=2.0)
        assert monitor.metrics["total_requests"] == 10

    def test_get_metrics(self, monitor):
        """Test getting metrics"""
        monitor.record_request(rtf=0.5, response_time=1.0, audio_duration=2.0)
        result = monitor.get_metrics()
        assert isinstance(result, dict)

    def test_get_rtf_trend(self, monitor):
        """Test getting RTF trend"""
        monitor.record_request(rtf=0.5, response_time=1.0, audio_duration=2.0)
        result = monitor.get_rtf_trend()
        assert isinstance(result, list)

    def test_reset_metrics(self, monitor):
        """Test resetting metrics"""
        monitor.record_request(rtf=0.5, response_time=1.0, audio_duration=2.0)
        monitor.reset_metrics()
        assert monitor.metrics["total_requests"] == 0


class TestRTFMonitorEdgeCases:
    """Edge case tests for RTFPerformanceMonitor"""

    @pytest.fixture
    def monitor(self):
        return RTFPerformanceMonitor(window_size=10)

    def test_get_metrics_with_no_data(self, monitor):
        """Test getting metrics with no recorded data"""
        result = monitor.get_metrics()
        assert isinstance(result, dict)

    def test_get_rtf_trend_with_no_data(self, monitor):
        """Test getting RTF trend with no data"""
        result = monitor.get_rtf_trend()
        assert isinstance(result, list)

    def test_reset_with_no_data(self, monitor):
        """Test resetting with no data"""
        monitor.reset_metrics()
        assert monitor.metrics["total_requests"] == 0

    def test_record_extreme_rtf_values(self, monitor):
        """Test recording extreme RTF values"""
        monitor.record_request(rtf=0.01, response_time=0.1, audio_duration=10.0)
        monitor.record_request(rtf=5.0, response_time=10.0, audio_duration=2.0)
        assert monitor.metrics["total_requests"] == 2
