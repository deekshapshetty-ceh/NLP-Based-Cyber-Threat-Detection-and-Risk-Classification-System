"""
CyberWatch — Premium Dark Cyber Theme v2
==========================================
Completely redesigned CSS system with:
  • Syne + JetBrains Mono typography (distinctive, editorial feel)
  • Multi-layer glassmorphism with depth
  • Animated gradient mesh backgrounds
  • CSS custom-property–driven design tokens
  • Micro-animations on all interactive elements
  • Proper WCAG AA contrast everywhere
  • Smooth page transitions
"""

import streamlit as st


def inject_css():
    """Inject the full premium CSS design system into every page."""
    st.markdown("""
    <style>
    /* ── Google Fonts ───────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap');

    /* ── Design Tokens ──────────────────────────────────────────────── */
    :root {
        color-scheme: dark;
        --cyan:        #00d4ff;
        --cyan-dim:    #00a8cc;
        --cyan-glow:   rgba(0,212,255,0.18);
        --violet:      #7c3aed;
        --emerald:     #00e5a0;
        --amber:       #f59e0b;
        --rose:        #f43f5e;
        --bg-base:     #04080f;
        --bg-surface:  #0a1220;
        --bg-raised:   #101d30;
        --border:      rgba(0,212,255,0.09);
        --border-md:   rgba(0,212,255,0.2);
        --text-1:      #eef2fa;
        --text-2:      #8fa3be;
        --text-3:      #3f5268;
        --font-sans:   'DM Sans', -apple-system, sans-serif;
        --font-head:   'Syne', sans-serif;
        --font-mono:   'Space Mono', monospace;
        --radius-sm:   6px;
        --radius-md:   10px;
        --radius-lg:   16px;
        --radius-xl:   22px;
        --shadow-cyan: 0 0 28px rgba(0,212,255,0.14);
        --sidebar-w:   260px;
    }

    /* ── Global Reset & Base ─────────────────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; }

    .stApp {
        font-family: var(--font-sans) !important;
        background: var(--bg-base) !important;
        color: var(--text-1) !important;
    }

    /* Subtle grid background */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(0,212,255,0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,212,255,0.025) 1px, transparent 1px);
        background-size: 48px 48px;
        pointer-events: none;
        z-index: 0;
    }
    /* Glow orbs */
    .stApp::after {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse 70% 50% at 10% 0%, rgba(0,212,255,0.05) 0%, transparent 55%),
            radial-gradient(ellipse 50% 40% at 90% 100%, rgba(124,58,237,0.07) 0%, transparent 55%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Sidebar — complete redesign ─────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: #050d1a !important;
        border-right: 1px solid rgba(0,212,255,0.12) !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }

    /* Sidebar nav links */
    section[data-testid="stSidebar"] .stMarkdown p {
        color: var(--text-3);
        font-size: 0.82rem;
        font-family: var(--font-sans);
    }
    section[data-testid="stSidebar"] a {
        color: var(--text-2) !important;
        text-decoration: none !important;
        transition: color 0.15s;
    }
    section[data-testid="stSidebar"] a:hover { color: var(--cyan) !important; }

    /* Nav item pills */
    section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] li {
        margin: 2px 8px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a {
        border-radius: var(--radius-md) !important;
        padding: 9px 14px !important;
        display: flex !important;
        align-items: center !important;
        font-family: var(--font-sans) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: var(--text-2) !important;
        transition: background 0.15s, color 0.15s !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a:hover {
        background: rgba(0,212,255,0.07) !important;
        color: var(--text-1) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a[aria-current="page"] {
        background: rgba(0,212,255,0.12) !important;
        color: var(--cyan) !important;
        font-weight: 600 !important;
        box-shadow: inset 3px 0 0 var(--cyan) !important;
    }

    /* ── Typography ──────────────────────────────────────────────────── */
    h1, h2, h3, h4, h5 {
        font-family: var(--font-head) !important;
        letter-spacing: -0.3px;
    }
    /* Scope to Streamlit's own h1 only — not custom .hero-title divs */
    [data-testid="stMarkdownContainer"] h1,
    .stMarkdown h1 {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: var(--text-1) !important;
        background: linear-gradient(120deg, #e8f0fe 0%, #a0b4d0 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 0.25rem !important;
    }
    h2 { color: var(--text-1) !important; font-weight: 700 !important; font-size: 1.4rem !important; }
    h3 { color: var(--text-2) !important; font-weight: 600 !important; font-size: 1.15rem !important; }
    h4 {
        color: var(--text-1) !important;
        font-family: var(--font-head) !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px;
    }
    p { line-height: 1.65; color: var(--text-2); }

    /* ── Button text fix: p tags inside buttons must not inherit global p color ── */
    button p, button span, button div {
        color: inherit !important;
        -webkit-text-fill-color: inherit !important;
        background: none !important;
        -webkit-background-clip: unset !important;
        background-clip: unset !important;
    }

    /* ── Buttons (Streamlit 1.30+ uses data-testid="baseButton-primary/secondary") ── */
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-secondary"],
    .stButton > button,
    .stFormSubmitButton > button {
        font-family: var(--font-sans) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        border-radius: var(--radius-md) !important;
        padding: 0.55rem 1.25rem !important;
        transition: all 0.18s ease !important;
        -webkit-text-fill-color: unset !important;
    }

    /* PRIMARY buttons */
    [data-testid="baseButton-primary"],
    .stButton > button[data-testid="baseButton-primary"],
    .stFormSubmitButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #0090b8 0%, #00d4ff 100%) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: none !important;
        box-shadow: 0 2px 12px rgba(0,212,255,0.3) !important;
    }
    [data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 22px rgba(0,212,255,0.4) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* SECONDARY buttons */
    [data-testid="baseButton-secondary"],
    .stButton > button[data-testid="baseButton-secondary"],
    .stFormSubmitButton > button[data-testid="baseButton-secondary"] {
        background: rgba(10,18,32,0.9) !important;
        border: 1px solid var(--border-md) !important;
        color: #eef2fa !important;
        -webkit-text-fill-color: #eef2fa !important;
    }
    [data-testid="baseButton-secondary"]:hover {
        background: rgba(0,212,255,0.07) !important;
        border-color: var(--cyan) !important;
        color: var(--cyan) !important;
        -webkit-text-fill-color: var(--cyan) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-cyan) !important;
    }

    /* Fallback for any button not matched by data-testid */
    .stButton > button {
        color: #eef2fa !important;
        -webkit-text-fill-color: #eef2fa !important;
    }

    [data-testid^="baseButton-"]:active,
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── Download Button ─────────────────────────────────────────────── */
    [data-testid="baseButton-download"],
    .stDownloadButton > button {
        font-family: var(--font-sans) !important;
        font-weight: 600 !important;
        background: rgba(0,212,255,0.06) !important;
        border: 1px solid rgba(0,212,255,0.25) !important;
        color: var(--cyan) !important;
        -webkit-text-fill-color: var(--cyan) !important;
        border-radius: var(--radius-md) !important;
        transition: all 0.18s ease !important;
    }
    [data-testid="baseButton-download"]:hover,
    .stDownloadButton > button:hover {
        background: rgba(0,212,255,0.13) !important;
        border-color: var(--cyan) !important;
        color: var(--cyan) !important;
        -webkit-text-fill-color: var(--cyan) !important;
        box-shadow: var(--shadow-cyan) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Inputs ─────────────────────────────────────────────────────── */
    .stTextInput input, .stTextArea textarea {
        font-family: var(--font-sans) !important;
        border-radius: var(--radius-md) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        background: rgba(10,18,32,0.8) !important;
        color: var(--text-1) !important;
        transition: border-color 0.18s, box-shadow 0.18s !important;
        font-size: 0.9rem !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--cyan) !important;
        box-shadow: 0 0 0 3px rgba(0,212,255,0.1) !important;
        outline: none !important;
    }

    /* ── Selectbox ────────────────────────────────────────────────────── */
    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(10,18,32,0.85) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: var(--radius-md) !important;
        transition: border-color 0.18s !important;
    }
    .stSelectbox [data-baseweb="select"] > div:hover {
        border-color: var(--border-md) !important;
    }

    /* ── Slider ──────────────────────────────────────────────────────── */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: var(--cyan) !important;
        border: 2px solid var(--cyan) !important;
        box-shadow: 0 0 10px rgba(0,212,255,0.5) !important;
    }

    /* ── Tabs ────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(10,18,32,0.7);
        border-radius: var(--radius-md);
        padding: 4px;
        border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-sans) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        color: var(--text-2) !important;
        transition: all 0.18s !important;
        border: none !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0,212,255,0.12) !important;
        color: var(--cyan) !important;
        box-shadow: 0 0 0 1px rgba(0,212,255,0.25) !important;
    }

    /* ── DataFrames ────────────────────────────────────────────────────── */
    .stDataFrame {
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
        border: 1px solid var(--border) !important;
    }

    /* ── Expanders ───────────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        font-family: var(--font-sans) !important;
        font-weight: 600 !important;
        background: rgba(10,18,32,0.7) !important;
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border) !important;
        transition: all 0.18s !important;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(0,212,255,0.05) !important;
        border-color: var(--border-md) !important;
    }
    .streamlit-expanderContent {
        border: 1px solid var(--border);
        border-top: none;
        border-radius: 0 0 var(--radius-md) var(--radius-md);
        background: rgba(10,18,32,0.5);
    }

    /* ── Progress bar ─────────────────────────────────────────────────── */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--cyan-dim), var(--cyan)) !important;
        border-radius: 4px !important;
    }
    .stProgress > div > div {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 4px !important;
    }

    /* ── File Uploader ───────────────────────────────────────────────── */
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(10,18,32,0.6) !important;
        border: 2px dashed var(--border-md) !important;
        border-radius: var(--radius-lg) !important;
        transition: all 0.18s !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--cyan) !important;
        background: rgba(0,212,255,0.04) !important;
    }

    /* ── Alerts ──────────────────────────────────────────────────────── */
    .stAlert {
        border-radius: var(--radius-md) !important;
        border: 1px solid !important;
        font-family: var(--font-sans) !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stAlert"][data-type="info"]    { background: rgba(0,212,255,0.06) !important;   border-color: rgba(0,212,255,0.22) !important; }
    [data-testid="stAlert"][data-type="warning"] { background: rgba(245,158,11,0.06) !important;  border-color: rgba(245,158,11,0.25) !important; }
    [data-testid="stAlert"][data-type="error"]   { background: rgba(244,63,94,0.06) !important;   border-color: rgba(244,63,94,0.25) !important; }
    [data-testid="stAlert"][data-type="success"] { background: rgba(0,229,160,0.06) !important;   border-color: rgba(0,229,160,0.25) !important; }

    /* ── Spinner ─────────────────────────────────────────────────────── */
    .stSpinner > div { border-top-color: var(--cyan) !important; }

    /* ── HR ──────────────────────────────────────────────────────────── */
    hr {
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Scrollbar ───────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.15); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.35); }

    /* ── Keyframes ───────────────────────────────────────────────────── */
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: 0.5; transform: scale(0.85); }
    }
    @keyframes shimmer-border {
        0%   { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }

    /* ── Main Container ──────────────────────────────────────────────── */
    .main .block-container {
        padding-top: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1380px;
        margin: 0 auto;
    }

    /* ── Metric cards ────────────────────────────────────────────────── */
    .cw-metric-card {
        background: linear-gradient(145deg, #0a1422, #0d1a2e);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: var(--radius-lg);
        padding: 18px 16px;
        position: relative;
        overflow: visible;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .cw-metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-color, #00d4ff), transparent);
        opacity: 0.8;
    }
    .cw-metric-card::after {
        content: '';
        position: absolute;
        bottom: 0; right: 0;
        width: 80px; height: 80px;
        background: radial-gradient(circle, var(--accent-color, #00d4ff) 0%, transparent 70%);
        opacity: 0.04;
        pointer-events: none;
    }
    .cw-metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.4), 0 0 0 1px rgba(0,212,255,0.08);
    }
    .cw-metric-icon {
        font-size: 1.5rem;
        margin-bottom: 12px;
        display: block;
    }
    .cw-metric-label {
        font-family: var(--font-sans);
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: var(--text-3);
        margin-bottom: 6px;
    }
    .cw-metric-value {
        font-family: var(--font-head);
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.5px;
        white-space: nowrap;
    }
    .cw-metric-delta {
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 6px;
    }

    /* ── Section label ────────────────────────────────────────────────── */
    .cw-section-label {
        font-family: var(--font-sans);
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--cyan);
        margin-bottom: 4px;
    }

    /* ── Threat cards ─────────────────────────────────────────────────── */
    .cw-threat-card {
        background: linear-gradient(145deg, #080f1c, #0b1626);
        border: 1px solid rgba(255,255,255,0.05);
        border-bottom: 2px solid var(--card-accent, rgba(0,212,255,0.25));
        border-radius: var(--radius-lg);
        padding: 18px 20px;
        margin-bottom: 12px;
        min-height: 150px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .cw-threat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(0,0,0,0.45);
        border-color: rgba(255,255,255,0.09);
        border-bottom-color: var(--card-accent, rgba(0,212,255,0.5));
    }

    /* ── Alert rows ───────────────────────────────────────────────────── */
    .cw-alert-row {
        background: linear-gradient(90deg, rgba(10,18,32,0.95), rgba(8,15,26,0.8));
        border-left: 3px solid var(--row-color, #f43f5e);
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        padding: 13px 18px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 16px;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .cw-alert-row:hover {
        transform: translateX(3px);
        box-shadow: -3px 0 16px rgba(0,0,0,0.3);
    }

    /* ── Status dot ───────────────────────────────────────────────────── */
    .cw-status-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: var(--emerald);
        animation: pulse-dot 2s ease-in-out infinite;
        margin-right: 6px;
        vertical-align: middle;
        box-shadow: 0 0 6px var(--emerald);
    }

    /* ── Hide Streamlit chrome ────────────────────────────────────────── */
    [data-testid="stDecoration"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    header { display: none !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    </style>
    """, unsafe_allow_html=True)





