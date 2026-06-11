"""
📊 Analytics — Dashboard charts and high-risk auto-alerts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from config.theme import (
    inject_css, metric_card, init_session_state,
    render_footer, page_header, chart_layout, sidebar_branding,
)
from utils.auth_gate import show_auth_gate

from config.constants import RISK_MAP
from utils.data_loader import load_data, get_stats
from utils.classifier import load_model, load_vectorizer


st.set_page_config(
    page_title="Analytics — CyberWatch",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
show_auth_gate()


init_session_state()

with st.sidebar:
    sidebar_branding()

df    = load_data()
stats = get_stats(df)
tc    = stats["type_counts"]

RISK_COLOR_V2 = {"HIGH": "#f43f5e", "MEDIUM": "#f59e0b", "LOW": "#00e5a0"}

page_header(
    "Analytics",
    "Comprehensive threat distribution, risk breakdown, model confidence, and live data insights.",
    "📊",
    label="Intelligence Dashboard",
)

# ── KPIs ───────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: metric_card("Total Analyzed",  f"{stats['total']:,}",      "📄", color="#00d4ff")
with c2: metric_card("High-Risk",       f"{stats['high_risk']:,}",  "🔴", color="#f43f5e")
with c3: metric_card("Medium-Risk",     f"{stats['medium_risk']:,}","🟡", color="#f59e0b")
with c4: metric_card("Low-Risk",        f"{stats['low_risk']:,}",   "🟢", color="#00e5a0")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ── Charts Row 1 ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("#### Threat Type Distribution")
    fig1 = px.bar(
        x=list(tc.keys()), y=list(tc.values()),
        color=list(tc.values()),
        color_continuous_scale=[[0,"#1e293b"],[0.5,"#7c3aed"],[1,"#00d4ff"]],
        labels={"x": "Threat Type", "y": "Count"},
        text=list(tc.values()),
    )
    fig1.update_traces(
        texttemplate="%{text:,}", textposition="outside",
        textfont=dict(size=10, color="#64748b"),
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>%{y:,} entries<extra></extra>",
    )
    layout1 = chart_layout(height=340)
    layout1["coloraxis_showscale"] = False
    fig1.update_layout(**layout1)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("#### Risk Level Breakdown")
    risk_data = {"HIGH": stats["high_risk"], "MEDIUM": stats["medium_risk"], "LOW": stats["low_risk"]}
    fig2 = px.pie(
        names=list(risk_data.keys()), values=list(risk_data.values()),
        color=list(risk_data.keys()), color_discrete_map=RISK_COLOR_V2,
        hole=0.58,
    )
    fig2.update_traces(
        hovertemplate="<b>%{label}</b><br>%{value:,} threats<br>%{percent}<extra></extra>",
        marker=dict(line=dict(color="rgba(6,9,18,0.8)", width=2)),
    )
    layout2 = chart_layout(height=340)
    layout2["showlegend"] = True
    layout2["legend"] = dict(
        font=dict(family="DM Sans", size=12, color="#94a3b8"),
        bgcolor="rgba(0,0,0,0)", orientation="h",
        yanchor="bottom", y=-0.12, xanchor="center", x=0.5,
    )
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ───────────────────────────────────────────────────────────────
col3, col4 = st.columns(2, gap="medium")

with col3:
    st.markdown("#### Threat Types by Risk Level")
    df_risk = pd.DataFrame({"Type": list(RISK_MAP.keys()), "Risk": list(RISK_MAP.values())})
    df_risk["Count"] = df_risk["Type"].map(tc).fillna(0).astype(int)
    fig3 = px.bar(
        df_risk, x="Type", y="Count", color="Risk",
        color_discrete_map=RISK_COLOR_V2, barmode="group",
    )
    fig3.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{x}</b> (%{data.name})<br>%{y:,}<extra></extra>",
    )
    layout3 = chart_layout(height=320)
    layout3["showlegend"] = True
    layout3["legend"] = dict(
        font=dict(family="DM Sans", size=11, color="#64748b"),
        bgcolor="rgba(0,0,0,0)", title=None,
    )
    fig3.update_layout(**layout3)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("#### Model Confidence Distribution")
    import numpy as np

    @st.cache_data(show_spinner=False)
    def _compute_confidence_dist(_df):
        """Run 500 predictions once and cache — avoids re-running on every widget interaction."""
        _model = load_model()
        _vectorizer = load_vectorizer()
        sample_texts = _df.sample(min(500, len(_df)), random_state=42)["text"].tolist()
        vecs = _vectorizer.transform(sample_texts)
        probs = _model.predict_proba(vecs)
        return [round(float(max(p)) * 100, 1) for p in probs]

    confs = _compute_confidence_dist(df)

    fig4 = px.histogram(
        x=confs, nbins=30,
        labels={"x": "Confidence %", "y": "Frequency"},
        color_discrete_sequence=["#7c3aed"],
    )
    fig4.update_traces(
        marker_line_width=0,
        hovertemplate="Confidence: %{x}%<br>Count: %{y}<extra></extra>",
    )
    layout4 = chart_layout(height=320)
    fig4.update_layout(**layout4)
    st.plotly_chart(fig4, use_container_width=True)

# ── High-Risk Alerts Table ─────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
    <span style="font-size:1.3rem">🚨</span>
    <div>
        <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#f0f4fa">
            Auto High-Risk Alerts
        </div>
        <div style="font-size:0.82rem;color:#475569;font-family:'DM Sans',sans-serif">
            Entries automatically flagged as HIGH risk from the dataset
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

high_risk_df = df[df["type"].isin(["ransomware", "leak", "0day"])].head(100).copy()
high_risk_df["Risk"] = high_risk_df["type"].map(RISK_MAP)
high_risk_df = high_risk_df[["text", "type", "Risk"]].rename(
    columns={"text": "Tweet", "type": "Threat Type"}
)
st.dataframe(high_risk_df, hide_index=True, use_container_width=True, height=340)

col_dl, col_add = st.columns(2)
with col_dl:
    csv = high_risk_df.to_csv(index=False)
    st.download_button(
        "📥 Download High-Risk Report",
        csv, "high_risk_threats.csv", "text/csv",
        use_container_width=True,
    )
with col_add:
    if st.button("➕ Add All to Action Tracker", use_container_width=True):
        for _, row in high_risk_df.iterrows():
            st.session_state.action_tracker.append({
                "Threat":   row["Tweet"][:80],
                "Type":     row["Threat Type"],
                "Owner":    "SOC Analyst",
                "Priority": "Critical",
                "Status":   "Pending",
                "Date":     datetime.now().strftime("%Y-%m-%d"),
            })
        st.success(f"✅ Added {len(high_risk_df)} threats to Action Tracker!")

render_footer()
