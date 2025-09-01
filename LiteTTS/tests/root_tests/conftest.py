#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Kokoro ONNX TTS API tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@pytest.fixture(scope="session")
def project_root_path():
    """Get project root path"""
    return project_root

@pytest.fixture(scope="session")
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings"""
    return {
        "test_voices": ["af_heart", "am_puck"],
        "test_formats": ["mp3", "wav"],
        "test_texts": [
            "Hello, world!",
            "This is a test.",
            "Testing the TTS system with a longer sentence."
        ],
        "performance_thresholds": {
            "max_rtf": 1.0,
            "max_cache_hit_ms": 50,
            "max_memory_mb": 500,
            "max_startup_seconds": 30
        }
    }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Ensure test directories exist
    test_dirs = ["docs/logs", "docs/benchmark", "LiteTTS/models", "LiteTTS/voices"]
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Cleanup after test if needed
    pass

@pytest.fixture
def mock_audio_data():
    """Generate mock audio data for testing"""
    import numpy as np
    
    def generate_audio(duration_seconds=2.0, sample_rate=24000):
        """Generate mock audio data"""
        num_samples = int(duration_seconds * sample_rate)
        # Generate simple sine wave
        t = np.linspace(0, duration_seconds, num_samples)
        frequency = 440  # A4 note
        audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        return audio, sample_rate
    
    return generate_audio

@pytest.fixture
def sample_tts_requests():
    """Sample TTS request data for testing"""
    return [
        {
            "input": "Hello, world!",
            "voice": "af_heart",
            "response_format": "mp3"
        },
        {
            "input": "Testing different voice",
            "voice": "am_puck",
            "response_format": "wav"
        },
        {
            "input": "Speed test",
            "voice": "af_heart",
            "response_format": "mp3",
            "speed": 1.5
        }
    ]

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API endpoint tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers based on test names/paths
    for item in items:
        # Mark slow tests
        if "slow" in item.name or "stress" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.name or "test_comprehensive" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark performance tests
        if "performance" in item.name or "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        
        # Mark API tests
        if "api" in item.name or "endpoint" in item.name:
            item.add_marker(pytest.mark.api)

# Test data constants
TEST_VOICES = ["af_heart", "am_puck", "af_sarah", "am_michael"]
TEST_FORMATS = ["mp3", "wav", "flac"]
TEST_TEXTS = [
    "Hi",
    "Hello, world!",
    "This is a test of the text-to-speech system.",
    "The quick brown fox jumps over the lazy dog.",
    "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole."
]

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "max_rtf": 1.0,  # Real-time factor should be < 1.0
    "max_cache_hit_ms": 50,  # Cache hits should be < 50ms
    "max_memory_mb": 500,  # Memory usage should be < 500MB
    "max_startup_seconds": 30,  # Startup should be < 30 seconds
    "min_audio_quality": 50,  # Audio quality score should be > 50
    "max_generation_time_per_second": 2.0  # Should generate 1s audio in < 2s
}
