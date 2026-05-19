"""
Cable Manufacturing AI - Main Entry Point
Multi-page Streamlit application for ML-based data mining, prediction, and real-time monitoring.
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

from auth_helpers import ensure_page_authentication, render_nav_bar, initialize_users_table  # noqa: E402
from db_helpers import initialize_machine_configuration_table  # noqa: E402


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
    """
    <style>
    [data-testid="stAppViewContainer"] {
        padding-top: 0px;
    }
    [data-testid="stHeader"] { 
        background: rgba(255, 255, 255, 0.98) !important;
        z-index: 999 !important;
        position: sticky !important;
        top: 0 !important;
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
    """,
    unsafe_allow_html=True,
)

render_nav_bar(current_page="app.py")

# ────────────────────────────────────────────────────────────────────────────
# HOME PAGE
# ────────────────────────────────────────────────────────────────────────────

def display_home():
    """Display home page."""

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title("🏭 Cable Manufacturing AI")
        st.markdown("## Machine Learning-Powered Production Monitoring & Quality Prediction")
        
        st.markdown("""
        Welcome to the advanced cable manufacturing quality monitoring system.
        This application provides real-time machine monitoring, historical data analysis,
        and machine learning-based quality predictions powered by MySQL.
        """)
    
    with col2:
        st.metric("Build Date", datetime.now().strftime("%B %d, %Y"))
        st.metric("Data Source", "MySQL OpcDb")
    
    st.divider()
    
    # Quick start guide
    st.markdown("## 🚀 Quick Start Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📋 Step 1: Configuration
        Go to **Machine Configuration & Recipe Setup**
        - Select machines to monitor
        - Choose parameters and recipes
        - Save your configuration
        
        **→ Next Step: Live Monitoring**
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Step 2: Monitor & Predict
        Go to **Live Monitoring & Quality Prediction**
        - View real-time parameter values
        - Train quality prediction models
        - Monitor production trends
        - Get instant quality predictions
        """)
    
    st.divider()
    
    # Feature overview
    st.markdown("## ✨ Key Features")
    
    features = {
        "🏭 Multi-Machine Support": "Configure and monitor multiple production machines",
        "📊 Real-Time Monitoring": "Live parameter tracking with automated data refresh",
        "🤖 ML Quality Prediction": "Trained models predict OK/NOTOK quality (Random Forest/XGBoost)",
        "📈 Data Mining": "Automatic min/optimal/max range calculation from historical OK runs",
        "🔍 Parameter Traceability": "Complete audit trail of all parameter values and predictions",
        "💾 Configuration Persistence": "Save/load machine configurations for consistent workflow",
        "📉 Trend Analysis": "Historical trend visualization and statistical analysis",
        "🎯 Feature Importance": "Understand which parameters influence quality predictions",
    }
    
    cols = st.columns(2)
    for i, (feature, description) in enumerate(features.items()):
        with cols[i % 2]:
            st.markdown(f"**{feature}**")
            st.caption(description)
    
    st.divider()
    
    # Architecture overview
    st.markdown("## 🏗️ System Architecture")
    
    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────────────┐
    │              Streamlit Multi-Page Application               │
    ├──────────────────────────────────┬──────────────────────────┤
    │   Configuration & Machine Setup  │  Live Monitoring & ML    │
    │  • Machine selection             │  • Real-time metrics     │
    │  • Parameter management          │  • Quality predictions   │
    │  • Recipe configuration          │  • Model training        │
    │  • Session persistence           │  • Trend visualization   │
    │  • Configuration export/import   │  • Traceability table    │
    └──────────────────────────────────┴──────────────────────────┘
                              ↓
    ┌─────────────────────────────────────────────────────────────┐
    │           Shared Database Helpers & ML Utils                │
    │  • streamlit_db_helpers.py (queries & caching)              │
    │  • ml_utils.py (training & prediction)                      │
    └─────────────────────────────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────────────────────────────┐
    │             MySQL Database (OpcDb Schema)                   │
    │  • Machines (OpcNodeId → Parameters)                        │
    │  • MachineTagValue (real-time & historical)                │
    │  • ProductionRun (quality flags)                           │
    │  • Tags Mapping                                             │
    └─────────────────────────────────────────────────────────────┘
    ```
    """)
    
    st.divider()
    
    # Database tables reference
    st.markdown("## 📚 Database Schema Reference")
    
    db_tables = {
        "MachineTagValue": ["MachineCode", "OpcNodeId", "Value", "SourceTimestamp", "ProductionRunId"],
        "ProductionRun": ["RunId", "MachineCode", "StartTs", "EndTs", "Status", "ScopeKey"],
        "tags_mapping": ["MachineCode", "Parameter"],
        "recipe_parameters": ["RecipeId", "RecipeName", "Parameter", "MinValue", "MaxValue"],
    }
    
    for table, columns in db_tables.items():
        st.markdown(f"**{table}**")
        for col in columns:
            st.caption(f"  • {col}")
    
    st.divider()
    
    # Tips and best practices
    with st.expander("💡 Tips & Best Practices", expanded=False):
        st.markdown("""
        ### Configuration Tips
        - Start with one machine and a few key parameters
        - Test with historical data before using live feeds
        - Save configurations frequently to avoid losing work
        
        ### Model Training Tips
        - Ensure you have at least 10 production runs of historical data
        - Use recipes that have "OK" quality status for training
        - Retrain models after collecting new production data
        
        ### Monitoring Tips
        - Set up auto-refresh (5-10 seconds) for continuous monitoring
        - Use the traceability table to verify data quality
        - Check trend charts to identify anomalies early
        
        ### Performance Tips
        - Database caching improves response times (TTL: 60-600 seconds)
        - Limit parameters to those that impact quality
        - Close unused tabs in the dashboard
        """)
    
    st.divider()
    
    st.divider()


# ────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    display_home()
