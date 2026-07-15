#!/usr/bin/env python3
"""
Unit tests for memory profiler
"""

import pytest
from LiteTTS.performance.memory_profiler import MemorySnapshot, MemoryLeak


class TestMemorySnapshot:
    """Test cases for MemorySnapshot"""

    def test_creation(self):
        """Test creating memory snapshot"""
        snapshot = MemorySnapshot(
            timestamp=1234567890.0,
            rss_mb=1024.0,
            vms_mb=2048.0,
            percent=50.0,
            available_mb=8192.0
        )
        assert snapshot.rss_mb == 1024.0
        assert snapshot.percent == 50.0

    def test_creation_with_metadata(self):
        """Test creating memory snapshot with metadata"""
        snapshot = MemorySnapshot(
            timestamp=1234567890.0,
            rss_mb=1024.0,
            vms_mb=2048.0,
            percent=50.0,
            available_mb=8192.0,
            gc_objects=100,
            metadata={"test": "value"}
        )
        assert snapshot.gc_objects == 100
        assert snapshot.metadata["test"] == "value"


class TestMemoryLeak:
    """Test cases for MemoryLeak"""

    def test_creation(self):
        """Test creating memory leak detection result"""
        leak = MemoryLeak(
            component="test_component",
            leak_rate_mb_per_sec=0.5,
            total_leaked_mb=100.0,
            confidence=0.8
        )
        assert leak.component == "test_component"
        assert leak.confidence == 0.8

    def test_creation_with_evidence(self):
        """Test creating memory leak with evidence"""
        leak = MemoryLeak(
            component="test_component",
            leak_rate_mb_per_sec=0.5,
            total_leaked_mb=100.0,
            confidence=0.8,
            evidence=["Evidence 1", "Evidence 2"],
            recommendations=["Fix 1", "Fix 2"]
        )
        assert len(leak.evidence) == 2
        assert len(leak.recommendations) == 2
