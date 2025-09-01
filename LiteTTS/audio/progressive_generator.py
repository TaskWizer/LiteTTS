#!/usr/bin/env python3
"""
Progressive Audio Generation System
Implements chunked audio synthesis for real-time streaming
"""

import asyncio
import logging
import time
import io
from typing import AsyncIterator, List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .chunking import TextChunker, TextChunk, ChunkingConfig, ChunkingStrategy
# from ..audio.streaming import AudioStreamer  # Will be implemented separately

logger = logging.getLogger(__name__)

class GenerationMode(Enum):
    """Audio generation modes"""
    STANDARD = "standard"      # Generate complete audio at once
    CHUNKED = "chunked"        # Generate audio in chunks
    STREAMING = "streaming"    # Stream audio as it's generated

@dataclass
class ChunkResult:
    """Result of generating audio for a single chunk"""
    chunk_id: int
    audio_data: bytes
    duration: float
    generation_time: float
    chunk_text: str
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProgressiveGenerationConfig:
    """Configuration for progressive audio generation"""
    mode: GenerationMode = GenerationMode.CHUNKED
    chunking_config: Optional[ChunkingConfig] = None
    max_concurrent_chunks: int = 3
    chunk_timeout: float = 30.0
    enable_voice_consistency: bool = True
    enable_prosody_continuity: bool = True
    buffer_size: int = 8192
    streaming_delay: float = 0.1  # Delay between chunk deliveries

