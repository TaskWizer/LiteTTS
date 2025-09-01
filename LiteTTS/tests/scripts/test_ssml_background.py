#!/usr/bin/env python3
"""
Test SSML Background Functionality

Tests the SSML background noise enhancement feature end-to-end.
"""

import requests
import time
import os
from mutagen.mp3 import MP3

def test_ssml_background():
    """Test SSML background functionality"""
    
    print("🎵 Testing SSML Background Functionality")
    print("=" * 45)
    
    # Test cases with different background types
    test_cases = [
        {
            "name": "Nature Background",
            "ssml": '<speak><background type="nature" volume="20">Hello world, this is a test with nature sounds in the background.</background></speak>',
            "expected_duration": 4.0
        },
        {
            "name": "Rain Background", 
            "ssml": '<speak><background type="rain" volume="15">The rain is falling gently while I speak these words.</background></speak>',
            "expected_duration": 3.5
        },
        {
            "name": "Coffee Shop Background",
            "ssml": '<speak><background type="coffee_shop" volume="25">Welcome to our cozy coffee shop where conversations blend with ambient sounds.</background></speak>',
            "expected_duration": 5.0
        },
        {
            "name": "No Background (Control)",
            "ssml": '<speak>This is a control test without any background sounds.</speak>',
            "expected_duration": 3.0
        },
        {
            "name": "Plain Text (Control)",
            "ssml": 'This is plain text without SSML markup.',
            "expected_duration": 2.5
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🔍 Test {i+1}: {test_case['name']}")
        print(f"   SSML: {test_case['ssml'][:60]}{'...' if len(test_case['ssml']) > 60 else ''}")
        
        # Make TTS request
        payload = {
            "input": test_case['ssml'],
            "voice": "af_heart",
            "response_format": "mp3"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8354/v1/audio/speech",
                json=payload,
                timeout=30
            )
            request_time = time.time() - start_time
            
            if response.status_code != 200:
                print(f"   ❌ Request failed: HTTP {response.status_code}")
                results.append({
                    "test": test_case['name'],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                continue
            
            # Save and analyze audio
            filename = f"ssml_test_{i+1}_{test_case['name'].lower().replace(' ', '_')}.mp3"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            # Get audio duration
            audio = MP3(filename)
            duration = audio.info.length
            file_size = len(response.content)
            
            print(f"   ✅ Generated: {duration:.2f}s audio, {file_size} bytes")
            print(f"   ⏱️ Request time: {request_time:.2f}s")
            
            # Check if duration is reasonable
            duration_ok = duration >= (test_case['expected_duration'] * 0.7)  # Allow 30% variance
            
            if duration_ok:
                print(f"   ✅ Duration check passed")
            else:
                print(f"   ⚠️ Duration shorter than expected ({test_case['expected_duration']}s)")
            
            results.append({
                "test": test_case['name'],
                "success": True,
                "duration": duration,
                "expected_duration": test_case['expected_duration'],
                "file_size": file_size,
                "request_time": request_time,
                "duration_ok": duration_ok,
                "filename": filename
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "test": test_case['name'],
                "success": False,
                "error": str(e)
            })
    
    # Generate summary
    print("\n" + "=" * 45)
    print("📊 SSML BACKGROUND TEST SUMMARY")
    print("=" * 45)
    
    successful_tests = [r for r in results if r.get('success', False)]
    failed_tests = [r for r in results if not r.get('success', False)]
    
    print(f"✅ Successful tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed tests: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        print("\n📈 Successful Test Details:")
        for result in successful_tests:
            duration_status = "✅" if result.get('duration_ok', False) else "⚠️"
            print(f"  {duration_status} {result['test']}: {result['duration']:.2f}s")
    
    if failed_tests:
        print("\n❌ Failed Test Details:")
        for result in failed_tests:
            print(f"  ❌ {result['test']}: {result.get('error', 'Unknown error')}")
    
    # Check for SSML background functionality
    background_tests = [r for r in successful_tests if 'background' in r['test'].lower() and r['test'] != 'No Background (Control)']
    control_tests = [r for r in successful_tests if 'control' in r['test'].lower()]
    
    if background_tests and control_tests:
        avg_bg_duration = sum(r['duration'] for r in background_tests) / len(background_tests)
        avg_control_duration = sum(r['duration'] for r in control_tests) / len(control_tests)
        
        print(f"\n🎯 Background Analysis:")
        print(f"   Average background test duration: {avg_bg_duration:.2f}s")
        print(f"   Average control test duration: {avg_control_duration:.2f}s")
        
        if avg_bg_duration > avg_control_duration * 0.8:  # Background tests should be similar duration
            print(f"   ✅ Background processing appears to be working")
        else:
            print(f"   ⚠️ Background tests significantly shorter - may indicate processing issues")
    
    return len(failed_tests) == 0

if __name__ == "__main__":
    success = test_ssml_background()
    exit(0 if success else 1)
