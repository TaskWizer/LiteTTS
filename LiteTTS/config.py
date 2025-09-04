#!/usr/bin/env python3
"""
Configuration management for Kokoro ONNX TTS API
"""

import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Model configuration"""
    name: str = "LiteTTS"
    type: str = "style_text_to_speech_2"
    version: str = "1.0.0"
    default_variant: str = "model_q4.onnx"  # Use Q4 quantized model for optimal performance/size balance
    available_variants: List[str] = None
    auto_discovery: bool = True
    cache_models: bool = True
    owner: str = "TaskWizer"
    performance_mode: str = "balanced"
    preload_models: bool = True  # Enable model preloading for faster startup

    def __post_init__(self):
        if self.available_variants is None:
            self.available_variants = [
                "model.onnx",
                "model_fp16.onnx",
                "model_q4.onnx",
                "model_q4f16.onnx",
                "model_q8f16.onnx",
                "model_quantized.onnx",
                "model_uint8.onnx",
                "model_uint8f16.onnx"
            ]

@dataclass
class VoiceConfig:
    """Voice configuration"""
    default_voice: str = "af_heart"
    auto_discovery: bool = True
    download_all_on_startup: bool = False  # Changed default to False for individual loading
    cache_discovery: bool = True
    discovery_cache_hours: int = 24
    default_voices: List[str] = None
    max_cache_size: int = 10  # Increased for better individual voice caching
    preload_default_voices: bool = True
    voice_blending: bool = True
    emotion_support: bool = True
    loading_strategy: str = "individual"  # New: individual, combined, auto
    cache_strategy: str = "lru"  # New: lru, fifo, priority
    performance_monitoring: bool = True  # New: enable performance tracking
    use_combined_file: bool = False  # New: disable combined file usage

    def __post_init__(self):
        if self.default_voices is None:
            self.default_voices = ["af_heart", "am_puck"]

@dataclass
class ChunkedGenerationConfig:
    """Chunked generation configuration for progressive audio output"""
    enabled: bool = True
    strategy: str = "adaptive"  # sentence, phrase, fixed_size, adaptive
    max_chunk_size: int = 200
    min_chunk_size: int = 50
    overlap_size: int = 20
    respect_sentence_boundaries: bool = True
    respect_paragraph_boundaries: bool = True
    preserve_punctuation: bool = True
    enable_for_streaming: bool = True
    min_text_length_for_chunking: int = 100

@dataclass
class AudioConfig:
    """Audio configuration"""
    default_format: str = "mp3"
    default_speed: float = 1.0
    default_language: str = "en-us"
    sample_rate: int = 24000
    chunk_size: int = 8192  # For streaming audio
    supported_formats: List[str] = None

    # Audio conversion parameters
    mp3_bitrate: int = 128
    wav_bit_depth: int = 16
    ogg_quality: int = 5
    flac_bit_depth: int = 24

    # Audio processing parameters
    compression_threshold: float = 0.7
    compression_ratio: float = 4.0
    normalization_threshold: float = 0.95
    streaming_chunk_duration: float = 1.0

    # Watermarking configuration
    watermarking_enabled: bool = True
    watermark_strength: float = 1.0
    watermark_detection_enabled: bool = True
    use_dummy_watermarker: bool = False
    device: str = "cpu"  # cpu or cuda
    quality_threshold: float = 0.8
    max_processing_time_ms: float = 1000.0

    # Chunked generation configuration
    chunked_generation: Optional[ChunkedGenerationConfig] = None

    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ["mp3", "wav", "ogg", "flac", "aac"]
        if self.chunked_generation is None:
            self.chunked_generation = ChunkedGenerationConfig()

@dataclass
class ServerConfig:
    """Server configuration"""
    port: int = 8354
    max_port_attempts: int = 10
    host: str = "0.0.0.0"
    workers: int = 1
    environment: str = "production"
    cors_origins: List[str] = None
    request_timeout: int = 30

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

@dataclass
class PerformanceConfig:
    """Performance configuration"""
    hot_reload: bool = True
    cache_enabled: bool = True
    preload_models: bool = False
    chunk_size: int = 100
    max_text_length: int = 5000
    timeout_seconds: int = 30
    max_retry_attempts: int = 3
    retry_delay_seconds: float = 0.1
    concurrent_requests: int = 10
    memory_optimization: bool = True

    # Text preprocessing configuration - Use settings.json as source of truth
    expand_contractions: bool = False  # Default: preserve natural speech, expand only problematic contractions
    expand_problematic_contractions_only: bool = True  # Only expand problematic contractions by default
    preserve_natural_speech: bool = True  # Preserve natural speech patterns while fixing pronunciation issues

    # Emoji and symbol handling configuration
    filter_emojis: bool = True  # Default: remove emojis to prevent verbalization
    emoji_replacement: str = ""  # What to replace emojis with (empty string = remove)
    preserve_word_count: bool = True  # Preserve word count to avoid phonemizer mismatches

    # Synthesis time estimation parameters
    base_time_per_char: float = 0.01  # 10ms per character
    cache_multiplier: float = 1.0
    no_cache_multiplier: float = 1.5
    cpu_device_multiplier: float = 2.0
    cuda_device_multiplier: float = 1.0
    min_synthesis_time: float = 0.1  # Minimum 100ms

    # Dynamic CPU allocation configuration
    dynamic_cpu_allocation: Optional[Dict] = None

@dataclass
class RepositoryConfig:
    """Repository configuration"""
    huggingface_repo: str = "onnx-community/Kokoro-82M-v1.0-ONNX"
    models_path: str = "onnx"
    voices_path: str = "voices"
    base_url: str = "https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main"
    model_branch: str = "main"  # Git branch for model repository
    cache_dir: str = "models"  # Local cache directory for models

@dataclass
class PathsConfig:
    """Paths configuration"""
    models_dir: str = "LiteTTS/models"
    voices_dir: str = "LiteTTS/voices"
    cache_dir: str = "cache"
    logs_dir: str = "docs/logs"
    temp_dir: str = "LiteTTS/temp"

@dataclass
class TokenizerConfig:
    """Tokenizer configuration"""
    character_set: str = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?;:-'"
    pad_token_id: int = 0
    unk_token_id: int = 0
    type: str = "character"

@dataclass
class EndpointsConfig:
    """API endpoints configuration"""
    tts: str = "/v1/audio/speech"
    stream: str = "/v1/audio/stream"
    voices: str = "/v1/voices"
    models: str = "/v1/models"
    health: str = "/health"
    docs: str = "/docs"
    dashboard: str = "/dashboard"
    metrics: str = "/metrics"

@dataclass
class ApplicationConfig:
    """Application metadata configuration"""
    name: str = "LiteTTS"
    description: str = "High-quality text-to-speech service with ONNX optimization and OpenWebUI compatibility (part of TaskWizer framework)"
    version: str = "1.0.0"
    author: str = "TaskWizer Team"
    license: str = "MIT"
    documentation_url: str = "https://github.com/aliasfoxkde/LiteTTS"

@dataclass
class TTSConfig:
    """Legacy TTS engine configuration for backward compatibility"""
    model_path: str = "LiteTTS/models/model_q4.onnx"  # Use Q4 quantized model by default
    voices_path: str = "LiteTTS/voices"
    default_voice: str = "af_heart"
    sample_rate: int = 24000
    chunk_size: int = 100
    device: str = "cpu"
    
@dataclass
class APIConfig:
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8354  # Use same default as ServerConfig
    workers: int = 1
    reload: bool = False
    log_level: str = "INFO"
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

@dataclass
class CacheConfig:
    """Caching configuration"""
    enabled: bool = True
    max_size: int = 100  # Maximum cached items
    ttl: int = 3600  # Time to live in seconds
    voice_cache_size: int = 10
    audio_cache_size: int = 50

    # Memory and disk cache sizes (in MB)
    memory_cache_size_mb: int = 100
    disk_cache_size_mb: int = 1024
    audio_memory_cache_mb: int = 50
    audio_disk_cache_mb: int = 500
    text_memory_cache_mb: int = 10
    text_disk_cache_mb: int = 50
    text_cache_ttl: int = 86400  # 24 hours for text cache

@dataclass
class MonitoringConfig:
    """Performance monitoring configuration"""
    enabled: bool = True
    max_history: int = 1000
    system_monitoring: bool = True
    monitoring_interval: float = 1.0  # seconds
    join_timeout: float = 5.0  # seconds

@dataclass
class TestingConfig:
    """Testing configuration"""
    enable_mock_voices: bool = False
    mock_voice_count: int = 10
    enable_performance_testing: bool = True
    test_timeout_seconds: int = 30

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class MetricsConfig:
    """Monitoring and metrics configuration"""
    enabled: bool = True
    metrics_endpoint: bool = True
    health_endpoint: bool = True
    request_tracking: bool = True
    performance_logging: bool = True
    metrics_retention_days: int = 7

@dataclass
class SecurityConfig:
    """Security configuration"""
    api_key_required: bool = False
    api_key: Optional[str] = None
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    max_text_length: int = 5000
    allowed_origins: list = None
    
    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = ["*"]

class ConfigManager:
    """Central configuration manager with comprehensive environment variable support"""

    def __init__(self, config_file: str = None):
        # Determine config file location with backward compatibility
        if config_file is None:
            # Check for new comprehensive settings file first (preferred)
            if Path("config/settings.json").exists():
                config_file = "config/settings.json"
            # Fall back to root config.json for backward compatibility
            elif Path("config.json").exists():
                config_file = "config.json"
            # Fall back to old location for backward compatibility
            elif Path("LiteTTS/config.json").exists():
                config_file = "LiteTTS/config.json"
            else:
                # Default to new comprehensive settings location
                config_file = "config/settings.json"

        # Load from JSON config file first
        self.config_file = Path(config_file)
        self._load_from_json()

        # Legacy configurations for backward compatibility
        self.tts = TTSConfig()
        self.api = APIConfig()
        self.cache = CacheConfig()
        self.logging = LoggingConfig()
        self.monitoring = MonitoringConfig()
        self.metrics = MetricsConfig()
        self.security = SecurityConfig()
        self.testing = TestingConfig()
        self.audio = AudioConfig()

        # Load environment overrides
        self._load_from_env()
        # Update legacy configs after environment loading to ensure proper sync
        self._update_legacy_configs()
        self._validate_startup()

    def _load_from_json(self):
        """Load configuration from JSON file with custom override support"""
        try:
            # Load base configuration
            config_data = {}
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                logger.info(f"Loaded base configuration from {self.config_file}")
            else:
                logger.warning(f"Config file {self.config_file} not found, using defaults")

            # Load override configuration
            override_config_file = Path("override.json")
            if override_config_file.exists():
                try:
                    with open(override_config_file, 'r') as f:
                        override_config_data = json.load(f)

                    # Merge override configuration with base configuration
                    config_data = self._deep_merge_config(config_data, override_config_data)
                    logger.info(f"Applied configuration overrides from {override_config_file}")
                except Exception as e:
                    logger.error(f"Failed to load override configuration from {override_config_file}: {e}")
                    logger.warning("Continuing with base configuration only")

            # Initialize configuration sections with merged data
            self.model = ModelConfig(**config_data.get("model", {}))
            self.voice = VoiceConfig(**config_data.get("voice", {}))
            # Handle nested chunked_generation config
            audio_config = config_data.get("audio", {})
            chunked_gen_data = audio_config.pop("chunked_generation", {})
            self.audio = AudioConfig(**audio_config)
            if chunked_gen_data:
                self.audio.chunked_generation = ChunkedGenerationConfig(**chunked_gen_data)
            self.server = ServerConfig(**config_data.get("server", {}))

            # Filter out problematic sections from performance config to prevent errors
            performance_data = config_data.get("performance", {}).copy()
            performance_data.pop("threading", None)  # Remove threading if present
            performance_data.pop("onnx_runtime", None)  # Remove onnx_runtime if present
            performance_data.pop("processing", None)  # Remove processing if present
            performance_data.pop("caching", None)  # Remove caching if present
            performance_data.pop("batch_processing", None)  # Remove batch_processing if present
            performance_data.pop("memory_management", None)  # Remove memory_management if present
            self.performance = PerformanceConfig(**performance_data)

            # Safe repository config initialization with error handling
            try:
                repo_config = config_data.get("repository", {})
                # Filter out any unknown parameters that might cause issues
                valid_repo_params = {
                    k: v for k, v in repo_config.items()
                    if k in ['huggingface_repo', 'models_path', 'voices_path', 'base_url', 'model_branch', 'cache_dir']
                }
                self.repository = RepositoryConfig(**valid_repo_params)
            except TypeError as e:
                logger.warning(f"Repository config initialization failed: {e}, using defaults")
                self.repository = RepositoryConfig()

            self.paths = PathsConfig(**config_data.get("paths", {}))
            self.tokenizer = TokenizerConfig(**config_data.get("tokenizer", {}))
            self.endpoints = EndpointsConfig(**config_data.get("endpoints", {}))
            self.application = ApplicationConfig(**config_data.get("application", {}))

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Fall back to defaults with safe initialization
            self.model = ModelConfig()
            self.voice = VoiceConfig()
            self.audio = AudioConfig()
            self.server = ServerConfig()
            self.performance = PerformanceConfig()

            # Safe repository config initialization
            try:
                self.repository = RepositoryConfig()
            except TypeError as repo_error:
                logger.warning(f"RepositoryConfig initialization failed: {repo_error}, using minimal config")
                # Create minimal repository config manually
                self.repository = type('RepositoryConfig', (), {
                    'huggingface_repo': "onnx-community/Kokoro-82M-v1.0-ONNX",
                    'models_path': "onnx",
                    'voices_path': "voices",
                    'base_url': "https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main",
                    'model_branch': "main",
                    'cache_dir': "models"
                })()

            self.paths = PathsConfig()
            self.tokenizer = TokenizerConfig()
            self.endpoints = EndpointsConfig()
            self.application = ApplicationConfig()

    def _deep_merge_config(self, base: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge custom configuration into base configuration.
        Custom values override base values, preserving nested structure.
        """
        result = base.copy()

        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge_config(result[key], value)
            else:
                # Override with custom value
                result[key] = value

        return result

    def _update_legacy_configs(self):
        """Update legacy configurations with new values for backward compatibility"""
        # Update TTSConfig with new values
        self.tts.model_path = str(Path(self.paths.models_dir) / self.model.default_variant)
        self.tts.voices_path = self.paths.voices_dir
        self.tts.default_voice = self.voice.default_voice
        self.tts.sample_rate = self.audio.sample_rate
        self.tts.chunk_size = self.performance.chunk_size

        # Update APIConfig with new values
        self.api.port = self.server.port
        self.api.host = self.server.host
        self.api.workers = self.server.workers

        # Update CacheConfig with new values
        self.cache.enabled = self.performance.cache_enabled
    
    def _load_from_env(self):
        """Load configuration from environment variables with type safety"""
        try:
            # Model Configuration
            self.model.name = os.getenv("KOKORO_MODEL_NAME", self.model.name)
            self.model.default_variant = os.getenv("KOKORO_MODEL_VARIANT", self.model.default_variant)
            self.model.auto_discovery = os.getenv("KOKORO_MODEL_AUTO_DISCOVERY", str(self.model.auto_discovery)).lower() == "true"
            self.model.cache_models = os.getenv("KOKORO_CACHE_MODELS", str(self.model.cache_models)).lower() == "true"

            # Voice Configuration
            self.voice.default_voice = os.getenv("KOKORO_DEFAULT_VOICE", self.voice.default_voice)
            self.voice.auto_discovery = os.getenv("KOKORO_VOICE_AUTO_DISCOVERY", str(self.voice.auto_discovery)).lower() == "true"
            self.voice.download_all_on_startup = os.getenv("DOWNLOAD_ALL_VOICES", str(self.voice.download_all_on_startup)).lower() == "true"
            self.voice.cache_discovery = os.getenv("KOKORO_CACHE_DISCOVERY", str(self.voice.cache_discovery)).lower() == "true"
            self.voice.discovery_cache_hours = int(os.getenv("KOKORO_DISCOVERY_CACHE_HOURS", str(self.voice.discovery_cache_hours)))

            # Audio Configuration
            self.audio.default_format = os.getenv("KOKORO_DEFAULT_FORMAT", self.audio.default_format)
            self.audio.sample_rate = int(os.getenv("KOKORO_SAMPLE_RATE", str(self.audio.sample_rate)))

            # Server Configuration
            self.server.port = int(os.getenv("PORT", str(self.server.port)))
            self.server.max_port_attempts = int(os.getenv("MAX_PORT_ATTEMPTS", str(self.server.max_port_attempts)))
            self.server.host = os.getenv("API_HOST", self.server.host)
            self.server.workers = int(os.getenv("WORKERS", str(self.server.workers)))
            self.server.environment = os.getenv("ENVIRONMENT", self.server.environment)

            # Performance Configuration
            self.performance.hot_reload = os.getenv("KOKORO_HOT_RELOAD", str(self.performance.hot_reload)).lower() == "true"
            self.performance.cache_enabled = os.getenv("CACHE_ENABLED", str(self.performance.cache_enabled)).lower() == "true"
            self.performance.preload_models = os.getenv("KOKORO_PRELOAD_MODELS", str(self.performance.preload_models)).lower() == "true"
            self.performance.chunk_size = int(os.getenv("KOKORO_CHUNK_SIZE", str(self.performance.chunk_size)))
            self.performance.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", str(self.performance.max_text_length)))
            self.performance.timeout_seconds = int(os.getenv("KOKORO_TIMEOUT", str(self.performance.timeout_seconds)))

            # Repository Configuration
            self.repository.huggingface_repo = os.getenv("LITETTS_HF_REPO", self.repository.huggingface_repo)
            self.repository.base_url = os.getenv("LITETTS_BASE_URL", self.repository.base_url)

            # Paths Configuration
            self.paths.models_dir = os.getenv("LITETTS_MODELS_DIR", self.paths.models_dir)
            self.paths.voices_dir = os.getenv("LITETTS_VOICES_DIR", self.paths.voices_dir)
            self.paths.cache_dir = os.getenv("LITETTS_CACHE_DIR", self.paths.cache_dir)

            # Legacy TTS Configuration (for backward compatibility)
            self.tts.model_path = os.getenv("KOKORO_MODEL_PATH", str(Path(self.paths.models_dir) / self.model.default_variant))
            self.tts.voices_path = os.getenv("KOKORO_VOICES_PATH", self.paths.voices_dir)
            self.tts.default_voice = os.getenv("KOKORO_DEFAULT_VOICE", self.voice.default_voice)
            self.tts.sample_rate = int(os.getenv("KOKORO_SAMPLE_RATE", str(self.audio.sample_rate)))
            self.tts.chunk_size = int(os.getenv("KOKORO_CHUNK_SIZE", str(self.performance.chunk_size)))
            self.tts.device = "cuda" if os.getenv("USE_CUDA", "false").lower() == "true" else "cpu"
            
            # API Configuration - sync with server configuration
            self.api.host = os.getenv("API_HOST", self.server.host)
            self.api.port = int(os.getenv("PORT", str(self.server.port)))
            self.api.workers = int(os.getenv("WORKERS", str(self.server.workers)))
            self.api.reload = os.getenv("API_RELOAD", "false").lower() == "true"
            self.api.log_level = os.getenv("LOG_LEVEL", self.api.log_level)
            
            # Parse CORS origins
            cors_origins = os.getenv("CORS_ORIGINS")
            if cors_origins:
                self.api.cors_origins = [origin.strip() for origin in cors_origins.split(",")]
            
            # Cache Configuration
            self.cache.enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
            self.cache.max_size = int(os.getenv("CACHE_MAX_SIZE", str(self.cache.max_size)))
            self.cache.ttl = int(os.getenv("CACHE_TTL", str(self.cache.ttl)))
            self.cache.voice_cache_size = int(os.getenv("VOICE_CACHE_SIZE", str(self.cache.voice_cache_size)))
            self.cache.audio_cache_size = int(os.getenv("AUDIO_CACHE_SIZE", str(self.cache.audio_cache_size)))
            
            # Logging Configuration
            self.logging.level = os.getenv("LOG_LEVEL", self.logging.level)
            self.logging.file_path = os.getenv("LOG_FILE_PATH")
            self.logging.max_file_size = int(os.getenv("LOG_MAX_FILE_SIZE", str(self.logging.max_file_size)))
            self.logging.backup_count = int(os.getenv("LOG_BACKUP_COUNT", str(self.logging.backup_count)))
            
            # Monitoring Configuration
            self.monitoring.enabled = os.getenv("MONITORING_ENABLED", str(self.monitoring.enabled)).lower() == "true"
            self.monitoring.max_history = int(os.getenv("MONITORING_MAX_HISTORY", str(self.monitoring.max_history)))
            self.monitoring.system_monitoring = os.getenv("SYSTEM_MONITORING", str(self.monitoring.system_monitoring)).lower() == "true"
            self.monitoring.monitoring_interval = float(os.getenv("MONITORING_INTERVAL", str(self.monitoring.monitoring_interval)))
            self.monitoring.join_timeout = float(os.getenv("MONITORING_JOIN_TIMEOUT", str(self.monitoring.join_timeout)))

            # Metrics Configuration
            self.metrics.enabled = os.getenv("METRICS_ENABLED", str(self.metrics.enabled)).lower() == "true"
            self.metrics.metrics_endpoint = os.getenv("METRICS_ENDPOINT", str(self.metrics.metrics_endpoint)).lower() == "true"
            self.metrics.health_endpoint = os.getenv("HEALTH_ENDPOINT", str(self.metrics.health_endpoint)).lower() == "true"
            self.metrics.request_tracking = os.getenv("REQUEST_TRACKING", str(self.metrics.request_tracking)).lower() == "true"
            
            # Security Configuration
            self.security.api_key_required = os.getenv("API_KEY_REQUIRED", "false").lower() == "true"
            self.security.api_key = os.getenv("API_KEY")
            self.security.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
            self.security.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", str(self.security.rate_limit_requests)))
            self.security.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", str(self.security.rate_limit_window)))
            self.security.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", str(self.security.max_text_length)))
            
            # Parse allowed origins
            allowed_origins = os.getenv("ALLOWED_ORIGINS")
            if allowed_origins:
                self.security.allowed_origins = [origin.strip() for origin in allowed_origins.split(",")]
                
        except (ValueError, TypeError) as e:
            logger.error(f"Error loading configuration from environment: {e}")
            # Use lazy import to avoid circular dependency
            from .exceptions import ConfigurationError
            raise ConfigurationError(f"Invalid environment variable configuration: {e}")
    
    def _validate_startup(self):
        """Validate configuration at startup"""
        if not self.validate():
            from .exceptions import ConfigurationError
            raise ConfigurationError("Configuration validation failed")
        
        # Log configuration summary
        logger.info("Configuration loaded successfully")
        logger.info(f"TTS Device: {self.tts.device}")
        logger.info(f"API Host: {self.api.host}:{self.api.port}")
        logger.info(f"Cache Enabled: {self.cache.enabled}")
        logger.info(f"Monitoring Enabled: {self.monitoring.enabled}")
        logger.info(f"Security: API Key Required = {self.security.api_key_required}")
    
    def reload_from_env(self):
        """Reload configuration from environment variables"""
        logger.info("Reloading configuration from environment")
        self._load_from_env()
        self._validate_startup()
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        errors = []
        
        # Validate TTS config
        if not Path(self.tts.model_path).parent.exists():
            errors.append(f"Model directory does not exist: {Path(self.tts.model_path).parent}")
        
        if not Path(self.tts.voices_path).parent.exists():
            errors.append(f"Voices directory does not exist: {Path(self.tts.voices_path).parent}")
        
        if self.tts.sample_rate <= 0:
            errors.append(f"Invalid sample rate: {self.tts.sample_rate}")
        
        # Validate API config
        if not (1 <= self.api.port <= 65535):
            errors.append(f"Invalid port: {self.api.port}")
        
        if self.api.workers < 1:
            errors.append(f"Invalid worker count: {self.api.workers}")
        
        # Validate cache config
        if self.cache.max_size < 0:
            errors.append(f"Invalid cache max size: {self.cache.max_size}")
        
        if self.cache.ttl < 0:
            errors.append(f"Invalid cache TTL: {self.cache.ttl}")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "model": {
                "name": self.model.name,
                "type": self.model.type,
                "default_variant": self.model.default_variant,
                "available_variants": self.model.available_variants,
                "auto_discovery": self.model.auto_discovery,
                "cache_models": self.model.cache_models,
            },
            "voice": {
                "default_voice": self.voice.default_voice,
                "auto_discovery": self.voice.auto_discovery,
                "download_all_on_startup": self.voice.download_all_on_startup,
                "cache_discovery": self.voice.cache_discovery,
                "discovery_cache_hours": self.voice.discovery_cache_hours,
            },
            "audio": {
                "default_format": self.audio.default_format,
                "sample_rate": self.audio.sample_rate,
                "supported_formats": self.audio.supported_formats,
            },
            "server": {
                "port": self.server.port,
                "max_port_attempts": self.server.max_port_attempts,
                "host": self.server.host,
                "workers": self.server.workers,
                "environment": self.server.environment,
            },
            "performance": {
                "hot_reload": self.performance.hot_reload,
                "cache_enabled": self.performance.cache_enabled,
                "preload_models": self.performance.preload_models,
                "chunk_size": self.performance.chunk_size,
                "max_text_length": self.performance.max_text_length,
                "timeout_seconds": self.performance.timeout_seconds,
            },
            "repository": {
                "huggingface_repo": self.repository.huggingface_repo,
                "models_path": self.repository.models_path,
                "voices_path": self.repository.voices_path,
                "base_url": self.repository.base_url,
            },
            "paths": {
                "models_dir": self.paths.models_dir,
                "voices_dir": self.paths.voices_dir,
                "cache_dir": self.paths.cache_dir,
            },
            # Legacy configurations for backward compatibility
            "tts": {
                "model_path": self.tts.model_path,
                "voices_path": self.tts.voices_path,
                "default_voice": self.tts.default_voice,
                "sample_rate": self.tts.sample_rate,
                "chunk_size": self.tts.chunk_size,
                "device": self.tts.device,
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "workers": self.api.workers,
                "reload": self.api.reload,
                "log_level": self.api.log_level,
                "cors_origins": self.api.cors_origins,
            },
            "cache": {
                "enabled": self.cache.enabled,
                "max_size": self.cache.max_size,
                "ttl": self.cache.ttl,
                "voice_cache_size": self.cache.voice_cache_size,
                "audio_cache_size": self.cache.audio_cache_size,
            },
            "logging": {
                "level": self.logging.level,
                "file_path": self.logging.file_path,
                "max_file_size": self.logging.max_file_size,
                "backup_count": self.logging.backup_count,
            },
            "monitoring": {
                "enabled": self.monitoring.enabled,
                "metrics_endpoint": self.monitoring.metrics_endpoint,
                "health_endpoint": self.monitoring.health_endpoint,
                "request_tracking": self.monitoring.request_tracking,
                "performance_logging": self.monitoring.performance_logging,
                "metrics_retention_days": self.monitoring.metrics_retention_days,
            },
            "security": {
                "api_key_required": self.security.api_key_required,
                "rate_limit_enabled": self.security.rate_limit_enabled,
                "rate_limit_requests": self.security.rate_limit_requests,
                "rate_limit_window": self.security.rate_limit_window,
                "max_text_length": self.security.max_text_length,
                "allowed_origins": self.security.allowed_origins,
            }
        }

    def save_to_json(self, filepath: Optional[str] = None) -> bool:
        """Save current configuration to JSON file"""
        try:
            if filepath is None:
                filepath = self.config_file
            else:
                filepath = Path(filepath)

            # Create directory if it doesn't exist
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Save only the new configuration sections (not legacy)
            config_data = {
                "model": {
                    "name": self.model.name,
                    "type": self.model.type,
                    "default_variant": self.model.default_variant,
                    "available_variants": self.model.available_variants,
                    "auto_discovery": self.model.auto_discovery,
                    "cache_models": self.model.cache_models,
                },
                "voice": {
                    "default_voice": self.voice.default_voice,
                    "auto_discovery": self.voice.auto_discovery,
                    "download_all_on_startup": self.voice.download_all_on_startup,
                    "cache_discovery": self.voice.cache_discovery,
                    "discovery_cache_hours": self.voice.discovery_cache_hours,
                },
                "audio": {
                    "default_format": self.audio.default_format,
                    "sample_rate": self.audio.sample_rate,
                    "supported_formats": self.audio.supported_formats,
                },
                "server": {
                    "port": self.server.port,
                    "max_port_attempts": self.server.max_port_attempts,
                    "host": self.server.host,
                    "workers": self.server.workers,
                    "environment": self.server.environment,
                },
                "performance": {
                    "hot_reload": self.performance.hot_reload,
                    "cache_enabled": self.performance.cache_enabled,
                    "preload_models": self.performance.preload_models,
                    "chunk_size": self.performance.chunk_size,
                    "max_text_length": self.performance.max_text_length,
                    "timeout_seconds": self.performance.timeout_seconds,
                },
                "repository": {
                    "huggingface_repo": self.repository.huggingface_repo,
                    "models_path": self.repository.models_path,
                    "voices_path": self.repository.voices_path,
                    "base_url": self.repository.base_url,
                },
                "paths": {
                    "models_dir": self.paths.models_dir,
                    "voices_dir": self.paths.voices_dir,
                    "cache_dir": self.paths.cache_dir,
                }
            }

            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Configuration saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save configuration to {filepath}: {e}")
            return False

# Global configuration instance - prioritize comprehensive settings file
config = ConfigManager()

# Alias for backward compatibility
LiteTTSConfig = ConfigManager