#!/usr/bin/env python3
"""
Unit tests for voice blender module
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from LiteTTS.voice.blender import (
    BlendConfig,
    VoiceBlender
)


class TestBlendConfig:
    """Test cases for BlendConfig dataclass"""

    def test_creation(self):
        """Test creating blend config"""
        config = BlendConfig(
            voices=[("voice1", 0.5), ("voice2", 0.5)],
            blend_method="weighted_average",
            normalize_weights=True,
            preserve_energy=True,
            smoothing_factor=0.1
        )
        assert len(config.voices) == 2
        assert config.blend_method == "weighted_average"
        assert config.normalize_weights is True
        assert config.preserve_energy is True
        assert config.smoothing_factor == 0.1

    def test_creation_defaults(self):
        """Test creating blend config with defaults"""
        config = BlendConfig(voices=[("voice1", 0.5)])
        assert config.blend_method == "weighted_average"
        assert config.normalize_weights is True
        assert config.preserve_energy is True
        assert config.smoothing_factor == 0.1


class TestVoiceBlender:
    """Test cases for VoiceBlender class"""

    def test_initialization(self):
        """Test blender initializes correctly"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)
        assert blender.voice_manager is mock_voice_manager
        assert "weighted_average" in blender.supported_methods
        assert "interpolation" in blender.supported_methods
        assert "style_mixing" in blender.supported_methods

    def test_blend_voices_empty(self):
        """Test blending with no voices"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)
        config = BlendConfig(voices=[])
        result = blender.blend_voices(config)
        assert result is None

    def test_blend_voices_single_voice(self):
        """Test blending with single voice returns original"""
        mock_voice_manager = Mock()
        mock_embedding = Mock()
        mock_embedding.name = "single_voice"
        mock_voice_manager.get_voice_embedding.return_value = mock_embedding
        
        blender = VoiceBlender(mock_voice_manager)
        config = BlendConfig(voices=[("single_voice", 1.0)])
        result = blender.blend_voices(config)
        assert result is mock_embedding

    def test_blend_voices_unsupported_method(self):
        """Test blending with unsupported method"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)
        config = BlendConfig(
            voices=[("voice1", 0.5), ("voice2", 0.5)],
            blend_method="unsupported_method"
        )
        result = blender.blend_voices(config)
        assert result is None

    def test_blend_voices_failed_to_load(self):
        """Test blending when voice fails to load"""
        mock_voice_manager = Mock()
        mock_voice_manager.get_voice_embedding.return_value = None
        
        blender = VoiceBlender(mock_voice_manager)
        config = BlendConfig(
            voices=[("voice1", 0.5), ("voice2", 0.5)],
            blend_method="weighted_average"
        )
        result = blender.blend_voices(config)
        assert result is None

    def test_blend_voices_zero_weights(self):
        """Test blending with all zero weights"""
        mock_voice_manager = Mock()
        mock_embedding = Mock()
        mock_embedding.embedding_data = np.random.randn(256).astype(np.float32)
        mock_voice_manager.get_voice_embedding.return_value = mock_embedding
        
        blender = VoiceBlender(mock_voice_manager)
        config = BlendConfig(
            voices=[("voice1", 0.0), ("voice2", 0.0)],
            blend_method="weighted_average",
            normalize_weights=True
        )
        result = blender.blend_voices(config)
        assert result is None

    def test_blend_voices_weighted_average(self):
        """Test blending with weighted average method"""
        mock_voice_manager = Mock()
        mock_embedding1 = Mock()
        mock_embedding1.name = "voice1"
        mock_embedding1.embedding_data = np.ones(256, dtype=np.float32)
        
        mock_embedding2 = Mock()
        mock_embedding2.name = "voice2"
        mock_embedding2.embedding_data = np.ones(256, dtype=np.float32) * 2
        
        def get_embedding(name):
            if name == "voice1":
                return mock_embedding1
            return mock_embedding2
        
        mock_voice_manager.get_voice_embedding.side_effect = get_embedding
        
        blender = VoiceBlender(mock_voice_manager)
        config = BlendConfig(
            voices=[("voice1", 0.5), ("voice2", 0.5)],
            blend_method="weighted_average",
            normalize_weights=True,
            preserve_energy=False
        )
        result = blender.blend_voices(config)
        assert result is not None
        assert result.name is not None

    def test_supported_methods(self):
        """Test supported blend methods"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)
        assert "weighted_average" in blender.supported_methods
        assert "interpolation" in blender.supported_methods
        assert "style_mixing" in blender.supported_methods
        assert len(blender.supported_methods) == 3
