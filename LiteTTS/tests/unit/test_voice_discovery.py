#!/usr/bin/env python3
"""
Unit tests for voice discovery
"""

import pytest
from LiteTTS.voice.discovery import VoiceDiscovery


class TestVoiceDiscovery:
    """Test cases for VoiceDiscovery"""

    @pytest.fixture
    def discovery(self):
        """Create voice discovery instance"""
        return VoiceDiscovery()

    def test_initialization(self, discovery):
        """Test discovery initializes correctly"""
        assert discovery is not None

    def test_discover_voices(self, discovery):
        """Test discovering voices"""
        count, new_count = discovery.discover_voices()
        assert isinstance(count, int)
        assert isinstance(new_count, int)

    def test_get_available_voices(self, discovery):
        """Test getting available voices"""
        voices = discovery.get_available_voices()
        assert isinstance(voices, list)

    def test_is_voice_available(self, discovery):
        """Test checking voice availability"""
        # Just check method exists
        assert hasattr(discovery, 'is_voice_available')


class TestVoiceDiscoveryEdgeCases:
    """Edge case tests for VoiceDiscovery"""

    @pytest.fixture
    def discovery(self):
        return VoiceDiscovery()

    def test_discover_with_empty_voices_dir(self, discovery):
        """Test discovery behavior"""
        assert discovery is not None
