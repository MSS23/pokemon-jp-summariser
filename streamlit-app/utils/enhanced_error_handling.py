# -*- coding: utf-8 -*-
"""
Enhanced error handling, logging, and system health monitoring
Addresses concerns: error recovery, system stability, monitoring, debugging
"""

import logging
import traceback
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import streamlit as st
import threading
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('streamlit-app/storage/system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SystemHealthMonitor:
    """Monitor system health and performance"""
    
    def __init__(self):
        self.start_time = time.time()
        self.error_count = 0
        self.success_count = 0
        self.performance_metrics = {}
        self._lock = threading.Lock()
    
    def record_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Record an error occurrence"""
        with self._lock:
            self.error_count += 1
            timestamp = datetime.now().isoformat()
            
            error_record = {
                'timestamp': timestamp,
                'error_type': error_type,
                'error_message': error_message,
                'context': context or {},
                'error_count': self.error_count
            }
            
            # Log to file
            logger.error(f"Error recorded: {error_type} - {error_message}")
            
            # Store in session state for display
            if 'system_errors' not in st.session_state:
                st.session_state['system_errors'] = []
            st.session_state['system_errors'].append(error_record)
            
            # Keep only last 50 errors
            if len(st.session_state['system_errors']) > 50:
                st.session_state['system_errors'] = st.session_state['system_errors'][-50:]
    
    def record_success(self, operation: str, duration: float = None):
        """Record a successful operation"""
        with self._lock:
            self.success_count += 1
            if duration:
                if operation not in self.performance_metrics:
                    self.performance_metrics[operation] = []
                self.performance_metrics[operation].append(duration)
                
                # Keep only last 100 measurements
                if len(self.performance_metrics[operation]) > 100:
                    self.performance_metrics[operation] = self.performance_metrics[operation][-100:]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status"""
        with self._lock:
            uptime = time.time() - self.start_time
            error_rate = self.error_count / max(self.success_count + self.error_count, 1)
            
            # Calculate performance averages
            avg_performance = {}
            for operation, measurements in self.performance_metrics.items():
                if measurements:
                    avg_performance[operation] = sum(measurements) / len(measurements)
            
            return {
                'uptime_seconds': uptime,
                'uptime_formatted': self._format_uptime(uptime),
                'total_operations': self.success_count + self.error_count,
                'success_count': self.success_count,
                'error_count': self.error_count,
                'error_rate': error_rate,
                'error_rate_percentage': error_rate * 100,
                'performance_metrics': avg_performance,
                'status': 'healthy' if error_rate < 0.1 else 'degraded' if error_rate < 0.3 else 'critical'
            }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

# Global system health monitor
system_monitor = SystemHealthMonitor()

class ErrorRecoveryManager:
    """Manage error recovery and fallback strategies"""
    
    def __init__(self):
        self.recovery_strategies = {}
        self.fallback_handlers = {}
        self._lock = threading.Lock()
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Register a recovery strategy for a specific error type"""
        with self._lock:
            if error_type not in self.recovery_strategies:
                self.recovery_strategies[error_type] = []
            self.recovery_strategies[error_type].append(strategy)
    
    def register_fallback_handler(self, operation: str, handler: Callable):
        """Register a fallback handler for a specific operation"""
        with self._lock:
            self.fallback_handlers[operation] = handler
    
    def attempt_recovery(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Attempt to recover from an error using registered strategies"""
        error_type = type(error).__name__
        
        with self._lock:
            strategies = self.recovery_strategies.get(error_type, [])
        
        for strategy in strategies:
            try:
                if strategy(error, context):
                    logger.info(f"Recovery successful using strategy for {error_type}")
                    return True
            except Exception as recovery_error:
                logger.error(f"Recovery strategy failed: {recovery_error}")
        
        return False
    
    def execute_with_fallback(self, operation: str, main_func: Callable, *args, **kwargs) -> Any:
        """Execute a function with fallback handling"""
        try:
            result = main_func(*args, **kwargs)
            system_monitor.record_success(operation)
            return result
        except Exception as e:
            system_monitor.record_error(type(e).__name__, str(e), {'operation': operation})
            
            # Try fallback handler
            with self._lock:
                fallback_handler = self.fallback_handlers.get(operation)
            
            if fallback_handler:
                try:
                    logger.info(f"Executing fallback handler for {operation}")
                    return fallback_handler(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback handler also failed: {fallback_error}")
                    system_monitor.record_error(
                        f"fallback_{type(fallback_error).__name__}", 
                        str(fallback_error), 
                        {'operation': operation}
                    )
            
            # Re-raise if no recovery possible
            raise

# Global error recovery manager
error_manager = ErrorRecoveryManager()

@contextmanager
def error_boundary(operation: str, context: Dict[str, Any] = None):
    """Context manager for error boundary handling"""
    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        system_monitor.record_success(operation, duration)
    except Exception as e:
        duration = time.time() - start_time
        system_monitor.record_error(type(e).__name__, str(e), context or {})
        
        # Attempt recovery
        if error_manager.attempt_recovery(e, context):
            logger.info(f"Error recovered for {operation}")
        else:
            logger.error(f"Error not recoverable for {operation}: {e}")
            raise

def safe_execute(operation: str, func: Callable, *args, **kwargs) -> Any:
    """Safely execute a function with error handling and recovery"""
    return error_manager.execute_with_fallback(operation, func, *args, **kwargs)

def log_operation(operation: str, level: str = 'info'):
    """Decorator for logging operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                system_monitor.record_success(operation, duration)
                logger.info(f"Operation {operation} completed successfully in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                system_monitor.record_error(type(e).__name__, str(e), {'operation': operation})
                logger.error(f"Operation {operation} failed after {duration:.2f}s: {e}")
                raise
        return wrapper
    return decorator

def display_system_health():
    """Display system health information in Streamlit"""
    try:
        health_status = system_monitor.get_health_status()
        
        st.markdown("""
        <div style="margin: 24px 0;">
            <h3 style="color: #1e293b; font-size: 1.4rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                🏥 System Health Monitor
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Health status overview
        status_color = {
            'healthy': '#22c55e',
            'degraded': '#f59e0b',
            'critical': '#ef4444'
        }.get(health_status['status'], '#6b7280')
        
        st.markdown(f"""
        <div style="
            background: white;
            border: 2px solid {status_color};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div style="color: #1e293b; font-size: 1.2rem; font-weight: 700;">
                    System Status: {health_status['status'].title()}
                </div>
                <div style="
                    background: {status_color};
                    color: white;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.8rem;
                    font-weight: 600;
                ">
                    {health_status['status'].upper()}
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                <div style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 4px;">Uptime</div>
                    <div style="color: #1e293b; font-size: 1.1rem; font-weight: 600;">{health_status['uptime_formatted']}</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 4px;">Total Operations</div>
                    <div style="color: #1e293b; font-size: 1.1rem; font-weight: 600;">{health_status['total_operations']}</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 4px;">Success Rate</div>
                    <div style="color: #22c55e; font-size: 1.1rem; font-weight: 600;">{((1 - health_status['error_rate']) * 100):.1f}%</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 4px;">Error Rate</div>
                    <div style="color: #ef4444; font-size: 1.1rem; font-weight: 600;">{health_status['error_rate_percentage']:.1f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Performance metrics
        if health_status['performance_metrics']:
            st.markdown("**Performance Metrics:**")
            for operation, avg_duration in health_status['performance_metrics'].items():
                st.metric(operation, f"{avg_duration:.3f}s")
        
        # Recent errors
        if 'system_errors' in st.session_state and st.session_state['system_errors']:
            with st.expander("Recent Errors", expanded=False):
                for error in st.session_state['system_errors'][-5:]:  # Show last 5 errors
                    st.markdown(f"""
                    <div style="
                        background: #fef2f2;
                        border: 1px solid #fecaca;
                        border-radius: 6px;
                        padding: 12px;
                        margin-bottom: 8px;
                    ">
                        <div style="color: #dc2626; font-weight: 600; margin-bottom: 4px;">
                            {error['error_type']}
                        </div>
                        <div style="color: #7f1d1d; font-size: 0.9rem; margin-bottom: 4px;">
                            {error['error_message']}
                        </div>
                        <div style="color: #991b1b; font-size: 0.8rem;">
                            {error['timestamp']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error displaying system health: {e}")

def cleanup_old_logs():
    """Clean up old log files and error records"""
    try:
        # Clean up old system errors from session state
        if 'system_errors' in st.session_state:
            cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)  # 24 hours
            
            st.session_state['system_errors'] = [
                error for error in st.session_state['system_errors']
                if datetime.fromisoformat(error['timestamp']).timestamp() > cutoff_time
            ]
        
        # Clean up old log files if they get too large
        log_file = 'streamlit-app/storage/system.log'
        if os.path.exists(log_file) and os.path.getsize(log_file) > 10 * 1024 * 1024:  # 10MB
            # Create backup and truncate
            backup_file = f"{log_file}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            with open(log_file, 'r') as src, open(backup_file, 'w') as dst:
                # Keep only last 1000 lines
                lines = src.readlines()
                if len(lines) > 1000:
                    dst.writelines(lines[-1000:])
            
            # Truncate original file
            with open(log_file, 'w') as f:
                f.writelines(lines[-1000:])
            
            logger.info("Log file cleaned up and backed up")
    
    except Exception as e:
        logger.error(f"Error during log cleanup: {e}")

# Register some default recovery strategies
def register_default_recovery_strategies():
    """Register default error recovery strategies"""
    
    def file_io_recovery(error: Exception, context: Dict[str, Any]) -> bool:
        """Recovery strategy for file I/O errors"""
        if "Permission denied" in str(error) or "Access denied" in str(error):
            # Try to create directory if it doesn't exist
            if 'filepath' in context:
                try:
                    os.makedirs(os.path.dirname(context['filepath']), exist_ok=True)
                    return True
                except:
                    pass
        return False
    
    def json_parse_recovery(error: Exception, context: Dict[str, Any]) -> bool:
        """Recovery strategy for JSON parsing errors"""
        if "Expecting value" in str(error) or "Invalid control character" in str(error):
            # Try to fix common JSON issues
            if 'json_string' in context:
                try:
                    # Remove null bytes and invalid characters
                    cleaned = context['json_string'].replace('\x00', '').strip()
                    json.loads(cleaned)
                    return True
                except:
                    pass
        return False
    
    error_manager.register_recovery_strategy("PermissionError", file_io_recovery)
    error_manager.register_recovery_strategy("FileNotFoundError", file_io_recovery)
    error_manager.register_recovery_strategy("json.JSONDecodeError", json_parse_recovery)

# Initialize default strategies
register_default_recovery_strategies()
