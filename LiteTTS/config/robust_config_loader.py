#!/usr/bin/env python3
"""
Robust Configuration Loader for LiteTTS
Properly loads and applies all settings from config/settings.json with full hierarchy support
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ConfigurationSource:
    """Information about where a configuration value came from"""
    file_path: str
    section: str
    key: str
    value: Any
    precedence: int  # Lower number = higher precedence

@dataclass
class LoadedConfiguration:
    """Complete loaded configuration with source tracking"""
    values: Dict[str, Any] = field(default_factory=dict)
    sources: Dict[str, ConfigurationSource] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class RobustConfigurationLoader:
    """
    Robust configuration loader that properly handles nested JSON structures
    and maintains clear precedence hierarchy
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.config_files = [
            ("override.json", 1),           # Highest precedence
            ("config/settings.json", 2),   # Main configuration
            ("config.json", 3),            # Legacy configuration
            ("config/production.json", 4), # Production defaults
        ]
        
        logger.info("Robust Configuration Loader initialized")
    
    def load_configuration(self) -> LoadedConfiguration:
        """Load configuration from all available sources with proper precedence"""
        logger.info("🔧 Loading configuration with robust loader...")
        
        loaded_config = LoadedConfiguration()
        
        # Load from each configuration file in precedence order
        for config_file, precedence in self.config_files:
            file_path = self.base_path / config_file
            
            if file_path.exists():
                logger.info(f"📄 Loading configuration from: {config_file}")
                self._load_config_file(file_path, precedence, loaded_config)
            else:
                logger.debug(f"📄 Configuration file not found: {config_file}")
        
        # Apply configuration hierarchy
        final_config = self._apply_configuration_hierarchy(loaded_config)
        
        # Log configuration summary
        self._log_configuration_summary(loaded_config)
        
        return final_config
    
    def _load_config_file(self, file_path: Path, precedence: int, loaded_config: LoadedConfiguration):
        """Load a single configuration file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Flatten nested configuration for easier access
            flattened = self._flatten_config(data)
            
            # Store each configuration value with its source
            for key, value in flattened.items():
                source = ConfigurationSource(
                    file_path=str(file_path),
                    section=self._get_section_from_key(key),
                    key=key,
                    value=value,
                    precedence=precedence
                )
                
                # Only store if this has higher precedence (lower number)
                if key not in loaded_config.sources or precedence < loaded_config.sources[key].precedence:
                    loaded_config.values[key] = value
                    loaded_config.sources[key] = source
            
            logger.info(f"✅ Loaded {len(flattened)} settings from {file_path.name}")
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in {file_path}: {e}"
            logger.error(error_msg)
            loaded_config.errors.append(error_msg)
        except Exception as e:
            error_msg = f"Failed to load {file_path}: {e}"
            logger.error(error_msg)
            loaded_config.errors.append(error_msg)
    
    def _flatten_config(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested configuration dictionary"""
        flattened = {}
        
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                nested = self._flatten_config(value, full_key)
                flattened.update(nested)
            else:
                # Store the value
                flattened[full_key] = value
        
        return flattened
    
    def _get_section_from_key(self, key: str) -> str:
        """Extract section name from flattened key"""
        return key.split('.')[0] if '.' in key else 'root'
    
    def _apply_configuration_hierarchy(self, loaded_config: LoadedConfiguration) -> LoadedConfiguration:
        """Apply configuration hierarchy and resolve conflicts"""
        # Configuration is already applied during loading based on precedence
        # This method can be extended for additional processing
        
        # Validate critical settings
        self._validate_configuration(loaded_config)
        
        return loaded_config
    
    def _validate_configuration(self, loaded_config: LoadedConfiguration):
        """Validate loaded configuration values"""
        validations = [
            ("performance.max_memory_mb", lambda x: isinstance(x, (int, float)) and x > 0, "Must be positive number"),
            ("performance.cpu_target", lambda x: isinstance(x, (int, float)) and 0 < x <= 100, "Must be between 0 and 100"),
            ("cache.max_size_mb", lambda x: isinstance(x, (int, float)) and x > 0, "Must be positive number"),
            ("server.port", lambda x: isinstance(x, int) and 1024 <= x <= 65535, "Must be valid port number"),
        ]
        
        for key, validator, error_msg in validations:
            if key in loaded_config.values:
                value = loaded_config.values[key]
                if not validator(value):
                    warning = f"Invalid value for {key}: {value} - {error_msg}"
                    logger.warning(warning)
                    loaded_config.warnings.append(warning)
    
    def _log_configuration_summary(self, loaded_config: LoadedConfiguration):
        """Log comprehensive configuration summary"""
        logger.info("📋 Configuration Loading Summary:")
        logger.info(f"   Total settings loaded: {len(loaded_config.values)}")
        logger.info(f"   Errors: {len(loaded_config.errors)}")
        logger.info(f"   Warnings: {len(loaded_config.warnings)}")
        
        # Log critical settings with their sources
        critical_settings = [
            "performance.max_memory_mb",
            "performance.cpu_target", 
            "cache.max_size_mb",
            "server.port",
            "performance.memory_optimization",
            "performance.dynamic_cpu_allocation.enabled"
        ]
        
        logger.info("🔍 Critical Settings:")
        for setting in critical_settings:
            if setting in loaded_config.values:
                value = loaded_config.values[setting]
                source = loaded_config.sources[setting]
                logger.info(f"   {setting}: {value} (from {Path(source.file_path).name})")
            else:
                logger.warning(f"   {setting}: NOT FOUND")
        
        # Log errors and warnings
        for error in loaded_config.errors:
            logger.error(f"   ❌ {error}")
        
        for warning in loaded_config.warnings:
            logger.warning(f"   ⚠️ {warning}")
    
    def get_setting(self, loaded_config: LoadedConfiguration, key: str, default: Any = None) -> Any:
        """Get a specific setting value with fallback to default"""
        return loaded_config.values.get(key, default)
    
    def get_setting_source(self, loaded_config: LoadedConfiguration, key: str) -> Optional[ConfigurationSource]:
        """Get the source information for a specific setting"""
        return loaded_config.sources.get(key)
    
    def export_effective_config(self, loaded_config: LoadedConfiguration) -> Dict[str, Any]:
        """Export the effective configuration as a nested dictionary"""
        nested_config = {}
        
        for key, value in loaded_config.values.items():
            self._set_nested_value(nested_config, key, value)
        
        return nested_config
    
    def _set_nested_value(self, config: Dict[str, Any], key: str, value: Any):
        """Set a value in a nested dictionary using dot notation"""
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value

