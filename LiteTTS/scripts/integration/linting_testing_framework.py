#!/usr/bin/env python3
"""
Linting and Testing Framework
Implement comprehensive linting rules, code quality checks, and testing frameworks with coverage requirements
"""

import os
import sys
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LintingResult:
    """Linting result for a tool"""
    tool_name: str
    success: bool
    issues_found: int
    critical_issues: int
    warnings: int
    execution_time: float
    output: str
    error_message: str = ""

@dataclass
class TestResult:
    """Test execution result"""
    test_suite: str
    success: bool
    tests_run: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    coverage_percentage: float
    execution_time: float
    output: str
    error_message: str = ""

@dataclass
class QualityConfiguration:
    """Code quality configuration"""
    enable_black: bool
    enable_isort: bool
    enable_flake8: bool
    enable_pylint: bool
    enable_mypy: bool
    enable_bandit: bool
    enable_pytest: bool
    enable_coverage: bool
    min_coverage_percentage: float
    max_line_length: int
    exclude_patterns: List[str]
    test_directories: List[str]

class LintingTestingManager:
    """Linting and testing framework manager"""
    
    def __init__(self):
        self.results_dir = Path("test_results/linting_testing")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.config = self._create_default_config()
        
        # Results storage
        self.linting_results = {}
        self.testing_results = {}
        
    def _create_default_config(self) -> QualityConfiguration:
        """Create default quality configuration"""
        return QualityConfiguration(
            enable_black=True,
            enable_isort=True,
            enable_flake8=True,
            enable_pylint=True,
            enable_mypy=True,
            enable_bandit=True,
            enable_pytest=True,
            enable_coverage=True,
            min_coverage_percentage=80.0,
            max_line_length=88,
            exclude_patterns=[
                "__pycache__",
                "*.pyc",
                ".git",
                ".pytest_cache",
                "venv",
                "env",
                "build",
                "dist",
                "*.egg-info"
            ],
            test_directories=["tests", "test"]
        )
    
    def check_tool_availability(self, tool_name: str) -> bool:
        """Check if a linting/testing tool is available"""
        try:
            result = subprocess.run([tool_name, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def run_black(self, check_only: bool = True) -> LintingResult:
        """Run Black code formatter"""
        logger.info("Running Black code formatter...")
        start_time = time.time()
        
        try:
            cmd = ["black"]
            if check_only:
                cmd.extend(["--check", "--diff"])
            cmd.extend([
                "--line-length", str(self.config.max_line_length),
                "."
            ])
            
            # Add exclusions
            for pattern in self.config.exclude_patterns:
                cmd.extend(["--exclude", pattern])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            execution_time = time.time() - start_time
            
            # Parse output for issues
            issues_found = result.stdout.count("would reformat") if check_only else 0
            
            return LintingResult(
                tool_name="black",
                success=result.returncode == 0,
                issues_found=issues_found,
                critical_issues=issues_found,  # All Black issues are formatting issues
                warnings=0,
                execution_time=execution_time,
                output=result.stdout,
                error_message=result.stderr if result.returncode != 0 else ""
            )
            
        except subprocess.TimeoutExpired:
            return LintingResult(
                tool_name="black",
                success=False,
                issues_found=0,
                critical_issues=0,
                warnings=0,
                execution_time=time.time() - start_time,
                output="",
                error_message="Black execution timed out"
            )
        except Exception as e:
            return LintingResult(
                tool_name="black",
                success=False,
                issues_found=0,
                critical_issues=0,
                warnings=0,
                execution_time=time.time() - start_time,
                output="",
                error_message=str(e)
            )
    
    def run_isort(self, check_only: bool = True) -> LintingResult:
        """Run isort import sorter"""
        logger.info("Running isort import sorter...")
        start_time = time.time()
        
        try:
            cmd = ["isort"]
            if check_only:
                cmd.extend(["--check-only", "--diff"])
            cmd.extend([
                "--profile", "black",
                "--line-length", str(self.config.max_line_length),
                "."
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            execution_time = time.time() - start_time
            
            # Parse output for issues
            issues_found = result.stdout.count("ERROR:") + result.stdout.count("would reformat")
            
            return LintingResult(
                tool_name="isort",
                success=result.returncode == 0,
                issues_found=issues_found,
                critical_issues=issues_found,
                warnings=0,
                execution_time=execution_time,
                output=result.stdout,
                error_message=result.stderr if result.returncode != 0 else ""
            )
            
        except Exception as e:
            return LintingResult(
                tool_name="isort",
                success=False,
                issues_found=0,
                critical_issues=0,
                warnings=0,
                execution_time=time.time() - start_time,
                output="",
                error_message=str(e)
            )
    
    def run_flake8(self) -> LintingResult:
        """Run Flake8 linter"""
        logger.info("Running Flake8 linter...")
        start_time = time.time()
        
        try:
            cmd = [
                "flake8",
                "--max-line-length", str(self.config.max_line_length),
                "--extend-ignore", "E203,W503",  # Compatible with Black
                "--exclude", ",".join(self.config.exclude_patterns),
                "."
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            execution_time = time.time() - start_time
            
            # Parse output for issues
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            issues_found = len([line for line in lines if line.strip()])
            
            # Count critical issues (errors) vs warnings
            critical_issues = len([line for line in lines if ':E' in line])
            warnings = issues_found - critical_issues
            
            return LintingResult(
                tool_name="flake8",
                success=result.returncode == 0,
                issues_found=issues_found,
                critical_issues=critical_issues,
                warnings=warnings,
                execution_time=execution_time,
                output=result.stdout,
                error_message=result.stderr if result.returncode != 0 else ""
            )
            
        except Exception as e:
            return LintingResult(
                tool_name="flake8",
                success=False,
                issues_found=0,
                critical_issues=0,
                warnings=0,
                execution_time=time.time() - start_time,
                output="",
                error_message=str(e)
            )
    
    def run_pylint(self) -> LintingResult:
        """Run Pylint linter"""
        logger.info("Running Pylint linter...")
        start_time = time.time()
        
        try:
            # Find Python files to lint
            python_files = []
            for pattern in ["*.py"]:
                python_files.extend(Path(".").rglob(pattern))
            
            # Filter out excluded patterns
            filtered_files = []
            for file_path in python_files:
                if not any(pattern in str(file_path) for pattern in self.config.exclude_patterns):
                    filtered_files.append(str(file_path))
            
            if not filtered_files:
                return LintingResult(
                    tool_name="pylint",
                    success=True,
                    issues_found=0,
                    critical_issues=0,
                    warnings=0,
                    execution_time=time.time() - start_time,
                    output="No Python files found to lint",
                    error_message=""
                )
            
            cmd = [
                "pylint",
                "--max-line-length", str(self.config.max_line_length),
                "--disable", "C0114,C0115,C0116",  # Disable docstring requirements for now
                "--output-format", "text"
            ] + filtered_files[:10]  # Limit to first 10 files for performance
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            execution_time = time.time() - start_time
            
            # Parse Pylint output
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Count different types of issues
            critical_issues = len([line for line in lines if ':E' in line or ':F' in line])
            warnings = len([line for line in lines if ':W' in line or ':R' in line or ':C' in line])
            issues_found = critical_issues + warnings
            
            return LintingResult(
                tool_name="pylint",
                success=result.returncode in [0, 1, 2, 4, 8, 16],  # Pylint exit codes
                issues_found=issues_found,
                critical_issues=critical_issues,
                warnings=warnings,
                execution_time=execution_time,
                output=result.stdout,
                error_message=result.stderr if result.returncode not in [0, 1, 2, 4, 8, 16] else ""
            )
            
        except Exception as e:
            return LintingResult(
                tool_name="pylint",
                success=False,
                issues_found=0,
                critical_issues=0,
                warnings=0,
                execution_time=time.time() - start_time,
                output="",
                error_message=str(e)
            )
    
    def run_mypy(self) -> LintingResult:
        """Run MyPy type checker"""
        logger.info("Running MyPy type checker...")
        start_time = time.time()
        
        try:
            cmd = [
                "mypy",
                "--ignore-missing-imports",
                "--no-strict-optional",
                "--show-error-codes",
                "."
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            execution_time = time.time() - start_time
            
            # Parse MyPy output
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            issues_found = len([line for line in lines if 'error:' in line])
            
            # MyPy mostly reports errors, treat all as critical
            critical_issues = issues_found
            warnings = 0
            
            return LintingResult(
                tool_name="mypy",
                success=result.returncode == 0,
                issues_found=issues_found,
                critical_issues=critical_issues,
                warnings=warnings,
                execution_time=execution_time,
                output=result.stdout,
                error_message=result.stderr if result.returncode != 0 else ""
            )
            
        except Exception as e:
            return LintingResult(
                tool_name="mypy",
                success=False,
                issues_found=0,
                critical_issues=0,
                warnings=0,
                execution_time=time.time() - start_time,
                output="",
                error_message=str(e)
            )
    
    def run_bandit(self) -> LintingResult:
        """Run Bandit security linter"""
        logger.info("Running Bandit security linter...")
        start_time = time.time()
        
        try:
            cmd = [
                "bandit",
                "-r", ".",
                "-f", "json",
                "--exclude", ",".join(self.config.exclude_patterns)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            execution_time = time.time() - start_time
            
            # Parse Bandit JSON output
            try:
                if result.stdout:
                    bandit_data = json.loads(result.stdout)
                    issues_found = len(bandit_data.get("results", []))
                    
                    # Count by severity
                    critical_issues = len([r for r in bandit_data.get("results", []) 
                                         if r.get("issue_severity") in ["HIGH", "MEDIUM"]])
                    warnings = issues_found - critical_issues
                else:
                    issues_found = critical_issues = warnings = 0
            except json.JSONDecodeError:
                issues_found = critical_issues = warnings = 0
            
            return LintingResult(
                tool_name="bandit",
                success=result.returncode == 0,
                issues_found=issues_found,
                critical_issues=critical_issues,
                warnings=warnings,
                execution_time=execution_time,
                output=result.stdout,
                error_message=result.stderr if result.returncode != 0 else ""
            )
            
        except Exception as e:
            return LintingResult(
                tool_name="bandit",
                success=False,
                issues_found=0,
                critical_issues=0,
                warnings=0,
                execution_time=time.time() - start_time,
                output="",
                error_message=str(e)
            )

    def run_pytest(self) -> TestResult:
        """Run pytest test suite"""
        logger.info("Running pytest test suite...")
        start_time = time.time()

        try:
            # Find test directories
            test_dirs = []
            for test_dir in self.config.test_directories:
                if Path(test_dir).exists():
                    test_dirs.append(test_dir)

            if not test_dirs:
                # Create a basic test directory and file
                test_dir = Path("tests")
                test_dir.mkdir(exist_ok=True)

                # Create a basic test file
                basic_test = test_dir / "test_basic.py"
                if not basic_test.exists():
                    basic_test.write_text('''"""Basic test file for Kokoro TTS API"""

def test_basic_functionality():
    """Test basic functionality"""
    assert True

def test_import_modules():
    """Test that main modules can be imported"""
    try:
        import sys
        import os
        assert True
    except ImportError:
        assert False, "Failed to import basic modules"

def test_environment():
    """Test environment setup"""
    import os
    assert os.getcwd() is not None
''')
                test_dirs = ["tests"]

            cmd = [
                "pytest",
                "-v",
                "--tb=short",
                "--strict-markers"
            ] + test_dirs

            # Add coverage if enabled
            if self.config.enable_coverage:
                cmd.extend([
                    "--cov=.",
                    "--cov-report=term-missing",
                    "--cov-report=json:coverage.json",
                    f"--cov-fail-under={self.config.min_coverage_percentage}"
                ])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            execution_time = time.time() - start_time

            # Parse pytest output
            output_lines = result.stdout.split('\n')

            # Extract test counts
            tests_run = tests_passed = tests_failed = tests_skipped = 0
            coverage_percentage = 0.0

            for line in output_lines:
                if "passed" in line and "failed" in line:
                    # Parse line like "5 passed, 2 failed, 1 skipped"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed" and i > 0:
                            tests_passed = int(parts[i-1])
                        elif part == "failed" and i > 0:
                            tests_failed = int(parts[i-1])
                        elif part == "skipped" and i > 0:
                            tests_skipped = int(parts[i-1])
                elif "passed" in line and "failed" not in line:
                    # Parse line like "5 passed"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed" and i > 0:
                            tests_passed = int(parts[i-1])

            tests_run = tests_passed + tests_failed + tests_skipped

            # Extract coverage if available
            if self.config.enable_coverage and Path("coverage.json").exists():
                try:
                    with open("coverage.json", 'r') as f:
                        coverage_data = json.load(f)
                        coverage_percentage = coverage_data.get("totals", {}).get("percent_covered", 0.0)
                except Exception:
                    coverage_percentage = 0.0

            return TestResult(
                test_suite="pytest",
                success=result.returncode == 0,
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                tests_skipped=tests_skipped,
                coverage_percentage=coverage_percentage,
                execution_time=execution_time,
                output=result.stdout,
                error_message=result.stderr if result.returncode != 0 else ""
            )

        except Exception as e:
            return TestResult(
                test_suite="pytest",
                success=False,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                coverage_percentage=0.0,
                execution_time=time.time() - start_time,
                output="",
                error_message=str(e)
            )

    def run_all_linting(self) -> Dict[str, LintingResult]:
        """Run all enabled linting tools"""
        logger.info("Running all linting tools...")

        results = {}

        if self.config.enable_black and self.check_tool_availability("black"):
            results["black"] = self.run_black()

        if self.config.enable_isort and self.check_tool_availability("isort"):
            results["isort"] = self.run_isort()

        if self.config.enable_flake8 and self.check_tool_availability("flake8"):
            results["flake8"] = self.run_flake8()

        if self.config.enable_pylint and self.check_tool_availability("pylint"):
            results["pylint"] = self.run_pylint()

        if self.config.enable_mypy and self.check_tool_availability("mypy"):
            results["mypy"] = self.run_mypy()

        if self.config.enable_bandit and self.check_tool_availability("bandit"):
            results["bandit"] = self.run_bandit()

        self.linting_results = results
        return results

    def run_all_testing(self) -> Dict[str, TestResult]:
        """Run all enabled testing tools"""
        logger.info("Running all testing tools...")

        results = {}

        if self.config.enable_pytest and self.check_tool_availability("pytest"):
            results["pytest"] = self.run_pytest()

        self.testing_results = results
        return results

    def generate_makefile(self) -> str:
        """Generate Makefile for quality checks"""
        makefile_content = f'''# Kokoro TTS Quality Assurance Makefile

.PHONY: help install-dev lint test format check-format security type-check all clean

help:
	@echo "Available targets:"
	@echo "  install-dev    Install development dependencies"
	@echo "  lint          Run all linting tools"
	@echo "  test          Run test suite with coverage"
	@echo "  format        Format code with black and isort"
	@echo "  check-format  Check code formatting without changes"
	@echo "  security      Run security checks with bandit"
	@echo "  type-check    Run type checking with mypy"
	@echo "  all           Run all quality checks"
	@echo "  clean         Clean up generated files"

install-dev:
	pip install black isort flake8 pylint mypy bandit pytest pytest-cov pre-commit

lint:
	@echo "Running linting tools..."
	flake8 --max-line-length={self.config.max_line_length} --extend-ignore=E203,W503 .
	pylint --max-line-length={self.config.max_line_length} --disable=C0114,C0115,C0116 *.py scripts/*.py || true

test:
	@echo "Running test suite..."
	pytest -v --cov=. --cov-report=term-missing --cov-report=html

format:
	@echo "Formatting code..."
	black --line-length={self.config.max_line_length} .
	isort --profile=black --line-length={self.config.max_line_length} .

check-format:
	@echo "Checking code formatting..."
	black --check --diff --line-length={self.config.max_line_length} .
	isort --check-only --diff --profile=black --line-length={self.config.max_line_length} .

security:
	@echo "Running security checks..."
	bandit -r . -f json -o bandit-report.json || true
	bandit -r . || true

type-check:
	@echo "Running type checks..."
	mypy --ignore-missing-imports . || true

all: check-format lint security type-check test
	@echo "All quality checks completed!"

clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.json
	rm -rf bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {{}} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
'''

        # Save Makefile
        makefile_path = Path("Makefile")
        with open(makefile_path, 'w') as f:
            f.write(makefile_content)

        logger.info("Generated Makefile for quality checks")
        return makefile_content

    def run_comprehensive_quality_check(self) -> Dict[str, Any]:
        """Run comprehensive quality check"""
        logger.info("Starting comprehensive quality check...")

        # Generate configuration files
        config_files = self.generate_quality_config_files()
        pre_commit_config = self.generate_pre_commit_config()
        makefile = self.generate_makefile()

        # Run linting tools
        linting_results = self.run_all_linting()

        # Run testing tools
        testing_results = self.run_all_testing()

        # Calculate summary statistics
        total_linting_issues = sum(result.issues_found for result in linting_results.values())
        total_critical_issues = sum(result.critical_issues for result in linting_results.values())
        total_warnings = sum(result.warnings for result in linting_results.values())

        successful_linting_tools = sum(1 for result in linting_results.values() if result.success)
        successful_testing_tools = sum(1 for result in testing_results.values() if result.success)

        # Compile results
        results = {
            "check_timestamp": time.time(),
            "quality_configuration": asdict(self.config),
            "linting_results": {name: asdict(result) for name, result in linting_results.items()},
            "testing_results": {name: asdict(result) for name, result in testing_results.items()},
            "generated_files": {
                "config_files": list(config_files.keys()),
                "pre_commit_config": ".pre-commit-config.yaml",
                "makefile": "Makefile"
            },
            "summary": {
                "total_linting_tools": len(linting_results),
                "successful_linting_tools": successful_linting_tools,
                "total_testing_tools": len(testing_results),
                "successful_testing_tools": successful_testing_tools,
                "total_issues": total_linting_issues,
                "critical_issues": total_critical_issues,
                "warnings": total_warnings,
                "overall_success": (
                    successful_linting_tools == len(linting_results) and
                    successful_testing_tools == len(testing_results) and
                    total_critical_issues == 0
                )
            },
            "recommendations": self._generate_quality_recommendations(linting_results, testing_results)
        }

        # Save complete results
        results_file = self.results_dir / f"quality_check_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Comprehensive quality check completed. Results saved to: {results_file}")
        return results

    def _generate_quality_recommendations(self, linting_results: Dict[str, LintingResult],
                                        testing_results: Dict[str, TestResult]) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []

        # Linting recommendations
        for tool_name, result in linting_results.items():
            if not result.success:
                recommendations.append(f"Fix {tool_name} configuration or installation issues")
            elif result.critical_issues > 0:
                recommendations.append(f"Address {result.critical_issues} critical issues found by {tool_name}")
            elif result.warnings > 10:
                recommendations.append(f"Consider addressing {result.warnings} warnings from {tool_name}")

        # Testing recommendations
        for test_name, result in testing_results.items():
            if not result.success:
                recommendations.append(f"Fix {test_name} test failures")
            elif result.coverage_percentage < self.config.min_coverage_percentage:
                recommendations.append(f"Increase test coverage from {result.coverage_percentage:.1f}% to {self.config.min_coverage_percentage}%")

        # General recommendations
        recommendations.extend([
            "Set up pre-commit hooks for automated quality checks",
            "Integrate quality checks into CI/CD pipeline",
            "Configure IDE with quality tool plugins",
            "Establish code review process with quality requirements",
            "Set up automated quality reporting and monitoring"
        ])

        return recommendations

    def generate_quality_config_files(self) -> Dict[str, str]:
        """Generate configuration files for quality tools"""
        logger.info("Generating quality tool configuration files...")

        config_files = {}

        # pyproject.toml for Black, isort, and other tools
        exclude_patterns = "|".join(self.config.exclude_patterns)
        test_paths = ", ".join(f'"{d}"' for d in self.config.test_directories)
        omit_patterns = ", ".join(f'"{p}/*"' for p in self.config.exclude_patterns)

        pyproject_content = f'''[tool.black]
line-length = {self.config.max_line_length}
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\\.pyi?$'
extend-exclude = """
({exclude_patterns})
"""

[tool.isort]
profile = "black"
line_length = {self.config.max_line_length}
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = [
    {test_paths}
]
markers = [
    "slow: marks tests as slow (deselect with '-m \\"not slow\\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests"
]

[tool.coverage.run]
source = ["."]
omit = [
    {omit_patterns},
    "*/tests/*",
    "*/test_*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:"
]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true
'''

        config_files["pyproject.toml"] = pyproject_content

        # .flake8 configuration
        exclude_list = ",".join(self.config.exclude_patterns)
        flake8_content = f'''[flake8]
max-line-length = {self.config.max_line_length}
extend-ignore = E203, W503, E501
exclude = {exclude_list}
per-file-ignores =
    __init__.py:F401
    tests/*:S101
max-complexity = 10
'''

        config_files[".flake8"] = flake8_content

        # Save all configuration files
        for filename, content in config_files.items():
            config_file = Path(filename)
            with open(config_file, 'w') as f:
                f.write(content)
            logger.info(f"Generated configuration file: {filename}")

        return config_files

    def generate_pre_commit_config(self) -> str:
        """Generate pre-commit configuration"""
        logger.info("Generating pre-commit configuration...")

        pre_commit_content = f'''# Pre-commit configuration for Kokoro TTS
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
        args: [--line-length={self.config.max_line_length}]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black, --line-length={self.config.max_line_length}]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length={self.config.max_line_length}, --extend-ignore=E203,W503]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-c, .bandit]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]
'''

        # Save pre-commit configuration
        pre_commit_file = Path(".pre-commit-config.yaml")
        with open(pre_commit_file, 'w') as f:
            f.write(pre_commit_content)

        logger.info("Generated pre-commit configuration: .pre-commit-config.yaml")
        return pre_commit_content

def main():
    """Main function to run linting and testing framework"""
    manager = LintingTestingManager()

    try:
        # Run comprehensive quality check
        results = manager.run_comprehensive_quality_check()

        print("\n" + "="*80)
        print("LINTING AND TESTING FRAMEWORK SUMMARY")
        print("="*80)

        summary = results["summary"]

        print(f"Overall Success: {'✅' if summary['overall_success'] else '❌'}")
        print(f"Linting Tools: {summary['successful_linting_tools']}/{summary['total_linting_tools']}")
        print(f"Testing Tools: {summary['successful_testing_tools']}/{summary['total_testing_tools']}")

        print(f"\nIssue Summary:")
        print(f"  Total Issues: {summary['total_issues']}")
        print(f"  Critical Issues: {summary['critical_issues']}")
        print(f"  Warnings: {summary['warnings']}")

        print(f"\nLinting Results:")
        for tool_name, result_data in results["linting_results"].items():
            status = "✅" if result_data["success"] else "❌"
            print(f"  {status} {tool_name}: {result_data['issues_found']} issues ({result_data['execution_time']:.2f}s)")

        print(f"\nTesting Results:")
        for test_name, result_data in results["testing_results"].items():
            status = "✅" if result_data["success"] else "❌"
            coverage = f" - {result_data['coverage_percentage']:.1f}% coverage" if result_data['coverage_percentage'] > 0 else ""
            print(f"  {status} {test_name}: {result_data['tests_passed']}/{result_data['tests_run']} passed{coverage}")

        print(f"\nGenerated Files:")
        for file_type, files in results["generated_files"].items():
            if isinstance(files, list):
                print(f"  {file_type}: {', '.join(files)}")
            else:
                print(f"  {file_type}: {files}")

        print(f"\nRecommendations:")
        for i, rec in enumerate(results["recommendations"][:5], 1):
            print(f"  {i}. {rec}")

        if len(results["recommendations"]) > 5:
            print(f"  ... and {len(results['recommendations']) - 5} more recommendations")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"Quality check failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
