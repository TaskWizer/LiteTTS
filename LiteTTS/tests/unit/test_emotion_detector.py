#!/usr/bin/env python3
"""
Unit tests for emotion detector
"""

import pytest

from LiteTTS.nlp.emotion_detector import (
    DialogueState,
    EmotionDetector,
    EmotionProfile,
)


class TestEmotionDetector:
    """Test cases for EmotionDetector"""

    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return EmotionDetector()

    def test_initialization(self, detector):
        """Test detector initializes correctly"""
        assert detector is not None

    def test_detect_emotional_context(self, detector):
        """Test detecting emotional context"""
        result = detector.detect_emotional_context("I'm so happy today!")
        assert isinstance(result, EmotionProfile)

    def test_update_conversation_history(self, detector):
        """Test updating conversation history"""
        import time

        emotion_profile = detector.detect_emotional_context("I'm happy!")
        detector.update_conversation_history("user", "Hello!", emotion_profile, time.time())
        result = detector.get_dialogue_state()
        assert isinstance(result, DialogueState)

    def test_get_dialogue_state(self, detector):
        """Test getting dialogue state"""
        result = detector.get_dialogue_state()
        assert isinstance(result, DialogueState)


class TestEmotionDetectorEdgeCases:
    """Edge case tests for EmotionDetector"""

    @pytest.fixture
    def detector(self):
        return EmotionDetector()

    def test_detect_neutral_text(self, detector):
        """Test detecting neutral text"""
        result = detector.detect_emotional_context("The weather is cloudy.")
        assert isinstance(result, EmotionProfile)

    def test_detect_long_text(self, detector):
        """Test detecting emotion in long text"""
        long_text = "I'm really excited about this! It's amazing! " * 10
        result = detector.detect_emotional_context(long_text)
        assert isinstance(result, EmotionProfile)

    def test_update_conversation_multiple(self, detector):
        """Test updating conversation with multiple turns"""
        import time

        t = time.time()
        emotion_profile1 = detector.detect_emotional_context("I'm happy!")
        emotion_profile2 = detector.detect_emotional_context("Hello there.")
        detector.update_conversation_history("user", "Hello!", emotion_profile1, t)
        detector.update_conversation_history("assistant", "Hi there!", emotion_profile2, t + 1)
        result = detector.get_dialogue_state()
        assert isinstance(result, DialogueState)
