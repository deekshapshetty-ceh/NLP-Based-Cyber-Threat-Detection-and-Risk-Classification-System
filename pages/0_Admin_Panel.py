"""
⚙️ Admin Panel — Account settings, password management, and sign out.
"""

import json
import streamlit as st
from datetime import datetime

from config.theme import (
    inject_css, init_session_state, render_footer,
    page_header, sidebar_branding,
)
from utils.auth_gate import show_auth_gate
from utils.auth import logout_user, _hash, _load, _save


st.set_page_config(
    page_title="Admin Panel — CyberWatch",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
show_auth_gate()
init_session_state()

with st.sidebar:
    sidebar_branding()

username  = st.session_state.get("username", "analyst")
user_role = st.session_state.get("user_role", "Analyst")
user_email = st.session_state.get("user_email", "")

page_header(
    "Admin Panel",
    "Manage your account settings, change your password, or sign out.",
    "⚙️",
    label="Account Management",
)

# ── Account Info Card ──────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:rgba(14,22,40,0.7);border:1px solid rgba(0,212,255,0.12);
            border-radius:16px;padding:24px 28px;margin-bottom:24px;
            display:flex;align-items:center;gap:20px">
    <div style="width:64px;height:64px;border-radius:50%;flex-shrink:0;
                background:linear-gradient(135deg,#0090b8,#7c3aed);
                display:flex;align-items:center;justify-content:center;
                font-family:'Syne',sans-serif;font-weight:800;font-size:1.5rem;
                color:#fff;box-shadow:0 0 24px rgba(0,212,255,0.25)">
        {username[:2].upper()}
    </div>
    <div style="flex:1">
        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
                    color:#f0f4fa">{username.capitalize()}</div>
        <div style="color:#64748b;font-size:0.85rem;font-family:'DM Sans',sans-serif;margin-top:2px">
            {user_email or "No email set"} &nbsp;·&nbsp;
            <span style="color:#00d4ff;font-weight:600">{user_role}</span>
        </div>
    </div>
    <div style="background:rgba(0,229,160,0.1);border:1px solid rgba(0,229,160,0.25);
                border-radius:20px;padding:4px 14px;font-size:0.75rem;font-weight:700;
                color:#00e5a0;font-family:'DM Sans',sans-serif;letter-spacing:0.5px">
        ● ACTIVE
    </div>
</div>
""", unsafe_allow_html=True)

# ── Two columns: Change Password | Sign Out ────────────────────────────────────
col_pw, col_signout = st.columns([3, 2], gap="large")

# ── Change Password ────────────────────────────────────────────────────────────
with col_pw:
    st.markdown("""
    <div style="font-size:0.65rem;letter-spacing:2.5px;text-transform:uppercase;
                color:#334155;font-weight:700;margin-bottom:14px;
                font-family:'DM Sans',sans-serif">◈ Change Password</div>
    """, unsafe_allow_html=True)

    with st.form("change_password_form", clear_on_submit=True):
        current_pw = st.text_input(
            "Current Password", type="password",
            placeholder="Enter your current password",
        )
        new_pw = st.text_input(
            "New Password", type="password",
            placeholder="Min. 6 characters",
        )
        confirm_pw = st.text_input(
            "Confirm New Password", type="password",
            placeholder="Repeat new password",
        )

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        save_btn = st.form_submit_button(
            "🔒 Update Password", type="primary", use_container_width=True
        )

        if save_btn:
            if not all([current_pw, new_pw, confirm_pw]):
                st.error("Please fill in all fields.")
            elif len(new_pw) < 6:
                st.error("New password must be at least 6 characters.")
            elif new_pw != confirm_pw:
                st.error("New passwords do not match.")
            else:
                users = _load()
                if users[username]["password"] != _hash(current_pw):
                    st.error("Current password is incorrect.")
                else:
                    users[username]["password"] = _hash(new_pw)
                    _save(users)
                    st.success("✅ Password updated successfully!")

# ── Sign Out ───────────────────────────────────────────────────────────────────
with col_signout:
    st.markdown("""
    <div style="font-size:0.65rem;letter-spacing:2.5px;text-transform:uppercase;
                color:#334155;font-weight:700;margin-bottom:14px;
                font-family:'DM Sans',sans-serif">◈ Session</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:rgba(14,22,40,0.5);border:1px solid rgba(255,255,255,0.05);
                border-radius:14px;padding:20px 22px;margin-bottom:16px">
        <div style="color:#64748b;font-size:0.83rem;font-family:'DM Sans',sans-serif;
                    line-height:1.8">
            Signed in as<br>
            <strong style="color:#f0f4fa">{username.capitalize()}</strong><br>
            Role: <strong style="color:#00d4ff">{user_role}</strong><br>
            Session started: <strong style="color:#94a3b8">{datetime.now().strftime("%b %d, %Y")}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⏻  Sign Out", type="primary", use_container_width=True, key="admin_signout"):
        logout_user()
        st.rerun()

    st.markdown("""
    <div style="color:#334155;font-size:0.75rem;font-family:'DM Sans',sans-serif;
                margin-top:8px;text-align:center">
        You will be redirected to the login screen.
    </div>
    """, unsafe_allow_html=True)

# ── Danger Zone (Admin only) ───────────────────────────────────────────────────
if user_role == "Admin":
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.65rem;letter-spacing:2.5px;text-transform:uppercase;
                color:#f43f5e;font-weight:700;margin-bottom:14px;
                font-family:'DM Sans',sans-serif">◈ Admin — User Management</div>
    """, unsafe_allow_html=True)

    users = _load()
    user_list = [
        {"Username": u, "Role": d.get("role","Analyst"), "Email": d.get("email","")}
        for u, d in users.items()
    ]

    import pandas as pd
    st.dataframe(pd.DataFrame(user_list), hide_index=True, use_container_width=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.65rem;letter-spacing:2.5px;text-transform:uppercase;
                color:#334155;font-weight:700;margin-bottom:10px;
                font-family:'DM Sans',sans-serif">◈ Add New User</div>
    """, unsafe_allow_html=True)

    with st.form("add_user_form", clear_on_submit=True):
        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1: new_uname = st.text_input("Username", placeholder="username")
        with ac2: new_email = st.text_input("Email", placeholder="user@email.com")
        with ac3: new_upass = st.text_input("Password", type="password", placeholder="Min. 6 chars")
        with ac4: new_role  = st.selectbox("Role", ["Analyst", "Researcher", "Viewer", "Admin"])

        add_btn = st.form_submit_button("➕ Add User", type="primary", use_container_width=True)
        if add_btn:
            if not all([new_uname, new_email, new_upass]):
                st.error("Please fill in all fields.")
            elif len(new_upass) < 6:
                st.error("Password must be at least 6 characters.")
            elif new_uname.lower() in users:
                st.error("Username already exists.")
            else:
                users[new_uname.lower()] = {
                    "password": _hash(new_upass),
                    "role": new_role,
                    "email": new_email,
                }
                _save(users)
                st.success(f"✅ User '{new_uname}' added successfully!")
                st.rerun()

render_footer()
