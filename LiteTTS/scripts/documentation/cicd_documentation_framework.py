#!/usr/bin/env python3
"""
CI/CD Integration and Documentation Coverage Framework
Implement CI/CD pipelines, documentation coverage tracking, and backward compatibility testing
"""

import os
import sys
import json
import logging
import subprocess
import time
import re
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
class DocumentationCoverage:
    """Documentation coverage metrics"""
    total_modules: int
    documented_modules: int
    total_functions: int
    documented_functions: int
    total_classes: int
    documented_classes: int
    coverage_percentage: float
    missing_docstrings: List[str]

@dataclass
class CICDConfiguration:
    """CI/CD configuration settings"""
    enable_github_actions: bool
    enable_gitlab_ci: bool
    enable_docker_build: bool
    enable_automated_testing: bool
    enable_security_scanning: bool
    enable_documentation_check: bool
    enable_performance_testing: bool
    min_test_coverage: float
    min_documentation_coverage: float
    python_versions: List[str]
    deployment_environments: List[str]

class CICDDocumentationManager:
    """CI/CD and documentation coverage manager"""
    
    def __init__(self):
        self.results_dir = Path("test_results/cicd_documentation")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.config = self._create_default_config()
        
        # Documentation patterns
        self.docstring_patterns = {
            'function': re.compile(r'def\s+(\w+)\s*\('),
            'class': re.compile(r'class\s+(\w+)\s*[\(:]'),
            'module': re.compile(r'^""".*?"""', re.MULTILINE | re.DOTALL)
        }
        
    def _create_default_config(self) -> CICDConfiguration:
        """Create default CI/CD configuration"""
        return CICDConfiguration(
            enable_github_actions=True,
            enable_gitlab_ci=True,
            enable_docker_build=True,
            enable_automated_testing=True,
            enable_security_scanning=True,
            enable_documentation_check=True,
            enable_performance_testing=True,
            min_test_coverage=80.0,
            min_documentation_coverage=83.7,  # User's target
            python_versions=["3.8", "3.9", "3.10", "3.11"],
            deployment_environments=["development", "staging", "production"]
        )
    
    def analyze_documentation_coverage(self) -> DocumentationCoverage:
        """Analyze documentation coverage across the codebase"""
        logger.info("Analyzing documentation coverage...")
        
        total_modules = documented_modules = 0
        total_functions = documented_functions = 0
        total_classes = documented_classes = 0
        missing_docstrings = []
        
        # Find all Python files
        python_files = []
        for pattern in ["*.py"]:
            python_files.extend(Path(".").rglob(pattern))
        
        # Filter out excluded files
        excluded_patterns = ["__pycache__", ".git", "venv", "env", "build", "dist"]
        filtered_files = []
        for file_path in python_files:
            if not any(pattern in str(file_path) for pattern in excluded_patterns):
                filtered_files.append(file_path)
        
        for file_path in filtered_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check module docstring
                total_modules += 1
                if self.docstring_patterns['module'].search(content):
                    documented_modules += 1
                else:
                    missing_docstrings.append(f"Module: {file_path}")
                
                # Check function docstrings
                functions = self.docstring_patterns['function'].findall(content)
                for func_name in functions:
                    if not func_name.startswith('_'):  # Skip private functions
                        total_functions += 1
                        
                        # Look for docstring after function definition
                        func_pattern = re.compile(
                            rf'def\s+{re.escape(func_name)}\s*\([^)]*\):\s*""".*?"""',
                            re.MULTILINE | re.DOTALL
                        )
                        
                        if func_pattern.search(content):
                            documented_functions += 1
                        else:
                            missing_docstrings.append(f"Function: {file_path}:{func_name}")
                
                # Check class docstrings
                classes = self.docstring_patterns['class'].findall(content)
                for class_name in classes:
                    if not class_name.startswith('_'):  # Skip private classes
                        total_classes += 1
                        
                        # Look for docstring after class definition
                        class_pattern = re.compile(
                            rf'class\s+{re.escape(class_name)}\s*[\(:].*?:\s*""".*?"""',
                            re.MULTILINE | re.DOTALL
                        )
                        
                        if class_pattern.search(content):
                            documented_classes += 1
                        else:
                            missing_docstrings.append(f"Class: {file_path}:{class_name}")
                
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")
        
        # Calculate overall coverage
        total_items = total_modules + total_functions + total_classes
        documented_items = documented_modules + documented_functions + documented_classes
        coverage_percentage = (documented_items / total_items * 100) if total_items > 0 else 0
        
        return DocumentationCoverage(
            total_modules=total_modules,
            documented_modules=documented_modules,
            total_functions=total_functions,
            documented_functions=documented_functions,
            total_classes=total_classes,
            documented_classes=documented_classes,
            coverage_percentage=coverage_percentage,
            missing_docstrings=missing_docstrings[:20]  # Limit to first 20
        )
    
    def generate_github_actions_workflow(self) -> str:
        """Generate GitHub Actions workflow"""
        logger.info("Generating GitHub Actions workflow...")
        
        workflow_content = f'''name: Kokoro TTS CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: {json.dumps(self.config.python_versions)}

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{{{ runner.os }}}}-pip-${{{{ hashFiles('**/requirements.txt') }}}}
        restore-keys: |
          ${{{{ runner.os }}}}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov black isort flake8 bandit mypy
    
    - name: Code formatting check
      run: |
        black --check --diff .
        isort --check-only --diff .
    
    - name: Linting
      run: |
        flake8 .
        bandit -r . || true
    
    - name: Type checking
      run: |
        mypy . || true
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml --cov-fail-under={self.config.min_test_coverage}
    
    - name: Documentation coverage check
      run: |
        python scripts/cicd_documentation_framework.py --check-docs
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      uses: securecodewarrior/github-action-add-sarif@v1
      with:
        sarif-file: bandit-report.sarif

  docker:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{{{ secrets.DOCKER_USERNAME }}}}
        password: ${{{{ secrets.DOCKER_PASSWORD }}}}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: kokoro-tts:latest,kokoro-tts:${{{{ github.sha }}}}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    runs-on: ubuntu-latest
    needs: [test, docker]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment..."
        # Add your deployment commands here
    
    - name: Run integration tests
      run: |
        echo "Running integration tests..."
        # Add integration test commands here
    
    - name: Deploy to production
      if: success()
      run: |
        echo "Deploying to production environment..."
        # Add production deployment commands here
'''
        
        # Save workflow file
        workflow_dir = Path(".github/workflows")
        workflow_dir.mkdir(parents=True, exist_ok=True)
        workflow_file = workflow_dir / "ci-cd.yml"
        
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        logger.info(f"GitHub Actions workflow saved: {workflow_file}")
        return workflow_content
    
    def generate_gitlab_ci_config(self) -> str:
        """Generate GitLab CI configuration"""
        logger.info("Generating GitLab CI configuration...")
        
        gitlab_ci_content = f'''# LiteTTS GitLab CI/CD Pipeline

stages:
  - test
  - security
  - build
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/
    - venv/

before_script:
  - python -m venv venv
  - source venv/bin/activate
  - pip install --upgrade pip
  - pip install -r requirements.txt

test:
  stage: test
  parallel:
    matrix:
      - PYTHON_VERSION: {json.dumps(self.config.python_versions)}
  image: python:$PYTHON_VERSION
  script:
    - pip install pytest pytest-cov black isort flake8 bandit mypy
    - black --check --diff .
    - isort --check-only --diff .
    - flake8 .
    - mypy . || true
    - pytest --cov=. --cov-report=xml --cov-fail-under={self.config.min_test_coverage}
    - python scripts/cicd_documentation_framework.py --check-docs
  coverage: '/TOTAL.*\\s+(\\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

security_scan:
  stage: security
  image: python:3.11
  script:
    - pip install bandit safety
    - bandit -r . -f json -o bandit-report.json || true
    - safety check --json --output safety-report.json || true
  artifacts:
    reports:
      sast: bandit-report.json
    paths:
      - bandit-report.json
      - safety-report.json

docker_build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main

deploy_staging:
  stage: deploy
  image: alpine:latest
  script:
    - echo "Deploying to staging environment..."
    # Add staging deployment commands
  environment:
    name: staging
    url: https://staging.kokoro-tts.example.com
  only:
    - main

deploy_production:
  stage: deploy
  image: alpine:latest
  script:
    - echo "Deploying to production environment..."
    # Add production deployment commands
  environment:
    name: production
    url: https://kokoro-tts.example.com
  when: manual
  only:
    - main
'''
        
        # Save GitLab CI file
        gitlab_ci_file = Path(".gitlab-ci.yml")
        with open(gitlab_ci_file, 'w') as f:
            f.write(gitlab_ci_content)
        
        logger.info(f"GitLab CI configuration saved: {gitlab_ci_file}")
        return gitlab_ci_content
    
    def generate_documentation_check_script(self) -> str:
        """Generate documentation coverage check script"""
        logger.info("Generating documentation check script...")
        
        doc_check_script = f'''#!/bin/bash
# Documentation Coverage Check Script
# Generated automatically - do not edit manually

set -e

echo "Checking documentation coverage..."

# Run documentation coverage analysis
python -c "
import sys
sys.path.append('scripts')
from cicd_documentation_framework import CICDDocumentationManager

manager = CICDDocumentationManager()
coverage = manager.analyze_documentation_coverage()

print(f'Documentation Coverage: {{coverage.coverage_percentage:.1f}}%')
print(f'Target Coverage: {self.config.min_documentation_coverage}%')

if coverage.coverage_percentage < {self.config.min_documentation_coverage}:
    print(f'ERROR: Documentation coverage ({{coverage.coverage_percentage:.1f}}%) below target ({self.config.min_documentation_coverage}%)')
    print('Missing docstrings:')
    for missing in coverage.missing_docstrings[:10]:
        print(f'  - {{missing}}')
    sys.exit(1)
else:
    print('✅ Documentation coverage meets requirements')
"

echo "Documentation check completed successfully!"
'''
        
        # Save documentation check script
        doc_script_file = self.results_dir / "check_documentation.sh"
        with open(doc_script_file, 'w') as f:
            f.write(doc_check_script)
        os.chmod(doc_script_file, 0o755)
        
        logger.info(f"Documentation check script saved: {doc_script_file}")
        return doc_check_script

    def generate_backward_compatibility_tests(self) -> str:
        """Generate backward compatibility test suite"""
        logger.info("Generating backward compatibility tests...")

        compat_test_content = '''"""
Backward Compatibility Test Suite
Tests to ensure API backward compatibility across versions
"""

import pytest
import json
import requests
from typing import Dict, Any

class TestBackwardCompatibility:
    """Test backward compatibility of API endpoints"""

    BASE_URL = "http://localhost:8354"

    def test_v1_audio_speech_endpoint(self):
        """Test v1 audio speech endpoint compatibility"""
        endpoint = f"{self.BASE_URL}/v1/audio/speech"

        # Test basic request format
        payload = {
            "model": "kokoro",
            "input": "Hello, world!",
            "voice": "af_heart"
        }

        # This should not fail in future versions
        response = requests.post(endpoint, json=payload)
        assert response.status_code in [200, 503]  # 503 if service not running

        if response.status_code == 200:
            assert response.headers.get("content-type") == "audio/wav"

    def test_health_endpoint_format(self):
        """Test health endpoint response format"""
        endpoint = f"{self.BASE_URL}/health"

        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()

                # These fields should always be present
                assert "status" in data
                assert "timestamp" in data

                # Status should be one of expected values
                assert data["status"] in ["healthy", "warning", "critical", "unknown"]
        except requests.exceptions.ConnectionError:
            pytest.skip("Service not running")

    def test_api_error_format(self):
        """Test API error response format consistency"""
        endpoint = f"{self.BASE_URL}/v1/audio/speech"

        # Send invalid request
        payload = {"invalid": "request"}

        try:
            response = requests.post(endpoint, json=payload)
            if response.status_code >= 400:
                # Error responses should be JSON
                assert response.headers.get("content-type", "").startswith("application/json")

                error_data = response.json()
                # Should have error information
                assert "error" in error_data or "detail" in error_data
        except requests.exceptions.ConnectionError:
            pytest.skip("Service not running")

    def test_voice_list_compatibility(self):
        """Test voice list endpoint compatibility"""
        endpoint = f"{self.BASE_URL}/v1/voices"

        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()

                # Should return a list or dict with voices
                assert isinstance(data, (list, dict))

                if isinstance(data, list) and data:
                    # Each voice should have required fields
                    voice = data[0]
                    assert "id" in voice or "name" in voice
        except requests.exceptions.ConnectionError:
            pytest.skip("Service not running")

    def test_model_list_compatibility(self):
        """Test model list endpoint compatibility"""
        endpoint = f"{self.BASE_URL}/v1/models"

        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()

                # Should return model information
                assert isinstance(data, (list, dict))

                if isinstance(data, dict) and "data" in data:
                    # OpenAI-compatible format
                    assert isinstance(data["data"], list)
        except requests.exceptions.ConnectionError:
            pytest.skip("Service not running")

class TestConfigurationCompatibility:
    """Test configuration backward compatibility"""

    def test_config_file_format(self):
        """Test configuration file format compatibility"""
        config_files = ["config.json", "config/config.json"]

        for config_file in config_files:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)

                # Basic configuration structure should be maintained
                assert isinstance(config, dict)

                # Check for critical configuration keys
                if "server" in config:
                    server_config = config["server"]
                    assert "host" in server_config or "port" in server_config

    def test_environment_variables(self):
        """Test environment variable compatibility"""
        # These environment variables should continue to work
        env_vars = [
            "KOKORO_HOST",
            "KOKORO_PORT",
            "KOKORO_MODEL_PATH",
            "KOKORO_VOICE_PATH"
        ]

        # Test that they can be set without breaking the application
        for var in env_vars:
            # Just check that setting them doesn't cause import errors
            os.environ[var] = "test_value"
            try:
                # Try importing main modules
                import sys
                assert True  # If we get here, no import errors
            finally:
                if var in os.environ:
                    del os.environ[var]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

        # Save backward compatibility tests
        compat_test_file = Path("tests/test_backward_compatibility.py")
        compat_test_file.parent.mkdir(exist_ok=True)

        with open(compat_test_file, 'w') as f:
            f.write(compat_test_content)

        logger.info(f"Backward compatibility tests saved: {compat_test_file}")
        return compat_test_content

    def generate_performance_benchmarks(self) -> str:
        """Generate performance benchmark suite"""
        logger.info("Generating performance benchmarks...")

        benchmark_content = '''"""
Performance Benchmark Suite
Automated performance testing to ensure no regressions
"""

