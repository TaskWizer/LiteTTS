#!/usr/bin/env python3
"""
Configuration Manager for LiteTTS
Bridges user-friendly config.json with internal technical configuration
"""

import json
import os
import sys
from typing import Dict, Any, Optional
import logging

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from LiteTTS.config.internal_config import get_internal_config, InternalConfig
except ImportError:
    # Fallback for direct execution
    from internal_config import get_internal_config, InternalConfig

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages both user-facing and internal configuration"""
    
    def __init__(self, config_path: str = None):
        # Determine config file location with preference for comprehensive settings
        if config_path is None:
            from pathlib import Path
            if Path("config/settings.json").exists():
                config_path = "config/settings.json"
            else:
                config_path = "config.json"  # Fallback for backward compatibility

        self.config_path = config_path
        self.user_config = self._load_user_config()
        self.internal_config = get_internal_config()
        self.merged_config = self._merge_configs()
        
    def _load_user_config(self) -> Dict[str, Any]:
        """Load user-facing configuration from config.json"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded user configuration from {self.config_path}")
                return config
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self._get_default_user_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.config_path}: {e}")
            return self._get_default_user_config()
        except Exception as e:
            logger.error(f"Error loading config from {self.config_path}: {e}")
            return self._get_default_user_config()
    
    def _get_default_user_config(self) -> Dict[str, Any]:
        """Get default user configuration"""
        return {
            "model": {
                "name": "LiteTTS",
                "type": "style_text_to_speech_2",
                "version": "1.0.0",
                "default_variant": "model_q4.onnx",
                "auto_discovery": True,
                "cache_models": True,
                "owner": "TaskWizer"
            },
            "voice": {
                "default_voice": "af_heart",
                "auto_discovery": True,
                "preload_default_voices": True
            },
            "audio": {
                "format": "mp3",
                "speed": 1.0,
                "language": "en-us",
                "quality": {
                    "sample_rate": 24000,
                    "mp3_bitrate": 96,
                    "enable_normalization": True
                },
                "streaming": {
                    "enabled": True,
                    "chunk_duration": 0.8
                }
            },
            "server": {
                "port": 8354,
                "host": "0.0.0.0",
                "environment": "production"
            },
            "performance": {
                "cache_enabled": True,
                "preload_models": True,
                "auto_optimize": True,
                "max_text_length": 3000
            },
            "text_processing": {
                "natural_speech": True,
                "pronunciation_fixes": True,
                "expand_contractions": False
            },
            "cache": {
                "enabled": True,
                "auto_optimize": True
            },
            "monitoring": {
                "enabled": True
            },
            "application": {
                "name": "Kokoro ONNX TTS API",
                "description": "High-quality text-to-speech service with ONNX optimization and natural pronunciation",
                "version": "1.0.0"
            }
        }
    
    def _merge_configs(self) -> Dict[str, Any]:
        """Merge user config with internal config based on user preferences"""
        merged = self.user_config.copy()
        
        # Map user settings to internal configuration
        text_processing = merged.get('text_processing', {})
        
        # Apply text processing preferences
        if text_processing.get('natural_speech', True):
            # Enable natural speech processing
            merged['use_pronunciation_rules'] = True
            merged['use_interjection_fixes'] = True

            # Respect pronunciation_dictionary.enabled setting
            pronunciation_dict = merged.get('pronunciation_dictionary', {})
            if pronunciation_dict.get('enabled', False):
                merged['use_proper_name_pronunciation'] = pronunciation_dict.get('proper_name_pronunciation', True)
                merged['use_ticker_symbol_processing'] = pronunciation_dict.get('ticker_symbol_processing', True)
            else:
                # If pronunciation dictionary is disabled, disable these features
                merged['use_proper_name_pronunciation'] = False
                merged['use_ticker_symbol_processing'] = False
        
        if text_processing.get('pronunciation_fixes', True):
            # Enable pronunciation fixes
            merged['use_pronunciation_rules'] = True
            merged['use_proper_name_pronunciation'] = True
        
        if text_processing.get('expand_contractions', False):
            # Enable legacy contraction expansion
            merged['use_phonetic_contractions'] = True
            merged['use_pronunciation_rules'] = False
        
        # Apply performance preferences
        performance = merged.get('performance', {})
        if performance.get('auto_optimize', True):
            # Enable automatic optimization
            merged['auto_optimize_enabled'] = True
        
        # Apply cache preferences
        cache = merged.get('cache', {})
        if cache.get('auto_optimize', True):
            # Enable automatic cache optimization
            merged['auto_cache_optimize'] = True
        
        # Add internal configuration sections
        internal_config = self.internal_config.get_all_config()
        for section, config in internal_config.items():
            merged[f'internal_{section}'] = config
        
        return merged
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        keys = key.split('.')
        value = self.merged_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_user_config(self) -> Dict[str, Any]:
        """Get the user-facing configuration"""
        return self.user_config.copy()
    
    def get_internal_config(self) -> Dict[str, Any]:
        """Get the internal configuration"""
        return self.internal_config.get_all_config()
    
    def get_merged_config(self) -> Dict[str, Any]:
        """Get the merged configuration"""
        return self.merged_config.copy()
    
    def update_user_config(self, updates: Dict[str, Any]):
        """Update user configuration and save to file"""
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(self.user_config, updates)
        self._save_user_config()
        self.merged_config = self._merge_configs()
        logger.info("User configuration updated and saved")
    
    def _save_user_config(self):
        """Save user configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.user_config, f, indent=2)
            logger.info(f"Saved user configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save user configuration: {e}")
    
    def override_internal_setting(self, section: str, key: str, value: Any):
        """Override an internal setting (for advanced users)"""
        self.internal_config.override_setting(section, key, value)
        self.merged_config = self._merge_configs()
        logger.info(f"Overrode internal setting: {section}.{key} = {value}")
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        feature_map = {
            'natural_speech': self.get('text_processing.natural_speech', True),
            'pronunciation_fixes': self.get('text_processing.pronunciation_fixes', True),
            'expand_contractions': self.get('text_processing.expand_contractions', False),
            'auto_optimize': self.get('performance.auto_optimize', True),
            'cache_enabled': self.get('cache.enabled', True),
            'monitoring': self.get('monitoring.enabled', True),
            'streaming': self.get('audio.streaming.enabled', True)
        }
        
        return feature_map.get(feature, False)
    
    def get_processing_options(self) -> Dict[str, bool]:
        """Get processing options for the unified text processor"""
        # Respect pronunciation_dictionary.enabled setting
        pronunciation_dict = self.get('pronunciation_dictionary', {})
        pronunciation_dict_enabled = pronunciation_dict.get('enabled', False)

        return {
            'use_pronunciation_rules': self.get('use_pronunciation_rules', True),
            'use_interjection_fixes': self.get('use_interjection_fixes', True),
            'use_proper_name_pronunciation': pronunciation_dict_enabled and pronunciation_dict.get('proper_name_pronunciation', True),
            'use_ticker_symbol_processing': pronunciation_dict_enabled and pronunciation_dict.get('ticker_symbol_processing', True),
            'use_phonetic_contractions': self.get('use_phonetic_contractions', False),
            'use_advanced_currency': self.get('use_advanced_currency', True),
            'use_enhanced_datetime': self.get('use_enhanced_datetime', True),
            'use_advanced_symbols': self.get('use_advanced_symbols', True),
            'use_clean_normalizer': self.get('use_clean_normalizer', True)
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate the current configuration"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Validate required sections
        required_sections = ['model', 'voice', 'audio', 'server']
        for section in required_sections:
            if section not in self.user_config:
                validation['errors'].append(f"Missing required section: {section}")
                validation['valid'] = False
        
        # Validate audio settings
        audio = self.user_config.get('audio', {})
        if audio.get('speed', 1.0) < 0.1 or audio.get('speed', 1.0) > 3.0:
            validation['warnings'].append("Audio speed should be between 0.1 and 3.0")
        
        # Validate server settings
        server = self.user_config.get('server', {})
        port = server.get('port', 8354)
        if not isinstance(port, int) or port < 1024 or port > 65535:
            validation['warnings'].append("Server port should be between 1024 and 65535")
        
        # Check for conflicting settings
        text_processing = self.user_config.get('text_processing', {})
        if text_processing.get('expand_contractions', False) and text_processing.get('natural_speech', True):
            validation['warnings'].append("Contraction expansion conflicts with natural speech - natural speech will take precedence")
        
        return validation

# Global instance
_config_manager = None

def get_config_manager(config_path: str = None) -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager

def reload_config():
    """Reload the configuration"""
    global _config_manager
    _config_manager = None
    return get_config_manager()

# Example usage
if __name__ == "__main__":
    config = get_config_manager()
    
    print("🔧 Configuration Manager")
    print("=" * 30)
    
    # Show user config
    print("\n📁 User Configuration:")
    user_config = config.get_user_config()
    for section, settings in user_config.items():
        print(f"  {section}: {type(settings).__name__}")
    
    # Show processing options
    print(f"\n⚙️  Processing Options:")
    options = config.get_processing_options()
    for option, enabled in options.items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {option}")
    
    # Validate config
    print(f"\n🔍 Configuration Validation:")
    validation = config.validate_config()
    print(f"  Valid: {validation['valid']}")
    if validation['errors']:
        print(f"  Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"  Warnings: {validation['warnings']}")
    
    # Test feature checks
    print(f"\n🎛️  Feature Status:")
    features = ['natural_speech', 'pronunciation_fixes', 'auto_optimize', 'cache_enabled']
    for feature in features:
        enabled = config.is_feature_enabled(feature)
        status = "✅" if enabled else "❌"
        print(f"  {status} {feature}")
