#!/usr/bin/env python3
"""
Unit tests for batch optimizer module
"""

import pytest
from LiteTTS.performance.batch_optimizer import BatchRequest, BatchConfig, BatchMetrics, DynamicBatchOptimizer


class TestBatchRequest:
    """Test cases for BatchRequest"""

    def test_creation(self):
        """Test creating batch request"""
        request = BatchRequest(
            request_id="req1",
            text="Hello world",
            voice="af_heart",
            params={},
            timestamp=1234567890.0,
            text_length=11
        )
        assert request.request_id == "req1"
        assert request.text == "Hello world"
        assert request.text_length == 11


class TestBatchConfig:
    """Test cases for BatchConfig"""

    def test_creation_defaults(self):
        """Test creating batch config with defaults"""
        config = BatchConfig()
        assert config.short_text_threshold == 20
        assert config.medium_text_threshold == 100
        assert config.long_text_threshold == 300
        assert config.enable_auto_tuning is True

    def test_creation_custom(self):
        """Test creating batch config with custom values"""
        config = BatchConfig(
            short_text_batch_size=20,
            medium_text_batch_size=10,
            long_text_batch_size=5,
            enable_auto_tuning=False
        )
        assert config.short_text_batch_size == 20
        assert config.enable_auto_tuning is False


class TestBatchMetrics:
    """Test cases for BatchMetrics"""

    def test_creation_defaults(self):
        """Test creating batch metrics with defaults"""
        metrics = BatchMetrics()
        assert metrics.total_requests == 0
        assert metrics.batch_efficiency == 0.0
        assert metrics.cache_hit_rate == 0.0


class TestDynamicBatchOptimizer:
    """Test cases for DynamicBatchOptimizer"""

    def test_initialization(self):
        """Test optimizer initializes correctly"""
        optimizer = DynamicBatchOptimizer()
        assert optimizer is not None

    def test_initialization_with_config(self):
        """Test optimizer with custom config"""
        config = BatchConfig(short_text_batch_size=20)
        optimizer = DynamicBatchOptimizer(config)
        assert optimizer.config.short_text_batch_size == 20
