"""
UI Components for Pokemon VGC Analysis application
"""

import html as _html
import streamlit as st
from typing import Dict, List, Any
from datetime import datetime
from utils import (
    get_pokemon_sprite_url,
    get_pokemon_type_class,
    create_pokepaste,
)


def esc(value: Any) -> str:
    """Escape a value for safe HTML interpolation."""
    return _html.escape(str(value)) if value is not None else ""


def render_page_header():
    """Render the main page header"""
    analysis_available = bool(st.session_state.get("analysis_result"))
    status = "Analysis ready" if analysis_available else "Ready to analyze VGC teams"

    st.markdown(
        f"""
        <div class="page-header">
            <h1>VGC Team Analyzer</h1>
            <p>Translate and analyze Japanese VGC articles</p>
            <div class="status-line">{esc(status)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis_input() -> tuple[str, str]:
    """Render input section for article analysis.

    Returns:
        Tuple of (input_type, content)
    """
    st.subheader("Analyze Content")

    with st.expander("How it works", expanded=False):
        st.markdown(
            """
**Quick Start:**
1. Choose your input method: Article URL or Article Text
2. Click "Analyze" for AI-powered translation and team analysis
3. Export results in Pokepaste format

**Tips:**
- Best sources: note.com, Japanese Pokemon blogs, tournament reports
- Shorter articles process faster and use fewer API resources
- Use the Switch Translation page for Nintendo Switch screenshots
            """
        )

    input_method = st.radio(
        "Input method:",
        ["Article URL", "Article Text"],
        horizontal=True,
    )

    if input_method == "Article URL":
        url = st.text_input(
            "Article URL",
            placeholder="https://note.com/example/article",
            help="Supported: note.com, Japanese Pokemon blogs, tournament reports",
        )

        if url and url.strip():
            if "note.com" in url or "hatenablog" in url or "pokemon" in url.lower():
                st.success("Supported VGC article URL detected")
            else:
                st.info("URL detected - we'll try to extract the content")

        return "url", url

    else:
        text = st.text_area(
            "Article text",
            height=200,
            placeholder="Paste the article content here for analysis...",
            help="Works well if the URL method doesn't support your article",
        )

        if text and text.strip():
            char_count = len(text.strip())
            if char_count > 100:
                st.success(f"{char_count:,} characters - ready for analysis")
            elif char_count > 20:
                st.info(f"{char_count} characters - add more content if needed")
            else:
                st.warning("Content seems short - consider adding more text")

        return "text", text


def render_pokemon_card(pokemon: Dict[str, Any], index: int):
    """Render a Pokemon card with stats, moves, EVs, and strategy."""
    name = pokemon.get("name", "Unknown Pokemon")
    tera_type = pokemon.get("tera_type", "Unknown")
    ability = pokemon.get("ability", "Not specified")
    item = pokemon.get("held_item", "Not specified")
    nature = pokemon.get("nature", "Not specified")
    moves = pokemon.get("moves", [])
    evs = pokemon.get("evs", "Not specified")
    ev_explanation = pokemon.get("ev_explanation", "No explanation provided")

    sprite_url = get_pokemon_sprite_url(name)
    type_class = get_pokemon_type_class(tera_type).lower()

    # Hero section with type-colored accent bar
    st.markdown(
        f"""
        <div class="pkmn-card">
            <div class="pkmn-card__hero {type_class}">
                <img src="{esc(sprite_url)}" alt="{esc(name)}" class="pkmn-card__sprite"
                     onerror="this.style.display='none'"/>
                <div class="pkmn-card__info">
                    <div class="pkmn-card__slot">#{index + 1}</div>
                    <h2 class="pkmn-card__name">{esc(name)}</h2>
                    <span class="pkmn-card__badge {type_class}">Tera: {esc(tera_type)}</span>
                </div>
            </div>
            <div class="pkmn-card__body">
                <div class="pkmn-stats">
                    <div class="pkmn-stat">
                        <span class="pkmn-stat__label">Ability</span>
                        <span class="pkmn-stat__value">{esc(ability)}</span>
                    </div>
                    <div class="pkmn-stat pkmn-stat--accent">
                        <span class="pkmn-stat__label">Item</span>
                        <span class="pkmn-stat__value">{esc(item)}</span>
                    </div>
                    <div class="pkmn-stat">
                        <span class="pkmn-stat__label">Nature</span>
                        <span class="pkmn-stat__value">{esc(nature)}</span>
                    </div>
                </div>

                <div class="pkmn-card__section-title">Moves</div>
                {_render_moves_html(moves)}

                <div class="pkmn-card__section-title">EV Distribution</div>
                {_render_ev_html(evs)}

                {_render_strategy_html(ev_explanation)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_moves_html(moves: List[str]) -> str:
    """Generate HTML for move grid."""
    moves_list = moves[:4] if moves else []
    while len(moves_list) < 4:
        moves_list.append(None)

    html = '<div class="pkmn-moves">'
    for move in moves_list:
        if move and move != "Not specified":
            html += f'<div class="pkmn-move">{esc(move)}</div>'
        else:
            html += '<div class="pkmn-move pkmn-move--empty">--</div>'
    html += "</div>"
    return html


def _render_ev_html(evs) -> str:
    """Generate HTML for EV bars."""
    if evs == "Not specified" or not evs:
        return '<div class="pkmn-ev-empty">EV spread not specified</div>'

    html = f'<div class="pkmn-ev-summary"><code>{esc(evs)}</code></div>'

    if "/" in str(evs):
        try:
            ev_values = [int(x.strip()) for x in str(evs).split("/")]
            if len(ev_values) == 6:
                labels = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
                colors = [
                    "var(--ev-hp)", "var(--ev-atk)", "var(--ev-def)",
                    "var(--ev-spa)", "var(--ev-spd)", "var(--ev-spe)",
                ]

                html += '<div class="pkmn-evs">'
                for label, value, color in zip(labels, ev_values, colors):
                    if value > 0:
                        pct = min((value / 252) * 100, 100)
                        html += f"""
                        <div class="pkmn-ev">
                            <span class="pkmn-ev__label">{label}</span>
                            <div class="pkmn-ev__track">
                                <div class="pkmn-ev__fill" style="width:{pct:.0f}%;background:{color};"></div>
                            </div>
                            <span class="pkmn-ev__value">{value}</span>
                        </div>"""
                html += "</div>"
        except Exception:
            pass

    return html


def _render_strategy_html(ev_explanation: str) -> str:
    """Generate HTML for strategy reasoning block."""
    if not ev_explanation or ev_explanation == "No explanation provided":
        return ""

    return f"""
    <div class="pkmn-strategy">
        <h4>Strategic Reasoning</h4>
        <p>{esc(ev_explanation)}</p>
    </div>"""


def render_article_summary(analysis_result: Dict[str, Any]):
    """Render article summary with metadata and strategic analysis."""
    title = analysis_result.get("title", "VGC Team Analysis")
    author = analysis_result.get("author", "Unknown Author")
    tournament_context = analysis_result.get("tournament_context", "Not specified")
    regulation = analysis_result.get("regulation", "Not specified")

    # Summary card
    tournament_html = f"<span>Tournament: <strong>{esc(tournament_context)}</strong></span>" if tournament_context != "Not specified" else ""
    st.markdown(
        f"""
        <div class="summary-card">
            <h1>{esc(title)}</h1>
            <div class="summary-meta">
                <span>Author: <strong>{esc(author)}</strong></span>
                <span>Regulation: <strong>{esc(regulation)}</strong></span>
                {tournament_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick team overview
    pokemon_team = analysis_result.get("pokemon_team", [])
    if pokemon_team:
        team_names = [esc(p.get("name", "Unknown")) for p in pokemon_team]
        st.markdown(f"**Team:** {' / '.join(team_names)} ({len(pokemon_team)} Pokemon)")

    # Strategic analysis blocks
    _placeholder_values = {
        "Team strategy analysis recovered",
        "Team strategy details not fully extracted",
        "Strategy not specified",
        "Unable to process due to type error in validation",
        "",
    }

    overall_strategy = analysis_result.get("overall_strategy", "")
    if overall_strategy and overall_strategy not in _placeholder_values:
        st.markdown(
            f"""
            <div class="info-block info-block--info">
                <h4>Overall Strategy</h4>
                <p>{esc(overall_strategy)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)

    with col1:
        team_strengths = analysis_result.get("team_strengths", "")
        _strengths_placeholders = {
            "Team strengths analysis not available",
            "Team strengths analysis not fully extracted",
            "Team strengths not specified",
            "",
        }
        if team_strengths and team_strengths not in _strengths_placeholders:
            st.markdown(
                f"""
                <div class="info-block info-block--success">
                    <h4>Strengths</h4>
                    <div>{esc(team_strengths).replace(chr(10), '<br>')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        team_weaknesses = analysis_result.get("team_weaknesses", "")
        _weakness_placeholders = {
            "Team weaknesses analysis not available",
            "Team weaknesses analysis not fully extracted",
            "Team weaknesses not specified",
            "",
        }
        if team_weaknesses and team_weaknesses not in _weakness_placeholders:
            st.markdown(
                f"""
                <div class="info-block info-block--danger">
                    <h4>Weaknesses</h4>
                    <div>{esc(team_weaknesses).replace(chr(10), '<br>')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    team_synergies = analysis_result.get("team_synergies", "")
    if team_synergies and not team_synergies.startswith("Team synergies analysis not available"):
        st.markdown(
            f"""
            <div class="info-block info-block--warning">
                <h4>Team Synergies</h4>
                <div>{esc(team_synergies).replace(chr(10), '<br>')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    meta_analysis = analysis_result.get("meta_analysis", "")
    if meta_analysis and not meta_analysis.startswith("Meta analysis not available"):
        st.markdown(
            f"""
            <div class="info-block info-block--info">
                <h4>Meta Analysis</h4>
                <div>{esc(meta_analysis).replace(chr(10), '<br>')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Full translation
    full_translation = analysis_result.get("full_translation", "")
    if full_translation and not full_translation.startswith("Full translation not available"):
        with st.expander("Full Article Translation", expanded=False):
            st.markdown(full_translation)

    st.divider()


def render_team_showcase(analysis_result: Dict[str, Any]):
    """Render team showcase with key metrics."""
    st.success("Analysis complete. Your Japanese VGC article has been translated and analyzed.")

    title = analysis_result.get("title", "VGC Team Analysis")
    regulation = analysis_result.get("regulation", "Not specified")
    team_size = len(analysis_result.get("pokemon_team", []))
    author = analysis_result.get("author", "Unknown")

    # Key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="metric-card"><h3>Regulation</h3><p>{esc(regulation)}</p></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-card"><h3>Team Size</h3><p>{team_size} Pokemon</p></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="metric-card"><h3>Author</h3><p>{esc(author)}</p></div>',
            unsafe_allow_html=True,
        )

    # Quick actions
    st.markdown("---")
    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        if st.button("New Analysis", key="new_analysis_quick"):
            st.session_state.analysis_result = None
            st.session_state.current_url = None
            st.session_state.analysis_complete = False
            st.rerun()
    with nav_col2:
        st.button("Export Team", help="Use the export options below", disabled=True)


def render_pokemon_team(pokemon_team):
    """Render the Pokemon team with sprite grid and detailed cards."""
    st.subheader("Team")

    if not pokemon_team:
        st.warning("No Pokemon team data available")
        return

    # Handle both list and dictionary inputs
    if isinstance(pokemon_team, dict):
        if "pokemon" in pokemon_team:
            team_list = pokemon_team["pokemon"]
        else:
            team_list = list(pokemon_team.values())
    else:
        team_list = pokemon_team

    # Filter valid entries
    valid_pokemon = []
    for pokemon in team_list:
        if isinstance(pokemon, dict):
            valid_pokemon.append(pokemon)
        elif isinstance(pokemon, str):
            valid_pokemon.append({"name": pokemon, "role": "Unknown"})
    team_list = valid_pokemon

    if not team_list:
        st.warning("No valid Pokemon data found in team")
        return

    # Team sprite grid
    grid_html = '<div class="team-grid">'
    for pokemon in team_list:
        name = pokemon.get("name", "Unknown")
        sprite_url = get_pokemon_sprite_url(name)
        role = pokemon.get("role", "Unknown")
        grid_html += f"""
            <div class="team-grid__item">
                <img src="{esc(sprite_url)}" alt="{esc(name)}"
                     onerror="this.style.display='none'"/>
                <h4>{esc(name)}</h4>
                <p>{esc(role)}</p>
            </div>"""
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

    st.divider()

    # Detailed cards in 2-column layout
    for i in range(0, len(team_list), 2):
        col1, col2 = st.columns([1, 1])
        with col1:
            render_pokemon_card(team_list[i], i)
        if i + 1 < len(team_list):
            with col2:
                render_pokemon_card(team_list[i + 1], i + 1)
        else:
            with col2:
                st.empty()


def render_export_section(analysis_result: Dict[str, Any]):
    """Render export functionality section."""
    st.subheader("Export")

    col1, col2 = st.columns(2)

    with col1:
        translation_content = create_translation_export(analysis_result)
        st.download_button(
            label="Download Translation",
            data=translation_content,
            file_name=f"{analysis_result.get('title', 'vgc_translation')}.txt",
            mime="text/plain",
            help="Download complete English translation as text file",
        )

    with col2:
        pokepaste_content = create_pokepaste(
            analysis_result.get("pokemon_team", []),
            analysis_result.get("title", "VGC Team"),
        )
        st.download_button(
            label="Export Pokepaste",
            data=pokepaste_content,
            file_name=f"{analysis_result.get('title', 'vgc_team')}_pokepaste.txt",
            mime="text/plain",
            help="Export team in pokepaste format",
        )

    with st.expander("Pokepaste (copy)", expanded=False):
        st.code(pokepaste_content, language=None)

    with st.expander("Raw JSON Data", expanded=False):
        st.json(analysis_result)


def create_translation_export(analysis_result: Dict[str, Any]) -> str:
    """Create formatted translation export content."""
    lines = []

    title = analysis_result.get("title", "VGC Team Analysis")
    lines.extend(["=" * 60, f"POKEMON VGC ANALYSIS: {title.upper()}", "=" * 60, ""])

    author = analysis_result.get("author", "Unknown")
    regulation = analysis_result.get("regulation", "Not specified")
    tournament = analysis_result.get("tournament_context", "Not specified")

    lines.extend([
        f"Author: {author}",
        f"Regulation: {regulation}",
        f"Tournament Context: {tournament}",
        "",
    ])

    strategy = analysis_result.get("overall_strategy", "Not specified")
    lines.extend(["OVERALL STRATEGY:", "-" * 20, strategy, ""])

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

            lines.extend([
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
            ])

    strengths = analysis_result.get("strengths", [])
    weaknesses = analysis_result.get("weaknesses", [])

    if strengths:
        lines.extend(["TEAM STRENGTHS:", "-" * 15])
        for strength in strengths:
            lines.append(f"  {strength}")
        lines.append("")

    if weaknesses:
        lines.extend(["TEAM WEAKNESSES:", "-" * 16])
        for weakness in weaknesses:
            lines.append(f"  {weakness}")
        lines.append("")

    meta_relevance = analysis_result.get("meta_relevance", "")
    if meta_relevance:
        lines.extend(["META RELEVANCE:", "-" * 15, meta_relevance, ""])

    lines.extend([
        "=" * 60,
        "Generated by Pokemon VGC Analysis Tool",
        "=" * 60,
    ])

    return "\n".join(lines)


def log_user_feedback(url: str, problem_type: str, description: str) -> bool:
    """Log user feedback to local file for developer review."""
    try:
        import json

        feedback_file = "feedback_log.txt"
        feedback_json = "feedback_data.json"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        feedback_entry = {
            "timestamp": timestamp,
            "url": url,
            "problem_type": problem_type,
            "description": description,
            "id": hash(f"{timestamp}{url}{description}") % 10000,
        }

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

        try:
            try:
                with open(feedback_json, "r", encoding="utf-8") as f:
                    feedback_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                feedback_data = {"feedback": []}

            feedback_data["feedback"].append(feedback_entry)

            with open(feedback_json, "w", encoding="utf-8") as f:
                json.dump(feedback_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        return True

    except Exception as e:
        st.error(f"Failed to log feedback: {str(e)}")
        return False


# Re-export from split modules for backward compatibility
from ui.sidebar import render_sidebar, render_image_analysis_section  # noqa: E402
from ui.css import apply_custom_css  # noqa: E402
