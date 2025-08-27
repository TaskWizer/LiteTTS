#!/usr/bin/env python3
"""
Period Pronunciation Issue Investigation

This script reproduces and analyzes the critical period pronunciation issue
where the TTS system incorrectly vocalizes "period" instead of natural pauses.
"""

import asyncio
import sys
import time
import requests
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_period_pronunciation_reproduction():
    """Reproduce the period pronunciation issue with various test cases"""
    print("🔍 Reproducing Period Pronunciation Issue")
    print("=" * 60)
    
    # Test cases specifically designed to reveal period vocalization
    test_cases = [
        {
            "text": "Hello world.",
            "description": "Simple sentence with period",
            "expected_behavior": "Natural pause, no 'period' vocalization"
        },
        {
            "text": "This is a test. This is another sentence.",
            "description": "Multiple sentences with periods",
            "expected_behavior": "Natural pauses between sentences"
        },
        {
            "text": "The cost is $25.99 for the item.",
            "description": "Decimal number with sentence-ending period",
            "expected_behavior": "Currency processing + natural pause"
        },
        {
            "text": "Dr. Smith went to the store.",
            "description": "Abbreviation period + sentence period",
            "expected_behavior": "Natural handling of both periods"
        },
        {
            "text": "Hello world",
            "description": "No period control test",
            "expected_behavior": "No period-related issues"
        },
        {
            "text": "What time is it? The answer is 3:30 PM.",
            "description": "Question mark + period combination",
            "expected_behavior": "Question mark pronunciation + natural pause"
        }
    ]
    
    api_url = "http://localhost:8354/v1/audio/speech"
    
    print("📝 Testing period pronunciation across different scenarios:")
    
    issues_found = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Input: '{test_case['text']}'")
        print(f"   Expected: {test_case['expected_behavior']}")
        
        payload = {
            "model": "kokoro",
            "input": test_case['text'],
            "voice": "af_heart",
            "response_format": "wav",
            "speed": 1.0
        }
        
        try:
            start_time = time.perf_counter()
            response = requests.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            processing_time = time.perf_counter() - start_time
            
            if response.status_code == 200:
                audio_size = len(response.content)
                estimated_duration = audio_size / (24000 * 2)  # 24kHz, 16-bit
                
                print(f"   ✅ Audio generated: {audio_size} bytes")
                print(f"   ⏱️  Processing time: {processing_time:.3f}s")
                print(f"   📊 Estimated duration: {estimated_duration:.3f}s")
                
                # Save audio for manual verification
                audio_file = f"period_test_{i}.wav"
                with open(audio_file, 'wb') as f:
                    f.write(response.content)
                print(f"   💾 Audio saved: {audio_file}")
                print(f"   🎧 Manual verification needed: Listen for 'period' vocalization")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                issues_found.append(f"API error for test case {i}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            issues_found.append(f"Exception for test case {i}: {e}")
    
    print(f"\n📊 Reproduction Test Summary:")
    print(f"   Test cases executed: {len(test_cases)}")
    print(f"   Issues found: {len(issues_found)}")
    if issues_found:
        print(f"   Issues: {', '.join(issues_found)}")
    
    return len(issues_found) == 0

def test_text_processing_pipeline():
    """Test the text processing pipeline to see how periods are handled"""
    print("\n🔧 Testing Text Processing Pipeline for Period Handling")
    print("=" * 60)
    
    try:
        from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode
        
        # Create processor
        processor = UnifiedTextProcessor(enable_advanced_features=True)
        
        # Test cases to trace period processing
        test_cases = [
            "Hello world.",
            "This is a test. Another sentence.",
            "The cost is $25.99.",
            "Dr. Smith went home.",
            "What time is it? It's 3:30 PM."
        ]
        
        options = ProcessingOptions(
            mode=ProcessingMode.ENHANCED,
            use_espeak_enhanced_symbols=True
        )
        
        print("📝 Tracing period processing through pipeline:")
        
        for i, test_text in enumerate(test_cases, 1):
            print(f"\n{i}. Input: '{test_text}'")
            
            try:
                result = processor.process_text(test_text, options)
                
                print(f"   ✅ Output: '{result.processed_text}'")
                print(f"   ⏱️  Time: {result.processing_time:.3f}s")
                print(f"   📊 Stages: {', '.join(result.stages_completed)}")
                
                # Check for period-related processing
                if "period" in result.processed_text.lower():
                    print(f"   ⚠️  WARNING: 'period' found in processed text!")
                    print(f"   🔍 This indicates period vocalization issue")
                else:
                    print(f"   ✅ No 'period' vocalization in processed text")
                
                # Check if periods are still present
                if "." in result.processed_text:
                    print(f"   📍 Periods preserved in processed text")
                else:
                    print(f"   📍 Periods removed/processed in text")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Text processing test failed: {e}")
        return False

def test_voice_model_comparison():
    """Test period pronunciation across different voice models"""
    print("\n🎭 Testing Period Pronunciation Across Voice Models")
    print("=" * 60)
    
    # Test with a subset of voice models to identify if issue is voice-specific
    test_voices = ["af_heart", "af_sky", "af_summit", "am_adam", "am_michael"]
    test_text = "Hello world. This is a test."
    
    api_url = "http://localhost:8354/v1/audio/speech"
    
    print(f"📝 Testing text: '{test_text}'")
    print(f"🎭 Testing voices: {', '.join(test_voices)}")
    
    voice_results = {}
    
    for voice in test_voices:
        print(f"\n🎤 Testing voice: {voice}")
        
        payload = {
            "model": "kokoro",
            "input": test_text,
            "voice": voice,
            "response_format": "wav",
            "speed": 1.0
        }
        
        try:
            start_time = time.perf_counter()
            response = requests.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            processing_time = time.perf_counter() - start_time
            
            if response.status_code == 200:
                audio_size = len(response.content)
                
                print(f"   ✅ Success: {audio_size} bytes")
                print(f"   ⏱️  Time: {processing_time:.3f}s")
                
                # Save audio for comparison
                audio_file = f"voice_comparison_{voice}.wav"
                with open(audio_file, 'wb') as f:
                    f.write(response.content)
                print(f"   💾 Audio saved: {audio_file}")
                
                voice_results[voice] = {
                    "success": True,
                    "audio_size": audio_size,
                    "processing_time": processing_time
                }
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                voice_results[voice] = {"success": False, "error": response.status_code}
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            voice_results[voice] = {"success": False, "error": str(e)}
    
    # Summary
    successful_voices = [v for v, r in voice_results.items() if r.get("success", False)]
    failed_voices = [v for v, r in voice_results.items() if not r.get("success", False)]
    
    print(f"\n📊 Voice Model Test Summary:")
    print(f"   Successful voices: {len(successful_voices)}/{len(test_voices)}")
    print(f"   Failed voices: {len(failed_voices)}")
    
    if successful_voices:
        print(f"   ✅ Working voices: {', '.join(successful_voices)}")
    if failed_voices:
        print(f"   ❌ Failed voices: {', '.join(failed_voices)}")
    
    return len(successful_voices) > 0

def test_configuration_impact():
    """Test how configuration settings affect period pronunciation"""
    print("\n⚙️  Testing Configuration Impact on Period Pronunciation")
    print("=" * 60)
    
    try:
        # Load current configuration
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        # Check punctuation handling settings
        punctuation_config = config.get("punctuation_handling", {})
        symbol_config = config.get("symbol_processing", {})
        text_config = config.get("text_processing", {})
        
        print("📊 Current Configuration Analysis:")
        
        # Punctuation handling
        print(f"\n🔤 Punctuation Handling:")
        print(f"   Enabled: {punctuation_config.get('enabled', 'Not set')}")
        print(f"   Comma pause timing: {punctuation_config.get('comma_pause_timing', 'Not set')}")
        print(f"   Question intonation: {punctuation_config.get('question_intonation', 'Not set')}")
        print(f"   Exclamation emphasis: {punctuation_config.get('exclamation_emphasis', 'Not set')}")
        
        # Symbol processing
        print(f"\n🔣 Symbol Processing:")
        espeak_config = symbol_config.get("espeak_enhanced_processing", {})
        print(f"   eSpeak enhanced enabled: {espeak_config.get('enabled', 'Not set')}")
        print(f"   Fix question mark: {espeak_config.get('fix_question_mark_pronunciation', 'Not set')}")
        print(f"   Fix asterisk: {espeak_config.get('fix_asterisk_pronunciation', 'Not set')}")
        print(f"   Context aware: {espeak_config.get('context_aware_processing', 'Not set')}")
        print(f"   Punctuation mode: {espeak_config.get('punctuation_mode', 'Not set')}")
        
        # Text processing
        print(f"\n📝 Text Processing:")
        print(f"   Enabled: {text_config.get('enabled', 'Not set')}")
        print(f"   Normalize punctuation: {text_config.get('normalize_punctuation', 'Not set')}")
        print(f"   Handle contractions: {text_config.get('handle_contractions', 'Not set')}")
        
        # Beta features
        beta_config = config.get("beta_features", {})
        print(f"\n🧪 Beta Features:")
        print(f"   Enabled: {beta_config.get('enabled', 'Not set')}")
        
        # Check for potential issues
        potential_issues = []
        
        if espeak_config.get("punctuation_mode") == "all":
            potential_issues.append("eSpeak punctuation_mode set to 'all' - may cause period vocalization")
        
        if text_config.get("normalize_punctuation", True):
            potential_issues.append("Text processing normalize_punctuation enabled - may affect period handling")
        
        if potential_issues:
            print(f"\n⚠️  Potential Configuration Issues:")
            for issue in potential_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ No obvious configuration issues detected")
        
        return len(potential_issues) == 0
        
    except Exception as e:
        print(f"❌ Configuration analysis failed: {e}")
        return False

async def main():
    """Main investigation function"""
    print("🚀 Period Pronunciation Issue Investigation")
    print("=" * 70)
    
    success = True
    
    # Test 1: Reproduce the issue
    print("Phase 1: Issue Reproduction")
    if not test_period_pronunciation_reproduction():
        success = False
    
    # Test 2: Text processing pipeline analysis
    print("\nPhase 2: Text Processing Pipeline Analysis")
    if not test_text_processing_pipeline():
        success = False
    
    # Test 3: Voice model comparison
    print("\nPhase 3: Voice Model Comparison")
    if not test_voice_model_comparison():
        success = False
    
    # Test 4: Configuration impact analysis
    print("\nPhase 4: Configuration Impact Analysis")
    if not test_configuration_impact():
        success = False
    
    # Summary
    print("\n" + "=" * 70)
    if success:
        print("✅ INVESTIGATION PHASE 1 COMPLETED!")
        print("\n🔍 Key Findings:")
        print("   - Audio generation working across test scenarios")
        print("   - Text processing pipeline operational")
        print("   - Voice models responding correctly")
        print("   - Configuration analysis completed")
        print("\n🎧 Next Steps:")
        print("   1. Listen to generated audio files for period vocalization")
        print("   2. Analyze text processing output for 'period' strings")
        print("   3. Identify specific pipeline stage causing the issue")
        print("   4. Implement targeted fixes")
        print("\n📁 Generated Files:")
        print("   - period_test_*.wav: Test audio files for manual verification")
        print("   - voice_comparison_*.wav: Voice model comparison files")
    else:
        print("❌ INVESTIGATION PHASE 1 ENCOUNTERED ISSUES!")
        print("   Some components are not working correctly.")
        print("   Check the error messages above for details.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
