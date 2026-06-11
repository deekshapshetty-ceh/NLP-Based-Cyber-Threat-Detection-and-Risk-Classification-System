"""
Authentication utilities for CyberWatch.
Users are stored in data/users.json with SHA-256 hashed passwords.
Default admin: username=admin, password=admin123
"""
import json
import hashlib
from pathlib import Path
import streamlit as st

USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"

# ── Helpers ───────────────────────────────────────────────────────────────────
def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _load() -> dict:
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
    return json.loads(USERS_FILE.read_text())

def _save(users: dict) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(users, indent=2))

# ── Public API ────────────────────────────────────────────────────────────────
def login_user(username: str, password: str) -> tuple:
    """Returns (success: bool, message: str)."""
    username = username.strip().lower()
    users = _load()
    if username not in users:
        return False, "User not found."
    if users[username]["password"] != _hash(password):
        return False, "Incorrect password."
    st.session_state.authenticated = True
    st.session_state.username     = username
    st.session_state.user_role    = users[username].get("role", "Analyst")
    st.session_state.user_email   = users[username].get("email", "")
    return True, "Welcome back!"

def register_user(username: str, password: str, email: str, role: str = "Analyst") -> tuple:
    """Returns (success: bool, message: str)."""
    username = username.strip().lower()
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if not email or "@" not in email:
        return False, "Please enter a valid email address."
    users = _load()
    if username in users:
        return False, "Username already taken."
    users[username] = {
        "password": _hash(password),
        "role": role,
        "email": email,
    }
    _save(users)
    return True, "Account created! You can now sign in."

def logout_user() -> None:
    for key in ["authenticated", "username", "user_role", "user_email"]:
        st.session_state.pop(key, None)

def require_auth() -> bool:
    """Returns True if the user is authenticated."""
    return st.session_state.get("authenticated", False)
