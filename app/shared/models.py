"""
Pydantic models for request/response schemas
Shared between FastAPI backend and Streamlit frontend
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, Any, Optional, List
from enum import Enum

class ComplianceStatus(str, Enum):
    """Status of compliance checks"""
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    ERROR = "error"

class ProviderStatus(str, Enum):
    """Provider availability status"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"

# Request Models
class CheckRequest(BaseModel):
    """Request to check URL compliance without analysis"""
    url: HttpUrl = Field(..., description="URL to check for compliance")

class AnalyzeRequest(BaseModel):
    """Request for full content analysis"""
    url: HttpUrl = Field(..., description="URL to analyze")
    options: Dict[str, Any] = Field(default_factory=dict, description="Analysis options")

# Response Models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service health status")
    provider_enabled: bool = Field(..., description="Whether Gemini provider is enabled")
    gemini_available: bool = Field(..., description="Whether Gemini client is available")
    timestamp: int = Field(..., description="Response timestamp")

class CheckResponse(BaseModel):
    """Response from URL compliance check"""
    status: ComplianceStatus = Field(..., description="Compliance check result")
    step_failed: Optional[str] = Field(None, description="Which compliance step failed")
    reason: str = Field(..., description="Human-readable reason for the result")
    domain: str = Field(..., description="Extracted domain from URL")
    robots_allowed: Optional[bool] = Field(None, description="Whether robots.txt allows crawling")
    content_type: Optional[str] = Field(None, description="Content type from headers")
    size_estimate: Optional[str] = Field(None, description="Estimated content size")

class RedactionStats(BaseModel):
    """Statistics about PII redaction"""
    emails_redacted: int = Field(default=0, description="Number of email addresses redacted")
    phone_numbers_redacted: int = Field(default=0, description="Number of phone numbers redacted")
    addresses_redacted: int = Field(default=0, description="Number of addresses redacted")
    other_pii_redacted: int = Field(default=0, description="Other PII items redacted")
    total_redactions: int = Field(default=0, description="Total redactions made")

class SafetyDecision(BaseModel):
    """Result of safety/scope validation"""
    allowed: bool = Field(..., description="Whether content is allowed")
    reason: str = Field(..., description="Reason for decision")
    blocked_categories: List[str] = Field(default_factory=list, description="Categories that triggered blocks")
    confidence: float = Field(default=1.0, description="Confidence in decision (0.0-1.0)")

class AnalysisMetadata(BaseModel):
    """Metadata about the analysis process"""
    domain: str = Field(..., description="Source domain")
    robots_allowed: bool = Field(..., description="Whether robots.txt allowed crawling")
    content_type: str = Field(..., description="Content type of source")
    original_size: int = Field(..., description="Original content size in bytes")
    processed_size: int = Field(..., description="Size after processing and redaction")
    redaction_stats: RedactionStats = Field(..., description="PII redaction statistics")
    processing_time: float = Field(..., description="Total processing time in seconds")

class AnalyzeResponse(BaseModel):
    """Response from full content analysis"""
    status: str = Field(..., description="Analysis status")
    analysis: Dict[str, Any] = Field(..., description="Analysis results from Gemini")
    metadata: AnalysisMetadata = Field(..., description="Analysis process metadata")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: bool = Field(default=True, description="Whether this is an error response")
    status_code: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Error detail message")
    timestamp: int = Field(..., description="Error timestamp")

# Logging Models
class RequestLogEntry(BaseModel):
    """Structure for request log entries"""
    request_id: str = Field(..., description="Unique request identifier")
    endpoint: str = Field(..., description="API endpoint called")
    hashed_ip: str = Field(..., description="Hashed client IP")
    session_id: str = Field(..., description="Session identifier")
    url: Optional[str] = Field(None, description="URL being processed")
    timestamp: int = Field(..., description="Request timestamp")
    user_agent: Optional[str] = Field(None, description="Client user agent")

class ComplianceLogEntry(BaseModel):
    """Structure for compliance decision log entries"""
    request_id: str = Field(..., description="Associated request ID")
    step: str = Field(..., description="Compliance check step")
    decision: str = Field(..., description="Decision result (allowed/blocked)")
    reason: str = Field(..., description="Reason for decision")
    domain: Optional[str] = Field(None, description="Domain being checked")
    timestamp: int = Field(..., description="Decision timestamp")
    additional_data: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")

class ErrorLogEntry(BaseModel):
    """Structure for error log entries"""
    request_id: str = Field(..., description="Associated request ID")
    step: str = Field(..., description="Processing step where error occurred")
    error_type: str = Field(..., description="Type/category of error")
    error_message: str = Field(..., description="Error message")
    timestamp: int = Field(..., description="Error timestamp")
    additional_data: Dict[str, Any] = Field(default_factory=dict, description="Additional error context")

class SystemLogEntry(BaseModel):
    """Structure for system event log entries"""
    event_type: str = Field(..., description="Type of system event")
    event_data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: int = Field(..., description="Event timestamp")
    service: str = Field(default="pokemon-vgc-api", description="Service name")

# Age Gate Models
class AgeVerification(BaseModel):
    """Age verification data"""
    verified: bool = Field(..., description="Whether user has verified they are 18+")
    timestamp: int = Field(..., description="Verification timestamp")
    session_id: str = Field(..., description="Session identifier")

# Rate Limiting Models
class RateLimitInfo(BaseModel):
    """Rate limit status information"""
    allowed: bool = Field(..., description="Whether request is allowed")
    limit: int = Field(..., description="Rate limit threshold")
    remaining: int = Field(..., description="Remaining requests in window")
    reset_time: int = Field(..., description="When the limit resets (timestamp)")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retry")

# Configuration Models
class DomainConfig(BaseModel):
    """Domain allowlist configuration"""
    allowed_domains: List[str] = Field(..., description="List of allowed domains")
    wildcard_patterns: List[str] = Field(default_factory=list, description="Wildcard patterns for domains")

class SafetyConfig(BaseModel):
    """Safety filter configuration"""
    blocked_keywords: List[str] = Field(..., description="Keywords that trigger blocks")
    scope_keywords: List[str] = Field(..., description="Keywords required for scope validation")
    max_content_length: int = Field(default=500000, description="Maximum content length to process")

class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""
    requests_per_hour: int = Field(default=5, description="Maximum requests per hour per IP")
    concurrent_requests: int = Field(default=1, description="Maximum concurrent requests per IP")
    window_minutes: int = Field(default=60, description="Rate limit window in minutes")

class AppConfig(BaseModel):
    """Overall application configuration"""
    provider_enabled: bool = Field(..., description="Whether Gemini provider is enabled")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key (server-side only)")
    redis_url: Optional[str] = Field(None, description="Redis connection URL")
    allowed_origins: List[str] = Field(default=["http://localhost:8501"], description="CORS allowed origins")
    domain_config: DomainConfig = Field(..., description="Domain allowlist configuration")
    safety_config: SafetyConfig = Field(..., description="Safety filter configuration")
    rate_limit_config: RateLimitConfig = Field(..., description="Rate limiting configuration")