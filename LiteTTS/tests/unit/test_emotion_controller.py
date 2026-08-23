#!/usr/bin/env python3
"""
Unit tests for emotion controller module
"""

import numpy as np

from LiteTTS.tts.emotion_controller import EmotionController, EmotionMapping


class TestEmotionMapping:
    """Test cases for EmotionMapping dataclass"""

    def test_creation(self):
        """Test creating an emotion mapping"""
        mapping = EmotionMapping(
            name='test_emotion',
            weight_adjustments={'brightness': 0.3},
            pitch_adjustment=0.1,
            speed_adjustment=1.2,
            energy_adjustment=1.1,
            description="Test emotion"
        )
        assert mapping.name == 'test_emotion'
        assert mapping.weight_adjustments == {'brightness': 0.3}
        assert mapping.pitch_adjustment == 0.1
        assert mapping.speed_adjustment == 1.2
        assert mapping.energy_adjustment == 1.1
        assert mapping.description == "Test emotion"

    def test_creation_defaults(self):
        """Test creating emotion mapping with defaults"""
        mapping = EmotionMapping(
            name='minimal',
            weight_adjustments={}
        )
        assert mapping.pitch_adjustment == 0.0
        assert mapping.speed_adjustment == 1.0
        assert mapping.energy_adjustment == 1.0
        assert mapping.description == ""


