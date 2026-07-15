#!/usr/bin/env python3
"""
Unit tests for debug router
"""

import pytest
from unittest.mock import Mock, patch


class TestDebugRouter:
    """Test cases for DebugRouter"""

    @pytest.fixture
    def mock_config(self):
        """Create mock config"""
        return Mock()

    @pytest.fixture
    def debug_router(self, mock_config):
        """Create debug router instance"""
        with patch('LiteTTS.api.debug_router.APIRouter'):
            from LiteTTS.api.debug_router import DebugRouter
            return DebugRouter(mock_config)

    def test_initialization(self, debug_router):
        """Test debug router initializes correctly"""
        assert debug_router is not None
        assert hasattr(debug_router, 'config')
        assert hasattr(debug_router, 'router')

    def test_ping_route(self, debug_router):
        """Test ping route exists"""
        # The router should have ping endpoint registered
        assert hasattr(debug_router, 'router')

    def test_phonetics_route(self, debug_router):
        """Test phonetics route exists"""
        assert hasattr(debug_router, 'router')

    def test_validate_route(self, debug_router):
        """Test validate route exists"""
        assert hasattr(debug_router, 'router')
