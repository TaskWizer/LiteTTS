#!/usr/bin/env python3
"""
Unit tests for health monitor
"""

import pytest
from LiteTTS.monitoring.health_monitor import HealthMonitor, SystemHealth, HealthStatus


class TestHealthMonitor:
    """Test cases for HealthMonitor"""

    @pytest.fixture
    def monitor(self):
        """Create health monitor instance"""
        return HealthMonitor(check_interval=30)

    def test_initialization(self, monitor):
        """Test monitor initializes correctly"""
        assert monitor is not None

    def test_register_health_checker(self, monitor):
        """Test registering a health checker"""
        def dummy_checker():
            return HealthStatus(name="test", status="healthy", message="OK")
        monitor.register_health_checker("test_check", dummy_checker)
        assert "test_check" in monitor.health_checkers

    def test_perform_health_check(self, monitor):
        """Test performing health check"""
        result = monitor.perform_health_check()
        assert isinstance(result, SystemHealth)

    def test_get_health_status(self, monitor):
        """Test getting health status"""
        result = monitor.get_health_status()
        assert isinstance(result, dict)

    def test_get_health_summary(self, monitor):
        """Test getting health summary"""
        result = monitor.get_health_summary()
        assert isinstance(result, dict)


class TestHealthMonitorEdgeCases:
    """Edge case tests for HealthMonitor"""

    @pytest.fixture
    def monitor(self):
        return HealthMonitor(check_interval=30)

    def test_register_multiple_checkers(self, monitor):
        """Test registering multiple health checkers"""
        def checker1():
            return HealthStatus(name="test1", status="healthy", message="OK")
        def checker2():
            return HealthStatus(name="test2", status="healthy", message="OK")
        monitor.register_health_checker("check1", checker1)
        monitor.register_health_checker("check2", checker2)
        assert len(monitor.health_checkers) >= 2

    def test_get_health_status_empty(self, monitor):
        """Test getting health status with no checkers"""
        result = monitor.get_health_status()
        assert isinstance(result, dict)
