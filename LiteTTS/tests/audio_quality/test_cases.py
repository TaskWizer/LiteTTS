#!/usr/bin/env python3
"""
Comprehensive Test Cases for Audio Quality Validation
Covers short/long text, special characters, numbers, and edge cases for both GGUF and ONNX models
"""

import json
import time
import logging
import requests
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from .framework import AudioQualityValidator, QualityThresholds, AudioQualityReport, TestResult

logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """Individual test case definition"""
    id: str
    name: str
    description: str
    input_text: str
    category: str
    priority: str
    expected_duration_range: Tuple[float, float]  # min, max in seconds
    special_requirements: Dict[str, Any]

class AudioQualityTestSuite:
    """Comprehensive test suite for audio quality validation"""
    
    def __init__(self, api_base_url: str = "http://localhost:8354", 
                 thresholds: Optional[QualityThresholds] = None):
        self.api_base_url = api_base_url.rstrip('/')
        self.validator = AudioQualityValidator(thresholds)
        self.test_cases = self._create_test_cases()
        self.results = []
        
    def _create_test_cases(self) -> List[TestCase]:
        """Create comprehensive test cases"""
        test_cases = []
        
        # Short text tests (RTF < 0.25 target)
        test_cases.extend([
            TestCase(
                id="short_001",
                name="Single Word",
                description="Test single word generation with minimal latency",
                input_text="Hello",
                category="short_text",
                priority="critical",
                expected_duration_range=(0.3, 0.8),
                special_requirements={"max_rtf": 0.25}
            ),
            TestCase(
                id="short_002", 
                name="Short Phrase",
                description="Test short phrase under 20 characters",
                input_text="Good morning!",
                category="short_text",
                priority="critical",
                expected_duration_range=(0.8, 1.5),
                special_requirements={"max_rtf": 0.25}
            ),
            TestCase(
                id="short_003",
                name="Question Mark",
                description="Test question mark pronunciation (should be 'question mark' not 'up arrow')",
                input_text="What?",
                category="short_text",
                priority="critical",
                expected_duration_range=(0.4, 1.0),
                special_requirements={"pronunciation_check": "question mark"}
            ),
            TestCase(
                id="short_004",
                name="Asterisk Symbol",
                description="Test asterisk pronunciation improvements",
                input_text="Note*",
                category="short_text", 
                priority="high",
                expected_duration_range=(0.4, 1.0),
                special_requirements={"pronunciation_check": "asterisk"}
            )
        ])
        
        # Long text tests
        test_cases.extend([
            TestCase(
                id="long_001",
                name="Paragraph Text",
                description="Test long paragraph generation",
                input_text="The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet and is commonly used for testing text-to-speech systems. It provides a good balance of phonemes and demonstrates the system's ability to handle connected speech with natural prosody and rhythm.",
                category="long_text",
                priority="high",
                expected_duration_range=(8.0, 15.0),
                special_requirements={"min_prosody_score": 0.7}
            ),
            TestCase(
                id="long_002",
                name="Technical Content",
                description="Test technical terminology and complex sentences",
                input_text="The implementation utilizes advanced neural network architectures with transformer-based attention mechanisms to achieve state-of-the-art performance in text-to-speech synthesis, incorporating phonetic preprocessing and prosodic modeling for enhanced naturalness.",
                category="long_text",
                priority="medium",
                expected_duration_range=(10.0, 18.0),
                special_requirements={"min_pronunciation_accuracy": 0.85}
            )
        ])
        
        # Special characters and symbols
        test_cases.extend([
            TestCase(
                id="symbols_001",
                name="Currency and Numbers",
                description="Test currency symbols and number pronunciation",
                input_text="The price is $29.99 for 3 items.",
                category="symbols",
                priority="high",
                expected_duration_range=(2.0, 4.0),
                special_requirements={"pronunciation_check": "twenty nine ninety nine"}
            ),
            TestCase(
                id="symbols_002",
                name="Punctuation Variety",
                description="Test various punctuation marks",
                input_text="Hello! How are you? I'm fine... Thanks & goodbye.",
                category="symbols",
                priority="medium",
                expected_duration_range=(3.0, 6.0),
                special_requirements={"prosody_check": True}
            ),
            TestCase(
                id="symbols_003",
                name="Email and URL",
                description="Test email and URL pronunciation",
                input_text="Contact us at info@example.com or visit https://example.com",
                category="symbols",
                priority="medium",
                expected_duration_range=(4.0, 8.0),
                special_requirements={"pronunciation_check": "at example dot com"}
            )
        ])
        
        # Contractions and natural speech
        test_cases.extend([
            TestCase(
                id="contractions_001",
                name="Common Contractions",
                description="Test natural contraction pronunciation",
                input_text="I can't believe it's working! We're almost done.",
                category="contractions",
                priority="high",
                expected_duration_range=(2.5, 5.0),
                special_requirements={"pronunciation_check": "cannot", "avoid_pronunciation": "caaant"}
            ),
            TestCase(
                id="contractions_002",
                name="Negative Contractions",
                description="Test negative contractions like wasn't, didn't",
                input_text="It wasn't easy, but we didn't give up.",
                category="contractions",
                priority="high",
                expected_duration_range=(2.0, 4.0),
                special_requirements={"pronunciation_check": "was not", "avoid_pronunciation": "waaasant"}
            )
        ])
        
        # Numbers and sequences
        test_cases.extend([
            TestCase(
                id="numbers_001",
                name="Individual Digits",
                description="Test individual digit pronunciation with pauses",
                input_text="1 2 3",
                category="numbers",
                priority="medium",
                expected_duration_range=(1.5, 3.0),
                special_requirements={"pronunciation_check": "one...two...three", "pause_detection": True}
            ),
            TestCase(
                id="numbers_002",
                name="Large Numbers",
                description="Test large number pronunciation",
                input_text="The year 2024 was significant.",
                category="numbers",
                priority="medium",
                expected_duration_range=(2.0, 4.0),
                special_requirements={"pronunciation_check": "twenty twenty four"}
            )
        ])
        
        # Emotional and prosodic tests
        test_cases.extend([
            TestCase(
                id="prosody_001",
                name="Question Intonation",
                description="Test question intonation patterns",
                input_text="Are you coming to the party tonight?",
                category="prosody",
                priority="high",
                expected_duration_range=(2.0, 4.0),
                special_requirements={"intonation_check": "rising", "min_prosody_score": 0.8}
            ),
            TestCase(
                id="prosody_002",
                name="Exclamation Emphasis",
                description="Test exclamation emphasis and emotion",
                input_text="Wow! That's absolutely amazing!",
                category="prosody",
                priority="high",
                expected_duration_range=(1.5, 3.0),
                special_requirements={"emphasis_check": True, "min_prosody_score": 0.8}
            )
        ])
        
        # Edge cases and stress tests
        test_cases.extend([
            TestCase(
                id="edge_001",
                name="Empty-like Input",
                description="Test minimal input handling",
                input_text=".",
                category="edge_cases",
                priority="low",
                expected_duration_range=(0.1, 0.5),
                special_requirements={"error_handling": True}
            ),
            TestCase(
                id="edge_002",
                name="Mixed Languages",
                description="Test mixed language content",
                input_text="Hello, bonjour, hola world!",
                category="edge_cases",
                priority="low",
                expected_duration_range=(2.0, 4.0),
                special_requirements={"pronunciation_tolerance": 0.7}
            ),
            TestCase(
                id="edge_003",
                name="Special Unicode",
                description="Test unicode and special characters",
                input_text="Café résumé naïve 🎵",
                category="edge_cases",
                priority="low",
                expected_duration_range=(1.5, 3.0),
                special_requirements={"unicode_handling": True}
            )
        ])
        
        return test_cases
    
    def run_test_case(self, test_case: TestCase, model_type: str, voice_name: str = "af_heart") -> AudioQualityReport:
        """Run a single test case"""
        logger.info(f"Running test case {test_case.id}: {test_case.name}")
        
        try:
            # Generate audio via API
            start_time = time.time()
            audio_file = self._generate_audio_via_api(test_case.input_text, voice_name)
            generation_time = (time.time() - start_time) * 1000  # ms
            
            if not audio_file:
                raise Exception("Failed to generate audio via API")
            
            # Calculate RTF
            audio_duration = self._get_audio_duration(audio_file)
            rtf = generation_time / 1000 / audio_duration if audio_duration > 0 else float('inf')
            
            # Validate audio quality
            report = self.validator.validate_audio(
                audio_file, test_case.input_text, model_type, voice_name, test_case.id
            )
            
            # Update performance metrics
            report.performance_metrics.rtf = rtf
            report.performance_metrics.generation_time_ms = generation_time
            
            # Apply test-specific validations
            self._apply_special_requirements(report, test_case)
            
            # Clean up temporary file
            try:
                audio_file.unlink()
            except Exception:
                pass
                
            return report
            
        except Exception as e:
            logger.error(f"Test case {test_case.id} failed: {e}")
            return self.validator._create_error_report(
                test_case.id, test_case.input_text, model_type, voice_name, str(e)
            )
    
    def _generate_audio_via_api(self, text: str, voice: str) -> Optional[Path]:
        """Generate audio via TTS API"""
        try:
            # Prepare API request
            url = f"{self.api_base_url}/v1/audio/speech"
            payload = {
                "input": text,
                "voice": voice,
                "response_format": "mp3",
                "speed": 1.0
            }
            
            # Make API request
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            # Save audio to temporary file
            temp_file = Path(tempfile.mktemp(suffix=".mp3"))
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            return temp_file
            
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def _get_audio_duration(self, audio_file: Path) -> float:
        """Get audio duration in seconds"""
        try:
            import soundfile as sf
            with sf.SoundFile(audio_file) as f:
                return len(f) / f.samplerate
        except Exception:
            return 0.0
    
    def _apply_special_requirements(self, report: AudioQualityReport, test_case: TestCase):
        """Apply test-specific validation requirements"""
        requirements = test_case.special_requirements
        
        # RTF requirement
        if "max_rtf" in requirements:
            max_rtf = requirements["max_rtf"]
            if report.performance_metrics.rtf > max_rtf:
                report.validation_errors.append(
                    f"RTF {report.performance_metrics.rtf:.3f} exceeds maximum {max_rtf}"
                )
        
        # Pronunciation checks
        if "pronunciation_check" in requirements:
            expected = requirements["pronunciation_check"]
            if expected.lower() not in report.content_metrics.transcription.lower():
                report.warnings.append(
                    f"Expected pronunciation '{expected}' not found in transcription"
                )
        
        # Avoid specific pronunciations
        if "avoid_pronunciation" in requirements:
            avoid = requirements["avoid_pronunciation"]
            if avoid.lower() in report.content_metrics.transcription.lower():
                report.validation_errors.append(
                    f"Unwanted pronunciation '{avoid}' found in transcription"
                )
        
        # Prosody requirements
        if "min_prosody_score" in requirements:
            min_score = requirements["min_prosody_score"]
            if report.quality_metrics.prosody_score < min_score:
                report.validation_errors.append(
                    f"Prosody score {report.quality_metrics.prosody_score:.3f} below minimum {min_score}"
                )
        
        # Duration validation
        expected_range = test_case.expected_duration_range
        actual_duration = report.technical_metrics.duration_ms / 1000
        if not (expected_range[0] <= actual_duration <= expected_range[1]):
            report.warnings.append(
                f"Duration {actual_duration:.2f}s outside expected range {expected_range}"
            )
    
    def run_full_suite(self, model_types: List[str] = None, 
                      categories: List[str] = None) -> Dict[str, List[AudioQualityReport]]:
        """Run the complete test suite"""
        if model_types is None:
            model_types = ["gguf", "onnx"]
        
        results = {}
        
        for model_type in model_types:
            logger.info(f"Running test suite for {model_type} model")
            model_results = []
            
            # Filter test cases by category if specified
            test_cases = self.test_cases
            if categories:
                test_cases = [tc for tc in test_cases if tc.category in categories]
            
            for test_case in test_cases:
                try:
                    # Switch model type via API if needed
                    self._switch_model_type(model_type)
                    
                    # Run test case
                    report = self.run_test_case(test_case, model_type)
                    model_results.append(report)
                    
                    # Log result
                    status = report.overall_result.value
                    logger.info(f"Test {test_case.id} ({model_type}): {status} (score: {report.score:.3f})")
                    
                except Exception as e:
                    logger.error(f"Failed to run test {test_case.id} for {model_type}: {e}")
            
            results[model_type] = model_results
        
        self.results = results
        return results
    
    def _switch_model_type(self, model_type: str):
        """Switch model type via API configuration"""
        try:
            # This would depend on the API's configuration endpoint
            # For now, assume the API auto-detects based on available models
            pass
        except Exception as e:
            logger.warning(f"Could not switch to {model_type} model: {e}")
    
    def generate_report(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        if not self.results:
            raise ValueError("No test results available. Run tests first.")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_suite_version": "1.0.0",
            "api_base_url": self.api_base_url,
            "summary": {},
            "model_results": {},
            "detailed_results": {}
        }
        
        # Generate summary statistics
        for model_type, results in self.results.items():
            total_tests = len(results)
            passed = sum(1 for r in results if r.overall_result == TestResult.PASS)
            failed = sum(1 for r in results if r.overall_result == TestResult.FAIL)
            warnings = sum(1 for r in results if r.overall_result == TestResult.WARNING)
            errors = sum(1 for r in results if r.overall_result == TestResult.ERROR)
            
            avg_score = sum(r.score for r in results) / total_tests if total_tests > 0 else 0
            avg_rtf = sum(r.performance_metrics.rtf for r in results) / total_tests if total_tests > 0 else 0
            
            report["summary"][model_type] = {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "errors": errors,
                "pass_rate": passed / total_tests if total_tests > 0 else 0,
                "average_score": avg_score,
                "average_rtf": avg_rtf
            }
            
            # Detailed results
            report["detailed_results"][model_type] = [
                asdict(result) for result in results
            ]
        
        # Save report if output file specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Test report saved to {output_file}")
        
        return report
    
    def cleanup(self):
        """Clean up test resources"""
        self.validator.cleanup()
