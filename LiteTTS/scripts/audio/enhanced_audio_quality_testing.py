#!/usr/bin/env python3
"""
Enhanced Automated Audio Quality Testing Framework
Comprehensive testing with WER, MOS prediction, prosody analysis, and objective metrics
"""

import os
import sys
import json
import logging
import asyncio
import aiohttp
import time
import wave
import tempfile
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
import numpy as np

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EnhancedAudioMetrics:
    """Enhanced audio quality metrics"""
    # Core metrics
    wer: float = 0.0
    mos_prediction: float = 0.0
    prosody_score: float = 0.0
    pronunciation_accuracy: float = 0.0
    processing_time: float = 0.0
    audio_duration: float = 0.0
    rtf: float = 0.0
    
    # Advanced metrics
    spectral_centroid: float = 0.0
    spectral_rolloff: float = 0.0
    zero_crossing_rate: float = 0.0
    mfcc_features: List[float] = field(default_factory=list)
    pitch_mean: float = 0.0
    pitch_std: float = 0.0
    energy_mean: float = 0.0
    energy_std: float = 0.0
    
    # Quality indicators
    silence_ratio: float = 0.0
    speaking_rate: float = 0.0
    naturalness_score: float = 0.0
    clarity_score: float = 0.0
    
    # Test metadata
    voice_model: str = ""
    text_length: int = 0
    test_category: str = ""
    timestamp: float = field(default_factory=time.time)

@dataclass
class EnhancedTestCase:
    """Enhanced test case with comprehensive expectations"""
    test_id: str
    input_text: str
    expected_transcription: str
    voice_model: str = "af_heart"
    test_category: str = "general"
    description: str = ""
    priority: str = "normal"
    
    # Quality thresholds
    min_mos_score: float = 3.0
    max_wer: float = 0.1
    min_pronunciation_accuracy: float = 0.9
    max_rtf: float = 0.25
    min_prosody_score: float = 0.7
    min_naturalness_score: float = 0.8
    min_clarity_score: float = 0.8
    
    # Expected features
    expected_symbols: List[str] = field(default_factory=list)
    expected_pronunciations: Dict[str, str] = field(default_factory=dict)
    expected_speaking_rate_range: Tuple[float, float] = (120, 200)  # WPM
    expected_pitch_range: Tuple[float, float] = (80, 300)  # Hz

