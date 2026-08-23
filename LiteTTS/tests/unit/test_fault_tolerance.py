#!/usr/bin/env python3
"""
Unit tests for fault tolerance module
"""

from LiteTTS.performance.fault_tolerance import CircuitBreaker, RetryManager


class TestCircuitBreaker:
    """Test cases for CircuitBreaker"""

    def test_initialization(self):
        """Test circuit breaker initializes correctly"""
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        assert cb.failure_threshold == 5
        assert cb.recovery_timeout == 60
        assert cb.state == "CLOSED"

    def test_initialization_custom(self):
        """Test circuit breaker with custom values"""
        cb = CircuitBreaker(failure_threshold=10, recovery_timeout=120)
        assert cb.failure_threshold == 10
        assert cb.recovery_timeout == 120


class TestRetryManager:
    """Test cases for RetryManager"""

    def test_retry_with_backoff_exists(self):
        """Test retry_with_backoff method exists"""
        assert hasattr(RetryManager, 'retry_with_backoff')
