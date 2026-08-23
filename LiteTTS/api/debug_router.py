#!/usr/bin/env python3
"""
Debug endpoints for TTS pronunciation debugging
"""

import logging
import time
from typing import Any

from fastapi import APIRouter

logger = logging.getLogger(__name__)


class DebugRouter:
    """Debug API router for pronunciation troubleshooting"""

    def __init__(self, config: Any):
        self.config = config
        self.router = APIRouter()
        self._setup_routes()
        logger.info("Debug API Router initialized")

    def _setup_routes(self):
        """Setup debug routes"""

        @self.router.get("/ping")
        async def ping():
            """Simple ping to test routing"""
            return {"status": "ok", "timestamp": time.time()}

        @self.router.post("/phonetics")
        async def debug_phonetics(text: str, voice: str = "af_heart"):
            """Show text processing pipeline stages."""
            result = {"input": text, "voice": voice, "timestamp": time.time()}

            try:
                from LiteTTS.text.phonemizer_preprocessor import PhonemizationPreprocessor

                prep = PhonemizationPreprocessor()
                prep_result = prep.preprocess_text(text)
                result["phonemizer"] = {
                    "output": prep_result.processed_text,
                    "confidence": prep_result.confidence_score,
                }
            except Exception as e:
                result["phonemizer"] = {"error": str(e)}

            try:
                from LiteTTS.nlp.clean_text_normalizer import CleanTextNormalizer

                clean = CleanTextNormalizer()
                clean_result = clean.normalize_text(text)
                result["clean_normalizer"] = {"output": clean_result.processed_text}
            except Exception as e:
                result["clean_normalizer"] = {"error": str(e)}

            return result

        @self.router.post("/validate")
        async def debug_validate(text: str, voice: str = "af_heart"):
            """Generate audio and transcribe with Whisper for validation."""
            import tempfile
            from pathlib import Path

            import requests

            result = {"input": text, "voice": voice, "timestamp": time.time()}

            try:
                resp = requests.post(
                    "http://localhost:8354/v1/audio/speech",
                    json={"input": text, "voice": voice, "response_format": "mp3"},
                    timeout=30,
                )
                result["tts_status"] = resp.status_code

                if resp.status_code == 200:
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                        f.write(resp.content)
                        audio_path = Path(f.name)

                    try:
                        from LiteTTS.backends.whisper_optimized import OptimizedWhisperProcessor

                        whisper = OptimizedWhisperProcessor()
                        whisper_result = whisper.transcribe(str(audio_path))
                        result["transcription"] = (
                            whisper_result.text
                            if hasattr(whisper_result, "text")
                            else str(whisper_result)
                        )
                    finally:
                        audio_path.unlink(missing_ok=True)
            except Exception as e:
                result["error"] = str(e)

            return result

        @self.router.get("/pipeline")
        async def debug_pipeline():
            """Get pipeline info."""
            return {
                "processors": [
                    "unified_text_processor",
                    "phonemizer_preprocessor",
                    "clean_text_normalizer",
                    "text_normalizer",
                ]
            }

    def get_router(self) -> APIRouter:
        """Get the configured router"""
        return self.router
