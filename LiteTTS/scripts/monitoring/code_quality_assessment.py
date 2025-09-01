#!/usr/bin/env python3
"""
Comprehensive Code Quality Assessment
Reviews code structure, identifies incomplete implementations, and security vulnerabilities
"""

import os
import ast
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CodeQualityAssessor:
    """Comprehensive code quality assessment tool"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = {
            "security": [],
            "incomplete": [],
            "structure": [],
            "performance": [],
            "maintainability": []
        }
        self.metrics = {
            "total_files": 0,
            "total_lines": 0,
            "python_files": 0,
            "test_files": 0,
            "config_files": 0
        }
        
        # Security patterns to check
        self.security_patterns = [
            (r'eval\s*\(', "Use of eval() function"),
            (r'exec\s*\(', "Use of exec() function"),
            (r'subprocess\.call\s*\(.*shell\s*=\s*True', "Shell injection risk"),
            (r'os\.system\s*\(', "Use of os.system()"),
            (r'pickle\.loads?\s*\(', "Unsafe pickle usage"),
            (r'yaml\.load\s*\((?!.*Loader)', "Unsafe YAML loading"),
            (r'input\s*\(.*\)', "Use of input() function"),
            (r'open\s*\(.*[\'\"]/.*[\'\"]\s*,\s*[\'\"]\w*w', "Potential path traversal"),
            (r'SECRET|PASSWORD|TOKEN|KEY.*=.*[\'\"]\w+', "Hardcoded secrets"),
            (r'DEBUG\s*=\s*True', "Debug mode enabled")
        ]
        
        # Code quality patterns
        self.quality_patterns = [
            (r'TODO|FIXME|HACK|XXX', "TODO/FIXME comments"),
            (r'print\s*\(', "Print statements (should use logging)"),
            (r'except\s*:', "Bare except clause"),
            (r'pass\s*$', "Empty pass statements"),
            (r'import\s+\*', "Wildcard imports"),
            (r'def\s+\w+\s*\([^)]*\)\s*:\s*$', "Empty function definitions")
        ]
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        analysis = {
            "path": str(file_path),
            "lines": 0,
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "security_issues": [],
            "quality_issues": [],
            "complexity_score": 0,
            "docstring_coverage": 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                analysis["lines"] = len(lines)
                self.metrics["total_lines"] += len(lines)
            
            # Parse AST for detailed analysis
            try:
                tree = ast.parse(content)
                analysis.update(self._analyze_ast(tree))
            except SyntaxError as e:
                self.issues["structure"].append({
                    "file": str(file_path),
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
                        "file": str(file_path),
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
                        "file": str(file_path),
                        "line": line_num,
                        "issue": description,
                        "severity": "low"
                    })
            
        except Exception as e:
            self.issues["structure"].append({
                "file": str(file_path),
                "issue": f"Failed to analyze file: {e}",
                "severity": "medium"
            })
        
        return analysis
    
    def _analyze_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze AST for code metrics"""
        analysis = {
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "complexity_score": 0,
            "docstring_coverage": 0
        }
        
        functions_with_docs = 0
        classes_with_docs = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"] += 1
                if ast.get_docstring(node):
                    functions_with_docs += 1
                # Calculate cyclomatic complexity (simplified)
                complexity = self._calculate_complexity(node)
                analysis["complexity_score"] += complexity
                
            elif isinstance(node, ast.ClassDef):
                analysis["classes"] += 1
                if ast.get_docstring(node):
                    classes_with_docs += 1
                    
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                analysis["imports"] += 1
        
        # Calculate docstring coverage
        total_definitions = analysis["functions"] + analysis["classes"]
        if total_definitions > 0:
            documented = functions_with_docs + classes_with_docs
            analysis["docstring_coverage"] = (documented / total_definitions) * 100
        
        return analysis
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def check_project_structure(self) -> Dict[str, Any]:
        """Check overall project structure"""
        logger.info("🏗️ Analyzing project structure...")
        
        structure_analysis = {
            "has_tests": False,
            "has_docs": False,
            "has_config": False,
            "has_requirements": False,
            "has_dockerfile": False,
            "has_gitignore": False,
            "missing_files": [],
            "directory_structure": {}
        }
        
        # Check for important files
        important_files = {
            "requirements.txt": "has_requirements",
            "pyproject.toml": "has_requirements",
            "Dockerfile": "has_dockerfile",
            ".gitignore": "has_gitignore",
            "README.md": "has_docs",
            "config.json": "has_config"
        }
        
        for file_name, flag in important_files.items():
            if (self.project_root / file_name).exists():
                structure_analysis[flag] = True
            else:
                structure_analysis["missing_files"].append(file_name)
        
        # Check for test directories
        test_dirs = ["tests", "test", "testing"]
        for test_dir in test_dirs:
            if (self.project_root / test_dir).exists():
                structure_analysis["has_tests"] = True
                break
        
        # Analyze directory structure
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                structure_analysis["directory_structure"][item.name] = {
                    "files": len(list(item.glob("*.py"))),
                    "subdirs": len([d for d in item.iterdir() if d.is_dir()])
                }
        
        return structure_analysis
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check dependency management"""
        logger.info("📦 Analyzing dependencies...")
        
        dependency_analysis = {
            "requirements_files": [],
            "dependency_count": 0,
            "security_issues": [],
            "outdated_patterns": []
        }
        
        # Check requirements files
        req_files = ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]
        
        for req_file in req_files:
            file_path = self.project_root / req_file
            if file_path.exists():
                dependency_analysis["requirements_files"].append(req_file)
                
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    # Count dependencies (simplified)
                    if req_file == "requirements.txt":
                        deps = [line.strip() for line in content.split('\n') 
                               if line.strip() and not line.startswith('#')]
                        dependency_analysis["dependency_count"] += len(deps)
                        
                        # Check for potentially insecure patterns
                        for dep in deps:
                            if '==' not in dep and '>=' not in dep:
                                dependency_analysis["security_issues"].append({
                                    "file": req_file,
                                    "issue": f"Unpinned dependency: {dep}",
                                    "severity": "medium"
                                })
                
                except Exception as e:
                    self.issues["structure"].append({
                        "file": req_file,
                        "issue": f"Failed to parse dependencies: {e}",
                        "severity": "low"
                    })
        
        return dependency_analysis
    
    def check_configuration_security(self) -> Dict[str, Any]:
        """Check configuration files for security issues"""
        logger.info("🔒 Analyzing configuration security...")
        
        config_analysis = {
            "config_files": [],
            "security_issues": [],
            "best_practices": []
        }
        
        config_files = ["config.json", "override.json", ".env", "docker-compose.yml"]
        
        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                config_analysis["config_files"].append(config_file)
                
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check for sensitive data patterns
                    sensitive_patterns = [
                        (r'password.*[\'\"]\w+', "Hardcoded password"),
                        (r'secret.*[\'\"]\w+', "Hardcoded secret"),
                        (r'token.*[\'\"]\w+', "Hardcoded token"),
                        (r'key.*[\'\"]\w+', "Hardcoded key"),
                        (r'api_key.*[\'\"]\w+', "Hardcoded API key")
                    ]
                    
                    for pattern, description in sensitive_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            config_analysis["security_issues"].append({
                                "file": config_file,
                                "issue": description,
                                "severity": "high"
                            })
                    
                    # Check for good practices
                    if config_file.endswith('.json'):
                        try:
                            json.loads(content)
                            config_analysis["best_practices"].append({
                                "file": config_file,
                                "practice": "Valid JSON format"
                            })
                        except json.JSONDecodeError:
                            config_analysis["security_issues"].append({
                                "file": config_file,
                                "issue": "Invalid JSON format",
                                "severity": "medium"
                            })
                
                except Exception as e:
                    self.issues["structure"].append({
                        "file": config_file,
                        "issue": f"Failed to analyze config: {e}",
                        "severity": "low"
                    })
        
        return config_analysis
    
    def run_comprehensive_assessment(self) -> Dict[str, Any]:
        """Run comprehensive code quality assessment"""
        logger.info("🚀 Starting comprehensive code quality assessment")
        logger.info("=" * 70)
        
        assessment_results = {
            "project_structure": {},
            "file_analysis": {},
            "dependencies": {},
            "configuration": {},
            "metrics": {},
            "issues_summary": {},
            "recommendations": []
        }
        
        # 1. Project structure analysis
        assessment_results["project_structure"] = self.check_project_structure()
        
        # 2. Dependency analysis
        assessment_results["dependencies"] = self.check_dependencies()
        
        # 3. Configuration security
        assessment_results["configuration"] = self.check_configuration_security()
        
        # 4. Analyze Python files
        logger.info("📝 Analyzing Python files...")
        python_files = list(self.project_root.rglob("*.py"))
        self.metrics["python_files"] = len(python_files)
        self.metrics["total_files"] = len(list(self.project_root.rglob("*")))
        
        file_analyses = {}
        for py_file in python_files:
            if not any(exclude in str(py_file) for exclude in ['.git', '__pycache__', '.venv', 'venv']):
                analysis = self.analyze_python_file(py_file)
                file_analyses[str(py_file.relative_to(self.project_root))] = analysis
        
        assessment_results["file_analysis"] = file_analyses
        
        # 5. Calculate metrics
        assessment_results["metrics"] = self.metrics
        
        # 6. Summarize issues
        assessment_results["issues_summary"] = {
            category: len(issues) for category, issues in self.issues.items()
        }
        
        # 7. Generate recommendations
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
                "recommendation": f"Address {len(self.issues['security'])} security issues including potential code injection and hardcoded secrets"
            })
        
        # Structure recommendations
        if self.issues["structure"]:
            recommendations.append({
                "category": "Structure",
                "priority": "Medium",
                "recommendation": f"Fix {len(self.issues['structure'])} structural issues including syntax errors and file parsing problems"
            })
        
        # Maintainability recommendations
        if self.issues["maintainability"]:
            recommendations.append({
                "category": "Maintainability",
                "priority": "Low",
                "recommendation": f"Improve {len(self.issues['maintainability'])} maintainability issues including TODO comments and code quality"
            })
        
        # Test coverage recommendation
        if self.metrics["test_files"] == 0:
            recommendations.append({
                "category": "Testing",
                "priority": "High",
                "recommendation": "Add comprehensive test suite - no test files detected"
            })
        
        return recommendations
    
    def _generate_assessment_report(self, results: Dict[str, Any]):
        """Generate assessment report"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 CODE QUALITY ASSESSMENT REPORT")
        logger.info("=" * 70)
        
        # Project metrics
        metrics = results["metrics"]
        logger.info(f"📁 Project Metrics:")
        logger.info(f"   Total Files: {metrics['total_files']}")
        logger.info(f"   Python Files: {metrics['python_files']}")
        logger.info(f"   Total Lines: {metrics['total_lines']}")
        
        # Issues summary
        issues = results["issues_summary"]
        total_issues = sum(issues.values())
        logger.info(f"\n🚨 Issues Summary:")
        logger.info(f"   Security Issues: {issues['security']}")
        logger.info(f"   Structure Issues: {issues['structure']}")
        logger.info(f"   Performance Issues: {issues['performance']}")
        logger.info(f"   Maintainability Issues: {issues['maintainability']}")
        logger.info(f"   Total Issues: {total_issues}")
        
        # Project structure
        structure = results["project_structure"]
        logger.info(f"\n🏗️ Project Structure:")
        logger.info(f"   Has Tests: {'✅' if structure['has_tests'] else '❌'}")
        logger.info(f"   Has Documentation: {'✅' if structure['has_docs'] else '❌'}")
        logger.info(f"   Has Configuration: {'✅' if structure['has_config'] else '❌'}")
        logger.info(f"   Has Requirements: {'✅' if structure['has_requirements'] else '❌'}")
        
        # Recommendations
        recommendations = results["recommendations"]
        if recommendations:
            logger.info(f"\n💡 Recommendations:")
            for rec in recommendations:
                priority_icon = "🔴" if rec["priority"] == "High" else "🟡" if rec["priority"] == "Medium" else "🟢"
                logger.info(f"   {priority_icon} {rec['category']}: {rec['recommendation']}")
        
        # Overall assessment
        if total_issues == 0:
            logger.info("\n🎉 EXCELLENT CODE QUALITY!")
            logger.info("✅ No significant issues detected")
        elif total_issues <= 5:
            logger.info("\n✅ GOOD CODE QUALITY")
            logger.info("🔧 Minor issues detected but overall quality is good")
        elif total_issues <= 15:
            logger.info("\n⚠️ MODERATE CODE QUALITY")
            logger.info("🔧 Several issues detected that should be addressed")
        else:
            logger.info("\n❌ POOR CODE QUALITY")
            logger.info("🔧 Significant issues detected requiring immediate attention")
        
        logger.info("=" * 70)

def main():
    """Main assessment function"""
    assessor = CodeQualityAssessor()
    results = assessor.run_comprehensive_assessment()
    
    # Save results to file
    with open("code_quality_assessment_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("📄 Assessment results saved to code_quality_assessment_results.json")
    
    # Exit with appropriate code based on issues
    total_issues = sum(results["issues_summary"].values())
    if total_issues <= 5:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
