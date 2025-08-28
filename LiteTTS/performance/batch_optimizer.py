#!/usr/bin/env python3
"""
Dynamic Batch Processing Optimizer for LiteTTS
Implements adaptive batching strategies to balance latency vs throughput while maintaining memory targets
"""

import asyncio
import logging
import time
import psutil
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class BatchRequest:
    """Individual request in a batch"""
    request_id: str
    text: str
    voice: str
    params: Dict[str, Any]
    timestamp: float
    text_length: int
    priority: int = 0
    future: Optional[asyncio.Future] = None

@dataclass
class BatchConfig:
    """Batch processing configuration"""
    # Text length categories for optimal batching
    short_text_threshold: int = 20
    medium_text_threshold: int = 100
    long_text_threshold: int = 300
    
    # Batch size limits per category
    short_text_batch_size: int = 16
    medium_text_batch_size: int = 8
    long_text_batch_size: int = 4
    
    # Timeout settings (milliseconds)
    short_text_timeout: float = 50.0
    medium_text_timeout: float = 100.0
    long_text_timeout: float = 200.0
    
    # Memory constraints
    max_memory_mb: int = 150
    batch_memory_limit_mb: int = 50
    
    # Performance targets
    target_rtf: float = 0.25
    max_latency_ms: float = 2000.0
    
    # Auto-tuning parameters
    enable_auto_tuning: bool = True
    tuning_interval: float = 30.0
    performance_window: int = 100

@dataclass
class BatchMetrics:
    """Batch processing performance metrics"""
    total_requests: int = 0
    batched_requests: int = 0
    batch_efficiency: float = 0.0
    avg_batch_size: float = 0.0
    avg_latency_ms: float = 0.0
    avg_rtf: float = 0.0
    memory_usage_mb: float = 0.0
    throughput_rps: float = 0.0
    cache_hit_rate: float = 0.0

