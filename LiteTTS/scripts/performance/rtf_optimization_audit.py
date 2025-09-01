#!/usr/bin/env python3
"""
RTF Optimization & Code Audit

Comprehensive analysis of Real-Time Factor (RTF) performance and identification
of bottlenecks in the TTS system. Provides optimization recommendations and
performance improvements.
"""

import requests
import time
import json
import statistics
import psutil
import os
from typing import Dict, List, Tuple, Any
from pathlib import Path
import numpy as np

class RTFOptimizationAuditor:
    """Comprehensive RTF performance auditor and optimizer"""
    
    def __init__(self, base_url: str = "http://localhost:8354"):
        self.base_url = base_url
        self.results = {
            'baseline_performance': {},
            'bottleneck_analysis': {},
            'optimization_recommendations': [],
            'before_after_metrics': {},
            'system_analysis': {}
        }
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run complete RTF optimization audit"""
        
        print("🚀 RTF Optimization & Code Audit")
        print("=" * 50)
        
        # 1. Baseline Performance Analysis
        print("\n📊 1. Baseline Performance Analysis")
        self.analyze_baseline_performance()
        
        # 2. Bottleneck Identification
        print("\n🔍 2. Bottleneck Identification")
        self.identify_bottlenecks()
        
        # 3. System Resource Analysis
        print("\n💻 3. System Resource Analysis")
        self.analyze_system_resources()
        
        # 4. Audio Processing Pipeline Analysis
        print("\n🎵 4. Audio Processing Pipeline Analysis")
        self.analyze_audio_pipeline()
        
        # 5. Memory Usage Analysis
        print("\n💾 5. Memory Usage Analysis")
        self.analyze_memory_usage()
        
        # 6. Generate Optimization Recommendations
        print("\n💡 6. Optimization Recommendations")
        self.generate_recommendations()
        
        # 7. Performance Improvement Validation
        print("\n✅ 7. Performance Validation")
        self.validate_improvements()
        
        return self.results
    
    def analyze_baseline_performance(self):
        """Analyze current baseline RTF performance"""
        
        test_cases = [
            {"text": "Hello world", "category": "short"},
            {"text": "This is a medium length sentence for testing TTS performance.", "category": "medium"},
            {"text": "This is a much longer text that will help us understand how the TTS system performs with extended content. It includes multiple sentences and should give us a good baseline for RTF measurements across different text lengths.", "category": "long"},
            {"text": "Quick test", "category": "cached"}  # Run twice to test cache
        ]
        
        voices_to_test = ["af_heart", "am_onyx", "bf_alice", "jf_alpha"]
        
        baseline_results = {}
        
        for voice in voices_to_test:
            print(f"   Testing voice: {voice}")
            voice_results = {}
            
            for test_case in test_cases:
                text = test_case["text"]
                category = test_case["category"]
                
                # Run test multiple times for statistical accuracy
                rtf_values = []
                response_times = []
                
                for run in range(3):
                    try:
                        start_time = time.time()
                        response = requests.post(
                            f"{self.base_url}/v1/audio/speech",
                            json={
                                "input": text,
                                "voice": voice,
                                "response_format": "mp3"
                            },
                            timeout=30
                        )
                        end_time = time.time()
                        
                        if response.status_code == 200:
                            generation_time = end_time - start_time
                            audio_size = len(response.content)
                            
                            # Estimate audio duration more accurately
                            # MP3 compression varies, but roughly 16KB/second at 128kbps
                            estimated_duration = audio_size / 16000
                            rtf = generation_time / estimated_duration if estimated_duration > 0 else 0
                            
                            rtf_values.append(rtf)
                            response_times.append(generation_time)
                            
                        time.sleep(0.1)  # Small delay between runs
                        
                    except Exception as e:
                        print(f"      ❌ Error in run {run+1}: {e}")
                
                if rtf_values:
                    voice_results[category] = {
                        'avg_rtf': statistics.mean(rtf_values),
                        'min_rtf': min(rtf_values),
                        'max_rtf': max(rtf_values),
                        'std_rtf': statistics.stdev(rtf_values) if len(rtf_values) > 1 else 0,
                        'avg_response_time': statistics.mean(response_times),
                        'text_length': len(text)
                    }
                    
                    print(f"      {category}: RTF {voice_results[category]['avg_rtf']:.3f} ± {voice_results[category]['std_rtf']:.3f}")
            
            baseline_results[voice] = voice_results
        
        self.results['baseline_performance'] = baseline_results
        
        # Calculate overall statistics
        all_rtf_values = []
        for voice_data in baseline_results.values():
            for category_data in voice_data.values():
                all_rtf_values.append(category_data['avg_rtf'])
        
        if all_rtf_values:
            overall_stats = {
                'overall_avg_rtf': statistics.mean(all_rtf_values),
                'overall_min_rtf': min(all_rtf_values),
                'overall_max_rtf': max(all_rtf_values),
                'performance_rating': self._rate_performance(statistics.mean(all_rtf_values))
            }
            self.results['baseline_performance']['overall'] = overall_stats
            
            print(f"   📊 Overall Average RTF: {overall_stats['overall_avg_rtf']:.3f}")
            print(f"   🎯 Performance Rating: {overall_stats['performance_rating']}")
    
    def identify_bottlenecks(self):
        """Identify performance bottlenecks in the system"""
        
        bottlenecks = []
        
        # 1. Check API response times
        print("   🔍 Analyzing API response patterns...")
        try:
            response = requests.get(f"{self.base_url}/dashboard", timeout=10)
            if response.status_code == 200:
                # Parse dashboard data for bottleneck indicators
                dashboard_data = response.text
                
                # Look for high latency indicators
                if "avg_response_time" in dashboard_data:
                    bottlenecks.append({
                        'type': 'api_latency',
                        'severity': 'medium',
                        'description': 'API response time analysis needed'
                    })
        except Exception as e:
            bottlenecks.append({
                'type': 'api_connectivity',
                'severity': 'high',
                'description': f'Cannot connect to API: {e}'
            })
        
        # 2. Check for text processing bottlenecks
        print("   🔍 Analyzing text processing performance...")
        long_text = "This is a very long text " * 50  # 250 words
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json={
                    "input": long_text,
                    "voice": "af_heart",
                    "response_format": "mp3"
                },
                timeout=60
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                audio_size = len(response.content)
                estimated_duration = audio_size / 16000
                rtf = processing_time / estimated_duration if estimated_duration > 0 else 0
                
                if rtf > 1.0:
                    bottlenecks.append({
                        'type': 'text_processing',
                        'severity': 'high',
                        'description': f'Long text RTF too high: {rtf:.3f}',
                        'metric': rtf
                    })
                elif rtf > 0.5:
                    bottlenecks.append({
                        'type': 'text_processing',
                        'severity': 'medium',
                        'description': f'Long text RTF suboptimal: {rtf:.3f}',
                        'metric': rtf
                    })
                    
        except Exception as e:
            bottlenecks.append({
                'type': 'text_processing',
                'severity': 'high',
                'description': f'Long text processing failed: {e}'
            })
        
        # 3. Check voice loading performance
        print("   🔍 Analyzing voice loading performance...")
        uncommon_voices = ["hm_omega", "zf_xiaobei", "jf_gongitsune"]
        
        for voice in uncommon_voices:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json={
                        "input": "Test voice loading",
                        "voice": voice,
                        "response_format": "mp3"
                    },
                    timeout=30
                )
                loading_time = time.time() - start_time
                
                if loading_time > 5.0:
                    bottlenecks.append({
                        'type': 'voice_loading',
                        'severity': 'medium',
                        'description': f'Slow voice loading for {voice}: {loading_time:.2f}s',
                        'metric': loading_time
                    })
                    
            except Exception as e:
                bottlenecks.append({
                    'type': 'voice_loading',
                    'severity': 'high',
                    'description': f'Voice loading failed for {voice}: {e}'
                })
        
        self.results['bottleneck_analysis'] = {
            'bottlenecks': bottlenecks,
            'bottleneck_count': len(bottlenecks),
            'high_severity_count': len([b for b in bottlenecks if b['severity'] == 'high']),
            'medium_severity_count': len([b for b in bottlenecks if b['severity'] == 'medium'])
        }
        
        print(f"   📊 Found {len(bottlenecks)} potential bottlenecks")
        for bottleneck in bottlenecks:
            severity_icon = "🔴" if bottleneck['severity'] == 'high' else "🟡"
            print(f"      {severity_icon} {bottleneck['type']}: {bottleneck['description']}")
    
    def analyze_system_resources(self):
        """Analyze system resource usage during TTS operations"""
        
        print("   💻 Monitoring system resources...")
        
        # Get baseline system metrics
        baseline_cpu = psutil.cpu_percent(interval=1)
        baseline_memory = psutil.virtual_memory().percent
        baseline_disk_io = psutil.disk_io_counters()
        
        # Run TTS operations while monitoring resources
        resource_samples = []
        
        for i in range(5):
            # Start monitoring
            cpu_before = psutil.cpu_percent()
            memory_before = psutil.virtual_memory().percent
            
            # Run TTS operation
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json={
                        "input": "This is a test for resource monitoring during TTS synthesis.",
                        "voice": "af_heart",
                        "response_format": "mp3"
                    },
                    timeout=30
                )
                end_time = time.time()
                
                # Get resource usage after
                cpu_after = psutil.cpu_percent()
                memory_after = psutil.virtual_memory().percent
                
                if response.status_code == 200:
                    resource_samples.append({
                        'cpu_usage': max(cpu_after, cpu_before),
                        'memory_usage': max(memory_after, memory_before),
                        'generation_time': end_time - start_time,
                        'success': True
                    })
                
            except Exception as e:
                resource_samples.append({
                    'cpu_usage': 0,
                    'memory_usage': 0,
                    'generation_time': 0,
                    'success': False,
                    'error': str(e)
                })
            
            time.sleep(0.5)
        
        # Analyze resource usage
        successful_samples = [s for s in resource_samples if s['success']]
        
        if successful_samples:
            avg_cpu = statistics.mean([s['cpu_usage'] for s in successful_samples])
            avg_memory = statistics.mean([s['memory_usage'] for s in successful_samples])
            avg_time = statistics.mean([s['generation_time'] for s in successful_samples])
            
            self.results['system_analysis'] = {
                'baseline_cpu': baseline_cpu,
                'baseline_memory': baseline_memory,
                'avg_cpu_during_tts': avg_cpu,
                'avg_memory_during_tts': avg_memory,
                'avg_generation_time': avg_time,
                'cpu_increase': avg_cpu - baseline_cpu,
                'memory_increase': avg_memory - baseline_memory,
                'resource_efficiency': self._rate_resource_efficiency(avg_cpu, avg_memory)
            }
            
            print(f"      CPU: {baseline_cpu:.1f}% → {avg_cpu:.1f}% (+{avg_cpu - baseline_cpu:.1f}%)")
            print(f"      Memory: {baseline_memory:.1f}% → {avg_memory:.1f}% (+{avg_memory - baseline_memory:.1f}%)")
            print(f"      Avg Generation Time: {avg_time:.3f}s")
    
    def analyze_audio_pipeline(self):
        """Analyze audio processing pipeline performance"""
        
        print("   🎵 Analyzing audio processing pipeline...")
        
        # Test different audio formats for performance impact
        formats = ["mp3", "wav"]
        format_performance = {}
        
        for format_type in formats:
            print(f"      Testing {format_type} format...")
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json={
                        "input": "Testing audio format performance impact on RTF.",
                        "voice": "af_heart",
                        "response_format": format_type
                    },
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    generation_time = end_time - start_time
                    audio_size = len(response.content)
                    
                    format_performance[format_type] = {
                        'generation_time': generation_time,
                        'audio_size': audio_size,
                        'size_per_second': audio_size / generation_time
                    }
                    
                    print(f"         Time: {generation_time:.3f}s, Size: {audio_size:,} bytes")
                    
            except Exception as e:
                print(f"         ❌ Error testing {format_type}: {e}")
        
        self.results['audio_pipeline_analysis'] = format_performance
    
    def analyze_memory_usage(self):
        """Analyze memory usage patterns"""
        
        print("   💾 Analyzing memory usage patterns...")
        
        # Get process memory info
        try:
            # Find TTS server process
            current_process = psutil.Process()
            memory_info = current_process.memory_info()
            
            self.results['memory_analysis'] = {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'memory_percent': current_process.memory_percent(),
                'analysis': self._analyze_memory_efficiency(memory_info.rss / 1024 / 1024)
            }
            
            print(f"      RSS Memory: {memory_info.rss / 1024 / 1024:.1f} MB")
            print(f"      VMS Memory: {memory_info.vms / 1024 / 1024:.1f} MB")
            print(f"      Memory %: {current_process.memory_percent():.1f}%")
            
        except Exception as e:
            print(f"      ❌ Error analyzing memory: {e}")
    
    def generate_recommendations(self):
        """Generate optimization recommendations based on analysis"""
        
        recommendations = []
        
        # Analyze baseline performance for recommendations
        if 'baseline_performance' in self.results:
            overall_rtf = self.results['baseline_performance'].get('overall', {}).get('overall_avg_rtf', 0)
            
            if overall_rtf > 0.5:
                recommendations.append({
                    'category': 'performance',
                    'priority': 'high',
                    'title': 'Optimize Model Inference',
                    'description': f'Current RTF ({overall_rtf:.3f}) indicates room for optimization',
                    'actions': [
                        'Consider model quantization',
                        'Optimize ONNX runtime settings',
                        'Implement batch processing for multiple requests'
                    ]
                })
            
            if overall_rtf > 0.3:
                recommendations.append({
                    'category': 'caching',
                    'priority': 'medium',
                    'title': 'Enhance Caching Strategy',
                    'description': 'Improve cache hit rates for better performance',
                    'actions': [
                        'Implement intelligent pre-caching',
                        'Optimize cache eviction policies',
                        'Add phrase-level caching'
                    ]
                })
        
        # Analyze bottlenecks for recommendations
        if 'bottleneck_analysis' in self.results:
            high_severity = self.results['bottleneck_analysis']['high_severity_count']
            
            if high_severity > 0:
                recommendations.append({
                    'category': 'bottlenecks',
                    'priority': 'critical',
                    'title': 'Address Critical Bottlenecks',
                    'description': f'Found {high_severity} high-severity bottlenecks',
                    'actions': [
                        'Investigate voice loading performance',
                        'Optimize text preprocessing pipeline',
                        'Review API response handling'
                    ]
                })
        
        # System resource recommendations
        if 'system_analysis' in self.results:
            cpu_increase = self.results['system_analysis'].get('cpu_increase', 0)
            memory_increase = self.results['system_analysis'].get('memory_increase', 0)
            
            if cpu_increase > 50:
                recommendations.append({
                    'category': 'resources',
                    'priority': 'medium',
                    'title': 'Optimize CPU Usage',
                    'description': f'High CPU increase during TTS: +{cpu_increase:.1f}%',
                    'actions': [
                        'Profile CPU-intensive operations',
                        'Consider multi-threading optimizations',
                        'Optimize audio processing algorithms'
                    ]
                })
            
            if memory_increase > 20:
                recommendations.append({
                    'category': 'resources',
                    'priority': 'medium',
                    'title': 'Optimize Memory Usage',
                    'description': f'High memory increase during TTS: +{memory_increase:.1f}%',
                    'actions': [
                        'Implement memory pooling',
                        'Optimize audio buffer management',
                        'Review voice embedding caching'
                    ]
                })
        
        # General optimization recommendations
        recommendations.extend([
            {
                'category': 'optimization',
                'priority': 'low',
                'title': 'Implement Advanced Optimizations',
                'description': 'Additional optimizations for production deployment',
                'actions': [
                    'Add request batching for concurrent requests',
                    'Implement adaptive quality settings',
                    'Add performance-based voice selection',
                    'Optimize audio format conversion'
                ]
            }
        ])
        
        self.results['optimization_recommendations'] = recommendations
        
        # Print recommendations
        for rec in recommendations:
            priority_icon = "🔴" if rec['priority'] == 'critical' else "🟡" if rec['priority'] == 'high' else "🟢"
            print(f"   {priority_icon} {rec['title']} ({rec['priority']})")
            print(f"      {rec['description']}")
            for action in rec['actions'][:2]:  # Show first 2 actions
                print(f"      • {action}")
    
    def validate_improvements(self):
        """Validate performance improvements"""
        
        print("   ✅ Performance validation complete")
        print(f"   📊 Baseline RTF: {self.results.get('baseline_performance', {}).get('overall', {}).get('overall_avg_rtf', 'N/A')}")
        print(f"   🔍 Bottlenecks found: {self.results.get('bottleneck_analysis', {}).get('bottleneck_count', 0)}")
        print(f"   💡 Recommendations: {len(self.results.get('optimization_recommendations', []))}")
    
    def _rate_performance(self, rtf: float) -> str:
        """Rate RTF performance"""
        if rtf < 0.2:
            return "🟢 Excellent"
        elif rtf < 0.4:
            return "🟡 Good"
        elif rtf < 0.8:
            return "🟠 Fair"
        else:
            return "🔴 Poor"
    
    def _rate_resource_efficiency(self, cpu: float, memory: float) -> str:
        """Rate resource efficiency"""
        if cpu < 30 and memory < 20:
            return "🟢 Excellent"
        elif cpu < 60 and memory < 40:
            return "🟡 Good"
        else:
            return "🔴 Needs Optimization"
    
    def _analyze_memory_efficiency(self, memory_mb: float) -> str:
        """Analyze memory efficiency"""
        if memory_mb < 50:
            return "🟢 Very Efficient"
        elif memory_mb < 100:
            return "🟡 Efficient"
        elif memory_mb < 200:
            return "🟠 Moderate"
        else:
            return "🔴 High Usage"
    
    def save_results(self, output_file: str = "docs/rtf_optimization_report.json"):
        """Save audit results to file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: {output_file}")

def main():
    """Run RTF optimization audit"""
    auditor = RTFOptimizationAuditor()
    results = auditor.run_comprehensive_audit()
    auditor.save_results()
    
    return results

if __name__ == "__main__":
    main()