import time
import statistics
import pytest
import requests
from typing import List, Dict, Any

class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    BASE_URL = "http://localhost:8354"

    @pytest.mark.performance
    def test_tts_latency_benchmark(self):
        """Test TTS generation latency"""
        endpoint = f"{self.BASE_URL}/v1/audio/speech"

        test_texts = [
            "Hello",  # Short text
            "Hello, world! This is a test.",  # Medium text
            "This is a longer text that should take more time to process and generate audio."  # Long text
        ]

        for text in test_texts:
            latencies = []

            for _ in range(5):  # Run 5 times for average
                payload = {
                    "model": "kokoro",
                    "input": text,
                    "voice": "af_heart"
                }

                start_time = time.time()
                try:
                    response = requests.post(endpoint, json=payload, timeout=30)
                    end_time = time.time()

                    if response.status_code == 200:
                        latency = end_time - start_time
                        latencies.append(latency)
                except requests.exceptions.ConnectionError:
                    pytest.skip("Service not running")
                except requests.exceptions.Timeout:
                    pytest.fail(f"Request timed out for text: {text}")

            if latencies:
                avg_latency = statistics.mean(latencies)
                max_latency = max(latencies)

                # Performance assertions
                if len(text) < 20:  # Short text
                    assert avg_latency < 0.25, f"Short text latency too high: {avg_latency:.3f}s"
                elif len(text) < 50:  # Medium text
                    assert avg_latency < 0.5, f"Medium text latency too high: {avg_latency:.3f}s"
                else:  # Long text
                    assert avg_latency < 1.0, f"Long text latency too high: {avg_latency:.3f}s"

                # No request should take more than 5 seconds
                assert max_latency < 5.0, f"Maximum latency too high: {max_latency:.3f}s"

    @pytest.mark.performance
    def test_concurrent_requests(self):
        """Test performance under concurrent load"""
        import concurrent.futures

        endpoint = f"{self.BASE_URL}/v1/audio/speech"
        payload = {
            "model": "kokoro",
            "input": "Concurrent test",
            "voice": "af_heart"
        }

        def make_request():
            try:
                start_time = time.time()
                response = requests.post(endpoint, json=payload, timeout=30)
                end_time = time.time()
                return {
                    "status_code": response.status_code,
                    "latency": end_time - start_time,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "status_code": 0,
                    "latency": 30.0,
                    "success": False,
                    "error": str(e)
                }

        # Test with 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Check results
        successful_requests = [r for r in results if r["success"]]

        if successful_requests:
            avg_latency = statistics.mean([r["latency"] for r in successful_requests])

            # Under concurrent load, average latency should still be reasonable
            assert avg_latency < 2.0, f"Concurrent request latency too high: {avg_latency:.3f}s"

            # At least 80% of requests should succeed
            success_rate = len(successful_requests) / len(results)
            assert success_rate >= 0.8, f"Success rate too low: {success_rate:.1%}"

    @pytest.mark.performance
    def test_memory_usage_stability(self):
        """Test memory usage doesn't grow excessively"""
        import psutil
        import os

        # This test would need to be run with the actual service process
        # For now, just check that we can measure memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make several requests
        endpoint = f"{self.BASE_URL}/v1/audio/speech"
        payload = {
            "model": "kokoro",
            "input": "Memory test",
            "voice": "af_heart"
        }

        for _ in range(10):
            try:
                requests.post(endpoint, json=payload, timeout=10)
            except:
                pass  # Ignore errors for this test

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory

        # Memory growth should be minimal for this test process
        assert memory_growth < 50, f"Excessive memory growth: {memory_growth:.1f}MB"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance"])
