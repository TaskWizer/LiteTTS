#!/usr/bin/env python3
"""
Comprehensive Model Performance Benchmark for LiteTTS
Tests all available model variants with systematic metrics collection.
"""

import os
import sys
import time
import json
import psutil
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@dataclass
class BenchmarkResult:
    """Results for a single model benchmark"""
    model_name: str
    model_size_mb: float
    rtf_mean: float
    rtf_std: float
    rtf_min: float
    rtf_max: float
    memory_peak_mb: float
    memory_baseline_mb: float
    memory_overhead_mb: float
    loading_time_ms: float
    audio_length_ms: float
    samples_generated: int
    sample_rate: int
    cpu_usage_percent: float
    test_iterations: int
    error_message: Optional[str] = None
    success: bool = True

@dataclass
class TestPhrase:
    """Test phrase with metadata"""
    text: str
    category: str
    expected_length_range: tuple  # (min_ms, max_ms)

class ModelBenchmark:
    """Comprehensive model performance benchmark"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.test_phrases = self._get_test_phrases()
        self.models_dir = Path("LiteTTS/models")
        self.results: List[BenchmarkResult] = []
        
        # Available model variants from discovery cache
        self.model_variants = [
            "model.onnx",           # Full precision base
            "model_fp16.onnx",      # Half precision
            "model_q4.onnx",        # 4-bit quantized (current default)
            "model_q4f16.onnx",     # 4-bit quantized + half precision
            "model_q8f16.onnx",     # 8-bit quantized + half precision (recommended)
            "model_quantized.onnx", # General quantized
            "model_uint8.onnx",     # 8-bit unsigned integer
            "model_uint8f16.onnx"   # 8-bit unsigned + half precision
        ]
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for benchmark"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('benchmark_results.log')
            ]
        )
        return logging.getLogger(__name__)
    
    def _get_test_phrases(self) -> List[TestPhrase]:
        """Get standardized test phrases for consistent benchmarking"""
        return [
            TestPhrase("Hello world", "short", (500, 1500)),
            TestPhrase("The quick brown fox jumps over the lazy dog", "medium", (2000, 4000)),
            TestPhrase("This is a longer sentence designed to test the performance of the text-to-speech system with more complex phonetic patterns and varied intonation.", "long", (8000, 15000)),
            TestPhrase("Testing numbers: 1, 2, 3, 4, 5 and punctuation! How does it sound?", "mixed", (4000, 8000))
        ]
    
    def _get_baseline_memory(self) -> float:
        """Get baseline memory usage before model loading"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    
    def _get_model_size(self, model_path: Path) -> float:
        """Get model file size in MB"""
        if model_path.exists():
            return model_path.stat().st_size / 1024 / 1024
        return 0.0
    
    def _download_model_if_needed(self, model_name: str) -> bool:
        """Download model if not present"""
        model_path = self.models_dir / model_name
        if model_path.exists():
            self.logger.info(f"✓ Model {model_name} already exists")
            return True

        self.logger.info(f"📥 Downloading {model_name}...")
        try:
            # Use the existing downloader with correct API
            from LiteTTS.downloader import ensure_model_files
            from LiteTTS.models.manager import ModelManager

            # Try using model manager for downloads
            model_manager = ModelManager()
            result = model_manager.download_model(model_name.replace('.onnx', ''))
            return result
        except Exception as e:
            self.logger.warning(f"⚠️ Could not download {model_name}: {e}")
            return False
    
    def benchmark_model(self, model_name: str, iterations: int = 3) -> BenchmarkResult:
        """Benchmark a specific model variant"""
        self.logger.info(f"🔬 Benchmarking {model_name}...")
        
        model_path = self.models_dir / model_name
        if not model_path.exists():
            if not self._download_model_if_needed(model_name):
                return BenchmarkResult(
                    model_name=model_name,
                    model_size_mb=0,
                    rtf_mean=0, rtf_std=0, rtf_min=0, rtf_max=0,
                    memory_peak_mb=0, memory_baseline_mb=0, memory_overhead_mb=0,
                    loading_time_ms=0, audio_length_ms=0, samples_generated=0,
                    sample_rate=0, cpu_usage_percent=0, test_iterations=0,
                    error_message=f"Model {model_name} not available",
                    success=False
                )
        
        baseline_memory = self._get_baseline_memory()
        model_size = self._get_model_size(model_path)
        
        try:
            # Import and initialize TTS with specific model
            loading_start = time.time()
            
            # Temporarily update config to use this model
            from LiteTTS.config import config
            original_model_path = config.tts.model_path
            config.tts.model_path = str(model_path)
            
            # Initialize TTS engine with proper API
            import kokoro_onnx

            # Initialize with the specific model
            tts = kokoro_onnx.Kokoro(str(model_path), "LiteTTS/voices/combined_voices.npz")
            loading_time = (time.time() - loading_start) * 1000

            # Measure memory after loading
            peak_memory = self._get_baseline_memory()
            memory_overhead = peak_memory - baseline_memory

            # Run benchmark iterations
            rtf_values = []
            cpu_usage_values = []
            total_audio_length = 0
            total_samples = 0

            for iteration in range(iterations):
                self.logger.info(f"  Iteration {iteration + 1}/{iterations}")

                for phrase in self.test_phrases:
                    # Monitor CPU usage
                    cpu_start = psutil.cpu_percent()

                    # Generate audio using correct API
                    start_time = time.time()
                    audio_data = tts.generate(phrase.text, voice="af_heart")
                    generation_time = time.time() - start_time

                    # Calculate metrics
                    audio_length_ms = len(audio_data) / 24000 * 1000  # Assuming 24kHz
                    rtf = generation_time / (audio_length_ms / 1000)

                    rtf_values.append(rtf)
                    total_audio_length += audio_length_ms
                    total_samples += len(audio_data)

                    # Monitor CPU usage
                    cpu_end = psutil.cpu_percent()
                    cpu_usage_values.append((cpu_start + cpu_end) / 2)

                    # Update peak memory
                    current_memory = self._get_baseline_memory()
                    peak_memory = max(peak_memory, current_memory)
            
            # Restore original model path
            config.tts.model_path = original_model_path
            
            # Calculate statistics
            rtf_mean = statistics.mean(rtf_values)
            rtf_std = statistics.stdev(rtf_values) if len(rtf_values) > 1 else 0
            rtf_min = min(rtf_values)
            rtf_max = max(rtf_values)
            cpu_mean = statistics.mean(cpu_usage_values)
            
            return BenchmarkResult(
                model_name=model_name,
                model_size_mb=model_size,
                rtf_mean=rtf_mean,
                rtf_std=rtf_std,
                rtf_min=rtf_min,
                rtf_max=rtf_max,
                memory_peak_mb=peak_memory,
                memory_baseline_mb=baseline_memory,
                memory_overhead_mb=memory_overhead,
                loading_time_ms=loading_time,
                audio_length_ms=total_audio_length,
                samples_generated=total_samples,
                sample_rate=24000,
                cpu_usage_percent=cpu_mean,
                test_iterations=iterations,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"❌ Benchmark failed for {model_name}: {e}")
            return BenchmarkResult(
                model_name=model_name,
                model_size_mb=model_size,
                rtf_mean=0, rtf_std=0, rtf_min=0, rtf_max=0,
                memory_peak_mb=0, memory_baseline_mb=baseline_memory, memory_overhead_mb=0,
                loading_time_ms=0, audio_length_ms=0, samples_generated=0,
                sample_rate=0, cpu_usage_percent=0, test_iterations=0,
                error_message=str(e),
                success=False
            )
    
    def run_full_benchmark(self, iterations: int = 3) -> Dict[str, Any]:
        """Run comprehensive benchmark on all model variants"""
        self.logger.info("🚀 Starting comprehensive model benchmark...")
        self.logger.info(f"📊 Testing {len(self.model_variants)} model variants")
        self.logger.info(f"🔄 {iterations} iterations per model")
        self.logger.info(f"📝 {len(self.test_phrases)} test phrases per iteration")
        
        start_time = time.time()
        
        for model_name in self.model_variants:
            result = self.benchmark_model(model_name, iterations)
            self.results.append(result)
            
            if result.success:
                self.logger.info(f"✅ {model_name}: RTF={result.rtf_mean:.3f}, Memory={result.memory_overhead_mb:.1f}MB")
            else:
                self.logger.error(f"❌ {model_name}: {result.error_message}")
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        report = self._generate_report(total_time)
        
        # Save results
        self._save_results(report)
        
        return report

    def _generate_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]

        if not successful_results:
            return {
                "benchmark_info": {
                    "total_time_seconds": total_time,
                    "models_tested": len(self.model_variants),
                    "successful_tests": 0,
                    "failed_tests": len(failed_results),
                    "test_phrases": len(self.test_phrases),
                    "iterations_per_model": 0
                },
                "summary": "No successful benchmarks",
                "failed_models": [{"model": r.model_name, "error": r.error_message} for r in failed_results],
                "detailed_results": [asdict(result) for result in self.results]
            }

        # Performance rankings
        rtf_ranking = sorted(successful_results, key=lambda x: x.rtf_mean)
        memory_ranking = sorted(successful_results, key=lambda x: x.memory_overhead_mb)
        size_ranking = sorted(successful_results, key=lambda x: x.model_size_mb)
        loading_ranking = sorted(successful_results, key=lambda x: x.loading_time_ms)

        # Best performers
        best_rtf = rtf_ranking[0]
        best_memory = memory_ranking[0]
        smallest_size = size_ranking[0]
        fastest_loading = loading_ranking[0]

        # Recommendations
        recommendations = self._generate_recommendations(successful_results)

        return {
            "benchmark_info": {
                "total_time_seconds": total_time,
                "models_tested": len(self.model_variants),
                "successful_tests": len(successful_results),
                "failed_tests": len(failed_results),
                "test_phrases": len(self.test_phrases),
                "iterations_per_model": successful_results[0].test_iterations if successful_results else 0
            },
            "performance_rankings": {
                "best_rtf": {
                    "model": best_rtf.model_name,
                    "rtf": best_rtf.rtf_mean,
                    "description": f"Fastest generation: {best_rtf.rtf_mean:.3f} RTF"
                },
                "best_memory": {
                    "model": best_memory.model_name,
                    "memory_mb": best_memory.memory_overhead_mb,
                    "description": f"Lowest memory usage: {best_memory.memory_overhead_mb:.1f}MB overhead"
                },
                "smallest_size": {
                    "model": smallest_size.model_name,
                    "size_mb": smallest_size.model_size_mb,
                    "description": f"Smallest file: {smallest_size.model_size_mb:.1f}MB"
                },
                "fastest_loading": {
                    "model": fastest_loading.model_name,
                    "loading_ms": fastest_loading.loading_time_ms,
                    "description": f"Fastest loading: {fastest_loading.loading_time_ms:.0f}ms"
                }
            },
            "detailed_results": [asdict(result) for result in self.results],
            "recommendations": recommendations,
            "failed_models": [{"model": r.model_name, "error": r.error_message} for r in failed_results]
        }

    def _generate_recommendations(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Generate usage recommendations based on benchmark results"""
        recommendations = {}

        # Development recommendation (balance of speed and quality)
        dev_candidates = [r for r in results if r.rtf_mean < 0.25 and r.memory_overhead_mb < 200]
        if dev_candidates:
            dev_best = min(dev_candidates, key=lambda x: x.rtf_mean + x.memory_overhead_mb/100)
            recommendations["development"] = {
                "model": dev_best.model_name,
                "reason": f"Good balance: {dev_best.rtf_mean:.3f} RTF, {dev_best.memory_overhead_mb:.1f}MB memory",
                "rtf": dev_best.rtf_mean,
                "memory_mb": dev_best.memory_overhead_mb
            }

        # Production recommendation (prioritize reliability and reasonable performance)
        prod_candidates = [r for r in results if r.rtf_mean < 0.3 and r.memory_overhead_mb < 300]
        if prod_candidates:
            prod_best = min(prod_candidates, key=lambda x: x.rtf_std + x.memory_overhead_mb/200)
            recommendations["production"] = {
                "model": prod_best.model_name,
                "reason": f"Stable performance: {prod_best.rtf_mean:.3f}±{prod_best.rtf_std:.3f} RTF",
                "rtf": prod_best.rtf_mean,
                "rtf_std": prod_best.rtf_std,
                "memory_mb": prod_best.memory_overhead_mb
            }

        # Resource-constrained recommendation (minimize memory and size)
        resource_candidates = [r for r in results if r.rtf_mean < 0.5]
        if resource_candidates:
            resource_best = min(resource_candidates, key=lambda x: x.memory_overhead_mb + x.model_size_mb/10)
            recommendations["resource_constrained"] = {
                "model": resource_best.model_name,
                "reason": f"Minimal resources: {resource_best.model_size_mb:.1f}MB file, {resource_best.memory_overhead_mb:.1f}MB memory",
                "model_size_mb": resource_best.model_size_mb,
                "memory_mb": resource_best.memory_overhead_mb,
                "rtf": resource_best.rtf_mean
            }

        # Performance recommendation (fastest generation)
        if results:
            perf_best = min(results, key=lambda x: x.rtf_mean)
            recommendations["performance"] = {
                "model": perf_best.model_name,
                "reason": f"Fastest generation: {perf_best.rtf_mean:.3f} RTF",
                "rtf": perf_best.rtf_mean,
                "memory_mb": perf_best.memory_overhead_mb
            }

        return recommendations

    def _save_results(self, report: Dict[str, Any]):
        """Save benchmark results to files"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # Save JSON report
        json_file = f"benchmark_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        self.logger.info(f"📄 JSON report saved: {json_file}")

        # Save markdown report
        md_file = f"benchmark_report_{timestamp}.md"
        self._save_markdown_report(report, md_file)
        self.logger.info(f"📄 Markdown report saved: {md_file}")

    def _save_markdown_report(self, report: Dict[str, Any], filename: str):
        """Save benchmark results as markdown report"""
        with open(filename, 'w') as f:
            f.write("# LiteTTS Model Performance Benchmark Report\n\n")

            # Summary
            info = report["benchmark_info"]
            f.write("## Benchmark Summary\n\n")
            f.write(f"- **Total Time**: {info['total_time_seconds']:.1f} seconds\n")
            f.write(f"- **Models Tested**: {info['models_tested']}\n")
            f.write(f"- **Successful Tests**: {info['successful_tests']}\n")
            f.write(f"- **Failed Tests**: {info['failed_tests']}\n")
            f.write(f"- **Test Phrases**: {info['test_phrases']}\n")
            f.write(f"- **Iterations per Model**: {info['iterations_per_model']}\n\n")

            # Performance Rankings
            f.write("## Performance Rankings\n\n")
            rankings = report["performance_rankings"]
            for category, data in rankings.items():
                f.write(f"### {category.replace('_', ' ').title()}\n")
                f.write(f"**{data['model']}** - {data['description']}\n\n")

            # Recommendations
            f.write("## Recommendations\n\n")
            recommendations = report["recommendations"]
            for use_case, rec in recommendations.items():
                f.write(f"### {use_case.replace('_', ' ').title()}\n")
                f.write(f"**Recommended Model**: `{rec['model']}`\n\n")
                f.write(f"**Reason**: {rec['reason']}\n\n")

            # Detailed Results Table
            f.write("## Detailed Results\n\n")
            f.write("| Model | RTF (mean±std) | Memory (MB) | Size (MB) | Loading (ms) | Success |\n")
            f.write("|-------|----------------|-------------|-----------|--------------|----------|\n")

            for result in report["detailed_results"]:
                if result["success"]:
                    rtf_str = f"{result['rtf_mean']:.3f}±{result['rtf_std']:.3f}"
                    memory_str = f"{result['memory_overhead_mb']:.1f}"
                    size_str = f"{result['model_size_mb']:.1f}"
                    loading_str = f"{result['loading_time_ms']:.0f}"
                    success_str = "✅"
                else:
                    rtf_str = "N/A"
                    memory_str = "N/A"
                    size_str = f"{result['model_size_mb']:.1f}" if result['model_size_mb'] > 0 else "N/A"
                    loading_str = "N/A"
                    success_str = "❌"

                f.write(f"| {result['model_name']} | {rtf_str} | {memory_str} | {size_str} | {loading_str} | {success_str} |\n")

            # Failed Models
            if report["failed_models"]:
                f.write("\n## Failed Models\n\n")
                for failed in report["failed_models"]:
                    f.write(f"- **{failed['model']}**: {failed['error']}\n")


def main():
    """Run the comprehensive model benchmark"""
    benchmark = ModelBenchmark()

    # Run benchmark with 3 iterations per model
    report = benchmark.run_full_benchmark(iterations=3)

    # Print summary
    print("\n" + "="*60)
    print("🎯 BENCHMARK COMPLETE")
    print("="*60)

    if report["benchmark_info"]["successful_tests"] > 0:
        rankings = report["performance_rankings"]
        print(f"🏆 Best RTF: {rankings['best_rtf']['model']} ({rankings['best_rtf']['rtf']:.3f})")
        print(f"💾 Best Memory: {rankings['best_memory']['model']} ({rankings['best_memory']['memory_mb']:.1f}MB)")
        print(f"📦 Smallest: {rankings['smallest_size']['model']} ({rankings['smallest_size']['size_mb']:.1f}MB)")

        print("\n🎯 RECOMMENDATIONS:")
        for use_case, rec in report["recommendations"].items():
            print(f"  {use_case.title()}: {rec['model']}")
    else:
        print("❌ No successful benchmarks completed")

    print("="*60)


if __name__ == "__main__":
    main()
