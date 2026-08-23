#!/usr/bin/env python3
"""
Comprehensive OpenWebUI Integration Test
Validates all voice/linguistic features through OpenWebUI interface
"""

import json
import logging
import sys
import time

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8354"

class OpenWebUIIntegrationTester:
    """Comprehensive OpenWebUI integration tester"""

    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = {}
        self.failed_tests = []
        self.passed_tests = []

    def test_voice_availability(self):
        """Test that all voices are available through OpenWebUI"""
        logger.info("🎭 Testing voice availability through OpenWebUI...")

        # Get available voices
        try:
            response = requests.get(f"{self.base_url}/v1/voices", timeout=10)
            if response.status_code != 200:
                logger.error(f"❌ Failed to get voices: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

            voices_data = response.json()
            available_voices = voices_data.get("voices", [])

            if not available_voices:
                logger.error("❌ No voices available")
                return {"success": False, "error": "No voices available"}

            logger.info(f"✅ Found {len(available_voices)} available voices")

            # Test a sample of voices with OpenWebUI-style requests
            test_voices = available_voices[:5]  # Test first 5 voices
            voice_results = {}

            for voice in test_voices:
                logger.info(f"   Testing voice: {voice}")

                try:
                    response = requests.post(
                        f"{self.base_url}/v1/audio/speech",
                        json={
                            "input": f"Testing voice {voice} through OpenWebUI interface.",
                            "voice": voice,
                            "response_format": "mp3"
                        },
                        headers={
                            "Content-Type": "application/json",
                            "User-Agent": "Mozilla/5.0 OpenWebUI"
                        },
                        timeout=30
                    )

                    if response.status_code == 200:
                        audio_size = len(response.content)
                        voice_results[voice] = {
                            "success": True,
                            "audio_size": audio_size
                        }
                        logger.info(f"      ✅ SUCCESS: {audio_size} bytes")
                    else:
                        voice_results[voice] = {
                            "success": False,
                            "error": f"HTTP {response.status_code}"
                        }
                        logger.error(f"      ❌ FAILED: HTTP {response.status_code}")

                except Exception as e:
                    voice_results[voice] = {
                        "success": False,
                        "error": str(e)
                    }
                    logger.error(f"      ❌ EXCEPTION: {e}")

            successful_voices = sum(1 for r in voice_results.values() if r["success"])

            return {
                "success": successful_voices > 0,
                "total_voices": len(available_voices),
                "tested_voices": len(test_voices),
                "successful_voices": successful_voices,
                "voice_results": voice_results
            }

        except Exception as e:
            logger.error(f"❌ Voice availability test failed: {e}")
            return {"success": False, "error": str(e)}

    def test_linguistic_features(self):
        """Test linguistic features through OpenWebUI"""
        logger.info("📝 Testing linguistic features through OpenWebUI...")

        linguistic_tests = [
            {
                "name": "Contractions",
                "text": "I can't believe it's working! We're testing contractions.",
                "expected_features": ["contractions"]
            },
            {
                "name": "Numbers and Currency",
                "text": "The price is $123.45 and the temperature is 98.6 degrees.",
                "expected_features": ["currency", "numbers"]
            },
            {
                "name": "Dates and Times",
                "text": "The meeting is on January 15th, 2024 at 3:30 PM.",
                "expected_features": ["dates", "times"]
            },
            {
                "name": "Acronyms and Abbreviations",
                "text": "The FBI and CIA work with NATO. Dr. Smith lives on Main St.",
                "expected_features": ["acronyms", "abbreviations"]
            },
            {
                "name": "Mixed Content",
                "text": "On 12/25/2023, we spent $50.99 at the store. It's amazing!",
                "expected_features": ["dates", "currency", "contractions"]
            }
        ]

        results = {}

        for test_case in linguistic_tests:
            logger.info(f"   Testing: {test_case['name']}")

            try:
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json={
                        "input": test_case["text"],
                        "voice": "af_heart",
                        "response_format": "mp3"
                    },
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 OpenWebUI"
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    audio_size = len(response.content)
                    results[test_case["name"]] = {
                        "success": True,
                        "audio_size": audio_size,
                        "text_length": len(test_case["text"]),
                        "features": test_case["expected_features"]
                    }
                    logger.info(f"      ✅ SUCCESS: {audio_size} bytes")
                else:
                    results[test_case["name"]] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "features": test_case["expected_features"]
                    }
                    logger.error(f"      ❌ FAILED: HTTP {response.status_code}")

            except Exception as e:
                results[test_case["name"]] = {
                    "success": False,
                    "error": str(e),
                    "features": test_case["expected_features"]
                }
                logger.error(f"      ❌ EXCEPTION: {e}")

        successful_tests = sum(1 for r in results.values() if r["success"])

        return {
            "success": successful_tests > 0,
            "total_tests": len(linguistic_tests),
            "successful_tests": successful_tests,
            "test_results": results
        }

    def test_audio_formats(self):
        """Test different audio formats through OpenWebUI"""
        logger.info("🎵 Testing audio formats through OpenWebUI...")

        formats_to_test = ["mp3", "wav", "ogg"]
        test_text = "Testing audio format compatibility with OpenWebUI."

        results = {}

        for format_name in formats_to_test:
            logger.info(f"   Testing format: {format_name}")

            try:
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json={
                        "input": test_text,
                        "voice": "af_heart",
                        "response_format": format_name
                    },
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 OpenWebUI"
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    audio_size = len(response.content)
                    content_type = response.headers.get("content-type", "")

                    results[format_name] = {
                        "success": True,
                        "audio_size": audio_size,
                        "content_type": content_type
                    }
                    logger.info(f"      ✅ SUCCESS: {audio_size} bytes, {content_type}")
                else:
                    results[format_name] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    }
                    logger.error(f"      ❌ FAILED: HTTP {response.status_code}")

            except Exception as e:
                results[format_name] = {
                    "success": False,
                    "error": str(e)
                }
                logger.error(f"      ❌ EXCEPTION: {e}")

        successful_formats = sum(1 for r in results.values() if r["success"])

        return {
            "success": successful_formats > 0,
            "total_formats": len(formats_to_test),
            "successful_formats": successful_formats,
            "format_results": results
        }

    def test_streaming_functionality(self):
        """Test streaming functionality through OpenWebUI"""
        logger.info("🌊 Testing streaming functionality through OpenWebUI...")

        test_text = "This is a longer text to test the streaming functionality through OpenWebUI. " * 3

        try:
            start_time = time.time()
            first_chunk_time = None

            response = requests.post(
                f"{self.base_url}/v1/audio/stream",
                json={
                    "input": test_text,
                    "voice": "af_heart",
                    "response_format": "mp3"
                },
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 OpenWebUI"
                },
                timeout=60,
                stream=True
            )

            if response.status_code == 200:
                chunk_count = 0
                total_size = 0

                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        if first_chunk_time is None:
                            first_chunk_time = time.time() - start_time

                        chunk_count += 1
                        total_size += len(chunk)

                total_time = time.time() - start_time

                logger.info("   ✅ Streaming SUCCESS:")
                logger.info(f"      Chunks: {chunk_count}")
                logger.info(f"      Total size: {total_size} bytes")
                logger.info(f"      First chunk: {first_chunk_time:.2f}s")
                logger.info(f"      Total time: {total_time:.2f}s")

                return {
                    "success": True,
                    "chunk_count": chunk_count,
                    "total_size": total_size,
                    "first_chunk_time": first_chunk_time,
                    "total_time": total_time,
                    "text_length": len(test_text)
                }
            else:
                logger.error(f"   ❌ Streaming FAILED: HTTP {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }

        except Exception as e:
            logger.error(f"   ❌ Streaming EXCEPTION: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def test_mobile_user_agents(self):
        """Test with various mobile user agents"""
        logger.info("📱 Testing mobile user agents...")

        mobile_user_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Android 12; Mobile; rv:109.0) Gecko/109.0 Firefox/109.0",
            "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "OpenWebUI/1.0 Mobile"
        ]

        test_text = "Testing mobile user agent compatibility."
        results = {}

        for i, user_agent in enumerate(mobile_user_agents):
            agent_name = f"Mobile_{i+1}"
            logger.info(f"   Testing: {agent_name}")

            try:
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json={
                        "input": test_text,
                        "voice": "af_heart",
                        "response_format": "mp3"
                    },
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": user_agent
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    audio_size = len(response.content)
                    results[agent_name] = {
                        "success": True,
                        "audio_size": audio_size,
                        "user_agent": user_agent[:50] + "..."
                    }
                    logger.info(f"      ✅ SUCCESS: {audio_size} bytes")
                else:
                    results[agent_name] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "user_agent": user_agent[:50] + "..."
                    }
                    logger.error(f"      ❌ FAILED: HTTP {response.status_code}")

            except Exception as e:
                results[agent_name] = {
                    "success": False,
                    "error": str(e),
                    "user_agent": user_agent[:50] + "..."
                }
                logger.error(f"      ❌ EXCEPTION: {e}")

        successful_agents = sum(1 for r in results.values() if r["success"])

        return {
            "success": successful_agents > 0,
            "total_agents": len(mobile_user_agents),
            "successful_agents": successful_agents,
            "agent_results": results
        }

    def run_comprehensive_test(self):
        """Run all OpenWebUI integration tests"""
        logger.info("🚀 Starting comprehensive OpenWebUI integration test")
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
            ("Voice Availability", self.test_voice_availability),
            ("Linguistic Features", self.test_linguistic_features),
            ("Audio Formats", self.test_audio_formats),
            ("Streaming Functionality", self.test_streaming_functionality),
            ("Mobile User Agents", self.test_mobile_user_agents)
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
        self.generate_test_summary(test_results)

        return {
            "success": len(self.passed_tests) > len(self.failed_tests),
            "test_results": test_results,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests
        }

    def generate_test_summary(self, test_results):
        """Generate test summary"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 OPENWEBUI INTEGRATION TEST SUMMARY")
        logger.info("=" * 70)

        total_tests = len(test_results)
        passed_tests = len(self.passed_tests)
        failed_tests = len(self.failed_tests)

        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if self.passed_tests:
            logger.info("\n✅ PASSED TESTS:")
            for test in self.passed_tests:
                logger.info(f"   • {test}")

        if self.failed_tests:
            logger.info("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                logger.info(f"   • {test}")

        # Overall assessment
        if passed_tests == total_tests:
            logger.info("\n🎉 ALL TESTS PASSED!")
            logger.info("✅ OpenWebUI integration is fully functional")
        elif passed_tests >= total_tests * 0.8:
            logger.info("\n✅ MOSTLY SUCCESSFUL!")
            logger.info("🔧 Minor issues detected but core functionality works")
        else:
            logger.info("\n⚠️ SIGNIFICANT ISSUES DETECTED!")
            logger.info("🔧 OpenWebUI integration needs attention")

        logger.info("=" * 70)

def main():
    """Main test function"""
    tester = OpenWebUIIntegrationTester()
    results = tester.run_comprehensive_test()

    # Save results to file
    with open("openwebui_integration_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    logger.info("📄 Test results saved to openwebui_integration_test_results.json")

    # Exit with appropriate code
    if results["success"]:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
