# Model Performance Benchmark Report
Generated: 2025-08-28 00:04:25

## Summary
| Model | RTF | Memory (MB) | Quality | Success Rate |
|-------|-----|-------------|---------|--------------|
| model_q4 | ✅ 0.203 | ✅ 43.8 | 75.6 | 100.0% |

## model_q4
**Model Size:** 291.1 MB
**Initialization Time:** 100.1 ms
**Warmup Time:** 50.1 ms

### Performance Metrics
- **Average RTF:** 0.203 (target: <0.25)
- **P95 RTF:** 0.210
- **RTF Range:** 0.200 - 0.229
- **Average Latency:** 802.4 ms
- **P95 Latency:** 2067.8 ms

### Memory Usage
- **Baseline Memory:** 36.1 MB
- **Peak Memory:** 43.8 MB (target: <150MB)
- **Memory Overhead:** 7.7 MB

### Quality Metrics
- **Audio Quality Score:** 75.6/100
- **Pronunciation Accuracy:** 95.0%
- **Prosody Score:** 80.0%

### Performance by Text Length
- **Short Text RTF:** 0.207
- **Medium Text RTF:** 0.201
- **Long Text RTF:** 0.201

### Test Statistics
- **Total Tests:** 15
- **Successful:** 15
- **Failed:** 0
- **Success Rate:** 100.0%
- **Throughput:** 99.4 chars/sec
