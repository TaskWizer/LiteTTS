#!/usr/bin/env python3
"""
RTF (Real-Time Factor) Benchmarking Script for Kokoro TTS
Tests performance improvements from optimizations
"""

import os
import sys
import time
import json
import logging
import statistics
from pathlib import Path
from typing import List, Dict, Any
import argparse

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment for benchmarking"""
    # Apply CPU optimizations
    try:
        from LiteTTS.performance.cpu_optimizer import get_cpu_optimizer
        cpu_optimizer = get_cpu_optimizer()
        env_vars = cpu_optimizer.optimize_environment_variables()
        
        for key, value in env_vars.items():
            os.environ[key] = value
        
        logger.info(f"Applied CPU optimizations: {list(env_vars.keys())}")
        return cpu_optimizer.cpu_info
        
    except ImportError:
        logger.warning("CPU optimizer not available, using default settings")
        return None

def benchmark_single_synthesis(text: str, voice: str = "af_heart", iterations: int = 5) -> Dict[str, float]:
    """Benchmark a single text synthesis using direct kokoro_onnx"""
    try:
        # Import and initialize kokoro_onnx directly
        import kokoro_onnx
        import numpy as np

        # Apply patches first
        from LiteTTS.patches import apply_all_patches
        apply_all_patches()

        # Initialize model
        model_path = "LiteTTS/models/model_q4.onnx"
        voices_path = "LiteTTS/voices/combined_voices.npz"

        logger.info(f"Loading model: {model_path}")
        logger.info(f"Loading voices: {voices_path}")

        kokoro = kokoro_onnx.Kokoro(model_path, voices_path)

        rtf_values = []
        synthesis_times = []
        audio_durations = []

        for i in range(iterations):
            start_time = time.time()

            # Perform synthesis
            audio, sample_rate = kokoro.create(text, voice, speed=1.0)

            synthesis_time = time.time() - start_time

            # Calculate audio duration
            audio_duration = len(audio) / sample_rate
            rtf = synthesis_time / audio_duration if audio_duration > 0 else float('inf')

            rtf_values.append(rtf)
            synthesis_times.append(synthesis_time)
            audio_durations.append(audio_duration)

            logger.info(f"Iteration {i+1}: RTF={rtf:.3f}, synthesis={synthesis_time:.3f}s, audio={audio_duration:.3f}s")

        return {
            'rtf_mean': statistics.mean(rtf_values),
            'rtf_median': statistics.median(rtf_values),
            'rtf_min': min(rtf_values),
            'rtf_max': max(rtf_values),
            'rtf_stdev': statistics.stdev(rtf_values) if len(rtf_values) > 1 else 0,
            'synthesis_time_mean': statistics.mean(synthesis_times),
            'audio_duration_mean': statistics.mean(audio_durations),
            'iterations': iterations
        }

    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {'error': str(e)}

def benchmark_batch_synthesis(texts: List[str], voice: str = "af_heart") -> Dict[str, float]:
    """Benchmark batch synthesis performance using direct kokoro_onnx"""
    try:
        import kokoro_onnx
        from concurrent.futures import ThreadPoolExecutor

        # Apply patches first
        from LiteTTS.patches import apply_all_patches
        apply_all_patches()

        # Initialize model
        model_path = "LiteTTS/models/model_q4.onnx"
        voices_path = "LiteTTS/voices/combined_voices.npz"

        kokoro = kokoro_onnx.Kokoro(model_path, voices_path)

        # Test single-threaded processing
        start_time = time.time()
        single_results = []
        total_audio_duration = 0

        for text in texts:
            audio, sample_rate = kokoro.create(text, voice, speed=1.0)
            single_results.append(audio)
            total_audio_duration += len(audio) / sample_rate

        single_time = time.time() - start_time

        # Test multi-threaded processing
        def synthesize_text(text):
            return kokoro.create(text, voice, speed=1.0)

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            batch_results = list(executor.map(synthesize_text, texts))
        batch_time = time.time() - start_time

        results = {
            'single_threaded_time': single_time,
            'single_threaded_rtf': single_time / total_audio_duration if total_audio_duration > 0 else float('inf'),
            'batch_time': batch_time,
            'batch_rtf': batch_time / total_audio_duration if total_audio_duration > 0 else float('inf'),
            'speedup_factor': single_time / batch_time if batch_time > 0 else 1.0,
            'batch_count': len(texts),
            'total_audio_duration': total_audio_duration
        }

        return results

    except Exception as e:
        logger.error(f"Batch benchmark failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {'error': str(e)}

def run_comprehensive_benchmark() -> Dict[str, Any]:
    """Run comprehensive RTF benchmarks"""
    logger.info("Starting comprehensive RTF benchmark...")
    
    # Test texts of varying lengths
    test_texts = [
        "Hello world!",  # Short
        "This is a medium length sentence for testing TTS performance.",  # Medium
        "This is a much longer text that will test the performance of the TTS system with more complex synthesis requirements and longer processing times.",  # Long
        "The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet and is commonly used for testing purposes."  # Complex
    ]
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'cpu_info': None,
        'single_synthesis': {},
        'batch_synthesis': {},
        'summary': {}
    }
    
    # Setup environment and get CPU info
    cpu_info = setup_environment()
    if cpu_info:
        results['cpu_info'] = {
            'model_name': cpu_info.model_name,
            'total_cores': cpu_info.total_cores,
            'physical_cores': cpu_info.physical_cores,
            'logical_cores': cpu_info.logical_cores,
            'has_hyperthreading': cpu_info.has_hyperthreading,
            'supports_avx2': cpu_info.supports_avx2,
            'supports_avx512': cpu_info.supports_avx512
        }
    
    # Benchmark single synthesis for each test text
    logger.info("Benchmarking single synthesis...")
    for i, text in enumerate(test_texts):
        text_label = f"text_{i+1}_{'short' if len(text) < 50 else 'medium' if len(text) < 150 else 'long'}"
        logger.info(f"Testing {text_label}: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        benchmark_result = benchmark_single_synthesis(text, iterations=3)
        results['single_synthesis'][text_label] = benchmark_result
    
    # Benchmark batch synthesis
    logger.info("Benchmarking batch synthesis...")
    batch_result = benchmark_batch_synthesis(test_texts)
    results['batch_synthesis'] = batch_result
    
    # Calculate summary statistics
    rtf_values = []
    for test_result in results['single_synthesis'].values():
        if 'rtf_mean' in test_result:
            rtf_values.append(test_result['rtf_mean'])
    
    if rtf_values:
        results['summary'] = {
            'overall_rtf_mean': statistics.mean(rtf_values),
            'overall_rtf_median': statistics.median(rtf_values),
            'overall_rtf_min': min(rtf_values),
            'overall_rtf_max': max(rtf_values),
            'performance_rating': 'excellent' if statistics.mean(rtf_values) < 0.3 else 
                                 'good' if statistics.mean(rtf_values) < 0.5 else
                                 'acceptable' if statistics.mean(rtf_values) < 1.0 else 'poor'
        }
    
    return results

def main():
    """Main benchmark function"""
    parser = argparse.ArgumentParser(description='Benchmark Kokoro TTS RTF performance')
    parser.add_argument('--output', '-o', type=str, help='Output JSON file for results')
    parser.add_argument('--text', '-t', type=str, help='Custom text to benchmark')
    parser.add_argument('--voice', '-v', type=str, default='af_heart', help='Voice to use for testing')
    parser.add_argument('--iterations', '-i', type=int, default=5, help='Number of iterations per test')
    
    args = parser.parse_args()
    
    try:
        if args.text:
            # Benchmark custom text
            logger.info(f"Benchmarking custom text: '{args.text[:50]}{'...' if len(args.text) > 50 else ''}'")
            results = benchmark_single_synthesis(args.text, args.voice, args.iterations)
            
            print(f"\nBenchmark Results:")
            rtf_mean = results.get('rtf_mean', 0)
            rtf_median = results.get('rtf_median', 0)
            rtf_min = results.get('rtf_min', 0)
            rtf_max = results.get('rtf_max', 0)
            synthesis_time = results.get('synthesis_time_mean', 0)

            if rtf_mean > 0:
                print(f"RTF Mean: {rtf_mean:.3f}")
                print(f"RTF Median: {rtf_median:.3f}")
                print(f"RTF Range: {rtf_min:.3f} - {rtf_max:.3f}")
                print(f"Synthesis Time: {synthesis_time:.3f}s")
            else:
                print("Benchmark failed - no valid results")
            
        else:
            # Run comprehensive benchmark
            results = run_comprehensive_benchmark()
            
            print(f"\nComprehensive Benchmark Results:")
            summary = results.get('summary', {})
            rtf_mean = summary.get('overall_rtf_mean', 0)
            rtf_min = summary.get('overall_rtf_min', 0)
            rtf_max = summary.get('overall_rtf_max', 0)

            if rtf_mean > 0:
                print(f"Overall RTF Mean: {rtf_mean:.3f}")
                print(f"Overall RTF Range: {rtf_min:.3f} - {rtf_max:.3f}")
                print(f"Performance Rating: {summary.get('performance_rating', 'N/A')}")
            else:
                print("Comprehensive benchmark failed - no valid results")

            batch_results = results.get('batch_synthesis', {})
            if 'speedup_factor' in batch_results:
                speedup = batch_results['speedup_factor']
                print(f"Batch Processing Speedup: {speedup:.2f}x")
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {args.output}")
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
