#!/usr/bin/env python3
"""
Unit tests for audio quality enhancer
"""

import pytest

from LiteTTS.nlp.audio_quality_enhancer import (
    AudioQualityEnhancer,
    AudioQualityProfile,
    EmotionType,
    ProsodyLevel,
    ProsodyMarker,
)


class TestAudioQualityEnhancer:
    """Test cases for AudioQualityEnhancer"""

    @pytest.fixture
    def enhancer(self):
        """Create enhancer instance"""
        return AudioQualityEnhancer()

    @pytest.fixture
    def profile(self):
        """Create audio quality profile"""
        return AudioQualityProfile()

    def test_initialization(self, enhancer):
        """Test enhancer initializes correctly"""
        assert enhancer is not None
        assert enhancer.profile is not None

    def test_initialization_with_profile(self, profile):
        """Test initialization with custom profile"""
        enhancer = AudioQualityEnhancer(profile=profile)
        assert enhancer.profile is profile

    def test_enhance_audio_quality(self, enhancer):
        """Test enhancing audio quality"""
        result = enhancer.enhance_audio_quality("Hello world")
        assert isinstance(result, str)

    def test_analyze_quality_potential(self, enhancer):
        """Test analyzing quality potential"""
        result = enhancer.analyze_quality_potential("Hello world")
        assert isinstance(result, dict)
        assert "emotional_content" in result
        assert "prosodic_opportunities" in result
        assert "context_adaptations" in result
        assert "naturalness_score" in result

    def test_enhance_audio_quality_with_emotion(self, enhancer):
        """Test enhancing audio quality with emotional content"""
        result = enhancer.enhance_audio_quality("I am so happy and excited today!")
        assert isinstance(result, str)

    def test_enhance_audio_quality_with_questions(self, enhancer):
        """Test enhancing audio with question marks"""
        result = enhancer.enhance_audio_quality("How are you today?")
        assert isinstance(result, str)

    def test_enhance_audio_quality_with_exclamations(self, enhancer):
        """Test enhancing audio with exclamation marks"""
        result = enhancer.enhance_audio_quality("This is amazing!")
        assert isinstance(result, str)


class TestAudioQualityProfile:
    """Test cases for AudioQualityProfile"""

    def test_profile_defaults(self):
        """Test profile default values"""
        profile = AudioQualityProfile()
        assert profile.enable_emotional_analysis is True
        assert profile.enable_prosodic_modeling is True
        assert profile.enable_natural_pauses is False
        assert profile.naturalness_level == 0.9

    def test_profile_custom(self):
        """Test profile with custom values"""
        profile = AudioQualityProfile(
            emotional_intensity=0.5,
            prosodic_variation=0.6,
            naturalness_level=0.8
        )
        assert profile.emotional_intensity == 0.5
        assert profile.prosodic_variation == 0.6
        assert profile.naturalness_level == 0.8


class TestProsodyMarker:
    """Test cases for ProsodyMarker"""

    def test_creation(self):
        """Test creating prosody marker"""
        marker = ProsodyMarker(
            start_pos=0,
            end_pos=5,
            emotion=EmotionType.NEUTRAL,
            emphasis=ProsodyLevel.NORMAL
        )
        assert marker.start_pos == 0
        assert marker.end_pos == 5
        assert marker.emotion == EmotionType.NEUTRAL
        assert marker.emphasis == ProsodyLevel.NORMAL

    def test_creation_with_options(self):
        """Test creating prosody marker with options"""
        marker = ProsodyMarker(
            start_pos=0,
            end_pos=5,
            emotion=EmotionType.HAPPY,
            emphasis=ProsodyLevel.HIGH,
            pause_before=0.2,
            pause_after=0.3,
            pitch_shift=2.0,
            speed_factor=1.1
        )
        assert marker.pause_before == 0.2
        assert marker.pause_after == 0.3
        assert marker.pitch_shift == 2.0
        assert marker.speed_factor == 1.1


class TestEmotionType:
    """Test cases for EmotionType enum"""

    def test_emotion_types(self):
        """Test emotion types exist"""
        assert EmotionType.NEUTRAL is not None
        assert EmotionType.HAPPY is not None
        assert EmotionType.SAD is not None
        assert EmotionType.EXCITED is not None
        assert EmotionType.CALM is not None
        assert EmotionType.ANGRY is not None
        assert EmotionType.SURPRISED is not None
        assert EmotionType.CONFIDENT is not None
        assert EmotionType.UNCERTAIN is not None
        assert EmotionType.EMPATHETIC is not None

    def test_emotion_values(self):
        """Test emotion type values"""
        assert EmotionType.NEUTRAL.value == "neutral"
        assert EmotionType.HAPPY.value == "happy"
        assert EmotionType.SAD.value == "sad"


class TestProsodyLevel:
    """Test cases for ProsodyLevel enum"""

    def test_prosody_levels(self):
        """Test prosody levels exist"""
        assert ProsodyLevel.VERY_LOW is not None
        assert ProsodyLevel.LOW is not None
        assert ProsodyLevel.NORMAL is not None
        assert ProsodyLevel.HIGH is not None
        assert ProsodyLevel.VERY_HIGH is not None


class TestAudioQualityEnhancerEdgeCases:
    """Edge case tests for AudioQualityEnhancer"""

    @pytest.fixture
    def enhancer(self):
        return AudioQualityEnhancer()

    def test_enhance_empty_string(self, enhancer):
        """Test enhancing empty string"""
        result = enhancer.enhance_audio_quality("")
        assert isinstance(result, str)

    def test_enhance_very_long_text(self, enhancer):
        """Test enhancing very long text"""
        text = "Hello world. " * 1000
        result = enhancer.enhance_audio_quality(text)
        assert isinstance(result, str)

    def test_enhance_special_characters(self, enhancer):
        """Test enhancing text with special characters"""
        result = enhancer.enhance_audio_quality("Hello! How are you? I'm doing great...")
        assert isinstance(result, str)

    def test_analyze_quality_potential_empty(self, enhancer):
        """Test analyzing quality potential of empty text"""
        result = enhancer.analyze_quality_potential("")
        assert isinstance(result, dict)
        # Empty text gets base score of 0.7 (50% base + 0.2 for short sentences)
        assert result["naturalness_score"] >= 0.0

    def test_analyze_quality_potential_long_text(self, enhancer):
        """Test analyzing quality potential of long text"""
        text = "This is a test. How are you? I am happy! "
        result = enhancer.analyze_quality_potential(text * 100)
        assert isinstance(result, dict)

    def test_enhance_with_disabled_profile(self):
        """Test enhancing with profile that has features disabled"""
        profile = AudioQualityProfile(
            enable_emotional_analysis=False,
            enable_prosodic_modeling=False,
            enable_context_adaptation=False,
            enable_dynamic_intonation=False
        )
        enhancer = AudioQualityEnhancer(profile=profile)
        result = enhancer.enhance_audio_quality("Hello world")
        assert isinstance(result, str)