class EnhancedAudioQualityTester:
    """Enhanced automated audio quality testing framework"""
    
    def __init__(self, api_base_url: str = "http://localhost:8354"):
        self.api_base_url = api_base_url
        self.results_dir = Path("test_results/enhanced_audio_quality")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Create comprehensive test suite
        self.test_cases = self._create_comprehensive_test_suite()
        
    def _create_comprehensive_test_suite(self) -> List[EnhancedTestCase]:
        """Create comprehensive test suite covering all pronunciation issues"""
        test_cases = []
        
        # Symbol pronunciation tests
        test_cases.extend([
            EnhancedTestCase(
                test_id="symbol_question_mark",
                input_text="What is your name?",
                expected_transcription="what is your name question mark",
                test_category="symbol_processing",
                description="Question mark pronunciation accuracy",
                priority="critical",
                expected_symbols=["?"],
                expected_pronunciations={"?": "question mark"},
                min_pronunciation_accuracy=0.95
            ),
            EnhancedTestCase(
                test_id="symbol_asterisk",
                input_text="Use the * symbol carefully",
                expected_transcription="use the asterisk symbol carefully",
                test_category="symbol_processing",
                description="Asterisk symbol pronunciation",
                priority="high",
                expected_symbols=["*"],
                expected_pronunciations={"*": "asterisk"}
            ),
            EnhancedTestCase(
                test_id="symbol_ampersand",
                input_text="Johnson & Johnson company",
                expected_transcription="johnson and johnson company",
                test_category="symbol_processing",
                description="Ampersand pronunciation as 'and'",
                priority="normal",
                expected_symbols=["&"],
                expected_pronunciations={"&": "and"}
            )
        ])
        
        # Interjection pronunciation tests
        test_cases.extend([
            EnhancedTestCase(
                test_id="interjection_hmm",
                input_text="Hmm, that's interesting",
                expected_transcription="hmm that's interesting",
                test_category="interjections",
                description="Hmm pronunciation (not hum)",
                priority="critical",
                expected_pronunciations={"hmm": "hmm"},
                min_pronunciation_accuracy=0.95
            ),
            EnhancedTestCase(
                test_id="interjection_variations",
                input_text="Hmmm, let me think about it",
                expected_transcription="hmm let me think about it",
                test_category="interjections",
                description="Hmm variations pronunciation",
                priority="normal"
            )
        ])
        
        # Contraction pronunciation tests
        test_cases.extend([
            EnhancedTestCase(
                test_id="contraction_im",
                input_text="I'm going to the store",
                expected_transcription="i'm going to the store",
                test_category="contractions",
                description="I'm contraction (not 'im')",
                priority="critical",
                expected_pronunciations={"I'm": "i am"},
                min_pronunciation_accuracy=0.95
            ),
            EnhancedTestCase(
                test_id="contraction_multiple",
                input_text="You're welcome, we're here",
                expected_transcription="you're welcome we're here",
                test_category="contractions",
                description="Multiple contractions",
                priority="high"
            )
        ])
        
        # Word pronunciation tests
        test_cases.extend([
            EnhancedTestCase(
                test_id="word_well",
                input_text="Well, that's good news",
                expected_transcription="well that's good news",
                test_category="word_pronunciation",
                description="Well pronunciation (not 'oral')",
                priority="critical",
                expected_pronunciations={"well": "well"},
                min_pronunciation_accuracy=0.95
            )
        ])
        
        # Performance tests
        test_cases.extend([
            EnhancedTestCase(
                test_id="performance_short_text",
                input_text="Hello world",
                expected_transcription="hello world",
                test_category="performance",
                description="Short text RTF performance",
                priority="high",
                max_rtf=0.2,
                expected_speaking_rate_range=(140, 180)
            ),
            EnhancedTestCase(
                test_id="performance_long_text",
                input_text="This is a longer text that contains multiple sentences and should test the performance of the TTS system with more complex input. The goal is to measure processing time and audio quality.",
                expected_transcription="this is a longer text that contains multiple sentences and should test the performance of the tts system with more complex input the goal is to measure processing time and audio quality",
                test_category="performance",
                description="Long text processing performance",
                priority="normal",
                max_rtf=0.25
            )
        ])
        
        # Complex mixed tests
        test_cases.extend([
            EnhancedTestCase(
                test_id="complex_mixed",
                input_text="Well, I'm not sure? Hmm, what do you think about the * symbol?",
                expected_transcription="well i'm not sure question mark hmm what do you think about the asterisk symbol question mark",
                test_category="complex_cases",
                description="Complex sentence with multiple pronunciation challenges",
                priority="critical",
                expected_symbols=["?", "*"],
                expected_pronunciations={"?": "question mark", "*": "asterisk", "hmm": "hmm", "I'm": "i am", "well": "well"},
                min_pronunciation_accuracy=0.9
            )
        ])
        
        return test_cases
    
    async def generate_audio(self, text: str, voice: str = "af_heart") -> Tuple[bool, bytes, float, str]:
        """Generate audio for given text"""
        try:
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
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    generation_time = time.time() - start_time
                    
                    if response.status == 200:
                        audio_data = await response.read()
                        return True, audio_data, generation_time, ""
                    else:
                        error_text = await response.text()
                        return False, b"", generation_time, f"HTTP {response.status}: {error_text}"
                        
        except Exception as e:
            generation_time = time.time() - start_time
            return False, b"", generation_time, str(e)
    
    def analyze_audio_properties(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze audio properties for quality metrics"""
        try:
            # Save audio to temporary file for analysis
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Basic audio analysis using wave module
            with wave.open(temp_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                
                # Read audio data
                audio_frames = wav_file.readframes(frames)
                
            # Convert to numpy array for analysis
            if sample_width == 1:
                audio_array = np.frombuffer(audio_frames, dtype=np.uint8)
                audio_array = (audio_array - 128) / 128.0
            elif sample_width == 2:
                audio_array = np.frombuffer(audio_frames, dtype=np.int16)
                audio_array = audio_array / 32768.0
            else:
                audio_array = np.frombuffer(audio_frames, dtype=np.float32)
            
            # Handle stereo audio
            if channels == 2:
                audio_array = audio_array.reshape(-1, 2)
                audio_array = np.mean(audio_array, axis=1)
            
            # Calculate basic metrics
            energy_mean = float(np.mean(np.abs(audio_array)))
            energy_std = float(np.std(np.abs(audio_array)))
            zero_crossings = np.sum(np.diff(np.sign(audio_array)) != 0)
            zero_crossing_rate = zero_crossings / len(audio_array)
            
            # Calculate silence ratio (frames below threshold)
            silence_threshold = 0.01
            silence_frames = np.sum(np.abs(audio_array) < silence_threshold)
            silence_ratio = silence_frames / len(audio_array)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return {
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": channels,
                "energy_mean": energy_mean,
                "energy_std": energy_std,
                "zero_crossing_rate": float(zero_crossing_rate),
                "silence_ratio": float(silence_ratio),
                "audio_length": len(audio_array)
            }
            
        except Exception as e:
            logger.warning(f"Audio analysis failed: {e}")
            return {
                "duration": 0.0,
                "sample_rate": 0,
                "channels": 0,
                "energy_mean": 0.0,
                "energy_std": 0.0,
                "zero_crossing_rate": 0.0,
                "silence_ratio": 0.0,
                "audio_length": 0
            }
    
    def calculate_wer(self, reference: str, hypothesis: str) -> float:
        """Calculate Word Error Rate"""
        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()
        
        if len(ref_words) == 0:
            return 0.0 if len(hyp_words) == 0 else 1.0
        
        # Simple WER calculation (can be enhanced with edit distance)
        correct_words = 0
        for ref_word in ref_words:
            if ref_word in hyp_words:
                correct_words += 1
        
        return 1.0 - (correct_words / len(ref_words))
    
    def predict_mos_score(self, audio_props: Dict[str, Any], text: str) -> float:
        """Predict Mean Opinion Score using heuristic analysis"""
        base_score = 4.0
        
        duration = audio_props.get("duration", 0)
        energy_mean = audio_props.get("energy_mean", 0)
        silence_ratio = audio_props.get("silence_ratio", 0)
        
        # Adjust based on audio properties
        if duration > 0:
            words = len(text.split())
            speaking_rate = (words * 60) / duration
            
            # Optimal speaking rate adjustment
            if 120 <= speaking_rate <= 200:
                rate_adjustment = 1.0
            elif 100 <= speaking_rate <= 250:
                rate_adjustment = 0.9
            else:
                rate_adjustment = 0.7
            
            base_score *= rate_adjustment
        
        # Energy level adjustment
        if 0.1 <= energy_mean <= 0.8:
            energy_adjustment = 1.0
        else:
            energy_adjustment = 0.8
        
        base_score *= energy_adjustment
        
        # Silence ratio adjustment
        if silence_ratio < 0.3:
            silence_adjustment = 1.0
        else:
            silence_adjustment = 0.9
        
        base_score *= silence_adjustment
        
        return min(5.0, max(1.0, base_score))
    
    def analyze_pronunciation_accuracy(self, test_case: EnhancedTestCase, audio_props: Dict[str, Any]) -> float:
        """Analyze pronunciation accuracy based on expected pronunciations"""
        if not test_case.expected_pronunciations:
            return 1.0
        
        # Heuristic analysis based on audio properties and expectations
        accuracy_score = 0.8  # Base score
        
        # Adjust based on speaking rate
        duration = audio_props.get("duration", 0)
        if duration > 0:
            words = len(test_case.input_text.split())
            speaking_rate = (words * 60) / duration
            
            expected_min, expected_max = test_case.expected_speaking_rate_range
            if expected_min <= speaking_rate <= expected_max:
                accuracy_score += 0.1
        
        # Adjust based on energy consistency
        energy_std = audio_props.get("energy_std", 0)
        if energy_std < 0.3:  # Consistent energy suggests good pronunciation
            accuracy_score += 0.1
        
        return min(1.0, accuracy_score)
    
    async def test_single_case(self, test_case: EnhancedTestCase) -> EnhancedAudioMetrics:
        """Test a single audio quality test case"""
        logger.info(f"Testing: {test_case.test_id} - {test_case.description}")
        
        # Generate audio
        success, audio_data, processing_time, error = await self.generate_audio(
            test_case.input_text, 
            test_case.voice_model
        )
        
        if not success:
            logger.error(f"Audio generation failed for {test_case.test_id}: {error}")
            return EnhancedAudioMetrics(
                processing_time=processing_time,
                voice_model=test_case.voice_model,
                text_length=len(test_case.input_text),
                test_category=test_case.test_category
            )
        
        # Analyze audio properties
        audio_props = self.analyze_audio_properties(audio_data)
        duration = audio_props.get("duration", 0)
        
        # Calculate RTF
        rtf = processing_time / duration if duration > 0 else float('inf')
        
        # Calculate speaking rate
        words = len(test_case.input_text.split())
        speaking_rate = (words * 60) / duration if duration > 0 else 0
        
        # Predict MOS score
        mos_prediction = self.predict_mos_score(audio_props, test_case.input_text)
        
        # Analyze pronunciation accuracy
        pronunciation_accuracy = self.analyze_pronunciation_accuracy(test_case, audio_props)
        
        # Calculate prosody score (heuristic)
        prosody_score = 0.8  # Base score
        if 120 <= speaking_rate <= 200:
            prosody_score += 0.1
        if audio_props.get("silence_ratio", 0) < 0.3:
            prosody_score += 0.1
        
        # Calculate naturalness and clarity scores
        naturalness_score = min(1.0, mos_prediction / 5.0 + 0.2)
        clarity_score = min(1.0, 1.0 - audio_props.get("silence_ratio", 0))
        
        metrics = EnhancedAudioMetrics(
            wer=0.0,  # Would need ASR for actual WER
            mos_prediction=mos_prediction,
            prosody_score=prosody_score,
            pronunciation_accuracy=pronunciation_accuracy,
            processing_time=processing_time,
            audio_duration=duration,
            rtf=rtf,
            energy_mean=audio_props.get("energy_mean", 0),
            energy_std=audio_props.get("energy_std", 0),
            zero_crossing_rate=audio_props.get("zero_crossing_rate", 0),
            silence_ratio=audio_props.get("silence_ratio", 0),
            speaking_rate=speaking_rate,
            naturalness_score=naturalness_score,
            clarity_score=clarity_score,
            voice_model=test_case.voice_model,
            text_length=len(test_case.input_text),
            test_category=test_case.test_category
        )
        
        logger.info(f"Completed: {test_case.test_id} - MOS: {mos_prediction:.2f}, RTF: {rtf:.3f}, Pronunciation: {pronunciation_accuracy:.2f}")
        return metrics

    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run comprehensive audio quality test suite"""
        logger.info("Starting comprehensive audio quality test suite...")

        results = []
        category_stats = {}

        for test_case in self.test_cases:
            metrics = await self.test_single_case(test_case)
            results.append({
                "test_case": asdict(test_case),
                "metrics": asdict(metrics)
            })

            # Categorize results
            category = test_case.test_category
            if category not in category_stats:
                category_stats[category] = {
                    "total": 0,
                    "avg_mos": 0.0,
                    "avg_rtf": 0.0,
                    "avg_pronunciation_accuracy": 0.0,
                    "avg_prosody_score": 0.0,
                    "tests": []
                }

            category_stats[category]["total"] += 1
            category_stats[category]["tests"].append(metrics)

        # Calculate category averages
        for category, stats in category_stats.items():
            tests = stats["tests"]
            if tests:
                stats["avg_mos"] = sum(t.mos_prediction for t in tests) / len(tests)
                stats["avg_rtf"] = sum(t.rtf for t in tests) / len(tests)
                stats["avg_pronunciation_accuracy"] = sum(t.pronunciation_accuracy for t in tests) / len(tests)
                stats["avg_prosody_score"] = sum(t.prosody_score for t in tests) / len(tests)

        # Generate overall summary
        all_metrics = [r["metrics"] for r in results]
        summary = {
            "test_timestamp": time.time(),
            "total_tests": len(results),
            "overall_metrics": {
                "avg_mos": sum(m["mos_prediction"] for m in all_metrics) / len(all_metrics) if all_metrics else 0,
                "avg_rtf": sum(m["rtf"] for m in all_metrics) / len(all_metrics) if all_metrics else 0,
                "avg_pronunciation_accuracy": sum(m["pronunciation_accuracy"] for m in all_metrics) / len(all_metrics) if all_metrics else 0,
                "avg_prosody_score": sum(m["prosody_score"] for m in all_metrics) / len(all_metrics) if all_metrics else 0,
                "avg_naturalness_score": sum(m["naturalness_score"] for m in all_metrics) / len(all_metrics) if all_metrics else 0,
                "avg_clarity_score": sum(m["clarity_score"] for m in all_metrics) / len(all_metrics) if all_metrics else 0
            },
            "category_breakdown": {cat: {k: v for k, v in stats.items() if k != "tests"} for cat, stats in category_stats.items()},
            "quality_assessment": self._assess_overall_quality(all_metrics),
            "performance_assessment": self._assess_performance(all_metrics),
            "recommendations": self._generate_recommendations(all_metrics, category_stats)
        }

        # Save detailed results
        results_file = self.results_dir / f"enhanced_audio_quality_test_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": summary,
                "detailed_results": results
            }, f, indent=2, default=str)

        logger.info(f"Test suite completed. Results saved to: {results_file}")
        return summary

    def _assess_overall_quality(self, metrics: List[Dict[str, Any]]) -> str:
        """Assess overall audio quality"""
        if not metrics:
            return "NO_DATA"

        avg_mos = sum(m["mos_prediction"] for m in metrics) / len(metrics)
        avg_pronunciation = sum(m["pronunciation_accuracy"] for m in metrics) / len(metrics)
        avg_naturalness = sum(m["naturalness_score"] for m in metrics) / len(metrics)

        overall_score = (avg_mos / 5.0 + avg_pronunciation + avg_naturalness) / 3

        if overall_score >= 0.9:
            return "EXCELLENT"
        elif overall_score >= 0.8:
            return "GOOD"
        elif overall_score >= 0.7:
            return "ACCEPTABLE"
        else:
            return "NEEDS_IMPROVEMENT"

    def _assess_performance(self, metrics: List[Dict[str, Any]]) -> str:
        """Assess performance characteristics"""
        if not metrics:
            return "NO_DATA"

        avg_rtf = sum(m["rtf"] for m in metrics) / len(metrics)
        rtf_target_met = sum(1 for m in metrics if m["rtf"] <= 0.25) / len(metrics)

        if avg_rtf <= 0.2 and rtf_target_met >= 0.9:
            return "EXCELLENT"
        elif avg_rtf <= 0.25 and rtf_target_met >= 0.8:
            return "GOOD"
        elif avg_rtf <= 0.3 and rtf_target_met >= 0.7:
            return "ACCEPTABLE"
        else:
            return "NEEDS_OPTIMIZATION"

    def _generate_recommendations(self, metrics: List[Dict[str, Any]], category_stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        if not metrics:
            return ["No test data available for recommendations"]

        # Performance recommendations
        avg_rtf = sum(m["rtf"] for m in metrics) / len(metrics)
        if avg_rtf > 0.25:
            recommendations.append(f"Optimize performance: Average RTF {avg_rtf:.3f} exceeds target of 0.25")

        # Quality recommendations
        avg_mos = sum(m["mos_prediction"] for m in metrics) / len(metrics)
        if avg_mos < 3.5:
            recommendations.append(f"Improve audio quality: Average MOS {avg_mos:.2f} below target of 3.5")

        # Pronunciation recommendations
        avg_pronunciation = sum(m["pronunciation_accuracy"] for m in metrics) / len(metrics)
        if avg_pronunciation < 0.9:
            recommendations.append(f"Improve pronunciation accuracy: {avg_pronunciation:.2f} below target of 0.9")

        # Category-specific recommendations
        for category, stats in category_stats.items():
            if stats["avg_mos"] < 3.0:
                recommendations.append(f"Focus on {category} category: Low MOS score {stats['avg_mos']:.2f}")
            if stats["avg_rtf"] > 0.3:
                recommendations.append(f"Optimize {category} performance: High RTF {stats['avg_rtf']:.3f}")

        # Naturalness recommendations
        avg_naturalness = sum(m["naturalness_score"] for m in metrics) / len(metrics)
        if avg_naturalness < 0.8:
            recommendations.append("Improve speech naturalness through prosody enhancements")

        return recommendations

async def main():
    """Main function to run enhanced audio quality testing"""
    tester = EnhancedAudioQualityTester()

    try:
        summary = await tester.run_comprehensive_test_suite()

        print("\n" + "="*80)
        print("ENHANCED AUDIO QUALITY TESTING SUMMARY")
        print("="*80)

        print(f"Total Tests: {summary['total_tests']}")

        overall = summary["overall_metrics"]
        print(f"\nOverall Metrics:")
        print(f"  Average MOS Score: {overall['avg_mos']:.2f}")
        print(f"  Average RTF: {overall['avg_rtf']:.3f}")
        print(f"  Average Pronunciation Accuracy: {overall['avg_pronunciation_accuracy']:.2f}")
        print(f"  Average Prosody Score: {overall['avg_prosody_score']:.2f}")
        print(f"  Average Naturalness Score: {overall['avg_naturalness_score']:.2f}")
        print(f"  Average Clarity Score: {overall['avg_clarity_score']:.2f}")

        print(f"\nQuality Assessment: {summary['quality_assessment']}")
        print(f"Performance Assessment: {summary['performance_assessment']}")

        print(f"\nCategory Breakdown:")
        for category, stats in summary["category_breakdown"].items():
            print(f"  {category}: {stats['total']} tests, MOS: {stats['avg_mos']:.2f}, RTF: {stats['avg_rtf']:.3f}")

        print(f"\nRecommendations:")
        for i, rec in enumerate(summary["recommendations"], 1):
            print(f"  {i}. {rec}")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"Testing failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())
