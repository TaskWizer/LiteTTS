"""
LiteTTS WebSocket Module

This module provides WebSocket infrastructure for real-time dashboard
communication, including connection management, message broadcasting,
and performance metrics streaming.
"""

from .endpoints import WebSocketEndpoints, setup_websocket_endpoints
from .performance_streamer import (
    PerformanceMetrics,
    PerformanceStreamer,
    SystemStatus,
    create_performance_streamer,
)
from .websocket_manager import (
    FASTAPI_AVAILABLE,
    ClientInfo,
    MessageType,
    WebSocketManager,
    WebSocketMessage,
    get_websocket_manager,
    websocket_manager,
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
