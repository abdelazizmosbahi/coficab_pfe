"""Admin page for Analyst user management — approve/decline operators."""

from __future__ import annotations

import os
import sys
import base64

import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)
BASE_DIR = os.path.dirname(APP_DIR)
ROOT_DIR = os.path.dirname(BASE_DIR)
from auth_helpers import (  # noqa: E402
    PAGE_REGISTRY,
    ensure_page_authentication,
    get_pending_operators,
    get_all_users,
    approve_operator,
    decline_operator,
    get_user_page_permissions,
    set_user_page_permissions,
    set_user_active_status,
    delete_user,
    is_current_user_analyst,
    render_nav_bar,
)


def apply_coficab_theme():
    """Coficab styling (matches model_page / opcua_realtime_page)."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600;700&family=Space+Grotesk:wght@500;700&display=swap');
        :root {
            --cof-navy: #0b1b2b; --cof-orange: #f57c00; --cof-ember: #ff9a3c;
            --cof-ash: #e4e8ec; --cof-slate: #5b6b7a;
        }
        html, body, [class*="css"] {
            font-family: 'Manrope', system-ui, -apple-system, 'Segoe UI', sans-serif;
            color: var(--cof-navy);
        }
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at 10% 15%, #ffffff 0%, #f7f9fb 35%, #eef2f6 100%);
            padding-top: 56px;
        }
        [data-testid="stHeader"] { background: transparent; }
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
        .stAlert [data-testid="stMarkdownContainer"], .stAlert p, .stAlert span { color: var(--cof-navy) !important; }
        .cofi-hero {
            display: grid; grid-template-columns: 1fr auto; gap: 24px; align-items: center;
            padding: 28px 32px; border-radius: 20px;
            background: linear-gradient(120deg, #0c1f31 0%, #133657 55%, #1f4a6f 100%);
            color: #f7fafc; box-shadow: 0 16px 40px rgba(7, 18, 30, 0.2); margin-bottom: 20px;
        }
        .cofi-hero__text h1 {
            font-family: 'Space Grotesk', 'Manrope', sans-serif; font-size: 30px;
            letter-spacing: 0.5px; margin: 6px 0 10px 0;
        }
        .cofi-hero__text p { margin: 0; font-size: 16px; color: rgba(247, 250, 252, 0.85); }
        .cofi-eyebrow {
            text-transform: uppercase; letter-spacing: 2px; font-size: 12px;
            color: rgba(247, 250, 252, 0.7);
        }
        .cofi-hero__logo { width: 160px; height: auto; filter: drop-shadow(0 6px 14px rgba(7, 18, 30, 0.35)); }
        .cofi-nav {
            display: flex; align-items: center; justify-content: space-between; gap: 24px;
            padding: 10px 24px; margin: 0;
            background: linear-gradient(120deg, #0c1f31 0%, #133657 55%, #1f4a6f 100%);
            box-shadow: 0 14px 32px rgba(7, 18, 30, 0.2);
            position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
        }
        .cofi-nav__left { display: flex; align-items: center; gap: 14px; }
        .cofi-nav__logo { height: 36px; width: auto; }
        .cofi-nav__links { display: flex; justify-content: center; gap: 18px; flex-wrap: wrap; flex: 1; }
        .cofi-nav__actions { display: flex; align-items: center; justify-content: flex-end; min-width: 120px; }
        .cofi-nav__link {
            color: #ffffff; text-decoration: none; font-weight: 600; font-size: 16px; letter-spacing: 0.6px;
        }
        .cofi-nav__link:visited { color: #ffffff; }
        .cofi-nav__link:hover { color: #ffddbf; }
        .cofi-nav__logout {
            display: inline-flex; align-items: center; justify-content: center;
            padding: 8px 14px; border-radius: 999px; border: 1px solid rgba(255, 221, 191, 0.35);
            background: rgba(255, 255, 255, 0.08); color: #ffffff; text-decoration: none;
            font-weight: 700; font-size: 14px;
        }
        .cofi-nav__logout:hover { background: rgba(255, 221, 191, 0.16); color: #ffffff; }
        [data-testid="stMetric"] {
            background: #ffffff; border: 1px solid var(--cof-ash); border-radius: 14px;
            padding: 14px 16px; box-shadow: 0 6px 18px rgba(12, 31, 49, 0.08);
        }
        [data-testid="stMetricLabel"] { font-weight: 600; color: var(--cof-slate); }
        [data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', 'Manrope', sans-serif; color: var(--cof-navy);
        }
        .stButton > button {
            background: linear-gradient(135deg, var(--cof-orange), var(--cof-ember));
            color: #1b1b1b; border: none; border-radius: 12px; font-weight: 700;
            padding: 0.6rem 1rem; box-shadow: 0 10px 22px rgba(245, 124, 0, 0.3);
        }
        .stButton > button:hover {
            transform: translateY(-1px); box-shadow: 0 14px 26px rgba(245, 124, 0, 0.35);
        }
        .stTabs [data-baseweb="tab"] { font-weight: 600; color: var(--cof-slate); }
        .stTabs [aria-selected="true"] {
            color: var(--cof-navy) !important; border-bottom: 3px solid var(--cof-orange) !important;
        }
        [data-testid="stExpander"] summary {
            color: var(--cof-navy) !important; background: #ffffff;
            border: 1px solid var(--cof-ash); border-radius: 12px; padding: 0.5rem 0.8rem;
        }
        [data-testid="stExpander"] summary:hover, [data-testid="stExpander"] summary:focus {
            color: var(--cof-navy) !important; background: #f3f6f9;
        }
        .stAlert { border-radius: 12px; }
        .stDataFrame, [data-testid="stDataFrame"] {
            background: #ffffff; border-radius: 14px; border: 1px solid var(--cof-ash);
            box-shadow: 0 10px 24px rgba(12, 31, 49, 0.08);
        }
        .cofi-section-title {
            font-family: 'Space Grotesk', 'Manrope', sans-serif; font-weight: 700;
            color: var(--cof-navy); margin-top: 8px; margin-bottom: 8px;
        }
        @media (max-width: 900px) { .cofi-hero { grid-template-columns: 1fr; } }
        [data-testid="stAppViewContainer"] .cofi-hero .cofi-hero__text h1,
        [data-testid="stAppViewContainer"] .cofi-hero .cofi-hero__text p,
        [data-testid="stAppViewContainer"] .cofi-hero .cofi-hero__text p * {
            color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Admin — User Management",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ensure_page_authentication("pages/admin_page.py")

if not is_current_user_analyst():
    st.error("Access denied. Only Analysts can view this page.")
    st.stop()

apply_coficab_theme()

render_nav_bar(current_page="admin_page")

logo_data_uri = ""
logo_path = os.path.join(ROOT_DIR, "coficab_logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as logo_file:
        logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
        logo_data_uri = f"data:image/png;base64,{logo_b64}"

hero_inner = """
    <div class="cofi-hero__text">
        <div class="cofi-eyebrow">ADMIN PANEL</div>
        <h1>User Management</h1>
    </div>
