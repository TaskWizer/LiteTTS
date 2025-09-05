#!/usr/bin/env python3
"""
Logging configuration for Kokoro ONNX TTS API
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

# Import platform-safe emoji utilities
try:
    from LiteTTS.utils.platform_emojis import EMOJIS, get_emoji, format_log_message
except ImportError:
    # Fallback if the utility module is not available
    def get_emoji(name: str, fallback: str = '[?]') -> str:
        return fallback

    def format_log_message(emoji_name: str, message: str) -> str:
        return f"[{emoji_name.upper()}] {message}"

    EMOJIS = {}

class PerformanceFilter(logging.Filter):
    """Filter for performance-related log messages"""
    def filter(self, record):
        message = record.getMessage()
        return ('RTF:' in message or 'Performance:' in message or
                'performance' in message.lower() or hasattr(record, 'performance'))

class CacheFilter(logging.Filter):
    """Filter for cache-related log messages"""
    def filter(self, record):
        message = record.getMessage()
        return ('cache' in message.lower() or 'Cache' in message or
                hasattr(record, 'cache_stats'))

def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    file_path: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    json_format: bool = False,
    include_trace_id: bool = True
) -> None:
    """
    Set up structured logging for the application with enhanced features
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        file_path: Optional file path for log output
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        json_format: Use JSON format for structured logging
        include_trace_id: Include trace ID in log messages
    """
    
    # Default format with better structure
    if format_string is None:
        if json_format:
            format_string = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        else:
            format_string = "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    if json_format:
        formatter = JSONFormatter(format_string)
    else:
        formatter = ColoredFormatter(format_string)
    
    # Console handler with enhanced formatting and Windows encoding support
    # Configure console output stream with proper encoding for Windows
    import platform
    if platform.system() == "Windows":
        # Try to configure console for UTF-8 output on Windows
        try:
            # Attempt to reconfigure stdout for UTF-8
            import codecs
            import locale

            # Get the current console encoding
            console_encoding = sys.stdout.encoding or locale.getpreferredencoding()

            # If we're using a problematic encoding, try to use UTF-8 with error handling
            if console_encoding.lower() in ['cp1252', 'windows-1252']:
                # Create a UTF-8 writer with error handling for Windows console
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach(), errors='replace')
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach(), errors='replace')
        except (AttributeError, OSError, ImportError):
            # If reconfiguration fails, we'll rely on the emoji fallback system
            pass

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(console_handler)
    
    # Set up comprehensive logging to docs/logs directory
    log_dir = Path("docs/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Main application log
    main_log_path = log_dir / "kokoro_tts.log"
    main_handler = logging.handlers.RotatingFileHandler(
        main_log_path,
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10
    )
    main_handler.setFormatter(logging.Formatter(format_string))
    main_handler.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(main_handler)

    # Performance metrics log
    performance_log_path = log_dir / "performance.log"
    performance_handler = logging.handlers.RotatingFileHandler(
        performance_log_path,
        maxBytes=20*1024*1024,  # 20MB
        backupCount=5
    )
    performance_handler.setFormatter(logging.Formatter(format_string))
    performance_handler.setLevel(logging.INFO)
    performance_handler.addFilter(PerformanceFilter())
    root_logger.addHandler(performance_handler)

    # Cache statistics log
    cache_log_path = log_dir / "cache.log"
    cache_handler = logging.handlers.RotatingFileHandler(
        cache_log_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3
    )
    cache_handler.setFormatter(logging.Formatter(format_string))
    cache_handler.setLevel(logging.INFO)
    cache_handler.addFilter(CacheFilter())
    root_logger.addHandler(cache_handler)

    # Error log
    error_log_path = log_dir / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path,
        maxBytes=20*1024*1024,  # 20MB
        backupCount=5
    )
    error_handler.setFormatter(logging.Formatter(format_string))
    error_handler.setLevel(logging.WARNING)
    root_logger.addHandler(error_handler)

    # Structured JSON log
    json_log_path = log_dir / "structured.jsonl"
    json_handler = logging.handlers.RotatingFileHandler(
        json_log_path,
        maxBytes=30*1024*1024,  # 30MB
        backupCount=5
    )
    json_handler.setFormatter(JSONFormatter())
    json_handler.setLevel(logging.INFO)
    root_logger.addHandler(json_handler)

    # Custom file handler (if file path provided)
    if file_path:
        file_path_obj = Path(file_path)
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Use JSON format for file logging for better parsing
        file_formatter = JSONFormatter() if json_format else logging.Formatter(format_string)

        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(getattr(logging, level.upper()))
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels for external libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("onnxruntime").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    
    # Log setup completion
    logger = logging.getLogger("kokoro.logging")
    logger.info(format_log_message('clipboard', 'Comprehensive logging system initialized'))
    logger.info(format_log_message('folder', f'Log directory: {log_dir.absolute()}'))
    logger.info(format_log_message('chart', f'Log level: {level}'))
    logger.info(format_log_message('memo', 'Log files: main, performance, cache, errors, structured'))
    if file_path:
        logger.info(format_log_message('page', f'Custom log file: {file_path}'))


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        import json
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry)

class RequestLogger:
    """Enhanced context manager for request-specific logging with metrics"""
    
    def __init__(self, request_id: str, logger: logging.Logger, extra_context: Optional[dict] = None):
        self.request_id = request_id
        self.logger = logger
        self.start_time = None
        self.context = extra_context or {}
        self.metrics = {}
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        context_str = f" | Context: {self.context}" if self.context else ""
        self.logger.info(format_log_message('rocket', f'Request {self.request_id} started{context_str}'),
                        extra={"request_id": self.request_id, "event": "request_start", **self.context})
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time if self.start_time else 0
        self.metrics["duration"] = duration
        
        if exc_type is None:
            self.logger.info(format_log_message('check', f'Request {self.request_id} completed in {duration:.3f}s'),
                           extra={"request_id": self.request_id, "event": "request_complete",
                                 "duration": duration, "metrics": self.metrics, **self.context})
        else:
            self.logger.error(format_log_message('cross', f'Request {self.request_id} failed in {duration:.3f}s: {exc_val}'),
                            extra={"request_id": self.request_id, "event": "request_error",
                                  "duration": duration, "error": str(exc_val), "metrics": self.metrics, **self.context})
    
    def info(self, message: str, **kwargs):
        self.logger.info(f"[{self.request_id}] {message}", 
                        extra={"request_id": self.request_id, **kwargs})
    
    def error(self, message: str, **kwargs):
        self.logger.error(f"[{self.request_id}] {message}", 
                         extra={"request_id": self.request_id, **kwargs})
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(f"[{self.request_id}] {message}", 
                           extra={"request_id": self.request_id, **kwargs})
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(f"[{self.request_id}] {message}", 
                         extra={"request_id": self.request_id, **kwargs})
    
    def add_metric(self, key: str, value: any):
        """Add a metric to be logged with the request"""
        self.metrics[key] = value
    
    def add_context(self, key: str, value: any):
        """Add context information to be logged with the request"""
        self.context[key] = value


def get_request_logger(request_id: str, logger_name: str = "kokoro.request", 
                      extra_context: Optional[dict] = None) -> RequestLogger:
    """Get a request-specific logger with optional context"""
    logger = logging.getLogger(logger_name)
    return RequestLogger(request_id, logger, extra_context)


def setup_performance_logging():
    """Set up performance-specific logging"""
    perf_logger = logging.getLogger("kokoro.performance")
    perf_logger.setLevel(logging.INFO)
    
    # Create a separate handler for performance logs if needed
    return perf_logger


def log_system_info():
    """Log system information at startup"""
    import platform
    import psutil
    import sys
    
    logger = logging.getLogger("kokoro.system")
    
    logger.info("System Information:")
    logger.info(f"  Platform: {platform.platform()}")
    logger.info(f"  Python: {sys.version}")
    logger.info(f"  CPU Count: {psutil.cpu_count()}")
    logger.info(f"  Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    
    # Check for CUDA availability
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        logger.info(f"  CUDA Available: {cuda_available}")
        if cuda_available:
            logger.info(f"  CUDA Device: {torch.cuda.get_device_name(0)}")
    except ImportError:
        logger.info("  CUDA: PyTorch not available")