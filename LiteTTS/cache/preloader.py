#!/usr/bin/env python3
"""
Intelligent pre-caching system for TTS optimization
Implements cache warming during idle time for near-instant response
"""

import asyncio
import threading
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class CacheWarmingConfig:
    """Configuration for cache warming system"""
    # Primary voices to focus on
    primary_voices: List[str] = field(default_factory=lambda: ["af_heart", "am_puck"])
    
    # Common words and phrases for instant response
    instant_words: List[str] = field(default_factory=lambda: [
        "Hi", "Hello", "Hey", "Yes", "No", "Okay", "Thanks", "Please",
        "Sorry", "Excuse me", "Welcome", "Goodbye", "Bye"
    ])
    
    common_phrases: List[str] = field(default_factory=lambda: [
        "Thank you", "You're welcome", "How are you?", "I'm fine",
        "Nice to meet you", "See you later", "Have a good day",
        "What's up?", "Not much", "How's it going?", "Pretty good",
        "Take care", "Talk to you later", "Catch you later"
    ])
    
    # Conversational starters and responses
    conversation_starters: List[str] = field(default_factory=lambda: [
        "How can I help you?", "What can I do for you?", "How may I assist you?",
        "Is there anything I can help you with?", "What would you like to know?",
        "How are you doing today?", "What brings you here today?",
        "I'm here to help", "Let me know if you need anything"
    ])
    
    # System responses
    system_responses: List[str] = field(default_factory=lambda: [
        "I understand", "That makes sense", "I see", "Got it",
        "Let me think about that", "That's interesting", "I agree",
        "You're right", "That's a good point", "Absolutely"
    ])
    
    # Cache warming settings
    warm_on_startup: bool = True
    warm_during_idle: bool = True
    idle_threshold_seconds: float = 5.0  # Start warming after 5s of idle
    max_concurrent_warming: int = 2
    warming_batch_size: int = 5
    cache_ttl_hours: int = 24

@dataclass
class WarmingTask:
    """Represents a cache warming task"""
    text: str
    voice: str
    priority: int = 1  # 1=highest, 5=lowest
    created_at: datetime = field(default_factory=datetime.now)
    attempts: int = 0
    max_attempts: int = 3

