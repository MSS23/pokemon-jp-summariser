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
    """Render the professional main page header"""
    st.markdown(
        """
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
            <p style="color: rgba(255,255,255,0.7); margin: 0.5rem 0 0 0; 
                      font-size: 1rem;">
                ✨ Professional tool for competitive Pokemon players and analysts
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
    
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 1.5rem; border-radius: 15px; border-left: 4px solid #667eea; 
                    margin-bottom: 1.5rem;">
            <p style="margin: 0; color: #2c3e50; font-size: 16px;">
                <strong>📝 How it works:</strong> Paste a Japanese VGC article URL or copy the article text directly. 
                Our AI will instantly translate and analyze the team data for you.
            </p>
        </div>
        """,
        unsafe_allow_html=True
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
        return "url", url
    else:
        text = st.text_area(
            "📝 **Paste your article text here:**",
            height=200,
            placeholder="Copy the article content and paste it here for instant analysis...",
            help="💡 Tip: This works great if the URL method doesn't work for your article",
        )
        return "text", text


def render_pokemon_card(pokemon: Dict[str, Any], index: int):
    """
    Render individual Pokemon card with enhanced formatting

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
    
    # Enhanced card styling
    st.markdown(
        f"""
        <div class="enhanced-pokemon-card">
            <div class="card-header">
                <div class="pokemon-number">#{index + 1}</div>
                <div class="pokemon-title">
                    <h2>{name}</h2>
                    <span class="tera-badge {get_pokemon_type_class(tera_type)}">
                        ⚡ {tera_type} Tera
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main content in columns
    col1, col2, col3 = st.columns([1, 2, 2])

    with col1:
        # Pokemon sprite with larger, more prominent display
        sprite_url = get_pokemon_sprite_url(name)
        st.image(sprite_url, width=160, caption="")
        
        # Pokemon name prominently displayed
        st.markdown(
            f"""
            <div class="pokemon-name-display">
                <h3 style="text-align: center; margin: 10px 0; color: #2c3e50; font-weight: bold;">
                    {name}
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Role badge with better styling
        st.markdown(
            f"""
            <div class="enhanced-role-badge {get_role_class(role)}" style="text-align: center; margin: 10px 0;">
                🎯 {role}
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        # Core stats in a clean format
        st.markdown("**⚔️ Core Information**")
        
        info_data = {
            "🧬 Ability": ability,
            "🎒 Held Item": item, 
            "🌟 Nature": nature
        }
        
        for label, value in info_data.items():
            if value != "Not specified":
                st.markdown(f"**{label}:** {value}")
            else:
                st.markdown(f"**{label}:** *{value}*")
        
        # Moves in a better format
        st.markdown("**🎮 Moveset**")
        if moves and any(move != "Not specified" for move in moves):
            for i, move in enumerate(moves[:4], 1):
                if move and move != "Not specified":
                    st.markdown(f"**{i}.** {move}")
                else:
                    st.markdown(f"**{i}.** *Not specified*")
        else:
            st.markdown("*Moves not specified*")

    with col3:
        # EV spread with visual representation
        st.markdown("**📊 EV Investment**")
        
        if evs != "Not specified":
            st.code(evs, language=None)
            
            # Parse and visualize EV spread if possible
            if "/" in str(evs):
                try:
                    ev_values = [int(x.strip()) for x in str(evs).split("/")]
                    if len(ev_values) == 6:
                        ev_labels = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
                        for label, value in zip(ev_labels, ev_values):
                            if value > 0:
                                st.markdown(f"**{label}:** {value}")
                except:
                    pass
        else:
            st.markdown("*EV spread not specified*")
        
        # EV explanation in expander
        with st.expander("💡 EV Strategy", expanded=False):
            if ev_explanation != "No explanation provided":
                st.write(ev_explanation)
            else:
                st.write("*No strategic explanation provided*")
    
    st.divider()


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
    
    # Strategy overview in a clean card
    if overall_strategy != "Strategy not specified":
        st.markdown("### 💡 Strategic Overview")
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
                        padding: 2rem; border-radius: 15px; 
                        border-left: 5px solid #6366f1; margin: 1.5rem 0;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
                <p style="margin: 0; color: #1e293b; font-size: 1.1rem; line-height: 1.7;">
                    {overall_strategy}
                </p>
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

    # Render each Pokemon individually with full width
    for i, pokemon in enumerate(pokemon_team):
        render_pokemon_card(pokemon, i)
        
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
    """Render enhanced sidebar with organized sections and scroll functionality"""
    with st.sidebar:
        # Modern sidebar header with style
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.5rem; margin: -1rem -1rem 1.5rem -1rem; border-radius: 0 0 15px 15px;">
                <h2 style="color: white; margin: 0; text-align: center; font-size: 1.4rem;">
                    🎯 VGC Analyzer
                </h2>
                <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; text-align: center; font-size: 0.9rem;">
                    Professional Analysis Tools
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Navigation Section
        with st.expander("📊 Navigation", expanded=True):
            page = st.selectbox(
                "Choose Page:",
                [
                    "🏠 Analysis Home",
                    "📚 Saved Teams", 
                    "🔍 Team Search",
                    "⚙️ Settings",
                    "📖 Help & Guide"
                ],
                index=0,
                label_visibility="collapsed"
            )
        
        # Quick Actions Section
        with st.expander("⚡ Quick Actions", expanded=True):
            if st.button("🆕 New Analysis", use_container_width=True, type="primary"):
                st.session_state.analysis_result = None
                st.session_state.current_url = None
                st.session_state.analysis_complete = False
                st.rerun()
                
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Cache", use_container_width=True):
                    from cache_manager import cache
                    cache.clear_all()
                    st.success("Cache cleared!", icon="✅")
            with col2:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
        
        # Analysis Status (if analysis is available)
        if st.session_state.get("analysis_result"):
            with st.expander("📈 Current Analysis", expanded=True):
                result = st.session_state.analysis_result
                pokemon_count = len(result.get("pokemon_team", []))
                regulation = result.get("regulation", "Unknown")
                
                st.markdown(
                    f"""
                    <div style="background: #f0f9ff; padding: 1rem; border-radius: 8px; 
                               border-left: 4px solid #0ea5e9; margin: 0.5rem 0;">
                        <div style="font-size: 0.9rem; color: #0f172a;">
                            <strong>🏆 Team:</strong> {pokemon_count} Pokemon<br>
                            <strong>📊 Regulation:</strong> {regulation}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Team Building Resources
        with st.expander("🛠️ Team Building Tools", expanded=False):
            st.markdown(
                """
                **Essential Tools:**
                
                🎮 [Pokemon Showdown](https://play.pokemonshowdown.com/)
                *Team building & testing*
                
                📊 [Pikalytics](https://www.pikalytics.com/)
                *Usage statistics & trends*
                
                📈 [VGC Stats](https://www.trainertower.com/vgc-stats/)
                *Tournament results*
                
                🏆 [Victory Road](https://victoryroadvgc.com/)
                *Strategy guides*
                """
            )
        
        # Analysis Tools
        with st.expander("🔬 Analysis Resources", expanded=False):
            st.markdown(
                """
                **Meta Analysis:**
                
                📋 [Trainer Tower](https://www.trainertower.com/)
                *In-depth articles*
                
                🎯 [Smogon VGC](https://www.smogon.com/forums/forums/vgc/)
                *Community discussion*
                
                📺 [VGC Guide](https://www.vgcguide.com/)
                *Video content*
                
                📱 [Pokemon HOME](https://home.pokemon.com/)
                *Team management*
                """
            )
        
        # Settings & Preferences
        with st.expander("⚙️ App Settings", expanded=False):
            # Cache info
            try:
                from cache_manager import cache
                cache_stats = cache.get_stats()
                
                st.markdown("**Cache Status:**")
                st.markdown(f"📁 Files: {cache_stats['total_files']}")
                st.markdown(f"💾 Size: {cache_stats['total_size_mb']} MB")
                
                if cache_stats['total_files'] > 0:
                    if st.button("🧹 Clear Expired", use_container_width=True):
                        cleared = cache.clear_expired()
                        st.success(f"Cleared {cleared} files!")
                        
            except Exception:
                st.markdown("*Cache info unavailable*")
        
        # About & Help
        with st.expander("ℹ️ About", expanded=False):
            st.markdown(
                """
                **VGC Analysis Tool**
                
                ✨ Instant Japanese translation
                🏆 Professional team analysis
                📊 EV spread explanations
                📋 Export formats
                
                **Perfect for:**
                • Competitive players
                • Content creators  
                • Tournament prep
                • Research & analysis
                
                *Powered by Google Gemini AI*
                """
            )
        
        # Footer
        st.markdown(
            """
            <div style="margin-top: 2rem; padding: 1rem; background: #f8fafc; 
                       border-radius: 8px; text-align: center; border: 1px solid #e2e8f0;">
                <small style="color: #64748b;">
                    💼 Professional VGC Analysis<br>
                    🚀 Powered by AI Technology
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
    
    /* Enhanced Pokemon card styling */
    .enhanced-pokemon-card {
        background: var(--surface);
        border-radius: var(--border-radius-xl);
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-color);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .enhanced-pokemon-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: var(--shadow-xl);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .enhanced-pokemon-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-gradient);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        background: var(--primary-gradient);
        padding: 1.5rem;
        border-radius: var(--border-radius-md);
        color: white;
        margin: -2rem -2rem 1.5rem -2rem;
        box-shadow: var(--shadow-md);
    }
    
    .pokemon-number {
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1.1rem;
        margin-right: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .pokemon-title h2 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.025em;
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