class ProgressiveAudioGenerator:
    """Progressive audio generation system for real-time TTS"""
    
    def __init__(self, tts_engine, config: ProgressiveGenerationConfig):
        self.tts_engine = tts_engine
        self.config = config
        self.text_chunker = TextChunker(config.chunking_config or ChunkingConfig())
        # self.audio_streamer = AudioStreamer()  # Will be implemented separately
        
        # Generation state
        self.active_generations = {}
        self.chunk_cache = {}
        
        logger.info(f"ProgressiveAudioGenerator initialized with mode: {config.mode.value}")
    
    async def generate_progressive(
        self, 
        text: str, 
        voice: str, 
        response_format: str = "mp3",
        speed: float = 1.0,
        generation_id: Optional[str] = None
    ) -> AsyncIterator[ChunkResult]:
        """
        Generate audio progressively in chunks
        
        Args:
            text: Input text to synthesize
            voice: Voice to use for synthesis
            response_format: Audio format (mp3, wav, etc.)
            speed: Speech speed multiplier
            generation_id: Optional ID for tracking this generation
            
        Yields:
            ChunkResult objects as they become available
        """
        generation_id = generation_id or f"gen_{int(time.time() * 1000)}"
        
        try:
            # Check if chunking should be used
            if not self._should_use_chunking(text):
                # Generate as single chunk
                async for result in self._generate_single_chunk(
                    text, voice, response_format, speed, generation_id
                ):
                    yield result
                return
            
            # Chunk the text
            chunks = self.text_chunker.chunk_text(text)
            logger.info(f"Text chunked into {len(chunks)} chunks for generation {generation_id}")
            
            # Track generation state
            self.active_generations[generation_id] = {
                "chunks": chunks,
                "completed": 0,
                "total": len(chunks),
                "start_time": time.time()
            }
            
            # Generate chunks progressively
            if self.config.mode == GenerationMode.STREAMING:
                async for result in self._generate_streaming(
                    chunks, voice, response_format, speed, generation_id
                ):
                    yield result
            else:
                async for result in self._generate_chunked(
                    chunks, voice, response_format, speed, generation_id
                ):
                    yield result
                    
        except Exception as e:
            logger.error(f"Progressive generation failed for {generation_id}: {e}")
            raise
        finally:
            # Cleanup generation state
            if generation_id in self.active_generations:
                del self.active_generations[generation_id]
    
    async def _generate_single_chunk(
        self, 
        text: str, 
        voice: str, 
        response_format: str, 
        speed: float,
        generation_id: str
    ) -> AsyncIterator[ChunkResult]:
        """Generate audio as a single chunk"""
        start_time = time.time()
        
        try:
            # Generate audio using the TTS engine
            audio_data = await self._synthesize_chunk(text, voice, response_format, speed)
            generation_time = time.time() - start_time
            
            # Estimate duration (rough calculation)
            duration = len(text) * 0.05  # ~50ms per character
            
            yield ChunkResult(
                chunk_id=0,
                audio_data=audio_data,
                duration=duration,
                generation_time=generation_time,
                chunk_text=text,
                is_final=True,
                metadata={
                    "mode": "single",
                    "generation_id": generation_id,
                    "text_length": len(text)
                }
            )
            
        except Exception as e:
            logger.error(f"Single chunk generation failed: {e}")
            raise
    
    async def _generate_chunked(
        self, 
        chunks: List[TextChunk], 
        voice: str, 
        response_format: str, 
        speed: float,
        generation_id: str
    ) -> AsyncIterator[ChunkResult]:
        """Generate audio chunks sequentially"""
        
        for i, chunk in enumerate(chunks):
            start_time = time.time()
            
            try:
                # Prepare chunk text with overlap if available
                chunk_text = self._prepare_chunk_text(chunk)
                
                # Generate audio for this chunk
                audio_data = await self._synthesize_chunk(
                    chunk_text, voice, response_format, speed
                )
                
                generation_time = time.time() - start_time
                
                # Estimate duration
                duration = len(chunk_text) * 0.05
                
                # Update generation state
                if generation_id in self.active_generations:
                    self.active_generations[generation_id]["completed"] += 1
                
                yield ChunkResult(
                    chunk_id=chunk.chunk_id,
                    audio_data=audio_data,
                    duration=duration,
                    generation_time=generation_time,
                    chunk_text=chunk_text,
                    is_final=(i == len(chunks) - 1),
                    metadata={
                        "mode": "chunked",
                        "generation_id": generation_id,
                        "chunk_position": i + 1,
                        "total_chunks": len(chunks),
                        "is_sentence_boundary": chunk.is_sentence_boundary,
                        "is_paragraph_boundary": chunk.is_paragraph_boundary
                    }
                )
                
                # Add small delay for streaming effect
                if self.config.streaming_delay > 0:
                    await asyncio.sleep(self.config.streaming_delay)
                    
            except Exception as e:
                logger.error(f"Chunk {chunk.chunk_id} generation failed: {e}")
                # Continue with next chunk instead of failing completely
                continue
    
    async def _generate_streaming(
        self, 
        chunks: List[TextChunk], 
        voice: str, 
        response_format: str, 
        speed: float,
        generation_id: str
    ) -> AsyncIterator[ChunkResult]:
        """Generate audio chunks with concurrent processing"""
        
        # Create semaphore to limit concurrent generations
        semaphore = asyncio.Semaphore(self.config.max_concurrent_chunks)
        
        async def generate_chunk_async(chunk: TextChunk, index: int) -> ChunkResult:
            async with semaphore:
                start_time = time.time()
                
                try:
                    chunk_text = self._prepare_chunk_text(chunk)
                    audio_data = await self._synthesize_chunk(
                        chunk_text, voice, response_format, speed
                    )
                    
                    generation_time = time.time() - start_time
                    duration = len(chunk_text) * 0.05
                    
                    return ChunkResult(
                        chunk_id=chunk.chunk_id,
                        audio_data=audio_data,
                        duration=duration,
                        generation_time=generation_time,
                        chunk_text=chunk_text,
                        is_final=(index == len(chunks) - 1),
                        metadata={
                            "mode": "streaming",
                            "generation_id": generation_id,
                            "chunk_position": index + 1,
                            "total_chunks": len(chunks)
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Streaming chunk {chunk.chunk_id} failed: {e}")
                    raise
        
        # Start all chunk generations concurrently
        tasks = [
            asyncio.create_task(generate_chunk_async(chunk, i))
            for i, chunk in enumerate(chunks)
        ]
        
        # Yield results as they complete, but maintain order
        completed_chunks = {}
        next_chunk_id = 0
        
        while tasks:
            # Wait for next completion
            done, pending = await asyncio.wait(
                tasks, 
                return_when=asyncio.FIRST_COMPLETED,
                timeout=self.config.chunk_timeout
            )
            
            # Process completed tasks
            for task in done:
                try:
                    result = await task
                    completed_chunks[result.chunk_id] = result
                    tasks.remove(task)
                    
                    # Update generation state
                    if generation_id in self.active_generations:
                        self.active_generations[generation_id]["completed"] += 1
                        
                except Exception as e:
                    logger.error(f"Streaming task failed: {e}")
                    tasks.remove(task)
                    continue
            
            # Yield chunks in order
            while next_chunk_id in completed_chunks:
                yield completed_chunks[next_chunk_id]
                del completed_chunks[next_chunk_id]
                next_chunk_id += 1
                
                # Add streaming delay
                if self.config.streaming_delay > 0:
                    await asyncio.sleep(self.config.streaming_delay)
    
    async def _synthesize_chunk(
        self, 
        text: str, 
        voice: str, 
        response_format: str, 
        speed: float
    ) -> bytes:
        """Synthesize audio for a single chunk"""
        
        # Check cache first
        cache_key = f"{hash(text)}:{voice}:{response_format}:{speed}"
        if cache_key in self.chunk_cache:
            logger.debug(f"Using cached audio for chunk: {text[:50]}...")
            return self.chunk_cache[cache_key]
        
        try:
            # Use the TTS engine to generate audio
            # This is a placeholder - actual implementation depends on TTS engine interface
            audio_data = await asyncio.get_event_loop().run_in_executor(
                None,
                self._sync_synthesize,
                text, voice, response_format, speed
            )
            
            # Cache the result
            self.chunk_cache[cache_key] = audio_data
            
            # Limit cache size
            if len(self.chunk_cache) > 100:
                # Remove oldest entries
                oldest_key = next(iter(self.chunk_cache))
                del self.chunk_cache[oldest_key]
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Chunk synthesis failed: {e}")
            raise
    
    def _sync_synthesize(self, text: str, voice: str, response_format: str, speed: float) -> bytes:
        """Synchronous synthesis wrapper"""
        # This would call the actual TTS engine
        # Placeholder implementation
        try:
            # Call the TTS engine's synthesis method
            if hasattr(self.tts_engine, 'synthesize'):
                return self.tts_engine.synthesize(text, voice, response_format, speed)
            else:
                # Fallback for different engine interfaces
                return self.tts_engine.generate_audio(text, voice)
        except Exception as e:
            logger.error(f"Synchronous synthesis failed: {e}")
            raise
    
    def _prepare_chunk_text(self, chunk: TextChunk) -> str:
        """Prepare chunk text with overlap for prosody continuity"""
        text = chunk.text
        
        # Add overlap text if available and prosody continuity is enabled
        if (self.config.enable_prosody_continuity and 
            chunk.overlap_text and 
            not chunk.chunk_id == 0):
            text = chunk.overlap_text + " " + text
        
        return text.strip()
    
    def _should_use_chunking(self, text: str) -> bool:
        """Determine if text should be chunked"""
        if not self.text_chunker.config.enabled:
            return False
        
        # Check minimum text length
        min_length = self.text_chunker.config.min_text_length_for_chunking or 100
        if len(text) < min_length:
            return False
        
        # Check if text has natural break points
        if self.text_chunker.config.strategy == ChunkingStrategy.SENTENCE:
            sentence_count = len(self.text_chunker.sentence_endings.findall(text))
            return sentence_count > 1
        
        return True
    
    def get_generation_status(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an active generation"""
        if generation_id not in self.active_generations:
            return None
        
        state = self.active_generations[generation_id]
        elapsed_time = time.time() - state["start_time"]
        
        return {
            "generation_id": generation_id,
            "completed_chunks": state["completed"],
            "total_chunks": state["total"],
            "progress_percentage": (state["completed"] / state["total"]) * 100,
            "elapsed_time": elapsed_time,
            "estimated_remaining": (elapsed_time / max(state["completed"], 1)) * (state["total"] - state["completed"])
        }
    
    def cancel_generation(self, generation_id: str) -> bool:
        """Cancel an active generation"""
        if generation_id in self.active_generations:
            del self.active_generations[generation_id]
            logger.info(f"Cancelled generation {generation_id}")
            return True
        return False
    
    def clear_cache(self):
        """Clear the chunk cache"""
        self.chunk_cache.clear()
        logger.info("Chunk cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.chunk_cache),
            "cache_memory_estimate": sum(len(data) for data in self.chunk_cache.values()),
            "active_generations": len(self.active_generations)
        }
