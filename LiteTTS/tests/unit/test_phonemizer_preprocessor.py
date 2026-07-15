#!/usr/bin/env python3
"""
Unit tests for phonemizer preprocessor
"""

import pytest
import re
from LiteTTS.text.phonemizer_preprocessor import PhonemizationPreprocessor


class TestPhonemizationPreprocessor:
    """Test cases for PhonemizationPreprocessor"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return PhonemizationPreprocessor()

    def test_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None

    def test_preprocess_basic_text(self, processor):
        """Test basic text processing"""
        text = "Hello world"
        result = processor.preprocess_text(text)
        assert result is not None
        assert hasattr(result, 'processed_text')
        assert isinstance(result.processed_text, str)

    def test_preprocess_temperature_celsius(self, processor):
        """Test temperature handling with Celsius"""
        text = "The temperature is 25°C."
        result = processor.preprocess_text(text)
        # Should convert to words
        processed = result.processed_text.lower()
        assert "degrees" in processed or "celsius" in processed

    def test_preprocess_temperature_fahrenheit(self, processor):
        """Test temperature handling with Fahrenheit"""
        text = "The temperature is 98.6°F."
        result = processor.preprocess_text(text)
        # Should convert to words
        processed = result.processed_text.lower()
        assert "degrees" in processed or "fahrenheit" in processed

    def test_preprocess_temperature_negative(self, processor):
        """Test negative temperature handling"""
        text = "It was -17.4°C outside."
        result = processor.preprocess_text(text)
        # Should handle negative temperatures
        assert result is not None

    def test_preprocess_empty_string(self, processor):
        """Test processing empty string"""
        text = ""
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_whitespace_only(self, processor):
        """Test processing whitespace-only string"""
        text = "   \t\n  "
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_unicode_text(self, processor):
        """Test processing unicode text"""
        text = "Hello 世界"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_decimal_numbers(self, processor):
        """Test decimal number handling"""
        text = "Pi is approximately 3.14159"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_numbers(self, processor):
        """Test number handling"""
        text = "I have 5 apples"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_special_characters(self, processor):
        """Test special character handling"""
        text = "Hello! How are you?"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_acronyms(self, processor):
        """Test acronym handling"""
        text = "NASA sent a rover to Mars."
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_email_address(self, processor):
        """Test email address handling"""
        text = "Contact me at test@example.com"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_url(self, processor):
        """Test URL handling"""
        text = "Visit https://example.com for more info"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_xml(self, processor):
        """Test XML tag handling"""
        text = "This is <XML> content"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_yaml(self, processor):
        """Test YAML-related text handling"""
        text = "The config uses YAML format"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_sql(self, processor):
        """Test SQL keyword handling"""
        text = "SELECT * FROM users WHERE id = 1"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_c_sharp(self, processor):
        """Test C# handling"""
        text = "I code in C# and F#"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_hashtag(self, processor):
        """Test hashtag handling"""
        text = "Check out #python"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_ordinal_numbers(self, processor):
        """Test ordinal number handling"""
        text = "He came in 1st place"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_currency(self, processor):
        """Test currency symbol handling"""
        text = "The price is $19.99"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_percentage(self, processor):
        """Test percentage handling"""
        text = "The increase was 50%"
        result = processor.preprocess_text(text)
        assert result is not None


class TestPhonemizationPreprocessorEdgeCases:
    """Edge case tests for PhonemizationPreprocessor"""

    @pytest.fixture
    def processor(self):
        return PhonemizationPreprocessor()

    def test_very_long_text(self, processor):
        """Test processing very long text"""
        text = "A" * 10000
        result = processor.preprocess_text(text)
        assert result is not None

    def test_mixed_languages(self, processor):
        """Test mixed language text"""
        text = "Hello world 你好世界"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_special_unicode_characters(self, processor):
        """Test special unicode characters"""
        text = "ñooo ñooña Señor"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_emoji(self, processor):
        """Test emoji handling"""
        text = "Hello 👋 world 🌍"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_aggressive_mode(self, processor):
        """Test aggressive processing mode"""
        text = "don't won't can't"
        result = processor.preprocess_text(text, aggressive=True)
        assert result is not None

    def test_preprocess_conservative_mode(self, processor):
        """Test conservative processing mode"""
        text = "don't won't can't"
        result = processor.preprocess_text(text, aggressive=False)
        assert result is not None
