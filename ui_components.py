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


def render_page_header():
    """Render the professional main page header with quick stats"""
    # Get quick stats for better UX
    saved_count = len(st.session_state.get("saved_teams", []))
    analysis_available = bool(st.session_state.get("analysis_result"))
    
    # Build stats display
    stats_items = []
    if saved_count > 0:
        stats_items.append(f"📊 {saved_count} Teams Saved")
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
        Tuple of (input_type, content) where input_type is 'url' or 'text'
    """
    st.header("🚀 Start Your Analysis")
    
    # Enhanced help section with performance tips
    help_expand = st.expander("📝 How it works & Pro Tips", expanded=False)
    with help_expand:
        st.markdown(
            """
            **🚀 Quick Start:**
            1. Paste a Japanese VGC article URL or copy the text directly
            2. Click "Analyze" for instant AI-powered translation and team analysis
            3. Teams are automatically saved for searching and future reference
            
            **💡 Pro Tips:**
            - **Best results**: Use articles from note.com, Japanese Pokemon blogs, tournament reports
            - **Speed boost**: Recently analyzed content is cached for faster loading
            - **Team building**: Use the export features to get pokepaste format for easy importing
            
            **🔍 What we analyze:**
            • Pokemon names, abilities, items, movesets
            • EV spreads with strategic explanations  
            • Team synergies and roles
            • Tournament context and author insights
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
    else:
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
    Render individual Pokemon card with professional, modern design

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
    
    # Professional card container with enhanced styling
    st.markdown(
        f"""
        <div class="professional-pokemon-card" data-pokemon="{name.lower().replace(' ', '-')}">
            <div class="card-header-modern">
                <div class="pokemon-number-badge">#{index + 1}</div>
                <div class="pokemon-title-section">
                    <h2 class="pokemon-name-title">{name}</h2>
                    <span class="tera-badge-modern {get_pokemon_type_class(tera_type)}">
                        <span class="tera-icon">⚡</span>
                        <span class="tera-text">{tera_type} Tera</span>
                    </span>
                </div>
                <div class="card-decoration"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Optimized layout with better content distribution and spacing
    sprite_col, info_col, stats_col = st.columns([1.5, 3.0, 2.5])

    with sprite_col:
        # Enhanced sprite display with proper error handling
        sprite_url = get_pokemon_sprite_url(name)
        
        st.markdown(
            f"""
            <div class="pokemon-sprite-container">
                <div class="sprite-frame">
                    <img src="{sprite_url}" alt="{name}" class="pokemon-sprite" 
                         onerror="this.src='https://via.placeholder.com/180x180/f0f0f0/999?text={name[:3]}'"/>
                </div>
                <div class="pokemon-name-label">{name}</div>
                <div class="pokemon-role-badge {get_role_class(role)}">
                    <span class="role-icon">🎯</span>
                    <span class="role-text">{role}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with info_col:
        st.markdown('<div class="info-section">', unsafe_allow_html=True)
        
        # Core information with modern styling and improved spacing
        st.markdown('<div class="section-header">#### ⚔️ Battle Ready Details</div>', unsafe_allow_html=True)
        
        # Clean single-column info display (no nested columns to prevent overlapping)
        info_items = [
            ("🧬", "Ability", ability),
            ("🎒", "Held Item", item), 
            ("🌟", "Nature", nature)
        ]
        
        # Display all items in a clean single-column layout
        for icon, label, value in info_items:
            status_class = "specified" if value != "Not specified" else "not-specified"
            info_html = f"""
            <div class="info-item {status_class}">
                <span class="info-icon">{icon}</span>
                <span class="info-label">{label}:</span>
                <span class="info-value">{value}</span>
            </div>
            """
            st.markdown(info_html, unsafe_allow_html=True)
        
        # Enhanced moveset display with better spacing
        st.markdown('<div class="section-header">#### 🎮 Combat Moveset</div>', unsafe_allow_html=True)
        
        if moves and any(move != "Not specified" for move in moves):
            moves_html = '<div class="moveset-container">'
            for i, move in enumerate(moves[:4], 1):
                if move and move != "Not specified":
                    moves_html += f'<div class="move-item"><span class="move-number">{i}</span><span class="move-name">{move}</span></div>'
                else:
                    moves_html += f'<div class="move-item empty"><span class="move-number">{i}</span><span class="move-name">Not specified</span></div>'
            moves_html += '</div>'
            st.markdown(moves_html, unsafe_allow_html=True)
        else:
            st.markdown('<div class="moveset-empty">*Moves not specified*</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    with stats_col:
        st.markdown('<div class="stats-section">', unsafe_allow_html=True)
        
        # Enhanced EV display with visual bars and better spacing
        st.markdown('<div class="section-header">#### 📊 EV Distribution</div>', unsafe_allow_html=True)
        
        if evs != "Not specified":
            # Display EV spread in code block
            st.markdown(
                f'''
                <div class="ev-spread-display">
                    <code class="ev-code">{evs}</code>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
            # Parse and create visual EV bars
            if "/" in str(evs):
                try:
                    ev_values = [int(x.strip()) for x in str(evs).split("/")]
                    if len(ev_values) == 6:
                        ev_labels = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
                        ev_icons = ["❤️", "⚔️", "🛡️", "✨", "💫", "💨"]
                        
                        ev_bars_html = '<div class="ev-bars-container">'
                        for label, icon, value in zip(ev_labels, ev_icons, ev_values):
                            if value > 0:
                                percentage = (value / 252) * 100
                                ev_bars_html += f'<div class="ev-bar-item"><div class="ev-bar-label"><span class="ev-icon">{icon}</span><span class="ev-stat">{label}</span><span class="ev-value">{value}</span></div><div class="ev-bar-track"><div class="ev-bar-fill" style="width: {percentage}%"></div></div></div>'
                        ev_bars_html += '</div>'
                        st.markdown(ev_bars_html, unsafe_allow_html=True)
                except Exception:
                    st.markdown('<div class="ev-parse-error">*EV format could not be parsed*</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ev-not-specified">*EV spread not specified*</div>', unsafe_allow_html=True)
        
        # Enhanced EV strategy explanation
        with st.expander("💡 Strategic Reasoning", expanded=False):
            if ev_explanation != "No explanation provided":
                st.markdown(f'<div class="ev-explanation">{ev_explanation}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ev-explanation empty">*No strategic explanation provided*</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Modern divider
    st.markdown('<div class="card-divider"></div>', unsafe_allow_html=True)


def render_article_summary(analysis_result: Dict[str, Any]):
    """
    Render a prominent article summary section
    
    Args:
        analysis_result: Complete analysis result from VGC analyzer
    """
    st.header("📋 Article Summary")
    
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
    
    # Key insights row
    col1, col2 = st.columns(2)
    
    with col1:
        strengths = analysis_result.get("strengths", [])
        if strengths:
            st.markdown("**🔥 Key Strengths:**")
            for strength in strengths[:3]:  # Show top 3
                st.markdown(f"• {strength}")
    
    with col2:
        weaknesses = analysis_result.get("weaknesses", [])
        if weaknesses:
            st.markdown("**⚠️ Watch Out For:**")
            for weakness in weaknesses[:3]:  # Show top 3
                st.markdown(f"• {weakness}")
    
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

    # Enhanced user experience: Quick actions and team save notification
    st.markdown("---")
    team_count = len(st.session_state.get("saved_teams", []))
    
    # Show save status and quick navigation
    col1, col2 = st.columns([2, 1])
    with col1:
        if team_count > 0:
            st.success(f"✅ **Team automatically saved!** You now have {team_count} teams in your collection.")
        else:
            st.info("💾 Team will be saved automatically for future searching.")
    
    with col2:
        if st.button("🔍 Search Similar Teams", help="Find similar teams in your collection", key="quick_search"):
            st.session_state.current_page = "🔍 Team Search"
            st.rerun()
    
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


def render_pokemon_team(pokemon_team: List[Dict[str, Any]]):
    """
    Render the Pokemon team with enhanced formatting and sprite grid

    Args:
        pokemon_team: List of Pokemon data dictionaries
    """
    st.header("🏆 Your VGC Team")

    if not pokemon_team:
        st.warning("❌ No Pokemon team data available")
        return
    
    # Team sprite grid overview
    st.subheader("📋 Team Overview")
    
    # Create sprite grid - display in rows of 3
    rows = [pokemon_team[i:i+3] for i in range(0, len(pokemon_team), 3)]
    
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
    for i in range(0, len(pokemon_team), 2):
        col1, col2 = st.columns([1, 1])
        
        # Render first Pokemon of the pair
        with col1:
            render_pokemon_card(pokemon_team[i], i)
        
        # Render second Pokemon of the pair (if it exists)
        if i + 1 < len(pokemon_team):
            with col2:
                render_pokemon_card(pokemon_team[i + 1], i + 1)
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
                "📚 Saved Teams", 
                "🔍 Team Search",
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
    """Apply modern VGCMulticalc-style CSS styling"""
    st.markdown(
        """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        --success-gradient: linear-gradient(135deg, #10b981 0%, #059669 100%);
        --surface: #ffffff;
        --surface-variant: #f8fafc;
        --on-surface: #1e293b;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.06);
        --shadow-lg: 0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05);
        --shadow-xl: 0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04);
        --border-radius-sm: 8px;
        --border-radius-md: 12px;
        --border-radius-lg: 16px;
        --border-radius-xl: 20px;
    }
    
    /* Modern typography */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Main application styling */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Main content container */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: none;
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
    
    /* Professional Pokemon Card Styling */
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
    }
    
    .professional-pokemon-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 60px rgba(99, 102, 241, 0.25);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .professional-pokemon-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
    }
    
    .card-header-modern {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .card-header-modern::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -20px;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
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
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
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
    
    .card-decoration {
        position: absolute;
        bottom: -30px;
        right: -30px;
        width: 80px;
        height: 80px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
        opacity: 0.6;
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
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--on-surface);
        margin-bottom: 0.8rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
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
        transform: translateX(4px);
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
        min-width: 80px;
    }
    
    .info-value {
        font-weight: 500;
        color: #475569;
        font-style: italic;
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
        transform: translateX(4px);
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
    
    /* Responsive Design */
    @media (max-width: 768px) {
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
    }
    
    @media (max-width: 480px) {
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
    }
    
    .slide-up {
        animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes slideUp {
        from { transform: translateY(10px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
