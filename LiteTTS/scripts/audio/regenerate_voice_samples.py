#!/usr/bin/env python3
"""
Voice Sample Regeneration and Time-Stretching Script
Regenerates all voice samples using the current TTS system and creates time-stretched versions
"""

import os
import sys
import json
import asyncio
import aiohttp
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceSampleGenerator:
    def __init__(self, api_base_url: str = "http://localhost:8354"):
        self.api_base_url = api_base_url
        self.samples_dir = Path("samples")
        self.time_stretched_dir = self.samples_dir / "time-stretched"
        self.sample_text = "Hello! This is a sample of the Kokoro ONNX TTS API voice synthesis system. The quick brown fox jumps over the lazy dog."
        
        # Ensure directories exist
        self.samples_dir.mkdir(exist_ok=True)
        self.time_stretched_dir.mkdir(exist_ok=True)
        
        # Voice categories for organization
        self.voice_categories = {
            "American Female": ["af_heart", "af_bella", "af_sarah", "af_jessica", "af_nicole", 
                              "af_nova", "af_sky", "af_river", "af_alloy", "af_aoede", "af_kore"],
            "American Male": ["am_adam", "am_onyx", "am_echo", "am_liam", "am_michael", 
                            "am_eric", "am_fenrir", "am_puck", "am_santa"],
            "British Female": ["bf_alice", "bf_emma", "bf_isabella", "bf_lily"],
            "British Male": ["bm_daniel", "bm_george", "bm_lewis"],
            "International": ["ff_siwis", "ef_dora", "em_alex", "em_santa", "hf_alpha", 
                            "hm_omega", "hm_psi", "if_sara", "im_nicola", "jf_alpha", 
                            "jf_gongitsune", "jf_nezumi", "jf_tebukuro", "jm_kumo", 
                            "pf_dora", "pm_alex", "pm_santa", "zf_xiaobei", "zf_xiaoni", 
                            "zf_xiaoxiao", "zf_xiaoyi", "zm_yunxi", "zm_yunxia", "zm_yunyang"]
        }

    async def get_available_voices(self) -> List[str]:
        """Get list of available voices from the API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/v1/voices") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [voice["id"] for voice in data.get("data", [])]
                    else:
                        logger.error(f"Failed to get voices: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []

    async def generate_voice_sample(self, voice: str) -> bool:
        """Generate a voice sample for the specified voice"""
        try:
            payload = {
                "model": "kokoro",
                "input": self.sample_text,
                "voice": voice,
                "response_format": "mp3",
                "speed": 1.0,
                "volume_multiplier": 1.0
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/v1/audio/speech",
                    json=payload
                ) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        output_file = self.samples_dir / f"{voice}.mp3"
                        
                        with open(output_file, "wb") as f:
                            f.write(audio_data)
                        
                        logger.info(f"✅ Generated sample for {voice}")
                        return True
                    else:
                        logger.error(f"❌ Failed to generate sample for {voice}: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Error generating sample for {voice}: {e}")
            return False

    def create_time_stretched_version(self, voice: str, stretch_factor: float = 0.8) -> bool:
        """Create time-stretched version of a voice sample using ffmpeg"""
        try:
            input_file = self.samples_dir / f"{voice}.mp3"
            output_file = self.time_stretched_dir / f"{voice}_stretched_{stretch_factor}x.mp3"
            
            if not input_file.exists():
                logger.error(f"❌ Input file not found: {input_file}")
                return False
            
            # Use ffmpeg to create time-stretched version
            cmd = [
                "ffmpeg", "-y", "-i", str(input_file),
                "-filter:a", f"atempo={stretch_factor}",
                "-c:a", "mp3", str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Created time-stretched version for {voice} ({stretch_factor}x)")
                return True
            else:
                logger.error(f"❌ Failed to create time-stretched version for {voice}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating time-stretched version for {voice}: {e}")
            return False

    def create_restored_version(self, voice: str, original_stretch: float = 0.8) -> bool:
        """Create restored version from time-stretched audio"""
        try:
            stretched_file = self.time_stretched_dir / f"{voice}_stretched_{original_stretch}x.mp3"
            restored_file = self.time_stretched_dir / f"{voice}_restored_from_{original_stretch}x.mp3"
            
            if not stretched_file.exists():
                logger.error(f"❌ Stretched file not found: {stretched_file}")
                return False
            
            # Restore by applying inverse stretch factor
            restore_factor = 1.0 / original_stretch
            
            cmd = [
                "ffmpeg", "-y", "-i", str(stretched_file),
                "-filter:a", f"atempo={restore_factor}",
                "-c:a", "mp3", str(restored_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Created restored version for {voice} (from {original_stretch}x)")
                return True
            else:
                logger.error(f"❌ Failed to create restored version for {voice}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating restored version for {voice}: {e}")
            return False

    async def regenerate_all_samples(self):
        """Regenerate all voice samples and create time-stretched versions"""
        logger.info("🚀 Starting voice sample regeneration...")
        
        # Get all available voices
        all_voices = []
        for category_voices in self.voice_categories.values():
            all_voices.extend(category_voices)
        
        # Remove duplicates
        all_voices = list(set(all_voices))
        
        logger.info(f"📊 Found {len(all_voices)} voices to process")
        
        # Generate original samples
        successful_generations = 0
        for voice in all_voices:
            if await self.generate_voice_sample(voice):
                successful_generations += 1
        
        logger.info(f"✅ Successfully generated {successful_generations}/{len(all_voices)} voice samples")
        
        # Create time-stretched versions
        stretch_factors = [0.6, 0.8, 1.2, 1.4]  # Various stretch factors for testing
        
        for voice in all_voices:
            for factor in stretch_factors:
                self.create_time_stretched_version(voice, factor)
                
                # Create restored version for quality comparison
                if factor < 1.0:  # Only for compressed versions
                    self.create_restored_version(voice, factor)
        
        logger.info("🎉 Voice sample regeneration and time-stretching complete!")
        
        # Generate summary report
        self.generate_summary_report()

    def generate_summary_report(self):
        """Generate a summary report of all generated samples"""
        report_file = self.samples_dir / "SAMPLE_GENERATION_REPORT.md"
        
        original_samples = list(self.samples_dir.glob("*.mp3"))
        stretched_samples = list(self.time_stretched_dir.glob("*_stretched_*.mp3"))
        restored_samples = list(self.time_stretched_dir.glob("*_restored_*.mp3"))
        
        with open(report_file, "w") as f:
            f.write("# Voice Sample Generation Report\n\n")
            f.write(f"**Generated on:** {asyncio.get_event_loop().time()}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Original Samples:** {len(original_samples)}\n")
            f.write(f"- **Time-Stretched Samples:** {len(stretched_samples)}\n")
            f.write(f"- **Restored Samples:** {len(restored_samples)}\n\n")
            
            f.write("## Sample Text Used\n\n")
            f.write(f"```\n{self.sample_text}\n```\n\n")
            
            f.write("## Voice Categories\n\n")
            for category, voices in self.voice_categories.items():
                f.write(f"### {category}\n")
                for voice in voices:
                    sample_file = self.samples_dir / f"{voice}.mp3"
                    status = "✅" if sample_file.exists() else "❌"
                    f.write(f"- {status} {voice}\n")
                f.write("\n")
        
        logger.info(f"📋 Generated summary report: {report_file}")

async def main():
    """Main function to run the voice sample regeneration"""
    generator = VoiceSampleGenerator()
    await generator.regenerate_all_samples()

if __name__ == "__main__":
    asyncio.run(main())
