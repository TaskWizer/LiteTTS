#!/usr/bin/env python3
"""
FastAPI router for TTS API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Dict, List, Any, Optional
import logging
import time

from LiteTTS.models import TTSRequest, TTSResponse, TTSConfiguration
from ..tts.synthesizer import TTSSynthesizer
from ..cache.audio_cache import AudioCache, TextCache
from .validators import RequestValidator
from .error_handler import ErrorHandler
from .response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)

class TTSAPIRouter:
    """Main API router for TTS endpoints"""
    
    def __init__(self, config: TTSConfiguration):
        self.config = config
        self.router = APIRouter()
        
        # Initialize components
        self.synthesizer = TTSSynthesizer(config)
        self.audio_cache = AudioCache()
        self.text_cache = TextCache()
        self.validator = RequestValidator(self.synthesizer)
        self.error_handler = ErrorHandler()
        self.response_formatter = ResponseFormatter()
        
        # Setup routes
        self._setup_routes()
        
        logger.info("TTS API Router initialized")
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.router.post("/v1/audio/speech")
        async def create_speech(
            request: TTSRequest,
            background_tasks: BackgroundTasks
        ):
            """Create speech from text"""
            start_time = time.time()
            
            try:
                # Validate request
                validation_errors = self.validator.validate_request(request)
                if validation_errors:
                    raise HTTPException(
                        status_code=400,
                        detail={"errors": validation_errors}
                    )
                
                # Check cache first
                cached_audio = self.audio_cache.get_cached_audio(
                    request.input, request.voice, request.speed,
                    request.response_format, 
                    getattr(request, 'emotion', None),
                    getattr(request, 'emotion_strength', 1.0)
                )
                
                if cached_audio:
                    logger.info(f"Cache hit for request: {request.input[:50]}...")
                    processing_time = time.time() - start_time
                    
                    return await self.response_formatter.format_audio_response(
                        cached_audio, request.response_format, processing_time,
                        request.stream
                    )
                
                # Synthesize audio
                audio_segment = self.synthesizer.synthesize(request)
                processing_time = time.time() - start_time
                
                # Cache the result
                background_tasks.add_task(
                    self.audio_cache.cache_audio,
                    audio_segment, request.input, request.voice,
                    request.speed, request.response_format,
                    getattr(request, 'emotion', None),
                    getattr(request, 'emotion_strength', 1.0)
                )
                
                # Return response
                return await self.response_formatter.format_audio_response(
                    audio_segment, request.response_format, processing_time,
                    request.stream
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Speech synthesis failed: {e}")
                return self.error_handler.handle_synthesis_error(e)
        
        @self.router.get("/voices")
        async def list_voices():
            """List available voices"""
            try:
                voices = self.synthesizer.get_available_voices()
                voice_info = {}
                
                for voice_name in voices:
                    info = self.synthesizer.get_voice_info(voice_name)
                    if info:
                        voice_info[voice_name] = {
                            'name': voice_name,
                            'ready': info.get('ready', False),
                            'cached': info.get('cached', False),
                            'metadata': info.get('metadata', {})
                        }
                
                return {
                    'voices': voice_info,
                    'total_voices': len(voices),
                    'emotions': self.synthesizer.get_supported_emotions()
                }
                
            except Exception as e:
                logger.error(f"Failed to list voices: {e}")
                return self.error_handler.handle_generic_error(e)
        
        @self.router.get("/voices/{voice_name}")
        async def get_voice_info(voice_name: str):
            """Get detailed information about a specific voice"""
            try:
                if voice_name not in self.synthesizer.get_available_voices():
                    raise HTTPException(
                        status_code=404,
                        detail=f"Voice '{voice_name}' not found"
                    )
                
                voice_info = self.synthesizer.get_voice_info(voice_name)
                return voice_info
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to get voice info for {voice_name}: {e}")
                return self.error_handler.handle_generic_error(e)
        
        @self.router.get("/emotions")
        async def list_emotions():
            """List supported emotions"""
            try:
                emotions = self.synthesizer.get_supported_emotions()
                emotion_info = {}
                
                for emotion in emotions:
                    info = self.synthesizer.get_emotion_info(emotion)
                    if info:
                        emotion_info[emotion] = info
                
                return {
                    'emotions': emotion_info,
                    'total_emotions': len(emotions)
                }
                
            except Exception as e:
                logger.error(f"Failed to list emotions: {e}")
                return self.error_handler.handle_generic_error(e)
        
        @self.router.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                system_status = self.synthesizer.get_system_status()
                
                # Determine overall health
                is_healthy = (
                    system_status['engine']['model_loaded'] and
                    system_status['voices']['system_health']['default_voices_ready'] and
                    len(system_status['voices']['voices']['ready']) > 0
                )
                
                return {
                    'status': 'healthy' if is_healthy else 'degraded',
                    'timestamp': time.time(),
                    'system': system_status,
                    'version': '1.0.0'
                }
                
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return {
                    'status': 'unhealthy',
                    'timestamp': time.time(),
                    'error': str(e)
                }
        
        @self.router.get("/stats")
        async def get_statistics():
            """Get system statistics"""
            try:
                synthesis_stats = self.synthesizer.get_synthesis_stats()
                cache_stats = {
                    'audio_cache': self.audio_cache.get_cache_stats(),
                    'text_cache': self.text_cache.get_cache_stats()
                }
                
                return {
                    'synthesis': synthesis_stats,
                    'cache': cache_stats,
                    'timestamp': time.time()
                }
                
            except Exception as e:
                logger.error(f"Failed to get statistics: {e}")
                return self.error_handler.handle_generic_error(e)     
   
        @self.router.post("/preload")
        async def preload_voices(voice_names: List[str]):
            """Preload voices into cache"""
            try:
                results = self.synthesizer.preload_voices(voice_names)
                
                successful = sum(1 for success in results.values() if success)
                
                return {
                    'preloaded': results,
                    'successful': successful,
                    'total': len(voice_names)
                }
                
            except Exception as e:
                logger.error(f"Failed to preload voices: {e}")
                return self.error_handler.handle_generic_error(e)
        
        @self.router.post("/cache/clear")
        async def clear_cache(
            voice: Optional[str] = None,
            format: Optional[str] = None,
            emotion: Optional[str] = None
        ):
            """Clear cache with optional filters"""
            try:
                if voice:
                    self.audio_cache.clear_voice_cache(voice)
                elif format:
                    self.audio_cache.clear_format_cache(format)
                elif emotion:
                    self.audio_cache.clear_emotion_cache(emotion)
                else:
                    self.audio_cache.cache_manager.clear()
                    self.text_cache.cache_manager.clear()
                
                return {
                    'status': 'success',
                    'message': 'Cache cleared',
                    'filters': {
                        'voice': voice,
                        'format': format,
                        'emotion': emotion
                    }
                }
                
            except Exception as e:
                logger.error(f"Failed to clear cache: {e}")
                return self.error_handler.handle_generic_error(e)
        
        @self.router.post("/cache/optimize")
        async def optimize_cache():
            """Optimize cache performance"""
            try:
                # Optimize caches
                self.audio_cache.optimize()
                self.text_cache.optimize()
                
                # Get updated stats
                audio_stats = self.audio_cache.get_cache_stats()
                text_stats = self.text_cache.get_cache_stats()
                
                return {
                    'status': 'success',
                    'message': 'Cache optimized',
                    'stats': {
                        'audio_cache': audio_stats,
                        'text_cache': text_stats
                    }
                }
                
            except Exception as e:
                logger.error(f"Failed to optimize cache: {e}")
                return self.error_handler.handle_generic_error(e)
        
        @self.router.post("/suggest")
        async def suggest_voice_and_emotion(text: str):
            """Suggest appropriate voice and emotion for text"""
            try:
                suggested_voice = self.synthesizer.suggest_voice_for_text(text)
                suggested_emotion = self.synthesizer.suggest_emotion_for_text(text)
                
                return {
                    'text': text[:100] + "..." if len(text) > 100 else text,
                    'suggestions': {
                        'voice': suggested_voice,
                        'emotion': suggested_emotion
                    },
                    'available_voices': self.synthesizer.get_available_voices(),
                    'available_emotions': self.synthesizer.get_supported_emotions()
                }
                
            except Exception as e:
                logger.error(f"Failed to generate suggestions: {e}")
                return self.error_handler.handle_generic_error(e)
        
        @self.router.post("/estimate")
        async def estimate_synthesis_time(request: TTSRequest):
            """Estimate synthesis time for a request"""
            try:
                estimated_time = self.synthesizer.estimate_synthesis_time(
                    request.input, request.voice
                )
                
                return {
                    'text_length': len(request.input),
                    'voice': request.voice,
                    'estimated_time_seconds': estimated_time,
                    'estimated_audio_duration': len(request.input) / 150 * 60 / 5  # Rough estimate
                }
                
            except Exception as e:
                logger.error(f"Failed to estimate synthesis time: {e}")
                return self.error_handler.handle_generic_error(e)
    
    def get_router(self) -> APIRouter:
        """Get the configured router"""
        return self.router
    
    def shutdown(self):
        """Shutdown the API router and cleanup resources"""
        logger.info("Shutting down TTS API Router")
        
        if self.synthesizer:
            self.synthesizer.cleanup()
        
        if self.audio_cache:
            self.audio_cache.shutdown()
        
        if self.text_cache:
            self.text_cache.shutdown()
        
        logger.info("TTS API Router shutdown completed")