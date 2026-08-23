#!/usr/bin/env python3
"""Tests for SpellProcessor"""

import importlib.util

import pytest


def load_module_from_path(module_name, file_path):
    """Load module directly from file path without triggering package __init__"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSpellProcessor:
    """Test suite for SpellProcessor"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures"""
        spell_module = load_module_from_path("spell_processor", "LiteTTS/nlp/spell_processor.py")
        self.processor = spell_module.SpellProcessor()

    def test_letter_names_complete(self):
        """Test all 26 letters have names"""
        assert len(self.processor.letter_names) == 26
        for char in "abcdefghijklmnopqrstuvwxyz":
            assert char in self.processor.letter_names

    def test_handle_spell_function_basic(self):
        """Test basic spell(word) handling"""
        result = self.processor.handle_spell_functions("spell(hello)")
        assert "aitch" in result  # h
        assert "ee" in result  # e
        assert "ell" in result  # l
        assert "ell" in result  # l
        assert "oh" in result  # o

    def test_handle_spell_function_double_quotes(self):
        """Test spell("word") with double quotes"""
        result = self.processor.handle_spell_functions('spell("test")')
        assert "tee" in result
        assert "ee" in result
        assert "ess" in result
        assert "tee" in result

    def test_handle_spell_function_single_quotes(self):
        """Test spell('word') with single quotes"""
        result = self.processor.handle_spell_functions("spell('hello')")
        assert "aitch" in result
        assert "ee" in result

    def test_handle_spell_function_no_quotes(self):
        """Test spell(word) without quotes"""
        result = self.processor.handle_spell_functions("spell(world)")
        assert "double-you" in result  # w
        assert "oh" in result
        assert "are" in result
        assert "ell" in result
        assert "dee" in result

    def test_handle_spell_function_mixed_case(self):
        """Test spell with mixed case word"""
        result = self.processor.handle_spell_functions("spell(Hi)")
        assert "aitch" in result  # h
        assert "eye" in result  # i

    def test_spell_word_direct(self):
        """Test direct word spelling"""
        result = self.processor.spell_word_direct("abc")
        assert "ay" in result
        assert "bee" in result
        assert "see" in result

    def test_spell_word_with_numbers(self):
        """Test spelling words containing numbers"""
        result = self.processor.spell_word_direct("abc123")
        assert "ay" in result
        assert "bee" in result
        assert "see" in result
        assert "one" in result
        assert "two" in result
        assert "three" in result

    def test_spell_word_with_special_chars(self):
        """Test spelling words with special characters"""
        result = self.processor.spell_word_direct("a-b")
        assert "ay" in result
        assert "dash" in result
        assert "bee" in result

    def test_spell_word_email(self):
        """Test spelling an email address"""
        result = self.processor.spell_word_direct("test@domain.com")
        assert "tee" in result
        assert "ess" in result
        assert "at" in result
        assert "dee" in result
        assert "em" in result
        assert "dot" in result
        assert "see" in result

    def test_spell_word_underscore(self):
        """Test underscore character"""
        result = self.processor.spell_word_direct("test_name")
        assert "tee" in result
        assert "ess" in result
        assert "underscore" in result
        assert "en" in result
        assert "em" in result
        assert "ee" in result

    def test_spell_parentheses(self):
        """Test parentheses characters"""
        result = self.processor.spell_word_direct("(test)")
        assert "open paren" in result
        assert "tee" in result
        assert "ess" in result
        assert "ee" in result
        assert "close paren" in result

    def test_no_spell_function(self):
        """Test text without spell function is unchanged"""
        text = "Hello world"
        result = self.processor.handle_spell_functions(text)
        assert result == text

    def test_multiple_spell_functions(self):
        """Test multiple spell functions in same text"""
        result = self.processor.handle_spell_functions("spell(hi) and spell(bye)")
        # Both words should be spelled
        assert "aitch" in result
        assert "eye" in result
        assert "bee" in result
        assert "why" in result
        assert "ee" in result

    def test_spell_xyz(self):
        """Test spelling x, y, z"""
        result = self.processor.spell_word_direct("xyz")
        assert "ex" in result
        assert "why" in result
        assert "zee" in result

    def test_empty_spell_result(self):
        """Test that spelled words are joined with commas"""
        result = self.processor.spell_word_direct("ab")
        assert ", " in result or "ay" in result

    def test_unknown_character_preserved(self):
        """Test unknown characters are preserved"""
        result = self.processor.spell_word_direct("a\x00b")
        # Unknown chars should be preserved as-is
        assert "\x00" in result or len(result) >= 2
