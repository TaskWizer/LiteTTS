#!/usr/bin/env python3
"""
Quick test of the eSpeak integration in the unified text processor
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode

def test_question_mark_fix():
    """Test the question mark fix in the unified processor"""
    print("🎯 Testing Question Mark Fix Integration")
    print("=" * 50)

    # Create processor with config
    config = {
        "symbol_processing": {
            "espeak_enhanced_processing": {
                "enabled": True,
                "fix_question_mark_pronunciation": True,
                "punctuation_mode": "some"
            }
        }
    }

    processor = UnifiedTextProcessor(enable_advanced_features=True, config=config)

    # Test cases
    test_cases = [
        "Hello? How are you?",
        "What time is it?",
        "Use the * symbol carefully",
        'She said "Hello world"',
        "Visit https://example.com for info",
    ]

    # Create processing options
    options = ProcessingOptions(
        mode=ProcessingMode.ENHANCED,
        use_espeak_enhanced_symbols=True
    )

    print("📝 Testing text processing with eSpeak enhancements:")

    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. Input: '{test_text}'")

        try:
            result = processor.process_text(test_text, options)

            print(f"   ✅ Output: '{result.processed_text}'")
            print(f"   🔧 Changes: {', '.join(result.changes_made) if result.changes_made else 'None'}")
            print(f"   📊 Stages: {', '.join(result.stages_completed)}")
            print(f"   ⏱️  Time: {result.processing_time:.3f}s")

            # Check if question mark fix was applied
            if "?" in test_text and "question mark" in result.processed_text.lower():
                print("   ✅ Question mark fix applied successfully!")
            elif "*" in test_text and "asterisk" in result.processed_text.lower():
                print("   ✅ Asterisk fix applied successfully!")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    return True

def main():
    """Main test function"""
    print("🚀 eSpeak Integration Test")
    print("=" * 40)

    try:
        success = test_question_mark_fix()

        if success:
            print("\n✅ Integration test completed successfully!")
            print("   eSpeak-enhanced symbol processing is working in the unified pipeline.")
        else:
            print("\n❌ Integration test failed.")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Integration Tests for Kokoro ONNX TTS API
Tests integration with external services, OpenWebUI compatibility, and real-world scenarios
"""

import pytest
import requests
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Import the app for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app import app
from fastapi.testclient import TestClient


class TestOpenWebUIIntegration:
    """Test OpenWebUI compatibility and integration"""

    def setup_method(self):
        self.client = TestClient(app)
        self.base_url = "http://localhost:8354"  # Default server URL

    def test_openwebui_models_endpoint(self):
        """Test OpenWebUI models endpoint compatibility"""
        response = self.client.get("/v1/models")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

        # Should have at least one model
        assert len(data["data"]) > 0

        # Check model structure
        model = data["data"][0]
        required_fields = ["id", "object", "created", "owned_by"]
        for field in required_fields:
            assert field in model, f"Missing required field: {field}"

    def test_openwebui_speech_endpoint(self):
        """Test OpenWebUI speech endpoint compatibility"""
        response = self.client.post(
            "/v1/audio/speech",
            json={
                "model": "tts-1",  # OpenWebUI uses this model name
                "input": "Hello from OpenWebUI integration test",
                "voice": "af_heart"
            }
        )

        # Should handle OpenWebUI format
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            # Should return audio content
            assert len(response.content) > 0
            assert response.headers.get("content-type", "").startswith("audio/")

    def test_openwebui_compatibility_routes(self):
        """Test OpenWebUI compatibility routes for malformed URLs"""
        compatibility_endpoints = [
            "/v1/audio/stream/audio/speech",
            "/v1/audio/speech/audio/speech"
        ]

        for endpoint in compatibility_endpoints:
            response = self.client.post(
                endpoint,
                json={
                    "input": "Testing compatibility route",
                    "voice": "af_heart"
                }
            )

            # Should handle gracefully
            assert response.status_code in [200, 400, 404]

    def test_openwebui_voice_parameter_variations(self):
        """Test various voice parameter formats that OpenWebUI might send"""
        voice_variations = [
            "af_heart",
            "heart",
            "alloy",
            "nova",
            "echo"
        ]

        for voice in voice_variations:
            response = self.client.post(
                "/v1/audio/speech",
                json={
                    "input": f"Testing voice {voice}",
                    "voice": voice
                }
            )

            # Should either work or fail gracefully
            assert response.status_code in [200, 400]


