#!/usr/bin/env python3
"""
Unit tests for voice consistency manager
"""

import pytest

from LiteTTS.audio.voice_consistency import ConsistencyLevel, VoiceConsistencyManager


class TestVoiceConsistencyManager:
    """Test cases for VoiceConsistencyManager"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        return VoiceConsistencyManager(consistency_level=ConsistencyLevel.ENHANCED)

    def test_initialization(self, manager):
        """Test manager initializes correctly"""
        assert manager is not None

    def test_start_consistency_session(self, manager):
        """Test starting a consistency session"""
        params = {"speed": 1.0, "pitch": 1.0}
        result = manager.start_consistency_session(
            "test_session", "af_heart", "Hello world", params
        )
        assert isinstance(result, str)

    def test_end_consistency_session(self, manager):
        """Test ending a consistency session"""
        params = {"speed": 1.0, "pitch": 1.0}
        manager.start_consistency_session("test_session", "af_heart", "Hello world", params)
        result = manager.end_consistency_session("test_session")
        assert isinstance(result, dict)


class TestVoiceConsistencyEdgeCases:
    """Edge case tests for VoiceConsistencyManager"""

    @pytest.fixture
    def manager(self):
        return VoiceConsistencyManager(consistency_level=ConsistencyLevel.BASIC)

    def test_start_multiple_sessions(self, manager):
        """Test starting multiple sessions"""
        params = {"speed": 1.0, "pitch": 1.0}
        manager.start_consistency_session("session1", "af_heart", "Text 1", params)
        manager.start_consistency_session("session2", "af_heart", "Text 2", params)
        result = manager.end_consistency_session("session1")
        assert isinstance(result, dict)

    def test_end_invalid_session(self, manager):
        """Test ending non-existent session"""
        result = manager.end_consistency_session("nonexistent_session")
        assert isinstance(result, dict)
