"""
Authentication UI components for Pokémon VGC Summariser
Provides login, registration, and user management interfaces
"""

import streamlit as st
from utils.auth import auth_manager
from utils.analytics import analytics_manager

def show_login_form():
    """Display login form"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 16px; margin-bottom: 2rem;">
        <h2 style="color: white; text-align: center; margin: 0;">🔐 Login to Your Account</h2>
        <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 0.5rem 0 0 0;">Access your personalized Pokémon VGC experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            help="Your unique username"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="Your secure password"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_button = st.form_submit_button(
                "🚀 Login",
                use_container_width=True
            )
        
        if login_button:
            if not username or not password:
                st.error("⚠️ Please enter both username and password")
                return False
            
            # Add debugging info for test account
            if username.lower() == "testuser":
                st.info(f"🔍 Debug: Attempting login for testuser with password: {password[:3]}***")
            
            success, message, session_token = auth_manager.login_user(username, password)
            
            if success:
                st.session_state['session_token'] = session_token
                st.session_state['username'] = username
                
                # Track login event
                analytics_manager.track_user_session(username, 'login')
                
                st.success(f"✅ {message}")
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ {message}")
                # Add helpful info for test account
                if username.lower() == "testuser":
                    st.info("💡 Test account credentials: Username: 'testuser', Password: 'testpass123'")
                return False
    
    return False

def show_registration_form():
    """Display registration form"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); padding: 2rem; border-radius: 16px; margin-bottom: 2rem;">
        <h2 style="color: white; text-align: center; margin: 0;">📝 Create New Account</h2>
        <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 0.5rem 0 0 0;">Join the Pokémon VGC community today</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("registration_form"):
        username = st.text_input(
            "Username",
            placeholder="Choose a unique username (min 3 characters)",
            help="This will be your unique identifier"
        )
        
        email = st.text_input(
            "Email (Optional)",
            placeholder="your.email@example.com",
            help="Optional: For account recovery and updates"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a secure password (min 6 characters)",
            help="Use a strong password with letters, numbers, and symbols"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            help="Must match your password exactly"
        )
        
        # Terms and conditions
        agree_terms = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            help="You must agree to continue"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            register_button = st.form_submit_button(
                "🎉 Create Account",
                use_container_width=True
            )
        
        if register_button:
            if not all([username, password, confirm_password]):
                st.error("⚠️ Please fill in all required fields")
                return False
            
            if password != confirm_password:
                st.error("❌ Passwords do not match")
                return False
            
            if not agree_terms:
                st.error("⚠️ You must agree to the Terms of Service")
                return False
            
            success, message = auth_manager.register_user(username, password, email)
            
            if success:
                st.success(f"✅ {message}")
                st.info("🎯 You can now login with your new account!")
                
                # Track registration event
                analytics_manager.track_user_session(username, 'register')
                
                st.balloons()
                return True
            else:
                st.error(f"❌ {message}")
                return False
    
    return False

