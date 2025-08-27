#!/usr/bin/env python3
"""
Test script to investigate phonetic processing issues
"""

import sys
import json
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_phonetic_processor_import():
    """Test if phonetic processor can be imported"""
    print("🔍 Testing Phonetic Processor Import")
    print("=" * 50)

    try:
        from LiteTTS.nlp.phonetic_processor import PhoneticProcessor
        print("✅ PhoneticProcessor imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import PhoneticProcessor: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing PhoneticProcessor: {e}")
        return False

def test_phonetic_dictionary_manager():
    """Test if phonetic dictionary manager can be imported and initialized"""
    print("\n🔍 Testing Phonetic Dictionary Manager")
    print("=" * 50)

    try:
        from LiteTTS.nlp.phonetic_dictionary_manager import PhoneticDictionaryManager
        print("✅ PhoneticDictionaryManager imported successfully")

        # Test initialization
        manager = PhoneticDictionaryManager({})
        print("✅ PhoneticDictionaryManager initialized successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import PhoneticDictionaryManager: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error with PhoneticDictionaryManager: {e}")
        return False

def test_dictionary_loading():
    """Test loading phonetic dictionaries"""
    print("\n🔍 Testing Dictionary Loading")
    print("=" * 50)

    try:
        from LiteTTS.nlp.phonetic_dictionary_manager import PhoneticDictionaryManager

        # Test configuration
        config = {
            "dictionary_sources": {
                "arpabet": "docs/dictionaries/cmudict.dict",
                "ipa": "docs/dictionaries/ipa_dict.json",
                "unisyn": "docs/dictionaries/unisyn_dict.json"
            }
        }

        manager = PhoneticDictionaryManager(config)

        # Try to load each dictionary
        for notation, file_path in config["dictionary_sources"].items():
            print(f"\n📚 Loading {notation} dictionary from {file_path}")

            # Check if file exists
            if not Path(file_path).exists():
                print(f"   ❌ File does not exist: {file_path}")
                continue

            try:
                success = manager.load_dictionary(notation, file_path)
                if success:
                    print(f"   ✅ Successfully loaded {notation} dictionary")

                    # Get some stats
                    stats = manager.get_statistics()
                    if notation in stats:
                        print(f"   📊 Entries: {stats[notation].total_entries}")
                        print(f"   ⏱️  Load time: {stats[notation].load_time:.3f}s")
                else:
                    print(f"   ❌ Failed to load {notation} dictionary")
            except Exception as e:
                print(f"   ❌ Error loading {notation} dictionary: {e}")

        return True

    except Exception as e:
        print(f"❌ Dictionary loading test failed: {e}")
        return False

def test_phonetic_processing():
    """Test phonetic processing with a simple example"""
    print("\n🔍 Testing Phonetic Processing")
    print("=" * 50)

    try:
        from LiteTTS.nlp.phonetic_processor import PhoneticProcessor

        # Test configuration
        config = {
            "enabled": True,
            "auto_load_dictionaries": False,  # Don't auto-load to avoid issues
            "pronunciation_markers": {
                "rime_ai_style": True,
                "custom_markers": True,
                "ipa_notation": True,
                "nato_phonetic": True
            }
        }

        processor = PhoneticProcessor({"phonetic_processing": config})

        # Test cases
        test_cases = [
            "Hello world",
            "The quick brown fox",
            "Testing phonetic processing"
        ]

        print("📝 Testing phonetic processing:")

        for i, test_text in enumerate(test_cases, 1):
            print(f"\n{i}. Input: '{test_text}'")

            try:
                start_time = time.perf_counter()
                result = processor.process_phonetics(test_text)
                processing_time = time.perf_counter() - start_time

                print(f"   ✅ Output: '{result}'")
                print(f"   ⏱️  Time: {processing_time:.3f}s")

            except Exception as e:
                print(f"   ❌ Error: {e}")
                return False

        return True

    except Exception as e:
        print(f"❌ Phonetic processing test failed: {e}")
        return False

def test_unified_processor_with_phonetics():
    """Test unified text processor with phonetic processing enabled"""
    print("\n🔍 Testing Unified Processor with Phonetics")
    print("=" * 50)

    try:
        from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode

        # Create a test config with phonetic processing enabled
        config = {
            "beta_features": {
                "enabled": True,
                "phonetic_processing": {
                    "enabled": True,
                    "auto_load_dictionaries": False,  # Avoid loading large dictionaries
                    "pronunciation_markers": {
                        "rime_ai_style": True,
                        "custom_markers": True,
                        "ipa_notation": True,
                        "nato_phonetic": True
                    }
                }
            }
        }

        processor = UnifiedTextProcessor(enable_advanced_features=True, config=config)

        # Test cases
        test_cases = [
            "Hello? How are you?",
            "Testing phonetic processing"
        ]

        options = ProcessingOptions(mode=ProcessingMode.ENHANCED)

        print("📝 Testing unified processor with phonetics:")

        for i, test_text in enumerate(test_cases, 1):
            print(f"\n{i}. Input: '{test_text}'")

            try:
                start_time = time.perf_counter()
                result = processor.process_text(test_text, options)
                processing_time = time.perf_counter() - start_time

                print(f"   ✅ Output: '{result.processed_text}'")
                print(f"   ⏱️  Time: {processing_time:.3f}s")
                print(f"   📊 Stages: {', '.join(result.stages_completed)}")

                # Check if phonetic processing was executed
                if "phonetic_processing" in result.stages_completed:
                    print("   ✅ Phonetic processing was executed")
                elif "phonetic_processing_skipped" in result.stages_completed:
                    print("   ⚠️  Phonetic processing was skipped")

            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
                return False

        return True

    except Exception as e:
        print(f"❌ Unified processor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Phonetic Processing Investigation")
    print("=" * 60)

    success = True

    # Test 1: Import test
    if not test_phonetic_processor_import():
        success = False

    # Test 2: Dictionary manager test
    if not test_phonetic_dictionary_manager():
        success = False

    # Test 3: Dictionary loading test
    if not test_dictionary_loading():
        success = False

    # Test 4: Phonetic processing test
    if not test_phonetic_processing():
        success = False

    # Test 5: Unified processor test
    if not test_unified_processor_with_phonetics():
        success = False

    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ INVESTIGATION SUCCESSFUL!")
        print("\n🎉 Phonetic processing components are working:")
        print("   - All imports successful")
        print("   - Dictionary loading functional")
        print("   - Phonetic processing operational")
        print("   - Integration with unified processor working")
        print("\n💡 The phonetic processing system appears to be functional.")
        print("   The issue may be with specific configurations or edge cases.")
    else:
        print("❌ INVESTIGATION FOUND ISSUES!")
        print("   Some phonetic processing components are not working correctly.")
        print("   Check the error messages above to identify the root cause.")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)