"""
LiteTTS WebSocket Module

This module provides WebSocket infrastructure for real-time dashboard
communication, including connection management, message broadcasting,
and performance metrics streaming.
"""

from .websocket_manager import (
    WebSocketManager,
    WebSocketMessage,
    MessageType,
    ClientInfo,
    websocket_manager,
    get_websocket_manager,
    FASTAPI_AVAILABLE
)

from .performance_streamer import (
    PerformanceStreamer,
    PerformanceMetrics,
    SystemStatus,
    create_performance_streamer
)

from .endpoints import (
    WebSocketEndpoints,
    setup_websocket_endpoints
)

__all__ = [
    "WebSocketManager",
    "WebSocketMessage",
    "MessageType",
    "ClientInfo",
    "websocket_manager",
    "get_websocket_manager",
    "FASTAPI_AVAILABLE",
    "PerformanceStreamer",
    "PerformanceMetrics",
    "SystemStatus",
    "create_performance_streamer",
    "WebSocketEndpoints",
    "setup_websocket_endpoints"
]
