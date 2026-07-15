#!/usr/bin/env python3
"""
Unit tests for dynamic voice manager
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from LiteTTS.voice.dynamic_manager import DynamicVoiceManager, VoiceEmbedding


class TestDynamicVoiceManager:
    """Test cases for DynamicVoiceManager"""

    @pytest.fixture
    def mock_manager(self):
        """Create manager with mocked dependencies"""
        with patch('LiteTTS.voice.dynamic_manager.VoiceDownloader'), \
             patch('LiteTTS.voice.dynamic_manager.VoiceDiscovery') as mock_discovery:
            mock_discovery_instance = Mock()
            mock_discovery_instance.get_available_voices.return_value = []
            mock_discovery_instance.is_voice_available.return_value = False
            mock_discovery.return_value = mock_discovery_instance
            manager = DynamicVoiceManager(voices_dir="/tmp/test_voices")
            return manager

    def test_initialization(self, mock_manager):
        """Test manager initializes correctly"""
        assert mock_manager is not None
        assert mock_manager.voices_dir.name == "test_voices"

    def test_get_available_voices(self, mock_manager):
        """Test getting available voices"""
        result = mock_manager.get_available_voices()
        assert isinstance(result, list)

    def test_is_voice_available(self, mock_manager):
        """Test checking if voice is available"""
        result = mock_manager.is_voice_available("test_voice")
        assert isinstance(result, bool)

    def test_voice_embedding_creation(self):
        """Test creating a voice embedding"""
        embedding = VoiceEmbedding(
            name="test_voice",
            embedding_data=np.random.randn(128).astype(np.float32),
            metadata={"gender": "female"},
            file_path="/path/to/voice.bin",
            checksum="abc123"
        )
        assert embedding.name == "test_voice"
        assert embedding.checksum == "abc123"
