#!/usr/bin/env python3
"""
Platform-safe emoji utility for cross-platform compatibility.
Provides fallback text for Windows systems that don't support Unicode emojis.
"""

import sys
import platform
from typing import Dict, Any


def is_windows_with_encoding_issues() -> bool:
    """
    Check if we're on Windows with potential Unicode encoding issues.

    This function detects if we're running on Windows with console encoding
    that cannot handle Unicode emoji characters. It checks multiple streams
    and encoding scenarios to provide accurate detection.
    """
    if platform.system() != "Windows":
        return False

    # Check multiple potential encoding issues on Windows
    try:
        # Test stdout encoding (console output)
        stdout_encoding = getattr(sys.stdout, 'encoding', None) or 'cp1252'

        # Test stderr encoding (error output)
        stderr_encoding = getattr(sys.stderr, 'encoding', None) or 'cp1252'

        # Test a representative emoji that commonly fails on Windows
        test_emoji = '🚀'

        # Try encoding to both stdout and stderr encodings
        test_emoji.encode(stdout_encoding)
        test_emoji.encode(stderr_encoding)

        # Additional check: try writing to a StringIO to simulate logging
        import io
        test_stream = io.StringIO()
        test_stream.write(test_emoji)
        test_content = test_stream.getvalue()

        # If we can encode to console encodings, check if it's actually cp1252
        # which is the problematic encoding on Windows
        if stdout_encoding.lower() in ['cp1252', 'windows-1252']:
            return True

        return False  # Encoding works fine

    except (UnicodeEncodeError, LookupError, AttributeError):
        return True  # Encoding issues detected


def get_safe_emoji(emoji: str, fallback: str) -> str:
    """
    Get emoji character if supported by the current platform, otherwise return fallback.
    
    Args:
        emoji: The Unicode emoji character
        fallback: Fallback text for unsupported platforms
        
    Returns:
        Either the emoji or fallback text
    """
    if is_windows_with_encoding_issues():
        return fallback
    return emoji


# Comprehensive emoji mappings for the LiteTTS application
EMOJIS = {
    # System and logging
    'clipboard': get_safe_emoji('📋', '[LOG]'),
    'folder': get_safe_emoji('📁', '[DIR]'),
    'chart': get_safe_emoji('📊', '[STAT]'),
    'memo': get_safe_emoji('📝', '[FILE]'),
    'page': get_safe_emoji('📄', '[DOC]'),
    'package': get_safe_emoji('📦', '[PKG]'),
    
    # Status indicators
    'check': get_safe_emoji('✅', '[OK]'),
    'cross': get_safe_emoji('❌', '[ERROR]'),
    'warning': get_safe_emoji('⚠️', '[WARN]'),
    'stop': get_safe_emoji('🛑', '[STOP]'),
    
    # Actions and processes
    'rocket': get_safe_emoji('🚀', '[START]'),
    'gear': get_safe_emoji('🔧', '[CONFIG]'),
    'wrench': get_safe_emoji('🔧', '[TOOL]'),
    'repeat': get_safe_emoji('🔄', '[LOOP]'),
    'refresh': get_safe_emoji('🔄', '[REFRESH]'),
    'electric_plug': get_safe_emoji('🔌', '[PLUG]'),
    'magnifying': get_safe_emoji('🔍', '[SEARCH]'),
    'test_tube': get_safe_emoji('🧪', '[TEST]'),
    
    # Network and communication
    'globe': get_safe_emoji('🌍', '[GLOBAL]'),
    'globe_web': get_safe_emoji('🌐', '[WEB]'),
    'download': get_safe_emoji('📥', '[DOWN]'),
    'upload': get_safe_emoji('📤', '[UP]'),
    'inbox': get_safe_emoji('📥', '[IN]'),
    'outbox': get_safe_emoji('📤', '[OUT]'),
    
    # Performance and optimization
    'fire': get_safe_emoji('🔥', '[HOT]'),
    'lightning': get_safe_emoji('⚡', '[FAST]'),
    'target': get_safe_emoji('🎯', '[TARGET]'),
    'clock': get_safe_emoji('⏰', '[TIME]'),
    
    # Audio and TTS specific
    'microphone': get_safe_emoji('🎤', '[MIC]'),
    'speaker': get_safe_emoji('🔊', '[SPEAKER]'),
    'musical_note': get_safe_emoji('♪', '[NOTE]'),
    'musical_notes': get_safe_emoji('♫', '[NOTES]'),
    'masks': get_safe_emoji('🎭', '[VOICE]'),
    'party': get_safe_emoji('🎉', '[READY]'),
    
    # Books and documentation
    'books': get_safe_emoji('📚', '[DOCS]'),
    'book': get_safe_emoji('📖', '[BOOK]'),
    'link': get_safe_emoji('🔗', '[LINK]'),
    'bulb': get_safe_emoji('💡', '[IDEA]'),
    
    # Music instruments (for audio processing)
    'trumpet': get_safe_emoji('🎺', '[TRUMPET]'),
    'saxophone': get_safe_emoji('🎷', '[SAX]'),
    'drum': get_safe_emoji('🥁', '[DRUM]'),
    'violin': get_safe_emoji('🎻', '[VIOLIN]'),
    'guitar': get_safe_emoji('🎸', '[GUITAR]'),
    'piano': get_safe_emoji('🎹', '[PIANO]'),
    
    # Volume controls
    'volume_high': get_safe_emoji('🔊', '[VOL_HIGH]'),
    'volume_medium': get_safe_emoji('🔉', '[VOL_MED]'),
    'volume_low': get_safe_emoji('🔈', '[VOL_LOW]'),
    'volume_mute': get_safe_emoji('🔇', '[MUTE]'),
    
    # Announcements
    'megaphone': get_safe_emoji('📢', '[ANNOUNCE]'),
    'loudspeaker': get_safe_emoji('📣', '[LOUD]'),
    'horn': get_safe_emoji('📯', '[HORN]'),
}


