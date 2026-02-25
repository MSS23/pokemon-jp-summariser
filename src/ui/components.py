"""
UI Components for Pokemon VGC Analysis application
"""

import html as _html
import streamlit as st
from typing import Dict, List, Any
import os
from datetime import datetime
from utils import (
    get_pokemon_sprite_url,
    format_moves_html,
    get_pokemon_type_class,
    get_role_class,
    create_pokepaste,
)


def esc(value: Any) -> str:
    """Escape a value for safe HTML interpolation."""
    return _html.escape(str(value)) if value is not None else ""

def render_section_header(icon: str, label: str):
    """Render a clean section header with icon and label"""
    st.markdown(
        f'''
        <div class="section-header">
            <span class="section-icon">{icon}</span>
            <span class="section-label">{label}</span>
            <div class="section-divider"></div>
        </div>
        ''',
        unsafe_allow_html=True
    )

def inject_stat_css():
    """Inject CSS styles for stat cards"""
    st.markdown("""
    <style>
      .stat-card{display:flex;align-items:center;gap:12px;padding:12px;border:1px solid #e5e7eb;
                 border-radius:16px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.05);margin-bottom:10px;}
      .stat-card.prominent{outline:2px solid #c7d2fe; outline-offset:0;}
      .stat-icon-wrapper{width:40px;height:40px;display:grid;place-items:center;border-radius:10px;background:#f8fafc;}
      .stat-label{font-size:12px;color:#64748b;margin-bottom:2px;line-height:1;}
      .stat-value{font-weight:600;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:220px;}
      .stat-content{min-width:0;}
      .stat-accent{margin-left:auto;width:8px;height:8px;border-radius:9999px;}
      .stat-accent.golden{background:#f59e0b;}
      @media (min-width: 640px){ .stat-value{max-width:360px;} }
    </style>
    """, unsafe_allow_html=True)

def render_stat_card(icon: str, label: str, value: str, accent: str = None, prominent: bool = False) -> str:
    """
    Generate HTML for a compact stat card
    
    Args:
        icon: Emoji icon for the card
        label: Display label (e.g., "Held Item", "Nature")
        value: Display value (e.g., "Focus Sash", "Timid")
        accent: Optional accent color class (e.g., "golden")
        prominent: Whether to apply prominent styling
    
    Returns:
        HTML string for the stat card
    """
    accent_html = f'<div class="stat-accent {accent}"></div>' if accent else ""
    prominent_cls = " prominent" if prominent else ""
    return f"""
    <article class="stat-card{prominent_cls}">
      <div class="stat-icon-wrapper"><span aria-hidden="true">{icon}</span></div>
      <div class="stat-content">
        <div class="stat-label">{esc(label)}</div>
        <div class="stat-value">{esc(value)}</div>
      </div>
      {accent_html}
    </article>
    """

def render_moves_grid(moves: List[str]):
    """Render moveset as dynamic, enhanced move cards"""
    moves_list = moves[:4] if moves else ["Not specified"] * 4
    
    moves_html = '<div class="moves-grid-enhanced">'
    for i, move in enumerate(moves_list, 1):
        is_empty = not move or move == 'Not specified'
        move_display = move if move and move != "Not specified" else "Not specified"
        
        # Add visual variety with different move card styles
        card_class = f"move-card-{(i-1) % 4 + 1}"
        
        moves_html += f'''
        <div class="move-card {card_class} {'empty' if is_empty else ''}">
            <div class="move-header">
                <div class="move-number-badge">{i}</div>
                <div class="move-type-indicator"></div>
            </div>
            <div class="move-content">
                <span class="move-name-dynamic" title="{esc(move_display)}">{esc(move_display)}</span>
            </div>
            <div class="move-accent"></div>
        </div>'''
    
    moves_html += '</div>'
    st.markdown(moves_html, unsafe_allow_html=True)

