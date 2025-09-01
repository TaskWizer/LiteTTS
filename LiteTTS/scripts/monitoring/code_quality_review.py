#!/usr/bin/env python3
"""
Code Quality Review and Analysis Script
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import defaultdict

class CodeQualityAnalyzer:
    """Analyze code quality across the codebase"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Analyze various aspects
            file_issues = {
                'unused_imports': self._find_unused_imports(content, tree),
                'long_functions': self._find_long_functions(tree),
                'missing_docstrings': self._find_missing_docstrings(tree),
                'complex_functions': self._find_complex_functions(tree),
                'duplicate_code': self._find_potential_duplicates(content),
                'naming_issues': self._find_naming_issues(tree),
                'magic_numbers': self._find_magic_numbers(tree),
            }
            
            return file_issues
            
        except Exception as e:
            return {'error': str(e)}
    
    def _find_unused_imports(self, content: str, tree: ast.AST) -> List[str]:
        """Find potentially unused imports"""
        imports = []
        used_names = set()
        
        # Collect imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.Name):
                used_names.add(node.id)
        
        # Simple heuristic - check if import name appears in content
        unused = []
        for imp in imports:
            if imp not in content.replace(f"import {imp}", ""):
                unused.append(imp)
        
        return unused
    
    def _find_long_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Find functions that are too long"""
        long_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Count lines in function
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    length = node.end_lineno - node.lineno
                    if length > 50:  # Threshold for long functions
                        long_functions.append({
                            'name': node.name,
                            'lines': length,
                            'line_number': node.lineno
                        })
        
        return long_functions
    
    def _find_missing_docstrings(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Find functions/classes without docstrings"""
        missing = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Check if first statement is a docstring
                has_docstring = (
                    node.body and
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)
                )
                
                if not has_docstring and not node.name.startswith('_'):
                    missing.append({
                        'type': type(node).__name__,
                        'name': node.name,
                        'line_number': node.lineno
                    })
        
        return missing
    
    def _find_complex_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Find functions with high cyclomatic complexity"""
        complex_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_complexity(node)
                if complexity > 10:  # Threshold for complex functions
                    complex_functions.append({
                        'name': node.name,
                        'complexity': complexity,
                        'line_number': node.lineno
                    })
        
        return complex_functions
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _find_potential_duplicates(self, content: str) -> List[str]:
        """Find potential code duplicates (simple heuristic)"""
        lines = content.split('\n')
        duplicates = []
        
        # Look for repeated lines (excluding empty lines and comments)
        line_counts = defaultdict(list)
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and len(stripped) > 20:
                line_counts[stripped].append(i + 1)
        
        for line, occurrences in line_counts.items():
            if len(occurrences) > 1:
                duplicates.append(f"Line repeated {len(occurrences)} times: {line[:50]}...")
        
        return duplicates
    
    def _find_naming_issues(self, tree: ast.AST) -> List[str]:
        """Find naming convention issues"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    issues.append(f"Function '{node.name}' doesn't follow snake_case")
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    issues.append(f"Class '{node.name}' doesn't follow PascalCase")
        
        return issues
    
    def _find_magic_numbers(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Find magic numbers in code"""
        magic_numbers = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # Skip common acceptable numbers
                if node.value not in [0, 1, -1, 2, 10, 100, 1000]:
                    magic_numbers.append({
                        'value': node.value,
                        'line_number': getattr(node, 'lineno', 'unknown')
                    })
        
        return magic_numbers
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the entire codebase"""
        print("🔍 Analyzing Code Quality")
        print("=" * 50)
        
        python_files = list(self.root_dir.rglob("*.py"))
        
        # Filter out __pycache__ and other irrelevant files
        python_files = [
            f for f in python_files 
            if '__pycache__' not in str(f) and 'venv' not in str(f)
        ]
        
        total_issues = defaultdict(int)
        file_results = {}
        
        for file_path in python_files:
            relative_path = file_path.relative_to(self.root_dir)
            print(f"   📄 Analyzing {relative_path}")
            
            file_issues = self.analyze_file(file_path)
            file_results[str(relative_path)] = file_issues
            
            # Count issues
            for issue_type, issues in file_issues.items():
                if isinstance(issues, list):
                    total_issues[issue_type] += len(issues)
        
        return {
            'total_files': len(python_files),
            'total_issues': dict(total_issues),
            'file_results': file_results
        }

def check_project_structure():
    """Check project structure and organization"""
    print("\n📁 Checking Project Structure")
    print("-" * 40)
    
    expected_structure = {
        'app.py': 'Main application file',
        'LiteTTS/': 'Main package directory',
        'LiteTTS/__init__.py': 'Package initialization',
        'LiteTTS/config.py': 'Configuration management',
        'LiteTTS/models.py': 'Data models',
        'tests/': 'Test directory',
        'docs/': 'Documentation directory',
        'REQUIREMENTS.txt': 'Dependencies',
        'pyproject.toml': 'Project configuration',
        'README.md': 'Project documentation'
    }
    
    missing_files = []
    present_files = []
    
    for file_path, description in expected_structure.items():
        if Path(file_path).exists():
            present_files.append(f"✅ {file_path} - {description}")
        else:
            missing_files.append(f"❌ {file_path} - {description}")
    
    print("   Present files:")
    for file_info in present_files:
        print(f"      {file_info}")
    
    if missing_files:
        print("\n   Missing files:")
        for file_info in missing_files:
            print(f"      {file_info}")
    
    return len(missing_files) == 0

def check_documentation_quality():
    """Check documentation quality"""
    print("\n📚 Checking Documentation Quality")
    print("-" * 40)
    
    doc_files = list(Path('.').rglob("*.md"))
    
    doc_quality = {
        'total_docs': len(doc_files),
        'readme_exists': Path('README.md').exists(),
        'docs_dir_exists': Path('docs').exists(),
        'api_docs_exist': any('api' in str(f).lower() for f in doc_files)
    }
    
    print(f"   📊 Total documentation files: {doc_quality['total_docs']}")
    print(f"   📋 README.md exists: {'✅' if doc_quality['readme_exists'] else '❌'}")
    print(f"   📁 docs/ directory exists: {'✅' if doc_quality['docs_dir_exists'] else '❌'}")
    print(f"   🔌 API documentation exists: {'✅' if doc_quality['api_docs_exist'] else '❌'}")
    
    return doc_quality

def main():
    """Main analysis function"""
    print("🚀 Starting Code Quality Review")
    print("=" * 50)
    
    # Analyze code quality
    analyzer = CodeQualityAnalyzer()
    results = analyzer.analyze_codebase()
    
    print(f"\n📊 Analysis Results:")
    print(f"   Total files analyzed: {results['total_files']}")
    
    for issue_type, count in results['total_issues'].items():
        if count > 0:
            print(f"   {issue_type}: {count}")
    
    # Check project structure
    structure_ok = check_project_structure()
    
    # Check documentation
    doc_quality = check_documentation_quality()
    
    print("\n" + "=" * 50)
    print("📋 Quality Summary:")
    print(f"   Project structure: {'✅ Good' if structure_ok else '⚠️ Issues found'}")
    print(f"   Documentation: {'✅ Good' if doc_quality['readme_exists'] else '⚠️ Needs improvement'}")
    
    # Overall assessment
    total_critical_issues = (
        results['total_issues'].get('missing_docstrings', 0) +
        results['total_issues'].get('complex_functions', 0) +
        results['total_issues'].get('long_functions', 0)
    )
    
    if total_critical_issues < 10:
        print("   Overall code quality: ✅ Good")
    elif total_critical_issues < 25:
        print("   Overall code quality: ⚠️ Acceptable")
    else:
        print("   Overall code quality: ❌ Needs improvement")
    
    print("\n💡 Recommendations:")
    print("   - Add docstrings to public functions and classes")
    print("   - Break down complex functions into smaller ones")
    print("   - Consider extracting magic numbers to constants")
    print("   - Review and remove unused imports")
    print("   - Ensure consistent naming conventions")

if __name__ == "__main__":
    main()
