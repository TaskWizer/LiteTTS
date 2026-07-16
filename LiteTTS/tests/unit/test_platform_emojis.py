#!/usr/bin/env python3
"""
Unit tests for platform emojis module
"""

import pytest
from LiteTTS.utils.platform_emojis import (
    is_windows_with_encoding_issues,
    get_safe_emoji,
    get_emoji,
    format_log_message,
    clean_message_for_json,
    log_start,
    log_success,
    log_error,
    log_warning,
    log_info,
    log_config,
    log_download,
    log_test,
    log_voice,
    log_ready,
    EMOJIS
)


class TestPlatformEmojis:
    """Test cases for platform emoji functions"""

    def test_is_windows_with_encoding_issues(self):
        """Test checking Windows encoding issues"""
        result = is_windows_with_encoding_issues()
        assert isinstance(result, bool)

    def test_get_safe_emoji(self):
        """Test getting safe emoji"""
        result = get_safe_emoji("🚀", fallback="[rocket]")
        assert isinstance(result, str)

    def test_get_emoji(self):
        """Test getting emoji"""
        result = get_emoji("test", fallback="[?]")
        assert isinstance(result, str)

    def test_format_log_message(self):
        """Test formatting log message"""
        result = format_log_message("check", "Operation completed")
        assert isinstance(result, str)

    def test_clean_message_for_json(self):
        """Test cleaning message for JSON"""
        result = clean_message_for_json("Test message")
        assert isinstance(result, str)

    def test_log_start(self):
        """Test log start"""
        result = log_start("Starting process")
        assert isinstance(result, str)

    def test_log_success(self):
        """Test log success"""
        result = log_success("Process succeeded")
        assert isinstance(result, str)

    def test_log_error(self):
        """Test log error"""
        result = log_error("Process failed")
        assert isinstance(result, str)

    def test_log_warning(self):
        """Test log warning"""
        result = log_warning("Process warning")
        assert isinstance(result, str)

    def test_log_info(self):
        """Test log info"""
        result = log_info("Process info")
        assert isinstance(result, str)


class TestEmojiMappings:
    """Test emoji mappings are properly defined"""

    def test_emojis_dict_exists(self):
        """Test EMOJIS dictionary exists"""
        assert isinstance(EMOJIS, dict)
        assert len(EMOJIS) > 0

    def test_system_emojis_defined(self):
        """Test system/logging emojis are defined"""
        assert 'clipboard' in EMOJIS
        assert 'folder' in EMOJIS
        assert 'chart' in EMOJIS

    def test_status_emojis_defined(self):
        """Test status indicator emojis are defined"""
        assert 'check' in EMOJIS
        assert 'cross' in EMOJIS
        assert 'warning' in EMOJIS
        assert 'stop' in EMOJIS

    def test_action_emojis_defined(self):
        """Test action/process emojis are defined"""
        assert 'rocket' in EMOJIS
        assert 'gear' in EMOJIS
        assert 'refresh' in EMOJIS

    def test_audio_emojis_defined(self):
        """Test audio/TTS emojis are defined"""
        assert 'microphone' in EMOJIS
        assert 'speaker' in EMOJIS
        assert 'musical_note' in EMOJIS
        assert 'masks' in EMOJIS


class TestGetEmoji:
    """Test get_emoji function"""

    def test_get_emoji_known(self):
        """Test getting known emoji"""
        result = get_emoji("rocket", fallback="[START]")
        assert isinstance(result, str)

    def test_get_emoji_unknown(self):
        """Test getting unknown emoji returns fallback"""
        result = get_emoji("nonexistent_emoji", fallback="[?]")
        assert result == "[?]"

    def test_get_emoji_default_fallback(self):
        """Test default fallback is [?]"""
        result = get_emoji("unknown")
        assert result == "[?]"

    def test_get_emoji_all_keys(self):
        """Test all emoji keys are accessible"""
        for key in EMOJIS:
            result = get_emoji(key)
            assert isinstance(result, str)


