# Dynamic CPU Allocation for Kokoro TTS API

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

## Overview

The Kokoro TTS API now includes dynamic CPU core allocation that automatically adjusts CPU resource usage based on real-time system utilization. This feature optimizes performance while maintaining efficient resource usage.

## Features

### Real-time CPU Monitoring
- **Continuous Monitoring**: Tracks CPU utilization every second
- **Single Target Threshold**: Simple, intuitive CPU target (default 75%)
- **Hysteresis Protection**: Prevents oscillation with automatic scale-down threshold
- **History Tracking**: Maintains rolling window of utilization samples
- **Average-based Decisions**: Uses averaged utilization to reduce noise

### Dynamic Core Allocation
- **Single-Threshold Logic**: Scale up when utilization > target, scale down when < (target × hysteresis)
- **Automatic Hysteresis**: Scale-down threshold = target × 0.6 (prevents oscillation)
- **Bounded Allocation**: Respects min/max core limits (1 to total_cores-1)
- **Cooldown Period**: 5-second minimum between allocation changes
- **Thread Optimization**: Automatically calculates optimal inter_op and intra_op threads

### ONNX Runtime Integration
- **Seamless Integration**: Automatically applies allocation to new ONNX sessions
- **Fallback Support**: Falls back to static CPU optimizer if dynamic allocation fails
- **Environment Variables**: Updates threading environment variables in real-time

## Single-Threshold Design

### Simplified Approach
The dynamic CPU allocation uses a **single, intuitive threshold** instead of complex dual thresholds:

- **`cpu_target`**: The maximum CPU utilization you want to maintain (e.g., 75%)
- **Automatic Hysteresis**: Scale-down threshold = `cpu_target × hysteresis_factor` (e.g., 75% × 0.6 = 45%)

### Algorithm Logic
```
if utilization > cpu_target:
    → Scale UP (add cores to reduce load per core)
elif utilization < (cpu_target × hysteresis_factor):
    → Scale DOWN (remove cores when significantly underutilized)
else:
    → STABLE ZONE (maintain current allocation)
```

### Benefits Over Dual-Threshold
- **Intuitive**: Single parameter "keep CPU below X%"
- **No Configuration Confusion**: No need to understand min/max threshold relationships
- **Automatic Hysteresis**: Prevents oscillation without manual tuning
- **Responsive**: Smaller stable zone means better adaptation to load changes

## Configuration

### config.json Settings

```json
{
  "performance": {
    "dynamic_cpu_allocation": {
      "enabled": true,
      "cpu_target": 75.0,
      "hysteresis_factor": 0.6,
      "monitoring_interval": 1.0,
      "history_window": 10,
      "allocation_cooldown": 5.0,
      "min_cores": 1,
      "max_cores": null,
      "aggressive_mode": false,
      "thermal_protection": true,
      "onnx_integration": true,
      "update_environment": true
    }
  }
}
```

### Choosing the Optimal CPU Target

| Workload Type | Recommended `cpu_target` | Reasoning |
|---------------|-------------------------|-----------|
| **Development** | `60-70%` | Lower threshold for responsive development |
| **Production (Balanced)** | `75%` | Good balance of performance and efficiency |
| **High-Throughput** | `80-85%` | Maximize resource utilization |
| **Latency-Critical** | `65-70%` | Keep headroom for request spikes |
| **Container/Shared** | `70-75%` | Leave resources for other processes |

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable dynamic CPU allocation |
| `cpu_target` | float | `75.0` | Target maximum CPU utilization threshold (%) |
| `hysteresis_factor` | float | `0.6` | Scale-down threshold factor (cpu_target × hysteresis_factor) |
| `monitoring_interval` | float | `1.0` | CPU monitoring interval (seconds) |
| `history_window` | int | `10` | Number of utilization samples to average |
| `allocation_cooldown` | float | `5.0` | Minimum time between allocation changes (seconds) |
| `min_cores` | int | `1` | Minimum number of cores to allocate |
| `max_cores` | int | `null` | Maximum cores (null = auto-detect as total-1) |
| `aggressive_mode` | boolean | `false` | Enable aggressive CPU optimization |
| `thermal_protection` | boolean | `true` | Enable thermal throttling protection |
| `onnx_integration` | boolean | `true` | Apply allocation to ONNX Runtime sessions |
| `update_environment` | boolean | `true` | Update threading environment variables |

## API Endpoints

### CPU Allocation Diagnostics

**Endpoint**: `GET /diagnostics/cpu-allocation`

**Response Example**:
```json
{
  "status": "success",
  "dynamic_allocation_enabled": true,
  "allocation_stats": {
    "monitoring_active": true,
    "total_cores": 20,
    "current_allocation": {
      "allocated_cores": 1,
      "inter_op_threads": 1,
      "intra_op_threads": 1,
      "utilization_percent": 10.91,
      "allocation_reason": "optimal_range_10.9%",
      "timestamp": 1755571329.824
    },
    "thresholds": {
      "cpu_target": 75.0,
      "scale_up_threshold": 75.0,
      "scale_down_threshold": 45.0,
      "hysteresis_factor": 0.6,
      "monitoring_interval": 1.0
    },
    "utilization_history": [27.4, 15.7, 4.5, 5.0, 27.0, 8.5, 5.1, 6.9, 5.5, 3.5],
    "average_utilization": 10.91
  },
  "recommended_settings": {
    "workers": 1,
    "onnx_inter_op_threads": 1,
    "onnx_intra_op_threads": 1,
    "batch_size": 1,
    "concurrent_requests": 2,
    "allocated_cores": 1
  },
  "system_info": {
    "total_cpu_cores": 20,
    "current_pid": 1
  }
}
```

