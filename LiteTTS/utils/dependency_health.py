#!/usr/bin/env python3
"""
Dependency Health Monitoring and Recovery System

Provides startup validation, runtime monitoring, and automatic recovery
for dependencies in the LiteTTS system.
"""

import sys
import importlib
import subprocess
import logging
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DependencyStatus(Enum):
    """Dependency status enumeration"""
    HEALTHY = "healthy"
    MISSING = "missing"
    OUTDATED = "outdated"
    CORRUPTED = "corrupted"
    RECOVERING = "recovering"
    FAILED = "failed"


@dataclass
class DependencyInfo:
    """Information about a dependency"""
    name: str
    required: bool
    min_version: Optional[str] = None
    import_name: Optional[str] = None
    description: str = ""
    recovery_command: Optional[str] = None
    health_check: Optional[Callable] = None


@dataclass
class HealthCheckResult:
    """Result of a dependency health check"""
    dependency: str
    status: DependencyStatus
    version: Optional[str] = None
    error_message: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False


class DependencyHealth:
    """
    Dependency health monitoring and recovery system.
    
    Provides functionality to validate dependencies at startup,
    monitor them at runtime, and attempt automatic recovery.
    """
    
    def __init__(self):
        """Initialize dependency health monitor"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Define core dependencies
        self.dependencies = {
            # Core required dependencies
            "torch": DependencyInfo(
                name="torch",
                required=True,
                min_version="1.9.0",
                description="PyTorch for neural network inference",
                recovery_command="uv add torch"
            ),
            "onnxruntime": DependencyInfo(
                name="onnxruntime",
                required=True,
                min_version="1.10.0",
                description="ONNX Runtime for model inference",
                recovery_command="uv add onnxruntime"
            ),
            "fastapi": DependencyInfo(
                name="fastapi",
                required=True,
                min_version="0.68.0",
                description="FastAPI web framework",
                recovery_command="uv add fastapi"
            ),
            "uvicorn": DependencyInfo(
                name="uvicorn",
                required=True,
                min_version="0.15.0",
                description="ASGI server for FastAPI",
                recovery_command="uv add uvicorn"
            ),
            "numpy": DependencyInfo(
                name="numpy",
                required=True,
                description="Numerical computing library",
                recovery_command="uv add numpy"
            ),
            "soundfile": DependencyInfo(
                name="soundfile",
                required=True,
                description="Audio file I/O library",
                recovery_command="uv add soundfile"
            ),
            
            # Optional dependencies
            "faster_whisper": DependencyInfo(
                name="faster-whisper",
                required=False,
                import_name="faster_whisper",
                description="Whisper STT for audio quality validation",
                recovery_command="uv add faster-whisper"
            ),
            "pydub": DependencyInfo(
                name="pydub",
                required=False,
                description="Audio processing library",
                recovery_command="uv add pydub"
            ),
            "websockets": DependencyInfo(
                name="websockets",
                required=False,
                description="WebSocket support for real-time communication",
                recovery_command="uv add websockets"
            ),
            "watchdog": DependencyInfo(
                name="watchdog",
                required=False,
                description="File system monitoring for hot reload",
                recovery_command="uv add watchdog"
            )
        }
        
        self.health_status = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        
        self.logger.info("DependencyHealth initialized")
    
    def check_dependency_health(self, dep_name: str) -> HealthCheckResult:
        """
        Check the health of a specific dependency.
        
        Args:
            dep_name: Name of the dependency to check
            
        Returns:
            HealthCheckResult with status and details
        """
        if dep_name not in self.dependencies:
            return HealthCheckResult(
                dependency=dep_name,
                status=DependencyStatus.FAILED,
                error_message=f"Unknown dependency: {dep_name}"
            )
        
        dep_info = self.dependencies[dep_name]
        import_name = dep_info.import_name or dep_name
        
        try:
            # Try to import the module
            module = importlib.import_module(import_name)
            
            # Get version if available
            version = None
            for attr in ['__version__', 'version', 'VERSION']:
                if hasattr(module, attr):
                    version = getattr(module, attr)
                    break
            
            # Check minimum version if specified
            if dep_info.min_version and version:
                try:
                    from packaging import version as pkg_version
                    if pkg_version.parse(str(version)) < pkg_version.parse(dep_info.min_version):
                        return HealthCheckResult(
                            dependency=dep_name,
                            status=DependencyStatus.OUTDATED,
                            version=str(version),
                            error_message=f"Version {version} < required {dep_info.min_version}"
                        )
                except ImportError:
                    # packaging not available, skip version check
                    pass
            
            # Run custom health check if provided
            if dep_info.health_check:
                try:
                    dep_info.health_check(module)
                except Exception as e:
                    return HealthCheckResult(
                        dependency=dep_name,
                        status=DependencyStatus.CORRUPTED,
                        version=str(version) if version else None,
                        error_message=f"Health check failed: {e}"
                    )
            
            return HealthCheckResult(
                dependency=dep_name,
                status=DependencyStatus.HEALTHY,
                version=str(version) if version else None
            )
            
        except ImportError as e:
            return HealthCheckResult(
                dependency=dep_name,
                status=DependencyStatus.MISSING,
                error_message=str(e)
            )
        except Exception as e:
            return HealthCheckResult(
                dependency=dep_name,
                status=DependencyStatus.CORRUPTED,
                error_message=str(e)
            )
    
    def validate_startup_dependencies(self) -> Dict[str, HealthCheckResult]:
        """
        Validate all dependencies at startup.
        
        Returns:
            Dictionary mapping dependency names to health check results
        """
        self.logger.info("Starting dependency validation...")
        
        results = {}
        critical_failures = []
        
        for dep_name, dep_info in self.dependencies.items():
            result = self.check_dependency_health(dep_name)
            results[dep_name] = result
            
            if result.status == DependencyStatus.HEALTHY:
                self.logger.debug(f"✅ {dep_name}: {result.status.value}")
            elif result.status == DependencyStatus.MISSING and dep_info.required:
                critical_failures.append(dep_name)
                self.logger.error(f"❌ {dep_name}: {result.error_message}")
            elif result.status != DependencyStatus.HEALTHY:
                self.logger.warning(f"⚠️ {dep_name}: {result.error_message}")
        
        if critical_failures:
            self.logger.critical(f"Critical dependencies missing: {', '.join(critical_failures)}")
            raise RuntimeError(f"Critical dependencies missing: {', '.join(critical_failures)}")
        
        self.health_status = results
        self.logger.info(f"Dependency validation completed: {len(results)} dependencies checked")
        
        return results
    
    def attempt_recovery(self, dep_name: str) -> HealthCheckResult:
        """
        Attempt to recover a failed dependency.
        
        Args:
            dep_name: Name of the dependency to recover
            
        Returns:
            HealthCheckResult after recovery attempt
        """
        if dep_name not in self.dependencies:
            return HealthCheckResult(
                dependency=dep_name,
                status=DependencyStatus.FAILED,
                error_message=f"Unknown dependency: {dep_name}"
            )
        
        dep_info = self.dependencies[dep_name]
        
        if not dep_info.recovery_command:
            return HealthCheckResult(
                dependency=dep_name,
                status=DependencyStatus.FAILED,
                error_message="No recovery command available",
                recovery_attempted=False
            )
        
        self.logger.info(f"Attempting recovery for {dep_name}...")
        
        try:
            # Execute recovery command
            result = subprocess.run(
                dep_info.recovery_command.split(),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.logger.info(f"Recovery command succeeded for {dep_name}")
                
                # Re-check health after recovery
                health_result = self.check_dependency_health(dep_name)
                health_result.recovery_attempted = True
                health_result.recovery_successful = (health_result.status == DependencyStatus.HEALTHY)
                
                if health_result.recovery_successful:
                    self.logger.info(f"✅ Recovery successful for {dep_name}")
                else:
                    self.logger.warning(f"⚠️ Recovery attempted but dependency still unhealthy: {dep_name}")
                
                return health_result
            else:
                self.logger.error(f"Recovery command failed for {dep_name}: {result.stderr}")
                return HealthCheckResult(
                    dependency=dep_name,
                    status=DependencyStatus.FAILED,
                    error_message=f"Recovery command failed: {result.stderr}",
                    recovery_attempted=True,
                    recovery_successful=False
                )
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Recovery command timed out for {dep_name}")
            return HealthCheckResult(
                dependency=dep_name,
                status=DependencyStatus.FAILED,
                error_message="Recovery command timed out",
                recovery_attempted=True,
                recovery_successful=False
            )
        except Exception as e:
            self.logger.error(f"Recovery attempt failed for {dep_name}: {e}")
            return HealthCheckResult(
                dependency=dep_name,
                status=DependencyStatus.FAILED,
                error_message=f"Recovery attempt failed: {e}",
                recovery_attempted=True,
                recovery_successful=False
            )
    
    def validate_and_recover(self, auto_recover: bool = True) -> Dict[str, HealthCheckResult]:
        """
        Validate dependencies and attempt recovery for failed ones.
        
        Args:
            auto_recover: Whether to automatically attempt recovery
            
        Returns:
            Dictionary mapping dependency names to final health check results
        """
        # Initial validation
        results = self.validate_startup_dependencies()
        
        if not auto_recover:
            return results
        
        # Attempt recovery for failed dependencies
        recovery_needed = [
            name for name, result in results.items()
            if result.status in [DependencyStatus.MISSING, DependencyStatus.CORRUPTED]
            and not self.dependencies[name].required  # Only recover optional deps automatically
        ]
        
        for dep_name in recovery_needed:
            self.logger.info(f"Attempting automatic recovery for {dep_name}")
            recovery_result = self.attempt_recovery(dep_name)
            results[dep_name] = recovery_result
        
        return results
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get a summary of dependency health status.
        
        Returns:
            Dictionary containing health summary
        """
        if not self.health_status:
            self.validate_startup_dependencies()
        
        summary = {
            "total_dependencies": len(self.health_status),
            "healthy": 0,
            "missing": 0,
            "outdated": 0,
            "corrupted": 0,
            "failed": 0,
            "critical_missing": 0,
            "optional_missing": 0
        }
        
        for dep_name, result in self.health_status.items():
            dep_info = self.dependencies[dep_name]
            
            if result.status == DependencyStatus.HEALTHY:
                summary["healthy"] += 1
            elif result.status == DependencyStatus.MISSING:
                summary["missing"] += 1
                if dep_info.required:
                    summary["critical_missing"] += 1
                else:
                    summary["optional_missing"] += 1
            elif result.status == DependencyStatus.OUTDATED:
                summary["outdated"] += 1
            elif result.status == DependencyStatus.CORRUPTED:
                summary["corrupted"] += 1
            else:
                summary["failed"] += 1
        
        summary["overall_health"] = "healthy" if summary["critical_missing"] == 0 else "critical"
        
        return summary


# Global instance
_dependency_health = None


def get_dependency_health() -> DependencyHealth:
    """Get or create global dependency health instance"""
    global _dependency_health
    if _dependency_health is None:
        _dependency_health = DependencyHealth()
    return _dependency_health