class IntelligentPreloader:
    """
    Intelligent pre-caching system that warms cache during idle time
    for near-instant TTS response on common phrases
    """
    
    def __init__(self, tts_app, config: CacheWarmingConfig = None):
        self.tts_app = tts_app
        self.config = config or CacheWarmingConfig()
        
        # State tracking
        self.is_warming = False
        self.last_request_time = datetime.now()
        self.warming_queue: List[WarmingTask] = []
        self.warmed_cache: Set[str] = set()
        self.warming_stats = {
            'total_warmed': 0,
            'cache_hits_from_warming': 0,
            'warming_time_spent': 0.0,
            'last_warming_session': None
        }
        
        # Threading
        self.warming_thread: Optional[threading.Thread] = None
        self.stop_warming = threading.Event()
        self.warming_lock = threading.RLock()
        
        # Performance tracking
        self.phrase_usage_stats: Dict[str, int] = {}
        self.voice_usage_stats: Dict[str, int] = {}
        
        logger.info("Intelligent preloader initialized")
    
    def start(self):
        """Start the preloader system"""
        if self.warming_thread and self.warming_thread.is_alive():
            logger.warning("Preloader already running")
            return
        
        self.stop_warming.clear()
        self.warming_thread = threading.Thread(target=self._warming_worker, daemon=True)
        self.warming_thread.start()
        
        if self.config.warm_on_startup:
            self._schedule_startup_warming()
        
        logger.info("Intelligent preloader started")
    
    def stop(self):
        """Stop the preloader system"""
        self.stop_warming.set()
        if self.warming_thread:
            self.warming_thread.join(timeout=5.0)
        logger.info("Intelligent preloader stopped")
    
    def on_request_received(self, text: str, voice: str):
        """Called when a TTS request is received"""
        self.last_request_time = datetime.now()
        
        # Track usage statistics
        self.phrase_usage_stats[text] = self.phrase_usage_stats.get(text, 0) + 1
        self.voice_usage_stats[voice] = self.voice_usage_stats.get(voice, 0) + 1
        
        # Check if this was a cache hit from our warming
        cache_key = self._generate_cache_key(text, voice)
        if cache_key in self.warmed_cache:
            self.warming_stats['cache_hits_from_warming'] += 1
            logger.debug(f"Cache hit from preloading: {text[:30]}...")
    
    def _schedule_startup_warming(self):
        """Schedule warming tasks for startup"""
        with self.warming_lock:
            # High priority: instant words for primary voices
            for voice in self.config.primary_voices:
                for word in self.config.instant_words:
                    task = WarmingTask(text=word, voice=voice, priority=1)
                    self.warming_queue.append(task)
            
            # Medium priority: common phrases for primary voices
            for voice in self.config.primary_voices:
                for phrase in self.config.common_phrases:
                    task = WarmingTask(text=phrase, voice=voice, priority=2)
                    self.warming_queue.append(task)
            
            # Lower priority: conversation starters and system responses
            for voice in self.config.primary_voices:
                for text in self.config.conversation_starters + self.config.system_responses:
                    task = WarmingTask(text=text, voice=voice, priority=3)
                    self.warming_queue.append(task)
            
            # Sort by priority
            self.warming_queue.sort(key=lambda x: (x.priority, x.created_at))
            
            logger.info(f"Scheduled {len(self.warming_queue)} warming tasks for startup")
    
    def _warming_worker(self):
        """Background worker that performs cache warming"""
        logger.info("Cache warming worker started")
        
        while not self.stop_warming.is_set():
            try:
                # Check if we should be warming
                if not self._should_warm():
                    time.sleep(1.0)
                    continue
                
                # Get next batch of tasks
                tasks = self._get_next_warming_batch()
                if not tasks:
                    time.sleep(2.0)
                    continue
                
                # Perform warming
                self._warm_batch(tasks)
                
            except Exception as e:
                logger.error(f"Error in warming worker: {e}")
                time.sleep(5.0)
        
        logger.info("Cache warming worker stopped")
    
    def _should_warm(self) -> bool:
        """Determine if we should perform cache warming now"""
        if self.is_warming:
            return False
        
        # Check if we're in idle period
        time_since_request = (datetime.now() - self.last_request_time).total_seconds()
        if time_since_request < self.config.idle_threshold_seconds:
            return False
        
        # Check if there are tasks to warm
        with self.warming_lock:
            return len(self.warming_queue) > 0
    
    def _get_next_warming_batch(self) -> List[WarmingTask]:
        """Get the next batch of warming tasks"""
        with self.warming_lock:
            if not self.warming_queue:
                return []
            
            # Get up to batch_size tasks
            batch_size = min(self.config.warming_batch_size, len(self.warming_queue))
            batch = self.warming_queue[:batch_size]
            self.warming_queue = self.warming_queue[batch_size:]
            
            return batch
    
    def _warm_batch(self, tasks: List[WarmingTask]):
        """Warm a batch of cache entries"""
        if not tasks:
            return
        
        self.is_warming = True
        start_time = time.time()
        
        try:
            successful_warmings = 0

            for task in tasks:
                if self.stop_warming.is_set():
                    break

                try:
                    self._warm_single_entry(task)
                    successful_warmings += 1
                except Exception as e:
                    logger.warning(f"Failed to warm cache for '{task.text}': {e}")
                    task.attempts += 1

                    # Retry failed tasks
                    if task.attempts < task.max_attempts:
                        with self.warming_lock:
                            self.warming_queue.append(task)

            warming_time = time.time() - start_time
            self.warming_stats['warming_time_spent'] += warming_time
            self.warming_stats['last_warming_session'] = datetime.now().isoformat()

            logger.info(f"Completed warming {successful_warmings}/{len(tasks)} cache entries in {warming_time:.2f}s")
            
        finally:
            self.is_warming = False
    
    def _warm_single_entry(self, task: WarmingTask):
        """Warm a single cache entry"""
        try:
            # Check if already cached
            cache_key = self._generate_cache_key(task.text, task.voice)
            if cache_key in self.warmed_cache:
                return
            
            # Generate audio (this will cache it)
            start_time = time.time()
            audio, sample_rate = self.tts_app.model.create(
                task.text,
                voice=task.voice,
                speed=1.0,
                lang="en-us"
            )
            
            generation_time = time.time() - start_time
            
            # Mark as warmed
            self.warmed_cache.add(cache_key)
            self.warming_stats['total_warmed'] += 1
            
            logger.debug(f"Warmed cache: '{task.text}' ({task.voice}) in {generation_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Failed to warm cache entry: {e}")
            raise
    
    def _generate_cache_key(self, text: str, voice: str, speed: float = 1.0, format: str = "mp3") -> str:
        """Generate cache key for text/voice combination"""
        # This should match the cache key generation in the main app
        import hashlib
        key_data = f"{text}|{voice}|{speed}|{format}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get preloader statistics"""
        with self.warming_lock:
            return {
                'warming_stats': self.warming_stats.copy(),
                'queue_size': len(self.warming_queue),
                'warmed_entries': len(self.warmed_cache),
                'is_warming': self.is_warming,
                'top_phrases': dict(sorted(self.phrase_usage_stats.items(), 
                                         key=lambda x: x[1], reverse=True)[:10]),
                'voice_usage': self.voice_usage_stats.copy(),
                'config': {
                    'primary_voices': self.config.primary_voices,
                    'instant_words_count': len(self.config.instant_words),
                    'common_phrases_count': len(self.config.common_phrases),
                    'idle_threshold': self.config.idle_threshold_seconds
                }
            }
    
    def add_dynamic_warming_task(self, text: str, voice: str, priority: int = 4):
        """Add a dynamic warming task based on usage patterns"""
        with self.warming_lock:
            # Check if already in queue or warmed
            cache_key = self._generate_cache_key(text, voice)
            if cache_key in self.warmed_cache:
                return
            
            # Check if already in queue
            for task in self.warming_queue:
                if task.text == text and task.voice == voice:
                    return
            
            # Add new task
            task = WarmingTask(text=text, voice=voice, priority=priority)
            self.warming_queue.append(task)
            self.warming_queue.sort(key=lambda x: (x.priority, x.created_at))
            
            logger.debug(f"Added dynamic warming task: '{text}' ({voice})")
