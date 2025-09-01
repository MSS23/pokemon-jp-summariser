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
    Render individual Pokemon card

    Args:
        pokemon: Pokemon data dictionary
        index: Pokemon position in team (0-5)
    """
    with st.container():
        col1, col2 = st.columns([1, 2])

        with col1:
            # Pokemon sprite
            sprite_url = get_pokemon_sprite_url(pokemon.get("name", "Unknown"))
            st.image(sprite_url, width=150)

        with col2:
            # Pokemon details
            name = pokemon.get("name", "Unknown Pokemon")
            tera_type = pokemon.get("tera_type", "Unknown")

            st.markdown(
                f"""
                <div class="pokemon-header">
                    <h3 style="margin: 0; color: #2c3e50;">{name}</h3>
                    <span class="tera-type {get_pokemon_type_class(tera_type)}">
                        ⚡ {tera_type} Tera
                    </span>
                </div>
            """,
                unsafe_allow_html=True,
            )

            # Basic info
            st.write(f"**Ability:** {pokemon.get('ability', 'Not specified')}")
            st.write(f"**Item:** {pokemon.get('held_item', 'Not specified')}")
            st.write(f"**Nature:** {pokemon.get('nature', 'Not specified')}")

            # Role
            role = pokemon.get("role", "Not specified")
            st.markdown(
                f"""
                <div class="role-badge {get_role_class(role)}">
                    🎯 {role}
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Moves section
    moves = pokemon.get("moves", [])
    st.markdown("**Moves:**")
    moves_html = format_moves_html(moves)
    st.markdown(moves_html, unsafe_allow_html=True)

    # EV spread and explanation
    evs = pokemon.get("evs", "Not specified")
    ev_explanation = pokemon.get("ev_explanation", "No explanation provided")

    with st.expander("📊 EV Details", expanded=False):
        st.write(f"**EV Spread:** {evs}")
        st.write(f"**Explanation:** {ev_explanation}")


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
    Render the Pokemon team grid

    Args:
        pokemon_team: List of Pokemon data dictionaries
    """
    st.header("👥 Team Members")

    if not pokemon_team:
        st.warning("No Pokemon team data available")
        return

    # Render Pokemon in a grid
    for i in range(0, len(pokemon_team), 2):
        cols = st.columns(2)

        with cols[0]:
            if i < len(pokemon_team):
                render_pokemon_card(pokemon_team[i], i)

        with cols[1]:
            if i + 1 < len(pokemon_team):
                render_pokemon_card(pokemon_team[i + 1], i + 1)


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
    """Render sidebar with additional tools and information"""
    with st.sidebar:
        st.header("🛠️ Tools")

        # Cache management
        st.subheader("Cache Management")
        if st.button("Clear Cache"):
            from cache_manager import cache

            cache.clear_all()
            st.success("Cache cleared!")

        # About section
        st.subheader("ℹ️ About")
        st.markdown(
            """
            This tool analyzes Japanese Pokemon VGC articles and provides:
            
            - **Team translations** with English names
            - **EV spread analysis** with strategic explanations  
            - **Team synergy** insights
            - **Export options** for sharing
            
            Perfect for studying Japanese tournament reports and team builds!
        """
        )

        # Links
        st.subheader("🔗 Useful Links")
        st.markdown(
            """
            - [Pokemon Showdown](https://pokemonshowdown.com/)
            - [Pikalytics](https://pikalytics.com/)
            - [VGC Stats](https://www.trainertower.com/vgc-stats/)
        """
        )


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
    
    /* Pokemon card styling */
    .pokemon-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .pokemon-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    /* Type badges */
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
    
    /* Role badges */
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
