#!/usr/bin/env python3
"""
Test script for time-stretching feature
"""

import requests
import json
import time
from pathlib import Path

def test_time_stretching_api():
    """Test time-stretching via API"""
    base_url = "http://localhost:9876"  # Using override.json port
    
    test_text = "This is a test of the time-stretching optimization feature. It should generate audio faster and then correct the playback speed."
    
    # Test cases
    test_cases = [
        {
            "name": "baseline_no_stretching",
            "params": {
                "input": test_text,
                "voice": "af_heart",
                "response_format": "wav",
                "time_stretching_enabled": False
            }
        },
        {
            "name": "stretching_20_percent_medium",
            "params": {
                "input": test_text,
                "voice": "af_heart", 
                "response_format": "wav",
                "time_stretching_enabled": True,
                "time_stretching_rate": 20,
                "time_stretching_quality": "medium"
            }
        },
        {
            "name": "stretching_50_percent_high",
            "params": {
                "input": test_text,
                "voice": "af_heart",
                "response_format": "wav", 
                "time_stretching_enabled": True,
                "time_stretching_rate": 50,
                "time_stretching_quality": "high"
            }
        },
        {
            "name": "stretching_80_percent_low",
            "params": {
                "input": test_text,
                "voice": "af_heart",
                "response_format": "wav",
                "time_stretching_enabled": True,
                "time_stretching_rate": 80,
                "time_stretching_quality": "low"
            }
        }
    ]
    
    results = []
    output_dir = Path("test_time_stretching_output")
    output_dir.mkdir(exist_ok=True)
    
    print("Testing time-stretching feature...")
    print(f"Output directory: {output_dir}")
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        
        start_time = time.perf_counter()
        
        try:
            response = requests.post(
                f"{base_url}/v1/audio/speech",
                json=test_case["params"],
                timeout=30
            )
            
            generation_time = time.perf_counter() - start_time
            
            if response.status_code == 200:
                # Save audio file
                output_file = output_dir / f"{test_case['name']}.wav"
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                
                result = {
                    "test_name": test_case['name'],
                    "success": True,
                    "generation_time": generation_time,
                    "file_size": file_size,
                    "output_file": str(output_file),
                    "parameters": test_case["params"]
                }
                
                print(f"  ✅ Success: {generation_time:.3f}s, {file_size} bytes")
                
            else:
                result = {
                    "test_name": test_case['name'],
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "generation_time": generation_time,
                    "parameters": test_case["params"]
                }
                
                print(f"  ❌ Failed: HTTP {response.status_code}")
                
        except Exception as e:
            result = {
                "test_name": test_case['name'],
                "success": False,
                "error": str(e),
                "generation_time": time.perf_counter() - start_time,
                "parameters": test_case["params"]
            }
            
            print(f"  ❌ Error: {e}")
        
        results.append(result)
    
    # Save results
    results_file = output_dir / "test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    # Print summary
    successful_tests = [r for r in results if r["success"]]
    print(f"\nSummary: {len(successful_tests)}/{len(results)} tests passed")
    
    if successful_tests:
        print("\nGeneration times:")
        for result in successful_tests:
            print(f"  {result['test_name']}: {result['generation_time']:.3f}s")
    
    return results

def test_config_based_stretching():
    """Test time-stretching using config.json settings"""
    base_url = "http://localhost:9876"
    
    test_text = "Testing config-based time-stretching with a longer text to trigger auto-enable threshold. This should be long enough to activate time-stretching automatically based on the configuration settings."
    
    print("\nTesting config-based time-stretching...")
    
    start_time = time.perf_counter()
    
    try:
        response = requests.post(
            f"{base_url}/v1/audio/speech",
            json={
                "input": test_text,
                "voice": "af_heart",
                "response_format": "wav"
                # No time-stretching parameters - should use config
            },
            timeout=30
        )
        
        generation_time = time.perf_counter() - start_time
        
        if response.status_code == 200:
            output_dir = Path("test_time_stretching_output")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / "config_based_stretching.wav"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print(f"  ✅ Config-based test: {generation_time:.3f}s, saved to {output_file}")
            return True
        else:
            print(f"  ❌ Config-based test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Config-based test error: {e}")
        return False

if __name__ == "__main__":
    print("Time-Stretching Feature Test")
    print("=" * 40)
    
    # Test API-based time-stretching
    api_results = test_time_stretching_api()
    
    # Test config-based time-stretching
    config_result = test_config_based_stretching()
    
    print("\n" + "=" * 40)
    print("Test completed!")
    
    successful_api_tests = len([r for r in api_results if r["success"]])
    total_tests = len(api_results) + (1 if config_result else 0)
    successful_total = successful_api_tests + (1 if config_result else 0)
    
    print(f"Overall: {successful_total}/{total_tests + 1} tests passed")
