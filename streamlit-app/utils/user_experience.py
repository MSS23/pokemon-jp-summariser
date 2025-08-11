# -*- coding: utf-8 -*-
"""
User experience improvements, security features, and rate limiting
Addresses concerns: user experience, security, access control, rate limiting
"""

import hashlib
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import streamlit as st
import threading
from contextlib import contextmanager

class UserSessionManager:
    """Manage user sessions and authentication"""
    
    def __init__(self):
        self.sessions = {}
        self._lock = threading.Lock()
        self.session_timeout = 3600  # 1 hour
        self.max_sessions_per_ip = 5
    
    def create_session(self, user_info: Dict[str, Any]) -> str:
        """Create a new user session"""
        session_id = self._generate_session_id(user_info)
        timestamp = datetime.now()
        
        with self._lock:
            # Clean up old sessions
            self._cleanup_expired_sessions()
            
            # Check IP-based rate limiting
            ip_address = user_info.get('ip_address', 'unknown')
            if self._is_ip_rate_limited(ip_address):
                raise Exception("Too many sessions from this IP address")
            
            # Create session
            self.sessions[session_id] = {
                'user_info': user_info,
                'created_at': timestamp,
                'last_activity': timestamp,
                'ip_address': ip_address,
                'corrections_made': 0,
                'rate_limit_reset': timestamp + timedelta(hours=1)
            }
        
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """Validate if a session is still active"""
        with self._lock:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            if self._is_session_expired(session):
                del self.sessions[session_id]
                return False
            
            # Update last activity
            session['last_activity'] = datetime.now()
            return True
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session"""
        with self._lock:
            if session_id in self.sessions:
                return self.sessions[session_id]
            return None
    
    def _generate_session_id(self, user_info: Dict[str, Any]) -> str:
        """Generate a unique session ID"""
        unique_string = f"{user_info.get('username', 'anonymous')}_{time.time()}_{os.getpid()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def _is_session_expired(self, session: Dict[str, Any]) -> bool:
        """Check if a session has expired"""
        return datetime.now() - session['last_activity'] > timedelta(seconds=self.session_timeout)
    
    def _is_ip_rate_limited(self, ip_address: str) -> bool:
        """Check if an IP address is rate limited"""
        active_sessions = [
            s for s in self.sessions.values()
            if s['ip_address'] == ip_address and not self._is_session_expired(s)
        ]
        return len(active_sessions) >= self.max_sessions_per_ip
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if self._is_session_expired(session)
        ]
        for session_id in expired_sessions:
            del self.sessions[session_id]

# Global session manager
session_manager = UserSessionManager()

class RateLimiter:
    """Rate limiting for various operations"""
    
    def __init__(self):
        self.rate_limits = {
            'corrections': {'max': 50, 'window': 3600},  # 50 corrections per hour
            'api_calls': {'max': 100, 'window': 3600},   # 100 API calls per hour
            'file_uploads': {'max': 10, 'window': 3600}, # 10 uploads per hour
            'cache_writes': {'max': 200, 'window': 3600} # 200 cache writes per hour
        }
        self.usage_records = {}
        self._lock = threading.Lock()
    
    def check_rate_limit(self, operation: str, user_id: str) -> Tuple[bool, str]:
        """Check if a user has exceeded rate limits for an operation"""
        if operation not in self.rate_limits:
            return True, "No rate limit configured"
        
        with self._lock:
            current_time = time.time()
            limit_config = self.rate_limits[operation]
            
            # Initialize user record if not exists
            if user_id not in self.usage_records:
                self.usage_records[user_id] = {}
            
            if operation not in self.usage_records[user_id]:
                self.usage_records[user_id][operation] = []
            
            # Clean up old records
            cutoff_time = current_time - limit_config['window']
            self.usage_records[user_id][operation] = [
                timestamp for timestamp in self.usage_records[user_id][operation]
                if timestamp > cutoff_time
            ]
            
            # Check if limit exceeded
            if len(self.usage_records[user_id][operation]) >= limit_config['max']:
                return False, f"Rate limit exceeded for {operation}"
            
            # Record usage
            self.usage_records[user_id][operation].append(current_time)
            return True, "Rate limit check passed"
    
    def get_remaining_quota(self, operation: str, user_id: str) -> Tuple[int, int]:
        """Get remaining quota for an operation"""
        if operation not in self.rate_limits:
            return 0, 0
        
        with self._lock:
            if user_id not in self.usage_records or operation not in self.usage_records[user_id]:
                return self.rate_limits[operation]['max'], self.rate_limits[operation]['max']
            
            current_time = time.time()
            limit_config = self.rate_limits[operation]
            cutoff_time = current_time - limit_config['window']
            
            # Count recent usage
            recent_usage = len([
                timestamp for timestamp in self.usage_records[user_id][operation]
                if timestamp > cutoff_time
            ])
            
            remaining = max(0, limit_config['max'] - recent_usage)
            return remaining, limit_config['max']

# Global rate limiter
rate_limiter = RateLimiter()

class SecurityManager:
    """Manage security features and access control"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.suspicious_activities = []
        self.security_log = []
        self._lock = threading.Lock()
    
    def check_security(self, request_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if a request passes security checks"""
        ip_address = request_info.get('ip_address', 'unknown')
        user_agent = request_info.get('user_agent', '')
        session_id = request_info.get('session_id', '')
        
        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            return False, "IP address is blocked"
        
        # Check for suspicious user agents
        if self._is_suspicious_user_agent(user_agent):
            self._log_suspicious_activity('suspicious_user_agent', request_info)
            return False, "Suspicious user agent detected"
        
        # Check for rapid requests (basic DDoS protection)
        if self._is_rapid_request(ip_address):
            self._log_suspicious_activity('rapid_requests', request_info)
            return False, "Too many requests from this IP"
        
        # Check session validity
        if session_id and not session_manager.validate_session(session_id):
            self._log_suspicious_activity('invalid_session', request_info)
            return False, "Invalid or expired session"
        
        return True, "Security check passed"
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious"""
        suspicious_patterns = [
            'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget',
            'python-requests', 'go-http-client', 'java-http-client'
        ]
        
        user_agent_lower = user_agent.lower()
        return any(pattern in user_agent_lower for pattern in suspicious_patterns)
    
    def _is_rapid_request(self, ip_address: str) -> bool:
        """Check if IP is making rapid requests"""
        current_time = time.time()
        
        with self._lock:
            # Clean up old records
            cutoff_time = current_time - 60  # 1 minute window
            self.suspicious_activities = [
                activity for activity in self.suspicious_activities
                if activity['timestamp'] > cutoff_time
            ]
            
            # Count recent requests from this IP
            recent_requests = len([
                activity for activity in self.suspicious_activities
                if activity['ip_address'] == ip_address
            ])
            
            # Block if more than 30 requests per minute
            if recent_requests > 30:
                return True
            
            return False
    
    def _log_suspicious_activity(self, activity_type: str, request_info: Dict[str, Any]):
        """Log suspicious activity"""
        with self._lock:
            activity_record = {
                'timestamp': time.time(),
                'activity_type': activity_type,
                'ip_address': request_info.get('ip_address', 'unknown'),
                'user_agent': request_info.get('user_agent', ''),
                'session_id': request_info.get('session_id', ''),
                'details': request_info
            }
            
            self.suspicious_activities.append(activity_record)
            self.security_log.append(activity_record)
            
            # Keep only last 1000 security log entries
            if len(self.security_log) > 1000:
                self.security_log = self.security_log[-1000:]

# Global security manager
security_manager = SecurityManager()

class UserExperienceEnhancer:
    """Enhance user experience with various features"""
    
    def __init__(self):
        self.user_preferences = {}
        self.feature_flags = {}
        self._lock = threading.Lock()
    
    def get_user_preference(self, user_id: str, preference_key: str, default_value: Any = None) -> Any:
        """Get a user's preference setting"""
        with self._lock:
            if user_id in self.user_preferences and preference_key in self.user_preferences[user_id]:
                return self.user_preferences[user_id][preference_key]
            return default_value
    
    def set_user_preference(self, user_id: str, preference_key: str, value: Any):
        """Set a user's preference"""
        with self._lock:
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {}
            self.user_preferences[user_id][preference_key] = value
    
    def is_feature_enabled(self, feature_name: str, user_id: str = None) -> bool:
        """Check if a feature is enabled for a user"""
        with self._lock:
            # Global feature flags
            if feature_name in self.feature_flags:
                return self.feature_flags[feature_name]
            
            # User-specific feature flags
            if user_id and user_id in self.user_preferences:
                feature_key = f"feature_{feature_name}"
                if feature_key in self.user_preferences[user_id]:
                    return self.user_preferences[user_id][feature_key]
            
            # Default feature states
            default_features = {
                'advanced_corrections': True,
                'data_validation': True,
                'system_monitoring': True,
                'audit_trail': True,
                'rate_limiting': True
            }
            
            return default_features.get(feature_name, False)
    
    def enable_feature(self, feature_name: str, enabled: bool = True):
        """Enable or disable a feature globally"""
        with self._lock:
            self.feature_flags[feature_name] = enabled

# Global UX enhancer
ux_enhancer = UserExperienceEnhancer()

def get_user_session_id() -> str:
    """Get or create a user session ID"""
    if 'user_session_id' not in st.session_state:
        # Create a unique session ID
        user_info = {
            'username': st.session_state.get('username', 'anonymous'),
            'timestamp': time.time(),
            'ip_address': 'unknown'  # In a real app, you'd get this from the request
        }
        
        try:
            session_id = session_manager.create_session(user_info)
            st.session_state['user_session_id'] = session_id
        except Exception as e:
            # Fallback to simple hash if session creation fails
            fallback_id = hashlib.md5(f"{user_info['username']}_{user_info['timestamp']}".encode()).hexdigest()[:8]
            st.session_state['user_session_id'] = fallback_id
    
    return st.session_state['user_session_id']

def check_user_permissions(operation: str, user_id: str = None) -> Tuple[bool, str]:
    """Check if a user has permission to perform an operation"""
    if not user_id:
        user_id = get_user_session_id()
    
    # Check rate limiting
    rate_ok, rate_message = rate_limiter.check_rate_limit(operation, user_id)
    if not rate_ok:
        return False, rate_message
    
    # Check security
    request_info = {
        'ip_address': 'unknown',  # In a real app, get from request
        'user_agent': 'streamlit',  # In a real app, get from request
        'session_id': user_id
    }
    
    security_ok, security_message = security_manager.check_security(request_info)
    if not security_ok:
        return False, security_message
    
    # Check feature flags
    if not ux_enhancer.is_feature_enabled(operation, user_id):
        return False, f"Feature '{operation}' is not enabled for this user"
    
    return True, "Permission check passed"

def display_user_status():
    """Display current user status and limits"""
    try:
        user_id = get_user_session_id()
        
        st.markdown("""
        <div style="margin: 24px 0;">
            <h3 style="color: #1e293b; font-size: 1.4rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                👤 User Status & Limits
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Session information
        session_info = session_manager.get_session_info(user_id)
        if session_info:
            created_time = session_info['created_at'].strftime("%H:%M:%S")
            last_activity = session_info['last_activity'].strftime("%H:%M:%S")
            
            st.markdown(f"""
            <div style="
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
            ">
                <div style="color: #1e293b; font-size: 1.1rem; font-weight: 600; margin-bottom: 16px;">
                    Session Information
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                    <div style="text-align: center;">
                        <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 4px;">Session Created</div>
                        <div style="color: #1e293b; font-size: 1rem; font-weight: 600;">{created_time}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 4px;">Last Activity</div>
                        <div style="color: #1e293b; font-size: 1rem; font-weight: 600;">{last_activity}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 4px;">Corrections Made</div>
                        <div style="color: #1e293b; font-size: 1rem; font-weight: 600;">{session_info['corrections_made']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Rate limit information
        st.markdown("**Rate Limits:**")
        operations = ['corrections', 'api_calls', 'file_uploads', 'cache_writes']
        
        for operation in operations:
            remaining, total = rate_limiter.get_remaining_quota(operation, user_id)
            percentage = (remaining / total) * 100 if total > 0 else 0
            
            # Color based on remaining quota
            if percentage > 70:
                color = "#22c55e"  # Green
            elif percentage > 30:
                color = "#f59e0b"  # Orange
            else:
                color = "#ef4444"  # Red
            
            st.markdown(f"""
            <div style="
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 8px;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="color: #1e293b; font-weight: 600;">
                        {operation.title()}
                    </div>
                    <div style="color: {color}; font-weight: 600;">
                        {remaining} / {total}
                    </div>
                </div>
                <div style="
                    width: 100%;
                    height: 8px;
                    background: #e2e8f0;
                    border-radius: 4px;
                    margin-top: 8px;
                    overflow: hidden;
                ">
                    <div style="
                        width: {percentage}%;
                        height: 100%;
                        background: {color};
                        border-radius: 4px;
                        transition: width 0.3s ease;
                    "></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error displaying user status: {e}")

def cleanup_user_data():
    """Clean up old user data and sessions"""
    try:
        # Clean up old sessions
        session_manager._cleanup_expired_sessions()
        
        # Clean up old rate limit records
        current_time = time.time()
        with rate_limiter._lock:
            for user_id in list(rate_limiter.usage_records.keys()):
                for operation in list(rate_limiter.usage_records[user_id].keys()):
                    cutoff_time = current_time - rate_limiter.rate_limits[operation]['window']
                    rate_limiter.usage_records[user_id][operation] = [
                        timestamp for timestamp in rate_limiter.usage_records[user_id][operation]
                        if timestamp > cutoff_time
                    ]
                    
                    # Remove empty operation records
                    if not rate_limiter.usage_records[user_id][operation]:
                        del rate_limiter.usage_records[user_id][operation]
                
                # Remove empty user records
                if not rate_limiter.usage_records[user_id]:
                    del rate_limiter.usage_records[user_id]
        
        # Clean up old security logs
        with security_manager._lock:
            cutoff_time = current_time - (24 * 60 * 60)  # 24 hours
            security_manager.security_log = [
                entry for entry in security_manager.security_log
                if entry['timestamp'] > cutoff_time
            ]
    
    except Exception as e:
        st.error(f"Error during user data cleanup: {e}")

# Initialize default settings
ux_enhancer.enable_feature('advanced_corrections', True)
ux_enhancer.enable_feature('data_validation', True)
ux_enhancer.enable_feature('system_monitoring', True)
ux_enhancer.enable_feature('audit_trail', True)
ux_enhancer.enable_feature('rate_limiting', True)
