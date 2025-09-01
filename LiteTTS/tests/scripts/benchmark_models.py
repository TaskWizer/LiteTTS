#!/usr/bin/env python3
"""
Comprehensive model benchmarking script to determine optimal model variant for RTF performance
"""

import os
import sys
import time
import json
import statistics
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ModelBenchmarkResult:
    """Results for a single model benchmark"""
    model_name: str
    model_path: str
    model_size_mb: float
    
    # Performance metrics
    avg_rtf: float
    min_rtf: float
    max_rtf: float
    median_rtf: float
    std_rtf: float
    
    # Timing metrics
    avg_generation_time: float
    avg_audio_duration: float
    load_time: float
    
    # System metrics
    peak_memory_mb: float
    avg_cpu_percent: float
    
    # Quality metrics
    success_rate: float
    error_count: int
    
    # Test details
    test_count: int
    total_test_time: float

class ModelBenchmarker:
    """Comprehensive model benchmarking system"""
    
    def __init__(self):
        self.test_texts = [
            "Hello world",
            "This is a test of the text-to-speech system.",
            "The quick brown fox jumps over the lazy dog.",
            "Performance testing with various text lengths and complexity levels.",
            "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort."
        ]
        self.test_voices = ["af_heart", "am_puck"]
        self.models_dir = Path("LiteTTS/models")
        
    def discover_models(self) -> List[Tuple[str, str, float]]:
        """Discover available ONNX models with their sizes"""
        models = []
        
        if not self.models_dir.exists():
            logger.error(f"Models directory not found: {self.models_dir}")
            return models
        
        for model_file in self.models_dir.glob("*.onnx"):
            model_name = model_file.stem
            model_path = str(model_file)
            model_size_mb = model_file.stat().st_size / (1024 * 1024)
            models.append((model_name, model_path, model_size_mb))
        
        return sorted(models, key=lambda x: x[2])  # Sort by size
    
    def benchmark_model(self, model_name: str, model_path: str, model_size_mb: float, 
                       iterations: int = 10) -> ModelBenchmarkResult:
        """Benchmark a single model variant"""
        logger.info(f"🔬 Benchmarking model: {model_name} ({model_size_mb:.1f}MB)")
        
        rtf_values = []
        generation_times = []
        audio_durations = []
        memory_values = []
        cpu_values = []
        errors = 0
        
        # Load model and measure load time
        load_start = time.time()
        try:
            import kokoro_onnx
            import psutil
            
            process = psutil.Process()
            
            # Apply patches for optimization
            from LiteTTS.patches import apply_all_patches
            apply_all_patches()
            
            model = kokoro_onnx.Kokoro(model_path, "LiteTTS/voices")
            load_time = time.time() - load_start
            
            logger.info(f"  Model loaded in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"  Failed to load model: {e}")
            return ModelBenchmarkResult(
                model_name=model_name,
                model_path=model_path,
                model_size_mb=model_size_mb,
                avg_rtf=float('inf'),
                min_rtf=float('inf'),
                max_rtf=float('inf'),
                median_rtf=float('inf'),
                std_rtf=0,
                avg_generation_time=0,
                avg_audio_duration=0,
                load_time=0,
                peak_memory_mb=0,
                avg_cpu_percent=0,
                success_rate=0,
                error_count=1,
                test_count=0,
                total_test_time=0
            )
        
        # Run benchmark iterations
        total_start = time.time()
        
        for i in range(iterations):
            text = self.test_texts[i % len(self.test_texts)]
            voice = self.test_voices[i % len(self.test_voices)]
            
            try:
                # Monitor system resources
                memory_before = process.memory_info().rss / (1024 * 1024)
                cpu_before = process.cpu_percent()
                
                # Generate audio
                gen_start = time.time()
                audio, sample_rate = model.create(text, voice=voice, speed=1.0, lang="en-us")
                gen_time = time.time() - gen_start
                
                # Calculate metrics
                audio_duration = len(audio) / sample_rate
                rtf = gen_time / audio_duration if audio_duration > 0 else float('inf')
                
                # Monitor system resources after
                memory_after = process.memory_info().rss / (1024 * 1024)
                cpu_after = process.cpu_percent()
                
                # Store results
                if rtf < 10:  # Filter out unrealistic RTF values
                    rtf_values.append(rtf)
                    generation_times.append(gen_time)
                    audio_durations.append(audio_duration)
                    memory_values.append(max(memory_before, memory_after))
                    cpu_values.append(max(cpu_before, cpu_after))
                
                logger.debug(f"  Iteration {i+1}: RTF={rtf:.3f}, Gen={gen_time:.3f}s, Audio={audio_duration:.2f}s")
                
            except Exception as e:
                logger.warning(f"  Iteration {i+1} failed: {e}")
                errors += 1
        
        total_test_time = time.time() - total_start
        
        # Calculate statistics
        if rtf_values:
            result = ModelBenchmarkResult(
                model_name=model_name,
                model_path=model_path,
                model_size_mb=model_size_mb,
                avg_rtf=statistics.mean(rtf_values),
                min_rtf=min(rtf_values),
                max_rtf=max(rtf_values),
                median_rtf=statistics.median(rtf_values),
                std_rtf=statistics.stdev(rtf_values) if len(rtf_values) > 1 else 0,
                avg_generation_time=statistics.mean(generation_times),
                avg_audio_duration=statistics.mean(audio_durations),
                load_time=load_time,
                peak_memory_mb=max(memory_values) if memory_values else 0,
                avg_cpu_percent=statistics.mean(cpu_values) if cpu_values else 0,
                success_rate=(iterations - errors) / iterations * 100,
                error_count=errors,
                test_count=iterations,
                total_test_time=total_test_time
            )
        else:
            result = ModelBenchmarkResult(
                model_name=model_name,
                model_path=model_path,
                model_size_mb=model_size_mb,
                avg_rtf=float('inf'),
                min_rtf=float('inf'),
                max_rtf=float('inf'),
                median_rtf=float('inf'),
                std_rtf=0,
                avg_generation_time=0,
                avg_audio_duration=0,
                load_time=load_time,
                peak_memory_mb=0,
                avg_cpu_percent=0,
                success_rate=0,
                error_count=errors,
                test_count=iterations,
                total_test_time=total_test_time
            )
        
        logger.info(f"  ✅ Results: RTF={result.avg_rtf:.3f} (±{result.std_rtf:.3f}), Success={result.success_rate:.1f}%")
        return result
    
    def run_comprehensive_benchmark(self, iterations: int = 10) -> Dict[str, Any]:
        """Run comprehensive benchmark on all available models"""
        logger.info("🚀 Starting comprehensive model benchmark")
        
        models = self.discover_models()
        if not models:
            logger.error("No models found for benchmarking")
            return {"error": "No models found"}
        
        logger.info(f"📊 Found {len(models)} models to benchmark")
        
        results = []
        
        for model_name, model_path, model_size_mb in models:
            result = self.benchmark_model(model_name, model_path, model_size_mb, iterations)
            results.append(result)
        
        # Analyze results
        analysis = self.analyze_results(results)
        
        return {
            "results": [asdict(r) for r in results],
            "analysis": analysis,
            "benchmark_info": {
                "iterations_per_model": iterations,
                "test_texts": len(self.test_texts),
                "test_voices": len(self.test_voices),
                "total_models": len(models)
            }
        }
    
    def analyze_results(self, results: List[ModelBenchmarkResult]) -> Dict[str, Any]:
        """Analyze benchmark results and provide recommendations"""
        
        # Filter successful results
        successful_results = [r for r in results if r.success_rate > 50 and r.avg_rtf < 10]
        
        if not successful_results:
            return {"error": "No successful benchmark results"}
        
        # Find best performers
        best_rtf = min(successful_results, key=lambda r: r.avg_rtf)
        best_memory = min(successful_results, key=lambda r: r.peak_memory_mb)
        best_load_time = min(successful_results, key=lambda r: r.load_time)
        fastest_generation = min(successful_results, key=lambda r: r.avg_generation_time)
        
        # Calculate efficiency scores (lower RTF + lower memory = better)
        for result in successful_results:
            result.efficiency_score = (result.avg_rtf * 0.7) + (result.peak_memory_mb / 1000 * 0.3)
        
        best_overall = min(successful_results, key=lambda r: r.efficiency_score)
        
        # Performance tiers
        excellent_rtf = [r for r in successful_results if r.avg_rtf < 0.3]
        good_rtf = [r for r in successful_results if 0.3 <= r.avg_rtf < 0.6]
        fair_rtf = [r for r in successful_results if 0.6 <= r.avg_rtf < 1.0]
        
        return {
            "best_performers": {
                "best_rtf": {
                    "model": best_rtf.model_name,
                    "rtf": best_rtf.avg_rtf,
                    "memory_mb": best_rtf.peak_memory_mb,
                    "size_mb": best_rtf.model_size_mb
                },
                "best_memory": {
                    "model": best_memory.model_name,
                    "rtf": best_memory.avg_rtf,
                    "memory_mb": best_memory.peak_memory_mb,
                    "size_mb": best_memory.model_size_mb
                },
                "best_overall": {
                    "model": best_overall.model_name,
                    "rtf": best_overall.avg_rtf,
                    "memory_mb": best_overall.peak_memory_mb,
                    "size_mb": best_overall.model_size_mb,
                    "efficiency_score": best_overall.efficiency_score
                }
            },
            "performance_tiers": {
                "excellent": [{"model": r.model_name, "rtf": r.avg_rtf} for r in excellent_rtf],
                "good": [{"model": r.model_name, "rtf": r.avg_rtf} for r in good_rtf],
                "fair": [{"model": r.model_name, "rtf": r.avg_rtf} for r in fair_rtf]
            },
            "recommendations": {
                "production": best_overall.model_name,
                "low_memory": best_memory.model_name,
                "fastest_rtf": best_rtf.model_name,
                "balanced": best_overall.model_name
            },
            "summary": {
                "total_models_tested": len(results),
                "successful_models": len(successful_results),
                "best_rtf_achieved": best_rtf.avg_rtf,
                "memory_range_mb": f"{best_memory.peak_memory_mb:.0f}-{max(r.peak_memory_mb for r in successful_results):.0f}"
            }
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save benchmark results to file"""
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"docs/benchmark_results_{timestamp}.json"
        
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📁 Results saved to: {filename}")
        return filename

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark Kokoro TTS model variants")
    parser.add_argument("--iterations", "-i", type=int, default=10, help="Iterations per model")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    benchmarker = ModelBenchmarker()
    
    try:
        results = benchmarker.run_comprehensive_benchmark(args.iterations)
        
        if "error" in results:
            logger.error(f"Benchmark failed: {results['error']}")
            return 1
        
        # Save results
        output_file = benchmarker.save_results(results, args.output)
        
        # Print summary
        analysis = results["analysis"]
        print("\n" + "="*60)
        print("🏆 MODEL BENCHMARK RESULTS")
        print("="*60)
        
        print(f"\n📊 Summary:")
        print(f"  Models Tested: {analysis['summary']['total_models_tested']}")
        print(f"  Successful: {analysis['summary']['successful_models']}")
        print(f"  Best RTF: {analysis['summary']['best_rtf_achieved']:.3f}")
        print(f"  Memory Range: {analysis['summary']['memory_range_mb']} MB")
        
        print(f"\n🏆 Best Performers:")
        best = analysis["best_performers"]
        print(f"  🚀 Best RTF: {best['best_rtf']['model']} (RTF: {best['best_rtf']['rtf']:.3f})")
        print(f"  💾 Best Memory: {best['best_memory']['model']} ({best['best_memory']['memory_mb']:.0f}MB)")
        print(f"  ⚖️ Best Overall: {best['best_overall']['model']} (Score: {best['best_overall']['efficiency_score']:.3f})")
        
        print(f"\n🎯 Recommendations:")
        rec = analysis["recommendations"]
        print(f"  Production: {rec['production']}")
        print(f"  Low Memory: {rec['low_memory']}")
        print(f"  Fastest RTF: {rec['fastest_rtf']}")
        
        print(f"\n📁 Detailed results saved to: {output_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())