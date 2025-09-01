#!/usr/bin/env python3
"""
Debug middleware for enhanced OpenWebUI integration debugging
Provides detailed request/response logging and analysis
"""

import time
import json
import logging
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
import asyncio

logger = logging.getLogger(__name__)

class DebugMiddleware:
    """Enhanced debugging middleware for OpenWebUI integration"""
    
    def __init__(self, app):
        self.app = app
        self.request_count = 0
        self.openwebui_requests = []
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Create request object
        request = Request(scope, receive)
        
        # Increment request counter
        self.request_count += 1
        request_id = self.request_count
        
        # Extract request details
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        url = str(request.url)
        
        # Check if this is an OpenWebUI request
        is_openwebui = self._is_openwebui_request(user_agent, url)
        
        # Log request start
        if is_openwebui:
            logger.info(f"🔧 [REQ-{request_id}] OpenWebUI Request START")
            logger.info(f"   📍 URL: {method} {url}")
            logger.info(f"   🌐 Client: {client_ip}")
            logger.info(f"   🤖 User-Agent: {user_agent}")
        else:
            logger.debug(f"📝 [REQ-{request_id}] Request START: {method} {url}")
        
        # Log headers for OpenWebUI requests
        if is_openwebui:
            logger.debug(f"   📋 Headers:")
            for name, value in request.headers.items():
                if name.lower() not in ['authorization', 'cookie']:  # Skip sensitive headers
                    logger.debug(f"      {name}: {value}")
        
        # Capture request body for POST requests
        request_body = None
        if method == "POST" and is_openwebui:
            try:
                body = await request.body()
                if body:
                    request_body = json.loads(body.decode())
                    logger.debug(f"   📦 Body: {json.dumps(request_body, indent=2)}")
            except Exception as e:
                logger.debug(f"   ⚠️ Could not parse request body: {e}")
        
        # Create a new receive function that replays the body
        async def receive_wrapper():
            if request_body is not None:
                return {
                    "type": "http.request",
                    "body": json.dumps(request_body).encode(),
                    "more_body": False
                }
            else:
                return await receive()
        
        # Response capture
        response_body = b""
        response_status = 200
        response_headers = {}
        
        async def send_wrapper(message):
            nonlocal response_body, response_status, response_headers
            
            if message["type"] == "http.response.start":
                response_status = message["status"]
                response_headers = dict(message.get("headers", []))
                
                if is_openwebui:
                    logger.debug(f"   📤 Response Status: {response_status}")
                    logger.debug(f"   📋 Response Headers:")
                    for name, value in response_headers.items():
                        if isinstance(name, bytes):
                            name = name.decode()
                        if isinstance(value, bytes):
                            value = value.decode()
                        logger.debug(f"      {name}: {value}")
            
            elif message["type"] == "http.response.body":
                body_chunk = message.get("body", b"")
                response_body += body_chunk
                
                if is_openwebui and body_chunk:
                    logger.debug(f"   📦 Response chunk: {len(body_chunk)} bytes")
            
            await send(message)
        
        # Process request
        try:
            await self.app(scope, receive_wrapper, send_wrapper)
            
            # Log completion
            duration = time.time() - start_time
            
            if is_openwebui:
                logger.info(f"🔧 [REQ-{request_id}] OpenWebUI Request COMPLETE")
                logger.info(f"   ⏱️ Duration: {duration:.3f}s")
                logger.info(f"   📊 Status: {response_status}")
                logger.info(f"   📏 Response Size: {len(response_body)} bytes")
                
                # Store OpenWebUI request for analysis
                self.openwebui_requests.append({
                    "request_id": request_id,
                    "timestamp": start_time,
                    "duration": duration,
                    "method": method,
                    "url": url,
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "request_body": request_body,
                    "response_status": response_status,
                    "response_size": len(response_body),
                    "response_headers": response_headers
                })
                
                # Keep only last 50 OpenWebUI requests
                if len(self.openwebui_requests) > 50:
                    self.openwebui_requests = self.openwebui_requests[-50:]
                
                # Check for potential issues
                self._analyze_openwebui_request(request_id, response_status, len(response_body), duration)
            else:
                logger.debug(f"📝 [REQ-{request_id}] Request COMPLETE: {response_status} in {duration:.3f}s")
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ [REQ-{request_id}] Request FAILED: {e}")
            logger.error(f"   ⏱️ Duration: {duration:.3f}s")
            raise
    
    def _is_openwebui_request(self, user_agent: str, url: str) -> bool:
        """Detect if this is an OpenWebUI request"""
        user_agent_lower = user_agent.lower()
        
        # Check for OpenWebUI user agents
        openwebui_indicators = [
            'openwebui',
            'open-webui',
            'open_webui',
            'webui'
        ]
        
        for indicator in openwebui_indicators:
            if indicator in user_agent_lower:
                return True
        
        # Check for mobile browsers that might be OpenWebUI
        mobile_indicators = [
            'mobile',
            'iphone',
            'android',
            'ipad'
        ]
        
        # If it's a mobile browser accessing TTS endpoints, likely OpenWebUI
        if any(indicator in user_agent_lower for indicator in mobile_indicators):
            if '/audio/' in url:
                return True
        
        return False
    
    def _analyze_openwebui_request(self, request_id: int, status: int, response_size: int, duration: float):
        """Analyze OpenWebUI request for potential issues"""
        issues = []
        
        # Check for errors
        if status >= 400:
            issues.append(f"HTTP error status: {status}")
        
        # Check for suspiciously small responses (might indicate truncation)
        if status == 200 and response_size < 1000:
            issues.append(f"Small response size: {response_size} bytes (possible truncation)")
        
        # Check for slow responses
        if duration > 5.0:
            issues.append(f"Slow response: {duration:.3f}s")
        
        # Check for very fast responses (might indicate cached/error)
        if duration < 0.1 and response_size > 10000:
            issues.append(f"Suspiciously fast large response: {duration:.3f}s for {response_size} bytes")
        
        if issues:
            logger.warning(f"🚨 [REQ-{request_id}] OpenWebUI Request Issues:")
            for issue in issues:
                logger.warning(f"   ⚠️ {issue}")
        else:
            logger.info(f"✅ [REQ-{request_id}] OpenWebUI Request looks healthy")
    
    def get_openwebui_stats(self) -> Dict[str, Any]:
        """Get statistics about OpenWebUI requests"""
        if not self.openwebui_requests:
            return {"message": "No OpenWebUI requests recorded"}
        
        total_requests = len(self.openwebui_requests)
        successful_requests = sum(1 for req in self.openwebui_requests if req["response_status"] < 400)
        failed_requests = total_requests - successful_requests
        
        durations = [req["duration"] for req in self.openwebui_requests]
        avg_duration = sum(durations) / len(durations)
        
        response_sizes = [req["response_size"] for req in self.openwebui_requests if req["response_status"] < 400]
        avg_response_size = sum(response_sizes) / len(response_sizes) if response_sizes else 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": f"{(successful_requests/total_requests)*100:.1f}%",
            "average_duration": f"{avg_duration:.3f}s",
            "average_response_size": f"{avg_response_size:.0f} bytes",
            "recent_requests": self.openwebui_requests[-5:]  # Last 5 requests
        }

# Global debug middleware instance
_debug_middleware = None

def get_debug_middleware():
    """Get global debug middleware instance"""
    global _debug_middleware
    return _debug_middleware

def set_debug_middleware(middleware):
    """Set global debug middleware instance"""
    global _debug_middleware
    _debug_middleware = middleware
