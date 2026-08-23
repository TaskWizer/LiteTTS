#!/usr/bin/env python3
"""
Unit tests for API error handler
"""

import pytest

from LiteTTS.api.error_handler import ErrorHandler


class TestErrorHandler:
    """Test cases for ErrorHandler"""

    @pytest.fixture
    def handler(self):
        """Create error handler instance"""
        return ErrorHandler()

    def test_initialization(self, handler):
        """Test error handler initializes correctly"""
        assert handler is not None

    def test_handle_synthesis_error_generic(self, handler):
        """Test handling of generic synthesis error"""
        error = Exception("Synthesis failed")
        result = handler.handle_synthesis_error(error)
        assert result is not None
        assert hasattr(result, "status_code")

    def test_handle_synthesis_error_empty_text(self, handler):
        """Test handling of empty text error"""
        error = ValueError("Empty text provided")
        result = handler.handle_synthesis_error(error)
        assert result is not None

    def test_handle_synthesis_error_voice_not_found(self, handler):
        """Test handling of voice not found error"""
        error = ValueError("Voice not found: nonexistent")
        result = handler.handle_synthesis_error(error)
        assert result is not None

    def test_handle_generic_error(self, handler):
        """Test handling of generic error"""
        error = Exception("Generic error")
        result = handler.handle_generic_error(error)
        assert result is not None

    def test_handle_validation_error_list(self, handler):
        """Test handling of validation error with list"""
        errors = ["Error 1", "Error 2"]
        result = handler.handle_validation_error(errors)
        assert result is not None

    def test_handle_rate_limit_error(self, handler):
        """Test handling of rate limit error"""
        result = handler.handle_rate_limit_error(retry_after=60)
        assert result is not None

    def test_handle_timeout_error(self, handler):
        """Test handling of timeout error"""
        result = handler.handle_timeout_error(timeout_seconds=30.0)
        assert result is not None

    def test_handle_service_unavailable(self, handler):
        """Test handling of service unavailable error"""
        result = handler.handle_service_unavailable("Model loading failed")
        assert result is not None

    def test_handle_not_found_error(self, handler):
        """Test handling of not found error"""
        result = handler.handle_not_found_error("voice", "nonexistent")
        assert result is not None

    def test_handle_method_not_allowed(self, handler):
        """Test handling of method not allowed error"""
        result = handler.handle_method_not_allowed("POST", "/v1/audio/speech")
        assert result is not None


class TestErrorHandlerEdgeCases:
    """Edge case tests for ErrorHandler"""

    @pytest.fixture
    def handler(self):
        return ErrorHandler()

    def test_handle_none_error(self, handler):
        """Test handling of None error"""
        result = handler.handle_synthesis_error(None)
        assert result is not None

    def test_handle_empty_error_message(self, handler):
        """Test handling of error with empty message"""
        error = Exception("")
        result = handler.handle_synthesis_error(error)
        assert result is not None

    def test_handle_validation_error_empty_list(self, handler):
        """Test handling of empty validation error list"""
        errors = []
        result = handler.handle_validation_error(errors)
        assert result is not None
