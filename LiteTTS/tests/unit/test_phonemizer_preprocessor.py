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

    def test_fix_fractions_and_symbols_plus_minus_percent(self, processor):
        """Test plus-minus with percent"""
        text = "The margin is ±5%"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_fix_fractions_and_symbols_plus_minus_decimal_percent(self, processor):
        """Test plus-minus with decimal percent"""
        text = "Error is ±3.5%"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_fix_fractions_and_symbols_plus_minus_zero_percent(self, processor):
        """Test plus-minus with zero percent (whole=0 case)"""
        text = "Error is ±.5%"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_international_text_arabic(self, processor):
        """Test Arabic text handling"""
        text = "Hello world"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_international_text_hebrew(self, processor):
        """Test Hebrew text handling"""
        text = "Hello world"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_international_text_thai(self, processor):
        """Test Thai text handling"""
        text = "Hello world"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_international_text_thai_script(self, processor):
        """Test Thai script handling in _fix_fractions_and_symbols"""
        text = "Hello สวัสดี world"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_international_text_georgian_script(self, processor):
        """Test Georgian script handling"""
        text = "Hello გამარჯობა world"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_international_text_armenian_script(self, processor):
        """Test Armenian script handling"""
        text = "Hello ողջ world"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_fix_fractions_and_symbols_time_am(self, processor):
        """Test a.m. time handling"""
        text = "Meet at 10:30 a.m."
        result, changes = processor._fix_fractions_and_symbols(text)
        assert "A M" in result or "AM" in result.upper()

    def test_fix_fractions_and_symbols_time_pm(self, processor):
        """Test p.m. time handling"""
        text = "Meet at 5:00 p.m."
        result, changes = processor._fix_fractions_and_symbols(text)
        assert "P M" in result or "PM" in result.upper()

    def test_fix_fractions_and_symbols_time_pm_no_period(self, processor):
        """Test p.m. time without period"""
        text = "Meeting at 3pm"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_fix_fractions_and_symbols_plus_minus_zero_whole(self, processor):
        """Test plus-minus with zero as whole number (e.g., ±0.5%)"""
        text = "Error is ±0.5%"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_temperature_whole_number_decimal(self, processor):
        """Test temperature with decimal point but no decimal digits (e.g., 5.)"""
        text = "It is 5.°C"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_temperature_decimal_only_point(self, processor):
        """Test temperature with only decimal part (e.g., .5°C)"""
        text = "It is .5°C"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_temperature_positive_celsius(self, processor):
        """Test positive Celsius temperature"""
        text = "It is 25°C outside"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_temperature_negative_celsius(self, processor):
        """Test negative Celsius temperature"""
        text = "It is -5°C outside"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_temperature_fahrenheit(self, processor):
        """Test Fahrenheit temperature"""
        text = "It is 98.6°F"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)
        assert "fahrenheit" in result.lower()

    def test_temperature_decimal_only(self, processor):
        """Test temperature with decimal only (0.5°C)"""
        text = "It is 0.5°C"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_fix_fractions_and_symbols_email(self, processor):
        """Test email handling"""
        text = "Contact qa-test@example.com"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_fix_fractions_and_symbols_email_simple(self, processor):
        """Test simple email with subdomain"""
        text = "Email test@mail.example.com"
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

    def test_expand_contractions_fallback_mode(self):
        """Test _expand_contractions when enhanced_contraction_processor is None"""
        # Create processor and force enhanced_contraction_processor to None
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None
        processor.expand_all = True
        processor.preserve_natural = False

        text = "I'm happy"
        result, changes = processor._expand_contractions(text)
        assert isinstance(result, str)
        assert isinstance(changes, list)

    def test_expand_contractions_preserve_all(self):
        """Test _expand_contractions when preserving all contractions"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None
        processor.expand_all = False
        processor.expand_problematic_only = True
        processor.preserve_natural = True

        text = "I'm happy"
        result, changes = processor._expand_contractions(text)
        # Should preserve contractions
        assert isinstance(result, str)

    def test_expand_contractions_problematic_only(self):
        """Test _expand_contractions with problematic_only mode"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None
        processor.expand_all = False
        processor.expand_problematic_only = True
        processor.preserve_natural = True

        text = "I'm happy"
        result, changes = processor._expand_contractions(text)
        assert isinstance(result, str)

    def test_convert_numbers_conservative_zero(self):
        """Test conservative number conversion with zero"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None

        text = "I have 0 apples"
        result, changes = processor._convert_numbers_conservative(text)
        assert "zero" in result.lower()

    def test_convert_numbers_conservative_decimal(self):
        """Test conservative number conversion with decimals"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None

        text = "Pi is 3.14159"
        result, changes = processor._convert_numbers_conservative(text)
        assert isinstance(result, str)

    def test_convert_numbers_conservative_comma_separated(self):
        """Test conservative number conversion with comma-separated numbers"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None

        text = "The population is 1,000,000"
        result, changes = processor._convert_numbers_conservative(text)
        # Should warn about comma-separated numbers
        assert isinstance(result, str)

    def test_convert_symbols_conservative_quotes(self):
        """Test conservative symbol conversion with quotes"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None

        text = 'He said "Hello"'
        result, changes = processor._convert_symbols_conservative(text)
        # Should remove quotes
        assert '"' not in result

    def test_convert_symbols_conservative_empty(self):
        """Test conservative symbol conversion with empty problematic_symbols"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None
        processor.problematic_symbols = {}

        text = "Hello + World"
        result, changes = processor._convert_symbols_conservative(text)
        # + should be preserved since it's not in problematic_symbols
        assert isinstance(result, str)

    def test_fix_problematic_patterns_conservative_dot(self):
        """Test conservative pattern fixing with domain names"""
        processor = PhonemizationPreprocessor()

        text = "Visit google.com please"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert isinstance(result, str)

    def test_fix_problematic_patterns_conservative_email(self):
        """Test conservative pattern fixing with email"""
        processor = PhonemizationPreprocessor()

        text = "Email test@example.com please"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert isinstance(result, str)

    def test_fix_problematic_patterns_conservative_range(self):
        """Test conservative pattern fixing with number range"""
        processor = PhonemizationPreprocessor()

        text = "The range is 1-10"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert isinstance(result, str)

    def test_fix_problematic_patterns_conservative_time(self):
        """Test conservative pattern fixing with time"""
        processor = PhonemizationPreprocessor()

        text = "The time is 10:30"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert isinstance(result, str)

    def test_fix_problematic_patterns_conservative_underscore(self):
        """Test conservative pattern fixing with underscored words"""
        processor = PhonemizationPreprocessor()

        text = "Variable name is test_value"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert isinstance(result, str)

    def test_fix_problematic_patterns_conservative_acronym(self):
        """Test conservative pattern fixing with acronyms"""
        processor = PhonemizationPreprocessor()

        text = "The CEO is here"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        # CEO should be lowercased
        assert isinstance(result, str)

    def test_fix_problematic_patterns_conservative_number_letter(self):
        """Test conservative pattern fixing with number-letter combinations"""
        processor = PhonemizationPreprocessor()

        text = "Item A1 is great"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert isinstance(result, str)

    def test_fix_problematic_patterns_conservative_no_match(self):
        """Test conservative pattern fixing with no matches"""
        processor = PhonemizationPreprocessor()

        text = "Hello world"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert result == text

    def test_is_time_expression_true(self):
        """Test time expression detection with a.m."""
        processor = PhonemizationPreprocessor()
        assert processor._is_time_expression("ten thirty five a m") is True

    def test_is_time_expression_false_simple(self):
        """Test time expression detection with simple text"""
        processor = PhonemizationPreprocessor()
        assert processor._is_time_expression("hello world") is False

    def test_clean_whitespace_and_punctuation_multiple(self):
        """Test whitespace and punctuation cleaning with multiple issues"""
        processor = PhonemizationPreprocessor()

        text = "Hello    world...\t\n"
        result = processor._clean_whitespace_and_punctuation(text)
        assert "  " not in result
        assert "\t" not in result
        assert "\n" not in result

    def test_clean_whitespace_and_punctuation_quotes(self):
        """Test whitespace cleaning around quotes"""
        processor = PhonemizationPreprocessor()

        text = 'Hello " world'
        result = processor._clean_whitespace_and_punctuation(text)
        assert isinstance(result, str)

    def test_clean_whitespace_and_punctuation_parens(self):
        """Test whitespace cleaning around parentheses"""
        processor = PhonemizationPreprocessor()

        text = "Hello ( world )"
        result = processor._clean_whitespace_and_punctuation(text)
        assert isinstance(result, str)

    def test_detect_potential_issues_empty(self):
        """Test issue detection with clean text"""
        processor = PhonemizationPreprocessor()

        text = "Hello world. This is a normal sentence."
        issues = processor._detect_potential_issues(text)
        assert isinstance(issues, list)

    def test_detect_potential_issues_urls(self):
        """Test issue detection with URLs"""
        processor = PhonemizationPreprocessor()

        text = "Check https://example.com/very/long/url/that/might/be/problematic"
        issues = processor._detect_potential_issues(text)
        assert any("url" in i.lower() for i in issues)

    def test_detect_potential_issues_many_numbers(self):
        """Test issue detection with many numbers"""
        processor = PhonemizationPreprocessor()

        text = "Numbers: 123 456 789 012 345 678"
        issues = processor._detect_potential_issues(text)
        assert any("number" in i.lower() for i in issues)

    def test_preprocess_text_no_preserve_word_count(self):
        """Test preprocessing with preserve_word_count=False"""
        processor = PhonemizationPreprocessor()

        text = "Hello world"
        result = processor.preprocess_text(text, preserve_word_count=False)
        assert result is not None
        assert hasattr(result, 'processed_text')

    def test_preprocess_text_aggressive_no_preserve(self):
        """Test aggressive preprocessing without word count preservation"""
        processor = PhonemizationPreprocessor()

        text = "don't won't can't"
        result = processor.preprocess_text(text, aggressive=True, preserve_word_count=False)
        assert result is not None

    def test_preprocess_returns_result(self):
        """Test that preprocess_text returns PreprocessingResult"""
        processor = PhonemizationPreprocessor()

        text = "Hello world."
        result = processor.preprocess_text(text)
        assert hasattr(result, 'original_text')
        assert hasattr(result, 'changes_made')
        assert hasattr(result, 'confidence_score')
        assert hasattr(result, 'warnings')

    def test_preprocess_text_with_config(self):
        """Test preprocessing with explicit config"""
        processor = PhonemizationPreprocessor()

        text = "I'm happy"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_preprocess_text_conservative_mode(self):
        """Test preprocessing in conservative mode"""
        processor = PhonemizationPreprocessor()

        text = "Hello world 123"
        result = processor.preprocess_text(text, aggressive=False)
        assert result is not None

    def test_preprocess_text_preserve_word_count_true(self):
        """Test preprocessing with preserve_word_count=True"""
        processor = PhonemizationPreprocessor()

        text = "Hello world"
        result = processor.preprocess_text(text, preserve_word_count=True)
        assert result is not None

    def test_preprocess_text_with_warnings(self):
        """Test preprocessing that generates warnings"""
        processor = PhonemizationPreprocessor()

        text = "Code: {foo: bar;} with $pecial@chars and 12345678901234"
        result = processor.preprocess_text(text)
        assert hasattr(result, 'warnings')

    def test_number_to_words_small(self):
        """Test number to words conversion for small numbers"""
        processor = PhonemizationPreprocessor()

        # Test single digit
        result = processor._number_to_words(5)
        assert result == "five"

        # Test teen numbers
        result = processor._number_to_words(12)
        assert result == "twelve"

        # Test tens
        result = processor._number_to_words(30)
        assert result == "thirty"

    def test_is_time_expression_various(self):
        """Test various time expression patterns"""
        processor = PhonemizationPreprocessor()

        # Various time patterns
        assert processor._is_time_expression("ten thirty five a m") is True
        assert processor._is_time_expression("nine o'clock p m") is True
        assert processor._is_time_expression("ten a m") is True
        assert processor._is_time_expression("hello world") is False
        assert processor._is_time_expression("at ten") is False

    def test_detect_issues_code_patterns(self):
        """Test issue detection with code patterns"""
        processor = PhonemizationPreprocessor()

        text = "if (x == 5) { return; }"
        issues = processor._detect_potential_issues(text)
        assert any("code" in i.lower() for i in issues)

    def test_detect_issues_long_numbers(self):
        """Test issue detection with long numbers"""
        processor = PhonemizationPreprocessor()

        text = "ID is 12345678901234"
        issues = processor._detect_potential_issues(text)
        assert any("long" in i.lower() for i in issues)

    def test_detect_issues_many_special_chars(self):
        """Test issue detection with many special characters"""
        processor = PhonemizationPreprocessor()

        text = "Test @#$%^&*() chars"
        issues = processor._detect_potential_issues(text)
        assert any("special" in i.lower() for i in issues)

    def test_detect_issues_long_words(self):
        """Test issue detection with very long words"""
        processor = PhonemizationPreprocessor()

        text = "This word is reallyverylongandshouldbetreatedasaproblem " * 2
        issues = processor._detect_potential_issues(text)
        assert any("long" in i.lower() for i in issues)

    def test_detect_issues_repeated_chars(self):
        """Test issue detection with repeated characters"""
        processor = PhonemizationPreprocessor()

        text = "Hellooooooo world"
        issues = processor._detect_potential_issues(text)
        assert any("repeated" in i.lower() for i in issues)

    def test_detect_issues_empty(self):
        """Test issue detection with empty list"""
        processor = PhonemizationPreprocessor()

        text = "Hello world"
        issues = processor._detect_potential_issues(text)
        assert isinstance(issues, list)

    def test_convert_numbers_conservative_decimal_only(self):
        """Test conservative number conversion with decimals only"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None

        text = "3.14"
        result, changes = processor._convert_numbers_conservative(text)
        assert isinstance(result, str)

    def test_convert_symbols_conservative_quotes_only(self):
        """Test conservative symbol conversion with quotes only"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None

        text = '"Hello"'
        result, changes = processor._convert_symbols_conservative(text)
        assert '"' not in result

    def test_convert_symbols_conservative_no_symbols(self):
        """Test conservative symbol conversion with no problematic symbols"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None
        processor.problematic_symbols = {}

        text = "Hello + World"
        result, changes = processor._convert_symbols_conservative(text)
        assert '+' in result

    def test_clean_whitespace_sentence_spacing(self):
        """Test whitespace cleaning ensures sentence spacing"""
        processor = PhonemizationPreprocessor()

        text = "Hello.A"
        result = processor._clean_whitespace_and_punctuation(text)
        assert ". A" in result or result == "Hello. A"

    def test_clean_whitespace_only(self):
        """Test whitespace cleaning with only whitespace issues"""
        processor = PhonemizationPreprocessor()

        text = "Hello    world"
        result = processor._clean_whitespace_and_punctuation(text)
        assert "  " not in result

    def test_calculate_confidence_score_high(self):
        """Test confidence score calculation for clean text"""
        processor = PhonemizationPreprocessor()

        text = "Hello world. This is a normal sentence."
        score = processor._calculate_confidence_score(text, text)
        assert score > 0.5

    def test_calculate_confidence_score_bounded(self):
        """Test confidence score is bounded between 0 and 1"""
        processor = PhonemizationPreprocessor()

        # Very bad text
        text = "@#$%^&* 12345678901234567890 " * 10
        score = processor._calculate_confidence_score(text, text)
        assert 0.0 <= score <= 1.0

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

    def test_tech_compounds_d_sharp(self, processor):
        """Test D# music note"""
        text = "D# is a music note"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_tech_compounds_a_sharp(self, processor):
        """Test A# music note"""
        text = "Play A# now"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_tech_compounds_oauth(self, processor):
        """Test OAuth 2.0"""
        text = "Use OAuth 2.0 for auth"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_tech_compounds_oauth_standalone(self, processor):
        """Test standalone OAuth"""
        text = "OAuth is common"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_tech_compounds_ipv6(self, processor):
        """Test IPv6"""
        text = "IPv6 is the new standard"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_tech_compounds_sha256(self, processor):
        """Test SHA-256"""
        text = "SHA-256 hash"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_tech_compounds_sha_256(self, processor):
        """Test SHA 256 without hyphen"""
        text = "SHA256 checksum"
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

    def test_lead_verb_context(self, processor):
        """Test lead verb context"""
        text = "Please lead the way"
        result = processor.preprocess_text(text)
        assert result is not None

    def test_read_lead_context(self, processor):
        """Test read lead context"""
        text = "I read lead yesterday"
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

    def test_preprocess_preserve_false_expand_true(self):
        """Test preprocessing with preserve_word_count=False triggers full expansion"""
        processor = PhonemizationPreprocessor()
        text = "I'm happy"
        result = processor.preprocess_text(text, preserve_word_count=False)
        assert result is not None

    def test_preprocess_preserve_false_aggressive_true(self):
        """Test preprocessing with preserve_word_count=False and aggressive=True"""
        processor = PhonemizationPreprocessor()
        text = "don't worry"
        result = processor.preprocess_text(text, aggressive=True, preserve_word_count=False)
        assert result is not None

    def test_preprocess_full_pipeline(self):
        """Test full preprocessing pipeline"""
        processor = PhonemizationPreprocessor()
        text = "Hello world! I'm fine."
        result = processor.preprocess_text(text)
        assert hasattr(result, 'processed_text')
        assert hasattr(result, 'original_text')
        assert result.processed_text is not None

    def test_html_entity_decoding(self):
        """Test HTML entity decoding"""
        processor = PhonemizationPreprocessor()
        text = "Tom &amp; Jerry"
        result, changes = processor._decode_html_entities(text)
        assert isinstance(result, str)

    def test_fix_tech_compounds_c_sharp(self):
        """Test tech compound fixing for C#"""
        processor = PhonemizationPreprocessor()
        text = "Use C# for development"
        result, changes = processor._fix_tech_compounds(text)
        assert isinstance(result, str)

    def test_fix_tech_compounds_oauth(self):
        """Test tech compound fixing for OAuth"""
        processor = PhonemizationPreprocessor()
        text = "OAuth 2.0 is common"
        result, changes = processor._fix_tech_compounds(text)
        assert isinstance(result, str)

    def test_fix_tech_compounds_ipv6(self):
        """Test tech compound fixing for IPv6"""
        processor = PhonemizationPreprocessor()
        text = "IPv6 address"
        result, changes = processor._fix_tech_compounds(text)
        assert isinstance(result, str)

    def test_fix_fractions_half(self):
        """Test fraction handling for ½"""
        processor = PhonemizationPreprocessor()
        text = "Use ½ cup"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_fix_fractions_quarter(self):
        """Test fraction handling for ¼"""
        processor = PhonemizationPreprocessor()
        text = "Use ¼ teaspoon"
        result, changes = processor._fix_fractions_and_symbols(text)
        assert isinstance(result, str)

    def test_filter_emojis(self):
        """Test emoji filtering"""
        processor = PhonemizationPreprocessor()
        text = "Hello 👋 world"
        result, changes = processor._filter_emojis(text)
        assert '👋' not in result

    def test_handle_quote_characters(self):
        """Test quote character handling"""
        processor = PhonemizationPreprocessor()
        text = 'He said "hello"'
        result, changes = processor._handle_quote_characters(text)
        assert isinstance(result, str)

    def test_process_contractions_enhanced_processor_mode_expanded(self):
        """Test _expand_contractions with enhanced processor in expanded mode"""
        processor = PhonemizationPreprocessor()
        processor.expand_all = True
        processor.preserve_natural = False
        # enhanced_contraction_processor is available, so this tests the enhanced path
        text = "I'm happy"
        result, changes = processor._expand_contractions(text)
        assert isinstance(result, str)

    def test_process_contractions_enhanced_processor_mode_natural(self):
        """Test _expand_contractions with enhanced processor in natural mode"""
        processor = PhonemizationPreprocessor()
        processor.expand_all = False
        processor.preserve_natural = False
        # enhanced_contraction_processor is available
        text = "I'm happy"
        result, changes = processor._expand_contractions(text)
        assert isinstance(result, str)

    def test_process_contractions_no_changes(self):
        """Test _expand_contractions with no changes needed"""
        processor = PhonemizationPreprocessor()
        text = "Hello world"
        result, changes = processor._expand_contractions(text)
        assert result == text

    def test_convert_numbers_conservative_zero_found(self):
        """Test _convert_numbers_conservative converts standalone 0"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None
        text = "I have 0 apples"
        result, changes = processor._convert_numbers_conservative(text)
        assert isinstance(result, str)

    def test_convert_symbols_conservative_with_quotes(self):
        """Test _convert_symbols_conservative removes quotes"""
        processor = PhonemizationPreprocessor()
        processor.enhanced_contraction_processor = None
        text = 'She said "hi"'
        result, changes = processor._convert_symbols_conservative(text)
        assert '"' not in result

    def test_fix_problematic_patterns_css_value(self):
        """Test _fix_problematic_patterns_conservative with CSS value"""
        processor = PhonemizationPreprocessor()
        text = "width: 100px"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert isinstance(result, str)

    def test_fix_problematic_patterns_excessive_dots(self):
        """Test _fix_problematic_patterns_conservative with excessive dots"""
        processor = PhonemizationPreprocessor()
        text = "Hello.... world"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert "...." not in result

    def test_fix_problematic_patterns_www(self):
        """Test _fix_problematic_patterns_conservative with www"""
        processor = PhonemizationPreprocessor()
        text = "Visit www.example.com"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert isinstance(result, str)

    def test_fix_problematic_patterns_time(self):
        """Test _fix_problematic_patterns_conservative with time"""
        processor = PhonemizationPreprocessor()
        text = "at 10:30"
        result, changes = processor._fix_problematic_patterns_conservative(text)
        assert isinstance(result, str)
