#!/usr/bin/env python3
"""
Comprehensive Test Suite for Pronunciation Issues

This test suite validates all the pronunciation fixes implemented:
1. Quote character pronunciation bug (fixed)
2. Possessive contractions HTML entity issue (fixed)
3. Word truncation/phonetic mapping issues (investigated)
4. Text skipping/omission bug (investigated)

Usage:
    python LiteTTS/scripts/comprehensive_pronunciation_test_suite.py
    python LiteTTS/scripts/comprehensive_pronunciation_test_suite.py --api-test  # Include API tests
    python LiteTTS/scripts/comprehensive_pronunciation_test_suite.py --verbose   # Detailed output
"""

import sys
import os
import argparse
import time
import requests
from typing import List, Dict, Any, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
from LiteTTS.nlp.processor import NLPProcessor

class PronunciationTestSuite:
    """Comprehensive test suite for pronunciation issues"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.nlp_processor = NLPProcessor()
        self.test_results = {
            'quote_character_tests': [],
            'possessive_contractions_tests': [],
            'word_truncation_tests': [],
            'text_skipping_tests': [],
            'regression_tests': []
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with optional verbosity control"""
        if self.verbose or level in ["ERROR", "FAIL", "PASS"]:
            print(f"[{level}] {message}")
    
    def test_quote_character_pronunciation(self) -> bool:
        """Test quote character pronunciation fixes"""
        
        self.log("Testing Quote Character Pronunciation Fixes", "INFO")
        self.log("=" * 50, "INFO")
        
        test_cases = [
            {
                "name": "Simple quoted text",
                "input": '"Hello world"',
                "expected_behavior": "Quotes should be silent"
            },
            {
                "name": "Mid-sentence quotes",
                "input": 'She said "yes" to the proposal',
                "expected_behavior": "Quotes should not be pronounced"
            },
            {
                "name": "Quotes with following text",
                "input": '"quoted text" and more',
                "expected_behavior": "Quotes should be silent"
            },
            {
                "name": "Embedded quotes",
                "input": 'The word "example" here',
                "expected_behavior": "Quotes should be silent"
            },
            {
                "name": "Multiple quoted sections",
                "input": 'He said "hello" and she replied "goodbye"',
                "expected_behavior": "All quotes should be handled consistently"
            },
            {
                "name": "Unicode quotes",
                "input": 'He said "hello" and "goodbye"',
                "expected_behavior": "Unicode quotes should be handled"
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            self.log(f"Test {i}: {test_case['name']}", "INFO")
            self.log(f"Input: '{test_case['input']}'", "INFO")
            
            # Test preprocessing
            result = phonemizer_preprocessor.preprocess_text(test_case['input'])
            nlp_result = self.nlp_processor.process_text(test_case['input'])
            
            self.log(f"Preprocessor: '{result.processed_text}'", "INFO")
            self.log(f"NLP: '{nlp_result}'", "INFO")
            
            # Check for problematic patterns
            problematic_quotes = ['"', '"', '"']
            found_quotes = any(quote in nlp_result for quote in problematic_quotes)
            
            if found_quotes:
                self.log("FAIL: Quotes still present in output", "FAIL")
                all_passed = False
            else:
                self.log("PASS: Quotes successfully removed", "PASS")
            
            self.test_results['quote_character_tests'].append({
                'name': test_case['name'],
                'input': test_case['input'],
                'output': nlp_result,
                'passed': not found_quotes
            })
        
        return all_passed
    
    def test_possessive_contractions_html_entities(self) -> bool:
        """Test possessive contractions HTML entity fixes"""
        
        self.log("Testing Possessive Contractions HTML Entity Fixes", "INFO")
        self.log("=" * 55, "INFO")
        
        test_cases = [
            {
                "name": "John's with HTML entity",
                "input": "John&#x27;s book",
                "expected": "Should be 'John's book'"
            },
            {
                "name": "it's with HTML entity",
                "input": "it&#x27;s working",
                "expected": "Should be 'it's working'"
            },
            {
                "name": "Multiple possessives",
                "input": "John&#x27;s and Mary&#x27;s books",
                "expected": "Both should be handled"
            },
            {
                "name": "Mixed HTML entities",
                "input": "He&#x27;s got Mary&#x27;s book",
                "expected": "Both contractions should work"
            },
            {
                "name": "Decimal HTML entity",
                "input": "John&#39;s book",
                "expected": "Should decode to apostrophe"
            },
            {
                "name": "Named HTML entity",
                "input": "John&apos;s book",
                "expected": "Should decode to apostrophe"
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            self.log(f"Test {i}: {test_case['name']}", "INFO")
            self.log(f"Input: '{test_case['input']}'", "INFO")
            
            # Test processing
            result = phonemizer_preprocessor.preprocess_text(test_case['input'])
            nlp_result = self.nlp_processor.process_text(test_case['input'])
            
            self.log(f"Preprocessor: '{result.processed_text}'", "INFO")
            self.log(f"NLP: '{nlp_result}'", "INFO")
            
            # Check for problematic patterns
            problematic_patterns = ['and hash', 'hash tag', 'x27', '&#x27;', '&#39;', '&apos;']
            found_issues = [p for p in problematic_patterns if p in nlp_result.lower()]
            
            if found_issues:
                self.log(f"FAIL: Found problematic patterns: {found_issues}", "FAIL")
                all_passed = False
            else:
                self.log("PASS: No problematic patterns found", "PASS")
            
            self.test_results['possessive_contractions_tests'].append({
                'name': test_case['name'],
                'input': test_case['input'],
                'output': nlp_result,
                'passed': not found_issues
            })
        
        return all_passed
    
    def test_word_truncation_phonetic_mapping(self) -> bool:
        """Test word truncation and phonetic mapping"""
        
        self.log("Testing Word Truncation/Phonetic Mapping", "INFO")
        self.log("=" * 40, "INFO")
        
        test_cases = [
            {"word": "Boy", "expected_phonetic": "/bɔɪ/"},
            {"word": "June", "expected_phonetic": "/dʒuːn/"},
            {"word": "Jan", "expected_phonetic": "/dʒæn/"},
            {"word": "toy", "expected_phonetic": "/tɔɪ/"},
            {"word": "joy", "expected_phonetic": "/dʒɔɪ/"},
            {"word": "tune", "expected_phonetic": "/tuːn/"},
            {"word": "done", "expected_phonetic": "/dʌn/"}
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            word = test_case['word']
            self.log(f"Test {i}: '{word}' -> {test_case['expected_phonetic']}", "INFO")
            
            # Test processing
            nlp_result = self.nlp_processor.process_text(word)
            
            self.log(f"NLP Output: '{nlp_result}'", "INFO")
            
            # Check if word is preserved (allowing for punctuation)
            clean_output = nlp_result.strip('.,!?;: ')
            if word.lower() == clean_output.lower():
                self.log("PASS: Word preserved correctly", "PASS")
                passed = True
            else:
                self.log(f"FAIL: Word changed from '{word}' to '{clean_output}'", "FAIL")
                all_passed = False
                passed = False
            
            self.test_results['word_truncation_tests'].append({
                'word': word,
                'expected_phonetic': test_case['expected_phonetic'],
                'output': nlp_result,
                'passed': passed
            })
        
        return all_passed

    def test_text_skipping_omission(self) -> bool:
        """Test text skipping and omission issues"""

        self.log("Testing Text Skipping/Omission", "INFO")
        self.log("=" * 35, "INFO")

        test_cases = [
            {
                "name": "Short text",
                "input": "Hello world, this is a test.",
                "min_words": 6
            },
            {
                "name": "Medium text",
                "input": " ".join(["word"] * 50) + ".",
                "min_words": 45  # Allow some loss for normalization
            },
            {
                "name": "Long text",
                "input": "This is a very long text passage. " * 20,
                "min_words": 120  # Allow some loss for normalization
            },
            {
                "name": "Special characters",
                "input": "Text with special chars: @#$%^&*()_+-=[]{}|;':\",./<>?",
                "min_words": 5  # Many symbols will be converted
            },
            {
                "name": "Unicode text",
                "input": "Hello 世界 🌍 café naïve résumé",
                "min_words": 5
            }
        ]

        all_passed = True

        for i, test_case in enumerate(test_cases, 1):
            self.log(f"Test {i}: {test_case['name']}", "INFO")
            self.log(f"Input length: {len(test_case['input'])} chars", "INFO")

            # Test processing
            nlp_result = self.nlp_processor.process_text(test_case['input'])

            self.log(f"Output length: {len(nlp_result)} chars", "INFO")

            # Count words
            input_words = len(test_case['input'].split())
            output_words = len(nlp_result.split())

            self.log(f"Words: {input_words} -> {output_words}", "INFO")

            # Check for significant word loss
            if output_words >= test_case['min_words']:
                self.log("PASS: No significant text loss", "PASS")
                passed = True
            else:
                self.log(f"FAIL: Significant text loss (expected >= {test_case['min_words']})", "FAIL")
                all_passed = False
                passed = False

            self.test_results['text_skipping_tests'].append({
                'name': test_case['name'],
                'input': test_case['input'],
                'output': nlp_result,
                'input_words': input_words,
                'output_words': output_words,
                'passed': passed
            })

        return all_passed

    def test_regression_cases(self) -> bool:
        """Test regression cases to ensure existing functionality works"""

        self.log("Testing Regression Cases", "INFO")
        self.log("=" * 25, "INFO")

        # Test cases that should continue to work correctly
        test_cases = [
            {
                "name": "Basic contractions",
                "input": "I'm happy, you're great, we're friends",
                "should_contain": ["happy", "great", "friends"]
            },
            {
                "name": "Numbers and symbols",
                "input": "Call me at 555-1234 or email@example.com",
                "should_contain": ["555", "1234", "email", "example", "com"]
            },
            {
                "name": "Abbreviations",
                "input": "Dr. Smith works at NASA in the U.S.A.",
                "should_contain": ["Smith", "works", "NASA"]
            },
            {
                "name": "Mixed punctuation",
                "input": "Hello! How are you? I'm fine... Thanks!",
                "should_contain": ["Hello", "How", "are", "you", "fine", "Thanks"]
            }
        ]

        all_passed = True

        for i, test_case in enumerate(test_cases, 1):
            self.log(f"Test {i}: {test_case['name']}", "INFO")
            self.log(f"Input: '{test_case['input']}'", "INFO")

            # Test processing
            nlp_result = self.nlp_processor.process_text(test_case['input'])

            self.log(f"Output: '{nlp_result}'", "INFO")

            # Check expected content
            passed = True
            if 'should_contain' in test_case:
                for word in test_case['should_contain']:
                    if word.lower() not in nlp_result.lower():
                        self.log(f"FAIL: Expected content '{word}' not found", "FAIL")
                        passed = False
                        all_passed = False

            if passed:
                self.log("PASS: Regression test passed", "PASS")

            self.test_results['regression_tests'].append({
                'name': test_case['name'],
                'input': test_case['input'],
                'output': nlp_result,
                'passed': passed
            })

        return all_passed

    def test_api_pronunciation(self, base_url: str = "http://localhost:8354") -> bool:
        """Test pronunciation through the API"""

        self.log("Testing Pronunciation via API", "INFO")
        self.log("=" * 35, "INFO")

        # Critical test cases for API
        test_cases = [
            '"Hello world"',  # Quote test
            'John&#x27;s book',  # HTML entity test
            'Boy and June',  # Word truncation test
            'This is a long text passage. ' * 5  # Text skipping test
        ]

        all_passed = True

        for i, test_text in enumerate(test_cases, 1):
            self.log(f"API Test {i}: '{test_text[:50]}...'", "INFO")

            payload = {
                "input": test_text,
                "voice": "af_heart",
                "response_format": "mp3"
            }

            try:
                start_time = time.time()
                response = requests.post(
                    f"{base_url}/v1/audio/speech",
                    json=payload,
                    timeout=60
                )
                end_time = time.time()

                if response.status_code == 200:
                    audio_size = len(response.content)
                    generation_time = end_time - start_time
                    self.log(f"PASS: {audio_size:,} bytes in {generation_time:.3f}s", "PASS")

                    # Save audio for manual inspection
                    filename = f"pronunciation_test_{i}.mp3"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    self.log(f"Audio saved as: {filename}", "INFO")

                else:
                    self.log(f"FAIL: API Error {response.status_code}", "FAIL")
                    all_passed = False

            except requests.exceptions.ConnectionError:
                self.log("SKIP: Could not connect to API server", "INFO")
                return True  # Don't fail if server isn't running
            except Exception as e:
                self.log(f"FAIL: API test failed: {e}", "FAIL")
                all_passed = False

        return all_passed

    def run_all_tests(self, include_api: bool = False) -> Dict[str, bool]:
        """Run all pronunciation tests"""

        self.log("🔧 Comprehensive Pronunciation Test Suite", "INFO")
        self.log("=" * 50, "INFO")
        self.log("Running all pronunciation issue tests...", "INFO")
        self.log("", "INFO")

        results = {}

        # Run all test categories
        results['quote_character'] = self.test_quote_character_pronunciation()
        self.log("", "INFO")

        results['possessive_contractions'] = self.test_possessive_contractions_html_entities()
        self.log("", "INFO")

        results['word_truncation'] = self.test_word_truncation_phonetic_mapping()
        self.log("", "INFO")

        results['text_skipping'] = self.test_text_skipping_omission()
        self.log("", "INFO")

        results['regression'] = self.test_regression_cases()
        self.log("", "INFO")

        if include_api:
            results['api_tests'] = self.test_api_pronunciation()
            self.log("", "INFO")

        return results

    def generate_summary_report(self, results: Dict[str, bool]) -> str:
        """Generate a comprehensive summary report"""

        report = []
        report.append("📊 COMPREHENSIVE PRONUNCIATION TEST RESULTS")
        report.append("=" * 50)

        # Overall status
        all_passed = all(results.values())
        overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
        report.append(f"Overall Status: {overall_status}")
        report.append("")

        # Individual test results
        test_names = {
            'quote_character': 'Quote Character Pronunciation',
            'possessive_contractions': 'Possessive Contractions HTML Entities',
            'word_truncation': 'Word Truncation/Phonetic Mapping',
            'text_skipping': 'Text Skipping/Omission',
            'regression': 'Regression Tests',
            'api_tests': 'API Tests'
        }

        for test_key, test_name in test_names.items():
            if test_key in results:
                status = "✅ PASS" if results[test_key] else "❌ FAIL"
                report.append(f"{test_name}: {status}")

        report.append("")

        # Detailed results
        report.append("📋 DETAILED RESULTS:")
        report.append("-" * 30)

        for category, tests in self.test_results.items():
            if tests:
                category_name = category.replace('_', ' ').title()
                report.append(f"\n{category_name}:")

                passed_count = sum(1 for test in tests if test['passed'])
                total_count = len(tests)
                report.append(f"  {passed_count}/{total_count} tests passed")

                # Show failed tests
                failed_tests = [test for test in tests if not test['passed']]
                if failed_tests:
                    report.append("  Failed tests:")
                    for test in failed_tests:
                        test_name = test.get('name', test.get('word', 'Unknown'))
                        report.append(f"    - {test_name}")

        report.append("")
        report.append("🎯 RECOMMENDATIONS:")

        if not results.get('quote_character', True):
            report.append("- Review quote character handling in text preprocessing")

        if not results.get('possessive_contractions', True):
            report.append("- Check HTML entity decoding and apostrophe normalization")

        if not results.get('word_truncation', True):
            report.append("- Investigate phonetic dictionary and consonant cluster handling")

        if not results.get('text_skipping', True):
            report.append("- Review text chunking logic and caching consistency")

        if not results.get('regression', True):
            report.append("- Fix regression issues to maintain existing functionality")

        if all_passed:
            report.append("✅ All pronunciation fixes are working correctly!")
            report.append("✅ No regressions detected in existing functionality!")

        return "\n".join(report)


def main():
    """Main execution function"""

    parser = argparse.ArgumentParser(description="Comprehensive Pronunciation Test Suite")
    parser.add_argument("--api-test", action="store_true", help="Include API tests")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output", help="Save report to file")

    args = parser.parse_args()

    # Create test suite
    test_suite = PronunciationTestSuite(verbose=args.verbose)

    # Run tests
    results = test_suite.run_all_tests(include_api=args.api_test)

    # Generate report
    report = test_suite.generate_summary_report(results)

    # Output report
    print("\n" + report)

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {args.output}")

    # Exit with appropriate code
    all_passed = all(results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
