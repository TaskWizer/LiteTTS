#!/usr/bin/env python3
"""
Test script for dynamic voice management system
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.voice import get_available_voices, resolve_voice_name, get_voice_manager
from LiteTTS.voice.dynamic_manager import DynamicVoiceManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

def test_voice_discovery():
    """Test voice discovery functionality"""
    print("🔍 Testing Voice Discovery")
    print("-" * 30)
    
    try:
        # Test voice manager initialization
        voice_manager = DynamicVoiceManager()
        print(f"✅ Voice manager initialized")
        
        # Test discovery stats
        stats = voice_manager.get_download_status()
        print(f"📊 Discovery Stats:")
        print(f"   - Discovered voices: {stats['discovered_voices']}")
        print(f"   - Downloaded voices: {stats['downloaded_voices']}")
        print(f"   - Missing voices: {stats['missing_voices']}")
        print(f"   - Voice mappings: {stats['voice_mappings']}")
        
        # Test available voices
        available_voices = voice_manager.get_available_voices()
        print(f"🎭 Available voices ({len(available_voices)}):")
        for voice in available_voices[:10]:  # Show first 10
            print(f"   - {voice}")
        if len(available_voices) > 10:
            print(f"   ... and {len(available_voices) - 10} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice discovery test failed: {e}")
        return False

def test_voice_mappings():
    """Test voice name mapping functionality"""
    print("\n🔗 Testing Voice Mappings")
    print("-" * 30)
    
    try:
        voice_manager = DynamicVoiceManager()
        
        # Test voice mappings
        mappings = voice_manager.get_voice_mappings()
        print(f"📝 Voice mappings ({len(mappings)}):")
        for short, full in list(mappings.items())[:10]:  # Show first 10
            print(f"   {short} -> {full}")
        if len(mappings) > 10:
            print(f"   ... and {len(mappings) - 10} more")
        
        # Test voice resolution
        test_voices = ["heart", "puck", "alloy", "af_heart", "am_liam", "nonexistent"]
        print(f"\n🎯 Testing voice resolution:")
        for voice in test_voices:
            resolved = voice_manager.resolve_voice_name(voice)
            available = voice_manager.is_voice_available(voice)
            status = "✅" if available else "❌"
            print(f"   {voice} -> {resolved} {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice mapping test failed: {e}")
        return False

def test_module_functions():
    """Test module-level functions"""
    print("\n🔧 Testing Module Functions")
    print("-" * 30)
    
    try:
        # Test get_available_voices function
        voices = get_available_voices()
        print(f"✅ get_available_voices(): {len(voices)} voices")
        
        # Test resolve_voice_name function
        test_names = ["heart", "af_heart", "puck", "nonexistent"]
        print(f"🎯 Testing resolve_voice_name():")
        for name in test_names:
            resolved = resolve_voice_name(name)
            print(f"   {name} -> {resolved}")
        
        # Test get_voice_manager function
        manager = get_voice_manager()
        if manager:
            print(f"✅ get_voice_manager(): {type(manager).__name__}")
        else:
            print(f"❌ get_voice_manager(): None")
        
        return True
        
    except Exception as e:
        print(f"❌ Module function test failed: {e}")
        return False

def test_huggingface_discovery():
    """Test HuggingFace discovery functionality"""
    print("\n🌐 Testing HuggingFace Discovery")
    print("-" * 30)
    
    try:
        voice_manager = DynamicVoiceManager()
        
        # Test discovery refresh
        print("🔄 Testing discovery refresh...")
        success = voice_manager.refresh_discovery()
        if success:
            print("✅ Discovery refresh successful")
        else:
            print("❌ Discovery refresh failed")
        
        # Test discovered voices from HuggingFace
        discovered = voice_manager.downloader.discovered_voices
        print(f"📦 HuggingFace discovered voices: {len(discovered)}")
        
        # Show some examples
        for i, (name, info) in enumerate(list(discovered.items())[:5]):
            size_mb = info.size / (1024 * 1024) if info.size > 0 else 0
            print(f"   {i+1}. {name} ({size_mb:.1f} MB)")
        
        if len(discovered) > 5:
            print(f"   ... and {len(discovered) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"❌ HuggingFace discovery test failed: {e}")
        return False

def test_download_functionality():
    """Test voice download functionality (without actually downloading)"""
    print("\n📥 Testing Download Functionality")
    print("-" * 30)
    
    try:
        voice_manager = DynamicVoiceManager()
        
        # Test download status
        download_info = voice_manager.downloader.get_download_info()
        downloaded_count = sum(1 for info in download_info.values() if info['downloaded'])
        total_count = len(download_info)
        
        print(f"📊 Download status: {downloaded_count}/{total_count} voices downloaded")
        
        # Show download info for a few voices
        print(f"📋 Sample download info:")
        for i, (name, info) in enumerate(list(download_info.items())[:5]):
            status = "✅ Downloaded" if info['downloaded'] else "❌ Missing"
            size_mb = info['file_size'] / (1024 * 1024) if info['file_size'] > 0 else 0
            expected_mb = info['expected_size'] / (1024 * 1024) if info['expected_size'] > 0 else 0
            
            print(f"   {i+1}. {name}: {status}")
            if info['downloaded']:
                print(f"      Size: {size_mb:.1f} MB")
            else:
                print(f"      Expected: {expected_mb:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Download functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Dynamic Voice Management System Tests")
    print("=" * 50)
    
    tests = [
        test_voice_discovery,
        test_voice_mappings,
        test_module_functions,
        test_huggingface_discovery,
        test_download_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
