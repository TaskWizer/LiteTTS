# logging_config.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../FEATURES.md) | [Configuration](../../../../CONFIGURATION.md) | [Performance](../../../../PERFORMANCE.md) | [Monitoring](../../../../MONITORING.md) | [Testing](../../../../TESTING.md) | [Troubleshooting](../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../DEPENDENCIES.md) | [Quick Start](../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../API_REFERENCE.md) | [Development](../../../../development/README.md) | [Voice System](../../../../voices/README.md) | [Watermarking](../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../CHANGELOG.md) | [Roadmap](../../../../ROADMAP.md) | [Contributing](../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../BETA_FEATURES.md)

---


Logging configuration for Kokoro ONNX TTS API


## Class: PerformanceFilter

Filter for performance-related log messages

### filter()

## Class: CacheFilter

Filter for cache-related log messages

### filter()

## Function: setup_logging()

Set up structured logging for the application with enhanced features

Args:
    level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format_string: Custom format string for log messages
    file_path: Optional file path for log output
    max_file_size: Maximum size of log file before rotation
    backup_count: Number of backup files to keep
    json_format: Use JSON format for structured logging
    include_trace_id: Include trace ID in log messages

## Class: ColoredFormatter

Custom formatter with color support for console output

### format()

## Class: JSONFormatter

JSON formatter for structured logging

### format()

## Class: RequestLogger

Enhanced context manager for request-specific logging with metrics

### __init__()

### __enter__()

### __exit__()

### info()

### error()

### warning()

### debug()

### add_metric()

Add a metric to be logged with the request

### add_context()

Add context information to be logged with the request

## Function: get_request_logger()

Get a request-specific logger with optional context

## Function: setup_performance_logging()

Set up performance-specific logging

## Function: log_system_info()

Log system information at startup

