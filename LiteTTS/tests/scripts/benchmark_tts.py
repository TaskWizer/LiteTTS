#!/usr/bin/env python3
"""
Comprehensive TTS Performance Benchmark Script
Generates detailed performance metrics, error analysis, and visual reporting
"""

import requests
import time
import json
import csv
import statistics
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import concurrent.futures
from pathlib import Path

@dataclass
class BenchmarkResult:
    """Individual benchmark test result"""
    test_name: str
    text: str
    voice: str
    format: str
    speed: float
    
    # Timing metrics
    total_time: float
    generation_time: float
    cache_hit: bool
    
    # Audio metrics
    audio_size: int
    estimated_duration: float
    rtf: float  # Real-Time Factor
    
    # Quality metrics
    success: bool
    error_message: str
    http_status: int
    
    # Resource metrics
    memory_usage: float
    cpu_usage: float

@dataclass
class BenchmarkSummary:
    """Summary of all benchmark results"""
    total_tests: int
    successful_tests: int
    failed_tests: int
    
    # Performance metrics
    avg_total_time: float
    avg_generation_time: float
    avg_rtf: float
    
    # Cache metrics
    cache_hit_rate: float
    cache_miss_rate: float
    
    # Error analysis
    error_rate: float
    empty_audio_rate: float
    phonemizer_warning_rate: float
    
    # Quality metrics
    avg_audio_size: int
    avg_estimated_duration: float

