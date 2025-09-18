#!/usr/bin/env python3
"""
Whisper Configuration Loader for LiteTTS
Handles loading configuration from JSON files and environment variables
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WhisperSettings:
    """Whisper configuration settings"""
    # Core Whisper settings
    default_model: str = "distil-small.en"
    implementation: str = "faster-whisper"
    quantization: str = "int8"
    cpu_threads: int = 4
    device: str = "cpu"
    fallback_model: str = "openai-whisper-base"
    model_cache_dir: str = "./models/whisper_cache"
    beam_size: int = 5
    language: str = "en"
    condition_on_previous_text: bool = False
    enable_fallback: bool = True
    
    # Performance thresholds
    rtf_threshold: float = 1.0
    memory_threshold_mb: float = 2000
    cpu_threshold_percent: float = 85
    
    # Voice cloning settings
    max_audio_duration: float = 120.0
    max_segment_duration: float = 30.0
    segment_overlap: float = 2.0
    max_reference_clips: int = 5
    enable_enhanced_mode: bool = True
    
    # Monitoring settings
    enable_monitoring: bool = True
    enable_filesystem_monitoring: bool = True
    log_performance_metrics: bool = True
    
    # Edge hardware profile
    edge_hardware_profile: str = "auto"

class WhisperConfigLoader:
    """
    Configuration loader for Whisper settings with environment variable support
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "LiteTTS/config/whisper_settings.json"
        self.config_data = {}
        self.settings = WhisperSettings()
        
        # Load configuration
        self._load_config()
        self._apply_environment_variables()
        self._validate_config()
        
    def _load_config(self):
        """Load configuration from JSON file"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    self.config_data = json.load(f)
                logger.info(f"Loaded Whisper configuration from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load config from {config_path}: {e}")
                self.config_data = {}
        else:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            self.config_data = {}
            
    def _apply_environment_variables(self):
        """Apply environment variable overrides"""
        env_mappings = self.config_data.get("environment_variables", {})
        
        for env_var, config_info in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                config_path = config_info.get("config_path", "")
                default_value = config_info.get("default")
                
                # Convert environment variable to appropriate type
                try:
                    if isinstance(default_value, bool):
                        env_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif isinstance(default_value, int):
                        env_value = int(env_value)
                    elif isinstance(default_value, float):
                        env_value = float(env_value)
                    # String values remain as-is
                    
                    # Apply to configuration
                    self._set_nested_config(config_path, env_value)
                    logger.info(f"Applied environment variable {env_var}={env_value}")
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid environment variable {env_var}={env_value}: {e}")
                    
    def _set_nested_config(self, config_path: str, value: Any):
        """Set nested configuration value using dot notation"""
        if not config_path:
            return
            
        keys = config_path.split('.')
        current = self.config_data
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        # Set the final value
        current[keys[-1]] = value
        
    def _validate_config(self):
        """Validate and apply configuration to settings"""
        whisper_config = self.config_data.get("whisper", {})
        voice_config = self.config_data.get("voice_cloning", {})
        monitoring_config = self.config_data.get("performance_monitoring", {})
        filesystem_config = self.config_data.get("filesystem_monitoring", {})
        edge_config = self.config_data.get("edge_hardware", {})
        
        # Apply Whisper settings
        self.settings.default_model = whisper_config.get("default_model", self.settings.default_model)
        self.settings.implementation = whisper_config.get("implementation", self.settings.implementation)
        self.settings.quantization = whisper_config.get("quantization", self.settings.quantization)
        self.settings.cpu_threads = whisper_config.get("cpu_threads", self.settings.cpu_threads)
        self.settings.device = whisper_config.get("device", self.settings.device)
        self.settings.fallback_model = whisper_config.get("fallback_model", self.settings.fallback_model)
        self.settings.model_cache_dir = whisper_config.get("model_cache_dir", self.settings.model_cache_dir)
        self.settings.beam_size = whisper_config.get("beam_size", self.settings.beam_size)
        self.settings.language = whisper_config.get("language", self.settings.language)
        self.settings.condition_on_previous_text = whisper_config.get("condition_on_previous_text", self.settings.condition_on_previous_text)
        self.settings.enable_fallback = whisper_config.get("enable_fallback", self.settings.enable_fallback)
        
        # Apply voice cloning settings
        self.settings.max_audio_duration = voice_config.get("max_audio_duration", self.settings.max_audio_duration)
        self.settings.max_segment_duration = voice_config.get("max_segment_duration", self.settings.max_segment_duration)
        self.settings.segment_overlap = voice_config.get("segment_overlap", self.settings.segment_overlap)
        self.settings.max_reference_clips = voice_config.get("max_reference_clips", self.settings.max_reference_clips)
        self.settings.enable_enhanced_mode = voice_config.get("enable_enhanced_mode", self.settings.enable_enhanced_mode)
        
        # Apply monitoring settings
        self.settings.enable_monitoring = monitoring_config.get("enable_monitoring", self.settings.enable_monitoring)
        self.settings.rtf_threshold = monitoring_config.get("rtf_threshold", self.settings.rtf_threshold)
        self.settings.memory_threshold_mb = monitoring_config.get("memory_threshold_mb", self.settings.memory_threshold_mb)
        self.settings.cpu_threshold_percent = monitoring_config.get("cpu_threshold_percent", self.settings.cpu_threshold_percent)
        self.settings.log_performance_metrics = monitoring_config.get("log_performance_metrics", self.settings.log_performance_metrics)
        
        # Apply filesystem monitoring settings
        self.settings.enable_filesystem_monitoring = filesystem_config.get("enable_realtime", self.settings.enable_filesystem_monitoring)
        
        # Apply edge hardware settings
        profile = os.environ.get("EDGE_HARDWARE_PROFILE", edge_config.get("auto_detect", "auto"))
        self.settings.edge_hardware_profile = profile
        
        # Auto-detect and apply edge hardware optimizations
        if self.settings.edge_hardware_profile == "auto":
            self._auto_detect_hardware()
        else:
            self._apply_hardware_profile(self.settings.edge_hardware_profile)
            
        # Validate critical settings
        self._validate_critical_settings()
        
    def _auto_detect_hardware(self):
        """Auto-detect hardware and apply appropriate optimizations"""
        try:
            import psutil
            import platform
            
            # Get system information
            cpu_count = psutil.cpu_count(logical=False)
            memory_gb = psutil.virtual_memory().total / (1024**3)
            architecture = platform.machine().lower()
            
            # Simple hardware detection logic
            if "arm" in architecture or "aarch64" in architecture:
                if memory_gb >= 4:
                    profile = "raspberry_pi_4"
                else:
                    profile = "generic_low_power"
            elif "x86_64" in architecture or "amd64" in architecture:
                if cpu_count <= 4 and memory_gb <= 8:
                    profile = "intel_atom_n5105"
                else:
                    profile = "generic_low_power"  # Conservative default
            else:
                profile = "generic_low_power"
                
            logger.info(f"Auto-detected hardware profile: {profile}")
            self._apply_hardware_profile(profile)
            
        except Exception as e:
            logger.warning(f"Hardware auto-detection failed: {e}, using generic profile")
            self._apply_hardware_profile("generic_low_power")
            
    def _apply_hardware_profile(self, profile: str):
        """Apply hardware-specific optimizations"""
        profiles = self.config_data.get("edge_hardware", {}).get("optimization_profiles", {})
        
        if profile in profiles:
            profile_config = profiles[profile]
            
            # Apply profile-specific settings
            self.settings.cpu_threads = min(
                profile_config.get("cpu_threads", self.settings.cpu_threads),
                self.settings.cpu_threads
            )
            
            memory_limit = profile_config.get("memory_limit_mb", self.settings.memory_threshold_mb)
            self.settings.memory_threshold_mb = min(memory_limit, self.settings.memory_threshold_mb)
            
            # Use preferred model if available
            preferred_models = profile_config.get("preferred_models", [])
            if preferred_models and self.settings.default_model not in preferred_models:
                self.settings.default_model = preferred_models[0]
                logger.info(f"Switched to preferred model for {profile}: {self.settings.default_model}")
                
            # Apply quantization preference
            preferred_quantization = profile_config.get("quantization", self.settings.quantization)
            self.settings.quantization = preferred_quantization
            
            logger.info(f"Applied hardware profile: {profile}")
        else:
            logger.warning(f"Unknown hardware profile: {profile}")
            
    def _validate_critical_settings(self):
        """Validate critical configuration settings"""
        # Ensure CPU threads is reasonable
        try:
            import psutil
            max_threads = psutil.cpu_count(logical=False)
            if self.settings.cpu_threads > max_threads:
                logger.warning(f"CPU threads ({self.settings.cpu_threads}) exceeds available cores ({max_threads})")
                self.settings.cpu_threads = max_threads
        except:
            pass
            
        # Ensure memory threshold is reasonable
        if self.settings.memory_threshold_mb < 500:
            logger.warning("Memory threshold too low, setting to 500MB minimum")
            self.settings.memory_threshold_mb = 500
            
        # Ensure audio duration limits are reasonable
        if self.settings.max_audio_duration < 30:
            logger.warning("Max audio duration too low, setting to 30s minimum")
            self.settings.max_audio_duration = 30
            
        if self.settings.max_audio_duration > 600:
            logger.warning("Max audio duration too high, setting to 600s maximum")
            self.settings.max_audio_duration = 600
            
        # Ensure RTF threshold is reasonable
        if self.settings.rtf_threshold < 0.1:
            logger.warning("RTF threshold too low, setting to 0.1 minimum")
            self.settings.rtf_threshold = 0.1
            
    def get_settings(self) -> WhisperSettings:
        """Get the loaded and validated settings"""
        return self.settings
        
    def get_raw_config(self) -> Dict[str, Any]:
        """Get the raw configuration data"""
        return self.config_data
        
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        model_variants = self.config_data.get("whisper", {}).get("model_variants", {})
        return model_variants.get(model_name, {})
        
    def get_fallback_chain(self) -> list:
        """Get the fallback chain configuration"""
        return self.config_data.get("fallback_strategy", {}).get("fallback_chain", [])
        
    def get_hardware_profile(self, profile_name: str) -> Dict[str, Any]:
        """Get hardware profile configuration"""
        profiles = self.config_data.get("edge_hardware", {}).get("optimization_profiles", {})
        return profiles.get(profile_name, {})
        
    def save_config(self, output_file: Optional[str] = None):
        """Save current configuration to file"""
        output_path = output_file or self.config_file
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            logger.info(f"Configuration saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

# Global configuration instance
_config_loader = None

def get_whisper_config(config_file: Optional[str] = None) -> WhisperConfigLoader:
    """Get the global Whisper configuration loader"""
    global _config_loader
    
    if _config_loader is None:
        _config_loader = WhisperConfigLoader(config_file)
        
    return _config_loader

def get_whisper_settings() -> WhisperSettings:
    """Get the current Whisper settings"""
    return get_whisper_config().get_settings()

# Example usage
if __name__ == "__main__":
    # Load configuration
    config_loader = WhisperConfigLoader()
    settings = config_loader.get_settings()
    
    print("Whisper Configuration:")
    print(f"  Model: {settings.default_model}")
    print(f"  Implementation: {settings.implementation}")
    print(f"  Quantization: {settings.quantization}")
    print(f"  CPU Threads: {settings.cpu_threads}")
    print(f"  RTF Threshold: {settings.rtf_threshold}")
    print(f"  Memory Threshold: {settings.memory_threshold_mb}MB")
    print(f"  Max Audio Duration: {settings.max_audio_duration}s")
    print(f"  Enhanced Mode: {settings.enable_enhanced_mode}")
    print(f"  Hardware Profile: {settings.edge_hardware_profile}")
    
    # Test model info
    model_info = config_loader.get_model_info(settings.default_model)
    if model_info:
        print(f"\nModel Info for {settings.default_model}:")
        print(f"  Size: {model_info.get('size_mb', 'Unknown')}MB")
        print(f"  Parameters: {model_info.get('parameters', 'Unknown')}")
        print(f"  Expected RTF (Pi4): {model_info.get('expected_rtf', {}).get('raspberry_pi_4', 'Unknown')}")
        print(f"  Memory Usage: {model_info.get('memory_usage_mb', 'Unknown')}MB")
