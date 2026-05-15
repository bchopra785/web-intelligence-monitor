"""
error_handling.py
Centralized error handling and classification for web measurement failures.
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


class ErrorType(Enum):
    """Classification of measurement failures."""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    SSL_ERROR = "ssl_error"
    HTTP_ERROR = "http_error"
    DNS_ERROR = "dns_error"
    BLOCKED_REQUEST = "blocked_request"
    UNKNOWN_ERROR = "unknown_error"
    SUCCESS = "success"


@dataclass
class MeasurementError:
    """Structured error representation for a measurement."""
    error_type: ErrorType
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "details": self.details or {},
            "timestamp": self.timestamp.isoformat()
        }


def classify_error(exception: Exception, context: Optional[Dict[str, Any]] = None) -> MeasurementError:
    """
    Classify a caught exception into a structured error type.
    
    Args:
        exception: The exception that was raised
        context: Additional context about the error
        
    Returns:
        MeasurementError with classified error type
    """
    error_msg = str(exception).lower()
    context = context or {}
    
    # Timeout errors
    if "timeout" in error_msg or "timed out" in error_msg:
        return MeasurementError(
            error_type=ErrorType.TIMEOUT,
            message=f"Page load timeout: {str(exception)}",
            details=context
        )
    
    # SSL/TLS errors
    if "ssl" in error_msg or "certificate" in error_msg or "https" in error_msg:
        return MeasurementError(
            error_type=ErrorType.SSL_ERROR,
            message=f"SSL/TLS error: {str(exception)}",
            details=context
        )
    
    # DNS resolution errors
    if "dns" in error_msg or "getaddrinfo" in error_msg or "name resolution" in error_msg:
        return MeasurementError(
            error_type=ErrorType.DNS_ERROR,
            message=f"DNS resolution failed: {str(exception)}",
            details=context
        )
    
    # Connection errors
    if "connection" in error_msg or "refused" in error_msg or "reset" in error_msg:
        return MeasurementError(
            error_type=ErrorType.CONNECTION_ERROR,
            message=f"Connection error: {str(exception)}",
            details=context
        )
    
    # HTTP errors (4xx, 5xx)
    if "http" in error_msg or "status" in error_msg:
        return MeasurementError(
            error_type=ErrorType.HTTP_ERROR,
            message=f"HTTP error: {str(exception)}",
            details=context
        )
    
    # Unknown error
    return MeasurementError(
        error_type=ErrorType.UNKNOWN_ERROR,
        message=f"Unmapped error: {str(exception)}",
        details=context
    )
