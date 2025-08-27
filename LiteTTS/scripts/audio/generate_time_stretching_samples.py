#!/usr/bin/env python3
"""
Generate time-stretching test samples without requiring full TTS system
Creates synthetic audio samples for testing time-stretching algorithms
"""

import os
import sys
import json
import csv
import time
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import librosa
    import soundfile as sf
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logger.warning("Audio libraries not available - will generate synthetic samples")

class TimeStretchingSampleGenerator:
    """Generate time-stretching test samples"""
    
    def __init__(self):
        self.test_rates = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # 10% to 100% (2x speed)
        self.output_dir = Path("samples/time-stretched")
        self.sample_rate = 24000
        self.duration = 3.0  # 3 seconds
        self.results = {}
        
        logger.info("Time-stretching sample generator initialized")
    
    def setup_output_directory(self):
        """Create output directory structure"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "raw").mkdir(exist_ok=True)
        (self.output_dir / "corrected").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        
        logger.info(f"Output directory created: {self.output_dir}")
    
    def generate_synthetic_audio(self) -> np.ndarray:
        """Generate synthetic speech-like audio for testing"""
        # Create a complex waveform that simulates speech characteristics
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        
        # Base frequency modulation (simulates speech formants)
        f1 = 200 + 100 * np.sin(2 * np.pi * 2 * t)  # First formant
        f2 = 800 + 200 * np.sin(2 * np.pi * 3 * t)  # Second formant
        f3 = 2400 + 300 * np.sin(2 * np.pi * 1.5 * t)  # Third formant
        
        # Generate speech-like signal
        signal = (
            0.4 * np.sin(2 * np.pi * f1 * t) +
            0.3 * np.sin(2 * np.pi * f2 * t) +
            0.2 * np.sin(2 * np.pi * f3 * t) +
            0.1 * np.random.normal(0, 0.1, len(t))  # Add some noise
        )
        
        # Apply amplitude envelope (simulates speech rhythm)
        envelope = 0.5 * (1 + np.sin(2 * np.pi * 4 * t))
        signal *= envelope
        
        # Normalize
        signal = signal / np.max(np.abs(signal)) * 0.8
        
        return signal.astype(np.float32)
    
    def apply_time_stretching(self, audio: np.ndarray, stretch_ratio: float, method: str = "librosa") -> np.ndarray:
        """Apply time-stretching to audio"""
        if AUDIO_LIBS_AVAILABLE and method == "librosa":
            # Use librosa for high-quality time-stretching
            rate = 1.0 / stretch_ratio
            stretched = librosa.effects.time_stretch(audio, rate=rate)
            return stretched.astype(np.float32)
        else:
            # Basic linear interpolation fallback
            new_length = int(len(audio) * stretch_ratio)
            old_indices = np.linspace(0, len(audio) - 1, new_length)
            stretched = np.interp(old_indices, np.arange(len(audio)), audio)
            return stretched.astype(np.float32)
    
    def simulate_fast_generation(self, audio: np.ndarray, speed_multiplier: float) -> np.ndarray:
        """Simulate faster TTS generation by speeding up audio"""
        # Speed up audio (inverse of time-stretching)
        stretch_ratio = 1.0 / speed_multiplier
        return self.apply_time_stretching(audio, stretch_ratio)
    
    def benchmark_rate(self, original_audio: np.ndarray, rate: int) -> Dict[str, Any]:
        """Benchmark a specific time-stretching rate"""
        logger.info(f"Benchmarking rate: {rate}%")
        
        # Calculate speed multiplier
        speed_multiplier = 1.0 + (rate / 100.0)
        
        # Simulate fast generation
        start_time = time.perf_counter()
        fast_audio = self.simulate_fast_generation(original_audio, speed_multiplier)
        generation_time = time.perf_counter() - start_time
        
        # Save fast audio
        fast_path = self.output_dir / f"raw_{rate}p.wav"
        if AUDIO_LIBS_AVAILABLE:
            sf.write(fast_path, fast_audio, self.sample_rate)
        else:
            # Simple WAV writing fallback
            self._write_wav_simple(fast_path, fast_audio, self.sample_rate)
        
        # Apply time-stretching correction
        start_time = time.perf_counter()
        stretch_ratio = speed_multiplier  # Stretch back to original speed
        corrected_audio = self.apply_time_stretching(fast_audio, stretch_ratio)
        stretch_time = time.perf_counter() - start_time
        
        # Save corrected audio
        corrected_path = self.output_dir / f"corrected_{rate}p.wav"
        if AUDIO_LIBS_AVAILABLE:
            sf.write(corrected_path, corrected_audio, self.sample_rate)
        else:
            self._write_wav_simple(corrected_path, corrected_audio, self.sample_rate)
        
        # Calculate metrics
        original_duration = len(original_audio) / self.sample_rate
        fast_duration = len(fast_audio) / self.sample_rate
        corrected_duration = len(corrected_audio) / self.sample_rate
        
        total_time = generation_time + stretch_time
        rtf_original = generation_time / fast_duration
        rtf_stretched = total_time / corrected_duration
        
        metrics = {
            'rate_percent': rate,
            'speed_multiplier': speed_multiplier,
            'original_duration': original_duration,
            'fast_duration': fast_duration,
            'corrected_duration': corrected_duration,
            'generation_time': generation_time,
            'stretch_time': stretch_time,
            'total_time': total_time,
            'rtf_original': rtf_original,
            'rtf_stretched': rtf_stretched,
            'improvement_percent': ((rtf_original - rtf_stretched) / rtf_original * 100) if rtf_original > 0 else 0
        }
        
        logger.info(f"Rate {rate}%: RTF {rtf_original:.3f} → {rtf_stretched:.3f} ({metrics['improvement_percent']:.1f}% improvement)")
        
        return metrics
    
    def _write_wav_simple(self, path: Path, audio: np.ndarray, sample_rate: int):
        """Simple WAV file writing without external dependencies"""
        # This is a very basic WAV writer - for production use proper libraries
        import struct
        import wave
        
        # Convert float32 to int16
        audio_int16 = (audio * 32767).astype(np.int16)
        
        with wave.open(str(path), 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
    
    def run_comprehensive_tests(self):
        """Run comprehensive time-stretching tests"""
        logger.info("Starting comprehensive time-stretching tests...")
        
        # Setup
        self.setup_output_directory()
        
        # Generate synthetic audio
        logger.info("Generating synthetic speech-like audio...")
        original_audio = self.generate_synthetic_audio()
        
        # Save original audio
        original_path = self.output_dir / "original.wav"
        if AUDIO_LIBS_AVAILABLE:
            sf.write(original_path, original_audio, self.sample_rate)
        else:
            self._write_wav_simple(original_path, original_audio, self.sample_rate)
        
        logger.info(f"Original audio saved: {original_path}")
        
        # Test each rate
        for rate in self.test_rates:
            try:
                metrics = self.benchmark_rate(original_audio, rate)
                self.results[rate] = metrics
                
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
                'Rate_%', 'Speed_Multiplier', 'RTF_Original', 'RTF_Stretched', 
                'Generation_Time_ms', 'Stretch_Time_ms', 'Total_Time_ms',
                'Original_Duration_s', 'Fast_Duration_s', 'Corrected_Duration_s',
                'Improvement_%'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for rate in sorted(self.results.keys()):
                metrics = self.results[rate]
                writer.writerow({
                    'Rate_%': rate,
                    'Speed_Multiplier': f"{metrics['speed_multiplier']:.2f}",
                    'RTF_Original': f"{metrics['rtf_original']:.4f}",
                    'RTF_Stretched': f"{metrics['rtf_stretched']:.4f}",
                    'Generation_Time_ms': f"{metrics['generation_time'] * 1000:.1f}",
                    'Stretch_Time_ms': f"{metrics['stretch_time'] * 1000:.1f}",
                    'Total_Time_ms': f"{metrics['total_time'] * 1000:.1f}",
                    'Original_Duration_s': f"{metrics['original_duration']:.2f}",
                    'Fast_Duration_s': f"{metrics['fast_duration']:.2f}",
                    'Corrected_Duration_s': f"{metrics['corrected_duration']:.2f}",
                    'Improvement_%': f"{metrics['improvement_percent']:.1f}"
                })
        
        logger.info(f"CSV report saved: {csv_path}")
    
    def generate_markdown_report(self):
        """Generate markdown benchmark report"""
        report = []
        report.append("# Time-Stretching Benchmark Report")
        report.append("=" * 50)
        report.append("")
        report.append("## Test Configuration")
        report.append("")
        report.append(f"- **Audio Type:** Synthetic speech-like signal")
        report.append(f"- **Duration:** {self.duration} seconds")
        report.append(f"- **Sample Rate:** {self.sample_rate} Hz")
        report.append(f"- **Test Rates:** {', '.join(map(str, self.test_rates))}%")
        report.append(f"- **Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary table
        report.append("## Performance Summary")
        report.append("")
        report.append("| Rate % | Speed | RTF Original | RTF Stretched | Improvement % | Generation (ms) | Stretch (ms) | Total (ms) |")
        report.append("|--------|-------|--------------|---------------|---------------|-----------------|--------------|------------|")
        
        for rate in sorted(self.results.keys()):
            metrics = self.results[rate]
            report.append(f"| {rate:6d} | {metrics['speed_multiplier']:5.1f}x | "
                         f"{metrics['rtf_original']:12.3f} | {metrics['rtf_stretched']:13.3f} | "
                         f"{metrics['improvement_percent']:13.1f} | {metrics['generation_time']*1000:15.1f} | "
                         f"{metrics['stretch_time']*1000:12.1f} | {metrics['total_time']*1000:10.1f} |")
        
        report.append("")
        
        # Analysis
        if self.results:
            best_rate = min(self.results.keys(), key=lambda r: self.results[r]['rtf_stretched'])
            best_metrics = self.results[best_rate]
            
            report.append("## Analysis")
            report.append("")
            report.append(f"**Best Rate:** {best_rate}% (RTF: {best_metrics['rtf_stretched']:.3f})")
            report.append(f"**Best Improvement:** {best_metrics['improvement_percent']:.1f}%")
            report.append("")
            
            # Recommendations
            report.append("## Recommendations")
            report.append("")
            
            if best_metrics['rtf_stretched'] < 0.8:
                report.append("✅ **Recommended:** Time-stretching shows significant latency improvement")
                report.append(f"   - Use rate: {best_rate}%")
                report.append(f"   - Expected RTF improvement: {best_metrics['rtf_original']:.3f} → {best_metrics['rtf_stretched']:.3f}")
            elif best_metrics['rtf_stretched'] < 1.0:
                report.append("⚠️  **Marginal:** Time-stretching shows modest improvement")
                report.append("   - Consider enabling for longer texts only")
            else:
                report.append("❌ **Not Recommended:** Time-stretching adds overhead without benefit")
                report.append("   - Keep feature disabled")
        
        report.append("")
        report.append("## Audio Samples")
        report.append("")
        report.append("Generated audio samples are available in `samples/time-stretched/`:")
        report.append("- `original.wav` - Original synthetic audio")
        
        for rate in sorted(self.results.keys()):
            report.append(f"- `raw_{rate}p.wav` - Audio generated at {1 + rate/100:.1f}x speed")
            report.append(f"- `corrected_{rate}p.wav` - Time-stretched back to normal speed")
        
        # Save report
        report_path = self.output_dir / "reports" / "benchmark_report.md"
        with open(report_path, 'w') as f:
            f.write("\n".join(report))
        
        logger.info(f"Markdown report saved: {report_path}")
    
    def generate_json_report(self):
        """Generate JSON report with detailed metrics"""
        json_data = {
            "test_configuration": {
                "audio_type": "synthetic_speech_like",
                "duration_seconds": self.duration,
                "sample_rate": self.sample_rate,
                "test_rates": self.test_rates,
                "generated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "audio_libraries_available": AUDIO_LIBS_AVAILABLE
            },
            "results": self.results
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
        best_rate = min(self.results.keys(), key=lambda r: self.results[r]['rtf_stretched'])
        best_metrics = self.results[best_rate]
        
        print(f"\n🏆 Best Rate: {best_rate}%")
        print(f"   RTF: {best_metrics['rtf_original']:.3f} → {best_metrics['rtf_stretched']:.3f}")
        print(f"   Improvement: {best_metrics['improvement_percent']:.1f}%")
        
        # Recommendation
        if best_metrics['rtf_stretched'] < 0.8:
            print("\n✅ RECOMMENDATION: Enable time-stretching")
            print(f"   Significant latency improvement achieved")
        elif best_metrics['rtf_stretched'] < 1.0:
            print("\n⚠️  RECOMMENDATION: Consider for longer texts")
            print(f"   Modest improvement, test with real workloads")
        else:
            print("\n❌ RECOMMENDATION: Keep disabled")
            print(f"   No significant benefit observed")
        
        print(f"\n📁 Results saved to: {self.output_dir}")
        print("="*60)

def main():
    """Main execution function"""
    print("🚀 Starting Time-Stretching Sample Generation")
    print("=" * 50)
    
    try:
        generator = TimeStretchingSampleGenerator()
        generator.run_comprehensive_tests()
        generator.print_summary()
        
        print("\n✅ Time-stretching sample generation completed successfully!")
        
    except Exception as e:
        logger.error(f"Sample generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
