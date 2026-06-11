🛡️ CyberWatch – NLP-Based Cyber Threat Detection & Risk Classification System

Project Overview

CyberWatch is an AI-powered Cyber Threat Intelligence System that automatically detects and classifies cybersecurity threats from textual data using Natural Language Processing (NLP) and Machine Learning.

The system analyzes cyber-related content such as security reports, threat intelligence feeds, tweets, messages, PDFs, and extracted image text to identify potential threats and assess their risk level.

The application is built using Streamlit and provides an interactive dashboard for real-time threat monitoring, analytics, bulk prediction, and explainable AI.


🎯 Objectives

* Detect cyber threats automatically from textual data.
* Classify threats into predefined cybersecurity categories.
* Assign risk levels based on threat severity.
* Assist SOC analysts in threat monitoring and incident response.
* Provide explainable AI insights for prediction transparency.


🧠 Machine Learning Pipeline

Input Text
↓
Text Preprocessing
↓
TF-IDF Vectorization (44,289 Features)
↓
Random Forest Classifier (100 Trees)
↓
Threat Classification
↓
Risk Assessment
↓
Interactive Dashboard Visualization

🔍 Threat Categories

| Threat Category | Risk Level | Description                                       |
| --------------- | ---------- | ------------------------------------------------- |
| Ransomware      | 🔴 High    | File encryption and extortion attacks             |
| Leak            | 🔴 High    | Data breaches and credential leaks                |
| 0-Day           | 🔴 High    | Zero-day vulnerability intelligence               |
| DDoS            | 🟡 Medium  | Distributed denial-of-service attacks             |
| Botnet          | 🟡 Medium  | Botnet activity and command-control communication |
| Vulnerability   | 🟢 Low     | Known security weaknesses and CVEs                |
| General         | 🟢 Low     | General cybersecurity discussions and news        |

📊 Dataset Information

* Dataset Size: 21,368 Records
* Number of Threat Categories: 7
* Feature Extraction Technique: TF-IDF
* Feature Count: 44,289 Features
* Machine Learning Model: Random Forest Classifier
* Training Source: Cyber Threat Intelligence Dataset

⚙️ Technologies Used

Programming Language

* Python

Machine Learning & NLP

* Scikit-Learn
* TF-IDF Vectorization
* Random Forest Classifier
* SHAP Explainability

Data Processing

* Pandas
* NumPy

Visualization

* Plotly
* Matplotlib
* Seaborn
* WordCloud

 Web Framework

* Streamlit

OCR & Document Processing

* Pytesseract
* Pillow
* PyPDF

✨ Key Features

 Real-Time Threat Prediction

* Single-text threat analysis
* Confidence score generation
* Risk-level classification

 OCR-Based Threat Analysis

* Extract text from uploaded images
* Analyze screenshots and threat intelligence images

 PDF Threat Analysis

* Extract and classify text from PDF documents

 Bulk Prediction

* Upload CSV files
* Analyze multiple threat records simultaneously

Alert Center

* Monitor high-risk threats
* SOC-focused incident tracking

 Analytics Dashboard

* Threat distribution
* Confidence analysis
* Risk-level visualization

Explainable AI

* SHAP-based model interpretation
* Feature importance visualization

 Action Tracker

* Track investigations
* Manage incident response activities

---
 📂 Project Structure

```text
CyberWatch/
│
├── app.py
├── README.md
├── requirements.txt
│
├── config/
│   ├── constants.py
│   └── theme.py
│
├── data/
│   ├── tweets_final.csv
│   ├── users.json
│   └── action_tracker.json
│
├── models/
│   ├── attack_model.pkl
│   └── vectorizer.pkl
│
├── pages/
│   ├── 1_Threat_Prediction.py
│   ├── 2_Alert_Center.py
│   ├── 3_Analytics.py
│   ├── 4_Dataset_Explorer.py
│   ├── 5_Bulk_Prediction.py
│   ├── 6_Action_Tracker.py
│   ├── 7_Model_Performance.py
│   ├── 8_Feature_Importance.py
│   └── 9_SHAP_Explainability.py
│
├── scripts/
│   └── twitter_monitor.py
│
└── utils/
    ├── classifier.py
    └── data_loader.py
```

- 🚀 Installation

Clone Repository

```bash
git clone https://github.com/deekshapshetty-ceh/NLP-Based-Cyber-Threat-Detection-and-Risk-Classification-System.git
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run Application

```bash
streamlit run app.py
```

Application will start at:

```text
http://localhost:8501
```

---
📈 Dashboard Modules

| Module              | Purpose                         |
| ------------------- | ------------------------------- |
| Home Dashboard      | System overview and KPIs        |
| Threat Prediction   | Real-time text classification   |
| Alert Center        | High-risk threat monitoring     |
| Analytics           | Charts and visual insights      |
| Dataset Explorer    | Exploratory data analysis       |
| Bulk Prediction     | CSV-based threat analysis       |
| Action Tracker      | Incident response management    |
| Model Performance   | Accuracy and evaluation metrics |
| Feature Importance  | Top TF-IDF features             |
| SHAP Explainability | Explain model decisions         |

---

🔮 Future Enhancements

* BERT-based threat classification
* Transformer models for improved accuracy
* Real-time social media monitoring
* Threat Intelligence API integration
* SIEM integration
* Multi-language threat detection
* Cloud deployment and scaling

---

👩‍💻 Author

Deeksha P Shetty

Cyber Security | Machine Learning | Threat Intelligence

 📜 License

This project was developed as an academic capstone project for educational and research purposes.
