#!/usr/bin/env python3
"""
Simplified voice combiner for Kokoro ONNX TTS API
Creates a combined voices file from individual .bin files for kokoro_onnx compatibility

DEPRECATION NOTICE: This module is deprecated in favor of individual voice loading.
Combined voice files are no longer necessary for optimal performance.
Use individual voice loading strategy for better memory usage and startup time.
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import json
import warnings

logger = logging.getLogger(__name__)

class SimplifiedVoiceCombiner:
    """
    Simplified voice combiner that creates combined voices file from individual .bin files

    DEPRECATED: This class is deprecated. Individual voice loading is now the recommended approach.
    Combined voice files provide no performance benefit and increase memory usage.
    """

    def __init__(self, voices_dir: str = "LiteTTS/voices", config=None):
        # Issue deprecation warning
        warnings.warn(
            "SimplifiedVoiceCombiner is deprecated. Use individual voice loading strategy instead. "
            "Combined voice files are no longer necessary for optimal performance.",
            DeprecationWarning,
            stacklevel=2
        )

        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self.config = config

        # Check if combined file usage is disabled in configuration
        if config and hasattr(config, 'voice') and not config.voice.use_combined_file:
            logger.info("Combined voice file usage is disabled in configuration. Skipping combiner initialization.")
            self.disabled = True
            return

        self.disabled = False
        self.combined_file = self.voices_dir / "combined_voices.npz"
        self.voice_index_file = self.voices_dir / "voice_index.json"

        logger.warning("SimplifiedVoiceCombiner is deprecated. Consider using individual voice loading strategy.")
    
    def _load_individual_voice(self, voice_name: str) -> Optional[np.ndarray]:
        """Load an individual voice file"""
        voice_file = self.voices_dir / f"{voice_name}.bin"

        if not voice_file.exists():
            logger.warning(f"Voice file not found: {voice_file}")
            return None

        try:
            # Load as float32 array
            voice_data = np.fromfile(voice_file, dtype=np.float32)

            # The kokoro_onnx library expects voice data in a specific format
            # Each voice should be a 2D array with shape (N, 256) for style vectors
            # Common formats: (510, 256), (512, 256), or single vector (256,)

            if len(voice_data) == 510 * 256:
                # Standard format: 510 style vectors of 256 dimensions each
                voice_data = voice_data.reshape(510, 256)
                logger.debug(f"✅ Voice {voice_name} loaded with shape: {voice_data.shape}")
            elif len(voice_data) == 512 * 256:
                # Alternative format: 512 style vectors of 256 dimensions each
                voice_data = voice_data.reshape(512, 256)
                logger.debug(f"✅ Voice {voice_name} loaded with shape: {voice_data.shape} (512-vector format)")
            elif len(voice_data) == 256:
                # Single style vector - expand to expected format
                voice_data = voice_data.reshape(1, 256)
                # Repeat to create 510 style vectors (this is a fallback)
                voice_data = np.repeat(voice_data, 510, axis=0)
                logger.warning(f"⚠️ Voice {voice_name} had single vector, expanded to shape: {voice_data.shape}")
            elif len(voice_data) % 256 == 0 and len(voice_data) >= 256:
                # Generic format: any multiple of 256 that could be reshaped
                num_vectors = len(voice_data) // 256
                voice_data = voice_data.reshape(num_vectors, 256)
                logger.info(f"✅ Voice {voice_name} loaded with shape: {voice_data.shape} ({num_vectors}-vector format)")
            else:
                logger.error(f"❌ Unexpected voice data size for {voice_name}: {len(voice_data)} (expected multiple of 256)")
                return None

            # Ensure the data is contiguous and in the right format
            voice_data = np.ascontiguousarray(voice_data, dtype=np.float32)

            return voice_data

        except Exception as e:
            logger.error(f"Failed to load voice {voice_name}: {e}")
            return None
    
    def _get_available_voices(self) -> List[str]:
        """Get list of available voice files"""
        voice_files = list(self.voices_dir.glob("*.bin"))
        voice_names = [f.stem for f in voice_files]
        return sorted(voice_names)
    
    def create_combined_file(self) -> bool:
        """
        Create combined voices file from individual .bin files

        DEPRECATED: This method is deprecated. Individual voice loading is recommended.
        """
        # Check if disabled by configuration
        if self.disabled:
            logger.info("Combined voice file creation is disabled by configuration. Skipping.")
            return True  # Return True to indicate no error, just skipped

        # Issue deprecation warning
        logger.warning("create_combined_file() is deprecated. Individual voice loading is recommended.")

        try:
            available_voices = self._get_available_voices()

            if not available_voices:
                logger.error("No voice files found to combine")
                return False

            logger.info(f"🔄 Creating combined voices file from {len(available_voices)} individual voices...")
            
            # Load all voice data
            voice_data_dict = {}
            voice_arrays = []
            voice_index = {}
            
            for i, voice_name in enumerate(available_voices):
                voice_data = self._load_individual_voice(voice_name)
                if voice_data is not None:
                    voice_data_dict[voice_name] = voice_data
                    voice_arrays.append(voice_data)
                    voice_index[voice_name] = i
                    logger.debug(f"✅ Loaded voice: {voice_name}")
                else:
                    logger.warning(f"⚠️ Failed to load voice: {voice_name}")
            
            if not voice_arrays:
                logger.error("No valid voice data loaded")
                return False
            
            # Create NPZ file with individual voice arrays as separate keys
            # This is the format expected by kokoro_onnx
            npz_data = {}
            for voice_name, voice_data in voice_data_dict.items():
                # Ensure each voice array has the correct shape and dtype
                # Accept common formats: (510, 256), (512, 256), or other (N, 256) shapes
                if len(voice_data.shape) != 2 or voice_data.shape[1] != 256:
                    logger.warning(f"⚠️ Voice {voice_name} has unexpected shape {voice_data.shape}, expected (N, 256)")
                else:
                    logger.debug(f"✅ Voice {voice_name} has valid shape: {voice_data.shape}")

                # Store with proper format for kokoro_onnx
                npz_data[voice_name] = np.ascontiguousarray(voice_data, dtype=np.float32)
                logger.debug(f"✅ Added voice {voice_name} to NPZ with shape: {voice_data.shape}")

            logger.info(f"📦 Creating NPZ with {len(npz_data)} individual voice arrays")
            logger.info(f"🔍 Voice shapes: {[(name, data.shape) for name, data in list(npz_data.items())[:3]]}")

            # Save combined file with individual voice keys
            np.savez_compressed(self.combined_file, **npz_data)
            
            # Save voice index
            with open(self.voice_index_file, 'w') as f:
                json.dump(voice_index, f, indent=2)
            
            logger.info(f"✅ Created combined voices file: {self.combined_file}")
            logger.info(f"📋 Voice index saved: {self.voice_index_file}")
            logger.info(f"🎭 Combined {len(voice_arrays)} voices successfully")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to create combined voices file: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def ensure_combined_file(self) -> str:
        """Ensure combined voices file exists and is current"""
        # Check if combined file exists
        if not self.combined_file.exists():
            logger.info("📦 Combined voices file not found, creating...")
            if not self.create_combined_file():
                raise RuntimeError("Failed to create combined voices file")
        else:
            # Check if we need to update (if any .bin file is newer than combined file)
            combined_mtime = self.combined_file.stat().st_mtime
            
            needs_update = False
            for voice_file in self.voices_dir.glob("*.bin"):
                if voice_file.stat().st_mtime > combined_mtime:
                    needs_update = True
                    break
            
            if needs_update:
                logger.info("🔄 Voice files updated, recreating combined file...")
                if not self.create_combined_file():
                    raise RuntimeError("Failed to update combined voices file")
            else:
                logger.info("✅ Combined voices file is current")
        
        return str(self.combined_file)
    
    def get_voice_list(self) -> List[str]:
        """Get list of voices in the combined file"""
        if self.voice_index_file.exists():
            try:
                with open(self.voice_index_file, 'r') as f:
                    voice_index = json.load(f)
                return sorted(voice_index.keys())
            except Exception as e:
                logger.warning(f"Failed to load voice index: {e}")
        
        # Fallback to scanning .bin files
        return self._get_available_voices()
    
    def get_voice_count(self) -> int:
        """Get number of voices in the combined file"""
        return len(self.get_voice_list())
