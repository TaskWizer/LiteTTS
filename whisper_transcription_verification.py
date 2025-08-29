#!/usr/bin/env python3
"""
Whisper ASR Transcription Verification for LiteTTS Audio Quality
Uses OpenAI Whisper to transcribe generated audio files and verify accuracy
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import difflib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Original test phrases for comparison
ORIGINAL_PHRASES = [
    "Hello world",
    "This is a test", 
    "The quick brown fox jumps over the lazy dog",
    "Testing audio quality",
    "LiteTTS verification"
]

class WhisperTranscriptionVerifier:
    """Whisper-based audio quality verification through transcription accuracy"""
    
    def __init__(self, audio_dir: str = "test_audio_output"):
        self.audio_dir = Path(audio_dir)
        self.results = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Try to import whisper
        try:
            import whisper
            self.whisper = whisper
            logger.info("✅ Whisper library imported successfully")
        except ImportError:
            logger.error("❌ Whisper library not available. Installing...")
            self._install_whisper()
            import whisper
            self.whisper = whisper
        
        # Load Whisper model
        try:
            logger.info("🔄 Loading Whisper model (base)...")
            self.model = self.whisper.load_model("base")
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            raise
    
    def _install_whisper(self):
        """Install Whisper if not available"""
        import subprocess
        try:
            logger.info("📦 Installing OpenAI Whisper...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
            logger.info("✅ Whisper installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install Whisper: {e}")
            raise
    
    def find_audio_files(self) -> List[Path]:
        """Find all generated audio files"""
        if not self.audio_dir.exists():
            raise FileNotFoundError(f"Audio directory not found: {self.audio_dir}")
        
        audio_files = list(self.audio_dir.glob("test_audio_*.wav"))
        audio_files.sort()  # Sort by filename for consistent ordering
        
        logger.info(f"📁 Found {len(audio_files)} audio files in {self.audio_dir}")
        return audio_files
    
    def transcribe_audio_file(self, audio_file: Path) -> Dict[str, Any]:
        """Transcribe a single audio file using Whisper"""
        logger.info(f"🎤 Transcribing: {audio_file.name}")
        
        try:
            # Transcribe with Whisper
            result = self.model.transcribe(str(audio_file))
            transcribed_text = result["text"].strip()
            
            # Extract phrase ID from filename
            phrase_id = self._extract_phrase_id(audio_file.name)
            original_text = ORIGINAL_PHRASES[phrase_id - 1] if phrase_id <= len(ORIGINAL_PHRASES) else "Unknown"
            
            # Calculate accuracy metrics
            accuracy_metrics = self._calculate_accuracy(original_text, transcribed_text)
            
            transcription_result = {
                "file_path": str(audio_file.absolute()),
                "filename": audio_file.name,
                "phrase_id": phrase_id,
                "original_text": original_text,
                "transcribed_text": transcribed_text,
                "accuracy_percent": accuracy_metrics["accuracy_percent"],
                "word_accuracy": accuracy_metrics["word_accuracy"],
                "character_accuracy": accuracy_metrics["character_accuracy"],
                "levenshtein_distance": accuracy_metrics["levenshtein_distance"],
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Transcription completed:")
            logger.info(f"   📝 Original: '{original_text}'")
            logger.info(f"   🎤 Transcribed: '{transcribed_text}'")
            logger.info(f"   📊 Accuracy: {accuracy_metrics['accuracy_percent']:.1f}%")
            
            return transcription_result
            
        except Exception as e:
            logger.error(f"❌ Transcription failed for {audio_file.name}: {e}")
            return {
                "file_path": str(audio_file.absolute()),
                "filename": audio_file.name,
                "phrase_id": self._extract_phrase_id(audio_file.name),
                "original_text": "Unknown",
                "transcribed_text": "",
                "accuracy_percent": 0.0,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_phrase_id(self, filename: str) -> int:
        """Extract phrase ID from filename"""
        try:
            # Extract number from filename like "test_audio_2025-08-28_20-52-39_01_Hello_world.wav"
            parts = filename.split("_")
            for part in parts:
                if part.isdigit() and len(part) == 2:
                    return int(part)
            return 1  # Default fallback
        except:
            return 1
    
    def _calculate_accuracy(self, original: str, transcribed: str) -> Dict[str, float]:
        """Calculate various accuracy metrics"""
        # Normalize texts for comparison
        orig_normalized = original.lower().strip()
        trans_normalized = transcribed.lower().strip()
        
        # Word-level accuracy
        orig_words = orig_normalized.split()
        trans_words = trans_normalized.split()
        
        # Calculate word accuracy using sequence matching
        word_matches = 0
        if orig_words and trans_words:
            matcher = difflib.SequenceMatcher(None, orig_words, trans_words)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    word_matches += (i2 - i1)
        
        word_accuracy = (word_matches / len(orig_words) * 100) if orig_words else 0
        
        # Character-level accuracy using Levenshtein distance
        levenshtein_dist = self._levenshtein_distance(orig_normalized, trans_normalized)
        max_len = max(len(orig_normalized), len(trans_normalized))
        char_accuracy = ((max_len - levenshtein_dist) / max_len * 100) if max_len > 0 else 100
        
        # Overall accuracy (weighted average of word and character accuracy)
        overall_accuracy = (word_accuracy * 0.7 + char_accuracy * 0.3)
        
        return {
            "accuracy_percent": overall_accuracy,
            "word_accuracy": word_accuracy,
            "character_accuracy": char_accuracy,
            "levenshtein_distance": levenshtein_dist
        }
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def transcribe_all_files(self) -> List[Dict[str, Any]]:
        """Transcribe all audio files and return results"""
        audio_files = self.find_audio_files()
        
        if not audio_files:
            logger.warning("⚠️ No audio files found for transcription")
            return []
        
        logger.info(f"🎤 Starting transcription of {len(audio_files)} audio files...")
        
        for audio_file in audio_files:
            result = self.transcribe_audio_file(audio_file)
            self.results.append(result)
        
        return self.results
    
    def save_transcription_report(self) -> str:
        """Save comprehensive transcription report"""
        report_file = self.audio_dir / f"whisper_transcription_report_{self.timestamp}.json"
        
        # Calculate summary statistics
        successful_results = [r for r in self.results if r.get("success", False)]
        total_files = len(self.results)
        successful_files = len(successful_results)
        
        if successful_results:
            avg_accuracy = sum(r["accuracy_percent"] for r in successful_results) / len(successful_results)
            avg_word_accuracy = sum(r["word_accuracy"] for r in successful_results) / len(successful_results)
            avg_char_accuracy = sum(r["character_accuracy"] for r in successful_results) / len(successful_results)
            high_quality_count = sum(1 for r in successful_results if r["accuracy_percent"] >= 80.0)
        else:
            avg_accuracy = avg_word_accuracy = avg_char_accuracy = 0.0
            high_quality_count = 0
        
        report = {
            "transcription_summary": {
                "timestamp": self.timestamp,
                "total_audio_files": total_files,
                "successful_transcriptions": successful_files,
                "failed_transcriptions": total_files - successful_files,
                "average_accuracy_percent": avg_accuracy,
                "average_word_accuracy_percent": avg_word_accuracy,
                "average_character_accuracy_percent": avg_char_accuracy,
                "high_quality_files_80_percent_plus": high_quality_count,
                "quality_threshold_met": high_quality_count >= (total_files * 0.8)  # 80% of files should meet 80% accuracy
            },
            "original_phrases": ORIGINAL_PHRASES,
            "detailed_results": self.results,
            "audio_directory": str(self.audio_dir.absolute())
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Transcription report saved: {report_file}")
        return str(report_file)
    
    def print_transcription_summary(self):
        """Print comprehensive summary of transcription results"""
        successful_results = [r for r in self.results if r.get("success", False)]
        high_quality_count = sum(1 for r in successful_results if r["accuracy_percent"] >= 80.0)
        
        print("\n" + "="*70)
        print("🎤 WHISPER TRANSCRIPTION VERIFICATION RESULTS")
        print("="*70)
        print(f"📅 Test Date: {self.timestamp}")
        print(f"📁 Audio Directory: {self.audio_dir.absolute()}")
        print(f"🎵 Total Audio Files: {len(self.results)}")
        print(f"✅ Successful Transcriptions: {len(successful_results)}")
        print(f"❌ Failed Transcriptions: {len(self.results) - len(successful_results)}")
        
        if successful_results:
            avg_accuracy = sum(r["accuracy_percent"] for r in successful_results) / len(successful_results)
            print(f"📊 Average Accuracy: {avg_accuracy:.1f}%")
            print(f"🎯 High Quality Files (≥80%): {high_quality_count}/{len(successful_results)}")
            print(f"✅ Quality Threshold Met: {'YES' if high_quality_count >= len(successful_results) * 0.8 else 'NO'}")
            
            print("\n📋 TRANSCRIPTION RESULTS:")
            for i, result in enumerate(successful_results, 1):
                status = "✅" if result["accuracy_percent"] >= 80.0 else "⚠️"
                print(f"  {i}. {status} {result['filename']}")
                print(f"      📝 Original: '{result['original_text']}'")
                print(f"      🎤 Transcribed: '{result['transcribed_text']}'")
                print(f"      📊 Accuracy: {result['accuracy_percent']:.1f}%")
                print()
        
        print("="*70)

def main():
    """Main execution function"""
    print("🎤 LiteTTS Whisper Transcription Verification")
    print("="*60)
    
    try:
        # Initialize verifier
        verifier = WhisperTranscriptionVerifier()
        
        # Transcribe all audio files
        results = verifier.transcribe_all_files()
        
        if not results:
            print("❌ No audio files found for transcription")
            return 1
        
        # Save transcription report
        report_file = verifier.save_transcription_report()
        
        # Print summary
        verifier.print_transcription_summary()
        
        print(f"\n📊 Detailed transcription report saved to: {report_file}")
        print("✅ Whisper transcription verification completed!")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Whisper transcription verification failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
