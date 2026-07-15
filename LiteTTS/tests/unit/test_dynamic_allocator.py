#!/usr/bin/env python3
"""
Unit tests for dynamic allocator module
"""

import pytest
from unittest.mock import Mock, patch


class TestDynamicAllocationConfig:
    """Test cases for DynamicAllocationConfig"""

    def test_creation_defaults(self):
        """Test creating config with defaults"""
        from LiteTTS.performance.dynamic_allocator import DynamicAllocationConfig
        config = DynamicAllocationConfig()
        assert config.enabled is True
        assert config.min_cores == 1
        assert config.aggressive_mode is False
        assert config.thermal_protection is True

    def test_creation_custom(self):
        """Test creating config with custom values"""
        from LiteTTS.performance.dynamic_allocator import DynamicAllocationConfig
        config = DynamicAllocationConfig(
            enabled=False,
            min_cores=2,
            max_cores=8,
            aggressive_mode=True
        )
        assert config.enabled is False
        assert config.min_cores == 2
        assert config.max_cores == 8
        assert config.aggressive_mode is True


class TestDynamicCPUAllocator:
    """Test cases for DynamicCPUAllocator"""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock dependencies"""
        with patch('LiteTTS.performance.dynamic_allocator.get_cpu_optimizer', return_value=Mock()):
            yield

    def test_initialization(self, mock_dependencies):
        """Test allocator initializes correctly"""
        from LiteTTS.performance.dynamic_allocator import DynamicCPUAllocator
        allocator = DynamicCPUAllocator()
        assert allocator is not None
        assert allocator.config.min_cores == 1

    def test_initialization_custom_config(self, mock_dependencies):
        """Test allocator with custom config"""
        from LiteTTS.performance.dynamic_allocator import DynamicCPUAllocator, DynamicAllocationConfig
        config = DynamicAllocationConfig(min_cores=2, max_cores=6)
        allocator = DynamicCPUAllocator(config)
        assert allocator.config.min_cores == 2
        assert allocator.config.max_cores == 6
