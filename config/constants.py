"""
CyberWatch — Shared Constants
==============================
Single source of truth for risk mappings, colors, icons, and descriptions.
"""

# ── Risk Level Mapping ──────────────────────────────────────────────────────
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

# ── Color Coding — updated to match v2 design system ───────────────────────
RISK_COLOR = {
    "HIGH":   "#f43f5e",
    "MEDIUM": "#f59e0b",
    "LOW":    "#00e5a0",
}

# ── Threat Category Icons ───────────────────────────────────────────────────
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

# ── Threat Descriptions ─────────────────────────────────────────────────────
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
