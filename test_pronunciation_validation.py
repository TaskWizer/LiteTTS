#!/usr/bin/env python3
"""
Comprehensive TTS Validation using built-in Whisper
Tests pronunciation fixes end-to-end
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple
import requests

# Use built-in Whisper
sys.path.insert(0, str(Path(__file__).parent))
from LiteTTS.backends.whisper_optimized import OptimizedWhisperProcessor, WhisperConfig

API_BASE = "http://localhost:8354"
VOICE = "af_heart"

# Comprehensive test cases
TEST_CASES = [
    # Issue 1: Directions being spelled out
    ("Directions spelled", "Take Directions from here.", "take directions from here"),
    ("Directions standalone", "Directions please.", "directions please"),

    # Issue 2: Slash handling
    ("Slash removed", "God Damn It", "god damn it"),
    ("Slash inline", "God/Damn/It", "god damn it"),

    # Issue 3: because pronunciation
    ("Because natural", "It's important because.", "its important because"),

    # Issue 4: know vs now
    ("Know context", "I know what you mean.", "i know what you mean"),

    # Issue 5: tests
    ("Tests plural", "Run the tests.", "run the tests"),

    # Issue 6: any
    ("Any natural", "Do you have any questions?", "do you have any questions"),

    # Issue 7: their/there
    ("Their possessive", "Their house is here.", "their house is here"),
    ("There location", "The book is there.", "the book is there"),

    # Issue 8: homographs
    ("Read present tense", "I read books daily.", "i read books daily"),
    ("Lead verb", "Lead the way.", "lead the way"),

    # Issue 9: contractions
    ("Wouldn't contraction", "I wouldn't go.", "i wouldnt go"),
    ("Couldn't contraction", "I couldn't agree.", "i couldnt agree"),

    # Issue 10: complex words
    ("Philosophy", "Study philosophy.", "study philosophy"),
    ("Acquisition", "The acquisition completed.", "the acquisition completed"),
]

class TTSPronunciationValidator:
    def __init__(self):
        print("Initializing Whisper processor...")
        self.whisper = OptimizedWhisperProcessor()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="tts_validation_"))
        print(f"Temp dir: {self.temp_dir}")

    def generate(self, text: str) -> Path:
        """Generate TTS audio"""
        output = self.temp_dir / f"{hash(text)}.mp3"
        resp = requests.post(
            f"{API_BASE}/v1/audio/speech",
            json={"input": text, "voice": VOICE, "response_format": "mp3"},
            timeout=30
        )
        if resp.status_code == 200:
            output.write_bytes(resp.content)
            return output
        raise RuntimeError(f"API error: {resp.status_code}")

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe using built-in Whisper"""
        result = self.whisper.transcribe(str(audio_path))
        if hasattr(result, 'text'):
            return result.text.strip()
        return str(result).strip()

    def normalize(self, text: str) -> str:
        """Normalize for comparison"""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = ' '.join(text.split())
        return text

    def run_validation(self) -> Dict:
        """Run full validation"""
        results = {"passed": [], "failed": [], "errors": []}

        for name, input_text, expected_normalized in TEST_CASES:
            print(f"\nTest: {name}")
            print(f"  Input: {input_text}")

            try:
                # Generate
                audio = self.generate(input_text)

                # Transcribe
                transcription = self.transcribe(audio)
                print(f"  Whisper: {transcription}")

                # Compare
                result_norm = self.normalize(transcription)
                if result_norm == expected_normalized:
                    results["passed"].append({
                        "name": name,
                        "input": input_text,
                        "transcription": transcription,
                        "expected": expected_normalized
                    })
                    print("  ✓ PASS")
                else:
                    results["failed"].append({
                        "name": name,
                        "input": input_text,
                        "transcription": transcription,
                        "expected": expected_normalized,
                        "normalized_got": result_norm
                    })
                    print(f"  ✗ FAIL")
                    print(f"    Expected: {expected_normalized}")
                    print(f"    Got: {result_norm}")

            except Exception as e:
                results["errors"].append({"name": name, "error": str(e)})
                print(f"  ✗ ERROR: {e}")

        return results

    def print_report(self, results: Dict):
        """Print validation report"""
        passed = len(results["passed"])
        failed = len(results["failed"])
        errors = len(results["errors"])
        total = passed + failed + errors

        print("\n" + "="*70)
        print("TTS PRONUNCIATION VALIDATION REPORT")
        print("="*70)
        print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Errors: {errors}")
        print(f"Success Rate: {100*passed/max(total,1):.1f}%")
        print("="*70)

        if results["failed"]:
            print("\nFAILED TESTS:")
            for f in results["failed"]:
                print(f"  • {f['name']}")
                print(f"    Input: {f['input']}")
                print(f"    Expected: {f['expected']}")
                print(f"    Got: {f['transcription']}")

        if results["errors"]:
            print("\nERRORS:")
            for e in results["errors"]:
                print(f"  • {e['name']}: {e['error']}")

        return passed, failed, errors

    def cleanup(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

def main():
    validator = TTSPronunciationValidator()
    try:
        results = validator.run_validation()
        passed, failed, errors = validator.print_report(results)

        # Save results
        output = Path("test_results/pronunciation_validation.json")
        output.parent.mkdir(exist_ok=True)
        with open(output, "w") as f:
            json.dump(results, f, indent=2)

        return 0 if failed == 0 and errors == 0 else 1
    finally:
        validator.cleanup()

if __name__ == "__main__":
    sys.exit(main())
