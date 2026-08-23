#!/usr/bin/env python3
"""
Unit tests for JSON sanitizer module
"""

import pytest

from LiteTTS.utils.json_sanitizer import (
    JSONSafeEncoder,
    dumps_safe,
    safe_division,
    safe_percentage,
    sanitize_dashboard_data,
    sanitize_float,
    sanitize_performance_data,
    sanitize_performance_summary,
    sanitize_value,
    validate_json_serializable,
)


class TestSanitizeFloat:
    """Test cases for sanitize_float function"""

    def test_sanitize_float_valid(self):
        """Test sanitizing valid float"""
        assert sanitize_float(1.5) == 1.5
        assert sanitize_float(0.0) == 0.0
        assert sanitize_float(-3.14) == -3.14

    def test_sanitize_float_nan(self):
        """Test sanitizing NaN returns default (0.0)"""
        # sanitize_float converts NaN to 0.0 (the default)
        assert sanitize_float(float("nan")) == 0.0

    def test_sanitize_float_inf(self):
        """Test sanitizing infinity"""
        assert sanitize_float(float("inf")) == 0.0
        assert sanitize_float(float("-inf")) == 0.0

    def test_sanitize_float_non_numeric(self):
        """Test sanitizing non-numeric values"""
        assert sanitize_float("string") == 0.0
        assert sanitize_float(None) == 0.0
        assert sanitize_float([1, 2, 3]) == 0.0

    def test_sanitize_float_custom_default(self):
        """Test sanitizing with custom default"""
        assert sanitize_float(float("nan"), default=-1.0) == -1.0
        assert sanitize_float("string", default=99.0) == 99.0


class TestSanitizeValue:
    """Test cases for sanitize_value function"""

    def test_sanitize_value_float(self):
        """Test sanitizing float values"""
        assert sanitize_value(1.5) == 1.5
        # NaN gets converted to 0.0 by sanitize_float
        assert sanitize_value(float("nan")) == 0.0

    def test_sanitize_value_dict(self):
        """Test sanitizing dictionary values"""
        result = sanitize_value({"a": 1.0, "b": float("nan")})
        assert result["a"] == 1.0
        # NaN gets converted to 0.0
        assert result["b"] == 0.0

    def test_sanitize_value_list(self):
        """Test sanitizing list values"""
        result = sanitize_value([1.0, float("nan"), 3.0])
        assert result[0] == 1.0
        # NaN gets converted to 0.0
        assert result[1] == 0.0
        assert result[2] == 3.0

    def test_sanitize_value_tuple(self):
        """Test sanitizing tuple values"""
        result = sanitize_value((1.0, float("nan")))
        assert result[0] == 1.0
        # NaN gets converted to 0.0
        assert result[1] == 0.0

    def test_sanitize_value_string(self):
        """Test sanitizing string values"""
        assert sanitize_value("hello") == "hello"

    def test_sanitize_value_bool(self):
        """Test sanitizing boolean values"""
        assert sanitize_value(True) is True
        assert sanitize_value(False) is False

    def test_sanitize_value_none(self):
        """Test sanitizing None values"""
        assert sanitize_value(None) is None

    def test_sanitize_value_nested(self):
        """Test sanitizing nested structures"""
        result = sanitize_value({"a": [1.0, float("nan")], "b": {"c": float("inf")}})
        assert result["a"][0] == 1.0
        # NaN gets converted to 0.0, inf to 0.0
        assert result["a"][1] == 0.0
        assert result["b"]["c"] == 0.0


class TestSanitizeDashboardData:
    """Test cases for sanitize_dashboard_data function"""

    def test_sanitize_dashboard_data_basic(self):
        """Test basic dashboard data sanitization"""
        data = {"requests": 100, "performance": {"avg_rtf": 0.5}}
        result = sanitize_dashboard_data(data)
        assert result["requests"] == 100

    def test_sanitize_dashboard_data_with_nan(self):
        """Test dashboard data with NaN values"""
        data = {"requests": 100, "performance": {"avg_rtf": float("nan")}}
        result = sanitize_dashboard_data(data)
        # NaN gets converted to 0.0
        assert result["performance"]["avg_rtf"] == 0.0


