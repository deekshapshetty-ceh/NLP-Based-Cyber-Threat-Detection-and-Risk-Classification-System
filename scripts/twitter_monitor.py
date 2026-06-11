"""
twitter_monitor.py
──────────────────
Real-time Twitter/X monitoring for cyber threats.
Run this alongside app.py to feed live tweets into your dashboard.

SETUP:
1. Get Twitter Developer API keys from https://developer.twitter.com
2. Fill in your keys below
3. Run: python twitter_monitor.py
"""

import tweepy
import pickle
import json
import time
from datetime import datetime

# ── YOUR TWITTER API KEYS (fill these in) ──────────────────────────────────
API_KEY             = "YOUR_API_KEY_HERE"
API_SECRET          = "YOUR_API_SECRET_HERE"
ACCESS_TOKEN        = "YOUR_ACCESS_TOKEN_HERE"
ACCESS_TOKEN_SECRET = "YOUR_ACCESS_TOKEN_SECRET_HERE"
BEARER_TOKEN        = "YOUR_BEARER_TOKEN_HERE"
# ───────────────────────────────────────────────────────────────────────────

# Load your trained model
model      = pickle.load(open('attack_model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

RISK_MAP = {
    'ransomware':    'HIGH',
    'leak':          'HIGH',
    '0day':          'HIGH',
    'ddos':          'MEDIUM',
    'botnet':        'MEDIUM',
    'vulnerability': 'LOW',
    'general':       'LOW',
    'all':           'LOW',
}

# Keywords to monitor on Twitter
MONITOR_KEYWORDS = [
    "ransomware attack",
    "data breach",
    "DDoS attack",
    "zero day vulnerability",
    "cyber attack",
    "malware detected",
    "data leak",
    "botnet",
]

def classify(text):
    vec  = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    conf = round(float(max(model.predict_proba(vec)[0])) * 100, 1)
    return pred, RISK_MAP.get(pred, 'LOW'), conf


class ThreatStreamListener(tweepy.StreamingClient):
    """Listens to live tweets and classifies them in real time."""

    def on_tweet(self, tweet):
        text = tweet.text

        # Skip retweets
        if text.startswith('RT '):
            return

        threat_type, risk, confidence = classify(text)

        # Print to console
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{timestamp}] 🔍 NEW TWEET")
        print(f"  Text      : {text[:100]}...")
        print(f"  Threat    : {threat_type.upper()}")
        print(f"  Risk      : {risk}")
        print(f"  Confidence: {confidence}%")

        # If HIGH risk, print alert
        if risk == 'HIGH':
            print(f"\n  ⚠️  HIGH RISK ALERT DETECTED!")
            print(f"  Threat Type: {threat_type}")
            # You can extend this to send email/Telegram alerts here

        # Save to a log file (the dashboard can read this)
        log_entry = {
            'timestamp': timestamp,
            'text': text[:200],
            'threat_type': threat_type,
            'risk': risk,
            'confidence': confidence,
        }
        with open('live_threats.json', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def on_error(self, status_code):
        print(f"Error: {status_code}")
        if status_code == 429:
            print("Rate limited — waiting 60 seconds...")
            time.sleep(60)


def start_monitoring():
    print("🛡️  CyberWatch Twitter Monitor Starting...")
    print(f"   Monitoring keywords: {', '.join(MONITOR_KEYWORDS)}")
    print("   Press Ctrl+C to stop\n")

    stream = ThreatStreamListener(BEARER_TOKEN)

    # Add rules (keywords to track)
    # First delete existing rules
    existing = stream.get_rules()
    if existing.data:
        ids = [rule.id for rule in existing.data]
        stream.delete_rules(ids)

    # Add new rules
    for keyword in MONITOR_KEYWORDS:
        stream.add_rules(tweepy.StreamRule(keyword))
        print(f"   ✓ Tracking: {keyword}")

    print("\n   Live feed started!\n")

    # Start streaming
    stream.filter(tweet_fields=['created_at', 'author_id'])


if __name__ == '__main__':
    if API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  Please fill in your Twitter API keys in twitter_monitor.py")
        print("   Get them from: https://developer.twitter.com/en/portal/dashboard")
    else:
        start_monitoring()
