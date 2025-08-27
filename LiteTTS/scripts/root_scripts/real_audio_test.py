#!/usr/bin/env python3
"""
REAL audio test - tests what the system ACTUALLY generates for audio
This will generate actual audio files and show what text processing is happening
"""

import requests
import json
import time
import os

def test_real_audio_generation():
    """Test actual audio generation with problematic words"""
    print("🎵 REAL AUDIO GENERATION TEST")
    print("=" * 60)
    
    api_url = "http://localhost:8354/v1/audio/speech"
    
    # Test the exact words that were problematic
    test_cases = [
        ("TSLA", "Should be pronounced as 'TESLA' not 'T-S-L-A'"),
        ("API", "Should be pronounced as 'API' not 'A-P-I'"),
        ("CEO", "Should be pronounced as 'CEO' not 'C-E-O'"),
        ("question", "Should be pronounced naturally, not 'quesʃən'"),
        ("pronunciation", "Should be pronounced naturally, not 'pro-NUN-see-AY-shun'"),
        ("hello", "Should be pronounced naturally"),
        ("The API is working correctly", "Full sentence test"),
        ("TSLA stock price is rising", "Full sentence with ticker"),
        ("I have a question about pronunciation", "Full sentence with problematic words")
    ]
    
    results = []
    
    for i, (text, expectation) in enumerate(test_cases):
        print(f"\n--- Test {i+1}: {text} ---")
        print(f"Expected: {expectation}")
        
        try:
            start_time = time.time()
            
            response = requests.post(api_url, 
                headers={'Content-Type': 'application/json'},
                json={
                    'model': 'kokoro',
                    'input': text,
                    'voice': 'af_heart',
                    'response_format': 'mp3'
                },
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                # Save the audio file
                filename = f'real_test_{i+1}_{text.replace(" ", "_").replace(".", "")[:20]}.mp3'
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                audio_size = len(response.content)
                print(f"✅ SUCCESS: Generated {filename}")
                print(f"   Audio size: {audio_size} bytes")
                print(f"   Response time: {response_time:.3f}s")
                
                results.append({
                    'text': text,
                    'filename': filename,
                    'success': True,
                    'audio_size': audio_size,
                    'response_time': response_time
                })
                
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
                results.append({
                    'text': text,
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                })
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results.append({
                'text': text,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 REAL AUDIO TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    
    print("\n📁 Generated Audio Files:")
    for result in results:
        if result['success']:
            print(f"  ✅ {result['filename']} - {result['text']}")
        else:
            print(f"  ❌ FAILED - {result['text']}: {result['error']}")
    
    print("\n🎧 MANUAL VERIFICATION REQUIRED:")
    print("Listen to each audio file to verify:")
    print("1. No letter-by-letter spelling (T-S-L-A, A-P-I, C-E-O)")
    print("2. No IPA symbols or weird pronunciations")
    print("3. Natural, clear pronunciation")
    print("4. Proper word stress and intonation")
    
    if successful == total:
        print("\n🎉 ALL TESTS PASSED - Audio generation working!")
    else:
        print(f"\n⚠️  {total - successful} TESTS FAILED - Check errors above")
    
    return results

def test_server_health():
    """Test if the server is responding"""
    try:
        response = requests.get("http://localhost:8354/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy and responding")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server is not responding: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 REAL AUDIO GENERATION TEST")
    print("Testing what the system ACTUALLY generates for audio")
    print("=" * 60)
    
    # Check server health first
    if not test_server_health():
        print("❌ Cannot proceed - server is not responding")
        return
    
    # Run the real audio tests
    results = test_real_audio_generation()
    
    print("\n" + "=" * 60)
    print("🎯 TEST COMPLETE")
    print("=" * 60)
    print("This test generated REAL audio files that you can listen to.")
    print("Compare these with your previous audio to verify the fixes work.")
    print("The proof is in the audio - listen and verify!")

if __name__ == "__main__":
    main()
