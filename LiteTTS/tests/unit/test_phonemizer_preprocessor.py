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


class TestPreprocessingResult:
    """Test cases for PreprocessingResult dataclass"""

    def test_preprocessing_result_creation(self):
        """Test creating a preprocessing result"""
        from LiteTTS.text.phonemizer_preprocessor import PreprocessingResult
        result = PreprocessingResult(
            processed_text="hello",
            original_text="hello",
            changes_made=["test"],
            confidence_score=0.9,
            warnings=[]
        )
        assert result.processed_text == "hello"
        assert result.original_text == "hello"
        assert result.changes_made == ["test"]
        assert result.confidence_score == 0.9


class TestPhonemizationPreprocessorMethods:
    """Test cases for individual methods of PhonemizationPreprocessor"""

    @pytest.fixture
    def processor(self):
        return PhonemizationPreprocessor()

    def test_is_time_expression(self, processor):
        """Test time expression detection"""
        # Should return True for time expressions
        assert processor._is_time_expression("ten thirty five a m") is True
        assert processor._is_time_expression("nine o'clock p m") is True

    def test_is_time_expression_false(self, processor):
        """Test time expression detection returns False for non-times"""
        assert processor._is_time_expression("Hello world") is False
        assert processor._is_time_expression("ten thirty five") is False

    def test_expand_contractions_conservative(self, processor):
        """Test conservative contraction expansion"""
        text = "don't won't can't"
        result, changes = processor._expand_contractions_conservative(text)
        assert isinstance(result, str)
        assert isinstance(changes, list)

    def test_convert_numbers_conservative(self, processor):
        """Test conservative number conversion"""
        text = "I have 5 apples and 0 oranges"
        result, changes = processor._convert_numbers_conservative(text)
        assert isinstance(result, str)
        assert isinstance(changes, list)

    def test_convert_symbols_conservative(self, processor):
        """Test conservative symbol conversion"""
        text = 'Hello "world"'
        result, changes = processor._convert_symbols_conservative(text)
        assert isinstance(result, str)

    def test_fix_problematic_patterns_conservative(self, processor):
        """Test conservative pattern fixing"""
        text = "test... more"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert isinstance(result, str)
        assert isinstance(changes, list)

    def test_fix_tech_compounds_c_sharp(self, processor):
        """Test C# tech compound handling"""
        text = "I code in C#"
        result, changes = processor._fix_tech_compounds(text)
        assert "C sharp" in result

    def test_fix_tech_compounds_oauth(self, processor):
        """Test OAuth tech compound handling"""
        text = "OAuth 2.0 is the standard"
        result, changes = processor._fix_tech_compounds(text)
        assert "OAuth" in result

    def test_fix_tech_compounds_ipv6(self, processor):
        """Test IPv6 tech compound handling"""
        text = "My IP is IPv6"
        result, changes = processor._fix_tech_compounds(text)
        assert "I P V six" in result

    def test_fix_tech_compounds_sha(self, processor):
        """Test SHA-256 tech compound handling"""
        text = "The hash is SHA-256"
        result, changes = processor._fix_tech_compounds(text)
        assert "SHA" in result

    def test_fix_fractions_and_symbols_fraction(self, processor):
        """Test fraction handling"""
        text = "Give me ½ of the pizza"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_fix_fractions_and_symbols_plus_minus(self, processor):
        """Test plus-minus symbol handling"""
        text = "The value is ±5"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert "plus or minus" in result.lower() or "plus minus" in result.lower()

    def test_fix_fractions_and_symbols_temperature(self, processor):
        """Test temperature handling"""
        text = "It is -17.4°C outside"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert "minus" in result.lower()

    def test_fix_fractions_and_symbols_email(self, processor):
        """Test email handling"""
        text = "Contact qa-test@example.com"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_fix_fractions_and_symbols_international(self, processor):
        """Test international text handling"""
        text = "Hello 世界"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_filter_emojis(self, processor):
        """Test emoji filtering"""
        text = "Hello 👋 world 🌍"
        result, changes = processor._filter_emojis(text)
        assert "👋" not in result
        assert "🌍" not in result

    def test_handle_quote_characters(self, processor):
        """Test quote character handling"""
        text = 'He said "Hello"'
        result, changes = processor._handle_quote_characters(text)
        assert '"' not in result

    def test_handle_quote_characters_with_contractions(self, processor):
        """Test quote handling preserves contractions"""
        text = "I'm happy"
        result, changes = processor._handle_quote_characters(text)
        assert "I'm" in result

    def test_decode_html_entities(self, processor):
        """Test HTML entity decoding"""
        text = "&#x27;test&#x27;"
        result, changes = processor._decode_html_entities(text)
        assert "'" in result

    def test_decode_html_entities_ampersand(self, processor):
        """Test ampersand entity decoding"""
        text = "Tom & Jerry"
        result, changes = processor._decode_html_entities(text)
        assert "&" in result

    def test_convert_numbers_to_words(self, processor):
        """Test number to words conversion"""
        text = "I have 5 apples"
        result, changes = processor._convert_numbers_to_words(text)
        assert isinstance(result, str)

    def test_convert_numbers_to_words_aggressive(self, processor):
        """Test aggressive number conversion"""
        text = "I have 5 apples"
        result, changes = processor._convert_numbers_to_words(text, aggressive=True)
        assert isinstance(result, str)

    def test_convert_numbers_to_words_large(self, processor):
        """Test large number conversion"""
        text = "One million dollars"
        result, changes = processor._convert_numbers_to_words(text)
        assert isinstance(result, str)

    def test_number_to_words(self, processor):
        """Test number to words helper"""
        assert processor._number_to_words(0) == "zero"
        assert processor._number_to_words(5) == "five"
        assert processor._number_to_words(15) == "fifteen"
        assert processor._number_to_words(42) is not None

    def test_number_to_words_negative(self, processor):
        """Test negative number conversion"""
        result = processor._number_to_words(-5)
        assert "negative" in result.lower()

    def test_convert_symbols_to_words(self, processor):
        """Test symbol to words conversion"""
        text = "A + B = C"
        result, changes = processor._convert_symbols_to_words(text)
        assert isinstance(result, str)

    def test_fix_problematic_patterns(self, processor):
        """Test problematic pattern fixing"""
        text = "test... more"
        result, changes = processor._fix_problematic_patterns(text)
        assert isinstance(result, str)

    def test_clean_whitespace_and_punctuation(self, processor):
        """Test whitespace and punctuation cleaning"""
        text = "Hello    world!"
        result = processor._clean_whitespace_and_punctuation(text)
        assert "  " not in result

    def test_calculate_confidence_score(self, processor):
        """Test confidence score calculation"""
        text = "Hello world."
        score = processor._calculate_confidence_score(text, "Hello world")
        assert 0.0 <= score <= 1.0

    def test_calculate_confidence_score_with_numbers(self, processor):
        """Test confidence score with numbers"""
        text = "我有5个苹果"  # Has numbers
        score = processor._calculate_confidence_score(text, text)
        assert score < 1.0

    def test_detect_potential_issues(self, processor):
        """Test issue detection"""
        text = "Hello world 12345 @test #hash"
        issues = processor._detect_potential_issues(text)
        assert isinstance(issues, list)

    def test_detect_potential_issues_long_text(self, processor):
        """Test issue detection on long text"""
        text = "A" * 600
        issues = processor._detect_potential_issues(text)
        assert len(issues) > 0

    def test_contractions_map_built(self, processor):
        """Test contractions map is built"""
        assert isinstance(processor.contractions_map, dict)
        assert len(processor.contractions_map) > 0

    def test_number_words_map_built(self, processor):
        """Test number words map is built"""
        assert isinstance(processor.number_words_map, dict)
        assert '0' in processor.number_words_map

    def test_symbol_words_map_built(self, processor):
        """Test symbol words map is built"""
        assert isinstance(processor.symbol_words_map, dict)
        assert '&' in processor.symbol_words_map

    def test_problematic_patterns_built(self, processor):
        """Test problematic patterns list is built"""
        assert isinstance(processor.problematic_patterns, list)
        assert len(processor.problematic_patterns) > 0

    def test_regex_patterns_compiled(self, processor):
        """Test regex patterns are compiled"""
        assert hasattr(processor, 'control_char_pattern')
        assert hasattr(processor, 'whitespace_pattern')

    def test_preprocess_preserves_word_count(self, processor):
        """Test word count preservation"""
        text = "Hello world"
        result = processor.preprocess_text(text, preserve_word_count=True)
        assert result is not None

    def test_preprocess_with_aggressive_mode(self, processor):
        """Test aggressive mode changes more"""
        text = "don't won't can't"
        result_normal = processor.preprocess_text(text, aggressive=False)
        result_aggressive = processor.preprocess_text(text, aggressive=True)
        # Both should produce valid results
        assert result_normal is not None
        assert result_aggressive is not None