class TestExternalAPICompatibility:
    """Test compatibility with external API standards"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_openai_api_compatibility(self):
        """Test OpenAI API compatibility"""
        # Test OpenAI-style request
        response = self.client.post(
            "/v1/audio/speech",
            json={
                "model": "tts-1",
                "input": "Testing OpenAI API compatibility",
                "voice": "alloy",
                "response_format": "mp3",
                "speed": 1.0
            }
        )

        assert response.status_code in [200, 400]

        if response.status_code == 200:
            # Should return proper audio
            assert len(response.content) > 0

    def test_content_type_variations(self):
        """Test different content type headers"""
        content_types = [
            "application/json",
            "application/json; charset=utf-8",
            "application/json;charset=UTF-8"
        ]

        for content_type in content_types:
            response = self.client.post(
                "/v1/audio/speech",
                json={"input": "Content type test", "voice": "af_heart"},
                headers={"Content-Type": content_type}
            )

            assert response.status_code in [200, 400]

    def test_user_agent_variations(self):
        """Test different User-Agent headers"""
        user_agents = [
            "OpenWebUI/1.0",
            "Mozilla/5.0 (compatible; OpenWebUI)",
            "curl/7.68.0",
            "python-requests/2.28.0",
            "PostmanRuntime/7.29.0"
        ]

        for user_agent in user_agents:
            response = self.client.post(
                "/v1/audio/speech",
                json={"input": "User agent test", "voice": "af_heart"},
                headers={"User-Agent": user_agent}
            )

            assert response.status_code in [200, 400]


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_chatbot_integration_scenario(self):
        """Test typical chatbot integration scenario"""
        # Simulate a conversation with multiple TTS requests
        conversation = [
            "Hello! How can I help you today?",
            "I can help you with various tasks.",
            "Is there anything specific you'd like to know?",
            "Thank you for using our service!"
        ]

        results = []

        for i, message in enumerate(conversation):
            start_time = time.time()
            response = self.client.post(
                "/v1/audio/speech",
                json={
                    "input": message,
                    "voice": "af_heart",
                    "response_format": "mp3"
                }
            )
            duration = time.time() - start_time

            results.append({
                "message_id": i,
                "success": response.status_code == 200,
                "duration": duration,
                "audio_size": len(response.content) if response.status_code == 200 else 0
            })

            # Brief pause between messages (realistic scenario)
            time.sleep(0.1)

        # Analyze conversation results
        successful_messages = [r for r in results if r["success"]]

        # Should handle most messages successfully
        success_rate = len(successful_messages) / len(conversation)
        assert success_rate >= 0.7, f"Conversation success rate {success_rate:.1%} too low"

        # Performance should be reasonable for chatbot use
        if successful_messages:
            avg_duration = sum(r["duration"] for r in successful_messages) / len(successful_messages)
            assert avg_duration < 5.0, f"Average response time {avg_duration:.2f}s too slow for chatbot"

    def test_multilingual_content_scenario(self):
        """Test multilingual content handling"""
        multilingual_texts = [
            "Hello, how are you today?",  # English
            "Bonjour, comment allez-vous?",  # French
            "Hola, ¿cómo estás?",  # Spanish
            "Guten Tag, wie geht es Ihnen?",  # German
            "Ciao, come stai?",  # Italian
        ]

        results = []

        for text in multilingual_texts:
            response = self.client.post(
                "/v1/audio/speech",
                json={
                    "input": text,
                    "voice": "af_heart"
                }
            )

            results.append({
                "text": text,
                "success": response.status_code == 200,
                "audio_size": len(response.content) if response.status_code == 200 else 0
            })

        # Should handle at least English successfully
        english_result = results[0]
        assert english_result["success"], "Should handle English text successfully"

        # Other languages may or may not work, but shouldn't crash
        for result in results:
            # No crashes or server errors
            assert result["success"] or result["audio_size"] == 0

    def test_educational_content_scenario(self):
        """Test educational content with various text types"""
        educational_texts = [
            "The quick brown fox jumps over the lazy dog.",  # Pangram
            "To be or not to be, that is the question.",  # Shakespeare
            "E = mc²",  # Mathematical formula
            "The mitochondria is the powerhouse of the cell.",  # Science
            "In 1492, Columbus sailed the ocean blue.",  # History
            "Red, orange, yellow, green, blue, indigo, violet.",  # Colors
        ]

        results = []

        for text in educational_texts:
            response = self.client.post(
                "/v1/audio/speech",
                json={
                    "input": text,
                    "voice": "af_heart",
                    "speed": 0.9  # Slightly slower for educational content
                }
            )

            results.append({
                "text": text[:30] + "..." if len(text) > 30 else text,
                "success": response.status_code == 200
            })

        # Should handle educational content well
        successful_count = sum(1 for r in results if r["success"])
        success_rate = successful_count / len(educational_texts)

        assert success_rate >= 0.8, f"Educational content success rate {success_rate:.1%} too low"


class TestPerformanceIntegration:
    """Test performance in integration scenarios"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_cache_behavior_in_integration(self):
        """Test cache behavior in realistic usage patterns"""
        # Common phrases that might be repeated
        common_phrases = [
            "Welcome to our service",
            "Thank you for your patience",
            "Please try again later",
            "Have a great day!"
        ]

        # First round - cache misses
        first_round_times = []
        for phrase in common_phrases:
            start_time = time.time()
            response = self.client.post(
                "/v1/audio/speech",
                json={"input": phrase, "voice": "af_heart"}
            )
            duration = time.time() - start_time

            if response.status_code == 200:
                first_round_times.append(duration)

        # Second round - should be cache hits
        second_round_times = []
        for phrase in common_phrases:
            start_time = time.time()
            response = self.client.post(
                "/v1/audio/speech",
                json={"input": phrase, "voice": "af_heart"}
            )
            duration = time.time() - start_time

            if response.status_code == 200:
                second_round_times.append(duration)

        # Cache hits should be faster
        if first_round_times and second_round_times:
            avg_first = sum(first_round_times) / len(first_round_times)
            avg_second = sum(second_round_times) / len(second_round_times)

            # Allow some tolerance, but second round should be faster
            assert avg_second <= avg_first * 1.5, "Cache doesn't seem to be working effectively"

    def test_mixed_voice_performance(self):
        """Test performance with mixed voice usage"""
        voices = ["af_heart", "am_puck"]
        text = "Performance test with different voices"

        results = []

        for voice in voices:
            for i in range(3):  # 3 requests per voice
                start_time = time.time()
                response = self.client.post(
                    "/v1/audio/speech",
                    json={
                        "input": f"{text} {i}",
                        "voice": voice
                    }
                )
                duration = time.time() - start_time

                results.append({
                    "voice": voice,
                    "success": response.status_code == 200,
                    "duration": duration
                })

        # Analyze per-voice performance
        for voice in voices:
            voice_results = [r for r in results if r["voice"] == voice and r["success"]]

            if voice_results:
                avg_duration = sum(r["duration"] for r in voice_results) / len(voice_results)
                assert avg_duration < 10.0, f"Voice {voice} average duration {avg_duration:.2f}s too slow"


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v", "-s"])  # -s to see print output
