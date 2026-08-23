#!/usr/bin/env python3
"""
Unit tests for hardware detector module
"""

import platform
import pytest

from LiteTTS.optimization.hardware_detector import HardwareDetector


class TestHardwareDetector:
    """Test cases for HardwareDetector"""

    def test_initialization(self):
        """Test detector initializes correctly"""
        detector = HardwareDetector()
        assert detector is not None
        assert detector.system_info is not None
        assert detector.cpu_info is not None
        assert detector.memory_info is not None
        assert detector.gpu_info is not None
        assert detector.storage_info is not None
        assert detector.system_fingerprint is not None

    def test_system_info_contains_platform(self):
        """Test system info contains platform information"""
        detector = HardwareDetector()
        assert "platform" in detector.system_info
        assert detector.system_info["platform"] == platform.system()
        assert "python_version" in detector.system_info

    def test_cpu_info_contains_cores(self):
        """Test CPU info contains core count"""
        detector = HardwareDetector()
        assert "physical_cores" in detector.cpu_info
        assert "logical_cores" in detector.cpu_info
        assert detector.cpu_info["physical_cores"] is not None
        assert detector.cpu_info["logical_cores"] is not None

    def test_memory_info_contains_ram(self):
        """Test memory info contains RAM information"""
        detector = HardwareDetector()
        assert "total_ram_gb" in detector.memory_info
        assert "available_ram_gb" in detector.memory_info
        assert "ram_usage_percent" in detector.memory_info
        assert detector.memory_info["total_ram_gb"] > 0

    def test_gpu_info_structure(self):
        """Test GPU info has correct structure"""
        detector = HardwareDetector()
        assert "cuda_available" in detector.gpu_info
        assert "gpu_count" in detector.gpu_info
        assert "gpu_names" in detector.gpu_info
        assert isinstance(detector.gpu_info["cuda_available"], bool)
        assert isinstance(detector.gpu_info["gpu_count"], int)

    def test_storage_info_structure(self):
        """Test storage info has correct structure"""
        detector = HardwareDetector()
        assert "total_storage_gb" in detector.storage_info
        assert "free_storage_gb" in detector.storage_info
        assert "storage_type" in detector.storage_info
        assert detector.storage_info["storage_type"] in ["SSD", "HDD", "unknown"]

    def test_system_fingerprint_format(self):
        """Test system fingerprint is proper format"""
        detector = HardwareDetector()
        fingerprint = detector.system_fingerprint
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 16  # SHA256 truncated to 16 chars

    def test_get_system_capabilities(self):
        """Test get_system_capabilities returns scores"""
        detector = HardwareDetector()
        caps = detector.get_system_capabilities()

        assert "cpu_score" in caps
        assert "memory_score" in caps
        assert "gpu_score" in caps
        assert "storage_score" in caps
        assert "overall_score" in caps

        # Scores should be 0-100
        for key in ["cpu_score", "memory_score", "gpu_score", "storage_score", "overall_score"]:
            assert 0 <= caps[key] <= 100

    def test_cpu_score_calculation(self):
        """Test CPU score calculation"""
        detector = HardwareDetector()
        score = detector._calculate_cpu_score()
        assert 0 <= score <= 100

    def test_memory_score_calculation(self):
        """Test memory score calculation"""
        detector = HardwareDetector()
        score = detector._calculate_memory_score()
        assert 0 <= score <= 100

    def test_gpu_score_calculation(self):
        """Test GPU score calculation"""
        detector = HardwareDetector()
        score = detector._calculate_gpu_score()
        assert 0 <= score <= 100

    def test_storage_score_calculation(self):
        """Test storage score calculation"""
        detector = HardwareDetector()
        score = detector._calculate_storage_score()
        assert 0 <= score <= 100

    def test_overall_score_calculation(self):
        """Test overall score calculation"""
        detector = HardwareDetector()
        score = detector._calculate_overall_score()
        assert 0 <= score <= 100

    def test_get_all_info(self):
        """Test get_all_info returns all information"""
        detector = HardwareDetector()
        info = detector.get_all_info()

        assert "system_info" in info
        assert "cpu_info" in info
        assert "memory_info" in info
        assert "gpu_info" in info
        assert "storage_info" in info
        assert "system_fingerprint" in info
        assert "capabilities" in info
