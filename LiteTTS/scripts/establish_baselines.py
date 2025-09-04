#!/usr/bin/env python3
"""
Baseline Metrics Establishment Script

Creates baseline audio files and WER scores for all available voices
to establish quality benchmarks for the LiteTTS system.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import shutil

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from LiteTTS.voice.discovery import VoiceDiscovery
from LiteTTS.validation.audio_quality_validator import AudioQualityValidator

def get_available_voices() -> List[str]:
    """Get list of all available voices"""
    try:
        discovery = VoiceDiscovery()
        voices = discovery.get_available_voices()
        return sorted(voices)
    except Exception as e:
        print(f"❌ Failed to discover voices: {e}")
        # Fallback to common voice names
        return [
            "af_heart", "af_alloy", "af_nova", "af_sky", "af_bella",
            "am_adam", "am_echo", "am_onyx", "am_fable", "am_michael"
        ]

def create_baseline_audio(voice: str, output_dir: Path) -> str:
    """
    Create baseline audio file for a voice.
    
    Args:
        voice: Voice name
        output_dir: Output directory for audio files
        
    Returns:
        Path to created audio file
    """
    baseline_text = "This is a baseline audio quality test for voice validation using Whisper transcription."
    audio_path = output_dir / f"baseline_{voice}.mp3"
    
    try:
        # Use curl to generate audio via API (simpler than importing TTS engine)
        import subprocess
        
        curl_cmd = [
            "curl", "-X", "POST",
            "http://localhost:8357/v1/audio/speech",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "input": baseline_text,
                "voice": voice,
                "response_format": "mp3"
            }),
            "--output", str(audio_path),
            "--silent"
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and audio_path.exists():
            return str(audio_path)
        else:
            print(f"❌ Failed to generate audio for {voice}: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating audio for {voice}: {e}")
        return None

def establish_voice_baselines(voices: List[str], output_dir: str) -> Dict[str, Any]:
    """
    Establish baseline metrics for all voices.
    
    Args:
        voices: List of voice names
        output_dir: Output directory for baseline files
        
    Returns:
        Dictionary containing baseline metrics for each voice
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    baseline_metrics = {
        "timestamp": time.time(),
        "total_voices": len(voices),
        "successful_baselines": 0,
        "failed_voices": [],
        "voice_metrics": {}
    }
    
    # Initialize audio quality validator
    try:
        validator = AudioQualityValidator()
        validator.initialize()
        print("✅ AudioQualityValidator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize validator: {e}")
        return baseline_metrics
    
    baseline_text = "This is a baseline audio quality test for voice validation using Whisper transcription."
    
    print(f"🎯 Establishing baselines for {len(voices)} voices...")
    
    for i, voice in enumerate(voices, 1):
        print(f"\nProcessing voice {i}/{len(voices)}: {voice}")
        
        try:
            # Generate baseline audio
            audio_path = create_baseline_audio(voice, output_path)
            
            if not audio_path:
                baseline_metrics["failed_voices"].append(voice)
                continue
            
            print(f"✅ Generated audio: {Path(audio_path).name}")
            
            # Validate audio quality and calculate WER
            result = validator.validate_transcription(audio_path, baseline_text)
            
            if result and result.metrics:
                voice_metrics = {
                    "wer": result.metrics.wer,
                    "cer": result.metrics.cer,
                    "bleu_score": result.metrics.bleu_score,
                    "transcription_time": result.metrics.transcription_time,
                    "audio_duration": result.metrics.audio_duration,
                    "rtf": result.metrics.rtf,
                    "confidence_score": result.metrics.confidence_score,
                    "word_count": result.metrics.word_count,
                    "transcribed_text": result.transcribed_text,
                    "audio_file": Path(audio_path).name
                }
                
                baseline_metrics["voice_metrics"][voice] = voice_metrics
                baseline_metrics["successful_baselines"] += 1
                
                print(f"✅ WER: {result.metrics.wer:.3f}, Confidence: {result.metrics.confidence_score:.3f}")
                
            else:
                print(f"❌ Failed to validate audio for {voice}")
                baseline_metrics["failed_voices"].append(voice)
                
        except Exception as e:
            print(f"❌ Error processing {voice}: {e}")
            baseline_metrics["failed_voices"].append(voice)
            continue
    
    return baseline_metrics

def main():
    """Main baseline establishment execution"""
    
    parser = argparse.ArgumentParser(description="Establish baseline metrics for LiteTTS voices")
    parser.add_argument("--all-voices", action="store_true", help="Process all available voices")
    parser.add_argument("--output-dir", default="baselines", help="Output directory for baseline files")
    parser.add_argument("--voices", nargs="+", help="Specific voices to process")
    
    args = parser.parse_args()
    
    print("🎯 LiteTTS Baseline Metrics Establishment")
    print("=" * 50)
    
    # Get voices to process
    if args.all_voices:
        voices = get_available_voices()
        print(f"Processing all {len(voices)} available voices")
    elif args.voices:
        voices = args.voices
        print(f"Processing {len(voices)} specified voices")
    else:
        # Default to a few test voices
        voices = ["af_heart", "af_alloy", "am_adam", "am_echo"]
        print(f"Processing {len(voices)} default test voices")
    
    print(f"Output directory: {args.output_dir}")
    print(f"Voices: {', '.join(voices)}")
    print()
    
    # Establish baselines
    start_time = time.time()
    baseline_metrics = establish_voice_baselines(voices, args.output_dir)
    total_time = time.time() - start_time
    
    # Save baseline metrics to JSON
    metrics_file = Path(args.output_dir) / "baseline_metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump(baseline_metrics, f, indent=2)
    
    # Print results
    print(f"\n" + "=" * 50)
    print(f"📊 BASELINE ESTABLISHMENT RESULTS:")
    print(f"   Total voices: {baseline_metrics['total_voices']}")
    print(f"   Successful baselines: {baseline_metrics['successful_baselines']}")
    print(f"   Failed voices: {len(baseline_metrics['failed_voices'])}")
    print(f"   Processing time: {total_time:.1f}s")
    print(f"   Baseline metrics saved: {metrics_file}")
    
    if baseline_metrics["failed_voices"]:
        print(f"   Failed voices: {', '.join(baseline_metrics['failed_voices'])}")
    
    # Success criteria
    success_rate = baseline_metrics['successful_baselines'] / baseline_metrics['total_voices']
    success = success_rate >= 0.8  # At least 80% success rate
    
    print(f"\nOverall Status: {'✅ PASS' if success else '❌ FAIL'} ({success_rate:.1%} success rate)")
    
    if success:
        print("\n🎉 Baseline metrics established successfully!")
        print(f"✅ {baseline_metrics['successful_baselines']} voice baselines created")
        print(f"✅ Baseline metrics saved to {metrics_file}")
        print(f"✅ Audio files saved to {args.output_dir}/")
        return 0
    else:
        print("\n⚠️ Baseline establishment needs attention")
        print("Some voices failed to generate proper baselines")
        return 1

if __name__ == "__main__":
    exit(main())
