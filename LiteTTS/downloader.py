#!/usr/bin/env python3
"""
Simple model and voice downloader for Kokoro ONNX TTS API
"""

import os
import requests
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Dynamic model and voice management - no hardcoded URLs or lists
# All models and voices are now discovered automatically from HuggingFace

def download_file(url: str, filepath: Path, description: str = "") -> bool:
    """Download a file with basic error handling"""
    try:
        # Create directory if it doesn't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file already exists
        if filepath.exists() and filepath.stat().st_size > 0:
            logger.info(f"✓ {filepath.name} already exists ({filepath.stat().st_size} bytes)")
            return True
        
        logger.info(f"📥 Downloading {description or filepath.name} from {url}")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        if downloaded % (1024 * 1024) == 0:  # Log every MB
                            logger.info(f"   Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)")
        
        logger.info(f"✅ Downloaded {filepath.name} ({downloaded} bytes)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download {filepath.name}: {e}")
        if filepath.exists():
            filepath.unlink()  # Remove partial file
        return False

def ensure_model_files() -> bool:
    """Ensure model and essential voices are downloaded using dynamic discovery"""
    from .config import config
    from .voice.downloader import VoiceDownloader
    from .models.manager import ModelManager

    success = True

    try:
        # Initialize model manager with configuration
        model_manager = ModelManager(config.paths.models_dir, config)

        # Get the configured model path
        model_path = model_manager.get_model_path(config.model.default_variant)

        # Download model if missing
        if not model_path.exists():
            logger.info(f"📥 Downloading configured model: {config.model.default_variant}")
            model_success = model_manager.download_model(config.model.default_variant)
            if not model_success:
                logger.error(f"❌ Failed to download model: {config.model.default_variant}")
                success = False
            else:
                logger.info(f"✅ Downloaded model: {config.model.default_variant}")
        else:
            logger.info(f"✓ Model already exists: {config.model.default_variant}")

        # Ensure voices directory exists and download essential voices
        voices_dir = Path(config.paths.voices_dir)
        voices_dir.mkdir(parents=True, exist_ok=True)

        # Download ALL voices using the simplified voice downloader
        voice_downloader = VoiceDownloader(str(voices_dir), config)

        # Always download ALL voices (simplified voice management)
        logger.info("🌍 Downloading ALL available voices...")
        voice_results = voice_downloader.download_all_voices()
        voice_success = any(voice_results.values())

        if not voice_success:
            logger.warning("⚠️ No voices were downloaded successfully")
            success = False
        else:
            successful_voices = [name for name, result in voice_results.items() if result]
            logger.info(f"✅ Downloaded {len(successful_voices)} voices successfully")

    except Exception as e:
        logger.error(f"❌ Failed to ensure model files: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        success = False

    return success

def get_available_voices():
    """Get list of available voices using dynamic discovery"""
    try:
        from .config import config
        from .voice.downloader import VoiceDownloader

        # Use dynamic voice discovery
        voice_downloader = VoiceDownloader(config.paths.voices_dir, config)
        return voice_downloader.get_available_voice_names()
    except Exception as e:
        logger.error(f"Failed to get available voices: {e}")
        # Fallback to empty list if discovery fails
        return []