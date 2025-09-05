"""
UI Components for Pokemon VGC Analysis application
"""

import streamlit as st
from typing import Dict, List, Any
from utils import (
    get_pokemon_sprite_url,
    format_moves_html,
    get_pokemon_type_class,
    get_role_class,
    create_pokepaste,
)

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
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value}</div>
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
                <span class="move-name-dynamic" title="{move_display}">{move_display}</span>
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
    st.markdown(f'<div class="ev-summary-enhanced"><span class="ev-label-text">EV Distribution:</span> <code class="ev-code-enhanced">{evs}</code></div>', unsafe_allow_html=True)
    
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
            - **Speed Boost**: Recently analyzed content is cached for faster loading
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
                        <img src="{sprite_url}" alt="{name}" class="poke-sprite-large" 
                             onerror="this.src='https://via.placeholder.com/96x96/f0f0f0/999?text={name[:3]}'"/>
                        <div class="sprite-glow {type_class}"></div>
                    </div>
                    <div class="poke-title-section">
                        <h2 class="poke-name-hero">{name}</h2>
                        <div class="poke-type-badge {type_class}">
                            <span class="type-icon">⚡</span>
                            <span class="type-name">{tera_type}</span>
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
                    {ev_explanation}
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
    # Analysis header with cache status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("📋 Article Summary")
    with col2:
        # Add cache status indicator
        is_cached = analysis_result.get("is_cached_result", False)
        analysis_timestamp = analysis_result.get("analysis_timestamp", "Unknown")
        
        if is_cached:
            st.markdown(
                f'<div style="text-align: right; margin-top: 1rem;"><small>💾 <b>Cached Result</b><br>🕐 {analysis_timestamp}</small></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="text-align: right; margin-top: 1rem;"><small>✨ <b>Fresh Analysis</b><br>🕐 {analysis_timestamp}</small></div>',
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
                    ✨ {title}
                </h1>
                <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; 
                           font-size: 1.1rem; opacity: 0.95;">
                    <span>👤 <strong>{author}</strong></span>
                    <span>📊 <strong>{regulation}</strong></span>
                    {f'<span>🏆 <strong>{tournament_context}</strong></span>' if tournament_context != "Not specified" else ''}
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
        team_names = [pokemon.get('name', 'Unknown') for pokemon in pokemon_team]
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
    if overall_strategy:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%); 
                        padding: 1.5rem; border-radius: 12px; border-left: 4px solid #0288d1; margin: 1rem 0;">
                <h4 style="color: #01579b; margin: 0 0 1rem 0;">🎯 Overall Strategy</h4>
                <p style="color: #0277bd; margin: 0; font-size: 1rem; line-height: 1.6;">
                    {overall_strategy}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Team Strengths and Weaknesses in columns
    col1, col2 = st.columns(2)
    
    with col1:
        team_strengths = analysis_result.get("team_strengths", "")
        # Show team strengths if we have meaningful content or indicate when not available
        if team_strengths and not team_strengths.startswith("Team strengths analysis not available"):
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); 
                            padding: 1.5rem; border-radius: 12px; border-left: 4px solid #4caf50; margin: 1rem 0;">
                    <h4 style="color: #2e7d32; margin: 0 0 1rem 0;">🔥 Team Strengths</h4>
                    <div style="color: #388e3c; font-size: 0.95rem; line-height: 1.6;">
                        {team_strengths.replace(chr(10), '<br>')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with col2:
        team_weaknesses = analysis_result.get("team_weaknesses", "")
        # Show team weaknesses if we have meaningful content or indicate when not available
        if team_weaknesses and not team_weaknesses.startswith("Team weaknesses analysis not available"):
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); 
                            padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f44336; margin: 1rem 0;">
                    <h4 style="color: #c62828; margin: 0 0 1rem 0;">⚠️ Team Weaknesses</h4>
                    <div style="color: #d32f2f; font-size: 0.95rem; line-height: 1.6;">
                        {team_weaknesses.replace(chr(10), '<br>')}
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
                    {team_synergies.replace(chr(10), '<br>')}
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
                    {meta_analysis.replace(chr(10), '<br>')}
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
                    {full_translation.replace(chr(10), '<br><br>')}
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
                🏆 {title}
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
                    {regulation}
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
                    {author}
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
                    {strategy}
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
                    {meta_relevance}
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
                            <img src="{sprite_url}" width="100" style="display: block; margin: 0 auto;"/>
                            <h4 style="margin: 10px 0 5px 0; font-size: 16px;">{name}</h4>
                            <p style="margin: 0; font-size: 12px; opacity: 0.9;">🎯 {role}</p>
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


