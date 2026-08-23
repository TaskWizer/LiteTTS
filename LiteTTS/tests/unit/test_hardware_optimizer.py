#!/usr/bin/env python3
"""
Unit tests for hardware optimizer module
"""

from unittest.mock import Mock, patch

import pytest

from LiteTTS.hardware_optimizer import (
    HardwareOptimizer,
    HardwareProfile,
    OptimizedSettings,
    run_hardware_optimization,
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


class TestHardwareOptimizerEdgeCases:
    """Test edge cases for HardwareOptimizer"""

    def test_detect_hardware_torch_import_error(self):
        """Test GPU detection when torch import fails (line 78-79)"""
        optimizer = HardwareOptimizer()

        with patch.dict('sys.modules', {'torch': None}):
            with patch('LiteTTS.hardware_optimizer.psutil') as mock_psutil:
                # Set up basic mock returns
                mock_psutil.cpu_count.side_effect = [4, 8]
                mock_freq = Mock()
                mock_freq.current = 2.5
                mock_psutil.cpu_freq.return_value = mock_freq
                mock_mem = Mock()
                mock_mem.total = 16 * (1024**3)
                mock_mem.available = 8 * (1024**3)
                mock_psutil.virtual_memory.return_value = mock_mem

                profile = optimizer.detect_hardware()
                assert profile.has_gpu is False
                assert profile.gpu_memory_gb is None

    def test_detect_hardware_gpu_detection_exception(self):
        """Test GPU detection when torch raises exception (lines 80-81)"""
        optimizer = HardwareOptimizer()

        with patch('LiteTTS.hardware_optimizer.psutil') as mock_psutil:
            mock_psutil.cpu_count.side_effect = [4, 8]
            mock_freq = Mock()
            mock_freq.current = 2.5
            mock_psutil.cpu_freq.return_value = mock_freq
            mock_mem = Mock()
            mock_mem.total = 16 * (1024**3)
            mock_mem.available = 8 * (1024**3)
            mock_psutil.virtual_memory.return_value = mock_mem

            import torch
            with patch.dict('sys.modules', {'torch': torch}):
                with patch.object(torch.cuda, 'is_available', side_effect=Exception("CUDA error")):
                    profile = optimizer.detect_hardware()
                    # Should handle exception gracefully
                    assert profile.has_gpu is False

    def test_run_benchmarks_io_exception(self):
        """Test I/O benchmark exception handling (lines 145-146)"""
        optimizer = HardwareOptimizer()
        optimizer.hardware_profile = HardwareProfile(
            cpu_cores=4, cpu_threads=8, cpu_frequency=2.5,
            total_memory_gb=16.0, available_memory_gb=8.0,
            has_gpu=False, gpu_memory_gb=None,
            platform_system="Linux", architecture="x86_64"
        )

        with patch('LiteTTS.hardware_optimizer.open', side_effect=OSError("Disk error")):
            benchmarks = optimizer.run_benchmarks()
            # Should still return benchmarks with partial results
            assert 'cpu_performance' in benchmarks
            assert 'memory_performance' in benchmarks
            assert 'io_performance' in benchmarks

    def test_calculate_optimal_settings_low_end_hardware(self):
        """Test optimal settings calculation for low-end hardware (lines 171-174, 179-184, 190-193, 201-204, 210-213)"""
        optimizer = HardwareOptimizer()
        optimizer.hardware_profile = HardwareProfile(
            cpu_cores=2, cpu_threads=4, cpu_frequency=1.5,
            total_memory_gb=3.5, available_memory_gb=2.0,
            has_gpu=False, gpu_memory_gb=None,
            platform_system="Linux", architecture="x86_64"
        )
        optimizer.benchmark_results = {
            'cpu_performance': 0.5,  # Slow CPU
            'memory_performance': 1.0,
            'io_performance': 1.0
        }

        settings = optimizer.calculate_optimal_settings()

        # Low-end: 2 cores < 4 -> workers=1 (line 174)
        assert settings.workers == 1
        # <4GB memory -> chunk_size=50 (line 184)
        assert settings.chunk_size == 50
        # <4GB available -> cache_size=50 (line 193)
        assert settings.cache_size == 50
        # <8GB total -> max_text_length=3000 (line 204)
        assert settings.max_text_length == 3000
        # slow CPU -> timeout_seconds=60 (line 213)
        assert settings.timeout_seconds == 60

    def test_calculate_optimal_settings_high_end_hardware(self):
        """Test optimal settings for high-end hardware"""
        optimizer = HardwareOptimizer()
        optimizer.hardware_profile = HardwareProfile(
            cpu_cores=16, cpu_threads=32, cpu_frequency=4.0,
            total_memory_gb=64.0, available_memory_gb=32.0,
            has_gpu=True, gpu_memory_gb=8.0,
            platform_system="Linux", architecture="x86_64"
        )
        optimizer.benchmark_results = {
            'cpu_performance': 3.0,  # Fast CPU
            'memory_performance': 2.0,
            'io_performance': 2.0
        }

        settings = optimizer.calculate_optimal_settings()

        # 16 cores >= 8 -> workers = min(4, 16//2) = 4 (line 170)
        assert settings.workers == 4
        # >=16GB && >=8 cores -> chunk_size=200 (line 178)
        assert settings.chunk_size == 200
        # >=8GB available -> cache_size=200 (line 189)
        assert settings.cache_size == 200
        # >=16GB total -> max_text_length=8000 (line 200)
        assert settings.max_text_length == 8000
        # fast CPU -> timeout_seconds=30 (line 209)
        assert settings.timeout_seconds == 30
        # has_gpu && >=2GB -> device="cuda" (line 216)
        assert settings.device == "cuda"

    def test_generate_override_config_with_cuda(self):
        """Test generate_override_config adds cuda device when available (line 276)"""
        optimizer = HardwareOptimizer()
        optimizer.hardware_profile = HardwareProfile(
            cpu_cores=8, cpu_threads=16, cpu_frequency=3.5,
            total_memory_gb=32.0, available_memory_gb=16.0,
            has_gpu=True, gpu_memory_gb=8.0,
            platform_system="Linux", architecture="x86_64"
        )
        optimizer.benchmark_results = {'cpu_performance': 1.5}
        optimizer.optimized_settings = OptimizedSettings(
            workers=4, chunk_size=200, cache_enabled=True, cache_size=100,
            preload_models=True, max_text_length=8000, timeout_seconds=30, device="cuda"
        )

        config = optimizer.generate_override_config()

        # Line 276: should add tts device when cuda
        assert "tts" in config
        assert config["tts"]["device"] == "cuda"

    def test_save_override_config_with_backup(self):
        """Test save_override_config backs up existing file (lines 286-288)"""
        optimizer = HardwareOptimizer()
        optimizer.optimized_settings = OptimizedSettings(
            workers=4, chunk_size=200, cache_enabled=True, cache_size=100,
            preload_models=True, max_text_length=8000, timeout_seconds=30, device="cpu"
        )

        with patch('LiteTTS.hardware_optimizer.Path') as mock_path:
            mock_existing = Mock()
            mock_existing.exists.return_value = True
            mock_backup = Mock()
            mock_path.return_value = mock_existing
            mock_path.side_effect = lambda x: mock_backup if 'backup' in str(x) else mock_existing

            with patch('builtins.open', create=True):
                result = optimizer.save_override_config({}, backup_existing=True)
                # Line 286-288: should rename existing to backup
                assert mock_existing.rename.called

    def test_optimize_system_already_completed(self):
        """Test optimize_system returns True when already done (lines 305-313)"""
        optimizer = HardwareOptimizer()

        existing_config = {
            "_generated_by": "Kokoro Hardware Optimizer",
            "server": {"workers": 4}
        }

        with patch('LiteTTS.hardware_optimizer.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path_instance.exists.return_value = True
            mock_path.return_value = mock_path_instance

            with patch('builtins.open', create=True) as mock_open:
                mock_file = Mock()
                mock_file.__enter__ = Mock(return_value=mock_file)
                mock_file.__exit__ = Mock(return_value=None)
                mock_file.read.return_value = '{"_generated_by": "Kokoro Hardware Optimizer"}'
                mock_open.return_value = mock_file

                result = optimizer.optimize_system()
                assert result is True

    def test_optimize_system_failure(self):
        """Test optimize_system handles failures (lines 336-341)"""
        optimizer = HardwareOptimizer()

        with patch.object(optimizer, 'detect_hardware', side_effect=Exception("Detection failed")):
            result = optimizer.optimize_system()
            assert result is False

    def test_optimize_system_save_fails(self):
        """Test optimize_system when save fails"""
        optimizer = HardwareOptimizer()
        optimizer.hardware_profile = HardwareProfile(
            cpu_cores=4, cpu_threads=8, cpu_frequency=2.5,
            total_memory_gb=16.0, available_memory_gb=8.0,
            has_gpu=False, gpu_memory_gb=None,
            platform_system="Linux", architecture="x86_64"
        )
        optimizer.benchmark_results = {'cpu_performance': 1.5}
        optimizer.optimized_settings = OptimizedSettings(
            workers=4, chunk_size=200, cache_enabled=True, cache_size=100,
            preload_models=True, max_text_length=8000, timeout_seconds=30, device="cpu"
        )

        with patch.object(optimizer, 'save_override_config', return_value=False):
            with patch('LiteTTS.hardware_optimizer.Path') as mock_path:
                mock_path_instance = Mock()
                mock_path_instance.exists.return_value = False
                mock_path.return_value = mock_path_instance

                result = optimizer.optimize_system()
                assert result is False

    def test_calculate_optimal_settings_mid_range_hardware(self):
        """Test optimal settings for mid-range hardware (hits lines 172, 180, 191, 202, 211)"""
        optimizer = HardwareOptimizer()
        # 4 cores triggers line 172 (workers=2)
        # 12GB memory triggers line 180 (chunk_size=150 for 8<=memory<16 AND cores>=4)
        # 6GB available triggers line 191 (cache_size=100 for 4<=available<8)
        # 12GB total triggers line 202 (max_text_length=5000 for 8<=total<16)
        # cpu_perf 1.5 triggers line 211 (timeout_seconds=45 for 1.0<perf<=2.0)
        optimizer.hardware_profile = HardwareProfile(
            cpu_cores=4, cpu_threads=8, cpu_frequency=2.5,
            total_memory_gb=12.0, available_memory_gb=6.0,
            has_gpu=False, gpu_memory_gb=None,
            platform_system="Linux", architecture="x86_64"
        )
        optimizer.benchmark_results = {
            'cpu_performance': 1.5,  # Medium CPU -> line 211
            'memory_performance': 1.5,
            'io_performance': 1.5
        }

        settings = optimizer.calculate_optimal_settings()

        # 4 cores (>=4 but <8) -> workers=2 (line 172)
        assert settings.workers == 2
        # 12GB (>=8 but <16) AND 4 cores (>=4) -> chunk_size=150 (line 180)
        assert settings.chunk_size == 150
        # 6GB available (>=4 but <8) -> cache_size=100 (line 191)
        assert settings.cache_size == 100
        # 12GB total (>=8 but <16) -> max_text_length=5000 (line 202)
        assert settings.max_text_length == 5000
        # 1.0 < 1.5 <= 2.0 -> timeout_seconds=45 (line 211)
        assert settings.timeout_seconds == 45

    def test_calculate_optimal_settings_8_cores(self):
        """Test workers calculation for 8 cores (line 170)"""
        optimizer = HardwareOptimizer()
        optimizer.hardware_profile = HardwareProfile(
            cpu_cores=8, cpu_threads=16, cpu_frequency=3.0,
            total_memory_gb=32.0, available_memory_gb=16.0,
            has_gpu=False, gpu_memory_gb=None,
            platform_system="Linux", architecture="x86_64"
        )
        optimizer.benchmark_results = {
            'cpu_performance': 2.5,
            'memory_performance': 2.0,
            'io_performance': 2.0
        }

        settings = optimizer.calculate_optimal_settings()

        # 8 cores >= 8 -> workers = min(4, 8//2) = 4 (line 170)
        assert settings.workers == 4

    def test_calculate_optimal_settings_4_to_8_gb_memory(self):
        """Test chunk_size for 4-8GB memory range (line 182)"""
        optimizer = HardwareOptimizer()
        optimizer.hardware_profile = HardwareProfile(
            cpu_cores=2, cpu_threads=4, cpu_frequency=2.0,
            total_memory_gb=6.0, available_memory_gb=3.0,
            has_gpu=False, gpu_memory_gb=None,
            platform_system="Linux", architecture="x86_64"
        )
        optimizer.benchmark_results = {
            'cpu_performance': 1.0,
            'memory_performance': 1.0,
            'io_performance': 1.0
        }

        settings = optimizer.calculate_optimal_settings()

        # 6GB memory (>=4 but <8) and cores < 4 -> chunk_size=100 (line 182)
        assert settings.chunk_size == 100

    def test_detect_hardware_with_cuda_gpu(self):
        """Test GPU detection when CUDA is available (lines 75-77)"""
        optimizer = HardwareOptimizer()

        with patch('LiteTTS.hardware_optimizer.psutil') as mock_psutil:
            mock_psutil.cpu_count.side_effect = [8, 16]
            mock_freq = Mock()
            mock_freq.current = 3.5
            mock_psutil.cpu_freq.return_value = mock_freq
            mock_mem = Mock()
            mock_mem.total = 32 * (1024**3)
            mock_mem.available = 16 * (1024**3)
            mock_psutil.virtual_memory.return_value = mock_mem

            mock_torch = Mock()
            mock_device = Mock()
            mock_device.total_memory = 8 * (1024**3)
            mock_torch.cuda.get_device_properties.return_value = mock_device
            mock_torch.cuda.is_available.return_value = True
            mock_torch.cuda.get_device_name.return_value = "NVIDIA RTX 3080"

            with patch.dict('sys.modules', {'torch': mock_torch}):
                with patch.object(mock_torch.cuda, 'get_device_properties', return_value=mock_device):
                    profile = optimizer.detect_hardware()

                    assert profile.has_gpu is True
                    assert profile.gpu_memory_gb is not None

    def test_optimize_system_backup_exception(self):
        """Test optimize_system handles exception during backup read (lines 312-313)"""
        optimizer = HardwareOptimizer()
        # Set up required state for generate_override_config
        optimizer.hardware_profile = HardwareProfile(
            cpu_cores=4, cpu_threads=8, cpu_frequency=2.5,
            total_memory_gb=16.0, available_memory_gb=8.0,
            has_gpu=False, gpu_memory_gb=None,
            platform_system="Linux", architecture="x86_64"
        )
        optimizer.benchmark_results = {'cpu_performance': 1.5}
        optimizer.optimized_settings = OptimizedSettings(
            workers=4, chunk_size=200, cache_enabled=True, cache_size=100,
            preload_models=True, max_text_length=8000, timeout_seconds=30, device="cpu"
        )

        with patch('LiteTTS.hardware_optimizer.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path_instance.exists.return_value = True
            mock_path.return_value = mock_path_instance

            with patch('builtins.open', side_effect=Exception("Cannot read backup")):
                # Should continue with optimization when existing config cannot be read
                with patch.object(optimizer, 'detect_hardware') as mock_detect, \
                     patch.object(optimizer, 'run_benchmarks') as mock_bench, \
                     patch.object(optimizer, 'calculate_optimal_settings') as mock_calc, \
                     patch.object(optimizer, 'save_override_config') as mock_save:

                    mock_detect.return_value = Mock()
                    mock_bench.return_value = {}
                    mock_calc.return_value = Mock()
                    mock_save.return_value = True

                    result = optimizer.optimize_system()
                    # Should continue despite backup read failure
                    assert result is True
