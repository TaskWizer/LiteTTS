#!/usr/bin/env python3
"""
Performance Benchmark for LiteTTS Whisper Integration
Measures and displays RTF, memory usage, and performance metrics
"""

import sys
import os
import time
import json
import psutil
import logging
import tempfile
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    """Benchmark result data"""
    test_name: str
    model_name: str
    audio_duration: float
    processing_time: float
    rtf: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success: bool
    error_message: str = ""

class PerformanceBenchmark:
    """Performance benchmarking system for Whisper alternatives"""
    
    def __init__(self):
        self.results = []
        self.system_info = self._get_system_info()
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "platform": sys.platform,
            "python_version": sys.version.split()[0]
        }
        
    def generate_test_audio(self, duration: float, complexity: str = "medium") -> str:
        """Generate test audio with different complexity levels"""
        try:
            import soundfile as sf
            
            sample_rate = 16000  # Standard for Whisper
            t = np.linspace(0, duration, int(duration * sample_rate))
            
            if complexity == "simple":
                # Simple sine wave
                audio = 0.5 * np.sin(2 * np.pi * 440 * t)
            elif complexity == "medium":
                # Multiple harmonics
                audio = (
                    0.3 * np.sin(2 * np.pi * 220 * t) +
                    0.2 * np.sin(2 * np.pi * 440 * t) +
                    0.1 * np.sin(2 * np.pi * 880 * t)
                )
            else:  # complex
                # Speech-like signal with modulation
                base_freq = 200 + 50 * np.sin(2 * np.pi * 3 * t)  # Varying fundamental
                audio = np.zeros_like(t)
                
                # Add harmonics
                for harmonic in range(1, 6):
                    amplitude = 0.3 / harmonic
                    audio += amplitude * np.sin(2 * np.pi * harmonic * base_freq * t)
                
                # Add formant-like resonances
                formant1 = 0.1 * np.sin(2 * np.pi * 800 * t)
                formant2 = 0.05 * np.sin(2 * np.pi * 1200 * t)
                audio += formant1 + formant2
            
            # Add realistic noise
            noise_level = 0.02 if complexity == "simple" else 0.05
            noise = np.random.normal(0, noise_level, len(audio))
            audio = audio + noise
            
            # Normalize
            audio = audio / np.max(np.abs(audio)) * 0.8
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            sf.write(temp_file.name, audio.astype(np.float32), sample_rate)
            
            return temp_file.name
            
        except ImportError:
            logger.error("soundfile library required for audio generation")
            raise
        except Exception as e:
            logger.error(f"Failed to generate test audio: {e}")
            raise
            
    def benchmark_whisper_processor(self, model_name: str = "distil-small.en", 
                                  compute_type: str = "int8") -> List[BenchmarkResult]:
        """Benchmark Whisper processor with different audio lengths"""
        logger.info(f"🔬 Benchmarking Whisper processor: {model_name} ({compute_type})")
        
        results = []
        
        try:
            from backends.whisper_optimized import create_whisper_processor
            
            # Create processor
            processor = create_whisper_processor(
                model_name=model_name,
                compute_type=compute_type,
                enable_fallback=True
            )
            
            # Test with different audio durations
            test_durations = [5, 10, 15, 30, 60]
            
            for duration in test_durations:
                logger.info(f"  Testing {duration}s audio...")
                
                # Generate test audio
                audio_file = self.generate_test_audio(duration, "medium")
                
                try:
                    # Monitor system resources
                    process = psutil.Process()
                    start_memory = process.memory_info().rss / 1024 / 1024  # MB
                    start_cpu = psutil.cpu_percent()
                    
                    # Perform transcription
                    start_time = time.time()
                    result = processor.transcribe(audio_file, duration)
                    processing_time = time.time() - start_time
                    
                    # Calculate metrics
                    end_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_usage = end_memory - start_memory
                    cpu_usage = psutil.cpu_percent()
                    rtf = processing_time / duration
                    
                    benchmark_result = BenchmarkResult(
                        test_name=f"whisper_{model_name}_{compute_type}_{duration}s",
                        model_name=f"{model_name}-{compute_type}",
                        audio_duration=duration,
                        processing_time=processing_time,
                        rtf=rtf,
                        memory_usage_mb=memory_usage,
                        cpu_usage_percent=cpu_usage,
                        success=result.success,
                        error_message=result.error_message or ""
                    )
                    
                    results.append(benchmark_result)
                    
                    logger.info(f"    RTF: {rtf:.3f}, Memory: {memory_usage:.1f}MB, Success: {result.success}")
                    
                except Exception as e:
                    error_result = BenchmarkResult(
                        test_name=f"whisper_{model_name}_{compute_type}_{duration}s",
                        model_name=f"{model_name}-{compute_type}",
                        audio_duration=duration,
                        processing_time=0,
                        rtf=float('inf'),
                        memory_usage_mb=0,
                        cpu_usage_percent=0,
                        success=False,
                        error_message=str(e)
                    )
                    results.append(error_result)
                    logger.error(f"    Failed: {e}")
                
                finally:
                    # Cleanup
                    try:
                        os.unlink(audio_file)
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"Failed to create Whisper processor: {e}")
            
        return results
        
    def benchmark_voice_cloning(self) -> List[BenchmarkResult]:
        """Benchmark voice cloning with different audio lengths"""
        logger.info("🎭 Benchmarking voice cloning performance")
        
        results = []
        
        try:
            from voice.cloning import VoiceCloner
            
            cloner = VoiceCloner()
            
            # Test with different audio durations
            test_durations = [10, 30, 60, 90, 120]
            
            for duration in test_durations:
                if duration <= cloner.max_audio_duration:
                    logger.info(f"  Testing {duration}s audio...")
                    
                    # Generate test audio
                    audio_file = self.generate_test_audio(duration, "complex")
                    
                    try:
                        # Monitor system resources
                        process = psutil.Process()
                        start_memory = process.memory_info().rss / 1024 / 1024  # MB
                        start_cpu = psutil.cpu_percent()
                        
                        # Perform analysis
                        start_time = time.time()
                        result = cloner.analyze_audio(audio_file)
                        processing_time = time.time() - start_time
                        
                        # Calculate metrics
                        end_memory = process.memory_info().rss / 1024 / 1024  # MB
                        memory_usage = end_memory - start_memory
                        cpu_usage = psutil.cpu_percent()
                        rtf = processing_time / duration
                        
                        benchmark_result = BenchmarkResult(
                            test_name=f"voice_cloning_{duration}s",
                            model_name="voice_cloning",
                            audio_duration=duration,
                            processing_time=processing_time,
                            rtf=rtf,
                            memory_usage_mb=memory_usage,
                            cpu_usage_percent=cpu_usage,
                            success=result.suitable,
                            error_message="" if result.suitable else f"Quality: {result.quality_score:.3f}"
                        )
                        
                        results.append(benchmark_result)
                        
                        logger.info(f"    RTF: {rtf:.3f}, Memory: {memory_usage:.1f}MB, Quality: {result.quality_score:.3f}")
                        
                    except Exception as e:
                        error_result = BenchmarkResult(
                            test_name=f"voice_cloning_{duration}s",
                            model_name="voice_cloning",
                            audio_duration=duration,
                            processing_time=0,
                            rtf=float('inf'),
                            memory_usage_mb=0,
                            cpu_usage_percent=0,
                            success=False,
                            error_message=str(e)
                        )
                        results.append(error_result)
                        logger.error(f"    Failed: {e}")
                    
                    finally:
                        # Cleanup
                        try:
                            os.unlink(audio_file)
                        except:
                            pass
                else:
                    logger.warning(f"  Skipping {duration}s (exceeds max duration)")
                    
        except Exception as e:
            logger.error(f"Failed to create voice cloner: {e}")
            
        return results
        
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark suite"""
        logger.info("🚀 Starting Comprehensive Performance Benchmark")
        logger.info("=" * 60)
        
        all_results = []
        
        # System info
        logger.info("💻 System Information:")
        for key, value in self.system_info.items():
            logger.info(f"  {key}: {value}")
        
        # Benchmark Whisper models
        whisper_configs = [
            ("distil-small.en", "int8"),
            ("base", "int8"),
            ("tiny", "int8"),
        ]
        
        for model_name, compute_type in whisper_configs:
            try:
                results = self.benchmark_whisper_processor(model_name, compute_type)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Whisper benchmark failed for {model_name}: {e}")
        
        # Benchmark voice cloning
        try:
            results = self.benchmark_voice_cloning()
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Voice cloning benchmark failed: {e}")
        
        self.results = all_results
        
        # Generate report
        return self.generate_report()
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        if not self.results:
            return {"error": "No benchmark results available"}
        
        # Separate successful and failed results
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]
        
        # Calculate statistics
        report = {
            "system_info": self.system_info,
            "total_tests": len(self.results),
            "successful_tests": len(successful_results),
            "failed_tests": len(failed_results),
            "success_rate": len(successful_results) / len(self.results) if self.results else 0,
        }
        
        if successful_results:
            # RTF statistics
            rtfs = [r.rtf for r in successful_results]
            report["rtf_stats"] = {
                "min": min(rtfs),
                "max": max(rtfs),
                "mean": sum(rtfs) / len(rtfs),
                "median": sorted(rtfs)[len(rtfs) // 2],
                "models_under_1_0": len([r for r in rtfs if r < 1.0])
            }
            
            # Memory statistics
            memories = [r.memory_usage_mb for r in successful_results]
            report["memory_stats"] = {
                "min": min(memories),
                "max": max(memories),
                "mean": sum(memories) / len(memories),
                "median": sorted(memories)[len(memories) // 2]
            }
            
            # Best performers
            best_rtf = min(successful_results, key=lambda x: x.rtf)
            best_memory = min(successful_results, key=lambda x: x.memory_usage_mb)
            
            report["best_performers"] = {
                "fastest_rtf": {
                    "model": best_rtf.model_name,
                    "rtf": best_rtf.rtf,
                    "duration": best_rtf.audio_duration
                },
                "lowest_memory": {
                    "model": best_memory.model_name,
                    "memory_mb": best_memory.memory_usage_mb,
                    "duration": best_memory.audio_duration
                }
            }
        
        # Failed tests summary
        if failed_results:
            report["failures"] = [
                {
                    "test": r.test_name,
                    "model": r.model_name,
                    "error": r.error_message
                }
                for r in failed_results
            ]
        
        # Detailed results
        report["detailed_results"] = [asdict(r) for r in self.results]
        
        return report
        
    def save_report(self, filename: str = None):
        """Save benchmark report to file"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_report_{timestamp}.json"
        
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📊 Benchmark report saved to {filename}")
        return filename

