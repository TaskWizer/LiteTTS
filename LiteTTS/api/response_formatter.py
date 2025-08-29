#!/usr/bin/env python3
"""
Response formatting for TTS API
"""

from fastapi.responses import StreamingResponse, Response
from typing import Dict, Any, Iterator, AsyncIterator
import io
import logging

from LiteTTS.audio.audio_segment import AudioSegment
from ..audio.processor import AudioProcessor
from ..audio.streaming import AudioStreamer

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Formats API responses for different output types"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.audio_streamer = AudioStreamer()
        logger.info("Response formatter initialized")
    
    async def format_audio_response(self, audio_segment: AudioSegment, 
                                   format: str, processing_time: float,
                                   stream: bool = False) -> Response:
        """Format audio response"""
        try:
            # Convert audio to requested format
            audio_bytes = self.audio_processor.convert_format(
                audio_segment, format
            )
            
            # Get content type
            content_type = self.audio_processor.format_converter.get_content_type(format)
            
            # Create response headers
            headers = self._create_audio_headers(
                audio_segment, format, processing_time
            )
            
            if stream:
                # Return streaming response
                return StreamingResponse(
                    self._create_audio_stream(audio_bytes),
                    media_type=content_type,
                    headers=headers
                )
            else:
                # Return direct response
                return Response(
                    content=audio_bytes,
                    media_type=content_type,
                    headers=headers
                )
                
        except Exception as e:
            logger.error(f"Failed to format audio response: {e}")
            raise
    
    def _create_audio_headers(self, audio_segment: AudioSegment, 
                             format: str, processing_time: float) -> Dict[str, str]:
        """Create headers for audio response"""
        headers = {
            'X-Audio-Duration': str(audio_segment.duration),
            'X-Audio-Sample-Rate': str(audio_segment.sample_rate),
            'X-Audio-Format': format,
            'X-Processing-Time': str(processing_time),
            'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Expose-Headers': 'X-Audio-Duration, X-Audio-Sample-Rate, X-Audio-Format, X-Processing-Time'
        }
        
        # Add format-specific headers
        if format.lower() == 'mp3':
            headers['X-Audio-Bitrate'] = '128'
        elif format.lower() == 'wav':
            headers['X-Audio-Bit-Depth'] = '16'
        
        return headers
    
    def _create_audio_stream(self, audio_bytes: bytes) -> Iterator[bytes]:
        """Create streaming iterator for audio data"""
        chunk_size = 8192  # 8KB chunks
        
        for i in range(0, len(audio_bytes), chunk_size):
            yield audio_bytes[i:i + chunk_size]
    
    async def format_streaming_audio_response(self, audio_segment: AudioSegment,
                                            format: str, processing_time: float) -> StreamingResponse:
        """Format streaming audio response with chunked transfer"""
        try:
            # Get content type and headers
            content_type = self.audio_processor.format_converter.get_content_type(format)
            headers = self._create_streaming_headers(audio_segment, format, processing_time)
            
            # Create async streaming generator
            async def audio_generator():
                async for chunk in self.audio_streamer.stream_audio_async(audio_segment, format):
                    yield chunk.data
            
            return StreamingResponse(
                audio_generator(),
                media_type=content_type,
                headers=headers
            )
            
        except Exception as e:
            logger.error(f"Failed to format streaming audio response: {e}")
            raise
    
    def _create_streaming_headers(self, audio_segment: AudioSegment,
                                 format: str, processing_time: float) -> Dict[str, str]:
        """Create headers for streaming audio response"""
        headers = self._create_audio_headers(audio_segment, format, processing_time)
        
        # Add streaming-specific headers
        headers.update({
            'Transfer-Encoding': 'chunked',
            'Connection': 'keep-alive',
            'X-Streaming': 'true'
        })
        
        # Estimate content length
        estimated_size = self.audio_streamer.estimate_stream_size(audio_segment, format)
        headers['X-Estimated-Content-Length'] = str(estimated_size)
        
        return headers
    
    def format_json_response(self, data: Dict[str, Any], 
                           status_code: int = 200) -> Dict[str, Any]:
        """Format JSON response with metadata"""
        return {
            "data": data,
            "status": "success",
            "timestamp": self._get_timestamp(),
            "version": "1.0.0"
        }
    
    def format_error_response(self, error_code: str, message: str,
                            details: Dict[str, Any] = None,
                            status_code: int = 500) -> Dict[str, Any]:
        """Format error response"""
        return {
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {},
                "timestamp": self._get_timestamp()
            },
            "status": "error"
        }
    
    def format_health_response(self, is_healthy: bool, 
                             system_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format health check response"""
        return {
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": self._get_timestamp(),
            "system": system_info,
            "version": "1.0.0"
        }
    
    def format_voice_list_response(self, voices: Dict[str, Any],
                                 emotions: list) -> Dict[str, Any]:
        """Format voice list response"""
        return {
            "voices": voices,
            "emotions": emotions,
            "total_voices": len(voices),
            "total_emotions": len(emotions),
            "timestamp": self._get_timestamp()
        }
    
    def format_stats_response(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Format statistics response"""
        return {
            "statistics": stats,
            "timestamp": self._get_timestamp(),
            "version": "1.0.0"
        }
    
    def create_sse_response(self, audio_segment: AudioSegment,
                          format: str) -> StreamingResponse:
        """Create Server-Sent Events response for real-time streaming"""
        try:
            def sse_generator():
                for sse_data in self.audio_streamer.create_sse_stream(audio_segment, format):
                    yield sse_data
            
            headers = {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
            
            return StreamingResponse(
                sse_generator(),
                media_type='text/event-stream',
                headers=headers
            )
            
        except Exception as e:
            logger.error(f"Failed to create SSE response: {e}")
            raise
    
    def create_download_response(self, audio_segment: AudioSegment,
                               format: str, filename: str = None) -> Response:
        """Create downloadable file response"""
        try:
            # Convert audio to requested format
            audio_bytes = self.audio_processor.convert_format(audio_segment, format)
            
            # Get content type and file extension
            content_type = self.audio_processor.format_converter.get_content_type(format)
            file_extension = self.audio_processor.format_converter.get_file_extension(format)
            
            # Generate filename if not provided
            if not filename:
                import time
                timestamp = int(time.time())
                filename = f"tts_audio_{timestamp}{file_extension}"
            
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': content_type,
                'Content-Length': str(len(audio_bytes)),
                'X-Audio-Duration': str(audio_segment.duration),
                'X-Audio-Sample-Rate': str(audio_segment.sample_rate)
            }
            
            return Response(
                content=audio_bytes,
                media_type=content_type,
                headers=headers
            )
            
        except Exception as e:
            logger.error(f"Failed to create download response: {e}")
            raise
    
    def _get_timestamp(self) -> float:
        """Get current timestamp"""
        import time
        return time.time()
    
    def get_supported_formats(self) -> list:
        """Get list of supported audio formats"""
        return self.audio_processor.get_supported_formats()
    
    def validate_format(self, format: str) -> bool:
        """Validate if format is supported"""
        return format.lower() in self.get_supported_formats()