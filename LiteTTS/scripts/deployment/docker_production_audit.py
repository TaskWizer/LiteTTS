#!/usr/bin/env python3
"""
Docker Production Readiness Audit
Review port conflicts, build warnings, deprecation fixes, Python version alignment, security best practices
"""

import os
import sys
import json
import logging
import subprocess
import re
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
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
class DockerAuditIssue:
    """Docker audit issue"""
    category: str
    severity: str  # critical, high, medium, low
    issue: str
    description: str
    recommendation: str
    file_path: str = ""
    line_number: int = 0

@dataclass
class DockerAuditResult:
    """Docker audit result"""
    audit_timestamp: float
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    issues_by_category: Dict[str, int]
    detailed_issues: List[DockerAuditIssue]
    recommendations: List[str]
    production_readiness_score: float

class DockerProductionAuditor:
    """Docker production readiness auditor"""
    
    def __init__(self):
        self.results_dir = Path("test_results/docker_audit")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Docker files to audit
        self.docker_files = [
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml",
            ".dockerignore"
        ]
        
        # Issues found during audit
        self.issues = []
        
    def audit_dockerfile(self, dockerfile_path: Path) -> List[DockerAuditIssue]:
        """Audit Dockerfile for production readiness"""
        logger.info(f"Auditing Dockerfile: {dockerfile_path}")
        
        if not dockerfile_path.exists():
            return [DockerAuditIssue(
                category="missing_files",
                severity="critical",
                issue="Dockerfile not found",
                description="No Dockerfile found in the project root",
                recommendation="Create a production-ready Dockerfile",
                file_path=str(dockerfile_path)
            )]
        
        issues = []
        
        try:
            with open(dockerfile_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check Python version
            python_version_issues = self._check_python_version(lines, str(dockerfile_path))
            issues.extend(python_version_issues)
            
            # Check base image security
            base_image_issues = self._check_base_image_security(lines, str(dockerfile_path))
            issues.extend(base_image_issues)
            
            # Check user privileges
            user_issues = self._check_user_privileges(lines, str(dockerfile_path))
            issues.extend(user_issues)
            
            # Check port configuration
            port_issues = self._check_port_configuration(lines, str(dockerfile_path))
            issues.extend(port_issues)
            
            # Check build optimization
            build_issues = self._check_build_optimization(lines, str(dockerfile_path))
            issues.extend(build_issues)
            
            # Check security practices
            security_issues = self._check_security_practices(lines, str(dockerfile_path))
            issues.extend(security_issues)
            
        except Exception as e:
            issues.append(DockerAuditIssue(
                category="file_errors",
                severity="high",
                issue="Dockerfile read error",
                description=f"Error reading Dockerfile: {str(e)}",
                recommendation="Fix Dockerfile syntax and permissions",
                file_path=str(dockerfile_path)
            ))
        
        return issues
    
    def _check_python_version(self, lines: List[str], file_path: str) -> List[DockerAuditIssue]:
        """Check Python version alignment"""
        issues = []
        
        python_version_found = False
        recommended_version = "3.12"
        
        for i, line in enumerate(lines):
            if line.strip().startswith('FROM python:'):
                python_version_found = True
                
                # Extract version
                version_match = re.search(r'python:(\d+\.\d+)', line)
                if version_match:
                    version = version_match.group(1)
                    if version != recommended_version:
                        issues.append(DockerAuditIssue(
                            category="python_version",
                            severity="medium",
                            issue=f"Python version mismatch: {version}",
                            description=f"Using Python {version} instead of recommended {recommended_version}",
                            recommendation=f"Update to Python {recommended_version} for better performance and security",
                            file_path=file_path,
                            line_number=i + 1
                        ))
                else:
                    issues.append(DockerAuditIssue(
                        category="python_version",
                        severity="medium",
                        issue="Python version not specified",
                        description="Python version not explicitly specified in base image",
                        recommendation=f"Use python:{recommended_version}-slim for production",
                        file_path=file_path,
                        line_number=i + 1
                    ))
        
        if not python_version_found:
            issues.append(DockerAuditIssue(
                category="python_version",
                severity="high",
                issue="Python base image not found",
                description="No Python base image detected",
                recommendation="Use official Python base image",
                file_path=file_path
            ))
        
        return issues
    
    def _check_base_image_security(self, lines: List[str], file_path: str) -> List[DockerAuditIssue]:
        """Check base image security practices"""
        issues = []
        
        for i, line in enumerate(lines):
            if line.strip().startswith('FROM'):
                # Check for latest tag
                if ':latest' in line or not ':' in line.split()[-1]:
                    issues.append(DockerAuditIssue(
                        category="security",
                        severity="high",
                        issue="Using 'latest' tag or no tag",
                        description="Base image uses 'latest' tag which is not reproducible",
                        recommendation="Pin to specific version tag for reproducible builds",
                        file_path=file_path,
                        line_number=i + 1
                    ))
                
                # Check for slim/alpine variants
                if 'slim' not in line and 'alpine' not in line:
                    issues.append(DockerAuditIssue(
                        category="optimization",
                        severity="medium",
                        issue="Not using minimal base image",
                        description="Using full base image instead of slim variant",
                        recommendation="Use python:3.12-slim for smaller image size",
                        file_path=file_path,
                        line_number=i + 1
                    ))
        
        return issues
    
    def _check_user_privileges(self, lines: List[str], file_path: str) -> List[DockerAuditIssue]:
        """Check user privilege configuration"""
        issues = []
        
        user_found = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('USER'):
                user_found = True
                user = line.strip().split()[-1]
                if user == 'root' or user == '0':
                    issues.append(DockerAuditIssue(
                        category="security",
                        severity="critical",
                        issue="Running as root user",
                        description="Container runs as root user, which is a security risk",
                        recommendation="Create and use non-root user for running the application",
                        file_path=file_path,
                        line_number=i + 1
                    ))
        
        if not user_found:
            issues.append(DockerAuditIssue(
                category="security",
                severity="high",
                issue="No USER directive found",
                description="Container will run as root by default",
                recommendation="Add USER directive to run as non-root user",
                file_path=file_path
            ))
        
        return issues
    
    def _check_port_configuration(self, lines: List[str], file_path: str) -> List[DockerAuditIssue]:
        """Check port configuration"""
        issues = []
        
        exposed_ports = []
        
        for i, line in enumerate(lines):
            if line.strip().startswith('EXPOSE'):
                port_match = re.findall(r'\d+', line)
                if port_match:
                    exposed_ports.extend(port_match)
        
        # Check for common port conflicts
        common_ports = ['80', '443', '22', '21', '25', '53', '110', '143', '993', '995']
        for port in exposed_ports:
            if port in common_ports:
                issues.append(DockerAuditIssue(
                    category="port_conflicts",
                    severity="medium",
                    issue=f"Using common system port: {port}",
                    description=f"Port {port} is commonly used by system services",
                    recommendation="Use non-standard ports to avoid conflicts",
                    file_path=file_path
                ))
        
        # Check for privileged ports
        for port in exposed_ports:
            if int(port) < 1024:
                issues.append(DockerAuditIssue(
                    category="security",
                    severity="medium",
                    issue=f"Using privileged port: {port}",
                    description=f"Port {port} requires root privileges",
                    recommendation="Use ports > 1024 for non-root users",
                    file_path=file_path
                ))
        
        return issues
    
    def _check_build_optimization(self, lines: List[str], file_path: str) -> List[DockerAuditIssue]:
        """Check build optimization practices"""
        issues = []
        
        # Check for layer optimization
        run_commands = [i for i, line in enumerate(lines) if line.strip().startswith('RUN')]
        if len(run_commands) > 5:
            issues.append(DockerAuditIssue(
                category="optimization",
                severity="medium",
                issue="Too many RUN commands",
                description=f"Found {len(run_commands)} RUN commands, which creates many layers",
                recommendation="Combine RUN commands to reduce image layers",
                file_path=file_path
            ))
        
        # Check for cache optimization
        copy_before_install = False
        for i, line in enumerate(lines):
            if line.strip().startswith('COPY') and ('requirements' in line or 'pyproject' in line):
                copy_before_install = True
                break
            elif line.strip().startswith('RUN') and ('pip install' in line or 'uv' in line):
                if not copy_before_install:
                    issues.append(DockerAuditIssue(
                        category="optimization",
                        severity="low",
                        issue="Dependencies not cached efficiently",
                        description="Requirements file not copied before installation",
                        recommendation="Copy requirements file first to leverage Docker cache",
                        file_path=file_path,
                        line_number=i + 1
                    ))
                break
        
        return issues
    
    def _check_security_practices(self, lines: List[str], file_path: str) -> List[DockerAuditIssue]:
        """Check security best practices"""
        issues = []
        
        # Check for secrets in Dockerfile
        for i, line in enumerate(lines):
            # Check for potential secrets
            secret_patterns = [
                r'password\s*=\s*["\'].*["\']',
                r'token\s*=\s*["\'].*["\']',
                r'key\s*=\s*["\'].*["\']',
                r'secret\s*=\s*["\'].*["\']'
            ]
            
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(DockerAuditIssue(
                        category="security",
                        severity="critical",
                        issue="Potential secret in Dockerfile",
                        description="Hardcoded credentials detected in Dockerfile",
                        recommendation="Use environment variables or Docker secrets",
                        file_path=file_path,
                        line_number=i + 1
                    ))
        
        # Check for package manager cache cleanup
        cache_cleanup_found = False
        for line in lines:
            if 'rm -rf' in line and ('/var/lib/apt/lists/*' in line or '/tmp/*' in line):
                cache_cleanup_found = True
                break
        
        if not cache_cleanup_found:
            issues.append(DockerAuditIssue(
                category="optimization",
                severity="low",
                issue="Package manager cache not cleaned",
                description="Package manager cache not cleaned up",
                recommendation="Add cache cleanup to reduce image size",
                file_path=file_path
            ))
        
        return issues
    
    def audit_docker_compose(self, compose_path: Path) -> List[DockerAuditIssue]:
        """Audit docker-compose file for production readiness"""
        logger.info(f"Auditing docker-compose: {compose_path}")
        
        if not compose_path.exists():
            return []  # Not required, so no issues if missing
        
        issues = []
        
        try:
            with open(compose_path, 'r') as f:
                if compose_path.suffix == '.yml' or compose_path.suffix == '.yaml':
                    if not YAML_AVAILABLE:
                        issues.append(DockerAuditIssue(
                            category="environment",
                            severity="medium",
                            issue="YAML module not available",
                            description="Cannot parse docker-compose file without PyYAML",
                            recommendation="Install PyYAML: pip install PyYAML",
                            file_path=str(compose_path)
                        ))
                        return issues
                    compose_data = yaml.safe_load(f)
                else:
                    return []
            
            # Check version
            if 'version' not in compose_data:
                issues.append(DockerAuditIssue(
                    category="configuration",
                    severity="medium",
                    issue="Docker Compose version not specified",
                    description="Docker Compose version not specified",
                    recommendation="Specify Docker Compose version for compatibility",
                    file_path=str(compose_path)
                ))
            
            # Check services
            if 'services' in compose_data:
                for service_name, service_config in compose_data['services'].items():
                    service_issues = self._check_compose_service(service_name, service_config, str(compose_path))
                    issues.extend(service_issues)
            
        except Exception as e:
            issues.append(DockerAuditIssue(
                category="file_errors",
                severity="high",
                issue="Docker Compose read error",
                description=f"Error reading docker-compose file: {str(e)}",
                recommendation="Fix docker-compose syntax",
                file_path=str(compose_path)
            ))
        
        return issues
    
    def _check_compose_service(self, service_name: str, service_config: Dict[str, Any], file_path: str) -> List[DockerAuditIssue]:
        """Check individual service configuration"""
        issues = []
        
        # Check restart policy
        if 'restart' not in service_config:
            issues.append(DockerAuditIssue(
                category="reliability",
                severity="medium",
                issue=f"No restart policy for service '{service_name}'",
                description="Service has no restart policy configured",
                recommendation="Add restart policy (e.g., 'unless-stopped') for production",
                file_path=file_path
            ))
        
        # Check resource limits
        if 'deploy' not in service_config or 'resources' not in service_config.get('deploy', {}):
            issues.append(DockerAuditIssue(
                category="resource_management",
                severity="medium",
                issue=f"No resource limits for service '{service_name}'",
                description="Service has no CPU/memory limits",
                recommendation="Add resource limits to prevent resource exhaustion",
                file_path=file_path
            ))
        
        # Check health checks
        if 'healthcheck' not in service_config:
            issues.append(DockerAuditIssue(
                category="monitoring",
                severity="low",
                issue=f"No health check for service '{service_name}'",
                description="Service has no health check configured",
                recommendation="Add health check for better monitoring",
                file_path=file_path
            ))
        
        return issues
    
    def check_dockerignore(self, dockerignore_path: Path) -> List[DockerAuditIssue]:
        """Check .dockerignore file"""
        logger.info("Checking .dockerignore file...")
        
        issues = []
        
        if not dockerignore_path.exists():
            issues.append(DockerAuditIssue(
                category="optimization",
                severity="medium",
                issue=".dockerignore file missing",
                description="No .dockerignore file found",
                recommendation="Create .dockerignore to exclude unnecessary files",
                file_path=str(dockerignore_path)
            ))
            return issues
        
        try:
            with open(dockerignore_path, 'r') as f:
                content = f.read()
            
            # Check for common exclusions
            recommended_exclusions = [
                '.git',
                '*.md',
                'Dockerfile*',
                '.dockerignore',
                'node_modules',
                '__pycache__',
                '*.pyc',
                '.pytest_cache',
                '.coverage',
                'test_results'
            ]
            
            missing_exclusions = []
            for exclusion in recommended_exclusions:
                if exclusion not in content:
                    missing_exclusions.append(exclusion)
            
            if missing_exclusions:
                issues.append(DockerAuditIssue(
                    category="optimization",
                    severity="low",
                    issue="Missing recommended .dockerignore entries",
                    description=f"Missing exclusions: {', '.join(missing_exclusions)}",
                    recommendation="Add recommended exclusions to reduce build context",
                    file_path=str(dockerignore_path)
                ))
        
        except Exception as e:
            issues.append(DockerAuditIssue(
                category="file_errors",
                severity="low",
                issue=".dockerignore read error",
                description=f"Error reading .dockerignore: {str(e)}",
                recommendation="Fix .dockerignore file permissions",
                file_path=str(dockerignore_path)
            ))
        
        return issues

    def run_comprehensive_docker_audit(self) -> DockerAuditResult:
        """Run comprehensive Docker production readiness audit"""
        logger.info("Starting comprehensive Docker production audit...")

        all_issues = []

        # Audit Dockerfile
        dockerfile_path = Path("Dockerfile")
        dockerfile_issues = self.audit_dockerfile(dockerfile_path)
        all_issues.extend(dockerfile_issues)

        # Audit docker-compose files
        for compose_file in ["docker-compose.yml", "docker-compose.yaml"]:
            compose_path = Path(compose_file)
            compose_issues = self.audit_docker_compose(compose_path)
            all_issues.extend(compose_issues)

        # Check .dockerignore
        dockerignore_path = Path(".dockerignore")
        dockerignore_issues = self.check_dockerignore(dockerignore_path)
        all_issues.extend(dockerignore_issues)

        # Additional security checks
        security_issues = self._run_security_checks()
        all_issues.extend(security_issues)

        # Categorize issues
        issues_by_category = {}
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for issue in all_issues:
            # Count by category
            if issue.category not in issues_by_category:
                issues_by_category[issue.category] = 0
            issues_by_category[issue.category] += 1

            # Count by severity
            severity_counts[issue.severity] += 1

        # Calculate production readiness score
        production_score = self._calculate_production_readiness_score(severity_counts, len(all_issues))

        # Generate recommendations
        recommendations = self._generate_production_recommendations(all_issues, severity_counts)

        # Create audit result
        result = DockerAuditResult(
            audit_timestamp=time.time(),
            total_issues=len(all_issues),
            critical_issues=severity_counts["critical"],
            high_issues=severity_counts["high"],
            medium_issues=severity_counts["medium"],
            low_issues=severity_counts["low"],
            issues_by_category=issues_by_category,
            detailed_issues=all_issues,
            recommendations=recommendations,
            production_readiness_score=production_score
        )

        # Save results
        results_file = self.results_dir / f"docker_audit_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)

        logger.info(f"Docker audit completed. Results saved to: {results_file}")
        return result

    def _run_security_checks(self) -> List[DockerAuditIssue]:
        """Run additional security checks"""
        issues = []

        # Check for Docker daemon security
        try:
            # Check if Docker is running
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                issues.append(DockerAuditIssue(
                    category="environment",
                    severity="high",
                    issue="Docker not available",
                    description="Docker daemon not running or not installed",
                    recommendation="Install and start Docker daemon"
                ))
        except Exception:
            issues.append(DockerAuditIssue(
                category="environment",
                severity="medium",
                issue="Cannot verify Docker installation",
                description="Unable to check Docker installation status",
                recommendation="Verify Docker is properly installed"
            ))

        return issues

    def _calculate_production_readiness_score(self, severity_counts: Dict[str, int], total_issues: int) -> float:
        """Calculate production readiness score (0-100)"""
        if total_issues == 0:
            return 100.0

        # Weight different severities
        weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}

        weighted_score = 0
        for severity, count in severity_counts.items():
            weighted_score += count * weights[severity]

        # Calculate score (lower weighted score = higher readiness)
        max_possible_score = total_issues * weights["critical"]
        readiness_score = max(0, 100 - (weighted_score / max_possible_score * 100))

        return round(readiness_score, 1)

    def _generate_production_recommendations(self, issues: List[DockerAuditIssue],
                                           severity_counts: Dict[str, int]) -> List[str]:
        """Generate production readiness recommendations"""
        recommendations = []

        # Critical issues first
        if severity_counts["critical"] > 0:
            recommendations.append(f"Address {severity_counts['critical']} critical security issues immediately")

        # High priority issues
        if severity_counts["high"] > 0:
            recommendations.append(f"Resolve {severity_counts['high']} high-priority issues before production deployment")

        # Category-specific recommendations
        categories = {}
        for issue in issues:
            if issue.category not in categories:
                categories[issue.category] = []
            categories[issue.category].append(issue)

        for category, category_issues in categories.items():
            if len(category_issues) >= 3:
                recommendations.append(f"Focus on {category} improvements: {len(category_issues)} issues found")

        # General recommendations
        if severity_counts["critical"] == 0 and severity_counts["high"] <= 2:
            recommendations.append("Consider implementing automated security scanning in CI/CD pipeline")

        recommendations.append("Regularly update base images and dependencies")
        recommendations.append("Implement container image vulnerability scanning")
        recommendations.append("Use multi-stage builds to reduce final image size")

        return recommendations

import time

def main():
    """Main function to run Docker production audit"""
    auditor = DockerProductionAuditor()

    try:
        # Run comprehensive audit
        result = auditor.run_comprehensive_docker_audit()

        print("\n" + "="*80)
        print("DOCKER PRODUCTION READINESS AUDIT SUMMARY")
        print("="*80)

        print(f"Production Readiness Score: {result.production_readiness_score}/100")
        print(f"Total Issues Found: {result.total_issues}")

        print(f"\nIssues by Severity:")
        print(f"  Critical: {result.critical_issues}")
        print(f"  High: {result.high_issues}")
        print(f"  Medium: {result.medium_issues}")
        print(f"  Low: {result.low_issues}")

        print(f"\nIssues by Category:")
        for category, count in result.issues_by_category.items():
            print(f"  {category}: {count}")

        print(f"\nCritical Issues:")
        critical_issues = [issue for issue in result.detailed_issues if issue.severity == "critical"]
        if critical_issues:
            for issue in critical_issues:
                print(f"  - {issue.issue}: {issue.description}")
        else:
            print("  None found ✅")

        print(f"\nRecommendations:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"Docker audit failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
