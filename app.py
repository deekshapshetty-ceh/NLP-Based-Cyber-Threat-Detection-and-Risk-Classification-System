"""
🛡️ CyberWatch — NLP Cyber Threat Intelligence Dashboard
Main entry point & Home page.
"""
import streamlit as st
import plotly.express as px

from config.theme import (
    inject_css, metric_card, sidebar_branding,
    init_session_state, render_footer, chart_layout,
)
from config.constants import RISK_MAP, THREAT_ICONS, THREAT_DESCRIPTIONS
from utils.data_loader import load_data, get_stats
from utils.auth_gate import show_auth_gate

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CyberWatch — Threat Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_session_state()

# ── Auth gate — shows login/register if not signed in ────────────────────────
show_auth_gate()

# ── Data ─────────────────────────────────────────────────────────────────────
df    = load_data()
stats = get_stats(df)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_branding()

# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Remove Streamlit top chrome gap */
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
header { display: none !important; }
.hero-wrap {
    background: linear-gradient(135deg, #080f1c 0%, #040810 100%);
    border: 1px solid rgba(0,212,255,0.13);
    border-radius: 20px;
    padding: 36px 44px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 40px rgba(0,0,0,0.6);
}
.hero-wrap::before {
    content: '';
    position: absolute;
    top: -80px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0,212,255,0.07) 0%, transparent 65%);
    pointer-events: none;
}
.hero-wrap::after {
    content: '';
    position: absolute;
    bottom: -60px; left: -40px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(124,58,237,0.08) 0%, transparent 65%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.6rem; font-weight: 700;
    letter-spacing: 3.5px; text-transform: uppercase;
    color: #00d4ff; margin-bottom: 10px;
    display: flex; align-items: center; gap: 8px;
}
.hero-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #00e5a0; box-shadow: 0 0 7px #00e5a0;
    display: inline-block; flex-shrink: 0;
}
.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.65rem !important;
    font-weight: 800 !important; letter-spacing: -0.5px;
    color: #eef2fa !important; -webkit-text-fill-color: #eef2fa !important;
    background: none !important; margin: 0 0 10px !important;
    line-height: 1.2 !important; white-space: normal; overflow: visible;
}
.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem; color: #5a7090;
    max-width: 540px; line-height: 1.7; margin-bottom: 20px;
}
.hero-sub strong { color: #00d4ff; }
.hero-badges { display: flex; gap: 8px; flex-wrap: wrap; }
.hero-badge {
    padding: 5px 14px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600;
    font-family: 'DM Sans', sans-serif;
}
.badge-cyan   { background: rgba(0,212,255,0.08);  border: 1px solid rgba(0,212,255,0.22);  color: #00d4ff; }
.badge-green  { background: rgba(0,229,160,0.06);  border: 1px solid rgba(0,229,160,0.2);   color: #00e5a0; }
.badge-violet { background: rgba(124,58,237,0.07); border: 1px solid rgba(124,58,237,0.2);  color: #a78bfa; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-eyebrow"><span class="hero-dot"></span>Real-Time Intelligence Platform</div>
  <div class="hero-title">Cyber Threat Dashboard</div>
  <div class="hero-sub">
    NLP-powered detection and classification across
    <strong>{stats['total']:,}</strong> social-media entries,
    spanning <strong>8</strong> threat categories in real time.
  </div>
  <div class="hero-badges">
    <span class="hero-badge badge-cyan">⚡ Live Analysis</span>
    <span class="hero-badge badge-green">🤖 ML-Powered</span>
    <span class="hero-badge badge-violet">🧩 SHAP Explainability</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Total Analyzed",    f"{stats['total']:,}",      "📄", color="#00d4ff")
with c2:
    metric_card("High-Risk Threats", f"{stats['high_risk']:,}",  "🔴", color="#f43f5e")
with c3:
    metric_card("Medium-Risk",       f"{stats['medium_risk']:,}","🟡", color="#f59e0b")
with c4:
    metric_card("Low-Risk",          f"{stats['low_risk']:,}",   "🟢", color="#00e5a0")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Charts Row ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 2], gap="medium")

with col1:
    st.markdown("#### 📊 Threat Distribution")
    tc = stats["type_counts"]
    fig1 = px.bar(
        x=list(tc.keys()), y=list(tc.values()),
        color=list(tc.values()),
        color_continuous_scale=[[0, "#1e293b"], [0.4, "#7c3aed"], [1, "#00d4ff"]],
        labels={"x": "Threat Type", "y": "Count"},
    )
    fig1.update_traces(marker_line_width=0,
                       hovertemplate="<b>%{x}</b><br>%{y:,} entries<extra></extra>")
    layout = chart_layout(height=320)
    layout["showlegend"] = False
    layout["coloraxis_showscale"] = False
    fig1.update_layout(**layout)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("#### 🎯 Risk Level Breakdown")
    risk_data = {"HIGH": stats["high_risk"], "MEDIUM": stats["medium_risk"], "LOW": stats["low_risk"]}
    RISK_COLOR_V2 = {"HIGH": "#f43f5e", "MEDIUM": "#f59e0b", "LOW": "#00e5a0"}
    fig2 = px.pie(
        names=list(risk_data.keys()), values=list(risk_data.values()),
        color=list(risk_data.keys()), color_discrete_map=RISK_COLOR_V2,
        hole=0.6,
    )
    fig2.update_traces(
        textfont=dict(family="DM Sans", size=12, color="#94a3b8"),
        hovertemplate="<b>%{label}</b><br>%{value:,} threats<br>%{percent}<extra></extra>",
        marker=dict(line=dict(color="rgba(4,8,15,0.8)", width=2)),
    )
    layout2 = chart_layout(height=320)
    layout2["showlegend"] = True
    layout2["legend"] = dict(
        font=dict(family="DM Sans", size=12, color="#94a3b8"),
        bgcolor="rgba(0,0,0,0)",
        orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5,
    )
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True)

# ── Threat Categories Overview ────────────────────────────────────────────────
st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
st.markdown("#### 🗂️ Threat Categories")

RISK_COLOR_V2 = {"HIGH": "#f43f5e", "MEDIUM": "#f59e0b", "LOW": "#00e5a0"}
cols = st.columns(4)
card_idx = 0
for threat, desc in THREAT_DESCRIPTIONS.items():
    if threat == "all":
        continue
    risk  = RISK_MAP[threat]
    color = RISK_COLOR_V2[risk]
    icon  = THREAT_ICONS[threat]
    count = stats["type_counts"].get(threat, 0)
    with cols[card_idx % 4]:
        st.markdown(f"""<div class="cw-threat-card" style="--card-accent:{color}40">
            <div style="font-size:1.5rem;margin-bottom:10px">{icon}</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:#e2e8f0;font-size:0.9rem;margin-bottom:5px">{threat.upper()}</div>
            <div style="color:#475569;font-size:0.75rem;line-height:1.5;margin-bottom:14px;font-family:'DM Sans',sans-serif">{desc}</div>
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="color:{color};font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem">{count:,}</span>
                <span style="background:{color}15;color:{color};padding:3px 11px;border-radius:12px;font-size:0.68rem;font-weight:700;letter-spacing:0.8px;border:1px solid {color}30;font-family:'DM Sans',sans-serif">{risk}</span>
            </div>
        </div>""", unsafe_allow_html=True)
    card_idx += 1

# ── Recent High-Risk Alerts ───────────────────────────────────────────────────
st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
st.markdown("#### 🚨 Recent High-Risk Alerts")

high_df = df[df["type"].isin(["ransomware", "leak", "0day"])].head(8)
for _, row in high_df.iterrows():
    risk  = RISK_MAP.get(row["type"], "LOW")
    color = RISK_COLOR_V2.get(risk, "#f43f5e")
    icon  = THREAT_ICONS.get(row["type"], "📡")
    st.markdown(f"""<div class="cw-alert-row" style="--row-color:{color}">
        <span style="font-size:1.3rem">{icon}</span>
        <div style="flex:1;min-width:0;color:#cbd5e1;font-size:0.85rem;line-height:1.5;font-family:'DM Sans',sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{str(row['text'])[:130]}</div>
        <span style="background:{color}12;color:{color};padding:4px 13px;border-radius:14px;font-size:0.68rem;font-weight:700;letter-spacing:0.8px;flex-shrink:0;border:1px solid {color}25;font-family:'DM Sans',sans-serif">{row['type'].upper()}</span>
    </div>""", unsafe_allow_html=True)

render_footer()
