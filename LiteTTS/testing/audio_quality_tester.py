#!/usr/bin/env python3
"""
Automated Audio Quality Testing Framework for Kokoro TTS API

This module provides comprehensive automated testing for TTS audio quality
with objective metrics, external ASR integration, and regression detection.
"""

import asyncio
import json
import logging
import time
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import tempfile
import hashlib
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


@dataclass
class AudioQualityMetrics:
    """Container for audio quality metrics"""
    wer: float = 0.0  # Word Error Rate
    mos_prediction: float = 0.0  # Mean Opinion Score prediction
    prosody_score: float = 0.0  # Prosody naturalness score
    pronunciation_accuracy: float = 0.0  # Pronunciation accuracy score
    processing_time: float = 0.0  # Time to generate audio
    audio_duration: float = 0.0  # Duration of generated audio
    rtf: float = 0.0  # Real-time factor
    confidence_score: float = 0.0  # Overall confidence in metrics
    
    # Detailed metrics
    pitch_variance: float = 0.0
    speaking_rate: float = 0.0  # Words per minute
    silence_ratio: float = 0.0
    spectral_quality: float = 0.0
    
    # Test-specific metrics
    symbol_processing_accuracy: float = 0.0
    currency_processing_accuracy: float = 0.0
    datetime_processing_accuracy: float = 0.0
    
    # Metadata
    voice_model: str = ""
    text_length: int = 0
    test_category: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class AudioTestCase:
    """Represents a single audio quality test case"""
    test_id: str
    input_text: str
    expected_transcription: str
    voice_model: str = "af_heart"
    test_category: str = "general"
    description: str = ""
    priority: str = "normal"  # low, normal, high, critical
    
    # Expected quality thresholds
    min_mos_score: float = 3.0
    max_wer: float = 0.1
    min_pronunciation_accuracy: float = 0.9
    max_rtf: float = 0.25
    
    # Test-specific expectations
    expected_symbols: List[str] = field(default_factory=list)
    expected_pronunciations: Dict[str, str] = field(default_factory=dict)


