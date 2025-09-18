#!/usr/bin/env python3
"""
File System Integration and Voice Management for LiteTTS
Implements automatic voice directory synchronization, real-time monitoring,
and enhanced voice library management with search/filter capabilities.
"""

import os
import time
import json
import hashlib
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sqlite3
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class VoiceFileInfo:
    """Information about a voice file"""
    name: str
    file_path: str
    file_size: int
    created_at: datetime
    modified_at: datetime
    file_hash: str
    is_custom: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    quality_rating: float = 0.0
    usage_count: int = 0
    last_used: Optional[datetime] = None

@dataclass
class VoiceSearchFilter:
    """Search and filter criteria for voices"""
    name_pattern: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    min_quality: float = 0.0
    max_quality: float = 5.0
    is_custom: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    min_size_mb: float = 0.0
    max_size_mb: float = float('inf')
    sort_by: str = "name"  # "name", "created_at", "quality", "usage_count"
    sort_order: str = "asc"  # "asc", "desc"

class VoiceFileWatcher(FileSystemEventHandler):
    """File system event handler for voice directory monitoring"""
    
    def __init__(self, voice_manager: 'VoiceFileSystemManager'):
        self.voice_manager = voice_manager
        self.debounce_time = 1.0  # Debounce events for 1 second
        self.pending_events = {}
        self.timer_lock = threading.Lock()
        
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory and self._is_voice_file(event.src_path):
            self._debounce_event('created', event.src_path)
            
    def on_deleted(self, event):
        """Handle file deletion events"""
        if not event.is_directory and self._is_voice_file(event.src_path):
            self._debounce_event('deleted', event.src_path)
            
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory and self._is_voice_file(event.src_path):
            self._debounce_event('modified', event.src_path)
            
    def on_moved(self, event):
        """Handle file move/rename events"""
        if not event.is_directory:
            if self._is_voice_file(event.src_path):
                self._debounce_event('deleted', event.src_path)
            if self._is_voice_file(event.dest_path):
                self._debounce_event('created', event.dest_path)
                
    def _is_voice_file(self, file_path: str) -> bool:
        """Check if file is a voice file"""
        return Path(file_path).suffix.lower() in ['.bin', '.npz']
        
    def _debounce_event(self, event_type: str, file_path: str):
        """Debounce file system events to avoid duplicate processing"""
        with self.timer_lock:
            key = f"{event_type}:{file_path}"
            
            # Cancel existing timer for this event
            if key in self.pending_events:
                self.pending_events[key].cancel()
                
            # Create new timer
            timer = threading.Timer(
                self.debounce_time,
                self._process_event,
                args=[event_type, file_path]
            )
            self.pending_events[key] = timer
            timer.start()
            
    def _process_event(self, event_type: str, file_path: str):
        """Process debounced file system event"""
        try:
            if event_type == 'created':
                self.voice_manager._handle_file_created(file_path)
            elif event_type == 'deleted':
                self.voice_manager._handle_file_deleted(file_path)
            elif event_type == 'modified':
                self.voice_manager._handle_file_modified(file_path)
                
            # Remove from pending events
            with self.timer_lock:
                key = f"{event_type}:{file_path}"
                self.pending_events.pop(key, None)
                
        except Exception as e:
            logger.error(f"Error processing file system event {event_type} for {file_path}: {e}")

