#!/usr/bin/env python3
"""
Unit tests for RIME AI integration
"""

import pytest

from LiteTTS.nlp.rime_ai_integration import PhoneticAnalysis, RIMEAIIntegration


class TestRIMEAIIntegration:
    """Test cases for RIMEAIIntegration"""

    @pytest.fixture
    def integration(self):
        """Create integration instance"""
        return RIMEAIIntegration()

    def test_initialization(self, integration):
        """Test integration initializes correctly"""
        assert integration is not None

    def test_process_text_with_rime_ai(self, integration):
        """Test processing text with RIME AI"""
        result = integration.process_text_with_rime_ai("Hello world")
        assert isinstance(result, PhoneticAnalysis)


class TestRIMEAIIntegrationEdgeCases:
    """Edge case tests for RIMEAIIntegration"""

    @pytest.fixture
    def integration(self):
        return RIMEAIIntegration()

    def test_process_empty_string(self, integration):
        """Test processing empty string"""
        result = integration.process_text_with_rime_ai("")
        assert isinstance(result, PhoneticAnalysis)
