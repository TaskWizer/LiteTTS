#!/usr/bin/env python3
"""
Focused RTF Audit for Kokoro Codebase

Focused audit specifically on the LiteTTS/ directory for RTF optimization
opportunities, excluding dependencies and virtual environments.
"""

import os
import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Any
import time

class FocusedRTFAuditor:
    """Focused RTF auditor for kokoro codebase only"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.kokoro_path = self.project_root / "kokoro"
        self.audit_results = {
            'performance_issues': [],
            'optimization_opportunities': [],
            'rtf_specific_findings': [],
            'recommendations': []
        }
    
    def run_focused_audit(self) -> Dict[str, Any]:
        """Run focused audit on kokoro codebase"""
        
        print("🎯 Focused RTF Audit - Kokoro Codebase")
        print("=" * 45)
        
        if not self.kokoro_path.exists():
            print("❌ Kokoro directory not found")
            return self.audit_results
        
        # 1. Analyze TTS synthesis pipeline
        print("\n🎵 1. Analyzing TTS Synthesis Pipeline")
        self.analyze_tts_pipeline()
        
        # 2. Check audio processing performance
        print("\n🔊 2. Checking Audio Processing Performance")
        self.analyze_audio_processing()
        
        # 3. Analyze caching effectiveness
        print("\n💾 3. Analyzing Caching Effectiveness")
        self.analyze_caching_patterns()
        
        # 4. Check for RTF-specific bottlenecks
        print("\n⚡ 4. Checking RTF-Specific Bottlenecks")
        self.check_rtf_bottlenecks()
        
        # 5. Analyze model loading and inference
        print("\n🧠 5. Analyzing Model Loading & Inference")
        self.analyze_model_performance()
        
        # 6. Generate focused recommendations
        print("\n💡 6. Generating Focused Recommendations")
        self.generate_focused_recommendations()
        
        return self.audit_results
    
    def analyze_tts_pipeline(self):
        """Analyze TTS synthesis pipeline for performance"""
        
        # Key files to analyze
        key_files = [
            "tts/synthesizer.py",
            "tts/engine.py", 
            "tts/chunk_processor.py",
            "api/router.py"
        ]
        
        pipeline_issues = []
        
        for file_name in key_files:
            file_path = self.kokoro_path / file_name
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for synchronous operations in main pipeline
                sync_patterns = [
                    (r'time\.sleep\(', 'sleep_in_pipeline', 'Sleep call in TTS pipeline'),
                    (r'\.wait\(\)', 'wait_in_pipeline', 'Wait call in TTS pipeline'),
                    (r'requests\.(?:get|post)\(', 'sync_http_in_pipeline', 'Synchronous HTTP in pipeline'),
                    (r'for\s+.*\s+in\s+.*:\s*\n\s*.*\.append\(', 'loop_append', 'Loop with append - consider list comprehension'),
                ]
                
                for pattern, issue_type, description in sync_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        pipeline_issues.append({
                            'type': issue_type,
                            'file': str(file_path),
                            'line': line_num,
                            'severity': 'high',
                            'description': description,
                            'context': 'tts_pipeline'
                        })
                
                # Check for inefficient string operations
                if 'text' in content.lower():
                    string_patterns = [
                        (r'\+\s*=.*str\(', 'string_concatenation', 'String concatenation in loop'),
                        (r'\.replace\(.*\.replace\(', 'chained_replace', 'Chained string replacements'),
                    ]
                    
                    for pattern, issue_type, description in string_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            pipeline_issues.append({
                                'type': issue_type,
                                'file': str(file_path),
                                'line': line_num,
                                'severity': 'medium',
                                'description': description,
                                'context': 'text_processing'
                            })
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {file_path}: {e}")
        
        self.audit_results['performance_issues'].extend(pipeline_issues)
        print(f"   📊 Found {len(pipeline_issues)} pipeline performance issues")
    
    def analyze_audio_processing(self):
        """Analyze audio processing for RTF optimization"""
        
        audio_files = list(self.kokoro_path.glob("audio/*.py"))
        audio_issues = []
        
        for file_path in audio_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for audio processing inefficiencies
                audio_patterns = [
                    (r'numpy\.array\(.*\)\.copy\(\)', 'unnecessary_copy', 'Unnecessary array copy'),
                    (r'for\s+i\s+in\s+range\(len\(.*\)\):', 'range_len_audio', 'Use enumerate or vectorized operations'),
                    (r'\.astype\(.*\)\.astype\(', 'double_conversion', 'Double type conversion'),
                    (r'np\.concatenate\(\[.*\]\)', 'list_concatenate', 'Consider using np.hstack or np.vstack'),
                ]
                
                for pattern, issue_type, description in audio_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        audio_issues.append({
                            'type': issue_type,
                            'file': str(file_path),
                            'line': line_num,
                            'severity': 'medium',
                            'description': description,
                            'context': 'audio_processing'
                        })
                
                # Check for potential memory leaks in audio processing
                if 'audio_data' in content and 'del ' not in content:
                    audio_issues.append({
                        'type': 'potential_memory_leak',
                        'file': str(file_path),
                        'line': 0,
                        'severity': 'low',
                        'description': 'Consider explicit memory cleanup for audio data',
                        'context': 'memory_management'
                    })
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {file_path}: {e}")
        
        self.audit_results['performance_issues'].extend(audio_issues)
        print(f"   📊 Found {len(audio_issues)} audio processing issues")
    
    def analyze_caching_patterns(self):
        """Analyze caching effectiveness"""
        
        cache_files = list(self.kokoro_path.glob("cache/*.py"))
        caching_opportunities = []
        
        for file_path in cache_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for caching improvements
                if 'lru_cache' not in content and 'cache' in str(file_path):
                    caching_opportunities.append({
                        'type': 'missing_lru_cache',
                        'file': str(file_path),
                        'severity': 'medium',
                        'description': 'Consider using @lru_cache for frequently called functions',
                        'context': 'caching'
                    })
                
                # Check for cache size optimization
                if 'maxsize=' in content:
                    cache_sizes = re.findall(r'maxsize=(\d+)', content)
                    for size in cache_sizes:
                        if int(size) > 1000:
                            caching_opportunities.append({
                                'type': 'large_cache_size',
                                'file': str(file_path),
                                'severity': 'low',
                                'description': f'Large cache size ({size}) - monitor memory usage',
                                'context': 'cache_tuning'
                            })
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {file_path}: {e}")
        
        self.audit_results['optimization_opportunities'].extend(caching_opportunities)
        print(f"   📊 Found {len(caching_opportunities)} caching opportunities")
    
    def check_rtf_bottlenecks(self):
        """Check for RTF-specific bottlenecks"""
        
        rtf_bottlenecks = []
        
        # Check performance monitoring
        perf_files = list(self.kokoro_path.glob("performance/*.py"))
        
        for file_path in perf_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for RTF calculation efficiency
                if 'rtf' in content.lower():
                    if 'time.time()' in content and content.count('time.time()') > 2:
                        rtf_bottlenecks.append({
                            'type': 'excessive_timing',
                            'file': str(file_path),
                            'severity': 'low',
                            'description': 'Multiple time.time() calls - consider using context manager',
                            'context': 'rtf_measurement'
                        })
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {file_path}: {e}")
        
        # Check main synthesis files for RTF impact
        synthesis_files = [
            self.kokoro_path / "tts" / "synthesizer.py",
            self.kokoro_path / "tts" / "engine.py"
        ]
        
        for file_path in synthesis_files:
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for potential RTF bottlenecks
                if 'phonemizer' in content and 'cache' not in content:
                    rtf_bottlenecks.append({
                        'type': 'uncached_phonemizer',
                        'file': str(file_path),
                        'severity': 'high',
                        'description': 'Phonemizer calls without caching - major RTF impact',
                        'context': 'phonemization'
                    })
                
                if 'model.run' in content or 'onnx' in content:
                    if 'batch' not in content:
                        rtf_bottlenecks.append({
                            'type': 'no_batching',
                            'file': str(file_path),
                            'severity': 'medium',
                            'description': 'Model inference without batching consideration',
                            'context': 'model_inference'
                        })
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {file_path}: {e}")
        
        self.audit_results['rtf_specific_findings'] = rtf_bottlenecks
        print(f"   📊 Found {len(rtf_bottlenecks)} RTF-specific bottlenecks")
    
    def analyze_model_performance(self):
        """Analyze model loading and inference performance"""
        
        model_files = list(self.kokoro_path.glob("models/*.py"))
        model_issues = []
        
        for file_path in model_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for model loading inefficiencies
                if 'onnx' in content:
                    if 'providers=' not in content:
                        model_issues.append({
                            'type': 'missing_providers',
                            'file': str(file_path),
                            'severity': 'medium',
                            'description': 'ONNX model without explicit providers - may not use optimal execution',
                            'context': 'model_optimization'
                        })
                    
                    if 'session_options' not in content:
                        model_issues.append({
                            'type': 'missing_session_options',
                            'file': str(file_path),
                            'severity': 'low',
                            'description': 'Consider setting ONNX session options for performance',
                            'context': 'model_optimization'
                        })
                
                # Check for model caching
                if 'load' in content and 'cache' not in content:
                    model_issues.append({
                        'type': 'uncached_model_loading',
                        'file': str(file_path),
                        'severity': 'high',
                        'description': 'Model loading without caching - impacts RTF',
                        'context': 'model_caching'
                    })
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {file_path}: {e}")
        
        self.audit_results['performance_issues'].extend(model_issues)
        print(f"   📊 Found {len(model_issues)} model performance issues")
    
    def generate_focused_recommendations(self):
        """Generate focused recommendations for RTF optimization"""
        
        recommendations = []
        
        # Analyze findings
        all_issues = (
            self.audit_results.get('performance_issues', []) +
            self.audit_results.get('rtf_specific_findings', [])
        )
        
        # Count by context
        context_counts = {}
        for issue in all_issues:
            context = issue.get('context', 'general')
            context_counts[context] = context_counts.get(context, 0) + 1
        
        # Generate context-specific recommendations
        if context_counts.get('phonemization', 0) > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'phonemization',
                'title': 'Optimize Phonemizer Caching',
                'description': 'Phonemizer operations without caching severely impact RTF',
                'actions': [
                    'Implement aggressive caching for phonemizer results',
                    'Use persistent cache across sessions',
                    'Consider pre-computing common phoneme patterns'
                ],
                'expected_rtf_improvement': '30-50%'
            })
        
        if context_counts.get('model_inference', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'model_optimization',
                'title': 'Optimize Model Inference',
                'description': 'Model inference can be optimized for better RTF',
                'actions': [
                    'Implement request batching for concurrent requests',
                    'Use optimal ONNX execution providers',
                    'Consider model quantization for faster inference'
                ],
                'expected_rtf_improvement': '15-25%'
            })
        
        if context_counts.get('audio_processing', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'audio_optimization',
                'title': 'Optimize Audio Processing',
                'description': 'Audio processing pipeline can be streamlined',
                'actions': [
                    'Use vectorized numpy operations',
                    'Minimize array copying',
                    'Implement efficient audio format conversion'
                ],
                'expected_rtf_improvement': '10-15%'
            })
        
        # General recommendations
        recommendations.append({
            'priority': 'low',
            'category': 'general',
            'title': 'Code Quality & Performance',
            'description': 'General optimizations for better RTF',
            'actions': [
                'Use list comprehensions instead of loops',
                'Implement proper memory management',
                'Add performance profiling hooks',
                'Optimize string operations'
            ],
            'expected_rtf_improvement': '5-10%'
        })
        
        self.audit_results['recommendations'] = recommendations
        
        # Print recommendations
        for rec in recommendations:
            priority_icon = "🔴" if rec['priority'] == 'critical' else "🟡" if rec['priority'] == 'high' else "🟢"
            improvement = rec.get('expected_rtf_improvement', 'N/A')
            print(f"   {priority_icon} {rec['title']} ({rec['priority']}) - RTF: {improvement}")
    
    def save_focused_report(self, output_file: str = "docs/focused_rtf_audit_report.json"):
        """Save focused audit results"""
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Add summary
        self.audit_results['summary'] = {
            'total_performance_issues': len(self.audit_results.get('performance_issues', [])),
            'rtf_specific_findings': len(self.audit_results.get('rtf_specific_findings', [])),
            'optimization_opportunities': len(self.audit_results.get('optimization_opportunities', [])),
            'recommendations': len(self.audit_results.get('recommendations', [])),
            'audit_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'scope': 'kokoro codebase only'
        }
        
        with open(output_file, 'w') as f:
            json.dump(self.audit_results, f, indent=2, default=str)
        
        print(f"\n📄 Focused audit report saved: {output_file}")

def main():
    """Run focused RTF audit"""
    auditor = FocusedRTFAuditor()
    results = auditor.run_focused_audit()
    auditor.save_focused_report()
    
    # Print summary
    print(f"\n📊 FOCUSED AUDIT SUMMARY")
    print(f"=" * 25)
    print(f"Performance Issues: {len(results.get('performance_issues', []))}")
    print(f"RTF-Specific Findings: {len(results.get('rtf_specific_findings', []))}")
    print(f"Optimization Opportunities: {len(results.get('optimization_opportunities', []))}")
    print(f"Recommendations: {len(results.get('recommendations', []))}")
    
    return results

if __name__ == "__main__":
    main()
