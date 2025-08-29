#!/usr/bin/env python3
"""
Audio Waveform Analysis for LiteTTS Quality Verification
Analyzes generated audio files for quality indicators without requiring Whisper
"""

import os
import sys
import json
import wave
import struct
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Original test phrases for reference
ORIGINAL_PHRASES = [
    "Hello world",
    "This is a test", 
    "The quick brown fox jumps over the lazy dog",
    "Testing audio quality",
    "LiteTTS verification"
]

class AudioWaveformAnalyzer:
    """Comprehensive audio quality analysis through waveform analysis"""
    
    def __init__(self, audio_dir: str = "test_audio_output"):
        self.audio_dir = Path(audio_dir)
        self.results = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        logger.info("🎵 Audio Waveform Analyzer initialized")
        logger.info(f"📁 Audio directory: {self.audio_dir.absolute()}")
    
    def find_audio_files(self) -> List[Path]:
        """Find all generated audio files"""
        if not self.audio_dir.exists():
            raise FileNotFoundError(f"Audio directory not found: {self.audio_dir}")
        
        audio_files = list(self.audio_dir.glob("test_audio_*.wav"))
        audio_files.sort()  # Sort by filename for consistent ordering
        
        logger.info(f"📁 Found {len(audio_files)} audio files for analysis")
        return audio_files
    
    def analyze_audio_file(self, audio_file: Path) -> Dict[str, Any]:
        """Comprehensive analysis of a single audio file"""
        logger.info(f"🔍 Analyzing: {audio_file.name}")
        
        try:
            # Basic file properties
            file_size = audio_file.stat().st_size
            
            # Open and analyze WAV file
            with wave.open(str(audio_file), 'rb') as wav_file:
                # Get basic audio properties
                sample_rate = wav_file.getframerate()
                num_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                num_frames = wav_file.getnframes()
                duration = num_frames / sample_rate
                
                # Read audio data
                audio_data = wav_file.readframes(num_frames)
                
                # Convert to numpy array for analysis
                if sample_width == 1:
                    audio_array = np.frombuffer(audio_data, dtype=np.uint8)
                    audio_array = (audio_array.astype(np.float32) - 128) / 128.0
                elif sample_width == 2:
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    audio_array = audio_array.astype(np.float32) / 32768.0
                elif sample_width == 4:
                    audio_array = np.frombuffer(audio_data, dtype=np.int32)
                    audio_array = audio_array.astype(np.float32) / 2147483648.0
                else:
                    raise ValueError(f"Unsupported sample width: {sample_width}")
                
                # Handle stereo audio
                if num_channels == 2:
                    audio_array = audio_array.reshape(-1, 2)
                    audio_array = np.mean(audio_array, axis=1)  # Convert to mono
            
            # Perform waveform analysis
            analysis_results = self._analyze_waveform(audio_array, sample_rate)
            
            # Extract phrase information
            phrase_id = self._extract_phrase_id(audio_file.name)
            original_text = ORIGINAL_PHRASES[phrase_id - 1] if phrase_id <= len(ORIGINAL_PHRASES) else "Unknown"
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(analysis_results)
            
            result = {
                "file_path": str(audio_file.absolute()),
                "filename": audio_file.name,
                "phrase_id": phrase_id,
                "original_text": original_text,
                "file_size_bytes": file_size,
                "duration_seconds": duration,
                "sample_rate": sample_rate,
                "num_channels": num_channels,
                "sample_width_bytes": sample_width,
                "num_frames": num_frames,
                "quality_score": quality_score,
                "analysis_results": analysis_results,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Analysis completed:")
            logger.info(f"   📊 Quality Score: {quality_score:.1f}/100")
            logger.info(f"   🔊 RMS Level: {analysis_results['rms_level']:.3f}")
            logger.info(f"   📈 Dynamic Range: {analysis_results['dynamic_range_db']:.1f} dB")
            logger.info(f"   🎵 Speech Activity: {analysis_results['speech_activity_percent']:.1f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Analysis failed for {audio_file.name}: {e}")
            return {
                "file_path": str(audio_file.absolute()),
                "filename": audio_file.name,
                "phrase_id": self._extract_phrase_id(audio_file.name),
                "original_text": "Unknown",
                "quality_score": 0.0,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_waveform(self, audio_array: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Perform detailed waveform analysis"""
        # Basic amplitude statistics
        rms_level = np.sqrt(np.mean(audio_array ** 2))
        peak_level = np.max(np.abs(audio_array))
        
        # Dynamic range analysis
        dynamic_range_db = 20 * np.log10(peak_level / max(rms_level, 1e-10))
        
        # Zero crossing rate (indicator of speech content)
        zero_crossings = np.sum(np.diff(np.sign(audio_array)) != 0)
        zero_crossing_rate = zero_crossings / len(audio_array)
        
        # Energy distribution analysis
        frame_size = int(0.025 * sample_rate)  # 25ms frames
        hop_size = int(0.010 * sample_rate)    # 10ms hop
        
        frames = []
        for i in range(0, len(audio_array) - frame_size, hop_size):
            frame = audio_array[i:i + frame_size]
            frames.append(frame)
        
        if frames:
            frame_energies = [np.sum(frame ** 2) for frame in frames]
            
            # Speech activity detection (frames above energy threshold)
            energy_threshold = np.mean(frame_energies) * 0.1
            active_frames = sum(1 for energy in frame_energies if energy > energy_threshold)
            speech_activity_percent = (active_frames / len(frame_energies)) * 100
            
            # Spectral analysis (basic)
            spectral_centroid = self._calculate_spectral_centroid(audio_array, sample_rate)
            spectral_rolloff = self._calculate_spectral_rolloff(audio_array, sample_rate)
        else:
            speech_activity_percent = 0.0
            spectral_centroid = 0.0
            spectral_rolloff = 0.0
        
        # Silence detection
        silence_threshold = rms_level * 0.01
        silence_samples = np.sum(np.abs(audio_array) < silence_threshold)
        silence_percent = (silence_samples / len(audio_array)) * 100
        
        # Clipping detection
        clipping_threshold = 0.95
        clipped_samples = np.sum(np.abs(audio_array) > clipping_threshold)
        clipping_percent = (clipped_samples / len(audio_array)) * 100
        
        return {
            "rms_level": float(rms_level),
            "peak_level": float(peak_level),
            "dynamic_range_db": float(dynamic_range_db),
            "zero_crossing_rate": float(zero_crossing_rate),
            "speech_activity_percent": float(speech_activity_percent),
            "silence_percent": float(silence_percent),
            "clipping_percent": float(clipping_percent),
            "spectral_centroid": float(spectral_centroid),
            "spectral_rolloff": float(spectral_rolloff)
        }
    
    def _calculate_spectral_centroid(self, audio_array: np.ndarray, sample_rate: int) -> float:
        """Calculate spectral centroid (brightness indicator)"""
        try:
            # Simple FFT-based spectral centroid
            fft = np.fft.rfft(audio_array)
            magnitude = np.abs(fft)
            freqs = np.fft.rfftfreq(len(audio_array), 1/sample_rate)
            
            if np.sum(magnitude) > 0:
                centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
                return centroid
            else:
                return 0.0
        except:
            return 0.0
    
    def _calculate_spectral_rolloff(self, audio_array: np.ndarray, sample_rate: int) -> float:
        """Calculate spectral rolloff (frequency content indicator)"""
        try:
            # Simple FFT-based spectral rolloff
            fft = np.fft.rfft(audio_array)
            magnitude = np.abs(fft)
            freqs = np.fft.rfftfreq(len(audio_array), 1/sample_rate)
            
            total_energy = np.sum(magnitude)
            if total_energy > 0:
                cumulative_energy = np.cumsum(magnitude)
                rolloff_threshold = 0.85 * total_energy
                rolloff_idx = np.where(cumulative_energy >= rolloff_threshold)[0]
                if len(rolloff_idx) > 0:
                    return freqs[rolloff_idx[0]]
            return 0.0
        except:
            return 0.0
    
    def _calculate_quality_score(self, analysis: Dict[str, float]) -> float:
        """Calculate overall quality score based on analysis metrics"""
        score = 100.0
        
        # Penalize for low RMS level (too quiet)
        if analysis["rms_level"] < 0.01:
            score -= 20
        elif analysis["rms_level"] < 0.05:
            score -= 10
        
        # Penalize for low speech activity
        if analysis["speech_activity_percent"] < 50:
            score -= 15
        elif analysis["speech_activity_percent"] < 70:
            score -= 5
        
        # Penalize for excessive silence
        if analysis["silence_percent"] > 50:
            score -= 20
        elif analysis["silence_percent"] > 30:
            score -= 10
        
        # Penalize for clipping
        if analysis["clipping_percent"] > 1:
            score -= 25
        elif analysis["clipping_percent"] > 0.1:
            score -= 10
        
        # Penalize for poor dynamic range
        if analysis["dynamic_range_db"] < 10:
            score -= 15
        elif analysis["dynamic_range_db"] < 20:
            score -= 5
        
        # Bonus for good spectral characteristics
        if 1000 <= analysis["spectral_centroid"] <= 3000:
            score += 5
        
        return max(0.0, min(100.0, score))
    
    def _extract_phrase_id(self, filename: str) -> int:
        """Extract phrase ID from filename"""
        try:
            parts = filename.split("_")
            for part in parts:
                if part.isdigit() and len(part) == 2:
                    return int(part)
            return 1
        except:
            return 1
    
    def analyze_all_files(self) -> List[Dict[str, Any]]:
        """Analyze all audio files"""
        audio_files = self.find_audio_files()
        
        if not audio_files:
            logger.warning("⚠️ No audio files found for analysis")
            return []
        
        logger.info(f"🔍 Starting analysis of {len(audio_files)} audio files...")
        
        for audio_file in audio_files:
            result = self.analyze_audio_file(audio_file)
            self.results.append(result)
        
        return self.results
    
    def save_analysis_report(self) -> str:
        """Save comprehensive analysis report"""
        report_file = self.audio_dir / f"waveform_analysis_report_{self.timestamp}.json"
        
        # Calculate summary statistics
        successful_results = [r for r in self.results if r.get("success", False)]
        total_files = len(self.results)
        successful_files = len(successful_results)
        
        if successful_results:
            avg_quality_score = sum(r["quality_score"] for r in successful_results) / len(successful_results)
            high_quality_count = sum(1 for r in successful_results if r["quality_score"] >= 80.0)
            avg_duration = sum(r["duration_seconds"] for r in successful_results) / len(successful_results)
            avg_file_size = sum(r["file_size_bytes"] for r in successful_results) / len(successful_results)
        else:
            avg_quality_score = 0.0
            high_quality_count = 0
            avg_duration = 0.0
            avg_file_size = 0.0
        
        report = {
            "analysis_summary": {
                "timestamp": self.timestamp,
                "total_audio_files": total_files,
                "successful_analyses": successful_files,
                "failed_analyses": total_files - successful_files,
                "average_quality_score": avg_quality_score,
                "high_quality_files_80_plus": high_quality_count,
                "quality_threshold_met": high_quality_count >= (total_files * 0.8),
                "average_duration_seconds": avg_duration,
                "average_file_size_bytes": avg_file_size
            },
            "original_phrases": ORIGINAL_PHRASES,
            "detailed_results": self.results,
            "audio_directory": str(self.audio_dir.absolute())
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Analysis report saved: {report_file}")
        return str(report_file)
    
    def print_analysis_summary(self):
        """Print comprehensive summary of analysis results"""
        successful_results = [r for r in self.results if r.get("success", False)]
        high_quality_count = sum(1 for r in successful_results if r["quality_score"] >= 80.0)
        
        print("\n" + "="*70)
        print("🔍 AUDIO WAVEFORM ANALYSIS RESULTS")
        print("="*70)
        print(f"📅 Analysis Date: {self.timestamp}")
        print(f"📁 Audio Directory: {self.audio_dir.absolute()}")
        print(f"🎵 Total Audio Files: {len(self.results)}")
        print(f"✅ Successful Analyses: {len(successful_results)}")
        print(f"❌ Failed Analyses: {len(self.results) - len(successful_results)}")
        
        if successful_results:
            avg_quality = sum(r["quality_score"] for r in successful_results) / len(successful_results)
            print(f"📊 Average Quality Score: {avg_quality:.1f}/100")
            print(f"🎯 High Quality Files (≥80): {high_quality_count}/{len(successful_results)}")
            print(f"✅ Quality Threshold Met: {'YES' if high_quality_count >= len(successful_results) * 0.8 else 'NO'}")
            
            print("\n📋 ANALYSIS RESULTS:")
            for i, result in enumerate(successful_results, 1):
                status = "✅" if result["quality_score"] >= 80.0 else "⚠️"
                print(f"  {i}. {status} {result['filename']}")
                print(f"      📝 Phrase: '{result['original_text']}'")
                print(f"      📊 Quality Score: {result['quality_score']:.1f}/100")
                print(f"      ⏱️  Duration: {result['duration_seconds']:.2f}s")
                print(f"      📏 File Size: {result['file_size_bytes']} bytes")
                if 'analysis_results' in result:
                    analysis = result['analysis_results']
                    print(f"      🔊 RMS Level: {analysis['rms_level']:.3f}")
                    print(f"      🎵 Speech Activity: {analysis['speech_activity_percent']:.1f}%")
                print()
        
        print("="*70)

def main():
    """Main execution function"""
    print("🔍 LiteTTS Audio Waveform Analysis")
    print("="*50)
    
    try:
        # Initialize analyzer
        analyzer = AudioWaveformAnalyzer()
        
        # Analyze all audio files
        results = analyzer.analyze_all_files()
        
        if not results:
            print("❌ No audio files found for analysis")
            return 1
        
        # Save analysis report
        report_file = analyzer.save_analysis_report()
        
        # Print summary
        analyzer.print_analysis_summary()
        
        print(f"\n📊 Detailed analysis report saved to: {report_file}")
        print("✅ Audio waveform analysis completed!")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Audio waveform analysis failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
