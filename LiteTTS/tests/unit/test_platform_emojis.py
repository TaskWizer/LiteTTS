#!/usr/bin/env python3
"""
Unit tests for platform emojis module
"""

import pytest
from LiteTTS.utils.platform_emojis import (
    is_windows_with_encoding_issues,
    get_safe_emoji,
    get_emoji,
    format_log_message,
    clean_message_for_json,
    log_start,
    log_success,
    log_error,
    log_warning,
    log_info
)


class TestPlatformEmojis:
    """Test cases for platform emoji functions"""

    def test_is_windows_with_encoding_issues(self):
        """Test checking Windows encoding issues"""
        result = is_windows_with_encoding_issues()
        assert isinstance(result, bool)

    def test_get_safe_emoji(self):
        """Test getting safe emoji"""
        result = get_safe_emoji("🚀", fallback="[rocket]")
        assert isinstance(result, str)

    def test_get_emoji(self):
        """Test getting emoji"""
        result = get_emoji("test", fallback="[?]")
        assert isinstance(result, str)

    def test_format_log_message(self):
        """Test formatting log message"""
        result = format_log_message("success", "Operation completed")
        assert isinstance(result, str)

    def test_clean_message_for_json(self):
        """Test cleaning message for JSON"""
        result = clean_message_for_json("Test message")
        assert isinstance(result, str)

    def test_log_start(self):
        """Test log start"""
        result = log_start("Starting process")
        assert isinstance(result, str)

    def test_log_success(self):
        """Test log success"""
        result = log_success("Process succeeded")
        assert isinstance(result, str)

    def test_log_error(self):
        """Test log error"""
        result = log_error("Process failed")
        assert isinstance(result, str)

    def test_log_warning(self):
        """Test log warning"""
        result = log_warning("Process warning")
        assert isinstance(result, str)

    def test_log_info(self):
        """Test log info"""
        result = log_info("Process info")
        assert isinstance(result, str)


class TestPlatformEmojisEdgeCases:
    """Edge case tests for platform emoji functions"""

    def test_get_safe_emoji_with_invalid_emoji(self):
        """Test getting safe emoji with invalid input"""
        result = get_safe_emoji("invalid", fallback="[fallback]")
        assert isinstance(result, str)

    def test_get_emoji_with_invalid_name(self):
        """Test getting emoji with invalid name"""
        result = get_emoji("invalid_name_xyz", fallback="[?]")
        assert isinstance(result, str)

    def test_clean_message_for_json_with_special_chars(self):
        """Test cleaning message with special characters"""
        result = clean_message_for_json("Test with 'quotes' and \"double quotes\"")
        assert isinstance(result, str)

    def test_clean_message_for_json_empty(self):
        """Test cleaning empty message"""
        result = clean_message_for_json("")
        assert isinstance(result, str)
