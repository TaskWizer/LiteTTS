#!/usr/bin/env python3
"""
Unit tests for voice modulation system
"""

import pytest

from LiteTTS.nlp.voice_modulation_system import VoiceModulationSystem


class TestVoiceModulationSystem:
    """Test cases for VoiceModulationSystem"""

    @pytest.fixture
    def system(self):
        """Create system instance"""
        return VoiceModulationSystem()

    def test_initialization(self, system):
        """Test system initializes correctly"""
        assert system is not None

    def test_process_voice_modulation(self, system):
        """Test processing voice modulation"""
        result = system.process_voice_modulation("Hello world", "default")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], list)

    def test_get_voice_profiles(self, system):
        """Test getting voice profiles"""
        result = system.get_voice_profiles()
        assert isinstance(result, dict)

    def test_analyze_modulation_opportunities(self, system):
        """Test analyzing modulation opportunities"""
        result = system.analyze_modulation_opportunities("Hello world")
        assert isinstance(result, dict)

    def test_enhance_parenthetical_processing(self, system):
        """Test enhancing parenthetical processing"""
        result = system.enhance_parenthetical_processing("Hello (whispered) world")
        assert isinstance(result, str)


class TestVoiceModulationEdgeCases:
    """Edge case tests for VoiceModulationSystem"""

    @pytest.fixture
    def system(self):
        return VoiceModulationSystem()

    def test_process_empty_text(self, system):
        """Test processing empty text"""
        result = system.process_voice_modulation("", "default")
        assert isinstance(result, tuple)

    def test_analyze_empty_text(self, system):
        """Test analyzing empty text"""
        result = system.analyze_modulation_opportunities("")
        assert isinstance(result, dict)

    def test_process_unicode_text(self, system):
        """Test processing unicode text"""
        result = system.process_voice_modulation("Hello 世界 🌍", "default")
        assert isinstance(result, tuple)

    def test_process_long_text(self, system):
        """Test processing long text"""
        long_text = "Hello world. " * 100
        result = system.process_voice_modulation(long_text, "default")
        assert isinstance(result, tuple)
