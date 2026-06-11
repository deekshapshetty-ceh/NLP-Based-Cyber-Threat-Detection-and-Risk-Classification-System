"""
CyberWatch — ML Classifier Utilities
======================================
Model / vectorizer loading and single-text classification.
"""

import os
import pickle
from datetime import datetime

import streamlit as st

from config.constants import RISK_MAP, RISK_COLOR, THREAT_ICONS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@st.cache_resource
def load_model():
    """Load the trained attack-classification model (cached across sessions)."""
    path = os.path.join(BASE_DIR, "models", "attack_model.pkl")
    if not os.path.exists(path):
        st.error(
            "⚠️ **Model not found:** `models/attack_model.pkl` is missing. "
            "Please ensure the model file exists in the `models/` folder and restart the app.",
            icon="🚨",
        )
        st.stop()
    with open(path, "rb") as f:
        return pickle.load(f)


@st.cache_resource
def load_vectorizer():
    """Load the TF-IDF vectorizer (cached across sessions)."""
    path = os.path.join(BASE_DIR, "models", "vectorizer.pkl")
    if not os.path.exists(path):
        st.error(
            "⚠️ **Vectorizer not found:** `models/vectorizer.pkl` is missing. "
            "Please ensure the vectorizer file exists in the `models/` folder and restart the app.",
            icon="🚨",
        )
        st.stop()
    with open(path, "rb") as f:
        return pickle.load(f)


def classify_text(text: str, _model=None, _vectorizer=None) -> dict:
    """Classify a single text and return a full result dictionary.

    Pass pre-loaded _model and _vectorizer to avoid redundant cache lookups
    when classifying many texts in a loop.
    """
    if _model is None:
        _model = load_model()
    if _vectorizer is None:
        _vectorizer = load_vectorizer()

    vec = _vectorizer.transform([text])
    prediction = _model.predict(vec)[0]
    probabilities = _model.predict_proba(vec)[0]
    confidence = round(float(max(probabilities)) * 100, 1)
    risk = RISK_MAP.get(prediction, "LOW")

    return {
        "threat_type": prediction,
        "risk_level": risk,
        "confidence": confidence,
        "icon": THREAT_ICONS.get(prediction, "📡"),
        "risk_color": RISK_COLOR.get(risk, "#00e5a0"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "all_probs": {
            cls: round(float(prob) * 100, 1)
            for cls, prob in zip(_model.classes_, probabilities)
        },
    }


def batch_classify(texts: list) -> list:
    """Classify a list of texts in one vectorized pass — much faster than looping classify_text."""
    _model = load_model()
    _vectorizer = load_vectorizer()

    vecs = _vectorizer.transform(texts)
    predictions = _model.predict(vecs)
    all_probs = _model.predict_proba(vecs)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    results = []
    for text, prediction, probabilities in zip(texts, predictions, all_probs):
        confidence = round(float(max(probabilities)) * 100, 1)
        risk = RISK_MAP.get(prediction, "LOW")
        results.append({
            "threat_type": prediction,
            "risk_level": risk,
            "confidence": confidence,
            "icon": THREAT_ICONS.get(prediction, "📡"),
            "risk_color": RISK_COLOR.get(risk, "#00e5a0"),
            "timestamp": ts,
            "all_probs": {
                cls: round(float(prob) * 100, 1)
                for cls, prob in zip(_model.classes_, probabilities)
            },
        })
    return results
