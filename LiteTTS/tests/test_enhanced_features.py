#!/usr/bin/env python3
"""
Test suite for enhanced Kokoro ONNX TTS API features
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Test configuration system
def test_enhanced_configuration():
    """Test the enhanced configuration system"""
    from LiteTTS.config import ConfigManager
    
    # Test with default configuration
    config = ConfigManager()
    
    # Verify new configuration sections exist
    assert hasattr(config, 'model')
    assert hasattr(config, 'voice')
    assert hasattr(config, 'audio')
    assert hasattr(config, 'server')
    assert hasattr(config, 'performance')
    assert hasattr(config, 'repository')
    assert hasattr(config, 'paths')
    
    # Test model configuration
    assert config.model.name == "kokoro"
    assert config.model.default_variant == "model_q8f16.onnx"
    assert config.model.auto_discovery == True
    
    # Test voice configuration
    assert config.voice.default_voice == "af_heart"
    assert config.voice.auto_discovery == True
    assert len(config.voice.essential_voices) > 0
    
    # Test audio configuration
    assert config.audio.default_format == "mp3"
    assert config.audio.sample_rate == 24000
    
    # Test server configuration
    assert config.server.port == 8354
    assert config.server.max_port_attempts == 10

def test_configuration_from_json():
    """Test loading configuration from JSON file"""
    from LiteTTS.config import ConfigManager
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_config = {
            "model": {
                "name": "test_model",
                "default_variant": "test_variant.onnx"
            },
            "voice": {
                "default_voice": "test_voice"
            },
            "server": {
                "port": 9999
            }
        }
        json.dump(test_config, f)
        config_file = f.name
    
    try:
        # Load configuration from file
        config = ConfigManager(config_file)
        
        # Verify loaded values
        assert config.model.name == "test_model"
        assert config.model.default_variant == "test_variant.onnx"
        assert config.voice.default_voice == "test_voice"
        assert config.server.port == 9999
        
    finally:
        Path(config_file).unlink()

def test_environment_variable_override():
    """Test environment variable configuration override"""
    import os
    from LiteTTS.config import ConfigManager
    
    # Set environment variables
    test_env = {
        "KOKORO_DEFAULT_VOICE": "env_voice",
        "PORT": "7777",
        "KOKORO_MODEL_VARIANT": "env_model.onnx"
    }
    
    with patch.dict(os.environ, test_env):
        config = ConfigManager()
        
        # Verify environment overrides
        assert config.voice.default_voice == "env_voice"
        assert config.server.port == 7777
        assert config.model.default_variant == "env_model.onnx"

def test_model_manager():
    """Test the model management system"""
    from LiteTTS.models.manager import ModelManager
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock configuration
        mock_config = Mock()
        mock_config.repository.huggingface_repo = "test/repo"
        mock_config.repository.base_url = "https://test.com"
        mock_config.repository.models_path = "onnx"
        mock_config.model.available_variants = ["model.onnx", "model_q8f16.onnx"]
        mock_config.model.default_variant = "model_q8f16.onnx"
        mock_config.model.auto_discovery = True
        mock_config.model.cache_models = True
        
        manager = ModelManager(temp_dir, mock_config)
        
        # Test model info methods
        assert manager.default_variant == "model_q8f16.onnx"
        assert manager.auto_discovery == True
        
        # Test model path generation
        model_path = manager.get_model_path("test_model.onnx")
        assert model_path == Path(temp_dir) / "test_model.onnx"

def test_voice_downloader():
    """Test the enhanced voice downloader"""
    from LiteTTS.voice.downloader import VoiceDownloader
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock configuration
        mock_config = Mock()
        mock_config.repository.huggingface_repo = "test/repo"
        mock_config.repository.base_url = "https://test.com"
        mock_config.repository.voices_path = "voices"
        mock_config.voice.auto_discovery = True
        mock_config.voice.cache_discovery = True
        mock_config.voice.discovery_cache_hours = 24
        mock_config.voice.essential_voices = ["test_voice1", "test_voice2"]
        
        downloader = VoiceDownloader(temp_dir, mock_config)
        
        # Test configuration loading
        assert downloader.auto_discovery == True
        assert downloader.cache_discovery == True
        assert downloader.cache_expiry_hours == 24

@patch('requests.get')
def test_voice_discovery(mock_get):
    """Test automatic voice discovery from HuggingFace"""
    from LiteTTS.voice.downloader import VoiceDownloader
    
    # Mock HuggingFace API response
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "type": "file",
            "path": "voices/test_voice1.bin",
            "size": 1024,
            "oid": "abc123",
            "lfs": {"oid": "def456", "size": 1024}
        },
        {
            "type": "file", 
            "path": "voices/test_voice2.bin",
            "size": 2048,
            "oid": "ghi789",
            "lfs": {"oid": "jkl012", "size": 2048}
        }
    ]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    with tempfile.TemporaryDirectory() as temp_dir:
        downloader = VoiceDownloader(temp_dir)
        
        # Test voice discovery
        result = downloader.discover_voices_from_huggingface()
        assert result == True
        
        # Verify discovered voices
        voices = downloader.get_available_voice_names()
        assert "test_voice1" in voices
        assert "test_voice2" in voices
        
        # Test voice info
        voice_info = downloader.discovered_voices["test_voice1"]
        assert voice_info.name == "test_voice1"
        assert voice_info.size == 1024
        assert voice_info.sha == "def456"

def test_hot_reload_manager():
    """Test hot reload functionality"""
    from LiteTTS.performance.hot_reload import HotReloadManager
    
    # Create mock configuration
    mock_config = Mock()
    mock_config.performance.hot_reload = True
    
    manager = HotReloadManager(mock_config)
    
    # Test manager initialization
    assert manager.enabled == True
    assert len(manager.observers) == 0
    assert len(manager.reload_callbacks) == 0
    
    # Test status
    status = manager.get_status()
    assert status["enabled"] == True
    assert status["active_watchers"] == 0

def test_fault_tolerance():
    """Test fault tolerance features"""
    from LiteTTS.performance.fault_tolerance import CircuitBreaker, RetryManager, HealthChecker
    
    # Test circuit breaker
    circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    
    @circuit_breaker
    def test_function():
        raise Exception("Test failure")
    
    # Test circuit breaker states
    assert circuit_breaker.state == "CLOSED"
    
    # Test retry manager
    @RetryManager.retry_with_backoff(max_retries=2, base_delay=0.1)
    def test_retry_function():
        raise Exception("Test failure")
    
    with pytest.raises(Exception):
        test_retry_function()
    
    # Test health checker
    health_checker = HealthChecker()
    
    def test_health_check():
        return True
    
    health_checker.register_check("test", test_health_check, interval=1)
    result = health_checker.run_check("test")
    assert result == True

def test_performance_monitor():
    """Test performance monitoring"""
    from LiteTTS.performance.hot_reload import PerformanceMonitor
    
    monitor = PerformanceMonitor()
    
    # Test metric recording
    monitor.record_request(0.5, success=True)
    monitor.record_cache_hit()
    monitor.record_model_load()
    
    # Test metrics retrieval
    metrics = monitor.get_metrics()
    assert metrics["requests_total"] == 1
    assert metrics["requests_successful"] == 1
    assert metrics["cache_hits"] == 1
    assert metrics["model_loads"] == 1
    assert metrics["average_response_time"] == 0.5

def test_api_request_defaults():
    """Test API request with configuration defaults"""
    from app import TTSRequest
    
    # Test request with minimal data
    request = TTSRequest(input="test")
    
    # Verify optional fields
    assert request.voice is None
    assert request.response_format is None
    assert request.model is None
    assert request.speed == 1.0

def test_dynamic_voice_list():
    """Test dynamic voice list generation"""
    from LiteTTS.downloader import get_available_voices
    
    with patch('kokoro.downloader.VoiceDownloader') as mock_downloader_class:
        mock_downloader = Mock()
        mock_downloader.get_available_voice_names.return_value = ["voice1", "voice2", "voice3"]
        mock_downloader_class.return_value = mock_downloader
        
        voices = get_available_voices()
        assert voices == ["voice1", "voice2", "voice3"]

def test_cpu_only_installation():
    """Test CPU-only installation verification"""
    from LiteTTS.scripts.install_cpu_only import check_gpu_packages, verify_installation
    
    # Test GPU package detection
    with patch('subprocess.run') as mock_run:
        # Mock no GPU packages found
        mock_run.return_value.returncode = 1
        result = check_gpu_packages()
        assert result == True
    
    # Test installation verification
    with patch('importlib.import_module') as mock_import:
        mock_import.return_value = Mock()
        # This would test the actual verification in a real environment

def test_configuration_save():
    """Test configuration saving"""
    from LiteTTS.config import ConfigManager
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_config.json"
        
        config = ConfigManager()
        
        # Modify some values
        config.voice.default_voice = "test_voice"
        config.server.port = 9999
        
        # Save configuration
        result = config.save_to_json(str(config_file))
        assert result == True
        assert config_file.exists()
        
        # Verify saved content
        with open(config_file) as f:
            saved_config = json.load(f)
        
        assert saved_config["voice"]["default_voice"] == "test_voice"
        assert saved_config["server"]["port"] == 9999

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
