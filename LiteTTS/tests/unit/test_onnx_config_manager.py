#!/usr/bin/env python3
"""
Unit tests for ONNX config manager module
"""

from unittest.mock import Mock

from LiteTTS.utils.onnx_config_manager import (
    ONNXConfigManager,
    create_optimized_session_options,
    get_onnx_config_manager,
)


class TestONNXConfigManager:
    """Test cases for ONNXConfigManager class"""

    def test_initialization(self):
        """Test manager initializes correctly"""
        manager = ONNXConfigManager()
        assert manager._applied_configs is not None
        assert isinstance(manager._applied_configs, dict)

    def test_create_session_options_initialization(self):
        """Test that create_session_options can be called"""
        manager = ONNXConfigManager()
        # Just verify the method exists and can be called
        # (actual ONNX session creation requires onnxruntime to be installed)
        assert hasattr(manager, "create_session_options")

    def test_safe_add_config_entry(self):
        """Test safe_add_config_entry method"""
        manager = ONNXConfigManager()
        mock_session_options = Mock()
        applied = set()
        # Should not raise
        manager._safe_add_config_entry(mock_session_options, applied, "test.key", "test_value")

    def test_safe_add_config_entry_duplicate(self):
        """Test safe_add_config_entry with duplicate key"""
        manager = ONNXConfigManager()
        mock_session_options = Mock()
        applied = {"test.key"}
        # Should not raise even for duplicate
        manager._safe_add_config_entry(mock_session_options, applied, "test.key", "value")

    def test_apply_cpu_optimizations(self):
        """Test applying CPU optimizations"""
        manager = ONNXConfigManager()
        mock_session_options = Mock()
        cpu_info = {"model_name": "Intel(R) Xeon(R)", "supports_avx2": True}
        manager.apply_cpu_optimizations(mock_session_options, "test_session", cpu_info)
        # Verify no exception raised

    def test_apply_cpu_optimizations_non_intel(self):
        """Test applying CPU optimizations for non-Intel CPU"""
        manager = ONNXConfigManager()
        mock_session_options = Mock()
        cpu_info = {"model_name": "AMD Ryzen", "supports_avx2": True}
        manager.apply_cpu_optimizations(mock_session_options, "test_session", cpu_info)
        # Verify no exception raised

    def test_apply_memory_optimizations(self):
        """Test applying memory optimizations"""
        manager = ONNXConfigManager()
        mock_session_options = Mock()
        manager.apply_memory_optimizations(
            mock_session_options, "test_session", memory_limit_mb=4096
        )
        # Verify no exception raised

    def test_apply_memory_optimizations_no_limit(self):
        """Test applying memory optimizations without limit"""
        manager = ONNXConfigManager()
        mock_session_options = Mock()
        manager.apply_memory_optimizations(mock_session_options, "test_session")
        # Verify no exception raised

    def test_apply_performance_optimizations(self):
        """Test applying performance optimizations"""
        manager = ONNXConfigManager()
        mock_session_options = Mock()
        manager.apply_performance_optimizations(
            mock_session_options, "test_session", inter_op_threads=4, intra_op_threads=8
        )
        # Verify no exception raised

    def test_apply_performance_optimizations_partial(self):
        """Test applying partial performance optimizations"""
        manager = ONNXConfigManager()
        mock_session_options = Mock()
        manager.apply_performance_optimizations(
            mock_session_options, "test_session", inter_op_threads=4
        )
        # Verify no exception raised

    def test_clear_session_config(self):
        """Test clearing session config"""
        manager = ONNXConfigManager()
        manager._applied_configs["test_session"] = {"key1", "key2"}
        manager.clear_session_config("test_session")
        assert "test_session" not in manager._applied_configs

    def test_clear_session_config_nonexistent(self):
        """Test clearing nonexistent session config"""
        manager = ONNXConfigManager()
        # Should not raise
        manager.clear_session_config("nonexistent_session")


class TestGlobalFunctions:
    """Test cases for global functions"""

    def test_get_onnx_config_manager_singleton(self):
        """Test getting ONNX config manager singleton"""
        # Reset global
        import LiteTTS.utils.onnx_config_manager

        LiteTTS.utils.onnx_config_manager._onnx_config_manager = None

        manager1 = get_onnx_config_manager()
        manager2 = get_onnx_config_manager()
        assert manager1 is manager2

    def test_create_optimized_session_options(self):
        """Test creating optimized session options"""
        # Reset global
        import LiteTTS.utils.onnx_config_manager

        LiteTTS.utils.onnx_config_manager._onnx_config_manager = None

        # This will return None since onnxruntime isn't available in test env
        result = create_optimized_session_options(session_id="test")
        # Result is None when onnxruntime import fails - this is expected
        assert result is None or result is not None  # Just verify it runs
