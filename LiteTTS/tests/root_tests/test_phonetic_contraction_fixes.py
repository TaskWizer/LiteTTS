#!/usr/bin/env python3
"""
Test suite for phonetic contraction pronunciation fixes
Validates fixes for wasn't→wAHz-uhnt, I'll→ill, you'll→yaw-wl, etc.
"""

import unittest
from LiteTTS.nlp.phonetic_contraction_processor import PhoneticContractionProcessor

class TestPhoneticContractionFixes(unittest.TestCase):
    """Test phonetic contraction pronunciation fixes"""
    
    def setUp(self):
        self.processor = PhoneticContractionProcessor()
    
    def test_critical_pronunciation_fixes(self):
        """Test the most critical pronunciation issues identified by user"""
        test_cases = [
            # Critical issues from user feedback
            ("I wasn't ready", "I was not ready", "wasn't should expand to 'was not', not 'wAHz-uhnt'"),
            ("I'll be there", "I will be there", "I'll should expand to 'I will', not sound like 'ill'"),
            ("you'll see", "you will see", "you'll should expand to 'you will', not 'yaw-wl'"),
            ("I'd like that", "I would like that", "I'd should expand to 'I would', not 'I-D'"),
            ("I'm here", "I am here", "I'm should expand to 'I am', not sound like 'im'"),
            ("hi, that's great", "hi, that is great", "that's should not become 'hit that'"),
        ]
        
        print("\n🔧 Testing Critical Contraction Pronunciation Fixes")
        print("=" * 60)
        
        success_count = 0
        for input_text, expected_output, description in test_cases:
            result = self.processor.process_contractions(input_text, mode="phonetic_expansion")
            
            if result.strip() == expected_output.strip():
                print(f"✅ PASS: '{input_text}' → '{result}'")
                success_count += 1
            else:
                print(f"❌ FAIL: '{input_text}' → '{result}' (expected: '{expected_output}')")
                print(f"   Issue: {description}")
        
        success_rate = success_count / len(test_cases)
        print(f"\nCritical Fixes Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        # Require 100% success for critical fixes
        self.assertEqual(success_count, len(test_cases), 
                        f"Critical contraction fixes must have 100% success rate, got {success_rate:.1%}")
    
    def test_negative_contractions(self):
        """Test negative contractions (wasn't, weren't, isn't, etc.)"""
        test_cases = [
            ("wasn't", "was not"),
            ("weren't", "were not"), 
            ("isn't", "is not"),
            ("aren't", "are not"),
            ("hasn't", "has not"),
            ("haven't", "have not"),
            ("hadn't", "had not"),
            ("don't", "do not"),
            ("doesn't", "does not"),
            ("didn't", "did not"),
            ("won't", "will not"),
            ("can't", "cannot"),
            ("couldn't", "could not"),
            ("shouldn't", "should not"),
            ("wouldn't", "would not"),
        ]
        
        print("\n🔧 Testing Negative Contractions")
        print("=" * 40)
        
        success_count = 0
        for contraction, expected in test_cases:
            test_text = f"I {contraction} go"
            result = self.processor.process_contractions(test_text, mode="phonetic_expansion")
            expected_result = f"I {expected} go"
            
            if result.strip() == expected_result.strip():
                print(f"✅ '{contraction}' → '{expected}'")
                success_count += 1
            else:
                print(f"❌ '{contraction}' → got '{result}' (expected '{expected_result}')")
        
        success_rate = success_count / len(test_cases)
        print(f"\nNegative Contractions Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        self.assertGreaterEqual(success_rate, 0.9, 
                               f"Negative contractions success rate {success_rate:.1%} below 90%")
    
    def test_will_contractions(self):
        """Test 'll contractions (I'll, you'll, etc.)"""
        test_cases = [
            ("I'll", "I will"),
            ("you'll", "you will"),
            ("he'll", "he will"),
            ("she'll", "she will"),
            ("it'll", "it will"),
            ("we'll", "we will"),
            ("they'll", "they will"),
            ("that'll", "that will"),
        ]
        
        print("\n🔧 Testing 'll Contractions")
        print("=" * 35)
        
        success_count = 0
        for contraction, expected in test_cases:
            test_text = f"{contraction} be fine"
            result = self.processor.process_contractions(test_text, mode="phonetic_expansion")
            expected_result = f"{expected} be fine"
            
            if result.strip() == expected_result.strip():
                print(f"✅ '{contraction}' → '{expected}'")
                success_count += 1
            else:
                print(f"❌ '{contraction}' → got '{result}' (expected '{expected_result}')")
        
        success_rate = success_count / len(test_cases)
        print(f"\n'll Contractions Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        self.assertGreaterEqual(success_rate, 0.9, 
                               f"'ll contractions success rate {success_rate:.1%} below 90%")
    
    def test_would_contractions(self):
        """Test 'd contractions (I'd, you'd, etc.)"""
        test_cases = [
            ("I'd like coffee", "I would like coffee"),
            ("you'd enjoy it", "you would enjoy it"),
            ("he'd prefer tea", "he would prefer tea"),
            ("she'd rather walk", "she would rather walk"),
            ("we'd better go", "we would better go"),
            ("they'd love this", "they would love this"),
        ]
        
        print("\n🔧 Testing 'd Contractions (would context)")
        print("=" * 45)
        
        success_count = 0
        for input_text, expected_output in test_cases:
            result = self.processor.process_contractions(input_text, mode="phonetic_expansion")
            
            if result.strip() == expected_output.strip():
                print(f"✅ '{input_text}' → '{result}'")
                success_count += 1
            else:
                print(f"❌ '{input_text}' → '{result}' (expected '{expected_output}')")
        
        success_rate = success_count / len(test_cases)
        print(f"\n'd Contractions Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        self.assertGreaterEqual(success_rate, 0.9, 
                               f"'d contractions success rate {success_rate:.1%} below 90%")
    
    def test_context_sensitive_contractions(self):
        """Test context-sensitive contractions ('d and 's)"""
        test_cases = [
            # 'd = "had" context
            ("I'd already seen it", "I had already seen it"),
            ("She'd been there before", "She had been there before"),
            ("They'd just finished", "They had just finished"),
            
            # 'd = "would" context (default)
            ("I'd like some coffee", "I would like some coffee"),
            ("He'd prefer to stay", "He would prefer to stay"),
            
            # 's = "has" context
            ("He's already gone", "He has already gone"),
            ("She's been working", "She has been working"),
            ("It's just arrived", "It has just arrived"),
            
            # 's = "is" context (default)
            ("He's tall", "He is tall"),
            ("She's happy", "She is happy"),
            ("It's blue", "It is blue"),
        ]
        
        print("\n🔧 Testing Context-Sensitive Contractions")
        print("=" * 45)
        
        success_count = 0
        for input_text, expected_output in test_cases:
            result = self.processor.process_contractions(input_text, mode="phonetic_expansion")
            
            if result.strip() == expected_output.strip():
                print(f"✅ '{input_text}' → '{result}'")
                success_count += 1
            else:
                print(f"❌ '{input_text}' → '{result}' (expected '{expected_output}')")
        
        success_rate = success_count / len(test_cases)
        print(f"\nContext-Sensitive Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        self.assertGreaterEqual(success_rate, 0.8, 
                               f"Context-sensitive contractions success rate {success_rate:.1%} below 80%")
    
    def test_case_preservation(self):
        """Test that original case is preserved"""
        test_cases = [
            ("I'll go", "I will go"),
            ("I'LL GO", "I WILL GO"),
            ("You'll see", "You will see"),
            ("YOU'LL SEE", "YOU WILL SEE"),
            ("We're here", "We are here"),
            ("WE'RE HERE", "WE ARE HERE"),
        ]
        
        print("\n🔧 Testing Case Preservation")
        print("=" * 35)
        
        success_count = 0
        for input_text, expected_output in test_cases:
            result = self.processor.process_contractions(input_text, mode="phonetic_expansion")
            
            if result == expected_output:
                print(f"✅ '{input_text}' → '{result}'")
                success_count += 1
            else:
                print(f"❌ '{input_text}' → '{result}' (expected '{expected_output}')")
        
        success_rate = success_count / len(test_cases)
        print(f"\nCase Preservation Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        self.assertGreaterEqual(success_rate, 0.9, 
                               f"Case preservation success rate {success_rate:.1%} below 90%")
    
    def test_phonetic_representations(self):
        """Test phonetic representations of contractions"""
        test_cases = [
            ("wasn't", ["wuhz naht", "wuhz"]),  # Should not be "wAHz-uhnt"
            ("I'll", ["aeeh weehl", "eye wihl", "aeeh"]),     # Should not be "ill"
            ("you'll", ["yoo weehl", "yoo"]),   # Should not be "yaw-wl"
            ("I'd", ["aeeh woohd", "eye wuhd", "aeeh"]),      # Should not be "I-D"
            ("I'm", ["aeeh aem", "eye aem", "aeeh"]),       # Should not be "im"
        ]
        
        print("\n🔧 Testing Phonetic Representations")
        print("=" * 40)
        
        success_count = 0
        for contraction, expected_phonetics in test_cases:
            phonetic = self.processor.get_phonetic_representation(contraction)

            # Check if any of the expected phonetic patterns match
            match_found = False
            if phonetic:
                for expected in expected_phonetics:
                    if expected in phonetic.lower():
                        match_found = True
                        break

            if match_found:
                print(f"✅ '{contraction}' → phonetic: {phonetic}")
                success_count += 1
            else:
                print(f"❌ '{contraction}' → phonetic: {phonetic} (expected to contain one of: {expected_phonetics})")
        
        success_rate = success_count / len(test_cases)
        print(f"\nPhonetic Representation Success Rate: {success_rate:.1%} ({success_count}/{len(test_cases)})")
        
        self.assertGreaterEqual(success_rate, 0.8, 
                               f"Phonetic representation success rate {success_rate:.1%} below 80%")
    
    def test_analysis_functionality(self):
        """Test contraction analysis functionality"""
        test_text = "I wasn't sure if you'll be there, but I'd like to know what's happening."
        
        analysis = self.processor.analyze_contractions(test_text)
        
        print("\n🔧 Testing Analysis Functionality")
        print("=" * 40)
        print(f"Text: {test_text}")
        print(f"Contractions found: {analysis['contractions_found']}")
        print(f"Problematic contractions: {analysis['problematic_contractions']}")
        print(f"Context-sensitive contractions: {analysis['context_sensitive_contractions']}")
        
        # Should find all contractions
        expected_contractions = ["wasn't", "you'll", "i'd", "what's"]
        found_contractions = [c.lower() for c in analysis['contractions_found']]
        
        for expected in expected_contractions:
            self.assertIn(expected, found_contractions, 
                         f"Should find contraction '{expected}' in text")
        
        # Should identify problematic ones
        self.assertGreater(len(analysis['problematic_contractions']), 0,
                          "Should identify problematic contractions")
        
        print("✅ Analysis functionality working correctly")

def run_comprehensive_contraction_tests():
    """Run all contraction tests and provide summary"""
    print("🔧" * 30)
    print("PHONETIC CONTRACTION PROCESSOR - COMPREHENSIVE TEST SUITE")
    print("🔧" * 30)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhoneticContractionFixes)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=open('/dev/null', 'w'))
    result = runner.run(suite)
    
    # Calculate success rate
    total_tests = result.testsRun
    failed_tests = len(result.failures) + len(result.errors)
    passed_tests = total_tests - failed_tests
    success_rate = passed_tests / total_tests if total_tests > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"CONTRACTION FIXES TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Run: {total_tests}")
    print(f"Tests Passed: {passed_tests}")
    print(f"Tests Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1%}")
    
    if success_rate >= 0.95:
        print("🎉 EXCELLENT: Contraction pronunciation fixes are working excellently!")
    elif success_rate >= 0.9:
        print("✅ GOOD: Contraction pronunciation fixes are working well!")
    elif success_rate >= 0.8:
        print("⚠️  ACCEPTABLE: Contraction pronunciation fixes need some improvements.")
    else:
        print("❌ NEEDS WORK: Contraction pronunciation fixes require significant improvements.")
    
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
    test_instance = TestPhoneticContractionFixes()
    test_instance.setUp()
    
    try:
        test_instance.test_critical_pronunciation_fixes()
        test_instance.test_negative_contractions()
        test_instance.test_will_contractions()
        test_instance.test_would_contractions()
        test_instance.test_context_sensitive_contractions()
        test_instance.test_case_preservation()
        test_instance.test_phonetic_representations()
        test_instance.test_analysis_functionality()
        
        print("\n🎉 All individual tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    
    # Run comprehensive test suite
    run_comprehensive_contraction_tests()