def render_ev_bars(evs):
    """Render dynamic, enhanced EV visualization"""
    if evs == "Not specified":
        st.markdown('<div class="ev-not-specified">EV spread not specified</div>', unsafe_allow_html=True)
        return
    
    # Display EV summary with enhanced styling
    st.markdown(f'<div class="ev-summary-enhanced"><span class="ev-label-text">EV Distribution:</span> <code class="ev-code-enhanced">{esc(evs)}</code></div>', unsafe_allow_html=True)
    
    # Parse and display enhanced bars
    if "/" in str(evs):
        try:
            ev_values = [int(x.strip()) for x in str(evs).split("/")]
            if len(ev_values) == 6:
                ev_labels = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
                ev_icons = ["❤️", "⚔️", "🛡️", "✨", "💫", "💨"]
                ev_colors = ["#ef4444", "#f59e0b", "#3b82f6", "#8b5cf6", "#06b6d4", "#10b981"]
                
                bars_html = '<div class="ev-bars-enhanced">'
                for i, (label, icon, value) in enumerate(zip(ev_labels, ev_icons, ev_values)):
                    if value > 0:
                        percentage = min((value / 252) * 100, 100)  # Cap at 100%
                        color = ev_colors[i]
                        
                        # Determine bar intensity for visual effect
                        intensity = "high" if value >= 200 else "medium" if value >= 100 else "low"
                        
                        bars_html += f'''
                        <div class="ev-bar-enhanced {intensity}">
                            <div class="ev-bar-header">
                                <div class="ev-stat-info">
                                    <span class="ev-icon-enhanced">{icon}</span>
                                    <span class="ev-label-enhanced">{label}</span>
                                </div>
                                <div class="ev-value-badge" style="background-color: {color}20; color: {color};">
                                    {value}
                                </div>
                            </div>
                            <div class="ev-bar-track-enhanced">
                                <div class="ev-bar-fill-enhanced {intensity}" 
                                     style="width: {percentage}%; background: linear-gradient(90deg, {color}80, {color});"></div>
                                <div class="ev-bar-shimmer"></div>
                            </div>
                        </div>'''
                bars_html += '</div>'
                st.markdown(bars_html, unsafe_allow_html=True)
        except Exception:
            st.markdown('<div class="ev-parse-error">EV format could not be parsed</div>', unsafe_allow_html=True)


def render_page_header():
    """Render the professional main page header with quick stats"""
    # Get quick stats for better UX
    analysis_available = bool(st.session_state.get("analysis_result"))
    
    # Build stats display
    stats_items = []
    if analysis_available:
        stats_items.append("✅ Analysis Ready")
    
    stats_text = " • ".join(stats_items) if stats_items else "🚀 Ready to analyze VGC teams"
    
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px; margin-bottom: 2rem; 
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
            <h1 style="color: white; margin: 0; font-size: 3rem; font-weight: 700; 
                      text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                🏆 VGC Team Analyzer
            </h1>
            <p style="color: rgba(255,255,255,0.9); margin: 1rem 0 0 0; 
                      font-size: 1.3rem; font-weight: 300;">
                Instant Japanese VGC Article Translation & Team Analysis
            </p>
            <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; 
                      font-size: 1rem; background: rgba(255,255,255,0.1); 
                      padding: 0.5rem 1rem; border-radius: 25px; display: inline-block;">
                {stats_text}
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_analysis_input() -> tuple[str, str]:
    """
    Render consumer-friendly input section for article analysis

    Returns:
        Tuple of (input_type, content) where input_type is 'url', 'text', or 'screenshot'
    """
    st.header("🚀 Start Your Analysis")
    
    # Enhanced help section with performance tips
    help_expand = st.expander("📝 How it works & Pro Tips", expanded=False)
    with help_expand:
        st.markdown(
            """
            **🚀 Quick Start:**
            1. Choose your input method: Article URL or Article Text
            2. Click "Analyze" for instant AI-powered translation and team analysis
            3. Teams are automatically saved for searching and future reference
            
            **💡 Pro Tips:**
            - **Best Sources**: note.com, Japanese Pokemon blogs, tournament reports
            - **Session Storage**: Your analysis results are kept during your session
            - **Team Building**: Use export features to get pokepaste format for easy importing
            - **For Screenshots**: Use the 🎮 Switch Translation page for Nintendo Switch team screenshots
            
            **🔍 What we analyze from articles:**
            • Complete Pokemon team compositions with strategic explanations
            • EV spreads with detailed reasoning and calculations
            • Move selections and item choices with justifications
            • Team synergies, roles, and battle strategies
            • Tournament context, results, and author insights
            • Meta analysis and matchup considerations
            
            **📚 Supported Content:**
            • Japanese VGC tournament reports and team analyses
            • Pokemon blog posts with detailed team breakdowns
            • Championship and regional tournament articles
            • Strategy guides and team building explanations
            """
        )

    input_method = st.radio(
        "**Choose your input method:**", 
        ["🔗 Article URL", "📄 Article Text"], 
        horizontal=True
    )

    if input_method == "🔗 Article URL":
        url = st.text_input(
            "📎 **Paste your Japanese VGC article URL here:**",
            placeholder="https://note.com/example/article",
            help="✅ Supported: note.com, Japanese Pokemon blogs, tournament reports",
        )
        
        # Visual feedback for URL input
        if url and url.strip():
            if "note.com" in url or "hatenablog" in url or "pokemon" in url.lower():
                st.success("✅ Great! This looks like a supported VGC article URL")
            else:
                st.info("ℹ️ URL detected - we'll try to extract the content")
        
        return "url", url
        
    else:  # Article Text
        text = st.text_area(
            "📝 **Paste your article text here:**",
            height=200,
            placeholder="Copy the article content and paste it here for instant analysis...",
            help="💡 Tip: This works great if the URL method doesn't work for your article",
        )
        
        # Character count and feedback for text input
        if text and text.strip():
            char_count = len(text.strip())
            if char_count > 100:
                st.success(f"✅ {char_count:,} characters detected - ready for analysis!")
            elif char_count > 20:
                st.info(f"📝 {char_count} characters - you can add more content if needed")
            else:
                st.warning("⚠️ Content seems short - consider adding more text for better analysis")
        
        return "text", text