"""
if logo_data_uri:
    hero_html = f'<div class="cofi-hero">{hero_inner}<img class="cofi-hero__logo" src="{logo_data_uri}" alt="Coficab logo" /></div>'
else:
    hero_html = f'<div class="cofi-hero">{hero_inner}</div>'
st.markdown(hero_html, unsafe_allow_html=True)

# ── Section 1: Pending Approvals ─────────────────────────────────────────────
st.markdown('<p class="cofi-section-title">⏳ Pending Approvals</p>', unsafe_allow_html=True)

if st.session_state.pop("user_approved_toast", False):
    st.toast("User approved successfully!", icon="✅")
if st.session_state.pop("user_declined_toast", False):
    st.toast("User declined!", icon="⚠️")

pending = get_pending_operators()

if not pending:
    st.info("No pending operator registrations.")
else:
    st.success(f"{len(pending)} operator(s) awaiting approval.")

    for op in pending:
        uid = op["user_id"]
        created = op["created_at"]
        created_str = created.strftime("%Y-%m-%d %H:%M") if hasattr(created, "strftime") else str(created)

        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.write(f"**{uid}**")
        with col2:
            st.caption(f"Registered: {created_str}")
        with col3:
            if st.button("✅ Approve", key=f"approve_{uid}"):
                ok, msg = approve_operator(uid)
                if ok:
                    st.session_state["user_approved_toast"] = True
                    st.rerun()
                else:
                    st.error(msg)
        with col4:
            if st.button("❌ Decline", key=f"decline_{uid}"):
                ok, msg = decline_operator(uid)
                if ok:
                    st.session_state["user_declined_toast"] = True
                    st.rerun()
                else:
                    st.error(msg)
        st.divider()

# ── Section 2: All Users ─────────────────────────────────────────────────────
st.markdown('<p class="cofi-section-title">📋 All Users</p>', unsafe_allow_html=True)

all_users = get_all_users()
if all_users:
    user_rows = []
    for u in all_users:
        perms = get_user_page_permissions(u["user_id"])
        if u["role"] == "analyst":
            page_access = "All pages (analyst)"
        elif perms is None:
            page_access = "Default (Realtime only)"
        else:
            page_access = ", ".join(PAGE_REGISTRY.get(p, p) for p in perms) if perms else "Default (Realtime only)"

        user_rows.append({
            "User ID": u["user_id"],
            "Role": u["role"],
            "Status": u["approval_status"],
            "Active": "Yes" if u["is_active"] else "No",
            "Page Access": page_access,
            "Created": u["created_at"].strftime("%Y-%m-%d %H:%M") if hasattr(u["created_at"], "strftime") else u["created_at"],
            "Last Login": u["last_login_at"].strftime("%Y-%m-%d %H:%M") if u["last_login_at"] and hasattr(u["last_login_at"], "strftime") else "Never",
        })

    st.dataframe(
        user_rows,
        use_container_width=True,
        hide_index=True,
        column_order=["User ID", "Role", "Status", "Active", "Page Access", "Created", "Last Login"],
    )

    st.divider()
    st.markdown('<p class="cofi-section-title">🔐 Manage Page Access</p>', unsafe_allow_html=True)
    st.caption("Configure which pages each operator can access. Realtime is always accessible by default.")

    if st.session_state.pop("perm_saved_toast", False):
        st.toast("Permissions saved successfully!", icon="✅")
    if st.session_state.pop("user_activated_toast", False):
        st.toast("User activated successfully!", icon="✅")
    if st.session_state.pop("user_disabled_toast", False):
        st.toast("User disabled!", icon="⚠️")
    if st.session_state.pop("user_deleted_toast", False):
        st.toast("User deleted successfully!", icon="🗑️")

    for u in all_users:
        if u["role"] != "operator":
            continue
        uid = u["user_id"]
        current_perms = get_user_page_permissions(uid)

        with st.expander(f"✏️ {uid}", expanded=False):
            st.write(f"**User:** {uid}  ·  **Status:** {u['approval_status']}  ·  **Active:** {'Yes' if u['is_active'] else 'No'}")

            is_full_access = current_perms is None
            grant_all = st.checkbox(
                "✅ Grant Full Access (Configuration + Analysis + Realtime)",
                value=is_full_access,
                key=f"full_access_{uid}",
            )

            st.markdown("**Individual page permissions:**")
            page_checks = {}
            for page_id, label in PAGE_REGISTRY.items():
                checked = grant_all or (current_perms is not None and page_id in current_perms)
                page_checks[page_id] = st.checkbox(
                    label,
                    value=checked,
                    disabled=grant_all,
                    key=f"perm_{uid}_{page_id}",
                )

            col_save, _, col_action1, col_action2 = st.columns([1, 1, 1, 1])
            with col_save:
                if st.button("💾 Save Permissions", key=f"save_perms_{uid}"):
                    if grant_all:
                        ok, msg = set_user_page_permissions(uid, None)
                    else:
                        selected = [p for p, checked in page_checks.items() if checked]
                        ok, msg = set_user_page_permissions(uid, selected)
                    if ok:
                        st.session_state["perm_saved_toast"] = True
                        st.rerun()
                    else:
                        st.error(msg)
            with col_action1:
                active_label = "🚫 Disable" if u["is_active"] else "✅ Activate"
                if st.button(active_label, key=f"toggle_active_{uid}", use_container_width=True):
                    ok, msg = set_user_active_status(uid, not u["is_active"])
                    if ok:
                        key = "user_activated_toast" if not u["is_active"] else "user_disabled_toast"
                        st.session_state[key] = True
                        st.rerun()
                    else:
                        st.error(msg)
            with col_action2:
                if st.button("🗑️ Delete", key=f"delete_user_{uid}", use_container_width=True):
                    ok, msg = delete_user(uid)
                    if ok:
                        st.session_state["user_deleted_toast"] = True
                        st.rerun()
                    else:
                        st.error(msg)
else:
    st.info("No users found.")
