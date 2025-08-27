# Monitoring & Observability

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

Comprehensive monitoring and observability features for production deployments of the Kokoro ONNX TTS API.

## Overview

The Kokoro ONNX TTS API includes comprehensive monitoring and observability features designed for production deployments, providing real-time insights into system performance, health, and reliability.

## Health Monitoring

### System Health Checks

**Component Status Monitoring:**
- **TTS Engine**: Real-time monitoring of model loading and inference
- **Cache System**: Cache hit rates, memory usage, and performance
- **Voice Manager**: Voice loading status and availability
- **Watermarking**: Perth watermarking system status
- **Resource Monitoring**: CPU, memory, disk space, and network health

### Health Endpoints

```bash
# Overall system health
curl http://localhost:8354/health

# Detailed health report with component breakdown
curl http://localhost:8354/health/detailed

# Component-specific health checks
curl http://localhost:8354/health/components

# Watermarking system health
curl http://localhost:8354/health/watermarking

# Voice system health
curl http://localhost:8354/health/voices
```

### Health Response Format

```json
{
  "status": "healthy",
  "timestamp": "2025-08-18T00:00:00Z",
  "model": "kokoro/models/model_q4.onnx",
  "model_loaded": true,
  "voices_available": 55,
  "uptime_seconds": 3600,
  "components": {
    "tts_engine": "healthy",
    "voice_manager": "healthy",
    "cache_system": "healthy",
    "watermarking": "healthy",
    "monitoring": "healthy"
  },
  "performance": {
    "avg_response_time_ms": 250,
    "requests_per_minute": 120,
    "cache_hit_rate": 0.85
  }
}
```

## Performance Monitoring

### Real-time Metrics

**Response Time Metrics:**
- **P50 Latency**: Median response time
- **P95 Latency**: 95th percentile response time
- **P99 Latency**: 99th percentile response time
- **Average Response Time**: Mean response time across all requests

**Throughput Metrics:**
- **Requests per Second**: Current request rate
- **Concurrent Users**: Active concurrent connections
- **Queue Length**: Pending request queue size
- **Processing Rate**: TTS generation rate

**Cache Performance:**
- **Hit Rate**: Percentage of cache hits
- **Miss Rate**: Percentage of cache misses
- **Cache Size**: Current cache memory usage
- **Eviction Rate**: Cache entry eviction frequency

### Performance Dashboard

```bash
# Access web-based monitoring dashboard
http://localhost:8354/dashboard

# Performance metrics API endpoint
curl http://localhost:8354/metrics

# Prometheus-compatible metrics export
curl http://localhost:8354/metrics/prometheus

# JSON metrics for custom integrations
curl http://localhost:8354/metrics/json
```

### Performance Metrics Example

```json
{
  "timestamp": "2025-08-18T00:00:00Z",
  "response_times": {
    "p50_ms": 180,
    "p95_ms": 450,
    "p99_ms": 800,
    "avg_ms": 220
  },
  "throughput": {
    "requests_per_second": 25.5,
    "requests_per_minute": 1530,
    "concurrent_users": 12
  },
  "cache": {
    "hit_rate": 0.87,
    "miss_rate": 0.13,
    "size_mb": 245,
    "entries": 1250
  },
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 62.8,
    "disk_usage_percent": 23.1
  }
}
```

## Fault Tolerance

### Built-in Resilience Features

**Circuit Breaker Pattern:**
- **Automatic Failure Detection**: Monitors error rates and response times
- **Circuit States**: Closed, Open, Half-Open states
- **Recovery Mechanism**: Automatic recovery testing
- **Configurable Thresholds**: Customizable failure thresholds

**Retry Logic:**
- **Exponential Backoff**: Intelligent retry delays
- **Maximum Attempts**: Configurable retry limits
- **Transient Failure Handling**: Automatic retry for temporary issues
- **Dead Letter Queue**: Failed request logging

**Graceful Degradation:**
- **Fallback Mechanisms**: Alternative processing paths
- **Partial Functionality**: Core features remain available
- **Resource Protection**: Prevents system overload
- **User Experience**: Maintains service availability

### Configuration

```json
{
  "monitoring": {
    "health_check_interval": 30,
    "performance_monitoring": true,
    "circuit_breaker_enabled": true,
    "circuit_breaker": {
      "failure_threshold": 5,
      "recovery_timeout": 60,
      "half_open_max_calls": 3
    },
    "retry_policy": {
      "max_attempts": 3,
      "base_delay_ms": 100,
      "max_delay_ms": 5000,
      "exponential_base": 2
    },
    "graceful_degradation": true
  }
}
```

## Logging & Observability

### Structured Logging

**Log Format:**
- **JSON Structure**: Machine-readable log entries
- **Correlation IDs**: End-to-end request tracking
- **Contextual Information**: Rich metadata for debugging
- **Performance Data**: Timing and resource usage

**Log Levels:**
- **DEBUG**: Detailed debugging information
- **INFO**: General operational information
- **WARN**: Warning conditions and recoverable errors
- **ERROR**: Error conditions requiring attention
- **CRITICAL**: Critical errors requiring immediate action

