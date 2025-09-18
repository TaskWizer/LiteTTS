#!/usr/bin/env python3
"""
Comprehensive Whisper Alternatives Performance Analysis for LiteTTS
Evaluates Distil-Whisper, Faster-Whisper, OpenAI Whisper variants, and other optimized implementations
for edge hardware deployment with RTF < 1.0 targets.
"""

import os
import sys
import time
import json
import psutil
import threading
import numpy as np
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
import asyncio
import aiohttp
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

@dataclass
class WhisperModelConfig:
    """Configuration for a Whisper model variant"""
    name: str
    model_id: str
    model_size_mb: float
    implementation: str  # 'distil-whisper', 'faster-whisper', 'openai-whisper', 'whisper-cpp', 'onnx', 'openvino'
    quantization: Optional[str] = None  # 'int8', 'int4', 'fp16', 'fp32'
    language: str = "en"
    device: str = "cpu"
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EdgeHardwareSpec:
    """Edge hardware specification for testing"""
    name: str
    cpu_model: str
    cpu_cores: int
    cpu_freq_ghz: float
    ram_gb: int
    architecture: str  # 'arm64', 'x86_64'
    simd_support: List[str]  # ['neon', 'avx2', 'sse4.1']
    os_info: str
    
@dataclass
class PerformanceResult:
    """Performance measurement result"""
    model_config: WhisperModelConfig
    hardware_spec: EdgeHardwareSpec
    audio_duration_s: float
    processing_time_s: float
    rtf: float  # Real-time factor
    peak_memory_mb: float
    avg_memory_mb: float
    peak_cpu_percent: float
    avg_cpu_percent: float
    transcription: str
    confidence_score: float
    wer: Optional[float] = None  # Word Error Rate vs reference
    model_load_time_s: float = 0.0
    cold_start_time_s: float = 0.0
    error_message: Optional[str] = None
    success: bool = True

@dataclass
class AudioTestSample:
    """Test audio sample with metadata"""
    file_path: str
    duration_s: float
    sample_rate: int
    reference_transcription: str
    audio_quality: str  # 'studio', 'phone', 'noisy'
    content_type: str  # 'technical', 'audiobook', 'podcast', 'conversation'
    speaker_info: Dict[str, Any] = field(default_factory=dict)

