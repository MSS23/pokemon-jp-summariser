"""
FastAPI backend for Pokemon VGC Article Translator
Compliant with Google Gemini API Terms & Generative AI Policy
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import hashlib
from typing import Dict, Any
import os
from contextlib import asynccontextmanager

# Import backend modules
from .compliance import ComplianceChecker
from .safety import SafetyFilter
from .rate_limit import RateLimiter
from .fetcher import SafeHTMLFetcher
from .gemini_client import GeminiClient

# Import shared models
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from shared.models import (
    HealthResponse,
    CheckRequest,
    CheckResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    ErrorResponse
)
from shared.logging import StructuredLogger

# Initialize components
compliance_checker = ComplianceChecker()
safety_filter = SafetyFilter()
rate_limiter = RateLimiter()
html_fetcher = SafeHTMLFetcher()
structured_logger = StructuredLogger()

# Provider control
PROVIDER_ENABLED_GEMINI = os.getenv("PROVIDER_ENABLED_GEMINI", "true").lower() == "true"
gemini_client = GeminiClient() if PROVIDER_ENABLED_GEMINI else None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    structured_logger.log_system_event("application_startup", {
        "provider_enabled": PROVIDER_ENABLED_GEMINI,
        "gemini_configured": gemini_client is not None
    })
    yield
    # Shutdown
    structured_logger.log_system_event("application_shutdown", {})

app = FastAPI(
    title="Pokemon VGC Article Translator API",
    description="Compliant backend for Pokemon VGC content analysis using Google Gemini AI",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def get_client_identifier(request: Request) -> tuple[str, str]:
    """Get hashed IP and session ID for rate limiting"""
    client_ip = request.client.host or "unknown"
    hashed_ip = hashlib.sha256(f"{client_ip}".encode()).hexdigest()[:16]

    # Try to get session ID from headers
    session_id = request.headers.get("X-Session-ID", "anonymous")

    return hashed_ip, session_id

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        provider_enabled=PROVIDER_ENABLED_GEMINI,
        gemini_available=gemini_client is not None,
        timestamp=int(time.time())
    )

@app.post("/check", response_model=CheckResponse)
async def check_url(request: CheckRequest, http_request: Request):
    """
    Check URL compliance without running LLM analysis
    Validates: domain allowlist, robots.txt, content headers
    """
    hashed_ip, session_id = get_client_identifier(http_request)
    request_id = structured_logger.generate_request_id()

    start_time = time.time()

    # Log request
    structured_logger.log_request(request_id, {
        "endpoint": "check",
        "url": request.url,
        "hashed_ip": hashed_ip,
        "session_id": session_id
    })

    try:
        # Step 1: Domain allowlist check
        if not compliance_checker.is_domain_allowed(request.url):
            error_msg = "Domain not in allowlist - only approved Pokemon community sites allowed"
            structured_logger.log_compliance_decision(request_id, {
                "step": "domain_check",
                "decision": "blocked",
                "reason": "domain_not_allowed",
                "domain": compliance_checker.extract_domain(request.url)
            })

            return CheckResponse(
                status="blocked",
                step_failed="domain_check",
                reason=error_msg,
                domain=compliance_checker.extract_domain(request.url),
                robots_allowed=None,
                content_type=None,
                size_estimate=None
            )

        # Step 2: Robots.txt check
        robots_allowed = compliance_checker.robots_allows(request.url)
        if not robots_allowed:
            error_msg = "robots.txt disallows crawling for this URL"
            structured_logger.log_compliance_decision(request_id, {
                "step": "robots_check",
                "decision": "blocked",
                "reason": "robots_disallowed",
                "domain": compliance_checker.extract_domain(request.url)
            })

            return CheckResponse(
                status="blocked",
                step_failed="robots_check",
                reason=error_msg,
                domain=compliance_checker.extract_domain(request.url),
                robots_allowed=False,
                content_type=None,
                size_estimate=None
            )

        # Step 3: HEAD request to check content type and size
        try:
            headers = html_fetcher.check_headers(request.url)
            content_type = headers.get("content-type", "unknown")
            content_length = headers.get("content-length", "unknown")

            # Check content type
            if not compliance_checker.is_content_type_allowed(content_type):
                error_msg = f"Content type not allowed: {content_type} (only text/html permitted)"
                structured_logger.log_compliance_decision(request_id, {
                    "step": "content_type_check",
                    "decision": "blocked",
                    "reason": "invalid_content_type",
                    "content_type": content_type
                })

                return CheckResponse(
                    status="blocked",
                    step_failed="content_type_check",
                    reason=error_msg,
                    domain=compliance_checker.extract_domain(request.url),
                    robots_allowed=True,
                    content_type=content_type,
                    size_estimate=content_length
                )

        except Exception as e:
            error_msg = f"Failed to check URL headers: {str(e)}"
            structured_logger.log_compliance_decision(request_id, {
                "step": "header_check",
                "decision": "blocked",
                "reason": "header_check_failed",
                "error": str(e)
            })

            return CheckResponse(
                status="blocked",
                step_failed="header_check",
                reason=error_msg,
                domain=compliance_checker.extract_domain(request.url),
                robots_allowed=True,
                content_type=None,
                size_estimate=None
            )

        # All checks passed
        structured_logger.log_compliance_decision(request_id, {
            "step": "all_checks_complete",
            "decision": "allowed",
            "domain": compliance_checker.extract_domain(request.url),
            "robots_allowed": robots_allowed,
            "content_type": content_type,
            "processing_time": time.time() - start_time
        })

        return CheckResponse(
            status="allowed",
            step_failed=None,
            reason="All compliance checks passed",
            domain=compliance_checker.extract_domain(request.url),
            robots_allowed=robots_allowed,
            content_type=content_type,
            size_estimate=content_length
        )

    except Exception as e:
        structured_logger.log_error(request_id, {
            "step": "check_general_error",
            "error": str(e),
            "processing_time": time.time() - start_time
        })

        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_content(request: AnalyzeRequest, http_request: Request, background_tasks: BackgroundTasks):
    """
    Full analysis pipeline: compliance checks → fetch → safety → Gemini analysis
    """
    hashed_ip, session_id = get_client_identifier(http_request)
    request_id = structured_logger.generate_request_id()

    start_time = time.time()

    # Log request
    structured_logger.log_request(request_id, {
        "endpoint": "analyze",
        "url": request.url,
        "hashed_ip": hashed_ip,
        "session_id": session_id,
        "options": request.options
    })

    try:
        # Step 0: Provider check
        if not PROVIDER_ENABLED_GEMINI or gemini_client is None:
            structured_logger.log_compliance_decision(request_id, {
                "step": "provider_check",
                "decision": "blocked",
                "reason": "provider_disabled"
            })

            raise HTTPException(
                status_code=503,
                detail={
                    "status": "provider_disabled",
                    "message": "Gemini API is temporarily disabled. Please try again later or contact support."
                }
            )

        # Step 1: Rate limiting
        if not rate_limiter.allow_request("analyze", hashed_ip, max_per_hour=5):
            structured_logger.log_compliance_decision(request_id, {
                "step": "rate_limit_check",
                "decision": "blocked",
                "reason": "rate_limit_exceeded",
                "hashed_ip": hashed_ip
            })

            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Maximum 5 analyses per hour per IP address."
            )

        # Check concurrent requests
        if not rate_limiter.allow_request("concurrent", hashed_ip, max_per_hour=1):
            structured_logger.log_compliance_decision(request_id, {
                "step": "concurrent_limit_check",
                "decision": "blocked",
                "reason": "concurrent_limit_exceeded",
                "hashed_ip": hashed_ip
            })

            raise HTTPException(
                status_code=429,
                detail="Concurrent request limit exceeded. Please wait for current analysis to complete."
            )

        # Step 2: Run compliance checks (same as /check)
        if not compliance_checker.is_domain_allowed(request.url):
            structured_logger.log_compliance_decision(request_id, {
                "step": "domain_check",
                "decision": "blocked",
                "reason": "domain_not_allowed"
            })

            raise HTTPException(
                status_code=403,
                detail="Domain not allowed - only approved Pokemon community sites permitted"
            )

        if not compliance_checker.robots_allows(request.url):
            structured_logger.log_compliance_decision(request_id, {
                "step": "robots_check",
                "decision": "blocked",
                "reason": "robots_disallowed"
            })

            raise HTTPException(
                status_code=403,
                detail="robots.txt disallows crawling for this URL"
            )

        # Step 3: Fetch HTML content safely
        try:
            html_content, metadata = html_fetcher.fetch_html(request.url)

            # Check for paywall/login gates
            if compliance_checker.looks_paywalled_or_gated(html_content[:5000]):  # Check first 5KB
                structured_logger.log_compliance_decision(request_id, {
                    "step": "paywall_check",
                    "decision": "blocked",
                    "reason": "content_appears_gated"
                })

                raise HTTPException(
                    status_code=403,
                    detail="Content appears to be behind paywall or login gate"
                )

        except Exception as e:
            structured_logger.log_compliance_decision(request_id, {
                "step": "fetch_content",
                "decision": "blocked",
                "reason": "fetch_failed",
                "error": str(e)
            })

            raise HTTPException(status_code=400, detail=f"Failed to fetch content: {str(e)}")

        # Step 4: Safety and scope validation
        safety_result = safety_filter.precheck_text_for_scope(html_content)
        if not safety_result.allowed:
            structured_logger.log_compliance_decision(request_id, {
                "step": "safety_check",
                "decision": "blocked",
                "reason": safety_result.reason,
                "categories": safety_result.blocked_categories
            })

            raise HTTPException(
                status_code=403,
                detail=f"Content blocked by safety filter: {safety_result.reason}"
            )

        # Step 5: PII redaction and content sanitization
        clean_content, redaction_stats = safety_filter.redact_pii(html_content)

        # Step 6: Call Gemini API
        try:
            analysis_result = await gemini_client.analyze(
                content=clean_content,
                options=request.options,
                session_id=session_id
            )

            # Log successful analysis
            structured_logger.log_analysis_success(request_id, {
                "content_length": len(clean_content),
                "redactions": redaction_stats.dict(),
                "processing_time": time.time() - start_time,
                "gemini_tokens_used": analysis_result.get("tokens_used", 0)
            })

            return AnalyzeResponse(
                status="success",
                analysis=analysis_result,
                metadata={
                    "domain": compliance_checker.extract_domain(request.url),
                    "robots_allowed": True,
                    "content_type": metadata.get("content_type", "text/html"),
                    "original_size": metadata.get("size", 0),
                    "processed_size": len(clean_content),
                    "redaction_stats": redaction_stats.dict(),
                    "processing_time": time.time() - start_time
                }
            )

        except Exception as e:
            structured_logger.log_error(request_id, {
                "step": "gemini_analysis",
                "error": str(e),
                "processing_time": time.time() - start_time
            })

            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

        finally:
            # Release concurrent request slot
            rate_limiter.release_concurrent_slot("concurrent", hashed_ip)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        structured_logger.log_error(request_id, {
            "step": "analyze_general_error",
            "error": str(e),
            "processing_time": time.time() - start_time
        })

        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler for better error responses"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "timestamp": int(time.time())
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)