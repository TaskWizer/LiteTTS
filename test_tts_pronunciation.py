#!/usr/bin/env python3
"""
Systematic TTS Pronunciation Testing Pipeline
Uses TTS API to generate audio and Whisper to validate pronunciation
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from faster_whisper import WhisperModel

# Test phrases that have known pronunciation issues
TEST_PHRASES = [
    # Common problematic words
    ("Directions", "Take Directions from here."),
    ("because", "It's important because we need to."),
    ("know", "I know what you mean."),
    ("tests", "Run the tests first."),
    ("any", "Do you have any questions?"),
    ("their", "Their house is nearby."),
    ("there", "The book is over there."),
    ("God Damn It", "God Damn It!"),
    ("Because", "Because it's right."),
    ("Know", "You should know by now."),
    ("Tests", "The tests all passed."),
    ("Any", "Any direction will work."),
    # Symbols
    ("Slash", "God/Damn/It"),  # slash handling
    # Numbers and fractions
    ("Half", "Half of it is broken."),
    # Complex words
    ("acquisition", "The acquisition was completed."),
    ("philosophy", "Study philosophy."),
    ("really", "I really mean it."),
    # contractions
    ("wouldn't", "I wouldn't do that."),
    ("couldn't", "I couldn't agree more."),
    # homographs
    ("read present", "I read books every day."),
    ("read past", "I read that book yesterday."),
    ("lead present", "Lead the way please."),
    ("lead metal", "The lead pipe leaked."),
]

API_BASE = "http://localhost:8354"
VOICE = "af_heart"

class TTSValidator:
    def __init__(self):
        print("Loading Whisper model...")
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="tts_test_"))
        print(f"Temp directory: {self.temp_dir}")

    def generate_audio(self, text: str, output_path: Path) -> bool:
        """Generate audio using TTS API"""
        import requests
        try:
            response = requests.post(
                f"{API_BASE}/v1/audio/speech",
                json={"input": text, "voice": VOICE, "response_format": "mp3"},
                timeout=30
            )
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                print(f"  ERROR: API returned {response.status_code}")
                return False
        except Exception as e:
            print(f"  ERROR: {e}")
            return False

    def transcribe_audio(self, audio_path: Path) -> Tuple[str, float]:
        """Transcribe audio using Whisper, returns (transcription, confidence)"""
        try:
            segments, info = self.model.transcribe(
                str(audio_path),
                language="en",
                condition_on_previous_text=False
            )
            text = "".join([seg.text for seg in segments])
            confidence = info.language_probability
            return text.strip(), confidence
        except Exception as e:
            print(f"  Whisper error: {e}")
            return "", 0.0

    def normalize_for_comparison(self, text: str) -> str:
        """Normalize text for comparison"""
        import re
        # Remove punctuation, lowercase
        text = re.sub(r'[^\w\s]', '', text.lower())
        # Normalize whitespace
        text = ' '.join(text.split())
        return text

    def run_test(self, phrase: str, description: str) -> Dict:
        """Run a single test"""
        print(f"\nTesting: {description}")
        print(f"  Expected: {phrase}")

        # Generate audio
        audio_path = self.temp_dir / f"test_{len(phrase)}.mp3"
        if not self.generate_audio(phrase, audio_path):
            return {"status": "error", "phrase": phrase, "description": description}

        # Transcribe
        transcription, confidence = self.transcribe_audio(audio_path)
        print(f"  Whisper: {transcription}")
        print(f"  Confidence: {confidence:.2f}")

        # Compare
        expected_normalized = self.normalize_for_comparison(phrase)
        transcription_normalized = self.normalize_for_comparison(transcription)

        if expected_normalized == transcription_normalized:
            status = "pass"
        else:
            status = "fail"
            # Calculate similarity
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, expected_normalized, transcription_normalized).ratio()
            print(f"  Similarity: {similarity:.2%}")

        return {
            "status": status,
            "phrase": phrase,
            "description": description,
            "transcription": transcription,
            "confidence": confidence,
            "normalized_expected": expected_normalized,
            "normalized_transcription": transcription_normalized
        }

    def run_all_tests(self) -> List[Dict]:
        """Run all tests"""
        results = []
        for description, phrase in TEST_PHRASES:
            result = self.run_test(phrase, description)
            results.append(result)

        return results

    def print_summary(self, results: List[Dict]):
        """Print summary of results"""
        passed = sum(1 for r in results if r["status"] == "pass")
        failed = sum(1 for r in results if r["status"] == "fail")
        errors = sum(1 for r in results if r["status"] == "error")

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Passed: {passed}/{len(results)}")
        print(f"Failed: {failed}/{len(results)}")
        print(f"Errors: {errors}/{len(results)}")

        if failed > 0:
            print("\nFailed tests:")
            for r in results:
                if r["status"] == "fail":
                    print(f"  - {r['description']}")
                    print(f"    Expected: {r['normalized_expected']}")
                    print(f"    Got: {r['normalized_transcription']}")

        return passed, failed, errors

    def cleanup(self):
        """Clean up temp files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

def main():
    validator = TTSValidator()
    try:
        results = validator.run_all_tests()
        passed, failed, errors = validator.print_summary(results)

        # Save results
        output_path = Path("test_results/pronunciation_test_results.json")
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w") as f:
            json.dump({
                "results": results,
                "summary": {"passed": passed, "failed": failed, "errors": errors}
            }, f, indent=2)
        print(f"\nResults saved to: {output_path}")

        return 0 if failed == 0 else 1
    finally:
        validator.cleanup()

if __name__ == "__main__":
    sys.exit(main())
