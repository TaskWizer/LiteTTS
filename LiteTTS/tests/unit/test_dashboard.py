#!/usr/bin/env python3
"""
Unit tests for dashboard analytics
"""

from datetime import datetime

import pytest

from LiteTTS.api.dashboard import ConcurrencyMetric, DashboardAnalytics, RequestMetric


class TestDashboardAnalytics:
    """Test cases for DashboardAnalytics"""

    @pytest.fixture
    def dashboard(self):
        """Create dashboard analytics instance"""
        return DashboardAnalytics(max_history=100)

    def test_initialization(self, dashboard):
        """Test dashboard initializes correctly"""
        assert dashboard is not None
        assert dashboard.max_history == 100

    def test_record_request(self, dashboard):
        """Test recording a request"""
        dashboard.record_request(
            method="POST",
            path="/tts",
            status_code=200,
            response_time=0.5,
            client_ip="127.0.0.1",
            user_agent="test",
        )
        assert len(dashboard.request_metrics) == 1

    def test_update_concurrency(self, dashboard):
        """Test updating concurrency metrics"""
        dashboard.update_concurrency(active_connections=5, queue_size=2, processing_requests=3)
        assert dashboard.active_connections == 5

    def test_get_requests_per_minute(self, dashboard):
        """Test getting requests per minute"""
        result = dashboard.get_requests_per_minute(minutes=60)
        assert isinstance(result, list)

    def test_get_response_time_stats(self, dashboard):
        """Test getting response time stats"""
        result = dashboard.get_response_time_stats(minutes=60)
        assert isinstance(result, dict)

    def test_get_error_rates(self, dashboard):
        """Test getting error rates"""
        result = dashboard.get_error_rates(minutes=60)
        assert isinstance(result, dict)

    def test_get_voice_usage_stats(self, dashboard):
        """Test getting voice usage stats"""
        result = dashboard.get_voice_usage_stats(minutes=60)
        assert isinstance(result, dict)

    def test_get_concurrency_stats(self, dashboard):
        """Test getting concurrency stats"""
        result = dashboard.get_concurrency_stats()
        assert isinstance(result, dict)

    def test_get_dashboard_data(self, dashboard):
        """Test getting dashboard data"""
        result = dashboard.get_dashboard_data()
        assert isinstance(result, dict)


class TestRequestMetric:
    """Test cases for RequestMetric"""

    def test_creation(self):
        """Test creating request metric"""
        metric = RequestMetric(
            timestamp=datetime.now(),
            method="POST",
            path="/tts",
            status_code=200,
            response_time=0.5,
            client_ip="127.0.0.1",
            user_agent="test",
        )
        assert metric.method == "POST"
        assert metric.status_code == 200


class TestConcurrencyMetric:
    """Test cases for ConcurrencyMetric"""

    def test_creation(self):
        """Test creating concurrency metric"""
        metric = ConcurrencyMetric(
            timestamp=datetime.now(), active_connections=5, queue_size=2, processing_requests=3
        )
        assert metric.active_connections == 5
