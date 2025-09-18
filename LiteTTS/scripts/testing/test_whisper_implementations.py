#!/usr/bin/env python3
"""
Practical Testing Script for Whisper Alternatives
Tests actual implementations with real audio samples and measures performance
"""

import os
import sys
import time
import json
import numpy as np
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import psutil
import threading
from dataclasses import dataclass
import asyncio

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result for a Whisper implementation"""
    model_name: str
    implementation: str
    audio_duration: float
    processing_time: float
    rtf: float
    peak_memory_mb: float
    transcription: str
    success: bool
    error_message: Optional[str] = None
    model_size_mb: Optional[float] = None
    load_time: Optional[float] = None

class PerformanceMonitor:
    """Monitor system performance during tests"""
    
    def __init__(self):
        self.monitoring = False
        self.peak_memory = 0
        self.memory_samples = []
        
    def start(self):
        self.monitoring = True
        self.peak_memory = 0
        self.memory_samples = []
        self.monitor_thread = threading.Thread(target=self._monitor)
        self.monitor_thread.start()
        
    def stop(self) -> float:
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        return self.peak_memory
        
    def _monitor(self):
        process = psutil.Process()
        while self.monitoring:
            try:
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.memory_samples.append(memory_mb)
                self.peak_memory = max(self.peak_memory, memory_mb)
                time.sleep(0.1)
            except:
                break

class WhisperImplementationTester:
    """Test various Whisper implementations"""
    
    def __init__(self):
        self.test_audio_path = None
        self.test_audio_duration = 0
        self.results = []
        
    def generate_test_audio(self, duration: float = 10.0) -> str:
        """Generate test audio file"""
        try:
            import soundfile as sf
            
            # Generate simple sine wave test audio
            sample_rate = 16000
            t = np.linspace(0, duration, int(duration * sample_rate))
            
            # Create a more complex signal (multiple frequencies)
            audio = (
                0.3 * np.sin(2 * np.pi * 440 * t) +  # A4 note
                0.2 * np.sin(2 * np.pi * 880 * t) +  # A5 note
                0.1 * np.sin(2 * np.pi * 220 * t)    # A3 note
            )
            
            # Add some noise to make it more realistic
            noise = np.random.normal(0, 0.05, len(audio))
            audio = audio + noise
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            sf.write(temp_file.name, audio, sample_rate)
            
            self.test_audio_path = temp_file.name
            self.test_audio_duration = duration
            
            logger.info(f"Generated test audio: {duration}s, saved to {temp_file.name}")
            return temp_file.name
            
        except ImportError:
            logger.error("soundfile library required for audio generation")
            raise
        except Exception as e:
            logger.error(f"Failed to generate test audio: {e}")
            raise
            
    def test_distil_whisper(self, model_id: str = "distil-whisper/distil-small.en") -> TestResult:
        """Test Distil-Whisper implementation"""
        logger.info(f"Testing Distil-Whisper: {model_id}")
        
        try:
            # Import required libraries
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
            import torch
            import soundfile as sf
            
            monitor = PerformanceMonitor()
            
            # Load model
            load_start = time.time()
            monitor.start()
            
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                use_safetensors=True
            )
            processor = AutoProcessor.from_pretrained(model_id)
            
            load_time = time.time() - load_start
            
            # Load test audio
            audio_array, sample_rate = sf.read(self.test_audio_path)
            
            # Transcribe
            start_time = time.time()
            
            inputs = processor(
                audio_array, 
                sampling_rate=sample_rate, 
                return_tensors="pt"
            )
            
            with torch.no_grad():
                predicted_ids = model.generate(
                    inputs["input_features"],
                    max_new_tokens=128,
                    do_sample=False
                )
                
            transcription = processor.batch_decode(
                predicted_ids, 
                skip_special_tokens=True
            )[0]
            
            processing_time = time.time() - start_time
            peak_memory = monitor.stop()
            
            rtf = processing_time / self.test_audio_duration
            
            return TestResult(
                model_name=model_id.split('/')[-1],
                implementation="distil-whisper",
                audio_duration=self.test_audio_duration,
                processing_time=processing_time,
                rtf=rtf,
                peak_memory_mb=peak_memory,
                transcription=transcription,
                success=True,
                load_time=load_time
            )
            
        except ImportError as e:
            return TestResult(
                model_name=model_id.split('/')[-1],
                implementation="distil-whisper",
                audio_duration=self.test_audio_duration,
                processing_time=0,
                rtf=float('inf'),
                peak_memory_mb=0,
                transcription="",
                success=False,
                error_message=f"Missing dependency: {e}"
            )
        except Exception as e:
            return TestResult(
                model_name=model_id.split('/')[-1],
                implementation="distil-whisper",
                audio_duration=self.test_audio_duration,
                processing_time=0,
                rtf=float('inf'),
                peak_memory_mb=0,
                transcription="",
                success=False,
                error_message=str(e)
            )
            
    def test_faster_whisper(self, model_size: str = "base", compute_type: str = "int8") -> TestResult:
        """Test Faster-Whisper implementation"""
        logger.info(f"Testing Faster-Whisper: {model_size} with {compute_type}")
        
        try:
            from faster_whisper import WhisperModel
            
            monitor = PerformanceMonitor()
            
            # Load model
            load_start = time.time()
            monitor.start()
            
            model = WhisperModel(
                model_size,
                device="cpu",
                compute_type=compute_type,
                cpu_threads=psutil.cpu_count(logical=False),
                num_workers=1
            )
            
            load_time = time.time() - load_start
            
            # Transcribe
            start_time = time.time()
            
            segments, info = model.transcribe(
                self.test_audio_path,
                beam_size=5,
                language="en",
                condition_on_previous_text=False
            )
            
            transcription = " ".join([segment.text for segment in segments])
            
            processing_time = time.time() - start_time
            peak_memory = monitor.stop()
            
            rtf = processing_time / self.test_audio_duration
            
            return TestResult(
                model_name=f"faster-whisper-{model_size}-{compute_type}",
                implementation="faster-whisper",
                audio_duration=self.test_audio_duration,
                processing_time=processing_time,
                rtf=rtf,
                peak_memory_mb=peak_memory,
                transcription=transcription,
                success=True,
                load_time=load_time
            )
            
        except ImportError as e:
            return TestResult(
                model_name=f"faster-whisper-{model_size}-{compute_type}",
                implementation="faster-whisper",
                audio_duration=self.test_audio_duration,
                processing_time=0,
                rtf=float('inf'),
                peak_memory_mb=0,
                transcription="",
                success=False,
                error_message=f"Missing dependency: {e}"
            )
        except Exception as e:
            return TestResult(
                model_name=f"faster-whisper-{model_size}-{compute_type}",
                implementation="faster-whisper",
                audio_duration=self.test_audio_duration,
                processing_time=0,
                rtf=float('inf'),
                peak_memory_mb=0,
                transcription="",
                success=False,
                error_message=str(e)
            )
            
    def test_openai_whisper(self, model_size: str = "base") -> TestResult:
        """Test OpenAI Whisper implementation"""
        logger.info(f"Testing OpenAI Whisper: {model_size}")
        
        try:
            import whisper
            
            monitor = PerformanceMonitor()
            
            # Load model
            load_start = time.time()
            monitor.start()
            
            model = whisper.load_model(model_size)
            
            load_time = time.time() - load_start
            
            # Transcribe
            start_time = time.time()
            
            result = model.transcribe(self.test_audio_path)
            
            processing_time = time.time() - start_time
            peak_memory = monitor.stop()
            
            rtf = processing_time / self.test_audio_duration
            
            return TestResult(
                model_name=f"openai-whisper-{model_size}",
                implementation="openai-whisper",
                audio_duration=self.test_audio_duration,
                processing_time=processing_time,
                rtf=rtf,
                peak_memory_mb=peak_memory,
                transcription=result["text"],
                success=True,
                load_time=load_time
            )
            
        except ImportError as e:
            return TestResult(
                model_name=f"openai-whisper-{model_size}",
                implementation="openai-whisper",
                audio_duration=self.test_audio_duration,
                processing_time=0,
                rtf=float('inf'),
                peak_memory_mb=0,
                transcription="",
                success=False,
                error_message=f"Missing dependency: {e}"
            )
        except Exception as e:
            return TestResult(
                model_name=f"openai-whisper-{model_size}",
                implementation="openai-whisper",
                audio_duration=self.test_audio_duration,
                processing_time=0,
                rtf=float('inf'),
                peak_memory_mb=0,
                transcription="",
                success=False,
                error_message=str(e)
            )
            
    def run_all_tests(self, audio_duration: float = 10.0) -> List[TestResult]:
        """Run all available Whisper implementation tests"""
        logger.info("Starting comprehensive Whisper implementation tests")
        
        # Generate test audio
        self.generate_test_audio(audio_duration)
        
        test_configs = [
            # Distil-Whisper models
            ("distil_whisper", {"model_id": "distil-whisper/distil-small.en"}),
            
            # Faster-Whisper variants
            ("faster_whisper", {"model_size": "tiny", "compute_type": "int8"}),
            ("faster_whisper", {"model_size": "base", "compute_type": "int8"}),
            ("faster_whisper", {"model_size": "small", "compute_type": "int8"}),
            ("faster_whisper", {"model_size": "base", "compute_type": "int4"}),
            
            # OpenAI Whisper models
            ("openai_whisper", {"model_size": "tiny"}),
            ("openai_whisper", {"model_size": "base"}),
        ]
        
        results = []
        
        for test_type, config in test_configs:
            try:
                if test_type == "distil_whisper":
                    result = self.test_distil_whisper(**config)
                elif test_type == "faster_whisper":
                    result = self.test_faster_whisper(**config)
                elif test_type == "openai_whisper":
                    result = self.test_openai_whisper(**config)
                else:
                    continue
                    
                results.append(result)
                
                if result.success:
                    logger.info(f"✅ {result.model_name}: RTF={result.rtf:.3f}, Memory={result.peak_memory_mb:.1f}MB")
                else:
                    logger.warning(f"❌ {result.model_name}: {result.error_message}")
                    
            except Exception as e:
                logger.error(f"Test failed for {test_type} with config {config}: {e}")
                
        # Cleanup
        if self.test_audio_path and os.path.exists(self.test_audio_path):
            os.unlink(self.test_audio_path)
            
        self.results = results
        return results
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        if not self.results:
            return {"error": "No test results available"}
            
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]
        
        # Find best performers
        rtf_performers = sorted(successful_results, key=lambda x: x.rtf)
        memory_performers = sorted(successful_results, key=lambda x: x.peak_memory_mb)
        
        # Models meeting RTF target
        rtf_target_met = [r for r in successful_results if r.rtf < 1.0]
        
        report = {
            "test_summary": {
                "total_tests": len(self.results),
                "successful_tests": len(successful_results),
                "failed_tests": len(failed_results),
                "audio_duration": self.test_audio_duration
            },
            "performance_results": [
                {
                    "model_name": r.model_name,
                    "implementation": r.implementation,
                    "rtf": r.rtf,
                    "memory_mb": r.peak_memory_mb,
                    "processing_time": r.processing_time,
                    "load_time": r.load_time,
                    "meets_rtf_target": r.rtf < 1.0
                }
                for r in successful_results
            ],
            "best_performers": {
                "fastest_rtf": rtf_performers[0].model_name if rtf_performers else None,
                "lowest_memory": memory_performers[0].model_name if memory_performers else None,
                "rtf_target_met": [r.model_name for r in rtf_target_met]
            },
            "failed_tests": [
                {
                    "model_name": r.model_name,
                    "implementation": r.implementation,
                    "error": r.error_message
                }
                for r in failed_results
            ],
            "recommendations": self._generate_recommendations(successful_results)
        }
        
        return report
        
    def _generate_recommendations(self, results: List[TestResult]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        rtf_target_met = [r for r in results if r.rtf < 1.0]
        
        if rtf_target_met:
            fastest = min(rtf_target_met, key=lambda x: x.rtf)
            recommendations.append(f"Primary recommendation: {fastest.model_name} (RTF: {fastest.rtf:.3f})")
            
            lowest_memory = min(rtf_target_met, key=lambda x: x.peak_memory_mb)
            if lowest_memory != fastest:
                recommendations.append(f"For memory-constrained devices: {lowest_memory.model_name} ({lowest_memory.peak_memory_mb:.1f}MB)")
        else:
            recommendations.append("No models met RTF < 1.0 target. Consider:")
            recommendations.append("- Using shorter audio segments")
            recommendations.append("- Upgrading hardware")
            recommendations.append("- Using smaller models")
            
        return recommendations

def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    tester = WhisperImplementationTester()
    
    print("🚀 Starting Whisper Implementation Tests")
    print("=" * 50)
    
    # Run tests with different audio durations
    test_durations = [5.0, 15.0, 30.0]
    
    all_reports = {}
    
    for duration in test_durations:
        print(f"\n📊 Testing with {duration}s audio...")
        
        results = tester.run_all_tests(duration)
        report = tester.generate_report()
        
        all_reports[f"{duration}s"] = report
        
        print(f"\nResults for {duration}s audio:")
        print(f"  Successful tests: {report['test_summary']['successful_tests']}")
        print(f"  Models meeting RTF target: {len(report['best_performers']['rtf_target_met'])}")
        
        if report['best_performers']['fastest_rtf']:
            print(f"  Fastest model: {report['best_performers']['fastest_rtf']}")
            
    # Save comprehensive report
    output_file = "whisper_implementation_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_reports, f, indent=2)
        
    print(f"\n✅ Testing complete! Results saved to {output_file}")
    
    # Print summary recommendations
    print("\n🎯 Summary Recommendations:")
    for duration, report in all_reports.items():
        print(f"\n{duration} audio:")
        for rec in report.get('recommendations', []):
            print(f"  • {rec}")

if __name__ == "__main__":
    main()
