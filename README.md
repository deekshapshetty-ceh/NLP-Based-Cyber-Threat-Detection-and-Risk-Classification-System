# 🛡️ CyberWatch — NLP Cyber Threat Intelligence System

> **Capstone Project** — Real-time cyber threat detection and classification
> using NLP (TF-IDF) and Random Forest, served via an interactive Streamlit dashboard.

---

## 📁 Project Structure

```
cyber_threat_app/
├── .gitignore                   # Excludes large binaries from git
├── .streamlit/
│   └── config.toml              # Streamlit dark theme configuration
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── app.py                       # Main entry — Home / Dashboard page
├── config/
│   ├── __init__.py
│   ├── constants.py             # Risk maps, colors, icons, descriptions
│   └── theme.py                 # CSS theme & reusable UI components
├── utils/
│   ├── __init__.py
│   ├── classifier.py            # Model loading & text classification
│   └── data_loader.py           # Dataset loading & statistics
├── pages/
│   ├── 1_Threat_Prediction.py   # Single-text threat analysis
│   ├── 2_Alert_Center.py        # High-risk threat alerts
│   ├── 3_Analytics.py           # Dashboard charts & analytics
│   ├── 4_Dataset_Explorer.py    # EDA & visualizations
│   ├── 5_Bulk_Prediction.py     # CSV batch classification
│   ├── 6_Action_Tracker.py      # SOC task management
│   ├── 7_Model_Performance.py   # Confusion matrix, ROC, PR curves
│   ├── 8_Feature_Importance.py  # TF-IDF feature analysis
│   └── 9_SHAP_Explainability.py # Model interpretability
├── models/
│   ├── attack_model.pkl         # Trained Random Forest classifier
│   └── vectorizer.pkl           # TF-IDF vectorizer
├── data/
│   └── tweets_final.csv         # Training / analysis dataset
└── scripts/
    └── twitter_monitor.py       # Optional live Twitter monitoring
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the dashboard
```bash
streamlit run app.py
```

### 3. Open in browser
```
http://localhost:8501
```

---

## 🧠 How It Works

```
Tweet / Text Input
      ↓
TF-IDF Vectorizer (44,289 features)
      ↓
Random Forest Classifier (100 trees)
      ↓
Threat Type: ransomware / ddos / leak / 0day / botnet / vulnerability
      ↓
Risk Level: HIGH / MEDIUM / LOW
      ↓
Dashboard Display + Alerts
```

---

## 🎯 Threat Categories

| Category      | Risk Level | Description                           |
|---------------|------------|---------------------------------------|
| ransomware    | 🔴 HIGH    | Ransomware attacks & extortion        |
| leak          | 🔴 HIGH    | Data breaches & credential leaks      |
| 0day          | 🔴 HIGH    | Zero-day exploit intelligence         |
| ddos          | 🟡 MEDIUM  | Distributed denial of service         |
| botnet        | 🟡 MEDIUM  | Botnet infections & C2 activity       |
| vulnerability | 🟢 LOW     | Known CVEs & security weaknesses      |
| general       | 🟢 LOW     | General cyber-security news           |

---

## 📊 Dashboard Pages

| # | Page                  | Description                                    |
|---|-----------------------|------------------------------------------------|
| 1 | **Home**              | KPI overview, threat distribution, recent alerts |
| 2 | **Threat Prediction** | Real-time single-text classification            |
| 3 | **Alert Center**      | High-risk threats requiring SOC attention       |
| 4 | **Analytics**         | Charts, risk breakdown, confidence histograms   |
| 5 | **Dataset Explorer**  | EDA with word clouds and text-length analysis   |
| 6 | **Bulk Prediction**   | CSV upload for batch classification             |
| 7 | **Action Tracker**    | SOC incident response task management           |
| 8 | **Model Performance** | Confusion matrix, ROC/PR curves, F1 scores     |
| 9 | **Feature Importance**| Top TF-IDF features driving classifications     |
| 10| **SHAP Explainability**| Global & local model interpretability          |

---

## 🌐 Deployment (Streamlit Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path**: `app.py`
5. Deploy!

> **Note:** The model files (`models/*.pkl`) and dataset (`data/*.csv`) must be
> included in the repo or managed via Git LFS for deployment.

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Port in use | `streamlit run app.py --server.port 8502` |
| Model not found | Ensure `models/attack_model.pkl` exists |

---

*Built with Streamlit · scikit-learn · TF-IDF · Random Forest · Plotly*
