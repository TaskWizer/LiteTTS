import os
import io
import time
import socket
import asyncio
import numpy as np
import soundfile as sf
from pathlib import Path
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import StreamingResponse, Response
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import Optional, List, Any, Union

# Import our modules
from LiteTTS.downloader import ensure_model_files
from LiteTTS.config import config
from LiteTTS.exceptions import ModelError
from LiteTTS.logging_config import setup_logging
from LiteTTS.cache import cache_manager
from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
# Import advanced text processing directly
try:
    from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode
    ADVANCED_TEXT_PROCESSING_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Advanced text processing not available: {e}")
    ADVANCED_TEXT_PROCESSING_AVAILABLE = False
    UnifiedTextProcessor = None
    ProcessingOptions = None
    ProcessingMode = None

# Import dynamic CPU allocation
try:
    from LiteTTS.performance.dynamic_allocator import initialize_dynamic_allocation, DynamicAllocationConfig
    from LiteTTS.performance.cpu_monitor import CPUThresholds
    DYNAMIC_CPU_ALLOCATION_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Dynamic CPU allocation not available: {e}")
    DYNAMIC_CPU_ALLOCATION_AVAILABLE = False
    initialize_dynamic_allocation = None
    DynamicAllocationConfig = None
    CPUThresholds = None


class TTSRequest(BaseModel):
    """Request model for TTS generation with OpenWebUI compatibility"""
    input: str
    voice: Optional[str] = None  # Will use config default if not specified
    response_format: Optional[Union[str, int, bool]] = None  # Accept any type for OpenWebUI compatibility
    speed: Optional[Union[float, str]] = None  # Accept string numbers for OpenWebUI compatibility
    model: Optional[str] = None  # OpenWebUI compatibility - ignored but accepted


