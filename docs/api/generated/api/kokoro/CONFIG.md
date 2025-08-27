# config.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../FEATURES.md) | [Configuration](../../../../CONFIGURATION.md) | [Performance](../../../../PERFORMANCE.md) | [Monitoring](../../../../MONITORING.md) | [Testing](../../../../TESTING.md) | [Troubleshooting](../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../DEPENDENCIES.md) | [Quick Start](../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../API_REFERENCE.md) | [Development](../../../../development/README.md) | [Voice System](../../../../voices/README.md) | [Watermarking](../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../CHANGELOG.md) | [Roadmap](../../../../ROADMAP.md) | [Contributing](../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../BETA_FEATURES.md)

---


Configuration management for Kokoro ONNX TTS API


## Class: ModelConfig

Model configuration

### __post_init__()

## Class: VoiceConfig

Voice configuration

### __post_init__()

## Class: AudioConfig

Audio configuration

### __post_init__()

## Class: ServerConfig

Server configuration

## Class: PerformanceConfig

Performance configuration

## Class: RepositoryConfig

Repository configuration

## Class: PathsConfig

Paths configuration

## Class: TokenizerConfig

Tokenizer configuration

## Class: EndpointsConfig

API endpoints configuration

## Class: ApplicationConfig

Application metadata configuration

## Class: TTSConfig

Legacy TTS engine configuration for backward compatibility

## Class: APIConfig

API server configuration

### __post_init__()

## Class: CacheConfig

Caching configuration

## Class: MonitoringConfig

Performance monitoring configuration

## Class: LoggingConfig

Logging configuration

## Class: MetricsConfig

Monitoring and metrics configuration

## Class: SecurityConfig

Security configuration

### __post_init__()

## Class: ConfigManager

Central configuration manager with comprehensive environment variable support

### __init__()

### _load_from_json()

Load configuration from JSON file

### _update_legacy_configs()

Update legacy configurations with new values for backward compatibility

### _load_from_env()

Load configuration from environment variables with type safety

### _validate_startup()

Validate configuration at startup

### reload_from_env()

Reload configuration from environment variables

### validate()

Validate configuration settings

### to_dict()

Convert configuration to dictionary

### save_to_json()

Save current configuration to JSON file

