"""
📊 Feature Importance — Top features used by the model.
"""

import streamlit as st
import numpy as np
import plotly.express as px

from config.theme import (
    inject_css, init_session_state, render_footer,
    page_header, metric_card, chart_layout, sidebar_branding,
)
from utils.auth_gate import show_auth_gate

from utils.classifier import load_model, load_vectorizer


st.set_page_config(
    page_title="Feature Importance — CyberWatch",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
show_auth_gate()
init_session_state()

with st.sidebar:
    sidebar_branding()

try:
    model      = load_model()
    vectorizer = load_vectorizer()
except Exception as e:
    page_header("Feature Importance", "Model Interpretability", "🔑", label="Model Interpretability")
    st.error(f"⚠️ **Could not load model files:** {e}\n\nEnsure `models/attack_model.pkl` and `models/vectorizer.pkl` exist in your project folder.")
    render_footer()
    st.stop()

page_header(
    "Feature Importance",
    "Explore which TF-IDF terms drive the model's threat classification decisions.",
    "🔑",
    label="Model Interpretability",
)

if not hasattr(model, "feature_importances_"):
    st.warning(
        "The loaded model does not expose `feature_importances_`. "
        "Train a tree-based model (Random Forest, XGBoost) to view this page."
    )
else:
    importances   = model.feature_importances_
    feature_names = vectorizer.get_feature_names_out()

    # Quick stats
    total_features    = len(feature_names)
    nonzero_features  = int(np.count_nonzero(importances))
    max_importance    = float(max(importances))
    mean_importance   = float(np.mean(importances))

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Total Features",    f"{total_features:,}",    "📚", color="#00d4ff")
    with c2: metric_card("Non-zero Features", f"{nonzero_features:,}",  "✨", color="#7c3aed")
    with c3: metric_card("Max Importance",    f"{max_importance:.5f}",  "🏆", color="#00e5a0")
    with c4: metric_card("Mean Importance",   f"{mean_importance:.5f}", "📊", color="#f59e0b")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Slider
    col_ctrl, _ = st.columns([1, 3])
    with col_ctrl:
        n_top = st.slider(
            "Top features to display",
            min_value=10, max_value=50, value=25, step=5,
        )

    top_idx      = np.argsort(importances)[-n_top:][::-1]
    top_features = [feature_names[i] for i in top_idx]
    top_values   = [importances[i]   for i in top_idx]

    # Horizontal bar chart
    st.markdown(f"#### Top {n_top} TF-IDF Features by Importance")
    fig = px.bar(
        x=top_values[::-1],
        y=top_features[::-1],
        orientation="h",
        color=top_values[::-1],
        color_continuous_scale=[[0,"#1e293b"],[0.4,"#7c3aed"],[0.75,"#00d4ff"],[1,"#00e5a0"]],
        labels={"x": "Importance Score", "y": ""},
        text=[f"{v:.5f}" for v in top_values[::-1]],
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=9, color="#475569"),
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Importance: %{x:.6f}<extra></extra>",
    )
    height = max(400, n_top * 22)
    layout = chart_layout(height=height)
    layout["coloraxis_showscale"] = False
    layout["margin"]["l"] = 130
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)

    # Distribution of all importances
    st.markdown("#### Importance Score Distribution (All Features)")
    fig_hist = px.histogram(
        x=importances[importances > 0], nbins=60,
        labels={"x": "Importance Score", "y": "Feature Count"},
        color_discrete_sequence=["#7c3aed"],
    )
    fig_hist.update_traces(marker_line_width=0)
    layout_h = chart_layout(height=240)
    fig_hist.update_layout(**layout_h)
    st.plotly_chart(fig_hist, use_container_width=True)

render_footer()
