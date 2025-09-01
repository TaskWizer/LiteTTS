#!/usr/bin/env python3
"""
Voice Consistency Management for Chunked Audio Generation
Ensures voice characteristics remain consistent across audio chunks
"""

import logging
import hashlib
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class ConsistencyLevel(Enum):
    """Voice consistency levels"""
    BASIC = "basic"           # Basic voice parameter consistency
    ENHANCED = "enhanced"     # Enhanced prosody and timing consistency
    STRICT = "strict"         # Strict consistency with overlap analysis

@dataclass
class VoiceProfile:
    """Voice profile for consistency tracking"""
    voice_id: str
    voice_name: str
    base_parameters: Dict[str, Any]
    prosody_profile: Dict[str, float]
    timing_profile: Dict[str, float]
    energy_profile: Dict[str, float]
    created_at: float
    last_used: float
    usage_count: int = 0

@dataclass
class ChunkConsistencyInfo:
    """Consistency information for a chunk"""
    chunk_id: int
    voice_profile: VoiceProfile
    prosody_adjustments: Dict[str, float]
    timing_adjustments: Dict[str, float]
    energy_adjustments: Dict[str, float]
    overlap_compensation: Optional[Dict[str, Any]] = None

class VoiceConsistencyManager:
    """Manages voice consistency across audio chunks"""
    
    def __init__(self, consistency_level: ConsistencyLevel = ConsistencyLevel.ENHANCED):
        self.consistency_level = consistency_level
        self.voice_profiles = {}
        self.active_sessions = {}
        self.consistency_cache = {}
        
        # Consistency parameters
        self.prosody_tolerance = 0.1    # 10% tolerance for prosody variations
        self.timing_tolerance = 0.05    # 5% tolerance for timing variations
        self.energy_tolerance = 0.15    # 15% tolerance for energy variations
        
        logger.info(f"VoiceConsistencyManager initialized with level: {consistency_level.value}")
    
    def create_voice_profile(
        self, 
        voice_id: str, 
        voice_name: str, 
        reference_audio: Optional[bytes] = None,
        base_parameters: Optional[Dict[str, Any]] = None
    ) -> VoiceProfile:
        """
        Create or update a voice profile for consistency tracking
        
        Args:
            voice_id: Unique voice identifier
            voice_name: Human-readable voice name
            reference_audio: Optional reference audio for analysis
            base_parameters: Base voice parameters
            
        Returns:
            VoiceProfile object
        """
        current_time = time.time()
        
        # Check if profile already exists
        if voice_id in self.voice_profiles:
            profile = self.voice_profiles[voice_id]
            profile.last_used = current_time
            profile.usage_count += 1
            return profile
        
        # Extract voice characteristics
        prosody_profile = self._extract_prosody_profile(reference_audio, base_parameters)
        timing_profile = self._extract_timing_profile(reference_audio, base_parameters)
        energy_profile = self._extract_energy_profile(reference_audio, base_parameters)
        
        # Create new profile
        profile = VoiceProfile(
            voice_id=voice_id,
            voice_name=voice_name,
            base_parameters=base_parameters or {},
            prosody_profile=prosody_profile,
            timing_profile=timing_profile,
            energy_profile=energy_profile,
            created_at=current_time,
            last_used=current_time,
            usage_count=1
        )
        
        self.voice_profiles[voice_id] = profile
        logger.info(f"Created voice profile for {voice_name} ({voice_id})")
        
        return profile
    
    def start_consistency_session(
        self, 
        session_id: str, 
        voice_id: str, 
        text: str,
        generation_parameters: Dict[str, Any]
    ) -> str:
        """
        Start a consistency session for chunked generation
        
        Args:
            session_id: Unique session identifier
            voice_id: Voice to use for generation
            text: Complete text to be generated
            generation_parameters: Generation parameters (speed, format, etc.)
            
        Returns:
            Session ID
        """
        # Get or create voice profile
        if voice_id not in self.voice_profiles:
            self.create_voice_profile(voice_id, voice_id)
        
        profile = self.voice_profiles[voice_id]
        
        # Analyze text for consistency requirements
        text_analysis = self._analyze_text_for_consistency(text)
        
        # Create session
        session = {
            "session_id": session_id,
            "voice_profile": profile,
            "text": text,
            "text_analysis": text_analysis,
            "generation_parameters": generation_parameters,
            "chunks_processed": 0,
            "consistency_state": self._initialize_consistency_state(profile, text_analysis),
            "start_time": time.time()
        }
        
        self.active_sessions[session_id] = session
        logger.info(f"Started consistency session {session_id} for voice {voice_id}")
        
        return session_id
    
    def prepare_chunk_for_consistency(
        self, 
        session_id: str, 
        chunk_id: int, 
        chunk_text: str,
        chunk_position: int,
        total_chunks: int,
        overlap_text: Optional[str] = None
    ) -> ChunkConsistencyInfo:
        """
        Prepare a chunk for consistent generation
        
        Args:
            session_id: Active session ID
            chunk_id: Chunk identifier
            chunk_text: Text for this chunk
            chunk_position: Position in sequence (0-based)
            total_chunks: Total number of chunks
            overlap_text: Overlap text from previous chunk
            
        Returns:
            ChunkConsistencyInfo with adjustments
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        voice_profile = session["voice_profile"]
        consistency_state = session["consistency_state"]
        
        # Calculate position-based adjustments
        position_factor = chunk_position / max(total_chunks - 1, 1)
        
        # Prosody adjustments based on position and context
        prosody_adjustments = self._calculate_prosody_adjustments(
            chunk_text, chunk_position, total_chunks, consistency_state
        )
        
        # Timing adjustments for natural flow
        timing_adjustments = self._calculate_timing_adjustments(
            chunk_text, chunk_position, overlap_text, consistency_state
        )
        
        # Energy adjustments for consistent volume and emphasis
        energy_adjustments = self._calculate_energy_adjustments(
            chunk_text, chunk_position, consistency_state
        )
        
        # Overlap compensation if needed
        overlap_compensation = None
        if overlap_text and self.consistency_level in [ConsistencyLevel.ENHANCED, ConsistencyLevel.STRICT]:
            overlap_compensation = self._calculate_overlap_compensation(
                overlap_text, chunk_text, consistency_state
            )
        
        # Update consistency state
        self._update_consistency_state(
            consistency_state, chunk_text, prosody_adjustments, timing_adjustments, energy_adjustments
        )
        
        # Update session
        session["chunks_processed"] += 1
        
        consistency_info = ChunkConsistencyInfo(
            chunk_id=chunk_id,
            voice_profile=voice_profile,
            prosody_adjustments=prosody_adjustments,
            timing_adjustments=timing_adjustments,
            energy_adjustments=energy_adjustments,
            overlap_compensation=overlap_compensation
        )
        
        logger.debug(f"Prepared chunk {chunk_id} for consistency in session {session_id}")
        return consistency_info
    
    def apply_consistency_adjustments(
        self, 
        generation_parameters: Dict[str, Any], 
        consistency_info: ChunkConsistencyInfo
    ) -> Dict[str, Any]:
        """
        Apply consistency adjustments to generation parameters
        
        Args:
            generation_parameters: Original generation parameters
            consistency_info: Consistency information for the chunk
            
        Returns:
            Adjusted generation parameters
        """
        adjusted_params = generation_parameters.copy()
        
        # Apply prosody adjustments
        if consistency_info.prosody_adjustments:
            for param, adjustment in consistency_info.prosody_adjustments.items():
                if param in adjusted_params:
                    original_value = adjusted_params[param]
                    if isinstance(original_value, (int, float)):
                        adjusted_params[param] = original_value * (1 + adjustment)
                    else:
                        adjusted_params[param] = adjustment
        
        # Apply timing adjustments
        if consistency_info.timing_adjustments:
            for param, adjustment in consistency_info.timing_adjustments.items():
                if param == "speed" and "speed" in adjusted_params:
                    adjusted_params["speed"] *= (1 + adjustment)
                elif param in adjusted_params:
                    adjusted_params[param] = adjustment
        
        # Apply energy adjustments
        if consistency_info.energy_adjustments:
            for param, adjustment in consistency_info.energy_adjustments.items():
                if param in adjusted_params:
                    if isinstance(adjusted_params[param], (int, float)):
                        adjusted_params[param] *= (1 + adjustment)
                    else:
                        adjusted_params[param] = adjustment
        
        # Apply overlap compensation
        if consistency_info.overlap_compensation:
            for param, value in consistency_info.overlap_compensation.items():
                adjusted_params[param] = value
        
        logger.debug(f"Applied consistency adjustments for chunk {consistency_info.chunk_id}")
        return adjusted_params
    
    def end_consistency_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a consistency session and return statistics
        
        Args:
            session_id: Session to end
            
        Returns:
            Session statistics
        """
        if session_id not in self.active_sessions:
            return {}
        
        session = self.active_sessions[session_id]
        end_time = time.time()
        
        stats = {
            "session_id": session_id,
            "voice_id": session["voice_profile"].voice_id,
            "chunks_processed": session["chunks_processed"],
            "duration": end_time - session["start_time"],
            "consistency_level": self.consistency_level.value,
            "text_length": len(session["text"])
        }
        
        # Update voice profile usage
        session["voice_profile"].last_used = end_time
        session["voice_profile"].usage_count += session["chunks_processed"]
        
        # Clean up session
        del self.active_sessions[session_id]
        
        logger.info(f"Ended consistency session {session_id}: {stats}")
        return stats
    
    def _extract_prosody_profile(
        self, 
        reference_audio: Optional[bytes], 
        base_parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract prosody characteristics from reference audio or parameters"""
        
        # Default prosody profile
        prosody_profile = {
            "pitch_mean": 0.0,
            "pitch_variance": 0.1,
            "intonation_range": 0.2,
            "stress_pattern": 0.5,
            "rhythm_regularity": 0.7
        }
        
        # If we have base parameters, use them to adjust the profile
        if base_parameters:
            if "pitch" in base_parameters:
                prosody_profile["pitch_mean"] = base_parameters["pitch"]
            if "intonation" in base_parameters:
                prosody_profile["intonation_range"] = base_parameters["intonation"]
        
        # TODO: If reference_audio is provided, analyze it for prosody characteristics
        # This would require audio analysis capabilities
        
        return prosody_profile
    
    def _extract_timing_profile(
        self, 
        reference_audio: Optional[bytes], 
        base_parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract timing characteristics"""
        
        timing_profile = {
            "speech_rate": 1.0,
            "pause_duration": 0.3,
            "word_spacing": 0.1,
            "sentence_boundary_pause": 0.5
        }
        
        if base_parameters:
            if "speed" in base_parameters:
                timing_profile["speech_rate"] = base_parameters["speed"]
        
        return timing_profile
    
    def _extract_energy_profile(
        self, 
        reference_audio: Optional[bytes], 
        base_parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract energy characteristics"""
        
        energy_profile = {
            "volume_level": 0.8,
            "dynamic_range": 0.3,
            "emphasis_strength": 0.5,
            "fade_characteristics": 0.1
        }
        
        if base_parameters:
            if "volume" in base_parameters:
                energy_profile["volume_level"] = base_parameters["volume"]
        
        return energy_profile
    
    def _analyze_text_for_consistency(self, text: str) -> Dict[str, Any]:
        """Analyze text for consistency requirements"""
        
        # Count sentences, questions, exclamations
        sentence_count = len([s for s in text.split('.') if s.strip()])
        question_count = text.count('?')
        exclamation_count = text.count('!')
        
        # Detect dialogue or quoted speech
        quote_count = text.count('"') + text.count("'")
        
        # Estimate emotional content (simple heuristic)
        emotional_words = ['excited', 'angry', 'sad', 'happy', 'surprised', 'calm']
        emotion_score = sum(1 for word in emotional_words if word.lower() in text.lower())
        
        return {
            "sentence_count": sentence_count,
            "question_count": question_count,
            "exclamation_count": exclamation_count,
            "quote_count": quote_count,
            "emotion_score": emotion_score,
            "text_length": len(text),
            "complexity_score": (question_count + exclamation_count + emotion_score) / max(sentence_count, 1)
        }
    
    def _initialize_consistency_state(
        self, 
        voice_profile: VoiceProfile, 
        text_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize consistency state for a session"""
        
        return {
            "current_prosody": voice_profile.prosody_profile.copy(),
            "current_timing": voice_profile.timing_profile.copy(),
            "current_energy": voice_profile.energy_profile.copy(),
            "text_context": text_analysis,
            "chunk_history": [],
            "drift_compensation": {
                "prosody_drift": 0.0,
                "timing_drift": 0.0,
                "energy_drift": 0.0
            }
        }
    
    def _calculate_prosody_adjustments(
        self, 
        chunk_text: str, 
        chunk_position: int, 
        total_chunks: int, 
        consistency_state: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate prosody adjustments for consistency"""
        
        adjustments = {}
        
        # Position-based adjustments
        if chunk_position == 0:
            # First chunk - establish baseline
            adjustments["pitch_adjustment"] = 0.0
            adjustments["intonation_adjustment"] = 0.0
        elif chunk_position == total_chunks - 1:
            # Last chunk - natural conclusion
            adjustments["pitch_adjustment"] = -0.05  # Slightly lower pitch for conclusion
            adjustments["intonation_adjustment"] = -0.1  # Less variation for finality
        else:
            # Middle chunks - maintain consistency
            drift = consistency_state["drift_compensation"]["prosody_drift"]
            adjustments["pitch_adjustment"] = -drift * 0.5  # Compensate for drift
            adjustments["intonation_adjustment"] = -drift * 0.3
        
        # Content-based adjustments
        if '?' in chunk_text:
            adjustments["intonation_adjustment"] = adjustments.get("intonation_adjustment", 0) + 0.2
        if '!' in chunk_text:
            adjustments["emphasis_adjustment"] = 0.3
        
        return adjustments
    
    def _calculate_timing_adjustments(
        self, 
        chunk_text: str, 
        chunk_position: int, 
        overlap_text: Optional[str], 
        consistency_state: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate timing adjustments for natural flow"""
        
        adjustments = {}
        
        # Overlap compensation
        if overlap_text and chunk_position > 0:
            # Slightly faster start to compensate for overlap
            adjustments["speed_adjustment"] = 0.05
            adjustments["initial_pause_reduction"] = 0.1
        
        # Position-based timing
        if chunk_position == 0:
            # First chunk - natural start
            adjustments["initial_pause"] = 0.0
        else:
            # Subsequent chunks - smooth continuation
            adjustments["initial_pause"] = -0.2  # Reduce pause for continuity
        
        # Content-based timing
        if chunk_text.endswith(','):
            adjustments["final_pause"] = 0.1  # Short pause for comma
        elif chunk_text.endswith('.'):
            adjustments["final_pause"] = 0.3  # Longer pause for period
        
        return adjustments
    
    def _calculate_energy_adjustments(
        self, 
        chunk_text: str, 
        chunk_position: int, 
        consistency_state: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate energy adjustments for consistent volume and emphasis"""
        
        adjustments = {}
        
        # Maintain consistent energy level
        energy_drift = consistency_state["drift_compensation"]["energy_drift"]
        adjustments["volume_adjustment"] = -energy_drift * 0.5
        
        # Content-based energy
        if chunk_text.isupper():
            adjustments["emphasis_boost"] = 0.3
        elif '!' in chunk_text:
            adjustments["emphasis_boost"] = 0.2
        
        return adjustments
    
    def _calculate_overlap_compensation(
        self, 
        overlap_text: str, 
        chunk_text: str, 
        consistency_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate compensation for overlap between chunks"""
        
        compensation = {}
        
        # Analyze overlap characteristics
        overlap_length = len(overlap_text)
        
        if overlap_length > 0:
            # Adjust for smooth transition
            compensation["overlap_fade_in"] = 0.1
            compensation["overlap_volume_reduction"] = 0.2
            compensation["transition_smoothing"] = True
        
        return compensation
    
    def _update_consistency_state(
        self, 
        consistency_state: Dict[str, Any], 
        chunk_text: str,
        prosody_adjustments: Dict[str, float],
        timing_adjustments: Dict[str, float],
        energy_adjustments: Dict[str, float]
    ):
        """Update consistency state after processing a chunk"""
        
        # Track drift over time
        prosody_drift = sum(prosody_adjustments.values()) * 0.1
        timing_drift = sum(timing_adjustments.values()) * 0.1
        energy_drift = sum(energy_adjustments.values()) * 0.1
        
        consistency_state["drift_compensation"]["prosody_drift"] += prosody_drift
        consistency_state["drift_compensation"]["timing_drift"] += timing_drift
        consistency_state["drift_compensation"]["energy_drift"] += energy_drift
        
        # Add to chunk history
        consistency_state["chunk_history"].append({
            "text": chunk_text,
            "prosody_adjustments": prosody_adjustments,
            "timing_adjustments": timing_adjustments,
            "energy_adjustments": energy_adjustments
        })
        
        # Limit history size
        if len(consistency_state["chunk_history"]) > 10:
            consistency_state["chunk_history"] = consistency_state["chunk_history"][-10:]
    
    def get_voice_profile(self, voice_id: str) -> Optional[VoiceProfile]:
        """Get voice profile by ID"""
        return self.voice_profiles.get(voice_id)
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active sessions"""
        return {
            session_id: {
                "voice_id": session["voice_profile"].voice_id,
                "chunks_processed": session["chunks_processed"],
                "start_time": session["start_time"],
                "text_length": len(session["text"])
            }
            for session_id, session in self.active_sessions.items()
        }
    
    def cleanup_expired_sessions(self, max_age_seconds: int = 3600):
        """Clean up sessions that have been active too long"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if current_time - session["start_time"] > max_age_seconds:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Cleaned up expired consistency session: {session_id}")
        
        return len(expired_sessions)
