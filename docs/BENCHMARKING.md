# LiteTTS Comprehensive Benchmarking Guide

## Overview

The LiteTTS Benchmarking System provides comprehensive performance analysis, quality metrics, and optimization guidance for all model variants. This system helps you choose the optimal configuration for your specific deployment requirements, from edge devices to high-performance servers.

### Key Features

- **🚀 Performance Metrics**: RTF (Real-Time Factor), latency, throughput analysis
- **🎵 Audio Quality Assessment**: PESQ, STOI, and perceptual quality metrics
- **💾 Resource Monitoring**: Memory usage, CPU utilization, disk I/O
- **📊 Comparative Analysis**: Side-by-side model variant comparisons
- **🎯 Optimization Recommendations**: Deployment-specific guidance
- **📈 Trend Analysis**: Performance tracking over time

## Model Variants

LiteTTS supports 8 different model variants, each optimized for different performance characteristics:

| Model Variant | Description | Use Case |
|---------------|-------------|----------|
| `model.onnx` | Base model with full precision | Highest quality, research |
| `model_f16.onnx` | Half-precision floating point | Balanced quality/performance |
| `model_q4.onnx` | 4-bit quantized | Fast inference, mobile |
| `model_q4f16.onnx` | 4-bit quantized with 16-bit weights | Optimized mobile |
| `model_q8f16.onnx` | 8-bit quantized with 16-bit weights | Production balance |
| `model_quantized.onnx` | General quantized model | Standard production |
| `model_uint8.onnx` | 8-bit unsigned integer | Edge devices |
| `model_uint8f16.onnx` | 8-bit unsigned with 16-bit weights | Optimized edge |

## Performance Metrics Overview

### Real-Time Factor (RTF)
The RTF measures how fast audio is generated compared to real-time playback:
- **RTF < 1.0**: Faster than real-time (ideal for production)
- **RTF = 1.0**: Real-time generation
- **RTF > 1.0**: Slower than real-time

**LiteTTS Typical RTF Values:**
- `model_q4.onnx`: ~0.15 RTF (6.7x faster than real-time)
- `model_f16.onnx`: ~0.25 RTF (4x faster than real-time)
- `model.onnx`: ~0.45 RTF (2.2x faster than real-time)

### Quality Metrics
- **PESQ Score**: Perceptual Evaluation of Speech Quality (1.0-4.5, higher is better)
- **STOI Score**: Short-Time Objective Intelligibility (0.0-1.0, higher is better)
- **MOS Estimation**: Mean Opinion Score estimation (1.0-5.0, higher is better)

### Resource Utilization
- **Memory Usage**: Peak and average RAM consumption
- **CPU Utilization**: Average CPU usage during synthesis
- **Model Size**: Disk space requirements for each variant

## Quick Start

### Automated Benchmarking

Run the complete benchmarking suite with a single command:

```bash
# Basic benchmark with all models
./LiteTTS/scripts/benchmarking/run_benchmark.sh

# Run benchmark and open HTML report
./LiteTTS/scripts/benchmarking/run_benchmark.sh --open

# Custom results directory
./LiteTTS/scripts/benchmarking/run_benchmark.sh --results-dir /path/to/results

# Benchmark specific model variant
./LiteTTS/scripts/benchmarking/run_benchmark.sh --model model_q4.onnx

# Quick benchmark (reduced test set)
./LiteTTS/scripts/benchmarking/run_benchmark.sh --quick
```

### Manual Benchmarking

For more control over the benchmarking process:

```bash
# Run benchmark only
uv run python LiteTTS/scripts/benchmarking/comprehensive_model_benchmark.py

# Generate reports from existing results
uv run python LiteTTS/scripts/benchmarking/generate_benchmark_report.py benchmark_report_20241222_143022.json
```

## Metrics Measured

### Performance Metrics
- **Inference Time**: Time taken to generate audio from text input (milliseconds)
- **Real-Time Factor (RTF)**: Ratio of inference time to audio duration (lower is better)
- **Throughput**: Estimated requests per second based on average inference time

### Resource Usage
- **Memory Usage**: Peak and average RAM consumption during synthesis
- **CPU Utilization**: Processor usage during synthesis

### Quality Metrics
- **Audio Samples**: Number of audio samples generated
- **Sample Rate**: Audio sample rate (Hz)
- **File Size**: Generated audio file size

