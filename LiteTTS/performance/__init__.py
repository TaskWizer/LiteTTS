#!/usr/bin/env python3
"""
Kokoro TTS Performance Package

This package provides performance enhancement features for the Kokoro ONNX TTS API,
including hot reload capabilities, fault tolerance mechanisms, and performance
monitoring tools.

Features:
- Hot reload for models and voices without server restart
- Circuit breaker pattern for fault tolerance
- Retry logic with exponential backoff
- Health checking system for components
- Performance monitoring and metrics collection
- Graceful degradation mechanisms

Available modules:
- hot_reload: HotReloadManager and PerformanceMonitor classes
- fault_tolerance: CircuitBreaker, RetryManager, HealthChecker, and GracefulDegradation classes
"""

from .hot_reload import (
    HotReloadManager,
    get_hot_reload_manager,
    get_performance_monitor
)

from .monitor import (
    PerformanceMonitor,
    TTSPerformanceData,
    SystemMetrics
)

from .fault_tolerance import (
    CircuitBreaker,
    RetryManager,
    HealthChecker,
    GracefulDegradation,
    get_health_checker,
    get_graceful_degradation,
    check_model_file_exists,
    check_voices_directory,
    check_disk_space,
    check_memory_usage
)

__all__ = [
    # Hot reload functionality
    'HotReloadManager',
    'get_hot_reload_manager',
    'get_performance_monitor',

    # Performance monitoring
    'PerformanceMonitor',
    'TTSPerformanceData',
    'SystemMetrics',

    # Fault tolerance functionality
    'CircuitBreaker',
    'RetryManager',
    'HealthChecker',
    'GracefulDegradation',
    'get_health_checker',
    'get_graceful_degradation',

    # Health check functions
    'check_model_file_exists',
    'check_voices_directory',
    'check_disk_space',
    'check_memory_usage'
]

__version__ = '1.0.0'
