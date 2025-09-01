#!/usr/bin/env python3
"""
Comprehensive Logging System
Set up structured logging for production debugging with appropriate log levels, rotation, and monitoring integration
"""

import os
import sys
import json
import logging
import logging.handlers
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import threading

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@dataclass
class LoggingConfiguration:
    """Logging configuration settings"""
    log_level: str
    log_format: str
    enable_file_logging: bool
    enable_console_logging: bool
    enable_structured_logging: bool
    log_directory: str
    max_file_size_mb: int
    backup_count: int
    enable_rotation: bool
    enable_compression: bool
    enable_remote_logging: bool
    remote_endpoint: str
    enable_performance_logging: bool
    enable_security_logging: bool
    enable_api_logging: bool

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    logger_name: str
    message: str
    module: str
    function: str
    line_number: int
    thread_id: int
    process_id: int
    extra_data: Dict[str, Any]

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        """Format log record as structured JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread_id": record.thread,
            "process_id": record.process
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                extra_fields[key] = value
        
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        return json.dumps(log_entry, default=str)

class PerformanceLogger:
    """Performance logging utility"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.start_times = {}
    
    def start_timer(self, operation_id: str):
        """Start timing an operation"""
        self.start_times[operation_id] = time.time()
    
    def end_timer(self, operation_id: str, operation_name: str, **kwargs):
        """End timing and log performance"""
        if operation_id in self.start_times:
            duration = time.time() - self.start_times[operation_id]
            del self.start_times[operation_id]
            
            self.logger.info(
                f"Performance: {operation_name} completed",
                extra={
                    "performance": True,
                    "operation": operation_name,
                    "duration_seconds": round(duration, 4),
                    "operation_id": operation_id,
                    **kwargs
                }
            )
        else:
            self.logger.warning(f"Timer not found for operation: {operation_id}")
    
    def log_metric(self, metric_name: str, value: float, unit: str = "", **kwargs):
        """Log a performance metric"""
        self.logger.info(
            f"Metric: {metric_name} = {value} {unit}",
            extra={
                "metric": True,
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                **kwargs
            }
        )

class SecurityLogger:
    """Security logging utility"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_authentication_attempt(self, username: str, success: bool, ip_address: str = "", **kwargs):
        """Log authentication attempt"""
        level = logging.INFO if success else logging.WARNING
        message = f"Authentication {'successful' if success else 'failed'} for user: {username}"
        
        self.logger.log(
            level,
            message,
            extra={
                "security": True,
                "event_type": "authentication",
                "username": username,
                "success": success,
                "ip_address": ip_address,
                **kwargs
            }
        )
    
    def log_authorization_failure(self, username: str, resource: str, action: str, **kwargs):
        """Log authorization failure"""
        self.logger.warning(
            f"Authorization failed: {username} attempted {action} on {resource}",
            extra={
                "security": True,
                "event_type": "authorization_failure",
                "username": username,
                "resource": resource,
                "action": action,
                **kwargs
            }
        )
    
    def log_suspicious_activity(self, activity_type: str, description: str, **kwargs):
        """Log suspicious activity"""
        self.logger.warning(
            f"Suspicious activity detected: {activity_type} - {description}",
            extra={
                "security": True,
                "event_type": "suspicious_activity",
                "activity_type": activity_type,
                "description": description,
                **kwargs
            }
        )

class APILogger:
    """API request/response logging utility"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(self, method: str, path: str, status_code: int, 
                   duration_ms: float, request_size: int = 0, 
                   response_size: int = 0, **kwargs):
        """Log API request"""
        self.logger.info(
            f"API {method} {path} - {status_code} ({duration_ms:.2f}ms)",
            extra={
                "api": True,
                "event_type": "request",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "request_size": request_size,
                "response_size": response_size,
                **kwargs
            }
        )
    
    def log_error(self, method: str, path: str, error: str, **kwargs):
        """Log API error"""
        self.logger.error(
            f"API Error {method} {path}: {error}",
            extra={
                "api": True,
                "event_type": "error",
                "method": method,
                "path": path,
                "error": error,
                **kwargs
            }
        )

