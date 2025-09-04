"""
WebSocket Infrastructure Test Suite for LiteTTS

This module provides comprehensive testing for WebSocket functionality
including connection handling, message broadcasting, and performance
streaming validation.
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch

# Import WebSocket components
try:
    from LiteTTS.websocket import (
        WebSocketManager,
        WebSocketMessage,
        MessageType,
        PerformanceStreamer,
        WebSocketEndpoints,
        FASTAPI_AVAILABLE
    )
    from fastapi import WebSocket
    from fastapi.testclient import TestClient
    WEBSOCKET_TESTS_AVAILABLE = True
except ImportError as e:
    WEBSOCKET_TESTS_AVAILABLE = False
    WebSocketManager = None
    WebSocket = None
    TestClient = None

import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.skipif(not WEBSOCKET_TESTS_AVAILABLE, reason="WebSocket dependencies not available")
class TestWebSocketManager:
    """Test suite for WebSocketManager functionality."""
    
    @pytest.fixture
    async def websocket_manager(self):
        """Create WebSocketManager instance for testing."""
        manager = WebSocketManager(heartbeat_interval=1.0, cleanup_interval=5.0)
        await manager.start()
        yield manager
        await manager.stop()
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket for testing."""
        websocket = Mock(spec=WebSocket)
        websocket.accept = AsyncMock()
        websocket.send_text = AsyncMock()
        websocket.close = AsyncMock()
        websocket.headers = {"user-agent": "test-client"}
        websocket.client = Mock()
        websocket.client.host = "127.0.0.1"
        return websocket
    
    @pytest.mark.asyncio
    async def test_websocket_manager_initialization(self, websocket_manager):
        """Test WebSocket manager initialization."""
        assert websocket_manager._running
        assert len(websocket_manager.clients) == 0
        assert websocket_manager.stats["total_connections"] == 0
        assert websocket_manager.stats["current_connections"] == 0
    
    @pytest.mark.asyncio
    async def test_client_connection(self, websocket_manager, mock_websocket):
        """Test client connection handling."""
        # Connect client
        client_id = await websocket_manager.connect(mock_websocket, "dashboard")
        
        # Verify connection
        assert client_id in websocket_manager.clients
        assert websocket_manager.stats["total_connections"] == 1
        assert websocket_manager.stats["current_connections"] == 1
        
        # Verify WebSocket was accepted
        mock_websocket.accept.assert_called_once()
        
        # Verify welcome message was sent
        mock_websocket.send_text.assert_called()
        
        # Disconnect client
        await websocket_manager.disconnect(client_id)
        
        # Verify disconnection
        assert client_id not in websocket_manager.clients
        assert websocket_manager.stats["current_connections"] == 0
    
    @pytest.mark.asyncio
    async def test_message_broadcasting(self, websocket_manager, mock_websocket):
        """Test message broadcasting to clients."""
        # Connect multiple clients
        client1_id = await websocket_manager.connect(mock_websocket, "dashboard")
        
        mock_websocket2 = Mock(spec=WebSocket)
        mock_websocket2.accept = AsyncMock()
        mock_websocket2.send_text = AsyncMock()
        mock_websocket2.headers = {"user-agent": "test-client-2"}
        mock_websocket2.client = Mock()
        mock_websocket2.client.host = "127.0.0.1"
        
        client2_id = await websocket_manager.connect(mock_websocket2, "dashboard")
        
        # Create test message
        test_message = WebSocketMessage(
            type=MessageType.PERFORMANCE_UPDATE,
            data={"test": "data"},
            timestamp=time.time()
        )
        
        # Broadcast message
        sent_count = await websocket_manager.broadcast(test_message, client_type="dashboard")
        
        # Verify broadcast
        assert sent_count == 2
        assert mock_websocket.send_text.call_count >= 2  # Welcome + broadcast
        assert mock_websocket2.send_text.call_count >= 2  # Welcome + broadcast
        
        # Cleanup
        await websocket_manager.disconnect(client1_id)
        await websocket_manager.disconnect(client2_id)
    
    @pytest.mark.asyncio
    async def test_heartbeat_handling(self, websocket_manager, mock_websocket):
        """Test heartbeat functionality."""
        # Connect client
        client_id = await websocket_manager.connect(mock_websocket, "dashboard")
        
        # Simulate heartbeat message
        heartbeat_data = json.dumps({
            "type": "heartbeat",
            "data": {"ping": True}
        })
        
        await websocket_manager.handle_client_message(client_id, heartbeat_data)
        
        # Verify heartbeat response was sent
        # Check that send_text was called (welcome + heartbeat response)
        assert mock_websocket.send_text.call_count >= 2
        
        # Cleanup
        await websocket_manager.disconnect(client_id)
    
    @pytest.mark.asyncio
    async def test_message_handler_registration(self, websocket_manager):
        """Test message handler registration and execution."""
        handler_called = False
        test_data = None
        
        async def test_handler(client_id: str, data: dict):
            nonlocal handler_called, test_data
            handler_called = True
            test_data = data
        
        # Register handler
        websocket_manager.register_message_handler(MessageType.DASHBOARD_UPDATE, test_handler)
        
        # Connect client and send message
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        mock_websocket.headers = {"user-agent": "test-client"}
        mock_websocket.client = Mock()
        mock_websocket.client.host = "127.0.0.1"
        
        client_id = await websocket_manager.connect(mock_websocket, "dashboard")
        
        # Send test message
        test_message_data = json.dumps({
            "type": "dashboard_update",
            "data": {"test": "handler_data"}
        })
        
        await websocket_manager.handle_client_message(client_id, test_message_data)
        
        # Verify handler was called
        assert handler_called
        assert test_data == {"test": "handler_data"}
        
        # Cleanup
        await websocket_manager.disconnect(client_id)


