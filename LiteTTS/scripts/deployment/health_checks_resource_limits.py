#!/usr/bin/env python3
"""
Health Checks and Resource Limits Manager
Implement comprehensive health checks, resource limits, monitoring endpoints, and production-ready configurations
"""

import os
import sys
import json
import logging
import time
import psutil
import threading
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class HealthCheckResult:
    """Health check result"""
    check_name: str
    status: str  # healthy, warning, critical, unknown
    message: str
    details: Dict[str, Any]
    timestamp: float
    response_time_ms: float

@dataclass
class ResourceLimits:
    """Resource limits configuration"""
    max_memory_mb: int
    max_cpu_percent: float
    max_disk_usage_percent: float
    max_open_files: int
    max_concurrent_requests: int
    request_timeout_seconds: int
    health_check_interval_seconds: int

@dataclass
class MonitoringEndpoint:
    """Monitoring endpoint configuration"""
    endpoint_path: str
    method: str
    description: str
    response_format: str
    authentication_required: bool

class HealthCheckManager:
    """Health checks and resource limits manager"""
    
    def __init__(self):
        self.results_dir = Path("test_results/health_monitoring")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Health check results storage
        self.health_results = {}
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Resource limits
        self.resource_limits = self._create_default_resource_limits()
        
        # Monitoring endpoints
        self.monitoring_endpoints = self._create_monitoring_endpoints()
        
        # System information
        self.system_info = self._get_system_info()
        
    def _create_default_resource_limits(self) -> ResourceLimits:
        """Create default resource limits"""
        return ResourceLimits(
            max_memory_mb=2048,  # 2GB memory limit
            max_cpu_percent=90.0,  # 90% CPU usage limit
            max_disk_usage_percent=85.0,  # 85% disk usage limit
            max_open_files=1024,  # File descriptor limit
            max_concurrent_requests=100,  # Concurrent request limit
            request_timeout_seconds=30,  # Request timeout
            health_check_interval_seconds=30  # Health check frequency
        )
    
    def _create_monitoring_endpoints(self) -> List[MonitoringEndpoint]:
        """Create monitoring endpoints configuration"""
        return [
            MonitoringEndpoint(
                endpoint_path="/health",
                method="GET",
                description="Basic health check endpoint",
                response_format="json",
                authentication_required=False
            ),
            MonitoringEndpoint(
                endpoint_path="/health/detailed",
                method="GET", 
                description="Detailed health check with all components",
                response_format="json",
                authentication_required=False
            ),
            MonitoringEndpoint(
                endpoint_path="/metrics",
                method="GET",
                description="Prometheus-compatible metrics endpoint",
                response_format="text",
                authentication_required=False
            ),
            MonitoringEndpoint(
                endpoint_path="/status",
                method="GET",
                description="System status and resource usage",
                response_format="json",
                authentication_required=False
            ),
            MonitoringEndpoint(
                endpoint_path="/ready",
                method="GET",
                description="Readiness probe for Kubernetes",
                response_format="json",
                authentication_required=False
            ),
            MonitoringEndpoint(
                endpoint_path="/live",
                method="GET",
                description="Liveness probe for Kubernetes",
                response_format="json",
                authentication_required=False
            )
        ]
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
                "platform": sys.platform,
                "python_version": sys.version,
                "process_id": os.getpid()
            }
        except Exception as e:
            logger.warning(f"Could not get system info: {e}")
            return {}
    
    def check_memory_usage(self) -> HealthCheckResult:
        """Check memory usage"""
        start_time = time.time()
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            memory_percent = process.memory_percent()
            
            if memory_mb > self.resource_limits.max_memory_mb:
                status = "critical"
                message = f"Memory usage ({memory_mb:.1f}MB) exceeds limit ({self.resource_limits.max_memory_mb}MB)"
            elif memory_mb > self.resource_limits.max_memory_mb * 0.8:
                status = "warning"
                message = f"Memory usage ({memory_mb:.1f}MB) approaching limit"
            else:
                status = "healthy"
                message = f"Memory usage normal ({memory_mb:.1f}MB)"
            
            details = {
                "memory_mb": round(memory_mb, 2),
                "memory_percent": round(memory_percent, 2),
                "limit_mb": self.resource_limits.max_memory_mb,
                "virtual_memory": memory_info.vms / (1024 * 1024)
            }
            
        except Exception as e:
            status = "unknown"
            message = f"Memory check failed: {str(e)}"
            details = {"error": str(e)}
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            check_name="memory_usage",
            status=status,
            message=message,
            details=details,
            timestamp=time.time(),
            response_time_ms=round(response_time, 2)
        )
    
    def check_cpu_usage(self) -> HealthCheckResult:
        """Check CPU usage"""
        start_time = time.time()
        
        try:
            # Get CPU usage over a short interval
            cpu_percent = psutil.cpu_percent(interval=1.0)
            cpu_count = psutil.cpu_count()
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            
            if cpu_percent > self.resource_limits.max_cpu_percent:
                status = "critical"
                message = f"CPU usage ({cpu_percent:.1f}%) exceeds limit ({self.resource_limits.max_cpu_percent}%)"
            elif cpu_percent > self.resource_limits.max_cpu_percent * 0.8:
                status = "warning"
                message = f"CPU usage ({cpu_percent:.1f}%) approaching limit"
            else:
                status = "healthy"
                message = f"CPU usage normal ({cpu_percent:.1f}%)"
            
            details = {
                "cpu_percent": round(cpu_percent, 2),
                "cpu_count": cpu_count,
                "load_average_1m": round(load_avg[0], 2),
                "load_average_5m": round(load_avg[1], 2),
                "load_average_15m": round(load_avg[2], 2),
                "limit_percent": self.resource_limits.max_cpu_percent
            }
            
        except Exception as e:
            status = "unknown"
            message = f"CPU check failed: {str(e)}"
            details = {"error": str(e)}
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            check_name="cpu_usage",
            status=status,
            message=message,
            details=details,
            timestamp=time.time(),
            response_time_ms=round(response_time, 2)
        )
    
    def check_disk_usage(self) -> HealthCheckResult:
        """Check disk usage"""
        start_time = time.time()
        
        try:
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            free_gb = disk_usage.free / (1024**3)
            
            if disk_percent > self.resource_limits.max_disk_usage_percent:
                status = "critical"
                message = f"Disk usage ({disk_percent:.1f}%) exceeds limit ({self.resource_limits.max_disk_usage_percent}%)"
            elif disk_percent > self.resource_limits.max_disk_usage_percent * 0.9:
                status = "warning"
                message = f"Disk usage ({disk_percent:.1f}%) approaching limit"
            else:
                status = "healthy"
                message = f"Disk usage normal ({disk_percent:.1f}%)"
            
            details = {
                "disk_percent": round(disk_percent, 2),
                "free_gb": round(free_gb, 2),
                "total_gb": round(disk_usage.total / (1024**3), 2),
                "used_gb": round(disk_usage.used / (1024**3), 2),
                "limit_percent": self.resource_limits.max_disk_usage_percent
            }
            
        except Exception as e:
            status = "unknown"
            message = f"Disk check failed: {str(e)}"
            details = {"error": str(e)}
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            check_name="disk_usage",
            status=status,
            message=message,
            details=details,
            timestamp=time.time(),
            response_time_ms=round(response_time, 2)
        )
    
    def check_file_descriptors(self) -> HealthCheckResult:
        """Check file descriptor usage"""
        start_time = time.time()
        
        try:
            process = psutil.Process()
            open_files = len(process.open_files())
            
            if open_files > self.resource_limits.max_open_files:
                status = "critical"
                message = f"Open files ({open_files}) exceeds limit ({self.resource_limits.max_open_files})"
            elif open_files > self.resource_limits.max_open_files * 0.8:
                status = "warning"
                message = f"Open files ({open_files}) approaching limit"
            else:
                status = "healthy"
                message = f"File descriptor usage normal ({open_files})"
            
            details = {
                "open_files": open_files,
                "limit": self.resource_limits.max_open_files,
                "usage_percent": round((open_files / self.resource_limits.max_open_files) * 100, 2)
            }
            
        except Exception as e:
            status = "unknown"
            message = f"File descriptor check failed: {str(e)}"
            details = {"error": str(e)}
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            check_name="file_descriptors",
            status=status,
            message=message,
            details=details,
            timestamp=time.time(),
            response_time_ms=round(response_time, 2)
        )
    
    def check_model_availability(self) -> HealthCheckResult:
        """Check if TTS models are available"""
        start_time = time.time()
        
        try:
            models_dir = Path("models")
            if not models_dir.exists():
                status = "critical"
                message = "Models directory not found"
                details = {"models_dir": str(models_dir), "exists": False}
            else:
                model_files = list(models_dir.glob("*.onnx"))
                if not model_files:
                    status = "critical"
                    message = "No ONNX model files found"
                    details = {"models_dir": str(models_dir), "model_count": 0}
                else:
                    status = "healthy"
                    message = f"Found {len(model_files)} model files"
                    details = {
                        "models_dir": str(models_dir),
                        "model_count": len(model_files),
                        "model_files": [f.name for f in model_files]
                    }
            
        except Exception as e:
            status = "unknown"
            message = f"Model availability check failed: {str(e)}"
            details = {"error": str(e)}
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            check_name="model_availability",
            status=status,
            message=message,
            details=details,
            timestamp=time.time(),
            response_time_ms=round(response_time, 2)
        )
    
    def check_voice_availability(self) -> HealthCheckResult:
        """Check if voices are available"""
        start_time = time.time()
        
        try:
            voices_dir = Path("voices")
            if not voices_dir.exists():
                status = "warning"
                message = "Voices directory not found"
                details = {"voices_dir": str(voices_dir), "exists": False}
            else:
                voice_files = list(voices_dir.glob("*.pt"))
                if not voice_files:
                    status = "warning"
                    message = "No voice files found"
                    details = {"voices_dir": str(voices_dir), "voice_count": 0}
                else:
                    status = "healthy"
                    message = f"Found {len(voice_files)} voice files"
                    details = {
                        "voices_dir": str(voices_dir),
                        "voice_count": len(voice_files),
                        "sample_voices": [f.name for f in voice_files[:5]]  # First 5 voices
                    }
            
        except Exception as e:
            status = "unknown"
            message = f"Voice availability check failed: {str(e)}"
            details = {"error": str(e)}
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            check_name="voice_availability",
            status=status,
            message=message,
            details=details,
            timestamp=time.time(),
            response_time_ms=round(response_time, 2)
        )
    
    def check_api_endpoint(self) -> HealthCheckResult:
        """Check if API endpoint is responsive"""
        start_time = time.time()
        
        try:
            import requests
            
            # Test the health endpoint
            response = requests.get("http://localhost:8354/health", timeout=5)
            
            if response.status_code == 200:
                status = "healthy"
                message = "API endpoint responsive"
                details = {
                    "status_code": response.status_code,
                    "response_time_ms": round((time.time() - start_time) * 1000, 2)
                }
            else:
                status = "warning"
                message = f"API endpoint returned status {response.status_code}"
                details = {"status_code": response.status_code}
            
        except requests.exceptions.ConnectionError:
            status = "critical"
            message = "API endpoint not reachable"
            details = {"error": "Connection refused"}
        except Exception as e:
            status = "unknown"
            message = f"API endpoint check failed: {str(e)}"
            details = {"error": str(e)}
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            check_name="api_endpoint",
            status=status,
            message=message,
            details=details,
            timestamp=time.time(),
            response_time_ms=round(response_time, 2)
        )
    
    def run_all_health_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all health checks"""
        logger.info("Running comprehensive health checks...")
        
        checks = {
            "memory_usage": self.check_memory_usage(),
            "cpu_usage": self.check_cpu_usage(),
            "disk_usage": self.check_disk_usage(),
            "file_descriptors": self.check_file_descriptors(),
            "model_availability": self.check_model_availability(),
            "voice_availability": self.check_voice_availability(),
            "api_endpoint": self.check_api_endpoint()
        }
        
        self.health_results = checks
        return checks
    
    def get_overall_health_status(self, checks: Dict[str, HealthCheckResult]) -> str:
        """Get overall health status"""
        statuses = [check.status for check in checks.values()]
        
        if "critical" in statuses:
            return "critical"
        elif "warning" in statuses:
            return "warning"
        elif "unknown" in statuses:
            return "unknown"
        else:
            return "healthy"

    def generate_health_check_endpoints(self) -> str:
        """Generate FastAPI health check endpoints"""
        logger.info("Generating health check endpoints...")

        endpoints_code = '''"""
