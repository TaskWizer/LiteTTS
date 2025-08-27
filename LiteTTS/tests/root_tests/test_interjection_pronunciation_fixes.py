#!/usr/bin/env python3
"""
Test suite for interjection pronunciation fixes
Validates fixes for Hmm→hum, and other interjection pronunciation issues
"""

import unittest
from LiteTTS.nlp.interjection_fix_processor import InterjectionFixProcessor
from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingMode

class TestInterjectionPronunciationFixes(unittest.TestCase):
    """Test interjection pronunciation fixes"""
    
    def setUp(self):
        self.processor = InterjectionFixProcessor()
        self.unified_processor = UnifiedTextProcessor()
    
    def test_critical_hmm_pronunciation_fix(self):
        """Test the critical Hmm→hum pronunciation issue identified by user"""
        test_cases = [
            # Critical issue from user feedback
            ("Hmm", "Hmmm", "Hmm should expand to 'Hmmm', not sound like 'hum'"),
            ("hmm", "hmmm", "hmm should expand to 'hmmm'"),
            ("Hm", "Hm", "Hm should be preserved (too short to expand reliably)"),
            ("hm", "hm", "hm should be preserved (too short to expand reliably)"),

            # Context variations
            ("Hmm, that's interesting", "Hmmm, that's interesting", "Hmm in sentence context"),
            ("I think, hmm, maybe", "I think, hmmm, maybe", "hmm in middle of sentence"),
            ("Hmm?", "Hmmm?", "Hmm with question mark"),
            ("Hmm!", "Hmmm!", "Hmm with exclamation"),
        ]
        
        print("\n🔧 Testing Critical Hmm Pronunciation Fixes")
        print("=" * 50)
        
        success_count = 0
        for input_text, expected_output, description in test_cases:
            result = self.processor.fix_interjection_pronunciation(input_text)
            
            if result.strip() == expected_output.strip():
                print(f"✅ PASS: '{input_text}' → '{result}'")
                success_count += 1
            else:
                print(f"❌ FAIL: '{input_text}' → '{result}' (expected: '{expected_output}')")
                print(f"   Issue: {description}")
        
        success_rate = success_count / len(test_cases)
        print(f"\nHmm Fixes Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        # Require 100% success for critical fixes
        self.assertEqual(success_count, len(test_cases), 
                        f"Hmm pronunciation fixes must have 100% success rate, got {success_rate:.1%}")
    
    def test_nasal_sound_fixes(self):
        """Test nasal sound pronunciation fixes"""
        test_cases = [
            ("mm", "Mmmm"),  # Capitalized at start
            ("Mm", "Mmmm"),  # Already capitalized
            ("mmm", "mmm"),  # Already long enough
            ("Mmm", "Mmm"),  # Already long enough and capitalized
            ("mm-hmm", "mm-hmm"),  # Should stay as-is
            ("Mm-hmm", "Mm-hmm"),  # Should preserve case
        ]
        
        print("\n🔧 Testing Nasal Sound Fixes")
        print("=" * 35)
        
        success_count = 0
        for input_text, expected_output in test_cases:
            result = self.processor.fix_interjection_pronunciation(input_text)
            
            if result.strip() == expected_output.strip():
                print(f"✅ '{input_text}' → '{result}'")
                success_count += 1
            else:
                print(f"❌ '{input_text}' → '{result}' (expected '{expected_output}')")
        
        success_rate = success_count / len(test_cases)
        print(f"\nNasal Sound Fixes Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        self.assertGreaterEqual(success_rate, 0.9, 
                               f"Nasal sound fixes success rate {success_rate:.1%} below 90%")
    
    def test_hesitation_sound_fixes(self):
        """Test hesitation sound pronunciation fixes"""
        test_cases = [
            ("uh", "uhh"),
            ("Uh", "uhh"),
            ("um", "umm"),
            ("Um", "umm"),
            ("er", "err"),
            ("Er", "err"),
            ("ah", "ahh"),
            ("Ah", "ahh"),
            ("oh", "ohh"),
            ("Oh", "ohh"),
        ]
        
        print("\n🔧 Testing Hesitation Sound Fixes")
        print("=" * 40)
        
        success_count = 0
        for input_text, expected_output in test_cases:
            result = self.processor.fix_interjection_pronunciation(input_text)
            
            if result.strip() == expected_output.strip():
                print(f"✅ '{input_text}' → '{result}'")
                success_count += 1
            else:
                print(f"❌ '{input_text}' → '{result}' (expected '{expected_output}')")
        
        success_rate = success_count / len(test_cases)
        print(f"\nHesitation Sound Fixes Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        self.assertGreaterEqual(success_rate, 0.9, 
                               f"Hesitation sound fixes success rate {success_rate:.1%} below 90%")
    
    def test_laughter_sound_fixes(self):
        """Test laughter sound pronunciation fixes"""
        test_cases = [
            ("haha", "ha ha"),
            ("Haha", "ha ha"),
            ("hehe", "he he"),
            ("Hehe", "he he"),
            ("hihi", "hi hi"),
            ("Hihi", "hi hi"),
        ]
        
        print("\n🔧 Testing Laughter Sound Fixes")
        print("=" * 35)
        
        success_count = 0
        for input_text, expected_output in test_cases:
            result = self.processor.fix_interjection_pronunciation(input_text)
            
            if result.strip() == expected_output.strip():
                print(f"✅ '{input_text}' → '{result}'")
                success_count += 1
            else:
                print(f"❌ '{input_text}' → '{result}' (expected '{expected_output}')")
        
        success_rate = success_count / len(test_cases)
        print(f"\nLaughter Sound Fixes Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        self.assertGreaterEqual(success_rate, 0.8, 
                               f"Laughter sound fixes success rate {success_rate:.1%} below 80%")
    
    def test_context_preservation(self):
        """Test that context around interjections is preserved"""
        test_cases = [
            ("Well, hmm, I think so", "Well, hmmm, I think so"),
            ("The answer is, uh, complicated", "The answer is, uhh, complicated"),
            ("She said 'hmm' thoughtfully", "She said 'hmm' thoughtfully"),  # In quotes, should preserve
            ("Hmm... let me see", "Hmmm... let me see"),  # Sentence start, capitalize
            ("Um, actually, never mind", "umm, actually, never mind"),
        ]
        
        print("\n🔧 Testing Context Preservation")
        print("=" * 35)
        
        success_count = 0
        for input_text, expected_output in test_cases:
            result = self.processor.fix_interjection_pronunciation(input_text)
            
            if result.strip() == expected_output.strip():
                print(f"✅ '{input_text}' → '{result}'")
                success_count += 1
            else:
                print(f"❌ '{input_text}' → '{result}' (expected '{expected_output}')")
        
        success_rate = success_count / len(test_cases)
        print(f"\nContext Preservation Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        self.assertGreaterEqual(success_rate, 0.9, 
                               f"Context preservation success rate {success_rate:.1%} below 90%")
    
    def test_unified_processor_integration(self):
        """Test integration with unified text processor"""
        test_cases = [
            "Hmm, that's interesting",
            "uh, I think so",
            "mm, okay then",
            "ah, yes indeed",
            "oh, really now"
        ]
        
        print("\n🔧 Testing Unified Processor Integration")
        print("=" * 45)
        
        success_count = 0
        for text in test_cases:
            try:
                # Process with premium mode (includes interjection fixes)
                options = self.unified_processor.create_processing_options(ProcessingMode.PREMIUM)
                result = self.unified_processor.process_text(text, options)
                
                # Check that processing completed successfully
                assert result.processed_text is not None
                assert "interjection_fixes" in result.stages_completed
                
                success_count += 1
                print(f"✅ '{text}' -> Interjection processing completed")
                
            except Exception as e:
                print(f"❌ '{text}' -> Error: {e}")
        
        success_rate = success_count / len(test_cases)
        print(f"\nUnified Integration Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        self.assertGreaterEqual(success_rate, 0.9, 
                               f"Unified integration success rate {success_rate:.1%} below 90%")
    
    def test_performance(self):
        """Test interjection processing performance"""
        test_text = "Hmm, uh, well, I think, um, maybe we should, ah, consider this carefully."
        
        # Warm up
        self.processor.fix_interjection_pronunciation(test_text)
        
        # Time multiple runs
        import time
        times = []
        for _ in range(10):
            start_time = time.perf_counter()
            result = self.processor.fix_interjection_pronunciation(test_text)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\n🔧 Testing Performance")
        print("=" * 25)
        print(f"Average processing time: {avg_time:.3f}s")
        print(f"Maximum processing time: {max_time:.3f}s")
        print(f"Test text: {test_text}")
        print(f"Result: {result}")
        
        assert avg_time < 0.01, f"Average processing time {avg_time:.3f}s exceeds 0.01s threshold"
        assert max_time < 0.02, f"Maximum processing time {max_time:.3f}s exceeds 0.02s threshold"
    
    def test_analysis_functionality(self):
        """Test interjection analysis functionality"""
        test_text = "Hmm, uh, well, I think, mm, maybe we should consider this."
        
        analysis = self.processor.analyze_interjection_issues(test_text)
        
        print("\n🔧 Testing Analysis Functionality")
        print("=" * 40)
        print(f"Text: {test_text}")
        print(f"Short interjections: {analysis['short_interjections']}")
        print(f"Nasal sounds: {analysis['nasal_sounds']}")
        print(f"Hesitation markers: {analysis['hesitation_markers']}")
        print(f"Potential fixes: {analysis['potential_fixes']}")
        
        # Should find interjections
        self.assertGreater(len(analysis['short_interjections']), 0,
                          "Should find short interjections")
        self.assertGreater(len(analysis['nasal_sounds']), 0,
                          "Should find nasal sounds")
        self.assertGreater(len(analysis['hesitation_markers']), 0,
                          "Should find hesitation markers")
        
        print("✅ Analysis functionality working correctly")

def run_comprehensive_interjection_tests():
    """Run all interjection tests and provide summary"""
    print("🔧" * 30)
    print("INTERJECTION PRONUNCIATION PROCESSOR - COMPREHENSIVE TEST SUITE")
    print("🔧" * 30)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInterjectionPronunciationFixes)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=open('/dev/null', 'w'))
    result = runner.run(suite)
    
    # Calculate success rate
    total_tests = result.testsRun
    failed_tests = len(result.failures) + len(result.errors)
    passed_tests = total_tests - failed_tests
    success_rate = passed_tests / total_tests if total_tests > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"INTERJECTION FIXES TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Run: {total_tests}")
    print(f"Tests Passed: {passed_tests}")
    print(f"Tests Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1%}")
    
    if success_rate >= 0.95:
        print("🎉 EXCELLENT: Interjection pronunciation fixes are working excellently!")
    elif success_rate >= 0.9:
        print("✅ GOOD: Interjection pronunciation fixes are working well!")
    elif success_rate >= 0.8:
        print("⚠️  ACCEPTABLE: Interjection pronunciation fixes need some improvements.")
    else:
        print("❌ NEEDS WORK: Interjection pronunciation fixes require significant improvements.")
    
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return success_rate

if __name__ == "__main__":
    # Run individual test instance for detailed output
    test_instance = TestInterjectionPronunciationFixes()
    test_instance.setUp()
    
    try:
        test_instance.test_critical_hmm_pronunciation_fix()
        test_instance.test_nasal_sound_fixes()
        test_instance.test_hesitation_sound_fixes()
        test_instance.test_laughter_sound_fixes()
        test_instance.test_context_preservation()
        test_instance.test_unified_processor_integration()
        test_instance.test_performance()
        test_instance.test_analysis_functionality()
        
        print("\n🎉 All individual tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    
    # Run comprehensive test suite
    run_comprehensive_interjection_tests()