class KokoroTTSApplication:
    """
    Main application class for Kokoro ONNX TTS API.
    Encapsulates all application state and provides clean architecture.
    """

    def __init__(self):
        """Initialize the application with configuration and logging."""
        # Set up logging
        setup_logging(level=config.logging.level, file_path=config.logging.file_path)
        self.logger = logging.getLogger(__name__)

        # Configuration - use new enhanced config
        self.config = config

        # Dynamic voice management
        from LiteTTS.voice import get_voice_manager, get_available_voices, resolve_voice_name
        self.voice_manager = get_voice_manager()
        self.get_available_voices = get_available_voices
        self.resolve_voice_name = resolve_voice_name

        # Model state
        self.model: Optional[Any] = None
        self.available_voices: List[str] = []

        # Performance monitoring and optimization
        from LiteTTS.performance import PerformanceMonitor
        from LiteTTS.cache.preloader import IntelligentPreloader

        self.performance_monitor = PerformanceMonitor(max_history=1000, enable_system_monitoring=True)
        self.preloader: Optional[IntelligentPreloader] = None

        # FastAPI app and routers
        self.app: Optional[FastAPI] = None
        self.v1_router: Optional[APIRouter] = None
        self.legacy_router: Optional[APIRouter] = None

    def find_available_port(self, start_port: Optional[int] = None, max_attempts: Optional[int] = None) -> int:
        """
        Find an available port starting from configured port.
        Uses configuration values instead of hardcoded defaults.
        """
        if start_port is None:
            start_port = self.config.server.port
        if max_attempts is None:
            max_attempts = self.config.server.max_port_attempts

        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.bind(('localhost', port))
                    self.logger.info(f"🔌 Found available port: {port}")
                    return port
            except OSError:
                self.logger.debug(f"Port {port} is in use, trying next...")
                continue

        # Fallback to original port if all attempts fail
        self.logger.warning(f"Could not find available port in range {start_port}-{start_port + max_attempts - 1}, using {start_port}")
        return start_port
    
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Modern FastAPI lifespan event handler"""
        # Startup
        self.logger.info("Starting Kokoro ONNX TTS API...")

        # Start performance monitoring
        self.performance_monitor.start_monitoring()
        self.logger.info("📊 Performance monitoring started")

        # Initialize and start preloader
        if self.model:
            from LiteTTS.cache.preloader import IntelligentPreloader, CacheWarmingConfig
            preloader_config = CacheWarmingConfig(
                primary_voices=["af_heart", "am_puck"],
                warm_on_startup=False,  # DISABLED: Stop all cache warming for performance
                warm_during_idle=False,  # DISABLED: No idle warming
                idle_threshold_seconds=30.0
            )
            self.preloader = IntelligentPreloader(self, preloader_config)
            self.preloader.start()
            self.logger.info("🚀 Intelligent preloader started")

        # Initialize configuration hot reload
        self.config_hot_reload_manager = None
        try:
            from LiteTTS.performance.config_hot_reload import initialize_config_hot_reload

            # Enable hot reload if configured
            hot_reload_enabled = getattr(self.config.performance, 'hot_reload', True)

            if hot_reload_enabled:
                self.config_hot_reload_manager = initialize_config_hot_reload(
                    config_files=['config.json', 'override.json'],
                    enabled=True
                )
                self.logger.info("🔄 Configuration hot reload enabled")
            else:
                self.logger.info("🔄 Configuration hot reload disabled by configuration")

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to initialize configuration hot reload: {e}")
            self.config_hot_reload_manager = None

        yield

        # Shutdown
        # Stop configuration hot reload
        if self.config_hot_reload_manager:
            self.config_hot_reload_manager.stop()
            self.logger.info("🔄 Configuration hot reload stopped")

        # Stop preloader
        if self.preloader:
            self.preloader.stop()
            self.logger.info("🛑 Preloader stopped")

        # Stop performance monitoring
        self.performance_monitor.stop_monitoring()
        self.logger.info("📊 Performance monitoring stopped")

        # Cleanup model
        if hasattr(self.model, "cleanup"):
            self.model.cleanup()
        self.logger.info("🔄 Service shutdown complete")

    def create_app(self) -> FastAPI:
        """Factory method to create and configure the FastAPI application."""
        self.app = FastAPI(
            title=self.config.application.name,
            description=self.config.application.description,
            version=self.config.application.version,
            lifespan=self.lifespan,
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        self.setup_middleware()
        self.setup_routers()
        self.setup_endpoints()
        self.initialize_model()
        
        # Include routers AFTER endpoints are defined
        self._include_routers()
        
        return self.app
    
    def setup_middleware(self):
        """Configure CORS and other middleware."""
        cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )

        # Mount static files for dashboard and assets
        from fastapi.staticfiles import StaticFiles
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

        # Import dashboard analytics (avoid circular imports)
        import sys
        import importlib.util
        spec = importlib.util.spec_from_file_location("dashboard", "LiteTTS/api/dashboard.py")
        dashboard_module = importlib.util.module_from_spec(spec)
        sys.modules["dashboard"] = dashboard_module
        spec.loader.exec_module(dashboard_module)
        dashboard_analytics = dashboard_module.dashboard_analytics

        # Add enhanced request logging middleware with analytics
        @self.app.middleware("http")
        async def log_requests(request, call_next):
            start_time = time.time()

            # Log incoming request with enhanced details for debugging (skip dashboard polling)
            client_ip = request.client.host if request.client else 'unknown'
            user_agent = request.headers.get('user-agent', 'unknown')

            # Reduce logging for dashboard endpoints to avoid spam
            if not request.url.path.startswith('/dashboard'):
                self.logger.info(f"📥 {request.method} {request.url.path} - Client: {client_ip}")
            elif request.url.path == '/dashboard' and request.method == 'GET':
                # Only log initial dashboard access, not data polling
                self.logger.debug(f"📊 Dashboard access from {client_ip}")
            else:
                # Dashboard data/ws requests - use debug level
                self.logger.debug(f"📊 {request.method} {request.url.path} - Client: {client_ip}")

            # Extract TTS-specific information for analytics
            voice = None
            text_length = None
            cache_hit = False

            if request.url.path == "/v1/audio/speech" and request.method == "POST":
                try:
                    # Read request body to extract TTS information
                    body = await request.body()
                    if body:
                        import json
                        request_data = json.loads(body.decode())
                        voice = request_data.get('voice')
                        input_text = request_data.get('input', '')
                        text_length = len(input_text) if input_text else None

                        # Recreate request with body for downstream processing
                        from starlette.requests import Request
                        request._body = body
                except Exception as e:
                    self.logger.debug(f"Could not extract TTS info from request: {e}")

            # Log headers for debugging external client issues
            if request.url.path.startswith(self.config.endpoints.tts):
                self.logger.info(f"🔍 Content-Type: {request.headers.get('content-type', 'not set')}")
                self.logger.info(f"🔍 User-Agent: {user_agent}")
                self.logger.info(f"🔍 Origin: {request.headers.get('origin', 'not set')}")

            try:
                # Process request
                response = await call_next(request)

                # Log response (reduce verbosity for dashboard endpoints)
                process_time = time.time() - start_time
                if not request.url.path.startswith('/dashboard'):
                    self.logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
                else:
                    self.logger.debug(f"📊 {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")

                # Record analytics (skip dashboard endpoints to avoid recursion)
                if not request.url.path.startswith('/dashboard'):
                    dashboard_analytics.record_request(
                        method=request.method,
                        path=request.url.path,
                        status_code=response.status_code,
                        response_time=process_time,
                        client_ip=client_ip,
                        user_agent=user_agent,
                        voice=voice,
                        text_length=text_length,
                        cache_hit=cache_hit
                    )

                return response
            except Exception as e:
                process_time = time.time() - start_time
                self.logger.error(f"❌ Request failed in {process_time:.3f}s: {e}")

                # Record error in analytics
                if not request.url.path.startswith('/dashboard'):
                    dashboard_analytics.record_request(
                        method=request.method,
                        path=request.url.path,
                        status_code=500,
                        response_time=process_time,
                        client_ip=client_ip,
                        user_agent=user_agent,
                        voice=voice,
                        text_length=text_length,
                        cache_hit=cache_hit
                    )

                raise
    
    def setup_routers(self):
        """Create and configure API routers."""
        self.v1_router = APIRouter(prefix="/v1", tags=["v1"])
        self.legacy_router = APIRouter(tags=["legacy"])

    def _include_routers(self):
        """Include routers in the main app with organized grouping."""

        # ============================================
        # Production API Endpoints
        # ============================================
        self.app.include_router(self.v1_router)

        # ============================================
        # Legacy Compatibility Endpoints
        # ============================================
        self.app.include_router(self.legacy_router)

        # Note: Utility/Debug endpoints are defined directly on main app
        # and don't require separate router inclusion
    
    def initialize_model(self):
        """Initialize the TTS model and download required files if needed"""
        try:
            # Ensure model files are downloaded
            self.logger.info("🔄 Checking for model files...")
            if not ensure_model_files():
                raise RuntimeError("Failed to download required model files")

            # Auto-download voices on first startup
            self._ensure_voices_downloaded()

            self.logger.info("📦 Model files ready, importing kokoro_onnx...")

            # Import kokoro_onnx here to avoid import errors if not installed
            try:
                from kokoro_onnx import Kokoro
                self.logger.info("✅ kokoro_onnx imported successfully")
            except ImportError as e:
                self.logger.error(f"❌ Failed to import kokoro_onnx: {e}")
                raise ModelError(f"kokoro_onnx not available: {e}")

            # Check kokoro_onnx version
            try:
                import kokoro_onnx
                self.logger.info(f"📦 kokoro_onnx version: {getattr(kokoro_onnx, '__version__', 'unknown')}")
            except:
                pass

            # Apply patches to fix tensor rank issues
            self.logger.info("🔧 Applying kokoro_onnx patches...")
            try:
                from LiteTTS.patches import apply_all_patches
                if apply_all_patches():
                    self.logger.info("✅ Patches applied successfully")
                else:
                    self.logger.warning("⚠️ Some patches failed - proceeding anyway")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to apply patches: {e} - proceeding anyway")

            # Voice loading strategy based on configuration
            if self.config.voice.use_combined_file:
                # Use combined voices file (legacy approach)
                from LiteTTS.voice.simple_combiner import SimplifiedVoiceCombiner
                self.voice_combiner = SimplifiedVoiceCombiner(self.config.tts.voices_path)
                voices_file = self.voice_combiner.ensure_combined_file()
                self.logger.info(f"🚀 Using combined voices file: {voices_file}")
            else:
                # Use individual voice loading strategy (recommended)
                from LiteTTS.voice.manager import VoiceManager
                self.voice_manager = VoiceManager(self.config.tts.voices_path, config=self.config)

                # Optimize for individual loading
                self.voice_manager.optimize_for_individual_loading()

                # Create a temporary combined file for Kokoro model compatibility
                # This is a bridge solution until Kokoro supports individual loading natively
                # Suppress deprecation warning since we're using it as a compatibility bridge
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=DeprecationWarning)
                    warnings.filterwarnings("ignore", message="SimplifiedVoiceCombiner is deprecated*")
                    from LiteTTS.voice.simple_combiner import SimplifiedVoiceCombiner
                    self.voice_combiner = SimplifiedVoiceCombiner(self.config.tts.voices_path)
                    voices_file = self.voice_combiner.ensure_combined_file()

                self.logger.info(f"🚀 Using individual voice loading with compatibility bridge")
                self.logger.info(f"   Voice manager: Individual loading strategy")
                self.logger.info(f"   Compatibility file: {voices_file}")

            self.logger.info(f"🚀 Initializing Kokoro model: {self.config.tts.model_path} | Voices: {voices_file}")

            # Initialize the model with voices file
            self.model = Kokoro(self.config.tts.model_path, voices_file)

            self.logger.info("✅ Model loaded successfully")

            # Initialize advanced text processing
            if ADVANCED_TEXT_PROCESSING_AVAILABLE:
                try:
                    self.unified_processor = UnifiedTextProcessor()
                    self.processing_options = ProcessingOptions(
                        mode=ProcessingMode.ENHANCED,
                        use_advanced_currency=True,
                        use_ticker_symbol_processing=False,  # DISABLE to prevent letter-by-letter spelling
                        use_advanced_symbols=False,  # DISABLE to prevent IPA symbols and stress markers
                        use_enhanced_datetime=True,
                        normalize_text=False,  # DISABLE RIME AI processing that adds IPA symbols
                        resolve_homographs=False,  # DISABLE homograph resolution that adds stress markers
                        process_phonetics=False,  # DISABLE phonetic processing to prevent IPA symbols
                        use_espeak_enhanced_symbols=False,  # DISABLE to prevent "?" → "question mark" conversion
                        use_interjection_fixes=False  # DISABLE to prevent "hmm" → "hmmm" conversion
                    )
                    self.logger.info("✅ Advanced text processing (UnifiedTextProcessor) initialized")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to initialize advanced text processing: {e}")
                    self.unified_processor = None
            else:
                self.logger.warning("⚠️ Advanced text processing not available - using basic preprocessing")
                self.unified_processor = None

            # Initialize dynamic CPU allocation
            if DYNAMIC_CPU_ALLOCATION_AVAILABLE:
                try:
                    # Get dynamic CPU allocation config from main config
                    cpu_config = self.config.performance.dynamic_cpu_allocation or {}

                    if cpu_config.get("enabled", True):
                        # Create allocation config
                        allocation_config = DynamicAllocationConfig(
                            enabled=cpu_config.get("enabled", True),
                            min_cores=cpu_config.get("min_cores", 1),
                            max_cores=cpu_config.get("max_cores"),
                            aggressive_mode=cpu_config.get("aggressive_mode", False),
                            thermal_protection=cpu_config.get("thermal_protection", True),
                            onnx_integration=cpu_config.get("onnx_integration", True),
                            update_environment=cpu_config.get("update_environment", True)
                        )

                        # Create monitor config
                        monitor_config = {
                            "min_threshold": cpu_config.get("min_threshold", 25.0),
                            "max_threshold": cpu_config.get("max_threshold", 80.0),
                            "monitoring_interval": cpu_config.get("monitoring_interval", 1.0),
                            "history_window": cpu_config.get("history_window", 10),
                            "allocation_cooldown": cpu_config.get("allocation_cooldown", 5.0)
                        }

                        # Initialize dynamic allocation
                        self.dynamic_allocator = initialize_dynamic_allocation(allocation_config, monitor_config)
                        self.logger.info("✅ Dynamic CPU allocation initialized")
                    else:
                        self.logger.info("⚠️ Dynamic CPU allocation disabled in configuration")
                        self.dynamic_allocator = None

                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to initialize dynamic CPU allocation: {e}")
                    self.dynamic_allocator = None
            else:
                self.logger.warning("⚠️ Dynamic CPU allocation not available")
                self.dynamic_allocator = None

            # Test the model with a simple generation
            self.logger.info("🧪 Testing model with simple text...")
            try:
                test_audio, test_sr = self.model.create("test", voice=self.config.voice.default_voice)
                self.logger.info(f"✅ Model test successful: {len(test_audio)} samples at {test_sr}Hz")
            except Exception as test_error:
                self.logger.error(f"❌ Model test failed: {test_error}")
                self.logger.error("� Model compatibility test failed - check model file and library version")
                import traceback
                self.logger.error(f"Full traceback: {traceback.format_exc()}")
                # Don't raise the error, just log it and continue
                self.logger.warning("🔧 Skipping model test - will attempt TTS generation on first request")

            # Get available voices from the voice combiner (more reliable)
            self.available_voices = self.voice_combiner.get_voice_list()
            self.logger.info(f"🎭 Available voices from combiner: {self.available_voices}")

            # Also try the dynamic system as fallback
            dynamic_voices = self.get_available_voices()
            self.logger.info(f"🔍 Dynamic system voices: {dynamic_voices}")

            # Use combiner voices if available, otherwise fallback to dynamic
            if not self.available_voices and dynamic_voices:
                self.available_voices = dynamic_voices
                self.logger.info("📋 Using dynamic voices as fallback")

            self.logger.info(f"🎭 Final available voices count: {len(self.available_voices)}")
            self.logger.info("🎉 Kokoro ONNX TTS API ready!")

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize model: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Failed to initialize model: {str(e)}")

    def _ensure_voices_downloaded(self):
        """Ensure voices are downloaded on first startup"""
        try:
            if not self.voice_manager:
                self.logger.warning("Voice manager not available, skipping auto-download")
                return

            # Check if this is first startup (no .bin voices downloaded)
            voices_dir = Path(self.config.paths.voices_dir)
            bin_voices = list(voices_dir.glob("*.bin"))
            total_discovered = len(self.voice_manager.downloader.discovered_voices)

            self.logger.info(f"📊 Voice status: {len(bin_voices)} .bin files, {total_discovered} voices discovered")

            # If less than 5 .bin voices exist, download ALL voices (simplified voice management)
            if len(bin_voices) < 5:
                self.logger.info("🚀 First startup detected - downloading ALL available voices...")

                # Download ALL voices (simplified voice management)
                all_voices = list(self.voice_manager.downloader.discovered_voices.keys())
                all_downloaded = 0
                all_converted = 0

                for voice_name in all_voices:
                    if voice_name in self.voice_manager.downloader.discovered_voices:
                        bin_path = voices_dir / f"{voice_name}.bin"

                        if not bin_path.exists():
                            self.logger.info(f"📥 Downloading: {voice_name}")
                            success = self.voice_manager.downloader.download_voice(voice_name)
                            if success:
                                all_downloaded += 1
                                if bin_path.exists():
                                    all_converted += 1
                                    self.logger.info(f"✅ Downloaded: {voice_name}")
                                else:
                                    self.logger.warning(f"⚠️ Downloaded but conversion failed: {voice_name}")
                            else:
                                self.logger.warning(f"❌ Failed to download: {voice_name}")
                        else:
                            all_converted += 1

                self.logger.info(f"🎊 Downloaded {all_downloaded}/{len(all_voices)} voices, {all_converted} .bin files available")

        except Exception as e:
            self.logger.error(f"❌ Failed to auto-download voices: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            # Don't fail startup if voice download fails
            pass
    
    def get_voice_name(self, voice_name: str) -> str:
        """Get the correct voice name for the API"""
        # Resolve voice name using dynamic system
        resolved_voice = self.resolve_voice_name(voice_name)

        if resolved_voice not in self.available_voices:
            raise HTTPException(400, detail=f"Voice '{voice_name}' not available. Available: {self.available_voices}")

        return resolved_voice
    
    def setup_endpoints(self):
        """Define all API endpoints."""
        self.setup_main_endpoints()
        self.setup_v1_endpoints()
        self.setup_legacy_endpoints()
        self.setup_utility_endpoints()
        self.setup_dashboard_endpoints()

    def setup_main_endpoints(self):
        """Setup main app endpoints (root, startup, shutdown)."""

        @self.app.get("/")
        async def root():
            """Enhanced API information and available endpoints"""
            # Get system information
            import time
            import psutil
            import platform

            # Calculate uptime
            uptime_seconds = time.time() - getattr(self, 'start_time', time.time())
            uptime_hours = int(uptime_seconds // 3600)
            uptime_days = int(uptime_hours // 24)

            # Get performance stats
            performance_summary = self.performance_monitor.get_performance_summary()

            return {
                "service": {
                    "name": self.config.application.name,
                    "version": self.config.application.version,
                    "description": "High-performance ONNX-based Text-to-Speech API with 54+ voices",
                    "status": "healthy",
                    "uptime": f"{uptime_days}d {uptime_hours % 24}h" if uptime_days > 0 else f"{uptime_hours}h"
                },
                "system_info": {
                    "platform": platform.system(),
                    "python_version": platform.python_version(),
                    "cpu_count": psutil.cpu_count(),
                    "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
                    "voices_available": len(self.available_voices)
                },
                "performance": {
                    "avg_rtf": round(performance_summary.get('summary', {}).get('avg_rtf', 0), 3),
                    "avg_latency_ms": round(performance_summary.get('summary', {}).get('avg_latency_ms', 0), 1),
                    "cache_hit_rate": f"{performance_summary.get('summary', {}).get('cache_hit_rate_percent', 0):.1f}%",
                    "total_requests": performance_summary.get('summary', {}).get('total_requests', 0)
                },
                "endpoints": {
                    "primary": {
                        "tts_openai_compatible": "/v1/audio/speech",
                        "tts_streaming": "/v1/audio/stream",
                        "voices_list": "/v1/voices",
                        "health_check": "/v1/health"
                    },
                    "management": {
                        "dashboard": "/dashboard",
                        "api_documentation": "/docs",
                        "api_docs_alias": "/api",
                        "metrics": "/metrics",
                        "cache_stats": "/cache/stats"
                    },
                    "legacy_compatibility": {
                        "tts": "/tts",
                        "voices": "/voices",
                        "health": "/health",
                        "note": "Legacy endpoints available without /v1 prefix"
                    }
                },
                "quick_links": {
                    "Try TTS": "/dashboard",
                    "API Docs": "/docs",
                    "Voice List": "/v1/voices",
                    "System Health": "/v1/health",
                    "Performance": "/metrics"
                },
                "usage_examples": {
                    "curl_basic": {
                        "description": "Basic TTS request with curl",
                        "command": 'curl -X POST "http://localhost:8000/v1/audio/speech" -H "Content-Type: application/json" -d \'{"input": "Hello world!", "voice": "af_heart"}\' --output hello.mp3'
                    },
                    "curl_streaming": {
                        "description": "Streaming TTS request",
                        "command": 'curl -X POST "http://localhost:8000/v1/audio/stream" -H "Content-Type: application/json" -d \'{"input": "Hello world!", "voice": "af_heart"}\' --output hello.mp3'
                    },
                    "python_requests": {
                        "description": "Python requests example",
                        "code": """import requests
