#!/usr/bin/env python3
"""
Unit tests for JSON sanitizer
"""

import pytest
from LiteTTS.utils.json_sanitizer import (
    sanitize_float,
    sanitize_value,
    sanitize_dashboard_data,
    sanitize_performance_data,
    safe_division,
    safe_percentage,
    validate_json_serializable
)


class TestJSONSanitizer:
    """Test cases for JSON sanitizer functions"""

    def test_sanitize_float_valid(self):
        """Test sanitizing valid float"""
        result = sanitize_float(3.14)
        assert result == 3.14

    def test_sanitize_float_invalid(self):
        """Test sanitizing invalid float"""
        result = sanitize_float("invalid")
        assert result == 0.0

    def test_sanitize_float_with_default(self):
        """Test sanitizing with default value"""
        result = sanitize_float("invalid", default=1.5)
        assert result == 1.5

    def test_sanitize_value_string(self):
        """Test sanitizing string value"""
        result = sanitize_value("hello")
        assert result == "hello"

    def test_sanitize_value_none(self):
        """Test sanitizing None value"""
        result = sanitize_value(None)
        assert result is None

    def test_sanitize_value_list(self):
        """Test sanitizing list value"""
        result = sanitize_value([1, 2, 3])
        assert result == [1, 2, 3]

    def test_sanitize_dashboard_data(self):
        """Test sanitizing dashboard data"""
        data = {"cpu": "50%", "memory": "100MB"}
        result = sanitize_dashboard_data(data)
        assert result is not None

    def test_sanitize_performance_data(self):
        """Test sanitizing performance data"""
        data = {"rtf": 0.5, "latency": 100}
        result = sanitize_performance_data(data)
        assert result is not None

    def test_safe_division_valid(self):
        """Test safe division with valid inputs"""
        result = safe_division(10, 2)
        assert result == 5.0

    def test_safe_division_by_zero(self):
        """Test safe division by zero"""
        result = safe_division(10, 0)
        assert result == 0.0

    def test_safe_percentage_valid(self):
        """Test safe percentage calculation"""
        result = safe_percentage(50, 100)
        assert result == 50.0

    def test_safe_percentage_by_zero(self):
        """Test safe percentage by zero"""
        result = safe_percentage(50, 0)
        assert result == 0.0

    def test_validate_json_serializable_true(self):
        """Test validation returns True for serializable"""
        assert validate_json_serializable({"key": "value"}) is True

    def test_validate_json_serializable_false(self):
        """Test validation returns False for non-serializable"""
        class NotSerializable:
            pass
        assert validate_json_serializable(NotSerializable()) is False


class TestJSONSanitizerEdgeCases:
    """Edge case tests for JSON sanitizer functions"""

    def test_sanitize_float_inf(self):
        """Test sanitizing infinity"""
        result = sanitize_float(float('inf'))
        assert result == 0.0

    def test_sanitize_float_nan(self):
        """Test sanitizing NaN"""
        import math
        result = sanitize_float(float('nan'))
        assert result == 0.0

    def test_sanitize_value_deeply_nested(self):
        """Test sanitizing deeply nested value"""
        data = {"a": {"b": {"c": {"d": "value"}}}}
        result = sanitize_value(data)
        assert result == data

    def test_safe_division_negative(self):
        """Test safe division with negative result"""
        result = safe_division(-10, 2)
        assert result == -5.0
