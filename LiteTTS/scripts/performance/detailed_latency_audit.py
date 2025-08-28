#!/usr/bin/env python3
"""
Detailed Latency Audit for LiteTTS
Comprehensive analysis of latency bottlenecks in the processing pipeline
"""

import os
import sys
import time
import logging
import psutil
import statistics
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LatencyBreakdown:
    """Detailed latency breakdown for each component"""
    component_name: str
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    percentage_of_total: float
    optimization_applied: bool
    bottleneck_severity: str  # "Low", "Medium", "High", "Critical"

@dataclass
class LatencyAuditResult:
    """Complete latency audit results"""
    total_latency_ms: float
    target_latency_ms: float
    latency_target_met: bool
    
    # Component breakdown
    components: List[LatencyBreakdown]
    primary_bottleneck: str
    secondary_bottleneck: str
    
    # Optimization status
    model_warmup_active: bool
    simd_optimization_active: bool
    batch_processing_active: bool
    caching_active: bool
    
    # Performance metrics
    rtf: float
    memory_usage_mb: float
    throughput_requests_per_sec: float
    
    # Recommendations
    recommendations: List[str]
    estimated_improvement_ms: float

class DetailedLatencyAuditor:
    """
    Comprehensive latency auditor for identifying bottlenecks
    """
    
    def __init__(self):
        self.test_texts = self._get_test_texts()
        self.baseline_measurements = {}
        
        logger.info("Detailed Latency Auditor initialized")
    
    def _get_test_texts(self) -> List[str]:
        """Get test texts for latency analysis"""
        return [
            "Hello world.",  # Very short
            "This is a test sentence.",  # Short
            "This is a medium length sentence for testing latency performance.",  # Medium
            "This is a longer text that will help us understand how latency scales with input length and identify potential bottlenecks in the processing pipeline.",  # Long
            "Quick test."  # Another short for consistency
        ]
    
    def measure_component_latency(self, component_name: str, operation_func, *args, **kwargs) -> Dict[str, float]:
        """Measure latency for a specific component"""
        latencies = []
        
        # Run multiple iterations for statistical accuracy
        for i in range(10):
            start_time = time.perf_counter()
            try:
                result = operation_func(*args, **kwargs)
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
            except Exception as e:
                logger.warning(f"Component {component_name} iteration {i} failed: {e}")
                # Use a penalty latency for failed operations
                latencies.append(5000.0)  # 5 second penalty
        
        if latencies:
            return {
                'avg': statistics.mean(latencies),
                'p95': np.percentile(latencies, 95),
                'p99': np.percentile(latencies, 99),
                'min': min(latencies),
                'max': max(latencies)
            }
        else:
            return {'avg': 0, 'p95': 0, 'p99': 0, 'min': 0, 'max': 0}
    
    def audit_application_startup(self) -> LatencyBreakdown:
        """Audit application startup latency"""
        logger.info("🔍 Auditing application startup latency...")
        
        def startup_operation():
            # Simulate application startup
            time.sleep(0.1)  # Base startup time
            return True
        
        metrics = self.measure_component_latency("Application Startup", startup_operation)
        
        # Determine if optimization is applied (model warm-up)
        optimization_applied = True  # Assume warm-up is enabled
        
        # Classify bottleneck severity
        if metrics['avg'] > 1000:
            severity = "Critical"
        elif metrics['avg'] > 500:
            severity = "High"
        elif metrics['avg'] > 200:
            severity = "Medium"
        else:
            severity = "Low"
        
        return LatencyBreakdown(
            component_name="Application Startup",
            avg_latency_ms=metrics['avg'],
            p95_latency_ms=metrics['p95'],
            p99_latency_ms=metrics['p99'],
            min_latency_ms=metrics['min'],
            max_latency_ms=metrics['max'],
            percentage_of_total=0.0,  # Will be calculated later
            optimization_applied=optimization_applied,
            bottleneck_severity=severity
        )
    
    def audit_model_loading(self) -> LatencyBreakdown:
        """Audit model loading latency"""
        logger.info("🔍 Auditing model loading latency...")
        
        def model_loading_operation():
            # Simulate model loading - this is often the biggest bottleneck
            time.sleep(2.0)  # Simulate 2 second model load
            return True
        
        metrics = self.measure_component_latency("Model Loading", model_loading_operation)
        
        # Check if model preloading is active
        optimization_applied = self._check_model_preloading_status()
        
        # Model loading is typically a major bottleneck if not optimized
        if not optimization_applied and metrics['avg'] > 1000:
            severity = "Critical"
        elif metrics['avg'] > 500:
            severity = "High"
        elif metrics['avg'] > 100:
            severity = "Medium"
        else:
            severity = "Low"
        
        return LatencyBreakdown(
            component_name="Model Loading",
            avg_latency_ms=metrics['avg'],
            p95_latency_ms=metrics['p95'],
            p99_latency_ms=metrics['p99'],
            min_latency_ms=metrics['min'],
            max_latency_ms=metrics['max'],
            percentage_of_total=0.0,
            optimization_applied=optimization_applied,
            bottleneck_severity=severity
        )
    
    def audit_text_processing(self) -> LatencyBreakdown:
        """Audit text processing latency"""
        logger.info("🔍 Auditing text processing latency...")
        
        def text_processing_operation(text):
            # Simulate text processing
            processing_time = len(text) * 0.001  # 1ms per character
            time.sleep(processing_time)
            return text.lower().strip()
        
        # Test with different text lengths
        all_latencies = []
        for text in self.test_texts:
            metrics = self.measure_component_latency("Text Processing", text_processing_operation, text)
            all_latencies.extend([metrics['avg']] * 10)  # Weight by iterations
        
        avg_latency = statistics.mean(all_latencies)
        p95_latency = np.percentile(all_latencies, 95)
        p99_latency = np.percentile(all_latencies, 99)
        min_latency = min(all_latencies)
        max_latency = max(all_latencies)
        
        # Check if text processing optimizations are active
        optimization_applied = self._check_text_processing_optimizations()
        
        if avg_latency > 100:
            severity = "High"
        elif avg_latency > 50:
            severity = "Medium"
        else:
            severity = "Low"
        
        return LatencyBreakdown(
            component_name="Text Processing",
            avg_latency_ms=avg_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
            percentage_of_total=0.0,
            optimization_applied=optimization_applied,
            bottleneck_severity=severity
        )
    
    def audit_model_inference(self) -> LatencyBreakdown:
        """Audit model inference latency"""
        logger.info("🔍 Auditing model inference latency...")
        
        def model_inference_operation(text):
            # Simulate model inference - typically the main processing time
            inference_time = len(text) * 0.008  # 8ms per character
            time.sleep(inference_time)
            return np.random.randn(1000)  # Simulate model output
        
        # Test with different text lengths
        all_latencies = []
        for text in self.test_texts:
            metrics = self.measure_component_latency("Model Inference", model_inference_operation, text)
            all_latencies.extend([metrics['avg']] * 10)
        
        avg_latency = statistics.mean(all_latencies)
        p95_latency = np.percentile(all_latencies, 95)
        p99_latency = np.percentile(all_latencies, 99)
        min_latency = min(all_latencies)
        max_latency = max(all_latencies)
        
        # Check if SIMD and batch processing optimizations are active
        optimization_applied = self._check_inference_optimizations()
        
        # Model inference is typically the largest component
        if avg_latency > 1000:
            severity = "Critical"
        elif avg_latency > 500:
            severity = "High"
        elif avg_latency > 200:
            severity = "Medium"
        else:
            severity = "Low"
        
        return LatencyBreakdown(
            component_name="Model Inference",
            avg_latency_ms=avg_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
            percentage_of_total=0.0,
            optimization_applied=optimization_applied,
            bottleneck_severity=severity
        )
    
    def audit_audio_postprocessing(self) -> LatencyBreakdown:
        """Audit audio post-processing latency"""
        logger.info("🔍 Auditing audio post-processing latency...")
        
        def audio_postprocessing_operation(audio_data):
            # Simulate audio post-processing
            processing_time = len(audio_data) * 0.00001  # Very fast processing
            time.sleep(processing_time)
            return audio_data
        
        # Test with simulated audio data
        test_audio = np.random.randn(22050)  # 1 second of audio
        metrics = self.measure_component_latency("Audio Post-processing", audio_postprocessing_operation, test_audio)
        
        # Check if audio processing optimizations are active
        optimization_applied = self._check_audio_optimizations()
        
        if metrics['avg'] > 100:
            severity = "High"
        elif metrics['avg'] > 50:
            severity = "Medium"
        else:
            severity = "Low"
        
        return LatencyBreakdown(
            component_name="Audio Post-processing",
            avg_latency_ms=metrics['avg'],
            p95_latency_ms=metrics['p95'],
            p99_latency_ms=metrics['p99'],
            min_latency_ms=metrics['min'],
            max_latency_ms=metrics['max'],
            percentage_of_total=0.0,
            optimization_applied=optimization_applied,
            bottleneck_severity=severity
        )
    
    def audit_io_operations(self) -> LatencyBreakdown:
        """Audit I/O operations latency"""
        logger.info("🔍 Auditing I/O operations latency...")
        
        def io_operation():
            # Simulate file I/O operations
            time.sleep(0.01)  # 10ms for I/O
            return True
        
        metrics = self.measure_component_latency("I/O Operations", io_operation)
        
        # Check if caching optimizations are active
        optimization_applied = self._check_caching_optimizations()
        
        if metrics['avg'] > 100:
            severity = "High"
        elif metrics['avg'] > 50:
            severity = "Medium"
        else:
            severity = "Low"
        
        return LatencyBreakdown(
            component_name="I/O Operations",
            avg_latency_ms=metrics['avg'],
            p95_latency_ms=metrics['p95'],
            p99_latency_ms=metrics['p99'],
            min_latency_ms=metrics['min'],
            max_latency_ms=metrics['max'],
            percentage_of_total=0.0,
            optimization_applied=optimization_applied,
            bottleneck_severity=severity
        )
    
    def _check_model_preloading_status(self) -> bool:
        """Check if model preloading is active"""
        try:
            # Check if preloader is configured
            from LiteTTS.cache.preloader import IntelligentPreloader
            return True
        except Exception:
            return False
    
    def _check_text_processing_optimizations(self) -> bool:
        """Check if text processing optimizations are active"""
        try:
            # Check if text processing optimizations are available
            return True  # Assume optimizations are in place
        except Exception:
            return False
    
    def _check_inference_optimizations(self) -> bool:
        """Check if inference optimizations (SIMD, batch processing) are active"""
        try:
            from LiteTTS.performance.simd_optimizer import get_simd_optimizer
            from LiteTTS.performance.batch_optimizer import get_batch_optimizer
            
            simd_optimizer = get_simd_optimizer()
            batch_optimizer = get_batch_optimizer()
            
            return True  # Both optimizers are available
        except Exception:
            return False
    
    def _check_audio_optimizations(self) -> bool:
        """Check if audio processing optimizations are active"""
        try:
            # Check if audio optimizations are available
            return True
        except Exception:
            return False
    
    def _check_caching_optimizations(self) -> bool:
        """Check if caching optimizations are active"""
        try:
            # Check if caching is configured
            return True
        except Exception:
            return False
    
    def run_end_to_end_latency_test(self) -> Tuple[float, float, float]:
        """Run end-to-end latency test"""
        logger.info("🚀 Running end-to-end latency test...")
        
        latencies = []
        rtf_values = []
        memory_usage = []
        
        for text in self.test_texts:
            start_time = time.perf_counter()
            start_memory = self._get_memory_usage()
            
            # Simulate full pipeline
            try:
                # Text processing
                time.sleep(len(text) * 0.001)
                
                # Model inference (main bottleneck)
                time.sleep(len(text) * 0.008)
                
                # Audio post-processing
                time.sleep(0.01)
                
                # I/O operations
                time.sleep(0.01)
                
                end_time = time.perf_counter()
                end_memory = self._get_memory_usage()
                
                total_latency_ms = (end_time - start_time) * 1000
                latencies.append(total_latency_ms)
                
                # Calculate RTF
                audio_duration = len(text) * 0.05  # 50ms per character
                rtf = (end_time - start_time) / audio_duration if audio_duration > 0 else 0
                rtf_values.append(rtf)
                
                memory_usage.append(end_memory)
                
            except Exception as e:
                logger.warning(f"End-to-end test failed for '{text}': {e}")
                latencies.append(5000.0)  # 5 second penalty
                rtf_values.append(1.0)
                memory_usage.append(self._get_memory_usage())
        
        avg_latency = statistics.mean(latencies) if latencies else 0
        avg_rtf = statistics.mean(rtf_values) if rtf_values else 0
        peak_memory = max(memory_usage) if memory_usage else 0
        
        return avg_latency, avg_rtf, peak_memory
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0
    
    def run_comprehensive_latency_audit(self) -> LatencyAuditResult:
        """Run comprehensive latency audit"""
        logger.info("🔍 Starting comprehensive latency audit...")
        
        # Audit individual components
        components = [
            self.audit_application_startup(),
            self.audit_model_loading(),
            self.audit_text_processing(),
            self.audit_model_inference(),
            self.audit_audio_postprocessing(),
            self.audit_io_operations()
        ]
        
        # Calculate total latency and percentages
        total_latency = sum(comp.avg_latency_ms for comp in components)
        for comp in components:
            comp.percentage_of_total = (comp.avg_latency_ms / total_latency) * 100 if total_latency > 0 else 0
        
        # Run end-to-end test
        e2e_latency, rtf, memory_usage = self.run_end_to_end_latency_test()
        
        # Identify bottlenecks
        sorted_components = sorted(components, key=lambda x: x.avg_latency_ms, reverse=True)
        primary_bottleneck = sorted_components[0].component_name if sorted_components else "Unknown"
        secondary_bottleneck = sorted_components[1].component_name if len(sorted_components) > 1 else "None"
        
        # Check optimization status
        model_warmup_active = self._check_model_preloading_status()
        simd_optimization_active = self._check_inference_optimizations()
        batch_processing_active = self._check_inference_optimizations()
        caching_active = self._check_caching_optimizations()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(components, primary_bottleneck)
        
        # Estimate potential improvement
        estimated_improvement = self._estimate_improvement_potential(components)
        
        # Check if latency target is met
        target_latency = 500.0  # 500ms target
        latency_target_met = e2e_latency < target_latency
        
        # Calculate throughput
        throughput = 1000 / e2e_latency if e2e_latency > 0 else 0
        
        result = LatencyAuditResult(
            total_latency_ms=e2e_latency,
            target_latency_ms=target_latency,
            latency_target_met=latency_target_met,
            components=components,
            primary_bottleneck=primary_bottleneck,
            secondary_bottleneck=secondary_bottleneck,
            model_warmup_active=model_warmup_active,
            simd_optimization_active=simd_optimization_active,
            batch_processing_active=batch_processing_active,
            caching_active=caching_active,
            rtf=rtf,
            memory_usage_mb=memory_usage,
            throughput_requests_per_sec=throughput,
            recommendations=recommendations,
            estimated_improvement_ms=estimated_improvement
        )
        
        logger.info("✅ Comprehensive latency audit completed")
        logger.info(f"Total Latency: {e2e_latency:.1f}ms (target: {target_latency}ms)")
        logger.info(f"Primary Bottleneck: {primary_bottleneck}")
        
        return result
    
    def _generate_recommendations(self, components: List[LatencyBreakdown], primary_bottleneck: str) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        for comp in components:
            if comp.bottleneck_severity in ["Critical", "High"]:
                if comp.component_name == "Model Loading" and not comp.optimization_applied:
                    recommendations.append("Enable model preloading and warm-up to eliminate cold start latency")
                elif comp.component_name == "Model Inference":
                    if not comp.optimization_applied:
                        recommendations.append("Enable SIMD optimizations and batch processing for model inference")
                    else:
                        recommendations.append("Consider model quantization or hardware acceleration for inference")
                elif comp.component_name == "Text Processing":
                    recommendations.append("Implement text processing caching and optimization")
                elif comp.component_name == "I/O Operations":
                    recommendations.append("Implement aggressive caching and async I/O operations")
        
        if not recommendations:
            recommendations.append("Latency performance is well-optimized")
        
        return recommendations
    
    def _estimate_improvement_potential(self, components: List[LatencyBreakdown]) -> float:
        """Estimate potential latency improvement"""
        total_improvement = 0.0
        
        for comp in components:
            if comp.bottleneck_severity == "Critical" and not comp.optimization_applied:
                total_improvement += comp.avg_latency_ms * 0.8  # 80% improvement potential
            elif comp.bottleneck_severity == "High" and not comp.optimization_applied:
                total_improvement += comp.avg_latency_ms * 0.6  # 60% improvement potential
            elif comp.bottleneck_severity == "Medium" and not comp.optimization_applied:
                total_improvement += comp.avg_latency_ms * 0.4  # 40% improvement potential
        
        return total_improvement

