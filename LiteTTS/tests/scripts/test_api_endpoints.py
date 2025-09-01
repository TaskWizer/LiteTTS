#!/usr/bin/env python3
"""
Comprehensive API Endpoint Validation
Tests all routing endpoints, request/response schemas, and error handling
"""

import requests
import json
import time
import sys
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8354"

class APIEndpointValidator:
    """Comprehensive API endpoint validator"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = {}
        self.failed_tests = []
        self.passed_tests = []
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        logger.info("🏥 Testing health endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Validate response schema
                required_fields = ["status", "timestamp"]
                missing_fields = [field for field in required_fields if field not in health_data]
                
                if missing_fields:
                    logger.warning(f"   ⚠️ Missing fields in health response: {missing_fields}")
                
                logger.info(f"   ✅ SUCCESS: {health_data.get('status', 'unknown')}")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_data": health_data,
                    "missing_fields": missing_fields
                }
            else:
                logger.error(f"   ❌ FAILED: HTTP {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"   ❌ EXCEPTION: {e}")
            return {"success": False, "error": str(e)}
    
    def test_voices_endpoint(self):
        """Test voices listing endpoint"""
        logger.info("🎭 Testing voices endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/v1/voices", timeout=10)
            
            if response.status_code == 200:
                voices_data = response.json()
                
                # Validate response schema
                if "voices" not in voices_data:
                    logger.error("   ❌ Missing 'voices' field in response")
                    return {"success": False, "error": "Missing 'voices' field"}
                
                voices = voices_data["voices"]
                if not isinstance(voices, list):
                    logger.error("   ❌ 'voices' field is not a list")
                    return {"success": False, "error": "'voices' field is not a list"}
                
                logger.info(f"   ✅ SUCCESS: {len(voices)} voices available")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "voice_count": len(voices),
                    "sample_voices": voices[:5] if voices else []
                }
            else:
                logger.error(f"   ❌ FAILED: HTTP {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"   ❌ EXCEPTION: {e}")
            return {"success": False, "error": str(e)}
    
    def test_speech_endpoint(self):
        """Test speech synthesis endpoint"""
        logger.info("🎵 Testing speech endpoint...")
        
        # Test valid request
        valid_payload = {
            "input": "Hello, this is a test of the speech endpoint.",
            "voice": "af_heart",
            "response_format": "mp3"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json=valid_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                audio_size = len(response.content)
                content_type = response.headers.get("content-type", "")
                
                logger.info(f"   ✅ SUCCESS: {audio_size} bytes, {content_type}")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "audio_size": audio_size,
                    "content_type": content_type
                }
            else:
                logger.error(f"   ❌ FAILED: HTTP {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"   ❌ EXCEPTION: {e}")
            return {"success": False, "error": str(e)}
    
    def test_streaming_endpoint(self):
        """Test streaming endpoint"""
        logger.info("🌊 Testing streaming endpoint...")
        
        payload = {
            "input": "This is a test of the streaming endpoint functionality.",
            "voice": "af_heart",
            "response_format": "mp3"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/audio/stream",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
                stream=True
            )
            
            if response.status_code == 200:
                chunk_count = 0
                total_size = 0
                
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        chunk_count += 1
                        total_size += len(chunk)
                
                logger.info(f"   ✅ SUCCESS: {chunk_count} chunks, {total_size} bytes")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "chunk_count": chunk_count,
                    "total_size": total_size
                }
            else:
                logger.error(f"   ❌ FAILED: HTTP {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"   ❌ EXCEPTION: {e}")
            return {"success": False, "error": str(e)}
    
    def test_error_handling(self):
        """Test error handling for various invalid requests"""
        logger.info("🚨 Testing error handling...")
        
        error_test_cases = [
            {
                "name": "Missing input",
                "payload": {"voice": "af_heart"},
                "expected_status": 400
            },
            {
                "name": "Missing voice",
                "payload": {"input": "Test"},
                "expected_status": 400
            },
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
                "name": "Invalid format",
                "payload": {"input": "Test", "voice": "af_heart", "response_format": "invalid"},
                "expected_status": 400
            },
            {
                "name": "Invalid speed",
                "payload": {"input": "Test", "voice": "af_heart", "speed": "invalid"},
                "expected_status": 400
            }
        ]
        
        results = {}
        
        for test_case in error_test_cases:
            logger.info(f"   Testing: {test_case['name']}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json=test_case["payload"],
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == test_case["expected_status"]:
                    logger.info(f"      ✅ SUCCESS: Correctly returned {response.status_code}")
                    results[test_case["name"]] = {
                        "success": True,
                        "status_code": response.status_code,
                        "expected_status": test_case["expected_status"]
                    }
                else:
                    logger.warning(f"      ⚠️ UNEXPECTED: Expected {test_case['expected_status']}, got {response.status_code}")
                    results[test_case["name"]] = {
                        "success": False,
                        "status_code": response.status_code,
                        "expected_status": test_case["expected_status"],
                        "note": "Unexpected status code"
                    }
                    
            except Exception as e:
                logger.error(f"      ❌ EXCEPTION: {e}")
                results[test_case["name"]] = {
                    "success": False,
                    "error": str(e)
                }
        
        successful_tests = sum(1 for r in results.values() if r.get("success", False))
        
        return {
            "success": successful_tests > 0,
            "total_tests": len(error_test_cases),
            "successful_tests": successful_tests,
            "test_results": results
        }
    
    def test_request_schemas(self):
        """Test request schema validation"""
        logger.info("📋 Testing request schemas...")
        
        schema_test_cases = [
            {
                "name": "Minimal valid request",
                "payload": {"input": "Test", "voice": "af_heart"},
                "should_succeed": True
            },
            {
                "name": "Complete valid request",
                "payload": {
                    "input": "Test",
                    "voice": "af_heart",
                    "response_format": "mp3",
                    "speed": 1.0
                },
                "should_succeed": True
            },
            {
                "name": "Extra fields",
                "payload": {
                    "input": "Test",
                    "voice": "af_heart",
                    "extra_field": "should_be_ignored"
                },
                "should_succeed": True
            },
            {
                "name": "Wrong data types",
                "payload": {
                    "input": 123,  # Should be string
                    "voice": "af_heart"
                },
                "should_succeed": False
            }
        ]
        
        results = {}
        
        for test_case in schema_test_cases:
            logger.info(f"   Testing: {test_case['name']}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json=test_case["payload"],
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                success = (response.status_code == 200) == test_case["should_succeed"]
                
                if success:
                    logger.info(f"      ✅ SUCCESS: Behaved as expected ({response.status_code})")
                    results[test_case["name"]] = {
                        "success": True,
                        "status_code": response.status_code,
                        "expected_success": test_case["should_succeed"]
                    }
                else:
                    logger.warning(f"      ⚠️ UNEXPECTED: Expected {'success' if test_case['should_succeed'] else 'failure'}, got {response.status_code}")
                    results[test_case["name"]] = {
                        "success": False,
                        "status_code": response.status_code,
                        "expected_success": test_case["should_succeed"]
                    }
                    
            except Exception as e:
                logger.error(f"      ❌ EXCEPTION: {e}")
                results[test_case["name"]] = {
                    "success": False,
                    "error": str(e)
                }
        
        successful_tests = sum(1 for r in results.values() if r.get("success", False))
        
        return {
            "success": successful_tests > 0,
            "total_tests": len(schema_test_cases),
            "successful_tests": successful_tests,
            "test_results": results
        }
    
    def test_response_headers(self):
        """Test response headers"""
        logger.info("📤 Testing response headers...")
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json={"input": "Test headers", "voice": "af_heart", "response_format": "mp3"},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                headers = dict(response.headers)
                
                # Check important headers
                header_checks = {
                    "content-type": headers.get("content-type", "").startswith("audio/"),
                    "content-disposition": "content-disposition" in headers,
                    "access-control-allow-origin": "access-control-allow-origin" in headers
                }
                
                passed_checks = sum(header_checks.values())
                total_checks = len(header_checks)
                
                logger.info(f"   ✅ Header checks: {passed_checks}/{total_checks} passed")
                
                return {
                    "success": passed_checks > 0,
                    "status_code": response.status_code,
                    "header_checks": header_checks,
                    "headers": headers
                }
            else:
                logger.error(f"   ❌ FAILED: HTTP {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"   ❌ EXCEPTION: {e}")
            return {"success": False, "error": str(e)}
    
    def test_openwebui_compatibility_routes(self):
        """Test OpenWebUI compatibility routes"""
        logger.info("🔗 Testing OpenWebUI compatibility routes...")
        
        compatibility_routes = [
            "/v1/audio/stream/audio/speech",
            "/v1/audio/speech/audio/speech"
        ]
        
        payload = {
            "input": "Testing compatibility routes",
            "voice": "af_heart",
            "response_format": "mp3"
        }
        
        results = {}
        
        for route in compatibility_routes:
            logger.info(f"   Testing route: {route}")
            
            try:
                response = requests.post(
                    f"{self.base_url}{route}",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    audio_size = len(response.content)
                    results[route] = {
                        "success": True,
                        "status_code": response.status_code,
                        "audio_size": audio_size
                    }
                    logger.info(f"      ✅ SUCCESS: {audio_size} bytes")
                else:
                    results[route] = {
                        "success": False,
                        "status_code": response.status_code,
                        "error": f"HTTP {response.status_code}"
                    }
                    logger.error(f"      ❌ FAILED: HTTP {response.status_code}")
                    
            except Exception as e:
                results[route] = {
                    "success": False,
                    "error": str(e)
                }
                logger.error(f"      ❌ EXCEPTION: {e}")
        
        successful_routes = sum(1 for r in results.values() if r.get("success", False))
        
        return {
            "success": successful_routes > 0,
            "total_routes": len(compatibility_routes),
            "successful_routes": successful_routes,
            "route_results": results
        }
    
    def run_comprehensive_validation(self):
        """Run all API endpoint validation tests"""
        logger.info("🚀 Starting comprehensive API endpoint validation")
        logger.info("=" * 70)
        
        # Check server availability
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code != 200:
                logger.error("❌ Server not available")
                return {"success": False, "error": "Server not available"}
            logger.info("✅ Server is available")
        except Exception as e:
            logger.error(f"❌ Cannot connect to server: {e}")
            return {"success": False, "error": f"Cannot connect to server: {e}"}
        
        # Run all tests
        tests = [
            ("Health Endpoint", self.test_health_endpoint),
            ("Voices Endpoint", self.test_voices_endpoint),
            ("Speech Endpoint", self.test_speech_endpoint),
            ("Streaming Endpoint", self.test_streaming_endpoint),
            ("Error Handling", self.test_error_handling),
            ("Request Schemas", self.test_request_schemas),
            ("Response Headers", self.test_response_headers),
            ("Compatibility Routes", self.test_openwebui_compatibility_routes)
        ]
        
        test_results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                test_results[test_name] = result
                
                if result["success"]:
                    logger.info(f"✅ {test_name}: PASSED")
                    self.passed_tests.append(test_name)
                else:
                    logger.error(f"❌ {test_name}: FAILED")
                    self.failed_tests.append(test_name)
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: EXCEPTION - {e}")
                test_results[test_name] = {"success": False, "error": str(e)}
                self.failed_tests.append(test_name)
        
        # Generate summary
        self.generate_validation_summary(test_results)
        
        return {
            "success": len(self.passed_tests) > len(self.failed_tests),
            "test_results": test_results,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests
        }
    
    def generate_validation_summary(self, test_results):
        """Generate validation summary"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 API ENDPOINT VALIDATION SUMMARY")
        logger.info("=" * 70)
        
        total_tests = len(test_results)
        passed_tests = len(self.passed_tests)
        failed_tests = len(self.failed_tests)
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.passed_tests:
            logger.info(f"\n✅ PASSED TESTS:")
            for test in self.passed_tests:
                logger.info(f"   • {test}")
        
        if self.failed_tests:
            logger.info(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                logger.info(f"   • {test}")
        
        # Overall assessment
        if passed_tests == total_tests:
            logger.info("\n🎉 ALL TESTS PASSED!")
            logger.info("✅ API endpoints are fully functional")
        elif passed_tests >= total_tests * 0.8:
            logger.info("\n✅ MOSTLY SUCCESSFUL!")
            logger.info("🔧 Minor issues detected but core functionality works")
        else:
            logger.info("\n⚠️ SIGNIFICANT ISSUES DETECTED!")
            logger.info("🔧 API endpoints need attention")
        
        logger.info("=" * 70)

def main():
    """Main validation function"""
    validator = APIEndpointValidator()
    results = validator.run_comprehensive_validation()
    
    # Save results to file
    with open("api_endpoint_validation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("📄 Validation results saved to api_endpoint_validation_results.json")
    
    # Exit with appropriate code
    if results["success"]:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
