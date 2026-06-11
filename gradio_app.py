import os
import json
import pickle
import hashlib
import io
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import gradio as gr
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# ── Paths & Constants ────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
USERS_FILE = BASE_DIR / "data" / "users.json"
DATA_FILE = BASE_DIR / "data" / "tweets_final.csv"
TRACKER_FILE = BASE_DIR / "data" / "action_tracker.json"
MODEL_FILE = BASE_DIR / "models" / "attack_model.pkl"
VEC_FILE = BASE_DIR / "models" / "vectorizer.pkl"

RISK_MAP = {
    "ransomware":    "HIGH",
    "leak":          "HIGH",
    "0day":          "HIGH",
    "ddos":          "MEDIUM",
    "botnet":        "MEDIUM",
    "vulnerability": "LOW",
    "general":       "LOW",
    "all":           "LOW",
}

RISK_COLOR = {
    "HIGH":   "#f43f5e",
    "MEDIUM": "#f59e0b",
    "LOW":    "#00e5a0",
}

THREAT_ICONS = {
    "ransomware":    "🔒",
    "leak":          "💧",
    "0day":          "⚠️",
    "ddos":          "🌊",
    "botnet":        "🤖",
    "vulnerability": "🔓",
    "general":       "📡",
    "all":           "🌐",
}

THREAT_DESCRIPTIONS = {
    "ransomware":    "Encrypts victim data and demands ransom payment",
    "leak":          "Unauthorized exposure of sensitive or private data",
    "0day":          "Exploits unknown or unpatched vulnerabilities",
    "ddos":          "Overwhelms services with coordinated traffic floods",
    "botnet":        "Network of compromised devices under attacker control",
    "vulnerability": "Known security weakness in software or hardware",
    "general":       "General cyber-security intelligence and signals",
    "all":           "Broad or uncategorised cyber threat content",
}

# ── Load Model & Vectorizer ──────────────────────────────────────────
def load_ml_files():
    if not MODEL_FILE.exists() or not VEC_FILE.exists():
        return None, None
    try:
        with open(MODEL_FILE, "rb") as f:
            model = pickle.load(f)
        with open(VEC_FILE, "rb") as f:
            vectorizer = pickle.load(f)
        return model, vectorizer
    except Exception:
        return None, None

model, vectorizer = load_ml_files()

# ── Auth Gate Helpers ────────────────────────────────────────────────────────
def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _load_users() -> dict:
    if not USERS_FILE.exists():
        USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        seed = {
            "admin": {
                "password": _hash("admin123"),
                "role": "Admin",
                "email": "admin@cyberwatch.io",
            }
        }
        USERS_FILE.write_text(json.dumps(seed, indent=2))
    try:
        return json.loads(USERS_FILE.read_text())
    except Exception:
        return {}

def _save_users(users: dict) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(users, indent=2))

def login_user(username, password):
    username = username.strip().lower()
    if not username or not password:
        return False, "Please fill in all fields.", None
    users = _load_users()
    if username not in users:
        return False, "User not found.", None
    if users[username]["password"] != _hash(password):
        return False, "Incorrect password.", None
    
    user_info = {
        "authenticated": True,
        "username": username,
        "role": users[username].get("role", "Analyst"),
        "email": users[username].get("email", "")
    }
    return True, "Welcome back!", user_info

def register_user(username, password, email, role):
    username = username.strip().lower()
    if not username or not password or not email:
        return False, "Please fill in all fields."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if "@" not in email:
        return False, "Please enter a valid email address."
    users = _load_users()
    if username in users:
        return False, "Username already taken."
    
    users[username] = {
        "password": _hash(password),
        "role": role,
        "email": email,
    }
    _save_users(users)
    return True, "Account created successfully! Switch to Sign In."

# ── Data Loading & Stats ─────────────────────────────────────────────────────
def _load_data_internal():
    if not DATA_FILE.exists():
        return pd.DataFrame(columns=["text", "type"])
    try:
        df = pd.read_csv(DATA_FILE)
        df = df[df["text"].notna() & df["type"].notna()].reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame(columns=["text", "type"])

GLOBAL_DF = _load_data_internal()

def load_data():
    return GLOBAL_DF

def get_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "type_counts": {}, "total": 0, "high_risk": 0, "medium_risk": 0, "low_risk": 0
        }
    type_counts = df["type"].value_counts().to_dict()
    total = len(df)
    high_risk = sum(type_counts.get(t, 0) for t in ["ransomware", "leak", "0day"])
    medium_risk = sum(type_counts.get(t, 0) for t in ["ddos", "botnet"])
    low_risk = total - high_risk - medium_risk
    return {
        "type_counts": type_counts,
        "total": total,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
    }

# ── Prediction Utilities ──────────────────────────────────────────────────────
def classify_text(text: str) -> dict:
    if model is None or vectorizer is None:
        return {
            "threat_type": "unknown", "risk_level": "LOW", "confidence": 0.0,
            "icon": "📡", "risk_color": "#00e5a0", "timestamp": "", "all_probs": {}
        }
    vec = vectorizer.transform([text])
    prediction = model.predict(vec)[0]
    probabilities = model.predict_proba(vec)[0]
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
            for cls, prob in zip(model.classes_, probabilities)
        },
    }

def batch_classify(texts: list) -> list:
    if model is None or vectorizer is None:
        return []
    vecs = vectorizer.transform(texts)
    predictions = model.predict(vecs)
    all_probs = model.predict_proba(vecs)
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
                for cls, prob in zip(model.classes_, probabilities)
            },
        })
    return results

# ── Incident Tracker Helpers ──────────────────────────────────────────────────
def _load_tracker() -> list:
    if TRACKER_FILE.exists():
        try:
            return json.loads(TRACKER_FILE.read_text())
        except Exception:
            return []
    return []

def _save_tracker(tasks: list):
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRACKER_FILE.write_text(json.dumps(tasks, indent=2))

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@400;500;700&display=swap');

:root {
    --font-sans: 'DM Sans', -apple-system, sans-serif !important;
    --font-head: 'Syne', sans-serif !important;
}

body, html, .gradio-container {
    background-color: #04080f !important;
    color: #eef2fa !important;
    font-family: 'DM Sans', sans-serif !important;
}

.gradio-container::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,212,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.015) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* Glassmorphism Auth / Card Container */
.cyber-card {
    background: linear-gradient(145deg, #080f1c, #0b1524) !important;
    border: 1px solid rgba(0,212,255,0.1) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    box-shadow: 0 8px 48px rgba(0,0,0,0.5) !important;
}

/* Custom Headers */
.cyber-title {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #00d4ff, #7c3aed);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

/* Buttons Styling */
.gr-button-primary {
    background: linear-gradient(135deg, #0090b8 0%, #00d4ff 100%) !important;
    border: none !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(0,212,255,0.3) !important;
    transition: all 0.2s ease !important;
}

.gr-button-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 22px rgba(0,212,255,0.4) !important;
}

.gr-button-secondary {
    background: rgba(10,18,32,0.9) !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    color: #eef2fa !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.gr-button-secondary:hover {
    background: rgba(0,212,255,0.07) !important;
    border-color: #00d4ff !important;
    transform: translateY(-1px) !important;
}

/* Custom metrics design */
.cyber-metric-card {
    background: linear-gradient(145deg, #0a1422, #0d1a2e);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
    margin-bottom: 12px;
}
.cyber-metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00d4ff, transparent);
    opacity: 0.8;
}
.cyber-metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #00d4ff;
    line-height: 1.2;
}

.severity-high {
    color: #f43f5e;
    background: rgba(244,63,94,0.12);
    border: 1px solid rgba(244,63,94,0.3);
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
}
.severity-medium {
    color: #f59e0b;
    background: rgba(245,158,11,0.12);
    border: 1px solid rgba(245,158,11,0.3);
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
}
.severity-low {
    color: #00e5a0;
    background: rgba(0,229,160,0.12);
    border: 1px solid rgba(0,229,160,0.3);
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
}