def get_emoji(name: str, fallback: str = '[?]') -> str:
    """
    Get an emoji by name with optional fallback.
    
    Args:
        name: The emoji name from the EMOJIS dictionary
        fallback: Fallback text if emoji name not found
        
    Returns:
        The emoji character or fallback text
    """
    return EMOJIS.get(name, fallback)


def format_log_message(emoji_name: str, message: str) -> str:
    """
    Format a log message with a platform-safe emoji.
    
    Args:
        emoji_name: Name of the emoji from EMOJIS dictionary
        message: The log message
        
    Returns:
        Formatted message with emoji prefix
    """
    emoji = get_emoji(emoji_name, '[LOG]')
    return f"{emoji} {message}"


def clean_message_for_json(message: str) -> str:
    """
    Clean a message by removing all Unicode emojis for JSON responses.
    This ensures API responses are machine-readable.
    
    Args:
        message: The message to clean
        
    Returns:
        Message with emojis removed
    """
    import re
    
    # Remove emoji characters (comprehensive Unicode ranges)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
        "]+",
        flags=re.UNICODE
    )
    
    # Apply emoji pattern removal
    cleaned = emoji_pattern.sub("", message)
    
    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


# Convenience functions for common logging patterns
def log_start(message: str) -> str:
    """Format a startup/initialization message."""
    return format_log_message('rocket', message)


def log_success(message: str) -> str:
    """Format a success message."""
    return format_log_message('check', message)


def log_error(message: str) -> str:
    """Format an error message."""
    return format_log_message('cross', message)


def log_warning(message: str) -> str:
    """Format a warning message."""
    return format_log_message('warning', message)


def log_config(message: str) -> str:
    """Format a configuration message."""
    return format_log_message('gear', message)


def log_info(message: str) -> str:
    """Format an informational message."""
    return format_log_message('clipboard', message)


def log_download(message: str) -> str:
    """Format a download message."""
    return format_log_message('download', message)


def log_test(message: str) -> str:
    """Format a test message."""
    return format_log_message('test_tube', message)


def log_voice(message: str) -> str:
    """Format a voice-related message."""
    return format_log_message('masks', message)


def log_ready(message: str) -> str:
    """Format a ready/completion message."""
    return format_log_message('party', message)


# Export the main functions and constants
__all__ = [
    'EMOJIS',
    'get_emoji',
    'format_log_message',
    'clean_message_for_json',
    'is_windows_with_encoding_issues',
    'log_start',
    'log_success',
    'log_error',
    'log_warning',
    'log_config',
    'log_info',
    'log_download',
    'log_test',
    'log_voice',
    'log_ready',
]
