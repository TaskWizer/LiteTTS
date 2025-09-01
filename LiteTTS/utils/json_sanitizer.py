#!/usr/bin/env python3
"""
JSON Sanitization Utility for LiteTTS

Provides robust JSON serialization that handles infinite and NaN float values
to prevent JSON serialization errors in dashboard and API responses.
"""

import math
import json
from typing import Any, Dict, List, Union


def sanitize_float(value: float, default: float = 0.0) -> float:
    """
    Sanitize a float value to ensure it's JSON-serializable.
    
    Args:
        value: The float value to sanitize
        default: Default value to return for invalid floats
        
    Returns:
        A finite float value that can be JSON serialized
    """
    if not isinstance(value, (int, float)):
        return default
    
    if math.isnan(value) or math.isinf(value):
        return default
    
    return float(value)


def sanitize_value(value: Any) -> Any:
    """
    Recursively sanitize any value to ensure JSON compatibility.
    
    Args:
        value: The value to sanitize
        
    Returns:
        A JSON-serializable version of the value
    """
    if isinstance(value, float):
        return sanitize_float(value)
    elif isinstance(value, dict):
        return {k: sanitize_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [sanitize_value(item) for item in value]
    elif isinstance(value, (int, str, bool)) or value is None:
        return value
    else:
        # For other types, convert to string as fallback
        return str(value)


def sanitize_dashboard_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize dashboard data specifically, with special handling for performance metrics.
    
    Args:
        data: Dashboard data dictionary
        
    Returns:
        Sanitized dashboard data safe for JSON serialization
    """
    sanitized = {}
    
    for key, value in data.items():
        if key == 'performance' and isinstance(value, dict):
            # Special handling for performance data
            sanitized[key] = sanitize_performance_data(value)
        else:
            sanitized[key] = sanitize_value(value)
    
    return sanitized


def sanitize_performance_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize performance data with specific defaults for metrics.
    
    Args:
        data: Performance data dictionary
        
    Returns:
        Sanitized performance data
    """
    sanitized = {}
    
    for key, value in data.items():
        if key == 'summary' and isinstance(value, dict):
            sanitized[key] = sanitize_performance_summary(value)
        else:
            sanitized[key] = sanitize_value(value)
    
    return sanitized


def sanitize_performance_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize performance summary with appropriate defaults for each metric.
    
    Args:
        summary: Performance summary dictionary
        
    Returns:
        Sanitized performance summary
    """
    sanitized = {}
    
    # Define appropriate defaults for different metrics
    metric_defaults = {
        'total_requests': 0,
        'cache_hit_rate_percent': 0.0,
        'avg_rtf': 0.0,
        'min_rtf': None,  # Use None for uninitialized min values
        'max_rtf': 0.0,
        'avg_latency_ms': 0.0,
        'min_latency_ms': None,  # Use None for uninitialized min values
        'max_latency_ms': 0.0,
        'efficiency_ratio': 0.0
    }
    
    for key, value in summary.items():
        if key in metric_defaults:
            default = metric_defaults[key]
            if default is None:
                # For min values, return None if infinite, otherwise sanitize
                if isinstance(value, float) and math.isinf(value):
                    sanitized[key] = None
                else:
                    sanitized[key] = sanitize_float(value, 0.0)
            else:
                sanitized[key] = sanitize_float(value, default) if isinstance(value, (int, float)) else value
        else:
            sanitized[key] = sanitize_value(value)
    
    return sanitized


def safe_division(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Perform safe division that handles zero denominators and produces finite results.
    
    Args:
        numerator: The numerator
        denominator: The denominator
        default: Default value to return if division is invalid
        
    Returns:
        Result of division or default if invalid
    """
    try:
        if denominator == 0:
            return default
        
        result = numerator / denominator
        return sanitize_float(result, default)
    except (ZeroDivisionError, OverflowError):
        return default


def safe_percentage(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Calculate a safe percentage that handles zero denominators.
    
    Args:
        numerator: The numerator
        denominator: The denominator  
        default: Default percentage to return if calculation is invalid
        
    Returns:
        Percentage (0-100) or default if invalid
    """
    return safe_division(numerator * 100, denominator, default)


class JSONSafeEncoder(json.JSONEncoder):
    """
    JSON encoder that automatically sanitizes infinite and NaN values.
    """
    
    def encode(self, obj):
        """Encode object with sanitization."""
        sanitized = sanitize_value(obj)
        return super().encode(sanitized)
    
    def iterencode(self, obj, _one_shot=False):
        """Iteratively encode object with sanitization."""
        sanitized = sanitize_value(obj)
        return super().iterencode(sanitized, _one_shot)


def dumps_safe(obj: Any, **kwargs) -> str:
    """
    JSON dumps with automatic sanitization of infinite and NaN values.
    
    Args:
        obj: Object to serialize
        **kwargs: Additional arguments for json.dumps
        
    Returns:
        JSON string with sanitized values
    """
    kwargs.setdefault('cls', JSONSafeEncoder)
    return json.dumps(obj, **kwargs)


def validate_json_serializable(obj: Any) -> bool:
    """
    Validate that an object can be JSON serialized without errors.
    
    Args:
        obj: Object to validate
        
    Returns:
        True if object can be JSON serialized, False otherwise
    """
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError, OverflowError):
        return False
