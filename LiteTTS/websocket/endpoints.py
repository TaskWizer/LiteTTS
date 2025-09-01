"""
WebSocket Endpoints for LiteTTS

This module provides WebSocket endpoint implementations for the FastAPI
application, including dashboard connectivity and real-time communication.
"""

import asyncio
import logging
import time
from typing import Optional
from dataclasses import asdict
from fastapi import WebSocket, WebSocketDisconnect, HTTPException

from .websocket_manager import WebSocketManager, WebSocketMessage, MessageType, get_websocket_manager
from .performance_streamer import PerformanceStreamer, create_performance_streamer

logger = logging.getLogger(__name__)


class WebSocketEndpoints:
    """
    WebSocket endpoints manager for LiteTTS FastAPI application.
    
    Provides WebSocket endpoint implementations with proper connection
    handling, authentication, and error management.
    """
    
    def __init__(self, app_instance):
        """
        Initialize WebSocket endpoints.
        
        Args:
            app_instance: LiteTTSApplication instance
        """
        self.app_instance = app_instance
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # WebSocket infrastructure
        self.websocket_manager: Optional[WebSocketManager] = None
        self.performance_streamer: Optional[PerformanceStreamer] = None
        
        # Initialize flag
        self._initialized = False
    
    async def initialize(self):
        """Initialize WebSocket infrastructure."""
        if self._initialized:
            return
        
        try:
            self.logger.info("Initializing WebSocket infrastructure...")
            
            # Get WebSocket manager
            self.websocket_manager = await get_websocket_manager()
            
            # Create performance streamer
            self.performance_streamer = create_performance_streamer(
                websocket_manager=self.websocket_manager,
                update_interval=1.0  # 1 second updates
            )
            
            # Start performance streamer
            await self.performance_streamer.start()
            
            # Register message handlers
            self._register_message_handlers()
            
            self._initialized = True
            self.logger.info("✅ WebSocket infrastructure initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebSocket infrastructure: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup WebSocket infrastructure."""
        if not self._initialized:
            return
        
        try:
            self.logger.info("Cleaning up WebSocket infrastructure...")
            
            # Stop performance streamer
            if self.performance_streamer:
                await self.performance_streamer.stop()
            
            # Stop WebSocket manager
            if self.websocket_manager:
                await self.websocket_manager.stop()
            
            self._initialized = False
            self.logger.info("WebSocket infrastructure cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during WebSocket cleanup: {e}")
    
    def _register_message_handlers(self):
        """Register WebSocket message handlers."""
        if not self.websocket_manager:
            return
        
        # Register dashboard-specific message handlers
        self.websocket_manager.register_message_handler(
            MessageType.DASHBOARD_UPDATE,
            self._handle_dashboard_update
        )
        
        self.logger.info("WebSocket message handlers registered")
    
    async def _handle_dashboard_update(self, client_id: str, data: dict):
        """Handle dashboard update requests from clients."""
        try:
            # Handle different types of dashboard updates
            update_type = data.get("type", "unknown")
            
            if update_type == "request_full_data":
                # Send comprehensive dashboard data
                if self.performance_streamer:
                    dashboard_data = self.performance_streamer.get_dashboard_data()
                    
                    message = WebSocketMessage(
                        type=MessageType.DASHBOARD_UPDATE,
                        data={
                            "type": "full_data",
                            "dashboard_data": dashboard_data
                        },
                        timestamp=time.time(),
                        client_id=client_id
                    )
                    
                    await self.websocket_manager.send_to_client(client_id, message)
            
            elif update_type == "request_metrics_history":
                # Send metrics history
                if self.performance_streamer:
                    limit = data.get("limit", 60)
                    history = self.performance_streamer.get_metrics_history(limit)
                    
                    message = WebSocketMessage(
                        type=MessageType.DASHBOARD_UPDATE,
                        data={
                            "type": "metrics_history",
                            "history": [asdict(m) for m in history]
                        },
                        timestamp=time.time(),
                        client_id=client_id
                    )
                    
                    await self.websocket_manager.send_to_client(client_id, message)
            
        except Exception as e:
            self.logger.error(f"Error handling dashboard update: {e}")
    
    async def dashboard_websocket_endpoint(self, websocket: WebSocket):
        """
        WebSocket endpoint for dashboard connectivity.
        
        Args:
            websocket: FastAPI WebSocket instance
        """
        if not self._initialized:
            await self.initialize()
        
        client_id = None
        
        try:
            # Connect client
            client_id = await self.websocket_manager.connect(websocket, client_type="dashboard")
            self.logger.info(f"Dashboard client connected: {client_id}")
            
            # Send initial dashboard data
            if self.performance_streamer:
                dashboard_data = self.performance_streamer.get_dashboard_data()
                
                welcome_message = WebSocketMessage(
                    type=MessageType.DASHBOARD_UPDATE,
                    data={
                        "type": "welcome",
                        "dashboard_data": dashboard_data
                    },
                    timestamp=time.time(),
                    client_id=client_id
                )
                
                await self.websocket_manager.send_to_client(client_id, welcome_message)
            
            # Handle incoming messages
            while True:
                try:
                    # Receive message from client
                    message_data = await websocket.receive_text()
                    
                    # Handle message through WebSocket manager
                    await self.websocket_manager.handle_client_message(client_id, message_data)
                    
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    self.logger.error(f"Error handling WebSocket message: {e}")
                    # Send error message to client
                    error_message = WebSocketMessage(
                        type=MessageType.ERROR,
                        data={
                            "error": str(e),
                            "timestamp": time.time()
                        },
                        timestamp=time.time(),
                        client_id=client_id
                    )
                    
                    try:
                        await self.websocket_manager.send_to_client(client_id, error_message)
                    except:
                        break  # Connection likely closed
        
        except WebSocketDisconnect:
            self.logger.info(f"Dashboard client disconnected: {client_id}")
        except Exception as e:
            self.logger.error(f"WebSocket endpoint error: {e}")
        finally:
            # Cleanup client connection
            if client_id and self.websocket_manager:
                await self.websocket_manager.disconnect(client_id, "Connection closed")
    
    def update_performance_metrics(self, **metrics):
        """
        Update performance metrics for streaming.
        
        Args:
            **metrics: Metric name-value pairs to update
        """
        if self.performance_streamer:
            self.performance_streamer.update_app_metrics(**metrics)
    
    def increment_requests(self):
        """Increment total request counter."""
        if self.performance_streamer:
            self.performance_streamer.increment_requests()
    
    def set_active_requests(self, count: int):
        """Set current active request count."""
        if self.performance_streamer:
            self.performance_streamer.set_active_requests(count)
    
    def update_rtf(self, rtf: float):
        """Update current RTF (Real-Time Factor)."""
        if self.performance_streamer:
            self.performance_streamer.update_rtf(rtf)
    
    def update_processing_time(self, time_ms: float):
        """Update last processing time."""
        if self.performance_streamer:
            self.performance_streamer.update_processing_time(time_ms)
    
    def report_error(self, error_message: str):
        """Report an error for metrics tracking."""
        if self.performance_streamer:
            self.performance_streamer.report_error(error_message)
    
    def get_websocket_stats(self) -> dict:
        """Get WebSocket connection statistics."""
        if self.websocket_manager:
            return self.websocket_manager.get_stats()
        return {}
    
    def get_performance_data(self) -> dict:
        """Get current performance data."""
        if self.performance_streamer:
            return self.performance_streamer.get_dashboard_data()
        return {}


def setup_websocket_endpoints(app, app_instance):
    """
    Setup WebSocket endpoints for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        app_instance: LiteTTSApplication instance
    """
    # Create WebSocket endpoints manager
    websocket_endpoints = WebSocketEndpoints(app_instance)
    
    # Store reference in app instance for access from other parts of the application
    app_instance.websocket_endpoints = websocket_endpoints
    
    @app.websocket("/ws/dashboard")
    async def dashboard_websocket(websocket: WebSocket):
        """WebSocket endpoint for dashboard connectivity"""
        await websocket_endpoints.dashboard_websocket_endpoint(websocket)
    
    @app.get("/ws/stats")
    async def websocket_stats():
        """Get WebSocket connection statistics"""
        try:
            return websocket_endpoints.get_websocket_stats()
        except Exception as e:
            logger.error(f"Error getting WebSocket stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/ws/performance")
    async def performance_data():
        """Get current performance data"""
        try:
            return websocket_endpoints.get_performance_data()
        except Exception as e:
            logger.error(f"Error getting performance data: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Add cleanup to application lifespan
    original_lifespan = getattr(app_instance, 'lifespan', None)
    
    async def enhanced_lifespan(app):
        """Enhanced lifespan with WebSocket cleanup"""
        # Initialize WebSocket infrastructure
        await websocket_endpoints.initialize()
        
        try:
            # Call original lifespan if it exists
            if original_lifespan:
                async with original_lifespan(app):
                    yield
            else:
                yield
        finally:
            # Cleanup WebSocket infrastructure
            await websocket_endpoints.cleanup()
    
    # Replace lifespan
    app_instance.lifespan = enhanced_lifespan
    
    logger.info("✅ WebSocket endpoints configured")
    return websocket_endpoints
