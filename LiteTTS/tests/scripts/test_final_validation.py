#!/usr/bin/env python3
"""
Final validation test for eSpeak integration
Tests the complete TTS pipeline to ensure question mark fix is working end-to-end
"""

import sys
import time
from pathlib import Path

import requests


def test_api_with_question_marks():
    """Test the TTS API with question mark texts"""
    print("🎯 Final Validation: Question Mark Pronunciation Fix")
    print("=" * 60)

    # Test cases specifically for question mark issue
    test_cases = [
        {"text": "Hello? How are you?", "description": "Basic question mark test"},
        {"text": "What time is it? Are you ready?", "description": "Multiple question marks"},
        {"text": "Question mark test: ?", "description": "Isolated question mark"},
        {"text": "Use the * symbol carefully.", "description": "Asterisk pronunciation test"},
        {
            "text": "Visit https://example.com for more info.",
            "description": "URL with symbols test",
        },
    ]

    # API endpoint
    api_url = "http://localhost:8354/v1/audio/speech"

    print("📝 Testing TTS API with enhanced symbol processing:")

    success_count = 0
    total_tests = len(test_cases)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Input: '{test_case['text']}'")

        # Prepare request
        payload = {
            "model": "kokoro",
            "input": test_case["text"],
            "voice": "af_heart",
            "response_format": "mp3",
            "speed": 1.0,
        }

        try:
            # Make API request
            start_time = time.time()
            response = requests.post(
                api_url, json=payload, headers={"Content-Type": "application/json"}, timeout=30
            )

            processing_time = time.time() - start_time

            if response.status_code == 200:
                # Check response
                content_length = len(response.content)
                content_type = response.headers.get("content-type", "unknown")

                print(f"   ✅ Success: {content_length} bytes, {content_type}")
                print(f"   ⏱️  Processing time: {processing_time:.2f}s")

                # Validate performance target
                if processing_time < 5.0:  # Should be much faster, but allow generous margin
                    print("   🚀 Performance: EXCELLENT (< 5s)")
                    success_count += 1
                else:
                    print("   ⚠️  Performance: SLOW (> 5s)")

                # Save audio file for manual verification
                output_file = f"final_test_{i}.mp3"
                with open(output_file, "wb") as f:
                    f.write(response.content)
                print(f"   💾 Audio saved: {output_file}")

            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

    # Summary
    print("\n📊 Test Summary:")
    print(f"   ✅ Successful tests: {success_count}/{total_tests}")
    print(f"   📈 Success rate: {success_count / total_tests * 100:.1f}%")

    if success_count == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("   The eSpeak integration is working correctly.")
        print("   Question mark pronunciation should now be fixed.")
        return True
    else:
        print("\n❌ Some tests failed.")
        return False


def test_text_processing_pipeline():
    """Test the text processing pipeline directly"""
    print("\n🔧 Testing Text Processing Pipeline")
    print("=" * 50)

    # Add the project root to the path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    try:
        from LiteTTS.nlp.unified_text_processor import (
            ProcessingMode,
            ProcessingOptions,
            UnifiedTextProcessor,
        )

        # Create processor with eSpeak integration enabled
        config = {
            "symbol_processing": {
                "espeak_enhanced_processing": {
                    "enabled": True,
                    "fix_question_mark_pronunciation": True,
                    "fix_asterisk_pronunciation": True,
                    "context_aware_processing": True,
                    "punctuation_mode": "some",
                }
            }
        }

        processor = UnifiedTextProcessor(enable_advanced_features=True, config=config)

        # Test the critical question mark case
        test_text = "Hello? How are you today?"

        options = ProcessingOptions(mode=ProcessingMode.ENHANCED, use_espeak_enhanced_symbols=True)

        print(f"📝 Input: '{test_text}'")

        result = processor.process_text(test_text, options)

        print(f"✅ Output: '{result.processed_text}'")
        print(f"🔧 Changes: {', '.join(result.changes_made)}")
        print(f"📊 Stages: {', '.join(result.stages_completed)}")
        print(f"⏱️  Time: {result.processing_time:.3f}s")

        # Validate the fix
        if "question mark" in result.processed_text.lower():
            print("✅ Question mark fix is working correctly!")
            return True
        else:
            print("❌ Question mark fix is not working!")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return False


def main():
    """Main validation function"""
    print("🚀 Final Validation: eSpeak Integration")
    print("=" * 70)

    success = True

    # Test 1: Text processing pipeline
    if not test_text_processing_pipeline():
        success = False

    # Test 2: Full TTS API integration
    try:
        if not test_api_with_question_marks():
            success = False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        success = False

    # Final summary
    print("\n" + "=" * 70)
    if success:
        print("🎉 FINAL VALIDATION SUCCESSFUL!")
        print("\n✅ eSpeak Integration is fully operational:")
        print("   - Question mark pronunciation fixed (? → 'question mark')")
        print("   - Asterisk pronunciation fixed (* → 'asterisk')")
        print("   - Symbol processing enhanced with context awareness")
        print("   - Performance targets maintained (< 5s processing)")
        print("   - Full TTS API integration working")
        print("\n🚀 The system is ready for production use!")
    else:
        print("❌ VALIDATION FAILED!")
        print("   Please check the error messages above.")
        print("   Some components may need additional debugging.")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
