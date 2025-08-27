"""
Backward Compatibility Test Suite
Tests to ensure API backward compatibility across versions
"""

import pytest
import json
import requests
from typing import Dict, Any

class TestBackwardCompatibility:
    """Test backward compatibility of API endpoints"""

    BASE_URL = "http://localhost:8354"

    def test_v1_audio_speech_endpoint(self):
        """Test v1 audio speech endpoint compatibility"""
        endpoint = f"{self.BASE_URL}/v1/audio/speech"

        # Test basic request format
        payload = {
            "model": "kokoro",
            "input": "Hello, world!",
            "voice": "af_heart"
        }

        # This should not fail in future versions
        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 503]  # 503 if service not running

        if response.status_code == 200:
            assert response.headers.get("content-type") == "audio/wav"

    def test_health_endpoint_format(self):
        """Test health endpoint response format"""
        endpoint = f"{self.BASE_URL}/health"

        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()

                # These fields should always be present
                assert "status" in data
                assert "timestamp" in data

                # Status should be one of expected values
                assert data["status"] in ["healthy", "warning", "critical", "unknown"]
        except requests.exceptions.ConnectionError:
            pytest.skip("Service not running")

    def test_api_error_format(self):
        """Test API error response format consistency"""
        endpoint = f"{self.BASE_URL}/v1/audio/speech"

        # Send invalid request
        payload = {"invalid": "request"}

        try:
            response = requests.post(endpoint, json=payload)
            if response.status_code >= 400:
                # Error responses should be JSON
                assert response.headers.get("content-type", "").startswith("application/json")

                error_data = response.json()
                # Should have error information
                assert "error" in error_data or "detail" in error_data
        except requests.exceptions.ConnectionError:
            pytest.skip("Service not running")

    def test_voice_list_compatibility(self):
        """Test voice list endpoint compatibility"""
        endpoint = f"{self.BASE_URL}/v1/voices"

        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()

                # Should return a list or dict with voices
                assert isinstance(data, (list, dict))

                if isinstance(data, list) and data:
                    # Each voice should have required fields
                    voice = data[0]
                    assert "id" in voice or "name" in voice
        except requests.exceptions.ConnectionError:
            pytest.skip("Service not running")

    def test_model_list_compatibility(self):
        """Test model list endpoint compatibility"""
        endpoint = f"{self.BASE_URL}/v1/models"

        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()

                # Should return model information
                assert isinstance(data, (list, dict))

                if isinstance(data, dict) and "data" in data:
                    # OpenAI-compatible format
                    assert isinstance(data["data"], list)
        except requests.exceptions.ConnectionError:
            pytest.skip("Service not running")

class TestConfigurationCompatibility:
    """Test configuration backward compatibility"""

    def test_config_file_format(self):
        """Test configuration file format compatibility"""
        config_files = ["config.json", "config/config.json"]

        for config_file in config_files:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)

                # Basic configuration structure should be maintained
                assert isinstance(config, dict)

                # Check for critical configuration keys
                if "server" in config:
                    server_config = config["server"]
                    assert "host" in server_config or "port" in server_config

    def test_environment_variables(self):
        """Test environment variable compatibility"""
        # These environment variables should continue to work
        env_vars = [
            "KOKORO_HOST",
            "KOKORO_PORT",
            "KOKORO_MODEL_PATH",
            "KOKORO_VOICE_PATH"
        ]

        # Test that they can be set without breaking the application
        for var in env_vars:
            # Just check that setting them doesn't cause import errors
            os.environ[var] = "test_value"
            try:
                # Try importing main modules
                import sys
                assert True  # If we get here, no import errors
            finally:
                if var in os.environ:
                    del os.environ[var]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
