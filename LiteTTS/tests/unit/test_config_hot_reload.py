#!/usr/bin/env python3
"""
Unit tests for config hot reload module
"""

from unittest.mock import Mock


class TestConfigReloadHandler:
    """Test cases for ConfigReloadHandler"""

    def test_initialization(self):
        """Test handler initializes correctly"""
        callback = Mock()
        from LiteTTS.performance.config_hot_reload import ConfigReloadHandler
        handler = ConfigReloadHandler(callback)
        assert handler.reload_callback is callback
        assert handler.reload_delay == 1.0

    def test_initialization_custom_delay(self):
        """Test handler with custom delay"""
        callback = Mock()
        from LiteTTS.performance.config_hot_reload import ConfigReloadHandler
        handler = ConfigReloadHandler(callback)
        handler.reload_delay = 2.0
        assert handler.reload_delay == 2.0
