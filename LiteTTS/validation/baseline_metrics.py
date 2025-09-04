"""
Baseline Quality Metrics for LiteTTS

This module provides baseline quality metric establishment and management
for all available voices in the LiteTTS system. It generates baseline
audio files and establishes quality benchmarks for ongoing validation.
"""

import logging
import os
import json
import time
import tempfile
import requests
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

from .audio_quality_validator import AudioQualityValidator, ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class VoiceBaseline:
    """Baseline metrics for a single voice"""
    voice_name: str
    wer: float
    cer: float
    bleu_score: float
    rtf: float
    confidence_score: float
    audio_duration: float
    transcription_time: float
    baseline_text: str
    timestamp: str
    audio_file_path: Optional[str] = None
    audio_file_size: int = 0


@dataclass
class BaselineReport:
    """Complete baseline report for all voices"""
    timestamp: str
    total_voices: int
    successful_baselines: int
    failed_voices: List[str]
    average_wer: float
    average_rtf: float
    best_wer_voice: str
    worst_wer_voice: str
    fastest_rtf_voice: str
    slowest_rtf_voice: str
    baseline_text: str
    voices: Dict[str, VoiceBaseline]


class BaselineMetrics:
    """
    Baseline quality metrics establishment and management.
    
    Generates baseline audio files for all available voices and establishes
    quality benchmarks for ongoing validation and regression testing.
    """
    
    def __init__(self, 
                 baseline_text: str = "The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet and serves as an excellent test for speech synthesis quality.",
                 output_dir: str = "data/baselines",
                 server_port: int = 8359):
        """
        Initialize BaselineMetrics.
        
        Args:
            baseline_text: Standard text for baseline generation
            output_dir: Directory to store baseline files
            server_port: Port for LiteTTS server
        """
        self.baseline_text = baseline_text
        self.output_dir = Path(output_dir)
        self.server_port = server_port
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize validator
        self.validator = AudioQualityValidator("base")
        self.validator_initialized = False
        
        # Server process handle
        self.server_process = None
        
    def initialize(self) -> bool:
        """Initialize the baseline metrics system."""
        try:
            self.logger.info("Initializing BaselineMetrics system...")
            
            # Initialize audio quality validator
            if not self.validator.initialize():
                self.logger.error("Failed to initialize AudioQualityValidator")
                return False
            
            self.validator_initialized = True
            self.logger.info("✅ BaselineMetrics system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize BaselineMetrics: {e}")
            return False
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voices from LiteTTS."""
        try:
            # Try to get voices from API
            response = requests.get(f"http://localhost:{self.server_port}/v1/voices", timeout=5)
            if response.status_code == 200:
                voices_data = response.json()
                if isinstance(voices_data, dict) and "voices" in voices_data:
                    return [voice["id"] for voice in voices_data["voices"]]
                elif isinstance(voices_data, list):
                    return [voice["id"] if isinstance(voice, dict) else str(voice) for voice in voices_data]
            
        except requests.exceptions.RequestException:
            pass
        
        # Fallback: use predefined voice list
        default_voices = [
            "af_heart", "af_soul", "af_sky", "af_bella", "af_sarah",
            "am_adam", "am_michael", "br_heart", "br_soul", "en_heart",
            "en_soul", "en_sky", "en_bella", "en_sarah", "en_adam",
            "en_michael", "es_heart", "es_soul", "fr_heart", "fr_soul",
            "de_heart", "de_soul", "it_heart", "it_soul", "pt_heart",
            "pt_soul", "ru_heart", "ru_soul", "ja_heart", "ja_soul",
            "ko_heart", "ko_soul", "zh_heart", "zh_soul", "ar_heart",
            "ar_soul", "hi_heart", "hi_soul", "tr_heart", "tr_soul",
            "pl_heart", "pl_soul", "nl_heart", "nl_soul", "sv_heart",
            "sv_soul", "da_heart", "da_soul", "no_heart", "no_soul",
            "fi_heart", "fi_soul", "cs_heart", "cs_soul", "hu_heart"
        ]
        
        self.logger.warning("Using default voice list (API not available)")
        return default_voices
    
    def start_litetts_server(self) -> bool:
        """Start LiteTTS server for audio generation."""
        try:
            self.logger.info(f"Starting LiteTTS server on port {self.server_port}...")
            
            # Start server process
            self.server_process = subprocess.Popen(
                ["python", "app.py", "--port", str(self.server_port)],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            max_wait = 30
            for i in range(max_wait):
                try:
                    response = requests.get(f"http://localhost:{self.server_port}/health", timeout=2)
                    if response.status_code == 200:
                        self.logger.info(f"✅ LiteTTS server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
                
                # Check if process died
                if self.server_process.poll() is not None:
                    self.logger.error("LiteTTS server process died during startup")
                    return False
            
            self.logger.error(f"LiteTTS server failed to start within {max_wait}s")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to start LiteTTS server: {e}")
            return False
    
    def stop_litetts_server(self):
        """Stop LiteTTS server."""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                self.logger.info("LiteTTS server stopped")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
                self.logger.warning("LiteTTS server killed (timeout)")
            except Exception as e:
                self.logger.error(f"Error stopping server: {e}")
            finally:
                self.server_process = None
    
    def generate_baseline_audio(self, voice: str, output_path: str) -> bool:
        """Generate baseline audio file for a voice."""
        try:
            response = requests.post(
                f"http://localhost:{self.server_port}/v1/audio/speech",
                json={
                    "input": self.baseline_text,
                    "voice": voice,
                    "response_format": "mp3"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                # Verify file was created and has reasonable size
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    return True
                else:
                    self.logger.warning(f"Generated file for {voice} is too small")
                    return False
            else:
                self.logger.warning(f"HTTP {response.status_code} for {voice}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to generate audio for {voice}: {e}")
            return False
    
    def establish_voice_baselines(self, voices: Optional[List[str]] = None, 
                                max_voices: Optional[int] = None) -> BaselineReport:
        """
        Establish baseline quality metrics for voices.
        
        Args:
            voices: List of voices to process (None = all available)
            max_voices: Maximum number of voices to process (for testing)
            
        Returns:
            BaselineReport with comprehensive baseline data
        """
        if not self.validator_initialized:
            raise RuntimeError("BaselineMetrics not initialized. Call initialize() first.")
        
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        # Get voices to process
        if voices is None:
            voices = self.get_available_voices()
        
        if max_voices:
            voices = voices[:max_voices]
        
        self.logger.info(f"Establishing baselines for {len(voices)} voices...")
        
        # Start server
        if not self.start_litetts_server():
            raise RuntimeError("Failed to start LiteTTS server")
        
        try:
            voice_baselines = {}
            failed_voices = []
            successful_count = 0
            
            for i, voice in enumerate(voices):
                self.logger.info(f"Processing {i+1}/{len(voices)}: {voice}")
                
                try:
                    # Generate audio file
                    audio_filename = f"baseline_{voice}_{timestamp.replace(':', '-')}.mp3"
                    audio_path = self.output_dir / audio_filename
                    
                    if self.generate_baseline_audio(voice, str(audio_path)):
                        # Validate audio quality
                        result = self.validator.validate_transcription(
                            audio_path=str(audio_path),
                            reference_text=self.baseline_text,
                            voice_name=voice
                        )
                        
                        if result.metrics.success:
                            # Create baseline record
                            baseline = VoiceBaseline(
                                voice_name=voice,
                                wer=result.metrics.wer,
                                cer=result.metrics.cer,
                                bleu_score=result.metrics.bleu_score,
                                rtf=result.metrics.rtf,
                                confidence_score=result.metrics.confidence_score,
                                audio_duration=result.metrics.audio_duration,
                                transcription_time=result.metrics.transcription_time,
                                baseline_text=self.baseline_text,
                                timestamp=timestamp,
                                audio_file_path=str(audio_path),
                                audio_file_size=os.path.getsize(audio_path)
                            )
                            
                            voice_baselines[voice] = baseline
                            successful_count += 1
                            
                            self.logger.info(f"✅ {voice}: WER={baseline.wer:.3f}, RTF={baseline.rtf:.3f}")
                        else:
                            failed_voices.append(voice)
                            self.logger.warning(f"❌ {voice}: Validation failed - {result.metrics.error_message}")
                    else:
                        failed_voices.append(voice)
                        self.logger.warning(f"❌ {voice}: Audio generation failed")
                        
                except Exception as e:
                    failed_voices.append(voice)
                    self.logger.error(f"❌ {voice}: Exception - {e}")
            
            # Calculate summary statistics
            if successful_count > 0:
                wer_values = [b.wer for b in voice_baselines.values()]
                rtf_values = [b.rtf for b in voice_baselines.values()]
                
                average_wer = sum(wer_values) / len(wer_values)
                average_rtf = sum(rtf_values) / len(rtf_values)
                
                # Find best/worst voices
                best_wer_voice = min(voice_baselines.keys(), key=lambda v: voice_baselines[v].wer)
                worst_wer_voice = max(voice_baselines.keys(), key=lambda v: voice_baselines[v].wer)
                fastest_rtf_voice = min(voice_baselines.keys(), key=lambda v: voice_baselines[v].rtf)
                slowest_rtf_voice = max(voice_baselines.keys(), key=lambda v: voice_baselines[v].rtf)
            else:
                average_wer = 1.0
                average_rtf = 0.0
                best_wer_voice = "none"
                worst_wer_voice = "none"
                fastest_rtf_voice = "none"
                slowest_rtf_voice = "none"
            
            # Create baseline report
            report = BaselineReport(
                timestamp=timestamp,
                total_voices=len(voices),
                successful_baselines=successful_count,
                failed_voices=failed_voices,
                average_wer=average_wer,
                average_rtf=average_rtf,
                best_wer_voice=best_wer_voice,
                worst_wer_voice=worst_wer_voice,
                fastest_rtf_voice=fastest_rtf_voice,
                slowest_rtf_voice=slowest_rtf_voice,
                baseline_text=self.baseline_text,
                voices=voice_baselines
            )
            
            # Save baseline report
            self.save_baseline_report(report)
            
            total_time = time.time() - start_time
            self.logger.info(f"✅ Baseline establishment completed in {total_time:.1f}s")
            self.logger.info(f"   Successful: {successful_count}/{len(voices)} voices")
            self.logger.info(f"   Average WER: {average_wer:.3f}")
            self.logger.info(f"   Average RTF: {average_rtf:.3f}")
            
            return report
            
        finally:
            self.stop_litetts_server()
    
    def save_baseline_report(self, report: BaselineReport):
        """Save baseline report to JSON file."""
        try:
            report_filename = f"baseline_report_{report.timestamp.replace(':', '-')}.json"
            report_path = self.output_dir / report_filename
            
            # Convert to dictionary for JSON serialization
            report_dict = asdict(report)
            
            with open(report_path, 'w') as f:
                json.dump(report_dict, f, indent=2)
            
            # Also save as latest baseline
            latest_path = self.output_dir / "latest_baseline.json"
            with open(latest_path, 'w') as f:
                json.dump(report_dict, f, indent=2)
            
            self.logger.info(f"Baseline report saved: {report_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save baseline report: {e}")
    
    def load_baseline_report(self, report_path: Optional[str] = None) -> Optional[BaselineReport]:
        """Load baseline report from JSON file."""
        try:
            if report_path is None:
                report_path = self.output_dir / "latest_baseline.json"
            
            with open(report_path, 'r') as f:
                report_dict = json.load(f)
            
            # Convert voice baselines back to VoiceBaseline objects
            voices = {}
            for voice_name, voice_data in report_dict["voices"].items():
                voices[voice_name] = VoiceBaseline(**voice_data)
            
            report_dict["voices"] = voices
            
            return BaselineReport(**report_dict)
            
        except Exception as e:
            self.logger.error(f"Failed to load baseline report: {e}")
            return None


def create_baseline_metrics(baseline_text: str = None, output_dir: str = "data/baselines") -> BaselineMetrics:
    """Factory function to create BaselineMetrics instance."""
    if baseline_text is None:
        baseline_text = "The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet and serves as an excellent test for speech synthesis quality."
    
    return BaselineMetrics(baseline_text=baseline_text, output_dir=output_dir)
