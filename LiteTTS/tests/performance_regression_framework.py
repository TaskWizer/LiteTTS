#!/usr/bin/env python3
"""
Performance Regression Testing Framework
Automated testing to ensure improvements don't degrade functionality and maintain processing speed
"""

import time
import logging
import json
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import psutil
import threading
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.tts.synthesizer import TTSSynthesizer
from LiteTTS.models import TTSConfiguration, TTSRequest
from LiteTTS.audio.audio_segment import AudioSegment

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a single test"""
    test_name: str
    text_length: int
    audio_duration: float
    processing_time: float
    rtf: float  # Real-time factor
    memory_usage_mb: float
    cpu_usage_percent: float
    success: bool
    error_message: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class RegressionTestResult:
    """Result of a regression test suite"""
    test_suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    average_rtf: float
    average_processing_time: float
    memory_peak_mb: float
    cpu_peak_percent: float
    performance_degradation: float  # Percentage change from baseline
    test_metrics: List[PerformanceMetrics]
    baseline_comparison: Dict[str, float]
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class PerformanceRegressionTester:
    """Automated performance regression testing framework"""
    
    def __init__(self, baseline_file: str = "performance_baseline.json"):
        self.baseline_file = Path(baseline_file)
        self.baseline_metrics = self._load_baseline()
        self.current_metrics = []
        
        # Test configuration
        self.test_texts = self._load_test_texts()
        self.test_voices = ["af_heart", "af_bella", "am_adam", "am_onyx"]
        self.test_speeds = [0.8, 1.0, 1.2]
        
        # Performance thresholds
        self.rtf_threshold = 0.5  # RTF should be < 0.5 for real-time
        self.memory_threshold_mb = 2048  # 2GB memory limit
        self.degradation_threshold = 0.15  # 15% performance degradation limit
        
        logger.info("Performance regression tester initialized")
    
    def _load_baseline(self) -> Dict[str, Any]:
        """Load baseline performance metrics"""
        if self.baseline_file.exists():
            try:
                with open(self.baseline_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load baseline: {e}")
        
        return {}
    
    def _save_baseline(self, metrics: Dict[str, Any]):
        """Save baseline performance metrics"""
        try:
            with open(self.baseline_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.info(f"Baseline saved to {self.baseline_file}")
        except Exception as e:
            logger.error(f"Failed to save baseline: {e}")
    
    def _load_test_texts(self) -> List[str]:
        """Load test texts for performance testing"""
        return [
            # Short texts
            "Hello world",
            "The quick brown fox jumps over the lazy dog.",
            "Testing TTS performance with short text.",
            
            # Medium texts
            "This is a medium-length text designed to test the performance of the TTS system. "
            "It includes various punctuation marks, numbers like 123 and 456, and common words "
            "that should be processed efficiently by the text normalization pipeline.",
            
            "Performance testing requires systematic evaluation of processing speed, memory usage, "
            "and audio quality. The system should maintain consistent performance across different "
            "text lengths, voice models, and synthesis parameters.",
            
            # Long texts
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor "
            "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
            "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute "
            "irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla "
            "pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia "
            "deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error "
            "sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae "
            "ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.",
            
            # Complex texts with numbers, symbols, and contractions
            "The company's Q3 2023 revenue was $1.2 million, representing a 15% increase from Q2. "
            "Key metrics include: RTF < 0.3, memory usage ≤ 1GB, and 99.9% uptime. "
            "Contact us at support@example.com or visit https://www.example.com for more info. "
            "Don't forget that we're launching at 3:30 PM EST on December 15th, 2023!",
            
            # Pronunciation challenges
            "The pronunciation of words like 'asterisk', 'hedonism', and 'inherently' should be "
            "accurate. Contractions like 'I'll', 'you'll', and 'that's' need proper handling. "
            "Currency amounts like $123.45 and dates like 2023-10-27 require normalization."
        ]
    
    def run_performance_test_suite(self, save_as_baseline: bool = False) -> RegressionTestResult:
        """Run complete performance regression test suite"""
        logger.info("Starting performance regression test suite")
        
        start_time = time.time()
        test_metrics = []
        
        # Initialize TTS system
        try:
            config = TTSConfiguration(
                sample_rate=24000,
                chunk_size=100,
                device="cpu",  # Use CPU for consistent testing
                default_voice="af_heart"
            )
            synthesizer = TTSSynthesizer(config)
        except Exception as e:
            logger.error(f"Failed to initialize TTS system: {e}")
            return self._create_failed_result("TTS initialization failed")
        
        # Run tests for each combination
        total_tests = len(self.test_texts) * len(self.test_voices) * len(self.test_speeds)
        current_test = 0
        
        for text in self.test_texts:
            for voice in self.test_voices:
                for speed in self.test_speeds:
                    current_test += 1
                    test_name = f"test_{current_test}_{voice}_{speed}x"
                    
                    logger.info(f"Running test {current_test}/{total_tests}: {test_name}")
                    
                    metrics = self._run_single_performance_test(
                        synthesizer, text, voice, speed, test_name
                    )
                    test_metrics.append(metrics)
        
        # Calculate aggregate metrics
        passed_tests = sum(1 for m in test_metrics if m.success)
        failed_tests = len(test_metrics) - passed_tests
        
        successful_metrics = [m for m in test_metrics if m.success]
        if successful_metrics:
            avg_rtf = statistics.mean(m.rtf for m in successful_metrics)
            avg_processing_time = statistics.mean(m.processing_time for m in successful_metrics)
            memory_peak = max(m.memory_usage_mb for m in successful_metrics)
            cpu_peak = max(m.cpu_usage_percent for m in successful_metrics)
        else:
            avg_rtf = avg_processing_time = memory_peak = cpu_peak = 0.0
        
        # Compare with baseline
        baseline_comparison = self._compare_with_baseline(successful_metrics)
        performance_degradation = baseline_comparison.get('rtf_change_percent', 0.0)
        
        result = RegressionTestResult(
            test_suite_name="Performance Regression Test Suite",
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            average_rtf=avg_rtf,
            average_processing_time=avg_processing_time,
            memory_peak_mb=memory_peak,
            cpu_peak_percent=cpu_peak,
            performance_degradation=performance_degradation,
            test_metrics=test_metrics,
            baseline_comparison=baseline_comparison
        )
        
        # Save as baseline if requested
        if save_as_baseline:
            self._save_current_as_baseline(successful_metrics)
        
        total_time = time.time() - start_time
        logger.info(f"Performance test suite completed in {total_time:.2f}s")
        logger.info(f"Results: {passed_tests}/{total_tests} passed, avg RTF: {avg_rtf:.3f}")
        
        return result
    
    def _run_single_performance_test(self, synthesizer: TTSSynthesizer, 
                                   text: str, voice: str, speed: float, 
                                   test_name: str) -> PerformanceMetrics:
        """Run a single performance test"""
        
        # Monitor system resources
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            # Create TTS request
            request = TTSRequest(
                input=text,
                voice=voice,
                speed=speed,
                response_format="wav"
            )
            
            # Measure performance
            start_time = time.time()
            start_cpu = psutil.cpu_percent()
            
            # Synthesize audio
            audio_segment = synthesizer.synthesize(request)
            
            end_time = time.time()
            end_cpu = psutil.cpu_percent()
            
            # Calculate metrics
            processing_time = end_time - start_time
            audio_duration = audio_segment.duration
            rtf = processing_time / audio_duration if audio_duration > 0 else float('inf')
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_usage = final_memory - initial_memory
            cpu_usage = (start_cpu + end_cpu) / 2
            
            return PerformanceMetrics(
                test_name=test_name,
                text_length=len(text),
                audio_duration=audio_duration,
                processing_time=processing_time,
                rtf=rtf,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Test {test_name} failed: {e}")
            return PerformanceMetrics(
                test_name=test_name,
                text_length=len(text),
                audio_duration=0.0,
                processing_time=0.0,
                rtf=float('inf'),
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                success=False,
                error_message=str(e)
            )
    
    def _compare_with_baseline(self, current_metrics: List[PerformanceMetrics]) -> Dict[str, float]:
        """Compare current metrics with baseline"""
        if not self.baseline_metrics or not current_metrics:
            return {}
        
        # Calculate current averages
        current_avg_rtf = statistics.mean(m.rtf for m in current_metrics)
        current_avg_memory = statistics.mean(m.memory_usage_mb for m in current_metrics)
        current_avg_cpu = statistics.mean(m.cpu_usage_percent for m in current_metrics)
        
        # Get baseline averages
        baseline_rtf = self.baseline_metrics.get('average_rtf', current_avg_rtf)
        baseline_memory = self.baseline_metrics.get('average_memory_mb', current_avg_memory)
        baseline_cpu = self.baseline_metrics.get('average_cpu_percent', current_avg_cpu)
        
        # Calculate percentage changes
        rtf_change = ((current_avg_rtf - baseline_rtf) / baseline_rtf * 100) if baseline_rtf > 0 else 0
        memory_change = ((current_avg_memory - baseline_memory) / baseline_memory * 100) if baseline_memory > 0 else 0
        cpu_change = ((current_avg_cpu - baseline_cpu) / baseline_cpu * 100) if baseline_cpu > 0 else 0
        
        return {
            'baseline_rtf': baseline_rtf,
            'current_rtf': current_avg_rtf,
            'rtf_change_percent': rtf_change,
            'baseline_memory_mb': baseline_memory,
            'current_memory_mb': current_avg_memory,
            'memory_change_percent': memory_change,
            'baseline_cpu_percent': baseline_cpu,
            'current_cpu_percent': current_avg_cpu,
            'cpu_change_percent': cpu_change
        }
    
    def _save_current_as_baseline(self, metrics: List[PerformanceMetrics]):
        """Save current metrics as new baseline"""
        if not metrics:
            return
        
        baseline_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(metrics),
            'average_rtf': statistics.mean(m.rtf for m in metrics),
            'average_memory_mb': statistics.mean(m.memory_usage_mb for m in metrics),
            'average_cpu_percent': statistics.mean(m.cpu_usage_percent for m in metrics),
            'rtf_p95': statistics.quantiles(sorted(m.rtf for m in metrics), n=20)[18],  # 95th percentile
            'memory_peak_mb': max(m.memory_usage_mb for m in metrics),
            'cpu_peak_percent': max(m.cpu_usage_percent for m in metrics),
            'test_details': [asdict(m) for m in metrics]
        }
        
        self._save_baseline(baseline_data)
    
    def _create_failed_result(self, error_message: str) -> RegressionTestResult:
        """Create a failed test result"""
        return RegressionTestResult(
            test_suite_name="Performance Regression Test Suite",
            total_tests=0,
            passed_tests=0,
            failed_tests=1,
            average_rtf=float('inf'),
            average_processing_time=0.0,
            memory_peak_mb=0.0,
            cpu_peak_percent=0.0,
            performance_degradation=100.0,
            test_metrics=[],
            baseline_comparison={'error': error_message}
        )
    
    def generate_performance_report(self, result: RegressionTestResult, 
                                  output_file: str = "performance_report.json"):
        """Generate detailed performance report"""
        report_data = asdict(result)
        
        # Add analysis
        report_data['analysis'] = {
            'performance_status': self._analyze_performance_status(result),
            'recommendations': self._generate_recommendations(result),
            'regression_detected': result.performance_degradation > self.degradation_threshold,
            'rtf_acceptable': result.average_rtf < self.rtf_threshold,
            'memory_acceptable': result.memory_peak_mb < self.memory_threshold_mb
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Performance report saved to {output_file}")
        return report_data
    
    def _analyze_performance_status(self, result: RegressionTestResult) -> str:
        """Analyze overall performance status"""
        if result.failed_tests > 0:
            return "FAILED"
        elif result.performance_degradation > self.degradation_threshold:
            return "REGRESSION_DETECTED"
        elif result.average_rtf > self.rtf_threshold:
            return "RTF_THRESHOLD_EXCEEDED"
        elif result.memory_peak_mb > self.memory_threshold_mb:
            return "MEMORY_THRESHOLD_EXCEEDED"
        else:
            return "PASSED"
    
    def _generate_recommendations(self, result: RegressionTestResult) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if result.average_rtf > self.rtf_threshold:
            recommendations.append(f"RTF ({result.average_rtf:.3f}) exceeds threshold ({self.rtf_threshold}). Consider optimizing synthesis pipeline.")
        
        if result.memory_peak_mb > self.memory_threshold_mb:
            recommendations.append(f"Memory usage ({result.memory_peak_mb:.1f}MB) exceeds threshold ({self.memory_threshold_mb}MB). Check for memory leaks.")
        
        if result.performance_degradation > self.degradation_threshold:
            recommendations.append(f"Performance degradation ({result.performance_degradation:.1f}%) detected. Review recent changes.")
        
        if result.failed_tests > 0:
            recommendations.append(f"{result.failed_tests} tests failed. Check error logs and fix issues.")
        
        if not recommendations:
            recommendations.append("Performance is within acceptable limits. No immediate action required.")
        
        return recommendations

def main():
    """Main performance testing execution"""
    print("Performance Regression Testing Framework")
    print("=" * 50)
    
    try:
        tester = PerformanceRegressionTester()
        
        # Run test suite
        result = tester.run_performance_test_suite()
        
        # Generate report
        report = tester.generate_performance_report(result)
        
        # Print summary
        print(f"\nTest Results:")
        print(f"  Total Tests: {result.total_tests}")
        print(f"  Passed: {result.passed_tests}")
        print(f"  Failed: {result.failed_tests}")
        print(f"  Average RTF: {result.average_rtf:.3f}")
        print(f"  Memory Peak: {result.memory_peak_mb:.1f}MB")
        print(f"  Performance Status: {report['analysis']['performance_status']}")
        
        if report['analysis']['recommendations']:
            print(f"\nRecommendations:")
            for rec in report['analysis']['recommendations']:
                print(f"  - {rec}")
        
        return result.failed_tests == 0
        
    except Exception as e:
        logger.error(f"Performance testing failed: {e}")
        print(f"\n❌ Testing failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
