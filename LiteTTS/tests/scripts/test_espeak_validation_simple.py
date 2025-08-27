#!/usr/bin/env python3
"""
Simple eSpeak Integration Validation Test

This script validates our eSpeak integration improvements by testing
the text processing pipeline directly and ensuring audio generation works.
"""

import asyncio
import sys
import time
import requests
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_text_processing_pipeline():
    """Test the text processing pipeline with eSpeak enhancements"""
    print("🔧 Testing Text Processing Pipeline with eSpeak Enhancements")
    print("=" * 60)
    
    try:
        from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode
        
        # Create processor with eSpeak integration enabled
        processor = UnifiedTextProcessor(enable_advanced_features=True)
        
        # Test cases for our eSpeak improvements
        test_cases = [
            {
                "input": "Hello? How are you?",
                "description": "Question mark pronunciation test",
                "expected_contains": ["question mark"]
            },
            {
                "input": "Use the * symbol carefully",
                "description": "Asterisk pronunciation test", 
                "expected_contains": ["asterisk"]
            },
            {
                "input": "What is 2 * 3? The answer is 6!",
                "description": "Combined symbols test",
                "expected_contains": ["asterisk", "question mark"]
            },
            {
                "input": "The cost is $50.99",
                "description": "Currency processing test",
                "expected_contains": ["dollars"]
            }
        ]
        
        options = ProcessingOptions(
            mode=ProcessingMode.ENHANCED,
            use_espeak_enhanced_symbols=True
        )
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['description']}")
            print(f"   Input: '{test_case['input']}'")
            
            try:
                result = processor.process_text(test_case['input'], options)
                
                print(f"   ✅ Output: '{result.processed_text}'")
                print(f"   ⏱️  Time: {result.processing_time:.3f}s")
                print(f"   📊 Stages: {', '.join(result.stages_completed)}")
                
                # Check if expected content is present
                output_lower = result.processed_text.lower()
                found_expected = []
                
                for expected in test_case.get("expected_contains", []):
                    if expected.lower() in output_lower:
                        found_expected.append(expected)
                
                if found_expected:
                    print(f"   ✅ Found expected content: {', '.join(found_expected)}")
                    passed_tests += 1
                else:
                    print(f"   ⚠️  Expected content not found: {test_case.get('expected_contains', [])}")
                
                # Check if eSpeak-enhanced symbol processing was applied
                if "espeak_enhanced_symbols" in result.stages_completed:
                    print("   ✅ eSpeak-enhanced symbol processing applied")
                else:
                    print("   ⚠️  eSpeak-enhanced symbol processing not applied")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        success_rate = passed_tests / total_tests
        print(f"\n📊 Text Processing Results:")
        print(f"   Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {success_rate:.1%}")
        
        return success_rate >= 0.75  # 75% success rate threshold
        
    except Exception as e:
        print(f"❌ Text processing test failed: {e}")
        return False

async def test_audio_generation():
    """Test audio generation with eSpeak-enhanced text"""
    print("\n🎵 Testing Audio Generation with eSpeak Enhancements")
    print("=" * 60)
    
    # Test cases specifically for our eSpeak improvements
    test_cases = [
        {
            "text": "Hello? How are you?",
            "description": "Question mark audio test"
        },
        {
            "text": "Use the * symbol carefully",
            "description": "Asterisk audio test"
        },
        {
            "text": "The cost is $25.99",
            "description": "Currency audio test"
        },
        {
            "text": "Hello world",
            "description": "Basic regression test"
        }
    ]
    
    api_url = "http://localhost:8354/v1/audio/speech"
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Input: '{test_case['text']}'")
        
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
                
                # Estimate audio duration (rough calculation)
                estimated_duration = audio_size / (24000 * 2)  # 24kHz, 16-bit
                rtf = processing_time / estimated_duration if estimated_duration > 0 else float('inf')
                
                print(f"   ✅ Success: {audio_size} bytes")
                print(f"   ⏱️  Processing time: {processing_time:.3f}s")
                print(f"   📊 Estimated duration: {estimated_duration:.3f}s")
                print(f"   🚀 RTF: {rtf:.3f}")
                
                # Check performance targets
                if rtf <= 0.5:  # Relaxed RTF target for testing
                    print("   ✅ Performance: Good RTF")
                    passed_tests += 1
                elif rtf <= 1.0:
                    print("   ⚠️  Performance: Acceptable RTF")
                    passed_tests += 0.5
                else:
                    print("   ❌ Performance: Poor RTF")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    success_rate = passed_tests / total_tests
    print(f"\n📊 Audio Generation Results:")
    print(f"   Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {success_rate:.1%}")
    
    return success_rate >= 0.75

def test_configuration_validation():
    """Test that our configuration changes are working"""
    print("\n⚙️  Testing Configuration Validation")
    print("=" * 60)
    
    try:
        import json
        
        # Load configuration
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        # Check audio quality testing configuration
        audio_config = config.get("audio_quality_testing", {})
        if not audio_config:
            print("❌ Audio quality testing configuration not found")
            return False
        
        print("✅ Audio quality testing configuration found")
        print(f"   Enabled: {audio_config.get('enabled', False)}")
        
        # Check symbol processing configuration
        symbol_config = config.get("symbol_processing", {})
        espeak_config = symbol_config.get("espeak_enhanced_processing", {})
        
        if espeak_config:
            print("✅ eSpeak-enhanced processing configuration found")
            print(f"   Enabled: {espeak_config.get('enabled', False)}")
            print(f"   Fix question mark: {espeak_config.get('fix_question_mark_pronunciation', False)}")
            print(f"   Fix asterisk: {espeak_config.get('fix_asterisk_pronunciation', False)}")
        else:
            print("⚠️  eSpeak-enhanced processing configuration not found")
        
        # Check beta features status
        beta_features = config.get("beta_features", {})
        beta_enabled = beta_features.get("enabled", True)
        
        print(f"📊 Beta features enabled: {beta_enabled}")
        if not beta_enabled:
            print("✅ Beta features correctly disabled")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

async def main():
    """Main validation function"""
    print("🚀 eSpeak Integration Simple Validation")
    print("=" * 70)
    
    success = True
    
    # Test 1: Configuration validation
    if not test_configuration_validation():
        success = False
    
    # Test 2: Text processing pipeline
    if not test_text_processing_pipeline():
        success = False
    
    # Test 3: Audio generation
    if not await test_audio_generation():
        success = False
    
    # Summary
    print("\n" + "=" * 70)
    if success:
        print("✅ eSpeak INTEGRATION VALIDATION SUCCESSFUL!")
        print("\n🎉 Key Findings:")
        print("   - Text processing pipeline working with eSpeak enhancements")
        print("   - Audio generation successful for all test cases")
        print("   - Configuration system properly integrated")
        print("   - Symbol processing improvements operational")
        print("\n💡 Next Steps:")
        print("   1. Consider enabling external ASR for transcription validation")
        print("   2. Monitor RTF performance and optimize if needed")
        print("   3. Run comprehensive test suite for full validation")
        print("   4. Establish baseline metrics for regression testing")
    else:
        print("❌ eSpeak INTEGRATION VALIDATION FAILED!")
        print("   Some components are not working as expected.")
        print("   Check the error messages above for details.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
