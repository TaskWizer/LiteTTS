"""
LiteTTS Configuration Module
"""

# Import from the main config.py file (parent directory)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import ConfigManager, config
except ImportError:
    # Fallback if config.py is not available
    ConfigManager = None
    config = None

# Import Whisper-specific configuration
from .whisper_config_loader import get_whisper_config, get_whisper_settings, WhisperConfigLoader, WhisperSettings

__all__ = [
    "ConfigManager",
    "config",
    "get_whisper_config",
    "get_whisper_settings",
    "WhisperConfigLoader",
    "WhisperSettings"
]
