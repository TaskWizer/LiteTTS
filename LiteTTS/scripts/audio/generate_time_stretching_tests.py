#!/usr/bin/env python3
"""
Generate comprehensive time-stretching test audio library
Creates test samples at 10% increments with benchmarking data
"""

import os
import sys
import json
import csv
import time
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from LiteTTS.tts.synthesizer import TTSSynthesizer
from LiteTTS.audio.time_stretcher import TimeStretcher, TimeStretchConfig, StretchQuality
from LiteTTS.models import TTSConfiguration, TTSRequest
from LiteTTS.config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TimeStretchingTestGenerator:
    """Generate comprehensive time-stretching tests"""
    
    def __init__(self):
        self.test_text = "The quick brown fox jumps over the lazy dog. This is a comprehensive test of the time-stretching optimization feature for the Kokoro ONNX TTS API system."
        self.test_rates = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # 10% to 100% (2x speed)
        self.output_dir = Path("samples/time-stretched")
        self.results = {}
        
        # Initialize TTS system
        self.tts_config = TTSConfiguration()
        self.synthesizer = TTSSynthesizer(self.tts_config)
        
        logger.info("Time-stretching test generator initialized")
    
    def setup_output_directory(self):
        """Create output directory structure"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "raw").mkdir(exist_ok=True)
        (self.output_dir / "corrected").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        
        logger.info(f"Output directory created: {self.output_dir}")
    
    def generate_baseline_audio(self) -> Any:
        """Generate baseline audio for testing"""
        logger.info("Generating baseline audio...")
        
        request = TTSRequest(
            text=self.test_text,
            voice="af_heart",
            speed=1.0,
            format="wav"
        )
        
        # Generate baseline audio
        baseline_audio = self.synthesizer.synthesize(request)
        
        # Save baseline
        baseline_path = self.output_dir / "baseline.wav"
        with open(baseline_path, 'wb') as f:
            f.write(baseline_audio.audio_data.tobytes())
        
        logger.info(f"Baseline audio saved: {baseline_path}")
        return baseline_audio
    
    def run_comprehensive_tests(self):
        """Run comprehensive time-stretching tests"""
        logger.info("Starting comprehensive time-stretching tests...")
        
        # Setup
        self.setup_output_directory()
        baseline_audio = self.generate_baseline_audio()
        
        # Test each rate
        for rate in self.test_rates:
            logger.info(f"Testing rate: {rate}%")
            
            try:
                # Configure time-stretcher for this rate
                stretch_config = TimeStretchConfig(
                    enabled=True,
                    compress_playback_rate=rate,
                    correction_quality=StretchQuality.MEDIUM,
                    benchmark_mode=True
                )
                
                time_stretcher = TimeStretcher(stretch_config)
                
                # Run benchmark for this rate
                rate_results = time_stretcher.benchmark_rates(
                    baseline_audio, [rate], save_samples=True
                )
                
                if rate in rate_results:
                    self.results[rate] = rate_results[rate]
                    logger.info(f"Rate {rate}% completed successfully")
                else:
                    logger.error(f"Rate {rate}% failed - no results")
                    
            except Exception as e:
                logger.error(f"Rate {rate}% failed with error: {e}")
                continue
        
        # Generate reports
        self.generate_reports()
        
        logger.info("Comprehensive tests completed!")
    
    def generate_reports(self):
        """Generate comprehensive reports"""
        if not self.results:
            logger.warning("No results to report")
            return
        
        # Generate CSV report
        self.generate_csv_report()
        
        # Generate markdown report
        self.generate_markdown_report()
        
        # Generate JSON report
        self.generate_json_report()
        
        logger.info("All reports generated successfully")
    
    def generate_csv_report(self):
        """Generate CSV benchmark report"""
        csv_path = self.output_dir / "reports" / "benchmark_results.csv"
        
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = [
                'Rate_%', 'RTF_Original', 'RTF_Stretched', 'Generation_Time_ms',
                'Stretch_Time_ms', 'Total_Time_ms', 'Original_Duration_s',
                'Stretched_Duration_s', 'Quality_Score'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for rate in sorted(self.results.keys()):
                metrics = self.results[rate]
                writer.writerow({
                    'Rate_%': rate,
                    'RTF_Original': f"{metrics.rtf_original:.4f}",
                    'RTF_Stretched': f"{metrics.rtf_stretched:.4f}",
                    'Generation_Time_ms': f"{metrics.generation_time * 1000:.1f}",
                    'Stretch_Time_ms': f"{metrics.stretch_time * 1000:.1f}",
                    'Total_Time_ms': f"{metrics.total_time * 1000:.1f}",
                    'Original_Duration_s': f"{metrics.original_duration:.2f}",
                    'Stretched_Duration_s': f"{metrics.stretched_duration:.2f}",
                    'Quality_Score': metrics.quality_score or "N/A"
                })
        
        logger.info(f"CSV report saved: {csv_path}")
    
    def generate_markdown_report(self):
        """Generate markdown benchmark report"""
        # Create time-stretcher for report generation
        stretch_config = TimeStretchConfig(enabled=True)
        time_stretcher = TimeStretcher(stretch_config)
        
        # Generate report content
        report_content = time_stretcher.generate_benchmark_report(self.results)
        
        # Add additional sections
        report_content += "\n\n## Test Configuration\n\n"
        report_content += f"- **Test Text:** {self.test_text}\n"
        report_content += f"- **Baseline Voice:** af_heart\n"
        report_content += f"- **Test Rates:** {', '.join(map(str, self.test_rates))}%\n"
        report_content += f"- **Quality Level:** Medium\n"
        report_content += f"- **Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # Save report
        report_path = self.output_dir / "reports" / "benchmark_report.md"
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        logger.info(f"Markdown report saved: {report_path}")
    
    def generate_json_report(self):
        """Generate JSON report with detailed metrics"""
        json_data = {
            "test_configuration": {
                "test_text": self.test_text,
                "test_rates": self.test_rates,
                "baseline_voice": "af_heart",
                "quality_level": "medium",
                "generated_at": time.strftime('%Y-%m-%d %H:%M:%S')
            },
            "results": {}
        }
        
        for rate, metrics in self.results.items():
            json_data["results"][str(rate)] = {
                "rate_percent": rate,
                "rtf_original": metrics.rtf_original,
                "rtf_stretched": metrics.rtf_stretched,
                "generation_time_ms": metrics.generation_time * 1000,
                "stretch_time_ms": metrics.stretch_time * 1000,
                "total_time_ms": metrics.total_time * 1000,
                "original_duration_s": metrics.original_duration,
                "stretched_duration_s": metrics.stretched_duration,
                "quality_score": metrics.quality_score
            }
        
        json_path = self.output_dir / "reports" / "benchmark_results.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        logger.info(f"JSON report saved: {json_path}")
    
    def print_summary(self):
        """Print test summary to console"""
        if not self.results:
            print("❌ No test results available")
            return
        
        print("\n" + "="*60)
        print("🎯 TIME-STRETCHING TEST SUMMARY")
        print("="*60)
        
        print(f"\n📊 Tested {len(self.results)} rates: {', '.join(map(str, sorted(self.results.keys())))}%")
        
        # Find best rate
        best_rate = min(self.results.keys(), key=lambda r: self.results[r].rtf_stretched)
        best_metrics = self.results[best_rate]
        
        print(f"\n🏆 Best Rate: {best_rate}%")
        print(f"   RTF: {best_metrics.rtf_original:.3f} → {best_metrics.rtf_stretched:.3f}")
        print(f"   Improvement: {((best_metrics.rtf_original - best_metrics.rtf_stretched) / best_metrics.rtf_original * 100):.1f}%")
        
        # Recommendation
        if best_metrics.rtf_stretched < 0.8:
            print("\n✅ RECOMMENDATION: Enable time-stretching")
            print(f"   Significant latency improvement achieved")
        elif best_metrics.rtf_stretched < 1.0:
            print("\n⚠️  RECOMMENDATION: Consider for longer texts")
            print(f"   Modest improvement, test with real workloads")
        else:
            print("\n❌ RECOMMENDATION: Keep disabled")
            print(f"   No significant benefit observed")
        
        print(f"\n📁 Results saved to: {self.output_dir}")
        print("="*60)

def main():
    """Main execution function"""
    print("🚀 Starting Time-Stretching Test Generation")
    print("=" * 50)
    
    try:
        generator = TimeStretchingTestGenerator()
        generator.run_comprehensive_tests()
        generator.print_summary()
        
        print("\n✅ Time-stretching tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
