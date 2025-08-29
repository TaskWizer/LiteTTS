#!/usr/bin/env python3
"""
Systematic Audio Pipeline Diagnosis for LiteTTS
Traces each stage of the TTS pipeline to identify where audio quality issues occur
"""

import os
import sys
import json
import logging
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioPipelineDiagnostic:
    """Comprehensive diagnostic tool for TTS audio pipeline"""
    
    def __init__(self, output_dir: str = "pipeline_diagnosis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.diagnosis_results = []
        
        logger.info("🔬 Audio Pipeline Diagnostic initialized")
        logger.info(f"📁 Output directory: {self.output_dir.absolute()}")
    
    def diagnose_full_pipeline(self, test_text: str = "Hello world", voice: str = "af_heart") -> Dict[str, Any]:
        """Diagnose the complete TTS pipeline with detailed stage-by-stage analysis"""
        logger.info(f"🔬 Starting full pipeline diagnosis for: '{test_text}' with voice '{voice}'")
        
        diagnosis = {
            "test_text": test_text,
            "voice": voice,
            "timestamp": datetime.now().isoformat(),
            "stages": {},
            "overall_success": False,
            "issues_found": [],
            "recommendations": []
        }
        
        try:
            # Stage 1: Text Input Processing
            stage1_result = self._diagnose_text_processing(test_text)
            diagnosis["stages"]["text_processing"] = stage1_result
            
            # Stage 2: TTS Configuration Setup
            stage2_result = self._diagnose_tts_configuration()
            diagnosis["stages"]["tts_configuration"] = stage2_result
            
            # Stage 3: Model Loading and Initialization
            stage3_result = self._diagnose_model_initialization()
            diagnosis["stages"]["model_initialization"] = stage3_result
            
            # Stage 4: Voice Loading and Validation
            stage4_result = self._diagnose_voice_loading(voice)
            diagnosis["stages"]["voice_loading"] = stage4_result
            
            # Stage 5: Phoneme Conversion
            stage5_result = self._diagnose_phoneme_conversion(test_text)
            diagnosis["stages"]["phoneme_conversion"] = stage5_result
            
            # Stage 6: ONNX Model Inference
            stage6_result = self._diagnose_onnx_inference(test_text, voice)
            diagnosis["stages"]["onnx_inference"] = stage6_result
            
            # Stage 7: Audio Post-processing
            stage7_result = self._diagnose_audio_postprocessing()
            diagnosis["stages"]["audio_postprocessing"] = stage7_result
            
            # Stage 8: Audio Output Generation
            stage8_result = self._diagnose_audio_output(test_text, voice)
            diagnosis["stages"]["audio_output"] = stage8_result
            
            # Analyze results and generate recommendations
            diagnosis["overall_success"] = all(
                stage.get("success", False) for stage in diagnosis["stages"].values()
            )
            
            diagnosis["issues_found"] = self._collect_issues(diagnosis["stages"])
            diagnosis["recommendations"] = self._generate_recommendations(diagnosis["stages"])
            
            logger.info(f"🔬 Pipeline diagnosis completed. Success: {diagnosis['overall_success']}")
            
        except Exception as e:
            logger.error(f"❌ Pipeline diagnosis failed: {e}")
            diagnosis["error"] = str(e)
            diagnosis["issues_found"].append(f"Critical pipeline failure: {e}")
        
        return diagnosis
    
    def _diagnose_text_processing(self, text: str) -> Dict[str, Any]:
        """Diagnose text input processing stage"""
        logger.info("🔍 Stage 1: Diagnosing text processing...")
        
        stage_result = {
            "stage_name": "text_processing",
            "success": False,
            "input_text": text,
            "processed_text": "",
            "processing_time_ms": 0,
            "issues": [],
            "details": {}
        }
        
        start_time = time.time()
        
        try:
            # Import text processing components
            from LiteTTS.text.phonemizer_preprocessor import phonemizer_preprocessor
            
            # Test basic text validation
            if not text or not text.strip():
                stage_result["issues"].append("Empty or whitespace-only input text")
                return stage_result
            
            # Test text preprocessing
            processed_text = phonemizer_preprocessor.preprocess_text(text)
            
            stage_result["processed_text"] = processed_text
            stage_result["details"]["original_length"] = len(text)
            stage_result["details"]["processed_length"] = len(processed_text)
            stage_result["details"]["text_changed"] = text != processed_text
            
            # Check for potential issues
            if len(processed_text) == 0:
                stage_result["issues"].append("Text preprocessing resulted in empty string")
            elif len(processed_text) > len(text) * 3:
                stage_result["issues"].append("Text preprocessing significantly expanded text (possible over-processing)")
            
            stage_result["success"] = len(stage_result["issues"]) == 0
            
        except Exception as e:
            stage_result["issues"].append(f"Text processing error: {e}")
            logger.error(f"Text processing failed: {e}")
        
        stage_result["processing_time_ms"] = (time.time() - start_time) * 1000
        logger.info(f"✅ Stage 1 completed in {stage_result['processing_time_ms']:.1f}ms")
        
        return stage_result
    
    def _diagnose_tts_configuration(self) -> Dict[str, Any]:
        """Diagnose TTS configuration setup"""
        logger.info("🔍 Stage 2: Diagnosing TTS configuration...")
        
        stage_result = {
            "stage_name": "tts_configuration",
            "success": False,
            "configuration": {},
            "issues": [],
            "details": {}
        }
        
        try:
            from LiteTTS.config import config
            from LiteTTS.models import TTSConfiguration
            
            # Check configuration values
            config_dict = {
                "model_path": config.tts.model_path,
                "voices_path": config.tts.voices_path,
                "device": config.tts.device,
                "sample_rate": config.tts.sample_rate,
                "default_voice": config.tts.default_voice
            }
            
            stage_result["configuration"] = config_dict
            
            # Validate configuration
            model_path = Path(config.tts.model_path)
            if not model_path.exists():
                stage_result["issues"].append(f"Model file not found: {model_path}")
            
            voices_path = Path(config.tts.voices_path)
            if not voices_path.exists():
                stage_result["issues"].append(f"Voices directory not found: {voices_path}")
            
            if config.tts.sample_rate <= 0:
                stage_result["issues"].append(f"Invalid sample rate: {config.tts.sample_rate}")
            
            # Test TTSConfiguration creation
            tts_config = TTSConfiguration(
                model_path=config.tts.model_path,
                voices_path=config.tts.voices_path,
                device=config.tts.device,
                sample_rate=config.tts.sample_rate,
                chunk_size=getattr(config.tts, 'chunk_size', 100),
                cache_size=getattr(config.cache, 'max_size', 1000),
                max_text_length=getattr(config.tts, 'max_text_length', 1000),
                default_voice=config.tts.default_voice
            )
            
            stage_result["details"]["tts_config_created"] = True
            stage_result["success"] = len(stage_result["issues"]) == 0
            
        except Exception as e:
            stage_result["issues"].append(f"Configuration error: {e}")
            logger.error(f"TTS configuration failed: {e}")
        
        logger.info(f"✅ Stage 2 completed. Issues: {len(stage_result['issues'])}")
        return stage_result
    
    def _diagnose_model_initialization(self) -> Dict[str, Any]:
        """Diagnose model loading and initialization"""
        logger.info("🔍 Stage 3: Diagnosing model initialization...")
        
        stage_result = {
            "stage_name": "model_initialization",
            "success": False,
            "model_info": {},
            "issues": [],
            "details": {}
        }
        
        try:
            from LiteTTS.config import config
            
            # Check if model file exists and get info
            model_path = Path(config.tts.model_path)
            if model_path.exists():
                stage_result["model_info"]["path"] = str(model_path)
                stage_result["model_info"]["size_bytes"] = model_path.stat().st_size
                stage_result["model_info"]["size_mb"] = model_path.stat().st_size / (1024 * 1024)
            else:
                stage_result["issues"].append(f"Model file not found: {model_path}")
                return stage_result
            
            # Test model loading with kokoro_onnx
            try:
                from kokoro_onnx import Kokoro
                
                # Check if voices file exists
                voices_path = Path(config.tts.voices_path)
                voices_file = None
                
                # Look for combined voices file
                combined_file = voices_path / "voices.bin"
                if combined_file.exists():
                    voices_file = str(combined_file)
                else:
                    # Look for individual voice files
                    voice_files = list(voices_path.glob("*.bin"))
                    if voice_files:
                        # Use first available voice file for testing
                        voices_file = str(voice_files[0])
                    else:
                        stage_result["issues"].append("No voice files found")
                        return stage_result
                
                stage_result["details"]["voices_file"] = voices_file
                
                # Test model initialization (this might take time)
                logger.info("Loading Kokoro model for testing...")
                model = Kokoro(str(model_path), voices_file)
                
                stage_result["details"]["model_loaded"] = True
                stage_result["details"]["available_voices"] = len(model.get_voices()) if hasattr(model, 'get_voices') else "unknown"
                
                stage_result["success"] = True
                
            except Exception as e:
                stage_result["issues"].append(f"Model loading error: {e}")
                logger.error(f"Model loading failed: {e}")
        
        except Exception as e:
            stage_result["issues"].append(f"Model initialization error: {e}")
            logger.error(f"Model initialization failed: {e}")
        
        logger.info(f"✅ Stage 3 completed. Success: {stage_result['success']}")
        return stage_result
    
    def _diagnose_voice_loading(self, voice: str) -> Dict[str, Any]:
        """Diagnose voice loading and validation"""
        logger.info(f"🔍 Stage 4: Diagnosing voice loading for '{voice}'...")
        
        stage_result = {
            "stage_name": "voice_loading",
            "success": False,
            "voice": voice,
            "voice_info": {},
            "issues": [],
            "details": {}
        }
        
        try:
            from LiteTTS.config import config
            
            voices_path = Path(config.tts.voices_path)
            voice_file = voices_path / f"{voice}.bin"
            
            if voice_file.exists():
                stage_result["voice_info"]["path"] = str(voice_file)
                stage_result["voice_info"]["size_bytes"] = voice_file.stat().st_size
                stage_result["voice_info"]["size_kb"] = voice_file.stat().st_size / 1024
                
                # Check if voice file is reasonable size
                if voice_file.stat().st_size < 1000:
                    stage_result["issues"].append(f"Voice file suspiciously small: {voice_file.stat().st_size} bytes")
                elif voice_file.stat().st_size > 10 * 1024 * 1024:  # 10MB
                    stage_result["issues"].append(f"Voice file suspiciously large: {voice_file.stat().st_size} bytes")
                
                stage_result["success"] = len(stage_result["issues"]) == 0
            else:
                stage_result["issues"].append(f"Voice file not found: {voice_file}")
                
                # List available voices
                available_voices = [f.stem for f in voices_path.glob("*.bin")]
                stage_result["details"]["available_voices"] = available_voices
                
                if available_voices:
                    stage_result["issues"].append(f"Available voices: {', '.join(available_voices[:10])}")
        
        except Exception as e:
            stage_result["issues"].append(f"Voice loading error: {e}")
            logger.error(f"Voice loading failed: {e}")
        
        logger.info(f"✅ Stage 4 completed. Success: {stage_result['success']}")
        return stage_result
    
    def _diagnose_phoneme_conversion(self, text: str) -> Dict[str, Any]:
        """Diagnose phoneme conversion process"""
        logger.info("🔍 Stage 5: Diagnosing phoneme conversion...")
        
        stage_result = {
            "stage_name": "phoneme_conversion",
            "success": False,
            "input_text": text,
            "phonemes": "",
            "issues": [],
            "details": {}
        }
        
        try:
            # This stage would test phoneme conversion if available
            # For now, we'll simulate the check
            stage_result["details"]["phoneme_conversion_available"] = False
            stage_result["issues"].append("Phoneme conversion diagnosis not implemented")
            stage_result["success"] = True  # Don't fail on this for now
            
        except Exception as e:
            stage_result["issues"].append(f"Phoneme conversion error: {e}")
            logger.error(f"Phoneme conversion failed: {e}")
        
        logger.info(f"✅ Stage 5 completed. Success: {stage_result['success']}")
        return stage_result
    
    def _diagnose_onnx_inference(self, text: str, voice: str) -> Dict[str, Any]:
        """Diagnose ONNX model inference"""
        logger.info("🔍 Stage 6: Diagnosing ONNX inference...")
        
        stage_result = {
            "stage_name": "onnx_inference",
            "success": False,
            "inference_time_ms": 0,
            "output_shape": None,
            "issues": [],
            "details": {}
        }
        
        start_time = time.time()
        
        try:
            # Test ONNX inference through the TTS synthesizer
            from LiteTTS.tts import TTSSynthesizer
            from LiteTTS.config import config
            from LiteTTS.models import TTSRequest, TTSConfiguration
            
            # Create configuration
            tts_config = TTSConfiguration(
                model_path=config.tts.model_path,
                voices_path=config.tts.voices_path,
                device=config.tts.device,
                sample_rate=config.tts.sample_rate,
                chunk_size=getattr(config.tts, 'chunk_size', 100),
                cache_size=getattr(config.cache, 'max_size', 1000),
                max_text_length=getattr(config.tts, 'max_text_length', 1000),
                default_voice=config.tts.default_voice
            )
            
            # Initialize synthesizer
            synthesizer = TTSSynthesizer(tts_config)
            
            # Create request
            request = TTSRequest(
                input=text,
                voice=voice,
                response_format="wav",
                speed=1.0,
                stream=False,
                volume_multiplier=1.0
            )
            
            # Test synthesis
            audio_segment = synthesizer.synthesize(request)
            
            stage_result["details"]["audio_segment_created"] = True
            
            if hasattr(audio_segment, 'audio_data'):
                if hasattr(audio_segment.audio_data, 'shape'):
                    stage_result["output_shape"] = list(audio_segment.audio_data.shape)
                stage_result["details"]["has_audio_data"] = True
                
                # Check audio data properties
                if hasattr(audio_segment.audio_data, '__len__'):
                    data_length = len(audio_segment.audio_data)
                    stage_result["details"]["audio_data_length"] = data_length
                    
                    if data_length == 0:
                        stage_result["issues"].append("Audio data is empty")
                    elif data_length < 1000:
                        stage_result["issues"].append(f"Audio data suspiciously short: {data_length} samples")
            else:
                stage_result["issues"].append("Audio segment missing audio_data attribute")
            
            stage_result["success"] = len(stage_result["issues"]) == 0
            
        except Exception as e:
            stage_result["issues"].append(f"ONNX inference error: {e}")
            logger.error(f"ONNX inference failed: {e}")
        
        stage_result["inference_time_ms"] = (time.time() - start_time) * 1000
        logger.info(f"✅ Stage 6 completed in {stage_result['inference_time_ms']:.1f}ms")
        
        return stage_result
    
    def _diagnose_audio_postprocessing(self) -> Dict[str, Any]:
        """Diagnose audio post-processing"""
        logger.info("🔍 Stage 7: Diagnosing audio post-processing...")
        
        stage_result = {
            "stage_name": "audio_postprocessing",
            "success": True,  # Assume success for now
            "issues": [],
            "details": {}
        }
        
        try:
            # Test audio processor availability
            from LiteTTS.audio.processor import AudioProcessor
            
            audio_processor = AudioProcessor()
            stage_result["details"]["audio_processor_available"] = True
            stage_result["details"]["supported_formats"] = ["wav", "mp3"]  # Common formats
            
        except Exception as e:
            stage_result["issues"].append(f"Audio post-processing error: {e}")
            stage_result["success"] = False
            logger.error(f"Audio post-processing failed: {e}")
        
        logger.info(f"✅ Stage 7 completed. Success: {stage_result['success']}")
        return stage_result
    
    def _diagnose_audio_output(self, text: str, voice: str) -> Dict[str, Any]:
        """Diagnose final audio output generation"""
        logger.info("🔍 Stage 8: Diagnosing audio output generation...")
        
        stage_result = {
            "stage_name": "audio_output",
            "success": False,
            "output_file": "",
            "file_size_bytes": 0,
            "issues": [],
            "details": {}
        }
        
        try:
            # Generate a test audio file
            output_file = self.output_dir / f"diagnosis_test_{self.timestamp}.wav"
            
            # Use the same process as the main audio generation
            from LiteTTS.tts import TTSSynthesizer
            from LiteTTS.config import config
            from LiteTTS.models import TTSRequest, TTSConfiguration
            from LiteTTS.audio.processor import AudioProcessor
            
            # Create configuration
            tts_config = TTSConfiguration(
                model_path=config.tts.model_path,
                voices_path=config.tts.voices_path,
                device=config.tts.device,
                sample_rate=config.tts.sample_rate,
                chunk_size=getattr(config.tts, 'chunk_size', 100),
                cache_size=getattr(config.cache, 'max_size', 1000),
                max_text_length=getattr(config.tts, 'max_text_length', 1000),
                default_voice=config.tts.default_voice
            )
            
            # Initialize components
            synthesizer = TTSSynthesizer(tts_config)
            audio_processor = AudioProcessor()
            
            # Create request
            request = TTSRequest(
                input=text,
                voice=voice,
                response_format="wav",
                speed=1.0,
                stream=False,
                volume_multiplier=1.0
            )
            
            # Generate audio
            audio_segment = synthesizer.synthesize(request)
            
            # Convert to bytes
            audio_bytes = audio_processor.convert_format(audio_segment, "wav")
            
            # Save to file
            with open(output_file, 'wb') as f:
                f.write(audio_bytes)
            
            stage_result["output_file"] = str(output_file)
            stage_result["file_size_bytes"] = len(audio_bytes)
            stage_result["details"]["audio_bytes_length"] = len(audio_bytes)
            
            # Validate output
            if len(audio_bytes) < 100:
                stage_result["issues"].append(f"Output file too small: {len(audio_bytes)} bytes")
            elif not output_file.exists():
                stage_result["issues"].append("Output file was not created")
            else:
                stage_result["success"] = True
            
        except Exception as e:
            stage_result["issues"].append(f"Audio output error: {e}")
            logger.error(f"Audio output failed: {e}")
        
        logger.info(f"✅ Stage 8 completed. Success: {stage_result['success']}")
        return stage_result
    
    def _collect_issues(self, stages: Dict[str, Any]) -> List[str]:
        """Collect all issues from all stages"""
        all_issues = []
        for stage_name, stage_data in stages.items():
            issues = stage_data.get("issues", [])
            for issue in issues:
                all_issues.append(f"[{stage_name}] {issue}")
        return all_issues
    
    def _generate_recommendations(self, stages: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on stage results"""
        recommendations = []
        
        # Check for common issues and provide recommendations
        for stage_name, stage_data in stages.items():
            if not stage_data.get("success", False):
                recommendations.append(f"Fix issues in {stage_name} stage")
        
        # Add specific recommendations based on patterns
        if any("Model file not found" in issue for stage in stages.values() for issue in stage.get("issues", [])):
            recommendations.append("Ensure model files are properly downloaded and accessible")
        
        if any("Voice file not found" in issue for stage in stages.values() for issue in stage.get("issues", [])):
            recommendations.append("Verify voice files are available in the voices directory")
        
        if any("Audio data is empty" in issue for stage in stages.values() for issue in stage.get("issues", [])):
            recommendations.append("Check ONNX model inference - may be producing empty audio")
        
        return recommendations
    
    def save_diagnosis_report(self, diagnosis: Dict[str, Any]) -> str:
        """Save comprehensive diagnosis report"""
        report_file = self.output_dir / f"pipeline_diagnosis_report_{self.timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(diagnosis, f, indent=2)
        
        logger.info(f"📊 Diagnosis report saved: {report_file}")
        return str(report_file)
    
    def print_diagnosis_summary(self, diagnosis: Dict[str, Any]):
        """Print comprehensive summary of diagnosis results"""
        print("\n" + "="*80)
        print("🔬 AUDIO PIPELINE DIAGNOSIS RESULTS")
        print("="*80)
        print(f"📅 Diagnosis Date: {self.timestamp}")
        print(f"📝 Test Text: '{diagnosis['test_text']}'")
        print(f"🎤 Voice: {diagnosis['voice']}")
        print(f"✅ Overall Success: {'YES' if diagnosis['overall_success'] else 'NO'}")
        print(f"🚨 Total Issues Found: {len(diagnosis['issues_found'])}")
        
        print("\n📋 STAGE-BY-STAGE RESULTS:")
        for stage_name, stage_data in diagnosis["stages"].items():
            status = "✅" if stage_data.get("success", False) else "❌"
            print(f"  {status} {stage_name.replace('_', ' ').title()}")
            
            issues = stage_data.get("issues", [])
            if issues:
                for issue in issues[:3]:  # Show first 3 issues
                    print(f"      ⚠️ {issue}")
                if len(issues) > 3:
                    print(f"      ... and {len(issues) - 3} more issues")
        
        if diagnosis["issues_found"]:
            print(f"\n🚨 ALL ISSUES FOUND:")
            for issue in diagnosis["issues_found"][:10]:  # Show first 10 issues
                print(f"  • {issue}")
            if len(diagnosis["issues_found"]) > 10:
                print(f"  ... and {len(diagnosis['issues_found']) - 10} more issues")
        
        if diagnosis["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in diagnosis["recommendations"]:
                print(f"  • {rec}")
        
        print("="*80)

def main():
    """Main execution function"""
    print("🔬 LiteTTS Audio Pipeline Diagnosis")
    print("="*60)
    
    try:
        # Initialize diagnostic tool
        diagnostic = AudioPipelineDiagnostic()
        
        # Run full pipeline diagnosis
        diagnosis = diagnostic.diagnose_full_pipeline()
        
        # Save diagnosis report
        report_file = diagnostic.save_diagnosis_report(diagnosis)
        
        # Print summary
        diagnostic.print_diagnosis_summary(diagnosis)
        
        print(f"\n📊 Detailed diagnosis report saved to: {report_file}")
        print("✅ Audio pipeline diagnosis completed!")
        
        return 0 if diagnosis["overall_success"] else 1
        
    except Exception as e:
        logger.error(f"❌ Audio pipeline diagnosis failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
