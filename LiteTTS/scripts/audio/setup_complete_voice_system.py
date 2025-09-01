#!/usr/bin/env python3
"""
Complete voice system setup script for Kokoro ONNX TTS API
Downloads all voices and tests the dynamic voice management system
"""

import sys
import logging
import time
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.voice.downloader import VoiceDownloader, DownloadProgress
from LiteTTS.voice.dynamic_manager import DynamicVoiceManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

def progress_callback(progress: DownloadProgress):
    """Enhanced progress callback for downloads"""
    bar_length = 30
    filled_length = int(bar_length * progress.percentage / 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    print(f"\r{progress.filename}: [{bar}] {progress.percentage:.1f}% "
          f"({progress.downloaded_bytes}/{progress.total_bytes} bytes) "
          f"@ {progress.speed_mbps:.1f} MB/s", end="", flush=True)

def download_all_voices():
    """Download all available voices from HuggingFace"""
    print("🌍 Downloading ALL voices from HuggingFace...")
    print("=" * 60)
    
    try:
        # Initialize voice manager
        voice_manager = DynamicVoiceManager()
        
        # Get current status
        stats = voice_manager.get_download_status()
        print(f"📊 Current Status:")
        print(f"   - Discovered voices: {stats['discovered_voices']}")
        print(f"   - Downloaded voices: {stats['downloaded_voices']}")
        print(f"   - Missing voices: {stats['missing_voices']}")
        
        if stats['missing_voices'] == 0:
            print("✅ All voices already downloaded!")
            return True
        
        # Estimate download size
        missing_voices = voice_manager.downloader.get_missing_voices()
        total_size_mb = 0
        for voice_name in missing_voices:
            voice_info = voice_manager.downloader.discovered_voices.get(voice_name)
            if voice_info:
                total_size_mb += voice_info.size / (1024 * 1024)
        
        print(f"\n📥 Will download {len(missing_voices)} voices (~{total_size_mb:.1f} MB)")
        
        # Confirm download
        response = input("\nProceed with download? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Download cancelled")
            return False
        
        # Download all voices
        print(f"\n🚀 Starting download of {len(missing_voices)} voices...")
        start_time = time.time()
        
        results = voice_manager.download_all_voices(progress_callback)
        
        print()  # New line after progress bars
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        download_time = time.time() - start_time
        
        print(f"\n✅ Download complete!")
        print(f"   - Success: {successful}/{total} voices")
        print(f"   - Time: {download_time:.1f} seconds")
        print(f"   - Average: {download_time/total:.1f}s per voice")
        
        if successful < total:
            print(f"\n❌ Failed downloads:")
            for voice, success in results.items():
                if not success:
                    print(f"   - {voice}")
        
        return successful == total
        
    except Exception as e:
        logger.error(f"Error during voice download: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_system():
    """Test the complete voice system"""
    print("\n🧪 Testing Voice System")
    print("=" * 40)
    
    try:
        # Initialize voice manager
        voice_manager = DynamicVoiceManager()
        
        # Test voice discovery
        available_voices = voice_manager.get_available_voices()
        print(f"✅ Available voices: {len(available_voices)}")
        
        # Test voice mappings
        mappings = voice_manager.get_voice_mappings()
        print(f"✅ Voice mappings: {len(mappings)}")
        
        # Test voice resolution
        test_voices = ["heart", "puck", "alloy", "alice", "af_heart"]
        print(f"\n🎯 Testing voice resolution:")
        for voice in test_voices:
            resolved = voice_manager.resolve_voice_name(voice)
            available = voice_manager.is_voice_available(voice)
            status = "✅" if available else "❌"
            print(f"   {voice} -> {resolved} {status}")
        
        # Test download status
        download_info = voice_manager.downloader.get_download_info()
        downloaded_count = sum(1 for info in download_info.values() if info['downloaded'])
        print(f"\n📊 Download status: {downloaded_count}/{len(download_info)} voices downloaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice system test failed: {e}")
        return False

def show_voice_summary():
    """Show comprehensive voice system summary"""
    print("\n📋 Voice System Summary")
    print("=" * 40)
    
    try:
        voice_manager = DynamicVoiceManager()
        
        # Discovery stats
        stats = voice_manager.get_download_status()
        print(f"🔍 Discovery:")
        print(f"   - Total discovered: {stats['discovered_voices']}")
        print(f"   - Downloaded: {stats['downloaded_voices']}")
        print(f"   - Missing: {stats['missing_voices']}")
        print(f"   - Voice mappings: {stats['voice_mappings']}")
        
        # Voice categories
        downloaded_voices = voice_manager.downloader.get_downloaded_voices()
        categories = {}
        for voice in downloaded_voices:
            if '_' in voice:
                prefix = voice.split('_')[0]
                if prefix not in categories:
                    categories[prefix] = []
                categories[prefix].append(voice)
        
        print(f"\n🎭 Voice Categories:")
        for category, voices in sorted(categories.items()):
            category_name = {
                'af': 'American Female',
                'am': 'American Male', 
                'bf': 'British Female',
                'bm': 'British Male',
                'jf': 'Japanese Female',
                'jm': 'Japanese Male',
                'zf': 'Chinese Female',
                'zm': 'Chinese Male',
                'ef': 'European Female',
                'em': 'European Male',
                'hf': 'Hindi Female',
                'hm': 'Hindi Male',
                'if': 'Italian Female',
                'im': 'Italian Male',
                'pf': 'Portuguese Female',
                'pm': 'Portuguese Male',
                'ff': 'French Female'
            }.get(category, category.upper())
            
            print(f"   {category_name}: {len(voices)} voices")
        
        # Voice mappings
        mappings = voice_manager.get_voice_mappings()
        if mappings:
            print(f"\n🔗 Short Name Mappings:")
            for short, full in sorted(mappings.items()):
                print(f"   {short} -> {full}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to show summary: {e}")
        return False

def main():
    """Main function"""
    print("🎵 Kokoro TTS Complete Voice System Setup")
    print("=" * 60)
    
    # Test current system
    if not test_voice_system():
        print("❌ Voice system test failed")
        return 1
    
    # Show current summary
    show_voice_summary()
    
    # Ask about downloading all voices
    print(f"\n🤔 Options:")
    print("1. Download all missing voices")
    print("2. Show detailed voice information")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        success = download_all_voices()
        if success:
            print("\n🎉 All voices downloaded successfully!")
            show_voice_summary()
        else:
            print("\n❌ Some voices failed to download")
            return 1
    
    elif choice == "2":
        # Show detailed information
        voice_manager = DynamicVoiceManager()
        download_info = voice_manager.downloader.get_download_info()
        
        print(f"\n📋 Detailed Voice Information:")
        for voice_name, info in sorted(download_info.items()):
            status = "✅ Downloaded" if info['downloaded'] else "❌ Missing"
            size_mb = info['file_size'] / (1024 * 1024) if info['file_size'] > 0 else 0
            expected_mb = info['expected_size'] / (1024 * 1024) if info['expected_size'] > 0 else 0
            
            print(f"\n   {voice_name}: {status}")
            if info['downloaded']:
                print(f"      Local size: {size_mb:.1f} MB")
                print(f"      Path: {info['local_path']}")
            else:
                print(f"      Expected size: {expected_mb:.1f} MB")
                print(f"      Download URL: {info['remote_url']}")
    
    elif choice == "3":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