class SystemMonitor:
    """System resource monitoring during benchmarks"""
    
    def __init__(self):
        self.monitoring = False
        self.metrics = []
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring = True
        self.metrics = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        
    def stop_monitoring(self) -> Tuple[float, float, float, float]:
        """Stop monitoring and return peak/avg memory and CPU"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
        if not self.metrics:
            return 0.0, 0.0, 0.0, 0.0
            
        memory_values = [m['memory_mb'] for m in self.metrics]
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        
        return (
            max(memory_values),
            sum(memory_values) / len(memory_values),
            max(cpu_values),
            sum(cpu_values) / len(cpu_values)
        )
        
    def _monitor_loop(self):
        """Monitoring loop"""
        process = psutil.Process()
        while self.monitoring:
            try:
                memory_info = process.memory_info()
                cpu_percent = process.cpu_percent()
                
                self.metrics.append({
                    'timestamp': time.time(),
                    'memory_mb': memory_info.rss / 1024 / 1024,
                    'cpu_percent': cpu_percent
                })
                time.sleep(0.1)  # Monitor every 100ms
            except Exception as e:
                logger.warning(f"Monitoring error: {e}")
                break

class WhisperAlternativesAnalyzer:
    """Main analyzer for Whisper alternatives performance"""
    
    def __init__(self, output_dir: str = "whisper_analysis_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Test configurations
        self.model_configs = self._get_model_configurations()
        self.hardware_specs = self._detect_hardware_specs()
        self.test_samples = []
        
        # Results storage
        self.results = []
        
        logger.info(f"WhisperAlternativesAnalyzer initialized with output dir: {self.output_dir}")
        
    def _get_model_configurations(self) -> List[WhisperModelConfig]:
        """Get all model configurations to test"""
        configs = []
        
        # Distil-Whisper models
        configs.extend([
            WhisperModelConfig(
                name="distil-small.en",
                model_id="distil-whisper/distil-small.en",
                model_size_mb=244,
                implementation="distil-whisper"
            ),
            WhisperModelConfig(
                name="distil-medium.en",
                model_id="distil-whisper/distil-medium.en", 
                model_size_mb=769,
                implementation="distil-whisper"
            ),
            WhisperModelConfig(
                name="distil-large-v2",
                model_id="distil-whisper/distil-large-v2",
                model_size_mb=1500,
                implementation="distil-whisper"
            )
        ])
        
        # OpenAI Whisper models
        configs.extend([
            WhisperModelConfig(
                name="whisper-tiny",
                model_id="openai/whisper-tiny",
                model_size_mb=39,
                implementation="openai-whisper"
            ),
            WhisperModelConfig(
                name="whisper-tiny.en",
                model_id="openai/whisper-tiny.en",
                model_size_mb=39,
                implementation="openai-whisper"
            ),
            WhisperModelConfig(
                name="whisper-base",
                model_id="openai/whisper-base",
                model_size_mb=74,
                implementation="openai-whisper"
            ),
            WhisperModelConfig(
                name="whisper-base.en",
                model_id="openai/whisper-base.en",
                model_size_mb=74,
                implementation="openai-whisper"
            )
        ])
        
        # Faster-Whisper with quantization variants
        for model_size in ["tiny", "base", "small"]:
            for quant in ["int8", "int4", "fp16"]:
                configs.append(WhisperModelConfig(
                    name=f"faster-whisper-{model_size}-{quant}",
                    model_id=f"openai/whisper-{model_size}",
                    model_size_mb=39 if model_size == "tiny" else 74 if model_size == "base" else 244,
                    implementation="faster-whisper",
                    quantization=quant
                ))
        
        return configs
        
    def _detect_hardware_specs(self) -> EdgeHardwareSpec:
        """Detect current hardware specifications"""
        import platform
        
        # Get CPU info
        cpu_info = {}
        try:
            if platform.system() == "Linux":
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if ":" in line:
                            key, value = line.split(":", 1)
                            cpu_info[key.strip()] = value.strip()
        except:
            pass
            
        # Detect SIMD support
        simd_support = []
        try:
            import cpuinfo
            info = cpuinfo.get_cpu_info()
            flags = info.get('flags', [])
            if 'avx2' in flags:
                simd_support.append('avx2')
            if 'sse4_1' in flags:
                simd_support.append('sse4.1')
            if 'neon' in flags:
                simd_support.append('neon')
        except:
            # Fallback detection
            if platform.machine().lower() in ['aarch64', 'arm64']:
                simd_support.append('neon')
            elif platform.machine().lower() in ['x86_64', 'amd64']:
                simd_support.extend(['sse4.1', 'avx2'])  # Assume modern x86
                
        return EdgeHardwareSpec(
            name=f"{platform.node()}-{platform.machine()}",
            cpu_model=cpu_info.get("model name", platform.processor()),
            cpu_cores=psutil.cpu_count(logical=False),
            cpu_freq_ghz=psutil.cpu_freq().max / 1000 if psutil.cpu_freq() else 2.0,
            ram_gb=psutil.virtual_memory().total / (1024**3),
            architecture=platform.machine(),
            simd_support=simd_support,
            os_info=f"{platform.system()} {platform.release()}"
        )
        
    def generate_test_audio_samples(self) -> List[AudioTestSample]:
        """Generate standardized test audio samples"""
        samples = []
        
        # Test durations as specified in requirements
        test_durations = [5, 15, 30, 60, 120]
        
        # Test content types
        test_texts = {
            "technical": "The neural network architecture utilizes transformer-based attention mechanisms with multi-head self-attention layers.",
            "audiobook": "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness.",
            "podcast": "Welcome to today's episode where we'll be discussing the latest developments in artificial intelligence and machine learning.",
            "conversation": "Hey, how are you doing today? I was wondering if you could help me with this project I'm working on."
        }
        
        # Generate synthetic audio samples (placeholder - in real implementation, use TTS or recorded samples)
        for duration in test_durations:
            for content_type, text in test_texts.items():
                # Repeat text to fill duration
                words_per_minute = 150
                target_words = int((duration / 60) * words_per_minute)
                repeated_text = (text + " ") * (target_words // len(text.split()) + 1)
                repeated_text = " ".join(repeated_text.split()[:target_words])
                
                sample = AudioTestSample(
                    file_path=f"test_audio_{content_type}_{duration}s.wav",
                    duration_s=duration,
                    sample_rate=16000,
                    reference_transcription=repeated_text,
                    audio_quality="studio",
                    content_type=content_type
                )
                samples.append(sample)
                
        return samples
        
    async def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive performance analysis"""
        logger.info("Starting comprehensive Whisper alternatives analysis")
        
        # Generate test samples
        self.test_samples = self.generate_test_audio_samples()
        
        # Run analysis for each model configuration
        for model_config in self.model_configs:
            logger.info(f"Analyzing model: {model_config.name}")
            
            try:
                model_results = await self._analyze_model(model_config)
                self.results.extend(model_results)
            except Exception as e:
                logger.error(f"Failed to analyze model {model_config.name}: {e}")
                
        # Generate comprehensive report
        report = self._generate_analysis_report()
        
        # Save results
        self._save_results()
        
        return report
        
    async def _analyze_model(self, model_config: WhisperModelConfig) -> List[PerformanceResult]:
        """Analyze a specific model configuration"""
        results = []
        
        # Test with each audio sample
        for sample in self.test_samples:
            try:
                result = await self._benchmark_model_on_sample(model_config, sample)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to benchmark {model_config.name} on {sample.file_path}: {e}")
                
        return results
        
    async def _benchmark_model_on_sample(self, model_config: WhisperModelConfig, 
                                       sample: AudioTestSample) -> PerformanceResult:
        """Benchmark a model on a specific audio sample"""
        monitor = SystemMonitor()
        
        try:
            # Start monitoring
            monitor.start_monitoring()
            
            # Measure model loading time
            load_start = time.time()
            model = await self._load_model(model_config)
            load_time = time.time() - load_start
            
            # Measure cold start time (first inference)
            cold_start = time.time()
            
            # Generate or load test audio
            audio_data = await self._get_test_audio(sample)
            
            # Perform transcription
            transcribe_start = time.time()
            transcription, confidence = await self._transcribe_audio(model, audio_data, model_config)
            processing_time = time.time() - transcribe_start
            
            cold_start_time = time.time() - cold_start
            
            # Calculate RTF
            rtf = processing_time / sample.duration_s
            
            # Calculate WER if reference available
            wer = self._calculate_wer(sample.reference_transcription, transcription) if sample.reference_transcription else None
            
            # Stop monitoring and get metrics
            peak_mem, avg_mem, peak_cpu, avg_cpu = monitor.stop_monitoring()
            
            return PerformanceResult(
                model_config=model_config,
                hardware_spec=self.hardware_specs,
                audio_duration_s=sample.duration_s,
                processing_time_s=processing_time,
                rtf=rtf,
                peak_memory_mb=peak_mem,
                avg_memory_mb=avg_mem,
                peak_cpu_percent=peak_cpu,
                avg_cpu_percent=avg_cpu,
                transcription=transcription,
                confidence_score=confidence,
                wer=wer,
                model_load_time_s=load_time,
                cold_start_time_s=cold_start_time,
                success=True
            )
            
        except Exception as e:
            monitor.stop_monitoring()
            return PerformanceResult(
                model_config=model_config,
                hardware_spec=self.hardware_specs,
                audio_duration_s=sample.duration_s,
                processing_time_s=0.0,
                rtf=float('inf'),
                peak_memory_mb=0.0,
                avg_memory_mb=0.0,
                peak_cpu_percent=0.0,
                avg_cpu_percent=0.0,
                transcription="",
                confidence_score=0.0,
                error_message=str(e),
                success=False
            )

    async def _load_model(self, model_config: WhisperModelConfig):
        """Load a model based on its configuration"""
        if model_config.implementation == "distil-whisper":
            return await self._load_distil_whisper(model_config)
        elif model_config.implementation == "faster-whisper":
            return await self._load_faster_whisper(model_config)
        elif model_config.implementation == "openai-whisper":
            return await self._load_openai_whisper(model_config)
        elif model_config.implementation == "whisper-cpp":
            return await self._load_whisper_cpp(model_config)
        else:
            raise ValueError(f"Unsupported implementation: {model_config.implementation}")

    async def _load_distil_whisper(self, model_config: WhisperModelConfig):
        """Load Distil-Whisper model"""
        try:
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
            import torch

            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_config.model_id,
                torch_dtype=torch.float16 if model_config.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
                use_safetensors=True
            )
            processor = AutoProcessor.from_pretrained(model_config.model_id)

            return {"model": model, "processor": processor, "type": "distil-whisper"}
        except ImportError:
            raise ImportError("transformers library required for Distil-Whisper")

    async def _load_faster_whisper(self, model_config: WhisperModelConfig):
        """Load Faster-Whisper model"""
        try:
            from faster_whisper import WhisperModel

            model = WhisperModel(
                model_config.model_id.split("/")[-1],  # Extract model size
                device="cpu",
                compute_type=model_config.quantization or "int8"
            )

            return {"model": model, "type": "faster-whisper"}
        except ImportError:
            raise ImportError("faster-whisper library required")

    async def _load_openai_whisper(self, model_config: WhisperModelConfig):
        """Load OpenAI Whisper model"""
        try:
            import whisper

            model = whisper.load_model(model_config.model_id.split("/")[-1])

            return {"model": model, "type": "openai-whisper"}
        except ImportError:
            raise ImportError("openai-whisper library required")

    async def _load_whisper_cpp(self, model_config: WhisperModelConfig):
        """Load Whisper.cpp model"""
        # Placeholder for whisper.cpp integration
        raise NotImplementedError("Whisper.cpp integration not yet implemented")

    async def _transcribe_audio(self, model, audio_data: np.ndarray,
                              model_config: WhisperModelConfig) -> Tuple[str, float]:
        """Transcribe audio using the loaded model"""
        if model["type"] == "distil-whisper":
            return await self._transcribe_distil_whisper(model, audio_data)
        elif model["type"] == "faster-whisper":
            return await self._transcribe_faster_whisper(model, audio_data)
        elif model["type"] == "openai-whisper":
            return await self._transcribe_openai_whisper(model, audio_data)
        else:
            raise ValueError(f"Unsupported model type: {model['type']}")

    async def _transcribe_distil_whisper(self, model, audio_data: np.ndarray) -> Tuple[str, float]:
        """Transcribe using Distil-Whisper"""
        try:
            import torch

            processor = model["processor"]
            whisper_model = model["model"]

            # Process audio
            inputs = processor(audio_data, sampling_rate=16000, return_tensors="pt")

            # Generate transcription
            with torch.no_grad():
                predicted_ids = whisper_model.generate(inputs["input_features"])
                transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

            return transcription, 1.0  # Distil-Whisper doesn't provide confidence scores
        except Exception as e:
            logger.error(f"Distil-Whisper transcription failed: {e}")
            return "", 0.0

    async def _transcribe_faster_whisper(self, model, audio_data: np.ndarray) -> Tuple[str, float]:
        """Transcribe using Faster-Whisper"""
        try:
            whisper_model = model["model"]

            # Transcribe
            segments, info = whisper_model.transcribe(audio_data, beam_size=5)

            # Combine segments
            transcription = " ".join([segment.text for segment in segments])
            confidence = info.language_probability if hasattr(info, 'language_probability') else 1.0

            return transcription, confidence
        except Exception as e:
            logger.error(f"Faster-Whisper transcription failed: {e}")
            return "", 0.0

    async def _transcribe_openai_whisper(self, model, audio_data: np.ndarray) -> Tuple[str, float]:
        """Transcribe using OpenAI Whisper"""
        try:
            whisper_model = model["model"]

            # Transcribe
            result = whisper_model.transcribe(audio_data)

            return result["text"], 1.0  # OpenAI Whisper doesn't provide confidence scores
        except Exception as e:
            logger.error(f"OpenAI Whisper transcription failed: {e}")
            return "", 0.0

    async def _get_test_audio(self, sample: AudioTestSample) -> np.ndarray:
        """Get test audio data (generate if needed)"""
        # For now, generate synthetic audio or use existing samples
        # In a real implementation, this would load actual audio files
        duration = sample.duration_s
        sample_rate = sample.sample_rate

        # Generate simple sine wave as placeholder
        t = np.linspace(0, duration, int(duration * sample_rate))
        audio_data = 0.1 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave

        return audio_data.astype(np.float32)

    def _calculate_wer(self, reference: str, hypothesis: str) -> float:
        """Calculate Word Error Rate"""
        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()

        # Simple WER calculation using edit distance
        d = np.zeros((len(ref_words) + 1, len(hyp_words) + 1))

        for i in range(len(ref_words) + 1):
            d[i][0] = i
        for j in range(len(hyp_words) + 1):
            d[0][j] = j

        for i in range(1, len(ref_words) + 1):
            for j in range(1, len(hyp_words) + 1):
                if ref_words[i-1] == hyp_words[j-1]:
                    d[i][j] = d[i-1][j-1]
                else:
                    d[i][j] = min(d[i-1][j], d[i][j-1], d[i-1][j-1]) + 1

        return d[len(ref_words)][len(hyp_words)] / len(ref_words) if ref_words else 0.0

    def _generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        if not self.results:
            return {"error": "No results available"}

        # Group results by model
        model_results = {}
        for result in self.results:
            model_name = result.model_config.name
            if model_name not in model_results:
                model_results[model_name] = []
            model_results[model_name].append(result)

        # Calculate summary statistics
        summary = {}
        for model_name, results in model_results.items():
            successful_results = [r for r in results if r.success]

            if successful_results:
                rtfs = [r.rtf for r in successful_results]
                memories = [r.peak_memory_mb for r in successful_results]
                wers = [r.wer for r in successful_results if r.wer is not None]

                summary[model_name] = {
                    "avg_rtf": np.mean(rtfs),
                    "min_rtf": np.min(rtfs),
                    "max_rtf": np.max(rtfs),
                    "avg_memory_mb": np.mean(memories),
                    "peak_memory_mb": np.max(memories),
                    "avg_wer": np.mean(wers) if wers else None,
                    "success_rate": len(successful_results) / len(results),
                    "model_size_mb": successful_results[0].model_config.model_size_mb,
                    "implementation": successful_results[0].model_config.implementation
                }
            else:
                summary[model_name] = {
                    "success_rate": 0.0,
                    "error": "All tests failed"
                }

        # Find best performers
        rtf_performers = sorted(
            [(name, stats) for name, stats in summary.items()
             if isinstance(stats, dict) and "avg_rtf" in stats],
            key=lambda x: x[1]["avg_rtf"]
        )

        memory_performers = sorted(
            [(name, stats) for name, stats in summary.items()
             if isinstance(stats, dict) and "avg_memory_mb" in stats],
            key=lambda x: x[1]["avg_memory_mb"]
        )

        return {
            "hardware_spec": asdict(self.hardware_specs),
            "total_models_tested": len(model_results),
            "total_tests_run": len(self.results),
            "model_summary": summary,
            "best_rtf_performers": rtf_performers[:5],
            "best_memory_performers": memory_performers[:5],
            "models_meeting_rtf_target": [
                name for name, stats in summary.items()
                if isinstance(stats, dict) and stats.get("avg_rtf", float('inf')) < 1.0
            ],
            "timestamp": datetime.now().isoformat()
        }

    def _save_results(self):
        """Save analysis results to files"""
        # Save detailed results
        results_file = self.output_dir / "detailed_results.json"
        with open(results_file, "w") as f:
            json.dump([asdict(r) for r in self.results], f, indent=2, default=str)

        # Save summary report
        report = self._generate_analysis_report()
        report_file = self.output_dir / "analysis_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Results saved to {self.output_dir}")

async def main():
    """Main function to run the analysis"""
    analyzer = WhisperAlternativesAnalyzer()

    try:
        report = await analyzer.run_comprehensive_analysis()

        print("\n" + "="*80)
        print("WHISPER ALTERNATIVES PERFORMANCE ANALYSIS COMPLETE")
        print("="*80)

        print(f"\nHardware: {report['hardware_spec']['name']}")
        print(f"Total models tested: {report['total_models_tested']}")
        print(f"Total tests run: {report['total_tests_run']}")

        print(f"\nModels meeting RTF < 1.0 target:")
        for model in report['models_meeting_rtf_target']:
            print(f"  ✅ {model}")

        print(f"\nTop RTF performers:")
        for i, (model, stats) in enumerate(report['best_rtf_performers'][:3], 1):
            print(f"  {i}. {model}: RTF {stats['avg_rtf']:.3f}")

        print(f"\nTop memory performers:")
        for i, (model, stats) in enumerate(report['best_memory_performers'][:3], 1):
            print(f"  {i}. {model}: {stats['avg_memory_mb']:.1f} MB")

        print(f"\nDetailed results saved to: {analyzer.output_dir}")

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