@pytest.mark.skipif(not WEBSOCKET_TESTS_AVAILABLE, reason="WebSocket dependencies not available")
class TestPerformanceStreamer:
    """Test suite for PerformanceStreamer functionality."""
    
    @pytest.fixture
    async def performance_streamer(self):
        """Create PerformanceStreamer instance for testing."""
        # Create mock WebSocket manager
        mock_manager = Mock(spec=WebSocketManager)
        mock_manager.broadcast = AsyncMock()
        mock_manager.get_client_count = Mock(return_value=1)
        
        streamer = PerformanceStreamer(
            websocket_manager=mock_manager,
            update_interval=0.1,  # Fast updates for testing
            history_size=10
        )
        
        await streamer.start()
        yield streamer
        await streamer.stop()
    
    @pytest.mark.asyncio
    async def test_performance_streamer_initialization(self, performance_streamer):
        """Test PerformanceStreamer initialization."""
        assert performance_streamer._running
        assert performance_streamer.current_metrics is None
        assert performance_streamer.current_status is None
        assert len(performance_streamer.metrics_history) == 0
    
    @pytest.mark.asyncio
    async def test_metrics_updates(self, performance_streamer):
        """Test application metrics updates."""
        # Update metrics
        performance_streamer.update_app_metrics(
            rtf=0.15,
            cache_hit_rate=0.85,
            voices_loaded=55
        )
        
        performance_streamer.increment_requests()
        performance_streamer.set_active_requests(3)
        performance_streamer.update_processing_time(250.0)
        
        # Verify metrics were updated
        with performance_streamer._metrics_lock:
            assert performance_streamer.app_metrics["rtf"] == 0.15
            assert performance_streamer.app_metrics["cache_hit_rate"] == 0.85
            assert performance_streamer.app_metrics["voices_loaded"] == 55
            assert performance_streamer.app_metrics["total_requests"] == 1
            assert performance_streamer.app_metrics["active_requests"] == 3
            assert performance_streamer.app_metrics["processing_time_ms"] == 250.0
    
    @pytest.mark.asyncio
    async def test_error_reporting(self, performance_streamer):
        """Test error reporting functionality."""
        # Report errors
        performance_streamer.report_error("Test error 1")
        performance_streamer.report_error("Test error 2")
        
        # Increment requests to calculate error rate
        performance_streamer.increment_requests()
        performance_streamer.increment_requests()
        
        # Verify error tracking
        with performance_streamer._metrics_lock:
            assert performance_streamer.app_metrics["last_error"] == "Test error 2"
            assert performance_streamer.app_metrics["error_rate"] > 0
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, performance_streamer):
        """Test system metrics collection."""
        # Update some app metrics first
        performance_streamer.update_app_metrics(rtf=0.2, voices_loaded=10)
        
        # Collect metrics
        metrics = performance_streamer._collect_system_metrics()
        
        # Verify metrics structure
        assert hasattr(metrics, 'timestamp')
        assert hasattr(metrics, 'rtf')
        assert hasattr(metrics, 'memory_usage_mb')
        assert hasattr(metrics, 'cpu_percent')
        assert hasattr(metrics, 'uptime_seconds')
        
        # Verify values
        assert metrics.rtf == 0.2
        assert metrics.voices_loaded == 10
        assert metrics.uptime_seconds >= 0
        assert metrics.memory_usage_mb > 0
    
    @pytest.mark.asyncio
    async def test_dashboard_data(self, performance_streamer):
        """Test dashboard data compilation."""
        # Update metrics and wait for collection
        performance_streamer.update_app_metrics(rtf=0.18, voices_loaded=25)
        
        # Wait a bit for metrics to be collected
        await asyncio.sleep(0.2)
        
        # Get dashboard data
        dashboard_data = performance_streamer.get_dashboard_data()
        
        # Verify dashboard data structure
        assert "current_metrics" in dashboard_data
        assert "current_status" in dashboard_data
        assert "recent_history" in dashboard_data
        assert "websocket_stats" in dashboard_data
        assert "update_interval" in dashboard_data


