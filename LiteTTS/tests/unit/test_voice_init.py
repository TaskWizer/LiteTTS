#!/usr/bin/env python3
"""
Unit tests for voice module __init__.py
"""

import pytest
from unittest.mock import Mock, patch
from LiteTTS.voice import get_available_voices, resolve_voice_name, ensure_voice_downloaded, _fallback_voice_discovery


class TestVoiceModuleFunctions:
    """Test cases for voice module functions"""

    def test_fallback_voice_discovery(self):
        """Test fallback voice discovery"""
        with patch('LiteTTS.voice.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path_instance.exists.return_value = False
            mock_path.return_value = mock_path_instance

            result = _fallback_voice_discovery("/tmp/nonexistent")
            assert isinstance(result, list)

    def test_resolve_voice_name(self):
        """Test resolving voice name"""
        with patch('LiteTTS.voice.get_voice_manager', return_value=None):
            result = resolve_voice_name("af_heart")
            assert result == "af_heart"

    def test_ensure_voice_downloaded(self):
        """Test ensuring voice is downloaded"""
        with patch('LiteTTS.voice.get_voice_manager', return_value=None):
            result = ensure_voice_downloaded("af_heart")
            assert isinstance(result, bool)
