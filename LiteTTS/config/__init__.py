"""
LiteTTS Configuration Module
"""

# Import from the main config.py file (parent directory)
import sys
from pathlib import Path

# Add parent directory to path to access config.py
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Import from the parent config.py file
    import importlib.util
    config_path = Path(__file__).parent.parent / "config.py"

    if config_path.exists():
        spec = importlib.util.spec_from_file_location("parent_config", config_path)
        parent_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parent_config)

        ConfigManager = parent_config.ConfigManager
        config = parent_config.config
    else:
        # Fallback if config.py is not available
        ConfigManager = None
        config = None

except Exception as e:
    # Fallback if config.py import fails
    print(f"Could not load config, using defaults: {e}")
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
