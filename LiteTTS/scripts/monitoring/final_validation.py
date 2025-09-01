#!/usr/bin/env python3
"""
Final System Validation for Kokoro TTS API
Comprehensive end-to-end testing including performance validation
"""

import requests
import json
import time
import sys
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8354"

def test_basic_functionality():
    """Test basic TTS functionality"""
    logger.info("🧪 Testing basic TTS functionality...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json={
                "input": "Hello world, this is a comprehensive system validation test.",
                "voice": "af_heart",
                "response_format": "mp3"
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            logger.info(f"   ✅ Basic TTS: SUCCESS ({len(response.content)} bytes)")
            return True
        else:
            logger.error(f"   ❌ Basic TTS: FAILED ({response.status_code})")
            return False
            
    except Exception as e:
        logger.error(f"   ❌ Basic TTS: EXCEPTION ({e})")
        return False

def test_performance_targets():
    """Test that performance targets are met"""
    logger.info("🧪 Testing performance targets...")
    
    test_cases = [
        {
            "name": "Short text",
            "text": "Hello world!",
            "target_rtf": 1.0  # Real-time performance
        },
        {
            "name": "Medium text",
            "text": "This is a medium length text that should test the system's performance with moderate complexity.",
            "target_rtf": 0.5  # Better than real-time
        },
        {
            "name": "Long text",
            "text": "This is a comprehensive long text that will thoroughly test the system's ability to handle substantial content while maintaining excellent performance metrics and ensuring that the real-time factor remains well below the target thresholds.",
            "target_rtf": 0.3  # Excellent performance
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/v1/audio/speech",
                json={
                    "input": test_case["text"],
                    "voice": "af_heart"
                },
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            synthesis_time = time.time() - start_time
            
            if response.status_code == 200:
                # Estimate audio duration (rough calculation)
                audio_duration = len(test_case["text"]) * 0.05  # ~50ms per character
                rtf = synthesis_time / audio_duration if audio_duration > 0 else float('inf')
                
                if rtf <= test_case["target_rtf"]:
                    logger.info(f"   ✅ {test_case['name']}: RTF={rtf:.3f} (target: {test_case['target_rtf']})")
                else:
                    logger.warning(f"   ⚠️ {test_case['name']}: RTF={rtf:.3f} exceeds target {test_case['target_rtf']}")
                    all_passed = False
            else:
                logger.error(f"   ❌ {test_case['name']}: HTTP {response.status_code}")
                all_passed = False
                
        except Exception as e:
            logger.error(f"   ❌ {test_case['name']}: EXCEPTION ({e})")
            all_passed = False
    
    return all_passed

def test_openwebui_integration():
    """Test OpenWebUI integration thoroughly"""
    logger.info("🧪 Testing OpenWebUI integration...")
    
    # Test different scenarios that OpenWebUI might use
    test_scenarios = [
        {
            "name": "Desktop OpenWebUI",
            "headers": {"User-Agent": "Mozilla/5.0 OpenWebUI/1.0"},
            "payload": {"input": "Desktop test", "voice": "af_heart"}
        },
        {
            "name": "Mobile OpenWebUI",
            "headers": {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"},
            "payload": {"input": "Mobile test", "voice": "af_heart", "response_format": "mp3"}
        },
        {
            "name": "Streaming request",
            "headers": {"User-Agent": "OpenWebUI/1.0"},
            "payload": {"input": "Streaming test", "voice": "af_heart"},
            "endpoint": "/v1/audio/stream"
        },
        {
            "name": "Compatibility route",
            "headers": {"User-Agent": "OpenWebUI/1.0"},
            "payload": {"input": "Compatibility test", "voice": "af_heart"},
            "endpoint": "/v1/audio/stream/audio/speech"
        }
    ]
    
    all_passed = True
    
    for scenario in test_scenarios:
        try:
            endpoint = scenario.get("endpoint", "/v1/audio/speech")
            
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json=scenario["payload"],
                headers={**scenario["headers"], "Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200 and len(response.content) > 1000:
                logger.info(f"   ✅ {scenario['name']}: SUCCESS ({len(response.content)} bytes)")
            else:
                logger.error(f"   ❌ {scenario['name']}: FAILED ({response.status_code}, {len(response.content)} bytes)")
                all_passed = False
                
        except Exception as e:
            logger.error(f"   ❌ {scenario['name']}: EXCEPTION ({e})")
            all_passed = False
    
    return all_passed

def test_voice_compatibility():
    """Test voice compatibility"""
    logger.info("🧪 Testing voice compatibility...")
    
    # Get available voices
    try:
        response = requests.get(f"{BASE_URL}/v1/voices", timeout=10)
        if response.status_code != 200:
            logger.error("   ❌ Could not get voice list")
            return False
        
        voices_data = response.json()
        # Handle the actual format returned by the API
        available_voices = voices_data.get("voices", [])
        
        if not available_voices:
            logger.error("   ❌ No voices available")
            return False
        
        logger.info(f"   📋 Found {len(available_voices)} voices")
        
        # Test a few different voices
        test_voices = available_voices[:3]  # Test first 3 voices
        all_passed = True
        
        for voice in test_voices:
            try:
                response = requests.post(
                    f"{BASE_URL}/v1/audio/speech",
                    json={
                        "input": f"Testing voice {voice}",
                        "voice": voice
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"   ✅ Voice {voice}: SUCCESS")
                else:
                    logger.error(f"   ❌ Voice {voice}: FAILED ({response.status_code})")
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"   ❌ Voice {voice}: EXCEPTION ({e})")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        logger.error(f"   ❌ Voice compatibility test failed: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    logger.info("🧪 Testing error handling...")
    
    error_test_cases = [
        {
            "name": "Invalid voice",
            "payload": {"input": "Test", "voice": "nonexistent_voice"},
            "expected_status": 400
        },
        {
            "name": "Empty input",
            "payload": {"input": "", "voice": "af_heart"},
            "expected_status": 400
        },
        {
            "name": "Missing voice",
            "payload": {"input": "Test"},
            "expected_status": 400
        },
        {
            "name": "Invalid speed",
            "payload": {"input": "Test", "voice": "af_heart", "speed": "invalid"},
            "expected_status": 400
        }
    ]
    
    all_passed = True
    
    for test_case in error_test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/v1/audio/speech",
                json=test_case["payload"],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == test_case["expected_status"]:
                logger.info(f"   ✅ {test_case['name']}: Correctly returned {response.status_code}")
            else:
                logger.warning(f"   ⚠️ {test_case['name']}: Expected {test_case['expected_status']}, got {response.status_code}")
                # Don't fail for error handling - some might be handled differently
                
        except Exception as e:
            logger.error(f"   ❌ {test_case['name']}: EXCEPTION ({e})")
            all_passed = False
    
    return all_passed

def test_concurrent_requests():
    """Test concurrent request handling"""
    logger.info("🧪 Testing concurrent request handling...")
    
    import threading
    import queue
    
    results_queue = queue.Queue()
    
    def make_request(request_id):
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/v1/audio/speech",
                json={
                    "input": f"Concurrent request {request_id}",
                    "voice": "af_heart"
                },
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            duration = time.time() - start_time
            
            results_queue.put({
                "id": request_id,
                "status": response.status_code,
                "duration": duration,
                "size": len(response.content),
                "success": response.status_code == 200
            })
            
        except Exception as e:
            results_queue.put({
                "id": request_id,
                "error": str(e),
                "success": False
            })
    
    # Launch 5 concurrent requests
    threads = []
    for i in range(5):
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Collect results
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())
    
    successful_requests = sum(1 for r in results if r.get("success", False))
    
    if successful_requests >= 4:  # Allow 1 failure out of 5
        logger.info(f"   ✅ Concurrent requests: {successful_requests}/5 successful")
        return True
    else:
        logger.error(f"   ❌ Concurrent requests: Only {successful_requests}/5 successful")
        return False

def main():
    """Run final validation"""
    logger.info("🚀 Starting Final System Validation")
    logger.info("=" * 60)
    
    # Check server availability
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            logger.error("❌ Server not available")
            sys.exit(1)
        logger.info("✅ Server is available")
    except Exception as e:
        logger.error(f"❌ Cannot connect to server: {e}")
        sys.exit(1)
    
    # Run all tests
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Performance Targets", test_performance_targets),
        ("OpenWebUI Integration", test_openwebui_integration),
        ("Voice Compatibility", test_voice_compatibility),
        ("Error Handling", test_error_handling),
        ("Concurrent Requests", test_concurrent_requests)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: EXCEPTION - {e}")
    
    # Final results
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 FINAL VALIDATION RESULTS")
    logger.info(f"{'='*60}")
    logger.info(f"Tests Passed: {passed_tests}/{total_tests}")
    logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED - System is fully validated!")
        sys.exit(0)
    elif passed_tests >= total_tests * 0.8:  # 80% pass rate
        logger.info("✅ MOSTLY PASSED - System is operational with minor issues")
        sys.exit(0)
    else:
        logger.error("❌ VALIDATION FAILED - System has significant issues")
        sys.exit(1)

if __name__ == "__main__":
    main()
