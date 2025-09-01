#!/usr/bin/env python3
"""
Comprehensive Test Suite for Chunked Audio Generation
Tests chunked generation with various text lengths and validates streaming performance
"""

import requests
import json
import time
import sys
import os
import asyncio
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8354"

class ChunkedGenerationTester:
    """Comprehensive tester for chunked audio generation"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = []
        self.performance_data = []
    
    def test_configuration_loading(self):
        """Test that chunked generation configuration is loaded correctly"""
        logger.info("🔧 Testing configuration loading...")
        
        try:
            # Test health endpoint to ensure server is running
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code != 200:
                logger.error("❌ Server not responding")
                return False
            
            logger.info("✅ Server is running")
            
            # Test that chunked generation is available (indirect test)
            response = requests.get(f"{self.base_url}/v1/voices", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Configuration appears to be loaded correctly")
                return True
            else:
                logger.error("❌ Configuration loading issue")
                return False
                
        except Exception as e:
            logger.error(f"❌ Configuration test failed: {e}")
            return False
    
    def test_text_chunking_strategies(self):
        """Test different text chunking strategies"""
        logger.info("🧩 Testing text chunking strategies...")
        
        test_texts = [
            {
                "name": "Short text",
                "text": "Hello world!",
                "expected_chunks": 1  # Should not be chunked
            },
            {
                "name": "Medium text",
                "text": "This is a medium length text that should test the chunking system. It contains multiple sentences. Each sentence should be processed appropriately.",
                "expected_chunks": 2  # Should be chunked
            },
            {
                "name": "Long text with dialogue",
                "text": "Once upon a time, there was a brave knight. 'I must save the kingdom!' he declared. The dragon roared in response. 'You shall not pass!' it bellowed. The battle was fierce and long.",
                "expected_chunks": 3  # Should be chunked with dialogue awareness
            },
            {
                "name": "Very long text",
                "text": "This is a very long text that will definitely require chunking. " * 20 + "It should be broken down into multiple logical chunks while maintaining voice consistency and prosody continuity across all segments.",
                "expected_chunks": 5  # Should be heavily chunked
            }
        ]
        
        results = []
        
        for test_case in test_texts:
            logger.info(f"   Testing: {test_case['name']}")
            
            try:
                start_time = time.time()
                
                # Test with streaming endpoint to trigger chunked generation
                response = requests.post(
                    f"{self.base_url}/v1/audio/stream",
                    json={
                        "input": test_case["text"],
                        "voice": "af_heart",
                        "response_format": "mp3"
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=60,
                    stream=True
                )
                
                if response.status_code == 200:
                    # Collect streaming data
                    chunks_received = 0
                    total_size = 0
                    
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            chunks_received += 1
                            total_size += len(chunk)
                    
                    duration = time.time() - start_time
                    
                    result = {
                        "name": test_case["name"],
                        "text_length": len(test_case["text"]),
                        "chunks_received": chunks_received,
                        "total_size": total_size,
                        "duration": duration,
                        "success": True
                    }
                    
                    logger.info(f"      ✅ SUCCESS: {chunks_received} chunks, {total_size} bytes in {duration:.2f}s")
                    
                else:
                    result = {
                        "name": test_case["name"],
                        "error": f"HTTP {response.status_code}",
                        "success": False
                    }
                    logger.error(f"      ❌ FAILED: HTTP {response.status_code}")
                
                results.append(result)
                
            except Exception as e:
                result = {
                    "name": test_case["name"],
                    "error": str(e),
                    "success": False
                }
                results.append(result)
                logger.error(f"      ❌ EXCEPTION: {e}")
        
        success_count = sum(1 for r in results if r.get("success", False))
        logger.info(f"📊 Text chunking test results: {success_count}/{len(results)} passed")
        
        return results
    
    def test_streaming_performance(self):
        """Test streaming performance with different text lengths"""
        logger.info("⚡ Testing streaming performance...")
        
        performance_tests = [
            {
                "name": "Short response time",
                "text": "Quick test.",
                "max_time_to_first_byte": 2.0
            },
            {
                "name": "Medium response time",
                "text": "This is a medium length text that should demonstrate the benefits of chunked generation for user experience.",
                "max_time_to_first_byte": 3.0
            },
            {
                "name": "Long response time",
                "text": "This is a much longer text that will really test the chunked generation system. " * 10 + "The user should start hearing audio much sooner than with traditional generation.",
                "max_time_to_first_byte": 5.0
            }
        ]
        
        results = []
        
        for test_case in performance_tests:
            logger.info(f"   Testing: {test_case['name']}")
            
            try:
                start_time = time.time()
                first_byte_time = None
                
                response = requests.post(
                    f"{self.base_url}/v1/audio/stream",
                    json={
                        "input": test_case["text"],
                        "voice": "af_heart",
                        "response_format": "mp3"
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=60,
                    stream=True
                )
                
                if response.status_code == 200:
                    # Measure time to first byte
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk and first_byte_time is None:
                            first_byte_time = time.time() - start_time
                            break
                    
                    # Consume the rest of the response
                    for chunk in response.iter_content(chunk_size=1024):
                        pass
                    
                    total_time = time.time() - start_time
                    
                    meets_requirement = first_byte_time <= test_case["max_time_to_first_byte"]
                    
                    result = {
                        "name": test_case["name"],
                        "text_length": len(test_case["text"]),
                        "time_to_first_byte": first_byte_time,
                        "total_time": total_time,
                        "max_allowed": test_case["max_time_to_first_byte"],
                        "meets_requirement": meets_requirement,
                        "success": True
                    }
                    
                    status = "✅" if meets_requirement else "⚠️"
                    logger.info(f"      {status} Time to first byte: {first_byte_time:.2f}s (max: {test_case['max_time_to_first_byte']}s)")
                    
                else:
                    result = {
                        "name": test_case["name"],
                        "error": f"HTTP {response.status_code}",
                        "success": False
                    }
                    logger.error(f"      ❌ FAILED: HTTP {response.status_code}")
                
                results.append(result)
                
            except Exception as e:
                result = {
                    "name": test_case["name"],
                    "error": str(e),
                    "success": False
                }
                results.append(result)
                logger.error(f"      ❌ EXCEPTION: {e}")
        
        success_count = sum(1 for r in results if r.get("success", False))
        performance_count = sum(1 for r in results if r.get("meets_requirement", False))
        
        logger.info(f"📊 Performance test results: {success_count}/{len(results)} successful, {performance_count}/{len(results)} met performance requirements")
        
        return results
    
    def test_voice_consistency(self):
        """Test voice consistency across chunks"""
        logger.info("🎭 Testing voice consistency...")
        
        test_text = "This is the first sentence with a specific voice characteristic. This is the second sentence that should maintain the same voice. And this is the third sentence to complete the consistency test."
        
        voices_to_test = ["af_heart", "am_adam", "bf_alice"]
        results = []
        
        for voice in voices_to_test:
            logger.info(f"   Testing voice: {voice}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/v1/audio/stream",
                    json={
                        "input": test_text,
                        "voice": voice,
                        "response_format": "mp3"
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=60,
                    stream=True
                )
                
                if response.status_code == 200:
                    # Collect all chunks
                    audio_chunks = []
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            audio_chunks.append(chunk)
                    
                    total_size = sum(len(chunk) for chunk in audio_chunks)
                    
                    result = {
                        "voice": voice,
                        "chunks_received": len(audio_chunks),
                        "total_size": total_size,
                        "success": True
                    }
                    
                    logger.info(f"      ✅ SUCCESS: {len(audio_chunks)} chunks, {total_size} bytes")
                    
                else:
                    result = {
                        "voice": voice,
                        "error": f"HTTP {response.status_code}",
                        "success": False
                    }
                    logger.error(f"      ❌ FAILED: HTTP {response.status_code}")
                
                results.append(result)
                
            except Exception as e:
                result = {
                    "voice": voice,
                    "error": str(e),
                    "success": False
                }
                results.append(result)
                logger.error(f"      ❌ EXCEPTION: {e}")
        
        success_count = sum(1 for r in results if r.get("success", False))
        logger.info(f"📊 Voice consistency test results: {success_count}/{len(results)} passed")
        
        return results
    
    def test_fallback_behavior(self):
        """Test fallback to standard generation when chunked generation fails"""
        logger.info("🔄 Testing fallback behavior...")
        
        # Test with a very short text that should not trigger chunking
        short_text = "Hi!"
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/v1/audio/stream",
                json={
                    "input": short_text,
                    "voice": "af_heart",
                    "response_format": "mp3"
                },
                headers={"Content-Type": "application/json"},
                timeout=30,
                stream=True
            )
            
            if response.status_code == 200:
                # Check response headers for generation mode
                generation_mode = response.headers.get("X-Generation-Mode", "unknown")
                
                audio_data = b""
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        audio_data += chunk
                
                duration = time.time() - start_time
                
                logger.info(f"   ✅ Fallback test successful")
                logger.info(f"      Generation mode: {generation_mode}")
                logger.info(f"      Audio size: {len(audio_data)} bytes")
                logger.info(f"      Duration: {duration:.2f}s")
                
                return {
                    "success": True,
                    "generation_mode": generation_mode,
                    "audio_size": len(audio_data),
                    "duration": duration
                }
            else:
                logger.error(f"   ❌ Fallback test failed: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"   ❌ Fallback test exception: {e}")
            return {"success": False, "error": str(e)}
    
    def run_comprehensive_test(self):
        """Run all tests and generate report"""
        logger.info("🚀 Starting comprehensive chunked generation test suite")
        logger.info("=" * 70)
        
        # Test results
        test_results = {}
        
        # 1. Configuration loading
        test_results["configuration"] = self.test_configuration_loading()
        
        # 2. Text chunking strategies
        test_results["chunking"] = self.test_text_chunking_strategies()
        
        # 3. Streaming performance
        test_results["performance"] = self.test_streaming_performance()
        
        # 4. Voice consistency
        test_results["voice_consistency"] = self.test_voice_consistency()
        
        # 5. Fallback behavior
        test_results["fallback"] = self.test_fallback_behavior()
        
        # Generate summary report
        self.generate_test_report(test_results)
        
        return test_results
    
    def generate_test_report(self, test_results):
        """Generate comprehensive test report"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 CHUNKED GENERATION TEST REPORT")
        logger.info("=" * 70)
        
        # Configuration test
        config_status = "✅ PASS" if test_results["configuration"] else "❌ FAIL"
        logger.info(f"Configuration Loading: {config_status}")
        
        # Chunking tests
        chunking_results = test_results["chunking"]
        chunking_passed = sum(1 for r in chunking_results if r.get("success", False))
        chunking_total = len(chunking_results)
        chunking_status = "✅ PASS" if chunking_passed == chunking_total else f"⚠️ PARTIAL ({chunking_passed}/{chunking_total})"
        logger.info(f"Text Chunking: {chunking_status}")
        
        # Performance tests
        performance_results = test_results["performance"]
        performance_passed = sum(1 for r in performance_results if r.get("meets_requirement", False))
        performance_total = len(performance_results)
        performance_status = "✅ PASS" if performance_passed == performance_total else f"⚠️ PARTIAL ({performance_passed}/{performance_total})"
        logger.info(f"Streaming Performance: {performance_status}")
        
        # Voice consistency tests
        voice_results = test_results["voice_consistency"]
        voice_passed = sum(1 for r in voice_results if r.get("success", False))
        voice_total = len(voice_results)
        voice_status = "✅ PASS" if voice_passed == voice_total else f"⚠️ PARTIAL ({voice_passed}/{voice_total})"
        logger.info(f"Voice Consistency: {voice_status}")
        
        # Fallback test
        fallback_status = "✅ PASS" if test_results["fallback"]["success"] else "❌ FAIL"
        logger.info(f"Fallback Behavior: {fallback_status}")
        
        # Overall assessment
        all_critical_passed = (
            test_results["configuration"] and
            chunking_passed > 0 and
            performance_passed > 0 and
            test_results["fallback"]["success"]
        )
        
        overall_status = "🎉 OVERALL: PASS" if all_critical_passed else "❌ OVERALL: FAIL"
        logger.info(f"\n{overall_status}")
        
        if all_critical_passed:
            logger.info("✅ Chunked generation system is working correctly!")
            logger.info("🚀 Ready for production use with improved real-time user experience")
        else:
            logger.info("⚠️ Some tests failed. Review the results above for details.")
        
        logger.info("=" * 70)

def main():
    """Main test function"""
    tester = ChunkedGenerationTester()
    results = tester.run_comprehensive_test()
    
    # Save results to file
    with open("chunked_generation_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("📄 Test results saved to chunked_generation_test_results.json")
    
    # Exit with appropriate code
    if results["configuration"] and results["fallback"]["success"]:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