class DynamicBatchOptimizer:
    """
    Dynamic batch processing optimizer that adapts batch sizes and timeouts
    based on text length, system resources, and performance metrics
    """
    
    def __init__(self, config: Optional[BatchConfig] = None):
        self.config = config or BatchConfig()
        
        # Request queues by text length category
        self.short_queue: deque = deque()
        self.medium_queue: deque = deque()
        self.long_queue: deque = deque()
        
        # Batch processing state
        self.active_batches: Dict[str, List[BatchRequest]] = {}
        self.batch_timers: Dict[str, asyncio.Task] = {}
        
        # Performance tracking
        self.metrics = BatchMetrics()
        self.performance_history: deque = deque(maxlen=self.config.performance_window)
        self.last_tuning_time = time.time()
        
        # Auto-tuning state
        self.current_batch_sizes = {
            "short": self.config.short_text_batch_size,
            "medium": self.config.medium_text_batch_size,
            "long": self.config.long_text_batch_size
        }
        
        self.current_timeouts = {
            "short": self.config.short_text_timeout,
            "medium": self.config.medium_text_timeout,
            "long": self.config.long_text_timeout
        }
        
        # Processing lock
        self.processing_lock = asyncio.Lock()
        
        logger.info("Dynamic Batch Optimizer initialized")
        logger.info(f"Batch sizes: Short={self.current_batch_sizes['short']}, "
                   f"Medium={self.current_batch_sizes['medium']}, "
                   f"Long={self.current_batch_sizes['long']}")
    
    def categorize_request(self, text: str) -> str:
        """Categorize request by text length"""
        text_length = len(text)
        
        if text_length <= self.config.short_text_threshold:
            return "short"
        elif text_length <= self.config.medium_text_threshold:
            return "medium"
        elif text_length <= self.config.long_text_threshold:
            return "long"
        else:
            return "extra_long"
    
    async def add_request(self, request: BatchRequest) -> asyncio.Future:
        """Add request to appropriate batch queue"""
        category = self.categorize_request(request.text)
        request.future = asyncio.Future()
        
        async with self.processing_lock:
            # Add to appropriate queue
            if category == "short":
                self.short_queue.append(request)
                await self._try_process_batch("short")
            elif category == "medium":
                self.medium_queue.append(request)
                await self._try_process_batch("medium")
            elif category == "long":
                self.long_queue.append(request)
                await self._try_process_batch("long")
            else:
                # Extra long texts are processed immediately
                await self._process_single_request(request)
        
        return request.future
    
    async def _try_process_batch(self, category: str):
        """Try to process a batch if conditions are met"""
        queue = self._get_queue(category)
        batch_size = self.current_batch_sizes[category]
        timeout = self.current_timeouts[category]
        
        # Check if we have enough requests for a full batch
        if len(queue) >= batch_size:
            await self._process_batch_now(category)
        elif len(queue) > 0:
            # Start timeout timer if not already running
            if category not in self.batch_timers:
                self.batch_timers[category] = asyncio.create_task(
                    self._batch_timeout_handler(category, timeout)
                )
    
    async def _batch_timeout_handler(self, category: str, timeout_ms: float):
        """Handle batch timeout - process partial batch"""
        try:
            await asyncio.sleep(timeout_ms / 1000.0)
            
            async with self.processing_lock:
                if category in self.batch_timers:
                    del self.batch_timers[category]
                
                queue = self._get_queue(category)
                if len(queue) > 0:
                    await self._process_batch_now(category)
                    
        except asyncio.CancelledError:
            # Timer was cancelled, batch was processed early
            pass
    
    async def _process_batch_now(self, category: str):
        """Process batch immediately"""
        queue = self._get_queue(category)
        batch_size = self.current_batch_sizes[category]
        
        if len(queue) == 0:
            return
        
        # Extract batch from queue
        batch = []
        for _ in range(min(batch_size, len(queue))):
            if queue:
                batch.append(queue.popleft())
        
        # Cancel timeout timer if running
        if category in self.batch_timers:
            self.batch_timers[category].cancel()
            del self.batch_timers[category]
        
        # Process the batch
        if batch:
            await self._process_batch(batch, category)
    
    async def _process_batch(self, batch: List[BatchRequest], category: str):
        """Process a batch of requests"""
        start_time = time.time()
        batch_id = f"{category}_{int(start_time * 1000)}"
        
        try:
            logger.debug(f"Processing {category} batch with {len(batch)} requests")
            
            # Check memory constraints
            current_memory = self._get_current_memory_usage()
            if current_memory > self.config.max_memory_mb:
                logger.warning(f"Memory usage {current_memory:.1f}MB exceeds limit, processing smaller batches")
                # Split batch if memory is high
                if len(batch) > 1:
                    mid = len(batch) // 2
                    await self._process_batch(batch[:mid], category)
                    await self._process_batch(batch[mid:], category)
                    return
            
            # Group by voice for more efficient processing
            voice_groups = defaultdict(list)
            for request in batch:
                voice_groups[request.voice].append(request)
            
            # Process each voice group
            results = {}
            for voice, voice_requests in voice_groups.items():
                voice_results = await self._process_voice_batch(voice_requests, voice)
                results.update(voice_results)
            
            # Complete futures with results
            for request in batch:
                if request.request_id in results:
                    request.future.set_result(results[request.request_id])
                else:
                    request.future.set_exception(Exception("Batch processing failed"))
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_metrics(batch, processing_time, category)
            
            # Auto-tune if enabled
            if self.config.enable_auto_tuning:
                await self._auto_tune_parameters()
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            # Complete futures with exception
            for request in batch:
                if not request.future.done():
                    request.future.set_exception(e)
    
    async def _process_voice_batch(self, requests: List[BatchRequest], voice: str) -> Dict[str, Any]:
        """Process batch of requests for a specific voice"""
        # This would integrate with the actual TTS engine
        # For now, simulate batch processing
        
        results = {}
        texts = [req.text for req in requests]
        
        # Simulate batch TTS processing
        # In real implementation, this would call the TTS engine with batched inputs
        for i, request in enumerate(requests):
            # Simulate processing time based on text length
            processing_time = len(request.text) * 0.001  # 1ms per character
            await asyncio.sleep(processing_time)
            
            # Simulate audio result
            results[request.request_id] = {
                "audio_data": f"audio_for_{request.request_id}",
                "duration": len(request.text) * 0.05,  # 50ms per character
                "voice": voice,
                "batch_processed": True
            }
        
        return results
    
    async def _process_single_request(self, request: BatchRequest):
        """Process a single request immediately (for extra long texts)"""
        try:
            # Simulate single request processing
            processing_time = len(request.text) * 0.002  # Longer for single processing
            await asyncio.sleep(processing_time)
            
            result = {
                "audio_data": f"audio_for_{request.request_id}",
                "duration": len(request.text) * 0.05,
                "voice": request.voice,
                "batch_processed": False
            }
            
            request.future.set_result(result)
            
        except Exception as e:
            request.future.set_exception(e)
    
    def _get_queue(self, category: str) -> deque:
        """Get queue for category"""
        if category == "short":
            return self.short_queue
        elif category == "medium":
            return self.medium_queue
        elif category == "long":
            return self.long_queue
        else:
            raise ValueError(f"Unknown category: {category}")
    
    def _get_current_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0
    
    def _update_metrics(self, batch: List[BatchRequest], processing_time: float, category: str):
        """Update performance metrics"""
        self.metrics.total_requests += len(batch)
        self.metrics.batched_requests += len(batch)
        
        # Calculate batch efficiency
        max_batch_size = self.current_batch_sizes[category]
        efficiency = len(batch) / max_batch_size
        
        # Update running averages
        self.metrics.batch_efficiency = (self.metrics.batch_efficiency * 0.9 + efficiency * 0.1)
        self.metrics.avg_batch_size = (self.metrics.avg_batch_size * 0.9 + len(batch) * 0.1)
        
        # Calculate latency and RTF
        avg_text_length = sum(req.text_length for req in batch) / len(batch)
        latency_ms = processing_time * 1000
        rtf = processing_time / (avg_text_length * 0.05)  # Assuming 50ms per character audio
        
        self.metrics.avg_latency_ms = (self.metrics.avg_latency_ms * 0.9 + latency_ms * 0.1)
        self.metrics.avg_rtf = (self.metrics.avg_rtf * 0.9 + rtf * 0.1)
        self.metrics.memory_usage_mb = self._get_current_memory_usage()
        
        # Add to performance history
        self.performance_history.append({
            "timestamp": time.time(),
            "category": category,
            "batch_size": len(batch),
            "processing_time": processing_time,
            "latency_ms": latency_ms,
            "rtf": rtf,
            "efficiency": efficiency
        })
    
    async def _auto_tune_parameters(self):
        """Auto-tune batch sizes and timeouts based on performance"""
        current_time = time.time()
        
        if current_time - self.last_tuning_time < self.config.tuning_interval:
            return
        
        self.last_tuning_time = current_time
        
        if len(self.performance_history) < 10:
            return  # Need more data
        
        try:
            # Analyze recent performance
            recent_performance = list(self.performance_history)[-50:]  # Last 50 batches
            
            # Group by category
            category_performance = defaultdict(list)
            for perf in recent_performance:
                category_performance[perf["category"]].append(perf)
            
            # Tune each category
            for category, perfs in category_performance.items():
                if len(perfs) < 5:
                    continue
                
                avg_rtf = sum(p["rtf"] for p in perfs) / len(perfs)
                avg_latency = sum(p["latency_ms"] for p in perfs) / len(perfs)
                avg_efficiency = sum(p["efficiency"] for p in perfs) / len(perfs)
                
                # Adjust batch size based on performance
                current_batch_size = self.current_batch_sizes[category]
                
                if avg_rtf < self.config.target_rtf * 0.8 and avg_efficiency > 0.8:
                    # Performance is good, can increase batch size
                    new_batch_size = min(current_batch_size + 1, current_batch_size * 2)
                elif avg_rtf > self.config.target_rtf * 1.2 or avg_latency > self.config.max_latency_ms:
                    # Performance is poor, decrease batch size
                    new_batch_size = max(current_batch_size - 1, 1)
                else:
                    new_batch_size = current_batch_size
                
                if new_batch_size != current_batch_size:
                    self.current_batch_sizes[category] = new_batch_size
                    logger.info(f"Auto-tuned {category} batch size: {current_batch_size} → {new_batch_size}")
                
                # Adjust timeout based on efficiency
                current_timeout = self.current_timeouts[category]
                if avg_efficiency < 0.5:
                    # Low efficiency, reduce timeout to process smaller batches faster
                    new_timeout = max(current_timeout * 0.8, 10.0)
                elif avg_efficiency > 0.9:
                    # High efficiency, can afford longer timeout
                    new_timeout = min(current_timeout * 1.1, current_timeout * 2)
                else:
                    new_timeout = current_timeout
                
                if abs(new_timeout - current_timeout) > 5.0:
                    self.current_timeouts[category] = new_timeout
                    logger.info(f"Auto-tuned {category} timeout: {current_timeout:.1f}ms → {new_timeout:.1f}ms")
            
        except Exception as e:
            logger.warning(f"Auto-tuning failed: {e}")
    
    def get_metrics(self) -> BatchMetrics:
        """Get current batch processing metrics"""
        return self.metrics
    
    def get_status(self) -> Dict[str, Any]:
        """Get current batch optimizer status"""
        return {
            "queue_lengths": {
                "short": len(self.short_queue),
                "medium": len(self.medium_queue),
                "long": len(self.long_queue)
            },
            "current_batch_sizes": self.current_batch_sizes.copy(),
            "current_timeouts": self.current_timeouts.copy(),
            "active_batches": len(self.active_batches),
            "metrics": self.metrics,
            "memory_usage_mb": self._get_current_memory_usage()
        }

# Global batch optimizer instance
_global_batch_optimizer: Optional[DynamicBatchOptimizer] = None

def get_batch_optimizer() -> DynamicBatchOptimizer:
    """Get or create global batch optimizer instance"""
    global _global_batch_optimizer
    if _global_batch_optimizer is None:
        _global_batch_optimizer = DynamicBatchOptimizer()
    return _global_batch_optimizer
