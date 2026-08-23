#!/usr/bin/env python3
"""
Unit tests for system optimizer module
"""

from LiteTTS.performance.system_optimizer import BatchRequest, RequestBatcher, SIMDCapabilities


class TestSIMDCapabilities:
    """Test cases for SIMDCapabilities"""

    def test_creation_defaults(self):
        """Test creating SIMD capabilities with defaults"""
        caps = SIMDCapabilities()
        assert caps.has_sse is False
        assert caps.has_avx is False

    def test_creation_custom(self):
        """Test creating SIMD capabilities with custom values"""
        caps = SIMDCapabilities(
            has_sse=True,
            has_sse2=True,
            has_avx=True,
            has_avx2=True
        )
        assert caps.has_sse is True
        assert caps.has_avx2 is True


class TestBatchRequest:
    """Test cases for BatchRequest"""

    def test_creation(self):
        """Test creating batch request"""
        request = BatchRequest(
            id="req1",
            text="Hello world",
            voice="af_heart",
            speed=1.0,
            format="mp3"
        )
        assert request.id == "req1"
        assert request.text == "Hello world"
        assert request.priority == 0

    def test_creation_with_priority(self):
        """Test creating batch request with priority"""
        request = BatchRequest(
            id="req2",
            text="Test",
            voice="am_puck",
            speed=1.0,
            format="wav",
            priority=5
        )
        assert request.priority == 5


class TestRequestBatcher:
    """Test cases for RequestBatcher"""

    def test_initialization(self):
        """Test batcher initializes correctly"""
        batcher = RequestBatcher(max_batch_size=6, batch_timeout_ms=25)
        assert batcher.max_batch_size == 6
        assert batcher.batch_timeout_ms == 25
        assert batcher.running is False

    def test_initialization_defaults(self):
        """Test batcher with default values"""
        batcher = RequestBatcher()
        assert batcher.max_batch_size == 6
        assert batcher.batch_timeout_ms == 25
        assert batcher.max_workers == 18
