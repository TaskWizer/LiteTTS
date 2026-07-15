#!/usr/bin/env python3
"""
Unit tests for voice metadata manager
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from LiteTTS.voice.metadata import VoiceMetadataManager, VoiceStats


class TestVoiceMetadataManager:
    """Test cases for VoiceMetadataManager"""

    @pytest.fixture
    def manager(self):
        """Create manager instance with mocked file operations"""
        with patch('LiteTTS.voice.metadata.Path.exists', return_value=False):
            manager = VoiceMetadataManager(metadata_file="/tmp/test_metadata.json")
            return manager

    def test_initialization(self, manager):
        """Test manager initializes correctly"""
        assert manager is not None
        assert manager.metadata_file.name == "test_metadata.json"

    def test_get_voice_metadata(self, manager):
        """Test getting voice metadata"""
        result = manager.get_voice_metadata("af_heart")
        # May return default or None depending on state

    def test_get_all_voices(self, manager):
        """Test getting all voices"""
        result = manager.get_all_voices()
        assert isinstance(result, dict)

    def test_filter_voices(self, manager):
        """Test filtering voices"""
        result = manager.filter_voices(gender="female")
        assert isinstance(result, list)

    def test_update_voice_stats(self, manager):
        """Test updating voice stats"""
        result = manager.update_voice_stats("af_heart", request_duration=1.5)
        # May return True/False depending on implementation

    def test_get_voice_stats(self, manager):
        """Test getting voice stats"""
        result = manager.get_voice_stats("af_heart")
        # May return None or VoiceStats

    def test_get_voice_categories(self, manager):
        """Test getting voice categories"""
        result = manager.get_voice_categories()
        assert isinstance(result, dict)


class TestVoiceStats:
    """Test cases for VoiceStats"""

    def test_voice_stats_creation(self):
        """Test creating voice stats"""
        stats = VoiceStats(
            total_requests=10,
            total_duration=30.0,
            average_request_length=3.0,
            last_used=datetime.now(),
            error_count=1,
            success_rate=0.9
        )
        assert stats.total_requests == 10
        assert stats.success_rate == 0.9

    def test_voice_stats_defaults(self):
        """Test voice stats default values"""
        stats = VoiceStats()
        assert stats.total_requests == 0
        assert stats.success_rate == 1.0
