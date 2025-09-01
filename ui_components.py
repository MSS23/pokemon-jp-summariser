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
    """Render the main page header"""
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px; margin-bottom: 2rem;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">
            ⚔️ Pokemon VGC Analysis</h1>
            <p style="color: rgba(255,255,255,0.8);
            margin: 0.5rem 0 0 0; font-size: 1.2rem;">
                Japanese Article Analyzer & Team Showcase
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_analysis_input() -> tuple[str, str]:
    """
    Render input section for article analysis

    Returns:
        Tuple of (input_type, content) where input_type is 'url' or 'text'
    """
    st.header("📖 Article Analysis")

    input_method = st.radio("Choose input method:", ["URL", "Text"], horizontal=True)

    if input_method == "URL":
        url = st.text_input(
            "Enter Japanese VGC article URL:",
            placeholder="https://example.com/vgc-article",
            help="Enter a URL to a Japanese Pokemon VGC article or team report",
        )
        return "url", url
    else:
        text = st.text_area(
            "Paste Japanese VGC article text:",
            height=200,
            placeholder="Paste the Japanese article content here...",
            help="Paste the text content from a Japanese Pokemon VGC article",
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
        # Pokemon sprite with better sizing
        sprite_url = get_pokemon_sprite_url(name)
        st.image(sprite_url, width=120, caption=f"{name}")
        
        # Role badge
        st.markdown(
            f"""
            <div class="enhanced-role-badge {get_role_class(role)}">
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


def render_team_showcase(analysis_result: Dict[str, Any]):
    """
    Render the complete team showcase

    Args:
        analysis_result: Complete analysis result from VGC analyzer
    """
    st.header("🎯 Team Analysis")

    # Team overview
    title = analysis_result.get("title", "VGC Team Analysis")
    st.subheader(title)

    # Team metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Regulation", analysis_result.get("regulation", "Not specified"))
    with col2:
        st.metric("Pokemon Count", len(analysis_result.get("pokemon_team", [])))
    with col3:
        author = analysis_result.get("author", "Unknown")
        st.write(f"**Author:** {author}")

    # Overall strategy
    strategy = analysis_result.get("overall_strategy", "Strategy not specified")
    st.markdown("### 🎪 Overall Strategy")
    st.write(strategy)

    # Team synergy
    synergy = analysis_result.get("team_synergy", "Team synergy not specified")
    if synergy != "Team synergy not specified":
        st.markdown("### 🔗 Team Synergy")
        st.write(synergy)

    # Strengths and weaknesses
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Strengths")
        strengths = analysis_result.get("strengths", [])
        if strengths:
            for strength in strengths:
                st.write(f"• {strength}")
        else:
            st.write("No specific strengths identified")

    with col2:
        st.markdown("### ⚠️ Weaknesses")
        weaknesses = analysis_result.get("weaknesses", [])
        if weaknesses:
            for weakness in weaknesses:
                st.write(f"• {weakness}")
        else:
            st.write("No specific weaknesses identified")

    # Meta relevance
    meta_relevance = analysis_result.get("meta_relevance", "")
    if meta_relevance:
        st.markdown("### 📈 Meta Relevance")
        st.write(meta_relevance)


def render_pokemon_team(pokemon_team: List[Dict[str, Any]]):
    """
    Render the Pokemon team with enhanced formatting

    Args:
        pokemon_team: List of Pokemon data dictionaries
    """
    st.header("👥 Team Roster")

    if not pokemon_team:
        st.warning("❌ No Pokemon team data available")
        return
    
    # Team summary
    st.markdown(
        f"""
        <div class="team-summary">
            <h3>📋 Team Overview</h3>
            <p><strong>Team Size:</strong> {len(pokemon_team)} Pokemon</p>
            <p><strong>Composition:</strong> {', '.join([p.get('name', 'Unknown') for p in pokemon_team])}</p>
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
    """Render sidebar with navigation and tools"""
    with st.sidebar:
        # Navigation
        st.header("📊 Navigation")
        
        # Page selection
        page = st.selectbox(
            "Choose Page:",
            [
                "🏠 Analysis Home",
                "📚 Saved Teams", 
                "🔍 Team Search",
                "⚙️ Settings",
                "📖 Help & Guide"
            ],
            index=0
        )
        
        st.divider()
        
        # Quick Actions
        st.header("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆕 New Analysis", use_container_width=True):
                st.session_state.analysis_result = None
                st.session_state.current_url = None
                st.experimental_rerun()
        
        with col2:
            if st.button("🗑️ Clear Cache", use_container_width=True):
                from cache_manager import cache
                cache.clear_all()
                st.success("Cache cleared!")
        
        st.divider()
        
        # Sample Analysis
        st.header("📋 Sample Analysis")
        st.markdown(
            """Try analyzing this Japanese VGC article:
            
            **Sample URL:**
            `https://note.com/icho_poke/n/n8ffb464e9335`
            
            Features teams with:
            - 🛡️ Zamazenta-Crowned
            - ⚔️ Iron Valiant  
            - ⚡ Pawmot
            """
        )
        
        if st.button("📝 Use Sample URL", use_container_width=True):
            st.session_state.sample_url = "https://note.com/icho_poke/n/n8ffb464e9335"
            st.success("Sample URL loaded! Paste it in the analysis section.")
        
        st.divider()

        # About section
        st.header("ℹ️ About VGC Analyzer")
        st.markdown(
            """
            **Advanced Pokemon VGC Analysis Tool**
            
            ✨ **Features:**
            - Japanese article translation
            - EV spread optimization analysis
            - Team synergy evaluation
            - Meta relevance assessment
            - Export to Pokepaste format
            
            🎯 **Perfect for:**
            - Tournament preparation
            - Team building research
            - Meta analysis
            - Competitive study
        """
        )

        # Links
        st.header("🔗 VGC Resources")
        st.markdown(
            """
            - [Pokemon Showdown](https://pokemonshowdown.com/)
            - [Pikalytics VGC Stats](https://pikalytics.com/)
            - [Victory Road](https://victoryroadvgc.com/)
            - [Trainer Tower](https://www.trainertower.com/)
            - [VGC Stats](https://www.trainertower.com/vgc-stats/)
        """
        )
        
        return page


def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown(
        """
    <style>
    /* Main container styling */
    .main {
        padding: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        border: none;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #764ba2, #667eea);
        transform: translateY(-1px);
    }
    
    /* Enhanced Pokemon card styling */
    .enhanced-pokemon-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: 2px solid #dee2e6;
        transition: all 0.3s ease;
    }
    
    .enhanced-pokemon-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: -1.5rem -1.5rem 1rem -1.5rem;
    }
    
    .pokemon-number {
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-right: 1rem;
    }
    
    .pokemon-title h2 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .team-summary {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .team-summary h3 {
        color: #2c3e50;
        margin-top: 0;
    }
    
    .team-footer {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin-top: 2rem;
        border: 1px solid #dee2e6;
    }
    
    /* Enhanced Type and Tera badges */
    .tera-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        color: white;
        margin-left: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .tera-type {
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
    }
    
    .type-fire { background: #F08030; }
    .type-water { background: #6890F0; }
    .type-grass { background: #78C850; }
    .type-electric { background: #F8D030; }
    .type-psychic { background: #F85888; }
    .type-fighting { background: #C03028; }
    .type-poison { background: #A040A0; }
    .type-ground { background: #E0C068; }
    .type-flying { background: #A890F0; }
    .type-bug { background: #A8B820; }
    .type-rock { background: #B8A038; }
    .type-ghost { background: #705898; }
    .type-dragon { background: #7038F8; }
    .type-dark { background: #705848; }
    .type-steel { background: #B8B8D0; }
    .type-fairy { background: #EE99AC; }
    .type-ice { background: #98D8D8; }
    .type-normal { background: #A8A878; }
    
    /* Enhanced Role badges */
    .enhanced-role-badge {
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 0.5rem 0;
        display: inline-block;
        text-align: center;
        width: 100%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        transition: all 0.2s ease;
    }
    
    .enhanced-role-badge:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .role-badge {
        padding: 0.3rem 0.6rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 0.5rem 0;
        display: inline-block;
    }
    
    .role-physical { background: #ff6b6b; color: white; }
    .role-special { background: #4ecdc4; color: white; }
    .role-tank { background: #45b7d1; color: white; }
    .role-support { background: #96ceb4; color: white; }
    .role-speed { background: #feca57; color: white; }
    .role-trick-room { background: #a55eea; color: white; }
    .role-default { background: #95a5a6; color: white; }
    
    /* Move names */
    .move-name {
        background: #f8f9fa;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.9rem;
    }
    
    /* Metrics styling */
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #2c3e50;
    }
    
    /* Success/warning styling */
    .stSuccess {
        background: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    
    .stWarning {
        background: #fff3cd;
        border-color: #ffeaa7;
        color: #856404;
    }
    
    .stError {
        background: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
