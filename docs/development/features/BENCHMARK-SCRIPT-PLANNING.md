### **Benchmark Script Plan**
#### **1. Objectives**
- Compare performance of all ONNX model variants (`model.onnx`, `model_fp16.onnx`, etc.).
- Test latency/quality differences between American voices (`af_*`, `am_*`).
- Validate performance claims (RTF, cache latency, pre-caching).
- Generate metrics for:
  - Time-to-first-word (TTFW)
  - Real-Time Factor (RTF)
  - Total generation time
  - CPU/RAM usage
  - Cache hit/miss latency
- Create visuals for `README.md`.

#### **2. Benchmark Setup**
##### **Dependencies**
```python
# Core

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../FEATURES.md) | [Configuration](../../CONFIGURATION.md) | [Performance](../../PERFORMANCE.md) | [Monitoring](../../MONITORING.md) | [Testing](../../TESTING.md) | [Troubleshooting](../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../DEPENDENCIES.md) | [Quick Start](../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../api/API_REFERENCE.md) | [Development](../README.md) | [Voice System](../../voices/README.md) | [Watermarking](../../WATERMARKING.md)

**Project:** [Changelog](../../CHANGELOG.md) | [Roadmap](../../ROADMAP.md) | [Contributing](../../CONTRIBUTIONS.md) | [Beta Features](../../BETA_FEATURES.md)

---
import time
import psutil  # For CPU/RAM tracking
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# TTS API
from your_tts_module import TTS, Voice, Metrics
```

##### **Test Cases**
```python
# Models to test (from ONNX variants)
MODELS = [
    "model.onnx", "model_fp16.onnx", "model_q4.onnx",
    "model_q4f16.onnx", "model_q8f16.onnx",
    "model_quantized.onnx", "model_uint8.onnx", "model_uint8f16.onnx"
]

# Voices to test (filter American)
VOICES = [v for v in Voice.list_all() if v.startswith(('af_', 'am_'))]

# Test prompts (short/long, cached/uncached)
PROMPTS = [
    "Hello world",  # Cached (pre-warmed)
    "The quick brown fox jumps over the lazy dog",  # Uncached
    "Lorem ipsum dolor sit amet...",  # Long uncached
]
```

#### **3. Metrics Collection**
```python
def run_benchmark(model: str, voice: str, prompt: str) -> dict:
    """Run a single TTS test and return metrics."""
    start_time = time.time()

    # Track CPU/RAM before and after
    cpu_start = psutil.cpu_percent()
    ram_start = psutil.virtual_memory().used

    # Initialize TTS with target model/voice
    tts = TTS(model=model, voice=voice)

    # Time to first word (TTFW)
    first_chunk_time = None
    def callback(chunk):
        nonlocal first_chunk_time
        if first_chunk_time is None:
            first_chunk_time = time.time() - start_time

    # Generate audio
    audio = tts.generate(prompt, stream_callback=callback)
    total_time = time.time() - start_time

    # Post-gen metrics
    cpu_end = psutil.cpu_percent()
    ram_end = psutil.virtual_memory().used

    return {
        "model": model,
        "voice": voice,
        "prompt": prompt,
        "ttfw_ms": first_chunk_time * 1000,
        "rtf": total_time / (len(audio) / tts.sample_rate),  # RTF = gen_time / audio_duration
        "total_time_ms": total_time * 1000,
        "cpu_usage": cpu_end - cpu_start,
        "ram_usage_mb": (ram_end - ram_start) / 1024 / 1024,
        "cache_status": "hit" if tts.is_cached(prompt) else "miss",
    }
```

#### **4. Automated Test Execution**
```python
def run_full_benchmark():
    results = []

    # Iterate through all combinations
    for model in MODELS:
        for voice in VOICES[:3]:  # Test subset first (e.g., 3 voices)
            for prompt in PROMPTS:
                print(f"Testing {model} + {voice} + '{prompt[:10]}...'")
                result = run_benchmark(model, voice, prompt)
                results.append(result)

    # Save to DataFrame
    df = pd.DataFrame(results)
    df.to_csv("benchmark_results.csv", index=False)
    return df
```

#### **5. Visualization & Reporting**
##### **Key Charts to Generate**
1. **Model Comparison (RTF, Latency, CPU)**
   ```python
   sns.barplot(data=df, x="model", y="rtf", hue="voice")
   plt.title("RTF by Model and Voice")
   plt.xticks(rotation=45)
   plt.savefig("charts/rtf_by_model.png")
   ```
   ![RTF Comparison](https://i.imgur.com/RTFbyModel.png)

2. **Cache Performance**
   ```python
   sns.boxplot(data=df, x="cache_status", y="ttfw_ms")
   plt.title("Time-to-First-Word: Cache Hit vs. Miss")
   plt.savefig("charts/cache_impact.png")
   ```

3. **Voice Latency Distribution**
   ```python
   sns.violinplot(data=df, x="voice", y="total_time_ms")
   plt.title("Total Generation Time by Voice")
   plt.savefig("charts/voice_latency.png")
   ```

4. **Resource Usage**
   ```python
   sns.scatterplot(data=df, x="cpu_usage", y="ram_usage_mb", hue="model")
   plt.title("CPU vs. RAM Usage by Model")
   plt.savefig("charts/resource_usage.png")
   ```

#### **6. Example Output (README.md)**
```markdown
## 📊 Benchmark Results
### **Model Performance**
| Model              | Avg RTF | TTFW (ms) | CPU Usage (%) |
|--------------------|---------|-----------|---------------|
| `model_fp16.onnx`  | 0.18    | 12        | 45            |
| `model_q4.onnx`    | 0.22    | 15        | 38            |

### **Key Insights**
- **Fastest Model:** `model_fp16.onnx` (RTF 0.18, 12ms TTFW).
- **Cache Impact:** Pre-warmed phrases reduce TTFW by 90%.
- **Voice Variance:** `am_voice2` is 10% faster than `af_voice1`.

![RTF Comparison](charts/rtf_by_model.png)
![Cache Impact](charts/cache_impact.png)
```

#### **7. Advanced Tests (Optional)**
- **Concurrency:** Simulate 10+ concurrent requests to test scalability.
- **Long-Running Stability:** Monitor CPU/RAM over 1 hour of usage.
- **Quality Metrics:** Use `librosa` to compare MFCCs of outputs.

### **Next Steps**
1. Run the script (`python benchmark.py`).
2. Review `benchmark_results.csv` and charts.
3. Update `README.md` with findings and visuals.
