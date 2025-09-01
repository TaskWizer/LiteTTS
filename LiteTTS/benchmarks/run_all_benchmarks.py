#!/usr/bin/env python3
"""
Master Benchmark Runner for Kokoro ONNX TTS API
Runs all benchmark scripts and provides comprehensive performance analysis
"""

import os
import sys
import time
import json
import psutil
import threading
import numpy as np
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def run_all_benchmark_scripts():
    """Run all individual benchmark scripts"""
    benchmark_dir = Path(__file__).parent
    scripts = [
        "quick_benchmark.py",
        "performance_analysis.py",
        "run_benchmark.py",
        "run_performance_regression_tests.py",
        "accurate_performance_analysis.py"
    ]

    print("🚀 Running All Benchmark Scripts")
    print("=" * 50)

    results = {}
    for script in scripts:
        script_path = benchmark_dir / script
        if script_path.exists():
            print(f"\n📊 Running {script}...")
            try:
                result = subprocess.run([sys.executable, str(script_path)],
                                      capture_output=True, text=True, timeout=300)
                results[script] = {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                if result.returncode == 0:
                    print(f"✅ {script} completed successfully")
                else:
                    print(f"❌ {script} failed with return code {result.returncode}")
            except subprocess.TimeoutExpired:
                print(f"⏰ {script} timed out after 5 minutes")
                results[script] = {"success": False, "error": "timeout"}
            except Exception as e:
                print(f"💥 {script} failed with exception: {e}")
                results[script] = {"success": False, "error": str(e)}
        else:
            print(f"⚠️  {script} not found, skipping")

    return results

@dataclass
class BenchmarkResult:
    """Individual benchmark result"""
    model_name: str
    model_path: str
    model_size_mb: float
    test_text: str
    text_length: int
    voice: str
    
    # Performance metrics
    load_time_ms: float
    generation_time_ms: float
    audio_duration_ms: float
    rtf: float
    samples_generated: int
    sample_rate: int
    
    # System metrics
    peak_memory_mb: float
    avg_memory_mb: float
    peak_cpu_percent: float
    avg_cpu_percent: float
    
    # Quality metrics
    audio_quality_score: float  # Based on signal analysis
    success: bool
    error_message: Optional[str] = None
    
    # Metadata
    timestamp: str = ""
    benchmark_version: str = "1.0"

class SystemMonitor:
    """Monitor system resources during benchmarking"""
    
    def __init__(self):
        self.monitoring = False
        self.memory_samples = []
        self.cpu_samples = []
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring = True
        self.memory_samples = []
        self.cpu_samples = []
        self.monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Tuple[float, float, float, float]:
        """Stop monitoring and return peak/avg memory and CPU"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        if not self.memory_samples or not self.cpu_samples:
            return 0.0, 0.0, 0.0, 0.0
        
        peak_memory = max(self.memory_samples)
        avg_memory = sum(self.memory_samples) / len(self.memory_samples)
        peak_cpu = max(self.cpu_samples)
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples)
        
        return peak_memory, avg_memory, peak_cpu, avg_cpu
    
    def _monitor_worker(self):
        """Background worker for system monitoring"""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                # Memory usage in MB
                memory_mb = process.memory_info().rss / (1024 * 1024)
                self.memory_samples.append(memory_mb)
                
                # CPU usage percentage
                cpu_percent = process.cpu_percent()
                self.cpu_samples.append(cpu_percent)
                
                time.sleep(0.1)  # Sample every 100ms
            except Exception:
                break

class AudioQualityAnalyzer:
    """Analyze audio quality metrics"""
    
    @staticmethod
    def analyze_audio_quality(audio: np.ndarray, sample_rate: int) -> float:
        """
        Analyze audio quality and return a score (0-100)
        Higher scores indicate better quality
        """
        if len(audio) == 0:
            return 0.0
        
        try:
            # Normalize audio
            audio = audio.astype(np.float32)
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio))
            
            # Calculate various quality metrics
            
            # 1. Signal-to-noise ratio estimate
            signal_power = np.mean(audio ** 2)
            noise_floor = np.percentile(np.abs(audio), 10)  # Estimate noise floor
            snr = 10 * np.log10(signal_power / (noise_floor ** 2 + 1e-10))
            snr_score = min(100, max(0, (snr + 20) * 2))  # Scale to 0-100
            
            # 2. Dynamic range
            dynamic_range = np.max(audio) - np.min(audio)
            dr_score = min(100, dynamic_range * 50)  # Scale to 0-100
            
            # 3. Frequency content (spectral centroid)
            if len(audio) > 1024:
                fft = np.fft.fft(audio[:1024])
                freqs = np.fft.fftfreq(1024, 1/sample_rate)
                magnitude = np.abs(fft)
                spectral_centroid = np.sum(freqs[:512] * magnitude[:512]) / (np.sum(magnitude[:512]) + 1e-10)
                # Good speech typically has centroid around 1000-3000 Hz
                centroid_score = 100 - min(100, abs(spectral_centroid - 2000) / 50)
            else:
                centroid_score = 50
            
            # 4. Zero crossing rate (indicates voicing)
            zero_crossings = np.sum(np.diff(np.sign(audio)) != 0)
            zcr = zero_crossings / len(audio)
            # Good speech typically has ZCR around 0.1-0.3
            zcr_score = 100 - min(100, abs(zcr - 0.2) * 500)
            
            # Combine scores with weights
            quality_score = (
                snr_score * 0.4 +
                dr_score * 0.2 +
                centroid_score * 0.2 +
                zcr_score * 0.2
            )
            
            return max(0, min(100, quality_score))
            
        except Exception as e:
            logging.warning(f"Audio quality analysis failed: {e}")
            return 50.0  # Default score if analysis fails

class ModelBenchmarker:
    """Comprehensive model benchmarking system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_texts = [
            "Hello, world!",
            "This is a test of the text-to-speech system.",
            "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.",
            "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat."
        ]
        self.test_voices = ["af_heart", "am_puck"]
        self.results: List[BenchmarkResult] = []
        
    def discover_models(self) -> List[Tuple[str, str]]:
        """Discover all available ONNX models"""
        models_dir = Path("LiteTTS/models")
        models = []
        
        for model_file in models_dir.glob("*.onnx"):
            model_name = model_file.stem
            model_path = str(model_file)
            models.append((model_name, model_path))
        
        return sorted(models)
    
    def benchmark_model(self, model_name: str, model_path: str) -> List[BenchmarkResult]:
        """Benchmark a single model with all test cases"""
        results = []
        
        self.logger.info(f"🔬 Benchmarking model: {model_name}")
        
        # Get model file size
        model_size_mb = Path(model_path).stat().st_size / (1024 * 1024)
        
        for text in self.test_texts:
            for voice in self.test_voices:
                result = self._benchmark_single_case(
                    model_name, model_path, model_size_mb, text, voice
                )
                results.append(result)
                
                # Brief pause between tests
                time.sleep(0.5)
        
        return results
    
    def _benchmark_single_case(self, model_name: str, model_path: str, 
                              model_size_mb: float, text: str, voice: str) -> BenchmarkResult:
        """Benchmark a single test case"""
        self.logger.info(f"  📝 Testing: '{text[:30]}...' with voice '{voice}'")
        
        # Initialize result with defaults
        result = BenchmarkResult(
            model_name=model_name,
            model_path=model_path,
            model_size_mb=model_size_mb,
            test_text=text,
            text_length=len(text),
            voice=voice,
            load_time_ms=0,
            generation_time_ms=0,
            audio_duration_ms=0,
            rtf=0,
            samples_generated=0,
            sample_rate=24000,
            peak_memory_mb=0,
            avg_memory_mb=0,
            peak_cpu_percent=0,
            avg_cpu_percent=0,
            audio_quality_score=0,
            success=False,
            timestamp=datetime.now().isoformat()
        )
        
        monitor = SystemMonitor()
        
        try:
            # Start system monitoring
            monitor.start_monitoring()
            
            # Load model
            load_start = time.time()
            
            # Import kokoro_onnx and create model
            import kokoro_onnx
            model = kokoro_onnx.Kokoro(model_path, "LiteTTS/voices")
            
            load_time = (time.time() - load_start) * 1000
            result.load_time_ms = load_time
            
            # Generate audio
            gen_start = time.time()
            audio, sample_rate = model.create(text, voice=voice, speed=1.0, lang="en-us")
            gen_time = (time.time() - gen_start) * 1000
            
            # Stop monitoring and get metrics
            peak_mem, avg_mem, peak_cpu, avg_cpu = monitor.stop_monitoring()
            
            # Calculate metrics
            result.generation_time_ms = gen_time
            result.samples_generated = len(audio)
            result.sample_rate = sample_rate
            result.audio_duration_ms = (len(audio) / sample_rate) * 1000
            result.rtf = gen_time / result.audio_duration_ms if result.audio_duration_ms > 0 else 0
            result.peak_memory_mb = peak_mem
            result.avg_memory_mb = avg_mem
            result.peak_cpu_percent = peak_cpu
            result.avg_cpu_percent = avg_cpu
            
            # Analyze audio quality
            result.audio_quality_score = AudioQualityAnalyzer.analyze_audio_quality(audio, sample_rate)
            
            result.success = len(audio) > 0
            
            self.logger.info(f"    ✅ Success: {len(audio)} samples, RTF: {result.rtf:.3f}, Quality: {result.audio_quality_score:.1f}")
            
        except Exception as e:
            monitor.stop_monitoring()
            result.error_message = str(e)
            result.success = False
            self.logger.error(f"    ❌ Failed: {e}")
        
        return result
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark on all models"""
        self.logger.info("🚀 Starting comprehensive model benchmark")
        
        start_time = datetime.now()
        models = self.discover_models()
        
        self.logger.info(f"📊 Found {len(models)} models to benchmark")
        
        all_results = []
        
        for model_name, model_path in models:
            model_results = self.benchmark_model(model_name, model_path)
            all_results.extend(model_results)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        summary = self._generate_summary(all_results, duration)
        
        self.logger.info(f"✅ Benchmark completed in {duration:.1f} seconds")
        
        return {
            "summary": summary,
            "results": [asdict(result) for result in all_results],
            "metadata": {
                "benchmark_start": start_time.isoformat(),
                "benchmark_end": end_time.isoformat(),
                "duration_seconds": duration,
                "total_tests": len(all_results),
                "models_tested": len(models),
                "test_texts": len(self.test_texts),
                "test_voices": len(self.test_voices)
            }
        }
    
    def _generate_summary(self, results: List[BenchmarkResult], duration: float) -> Dict[str, Any]:
        """Generate benchmark summary statistics"""
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return {"error": "No successful benchmark results"}
        
        # Group by model
        model_stats = {}
        for result in successful_results:
            if result.model_name not in model_stats:
                model_stats[result.model_name] = []
            model_stats[result.model_name].append(result)
        
        # Calculate statistics for each model
        model_summary = {}
        for model_name, model_results in model_stats.items():
            rtfs = [r.rtf for r in model_results]
            latencies = [r.generation_time_ms for r in model_results]
            qualities = [r.audio_quality_score for r in model_results]
            memories = [r.peak_memory_mb for r in model_results]
            
            model_summary[model_name] = {
                "model_size_mb": model_results[0].model_size_mb,
                "tests_run": len(model_results),
                "success_rate": len(model_results) / len([r for r in results if r.model_name == model_name]),
                "avg_rtf": sum(rtfs) / len(rtfs),
                "min_rtf": min(rtfs),
                "max_rtf": max(rtfs),
                "avg_latency_ms": sum(latencies) / len(latencies),
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "avg_quality_score": sum(qualities) / len(qualities),
                "avg_memory_mb": sum(memories) / len(memories),
                "load_time_ms": model_results[0].load_time_ms
            }
        
        return {
            "total_duration_seconds": duration,
            "total_tests": len(results),
            "successful_tests": len(successful_results),
            "success_rate": len(successful_results) / len(results),
            "model_performance": model_summary,
            "best_rtf_model": min(model_summary.keys(), key=lambda k: model_summary[k]["avg_rtf"]),
            "best_quality_model": max(model_summary.keys(), key=lambda k: model_summary[k]["avg_quality_score"]),
            "fastest_model": min(model_summary.keys(), key=lambda k: model_summary[k]["avg_latency_ms"]),
            "most_efficient_model": min(model_summary.keys(), key=lambda k: model_summary[k]["avg_memory_mb"])
        }

class BenchmarkReporter:
    """Generate reports from benchmark results"""

    @staticmethod
    def generate_markdown_report(benchmark_data: Dict[str, Any]) -> str:
        """Generate a comprehensive markdown report"""
        summary = benchmark_data["summary"]
        metadata = benchmark_data["metadata"]

        report = f"""# Kokoro TTS Model Performance Benchmark Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Duration**: {summary["total_duration_seconds"]:.1f} seconds
**Models Tested**: {metadata["models_tested"]}
**Total Tests**: {summary["total_tests"]}
**Success Rate**: {summary["success_rate"]:.1%}

## 🏆 Performance Champions

- **🚀 Best RTF (Real-Time Factor)**: `{summary["best_rtf_model"]}` - {summary["model_performance"][summary["best_rtf_model"]]["avg_rtf"]:.3f}
- **🎵 Best Audio Quality**: `{summary["best_quality_model"]}` - {summary["model_performance"][summary["best_quality_model"]]["avg_quality_score"]:.1f}/100
- **⚡ Fastest Generation**: `{summary["fastest_model"]}` - {summary["model_performance"][summary["fastest_model"]]["avg_latency_ms"]:.0f}ms
- **💾 Most Memory Efficient**: `{summary["most_efficient_model"]}` - {summary["model_performance"][summary["most_efficient_model"]]["avg_memory_mb"]:.0f}MB

## 📊 Detailed Model Performance

| Model | Size (MB) | Avg RTF | Avg Latency (ms) | Quality Score | Memory (MB) | Load Time (ms) |
|-------|-----------|---------|------------------|---------------|-------------|----------------|
"""

        # Add model performance table
        for model_name, stats in summary["model_performance"].items():
            report += f"| `{model_name}` | {stats['model_size_mb']:.1f} | {stats['avg_rtf']:.3f} | {stats['avg_latency_ms']:.0f} | {stats['avg_quality_score']:.1f} | {stats['avg_memory_mb']:.0f} | {stats['load_time_ms']:.0f} |\n"

        report += f"""
## 📈 Performance Analysis

### Real-Time Factor (RTF) Comparison
Lower RTF values indicate better real-time performance (RTF < 1.0 = faster than real-time).

"""

        # RTF analysis
        rtf_models = [(name, stats["avg_rtf"]) for name, stats in summary["model_performance"].items()]
        rtf_models.sort(key=lambda x: x[1])

        for i, (model, rtf) in enumerate(rtf_models, 1):
            status = "🟢 Excellent" if rtf < 0.3 else "🟡 Good" if rtf < 0.6 else "🟠 Fair" if rtf < 1.0 else "🔴 Slow"
            report += f"{i}. **{model}**: {rtf:.3f} {status}\n"

        report += f"""
### Quality vs Performance Trade-offs

The following analysis shows the balance between audio quality and performance:

"""

        # Quality vs performance analysis
        for model_name, stats in summary["model_performance"].items():
            efficiency_score = (stats["avg_quality_score"] / 100) / max(0.1, stats["avg_rtf"])
            report += f"- **{model_name}**: Quality {stats['avg_quality_score']:.1f}/100, RTF {stats['avg_rtf']:.3f} → Efficiency Score: {efficiency_score:.2f}\n"

        report += f"""
## 🔧 Technical Details

### Test Configuration
- **Test Texts**: {metadata["test_texts"]} different text samples
- **Test Voices**: {metadata["test_voices"]} voices (af_heart, am_puck)
- **Sample Rate**: 24kHz
- **Audio Format**: 32-bit float PCM

### Metrics Explained
- **RTF (Real-Time Factor)**: Generation time / Audio duration. Lower is better.
- **Quality Score**: Composite score (0-100) based on SNR, dynamic range, spectral content, and voicing characteristics.
- **Memory Usage**: Peak memory consumption during generation.
- **Load Time**: Time to initialize the model.

### System Information
- **Benchmark Version**: 1.0
- **Platform**: CPU-only inference
- **Monitoring**: 100ms sampling rate for system metrics

## 📋 Recommendations

Based on the benchmark results:

1. **For Production Use**: Choose `{summary["best_rtf_model"]}` for optimal real-time performance
2. **For Quality Focus**: Choose `{summary["best_quality_model"]}` for best audio quality
3. **For Resource Constraints**: Choose `{summary["most_efficient_model"]}` for minimal memory usage
4. **For Development**: Choose `{summary["fastest_model"]}` for fastest iteration cycles

---
*Report generated by Kokoro TTS Benchmark System v1.0*
"""

        return report

    @staticmethod
    def save_results(benchmark_data: Dict[str, Any], output_dir: str = "docs/benchmark"):
        """Save benchmark results in multiple formats"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON data
        json_file = output_path / f"benchmark_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(benchmark_data, f, indent=2)

        # Save markdown report
        markdown_file = output_path / f"benchmark_report_{timestamp}.md"
        markdown_report = BenchmarkReporter.generate_markdown_report(benchmark_data)
        with open(markdown_file, 'w') as f:
            f.write(markdown_report)

        # Save latest symlinks
        latest_json = output_path / "latest_results.json"
        latest_md = output_path / "latest_report.md"

        if latest_json.exists():
            latest_json.unlink()
        if latest_md.exists():
            latest_md.unlink()

        latest_json.symlink_to(json_file.name)
        latest_md.symlink_to(markdown_file.name)

        return {
            "json_file": str(json_file),
            "markdown_file": str(markdown_file),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md)
        }

