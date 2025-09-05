#!/usr/bin/env python3
"""
CRITICAL TIME PROCESSING VALIDATION SCRIPT
Comprehensive testing of time format processing to identify and fix regressions
"""

import sys
import os
import logging
from typing import Dict, List, Tuple, Any

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import all relevant processors
try:
    from LiteTTS.nlp.enhanced_datetime_processor import EnhancedDateTimeProcessor
    from LiteTTS.nlp.text_normalizer import TextNormalizer
    PROCESSORS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import processors: {e}")
    PROCESSORS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TimeProcessingValidator:
    """Comprehensive time processing validation and testing"""

    def __init__(self):
        if not PROCESSORS_AVAILABLE:
            print("Processors not available, creating minimal validator")
            self.enhanced_datetime = None
            self.text_normalizer = None
            return

        self.enhanced_datetime = EnhancedDateTimeProcessor()
        self.text_normalizer = TextNormalizer()
        
        # Test cases from the requirements
        self.critical_test_cases = [
            # CONFIRMED FAILING CASES
            ("10:45 a.m.", "ten forty-five a m"),
            ("3:30 p.m.", "three thirty p m"),
            
            # Digital times
            ("10:45", "ten forty-five"),
            ("3:30", "three thirty"),
            ("12:00", "twelve o'clock"),
            ("6:15", "six fifteen"),
            ("9:05", "nine oh five"),
            
            # AM/PM variations
            ("10:45 AM", "ten forty-five a m"),
            ("3:30 PM", "three thirty p m"),
            ("12:00 AM", "twelve o'clock a m"),
            ("6:15 PM", "six fifteen p m"),
            ("10:45 a.m.", "ten forty-five a m"),
            ("3:30 p.m.", "three thirty p m"),
            ("12:00 a.m.", "twelve o'clock a m"),
            ("6:15 p.m.", "six fifteen p m"),
            
            # Natural expressions
            ("quarter past three", "quarter past three"),
            ("half past two", "half past two"),
            ("quarter till eleven", "quarter till eleven"),
            
            # 24-hour format
            ("14:30", "two thirty p m"),
            ("22:45", "ten forty-five p m"),
            ("08:15", "eight fifteen a m"),
            ("00:30", "twelve thirty a m"),
            
            # Edge cases
            ("12:00 noon", "twelve o'clock noon"),
            ("12:00 midnight", "twelve o'clock midnight"),
            ("11:59 p.m.", "eleven fifty-nine p m"),
        ]
        
        self.results = {}
        
    def test_individual_processors(self) -> Dict[str, Any]:
        """Test each processor individually to identify the source of corruption"""
        results = {
            'enhanced_datetime': {},
            'text_normalizer': {},
            'phase6_processor': {},
            'unified_processor': {}
        }
        
        print("\n" + "="*80)
        print("INDIVIDUAL PROCESSOR TESTING")
        print("="*80)
        
        for input_text, expected in self.critical_test_cases:
            print(f"\n🔍 Testing: '{input_text}' → Expected: '{expected}'")
            
            # Test Enhanced DateTime Processor
            try:
                enhanced_result = self.enhanced_datetime.process_dates_and_times(input_text)
                results['enhanced_datetime'][input_text] = enhanced_result
                print(f"   Enhanced DateTime: '{enhanced_result}'")
                if "meters" in enhanced_result.lower():
                    print(f"   ❌ CORRUPTION DETECTED: 'meters' found in output!")
            except Exception as e:
                results['enhanced_datetime'][input_text] = f"ERROR: {e}"
                print(f"   Enhanced DateTime: ERROR - {e}")
            
            # Test Text Normalizer
            try:
                normalizer_result = self.text_normalizer.normalize_text(input_text)
                results['text_normalizer'][input_text] = normalizer_result
                print(f"   Text Normalizer: '{normalizer_result}'")
                if "meters" in normalizer_result.lower():
                    print(f"   ❌ CORRUPTION DETECTED: 'meters' found in output!")
            except Exception as e:
                results['text_normalizer'][input_text] = f"ERROR: {e}"
                print(f"   Text Normalizer: ERROR - {e}")
            
            # Test Phase6 Processor
            try:
                phase6_result = self.phase6_processor.process_text(input_text, mode=Phase6ProcessingMode.COMPREHENSIVE)
                results['phase6_processor'][input_text] = phase6_result.processed_text
                print(f"   Phase6 Processor: '{phase6_result.processed_text}'")
                if "meters" in phase6_result.processed_text.lower():
                    print(f"   ❌ CORRUPTION DETECTED: 'meters' found in output!")
            except Exception as e:
                results['phase6_processor'][input_text] = f"ERROR: {e}"
                print(f"   Phase6 Processor: ERROR - {e}")
            
            # Test Unified Processor
            try:
                options = ProcessingOptions(use_enhanced_datetime=True)
                unified_result = self.unified_processor.process_text(input_text, options)
                results['unified_processor'][input_text] = unified_result.processed_text
                print(f"   Unified Processor: '{unified_result.processed_text}'")
                if "meters" in unified_result.processed_text.lower():
                    print(f"   ❌ CORRUPTION DETECTED: 'meters' found in output!")
            except Exception as e:
                results['unified_processor'][input_text] = f"ERROR: {e}"
                print(f"   Unified Processor: ERROR - {e}")
        
        return results
    
    def analyze_corruption_patterns(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the results to identify corruption patterns"""
        analysis = {
            'corrupted_processors': [],
            'corruption_patterns': [],
            'clean_processors': []
        }
        
        print("\n" + "="*80)
        print("CORRUPTION PATTERN ANALYSIS")
        print("="*80)
        
        for processor_name, processor_results in results.items():
            corrupted_count = 0
            total_count = len(processor_results)
            
            for input_text, output in processor_results.items():
                if isinstance(output, str) and "meters" in output.lower():
                    corrupted_count += 1
                    analysis['corruption_patterns'].append({
                        'processor': processor_name,
                        'input': input_text,
                        'output': output,
                        'corruption_type': 'meters_substitution'
                    })
            
            corruption_rate = (corrupted_count / total_count) * 100 if total_count > 0 else 0
            
            if corrupted_count > 0:
                analysis['corrupted_processors'].append({
                    'name': processor_name,
                    'corruption_rate': corruption_rate,
                    'corrupted_cases': corrupted_count,
                    'total_cases': total_count
                })
                print(f"❌ {processor_name}: {corrupted_count}/{total_count} cases corrupted ({corruption_rate:.1f}%)")
            else:
                analysis['clean_processors'].append(processor_name)
                print(f"✅ {processor_name}: Clean (0/{total_count} corrupted)")
        
        return analysis
    
    def test_am_pm_processing(self) -> Dict[str, Any]:
        """Specifically test AM/PM processing to identify the exact issue"""
        print("\n" + "="*80)
        print("AM/PM PROCESSING DEEP DIVE")
        print("="*80)
        
        am_pm_tests = [
            "a.m.", "p.m.", "AM", "PM", "am", "pm",
            "10:45 a.m.", "3:30 p.m.", "12:00 AM", "6:15 PM"
        ]
        
        results = {}
        
        for test_input in am_pm_tests:
            print(f"\n🔍 Testing AM/PM processing: '{test_input}'")
            
            # Test each processor's handling of AM/PM
            enhanced_result = self.enhanced_datetime.process_dates_and_times(test_input)
            normalizer_result = self.text_normalizer.normalize_text(test_input)
            
            results[test_input] = {
                'enhanced_datetime': enhanced_result,
                'text_normalizer': normalizer_result
            }
            
            print(f"   Enhanced DateTime: '{enhanced_result}'")
            print(f"   Text Normalizer: '{normalizer_result}'")
            
            # Check for specific corruption patterns
            if "meters" in enhanced_result.lower():
                print(f"   ❌ Enhanced DateTime corrupted: 'meters' found!")
            if "meters" in normalizer_result.lower():
                print(f"   ❌ Text Normalizer corrupted: 'meters' found!")
        
        return results
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run the complete validation suite"""
        print("🚀 STARTING COMPREHENSIVE TIME PROCESSING VALIDATION")
        print("="*80)
        
        # Test individual processors
        individual_results = self.test_individual_processors()
        
        # Analyze corruption patterns
        corruption_analysis = self.analyze_corruption_patterns(individual_results)
        
        # Deep dive into AM/PM processing
        am_pm_results = self.test_am_pm_processing()
        
        # Compile final report
        final_report = {
            'individual_results': individual_results,
            'corruption_analysis': corruption_analysis,
            'am_pm_results': am_pm_results,
            'summary': self._generate_summary(corruption_analysis)
        }
        
        self._print_final_report(final_report)
        
        return final_report
    
    def _generate_summary(self, corruption_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of findings"""
        return {
            'total_corrupted_processors': len(corruption_analysis['corrupted_processors']),
            'total_clean_processors': len(corruption_analysis['clean_processors']),
            'total_corruption_patterns': len(corruption_analysis['corruption_patterns']),
            'most_corrupted_processor': max(corruption_analysis['corrupted_processors'], 
                                          key=lambda x: x['corruption_rate'])['name'] if corruption_analysis['corrupted_processors'] else None
        }
    
    def _print_final_report(self, report: Dict[str, Any]) -> None:
        """Print the final validation report"""
        print("\n" + "="*80)
        print("FINAL VALIDATION REPORT")
        print("="*80)
        
        summary = report['summary']
        print(f"📊 Total Processors Tested: {summary['total_corrupted_processors'] + summary['total_clean_processors']}")
        print(f"❌ Corrupted Processors: {summary['total_corrupted_processors']}")
        print(f"✅ Clean Processors: {summary['total_clean_processors']}")
        print(f"🔍 Total Corruption Patterns: {summary['total_corruption_patterns']}")
        
        if summary['most_corrupted_processor']:
            print(f"🎯 Most Corrupted Processor: {summary['most_corrupted_processor']}")
        
        print("\n📋 CORRUPTION PATTERNS FOUND:")
        for pattern in report['corruption_analysis']['corruption_patterns']:
            print(f"   {pattern['processor']}: '{pattern['input']}' → '{pattern['output']}'")
        
        print("\n🔧 RECOMMENDED ACTIONS:")
        if summary['total_corrupted_processors'] > 0:
            print("   1. Fix the processors showing 'meters' corruption")
            print("   2. Ensure AM/PM is processed as 'a m' and 'p m' (with spaces)")
            print("   3. Test all time formats after fixes")
            print("   4. Validate with audio generation and Whisper transcription")
        else:
            print("   ✅ No corruption detected - system appears to be working correctly")

if __name__ == "__main__":
    validator = TimeProcessingValidator()
    results = validator.run_comprehensive_validation()
