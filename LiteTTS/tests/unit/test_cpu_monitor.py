#!/usr/bin/env python3
"""
Unit tests for CPU monitor
"""

from LiteTTS.performance.cpu_monitor import CPUAllocation, CPUThresholds


class TestCPUThresholds:
    """Test cases for CPUThresholds"""

    def test_creation_defaults(self):
        """Test creating CPU thresholds with defaults"""
        thresholds = CPUThresholds()
        assert thresholds.cpu_target == 75.0
        assert thresholds.hysteresis_factor == 0.6
        assert thresholds.monitoring_interval == 1.0

    def test_creation_custom(self):
        """Test creating CPU thresholds with custom values"""
        thresholds = CPUThresholds(cpu_target=80.0, hysteresis_factor=0.5, monitoring_interval=2.0)
        assert thresholds.cpu_target == 80.0
        assert thresholds.hysteresis_factor == 0.5


class TestCPUAllocation:
    """Test cases for CPUAllocation"""

    def test_creation(self):
        """Test creating CPU allocation"""
        allocation = CPUAllocation(
            total_cores=8,
            allocated_cores=4,
            utilization_percent=50.0,
            timestamp=1234567890.0,
            inter_op_threads=2,
            intra_op_threads=2,
            allocation_reason="test",
        )
        assert allocation.total_cores == 8
        assert allocation.allocated_cores == 4
        assert allocation.utilization_percent == 50.0