def show_user_profile():
    """Display user profile and settings"""
    current_user = auth_manager.get_current_user()
    if not current_user:
        return False
    
    user_info = auth_manager.get_user_info(current_user)
    if not user_info:
        return False
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); padding: 2rem; border-radius: 16px; margin-bottom: 2rem;">
        <h2 style="color: white; text-align: center; margin: 0;">👤 Welcome, {current_user}!</h2>
        <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 0.5rem 0 0 0;">Manage your account and view your activity</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User statistics
    user_activity = analytics_manager.get_user_activity_summary(current_user)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🔍 Total Searches",
            user_activity['total_searches'],
            help="Number of searches you've performed"
        )
    
    with col2:
        st.metric(
            "👁️ Teams Viewed",
            user_activity['total_team_views'],
            help="Number of teams you've viewed"
        )
    
    with col3:
        st.metric(
            "📄 Articles Summarized",
            user_activity['total_summaries'],
            help="Number of articles you've summarized"
        )
    
    with col4:
        login_count = user_info.get('login_count', 0)
        st.metric(
            "🚀 Total Logins",
            login_count,
            help="Number of times you've logged in"
        )
    
    # Favorite Pokémon
    if user_activity['favorite_pokemon']:
        st.markdown("### ⭐ Your Favorite Pokémon")
        fav_cols = st.columns(len(user_activity['favorite_pokemon']))
        for i, (pokemon, count) in enumerate(user_activity['favorite_pokemon']):
            with fav_cols[i]:
                st.metric(
                    pokemon.title(),
                    f"{count} searches",
                    help=f"You've searched for {pokemon} {count} times"
                )
    
    # Recent Activity
    if user_activity['recent_activity']:
        st.markdown("### 📈 Recent Activity")
        for activity in user_activity['recent_activity'][:5]:
            activity_time = activity['timestamp'][:19].replace('T', ' ')
            
            if activity['type'] == 'search':
                icon = "🔍"
            elif activity['type'] == 'team_view':
                icon = "👁️"
            else:
                icon = "📄"
            
            st.markdown(f"**{icon} {activity['details']}**")
            st.caption(f"📅 {activity_time}")
    
    # Account Settings
    st.markdown("### ⚙️ Account Settings")
    
    with st.expander("🎨 Preferences", expanded=False):
        preferences = user_info.get('preferences', {})
        
        theme = st.selectbox(
            "Theme",
            ["light", "dark"],
            index=0 if preferences.get('theme', 'light') == 'light' else 1
        )
        
        notifications = st.checkbox(
            "Enable Notifications",
            value=preferences.get('notifications', True)
        )
        
        if st.button("💾 Save Preferences"):
            new_preferences = {
                'theme': theme,
                'notifications': notifications
            }
            
            if auth_manager.update_user_preferences(current_user, new_preferences):
                st.success("✅ Preferences saved successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to save preferences")
    
    # Account Info
    with st.expander("📋 Account Information", expanded=False):
        st.write(f"**Username:** {current_user}")
        st.write(f"**Email:** {user_info.get('email', 'Not provided')}")
        st.write(f"**Member Since:** {user_info.get('created_at', 'Unknown')[:10]}")
        st.write(f"**Last Login:** {user_info.get('last_login', 'Unknown')[:19].replace('T', ' ')}")
    
    # Logout button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            if 'session_token' in st.session_state:
                auth_manager.logout_user(st.session_state['session_token'])
                
                # Track logout event
                analytics_manager.track_user_session(current_user, 'logout')
                
                del st.session_state['session_token']
                if 'username' in st.session_state:
                    del st.session_state['username']
            
            st.success("👋 Logged out successfully!")
            st.rerun()
    
    return True

def show_auth_sidebar():
    """Show authentication status in sidebar"""
    current_user = auth_manager.get_current_user()
    
    if current_user:
        st.markdown(f"""
        <div style="background: #f0fff4; padding: 1rem; border-radius: 8px; border-left: 4px solid #48bb78; margin-bottom: 1rem;">
            <div style="color: #2f855a; font-weight: 600;">👤 Logged in as:</div>
            <div style="color: #38a169; font-size: 1.1rem; font-weight: 700;">{current_user}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("👤 View Profile", use_container_width=True):
            st.session_state['show_profile'] = True
            st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True):
            if 'session_token' in st.session_state:
                auth_manager.logout_user(st.session_state['session_token'])
                analytics_manager.track_user_session(current_user, 'logout')
                del st.session_state['session_token']
                if 'username' in st.session_state:
                    del st.session_state['username']
            st.rerun()
    else:
        st.markdown("""
        <div style="background: #fef5e7; padding: 1rem; border-radius: 8px; border-left: 4px solid #ed8936; margin-bottom: 1rem;">
            <div style="color: #c05621; font-weight: 600;">🔐 Not logged in</div>
            <div style="color: #9c4221; font-size: 0.9rem;">Login for personalized features</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔐 Login", use_container_width=True):
            st.session_state['show_login'] = True
            st.rerun()

def require_authentication():
    """Decorator-like function to require authentication"""
    current_user = auth_manager.get_current_user()
    
    if not current_user:
        st.warning("🔐 Please login to access this feature")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔐 Login", use_container_width=True):
                st.session_state['show_login'] = True
                st.rerun()
        
        with col2:
            if st.button("📝 Register", use_container_width=True):
                st.session_state['show_register'] = True
                st.rerun()
        
        return False
    
    return current_user
