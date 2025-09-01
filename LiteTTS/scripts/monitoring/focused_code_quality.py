#!/usr/bin/env python3
"""
Focused Code Quality Assessment for Project Code Only
Reviews only the main project code, excluding dependencies and vendor code
"""

import os
import ast
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FocusedCodeQualityAssessor:
    """Focused code quality assessment for project code only"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = {
            "security": [],
            "incomplete": [],
            "structure": [],
            "performance": [],
            "maintainability": []
        }
        
        # Only analyze these directories (project code)
        self.include_dirs = ["kokoro", "scripts", "monitoring"]
        self.exclude_patterns = [
            "__pycache__", ".git", ".venv", "venv", "node_modules",
            "cache", "samples", "examples", "static", "nginx", "docs"
        ]
        
        # Security patterns to check
        self.security_patterns = [
            (r'eval\s*\(', "Use of eval() function"),
            (r'exec\s*\(', "Use of exec() function"),
            (r'subprocess\.call\s*\(.*shell\s*=\s*True', "Shell injection risk"),
            (r'os\.system\s*\(', "Use of os.system()"),
            (r'pickle\.loads?\s*\(', "Unsafe pickle usage"),
            (r'SECRET|PASSWORD|TOKEN|KEY.*=.*[\'\"]\w{8,}', "Hardcoded secrets"),
            (r'DEBUG\s*=\s*True', "Debug mode enabled in production")
        ]
        
        # Code quality patterns
        self.quality_patterns = [
            (r'TODO|FIXME|HACK|XXX', "TODO/FIXME comments"),
            (r'print\s*\(', "Print statements (should use logging)"),
            (r'except\s*:', "Bare except clause"),
            (r'pass\s*#.*TODO', "TODO pass statements"),
            (r'import\s+\*', "Wildcard imports")
        ]
    
    def should_analyze_file(self, file_path: Path) -> bool:
        """Determine if a file should be analyzed"""
        path_str = str(file_path)
        
        # Exclude patterns
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return False
        
        # Include only specific directories or root level files
        relative_path = file_path.relative_to(self.project_root)
        path_parts = relative_path.parts
        
        if len(path_parts) == 1:  # Root level files
            return True
        
        # Check if in included directories
        return path_parts[0] in self.include_dirs
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        analysis = {
            "path": str(file_path.relative_to(self.project_root)),
            "lines": 0,
            "functions": 0,
            "classes": 0,
            "security_issues": [],
            "quality_issues": [],
            "incomplete_implementations": [],
            "docstring_coverage": 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                analysis["lines"] = len(lines)
            
            # Parse AST for detailed analysis
            try:
                tree = ast.parse(content)
                analysis.update(self._analyze_ast(tree, content))
            except SyntaxError as e:
                self.issues["structure"].append({
                    "file": str(file_path.relative_to(self.project_root)),
                    "issue": f"Syntax error: {e}",
                    "severity": "high"
                })
            
            # Check security patterns
            for pattern, description in self.security_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    analysis["security_issues"].append({
                        "line": line_num,
                        "issue": description,
                        "code": lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    })
                    self.issues["security"].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "line": line_num,
                        "issue": description,
                        "severity": "medium"
                    })
            
            # Check quality patterns
            for pattern, description in self.quality_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    analysis["quality_issues"].append({
                        "line": line_num,
                        "issue": description,
                        "code": lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    })
                    self.issues["maintainability"].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "line": line_num,
                        "issue": description,
                        "severity": "low"
                    })
            
            # Check for incomplete implementations
            incomplete_patterns = [
                (r'raise\s+NotImplementedError', "NotImplementedError"),
                (r'pass\s*#.*TODO', "TODO implementation"),
                (r'def\s+\w+.*:\s*pass\s*$', "Empty function"),
                (r'class\s+\w+.*:\s*pass\s*$', "Empty class")
            ]
            
            for pattern, description in incomplete_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    analysis["incomplete_implementations"].append({
                        "line": line_num,
                        "issue": description,
                        "code": lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    })
                    self.issues["incomplete"].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "line": line_num,
                        "issue": description,
                        "severity": "medium"
                    })
            
        except Exception as e:
            self.issues["structure"].append({
                "file": str(file_path.relative_to(self.project_root)),
                "issue": f"Failed to analyze file: {e}",
                "severity": "medium"
            })
        
        return analysis
    
    def _analyze_ast(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Analyze AST for code metrics"""
        analysis = {
            "functions": 0,
            "classes": 0,
            "docstring_coverage": 0
        }
        
        functions_with_docs = 0
        classes_with_docs = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"] += 1
                if ast.get_docstring(node):
                    functions_with_docs += 1
                    
            elif isinstance(node, ast.ClassDef):
                analysis["classes"] += 1
                if ast.get_docstring(node):
                    classes_with_docs += 1
        
        # Calculate docstring coverage
        total_definitions = analysis["functions"] + analysis["classes"]
        if total_definitions > 0:
            documented = functions_with_docs + classes_with_docs
            analysis["docstring_coverage"] = (documented / total_definitions) * 100
        
        return analysis
    
    def check_configuration_files(self) -> Dict[str, Any]:
        """Check configuration files for issues"""
        logger.info("🔧 Analyzing configuration files...")
        
        config_analysis = {
            "files_checked": [],
            "security_issues": [],
            "structure_issues": []
        }
        
        config_files = ["config.json", "override.json", "app.py"]
        
        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                config_analysis["files_checked"].append(config_file)
                
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check for sensitive data patterns (more specific)
                    if config_file.endswith('.json'):
                        try:
                            json.loads(content)
                        except json.JSONDecodeError as e:
                            config_analysis["structure_issues"].append({
                                "file": config_file,
                                "issue": f"Invalid JSON: {e}",
                                "severity": "high"
                            })
                    
                    # Check for hardcoded secrets (more specific patterns)
                    secret_patterns = [
                        (r'"password"\s*:\s*"[^"]{8,}"', "Hardcoded password in config"),
                        (r'"secret"\s*:\s*"[^"]{16,}"', "Hardcoded secret in config"),
                        (r'"token"\s*:\s*"[^"]{20,}"', "Hardcoded token in config")
                    ]
                    
                    for pattern, description in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            config_analysis["security_issues"].append({
                                "file": config_file,
                                "issue": description,
                                "severity": "high"
                            })
                
                except Exception as e:
                    config_analysis["structure_issues"].append({
                        "file": config_file,
                        "issue": f"Failed to analyze: {e}",
                        "severity": "medium"
                    })
        
        return config_analysis
    
    def run_focused_assessment(self) -> Dict[str, Any]:
        """Run focused code quality assessment"""
        logger.info("🚀 Starting focused code quality assessment")
        logger.info("=" * 70)
        
        assessment_results = {
            "file_analysis": {},
            "configuration": {},
            "metrics": {
                "total_files": 0,
                "total_lines": 0,
                "total_functions": 0,
                "total_classes": 0,
                "avg_docstring_coverage": 0
            },
            "issues_summary": {},
            "recommendations": []
        }
        
        # 1. Configuration analysis
        assessment_results["configuration"] = self.check_configuration_files()
        
        # 2. Analyze project Python files
        logger.info("📝 Analyzing project Python files...")
        python_files = []
        
        for py_file in self.project_root.rglob("*.py"):
            if self.should_analyze_file(py_file):
                python_files.append(py_file)
        
        logger.info(f"   Found {len(python_files)} project Python files to analyze")
        
        file_analyses = {}
        total_lines = 0
        total_functions = 0
        total_classes = 0
        total_docstring_coverage = 0
        
        for py_file in python_files:
            analysis = self.analyze_python_file(py_file)
            file_analyses[analysis["path"]] = analysis
            
            total_lines += analysis["lines"]
            total_functions += analysis["functions"]
            total_classes += analysis["classes"]
            total_docstring_coverage += analysis["docstring_coverage"]
        
        assessment_results["file_analysis"] = file_analyses
        
        # 3. Calculate metrics
        assessment_results["metrics"] = {
            "total_files": len(python_files),
            "total_lines": total_lines,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "avg_docstring_coverage": total_docstring_coverage / len(python_files) if python_files else 0
        }
        
        # 4. Summarize issues
        assessment_results["issues_summary"] = {
            category: len(issues) for category, issues in self.issues.items()
        }
        
        # 5. Generate recommendations
        assessment_results["recommendations"] = self._generate_recommendations()
        
        # Generate summary report
        self._generate_assessment_report(assessment_results)
        
        return assessment_results
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Security recommendations
        if self.issues["security"]:
            recommendations.append({
                "category": "Security",
                "priority": "High",
                "recommendation": f"Address {len(self.issues['security'])} security issues in project code"
            })
        
        # Incomplete implementations
        if self.issues["incomplete"]:
            recommendations.append({
                "category": "Implementation",
                "priority": "High",
                "recommendation": f"Complete {len(self.issues['incomplete'])} incomplete implementations"
            })
        
        # Structure recommendations
        if self.issues["structure"]:
            recommendations.append({
                "category": "Structure",
                "priority": "Medium",
                "recommendation": f"Fix {len(self.issues['structure'])} structural issues"
            })
        
        # Maintainability recommendations
        if self.issues["maintainability"]:
            recommendations.append({
                "category": "Maintainability",
                "priority": "Low",
                "recommendation": f"Improve {len(self.issues['maintainability'])} maintainability issues"
            })
        
        return recommendations
    
    def _generate_assessment_report(self, results: Dict[str, Any]):
        """Generate assessment report"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 FOCUSED CODE QUALITY ASSESSMENT REPORT")
        logger.info("=" * 70)
        
        # Project metrics
        metrics = results["metrics"]
        logger.info(f"📁 Project Code Metrics:")
        logger.info(f"   Python Files: {metrics['total_files']}")
        logger.info(f"   Total Lines: {metrics['total_lines']}")
        logger.info(f"   Functions: {metrics['total_functions']}")
        logger.info(f"   Classes: {metrics['total_classes']}")
        logger.info(f"   Avg Docstring Coverage: {metrics['avg_docstring_coverage']:.1f}%")
        
        # Issues summary
        issues = results["issues_summary"]
        total_issues = sum(issues.values())
        logger.info(f"\n🚨 Issues Summary:")
        logger.info(f"   Security Issues: {issues['security']}")
        logger.info(f"   Incomplete Implementations: {issues['incomplete']}")
        logger.info(f"   Structure Issues: {issues['structure']}")
        logger.info(f"   Maintainability Issues: {issues['maintainability']}")
        logger.info(f"   Total Issues: {total_issues}")
        
        # Configuration analysis
        config = results["configuration"]
        logger.info(f"\n🔧 Configuration Analysis:")
        logger.info(f"   Files Checked: {len(config['files_checked'])}")
        logger.info(f"   Security Issues: {len(config['security_issues'])}")
        logger.info(f"   Structure Issues: {len(config['structure_issues'])}")
        
        # Top issues by file
        if results["file_analysis"]:
            logger.info(f"\n📋 Files with Most Issues:")
            file_issue_counts = {}
            for file_path, analysis in results["file_analysis"].items():
                issue_count = (len(analysis["security_issues"]) + 
                             len(analysis["quality_issues"]) + 
                             len(analysis["incomplete_implementations"]))
                if issue_count > 0:
                    file_issue_counts[file_path] = issue_count
            
            # Sort by issue count
            sorted_files = sorted(file_issue_counts.items(), key=lambda x: x[1], reverse=True)
            for file_path, count in sorted_files[:5]:  # Top 5
                logger.info(f"   {file_path}: {count} issues")
        
        # Recommendations
        recommendations = results["recommendations"]
        if recommendations:
            logger.info(f"\n💡 Recommendations:")
            for rec in recommendations:
                priority_icon = "🔴" if rec["priority"] == "High" else "🟡" if rec["priority"] == "Medium" else "🟢"
                logger.info(f"   {priority_icon} {rec['category']}: {rec['recommendation']}")
        
        # Overall assessment
        if total_issues == 0:
            logger.info("\n🎉 EXCELLENT PROJECT CODE QUALITY!")
            logger.info("✅ No significant issues detected in project code")
        elif total_issues <= 10:
            logger.info("\n✅ GOOD PROJECT CODE QUALITY")
            logger.info("🔧 Minor issues detected but overall quality is good")
        elif total_issues <= 25:
            logger.info("\n⚠️ MODERATE PROJECT CODE QUALITY")
            logger.info("🔧 Several issues detected that should be addressed")
        else:
            logger.info("\n❌ PROJECT CODE NEEDS ATTENTION")
            logger.info("🔧 Multiple issues detected requiring attention")
        
        logger.info("=" * 70)

def main():
    """Main assessment function"""
    assessor = FocusedCodeQualityAssessor()
    results = assessor.run_focused_assessment()
    
    # Save results to file
    with open("focused_code_quality_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("📄 Assessment results saved to focused_code_quality_results.json")
    
    # Exit with appropriate code based on issues
    total_issues = sum(results["issues_summary"].values())
    if total_issues <= 10:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
