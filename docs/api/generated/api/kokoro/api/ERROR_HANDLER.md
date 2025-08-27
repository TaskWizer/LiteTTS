# error_handler.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Error handling for TTS API


## Class: ErrorHandler

Handles errors and exceptions in the TTS API

### __init__()

### handle_synthesis_error()

Handle synthesis-related errors

### handle_validation_error()

Handle request validation errors

### handle_rate_limit_error()

Handle rate limiting errors

### handle_timeout_error()

Handle request timeout errors

### handle_service_unavailable()

Handle service unavailable errors

### handle_generic_error()

Handle generic/unexpected errors

### handle_not_found_error()

Handle resource not found errors

### handle_method_not_allowed()

Handle method not allowed errors

### _create_error_response()

Create standardized error response

### _log_error()

Log error with appropriate level

### _log_validation_error()

Log validation errors

### _get_timestamp()

Get current timestamp

### get_error_stats()

Get error statistics

### reset_error_stats()

Reset error statistics

## Class: APIExceptionHandler

Global exception handler for the API

### __init__()

