"""
Base ASR client interface for audio quality testing
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseASRClient(ABC):
    """
    Base class for ASR (Automatic Speech Recognition) clients
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.timeout = self.config.get("timeout", 30)
        self.language = self.config.get("language", "en-US")
        self.model = self.config.get("model", "general")

    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> tuple[str, float]:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Audio data in bytes (WAV format)
            
        Returns:
            Tuple of (transcription, confidence_score)
        """

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the ASR service is available and properly configured
        
        Returns:
            True if service is available, False otherwise
        """

    def get_service_info(self) -> dict[str, Any]:
        """
        Get information about the ASR service
        
        Returns:
            Dictionary with service information
        """
        return {
            "service_name": self.__class__.__name__,
            "language": self.language,
            "model": self.model,
            "timeout": self.timeout,
            "available": self.is_available()
        }
