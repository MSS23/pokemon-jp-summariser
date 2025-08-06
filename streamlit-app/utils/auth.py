"""
Secure authentication system for Pokémon VGC Summariser
Handles user registration, login, and session management
"""

import streamlit as st
import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import hmac

# Configuration
AUTH_DATA_PATH = "storage/users.json"
SESSIONS_PATH = "storage/sessions.json"
SECRET_KEY_PATH = "storage/secret_key.txt"
SESSION_TIMEOUT_HOURS = 24

class AuthManager:
    def __init__(self):
        self.ensure_storage_directory()
        self.secret_key = self.get_or_create_secret_key()
    
    def ensure_storage_directory(self):
        """Ensure storage directory exists"""
        os.makedirs(os.path.dirname(AUTH_DATA_PATH), exist_ok=True)
    
    def get_or_create_secret_key(self) -> str:
        """Get or create a secret key for session management"""
        if os.path.exists(SECRET_KEY_PATH):
            with open(SECRET_KEY_PATH, 'r') as f:
                return f.read().strip()
        else:
            secret_key = secrets.token_hex(32)
            with open(SECRET_KEY_PATH, 'w') as f:
                f.write(secret_key)
            return secret_key
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for secure password hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        computed_hash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, password_hash)
    
    def load_users(self) -> Dict:
        """Load user data from file"""
        try:
            if os.path.exists(AUTH_DATA_PATH):
                with open(AUTH_DATA_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_users(self, users: Dict) -> bool:
        """Save user data to file"""
        try:
            with open(AUTH_DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def load_sessions(self) -> Dict:
        """Load session data from file"""
        try:
            if os.path.exists(SESSIONS_PATH):
                with open(SESSIONS_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_sessions(self, sessions: Dict) -> bool:
        """Save session data to file"""
        try:
            with open(SESSIONS_PATH, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def create_session_token(self, username: str) -> str:
        """Create a secure session token"""
        timestamp = datetime.now().isoformat()
        data = f"{username}:{timestamp}:{secrets.token_hex(16)}"
        signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{data}:{signature}"
    
    def verify_session_token(self, token: str) -> Optional[str]:
        """Verify session token and return username if valid"""
        try:
            parts = token.split(':')
            if len(parts) != 4:
                return None
            
            username, timestamp, random_part, signature = parts
            data = f"{username}:{timestamp}:{random_part}"
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # Check if session is expired
            session_time = datetime.fromisoformat(timestamp)
            if datetime.now() - session_time > timedelta(hours=SESSION_TIMEOUT_HOURS):
                return None
            
            return username
        except Exception:
            return None
    
    def register_user(self, username: str, password: str, email: str = "") -> Tuple[bool, str]:
        """Register a new user"""
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        users = self.load_users()
        
        if username.lower() in [u.lower() for u in users.keys()]:
            return False, "Username already exists"
        
        # Hash password
        password_hash, salt = self.hash_password(password)
        
        # Create user record
        users[username] = {
            'password_hash': password_hash,
            'salt': salt,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'login_count': 0,
            'preferences': {
                'theme': 'light',
                'notifications': True
            }
        }
        
        if self.save_users(users):
            return True, "User registered successfully"
        else:
            return False, "Failed to save user data"
    
    def login_user(self, username: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """Login user and return session token"""
        users = self.load_users()
        
        # Find user (case-insensitive)
        actual_username = None
        for user in users.keys():
            if user.lower() == username.lower():
                actual_username = user
                break
        
        if not actual_username:
            return False, "Invalid username or password", None
        
        user_data = users[actual_username]
        
        if not self.verify_password(password, user_data['password_hash'], user_data['salt']):
            return False, "Invalid username or password", None
        
        # Update login info
        user_data['last_login'] = datetime.now().isoformat()
        user_data['login_count'] = user_data.get('login_count', 0) + 1
        users[actual_username] = user_data
        self.save_users(users)
        
        # Create session
        session_token = self.create_session_token(actual_username)
        sessions = self.load_sessions()
        sessions[session_token] = {
            'username': actual_username,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        self.save_sessions(sessions)
        
        return True, "Login successful", session_token
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user by removing session"""
        sessions = self.load_sessions()
        if session_token in sessions:
            del sessions[session_token]
            return self.save_sessions(sessions)
        return True
    
    def get_current_user(self) -> Optional[str]:
        """Get current logged-in user from session state"""
        if 'session_token' not in st.session_state:
            return None
        
        username = self.verify_session_token(st.session_state['session_token'])
        if username:
            # Update last activity
            sessions = self.load_sessions()
            if st.session_state['session_token'] in sessions:
                sessions[st.session_state['session_token']]['last_activity'] = datetime.now().isoformat()
                self.save_sessions(sessions)
            return username
        else:
            # Invalid session, clear it
            if 'session_token' in st.session_state:
                del st.session_state['session_token']
            return None
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        users = self.load_users()
        return users.get(username)
    
    def update_user_preferences(self, username: str, preferences: Dict) -> bool:
        """Update user preferences"""
        users = self.load_users()
        if username in users:
            users[username]['preferences'].update(preferences)
            return self.save_users(users)
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        sessions = self.load_sessions()
        current_time = datetime.now()
        expired_sessions = []
        
        for token, session_data in sessions.items():
            try:
                last_activity = datetime.fromisoformat(session_data['last_activity'])
                if current_time - last_activity > timedelta(hours=SESSION_TIMEOUT_HOURS):
                    expired_sessions.append(token)
            except Exception:
                expired_sessions.append(token)
        
        for token in expired_sessions:
            del sessions[token]
        
        if expired_sessions:
            self.save_sessions(sessions)
    
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        users = self.load_users()
        sessions = self.load_sessions()
        
        total_users = len(users)
        active_sessions = len(sessions)
        
        # Calculate login stats
        login_counts = [user.get('login_count', 0) for user in users.values()]
        avg_logins = sum(login_counts) / len(login_counts) if login_counts else 0
        
        return {
            'total_users': total_users,
            'active_sessions': active_sessions,
            'average_logins': round(avg_logins, 1)
        }
    
    def create_test_account(self) -> Tuple[bool, str]:
        """Create a test account for development/testing"""
        test_username = "testuser"
        test_password = "testpass123"
        test_email = "test@pokemon-vgc.com"
        
        users = self.load_users()
        
        # Check if test account already exists
        if test_username in users:
            return True, f"Test account '{test_username}' already exists"
        
        # Create test account
        password_hash, salt = self.hash_password(test_password)
        
        users[test_username] = {
            'password_hash': password_hash,
            'salt': salt,
            'email': test_email,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'login_count': 0,
            'preferences': {
                'theme': 'light',
                'notifications': True
            }
        }
        
        if self.save_users(users):
            return True, f"Test account created successfully! Username: {test_username}, Password: {test_password}"
        else:
            return False, "Failed to create test account"

# Global auth manager instance
auth_manager = AuthManager()
