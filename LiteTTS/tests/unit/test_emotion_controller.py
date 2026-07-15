#!/usr/bin/env python3
"""
Unit tests for emotion controller
"""

import pytest
from LiteTTS.tts.emotion_controller import EmotionController


class TestEmotionController:
    """Test cases for EmotionController"""

    @pytest.fixture
    def controller(self):
        """Create emotion controller instance"""
        return EmotionController()

    def test_initialization(self, controller):
        """Test controller initializes correctly"""
        assert controller is not None

    def test_get_supported_emotions(self, controller):
        """Test getting supported emotions"""
        emotions = controller.get_supported_emotions()
        assert isinstance(emotions, list)

    def test_get_emotion_info(self, controller):
        """Test getting emotion info"""
        emotions = controller.get_supported_emotions()
        if emotions:
            info = controller.get_emotion_info(emotions[0])
            assert info is not None


class TestEmotionControllerEdgeCases:
    """Edge case tests for EmotionController"""

    @pytest.fixture
    def controller(self):
        return EmotionController()

    def test_get_emotion_info_invalid(self, controller):
        """Test getting info for invalid emotion"""
        info = controller.get_emotion_info("nonexistent")
        assert info is None

    def test_get_supported_emotions_returns_list(self, controller):
        """Test that emotions list is not empty"""
        emotions = controller.get_supported_emotions()
        assert isinstance(emotions, list)
