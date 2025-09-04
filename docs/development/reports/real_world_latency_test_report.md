# Real-World Latency Test Report
Generated: 2025-08-28 00:13:40

## Executive Summary
**Cold Start Latency:** 562.2ms
**Warm Request Latency:** 304.0ms
**Latency Target (500ms):** ✅ MEETS TARGET

## Detailed Test Results
| Test | Avg Latency | P95 | P99 | Min | Max | Success Rate | Throughput |
|------|-------------|-----|-----|-----|-----|--------------|------------|
| Health Endpoint | 1.3ms | 3.1ms | 7.0ms | 0.6ms | 8.0ms | 100.0% | 2508.87 RPS |
| TTS Cold Start | 562.2ms | 562.2ms | 562.2ms | 562.2ms | 562.2ms | 100.0% | 1.78 RPS |
| TTS Warm Requests | 304.0ms | 823.3ms | 977.3ms | 25.8ms | 1015.7ms | 100.0% | 3.29 RPS |
| Concurrent Requests | 132.9ms | 138.1ms | 138.7ms | 129.9ms | 138.9ms | 100.0% | 36.00 RPS |

## Analysis
**Cold Start Penalty:** 258.2ms
✅ **Low cold start penalty** - model warm-up is working well

## Recommendations
1. **Latency performance is good** - meets 500ms target