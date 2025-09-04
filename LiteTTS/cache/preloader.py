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
    """Configuration for cache warming system - OPTIMIZED FOR FAST STARTUP"""
    # Primary voice for fastest startup (single voice only)
    primary_voices: List[str] = field(default_factory=lambda: ["af_heart"])

    # CRITICAL: Only essential words for instant response (reduced from 13 to 6)
    instant_words: List[str] = field(default_factory=lambda: [
        "Hi", "Hello", "Yes", "No", "Okay", "Thanks"
    ])

    # CRITICAL: Only most common phrases (reduced from 14 to 4)
    common_phrases: List[str] = field(default_factory=lambda: [
        "Thank you", "How are you?", "Have a good day", "See you later"
    ])

    # DEFERRED: Load these during idle time, not startup (moved to background)
    conversation_starters: List[str] = field(default_factory=lambda: [
        "How can I help you?", "What can I do for you?", "I'm here to help"
    ])

    # DEFERRED: Load these during idle time, not startup (moved to background)
    system_responses: List[str] = field(default_factory=lambda: [
        "I understand", "Got it", "That makes sense"
    ])

    # PERFORMANCE OPTIMIZED: Cache warming settings
    warm_on_startup: bool = True
    warm_during_idle: bool = True
    idle_threshold_seconds: float = 2.0  # Start background warming after 2s of idle
    max_concurrent_warming: int = 4  # Increased from 2 to 4 for parallel processing
    warming_batch_size: int = 3  # Reduced from 5 to 3 for faster batches
    cache_ttl_hours: int = 24

    # NEW: Startup optimization settings
    startup_cache_limit: int = 10  # Maximum cache entries to warm at startup
    enable_parallel_startup_warming: bool = True
    startup_timeout_seconds: float = 2.0  # Maximum time to spend on startup warming
    background_warming_enabled: bool = True  # Enable background warming for non-critical items

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

    def warm_critical_cache_immediately(self) -> bool:
        """
        Immediately warm critical cache entries for fastest startup.
        This is called synchronously during application startup.
        Returns True if warming completed within timeout.
        """
        logger.info("🔥 Starting IMMEDIATE critical cache warming...")
        start_time = time.time()

        try:
            # Get only the most critical tasks (priority 1)
            critical_tasks = []
            primary_voice = self.config.primary_voices[0] if self.config.primary_voices else "af_heart"

            # Only the most essential words (reduced set)
            essential_words = ["Hi", "Hello", "Yes", "No"]
            for word in essential_words:
                task = WarmingTask(text=word, voice=primary_voice, priority=1)
                critical_tasks.append(task)

            # Limit to absolute minimum for fastest startup
            critical_tasks = critical_tasks[:4]  # Maximum 4 entries

            logger.info(f"Warming {len(critical_tasks)} CRITICAL entries with {self.config.startup_timeout_seconds}s timeout")

            # Warm immediately with parallel processing
            if self.config.enable_parallel_startup_warming and len(critical_tasks) > 1:
                successful = self._warm_batch_parallel(critical_tasks, self.config.startup_timeout_seconds)
            else:
                successful = self._warm_batch_sequential(critical_tasks, self.config.startup_timeout_seconds)

            warming_time = time.time() - start_time
            success_rate = successful / len(critical_tasks) if critical_tasks else 1.0

            if warming_time <= self.config.startup_timeout_seconds and success_rate >= 0.75:
                logger.info(f"✅ CRITICAL cache warming completed: {successful}/{len(critical_tasks)} in {warming_time:.2f}s")
                return True
            else:
                logger.warning(f"⚠️ CRITICAL cache warming incomplete: {successful}/{len(critical_tasks)} in {warming_time:.2f}s")
                return False

        except Exception as e:
            warming_time = time.time() - start_time
            logger.error(f"❌ CRITICAL cache warming failed after {warming_time:.2f}s: {e}")
            return False
    
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
        """Schedule OPTIMIZED warming tasks for fast startup"""
        with self.warming_lock:
            startup_tasks = []
            background_tasks = []

            # CRITICAL PRIORITY: Only essential instant words for primary voice (startup)
            primary_voice = self.config.primary_voices[0] if self.config.primary_voices else "af_heart"
            for word in self.config.instant_words:
                task = WarmingTask(text=word, voice=primary_voice, priority=1)
                startup_tasks.append(task)

            # CRITICAL PRIORITY: Only most essential phrases for primary voice (startup)
            for phrase in self.config.common_phrases:
                task = WarmingTask(text=phrase, voice=primary_voice, priority=1)
                startup_tasks.append(task)

            # Apply startup cache limit to prevent excessive warming
            startup_tasks = startup_tasks[:self.config.startup_cache_limit]

            # BACKGROUND PRIORITY: Conversation starters and system responses (background)
            for text in self.config.conversation_starters + self.config.system_responses:
                task = WarmingTask(text=text, voice=primary_voice, priority=4)  # Lower priority
                background_tasks.append(task)

            # Add additional voices as background tasks
            for voice in self.config.primary_voices[1:]:
                for word in self.config.instant_words:
                    task = WarmingTask(text=word, voice=voice, priority=5)
                    background_tasks.append(task)

            # Add startup tasks first (high priority)
            self.warming_queue.extend(startup_tasks)

            # Add background tasks (will be processed during idle time)
            if self.config.background_warming_enabled:
                self.warming_queue.extend(background_tasks)

            # Sort by priority (startup tasks first)
            self.warming_queue.sort(key=lambda x: (x.priority, x.created_at))

            logger.info(f"Scheduled {len(startup_tasks)} CRITICAL startup tasks + {len(background_tasks)} background tasks")
            logger.info(f"Startup cache limit: {self.config.startup_cache_limit}, Timeout: {self.config.startup_timeout_seconds}s")
    
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
        """Warm a batch of cache entries with PARALLEL PROCESSING"""
        if not tasks:
            return

        self.is_warming = True
        start_time = time.time()

        try:
            # Check if this is a startup batch (priority 1-2) for timeout protection
            is_startup_batch = any(task.priority <= 2 for task in tasks)
            timeout = self.config.startup_timeout_seconds if is_startup_batch else None

            if self.config.enable_parallel_startup_warming and len(tasks) > 1:
                successful_warmings = self._warm_batch_parallel(tasks, timeout)
            else:
                successful_warmings = self._warm_batch_sequential(tasks, timeout)

            warming_time = time.time() - start_time
            self.warming_stats['warming_time_spent'] += warming_time
            self.warming_stats['last_warming_session'] = datetime.now().isoformat()

            batch_type = "STARTUP" if is_startup_batch else "BACKGROUND"
            logger.info(f"Completed {batch_type} warming {successful_warmings}/{len(tasks)} cache entries in {warming_time:.2f}s")

        finally:
            self.is_warming = False

    def _warm_batch_parallel(self, tasks: List[WarmingTask], timeout: float = None) -> int:
        """Warm batch using parallel processing for faster startup"""
        import concurrent.futures
        import threading

        successful_warmings = 0
        start_time = time.time()

        # Use ThreadPoolExecutor for parallel warming
        max_workers = min(len(tasks), self.config.max_concurrent_warming)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for task in tasks:
                if timeout and (time.time() - start_time) > timeout:
                    logger.warning(f"Startup warming timeout reached ({timeout}s), skipping remaining tasks")
                    break

                future = executor.submit(self._warm_single_entry_safe, task)
                future_to_task[future] = task

            # Collect results with timeout
            remaining_timeout = timeout - (time.time() - start_time) if timeout else None

            try:
                for future in concurrent.futures.as_completed(future_to_task, timeout=remaining_timeout):
                    task = future_to_task[future]
                    try:
                        success = future.result()
                        if success:
                            successful_warmings += 1
                    except Exception as e:
                        logger.warning(f"Parallel warming failed for '{task.text}': {e}")
                        # Retry failed tasks
                        if task.attempts < task.max_attempts:
                            task.attempts += 1
                            with self.warming_lock:
                                self.warming_queue.append(task)

            except concurrent.futures.TimeoutError:
                logger.warning(f"Parallel warming timeout after {timeout}s")
                # Cancel remaining futures
                for future in future_to_task:
                    future.cancel()

        return successful_warmings

    def _warm_batch_sequential(self, tasks: List[WarmingTask], timeout: float = None) -> int:
        """Warm batch sequentially (fallback method)"""
        successful_warmings = 0
        start_time = time.time()

        for task in tasks:
            if self.stop_warming.is_set():
                break

            if timeout and (time.time() - start_time) > timeout:
                logger.warning(f"Sequential warming timeout reached ({timeout}s)")
                break

            try:
                success = self._warm_single_entry_safe(task)
                if success:
                    successful_warmings += 1
            except Exception as e:
                logger.warning(f"Failed to warm cache for '{task.text}': {e}")
                task.attempts += 1

                # Retry failed tasks
                if task.attempts < task.max_attempts:
                    with self.warming_lock:
                        self.warming_queue.append(task)

        return successful_warmings
    
    def _warm_single_entry_safe(self, task: WarmingTask) -> bool:
        """Thread-safe wrapper for warming a single cache entry"""
        try:
            return self._warm_single_entry(task)
        except Exception as e:
            logger.warning(f"Safe warming failed for '{task.text}': {e}")
            return False

    def _warm_single_entry(self, task: WarmingTask) -> bool:
        """Warm a single cache entry - OPTIMIZED VERSION"""
        try:
            # Check if already cached (thread-safe check)
            cache_key = self._generate_cache_key(task.text, task.voice)
            if cache_key in self.warmed_cache:
                return True

            # Quick validation
            if not task.text or not task.text.strip():
                logger.debug(f"Skipping empty text for voice {task.voice}")
                return False

            # Generate audio with timeout protection
            start_time = time.time()

            # Use a shorter timeout for startup warming
            generation_timeout = 5.0 if task.priority <= 2 else 10.0

            try:
                audio, sample_rate = self.tts_app.model.create(
                    task.text,
                    voice=task.voice,
                    speed=1.0,
                    lang="en-us"
                )

                generation_time = time.time() - start_time

                # Validate audio was generated
                if audio is None or len(audio) == 0:
                    logger.warning(f"Empty audio generated for '{task.text}' ({task.voice})")
                    return False

                # Mark as warmed (thread-safe)
                self.warmed_cache.add(cache_key)
                self.warming_stats['total_warmed'] += 1

                priority_label = "CRITICAL" if task.priority <= 2 else "BACKGROUND"
                logger.debug(f"[{priority_label}] Warmed cache: '{task.text}' ({task.voice}) in {generation_time:.3f}s")

                return True

            except Exception as generation_error:
                generation_time = time.time() - start_time
                if generation_time > generation_timeout:
                    logger.warning(f"Warming timeout for '{task.text}' after {generation_time:.2f}s")
                else:
                    logger.warning(f"Generation failed for '{task.text}': {generation_error}")
                return False

        except Exception as e:
            logger.error(f"Failed to warm cache entry '{task.text}': {e}")
            return False
    
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
