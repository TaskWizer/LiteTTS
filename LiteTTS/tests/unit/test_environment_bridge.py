#!/usr/bin/env python3
"""
Unit tests for environment bridge module
"""

import pytest
from unittest.mock import patch
from LiteTTS.config.environment_bridge import (
    EnvironmentConfig,
    EnvironmentConfigLoader,
    get_environment_config,
    initialize_environment_config
)


class TestEnvironmentConfig:
    """Test cases for EnvironmentConfig dataclass"""

    def test_creation_defaults(self):
        """Test creating config with defaults"""
        config = EnvironmentConfig()
        assert config.enable_performance_optimization is True
        assert config.max_memory_mb == 4096
        assert config.target_rtf == 0.25
        assert config.dynamic_cpu_allocation_enabled is True
        assert config.cpu_target == 75.0
        assert config.aggressive_mode is True
        assert config.thermal_protection is True

    def test_creation_custom(self):
        """Test creating config with custom values"""
        config = EnvironmentConfig(
            enable_performance_optimization=False,
            max_memory_mb=8192,
            target_rtf=0.5,
            cpu_target=50.0,
            aggressive_mode=False
        )
        assert config.enable_performance_optimization is False
        assert config.max_memory_mb == 8192
        assert config.target_rtf == 0.5
        assert config.cpu_target == 50.0
        assert config.aggressive_mode is False


class TestEnvironmentConfigLoader:
    """Test cases for EnvironmentConfigLoader class"""

    def test_initialization(self):
        """Test loader initializes with defaults"""
        loader = EnvironmentConfigLoader()
        assert loader.config is not None
        assert isinstance(loader.config, EnvironmentConfig)

    def test_get_bool_env_true(self):
        """Test getting true boolean environment variable"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {'TEST_VAR': 'true'}):
            result = loader._get_bool_env('TEST_VAR', False)
            assert result is True

    def test_get_bool_env_false(self):
        """Test getting false boolean environment variable"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {'TEST_VAR': 'false'}):
            result = loader._get_bool_env('TEST_VAR', True)
            assert result is False

    def test_get_bool_env_default(self):
        """Test getting boolean with default"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {}, clear=True):
            result = loader._get_bool_env('NONEXISTENT_VAR', True)
            assert result is True

    def test_get_int_env_valid(self):
        """Test getting valid integer environment variable"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {'TEST_INT': '2048'}):
            result = loader._get_int_env('TEST_INT', 1024)
            assert result == 2048

    def test_get_int_env_invalid(self):
        """Test getting invalid integer environment variable"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {'TEST_INT': 'not_a_number'}):
            result = loader._get_int_env('TEST_INT', 1024)
            assert result == 1024

    def test_get_int_env_none(self):
        """Test getting non-existent integer environment variable"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {}, clear=True):
            result = loader._get_int_env('NONEXISTENT_INT', 512)
            assert result == 512

    def test_get_int_env_with_none_default(self):
        """Test getting integer with None default (threading vars)"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {}, clear=True):
            result = loader._get_int_env('NONEXISTENT_THREADS')
            assert result is None

    def test_get_float_env_valid(self):
        """Test getting valid float environment variable"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {'TEST_FLOAT': '0.75'}):
            result = loader._get_float_env('TEST_FLOAT', 0.5)
            assert result == 0.75

    def test_get_float_env_invalid(self):
        """Test getting invalid float environment variable"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {'TEST_FLOAT': 'not_a_float'}):
            result = loader._get_float_env('TEST_FLOAT', 0.5)
            assert result == 0.5

    def test_get_dynamic_cpu_allocation_config(self):
        """Test getting dynamic CPU allocation config"""
        loader = EnvironmentConfigLoader()
        config = loader.get_dynamic_cpu_allocation_config()
        assert isinstance(config, dict)
        assert 'enabled' in config
        assert 'cpu_target' in config
        assert 'aggressive_mode' in config
        assert 'thermal_protection' in config
        assert 'onnx_integration' in config
        assert 'update_environment' in config

    def test_get_performance_config(self):
        """Test getting performance config"""
        loader = EnvironmentConfigLoader()
        config = loader.get_performance_config()
        assert isinstance(config, dict)
        assert 'memory_optimization' in config
        assert 'max_memory_mb' in config
        assert 'target_rtf' in config
        assert 'dynamic_cpu_allocation' in config

    def test_apply_onnx_environment_variables(self):
        """Test applying ONNX environment variables"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {}, clear=True):
            loader.apply_onnx_environment_variables()
            # Check that variables were set
            import os
            assert 'ORT_DISABLE_ALL_OPTIMIZATION' in os.environ
            assert 'ORT_ENABLE_CPU_FP16_OPS' in os.environ

    def test_apply_memory_allocation_variables(self):
        """Test applying memory allocation variables"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {}, clear=True):
            loader.apply_memory_allocation_variables()
            import os
            assert 'MALLOC_ARENA_MAX' in os.environ
            assert 'MALLOC_MMAP_THRESHOLD_' in os.environ

    def test_apply_threading_variables(self):
        """Test applying threading variables"""
        loader = EnvironmentConfigLoader()
        loader.config.omp_num_threads = 4
        with patch.dict('os.environ', {}, clear=True):
            loader.apply_threading_variables()
            import os
            assert os.environ.get('OMP_NUM_THREADS') == '4'

    def test_apply_all_environment_variables(self):
        """Test applying all environment variables"""
        loader = EnvironmentConfigLoader()
        with patch.dict('os.environ', {}, clear=True):
            loader.apply_all_environment_variables()
            import os
            assert 'ORT_DISABLE_ALL_OPTIMIZATION' in os.environ


class TestGlobalFunctions:
    """Test cases for global functions"""

    def test_get_environment_config(self):
        """Test getting environment config returns a valid object"""
        config = get_environment_config()
        assert config is not None
        assert isinstance(config, EnvironmentConfigLoader)

    def test_initialize_environment_config(self):
        """Test initializing environment config returns a valid object"""
        result = initialize_environment_config()
        assert result is not None
        assert isinstance(result, EnvironmentConfigLoader)
