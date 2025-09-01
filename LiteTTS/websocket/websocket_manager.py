"""
WebSocket Manager for LiteTTS

This module provides WebSocket connection management, message broadcasting,
and client management for real-time dashboard communication.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Set, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

try:
    from fastapi import WebSocket, WebSocketDisconnect
    from websockets.exceptions import ConnectionClosed
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    WebSocket = None
    WebSocketDisconnect = Exception
    ConnectionClosed = Exception

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """WebSocket message types"""
    PERFORMANCE_UPDATE = "performance_update"
    SYSTEM_STATUS = "system_status"
    VOICE_STATUS = "voice_status"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    CLIENT_INFO = "client_info"
    DASHBOARD_UPDATE = "dashboard_update"


@dataclass
class ClientInfo:
    """Information about a connected WebSocket client"""
    client_id: str
    websocket: WebSocket
    connected_at: float
    last_heartbeat: float
    client_type: str = "dashboard"
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


@dataclass
class WebSocketMessage:
    """Structured WebSocket message"""
    type: MessageType
    data: Dict[str, Any]
    timestamp: float
    client_id: Optional[str] = None
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps({
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "client_id": self.client_id
        })


class WebSocketManager:
    """
    WebSocket connection manager for real-time communication.
    
    Handles client connections, message broadcasting, heartbeat monitoring,
    and connection lifecycle management for the LiteTTS dashboard.
    """
    
    def __init__(self, heartbeat_interval: float = 30.0, cleanup_interval: float = 60.0):
        """
        Initialize WebSocket manager.
        
        Args:
            heartbeat_interval: Interval for heartbeat checks (seconds)
            cleanup_interval: Interval for connection cleanup (seconds)
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not available. Install with: pip install fastapi")
        
        self.clients: Dict[str, ClientInfo] = {}
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.heartbeat_interval = heartbeat_interval
        self.cleanup_interval = cleanup_interval
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Background tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "current_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "start_time": time.time()
        }
    
    async def start(self):
        """Start the WebSocket manager and background tasks."""
        if self._running:
            return
        
        self._running = True
        self.logger.info("Starting WebSocket manager...")
        
        # Start background tasks
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        self.logger.info("✅ WebSocket manager started")
    
    async def stop(self):
        """Stop the WebSocket manager and cleanup connections."""
        if not self._running:
            return
        
        self._running = False
        self.logger.info("Stopping WebSocket manager...")
        
        # Cancel background tasks
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect all clients
        await self._disconnect_all_clients()
        
        self.logger.info("WebSocket manager stopped")
    
    async def connect(self, websocket: WebSocket, client_type: str = "dashboard") -> str:
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
            client_type: Type of client connecting
            
        Returns:
            str: Unique client ID
        """
        await websocket.accept()
        
        # Generate unique client ID
        client_id = str(uuid.uuid4())
        
        # Extract client information
        headers = dict(websocket.headers)
        user_agent = headers.get("user-agent")
        
        # Get client IP (simplified)
        ip_address = getattr(websocket.client, 'host', 'unknown') if websocket.client else 'unknown'
        
        # Create client info
        client_info = ClientInfo(
            client_id=client_id,
            websocket=websocket,
            connected_at=time.time(),
            last_heartbeat=time.time(),
            client_type=client_type,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # Store client
        self.clients[client_id] = client_info
        
        # Update statistics
        self.stats["total_connections"] += 1
        self.stats["current_connections"] = len(self.clients)
        
        self.logger.info(f"✅ Client connected: {client_id} ({client_type}) from {ip_address}")
        
        # Send welcome message
        await self.send_to_client(client_id, WebSocketMessage(
            type=MessageType.CLIENT_INFO,
            data={
                "client_id": client_id,
                "server_time": time.time(),
                "message": "Connected to LiteTTS WebSocket"
            },
            timestamp=time.time(),
            client_id=client_id
        ))
        
        return client_id
    
    async def disconnect(self, client_id: str, reason: str = "Client disconnected"):
        """
        Disconnect a WebSocket client.
        
        Args:
            client_id: Client ID to disconnect
            reason: Reason for disconnection
        """
        if client_id not in self.clients:
            return
        
        client_info = self.clients[client_id]
        
        try:
            # Close WebSocket connection
            await client_info.websocket.close()
        except Exception as e:
            self.logger.warning(f"Error closing WebSocket for {client_id}: {e}")
        
        # Remove from clients
        del self.clients[client_id]
        
        # Update statistics
        self.stats["current_connections"] = len(self.clients)
        
        self.logger.info(f"Client disconnected: {client_id} - {reason}")
    
    async def send_to_client(self, client_id: str, message: WebSocketMessage) -> bool:
        """
        Send message to a specific client.
        
        Args:
            client_id: Target client ID
            message: Message to send
            
        Returns:
            bool: True if sent successfully
        """
        if client_id not in self.clients:
            return False
        
        client_info = self.clients[client_id]
        
        try:
            await client_info.websocket.send_text(message.to_json())
            self.stats["messages_sent"] += 1
            return True
            
        except (WebSocketDisconnect, ConnectionClosed, Exception) as e:
            self.logger.warning(f"Failed to send message to {client_id}: {e}")
            # Schedule client for disconnection
            asyncio.create_task(self.disconnect(client_id, f"Send failed: {e}"))
            self.stats["errors"] += 1
            return False
    
    async def broadcast(self, message: WebSocketMessage, client_type: Optional[str] = None) -> int:
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Message to broadcast
            client_type: Optional filter by client type
            
        Returns:
            int: Number of clients message was sent to
        """
        sent_count = 0
        
        # Filter clients by type if specified
        target_clients = self.clients.values()
        if client_type:
            target_clients = [c for c in target_clients if c.client_type == client_type]
        
        # Send to all target clients
        for client_info in target_clients:
            success = await self.send_to_client(client_info.client_id, message)
            if success:
                sent_count += 1
        
        return sent_count
    
    async def handle_client_message(self, client_id: str, message_data: str):
        """
        Handle incoming message from client.
        
        Args:
            client_id: Client ID that sent the message
            message_data: Raw message data
        """
        try:
            # Parse message
            data = json.loads(message_data)
            message_type = MessageType(data.get("type", "unknown"))
            
            # Update client heartbeat
            if client_id in self.clients:
                self.clients[client_id].last_heartbeat = time.time()
            
            # Update statistics
            self.stats["messages_received"] += 1
            
            # Handle heartbeat
            if message_type == MessageType.HEARTBEAT:
                await self.send_to_client(client_id, WebSocketMessage(
                    type=MessageType.HEARTBEAT,
                    data={"pong": True, "server_time": time.time()},
                    timestamp=time.time(),
                    client_id=client_id
                ))
                return
            
            # Call registered handlers
            if message_type in self.message_handlers:
                for handler in self.message_handlers[message_type]:
                    try:
                        await handler(client_id, data.get("data", {}))
                    except Exception as e:
                        self.logger.error(f"Message handler error: {e}")
            
        except Exception as e:
            self.logger.error(f"Error handling message from {client_id}: {e}")
            self.stats["errors"] += 1
    
    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """
        Register a message handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async function to handle the message
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        
        self.message_handlers[message_type].append(handler)
        self.logger.info(f"Registered handler for {message_type.value}")
    
    async def _heartbeat_loop(self):
        """Background task for heartbeat monitoring."""
        while self._running:
            try:
                current_time = time.time()
                stale_clients = []
                
                # Check for stale connections
                for client_id, client_info in self.clients.items():
                    if current_time - client_info.last_heartbeat > self.heartbeat_interval * 2:
                        stale_clients.append(client_id)
                
                # Disconnect stale clients
                for client_id in stale_clients:
                    await self.disconnect(client_id, "Heartbeat timeout")
                
                # Send heartbeat to all clients
                if self.clients:
                    heartbeat_message = WebSocketMessage(
                        type=MessageType.HEARTBEAT,
                        data={"ping": True, "server_time": current_time},
                        timestamp=current_time
                    )
                    await self.broadcast(heartbeat_message)
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_loop(self):
        """Background task for periodic cleanup."""
        while self._running:
            try:
                # Cleanup can be extended for other maintenance tasks
                await asyncio.sleep(self.cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(10)
    
    async def _disconnect_all_clients(self):
        """Disconnect all connected clients."""
        client_ids = list(self.clients.keys())
        for client_id in client_ids:
            await self.disconnect(client_id, "Server shutdown")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics."""
        current_time = time.time()
        uptime = current_time - self.stats["start_time"]
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "clients": {
                client_id: {
                    "client_type": info.client_type,
                    "connected_at": info.connected_at,
                    "connection_duration": current_time - info.connected_at,
                    "last_heartbeat": info.last_heartbeat,
                    "ip_address": info.ip_address
                }
                for client_id, info in self.clients.items()
            }
        }
    
    def get_client_count(self, client_type: Optional[str] = None) -> int:
        """Get count of connected clients, optionally filtered by type."""
        if client_type:
            return len([c for c in self.clients.values() if c.client_type == client_type])
        return len(self.clients)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


async def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance."""
    if not websocket_manager._running:
        await websocket_manager.start()
    return websocket_manager
