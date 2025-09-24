"""
Structured logging system for compliance tracking and audit trails
All logs are in JSON format for easy parsing and analysis
"""

import json
import logging
import time
import uuid
import os
from typing import Dict, Any, Optional
from pathlib import Path

from .models import (
    RequestLogEntry,
    ComplianceLogEntry,
    ErrorLogEntry,
    SystemLogEntry
)

class StructuredLogger:
    """
    JSON structured logger for compliance tracking and audit trails
    Logs to both file and stdout for development/production flexibility
    """

    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize the structured logger

        Args:
            log_dir: Directory to store log files (None = current directory)
        """
        self.log_dir = Path(log_dir or "logs")
        self.log_dir.mkdir(exist_ok=True)

        # Set up log files
        self.request_log_file = self.log_dir / "requests.jsonl"
        self.compliance_log_file = self.log_dir / "compliance.jsonl"
        self.error_log_file = self.log_dir / "errors.jsonl"
        self.system_log_file = self.log_dir / "system.jsonl"

        # Configure Python logging to also output to stdout
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("pokemon-vgc-api")

    def generate_request_id(self) -> str:
        """Generate a unique request ID"""
        return str(uuid.uuid4())

    def _write_log_entry(self, file_path: Path, entry: Dict[str, Any]):
        """Write a log entry to file and stdout"""
        json_entry = json.dumps(entry, ensure_ascii=False, separators=(',', ':'))

        # Write to file (append mode)
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(json_entry + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write to log file {file_path}: {e}")

        # Also log to stdout for development and container environments
        self.logger.info(json_entry)

    def log_request(self, request_id: str, request_data: Dict[str, Any]):
        """
        Log an incoming request

        Args:
            request_id: Unique request identifier
            request_data: Request details (endpoint, url, IP, etc.)
        """
        entry = RequestLogEntry(
            request_id=request_id,
            endpoint=request_data.get("endpoint", "unknown"),
            hashed_ip=request_data.get("hashed_ip", "unknown"),
            session_id=request_data.get("session_id", "anonymous"),
            url=request_data.get("url"),
            timestamp=int(time.time()),
            user_agent=request_data.get("user_agent")
        )

        self._write_log_entry(self.request_log_file, entry.dict())

    def log_compliance_decision(self, request_id: str, decision_data: Dict[str, Any]):
        """
        Log a compliance check decision

        Args:
            request_id: Associated request ID
            decision_data: Compliance decision details
        """
        entry = ComplianceLogEntry(
            request_id=request_id,
            step=decision_data.get("step", "unknown"),
            decision=decision_data.get("decision", "unknown"),
            reason=decision_data.get("reason", "no reason provided"),
            domain=decision_data.get("domain"),
            timestamp=int(time.time()),
            additional_data={k: v for k, v in decision_data.items()
                           if k not in ["step", "decision", "reason", "domain"]}
        )

        self._write_log_entry(self.compliance_log_file, entry.dict())

    def log_error(self, request_id: str, error_data: Dict[str, Any]):
        """
        Log an error occurrence

        Args:
            request_id: Associated request ID
            error_data: Error details
        """
        entry = ErrorLogEntry(
            request_id=request_id,
            step=error_data.get("step", "unknown"),
            error_type=error_data.get("error_type", "general_error"),
            error_message=error_data.get("error", "unknown error"),
            timestamp=int(time.time()),
            additional_data={k: v for k, v in error_data.items()
                           if k not in ["step", "error_type", "error"]}
        )

        self._write_log_entry(self.error_log_file, entry.dict())

    def log_analysis_success(self, request_id: str, success_data: Dict[str, Any]):
        """
        Log a successful analysis completion

        Args:
            request_id: Associated request ID
            success_data: Analysis success details
        """
        # Log as a special compliance decision for successful analyses
        self.log_compliance_decision(request_id, {
            "step": "analysis_complete",
            "decision": "success",
            "reason": "analysis completed successfully",
            **success_data
        })

    def log_system_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Log system events (startup, shutdown, configuration changes)

        Args:
            event_type: Type of system event
            event_data: Event details
        """
        entry = SystemLogEntry(
            event_type=event_type,
            event_data=event_data,
            timestamp=int(time.time())
        )

        self._write_log_entry(self.system_log_file, entry.dict())

    def log_rate_limit_violation(self, hashed_ip: str, endpoint: str, limit_type: str):
        """
        Log rate limit violations

        Args:
            hashed_ip: Hashed IP address
            endpoint: API endpoint
            limit_type: Type of rate limit (hourly, concurrent, etc.)
        """
        self.log_system_event("rate_limit_violation", {
            "hashed_ip": hashed_ip,
            "endpoint": endpoint,
            "limit_type": limit_type,
            "action": "request_blocked"
        })

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """
        Log security-related events

        Args:
            event_type: Type of security event
            details: Event details
        """
        self.log_system_event(f"security_{event_type}", {
            "severity": "high",
            **details
        })

    def get_log_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get a summary of log activity for the past N hours

        Args:
            hours: Number of hours to look back

        Returns:
            Dictionary with log statistics
        """
        cutoff_time = int(time.time()) - (hours * 3600)

        # This is a simplified version - in production you might want
        # to use a proper log analysis tool
        try:
            summary = {
                "time_range_hours": hours,
                "requests": 0,
                "blocked_requests": 0,
                "errors": 0,
                "unique_ips": set(),
                "top_domains": {},
                "blocked_reasons": {}
            }

            # Read and analyze recent logs
            # Note: In production, consider using a log aggregation service
            return summary

        except Exception as e:
            self.logger.error(f"Failed to generate log summary: {e}")
            return {"error": "Failed to generate summary"}

    def cleanup_old_logs(self, days: int = 30):
        """
        Clean up log files older than specified days

        Args:
            days: Age in days after which to delete logs
        """
        try:
            cutoff_time = time.time() - (days * 24 * 3600)

            for log_file in self.log_dir.glob("*.jsonl"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file}")

        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")

# Global logger instance for easy import
default_logger = StructuredLogger()

# Convenience functions for common logging operations
def log_request(request_id: str, data: Dict[str, Any]):
    """Convenience function for request logging"""
    default_logger.log_request(request_id, data)

def log_compliance(request_id: str, data: Dict[str, Any]):
    """Convenience function for compliance logging"""
    default_logger.log_compliance_decision(request_id, data)

def log_error(request_id: str, data: Dict[str, Any]):
    """Convenience function for error logging"""
    default_logger.log_error(request_id, data)

def log_system(event_type: str, data: Dict[str, Any]):
    """Convenience function for system logging"""
    default_logger.log_system_event(event_type, data)