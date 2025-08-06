"""
Analytics Dashboard for Pokémon VGC Summariser
Shows trending teams, popular Pokémon, and user statistics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.analytics import analytics_manager
from utils.auth import auth_manager
from components.auth_ui import require_authentication, show_auth_sidebar
from components.global_styles import inject_global_styles
from components.navigation import show_navigation

# Page configuration
st.set_page_config(
    page_title="Analytics Dashboard - VGC Summariser",
    page_icon="📊",
    layout="wide"
)

# Inject global styles and navigation
inject_global_styles()

# Defensive authentication and user info handling
current_user = require_authentication()
if not current_user:
    st.stop()
user_info = auth_manager.get_user_info(current_user) if current_user else None
show_navigation(current_page="Analytics Dashboard", authenticated=bool(current_user), user_info=user_info)

# Unified sidebar
show_auth_sidebar(user_info=user_info)
if not current_user:
    st.stop()

# Time period selector
st.markdown("### 📅 Select Time Period")
time_period = st.selectbox(
    "Choose time period for analytics",
    ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
    index=1
)

# Convert time period to days
time_mapping = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "All time": 365 * 10  # 10 years as "all time"
}
days = time_mapping[time_period]

# Get analytics data
trending_pokemon = analytics_manager.get_trending_pokemon(days=days, limit=15)
trending_teams = analytics_manager.get_trending_teams(days=days, limit=10)
search_stats = analytics_manager.get_search_statistics()
daily_activity = analytics_manager.get_daily_activity(days=min(days, 30))

# --- Main Content ---
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📊 Analytics Dashboard</h1>
    <p class="header-subtitle">Real-time insights into Pokémon VGC trends and your activity</p>
</div>
""", unsafe_allow_html=True)

