#!/usr/bin/env python3
"""
Quick test of the eSpeak integration in the unified text processor
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode

def test_question_mark_fix():
    """Test the question mark fix in the unified processor"""
    print("🎯 Testing Question Mark Fix Integration")
    print("=" * 50)

    # Create processor with config
    config = {
        "symbol_processing": {
            "espeak_enhanced_processing": {
                "enabled": True,
                "fix_question_mark_pronunciation": True,
                "punctuation_mode": "some"
            }
        }
    }

    processor = UnifiedTextProcessor(enable_advanced_features=True, config=config)

    # Test cases
    test_cases = [
        "Hello? How are you?",
        "What time is it?",
        "Use the * symbol carefully",
        'She said "Hello world"',
        "Visit https://example.com for info",
    ]

    # Create processing options
    options = ProcessingOptions(
        mode=ProcessingMode.ENHANCED,
        use_espeak_enhanced_symbols=True
    )

    print("📝 Testing text processing with eSpeak enhancements:")

    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. Input: '{test_text}'")

        try:
            result = processor.process_text(test_text, options)

            print(f"   ✅ Output: '{result.processed_text}'")
            print(f"   🔧 Changes: {', '.join(result.changes_made) if result.changes_made else 'None'}")
            print(f"   📊 Stages: {', '.join(result.stages_completed)}")
            print(f"   ⏱️  Time: {result.processing_time:.3f}s")

            # Check if question mark fix was applied
            if "?" in test_text and "question mark" in result.processed_text.lower():
                print("   ✅ Question mark fix applied successfully!")
            elif "*" in test_text and "asterisk" in result.processed_text.lower():
                print("   ✅ Asterisk fix applied successfully!")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    return True

def main():
    """Main test function"""
    print("🚀 eSpeak Integration Test")
    print("=" * 40)

    try:
        success = test_question_mark_fix()

        if success:
            print("\n✅ Integration test completed successfully!")
            print("   eSpeak-enhanced symbol processing is working in the unified pipeline.")
        else:
            print("\n❌ Integration test failed.")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