class TestSanitizePerformanceData:
    """Test cases for sanitize_performance_data function"""

    def test_sanitize_performance_data_basic(self):
        """Test basic performance data sanitization"""
        data = {"summary": {"total_requests": 100}}
        result = sanitize_performance_data(data)
        assert result["summary"]["total_requests"] == 100


class TestSanitizePerformanceSummary:
    """Test cases for sanitize_performance_summary function"""

    def test_sanitize_performance_summary_defaults(self):
        """Test performance summary with default values"""
        data = {"total_requests": 100, "cache_hit_rate_percent": 0.5, "avg_rtf": 0.3}
        result = sanitize_performance_summary(data)
        assert result["total_requests"] == 100
        assert result["cache_hit_rate_percent"] == 0.5

    def test_sanitize_performance_summary_inf(self):
        """Test performance summary with infinity values"""
        data = {"min_rtf": float("inf"), "max_rtf": float("inf")}
        result = sanitize_performance_summary(data)
        assert result["min_rtf"] is None
        assert result["max_rtf"] == 0.0


class TestSafeDivision:
    """Test cases for safe_division function"""

    def test_safe_division_normal(self):
        """Test normal division"""
        assert safe_division(10, 2) == 5.0

    def test_safe_division_zero_denominator(self):
        """Test division by zero"""
        assert safe_division(10, 0) == 0.0
        assert safe_division(10, 0, default=-1.0) == -1.0

    def test_safe_division_float_result(self):
        """Test division with float result"""
        assert safe_division(10, 3) == pytest.approx(3.333, 0.01)

    def test_safe_division_inf_result(self):
        """Test division resulting in infinity"""
        result = safe_division(float("inf"), 1)
        assert result == 0.0


class TestSafePercentage:
    """Test cases for safe_percentage function"""

    def test_safe_percentage_normal(self):
        """Test normal percentage calculation"""
        assert safe_percentage(25, 100) == 25.0

    def test_safe_percentage_zero_denominator(self):
        """Test percentage with zero denominator"""
        assert safe_percentage(25, 0) == 0.0

    def test_safe_percentage_half(self):
        """Test 50% calculation"""
        assert safe_percentage(1, 2) == 50.0


class TestJSONSafeEncoder:
    """Test cases for JSONSafeEncoder class"""

    def test_encode_valid(self):
        """Test encoding valid JSON"""
        encoder = JSONSafeEncoder()
        result = encoder.encode({"a": 1.0})
        assert '"a": 1.0' in result

    def test_encode_with_nan(self):
        """Test encoding with NaN value"""
        encoder = JSONSafeEncoder()
        result = encoder.encode({"a": float("nan")})
        # Should not raise, NaN should be sanitized
        assert '"a"' in result


class TestDumpsSafe:
    """Test cases for dumps_safe function"""

    def test_dumps_safe_valid(self):
        """Test dumping valid object"""
        result = dumps_safe({"a": 1.0})
        assert '"a": 1.0' in result

    def test_dumps_safe_with_nan(self):
        """Test dumping object with NaN"""
        result = dumps_safe({"a": float("nan")})
        # Should not raise
        assert '"a"' in result

    def test_dumps_safe_with_inf(self):
        """Test dumping object with infinity"""
        result = dumps_safe({"a": float("inf")})
        # Should not raise
        assert '"a"' in result


class TestValidateJsonSerializable:
    """Test cases for validate_json_serializable function"""

    def test_validate_valid_dict(self):
        """Test validating valid dictionary"""
        assert validate_json_serializable({"a": 1}) is True

    def test_validate_valid_list(self):
        """Test validating valid list"""
        assert validate_json_serializable([1, 2, 3]) is True

    def test_validate_invalid(self):
        """Test validating invalid object (unserializable)"""

        class Unserializable:
            pass

        assert validate_json_serializable(Unserializable()) is False

    def test_validate_with_nan(self):
        """Test validating with NaN returns True (passes through)"""
        # NaN passes validation since sanitize_float is only used in encoding, not validation
        assert validate_json_serializable(float("nan")) is True

    def test_validate_string(self):
        """Test validating string"""
        assert validate_json_serializable("hello") is True

    def test_validate_none(self):
        """Test validating None"""
        assert validate_json_serializable(None) is True