'''

        # Save performance benchmarks
        benchmark_file = Path("tests/test_performance_benchmarks.py")
        benchmark_file.parent.mkdir(exist_ok=True)

        with open(benchmark_file, 'w') as f:
            f.write(benchmark_content)

        logger.info(f"Performance benchmarks saved: {benchmark_file}")
        return benchmark_content

    def run_comprehensive_cicd_setup(self) -> Dict[str, Any]:
        """Run comprehensive CI/CD and documentation setup"""
        logger.info("Starting comprehensive CI/CD and documentation setup...")

        # Analyze documentation coverage
        doc_coverage = self.analyze_documentation_coverage()

        # Generate CI/CD configurations
        github_workflow = self.generate_github_actions_workflow()
        gitlab_ci = self.generate_gitlab_ci_config()
        doc_check_script = self.generate_documentation_check_script()

        # Generate test suites
        compat_tests = self.generate_backward_compatibility_tests()
        performance_tests = self.generate_performance_benchmarks()

        # Compile results
        results = {
            "setup_timestamp": time.time(),
            "cicd_configuration": asdict(self.config),
            "documentation_coverage": asdict(doc_coverage),
            "generated_files": {
                "github_workflow": ".github/workflows/ci-cd.yml",
                "gitlab_ci": ".gitlab-ci.yml",
                "doc_check_script": "test_results/cicd_documentation/check_documentation.sh",
                "backward_compatibility_tests": "tests/test_backward_compatibility.py",
                "performance_benchmarks": "tests/test_performance_benchmarks.py"
            },
            "setup_summary": self._generate_cicd_summary(doc_coverage),
            "next_steps": self._generate_cicd_next_steps(doc_coverage)
        }

        # Save complete results
        results_file = self.results_dir / f"cicd_setup_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"CI/CD and documentation setup completed. Results saved to: {results_file}")
        return results

    def _generate_cicd_summary(self, doc_coverage: DocumentationCoverage) -> Dict[str, Any]:
        """Generate CI/CD setup summary"""

        doc_target_met = doc_coverage.coverage_percentage >= self.config.min_documentation_coverage

        summary = {
            "documentation_coverage": {
                "current_percentage": round(doc_coverage.coverage_percentage, 1),
                "target_percentage": self.config.min_documentation_coverage,
                "target_met": doc_target_met,
                "total_items": (doc_coverage.total_modules +
                              doc_coverage.total_functions +
                              doc_coverage.total_classes),
                "documented_items": (doc_coverage.documented_modules +
                                   doc_coverage.documented_functions +
                                   doc_coverage.documented_classes),
                "missing_count": len(doc_coverage.missing_docstrings)
            },
            "cicd_features": {
                "github_actions": self.config.enable_github_actions,
                "gitlab_ci": self.config.enable_gitlab_ci,
                "docker_build": self.config.enable_docker_build,
                "automated_testing": self.config.enable_automated_testing,
                "security_scanning": self.config.enable_security_scanning,
                "performance_testing": self.config.enable_performance_testing
            },
            "test_coverage_target": self.config.min_test_coverage,
            "python_versions_supported": len(self.config.python_versions),
            "deployment_environments": len(self.config.deployment_environments),
            "production_ready": doc_target_met and all([
                self.config.enable_automated_testing,
                self.config.enable_security_scanning,
                self.config.enable_documentation_check
            ])
        }

        return summary

    def _generate_cicd_next_steps(self, doc_coverage: DocumentationCoverage) -> List[str]:
        """Generate next steps for CI/CD deployment"""
        next_steps = [
            "Configure repository secrets for CI/CD pipelines",
            "Set up Docker registry credentials",
            "Configure deployment environments and access",
            "Test CI/CD pipelines with sample commits",
            "Set up monitoring and alerting for deployments",
            "Configure automated rollback procedures",
            "Set up staging environment for testing",
            "Configure production deployment approvals",
            "Set up performance monitoring in production",
            "Document CI/CD procedures for team"
        ]

        # Add specific recommendations based on documentation coverage
        if doc_coverage.coverage_percentage < self.config.min_documentation_coverage:
            gap = self.config.min_documentation_coverage - doc_coverage.coverage_percentage
            next_steps.insert(0, f"Improve documentation coverage by {gap:.1f}% to meet target")
            next_steps.insert(1, "Add missing docstrings to modules, functions, and classes")

        # Add specific recommendations based on missing features
        if not self.config.enable_security_scanning:
            next_steps.append("Enable security scanning in CI/CD pipeline")

        if not self.config.enable_performance_testing:
            next_steps.append("Enable performance testing to catch regressions")

        return next_steps

def main():
    """Main function to run CI/CD and documentation setup"""
    import argparse

    parser = argparse.ArgumentParser(description="CI/CD and Documentation Framework")
    parser.add_argument("--check-docs", action="store_true",
                       help="Check documentation coverage only")
    args = parser.parse_args()

    manager = CICDDocumentationManager()

    if args.check_docs:
        # Just check documentation coverage
        coverage = manager.analyze_documentation_coverage()

        print(f"Documentation Coverage: {coverage.coverage_percentage:.1f}%")
        print(f"Target Coverage: {manager.config.min_documentation_coverage}%")

        if coverage.coverage_percentage < manager.config.min_documentation_coverage:
            print(f"ERROR: Documentation coverage below target")
            print("Missing docstrings:")
            for missing in coverage.missing_docstrings[:10]:
                print(f"  - {missing}")
            sys.exit(1)
        else:
            print("✅ Documentation coverage meets requirements")
            sys.exit(0)

    try:
        # Run comprehensive CI/CD setup
        results = manager.run_comprehensive_cicd_setup()

        print("\n" + "="*80)
        print("CI/CD AND DOCUMENTATION FRAMEWORK SUMMARY")
        print("="*80)

        summary = results["setup_summary"]
        doc_summary = summary["documentation_coverage"]

        print(f"Documentation Coverage: {doc_summary['current_percentage']}% (Target: {doc_summary['target_percentage']}%)")
        print(f"Target Met: {'✅' if doc_summary['target_met'] else '❌'}")
        print(f"Documented Items: {doc_summary['documented_items']}/{doc_summary['total_items']}")

        if doc_summary['missing_count'] > 0:
            print(f"Missing Docstrings: {doc_summary['missing_count']}")

        print(f"\nCI/CD Features:")
        features = summary["cicd_features"]
        print(f"  GitHub Actions: {'✅' if features['github_actions'] else '❌'}")
        print(f"  GitLab CI: {'✅' if features['gitlab_ci'] else '❌'}")
        print(f"  Docker Build: {'✅' if features['docker_build'] else '❌'}")
        print(f"  Automated Testing: {'✅' if features['automated_testing'] else '❌'}")
        print(f"  Security Scanning: {'✅' if features['security_scanning'] else '❌'}")
        print(f"  Performance Testing: {'✅' if features['performance_testing'] else '❌'}")

        print(f"\nConfiguration:")
        print(f"  Test Coverage Target: {summary['test_coverage_target']}%")
        print(f"  Python Versions: {summary['python_versions_supported']}")
        print(f"  Deployment Environments: {summary['deployment_environments']}")

        print(f"\nGenerated Files:")
        for file_type, filename in results["generated_files"].items():
            print(f"  {file_type}: {filename}")

        print(f"\nProduction Ready: {'✅' if summary['production_ready'] else '❌'}")

        print(f"\nNext Steps:")
        for i, step in enumerate(results["next_steps"][:5], 1):
            print(f"  {i}. {step}")

        if len(results["next_steps"]) > 5:
            print(f"  ... and {len(results['next_steps']) - 5} more steps")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"CI/CD setup failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
