#!/usr/bin/env python3
"""
Text Chunking System for Progressive Audio Generation
Implements intelligent text segmentation for real-time TTS streaming
"""

import re
import logging
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ChunkingStrategy(Enum):
    """Different strategies for text chunking"""
    SENTENCE = "sentence"
    PHRASE = "phrase"
    FIXED_SIZE = "fixed_size"
    ADAPTIVE = "adaptive"

@dataclass
class TextChunk:
    """Represents a chunk of text for audio generation"""
    text: str
    chunk_id: int
    start_position: int
    end_position: int
    is_sentence_boundary: bool
    is_paragraph_boundary: bool
    prosody_context: Optional[str] = None
    overlap_text: Optional[str] = None

@dataclass
class ChunkingConfig:
    """Configuration for text chunking"""
    enabled: bool = True
    strategy: ChunkingStrategy = ChunkingStrategy.ADAPTIVE
    max_chunk_size: int = 200  # characters
    min_chunk_size: int = 50   # characters
    overlap_size: int = 20     # characters for prosody continuity
    respect_sentence_boundaries: bool = True
    respect_paragraph_boundaries: bool = True
    preserve_punctuation: bool = True

class TextChunker:
    """Intelligent text chunking system for progressive TTS generation"""
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
        
        # Sentence boundary patterns
        self.sentence_endings = re.compile(r'[.!?]+\s*')
        self.phrase_boundaries = re.compile(r'[,;:]\s*')
        self.paragraph_boundaries = re.compile(r'\n\s*\n')
        
        # Prosody-sensitive patterns
        self.prosody_breaks = re.compile(r'[.!?;:,]\s*')
        self.quotation_marks = re.compile(r'["\'""]')
        
        logger.info(f"TextChunker initialized with strategy: {config.strategy.value}")
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        """
        Main method to chunk text based on configuration
        
        Args:
            text: Input text to be chunked
            
        Returns:
            List of TextChunk objects
        """
        if not self.config.enabled:
            # Return single chunk if chunking is disabled
            return [TextChunk(
                text=text,
                chunk_id=0,
                start_position=0,
                end_position=len(text),
                is_sentence_boundary=True,
                is_paragraph_boundary=True
            )]
        
        # Preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # Apply chunking strategy
        if self.config.strategy == ChunkingStrategy.SENTENCE:
            chunks = self._chunk_by_sentences(cleaned_text)
        elif self.config.strategy == ChunkingStrategy.PHRASE:
            chunks = self._chunk_by_phrases(cleaned_text)
        elif self.config.strategy == ChunkingStrategy.FIXED_SIZE:
            chunks = self._chunk_by_fixed_size(cleaned_text)
        else:  # ADAPTIVE
            chunks = self._chunk_adaptively(cleaned_text)
        
        # Add overlap for prosody continuity
        if self.config.overlap_size > 0:
            chunks = self._add_overlap(chunks, cleaned_text)
        
        # Add prosody context
        chunks = self._add_prosody_context(chunks, cleaned_text)
        
        logger.info(f"Text chunked into {len(chunks)} chunks using {self.config.strategy.value} strategy")
        return chunks
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better chunking"""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Handle common abbreviations that shouldn't break sentences
        abbreviations = ['Mr.', 'Mrs.', 'Dr.', 'Prof.', 'Sr.', 'Jr.', 'vs.', 'etc.', 'i.e.', 'e.g.']
        for abbrev in abbreviations:
            text = text.replace(abbrev, abbrev.replace('.', '<!DOT!>'))
        
        return text
    
    def _chunk_by_sentences(self, text: str) -> List[TextChunk]:
        """Chunk text by sentence boundaries"""
        chunks = []
        sentences = self.sentence_endings.split(text)
        
        current_chunk = ""
        chunk_id = 0
        start_pos = 0
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            
            # Restore the sentence ending
            if i < len(sentences) - 1:
                sentence += self._get_sentence_ending(text, sentence)
            
            # Check if adding this sentence would exceed max chunk size
            if (len(current_chunk) + len(sentence) > self.config.max_chunk_size and 
                current_chunk and len(current_chunk) >= self.config.min_chunk_size):
                
                # Create chunk from current content
                chunks.append(TextChunk(
                    text=current_chunk.strip(),
                    chunk_id=chunk_id,
                    start_position=start_pos,
                    end_position=start_pos + len(current_chunk),
                    is_sentence_boundary=True,
                    is_paragraph_boundary='\n' in current_chunk
                ))
                
                chunk_id += 1
                start_pos += len(current_chunk)
                current_chunk = sentence
            else:
                current_chunk += sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(TextChunk(
                text=current_chunk.strip(),
                chunk_id=chunk_id,
                start_position=start_pos,
                end_position=start_pos + len(current_chunk),
                is_sentence_boundary=True,
                is_paragraph_boundary='\n' in current_chunk
            ))
        
        return chunks
    
    def _chunk_by_phrases(self, text: str) -> List[TextChunk]:
        """Chunk text by phrase boundaries (commas, semicolons, etc.)"""
        chunks = []
        phrases = self.phrase_boundaries.split(text)
        
        current_chunk = ""
        chunk_id = 0
        start_pos = 0
        
        for i, phrase in enumerate(phrases):
            if not phrase.strip():
                continue
            
            # Restore the phrase boundary
            if i < len(phrases) - 1:
                phrase += self._get_phrase_boundary(text, phrase)
            
            # Check chunk size limits
            if (len(current_chunk) + len(phrase) > self.config.max_chunk_size and 
                current_chunk and len(current_chunk) >= self.config.min_chunk_size):
                
                chunks.append(TextChunk(
                    text=current_chunk.strip(),
                    chunk_id=chunk_id,
                    start_position=start_pos,
                    end_position=start_pos + len(current_chunk),
                    is_sentence_boundary=self._is_sentence_boundary(current_chunk),
                    is_paragraph_boundary='\n' in current_chunk
                ))
                
                chunk_id += 1
                start_pos += len(current_chunk)
                current_chunk = phrase
            else:
                current_chunk += phrase
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(TextChunk(
                text=current_chunk.strip(),
                chunk_id=chunk_id,
                start_position=start_pos,
                end_position=start_pos + len(current_chunk),
                is_sentence_boundary=self._is_sentence_boundary(current_chunk),
                is_paragraph_boundary='\n' in current_chunk
            ))
        
        return chunks
    
    def _chunk_by_fixed_size(self, text: str) -> List[TextChunk]:
        """Chunk text by fixed character size"""
        chunks = []
        chunk_id = 0
        
        for i in range(0, len(text), self.config.max_chunk_size):
            chunk_text = text[i:i + self.config.max_chunk_size]
            
            # Try to break at word boundary if possible
            if i + self.config.max_chunk_size < len(text):
                last_space = chunk_text.rfind(' ')
                if last_space > self.config.max_chunk_size * 0.8:  # At least 80% of chunk size
                    chunk_text = chunk_text[:last_space]
            
            chunks.append(TextChunk(
                text=chunk_text.strip(),
                chunk_id=chunk_id,
                start_position=i,
                end_position=i + len(chunk_text),
                is_sentence_boundary=self._is_sentence_boundary(chunk_text),
                is_paragraph_boundary='\n' in chunk_text
            ))
            
            chunk_id += 1
        
        return chunks
    
    def _chunk_adaptively(self, text: str) -> List[TextChunk]:
        """Adaptive chunking that combines multiple strategies"""
        # Start with sentence-based chunking
        sentence_chunks = self._chunk_by_sentences(text)
        
        # If chunks are too large, break them down further
        refined_chunks = []
        for chunk in sentence_chunks:
            if len(chunk.text) > self.config.max_chunk_size:
                # Break large chunks by phrases
                phrase_chunks = self._chunk_by_phrases(chunk.text)
                
                # If still too large, use fixed size
                for phrase_chunk in phrase_chunks:
                    if len(phrase_chunk.text) > self.config.max_chunk_size:
                        fixed_chunks = self._chunk_by_fixed_size(phrase_chunk.text)
                        refined_chunks.extend(fixed_chunks)
                    else:
                        refined_chunks.append(phrase_chunk)
            else:
                refined_chunks.append(chunk)
        
        # Renumber chunks
        for i, chunk in enumerate(refined_chunks):
            chunk.chunk_id = i
        
        return refined_chunks
    
    def _add_overlap(self, chunks: List[TextChunk], original_text: str) -> List[TextChunk]:
        """Add overlap between chunks for prosody continuity"""
        if len(chunks) <= 1:
            return chunks
        
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]
            
            # Get overlap text from the end of current chunk
            overlap_start = max(0, len(current_chunk.text) - self.config.overlap_size)
            overlap_text = current_chunk.text[overlap_start:]
            
            # Add overlap to next chunk
            next_chunk.overlap_text = overlap_text
        
        return chunks
    
    def _add_prosody_context(self, chunks: List[TextChunk], original_text: str) -> List[TextChunk]:
        """Add prosody context information to chunks"""
        for chunk in chunks:
            # Determine prosody context based on surrounding text
            context_info = {
                'has_question': '?' in chunk.text,
                'has_exclamation': '!' in chunk.text,
                'has_quotation': bool(self.quotation_marks.search(chunk.text)),
                'ends_with_comma': chunk.text.rstrip().endswith(','),
                'starts_with_capital': chunk.text.strip() and chunk.text.strip()[0].isupper()
            }
            
            chunk.prosody_context = str(context_info)
        
        return chunks
    
    def _get_sentence_ending(self, text: str, sentence: str) -> str:
        """Get the sentence ending punctuation"""
        # Find the sentence in the original text and get its ending
        match = self.sentence_endings.search(text[text.find(sentence) + len(sentence):])
        return match.group(0) if match else ""
    
    def _get_phrase_boundary(self, text: str, phrase: str) -> str:
        """Get the phrase boundary punctuation"""
        match = self.phrase_boundaries.search(text[text.find(phrase) + len(phrase):])
        return match.group(0) if match else ""
    
    def _is_sentence_boundary(self, text: str) -> bool:
        """Check if text ends with sentence boundary"""
        return bool(self.sentence_endings.search(text.rstrip()))
    
    def estimate_chunk_count(self, text: str) -> int:
        """Estimate number of chunks for given text"""
        if not self.config.enabled:
            return 1
        
        # Simple estimation based on text length and chunk size
        estimated_count = max(1, len(text) // self.config.max_chunk_size)
        
        # Adjust based on sentence count for sentence-based chunking
        if self.config.strategy == ChunkingStrategy.SENTENCE:
            sentence_count = len(self.sentence_endings.findall(text))
            estimated_count = min(estimated_count, sentence_count)
        
        return estimated_count
    
    def get_chunk_info(self, chunks: List[TextChunk]) -> Dict[str, Any]:
        """Get information about the chunking results"""
        if not chunks:
            return {}
        
        total_chars = sum(len(chunk.text) for chunk in chunks)
        avg_chunk_size = total_chars / len(chunks)
        
        return {
            "total_chunks": len(chunks),
            "total_characters": total_chars,
            "average_chunk_size": avg_chunk_size,
            "min_chunk_size": min(len(chunk.text) for chunk in chunks),
            "max_chunk_size": max(len(chunk.text) for chunk in chunks),
            "sentence_boundaries": sum(1 for chunk in chunks if chunk.is_sentence_boundary),
            "paragraph_boundaries": sum(1 for chunk in chunks if chunk.is_paragraph_boundary)
        }