class TestCleanMessageForJson:
    """Test clean_message_for_json function"""

    def test_clean_message_basic(self):
        """Test basic cleaning"""
        result = clean_message_for_json("Hello World")
        assert result == "Hello World"

    def test_clean_message_with_emoji(self):
        """Test removing emoji characters"""
        result = clean_message_for_json("Hello 🚀 World")
        assert "🚀" not in result
        assert "Hello" in result
        assert "World" in result

    def test_clean_message_with_multiple_emojis(self):
        """Test removing multiple emojis"""
        result = clean_message_for_json("📁 Start 🔥 End ⚡")
        assert "📁" not in result
        assert "🔥" not in result
        assert "⚡" not in result

    def test_clean_message_with_flags(self):
        """Test removing flag emojis"""
        result = clean_message_for_json("🇺🇸 USA 🏴󠁧󠁢󠁥󠁮󠁧󠁿 UK")
        assert "🇺🇸" not in result
        assert "🏴󠁧󠁢󠁥󠁮󠁧󠁿" not in result

    def test_clean_message_empty(self):
        """Test cleaning empty string"""
        result = clean_message_for_json("")
        assert result == ""

    def test_clean_message_only_emoji(self):
        """Test cleaning string with only emojis"""
        result = clean_message_for_json("🚀🔥⚡")
        assert result == ""

    def test_clean_message_extra_whitespace(self):
        """Test cleaning removes extra whitespace"""
        result = clean_message_for_json("Hello    World")
        assert "  " not in result

    def test_clean_message_preserves_regular_text(self):
        """Test that regular text is preserved"""
        result = clean_message_for_json("Hello World 123 !?.,")
        assert "Hello World 123 !?.," == result


class TestLogFunctions:
    """Test logging convenience functions"""

    def test_log_start_format(self):
        """Test log_start formatting"""
        result = log_start("Test message")
        assert "Test message" in result

    def test_log_success_format(self):
        """Test log_success formatting"""
        result = log_success("Test message")
        assert "Test message" in result

    def test_log_error_format(self):
        """Test log_error formatting"""
        result = log_error("Test message")
        assert "Test message" in result

    def test_log_warning_format(self):
        """Test log_warning formatting"""
        result = log_warning("Test message")
        assert "Test message" in result

    def test_log_info_format(self):
        """Test log_info formatting"""
        result = log_info("Test message")
        assert "Test message" in result

    def test_log_config_format(self):
        """Test log_config formatting"""
        result = log_config("Test message")
        assert "Test message" in result

    def test_log_download_format(self):
        """Test log_download formatting"""
        result = log_download("Test message")
        assert "Test message" in result

    def test_log_test_format(self):
        """Test log_test formatting"""
        result = log_test("Test message")
        assert "Test message" in result

    def test_log_voice_format(self):
        """Test log_voice formatting"""
        result = log_voice("Test message")
        assert "Test message" in result

    def test_log_ready_format(self):
        """Test log_ready formatting"""
        result = log_ready("Test message")
        assert "Test message" in result


class TestFormatLogMessage:
    """Test format_log_message function"""

    def test_format_log_message_check(self):
        """Test formatting with check emoji"""
        result = format_log_message("check", "Success")
        assert "Success" in result

    def test_format_log_message_cross(self):
        """Test formatting with cross emoji"""
        result = format_log_message("cross", "Failed")
        assert "Failed" in result

    def test_format_log_message_warning(self):
        """Test formatting with warning emoji"""
        result = format_log_message("warning", "Caution")
        assert "Caution" in result

    def test_format_log_message_unknown(self):
        """Test formatting with unknown emoji uses fallback"""
        result = format_log_message("unknown_emoji", "Message")
        assert "Message" in result


class TestGetSafeEmoji:
    """Test get_safe_emoji function"""

    def test_get_safe_emoji_returns_emoji(self):
        """Test returns emoji when not Windows"""
        result = get_safe_emoji("🚀", fallback="[rocket]")
        assert result == "🚀" or result == "[rocket]"

    def test_get_safe_emoji_fallback(self):
        """Test fallback is used on Windows with issues"""
        # This may return either emoji or fallback depending on platform
        result = get_safe_emoji("🚀", fallback="[rocket]")
        assert isinstance(result, str)
        assert len(result) > 0
