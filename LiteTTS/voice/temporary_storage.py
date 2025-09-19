#!/usr/bin/env python3
"""
Temporary Voice Storage System for LiteTTS

This module manages temporary voice storage to prevent automatic addition
of test/preview voices to the permanent voice library without explicit user consent.
"""

import logging
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import threading
import time

logger = logging.getLogger(__name__)


class TemporaryVoiceManager:
    """
    Manages temporary voice storage with automatic cleanup and explicit save functionality.
    
    Features:
    - Session-based temporary voice management
    - Automatic cleanup of expired temporary voices
    - Explicit save mechanism to move voices to permanent storage
    - Thread-safe operations
    """
    
    def __init__(self, voices_dir: str = "LiteTTS/voices", temp_dir: str = "LiteTTS/temp/voices"):
        self.voices_dir = Path(voices_dir)
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Session tracking
        self.session_file = self.temp_dir / "sessions.json"
        self.sessions: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        
        # Configuration
        self.default_ttl_hours = 24  # Default TTL for temporary voices
        self.cleanup_interval = 3600  # Cleanup every hour
        
        # Load existing sessions
        self._load_sessions()
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        logger.info(f"Temporary voice manager initialized: {self.temp_dir}")
    
    def _load_sessions(self):
        """Load existing sessions from disk"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    self.sessions = json.load(f)
                logger.info(f"Loaded {len(self.sessions)} temporary voice sessions")
        except Exception as e:
            logger.warning(f"Failed to load sessions: {e}")
            self.sessions = {}
    
    def _save_sessions(self):
        """Save sessions to disk"""
        try:
            with open(self.session_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while True:
                try:
                    self.cleanup_expired_voices()
                    time.sleep(self.cleanup_interval)
                except Exception as e:
                    logger.error(f"Cleanup thread error: {e}")
                    time.sleep(60)  # Wait a minute before retrying
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("Started temporary voice cleanup thread")
    
    def create_temporary_voice(self, voice_name: str, voice_data: bytes, 
                             session_id: Optional[str] = None, 
                             ttl_hours: Optional[int] = None) -> str:
        """
        Create a temporary voice file
        
        Args:
            voice_name: Name of the voice
            voice_data: Binary voice data
            session_id: Optional session ID for grouping
            ttl_hours: Time to live in hours (default: 24)
        
        Returns:
            Path to the temporary voice file
        """
        with self.lock:
            if ttl_hours is None:
                ttl_hours = self.default_ttl_hours
            
            if session_id is None:
                session_id = f"session_{int(time.time())}"
            
            # Create temporary voice file
            temp_voice_file = self.temp_dir / f"{voice_name}.bin"
            temp_voice_file.write_bytes(voice_data)
            
            # Track in session
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
            
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "created_at": datetime.now().isoformat(),
                    "voices": {}
                }
            
            self.sessions[session_id]["voices"][voice_name] = {
                "file_path": str(temp_voice_file),
                "created_at": datetime.now().isoformat(),
                "expires_at": expires_at.isoformat(),
                "ttl_hours": ttl_hours
            }
            
            self._save_sessions()
            
            logger.info(f"Created temporary voice: {voice_name} (session: {session_id}, expires: {expires_at})")
            return str(temp_voice_file)
    
    def save_voice_permanently(self, voice_name: str, session_id: Optional[str] = None) -> bool:
        """
        Move a temporary voice to permanent storage
        
        Args:
            voice_name: Name of the voice to save
            session_id: Session ID (if None, searches all sessions)
        
        Returns:
            True if saved successfully, False otherwise
        """
        with self.lock:
            # Find the voice in sessions
            found_session = None
            voice_info = None
            
            if session_id:
                if session_id in self.sessions and voice_name in self.sessions[session_id]["voices"]:
                    found_session = session_id
                    voice_info = self.sessions[session_id]["voices"][voice_name]
            else:
                # Search all sessions
                for sid, session in self.sessions.items():
                    if voice_name in session["voices"]:
                        found_session = sid
                        voice_info = session["voices"][voice_name]
                        break
            
            if not found_session or not voice_info:
                logger.error(f"Temporary voice not found: {voice_name}")
                return False
            
            try:
                # Move file to permanent storage
                temp_file = Path(voice_info["file_path"])
                permanent_file = self.voices_dir / f"{voice_name}.bin"
                
                if not temp_file.exists():
                    logger.error(f"Temporary voice file not found: {temp_file}")
                    return False
                
                shutil.move(str(temp_file), str(permanent_file))
                
                # Remove from session tracking
                del self.sessions[found_session]["voices"][voice_name]
                
                # Remove empty sessions
                if not self.sessions[found_session]["voices"]:
                    del self.sessions[found_session]
                
                self._save_sessions()
                
                logger.info(f"Saved temporary voice permanently: {voice_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to save voice permanently: {voice_name}: {e}")
                return False
    
    def delete_temporary_voice(self, voice_name: str, session_id: Optional[str] = None) -> bool:
        """
        Delete a temporary voice
        
        Args:
            voice_name: Name of the voice to delete
            session_id: Session ID (if None, searches all sessions)
        
        Returns:
            True if deleted successfully, False otherwise
        """
        with self.lock:
            # Find and remove the voice
            found_session = None
            voice_info = None
            
            if session_id:
                if session_id in self.sessions and voice_name in self.sessions[session_id]["voices"]:
                    found_session = session_id
                    voice_info = self.sessions[session_id]["voices"][voice_name]
            else:
                # Search all sessions
                for sid, session in self.sessions.items():
                    if voice_name in session["voices"]:
                        found_session = sid
                        voice_info = session["voices"][voice_name]
                        break
            
            if not found_session or not voice_info:
                logger.warning(f"Temporary voice not found for deletion: {voice_name}")
                return False
            
            try:
                # Delete file
                temp_file = Path(voice_info["file_path"])
                if temp_file.exists():
                    temp_file.unlink()
                
                # Remove from session tracking
                del self.sessions[found_session]["voices"][voice_name]
                
                # Remove empty sessions
                if not self.sessions[found_session]["voices"]:
                    del self.sessions[found_session]
                
                self._save_sessions()
                
                logger.info(f"Deleted temporary voice: {voice_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete temporary voice: {voice_name}: {e}")
                return False
    
    def cleanup_expired_voices(self) -> int:
        """
        Clean up expired temporary voices
        
        Returns:
            Number of voices cleaned up
        """
        with self.lock:
            now = datetime.now()
            cleaned_count = 0
            sessions_to_remove = []
            
            for session_id, session in self.sessions.items():
                voices_to_remove = []
                
                for voice_name, voice_info in session["voices"].items():
                    try:
                        expires_at = datetime.fromisoformat(voice_info["expires_at"])
                        if now > expires_at:
                            # Delete expired voice file
                            temp_file = Path(voice_info["file_path"])
                            if temp_file.exists():
                                temp_file.unlink()
                                logger.info(f"Cleaned up expired temporary voice: {voice_name}")
                            
                            voices_to_remove.append(voice_name)
                            cleaned_count += 1
                    except Exception as e:
                        logger.error(f"Error cleaning up voice {voice_name}: {e}")
                        voices_to_remove.append(voice_name)  # Remove problematic entries
                
                # Remove expired voices from session
                for voice_name in voices_to_remove:
                    del session["voices"][voice_name]
                
                # Mark empty sessions for removal
                if not session["voices"]:
                    sessions_to_remove.append(session_id)
            
            # Remove empty sessions
            for session_id in sessions_to_remove:
                del self.sessions[session_id]
            
            if cleaned_count > 0 or sessions_to_remove:
                self._save_sessions()
                logger.info(f"Cleanup completed: {cleaned_count} voices, {len(sessions_to_remove)} sessions")
            
            return cleaned_count
    
    def list_temporary_voices(self, session_id: Optional[str] = None) -> Dict[str, Dict]:
        """
        List temporary voices
        
        Args:
            session_id: Optional session ID to filter by
        
        Returns:
            Dictionary of voice information
        """
        with self.lock:
            result = {}
            
            sessions_to_check = [session_id] if session_id else self.sessions.keys()
            
            for sid in sessions_to_check:
                if sid in self.sessions:
                    for voice_name, voice_info in self.sessions[sid]["voices"].items():
                        result[voice_name] = {
                            **voice_info,
                            "session_id": sid
                        }
            
            return result
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get information about a specific session"""
        with self.lock:
            return self.sessions.get(session_id)
    
    def is_temporary_voice(self, voice_name: str) -> bool:
        """Check if a voice is in temporary storage"""
        with self.lock:
            for session in self.sessions.values():
                if voice_name in session["voices"]:
                    return True
            return False