## Understanding Results

### Real-Time Factor (RTF)
- **RTF < 1.0**: Faster than real-time (can generate audio faster than playback)
- **RTF = 1.0**: Real-time generation (generates audio at playback speed)
- **RTF > 1.0**: Slower than real-time (takes longer to generate than playback)

### Performance Trade-offs
- **Speed vs Quality**: Quantized models are faster but may have slightly lower quality
- **Memory vs Performance**: Smaller models use less memory but may be slower
- **Precision vs Size**: Higher precision models are larger but potentially more accurate

## Use Case Recommendations

### Real-Time Applications
**Recommended**: `model_q4.onnx` or `model_uint8.onnx`
- Interactive voice assistants
- Live streaming applications
- Real-time communication systems

### Batch Processing
**Recommended**: `model.onnx` or `model_f16.onnx`
- Audiobook generation
- Large-scale content creation
- Offline processing workflows

### Resource-Constrained Environments
**Recommended**: `model_uint8.onnx` or `model_q4.onnx`
- Mobile applications
- Edge devices
- Embedded systems

### High-Quality Production
**Recommended**: `model.onnx` or `model_f16.onnx`
- Professional audio production
- Commercial applications
- High-fidelity requirements

## Benchmark Configuration

### Test Parameters
- **Test Texts**: 8 standardized text samples of varying lengths
- **Voices**: 4 different voice models (af_heart, am_puck, af_sarah, am_liam)
- **Iterations**: Multiple runs per configuration for statistical accuracy

### Customization
You can customize the benchmark by modifying:
- Test texts in `comprehensive_model_benchmark.py`
- Voice selection
- Number of iterations
- Monitoring frequency

## Output Files

The benchmarking system generates several output files:

### JSON Files
- `benchmark_results_TIMESTAMP.json`: Detailed raw results
- `benchmark_summaries_TIMESTAMP.json`: Statistical summaries
- `benchmark_report_TIMESTAMP.json`: Comprehensive analysis

### Reports
- `benchmark_report_TIMESTAMP.md`: Markdown report
- `benchmark_report_TIMESTAMP.html`: Interactive HTML report

### Logs
- `benchmark_results.log`: Execution logs and debug information

## Interpreting HTML Reports

The HTML report provides:
- **Executive Summary**: Key metrics and performance leaders
- **Performance Comparison Table**: Side-by-side model comparison
- **Detailed Analysis**: Per-model statistics and recommendations
- **Interactive Elements**: Sortable tables and visual indicators

## Troubleshooting

### Common Issues

#### Benchmark Fails to Start
```bash
# Check prerequisites
python3 --version
ls -la config.json
```

#### Memory Errors
- Reduce number of test iterations
- Close other applications
- Use smaller model variants first

#### Inconsistent Results
- Ensure system is not under load
- Run multiple benchmark sessions
- Check for thermal throttling

### Performance Tips
- Close unnecessary applications during benchmarking
- Ensure adequate system cooling
- Use consistent system load conditions
- Run benchmarks multiple times for accuracy

## Advanced Usage

### Custom Test Scenarios
Create custom benchmark scenarios by modifying the test parameters:

```python
# Custom text samples
custom_texts = [
    "Your custom test text here",
    "Another test scenario",
]

# Custom voice selection
custom_voices = ["specific_voice_id"]
```

### Integration with CI/CD
Integrate benchmarking into your development workflow:

```yaml
# GitHub Actions example
- name: Run Model Benchmarks
  run: |
    ./LiteTTS/scripts/benchmarking/run_benchmark.sh --quiet
    # Upload results to artifacts
```

## Best Practices

1. **Consistent Environment**: Run benchmarks in consistent system conditions
2. **Multiple Runs**: Execute multiple benchmark sessions for statistical accuracy
3. **Documentation**: Document your benchmark configurations and results
4. **Version Control**: Track benchmark results across model versions
5. **Automation**: Integrate benchmarking into your development workflow

## Contributing

To improve the benchmarking system:
1. Add new test scenarios
2. Enhance metrics collection
3. Improve report visualization
4. Add platform-specific optimizations

## Support

For benchmarking issues:
1. Check the troubleshooting section
2. Review benchmark logs
3. Open an issue with system specifications and error details

---

*For more information, see the [LiteTTS Documentation](../README.md)*
