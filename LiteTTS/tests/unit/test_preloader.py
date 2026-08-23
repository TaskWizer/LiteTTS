#!/usr/bin/env python3
"""
Unit tests for intelligent preloader
"""

from unittest.mock import Mock

from LiteTTS.cache.preloader import CacheWarmingConfig, IntelligentPreloader, WarmingTask


class TestCacheWarmingConfig:
    """Test cases for CacheWarmingConfig"""

    def test_creation_defaults(self):
        """Test creating config with defaults"""
        config = CacheWarmingConfig()
        assert config.primary_voices == ["af_heart"]
        assert config.warm_on_startup is True
        assert config.warm_during_idle is True

    def test_creation_custom(self):
        """Test creating config with custom values"""
        config = CacheWarmingConfig(
            primary_voices=["am_puck"], instant_words=["Hello", "Goodbye"], warm_on_startup=False
        )
        assert config.primary_voices == ["am_puck"]
        assert config.warm_on_startup is False


class TestWarmingTask:
    """Test cases for WarmingTask"""

    def test_creation(self):
        """Test creating warming task"""
        task = WarmingTask(text="Hello world", voice="af_heart", priority=1)
        assert task.text == "Hello world"
        assert task.voice == "af_heart"
        assert task.priority == 1

    def test_creation_defaults(self):
        """Test warming task default values"""
        task = WarmingTask(text="Test", voice="af_heart")
        assert task.priority == 1
        assert task.attempts == 0
        assert task.max_attempts == 3


class TestIntelligentPreloader:
    """Test cases for IntelligentPreloader"""

    def test_initialization(self):
        """Test preloader initializes correctly"""
        mock_app = Mock()
        config = CacheWarmingConfig()
        preloader = IntelligentPreloader(mock_app, config)
        assert preloader.tts_app is mock_app
        assert preloader.config is config

    def test_initialization_default_config(self):
        """Test preloader with default config"""
        mock_app = Mock()
        preloader = IntelligentPreloader(mock_app)
        assert preloader.config is not None
        assert preloader.config.primary_voices == ["af_heart"]