class TTSBenchmark:
    """Comprehensive TTS benchmarking system"""
    
    def __init__(self, base_url: str = "http://localhost:8354"):
        self.base_url = base_url
        self.results: List[BenchmarkResult] = []
        self.start_time = datetime.now()
        
        # Test configurations
        self.test_texts = [
            "Hello, world!",
            "This is a simple test sentence.",
            "The quick brown fox jumps over the lazy dog.",
            "I am doing well, thank you for asking! As a large language model, I do not have feelings in the traditional sense.",
            "Test with numbers: 123, 456, and symbols: @#$%^&*()_+{}|:\"<>?/~`",
            "Very long text to test performance with extended content that includes multiple sentences, various punctuation marks, and complex linguistic structures that might challenge the TTS system's processing capabilities.",
            "Contractions test: don't, won't, can't, shouldn't, wouldn't, I'm, you're, he's, she's, it's, we're, they're.",
            "Special characters and formatting: email@domain.com, https://example.com, file.txt, 50% discount, $100.00, 3:30 PM.",
        ]
        
        self.test_voices = ["af_heart", "am_puck", "af_sarah", "am_adam"]
        self.test_formats = ["mp3", "wav", "ogg"]
        self.test_speeds = [0.8, 1.0, 1.2, 1.5]
    
    def run_single_test(self, text: str, voice: str, format: str = "mp3", speed: float = 1.0) -> BenchmarkResult:
        """Run a single TTS test and collect metrics"""
        test_name = f"{voice}_{format}_{speed}_{len(text)}chars"
        
        payload = {
            "input": text,
            "voice": voice,
            "response_format": format,
            "speed": speed
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json=payload,
                timeout=30
            )
            
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                audio_size = len(response.content)
                estimated_duration = self._estimate_audio_duration(audio_size, format)
                rtf = total_time / estimated_duration if estimated_duration > 0 else 0
                
                # Check if this was a cache hit (very fast response)
                cache_hit = total_time < 0.1
                
                return BenchmarkResult(
                    test_name=test_name,
                    text=text[:50] + "..." if len(text) > 50 else text,
                    voice=voice,
                    format=format,
                    speed=speed,
                    total_time=total_time,
                    generation_time=total_time,  # Simplified for now
                    cache_hit=cache_hit,
                    audio_size=audio_size,
                    estimated_duration=estimated_duration,
                    rtf=rtf,
                    success=True,
                    error_message="",
                    http_status=response.status_code,
                    memory_usage=0.0,  # Would need psutil for real metrics
                    cpu_usage=0.0
                )
            else:
                return BenchmarkResult(
                    test_name=test_name,
                    text=text[:50] + "..." if len(text) > 50 else text,
                    voice=voice,
                    format=format,
                    speed=speed,
                    total_time=total_time,
                    generation_time=total_time,
                    cache_hit=False,
                    audio_size=0,
                    estimated_duration=0.0,
                    rtf=0.0,
                    success=False,
                    error_message=f"HTTP {response.status_code}",
                    http_status=response.status_code,
                    memory_usage=0.0,
                    cpu_usage=0.0
                )
                
        except Exception as e:
            total_time = time.time() - start_time
            return BenchmarkResult(
                test_name=test_name,
                text=text[:50] + "..." if len(text) > 50 else text,
                voice=voice,
                format=format,
                speed=speed,
                total_time=total_time,
                generation_time=total_time,
                cache_hit=False,
                audio_size=0,
                estimated_duration=0.0,
                rtf=0.0,
                success=False,
                error_message=str(e),
                http_status=0,
                memory_usage=0.0,
                cpu_usage=0.0
            )
    
    def _estimate_audio_duration(self, audio_size: int, format: str) -> float:
        """Estimate audio duration based on file size and format"""
        # Rough estimates based on typical compression ratios
        if format == "wav":
            # Uncompressed: ~24000 Hz * 2 bytes * 1 channel = 48000 bytes/second
            return audio_size / 48000
        elif format == "mp3":
            # Compressed: ~128 kbps = 16000 bytes/second
            return audio_size / 16000
        elif format == "ogg":
            # Compressed: ~128 kbps = 16000 bytes/second
            return audio_size / 16000
        else:
            return audio_size / 16000  # Default estimate
    
    def run_comprehensive_benchmark(self) -> BenchmarkSummary:
        """Run comprehensive benchmark suite"""
        print("🚀 Starting Comprehensive TTS Benchmark")
        print("=" * 60)
        
        total_tests = 0
        
        # Basic functionality tests
        print("📋 Running basic functionality tests...")
        for text in self.test_texts[:4]:  # First 4 texts
            for voice in self.test_voices[:2]:  # First 2 voices
                result = self.run_single_test(text, voice)
                self.results.append(result)
                total_tests += 1
                print(f"  ✓ {result.test_name}: {result.total_time:.3f}s ({'✅' if result.success else '❌'})")
        
        # Format compatibility tests
        print("\n🎵 Running format compatibility tests...")
        test_text = self.test_texts[1]  # Medium length text
        for format in self.test_formats:
            result = self.run_single_test(test_text, "af_heart", format)
            self.results.append(result)
            total_tests += 1
            print(f"  ✓ Format {format}: {result.total_time:.3f}s ({'✅' if result.success else '❌'})")
        
        # Speed variation tests
        print("\n⚡ Running speed variation tests...")
        for speed in self.test_speeds:
            result = self.run_single_test(test_text, "af_heart", "mp3", speed)
            self.results.append(result)
            total_tests += 1
            print(f"  ✓ Speed {speed}x: {result.total_time:.3f}s ({'✅' if result.success else '❌'})")
        
        # Cache performance tests
        print("\n🎯 Running cache performance tests...")
        cache_test_text = "Cache performance test sentence."
        
        # First request (should be cache miss)
        result1 = self.run_single_test(cache_test_text, "af_heart")
        self.results.append(result1)
        total_tests += 1
        
        # Second request (should be cache hit)
        result2 = self.run_single_test(cache_test_text, "af_heart")
        self.results.append(result2)
        total_tests += 1
        
        speedup = result1.total_time / result2.total_time if result2.total_time > 0 else 1
        print(f"  ✓ Cache miss: {result1.total_time:.3f}s")
        print(f"  ✓ Cache hit: {result2.total_time:.3f}s ({speedup:.1f}x speedup)")
        
        # Error handling tests
        print("\n🔍 Running error handling tests...")
        error_tests = [
            ("", "af_heart", "mp3", 1.0, "Empty text"),
            ("Test", "invalid_voice", "mp3", 1.0, "Invalid voice"),
            ("Test", "af_heart", "invalid_format", 1.0, "Invalid format"),
        ]
        
        for text, voice, format, speed, description in error_tests:
            result = self.run_single_test(text, voice, format, speed)
            self.results.append(result)
            total_tests += 1
            print(f"  ✓ {description}: {'✅' if not result.success else '❌ (should have failed)'}")
        
        # Problematic text tests
        print("\n⚠️ Running problematic text tests...")
        problematic_texts = [
            self.test_texts[4],  # Numbers and symbols
            self.test_texts[6],  # Contractions
            self.test_texts[7],  # Special characters
        ]
        
        for text in problematic_texts:
            result = self.run_single_test(text, "af_heart")
            self.results.append(result)
            total_tests += 1
            print(f"  ✓ Problematic text: {result.total_time:.3f}s ({'✅' if result.success else '❌'})")
        
        print(f"\n📊 Completed {total_tests} tests")
        return self._generate_summary()
    
    def _generate_summary(self) -> BenchmarkSummary:
        """Generate benchmark summary statistics"""
        if not self.results:
            return BenchmarkSummary(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]
        
        total_tests = len(self.results)
        successful_tests = len(successful_results)
        failed_tests = len(failed_results)
        
        if successful_results:
            avg_total_time = statistics.mean([r.total_time for r in successful_results])
            avg_generation_time = statistics.mean([r.generation_time for r in successful_results])
            avg_rtf = statistics.mean([r.rtf for r in successful_results if r.rtf > 0])
            avg_audio_size = int(statistics.mean([r.audio_size for r in successful_results if r.audio_size > 0]))
            avg_estimated_duration = statistics.mean([r.estimated_duration for r in successful_results if r.estimated_duration > 0])
        else:
            avg_total_time = avg_generation_time = avg_rtf = avg_audio_size = avg_estimated_duration = 0
        
        cache_hits = len([r for r in self.results if r.cache_hit])
        cache_hit_rate = cache_hits / total_tests if total_tests > 0 else 0
        cache_miss_rate = 1 - cache_hit_rate
        
        error_rate = failed_tests / total_tests if total_tests > 0 else 0
        empty_audio_rate = len([r for r in self.results if r.success and r.audio_size == 0]) / total_tests if total_tests > 0 else 0
        
        return BenchmarkSummary(
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            avg_total_time=avg_total_time,
            avg_generation_time=avg_generation_time,
            avg_rtf=avg_rtf,
            cache_hit_rate=cache_hit_rate,
            cache_miss_rate=cache_miss_rate,
            error_rate=error_rate,
            empty_audio_rate=empty_audio_rate,
            phonemizer_warning_rate=0.0,  # Would need log analysis
            avg_audio_size=avg_audio_size,
            avg_estimated_duration=avg_estimated_duration
        )
    
    def export_results(self, output_dir: str = "docs/benchmark_results"):
        """Export results in multiple formats"""
        Path(output_dir).mkdir(exist_ok=True)
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        # JSON export
        json_file = f"{output_dir}/benchmark_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump({
                'metadata': {
                    'timestamp': self.start_time.isoformat(),
                    'base_url': self.base_url,
                    'total_tests': len(self.results)
                },
                'results': [asdict(r) for r in self.results],
                'summary': asdict(self._generate_summary())
            }, f, indent=2)
        
        # CSV export
        csv_file = f"{output_dir}/benchmark_{timestamp}.csv"
        with open(csv_file, 'w', newline='') as f:
            if self.results:
                writer = csv.DictWriter(f, fieldnames=asdict(self.results[0]).keys())
                writer.writeheader()
                for result in self.results:
                    writer.writerow(asdict(result))
        
        # Markdown report
        md_file = f"{output_dir}/benchmark_report_{timestamp}.md"
        self._generate_markdown_report(md_file)
        
        print(f"\n📁 Results exported to:")
        print(f"   JSON: {json_file}")
        print(f"   CSV: {csv_file}")
        print(f"   Report: {md_file}")
    
    def _generate_markdown_report(self, filename: str):
        """Generate detailed markdown report"""
        summary = self._generate_summary()
        
        with open(filename, 'w') as f:
            f.write(f"# TTS Benchmark Report\n\n")
            f.write(f"**Generated:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Base URL:** {self.base_url}\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Tests:** {summary.total_tests}\n")
            f.write(f"- **Success Rate:** {(summary.successful_tests/summary.total_tests*100):.1f}%\n")
            f.write(f"- **Average Response Time:** {summary.avg_total_time:.3f}s\n")
            f.write(f"- **Average RTF:** {summary.avg_rtf:.3f}\n")
            f.write(f"- **Cache Hit Rate:** {summary.cache_hit_rate*100:.1f}%\n\n")
            
            f.write("## Performance Metrics\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Average Total Time | {summary.avg_total_time:.3f}s |\n")
            f.write(f"| Average Generation Time | {summary.avg_generation_time:.3f}s |\n")
            f.write(f"| Average RTF | {summary.avg_rtf:.3f} |\n")
            f.write(f"| Average Audio Size | {summary.avg_audio_size:,} bytes |\n")
            f.write(f"| Average Duration | {summary.avg_estimated_duration:.2f}s |\n\n")
            
            f.write("## Error Analysis\n\n")
            f.write(f"- **Error Rate:** {summary.error_rate*100:.1f}%\n")
            f.write(f"- **Empty Audio Rate:** {summary.empty_audio_rate*100:.1f}%\n")
            f.write(f"- **Failed Tests:** {summary.failed_tests}\n\n")
            
            if summary.failed_tests > 0:
                f.write("### Failed Tests\n\n")
                for result in self.results:
                    if not result.success:
                        f.write(f"- **{result.test_name}:** {result.error_message}\n")
                f.write("\n")
            
            f.write("## Detailed Results\n\n")
            f.write("| Test | Voice | Format | Speed | Time | RTF | Size | Status |\n")
            f.write("|------|-------|--------|-------|------|-----|------|--------|\n")
            
            for result in self.results:
                status = "✅" if result.success else "❌"
                f.write(f"| {result.test_name} | {result.voice} | {result.format} | {result.speed} | {result.total_time:.3f}s | {result.rtf:.3f} | {result.audio_size:,} | {status} |\n")

def main():
    """Main benchmark execution"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8354"
    
    print(f"🎯 TTS Benchmark Tool")
    print(f"📡 Target: {base_url}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    benchmark = TTSBenchmark(base_url)
    
    try:
        summary = benchmark.run_comprehensive_benchmark()
        
        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 60)
        print(f"✅ Successful Tests: {summary.successful_tests}/{summary.total_tests} ({summary.successful_tests/summary.total_tests*100:.1f}%)")
        print(f"⚡ Average Response Time: {summary.avg_total_time:.3f}s")
        print(f"🎵 Average RTF: {summary.avg_rtf:.3f}")
        print(f"🎯 Cache Hit Rate: {summary.cache_hit_rate*100:.1f}%")
        print(f"📦 Average Audio Size: {summary.avg_audio_size:,} bytes")
        
        if summary.error_rate > 0:
            print(f"❌ Error Rate: {summary.error_rate*100:.1f}%")
        
        if summary.empty_audio_rate > 0:
            print(f"⚠️ Empty Audio Rate: {summary.empty_audio_rate*100:.1f}%")
        
        benchmark.export_results()
        
        print(f"\n🎉 Benchmark completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Benchmark interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
