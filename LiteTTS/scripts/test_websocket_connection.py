#!/usr/bin/env python3
"""
WebSocket Connection Test Script

Tests the WebSocket endpoint connectivity for the LiteTTS dashboard
to validate real-time communication functionality.
"""

import asyncio
import json
import time
import argparse
from typing import Optional
import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI

async def test_websocket_connection(endpoint: str, duration: int = 10) -> bool:
    """
    Test WebSocket connection to the specified endpoint.
    
    Args:
        endpoint: WebSocket endpoint URL
        duration: Test duration in seconds
        
    Returns:
        True if connection test passes, False otherwise
    """
    
    print(f"🔌 Testing WebSocket Connection")
    print(f"   Endpoint: {endpoint}")
    print(f"   Duration: {duration}s")
    print("=" * 40)
    
    try:
        # Connect to WebSocket
        print("Attempting to connect...")
        
        async with websockets.connect(endpoint) as websocket:
            print("✅ WebSocket connection established")
            
            # Test ping/pong
            print("Testing ping/pong...")
            pong_waiter = await websocket.ping()
            await asyncio.wait_for(pong_waiter, timeout=5.0)
            print("✅ Ping/pong successful")
            
            # Send test message
            print("Sending test message...")
            test_message = {
                "type": "request_full_data",
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(test_message))
            print("✅ Test message sent")
            
            # Listen for responses
            messages_received = 0
            start_time = time.time()
            
            print(f"Listening for messages for {duration}s...")
            
            while time.time() - start_time < duration:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    messages_received += 1
                    
                    # Parse and display message info
                    try:
                        data = json.loads(message)
                        msg_type = data.get("type", "unknown")
                        print(f"📨 Received message {messages_received}: type={msg_type}")
                    except json.JSONDecodeError:
                        print(f"📨 Received non-JSON message {messages_received}: {len(message)} bytes")
                        
                except asyncio.TimeoutError:
                    # No message received in timeout period, continue
                    continue
                except ConnectionClosed:
                    print("❌ Connection closed by server")
                    return False
            
            print(f"\n📊 Test Results:")
            print(f"   Connection duration: {duration}s")
            print(f"   Messages received: {messages_received}")
            print(f"   Connection stable: ✅ YES")
            
            return True
            
    except InvalidURI:
        print(f"❌ Invalid WebSocket URI: {endpoint}")
        return False
    except ConnectionRefusedError:
        print(f"❌ Connection refused - server not running or endpoint unavailable")
        return False
    except asyncio.TimeoutError:
        print(f"❌ Connection timeout - server took too long to respond")
        return False
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

async def test_concurrent_connections(endpoint: str, num_connections: int = 5) -> bool:
    """
    Test multiple concurrent WebSocket connections.
    
    Args:
        endpoint: WebSocket endpoint URL
        num_connections: Number of concurrent connections to test
        
    Returns:
        True if concurrent connection test passes, False otherwise
    """
    
    print(f"\n🔗 Testing Concurrent Connections")
    print(f"   Endpoint: {endpoint}")
    print(f"   Connections: {num_connections}")
    print("=" * 40)
    
    async def single_connection_test(connection_id: int):
        """Test a single connection"""
        try:
            async with websockets.connect(endpoint) as websocket:
                # Send ping
                pong_waiter = await websocket.ping()
                await asyncio.wait_for(pong_waiter, timeout=5.0)
                
                # Send test message
                test_message = {
                    "type": "request_full_data",
                    "connection_id": connection_id,
                    "timestamp": time.time()
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Wait for response
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                return True
                
        except Exception as e:
            print(f"❌ Connection {connection_id} failed: {e}")
            return False
    
    # Run concurrent connections
    tasks = [single_connection_test(i) for i in range(num_connections)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Count successful connections
    successful = sum(1 for result in results if result is True)
    
    print(f"📊 Concurrent Connection Results:")
    print(f"   Total connections: {num_connections}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {num_connections - successful}")
    print(f"   Success rate: {successful/num_connections:.1%}")
    
    return successful >= num_connections * 0.8  # 80% success rate

async def main():
    """Main test execution"""
    
    parser = argparse.ArgumentParser(description="Test WebSocket connection functionality")
    parser.add_argument("--endpoint", default="ws://localhost:8357/ws/dashboard", 
                       help="WebSocket endpoint to test")
    parser.add_argument("--duration", type=int, default=10,
                       help="Connection test duration in seconds")
    parser.add_argument("--concurrent", type=int, default=5,
                       help="Number of concurrent connections to test")
    
    args = parser.parse_args()
    
    print("🧪 WebSocket Connection Test Suite")
    print("=" * 50)
    print(f"Testing WebSocket endpoint: {args.endpoint}")
    print()
    
    # Test basic connection
    basic_test = await test_websocket_connection(args.endpoint, args.duration)
    
    # Test concurrent connections if basic test passes
    concurrent_test = False
    if basic_test:
        concurrent_test = await test_concurrent_connections(args.endpoint, args.concurrent)
    else:
        print("\n⚠️ Skipping concurrent connection test due to basic connection failure")
    
    # Overall results
    print(f"\n" + "=" * 50)
    print(f"📊 WEBSOCKET TEST RESULTS:")
    print(f"   Basic Connection: {'✅ PASS' if basic_test else '❌ FAIL'}")
    print(f"   Concurrent Connections: {'✅ PASS' if concurrent_test else '❌ FAIL'}")
    
    overall_success = basic_test and concurrent_test
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 WebSocket infrastructure is working correctly!")
        print("✅ Connection establishes successfully")
        print("✅ Ping/pong responses working")
        print("✅ Message sending/receiving functional")
        print("✅ Concurrent connections supported")
    else:
        print("\n⚠️ WebSocket infrastructure needs attention")
        if not basic_test:
            print("❌ Basic connection failed - check server status")
        if not concurrent_test:
            print("❌ Concurrent connections failed - check connection limits")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
