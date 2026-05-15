"""
website_session.py
Individual website measurement session and metrics collection.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


@dataclass
class WebsiteMetrics:
    """Container for metrics collected from a single website visit."""
    
    # Site identification
    url: str
    name: str
    category: str
    
    # Timing metrics (milliseconds)
    page_load_time_ms: Optional[float] = None
    dom_content_loaded_ms: Optional[float] = None
    time_to_first_byte_ms: Optional[float] = None
    
    # Response metrics
    http_status_code: Optional[int] = None
    response_size_bytes: Optional[int] = None
    redirect_count: int = 0
    
    # Request metrics
    total_requests: Optional[int] = None
    failed_requests: Optional[int] = None
    blocked_requests: Optional[int] = None
    
    # Error tracking
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Metadata
    timestamp: str = None
    browser: str = "chromium"
    user_agent: Optional[str] = None
    
    # Flags
    is_success: bool = False
    is_timeout: bool = False
    is_ssl_error: bool = False
    is_http_error: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        data = asdict(self)
        # Convert None values to empty strings or 0 for cleaner JSON
        return data
    
    def to_json(self) -> str:
        """Convert metrics to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebsiteMetrics':
        """Create metrics instance from dictionary."""
        return cls(**data)


@dataclass
class WebsiteSession:
    """Represents a single measurement session for a website."""
    
    url: str
    name: str
    category: str
    metrics: WebsiteMetrics = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = WebsiteMetrics(
                url=self.url,
                name=self.name,
                category=self.category
            )
    
    def record_success(self):
        """Mark session as successful."""
        self.metrics.is_success = True
    
    def record_timeout(self):
        """Mark session as timed out."""
        self.metrics.is_timeout = True
        self.metrics.is_success = False
    
    def record_ssl_error(self):
        """Mark session as SSL error."""
        self.metrics.is_ssl_error = True
        self.metrics.is_success = False
    
    def record_http_error(self, status_code: int):
        """Mark session with HTTP error."""
        self.metrics.is_http_error = True
        self.metrics.http_status_code = status_code
        self.metrics.is_success = (200 <= status_code < 300)
    
    def get_performance_dict(self) -> Dict[str, Any]:
        """Get performance-focused metrics."""
        return {
            "url": self.metrics.url,
            "name": self.metrics.name,
            "category": self.metrics.category,
            "page_load_time_ms": self.metrics.page_load_time_ms,
            "dom_content_loaded_ms": self.metrics.dom_content_loaded_ms,
            "time_to_first_byte_ms": self.metrics.time_to_first_byte_ms,
            "response_size_bytes": self.metrics.response_size_bytes,
            "total_requests": self.metrics.total_requests,
            "failed_requests": self.metrics.failed_requests,
            "http_status_code": self.metrics.http_status_code,
            "is_success": self.metrics.is_success,
            "timestamp": self.metrics.timestamp
        }
