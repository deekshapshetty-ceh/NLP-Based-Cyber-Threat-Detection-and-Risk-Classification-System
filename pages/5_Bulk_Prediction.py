"""
📦 Bulk Prediction — Upload CSV for batch threat classification.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from config.theme import (
    inject_css, init_session_state, render_footer,
    page_header, metric_card, chart_layout, sidebar_branding,
)
from utils.auth_gate import show_auth_gate

from config.constants import RISK_MAP
from utils.classifier import batch_classify


st.set_page_config(
    page_title="Bulk Prediction — CyberWatch",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
show_auth_gate()


init_session_state()

with st.sidebar:
    sidebar_branding()

RISK_COLOR_V2 = {"HIGH": "#f43f5e", "MEDIUM": "#f59e0b", "LOW": "#00e5a0"}

page_header(
    "Bulk Prediction",
    "Upload a CSV with a 'text' column to classify multiple entries at once. Download enriched results when done.",
    "📦",
    label="Batch Classification Engine",
)

# ── Instructions + Template ────────────────────────────────────────────────────
col_info, col_dl = st.columns([3, 1], gap="medium")

with col_info:
    st.markdown("""
    <div style="background:rgba(14,22,40,0.6);border:1px solid rgba(0,212,255,0.08);
                border-radius:14px;padding:20px 24px">
        <div style="font-size:0.65rem;letter-spacing:2px;text-transform:uppercase;
                    color:#334155;font-weight:700;margin-bottom:12px;
                    font-family:'DM Sans',sans-serif">◈ How it works</div>
        <div style="color:#64748b;font-size:0.88rem;line-height:1.8;font-family:'DM Sans',sans-serif">
            1. Download the CSV template (or prepare your own with a <code style="color:#00d4ff;background:rgba(0,212,255,0.08);padding:1px 6px;border-radius:4px">text</code> column)<br>
            2. Upload the file — the classifier will process each row<br>
            3. Review the enriched results table with threat type, risk level, and confidence<br>
            4. Export the annotated CSV for your SIEM or reporting workflows
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_dl:
    template_df = pd.DataFrame({"text": [
        "New ransomware variant targets healthcare sector",
        "DDoS attack floods major ISP servers",
        "Critical zero-day found in popular CMS",
        "Data leaked from government database",
        "Botnet infects IoT devices worldwide",
    ]})
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.download_button(
        "📄 Download Template",
        template_df.to_csv(index=False),
        "threat_template.csv",
        "text/csv",
        use_container_width=True,
    )

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── File Uploader ──────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Upload CSV file",
    type=["csv"],
    help="File must contain a 'text' column with entries to classify.",
    label_visibility="collapsed",
)

if uploaded:
    upload_df = pd.read_csv(uploaded)

    if "text" not in upload_df.columns:
        st.error("❌ CSV must have a `text` column. Download the template above for reference.")
    else:
        total = len(upload_df)
        st.markdown(f"""
        <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);
                    border-radius:10px;padding:12px 18px;margin-bottom:16px;
                    font-family:'DM Sans',sans-serif;font-size:0.9rem;color:#94a3b8">
            📁 <strong style="color:#00d4ff">{total:,} entries</strong> detected in uploaded file.
            Processing all rows…
        </div>
        """, unsafe_allow_html=True)

        progress_bar = st.progress(0, text="Running batch classifier…")
        texts = upload_df["text"].astype(str).tolist()

        with st.spinner("Classifying all entries in one pass…"):
            batch_results = batch_classify(texts)

        progress_bar.progress(1.0, text="Done!")
        progress_bar.empty()

        results = []
        for i, res in enumerate(batch_results):
            results.append({
                "Text":         texts[i][:120],
                "Threat Type":  res["threat_type"],
                "Risk Level":   res["risk_level"],
                "Confidence %": res["confidence"],
            })
        result_df = pd.DataFrame(results)

        # Summary metrics
        high_count   = len(result_df[result_df["Risk Level"] == "HIGH"])
        medium_count = len(result_df[result_df["Risk Level"] == "MEDIUM"])
        low_count    = len(result_df[result_df["Risk Level"] == "LOW"])
        avg_conf     = result_df["Confidence %"].mean()

        st.success(f"✅ Successfully classified {total:,} entries!")

        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("Total Classified", f"{total:,}",       "📦", color="#00d4ff")
        with c2: metric_card("High Risk",         f"{high_count:,}",  "🔴", color="#f43f5e")
        with c3: metric_card("Medium Risk",       f"{medium_count:,}","🟡", color="#f59e0b")
        with c4: metric_card("Avg Confidence",    f"{avg_conf:.1f}%", "📊", color="#7c3aed")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Results table
        st.markdown("#### Classification Results")
        st.dataframe(result_df, hide_index=True, use_container_width=True, height=360)

        # Charts
        col_pie, col_bar = st.columns(2, gap="medium")

        with col_pie:
            st.markdown("#### Risk Distribution")
            fig_pie = px.pie(
                result_df, names="Risk Level", color="Risk Level",
                color_discrete_map=RISK_COLOR_V2, hole=0.55,
            )
            fig_pie.update_traces(
                marker=dict(line=dict(color="rgba(6,9,18,0.8)", width=2)),
                hovertemplate="<b>%{label}</b><br>%{value} entries<extra></extra>",
            )
            layout_p = chart_layout(height=280)
            layout_p["showlegend"] = True
            layout_p["legend"] = dict(
                font=dict(family="DM Sans", size=11, color="#94a3b8"),
                bgcolor="rgba(0,0,0,0)", orientation="h",
                yanchor="bottom", y=-0.15, xanchor="center", x=0.5,
            )
            fig_pie.update_layout(**layout_p)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_bar:
            st.markdown("#### Threat Type Breakdown")
            type_counts = result_df["Threat Type"].value_counts().reset_index()
            type_counts.columns = ["Threat Type", "Count"]
            fig_bar2 = px.bar(
                type_counts, x="Threat Type", y="Count",
                color="Count",
                color_continuous_scale=[[0,"#1e293b"],[0.5,"#7c3aed"],[1,"#00d4ff"]],
            )
            fig_bar2.update_traces(marker_line_width=0)
            layout_b = chart_layout(height=280)
            layout_b["coloraxis_showscale"] = False
            fig_bar2.update_layout(**layout_b)
            st.plotly_chart(fig_bar2, use_container_width=True)

        # Export
        col_exp, _ = st.columns([1, 2])
        with col_exp:
            st.download_button(
                "📥 Download Results CSV",
                result_df.to_csv(index=False),
                "bulk_predictions.csv",
                "text/csv",
                use_container_width=True,
            )

render_footer()
