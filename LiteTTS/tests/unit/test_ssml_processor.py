#!/usr/bin/env python3
"""
Unit tests for SSML processor
"""

import pytest

from LiteTTS.ssml.processor import SSMLProcessor


class TestSSMLProcessor:
    """Test cases for SSMLProcessor"""

    @pytest.fixture
    def processor(self):
        """Create SSML processor instance"""
        return SSMLProcessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_process_ssml_simple(self, processor):
        """Test processing simple SSML"""
        ssml = "<speak>Hello world</speak>"
        result = processor.process_ssml(ssml)
        assert result is not None
        assert isinstance(result, tuple)

    def test_validate_ssml_simple(self, processor):
        """Test validating simple SSML"""
        ssml = "<speak>Hello world</speak>"
        result = processor.validate_ssml(ssml)
        assert result is not None
        assert isinstance(result, dict)

    def test_validate_ssml_empty(self, processor):
        """Test validating empty SSML"""
        ssml = ""
        result = processor.validate_ssml(ssml)
        assert result is not None

    def test_get_supported_background_types(self, processor):
        """Test getting supported background types"""
        result = processor.get_supported_background_types()
        assert isinstance(result, list)


class TestSSMLProcessorEdgeCases:
    """Edge case tests for SSMLProcessor"""

    @pytest.fixture
    def processor(self):
        return SSMLProcessor()

    def test_validate_invalid_ssml(self, processor):
        """Test validating invalid SSML"""
        ssml = "<speak>Unclosed tag"
        result = processor.validate_ssml(ssml)
        assert result is not None

    def test_validate_ssml_with_voice(self, processor):
        """Test validating SSML with voice tag"""
        ssml = '<speak><voice name="af_heart">Hello</voice></speak>'
        result = processor.validate_ssml(ssml)
        assert result is not None

    def test_validate_ssml_with_break(self, processor):
        """Test validating SSML with break tag"""
        ssml = "<speak>Hello <break time='1s'/> world</speak>"
        result = processor.validate_ssml(ssml)
        assert result is not None
