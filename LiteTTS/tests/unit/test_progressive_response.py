#!/usr/bin/env python3
"""
Unit tests for progressive response handler
"""

from unittest.mock import Mock


class TestProgressiveResponseHandler:
    """Test cases for ProgressiveResponseHandler"""

    def test_initialization(self):
        """Test handler initializes correctly"""
        from LiteTTS.api.progressive_response import ProgressiveResponseHandler
        mock_generator = Mock()
        handler = ProgressiveResponseHandler(mock_generator)
        assert handler is not None
        assert handler.progressive_generator is mock_generator
        assert isinstance(handler.active_streams, dict)
