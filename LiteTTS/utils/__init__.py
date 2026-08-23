#!/usr/bin/env python3
"""
LiteTTS Utilities Package

Provides common utility functions for the LiteTTS system.
"""

from .json_sanitizer import (
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

__all__ = [
    "JSONSafeEncoder",
    "dumps_safe",
    "safe_division",
    "safe_percentage",
    "sanitize_dashboard_data",
    "sanitize_float",
    "sanitize_performance_data",
    "sanitize_performance_summary",
    "sanitize_value",
    "validate_json_serializable",
]
