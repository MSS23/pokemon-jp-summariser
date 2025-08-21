"""
Progressive loading and UX improvements for Pokemon VGC Summariser
Provides enhanced loading indicators, animations, and user feedback
"""

import time
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st


class ProgressTracker:
    """Enhanced progress tracking with detailed steps and animations"""

    def __init__(self, total_steps: int = 100, show_eta: bool = True):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.show_eta = show_eta
        self.step_times = []

        # Initialize UI elements
        self.progress_container = st.container()
        with self.progress_container:
            self.progress_bar = st.progress(0)
            self.status_text = st.empty()
            self.detail_text = st.empty()
            if show_eta:
                self.eta_text = st.empty()

    def update(
        self,
        step: int,
        status: str,
        detail: str = "",
        substeps: Optional[List[str]] = None,
    ):
        """Update progress with enhanced feedback"""
        self.current_step = step
        progress_percent = min(step / self.total_steps, 1.0)

        # Update progress bar with smooth animation
        self.progress_bar.progress(progress_percent)

        # Update status with animated emoji
        animated_status = self._animate_status(status)
        self.status_text.markdown(f"### {animated_status}")

        # Update detail information
        if detail:
            self.detail_text.markdown(f"*{detail}*")

        # Show substeps if provided
        if substeps:
            substeps_html = ""
            for i, substep in enumerate(substeps):
                if i < len(substeps) - 1:
                    substeps_html += f"✅ {substep}<br>"
                else:
                    substeps_html += f"⏳ {substep}<br>"
            self.detail_text.markdown(substeps_html, unsafe_allow_html=True)

        # Calculate and show ETA
        if self.show_eta and step > 0:
            elapsed = time.time() - self.start_time
            avg_time_per_step = elapsed / step
            remaining_steps = max(0, self.total_steps - step)
            eta_seconds = remaining_steps * avg_time_per_step

            if eta_seconds > 0:
                eta_text = self._format_eta(eta_seconds)
                self.eta_text.markdown(f"📊 **ETA:** {eta_text}")

        # Record step time for analytics
        self.step_times.append(time.time())

    def _animate_status(self, status: str) -> str:
        """Add animated emoji to status based on keywords"""
        animations = {
            "fetching": ["🌐", "🔄", "📡", "🌍"],
            "analyzing": ["🤖", "🧠", "⚡", "🔍"],
            "extracting": ["📊", "🔍", "📈", "📋"],
            "saving": ["💾", "📁", "✨", "🗃️"],
            "loading": ["⚡", "🚀", "💫", "⭐"],
            "complete": ["✅", "🎉", "🌟", "🎯"],
            "processing": ["⚙️", "🔧", "🛠️", "⚡"],
        }

        # Get appropriate animation frames
        for keyword, frames in animations.items():
            if keyword.lower() in status.lower():
                frame_index = int(time.time() * 2) % len(frames)  # 2 FPS animation
                return f"{frames[frame_index]} {status}"

        return f"🔄 {status}"

    def _format_eta(self, seconds: float) -> str:
        """Format ETA in human-readable format"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def complete(
        self, final_status: str = "Complete!", duration: Optional[float] = None
    ):
        """Mark progress as complete with celebration animation"""
        self.progress_bar.progress(1.0)

        # Celebration animation
        celebration_frames = ["🎉", "✨", "🌟", "🎯", "🏆"]
        for frame in celebration_frames:
            self.status_text.markdown(f"### {frame} {final_status}")
            time.sleep(0.2)

        # Show final stats if duration provided
        if duration:
            self.detail_text.markdown(f"*Completed in {duration:.1f} seconds*")

        # Clear after delay
        time.sleep(1)
        self.cleanup()

    def cleanup(self):
        """Clean up progress UI elements"""
        self.progress_bar.empty()
        self.status_text.empty()
        self.detail_text.empty()
        if hasattr(self, "eta_text"):
            self.eta_text.empty()


class SmartCache:
    """Enhanced caching with preloading and smart prefetch"""

    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.prefetch_queue = []
        self.preload_history = []

    def get_with_preload(
        self, url: str, similar_urls: List[str] = None
    ) -> Tuple[Any, bool]:
        """Get cached data and trigger preloading of similar content"""
        # Get main content
        cached_data = self.cache_manager.get(url)
        is_cache_hit = cached_data is not None

        # Trigger preloading of similar content in background
        if similar_urls and not is_cache_hit:
            self._schedule_preload(similar_urls)

        return cached_data, is_cache_hit

    def _schedule_preload(self, urls: List[str]):
        """Schedule URLs for background preloading"""
        for url in urls:
            if url not in self.prefetch_queue and not self.cache_manager.get(url):
                self.prefetch_queue.append(url)

        # Limit queue size
        self.prefetch_queue = self.prefetch_queue[-5:]  # Keep last 5


def create_loading_animation(container, message: str = "Loading..."):
    """Create an elegant loading animation"""
    frames = ["🔄 " + message, "⚡ " + message, "✨ " + message, "💫 " + message]

    placeholder = container.empty()

    for _ in range(3):  # 3 cycles
        for frame in frames:
            placeholder.markdown(f"### {frame}")
            time.sleep(0.3)

    return placeholder


def show_success_animation(container, message: str = "Success!", duration: float = 2.0):
    """Show success animation with confetti effect"""
    frames = ["🎉", "✨", "🌟", "🎯", "🏆", "✅"]
    placeholder = container.empty()

    for frame in frames:
        placeholder.markdown(f"### {frame} {message}")
        time.sleep(duration / len(frames))

    return placeholder


def create_step_indicator(steps: List[str], current_step: int) -> str:
    """Create a visual step indicator with clean, responsive design"""
    import html

    step_components = []

    for i, step in enumerate(steps):
        safe_step = html.escape(step)

        if i < current_step:
            # Completed step
            step_components.append(
                f'<div style="display: flex; align-items: center; margin: 4px;">'
                f'<div style="width: 28px; height: 28px; border-radius: 50%; background: #22c55e; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; margin-right: 8px;">✓</div>'
                f'<span style="color: #22c55e; font-weight: 500; font-size: 14px;">{safe_step}</span>'
                f"</div>"
            )
        elif i == current_step:
            # Current step
            step_components.append(
                f'<div style="display: flex; align-items: center; margin: 4px;">'
                f'<div style="width: 28px; height: 28px; border-radius: 50%; background: #3b82f6; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; margin-right: 8px; animation: pulse 1.5s ease-in-out infinite;">{i+1}</div>'
                f'<span style="color: #3b82f6; font-weight: 600; font-size: 14px;">{safe_step}</span>'
                f"</div>"
            )
        else:
            # Future step
            step_components.append(
                f'<div style="display: flex; align-items: center; margin: 4px;">'
                f'<div style="width: 28px; height: 28px; border-radius: 50%; background: #e5e7eb; color: #9ca3af; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; margin-right: 8px;">{i+1}</div>'
                f'<span style="color: #9ca3af; font-size: 14px;">{safe_step}</span>'
                f"</div>"
            )

        # Add connector line (except for last step)
        if i < len(steps) - 1:
            color = "#22c55e" if i < current_step else "#e5e7eb"
            step_components.append(
                f'<div style="width: 20px; height: 2px; background: {color}; margin: 0 8px;"></div>'
            )

    step_html = f'<div style="display: flex; align-items: center; margin: 16px 0; flex-wrap: wrap; gap: 4px; justify-content: center; max-width: 100%;">{"".join(step_components)}</div>'

    return step_html


def create_enhanced_card(
    title: str, content: str, status: str = "info", icon: str = "📝"
) -> str:
    """Create enhanced card with animations and better styling"""
    import html

    status_colors = {
        "success": {"bg": "#f9fafb", "border": "#10b981", "text": "#10b981"},
        "error": {"bg": "#f9fafb", "border": "#ef4444", "text": "#ef4444"},
        "warning": {"bg": "#f9fafb", "border": "#f59e0b", "text": "#f59e0b"},
        "info": {"bg": "#f9fafb", "border": "#2563eb", "text": "#2563eb"},
    }

    colors = status_colors.get(status, status_colors["info"])

    # Escape the title to prevent HTML injection but allow content to contain HTML
    safe_title = html.escape(title)

    # Create HTML content with modern styling
    html_content = (
        f'<div style="background: {colors["bg"]}; border: 1px solid {colors["border"]}; '
        f'border-left: 4px solid {colors["border"]}; border-radius: 8px; padding: 1.5rem; '
        f'margin: 1rem 0; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);">'
        f'<h4 style="margin: 0 0 1rem 0; color: {colors["text"]}; font-size: 1.125rem; '
        f'font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">{icon} {safe_title}</h4>'
        f'<div style="color: #374151; line-height: 1.6;">{content}</div>'
        f"</div>"
    )

    return html_content


def add_enhanced_css():
    """Add enhanced CSS for better animations and UX"""
    st.markdown(
        """
    <style>
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.8; }
    }
    
    @keyframes countdown {
        0% { width: 100%; }
        100% { width: 0%; }
    }
    
    @keyframes shimmer {
        0% { background-position: -200px 0; }
        100% { background-position: calc(200px + 100%) 0; }
    }
    
    @keyframes slideIn {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .smooth-card {
        animation: slideIn 0.6s ease-out;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .fade-in {
        animation: fadeIn 0.8s ease-out;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
        animation: shimmer 2s linear infinite;
    }
    
    /* Enhanced button hover effects */
    .stButton > button {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    /* Smooth text input focus */
    .stTextInput input:focus {
        transform: scale(1.02);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
    }
    
    /* Loading spinner animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(59, 130, 246, 0.3);
        border-radius: 50%;
        border-top-color: #3b82f6;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def show_feature_tour():
    """Show an interactive feature tour for new users"""
    if "feature_tour_shown" not in st.session_state:
        st.session_state.feature_tour_shown = False

    if not st.session_state.feature_tour_shown:
        with st.sidebar:
            st.info(
                """
            🎯 **Quick Tour**
            
            Welcome to the Pokemon VGC Summariser! Here's what you can do:
            
            1. **🔗 Paste URL** - Enter any Pokemon VGC article URL
            2. **⚡ Instant Analysis** - AI analyzes and summarizes content
            3. **📊 Pokemon Cards** - View detailed team information
            4. **💾 Smart Caching** - Results are cached for faster access
            5. **📈 Analytics** - Track your usage and cache performance
            
            Ready to get started? Just paste a URL above!
            """
            )

            if st.button("Got it! 👍", key="dismiss_tour"):
                st.session_state.feature_tour_shown = True
                st.rerun()


def create_status_badge(status: str, count: int = None) -> str:
    """Create animated status badges"""
    import html

    badge_configs = {
        "cached": {"color": "#22c55e", "bg": "#dcfce7", "icon": "⚡"},
        "processing": {"color": "#3b82f6", "bg": "#dbeafe", "icon": "🔄"},
        "error": {"color": "#ef4444", "bg": "#fef2f2", "icon": "❌"},
        "complete": {"color": "#8b5cf6", "bg": "#f3e8ff", "icon": "✅"},
        "warning": {"color": "#eab308", "bg": "#fefce8", "icon": "⚠️"},
    }

    config = badge_configs.get(status, badge_configs["processing"])
    count_text = f" ({count})" if count is not None else ""
    safe_status = html.escape(status.title())

    # Create badge HTML without problematic newlines
    badge_html = (
        f'<span style="background: {config["bg"]}; color: {config["color"]}; '
        f"padding: 4px 12px; border-radius: 20px; font-size: 0.9rem; "
        f"font-weight: 600; display: inline-flex; align-items: center; gap: 4px; "
        f'border: 1px solid {config["color"]};">'
        f'{config["icon"]} {safe_status}{count_text}'
        f"</span>"
    )

    return badge_html
