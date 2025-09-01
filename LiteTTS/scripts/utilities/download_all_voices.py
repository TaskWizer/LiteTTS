#!/usr/bin/env python3
"""
Script to download all available voices from HuggingFace
"""

import sys
import logging
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
    """Progress callback for downloads"""
    print(f"\r{progress.filename}: {progress.percentage:.1f}% "
          f"({progress.downloaded_bytes}/{progress.total_bytes} bytes) "
          f"@ {progress.speed_mbps:.1f} MB/s", end="", flush=True)

def main():
    """Main function to download all voices"""
    print("🎵 Kokoro TTS Voice Downloader")
    print("=" * 50)
    
    try:
        # Initialize voice manager
        print("📦 Initializing voice manager...")
        voice_manager = DynamicVoiceManager()
        
        # Get discovery stats
        stats = voice_manager.get_download_status()
        print(f"📊 Discovery Stats:")
        print(f"   - Discovered voices: {stats['discovered_voices']}")
        print(f"   - Downloaded voices: {stats['downloaded_voices']}")
        print(f"   - Missing voices: {stats['missing_voices']}")
        print(f"   - Voice mappings: {stats['voice_mappings']}")
        
        # Show available voices
        available_voices = voice_manager.downloader.get_available_voice_names()
        print(f"\n🎭 Available voices ({len(available_voices)}):")
        for i, voice in enumerate(available_voices, 1):
            status = "✅" if voice_manager.downloader.is_voice_downloaded(voice) else "❌"
            print(f"   {i:2d}. {voice} {status}")
        
        # Ask user what to download
        print(f"\n📥 Download Options:")
        print("1. Download all voices (~26MB)")
        print("2. Download default voices only (af_heart, am_puck)")
        print("3. Download specific voices")
        print("4. Show download info and exit")
        print("5. Refresh discovery and exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n🚀 Downloading all voices...")
            results = voice_manager.download_all_voices(progress_callback)
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            print(f"\n✅ Download complete: {successful}/{total} voices downloaded successfully")
            
            if successful < total:
                print("\n❌ Failed downloads:")
                for voice, success in results.items():
                    if not success:
                        print(f"   - {voice}")
        
        elif choice == "2":
            print("\n🚀 Downloading default voices...")
            results = voice_manager.downloader.download_default_voices(progress_callback)
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            print(f"\n✅ Download complete: {successful}/{total} default voices downloaded")
        
        elif choice == "3":
            print("\n📝 Available voices:")
            for i, voice in enumerate(available_voices, 1):
                status = "✅" if voice_manager.downloader.is_voice_downloaded(voice) else "❌"
                print(f"   {i:2d}. {voice} {status}")
            
            voice_input = input("\nEnter voice names (comma-separated): ").strip()
            if voice_input:
                voice_names = [v.strip() for v in voice_input.split(",")]
                
                print(f"\n🚀 Downloading {len(voice_names)} voices...")
                results = {}
                for voice_name in voice_names:
                    if voice_name in available_voices:
                        print(f"\nDownloading {voice_name}...")
                        results[voice_name] = voice_manager.downloader.download_voice(voice_name, progress_callback)
                        print()  # New line after progress
                    else:
                        print(f"❌ Voice '{voice_name}' not found")
                        results[voice_name] = False
                
                successful = sum(1 for success in results.values() if success)
                total = len(results)
                print(f"\n✅ Download complete: {successful}/{total} voices downloaded")
        
        elif choice == "4":
            print("\n📊 Download Information:")
            download_info = voice_manager.downloader.get_download_info()
            
            for voice_name, info in download_info.items():
                status = "✅ Downloaded" if info['downloaded'] else "❌ Missing"
                size_mb = info['file_size'] / (1024 * 1024) if info['file_size'] > 0 else 0
                expected_mb = info['expected_size'] / (1024 * 1024) if info['expected_size'] > 0 else 0
                
                print(f"   {voice_name}: {status}")
                if info['downloaded']:
                    print(f"      Size: {size_mb:.1f} MB")
                else:
                    print(f"      Expected: {expected_mb:.1f} MB")
                    print(f"      URL: {info['remote_url']}")
        
        elif choice == "5":
            print("\n🔄 Refreshing voice discovery...")
            success = voice_manager.refresh_discovery()
            if success:
                new_stats = voice_manager.get_download_status()
                print(f"✅ Discovery refreshed!")
                print(f"   - Discovered voices: {new_stats['discovered_voices']}")
                print(f"   - Voice mappings: {new_stats['voice_mappings']}")
            else:
                print("❌ Failed to refresh discovery")
        
        else:
            print("❌ Invalid choice")
            return 1
        
        # Final stats
        final_stats = voice_manager.get_download_status()
        print(f"\n📈 Final Stats:")
        print(f"   - Total discovered: {final_stats['discovered_voices']}")
        print(f"   - Total downloaded: {final_stats['downloaded_voices']}")
        print(f"   - Voice mappings: {final_stats['voice_mappings']}")
        
        # Show voice mappings
        mappings = voice_manager.get_voice_mappings()
        if mappings:
            print(f"\n🔗 Voice Mappings ({len(mappings)}):")
            for short, full in sorted(mappings.items()):
                print(f"   {short} -> {full}")
        
        print("\n🎉 Voice management complete!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Download interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error during voice download: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
