"""Shared auth gate — call show_auth_gate() at the top of every page."""
import streamlit as st
from utils.auth import login_user, register_user

_AUTH_CSS = """
<style>
/* Fullscreen auth overlay */
.auth-page { max-width: 460px; margin: 0 auto; padding: 40px 0 60px; }
.auth-logo-wrap {
    text-align: center;
    margin-bottom: 32px;
}
.auth-logo-icon {
    width: 64px; height: 64px;
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(124,58,237,0.15));
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 18px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem;
    margin: 0 auto 14px;
    box-shadow: 0 0 32px rgba(0,212,255,0.12);
}
.auth-brand {
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
    margin-bottom: 4px;
}
.auth-tagline {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    color: #3f5268;
    letter-spacing: 2.5px;
    text-transform: uppercase;
}
.auth-card {
    background: linear-gradient(145deg, #080f1c, #0b1524);
    border: 1px solid rgba(0,212,255,0.1);
    border-radius: 20px;
    padding: 36px 36px 32px;
    box-shadow: 0 8px 48px rgba(0,0,0,0.5);
}
.auth-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #eef2fa;
    margin-bottom: 6px;
}
.auth-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.87rem;
    color: #3f5268;
    margin-bottom: 28px;
}
/* Hide Streamlit top bar AND sidebar on login page */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stSidebar"],
header { display: none !important; }
</style>
"""

_SHOW_SIDEBAR_CSS = """
<style>
/* Force sidebar visible after login */
[data-testid="stSidebar"] { display: flex !important; }
</style>
"""

def show_auth_gate():
    """Display login/register UI. Calls st.stop() if not authenticated."""
    if st.session_state.get("authenticated"):
        # Already logged in — force sidebar back on
        st.markdown(_SHOW_SIDEBAR_CSS, unsafe_allow_html=True)
        return

    # Not logged in — hide sidebar
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)

    # Centre column
    _, col, _ = st.columns([1, 2, 1])
    with col:
        # Logo
        st.markdown("""
        <div class="auth-logo-wrap">
            <div class="auth-logo-icon">🛡️</div>
            <div class="auth-brand">CyberWatch</div>
            <div class="auth-tagline">Threat Intelligence Platform</div>
        </div>
        """, unsafe_allow_html=True)

        # Tabs
        tab_login, tab_reg = st.tabs(["Sign In", "Create Account"])

        # ── Login ──────────────────────────────────────────────────────────
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
                st.markdown('<div class="auth-subtitle">Sign in to your account to continue.</div>', unsafe_allow_html=True)

                username = st.text_input("Username", placeholder="Enter your username", key="li_user")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="li_pass")

                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

                if submitted:
                    if not username or not password:
                        st.error("Please fill in all fields.")
                    else:
                        ok, msg = login_user(username, password)
                        if ok:
                            st.rerun()
                        else:
                            st.error(msg)

            st.markdown("""
            <div style="text-align:center;margin-top:16px;font-family:'DM Sans',sans-serif;
                        font-size:0.8rem;color:#3f5268">
                Default admin: <code style="color:#00d4ff">admin</code> /
                <code style="color:#00d4ff">admin123</code>
            </div>
            """, unsafe_allow_html=True)

        # ── Register ───────────────────────────────────────────────────────
        with tab_reg:
            with st.form("reg_form", clear_on_submit=True):
                st.markdown('<div class="auth-title">Create an account</div>', unsafe_allow_html=True)
                st.markdown('<div class="auth-subtitle">Join the CyberWatch platform.</div>', unsafe_allow_html=True)

                r_user  = st.text_input("Username", placeholder="Choose a username", key="r_user")
                r_email = st.text_input("Email", placeholder="your@email.com", key="r_email")
                r_pass  = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="r_pass")
                r_pass2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="r_pass2")
                r_role  = st.selectbox("Role", ["Analyst", "Researcher", "Viewer"], key="r_role")

                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                reg_btn = st.form_submit_button("Create Account →", use_container_width=True, type="primary")

                if reg_btn:
                    if not all([r_user, r_email, r_pass, r_pass2]):
                        st.error("Please fill in all fields.")
                    elif r_pass != r_pass2:
                        st.error("Passwords do not match.")
                    else:
                        ok, msg = register_user(r_user, r_pass, r_email, r_role)
                        if ok:
                            st.success(msg + " Switch to Sign In.")
                        else:
                            st.error(msg)

    st.stop()