#!/usr/bin/env python3
"""
Comprehensive Pronunciation Test Suite
Extensive test suite covering all identified pronunciation issues with before/after validation
"""

import sys
import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.nlp.text_normalizer import TextNormalizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PronunciationTestCase:
    """Individual pronunciation test case"""
    category: str
    input_text: str
    expected_output: str
    description: str
    priority: str = "medium"  # low, medium, high, critical
    
@dataclass
class PronunciationTestResult:
    """Result of a pronunciation test"""
    test_case: PronunciationTestCase
    actual_output: str
    passed: bool
    error_message: str = ""

class ComprehensivePronunciationTestSuite:
    """Comprehensive test suite for all pronunciation improvements"""
    
    def __init__(self):
        self.text_normalizer = TextNormalizer()
        self.test_cases = self._load_test_cases()
        self.results = []
        
        logger.info(f"Pronunciation test suite initialized with {len(self.test_cases)} test cases")
    
    def _load_test_cases(self) -> List[PronunciationTestCase]:
        """Load comprehensive pronunciation test cases"""
        test_cases = []
        
        # Contraction handling tests
        contraction_tests = [
            ("I'll", "eye will", "Problematic contraction I'll"),
            ("you'll", "you will", "Problematic contraction you'll"),
            ("I'd", "eye would", "Problematic contraction I'd"),
            ("I'm", "eye am", "Contraction I'm"),
            ("that's", "thats", "Natural contraction that's"),
            ("don't", "dont", "Natural contraction don't"),
            ("won't", "wont", "Natural contraction won't"),
            ("can't", "cant", "Natural contraction can't"),
            ("wasn't", "wuznt", "Contraction wasn't"),
            ("we're", "weer", "Contraction we're"),
            ("they're", "thair", "Contraction they're"),
        ]
        
        for input_text, expected, description in contraction_tests:
            test_cases.append(PronunciationTestCase(
                category="contractions",
                input_text=input_text,
                expected_output=expected,
                description=description,
                priority="high"
            ))
        
        # Symbol processing tests
        symbol_tests = [
            ("&", "and", "Ampersand symbol"),
            ("@", "at", "At symbol"),
            ("*", "asterisk", "Asterisk symbol"),
            ("e.g.", "for example", "Abbreviation e.g."),
            ("i.e.", "that is", "Abbreviation i.e."),
            ("etc.", "etcetera", "Abbreviation etc."),
            ("vs.", "versus", "Abbreviation vs."),
            ("Mr.", "Mister", "Title Mr."),
            ("Dr.", "Doctor", "Title Dr."),
            ("Inc.", "Incorporated", "Business Inc."),
        ]
        
        for input_text, expected, description in symbol_tests:
            test_cases.append(PronunciationTestCase(
                category="symbols",
                input_text=input_text,
                expected_output=expected,
                description=description,
                priority="medium"
            ))
        
        # Currency processing tests
        currency_tests = [
            ("$123.45", "one hundred twenty-three dollars and forty-five cents", "Currency with cents"),
            ("$1,000", "one thousand dollars", "Currency with thousands"),
            ("$5", "five dollars", "Simple currency"),
            ("€50", "fifty euros", "Euro currency"),
            ("£25.99", "twenty-five pounds and ninety-nine pence", "British pounds"),
            ("¥100", "one hundred yen", "Japanese yen"),
        ]
        
        for input_text, expected, description in currency_tests:
            test_cases.append(PronunciationTestCase(
                category="currency",
                input_text=input_text,
                expected_output=expected,
                description=description,
                priority="medium"
            ))
        
        # Date and time processing tests
        datetime_tests = [
            ("2023-10-27", "October twenty-seventh, twenty twenty-three", "ISO date format"),
            ("10/27/2023", "October twenty-seventh, twenty twenty-three", "US date format"),
            ("27/10/2023", "twenty-seventh of October, twenty twenty-three", "European date format"),
            ("3:30 PM", "three thirty PM", "Time with PM"),
            ("15:45", "fifteen forty-five", "24-hour time"),
            ("Dec 15th", "December fifteenth", "Month abbreviation with ordinal"),
        ]
        
        for input_text, expected, description in datetime_tests:
            test_cases.append(PronunciationTestCase(
                category="datetime",
                input_text=input_text,
                expected_output=expected,
                description=description,
                priority="medium"
            ))
        
        # URL and email processing tests
        url_tests = [
            ("https://www.google.com", "google dot com", "HTTPS URL"),
            ("http://example.org", "example dot org", "HTTP URL"),
            ("test@example.com", "test at example dot com", "Email address"),
            ("www.github.com", "github dot com", "WWW URL"),
            ("ftp://files.example.net", "files dot example dot net", "FTP URL"),
        ]
        
        for input_text, expected, description in url_tests:
            test_cases.append(PronunciationTestCase(
                category="urls",
                input_text=input_text,
                expected_output=expected,
                description=description,
                priority="low"
            ))
        
        # Number processing tests
        number_tests = [
            ("123", "one hundred twenty-three", "Three-digit number"),
            ("1,000,000", "one million", "Large number with commas"),
            ("3.14159", "three point one four one five nine", "Decimal number"),
            ("50%", "fifty percent", "Percentage"),
            ("1st", "first", "Ordinal number"),
            ("2nd", "second", "Ordinal number"),
            ("3rd", "third", "Ordinal number"),
            ("21st", "twenty-first", "Complex ordinal"),
        ]
        
        for input_text, expected, description in number_tests:
            test_cases.append(PronunciationTestCase(
                category="numbers",
                input_text=input_text,
                expected_output=expected,
                description=description,
                priority="medium"
            ))
        
        # Specific pronunciation fixes
        pronunciation_tests = [
            ("asterisk", "asterisk", "Word asterisk pronunciation"),
            ("hedonism", "hedonism", "Word hedonism pronunciation"),
            ("inherently", "inherently", "Word inherently pronunciation"),
            ("resume", "resume", "Word resume (not re-zoom)"),
            ("ASAP", "A S A P", "Acronym ASAP"),
            ("NASA", "NASA", "Acronym NASA"),
            ("FAQ", "F A Q", "Acronym FAQ"),
            ("CEO", "C E O", "Acronym CEO"),
        ]
        
        for input_text, expected, description in pronunciation_tests:
            test_cases.append(PronunciationTestCase(
                category="pronunciation_fixes",
                input_text=input_text,
                expected_output=expected,
                description=description,
                priority="high"
            ))
        
        # Interjection and filler word tests
        interjection_tests = [
            ("hmm", "hum", "Interjection hmm"),
            ("uh", "uh", "Filler word uh"),
            ("um", "um", "Filler word um"),
            ("ah", "ah", "Interjection ah"),
            ("oh", "oh", "Interjection oh"),
            ("wow", "wow", "Exclamation wow"),
        ]
        
        for input_text, expected, description in interjection_tests:
            test_cases.append(PronunciationTestCase(
                category="interjections",
                input_text=input_text,
                expected_output=expected,
                description=description,
                priority="low"
            ))
        
        # Complex sentence tests
        complex_tests = [
            (
                "I'll visit https://www.example.com at 3:30 PM on 2023-10-27 & pay $123.45.",
                "eye will visit example dot com at three thirty PM on October twenty-seventh, twenty twenty-three and pay one hundred twenty-three dollars and forty-five cents.",
                "Complex sentence with multiple elements"
            ),
            (
                "The CEO said 'ASAP' but I think it's 50% likely by Dec 15th.",
                "The C E O said A S A P but I think its fifty percent likely by December fifteenth.",
                "Complex sentence with quotes and mixed elements"
            ),
            (
                "Contact support@company.com or call (555) 123-4567 for help.",
                "Contact support at company dot com or call five five five one two three four five six seven for help.",
                "Contact information processing"
            ),
        ]
        
        for input_text, expected, description in complex_tests:
            test_cases.append(PronunciationTestCase(
                category="complex_sentences",
                input_text=input_text,
                expected_output=expected,
                description=description,
                priority="critical"
            ))
        
        return test_cases
    
    def run_single_test(self, test_case: PronunciationTestCase) -> PronunciationTestResult:
        """Run a single pronunciation test"""
        try:
            # Process the input text through the normalizer
            actual_output = self.text_normalizer.normalize_text(test_case.input_text)
            
            # Check if the output matches expected (case-insensitive, whitespace normalized)
            expected_normalized = ' '.join(test_case.expected_output.lower().split())
            actual_normalized = ' '.join(actual_output.lower().split())
            
            passed = expected_normalized == actual_normalized
            
            return PronunciationTestResult(
                test_case=test_case,
                actual_output=actual_output,
                passed=passed,
                error_message="" if passed else f"Expected: '{test_case.expected_output}', Got: '{actual_output}'"
            )
            
        except Exception as e:
            return PronunciationTestResult(
                test_case=test_case,
                actual_output="",
                passed=False,
                error_message=f"Exception: {str(e)}"
            )
    
    def run_category_tests(self, category: str) -> List[PronunciationTestResult]:
        """Run all tests for a specific category"""
        category_tests = [tc for tc in self.test_cases if tc.category == category]
        results = []
        
        logger.info(f"Running {len(category_tests)} tests for category: {category}")
        
        for test_case in category_tests:
            result = self.run_single_test(test_case)
            results.append(result)
            
            if result.passed:
                logger.debug(f"✅ {test_case.description}: PASSED")
            else:
                logger.warning(f"❌ {test_case.description}: FAILED - {result.error_message}")
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all pronunciation tests"""
        logger.info("Running comprehensive pronunciation test suite")
        
        # Get all categories
        categories = list(set(tc.category for tc in self.test_cases))
        categories.sort()
        
        all_results = {}
        total_passed = 0
        total_tests = 0
        
        # Run tests by category
        for category in categories:
            category_results = self.run_category_tests(category)
            all_results[category] = category_results
            
            category_passed = sum(1 for r in category_results if r.passed)
            category_total = len(category_results)
            
            total_passed += category_passed
            total_tests += category_total
            
            logger.info(f"Category '{category}': {category_passed}/{category_total} passed "
                       f"({(category_passed/category_total*100):.1f}%)")
        
        # Calculate overall statistics
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_tests - total_passed,
            "success_rate": success_rate,
            "categories": {
                cat: {
                    "passed": sum(1 for r in results if r.passed),
                    "total": len(results),
                    "success_rate": (sum(1 for r in results if r.passed) / len(results) * 100) if results else 0
                }
                for cat, results in all_results.items()
            }
        }
        
        # Store results for detailed analysis
        self.results = all_results
        
        return {
            "summary": summary,
            "detailed_results": all_results
        }
    
    def generate_detailed_report(self, output_file: str = "pronunciation_test_report.json"):
        """Generate detailed test report"""
        if not self.results:
            logger.warning("No test results available. Run tests first.")
            return
        
        # Prepare serializable results
        serializable_results = {}
        
        for category, results in self.results.items():
            serializable_results[category] = []
            
            for result in results:
                serializable_results[category].append({
                    "test_case": asdict(result.test_case),
                    "actual_output": result.actual_output,
                    "passed": result.passed,
                    "error_message": result.error_message
                })
        
        # Calculate priority-based statistics
        priority_stats = {}
        for priority in ["critical", "high", "medium", "low"]:
            priority_tests = [
                result for results in self.results.values() 
                for result in results 
                if result.test_case.priority == priority
            ]
            
            if priority_tests:
                priority_passed = sum(1 for r in priority_tests if r.passed)
                priority_stats[priority] = {
                    "total": len(priority_tests),
                    "passed": priority_passed,
                    "success_rate": (priority_passed / len(priority_tests) * 100)
                }
        
        report_data = {
            "test_summary": {
                "total_categories": len(self.results),
                "total_tests": sum(len(results) for results in self.results.values()),
                "overall_success_rate": self._calculate_overall_success_rate(),
                "priority_breakdown": priority_stats
            },
            "category_results": serializable_results,
            "failed_tests": self._get_failed_tests_summary(),
            "recommendations": self._generate_recommendations()
        }
        
        # Save report
        try:
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            logger.info(f"Detailed report saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        return report_data
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate"""
        total_tests = sum(len(results) for results in self.results.values())
        total_passed = sum(sum(1 for r in results if r.passed) for results in self.results.values())
        
        return (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    def _get_failed_tests_summary(self) -> List[Dict[str, str]]:
        """Get summary of failed tests"""
        failed_tests = []
        
        for category, results in self.results.items():
            for result in results:
                if not result.passed:
                    failed_tests.append({
                        "category": category,
                        "description": result.test_case.description,
                        "input": result.test_case.input_text,
                        "expected": result.test_case.expected_output,
                        "actual": result.actual_output,
                        "priority": result.test_case.priority,
                        "error": result.error_message
                    })
        
        # Sort by priority (critical first)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        failed_tests.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return failed_tests
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check success rate by category
        for category, results in self.results.items():
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            success_rate = (passed / total * 100) if total > 0 else 0
            
            if success_rate < 80:
                recommendations.append(f"Category '{category}' has low success rate ({success_rate:.1f}%) - needs attention")
            elif success_rate < 95:
                recommendations.append(f"Category '{category}' has moderate success rate ({success_rate:.1f}%) - consider improvements")
        
        # Check critical priority tests
        critical_tests = [
            result for results in self.results.values() 
            for result in results 
            if result.test_case.priority == "critical"
        ]
        
        critical_failed = [r for r in critical_tests if not r.passed]
        if critical_failed:
            recommendations.append(f"{len(critical_failed)} critical tests failed - immediate attention required")
        
        # Overall recommendations
        overall_success = self._calculate_overall_success_rate()
        if overall_success < 90:
            recommendations.append("Overall success rate below 90% - comprehensive review needed")
        elif overall_success >= 95:
            recommendations.append("Excellent pronunciation accuracy - system ready for production")
        
        return recommendations

def main():
    """Main test execution"""
    print("Comprehensive Pronunciation Test Suite")
    print("=" * 50)
    
    try:
        test_suite = ComprehensivePronunciationTestSuite()
        results = test_suite.run_all_tests()
        
        # Print summary
        summary = results["summary"]
        print(f"\n📊 Test Results Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['total_passed']}")
        print(f"   Failed: {summary['total_failed']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        
        print(f"\n📋 Category Breakdown:")
        for category, stats in summary["categories"].items():
            print(f"   {category}: {stats['passed']}/{stats['total']} ({stats['success_rate']:.1f}%)")
        
        # Generate detailed report
        report = test_suite.generate_detailed_report()
        
        # Print recommendations
        if report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   - {rec}")
        
        # Print failed tests summary
        failed_tests = report["failed_tests"]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests[:10]:  # Show first 10 failed tests
                print(f"   {test['priority'].upper()}: {test['description']}")
                print(f"      Input: '{test['input']}'")
                print(f"      Expected: '{test['expected']}'")
                print(f"      Actual: '{test['actual']}'")
                print()
        
        success = summary['success_rate'] >= 90
        
        if success:
            print("🎉 Pronunciation test suite passed! System ready for production.")
        else:
            print("⚠️  Some pronunciation issues detected. Review failed tests.")
        
        return success
        
    except Exception as e:
        logger.error(f"Test suite execution failed: {e}")
        print(f"\n❌ Test suite failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