def main():
    """Run performance benchmark"""
    benchmark = PerformanceBenchmark()
    
    try:
        # Run comprehensive benchmark
        report = benchmark.run_comprehensive_benchmark()
        
        # Display summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 BENCHMARK SUMMARY")
        logger.info("=" * 60)
        
        logger.info(f"Total tests: {report['total_tests']}")
        logger.info(f"Successful: {report['successful_tests']}")
        logger.info(f"Failed: {report['failed_tests']}")
        logger.info(f"Success rate: {report['success_rate']:.1%}")
        
        if 'rtf_stats' in report:
            rtf_stats = report['rtf_stats']
            logger.info(f"\nRTF Statistics:")
            logger.info(f"  Mean: {rtf_stats['mean']:.3f}")
            logger.info(f"  Median: {rtf_stats['median']:.3f}")
            logger.info(f"  Range: {rtf_stats['min']:.3f} - {rtf_stats['max']:.3f}")
            logger.info(f"  Models under RTF 1.0: {rtf_stats['models_under_1_0']}")
        
        if 'memory_stats' in report:
            mem_stats = report['memory_stats']
            logger.info(f"\nMemory Statistics:")
            logger.info(f"  Mean: {mem_stats['mean']:.1f}MB")
            logger.info(f"  Median: {mem_stats['median']:.1f}MB")
            logger.info(f"  Range: {mem_stats['min']:.1f} - {mem_stats['max']:.1f}MB")
        
        if 'best_performers' in report:
            best = report['best_performers']
            logger.info(f"\nBest Performers:")
            logger.info(f"  Fastest RTF: {best['fastest_rtf']['model']} ({best['fastest_rtf']['rtf']:.3f})")
            logger.info(f"  Lowest Memory: {best['lowest_memory']['model']} ({best['lowest_memory']['memory_mb']:.1f}MB)")
        
        # Save report
        report_file = benchmark.save_report()
        
        logger.info(f"\n✅ Benchmark completed successfully!")
        logger.info(f"📄 Detailed report: {report_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Benchmark failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
