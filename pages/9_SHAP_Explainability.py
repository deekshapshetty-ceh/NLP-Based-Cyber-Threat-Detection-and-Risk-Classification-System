"""
🧩 SHAP Explainability — Understand why the model made a prediction.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from config.theme import (
    inject_css, init_session_state, render_footer,
    page_header, severity_badge, chart_layout, sidebar_branding,
)
from utils.auth_gate import show_auth_gate

from utils.classifier import load_model, load_vectorizer, classify_text


st.set_page_config(
    page_title="SHAP Explainability — CyberWatch",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
show_auth_gate()


init_session_state()

with st.sidebar:
    sidebar_branding()

model      = load_model()
vectorizer = load_vectorizer()

page_header(
    "SHAP Explainability",
    "Understand why the model made a specific prediction. Global feature impact and per-text local explanations.",
    "🧩",
    label="Model Interpretability",
)

tab1, tab2 = st.tabs(["🌍 Global Explainability", "🔬 Local Explainability"])

# ── Global ─────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("""
    <div style="color:#64748b;font-size:0.88rem;margin-bottom:20px;
                font-family:'DM Sans',sans-serif;line-height:1.6">
        Shows which TF-IDF terms most consistently influence the model's predictions across all classes.
        Higher impact means the word strongly shifts model confidence when it appears in text.
    </div>
    """, unsafe_allow_html=True)

    if hasattr(model, "feature_importances_"):
        feature_names = vectorizer.get_feature_names_out()
        importances   = model.feature_importances_
        top_idx       = np.argsort(importances)[-15:][::-1]

        col_g1, col_g2 = st.columns(2, gap="medium")

        with col_g1:
            st.markdown("#### Global Feature Impact (Top 15)")
            fig_global = px.bar(
                x=[importances[i] for i in top_idx],
                y=[feature_names[i] for i in top_idx[::-1][::-1]],
                orientation="h",
                color=[importances[i] for i in top_idx],
                color_continuous_scale=[[0,"#1e293b"],[0.4,"#7c3aed"],[1,"#00d4ff"]],
                labels={"x": "Mean Impact", "y": ""},
                text=[f"{importances[i]:.5f}" for i in top_idx],
            )
            fig_global.update_traces(
                textposition="outside",
                textfont=dict(size=9, color="#475569"),
                marker_line_width=0,
                hovertemplate="<b>%{y}</b><br>Impact: %{x:.6f}<extra></extra>",
            )
            layout_g = chart_layout(height=440)
            layout_g["coloraxis_showscale"] = False
            layout_g["yaxis"]["autorange"] = "reversed"
            layout_g["margin"]["l"] = 120
            fig_global.update_layout(**layout_g)
            st.plotly_chart(fig_global, use_container_width=True)

        with col_g2:
            st.markdown("#### SHAP Summary Plot (Simulated)")
            np.random.seed(42)
            dot_data = []
            for idx in top_idx:
                for _ in range(40):
                    dot_data.append({
                        "Feature":       feature_names[idx],
                        "SHAP Value":    np.random.normal(importances[idx], importances[idx] * 0.3),
                        "Feature Value": np.random.uniform(0, 1),
                    })
            dot_df = pd.DataFrame(dot_data)

            fig_dot = px.scatter(
                dot_df, x="SHAP Value", y="Feature",
                color="Feature Value",
                color_continuous_scale="RdBu_r",
                opacity=0.65,
            )
            fig_dot.update_traces(
                marker=dict(size=7, line=dict(width=0)),
                hovertemplate="<b>%{y}</b><br>SHAP: %{x:.4f}<extra></extra>",
            )
            layout_d = chart_layout(height=440)
            layout_d["yaxis"]["autorange"] = "reversed"
            layout_d["margin"]["l"] = 120
            layout_d["coloraxis_showscale"] = True
            layout_d["coloraxis_colorbar"] = dict(
                title=dict(text="Feature Value", font=dict(size=10, color="#64748b")),
                tickfont=dict(size=10, color="#64748b"),
                len=0.6,
            )
            fig_dot.update_layout(**layout_d)
            st.plotly_chart(fig_dot, use_container_width=True)
    else:
        st.info("Global SHAP requires a tree-based model with `feature_importances_`.")

# ── Local ──────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div style="color:#64748b;font-size:0.88rem;margin-bottom:20px;
                font-family:'DM Sans',sans-serif;line-height:1.6">
        Enter any text to see which individual words most contributed to the classification decision.
        Impact score = TF-IDF weight × feature importance.
    </div>
    """, unsafe_allow_html=True)

    shap_text = st.text_area(
        "Text to explain:",
        height=110,
        value="Critical ransomware attack encrypts hospital records demanding bitcoin payment",
        key="shap_input",
        label_visibility="collapsed",
    )

    col_btn, _ = st.columns([1, 3])
    with col_btn:
        explain_clicked = st.button("🔍 Explain Prediction", type="primary", use_container_width=True)

    if explain_clicked:
        if shap_text.strip():
            with st.spinner("Computing word-level impact scores…"):
                result = classify_text(shap_text)
                vec    = vectorizer.transform([shap_text])

            # Prediction banner
            risk_color_map = {"HIGH": "#f43f5e", "MEDIUM": "#f59e0b", "LOW": "#00e5a0"}
            color = risk_color_map.get(result["risk_level"], "#00e5a0")
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{color}08,{color}03);
                        border:1px solid {color}20;border-radius:14px;padding:18px 22px;
                        margin-bottom:20px;display:flex;align-items:center;gap:14px">
                <span style="font-size:2rem;filter:drop-shadow(0 0 8px {color}60)">{result['icon']}</span>
                <div>
                    <span style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;
                                 color:#f0f4fa">{result['threat_type'].upper()}</span>
                    &nbsp;·&nbsp;
                    {severity_badge(result['risk_level'])}
                    &nbsp;·&nbsp;
                    <span style="color:#64748b;font-size:0.85rem;font-family:'DM Sans',sans-serif">
                        <strong style="color:{color}">{result['confidence']}%</strong> confidence
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            feature_names = vectorizer.get_feature_names_out()
            importances   = (
                model.feature_importances_
                if hasattr(model, "feature_importances_")
                else np.zeros(len(feature_names))
            )

            nonzero_idx  = vec.nonzero()[1]
            word_impacts = []
            for idx in nonzero_idx:
                word_impacts.append({
                    "Word":               feature_names[idx],
                    "TF-IDF Weight":      round(float(vec[0, idx]), 4),
                    "Feature Importance": round(float(importances[idx]), 6),
                    "Impact Score":       round(float(vec[0, idx]) * float(importances[idx]), 6),
                })

            if word_impacts:
                impact_df = pd.DataFrame(word_impacts).sort_values("Impact Score", ascending=False)
                top_words = impact_df.head(20)

                col_chart, col_table = st.columns([3, 2], gap="medium")

                with col_chart:
                    st.markdown("#### Word-Level Impact Scores")
                    fig_local = px.bar(
                        x=top_words["Impact Score"].iloc[::-1],
                        y=top_words["Word"].iloc[::-1],
                        orientation="h",
                        color=top_words["Impact Score"].iloc[::-1],
                        color_continuous_scale=[[0,"#1e293b"],[0.4,"#7c3aed"],[1,"#00d4ff"]],
                        labels={"x": "Impact Score", "y": ""},
                        text=[f"{v:.5f}" for v in top_words["Impact Score"].iloc[::-1]],
                    )
                    fig_local.update_traces(
                        textposition="outside",
                        textfont=dict(size=9, color="#475569"),
                        marker_line_width=0,
                        hovertemplate="<b>%{y}</b><br>Impact: %{x:.6f}<extra></extra>",
                    )
                    layout_l = chart_layout(height=440)
                    layout_l["coloraxis_showscale"] = False
                    layout_l["margin"]["l"] = 100
                    fig_local.update_layout(**layout_l)
                    st.plotly_chart(fig_local, use_container_width=True)

                with col_table:
                    st.markdown("#### Detailed Breakdown")
                    st.dataframe(
                        impact_df.head(30).style.format({
                            "TF-IDF Weight":      "{:.4f}",
                            "Feature Importance": "{:.6f}",
                            "Impact Score":       "{:.6f}",
                        }),
                        hide_index=True,
                        use_container_width=True,
                        height=440,
                    )
            else:
                st.info("No matching features found in the vocabulary for this text.")
        else:
            st.warning("Please enter text to explain.")

render_footer()
