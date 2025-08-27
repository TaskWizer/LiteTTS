#!/usr/bin/env python3
"""
Progressive Response Handler for Chunked Audio Generation
Handles streaming responses for real-time TTS
"""

import asyncio
import json
import logging
import time
from typing import AsyncIterator, Dict, Any, Optional
from fastapi import Response
from fastapi.responses import StreamingResponse
import io

from ..audio.progressive_generator import ProgressiveAudioGenerator, ChunkResult, GenerationMode

logger = logging.getLogger(__name__)

class ProgressiveResponseHandler:
    """Handles progressive audio responses for chunked generation"""
    
    def __init__(self, progressive_generator: ProgressiveAudioGenerator):
        self.progressive_generator = progressive_generator
        self.active_streams = {}
    
    async def create_progressive_response(
        self,
        text: str,
        voice: str,
        response_format: str = "mp3",
        speed: float = 1.0,
        streaming: bool = True,
        generation_id: Optional[str] = None
    ) -> StreamingResponse:
        """
        Create a progressive streaming response
        
        Args:
            text: Text to synthesize
            voice: Voice to use
            response_format: Audio format
            speed: Speech speed
            streaming: Whether to use streaming mode
            generation_id: Optional generation ID
            
        Returns:
            StreamingResponse with progressive audio
        """
        generation_id = generation_id or f"stream_{int(time.time() * 1000)}"
        
        # Store stream info
        self.active_streams[generation_id] = {
            "start_time": time.time(),
            "text": text,
            "voice": voice,
            "format": response_format
        }
        
        try:
            if streaming:
                # Create streaming response with chunked audio
                return StreamingResponse(
                    self._stream_chunked_audio(
                        text, voice, response_format, speed, generation_id
                    ),
                    media_type=f"audio/{response_format}",
                    headers={
                        "Content-Disposition": f"attachment; filename=progressive_speech.{response_format}",
                        "Transfer-Encoding": "chunked",
                        "Cache-Control": "no-cache",
                        "X-Generation-Mode": "progressive",
                        "X-Generation-ID": generation_id,
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                        "Access-Control-Allow-Headers": "*"
                    }
                )
            else:
                # Create response with complete audio (but still chunked internally)
                return StreamingResponse(
                    self._stream_complete_audio(
                        text, voice, response_format, speed, generation_id
                    ),
                    media_type=f"audio/{response_format}",
                    headers={
                        "Content-Disposition": f"attachment; filename=speech.{response_format}",
                        "Content-Length": "0",  # Will be updated
                        "Cache-Control": "no-cache",
                        "X-Generation-Mode": "chunked",
                        "X-Generation-ID": generation_id,
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                        "Access-Control-Allow-Headers": "*"
                    }
                )
        except Exception as e:
            logger.error(f"Failed to create progressive response: {e}")
            # Cleanup
            if generation_id in self.active_streams:
                del self.active_streams[generation_id]
            raise
    
    async def _stream_chunked_audio(
        self,
        text: str,
        voice: str,
        response_format: str,
        speed: float,
        generation_id: str
    ) -> AsyncIterator[bytes]:
        """Stream audio chunks as they become available"""
        
        try:
            chunk_count = 0
            total_bytes = 0
            
            async for chunk_result in self.progressive_generator.generate_progressive(
                text=text,
                voice=voice,
                response_format=response_format,
                speed=speed,
                generation_id=generation_id
            ):
                # Yield the audio data
                yield chunk_result.audio_data
                
                chunk_count += 1
                total_bytes += len(chunk_result.audio_data)
                
                logger.debug(
                    f"Streamed chunk {chunk_result.chunk_id} "
                    f"({len(chunk_result.audio_data)} bytes) "
                    f"for generation {generation_id}"
                )
                
                # Update stream info
                if generation_id in self.active_streams:
                    self.active_streams[generation_id].update({
                        "chunks_sent": chunk_count,
                        "bytes_sent": total_bytes,
                        "last_chunk_time": time.time()
                    })
                
                # If this is the final chunk, log completion
                if chunk_result.is_final:
                    elapsed_time = time.time() - self.active_streams[generation_id]["start_time"]
                    logger.info(
                        f"Completed progressive generation {generation_id}: "
                        f"{chunk_count} chunks, {total_bytes} bytes in {elapsed_time:.2f}s"
                    )
                    break
                    
        except Exception as e:
            logger.error(f"Streaming failed for generation {generation_id}: {e}")
            raise
        finally:
            # Cleanup
            if generation_id in self.active_streams:
                del self.active_streams[generation_id]
    
    async def _stream_complete_audio(
        self,
        text: str,
        voice: str,
        response_format: str,
        speed: float,
        generation_id: str
    ) -> AsyncIterator[bytes]:
        """Generate complete audio using chunked processing but return as single stream"""
        
        try:
            audio_chunks = []
            chunk_count = 0
            
            # Collect all chunks
            async for chunk_result in self.progressive_generator.generate_progressive(
                text=text,
                voice=voice,
                response_format=response_format,
                speed=speed,
                generation_id=generation_id
            ):
                audio_chunks.append(chunk_result.audio_data)
                chunk_count += 1
                
                logger.debug(
                    f"Generated chunk {chunk_result.chunk_id} "
                    f"({len(chunk_result.audio_data)} bytes) "
                    f"for generation {generation_id}"
                )
                
                if chunk_result.is_final:
                    break
            
            # Combine all chunks and yield as single response
            if audio_chunks:
                combined_audio = b''.join(audio_chunks)
                
                elapsed_time = time.time() - self.active_streams[generation_id]["start_time"]
                logger.info(
                    f"Completed chunked generation {generation_id}: "
                    f"{chunk_count} chunks combined into {len(combined_audio)} bytes "
                    f"in {elapsed_time:.2f}s"
                )
                
                yield combined_audio
            else:
                logger.warning(f"No audio chunks generated for {generation_id}")
                
        except Exception as e:
            logger.error(f"Complete audio generation failed for {generation_id}: {e}")
            raise
        finally:
            # Cleanup
            if generation_id in self.active_streams:
                del self.active_streams[generation_id]
    
    async def create_server_sent_events_response(
        self,
        text: str,
        voice: str,
        response_format: str = "mp3",
        speed: float = 1.0,
        generation_id: Optional[str] = None
    ) -> StreamingResponse:
        """
        Create Server-Sent Events response for real-time progress updates
        
        Returns:
            StreamingResponse with SSE format
        """
        generation_id = generation_id or f"sse_{int(time.time() * 1000)}"
        
        return StreamingResponse(
            self._stream_sse_events(
                text, voice, response_format, speed, generation_id
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Generation-ID": generation_id,
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    async def _stream_sse_events(
        self,
        text: str,
        voice: str,
        response_format: str,
        speed: float,
        generation_id: str
    ) -> AsyncIterator[str]:
        """Stream Server-Sent Events with audio chunks and progress"""
        
        try:
            chunk_count = 0
            
            # Send initial event
            yield f"event: start\n"
            yield f"data: {json.dumps({'generation_id': generation_id, 'status': 'started'})}\n\n"
            
            async for chunk_result in self.progressive_generator.generate_progressive(
                text=text,
                voice=voice,
                response_format=response_format,
                speed=speed,
                generation_id=generation_id
            ):
                chunk_count += 1
                
                # Encode audio data as base64 for SSE
                import base64
                encoded_audio = base64.b64encode(chunk_result.audio_data).decode('utf-8')
                
                # Send chunk event
                event_data = {
                    "chunk_id": chunk_result.chunk_id,
                    "audio_data": encoded_audio,
                    "duration": chunk_result.duration,
                    "generation_time": chunk_result.generation_time,
                    "chunk_text": chunk_result.chunk_text,
                    "is_final": chunk_result.is_final,
                    "metadata": chunk_result.metadata
                }
                
                yield f"event: chunk\n"
                yield f"data: {json.dumps(event_data)}\n\n"
                
                # Send progress event
                if chunk_result.metadata:
                    total_chunks = chunk_result.metadata.get("total_chunks", 1)
                    progress = (chunk_count / total_chunks) * 100
                    
                    progress_data = {
                        "progress": progress,
                        "completed_chunks": chunk_count,
                        "total_chunks": total_chunks
                    }
                    
                    yield f"event: progress\n"
                    yield f"data: {json.dumps(progress_data)}\n\n"
                
                if chunk_result.is_final:
                    # Send completion event
                    yield f"event: complete\n"
                    yield f"data: {json.dumps({'generation_id': generation_id, 'status': 'completed'})}\n\n"
                    break
                    
        except Exception as e:
            logger.error(f"SSE streaming failed for generation {generation_id}: {e}")
            # Send error event
            error_data = {
                "generation_id": generation_id,
                "status": "error",
                "error": str(e)
            }
            yield f"event: error\n"
            yield f"data: {json.dumps(error_data)}\n\n"
    
    def get_stream_status(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an active stream"""
        if generation_id not in self.active_streams:
            return None
        
        stream_info = self.active_streams[generation_id]
        current_time = time.time()
        
        status = {
            "generation_id": generation_id,
            "start_time": stream_info["start_time"],
            "elapsed_time": current_time - stream_info["start_time"],
            "text": stream_info["text"],
            "voice": stream_info["voice"],
            "format": stream_info["format"]
        }
        
        # Add progress info if available
        if "chunks_sent" in stream_info:
            status.update({
                "chunks_sent": stream_info["chunks_sent"],
                "bytes_sent": stream_info["bytes_sent"],
                "last_chunk_time": stream_info.get("last_chunk_time")
            })
        
        return status
    
    def cancel_stream(self, generation_id: str) -> bool:
        """Cancel an active stream"""
        if generation_id in self.active_streams:
            del self.active_streams[generation_id]
            # Also cancel the underlying generation
            return self.progressive_generator.cancel_generation(generation_id)
        return False
    
    def get_active_streams(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all active streams"""
        return {
            stream_id: self.get_stream_status(stream_id)
            for stream_id in self.active_streams.keys()
        }
    
    def cleanup_expired_streams(self, max_age_seconds: int = 3600):
        """Clean up streams that have been active too long"""
        current_time = time.time()
        expired_streams = []
        
        for stream_id, stream_info in self.active_streams.items():
            if current_time - stream_info["start_time"] > max_age_seconds:
                expired_streams.append(stream_id)
        
        for stream_id in expired_streams:
            del self.active_streams[stream_id]
            logger.info(f"Cleaned up expired stream: {stream_id}")
        
        return len(expired_streams)
