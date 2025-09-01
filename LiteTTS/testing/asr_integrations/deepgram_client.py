"""
Deepgram ASR client for audio quality testing
"""

import asyncio
import aiohttp
import tempfile
import json
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import logging

from .base_asr_client import BaseASRClient

logger = logging.getLogger(__name__)


class DeepgramASRClient(BaseASRClient):
    """
    Deepgram ASR client implementation
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = api_key
        self.base_url = "https://api.deepgram.com/v1/listen"
        
        # Deepgram-specific configuration
        self.model = self.config.get("model", "nova-2")
        self.tier = self.config.get("tier", "enhanced")
        self.punctuate = self.config.get("punctuate", True)
        self.diarize = self.config.get("diarize", False)
        self.smart_format = self.config.get("smart_format", True)
        
    async def transcribe(self, audio_data: bytes) -> Tuple[str, float]:
        """
        Transcribe audio using Deepgram API
        """
        if not self.is_available():
            raise Exception("Deepgram API key not configured")
        
        try:
            # Prepare request parameters
            params = {
                "model": self.model,
                "tier": self.tier,
                "language": self.language,
                "punctuate": self.punctuate,
                "smart_format": self.smart_format,
                "diarize": self.diarize
            }
            
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/wav"
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    params=params,
                    headers=headers,
                    data=audio_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._extract_transcription(result)
                    else:
                        error_text = await response.text()
                        raise Exception(f"Deepgram API error {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"Deepgram transcription error: {e}")
            return "", 0.0
    
    def _extract_transcription(self, result: Dict[str, Any]) -> Tuple[str, float]:
        """
        Extract transcription and confidence from Deepgram response
        """
        try:
            results = result.get("results", {})
            channels = results.get("channels", [])
            
            if not channels:
                return "", 0.0
            
            alternatives = channels[0].get("alternatives", [])
            if not alternatives:
                return "", 0.0
            
            best_alternative = alternatives[0]
            transcript = best_alternative.get("transcript", "")
            confidence = best_alternative.get("confidence", 0.0)
            
            return transcript, confidence
            
        except Exception as e:
            logger.error(f"Error extracting Deepgram transcription: {e}")
            return "", 0.0
    
    def is_available(self) -> bool:
        """
        Check if Deepgram API is available
        """
        return bool(self.api_key)
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get Deepgram service information
        """
        info = super().get_service_info()
        info.update({
            "service_name": "Deepgram",
            "model": self.model,
            "tier": self.tier,
            "features": {
                "punctuate": self.punctuate,
                "smart_format": self.smart_format,
                "diarize": self.diarize
            }
        })
        return info
