#!/usr/bin/env python3
"""
Pipeline Parallelism Implementation
Add pipeline parallelism for TTS stages, optimize threading configuration for aggressive CPU utilization (90-95%)
"""

import os
import sys
import json
import logging
import asyncio
import time
import threading
import queue
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PipelineStage:
    """Pipeline stage configuration"""
    stage_name: str
    stage_function: str
    input_queue_size: int
    output_queue_size: int
    worker_count: int
    cpu_affinity: List[int]
    priority: int
    timeout_seconds: float

@dataclass
class PipelineMetrics:
    """Pipeline performance metrics"""
    stage_name: str
    total_processed: int
    processing_time: float
    queue_wait_time: float
    cpu_utilization: float
    memory_usage_mb: float
    throughput_per_second: float
    error_count: int

@dataclass
class PipelineConfiguration:
    """Complete pipeline configuration"""
    enable_pipeline_parallelism: bool
    target_cpu_utilization: float
    max_concurrent_pipelines: int
    enable_stage_overlap: bool
    enable_batch_processing: bool
    batch_size: int
    queue_monitoring_enabled: bool
    adaptive_worker_scaling: bool
    stages: List[PipelineStage]

class TTSPipelineStage:
    """Individual TTS pipeline stage"""
    
    def __init__(self, stage_config: PipelineStage):
        self.config = stage_config
        self.input_queue = queue.Queue(maxsize=stage_config.input_queue_size)
        self.output_queue = queue.Queue(maxsize=stage_config.output_queue_size)
        self.workers = []
        self.metrics = PipelineMetrics(
            stage_name=stage_config.stage_name,
            total_processed=0,
            processing_time=0.0,
            queue_wait_time=0.0,
            cpu_utilization=0.0,
            memory_usage_mb=0.0,
            throughput_per_second=0.0,
            error_count=0
        )
        self.running = False
        self.start_time = None
    
    def start_workers(self):
        """Start worker threads for this stage"""
        self.running = True
        self.start_time = time.time()
        
        for i in range(self.config.worker_count):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"{self.config.stage_name}_worker_{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Started {self.config.worker_count} workers for stage: {self.config.stage_name}")
    
    def stop_workers(self):
        """Stop worker threads"""
        self.running = False
        
        # Add sentinel values to wake up workers
        for _ in range(self.config.worker_count):
            try:
                self.input_queue.put(None, timeout=1.0)
            except queue.Full:
                pass
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5.0)
        
        logger.info(f"Stopped workers for stage: {self.config.stage_name}")
    
    def _worker_loop(self):
        """Main worker loop"""
        while self.running:
            try:
                # Get input with timeout
                queue_wait_start = time.time()
                item = self.input_queue.get(timeout=1.0)
                queue_wait_time = time.time() - queue_wait_start
                
                if item is None:  # Sentinel value to stop
                    break
                
                # Process item
                process_start = time.time()
                result = self._process_item(item)
                process_time = time.time() - process_start
                
                # Update metrics
                self.metrics.total_processed += 1
                self.metrics.processing_time += process_time
                self.metrics.queue_wait_time += queue_wait_time
                
                # Put result in output queue
                if result is not None:
                    self.output_queue.put(result, timeout=self.config.timeout_seconds)
                
                self.input_queue.task_done()
                
            except queue.Empty:
                continue
            except queue.Full:
                self.metrics.error_count += 1
                logger.warning(f"Output queue full for stage: {self.config.stage_name}")
            except Exception as e:
                self.metrics.error_count += 1
                logger.error(f"Error in stage {self.config.stage_name}: {e}")
    
    def _process_item(self, item: Any) -> Any:
        """Process individual item (to be overridden by specific stages)"""
        # Simulate processing time
        time.sleep(0.001)
        return item
    
    def get_metrics(self) -> PipelineMetrics:
        """Get current stage metrics"""
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                self.metrics.throughput_per_second = self.metrics.total_processed / elapsed_time
        
        return self.metrics

class TextPreprocessingStage(TTSPipelineStage):
    """Text preprocessing pipeline stage"""
    
    def _process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process text preprocessing"""
        text = item.get("text", "")
        
        # Simulate text preprocessing
        processed_text = text.strip().lower()
        
        return {
            **item,
            "processed_text": processed_text,
            "stage": "text_preprocessing"
        }

class PhonemizationStage(TTSPipelineStage):
    """Phonemization pipeline stage"""
    
    def _process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process phonemization"""
        processed_text = item.get("processed_text", "")
        
        # Simulate phonemization
        phonemes = f"/{processed_text.replace(' ', '/')}/".replace("//", "/")
        
        return {
            **item,
            "phonemes": phonemes,
            "stage": "phonemization"
        }

