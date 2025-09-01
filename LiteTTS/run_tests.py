#!/usr/bin/env python3
"""
Comprehensive Test Runner for Kokoro ONNX TTS API
Executes all test suites with proper reporting and configuration
"""

import os
import sys
import subprocess
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class TestRunner:
    """Comprehensive test runner for Kokoro ONNX TTS API"""
    
    def __init__(self, verbose: bool = False, coverage: bool = False):
        self.verbose = verbose
        self.coverage = coverage
        self.results = {}
        self.start_time = time.time()
        
        # Test suites configuration
        self.test_suites = {
            "unit": {
                "description": "Unit tests for individual components",
                "paths": [
                    "tests/test_performance.py",
                    "LiteTTS/tests/test_*.py"
                ],
                "timeout": 300,  # 5 minutes
                "critical": True
            },
            "error_handling": {
                "description": "Error handling and edge case tests",
                "paths": [
                    "tests/test_error_handling.py",
                    "tests/test_edge_cases.py"
                ],
                "timeout": 600,  # 10 minutes
                "critical": True
            },
            "integration": {
                "description": "Integration tests with external services",
                "paths": [
                    "tests/test_integration.py",
                    "tests/test_comprehensive.py"
                ],
                "timeout": 900,  # 15 minutes
                "critical": False
            },
            "load": {
                "description": "Load and performance tests",
                "paths": [
                    "tests/test_load_testing.py"
                ],
                "timeout": 1200,  # 20 minutes
                "critical": False
            },
            "validation": {
                "description": "System validation and health checks",
                "paths": [
                    "LiteTTS/tests/comprehensive_validation.py"
                ],
                "timeout": 180,  # 3 minutes
                "critical": True
            }
        }
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        try:
            # Check if uv is available
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ uv is not installed or not in PATH")
                return False
            
            # Check if pytest is available
            result = subprocess.run(["uv", "run", "python", "-m", "pytest", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ pytest is not available. Installing dev dependencies...")
                install_result = subprocess.run(["uv", "sync", "--extra", "dev"], 
                                               capture_output=True, text=True)
                if install_result.returncode != 0:
                    print(f"❌ Failed to install dev dependencies: {install_result.stderr}")
                    return False
                print("✅ Dev dependencies installed")
            
            return True
            
        except Exception as e:
            print(f"❌ Dependency check failed: {e}")
            return False
    
    def find_test_files(self, paths: List[str]) -> List[Path]:
        """Find all test files matching the given patterns"""
        test_files = []
        
        for path_pattern in paths:
            path = Path(path_pattern)
            
            if path.is_file():
                test_files.append(path)
            elif "*" in str(path):
                # Handle glob patterns
                parent = path.parent
                pattern = path.name
                if parent.exists():
                    test_files.extend(parent.glob(pattern))
            elif path.is_dir():
                # Find all test files in directory
                test_files.extend(path.glob("test_*.py"))
                test_files.extend(path.glob("*_test.py"))
        
        return [f for f in test_files if f.exists()]
    
    def run_test_suite(self, suite_name: str, suite_config: Dict) -> Dict:
        """Run a specific test suite"""
        print(f"\n🧪 Running {suite_name} tests...")
        print(f"📝 {suite_config['description']}")
        
        # Find test files
        test_files = self.find_test_files(suite_config["paths"])
        
        if not test_files:
            print(f"⚠️  No test files found for {suite_name}")
            return {
                "status": "skipped",
                "reason": "No test files found",
                "duration": 0,
                "tests_run": 0,
                "failures": 0,
                "errors": 0
            }
        
        print(f"📁 Found {len(test_files)} test files")
        
        # Build pytest command
        cmd = ["uv", "run", "python", "-m", "pytest"]
        
        # Add test files
        cmd.extend(str(f) for f in test_files)
        
        # Add options
        if self.verbose:
            cmd.extend(["-v", "-s"])
        else:
            cmd.append("-q")
        
        # Add coverage if requested
        if self.coverage:
            cmd.extend([
                "--cov=kokoro",
                "--cov-report=term-missing",
                f"--cov-report=html:docs/coverage_{suite_name}"
            ])
        
        # Add timeout
        cmd.extend(["--timeout", str(suite_config["timeout"])])
        
        # Add JSON report
        json_report = f"docs/test_results_{suite_name}.json"
        cmd.extend(["--json-report", f"--json-report-file={json_report}"])
        
        # Run tests
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=suite_config["timeout"] + 60  # Extra buffer
            )
            
            duration = time.time() - start_time
            
            # Parse results
            test_result = self._parse_test_result(result, json_report, duration)
            
            # Print summary
            if test_result["status"] == "passed":
                print(f"✅ {suite_name}: {test_result['tests_run']} tests passed in {duration:.1f}s")
            elif test_result["status"] == "failed":
                print(f"❌ {suite_name}: {test_result['failures']} failures, {test_result['errors']} errors")
            else:
                print(f"⚠️  {suite_name}: {test_result['status']}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"⏰ {suite_name}: Timed out after {duration:.1f}s")
            return {
                "status": "timeout",
                "duration": duration,
                "tests_run": 0,
                "failures": 0,
                "errors": 1
            }
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {suite_name}: Exception - {e}")
            return {
                "status": "error",
                "error": str(e),
                "duration": duration,
                "tests_run": 0,
                "failures": 0,
                "errors": 1
            }
    
    def _parse_test_result(self, result: subprocess.CompletedProcess, 
                          json_report: str, duration: float) -> Dict:
        """Parse test result from subprocess and JSON report"""
        
        # Try to parse JSON report first
        try:
            if Path(json_report).exists():
                with open(json_report, 'r') as f:
                    json_data = json.load(f)
                
                return {
                    "status": "passed" if result.returncode == 0 else "failed",
                    "duration": duration,
                    "tests_run": json_data.get("summary", {}).get("total", 0),
                    "failures": json_data.get("summary", {}).get("failed", 0),
                    "errors": json_data.get("summary", {}).get("error", 0),
                    "json_report": json_report
                }
        except Exception:
            pass
        
        # Fallback to parsing stdout/stderr
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "duration": duration,
            "tests_run": 0,  # Can't determine from basic output
            "failures": 1 if result.returncode != 0 else 0,
            "errors": 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def run_all_tests(self, suites: Optional[List[str]] = None) -> Dict:
        """Run all test suites or specified suites"""
        
        if not self.check_dependencies():
            return {"status": "error", "message": "Dependency check failed"}
        
        # Determine which suites to run
        suites_to_run = suites if suites else list(self.test_suites.keys())
        
        print("🚀 Starting Kokoro ONNX TTS API Test Suite")
        print("=" * 60)
        
        # Create results directory
        Path("docs").mkdir(exist_ok=True)
        
        # Run each test suite
        for suite_name in suites_to_run:
            if suite_name not in self.test_suites:
                print(f"⚠️  Unknown test suite: {suite_name}")
                continue
            
            suite_config = self.test_suites[suite_name]
            self.results[suite_name] = self.run_test_suite(suite_name, suite_config)
        
        # Generate summary
        return self._generate_summary()
    
    def _generate_summary(self) -> Dict:
        """Generate test run summary"""
        total_duration = time.time() - self.start_time
        
        total_tests = sum(r.get("tests_run", 0) for r in self.results.values())
        total_failures = sum(r.get("failures", 0) for r in self.results.values())
        total_errors = sum(r.get("errors", 0) for r in self.results.values())
        
        passed_suites = sum(1 for r in self.results.values() if r.get("status") == "passed")
        total_suites = len(self.results)
        
        # Determine overall status
        critical_suites = [name for name, config in self.test_suites.items() 
                          if config.get("critical", False) and name in self.results]
        critical_failures = [name for name in critical_suites 
                           if self.results[name].get("status") != "passed"]
        
        if critical_failures:
            overall_status = "failed"
        elif total_failures > 0 or total_errors > 0:
            overall_status = "partial"
        else:
            overall_status = "passed"
        
        summary = {
            "status": overall_status,
            "duration": total_duration,
            "suites": {
                "total": total_suites,
                "passed": passed_suites,
                "failed": total_suites - passed_suites
            },
            "tests": {
                "total": total_tests,
                "passed": total_tests - total_failures - total_errors,
                "failed": total_failures,
                "errors": total_errors
            },
            "critical_failures": critical_failures,
            "results": self.results
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"🎯 Overall Status: {overall_status.upper()}")
        print(f"⏱️  Total Duration: {total_duration:.1f}s")
        print(f"📦 Test Suites: {passed_suites}/{total_suites} passed")
        print(f"🧪 Individual Tests: {total_tests - total_failures - total_errors}/{total_tests} passed")
        
        if critical_failures:
            print(f"🚨 Critical Failures: {', '.join(critical_failures)}")
        
        # Save summary to file
        summary_file = "docs/test_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📄 Detailed results saved to: {summary_file}")
        
        return summary


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Run Kokoro ONNX TTS API test suites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Suites:
  unit          - Unit tests for individual components
  error_handling - Error handling and edge case tests  
  integration   - Integration tests with external services
  load          - Load and performance tests
  validation    - System validation and health checks

Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py unit integration  # Run specific suites
  python run_tests.py --verbose         # Verbose output
  python run_tests.py --coverage        # Include coverage report
        """
    )
    
    parser.add_argument(
        "suites",
        nargs="*",
        help="Test suites to run (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--list-suites",
        action="store_true",
        help="List available test suites"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose, coverage=args.coverage)
    
    if args.list_suites:
        print("Available test suites:")
        for name, config in runner.test_suites.items():
            critical = "🚨 CRITICAL" if config.get("critical") else "📋 Optional"
            print(f"  {name:15} - {config['description']} ({critical})")
        return 0
    
    # Run tests
    summary = runner.run_all_tests(args.suites)
    
    # Return appropriate exit code
    if summary["status"] == "passed":
        return 0
    elif summary["status"] == "partial":
        return 1  # Some non-critical tests failed
    else:
        return 2  # Critical tests failed


if __name__ == "__main__":
    sys.exit(main())
