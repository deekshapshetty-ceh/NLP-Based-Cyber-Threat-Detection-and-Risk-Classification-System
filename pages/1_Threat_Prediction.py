"""
🔮 Threat Prediction — Classify any text for cyber threats.
Supports: Text · Image (OCR) · PDF · Bulk CSV
"""

import io
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

from config.theme import (
    inject_css, metric_card, init_session_state,
    render_footer, page_header, severity_badge, chart_layout, sidebar_branding,
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
from config.constants import RISK_MAP, RISK_COLOR, THREAT_DESCRIPTIONS
from utils.classifier import classify_text, batch_classify


st.set_page_config(
    page_title="Threat Intelligence Engine — CyberWatch",
    page_icon="🛡️",
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

RISK_COLOR_V2 = {"HIGH": "#f43f5e", "MEDIUM": "#f59e0b", "LOW": "#00e5a0"}

page_header(
    "Threat Intelligence Engine",
    "Analyze suspicious messages, URLs, emails, images, PDFs, or bulk datasets for cyber threats.",
    "🛡️",
    label="Multi-Modal Analysis Engine",
)

# ── Tab CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    color: #64748b;
    padding: 8px 20px;
    border-radius: 8px;
    border: 1px solid transparent;
    background: transparent;
    transition: all 0.2s;
}
div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color: #94a3b8;
    background: rgba(255,255,255,0.04);
}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color: #00d4ff;
    background: rgba(0,212,255,0.1);
    border-color: rgba(0,212,255,0.3);
}
div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] { background: transparent; }
div[data-testid="stTabs"] div[data-baseweb="tab-border"] { background: rgba(0,212,255,0.08); }
</style>
""", unsafe_allow_html=True)

tab_text, tab_image, tab_pdf, tab_csv = st.tabs([
    "📝  Text",
    "🖼️  Image (OCR)",
    "📄  PDF",
    "📊  Bulk CSV",
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — Text
# ──────────────────────────────────────────────────────────────────────────────
with tab_text:
    st.markdown("""
    <div style="color:#64748b;font-size:0.88rem;font-family:'DM Sans',sans-serif;
                margin:12px 0 8px">Paste a suspicious message, URL, or email to analyze</div>
    """, unsafe_allow_html=True)

    text_input = st.text_area(
        "Text input", height=155,
        placeholder='Example: "URGENT: Your account will be suspended unless you verify now. '
                    'Click http://phish.link/verify"',
        label_visibility="collapsed", key="text_mode_input",
    )

    col_name, col_btn, col_hint = st.columns([3, 1.4, 1.6])
    with col_name:
        analyst_name = st.text_input("Analyst name", value="SOC Analyst",
                                     placeholder="Your name for logging")
    with col_btn:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        analyze_text_btn = st.button("🔍  Analyze Threat", type="primary",
                                     use_container_width=True, key="analyze_text")
    with col_hint:
        st.markdown(
            f"<div style='height:52px;display:flex;align-items:flex-end;justify-content:flex-end;"
            f"color:#334155;font-size:0.78rem;font-family:DM Sans,sans-serif'>"
            f"{len(text_input)} chars · Ctrl+Enter to scan</div>",
            unsafe_allow_html=True,
        )

    text_to_classify = text_input if analyze_text_btn else None


# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — Image (OCR)
# ──────────────────────────────────────────────────────────────────────────────
with tab_image:
    st.markdown("""
    <div style="color:#64748b;font-size:0.88rem;font-family:'DM Sans',sans-serif;
                margin:12px 0 8px">
        Upload a screenshot or image — text will be extracted via OCR, then analyzed
    </div>
    """, unsafe_allow_html=True)

    img_file = st.file_uploader("Upload image",
                                 type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
                                 label_visibility="collapsed", key="img_uploader")
    ocr_text = ""
    if img_file:
        col_prev, col_ocr = st.columns([1, 1], gap="medium")
        with col_prev:
            st.image(img_file, caption="Uploaded image", use_container_width=True)
        with col_ocr:
            st.markdown("""
            <div style="font-size:0.75rem;letter-spacing:2px;text-transform:uppercase;
                        color:#334155;font-weight:700;margin-bottom:8px;
                        font-family:'DM Sans',sans-serif">◈ Extracted Text (OCR)</div>
            """, unsafe_allow_html=True)
            try:
                import pytesseract
                from PIL import Image as PILImage
                pil_img = PILImage.open(img_file)
                ocr_text = pytesseract.image_to_string(pil_img).strip()
                if ocr_text:
                    st.text_area("OCR output", value=ocr_text, height=160,
                                 label_visibility="collapsed", key="ocr_preview")
                else:
                    st.warning("No text detected in the image.")
            except ImportError:
                st.error("⚠️ pytesseract is not installed. "
                         "Run `pip install pytesseract` and install Tesseract-OCR to enable this feature.")
            except Exception as e:
                st.error(f"OCR failed: {e}")

    img_analyze_btn = st.button("🔍  Analyze Extracted Text", type="primary",
                                 disabled=not bool(ocr_text), key="analyze_image")
    ocr_to_classify = ocr_text if img_analyze_btn else None


# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — PDF
# ──────────────────────────────────────────────────────────────────────────────
with tab_pdf:
    st.markdown("""
    <div style="color:#64748b;font-size:0.88rem;font-family:'DM Sans',sans-serif;
                margin:12px 0 8px">
        Upload a PDF report, threat bulletin, or phishing email export
    </div>
    """, unsafe_allow_html=True)

    pdf_file = st.file_uploader("Upload PDF", type=["pdf"],
                                 label_visibility="collapsed", key="pdf_uploader")
    pdf_text = ""
    if pdf_file:
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(pdf_file.read()))
            pages_text = [p.extract_text() for p in reader.pages if p.extract_text()]
            pdf_text = "\n\n".join(t.strip() for t in pages_text).strip()

            col_info, col_content = st.columns([1, 2], gap="medium")
            with col_info:
                st.markdown(f"""
                <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);
                            border-radius:12px;padding:16px 20px;font-family:'DM Sans',sans-serif">
                    <div style="font-size:0.65rem;letter-spacing:2px;text-transform:uppercase;
                                color:#334155;font-weight:700;margin-bottom:10px">◈ PDF Info</div>
                    <div style="color:#94a3b8;font-size:0.85rem;line-height:2">
                        📄 Pages: <strong style="color:#00d4ff">{len(reader.pages)}</strong><br>
                        🔤 Chars: <strong style="color:#00d4ff">{len(pdf_text):,}</strong><br>
                        📦 Size: <strong style="color:#00d4ff">{pdf_file.size/1024:.1f} KB</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_content:
                st.markdown("""
                <div style="font-size:0.75rem;letter-spacing:2px;text-transform:uppercase;
                            color:#334155;font-weight:700;margin-bottom:8px;
                            font-family:'DM Sans',sans-serif">◈ Extracted Text Preview</div>
                """, unsafe_allow_html=True)
                preview = pdf_text[:2000] + ("…" if len(pdf_text) > 2000 else "")
                st.text_area("PDF preview", value=preview, height=160,
                             label_visibility="collapsed", key="pdf_preview")
        except ImportError:
            st.error("⚠️ pypdf is not installed. Run `pip install pypdf` to enable PDF analysis.")
        except Exception as e:
            st.error(f"PDF extraction failed: {e}")

    pdf_analyze_btn = st.button("🔍  Analyze PDF Content", type="primary",
                                 disabled=not bool(pdf_text), key="analyze_pdf")
    pdf_to_classify = pdf_text if pdf_analyze_btn else None


# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — Bulk CSV
# ──────────────────────────────────────────────────────────────────────────────
with tab_csv:
    st.markdown("""
    <div style="color:#64748b;font-size:0.88rem;font-family:'DM Sans',sans-serif;
                margin:12px 0 8px">
        Upload a CSV with a <code style="color:#00d4ff;background:rgba(0,212,255,0.08);
        padding:1px 6px;border-radius:4px">text</code> column to classify multiple entries at once
    </div>
    """, unsafe_allow_html=True)

    col_ul, col_dl = st.columns([3, 1], gap="medium")
    with col_ul:
        csv_file = st.file_uploader("Upload CSV", type=["csv"],
                                     label_visibility="collapsed", key="csv_uploader")
    with col_dl:
        tpl = pd.DataFrame({"text": [
            "New ransomware variant targets healthcare sector",
            "DDoS attack floods major ISP servers",
            "Critical zero-day found in popular CMS",
        ]})
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.download_button("📄 Download Template", tpl.to_csv(index=False),
                           "threat_template.csv", "text/csv", use_container_width=True)

    if csv_file:
        upload_df = pd.read_csv(csv_file)
        if "text" not in upload_df.columns:
            st.error("❌ CSV must have a `text` column. Download the template above.")
        else:
            total = len(upload_df)
            st.info(f"📁 **{total:,} entries** detected. Click below to classify all rows.")

            if st.button("🔍  Run Bulk Classification", type="primary", key="analyze_bulk"):
                texts = upload_df["text"].astype(str).tolist()
                with st.spinner("Classifying all entries…"):
                    batch_results = batch_classify(texts)

                rows = [{"Text": t[:120], "Threat Type": r["threat_type"],
                          "Risk Level": r["risk_level"], "Confidence %": r["confidence"]}
                        for t, r in zip(texts, batch_results)]
                bdf = pd.DataFrame(rows)

                high = len(bdf[bdf["Risk Level"] == "HIGH"])
                med  = len(bdf[bdf["Risk Level"] == "MEDIUM"])
                avg_c = bdf["Confidence %"].mean()

                st.success(f"✅ Classified {total:,} entries successfully!")
                c1, c2, c3, c4 = st.columns(4)
                with c1: metric_card("Total",       f"{total:,}", "📊", color="#00d4ff")
                with c2: metric_card("High Risk",   f"{high:,}",  "🔴", color="#f43f5e")
                with c3: metric_card("Medium Risk", f"{med:,}",   "🟡", color="#f59e0b")
                with c4: metric_card("Avg Conf.",   f"{avg_c:.1f}%", "📈", color="#7c3aed")

                st.dataframe(bdf, hide_index=True, use_container_width=True, height=320)
                col_exp, _ = st.columns([1, 2])
                with col_exp:
                    st.download_button("📥 Download Results CSV", bdf.to_csv(index=False),
                                       "bulk_predictions.csv", "text/csv",
                                       use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# ── Shared Analysis Renderer ──────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────
def run_analysis(input_text: str, analyst: str = "SOC Analyst"):
    if not input_text.strip():
        st.warning("Please provide some text to analyze.")
        return

    with st.spinner("Running NLP classifier…"):
        result = classify_text(input_text)

    risk  = result["risk_level"]
    color = RISK_COLOR_V2.get(risk, "#00e5a0")

    # Result banner
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{color}08,{color}03);
                border:1px solid {color}20;border-radius:16px;padding:20px 24px;
                margin-bottom:20px;display:flex;align-items:center;gap:16px">
        <div style="font-size:2.2rem;filter:drop-shadow(0 0 10px {color}60)">{result['icon']}</div>
        <div style="flex:1">
            <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
                        color:#f0f4fa;letter-spacing:-0.3px">{result['threat_type'].upper()}</div>
            <div style="color:#64748b;font-size:0.85rem;font-family:'DM Sans',sans-serif;margin-top:2px">
                Classified with <strong style="color:{color}">{result['confidence']}%</strong> confidence
            </div>
        </div>
        <div>{severity_badge(risk)}</div>
    </div>
    """, unsafe_allow_html=True)

    priority = "Critical" if risk == "HIGH" else ("High" if risk == "MEDIUM" else "Low")
    owner    = "CISO"     if priority == "Critical" else ("SOC Lead" if priority == "High" else "Analyst")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: metric_card("Threat Type", result['threat_type'].upper(), result['icon'], color=color)
    with c2: metric_card("Risk Level",  risk,                          "⚠️",          color=color)
    with c3: metric_card("Confidence",  f"{result['confidence']}%",    "📊",          color="#7c3aed")
    with c4: metric_card("Priority",    priority,                      "🏷️",         color="#f43f5e" if priority == "Critical" else "#f59e0b")
    with c5: metric_card("Assigned To", owner,                         "👤",          color="#00d4ff")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col_chart, col_rec = st.columns([3, 2], gap="medium")
    with col_chart:
        st.markdown("#### 📊 Probability Distribution")
        probs = dict(sorted(result["all_probs"].items(), key=lambda x: x[1], reverse=True))
        fig = px.bar(x=list(probs.values()), y=list(probs.keys()), orientation="h",
                     color=list(probs.values()),
                     color_continuous_scale=[[0,"#1e293b"],[0.5,"#7c3aed"],[1,"#00d4ff"]],
                     labels={"x":"Probability (%)","y":""},
                     text=[f"{v}%" for v in probs.values()])
        fig.update_traces(textposition="outside", textfont=dict(size=11,color="#94a3b8"),
                          marker_line_width=0,
                          hovertemplate="<b>%{y}</b><br>%{x}%<extra></extra>")
        layout = chart_layout(height=320)
        layout["coloraxis_showscale"] = False
        layout["xaxis"]["range"] = [0, 105]
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

    with col_rec:
        st.markdown("#### 💡 Response Recommendations")
        recs = {
            "HIGH":   ["🚨 Escalate to CISO / IR Team immediately","🔒 Isolate affected systems",
                       "📧 Notify stakeholders & legal","📝 Create SIEM incident ticket",
                       "🔍 Correlate IOCs in threat intel"],
            "MEDIUM": ["👀 Assign to SOC L2 analyst","📊 Cross-reference SIEM alerts",
                       "🔄 Update IDS/IPS signatures","📝 Document in ticketing system"],
            "LOW":    ["📊 Log for trend analysis","🔄 Update threat intel database",
                       "📝 Include in daily briefing"],
        }
        for rec in recs.get(risk, []):
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:10px;padding:10px 14px;
                        background:rgba(14,22,40,0.5);border:1px solid rgba(255,255,255,0.05);
                        border-radius:10px;margin-bottom:8px;
                        font-family:'DM Sans',sans-serif;font-size:0.85rem;color:#94a3b8">
                {rec}
            </div>""", unsafe_allow_html=True)

    if risk == "HIGH":
        st.error("⚠️ **HIGH RISK** — Immediate escalation recommended! Notify CISO and initiate IR procedures.")
    elif risk == "MEDIUM":
        st.warning("⚡ **MEDIUM RISK** — Monitor closely and prepare response procedures.")
    else:
        st.success("✅ **LOW RISK** — Continue routine monitoring.")

    st.info(f"**{result['threat_type'].upper()}**: {THREAT_DESCRIPTIONS.get(result['threat_type'], 'Unknown threat type')}")

    with st.expander("📋 Add to Action Tracker", expanded=False):
        tr1, tr2, tr3 = st.columns(3)
        with tr1: task_owner = st.text_input("Task Owner", value=owner, key="task_owner")
        with tr2: target_date = st.date_input("Target Date", value=datetime.now() + timedelta(days=3), key="task_date")
        with tr3:
            task_priority = st.selectbox("Task Priority", ["Critical","High","Medium","Low"],
                                          index=0 if priority=="Critical" else 1, key="task_priority")
        if st.button("➕ Add to Tracker", key="add_tracker"):
            st.session_state.action_tracker.append({
                "Threat": input_text[:80], "Type": result["threat_type"],
                "Owner": task_owner, "Priority": task_priority,
                "Status": "Pending", "Date": str(target_date),
            })
            _save_tracker(st.session_state.action_tracker)
            st.success("✅ Added to Action Tracker!")

    st.session_state.prediction_history.append({
        "Analyst":     analyst,
        "Text":        input_text[:100],
        "Threat Type": result["threat_type"],
        "Risk Level":  result["risk_level"],
        "Confidence":  result["confidence"],
        "Priority":    priority,
        "Assigned To": owner,
        "Timestamp":   result["timestamp"],
    })


# ── Dispatch ──────────────────────────────────────────────────────────────────
if text_to_classify:
    run_analysis(text_to_classify, analyst_name)
elif ocr_to_classify:
    run_analysis(ocr_to_classify, "OCR Analyst")
elif pdf_to_classify:
    run_analysis(pdf_to_classify, "PDF Analyst")

# ── Prediction History ─────────────────────────────────────────────────────────
if st.session_state.prediction_history:
    with st.expander(f"🕐 Prediction History ({len(st.session_state.prediction_history)} entries)", expanded=False):
        st.dataframe(pd.DataFrame(st.session_state.prediction_history),
                     hide_index=True, use_container_width=True)

render_footer()