Health Check and Monitoring Endpoints
Add these endpoints to your FastAPI application
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
import time
import json
from typing import Dict, Any

# Import the health check manager
from scripts.health_checks_resource_limits import HealthCheckManager

router = APIRouter()
health_manager = HealthCheckManager()

@router.get("/health")
async def basic_health_check():
    """Basic health check endpoint"""
    try:
        checks = health_manager.run_all_health_checks()
        overall_status = health_manager.get_overall_health_status(checks)

        return {
            "status": overall_status,
            "timestamp": time.time(),
            "checks": len(checks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all components"""
    try:
        checks = health_manager.run_all_health_checks()
        overall_status = health_manager.get_overall_health_status(checks)

        return {
            "status": overall_status,
            "timestamp": time.time(),
            "system_info": health_manager.system_info,
            "resource_limits": health_manager.resource_limits.__dict__,
            "checks": {name: {
                "status": check.status,
                "message": check.message,
                "details": check.details,
                "response_time_ms": check.response_time_ms
            } for name, check in checks.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Prometheus-compatible metrics endpoint"""
    try:
        checks = health_manager.run_all_health_checks()

        metrics = []

        # Health check metrics
        for name, check in checks.items():
            status_value = 1 if check.status == "healthy" else 0
            metrics.append(f'health_check_status{{check="{name}"}} {status_value}')
            metrics.append(f'health_check_response_time_ms{{check="{name}"}} {check.response_time_ms}')

        # Resource metrics
        if "memory_usage" in checks:
            memory_details = checks["memory_usage"].details
            if "memory_mb" in memory_details:
                metrics.append(f'memory_usage_mb {memory_details["memory_mb"]}')
                metrics.append(f'memory_limit_mb {memory_details["limit_mb"]}')

        if "cpu_usage" in checks:
            cpu_details = checks["cpu_usage"].details
            if "cpu_percent" in cpu_details:
                metrics.append(f'cpu_usage_percent {cpu_details["cpu_percent"]}')
                metrics.append(f'cpu_limit_percent {cpu_details["limit_percent"]}')

        if "disk_usage" in checks:
            disk_details = checks["disk_usage"].details
            if "disk_percent" in disk_details:
                metrics.append(f'disk_usage_percent {disk_details["disk_percent"]}')
                metrics.append(f'disk_free_gb {disk_details["free_gb"]}')

        return "\\n".join(metrics) + "\\n"

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def system_status():
    """System status and resource usage"""
    try:
        checks = health_manager.run_all_health_checks()
        overall_status = health_manager.get_overall_health_status(checks)

        # Calculate summary statistics
        healthy_checks = sum(1 for check in checks.values() if check.status == "healthy")
        total_checks = len(checks)
        avg_response_time = sum(check.response_time_ms for check in checks.values()) / total_checks

        return {
            "overall_status": overall_status,
            "health_score": f"{healthy_checks}/{total_checks}",
            "health_percentage": round((healthy_checks / total_checks) * 100, 1),
            "average_response_time_ms": round(avg_response_time, 2),
            "timestamp": time.time(),
            "uptime_seconds": time.time() - health_manager.system_info.get("start_time", time.time()),
            "system_info": health_manager.system_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ready")
async def readiness_probe():
    """Readiness probe for Kubernetes"""
    try:
        checks = health_manager.run_all_health_checks()

        # Check critical components for readiness
        critical_checks = ["model_availability", "api_endpoint"]
        ready = all(checks.get(check, HealthCheckResult("", "unknown", "", {}, 0, 0)).status == "healthy"
                   for check in critical_checks)

        if ready:
            return {"status": "ready", "timestamp": time.time()}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live")
async def liveness_probe():
    """Liveness probe for Kubernetes"""
    try:
        # Simple liveness check - just verify the service is responding
        return {"status": "alive", "timestamp": time.time()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

        # Save endpoints code
        endpoints_file = self.results_dir / "health_endpoints.py"
        with open(endpoints_file, 'w') as f:
            f.write(endpoints_code)

        logger.info(f"Health check endpoints saved: {endpoints_file}")
        return endpoints_code

    def generate_docker_health_config(self) -> str:
        """Generate Docker health check configuration"""
        logger.info("Generating Docker health check configuration...")

        docker_config = f'''# Docker Health Check Configuration
# Add this to your Dockerfile

# Health check configuration
HEALTHCHECK --interval={self.resource_limits.health_check_interval_seconds}s \\
            --timeout=10s \\
            --start-period=30s \\
            --retries=3 \\
            CMD curl -f http://localhost:8354/health || exit 1

# Resource limits in docker-compose.yml
version: '3.8'

services:
  kokoro-tts:
    build: .
    container_name: kokoro-tts-prod
    restart: unless-stopped
    ports:
      - "8354:8354"

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '{self.resource_limits.max_cpu_percent / 100:.1f}'
          memory: {self.resource_limits.max_memory_mb}M
        reservations:
          cpus: '0.5'
          memory: 512M

    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8354/health"]
      interval: {self.resource_limits.health_check_interval_seconds}s
      timeout: 10s
      retries: 3
      start_period: 30s

    # Environment variables
    environment:
      - MAX_MEMORY_MB={self.resource_limits.max_memory_mb}
      - MAX_CPU_PERCENT={self.resource_limits.max_cpu_percent}
      - MAX_CONCURRENT_REQUESTS={self.resource_limits.max_concurrent_requests}
      - REQUEST_TIMEOUT_SECONDS={self.resource_limits.request_timeout_seconds}

    # Logging configuration
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

    networks:
      - kokoro-network

networks:
  kokoro-network:
    driver: bridge
'''

        # Save Docker configuration
        docker_file = self.results_dir / "docker_health_config.yml"
        with open(docker_file, 'w') as f:
            f.write(docker_config)

        logger.info(f"Docker health configuration saved: {docker_file}")
        return docker_config

    def generate_kubernetes_config(self) -> str:
        """Generate Kubernetes deployment with health checks"""
        logger.info("Generating Kubernetes configuration...")

        k8s_config = f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: kokoro-tts
  labels:
    app: kokoro-tts
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kokoro-tts
  template:
    metadata:
      labels:
        app: kokoro-tts
    spec:
      containers:
      - name: kokoro-tts
        image: kokoro-tts:latest
        ports:
        - containerPort: 8354

        # Resource limits
        resources:
          limits:
            memory: "{self.resource_limits.max_memory_mb}Mi"
            cpu: "{self.resource_limits.max_cpu_percent / 100:.1f}"
          requests:
            memory: "512Mi"
            cpu: "0.5"

        # Health checks
        livenessProbe:
          httpGet:
            path: /live
            port: 8354
          initialDelaySeconds: 30
          periodSeconds: {self.resource_limits.health_check_interval_seconds}
          timeoutSeconds: 10
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /ready
            port: 8354
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 5
          failureThreshold: 3

        # Environment variables
        env:
        - name: MAX_MEMORY_MB
          value: "{self.resource_limits.max_memory_mb}"
        - name: MAX_CPU_PERCENT
          value: "{self.resource_limits.max_cpu_percent}"
        - name: MAX_CONCURRENT_REQUESTS
          value: "{self.resource_limits.max_concurrent_requests}"
        - name: REQUEST_TIMEOUT_SECONDS
          value: "{self.resource_limits.request_timeout_seconds}"

        # Volume mounts
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
        - name: voices
          mountPath: /app/voices
          readOnly: true
        - name: cache
          mountPath: /app/cache
        - name: logs
          mountPath: /app/logs

      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: kokoro-models-pvc
      - name: voices
        persistentVolumeClaim:
          claimName: kokoro-voices-pvc
      - name: cache
        emptyDir: {{}}
      - name: logs
        emptyDir: {{}}

---
apiVersion: v1
kind: Service
metadata:
  name: kokoro-tts-service
spec:
  selector:
    app: kokoro-tts
  ports:
  - protocol: TCP
    port: 8354
    targetPort: 8354
  type: ClusterIP

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: kokoro-models-pvc
spec:
  accessModes:
    - ReadOnlyMany
  resources:
    requests:
      storage: 5Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: kokoro-voices-pvc
spec:
  accessModes:
    - ReadOnlyMany
  resources:
    requests:
      storage: 2Gi
'''

        # Save Kubernetes configuration
        k8s_file = self.results_dir / "kubernetes_deployment.yaml"
        with open(k8s_file, 'w') as f:
            f.write(k8s_config)

        logger.info(f"Kubernetes configuration saved: {k8s_file}")
        return k8s_config

    def generate_monitoring_script(self) -> str:
        """Generate monitoring script"""
        logger.info("Generating monitoring script...")

        monitoring_script = f'''#!/bin/bash
# Kokoro TTS Health Monitoring Script
# Generated automatically - do not edit manually

set -e

API_BASE="http://localhost:8354"
LOG_FILE="/var/log/kokoro-health.log"
ALERT_THRESHOLD_CRITICAL=3
ALERT_THRESHOLD_WARNING=5

# Create log file if it doesn't exist
touch "$LOG_FILE"

echo "$(date): Starting health monitoring check" >> "$LOG_FILE"

# Function to send alert
send_alert() {{
    local severity=$1
    local message=$2
    echo "$(date): ALERT [$severity] $message" >> "$LOG_FILE"

    # Add your alerting mechanism here (email, webhook, etc.)
    # Example: curl -X POST "https://hooks.slack.com/..." -d "{{\\"text\\": \\"$message\\"}}"
}}

# Check basic health
echo "Checking basic health..."
HEALTH_STATUS=$(curl -s "$API_BASE/health" | jq -r '.status' 2>/dev/null || echo "unknown")

if [ "$HEALTH_STATUS" = "critical" ]; then
    send_alert "CRITICAL" "Kokoro TTS health check failed: $HEALTH_STATUS"
    exit 1
elif [ "$HEALTH_STATUS" = "warning" ]; then
    send_alert "WARNING" "Kokoro TTS health check warning: $HEALTH_STATUS"
elif [ "$HEALTH_STATUS" = "healthy" ]; then
    echo "$(date): Health check passed" >> "$LOG_FILE"
else
    send_alert "UNKNOWN" "Kokoro TTS health check returned unknown status: $HEALTH_STATUS"
fi

# Check detailed metrics
echo "Checking detailed metrics..."
METRICS=$(curl -s "$API_BASE/health/detailed" 2>/dev/null || echo "{{}}")

# Check memory usage
MEMORY_STATUS=$(echo "$METRICS" | jq -r '.checks.memory_usage.status' 2>/dev/null || echo "unknown")
if [ "$MEMORY_STATUS" = "critical" ]; then
    MEMORY_MSG=$(echo "$METRICS" | jq -r '.checks.memory_usage.message' 2>/dev/null || echo "Memory check failed")
    send_alert "CRITICAL" "Memory usage critical: $MEMORY_MSG"
fi

# Check CPU usage
CPU_STATUS=$(echo "$METRICS" | jq -r '.checks.cpu_usage.status' 2>/dev/null || echo "unknown")
if [ "$CPU_STATUS" = "critical" ]; then
    CPU_MSG=$(echo "$METRICS" | jq -r '.checks.cpu_usage.message' 2>/dev/null || echo "CPU check failed")
    send_alert "CRITICAL" "CPU usage critical: $CPU_MSG"
fi

# Check disk usage
DISK_STATUS=$(echo "$METRICS" | jq -r '.checks.disk_usage.status' 2>/dev/null || echo "unknown")
if [ "$DISK_STATUS" = "critical" ]; then
    DISK_MSG=$(echo "$METRICS" | jq -r '.checks.disk_usage.message' 2>/dev/null || echo "Disk check failed")
    send_alert "CRITICAL" "Disk usage critical: $DISK_MSG"
fi

# Test API functionality
echo "Testing API functionality..."
TEST_RESPONSE=$(curl -s -w "%{{http_code}}" -X POST "$API_BASE/v1/audio/speech" \\
    -H "Content-Type: application/json" \\
    -d '{{"model": "kokoro", "input": "test", "voice": "af_heart"}}' \\
    -o /dev/null 2>/dev/null || echo "000")

if [ "$TEST_RESPONSE" != "200" ]; then
    send_alert "CRITICAL" "API functionality test failed: HTTP $TEST_RESPONSE"
else
    echo "$(date): API functionality test passed" >> "$LOG_FILE"
fi

echo "$(date): Health monitoring check completed" >> "$LOG_FILE"
'''

        # Save monitoring script
        script_file = self.results_dir / "health_monitor.sh"
        with open(script_file, 'w') as f:
            f.write(monitoring_script)
        os.chmod(script_file, 0o755)

        logger.info(f"Monitoring script saved: {script_file}")
        return monitoring_script

    def run_comprehensive_health_setup(self) -> Dict[str, Any]:
        """Run comprehensive health checks and resource limits setup"""
        logger.info("Starting comprehensive health checks and resource limits setup...")

        # Run initial health checks
        health_checks = self.run_all_health_checks()
        overall_status = self.get_overall_health_status(health_checks)

        # Generate configurations
        endpoints_code = self.generate_health_check_endpoints()
        docker_config = self.generate_docker_health_config()
        k8s_config = self.generate_kubernetes_config()
        monitoring_script = self.generate_monitoring_script()

        # Calculate health summary
        healthy_checks = sum(1 for check in health_checks.values() if check.status == "healthy")
        total_checks = len(health_checks)
        avg_response_time = sum(check.response_time_ms for check in health_checks.values()) / total_checks

        # Compile results
        setup_results = {
            "setup_timestamp": time.time(),
            "overall_health_status": overall_status,
            "health_summary": {
                "healthy_checks": healthy_checks,
                "total_checks": total_checks,
                "health_percentage": round((healthy_checks / total_checks) * 100, 1),
                "average_response_time_ms": round(avg_response_time, 2)
            },
            "resource_limits": asdict(self.resource_limits),
            "system_info": self.system_info,
            "health_checks": {name: asdict(check) for name, check in health_checks.items()},
            "generated_files": {
                "health_endpoints": "health_endpoints.py",
                "docker_config": "docker_health_config.yml",
                "kubernetes_config": "kubernetes_deployment.yaml",
                "monitoring_script": "health_monitor.sh"
            },
            "monitoring_endpoints": [asdict(endpoint) for endpoint in self.monitoring_endpoints],
            "setup_summary": self._generate_health_summary(health_checks, overall_status),
            "next_steps": self._generate_health_next_steps(overall_status, health_checks)
        }

        # Save complete configuration
        results_file = self.results_dir / f"health_setup_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(setup_results, f, indent=2, default=str)

        logger.info(f"Health checks setup completed. Results saved to: {results_file}")
        return setup_results

    def _generate_health_summary(self, health_checks: Dict[str, HealthCheckResult],
                                overall_status: str) -> Dict[str, Any]:
        """Generate health setup summary"""

        status_counts = {}
        for check in health_checks.values():
            status_counts[check.status] = status_counts.get(check.status, 0) + 1

        critical_issues = [check.message for check in health_checks.values() if check.status == "critical"]
        warning_issues = [check.message for check in health_checks.values() if check.status == "warning"]

        summary = {
            "overall_status": overall_status,
            "status_distribution": status_counts,
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "total_endpoints_generated": len(self.monitoring_endpoints),
            "resource_limits_configured": True,
            "monitoring_enabled": True,
            "production_ready": overall_status in ["healthy", "warning"]
        }

        return summary

    def _generate_health_next_steps(self, overall_status: str,
                                  health_checks: Dict[str, HealthCheckResult]) -> List[str]:
        """Generate next steps for health monitoring deployment"""
        next_steps = [
            "Integrate health check endpoints into your FastAPI application",
            "Configure Docker health checks in your container deployment",
            "Set up monitoring alerts for critical health check failures",
            "Test health check endpoints with load testing tools",
            "Configure log aggregation for health monitoring data",
            "Set up automated health check monitoring in production",
            "Configure resource limit alerts and notifications",
            "Test Kubernetes readiness and liveness probes",
            "Implement custom health checks for business logic",
            "Document health check procedures for operations team"
        ]

        # Add specific recommendations based on health status
        if overall_status == "critical":
            next_steps.insert(0, "Address critical health issues immediately before deployment")

        if overall_status == "warning":
            next_steps.insert(0, "Review and resolve warning-level health issues")

        # Add specific recommendations based on failed checks
        for name, check in health_checks.items():
            if check.status == "critical":
                if name == "memory_usage":
                    next_steps.append("Optimize memory usage or increase memory limits")
                elif name == "cpu_usage":
                    next_steps.append("Optimize CPU usage or increase CPU limits")
                elif name == "disk_usage":
                    next_steps.append("Clean up disk space or increase storage capacity")
                elif name == "model_availability":
                    next_steps.append("Ensure TTS models are properly deployed")
                elif name == "api_endpoint":
                    next_steps.append("Fix API endpoint connectivity issues")

        return next_steps

def main():
    """Main function to run health checks and resource limits setup"""
    manager = HealthCheckManager()

    try:
        # Run comprehensive health setup
        results = manager.run_comprehensive_health_setup()

        print("\n" + "="*80)
        print("HEALTH CHECKS AND RESOURCE LIMITS SUMMARY")
        print("="*80)

        summary = results["setup_summary"]
        health_summary = results["health_summary"]

        print(f"Overall Health Status: {summary['overall_status'].upper()}")
        print(f"Health Score: {health_summary['healthy_checks']}/{health_summary['total_checks']} ({health_summary['health_percentage']:.1f}%)")
        print(f"Average Response Time: {health_summary['average_response_time_ms']:.2f}ms")

        print(f"\nHealth Check Results:")
        for status, count in summary["status_distribution"].items():
            emoji = {"healthy": "✅", "warning": "⚠️", "critical": "❌", "unknown": "❓"}.get(status, "❓")
            print(f"  {emoji} {status.title()}: {count}")

        if summary["critical_issues"]:
            print(f"\nCritical Issues:")
            for issue in summary["critical_issues"]:
                print(f"  ❌ {issue}")

        if summary["warning_issues"]:
            print(f"\nWarning Issues:")
            for issue in summary["warning_issues"]:
                print(f"  ⚠️  {issue}")

        print(f"\nResource Limits:")
        limits = results["resource_limits"]
        print(f"  Memory: {limits['max_memory_mb']}MB")
        print(f"  CPU: {limits['max_cpu_percent']}%")
        print(f"  Disk: {limits['max_disk_usage_percent']}%")
        print(f"  Concurrent Requests: {limits['max_concurrent_requests']}")

        print(f"\nGenerated Files:")
        for file_type, filename in results["generated_files"].items():
            print(f"  {file_type}: {filename}")

        print(f"\nMonitoring Endpoints: {len(results['monitoring_endpoints'])}")
        for endpoint in results["monitoring_endpoints"]:
            print(f"  {endpoint['method']} {endpoint['endpoint_path']} - {endpoint['description']}")

        print(f"\nProduction Ready: {'✅' if summary['production_ready'] else '❌'}")

        print(f"\nNext Steps:")
        for i, step in enumerate(results["next_steps"][:5], 1):
            print(f"  {i}. {step}")

        if len(results["next_steps"]) > 5:
            print(f"  ... and {len(results['next_steps']) - 5} more steps")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"Health checks setup failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
