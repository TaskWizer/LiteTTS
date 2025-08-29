#!/usr/bin/env python3
"""
Integrated Configuration System for LiteTTS
Replaces the broken configuration system with robust loading and application
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

try:
    from .robust_config_loader import RobustConfigurationLoader, LoadedConfiguration, ConfigurationApplicator
except ImportError:
    # Handle direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from robust_config_loader import RobustConfigurationLoader, LoadedConfiguration, ConfigurationApplicator

logger = logging.getLogger(__name__)

@dataclass
class IntegratedConfigurationManager:
    """
    Integrated configuration manager that properly loads and applies all settings
    from config/settings.json with full hierarchy support
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.loader = RobustConfigurationLoader(base_path)
        self.loaded_config: Optional[LoadedConfiguration] = None
        self.applicator: Optional[ConfigurationApplicator] = None
        
        # Load configuration immediately
        self.reload_configuration()
        
        logger.info("✅ Integrated Configuration Manager initialized")
    
    def reload_configuration(self):
        """Reload configuration from all sources"""
        logger.info("🔄 Reloading configuration...")
        
        self.loaded_config = self.loader.load_configuration()
        self.applicator = ConfigurationApplicator(self.loaded_config)
        
        # Log critical settings that are now properly loaded
        self._log_critical_settings()
        
        logger.info("✅ Configuration reloaded successfully")
    
    def _log_critical_settings(self):
        """Log critical settings to verify they're properly loaded"""
        critical_settings = [
            ("performance.dynamic_cpu_allocation.cpu_target", "CPU Target"),
            ("performance.max_memory_mb", "Max Memory"),
            ("cache.max_size_mb", "Cache Size"),
            ("server.port", "Server Port"),
            ("performance.memory_optimization", "Memory Optimization"),
            ("performance.dynamic_cpu_allocation.enabled", "Dynamic CPU Allocation"),
            ("performance.dynamic_cpu_allocation.aggressive_mode", "Aggressive CPU Mode"),
            ("tts.device", "TTS Device"),
            ("voice.default_voice", "Default Voice"),
        ]
        
        logger.info("📋 Critical Configuration Settings:")
        for setting_key, display_name in critical_settings:
            value = self.get_setting(setting_key)
            source = self.get_setting_source(setting_key)
            
            if source:
                source_file = Path(source.file_path).name
                logger.info(f"   ✅ {display_name}: {value} (from {source_file})")
            else:
                logger.warning(f"   ❌ {display_name}: NOT FOUND")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting value"""
        if not self.loaded_config:
            return default
        return self.loader.get_setting(self.loaded_config, key, default)
    
    def get_setting_source(self, key: str):
        """Get the source information for a setting"""
        if not self.loaded_config:
            return None
        return self.loader.get_setting_source(self.loaded_config, key)
    
    def apply_to_performance_components(self, performance_monitor=None, cpu_monitor=None, memory_optimizer=None):
        """Apply configuration to performance components"""
        if not self.applicator:
            logger.error("Configuration applicator not available")
            return
        
        logger.info("🔧 Applying configuration to performance components...")
        
        try:
            # Apply to performance monitor
            if performance_monitor:
                self.applicator.apply_to_performance_monitor(performance_monitor)
            
            # Apply CPU settings
            if cpu_monitor:
                cpu_target = self.get_setting("performance.dynamic_cpu_allocation.cpu_target", 50.0)
                aggressive_mode = self.get_setting("performance.dynamic_cpu_allocation.aggressive_mode", False)
                
                if hasattr(cpu_monitor, 'set_cpu_target'):
                    cpu_monitor.set_cpu_target(cpu_target)
                    logger.info(f"✅ Applied CPU target: {cpu_target}%")
                
                if hasattr(cpu_monitor, 'set_aggressive_mode'):
                    cpu_monitor.set_aggressive_mode(aggressive_mode)
                    logger.info(f"✅ Applied aggressive mode: {aggressive_mode}")
            
            # Apply memory settings
            if memory_optimizer:
                max_memory = self.get_setting("performance.max_memory_mb", 150)
                memory_optimization = self.get_setting("performance.memory_optimization", True)
                
                if hasattr(memory_optimizer, 'set_memory_limit'):
                    memory_optimizer.set_memory_limit(max_memory)
                    logger.info(f"✅ Applied memory limit: {max_memory}MB")
                
                if hasattr(memory_optimizer, 'set_optimization_enabled'):
                    memory_optimizer.set_optimization_enabled(memory_optimization)
                    logger.info(f"✅ Applied memory optimization: {memory_optimization}")
            
            logger.info("✅ Configuration applied to performance components")
            
        except Exception as e:
            logger.error(f"❌ Failed to apply configuration to performance components: {e}")
    
    def apply_to_cache_components(self, cache_manager=None, intelligent_cache=None):
        """Apply configuration to cache components"""
        if not self.applicator:
            logger.error("Configuration applicator not available")
            return
        
        logger.info("🔧 Applying configuration to cache components...")
        
        try:
            # Apply cache settings
            cache_size_mb = self.get_setting("cache.max_size_mb", 32)
            cache_enabled = self.get_setting("cache.enabled", True)
            
            if cache_manager:
                if hasattr(cache_manager, 'set_max_size'):
                    cache_manager.set_max_size(cache_size_mb * 1024 * 1024)  # Convert to bytes
                    logger.info(f"✅ Applied cache size: {cache_size_mb}MB")
                
                if hasattr(cache_manager, 'set_enabled'):
                    cache_manager.set_enabled(cache_enabled)
                    logger.info(f"✅ Applied cache enabled: {cache_enabled}")
            
            if intelligent_cache:
                # Apply intelligent cache settings
                warm_on_startup = self.get_setting("cache.warm_cache_on_startup", True)
                preload_common = self.get_setting("cache.preload_common_phrases", True)
                
                if hasattr(intelligent_cache, 'set_warm_on_startup'):
                    intelligent_cache.set_warm_on_startup(warm_on_startup)
                    logger.info(f"✅ Applied warm on startup: {warm_on_startup}")
                
                if hasattr(intelligent_cache, 'set_preload_common'):
                    intelligent_cache.set_preload_common(preload_common)
                    logger.info(f"✅ Applied preload common phrases: {preload_common}")
            
            logger.info("✅ Configuration applied to cache components")
            
        except Exception as e:
            logger.error(f"❌ Failed to apply configuration to cache components: {e}")
    
    def apply_to_server_components(self, server_config=None, app_config=None):
        """Apply configuration to server components"""
        logger.info("🔧 Applying configuration to server components...")
        
        try:
            # Apply server settings
            port = self.get_setting("server.port", 8355)
            host = self.get_setting("server.host", "0.0.0.0")
            workers = self.get_setting("server.workers", 1)
            
            if server_config:
                if hasattr(server_config, 'port'):
                    server_config.port = port
                    logger.info(f"✅ Applied server port: {port}")
                
                if hasattr(server_config, 'host'):
                    server_config.host = host
                    logger.info(f"✅ Applied server host: {host}")
                
                if hasattr(server_config, 'workers'):
                    server_config.workers = workers
                    logger.info(f"✅ Applied server workers: {workers}")
            
            # Apply application settings
            if app_config:
                app_name = self.get_setting("application.name", "LiteTTS")
                app_version = self.get_setting("application.version", "1.0.0")
                app_description = self.get_setting("application.description", "High-quality TTS service")
                
                if hasattr(app_config, 'name'):
                    app_config.name = app_name
                    logger.info(f"✅ Applied app name: {app_name}")
                
                if hasattr(app_config, 'version'):
                    app_config.version = app_version
                    logger.info(f"✅ Applied app version: {app_version}")
                
                if hasattr(app_config, 'description'):
                    app_config.description = app_description
                    logger.info(f"✅ Applied app description: {app_description}")
            
            logger.info("✅ Configuration applied to server components")
            
        except Exception as e:
            logger.error(f"❌ Failed to apply configuration to server components: {e}")
    
    def get_effective_config_dict(self) -> Dict[str, Any]:
        """Get the effective configuration as a nested dictionary"""
        if not self.loaded_config:
            return {}
        
        return self.loader.export_effective_config(self.loaded_config)
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the configuration loading results"""
        if not self.loaded_config:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "total_settings": len(self.loaded_config.values),
            "errors": len(self.loaded_config.errors),
            "warnings": len(self.loaded_config.warnings),
            "sources": list(set(source.file_path for source in self.loaded_config.sources.values())),
            "critical_settings_found": self._count_critical_settings_found(),
            "errors_list": self.loaded_config.errors,
            "warnings_list": self.loaded_config.warnings
        }
    
    def _count_critical_settings_found(self) -> int:
        """Count how many critical settings were found"""
        critical_settings = [
            "performance.dynamic_cpu_allocation.cpu_target",
            "performance.max_memory_mb",
            "cache.max_size_mb",
            "server.port",
            "performance.memory_optimization",
            "performance.dynamic_cpu_allocation.enabled",
        ]
        
        found_count = 0
        for setting in critical_settings:
            if self.get_setting(setting) is not None:
                found_count += 1
        
        return found_count
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the loaded configuration"""
        validation_results = {
            "valid": True,
            "issues": [],
            "critical_missing": [],
            "recommendations": []
        }
        
        # Check critical settings
        critical_checks = [
            ("performance.dynamic_cpu_allocation.cpu_target", lambda x: 0 < x <= 100, "CPU target must be between 0 and 100"),
            ("performance.max_memory_mb", lambda x: x > 0, "Max memory must be positive"),
            ("cache.max_size_mb", lambda x: x > 0, "Cache size must be positive"),
            ("server.port", lambda x: 1024 <= x <= 65535, "Port must be between 1024 and 65535"),
        ]
        
        for setting, validator, error_msg in critical_checks:
            value = self.get_setting(setting)
            if value is None:
                validation_results["critical_missing"].append(setting)
                validation_results["valid"] = False
            elif not validator(value):
                validation_results["issues"].append(f"{setting}: {error_msg} (current: {value})")
                validation_results["valid"] = False
        
        # Add recommendations
        if self.get_setting("performance.dynamic_cpu_allocation.aggressive_mode", False):
            validation_results["recommendations"].append("Aggressive CPU mode is enabled - monitor system stability")
        
        if self.get_setting("cache.max_size_mb", 0) > 512:
            validation_results["recommendations"].append("Large cache size configured - ensure sufficient system memory")
        
        return validation_results

# Global integrated configuration manager instance
_integrated_config_manager: Optional[IntegratedConfigurationManager] = None

def get_integrated_config_manager() -> IntegratedConfigurationManager:
    """Get or create the global integrated configuration manager"""
    global _integrated_config_manager
    if _integrated_config_manager is None:
        _integrated_config_manager = IntegratedConfigurationManager()
    return _integrated_config_manager

def reload_integrated_configuration():
    """Reload the integrated configuration"""
    global _integrated_config_manager
    if _integrated_config_manager:
        _integrated_config_manager.reload_configuration()
    else:
        _integrated_config_manager = IntegratedConfigurationManager()
    return _integrated_config_manager

def main():
    """Test the integrated configuration system"""
    config_manager = IntegratedConfigurationManager()
    
    print("🔧 Integrated Configuration System Test")
    print("=" * 50)
    
    # Get configuration summary
    summary = config_manager.get_configuration_summary()
    print(f"Status: {summary['status']}")
    print(f"Total settings: {summary['total_settings']}")
    print(f"Critical settings found: {summary['critical_settings_found']}")
    print(f"Errors: {summary['errors']}")
    print(f"Warnings: {summary['warnings']}")
    
    # Validate configuration
    validation = config_manager.validate_configuration()
    print(f"\nValidation: {'✅ PASSED' if validation['valid'] else '❌ FAILED'}")
    
    if validation['issues']:
        print("Issues:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    
    if validation['critical_missing']:
        print("Critical missing:")
        for missing in validation['critical_missing']:
            print(f"  - {missing}")

if __name__ == "__main__":
    main()
