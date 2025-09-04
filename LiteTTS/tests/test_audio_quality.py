"""
Audio Quality Test Suite for LiteTTS

This module provides comprehensive automated testing for audio quality
validation using Whisper STT integration. Tests generate audio files
for all available voices and validate quality metrics.
"""

import pytest
import os
import tempfile
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

# Import LiteTTS components
from LiteTTS.validation.audio_quality_validator import AudioQualityValidator, ValidationResult
from LiteTTS.validation.whisper_integration import validate_whisper_installation

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAudioQuality:
    """Test suite for audio quality validation."""
    
    @classmethod
    def setup_class(cls):
        """Set up test class with validator and test data."""
        cls.validator = None
        cls.test_text = "Hello world, this is a test of the text to speech system."
        cls.test_voices = [
            "af_heart", "af_soul", "af_sky", "af_bella", "af_sarah",
            "am_adam", "am_michael", "br_heart", "br_soul", "en_heart"
        ]  # Sample of voices for testing
        cls.temp_dir = None
        cls.generated_files = []
        
    def setup_method(self):
        """Set up each test method."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix="litetts_audio_test_")
        logger.info(f"Test temp directory: {self.temp_dir}")
        
    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up generated files
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_whisper_installation(self):
        """Test that Whisper is properly installed and configured."""
        result = validate_whisper_installation()
        
        assert result["faster_whisper_available"], "faster-whisper not available"
        assert result["installation_valid"], f"Installation invalid: {result.get('error_message')}"
        
        # Check that model loading is reasonably fast
        if "test_load_time" in result:
            assert result["test_load_time"] < 30.0, f"Model loading too slow: {result['test_load_time']}s"
        
        logger.info(f"✅ Whisper installation valid: {result['supported_models']}")
    
    def test_validator_initialization(self):
        """Test AudioQualityValidator initialization."""
        validator = AudioQualityValidator("base")
        
        # Test initialization
        success = validator.initialize()
        assert success, "Failed to initialize AudioQualityValidator"
        
        # Verify model is loaded
        assert validator.model_loaded, "Model not marked as loaded"
        assert validator.whisper_validator.is_model_loaded(), "Whisper model not loaded"
        
        # Store for other tests
        self.__class__.validator = validator
        
        logger.info("✅ AudioQualityValidator initialized successfully")
    
    def test_generate_test_audio_files(self):
        """Generate audio files for testing using LiteTTS API."""
        if not self.validator:
            pytest.skip("Validator not initialized")
        
        # Start LiteTTS server for audio generation
        import subprocess
        import requests
        import signal
        
        # Start server in background
        server_process = subprocess.Popen(
            ["python", "app.py", "--port", "8358"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            # Wait for server to start
            time.sleep(10)
            
            # Test server is responding
            try:
                response = requests.get("http://localhost:8358/health", timeout=5)
                if response.status_code != 200:
                    pytest.skip("LiteTTS server not responding")
            except requests.exceptions.RequestException:
                pytest.skip("Cannot connect to LiteTTS server")
            
            # Generate audio files for test voices
            generated_count = 0
            for voice in self.test_voices[:5]:  # Limit to 5 voices for testing
                try:
                    audio_path = os.path.join(self.temp_dir, f"test_{voice}.mp3")
                    
                    # Make TTS request
                    response = requests.post(
                        "http://localhost:8358/v1/audio/speech",
                        json={
                            "input": self.test_text,
                            "voice": voice,
                            "response_format": "mp3"
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        # Save audio file
                        with open(audio_path, "wb") as f:
                            f.write(response.content)
                        
                        # Verify file was created and has content
                        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                            self.generated_files.append((audio_path, self.test_text, voice))
                            generated_count += 1
                            logger.info(f"✅ Generated audio for {voice}: {os.path.getsize(audio_path)} bytes")
                        else:
                            logger.warning(f"⚠️ Generated file for {voice} is too small or missing")
                    else:
                        logger.warning(f"⚠️ Failed to generate audio for {voice}: HTTP {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error generating audio for {voice}: {e}")
                    continue
            
            # Store generated files for other tests
            self.__class__.generated_files = self.generated_files
            
            assert generated_count > 0, f"No audio files generated successfully (tried {len(self.test_voices[:5])} voices)"
            logger.info(f"✅ Generated {generated_count} test audio files")
            
        finally:
            # Clean up server
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()
    
    def test_audio_quality_validation(self):
        """Test audio quality validation on generated files."""
        if not self.validator:
            pytest.skip("Validator not initialized")
        
        if not self.generated_files:
            pytest.skip("No generated audio files available")
        
        results = []
        
        for audio_path, reference_text, voice_name in self.generated_files:
            logger.info(f"Validating {voice_name}...")
            
            # Validate audio quality
            result = self.validator.validate_transcription(
                audio_path=audio_path,
                reference_text=reference_text,
                voice_name=voice_name
            )
            
            results.append(result)
            
            # Basic assertions
            assert isinstance(result, ValidationResult), "Invalid result type"
            assert result.voice_name == voice_name, "Voice name mismatch"
            assert result.reference_text == reference_text, "Reference text mismatch"
            
            if result.metrics.success:
                # Quality assertions
                assert 0.0 <= result.metrics.wer <= 1.0, f"Invalid WER: {result.metrics.wer}"
                assert 0.0 <= result.metrics.cer <= 1.0, f"Invalid CER: {result.metrics.cer}"
                assert 0.0 <= result.metrics.bleu_score <= 1.0, f"Invalid BLEU: {result.metrics.bleu_score}"
                assert result.metrics.rtf >= 0.0, f"Invalid RTF: {result.metrics.rtf}"
                
                # Performance assertions (based on roadmap targets)
                assert result.metrics.rtf < 0.25, f"RTF too high: {result.metrics.rtf} (target: <0.25)"
                
                logger.info(f"✅ {voice_name}: WER={result.metrics.wer:.3f}, RTF={result.metrics.rtf:.3f}")
            else:
                logger.warning(f"⚠️ {voice_name}: Validation failed - {result.metrics.error_message}")
        
        # Store results for summary test
        self.__class__.validation_results = results
        
        # Ensure at least some validations succeeded
        successful_results = [r for r in results if r.metrics.success]
        assert len(successful_results) > 0, "No successful validations"
        
        logger.info(f"✅ Validated {len(successful_results)}/{len(results)} audio files successfully")
    
    def test_quality_metrics_summary(self):
        """Test quality metrics summary calculation."""
        if not hasattr(self.__class__, 'validation_results'):
            pytest.skip("No validation results available")
        
        if not self.validator:
            pytest.skip("Validator not initialized")
        
        # Calculate summary statistics
        summary = self.validator.get_summary_statistics(self.validation_results)
        
        # Verify summary structure
        required_keys = [
            "total_files", "successful_validations", "success_rate",
            "average_wer", "min_wer", "max_wer",
            "average_rtf", "min_rtf", "max_rtf", "voices_tested"
        ]
        
        for key in required_keys:
            assert key in summary, f"Missing summary key: {key}"
        
        # Verify summary values
        assert summary["total_files"] == len(self.validation_results)
        assert summary["successful_validations"] <= summary["total_files"]
        assert 0.0 <= summary["success_rate"] <= 1.0
        
        if summary["successful_validations"] > 0:
            assert 0.0 <= summary["average_wer"] <= 1.0
            assert 0.0 <= summary["min_wer"] <= summary["max_wer"] <= 1.0
            assert summary["average_rtf"] >= 0.0
            assert summary["min_rtf"] <= summary["max_rtf"]
            
            # Performance targets from roadmap
            assert summary["average_rtf"] < 0.25, f"Average RTF too high: {summary['average_rtf']}"
        
        logger.info(f"✅ Quality Summary:")
        logger.info(f"   Success rate: {summary['success_rate']:.1%}")
        logger.info(f"   Average WER: {summary.get('average_wer', 'N/A'):.3f}")
        logger.info(f"   Average RTF: {summary.get('average_rtf', 'N/A'):.3f}")
        logger.info(f"   Voices tested: {summary['voices_tested']}")
    
    def test_batch_validation(self):
        """Test batch validation functionality."""
        if not self.validator:
            pytest.skip("Validator not initialized")
        
        if not self.generated_files:
            pytest.skip("No generated audio files available")
        
        # Test batch validation
        batch_results = self.validator.batch_validate(self.generated_files)
        
        # Verify results
        assert len(batch_results) == len(self.generated_files)
        
        for i, result in enumerate(batch_results):
            expected_voice = self.generated_files[i][2]
            assert result.voice_name == expected_voice
        
        logger.info(f"✅ Batch validation completed: {len(batch_results)} results")
    
    def test_performance_targets(self):
        """Test that performance targets from roadmap are met."""
        if not hasattr(self.__class__, 'validation_results'):
            pytest.skip("No validation results available")
        
        successful_results = [r for r in self.validation_results if r.metrics.success]
        
        if not successful_results:
            pytest.skip("No successful validation results")
        
        # Test RTF targets (< 0.25 from roadmap)
        rtf_violations = [r for r in successful_results if r.metrics.rtf >= 0.25]
        
        if rtf_violations:
            violation_details = [f"{r.voice_name}: {r.metrics.rtf:.3f}" for r in rtf_violations]
            logger.warning(f"RTF violations: {violation_details}")
        
        # Allow some tolerance for test environment
        violation_rate = len(rtf_violations) / len(successful_results)
        assert violation_rate < 0.5, f"Too many RTF violations: {violation_rate:.1%} (target: <50%)"
        
        # Test transcription quality (WER should be reasonable)
        high_wer_results = [r for r in successful_results if r.metrics.wer > 0.3]
        wer_violation_rate = len(high_wer_results) / len(successful_results)
        
        assert wer_violation_rate < 0.3, f"Too many high WER results: {wer_violation_rate:.1%}"
        
        logger.info(f"✅ Performance targets check:")
        logger.info(f"   RTF violations: {len(rtf_violations)}/{len(successful_results)} ({violation_rate:.1%})")
        logger.info(f"   High WER results: {len(high_wer_results)}/{len(successful_results)} ({wer_violation_rate:.1%})")


# Utility functions for test execution
def run_audio_quality_tests():
    """Run audio quality tests and return results."""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ]
    
    return pytest.main(pytest_args)


if __name__ == "__main__":
    # Run tests when executed directly
    exit_code = run_audio_quality_tests()
    exit(exit_code)
