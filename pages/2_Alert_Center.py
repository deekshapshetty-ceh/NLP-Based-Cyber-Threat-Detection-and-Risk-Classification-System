"""
🚨 Alert Center — High-risk threats requiring SOC attention.
"""

import streamlit as st
from datetime import datetime

from config.theme import (
    inject_css, severity_badge, init_session_state,
    render_footer, page_header, sidebar_branding,
)
from utils.auth_gate import show_auth_gate

from config.constants import RISK_MAP, THREAT_ICONS
from utils.data_loader import load_data


st.set_page_config(
    page_title="Alert Center — CyberWatch",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
show_auth_gate()


init_session_state()

with st.sidebar:
    sidebar_branding()

df = load_data()

page_header(
    "Alert Center",
    "High-risk threats requiring immediate SOC attention. Triage and assign incidents below.",
    "🚨",
    label="Security Operations Center",
)

# ── Summary strip ──────────────────────────────────────────────────────────────
high_risk_df = df[df["type"].isin(["ransomware", "leak", "0day"])]
sample = high_risk_df.sample(min(20, len(high_risk_df)), random_state=42)

RISK_COLOR_V2 = {"HIGH": "#f43f5e", "MEDIUM": "#f59e0b", "LOW": "#00e5a0"}

col_a, col_b, col_c = st.columns(3)
with col_a:
    ransomware_count = len(df[df["type"] == "ransomware"])
    st.markdown(f"""
    <div style="background:rgba(244,63,94,0.06);border:1px solid rgba(244,63,94,0.18);
                border-radius:12px;padding:16px 20px;text-align:center">
        <div style="font-size:1.5rem;margin-bottom:6px">🔒</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#f43f5e">{ransomware_count:,}</div>
        <div style="font-size:0.7rem;letter-spacing:1.5px;text-transform:uppercase;
                    color:#475569;font-family:'DM Sans',sans-serif;font-weight:600">Ransomware</div>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    leak_count = len(df[df["type"] == "leak"])
    st.markdown(f"""
    <div style="background:rgba(244,63,94,0.06);border:1px solid rgba(244,63,94,0.18);
                border-radius:12px;padding:16px 20px;text-align:center">
        <div style="font-size:1.5rem;margin-bottom:6px">💧</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#f43f5e">{leak_count:,}</div>
        <div style="font-size:0.7rem;letter-spacing:1.5px;text-transform:uppercase;
                    color:#475569;font-family:'DM Sans',sans-serif;font-weight:600">Data Leaks</div>
    </div>
    """, unsafe_allow_html=True)
with col_c:
    zeroday_count = len(df[df["type"] == "0day"])
    st.markdown(f"""
    <div style="background:rgba(244,63,94,0.06);border:1px solid rgba(244,63,94,0.18);
                border-radius:12px;padding:16px 20px;text-align:center">
        <div style="font-size:1.5rem;margin-bottom:6px">⚠️</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#f43f5e">{zeroday_count:,}</div>
        <div style="font-size:0.7rem;letter-spacing:1.5px;text-transform:uppercase;
                    color:#475569;font-family:'DM Sans',sans-serif;font-weight:600">Zero-Days</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown(f"#### Active Alerts — {len(sample)} incidents")

# ── Alert Cards ────────────────────────────────────────────────────────────────
for i, (_, row) in enumerate(sample.iterrows()):
    risk  = RISK_MAP.get(row["type"], "LOW")
    icon  = THREAT_ICONS.get(row["type"], "📡")
    color = RISK_COLOR_V2.get(risk, "#f43f5e")

    with st.expander(
        f"{icon}  [{risk}]  {row['type'].upper()} — {str(row['text'])[:75]}…",
        expanded=(i < 2),
    ):
        col_text, col_actions = st.columns([3, 1])

        with col_text:
            st.markdown(f"""
            <div style="background:rgba(14,22,40,0.5);border:1px solid rgba(255,255,255,0.05);
                        border-radius:12px;padding:16px 20px;margin-bottom:12px">
                <div style="font-size:0.65rem;letter-spacing:2px;text-transform:uppercase;
                            color:#334155;font-weight:700;margin-bottom:8px;
                            font-family:'DM Sans',sans-serif">Full Text</div>
                <div style="color:#94a3b8;font-size:0.88rem;line-height:1.7;
                            font-family:'DM Sans',sans-serif">{str(row['text'])[:400]}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(
                f"**Threat Type:** `{row['type']}` &nbsp;·&nbsp; **Risk Level:** {severity_badge(risk)}",
                unsafe_allow_html=True,
            )

        with col_actions:
            st.markdown("""
            <div style="font-size:0.65rem;letter-spacing:2px;text-transform:uppercase;
                        color:#334155;font-weight:700;margin-bottom:12px;
                        font-family:'DM Sans',sans-serif">Actions</div>
            """, unsafe_allow_html=True)

            if st.button("📧 Send Alert", key=f"alert_email_{i}", use_container_width=True):
                st.success("Alert email dispatched!")
            if st.button("📅 Schedule Review", key=f"alert_schedule_{i}", use_container_width=True):
                st.success("Review scheduled!")
            if st.button("➕ Track Incident", key=f"alert_track_{i}", use_container_width=True):
                st.session_state.action_tracker.append({
                    "Threat":   str(row["text"])[:80],
                    "Type":     row["type"],
                    "Owner":    "SOC Lead",
                    "Priority": "Critical",
                    "Status":   "Pending",
                    "Date":     datetime.now().strftime("%Y-%m-%d"),
                })
                st.success("Added to tracker!")

render_footer()