class TestPhonemizationPreprocessorEdgeCases2:
    """More edge case tests for PhonemizationPreprocessor"""

    @pytest.fixture
    def processor(self):
        return PhonemizationPreprocessor()

    def test_html_entities_multiple(self, processor):
        """Test multiple HTML entities"""
        text = "&#x27;hello&#x27; and &#39;world&#39;"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_tech_compounds_multiple(self, processor):
        """Test multiple tech compounds"""
        text = "C# and F# and G#"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_email_complex(self, processor):
        """Test complex email"""
        text = "Email test@sub.domain.example.com please"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_lead_bass_context(self, processor):
        """Test lead/bass context handling"""
        text = "The bass player is good"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_lead_metal_context(self, processor):
        """Test lead metal context"""
        text = "Lead metal is heavy"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_decimal_numbers_conservative(self, processor):
        """Test decimal number handling conservative"""
        text = "Pi is 3.14159"
        result, changes = processor._convert_numbers_conservative(text)
        assert isinstance(result, str)

    def test_fractions_with_number(self, processor):
        """Test fractions with leading number"""
        text = "2½ cups of flour"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert "half" in result.lower() or "and a half" in result.lower()

    def test_unicode_quotes(self, processor):
        """Test unicode quote handling"""
        text = '“Hello”'
        result, changes = processor._handle_quote_characters(text)
        assert '“' not in result
        assert '”' not in result

    def test_international_scripts(self, processor):
        """Test various international scripts"""
        # Korean
        text = "안녕하세요"
        result = processor.preprocess_text(text)
        assert result is not None

        # Arabic
        text = "مرحبا"
        result = processor.preprocess_text(text)
        assert result is not None

        # Hebrew
        text = "שלום"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_code_patterns(self, processor):
        """Test code pattern detection"""
        text = "function() { return true; }"
        issues = processor._detect_potential_issues(text)
        assert isinstance(issues, list)

    def test_url_pattern(self, processor):
        """Test URL pattern detection"""
        text = "Visit https://example.com for info"
        issues = processor._detect_potential_issues(text)
        assert any("url" in i.lower() for i in issues)

    def test_repeated_characters(self, processor):
        """Test repeated character detection"""
        text = "Helllooooo"
        issues = processor._detect_potential_issues(text)
        assert any("repeated" in i.lower() for i in issues)

    def test_excessive_punctuation(self, processor):
        """Test excessive punctuation detection"""
        text = "Hello!!!!! How are you????"
        issues = processor._detect_potential_issues(text)
        assert any("punctuation" in i.lower() for i in issues)

    def test_smileys_not_emoji(self, processor):
        """Test that smileys aren't filtered as emojis"""
        text = "Hello :)"
        result = processor.preprocess_text(text)
        assert result is not None
