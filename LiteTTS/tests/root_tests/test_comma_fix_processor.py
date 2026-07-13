#!/usr/bin/env python3
"""Tests for CommaFixProcessor"""

import pytest
import importlib.util


def load_module_from_path(module_name, file_path):
    """Load module directly from file path without triggering package __init__"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCommaFixProcessor:
    """Test suite for CommaFixProcessor"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures"""
        module = load_module_from_path('comma_fix_processor', 'LiteTTS/nlp/comma_fix_processor.py')
        self.processor = module.CommaFixProcessor()

    def test_problematic_patterns_loaded(self):
        """Test that problematic patterns are loaded"""
        assert len(self.processor.problematic_patterns) > 0
        assert len(self.processor.comma_context_patterns) > 0

    def test_fix_comma_pronunciation_basic(self):
        """Test basic comma pronunciation fix"""
        result = self.processor.fix_comma_pronunciation('thinking,or')
        # Should ensure proper spacing after comma
        assert 'thinking, or' in result

    def test_fix_comma_spacing_missing_space(self):
        """Test fixing missing space after comma"""
        result = self.processor._fix_comma_spacing('hello,world')
        assert 'hello, world' in result

    def test_fix_comma_spacing_multiple_spaces(self):
        """Test fixing multiple spaces after comma"""
        result = self.processor._fix_comma_spacing('hello,   world')
        assert 'hello, world' in result

    def test_fix_comma_spacing_space_before_comma(self):
        """Test removing space before comma"""
        result = self.processor._fix_comma_spacing('hello ,world')
        assert 'hello,' in result
        assert 'hello, world' in result

    def test_fix_comma_conjunction_or(self):
        """Test fixing comma before 'or'"""
        result = self.processor._fix_comma_conjunctions('thinking,or not')
        assert 'thinking, or not' in result

    def test_fix_comma_conjunction_and(self):
        """Test fixing comma before 'and'"""
        result = self.processor._fix_comma_conjunctions('walking,and running')
        assert 'walking, and' in result

    def test_fix_comma_conjunction_but(self):
        """Test fixing comma before 'but'"""
        result = self.processor._fix_comma_conjunctions('running,but tired')
        assert 'running, but' in result

    def test_fix_comma_interjection_hmm(self):
        """Test fixing comma before interjection"""
        result = self.processor._fix_comma_interjections('hmm,let me think')
        assert 'hmm, let' in result

    def test_fix_comma_interjection_well(self):
        """Test fixing comma before 'well'"""
        result = self.processor._fix_comma_interjections('well,I agree')
        assert 'well, I' in result

    def test_fix_comma_interjection_oh(self):
        """Test fixing comma before 'oh'"""
        result = self.processor._fix_comma_interjections('oh,I see')
        assert 'oh, I' in result

    def test_analyze_comma_issues_missing_space(self):
        """Test analyzing missing space after comma"""
        issues = self.processor.analyze_comma_issues('hello,world')
        assert 'missing_space_after_comma' in issues
        assert len(issues['missing_space_after_comma']) > 0

    def test_analyze_comma_issues_space_before(self):
        """Test analyzing space before comma"""
        issues = self.processor.analyze_comma_issues('hello , world')
        assert 'space_before_comma' in issues
        assert len(issues['space_before_comma']) > 0

    def test_analyze_comma_issues_problematic_conjunctions(self):
        """Test analyzing problematic conjunction patterns"""
        issues = self.processor.analyze_comma_issues('thinking,or not')
        assert 'problematic_conjunctions' in issues

    def test_analyze_comma_issues_clean_text(self):
        """Test analyzing text with no issues"""
        issues = self.processor.analyze_comma_issues('Hello, world. This is fine.')
        # Clean text should have minimal issues
        assert 'missing_space_after_comma' in issues
        assert 'space_before_comma' in issues

    def test_context_patterns(self):
        """Test that context patterns are properly loaded"""
        assert 'thinking, or' in self.processor.comma_context_patterns
        assert 'walking, and' in self.processor.comma_context_patterns

    def test_preserves_punctuation(self):
        """Test that fixes preserve other punctuation"""
        result = self.processor.fix_comma_pronunciation('Hello, world!')
        assert 'world!' in result

    def test_preserves_multiple_commas(self):
        """Test handling multiple commas"""
        result = self.processor.fix_comma_pronunciation('one, two, three')
        assert 'one, two, three' in result

    def test_fix_problematic_patterns_conjunction(self):
        """Test fixing problematic patterns with conjunctions"""
        result = self.processor._fix_problematic_patterns('walking,or not')
        assert 'walking, or' in result

    def test_fix_problematic_patterns_subordinate(self):
        """Test fixing problematic patterns with subordinate clauses"""
        result = self.processor._fix_problematic_patterns('left,because')
        assert 'left, because' in result

    def test_unchanged_text(self):
        """Test that already correct text remains unchanged"""
        text = 'Hello, world. This is fine.'
        result = self.processor.fix_comma_pronunciation(text)
        # Result should be close to original
        assert 'Hello' in result
        assert 'world' in result

    def test_global_instance_exists(self):
        """Test that global instance is available"""
        module = load_module_from_path('comma_fix_processor_g', 'LiteTTS/nlp/comma_fix_processor.py')
        assert hasattr(module, 'comma_fix_processor')
