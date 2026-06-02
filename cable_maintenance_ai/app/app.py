"""
Cable Manufacturing AI - Main Entry Point
Multi-page Streamlit application for machine configuration, real-time monitoring, and recipe analysis.
"""

import os
import sys
from datetime import datetime

import streamlit as st

# ========================================
# Python Path Configuration
# ========================================
# Add both app directory and project root to sys.path
# so imports work both locally and in Docker
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from auth_helpers import ensure_page_authentication, render_nav_bar, initialize_users_table, get_current_user_role  # noqa: E402
from db_helpers import initialize_machine_configuration_table  # noqa: E402

COFICAB_LOGO_B64 = "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"


st.set_page_config(
    page_title="Cable Manufacturing AI",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========================================
# Initialize Database Schema (one-time)
# ========================================
# Create model_schema and required tables on app startup
try:
    initialize_users_table()
    initialize_machine_configuration_table()
except Exception as e:
    st.error(f"⚠️ Database initialization warning: {e}")

ensure_page_authentication("app.py")

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        padding-top: 0px;
    }}
    [data-testid="stHeader"] {{ 
        background: rgba(255, 255, 255, 0.98) !important;
        z-index: 999 !important;
        position: sticky !important;
        top: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
    }}
    [data-testid="stToolbar"] {{ 
        display: none !important;
    }}
    [data-testid="stSidebar"] {{ display: none !important; }}

    .cofi-nav__left {{
        background-image: url('data:image/png;base64,{COFICAB_LOGO_B64}');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center left;
        min-width: 140px;
        height: 36px;
    }}

    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    @keyframes float {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
        100% {{ transform: translateY(0px); }}
    }}
    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 5px rgba(0,200,255,0.3); }}
        50% {{ box-shadow: 0 0 25px rgba(0,200,255,0.6); }}
        100% {{ box-shadow: 0 0 5px rgba(0,200,255,0.3); }}
    }}
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    @keyframes drift {{
        0% {{ transform: translate(0, 0); opacity: 0; }}
        10% {{ opacity: 0.6; }}
        90% {{ opacity: 0.6; }}
        100% {{ transform: translate(100px, -100vh); opacity: 0; }}
    }}
    </style>
    <script>
    (function(){{
        var s=document.createElement('style');
        s.textContent='[data-testid="stSidebar"]{{display:none!important}}';
        document.head.appendChild(s);
        var o=new MutationObserver(function(){{
            var e=document.querySelector('[data-testid="stSidebar"]');
            if(e)e.style.display='none';
        }});
        o.observe(document.documentElement,{{childList:true,subtree:true}});
        setTimeout(function(){{o.disconnect();}},3000);
    }})();
    </script>
    """,
    unsafe_allow_html=True,
)

render_nav_bar(current_page="app.py")

# ────────────────────────────────────────────────────────────────────────────
# HOME PAGE
# ────────────────────────────────────────────────────────────────────────────

def display_home():
    role = get_current_user_role().capitalize() or "Operator"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #080c18 0%, #0d1a2e 30%, #121e36 60%, #080c18 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
        }}
        .logo-bg {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; z-index: 0; overflow: hidden;
        }}
        .logo-float {{
            position: absolute;
            background-image: url('data:image/png;base64,{COFICAB_LOGO_B64}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            opacity: 0.06;
            animation: drift linear infinite;
        }}
        .lf1 {{ width: 110px; height: 110px; left: -20px; top: 10%; animation-duration: 22s; }}
        .lf2 {{ width: 85px; height: 85px; right: -15px; top: 35%; animation-duration: 28s; animation-delay: 5s; }}
        .lf3 {{ width: 70px; height: 70px; left: 20%; top: 70%; animation-duration: 18s; animation-delay: 8s; }}
        .lf4 {{ width: 95px; height: 95px; right: 25%; top: 8%; animation-duration: 25s; animation-delay: 3s; }}
        .lf5 {{ width: 65px; height: 65px; left: 55%; top: 82%; animation-duration: 30s; animation-delay: 11s; }}
        .lf6 {{ width: 80px; height: 80px; right: 10%; top: 60%; animation-duration: 20s; animation-delay: 6s; }}

        .hero-section {{
            display: flex; flex-direction: column; align-items: center;
            padding: 50px 20px 20px; position: relative; z-index: 1;
            animation: fadeInUp 0.8s ease-out;
        }}
        # .hero-logo {{
        #     width: 400px; height: 200px; margin-bottom: 20px; border-radius: 20px;
        #     animation: heroFloat 4s ease-in-out infinite;
        #     filter: drop-shadow(0 0 30px rgba(0,200,255,0.2));
        # }}
        .hero-title {{
            font-size: 2.8rem; font-weight: 800; margin-bottom: 8px;
            background: linear-gradient(135deg, #00d4ff, #0088ff, #a855f7, #00d4ff);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientShift 4s ease infinite;
            letter-spacing: -0.5px;
        }}
        .hero-subtitle {{
            font-size: 1.05rem; color: rgba(255,255,255,0.55);
            max-width: 650px; margin: 0 auto 6px;
            animation: fadeIn 1.2s ease-out;
            letter-spacing: 0.3px;
        }}
        .hero-badge {{
            display: inline-block; margin-top: 4px;
            padding: 4px 16px; border-radius: 999px;
            background: linear-gradient(135deg, rgba(0,200,255,0.1), rgba(168,85,247,0.1));
            border: 1px solid rgba(0,200,255,0.15);
            color: rgba(255,255,255,0.65); font-size: 0.8rem;
            backdrop-filter: blur(4px);
            animation: fadeIn 1.6s ease-out;
        }}

        .workflow-section {{
            position: relative; z-index: 1;
            margin: 10px auto 25px; max-width: 1000px;
            animation: fadeInUp 1s ease-out;
        }}
        .workflow-title {{
            text-align: center; font-size: 1.3rem; font-weight: 700;
            color: rgba(255,255,255,0.5); margin-bottom: 24px;
            letter-spacing: 2px; text-transform: uppercase;
        }}
        .workflow-steps {{
            display: flex; justify-content: center; align-items: flex-start;
            gap: 12px; flex-wrap: wrap;
        }}
        .workflow-step {{
            flex: 1; min-width: 220px; max-width: 300px;
            border-radius: 18px; text-align: left;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            backdrop-filter: blur(12px);
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeInUp 1.2s ease-out both;
            position: relative; overflow: hidden;
            cursor: pointer;
        }}
        .workflow-step:nth-child(1) {{ animation-delay: 0.15s; }}
        .workflow-step:nth-child(2) {{ animation-delay: 0.3s; }}
        .workflow-step:nth-child(3) {{ animation-delay: 0.45s; }}
        .workflow-step:hover {{
            border-color: rgba(0,200,255,0.3);
            box-shadow: 0 8px 30px rgba(0,200,255,0.1);
            background: rgba(255,255,255,0.06);
        }}
        .step-toggle {{ display: none; }}
        .step-summary {{
            padding: 22px 18px 18px; text-align: center; display: block;
        }}
        .step-details {{
            max-height: 0; overflow: hidden;
            transition: max-height 0.4s ease, padding 0.4s ease;
            padding: 0 18px;
        }}
        .step-toggle:checked ~ .step-details {{
            max-height: 300px; padding: 0 18px 16px;
        }}
        .step-toggle:checked ~ .step-summary .step-chevron {{
            transform: rotate(180deg);
        }}
        .step-number {{
            position: absolute; top: -10px; right: -10px;
            width: 28px; height: 28px; border-radius: 50%;
            background: linear-gradient(135deg, #00d4ff, #a855f7);
            color: #fff; font-size: 0.75rem; font-weight: 700;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 0 15px rgba(0,212,255,0.3);
        }}
        .step-icon {{ font-size: 2rem; margin-bottom: 6px; display: block; }}
        .step-title {{ font-size: 1rem; font-weight: 700; color: #ffffff; margin-bottom: 4px; text-align: center; }}
        .step-desc {{ font-size: 0.78rem; color: rgba(255,255,255,0.45); line-height: 1.4; text-align: center; }}
        .step-chevron {{
            display: inline-block; margin-left: 6px; font-size: 0.7rem;
            transition: transform 0.3s ease; color: rgba(255,255,255,0.3);
        }}
        .detail-item {{
            font-size: 0.78rem; color: rgba(255,255,255,0.5);
            padding: 5px 0; line-height: 1.4;
            border-bottom: 1px solid rgba(255,255,255,0.04);
        }}
        .detail-item:last-child {{ border-bottom: none; }}
        .detail-icon {{ margin-right: 8px; opacity: 0.5; }}
        .step-arrow {{
            display: flex; align-items: center; font-size: 1.4rem;
            color: rgba(0,200,255,0.2); min-width: 16px; padding-top: 30px;
            animation: fadeIn 1.5s ease-out 0.6s both;
        }}

        .footer-section {{
            text-align: center; padding: 20px 0 10px;
            position: relative; z-index: 1;
            animation: fadeIn 2s ease-out;
        }}
        .footer-text {{
            color: rgba(255,255,255,0.25); font-size: 0.75rem;
            letter-spacing: 0.3px;
        }}
        .footer-divider {{
            border: none; height: 1px;
            background: linear-gradient(90deg, transparent, rgba(0,200,255,0.1), transparent);
            margin-bottom: 12px;
        }}

        @keyframes heroFloat {{
            0% {{ transform: translateY(0px); filter: drop-shadow(0 0 20px rgba(0,200,255,0.2)); }}
            50% {{ transform: translateY(-12px); filter: drop-shadow(0 0 50px rgba(0,200,255,0.4)); }}
            100% {{ transform: translateY(0px); filter: drop-shadow(0 0 20px rgba(0,200,255,0.2)); }}
        }}
        </style>

        <div class="logo-bg">
            <div class="logo-float lf1"></div>
            <div class="logo-float lf2"></div>
            <div class="logo-float lf3"></div>
            <div class="logo-float lf4"></div>
            <div class="logo-float lf5"></div>
            <div class="logo-float lf6"></div>
        </div>

        <div class="hero-section">
            <div class="hero-title">Cable Manufacturing AI</div>
            <div class="hero-subtitle">Configuration-based production monitoring &middot; Live OPC traceability &middot; Analysis-based production datasheet</div>
            <div class="hero-badge">🔒 {role} · {datetime.now().strftime('%B %Y')}</div>
        </div>

        <div class="workflow-section">
            <div class="workflow-title">How it works</div>
            <div class="workflow-steps">
                <label class="workflow-step">
                    <input type="checkbox" class="step-toggle">
                    <div class="step-summary">
                        <div class="step-number">1</div>
                        <span class="step-icon">⚙️</span>
                        <div class="step-title">Configure <span class="step-chevron">▼</span></div>
                        <div class="step-desc">Define machines, OPC parameters &amp; recipe subsets</div>
                    </div>
                    <div class="step-details">
                        <div class="detail-item"><span class="detail-icon">▸</span>Create machine monitoring configs with full CRUD</div>
                        <div class="detail-item"><span class="detail-icon">▸</span>Select OPC parameters to track per machine</div>
                        <div class="detail-item"><span class="detail-icon">▸</span>Designate recipe parameter subsets</div>
                        <div class="detail-item"><span class="detail-icon">▸</span>Manage realtime &amp; analysis config types</div>
                    </div>
                </label>
                <div class="step-arrow">→</div>
                <label class="workflow-step">
                    <input type="checkbox" class="step-toggle">
                    <div class="step-summary">
                        <div class="step-number">2</div>
                        <span class="step-icon">📈</span>
                        <div class="step-title">Analyze <span class="step-chevron">▼</span></div>
                        <div class="step-desc">Generate datasheets from production run samples</div>
                    </div>
                    <div class="step-details">
                        <div class="detail-item"><span class="detail-icon">▸</span>Load analysis configs &amp; browse production runs</div>
                        <div class="detail-item"><span class="detail-icon">▸</span>Filter runs by quality labels (OK / NOTOK)</div>
                        <div class="detail-item"><span class="detail-icon">▸</span>Collect labeled samples &amp; compute statistics</div>
                        <div class="detail-item"><span class="detail-icon">▸</span>Save &amp; compare datasheets across runs</div>
                    </div>
                </label>
                <div class="step-arrow">→</div>
                <label class="workflow-step">
                    <input type="checkbox" class="step-toggle">
                    <div class="step-summary">
                        <div class="step-number">3</div>
                        <span class="step-icon">📊</span>
                        <div class="step-title">Monitor <span class="step-chevron">▼</span></div>
                        <div class="step-desc">Track live values against reference specs in real-time</div>
                    </div>
                    <div class="step-details">
                        <div class="detail-item"><span class="detail-icon">▸</span>Select realtime config &amp; run analysis notebook</div>
                        <div class="detail-item"><span class="detail-icon">▸</span>Monitor live OPC values with 1s auto-refresh</div>
                        <div class="detail-item"><span class="detail-icon">▸</span>View traceability charts (3s &amp; full timeline)</div>
                        <div class="detail-item"><span class="detail-icon">▸</span>Identify spec violations &amp; trigger Mistral RCA</div>
                    </div>
                </label>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="footer-section">
            <hr class="footer-divider">
            <div class="footer-text">
                Cable Manufacturing AI &middot; Streamlit &middot; Mistral AI
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



# ────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    display_home()
