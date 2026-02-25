"""
Custom CSS styling for the Pokemon VGC Analysis Platform.
Minimalist design system with clean typography and consistent spacing.
"""

import streamlit as st


def apply_custom_css():
    """Apply clean, minimalist CSS styling for VGC Analysis Platform"""
    st.markdown(
        """
    <style>
    /* ===== 1. DESIGN TOKENS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        /* Primary: Indigo */
        --color-primary-50:  #eef2ff;
        --color-primary-100: #e0e7ff;
        --color-primary-200: #c7d2fe;
        --color-primary-300: #a5b4fc;
        --color-primary-400: #818cf8;
        --color-primary-500: #6366f1;
        --color-primary-600: #4f46e5;
        --color-primary-700: #4338ca;

        /* Neutrals: Slate */
        --color-neutral-0:   #ffffff;
        --color-neutral-50:  #f8fafc;
        --color-neutral-100: #f1f5f9;
        --color-neutral-200: #e2e8f0;
        --color-neutral-300: #cbd5e1;
        --color-neutral-400: #94a3b8;
        --color-neutral-500: #64748b;
        --color-neutral-600: #475569;
        --color-neutral-700: #334155;
        --color-neutral-800: #1e293b;
        --color-neutral-900: #0f172a;

        /* Semantic */
        --color-success: #22c55e;
        --color-warning: #f59e0b;
        --color-error:   #ef4444;
        --color-info:    #3b82f6;

        /* Surfaces */
        --surface-bg:   var(--color-neutral-50);
        --surface-card: var(--color-neutral-0);
        --surface-muted: var(--color-neutral-100);

        /* Text */
        --text-primary:   var(--color-neutral-900);
        --text-secondary: var(--color-neutral-600);
        --text-tertiary:  var(--color-neutral-400);
        --text-inverse:   var(--color-neutral-0);
        --text-accent:    var(--color-primary-600);

        /* Borders */
        --border-default: var(--color-neutral-200);
        --border-subtle:  var(--color-neutral-100);
        --border-focus:   var(--color-primary-400);

        /* Spacing (4px base) */
        --space-1:  4px;
        --space-2:  8px;
        --space-3:  12px;
        --space-4:  16px;
        --space-6:  24px;
        --space-8:  32px;
        --space-12: 48px;

        /* Typography */
        --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --font-mono:   'JetBrains Mono', 'Fira Code', Consolas, monospace;
        --text-xs:   0.75rem;
        --text-sm:   0.875rem;
        --text-base: 1rem;
        --text-lg:   1.125rem;
        --text-xl:   1.25rem;
        --text-2xl:  1.5rem;
        --text-3xl:  1.875rem;

        /* Radii */
        --radius-sm:   6px;
        --radius-md:   8px;
        --radius-lg:   12px;
        --radius-xl:   16px;
        --radius-full: 9999px;

        /* Shadows (only 2 levels) */
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.05);

        /* Pokemon Type Colors (flat) */
        --type-normal:   #a8a878;
        --type-fire:     #f08030;
        --type-water:    #6890f0;
        --type-grass:    #78c850;
        --type-electric: #f8d030;
        --type-psychic:  #f85888;
        --type-fighting: #c03028;
        --type-poison:   #a040a0;
        --type-ground:   #e0c068;
        --type-flying:   #a890f0;
        --type-bug:      #a8b820;
        --type-rock:     #b8a038;
        --type-ghost:    #705898;
        --type-dragon:   #7038f8;
        --type-dark:     #705848;
        --type-steel:    #b8b8d0;
        --type-fairy:    #ee99ac;
        --type-ice:      #98d8d8;

        /* EV stat colors */
        --ev-hp:   #ef4444;
        --ev-atk:  #f59e0b;
        --ev-def:  #3b82f6;
        --ev-spa:  #8b5cf6;
        --ev-spd:  #06b6d4;
        --ev-spe:  #10b981;
    }

    /* ===== 2. RESET & BASE ===== */
    * { font-family: var(--font-family); }

    .stApp { background: var(--surface-bg); }

    .main .block-container {
        padding: var(--space-6) var(--space-4);
        max-width: 1200px;
    }

    hr {
        border: none;
        height: 1px;
        background: var(--border-default);
        margin: var(--space-6) 0;
    }

    /* ===== 3. STREAMLIT OVERRIDES ===== */

    /* Buttons */
    .stButton > button {
        border-radius: var(--radius-md);
        border: 1px solid var(--border-default);
        background: var(--surface-card);
        color: var(--text-primary);
        font-weight: 500;
        padding: var(--space-2) var(--space-4);
        font-size: var(--text-sm);
        box-shadow: var(--shadow-sm);
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    .stButton > button:hover {
        border-color: var(--color-primary-300);
        box-shadow: var(--shadow-md);
    }

    .stButton > button[kind="primary"] {
        background: var(--color-primary-500);
        color: var(--text-inverse);
        border-color: var(--color-primary-500);
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--color-primary-600);
        border-color: var(--color-primary-600);
        box-shadow: var(--shadow-md);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-default);
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--border-focus);
        box-shadow: 0 0 0 3px var(--color-primary-100);
    }

    /* Code blocks */
    .stCode {
        border-radius: var(--radius-sm);
        font-family: var(--font-mono);
    }

    /* ===== 4. PAGE HEADER ===== */
    .page-header {
        text-align: center;
        padding: var(--space-8) 0 var(--space-6) 0;
        border-bottom: 1px solid var(--border-default);
        margin-bottom: var(--space-8);
    }

    .page-header h1 {
        font-size: var(--text-3xl);
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 var(--space-2) 0;
        letter-spacing: -0.02em;
    }

    .page-header p {
        font-size: var(--text-base);
        color: var(--text-secondary);
        margin: 0;
    }

    .page-header .status-line {
        font-size: var(--text-sm);
        color: var(--text-tertiary);
        margin-top: var(--space-2);
    }

    /* ===== 5. SIDEBAR ===== */
    .sidebar-header {
        padding: var(--space-4);
        border-bottom: 1px solid var(--border-default);
        margin: -1rem -1rem var(--space-4) -1rem;
    }

    .sidebar-header h2 {
        font-size: var(--text-lg);
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }

    .sidebar-header p {
        font-size: var(--text-sm);
        color: var(--text-secondary);
        margin: var(--space-1) 0 0 0;
    }

    .sidebar-status {
        background: var(--color-primary-50);
        border: 1px solid var(--color-primary-200);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        margin: var(--space-3) 0;
        font-size: var(--text-sm);
        color: var(--text-primary);
    }

    .sidebar-about {
        background: var(--surface-muted);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        text-align: center;
        font-size: var(--text-xs);
        color: var(--text-secondary);
        line-height: 1.6;
    }

    /* ===== 6. SUMMARY CARD ===== */
    .summary-card {
        background: var(--surface-card);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-lg);
        padding: var(--space-6);
        margin-bottom: var(--space-6);
    }

    .summary-card h1 {
        font-size: var(--text-2xl);
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 var(--space-3) 0;
    }

    .summary-meta {
        display: flex;
        gap: var(--space-4);
        flex-wrap: wrap;
        color: var(--text-secondary);
        font-size: var(--text-sm);
    }

    .summary-meta span {
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
    }

    /* ===== 7. INFO BLOCKS (strategy, strengths, weaknesses, etc.) ===== */
    .info-block {
        background: var(--surface-card);
        border: 1px solid var(--border-default);
        border-left: 3px solid var(--border-default);
        border-radius: var(--radius-md);
        padding: var(--space-4);
        margin-bottom: var(--space-4);
    }

    .info-block h4 {
        font-size: var(--text-sm);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin: 0 0 var(--space-2) 0;
    }

    .info-block p, .info-block div {
        font-size: var(--text-sm);
        color: var(--text-primary);
        line-height: 1.6;
        margin: 0;
    }

    .info-block--info    { border-left-color: var(--color-info); }
    .info-block--info h4 { color: var(--color-info); }

    .info-block--success    { border-left-color: var(--color-success); }
    .info-block--success h4 { color: var(--color-success); }

    .info-block--danger    { border-left-color: var(--color-error); }
    .info-block--danger h4 { color: var(--color-error); }

    .info-block--warning    { border-left-color: var(--color-warning); }
    .info-block--warning h4 { color: var(--color-warning); }

    /* ===== 8. METRIC CARD ===== */
    .metric-card {
        background: var(--surface-card);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        padding: var(--space-4);
        text-align: center;
    }

    .metric-card h3 {
        font-size: var(--text-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--text-secondary);
        margin: 0 0 var(--space-2) 0;
    }

    .metric-card p {
        font-size: var(--text-lg);
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }

    /* ===== 9. POKEMON CARD ===== */
    .pkmn-card {
        background: var(--surface-card);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-lg);
        overflow: hidden;
        margin-bottom: var(--space-6);
        container-type: inline-size;
        transition: box-shadow 0.2s ease;
    }

    .pkmn-card:hover {
        box-shadow: var(--shadow-md);
    }

    .pkmn-card__hero {
        padding: var(--space-4) var(--space-6);
        display: flex;
        align-items: center;
        gap: var(--space-4);
        border-bottom: 1px solid var(--border-default);
        position: relative;
    }

    .pkmn-card__hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        width: 4px;
    }

    .pkmn-card__slot {
        font-size: var(--text-xs);
        font-weight: 600;
        color: var(--text-tertiary);
    }

    .pkmn-card__sprite {
        width: 72px;
        height: 72px;
        object-fit: contain;
        flex-shrink: 0;
    }

    .pkmn-card__info {
        flex: 1;
        min-width: 0;
    }

    .pkmn-card__name {
        font-size: var(--text-2xl);
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 var(--space-1) 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .pkmn-card__badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
        padding: 2px var(--space-2);
        border-radius: var(--radius-full);
        font-size: var(--text-xs);
        font-weight: 600;
        color: var(--text-inverse);
    }

    .pkmn-card__body {
        padding: var(--space-4) var(--space-6);
    }

    .pkmn-card__section-title {
        font-size: var(--text-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-tertiary);
        margin: var(--space-4) 0 var(--space-3) 0;
        padding-bottom: var(--space-2);
        border-bottom: 1px solid var(--border-subtle);
    }

    /* ===== 10. POKEMON STAT ROWS ===== */
    .pkmn-stats {
        display: flex;
        flex-direction: column;
        gap: var(--space-1);
    }

    .pkmn-stat {
        display: flex;
        align-items: baseline;
        gap: var(--space-2);
        padding: var(--space-2) 0;
        font-size: var(--text-sm);
    }

    .pkmn-stat__label {
        color: var(--text-secondary);
        font-weight: 500;
        min-width: 56px;
        flex-shrink: 0;
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

    /* ===== 11. MOVE GRID ===== */
    .pkmn-moves {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--space-2);
    }

    .pkmn-move {
        background: var(--surface-muted);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        padding: var(--space-2) var(--space-3);
        font-size: var(--text-sm);
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
    }

    /* ===== 12. EV BARS ===== */
    .pkmn-ev-summary {
        margin-bottom: var(--space-3);
    }

    .pkmn-ev-summary code {
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        background: var(--surface-muted);
        padding: var(--space-1) var(--space-2);
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-default);
    }

    .pkmn-evs {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .pkmn-ev {
        display: flex;
        align-items: center;
        gap: var(--space-3);
    }

    .pkmn-ev__label {
        font-size: var(--text-xs);
        font-weight: 600;
        color: var(--text-secondary);
        width: 28px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        flex-shrink: 0;
    }

    .pkmn-ev__track {
        flex: 1;
        height: 6px;
        background: var(--color-neutral-200);
        border-radius: 3px;
        overflow: hidden;
    }

    .pkmn-ev__fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.5s ease-out;
    }

    .pkmn-ev__value {
        font-size: var(--text-xs);
        font-weight: 600;
        color: var(--text-primary);
        width: 32px;
        text-align: right;
        font-variant-numeric: tabular-nums;
        flex-shrink: 0;
    }

    .pkmn-ev-empty {
        font-size: var(--text-sm);
        color: var(--text-tertiary);
        font-style: italic;
        padding: var(--space-3) 0;
    }

    /* ===== 13. STRATEGY BLOCK ===== */
    .pkmn-strategy {
        background: var(--surface-card);
        border: 1px solid var(--border-default);
        border-left: 3px solid var(--color-warning);
        border-radius: var(--radius-md);
        padding: var(--space-4);
        margin-top: var(--space-3);
    }

    .pkmn-strategy h4 {
        font-size: var(--text-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--color-warning);
        margin: 0 0 var(--space-2) 0;
    }

    .pkmn-strategy p {
        font-size: var(--text-sm);
        color: var(--text-primary);
        line-height: 1.6;
        margin: 0;
    }

    /* ===== 14. TEAM GRID (sprite previews) ===== */
    .team-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--space-3);
        margin-bottom: var(--space-6);
    }

    .team-grid__item {
        background: var(--surface-card);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        text-align: center;
        transition: box-shadow 0.2s ease;
    }

    .team-grid__item:hover {
        box-shadow: var(--shadow-md);
    }

    .team-grid__item img {
        display: block;
        margin: 0 auto var(--space-2) auto;
        width: 80px;
        height: 80px;
        object-fit: contain;
    }

    .team-grid__item h4 {
        font-size: var(--text-sm);
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 var(--space-1) 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .team-grid__item p {
        font-size: var(--text-xs);
        color: var(--text-secondary);
        margin: 0;
    }

    /* ===== 15. TYPE COLOR CLASSES ===== */
    .type-normal   { background-color: var(--type-normal); }
    .type-fire     { background-color: var(--type-fire); }
    .type-water    { background-color: var(--type-water); }
    .type-grass    { background-color: var(--type-grass); }
    .type-electric { background-color: var(--type-electric); color: var(--color-neutral-900); }
    .type-psychic  { background-color: var(--type-psychic); }
    .type-fighting { background-color: var(--type-fighting); }
    .type-poison   { background-color: var(--type-poison); }
    .type-ground   { background-color: var(--type-ground); color: var(--color-neutral-900); }
    .type-flying   { background-color: var(--type-flying); }
    .type-bug      { background-color: var(--type-bug); }
    .type-rock     { background-color: var(--type-rock); }
    .type-ghost    { background-color: var(--type-ghost); }
    .type-dragon   { background-color: var(--type-dragon); }
    .type-dark     { background-color: var(--type-dark); }
    .type-steel    { background-color: var(--type-steel); color: var(--color-neutral-900); }
    .type-fairy    { background-color: var(--type-fairy); }
    .type-ice      { background-color: var(--type-ice); color: var(--color-neutral-900); }

    /* Hero accent bar picks up type color */
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

    /* ===== 16. RESPONSIVE ===== */

    /* Mobile-first base: everything stacks */
    .pkmn-moves {
        grid-template-columns: 1fr;
    }

    .team-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .pkmn-card__hero {
        flex-wrap: wrap;
    }

    .pkmn-card__name {
        font-size: var(--text-xl);
    }

    .page-header h1 {
        font-size: var(--text-2xl);
    }

    /* Tablet: 640px+ */
    @media (min-width: 640px) {
        .pkmn-moves {
            grid-template-columns: 1fr 1fr;
        }

        .team-grid {
            grid-template-columns: repeat(3, 1fr);
        }

        .pkmn-card__name {
            font-size: var(--text-2xl);
        }

        .page-header h1 {
            font-size: var(--text-3xl);
        }
    }

    /* Desktop: 1024px+ */
    @media (min-width: 1024px) {
        .pkmn-card__body {
            padding: var(--space-6);
        }

        .summary-card {
            padding: var(--space-8);
        }
    }

    /* Container queries for pokemon cards in columns */
    @container (max-width: 400px) {
        .pkmn-card__hero {
            flex-direction: column;
            text-align: center;
        }

        .pkmn-card__name {
            font-size: var(--text-xl);
        }

        .pkmn-moves {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