# --- Overview Metrics ---
st.markdown("""
<div class="vgc-card" style="margin-bottom:2rem;">
    <div class="card-section-title">📈 Overview Metrics</div>
    <div style="margin-top:1rem;">
""", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{search_stats['total_searches']}</div>
            <div class='metric-label'>Total Searches</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{search_stats['unique_terms']}</div>
            <div class='metric-label'>Unique Terms</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{search_stats['avg_results']}</div>
            <div class='metric-label'>Avg Results</div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    user_stats = auth_manager.get_user_stats()
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{user_stats['total_users']}</div>
            <div class='metric-label'>Total Users</div>
        </div>
    """, unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

# --- Daily Activity Trends ---
if daily_activity:
    st.markdown("""
    <div class="vgc-card" style="margin-bottom:2rem;">
        <div class="card-section-title">📊 Daily Activity Trends</div>
    """, unsafe_allow_html=True)
    # Prepare data for chart
    dates = list(daily_activity.keys())
    searches = [daily_activity[date]['searches'] for date in dates]
    team_views = [daily_activity[date]['team_views'] for date in dates]
    summaries = [daily_activity[date]['summaries'] for date in dates]
    df_activity = pd.DataFrame({
        'Date': dates,
        'Searches': searches,
        'Team Views': team_views,
        'Summaries': summaries
    })
    df_activity['Date'] = pd.to_datetime(df_activity['Date'])
    df_activity = df_activity.sort_values('Date')
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_activity['Date'],
        y=df_activity['Searches'],
        mode='lines+markers',
        name='Searches',
        line=dict(color='#667eea', width=3),
        marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=df_activity['Date'],
        y=df_activity['Team Views'],
        mode='lines+markers',
        name='Team Views',
        line=dict(color='#48bb78', width=3),
        marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=df_activity['Date'],
        y=df_activity['Summaries'],
        mode='lines+markers',
        name='Summaries',
        line=dict(color='#ed8936', width=3),
        marker=dict(size=6)
    ))
    fig.update_layout(
        title="Daily Activity Over Time",
        xaxis_title="Date",
        yaxis_title="Count",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Trending Pokémon & Teams ---
st.markdown("""
<div class="vgc-card" style="margin-bottom:2rem;">
    <div class="card-section-title">🔥 Trending Pokémon & ⭐ Trending Teams</div>
    <div style="margin-top:1.5rem;">
""", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
        <div class="trend-card">
            <div class="trend-title">🔥 Trending Pokémon</div>
    """, unsafe_allow_html=True)
    if trending_pokemon:
        pokemon_names = [p[0].title() for p in trending_pokemon]
        pokemon_counts = [p[1] for p in trending_pokemon]
        fig_pokemon = px.bar(
            x=pokemon_counts,
            y=pokemon_names,
            orientation='h',
            title=f"Most Searched Pokémon ({time_period})",
            labels={'x': 'Search Count', 'y': 'Pokémon'},
            color=pokemon_counts,
            color_continuous_scale='Viridis'
        )
        fig_pokemon.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif"),
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_pokemon, use_container_width=True)
        st.markdown("**Top 5 Most Searched:**")
        for i, (pokemon, count) in enumerate(trending_pokemon[:5]):
            st.markdown(f"<span class='pokemon-badge'>#{i+1} {pokemon.title()} ({count} searches)</span>", unsafe_allow_html=True)
    else:
        st.info("No trending Pokémon data available for the selected time period.")
    st.markdown("</div>", unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class="trend-card">
            <div class="trend-title">⭐ Trending Teams</div>
    """, unsafe_allow_html=True)
    if trending_teams:
        for i, team in enumerate(trending_teams[:5]):
            st.markdown(f"""
                <div class='team-card'>
                    <div style='font-weight:600; color:#1a202c; margin-bottom:0.5rem;'>
                        #{i+1} Team ({team['views']} views)
                    </div>
                    <div style='color:#4a5568; font-size:0.9rem; margin-bottom:0.5rem;'>
                        {team['article_title'][:60]}{'...' if len(team['article_title']) > 60 else ''}
                    </div>
                    <div style='display:flex; flex-wrap:wrap; gap:0.25rem;'>
            """, unsafe_allow_html=True)
            for pokemon in team['pokemon'][:6]:
                st.markdown(f"<span style='background:#e2e8f0; color:#2d3748; padding:0.25rem 0.5rem; border-radius:12px; font-size:0.8rem; font-weight:500;'>{pokemon}</span>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
        if len(trending_teams) > 1:
            team_labels = [f"Team {i+1}" for i in range(len(trending_teams[:8]))]
            team_views = [team['views'] for team in trending_teams[:8]]
            fig_teams = px.pie(
                values=team_views,
                names=team_labels,
                title="Team View Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_teams.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif"),
                height=300
            )
            st.plotly_chart(fig_teams, use_container_width=True)
    else:
        st.info("No trending teams data available for the selected time period.")
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

# --- Most Common Search Terms ---
if search_stats['most_common_terms']:
    st.markdown("""
    <div class="vgc-card" style="margin-bottom:2rem;">
        <div class="card-section-title">🔍 Most Common Search Terms</div>
    """, unsafe_allow_html=True)
    terms_df = pd.DataFrame(search_stats['most_common_terms'], columns=['Term', 'Count'])
    fig_terms = px.bar(
        terms_df,
        x='Count',
        y='Term',
        orientation='h',
        title="Most Frequently Searched Terms",
        color='Count',
        color_continuous_scale='Blues'
    )
    fig_terms.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_terms, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- User Personal Statistics ---
st.markdown("""
<div class="vgc-card" style="margin-bottom:2rem;">
    <div class="card-section-title">👤 Your Personal Statistics</div>
    <div style="margin-top:1rem;">
""", unsafe_allow_html=True)
user_activity = analytics_manager.get_user_activity_summary(current_user)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "🔍 Your Searches",
        user_activity['total_searches'],
        help="Total searches you've performed"
    )
with col2:
    st.metric(
        "👁️ Teams Viewed",
        user_activity['total_team_views'],
        help="Teams you've viewed in detail"
    )
with col3:
    st.metric(
        "📄 Articles Summarized",
        user_activity['total_summaries'],
        help="Articles you've summarized"
    )
st.markdown("</div>", unsafe_allow_html=True)

if user_activity['favorite_pokemon']:
    st.markdown("""
    <div class="vgc-card" style="margin-top:1rem;">
        <div class="card-section-title">⭐ Your Favorite Pokémon</div>
    """, unsafe_allow_html=True)
    user_pokemon = [p[0].title() for p in user_activity['favorite_pokemon']]
    user_counts = [p[1] for p in user_activity['favorite_pokemon']]
    fig_user_pokemon = px.bar(
        x=user_pokemon,
        y=user_counts,
        title="Your Most Searched Pokémon",
        labels={'x': 'Pokémon', 'y': 'Search Count'},
        color=user_counts,
        color_continuous_scale='Plasma'
    )
    fig_user_pokemon.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        height=300,
        showlegend=False
    )
    st.plotly_chart(fig_user_pokemon, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

from components.global_styles import show_global_footer
show_global_footer()
