#!/usr/bin/env python3
"""
Start the Kokoro ONNX TTS API server
"""

import uvicorn
import sys
import os

def main():
    print("🎤 Starting Kokoro ONNX TTS API Server...")
    print("📍 Server will be available at: http://localhost:8080")
    print("📚 API docs will be at: http://localhost:8080/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)

    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8080,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()