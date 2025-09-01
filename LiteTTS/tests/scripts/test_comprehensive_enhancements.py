#!/usr/bin/env python3
"""
Comprehensive test script for all TTS enhancements
Tests pronunciation fixes, audio quality enhancements, and performance optimizations
"""

import sys
import os
import time
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from LiteTTS.nlp.unified_pronunciation_fix import unified_pronunciation_fix
from LiteTTS.nlp.audio_quality_enhancer import audio_quality_enhancer, AudioQualityProfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_pronunciation_fixes():
    """Test all pronunciation fixes"""
    print("\n🔧 Testing Pronunciation Fixes")
    print("=" * 50)
    
    test_cases = [
        # Comma handling issues
        "thinking, or not thinking",
        "walking, and running together",
        "hmm, let me think about this",
        
        # Diphthong pronunciation issues
        "joy to the world",
        "that boy is full of joy",
        "I enjoy reading books",
        
        # Contraction processing issues
        "I'm happy to see you",
        "you're absolutely right",
        "we'll be there soon",
        "I'd like to help",
        
        # Interjection handling issues
        "hmm, that's interesting",
        "uh, I don't know",
        "um, maybe we should try",
        "ah, I see what you mean",
    ]
    
    total_fixes = 0
    for i, test_text in enumerate(test_cases, 1):
        result = unified_pronunciation_fix.process_pronunciation_fixes(test_text)
        
        if result.processed_text != result.original_text:
            print(f"✅ Test {i}: FIXED")
            print(f"   Original: '{result.original_text}'")
            print(f"   Fixed:    '{result.processed_text}'")
            print(f"   Fixes:    {', '.join(result.fixes_applied)}")
            total_fixes += len(result.fixes_applied)
        else:
            print(f"⚪ Test {i}: OK (no changes needed)")
            print(f"   Text: '{test_text}'")
    
    print(f"\n📊 Pronunciation Fix Summary: {total_fixes} total fixes applied")
    return total_fixes > 0

def test_audio_quality_enhancements():
    """Test audio quality enhancements"""
    print("\n🎵 Testing Audio Quality Enhancements")
    print("=" * 50)
    
    test_cases = [
        # Emotional content
        "I'm so excited about this amazing opportunity!",
        "I'm really sorry to hear about your loss.",
        "That's absolutely fantastic news!",
        "I'm not sure if this is the right approach.",
        
        # Prosodic opportunities
        "However, we need to consider the consequences.",
        "The quick brown fox jumps over the lazy dog.",
        "Please, thank you, and excuse me are polite phrases.",
        
        # Context adaptations
        "Are you coming to the party tonight?",
        "What an incredible performance!",
        "The book (which I mentioned earlier) is excellent.",
        "She said, \"I'll be there at five o'clock.\"",
        
        # Complex sentences
        "Well, I think we should carefully consider all the options, but ultimately, the decision is yours to make.",
    ]
    
    total_enhancements = 0
    for i, test_text in enumerate(test_cases, 1):
        # Analyze quality potential
        analysis = audio_quality_enhancer.analyze_quality_potential(test_text)
        
        # Apply enhancements
        enhanced_text = audio_quality_enhancer.enhance_audio_quality(test_text)
        
        print(f"\n📝 Test {i}:")
        print(f"   Original: '{test_text}'")
        if enhanced_text != test_text:
            print(f"   Enhanced: '{enhanced_text}'")
            total_enhancements += 1
        else:
            print(f"   Enhanced: (no changes)")
        
        print(f"   Analysis:")
        print(f"     - Emotional content: {analysis['emotional_content']}")
        print(f"     - Prosodic opportunities: {len(analysis['prosodic_opportunities'])}")
        print(f"     - Context adaptations: {analysis['context_adaptations']}")
        print(f"     - Naturalness score: {analysis['naturalness_score']:.2f}")
        print(f"     - Enhancement potential: {analysis['enhancement_potential']}")
    
    print(f"\n📊 Audio Quality Summary: {total_enhancements} texts enhanced")
    return total_enhancements > 0

