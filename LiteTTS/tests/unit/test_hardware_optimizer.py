#!/usr/bin/env python3
"""
Unit tests for hardware optimizer module
"""

import pytest
from unittest.mock import patch, Mock
from LiteTTS.hardware_optimizer import (
    HardwareProfile,
    OptimizedSettings,
    HardwareOptimizer,
    run_hardware_optimization
)


class TestHardwareProfile:
    """Test cases for HardwareProfile dataclass"""

    def test_creation(self):
        """Test creating a hardware profile"""
        profile = HardwareProfile(
            cpu_cores=8,
            cpu_threads=16,
            cpu_frequency=3.5,
            total_memory_gb=32.0,
            available_memory_gb=16.0,
            has_gpu=True,
            gpu_memory_gb=8.0,
            platform_system="Linux",
            architecture="x86_64"
        )
        assert profile.cpu_cores == 8
        assert profile.cpu_threads == 16
        assert profile.cpu_frequency == 3.5
        assert profile.total_memory_gb == 32.0
        assert profile.available_memory_gb == 16.0
        assert profile.has_gpu is True
        assert profile.gpu_memory_gb == 8.0
        assert profile.platform_system == "Linux"
        assert profile.architecture == "x86_64"

    def test_creation_without_gpu(self):
        """Test creating a hardware profile without GPU"""
        profile = HardwareProfile(
            cpu_cores=4,
            cpu_threads=8,
            cpu_frequency=2.5,
            total_memory_gb=16.0,
            available_memory_gb=8.0,
            has_gpu=False,
            gpu_memory_gb=None,
            platform_system="Linux",
            architecture="x86_64"
        )
        assert profile.has_gpu is False
        assert profile.gpu_memory_gb is None


class TestOptimizedSettings:
    """Test cases for OptimizedSettings dataclass"""

    def test_creation(self):
        """Test creating optimized settings"""
        settings = OptimizedSettings(
            workers=4,
            chunk_size=200,
            cache_enabled=True,
            cache_size=100,
            preload_models=True,
            max_text_length=8000,
            timeout_seconds=30,
            device="cuda"
        )
        assert settings.workers == 4
        assert settings.chunk_size == 200
        assert settings.cache_enabled is True
        assert settings.cache_size == 100
        assert settings.preload_models is True
        assert settings.max_text_length == 8000
        assert settings.timeout_seconds == 30
        assert settings.device == "cuda"

    def test_creation_cpu_only(self):
        """Test creating optimized settings for CPU only"""
        settings = OptimizedSettings(
            workers=2,
            chunk_size=100,
            cache_enabled=True,
            cache_size=50,
            preload_models=False,
            max_text_length=3000,
            timeout_seconds=60,
            device="cpu"
        )
        assert settings.device == "cpu"
        assert settings.workers == 2


