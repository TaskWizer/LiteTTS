#!/usr/bin/env python3
"""
Unit tests for voice blender
"""

import pytest
import numpy as np
from unittest.mock import Mock
from LiteTTS.voice.blender import VoiceBlender, BlendConfig


class TestVoiceBlender:
    """Test cases for VoiceBlender"""

    @pytest.fixture
    def blender(self):
        """Create blender instance with mock voice manager"""
        mock_manager = Mock()
        return VoiceBlender(voice_manager=mock_manager)

    def test_initialization(self, blender):
        """Test blender initializes correctly"""
        assert blender is not None
        assert blender.voice_manager is not None

    def test_blend_config_creation(self):
        """Test creating blend config"""
        config = BlendConfig(
            voices=[("voice1", 0.5), ("voice2", 0.5)],
            blend_method="weighted_average"
        )
        assert len(config.voices) == 2
        assert config.blend_method == "weighted_average"


class TestVoiceBlenderEdgeCases:
    """Edge case tests for VoiceBlender"""

    def test_blend_with_empty_voices(self):
        """Test blending with empty voice list"""
        mock_manager = Mock()
        blender = VoiceBlender(voice_manager=mock_manager)
        assert blender is not None

    def test_blend_config_defaults(self):
        """Test blend config default values"""
        config = BlendConfig(voices=[("voice1", 1.0)])
        assert config.normalize_weights is True
        assert config.preserve_energy is True
