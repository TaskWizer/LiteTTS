"""
LiteTTS Configuration Module

This module provides configuration management for the LiteTTS system,
including user-friendly configuration loading, internal configuration
management, and hot reload capabilities.
"""

try:
    from .config_manager import ConfigManager, get_config_manager, reload_config
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False
    ConfigManager = None
    get_config_manager = None
    reload_config = None

try:
    from .internal_config import get_internal_config, InternalConfig
    INTERNAL_CONFIG_AVAILABLE = True
except ImportError:
    INTERNAL_CONFIG_AVAILABLE = False
    get_internal_config = None
    InternalConfig = None

# Import TTSConfig from the main config module
try:
    from ..config import TTSConfig
    TTSCONFIG_AVAILABLE = True
except ImportError:
    TTSCONFIG_AVAILABLE = False
    TTSConfig = None

# Export main configuration interface
__all__ = [
    "ConfigManager",
    "get_config_manager",
    "reload_config",
    "get_internal_config",
    "InternalConfig",
    "TTSConfig",
    "CONFIG_MANAGER_AVAILABLE",
    "INTERNAL_CONFIG_AVAILABLE",
    "TTSCONFIG_AVAILABLE"
]

class ConfigObject:
    """Configuration object that provides attribute access to dictionary data"""

    def __init__(self, config_dict):
        self._config = config_dict or {}

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        value = self._config.get(name)
        if isinstance(value, dict):
            return ConfigObject(value)
        return value

    def __getitem__(self, key):
        return self._config[key]

    def get(self, key, default=None):
        return self._config.get(key, default)

    def __contains__(self, key):
        return key in self._config

    def __repr__(self):
        return f"ConfigObject({self._config})"

# Provide a default config instance for backward compatibility
config = None
if CONFIG_MANAGER_AVAILABLE:
    try:
        config_dict = get_config_manager().merged_config
        config = ConfigObject(config_dict)
    except Exception:
        # Fallback to basic config structure
        fallback_config = {
            "logging": {
                "level": "INFO",
                "file_path": None
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8354
            }
        }
        config = ConfigObject(fallback_config)
