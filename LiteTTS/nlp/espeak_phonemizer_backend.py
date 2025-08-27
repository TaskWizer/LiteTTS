#!/usr/bin/env python3
"""
eSpeak phonemizer backend for Kokoro TTS
Provides text-to-phoneme conversion using eSpeak library
"""

import logging
import subprocess
import shutil
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import threading
import json

logger = logging.getLogger(__name__)

@dataclass
class EspeakConfig:
    """Configuration for eSpeak backend"""
    enabled: bool = False
    voice: str = "en-us"
    phoneme_format: str = "ascii"  # "ascii" or "ipa"
    punctuation_mode: str = "some"  # "none", "all", "some"
    cache_enabled: bool = True
    cache_size: int = 10000
    fallback_to_existing: bool = True
    espeak_path: Optional[str] = None
    timeout_seconds: float = 5.0

@dataclass
class PhonemeResult:
    """Result of phonemization"""
    phonemes: str
    success: bool
    error_message: Optional[str] = None
    processing_time: float = 0.0
    cache_hit: bool = False

class EspeakPhonemizerBackend:
    """
    eSpeak-based phonemizer backend for text-to-phoneme conversion

    This backend uses the eSpeak speech synthesis library to convert
    text to phonemes, providing better symbol handling and pronunciation
    accuracy than basic text processing.
    """

    def __init__(self, config: EspeakConfig):
        self.config = config
        self.cache: Dict[str, PhonemeResult] = {}
        self.cache_lock = threading.Lock()
        self.espeak_available = False
        self.espeak_path = None

        # Initialize eSpeak if enabled
        if self.config.enabled:
            self._initialize_espeak()

    def _initialize_espeak(self) -> bool:
        """Initialize eSpeak library"""
        logger.info("Initializing eSpeak phonemizer backend...")

        # Find eSpeak executable
        espeak_path = self.config.espeak_path or shutil.which("espeak")
        if not espeak_path:
            espeak_path = shutil.which("espeak-ng")

        if not espeak_path:
            logger.warning("eSpeak not found in PATH. eSpeak backend disabled.")
            return False

        self.espeak_path = espeak_path

        # Test eSpeak functionality
        try:
            result = subprocess.run(
                [espeak_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5.0
            )

            if result.returncode == 0:
                logger.info(f"eSpeak found: {espeak_path}")
                logger.debug(f"eSpeak version: {result.stdout.strip()}")
                self.espeak_available = True
                return True
            else:
                logger.warning(f"eSpeak test failed: {result.stderr}")
                return False

        except Exception as e:
            logger.warning(f"Failed to initialize eSpeak: {e}")
            return False

    def is_available(self) -> bool:
        """Check if eSpeak backend is available"""
        return self.espeak_available and self.config.enabled

    def phonemize(self, text: str) -> PhonemeResult:
        """
        Convert text to phonemes using eSpeak

        Args:
            text: Input text to phonemize

        Returns:
            PhonemeResult with phonemes and metadata
        """
        if not self.is_available():
            return PhonemeResult(
                phonemes="",
                success=False,
                error_message="eSpeak backend not available"
            )

        # Check cache first
        if self.config.cache_enabled:
            cache_key = self._get_cache_key(text)
            with self.cache_lock:
                if cache_key in self.cache:
                    result = self.cache[cache_key]
                    result.cache_hit = True
                    logger.debug(f"eSpeak cache hit for: {text[:30]}...")
                    return result

        # Phonemize using eSpeak
        start_time = time.perf_counter()
        result = self._espeak_phonemize(text)
        result.processing_time = time.perf_counter() - start_time

        # Cache result
        if self.config.cache_enabled and result.success:
            with self.cache_lock:
                if len(self.cache) >= self.config.cache_size:
                    # Simple LRU: remove oldest entries
                    oldest_keys = list(self.cache.keys())[:len(self.cache) // 4]
                    for key in oldest_keys:
                        del self.cache[key]

                self.cache[cache_key] = result

        return result

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return f"{text}:{self.config.voice}:{self.config.phoneme_format}:{self.config.punctuation_mode}"

    def _espeak_phonemize(self, text: str) -> PhonemeResult:
        """Perform actual eSpeak phonemization"""
        try:
            # Build eSpeak command
            cmd = [self.espeak_path]

            # Set voice
            cmd.extend(["-v", self.config.voice])

            # Set phoneme output mode
            if self.config.phoneme_format == "ipa":
                cmd.append("--ipa")
            else:
                cmd.append("-x")  # ASCII phonemes

            # Set punctuation mode
            if self.config.punctuation_mode == "all":
                cmd.append("--punct")
            elif self.config.punctuation_mode == "some":
                cmd.append("--punct=some")
            # "none" is default, no flag needed

            # Quiet mode (no audio output)
            cmd.append("-q")

            # Add text
            cmd.append(text)

            # Execute eSpeak
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds
            )

            if result.returncode == 0:
                phonemes = result.stdout.strip()
                # Clean up phoneme output
                phonemes = self._clean_phoneme_output(phonemes)

                return PhonemeResult(
                    phonemes=phonemes,
                    success=True
                )
            else:
                error_msg = result.stderr.strip() or "eSpeak returned non-zero exit code"
                logger.warning(f"eSpeak error: {error_msg}")
                return PhonemeResult(
                    phonemes="",
                    success=False,
                    error_message=error_msg
                )

        except subprocess.TimeoutExpired:
            error_msg = f"eSpeak timeout after {self.config.timeout_seconds}s"
            logger.warning(error_msg)
            return PhonemeResult(
                phonemes="",
                success=False,
                error_message=error_msg
            )
        except Exception as e:
            error_msg = f"eSpeak execution failed: {e}"
            logger.warning(error_msg)
            return PhonemeResult(
                phonemes="",
                success=False,
                error_message=error_msg
            )

    def _clean_phoneme_output(self, phonemes: str) -> str:
        """Clean and normalize phoneme output"""
        # Remove extra whitespace
        phonemes = " ".join(phonemes.split())

        # Handle specific eSpeak output formatting
        if self.config.phoneme_format == "ascii":
            # Clean ASCII phoneme output
            phonemes = phonemes.replace("_:", "")  # Remove stress markers if not needed
            phonemes = phonemes.replace("'", "")   # Remove primary stress if not needed

        return phonemes

    def get_statistics(self) -> Dict[str, Any]:
        """Get backend statistics"""
        with self.cache_lock:
            cache_size = len(self.cache)

        return {
            "backend": "espeak",
            "available": self.is_available(),
            "espeak_path": self.espeak_path,
            "cache_size": cache_size,
            "cache_enabled": self.config.cache_enabled,
            "voice": self.config.voice,
            "phoneme_format": self.config.phoneme_format,
            "punctuation_mode": self.config.punctuation_mode
        }

    def clear_cache(self) -> None:
        """Clear phoneme cache"""
        with self.cache_lock:
            self.cache.clear()
        logger.info("eSpeak phoneme cache cleared")

    def test_phonemization(self, test_text: str = "Hello, world! How are you?") -> Dict[str, Any]:
        """Test phonemization with sample text"""
        logger.info(f"Testing eSpeak phonemization with: '{test_text}'")

        result = self.phonemize(test_text)

        test_result = {
            "test_text": test_text,
            "success": result.success,
            "phonemes": result.phonemes,
            "processing_time": result.processing_time,
            "error_message": result.error_message,
            "backend_available": self.is_available(),
            "config": {
                "voice": self.config.voice,
                "phoneme_format": self.config.phoneme_format,
                "punctuation_mode": self.config.punctuation_mode
            }
        }

        if result.success:
            logger.info(f"✅ eSpeak test successful: '{result.phonemes}'")
        else:
            logger.warning(f"❌ eSpeak test failed: {result.error_message}")

        return test_result

# Factory function for easy integration
def create_espeak_backend(config_dict: Dict[str, Any]) -> EspeakPhonemizerBackend:
    """Create eSpeak backend from configuration dictionary"""
    config = EspeakConfig(
        enabled=config_dict.get("enabled", False),
        voice=config_dict.get("voice", "en-us"),
        phoneme_format=config_dict.get("phoneme_format", "ascii"),
        punctuation_mode=config_dict.get("punctuation_mode", "some"),
        cache_enabled=config_dict.get("cache_enabled", True),
        cache_size=config_dict.get("cache_size", 10000),
        fallback_to_existing=config_dict.get("fallback_to_existing", True),
        espeak_path=config_dict.get("espeak_path"),
        timeout_seconds=config_dict.get("timeout_seconds", 5.0)
    )

    return EspeakPhonemizerBackend(config)