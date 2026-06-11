"""
🔍 Dataset Explorer — EDA and visualizations.
"""

import streamlit as st
import plotly.express as px

from config.theme import (
    inject_css, init_session_state, render_footer,
    page_header, chart_layout, sidebar_branding,
)
from utils.auth_gate import show_auth_gate

from utils.data_loader import load_data, get_stats


st.set_page_config(
    page_title="Dataset Explorer — CyberWatch",
    page_icon="🔍",
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

page_header(
    "Dataset Explorer",
    f"Exploratory data analysis across {df.shape[0]:,} rows and {df.shape[1]} columns of cyber threat data.",
    "🔍",
    label="Exploratory Analysis",
)

# ── Dataset Preview ────────────────────────────────────────────────────────────
with st.expander("📋 Dataset Preview (first 20 rows)", expanded=True):
    st.dataframe(df.head(20), hide_index=True, use_container_width=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Charts Row 1 ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("#### Threat Category Counts")
    fig1 = px.bar(
        x=list(tc.keys()), y=list(tc.values()),
        color=list(tc.values()),
        color_continuous_scale=[[0,"#1e293b"],[0.5,"#7c3aed"],[1,"#00d4ff"]],
        labels={"x": "Category", "y": "Count"},
        text=list(tc.values()),
    )
    fig1.update_traces(
        texttemplate="%{text:,}", textposition="outside",
        textfont=dict(size=10, color="#64748b"),
        marker_line_width=0,
    )
    layout1 = chart_layout(height=340)
    layout1["coloraxis_showscale"] = False
    fig1.update_layout(**layout1)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("#### Text Length Distribution")
    df_temp = df.copy()
    df_temp["text_length"] = df_temp["text"].str.len()

    COLORS = ["#00d4ff","#7c3aed","#f43f5e","#f59e0b","#00e5a0","#a78bfa","#38bdf8","#fb923c"]
    fig2 = px.histogram(
        df_temp, x="text_length", color="type", nbins=50,
        color_discrete_sequence=COLORS,
        labels={"text_length": "Character Count"},
    )
    fig2.update_traces(marker_line_width=0)
    layout2 = chart_layout(height=340)
    layout2["showlegend"] = True
    layout2["legend"] = dict(
        font=dict(family="DM Sans", size=10, color="#64748b"),
        bgcolor="rgba(0,0,0,0)", title=None,
    )
    layout2["barmode"] = "overlay"
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True)

# ── Average Text Length ────────────────────────────────────────────────────────
st.markdown("#### Average Text Length per Category")
df_temp2 = df.copy()
df_temp2["text_length"] = df_temp2["text"].str.len()
avg_len = df_temp2.groupby("type")["text_length"].mean().reset_index()
avg_len.columns = ["Category", "Avg Length"]
avg_len = avg_len.sort_values("Avg Length", ascending=False)

fig3 = px.bar(
    avg_len, x="Category", y="Avg Length",
    color="Avg Length",
    color_continuous_scale=[[0,"#1e293b"],[0.5,"#7c3aed"],[1,"#00e5a0"]],
    text=avg_len["Avg Length"].round(0).astype(int),
)
fig3.update_traces(
    texttemplate="%{text}", textposition="outside",
    textfont=dict(size=11, color="#64748b"),
    marker_line_width=0,
)
layout3 = chart_layout(height=280)
layout3["coloraxis_showscale"] = False
fig3.update_layout(**layout3)
st.plotly_chart(fig3, use_container_width=True)

# ── Word Frequency ─────────────────────────────────────────────────────────────
st.markdown("#### Most Frequent Words by Category")
selected_cat = st.selectbox(
    "Select threat category",
    list(tc.keys()),
    label_visibility="collapsed",
)
cat_texts = " ".join(df[df["type"] == selected_cat]["text"].astype(str).tolist())

try:
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    wc = WordCloud(
        width=900, height=380, background_color="black",
        colormap="cool", max_words=100, prefer_horizontal=0.8,
    ).generate(cat_texts)
    fig_wc, ax = plt.subplots(figsize=(11, 4))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig_wc.patch.set_facecolor("#060912")
    plt.tight_layout(pad=0)
    st.pyplot(fig_wc)

except ImportError:
    from collections import Counter
    stopwords = {"the","a","an","in","of","to","and","for","is","on","at","by","it",
                 "as","or","be","was","are","with","that","this","from","have","has"}
    words   = [w for w in cat_texts.lower().split() if w not in stopwords and len(w) > 2]
    common  = Counter(words).most_common(25)

    fig_bar = px.bar(
        x=[w[1] for w in common], y=[w[0] for w in common],
        orientation="h",
        color=[w[1] for w in common],
        color_continuous_scale=[[0,"#1e293b"],[0.5,"#7c3aed"],[1,"#00d4ff"]],
        labels={"x": "Frequency", "y": "Word"},
    )
    fig_bar.update_traces(marker_line_width=0)
    layout_wf = chart_layout(height=500)
    layout_wf["coloraxis_showscale"] = False
    layout_wf["yaxis"]["autorange"] = "reversed"
    fig_bar.update_layout(**layout_wf)
    st.plotly_chart(fig_bar, use_container_width=True)

render_footer()
