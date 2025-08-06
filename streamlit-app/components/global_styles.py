import streamlit as st

def inject_global_styles():
    """Inject professional, modern CSS styles for the entire application"""
    st.markdown("""
    <style>
    /* === MINIMAL DESIGN SYSTEM (ACCESSIBLE) === */
    :root {
        /* Color Palette - Minimal Blue/Gray Theme */
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --primary-light: #e0e7ef;
        --secondary: #475569;
        --accent: #059669;
        --success: #059669;
        --warning: #d97706;
        --error: #dc2626;
        --info: #2563eb;

        /* Neutral Colors */
        --background: #f8fafc;
        --surface: #ffffff;
        --surface-hover: #f1f5f9;
        --border: #e2e8f0;
        --border-light: #f3f4f6;
        --text-primary: #000000;
        --text-secondary: #2d3748;
        --text-muted: #5a6270;

        /* Spacing & Layout */
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.03);
        --shadow-md: 0 2px 8px rgba(0,0,0,0.04);

        /* Typography */
        --font-main: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
    }
    
    /* === GLOBAL RESET & BASE STYLES === */
    * {
        box-sizing: border-box;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: var(--font-main) !important;
        background: var(--background) !important;
        color: var(--text-primary) !important;
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Hide default Streamlit elements */
    header, footer, #MainMenu { 
        visibility: hidden !important; 
    }
    
    .stApp {
        background: var(--background) !important;
    }
    
    /* === MINIMAL NAVIGATION BAR === */
    .vgc-navbar {
        position: sticky;
        top: 0;
        z-index: 1000;
        background: #fff;
        border-bottom: 1px solid var(--border);
        box-shadow: none;
        padding: 0.75rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        transition: background 0.2s;
    }
    .vgc-navbar .nav-logo {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--primary);
        background: none;
        letter-spacing: -0.5px;
        margin-right: 1.5rem;
    }
    .vgc-navbar .nav-link {
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: var(--radius-sm);
        background: none;
        border: none;
        transition: background 0.15s, color 0.15s;
        text-decoration: none;
        outline: none;
        position: relative;
    }
    .vgc-navbar .nav-link:focus {
        outline: 2.5px solid #1d4ed8 !important;
        outline-offset: 2.5px !important;
        box-shadow: none !important;
    }
    .vgc-navbar .nav-link:hover, .vgc-navbar .nav-link.active {
        background: var(--primary-light);
        color: var(--primary);
    }
    .vgc-navbar .nav-avatar {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem;
        border-radius: var(--radius-md);
        background: var(--surface-hover);
    }
    
    .vgc-navbar .nav-avatar-img {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: 3px solid var(--primary);
        object-fit: cover;
        box-shadow: var(--shadow-sm);
    }
    
    /* === MAIN CONTENT LAYOUT === */
    /* Full width layout without sidebar */
    .main .block-container {
        margin-left: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: none !important;
    }
    
    /* === MINIMAL BUTTONS === */
    .vgc-btn, .stButton > button, .stDownloadButton > button {
        background: var(--primary);
        color: #fff;
        border: none;
        border-radius: var(--radius-sm);
        padding: 0.5rem 1.1rem;
        font-size: 1rem;
        font-weight: 500;
        box-shadow: none;
        transition: background 0.15s, color 0.15s;
        outline: none;
        cursor: pointer;
    }
    .vgc-btn:focus, .stButton > button:focus, .stDownloadButton > button:focus {
        outline: 2px solid #1d4ed8;
        outline-offset: 2px;
        box-shadow: none;
    }
    .vgc-btn:hover, .stButton > button:hover, .stDownloadButton > button:hover {
        background: var(--primary-dark);
        color: #fff;
    }
    
    /* === MINIMAL CARDS === */
    .vgc-card, .card-section, .trend-card, .help-card {
        background: var(--surface);
        border-radius: var(--radius-md);
        box-shadow: none;
        border: 1px solid var(--border);
        padding: 1.25rem 1.25rem 1rem 1.25rem;
        margin-bottom: 1.25rem;
        transition: border-color 0.15s;
    }
    .vgc-card:focus-within, .card-section:focus-within, .trend-card:focus-within, .help-card:focus-within {
        border-color: var(--primary);
    }
    
    /* === SECTION TITLES (Semantic Headings) === */
    .card-section-title, .help-card h3, .vgc-card h3 {
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 0.75rem;
        letter-spacing: -0.5px;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem 1.5rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--surface-hover) !important;
        border-color: var(--primary) !important;
    }
    
    /* === PROFESSIONAL ALERTS === */
    .stAlert {
        border-radius: var(--radius-md) !important;
        border: none !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* === PROFESSIONAL FOOTER === */
    .vgc-footer {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.9rem;
        padding: 3rem 0 2rem 0;
        margin-top: 4rem;
        border-top: 1px solid var(--border);
        background: var(--surface);
    }
    
    /* === RESPONSIVE DESIGN === */
    @media (max-width: 1200px) {
        .vgc-navbar { 
            padding: 0.75rem 1rem; 
            gap: 1rem; 
        }
        .vgc-navbar .nav-logo { 
            font-size: 1.25rem; 
            margin-right: 1rem; 
        }
    }
    
    @media (max-width: 900px) {
        .vgc-navbar { 
            flex-direction: column; 
            gap: 1rem; 
            padding: 1rem; 
        }
        .vgc-navbar .nav-avatar { 
            margin-left: 0; 
        }
    }
    
    @media (max-width: 768px) {
        [data-testid="stSidebar"] { 
            width: 100vw !important; 
            min-width: 0 !important; 
            max-width: none !important; 
        }
        .vgc-navbar { 
            padding: 0.5rem 1rem; 
        }
        .vgc-card {
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
    }
    
    /* === ANIMATIONS === */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .vgc-card, .vgc-metric-card {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* === CUSTOM SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--border-light);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--primary-dark), var(--secondary));
    }
    
    /* Prevent page jumps on button clicks */
    .stDownloadButton {
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton:hover {
        transform: translateY(-2px) !important;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script>
    // Preserve scroll position and prevent page jumps
    document.addEventListener('DOMContentLoaded', function() {
        // Store scroll position before any button clicks
        let scrollPosition = 0;
        
        // Save scroll position before any interaction
        window.addEventListener('beforeunload', function() {
            sessionStorage.setItem('scrollPosition', window.scrollY);
        });
        
        // Restore scroll position after page load
        window.addEventListener('load', function() {
            const savedPosition = sessionStorage.getItem('scrollPosition');
            if (savedPosition) {
                setTimeout(function() {
                    window.scrollTo(0, parseInt(savedPosition));
                }, 100);
            }
        });
        
        // Prevent download buttons from causing page jumps
        document.addEventListener('click', function(e) {
            if (e.target.closest('.stDownloadButton')) {
                scrollPosition = window.scrollY;
                setTimeout(function() {
                    window.scrollTo(0, scrollPosition);
                }, 50);
            }
        });
    });
    </script>
    """, unsafe_allow_html=True)