class VoiceDatabase:
    """SQLite database for voice metadata and search"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize the voice database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS voices (
                    name TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    modified_at TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    is_custom BOOLEAN NOT NULL,
                    metadata TEXT,
                    tags TEXT,
                    quality_rating REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_voices_created_at ON voices(created_at)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_voices_quality ON voices(quality_rating)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_voices_custom ON voices(is_custom)
            """)
            
    def upsert_voice(self, voice_info: VoiceFileInfo):
        """Insert or update voice information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO voices (
                    name, file_path, file_size, created_at, modified_at,
                    file_hash, is_custom, metadata, tags, quality_rating,
                    usage_count, last_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                voice_info.name,
                voice_info.file_path,
                voice_info.file_size,
                voice_info.created_at.isoformat(),
                voice_info.modified_at.isoformat(),
                voice_info.file_hash,
                voice_info.is_custom,
                json.dumps(voice_info.metadata),
                json.dumps(voice_info.tags),
                voice_info.quality_rating,
                voice_info.usage_count,
                voice_info.last_used.isoformat() if voice_info.last_used else None
            ))
            
    def delete_voice(self, voice_name: str):
        """Delete voice from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM voices WHERE name = ?", (voice_name,))
            
    def get_voice(self, voice_name: str) -> Optional[VoiceFileInfo]:
        """Get voice information by name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM voices WHERE name = ?", (voice_name,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_voice_info(row)
            return None
            
    def search_voices(self, filter_criteria: VoiceSearchFilter) -> List[VoiceFileInfo]:
        """Search voices with filter criteria"""
        query = "SELECT * FROM voices WHERE 1=1"
        params = []
        
        # Build WHERE clause
        if filter_criteria.name_pattern:
            query += " AND name LIKE ?"
            params.append(f"%{filter_criteria.name_pattern}%")
            
        if filter_criteria.tags:
            for tag in filter_criteria.tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")
                
        if filter_criteria.min_quality > 0:
            query += " AND quality_rating >= ?"
            params.append(filter_criteria.min_quality)
            
        if filter_criteria.max_quality < 5.0:
            query += " AND quality_rating <= ?"
            params.append(filter_criteria.max_quality)
            
        if filter_criteria.is_custom is not None:
            query += " AND is_custom = ?"
            params.append(filter_criteria.is_custom)
            
        if filter_criteria.created_after:
            query += " AND created_at >= ?"
            params.append(filter_criteria.created_after.isoformat())
            
        if filter_criteria.created_before:
            query += " AND created_at <= ?"
            params.append(filter_criteria.created_before.isoformat())
            
        if filter_criteria.min_size_mb > 0:
            query += " AND file_size >= ?"
            params.append(filter_criteria.min_size_mb * 1024 * 1024)
            
        if filter_criteria.max_size_mb < float('inf'):
            query += " AND file_size <= ?"
            params.append(filter_criteria.max_size_mb * 1024 * 1024)
            
        # Add ORDER BY clause
        order_direction = "ASC" if filter_criteria.sort_order == "asc" else "DESC"
        query += f" ORDER BY {filter_criteria.sort_by} {order_direction}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_voice_info(row) for row in rows]
            
    def _row_to_voice_info(self, row) -> VoiceFileInfo:
        """Convert database row to VoiceFileInfo"""
        return VoiceFileInfo(
            name=row[0],
            file_path=row[1],
            file_size=row[2],
            created_at=datetime.fromisoformat(row[3]),
            modified_at=datetime.fromisoformat(row[4]),
            file_hash=row[5],
            is_custom=bool(row[6]),
            metadata=json.loads(row[7]) if row[7] else {},
            tags=json.loads(row[8]) if row[8] else [],
            quality_rating=row[9],
            usage_count=row[10],
            last_used=datetime.fromisoformat(row[11]) if row[11] else None
        )

class VoiceFileSystemManager:
    """Main voice file system manager with real-time monitoring"""
    
    def __init__(self, voices_dir: str = "LiteTTS/voices"):
        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self.db = VoiceDatabase(str(self.voices_dir / "voice_index.db"))
        
        # File system monitoring
        self.observer = Observer()
        self.event_handler = VoiceFileWatcher(self)
        self.monitoring = False
        
        # Thread pool for background tasks
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Callbacks for voice changes
        self.change_callbacks: List[Callable[[str, str, VoiceFileInfo], None]] = []
        
        # Standard voice names (not custom)
        self.standard_voices = {
            'af_heart', 'af_alloy', 'af_aoede', 'af_bella', 'af_jessica',
            'af_kore', 'af_nicole', 'af_nova', 'af_river', 'af_sarah', 'af_sky',
            'am_adam', 'am_echo', 'am_eric', 'am_fenrir', 'am_liam',
            'am_michael', 'am_onyx', 'am_puck', 'am_santa',
            'bf_alice', 'bf_emma', 'bf_isabella', 'bf_lily',
            'bm_daniel', 'bm_fable', 'bm_george', 'bm_lewis'
        }
        
        logger.info(f"VoiceFileSystemManager initialized for: {self.voices_dir}")
        
    def start_monitoring(self):
        """Start real-time file system monitoring"""
        if not self.monitoring:
            self.observer.schedule(self.event_handler, str(self.voices_dir), recursive=False)
            self.observer.start()
            self.monitoring = True
            logger.info("Voice directory monitoring started")
            
            # Perform initial scan
            self.executor.submit(self._initial_scan)
            
    def stop_monitoring(self):
        """Stop file system monitoring"""
        if self.monitoring:
            self.observer.stop()
            self.observer.join()
            self.monitoring = False
            logger.info("Voice directory monitoring stopped")
            
    def add_change_callback(self, callback: Callable[[str, str, VoiceFileInfo], None]):
        """Add callback for voice changes (event_type, voice_name, voice_info)"""
        self.change_callbacks.append(callback)
        
    def remove_change_callback(self, callback: Callable[[str, str, VoiceFileInfo], None]):
        """Remove change callback"""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
            
    def _initial_scan(self):
        """Perform initial scan of voice directory"""
        logger.info("Performing initial voice directory scan...")
        
        try:
            for voice_file in self.voices_dir.glob("*.bin"):
                self._process_voice_file(voice_file)
                
            for voice_file in self.voices_dir.glob("*.npz"):
                self._process_voice_file(voice_file)
                
            logger.info("Initial voice directory scan completed")
            
        except Exception as e:
            logger.error(f"Error during initial scan: {e}")
            
    def _process_voice_file(self, file_path: Path):
        """Process a voice file and update database"""
        try:
            stat = file_path.stat()
            voice_name = file_path.stem
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Check if this is a custom voice
            is_custom = voice_name not in self.standard_voices
            
            # Load metadata if available
            metadata = self._load_voice_metadata(voice_name)
            
            voice_info = VoiceFileInfo(
                name=voice_name,
                file_path=str(file_path),
                file_size=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                file_hash=file_hash,
                is_custom=is_custom,
                metadata=metadata.get('metadata', {}),
                tags=metadata.get('tags', []),
                quality_rating=metadata.get('quality_rating', 0.0)
            )
            
            self.db.upsert_voice(voice_info)
            
        except Exception as e:
            logger.error(f"Error processing voice file {file_path}: {e}")
            
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
        
    def _load_voice_metadata(self, voice_name: str) -> Dict[str, Any]:
        """Load voice metadata from JSON file if available"""
        metadata_file = self.voices_dir / f"{voice_name}_metadata.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load metadata for {voice_name}: {e}")
                
        return {}
        
    def _handle_file_created(self, file_path: str):
        """Handle file creation event"""
        path = Path(file_path)
        self._process_voice_file(path)
        
        voice_info = self.db.get_voice(path.stem)
        if voice_info:
            self._notify_callbacks('created', voice_info.name, voice_info)
            logger.info(f"Voice file created: {voice_info.name}")
            
    def _handle_file_deleted(self, file_path: str):
        """Handle file deletion event"""
        voice_name = Path(file_path).stem
        voice_info = self.db.get_voice(voice_name)
        
        if voice_info:
            self.db.delete_voice(voice_name)
            self._notify_callbacks('deleted', voice_name, voice_info)
            logger.info(f"Voice file deleted: {voice_name}")
            
    def _handle_file_modified(self, file_path: str):
        """Handle file modification event"""
        path = Path(file_path)
        self._process_voice_file(path)
        
        voice_info = self.db.get_voice(path.stem)
        if voice_info:
            self._notify_callbacks('modified', voice_info.name, voice_info)
            logger.info(f"Voice file modified: {voice_info.name}")
            
    def _notify_callbacks(self, event_type: str, voice_name: str, voice_info: VoiceFileInfo):
        """Notify all registered callbacks of voice changes"""
        for callback in self.change_callbacks:
            try:
                callback(event_type, voice_name, voice_info)
            except Exception as e:
                logger.error(f"Error in voice change callback: {e}")
                
    def search_voices(self, filter_criteria: VoiceSearchFilter) -> List[VoiceFileInfo]:
        """Search voices with filter criteria"""
        return self.db.search_voices(filter_criteria)
        
    def get_voice_info(self, voice_name: str) -> Optional[VoiceFileInfo]:
        """Get information about a specific voice"""
        return self.db.get_voice(voice_name)
        
    def update_voice_usage(self, voice_name: str):
        """Update voice usage statistics"""
        voice_info = self.db.get_voice(voice_name)
        if voice_info:
            voice_info.usage_count += 1
            voice_info.last_used = datetime.now()
            self.db.upsert_voice(voice_info)
            
    def get_voice_statistics(self) -> Dict[str, Any]:
        """Get voice library statistics"""
        all_voices = self.search_voices(VoiceSearchFilter())
        
        custom_voices = [v for v in all_voices if v.is_custom]
        standard_voices = [v for v in all_voices if not v.is_custom]
        
        total_size_mb = sum(v.file_size for v in all_voices) / (1024 * 1024)
        
        return {
            'total_voices': len(all_voices),
            'custom_voices': len(custom_voices),
            'standard_voices': len(standard_voices),
            'total_size_mb': total_size_mb,
            'avg_quality': np.mean([v.quality_rating for v in all_voices]) if all_voices else 0.0,
            'most_used': max(all_voices, key=lambda v: v.usage_count) if all_voices else None
        }
