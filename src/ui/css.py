"""
Custom CSS styling for the Pokemon VGC Analysis Platform.
Inspired by VGC Team Report design system — Sora font, rose accent, dark + light themes.
"""

import streamlit as st


# Color tokens per theme. Non-color tokens (spacing, fonts, type colors) live in :root below.
THEME_TOKENS = {
    "dark": {
        "background": "#0B0B1A",
        "foreground": "#F4F1EA",
        "surface": "#161635",
        "surface-alt": "#1F1F42",
        "bg-hover": "#2A2A55",

        "text-primary": "#F4F1EA",
        "text-secondary": "#D4D4E8",
        "text-tertiary": "#9A9AC0",

        "border": "#2A2A52",
        "border-subtle": "#222244",

        "accent": "#E11D48",
        "accent-light": "#FB7185",
        "accent-surface": "#3B1525",
        "accent-dim": "rgba(225, 29, 72, 0.15)",
        "accent-glow": "rgba(225, 29, 72, 0.35)",

        "success": "#16A34A",
        "success-dim": "rgba(22, 163, 74, 0.12)",
        "danger": "#DC2626",
        "danger-dim": "rgba(220, 38, 38, 0.12)",
        "warning": "#D97706",
        "warning-dim": "rgba(217, 119, 6, 0.12)",
        "info": "#3B82F6",
        "info-dim": "rgba(59, 130, 246, 0.12)",

        "shadow-sm": "0 1px 2px rgba(0, 0, 0, 0.15)",
        "shadow-md": "0 4px 12px rgba(0, 0, 0, 0.25)",
        "shadow-lg": "0 10px 24px rgba(0, 0, 0, 0.35)",
        "sprite-shadow": "drop-shadow(0 2px 8px rgba(0, 0, 0, 0.4))",

        "scroll-thumb": "#2A2A52",
        "scroll-thumb-hover": "#7A7AA0",
        "type-text-light": "#1A1A2E",
    },
    "light": {
        "background": "#F4F2EC",
        "foreground": "#0F1020",
        "surface": "#FFFFFF",
        "surface-alt": "#EDEBE3",
        "bg-hover": "#E4E2D8",

        "text-primary": "#0F1020",
        "text-secondary": "#3A3A52",
        "text-tertiary": "#5C5C78",

        "border": "#CFCDC2",
        "border-subtle": "#DEDCD3",

        "accent": "#E11D48",
        "accent-light": "#BE123C",
        "accent-surface": "#FCE7EC",
        "accent-dim": "rgba(225, 29, 72, 0.10)",
        "accent-glow": "rgba(225, 29, 72, 0.20)",

        "success": "#15803D",
        "success-dim": "rgba(21, 128, 61, 0.10)",
        "danger": "#B91C1C",
        "danger-dim": "rgba(185, 28, 28, 0.10)",
        "warning": "#B45309",
        "warning-dim": "rgba(180, 83, 9, 0.10)",
        "info": "#1D4ED8",
        "info-dim": "rgba(29, 78, 216, 0.10)",

        "shadow-sm": "0 1px 2px rgba(20, 20, 50, 0.06)",
        "shadow-md": "0 4px 12px rgba(20, 20, 50, 0.08)",
        "shadow-lg": "0 12px 28px rgba(20, 20, 50, 0.12)",
        "sprite-shadow": "drop-shadow(0 4px 10px rgba(20, 20, 50, 0.18))",

        "scroll-thumb": "#D6D4CB",
        "scroll-thumb-hover": "#A6A4A0",
        "type-text-light": "#FFFFFF",
    },
}


def _build_root_block(theme: str) -> str:
    """Build the :root token block for the chosen theme. Falls back to dark on unknown values."""
    tokens = THEME_TOKENS.get(theme, THEME_TOKENS["dark"])
    lines = [f"        --{k}: {v};" for k, v in tokens.items()]
    return "\n".join(lines)


