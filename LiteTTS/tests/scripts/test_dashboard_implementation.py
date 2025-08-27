#!/usr/bin/env python3
"""
Test script for API Analytics & Concurrency Dashboard implementation

Validates that the dashboard is working correctly with:
1. Dashboard web interface accessibility
2. Dashboard data API functionality
3. Analytics data collection from TTS requests
4. Real-time metrics tracking
"""

import requests
import time
import json
from typing import Dict, Any

def test_dashboard_web_interface() -> bool:
    """Test that the dashboard web interface is accessible"""
    
    print("🌐 Testing Dashboard Web Interface")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8354/dashboard", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for key dashboard elements
            required_elements = [
                "Kokoro ONNX TTS API Dashboard",
                "Real-time monitoring",
                "chart.js",
                "dashboard-data"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element.lower() not in content.lower():
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"❌ Missing dashboard elements: {missing_elements}")
                return False
            else:
                print("✅ Dashboard web interface is accessible and contains required elements")
                return True
        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to dashboard - is the server running?")
        return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_dashboard_data_api() -> bool:
    """Test that the dashboard data API returns valid data"""
    
    print("\n📊 Testing Dashboard Data API")
    print("=" * 35)
    
    try:
        response = requests.get("http://localhost:8354/dashboard/data", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for required data fields
            required_fields = [
                'timestamp',
                'requests_per_minute',
                'response_time_stats',
                'error_rates',
                'voice_usage',
                'concurrency',
                'system_status',
                'performance',
                'tts_stats'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing data fields: {missing_fields}")
                return False
            
            # Validate data structure
            if not isinstance(data['requests_per_minute'], list):
                print("❌ requests_per_minute should be a list")
                return False
            
            if not isinstance(data['response_time_stats'], dict):
                print("❌ response_time_stats should be a dict")
                return False
            
            if not isinstance(data['concurrency'], dict):
                print("❌ concurrency should be a dict")
                return False
            
            print("✅ Dashboard data API returns valid structured data")
            print(f"   Timestamp: {data['timestamp']}")
            print(f"   Total requests: {data['system_status']['total_requests_all_time']}")
            print(f"   Uptime: {data['system_status']['uptime_seconds']:.1f}s")
            
            return True
        else:
            print(f"❌ Dashboard data API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard data API test failed: {e}")
        return False

def test_analytics_data_collection() -> bool:
    """Test that analytics properly collect data from TTS requests"""
    
    print("\n🔍 Testing Analytics Data Collection")
    print("=" * 40)
    
    try:
        # Get initial state
        initial_response = requests.get("http://localhost:8354/dashboard/data", timeout=10)
        initial_data = initial_response.json()

        # Check both dashboard analytics and performance monitor
        initial_dashboard_requests = initial_data['system_status']['total_requests_all_time']
        initial_performance_requests = initial_data.get('performance', {}).get('summary', {}).get('total_requests', 0)

        print(f"Initial dashboard request count: {initial_dashboard_requests}")
        print(f"Initial performance request count: {initial_performance_requests}")

        # Make a test TTS request
        tts_payload = {
            "input": "Dashboard analytics test request",
            "voice": "af_heart",
            "response_format": "mp3"
        }

        print("Making test TTS request...")
        tts_response = requests.post(
            "http://localhost:8354/v1/audio/speech",
            json=tts_payload,
            timeout=30
        )

        if tts_response.status_code != 200:
            print(f"❌ TTS request failed with status: {tts_response.status_code}")
            return False

        print("✅ TTS request successful")

        # Wait a moment for analytics to update
        time.sleep(2)

        # Check updated analytics
        updated_response = requests.get("http://localhost:8354/dashboard/data", timeout=10)
        updated_data = updated_response.json()

        updated_dashboard_requests = updated_data['system_status']['total_requests_all_time']
        updated_performance_requests = updated_data.get('performance', {}).get('summary', {}).get('total_requests', 0)

        print(f"Updated dashboard request count: {updated_dashboard_requests}")
        print(f"Updated performance request count: {updated_performance_requests}")

        # Check if either analytics system captured the request
        dashboard_captured = updated_dashboard_requests > initial_dashboard_requests
        performance_captured = updated_performance_requests > initial_performance_requests

        if dashboard_captured or performance_captured:
            print("✅ Analytics successfully captured TTS request")

            if performance_captured:
                print("✅ Performance monitor captured the request")

                # Check if voice usage was tracked in performance data
                voice_performance = updated_data.get('performance', {}).get('voice_performance', {})
                if 'af_heart' in voice_performance:
                    requests_count = voice_performance['af_heart'].get('requests', 0)
                    print(f"✅ Voice usage tracked in performance: af_heart used {requests_count} times")

            if dashboard_captured:
                print("✅ Dashboard analytics captured the request")

                # Check if voice usage was tracked in dashboard analytics
                voice_usage = updated_data.get('voice_usage', {})
                if 'af_heart' in voice_usage:
                    print(f"✅ Voice usage tracked in dashboard: af_heart used {voice_usage['af_heart']} times")

            return True
        else:
            print("❌ Neither analytics system captured the TTS request")
            return False
            
    except Exception as e:
        print(f"❌ Analytics data collection test failed: {e}")
        return False

def test_real_time_metrics() -> bool:
    """Test that metrics update in real-time"""
    
    print("\n⏱️ Testing Real-time Metrics")
    print("=" * 30)
    
    try:
        # Get initial metrics
        response1 = requests.get("http://localhost:8354/dashboard/data", timeout=10)
        data1 = response1.json()
        timestamp1 = data1['timestamp']
        
        print(f"First timestamp: {timestamp1}")
        
        # Wait a moment
        time.sleep(3)
        
        # Get updated metrics
        response2 = requests.get("http://localhost:8354/dashboard/data", timeout=10)
        data2 = response2.json()
        timestamp2 = data2['timestamp']
        
        print(f"Second timestamp: {timestamp2}")
        
        if timestamp2 > timestamp1:
            print("✅ Metrics are updating in real-time")
            
            # Check if uptime increased
            uptime1 = data1['system_status']['uptime_seconds']
            uptime2 = data2['system_status']['uptime_seconds']
            
            if uptime2 > uptime1:
                print(f"✅ Uptime tracking working: {uptime1:.1f}s -> {uptime2:.1f}s")
            
            return True
        else:
            print("❌ Metrics are not updating")
            return False
            
    except Exception as e:
        print(f"❌ Real-time metrics test failed: {e}")
        return False

def test_dashboard_comprehensive() -> Dict[str, bool]:
    """Run comprehensive dashboard tests"""
    
    print("🔧 API Analytics & Concurrency Dashboard Test Suite")
    print("=" * 55)
    print("Testing the complete dashboard implementation...")
    print()
    
    results = {}
    
    # Run all tests
    results['web_interface'] = test_dashboard_web_interface()
    results['data_api'] = test_dashboard_data_api()
    results['analytics_collection'] = test_analytics_data_collection()
    results['real_time_metrics'] = test_real_time_metrics()
    
    return results

def main():
    """Main test execution"""
    
    results = test_dashboard_comprehensive()
    
    print("\n" + "=" * 55)
    print("📊 DASHBOARD TEST RESULTS:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        test_display = test_name.replace('_', ' ').title()
        print(f"   {test_display}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Dashboard implementation is working correctly!")
        print("✅ Web interface accessible")
        print("✅ Data API functional")
        print("✅ Analytics collection working")
        print("✅ Real-time metrics updating")
        print("\n🌐 Access the dashboard at: http://localhost:8354/dashboard")
    else:
        print("\n⚠️ Some dashboard features need attention")
        print("Please check the failed tests and fix any issues")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
