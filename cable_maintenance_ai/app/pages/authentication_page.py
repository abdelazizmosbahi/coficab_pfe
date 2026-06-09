"""Authentication page for login and registration."""

from __future__ import annotations

import base64
import os
import sys

import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_DIR = os.path.dirname(BASE_DIR)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_helpers import (  # noqa: E402
    authenticate_user,
    bootstrap_auth_page,
    register_user,
    sign_in_user,
)


def apply_auth_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600;700&family=Space+Grotesk:wght@500;700&display=swap');
        :root {
            --cof-navy: #0b1b2b;
            --cof-orange: #f57c00;
            --cof-ember: #ff9a3c;
            --cof-ash: #e4e8ec;
            --cof-slate: #5b6b7a;
        }
        html, body, [class*="css"] {
            font-family: 'Manrope', system-ui, -apple-system, 'Segoe UI', sans-serif;
            color: var(--cof-navy);
        }
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at 10% 15%, #ffffff 0%, #f7f9fb 35%, #eef2f6 100%) !important;
        }
        [data-testid="stHeader"] { 
            background: transparent !important;
            z-index: 999 !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
        }
        [data-testid="stToolbar"] { 
            display: none !important;
        }
        [data-testid="stSidebar"] { display: none !important; }
        </style>
        <script>
        (function(){
            var s=document.createElement('style');
            s.textContent='[data-testid="stSidebar"]{display:none!important}';
            document.head.appendChild(s);
            var o=new MutationObserver(function(){
                var e=document.querySelector('[data-testid="stSidebar"]');
                if(e)e.style.display='none';
            });
            o.observe(document.documentElement,{childList:true,subtree:true});
            setTimeout(function(){o.disconnect();},3000);
        })();
        </script>
        <style>
        [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"],
        [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] span,
        [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] li,
        [data-testid="stAppViewContainer"] .stCaption, [data-testid="stAppViewContainer"] label {
            color: var(--cof-navy) !important;
        }
        .auth-shell {
            max-width: 1040px;
            margin: 0 auto;
        }
        .auth-hero {
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 24px;
            align-items: stretch;
            padding: 28px 32px;
            border-radius: 22px;
            background: linear-gradient(120deg, #0c1f31 0%, #133657 55%, #1f4a6f 100%);
            color: #f7fafc;
            box-shadow: 0 16px 40px rgba(7, 18, 30, 0.2);
            margin-bottom: 22px;
        }
        .auth-hero h1 {
            font-family: 'Space Grotesk', 'Manrope', sans-serif;
            font-size: 30px;
            margin: 8px 0 10px 0;
            letter-spacing: 0.3px;
        }
        .auth-hero p {
            margin: 0;
            font-size: 16px;
            color: rgba(247, 250, 252, 0.86);
        }
        .auth-badge {
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 12px;
            color: rgba(247, 250, 252, 0.72);
        }
        .auth-panel {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(228, 232, 236, 0.95);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 10px 28px rgba(12, 31, 49, 0.08);
        }
        .auth-card {
            background: #ffffff;
            border: 1px solid var(--cof-ash);
            border-radius: 18px;
            padding: 24px;
            box-shadow: 0 10px 24px rgba(12, 31, 49, 0.08);
        }
        .auth-kicker {
            font-family: 'Space Grotesk', 'Manrope', sans-serif;
            font-weight: 700;
            color: var(--cof-slate);
            text-transform: uppercase;
            letter-spacing: 1.6px;
            font-size: 12px;
            margin-bottom: 6px;
        }
        .stButton > button {
            background: linear-gradient(135deg, var(--cof-orange), var(--cof-ember));
            color: #1b1b1b;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            padding: 0.6rem 1rem;
            box-shadow: 0 10px 22px rgba(245, 124, 0, 0.3);
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 26px rgba(245, 124, 0, 0.35);
        }
        [data-testid="stTextInput"] input {
            border-radius: 12px;
        }
        [data-testid="stTabs"] {
            gap: 0.5rem;
        }
        [data-baseweb="tab-list"] {
            gap: 0.4rem;
        }
        [data-baseweb="tab"] {
            font-weight: 600;
            color: var(--cof-slate);
            border-radius: 999px;
        }
        [aria-selected="true"] {
            color: var(--cof-navy) !important;
            border-bottom: 3px solid var(--cof-orange) !important;
        }
        .auth-footer {
            margin-top: 18px;
            color: var(--cof-slate);
            font-size: 14px;
        }
        @media (max-width: 900px) {
            .auth-hero { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Authentication",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_auth_theme()

if bootstrap_auth_page():
    st.stop()

logo_path = os.path.join(ROOT_DIR, "cofai_logo_transparent.png")
logo_data_uri = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as logo_file:
        logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
        logo_data_uri = f"data:image/png;base64,{logo_b64}"

shell_logo_html = (
    f'<img src="{logo_data_uri}" alt="Cofai logo" style="height:52px; width:auto; filter: drop-shadow(0 6px 14px rgba(7, 18, 30, 0.35));" />'
    if logo_data_uri
    else ""
)

st.markdown(
    f"""
    <div class="auth-shell">
        <div class="auth-hero">
            <div>
                <div class="auth-badge">SECURE ACCESS</div>
            </div>
            <div style="display:flex; align-items:center; justify-content:flex-end;">{shell_logo_html}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

login_tab, register_tab = st.tabs(["Login", "Register"])

with login_tab:
    st.markdown("<div class='auth-kicker'>Login</div>", unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        login_user_id = st.text_input("User ID", key="login_user_id")
        login_password = st.text_input("Password", type="password", key="login_password")
        login_submitted = st.form_submit_button("Log in", use_container_width=True)

    if login_submitted:
        success, message, role = authenticate_user(login_user_id, login_password)
        if success:
            sign_in_user(login_user_id, role=role)
            target_page = st.session_state.pop("auth_next_page", "app.py") or "app.py"
            if target_page == "pages/authentication_page.py":
                target_page = "app.py"
            st.switch_page(target_page)
        else:
            st.error(message)
    st.markdown("</div>", unsafe_allow_html=True)

with register_tab:
    st.markdown("<div class='auth-kicker'>Register</div>", unsafe_allow_html=True)
    with st.form("register_form", clear_on_submit=False):
        register_user_id = st.text_input("User ID", key="register_user_id")
        register_password = st.text_input("Password", type="password", key="register_password")
        register_submitted = st.form_submit_button("Create account", use_container_width=True)

    if register_submitted:
        success, message = register_user(register_user_id, register_password)
        if success:
            st.success(message)
        else:
            st.error(message)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

