#!/usr/bin/env python3
"""
Audio streaming utilities for chunked responses
"""

import asyncio
import numpy as np
from typing import Iterator, AsyncIterator, Optional, Dict, Any
from dataclasses import dataclass
import logging

from .audio_segment import AudioSegment
from .format_converter import AudioFormatConverter

logger = logging.getLogger(__name__)

@dataclass
class StreamChunk:
    """Represents a chunk of streaming audio data"""
    data: bytes
    chunk_index: int
    total_chunks: Optional[int] = None
    metadata: Dict[str, Any] = None
    is_final: bool = False

class AudioStreamer:
    """Handles streaming audio responses"""
    
    def __init__(self, chunk_duration: float = 1.0):
        self.chunk_duration = chunk_duration
        self.format_converter = AudioFormatConverter()
        
    def stream_audio_sync(self, audio_segment: AudioSegment, 
                         format: str = "mp3") -> Iterator[StreamChunk]:
        """Stream audio synchronously in chunks"""
        logger.debug(f"Starting sync audio stream, duration: {audio_segment.duration}s")
        
        chunks = list(audio_segment.get_chunks(self.chunk_duration))
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks):
            try:
                # Convert chunk to target format
                chunk_bytes = self.format_converter.convert_format(
                    chunk.audio_data, 
                    chunk.sample_rate, 
                    format
                )
                
                yield StreamChunk(
                    data=chunk_bytes,
                    chunk_index=i,
                    total_chunks=total_chunks,
                    metadata={
                        'duration': chunk.duration,
                        'sample_rate': chunk.sample_rate,
                        'format': format,
                        'chunk_size': len(chunk_bytes)
                    },
                    is_final=(i == total_chunks - 1)
                )
                
            except Exception as e:
                logger.error(f"Error streaming chunk {i}: {e}")
                continue
        
        logger.debug(f"Completed sync audio stream, {total_chunks} chunks")
    
    async def stream_audio_async(self, audio_segment: AudioSegment,
                                format: str = "mp3") -> AsyncIterator[StreamChunk]:
        """Stream audio asynchronously in chunks"""
        logger.debug(f"Starting async audio stream, duration: {audio_segment.duration}s")
        
        chunks = list(audio_segment.get_chunks(self.chunk_duration))
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks):
            try:
                # Convert chunk to target format (run in thread pool for CPU-intensive work)
                chunk_bytes = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.format_converter.convert_format,
                    chunk.audio_data,
                    chunk.sample_rate,
                    format
                )
                
                yield StreamChunk(
                    data=chunk_bytes,
                    chunk_index=i,
                    total_chunks=total_chunks,
                    metadata={
                        'duration': chunk.duration,
                        'sample_rate': chunk.sample_rate,
                        'format': format,
                        'chunk_size': len(chunk_bytes)
                    },
                    is_final=(i == total_chunks - 1)
                )
                
                # Small delay to allow other coroutines to run
                await asyncio.sleep(0.001)
                
            except Exception as e:
                logger.error(f"Error streaming chunk {i}: {e}")
                continue
        
        logger.debug(f"Completed async audio stream, {total_chunks} chunks")    

    def create_streaming_response_headers(self, format: str, 
                                        estimated_size: Optional[int] = None) -> Dict[str, str]:
        """Create headers for streaming audio response"""
        headers = {
            'Content-Type': self.format_converter.get_content_type(format),
            'Transfer-Encoding': 'chunked',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
        
        if estimated_size:
            headers['X-Estimated-Content-Length'] = str(estimated_size)
        
        # Add format-specific headers
        if format.lower() == 'mp3':
            headers['X-Audio-Bitrate'] = '128'
        elif format.lower() == 'wav':
            headers['X-Audio-Bit-Depth'] = '16'
        
        return headers
    
    def estimate_stream_size(self, audio_segment: AudioSegment, format: str) -> int:
        """Estimate the total size of the streaming response"""
        # Rough estimates based on format
        duration = audio_segment.duration
        sample_rate = audio_segment.sample_rate
        
        if format.lower() == 'wav':
            # WAV: sample_rate * duration * 2 bytes (16-bit) + header
            return int(sample_rate * duration * 2) + 44
        elif format.lower() == 'mp3':
            # MP3: roughly 128 kbps = 16 KB/s
            return int(duration * 16 * 1024)
        elif format.lower() == 'ogg':
            # OGG: roughly 96 kbps = 12 KB/s
            return int(duration * 12 * 1024)
        else:
            # Default to WAV estimate
            return int(sample_rate * duration * 2) + 44
    
    def create_sse_stream(self, audio_segment: AudioSegment, 
                         format: str = "mp3") -> Iterator[str]:
        """Create Server-Sent Events stream for audio data"""
        logger.debug("Creating SSE stream for audio")
        
        for chunk in self.stream_audio_sync(audio_segment, format):
            # Encode chunk data as base64 for SSE
            import base64
            encoded_data = base64.b64encode(chunk.data).decode('utf-8')
            
            # Create SSE event
            sse_data = {
                'chunk_index': chunk.chunk_index,
                'total_chunks': chunk.total_chunks,
                'data': encoded_data,
                'metadata': chunk.metadata,
                'is_final': chunk.is_final
            }
            
            import json
            yield f"data: {json.dumps(sse_data)}\n\n"
        
        # Send final event
        yield "event: complete\ndata: {}\n\n"

class RealTimeStreamer:
    """Handles real-time audio streaming as it's being generated"""
    
    def __init__(self, buffer_size: int = 4096):
        self.buffer_size = buffer_size
        self.format_converter = AudioFormatConverter()
        self._buffer = []
        self._buffer_lock = asyncio.Lock()
        
    async def add_audio_chunk(self, audio_data: np.ndarray, sample_rate: int):
        """Add audio chunk to the streaming buffer"""
        async with self._buffer_lock:
            self._buffer.append((audio_data, sample_rate))
    
    async def stream_realtime(self, format: str = "mp3") -> AsyncIterator[bytes]:
        """Stream audio in real-time as it becomes available"""
        logger.debug("Starting real-time audio stream")
        
        while True:
            # Check if we have data to stream
            async with self._buffer_lock:
                if not self._buffer:
                    await asyncio.sleep(0.01)  # Wait for more data
                    continue
                
                # Get next chunk
                audio_data, sample_rate = self._buffer.pop(0)
            
            try:
                # Convert to target format
                chunk_bytes = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.format_converter.convert_format,
                    audio_data,
                    sample_rate,
                    format
                )
                
                yield chunk_bytes
                
            except Exception as e:
                logger.error(f"Error in real-time streaming: {e}")
                continue
    
    def is_buffer_empty(self) -> bool:
        """Check if the streaming buffer is empty"""
        return len(self._buffer) == 0
    
    async def flush_buffer(self) -> AsyncIterator[bytes]:
        """Flush remaining buffer contents"""
        while not self.is_buffer_empty():
            async for chunk in self.stream_realtime():
                yield chunk
                if self.is_buffer_empty():
                    break