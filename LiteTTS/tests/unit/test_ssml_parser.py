#!/usr/bin/env python3
"""
Unit tests for SSML parser
"""

import pytest
from LiteTTS.ssml.parser import SSMLParser


class TestSSMLParser:
    """Test cases for SSMLParser"""

    @pytest.fixture
    def parser(self):
        """Create SSML parser instance"""
        return SSMLParser()

    def test_initialization(self, parser):
        """Test parser initializes correctly"""
        assert parser is not None

    def test_parse_simple_ssml(self, parser):
        """Test parsing simple SSML"""
        ssml = "<speak>Hello world</speak>"
        result = parser.parse(ssml)
        assert result is not None

    def test_parse_ssml_with_voice(self, parser):
        """Test parsing SSML with voice tag"""
        ssml = '<speak><voice name="af_heart">Hello</voice></speak>'
        result = parser.parse(ssml)
        assert result is not None

    def test_parse_ssml_with_break(self, parser):
        """Test parsing SSML with break tag"""
        ssml = "<speak>Hello <break time='1s'/> world</speak>"
        result = parser.parse(ssml)
        assert result is not None

    def test_parse_ssml_with_emphasis(self, parser):
        """Test parsing SSML with emphasis tag"""
        ssml = "<speak><emphasis>Important</emphasis> text</speak>"
        result = parser.parse(ssml)
        assert result is not None

    def test_parse_ssml_with_phoneme(self, parser):
        """Test parsing SSML with phoneme tag"""
        ssml = '<speak><phoneme alphabet="ipa" ph="həˈloʊ">Hello</phoneme></speak>'
        result = parser.parse(ssml)
        assert result is not None

    def test_parse_empty_ssml(self, parser):
        """Test parsing empty SSML"""
        ssml = ""
        result = parser.parse(ssml)
        assert result is not None

    def test_parse_invalid_ssml(self, parser):
        """Test parsing invalid SSML"""
        ssml = "<speak>Unclosed tag"
        result = parser.parse(ssml)
        assert result is not None

    def test_parse_ssml_with_multiple_tags(self, parser):
        """Test parsing SSML with multiple tags"""
        ssml = """
        <speak>
            <voice name="af_heart">Hello</voice>
            <break time='500ms'/>
            <emphasis>World</emphasis>
        </speak>
        """
        result = parser.parse(ssml)
        assert result is not None


class TestSSMLParserEdgeCases:
    """Edge case tests for SSMLParser"""

    @pytest.fixture
    def parser(self):
        return SSMLParser()

    def test_parse_deeply_nested_tags(self, parser):
        """Test parsing deeply nested tags"""
        ssml = "<speak><voice><emphasis><break/>World</emphasis></voice></speak>"
        result = parser.parse(ssml)
        assert result is not None

    def test_parse_ssml_with_attributes(self, parser):
        """Test parsing SSML with various attributes"""
        ssml = '<speak voice="af_heart" rate="medium">Hello</speak>'
        result = parser.parse(ssml)
        assert result is not None

    def test_parse_ssml_with_xml_declaration(self, parser):
        """Test parsing SSML with XML declaration"""
        ssml = '<?xml version="1.0"?><speak>Hello</speak>'
        result = parser.parse(ssml)
        assert result is not None