class AudioQualityTester:
    """
    Comprehensive automated audio quality testing framework
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.audio_config = self.config.get("audio_quality_testing", {})
        
        # API configuration
        self.api_base_url = self.audio_config.get("api_base_url", "http://localhost:8354")
        self.api_timeout = self.audio_config.get("api_timeout", 30)
        
        # External services configuration
        self.asr_config = self.audio_config.get("asr_services", {})
        self.enable_external_asr = self.asr_config.get("enabled", False)
        
        # Quality thresholds
        self.quality_thresholds = self.audio_config.get("quality_thresholds", {
            "min_mos_score": 3.0,
            "max_wer": 0.1,
            "min_pronunciation_accuracy": 0.9,
            "max_rtf": 0.25,
            "min_prosody_score": 0.7
        })
        
        # Performance settings
        self.max_concurrent_tests = self.audio_config.get("max_concurrent_tests", 3)
        self.cache_enabled = self.audio_config.get("cache_enabled", True)
        self.cache_dir = Path(self.audio_config.get("cache_dir", "cache/audio_quality"))
        
        # Initialize components
        self._init_cache_directory()
        self._init_external_services()
        
        # Test results storage
        self.test_results: List[Tuple[AudioTestCase, AudioQualityMetrics]] = []
        self.baseline_metrics: Optional[Dict[str, AudioQualityMetrics]] = None
        
    def _init_cache_directory(self):
        """Initialize cache directory for audio files and results"""
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Audio quality testing cache directory: {self.cache_dir}")
    
    def _init_external_services(self):
        """Initialize external ASR and analysis services"""
        if self.enable_external_asr:
            # Initialize ASR service clients based on configuration
            self.asr_services = {}
            
            # Deepgram configuration
            if self.asr_config.get("deepgram", {}).get("enabled", False):
                try:
                    from .asr_integrations.deepgram_client import DeepgramASRClient
                    self.asr_services["deepgram"] = DeepgramASRClient(
                        api_key=self.asr_config["deepgram"].get("api_key"),
                        config=self.asr_config["deepgram"]
                    )
                    logger.info("Deepgram ASR service initialized")
                except ImportError:
                    logger.warning("Deepgram client not available")
            
            # Azure Speech configuration
            if self.asr_config.get("azure_speech", {}).get("enabled", False):
                try:
                    from .asr_integrations.azure_speech_client import AzureSpeechASRClient
                    self.asr_services["azure"] = AzureSpeechASRClient(
                        subscription_key=self.asr_config["azure_speech"].get("subscription_key"),
                        region=self.asr_config["azure_speech"].get("region"),
                        config=self.asr_config["azure_speech"]
                    )
                    logger.info("Azure Speech ASR service initialized")
                except ImportError:
                    logger.warning("Azure Speech client not available")
            
            # Google Speech-to-Text configuration
            if self.asr_config.get("google_stt", {}).get("enabled", False):
                try:
                    from .asr_integrations.google_stt_client import GoogleSTTClient
                    self.asr_services["google"] = GoogleSTTClient(
                        credentials_path=self.asr_config["google_stt"].get("credentials_path"),
                        config=self.asr_config["google_stt"]
                    )
                    logger.info("Google Speech-to-Text service initialized")
                except ImportError:
                    logger.warning("Google STT client not available")
        else:
            self.asr_services = {}
            logger.info("External ASR services disabled")
    
    async def generate_audio(self, test_case: AudioTestCase) -> Tuple[bytes, float]:
        """
        Generate audio using the Kokoro TTS API
        
        Returns:
            Tuple of (audio_bytes, processing_time)
        """
        import aiohttp
        
        payload = {
            "model": "kokoro",
            "input": test_case.input_text,
            "voice": test_case.voice_model,
            "response_format": "wav",  # Use WAV for better analysis
            "speed": 1.0
        }
        
        start_time = time.perf_counter()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base_url}/v1/audio/speech",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.api_timeout)
            ) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    processing_time = time.perf_counter() - start_time
                    return audio_data, processing_time
                else:
                    error_text = await response.text()
                    raise Exception(f"TTS API error {response.status}: {error_text}")
    
    def analyze_audio_properties(self, audio_data: bytes) -> Dict[str, float]:
        """
        Analyze basic audio properties (duration, spectral quality, etc.)
        """
        try:
            # Check if audio_data looks like valid audio
            if len(audio_data) < 44:  # Minimum WAV header size
                logger.warning("Audio data too small to be valid WAV file")
                return {"duration": 0.0, "sample_rate": 22050, "frames": 0}

            # Check for WAV header
            if not audio_data.startswith(b'RIFF'):
                logger.warning("Audio data does not appear to be WAV format")
                # Estimate duration based on data size (fallback)
                estimated_duration = len(audio_data) / (22050 * 2)  # Assume 22kHz, 16-bit
                return {
                    "duration": estimated_duration,
                    "sample_rate": 22050,
                    "frames": int(estimated_duration * 22050)
                }

            # Save audio to temporary file for analysis
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            # Analyze audio properties
            with wave.open(temp_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / sample_rate if sample_rate > 0 else 0.0

                # Basic audio analysis
                audio_properties = {
                    "duration": duration,
                    "sample_rate": sample_rate,
                    "frames": frames,
                    "channels": wav_file.getnchannels(),
                    "sample_width": wav_file.getsampwidth()
                }

            # Clean up temporary file
            Path(temp_path).unlink()

            return audio_properties

        except Exception as e:
            logger.error(f"Error analyzing audio properties: {e}")
            # Return reasonable defaults
            return {
                "duration": len(audio_data) / (22050 * 2),  # Estimate
                "sample_rate": 22050,
                "frames": len(audio_data) // 2
            }
    
    async def transcribe_audio(self, audio_data: bytes, service: str = "auto") -> Tuple[str, float]:
        """
        Transcribe audio using external ASR services
        
        Returns:
            Tuple of (transcription, confidence_score)
        """
        if not self.enable_external_asr or not self.asr_services:
            # Fallback: return empty transcription
            logger.warning("External ASR not available, skipping transcription")
            return "", 0.0
        
        # Select ASR service
        if service == "auto":
            # Use the first available service
            service = next(iter(self.asr_services.keys()))
        
        if service not in self.asr_services:
            raise ValueError(f"ASR service '{service}' not available")
        
        try:
            asr_client = self.asr_services[service]
            transcription, confidence = await asr_client.transcribe(audio_data)
            return transcription, confidence
        except Exception as e:
            logger.error(f"Error transcribing audio with {service}: {e}")
            return "", 0.0
    
    def calculate_wer(self, reference: str, hypothesis: str) -> float:
        """
        Calculate Word Error Rate between reference and hypothesis text
        """
        # Simple WER calculation (can be enhanced with more sophisticated algorithms)
        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()
        
        if not ref_words:
            return 0.0 if not hyp_words else 1.0
        
        # Simple edit distance calculation
        d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
        
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
        
        return d[len(ref_words)][len(hyp_words)] / len(ref_words)

    def predict_mos_score(self, audio_data: bytes, text: str) -> float:
        """
        Predict Mean Opinion Score using heuristic analysis
        (Can be enhanced with pre-trained MOS prediction models)
        """
        try:
            audio_props = self.analyze_audio_properties(audio_data)
            duration = audio_props.get("duration", 0)

            # Heuristic MOS prediction based on audio properties
            base_score = 4.0  # Start with good quality assumption

            # Adjust based on duration vs text length
            words = len(text.split())
            if duration > 0:
                speaking_rate = (words * 60) / duration  # words per minute

                # Optimal speaking rate is around 150-180 WPM
                if 120 <= speaking_rate <= 200:
                    rate_score = 1.0
                elif 100 <= speaking_rate <= 250:
                    rate_score = 0.8
                else:
                    rate_score = 0.6

                base_score *= rate_score

            # Adjust based on audio quality indicators
            sample_rate = audio_props.get("sample_rate", 0)
            if sample_rate >= 22050:
                base_score *= 1.0  # Good sample rate
            elif sample_rate >= 16000:
                base_score *= 0.9  # Acceptable sample rate
            else:
                base_score *= 0.7  # Low sample rate

            # Ensure score is within valid MOS range (1-5)
            return max(1.0, min(5.0, base_score))

        except Exception as e:
            logger.error(f"Error predicting MOS score: {e}")
            return 3.0  # Default neutral score

    def analyze_pronunciation_accuracy(self, test_case: AudioTestCase, transcription: str) -> float:
        """
        Analyze pronunciation accuracy based on expected pronunciations
        """
        if not test_case.expected_pronunciations:
            return 1.0  # No specific expectations

        accuracy_scores = []
        transcription_lower = transcription.lower()

        for symbol, expected_pronunciation in test_case.expected_pronunciations.items():
            if symbol in test_case.input_text:
                # Check if the expected pronunciation appears in transcription
                if expected_pronunciation.lower() in transcription_lower:
                    accuracy_scores.append(1.0)
                else:
                    accuracy_scores.append(0.0)
                    logger.warning(f"Expected pronunciation '{expected_pronunciation}' for '{symbol}' not found in transcription")

        return statistics.mean(accuracy_scores) if accuracy_scores else 1.0

    def analyze_symbol_processing_accuracy(self, test_case: AudioTestCase, transcription: str) -> float:
        """
        Analyze symbol processing accuracy for our eSpeak integration improvements
        """
        if not test_case.expected_symbols:
            return 1.0  # No specific symbol expectations

        accuracy_scores = []
        transcription_lower = transcription.lower()

        # Check for specific symbol processing improvements
        symbol_mappings = {
            "?": "question mark",
            "*": "asterisk",
            "&": "and",
            "@": "at",
            "%": "percent",
            "$": "dollar"
        }

        for symbol in test_case.expected_symbols:
            if symbol in test_case.input_text:
                expected_word = symbol_mappings.get(symbol, symbol)
                if expected_word in transcription_lower:
                    accuracy_scores.append(1.0)
                else:
                    accuracy_scores.append(0.0)
                    logger.warning(f"Symbol '{symbol}' not properly processed - expected '{expected_word}' in transcription")

        return statistics.mean(accuracy_scores) if accuracy_scores else 1.0

    async def test_single_case(self, test_case: AudioTestCase) -> AudioQualityMetrics:
        """
        Test a single audio quality test case
        """
        logger.info(f"Testing case: {test_case.test_id} - {test_case.description}")

        try:
            # Generate audio
            audio_data, processing_time = await self.generate_audio(test_case)

            # Analyze audio properties
            audio_props = self.analyze_audio_properties(audio_data)
            duration = audio_props.get("duration", 0)

            # Calculate RTF
            rtf = processing_time / duration if duration > 0 else float('inf')

            # Transcribe audio (if external ASR is available)
            transcription = ""
            confidence_score = 0.0
            wer = 0.0

            if self.enable_external_asr and self.asr_services:
                transcription, confidence_score = await self.transcribe_audio(audio_data)
                wer = self.calculate_wer(test_case.expected_transcription, transcription)

            # Predict MOS score
            mos_prediction = self.predict_mos_score(audio_data, test_case.input_text)

            # Analyze pronunciation accuracy
            pronunciation_accuracy = self.analyze_pronunciation_accuracy(test_case, transcription)

            # Analyze symbol processing accuracy
            symbol_processing_accuracy = self.analyze_symbol_processing_accuracy(test_case, transcription)

            # Calculate prosody score (heuristic based on speaking rate and duration)
            words = len(test_case.input_text.split())
            speaking_rate = (words * 60) / duration if duration > 0 else 0
            prosody_score = 1.0 if 120 <= speaking_rate <= 200 else 0.7

            # Create metrics object
            metrics = AudioQualityMetrics(
                wer=wer,
                mos_prediction=mos_prediction,
                prosody_score=prosody_score,
                pronunciation_accuracy=pronunciation_accuracy,
                processing_time=processing_time,
                audio_duration=duration,
                rtf=rtf,
                confidence_score=confidence_score,
                speaking_rate=speaking_rate,
                symbol_processing_accuracy=symbol_processing_accuracy,
                voice_model=test_case.voice_model,
                text_length=len(test_case.input_text),
                test_category=test_case.test_category
            )

            logger.info(f"Test completed: {test_case.test_id} - MOS: {mos_prediction:.2f}, WER: {wer:.3f}, RTF: {rtf:.3f}")
            return metrics

        except Exception as e:
            logger.error(f"Error testing case {test_case.test_id}: {e}")
            # Return default metrics indicating failure
            return AudioQualityMetrics(
                wer=1.0,  # Maximum error
                mos_prediction=1.0,  # Minimum quality
                prosody_score=0.0,
                pronunciation_accuracy=0.0,
                processing_time=float('inf'),
                audio_duration=0.0,
                rtf=float('inf'),
                confidence_score=0.0,
                voice_model=test_case.voice_model,
                text_length=len(test_case.input_text),
                test_category=test_case.test_category
            )

    async def run_test_suite(self, test_cases: List[AudioTestCase]) -> Dict[str, Any]:
        """
        Run a complete test suite with multiple test cases
        """
        logger.info(f"Starting audio quality test suite with {len(test_cases)} test cases")
        start_time = time.perf_counter()

        # Run tests concurrently with limited concurrency
        semaphore = asyncio.Semaphore(self.max_concurrent_tests)

        async def run_with_semaphore(test_case):
            async with semaphore:
                return await self.test_single_case(test_case)

        # Execute all tests
        tasks = [run_with_semaphore(test_case) for test_case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        test_results = []
        failed_tests = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Test case {test_cases[i].test_id} failed with exception: {result}")
                failed_tests.append(test_cases[i].test_id)
            else:
                test_results.append((test_cases[i], result))

        # Store results
        self.test_results.extend(test_results)

        # Calculate summary statistics
        total_time = time.perf_counter() - start_time
        summary = self._calculate_test_summary(test_results, failed_tests, total_time)

        logger.info(f"Test suite completed in {total_time:.2f}s - {len(test_results)} passed, {len(failed_tests)} failed")
        return summary

    def _calculate_test_summary(self, test_results: List[Tuple[AudioTestCase, AudioQualityMetrics]],
                               failed_tests: List[str], total_time: float) -> Dict[str, Any]:
        """
        Calculate summary statistics for test results
        """
        if not test_results:
            return {
                "total_tests": len(failed_tests),
                "passed_tests": 0,
                "failed_tests": len(failed_tests),
                "success_rate": 0.0,
                "total_time": total_time,
                "average_metrics": {},
                "quality_assessment": "FAILED"
            }

        # Extract metrics
        metrics_list = [metrics for _, metrics in test_results]

        # Calculate averages
        avg_metrics = {
            "wer": statistics.mean([m.wer for m in metrics_list]),
            "mos_prediction": statistics.mean([m.mos_prediction for m in metrics_list]),
            "prosody_score": statistics.mean([m.prosody_score for m in metrics_list]),
            "pronunciation_accuracy": statistics.mean([m.pronunciation_accuracy for m in metrics_list]),
            "rtf": statistics.mean([m.rtf for m in metrics_list if m.rtf != float('inf')]),
            "processing_time": statistics.mean([m.processing_time for m in metrics_list]),
            "symbol_processing_accuracy": statistics.mean([m.symbol_processing_accuracy for m in metrics_list])
        }

        # Assess overall quality
        quality_assessment = self._assess_overall_quality(avg_metrics)

        # Calculate pass/fail based on thresholds
        passed_tests = sum(1 for _, metrics in test_results if self._meets_quality_thresholds(metrics))

        return {
            "total_tests": len(test_results) + len(failed_tests),
            "passed_tests": passed_tests,
            "failed_tests": len(test_results) - passed_tests + len(failed_tests),
            "success_rate": passed_tests / (len(test_results) + len(failed_tests)),
            "total_time": total_time,
            "average_metrics": avg_metrics,
            "quality_assessment": quality_assessment,
            "failed_test_ids": failed_tests,
            "detailed_results": test_results
        }

    def _meets_quality_thresholds(self, metrics: AudioQualityMetrics) -> bool:
        """
        Check if metrics meet quality thresholds
        """
        thresholds = self.quality_thresholds

        return (
            metrics.mos_prediction >= thresholds.get("min_mos_score", 3.0) and
            metrics.wer <= thresholds.get("max_wer", 0.1) and
            metrics.pronunciation_accuracy >= thresholds.get("min_pronunciation_accuracy", 0.9) and
            metrics.rtf <= thresholds.get("max_rtf", 0.25) and
            metrics.prosody_score >= thresholds.get("min_prosody_score", 0.7)
        )

    def _assess_overall_quality(self, avg_metrics: Dict[str, float]) -> str:
        """
        Assess overall quality based on average metrics
        """
        score = 0
        total_checks = 0

        # MOS score assessment
        if avg_metrics.get("mos_prediction", 0) >= 4.0:
            score += 2
        elif avg_metrics.get("mos_prediction", 0) >= 3.5:
            score += 1
        total_checks += 2

        # WER assessment
        if avg_metrics.get("wer", 1.0) <= 0.05:
            score += 2
        elif avg_metrics.get("wer", 1.0) <= 0.1:
            score += 1
        total_checks += 2

        # RTF assessment
        if avg_metrics.get("rtf", float('inf')) <= 0.15:
            score += 2
        elif avg_metrics.get("rtf", float('inf')) <= 0.25:
            score += 1
        total_checks += 2

        # Pronunciation accuracy assessment
        if avg_metrics.get("pronunciation_accuracy", 0) >= 0.95:
            score += 2
        elif avg_metrics.get("pronunciation_accuracy", 0) >= 0.9:
            score += 1
        total_checks += 2

        # Calculate percentage
        percentage = (score / total_checks) * 100 if total_checks > 0 else 0

        if percentage >= 80:
            return "EXCELLENT"
        elif percentage >= 60:
            return "GOOD"
        elif percentage >= 40:
            return "ACCEPTABLE"
        else:
            return "POOR"

    def generate_report(self, summary: Dict[str, Any], output_path: Optional[Path] = None) -> str:
        """
        Generate a comprehensive test report
        """
        report_lines = [
            "# Audio Quality Testing Report",
            "=" * 50,
            "",
            f"**Test Summary:**",
            f"- Total Tests: {summary['total_tests']}",
            f"- Passed: {summary['passed_tests']}",
            f"- Failed: {summary['failed_tests']}",
            f"- Success Rate: {summary['success_rate']:.1%}",
            f"- Total Time: {summary['total_time']:.2f}s",
            f"- Quality Assessment: {summary['quality_assessment']}",
            "",
            "**Average Metrics:**"
        ]

        avg_metrics = summary.get("average_metrics", {})
        for metric, value in avg_metrics.items():
            if isinstance(value, float):
                report_lines.append(f"- {metric.replace('_', ' ').title()}: {value:.3f}")

        report_lines.extend([
            "",
            "**Quality Thresholds:**"
        ])

        for threshold, value in self.quality_thresholds.items():
            report_lines.append(f"- {threshold.replace('_', ' ').title()}: {value}")

        if summary.get("failed_test_ids"):
            report_lines.extend([
                "",
                "**Failed Tests:**"
            ])
            for test_id in summary["failed_test_ids"]:
                report_lines.append(f"- {test_id}")

        report_content = "\n".join(report_lines)

        if output_path:
            output_path.write_text(report_content)
            logger.info(f"Report saved to: {output_path}")

        return report_content

    def save_baseline_metrics(self, summary: Dict[str, Any], baseline_path: Optional[Path] = None):
        """
        Save current metrics as baseline for regression testing
        """
        if baseline_path is None:
            baseline_path = self.cache_dir / "baseline_metrics.json"

        baseline_data = {
            "timestamp": time.time(),
            "average_metrics": summary.get("average_metrics", {}),
            "quality_assessment": summary.get("quality_assessment", ""),
            "success_rate": summary.get("success_rate", 0.0),
            "quality_thresholds": self.quality_thresholds
        }

        with open(baseline_path, 'w') as f:
            json.dump(baseline_data, f, indent=2)

        logger.info(f"Baseline metrics saved to: {baseline_path}")

    def load_baseline_metrics(self, baseline_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
        """
        Load baseline metrics for regression comparison
        """
        if baseline_path is None:
            baseline_path = self.cache_dir / "baseline_metrics.json"

        if not baseline_path.exists():
            logger.warning(f"Baseline metrics file not found: {baseline_path}")
            return None

        try:
            with open(baseline_path, 'r') as f:
                baseline_data = json.load(f)

            logger.info(f"Baseline metrics loaded from: {baseline_path}")
            return baseline_data
        except Exception as e:
            logger.error(f"Error loading baseline metrics: {e}")
            return None
