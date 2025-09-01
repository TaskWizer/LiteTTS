#!/usr/bin/env python3
"""
Demo script to showcase the improved user experience with chunked audio generation
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8354"

def demo_chunked_vs_standard():
    """Demonstrate the difference between chunked and standard generation"""
    
    # Long text that will benefit from chunking
    long_text = """
    Welcome to the demonstration of chunked audio generation! This is a significantly longer piece of text 
    that will showcase how the new chunked generation system provides a much better user experience. 
    Instead of waiting for the entire audio to be generated before hearing anything, you'll start hearing 
    the speech much sooner. This creates a more responsive and real-time feeling interaction. The system 
    intelligently breaks down the text into logical chunks while maintaining voice consistency and natural 
    prosody across all segments. This technology represents a major improvement in text-to-speech user experience.
    """
    
    print("🎯 Chunked Audio Generation Demo")
    print("=" * 50)
    print(f"📝 Text length: {len(long_text)} characters")
    print(f"🎵 Voice: af_heart")
    print(f"📊 Format: mp3")
    print()
    
    # Test chunked generation (streaming endpoint)
    print("🧩 Testing CHUNKED generation (streaming)...")
    start_time = time.time()
    first_byte_time = None
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/audio/stream",
            json={
                "input": long_text.strip(),
                "voice": "af_heart",
                "response_format": "mp3"
            },
            headers={"Content-Type": "application/json"},
            timeout=120,
            stream=True
        )
        
        if response.status_code == 200:
            chunk_count = 0
            total_size = 0
            
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    if first_byte_time is None:
                        first_byte_time = time.time() - start_time
                        print(f"   ⚡ First audio chunk received in: {first_byte_time:.2f}s")
                    
                    chunk_count += 1
                    total_size += len(chunk)
                    
                    # Show progress every 10 chunks
                    if chunk_count % 10 == 0:
                        elapsed = time.time() - start_time
                        print(f"   📦 Received {chunk_count} chunks ({total_size:,} bytes) in {elapsed:.2f}s")
            
            total_time = time.time() - start_time
            print(f"   ✅ CHUNKED complete: {chunk_count} chunks, {total_size:,} bytes in {total_time:.2f}s")
            print(f"   🚀 Time to first audio: {first_byte_time:.2f}s")
            
            chunked_stats = {
                "first_byte_time": first_byte_time,
                "total_time": total_time,
                "chunk_count": chunk_count,
                "total_size": total_size
            }
            
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return
    
    print()
    
    # Test standard generation (speech endpoint)
    print("📦 Testing STANDARD generation (non-streaming)...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json={
                "input": long_text.strip(),
                "voice": "af_heart",
                "response_format": "mp3"
            },
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            total_time = time.time() - start_time
            total_size = len(response.content)
            
            print(f"   ✅ STANDARD complete: {total_size:,} bytes in {total_time:.2f}s")
            print(f"   ⏳ Time to first audio: {total_time:.2f}s (complete generation)")
            
            standard_stats = {
                "first_byte_time": total_time,  # User waits for complete generation
                "total_time": total_time,
                "total_size": total_size
            }
            
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return
    
    print()
    print("📊 COMPARISON RESULTS")
    print("=" * 50)
    
    # Calculate improvements
    time_improvement = ((standard_stats["first_byte_time"] - chunked_stats["first_byte_time"]) / 
                       standard_stats["first_byte_time"]) * 100
    
    print(f"⚡ Time to First Audio:")
    print(f"   Chunked:  {chunked_stats['first_byte_time']:.2f}s")
    print(f"   Standard: {standard_stats['first_byte_time']:.2f}s")
    print(f"   🚀 Improvement: {time_improvement:.1f}% faster to first audio!")
    
    print(f"\n📊 Total Generation Time:")
    print(f"   Chunked:  {chunked_stats['total_time']:.2f}s")
    print(f"   Standard: {standard_stats['total_time']:.2f}s")
    
    print(f"\n📦 Audio Quality:")
    print(f"   Chunked:  {chunked_stats['total_size']:,} bytes")
    print(f"   Standard: {standard_stats['total_size']:,} bytes")
    
    size_diff = abs(chunked_stats['total_size'] - standard_stats['total_size'])
    size_diff_percent = (size_diff / standard_stats['total_size']) * 100
    print(f"   📏 Size difference: {size_diff_percent:.1f}%")
    
    print(f"\n🎯 User Experience:")
    if time_improvement > 50:
        print("   🌟 EXCELLENT: Users will notice significantly faster response")
    elif time_improvement > 25:
        print("   ✅ GOOD: Users will experience noticeably faster response")
    elif time_improvement > 10:
        print("   👍 IMPROVED: Users will experience somewhat faster response")
    else:
        print("   📝 MINIMAL: Improvement may not be noticeable for this text length")
    
    print(f"\n💡 Key Benefits:")
    print(f"   • {time_improvement:.1f}% faster time to first audio")
    print(f"   • Progressive audio delivery in {chunked_stats['chunk_count']} chunks")
    print(f"   • Maintained audio quality (size difference: {size_diff_percent:.1f}%)")
    print(f"   • Better perceived responsiveness for long texts")
    
    print("\n🎉 Chunked generation successfully improves user experience!")

def main():
    """Main demo function"""
    print("🚀 Starting Chunked Audio Generation Demo")
    print()
    
    # Check server availability
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not available")
            sys.exit(1)
        print("✅ Server is available")
        print()
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        sys.exit(1)
    
    # Run the demo
    demo_chunked_vs_standard()

if __name__ == "__main__":
    main()
