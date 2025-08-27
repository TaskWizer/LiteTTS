#!/usr/bin/env python3
"""
Standalone startup validation script for Kokoro ONNX TTS API
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path so we can import LiteTTS
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from LiteTTS.startup import initialize_system

async def main():
    """Main startup function"""
    try:
        await initialize_system()
        print("✅ Kokoro ONNX TTS API is ready to start!")
        return 0
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)