# ── Component Helpers ──────────────────────────────────────────────────────

def metric_card(label: str, value: str, icon: str = "", delta=None, color: str = "#00d4ff"):
    """Render a premium glassmorphism metric card."""
    delta_html = ""
    if delta is not None:
        arrow = "▲" if delta >= 0 else "▼"
        dc = "#00e5a0" if delta >= 0 else "#f43f5e"
        delta_html = (
            f'<div class="cw-metric-delta" style="color:{dc}">'
            f'{arrow} {abs(delta):.1f}%</div>'
        )
    st.markdown(f"""
    <div class="cw-metric-card" style="--accent-color:{color}">
        <span class="cw-metric-icon" style="color:{color}">{icon}</span>
        <div class="cw-metric-label">{label}</div>
        <div class="cw-metric-value" style="color:{color}">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def severity_badge(risk: str) -> str:
    """Return an inline HTML severity badge."""
    palette = {
        "HIGH":   {"bg": "rgba(244,63,94,0.12)",  "border": "rgba(244,63,94,0.3)",  "text": "#f43f5e"},
        "MEDIUM": {"bg": "rgba(245,158,11,0.12)", "border": "rgba(245,158,11,0.3)", "text": "#f59e0b"},
        "LOW":    {"bg": "rgba(0,229,160,0.12)",  "border": "rgba(0,229,160,0.3)",  "text": "#00e5a0"},
    }
    c = palette.get(risk, {"bg": "rgba(148,163,184,0.1)", "border": "rgba(148,163,184,0.2)", "text": "#94a3b8"})
    return (
        f'<span style="background:{c["bg"]};color:{c["text"]};padding:4px 14px;'
        f'border-radius:20px;font-size:0.75rem;font-weight:700;font-family:var(--font-sans,sans-serif);'
        f'letter-spacing:0.8px;border:1px solid {c["border"]};display:inline-block">{risk}</span>'
    )


def page_header(title: str, subtitle: str = "", icon: str = "", label: str = ""):
    """Render a polished page header with optional subtitle and label."""
    label_html = (
        f'<div class="cw-section-label" style="color:#00d4ff;font-family:\'DM Sans\',sans-serif;'
        f'font-size:0.65rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;'
        f'margin-bottom:6px">{label}</div>'
    ) if label else ""
    subtitle_html = (
        f'<p style="margin:8px 0 0;color:#64748b;font-size:0.95rem;max-width:640px;'
        f'line-height:1.6;font-family:\'DM Sans\',sans-serif">{subtitle}</p>'
    ) if subtitle else ""
    icon_html = f'<span style="font-size:1.8rem;margin-right:12px;vertical-align:middle">{icon}</span>' if icon else ""

    st.markdown(f"""
    <div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid rgba(0,212,255,0.07)">
        {label_html}
        <h1 style="margin:0;font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;
                   color:#f0f4fa;letter-spacing:-0.5px;display:flex;align-items:center">
            {icon_html}{title}
        </h1>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def sidebar_branding():
    """Premium control-panel sidebar: logo, user card, grouped nav, sign-out."""
    from utils.auth import logout_user

    username   = st.session_state.get("username",   "analyst")
    user_role  = st.session_state.get("user_role",  "Analyst")
    initials   = username[:2].upper()

    # ── CSS for custom nav ───────────────────────────────────────────────
    st.markdown("""
    <style>
    [data-testid="stSidebarNavItems"] { display: none !important; }
    [data-testid="stSidebarNavSeparator"] { display: none !important; }
    .sb-section {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.58rem; font-weight: 700;
        letter-spacing: 2.5px; text-transform: uppercase;
        color: #1e3a4a; padding: 14px 16px 5px; display: block;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"] {
        border-radius: 10px !important; margin: 1px 8px !important;
        transition: background 0.15s !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
        background: rgba(0,212,255,0.06) !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] {
        background: rgba(0,212,255,0.1) !important;
        box-shadow: inset 3px 0 0 #00d4ff !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"] p {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.875rem !important; font-weight: 500 !important;
    }
    .sb-sep {
        height: 1px;
        background: linear-gradient(90deg,transparent,rgba(0,212,255,0.1),transparent);
        margin: 8px 12px;
    }
    .sb-user-card {
        background: rgba(0,212,255,0.04); border: 1px solid rgba(0,212,255,0.09);
        border-radius: 12px; padding: 12px 14px; margin: 0 10px 4px;
        display: flex; align-items: center; gap: 11px;
    }
    .sb-avatar {
        width: 38px; height: 38px; border-radius: 50%;
        background: linear-gradient(135deg,#0090b8,#7c3aed);
        display: flex; align-items: center; justify-content: center;
        font-family: 'Syne', sans-serif; font-weight: 800;
        font-size: 0.85rem; color: #fff; flex-shrink: 0;
        box-shadow: 0 0 12px rgba(0,212,255,0.2);
    }
    .sb-user-name { font-family:'DM Sans',sans-serif; font-weight:600; font-size:0.875rem; color:#c8d6e5; }
    .sb-user-role {
        display:inline-block; background:rgba(0,212,255,0.1); color:#00d4ff;
        border:1px solid rgba(0,212,255,0.2); border-radius:8px;
        font-size:0.62rem; font-weight:700; letter-spacing:0.8px;
        padding:2px 8px; font-family:'DM Sans',sans-serif; margin-top:3px;
    }
    .sb-status {
        display:flex; align-items:center; gap:7px; padding:8px 18px;
        font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#1e3a4a;
    }
    .sb-online-dot {
        width:7px; height:7px; border-radius:50%; background:#00e5a0;
        box-shadow:0 0 6px #00e5a0; animation:pulse-dot 2s ease-in-out infinite;
    }
    </style>
    """, unsafe_allow_html=True)

    # Logo
    st.markdown("""
    <div style="padding:20px 16px 12px;text-align:center">
        <div style="display:flex;align-items:center;justify-content:center;gap:10px">
            <div style="width:36px;height:36px;background:linear-gradient(135deg,rgba(0,212,255,0.15),rgba(124,58,237,0.2));
                        border:1px solid rgba(0,212,255,0.25);border-radius:10px;
                        display:flex;align-items:center;justify-content:center;font-size:1.1rem;
                        box-shadow:0 0 16px rgba(0,212,255,0.1)">\U0001f6e1\ufe0f</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;
                            background:linear-gradient(135deg,#00d4ff,#7c3aed);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                            background-clip:text;line-height:1">CyberWatch</div>
                <div style="font-size:0.52rem;letter-spacing:2.5px;text-transform:uppercase;
                            color:#1e3a4a;font-family:'DM Sans',sans-serif;font-weight:600">Threat Intel</div>
            </div>
        </div>
    </div>
    <div class="sb-sep"></div>
    """, unsafe_allow_html=True)

    # User card
    st.markdown(f"""
    <div class="sb-user-card">
        <div class="sb-avatar">{initials}</div>
        <div>
            <div class="sb-user-name">{username.capitalize()}</div>
            <div class="sb-user-role">{user_role}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nav sections
    st.markdown('<span class="sb-section">\u25c6 Core</span>', unsafe_allow_html=True)
    st.page_link("app.py",                        label="Dashboard",          icon="\U0001f3e0")
    st.page_link("pages/1_Threat_Prediction.py",  label="Threat Prediction",  icon="\U0001f3af")
    st.page_link("pages/2_Alert_Center.py",       label="Alert Center",       icon="\U0001f6a8")
    st.page_link("pages/6_Action_Tracker.py",     label="Action Tracker",     icon="\u2705")

    st.markdown('<span class="sb-section">\u25c6 Analytics</span>', unsafe_allow_html=True)
    st.page_link("pages/3_Analytics.py",          label="Analytics",          icon="\U0001f4ca")
    st.page_link("pages/4_Dataset_Explorer.py",   label="Dataset Explorer",   icon="\U0001f5c2\ufe0f")
    st.page_link("pages/5_Bulk_Prediction.py",    label="Bulk Prediction",    icon="\u26a1")

    st.markdown('<span class="sb-section">\u25c6 ML Insights</span>', unsafe_allow_html=True)
    st.page_link("pages/7_Model_Performance.py",  label="Model Performance",  icon="\U0001f3c6")
    st.page_link("pages/8_Feature_Importance.py", label="Feature Importance", icon="\U0001f52c")
    st.page_link("pages/9_SHAP_Explainability.py",label="SHAP Explainability",icon="\U0001f9e9")

    st.markdown('<div class="sb-sep" style="margin-top:12px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-status"><span class="sb-online-dot"></span>System Online · Live</div>',
                unsafe_allow_html=True)

    st.markdown('<span class="sb-section">◆ Account</span>', unsafe_allow_html=True)
    st.page_link("pages/0_Admin_Panel.py", label="Admin Panel", icon="⚙️")

    if st.button("\u23fb  Sign Out", use_container_width=True, key="sidebar_signout"):
        logout_user()
        st.rerun()



def init_session_state():
    """Initialize all session-state variables (safe to call multiple times)."""
    defaults = {
        "prediction_history": [],
        "action_tracker":     [],
        "alerts":             [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_footer():
    """Render the app footer."""
    st.markdown("""
    <div style="margin-top:40px;padding-top:20px;border-top:1px solid rgba(0,212,255,0.07);
                text-align:center">
        <p style="color:#1e293b;font-size:0.72rem;letter-spacing:0.8px;
                  font-family:'DM Sans',sans-serif;margin:0">
            🛡️ CyberWatch &nbsp;·&nbsp; NLP Threat Intelligence &nbsp;·&nbsp;
            Streamlit · scikit-learn · TF-IDF · Random Forest
        </p>
    </div>
    """, unsafe_allow_html=True)


def chart_layout(title: str = "", height: int = 360):
    """Return consistent Plotly layout kwargs for dark charts."""
    base = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#94a3b8", size=12),
        margin=dict(t=32 if title else 8, b=20, l=10, r=10),
        height=height,
        showlegend=False,
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(255,255,255,0.06)",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(255,255,255,0.06)",
            tickfont=dict(size=11),
        ),
    )
    if title:
        base["title"] = dict(
            text=title,
            font=dict(family="Syne, sans-serif", color="#e8edf5", size=14),
        )
    return base
