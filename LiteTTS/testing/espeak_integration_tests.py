#!/usr/bin/env python3
"""
eSpeak Integration Test Cases for Automated Audio Quality Testing

This module provides specific test cases to validate our recent eSpeak integration
improvements, particularly the question mark and asterisk pronunciation fixes.
"""

from typing import List, Dict, Any
from .audio_quality_tester import AudioTestCase
import logging

logger = logging.getLogger(__name__)


class EspeakIntegrationTestSuite:
    """
    Test suite specifically for validating eSpeak integration improvements
    """
    
    def __init__(self):
        self.test_cases = []
        self._create_test_cases()
    
    def _create_test_cases(self):
        """
        Create comprehensive test cases for eSpeak integration validation
        """
        # Critical symbol processing tests
        self.test_cases.extend(self._create_symbol_processing_tests())
        
        # Currency and datetime processing tests
        self.test_cases.extend(self._create_currency_datetime_tests())
        
        # Context-aware processing tests
        self.test_cases.extend(self._create_context_aware_tests())
        
        # Edge cases and regression tests
        self.test_cases.extend(self._create_edge_case_tests())
    
    def _create_symbol_processing_tests(self) -> List[AudioTestCase]:
        """
        Create test cases for symbol processing improvements
        """
        return [
            # Question mark pronunciation fix
            AudioTestCase(
                test_id="espeak_question_mark_basic",
                input_text="Hello? How are you?",
                expected_transcription="hello question mark how are you question mark",
                test_category="espeak_symbols",
                description="Basic question mark pronunciation test",
                priority="critical",
                expected_symbols=["?"],
                expected_pronunciations={"?": "question mark"},
                min_pronunciation_accuracy=0.95
            ),
            
            AudioTestCase(
                test_id="espeak_question_mark_multiple",
                input_text="What time is it? Are you ready? Let's go?",
                expected_transcription="what time is it question mark are you ready question mark let's go question mark",
                test_category="espeak_symbols",
                description="Multiple question marks test",
                priority="critical",
                expected_symbols=["?"],
                expected_pronunciations={"?": "question mark"},
                min_pronunciation_accuracy=0.95
            ),
            
            # Asterisk pronunciation fix
            AudioTestCase(
                test_id="espeak_asterisk_basic",
                input_text="Use the * symbol carefully",
                expected_transcription="use the asterisk symbol carefully",
                test_category="espeak_symbols",
                description="Basic asterisk pronunciation test",
                priority="critical",
                expected_symbols=["*"],
                expected_pronunciations={"*": "asterisk"},
                min_pronunciation_accuracy=0.95
            ),
            
            AudioTestCase(
                test_id="espeak_asterisk_math",
                input_text="Calculate 5 * 3 = 15",
                expected_transcription="calculate 5 asterisk 3 equals 15",
                test_category="espeak_symbols",
                description="Asterisk in mathematical context",
                priority="high",
                expected_symbols=["*"],
                expected_pronunciations={"*": "asterisk"},
                min_pronunciation_accuracy=0.9
            ),
            
            # Combined symbol tests
            AudioTestCase(
                test_id="espeak_combined_symbols",
                input_text="What is 2 * 3? The answer is 6!",
                expected_transcription="what is 2 asterisk 3 question mark the answer is 6 exclamation mark",
                test_category="espeak_symbols",
                description="Combined symbols test",
                priority="high",
                expected_symbols=["*", "?", "!"],
                expected_pronunciations={
                    "*": "asterisk",
                    "?": "question mark",
                    "!": "exclamation mark"
                },
                min_pronunciation_accuracy=0.9
            ),
            
            # Quote handling test
            AudioTestCase(
                test_id="espeak_quote_handling",
                input_text='She said "Hello world" to everyone',
                expected_transcription="she said hello world to everyone",
                test_category="espeak_symbols",
                description="Quote character handling test",
                priority="normal",
                min_pronunciation_accuracy=0.9
            ),
            
            # Ampersand test
            AudioTestCase(
                test_id="espeak_ampersand",
                input_text="Tom & Jerry are friends",
                expected_transcription="tom and jerry are friends",
                test_category="espeak_symbols",
                description="Ampersand pronunciation test",
                priority="normal",
                expected_symbols=["&"],
                expected_pronunciations={"&": "and"},
                min_pronunciation_accuracy=0.9
            )
        ]
    
    def _create_currency_datetime_tests(self) -> List[AudioTestCase]:
        """
        Create test cases for currency and datetime processing
        """
        return [
            AudioTestCase(
                test_id="espeak_currency_basic",
                input_text="The cost is $50.99",
                expected_transcription="the cost is fifty dollars and ninety nine cents",
                test_category="espeak_currency",
                description="Basic currency processing test",
                priority="high",
                min_pronunciation_accuracy=0.9
            ),
            
            AudioTestCase(
                test_id="espeak_currency_large",
                input_text="The price is $1,234.56",
                expected_transcription="the price is one thousand two hundred thirty four dollars and fifty six cents",
                test_category="espeak_currency",
                description="Large currency amount test",
                priority="normal",
                min_pronunciation_accuracy=0.85
            ),
            
            AudioTestCase(
                test_id="espeak_percentage",
                input_text="The tax rate is 8.5%",
                expected_transcription="the tax rate is eight point five percent",
                test_category="espeak_currency",
                description="Percentage processing test",
                priority="normal",
                expected_symbols=["%"],
                expected_pronunciations={"%": "percent"},
                min_pronunciation_accuracy=0.9
            ),
            
            AudioTestCase(
                test_id="espeak_datetime_basic",
                input_text="The meeting is at 3:30 PM",
                expected_transcription="the meeting is at three thirty p m",
                test_category="espeak_datetime",
                description="Basic time processing test",
                priority="normal",
                min_pronunciation_accuracy=0.85
            )
        ]
    
    def _create_context_aware_tests(self) -> List[AudioTestCase]:
        """
        Create test cases for context-aware symbol processing
        """
        return [
            AudioTestCase(
                test_id="espeak_url_context",
                input_text="Visit https://example.com for more info",
                expected_transcription="visit https example com for more info",
                test_category="espeak_context",
                description="URL context processing test",
                priority="normal",
                min_pronunciation_accuracy=0.8
            ),
            
            AudioTestCase(
                test_id="espeak_email_context",
                input_text="Email me at test@example.com",
                expected_transcription="email me at test example com",
                test_category="espeak_context",
                description="Email context processing test",
                priority="normal",
                min_pronunciation_accuracy=0.8
            ),
            
            AudioTestCase(
                test_id="espeak_filepath_context",
                input_text="The file is at C:\\Users\\test.txt",
                expected_transcription="the file is at c users test txt",
                test_category="espeak_context",
                description="File path context processing test",
                priority="low",
                min_pronunciation_accuracy=0.7
            ),
            
            AudioTestCase(
                test_id="espeak_math_expression",
                input_text="Solve x + y = z * 2",
                expected_transcription="solve x plus y equals z asterisk 2",
                test_category="espeak_context",
                description="Mathematical expression test",
                priority="normal",
                expected_symbols=["*", "+", "="],
                expected_pronunciations={
                    "*": "asterisk",
                    "+": "plus",
                    "=": "equals"
                },
                min_pronunciation_accuracy=0.85
            )
        ]
    
    def _create_edge_case_tests(self) -> List[AudioTestCase]:
        """
        Create edge case and regression test cases
        """
        return [
            AudioTestCase(
                test_id="espeak_edge_isolated_symbols",
                input_text="? * & @ %",
                expected_transcription="question mark asterisk and at percent",
                test_category="espeak_edge_cases",
                description="Isolated symbols test",
                priority="normal",
                expected_symbols=["?", "*", "&", "@", "%"],
                expected_pronunciations={
                    "?": "question mark",
                    "*": "asterisk",
                    "&": "and",
                    "@": "at",
                    "%": "percent"
                },
                min_pronunciation_accuracy=0.9
            ),
            
            AudioTestCase(
                test_id="espeak_edge_long_text",
                input_text="This is a longer text with multiple symbols: What time is it? The cost is $25.99. Use the * symbol. Email test@example.com for more info!",
                expected_transcription="this is a longer text with multiple symbols what time is it question mark the cost is twenty five dollars and ninety nine cents use the asterisk symbol email test example com for more info exclamation mark",
                test_category="espeak_edge_cases",
                description="Long text with multiple symbols",
                priority="normal",
                min_pronunciation_accuracy=0.8,
                max_rtf=0.3  # Allow slightly higher RTF for longer text
            ),
            
            AudioTestCase(
                test_id="espeak_regression_basic",
                input_text="Hello world",
                expected_transcription="hello world",
                test_category="espeak_regression",
                description="Basic regression test",
                priority="critical",
                min_pronunciation_accuracy=0.95,
                min_mos_score=4.0
            ),
            
            AudioTestCase(
                test_id="espeak_regression_no_symbols",
                input_text="The quick brown fox jumps over the lazy dog",
                expected_transcription="the quick brown fox jumps over the lazy dog",
                test_category="espeak_regression",
                description="No symbols regression test",
                priority="high",
                min_pronunciation_accuracy=0.95,
                min_mos_score=4.0
            )
        ]
    
    def get_test_cases(self, category: str = None, priority: str = None) -> List[AudioTestCase]:
        """
        Get test cases filtered by category and/or priority
        """
        filtered_cases = self.test_cases
        
        if category:
            filtered_cases = [tc for tc in filtered_cases if tc.test_category == category]
        
        if priority:
            filtered_cases = [tc for tc in filtered_cases if tc.priority == priority]
        
        return filtered_cases
    
    def get_critical_tests(self) -> List[AudioTestCase]:
        """
        Get only critical test cases for quick validation
        """
        return self.get_test_cases(priority="critical")
    
    def get_symbol_processing_tests(self) -> List[AudioTestCase]:
        """
        Get symbol processing specific tests
        """
        return self.get_test_cases(category="espeak_symbols")
    
    def get_regression_tests(self) -> List[AudioTestCase]:
        """
        Get regression test cases
        """
        return self.get_test_cases(category="espeak_regression")
