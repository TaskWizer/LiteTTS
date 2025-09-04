#!/usr/bin/env python3
"""
Cross-platform server startup script for LiteTTS
Replaces start.sh with better error handling and cross-platform compatibility
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_and_run_hardware_optimization():
    """Check if hardware optimization is needed and run it"""
    from pathlib import Path

    override_path = Path("override.json")

    # Check if we need to run hardware optimization
    needs_optimization = True

    if override_path.exists():
        try:
            import json
            with open(override_path, 'r') as f:
                config = json.load(f)

            # Check if this is an auto-generated config
            if config.get("_generated_by") == "Kokoro Hardware Optimizer":
                needs_optimization = False
                logger.info("✅ Hardware optimization already completed")
            else:
                logger.info("ℹ️  Custom override.json detected, skipping auto-optimization")
                needs_optimization = False
        except Exception as e:
            logger.warning(f"⚠️  Could not read override.json: {e}")

    if needs_optimization:
        logger.info("🔧 No hardware optimization found, running automatic optimization...")
        try:
            from LiteTTS.hardware_optimizer import run_hardware_optimization
            success = run_hardware_optimization(force=False)
            if success:
                logger.info("✅ Hardware optimization completed successfully")
            else:
                logger.warning("⚠️  Hardware optimization failed, using default settings")
        except Exception as e:
            logger.warning(f"⚠️  Hardware optimization failed: {e}")
            logger.info("ℹ️  Continuing with default settings")

def main():
    """Start the Kokoro ONNX TTS API server with proper configuration"""
    parser = argparse.ArgumentParser(
        description="Start Kokoro ONNX TTS API server",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Host to bind to (overrides config)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind to (overrides config)"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level (default: info)"
    )

    args = parser.parse_args()

    try:
        # Run hardware optimization if needed
        check_and_run_hardware_optimization()

        # Import the app and get configuration
        from app import tts_app, app

        logger.info("🚀 Starting Kokoro ONNX TTS API...")

        # Log configuration status
        from pathlib import Path
        import json

        logger.info("📋 Configuration Status:")
        config_sources = []

        # Check settings config
        if Path("config/settings.json").exists():
            config_sources.append("config/settings.json")
            with open("config/settings.json", 'r') as f:
                base_config = json.load(f)
            logger.info(f"   📄 Base config: port={base_config.get('server', {}).get('port', 'unknown')}")
        else:
            logger.warning("config/settings.json not found - using defaults")

        # Check override config
        override_path = Path("override.json")
        if override_path.exists():
            try:
                with open(override_path, 'r') as f:
                    override_data = json.load(f)
                config_sources.append("override.json")
                if "server" in override_data and "port" in override_data["server"]:
                    logger.info(f"   🔧 Override config: port={override_data['server']['port']}")
            except Exception as e:
                logger.warning(f"   ⚠️  Error reading override.json: {e}")

        # Check environment variables
        env_overrides = []
        if os.getenv("PORT"):
            env_overrides.append(f"PORT={os.getenv('PORT')}")
        if os.getenv("API_HOST"):
            env_overrides.append(f"API_HOST={os.getenv('API_HOST')}")

        if env_overrides:
            config_sources.append("environment")
            logger.info(f"   🌍 Environment: {', '.join(env_overrides)}")

        logger.info(f"   📁 Sources: {' → '.join(config_sources)}")

        # Use command line args or config defaults
        host = args.host or tts_app.config.server.host
        port = args.port or tts_app.config.server.port

        logger.info(f"📍 Final configuration: host={host}, port={port}")

        # Show configuration precedence
        if args.port:
            logger.info(f"   🎯 Using command line port: {port}")
        elif os.getenv("PORT"):
            logger.info(f"   🎯 Using environment PORT: {port}")
        elif override_path.exists():
            logger.info(f"   🎯 Using override.json port: {port}")
        else:
            logger.info(f"   🎯 Using config/settings.json port: {port}")

        # Find available port if not explicitly specified
        if args.port is None:
            available_port = tts_app.find_available_port(port)
            if available_port != port:
                logger.warning(f"Port {port} unavailable, using {available_port}")
                port = available_port
        else:
            # Use exact port if specified via command line
            logger.info(f"Using exact port {port} as specified")

        # Set environment variables for performance
        os.environ.setdefault("OMP_NUM_THREADS", "4")
        os.environ.setdefault("ONNX_DISABLE_SPARSE_TENSORS", "1")

        # Import and run uvicorn
        import uvicorn

        logger.info(f"🌐 Server starting at http://{host}:{port}")
        logger.info(f"📊 Dashboard available at http://{host}:{port}/dashboard")
        logger.info(f"📚 API docs available at http://{host}:{port}/docs")

        uvicorn.run(
            "app:app",  # Use string import to avoid import issues
            host=host,
            port=port,
            workers=args.workers,
            reload=args.reload,
            log_level=args.log_level,
            access_log=not args.reload,  # Disable access log in dev mode
            server_header=False,  # Disable server header for security
            date_header=False  # Disable date header for performance
        )

    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