## Performance Impact

### Benchmarks
- **RTF Performance**: Maintains < 0.25 RTF (target < 0.2)
- **Memory Overhead**: < 50MB additional memory usage
- **CPU Efficiency**: Optimizes core usage based on actual load
- **Response Time**: No measurable impact on API response times

### Resource Usage
- **Monitoring Thread**: Single background thread for CPU monitoring
- **Memory Footprint**: Minimal additional memory for utilization history
- **CPU Overhead**: < 0.1% CPU usage for monitoring itself

## Architecture

### Components

1. **CPUUtilizationMonitor**: Real-time CPU monitoring and history tracking
2. **DynamicCPUAllocator**: Core allocation logic and ONNX integration
3. **Configuration Integration**: Seamless config.json integration
4. **ONNX Runtime Patches**: Automatic application to new sessions

### Thread Safety
- **Thread-safe Operations**: All allocation changes are thread-safe
- **Lock-based Synchronization**: Uses RLock for critical sections
- **Callback System**: Safe callback mechanism for allocation changes

## Deployment

### Local Development
```bash
# Start with dynamic allocation enabled
uv run python app.py --port 8354
```

### Docker Deployment
```bash
# Build with dynamic allocation support
docker build -t kokoro-tts-dynamic .

# Run with dynamic allocation
docker run -d --name kokoro-tts -p 8354:8354 kokoro-tts-dynamic
```

### Environment Variables
The system automatically sets these environment variables based on allocation:
- `OMP_NUM_THREADS`
- `OPENBLAS_NUM_THREADS`
- `MKL_NUM_THREADS`
- `NUMEXPR_NUM_THREADS`

## Monitoring and Debugging

### Log Messages
```
INFO | Dynamic CPU Allocator initialized: cores=1-19, aggressive=False
INFO | CPU Monitor initialized: 20 cores available
INFO | CPU utilization monitoring started
INFO | Dynamic CPU allocation monitoring initialized
INFO | CPU allocation changed: 1 → 2 cores (utilization: 85.2%, reason: high_utilization_85.2%)
```

### Diagnostic Endpoint
Use `/diagnostics/cpu-allocation` to monitor:
- Current core allocation
- CPU utilization history
- Allocation reasons
- Performance recommendations

## Troubleshooting

### Common Issues

1. **Dynamic allocation not working**
   - Check `enabled: true` in config.json
   - Verify psutil is installed
   - Check logs for initialization errors

2. **Allocation not changing under load**
   - Check if utilization crosses thresholds (25%/80%)
   - Verify cooldown period (5 seconds) has passed
   - Check thermal protection status

3. **Performance degradation**
   - Monitor allocation changes in logs
   - Check if thermal protection is reducing cores
   - Verify ONNX integration is working

### Legacy Configuration Migration

The system automatically migrates old dual-threshold configurations:

**Old Format (Deprecated):**
```json
{
  "dynamic_cpu_allocation": {
    "min_threshold": 25.0,
    "max_threshold": 80.0
  }
}
```

**New Format (Recommended):**
```json
{
  "dynamic_cpu_allocation": {
    "cpu_target": 80.0,
    "hysteresis_factor": 0.6
  }
}
```

**Auto-Migration**: If old format detected, `cpu_target = max_threshold` and `hysteresis_factor = 0.6`

### Configuration Override
Use `override.json` to modify settings without changing main config:
```json
{
  "performance": {
    "dynamic_cpu_allocation": {
      "cpu_target": 70.0,
      "hysteresis_factor": 0.7,
      "aggressive_mode": true
    }
  }
}
```

## Integration with Existing Features

### Advanced Text Processing
- **Compatibility**: Fully compatible with UnifiedTextProcessor
- **Performance**: No impact on text processing performance
- **Resource Sharing**: Efficiently shares CPU resources

### Voice Processing
- **Voice Loading**: Optimizes CPU usage during voice loading
- **Cache Management**: Works with existing voice caching
- **Memory Management**: Coordinates with voice memory management

### Performance Monitoring
- **Metrics Integration**: Integrates with existing performance monitoring
- **Cache Statistics**: Works with cache performance tracking
- **System Monitoring**: Enhances overall system monitoring

## Future Enhancements

### Planned Features
- **GPU Integration**: Extend to GPU resource allocation
- **Memory-based Allocation**: Consider memory usage in allocation decisions
- **Load Prediction**: Predictive allocation based on request patterns
- **Multi-instance Coordination**: Coordinate allocation across multiple instances

### Advanced Configuration
- **Per-voice Optimization**: Different allocation strategies per voice
- **Time-based Profiles**: Different allocation profiles for different times
- **Request-type Optimization**: Optimize allocation based on request characteristics