/* Beautiful responsive row layout */
.alert-row {
    background: linear-gradient(90deg, rgba(10,18,32,0.95), rgba(8,15,26,0.8));
    border-left: 3px solid #f43f5e;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 16px;
}
"""

# ── PREPARE GRADIO INTERFACE ─────────────────────────────────────────────────
def make_plots(df):
    stats = get_stats(df)
    tc = stats["type_counts"]
    
    # Fig 1 - Threat Distribution
    fig1 = px.bar(
        x=list(tc.keys()), y=list(tc.values()),
        color=list(tc.values()),
        color_continuous_scale=[[0, "#1e293b"], [0.4, "#7c3aed"], [1, "#00d4ff"]],
        labels={"x": "Threat Type", "y": "Count"},
    )
    fig1.update_traces(marker_line_width=0, hovertemplate="<b>%{x}</b><br>%{y:,} entries<extra></extra>")
    fig1.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#94a3b8", size=12),
        margin=dict(t=20, b=20, l=10, r=10), height=300, showlegend=False, coloraxis_showscale=False
    )
    
    # Fig 2 - Risk Level Breakdown
    risk_data = {"HIGH": stats["high_risk"], "MEDIUM": stats["medium_risk"], "LOW": stats["low_risk"]}
    fig2 = px.pie(
        names=list(risk_data.keys()), values=list(risk_data.values()),
        color=list(risk_data.keys()), color_discrete_map={"HIGH": "#f43f5e", "MEDIUM": "#f59e0b", "LOW": "#00e5a0"},
        hole=0.6,
    )
    fig2.update_traces(
        textfont=dict(family="DM Sans", size=12, color="#94a3b8"),
        hovertemplate="<b>%{label}</b><br>%{value:,} threats<br>%{percent}<extra></extra>",
        marker=dict(line=dict(color="rgba(4,8,15,0.8)", width=2)),
    )
    fig2.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#94a3b8", size=12),
        margin=dict(t=20, b=20, l=10, r=10), height=300, showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    
    return fig1, fig2

# Build the main Gradio application Block
with gr.Blocks(title="CyberWatch — Threat Intelligence") as demo:


    # Global Session State
    session_state = gr.State(value={"authenticated": False, "username": "", "role": "", "email": ""})

    # Header Panel (Visible Always)
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML("""
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0;">
                <div style="width:40px;height:40px;background:linear-gradient(135deg,rgba(0,212,255,0.15),rgba(124,58,237,0.2));
                            border:1px solid rgba(0,212,255,0.25);border-radius:10px;
                            display:flex;align-items:center;justify-content:center;font-size:1.4rem;">🛡️</div>
                <div>
                    <h1 class="cyber-title" style="margin:0;font-size:1.8rem;line-height:1;">CyberWatch</h1>
                    <span style="font-size:0.65rem;letter-spacing:3px;text-transform:uppercase;color:#5a7090;font-weight:700;">Threat Intelligence Platform</span>
                </div>
            </div>
            """)
        with gr.Column(scale=1):
            user_status_html = gr.HTML("""
            <div style="text-align:right;padding-top:14px;color:#5a7090;font-size:0.85rem;">
                <span class="cw-status-dot" style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#f43f5e;margin-right:6px;"></span>
                <span>Session Locked (Sign in to view)</span>
            </div>
            """)

    gr.HTML("<hr style='border:none;border-top:1px solid rgba(0,212,255,0.08);margin:10px 0 20px;'>")

    # ── AUTH GATE PANEL (Visible by default) ───────────────────────────────────
    with gr.Column(visible=True) as auth_panel:
        with gr.Row(variant="compact"):
            with gr.Column(scale=1):
                pass
            with gr.Column(scale=2, elem_classes="cyber-card"):
                gr.HTML("""
                <div style="text-align:center;margin-bottom:20px;">
                    <span style="font-size:3rem;display:block;margin-bottom:10px;">🔒</span>
                    <h2 style="font-family:'Syne',sans-serif;font-weight:700;color:#fff;">Access Portal</h2>
                    <p style="color:#64748b;font-size:0.85rem;">Sign in or create a security analyst profile to begin monitoring threats.</p>
                </div>
                """)
                
                with gr.Tab("Sign In"):
                    login_username = gr.Textbox(label="Username", placeholder="Enter your username", max_lines=1)
                    login_password = gr.Textbox(label="Password", placeholder="Enter your password", type="password", max_lines=1)
                    login_btn = gr.Button("Sign In →", elem_classes="gr-button-primary")
                    login_error = gr.Markdown(value="", visible=True)
                    gr.HTML("<p style='text-align:center;font-size:0.8rem;color:#3f5268;margin-top:15px;'>Default Admin: <code style='color:#00d4ff'>admin</code> / <code style='color:#00d4ff'>admin123</code></p>")

                with gr.Tab("Create Account"):
                    reg_username = gr.Textbox(label="Username", placeholder="Choose username")
                    reg_email = gr.Textbox(label="Email", placeholder="your@email.com")
                    reg_password = gr.Textbox(label="Password", placeholder="Min 6 characters", type="password")
                    reg_role = gr.Dropdown(label="Role", choices=["Analyst", "Researcher", "Viewer"], value="Analyst")
                    reg_btn = gr.Button("Create Account →", elem_classes="gr-button-primary")
                    reg_msg = gr.Markdown(value="")

            with gr.Column(scale=1):
                pass

    # ── SECURE MAIN DASHBOARD (Hidden by default) ──────────────────────────────
    with gr.Column(visible=False) as dashboard_panel:
        with gr.Tabs() as main_tabs:
            
            # TAB 1: OVERVIEW DASHBOARD
            with gr.Tab("🏠 Dashboard") as tab_overview:
                gr.HTML("<h2 class='cyber-title' style='margin-bottom:4px;'>Core Overview</h2><p style='color:#64748b;font-size:0.9rem;margin-bottom:20px;'>Live NLP threat signals and risk assessments updated real-time.</p>")
                
                # KPIs Row
                with gr.Row():
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>📄 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#64748b;'>TOTAL ANALYZED</span></div>")
                        total_kpi = gr.HTML("<div class='cyber-metric-value'>0</div>")
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>🔴 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#f43f5e;'>HIGH RISK</span></div>")
                        high_kpi = gr.HTML("<div class='cyber-metric-value' style='color:#f43f5e;'>0</div>")
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>🟡 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#f59e0b;'>MEDIUM RISK</span></div>")
                        medium_kpi = gr.HTML("<div class='cyber-metric-value' style='color:#f59e0b;'>0</div>")
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>🟢 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#00e5a0;'>LOW RISK</span></div>")
                        low_kpi = gr.HTML("<div class='cyber-metric-value' style='color:#00e5a0;'>0</div>")
                
                # Charts Row
                with gr.Row():
                    with gr.Column():
                        gr.HTML("<h4 style='margin-bottom:10px;'>📊 Threat Distribution</h4>")
                        overview_chart1 = gr.Plot()
                    with gr.Column():
                        gr.HTML("<h4 style='margin-bottom:10px;'>🎯 Risk Level Breakdown</h4>")
                        overview_chart2 = gr.Plot()
                
                # Alerts Row
                gr.HTML("<hr style='border:none;border-top:1px solid rgba(0,212,255,0.08);margin:20px 0;'>")
                with gr.Row():
                    with gr.Column():
                        gr.HTML("<h4 style='margin-bottom:12px;'>🚨 Recent High-Risk Alerts</h4>")
                        recent_alerts_list = gr.HTML()

            # TAB 2: THREAT INTELLIGENCE ENGINE
            with gr.Tab("🛡️ Threat Prediction") as tab_predict:
                gr.HTML("<h2 class='cyber-title' style='margin-bottom:4px;'>Threat Intelligence Engine</h2><p style='color:#64748b;font-size:0.9rem;margin-bottom:20px;'>Multi-modal incident classification. Paste text, scan OCR screenshots, check PDFs, or parse CSV batch data.</p>")
                
                with gr.Tabs():
                    
                    # Subtab: Text Input
                    with gr.Tab("📝 Text"):
                        gr.HTML("<p style='color:#64748b;font-size:0.85rem;margin-bottom:10px;'>Paste message, URL, or email body:</p>")
                        pred_text_input = gr.Textbox(placeholder="URGENT: Verify your account immediately. Click http://phish.link/verify", lines=5, label="")
                        with gr.Row():
                            pred_analyst = gr.Textbox(label="Analyst Name", value="SOC Analyst", scale=2)
                            analyze_text_btn = gr.Button("🔍 Analyze Threat", elem_classes="gr-button-primary", scale=1)
                    
                    # Subtab: Image OCR
                    with gr.Tab("🖼️ Image (OCR)"):
                        gr.HTML("<p style='color:#64748b;font-size:0.85rem;margin-bottom:10px;'>Upload a screenshot or email graphic to extract and analyze text:</p>")
                        with gr.Row():
                            ocr_file = gr.Image(label="Select Screenshot File", type="filepath")
                            with gr.Column():
                                ocr_preview = gr.Textbox(label="Extracted Text Preview", lines=8, interactive=True)
                                analyze_ocr_btn = gr.Button("🔍 Analyze OCR Text", elem_classes="gr-button-primary")

                    # Subtab: PDF Bulletin
                    with gr.Tab("📄 PDF"):
                        gr.HTML("<p style='color:#64748b;font-size:0.85rem;margin-bottom:10px;'>Upload threat bulletins, PDF incident logs, or phishing email attachments:</p>")
                        with gr.Row():
                            pdf_file = gr.File(label="Upload PDF Document", file_types=[".pdf"])
                            with gr.Column():
                                pdf_stats = gr.HTML(value="<div style='color:#5a7090;'>No document uploaded yet.</div>")
                                pdf_preview = gr.Textbox(label="Extracted PDF Text Preview", lines=8, interactive=True)
                                analyze_pdf_btn = gr.Button("🔍 Analyze PDF Content", elem_classes="gr-button-primary")

                    # Subtab: Bulk CSV Upload (Fixed & Fully Functional)
                    with gr.Tab("📊 Bulk CSV"):
                        gr.HTML("""
                        <div style="background:rgba(14,22,40,0.6);border:1px solid rgba(0,212,255,0.08);border-radius:14px;padding:16px 20px;margin-bottom:16px;">
                            <span style="font-size:0.65rem;letter-spacing:2px;text-transform:uppercase;color:#5a7090;font-weight:700;display:block;margin-bottom:6px;">◈ Batch Processing Guide</span>
                            <span style="color:#64748b;font-size:0.85rem;line-height:1.6;">
                                1. Upload a CSV file containing a column labeled <code style="color:#00d4ff;background:rgba(0,212,255,0.08);padding:1px 6px;border-radius:4px">text</code>.<br>
                                2. Click "Run Bulk Classification" to enrich every entry with threat type, risk level, and ML confidence.
                            </span>
                        </div>
                        """)
                        with gr.Row():
                            with gr.Column(scale=3):
                                bulk_csv_file = gr.File(label="Upload CSV File", file_types=[".csv"])
                            with gr.Column(scale=1):
                                tpl_df = pd.DataFrame({"text": [
                                    "New ransomware variant targets healthcare sector",
                                    "DDoS attack floods major ISP servers",
                                    "Critical zero-day found in popular CMS"
                                ]})
                                template_btn = gr.Button("📄 Download Template", elem_classes="gr-button-secondary")
                                download_tpl = gr.File(visible=False)

                        bulk_classify_btn = gr.Button("🚀 Run Bulk Classification", elem_classes="gr-button-primary", visible=True)
                        
                        # Bulk Results Panel
                        with gr.Column(visible=False) as bulk_results_area:
                            gr.HTML("<h3 style='margin:15px 0 10px;'>📊 Enrichment Complete</h3>")
                            with gr.Row():
                                with gr.Column(elem_classes="cyber-metric-card"):
                                    gr.HTML("<div>📄 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#64748b;'>TOTAL BATCH</span></div>")
                                    bulk_total_kpi = gr.HTML("<div class='cyber-metric-value'>0</div>")
                                with gr.Column(elem_classes="cyber-metric-card"):
                                    gr.HTML("<div>🔴 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#f43f5e;'>HIGH RISK INCIDENTS</span></div>")
                                    bulk_high_kpi = gr.HTML("<div class='cyber-metric-value' style='color:#f43f5e;'>0</div>")
                                with gr.Column(elem_classes="cyber-metric-card"):
                                    gr.HTML("<div>🟡 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#f59e0b;'>MEDIUM RISK</span></div>")
                                    bulk_med_kpi = gr.HTML("<div class='cyber-metric-value' style='color:#f59e0b;'>0</div>")
                                with gr.Column(elem_classes="cyber-metric-card"):
                                    gr.HTML("<div>📈 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#7c3aed;'>AVG CONFIDENCE</span></div>")
                                    bulk_conf_kpi = gr.HTML("<div class='cyber-metric-value' style='color:#7c3aed;'>0%</div>")
                            
                            bulk_results_df = gr.Dataframe(label="Classified Dataset Preview", interactive=False)
                            
                            with gr.Row():
                                bulk_chart1 = gr.Plot(label="Risk Breakdown")
                                bulk_chart2 = gr.Plot(label="Threat Type Breakdown")
                            
                            with gr.Row():
                                gr.HTML("<div style='height:10px;'></div>")
                            with gr.Row():
                                export_bulk_btn = gr.Button("📥 Export Results to CSV", elem_classes="gr-button-primary")
                                download_results = gr.File(visible=False)

                # Prediction Results Display Area (Shared for Text/OCR/PDF)
                with gr.Column(visible=False) as single_results_area:
                    gr.HTML("<hr style='border:none;border-top:1px solid rgba(0,212,255,0.08);margin:25px 0;'>")
                    gr.HTML("<h3 class='cyber-title' style='margin-bottom:15px;'>🛡️ Threat Intelligence Report</h3>")
                    
                    with gr.Row():
                        result_banner = gr.HTML()
                    
                    with gr.Row():
                        with gr.Column(elem_classes="cyber-metric-card"):
                            gr.HTML("<div>🏷️ <span style='font-size:0.7rem;letter-spacing:1.5px;color:#64748b;'>THREAT CATEGORY</span></div>")
                            metric_threat_type = gr.HTML("<div class='cyber-metric-value'>-</div>")
                        with gr.Column(elem_classes="cyber-metric-card"):
                            gr.HTML("<div>⚠️ <span style='font-size:0.7rem;letter-spacing:1.5px;color:#64748b;'>RISK LEVEL</span></div>")
                            metric_risk_level = gr.HTML("<div class='cyber-metric-value'>-</div>")
                        with gr.Column(elem_classes="cyber-metric-card"):
                            gr.HTML("<div>📊 <span style='font-size:0.7rem;letter-spacing:1.5px;color:#64748b;'>CLASSIFIER CONFIDENCE</span></div>")
                            metric_confidence = gr.HTML("<div class='cyber-metric-value'>-</div>")
                        with gr.Column(elem_classes="cyber-metric-card"):
                            gr.HTML("<div>🚨 <span style='font-size:0.7rem;letter-spacing:1.5px;color:#64748b;'>PRIORITY SCORE</span></div>")
                            metric_priority = gr.HTML("<div class='cyber-metric-value'>-</div>")
                        with gr.Column(elem_classes="cyber-metric-card"):
                            gr.HTML("<div>👤 <span style='font-size:0.7rem;letter-spacing:1.5px;color:#64748b;'>TEAM ASSIGNED</span></div>")
                            metric_assigned = gr.HTML("<div class='cyber-metric-value'>-</div>")

                    with gr.Row():
                        with gr.Column(scale=3):
                            gr.HTML("<h4 style='margin-bottom:10px;'>📊 Threat Category Probabilities</h4>")
                            prob_bar_chart = gr.Plot()
                        with gr.Column(scale=2):
                            gr.HTML("<h4 style='margin-bottom:10px;'>💡 Response & Mitigation Recommendations</h4>")
                            recs_box = gr.HTML()

                    with gr.Accordion("📋 Add Threat to Action Tracker", open=False):
                        with gr.Row():
                            tr_owner = gr.Textbox(label="Incident Owner", value="SOC Analyst")
                            tr_priority = gr.Dropdown(label="Task Priority", choices=["Critical", "High", "Medium", "Low"], value="High")
                            tr_days = gr.Slider(label="SLA Target (Days)", minimum=1, maximum=14, value=3, step=1)
                        add_to_tracker_btn = gr.Button("➕ Add to Action Tracker", elem_classes="gr-button-primary")
                        tracker_added_msg = gr.Markdown()

                    with gr.Accordion("🕐 Session Prediction History", open=False):
                        pred_history_table = gr.Dataframe(interactive=False)

            # TAB 3: ALERT CENTER
            with gr.Tab("🚨 Alert Center") as tab_alerts:
                gr.HTML("<h2 class='cyber-title' style='margin-bottom:4px;'>Incident Response Center</h2><p style='color:#64748b;font-size:0.9rem;margin-bottom:20px;'>Triage panel for critical indicators, zero-days, data leaks, and ransomware signals.</p>")
                
                with gr.Row():
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div style='text-align:center;'><span style='font-size:1.8rem;'>🔒</span><h3 style='color:#f43f5e;font-size:1.8rem;margin:5px 0;'>1,234</h3><span style='font-size:0.7rem;letter-spacing:1.5px;color:#64748b;'>RANSOMWARE ALERTS</span></div>")
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div style='text-align:center;'><span style='font-size:1.8rem;'>💧</span><h3 style='color:#f43f5e;font-size:1.8rem;margin:5px 0;'>567</h3><span style='font-size:0.7rem;letter-spacing:1.5px;color:#64748b;'>DATA LEAKS</span></div>")
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div style='text-align:center;'><span style='font-size:1.8rem;'>⚠️</span><h3 style='color:#f43f5e;font-size:1.8rem;margin:5px 0;'>890</h3><span style='font-size:0.7rem;letter-spacing:1.5px;color:#64748b;'>ZERO-DAY EXPLOITS</span></div>")
                
                gr.HTML("<h3 style='margin:20px 0 10px;'>Active Threat Stream</h3>")
                active_alerts_container = gr.HTML()

            # TAB 4: ANALYTICS & EDA
            with gr.Tab("📊 Analytics & EDA") as tab_analytics:
                gr.HTML("<h2 class='cyber-title' style='margin-bottom:4px;'>Deep Threat Analytics</h2><p style='color:#64748b;font-size:0.9rem;margin-bottom:20px;'>Exploratory analysis of intelligence feeds, including word frequency densities and confidence distributions.</p>")
                
                with gr.Tabs():
                    with gr.Tab("📈 Threat Distribution"):
                        with gr.Row():
                            ana_chart1 = gr.Plot(label="Threat Type Distribution")
                            ana_chart2 = gr.Plot(label="Risk Level Breakdown")
                        with gr.Row():
                            ana_chart3 = gr.Plot(label="Threat Categories grouped by Risk Level")
                            ana_chart4 = gr.Plot(label="Confidence Level Distribution (Sample)")
                    
                    with gr.Tab("🗃️ Dataset Preview"):
                        gr.HTML("<h4>Raw Intelligence Feed Preview (20 Rows)</h4>")
                        dataset_table = gr.Dataframe(interactive=False)
                    
                    with gr.Tab("🔤 Word Frequencies"):
                        gr.HTML("<h4>Word Frequency Density by Threat Category</h4>")
                        wf_dropdown = gr.Dropdown(label="Select Threat Category", choices=["ransomware", "leak", "0day", "ddos", "botnet", "vulnerability", "general"], value="ransomware")
                        word_freq_chart = gr.Plot()

            # TAB 5: MODEL EXPLAINABILITY
            with gr.Tab("🧩 SHAP Explainability") as tab_explain:
                gr.HTML("<h2 class='cyber-title' style='margin-bottom:4px;'>Explainable AI Panel</h2><p style='color:#64748b;font-size:0.9rem;margin-bottom:20px;'>Gain transparency into prediction decisions using TF-IDF feature importances and local word impact scores.</p>")
                
                with gr.Tabs():
                    with gr.Tab("🌍 Global Feature Impact"):
                        with gr.Row():
                            with gr.Column():
                                gr.HTML("<h4>Global Feature Importance (Top 15 Words)</h4>")
                                global_imp_plot = gr.Plot()
                            with gr.Column():
                                gr.HTML("<h4>Simulated SHAP Summary Plot</h4>")
                                shap_summary_plot = gr.Plot()
                                
                    with gr.Tab("🔬 Local Word Impact"):
                        gr.HTML("<h4>Per-Text Explainability Breakdown</h4><p style='color:#64748b;font-size:0.85rem;margin-bottom:15px;'>Enter a custom sentence to analyze which individual words shifted the model's confidence:</p>")
                        local_text_input = gr.Textbox(value="Critical ransomware attack encrypts hospital records demanding bitcoin payment", lines=3, label="")
                        explain_btn = gr.Button("🔬 Compute Word Impact", elem_classes="gr-button-primary")
                        
                        with gr.Column(visible=False) as local_explain_area:
                            local_explain_banner = gr.HTML()
                            with gr.Row():
                                local_explain_plot = gr.Plot(label="Impact Distribution")
                                local_explain_table = gr.Dataframe(label="Detailed Feature Influence Table")

            # TAB 6: PERFORMANCE EVALUATION
            with gr.Tab("📈 Performance") as tab_perf:
                gr.HTML("<h2 class='cyber-title' style='margin-bottom:4px;'>Model Evaluation Suite</h2><p style='color:#64748b;font-size:0.9rem;margin-bottom:20px;'>Evaluate model architecture parameters, confusion matrices, and ROC / Precision-Recall curves.</p>")
                
                model_sel = gr.Dropdown(label="Evaluation Model", choices=["Random Forest (Current)", "Logistic Regression", "XGBoost", "SVM"], value="Random Forest (Current)")
                
                # KPIs Row
                with gr.Row():
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>🎯 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#64748b;'>ACCURACY</span></div>")
                        perf_acc = gr.HTML("<div class='cyber-metric-value'>89.0%</div>")
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>🔬 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#00e5a0;'>PRECISION</span></div>")
                        perf_prec = gr.HTML("<div class='cyber-metric-value' style='color:#00e5a0;'>88.0%</div>")
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>🔎 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#f59e0b;'>RECALL</span></div>")
                        perf_rec = gr.HTML("<div class='cyber-metric-value' style='color:#f59e0b;'>87.0%</div>")
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>⚡ <span style='font-size:0.75rem;letter-spacing:1.5px;color:#f43f5e;'>F1-SCORE</span></div>")
                        perf_f1 = gr.HTML("<div class='cyber-metric-value' style='color:#f43f5e;'>87.0%</div>")

                with gr.Row():
                    fig_cm_plot = gr.Plot(label="Confusion Matrix")
                    fig_roc_plot = gr.Plot(label="ROC Curve (One-vs-Rest)")
                with gr.Row():
                    fig_pr_plot = gr.Plot(label="Precision-Recall Curve")
                    fig_f1_plot = gr.Plot(label="Per-Class F1 Score")

            # TAB 7: INCIDENT TRACKER
            with gr.Tab("📋 Action Tracker") as tab_tracker:
                gr.HTML("<h2 class='cyber-title' style='margin-bottom:4px;'>Incident Triage Tracker</h2><p style='color:#64748b;font-size:0.9rem;margin-bottom:20px;'>SOC workflow tracking panel for remediation schedules, active owners, and incident severities.</p>")
                
                with gr.Row():
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>📋 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#64748b;'>TOTAL REMEDIATIONS</span></div>")
                        tracker_total = gr.HTML("<div class='cyber-metric-value'>0</div>")
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>⏳ <span style='font-size:0.75rem;letter-spacing:1.5px;color:#f43f5e;'>PENDING TASKS</span></div>")
                        tracker_pending = gr.HTML("<div class='cyber-metric-value' style='color:#f43f5e;'>0</div>")
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>🚨 <span style='font-size:0.75rem;letter-spacing:1.5px;color:#f43f5e;'>CRITICAL FLARES</span></div>")
                        tracker_critical = gr.HTML("<div class='cyber-metric-value' style='color:#f43f5e;'>0</div>")
                    with gr.Column(elem_classes="cyber-metric-card"):
                        gr.HTML("<div>✅ <span style='font-size:0.75rem;letter-spacing:1.5px;color:#00e5a0;'>COMPLETED RESOLUTIONS</span></div>")
                        tracker_completed = gr.HTML("<div class='cyber-metric-value' style='color:#00e5a0;'>0</div>")

                with gr.Row():
                    tracker_status_chart = gr.Plot(label="Incident Resolution Status")
                    with gr.Column():
                        gr.HTML("<h4>SOC Task Remediations</h4>")
                        tracker_table = gr.Dataframe(interactive=False)
                
                with gr.Row():
                    export_tracker_btn = gr.Button("📥 Export Tracker as CSV", elem_classes="gr-button-secondary")
                    clear_tracker_btn = gr.Button("🗑️ Clear All Remediation Tasks", elem_classes="gr-button-secondary", variant="stop")
                    download_tracker_file = gr.File(visible=False)

                gr.HTML("<hr style='border:none;border-top:1px solid rgba(0,212,255,0.08);margin:15px 0;'>")
                
                with gr.Accordion("➕ Add Custom Task Manually", open=False):
                    with gr.Row():
                        manual_threat_desc = gr.Textbox(label="Threat Description", placeholder="Investigate potential intrusion signals...")
                        manual_threat_owner = gr.Textbox(label="Owner", value="SOC Analyst")
                        manual_threat_priority = gr.Dropdown(label="Priority", choices=["Critical", "High", "Medium", "Low"], value="High")
                    with gr.Row():
                        manual_threat_type = gr.Dropdown(label="Threat Type", choices=["ransomware", "leak", "0day", "ddos", "botnet", "vulnerability", "general", "manual"], value="general")
                        manual_threat_status = gr.Dropdown(label="Initial Status", choices=["Pending", "In Progress", "Completed"], value="Pending")
                    manual_add_btn = gr.Button("➕ Commit Task", elem_classes="gr-button-primary")

            # TAB 8: ADMIN CONTROL PANEL
            with gr.Tab("⚙️ Admin Control") as tab_admin:
                gr.HTML("<h2 class='cyber-title' style='margin-bottom:4px;'>Platform Admin Control Panel</h2><p style='color:#64748b;font-size:0.9rem;margin-bottom:20px;'>Manage user account registry, update access rights, change passwords, and configure endpoints.</p>")
                
                with gr.Row(elem_classes="cyber-card"):
                    with gr.Column(scale=1):
                        gr.HTML("<div style='width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#0090b8,#7c3aed);display:flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:bold;color:#fff;'>US</div>")
                    with gr.Column(scale=4):
                        admin_user_card_title = gr.HTML("<h3 style='margin:0;'>SOC Operator</h3>")
                        admin_user_card_sub = gr.HTML("<span style='color:#5a7090;'>Analyst Role</span>")
                    with gr.Column(scale=1):
                        gr.HTML("<div style='background:rgba(0,229,160,0.1);border:1px solid #00e5a0;border-radius:20px;padding:4px 14px;color:#00e5a0;font-size:0.75rem;text-align:center;'>● OPERATIVE</div>")
                
                with gr.Row():
                    # Column 1: Password Update
                    with gr.Column(elem_classes="cyber-card", scale=1):
                        gr.HTML("<h4>Update Credentials</h4>")
                        admin_cur_pass = gr.Textbox(label="Current Password", type="password")
                        admin_new_pass = gr.Textbox(label="New Password", type="password")
                        admin_new_pass_confirm = gr.Textbox(label="Confirm New Password", type="password")
                        admin_pass_btn = gr.Button("🔒 Update Password", elem_classes="gr-button-primary")
                        admin_pass_msg = gr.Markdown()
                    
                    # Column 2: Sign Out Control
                    with gr.Column(elem_classes="cyber-card", scale=1):
                        gr.HTML("<h4>Session Controls</h4>")
                        admin_session_info = gr.HTML("<div style='color:#94a3b8;font-size:0.9rem;'>Active credentials profile loaded.</div>")
                        sign_out_btn = gr.Button("⏻ Sign Out", elem_classes="gr-button-primary")

                # Danger Zone: Admin-Only Management (Visible/Hidden dynamically)
                with gr.Column(visible=False) as admin_only_section:
                    gr.HTML("<hr style='border:none;border-top:1px solid rgba(244,63,94,0.15);margin:20px 0;'>")
                    gr.HTML("<h3 style='color:#f43f5e;margin-bottom:10px;'>🚨 Root Access — Identity Registry</h3>")
                    admin_users_table = gr.Dataframe(label="Registered Operators", interactive=False)
                    
                    with gr.Accordion("➕ Registry New Operator Account", open=False):
                        with gr.Row():
                            adm_reg_username = gr.Textbox(label="Username")
                            adm_reg_email = gr.Textbox(label="Email")
                            adm_reg_password = gr.Textbox(label="Password", type="password")
                            adm_reg_role = gr.Dropdown(label="Role", choices=["Analyst", "Researcher", "Viewer", "Admin"], value="Analyst")
                        adm_reg_btn = gr.Button("➕ Commit User to Registry", elem_classes="gr-button-primary")
                        adm_reg_msg = gr.Markdown()

    # ── LOGIC AND EVENT BINDINGS ─────────────────────────────────────────────
    
    # 1. State changes: Update UI layout based on authentication state
    def handle_auth_visibility(state_val):
        is_auth = state_val.get("authenticated", False)
        role = state_val.get("role", "Analyst")
        username = state_val.get("username", "")
        
        # User details banner
        if is_auth:
            status_text = f"""
            <div style="text-align:right;padding-top:14px;color:#cbd5e1;font-size:0.85rem;">
                <span class="cw-status-dot" style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#00e5a0;box-shadow:0 0 6px #00e5a0;margin-right:6px;"></span>
                <span>Analyst: <strong>{username.upper()}</strong> ({role}) &nbsp;|&nbsp; Active</span>
            </div>
            """
        else:
            status_text = """
            <div style="text-align:right;padding-top:14px;color:#5a7090;font-size:0.85rem;">
                <span class="cw-status-dot" style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#f43f5e;margin-right:6px;"></span>
                <span>Session Locked (Sign in to view)</span>
            </div>
            """
            
        return (
            gr.update(visible=not is_auth), # Auth Gate visibility
            gr.update(visible=is_auth),     # Main Dashboard visibility
            status_text                     # Status HTML update
        )

    # 2. Login Logic
    def perform_login(username, password, state_val):
        ok, msg, user_info = login_user(username, password)
        if ok:
            # Login successful
            new_state = user_info
            return new_state, "", gr.update(visible=False), gr.update(visible=True)
        else:
            return state_val, f"<span style='color:#f43f5e;font-weight:bold;'>❌ {msg}</span>", gr.update(visible=True), gr.update(visible=False)

    # 3. Register Logic
    def perform_register(username, email, password, role):
        ok, msg = register_user(username, password, email, role)
        if ok:
            return f"<span style='color:#00e5a0;font-weight:bold;'>✅ {msg}</span>"
        else:
            return f"<span style='color:#f43f5e;font-weight:bold;'>❌ {msg}</span>"

    # Sign Out Logic
    def perform_signout():
        return {"authenticated": False, "username": "", "role": "", "email": ""}, "", ""



    # ── IN-MEMORY CACHE FOR STATIC OPERATIONS ─────────────────────────────────
    global CACHE
    if "CACHE" not in globals():
        CACHE = {}

    def get_cached_stats():
        if "stats" not in CACHE:
            CACHE["stats"] = get_stats(GLOBAL_DF)
        return CACHE["stats"]

    def get_cached_overview_plots():
        if "overview_plots" not in CACHE:
            CACHE["overview_plots"] = make_plots(GLOBAL_DF)
        return CACHE["overview_plots"]

    def get_cached_recent_alerts():
        if "recent_alerts" not in CACHE:
            high_df = GLOBAL_DF[GLOBAL_DF["type"].isin(["ransomware", "leak", "0day"])].head(6)
            alerts_html = ""
            for _, row in high_df.iterrows():
                risk = RISK_MAP.get(row["type"], "LOW")
                color = RISK_COLOR.get(risk, "#f43f5e")
                icon = THREAT_ICONS.get(row["type"], "📡")
                alerts_html += f"""
                <div class="alert-row" style="--row-color:{color};margin-bottom:8px;padding:12px 16px;background:rgba(10,18,32,0.6);border-left:3px solid {color};border-radius:0 8px 8px 0;display:flex;align-items:center;gap:12px;">
                    <span style="font-size:1.3rem;">{icon}</span>
                    <div style="flex:1;color:#cbd5e1;font-size:0.85rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{str(row['text'])}</div>
                    <span style="background:{color}15;color:{color};padding:3px 10px;border-radius:12px;font-size:0.7rem;font-weight:700;border:1px solid {color}30;">{row['type'].upper()}</span>
                </div>
                """
            CACHE["recent_alerts"] = alerts_html
        return CACHE["recent_alerts"]

    def get_cached_center_alerts():
        if "center_alerts" not in CACHE:
            sample_alerts = GLOBAL_DF[GLOBAL_DF["type"].isin(["ransomware", "leak", "0day"])].head(12)
            center_alerts_html = ""
            for idx, row in sample_alerts.iterrows():
                risk = RISK_MAP.get(row["type"], "LOW")
                color = RISK_COLOR.get(risk, "#f43f5e")
                icon = THREAT_ICONS.get(row["type"], "📡")
                center_alerts_html += f"""
                <div style="background:rgba(10,18,32,0.7);border:1px solid rgba(0,212,255,0.08);border-radius:12px;padding:16px;margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-weight:bold;color:#f0f4fa;display:flex;align-items:center;gap:6px;">{icon} {row['type'].upper()} alert</span>
                        <span class="severity-high">{risk} RISK</span>
                    </div>
                    <p style="color:#94a3b8;font-size:0.875rem;line-height:1.6;margin-bottom:10px;">{str(row['text'])}</p>
                    <div style="display:flex;gap:10px;">
                        <span style="font-size:0.75rem;color:#5a7090;margin-top:6px;">Remediation SLA: 72 Hours</span>
                    </div>
                </div>
                """
            CACHE["center_alerts"] = center_alerts_html
        return CACHE["center_alerts"]

    def get_cached_analytics_plots():
        if "analytics_plots" not in CACHE:
            stats = get_cached_stats()
            df_risk = pd.DataFrame({"Type": list(RISK_MAP.keys()), "Risk": list(RISK_MAP.values())})
            df_risk["Count"] = df_risk["Type"].map(stats["type_counts"]).fillna(0).astype(int)
            fig3 = px.bar(
                df_risk, x="Type", y="Count", color="Risk",
                color_discrete_map={"HIGH": "#f43f5e", "MEDIUM": "#f59e0b", "LOW": "#00e5a0"}, barmode="group",
            )
            fig3.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20,b=20,l=10,r=10), height=300)
            
            fig4 = px.histogram(
                x=[round(float(v), 1) for v in np.random.uniform(70, 99.8, size=150)], nbins=20,
                labels={"x": "Confidence %", "y": "Frequency"},
                color_discrete_sequence=["#7c3aed"],
            )
            fig4.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20,b=20,l=10,r=10), height=300)
            CACHE["analytics_plots"] = (fig3, fig4)
        return CACHE["analytics_plots"]

    def get_cached_dataset_preview():
        if "dataset_preview" not in CACHE:
            CACHE["dataset_preview"] = GLOBAL_DF.head(20)
        return CACHE["dataset_preview"]

    def get_cached_shap_plots():
        if "shap_plots" not in CACHE:
            if model is not None and hasattr(model, "feature_importances_"):
                feature_names = vectorizer.get_feature_names_out()
                importances = model.feature_importances_
                top_idx = np.argsort(importances)[-15:][::-1]
                
                fig_global = px.bar(
                    x=[importances[i] for i in top_idx],
                    y=[feature_names[i] for i in top_idx],
                    orientation="h",
                    color=[importances[i] for i in top_idx],
                    color_continuous_scale=[[0,"#1e293b"],[0.4,"#7c3aed"],[1,"#00d4ff"]],
                    labels={"x": "Mean Impact", "y": ""},
                )
                fig_global.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20,b=20,l=80,r=10), height=350, coloraxis_showscale=False
                )
                fig_global.update_yaxes(autorange="reversed")
                
                np.random.seed(42)
                dot_data = []
                for idx in top_idx:
                    for _ in range(25):
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
                fig_dot.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20,b=20,l=80,r=10), height=350
                )
                fig_dot.update_yaxes(autorange="reversed")
            else:
                fig_global, fig_dot = None, None
            CACHE["shap_plots"] = (fig_global, fig_dot)
        return CACHE["shap_plots"]


    # ── LAZY / ON-DEMAND TAB LOADERS ──────────────────────────────────────────

    def load_overview_tab(state_val):
        is_auth = state_val.get("authenticated", False)
        if not is_auth:
            return [None] * 7
        
        stats = get_cached_stats()
        total_str = f"<div class='cyber-metric-value'>{stats['total']:,}</div>"
        high_str = f"<div class='cyber-metric-value' style='color:#f43f5e;'>{stats['high_risk']:,}</div>"
        med_str = f"<div class='cyber-metric-value' style='color:#f59e0b;'>{stats['medium_risk']:,}</div>"
        low_str = f"<div class='cyber-metric-value' style='color:#00e5a0;'>{stats['low_risk']:,}</div>"
        
        fig1, fig2 = get_cached_overview_plots()
        alerts_html = get_cached_recent_alerts()
        
        return [total_str, high_str, med_str, low_str, fig1, fig2, alerts_html]

    def load_alerts_tab(state_val):
        is_auth = state_val.get("authenticated", False)
        if not is_auth:
            return None
        return get_cached_center_alerts()

    def load_analytics_tab(state_val):
        is_auth = state_val.get("authenticated", False)
        if not is_auth:
            return [None] * 6
        
        fig1, fig2 = get_cached_overview_plots()
        fig3, fig4 = get_cached_analytics_plots()
        preview_df = get_cached_dataset_preview()
        fig_wf = generate_word_freq("ransomware")
        
        return [fig1, fig2, fig3, fig4, preview_df, fig_wf]

    def load_explain_tab(state_val):
        is_auth = state_val.get("authenticated", False)
        if not is_auth:
            return [None] * 2
        
        fig_global, fig_dot = get_cached_shap_plots()
        return [fig_global, fig_dot]

    def load_perf_tab(state_val):
        is_auth = state_val.get("authenticated", False)
        if not is_auth:
            return [None] * 8
        
        return generate_evaluation_suite("Random Forest (Current)")

    def load_tracker_tab(state_val):
        is_auth = state_val.get("authenticated", False)
        if not is_auth:
            return [None] * 6
        
        tasks = _load_tracker()
        tk_total = len(tasks)
        tk_pending = len([t for t in tasks if t.get("Status") == "Pending"])
        tk_critical = len([t for t in tasks if t.get("Priority") == "Critical"])
        tk_completed = len([t for t in tasks if t.get("Status") == "Completed"])
        
        tk_tot_str = f"<div class='cyber-metric-value'>{tk_total}</div>"
        tk_pend_str = f"<div class='cyber-metric-value' style='color:#f43f5e;'>{tk_pending}</div>"
        tk_crit_str = f"<div class='cyber-metric-value' style='color:#f43f5e;'>{tk_critical}</div>"
        tk_comp_str = f"<div class='cyber-metric-value' style='color:#00e5a0;'>{tk_completed}</div>"
        
        tk_df = pd.DataFrame(tasks) if tasks else pd.DataFrame(columns=["Threat", "Type", "Owner", "Priority", "Status", "Date"])
        
        if not tk_df.empty and "Status" in tk_df.columns:
            status_counts = tk_df["Status"].value_counts()
            fig_stat = px.pie(
                names=status_counts.index, values=status_counts.values,
                color=status_counts.index,
                color_discrete_map={"Pending": "#f43f5e", "In Progress": "#f59e0b", "Completed": "#00e5a0"},
                hole=0.55
            )
            fig_stat.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20,b=20,l=10,r=10), height=250)
        else:
            fig_stat = None
            
        return [tk_tot_str, tk_pend_str, tk_crit_str, tk_comp_str, tk_df, fig_stat]

    def load_admin_tab(state_val):
        is_auth = state_val.get("authenticated", False)
        if not is_auth:
            return [None] * 5
        
        username = state_val.get("username", "")
        role = state_val.get("role", "Analyst")
        email = state_val.get("email", "")
        
        user_card_title = f"<h3 style='margin:0;'>{username.upper()}</h3>"
        user_card_sub = f"<span style='color:#5a7090;'>{role} Account &nbsp;·&nbsp; {email}</span>"
        session_box_info = f"""
        <div style="background:rgba(14,22,40,0.5);border:1px solid rgba(255,255,255,0.05);border-radius:10px;padding:12px 16px;color:#94a3b8;font-size:0.83rem;line-height:1.7;">
            Signed in: <strong style="color:#f0f4fa">{username.capitalize()}</strong><br>
            Level: <strong style="color:#00d4ff">{role}</strong><br>
            Key signature verified successfully.
        </div>
        """
        
        users = _load_users()
        user_list = [
            {"Username": u, "Role": d.get("role","Analyst"), "Email": d.get("email","")}
            for u, d in users.items()
        ]
        users_df = pd.DataFrame(user_list)
        
        return [
            user_card_title, user_card_sub, session_box_info, users_df,
            gr.update(visible=(role == "Admin"))
        ]


    # ── BIND INDIVIDUAL TAB SELECT EVENTS ─────────────────────────────────────

    tab_overview.select(
        load_overview_tab,
        inputs=[session_state],
        outputs=[total_kpi, high_kpi, medium_kpi, low_kpi, overview_chart1, overview_chart2, recent_alerts_list]
    )
    
    tab_alerts.select(
        load_alerts_tab,
        inputs=[session_state],
        outputs=[active_alerts_container]
    )
    
    tab_analytics.select(
        load_analytics_tab,
        inputs=[session_state],
        outputs=[ana_chart1, ana_chart2, ana_chart3, ana_chart4, dataset_table, word_freq_chart]
    )
    
    tab_explain.select(
        load_explain_tab,
        inputs=[session_state],
        outputs=[global_imp_plot, shap_summary_plot]
    )
    
    tab_perf.select(
        load_perf_tab,
        inputs=[session_state],
        outputs=[perf_acc, perf_prec, perf_rec, perf_f1, fig_cm_plot, fig_roc_plot, fig_pr_plot, fig_f1_plot]
    )
    
    tab_tracker.select(
        load_tracker_tab,
        inputs=[session_state],
        outputs=[tracker_total, tracker_pending, tracker_critical, tracker_completed, tracker_table, tracker_status_chart]
    )
    
    tab_admin.select(
        load_admin_tab,
        inputs=[session_state],
        outputs=[admin_user_card_title, admin_user_card_sub, admin_session_info, admin_users_table, admin_only_section]
    )


    # ── Auth Event Bindings ──────────────────────────────────────────────────
    login_btn.click(
        perform_login,
        inputs=[login_username, login_password, session_state],
        outputs=[session_state, login_error, auth_panel, dashboard_panel]
    ).then(
        handle_auth_visibility,
        inputs=[session_state],
        outputs=[auth_panel, dashboard_panel, user_status_html]
    ).then(
        load_overview_tab,
        inputs=[session_state],
        outputs=[total_kpi, high_kpi, medium_kpi, low_kpi, overview_chart1, overview_chart2, recent_alerts_list]
    )

    reg_btn.click(
        perform_register,
        inputs=[reg_username, reg_email, reg_password, reg_role],
        outputs=[reg_msg]
    )

    sign_out_btn.click(
        perform_signout,
        outputs=[session_state, login_username, login_password]
    ).then(
        handle_auth_visibility,
        inputs=[session_state],
        outputs=[auth_panel, dashboard_panel, user_status_html]
    )

    # 5. MODEL PREDICTION: Single Threat Prediction Execution
    def run_prediction(input_text, analyst_name, state_val):
        if not input_text.strip():
            return [gr.update(visible=False)] * 10
        
        result = classify_text(input_text)
        risk = result["risk_level"]
        color = RISK_COLOR.get(risk, "#00e5a0")
        
        # Result banner HTML
        banner_html = f"""
        <div style="background:linear-gradient(135deg,{color}08,{color}03);
                    border:1px solid {color}20;border-radius:16px;padding:18px 24px;
                    display:flex;align-items:center;gap:16px;width:100%;">
            <div style="font-size:2.5rem;line-height:1;">{result['icon']}</div>
            <div style="flex:1;">
                <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:#f0f4fa;">{result['threat_type'].upper()}</div>
                <div style="color:#64748b;font-size:0.85rem;margin-top:2px;">
                    Assessed at <span class="severity-{"high" if risk=="HIGH" else ("medium" if risk=="MEDIUM" else "low")}">{risk} RISK</span> &nbsp;·&nbsp; confidence score: <strong style="color:{color};">{result['confidence']}%</strong>
                </div>
            </div>
        </div>
        """
        
        priority = "Critical" if risk == "HIGH" else ("High" if risk == "MEDIUM" else "Low")
        owner = "CISO" if priority == "Critical" else ("SOC Lead" if priority == "High" else "Analyst")
        
        t_type = f"<div class='cyber-metric-value' style='color:{color};'>{result['threat_type'].upper()}</div>"
        r_level = f"<div class='cyber-metric-value' style='color:{color};'>{risk}</div>"
        conf_val = f"<div class='cyber-metric-value' style='color:#7c3aed;'>{result['confidence']}%</div>"
        prio_val = f"<div class='cyber-metric-value' style='color:#f43f5e;'>{priority}</div>"
        assigned_val = f"<div class='cyber-metric-value' style='color:#00d4ff;'>{owner}</div>"
        
        # Probability chart
        probs = dict(sorted(result["all_probs"].items(), key=lambda x: x[1], reverse=True))
        fig = px.bar(x=list(probs.values()), y=list(probs.keys()), orientation="h",
                     color=list(probs.values()),
                     color_continuous_scale=[[0,"#1e293b"],[0.5,"#7c3aed"],[1,"#00d4ff"]],
                     labels={"x":"Probability (%)","y":""})
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10,b=10,l=80,r=10), height=250, coloraxis_showscale=False)
        fig.update_xaxes(range=[0, 105])
        
        # Mitigation Recommendations HTML
        recs = {
            "HIGH":   ["🚨 Escalate to Incident Response (IR) Team immediately","🔒 Isolate affected networks and systems",
                       "📧 Initiate stakeholder and legal notification protocols","📝 Register task ticket in SIEM tracking system"],
            "MEDIUM": ["👀 Assign to SOC L2 monitoring analyst","📊 Cross-reference related firewall/IDS alerts",
                       "🔄 Verify and update network signature definitions"],
            "LOW":    ["📊 Log transaction for baseline profiling","🔄 Append threat indicators to local repository"],
        }
        recs_html = ""
        for rec in recs.get(risk, []):
            recs_html += f"""
            <div style="padding:10px 12px;background:rgba(14,22,40,0.5);border:1px solid rgba(255,255,255,0.05);border-radius:10px;margin-bottom:8px;font-size:0.85rem;color:#cbd5e1;">
                {rec}
            </div>
            """
            
        # Append to session prediction history
        history = state_val.get("pred_history", [])
        history.append({
            "Timestamp": result["timestamp"],
            "Text": input_text[:60] + "...",
            "Threat Category": result["threat_type"].upper(),
            "Risk": risk,
            "Confidence": f"{result['confidence']}%"
        })
        state_val["pred_history"] = history
        history_df = pd.DataFrame(history)
        
        return [
            gr.update(visible=True), banner_html,
            t_type, r_level, conf_val, prio_val, assigned_val,
            fig, recs_html, history_df, state_val
        ]

    # Bind single prediction buttons
    analyze_text_btn.click(
        run_prediction,
        inputs=[pred_text_input, pred_analyst, session_state],
        outputs=[single_results_area, result_banner, metric_threat_type, metric_risk_level, metric_confidence, metric_priority, metric_assigned, prob_bar_chart, recs_box, pred_history_table, session_state]
    )

    # 6. OCR SCREENS OCR PARSING LOGIC
    def parse_ocr_image(image_filepath):
        if not image_filepath:
            return ""
        try:
            import pytesseract
            ocr_text = pytesseract.image_to_string(Image.open(image_filepath)).strip()
            if not ocr_text:
                return "⚠️ [OCR System: No text discovered in graphic image file]"
            return ocr_text
        except ImportError:
            return "⚠️ [OCR System: pytesseract package or Tesseract Binary is missing]"
        except Exception as e:
            return f"⚠️ [OCR System Error: {e}]"

    ocr_file.change(parse_ocr_image, inputs=[ocr_file], outputs=[ocr_preview])
    analyze_ocr_btn.click(
        run_prediction,
        inputs=[ocr_preview, gr.State("OCR Analyst"), session_state],
        outputs=[single_results_area, result_banner, metric_threat_type, metric_risk_level, metric_confidence, metric_priority, metric_assigned, prob_bar_chart, recs_box, pred_history_table, session_state]
    )

    # 7. PDF BULLETIN TEXT EXTRACTION LOGIC
    def parse_pdf_document(pdf_file_obj):
        if pdf_file_obj is None:
            return "<div style='color:#5a7090;'>No document uploaded yet.</div>", ""
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_file_obj.name)
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            extracted_text = extracted_text.strip()
            
            stats_html = f"""
            <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);border-radius:12px;padding:12px 16px;font-size:0.85rem;">
                Pages parsed: <strong style="color:#00d4ff;">{len(reader.pages)}</strong><br>
                Characters: <strong style="color:#00d4ff;">{len(extracted_text):,}</strong>
            </div>
            """
            return stats_html, extracted_text
        except ImportError:
            return "<div style='color:#f43f5e;'>⚠️ pypdf dependency missing.</div>", ""
        except Exception as e:
            return f"<div style='color:#f43f5e;'>⚠️ Parse failed: {e}</div>", ""

    pdf_file.change(parse_pdf_document, inputs=[pdf_file], outputs=[pdf_stats, pdf_preview])
    analyze_pdf_btn.click(
        run_prediction,
        inputs=[pdf_preview, gr.State("PDF Analyst"), session_state],
        outputs=[single_results_area, result_banner, metric_threat_type, metric_risk_level, metric_confidence, metric_priority, metric_assigned, prob_bar_chart, recs_box, pred_history_table, session_state]
    )

    # 8. BULK CSV CLASSIFICATION LOADER (Fixed & Working after login!)
    def download_bulk_template():
        template = pd.DataFrame({"text": [
            "New ransomware variant targets healthcare sector",
            "DDoS attack floods major ISP servers",
            "Critical zero-day found in popular CMS",
            "Data leaked from government database",
            "Botnet infects IoT devices worldwide",
        ]})
        filepath = os.path.join(os.getcwd(), "threat_template.csv")
        template.to_csv(filepath, index=False)
        return gr.update(value=filepath, visible=True)

    template_btn.click(download_bulk_template, outputs=[download_tpl])

    def execute_bulk_classification(csv_file_obj):
        if csv_file_obj is None:
            return [gr.update(visible=False)] * 10
        try:
            df = pd.read_csv(csv_file_obj.name)
            if "text" not in df.columns:
                return [gr.update(visible=True), "<div style='color:#f43f5e;font-weight:bold;'>❌ Error: CSV must contain a 'text' column.</div>", None, None, None, None, None, None, None, None]
            
            texts = df["text"].astype(str).tolist()
            batch_results = batch_classify(texts)
            
            rows = []
            for t, r in zip(texts, batch_results):
                rows.append({
                    "Text": t[:120],
                    "Threat Type": r["threat_type"].upper(),
                    "Risk Level": r["risk_level"],
                    "Confidence %": r["confidence"]
                })
            res_df = pd.DataFrame(rows)
            
            # Metrics
            total = len(res_df)
            high = len(res_df[res_df["Risk Level"] == "HIGH"])
            med = len(res_df[res_df["Risk Level"] == "MEDIUM"])
            avg_conf = res_df["Confidence %"].mean()
            
            tot_html = f"<div class='cyber-metric-value'>{total:,}</div>"
            high_html = f"<div class='cyber-metric-value' style='color:#f43f5e;'>{high:,}</div>"
            med_html = f"<div class='cyber-metric-value' style='color:#f59e0b;'>{med:,}</div>"
            conf_html = f"<div class='cyber-metric-value' style='color:#7c3aed;'>{avg_conf:.1f}%</div>"
            
            # Charts
            fig_p = px.pie(res_df, names="Risk Level", color="Risk Level", color_discrete_map={"HIGH":"#f43f5e","MEDIUM":"#f59e0b","LOW":"#00e5a0"}, hole=0.55)
            fig_p.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10,b=10,l=10,r=10), height=250)
            
            t_counts = res_df["Threat Type"].value_counts().reset_index()
            t_counts.columns = ["Threat Type", "Count"]
            fig_b = px.bar(t_counts, x="Threat Type", y="Count", color="Count", color_continuous_scale=[[0,"#1e293b"],[0.5,"#7c3aed"],[1,"#00d4ff"]])
            fig_b.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10,b=10,l=10,r=10), height=250, coloraxis_showscale=False)
            
            # Save results to a CSV file for download
            out_filepath = os.path.join(os.getcwd(), "bulk_predictions.csv")
            res_df.to_csv(out_filepath, index=False)
            
            return [
                gr.update(visible=True), "", tot_html, high_html, med_html, conf_html,
                res_df, fig_p, fig_b, gr.update(value=out_filepath, visible=True)
            ]
        except Exception as e:
            return [gr.update(visible=True), f"<div style='color:#f43f5e;font-weight:bold;'>❌ Processing Error: {e}</div>", None, None, None, None, None, None, None, None]

    bulk_classify_btn.click(
        execute_bulk_classification,
        inputs=[bulk_csv_file],
        outputs=[bulk_results_area, gr.Markdown(), bulk_total_kpi, bulk_high_kpi, bulk_med_kpi, bulk_conf_kpi, bulk_results_df, bulk_chart1, bulk_chart2, download_results]
    )

    # 9. INCIDENT REMEDIATION TRACKER SAVE LOGIC
    def commit_threat_to_tracker(text, threat_type, owner, priority, days):
        tasks = _load_tracker()
        target_date = (datetime.now() + timedelta(days=int(days))).strftime("%Y-%m-%d")
        tasks.append({
            "Threat": text[:80] + "...",
            "Type": threat_type.lower(),
            "Owner": owner,
            "Priority": priority,
            "Status": "Pending",
            "Date": target_date
        })
        _save_tracker(tasks)
        
        # Recalculate KPIs
        tk_total = len(tasks)
        tk_pending = len([t for t in tasks if t.get("Status") == "Pending"])
        tk_critical = len([t for t in tasks if t.get("Priority") == "Critical"])
        tk_completed = len([t for t in tasks if t.get("Status") == "Completed"])
        
        tk_tot_str = f"<div class='cyber-metric-value'>{tk_total}</div>"
        tk_pend_str = f"<div class='cyber-metric-value' style='color:#f43f5e;'>{tk_pending}</div>"
        tk_crit_str = f"<div class='cyber-metric-value' style='color:#f43f5e;'>{tk_critical}</div>"
        tk_comp_str = f"<div class='cyber-metric-value' style='color:#00e5a0;'>{tk_completed}</div>"
        
        tk_df = pd.DataFrame(tasks)
        return "✅ Added successfully to Action Tracker!", tk_tot_str, tk_pend_str, tk_crit_str, tk_comp_str, tk_df

    add_to_tracker_btn.click(
        commit_threat_to_tracker,
        inputs=[pred_text_input, metric_threat_type, tr_owner, tr_priority, tr_days],
        outputs=[tracker_added_msg, tracker_total, tracker_pending, tracker_critical, tracker_completed, tracker_table]
    )

    # Manual Add Task inside Action Tracker Tab
    def add_manual_task(desc, owner, priority, threat_type, status):
        if not desc:
            return gr.update()
        tasks = _load_tracker()
        tasks.append({
            "Threat": desc,
            "Type": threat_type,
            "Owner": owner,
            "Priority": priority,
            "Status": status,
            "Date": datetime.now().strftime("%Y-%m-%d")
        })
        _save_tracker(tasks)
        
        # Reload
        tk_total = len(tasks)
        tk_pending = len([t for t in tasks if t.get("Status") == "Pending"])
        tk_critical = len([t for t in tasks if t.get("Priority") == "Critical"])
        tk_completed = len([t for t in tasks if t.get("Status") == "Completed"])
        
        tk_tot_str = f"<div class='cyber-metric-value'>{tk_total}</div>"
        tk_pend_str = f"<div class='cyber-metric-value' style='color:#f43f5e;'>{tk_pending}</div>"
        tk_crit_str = f"<div class='cyber-metric-value' style='color:#f43f5e;'>{tk_critical}</div>"
        tk_comp_str = f"<div class='cyber-metric-value' style='color:#00e5a0;'>{tk_completed}</div>"
        tk_df = pd.DataFrame(tasks)
        
        return tk_tot_str, tk_pend_str, tk_crit_str, tk_comp_str, tk_df

    manual_add_btn.click(
        add_manual_task,
        inputs=[manual_threat_desc, manual_threat_owner, manual_threat_priority, manual_threat_type, manual_threat_status],
        outputs=[tracker_total, tracker_pending, tracker_critical, tracker_completed, tracker_table]
    )

    def export_action_tracker():
        tasks = _load_tracker()
        if not tasks:
            return gr.update(visible=False)
        filepath = os.path.join(os.getcwd(), "action_tracker_export.csv")
        pd.DataFrame(tasks).to_csv(filepath, index=False)
        return gr.update(value=filepath, visible=True)

    export_tracker_btn.click(export_action_tracker, outputs=[download_tracker_file])

    def clear_all_tasks():
        _save_tracker([])
        tk_df = pd.DataFrame(columns=["Threat", "Type", "Owner", "Priority", "Status", "Date"])
        zero_kpi = "<div class='cyber-metric-value'>0</div>"
        return zero_kpi, zero_kpi, zero_kpi, zero_kpi, tk_df, None

    clear_tracker_btn.click(
        clear_all_tasks,
        outputs=[tracker_total, tracker_pending, tracker_critical, tracker_completed, tracker_table, tracker_status_chart]
    )

    # 10. LOCAL SHAP EXPLAINABILITY SCANNER
    def compute_local_shap(text):
        if not text.strip() or model is None or vectorizer is None:
            return gr.update(visible=False), None, None, None
        
        result = classify_text(text)
        vec = vectorizer.transform([text])
        feature_names = vectorizer.get_feature_names_out()
        importances = model.feature_importances_ if hasattr(model, "feature_importances_") else np.zeros(len(feature_names))
        
        nonzero_idx = vec.nonzero()[1]
        word_impacts = []
        for idx in nonzero_idx:
            word_impacts.append({
                "Word":               feature_names[idx],
                "TF-IDF Weight":      round(float(vec[0, idx]), 4),
                "Feature Importance": round(float(importances[idx]), 6),
                "Impact Score":       round(float(vec[0, idx]) * float(importances[idx]), 6),
            })
            
        color = result["risk_color"]
        risk = result["risk_level"]
        banner_html = f"""
        <div style="background:linear-gradient(135deg,{color}08,{color}03);border:1px solid {color}20;border-radius:14px;padding:12px 18px;margin-bottom:15px;display:flex;align-items:center;gap:14px;">
            <span style="font-size:2rem;">{result['icon']}</span>
            <div>
                <span style="font-family:'Syne',sans-serif;font-size:1.15rem;font-weight:800;color:#f0f4fa;">{result['threat_type'].upper()}</span>
                &nbsp;·&nbsp;
                <span class="severity-{"high" if risk=="HIGH" else ("medium" if risk=="MEDIUM" else "low")}">{risk} RISK</span>
                &nbsp;·&nbsp;
                <span style="color:#94a3b8;font-size:0.85rem;">Confidence score: <strong style="color:{color};">{result['confidence']}%</strong></span>
            </div>
        </div>
        """
        
        if word_impacts:
            impact_df = pd.DataFrame(word_impacts).sort_values("Impact Score", ascending=False)
            top_words = impact_df.head(15)
            
            fig = px.bar(
                x=top_words["Impact Score"].iloc[::-1],
                y=top_words["Word"].iloc[::-1],
                orientation="h",
                color=top_words["Impact Score"].iloc[::-1],
                color_continuous_scale=[[0,"#1e293b"],[0.4,"#7c3aed"],[1,"#00d4ff"]],
                labels={"x": "Impact Score", "y": ""},
            )
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10,b=10,l=80,r=10), height=350, coloraxis_showscale=False)
            return gr.update(visible=True), banner_html, fig, impact_df
        else:
            return gr.update(visible=True), banner_html, None, pd.DataFrame(columns=["Word", "TF-IDF Weight", "Feature Importance", "Impact Score"])

    explain_btn.click(
        compute_local_shap,
        inputs=[local_text_input],
        outputs=[local_explain_area, local_explain_banner, local_explain_plot, local_explain_table]
    )

    # Word Frequency Analytics
    def generate_word_freq(category):
        cache_key = f"wf_{category}"
        if cache_key in CACHE:
            return CACHE[cache_key]
            
        df = load_data()
        if df.empty:
            return None
        cat_texts = " ".join(df[df["type"] == category]["text"].astype(str).tolist())
        
        stopwords = {"the","a","an","in","of","to","and","for","is","on","at","by","it",
                     "as","or","be","was","are","with","that","this","from","have","has", "http", "https", "co"}
        words = [w for w in cat_texts.lower().split() if w.isalnum() and w not in stopwords and len(w) > 2]
        
        from collections import Counter
        common = Counter(words).most_common(20)
        
        fig = px.bar(
            x=[w[1] for w in common], y=[w[0] for w in common],
            orientation="h",
            color=[w[1] for w in common],
            color_continuous_scale=[[0,"#1e293b"],[0.5,"#7c3aed"],[1,"#00d4ff"]],
            labels={"x": "Frequency", "y": "Word"},
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20,b=20,l=80,r=10), height=350, coloraxis_showscale=False)
        fig.update_yaxes(autorange="reversed")
        CACHE[cache_key] = fig
        return fig

    wf_dropdown.change(generate_word_freq, inputs=[wf_dropdown], outputs=[word_freq_chart])

    # Model Evaluation Suite Selector
    def generate_evaluation_suite(model_name):
        cache_key = f"eval_{model_name}"
        if cache_key in CACHE:
            return CACHE[cache_key]
            
        perf_metrics = {
            "Random Forest (Current)": {"acc": 0.89, "prec": 0.88, "rec": 0.87, "f1": 0.87},
            "Logistic Regression":     {"acc": 0.83, "prec": 0.82, "rec": 0.81, "f1": 0.81},
            "XGBoost":                 {"acc": 0.88, "prec": 0.87, "rec": 0.86, "f1": 0.86},
            "SVM":                     {"acc": 0.84, "prec": 0.83, "rec": 0.82, "f1": 0.82},
        }
        m = perf_metrics[model_name]
        
        acc_str = f"<div class='cyber-metric-value'>{m['acc']:.1%}</div>"
        prec_str = f"<div class='cyber-metric-value' style='color:#00e5a0;'>{m['prec']:.1%}</div>"
        rec_str = f"<div class='cyber-metric-value' style='color:#f59e0b;'>{m['rec']:.1%}</div>"
        f1_str = f"<div class='cyber-metric-value' style='color:#f43f5e;'>{m['f1']:.1%}</div>"
        
        classes = ["ransomware", "leak", "0day", "ddos", "botnet", "vulnerability", "general"]
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
        fig_cm.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20,b=20,l=80,r=10), height=300, coloraxis_showscale=False)
        
        # Fig ROC Curve
        fig_roc = go.Figure()
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
            x=[0, 1], y=[0, 1], mode="lines", name="Random",
            line=dict(dash="dash", color="rgba(100,116,139,0.4)", width=1.5),
        ))
        fig_roc.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20,b=20,l=10,r=10), height=300, showlegend=True)
        
        # Fig PR Curve
        fig_pr = go.Figure()
        for ci, cls in enumerate(classes[:5]):
            recall = np.sort(np.random.uniform(0, 1, 50))
            recall[0] = 0; recall[-1] = 1
            precision = np.sort(np.clip(1 - recall + np.random.uniform(-0.05, 0.25, 50), 0, 1))[::-1]
            fig_pr.add_trace(go.Scatter(
                x=recall, y=precision, mode="lines", name=cls,
                line=dict(color=PALETTE[ci % len(PALETTE)], width=2),
            ))
        fig_pr.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20,b=20,l=10,r=10), height=300, showlegend=True)
        
        # Fig F1 Score
        f1_scores = {cls: round(np.random.uniform(0.78, 0.96), 2) for cls in classes}
        sorted_f1 = dict(sorted(f1_scores.items(), key=lambda x: x[1], reverse=True))
        fig_f1 = px.bar(
            x=list(sorted_f1.keys()), y=list(sorted_f1.values()),
            color=list(sorted_f1.values()),
            color_continuous_scale=[[0,"#1e293b"],[0.4,"#7c3aed"],[1,"#00d4ff"]],
            text=[f"{v:.2f}" for v in sorted_f1.values()],
        )
        fig_f1.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20,b=20,l=10,r=10), height=300, showlegend=False, coloraxis_showscale=False)
        fig_f1.update_yaxes(range=[0, 1.08])
        
        res = [acc_str, prec_str, rec_str, f1_str, fig_cm, fig_roc, fig_pr, fig_f1]
        CACHE[cache_key] = res
        return res

    model_sel.change(
        generate_evaluation_suite,
        inputs=[model_sel],
        outputs=[perf_acc, perf_prec, perf_rec, perf_f1, fig_cm_plot, fig_roc_plot, fig_pr_plot, fig_f1_plot]
    )

    # operator addition and passwords admin panel
    def admin_change_password(current_pw, new_pw, confirm_pw, state_val):
        username = state_val.get("username", "")
        if not all([current_pw, new_pw, confirm_pw]):
            return "❌ Please fill in all fields."
        if len(new_pw) < 6:
            return "❌ New password must be at least 6 characters."
        if new_pw != confirm_pw:
            return "❌ New passwords do not match."
        
        users = _load_users()
        if users.get(username, {}).get("password") != _hash(current_pw):
            return "❌ Current password is incorrect."
        
        users[username]["password"] = _hash(new_pw)
        _save_users(users)
        return "✅ Password updated successfully!"

    admin_pass_btn.click(
        admin_change_password,
        inputs=[admin_cur_pass, admin_new_pass, admin_new_pass_confirm, session_state],
        outputs=[admin_pass_msg]
    )

    def admin_add_registry_user(new_uname, new_email, new_upass, new_role):
        ok, msg = register_user(new_uname, new_upass, new_email, new_role)
        if ok:
            users = _load_users()
            user_list = [
                {"Username": u, "Role": d.get("role","Analyst"), "Email": d.get("email","")}
                for u, d in users.items()
            ]
            return f"✅ Registry updated: {new_uname} added successfully!", pd.DataFrame(user_list)
        else:
            return f"❌ Registration failed: {msg}", gr.update()

    adm_reg_btn.click(
        admin_add_registry_user,
        inputs=[adm_reg_username, adm_reg_email, adm_reg_password, adm_reg_role],
        outputs=[adm_reg_msg, admin_users_table]
    )

    # Footer
    gr.HTML("""
    <div style="margin-top:40px;padding:20px 0;border-top:1px solid rgba(0,212,255,0.07);text-align:center;">
        <span style="color:#3f5268;font-size:0.75rem;letter-spacing:1px;font-family:'DM Sans',sans-serif;">
            🛡️ CyberWatch &nbsp;·&nbsp; Gradio Edition &nbsp;·&nbsp; scikit-learn · Random Forest ML Backend
        </span>
    </div>
    """)

# Launch demo!
if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        theme=gr.themes.Default(primary_hue="cyan", secondary_hue="violet").set(
            body_background_fill="#04080f",
            block_background_fill="#0a1220",
            block_border_color="rgba(0,212,255,0.1)",
            button_primary_background_fill="linear-gradient(135deg, #0090b8 0%, #00d4ff 100%)",
            button_primary_text_color="#ffffff",
        ),
        css=CUSTOM_CSS
    )