### Log Configuration

```bash
# Set log level
export KOKORO_LOG_LEVEL=INFO

# Enable structured logging (JSON format)
export KOKORO_STRUCTURED_LOGGING=true

# Configure log file location
export KOKORO_LOG_FILE=logs/kokoro_tts.log

# Enable performance logging
export KOKORO_PERFORMANCE_LOGGING=true

# Set log rotation
export KOKORO_LOG_ROTATION=daily
```

### Log Files

```
docs/logs/
├── main.log              # General application logs
├── performance.log       # Performance metrics and timing
├── cache.log            # Cache operations and statistics
├── errors.log           # Error logs and stack traces
└── structured.log       # JSON-formatted structured logs
```

### Sample Log Entry

```json
{
  "timestamp": "2025-08-18T00:00:00.000Z",
  "level": "INFO",
  "logger": "kokoro.tts.engine",
  "message": "TTS request completed successfully",
  "correlation_id": "req_123456789",
  "request": {
    "voice": "af_heart",
    "text_length": 50,
    "format": "mp3"
  },
  "performance": {
    "processing_time_ms": 245,
    "cache_hit": true,
    "watermark_time_ms": 0.44
  },
  "system": {
    "cpu_percent": 45.2,
    "memory_mb": 1024
  }
}
```

## Production Monitoring

### Key Metrics to Monitor

**Availability Metrics:**
- **System Uptime**: Overall system availability
- **Health Check Status**: Component health status
- **Error Rate**: Percentage of failed requests
- **Service Degradation**: Partial functionality events

**Performance Metrics:**
- **Response Times**: Latency percentiles and averages
- **Throughput**: Request rates and processing capacity
- **Resource Utilization**: CPU, memory, and disk usage
- **Cache Effectiveness**: Hit rates and performance impact

**Business Metrics:**
- **Request Volume**: Total requests processed
- **Voice Usage**: Popular voices and usage patterns
- **Feature Adoption**: SSML, watermarking, and advanced features
- **User Satisfaction**: Error rates and performance metrics

### Alerting Integration

**Prometheus Integration:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'kokoro-tts'
    static_configs:
      - targets: ['localhost:8354']
    metrics_path: '/metrics/prometheus'
    scrape_interval: 15s
```

**Grafana Dashboard:**
- **Pre-built Templates**: Ready-to-use dashboard configurations
- **Custom Metrics**: Configurable charts and alerts
- **Real-time Monitoring**: Live performance visualization
- **Historical Analysis**: Trend analysis and capacity planning

**Custom Webhooks:**
```json
{
  "alerting": {
    "webhooks": [
      {
        "name": "slack_alerts",
        "url": "https://hooks.slack.com/services/...",
        "events": ["error", "degradation", "recovery"]
      }
    ],
    "thresholds": {
      "error_rate": 0.05,
      "response_time_p95": 1000,
      "cpu_usage": 0.8,
      "memory_usage": 0.9
    }
  }
}
```

## Monitoring Dashboard

### Web Interface

Access the monitoring dashboard at: `http://localhost:8354/dashboard`

**Dashboard Features:**
- **Real-time Metrics**: Live performance data
- **System Health**: Component status overview
- **Performance Charts**: Response time and throughput graphs
- **Resource Usage**: CPU, memory, and disk utilization
- **Cache Statistics**: Hit rates and cache performance
- **Error Tracking**: Error rates and recent failures

### API Endpoints

```bash
# Dashboard data API
curl http://localhost:8354/api/dashboard/data

# Real-time metrics stream
curl http://localhost:8354/api/metrics/stream

# Historical data
curl http://localhost:8354/api/metrics/history?hours=24

# System status summary
curl http://localhost:8354/api/status/summary
```

## Best Practices

### Production Deployment

1. **Enable All Monitoring**: Activate comprehensive monitoring features
2. **Set Up Alerting**: Configure alerts for critical metrics
3. **Monitor Trends**: Track performance trends over time
4. **Capacity Planning**: Use metrics for scaling decisions
5. **Regular Health Checks**: Implement automated health monitoring

### Performance Optimization

1. **Monitor Cache Performance**: Optimize cache hit rates
2. **Track Resource Usage**: Prevent resource exhaustion
3. **Analyze Response Times**: Identify performance bottlenecks
4. **Monitor Error Patterns**: Proactively address issues
5. **Capacity Monitoring**: Plan for traffic growth

### Troubleshooting

1. **Use Correlation IDs**: Track requests end-to-end
2. **Analyze Log Patterns**: Identify recurring issues
3. **Monitor System Resources**: Check for resource constraints
4. **Review Performance Metrics**: Identify degradation patterns
5. **Check Component Health**: Isolate failing components

## Support

For monitoring-related issues:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review [Configuration Guide](CONFIGURATION.md)
3. Open an issue on [GitHub](https://github.com/TaskWizer/LiteTTS/issues)
