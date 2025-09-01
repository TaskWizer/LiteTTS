#!/usr/bin/env python3
"""
Comprehensive Performance Benchmarking Framework
Enhanced RTF benchmarking with CPU utilization, thermal monitoring, and multi-model testing
"""

import os
import sys
import json
import logging
import asyncio
import aiohttp
import time
import psutil
import statistics
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor
import subprocess

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    # Core TTS metrics
    rtf: float = 0.0
    generation_time: float = 0.0
    audio_duration: float = 0.0
    text_length: int = 0
    words_per_minute: float = 0.0
    
    # System metrics
    cpu_usage_avg: float = 0.0
    cpu_usage_peak: float = 0.0
    memory_usage_mb: float = 0.0
    memory_peak_mb: float = 0.0
    cpu_temperature: float = 0.0
    
    # Model metrics
    model_variant: str = ""
    voice_model: str = ""
    
    # Quality indicators
    audio_size_bytes: int = 0
    sample_rate: int = 0
    
    # Test metadata
    test_category: str = ""
    timestamp: float = field(default_factory=time.time)

@dataclass
class BenchmarkResult:
    """Complete benchmark result"""
    test_id: str
    input_text: str
    metrics: PerformanceMetrics
    success: bool
    error_message: str = ""

class SystemMonitor:
    """System resource monitoring during benchmarks"""
    
    def __init__(self):
        self.monitoring = False
        self.cpu_readings = []
        self.memory_readings = []
        self.temperature_readings = []
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring = True
        self.cpu_readings = []
        self.memory_readings = []
        self.temperature_readings = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        
    def stop_monitoring(self) -> Dict[str, float]:
        """Stop monitoring and return statistics"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        return {
            "cpu_avg": statistics.mean(self.cpu_readings) if self.cpu_readings else 0.0,
            "cpu_peak": max(self.cpu_readings) if self.cpu_readings else 0.0,
            "memory_avg": statistics.mean(self.memory_readings) if self.memory_readings else 0.0,
            "memory_peak": max(self.memory_readings) if self.memory_readings else 0.0,
            "temperature_avg": statistics.mean(self.temperature_readings) if self.temperature_readings else 0.0
        }
    
    def _monitor_loop(self):
        """Monitoring loop"""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                self.cpu_readings.append(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.memory_readings.append(memory.used / (1024 * 1024))  # MB
                
                # Temperature (if available)
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Get CPU temperature if available
                        for name, entries in temps.items():
                            if 'cpu' in name.lower() or 'core' in name.lower():
                                for entry in entries:
                                    if entry.current:
                                        self.temperature_readings.append(entry.current)
                                        break
                                break
                except:
                    pass  # Temperature monitoring not available
                
                time.sleep(0.5)  # Monitor every 500ms
            except Exception as e:
                logger.warning(f"Monitoring error: {e}")

class ComprehensivePerformanceBenchmarker:
    """Comprehensive performance benchmarking framework"""
    
    def __init__(self, api_base_url: str = "http://localhost:8354"):
        self.api_base_url = api_base_url
        self.results_dir = Path("test_results/comprehensive_performance")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # System monitor
        self.system_monitor = SystemMonitor()
        
        # Test configurations
        self.model_variants = ["model_q4.onnx", "model_f16.onnx", "model_q8f16.onnx"]
        self.voice_models = ["af_heart", "af_sky", "am_adam", "am_michael"]
        
        # Create comprehensive test cases
        self.test_cases = self._create_performance_test_cases()
        
    def _create_performance_test_cases(self) -> List[Dict[str, Any]]:
        """Create comprehensive performance test cases"""
        test_cases = []
        
        # Short text performance tests (< 20 characters)
        short_texts = [
            "Hi",
            "Hello",
            "Good morning",
            "How are you?",
            "Thank you very much"
        ]
        
        for i, text in enumerate(short_texts):
            test_cases.append({
                "test_id": f"short_text_{i+1}",
                "input_text": text,
                "category": "short_text",
                "target_rtf": 0.2,
                "description": f"Short text performance: {len(text)} chars"
            })
        
        # Medium text performance tests (20-100 characters)
        medium_texts = [
            "The quick brown fox jumps over the lazy dog",
            "This is a medium length sentence for testing purposes",
            "Performance testing with various sentence structures and lengths",
            "Natural language processing requires careful attention to detail",
            "Text-to-speech systems must balance quality with processing speed"
        ]
        
        for i, text in enumerate(medium_texts):
            test_cases.append({
                "test_id": f"medium_text_{i+1}",
                "input_text": text,
                "category": "medium_text",
                "target_rtf": 0.25,
                "description": f"Medium text performance: {len(text)} chars"
            })
        
        # Long text performance tests (> 100 characters)
        long_texts = [
            "This is a comprehensive test of the text-to-speech system's ability to handle longer passages of text while maintaining both quality and performance. The system should process this text efficiently while preserving natural speech patterns and pronunciation accuracy.",
            "Performance benchmarking is essential for ensuring that text-to-speech systems meet production requirements. This includes measuring real-time factor, CPU utilization, memory usage, and thermal characteristics under various workloads and text lengths.",
            "The Kokoro ONNX TTS API represents a significant advancement in neural text-to-speech technology, combining high-quality audio generation with optimized performance characteristics suitable for production deployment in various environments and use cases."
        ]
        
        for i, text in enumerate(long_texts):
            test_cases.append({
                "test_id": f"long_text_{i+1}",
                "input_text": text,
                "category": "long_text",
                "target_rtf": 0.25,
                "description": f"Long text performance: {len(text)} chars"
            })
        
        # Stress test cases
        stress_texts = [
            "A" * 50,  # Repetitive short
            "The quick brown fox jumps over the lazy dog. " * 5,  # Repetitive medium
            "Performance testing with numbers: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10. Special characters: @, #, $, %, &, *, +, =. Punctuation: ?, !, ., ,, ;, :. Mixed content for comprehensive evaluation.",
        ]
        
        for i, text in enumerate(stress_texts):
            test_cases.append({
                "test_id": f"stress_test_{i+1}",
                "input_text": text,
                "category": "stress_test",
                "target_rtf": 0.3,
                "description": f"Stress test: {len(text)} chars"
            })
        
        return test_cases
    
    async def generate_audio_with_monitoring(self, text: str, voice: str = "af_heart") -> Tuple[bool, bytes, float, Dict[str, float], str]:
        """Generate audio with system monitoring"""
        try:
            # Start system monitoring
            self.system_monitor.start_monitoring()
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    'model': 'kokoro',
                    'input': text,
                    'voice': voice,
                    'response_format': 'wav'
                }
                
                async with session.post(
                    f"{self.api_base_url}/v1/audio/speech",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    generation_time = time.time() - start_time
                    
                    # Stop monitoring
                    system_stats = self.system_monitor.stop_monitoring()
                    
                    if response.status == 200:
                        audio_data = await response.read()
                        return True, audio_data, generation_time, system_stats, ""
                    else:
                        error_text = await response.text()
                        return False, b"", generation_time, system_stats, f"HTTP {response.status}: {error_text}"
                        
        except Exception as e:
            generation_time = time.time() - start_time
            system_stats = self.system_monitor.stop_monitoring()
            return False, b"", generation_time, system_stats, str(e)
    
    def analyze_audio_properties(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze audio properties"""
        try:
            import wave
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            with wave.open(temp_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
                channels = wav_file.getnchannels()
            
            os.unlink(temp_path)
            
            return {
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": channels,
                "size_bytes": len(audio_data)
            }
            
        except Exception as e:
            logger.warning(f"Audio analysis failed: {e}")
            return {
                "duration": 0.0,
                "sample_rate": 0,
                "channels": 0,
                "size_bytes": len(audio_data)
            }
    
    async def benchmark_single_case(self, test_case: Dict[str, Any], voice: str = "af_heart", model_variant: str = "model_q4.onnx") -> BenchmarkResult:
        """Benchmark a single test case"""
        logger.info(f"Benchmarking: {test_case['test_id']} - {test_case['description']} (Voice: {voice}, Model: {model_variant})")
        
        # Generate audio with monitoring
        success, audio_data, generation_time, system_stats, error = await self.generate_audio_with_monitoring(
            test_case["input_text"], voice
        )
        
        if not success:
            logger.error(f"Benchmark failed for {test_case['test_id']}: {error}")
            return BenchmarkResult(
                test_id=test_case["test_id"],
                input_text=test_case["input_text"],
                metrics=PerformanceMetrics(
                    generation_time=generation_time,
                    text_length=len(test_case["input_text"]),
                    model_variant=model_variant,
                    voice_model=voice,
                    test_category=test_case["category"]
                ),
                success=False,
                error_message=error
            )
        
        # Analyze audio properties
        audio_props = self.analyze_audio_properties(audio_data)
        duration = audio_props.get("duration", 0)
        
        # Calculate performance metrics
        rtf = generation_time / duration if duration > 0 else float('inf')
        words = len(test_case["input_text"].split())
        words_per_minute = (words * 60) / duration if duration > 0 else 0
        
        metrics = PerformanceMetrics(
            rtf=rtf,
            generation_time=generation_time,
            audio_duration=duration,
            text_length=len(test_case["input_text"]),
            words_per_minute=words_per_minute,
            cpu_usage_avg=system_stats.get("cpu_avg", 0),
            cpu_usage_peak=system_stats.get("cpu_peak", 0),
            memory_usage_mb=system_stats.get("memory_avg", 0),
            memory_peak_mb=system_stats.get("memory_peak", 0),
            cpu_temperature=system_stats.get("temperature_avg", 0),
            model_variant=model_variant,
            voice_model=voice,
            audio_size_bytes=audio_props.get("size_bytes", 0),
            sample_rate=audio_props.get("sample_rate", 0),
            test_category=test_case["category"]
        )
        
        logger.info(f"Completed: {test_case['test_id']} - RTF: {rtf:.3f}, CPU: {system_stats.get('cpu_avg', 0):.1f}%, Memory: {system_stats.get('memory_avg', 0):.1f}MB")
        
        return BenchmarkResult(
            test_id=test_case["test_id"],
            input_text=test_case["input_text"],
            metrics=metrics,
            success=True
        )

    async def run_comprehensive_benchmarks(self, max_concurrent: int = 2) -> Dict[str, Any]:
        """Run comprehensive performance benchmarks"""
        logger.info("Starting comprehensive performance benchmarks...")

        all_results = []
        category_stats = {}
        model_stats = {}
        voice_stats = {}

        # Test with primary voice and model first
        primary_voice = "af_heart"
        primary_model = "model_q4.onnx"

        logger.info(f"Running primary benchmarks with {primary_voice} voice and {primary_model} model...")

        for test_case in self.test_cases:
            result = await self.benchmark_single_case(test_case, primary_voice, primary_model)
            all_results.append(result)

            # Categorize results
            category = test_case["category"]
            if category not in category_stats:
                category_stats[category] = []
            category_stats[category].append(result)

        # Test with additional voices (subset of tests)
        logger.info("Running voice comparison benchmarks...")
        comparison_tests = [tc for tc in self.test_cases if tc["category"] in ["short_text", "medium_text"]]

        for voice in ["af_sky", "am_adam"]:
            logger.info(f"Testing voice: {voice}")
            voice_results = []

            for test_case in comparison_tests[:3]:  # Limit to 3 tests per voice
                result = await self.benchmark_single_case(test_case, voice, primary_model)
                all_results.append(result)
                voice_results.append(result)

            if voice_results:
                voice_stats[voice] = {
                    "avg_rtf": statistics.mean(r.metrics.rtf for r in voice_results if r.success),
                    "avg_cpu": statistics.mean(r.metrics.cpu_usage_avg for r in voice_results if r.success),
                    "total_tests": len(voice_results)
                }

        # Calculate category statistics
        for category, results in category_stats.items():
            successful_results = [r for r in results if r.success]
            if successful_results:
                category_stats[category] = {
                    "total_tests": len(results),
                    "successful_tests": len(successful_results),
                    "avg_rtf": statistics.mean(r.metrics.rtf for r in successful_results),
                    "avg_cpu": statistics.mean(r.metrics.cpu_usage_avg for r in successful_results),
                    "avg_memory": statistics.mean(r.metrics.memory_usage_mb for r in successful_results),
                    "rtf_target_compliance": sum(1 for r in successful_results if r.metrics.rtf <= 0.25) / len(successful_results),
                    "performance_grade": self._calculate_category_grade(successful_results)
                }

        # Generate overall performance summary
        successful_results = [r for r in all_results if r.success]
        overall_stats = self._calculate_overall_stats(successful_results)

        # Generate report
        report = {
            "benchmark_timestamp": time.time(),
            "total_tests": len(all_results),
            "successful_tests": len(successful_results),
            "overall_performance": overall_stats,
            "category_performance": category_stats,
            "voice_performance": voice_stats,
            "detailed_results": [asdict(r) for r in all_results],
            "performance_analysis": self._analyze_performance_trends(successful_results),
            "optimization_recommendations": self._generate_optimization_recommendations(overall_stats, category_stats),
            "system_requirements": self._analyze_system_requirements(successful_results)
        }

        # Save results
        results_file = self.results_dir / f"comprehensive_benchmarks_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Comprehensive benchmarks completed. Results saved to: {results_file}")
        return report

    def _calculate_category_grade(self, results: List[BenchmarkResult]) -> str:
        """Calculate performance grade for a category"""
        if not results:
            return "N/A"

        avg_rtf = statistics.mean(r.metrics.rtf for r in results)
        rtf_compliance = sum(1 for r in results if r.metrics.rtf <= 0.25) / len(results)

        if avg_rtf <= 0.2 and rtf_compliance >= 0.9:
            return "A+"
        elif avg_rtf <= 0.25 and rtf_compliance >= 0.8:
            return "A"
        elif avg_rtf <= 0.3 and rtf_compliance >= 0.7:
            return "B"
        elif avg_rtf <= 0.4:
            return "C"
        else:
            return "D"

    def _calculate_overall_stats(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Calculate overall performance statistics"""
        if not results:
            return {}

        rtf_values = [r.metrics.rtf for r in results]
        cpu_values = [r.metrics.cpu_usage_avg for r in results]
        memory_values = [r.metrics.memory_usage_mb for r in results]

        return {
            "avg_rtf": statistics.mean(rtf_values),
            "median_rtf": statistics.median(rtf_values),
            "rtf_std": statistics.stdev(rtf_values) if len(rtf_values) > 1 else 0,
            "rtf_target_compliance": sum(1 for rtf in rtf_values if rtf <= 0.25) / len(rtf_values),
            "short_text_rtf_compliance": self._calculate_short_text_compliance(results),
            "avg_cpu_usage": statistics.mean(cpu_values),
            "peak_cpu_usage": max(r.metrics.cpu_usage_peak for r in results),
            "avg_memory_usage": statistics.mean(memory_values),
            "peak_memory_usage": max(r.metrics.memory_peak_mb for r in results),
            "overall_grade": self._calculate_overall_grade(results)
        }

    def _calculate_short_text_compliance(self, results: List[BenchmarkResult]) -> float:
        """Calculate RTF compliance for short text (< 20 chars)"""
        short_text_results = [r for r in results if r.metrics.text_length < 20]
        if not short_text_results:
            return 0.0

        compliant = sum(1 for r in short_text_results if r.metrics.rtf <= 0.2)
        return compliant / len(short_text_results)

    def _calculate_overall_grade(self, results: List[BenchmarkResult]) -> str:
        """Calculate overall performance grade"""
        if not results:
            return "N/A"

        avg_rtf = statistics.mean(r.metrics.rtf for r in results)
        rtf_compliance = sum(1 for r in results if r.metrics.rtf <= 0.25) / len(results)
        avg_cpu = statistics.mean(r.metrics.cpu_usage_avg for r in results)

        # Grade based on multiple factors
        score = 0
        if avg_rtf <= 0.2:
            score += 3
        elif avg_rtf <= 0.25:
            score += 2
        elif avg_rtf <= 0.3:
            score += 1

        if rtf_compliance >= 0.9:
            score += 2
        elif rtf_compliance >= 0.8:
            score += 1

        if avg_cpu <= 50:
            score += 1

        if score >= 5:
            return "A+"
        elif score >= 4:
            return "A"
        elif score >= 3:
            return "B"
        elif score >= 2:
            return "C"
        else:
            return "D"

    def _analyze_performance_trends(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Analyze performance trends"""
        trends = {
            "text_length_correlation": self._analyze_text_length_correlation(results),
            "cpu_utilization_patterns": self._analyze_cpu_patterns(results),
            "memory_usage_patterns": self._analyze_memory_patterns(results),
            "bottleneck_analysis": self._identify_bottlenecks(results)
        }
        return trends

    def _analyze_text_length_correlation(self, results: List[BenchmarkResult]) -> Dict[str, float]:
        """Analyze correlation between text length and performance"""
        if len(results) < 2:
            return {"correlation": 0.0}

        text_lengths = [r.metrics.text_length for r in results]
        rtf_values = [r.metrics.rtf for r in results]

        # Simple correlation calculation
        n = len(text_lengths)
        sum_x = sum(text_lengths)
        sum_y = sum(rtf_values)
        sum_xy = sum(x * y for x, y in zip(text_lengths, rtf_values))
        sum_x2 = sum(x * x for x in text_lengths)
        sum_y2 = sum(y * y for y in rtf_values)

        correlation = (n * sum_xy - sum_x * sum_y) / ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5

        return {
            "correlation": correlation,
            "interpretation": "positive" if correlation > 0.3 else "negative" if correlation < -0.3 else "weak"
        }

    def _analyze_cpu_patterns(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Analyze CPU utilization patterns"""
        cpu_values = [r.metrics.cpu_usage_avg for r in results]
        cpu_peaks = [r.metrics.cpu_usage_peak for r in results]

        return {
            "avg_utilization": statistics.mean(cpu_values),
            "peak_utilization": max(cpu_peaks),
            "utilization_efficiency": statistics.mean(cpu_values) / max(cpu_peaks) if max(cpu_peaks) > 0 else 0,
            "high_utilization_tests": sum(1 for cpu in cpu_values if cpu > 80)
        }

    def _analyze_memory_patterns(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Analyze memory usage patterns"""
        memory_values = [r.metrics.memory_usage_mb for r in results]
        memory_peaks = [r.metrics.memory_peak_mb for r in results]

        return {
            "avg_usage_mb": statistics.mean(memory_values),
            "peak_usage_mb": max(memory_peaks),
            "memory_efficiency": statistics.mean(memory_values) / max(memory_peaks) if max(memory_peaks) > 0 else 0,
            "high_memory_tests": sum(1 for mem in memory_values if mem > 500)
        }

    def _identify_bottlenecks(self, results: List[BenchmarkResult]) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        # RTF bottlenecks
        high_rtf_results = [r for r in results if r.metrics.rtf > 0.3]
        if len(high_rtf_results) > len(results) * 0.2:
            bottlenecks.append("High RTF values indicate processing speed bottleneck")

        # CPU bottlenecks
        high_cpu_results = [r for r in results if r.metrics.cpu_usage_avg > 80]
        if len(high_cpu_results) > len(results) * 0.3:
            bottlenecks.append("High CPU utilization indicates compute bottleneck")

        # Memory bottlenecks
        high_memory_results = [r for r in results if r.metrics.memory_usage_mb > 500]
        if len(high_memory_results) > len(results) * 0.2:
            bottlenecks.append("High memory usage indicates memory bottleneck")

        return bottlenecks

    def _generate_optimization_recommendations(self, overall_stats: Dict[str, Any], category_stats: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # RTF optimization
        if overall_stats.get("avg_rtf", 0) > 0.25:
            recommendations.append(f"Optimize processing speed: Average RTF {overall_stats['avg_rtf']:.3f} exceeds target 0.25")

        # Short text optimization
        if overall_stats.get("short_text_rtf_compliance", 0) < 0.8:
            recommendations.append("Optimize short text processing for RTF < 0.2 target")

        # CPU optimization
        if overall_stats.get("avg_cpu_usage", 0) > 70:
            recommendations.append("Implement CPU optimization strategies for better utilization")

        # Memory optimization
        if overall_stats.get("avg_memory_usage", 0) > 300:
            recommendations.append("Optimize memory usage to reduce resource consumption")

        # Category-specific recommendations
        for category, stats in category_stats.items():
            if stats.get("performance_grade", "A") in ["C", "D"]:
                recommendations.append(f"Focus optimization efforts on {category} category")

        return recommendations

    def _analyze_system_requirements(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Analyze system requirements based on benchmark results"""
        if not results:
            return {}

        return {
            "recommended_cpu_cores": max(2, int(statistics.mean(r.metrics.cpu_usage_avg for r in results) / 25)),
            "recommended_memory_gb": max(2, int(statistics.mean(r.metrics.memory_usage_mb for r in results) / 512)),
            "minimum_memory_mb": max(r.metrics.memory_peak_mb for r in results),
            "thermal_considerations": max(r.metrics.cpu_temperature for r in results) > 70,
            "concurrent_request_capacity": int(100 / max(r.metrics.cpu_usage_avg for r in results)) if max(r.metrics.cpu_usage_avg for r in results) > 0 else 10
        }

async def main():
    """Main function to run comprehensive performance benchmarks"""
    benchmarker = ComprehensivePerformanceBenchmarker()

    try:
        report = await benchmarker.run_comprehensive_benchmarks()

        print("\n" + "="*80)
        print("COMPREHENSIVE PERFORMANCE BENCHMARKS SUMMARY")
        print("="*80)

        overall = report["overall_performance"]
        print(f"Total Tests: {report['total_tests']}")
        print(f"Successful Tests: {report['successful_tests']}")
        print(f"Overall Grade: {overall['overall_grade']}")

        print(f"\nPerformance Metrics:")
        print(f"  Average RTF: {overall['avg_rtf']:.3f}")
        print(f"  RTF Target Compliance: {overall['rtf_target_compliance']:.1%}")
        print(f"  Short Text RTF Compliance: {overall['short_text_rtf_compliance']:.1%}")
        print(f"  Average CPU Usage: {overall['avg_cpu_usage']:.1f}%")
        print(f"  Peak CPU Usage: {overall['peak_cpu_usage']:.1f}%")
        print(f"  Average Memory Usage: {overall['avg_memory_usage']:.1f} MB")
        print(f"  Peak Memory Usage: {overall['peak_memory_usage']:.1f} MB")

        print(f"\nCategory Performance:")
        for category, stats in report["category_performance"].items():
            print(f"  {category}: Grade {stats['performance_grade']}, RTF {stats['avg_rtf']:.3f}, CPU {stats['avg_cpu']:.1f}%")

        print(f"\nOptimization Recommendations:")
        for i, rec in enumerate(report["optimization_recommendations"], 1):
            print(f"  {i}. {rec}")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"Benchmarking failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())
