#!/usr/bin/env python3
"""
Code Audit for RTF Optimization

Comprehensive code audit to identify performance bottlenecks and optimization
opportunities in the TTS codebase.
"""

import os
import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import time

class CodeAuditor:
    """Comprehensive code auditor for RTF optimization"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.audit_results = {
            'performance_issues': [],
            'optimization_opportunities': [],
            'code_quality_metrics': {},
            'bottleneck_analysis': {},
            'recommendations': []
        }
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive code audit"""
        
        print("🔍 RTF Code Audit & Analysis")
        print("=" * 40)
        
        # 1. Analyze Python files for performance issues
        print("\n📝 1. Analyzing Python Code Performance")
        self.analyze_python_performance()
        
        # 2. Check for common performance anti-patterns
        print("\n⚠️ 2. Checking Performance Anti-patterns")
        self.check_performance_antipatterns()
        
        # 3. Analyze import dependencies
        print("\n📦 3. Analyzing Import Dependencies")
        self.analyze_import_dependencies()
        
        # 4. Check for blocking operations
        print("\n🚫 4. Checking for Blocking Operations")
        self.check_blocking_operations()
        
        # 5. Analyze memory usage patterns
        print("\n💾 5. Analyzing Memory Usage Patterns")
        self.analyze_memory_patterns()
        
        # 6. Generate optimization recommendations
        print("\n💡 6. Generating Optimization Recommendations")
        self.generate_optimization_recommendations()
        
        return self.audit_results
    
    def analyze_python_performance(self):
        """Analyze Python files for performance issues"""
        
        python_files = list(self.project_root.rglob("*.py"))
        performance_issues = []
        
        for file_path in python_files:
            if "test" in str(file_path) or "__pycache__" in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST for analysis
                tree = ast.parse(content)
                
                # Check for performance issues
                issues = self._analyze_ast_performance(tree, file_path)
                performance_issues.extend(issues)
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {file_path}: {e}")
        
        self.audit_results['performance_issues'] = performance_issues
        print(f"   📊 Found {len(performance_issues)} potential performance issues")
    
    def _analyze_ast_performance(self, tree: ast.AST, file_path: Path) -> List[Dict]:
        """Analyze AST for performance issues"""
        issues = []
        
        class PerformanceVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # Check for nested loops
                for child in ast.walk(node):
                    if isinstance(child, ast.For) and child != node:
                        issues.append({
                            'type': 'nested_loops',
                            'file': str(file_path),
                            'line': node.lineno,
                            'severity': 'medium',
                            'description': 'Nested loops detected - potential O(n²) complexity'
                        })
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # Check for expensive function calls
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['sleep', 'time', 'wait']:
                        issues.append({
                            'type': 'blocking_call',
                            'file': str(file_path),
                            'line': node.lineno,
                            'severity': 'high',
                            'description': f'Blocking call detected: {node.func.attr}'
                        })
                    
                    if node.func.attr in ['append'] and len(node.args) == 1:
                        # Check if in a loop (simplified check)
                        issues.append({
                            'type': 'list_append_in_loop',
                            'file': str(file_path),
                            'line': node.lineno,
                            'severity': 'low',
                            'description': 'List append in potential loop - consider list comprehension'
                        })
                
                self.generic_visit(node)
            
            def visit_ListComp(self, node):
                # Check for complex list comprehensions
                if len(node.generators) > 1:
                    issues.append({
                        'type': 'complex_comprehension',
                        'file': str(file_path),
                        'line': node.lineno,
                        'severity': 'low',
                        'description': 'Complex list comprehension - consider breaking down'
                    })
                self.generic_visit(node)
        
        visitor = PerformanceVisitor()
        visitor.visit(tree)
        
        return issues
    
    def check_performance_antipatterns(self):
        """Check for common performance anti-patterns"""
        
        antipatterns = []
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            if "test" in str(file_path) or "__pycache__" in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for specific anti-patterns
                patterns = [
                    (r'\.join\(\[.*for.*in.*\]\)', 'string_join_comprehension', 'Use generator expression instead of list comprehension with join()'),
                    (r'len\(.*\)\s*==\s*0', 'len_zero_check', 'Use "not sequence" instead of "len(sequence) == 0"'),
                    (r'range\(len\(.*\)\)', 'range_len_pattern', 'Use enumerate() instead of range(len())'),
                    (r'\.keys\(\)\s*in\s', 'dict_keys_in', 'Check key directly instead of using .keys()'),
                    (r'import\s+\*', 'wildcard_import', 'Avoid wildcard imports for better performance'),
                ]
                
                for pattern, issue_type, description in patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        antipatterns.append({
                            'type': issue_type,
                            'file': str(file_path),
                            'line': line_num,
                            'severity': 'medium',
                            'description': description,
                            'pattern': match.group()
                        })
                
            except Exception as e:
                print(f"   ⚠️ Error checking {file_path}: {e}")
        
        self.audit_results['performance_issues'].extend(antipatterns)
        print(f"   📊 Found {len(antipatterns)} performance anti-patterns")
    
    def analyze_import_dependencies(self):
        """Analyze import dependencies for optimization"""
        
        import_analysis = {
            'heavy_imports': [],
            'unused_imports': [],
            'circular_imports': [],
            'optimization_opportunities': []
        }
        
        python_files = list(self.project_root.rglob("*.py"))
        
        # Heavy imports that might affect startup time
        heavy_modules = ['torch', 'tensorflow', 'numpy', 'scipy', 'pandas', 'matplotlib']
        
        for file_path in python_files:
            if "test" in str(file_path) or "__pycache__" in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for heavy imports
                for module in heavy_modules:
                    if re.search(rf'import\s+{module}|from\s+{module}', content):
                        import_analysis['heavy_imports'].append({
                            'file': str(file_path),
                            'module': module,
                            'suggestion': f'Consider lazy loading {module} if not always needed'
                        })
                
                # Check for potential lazy loading opportunities
                if 'import torch' in content and 'def ' in content:
                    import_analysis['optimization_opportunities'].append({
                        'file': str(file_path),
                        'type': 'lazy_loading',
                        'description': 'Consider lazy loading torch inside functions if not used at module level'
                    })
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing imports in {file_path}: {e}")
        
        self.audit_results['import_analysis'] = import_analysis
        print(f"   📊 Found {len(import_analysis['heavy_imports'])} heavy imports")
    
    def check_blocking_operations(self):
        """Check for blocking operations that could affect RTF"""
        
        blocking_ops = []
        python_files = list(self.project_root.rglob("*.py"))
        
        # Patterns that indicate blocking operations
        blocking_patterns = [
            (r'time\.sleep\(', 'sleep_call', 'Sleep call blocks execution'),
            (r'requests\.get\(', 'sync_http', 'Synchronous HTTP request'),
            (r'requests\.post\(', 'sync_http', 'Synchronous HTTP request'),
            (r'open\(.*\)\.read\(\)', 'sync_file_read', 'Synchronous file read'),
            (r'subprocess\.run\(', 'subprocess_run', 'Synchronous subprocess call'),
            (r'\.join\(\)', 'thread_join', 'Thread join operation'),
        ]
        
        for file_path in python_files:
            if "test" in str(file_path) or "__pycache__" in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern, op_type, description in blocking_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        blocking_ops.append({
                            'type': op_type,
                            'file': str(file_path),
                            'line': line_num,
                            'severity': 'high' if op_type in ['sleep_call', 'sync_http'] else 'medium',
                            'description': description,
                            'pattern': match.group()
                        })
                
            except Exception as e:
                print(f"   ⚠️ Error checking {file_path}: {e}")
        
        self.audit_results['blocking_operations'] = blocking_ops
        print(f"   📊 Found {len(blocking_ops)} potential blocking operations")
    
    def analyze_memory_patterns(self):
        """Analyze memory usage patterns"""
        
        memory_issues = []
        python_files = list(self.project_root.rglob("*.py"))
        
        # Memory-related patterns
        memory_patterns = [
            (r'\[\].*for.*in.*range\(.*\)', 'large_list_creation', 'Large list creation - consider generators'),
            (r'\.copy\(\)', 'object_copy', 'Object copying - ensure necessary'),
            (r'pickle\.loads?\(', 'pickle_usage', 'Pickle usage - consider alternatives for performance'),
            (r'json\.loads?\(.*\)', 'json_parsing', 'JSON parsing - consider streaming for large data'),
        ]
        
        for file_path in python_files:
            if "test" in str(file_path) or "__pycache__" in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern, issue_type, description in memory_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        memory_issues.append({
                            'type': issue_type,
                            'file': str(file_path),
                            'line': line_num,
                            'severity': 'medium',
                            'description': description,
                            'pattern': match.group()
                        })
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {file_path}: {e}")
        
        self.audit_results['memory_patterns'] = memory_issues
        print(f"   📊 Found {len(memory_issues)} memory-related patterns")
    
    def generate_optimization_recommendations(self):
        """Generate optimization recommendations based on audit"""
        
        recommendations = []
        
        # Analyze all issues to generate recommendations
        all_issues = (
            self.audit_results.get('performance_issues', []) +
            self.audit_results.get('blocking_operations', []) +
            self.audit_results.get('memory_patterns', [])
        )
        
        # Count issue types
        issue_counts = {}
        for issue in all_issues:
            issue_type = issue['type']
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Generate recommendations based on most common issues
        if issue_counts.get('blocking_call', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'blocking_operations',
                'title': 'Eliminate Blocking Operations',
                'description': f'Found {issue_counts["blocking_call"]} blocking calls that could impact RTF',
                'actions': [
                    'Replace synchronous calls with asynchronous alternatives',
                    'Use threading for I/O operations',
                    'Implement non-blocking audio processing'
                ]
            })
        
        if issue_counts.get('nested_loops', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'algorithmic',
                'title': 'Optimize Nested Loops',
                'description': f'Found {issue_counts["nested_loops"]} nested loops with potential O(n²) complexity',
                'actions': [
                    'Consider using hash tables for lookups',
                    'Implement early termination conditions',
                    'Use vectorized operations where possible'
                ]
            })
        
        if len(self.audit_results.get('import_analysis', {}).get('heavy_imports', [])) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'imports',
                'title': 'Optimize Import Strategy',
                'description': 'Heavy imports detected that may affect startup time',
                'actions': [
                    'Implement lazy loading for heavy modules',
                    'Move imports inside functions where appropriate',
                    'Consider using importlib for dynamic imports'
                ]
            })
        
        # General recommendations
        recommendations.extend([
            {
                'priority': 'low',
                'category': 'general',
                'title': 'Code Quality Improvements',
                'description': 'General code quality improvements for better performance',
                'actions': [
                    'Use list comprehensions instead of loops where appropriate',
                    'Implement proper error handling to avoid exceptions',
                    'Add type hints for better optimization',
                    'Use __slots__ for frequently instantiated classes'
                ]
            }
        ])
        
        self.audit_results['recommendations'] = recommendations
        
        # Print summary
        for rec in recommendations:
            priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
            print(f"   {priority_icon} {rec['title']} ({rec['priority']})")
    
    def save_audit_report(self, output_file: str = "docs/code_audit_rtf_report.json"):
        """Save audit results to file"""
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Add summary statistics
        self.audit_results['summary'] = {
            'total_issues': len(self.audit_results.get('performance_issues', [])),
            'blocking_operations': len(self.audit_results.get('blocking_operations', [])),
            'memory_patterns': len(self.audit_results.get('memory_patterns', [])),
            'recommendations': len(self.audit_results.get('recommendations', [])),
            'audit_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(output_file, 'w') as f:
            json.dump(self.audit_results, f, indent=2, default=str)
        
        print(f"\n📄 Audit report saved: {output_file}")

def main():
    """Run code audit for RTF optimization"""
    auditor = CodeAuditor()
    results = auditor.run_comprehensive_audit()
    auditor.save_audit_report()
    
    # Print summary
    print(f"\n📊 AUDIT SUMMARY")
    print(f"=" * 20)
    print(f"Performance Issues: {len(results.get('performance_issues', []))}")
    print(f"Blocking Operations: {len(results.get('blocking_operations', []))}")
    print(f"Memory Patterns: {len(results.get('memory_patterns', []))}")
    print(f"Recommendations: {len(results.get('recommendations', []))}")
    
    return results

if __name__ == "__main__":
    main()
