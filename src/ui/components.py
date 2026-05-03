"""
UI Components for Pokemon VGC Analysis application
Neon Dex design system with holographic cards and animated elements.
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
    """Render the hero header. Compact when results are showing."""
    analysis_available = bool(st.session_state.get("analysis_result"))
    history_count = len(st.session_state.get("analysis_history", []))
    if analysis_available:
        status = "Analysis ready"
    elif history_count > 0:
        status = f"{history_count} previous {'analysis' if history_count == 1 else 'analyses'} saved"
    else:
        status = "Paste a URL or article text to begin"

    # Compact header when results are displayed to save vertical space
    if analysis_available:
        st.markdown(
            f"""
            <div class="page-hero" style="padding: var(--sp-4) var(--sp-2) var(--sp-3); margin-bottom: var(--sp-3);">
                <div class="hero-content">
                    <h1 style="font-size: 1.3rem; margin-bottom: var(--sp-1);">VGC Team Analyzer</h1>
                    <p class="hero-status">{esc(status)}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="page-hero">
                <div class="hero-content">
                    <div class="hero-badge">
                        <span class="dot"></span>
                        AI-Powered Translation Engine
                    </div>
                    <h1>VGC Team Analyzer</h1>
                    <p class="hero-sub">Translate Japanese VGC articles into full team breakdowns instantly</p>
                    <p class="hero-status">{esc(status)}</p>
                </div>
                <div class="hero-divider"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_onboarding():
    """Render a friendly onboarding card when no API key is set."""
    st.markdown(
        """
        <div class="onboarding-card">
            <div class="onboarding-card__icon">&#x1F50D;</div>
            <h2>Get Started in 30 Seconds</h2>
            <p>
                This tool translates Japanese VGC articles into full English team breakdowns
                with Pokemon, EVs, moves, items, and strategic analysis.
                You just need a free Google Gemini API key.
            </p>
            <div class="onboarding-card__steps">
                <div class="onboarding-card__step">
                    <span class="num">1</span> Get a free API key
                </div>
                <div class="onboarding-card__step">
                    <span class="num">2</span> Enter it in the sidebar
                </div>
                <div class="onboarding-card__step">
                    <span class="num">3</span> Paste a URL and analyze
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "[Get your free API key from Google AI Studio](https://aistudio.google.com/app/apikey)",
    )


def render_analysis_input() -> tuple[str, str]:
    """Render input section for article analysis.

    Returns:
        Tuple of (input_type, content)
    """
    # Only show "How it Works" when no analysis has been done yet
    if not st.session_state.get("analysis_result"):
        st.markdown(
            """
            <div class="steps-grid">
                <div class="step-card">
                    <div class="step-card__num">01</div>
                    <div class="step-card__title">Input</div>
                    <div class="step-card__desc">Paste a Japanese VGC article URL or text</div>
                </div>
                <div class="step-card">
                    <div class="step-card__num">02</div>
                    <div class="step-card__title">Analyze</div>
                    <div class="step-card__desc">Gemini AI translates and extracts team data</div>
                </div>
                <div class="step-card">
                    <div class="step-card__num">03</div>
                    <div class="step-card__title">Export</div>
                    <div class="step-card__desc">Download as Pokepaste or view detailed breakdowns</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

    input_method = st.radio(
        "Input method",
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

    # Stagger animation delay based on card index
    delay = index * 0.1

    # Build the card as one continuous HTML string (no leading indentation,
    # no blank lines). Streamlit's Markdown parser ends a raw-HTML block at
    # the first blank line, which would cause everything after the first
    # `<div class="pkmn-stats">…</div>` to be printed as literal text.
    card_html = (
        f'<div class="pkmn-card" style="animation-delay: {delay}s;">'
        f'<div class="pkmn-card__hero {type_class}">'
        f'<span class="pkmn-card__slot">#{index + 1}</span>'
        f'<img src="{esc(sprite_url)}" alt="{esc(name)}" class="pkmn-card__sprite" '
        f'onerror="this.style.display=\'none\'" style="animation-delay: {delay + 0.2}s;"/>'
        f'<div class="pkmn-card__info">'
        f'<h2 class="pkmn-card__name">{esc(name)}</h2>'
        f'<span class="pkmn-card__badge {type_class}">Tera: {esc(tera_type)}</span>'
        f'</div>'
        f'</div>'
        f'<div class="pkmn-card__body">'
        f'<div class="pkmn-stats">'
        f'<div class="pkmn-stat">'
        f'<span class="pkmn-stat__label">Ability</span>'
        f'<span class="pkmn-stat__value">{esc(ability)}</span>'
        f'</div>'
        f'<div class="pkmn-stat pkmn-stat--accent">'
        f'<span class="pkmn-stat__label">Item</span>'
        f'<span class="pkmn-stat__value">{esc(item)}</span>'
        f'</div>'
        f'<div class="pkmn-stat">'
        f'<span class="pkmn-stat__label">Nature</span>'
        f'<span class="pkmn-stat__value">{esc(nature)}</span>'
        f'</div>'
        f'</div>'
        f'<div class="pkmn-card__section-title">Moves</div>'
        f'{_render_moves_html(moves)}'
        f'<div class="pkmn-card__section-title">EV Distribution</div>'
        f'{_render_ev_html(evs, delay)}'
        f'{_render_strategy_html(ev_explanation)}'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


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


def _render_ev_html(evs, base_delay: float = 0) -> str:
    """Generate HTML for animated EV bars."""
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
                for i, (label, value, color) in enumerate(zip(labels, ev_values, colors)):
                    if value > 0:
                        pct = min((value / 252) * 100, 100)
                        bar_delay = base_delay + 0.3 + (i * 0.08)
                        html += (
                            f'<div class="pkmn-ev">'
                            f'<span class="pkmn-ev__label">{label}</span>'
                            f'<div class="pkmn-ev__track">'
                            f'<div class="pkmn-ev__fill" style="width:{pct:.0f}%;background:linear-gradient(90deg,{color},{color}dd);animation-delay:{bar_delay:.2f}s;"></div>'
                            f'</div>'
                            f'<span class="pkmn-ev__value">{value}</span>'
                            f'</div>'
                        )
                html += "</div>"
        except Exception:
            pass

    return html


def _render_strategy_html(ev_explanation: str) -> str:
    """Generate HTML for strategy reasoning block."""
    if not ev_explanation or ev_explanation == "No explanation provided":
        return ""

    return (
        f'<div class="pkmn-strategy">'
        f'<h4>Strategic Reasoning</h4>'
        f'<p>{esc(ev_explanation)}</p>'
        f'</div>'
    )


def render_article_summary(analysis_result: Dict[str, Any]):
    """Render article summary with metadata and strategic analysis."""
    title = analysis_result.get("title", "VGC Team Analysis")
    author = analysis_result.get("author", "Unknown Author")
    tournament_context = analysis_result.get("tournament_context", "Not specified")
    regulation = analysis_result.get("regulation", "Not specified")

    # Summary card with glassmorphism
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

    # Team name pills
    pokemon_team = analysis_result.get("pokemon_team", [])
    if pokemon_team:
        names_html = ""
        for i, p in enumerate(pokemon_team):
            name = esc(p.get("name", "Unknown"))
            if i > 0:
                names_html += '<span class="team-inline__sep">/</span>'
            names_html += f'<span class="team-inline__name">{name}</span>'

        st.markdown(
            f"""
            <div class="team-inline">
                <span class="team-inline__label">Team</span>
                {names_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

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
    """Render compact metrics bar and quick actions."""
    team_size = len(analysis_result.get("pokemon_team", []))
    regulation = analysis_result.get("regulation", "Not specified")
    author = analysis_result.get("author", "Unknown")

    # Compact metrics bar instead of bulky cards
    st.markdown(
        f"""
        <div class="metrics-bar">
            <div class="metrics-bar__item">
                <span class="metrics-bar__label">Regulation</span>
                <span class="metrics-bar__value">{esc(regulation)}</span>
            </div>
            <div class="metrics-bar__item">
                <span class="metrics-bar__label">Team</span>
                <span class="metrics-bar__value">{team_size} Pokemon</span>
            </div>
            <div class="metrics-bar__item">
                <span class="metrics-bar__label">Author</span>
                <span class="metrics-bar__value">{esc(author)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("New Analysis", key="new_analysis_quick"):
        st.session_state.analysis_result = None
        st.session_state.current_url = None
        st.session_state.analysis_complete = False
        st.rerun()


def render_pokemon_team(pokemon_team):
    """Render the Pokemon team with sprite grid and detailed cards."""
    st.markdown(
        """
        <div class="pkmn-card__section-title" style="font-size: 0.8rem; margin-top: var(--sp-4);">
            Team Roster
        </div>
        """,
        unsafe_allow_html=True,
    )

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

    # Team sprite grid with staggered animations
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
    """Render export functionality with one-click Pokepaste copy."""
    st.markdown(
        """
        <div class="pkmn-card__section-title" style="font-size: 0.8rem;">
            Export Options
        </div>
        """,
        unsafe_allow_html=True,
    )

    pokepaste_content = create_pokepaste(
        analysis_result.get("pokemon_team", []),
        analysis_result.get("title", "VGC Team"),
    )

    # One-click copy Pokepaste button using hidden textarea for robustness
    import base64 as _b64
    encoded = _b64.b64encode(pokepaste_content.encode("utf-8")).decode("ascii")
    st.markdown(
        f"""
        <button class="copy-btn" id="copyPaste"
                onclick="
                    var t=atob('{encoded}');
                    navigator.clipboard.writeText(t).then(()=>{{
                        this.classList.add('copied');
                        this.innerHTML='&#x2714; Copied Pokepaste!';
                        setTimeout(()=>{{this.classList.remove('copied');this.innerHTML='&#x1F4CB; Copy Pokepaste to Clipboard';}}, 2000);
                    }});
                ">
            &#x1F4CB; Copy Pokepaste to Clipboard
        </button>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

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
        st.download_button(
            label="Download Pokepaste",
            data=pokepaste_content,
            file_name=f"{analysis_result.get('title', 'vgc_team')}_pokepaste.txt",
            mime="text/plain",
            help="Export team in pokepaste format",
        )

    with st.expander("View Pokepaste", expanded=False):
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
