# dashboard.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


API Analytics & Concurrency Dashboard

Provides real-time monitoring and analytics for the TTS API including:
- Request metrics (requests per minute/hour, response times)
- Concurrency metrics (active connections, queue status)
- Performance statistics (latency, RTF)
- Voice usage statistics
- Error rates and status codes


## Class: RequestMetric

Individual request metric

## Class: ConcurrencyMetric

Concurrency tracking metric

## Class: DashboardAnalytics

Real-time analytics collector for the dashboard

Tracks all API requests, performance metrics, and system status
for display in the web dashboard.

### __init__()

### record_request()

Record a completed request

### update_concurrency()

Update concurrency metrics

### get_requests_per_minute()

Get requests per minute for the last N minutes

### get_response_time_stats()

Get response time statistics

### get_error_rates()

Get error rates and status code distribution

### get_voice_usage_stats()

Get voice usage statistics

### get_concurrency_stats()

Get current concurrency statistics

### get_dashboard_data()

Get comprehensive dashboard data

### _start_cleanup_task()

Start background task to clean up old metrics