class TestHardwareOptimizer:
    """Test cases for HardwareOptimizer class"""

    def test_initialization(self):
        """Test optimizer initializes correctly"""
        optimizer = HardwareOptimizer()
        assert optimizer.hardware_profile is None
        assert optimizer.optimized_settings is None
        assert optimizer.benchmark_results == {}

    def test_detect_hardware(self):
        """Test hardware detection"""
        optimizer = HardwareOptimizer()
        profile = optimizer.detect_hardware()

        assert isinstance(profile, HardwareProfile)
        assert profile.cpu_cores is not None
        assert profile.cpu_threads is not None
        assert profile.cpu_frequency is not None
        assert profile.total_memory_gb is not None
        assert profile.available_memory_gb is not None
        assert profile.platform_system is not None
        assert profile.architecture is not None

        # Verify stored in instance
        assert optimizer.hardware_profile is profile

    def test_run_benchmarks(self):
        """Test running benchmarks"""
        optimizer = HardwareOptimizer()
        optimizer.detect_hardware()  # Must detect hardware first

        benchmarks = optimizer.run_benchmarks()

        assert isinstance(benchmarks, dict)
        assert 'cpu_performance' in benchmarks
        assert 'memory_performance' in benchmarks
        assert 'io_performance' in benchmarks
        assert optimizer.benchmark_results == benchmarks

    def test_run_benchmarks_raises_without_hardware(self):
        """Test benchmarks raise error without hardware detection"""
        optimizer = HardwareOptimizer()
        with pytest.raises(ValueError, match="Hardware profile not detected"):
            optimizer.run_benchmarks()

    def test_calculate_optimal_settings(self):
        """Test calculating optimal settings"""
        optimizer = HardwareOptimizer()
        optimizer.detect_hardware()
        optimizer.run_benchmarks()

        settings = optimizer.calculate_optimal_settings()

        assert isinstance(settings, OptimizedSettings)
        assert settings.workers >= 1
        assert settings.chunk_size >= 50
        assert settings.max_text_length >= 1000
        assert settings.timeout_seconds >= 10
        assert settings.device in ["cuda", "cpu"]
        assert optimizer.optimized_settings is settings

    def test_calculate_optimal_settings_raises_without_benchmarks(self):
        """Test calculate optimal settings raises error without benchmarks"""
        optimizer = HardwareOptimizer()
        optimizer.detect_hardware()

        with pytest.raises(ValueError, match="Hardware profile and benchmarks required"):
            optimizer.calculate_optimal_settings()

    def test_generate_override_config(self):
        """Test generating override configuration"""
        optimizer = HardwareOptimizer()
        optimizer.detect_hardware()
        optimizer.run_benchmarks()
        optimizer.calculate_optimal_settings()

        config = optimizer.generate_override_config()

        assert isinstance(config, dict)
        assert "_generated_by" in config
        assert config["_generated_by"] == "Kokoro Hardware Optimizer"
        assert "_hardware_profile" in config
        assert "server" in config
        assert "performance" in config
        assert "cache" in config

    def test_generate_override_config_raises_without_settings(self):
        """Test generate override config raises error without settings"""
        optimizer = HardwareOptimizer()

        with pytest.raises(ValueError, match="Optimal settings not calculated"):
            optimizer.generate_override_config()

    @patch("LiteTTS.hardware_optimizer.Path")
    @patch("builtins.open", create=True)
    def test_save_override_config(self, mock_open, mock_path):
        """Test saving override configuration"""
        optimizer = HardwareOptimizer()
        optimizer.optimized_settings = OptimizedSettings(
            workers=4, chunk_size=200, cache_enabled=True, cache_size=100,
            preload_models=True, max_text_length=8000, timeout_seconds=30, device="cpu"
        )

        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        config = {"test": "config"}
        result = optimizer.save_override_config(config, backup_existing=False)

        assert result is True

    @patch("LiteTTS.hardware_optimizer.Path")
    def test_save_override_config_failure(self, mock_path):
        """Test save override config handles failures"""
        optimizer = HardwareOptimizer()
        optimizer.optimized_settings = OptimizedSettings(
            workers=4, chunk_size=200, cache_enabled=True, cache_size=100,
            preload_models=True, max_text_length=8000, timeout_seconds=30, device="cpu"
        )

        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        with patch("builtins.open", side_effect=Exception("Write error")):
            result = optimizer.save_override_config({})
            assert result is False

    def test_optimize_system(self):
        """Test complete system optimization"""
        optimizer = HardwareOptimizer()
        # Set up real objects for generate_override_config to work
        optimizer.hardware_profile = HardwareProfile(
            cpu_cores=8, cpu_threads=16, cpu_frequency=3.5,
            total_memory_gb=32.0, available_memory_gb=16.0,
            has_gpu=False, gpu_memory_gb=None,
            platform_system="Linux", architecture="x86_64"
        )
        optimizer.benchmark_results = {'cpu_performance': 1.5}
        optimizer.optimized_settings = OptimizedSettings(
            workers=4, chunk_size=200, cache_enabled=True, cache_size=100,
            preload_models=True, max_text_length=8000, timeout_seconds=30, device="cpu"
        )

        with patch.object(optimizer, 'detect_hardware') as mock_detect, \
             patch.object(optimizer, 'run_benchmarks') as mock_bench, \
             patch.object(optimizer, 'calculate_optimal_settings') as mock_calc, \
             patch.object(optimizer, 'save_override_config') as mock_save:

            mock_detect.return_value = Mock()
            mock_bench.return_value = {}
            mock_calc.return_value = Mock()
            mock_save.return_value = True

            with patch("LiteTTS.hardware_optimizer.Path") as mock_path:
                mock_path_instance = Mock()
                mock_path_instance.exists.return_value = False
                mock_path.return_value = mock_path_instance

                result = optimizer.optimize_system()

                assert result is True
                mock_detect.assert_called_once()
                mock_bench.assert_called_once()
                mock_calc.assert_called_once()
                mock_save.assert_called_once()


class TestRunHardwareOptimization:
    """Test cases for run_hardware_optimization function"""

    def test_run_hardware_optimization_function(self):
        """Test the convenience function"""
        with patch("LiteTTS.hardware_optimizer.HardwareOptimizer") as mock_class:
            mock_instance = Mock()
            mock_instance.optimize_system.return_value = True
            mock_class.return_value = mock_instance

            result = run_hardware_optimization()

            assert result is True
            mock_instance.optimize_system.assert_called_once_with(force=False)

    def test_run_hardware_optimization_with_force(self):
        """Test the convenience function with force=True"""
        with patch("LiteTTS.hardware_optimizer.HardwareOptimizer") as mock_class:
            mock_instance = Mock()
            mock_instance.optimize_system.return_value = True
            mock_class.return_value = mock_instance

            result = run_hardware_optimization(force=True)

            assert result is True
            mock_instance.optimize_system.assert_called_once_with(force=True)
