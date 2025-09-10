#!/usr/bin/env python3
"""
Voice cloning API endpoints for LiteTTS
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import JSONResponse, Response
from typing import Dict, List, Any, Optional
import logging
import tempfile
import os
from pathlib import Path
import shutil

from ..voice.cloning import VoiceCloner, VoiceCloneResult, AudioAnalysisResult
from ..voice.metadata import VoiceMetadataManager

try:
    from ..models import VoiceMetadata
except ImportError:
    # Fallback import from models.py file
    import sys
    from pathlib import Path
    models_path = Path(__file__).parent.parent / "models.py"
    if models_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("models", models_path)
        models_module = importlib.util.module_from_spec(spec)
        sys.modules["models"] = models_module
        spec.loader.exec_module(models_module)
        VoiceMetadata = models_module.VoiceMetadata
    else:
        # Final fallback - define minimal class
        from dataclasses import dataclass
        @dataclass
        class VoiceMetadata:
            name: str
            gender: str = "unknown"
            accent: str = "american"
            voice_type: str = "neural"
            quality_rating: float = 4.0
            language: str = "en-us"
            description: str = ""

logger = logging.getLogger(__name__)

class VoiceCloningRouter:
    """API router for voice cloning endpoints"""
    
    def __init__(self):
        self.router = APIRouter()
        self.voice_cloner = VoiceCloner()
        self.metadata_manager = VoiceMetadataManager()

        # Supported audio formats
        self.supported_formats = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
        # Setup routes
        self._setup_routes()
        
        logger.info("Voice Cloning API Router initialized")
    
    def _setup_routes(self):
        """Setup voice cloning API routes"""
        
        @self.router.post("/v1/voices/analyze")
        async def analyze_voice_sample(
            audio_file: UploadFile = File(..., description="Audio file for voice analysis")
        ):
            """
            Analyze uploaded audio file for voice cloning suitability
            
            Supports: WAV, MP3, M4A, FLAC, OGG files up to 50MB
            """
            try:
                # Validate file
                validation_error = self._validate_audio_file(audio_file)
                if validation_error:
                    raise HTTPException(status_code=400, detail=validation_error)
                
                # Save temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as temp_file:
                    shutil.copyfileobj(audio_file.file, temp_file)
                    temp_path = temp_file.name
                
                try:
                    # Analyze audio
                    analysis_result = self.voice_cloner.analyze_audio(temp_path)
                    
                    if not analysis_result.success:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Audio analysis failed: {analysis_result.error_message}"
                        )
                    
                    # Return analysis results
                    return {
                        'status': 'success',
                        'analysis': {
                            'duration': analysis_result.duration,
                            'sample_rate': analysis_result.sample_rate,
                            'channels': analysis_result.channels,
                            'quality_score': analysis_result.quality_score,
                            'voice_characteristics': analysis_result.voice_characteristics,
                            'suitability': self._assess_suitability(analysis_result)
                        },
                        'recommendations': self._get_recommendations(analysis_result)
                    }
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                        
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Voice analysis failed: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Voice analysis failed", "detail": str(e)}
                )
        
        @self.router.post("/v1/voices/create")
        async def create_custom_voice(
            audio_file: UploadFile = File(..., description="Audio file for voice cloning"),
            voice_name: str = Form(..., description="Name for the custom voice"),
            description: str = Form("", description="Optional description for the voice"),
            background_tasks: BackgroundTasks = None
        ):
            """
            Create a custom voice from an audio sample
            
            This endpoint processes the audio file and generates a BIN voice file
            compatible with the LiteTTS synthesis engine.
            """
            try:
                # Validate inputs
                validation_error = self._validate_audio_file(audio_file)
                if validation_error:
                    raise HTTPException(status_code=400, detail=validation_error)
                
                voice_name_error = self._validate_voice_name(voice_name)
                if voice_name_error:
                    raise HTTPException(status_code=400, detail=voice_name_error)
                
                # Save temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as temp_file:
                    shutil.copyfileobj(audio_file.file, temp_file)
                    temp_path = temp_file.name
                
                try:
                    # Clone voice
                    clone_result = self.voice_cloner.clone_voice(temp_path, voice_name, description)
                    
                    if not clone_result.success:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Voice cloning failed: {clone_result.error_message}"
                        )

                    # Register the custom voice with the metadata manager
                    try:
                        voice_metadata = VoiceMetadata(
                            name=voice_name,
                            gender="unknown",  # Could be enhanced with voice analysis
                            accent="custom",
                            voice_type="cloned",
                            quality_rating=clone_result.similarity_score * 5.0 if clone_result.similarity_score else 4.0,
                            language="en-us",  # Could be detected from audio
                            description=description or f"Custom cloned voice: {voice_name}"
                        )
                        self.metadata_manager.add_custom_voice(voice_name, voice_metadata)
                        logger.info(f"Registered custom voice metadata for: {voice_name}")
                    except Exception as e:
                        logger.warning(f"Failed to register voice metadata for {voice_name}: {e}")

                    # Refresh the main app's voice list so the new voice is available for synthesis
                    try:
                        import app
                        app_instance = getattr(app, 'app_instance', None)
                        if app_instance and hasattr(app_instance, 'refresh_available_voices'):
                            app_instance.refresh_available_voices()
                            logger.info(f"Refreshed main app voice list after creating: {voice_name}")
                    except Exception as e:
                        logger.warning(f"Failed to refresh main app voice list: {e}")

                    # Return success response
                    return {
                        'status': 'success',
                        'voice': {
                            'name': clone_result.voice_name,
                            'file_path': clone_result.voice_file_path,
                            'similarity_score': clone_result.similarity_score,
                            'metadata': clone_result.metadata
                        },
                        'message': f"Voice '{voice_name}' created successfully"
                    }
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                        
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Voice creation failed: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Voice creation failed", "detail": str(e)}
                )
        
        @self.router.get("/v1/voices/custom")
        async def list_custom_voices():
            """
            List all custom voices created through voice cloning
            """
            try:
                custom_voices = self.voice_cloner.list_custom_voices()
                
                return {
                    'status': 'success',
                    'custom_voices': custom_voices,
                    'total_count': len(custom_voices)
                }
                
            except Exception as e:
                logger.error(f"Failed to list custom voices: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Failed to list custom voices", "detail": str(e)}
                )
        
        @self.router.delete("/v1/voices/custom/{voice_name}")
        async def delete_custom_voice(voice_name: str):
            """
            Delete a custom voice
            """
            try:
                success = self.voice_cloner.delete_custom_voice(voice_name)

                if success:
                    # Also remove from metadata manager
                    try:
                        self.metadata_manager.remove_voice(voice_name)
                        logger.info(f"Removed voice metadata for: {voice_name}")
                    except Exception as e:
                        logger.warning(f"Failed to remove voice metadata for {voice_name}: {e}")

                    # Refresh the main app's voice list so the deleted voice is removed
                    try:
                        import app
                        app_instance = getattr(app, 'app_instance', None)
                        if app_instance and hasattr(app_instance, 'refresh_available_voices'):
                            app_instance.refresh_available_voices()
                            logger.info(f"Refreshed main app voice list after deleting: {voice_name}")
                    except Exception as e:
                        logger.warning(f"Failed to refresh main app voice list: {e}")

                    return {
                        'status': 'success',
                        'message': f"Voice '{voice_name}' deleted successfully"
                    }
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Voice '{voice_name}' not found"
                    )
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to delete voice {voice_name}: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to delete voice {voice_name}", "detail": str(e)}
                )
        
        @self.router.post("/v1/audio/clone")
        async def generate_with_cloned_voice(
            text: str = Form(..., description="Text to synthesize"),
            voice_name: str = Form(..., description="Name of the custom voice to use"),
            response_format: str = Form("mp3", description="Audio format (mp3, wav)"),
            speed: float = Form(1.0, description="Speech speed (0.5-2.0)")
        ):
            """
            Generate speech using a cloned voice

            This endpoint redirects to the existing TTS API with the custom voice.
            """
            try:
                # Check if custom voice exists
                custom_voices = self.voice_cloner.list_custom_voices()
                if voice_name not in custom_voices:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Custom voice '{voice_name}' not found"
                    )

                # Use the model directly for synthesis
                try:
                    # Import the global model instance
                    import app

                    # Get the app instance from the global scope
                    app_instance = getattr(app, 'app_instance', None)

                    if not app_instance:
                        raise HTTPException(
                            status_code=500,
                            detail="TTS service not available"
                        )

                    # Create TTS request
                    from LiteTTS.models import TTSRequest
                    tts_request = TTSRequest(
                        input=text,
                        voice=voice_name,
                        response_format=response_format,
                        speed=speed,
                        stream=False
                    )

                    # Use the app's internal synthesis method
                    return await app_instance._generate_speech_internal(tts_request)

                except Exception as synthesis_error:
                    logger.error(f"Direct synthesis failed: {synthesis_error}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Voice synthesis failed: {str(synthesis_error)}"
                    )

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Cloned voice synthesis failed: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Cloned voice synthesis failed", "detail": str(e)}
                )
    
    def _validate_audio_file(self, audio_file: UploadFile) -> Optional[str]:
        """Validate uploaded audio file"""
        
        # Check file size
        if hasattr(audio_file, 'size') and audio_file.size > self.max_file_size:
            return f"File too large: {audio_file.size / 1024 / 1024:.1f}MB (max: {self.max_file_size / 1024 / 1024}MB)"
        
        # Check file extension
        if audio_file.filename:
            file_ext = Path(audio_file.filename).suffix.lower()
            if file_ext not in self.supported_formats:
                return f"Unsupported format: {file_ext}. Supported: {', '.join(self.supported_formats)}"
        
        # Check content type
        if audio_file.content_type and not audio_file.content_type.startswith('audio/'):
            return f"Invalid content type: {audio_file.content_type}. Expected audio file."
        
        return None
    
    def _validate_voice_name(self, voice_name: str) -> Optional[str]:
        """Validate voice name"""
        
        if not voice_name or not voice_name.strip():
            return "Voice name cannot be empty"
        
        if len(voice_name) > 50:
            return "Voice name too long (max: 50 characters)"
        
        # Check for valid characters (alphanumeric, underscore, hyphen)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', voice_name):
            return "Voice name can only contain letters, numbers, underscores, and hyphens"
        
        # Check if voice already exists
        existing_voices = self.voice_cloner.list_custom_voices()
        if voice_name in existing_voices:
            return f"Voice name '{voice_name}' already exists"
        
        return None
    
    def _assess_suitability(self, analysis: AudioAnalysisResult) -> Dict[str, Any]:
        """Assess audio suitability for voice cloning"""
        
        suitability = {
            'overall_score': 0.0,
            'duration_ok': False,
            'quality_ok': False,
            'recommended': False,
            'issues': []
        }
        
        # Duration check
        if analysis.duration >= self.voice_cloner.min_audio_duration and analysis.duration <= self.voice_cloner.max_audio_duration:
            suitability['duration_ok'] = True
        else:
            if analysis.duration < self.voice_cloner.min_audio_duration:
                suitability['issues'].append(f"Audio too short ({analysis.duration:.1f}s, need ≥{self.voice_cloner.min_audio_duration}s)")
            else:
                suitability['issues'].append(f"Audio too long ({analysis.duration:.1f}s, max {self.voice_cloner.max_audio_duration}s)")
        
        # Quality check
        if analysis.quality_score >= 0.5:
            suitability['quality_ok'] = True
        else:
            suitability['issues'].append(f"Audio quality too low ({analysis.quality_score:.2f}, need ≥0.5)")
        
        # Overall assessment
        suitability['overall_score'] = analysis.quality_score * (1.0 if suitability['duration_ok'] else 0.5)
        suitability['recommended'] = suitability['duration_ok'] and suitability['quality_ok']
        
        return suitability
    
    def _get_recommendations(self, analysis: AudioAnalysisResult) -> List[str]:
        """Get recommendations for improving voice cloning quality"""
        
        recommendations = []
        
        if analysis.duration < self.voice_cloner.min_audio_duration:
            recommendations.append(f"Record at least {self.voice_cloner.min_audio_duration} seconds of clear speech")
        
        if analysis.duration > self.voice_cloner.max_audio_duration:
            recommendations.append(f"Trim audio to under {self.voice_cloner.max_audio_duration} seconds")
        
        if analysis.quality_score < 0.7:
            recommendations.append("Use a quiet environment with minimal background noise")
            recommendations.append("Speak clearly and at a consistent volume")
            recommendations.append("Use a good quality microphone if possible")
        
        if analysis.sample_rate < 16000:
            recommendations.append("Use higher quality audio (at least 16kHz sample rate)")
        
        if not recommendations:
            recommendations.append("Audio quality looks good for voice cloning!")
        
        return recommendations
    
    def get_router(self) -> APIRouter:
        """Get the configured router"""
        return self.router
