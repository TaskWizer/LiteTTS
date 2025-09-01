#!/usr/bin/env python3
"""
Error handling for TTS API
"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import traceback

from ..models import TTSError, VoiceNotFoundError, ModelLoadError, AudioGenerationError

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Handles errors and exceptions in the TTS API"""
    
    def __init__(self):
        self.error_counts = {}
        logger.info("Error handler initialized")
    
    def handle_synthesis_error(self, error: Exception) -> JSONResponse:
        """Handle synthesis-related errors"""
        self._log_error(error)
        
        if isinstance(error, VoiceNotFoundError):
            return self._create_error_response(
                status_code=404,
                error_code="VOICE_NOT_FOUND",
                message=error.message,
                details=error.details
            )
        
        elif isinstance(error, ModelLoadError):
            return self._create_error_response(
                status_code=503,
                error_code="MODEL_LOAD_ERROR", 
                message=error.message,
                details=error.details
            )
        
        elif isinstance(error, AudioGenerationError):
            return self._create_error_response(
                status_code=500,
                error_code="AUDIO_GENERATION_ERROR",
                message=error.message,
                details=error.details
            )
        
        elif isinstance(error, TTSError):
            return self._create_error_response(
                status_code=500,
                error_code=error.error_code,
                message=error.message,
                details=error.details
            )
        
        else:
            return self._create_error_response(
                status_code=500,
                error_code="SYNTHESIS_ERROR",
                message="An error occurred during synthesis",
                details={"original_error": str(error)}
            )
    
    def handle_validation_error(self, errors: list) -> JSONResponse:
        """Handle request validation errors"""
        self._log_validation_error(errors)
        
        return self._create_error_response(
            status_code=400,
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"validation_errors": errors}
        )
    
    def handle_rate_limit_error(self, retry_after: int = 60) -> JSONResponse:
        """Handle rate limiting errors"""
        logger.warning("Rate limit exceeded")
        
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests",
                    "details": {
                        "retry_after_seconds": retry_after
                    }
                }
            },
            headers={"Retry-After": str(retry_after)}
        )
    
    def handle_timeout_error(self, timeout_seconds: float) -> JSONResponse:
        """Handle request timeout errors"""
        logger.warning(f"Request timeout after {timeout_seconds}s")
        
        return self._create_error_response(
            status_code=408,
            error_code="REQUEST_TIMEOUT",
            message="Request timed out",
            details={"timeout_seconds": timeout_seconds}
        )
    
    def handle_service_unavailable(self, reason: str = "Service temporarily unavailable") -> JSONResponse:
        """Handle service unavailable errors"""
        logger.error(f"Service unavailable: {reason}")
        
        return self._create_error_response(
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
            message=reason,
            details={}
        )
    
    def handle_generic_error(self, error: Exception) -> JSONResponse:
        """Handle generic/unexpected errors"""
        self._log_error(error)
        
        return self._create_error_response(
            status_code=500,
            error_code="INTERNAL_ERROR",
            message="An internal error occurred",
            details={"error_type": type(error).__name__}
        )
    
    def handle_not_found_error(self, resource: str, identifier: str) -> JSONResponse:
        """Handle resource not found errors"""
        logger.warning(f"Resource not found: {resource} '{identifier}'")
        
        return self._create_error_response(
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            message=f"{resource} not found",
            details={"resource": resource, "identifier": identifier}
        )
    
    def handle_method_not_allowed(self, method: str, path: str) -> JSONResponse:
        """Handle method not allowed errors"""
        logger.warning(f"Method not allowed: {method} {path}")
        
        return self._create_error_response(
            status_code=405,
            error_code="METHOD_NOT_ALLOWED",
            message=f"Method {method} not allowed for {path}",
            details={"method": method, "path": path}
        )
    
    def _create_error_response(self, status_code: int, error_code: str, 
                              message: str, details: Dict[str, Any]) -> JSONResponse:
        """Create standardized error response"""
        # Track error counts
        self.error_counts[error_code] = self.error_counts.get(error_code, 0) + 1
        
        error_response = {
            "error": {
                "code": error_code,
                "message": message,
                "details": details,
                "timestamp": self._get_timestamp()
            }
        }
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )
    
    def _log_error(self, error: Exception):
        """Log error with appropriate level"""
        error_msg = f"Error: {type(error).__name__}: {str(error)}"
        
        if isinstance(error, (VoiceNotFoundError, TTSError)):
            logger.warning(error_msg)
        else:
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
    
    def _log_validation_error(self, errors: list):
        """Log validation errors"""
        logger.warning(f"Validation errors: {errors}")
    
    def _get_timestamp(self) -> float:
        """Get current timestamp"""
        import time
        return time.time()
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_errors = sum(self.error_counts.values())
        
        return {
            "total_errors": total_errors,
            "error_counts": self.error_counts.copy(),
            "most_common_error": max(self.error_counts.items(), key=lambda x: x[1])[0] if self.error_counts else None
        }
    
    def reset_error_stats(self):
        """Reset error statistics"""
        self.error_counts.clear()
        logger.info("Error statistics reset")

class APIExceptionHandler:
    """Global exception handler for the API"""
    
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
    
    async def handle_http_exception(self, request, exc: HTTPException):
        """Handle HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "details": {},
                    "timestamp": self.error_handler._get_timestamp()
                }
            }
        )
    
    async def handle_generic_exception(self, request, exc: Exception):
        """Handle generic exceptions"""
        logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
        logger.debug(traceback.format_exc())
        
        return self.error_handler.handle_generic_error(exc)
    
    async def handle_validation_exception(self, request, exc):
        """Handle Pydantic validation exceptions"""
        errors = []
        
        if hasattr(exc, 'errors'):
            for error in exc.errors():
                field = " -> ".join(str(loc) for loc in error['loc'])
                errors.append(f"{field}: {error['msg']}")
        else:
            errors.append(str(exc))
        
        return self.error_handler.handle_validation_error(errors)