response = requests.post(
    "http://localhost:8000/v1/audio/speech",
    json={"input": "Hello world!", "voice": "af_heart"}
)
with open("hello.mp3", "wb") as f:
    f.write(response.content)"""
                    },
                    "javascript_fetch": {
                        "description": "JavaScript fetch example",
                        "code": """fetch('http://localhost:8000/v1/audio/speech', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({input: 'Hello world!', voice: 'af_heart'})
}).then(response => response.blob())
  .then(blob => {
    const audio = new Audio(URL.createObjectURL(blob));
    audio.play();
  });"""
                    }
                },
                "features": [
                    "🎵 54+ high-quality voices",
                    "⚡ 0.15 RTF (6.7x faster than real-time)",
                    "🔄 Multiple audio formats (MP3, WAV, OGG, FLAC)",
                    "📡 Real-time streaming support",
                    "🎛️ Voice blending and speed control",
                    "🧠 Intelligent caching system",
                    "📊 Real-time performance monitoring",
                    "🔗 OpenAI API compatibility",
                    "🌐 OpenWebUI integration ready"
                ]
            }

        @self.app.get("/api")
        async def api_docs_alias():
            """Redirect to API documentation"""
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/docs", status_code=302)

        @self.app.get("/favicon.ico")
        async def favicon():
            """Serve favicon.ico"""
            from fastapi.responses import FileResponse
            favicon_path = Path("static/favicon.ico")
            if favicon_path.exists():
                return FileResponse(favicon_path, media_type="image/x-icon")
            else:
                raise HTTPException(status_code=404, detail="Favicon not found")


    async def _generate_speech_internal(self, request: TTSRequest):
        """Internal speech generation logic shared by all endpoints"""
        try:
            # Apply configuration defaults if not specified in request
            voice_name = request.voice or self.config.voice.default_voice
            response_format = request.response_format or self.config.audio.default_format
            speed = request.speed if request.speed is not None else 1.0  # Default speed to 1.0 if None

            # Validate model is loaded
            if self.model is None:
                raise HTTPException(500, detail="TTS model not loaded")

            # Get the correct voice name
            voice_name = self.get_voice_name(voice_name)

            # Notify preloader of request
            if self.preloader:
                self.preloader.on_request_received(request.input, voice_name)

            # Check cache first
            if cache_manager.is_enabled():
                cached_audio = cache_manager.audio_cache.get_audio(request.input, voice_name, speed, response_format)
                if cached_audio:
                    self.logger.info("🎯 Cache hit! Returning cached audio")

                    # Record cache hit performance
                    from LiteTTS.performance import TTSPerformanceData
                    perf_data = TTSPerformanceData(
                        text_length=len(request.input),
                        voice=voice_name,
                        audio_duration=0.0,  # We don't know duration for cached audio
                        generation_time=0.001,  # Minimal cache retrieval time
                        rtf=0.0,
                        cache_hit=True,
                        format=response_format,
                        speed=request.speed
                    )
                    self.performance_monitor.record_tts_performance(perf_data)

                    return StreamingResponse(
                        io.BytesIO(cached_audio),
                        media_type=f"audio/{response_format}",
                        headers={"Content-Disposition": f"attachment; filename=speech.{response_format}"}
                    )
            self.logger.info(f"🎵 Generating speech: '{request.input[:50]}...' with voice '{voice_name}'")

            # Enhanced text preprocessing to prevent phonemizer issues (CONSERVATIVE MODE)
            # Use conservative mode by default to preserve word count and avoid phonemizer mismatches
            preprocessing_result = phonemizer_preprocessor.preprocess_text(
                request.input,
                aggressive=False,
                preserve_word_count=True
            )

            if preprocessing_result.warnings:
                for warning in preprocessing_result.warnings:
                    self.logger.warning(f"⚠️ Text preprocessing warning: {warning}")

            if preprocessing_result.confidence_score < 0.7:
                self.logger.warning(f"⚠️ Low confidence score ({preprocessing_result.confidence_score:.2f}) for phonemizer success")

            # Generate audio with enhanced retry mechanism for empty audio issue
            import re
            max_retries = config.performance.max_retry_attempts
            retry_delay = config.performance.retry_delay_seconds
            audio = None
            sample_rate = None
            generation_time = 0

            # Try different text preprocessing strategies if initial attempts fail
            # Start with conservative approaches to preserve word count, then get more aggressive
            text_variants = [
                preprocessing_result.processed_text,  # Conservative preprocessed text (preserve word count)
                request.input.strip() + '.',  # Minimal processing (original text)
                phonemizer_preprocessor.preprocess_text(request.input, aggressive=False, preserve_word_count=False).processed_text,  # Standard preprocessing
                phonemizer_preprocessor.preprocess_text(request.input, aggressive=True, preserve_word_count=False).processed_text  # Aggressive preprocessing
            ]

            for attempt in range(max_retries):
                try:
                    # Use different text variant for each retry
                    current_text = text_variants[min(attempt, len(text_variants) - 1)]

                    start_time = time.time()

                    # Apply advanced text processing if available
                    processed_text = current_text
                    if self.unified_processor:
                        try:
                            processing_result = self.unified_processor.process_text(current_text, self.processing_options)
                            processed_text = processing_result.processed_text

                            # Log processing details for debugging
                            if processing_result.changes_made:
                                self.logger.info(f"🔧 Advanced text processing applied: {', '.join(processing_result.changes_made[:3])}")
                            if processing_result.currency_enhancements > 0:
                                self.logger.debug(f"💰 Currency processing: {processing_result.currency_enhancements} enhancements")

                        except Exception as e:
                            self.logger.warning(f"⚠️ Advanced text processing failed, using original text: {e}")
                            processed_text = current_text

                    # Generate audio with processed text
                    audio, sample_rate = self.model.create(
                        processed_text,
                        voice=voice_name,
                        speed=speed,
                        lang=config.audio.default_language
                    )

                    generation_time = time.time() - start_time

                    self.logger.info(f"✅ Generated {len(audio)} samples in {generation_time:.2f}s (attempt {attempt + 1})")

                    # Check if audio generation was successful
                    if len(audio) > 0:
                        if attempt > 0:
                            self.logger.info(f"🔄 Success with text variant {attempt + 1}: '{current_text[:50]}...'")
                        break
                    else:
                        self.logger.warning(f"⚠️ Empty audio generated on attempt {attempt + 1} with text: '{current_text[:50]}...'")
                        if attempt < max_retries - 1:
                            # Brief pause before retry with different text variant
                            time.sleep(retry_delay)
                            continue

                except Exception as e:
                    self.logger.warning(f"⚠️ Audio generation failed on attempt {attempt + 1}: {e}")
                    self.logger.warning(f"📝 Failed text variant: '{text_variants[min(attempt, len(text_variants) - 1)][:50]}...'")
                    if attempt < max_retries - 1:
                        time.sleep(0.1)
                        continue
                    raise

            # Validate final audio data
            if audio is None or len(audio) == 0:
                self.logger.error(f"❌ Failed to generate audio after {max_retries} attempts")
                self.logger.error(f"📋 Input text: '{request.input}'")
                self.logger.error(f"📋 Processed text: '{preprocessing_result.processed_text}'")
                self.logger.error(f"📋 Voice: {voice_name}, Speed: {request.speed}")
                self.logger.error(f"📋 Preprocessing changes: {preprocessing_result.changes_made}")
                raise ValueError(f"Generated audio is empty after {max_retries} attempts")

            # Calculate audio duration and performance metrics
            audio_duration = len(audio) / sample_rate
            rtf = generation_time / audio_duration if audio_duration > 0 else 0
            self.logger.info(f"🎵 Audio duration: {audio_duration:.2f}s, RTF: {rtf:.2f}")

            if not np.isfinite(audio).all():
                raise ValueError("Generated audio contains invalid values (NaN or Inf)")

            # Convert to the requested format
            format_upper = response_format.upper()
            buffer = io.BytesIO()

            # Ensure audio is in the correct format for soundfile
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # Ensure audio is 1D
            if audio.ndim > 1:
                audio = audio.flatten()

            sf.write(buffer, audio, sample_rate, format=format_upper)
            buffer.seek(0)
            audio_data = buffer.read()

            # Cache the result
            if cache_manager.is_enabled():
                cache_manager.audio_cache.put_audio(request.input, voice_name, audio_data, speed, response_format)
                self.logger.info("💾 Audio cached for future requests")

            # Record performance metrics
            from LiteTTS.performance import TTSPerformanceData
            perf_data = TTSPerformanceData(
                text_length=len(request.input),
                voice=voice_name,
                audio_duration=audio_duration,
                generation_time=generation_time,
                rtf=rtf,
                cache_hit=False,
                format=response_format,
                speed=speed
            )
            self.performance_monitor.record_tts_performance(perf_data)

            # Log performance
            duration = len(audio) / sample_rate
            processing_time = generation_time
            self.logger.info(f"⚡ Performance: {duration:.2f}s audio in {processing_time:.2f}s (RTF: {processing_time/duration:.2f})")

            # Return proper Response with Content-Length for better OpenWebUI compatibility
            from fastapi import Response
            return Response(
                content=audio_data,
                media_type=f"audio/{response_format}",
                headers={
                    "Content-Disposition": f"attachment; filename=speech.{response_format}",
                    "Content-Length": str(len(audio_data)),
                    "Accept-Ranges": "bytes",
                    "Cache-Control": "no-cache",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "*"
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            raise HTTPException(500, detail=f"Generation failed: {str(e)}")

    def _preprocess_text_for_tts(self, text: str) -> str:
        """Preprocess text to prevent phonemizer issues"""
        import re
        import unicodedata

        # Normalize Unicode characters to prevent encoding issues
        text = unicodedata.normalize('NFKC', text)

        # Remove control characters that can cause issues
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)

        # Fix common problematic patterns that cause phonemizer word count mismatches

        # 1. Handle contractions properly (don't -> do not)
        contractions = {
            "don't": "do not", "won't": "will not", "can't": "cannot",
            "n't": " not", "'re": " are", "'ve": " have", "'ll": " will",
            "'d": " would", "'m": " am", "'s": " is"
        }
        for contraction, expansion in contractions.items():
            text = re.sub(r'\b\w*' + re.escape(contraction) + r'\b',
                         lambda m: m.group(0).replace(contraction, expansion), text, flags=re.IGNORECASE)

        # 2. Handle numbers and special characters that confuse phonemizer
        # Replace standalone numbers with words for better phonemization
        number_words = {
            '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
            '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
        }
        text = re.sub(r'\b(\d)\b', lambda m: number_words.get(m.group(1), m.group(1)), text)

        # 3. Remove excessive punctuation that can cause issues
        text = re.sub(r'([.!?]){4,}', r'\1\1\1', text)
        text = re.sub(r'([,;:]){3,}', r'\1', text)

        # 4. Normalize whitespace and remove excessive spacing
        text = re.sub(r'\s+', ' ', text)

        # 5. Handle very long words that might cause tokenization issues
        words = text.split()
        processed_words = []
        for word in words:
            # Remove non-alphabetic characters from very long words
            if len(word) > 25:
                # Keep only letters and basic punctuation
                clean_word = re.sub(r'[^a-zA-Z\s\-\']', '', word)
                if len(clean_word) > 20:
                    # Split very long words at natural boundaries
                    clean_word = re.sub(r'(.{15})', r'\1 ', clean_word).strip()
                processed_words.append(clean_word)
            else:
                processed_words.append(word)

        text = ' '.join(processed_words)

        # 6. Ensure proper sentence structure
        text = text.strip()
        if text and not text[-1] in '.!?':
            text += '.'

        # 7. Final cleanup - remove any double spaces
        text = re.sub(r'\s+', ' ', text)

        # 8. Log preprocessing if significant changes were made
        if len(text) != len(text.strip()) or '  ' in text:
            self.logger.debug(f"📝 Text preprocessed for phonemizer compatibility")

        return text.strip()

    async def _stream_speech_internal(self, request: TTSRequest):
        """Internal streaming speech generation logic"""
        try:
            # Validate model is loaded
            if self.model is None:
                raise HTTPException(500, detail="TTS model not loaded")

            # Apply configuration defaults if not specified in request
            voice_name = request.voice or self.config.voice.default_voice
            response_format = request.response_format or self.config.audio.default_format
            speed = request.speed if request.speed is not None else 1.0  # Default speed to 1.0 if None

            # Get the correct voice name
            voice_name = self.get_voice_name(voice_name)

            self.logger.info(f"🎵 Streaming speech: '{request.input[:100]}...' with voice '{voice_name}'")
            self.logger.info(f"🔧 Stream parameters: format={response_format}, speed={speed}")

            # Check if chunked generation should be used
            use_chunked = hasattr(self.model, 'should_use_chunked_generation') and self.model.should_use_chunked_generation(request.input, streaming=True)

            if use_chunked:
                self.logger.info("🧩 Using chunked generation for streaming")
                return await self._stream_chunked_audio(request, voice_name, response_format, speed)

            # For streaming, generate the complete audio and stream it in chunks
            # This ensures consistent audio quality and proper streaming behavior
            async def generate_audio_stream():
                try:
                    start_time = time.time()

                    # Generate complete audio first for better quality
                    self.logger.info(f"🎯 Generating complete audio for streaming...")
                    audio, sample_rate = self.model.create(
                        request.input,
                        voice=voice_name,
                        speed=speed,
                        lang="en-us"
                    )

                    generation_time = time.time() - start_time
                    self.logger.info(f"✅ Audio generated: {len(audio)} samples at {sample_rate}Hz in {generation_time:.2f}s")

                    # Convert to requested format
                    buffer = io.BytesIO()
                    sf.write(buffer, audio, sample_rate, format=response_format.upper())
                    buffer.seek(0)
                    audio_data = buffer.read()

                    self.logger.info(f"📦 Audio converted to {response_format}: {len(audio_data)} bytes")

                    # Stream the audio in chunks for better user experience
                    chunk_size = config.audio.chunk_size
                    total_chunks = (len(audio_data) + chunk_size - 1) // chunk_size

                    self.logger.info(f"🚀 Starting stream: {total_chunks} chunks of {chunk_size} bytes")

                    for i in range(0, len(audio_data), chunk_size):
                        chunk = audio_data[i:i + chunk_size]
                        chunk_num = (i // chunk_size) + 1

                        self.logger.debug(f"📦 Streaming chunk {chunk_num}/{total_chunks}: {len(chunk)} bytes")

                        yield chunk

                        # Small delay to allow proper streaming
                        await asyncio.sleep(0.005)

                    total_time = time.time() - start_time
                    self.logger.info(f"✅ Streaming complete: {total_chunks} chunks in {total_time:.2f}s")

                except Exception as stream_error:
                    self.logger.error(f"❌ Streaming error: {stream_error}")
                    import traceback
                    self.logger.error(f"Full traceback: {traceback.format_exc()}")
                    raise

            return StreamingResponse(
                generate_audio_stream(),
                media_type=f"audio/{response_format}",
                headers={
                    "Content-Disposition": f"attachment; filename=stream.{response_format}",
                    "Transfer-Encoding": "chunked",
                    "Cache-Control": "no-cache",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "*"
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Streaming generation failed: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            raise HTTPException(500, detail=f"Streaming generation failed: {str(e)}")

    async def _stream_chunked_audio(self, request: TTSRequest, voice_name: str, response_format: str, speed: float):
        """Stream audio using chunked generation"""
        try:
            from LiteTTS.api.progressive_response import ProgressiveResponseHandler

            # Create progressive response handler
            progressive_handler = ProgressiveResponseHandler(self.model.progressive_generator)

            # Generate progressive response
            return await progressive_handler.create_progressive_response(
                text=request.input,
                voice=voice_name,
                response_format=response_format,
                speed=speed,
                streaming=True
            )

        except Exception as e:
            self.logger.error(f"Chunked streaming failed: {e}")
            # Fallback to standard streaming
            self.logger.info("🔄 Falling back to standard streaming")
            return await self._stream_standard_audio(request, voice_name, response_format, speed)

    async def _stream_standard_audio(self, request: TTSRequest, voice_name: str, response_format: str, speed: float):
        """Stream audio using standard generation (fallback)"""

        async def generate_audio_stream():
            try:
                start_time = time.time()

                # Generate complete audio first for better quality
                self.logger.info(f"🎯 Generating complete audio for streaming...")
                audio, sample_rate = self.model.create(
                    request.input,
                    voice=voice_name,
                    speed=speed,
                    lang="en-us"
                )

                generation_time = time.time() - start_time
                self.logger.info(f"✅ Audio generated: {len(audio)} samples at {sample_rate}Hz in {generation_time:.2f}s")

                # Convert to requested format
                buffer = io.BytesIO()
                sf.write(buffer, audio, sample_rate, format=response_format.upper())
                buffer.seek(0)
                audio_data = buffer.read()

                self.logger.info(f"📦 Audio converted to {response_format}: {len(audio_data)} bytes")

                # Stream the audio in chunks for better user experience
                chunk_size = int(self.config.audio.streaming_chunk_duration * 8000)  # Estimate bytes from duration
                total_chunks = (len(audio_data) + chunk_size - 1) // chunk_size

                self.logger.info(f"🚀 Starting standard stream: {total_chunks} chunks of ~{chunk_size} bytes")

                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i + chunk_size]
                    chunk_num = (i // chunk_size) + 1

                    self.logger.debug(f"📦 Streaming chunk {chunk_num}/{total_chunks}: {len(chunk)} bytes")

                    yield chunk

                    # Small delay to allow proper streaming
                    await asyncio.sleep(0.005)

                total_time = time.time() - start_time
                self.logger.info(f"✅ Standard streaming complete: {total_chunks} chunks in {total_time:.2f}s")

            except Exception as stream_error:
                self.logger.error(f"❌ Standard streaming error: {stream_error}")
                import traceback
                self.logger.error(f"Full traceback: {traceback.format_exc()}")
                raise

        return StreamingResponse(
            generate_audio_stream(),
            media_type=f"audio/{response_format}",
            headers={
                "Content-Disposition": f"attachment; filename=stream.{response_format}",
                "Transfer-Encoding": "chunked",
                "Cache-Control": "no-cache",
                "X-Generation-Mode": "standard",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )

    def setup_v1_endpoints(self):
        """Setup v1 API endpoints."""

        @self.v1_router.post("/audio/speech")
        async def generate_speech_v1(request: TTSRequest):
            """OpenAI-compatible TTS endpoint"""
            try:
                # Import validation here to avoid circular imports
                from LiteTTS.validation import validate_request

                # Validate and sanitize request
                request_dict = request.model_dump()
                is_valid, data_or_error, warnings = validate_request(
                    request_dict,
                    list(self.voice_manager.get_available_voices())
                )

                if not is_valid:
                    error_message = data_or_error  # This is the error message when validation fails
                    self.logger.warning(f"⚠️ Invalid request: {error_message}")
                    self.logger.warning(f"⚠️ Failed request data: {request_dict}")
                    raise HTTPException(status_code=400, detail={"error": error_message, "type": "validation_error"})

                # Log warnings if any
                if warnings:
                    for warning in warnings:
                        self.logger.warning(f"⚠️ Request warning: {warning}")

                # Create sanitized request object from validated data
                sanitized_data = data_or_error  # This is the sanitized data when validation succeeds
                sanitized_request = TTSRequest(**sanitized_data)

                self.logger.info(f"🎵 TTS request: '{sanitized_request.input[:50]}...' voice='{sanitized_request.voice}' format='{sanitized_request.response_format}'")
                return await self._generate_speech_internal(sanitized_request)
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"❌ TTS endpoint error: {e}")
                self.logger.error(f"📋 Request details: input_length={len(request.input)}, voice={request.voice}, format={request.response_format}")
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

        @self.v1_router.post("/audio/stream")
        async def stream_speech_v1(request: TTSRequest):
            """Streaming TTS endpoint for real-time audio generation"""
            try:
                # Import validation here to avoid circular imports
                from LiteTTS.validation import validate_request

                # Validate and sanitize request
                request_dict = request.model_dump()
                is_valid, data_or_error, warnings = validate_request(
                    request_dict,
                    list(self.voice_manager.get_available_voices())
                )

                if not is_valid:
                    error_message = data_or_error  # This is the error message when validation fails
                    self.logger.warning(f"⚠️ Invalid streaming request: {error_message}")
                    self.logger.warning(f"⚠️ Failed request data: {request_dict}")
                    raise HTTPException(status_code=400, detail={"error": error_message, "type": "validation_error"})

                # Log warnings if any
                if warnings:
                    for warning in warnings:
                        self.logger.warning(f"⚠️ Request warning: {warning}")

                # Create sanitized request object from validated data
                sanitized_data = data_or_error  # This is the sanitized data when validation succeeds
                sanitized_request = TTSRequest(**sanitized_data)

                self.logger.info(f"🌊 Streaming TTS request: '{sanitized_request.input[:50]}...' voice='{sanitized_request.voice}' format='{sanitized_request.response_format}'")
                return await self._stream_speech_internal(sanitized_request)
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"❌ Streaming TTS endpoint error: {e}")
                self.logger.error(f"📋 Request details: input_length={len(request.input)}, voice={request.voice}, format={request.response_format}")
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

        # OpenWebUI Compatibility Routes
        # OpenWebUI appends "/audio/speech" to the configured base URL
        # So if user configures "http://host/v1/audio/stream", OpenWebUI tries "http://host/v1/audio/stream/audio/speech"
        @self.v1_router.post("/audio/stream/audio/speech")
        async def stream_speech_openwebui_compat(request: TTSRequest):
            """OpenWebUI compatibility route - handles malformed URL construction"""
            self.logger.info(f"🔧 OpenWebUI compatibility route called: {self.config.endpoints.stream}/audio/speech")
            self.logger.info("💡 Tip: Configure OpenWebUI with base URL 'http://host:port/v1' instead of full endpoint")

            try:
                # Import validation here to avoid circular imports
                from LiteTTS.validation import validate_request

                # Validate and sanitize request
                request_dict = request.model_dump()
                is_valid, data_or_error, warnings = validate_request(
                    request_dict,
                    list(self.voice_manager.get_available_voices())
                )

                if not is_valid:
                    error_message = data_or_error
                    self.logger.warning(f"⚠️ Invalid OpenWebUI compat request: {error_message}")
                    raise HTTPException(status_code=400, detail={"error": error_message, "type": "validation_error"})

                # Create sanitized request object from validated data
                sanitized_data = data_or_error
                sanitized_request = TTSRequest(**sanitized_data)

                return await self._stream_speech_internal(sanitized_request)
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"❌ OpenWebUI compat endpoint error: {e}")
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

        # Additional compatibility route for other potential malformed URLs
        @self.v1_router.post("/audio/speech/audio/speech")
        async def speech_speech_openwebui_compat(request: TTSRequest):
            """OpenWebUI compatibility route - handles double audio/speech paths"""
            self.logger.info(f"🔧 OpenWebUI compatibility route called: {self.config.endpoints.tts}/audio/speech")
            self.logger.info("💡 Tip: Configure OpenWebUI with base URL 'http://host:port/v1' instead of full endpoint")

            try:
                # Import validation here to avoid circular imports
                from LiteTTS.validation import validate_request

                # Validate and sanitize request
                request_dict = request.model_dump()
                is_valid, data_or_error, warnings = validate_request(
                    request_dict,
                    list(self.voice_manager.get_available_voices())
                )

                if not is_valid:
                    error_message = data_or_error
                    self.logger.warning(f"⚠️ Invalid malformed URL request: {error_message}")
                    raise HTTPException(status_code=400, detail={"error": error_message, "type": "validation_error"})

                # Create sanitized request object from validated data
                sanitized_data = data_or_error
                sanitized_request = TTSRequest(**sanitized_data)

                return await self._generate_speech_internal(sanitized_request)
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"❌ Malformed URL endpoint error: {e}")
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

        @self.v1_router.get("/models")
        async def list_models():
            """List available models (OpenAI compatibility)"""
            import time

            return {
                "object": "list",
                "data": [
                    {
                        "id": self.config.model.name,
                        "object": "model",
                        "created": int(time.time()),  # Dynamic timestamp
                        "owned_by": self.config.model.owner,
                        "version": self.config.model.version,
                        "type": self.config.model.type,
                        "available_variants": self.config.model.available_variants,
                        "default_variant": self.config.model.default_variant
                    }
                ]
            }

        @self.v1_router.get("/audio/voices")
        async def list_voices_v1():
            """List available voices (OpenWebUI compatible)"""
            # Get fresh voice list - prefer combiner if available
            if hasattr(self, 'voice_combiner') and self.voice_combiner:
                current_voices = self.voice_combiner.get_voice_list()
            else:
                current_voices = self.get_available_voices()

            voice_list = []

            # Parse voice attributes inline to avoid import conflicts
            for voice in current_voices:
                # Parse voice attributes from voice name using naming convention
                if len(voice) >= 2 and '_' in voice:
                    prefix = voice.split('_')[0]
                    if len(prefix) >= 2:
                        region_char = prefix[0].upper()
                        gender_char = prefix[1].lower()

                        # Gender mapping
                        gender = "female" if gender_char == 'f' else "male" if gender_char == 'm' else "unknown"

                        # Region and language mapping
                        region_mapping = {
                            'A': {"region": "american", "language": "en-us", "flag": "🇺🇸"},
                            'B': {"region": "british", "language": "en-gb", "flag": "🇬🇧"},
                            'J': {"region": "japanese", "language": "ja-jp", "flag": "🇯🇵"},
                            'Z': {"region": "chinese", "language": "zh-cn", "flag": "🇨🇳"},
                            'S': {"region": "spanish", "language": "es-es", "flag": "🇪🇸"},
                            'F': {"region": "french", "language": "fr-fr", "flag": "🇫🇷"},
                            'H': {"region": "hindi", "language": "hi-in", "flag": "🇮🇳"},
                            'I': {"region": "italian", "language": "it-it", "flag": "🇮🇹"},
                            'P': {"region": "portuguese", "language": "pt-br", "flag": "🇧🇷"}
                        }

                        region_info = region_mapping.get(region_char, {"region": "unknown", "language": "en-us", "flag": "🌍"})
                    else:
                        gender = "unknown"
                        region_info = {"region": "unknown", "language": "en-us", "flag": "🌍"}
                else:
                    gender = "unknown"
                    region_info = {"region": "unknown", "language": "en-us", "flag": "🌍"}

                voice_list.append({
                    "id": voice,
                    "name": voice.replace("_", " ").title(),
                    "gender": gender,
                    "language": region_info["language"],
                    "region": region_info["region"],
                    "flag": region_info["flag"]
                })

            return {
                "object": "list",
                "data": voice_list
            }

        @self.v1_router.get("/health")
        async def health_check_v1():
            """Service health check (v1 API compatibility)"""
            return {
                "status": "healthy",
                "model": self.config.tts.model_path,
                "model_loaded": self.model is not None,
                "voices_available": len(self.available_voices),
                "available_voices": self.available_voices,
                "version": self.config.model.version
            }

        @self.v1_router.get("/voices")
        async def list_voices_v1_simple():
            """List available voices (OpenWebUI compatible format)"""
            # Get fresh voice list - prefer combiner if available
            if hasattr(self, 'voice_combiner') and self.voice_combiner:
                current_voices = self.voice_combiner.get_voice_list()
            else:
                current_voices = self.get_available_voices()

            # Return OpenWebUI-compatible format: array of objects with 'id' and 'name'
            voice_list = []

            # Parse voice attributes inline to avoid import conflicts
            for voice in current_voices:
                # Parse voice attributes from voice name using naming convention
                if len(voice) >= 2 and '_' in voice:
                    prefix = voice.split('_')[0]
                    if len(prefix) >= 2:
                        region_char = prefix[0].upper()
                        gender_char = prefix[1].lower()

                        # Gender mapping
                        gender = "female" if gender_char == 'f' else "male" if gender_char == 'm' else "unknown"

                        # Region mapping
                        region_mapping = {
                            'A': {"region": "american", "language": "en-us", "flag": "🇺🇸"},
                            'B': {"region": "british", "language": "en-gb", "flag": "🇬🇧"},
                            'E': {"region": "european", "language": "en-eu", "flag": "🇪🇺"},
                            'I': {"region": "international", "language": "en", "flag": "🌍"}
                        }

                        region_info = region_mapping.get(region_char, {"region": "unknown", "language": "en-us", "flag": "🌍"})
                    else:
                        gender = "unknown"
                        region_info = {"region": "unknown", "language": "en-us", "flag": "🌍"}
                else:
                    gender = "unknown"
                    region_info = {"region": "unknown", "language": "en-us", "flag": "🌍"}

                voice_list.append({
                    "id": voice,
                    "name": voice.replace("_", " ").title(),
                    "gender": gender,
                    "language": region_info["language"],
                    "region": region_info["region"],
                    "flag": region_info["flag"]
                })

            # Return direct array for OpenWebUI compatibility
            return voice_list

        @self.v1_router.post("/audio/blend")
        async def blend_voices_speech(request: dict):
            """Generate speech using blended voices"""
            try:
                # Validate required fields
                if "input" not in request:
                    raise HTTPException(400, detail="Missing 'input' field")
                if "voices" not in request:
                    raise HTTPException(400, detail="Missing 'voices' field")

                text = request["input"]
                voices_config = request["voices"]

                # Parse voice configuration
                if isinstance(voices_config, list):
                    # Format: [{"voice": "af_heart", "weight": 0.6}, {"voice": "af_sarah", "weight": 0.4}]
                    voices_and_weights = [(v["voice"], v["weight"]) for v in voices_config]
                elif isinstance(voices_config, dict):
                    # Format: {"af_heart": 0.6, "af_sarah": 0.4}
                    voices_and_weights = list(voices_config.items())
                else:
                    raise HTTPException(400, detail="Invalid voices format")

                # Get optional parameters
                blend_method = request.get("blend_method", "weighted_average")
                speed = request.get("speed", 1.0)
                response_format = request.get("response_format", self.config.audio.default_format)

                # Validate model is loaded
                if self.model is None:
                    raise HTTPException(500, detail="TTS model not loaded")

                # Create blend configuration
                from LiteTTS.voice.blender import BlendConfig
                blend_config = BlendConfig(
                    voices=voices_and_weights,
                    blend_method=blend_method,
                    normalize_weights=True,
                    preserve_energy=True
                )

                # Generate audio with blended voice
                if hasattr(self.model, 'synthesize_with_blended_voice'):
                    audio_segment = self.model.synthesize_with_blended_voice(text, blend_config, speed)
                else:
                    # Fallback: create blend and use regular synthesis
                    blended_voice = self.model.voice_blender.blend_voices(blend_config)
                    if not blended_voice:
                        raise HTTPException(500, detail="Failed to create voice blend")

                    # Use the blended voice for synthesis (this would need engine support)
                    raise HTTPException(501, detail="Voice blending not fully implemented in current engine")

                # Convert to requested format
                audio_data = self._convert_audio_format(audio_segment, response_format)

                return Response(
                    content=audio_data,
                    media_type=f"audio/{response_format}",
                    headers={
                        "Content-Disposition": f"attachment; filename=blended_speech.{response_format}",
                        "X-Blend-Voices": ",".join([v[0] for v in voices_and_weights]),
                        "X-Blend-Method": blend_method
                    }
                )

            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Voice blending failed: {e}")
                raise HTTPException(500, detail=f"Voice blending failed: {str(e)}")

        @self.v1_router.post("/audio/blend/preset")
        async def blend_preset_speech(request: dict):
            """Generate speech using preset voice blends"""
            try:
                # Validate required fields
                if "input" not in request:
                    raise HTTPException(400, detail="Missing 'input' field")
                if "preset" not in request:
                    raise HTTPException(400, detail="Missing 'preset' field")

                text = request["input"]
                preset_name = request["preset"]
                speed = request.get("speed", 1.0)
                response_format = request.get("response_format", self.config.audio.default_format)

                # Validate model is loaded
                if self.model is None:
                    raise HTTPException(500, detail="TTS model not loaded")

                # Generate audio with preset blend
                if hasattr(self.model, 'synthesize_with_preset_blend'):
                    audio_segment = self.model.synthesize_with_preset_blend(text, preset_name, speed)
                else:
                    raise HTTPException(501, detail="Preset voice blending not implemented in current engine")

                # Convert to requested format
                audio_data = self._convert_audio_format(audio_segment, response_format)

                return Response(
                    content=audio_data,
                    media_type=f"audio/{response_format}",
                    headers={
                        "Content-Disposition": f"attachment; filename=preset_blend_{preset_name}.{response_format}",
                        "X-Blend-Preset": preset_name
                    }
                )

            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Preset voice blending failed: {e}")
                raise HTTPException(500, detail=f"Preset voice blending failed: {str(e)}")

        @self.v1_router.get("/audio/blend/presets")
        async def list_blend_presets():
            """List available voice blend presets"""
            try:
                if self.model and hasattr(self.model, 'get_blend_presets'):
                    presets = self.model.get_blend_presets()
                else:
                    presets = ["warm_friendly", "professional_calm", "energetic_mix"]

                return {
                    "presets": presets,
                    "description": {
                        "warm_friendly": "Warm and friendly blend of heart and sarah voices",
                        "professional_calm": "Professional and calm blend of puck and bella voices",
                        "energetic_mix": "Energetic mix of sky, echo, and nova voices"
                    }
                }

            except Exception as e:
                self.logger.error(f"Failed to list blend presets: {e}")
                return {"presets": [], "error": str(e)}

        @self.v1_router.get("/download/{filename}")
        async def download_audio_file(filename: str):
            """Download audio file endpoint (placeholder)"""
            # Note: filename parameter required by FastAPI path parameter
            raise HTTPException(404, detail=f"Download functionality not implemented for {filename}")

    def setup_legacy_endpoints(self):
        """Setup legacy API endpoints for backward compatibility."""

        @self.legacy_router.post("/audio/speech")
        async def generate_speech_direct(request: TTSRequest):
            """Direct TTS endpoint for OpenWebUI compatibility"""
            self.logger.info("📍 Direct /audio/speech endpoint called")
            try:
                # Import validation here to avoid circular imports
                from LiteTTS.validation import validate_request

                # Validate and sanitize request
                request_dict = request.model_dump()
                is_valid, data_or_error, warnings = validate_request(
                    request_dict,
                    list(self.voice_manager.get_available_voices())
                )

                if not is_valid:
                    error_message = data_or_error
                    self.logger.warning(f"⚠️ Invalid legacy request: {error_message}")
                    raise HTTPException(status_code=400, detail={"error": error_message, "type": "validation_error"})

                # Create sanitized request object from validated data
                sanitized_data = data_or_error
                sanitized_request = TTSRequest(**sanitized_data)

                self.logger.info(f"📍 Legacy TTS request: '{sanitized_request.input[:50]}...' voice='{sanitized_request.voice}' format='{sanitized_request.response_format}'")
                return await self._generate_speech_internal(sanitized_request)
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"❌ Legacy endpoint error: {e}")
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

        @self.legacy_router.get("/voices")
        async def list_voices():
            """List available voices (legacy endpoint)"""
            # Get fresh voice list - prefer combiner if available
            if hasattr(self, 'voice_combiner') and self.voice_combiner:
                current_voices = self.voice_combiner.get_voice_list()
            else:
                current_voices = self.get_available_voices()
            return {
                "voices": current_voices,
                "default_voice": self.config.voice.default_voice
            }

        @self.legacy_router.get("/health")
        async def health_check():
            """Service health check"""
            return {
                "status": "healthy",
                "model": self.config.tts.model_path,
                "model_loaded": self.model is not None,
                "voices_available": len(self.available_voices),
                "available_voices": self.available_voices,
                "version": self.config.application.version
            }

    def setup_utility_endpoints(self):
        """Setup utility and development endpoints."""

        @self.app.post("/test-tts")
        async def test_tts():
            """Simple test endpoint to isolate TTS issues (development only)"""
            # Only allow test endpoint in development mode
            if os.getenv("ENVIRONMENT", "production").lower() == "production":
                raise HTTPException(404, detail="Test endpoint not available in production")

            try:
                self.logger.info("🧪 Testing TTS with simple request...")

                if self.model is None:
                    return {"error": "Model not loaded", "status": "failed"}

                # Simple test using configured default voice
                audio, sample_rate = self.model.create(
                    "Hello world!",
                    voice=self.config.voice.default_voice,
                    speed=self.config.audio.default_speed,
                    lang=self.config.audio.default_language
                )

                return {
                    "status": "success",
                    "audio_length": len(audio),
                    "sample_rate": sample_rate,
                    "duration": len(audio) / sample_rate
                }

            except Exception as e:
                self.logger.error(f"Test TTS failed: {e}")
                return {"error": str(e), "status": "failed"}

        @self.app.get("/cache/stats")
        async def cache_stats():
            """Get cache statistics"""
            return cache_manager.get_stats()

        @self.app.post("/cache/clear")
        async def clear_cache():
            """Clear all caches"""
            cache_manager.clear_all()
            return {"status": "success", "message": "All caches cleared"}

        @self.app.get("/performance/stats")
        async def performance_stats():
            """Get comprehensive performance statistics"""
            return self.performance_monitor.get_performance_summary()

        @self.app.get("/performance/preloader")
        async def preloader_stats():
            """Get preloader statistics"""
            if self.preloader:
                return self.preloader.get_stats()
            return {"error": "Preloader not initialized"}

        @self.app.get("/performance/rtf-trend")
        async def rtf_trend(minutes: int = 30):
            """Get RTF trend over specified time period"""
            trend_data = self.performance_monitor.get_rtf_trend(minutes)
            return {
                "trend_data": [{"timestamp": ts.isoformat(), "rtf": rtf} for ts, rtf in trend_data],
                "period_minutes": minutes,
                "data_points": len(trend_data)
            }

        @self.app.post("/performance/export")
        async def export_performance():
            """Export performance metrics to file"""
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"docs/logs/performance_export_{timestamp}.json"
            self.performance_monitor.export_metrics(filepath)
            return {"status": "success", "filepath": filepath}

        @self.app.get("/metrics")
        async def metrics():
            """Prometheus-compatible metrics endpoint"""
            try:
                # Get performance data
                performance_data = self.performance_monitor.get_performance_summary()

                # Get system metrics
                import psutil
                import time

                # Calculate uptime
                uptime_seconds = time.time() - getattr(self, 'start_time', time.time())

                # Get memory usage
                memory = psutil.virtual_memory()
                process = psutil.Process()
                process_memory = process.memory_info()

                # Get CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)

                # Format as Prometheus metrics
                metrics_lines = [
                    "# HELP kokoro_uptime_seconds Total uptime in seconds",
                    "# TYPE kokoro_uptime_seconds counter",
                    f"kokoro_uptime_seconds {uptime_seconds:.2f}",
                    "",
                    "# HELP kokoro_requests_total Total number of requests",
                    "# TYPE kokoro_requests_total counter",
                    f"kokoro_requests_total {performance_data.get('summary', {}).get('total_requests', 0)}",
                    "",
                    "# HELP kokoro_avg_rtf Average real-time factor",
                    "# TYPE kokoro_avg_rtf gauge",
                    f"kokoro_avg_rtf {performance_data.get('summary', {}).get('avg_rtf', 0):.3f}",
                    "",
                    "# HELP kokoro_avg_latency_ms Average latency in milliseconds",
                    "# TYPE kokoro_avg_latency_ms gauge",
                    f"kokoro_avg_latency_ms {performance_data.get('summary', {}).get('avg_latency_ms', 0):.2f}",
                    "",
                    "# HELP kokoro_cache_hit_rate Cache hit rate percentage",
                    "# TYPE kokoro_cache_hit_rate gauge",
                    f"kokoro_cache_hit_rate {performance_data.get('summary', {}).get('cache_hit_rate_percent', 0):.2f}",
                    "",
                    "# HELP kokoro_memory_usage_bytes Memory usage in bytes",
                    "# TYPE kokoro_memory_usage_bytes gauge",
                    f"kokoro_memory_usage_bytes {process_memory.rss}",
                    "",
                    "# HELP kokoro_system_memory_usage_percent System memory usage percentage",
                    "# TYPE kokoro_system_memory_usage_percent gauge",
                    f"kokoro_system_memory_usage_percent {memory.percent:.2f}",
                    "",
                    "# HELP kokoro_cpu_usage_percent CPU usage percentage",
                    "# TYPE kokoro_cpu_usage_percent gauge",
                    f"kokoro_cpu_usage_percent {cpu_percent:.2f}",
                    "",
                    "# HELP kokoro_available_voices Number of available voices",
                    "# TYPE kokoro_available_voices gauge",
                    f"kokoro_available_voices {len(self.available_voices)}",
                ]

                # Return as plain text with proper content type
                from fastapi.responses import PlainTextResponse
                return PlainTextResponse(
                    content="\n".join(metrics_lines) + "\n",
                    media_type="text/plain; version=0.0.4; charset=utf-8"
                )

            except Exception as e:
                self.logger.error(f"Failed to generate metrics: {e}")
                raise HTTPException(status_code=500, detail="Failed to generate metrics")

        @self.app.get("/debug")
        async def debug_info():
            """Debug information (development only)"""
            # Only allow debug endpoint in development mode
            if os.getenv("ENVIRONMENT", "production").lower() == "production":
                raise HTTPException(404, detail="Debug endpoint not available in production")

            from pathlib import Path
            model_exists = Path(self.config.tts.model_path).exists()
            voices_exists = Path(self.config.tts.voices_path).exists()

            # Return limited debug info without sensitive configuration
            return {
                "model_exists": model_exists,
                "voices_exists": voices_exists,
                "model_loaded": self.model is not None,
                "voices_available": len(self.available_voices),
                "cache_enabled": cache_manager.is_enabled(),
                "cache_stats": cache_manager.get_stats(),
                "environment": os.getenv("ENVIRONMENT", "development")
            }

        @self.app.post("/diagnostics/text-processing")
        async def test_text_processing(request: dict):
            """Diagnostic endpoint to test advanced text processing components"""
            try:
                text = request.get("text", "")
                if not text:
                    raise HTTPException(400, detail="Text parameter required")

                # Import the unified text processor for testing
                from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode

                # Initialize processor
                processor = UnifiedTextProcessor()

                # Test with enhanced mode (production settings)
                options = ProcessingOptions(
                    mode=ProcessingMode.ENHANCED,
                    use_advanced_currency=True,
                    use_enhanced_datetime=True,
                    use_advanced_symbols=True,
                    use_ticker_symbol_processing=True,
                    use_proper_name_pronunciation=True,
                    use_pronunciation_rules=True,
                    use_interjection_fixes=True
                )

                # Process the text
                result = processor.process_text(text, options)

                # Test specific critical cases
                test_cases = {
                    "tsla_test": "TSLA stock is rising",
                    "currency_test": "The price is $5,678.89",
                    "symbol_test": "Cost is ~$568.91",
                    "phonetic_test": "hedonism philosophy"
                }

                test_results = {}
                for test_name, test_text in test_cases.items():
                    test_result = processor.process_text(test_text, options)
                    test_results[test_name] = {
                        "input": test_text,
                        "output": test_result.processed_text,
                        "changes": test_result.changes_made,
                        "stages": test_result.stages_completed
                    }

                return {
                    "status": "success",
                    "input_text": text,
                    "processed_text": result.processed_text,
                    "processing_time": result.processing_time,
                    "mode_used": result.mode_used.value,
                    "stages_completed": result.stages_completed,
                    "changes_made": result.changes_made,
                    "currency_enhancements": result.currency_enhancements,
                    "datetime_enhancements": result.datetime_enhancements,
                    "audio_enhancements": result.audio_enhancements,
                    "test_cases": test_results,
                    "processor_status": {
                        "unified_processor_available": True,
                        "advanced_currency_enabled": options.use_advanced_currency,
                        "ticker_processing_enabled": options.use_ticker_symbol_processing,
                        "symbol_processing_enabled": options.use_advanced_symbols
                    }
                }

            except Exception as e:
                self.logger.error(f"Text processing diagnostic failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "processor_status": {
                        "unified_processor_available": False,
                        "error_details": str(e)
                    }
                }

        @self.app.get("/diagnostics/cpu-allocation")
        async def cpu_allocation_diagnostics():
            """Diagnostic endpoint for dynamic CPU allocation monitoring"""
            try:
                if hasattr(self, 'dynamic_allocator') and self.dynamic_allocator:
                    stats = self.dynamic_allocator.get_allocation_stats()
                    recommended = self.dynamic_allocator.get_recommended_settings()

                    return {
                        "status": "success",
                        "dynamic_allocation_enabled": True,
                        "allocation_stats": stats,
                        "recommended_settings": recommended,
                        "system_info": {
                            "total_cpu_cores": os.cpu_count(),
                            "current_pid": os.getpid()
                        }
                    }
                else:
                    return {
                        "status": "disabled",
                        "dynamic_allocation_enabled": False,
                        "message": "Dynamic CPU allocation is not initialized or disabled",
                        "system_info": {
                            "total_cpu_cores": os.cpu_count(),
                            "current_pid": os.getpid()
                        }
                    }

            except Exception as e:
                self.logger.error(f"CPU allocation diagnostic failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "dynamic_allocation_enabled": False
                }

        @self.app.get("/diagnostics/question-mark-fix")
        async def question_mark_fix_diagnostics():
            """Diagnostic endpoint specifically for question mark processing validation"""
            try:
                from LiteTTS.nlp.prosody_analyzer import ProsodyAnalyzer
                from LiteTTS.nlp.advanced_symbol_processor import AdvancedSymbolProcessor
                from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions

                # Test question mark processing pipeline
                test_cases = [
                    "What is this?",
                    "How are you?",
                    "What??? Why???",
                    "Hello! How are you? That's great!"
                ]

                prosody = ProsodyAnalyzer()
                symbol_processor = AdvancedSymbolProcessor()
                processor = UnifiedTextProcessor()

                results = []

                for test_text in test_cases:
                    # Step 1: Prosody processing
                    after_prosody_intonation = prosody.enhance_intonation_markers(test_text)
                    after_prosody_conversational = prosody.process_conversational_intonation(test_text)

                    # Step 2: Symbol processing
                    after_symbols = symbol_processor.process_symbols(after_prosody_intonation)

                    # Step 3: Complete pipeline
                    options = ProcessingOptions()
                    complete_result = processor.process_text(test_text, options)

                    # Check for arrow symbols
                    arrow_symbols = ['↗', '↘', '↑', '↓', '→', '←', '‼']
                    has_arrows_prosody = any(arrow in after_prosody_intonation for arrow in arrow_symbols)
                    has_arrows_symbols = any(arrow in after_symbols for arrow in arrow_symbols)
                    has_arrow_words = 'arrow' in complete_result.processed_text.lower()

                    results.append({
                        "input": test_text,
                        "prosody_intonation": after_prosody_intonation,
                        "prosody_conversational": after_prosody_conversational,
                        "after_symbols": after_symbols,
                        "final_output": complete_result.processed_text,
                        "stages_completed": complete_result.stages_completed,
                        "validation": {
                            "has_arrows_in_prosody": has_arrows_prosody,
                            "has_arrows_in_symbols": has_arrows_symbols,
                            "has_arrow_words_in_output": has_arrow_words,
                            "question_mark_preserved": '?' in complete_result.processed_text,
                            "fix_working": not has_arrows_prosody and not has_arrow_words
                        }
                    })

                # Overall validation
                all_fixes_working = all(r["validation"]["fix_working"] for r in results)

                return {
                    "status": "success",
                    "fix_status": "working" if all_fixes_working else "broken",
                    "description": "Question mark fix validation - ensures '?' is not converted to 'up right arrow'",
                    "test_results": results,
                    "summary": {
                        "total_tests": len(results),
                        "passing_tests": sum(1 for r in results if r["validation"]["fix_working"]),
                        "all_fixes_working": all_fixes_working,
                        "phonetic_processing_disabled": "phonetic_processing_skipped" in results[0]["stages_completed"] if results else False
                    }
                }

            except Exception as e:
                self.logger.error(f"Question mark fix diagnostic failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "description": "Failed to run question mark fix diagnostics"
                }

        @self.app.get("/examples")
        async def examples_redirect():
            """Redirect to static examples page"""
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/static/examples/", status_code=302)

        @self.app.get("/api/examples")
        async def api_examples():
            """API usage examples and documentation (JSON format for API consumers)"""
            return {
                "examples": {
                    "basic_tts": {
                        "description": "Basic text-to-speech synthesis",
                        "endpoint": "/v1/audio/speech",
                        "method": "POST",
                        "payload": {
                            "input": "Hello, world!",
                            "voice": "af_heart",
                            "response_format": "mp3"
                        }
                    },
                    "voice_selection": {
                        "description": "List available voices",
                        "endpoint": "/v1/voices",
                        "method": "GET"
                    },
                    "streaming": {
                        "description": "Streaming audio synthesis",
                        "endpoint": "/v1/audio/stream",
                        "method": "POST",
                        "payload": {
                            "input": "This is streaming text-to-speech",
                            "voice": "af_bella",
                            "response_format": "wav"
                        }
                    },
                    "models": {
                        "description": "List available models",
                        "endpoint": "/v1/models",
                        "method": "GET"
                    }
                },
                "curl_examples": {
                    "basic_synthesis": f"curl -X POST {self.config.endpoints.tts} -H 'Content-Type: application/json' -d '{{\"input\": \"Hello world\", \"voice\": \"af_heart\"}}' --output audio.mp3",
                    "list_voices": f"curl {self.config.endpoints.voices}",
                    "health_check": f"curl {self.config.endpoints.health}"
                },
                "available_voices": self.available_voices,
                "supported_formats": ["mp3", "wav", "flac", "opus"],
                "api_version": self.config.application.version,
                "interactive_examples": "/static/examples/"
            }

        @self.app.post("/suggest")
        async def suggest_voice_and_emotion():
            """Suggest optimal voice and emotion based on text content"""
            # This is a placeholder for future AI-powered voice suggestion
            return {
                "status": "not_implemented",
                "message": "Voice and emotion suggestion feature coming soon",
                "default_suggestion": {
                    "voice": self.config.voice.default_voice,
                    "emotion": "neutral",
                    "confidence": 0.5
                }
            }

        @self.app.post("/estimate")
        async def estimate_synthesis_time():
            """Estimate synthesis time for given text and voice"""
            # This is a placeholder for synthesis time estimation
            return {
                "status": "not_implemented",
                "message": "Synthesis time estimation feature coming soon",
                "estimated_time_seconds": 1.0,
                "estimated_rtf": 0.8
            }

        @self.app.get("/config/reload")
        async def reload_config_endpoint():
            """Manually reload configuration"""
            try:
                # Reload the main configuration module
                import importlib
                import LiteTTS.config
                importlib.reload(LiteTTS.config)

                # Update application config reference
                from LiteTTS.config import config
                self.config = config

                return {
                    "success": True,
                    "message": "Configuration reloaded successfully",
                    "timestamp": time.time()
                }
            except Exception as e:
                self.logger.error(f"❌ Manual config reload failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": time.time()
                }

        @self.app.get("/config/hot-reload/status")
        async def hot_reload_status():
            """Get configuration hot reload status"""
            if self.config_hot_reload_manager:
                status = self.config_hot_reload_manager.get_status()
                status["available"] = True
            else:
                status = {
                    "available": False,
                    "enabled": False,
                    "reason": "Hot reload manager not initialized"
                }

            return status

        @self.app.post("/config/hot-reload/reload-all")
        async def reload_all_configs():
            """Manually reload all configuration files"""
            if not self.config_hot_reload_manager:
                return {
                    "success": False,
                    "error": "Configuration hot reload not available"
                }

            try:
                results = self.config_hot_reload_manager.reload_all()

                # Update application config reference
                from LiteTTS.config import config
                self.config = config

                return {
                    "success": True,
                    "message": "All configuration files reloaded",
                    "results": results,
                    "timestamp": time.time()
                }
            except Exception as e:
                self.logger.error(f"❌ Reload all configs failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": time.time()
                }

    def setup_dashboard_endpoints(self):
        """Setup dashboard endpoints for real-time monitoring"""

        from fastapi.responses import HTMLResponse, RedirectResponse

        # Import dashboard analytics directly to avoid circular imports
        import sys
        import importlib.util
        spec = importlib.util.spec_from_file_location("dashboard", "LiteTTS/api/dashboard.py")
        dashboard_module = importlib.util.module_from_spec(spec)
        sys.modules["dashboard_endpoints"] = dashboard_module
        spec.loader.exec_module(dashboard_module)
        dashboard_analytics = dashboard_module.dashboard_analytics

        @self.app.get("/dashboard", response_class=HTMLResponse)
        async def dashboard_page():
            """Dashboard web interface - serve static file"""
            try:
                with open("static/dashboard/index.html", "r") as f:
                    html_content = f.read()
                return HTMLResponse(content=html_content)
            except FileNotFoundError:
                return HTMLResponse(content="<h1>Dashboard not found</h1><p>Dashboard file missing at static/dashboard/index.html</p>", status_code=404)

        @self.app.websocket("/dashboard/ws")
        async def dashboard_websocket(websocket):
            """WebSocket endpoint for real-time dashboard updates"""
            import json
            import asyncio
            import time

            await websocket.accept()
            try:
                while True:
                    # Get real-time data
                    performance_data = self.performance_monitor.get_performance_summary()
                    dashboard_data = dashboard_analytics.get_analytics_data()

                    # Combine data
                    real_time_data = {
                        "performance": performance_data,
                        "analytics": dashboard_data,
                        "system": {
                            "voices_available": len(self.available_voices),
                            "timestamp": time.time()
                        }
                    }

                    # Send data to client
                    await websocket.send_text(json.dumps(real_time_data))

                    # Wait 1 second before next update
                    await asyncio.sleep(1)

            except Exception as e:
                self.logger.debug(f"WebSocket connection closed: {e}")
            finally:
                await websocket.close()

        @self.app.get("/dashboard/data")
        async def dashboard_data():
            """Dashboard data API endpoint (fallback for non-WebSocket clients)"""
            try:
                # Get performance data from existing monitor
                performance_data = self.performance_monitor.get_performance_summary()

                # Get dashboard analytics data
                analytics_data = dashboard_analytics.get_dashboard_data()

                # Combine data sources with fallbacks
                performance_summary = performance_data.get('summary', {})
                analytics_system = analytics_data.get('system_status', {})

                combined_data = {
                    **analytics_data,
                    'performance': performance_data,
                    'tts_stats': {
                        # Use analytics data first, then performance data as fallback
                        'total_requests': max(
                            analytics_system.get('total_requests_all_time', 0),
                            performance_summary.get('total_requests', 0)
                        ),
                        'cache_hit_rate': performance_summary.get('cache_hit_rate_percent', 0),
                        'avg_rtf': performance_summary.get('avg_rtf', 0),
                        'avg_latency_ms': performance_summary.get('avg_latency_ms', 0)
                    }
                }

                return combined_data

            except Exception as e:
                self.logger.error(f"Dashboard data error: {e}")
                return {
                    "error": "Failed to fetch dashboard data",
                    "timestamp": time.time(),
                    "requests_per_minute": [],
                    "response_time_stats": {"avg": 0, "min": 0, "max": 0, "p50": 0, "p95": 0, "p99": 0},
                    "error_rates": {"total_requests": 0, "error_rate_percent": 0, "status_code_distribution": {}},
                    "voice_usage": {},
                    "concurrency": {"current": {"active_connections": 0, "queue_size": 0, "processing_requests": 0}, "history": []},
                    "system_status": {"uptime_seconds": 0, "total_requests_all_time": 0, "total_errors_all_time": 0}
                }


# Auto-configure uvicorn when imported directly
import os
import sys

# Check if we're being run by uvicorn and apply configuration
def _configure_uvicorn_early():
    """Configure uvicorn when imported directly"""
    # Check if we're being run by uvicorn
    is_uvicorn_import = (
        'uvicorn' in ' '.join(sys.argv) or
        any('uvicorn' in str(arg) for arg in sys.argv)
    )

    if is_uvicorn_import:
        try:
            # We need to create a minimal config instance to get the configuration
            from LiteTTS.config import LiteTTSConfig
            temp_config = LiteTTSConfig()

            # Get configuration values
            configured_port = int(os.getenv("PORT", temp_config.server.port))
            configured_host = os.getenv("API_HOST", temp_config.server.host)
            configured_workers = int(os.getenv("WORKERS", temp_config.server.workers))

            # Find available port
            import socket
            def find_available_port_simple(start_port):
                for port in range(start_port, start_port + 10):
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                            sock.bind(('localhost', port))
                            return port
                    except OSError:
                        continue
                return start_port

            available_port = find_available_port_simple(configured_port)

            # Store configuration globally for uvicorn to pick up
            import builtins
            builtins._kokoro_uvicorn_config = {
                'port': available_port,
                'host': configured_host,
                'workers': configured_workers,
                'configured_port': configured_port
            }

            # Log configuration being applied
            if available_port != configured_port:
                print(f"⚠️  Port {configured_port} was unavailable, using {available_port}")
            print(f"🚀 Auto-configured uvicorn: {configured_host}:{available_port} (workers: {configured_workers})")

        except Exception:
            # Silently fail if configuration fails
            pass

# Apply early uvicorn configuration
_configure_uvicorn_early()

# Create application instance
tts_app = KokoroTTSApplication()
app = tts_app.create_app()

# Configuration is available via tts_app.config for external scripts

# Auto-configure uvicorn when imported directly
def _configure_uvicorn_on_import():
    """
    Configure uvicorn when app.py is imported directly by uvicorn.
    This enables 'uv run uvicorn app:app' to automatically use configured settings.
    """
    import sys

    # Check if we're being run by uvicorn
    is_uvicorn_import = (
        'uvicorn' in ' '.join(sys.argv) or
        any('uvicorn' in str(arg) for arg in sys.argv)
    )

    if is_uvicorn_import:
        _apply_uvicorn_configuration()

def _apply_uvicorn_configuration():
    """Apply configuration to uvicorn when imported directly"""
    try:
        import sys
        import builtins

        # Get stored configuration
        config = getattr(builtins, '_kokoro_uvicorn_config', None)
        if not config:
            return

        # Try to patch uvicorn's Config class
        try:
            import uvicorn.config

            original_init = uvicorn.config.Config.__init__

            def patched_init(self, app, **kwargs):
                # Apply our configuration if not explicitly provided
                if 'port' not in kwargs and not any('--port' in arg for arg in sys.argv):
                    kwargs['port'] = config['port']
                if 'host' not in kwargs and not any('--host' in arg for arg in sys.argv):
                    kwargs['host'] = config['host']
                if 'workers' not in kwargs and not any('--workers' in arg for arg in sys.argv):
                    kwargs['workers'] = config['workers']

                return original_init(self, app, **kwargs)

            uvicorn.config.Config.__init__ = patched_init

        except ImportError:
            # uvicorn not available yet
            pass

    except Exception:
        # Silently fail if uvicorn configuration fails
        pass

# Apply uvicorn configuration when imported
_configure_uvicorn_on_import()

# Enhanced configuration logging and uvicorn guidance
def log_configuration_status():
    """Log detailed configuration status and provide guidance"""
    from pathlib import Path
    import json

    print()
    print("Configuration Status:")

    # Check which config files exist and are being used
    config_sources = []

    # Base config
    if Path("config.json").exists():
        config_sources.append("config.json (base)")

    # Override config
    override_path = Path("override.json")
    if override_path.exists():
        try:
            with open(override_path, 'r') as f:
                override_data = json.load(f)
            config_sources.append("override.json (active)")
            if "server" in override_data and "port" in override_data["server"]:
                print(f"   Port override: {override_data['server']['port']} (from override.json)")
        except Exception as e:
            config_sources.append("override.json (error)")
            print(f"   Error reading override.json: {e}")

    # Environment variables
    env_vars = []
    if os.getenv("PORT"):
        env_vars.append(f"PORT={os.getenv('PORT')}")
    if os.getenv("API_HOST"):
        env_vars.append(f"API_HOST={os.getenv('API_HOST')}")

    if env_vars:
        config_sources.append("environment variables")
        print(f"   Environment overrides: {', '.join(env_vars)}")

    print(f"   Configuration sources: {' → '.join(config_sources)}")
    print(f"   Final configuration: port={tts_app.config.server.port}, host={tts_app.config.server.host}")

    return tts_app.config.server.port

# Print helpful message when uvicorn is used without port specification
if 'uvicorn' in ' '.join(sys.argv) and __name__ != "__main__":
    configured_port = log_configuration_status()

    if not any('--port' in arg for arg in sys.argv):
        print()
        print(f"WARNING: uvicorn will use its default port 8000, ignoring configured port {configured_port}")
        print(f"To use the configured port, run: uv run uvicorn app:app --port {configured_port}")
        print(f"Or use the built-in server: python start_server.py")
        print(f"Dashboard: http://{tts_app.config.server.host}:8000/dashboard")
        print(f"API docs: http://{tts_app.config.server.host}:8000/docs")
        print()
    else:
        print()
        print("Using uvicorn with explicit port configuration")
        print()

# Export port configuration for uvicorn
def get_configured_port():
    """Get the configured port for uvicorn"""
    return tts_app.config.server.port

def get_configured_host():
    """Get the configured host for uvicorn"""
    return tts_app.config.server.host

def get_configured_host():
    """Get the configured host for uvicorn"""
    return tts_app.config.server.host

def get_configured_workers():
    """Get the configured workers for uvicorn"""
    return tts_app.config.server.workers

# Configuration is available via tts_app.config for external scripts
import os
import sys


def run_server():
    """Run the server with proper configuration"""
    import uvicorn

    # Use configured port with auto-increment if unavailable
    default_port = int(os.getenv("PORT", tts_app.config.server.port))
    available_port = tts_app.find_available_port(default_port)

    print(f"Starting Kokoro ONNX TTS API on {tts_app.config.server.host}:{available_port}")
    print(f"Configuration loaded from config.json")
    if available_port != default_port:
        print(f"Port {default_port} was unavailable, using {available_port}")

    uvicorn.run(
        app,
        host=tts_app.config.server.host,
        port=available_port,
        workers=int(os.getenv("WORKERS", tts_app.config.server.workers))
    )


# Export configuration for external tools
def get_uvicorn_config():
    """Get uvicorn configuration dict for external use"""
    return {
        "app": "app:app",
        "host": tts_app.config.server.host,
        "port": tts_app.config.server.port,
        "workers": tts_app.config.server.workers,
        "reload": False,
        "log_level": "info"
    }


def clean_json_response(text: str) -> str:
    """
    Clean JSON response text by removing emojis and decorative Unicode characters.
    Keeps responses machine-readable while maintaining informative content.
    """
    import re

    # Remove emoji characters (comprehensive Unicode ranges)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
        "]+",
        flags=re.UNICODE
    )

    # Remove common decorative symbols
    decorative_symbols = [
        "🚀", "📊", "✅", "⚠️", "❌", "🔧", "🌍", "📁", "🎯", "💡",
        "🌐", "📚", "🎤", "🔗", "📝", "🔌", "🎵", "🎭", "🔍", "🧪",
        "🎉", "📋", "📄", "📦", "🛑", "⏰", "🔄", "🎶", "🎼", "🎹",
        "🎸", "♪", "♫", "♬", "♩", "♭", "♮", "♯", "🔊", "🔉", "🔈",
        "🔇", "📢", "📣", "📯", "🎺", "🎷", "🥁", "🎻"
    ]

    # Remove decorative symbols
    for symbol in decorative_symbols:
        text = text.replace(symbol, "")

    # Apply emoji pattern removal
    text = emoji_pattern.sub("", text)

    # Clean up extra whitespace that might be left after removing symbols
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def main():
    """Main entry point with command-line argument support"""
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(
        description="Kokoro ONNX TTS API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                                    # Use configured defaults
  python app.py --config custom.json              # Use custom configuration file
  python app.py --reload                          # Enable hot reload for development
  python app.py --host 0.0.0.0 --port 8354       # Override host and port
  python app.py --reload --workers 1              # Development with specific workers
  python app.py --config prod.json --host 0.0.0.0 # Custom config with host override
  uv run python app.py --reload                   # Same functionality with uv
        """
    )

    # Configuration arguments
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (default: config.json)"
    )

    # Server configuration arguments
    parser.add_argument(
        "--host",
        type=str,
        help="Host to bind the server to (default: from config)"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to bind the server to (default: from config)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        help="Number of worker processes (default: from config)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        default="info",
        help="Log level (default: info)"
    )

    args = parser.parse_args()

    # Handle custom configuration file if specified
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Configuration file '{args.config}' not found")
            return 1

        print(f"Loading configuration from: {args.config}")

        # Reload configuration with custom path
        try:
            import json
            from LiteTTS.config import Config

            # Load custom config
            with open(config_path) as f:
                custom_config_data = json.load(f)

            # Create new config instance with custom data
            tts_app.config = Config(custom_config_data)

            print(f"✅ Configuration loaded successfully from {args.config}")

        except Exception as e:
            print(f"Error loading configuration from '{args.config}': {e}")
            return 1

    # Get configuration from app with environment variable and config file precedence
    configured_host = args.host or os.getenv("API_HOST", tts_app.config.server.host)
    configured_port = args.port or int(os.getenv("PORT", tts_app.config.server.port))
    configured_workers = args.workers or int(os.getenv("WORKERS", tts_app.config.server.workers))

    # Find available port if configured port is in use (unless explicitly specified)
    if args.port is None:
        available_port = tts_app.find_available_port(configured_port)
        if available_port != configured_port:
            print(f"Port {configured_port} was unavailable, using {available_port}")
        configured_port = available_port
    else:
        print(f"Using exact port {configured_port} as specified")

    # Display startup information
    print(f"Starting Kokoro ONNX TTS API on {configured_host}:{configured_port}")
    print(f"Configuration loaded from config.json")
    if args.reload:
        print("Hot reload enabled for development")

    # Start the server
    final_workers = configured_workers if not args.reload else 1

    # Use import string for multiple workers, app object for single worker
    if final_workers > 1:
        # Multiple workers require import string
        uvicorn.run(
            "app:app",  # Import string
            host=configured_host,
            port=configured_port,
            workers=final_workers,
            reload=args.reload,
            log_level=args.log_level,
            access_log=not args.reload,
            server_header=False,
            date_header=False
        )
    else:
        # Single worker can use app object directly
        uvicorn.run(
            app,  # App object
            host=configured_host,
            port=configured_port,
            reload=args.reload,
            log_level=args.log_level,
            access_log=not args.reload,
            server_header=False,
            date_header=False
        )


if __name__ == "__main__":
    main()