class ConfigurationApplicator:
    """
    Applies loaded configuration to the actual application components
    """
    
    def __init__(self, loaded_config: LoadedConfiguration):
        self.loaded_config = loaded_config
        self.loader = RobustConfigurationLoader()
        
    def apply_to_performance_monitor(self, performance_monitor):
        """Apply configuration to performance monitor"""
        try:
            # Apply memory settings
            max_memory = self.loader.get_setting(self.loaded_config, "performance.max_memory_mb", 150)
            if hasattr(performance_monitor, 'set_memory_limit'):
                performance_monitor.set_memory_limit(max_memory)
                logger.info(f"✅ Applied memory limit: {max_memory}MB")
            
            # Apply CPU settings
            cpu_target = self.loader.get_setting(self.loaded_config, "performance.cpu_target", 50.0)
            if hasattr(performance_monitor, 'set_cpu_target'):
                performance_monitor.set_cpu_target(cpu_target)
                logger.info(f"✅ Applied CPU target: {cpu_target}%")
            
        except Exception as e:
            logger.error(f"Failed to apply performance monitor configuration: {e}")
    
    def apply_to_cache_manager(self, cache_manager):
        """Apply configuration to cache manager"""
        try:
            # Apply cache size settings
            cache_size = self.loader.get_setting(self.loaded_config, "cache.max_size_mb", 32)
            if hasattr(cache_manager, 'set_max_size'):
                cache_manager.set_max_size(cache_size * 1024 * 1024)  # Convert to bytes
                logger.info(f"✅ Applied cache size: {cache_size}MB")
            
        except Exception as e:
            logger.error(f"Failed to apply cache manager configuration: {e}")
    
    def apply_to_server_config(self, server_config):
        """Apply configuration to server configuration"""
        try:
            # Apply server settings
            port = self.loader.get_setting(self.loaded_config, "server.port", 8355)
            if hasattr(server_config, 'port'):
                server_config.port = port
                logger.info(f"✅ Applied server port: {port}")
            
        except Exception as e:
            logger.error(f"Failed to apply server configuration: {e}")

def load_and_apply_configuration(base_path: str = ".") -> LoadedConfiguration:
    """Convenience function to load and return configuration"""
    loader = RobustConfigurationLoader(base_path)
    return loader.load_configuration()

def main():
    """Test the configuration loader"""
    loader = RobustConfigurationLoader()
    config = loader.load_configuration()
    
    print("Configuration loaded successfully!")
    print(f"Total settings: {len(config.values)}")
    
    # Test specific settings
    test_settings = [
        "performance.max_memory_mb",
        "performance.cpu_target",
        "cache.max_size_mb"
    ]
    
    for setting in test_settings:
        value = loader.get_setting(config, setting)
        source = loader.get_setting_source(config, setting)
        if source:
            print(f"{setting}: {value} (from {Path(source.file_path).name})")
        else:
            print(f"{setting}: NOT FOUND")

if __name__ == "__main__":
    main()