def render_sidebar():
    """Clean and user-friendly sidebar with essential navigation"""
    with st.sidebar:
        # Clean sidebar header
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.5rem; margin: -1rem -1rem 1.5rem -1rem; border-radius: 0 0 15px 15px;">
                <h2 style="color: white; margin: 0; text-align: center; font-size: 1.5rem;">
                    ⚔️ VGC Analyzer
                </h2>
                <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; text-align: center; font-size: 0.95rem;">
                    Pokemon Team Analysis
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Clean navigation
        page = st.selectbox(
            "**Navigate to:**",
            [
                "🏠 Analysis Home",
                "🎮 Switch Translation",
                "⚙️ Settings",
                "📖 Help & Guide"
            ],
            index=0
        )
        
        st.markdown("---")
        
        # Essential actions only
        if st.button("🆕 New Analysis", use_container_width=True, type="primary"):
            st.session_state.analysis_result = None
            st.session_state.current_url = None
            st.session_state.analysis_complete = False
            st.rerun()
        
        # Current analysis status (only if available)
        if st.session_state.get("analysis_result"):
            st.markdown("---")
            result = st.session_state.analysis_result
            pokemon_count = len(result.get("pokemon_team", []))
            regulation = result.get("regulation", "Unknown")
            
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                           padding: 1rem; border-radius: 10px; border-left: 4px solid #0ea5e9; margin: 0.5rem 0;">
                    <div style="font-size: 0.9rem; color: #0f172a;">
                        <strong>📊 Current Team</strong><br>
                        🏆 {pokemon_count} Pokemon<br>
                        📋 Regulation {regulation}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Minimal about section
        st.markdown("---")
        st.markdown(
            """
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; text-align: center;">
                <small style="color: #64748b;">
                    <strong>✨ VGC Analysis Tool</strong><br>
                    Powered by Google Gemini 2.5<br><br>
                    🎯 Instant Japanese Translation<br>
                    📊 Professional Team Analysis<br>
                    📋 Export Ready Formats
                </small>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Add cache clearing section
        st.markdown("---")
        st.markdown("**🛠️ Troubleshooting**")
        
        if st.button("🗑️ Clear Cache & Reset", 
                    use_container_width=True, 
                    help="Clear all cached results and reset the application. Use this if you see old analysis results."):
            
            # Import cache at the point of use to avoid circular imports
            try:
                from utils import cache
                
                # Clear all caches
                st.session_state.clear()  # Clear session state
                cache.clear_all()         # Clear file cache
                
                # Show success message
                st.success("✅ Cache cleared! Application reset complete.")
                st.info("📝 The page will refresh to load fresh data.")
                
                # Force rerun to reset everything
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error clearing cache: {str(e)}")
                st.info("💡 Try refreshing the page manually.")
        
        return page


def render_image_analysis_section(analysis_result: Dict[str, Any]):
    """Render consumer-friendly image analysis insights"""
    image_analysis = analysis_result.get("image_analysis")
    
    if not image_analysis or not image_analysis.get("success", False):
        return
        
    # Count total EV spreads found across all images
    total_ev_spreads = 0
    image_analyses = image_analysis.get("image_analyses", [])
    
    for img_analysis in image_analyses:
        total_ev_spreads += len(img_analysis.get("ev_spreads", []))
    
    # Only show if we found additional EV data from images
    if total_ev_spreads > 0:
        st.success(f"🎯 Enhanced Analysis: Found {total_ev_spreads} additional EV spread{'s' if total_ev_spreads != 1 else ''} from team images!")
        
        # Show the EV spreads in a clean format
        with st.expander("📊 View Additional EV Spreads", expanded=False):
            for i, img_analysis in enumerate(image_analyses):
                ev_spreads = img_analysis.get("ev_spreads", [])
                if ev_spreads:
                    st.write(f"**From Image {i+1}:**")
                    for j, ev_spread in enumerate(ev_spreads):
                        spread_format = ev_spread.get('format', 'Unknown')
                        st.code(f"{spread_format} (Total: {ev_spread.get('total', 'Unknown')} EVs)")
                    st.divider()
    else:
        # Just show a subtle indicator that image analysis was performed
        st.info("🔍 Team images analyzed for additional details")


def apply_custom_css():
    """Apply clean, professional CSS styling for VGC Analysis Platform"""
    st.markdown(
        """
    <style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Clean design tokens */
    :root {
        --color-gray-50: #f9fafb;
        --color-gray-100: #f3f4f6;
        --color-gray-200: #e5e7eb;
        --color-gray-300: #d1d5db;
        --color-gray-400: #9ca3af;
        --color-gray-500: #6b7280;
        --color-gray-600: #4b5563;
        --color-gray-700: #374151;
        --color-gray-800: #1f2937;
        --color-gray-900: #111827;
        
        --color-blue-50: #eff6ff;
        --color-blue-100: #dbeafe;
        --color-blue-500: #3b82f6;
        --color-blue-600: #2563eb;
        --color-blue-700: #1d4ed8;
        
        --color-green-50: #f0fdf4;
        --color-green-500: #22c55e;
        --color-green-600: #16a34a;
        
        --color-red-50: #fef2f2;
        --color-red-500: #ef4444;
        --color-red-600: #dc2626;
        
        --color-amber-50: #fffbeb;
        --color-amber-500: #f59e0b;
        --color-amber-600: #d97706;
        
        --color-purple-50: #faf5ff;
        --color-purple-500: #a855f7;
        --color-purple-600: #9333ea;
        
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        
        --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Modern typography */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Main application styling */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Main content container - improved for split screen */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: none;
        overflow-x: hidden; /* Prevent horizontal scrolling */
    }
    
    /* Ensure columns don't overflow */
    .stColumns {
        overflow: hidden;
    }
    
    .stColumn {
        min-width: 0; /* Allow columns to shrink below content size */
        overflow-wrap: break-word; /* Break long words if needed */
    }
    
    /* Sidebar styling with VGCMulticalc inspiration */
    .stSidebar > div:first-child {
        background: var(--surface);
        border-right: 1px solid var(--border-color);
        box-shadow: var(--shadow-md);
    }
    
    .stSidebar .stMarkdown {
        padding: 0;
    }
    
    /* Custom scrollbar for sidebar */
    .stSidebar ::-webkit-scrollbar {
        width: 6px;
    }
    
    .stSidebar ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    
    .stSidebar ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #cbd5e1, #94a3b8);
        border-radius: 3px;
    }
    
    .stSidebar ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #94a3b8, #64748b);
    }
    
    /* Enhanced button styling with VGCMulticalc aesthetics */
    .stButton > button {
        width: 100%;
        border-radius: var(--border-radius-sm);
        border: none;
        background: var(--primary-gradient);
        color: white;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 14px;
        box-shadow: var(--shadow-sm);
        letter-spacing: 0.025em;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }
    
    /* Primary button enhancement */
    .stButton > button[kind="primary"] {
        background: var(--success-gradient);
        font-weight: 600;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        box-shadow: var(--shadow-lg);
    }
    
    /* Professional Pokemon Card Styling - CSS Grid Based */
    .professional-pokemon-card {
        background: var(--surface);
        border-radius: 20px;
        padding: 0;
        margin: 3rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        border: 1px solid rgba(99, 102, 241, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
        container-type: inline-size; /* Enable container queries */
        min-width: 320px; /* Safe minimum width */
    }
    
    .professional-pokemon-card:hover {
        box-shadow: 0 20px 60px rgba(99, 102, 241, 0.25);
        border-color: rgba(99, 102, 241, 0.3);
        /* Removed transform to prevent overflow issues */
    }
    
    .professional-pokemon-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        z-index: 1;
    }
    
    /* New Pokemon Card Wrapper - Compact Vertical Spacing */
    .pokemon-card-wrapper {
        background: var(--surface);
        border-radius: 20px;
        margin: 1rem 0; /* Reduced from 3rem to 1rem (16px vs 48px) */
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        border: 1px solid rgba(99, 102, 241, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
        container-type: inline-size;
        min-width: 320px;
    }
    
    .pokemon-card-wrapper:hover {
        box-shadow: 0 20px 60px rgba(99, 102, 241, 0.25);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .pokemon-card-wrapper::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        z-index: 1;
    }
    
    /* Header with minimal bottom spacing for tight gap */
    .pokemon-card-wrapper .card-header-modern {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem 0.5rem 2rem; /* Further reduced bottom padding to 0.5rem (8px) */
        position: relative;
        overflow: hidden;
        margin-bottom: 0; /* Explicit zero margin */
    }
    
    /* Grid container with minimal top padding for seamless connection */
    .pokemon-card-wrapper .pokemon-card-container {
        padding-top: 0.5rem; /* Further reduced from 0.75rem to 0.5rem (8px) */
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        margin-top: 0; /* Explicit zero margin */
    }
    
    .card-header-modern {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        position: relative;
        overflow: hidden;
        /* Removed problematic ::after pseudo-element */
    }
    
    /* CSS Grid Container for Pokemon Card Layout */
    .pokemon-card-container {
        display: grid;
        grid-template-columns: minmax(200px, 1fr) minmax(300px, 2fr) minmax(200px, 1fr);
        gap: 1.5rem;
        padding: 2rem;
        min-height: 400px;
        container-type: inline-size;
    }
    
    /* Container queries for responsive behavior */
    @container (max-width: 800px) {
        .pokemon-card-container {
            grid-template-columns: 1fr;
            gap: 1rem;
            padding: 1.5rem;
        }
    }
    
    @container (max-width: 600px) {
        .pokemon-card-container {
            padding: 1rem;
            gap: 0.75rem;
        }
    }
    
    .pokemon-number-badge {
        background: rgba(255,255,255,0.25);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.2rem;
        color: white;
        margin-bottom: 1rem;
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255,255,255,0.3);
    }
    
    .pokemon-title-section h2.pokemon-name-title {
        color: white;
        margin: 0.5rem 0 1rem 0;
        font-size: clamp(1.5rem, 4vw, 2.2rem); /* Responsive font size */
        font-weight: 800;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
        max-width: 100%;
    }
    
    .tera-badge-modern {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        color: white;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255,255,255,0.2);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .tera-icon {
        font-size: 1rem;
    }
    
    .tera-text {
        font-weight: 700;
    }
    
    /* Removed problematic absolute positioning decoration */
    
    /* Grid Section Styling */
    .pokemon-sprite-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1.5rem;
        gap: 1rem;
    }
    
    .pokemon-info-section {
        display: flex;
        flex-direction: column;
        padding: 1.5rem;
        gap: 1rem;
        min-width: 0; /* Allow content to shrink */
    }
    
    .pokemon-stats-section {
        display: flex;
        flex-direction: column;
        padding: 1.5rem;
        gap: 1rem;
        min-width: 0; /* Allow content to shrink */
    }
    
    /* Sprite Container Styling */
    .pokemon-sprite-container {
        text-align: center;
        padding: 1.5rem;
    }
    
    .sprite-frame {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 2px solid rgba(99, 102, 241, 0.1);
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .sprite-frame:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
    }
    
    .pokemon-sprite {
        width: 160px;
        height: 160px;
        object-fit: contain;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }
    
    .pokemon-name-label {
        font-size: clamp(1rem, 2.5vw, 1.1rem);
        font-weight: 700;
        color: var(--on-surface);
        margin-bottom: 0.8rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
        max-width: 100%;
    }
    
    .pokemon-role-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 0.8rem 1.2rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: all 0.2s ease;
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    .pokemon-role-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }
    
    .role-icon {
        font-size: 1rem;
    }
    
    .role-text {
        font-weight: 700;
    }
    
    /* Info Section Styling */
    .info-section {
        padding: 1.5rem;
    }
    
    .info-section h4 {
        color: var(--on-surface);
        margin-bottom: 1.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        border-bottom: 2px solid rgba(99, 102, 241, 0.2);
        padding-bottom: 0.5rem;
    }
    
    /* Section Headers with Improved Spacing */
    .section-header {
        margin: 1.5rem 0 1.0rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(99, 102, 241, 0.1);
    }
    
    .section-header h4 {
        margin: 0 !important;
        color: #4f46e5 !important;
        font-weight: 700 !important;
    }
    
    .info-item {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 1.0rem;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 12px;
        border-left: 4px solid #6366f1;
        transition: all 0.2s ease;
        width: 100%;
        box-sizing: border-box;
    }
    
    .info-item:hover {
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        /* Removed transform to prevent overflow */
    }
    
    .info-item.not-specified {
        border-left-color: #94a3b8;
        opacity: 0.7;
    }
    
    .info-icon {
        font-size: 1.2rem;
        min-width: 20px;
    }
    
    .info-label {
        font-weight: 600;
        color: var(--on-surface);
        min-width: 60px; /* Reduced min-width for flexibility */
        flex-shrink: 0;
    }
    
    .info-value {
        font-weight: 500;
        color: #475569;
        font-style: italic;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
        flex: 1; /* Allow to grow and shrink */
        min-width: 0;
    }
    
    .info-item.specified .info-value {
        font-style: normal;
        color: var(--on-surface);
        font-weight: 600;
    }
    
    /* Moveset Styling */
    .moveset-container {
        display: grid;
        gap: 0.9rem;
        margin-top: 1.2rem;
        margin-bottom: 1.5rem;
        width: 100%;
    }
    
    .move-item {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 1.0rem 1.2rem;
        background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%);
        border-radius: 12px;
        border-left: 4px solid #0ea5e9;
        transition: all 0.2s ease;
        width: 100%;
        box-sizing: border-box;
    }
    
    .move-item:hover {
        background: linear-gradient(135deg, #b3e5fc 0%, #81d4fa 100%);
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
        /* Removed transform to prevent overflow */
    }
    
    .move-item.empty {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-left-color: #94a3b8;
        opacity: 0.6;
    }
    
    .move-number {
        background: rgba(14, 165, 233, 0.2);
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        color: #0369a1;
    }
    
    .move-item.empty .move-number {
        background: rgba(148, 163, 184, 0.2);
        color: #64748b;
    }
    
    .move-name {
        font-weight: 600;
        color: #0369a1;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
        flex: 1;
        min-width: 0;
    }
    
    .move-item.empty .move-name {
        color: #64748b;
        font-style: italic;
    }
    
    .moveset-empty {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        font-style: italic;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        margin-top: 1rem;
    }
    
    /* Stats Section Styling */
    .stats-section {
        padding: 1.5rem;
    }
    
    .stats-section h4 {
        color: var(--on-surface);
        margin-bottom: 1.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        border-bottom: 2px solid rgba(99, 102, 241, 0.2);
        padding-bottom: 0.5rem;
    }
    
    .ev-spread-display {
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .ev-code {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #f1f5f9;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
        font-size: 1.1rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 2px solid rgba(99, 102, 241, 0.2);
    }
    
    .ev-bars-container {
        margin-top: 1.5rem;
        display: grid;
        gap: 1rem;
    }
    
    .ev-bar-item {
        background: var(--surface);
        border-radius: 12px;
        padding: 0.8rem;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .ev-bar-label {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    
    .ev-icon {
        font-size: 1rem;
    }
    
    .ev-stat {
        font-weight: 600;
        color: var(--on-surface);
        flex: 1;
        margin-left: 8px;
    }
    
    .ev-value {
        font-weight: 700;
        color: #6366f1;
        font-size: 1rem;
    }
    
    .ev-bar-track {
        background: #e2e8f0;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .ev-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 4px;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .ev-bar-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .ev-parse-error, .ev-not-specified {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        font-style: italic;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        margin-top: 1rem;
        border: 1px dashed #cbd5e1;
    }
    
    .ev-explanation {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #22c55e;
        color: #166534;
        line-height: 1.6;
        margin-top: 0.5rem;
    }
    
    .ev-explanation.empty {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-left-color: #94a3b8;
        color: #64748b;
        font-style: italic;
    }
    
    /* Card Divider */
    .card-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
        margin: 3rem 0;
        position: relative;
    }
    
    .card-divider::before {
        content: '⚡';
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        background: var(--surface);
        padding: 0 1rem;
        color: #6366f1;
        font-size: 1.2rem;
    }
    
    /* Team preview cards */
    .team-preview-card {
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .team-preview-card:hover {
        transform: translateY(-2px) scale(1.05);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--surface-variant);
        border-radius: var(--border-radius-sm);
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: var(--on-surface);
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: #e2e8f0;
        border-color: #cbd5e1;
    }
    
    .streamlit-expanderContent {
        background: var(--surface);
        border: 1px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 var(--border-radius-sm) var(--border-radius-sm);
        padding: 1rem;
    }
    
    /* Enhanced Type and Tera badges */
    .tera-badge {
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
        margin-left: 1rem;
        box-shadow: var(--shadow-sm);
        backdrop-filter: blur(10px);
    }
    
    /* Type color system */
    .type-fire { background: linear-gradient(135deg, #F08030 0%, #E4722E 100%); }
    .type-water { background: linear-gradient(135deg, #6890F0 0%, #5E7FDB 100%); }
    .type-grass { background: linear-gradient(135deg, #78C850 0%, #6BB544 100%); }
    .type-electric { background: linear-gradient(135deg, #F8D030 0%, #F4C20D 100%); }
    .type-psychic { background: linear-gradient(135deg, #F85888 0%, #F24C7C 100%); }
    .type-fighting { background: linear-gradient(135deg, #C03028 0%, #A82A23 100%); }
    .type-poison { background: linear-gradient(135deg, #A040A0 0%, #8E3A8E 100%); }
    .type-ground { background: linear-gradient(135deg, #E0C068 0%, #D4B451 100%); }
    .type-flying { background: linear-gradient(135deg, #A890F0 0%, #9A82E8 100%); }
    .type-bug { background: linear-gradient(135deg, #A8B820 0%, #97A51D 100%); }
    .type-rock { background: linear-gradient(135deg, #B8A038 0%, #A59132 100%); }
    .type-ghost { background: linear-gradient(135deg, #705898 0%, #634E83 100%); }
    .type-dragon { background: linear-gradient(135deg, #7038F8 0%, #5F2EE8 100%); }
    .type-dark { background: linear-gradient(135deg, #705848 0%, #634E3F 100%); }
    .type-steel { background: linear-gradient(135deg, #B8B8D0 0%, #A8A8C0 100%); }
    .type-fairy { background: linear-gradient(135deg, #EE99AC 0%, #E985A0 100%); }
    .type-ice { background: linear-gradient(135deg, #98D8D8 0%, #85C6C6 100%); }
    .type-normal { background: linear-gradient(135deg, #A8A878 0%, #999969 100%); }
    
    /* Enhanced Role badges */
    .enhanced-role-badge {
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.5rem 0;
        display: inline-block;
        text-align: center;
        width: 100%;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.025em;
    }
    
    .enhanced-role-badge:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    .role-physical { background: linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%); color: white; }
    .role-special { background: linear-gradient(135deg, #4ecdc4 0%, #26a69a 100%); color: white; }
    .role-tank { background: linear-gradient(135deg, #45b7d1 0%, #2196f3 100%); color: white; }
    .role-support { background: linear-gradient(135deg, #96ceb4 0%, #4caf50 100%); color: white; }
    .role-speed { background: linear-gradient(135deg, #feca57 0%, #ffc107 100%); color: white; }
    .role-trick-room { background: linear-gradient(135deg, #a55eea 0%, #9c27b0 100%); color: white; }
    .role-default { background: linear-gradient(135deg, #95a5a6 0%, #607d8b 100%); color: white; }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: var(--border-radius-sm);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        border-color: #6366f1;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: var(--border-radius-sm);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        border-color: #6366f1;
    }
    
    /* Select box styling */
    .stSelectbox > div > div > select {
        border-radius: var(--border-radius-sm);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }
    
    /* Success/warning/error alerts */
    .stSuccess {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #86efac;
        border-radius: var(--border-radius-sm);
        color: #065f46;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fcd34d;
        border-radius: var(--border-radius-sm);
        color: #92400e;
    }
    
    .stError {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #fca5a5;
        border-radius: var(--border-radius-sm);
        color: #991b1b;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 1px solid #93c5fd;
        border-radius: var(--border-radius-sm);
        color: #1e40af;
    }
    
    /* Code blocks */
    .stCode {
        background: #f8fafc;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-sm);
        font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
    }
    
    /* Metrics styling */
    .metric-container {
        background: var(--surface);
        padding: 1.5rem;
        border-radius: var(--border-radius-md);
        text-align: center;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
    }
    
    /* Divider styling */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 2rem 0;
    }
    
    /* Animation classes */
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Responsive Design - Enhanced for better split screen support */
    @media (max-width: 1200px) {
        /* Tablet and split screen improvements */
        .info-item {
            flex-wrap: wrap;
            padding: 0.9rem 1.0rem;
        }
        
        .info-label {
            min-width: 70px;
            font-size: 0.9rem;
        }
        
        .info-value {
            font-size: 0.9rem;
        }
        
        .move-item {
            flex-wrap: wrap;
            padding: 0.8rem 1.0rem;
        }
        
        .pokemon-sprite {
            width: 140px;
            height: 140px;
        }
        
        .sprite-frame {
            padding: 0.8rem;
        }
        
        .ev-code {
            font-size: 1.0rem;
            padding: 0.8rem 1.2rem;
        }
    }
    
    @media (max-width: 768px) {
        /* Mobile and narrow split screen */
        .info-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
            padding: 1.0rem;
        }
        
        .move-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
            padding: 0.9rem;
        }
        
        .section-header {
            margin: 1.0rem 0 0.8rem 0;
        }
        
        .moveset-container {
            gap: 0.7rem;
            margin-top: 1.0rem;
            margin-bottom: 1.2rem;
        }
        
        .pokemon-sprite {
            width: 120px;
            height: 120px;
        }
        
        .pokemon-name-title {
            font-size: 1.8rem !important;
        }
        
        .card-header-modern {
            padding: 2rem 1.5rem;
        }
    }
    
    @media (max-width: 600px) {
        /* Very narrow screens - stack everything vertically */
        .professional-pokemon-card {
            margin: 2rem 0;
        }
        
        .info-item, .move-item {
            padding: 0.8rem;
            border-radius: 8px;
        }
        
        .info-icon, .move-number {
            font-size: 1.0rem;
        }
        
        .section-header h4 {
            font-size: 1.0rem !important;
        }
        
        .ev-spread-display {
            font-size: 0.9rem;
        }
        
        .pokemon-sprite {
            width: 100px;
            height: 100px;
        }
        
        .sprite-frame {
            padding: 0.6rem;
        }
    }
    
    /* Split screen and narrow monitor optimizations */
    @media (max-width: 900px) and (min-width: 769px) {
        /* This targets split screen scenarios specifically */
        .info-section, .stats-section {
            padding: 1.2rem;
        }
        
        .info-item {
            padding: 0.8rem 1.0rem;
            margin-bottom: 0.8rem;
        }
        
        .info-label {
            min-width: 60px;
        }
        
        .move-item {
            padding: 0.8rem 1.0rem;
        }
        
        .ev-bars-container {
            gap: 0.8rem;
        }
        
        .ev-bar-item {
            padding: 0.6rem;
        }
        
        /* Reduce font sizes slightly for better fit */
        .pokemon-name-title {
            font-size: 1.9rem !important;
        }
        
        .section-header h4 {
            font-size: 1.0rem !important;
        }
    }
    
    .slide-up {
        animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes slideUp {
        from { transform: translateY(10px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    /* Additional CSS for new grid containers */
    .info-items-container {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
        width: 100%;
    }
    
    /* Tera badge responsive text handling */
    .tera-text {
        font-weight: 700;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
    }
    
    .role-text {
        font-weight: 700;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
    }
    
    /* EV code responsive sizing */
    .ev-code {
        font-size: clamp(0.9rem, 2.5vw, 1.1rem) !important;
        word-break: break-all;
        overflow-wrap: break-word;
    }
    
    /* Safe interaction for all hoverable elements */
    .pokemon-role-badge:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        /* Removed transform to prevent overflow */
    }
    
    .sprite-frame:hover {
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
        /* Removed transform to prevent overflow */
    }
    
    /* Container queries support check and fallback */
    @supports not (container-type: inline-size) {
        @media (max-width: 800px) {
            .pokemon-card-container {
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }
        }
    }
    
    /* ============================================= */
    /* ENHANCED DYNAMIC POKEMON CARD STYLES */
    /* ============================================= */
    
    .poke-card-enhanced {
        background: white;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        margin: 2rem 0;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .poke-card-enhanced:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 64px rgba(0,0,0,0.15);
    }
    
    .poke-card-hero {
        position: relative;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        overflow: hidden;
    }
    
    .poke-card-hero.ghost {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    }
    
    .poke-card-hero.psychic {
        background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
    }
    
    .poke-card-hero.dark {
        background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
    }
    
    .hero-background {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at top right, rgba(255,255,255,0.1), transparent);
    }
    
    .hero-content {
        position: relative;
        display: flex;
        align-items: center;
        gap: 2rem;
        z-index: 1;
    }
    
    .poke-slot-number {
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        backdrop-filter: blur(10px);
    }
    
    .poke-sprite-container {
        position: relative;
    }
    
    .poke-sprite-large {
        width: 96px;
        height: 96px;
        border-radius: 50%;
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }
    
    .poke-sprite-large:hover {
        transform: scale(1.1) rotate(5deg);
    }
    
    .sprite-glow {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.3), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .poke-sprite-container:hover .sprite-glow {
        opacity: 1;
    }
    
    .poke-name-hero {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .poke-type-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        backdrop-filter: blur(10px);
    }
    
    .type-icon {
        font-size: 1.2rem;
    }
    
    /* Enhanced Battle Stats */
    .battle-stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        padding: 2rem;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    .stat-card.prominent {
        background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
        border: 2px solid #f59e0b;
    }
    
    .stat-icon-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 3rem;
        height: 3rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        margin-bottom: 1rem;
    }
    
    .stat-icon {
        font-size: 1.5rem;
    }
    
    .stat-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--color-gray-600);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--color-gray-900);
    }
    
    .stat-accent {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }
    
    .stat-accent.golden {
        background: linear-gradient(90deg, #f59e0b, #f97316);
    }
    
    /* Enhanced Section Dividers */
    .section-divider-enhanced {
        display: flex;
        align-items: center;
        padding: 1.5rem 2rem 1rem 2rem;
        position: relative;
    }
    
    .section-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Enhanced Moves Grid */
    .moves-grid-enhanced {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        padding: 0 2rem 2rem 2rem;
    }
    
    .move-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .move-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }
    
    .move-card-1 { border-left: 4px solid #ef4444; }
    .move-card-2 { border-left: 4px solid #3b82f6; }
    .move-card-3 { border-left: 4px solid #10b981; }
    .move-card-4 { border-left: 4px solid #f59e0b; }
    
    .move-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .move-number-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    .move-name-dynamic {
        font-size: 1rem;
        font-weight: 600;
        color: var(--color-gray-900);
        display: block;
    }
    
    .move-card.empty {
        opacity: 0.5;
        background: #f8fafc;
    }
    
    .move-accent {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .move-card:hover .move-accent {
        opacity: 1;
    }
    
    /* Enhanced EV Bars */
    .ev-summary-enhanced {
        padding: 1rem 2rem;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 12px;
        margin: 0 2rem 1rem 2rem;
        border: 1px solid #0ea5e9;
    }
    
    .ev-label-text {
        font-weight: 600;
        color: #0369a1;
        margin-right: 1rem;
    }
    
    .ev-code-enhanced {
        background: white;
        color: #0c4a6e;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-family: 'Monaco', 'Menlo', monospace;
        font-weight: 600;
        border: 1px solid #0ea5e9;
    }
    
    .ev-bars-enhanced {
        padding: 0 2rem 2rem 2rem;
        display: grid;
        gap: 1rem;
    }
    
    .ev-bar-enhanced {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .ev-bar-enhanced:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }
    
    .ev-bar-enhanced.high {
        border-left: 4px solid #10b981;
    }
    
    .ev-bar-enhanced.medium {
        border-left: 4px solid #f59e0b;
    }
    
    .ev-bar-enhanced.low {
        border-left: 4px solid #6b7280;
    }
    
    .ev-bar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .ev-stat-info {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .ev-icon-enhanced {
        font-size: 1.25rem;
    }
    
    .ev-label-enhanced {
        font-weight: 600;
        color: var(--color-gray-700);
    }
    
    .ev-value-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    .ev-bar-track-enhanced {
        height: 8px;
        background: #f1f5f9;
        border-radius: 4px;
        position: relative;
        overflow: hidden;
    }
    
    .ev-bar-fill-enhanced {
        height: 100%;
        border-radius: 4px;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .ev-bar-shimmer {
        position: absolute;
        top: 0;
        left: -100%;
        height: 100%;
        width: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* Enhanced Strategy Section */
    .strategy-section-enhanced {
        background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
        border: 1px solid #f59e0b;
        border-radius: 16px;
        margin: 1rem 2rem 2rem 2rem;
        overflow: hidden;
    }
    
    .strategy-header {
        background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
        color: white;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .strategy-icon {
        font-size: 1.25rem;
    }
    
    .strategy-title {
        font-weight: 600;
        font-size: 1rem;
    }
    
    .strategy-content {
        padding: 1.5rem;
        line-height: 1.7;
        color: #92400e;
    }
    
    /* Mobile Responsive for Enhanced Cards */
    @media (max-width: 768px) {
        .poke-card-hero {
            padding: 1.5rem;
        }
        
        .hero-content {
            flex-direction: column;
            text-align: center;
            gap: 1rem;
        }
        
        .poke-sprite-large {
            width: 80px;
            height: 80px;
        }
        
        .poke-name-hero {
            font-size: 1.5rem;
        }
        
        .battle-stats-grid {
            grid-template-columns: 1fr;
            padding: 1rem;
        }
        
        .moves-grid-enhanced {
            grid-template-columns: 1fr;
            padding: 0 1rem 1rem 1rem;
        }
        
        .ev-bars-enhanced {
            padding: 0 1rem 1rem 1rem;
        }
        
        .section-divider-enhanced {
            padding: 1rem;
        }
        
        .strategy-section-enhanced {
            margin: 1rem;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
