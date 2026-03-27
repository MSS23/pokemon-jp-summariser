"""
Custom CSS styling for the Pokemon VGC Analysis Platform.
Clean dark theme with clear typography and functional Pokemon type colors.
"""

import streamlit as st


def apply_custom_css():
    """Apply clean CSS styling and PWA head tags for VGC Analysis Platform"""

    # PWA meta tags + service worker registration
    st.markdown(
        """
    <link rel="manifest" href="./static/manifest.json">
    <meta name="theme-color" content="#818cf8">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="VGC Analyzer">
    <link rel="apple-touch-icon" href="./static/icon-192.svg">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('./static/sw.js').catch(()=>{});
    }
    </script>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <style>
    /* ===== 1. FONTS & ANIMATIONS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes fillBar {
        from { width: 0%; }
    }

    /* ===== 2. DESIGN TOKENS ===== */
    :root {
        /* Surfaces */
        --bg-base: #0f1117;
        --bg-raised: #161822;
        --bg-card: #1c1e2e;
        --bg-hover: #242640;
        --bg-input: #1a1c2c;

        /* Text */
        --text-primary: #e8eaf0;
        --text-secondary: #9ba1b0;
        --text-muted: #6b7280;
        --text-accent: #818cf8;

        /* Borders */
        --border-subtle: rgba(255, 255, 255, 0.06);
        --border-default: rgba(255, 255, 255, 0.1);
        --border-focus: #818cf8;

        /* Accent */
        --accent: #818cf8;
        --accent-dim: rgba(129, 140, 248, 0.15);
        --green: #34d399;
        --green-dim: rgba(52, 211, 153, 0.12);
        --red: #f87171;
        --red-dim: rgba(248, 113, 113, 0.12);
        --amber: #fbbf24;
        --amber-dim: rgba(251, 191, 36, 0.12);
        --blue: #60a5fa;
        --blue-dim: rgba(96, 165, 250, 0.12);

        /* Spacing */
        --sp-1: 4px; --sp-2: 8px; --sp-3: 12px; --sp-4: 16px;
        --sp-5: 20px; --sp-6: 24px; --sp-8: 32px; --sp-10: 40px;

        /* Typography */
        --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

        /* Radii */
        --r-sm: 6px; --r-md: 10px; --r-lg: 14px; --r-xl: 18px; --r-full: 9999px;

        /* Shadows */
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);

        /* Pokemon Type Colors */
        --type-normal:   #a8a878; --type-fire:     #f08030; --type-water:    #6890f0;
        --type-grass:    #78c850; --type-electric: #f8d030; --type-psychic:  #f85888;
        --type-fighting: #c03028; --type-poison:   #a040a0; --type-ground:   #e0c068;
        --type-flying:   #a890f0; --type-bug:      #a8b820; --type-rock:     #b8a038;
        --type-ghost:    #705898; --type-dragon:   #7038f8; --type-dark:     #705848;
        --type-steel:    #b8b8d0; --type-fairy:    #ee99ac; --type-ice:      #98d8d8;

        /* EV stat colors */
        --ev-hp: #f87171; --ev-atk: #fbbf24; --ev-def: #60a5fa;
        --ev-spa: #a78bfa; --ev-spd: #34d399; --ev-spe: #f472b6;
    }

    /* ===== 3. BASE ===== */
    * { font-family: var(--font-sans) !important; }
    code, pre, .stCode { font-family: var(--font-mono) !important; }

    .stApp {
        background: var(--bg-base);
        color: var(--text-primary);
    }

    .main .block-container {
        max-width: 1100px;
    }

    hr {
        border: none;
        height: 1px;
        background: var(--border-default);
        margin: var(--sp-6) 0;
    }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: #3f4257; border-radius: 3px; }

    /* ===== 4. STREAMLIT OVERRIDES ===== */
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }

    /* Buttons */
    .stButton > button {
        border-radius: var(--r-md);
        border: 1px solid var(--border-default);
        background: var(--bg-card);
        color: var(--text-primary);
        font-weight: 600;
        padding: var(--sp-3) var(--sp-6);
        font-size: 0.875rem;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        background: var(--bg-hover);
        border-color: var(--border-focus);
    }

    .stButton > button[kind="primary"] {
        background: var(--accent);
        color: white;
        border: none;
    }

    .stButton > button[kind="primary"]:hover {
        background: #6366f1;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: var(--bg-input) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
        transition: border-color 0.15s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 2px var(--accent-dim) !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-muted) !important;
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
        background: var(--bg-card) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--r-md) !important;
        padding: var(--sp-2) var(--sp-4) !important;
        transition: all 0.15s ease !important;
    }
    .stRadio > div > label:hover {
        border-color: var(--border-focus) !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    .streamlit-expanderContent {
        background: var(--bg-raised) !important;
        border: 1px solid var(--border-subtle) !important;
        border-top: none !important;
        border-radius: 0 0 var(--r-md) var(--r-md) !important;
    }

    /* Status */
    .stStatus {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--r-lg) !important;
    }

    /* Alerts */
    .stAlert { border-radius: var(--r-md) !important; }

    /* Code */
    .stCode, pre {
        background: var(--bg-raised) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--r-md) !important;
    }

    /* Download buttons */
    .stDownloadButton > button {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-default) !important;
        color: var(--text-primary) !important;
        border-radius: var(--r-md) !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--green) !important;
        background: var(--green-dim) !important;
    }

    /* ===== 5. SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: var(--bg-raised) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text-secondary);
    }

    .sidebar-header {
        padding: var(--sp-5) var(--sp-4) var(--sp-4);
        border-bottom: 1px solid var(--border-subtle);
        margin: -1rem -1rem var(--sp-4) -1rem;
    }

    .sidebar-header h2 {
        font-size: 1.15rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0;
    }

    .sidebar-header p {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin: var(--sp-1) 0 0 0;
    }

    .sidebar-status {
        background: var(--accent-dim);
        border: 1px solid rgba(129, 140, 248, 0.25);
        border-radius: var(--r-md);
        padding: var(--sp-3) var(--sp-4);
        margin: var(--sp-3) 0;
        font-size: 0.85rem;
        color: var(--text-primary);
    }

    .sidebar-about {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-md);
        padding: var(--sp-4);
        text-align: center;
        font-size: 0.75rem;
        color: var(--text-muted);
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
        background: var(--accent-dim);
        border: 1px solid rgba(129, 140, 248, 0.25);
        border-radius: var(--r-full);
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-accent);
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: var(--sp-5);
    }

    .hero-badge .dot {
        width: 6px; height: 6px;
        background: var(--green);
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
        color: var(--text-muted);
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
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--r-xl);
        padding: var(--sp-6) var(--sp-8);
        margin-bottom: var(--sp-6);
        animation: fadeIn 0.3s ease both;
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
        background: var(--bg-raised);
        border-radius: var(--r-full);
        border: 1px solid var(--border-subtle);
    }

    .summary-meta strong { color: var(--text-primary); }

    /* ===== 8. INFO BLOCKS ===== */
    .info-block {
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-left: 3px solid var(--border-default);
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

    .info-block--info    { border-left-color: var(--blue); }
    .info-block--info h4 { color: var(--blue); }

    .info-block--success    { border-left-color: var(--green); }
    .info-block--success h4 { color: var(--green); }

    .info-block--danger    { border-left-color: var(--red); }
    .info-block--danger h4 { color: var(--red); }

    .info-block--warning    { border-left-color: var(--amber); }
    .info-block--warning h4 { color: var(--amber); }

    /* ===== 9. METRIC CARD ===== */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--r-lg);
        padding: var(--sp-5);
        text-align: center;
        animation: fadeIn 0.3s ease both;
    }

    .metric-card h3 {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        margin: 0 0 var(--sp-2) 0;
    }

    .metric-card p {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }

    /* ===== 10. POKEMON CARD ===== */
    .pkmn-card {
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--r-xl);
        overflow: hidden;
        margin-bottom: var(--sp-6);
        animation: fadeIn 0.3s ease both;
        transition: border-color 0.15s ease;
    }

    .pkmn-card:hover {
        border-color: rgba(129, 140, 248, 0.3);
    }

    .pkmn-card__hero {
        padding: var(--sp-5) var(--sp-6);
        display: flex;
        align-items: center;
        gap: var(--sp-4);
        position: relative;
    }

    /* Type-colored top border */
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
        color: var(--text-muted);
        background: var(--bg-raised);
        padding: 2px var(--sp-2);
        border-radius: var(--r-sm);
    }

    .pkmn-card__sprite {
        width: 72px;
        height: 72px;
        object-fit: contain;
        flex-shrink: 0;
        filter: drop-shadow(0 2px 6px rgba(0,0,0,0.3));
    }

    .pkmn-card__info {
        flex: 1;
        min-width: 0;
    }

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
        border-radius: var(--r-full);
        font-size: 0.7rem;
        font-weight: 700;
        color: white;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
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
        color: var(--text-muted);
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

    /* ===== 11. STAT ROWS ===== */
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
        color: var(--text-muted);
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
        color: var(--text-accent);
        font-weight: 700;
    }

    /* ===== 12. MOVE GRID ===== */
    .pkmn-moves {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--sp-2);
    }

    .pkmn-move {
        background: var(--bg-raised);
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
        color: var(--text-muted);
        font-style: italic;
        font-weight: 400;
        border-style: dashed;
    }

    /* ===== 13. EV BARS ===== */
    .pkmn-ev-summary { margin-bottom: var(--sp-3); }

    .pkmn-ev-summary code {
        font-family: var(--font-mono) !important;
        font-size: 0.8rem;
        background: var(--bg-raised);
        padding: var(--sp-2) var(--sp-3);
        border-radius: var(--r-sm);
        border: 1px solid var(--border-subtle);
        color: var(--text-accent);
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
        color: var(--text-muted);
        width: 28px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        flex-shrink: 0;
    }

    .pkmn-ev__track {
        flex: 1;
        height: 7px;
        background: var(--bg-raised);
        border-radius: 4px;
        overflow: hidden;
        border: 1px solid var(--border-subtle);
    }

    .pkmn-ev__fill {
        height: 100%;
        border-radius: 4px;
        animation: fillBar 0.8s ease-out both;
    }

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
        color: var(--text-muted);
        font-style: italic;
        padding: var(--sp-3) 0;
    }

    /* ===== 14. STRATEGY BLOCK ===== */
    .pkmn-strategy {
        background: var(--amber-dim);
        border: 1px solid rgba(251, 191, 36, 0.2);
        border-left: 3px solid var(--amber);
        border-radius: var(--r-md);
        padding: var(--sp-4);
        margin-top: var(--sp-4);
    }

    .pkmn-strategy h4 {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--amber);
        margin: 0 0 var(--sp-2) 0;
    }

    .pkmn-strategy p {
        font-size: 0.85rem;
        color: var(--text-primary);
        line-height: 1.65;
        margin: 0;
    }

    /* ===== 15. TEAM GRID ===== */
    .team-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--sp-3);
        margin-bottom: var(--sp-6);
    }

    .team-grid__item {
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--r-lg);
        padding: var(--sp-4) var(--sp-3);
        text-align: center;
        transition: border-color 0.15s ease;
        animation: fadeIn 0.3s ease both;
    }

    .team-grid__item:hover {
        border-color: rgba(129, 140, 248, 0.3);
    }

    .team-grid__item img {
        display: block;
        margin: 0 auto var(--sp-2) auto;
        width: 80px;
        height: 80px;
        object-fit: contain;
        filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3));
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
        color: var(--text-muted);
        margin: 0;
    }

    /* ===== 16. TYPE COLORS ===== */
    .type-normal   { background-color: var(--type-normal); }
    .type-fire     { background-color: var(--type-fire); }
    .type-water    { background-color: var(--type-water); }
    .type-grass    { background-color: var(--type-grass); }
    .type-electric { background-color: var(--type-electric); color: #1a1b25; }
    .type-psychic  { background-color: var(--type-psychic); }
    .type-fighting { background-color: var(--type-fighting); }
    .type-poison   { background-color: var(--type-poison); }
    .type-ground   { background-color: var(--type-ground); color: #1a1b25; }
    .type-flying   { background-color: var(--type-flying); }
    .type-bug      { background-color: var(--type-bug); }
    .type-rock     { background-color: var(--type-rock); }
    .type-ghost    { background-color: var(--type-ghost); }
    .type-dragon   { background-color: var(--type-dragon); }
    .type-dark     { background-color: var(--type-dark); }
    .type-steel    { background-color: var(--type-steel); color: #1a1b25; }
    .type-fairy    { background-color: var(--type-fairy); }
    .type-ice      { background-color: var(--type-ice); color: #1a1b25; }

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

    /* ===== 17. TEAM NAME INLINE ===== */
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
        color: var(--text-muted);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .team-inline__name {
        padding: 2px var(--sp-3);
        background: var(--bg-raised);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-full);
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.8rem;
    }

    .team-inline__sep {
        color: var(--text-muted);
        font-size: 0.75rem;
    }

    /* ===== 18. SUCCESS BANNER ===== */
    .success-banner {
        background: var(--green-dim);
        border: 1px solid rgba(52, 211, 153, 0.25);
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
        color: var(--green);
        font-weight: 600;
    }

    .success-banner__sub {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 2px;
    }

    /* ===== 18b. ONBOARDING CARD ===== */
    .onboarding-card {
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--r-xl);
        padding: var(--sp-8) var(--sp-6);
        text-align: center;
        max-width: 520px;
        margin: var(--sp-6) auto var(--sp-8);
        animation: fadeIn 0.4s ease both;
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
        color: var(--text-muted);
    }

    .onboarding-card__step .num {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--accent-dim);
        color: var(--text-accent);
        font-size: 0.65rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* ===== 18c. HISTORY PANEL ===== */
    .history-item {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-md);
        padding: var(--sp-3) var(--sp-4);
        margin-bottom: var(--sp-2);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .history-item:hover {
        border-color: var(--accent);
        background: var(--bg-hover);
    }

    .history-item__title {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-primary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin: 0 0 2px 0;
    }

    .history-item__meta {
        font-size: 0.7rem;
        color: var(--text-muted);
        display: flex;
        gap: var(--sp-2);
    }

    /* ===== 18d. COPY BUTTON ===== */
    .copy-wrapper {
        position: relative;
    }

    .copy-btn {
        display: inline-flex;
        align-items: center;
        gap: var(--sp-2);
        padding: var(--sp-2) var(--sp-4);
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--r-md);
        color: var(--text-primary);
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s ease;
        font-family: var(--font-sans) !important;
    }

    .copy-btn:hover {
        border-color: var(--green);
        background: var(--green-dim);
        color: var(--green);
    }

    .copy-btn.copied {
        border-color: var(--green);
        background: var(--green-dim);
        color: var(--green);
    }

    /* ===== 18e. COMPACT METRICS ===== */
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
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--r-full);
        font-size: 0.8rem;
    }

    .metrics-bar__label {
        color: var(--text-muted);
        font-weight: 500;
    }

    .metrics-bar__value {
        color: var(--text-primary);
        font-weight: 700;
    }

    /* ===== 19. RESPONSIVE (mobile-first) ===== */

    /* --- Base: phones (<640px) --- */
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

    .copy-btn { width: 100%; justify-content: center; padding: var(--sp-3) var(--sp-4); }

    .onboarding-card { padding: var(--sp-5) var(--sp-4); margin: var(--sp-4) auto; }

    /* Touch-friendly tap targets */
    .stButton > button { min-height: 44px; }
    .stTextInput > div > div > input { min-height: 44px; }
    .stRadio > div > label { min-height: 44px; display: flex; align-items: center; }
    .stDownloadButton > button { min-height: 44px; }

    /* --- Tablets (>=640px) --- */
    @media (min-width: 640px) {
        .main .block-container {
            padding: var(--sp-5) var(--sp-5) var(--sp-10);
        }

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

    /* --- Desktop (>=1024px) --- */
    @media (min-width: 1024px) {
        .main .block-container {
            padding: var(--sp-6) var(--sp-6) var(--sp-10);
            max-width: 1100px;
        }

        .pkmn-card__body { padding: var(--sp-6) var(--sp-8); }
        .pkmn-card__sprite { width: 72px; height: 72px; }
        .pkmn-card__name { font-size: 1.35rem; }

        .summary-card { padding: var(--sp-8); }
        .summary-card h1 { font-size: 1.5rem; }

        .page-hero h1 { font-size: clamp(1.8rem, 4vw, 2.5rem); }

        .team-grid__item img { width: 80px; height: 80px; }
    }

    /* --- Animated GIF sprite tweaks --- */
    .pkmn-card__sprite,
    .team-grid__item img {
        image-rendering: pixelated;        /* keep pixel art crisp */
        image-rendering: -moz-crisp-edges;
    }

    /* ===== 20. PAGE SECTIONS ===== */
    .page-section {
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--r-lg);
        padding: var(--sp-5);
        margin-bottom: var(--sp-5);
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
        background: var(--bg-raised);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-md);
        padding: var(--sp-4);
        text-align: center;
    }

    .step-card__num {
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text-accent);
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
    </style>
    """,
        unsafe_allow_html=True,
    )