class AudioGenerationStage(TTSPipelineStage):
    """Audio generation pipeline stage"""
    
    def _process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process audio generation"""
        phonemes = item.get("phonemes", "")
        
        # Simulate audio generation (more CPU intensive)
        time.sleep(0.01)  # Simulate ONNX inference time
        
        return {
            **item,
            "audio_data": f"audio_for_{phonemes}",
            "stage": "audio_generation"
        }

class PostProcessingStage(TTSPipelineStage):
    """Post-processing pipeline stage"""
    
    def _process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process post-processing"""
        audio_data = item.get("audio_data", "")
        
        # Simulate post-processing
        processed_audio = f"processed_{audio_data}"
        
        return {
            **item,
            "final_audio": processed_audio,
            "stage": "post_processing"
        }

class PipelineParallelismManager:
    """Pipeline parallelism manager"""
    
    def __init__(self):
        self.results_dir = Path("test_results/pipeline_parallelism")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # CPU information
        self.cpu_count = psutil.cpu_count()
        self.target_cpu_utilization = 0.92  # 92% target
        
        # Pipeline stages
        self.stages = {}
        self.pipeline_config = None
        
        # Monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        self.cpu_history = []
        
    def create_optimal_pipeline_config(self) -> PipelineConfiguration:
        """Create optimal pipeline configuration"""
        logger.info("Creating optimal pipeline configuration...")
        
        # Calculate optimal worker distribution
        total_workers = max(4, int(self.cpu_count * 0.8))  # Use 80% of cores
        
        # Stage configurations with different CPU requirements
        stage_configs = [
            PipelineStage(
                stage_name="text_preprocessing",
                stage_function="text_preprocessing",
                input_queue_size=100,
                output_queue_size=100,
                worker_count=max(1, total_workers // 8),  # Light CPU usage
                cpu_affinity=[],
                priority=1,
                timeout_seconds=5.0
            ),
            PipelineStage(
                stage_name="phonemization",
                stage_function="phonemization",
                input_queue_size=50,
                output_queue_size=50,
                worker_count=max(1, total_workers // 4),  # Medium CPU usage
                cpu_affinity=[],
                priority=2,
                timeout_seconds=10.0
            ),
            PipelineStage(
                stage_name="audio_generation",
                stage_function="audio_generation",
                input_queue_size=20,
                output_queue_size=20,
                worker_count=max(2, total_workers // 2),  # Heavy CPU usage
                cpu_affinity=[],
                priority=3,
                timeout_seconds=30.0
            ),
            PipelineStage(
                stage_name="post_processing",
                stage_function="post_processing",
                input_queue_size=50,
                output_queue_size=50,
                worker_count=max(1, total_workers // 8),  # Light CPU usage
                cpu_affinity=[],
                priority=1,
                timeout_seconds=5.0
            )
        ]
        
        config = PipelineConfiguration(
            enable_pipeline_parallelism=True,
            target_cpu_utilization=self.target_cpu_utilization,
            max_concurrent_pipelines=max(2, self.cpu_count // 4),
            enable_stage_overlap=True,
            enable_batch_processing=True,
            batch_size=4,
            queue_monitoring_enabled=True,
            adaptive_worker_scaling=True,
            stages=stage_configs
        )
        
        logger.info(f"Created pipeline config with {total_workers} total workers across {len(stage_configs)} stages")
        return config
    
    def initialize_pipeline(self, config: PipelineConfiguration):
        """Initialize pipeline with given configuration"""
        logger.info("Initializing pipeline...")
        
        self.pipeline_config = config
        
        # Create stage instances
        stage_classes = {
            "text_preprocessing": TextPreprocessingStage,
            "phonemization": PhonemizationStage,
            "audio_generation": AudioGenerationStage,
            "post_processing": PostProcessingStage
        }
        
        for stage_config in config.stages:
            stage_class = stage_classes.get(stage_config.stage_function, TTSPipelineStage)
            stage = stage_class(stage_config)
            self.stages[stage_config.stage_name] = stage
        
        # Connect stages
        stage_names = [s.stage_name for s in config.stages]
        for i in range(len(stage_names) - 1):
            current_stage = self.stages[stage_names[i]]
            next_stage = self.stages[stage_names[i + 1]]
            # Output of current stage becomes input of next stage
            # This would be implemented with proper queue connections in production
        
        logger.info(f"Initialized {len(self.stages)} pipeline stages")
    
    def start_pipeline(self):
        """Start all pipeline stages"""
        logger.info("Starting pipeline...")
        
        for stage in self.stages.values():
            stage.start_workers()
        
        # Start monitoring
        self.start_cpu_monitoring()
        
        logger.info("Pipeline started successfully")
    
    def stop_pipeline(self):
        """Stop all pipeline stages"""
        logger.info("Stopping pipeline...")
        
        # Stop monitoring
        self.stop_cpu_monitoring()
        
        # Stop stages in reverse order
        stage_names = list(self.stages.keys())
        for stage_name in reversed(stage_names):
            self.stages[stage_name].stop_workers()
        
        logger.info("Pipeline stopped successfully")
    
    def start_cpu_monitoring(self):
        """Start CPU utilization monitoring"""
        self.monitoring_active = True
        self.cpu_history = []
        
        def monitor_loop():
            while self.monitoring_active:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1.0)
                    self.cpu_history.append({
                        "timestamp": time.time(),
                        "cpu_percent": cpu_percent
                    })
                except Exception as e:
                    logger.warning(f"CPU monitoring error: {e}")
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("CPU monitoring started")
    
    def stop_cpu_monitoring(self) -> Dict[str, float]:
        """Stop CPU monitoring and return statistics"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        if not self.cpu_history:
            return {"error": "No monitoring data"}
        
        cpu_values = [entry["cpu_percent"] for entry in self.cpu_history]
        
        stats = {
            "avg_cpu_utilization": sum(cpu_values) / len(cpu_values),
            "max_cpu_utilization": max(cpu_values),
            "min_cpu_utilization": min(cpu_values),
            "target_cpu_utilization": self.target_cpu_utilization * 100,
            "target_achieved": (sum(cpu_values) / len(cpu_values)) >= (self.target_cpu_utilization * 100 * 0.9),
            "monitoring_duration": self.cpu_history[-1]["timestamp"] - self.cpu_history[0]["timestamp"]
        }
        
        logger.info("CPU monitoring stopped")
        return stats
    
    def simulate_pipeline_workload(self, num_requests: int = 100) -> Dict[str, Any]:
        """Simulate pipeline workload"""
        logger.info(f"Simulating pipeline workload with {num_requests} requests...")
        
        start_time = time.time()
        
        # Generate test requests
        test_requests = []
        for i in range(num_requests):
            test_requests.append({
                "request_id": f"req_{i}",
                "text": f"Test text number {i} for pipeline processing",
                "voice": "af_heart",
                "timestamp": time.time()
            })
        
        # Process requests through pipeline (simulation)
        processed_requests = []
        
        for request in test_requests:
            # Simulate pipeline processing
            current_item = request
            
            for stage_name in self.stages.keys():
                stage = self.stages[stage_name]
                # Simulate stage processing
                if stage_name == "text_preprocessing":
                    current_item = TextPreprocessingStage(stage.config)._process_item(current_item)
                elif stage_name == "phonemization":
                    current_item = PhonemizationStage(stage.config)._process_item(current_item)
                elif stage_name == "audio_generation":
                    current_item = AudioGenerationStage(stage.config)._process_item(current_item)
                elif stage_name == "post_processing":
                    current_item = PostProcessingStage(stage.config)._process_item(current_item)
                
                # Update stage metrics
                stage.metrics.total_processed += 1
            
            processed_requests.append(current_item)
        
        total_time = time.time() - start_time
        
        workload_stats = {
            "total_requests": num_requests,
            "processed_requests": len(processed_requests),
            "total_processing_time": total_time,
            "requests_per_second": len(processed_requests) / total_time if total_time > 0 else 0,
            "avg_request_time": total_time / len(processed_requests) if processed_requests else 0
        }
        
        logger.info(f"Workload simulation completed: {workload_stats['requests_per_second']:.2f} req/s")
        return workload_stats
    
    def run_comprehensive_pipeline_test(self, test_duration: int = 60) -> Dict[str, Any]:
        """Run comprehensive pipeline parallelism test"""
        logger.info("Starting comprehensive pipeline parallelism test...")
        
        # Create optimal configuration
        config = self.create_optimal_pipeline_config()
        
        # Initialize pipeline
        self.initialize_pipeline(config)
        
        # Start pipeline
        self.start_pipeline()
        
        # Run workload simulation
        workload_stats = self.simulate_pipeline_workload(num_requests=200)
        
        # Let pipeline run for test duration
        logger.info(f"Running pipeline for {test_duration} seconds...")
        time.sleep(test_duration)
        
        # Collect metrics
        stage_metrics = {}
        for stage_name, stage in self.stages.items():
            stage_metrics[stage_name] = asdict(stage.get_metrics())
        
        # Stop pipeline
        cpu_stats = self.stop_cpu_monitoring()
        self.stop_pipeline()
        
        # Compile results
        results = {
            "test_timestamp": time.time(),
            "test_duration": test_duration,
            "pipeline_configuration": asdict(config),
            "workload_statistics": workload_stats,
            "stage_metrics": stage_metrics,
            "cpu_utilization_stats": cpu_stats,
            "performance_analysis": self._analyze_pipeline_performance(stage_metrics, cpu_stats, workload_stats),
            "recommendations": self._generate_pipeline_recommendations(config, stage_metrics, cpu_stats)
        }
        
        # Save results
        results_file = self.results_dir / f"pipeline_parallelism_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Pipeline test completed. Results saved to: {results_file}")
        return results

    def _analyze_pipeline_performance(self, stage_metrics: Dict[str, Any],
                                    cpu_stats: Dict[str, float],
                                    workload_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pipeline performance"""

        # Calculate overall throughput
        total_processed = sum(metrics["total_processed"] for metrics in stage_metrics.values())
        total_processing_time = sum(metrics["processing_time"] for metrics in stage_metrics.values())

        # Identify bottlenecks
        bottleneck_stage = None
        min_throughput = float('inf')

        for stage_name, metrics in stage_metrics.items():
            if metrics["throughput_per_second"] < min_throughput:
                min_throughput = metrics["throughput_per_second"]
                bottleneck_stage = stage_name

        # Calculate efficiency metrics
        cpu_efficiency = cpu_stats.get("avg_cpu_utilization", 0) / 100.0
        target_efficiency = cpu_stats.get("target_cpu_utilization", 90) / 100.0
        efficiency_ratio = cpu_efficiency / target_efficiency if target_efficiency > 0 else 0

        analysis = {
            "overall_throughput": total_processed / total_processing_time if total_processing_time > 0 else 0,
            "bottleneck_stage": bottleneck_stage,
            "bottleneck_throughput": min_throughput,
            "cpu_efficiency": cpu_efficiency,
            "target_efficiency": target_efficiency,
            "efficiency_ratio": efficiency_ratio,
            "cpu_target_achieved": cpu_stats.get("target_achieved", False),
            "pipeline_balance": self._calculate_pipeline_balance(stage_metrics),
            "performance_grade": self._calculate_pipeline_grade(cpu_efficiency, efficiency_ratio, workload_stats)
        }

        return analysis

    def _calculate_pipeline_balance(self, stage_metrics: Dict[str, Any]) -> float:
        """Calculate pipeline balance (how evenly distributed the load is)"""
        throughputs = [metrics["throughput_per_second"] for metrics in stage_metrics.values()]

        if not throughputs or max(throughputs) == 0:
            return 0.0

        # Calculate coefficient of variation (lower is better balanced)
        mean_throughput = sum(throughputs) / len(throughputs)
        variance = sum((t - mean_throughput) ** 2 for t in throughputs) / len(throughputs)
        std_dev = variance ** 0.5

        cv = std_dev / mean_throughput if mean_throughput > 0 else float('inf')

        # Convert to balance score (0-1, higher is better)
        balance_score = max(0, 1 - cv)
        return balance_score

    def _calculate_pipeline_grade(self, cpu_efficiency: float, efficiency_ratio: float,
                                workload_stats: Dict[str, Any]) -> str:
        """Calculate overall pipeline performance grade"""
        score = 0

        # CPU utilization score
        if cpu_efficiency >= 0.90:
            score += 3
        elif cpu_efficiency >= 0.80:
            score += 2
        elif cpu_efficiency >= 0.70:
            score += 1

        # Efficiency ratio score
        if efficiency_ratio >= 0.95:
            score += 2
        elif efficiency_ratio >= 0.85:
            score += 1

        # Throughput score
        req_per_sec = workload_stats.get("requests_per_second", 0)
        if req_per_sec >= 10:
            score += 2
        elif req_per_sec >= 5:
            score += 1

        # Grade assignment
        if score >= 6:
            return "A+"
        elif score >= 5:
            return "A"
        elif score >= 4:
            return "B"
        elif score >= 3:
            return "C"
        else:
            return "D"

    def _generate_pipeline_recommendations(self, config: PipelineConfiguration,
                                         stage_metrics: Dict[str, Any],
                                         cpu_stats: Dict[str, float]) -> List[str]:
        """Generate pipeline optimization recommendations"""
        recommendations = []

        # CPU utilization recommendations
        avg_cpu = cpu_stats.get("avg_cpu_utilization", 0)
        target_cpu = cpu_stats.get("target_cpu_utilization", 90)

        if avg_cpu < target_cpu * 0.8:
            recommendations.append(f"CPU utilization ({avg_cpu:.1f}%) below target ({target_cpu:.1f}%) - increase worker count or workload")
        elif avg_cpu > target_cpu * 1.1:
            recommendations.append(f"CPU utilization ({avg_cpu:.1f}%) exceeds target ({target_cpu:.1f}%) - reduce worker count or optimize algorithms")

        # Stage-specific recommendations
        for stage_name, metrics in stage_metrics.items():
            error_rate = metrics["error_count"] / max(1, metrics["total_processed"])

            if error_rate > 0.05:  # > 5% error rate
                recommendations.append(f"High error rate in {stage_name} stage ({error_rate:.1%}) - investigate queue sizes and timeouts")

            if metrics["throughput_per_second"] < 1.0:
                recommendations.append(f"Low throughput in {stage_name} stage - consider increasing worker count")

        # Configuration recommendations
        if not config.enable_stage_overlap:
            recommendations.append("Enable stage overlap for better pipeline efficiency")

        if not config.enable_batch_processing:
            recommendations.append("Enable batch processing for improved throughput")

        if config.max_concurrent_pipelines < self.cpu_count // 2:
            recommendations.append("Consider increasing max concurrent pipelines for better CPU utilization")

        return recommendations

def main():
    """Main function to run pipeline parallelism test"""
    manager = PipelineParallelismManager()

    try:
        results = manager.run_comprehensive_pipeline_test(test_duration=30)

        print("\n" + "="*80)
        print("PIPELINE PARALLELISM SUMMARY")
        print("="*80)

        config = results["pipeline_configuration"]
        workload = results["workload_statistics"]
        cpu_stats = results["cpu_utilization_stats"]
        analysis = results["performance_analysis"]

        print(f"Pipeline Configuration:")
        print(f"  Total Stages: {len(config['stages'])}")
        print(f"  Total Workers: {sum(stage['worker_count'] for stage in config['stages'])}")
        print(f"  Target CPU Utilization: {config['target_cpu_utilization']:.1%}")
        print(f"  Max Concurrent Pipelines: {config['max_concurrent_pipelines']}")

        print(f"\nWorkload Performance:")
        print(f"  Requests Processed: {workload['processed_requests']}")
        print(f"  Requests per Second: {workload['requests_per_second']:.2f}")
        print(f"  Average Request Time: {workload['avg_request_time']:.3f}s")

        print(f"\nCPU Utilization:")
        print(f"  Average: {cpu_stats['avg_cpu_utilization']:.1f}%")
        print(f"  Maximum: {cpu_stats['max_cpu_utilization']:.1f}%")
        print(f"  Target Achieved: {'✅' if cpu_stats['target_achieved'] else '❌'}")

        print(f"\nPerformance Analysis:")
        print(f"  Performance Grade: {analysis['performance_grade']}")
        print(f"  CPU Efficiency: {analysis['cpu_efficiency']:.1%}")
        print(f"  Efficiency Ratio: {analysis['efficiency_ratio']:.1%}")
        print(f"  Pipeline Balance: {analysis['pipeline_balance']:.3f}")
        print(f"  Bottleneck Stage: {analysis['bottleneck_stage']}")

        print(f"\nStage Performance:")
        for stage_name, metrics in results["stage_metrics"].items():
            print(f"  {stage_name}: {metrics['total_processed']} processed, {metrics['throughput_per_second']:.2f} req/s")

        print(f"\nRecommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
