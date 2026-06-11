"""
📋 Action Tracker — SOC incident response task management.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from config.theme import (
    inject_css, init_session_state, render_footer,
    page_header, metric_card, chart_layout, sidebar_branding,
)
from utils.auth_gate import show_auth_gate

import json, os

def _save_tracker(tasks: list):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "action_tracker.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(tasks, f, indent=2)

def _load_tracker() -> list:
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "action_tracker.json")
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


st.set_page_config(
    page_title="Action Tracker — CyberWatch",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
show_auth_gate()


init_session_state()
if "action_tracker" not in st.session_state:
    st.session_state.action_tracker = _load_tracker()

with st.sidebar:
    sidebar_branding()

STATUS_COLORS = {
    "Pending":     "#f43f5e",
    "In Progress": "#f59e0b",
    "Completed":   "#00e5a0",
}
PRIORITY_COLORS = {
    "Critical": "#f43f5e",
    "High":     "#f59e0b",
    "Medium":   "#00d4ff",
    "Low":      "#94a3b8",
}

page_header(
    "Action Tracker",
    "Track, prioritize, and manage security incident response tasks across your SOC team.",
    "📋",
    label="Incident Response",
)

# ── If tasks exist ─────────────────────────────────────────────────────────────
if st.session_state.action_tracker:
    tracker_df = pd.DataFrame(st.session_state.action_tracker)

    # Summary KPIs
    total     = len(tracker_df)
    pending   = len(tracker_df[tracker_df["Status"] == "Pending"])   if "Status"   in tracker_df.columns else 0
    critical  = len(tracker_df[tracker_df["Priority"] == "Critical"]) if "Priority" in tracker_df.columns else 0
    completed = len(tracker_df[tracker_df["Status"] == "Completed"]) if "Status"   in tracker_df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Total Tasks",   f"{total}",     "📋", color="#00d4ff")
    with c2: metric_card("Pending",       f"{pending}",   "⏳", color="#f43f5e")
    with c3: metric_card("Critical",      f"{critical}",  "🚨", color="#f43f5e")
    with c4: metric_card("Completed",     f"{completed}", "✅", color="#00e5a0")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Status chart + table
    col_chart, col_table = st.columns([1, 2], gap="medium")

    with col_chart:
        if "Status" in tracker_df.columns:
            st.markdown("#### Task Status")
            status_counts = tracker_df["Status"].value_counts()
            fig = px.pie(
                names=status_counts.index, values=status_counts.values,
                color=status_counts.index,
                color_discrete_map=STATUS_COLORS,
                hole=0.55,
            )
            fig.update_traces(
                marker=dict(line=dict(color="rgba(6,9,18,0.8)", width=2)),
                hovertemplate="<b>%{label}</b><br>%{value} tasks<extra></extra>",
            )
            layout = chart_layout(height=260)
            layout["showlegend"] = True
            layout["legend"] = dict(
                font=dict(family="DM Sans", size=11, color="#94a3b8"),
                bgcolor="rgba(0,0,0,0)", orientation="v",
                yanchor="middle", y=0.5, xanchor="left", x=1.0,
            )
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("#### All Tasks")
        st.dataframe(tracker_df, hide_index=True, use_container_width=True, height=280)

    # Actions
    col_dl, col_clear = st.columns(2)
    with col_dl:
        st.download_button(
            "📥 Export Tracker CSV",
            tracker_df.to_csv(index=False),
            "action_tracker.csv",
            "text/csv",
            use_container_width=True,
        )
    with col_clear:
        if st.button("🗑️ Clear All Tasks", use_container_width=True):
            st.session_state.action_tracker = []
            _save_tracker([])
            st.rerun()

else:
    st.markdown("""
    <div style="background:rgba(14,22,40,0.5);border:1px solid rgba(0,212,255,0.08);
                border-radius:16px;padding:40px;text-align:center;margin:20px 0">
        <div style="font-size:3rem;margin-bottom:16px;opacity:0.4">📋</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
                    color:#f0f4fa;margin-bottom:8px">No tasks yet</div>
        <div style="color:#475569;font-size:0.88rem;max-width:400px;margin:0 auto;
                    font-family:'DM Sans',sans-serif;line-height:1.6">
            Add threats from <strong style="color:#00d4ff">Threat Prediction</strong>,
            <strong style="color:#00d4ff">Analytics</strong>, or
            <strong style="color:#00d4ff">Alert Center</strong>
            to populate this tracker.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Manual Task Entry ──────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("#### ➕ Add Manual Task")

with st.container():
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        manual_threat = st.text_input("Threat Description", placeholder="Describe the incident…")
    with mc2:
        manual_owner = st.text_input("Owner", value="SOC Analyst")
    with mc3:
        manual_priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])

    mc4, mc5 = st.columns(2)
    with mc4:
        manual_type = st.selectbox(
            "Threat Type",
            ["ransomware", "leak", "0day", "ddos", "botnet", "vulnerability", "general", "manual"],
        )
    with mc5:
        manual_status = st.selectbox("Initial Status", ["Pending", "In Progress", "Completed"])

    if st.button("➕ Add Task", type="primary"):
        if manual_threat:
            st.session_state.action_tracker.append({
                "Threat":   manual_threat,
                "Type":     manual_type,
                "Owner":    manual_owner,
                "Priority": manual_priority,
                "Status":   manual_status,
                "Date":     datetime.now().strftime("%Y-%m-%d"),
            })
            _save_tracker(st.session_state.action_tracker)
            st.success("✅ Task added successfully!")
            st.rerun()
        else:
            st.warning("Please enter a threat description.")

render_footer()