class ComprehensiveLoggingManager:
    """Comprehensive logging system manager"""
    
    def __init__(self):
        self.results_dir = Path("test_results/logging_system")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.config = self._create_default_config()
        
        # Specialized loggers
        self.performance_logger = None
        self.security_logger = None
        self.api_logger = None
        
        # Logger instances
        self.loggers = {}
        
    def _create_default_config(self) -> LoggingConfiguration:
        """Create default logging configuration"""
        return LoggingConfiguration(
            log_level="INFO",
            log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            enable_file_logging=True,
            enable_console_logging=True,
            enable_structured_logging=True,
            log_directory="logs",
            max_file_size_mb=10,
            backup_count=5,
            enable_rotation=True,
            enable_compression=True,
            enable_remote_logging=False,
            remote_endpoint="",
            enable_performance_logging=True,
            enable_security_logging=True,
            enable_api_logging=True
        )
    
    def setup_logging(self, config: Optional[LoggingConfiguration] = None) -> Dict[str, Any]:
        """Set up comprehensive logging system"""
        if config:
            self.config = config
        
        # Create logs directory
        log_dir = Path(self.config.log_directory)
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        handlers = []
        
        # Console handler
        if self.config.enable_console_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            if self.config.enable_structured_logging:
                console_handler.setFormatter(StructuredFormatter())
            else:
                console_handler.setFormatter(logging.Formatter(self.config.log_format))
            handlers.append(console_handler)
        
        # File handlers
        if self.config.enable_file_logging:
            # Main application log
            app_log_file = log_dir / "kokoro_tts.log"
            if self.config.enable_rotation:
                app_handler = logging.handlers.RotatingFileHandler(
                    app_log_file,
                    maxBytes=self.config.max_file_size_mb * 1024 * 1024,
                    backupCount=self.config.backup_count
                )
            else:
                app_handler = logging.FileHandler(app_log_file)
            
            if self.config.enable_structured_logging:
                app_handler.setFormatter(StructuredFormatter())
            else:
                app_handler.setFormatter(logging.Formatter(self.config.log_format))
            handlers.append(app_handler)
            
            # Error log
            error_log_file = log_dir / "error.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self.config.max_file_size_mb * 1024 * 1024,
                backupCount=self.config.backup_count
            )
            error_handler.setLevel(logging.ERROR)
            if self.config.enable_structured_logging:
                error_handler.setFormatter(StructuredFormatter())
            else:
                error_handler.setFormatter(logging.Formatter(self.config.log_format))
            handlers.append(error_handler)
            
            # Performance log
            if self.config.enable_performance_logging:
                perf_log_file = log_dir / "performance.log"
                perf_handler = logging.handlers.RotatingFileHandler(
                    perf_log_file,
                    maxBytes=self.config.max_file_size_mb * 1024 * 1024,
                    backupCount=self.config.backup_count
                )
                perf_handler.addFilter(lambda record: hasattr(record, 'performance') or hasattr(record, 'metric'))
                if self.config.enable_structured_logging:
                    perf_handler.setFormatter(StructuredFormatter())
                else:
                    perf_handler.setFormatter(logging.Formatter(self.config.log_format))
                handlers.append(perf_handler)
            
            # Security log
            if self.config.enable_security_logging:
                security_log_file = log_dir / "security.log"
                security_handler = logging.handlers.RotatingFileHandler(
                    security_log_file,
                    maxBytes=self.config.max_file_size_mb * 1024 * 1024,
                    backupCount=self.config.backup_count
                )
                security_handler.addFilter(lambda record: hasattr(record, 'security'))
                if self.config.enable_structured_logging:
                    security_handler.setFormatter(StructuredFormatter())
                else:
                    security_handler.setFormatter(logging.Formatter(self.config.log_format))
                handlers.append(security_handler)
            
            # API log
            if self.config.enable_api_logging:
                api_log_file = log_dir / "api.log"
                api_handler = logging.handlers.RotatingFileHandler(
                    api_log_file,
                    maxBytes=self.config.max_file_size_mb * 1024 * 1024,
                    backupCount=self.config.backup_count
                )
                api_handler.addFilter(lambda record: hasattr(record, 'api'))
                if self.config.enable_structured_logging:
                    api_handler.setFormatter(StructuredFormatter())
                else:
                    api_handler.setFormatter(logging.Formatter(self.config.log_format))
                handlers.append(api_handler)
        
        # Add all handlers to root logger
        for handler in handlers:
            root_logger.addHandler(handler)
        
        # Create specialized loggers
        main_logger = logging.getLogger("kokoro_tts")
        self.performance_logger = PerformanceLogger(main_logger)
        self.security_logger = SecurityLogger(main_logger)
        self.api_logger = APILogger(main_logger)
        
        # Store logger references
        self.loggers = {
            "main": main_logger,
            "performance": self.performance_logger,
            "security": self.security_logger,
            "api": self.api_logger
        }
        
        setup_result = {
            "success": True,
            "handlers_configured": len(handlers),
            "log_directory": str(log_dir),
            "log_level": self.config.log_level,
            "structured_logging": self.config.enable_structured_logging,
            "specialized_loggers": list(self.loggers.keys())
        }
        
        main_logger.info("Comprehensive logging system initialized", extra={"setup": setup_result})
        
        return setup_result

    def generate_logging_middleware(self) -> str:
        """Generate FastAPI logging middleware"""
        middleware_code = '''"""
FastAPI Logging Middleware
Add this middleware to your FastAPI application for comprehensive request logging
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class LoggingMiddleware(BaseHTTPMiddleware):
    """Comprehensive logging middleware for FastAPI"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger("kokoro_tts.api")

    async def dispatch(self, request: Request, call_next):
        """Process request and log details"""
        start_time = time.time()

        # Extract request information
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")

        # Generate request ID
        request_id = f"{int(start_time * 1000000)}"

        # Log request start
        self.logger.info(
            f"Request started: {method} {path}",
            extra={
                "api": True,
                "event_type": "request_start",
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_ip": client_ip,
                "user_agent": user_agent
            }
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log successful response
            self.logger.info(
                f"Request completed: {method} {path} - {response.status_code} ({duration_ms:.2f}ms)",
                extra={
                    "api": True,
                    "event_type": "request_completed",
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                    "client_ip": client_ip
                }
            )

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            self.logger.error(
                f"Request failed: {method} {path} - {str(e)} ({duration_ms:.2f}ms)",
                extra={
                    "api": True,
                    "event_type": "request_error",
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "error": str(e),
                    "duration_ms": round(duration_ms, 2),
                    "client_ip": client_ip
                },
                exc_info=True
            )

            raise

# Usage in FastAPI app:
# from fastapi import FastAPI
# app = FastAPI()
# app.add_middleware(LoggingMiddleware)
'''

        # Save middleware code
        middleware_file = self.results_dir / "logging_middleware.py"
        with open(middleware_file, 'w') as f:
            f.write(middleware_code)

        return middleware_code

    def generate_logging_config_file(self) -> str:
        """Generate logging configuration file"""
        config_content = f'''# Kokoro TTS Logging Configuration
# This file configures the comprehensive logging system

[loggers]
keys=root,kokoro_tts,performance,security,api

[handlers]
keys=consoleHandler,fileHandler,errorHandler,performanceHandler,securityHandler,apiHandler

[formatters]
keys=standardFormatter,structuredFormatter

[logger_root]
level={self.config.log_level}
handlers=consoleHandler,fileHandler,errorHandler

[logger_kokoro_tts]
level={self.config.log_level}
handlers=consoleHandler,fileHandler
qualname=kokoro_tts
propagate=0

[logger_performance]
level=INFO
handlers=performanceHandler
qualname=kokoro_tts.performance
propagate=0

[logger_security]
level=WARNING
handlers=securityHandler
qualname=kokoro_tts.security
propagate=0

[logger_api]
level=INFO
handlers=apiHandler
qualname=kokoro_tts.api
propagate=0

[handler_consoleHandler]
class=StreamHandler
level={self.config.log_level}
formatter={"structuredFormatter" if self.config.enable_structured_logging else "standardFormatter"}
args=(sys.stdout,)

[handler_fileHandler]
class=handlers.RotatingFileHandler
level={self.config.log_level}
formatter={"structuredFormatter" if self.config.enable_structured_logging else "standardFormatter"}
args=('{self.config.log_directory}/kokoro_tts.log', 'a', {self.config.max_file_size_mb * 1024 * 1024}, {self.config.backup_count})

[handler_errorHandler]
class=handlers.RotatingFileHandler
level=ERROR
formatter={"structuredFormatter" if self.config.enable_structured_logging else "standardFormatter"}
args=('{self.config.log_directory}/error.log', 'a', {self.config.max_file_size_mb * 1024 * 1024}, {self.config.backup_count})

[handler_performanceHandler]
class=handlers.RotatingFileHandler
level=INFO
formatter={"structuredFormatter" if self.config.enable_structured_logging else "standardFormatter"}
args=('{self.config.log_directory}/performance.log', 'a', {self.config.max_file_size_mb * 1024 * 1024}, {self.config.backup_count})

[handler_securityHandler]
class=handlers.RotatingFileHandler
level=WARNING
formatter={"structuredFormatter" if self.config.enable_structured_logging else "standardFormatter"}
args=('{self.config.log_directory}/security.log', 'a', {self.config.max_file_size_mb * 1024 * 1024}, {self.config.backup_count})

[handler_apiHandler]
class=handlers.RotatingFileHandler
level=INFO
formatter={"structuredFormatter" if self.config.enable_structured_logging else "standardFormatter"}
args=('{self.config.log_directory}/api.log', 'a', {self.config.max_file_size_mb * 1024 * 1024}, {self.config.backup_count})

[formatter_standardFormatter]
format={self.config.log_format}
datefmt=%Y-%m-%d %H:%M:%S

[formatter_structuredFormatter]
class=scripts.comprehensive_logging_system.StructuredFormatter
'''

        # Save configuration file
        config_file = self.results_dir / "logging.conf"
        with open(config_file, 'w') as f:
            f.write(config_content)

        return config_content

    def generate_log_analysis_script(self) -> str:
        """Generate log analysis script"""
        analysis_script = f'''#!/bin/bash
# Kokoro TTS Log Analysis Script
# Generated automatically - do not edit manually

set -e

LOG_DIR="{self.config.log_directory}"
ANALYSIS_DIR="log_analysis"

# Create analysis directory
mkdir -p "$ANALYSIS_DIR"

echo "Starting log analysis..."

# Analyze error patterns
echo "Analyzing error patterns..."
if [ -f "$LOG_DIR/error.log" ]; then
    echo "Error Summary:" > "$ANALYSIS_DIR/error_summary.txt"
    grep -E "(ERROR|CRITICAL)" "$LOG_DIR/error.log" | \\
        awk '{{print $3, $4}}' | sort | uniq -c | sort -nr >> "$ANALYSIS_DIR/error_summary.txt"

    echo "Recent Errors (last 100):" > "$ANALYSIS_DIR/recent_errors.txt"
    tail -100 "$LOG_DIR/error.log" >> "$ANALYSIS_DIR/recent_errors.txt"
fi

# Analyze API performance
echo "Analyzing API performance..."
if [ -f "$LOG_DIR/api.log" ]; then
    echo "API Endpoint Usage:" > "$ANALYSIS_DIR/api_usage.txt"
    grep "Request completed" "$LOG_DIR/api.log" | \\
        awk '{{print $6}}' | sort | uniq -c | sort -nr >> "$ANALYSIS_DIR/api_usage.txt"

    echo "Slow API Requests (>1000ms):" > "$ANALYSIS_DIR/slow_requests.txt"
    grep "Request completed" "$LOG_DIR/api.log" | \\
        awk '{{if ($NF > 1000) print $0}}' >> "$ANALYSIS_DIR/slow_requests.txt"

    echo "API Status Codes:" > "$ANALYSIS_DIR/status_codes.txt"
    grep "Request completed" "$LOG_DIR/api.log" | \\
        awk '{{print $(NF-2)}}' | sort | uniq -c | sort -nr >> "$ANALYSIS_DIR/status_codes.txt"
fi

# Analyze performance metrics
echo "Analyzing performance metrics..."
if [ -f "$LOG_DIR/performance.log" ]; then
    echo "Performance Operations:" > "$ANALYSIS_DIR/performance_summary.txt"
    grep "Performance:" "$LOG_DIR/performance.log" | \\
        awk '{{print $3}}' | sort | uniq -c | sort -nr >> "$ANALYSIS_DIR/performance_summary.txt"

    echo "Slow Operations (>5s):" > "$ANALYSIS_DIR/slow_operations.txt"
    grep "Performance:" "$LOG_DIR/performance.log" | \\
        awk '{{if ($NF > 5) print $0}}' >> "$ANALYSIS_DIR/slow_operations.txt"
fi

# Analyze security events
echo "Analyzing security events..."
if [ -f "$LOG_DIR/security.log" ]; then
    echo "Security Event Summary:" > "$ANALYSIS_DIR/security_summary.txt"
    grep -E "(authentication|authorization|suspicious)" "$LOG_DIR/security.log" | \\
        awk '{{print $4}}' | sort | uniq -c | sort -nr >> "$ANALYSIS_DIR/security_summary.txt"

    echo "Failed Authentication Attempts:" > "$ANALYSIS_DIR/auth_failures.txt"
    grep "Authentication failed" "$LOG_DIR/security.log" >> "$ANALYSIS_DIR/auth_failures.txt"
fi

# Generate summary report
echo "Generating summary report..."
cat > "$ANALYSIS_DIR/analysis_report.txt" << EOF
Kokoro TTS Log Analysis Report
Generated: $(date)
Analysis Period: Last 24 hours

=== ERROR ANALYSIS ===
$(if [ -f "$ANALYSIS_DIR/error_summary.txt" ]; then head -10 "$ANALYSIS_DIR/error_summary.txt"; else echo "No error log found"; fi)

=== API PERFORMANCE ===
$(if [ -f "$ANALYSIS_DIR/api_usage.txt" ]; then head -10 "$ANALYSIS_DIR/api_usage.txt"; else echo "No API log found"; fi)

=== SECURITY EVENTS ===
$(if [ -f "$ANALYSIS_DIR/security_summary.txt" ]; then head -10 "$ANALYSIS_DIR/security_summary.txt"; else echo "No security log found"; fi)

=== RECOMMENDATIONS ===
$(if [ -f "$ANALYSIS_DIR/slow_requests.txt" ] && [ -s "$ANALYSIS_DIR/slow_requests.txt" ]; then echo "- Investigate slow API requests"; fi)
$(if [ -f "$ANALYSIS_DIR/slow_operations.txt" ] && [ -s "$ANALYSIS_DIR/slow_operations.txt" ]; then echo "- Optimize slow operations"; fi)
$(if [ -f "$ANALYSIS_DIR/auth_failures.txt" ] && [ -s "$ANALYSIS_DIR/auth_failures.txt" ]; then echo "- Review authentication failures"; fi)
EOF

echo "Log analysis completed. Results saved to $ANALYSIS_DIR/"
echo "Summary report: $ANALYSIS_DIR/analysis_report.txt"
'''

        # Save analysis script
        script_file = self.results_dir / "analyze_logs.sh"
        with open(script_file, 'w') as f:
            f.write(analysis_script)
        os.chmod(script_file, 0o755)

        return analysis_script

    def test_logging_system(self) -> Dict[str, Any]:
        """Test the logging system"""
        test_results = {
            "setup_test": False,
            "console_logging": False,
            "file_logging": False,
            "structured_logging": False,
            "performance_logging": False,
            "security_logging": False,
            "api_logging": False,
            "log_files_created": [],
            "errors": []
        }

        try:
            # Test setup
            setup_result = self.setup_logging()
            test_results["setup_test"] = setup_result["success"]

            # Test different types of logging
            main_logger = self.loggers["main"]

            # Test basic logging
            main_logger.info("Test info message")
            main_logger.warning("Test warning message")
            main_logger.error("Test error message")
            test_results["console_logging"] = True

            # Test performance logging
            if self.performance_logger:
                self.performance_logger.start_timer("test_operation")
                time.sleep(0.1)
                self.performance_logger.end_timer("test_operation", "Test Operation")
                self.performance_logger.log_metric("test_metric", 42.0, "units")
                test_results["performance_logging"] = True

            # Test security logging
            if self.security_logger:
                self.security_logger.log_authentication_attempt("test_user", True, "127.0.0.1")
                self.security_logger.log_authorization_failure("test_user", "test_resource", "read")
                self.security_logger.log_suspicious_activity("test_activity", "Test suspicious activity")
                test_results["security_logging"] = True

            # Test API logging
            if self.api_logger:
                self.api_logger.log_request("GET", "/test", 200, 150.5, 1024, 2048)
                self.api_logger.log_error("POST", "/test", "Test error")
                test_results["api_logging"] = True

            # Check log files
            log_dir = Path(self.config.log_directory)
            if log_dir.exists():
                log_files = list(log_dir.glob("*.log"))
                test_results["log_files_created"] = [f.name for f in log_files]
                test_results["file_logging"] = len(log_files) > 0

            # Test structured logging
            if self.config.enable_structured_logging:
                test_results["structured_logging"] = True

        except Exception as e:
            test_results["errors"].append(str(e))

        return test_results

    def run_comprehensive_logging_setup(self) -> Dict[str, Any]:
        """Run comprehensive logging system setup"""
        logging.info("Starting comprehensive logging system setup...")

        # Setup logging system
        setup_result = self.setup_logging()

        # Generate additional files
        middleware_code = self.generate_logging_middleware()
        config_content = self.generate_logging_config_file()
        analysis_script = self.generate_log_analysis_script()

        # Test the system
        test_results = self.test_logging_system()

        # Compile results
        results = {
            "setup_timestamp": time.time(),
            "logging_configuration": asdict(self.config),
            "setup_result": setup_result,
            "test_results": test_results,
            "generated_files": {
                "middleware": "logging_middleware.py",
                "config": "logging.conf",
                "analysis_script": "analyze_logs.sh"
            },
            "specialized_loggers": {
                "performance": self.performance_logger is not None,
                "security": self.security_logger is not None,
                "api": self.api_logger is not None
            },
            "setup_summary": self._generate_logging_summary(setup_result, test_results),
            "next_steps": self._generate_logging_next_steps(test_results)
        }

        # Save complete configuration
        results_file = self.results_dir / f"logging_setup_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        main_logger = self.loggers.get("main")
        if main_logger:
            main_logger.info(f"Comprehensive logging setup completed. Results saved to: {results_file}")

        return results

    def _generate_logging_summary(self, setup_result: Dict[str, Any],
                                 test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate logging setup summary"""

        successful_tests = sum(1 for key, value in test_results.items()
                             if key != "errors" and key != "log_files_created" and value is True)
        total_tests = len([key for key in test_results.keys()
                          if key != "errors" and key != "log_files_created"])

        summary = {
            "setup_successful": setup_result.get("success", False),
            "handlers_configured": setup_result.get("handlers_configured", 0),
            "test_success_rate": f"{successful_tests}/{total_tests}",
            "test_percentage": round((successful_tests / total_tests * 100), 1) if total_tests > 0 else 0,
            "log_files_created": len(test_results.get("log_files_created", [])),
            "structured_logging_enabled": self.config.enable_structured_logging,
            "specialized_loggers_enabled": {
                "performance": self.config.enable_performance_logging,
                "security": self.config.enable_security_logging,
                "api": self.config.enable_api_logging
            },
            "errors_encountered": len(test_results.get("errors", [])),
            "production_ready": (
                setup_result.get("success", False) and
                successful_tests >= total_tests * 0.8 and
                len(test_results.get("errors", [])) == 0
            )
        }

        return summary

    def _generate_logging_next_steps(self, test_results: Dict[str, Any]) -> List[str]:
        """Generate next steps for logging deployment"""
        next_steps = [
            "Integrate logging middleware into your FastAPI application",
            "Configure log rotation and archival policies",
            "Set up log monitoring and alerting systems",
            "Test logging performance under load",
            "Configure centralized log aggregation (ELK stack, Splunk, etc.)",
            "Set up log-based metrics and dashboards",
            "Implement log retention policies",
            "Configure secure log transmission for remote logging",
            "Test log analysis scripts with production data",
            "Document logging procedures for operations team"
        ]

        # Add specific recommendations based on test results
        if not test_results.get("file_logging", False):
            next_steps.insert(0, "Fix file logging configuration issues")

        if not test_results.get("structured_logging", False):
            next_steps.append("Enable structured logging for better log analysis")

        if test_results.get("errors"):
            next_steps.insert(0, "Resolve logging system errors before deployment")

        if len(test_results.get("log_files_created", [])) == 0:
            next_steps.insert(0, "Verify log directory permissions and configuration")

        return next_steps

def main():
    """Main function to run comprehensive logging setup"""
    manager = ComprehensiveLoggingManager()

    try:
        # Run comprehensive logging setup
        results = manager.run_comprehensive_logging_setup()

        print("\n" + "="*80)
        print("COMPREHENSIVE LOGGING SYSTEM SUMMARY")
        print("="*80)

        summary = results["setup_summary"]
        config = results["logging_configuration"]

        print(f"Setup Status: {'✅ Success' if summary['setup_successful'] else '❌ Failed'}")
        print(f"Test Results: {summary['test_success_rate']} ({summary['test_percentage']:.1f}%)")
        print(f"Handlers Configured: {summary['handlers_configured']}")
        print(f"Log Files Created: {summary['log_files_created']}")

        print(f"\nLogging Configuration:")
        print(f"  Log Level: {config['log_level']}")
        print(f"  Log Directory: {config['log_directory']}")
        print(f"  Structured Logging: {'✅' if config['enable_structured_logging'] else '❌'}")
        print(f"  File Rotation: {'✅' if config['enable_rotation'] else '❌'}")
        print(f"  Max File Size: {config['max_file_size_mb']}MB")
        print(f"  Backup Count: {config['backup_count']}")

        print(f"\nSpecialized Loggers:")
        specialized = summary["specialized_loggers_enabled"]
        print(f"  Performance: {'✅' if specialized['performance'] else '❌'}")
        print(f"  Security: {'✅' if specialized['security'] else '❌'}")
        print(f"  API: {'✅' if specialized['api'] else '❌'}")

        print(f"\nTest Results:")
        test_results = results["test_results"]
        for test_name, result in test_results.items():
            if test_name not in ["errors", "log_files_created"]:
                emoji = "✅" if result else "❌"
                print(f"  {emoji} {test_name.replace('_', ' ').title()}")

        if test_results.get("errors"):
            print(f"\nErrors:")
            for error in test_results["errors"]:
                print(f"  ❌ {error}")

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
        print(f"Logging setup failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
