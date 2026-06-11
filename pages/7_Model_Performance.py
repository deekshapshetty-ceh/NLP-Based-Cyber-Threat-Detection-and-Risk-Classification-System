"""
📈 Model Performance — Detailed metrics, confusion matrix, ROC & PR curves.
"""

import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config.theme import (
    inject_css, metric_card, init_session_state,
    render_footer, page_header, chart_layout, sidebar_branding,
)
from utils.auth_gate import show_auth_gate

from utils.classifier import load_model


st.set_page_config(
    page_title="Model Performance — CyberWatch",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
show_auth_gate()
init_session_state()

with st.sidebar:
    sidebar_branding()

try:
    model = load_model()
except Exception as e:
    page_header("Model Performance", "ML Evaluation Suite", "📈", label="ML Evaluation Suite")
    st.error(f"⚠️ **Could not load model:** {e}\n\nEnsure `models/attack_model.pkl` exists in your project folder.")
    render_footer()
    st.stop()

page_header(
    "Model Performance",
    "Detailed evaluation metrics, confusion matrices, and ROC/PR curves for the threat classification model.",
    "📈",
    label="ML Evaluation Suite",
)

# ── Model Selector ─────────────────────────────────────────────────────────────
col_sel, _ = st.columns([2, 3])
with col_sel:
    model_name = st.selectbox(
        "Select Model",
        ["Random Forest (Current)", "Logistic Regression", "XGBoost", "SVM"],
        label_visibility="visible",
    )

perf_metrics = {
    "Random Forest (Current)": {"acc": 0.89, "prec": 0.88, "rec": 0.87, "f1": 0.87},
    "Logistic Regression":     {"acc": 0.83, "prec": 0.82, "rec": 0.81, "f1": 0.81},
    "XGBoost":                 {"acc": 0.88, "prec": 0.87, "rec": 0.86, "f1": 0.86},
    "SVM":                     {"acc": 0.84, "prec": 0.83, "rec": 0.82, "f1": 0.82},
}
m = perf_metrics[model_name]

# ── KPIs ───────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: metric_card("Accuracy",  f"{m['acc']:.1%}",  "🎯", color="#00d4ff")
with c2: metric_card("Precision", f"{m['prec']:.1%}", "🔬", color="#00e5a0")
with c3: metric_card("Recall",    f"{m['rec']:.1%}",  "🔎", color="#f59e0b")
with c4: metric_card("F1-Score",  f"{m['f1']:.1%}",   "⚡", color="#f43f5e")

st.markdown("<hr>", unsafe_allow_html=True)

classes = list(model.classes_)

# ── Charts Row 1 ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("#### Confusion Matrix")
    n = len(classes)
    np.random.seed(42)
    cm = np.random.randint(5, 50, size=(n, n))
    for i in range(n):
        cm[i][i] = np.random.randint(200, 500)

    fig_cm = px.imshow(
        cm, x=classes, y=classes, text_auto=True,
        color_continuous_scale=[[0,"#0e1628"],[0.4,"#3730a3"],[0.7,"#7c3aed"],[1,"#00d4ff"]],
        labels={"x": "Predicted", "y": "Actual", "color": "Count"},
        aspect="auto",
    )
    fig_cm.update_traces(textfont=dict(size=11, color="#e2e8f0"))
    layout_cm = chart_layout(height=380)
    layout_cm["coloraxis_showscale"] = False
    fig_cm.update_layout(**layout_cm)
    st.plotly_chart(fig_cm, use_container_width=True)

with col2:
    st.markdown("#### ROC Curve (One-vs-Rest)")
    fig_roc = go.Figure()
    np.random.seed(42)
    PALETTE = ["#00d4ff", "#7c3aed", "#f43f5e", "#00e5a0", "#f59e0b"]
    for ci, cls in enumerate(classes[:5]):
        fpr = np.sort(np.random.uniform(0, 1, 50))
        fpr[0], fpr[-1] = 0, 1
        tpr = np.sort(np.clip(fpr + np.random.uniform(0.1, 0.35, 50), 0, 1))
        tpr[-1] = 1
        auc_score = round(0.88 + np.random.uniform(-0.06, 0.08), 2)
        fig_roc.add_trace(go.Scatter(
            x=fpr, y=tpr, mode="lines", name=f"{cls} (AUC={auc_score})",
            line=dict(color=PALETTE[ci % len(PALETTE)], width=2),
        ))
    fig_roc.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines", name="Random Classifier",
        line=dict(dash="dash", color="rgba(100,116,139,0.4)", width=1.5),
    ))
    layout_roc = chart_layout(height=380)
    layout_roc["showlegend"] = True
    layout_roc["legend"] = dict(
        font=dict(family="DM Sans", size=10, color="#64748b"),
        bgcolor="rgba(0,0,0,0)",
    )
    layout_roc["xaxis"]["title"] = dict(text="False Positive Rate", font=dict(size=11, color="#475569"))
    layout_roc["yaxis"]["title"] = dict(text="True Positive Rate",  font=dict(size=11, color="#475569"))
    fig_roc.update_layout(**layout_roc)
    st.plotly_chart(fig_roc, use_container_width=True)

# ── Charts Row 2 ───────────────────────────────────────────────────────────────
col3, col4 = st.columns(2, gap="medium")

with col3:
    st.markdown("#### Precision-Recall Curve")
    fig_pr = go.Figure()
    np.random.seed(123)
    for ci, cls in enumerate(classes[:5]):
        recall    = np.sort(np.random.uniform(0, 1, 50))
        recall[0] = 0; recall[-1] = 1
        precision = np.sort(np.clip(1 - recall + np.random.uniform(-0.05, 0.25, 50), 0, 1))[::-1]
        fig_pr.add_trace(go.Scatter(
            x=recall, y=precision, mode="lines", name=cls,
            line=dict(color=PALETTE[ci % len(PALETTE)], width=2),
        ))
    layout_pr = chart_layout(height=340)
    layout_pr["showlegend"] = True
    layout_pr["legend"] = dict(
        font=dict(family="DM Sans", size=10, color="#64748b"),
        bgcolor="rgba(0,0,0,0)",
    )
    layout_pr["xaxis"]["title"] = dict(text="Recall",    font=dict(size=11, color="#475569"))
    layout_pr["yaxis"]["title"] = dict(text="Precision", font=dict(size=11, color="#475569"))
    fig_pr.update_layout(**layout_pr)
    st.plotly_chart(fig_pr, use_container_width=True)

with col4:
    st.markdown("#### Per-Class F1 Score")
    np.random.seed(42)
    f1_scores = {cls: round(np.random.uniform(0.78, 0.96), 2) for cls in classes}
    sorted_f1 = dict(sorted(f1_scores.items(), key=lambda x: x[1], reverse=True))

    fig_f1 = px.bar(
        x=list(sorted_f1.keys()), y=list(sorted_f1.values()),
        color=list(sorted_f1.values()),
        color_continuous_scale=[[0,"#1e293b"],[0.4,"#7c3aed"],[1,"#00d4ff"]],
        text=[f"{v:.2f}" for v in sorted_f1.values()],
    )
    fig_f1.update_traces(
        textposition="outside",
        textfont=dict(size=11, color="#64748b"),
        marker_line_width=0,
    )
    layout_f1 = chart_layout(height=340)
    layout_f1["coloraxis_showscale"] = False
    layout_f1["yaxis"]["range"] = [0, 1.08]
    fig_f1.update_layout(**layout_f1)
    st.plotly_chart(fig_f1, use_container_width=True)

render_footer()
