#!/usr/bin/env python3
"""
Unit tests for voice blender module
"""

from unittest.mock import Mock

import numpy as np

from LiteTTS.voice.blender import BlendConfig, VoiceBlender


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

    def test_weighted_average_blend_success(self):
        """Test _weighted_average_blend with valid data"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)

        embedding1 = Mock()
        embedding1.embedding_data = np.ones(256, dtype=np.float32)
        embedding2 = Mock()
        embedding2.embedding_data = np.ones(256, dtype=np.float32) * 2

        result = blender._weighted_average_blend([embedding1, embedding2], [0.5, 0.5])

        assert result is not None
        assert result.shape == (256,)
        assert result.dtype == np.float32

    def test_weighted_average_blend_different_shapes(self):
        """Test _weighted_average_blend handles different shapes"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)

        embedding1 = Mock()
        embedding1.embedding_data = np.ones(256, dtype=np.float32)
        embedding2 = Mock()
        embedding2.embedding_data = np.ones(512, dtype=np.float32) * 2

        result = blender._weighted_average_blend([embedding1, embedding2], [0.5, 0.5])

        assert result is not None

    def test_weighted_average_blend_reshaping_insufficient_data(self):
        """Test _weighted_average_blend with insufficient data returns None"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)

        embedding1 = Mock()
        embedding1.embedding_data = np.ones(256, dtype=np.float32)
        embedding2 = Mock()
        embedding2.embedding_data = np.ones(128, dtype=np.float32) * 2

        result = blender._weighted_average_blend([embedding1, embedding2], [0.5, 0.5])

        assert result is None

    def test_interpolation_blend_two_voices(self):
        """Test _interpolation_blend with two voices"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)

        embedding1 = Mock()
        embedding1.embedding_data = np.ones(256, dtype=np.float32)
        embedding2 = Mock()
        embedding2.embedding_data = np.ones(256, dtype=np.float32) * 2

        result = blender._interpolation_blend([embedding1, embedding2], [0.5, 0.5])

        assert result is not None

    def test_interpolation_blend_multiple_voices(self):
        """Test _interpolation_blend with more than 2 voices falls back to weighted average"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)

        embedding1 = Mock()
        embedding1.embedding_data = np.ones(256, dtype=np.float32)
        embedding2 = Mock()
        embedding2.embedding_data = np.ones(256, dtype=np.float32) * 2
        embedding3 = Mock()
        embedding3.embedding_data = np.ones(256, dtype=np.float32) * 3

        result = blender._interpolation_blend([embedding1, embedding2, embedding3], [0.33, 0.33, 0.34])

        assert result is not None

    def test_style_mixing_blend(self):
        """Test _style_mixing_blend"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)

        embedding1 = Mock()
        embedding1.embedding_data = np.ones(256, dtype=np.float32)
        embedding2 = Mock()
        embedding2.embedding_data = np.ones(256, dtype=np.float32) * 2

        result = blender._style_mixing_blend([embedding1, embedding2], [0.5, 0.5], 0.1)

        assert result is not None

    def test_slerp_blend(self):
        """Test _slerp_blend for spherical interpolation"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)

        embedding1 = Mock()
        embedding1.embedding_data = np.ones(256, dtype=np.float32)
        embedding2 = Mock()
        embedding2.embedding_data = np.ones(256, dtype=np.float32) * 2

        result = blender._slerp_blend(embedding1, embedding2, 0.5)

        assert result is not None

    def test_preserve_energy(self):
        """Test _preserve_energy method"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)

        blended = np.ones(256, dtype=np.float32) * 1.5
        original = np.ones(256, dtype=np.float32)

        result = blender._preserve_energy(blended, original)

        assert result is not None
        assert result.shape == (256,)

    def test_create_blended_metadata(self):
        """Test _create_blended_metadata method"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)

        embedding1 = Mock()
        embedding1.name = "voice1"
        embedding1.metadata = Mock()
        embedding1.metadata.gender = "female"
        embedding2 = Mock()
        embedding2.name = "voice2"
        embedding2.metadata = Mock()
        embedding2.metadata.gender = "male"

        result = blender._create_blended_metadata([embedding1, embedding2], [0.5, 0.5])

        assert result is not None
        assert hasattr(result, 'gender')

    def test_generate_blend_name(self):
        """Test _generate_blend_name method"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)

        result = blender._generate_blend_name([("voice1", 0.5), ("voice2", 0.5)])

        assert result is not None
        assert isinstance(result, str)

    def test_generate_blend_name_single(self):
        """Test _generate_blend_name with single voice"""
        mock_voice_manager = Mock()
        blender = VoiceBlender(mock_voice_manager)

        result = blender._generate_blend_name([("voice1", 1.0)])

        assert result is not None
        assert isinstance(result, str)

    def test_blend_voices_preserves_metadata(self):
        """Test blending preserves metadata from source voices"""
        mock_voice_manager = Mock()
        mock_embedding = Mock()
        mock_embedding.name = "voice1"
        mock_embedding.embedding_data = np.ones(256, dtype=np.float32)
        mock_embedding.metadata = Mock()
        mock_embedding.metadata.gender = "female"
        mock_voice_manager.get_voice_embedding.return_value = mock_embedding

        blender = VoiceBlender(mock_voice_manager)
        config = BlendConfig(
            voices=[("voice1", 1.0)],
            blend_method="weighted_average",
            preserve_energy=True
        )
        result = blender.blend_voices(config)

        assert result is not None
        assert result.name is not None

    def test_blend_voices_interpolation_method(self):
        """Test blending with interpolation method"""
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
            blend_method="interpolation"
        )
        result = blender.blend_voices(config)

        assert result is not None

    def test_blend_voices_style_mixing_method(self):
        """Test blending with style mixing method"""
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
            blend_method="style_mixing",
            smoothing_factor=0.2
        )
        result = blender.blend_voices(config)

        assert result is not None