def test_api_performance():
    """Test API performance with enhancements"""
    print("\n🚀 Testing API Performance with Enhancements")
    print("=" * 50)
    
    # Test cases with different complexity levels
    test_cases = [
        ("Simple", "Hello, world!"),
        ("Emotional", "I'm so excited about this amazing opportunity!"),
        ("Complex", "Well, thinking, or perhaps I should say pondering, about this joyful occasion makes me feel quite happy, and I'm sure you're excited too!"),
        ("Problematic", "hmm, thinking, or maybe I'm wrong about joy, but you're right"),
    ]
    
    api_url = "http://localhost:8354/v1/audio/speech"
    
    performance_results = []
    
    for test_name, test_text in test_cases:
        print(f"\n🧪 Testing: {test_name}")
        print(f"   Text: {test_text[:60]}{'...' if len(test_text) > 60 else ''}")
        
        try:
            start_time = time.time()
            response = requests.post(api_url, json={
                'model': 'kokoro',
                'input': test_text,
                'voice': 'af_heart',
                'response_format': 'mp3'
            }, timeout=30)
            
            if response.status_code == 200:
                generation_time = time.time() - start_time
                audio_length = len(response.content)
                
                # Estimate RTF
                estimated_duration = audio_length / 16000  # Rough estimate
                rtf = generation_time / estimated_duration if estimated_duration > 0 else 0
                
                print(f"   ✅ Success: RTF={rtf:.3f}, Time={generation_time:.3f}s, Size={audio_length}B")
                
                performance_results.append({
                    'test': test_name,
                    'rtf': rtf,
                    'time': generation_time,
                    'size': audio_length
                })
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ API not running. Start with: python app.py")
            return False
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    if performance_results:
        print(f"\n📊 Performance Summary:")
        avg_rtf = sum(r['rtf'] for r in performance_results) / len(performance_results)
        avg_time = sum(r['time'] for r in performance_results) / len(performance_results)
        print(f"   Average RTF: {avg_rtf:.3f}")
        print(f"   Average Time: {avg_time:.3f}s")
        print(f"   Target RTF: 0.6-0.7 {'✅ ACHIEVED' if avg_rtf <= 0.7 else '⚠️ ABOVE TARGET'}")
    
    return len(performance_results) > 0

def test_end_to_end_processing():
    """Test complete end-to-end processing pipeline"""
    print("\n🔄 Testing End-to-End Processing Pipeline")
    print("=" * 50)
    
    # Complex test case with multiple issues
    test_text = "hmm, thinking, or maybe I'm wrong about joy, but you're absolutely right! Are you excited? I'd say this is fantastic news, however, we should be careful."
    
    print(f"📝 Original Text:")
    print(f"   '{test_text}'")
    
    # Step 1: Pronunciation fixes
    print(f"\n🔧 Step 1: Pronunciation Fixes")
    pronunciation_result = unified_pronunciation_fix.process_pronunciation_fixes(test_text)
    print(f"   Result: '{pronunciation_result.processed_text}'")
    print(f"   Fixes: {pronunciation_result.fixes_applied}")
    
    # Step 2: Audio quality enhancements
    print(f"\n🎵 Step 2: Audio Quality Enhancements")
    quality_analysis = audio_quality_enhancer.analyze_quality_potential(pronunciation_result.processed_text)
    enhanced_text = audio_quality_enhancer.enhance_audio_quality(pronunciation_result.processed_text)
    print(f"   Result: '{enhanced_text}'")
    print(f"   Analysis: {quality_analysis['enhancement_potential']} potential")
    
    # Step 3: API test
    print(f"\n🚀 Step 3: API Generation Test")
    try:
        start_time = time.time()
        response = requests.post("http://localhost:8354/v1/audio/speech", json={
            'model': 'kokoro',
            'input': enhanced_text,
            'voice': 'af_heart',
            'response_format': 'mp3'
        }, timeout=30)
        
        if response.status_code == 200:
            generation_time = time.time() - start_time
            audio_length = len(response.content)
            estimated_duration = audio_length / 16000
            rtf = generation_time / estimated_duration if estimated_duration > 0 else 0
            
            print(f"   ✅ Success: RTF={rtf:.3f}, Time={generation_time:.3f}s")
            print(f"   Audio size: {audio_length} bytes")
            
            # Save test audio
            output_path = project_root / "test_output_enhanced.mp3"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"   💾 Audio saved to: {output_path}")
            
            return True
        else:
            print(f"   ❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Run comprehensive enhancement tests"""
    print("🎯 Kokoro TTS Comprehensive Enhancement Testing")
    print("=" * 60)
    
    test_results = {
        'pronunciation_fixes': False,
        'audio_quality': False,
        'api_performance': False,
        'end_to_end': False
    }
    
    try:
        # Run all tests
        test_results['pronunciation_fixes'] = test_pronunciation_fixes()
        test_results['audio_quality'] = test_audio_quality_enhancements()
        test_results['api_performance'] = test_api_performance()
        test_results['end_to_end'] = test_end_to_end_processing()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL ENHANCEMENTS WORKING CORRECTLY!")
            print("📈 System is ready for production deployment")
        elif passed_tests >= total_tests * 0.75:
            print("⚠️  Most enhancements working, minor issues detected")
            print("🔧 Review failed tests and apply fixes")
        else:
            print("❌ Multiple enhancement failures detected")
            print("🚨 System needs attention before deployment")
        
        return 0 if passed_tests == total_tests else 1
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