class TestEmotionController:
    """Test cases for EmotionController class"""

    def test_initialization(self):
        """Test controller initializes correctly"""
        controller = EmotionController()
        assert controller.emotion_mappings is not None
        assert len(controller.emotion_mappings) > 0
        assert 'neutral' in controller.emotion_mappings

    def test_supported_emotions(self):
        """Test getting supported emotions"""
        controller = EmotionController()
        emotions = controller.supported_emotions
        assert isinstance(emotions, list)
        assert 'neutral' in emotions
        assert 'happy' in emotions
        assert 'sad' in emotions

    def test_apply_emotion_neutral(self):
        """Test applying neutral emotion returns original"""
        controller = EmotionController()
        embedding = np.random.randn(256).astype(np.float32)
        result = controller.apply_emotion(embedding, 'neutral')
        np.testing.assert_array_equal(result, embedding)

    def test_apply_emotion_unknown(self):
        """Test applying unknown emotion falls back to neutral"""
        controller = EmotionController()
        embedding = np.random.randn(256).astype(np.float32)
        original = embedding.copy()
        result = controller.apply_emotion(embedding, 'unknown_emotion')
        # Should return neutral (original) embedding
        np.testing.assert_array_equal(result, original)

    def test_apply_emotion_strength_zero(self):
        """Test applying emotion with zero strength"""
        controller = EmotionController()
        embedding = np.random.randn(256).astype(np.float32)
        result = controller.apply_emotion(embedding, 'happy', strength=0.0)
        np.testing.assert_array_equal(result, embedding)

    def test_apply_emotion_strength_clamped(self):
        """Test emotion strength is clamped to valid range"""
        controller = EmotionController()
        embedding = np.random.randn(256).astype(np.float32)
        # Should not raise even with out-of-range strength
        result = controller.apply_emotion(embedding, 'happy', strength=5.0)
        assert result is not None
        result = controller.apply_emotion(embedding, 'happy', strength=-1.0)
        assert result is not None

    def test_apply_emotion_happy(self):
        """Test applying happy emotion modifies embedding"""
        controller = EmotionController()
        embedding = np.random.randn(256).astype(np.float32)
        result = controller.apply_emotion(embedding, 'happy', strength=1.0)
        assert result.shape == embedding.shape
        assert result.dtype == embedding.dtype

    def test_get_emotion_adjustments(self):
        """Test getting emotion adjustments"""
        controller = EmotionController()
        adjustments = controller.get_emotion_adjustments('happy', strength=1.0)
        assert 'pitch_adjustment' in adjustments
        assert 'speed_adjustment' in adjustments
        assert 'energy_adjustment' in adjustments
        assert adjustments['pitch_adjustment'] == 0.1
        assert adjustments['speed_adjustment'] == 1.1

    def test_get_emotion_adjustments_unknown(self):
        """Test getting adjustments for unknown emotion returns neutral"""
        controller = EmotionController()
        adjustments = controller.get_emotion_adjustments('unknown', strength=1.0)
        # Should return neutral adjustments
        assert adjustments['pitch_adjustment'] == 0.0
        assert adjustments['speed_adjustment'] == 1.0
        assert adjustments['energy_adjustment'] == 1.0

    def test_blend_emotions_empty(self):
        """Test blending with empty emotions list"""
        controller = EmotionController()
        embedding = np.random.randn(256).astype(np.float32)
        result = controller.blend_emotions(embedding, [])
        np.testing.assert_array_equal(result, embedding)

    def test_blend_emotions_zero_total_strength(self):
        """Test blending emotions with zero total strength"""
        controller = EmotionController()
        embedding = np.random.randn(256).astype(np.float32)
        result = controller.blend_emotions(embedding, [('happy', 0.0), ('sad', 0.0)])
        np.testing.assert_array_equal(result, embedding)

    def test_blend_emotions_multiple(self):
        """Test blending multiple emotions"""
        controller = EmotionController()
        embedding = np.random.randn(256).astype(np.float32)
        result = controller.blend_emotions(embedding, [('happy', 0.5), ('calm', 0.5)])
        assert result.shape == embedding.shape

    def test_get_supported_emotions(self):
        """Test getting supported emotions list"""
        controller = EmotionController()
        emotions = controller.get_supported_emotions()
        assert isinstance(emotions, list)
        assert len(emotions) > 0
        # Verify it returns a copy
        emotions.append('test')
        assert 'test' not in controller.supported_emotions

    def test_get_emotion_info_existing(self):
        """Test getting info for existing emotion"""
        controller = EmotionController()
        info = controller.get_emotion_info('happy')
        assert info is not None
        assert info['name'] == 'happy'
        assert 'description' in info
        assert 'pitch_adjustment' in info
        assert 'weight_adjustments' in info

    def test_get_emotion_info_nonexistent(self):
        """Test getting info for nonexistent emotion"""
        controller = EmotionController()
        info = controller.get_emotion_info('nonexistent')
        assert info is None

    def test_validate_emotion_strength_valid(self):
        """Test validating valid emotion strength"""
        controller = EmotionController()
        valid, msg = controller.validate_emotion_strength(1.0)
        assert valid is True
        assert "Valid" in msg

    def test_validate_emotion_strength_zero(self):
        """Test validating zero emotion strength"""
        controller = EmotionController()
        valid, msg = controller.validate_emotion_strength(0.0)
        assert valid is True

    def test_validate_emotion_strength_negative(self):
        """Test validating negative emotion strength"""
        controller = EmotionController()
        valid, msg = controller.validate_emotion_strength(-0.5)
        assert valid is False
        assert "negative" in msg.lower()

    def test_validate_emotion_strength_too_high(self):
        """Test validating too high emotion strength"""
        controller = EmotionController()
        valid, msg = controller.validate_emotion_strength(3.0)
        assert valid is False
        assert "2.0" in msg

    def test_validate_emotion_strength_non_number(self):
        """Test validating non-number emotion strength"""
        controller = EmotionController()
        valid, msg = controller.validate_emotion_strength("high")
        assert valid is False
        assert "number" in msg.lower()

    def test_suggest_emotion_for_text_happy(self):
        """Test suggesting emotion for happy text"""
        controller = EmotionController()
        emotion = controller.suggest_emotion_for_text("I am so happy and excited today!")
        assert emotion == 'happy'

    def test_suggest_emotion_for_text_sad(self):
        """Test suggesting emotion for sad text"""
        controller = EmotionController()
        emotion = controller.suggest_emotion_for_text("I am sad and it is terrible")
        assert emotion == 'sad'

    def test_suggest_emotion_for_text_neutral(self):
        """Test suggesting emotion for neutral text"""
        controller = EmotionController()
        emotion = controller.suggest_emotion_for_text("The weather is cloudy today")
        assert emotion == 'neutral'

    def test_create_custom_emotion_success(self):
        """Test creating custom emotion successfully"""
        controller = EmotionController()
        result = controller.create_custom_emotion(
            name='custom_emotion',
            weight_adjustments={'brightness': 0.5},
            pitch_adjustment=0.2,
            speed_adjustment=1.1,
            energy_adjustment=1.2,
            description="A custom emotion"
        )
        assert result is True
        assert 'custom_emotion' in controller.emotion_mappings
        assert 'custom_emotion' in controller.supported_emotions

    def test_create_custom_emotion_info(self):
        """Test that custom emotion has correct info"""
        controller = EmotionController()
        controller.create_custom_emotion(
            name='my_emotion',
            weight_adjustments={'intensity': 0.5},
            pitch_adjustment=0.1
        )
        info = controller.get_emotion_info('my_emotion')
        assert info is not None
        assert info['name'] == 'my_emotion'
        assert info['pitch_adjustment'] == 0.1
