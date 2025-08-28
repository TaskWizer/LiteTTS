# End-to-End Performance Audit Report
Generated: 2025-08-28 00:04:36

## Executive Summary
**Performance Grade: A**
- RTF: 0.173 (target: <0.25) ✅
- Memory: 45.5MB (target: <150MB) ✅
- Success Rate: 16/16 (100.0%)

## Bottleneck Analysis
**Primary Bottleneck:** Audio Generation
**Secondary Bottleneck:** Caching

**Recommendations:**
- System performance is well-optimized

## Component Performance
### Text Processing
- Processing Time: 27.5ms (P95: 92.7ms)
- Memory Usage: 35.8MB
- CPU Usage: 15.0%
- Throughput: 36.4 ops/sec
- Error Rate: 0.0%
- Bottleneck Score: 2.7/100

### Audio Generation
- Processing Time: 437.4ms (P95: 1465.6ms)
- Memory Usage: 41.8MB
- CPU Usage: 60.0%
- Throughput: 2.3 ops/sec
- Error Rate: 0.0%
- Bottleneck Score: 48.7/100

### Caching
- Processing Time: 3.5ms (P95: 5.1ms)
- Memory Usage: 43.0MB
- CPU Usage: 5.0%
- Throughput: 282.8 ops/sec
- Error Rate: 0.0%
- Bottleneck Score: 20.0/100

### Memory Management
- Processing Time: 14.9ms (P95: 15.0ms)
- Memory Usage: 43.0MB
- CPU Usage: 10.0%
- Throughput: 100.0 ops/sec
- Error Rate: 0.0%
- Bottleneck Score: 7.5/100
