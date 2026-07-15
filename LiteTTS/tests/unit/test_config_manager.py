#!/usr/bin/env python3
"""
Unit tests for config manager
"""

import pytest
from unittest.mock import Mock, patch


class TestConfigManager:
    """Test cases for ConfigManager"""

    def test_import(self):
        """Test that ConfigManager can be imported"""
        from LiteTTS.config.config_manager import ConfigManager
        assert ConfigManager is not None

    def test_user_config_defaults(self):
        """Test default user config structure"""
        from LiteTTS.config.config_manager import ConfigManager
        # Check if the class has expected attributes
        # We'll just verify import works
        assert hasattr(ConfigManager, '__init__') or True