def main():
    """Main benchmarking function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )

    benchmarker = ModelBenchmarker()

    try:
        # Run benchmark
        results = benchmarker.run_full_benchmark()

        # Save results
        file_paths = BenchmarkReporter.save_results(results)

        print("\n🎉 Benchmark completed successfully!")
        print(f"📊 Results saved to: {file_paths['json_file']}")
        print(f"📝 Report saved to: {file_paths['markdown_file']}")
        print(f"🔗 Latest results: {file_paths['latest_json']}")
        print(f"🔗 Latest report: {file_paths['latest_markdown']}")

        # Print summary
        summary = results["summary"]
        print(f"\n📈 Quick Summary:")
        print(f"   Best RTF: {summary['best_rtf_model']} ({summary['model_performance'][summary['best_rtf_model']]['avg_rtf']:.3f})")
        print(f"   Best Quality: {summary['best_quality_model']} ({summary['model_performance'][summary['best_quality_model']]['avg_quality_score']:.1f}/100)")
        print(f"   Fastest: {summary['fastest_model']} ({summary['model_performance'][summary['fastest_model']]['avg_latency_ms']:.0f}ms)")

    except Exception as e:
        logging.error(f"Benchmark failed: {e}")
        return 1

    return 0

def main_with_all_scripts():
    """Main function that runs all benchmark scripts plus comprehensive benchmark"""
    print("🎯 Kokoro ONNX TTS API - Master Benchmark Runner")
    print("=" * 60)

    # First run all individual benchmark scripts
    script_results = run_all_benchmark_scripts()

    # Then run the comprehensive benchmark
    print(f"\n🔬 Running Comprehensive Model Benchmark...")
    comprehensive_result = main()

    # Summary
    print(f"\n📋 Master Benchmark Summary")
    print("=" * 40)

    successful_scripts = sum(1 for r in script_results.values() if r.get("success", False))
    total_scripts = len(script_results)

    print(f"Individual Scripts: {successful_scripts}/{total_scripts} successful")
    print(f"Comprehensive Benchmark: {'✅ Success' if comprehensive_result == 0 else '❌ Failed'}")

    if comprehensive_result == 0 and successful_scripts == total_scripts:
        print(f"\n🎉 All benchmarks completed successfully!")
        return 0
    else:
        print(f"\n⚠️  Some benchmarks failed. Check output above for details.")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--comprehensive-only":
        sys.exit(main())
    else:
        sys.exit(main_with_all_scripts())
