#!/usr/bin/env python3
"""
Unit tests for deprecation warnings manager
"""

import pytest

from LiteTTS.utils.deprecation_warnings import (
    DeprecationWarningManager,
    initialize_warning_suppression,
    suppress_known_warnings,
)


class TestDeprecationWarningManager:
    """Test cases for DeprecationWarningManager"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        return DeprecationWarningManager()

    def test_initialization(self, manager):
        """Test manager initializes correctly"""
        assert manager is not None
        assert isinstance(manager.suppressed_warnings, list)
        assert isinstance(manager.warning_counts, dict)

    def test_suppress_pkg_resources_warnings(self, manager):
        """Test suppressing pkg_resources warnings"""
        result = manager.suppress_pkg_resources_warnings()
        assert result is None

    def test_suppress_setuptools_warnings(self, manager):
        """Test suppressing setuptools warnings"""
        result = manager.suppress_setuptools_warnings()
        assert result is None

    def test_suppress_torch_warnings(self, manager):
        """Test suppressing torch warnings"""
        result = manager.suppress_torch_warnings()
        assert result is None

    def test_apply_all_suppressions(self, manager):
        """Test applying all suppressions"""
        result = manager.apply_all_suppressions()
        assert result is None

    def test_get_suppression_summary(self, manager):
        """Test getting suppression summary"""
        result = manager.get_suppression_summary()
        assert isinstance(result, dict)


class TestModuleFunctions:
    """Test module-level functions"""

    def test_suppress_known_warnings(self):
        """Test suppress_known_warnings function"""
        result = suppress_known_warnings()
        assert result is None

    def test_initialize_warning_suppression(self):
        """Test initialize_warning_suppression function"""
        result = initialize_warning_suppression()
        assert result is None