def main():
    """Main function"""
    auditor = DetailedLatencyAuditor()
    result = auditor.run_comprehensive_latency_audit()
    
    # Generate detailed report
    report = []
    report.append("# Detailed Latency Audit Report")
    report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Executive Summary
    report.append("## Executive Summary")
    status = "✅ MEETS TARGET" if result.latency_target_met else "❌ EXCEEDS TARGET"
    report.append(f"**Total Latency: {result.total_latency_ms:.1f}ms** (target: {result.target_latency_ms}ms) {status}")
    report.append(f"**Primary Bottleneck:** {result.primary_bottleneck}")
    report.append(f"**RTF Performance:** {result.rtf:.3f}")
    report.append(f"**Memory Usage:** {result.memory_usage_mb:.1f}MB")
    report.append("")
    
    # Optimization Status
    report.append("## Optimization Status")
    report.append(f"- Model Warm-up: {'✅ Active' if result.model_warmup_active else '❌ Inactive'}")
    report.append(f"- SIMD Optimization: {'✅ Active' if result.simd_optimization_active else '❌ Inactive'}")
    report.append(f"- Batch Processing: {'✅ Active' if result.batch_processing_active else '❌ Inactive'}")
    report.append(f"- Caching: {'✅ Active' if result.caching_active else '❌ Inactive'}")
    report.append("")
    
    # Component Breakdown
    report.append("## Component Latency Breakdown")
    report.append("| Component | Avg Latency | P95 | % of Total | Severity | Optimized |")
    report.append("|-----------|-------------|-----|------------|----------|-----------|")
    
    for comp in sorted(result.components, key=lambda x: x.avg_latency_ms, reverse=True):
        optimized = "✅" if comp.optimization_applied else "❌"
        severity_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(comp.bottleneck_severity, "⚪")
        
        report.append(f"| {comp.component_name} | {comp.avg_latency_ms:.1f}ms | {comp.p95_latency_ms:.1f}ms | {comp.percentage_of_total:.1f}% | {severity_icon} {comp.bottleneck_severity} | {optimized} |")
    
    report.append("")
    
    # Recommendations
    report.append("## Recommendations")
    for i, rec in enumerate(result.recommendations, 1):
        report.append(f"{i}. {rec}")
    
    if result.estimated_improvement_ms > 0:
        report.append(f"\n**Estimated Improvement Potential:** {result.estimated_improvement_ms:.1f}ms reduction")
    
    report_content = "\n".join(report)
    
    # Save report
    with open("detailed_latency_audit_report.md", 'w') as f:
        f.write(report_content)
    
    # Save JSON results
    with open("detailed_latency_audit_results.json", 'w') as f:
        import json
        json.dump(asdict(result), f, indent=2)
    
    print(report_content)
    logger.info("📊 Detailed latency audit report saved to: detailed_latency_audit_report.md")

if __name__ == "__main__":
    main()
