#!/usr/bin/env python3
"""
Time-Stretching Optimization Benchmark Script
Tests different time-stretching rates and measures performance metrics
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.audio.time_stretcher import TimeStretcher, TimeStretchConfig, StretchQuality
from LiteTTS.audio.segment import AudioSegment
from LiteTTS.tts.synthesizer import TTSSynthesizer
from LiteTTS.models import TTSConfiguration, TTSRequest

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TimeStretchingBenchmark:
    """Benchmark time-stretching optimization feature"""
    
    def __init__(self, output_dir: str = "samples/time-stretched"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Test configuration
        self.test_text = "The quick brown fox jumps over the lazy dog. This is a test of the time-stretching optimization feature."
        self.test_rates = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # 10% to 100% (2x speed)
        self.quality_levels = ['low', 'medium', 'high']
        
        # Results storage
        self.results = {}
        
        logger.info(f"Benchmark initialized. Output directory: {self.output_dir}")
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark across all rates and quality levels"""
        logger.info("Starting comprehensive time-stretching benchmark")
        
        try:
            # Initialize TTS system
            config = self._load_tts_config()
            synthesizer = TTSSynthesizer(config)
            
            # Generate baseline audio (no time-stretching)
            baseline_audio = self._generate_baseline_audio(synthesizer)
            
            # Test each quality level
            for quality in self.quality_levels:
                logger.info(f"Testing quality level: {quality}")
                self.results[quality] = {}
                
                # Test each rate
                for rate in self.test_rates:
                    logger.info(f"Testing rate: {rate}%")
                    
                    try:
                        result = self._benchmark_rate(synthesizer, baseline_audio, rate, quality)
                        self.results[quality][rate] = result
                        
                        # Save audio samples
                        self._save_audio_samples(result, rate, quality)
                        
                    except Exception as e:
                        logger.error(f"Failed to benchmark rate {rate}% with quality {quality}: {e}")
                        self.results[quality][rate] = {"error": str(e)}
            
            # Generate summary report
            summary = self._generate_summary()
            self._save_results(summary)
            
            logger.info("Benchmark completed successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            raise
    
    def _load_tts_config(self) -> TTSConfiguration:
        """Load TTS configuration"""
        # Use default configuration for benchmarking
        return TTSConfiguration(
            sample_rate=24000,
            chunk_size=100,
            device="cpu",  # Use CPU for consistent benchmarking
            default_voice="af_heart"
        )
    
    def _generate_baseline_audio(self, synthesizer: TTSSynthesizer) -> AudioSegment:
        """Generate baseline audio without time-stretching"""
        logger.info("Generating baseline audio")
        
        request = TTSRequest(
            input=self.test_text,
            voice="af_heart",
            speed=1.0,
            response_format="wav"
        )
        
        start_time = time.perf_counter()
        audio = synthesizer.synthesize(request)
        generation_time = time.perf_counter() - start_time
        
        # Save baseline audio
        baseline_path = self.output_dir / "baseline.wav"
        self._save_audio_to_file(audio, baseline_path)
        
        logger.info(f"Baseline audio generated: {audio.duration:.2f}s, generation time: {generation_time:.3f}s")
        return audio
    
    def _benchmark_rate(self, synthesizer: TTSSynthesizer, baseline_audio: AudioSegment, 
                       rate: int, quality: str) -> Dict[str, Any]:
        """Benchmark a specific rate and quality combination"""
        
        # Configure time-stretching
        stretch_config = TimeStretchConfig(
            enabled=True,
            compress_playback_rate=rate,
            correction_quality=StretchQuality(quality)
        )
        
        time_stretcher = TimeStretcher(stretch_config)
        
        # Measure generation at faster speed
        generation_speed = time_stretcher.get_generation_speed_multiplier()
        
        start_time = time.perf_counter()
        
        # Generate audio at faster speed
        request = TTSRequest(
            input=self.test_text,
            voice="af_heart",
            speed=generation_speed,
            response_format="wav"
        )
        
        fast_audio = synthesizer.synthesize(request)
        generation_time = time.perf_counter() - start_time
        
        # Apply time-stretching
        stretch_start = time.perf_counter()
        corrected_audio, metrics = time_stretcher.stretch_audio_to_normal_speed(
            fast_audio, generation_speed
        )
        stretch_time = time.perf_counter() - stretch_start
        
        # Calculate metrics
        total_time = generation_time + stretch_time
        rtf_original = generation_time / baseline_audio.duration
        rtf_stretched = total_time / corrected_audio.duration
        
        # Quality assessment (basic)
        quality_score = self._assess_audio_quality(baseline_audio, corrected_audio)
        
        return {
            "rate_percent": rate,
            "quality_level": quality,
            "generation_speed": generation_speed,
            "baseline_duration": baseline_audio.duration,
            "fast_audio_duration": fast_audio.duration,
            "corrected_duration": corrected_audio.duration,
            "generation_time": generation_time,
            "stretch_time": stretch_time,
            "total_time": total_time,
            "rtf_original": rtf_original,
            "rtf_stretched": rtf_stretched,
            "rtf_improvement": rtf_original - rtf_stretched,
            "quality_score": quality_score,
            "fast_audio": fast_audio,
            "corrected_audio": corrected_audio
        }
    
    def _assess_audio_quality(self, baseline: AudioSegment, corrected: AudioSegment) -> float:
        """Basic audio quality assessment (placeholder for more sophisticated metrics)"""
        try:
            # Simple RMS comparison as a basic quality metric
            baseline_rms = np.sqrt(np.mean(baseline.audio_data ** 2))
            corrected_rms = np.sqrt(np.mean(corrected.audio_data ** 2))
            
            # Quality score based on RMS similarity (0-1, higher is better)
            rms_ratio = min(baseline_rms, corrected_rms) / max(baseline_rms, corrected_rms)
            
            # Duration similarity
            duration_ratio = min(baseline.duration, corrected.duration) / max(baseline.duration, corrected.duration)
            
            # Combined score
            quality_score = (rms_ratio + duration_ratio) / 2
            
            return quality_score
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
            return 0.5  # Neutral score
    
    def _save_audio_samples(self, result: Dict[str, Any], rate: int, quality: str):
        """Save audio samples for manual review"""
        try:
            # Save fast (raw) audio
            fast_path = self.output_dir / f"raw_{rate}p_{quality}.wav"
            self._save_audio_to_file(result["fast_audio"], fast_path)
            
            # Save corrected audio
            corrected_path = self.output_dir / f"corrected_{rate}p_{quality}.wav"
            self._save_audio_to_file(result["corrected_audio"], corrected_path)
            
        except Exception as e:
            logger.warning(f"Failed to save audio samples for rate {rate}%, quality {quality}: {e}")
    
    def _save_audio_to_file(self, audio: AudioSegment, path: Path):
        """Save audio segment to file"""
        try:
            # Convert to bytes and save
            audio_bytes = audio.to_wav_bytes()
            with open(path, 'wb') as f:
                f.write(audio_bytes)
                
        except Exception as e:
            logger.warning(f"Failed to save audio to {path}: {e}")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate benchmark summary"""
        summary = {
            "test_configuration": {
                "test_text": self.test_text,
                "rates_tested": self.test_rates,
                "quality_levels": self.quality_levels
            },
            "results": self.results,
            "recommendations": self._generate_recommendations()
        }
        
        return summary
    
    def _generate_recommendations(self) -> Dict[str, Any]:
        """Generate recommendations based on benchmark results"""
        recommendations = {
            "optimal_rate": None,
            "optimal_quality": None,
            "rtf_improvement": 0.0,
            "quality_threshold": 0.8,
            "notes": []
        }
        
        try:
            best_improvement = 0.0
            best_config = None
            
            for quality in self.quality_levels:
                if quality not in self.results:
                    continue
                    
                for rate in self.test_rates:
                    if rate not in self.results[quality]:
                        continue
                        
                    result = self.results[quality][rate]
                    if "error" in result:
                        continue
                    
                    # Check if this configuration is better
                    rtf_improvement = result.get("rtf_improvement", 0.0)
                    quality_score = result.get("quality_score", 0.0)
                    
                    if (rtf_improvement > best_improvement and 
                        quality_score >= recommendations["quality_threshold"]):
                        best_improvement = rtf_improvement
                        best_config = (rate, quality)
            
            if best_config:
                recommendations["optimal_rate"] = best_config[0]
                recommendations["optimal_quality"] = best_config[1]
                recommendations["rtf_improvement"] = best_improvement
                recommendations["notes"].append(f"Best configuration: {best_config[0]}% rate with {best_config[1]} quality")
            else:
                recommendations["notes"].append("No configuration met quality threshold")
                
        except Exception as e:
            logger.warning(f"Failed to generate recommendations: {e}")
            recommendations["notes"].append(f"Recommendation generation failed: {e}")
        
        return recommendations
    
    def _save_results(self, summary: Dict[str, Any]):
        """Save benchmark results to file"""
        try:
            # Remove audio objects for JSON serialization
            clean_summary = self._clean_results_for_json(summary)
            
            results_path = self.output_dir / "benchmark_results.json"
            with open(results_path, 'w') as f:
                json.dump(clean_summary, f, indent=2)
            
            logger.info(f"Results saved to {results_path}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def _clean_results_for_json(self, data: Any) -> Any:
        """Remove non-serializable objects from results"""
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                if key in ["fast_audio", "corrected_audio"]:
                    continue  # Skip audio objects
                cleaned[key] = self._clean_results_for_json(value)
            return cleaned
        elif isinstance(data, list):
            return [self._clean_results_for_json(item) for item in data]
        else:
            return data

def main():
    """Main benchmark execution"""
    print("Time-Stretching Optimization Benchmark")
    print("=" * 50)
    
    try:
        benchmark = TimeStretchingBenchmark()
        results = benchmark.run_full_benchmark()
        
        print("\nBenchmark Summary:")
        print(f"Optimal rate: {results['recommendations']['optimal_rate']}%")
        print(f"Optimal quality: {results['recommendations']['optimal_quality']}")
        print(f"RTF improvement: {results['recommendations']['rtf_improvement']:.3f}")
        
        print(f"\nResults saved to: {benchmark.output_dir}")
        print("Review audio samples and benchmark_results.json for detailed analysis")
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
