#!/usr/bin/env python3
"""
Unit tests for ONNX config manager
"""

import pytest
from unittest.mock import Mock, patch


class TestONNXConfigManager:
    """Test cases for ONNXConfigManager"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        with patch.dict('sys.modules', {'onnxruntime': Mock()}):
            from LiteTTS.utils.onnx_config_manager import ONNXConfigManager
            return ONNXConfigManager()

    def test_initialization(self, manager):
        """Test manager initializes correctly"""
        assert manager is not None
        assert hasattr(manager, '_applied_configs')
