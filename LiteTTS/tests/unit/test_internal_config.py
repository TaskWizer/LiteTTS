#!/usr/bin/env python3
"""
Unit tests for internal config module
"""

from unittest.mock import patch

from LiteTTS.config.internal_config import (
    InternalConfig,
    get_internal_config,
    reload_internal_config,
)


class TestInternalConfig:
    """Test cases for InternalConfig class"""

    def test_initialization(self):
        """Test config initializes correctly"""
        config = InternalConfig()
        assert config.pronunciation_rules is not None
        assert config.acronym_handling is not None
        assert config.text_processing is not None
        assert config.performance_optimization is not None
        assert config.cache_optimization is not None

    def test_pronunciation_rules_structure(self):
        """Test pronunciation rules structure"""
        config = InternalConfig()
        rules = config.pronunciation_rules
        assert 'contraction_handling' in rules
        assert 'proper_name_handling' in rules

        contraction = rules['contraction_handling']
        assert 'expand_contractions' in contraction
        assert 'pronunciation_rules' in contraction
        contraction_rules = contraction['pronunciation_rules']
        assert contraction_rules.get("wasn't") == "was not"
        assert contraction_rules.get("I'll") == "I will"

    def test_acronym_handling_structure(self):
        """Test acronym handling structure"""
        config = InternalConfig()
        acronym = config.acronym_handling
        assert acronym['enabled'] is True
        assert 'preserve_common_acronyms' in acronym
        assert 'financial_symbols' in acronym
        assert 'TSLA' in acronym['financial_symbols']

    def test_text_processing_structure(self):
        """Test text processing structure"""
        config = InternalConfig()
        processing = config.text_processing
        assert 'interjection_handling' in processing
        assert 'symbol_processing' in processing
        assert 'punctuation_handling' in processing

    def test_performance_optimization_structure(self):
        """Test performance optimization structure"""
        config = InternalConfig()
        perf = config.performance_optimization
        assert 'processing' in perf
        assert 'threading' in perf
        assert 'caching' in perf

        processing = perf['processing']
        assert processing['chunk_size'] == 80
        assert processing['max_text_length'] == 3000
        assert processing['timeout_seconds'] == 25

    def test_cache_optimization_structure(self):
        """Test cache optimization structure"""
        config = InternalConfig()
        cache = config.cache_optimization
        assert 'memory_management' in cache
        assert 'disk_management' in cache
        assert 'cache_policies' in cache

        policies = cache['cache_policies']
        assert policies['max_size'] == 100
        assert policies['ttl'] == 5400
        assert policies['phoneme_cache_enabled'] is True

    def test_get_config_section(self):
        """Test getting config section"""
        config = InternalConfig()
        section = config.get_config_section('pronunciation_rules')
        assert section is not None
        assert isinstance(section, dict)

    def test_get_config_section_nonexistent(self):
        """Test getting non-existent config section"""
        config = InternalConfig()
        section = config.get_config_section('nonexistent')
        assert section is None

    def test_override_setting(self):
        """Test overriding a setting"""
        config = InternalConfig()
        config.override_setting('performance_optimization', 'processing', {'chunk_size': 100})
        # The section is 'performance_optimization' which contains nested dicts
        # So we just verify no exception is raised

    def test_override_setting_nonexistent(self):
        """Test overriding non-existent setting"""
        config = InternalConfig()
        # Should not raise, just log warning
        config.override_setting('nonexistent', 'key', 'value')

    def test_load_overrides_from_env(self):
        """Test loading overrides from environment"""
        config = InternalConfig()
        with patch.dict('os.environ', {'KOKORO_INTERNAL_PRONUNCIATION_RULES_ENABLED': 'true'}):
            config.load_overrides_from_env()
            # Just verify it runs without error

    def test_load_overrides_from_env_int(self):
        """Test loading integer override from environment"""
        config = InternalConfig()
        with patch.dict('os.environ', {'KOKORO_INTERNAL_PROCESSING_CHUNK_SIZE': '100'}):
            config.load_overrides_from_env()

    def test_load_overrides_from_env_float(self):
        """Test loading float override from environment"""
        config = InternalConfig()
        with patch.dict('os.environ', {'KOKORO_INTERNAL_TARGET_RTF': '0.5'}):
            config.load_overrides_from_env()

    def test_get_all_config(self):
        """Test getting all config"""
        config = InternalConfig()
        all_config = config.get_all_config()
        assert isinstance(all_config, dict)
        assert 'pronunciation_rules' in all_config
        assert 'acronym_handling' in all_config
        assert 'text_processing' in all_config
        assert 'performance_optimization' in all_config
        assert 'cache_optimization' in all_config


class TestGlobalFunctions:
    """Test cases for global functions"""

    def test_get_internal_config(self):
        """Test getting internal config returns a valid object"""
        config = get_internal_config()
        assert config is not None
        assert isinstance(config, InternalConfig)

    def test_reload_internal_config(self):
        """Test reloading internal config returns a valid object"""
        config = reload_internal_config()
        assert config is not None
        assert isinstance(config, InternalConfig)