@pytest.mark.skipif(not WEBSOCKET_TESTS_AVAILABLE, reason="WebSocket dependencies not available")
class TestWebSocketEndpoints:
    """Test suite for WebSocket endpoints integration."""
    
    @pytest.fixture
    def mock_app_instance(self):
        """Create mock LiteTTSApplication instance."""
        app_instance = Mock()
        app_instance.logger = logger
        return app_instance
    
    @pytest.fixture
    async def websocket_endpoints(self, mock_app_instance):
        """Create WebSocketEndpoints instance for testing."""
        endpoints = WebSocketEndpoints(mock_app_instance)
        await endpoints.initialize()
        yield endpoints
        await endpoints.cleanup()
    
    @pytest.mark.asyncio
    async def test_websocket_endpoints_initialization(self, websocket_endpoints):
        """Test WebSocket endpoints initialization."""
        assert websocket_endpoints._initialized
        assert websocket_endpoints.websocket_manager is not None
        assert websocket_endpoints.performance_streamer is not None
    
    @pytest.mark.asyncio
    async def test_performance_metrics_integration(self, websocket_endpoints):
        """Test performance metrics integration."""
        # Update metrics through endpoints
        websocket_endpoints.update_performance_metrics(rtf=0.22, voices_loaded=30)
        websocket_endpoints.increment_requests()
        websocket_endpoints.set_active_requests(5)
        websocket_endpoints.update_processing_time(180.0)
        websocket_endpoints.report_error("Integration test error")
        
        # Verify metrics were passed to performance streamer
        streamer = websocket_endpoints.performance_streamer
        with streamer._metrics_lock:
            assert streamer.app_metrics["rtf"] == 0.22
            assert streamer.app_metrics["voices_loaded"] == 30
            assert streamer.app_metrics["total_requests"] >= 1
            assert streamer.app_metrics["active_requests"] == 5
            assert streamer.app_metrics["processing_time_ms"] == 180.0
            assert streamer.app_metrics["last_error"] == "Integration test error"
    
    @pytest.mark.asyncio
    async def test_websocket_stats_retrieval(self, websocket_endpoints):
        """Test WebSocket statistics retrieval."""
        stats = websocket_endpoints.get_websocket_stats()
        
        # Verify stats structure
        assert "total_connections" in stats
        assert "current_connections" in stats
        assert "messages_sent" in stats
        assert "messages_received" in stats
        assert "uptime_seconds" in stats
    
    @pytest.mark.asyncio
    async def test_performance_data_retrieval(self, websocket_endpoints):
        """Test performance data retrieval."""
        # Update some metrics first
        websocket_endpoints.update_performance_metrics(rtf=0.19)
        
        # Wait for metrics collection
        await asyncio.sleep(0.2)
        
        performance_data = websocket_endpoints.get_performance_data()
        
        # Verify performance data structure
        assert "current_metrics" in performance_data
        assert "current_status" in performance_data
        assert "recent_history" in performance_data
        assert "update_interval" in performance_data


def test_websocket_availability():
    """Test that WebSocket dependencies are available."""
    if WEBSOCKET_TESTS_AVAILABLE:
        assert FASTAPI_AVAILABLE
        assert WebSocketManager is not None
        assert PerformanceStreamer is not None
        logger.info("✅ WebSocket infrastructure tests available")
    else:
        logger.warning("⚠️ WebSocket infrastructure tests skipped - dependencies not available")


# Integration test with actual FastAPI app (requires running server)
@pytest.mark.skipif(not WEBSOCKET_TESTS_AVAILABLE, reason="WebSocket dependencies not available")
@pytest.mark.integration
class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality with actual FastAPI app."""
    
    def test_websocket_endpoint_setup(self):
        """Test that WebSocket endpoints can be set up with FastAPI app."""
        try:
            from fastapi import FastAPI
            from LiteTTS.websocket import setup_websocket_endpoints
            
            # Create test app
            app = FastAPI()
            mock_app_instance = Mock()
            mock_app_instance.logger = logger
            
            # Setup WebSocket endpoints
            websocket_endpoints = setup_websocket_endpoints(app, mock_app_instance)
            
            # Verify setup
            assert websocket_endpoints is not None
            assert hasattr(mock_app_instance, 'websocket_endpoints')
            
            logger.info("✅ WebSocket endpoint setup successful")
            
        except Exception as e:
            pytest.fail(f"WebSocket endpoint setup failed: {e}")


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v", "--tb=short"])
