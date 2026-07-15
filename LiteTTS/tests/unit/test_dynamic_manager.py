#!/usr/bin/env python3
"""
Unit tests for dynamic voice manager
"""

import pytest
from LiteTTS.voice.dynamic_manager import DynamicVoiceManager


class TestDynamicVoiceManager:
    """Test cases for DynamicVoiceManager"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        return DynamicVoiceManager()

    def test_initialization(self, manager):
        """Test manager initializes correctly"""
        assert manager is not None

    def test_get_available_voices(self, manager):
        """Test getting available voices"""
        voices = manager.get_available_voices()
        assert isinstance(voices, list)

    def test_is_voice_available(self, manager):
        """Test checking voice availability"""
        voices = manager.get_available_voices()
        if voices:
            result = manager.is_voice_available(voices[0])
            assert isinstance(result, bool)

    def test_resolve_voice_name(self, manager):
        """Test resolving voice name"""
        voices = manager.get_available_voices()
        if voices:
            result = manager.resolve_voice_name(voices[0])
            assert isinstance(result, str)

    def test_get_voice_mappings(self, manager):
        """Test getting voice mappings"""
        mappings = manager.get_voice_mappings()
        assert isinstance(mappings, dict)


class TestDynamicVoiceManagerEdgeCases:
    """Edge case tests for DynamicVoiceManager"""

    @pytest.fixture
    def manager(self):
        return DynamicVoiceManager()

    def test_is_voice_available_invalid(self, manager):
        """Test checking availability of invalid voice"""
        result = manager.is_voice_available("nonexistent_voice_xyz")
        assert result is False

    def test_resolve_voice_name_invalid(self, manager):
        """Test resolving invalid voice name"""
        result = manager.resolve_voice_name("nonexistent_voice_xyz")
        assert isinstance(result, str)

    def test_get_available_voices_returns_list(self, manager):
        """Test that voices list is a list"""
        voices = manager.get_available_voices()
        assert isinstance(voices, list)
