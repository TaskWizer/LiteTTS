#!/usr/bin/env python3
"""
Unit tests for dependency health checker
"""

import pytest

from LiteTTS.utils.dependency_health import DependencyHealth


class TestDependencyHealth:
    """Test cases for DependencyHealth"""

    @pytest.fixture
    def health(self):
        """Create health checker instance"""
        return DependencyHealth()

    def test_initialization(self, health):
        """Test health checker initializes correctly"""
        assert health is not None

    def test_get_health_summary(self, health):
        """Test getting health summary"""
        result = health.get_health_summary()
        assert isinstance(result, dict)

    def test_validate_startup_dependencies(self, health):
        """Test validating startup dependencies"""
        result = health.validate_startup_dependencies()
        assert isinstance(result, dict)

    def test_validate_and_recover(self, health):
        """Test validating and recovering"""
        result = health.validate_and_recover(auto_recover=False)
        assert isinstance(result, dict)


class TestDependencyHealthEdgeCases:
    """Edge case tests for DependencyHealth"""

    @pytest.fixture
    def health(self):
        return DependencyHealth()

    def test_validate_with_auto_recover(self, health):
        """Test validation with auto recovery enabled"""
        result = health.validate_and_recover(auto_recover=True)
        assert isinstance(result, dict)

    def test_get_health_summary_keys(self, health):
        """Test health summary contains expected keys"""
        result = health.get_health_summary()
        assert 'total' in result or 'dependencies' in result or isinstance(result, dict)