def apply_custom_css():
    """Apply theme-aware CSS styling and PWA head tags."""
    theme = st.session_state.get("theme", "dark")
    if theme not in THEME_TOKENS:
        theme = "dark"

    # Theme color for browser chrome (PWA / mobile address bar)
    pwa_theme_color = "#0B0B1A" if theme == "dark" else "#F7F6F2"

    # PWA meta tags + service worker registration
    st.markdown(
        f"""
    <link rel="manifest" href="./static/manifest.json">
    <meta name="theme-color" content="{pwa_theme_color}">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="VGC Analyzer">
    <link rel="apple-touch-icon" href="./static/icon-192.svg">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <script>
    if ('serviceWorker' in navigator) {{
        navigator.serviceWorker.register('./static/sw.js').catch(()=>{{}});
    }}
    </script>
    """,
        unsafe_allow_html=True,
    )

    # First block: theme-dependent design tokens (rendered via f-string)
    st.markdown(
        f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Theme tokens — active theme: {theme} */
    :root {{
{_build_root_block(theme)}
        --border-focus: var(--accent);
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Second block: static layout/component rules (no f-string — keeps {{}} simple)
    st.markdown(
        """
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes fillBar {
        from { width: 0%; }
    }

    @keyframes popIn {
        0%   { opacity: 0; transform: scale(0.92); }
        100% { opacity: 1; transform: scale(1); }
    }

    /* ===== Theme-invariant tokens ===== */
    :root {
        --sp-1: 4px; --sp-2: 8px; --sp-3: 12px; --sp-4: 16px;
        --sp-5: 20px; --sp-6: 24px; --sp-8: 32px; --sp-10: 40px;

        --font-sans: 'Sora', system-ui, -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

        --r-sm: 6px; --r-md: 8px; --r-lg: 12px; --r-xl: 16px; --r-full: 9999px;

        --type-normal:   #A8A77A; --type-fire:     #EE8130; --type-water:    #6390F0;
        --type-grass:    #7AC74C; --type-electric: #F7D02C; --type-psychic:  #F95587;
        --type-fighting: #C22E28; --type-poison:   #A33EA1; --type-ground:   #E2BF65;
        --type-flying:   #A98FF0; --type-bug:      #A6B91A; --type-rock:     #B6A136;
        --type-ghost:    #735797; --type-dragon:   #6F35FC; --type-dark:     #705746;
        --type-steel:    #B7B7CE; --type-fairy:    #D685AD; --type-ice:      #96D9D6;

        --ev-hp: #FF5959; --ev-atk: #F5AC78; --ev-def: #FAE078;
        --ev-spa: #9DB7F5; --ev-spd: #A7DB8D; --ev-spe: #FA92B2;
    }

    /* ===== 3. BASE ===== */
    * { font-family: var(--font-sans) !important; }
    code, pre, .stCode { font-family: var(--font-mono) !important; }

    /* Force theme tokens to win over Streamlit's built-in theme.
       Without !important, Streamlit's inline styles can leave dark text
       on a light surface (or vice versa) and make text unreadable. */
    html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        background: var(--background) !important;
        color: var(--text-primary) !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Default text colour for everything Streamlit renders inside the app.
       Component-specific rules below selectively override this where needed. */
    .stApp p, .stApp span, .stApp li, .stApp label,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stCaptionContainer"],
    .stCaption {
        color: var(--text-primary);
    }

    /* Links stay accent-coloured but readable in both themes */
    .stApp a, [data-testid="stMarkdownContainer"] a {
        color: var(--accent);
        text-decoration: underline;
    }
    .stApp a:hover, [data-testid="stMarkdownContainer"] a:hover {
        color: var(--accent-light);
    }

    .main .block-container {
        max-width: 1100px;
    }

    hr {
        border: none;
        height: 1px;
        background: var(--border);
        margin: var(--sp-6) 0;
    }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--background); }
    ::-webkit-scrollbar-thumb { background: var(--scroll-thumb); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--scroll-thumb-hover); }

    /* ===== 4. STREAMLIT OVERRIDES ===== */
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }

    /* Buttons */
    .stButton > button {
        border-radius: var(--r-md);
        border: 1px solid var(--border);
        background: var(--surface);
        color: var(--text-primary);
        font-weight: 600;
        padding: var(--sp-3) var(--sp-6);
        font-size: 0.875rem;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: var(--shadow-sm);
    }

    .stButton > button:hover {
        background: var(--bg-hover);
        border-color: rgba(225, 29, 72, 0.4);
        box-shadow: var(--shadow-md);
    }

    .stButton > button:active {
        transform: scale(0.97);
    }

    .stButton > button[kind="primary"] {
        background: var(--accent);
        color: white;
        border: none;
        box-shadow: 0 2px 8px rgba(225, 29, 72, 0.3);
    }

    .stButton > button[kind="primary"]:hover {
        filter: brightness(1.1);
        box-shadow: 0 4px 16px rgba(225, 29, 72, 0.4);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    [data-baseweb="select"] > div,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
        transition: border-color 0.2s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--accent-dim) !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-tertiary) !important;
    }

    /* Selectbox dropdown menu items */
    [data-baseweb="popover"] [role="option"],
    [data-baseweb="menu"] li {
        color: var(--text-primary) !important;
        background: var(--surface) !important;
    }
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="menu"] li:hover {
        background: var(--bg-hover) !important;
    }

    /* Labels */
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stRadio label, .stFileUploader label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }

    /* Radio buttons */
    .stRadio > div { gap: var(--sp-2); }
    .stRadio > div > label {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-md) !important;
        padding: var(--sp-2) var(--sp-4) !important;
        transition: all 0.2s ease !important;
    }
    .stRadio > div > label:hover {
        border-color: rgba(225, 29, 72, 0.4) !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    .streamlit-expanderContent {
        background: var(--surface-alt) !important;
        border: 1px solid var(--border-subtle) !important;
        border-top: none !important;
        border-radius: 0 0 var(--r-md) var(--r-md) !important;
    }

    /* Status */
    .stStatus {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-lg) !important;
    }

    /* Alerts — Streamlit's defaults often have low contrast on a white surface */
    .stAlert { border-radius: var(--r-md) !important; }
    .stAlert,
    .stAlert *,
    [data-testid="stAlertContainer"],
    [data-testid="stAlertContainer"] * {
        color: var(--text-primary) !important;
    }
    [data-testid="stNotification"],
    [data-testid="stNotification"] * {
        color: var(--text-primary) !important;
    }

    /* Code */
    .stCode, pre, code {
        background: var(--surface-alt) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
    }
    .stCode *, pre *, code * { color: var(--text-primary) !important; }

    /* Download buttons */
    .stDownloadButton > button {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: var(--r-md) !important;
    }
    .stDownloadButton > button:hover {
        border-color: rgba(225, 29, 72, 0.4) !important;
        background: var(--surface-alt) !important;
    }

    /* ===== 5. SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border-subtle) !important;
        color: var(--text-primary) !important;
    }

    section[data-testid="stSidebar"] *,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: var(--text-primary);
    }

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small {
        color: var(--text-secondary) !important;
    }

    .sidebar-header {
        padding: var(--sp-5) var(--sp-4) var(--sp-4);
        border-bottom: 1px solid var(--border-subtle);
        margin: -1rem -1rem var(--sp-4) -1rem;
    }

    .sidebar-header h2 {
        font-size: 1.1rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0;
    }

    .sidebar-header p {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        margin: var(--sp-1) 0 0 0;
    }

    .sidebar-status {
        background: var(--accent-surface);
        border: 1px solid rgba(225, 29, 72, 0.25);
        border-radius: var(--r-md);
        padding: var(--sp-3) var(--sp-4);
        margin: var(--sp-3) 0;
        font-size: 0.85rem;
        color: var(--text-primary);
    }

    .sidebar-about {
        background: var(--surface-alt);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-md);
        padding: var(--sp-4);
        text-align: center;
        font-size: 0.75rem;
        color: var(--text-tertiary);
        line-height: 1.8;
    }

    .sidebar-about strong { color: var(--text-secondary); }

    /* ===== 6. PAGE HEADER ===== */
    .page-hero {
        text-align: center;
        padding: var(--sp-10) var(--sp-4) var(--sp-6);
        margin-bottom: var(--sp-8);
    }

    .page-hero .hero-content { position: relative; }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--sp-2);
        padding: var(--sp-2) var(--sp-4);
        background: var(--accent-surface);
        border: 1px solid rgba(225, 29, 72, 0.25);
        border-radius: var(--r-full);
        font-size: 0.7rem;
        font-weight: 700;
        color: var(--accent-light);
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: var(--sp-5);
    }

    .hero-badge .dot {
        width: 6px; height: 6px;
        background: var(--accent);
        border-radius: 50%;
    }

    .page-hero h1 {
        font-size: clamp(1.8rem, 4vw, 2.5rem);
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.15;
        margin: 0 0 var(--sp-3) 0;
        color: var(--text-primary);
    }

    .page-hero .hero-sub {
        font-size: 1rem;
        color: var(--text-secondary);
        margin: 0 0 var(--sp-2);
        font-weight: 400;
    }

    .page-hero .hero-status {
        font-size: 0.8rem;
        color: var(--text-tertiary);
    }

    .page-hero .scan-line { display: none; }

    .page-hero .hero-divider {
        width: 60px;
        height: 3px;
        background: var(--accent);
        margin: var(--sp-6) auto 0;
        border-radius: 2px;
    }

    /* ===== 7. SUMMARY CARD ===== */
    .summary-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-xl);
        padding: var(--sp-6) var(--sp-8);
        margin-bottom: var(--sp-6);
        animation: fadeIn 0.3s ease both;
        box-shadow: var(--shadow-sm);
    }

    .summary-card h1 {
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0 0 var(--sp-4) 0;
        letter-spacing: -0.02em;
    }

    .summary-meta {
        display: flex;
        gap: var(--sp-4);
        flex-wrap: wrap;
        color: var(--text-secondary);
        font-size: 0.85rem;
    }

    .summary-meta span {
        display: inline-flex;
        align-items: center;
        gap: var(--sp-2);
        padding: var(--sp-1) var(--sp-3);
        background: var(--surface-alt);
        border-radius: var(--r-full);
        border: 1px solid var(--border-subtle);
    }

    .summary-meta strong { color: var(--text-primary); }

    /* ===== 8. INFO BLOCKS ===== */
    .info-block {
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 3px solid var(--border);
        border-radius: var(--r-md);
        padding: var(--sp-5);
        margin-bottom: var(--sp-4);
        animation: fadeIn 0.3s ease both;
    }

    .info-block h4 {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0 0 var(--sp-3) 0;
    }

    .info-block p, .info-block div {
        font-size: 0.875rem;
        color: var(--text-primary);
        line-height: 1.65;
        margin: 0;
    }

    .info-block--info    { border-left-color: var(--info); }
    .info-block--info h4 { color: var(--info); }

    .info-block--success    { border-left-color: var(--success); }
    .info-block--success h4 { color: var(--success); }

    .info-block--danger    { border-left-color: var(--danger); }
    .info-block--danger h4 { color: var(--danger); }

    .info-block--warning    { border-left-color: var(--warning); }
    .info-block--warning h4 { color: var(--warning); }

    /* ===== 9. POKEMON CARD ===== */
    .pkmn-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-xl);
        overflow: hidden;
        margin-bottom: var(--sp-6);
        animation: popIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: var(--shadow-sm);
    }

    .pkmn-card:hover {
        border-color: rgba(225, 29, 72, 0.3);
        box-shadow: var(--shadow-md), 0 0 0 1px rgba(225, 29, 72, 0.1);
    }

    .pkmn-card__hero {
        padding: var(--sp-5) var(--sp-6);
        display: flex;
        align-items: center;
        gap: var(--sp-4);
        position: relative;
    }

    .pkmn-card__hero::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }

    .pkmn-card__slot {
        position: absolute;
        top: var(--sp-3);
        right: var(--sp-4);
        font-family: var(--font-mono) !important;
        font-size: 0.65rem;
        font-weight: 600;
        color: var(--text-tertiary);
        background: var(--surface-alt);
        padding: 2px var(--sp-2);
        border-radius: var(--r-sm);
    }

    .pkmn-card__sprite {
        width: 72px;
        height: 72px;
        object-fit: contain;
        flex-shrink: 0;
        filter: var(--sprite-shadow);
    }

    .pkmn-card__info { flex: 1; min-width: 0; }

    .pkmn-card__name {
        font-size: 1.35rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0 0 var(--sp-2) 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        letter-spacing: -0.02em;
    }

    .pkmn-card__badge {
        display: inline-flex;
        align-items: center;
        padding: 3px var(--sp-3);
        border-radius: var(--r-sm);
        font-size: 0.65rem;
        font-weight: 800;
        color: white;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }

    .pkmn-card__body {
        padding: var(--sp-5) var(--sp-6);
        border-top: 1px solid var(--border-subtle);
    }

    .pkmn-card__section-title {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-tertiary);
        margin: var(--sp-5) 0 var(--sp-3) 0;
        padding-bottom: var(--sp-2);
        border-bottom: 1px solid var(--border-subtle);
        display: flex;
        align-items: center;
        gap: var(--sp-2);
    }

    .pkmn-card__section-title::before {
        content: '';
        width: 3px; height: 12px;
        background: var(--accent);
        border-radius: 2px;
    }

    /* ===== 10. STAT ROWS ===== */
    .pkmn-stats {
        display: flex;
        flex-direction: column;
        gap: 1px;
    }

    .pkmn-stat {
        display: flex;
        align-items: center;
        gap: var(--sp-3);
        padding: var(--sp-2) var(--sp-3);
        font-size: 0.85rem;
        border-radius: var(--r-sm);
    }

    .pkmn-stat__label {
        color: var(--text-tertiary);
        font-weight: 500;
        min-width: 56px;
        flex-shrink: 0;
        font-size: 0.8rem;
    }

    .pkmn-stat__value {
        color: var(--text-primary);
        font-weight: 600;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .pkmn-stat--accent .pkmn-stat__value {
        color: var(--accent-light);
        font-weight: 700;
    }

    /* ===== 11. MOVE GRID ===== */
    .pkmn-moves {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--sp-2);
    }

    .pkmn-move {
        background: var(--surface-alt);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-sm);
        padding: var(--sp-2) var(--sp-3);
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-primary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .pkmn-move--empty {
        color: var(--text-tertiary);
        font-style: italic;
        font-weight: 400;
        border-style: dashed;
    }

    /* ===== 12. EV BARS ===== */
    .pkmn-ev-summary { margin-bottom: var(--sp-3); }

    .pkmn-ev-summary code {
        font-family: var(--font-mono) !important;
        font-size: 0.8rem;
        background: var(--surface-alt) !important;
        padding: var(--sp-2) var(--sp-3);
        border-radius: var(--r-sm);
        border: 1px solid var(--border-subtle);
        color: var(--text-primary) !important;
        font-weight: 600;
    }

    .pkmn-evs {
        display: flex;
        flex-direction: column;
        gap: var(--sp-2);
    }

    .pkmn-ev {
        display: flex;
        align-items: center;
        gap: var(--sp-3);
    }

    .pkmn-ev__label {
        font-family: var(--font-mono) !important;
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-tertiary);
        width: 28px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        flex-shrink: 0;
    }

    .pkmn-ev__track {
        flex: 1;
        height: 10px;
        background: var(--surface-alt);
        border-radius: 5px;
        overflow: hidden;
        border: 1px solid var(--border-subtle);
        position: relative;
    }

    .pkmn-ev__fill {
        height: 100%;
        border-radius: 5px;
        animation: fillBar 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25),
                    inset 0 -1px 0 rgba(0, 0, 0, 0.15);
        min-width: 2px; /* Even tiny EVs (e.g. 4) leave a visible nub */
    }

    /* Zero-EV rows: keep label + value visible but mute the empty track. */
    .pkmn-ev--zero { opacity: 0.55; }
    .pkmn-ev--zero .pkmn-ev__fill { min-width: 0; box-shadow: none; }

    .pkmn-ev__value {
        font-family: var(--font-mono) !important;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-primary);
        width: 32px;
        text-align: right;
        font-variant-numeric: tabular-nums;
        flex-shrink: 0;
    }

    .pkmn-ev-empty {
        font-size: 0.85rem;
        color: var(--text-tertiary);
        font-style: italic;
        padding: var(--sp-3) 0;
    }

    /* ===== 13. STRATEGY BLOCK ===== */
    .pkmn-strategy {
        background: var(--warning-dim);
        border: 1px solid rgba(217, 119, 6, 0.2);
        border-left: 3px solid var(--warning);
        border-radius: var(--r-md);
        padding: var(--sp-4);
        margin-top: var(--sp-4);
    }

    .pkmn-strategy h4 {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--warning);
        margin: 0 0 var(--sp-2) 0;
    }

    .pkmn-strategy p {
        font-size: 0.85rem;
        color: var(--text-primary);
        line-height: 1.65;
        margin: 0;
    }

    /* ===== 14. TEAM GRID ===== */
    .team-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--sp-3);
        margin-bottom: var(--sp-6);
    }

    .team-grid__item {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-lg);
        padding: var(--sp-4) var(--sp-3);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        animation: fadeIn 0.3s ease both;
        box-shadow: var(--shadow-sm);
    }

    .team-grid__item:hover {
        border-color: rgba(225, 29, 72, 0.3);
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }

    .team-grid__item img {
        display: block;
        margin: 0 auto var(--sp-2) auto;
        width: 80px;
        height: 80px;
        object-fit: contain;
        filter: var(--sprite-shadow);
    }

    .team-grid__item h4 {
        font-size: 0.875rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 2px 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .team-grid__item p {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        margin: 0;
    }

    /* ===== 15. TYPE COLORS ===== */
    .type-normal   { background-color: var(--type-normal); }
    .type-fire     { background-color: var(--type-fire); }
    .type-water    { background-color: var(--type-water); }
    .type-grass    { background-color: var(--type-grass); }
    .type-electric { background-color: var(--type-electric); color: #1A1A2E; }
    .type-psychic  { background-color: var(--type-psychic); }
    .type-fighting { background-color: var(--type-fighting); }
    .type-poison   { background-color: var(--type-poison); }
    .type-ground   { background-color: var(--type-ground); color: #1A1A2E; }
    .type-flying   { background-color: var(--type-flying); }
    .type-bug      { background-color: var(--type-bug); }
    .type-rock     { background-color: var(--type-rock); }
    .type-ghost    { background-color: var(--type-ghost); }
    .type-dragon   { background-color: var(--type-dragon); }
    .type-dark     { background-color: var(--type-dark); }
    .type-steel    { background-color: var(--type-steel); color: #1A1A2E; }
    .type-fairy    { background-color: var(--type-fairy); }
    .type-ice      { background-color: var(--type-ice); color: #1A1A2E; }

    /* Hero type accent bars */
    .pkmn-card__hero.type-normal::before   { background: var(--type-normal); }
    .pkmn-card__hero.type-fire::before     { background: var(--type-fire); }
    .pkmn-card__hero.type-water::before    { background: var(--type-water); }
    .pkmn-card__hero.type-grass::before    { background: var(--type-grass); }
    .pkmn-card__hero.type-electric::before { background: var(--type-electric); }
    .pkmn-card__hero.type-psychic::before  { background: var(--type-psychic); }
    .pkmn-card__hero.type-fighting::before { background: var(--type-fighting); }
    .pkmn-card__hero.type-poison::before   { background: var(--type-poison); }
    .pkmn-card__hero.type-ground::before   { background: var(--type-ground); }
    .pkmn-card__hero.type-flying::before   { background: var(--type-flying); }
    .pkmn-card__hero.type-bug::before      { background: var(--type-bug); }
    .pkmn-card__hero.type-rock::before     { background: var(--type-rock); }
    .pkmn-card__hero.type-ghost::before    { background: var(--type-ghost); }
    .pkmn-card__hero.type-dragon::before   { background: var(--type-dragon); }
    .pkmn-card__hero.type-dark::before     { background: var(--type-dark); }
    .pkmn-card__hero.type-steel::before    { background: var(--type-steel); }
    .pkmn-card__hero.type-fairy::before    { background: var(--type-fairy); }
    .pkmn-card__hero.type-ice::before      { background: var(--type-ice); }

    /* ===== 16. TEAM NAME INLINE ===== */
    .team-inline {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: var(--sp-2);
        padding: var(--sp-3) 0;
        font-size: 0.875rem;
        color: var(--text-secondary);
    }

    .team-inline__label {
        font-weight: 600;
        color: var(--text-tertiary);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .team-inline__name {
        padding: 2px var(--sp-3);
        background: var(--surface-alt);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-full);
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.8rem;
    }

    .team-inline__sep {
        color: var(--text-tertiary);
        font-size: 0.75rem;
    }

    /* ===== 17. SUCCESS BANNER ===== */
    .success-banner {
        background: var(--success-dim);
        border: 1px solid rgba(22, 163, 74, 0.25);
        border-radius: var(--r-lg);
        padding: var(--sp-4) var(--sp-5);
        display: flex;
        align-items: center;
        gap: var(--sp-4);
        margin-bottom: var(--sp-5);
    }

    .success-banner__icon { font-size: 1.25rem; }

    .success-banner__text {
        font-size: 0.875rem;
        color: var(--success);
        font-weight: 600;
    }

    .success-banner__sub {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 2px;
    }

    /* ===== 17b. ONBOARDING CARD ===== */
    .onboarding-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-xl);
        padding: var(--sp-8) var(--sp-6);
        text-align: center;
        max-width: 520px;
        margin: var(--sp-6) auto var(--sp-8);
        animation: popIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
        box-shadow: var(--shadow-md);
    }

    .onboarding-card__icon {
        font-size: 2.5rem;
        margin-bottom: var(--sp-4);
        line-height: 1;
    }

    .onboarding-card h2 {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 var(--sp-2) 0;
    }

    .onboarding-card p {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0 0 var(--sp-5) 0;
        line-height: 1.6;
    }

    .onboarding-card__steps {
        display: flex;
        gap: var(--sp-3);
        justify-content: center;
        flex-wrap: wrap;
        margin-top: var(--sp-4);
    }

    .onboarding-card__step {
        display: flex;
        align-items: center;
        gap: var(--sp-2);
        font-size: 0.8rem;
        color: var(--text-tertiary);
    }

    .onboarding-card__step .num {
        width: 20px; height: 20px;
        border-radius: 50%;
        background: var(--accent-surface);
        color: var(--accent-light);
        font-size: 0.65rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* ===== 17c. COPY BUTTON ===== */
    .copy-btn {
        display: inline-flex;
        align-items: center;
        gap: var(--sp-2);
        padding: var(--sp-3) var(--sp-5);
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-md);
        color: var(--text-primary);
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        font-family: var(--font-sans) !important;
        box-shadow: var(--shadow-sm);
    }

    .copy-btn:hover {
        border-color: rgba(225, 29, 72, 0.4);
        background: var(--surface-alt);
        box-shadow: var(--shadow-md);
    }

    .copy-btn:active { transform: scale(0.97); }

    .copy-btn.copied {
        border-color: var(--success);
        background: var(--success-dim);
        color: var(--success);
    }

    /* ===== 17d. COMPACT METRICS ===== */
    .metrics-bar {
        display: flex;
        gap: var(--sp-3);
        flex-wrap: wrap;
        margin-bottom: var(--sp-5);
    }

    .metrics-bar__item {
        display: inline-flex;
        align-items: center;
        gap: var(--sp-2);
        padding: var(--sp-2) var(--sp-4);
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-full);
        font-size: 0.8rem;
        box-shadow: var(--shadow-sm);
    }

    .metrics-bar__label {
        color: var(--text-tertiary);
        font-weight: 500;
    }

    .metrics-bar__value {
        color: var(--text-primary);
        font-weight: 700;
    }

    /* ===== 18. RESPONSIVE (mobile-first) ===== */

    /* Base: phones (<640px) */
    .main .block-container {
        padding: var(--sp-3) var(--sp-3) var(--sp-8);
        padding-bottom: calc(var(--sp-8) + env(safe-area-inset-bottom, 0px));
    }

    .pkmn-moves { grid-template-columns: 1fr 1fr; }
    .team-grid { grid-template-columns: repeat(2, 1fr); gap: var(--sp-2); }
    .pkmn-card__hero { flex-wrap: wrap; gap: var(--sp-3); }
    .pkmn-card__name { font-size: 1.1rem; }
    .pkmn-card__sprite { width: 56px; height: 56px; }
    .pkmn-card__body { padding: var(--sp-4); }
    .pkmn-card__hero { padding: var(--sp-4); }

    .page-hero { padding: var(--sp-6) var(--sp-2) var(--sp-4); margin-bottom: var(--sp-4); }
    .page-hero h1 { font-size: 1.6rem; }

    .summary-card { padding: var(--sp-4); border-radius: var(--r-lg); }
    .summary-card h1 { font-size: 1.2rem; }

    .info-block { padding: var(--sp-4); }
    .info-block p, .info-block div { font-size: 0.825rem; }

    .steps-grid { grid-template-columns: 1fr; }
    .metrics-bar { gap: var(--sp-2); }
    .metrics-bar__item { font-size: 0.75rem; padding: var(--sp-2) var(--sp-3); }
    .team-inline { font-size: 0.8rem; }
    .team-inline__name { font-size: 0.75rem; }
    .team-grid__item img { width: 56px; height: 56px; }
    .team-grid__item h4 { font-size: 0.8rem; }
    .copy-btn { width: 100%; justify-content: center; }
    .onboarding-card { padding: var(--sp-5) var(--sp-4); margin: var(--sp-4) auto; }

    /* Touch-friendly */
    .stButton > button { min-height: 44px; }
    .stTextInput > div > div > input { min-height: 44px; }
    .stRadio > div > label { min-height: 44px; display: flex; align-items: center; }
    .stDownloadButton > button { min-height: 44px; }

    /* Tablets (>=640px) */
    @media (min-width: 640px) {
        .main .block-container { padding: var(--sp-5) var(--sp-5) var(--sp-10); }
        .pkmn-moves { grid-template-columns: 1fr 1fr; }
        .team-grid { grid-template-columns: repeat(3, 1fr); gap: var(--sp-3); }
        .pkmn-card__name { font-size: 1.25rem; }
        .pkmn-card__sprite { width: 68px; height: 68px; }
        .pkmn-card__body { padding: var(--sp-5) var(--sp-6); }
        .pkmn-card__hero { padding: var(--sp-5) var(--sp-6); }
        .page-hero h1 { font-size: 2rem; }
        .summary-card { padding: var(--sp-6); }
        .summary-card h1 { font-size: 1.4rem; }
        .steps-grid { grid-template-columns: repeat(3, 1fr); }
        .team-grid__item img { width: 72px; height: 72px; }
        .copy-btn { width: auto; }
    }

    /* Desktop (>=1024px) */
    @media (min-width: 1024px) {
        .main .block-container { padding: var(--sp-6) var(--sp-6) var(--sp-10); max-width: 1100px; }
        .pkmn-card__body { padding: var(--sp-6) var(--sp-8); }
        .pkmn-card__sprite { width: 72px; height: 72px; }
        .pkmn-card__name { font-size: 1.35rem; }
        .summary-card { padding: var(--sp-8); }
        .summary-card h1 { font-size: 1.5rem; }
        .page-hero h1 { font-size: clamp(1.8rem, 4vw, 2.5rem); }
        .team-grid__item img { width: 80px; height: 80px; }
    }

    /* Animated GIF sprites */
    .pkmn-card__sprite,
    .team-grid__item img {
        image-rendering: pixelated;
        image-rendering: -moz-crisp-edges;
    }

    /* ===== 19. PAGE SECTIONS ===== */
    .page-section {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-lg);
        padding: var(--sp-5);
        margin-bottom: var(--sp-5);
        box-shadow: var(--shadow-sm);
    }

    .page-section h3 {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 var(--sp-3) 0;
        display: flex;
        align-items: center;
        gap: var(--sp-2);
    }

    .page-section h3::before {
        content: '';
        width: 3px; height: 16px;
        background: var(--accent);
        border-radius: 2px;
    }

    /* Steps grid */
    .steps-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: var(--sp-3);
    }

    .step-card {
        background: var(--surface-alt);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-md);
        padding: var(--sp-4);
        text-align: center;
        transition: all 0.2s ease;
    }

    .step-card:hover {
        border-color: rgba(225, 29, 72, 0.3);
    }

    .step-card__num {
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--accent-light);
    }

    .step-card__title {
        font-weight: 700;
        font-size: 0.875rem;
        color: var(--text-primary);
        margin: var(--sp-1) 0;
    }

    .step-card__desc {
        font-size: 0.8rem;
        color: var(--text-secondary);
        line-height: 1.45;
    }

    /* ===== 20. REDUCED MOTION ===== */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
