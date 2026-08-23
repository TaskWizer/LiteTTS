#!/usr/bin/env python3
"""
Unit tests for voice module __init__.py
"""

from unittest.mock import Mock, patch


class TestVoiceModuleImports:
    """Test cases for voice module imports"""

    def test_voice_downloader_importable(self):
        """Test VoiceDownloader is importable"""
        from LiteTTS.voice import VoiceDownloader

        assert VoiceDownloader is not None

    def test_voice_discovery_importable(self):
        """Test VoiceDiscovery is importable"""
        from LiteTTS.voice import VoiceDiscovery

        assert VoiceDiscovery is not None

    def test_voice_validator_importable(self):
        """Test VoiceValidator is importable"""
        from LiteTTS.voice import VoiceValidator

        assert VoiceValidator is not None

    def test_voice_cache_importable(self):
        """Test VoiceCache is importable"""
        from LiteTTS.voice import VoiceCache

        assert VoiceCache is not None

    def test_voice_manager_importable(self):
        """Test VoiceManager is importable"""
        from LiteTTS.voice import VoiceManager

        assert VoiceManager is not None

    def test_voice_blender_importable(self):
        """Test VoiceBlender is importable"""
        from LiteTTS.voice import VoiceBlender

        assert VoiceBlender is not None

    def test_dynamic_voice_manager_importable(self):
        """Test DynamicVoiceManager is importable"""
        from LiteTTS.voice import DynamicVoiceManager

        assert DynamicVoiceManager is not None


class TestFallbackVoiceDiscovery:
    """Test cases for fallback voice discovery"""

    def test_fallback_returns_empty_for_nonexistent_dir(self):
        """Test fallback returns empty list for non-existent directory"""
        from LiteTTS.voice import _fallback_voice_discovery

        result = _fallback_voice_discovery("/nonexistent/path/12345")
        assert result == []

    def test_fallback_discovers_local_voices(self, tmp_path):
        """Test fallback discovers local voice files"""
        from LiteTTS.voice import _fallback_voice_discovery

        # Create some mock voice files
        (tmp_path / "af_heart.bin").write_bytes(b"\x00" * 100)
        (tmp_path / "am_puck.pt").write_bytes(b"\x00" * 100)

        result = _fallback_voice_discovery(str(tmp_path))
        assert "af_heart" in result
        assert "am_puck" in result

    def test_fallback_handles_short_name_mappings(self, tmp_path):
        """Test fallback handles short name mappings"""
        from LiteTTS.voice import _fallback_voice_discovery

        # Create voice file with underscore
        (tmp_path / "af_heart.bin").write_bytes(b"\x00" * 100)

        result = _fallback_voice_discovery(str(tmp_path))
        assert "heart" in result  # Short name mapping

    def test_fallback_returns_empty_for_nonexistent_path(self):
        """Test fallback returns empty when path doesn't exist"""
        from LiteTTS.voice import _fallback_voice_discovery

        result = _fallback_voice_discovery("/nonexistent/path/12345")
        assert result == []


class TestGetAvailableVoices:
    """Test cases for get_available_voices function"""

    def test_get_available_voices_with_voices_dir(self, tmp_path):
        """Test get_available_voices with specified voices_dir"""
        from LiteTTS.voice import get_available_voices

        # Create mock voice files
        (tmp_path / "voice1.bin").write_bytes(b"\x00" * 100)
        (tmp_path / "voice2.bin").write_bytes(b"\x00" * 100)

        result = get_available_voices(str(tmp_path))
        assert "voice1" in result
        assert "voice2" in result

    def test_get_available_voices_handles_manager_error(self):
        """Test get_available_voices handles errors gracefully"""
        from LiteTTS.voice import get_available_voices

        with patch("LiteTTS.voice.get_voice_manager", side_effect=Exception("Test error")):
            result = get_available_voices("/nonexistent")
            # Should fall back to basic discovery
            assert isinstance(result, list)


class TestResolveVoiceName:
    """Test cases for resolve_voice_name function"""

    def test_resolve_voice_name_returns_input_on_error(self):
        """Test resolve_voice_name returns input when manager fails"""
        from LiteTTS.voice import resolve_voice_name

        with patch("LiteTTS.voice.get_voice_manager", side_effect=Exception("Test error")):
            result = resolve_voice_name("test_voice")
            assert result == "test_voice"

    def test_resolve_voice_name_delegates_to_manager(self):
        """Test resolve_voice_name delegates to manager"""
        from LiteTTS.voice import resolve_voice_name

        mock_manager = Mock()
        mock_manager.resolve_voice_name.return_value = "full_voice_name"

        with patch("LiteTTS.voice.get_voice_manager", return_value=mock_manager):
            result = resolve_voice_name("short")
            assert result == "full_voice_name"


class TestEnsureVoiceDownloaded:
    """Test cases for ensure_voice_downloaded function"""

    def test_ensure_voice_downloaded_returns_false_on_error(self):
        """Test ensure_voice_downloaded returns False on error"""
        from LiteTTS.voice import ensure_voice_downloaded

        with patch("LiteTTS.voice.get_voice_manager", side_effect=Exception("Test error")):
            result = ensure_voice_downloaded("test_voice")
            assert result is False

    def test_ensure_voice_downloaded_delegates_to_manager(self):
        """Test ensure_voice_downloaded delegates to manager"""
        from LiteTTS.voice import ensure_voice_downloaded

        mock_manager = Mock()
        mock_manager.ensure_voice_downloaded.return_value = True

        with patch("LiteTTS.voice.get_voice_manager", return_value=mock_manager):
            result = ensure_voice_downloaded("test_voice")
            assert result is True


class TestGetVoiceManager:
    """Test cases for get_voice_manager function"""

    def test_get_voice_manager_returns_none_when_unavailable(self):
        """Test get_voice_manager returns None when DynamicVoiceManager unavailable"""
        from LiteTTS.voice import get_voice_manager

        with patch.dict("LiteTTS.voice.__dict__", {"_has_dynamic_manager": False}):
            with patch("LiteTTS.voice.logger"):
                result = get_voice_manager()
                assert result is None

    def test_get_voice_manager_creates_instance(self):
        """Test get_voice_manager creates instance"""
        from LiteTTS.voice import get_voice_manager

        with patch("LiteTTS.voice.DynamicVoiceManager") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance

            # Reset global
            import LiteTTS.voice

            LiteTTS.voice._voice_manager = None

            result = get_voice_manager("/fake/path")

            mock_class.assert_called_once_with("/fake/path")

    def test_get_voice_manager_returns_cached_instance(self):
        """Test get_voice_manager returns cached instance"""
        from LiteTTS.voice import get_voice_manager

        mock_manager = Mock()

        import LiteTTS.voice

        original = LiteTTS.voice._voice_manager
        LiteTTS.voice._voice_manager = mock_manager

        try:
            result = get_voice_manager()
            assert result is mock_manager
        finally:
            LiteTTS.voice._voice_manager = original
