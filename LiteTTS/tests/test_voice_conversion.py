#!/usr/bin/env python3
"""
Test voice conversion from .pt to .bin format
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.voice.downloader import VoiceDownloader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

def test_voice_discovery():
    """Test voice discovery from HuggingFace"""
    print("🔍 Testing voice discovery...")

    try:
        downloader = VoiceDownloader()

        # Discovery happens automatically in __init__
        discovered_count = len(downloader.discovered_voices)
        print(f"Discovered voices: {discovered_count}")

        # Show first 10 voices
        voice_names = list(downloader.discovered_voices.keys())[:10]
        print(f"Sample voices: {voice_names}")

        return discovered_count > 0

    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        return False

def test_voice_download_and_conversion():
    """Test downloading and converting a single voice"""
    print("\n📥 Testing voice download and conversion...")
    
    try:
        downloader = VoiceDownloader()
        
        # Ensure discovery is done
        if not downloader.discovered_voices:
            downloader.discover_voices()
        
        # Test with af_heart voice
        test_voice = "af_heart"
        if test_voice not in downloader.discovered_voices:
            print(f"❌ Test voice {test_voice} not found in discovered voices")
            return False
        
        print(f"Testing download and conversion of: {test_voice}")
        
        # Download and convert
        success = downloader.download_voice(test_voice)
        print(f"Download success: {success}")
        
        if success:
            # Check if .bin file was created
            bin_path = Path("LiteTTS/voices") / f"{test_voice}.bin"
            pt_path = Path("LiteTTS/voices") / f"{test_voice}.pt"
            
            print(f".pt file exists: {pt_path.exists()}")
            print(f".bin file exists: {bin_path.exists()}")
            
            if bin_path.exists():
                # Check file size
                bin_size = bin_path.stat().st_size
                expected_size = 510 * 256 * 4  # float32
                print(f".bin file size: {bin_size} bytes (expected: {expected_size})")
                
                if bin_size == expected_size:
                    print("✅ Voice conversion successful!")
                    return True
                else:
                    print("❌ Voice file has incorrect size")
                    return False
            else:
                print("❌ .bin file was not created")
                return False
        else:
            print("❌ Download failed")
            return False
            
    except Exception as e:
        print(f"❌ Download/conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_validation():
    """Test voice file validation"""
    print("\n🔍 Testing voice file validation...")
    
    try:
        downloader = VoiceDownloader()
        
        # Test validation of existing .bin file
        test_voice = "af_heart"
        bin_path = Path("LiteTTS/voices") / f"{test_voice}.bin"
        
        if bin_path.exists():
            is_valid = downloader._validate_bin_file(bin_path)
            print(f"Voice file validation: {is_valid}")
            return is_valid
        else:
            print("❌ No .bin file to validate")
            return False
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def test_voice_combiner_integration():
    """Test integration with voice combiner"""
    print("\n🔧 Testing voice combiner integration...")
    
    try:
        from LiteTTS.voice.combiner import VoiceCombiner
        
        combiner = VoiceCombiner()
        
        # Check available voices
        voice_files = combiner.get_voice_list()
        print(f"Voice files found: {len(voice_files)}")

        if voice_files:
            print(f"Sample voice files: {voice_files[:5]}")
            
            # Test combining
            print("Testing voice combination...")
            success = combiner.combine_voices()
            print(f"Voice combination success: {success}")
            
            if success:
                # Check if combined file exists
                combined_file = combiner.combined_file
                npz_file = combined_file.with_suffix('.npz')
                
                print(f"Combined file exists: {combined_file.exists()}")
                print(f"NPZ file exists: {npz_file.exists()}")
                
                return npz_file.exists() or combined_file.exists()
            else:
                return False
        else:
            print("❌ No voice files found for combination")
            return False
            
    except Exception as e:
        print(f"❌ Voice combiner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all voice conversion tests"""
    print("🧪 Voice Conversion Test Suite")
    print("=" * 50)
    
    # Test 1: Voice discovery
    discovery_ok = test_voice_discovery()
    
    # Test 2: Download and conversion
    download_ok = test_voice_download_and_conversion()
    
    # Test 3: Validation
    validation_ok = test_voice_validation()
    
    # Test 4: Combiner integration
    combiner_ok = test_voice_combiner_integration()
    
    # Summary
    print("\n📊 Test Results:")
    print(f"   Voice Discovery: {'✅ PASS' if discovery_ok else '❌ FAIL'}")
    print(f"   Download & Convert: {'✅ PASS' if download_ok else '❌ FAIL'}")
    print(f"   File Validation: {'✅ PASS' if validation_ok else '❌ FAIL'}")
    print(f"   Combiner Integration: {'✅ PASS' if combiner_ok else '❌ FAIL'}")
    
    all_passed = all([discovery_ok, download_ok, validation_ok, combiner_ok])
    
    if all_passed:
        print("\n🎉 All tests passed! Voice conversion system is working correctly.")
    else:
        print("\n❌ Some tests failed. Voice conversion system needs fixes.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
