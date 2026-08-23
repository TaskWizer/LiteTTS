#!/usr/bin/env python3
"""
Unit tests for voice metadata manager
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from LiteTTS.voice.metadata import VoiceMetadata, VoiceMetadataManager, VoiceStats


class TestVoiceMetadataManager:
    """Test cases for VoiceMetadataManager"""

    @pytest.fixture
    def manager(self):
        """Create manager instance with mocked file operations"""
        with patch('LiteTTS.voice.metadata.Path.exists', return_value=False):
            manager = VoiceMetadataManager(metadata_file="/tmp/test_metadata.json")
            return manager

    @pytest.fixture
    def manager_with_data(self, tmp_path):
        """Create manager with actual data"""
        metadata_file = tmp_path / "metadata.json"
        with patch.object(Path, 'exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps({
                'voices': {
                    'test_voice': {
                        'name': 'test_voice',
                        'gender': 'female',
                        'accent': 'american',
                        'voice_type': 'neural',
                        'quality_rating': 4.5,
                        'language': 'en-us',
                        'description': 'Test voice'
                    }
                },
                'stats': {
                    'test_voice': {
                        'total_requests': 10,
                        'total_duration': 30.0,
                        'average_request_length': 3.0,
                        'last_used': None,
                        'error_count': 1,
                        'success_rate': 0.9
                    }
                }
            }))):
                manager = VoiceMetadataManager(metadata_file=str(metadata_file))
                return manager

    def test_initialization(self, manager):
        """Test manager initializes correctly"""
        assert manager is not None
        assert manager.metadata_file.name == "test_metadata.json"

    def test_initialization_with_defaults(self):
        """Test manager initializes with default metadata"""
        with patch('LiteTTS.voice.metadata.Path.exists', return_value=False):
            manager = VoiceMetadataManager(metadata_file="/tmp/test_metadata.json")
            # Should have default voices loaded
            assert len(manager.voice_metadata) > 0
            assert "af_heart" in manager.voice_metadata

    def test_get_voice_metadata_existing(self, manager):
        """Test getting metadata for existing voice"""
        result = manager.get_voice_metadata("af_heart")
        assert result is not None
        assert result.name == "af_heart"

    def test_get_voice_metadata_nonexistent(self, manager):
        """Test getting metadata for nonexistent voice"""
        result = manager.get_voice_metadata("nonexistent_voice_xyz")
        assert result is None

    def test_get_all_voices(self, manager):
        """Test getting all voices"""
        result = manager.get_all_voices()
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_filter_voices_by_gender(self, manager):
        """Test filtering voices by gender"""
        result = manager.filter_voices(gender="female")
        assert isinstance(result, list)
        for voice in result:
            assert voice.gender.lower() == "female"

    def test_filter_voices_by_quality_rating(self, manager):
        """Test filtering voices by quality rating"""
        result = manager.filter_voices(quality_rating=4.5)
        assert isinstance(result, list)

    def test_filter_voices_no_match(self, manager):
        """Test filtering voices with no matches"""
        result = manager.filter_voices(gender="unknown_gender_xyz")
        assert isinstance(result, list)

    def test_get_voices_by_gender(self, manager):
        """Test getting voices by gender"""
        result = manager.get_voices_by_gender("male")
        assert isinstance(result, list)

    def test_get_voices_by_quality(self, manager):
        """Test getting voices by quality"""
        result = manager.get_voices_by_quality(min_rating=4.0)
        assert isinstance(result, list)
        for voice in result:
            assert voice.quality_rating >= 4.0

    def test_get_recommended_voices(self, manager):
        """Test getting recommended voices"""
        result = manager.get_recommended_voices(count=3)
        assert isinstance(result, list)
        assert len(result) <= 3

    def test_update_voice_stats_new_voice(self, manager):
        """Test updating stats for new voice"""
        manager.update_voice_stats("new_voice_xyz", request_duration=1.5, success=True)
        stats = manager.get_voice_stats("new_voice_xyz")
        assert stats is not None
        assert stats.total_requests == 1

    def test_update_voice_stats_failure(self, manager):
        """Test updating stats for failed request"""
        manager.update_voice_stats("af_heart", request_duration=1.5, success=False)
        stats = manager.get_voice_stats("af_heart")
        assert stats is not None
        assert stats.error_count > 0

    def test_get_voice_stats_existing(self, manager):
        """Test getting voice stats"""
        manager.update_voice_stats("af_heart", request_duration=1.0)
        result = manager.get_voice_stats("af_heart")
        assert result is not None
        assert result.total_requests >= 1

    def test_get_voice_stats_nonexistent(self, manager):
        """Test getting stats for nonexistent voice"""
        result = manager.get_voice_stats("nonexistent_voice_xyz")
        assert result is None

    def test_get_usage_summary(self, manager):
        """Test getting usage summary"""
        manager.update_voice_stats("af_heart", request_duration=1.0)
        result = manager.get_usage_summary()
        assert isinstance(result, dict)
        assert "total_requests" in result
        assert "total_duration" in result
        assert "overall_success_rate" in result

    def test_get_voice_categories(self, manager):
        """Test getting voice categories"""
        result = manager.get_voice_categories()
        assert isinstance(result, dict)
        assert "female" in result
        assert "male" in result
        assert "high_quality" in result

    def test_add_custom_voice(self, manager):
        """Test adding custom voice"""
        new_metadata = VoiceMetadata(
            name="custom_voice",
            gender="female",
            accent="british",
            voice_type="neural",
            quality_rating=4.0,
            language="en-gb",
            description="Custom test voice"
        )
        manager.add_custom_voice("custom_voice", new_metadata)
        result = manager.get_voice_metadata("custom_voice")
        assert result is not None
        assert result.name == "custom_voice"

    def test_remove_voice(self, manager):
        """Test removing voice"""
        # First add a voice
        new_metadata = VoiceMetadata(
            name="to_remove",
            gender="male"
        )
        manager.add_custom_voice("to_remove", new_metadata)
        # Then remove it
        manager.remove_voice("to_remove")
        result = manager.get_voice_metadata("to_remove")
        assert result is None

    def test_update_voice_metadata(self, manager):
        """Test updating voice metadata"""
        manager.update_voice_metadata("af_heart", quality_rating=5.0)
        result = manager.get_voice_metadata("af_heart")
        assert result.quality_rating == 5.0

    def test_update_voice_metadata_nonexistent(self, manager):
        """Test updating nonexistent voice"""
        manager.update_voice_metadata("nonexistent_xyz", quality_rating=5.0)
        # Should not raise error

    def test_save_metadata(self, manager, tmp_path):
        """Test saving metadata"""
        metadata_file = tmp_path / "test_save.json"
        manager.metadata_file = metadata_file
        manager.update_voice_stats("af_heart", request_duration=1.0)
        manager.save_metadata()
        assert metadata_file.exists()


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

    def test_voice_stats_with_last_used(self):
        """Test voice stats with last_used datetime"""
        now = datetime.now()
        stats = VoiceStats(last_used=now)
        assert stats.last_used == now
