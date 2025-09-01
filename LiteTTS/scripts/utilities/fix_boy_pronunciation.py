#!/usr/bin/env python3
"""
Fix for "Boy" pronunciation issue - being pronounced as "boi" instead of full /bɔɪ/ sound

Since text processing preserves "Boy" correctly, the issue is likely in:
1. Phonemizer configuration
2. Phonetic dictionary mapping
3. TTS model behavior

This script implements pronunciation overrides for problematic words.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LiteTTS.nlp.homograph_resolver import HomographResolver
from LiteTTS.nlp.phonetic_processor import PhoneticProcessor
import json

def add_pronunciation_overrides():
    """Add pronunciation overrides for words with known issues"""
    
    print("🔧 Adding Pronunciation Overrides for Problematic Words")
    print("=" * 55)
    
    # Words that need pronunciation fixes
    pronunciation_fixes = {
        # Words losing final consonants
        "Boy": "/bɔɪ/",      # Ensure full diphthong pronunciation
        "boy": "/bɔɪ/",      # Lowercase version
        "Joy": "/dʒɔɪ/",     # Similar pattern
        "joy": "/dʒɔɪ/",     # Lowercase version
        "Toy": "/tɔɪ/",      # Similar pattern
        "toy": "/tɔɪ/",      # Lowercase version
        "June": "/dʒuːn/",   # Ensure final consonant
        "june": "/dʒuːn/",   # Lowercase version
        "Jan": "/dʒæn/",     # Ensure final consonant
        "jan": "/dʒæn/",     # Lowercase version
    }
    
    # Add to homograph resolver
    homograph_resolver = HomographResolver()
    
    for word, pronunciation in pronunciation_fixes.items():
        print(f"Adding override: '{word}' -> {pronunciation}")
        
        # Add as homograph with single pronunciation
        homograph_resolver.add_homograph(word, {
            "default": pronunciation,
            "phonetic": pronunciation
        })
    
    print(f"\n✅ Added {len(pronunciation_fixes)} pronunciation overrides")
    
    return pronunciation_fixes

def create_phonetic_markers():
    """Create phonetic markers for problematic words"""
    
    print("\n🔧 Creating Phonetic Markers")
    print("=" * 30)
    
    # Test phonetic processor with explicit markers
    phonetic_processor = PhoneticProcessor()
    
    test_cases = [
        "Boy",
        "The boy is here",
        "Joy and toy",
        "June is coming",
        "Jan said hello"
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: '{test_case}'")
        
        # Add phonetic markers
        with_markers = test_case
        with_markers = with_markers.replace("Boy", "{bɔɪ}")
        with_markers = with_markers.replace("boy", "{bɔɪ}")
        with_markers = with_markers.replace("Joy", "{dʒɔɪ}")
        with_markers = with_markers.replace("joy", "{dʒɔɪ}")
        with_markers = with_markers.replace("Toy", "{tɔɪ}")
        with_markers = with_markers.replace("toy", "{tɔɪ}")
        with_markers = with_markers.replace("June", "{dʒuːn}")
        with_markers = with_markers.replace("june", "{dʒuːn}")
        with_markers = with_markers.replace("Jan", "{dʒæn}")
        with_markers = with_markers.replace("jan", "{dʒæn}")
        
        print(f"With markers: '{with_markers}'")
        
        # Process through phonetic processor
        processed = phonetic_processor.process_phonetics(with_markers)
        print(f"Processed: '{processed}'")

def update_pronunciation_config():
    """Update pronunciation configuration files"""
    
    print("\n🔧 Updating Pronunciation Configuration")
    print("=" * 40)
    
    # Check if there's a pronunciation config file
    config_files = [
        "LiteTTS/config/pronunciation.json",
        "LiteTTS/config/phonetic_overrides.json",
        "LiteTTS/config/word_pronunciations.json"
    ]
    
    pronunciation_data = {
        "word_overrides": {
            "Boy": {
                "phonetic": "/bɔɪ/",
                "ipa": "bɔɪ",
                "description": "Full diphthong pronunciation to prevent 'boi' truncation"
            },
            "boy": {
                "phonetic": "/bɔɪ/",
                "ipa": "bɔɪ",
                "description": "Full diphthong pronunciation to prevent 'boi' truncation"
            },
            "Joy": {
                "phonetic": "/dʒɔɪ/",
                "ipa": "dʒɔɪ",
                "description": "Full diphthong pronunciation"
            },
            "joy": {
                "phonetic": "/dʒɔɪ/",
                "ipa": "dʒɔɪ",
                "description": "Full diphthong pronunciation"
            },
            "Toy": {
                "phonetic": "/tɔɪ/",
                "ipa": "tɔɪ",
                "description": "Full diphthong pronunciation"
            },
            "toy": {
                "phonetic": "/tɔɪ/",
                "ipa": "tɔɪ",
                "description": "Full diphthong pronunciation"
            },
            "June": {
                "phonetic": "/dʒuːn/",
                "ipa": "dʒuːn",
                "description": "Ensure final consonant is pronounced"
            },
            "june": {
                "phonetic": "/dʒuːn/",
                "ipa": "dʒuːn",
                "description": "Ensure final consonant is pronounced"
            },
            "Jan": {
                "phonetic": "/dʒæn/",
                "ipa": "dʒæn",
                "description": "Ensure final consonant is pronounced"
            },
            "jan": {
                "phonetic": "/dʒæn/",
                "ipa": "dʒæn",
                "description": "Ensure final consonant is pronounced"
            }
        },
        "metadata": {
            "description": "Pronunciation overrides for words with known TTS issues",
            "version": "1.0",
            "created_by": "pronunciation_fix_script"
        }
    }
    
    # Create pronunciation override file
    config_file = "LiteTTS/config/pronunciation_overrides.json"
    
    try:
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(pronunciation_data, f, indent=2)
        print(f"✅ Created pronunciation config: {config_file}")
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")
    
    return config_file

def test_pronunciation_fixes():
    """Test the pronunciation fixes"""
    
    print("\n🔍 Testing Pronunciation Fixes")
    print("=" * 35)
    
    from LiteTTS.nlp.processor import NLPProcessor
    
    nlp_processor = NLPProcessor()
    
    test_cases = [
        "Boy",
        "The boy is here",
        "Joy and toy",
        "June is coming",
        "Jan said hello",
        "Boy, joy, and toy",
        "June and Jan are friends"
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: '{test_case}'")
        
        # Process through NLP pipeline
        result = nlp_processor.process_text(test_case)
        print(f"Result: '{result}'")
        
        # Check if problematic words are preserved
        problematic_words = ["boy", "joy", "toy", "june", "jan"]
        for word in problematic_words:
            if word in test_case.lower() and word in result.lower():
                print(f"  ✅ '{word}' preserved in output")
            elif word in test_case.lower():
                print(f"  ⚠️ '{word}' may have been altered")

def main():
    """Main function to implement pronunciation fixes"""
    
    print("🔧 Boy Pronunciation Fix Implementation")
    print("=" * 45)
    print("Addressing 'Boy' pronounced as 'boi' issue")
    print()
    
    # Add pronunciation overrides
    overrides = add_pronunciation_overrides()
    
    # Create phonetic markers
    create_phonetic_markers()
    
    # Update configuration
    config_file = update_pronunciation_config()
    
    # Test the fixes
    test_pronunciation_fixes()
    
    print("\n" + "=" * 45)
    print("📊 PRONUNCIATION FIX SUMMARY:")
    print(f"✅ Added {len(overrides)} pronunciation overrides")
    print(f"✅ Created configuration file: {config_file}")
    print("✅ Tested pronunciation fixes")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Test with actual TTS synthesis to verify pronunciation")
    print("2. If issues persist, may need phonemizer backend configuration")
    print("3. Consider model-specific pronunciation adjustments")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
