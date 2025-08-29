#!/usr/bin/env python3
"""
Chunk processor for handling long text inputs
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from ..audio.audio_segment import AudioSegment
from ..audio.processor import AudioProcessor

logger = logging.getLogger(__name__)

@dataclass
class TextChunk:
    """Represents a chunk of text for processing"""
    text: str
    chunk_index: int
    total_chunks: int
    is_sentence_boundary: bool = False
    is_paragraph_boundary: bool = False
    pause_after: float = 0.0

class ChunkProcessor:
    """Processes long text by splitting into manageable chunks"""
    
    def __init__(self, max_chunk_length: int = 200, overlap_length: int = 20):
        self.max_chunk_length = max_chunk_length
        self.overlap_length = overlap_length
        self.audio_processor = AudioProcessor()
        
        # Sentence boundary patterns
        self.sentence_patterns = [
            re.compile(r'[.!?]+\s+'),  # Sentence endings
            re.compile(r'[.!?]+$'),    # End of text
        ]
        
        # Paragraph boundary patterns
        self.paragraph_patterns = [
            re.compile(r'\n\s*\n'),    # Double newlines
            re.compile(r'\r\n\s*\r\n'), # Windows line endings
        ]
        
        # Phrase boundary patterns (for better chunking)
        self.phrase_patterns = [
            re.compile(r',\s+'),       # Commas
            re.compile(r';\s+'),       # Semicolons
            re.compile(r':\s+'),       # Colons
            re.compile(r'\s+and\s+'),  # Conjunctions
            re.compile(r'\s+but\s+'),
            re.compile(r'\s+or\s+'),
            re.compile(r'\s+so\s+'),
        ]
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        """Split text into processable chunks"""
        if len(text) <= self.max_chunk_length:
            return [TextChunk(
                text=text,
                chunk_index=0,
                total_chunks=1,
                is_sentence_boundary=True,
                is_paragraph_boundary=True
            )]
        
        logger.debug(f"Chunking text of length {len(text)}")
        
        # First, split by paragraphs to preserve structure
        paragraphs = self._split_by_paragraphs(text)
        
        # Then chunk each paragraph if needed
        all_chunks = []
        chunk_index = 0
        
        for para_index, paragraph in enumerate(paragraphs):
            para_chunks = self._chunk_paragraph(paragraph)
            
            for chunk_text in para_chunks:
                is_last_chunk_in_para = chunk_text == para_chunks[-1]
                is_last_para = para_index == len(paragraphs) - 1
                
                chunk = TextChunk(
                    text=chunk_text,
                    chunk_index=chunk_index,
                    total_chunks=0,  # Will be set later
                    is_sentence_boundary=self._ends_with_sentence_boundary(chunk_text),
                    is_paragraph_boundary=is_last_chunk_in_para,
                    pause_after=self._calculate_pause_duration(chunk_text, is_last_chunk_in_para, is_last_para)
                )
                
                all_chunks.append(chunk)
                chunk_index += 1
        
        # Set total chunks for all chunks
        total_chunks = len(all_chunks)
        for chunk in all_chunks:
            chunk.total_chunks = total_chunks
        
        logger.debug(f"Created {total_chunks} chunks")
        return all_chunks
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraph boundaries"""
        # Split by double newlines
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Clean up paragraphs
        paragraphs = [para.strip() for para in paragraphs if para.strip()]
        
        return paragraphs
    
    def _chunk_paragraph(self, paragraph: str) -> List[str]:
        """Chunk a single paragraph"""
        if len(paragraph) <= self.max_chunk_length:
            return [paragraph]
        
        chunks = []
        remaining_text = paragraph
        
        while len(remaining_text) > self.max_chunk_length:
            # Find the best split point
            split_point = self._find_best_split_point(remaining_text)
            
            if split_point == -1:
                # No good split point found, force split at max length
                split_point = self.max_chunk_length
            
            # Extract chunk
            chunk_text = remaining_text[:split_point].strip()
            if chunk_text:
                chunks.append(chunk_text)
            
            # Update remaining text with overlap
            overlap_start = max(0, split_point - self.overlap_length)
            remaining_text = remaining_text[overlap_start:].strip()
        
        # Add remaining text
        if remaining_text:
            chunks.append(remaining_text)
        
        return chunks
    
    def _find_best_split_point(self, text: str) -> int:
        """Find the best point to split text"""
        max_search_length = min(len(text), self.max_chunk_length)
        
        # Look for sentence boundaries first (highest priority)
        for pattern in self.sentence_patterns:
            matches = list(pattern.finditer(text[:max_search_length]))
            if matches:
                # Use the last sentence boundary within the limit
                return matches[-1].end()
        
        # Look for phrase boundaries (medium priority)
        for pattern in self.phrase_patterns:
            matches = list(pattern.finditer(text[:max_search_length]))
            if matches:
                # Use the last phrase boundary within the limit
                return matches[-1].end()
        
        # Look for word boundaries (low priority)
        word_boundary = text.rfind(' ', 0, max_search_length)
        if word_boundary > max_search_length // 2:  # Don't split too early
            return word_boundary + 1
        
        # No good split point found
        return -1
    
    def _ends_with_sentence_boundary(self, text: str) -> bool:
        """Check if text ends with a sentence boundary"""
        text = text.strip()
        return bool(re.search(r'[.!?]+$', text))
    
    def _calculate_pause_duration(self, text: str, is_paragraph_end: bool, is_last_para: bool) -> float:
        """Calculate pause duration after chunk"""
        if is_last_para:
            return 0.0  # No pause after last chunk
        
        if is_paragraph_end:
            return 0.8  # Longer pause after paragraph
        
        if self._ends_with_sentence_boundary(text):
            return 0.5  # Medium pause after sentence
        
        return 0.2  # Short pause for other chunks
    
    def process_chunks_to_audio(self, chunks: List[TextChunk], 
                               synthesize_func, voice: str, speed: float = 1.0,
                               **synthesis_kwargs) -> AudioSegment:
        """Process text chunks and combine into single audio"""
        logger.debug(f"Processing {len(chunks)} chunks to audio")
        
        audio_segments = []
        
        for chunk in chunks:
            try:
                # Synthesize chunk
                chunk_audio = synthesize_func(chunk.text, voice, speed, **synthesis_kwargs)
                audio_segments.append(chunk_audio)
                
                # Add pause if needed
                if chunk.pause_after > 0.0:
                    pause_audio = AudioSegment.silence(chunk.pause_after, chunk_audio.sample_rate)
                    audio_segments.append(pause_audio)
                
                logger.debug(f"Processed chunk {chunk.chunk_index + 1}/{chunk.total_chunks}")
                
            except Exception as e:
                logger.error(f"Failed to process chunk {chunk.chunk_index}: {e}")
                # Continue with other chunks
                continue
        
        if not audio_segments:
            raise RuntimeError("No audio segments were successfully generated")
        
        # Combine all segments with crossfade
        if len(audio_segments) == 1:
            combined_audio = audio_segments[0]
        else:
            combined_audio = self.audio_processor.apply_crossfade(audio_segments, fade_duration=0.05)
        
        logger.debug(f"Combined audio duration: {combined_audio.duration:.2f}s")
        return combined_audio  
  
    def estimate_processing_time(self, chunks: List[TextChunk], 
                                base_time_per_char: float = 0.01) -> float:
        """Estimate total processing time for chunks"""
        total_chars = sum(len(chunk.text) for chunk in chunks)
        total_pauses = sum(chunk.pause_after for chunk in chunks)
        
        # Base processing time
        processing_time = total_chars * base_time_per_char
        
        # Add overhead for chunk processing
        chunk_overhead = len(chunks) * 0.1  # 100ms per chunk
        
        return processing_time + chunk_overhead + total_pauses
    
    def get_chunk_statistics(self, chunks: List[TextChunk]) -> Dict[str, Any]:
        """Get statistics about the chunks"""
        if not chunks:
            return {}
        
        chunk_lengths = [len(chunk.text) for chunk in chunks]
        total_pauses = sum(chunk.pause_after for chunk in chunks)
        sentence_boundaries = sum(1 for chunk in chunks if chunk.is_sentence_boundary)
        paragraph_boundaries = sum(1 for chunk in chunks if chunk.is_paragraph_boundary)
        
        return {
            'total_chunks': len(chunks),
            'total_characters': sum(chunk_lengths),
            'average_chunk_length': sum(chunk_lengths) / len(chunks),
            'min_chunk_length': min(chunk_lengths),
            'max_chunk_length': max(chunk_lengths),
            'total_pause_duration': total_pauses,
            'sentence_boundaries': sentence_boundaries,
            'paragraph_boundaries': paragraph_boundaries,
            'estimated_audio_duration': self._estimate_audio_duration(chunks)
        }
    
    def _estimate_audio_duration(self, chunks: List[TextChunk]) -> float:
        """Estimate total audio duration"""
        # Rough estimate: 150 words per minute, average 5 characters per word
        total_chars = sum(len(chunk.text) for chunk in chunks)
        words_estimate = total_chars / 5
        minutes_estimate = words_estimate / 150
        audio_duration = minutes_estimate * 60
        
        # Add pause durations
        total_pauses = sum(chunk.pause_after for chunk in chunks)
        
        return audio_duration + total_pauses
    
    def optimize_chunks(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """Optimize chunks for better synthesis"""
        if not chunks:
            return chunks
        
        optimized_chunks = []
        
        for i, chunk in enumerate(chunks):
            optimized_text = self._optimize_chunk_text(chunk.text)
            
            # Create optimized chunk
            optimized_chunk = TextChunk(
                text=optimized_text,
                chunk_index=chunk.chunk_index,
                total_chunks=chunk.total_chunks,
                is_sentence_boundary=chunk.is_sentence_boundary,
                is_paragraph_boundary=chunk.is_paragraph_boundary,
                pause_after=chunk.pause_after
            )
            
            optimized_chunks.append(optimized_chunk)
        
        return optimized_chunks
    
    def _optimize_chunk_text(self, text: str) -> str:
        """Optimize individual chunk text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure proper spacing after punctuation
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
        # Clean up quotes and parentheses
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([(\["])\s+', r'\1', text)
        text = re.sub(r'\s+([)\]"])', r'\1', text)
        
        return text.strip()
    
    def validate_chunks(self, chunks: List[TextChunk]) -> List[str]:
        """Validate chunks and return list of issues"""
        issues = []
        
        if not chunks:
            issues.append("No chunks provided")
            return issues
        
        for i, chunk in enumerate(chunks):
            # Check chunk length
            if len(chunk.text) > self.max_chunk_length * 1.5:
                issues.append(f"Chunk {i} is too long: {len(chunk.text)} characters")
            
            # Check for empty chunks
            if not chunk.text.strip():
                issues.append(f"Chunk {i} is empty")
            
            # Check chunk index consistency
            if chunk.chunk_index != i:
                issues.append(f"Chunk {i} has incorrect index: {chunk.chunk_index}")
            
            # Check total chunks consistency
            if chunk.total_chunks != len(chunks):
                issues.append(f"Chunk {i} has incorrect total_chunks: {chunk.total_chunks}")
        
        return issues
    
    def merge_small_chunks(self, chunks: List[TextChunk], 
                          min_chunk_length: int = 50) -> List[TextChunk]:
        """Merge chunks that are too small"""
        if not chunks:
            return chunks
        
        merged_chunks = []
        current_chunk_text = ""
        current_chunk_index = 0
        
        for chunk in chunks:
            if len(current_chunk_text) == 0:
                # Start new chunk
                current_chunk_text = chunk.text
                current_chunk_index = chunk.chunk_index
            elif len(current_chunk_text) + len(chunk.text) < self.max_chunk_length:
                # Merge with current chunk
                current_chunk_text += " " + chunk.text
            else:
                # Finalize current chunk and start new one
                if len(current_chunk_text) >= min_chunk_length:
                    merged_chunk = TextChunk(
                        text=current_chunk_text,
                        chunk_index=len(merged_chunks),
                        total_chunks=0,  # Will be updated later
                        is_sentence_boundary=self._ends_with_sentence_boundary(current_chunk_text),
                        is_paragraph_boundary=chunk.is_paragraph_boundary
                    )
                    merged_chunks.append(merged_chunk)
                
                current_chunk_text = chunk.text
                current_chunk_index = chunk.chunk_index
        
        # Add final chunk
        if current_chunk_text:
            merged_chunk = TextChunk(
                text=current_chunk_text,
                chunk_index=len(merged_chunks),
                total_chunks=0,
                is_sentence_boundary=self._ends_with_sentence_boundary(current_chunk_text),
                is_paragraph_boundary=True
            )
            merged_chunks.append(merged_chunk)
        
        # Update total chunks
        total_chunks = len(merged_chunks)
        for chunk in merged_chunks:
            chunk.total_chunks = total_chunks
        
        logger.debug(f"Merged {len(chunks)} chunks into {total_chunks} chunks")
        return merged_chunks