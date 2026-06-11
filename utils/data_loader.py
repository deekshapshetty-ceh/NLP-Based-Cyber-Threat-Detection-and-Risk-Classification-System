"""
CyberWatch — Data Loading Utilities
=====================================
CSV loading (cached) and pre-computed statistics.
"""

import os

import pandas as pd
import streamlit as st

from config.constants import RISK_MAP

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and clean the tweets dataset (cached across sessions)."""
    path = os.path.join(BASE_DIR, "data", "tweets_final.csv")
    if not os.path.exists(path):
        st.error(
            "⚠️ **Dataset not found:** `data/tweets_final.csv` is missing. "
            "Please ensure the file exists in the `data/` folder and restart the app.",
            icon="🚨",
        )
        st.stop()
    df = pd.read_csv(path)
    df = df[df["text"].notna() & df["type"].notna()].reset_index(drop=True)
    return df


@st.cache_data
def get_stats(df: pd.DataFrame) -> dict:
    """Compute risk-level statistics from the dataframe."""
    type_counts = df["type"].value_counts().to_dict()
    total = len(df)
    high_risk = sum(type_counts.get(t, 0)
                    for t in ["ransomware", "leak", "0day"])
    medium_risk = sum(type_counts.get(t, 0) for t in ["ddos", "botnet"])
    low_risk = total - high_risk - medium_risk
    return {
        "type_counts": type_counts,
        "total": total,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
    }