def render_pokemon_card(pokemon: Dict[str, Any], index: int):
    """
    Render a dynamic, visually enhanced Pokemon card
    
    Args:
        pokemon: Pokemon data dictionary
        index: Pokemon position in team (0-5)
    """
    name = pokemon.get("name", "Unknown Pokemon")
    tera_type = pokemon.get("tera_type", "Unknown")
    ability = pokemon.get('ability', 'Not specified')
    item = pokemon.get('held_item', 'Not specified')
    nature = pokemon.get('nature', 'Not specified')
    role = pokemon.get("role", "Not specified")
    moves = pokemon.get("moves", [])
    evs = pokemon.get("evs", "Not specified")
    ev_explanation = pokemon.get("ev_explanation", "No explanation provided")
    
    sprite_url = get_pokemon_sprite_url(name)
    type_class = get_pokemon_type_class(tera_type).lower()
    
    # Dynamic Pokemon card with enhanced visual hierarchy
    st.markdown(
        f"""
        <div class="poke-card-enhanced">
            <div class="poke-card-hero {type_class}">
                <div class="hero-background"></div>
                <div class="hero-content">
                    <div class="poke-slot-number">#{index + 1}</div>
                    <div class="poke-sprite-container">
                        <img src="{esc(sprite_url)}" alt="{esc(name)}" class="poke-sprite-large"
                             onerror="this.src='https://via.placeholder.com/96x96/f0f0f0/999?text={esc(name[:3])}'"/>
                        <div class="sprite-glow {type_class}"></div>
                    </div>
                    <div class="poke-title-section">
                        <h2 class="poke-name-hero">{esc(name)}</h2>
                        <div class="poke-type-badge {type_class}">
                            <span class="type-icon">⚡</span>
                            <span class="type-name">{esc(tera_type)}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Inject CSS for stat cards
    inject_stat_css()
    
    # Enhanced Battle Stats Section with individual stat cards
    st.markdown(render_stat_card("🧬", "Ability", ability), unsafe_allow_html=True)
    st.markdown(render_stat_card("🎒", "Held Item", item, accent="golden", prominent=True), unsafe_allow_html=True)
    st.markdown(render_stat_card("🌟", "Nature", nature), unsafe_allow_html=True)
    
    # Enhanced Moveset Section
    st.markdown('<div class="section-divider-enhanced"><span class="section-title">🎮 Combat Moveset</span></div>', unsafe_allow_html=True)
    render_moves_grid(moves)
    
    # Enhanced EV Distribution Section
    st.markdown('<div class="section-divider-enhanced"><span class="section-title">📊 EV Distribution</span></div>', unsafe_allow_html=True)
    render_ev_bars(evs)
    
    # Enhanced strategic reasoning section
    if ev_explanation != "No explanation provided":
        st.markdown(
            f'''
            <div class="strategy-section-enhanced">
                <div class="strategy-header">
                    <span class="strategy-icon">💡</span>
                    <span class="strategy-title">Strategic Reasoning</span>
                </div>
                <div class="strategy-content">
                    {esc(ev_explanation)}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )


def render_article_summary(analysis_result: Dict[str, Any]):
    """
    Render a prominent article summary section
    
    Args:
        analysis_result: Complete analysis result from VGC analyzer
    """
    # Analysis header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("📋 Article Summary")
    with col2:
        # Add analysis timestamp
        analysis_timestamp = analysis_result.get("analysis_timestamp", "Unknown")
        st.markdown(
            f'<div style="text-align: right; margin-top: 1rem;"><small>🕐 Analyzed: {esc(analysis_timestamp)}</small></div>',
            unsafe_allow_html=True
        )
    
    # Main summary card with gradient background
    title = analysis_result.get("title", "VGC Team Analysis")
    author = analysis_result.get("author", "Unknown Author")
    tournament_context = analysis_result.get("tournament_context", "Not specified")
    regulation = analysis_result.get("regulation", "Not specified")
    overall_strategy = analysis_result.get("overall_strategy", "Strategy not specified")
    
    # Create main summary card
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%); 
                    padding: 2.5rem; border-radius: 20px; color: white; margin: 1.5rem 0;
                    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);">
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="margin: 0 0 1rem 0; font-size: 2.2rem; font-weight: 700;">
                    ✨ {esc(title)}
                </h1>
                <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;
                           font-size: 1.1rem; opacity: 0.95;">
                    <span>👤 <strong>{esc(author)}</strong></span>
                    <span>📊 <strong>{esc(regulation)}</strong></span>
                    {f'<span>🏆 <strong>{esc(tournament_context)}</strong></span>' if tournament_context != "Not specified" else ''}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Quick team overview
    pokemon_team = analysis_result.get("pokemon_team", [])
    if pokemon_team:
        st.markdown("### 👥 Quick Team Overview")
        
        # Create team member badges
        team_names = [esc(pokemon.get('name', 'Unknown')) for pokemon in pokemon_team]
        team_badges = " • ".join([f"**{name}**" for name in team_names if name != 'Unknown'])
        
        st.markdown(
            f"""
            <div style="background: #f1f5f9; padding: 1.5rem; border-radius: 12px; 
                        border: 1px solid #cbd5e1; margin: 1rem 0;">
                <div style="color: #475569; font-size: 1.1rem; text-align: center;">
                    {team_badges}
                </div>
                <div style="text-align: center; margin-top: 0.5rem; color: #64748b; font-size: 0.9rem;">
                    Team Size: {len(pokemon_team)} Pokemon
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Strategic Analysis Section
    st.markdown("### 🧠 Strategic Analysis")
    
    # Team Strategy
    overall_strategy = analysis_result.get("overall_strategy", "")
    # Only display if strategy contains meaningful content, not generic placeholders
    if (overall_strategy and 
        overall_strategy not in ["Team strategy analysis recovered", "Team strategy details not fully extracted", 
                               "Strategy not specified", "Unable to process due to type error in validation", ""]):
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%); 
                        padding: 1.5rem; border-radius: 12px; border-left: 4px solid #0288d1; margin: 1rem 0;">
                <h4 style="color: #01579b; margin: 0 0 1rem 0;">🎯 Overall Strategy</h4>
                <p style="color: #0277bd; margin: 0; font-size: 1rem; line-height: 1.6;">
                    {esc(overall_strategy)}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Team Strengths and Weaknesses in columns
    col1, col2 = st.columns(2)
    
    with col1:
        team_strengths = analysis_result.get("team_strengths", "")
        # Show team strengths if we have meaningful content, not generic placeholders
        if (team_strengths and 
            team_strengths not in ["Team strengths analysis not available", "Team strengths analysis not fully extracted", 
                                 "Team strengths not specified", ""]):
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); 
                            padding: 1.5rem; border-radius: 12px; border-left: 4px solid #4caf50; margin: 1rem 0;">
                    <h4 style="color: #2e7d32; margin: 0 0 1rem 0;">🔥 Team Strengths</h4>
                    <div style="color: #388e3c; font-size: 0.95rem; line-height: 1.6;">
                        {esc(team_strengths).replace(chr(10), '<br>')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col2:
        team_weaknesses = analysis_result.get("team_weaknesses", "")
        # Show team weaknesses if we have meaningful content, not generic placeholders
        if (team_weaknesses and
            team_weaknesses not in ["Team weaknesses analysis not available", "Team weaknesses analysis not fully extracted",
                                  "Team weaknesses not specified", ""]):
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
                            padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f44336; margin: 1rem 0;">
                    <h4 style="color: #c62828; margin: 0 0 1rem 0;">⚠️ Team Weaknesses</h4>
                    <div style="color: #d32f2f; font-size: 0.95rem; line-height: 1.6;">
                        {esc(team_weaknesses).replace(chr(10), '<br>')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Team Synergies
    team_synergies = analysis_result.get("team_synergies", "")
    if team_synergies and not team_synergies.startswith("Team synergies analysis not available"):
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 40%); 
                        padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ff9800; margin: 1rem 0;">
                <h4 style="color: #ef6c00; margin: 0 0 1rem 0;">🤝 Team Synergies</h4>
                <div style="color: #f57c00; font-size: 0.95rem; line-height: 1.6;">
                    {esc(team_synergies).replace(chr(10), '<br>')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Meta Analysis
    meta_analysis = analysis_result.get("meta_analysis", "")
    if meta_analysis and not meta_analysis.startswith("Meta analysis not available"):
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); 
                        padding: 1.5rem; border-radius: 12px; border-left: 4px solid #9c27b0; margin: 1rem 0;">
                <h4 style="color: #6a1b9a; margin: 0 0 1rem 0;">📊 Meta Analysis</h4>
                <div style="color: #7b1fa2; font-size: 0.95rem; line-height: 1.6;">
                    {esc(meta_analysis).replace(chr(10), '<br>')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Full Translation Section
    full_translation = analysis_result.get("full_translation", "")
    if full_translation and not full_translation.startswith("Full translation not available"):
        with st.expander("📖 Complete Article Translation", expanded=False):
            st.markdown(
                f"""
                <div style="background: #fafafa; padding: 1.5rem; border-radius: 8px; 
                            border: 1px solid #e0e0e0; line-height: 1.8; font-size: 0.95rem;">
                    {esc(full_translation).replace(chr(10), '<br><br>')}
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.divider()


def render_team_showcase(analysis_result: Dict[str, Any]):
    """
    Render the professional team showcase

    Args:
        analysis_result: Complete analysis result from VGC analyzer
    """
    # Success message
    st.success("🎉 **Analysis Complete!** Your Japanese VGC article has been successfully translated and analyzed.")
    
    # Team overview with professional styling
    title = analysis_result.get("title", "VGC Team Analysis")
    
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 20px; color: white; margin: 1rem 0;
                    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);">
            <h2 style="margin: 0 0 0.5rem 0; font-size: 2rem; font-weight: 700;">
                🏆 {esc(title)}
            </h2>
            <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">
                Professional VGC team analysis and strategy breakdown
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Key info in professional cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        regulation = analysis_result.get("regulation", "Not specified")
        st.markdown(
            f"""
            <div style="background: white; padding: 1.5rem; border-radius: 15px; 
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
                        border-left: 4px solid #28a745;">
                <h3 style="color: #28a745; margin: 0 0 0.5rem 0;">📋 Regulation</h3>
                <p style="margin: 0; font-size: 1.2rem; font-weight: 600; color: #2c3e50;">
                    {esc(regulation)}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        team_size = len(analysis_result.get("pokemon_team", []))
        st.markdown(
            f"""
            <div style="background: white; padding: 1.5rem; border-radius: 15px; 
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
                        border-left: 4px solid #667eea;">
                <h3 style="color: #667eea; margin: 0 0 0.5rem 0;">👥 Team Size</h3>
                <p style="margin: 0; font-size: 1.2rem; font-weight: 600; color: #2c3e50;">
                    {team_size} Pokemon
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        author = analysis_result.get("author", "Unknown")
        st.markdown(
            f"""
            <div style="background: white; padding: 1.5rem; border-radius: 15px; 
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
                        border-left: 4px solid #764ba2;">
                <h3 style="color: #764ba2; margin: 0 0 0.5rem 0;">👤 Author</h3>
                <p style="margin: 0; font-size: 1.2rem; font-weight: 600; color: #2c3e50;">
                    {esc(author)}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Strategy section with better formatting
    strategy = analysis_result.get("overall_strategy", "Strategy not specified")
    if strategy != "Strategy not specified":
        st.markdown("### 💡 Team Strategy")
        st.markdown(
            f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 15px; 
                        border-left: 4px solid #667eea; margin: 1rem 0;">
                <p style="margin: 0; color: #2c3e50; font-size: 16px; line-height: 1.6;">
                    {esc(strategy)}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Strengths and weaknesses in professional layout
    strengths = analysis_result.get("strengths", [])
    weaknesses = analysis_result.get("weaknesses", [])
    
    if strengths or weaknesses:
        col1, col2 = st.columns(2)

        with col1:
            if strengths:
                st.markdown("### ✅ Key Strengths")
                for strength in strengths:
                    st.markdown(f"• {strength}")

        with col2:
            if weaknesses:
                st.markdown("### ⚠️ Considerations")
                for weakness in weaknesses:
                    st.markdown(f"• {weakness}")

    # Meta relevance
    meta_relevance = analysis_result.get("meta_relevance", "")
    if meta_relevance and meta_relevance != "Not specified":
        st.markdown("### 📊 Meta Analysis")
        st.markdown(
            f"""
            <div style="background: #e8f5e8; padding: 1.5rem; border-radius: 15px; 
                        border-left: 4px solid #28a745; margin: 1rem 0;">
                <p style="margin: 0; color: #2c3e50; font-size: 16px; line-height: 1.6;">
                    {esc(meta_relevance)}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Enhanced user experience: Quick actions 
    st.markdown("---")
    
    # Quick navigation options
    st.markdown("**⚡ What's next?**")
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    with nav_col1:
        if st.button("📚 View All Teams", help="Browse your complete team collection", key="view_all_teams"):
            st.session_state.current_page = "📚 Saved Teams"
            st.rerun()
    
    with nav_col2:
        if st.button("🆕 New Analysis", help="Analyze another VGC article", key="new_analysis_quick"):
            st.session_state.analysis_result = None
            st.session_state.current_url = None
            st.session_state.analysis_complete = False
            st.rerun()
    
    with nav_col3:
        st.button("📊 Export Team", help="Use the export options below", disabled=True)


def render_pokemon_team(pokemon_team):
    """
    Render the Pokemon team with enhanced formatting and sprite grid

    Args:
        pokemon_team: List of Pokemon data dictionaries or dict with pokemon data
    """
    st.header("🏆 Your VGC Team")

    if not pokemon_team:
        st.warning("❌ No Pokemon team data available")
        return
    
    # Handle both list and dictionary inputs
    if isinstance(pokemon_team, dict):
        # If it's a dict, get the values or look for 'pokemon' key
        if 'pokemon' in pokemon_team:
            team_list = pokemon_team['pokemon']
        else:
            team_list = list(pokemon_team.values())
    else:
        team_list = pokemon_team
    
    # Filter and validate pokemon entries - only keep valid dictionary entries
    valid_pokemon = []
    for pokemon in team_list:
        if isinstance(pokemon, dict):
            # Valid pokemon dict - keep it
            valid_pokemon.append(pokemon)
        elif isinstance(pokemon, str):
            # Convert string to basic pokemon dict
            valid_pokemon.append({'name': pokemon, 'role': 'Unknown'})
        # Skip any other invalid entries
    
    team_list = valid_pokemon
    
    # Check if we have any valid pokemon after filtering
    if not team_list:
        st.warning("❌ No valid Pokemon data found in team")
        return
    
    # Team sprite grid overview
    st.subheader("📋 Team Overview")
    
    # Create sprite grid - display in rows of 3
    rows = [team_list[i:i+3] for i in range(0, len(team_list), 3)]
    
    for row in rows:
        cols = st.columns(3)
        for i, pokemon in enumerate(row):
            with cols[i]:
                name = pokemon.get('name', 'Unknown')
                sprite_url = get_pokemon_sprite_url(name)
                role = pokemon.get('role', 'Unknown')
                
                # Create a beautiful Pokemon preview card
                st.markdown(
                    f"""
                    <div class="team-preview-card">
                        <div style="text-align: center; padding: 15px; border-radius: 12px; 
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    color: white; margin: 10px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                            <img src="{esc(sprite_url)}" width="100" style="display: block; margin: 0 auto;"/>
                            <h4 style="margin: 10px 0 5px 0; font-size: 16px;">{esc(name)}</h4>
                            <p style="margin: 0; font-size: 12px; opacity: 0.9;">🎯 {esc(role)}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    st.divider()

    # Render Pokemon cards in 2-column layout to reduce scrolling
    for i in range(0, len(team_list), 2):
        col1, col2 = st.columns([1, 1])
        
        # Render first Pokemon of the pair
        with col1:
            render_pokemon_card(team_list[i], i)
        
        # Render second Pokemon of the pair (if it exists)
        if i + 1 < len(team_list):
            with col2:
                render_pokemon_card(team_list[i + 1], i + 1)
        else:
            # If odd number of Pokemon, leave second column empty
            with col2:
                st.empty()
        
    # Team analysis summary
    st.markdown(
        """
        <div class="team-footer">
            <p><em>💡 Use the EV Strategy expanders above to understand the reasoning behind each Pokemon's stat distribution.</em></p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_export_section(analysis_result: Dict[str, Any]):
    """
    Render export functionality section

    Args:
        analysis_result: Complete analysis result
    """
    st.header("💾 Export Options")

    col1, col2 = st.columns(2)

    with col1:
        # Translation download
        translation_content = create_translation_export(analysis_result)
        st.download_button(
            label="📄 Download Translation",
            data=translation_content,
            file_name=f"{analysis_result.get('title', 'vgc_translation')}.txt",
            mime="text/plain",
            help="Download complete English translation as text file",
        )

    with col2:
        # Pokepaste export
        pokepaste_content = create_pokepaste(
            analysis_result.get("pokemon_team", []),
            analysis_result.get("title", "VGC Team"),
        )
        st.download_button(
            label="📋 Export Pokepaste",
            data=pokepaste_content,
            file_name=f"{analysis_result.get('title', 'vgc_team')}_pokepaste.txt",
            mime="text/plain",
            help="Export team in pokepaste format for easy importing",
        )

    # One-click Pokepaste copy (st.code has a built-in copy button)
    with st.expander("📋 Pokepaste (click to copy)", expanded=False):
        st.code(pokepaste_content, language=None)

    # Raw JSON viewer for debugging
    with st.expander("🔍 Raw JSON Data", expanded=False):
        st.json(analysis_result)


def create_translation_export(analysis_result: Dict[str, Any]) -> str:
    """
    Create formatted translation export content

    Args:
        analysis_result: Analysis result to format

    Returns:
        Formatted translation content
    """
    lines = []

    # Header
    title = analysis_result.get("title", "VGC Team Analysis")
    lines.extend(["=" * 60, f"POKEMON VGC ANALYSIS: {title.upper()}", "=" * 60, ""])

    # Metadata
    author = analysis_result.get("author", "Unknown")
    regulation = analysis_result.get("regulation", "Not specified")
    tournament = analysis_result.get("tournament_context", "Not specified")

    lines.extend(
        [
            f"Author: {author}",
            f"Regulation: {regulation}",
            f"Tournament Context: {tournament}",
            "",
        ]
    )

    # Overall strategy
    strategy = analysis_result.get("overall_strategy", "Not specified")
    lines.extend(["OVERALL STRATEGY:", "-" * 20, strategy, ""])

    # Team members
    pokemon_team = analysis_result.get("pokemon_team", [])
    if pokemon_team:
        lines.extend(["TEAM MEMBERS:", "-" * 15, ""])

        for i, pokemon in enumerate(pokemon_team, 1):
            name = pokemon.get("name", "Unknown")
            ability = pokemon.get("ability", "Not specified")
            item = pokemon.get("held_item", "Not specified")
            nature = pokemon.get("nature", "Not specified")
            tera = pokemon.get("tera_type", "Not specified")
            evs = pokemon.get("evs", "Not specified")
            role = pokemon.get("role", "Not specified")
            explanation = pokemon.get("ev_explanation", "Not specified")
            moves = pokemon.get("moves", [])

            lines.extend(
                [
                    f"{i}. {name}",
                    f"   Ability: {ability}",
                    f"   Item: {item}",
                    f"   Nature: {nature}",
                    f"   Tera Type: {tera}",
                    f"   Role: {role}",
                    f"   EVs: {evs}",
                    f"   EV Reasoning: {explanation}",
                    f"   Moves: {', '.join(moves)}",
                    "",
                ]
            )

    # Strengths and weaknesses
    strengths = analysis_result.get("strengths", [])
    weaknesses = analysis_result.get("weaknesses", [])

    if strengths:
        lines.extend(["TEAM STRENGTHS:", "-" * 15])
        for strength in strengths:
            lines.append(f"• {strength}")
        lines.append("")

    if weaknesses:
        lines.extend(["TEAM WEAKNESSES:", "-" * 16])
        for weakness in weaknesses:
            lines.append(f"• {weakness}")
        lines.append("")

    # Meta relevance
    meta_relevance = analysis_result.get("meta_relevance", "")
    if meta_relevance:
        lines.extend(["META RELEVANCE:", "-" * 15, meta_relevance, ""])

    # Footer
    lines.extend(
        [
            "=" * 60,
            "Generated by Pokemon VGC Analysis Tool",
            "https://github.com/your-repo/pokemon-vgc-analysis",
            "=" * 60,
        ]
    )

    return "\n".join(lines)


def log_user_feedback(url: str, problem_type: str, description: str) -> bool:
    """
    Log user feedback to local file for developer review
    
    Args:
        url: The article URL that had issues
        problem_type: Category of the problem
        description: Detailed problem description
        
    Returns:
        True if logging successful, False otherwise
    """
    try:
        import json
        
        feedback_file = "feedback_log.txt"
        feedback_json = "feedback_data.json"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create structured feedback entry
        feedback_entry = {
            "timestamp": timestamp,
            "url": url,
            "problem_type": problem_type,
            "description": description,
            "id": hash(f"{timestamp}{url}{description}") % 10000  # Simple ID for tracking
        }
        
        # Log to human-readable text file
        text_entry = f"""
{'='*50}
FEEDBACK #{feedback_entry['id']} - {timestamp}
{'='*50}
URL: {url}
Problem Type: {problem_type}
Description: {description}
{'='*50}

"""
        
        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(text_entry)
        
        # Also log to JSON for easier programmatic access
        try:
            # Try to read existing JSON data
            try:
                with open(feedback_json, "r", encoding="utf-8") as f:
                    feedback_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                feedback_data = {"feedback": []}
            
            # Add new entry
            feedback_data["feedback"].append(feedback_entry)
            
            # Write back to JSON file
            with open(feedback_json, "w", encoding="utf-8") as f:
                json.dump(feedback_data, f, indent=2, ensure_ascii=False)
                
        except Exception as json_error:
            # JSON logging is optional - don't fail if it doesn't work
            pass
        
        return True
        
    except Exception as e:
        st.error(f"Failed to log feedback: {str(e)}")
        return False


# Re-export from split modules for backward compatibility
from ui.sidebar import render_sidebar, render_image_analysis_section  # noqa: E402
from ui.css import apply_custom_css  # noqa: E402
