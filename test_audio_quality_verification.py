#!/usr/bin/env python3
"""
Audio Quality Verification Script for LiteTTS
Generates test audio files and provides comprehensive evidence of audio quality
"""

import os
import sys
import time
import json
import wave
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test phrases as specified in requirements
TEST_PHRASES = [
    "Hello world",
    "This is a test", 
    "The quick brown fox jumps over the lazy dog",
    "Testing audio quality",
    "LiteTTS verification"
]

# Default voice for testing
DEFAULT_VOICE = "af_heart"

class AudioQualityVerifier:
    """Comprehensive audio quality verification system"""
    
    def __init__(self, output_dir: str = "test_audio_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        logger.info(f"🎯 Audio Quality Verifier initialized")
        logger.info(f"📁 Output directory: {self.output_dir.absolute()}")
    
    def generate_test_audio_files(self) -> List[Dict[str, Any]]:
        """Generate all test audio files and capture metadata"""
        logger.info("🎵 Starting audio file generation...")
        
        try:
            # Import LiteTTS components
            from LiteTTS.tts import TTSSynthesizer
            from LiteTTS.config import config
            from LiteTTS.models import TTSRequest, TTSConfiguration
            
            # Create TTSConfiguration
            tts_config = TTSConfiguration(
                model_path=config.tts.model_path,
                voices_path=config.tts.voices_path,
                device=config.tts.device,
                sample_rate=config.tts.sample_rate,
                chunk_size=getattr(config.tts, 'chunk_size', 100),
                cache_size=getattr(config.cache, 'max_size', 1000),
                max_text_length=getattr(config.tts, 'max_text_length', 1000),
                default_voice=config.tts.default_voice
            )
            
            # Initialize synthesizer
            synthesizer = TTSSynthesizer(tts_config)
            logger.info("✅ TTS Synthesizer initialized successfully")
            
            # Generate audio for each test phrase
            for i, phrase in enumerate(TEST_PHRASES, 1):
                logger.info(f"🎵 Generating audio {i}/{len(TEST_PHRASES)}: '{phrase}'")
                
                try:
                    result = self._generate_single_audio_file(synthesizer, phrase, i)
                    self.results.append(result)
                    
                    # Log success with metadata
                    logger.info(f"✅ Audio {i} generated successfully:")
                    logger.info(f"   📁 File: {result['file_path']}")
                    logger.info(f"   📏 Size: {result['file_size_bytes']} bytes")
                    logger.info(f"   ⏱️  Duration: {result['duration_seconds']:.2f}s")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to generate audio {i}: {e}")
                    error_result = {
                        "phrase_id": i,
                        "phrase": phrase,
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    self.results.append(error_result)
            
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Critical error in audio generation: {e}")
            raise
    
    def _generate_single_audio_file(self, synthesizer, phrase: str, phrase_id: int) -> Dict[str, Any]:
        """Generate a single audio file and capture all metadata"""
        start_time = time.time()
        
        # Create filename with timestamp and phrase identifier
        safe_phrase = "".join(c for c in phrase if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_phrase = safe_phrase.replace(' ', '_')[:20]  # Limit length
        filename = f"test_audio_{self.timestamp}_{phrase_id:02d}_{safe_phrase}.wav"
        file_path = self.output_dir / filename
        
        # Create TTS request
        from LiteTTS.models import TTSRequest
        request = TTSRequest(
            input=phrase,
            voice=DEFAULT_VOICE,
            response_format="wav",
            speed=1.0,
            stream=False,
            volume_multiplier=1.0
        )
        
        # Generate audio
        audio_segment = synthesizer.synthesize(request)
        generation_time = time.time() - start_time
        
        # Validate audio segment
        if not hasattr(audio_segment, 'audio_data'):
            raise ValueError("Invalid audio segment - missing audio_data attribute")
        
        # Convert to WAV format and save
        from LiteTTS.audio.processor import AudioProcessor
        audio_processor = AudioProcessor()
        audio_bytes = audio_processor.convert_format(audio_segment, "wav")
        
        # Validate audio data size
        if len(audio_bytes) < 100:
            raise ValueError(f"Generated audio too small ({len(audio_bytes)} bytes)")
        
        # Write to file
        with open(file_path, 'wb') as f:
            f.write(audio_bytes)
        
        # Get audio duration using wave module
        duration_seconds = self._get_audio_duration(file_path)
        
        # Calculate RTF (Real-Time Factor)
        rtf = generation_time / max(duration_seconds, 0.1)
        
        return {
            "phrase_id": phrase_id,
            "phrase": phrase,
            "file_path": str(file_path.absolute()),
            "filename": filename,
            "file_size_bytes": len(audio_bytes),
            "duration_seconds": duration_seconds,
            "generation_time_seconds": generation_time,
            "rtf": rtf,
            "voice": DEFAULT_VOICE,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_audio_duration(self, file_path: Path) -> float:
        """Get audio duration in seconds using wave module"""
        try:
            with wave.open(str(file_path), 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
                return duration
        except Exception as e:
            logger.warning(f"Could not determine audio duration: {e}")
            return 0.0
    
    def save_results_report(self) -> str:
        """Save comprehensive results report"""
        report_file = self.output_dir / f"audio_quality_report_{self.timestamp}.json"
        
        # Calculate summary statistics
        successful_results = [r for r in self.results if r.get("success", False)]
        total_files = len(self.results)
        successful_files = len(successful_results)
        
        if successful_results:
            avg_file_size = sum(r["file_size_bytes"] for r in successful_results) / len(successful_results)
            avg_duration = sum(r["duration_seconds"] for r in successful_results) / len(successful_results)
            avg_rtf = sum(r["rtf"] for r in successful_results) / len(successful_results)
        else:
            avg_file_size = avg_duration = avg_rtf = 0.0
        
        report = {
            "test_summary": {
                "timestamp": self.timestamp,
                "total_test_phrases": total_files,
                "successful_generations": successful_files,
                "failed_generations": total_files - successful_files,
                "success_rate_percent": (successful_files / total_files * 100) if total_files > 0 else 0,
                "average_file_size_bytes": avg_file_size,
                "average_duration_seconds": avg_duration,
                "average_rtf": avg_rtf
            },
            "test_phrases": TEST_PHRASES,
            "detailed_results": self.results,
            "output_directory": str(self.output_dir.absolute())
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Results report saved: {report_file}")
        return str(report_file)
    
    def print_summary(self):
        """Print comprehensive summary of results"""
        successful_results = [r for r in self.results if r.get("success", False)]
        
        print("\n" + "="*60)
        print("🎯 AUDIO QUALITY VERIFICATION RESULTS")
        print("="*60)
        print(f"📅 Test Date: {self.timestamp}")
        print(f"📁 Output Directory: {self.output_dir.absolute()}")
        print(f"🎵 Total Test Phrases: {len(self.results)}")
        print(f"✅ Successful Generations: {len(successful_results)}")
        print(f"❌ Failed Generations: {len(self.results) - len(successful_results)}")
        
        if successful_results:
            print(f"📊 Success Rate: {len(successful_results)/len(self.results)*100:.1f}%")
            print(f"📏 Average File Size: {sum(r['file_size_bytes'] for r in successful_results)/len(successful_results):.0f} bytes")
            print(f"⏱️  Average Duration: {sum(r['duration_seconds'] for r in successful_results)/len(successful_results):.2f}s")
            print(f"🚀 Average RTF: {sum(r['rtf'] for r in successful_results)/len(successful_results):.3f}")
            
            print("\n📋 GENERATED FILES:")
            for result in successful_results:
                print(f"  {result['phrase_id']:2d}. {result['filename']}")
                print(f"      📝 Phrase: '{result['phrase']}'")
                print(f"      📏 Size: {result['file_size_bytes']} bytes")
                print(f"      ⏱️  Duration: {result['duration_seconds']:.2f}s")
                print(f"      🚀 RTF: {result['rtf']:.3f}")
                print()
        
        print("="*60)

def main():
    """Main execution function"""
    print("🎯 LiteTTS Audio Quality Verification")
    print("="*50)
    
    try:
        # Initialize verifier
        verifier = AudioQualityVerifier()
        
        # Generate test audio files
        results = verifier.generate_test_audio_files()
        
        # Save results report
        report_file = verifier.save_results_report()
        
        # Print summary
        verifier.print_summary()
        
        print(f"\n📊 Detailed report saved to: {report_file}")
        print("✅ Audio quality verification completed!")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Audio quality verification failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
