"""
Custom CSS styling for the Pokemon VGC Analysis Platform.
Neon Dex: Dark cyberpunk holographic design with type-colored glows and animations.
"""

import streamlit as st


def apply_custom_css():
    """Apply Neon Dex CSS styling for VGC Analysis Platform"""
    st.markdown(
        """
    <style>
    /* ===== 1. FONTS & KEYFRAMES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* --- Animations --- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(28px) scale(0.97); }
        to   { opacity: 1; transform: translateY(0) scale(1); }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }

    @keyframes shimmer {
        0%   { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes fillBar {
        from { width: 0%; }
    }

    @keyframes glow {
        0%, 100% { opacity: 0.6; }
        50%      { opacity: 1; }
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50%      { transform: scale(1.04); }
    }

    @keyframes borderGlow {
        0%, 100% { border-color: rgba(139, 92, 246, 0.3); box-shadow: 0 0 15px rgba(139, 92, 246, 0.1); }
        50%      { border-color: rgba(139, 92, 246, 0.6); box-shadow: 0 0 25px rgba(139, 92, 246, 0.2); }
    }

    @keyframes float1 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        25%      { transform: translate(12px, -18px) scale(1.05); }
        50%      { transform: translate(-8px, -30px) scale(0.95); }
        75%      { transform: translate(15px, -12px) scale(1.02); }
    }

    @keyframes float2 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33%      { transform: translate(-20px, -15px) scale(1.08); }
        66%      { transform: translate(10px, -25px) scale(0.96); }
    }

    @keyframes scanLine {
        0%   { top: -10%; }
        100% { top: 110%; }
    }

    @keyframes textReveal {
        from { opacity: 0; transform: translateY(16px); filter: blur(8px); }
        to   { opacity: 1; transform: translateY(0); filter: blur(0); }
    }

    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    @keyframes typeGlow {
        0%, 100% { filter: brightness(1) drop-shadow(0 0 4px currentColor); }
        50%      { filter: brightness(1.2) drop-shadow(0 0 8px currentColor); }
    }

    @keyframes spriteFloat {
        0%, 100% { transform: translateY(0); }
        50%      { transform: translateY(-6px); }
    }

    @keyframes barShine {
        0%   { left: -100%; }
        100% { left: 200%; }
    }

    /* ===== 2. DESIGN TOKENS ===== */
    :root {
        /* Core palette */
        --neon-purple: #8b5cf6;
        --neon-purple-dim: #7c3aed;
        --neon-blue: #3b82f6;
        --neon-cyan: #06b6d4;
        --neon-pink: #ec4899;
        --neon-green: #10b981;
        --neon-amber: #f59e0b;
        --neon-red: #ef4444;

        /* Surfaces */
        --bg-void: #08090e;
        --bg-deep: #0c0d14;
        --bg-base: #111219;
        --bg-raised: #16171f;
        --bg-card: #1a1b25;
        --bg-hover: #1f2130;
        --bg-glass: rgba(22, 23, 31, 0.7);
        --bg-glass-hover: rgba(31, 33, 48, 0.8);

        /* Text */
        --text-bright: #f1f5f9;
        --text-primary: #e2e8f0;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --text-dim: #475569;
        --text-accent: #a78bfa;

        /* Borders */
        --border-subtle: rgba(148, 163, 184, 0.08);
        --border-default: rgba(148, 163, 184, 0.12);
        --border-glow: rgba(139, 92, 246, 0.3);

        /* Spacing */
        --sp-1: 4px; --sp-2: 8px; --sp-3: 12px; --sp-4: 16px;
        --sp-5: 20px; --sp-6: 24px; --sp-8: 32px; --sp-10: 40px; --sp-12: 48px;

        /* Typography */
        --font-display: 'Outfit', system-ui, sans-serif;
        --font-body: 'DM Sans', system-ui, sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

        /* Radii */
        --r-sm: 8px; --r-md: 12px; --r-lg: 16px; --r-xl: 20px; --r-2xl: 24px; --r-full: 9999px;

        /* Shadows */
        --shadow-glow-sm: 0 0 15px rgba(139, 92, 246, 0.15);
        --shadow-glow-md: 0 0 30px rgba(139, 92, 246, 0.2);
        --shadow-glow-lg: 0 4px 40px rgba(139, 92, 246, 0.25);
        --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.4);
        --shadow-card-hover: 0 8px 40px rgba(0, 0, 0, 0.5), 0 0 30px rgba(139, 92, 246, 0.15);

        /* Pokemon Type Colors */
        --type-normal:   #a8a878; --type-fire:     #f08030; --type-water:    #6890f0;
        --type-grass:    #78c850; --type-electric: #f8d030; --type-psychic:  #f85888;
        --type-fighting: #c03028; --type-poison:   #a040a0; --type-ground:   #e0c068;
        --type-flying:   #a890f0; --type-bug:      #a8b820; --type-rock:     #b8a038;
        --type-ghost:    #705898; --type-dragon:   #7038f8; --type-dark:     #705848;
        --type-steel:    #b8b8d0; --type-fairy:    #ee99ac; --type-ice:      #98d8d8;

        /* EV stat colors */
        --ev-hp: #ef4444; --ev-atk: #f59e0b; --ev-def: #3b82f6;
        --ev-spa: #a78bfa; --ev-spd: #06b6d4; --ev-spe: #10b981;
    }

    /* ===== 3. RESET & BASE ===== */
    * { font-family: var(--font-body) !important; }
    h1, h2, h3, h4, h5, h6 { font-family: var(--font-display) !important; }
    code, pre, .stCode { font-family: var(--font-mono) !important; }

    .stApp {
        background: var(--bg-void);
        color: var(--text-primary);
    }

    /* Animated background mesh */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(ellipse 80% 60% at 10% 20%, rgba(139, 92, 246, 0.06) 0%, transparent 60%),
            radial-gradient(ellipse 60% 80% at 85% 70%, rgba(59, 130, 246, 0.05) 0%, transparent 60%),
            radial-gradient(ellipse 50% 50% at 50% 50%, rgba(236, 72, 153, 0.03) 0%, transparent 60%);
        animation: gradientShift 20s ease infinite;
        background-size: 200% 200%;
        pointer-events: none;
        z-index: 0;
    }

    .main .block-container {
        padding: var(--sp-8) var(--sp-6);
        max-width: 1200px;
        position: relative;
        z-index: 1;
    }

    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-default), transparent);
        margin: var(--sp-8) 0;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-deep); }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--neon-purple), var(--neon-blue));
        border-radius: 3px;
    }

    /* ===== 4. STREAMLIT OVERRIDES ===== */

    /* Hide default Streamlit branding */
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }

    /* Buttons */
    .stButton > button {
        font-family: var(--font-display) !important;
        border-radius: var(--r-lg);
        border: 1px solid var(--border-default);
        background: var(--bg-card);
        color: var(--text-primary);
        font-weight: 600;
        padding: var(--sp-3) var(--sp-6);
        font-size: 0.9rem;
        letter-spacing: 0.02em;
        box-shadow: var(--shadow-card);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .stButton > button:hover {
        border-color: var(--border-glow);
        box-shadow: var(--shadow-card-hover);
        transform: translateY(-1px);
    }

    .stButton > button:hover::before {
        opacity: 1;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
        color: white;
        border: none;
        box-shadow: var(--shadow-glow-sm);
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: var(--shadow-glow-lg);
        transform: translateY(-2px);
    }

    .stButton > button[kind="primary"]:active {
        transform: translateY(0);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-body) !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--neon-purple) !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15), var(--shadow-glow-sm) !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-dim) !important;
    }

    /* Labels */
    .stTextInput label, .stTextArea label, .stSelectbox label, .stRadio label,
    .stFileUploader label {
        color: var(--text-secondary) !important;
        font-family: var(--font-display) !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
    }

    /* Radio buttons */
    .stRadio > div {
        gap: var(--sp-3);
    }

    .stRadio > div > label {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--r-md) !important;
        padding: var(--sp-2) var(--sp-4) !important;
        transition: all 0.3s ease !important;
    }

    .stRadio > div > label:hover {
        border-color: var(--border-glow) !important;
        background: var(--bg-hover) !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-display) !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--border-glow) !important;
        box-shadow: var(--shadow-glow-sm) !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-raised) !important;
        border: 1px solid var(--border-subtle) !important;
        border-top: none !important;
        border-radius: 0 0 var(--r-md) var(--r-md) !important;
    }

    /* Status containers */
    .stStatus {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--r-lg) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: var(--sp-2);
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--r-md);
        color: var(--text-secondary);
        font-family: var(--font-display) !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(59, 130, 246, 0.15)) !important;
        border-color: var(--border-glow) !important;
        color: var(--text-bright) !important;
    }

    /* Alerts/Info boxes */
    .stAlert {
        border-radius: var(--r-md) !important;
        border: 1px solid var(--border-default) !important;
    }

    /* Code blocks */
    .stCode, pre {
        background: var(--bg-deep) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--r-md) !important;
    }

    /* Divider */
    .stDivider {
        border-color: var(--border-subtle) !important;
    }

    /* Download buttons */
    .stDownloadButton > button {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-default) !important;
        color: var(--text-primary) !important;
        border-radius: var(--r-lg) !important;
        transition: all 0.3s ease !important;
    }

    .stDownloadButton > button:hover {
        border-color: var(--neon-green) !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.15) !important;
    }

    /* ===== 5. SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: var(--bg-deep) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text-secondary);
    }

    .sidebar-header {
        padding: var(--sp-6) var(--sp-4) var(--sp-4);
        border-bottom: 1px solid var(--border-subtle);
        margin: -1rem -1rem var(--sp-4) -1rem;
        position: relative;
        overflow: hidden;
    }

    .sidebar-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(59, 130, 246, 0.05));
        pointer-events: none;
    }

    .sidebar-header h2 {
        font-size: 1.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -0.02em;
        position: relative;
    }

    .sidebar-header p {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin: var(--sp-1) 0 0 0;
        position: relative;
    }

    .sidebar-status {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.08));
        border: 1px solid var(--border-glow);
        border-radius: var(--r-lg);
        padding: var(--sp-4);
        margin: var(--sp-3) 0;
        font-size: 0.85rem;
        color: var(--text-primary);
        animation: fadeIn 0.5s ease;
        position: relative;
        overflow: hidden;
    }

    .sidebar-status::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.05) 0%, transparent 70%);
        animation: float1 8s ease-in-out infinite;
        pointer-events: none;
    }

    .sidebar-about {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-lg);
        padding: var(--sp-4);
        text-align: center;
        font-size: 0.75rem;
        color: var(--text-muted);
        line-height: 1.8;
    }

    .sidebar-about strong {
        color: var(--text-secondary);
    }

    /* ===== 6. PAGE HEADER — HERO ===== */
    .page-hero {
        text-align: center;
        padding: var(--sp-12) var(--sp-4) var(--sp-8);
        margin-bottom: var(--sp-10);
        position: relative;
        overflow: hidden;
    }

    /* Animated gradient orbs */
    .page-hero::before {
        content: '';
        position: absolute;
        width: 400px; height: 400px;
        top: -100px; left: -100px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%);
        border-radius: 50%;
        animation: float1 12s ease-in-out infinite;
        pointer-events: none;
    }

    .page-hero::after {
        content: '';
        position: absolute;
        width: 350px; height: 350px;
        bottom: -80px; right: -80px;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, transparent 70%);
        border-radius: 50%;
        animation: float2 10s ease-in-out infinite;
        pointer-events: none;
    }

    .page-hero .hero-content {
        position: relative;
        z-index: 1;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--sp-2);
        padding: var(--sp-2) var(--sp-4);
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.1));
        border: 1px solid var(--border-glow);
        border-radius: var(--r-full);
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-accent);
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: var(--sp-6);
        animation: fadeInUp 0.6s ease both, borderGlow 3s ease-in-out infinite;
    }

    .hero-badge .dot {
        width: 6px; height: 6px;
        background: var(--neon-green);
        border-radius: 50%;
        animation: glow 2s ease-in-out infinite;
    }

    .page-hero h1 {
        font-size: clamp(2.2rem, 5vw, 3.5rem);
        font-weight: 900;
        letter-spacing: -0.04em;
        line-height: 1.1;
        margin: 0 0 var(--sp-4) 0;
        background: linear-gradient(135deg, var(--text-bright) 0%, var(--neon-purple) 40%, var(--neon-blue) 70%, var(--neon-cyan) 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: textReveal 0.8s ease both, shimmer 6s linear infinite;
    }

    .page-hero .hero-sub {
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin: 0 0 var(--sp-3);
        animation: textReveal 0.8s ease 0.15s both;
        font-weight: 400;
    }

    .page-hero .hero-status {
        font-size: 0.8rem;
        color: var(--text-dim);
        animation: textReveal 0.8s ease 0.3s both;
    }

    /* Scan line */
    .page-hero .scan-line {
        position: absolute;
        left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.4), transparent);
        animation: scanLine 4s linear infinite;
        pointer-events: none;
        z-index: 2;
    }

    /* Bottom border glow */
    .page-hero .hero-divider {
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--neon-purple), var(--neon-blue), transparent);
        margin-top: var(--sp-8);
        opacity: 0.5;
    }

    /* ===== 7. SUMMARY CARD (glassmorphism) ===== */
    .summary-card {
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-default);
        border-radius: var(--r-2xl);
        padding: var(--sp-8);
        margin-bottom: var(--sp-8);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease both;
    }

    .summary-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--neon-purple), var(--neon-blue), var(--neon-cyan));
    }

    .summary-card::after {
        content: '';
        position: absolute;
        top: -50%; right: -20%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.06) 0%, transparent 70%);
        pointer-events: none;
    }

    .summary-card h1 {
        font-family: var(--font-display) !important;
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--text-bright);
        margin: 0 0 var(--sp-4) 0;
        letter-spacing: -0.03em;
        position: relative;
    }

    .summary-meta {
        display: flex;
        gap: var(--sp-5);
        flex-wrap: wrap;
        color: var(--text-secondary);
        font-size: 0.85rem;
        position: relative;
    }

    .summary-meta span {
        display: inline-flex;
        align-items: center;
        gap: var(--sp-2);
        padding: var(--sp-1) var(--sp-3);
        background: rgba(148, 163, 184, 0.06);
        border-radius: var(--r-full);
        border: 1px solid var(--border-subtle);
    }

    .summary-meta strong {
        color: var(--text-primary);
    }

    /* ===== 8. INFO BLOCKS ===== */
    .info-block {
        background: var(--bg-glass);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-default);
        border-left: 3px solid var(--border-default);
        border-radius: var(--r-lg);
        padding: var(--sp-5);
        margin-bottom: var(--sp-5);
        animation: fadeInUp 0.5s ease both;
        transition: all 0.3s ease;
    }

    .info-block:hover {
        border-color: var(--border-glow);
        box-shadow: var(--shadow-glow-sm);
        transform: translateY(-1px);
    }

    .info-block h4 {
        font-family: var(--font-display) !important;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0 0 var(--sp-3) 0;
    }

    .info-block p, .info-block div {
        font-size: 0.9rem;
        color: var(--text-primary);
        line-height: 1.7;
        margin: 0;
    }

    .info-block--info    { border-left-color: var(--neon-blue); }
    .info-block--info h4 { color: var(--neon-blue); }
    .info-block--info:hover { box-shadow: 0 0 20px rgba(59, 130, 246, 0.15); }

    .info-block--success    { border-left-color: var(--neon-green); }
    .info-block--success h4 { color: var(--neon-green); }
    .info-block--success:hover { box-shadow: 0 0 20px rgba(16, 185, 129, 0.15); }

    .info-block--danger    { border-left-color: var(--neon-red); }
    .info-block--danger h4 { color: var(--neon-red); }
    .info-block--danger:hover { box-shadow: 0 0 20px rgba(239, 68, 68, 0.15); }

    .info-block--warning    { border-left-color: var(--neon-amber); }
    .info-block--warning h4 { color: var(--neon-amber); }
    .info-block--warning:hover { box-shadow: 0 0 20px rgba(245, 158, 11, 0.15); }

    /* ===== 9. METRIC CARD ===== */
    .metric-card {
        background: var(--bg-glass);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-default);
        border-radius: var(--r-xl);
        padding: var(--sp-6);
        text-align: center;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.5s ease both;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: var(--border-glow);
        box-shadow: var(--shadow-glow-sm);
        transform: translateY(-2px);
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--neon-purple), var(--neon-blue));
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .metric-card:hover::before {
        opacity: 1;
    }

    .metric-card h3 {
        font-family: var(--font-display) !important;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-muted);
        margin: 0 0 var(--sp-3) 0;
    }

    .metric-card p {
        font-family: var(--font-display) !important;
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--text-bright);
        margin: 0;
    }

    /* ===== 10. POKEMON CARD — THE STAR ===== */
    .pkmn-card {
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--r-2xl);
        overflow: hidden;
        margin-bottom: var(--sp-8);
        container-type: inline-size;
        position: relative;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease both;
    }

    /* Stagger delays — set via inline style in components */
    .pkmn-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-card-hover);
        border-color: var(--border-glow);
    }

    /* Holographic shimmer overlay */
    .pkmn-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(
            135deg,
            transparent 20%,
            rgba(139, 92, 246, 0.03) 40%,
            rgba(59, 130, 246, 0.03) 60%,
            transparent 80%
        );
        background-size: 200% 200%;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .pkmn-card:hover::after {
        opacity: 1;
        animation: shimmer 3s linear infinite;
    }

    .pkmn-card__hero {
        padding: var(--sp-5) var(--sp-6);
        display: flex;
        align-items: center;
        gap: var(--sp-5);
        position: relative;
        overflow: hidden;
    }

    /* Type-colored top glow */
    .pkmn-card__hero::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }

    /* Subtle radial glow behind sprite */
    .pkmn-card__hero::after {
        content: '';
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        width: 100px; height: 100px;
        border-radius: 50%;
        background: radial-gradient(circle, var(--type-glow, rgba(139, 92, 246, 0.15)) 0%, transparent 70%);
        pointer-events: none;
        animation: glow 3s ease-in-out infinite;
    }

    .pkmn-card__slot {
        position: absolute;
        top: var(--sp-3);
        right: var(--sp-4);
        font-family: var(--font-mono) !important;
        font-size: 0.65rem;
        font-weight: 600;
        color: var(--text-dim);
        background: var(--bg-raised);
        padding: 2px var(--sp-2);
        border-radius: var(--r-sm);
        border: 1px solid var(--border-subtle);
    }

    .pkmn-card__sprite {
        width: 80px;
        height: 80px;
        object-fit: contain;
        flex-shrink: 0;
        position: relative;
        z-index: 1;
        filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3));
        animation: spriteFloat 3s ease-in-out infinite;
        transition: transform 0.3s ease;
    }

    .pkmn-card:hover .pkmn-card__sprite {
        transform: scale(1.08);
    }

    .pkmn-card__info {
        flex: 1;
        min-width: 0;
        position: relative;
        z-index: 1;
    }

    .pkmn-card__name {
        font-family: var(--font-display) !important;
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text-bright);
        margin: 0 0 var(--sp-2) 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        letter-spacing: -0.02em;
    }

    .pkmn-card__badge {
        display: inline-flex;
        align-items: center;
        gap: var(--sp-1);
        padding: 3px var(--sp-3);
        border-radius: var(--r-full);
        font-family: var(--font-display) !important;
        font-size: 0.7rem;
        font-weight: 700;
        color: white;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        animation: typeGlow 3s ease-in-out infinite;
    }

    .pkmn-card__body {
        padding: var(--sp-5) var(--sp-6);
        border-top: 1px solid var(--border-subtle);
    }

    .pkmn-card__section-title {
        font-family: var(--font-display) !important;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-dim);
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
        background: linear-gradient(180deg, var(--neon-purple), var(--neon-blue));
        border-radius: 2px;
    }

    /* ===== 11. STAT ROWS ===== */
    .pkmn-stats {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .pkmn-stat {
        display: flex;
        align-items: center;
        gap: var(--sp-3);
        padding: var(--sp-2) var(--sp-3);
        font-size: 0.85rem;
        border-radius: var(--r-sm);
        transition: background 0.2s ease;
    }

    .pkmn-stat:hover {
        background: rgba(148, 163, 184, 0.04);
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
        border-radius: var(--r-md);
        padding: var(--sp-2) var(--sp-3);
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-primary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        transition: all 0.25s ease;
        position: relative;
    }

    .pkmn-move::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 2px;
        background: var(--neon-purple);
        opacity: 0;
        transition: opacity 0.25s ease;
    }

    .pkmn-move:hover {
        border-color: var(--border-glow);
        background: var(--bg-hover);
        transform: translateX(2px);
    }

    .pkmn-move:hover::before {
        opacity: 1;
    }

    .pkmn-move--empty {
        color: var(--text-dim);
        font-style: italic;
        font-weight: 400;
        border-style: dashed;
    }

    /* ===== 13. EV BARS (animated) ===== */
    .pkmn-ev-summary {
        margin-bottom: var(--sp-3);
    }

    .pkmn-ev-summary code {
        font-family: var(--font-mono) !important;
        font-size: 0.8rem;
        background: var(--bg-raised);
        padding: var(--sp-2) var(--sp-3);
        border-radius: var(--r-md);
        border: 1px solid var(--border-subtle);
        color: var(--text-accent);
    }

    .pkmn-evs {
        display: flex;
        flex-direction: column;
        gap: var(--sp-3);
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
        height: 8px;
        background: var(--bg-raised);
        border-radius: 4px;
        overflow: hidden;
        border: 1px solid var(--border-subtle);
        position: relative;
    }

    .pkmn-ev__fill {
        height: 100%;
        border-radius: 4px;
        animation: fillBar 1.2s cubic-bezier(0.4, 0, 0.2, 1) both;
        position: relative;
        overflow: hidden;
    }

    /* Shine sweep on EV bars */
    .pkmn-ev__fill::after {
        content: '';
        position: absolute;
        top: 0; bottom: 0;
        width: 60%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
        animation: barShine 2.5s ease-in-out infinite;
        animation-delay: inherit;
    }

    .pkmn-ev__value {
        font-family: var(--font-mono) !important;
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--text-primary);
        width: 32px;
        text-align: right;
        font-variant-numeric: tabular-nums;
        flex-shrink: 0;
    }

    .pkmn-ev-empty {
        font-size: 0.85rem;
        color: var(--text-dim);
        font-style: italic;
        padding: var(--sp-3) 0;
    }

    /* ===== 14. STRATEGY BLOCK ===== */
    .pkmn-strategy {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.06), rgba(245, 158, 11, 0.02));
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-left: 3px solid var(--neon-amber);
        border-radius: var(--r-lg);
        padding: var(--sp-4);
        margin-top: var(--sp-4);
    }

    .pkmn-strategy h4 {
        font-family: var(--font-display) !important;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--neon-amber);
        margin: 0 0 var(--sp-2) 0;
    }

    .pkmn-strategy p {
        font-size: 0.85rem;
        color: var(--text-primary);
        line-height: 1.7;
        margin: 0;
    }

    /* ===== 15. TEAM GRID (sprite overview) ===== */
    .team-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--sp-4);
        margin-bottom: var(--sp-8);
    }

    .team-grid__item {
        background: var(--bg-glass);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-default);
        border-radius: var(--r-xl);
        padding: var(--sp-5) var(--sp-3);
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.5s ease both;
    }

    .team-grid__item:nth-child(1) { animation-delay: 0s; }
    .team-grid__item:nth-child(2) { animation-delay: 0.06s; }
    .team-grid__item:nth-child(3) { animation-delay: 0.12s; }
    .team-grid__item:nth-child(4) { animation-delay: 0.18s; }
    .team-grid__item:nth-child(5) { animation-delay: 0.24s; }
    .team-grid__item:nth-child(6) { animation-delay: 0.3s; }

    .team-grid__item::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--neon-purple), var(--neon-blue));
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .team-grid__item:hover {
        border-color: var(--border-glow);
        box-shadow: var(--shadow-glow-md);
        transform: translateY(-6px) scale(1.02);
    }

    .team-grid__item:hover::before {
        opacity: 1;
    }

    .team-grid__item img {
        display: block;
        margin: 0 auto var(--sp-3) auto;
        width: 88px;
        height: 88px;
        object-fit: contain;
        filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3));
        transition: transform 0.3s ease;
    }

    .team-grid__item:hover img {
        transform: scale(1.12);
    }

    .team-grid__item h4 {
        font-family: var(--font-display) !important;
        font-size: 0.9rem;
        font-weight: 700;
        color: var(--text-bright);
        margin: 0 0 var(--sp-1) 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .team-grid__item p {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin: 0;
    }

    /* ===== 16. TYPE COLOR CLASSES ===== */
    .type-normal   { background-color: var(--type-normal); --type-glow: rgba(168, 168, 120, 0.2); }
    .type-fire     { background-color: var(--type-fire); --type-glow: rgba(240, 128, 48, 0.25); }
    .type-water    { background-color: var(--type-water); --type-glow: rgba(104, 144, 240, 0.25); }
    .type-grass    { background-color: var(--type-grass); --type-glow: rgba(120, 200, 80, 0.25); }
    .type-electric { background-color: var(--type-electric); color: #1a1b25; --type-glow: rgba(248, 208, 48, 0.25); }
    .type-psychic  { background-color: var(--type-psychic); --type-glow: rgba(248, 88, 136, 0.25); }
    .type-fighting { background-color: var(--type-fighting); --type-glow: rgba(192, 48, 40, 0.25); }
    .type-poison   { background-color: var(--type-poison); --type-glow: rgba(160, 64, 160, 0.25); }
    .type-ground   { background-color: var(--type-ground); color: #1a1b25; --type-glow: rgba(224, 192, 104, 0.25); }
    .type-flying   { background-color: var(--type-flying); --type-glow: rgba(168, 144, 240, 0.25); }
    .type-bug      { background-color: var(--type-bug); --type-glow: rgba(168, 184, 32, 0.2); }
    .type-rock     { background-color: var(--type-rock); --type-glow: rgba(184, 160, 56, 0.2); }
    .type-ghost    { background-color: var(--type-ghost); --type-glow: rgba(112, 88, 152, 0.25); }
    .type-dragon   { background-color: var(--type-dragon); --type-glow: rgba(112, 56, 248, 0.3); }
    .type-dark     { background-color: var(--type-dark); --type-glow: rgba(112, 88, 72, 0.2); }
    .type-steel    { background-color: var(--type-steel); color: #1a1b25; --type-glow: rgba(184, 184, 208, 0.2); }
    .type-fairy    { background-color: var(--type-fairy); --type-glow: rgba(238, 153, 172, 0.25); }
    .type-ice      { background-color: var(--type-ice); color: #1a1b25; --type-glow: rgba(152, 216, 216, 0.25); }

    /* Hero accent bar picks up type color */
    .pkmn-card__hero.type-normal::before   { background: var(--type-normal); }
    .pkmn-card__hero.type-fire::before     { background: linear-gradient(90deg, var(--type-fire), #ff6b35); }
    .pkmn-card__hero.type-water::before    { background: linear-gradient(90deg, var(--type-water), #60a5fa); }
    .pkmn-card__hero.type-grass::before    { background: linear-gradient(90deg, var(--type-grass), #4ade80); }
    .pkmn-card__hero.type-electric::before { background: linear-gradient(90deg, var(--type-electric), #fbbf24); }
    .pkmn-card__hero.type-psychic::before  { background: linear-gradient(90deg, var(--type-psychic), #f472b6); }
    .pkmn-card__hero.type-fighting::before { background: linear-gradient(90deg, var(--type-fighting), #ef4444); }
    .pkmn-card__hero.type-poison::before   { background: linear-gradient(90deg, var(--type-poison), #c084fc); }
    .pkmn-card__hero.type-ground::before   { background: linear-gradient(90deg, var(--type-ground), #fbbf24); }
    .pkmn-card__hero.type-flying::before   { background: linear-gradient(90deg, var(--type-flying), #a78bfa); }
    .pkmn-card__hero.type-bug::before      { background: linear-gradient(90deg, var(--type-bug), #84cc16); }
    .pkmn-card__hero.type-rock::before     { background: linear-gradient(90deg, var(--type-rock), #d97706); }
    .pkmn-card__hero.type-ghost::before    { background: linear-gradient(90deg, var(--type-ghost), #8b5cf6); }
    .pkmn-card__hero.type-dragon::before   { background: linear-gradient(90deg, var(--type-dragon), #6366f1); }
    .pkmn-card__hero.type-dark::before     { background: linear-gradient(90deg, var(--type-dark), #78716c); }
    .pkmn-card__hero.type-steel::before    { background: linear-gradient(90deg, var(--type-steel), #a8a29e); }
    .pkmn-card__hero.type-fairy::before    { background: linear-gradient(90deg, var(--type-fairy), #f9a8d4); }
    .pkmn-card__hero.type-ice::before      { background: linear-gradient(90deg, var(--type-ice), #67e8f9); }

    /* Card glow on hover matches type */
    .pkmn-card:has(.pkmn-card__hero.type-fire):hover     { box-shadow: 0 0 30px rgba(240, 128, 48, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-water):hover    { box-shadow: 0 0 30px rgba(104, 144, 240, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-grass):hover    { box-shadow: 0 0 30px rgba(120, 200, 80, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-electric):hover { box-shadow: 0 0 30px rgba(248, 208, 48, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-psychic):hover  { box-shadow: 0 0 30px rgba(248, 88, 136, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-dragon):hover   { box-shadow: 0 0 30px rgba(112, 56, 248, 0.2); }
    .pkmn-card:has(.pkmn-card__hero.type-ghost):hover    { box-shadow: 0 0 30px rgba(112, 88, 152, 0.2); }
    .pkmn-card:has(.pkmn-card__hero.type-fairy):hover    { box-shadow: 0 0 30px rgba(238, 153, 172, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-ice):hover      { box-shadow: 0 0 30px rgba(152, 216, 216, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-fighting):hover { box-shadow: 0 0 30px rgba(192, 48, 40, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-poison):hover   { box-shadow: 0 0 30px rgba(160, 64, 160, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-dark):hover     { box-shadow: 0 0 30px rgba(112, 88, 72, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-steel):hover    { box-shadow: 0 0 30px rgba(184, 184, 208, 0.12); }
    .pkmn-card:has(.pkmn-card__hero.type-ground):hover   { box-shadow: 0 0 30px rgba(224, 192, 104, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-flying):hover   { box-shadow: 0 0 30px rgba(168, 144, 240, 0.15); }
    .pkmn-card:has(.pkmn-card__hero.type-bug):hover      { box-shadow: 0 0 30px rgba(168, 184, 32, 0.12); }
    .pkmn-card:has(.pkmn-card__hero.type-rock):hover     { box-shadow: 0 0 30px rgba(184, 160, 56, 0.12); }
    .pkmn-card:has(.pkmn-card__hero.type-normal):hover   { box-shadow: 0 0 30px rgba(168, 168, 120, 0.12); }

    /* ===== 17. TEAM NAME INLINE ===== */
    .team-inline {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: var(--sp-2);
        padding: var(--sp-3) 0;
        font-size: 0.9rem;
        color: var(--text-secondary);
        animation: fadeIn 0.5s ease both;
    }

    .team-inline__label {
        font-weight: 600;
        color: var(--text-muted);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .team-inline__name {
        padding: 2px var(--sp-3);
        background: var(--bg-raised);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-full);
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.8rem;
        transition: all 0.2s ease;
    }

    .team-inline__name:hover {
        border-color: var(--border-glow);
        background: var(--bg-hover);
    }

    .team-inline__sep {
        color: var(--text-dim);
        font-size: 0.75rem;
    }

    /* ===== 18. SUCCESS BANNER ===== */
    .success-banner {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(59, 130, 246, 0.05));
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: var(--r-xl);
        padding: var(--sp-5) var(--sp-6);
        display: flex;
        align-items: center;
        gap: var(--sp-4);
        margin-bottom: var(--sp-6);
        animation: fadeInUp 0.5s ease both;
    }

    .success-banner__icon {
        font-size: 1.5rem;
        animation: pulse 2s ease-in-out infinite;
    }

    .success-banner__text {
        font-size: 0.9rem;
        color: var(--neon-green);
        font-weight: 600;
    }

    .success-banner__sub {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 2px;
    }

    /* ===== 19. RESPONSIVE ===== */
    .pkmn-moves { grid-template-columns: 1fr; }
    .team-grid { grid-template-columns: repeat(2, 1fr); }
    .pkmn-card__hero { flex-wrap: wrap; }
    .pkmn-card__name { font-size: 1.25rem; }

    @media (min-width: 640px) {
        .pkmn-moves { grid-template-columns: 1fr 1fr; }
        .team-grid { grid-template-columns: repeat(3, 1fr); }
        .pkmn-card__name { font-size: 1.5rem; }
    }

    @media (min-width: 1024px) {
        .pkmn-card__body { padding: var(--sp-6) var(--sp-8); }
        .summary-card { padding: var(--sp-10); }
    }

    @container (max-width: 400px) {
        .pkmn-card__hero {
            flex-direction: column;
            text-align: center;
        }
        .pkmn-card__name { font-size: 1.15rem; }
        .pkmn-moves { grid-template-columns: 1fr; }
    }

    /* ===== 20. PAGE-SPECIFIC STYLES ===== */

    /* Help/Settings pages */
    .page-section {
        background: var(--bg-glass);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-default);
        border-radius: var(--r-xl);
        padding: var(--sp-6);
        margin-bottom: var(--sp-6);
        animation: fadeInUp 0.5s ease both;
    }

    .page-section h3 {
        font-family: var(--font-display) !important;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-bright);
        margin: 0 0 var(--sp-4) 0;
        display: flex;
        align-items: center;
        gap: var(--sp-2);
    }

    .page-section h3::before {
        content: '';
        width: 3px; height: 18px;
        background: linear-gradient(180deg, var(--neon-purple), var(--neon-blue));
        border-radius: 2px;
    }

    /* How-it-works steps */
    .steps-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--sp-4);
    }

    .step-card {
        background: var(--bg-raised);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-lg);
        padding: var(--sp-5);
        text-align: center;
        transition: all 0.3s ease;
    }

    .step-card:hover {
        border-color: var(--border-glow);
        transform: translateY(-2px);
    }

    .step-card__num {
        font-family: var(--font-display) !important;
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .step-card__title {
        font-family: var(--font-display) !important;
        font-weight: 700;
        font-size: 0.9rem;
        color: var(--text-bright);
        margin: var(--sp-2) 0;
    }

    .step-card__desc {
        font-size: 0.8rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
