#!/usr/bin/env python3
"""
Production startup script for Kokoro ONNX TTS API
Optimized for VPS deployment with OpenWebUI integration
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the Kokoro ONNX TTS API server optimized for production"""
    parser = argparse.ArgumentParser(
        description="Start Kokoro ONNX TTS API server (Production Mode)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start on default port (8080) with auto-discovery
  python LiteTTS/scripts/start_production.py

  # Start on specific port for OpenWebUI
  python LiteTTS/scripts/start_production.py --port 9001

  # Start with custom host and port
  python LiteTTS/scripts/start_production.py --host 0.0.0.0 --port 8000
        """
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind to (default: from config.json)"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level (default: info)"
    )

    parser.add_argument(
        "--no-auto-port",
        action="store_true",
        help="Don't automatically find available port, use exact port specified"
    )

    args = parser.parse_args()

    try:
        # Set AGGRESSIVE performance environment variables for maximum CPU utilization
        try:
            from LiteTTS.performance.cpu_optimizer import get_cpu_optimizer
            cpu_optimizer = get_cpu_optimizer()

            # Check thermal status for aggressive optimization safety
            thermal_status = cpu_optimizer.get_thermal_status()
            enable_aggressive = thermal_status["safe_for_aggressive"]

            # Apply aggressive CPU optimizations
            env_vars = cpu_optimizer.optimize_environment_variables(aggressive=enable_aggressive)
            for key, value in env_vars.items():
                os.environ.setdefault(key, value)

            # Set CPU affinity for hybrid architecture if available
            if cpu_optimizer.cpu_info.has_hybrid_architecture and enable_aggressive:
                cpu_optimizer.set_hybrid_cpu_affinity(enable_aggressive=True)

            mode = "AGGRESSIVE" if enable_aggressive else "CONSERVATIVE"
            temp = thermal_status.get("temperature", 0)
            logger.info(f"Applied {mode} CPU optimization mode (temp: {temp:.1f}°C)")
            logger.info(f"Environment variables: {list(env_vars.keys())}")

            # Log detailed CPU information
            cpu_info = cpu_optimizer.cpu_info
            logger.info(f"Detected CPU: {cpu_info.model_name}")
            logger.info(f"CPU cores: {cpu_info.physical_cores} physical, {cpu_info.logical_cores} logical")
            logger.info(f"Hybrid architecture: {cpu_info.has_hybrid_architecture}")
            if cpu_info.has_hybrid_architecture:
                logger.info(f"P-cores: {cpu_info.performance_cores}, E-cores: {cpu_info.efficiency_cores}")
            logger.info(f"Hyperthreading: {'enabled' if cpu_info.has_hyperthreading else 'disabled'}")
            logger.info(f"AVX support: AVX2={cpu_info.supports_avx2}, AVX512={cpu_info.supports_avx512}")
            logger.info(f"NUMA nodes: {cpu_info.numa_nodes}")

            # Apply system-level optimizations
            try:
                from LiteTTS.performance.system_optimizer import get_system_optimizer
                system_optimizer = get_system_optimizer()

                system_results = system_optimizer.apply_all_optimizations()

                # Log SIMD capabilities
                simd_info = system_results.get("simd", {})
                optimization_level = simd_info.get("optimization_level", "unknown")
                logger.info(f"SIMD optimization level: {optimization_level}")

                avx_support = simd_info.get("avx_family", {})
                logger.info(f"AVX capabilities: AVX={avx_support.get('avx', False)}, "
                           f"AVX2={avx_support.get('avx2', False)}, "
                           f"AVX512={avx_support.get('avx512f', False)}")

                # Log memory optimizations
                memory_result = system_results.get("memory", {})
                if memory_result.get("status") == "applied":
                    logger.info("Applied aggressive memory optimizations")

                # Log batching setup
                if system_results.get("batching"):
                    logger.info("Request batching system enabled")

            except ImportError:
                logger.warning("System optimizer not available")

        except ImportError:
            # Fallback to manual optimization
            cpu_count = os.cpu_count() or 4

            if cpu_count >= 16:
                omp_threads = min(12, cpu_count // 2)
            elif cpu_count >= 8:
                omp_threads = min(8, cpu_count)
            else:
                omp_threads = min(4, cpu_count)

            os.environ.setdefault("OMP_NUM_THREADS", str(omp_threads))
            os.environ.setdefault("OPENBLAS_NUM_THREADS", str(omp_threads))
            os.environ.setdefault("MKL_NUM_THREADS", str(omp_threads))
            os.environ.setdefault("NUMEXPR_NUM_THREADS", str(min(4, cpu_count // 4)))

            logger.info(f"Applied fallback CPU optimization with {omp_threads} threads")

        # Common environment variables
        os.environ.setdefault("ENVIRONMENT", "production")
        os.environ.setdefault("CACHE_ENABLED", "true")

        # Import the app and get configuration
        from app import tts_app, app

        logger.info("🚀 Starting Kokoro ONNX TTS API (Production Mode)")
        
        # Use command line args or config defaults
        host = args.host
        port = args.port or tts_app.config.server.port
        
        logger.info(f"📍 Target host: {host}")
        logger.info(f"📍 Target port: {port}")

        # Find available port unless disabled
        if not args.no_auto_port and args.port is None:
            available_port = tts_app.find_available_port(port)
            if available_port != port:
                logger.warning(f"Port {port} unavailable, using {available_port}")
                port = available_port
        else:
            logger.info(f"Using exact port {port} as specified")

        # Import and run uvicorn
        import uvicorn

        logger.info(f"🌐 Server starting at http://{host}:{port}")
        logger.info(f"📊 Dashboard: http://{host}:{port}/dashboard")
        logger.info(f"📚 API docs: http://{host}:{port}/docs")
        logger.info(f"🎤 TTS endpoint: http://{host}:{port}/v1/audio/speech")
        
        # OpenWebUI integration info
        if port != 8080:
            logger.info(f"🔗 OpenWebUI API Base URL: http://YOUR_VPS_IP:{port}/v1")

        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            workers=args.workers,
            reload=False,  # Never reload in production
            log_level=args.log_level,
            access_log=True,
            server_header=False,
            date_header=False,
            # Production optimizations
            loop="uvloop" if sys.platform != "win32" else "asyncio",
            http="httptools" if sys.platform != "win32" else "h11"
        )

    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()