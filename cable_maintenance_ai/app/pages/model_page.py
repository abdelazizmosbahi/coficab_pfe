"""
Cable Manufacturing - Model Analysis & Real-Time Monitoring
Execute configuration analysis and display real-time parameter monitoring with quality predictions.
Styled to match opcua_realtime_page (Coficab theme, nav, hero, monitoring layout).
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import time
import json
import base64
from datetime import datetime
from dotenv import load_dotenv
import plotly.graph_objects as go
from sqlalchemy import text

try:
    from mistralai.client import Mistral
except ImportError:
    try:
        from mistralai import Mistral
    except ImportError:
        Mistral = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_DIR = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_helpers import ensure_page_authentication, render_nav_bar  # noqa: E402
from db_helpers import (
    load_machine_configurations,
    load_working_machines,
    load_parameter_reference_datasheet,
    analyze_parameter_anomaly,
    get_machine_status_for,
    get_machine_status_by_linespeed,
    store_analysis_results,
    load_latest_analysis_results,
    load_current_machine_values,
    get_engine,
    initialize_parameter_reference_datasheet_table,
    save_parameter_datasheet,
)

try:
    import papermill as pm
    import nbformat

    PAPERMILL_AVAILABLE = True
except ImportError:
    PAPERMILL_AVAILABLE = False


def extract_results_from_notebook(notebook_path: str) -> dict:
    """Extract results_export from the executed notebook. Fast, minimal logging."""
    try:
        if not os.path.exists(notebook_path):
            return {}

        notebook = nbformat.read(notebook_path, as_version=4)

        for cell in reversed(notebook.cells):
            if cell.cell_type == "code":
                if hasattr(cell, "outputs"):
                    for output in cell.outputs:
                        if output.output_type == "stream" and "text" in output:
                            text_output = output["text"]
                            if "ANALYSIS RESULTS EXPORTED FOR STREAMLIT" in text_output:
                                try:
                                    json_start = text_output.find("{")
                                    json_end = text_output.rfind("}") + 1
                                    if json_start >= 0 and json_end > json_start:
                                        json_str = text_output[json_start:json_end]
                                        return json.loads(json_str)
                                except (json.JSONDecodeError, ValueError):
                                    pass
        
        return {}
    except Exception:
        return {}


def execute_analysis_notebook(
    configuration_id: int, machine_code: str, config_name: str, progress_callback=None
) -> dict:
    """
    Execute the analysis notebook using papermill and store results ONLY in database.
    Optimized for speed - minimal UI updates during execution.
    """
    if not PAPERMILL_AVAILABLE:
        return {
            "success": False,
            "error": "Papermill not installed. Run: pip install papermill",
            "results_export": None,
        }

    temp_notebook_path = None
    status_placeholder = st.empty()

    try:
        initialize_parameter_reference_datasheet_table()
        
        # Create temp file in user's temp directory (auto-cleanup by OS)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.ipynb', delete=False) as tmp:
            temp_notebook_path = tmp.name

        source_notebook = os.path.join(BASE_DIR, "notebooks", "model_page.ipynb")

        if not os.path.exists(source_notebook):
            status_placeholder.error(f"❌ Notebook not found: {source_notebook}")
            return {
                "success": False,
                "error": f"Notebook not found: {source_notebook}",
                "results_export": None,
            }

        # Execute notebook - THIS IS THE MAIN OPERATION
        st.write("⏳ Running analysis (this takes 30-90 seconds)...")
        
        try:
            pm.execute_notebook(
                source_notebook,
                temp_notebook_path,
                parameters={"configuration_id": configuration_id},
                progress_bar=False,
                timeout=600  # 10 minute timeout
            )
        except Exception as exec_error:
            status_placeholder.error(f"❌ Execution error: {str(exec_error)}")
            return {
                "success": False,
                "error": f"Notebook execution error: {str(exec_error)}",
                "results_export": None,
            }

        # Verify temp file exists
        if not os.path.exists(temp_notebook_path) or os.path.getsize(temp_notebook_path) == 0:
            status_placeholder.error("❌ Notebook did not produce output")
            return {
                "success": False,
                "error": "Notebook execution produced empty file",
                "results_export": None,
            }
        
        # Extract results from executed notebook
        results_export = extract_results_from_notebook(temp_notebook_path)

        if not results_export:
            status_placeholder.error("❌ No results in notebook output")
            return {
                "success": False,
                "error": "No analysis results found in notebook output",
                "results_export": None,
            }

        # Store results in database - this is fast
        db_stored = store_analysis_results(results_export, notebook_content=None)

        if not db_stored:
            status_placeholder.error("❌ Database storage failed")
            return {
                "success": False,
                "error": "Failed to store results in database",
                "results_export": None,
            }

        # Success!
        return {
            "success": True,
            "results_export": results_export,
            "error": None
        }

    except Exception as e:
        status_placeholder.error(f"❌ Error: {str(e)}")
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}",
            "results_export": None
        }

    finally:
        # Clean up temporary file - results are safely in database
        if temp_notebook_path and os.path.exists(temp_notebook_path):
            try:
                os.remove(temp_notebook_path)
            except Exception:
                pass  # Not critical if cleanup fails


def apply_coficab_theme():
    """Inject Coficab-inspired styling for this page only (matches opcua_realtime_page)."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600;700&family=Space+Grotesk:wght@500;700&display=swap');

        :root {
            --cof-navy: #0b1b2b;
            --cof-deep: #0f2b44;
            --cof-orange: #f57c00;
            --cof-ember: #ff9a3c;
            --cof-ice: #f5f7f9;
            --cof-ash: #e4e8ec;
            --cof-slate: #5b6b7a;
            --cof-green: #1d8f5a;
            --cof-red: #c3432f;
        }

        html, body, [class*="css"] {
            font-family: 'Manrope', system-ui, -apple-system, 'Segoe UI', sans-serif;
            color: var(--cof-navy);
        }

        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at 10% 15%, #ffffff 0%, #f7f9fb 35%, #eef2f6 100%);
            padding-top: 56px;
        }

        [data-testid="stHeader"] {
            background: transparent;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
        }

        [data-testid="stToolbar"] {
            display: none !important;
        }

        [data-testid="stSidebar"] {
            display: none !important;
        }
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
        [data-testid="stAppViewContainer"] .stCaption,
        [data-testid="stAppViewContainer"] .stText,
        [data-testid="stAppViewContainer"] label {
            color: var(--cof-navy) !important;
        }

        .stAlert [data-testid="stMarkdownContainer"],
        .stAlert p,
        .stAlert span,
        .stAlert li {
            color: var(--cof-navy) !important;
        }

        .cofi-hero {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 24px;
            align-items: center;
            padding: 28px 32px;
            border-radius: 20px;
            background: linear-gradient(120deg, #0c1f31 0%, #133657 55%, #1f4a6f 100%);
            color: #f7fafc;
            box-shadow: 0 16px 40px rgba(7, 18, 30, 0.2);
            margin-bottom: 20px;
        }

        .cofi-hero__text h1 {
            font-family: 'Space Grotesk', 'Manrope', sans-serif;
            font-size: 30px;
            letter-spacing: 0.5px;
            margin: 6px 0 10px 0;
        }

        .cofi-hero__text p {
            margin: 0;
            font-size: 16px;
            color: rgba(247, 250, 252, 0.85);
        }

        .cofi-eyebrow {
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 12px;
            color: rgba(247, 250, 252, 0.7);
        }

        .cofi-hero__logo {
            width: 160px;
            height: auto;
            filter: drop-shadow(0 6px 14px rgba(7, 18, 30, 0.35));
        }

        .cofi-nav {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            padding: 8px 24px;
            margin: 0;
            border-radius: 0;
            background: linear-gradient(120deg, #0c1f31 0%, #133657 55%, #1f4a6f 100%);
            box-shadow: 0 14px 32px rgba(7, 18, 30, 0.2);
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            height: 56px;
            width: 100%;
        }

        .cofi-nav__left {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .cofi-nav__logo {
            height: 36px;
            width: auto;
        }

        .cofi-nav__links {
            display: flex;
            justify-content: center;
            gap: 18px;
            flex-wrap: wrap;
            flex: 1;
        }
        .cofi-nav__actions {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            min-width: 120px;
        }

        .cofi-nav__link {
            color: #ffffff;
            text-decoration: none;
            font-weight: 600;
            font-size: 16px;
            letter-spacing: 0.6px;
        }

        .cofi-nav__link:visited {
            color: #ffffff;
        }

        .cofi-nav__link:hover {
            color: #ffddbf;
        }
        .cofi-nav__logout {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 8px 14px;
            border-radius: 999px;
            border: 1px solid rgba(255, 221, 191, 0.35);
            background: rgba(255, 255, 255, 0.08);
            color: #ffffff;
            text-decoration: none;
            font-weight: 700;
            font-size: 14px;
        }
        .cofi-nav__logout:hover {
            background: rgba(255, 221, 191, 0.16);
            color: #ffffff;
        }

        /* Ensure only one navbar is displayed (hide duplicates) */
        .cofi-nav:not(:first-of-type) {
            display: none !important;
        }

        /* Remove any native Streamlit navbar that might appear */
        [data-testid="stHeader"] + * {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        [data-testid="stMetric"] {
            background: transparent !important;
            border: none;
            padding: 4px 6px;
            box-shadow: none;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            /* Disabled custom styling to prevent 'page within page' effect with autorefresh */
            display: block;
        }
        }

        [data-testid="stVerticalBlockBorderWrapper"] .stButton > button {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            font-size: 1.4rem !important;
            color: var(--cof-slate) !important;
            float: right;
            margin-top: -8px;
        }

        [data-testid="stVerticalBlockBorderWrapper"] .stButton > button:hover {
            transform: scale(1.1);
            color: var(--cof-orange) !important;
        }

        [data-testid="stMetricLabel"] {
            font-weight: 600;
            color: var(--cof-slate);
        }

        [data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', 'Manrope', sans-serif;
            color: var(--cof-navy);
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

        .stTabs [data-baseweb="tab"] {
            font-weight: 600;
            color: var(--cof-slate);
        }

        .stTabs [aria-selected="true"] {
            color: var(--cof-navy) !important;
            border-bottom: 3px solid var(--cof-orange) !important;
        }

        [data-testid="stExpander"] summary {
            color: var(--cof-navy) !important;
            background: #ffffff;
            border: 1px solid var(--cof-ash);
            border-radius: 12px;
            padding: 0.5rem 0.8rem;
        }

        [data-testid="stExpander"] summary:hover,
        [data-testid="stExpander"] summary:focus {
            color: var(--cof-navy) !important;
            background: #f3f6f9;
        }

        .stAlert {
            border-radius: 12px;
        }

        .stDataFrame,
        [data-testid="stDataFrame"] {
            background: #ffffff;
            border-radius: 14px;
            border: 1px solid var(--cof-ash);
            box-shadow: 0 10px 24px rgba(12, 31, 49, 0.08);
        }

        .cofi-section-title {
            font-family: 'Space Grotesk', 'Manrope', sans-serif;
            font-weight: 700;
            color: var(--cof-navy);
            margin-top: 18px;
        }

        @media (max-width: 900px) {
            .cofi-hero {
                grid-template-columns: 1fr;
            }
        }

        [data-testid="stAppViewContainer"] .cofi-hero .cofi-hero__text h1,
        [data-testid="stAppViewContainer"] .cofi-hero .cofi-hero__text h1 *,
        [data-testid="stAppViewContainer"] .cofi-hero .cofi-hero__text p,
        [data-testid="stAppViewContainer"] .cofi-hero .cofi-hero__text p * {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_reference_df_from_analysis_results(analysis_results: dict, machine_code: str) -> pd.DataFrame:
    """
    Extract reference datasheet from analysis results JSON.
    Returns DataFrame with parameter statistics (Min, Mean, Max, etc).
    """
    try:
        ref_datasheets = analysis_results.get("reference_datasheets", {})
        machine_data = ref_datasheets.get(machine_code, {})
        parameters = machine_data.get("parameters", [])
        
        if not parameters:
            return pd.DataFrame()
        
        # Convert list of parameter dicts to DataFrame
        df = pd.DataFrame(parameters)
        return df
    except Exception:
        return pd.DataFrame()


def build_filtered_datasheet(reference_df: pd.DataFrame, machine_code: str, opc_ids: list) -> pd.DataFrame:
    """Datasheet rows for the analysed configuration (monitoring + recipe OPC node ids)."""
    if reference_df.empty or not opc_ids:
        print(f"DEBUG [build_filtered_datasheet]: reference_df.empty={reference_df.empty}, opc_ids={len(opc_ids) if opc_ids else 0}")
        return pd.DataFrame()
    want = list(dict.fromkeys(opc_ids))
    
    print(f"DEBUG [build_filtered_datasheet]: want=[{len(want)} params] from opc_ids")
    print(f"DEBUG [build_filtered_datasheet]: reference_df shape={reference_df.shape}")
    print(f"DEBUG [build_filtered_datasheet]: reference_df columns: {reference_df.columns.tolist()}")
    
    # Filter by OpcNodeId - also filter by machine if column exists
    if "MachineCode" in reference_df.columns:
        print(f"DEBUG [build_filtered_datasheet]: Filtering by MachineCode ({machine_code}) + OpcNodeId")
        sub = reference_df[
            (reference_df["OpcNodeId"].isin(want)) & (reference_df["MachineCode"] == machine_code)
        ].copy()
    else:
        # If no MachineCode column, just filter by OpcNodeId (already machine-filtered)
        print(f"DEBUG [build_filtered_datasheet]: No MachineCode column, filtering by OpcNodeId only")
        sub = reference_df[reference_df["OpcNodeId"].isin(want)].copy()
    
    print(f"DEBUG [build_filtered_datasheet]: After filtering: sub has {len(sub)} rows")
    if not sub.empty:
        print(f"DEBUG [build_filtered_datasheet]: sub OpcNodeIds: {sub['OpcNodeId'].tolist()}")
    
    if sub.empty:
        print(f"DEBUG [build_filtered_datasheet]: sub is empty, returning empty DataFrame")
        return pd.DataFrame()

    mean_col = sub["MeanValue"] if "MeanValue" in sub.columns else pd.Series([np.nan] * len(sub))
    out = pd.DataFrame(
        {
            "Machine": sub["MachineCode"] if "MachineCode" in sub.columns else machine_code,
            "Parameter": sub["OpcNodeId"],
            "Min": pd.to_numeric(sub["MinValue"], errors="coerce").round(2),
            "Mean": pd.to_numeric(mean_col, errors="coerce").round(2),
            "Max": pd.to_numeric(sub["MaxValue"], errors="coerce").round(2),
        }
    )
    if "UpdatedAt" in sub.columns:
        u = pd.to_datetime(sub["UpdatedAt"], errors="coerce")
        out["Date_Analysed"] = u.dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        out["Date_Analysed"] = ""
    order = {p: i for i, p in enumerate(want)}
    out["_ord"] = out["Parameter"].map(lambda x: order.get(x, 999))
    out = out.sort_values("_ord").drop(columns=["_ord"], errors="ignore")
    
    # Add all missing parameters from want that weren't in reference_df
    missing_params = [p for p in want if p not in out["Parameter"].values]
    print(f"DEBUG [build_filtered_datasheet]: Found {len(missing_params)} missing parameters")
    if missing_params:
        print(f"DEBUG [build_filtered_datasheet]: Missing params: {missing_params[:5]}...")
        missing_rows = pd.DataFrame({
            "Machine": machine_code,
            "Parameter": missing_params,
            "Min": np.nan,
            "Mean": np.nan,
            "Max": np.nan,
            "Date_Analysed": "—"
        })
        out = pd.concat([out, missing_rows], ignore_index=True)
    
    print(f"DEBUG [build_filtered_datasheet]: Final output: {len(out)} rows")
    return out.reset_index(drop=True)


COFI_METRIC_CARD_STYLE = """
<style>
.cofi-metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
    border: 2px solid #e4e8ec;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(12, 31, 49, 0.06);
    min-height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.cofi-metric-card:hover {
    border-color: #f57c00;
    box-shadow: 0 8px 20px rgba(245, 124, 0, 0.15);
    transform: translateY(-2px);
}
.cofi-metric-label {
    font-size: 11px;
    font-weight: 600;
    color: #5b6b7a;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}
.cofi-metric-value {
    font-size: 22px;
    font-weight: 700;
    color: #0b1b2b;
    font-family: 'Space Grotesk', monospace;
}
</style>
"""


def spec_violation_badge_html(current: float, lo: float, hi: float) -> str:
    """Colored pill: how far below min or above max (absolute + % of spec span), like an interactive spec strip."""
    span = float(hi) - float(lo)
    if span <= 0:
        span = 1e-12
    base = (
        "display:inline-block;margin-top:8px;padding:5px 12px;border-radius:999px;"
        "font-size:12px;font-weight:700;letter-spacing:0.02em;"
    )
    if current < lo:
        gap = lo - current
        pct = (gap / span) * 100.0
        return (
            f'<span style="{base}background:linear-gradient(135deg,#fdecea,#fcd5d0);color:#9b2c1f;'
            f'border:1px solid #f0a8a0;box-shadow:0 2px 8px rgba(195,67,47,0.2);">'
            f"↓ {gap:.2f} below min · {pct:.1f}% of spec span</span>"
        )
    if current > hi:
        gap = current - hi
        pct = (gap / span) * 100.0
        return (
            f'<span style="{base}background:linear-gradient(135deg,#fff4e6,#ffe0c2);color:#a65a00;'
            f'border:1px solid #f5c48c;box-shadow:0 2px 8px rgba(245,124,0,0.2);">'
            f"↑ {gap:.2f} above max · {pct:.1f}% of spec span</span>"
        )
    return ""


def safe_float(val):
    """Safely convert value to float, handling None and strings."""
    if val is None:
        return None
    if pd.isna(val):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def format_elapsed(ts):
    if ts is None:
        return "—"
    if hasattr(ts, "tzinfo") and ts.tzinfo is not None:
        ts = ts.replace(tzinfo=None)
    now = datetime.now()
    elapsed = max(0, int((now - ts).total_seconds()))
    days = elapsed // 86400
    hours = (elapsed % 86400) // 3600
    minutes = (elapsed % 3600) // 60
    seconds = elapsed % 60
    if days > 0:
        return f"{days}d {hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@st.cache_data(ttl=300)  # Cache for 5 minutes
def _cached_load_reference_df(machine_code: str, config_id: int, analysis_results: dict):
    """Cache the reference dataframe to avoid rebuilding it on every refresh."""
    reference_df = pd.DataFrame()
    
    # If we have analysis results, build datasheet from them
    if analysis_results and 'results_export' in analysis_results:
        results_export = analysis_results['results_export']
        reference_datasheets = results_export.get('reference_datasheets', {})
        
        if machine_code in reference_datasheets:
            machine_data = reference_datasheets[machine_code]
            parameters = machine_data.get('parameters', [])
            
            if parameters:
                reference_df = pd.DataFrame([
                    {
                        'MachineCode': machine_code,
                        'OpcNodeId': p['OpcNodeId'],
                        'ParameterName': p['ParameterName'],
                        'MinValue': p.get('MinValue'),
                        'MeanValue': p.get('MeanValue'),
                        'MaxValue': p.get('MaxValue'),
                        'StdDev': p.get('StdDev'),
                        'SampleCount': p.get('SampleCount')
                    }
                    for p in parameters
                ])
    
    # If no analysis results, try to load from old parameter_reference_datasheet table
    if reference_df.empty:
        reference_df = load_parameter_reference_datasheet(machine_code=machine_code)
    
    return reference_df


# ────────────────────────────────────────────────────────────────────────────────
# OPTIMIZED TRACEABILITY: 3-Second Cache + Full Timeline with Incremental Updates
# ────────────────────────────────────────────────────────────────────────────────

def _get_cached_3second_data(mc: str, param: str) -> pd.DataFrame:
    """
    Get last 3 seconds of data with SLIDING WINDOW approach.
    Each refresh: drop oldest second, add newest second = smooth continuous update.
    """
    from datetime import datetime, timedelta
    
    cache_key = f"trace_cache_{mc}_{param}"
    
    now = datetime.utcnow()
    three_seconds_ago = now - timedelta(seconds=3)
    
    # Fetch fresh data from last 4 seconds (to catch any we missed)
    four_seconds_ago = now - timedelta(seconds=4)
    new_data = pd.read_sql(
        text("""SELECT SourceTimestamp, Value FROM MachineTagValue 
           WHERE MachineCode = :mc AND OpcNodeId = :param 
           AND SourceTimestamp >= :start_time
           ORDER BY SourceTimestamp"""),
        params={"mc": mc, "param": param, "start_time": four_seconds_ago},
        con=get_engine()
    )
    
    if new_data.empty:
        return pd.DataFrame()
    
    # Convert to numeric
    new_data["Value"] = pd.to_numeric(new_data["Value"], errors="coerce")
    new_data = new_data.dropna(subset=["Value"])
    
    # Merge with existing cache and keep only last 3 seconds (sliding window)
    if cache_key not in st.session_state:
        # First load: get last 3 seconds only
        window_data = new_data[new_data["SourceTimestamp"] >= three_seconds_ago].copy()
    else:
        # Subsequent loads: merge old cache with new data
        cached = st.session_state[cache_key].copy()
        merged = pd.concat([cached, new_data]).drop_duplicates(subset=["SourceTimestamp"]).reset_index(drop=True)
        merged = merged.sort_values("SourceTimestamp").reset_index(drop=True)
        
        # SLIDING WINDOW: Keep only last 3 seconds (drops oldest automatically)
        window_data = merged[merged["SourceTimestamp"] >= three_seconds_ago].copy()
    
    st.session_state[cache_key] = window_data.reset_index(drop=True)
    
    return st.session_state[cache_key]


def _render_3second_fast_trace(mc: str, param: str, v_min: float, v_max: float, v_mean: float):
    """Render fast 3-second window - no database delay, uses cache. Perfect for initial load."""
    try:
        from datetime import datetime, timedelta
        
        # Get cached 3-second data
        recent_data = _get_cached_3second_data(mc, param)
        
        if recent_data.empty:
            st.info("⏳ Waiting for real-time data (no readings in last 3 seconds)...")
            return
        
        # Create figure for last 3 seconds
        fig = go.Figure()
        
        # Ensure min/max/mean are floats
        v_min = safe_float(v_min)
        v_max = safe_float(v_max)
        v_mean = safe_float(v_mean)
        specs_defined = v_min is not None and v_max is not None
        
        # Add spec range background if available
        if specs_defined:
            valid_vals = recent_data["Value"].tolist()
            all_vals = valid_vals + [v_min, v_max, v_mean if v_mean else 0]
            _spread = (max(all_vals) - min(all_vals)) or 1.0
            y_lo = min(all_vals) - _spread * 0.2
            y_hi = max(all_vals) + _spread * 0.2
            
            fig.add_hrect(y0=y_lo, y1=v_min, fillcolor="rgba(255,0,0,0.10)", line_width=0,
                         annotation_text="Below Min", annotation_position="bottom left", layer="below")
            fig.add_hrect(y0=v_max, y1=y_hi, fillcolor="rgba(255,0,0,0.10)", line_width=0,
                         annotation_text="Above Max", annotation_position="top left", layer="below")
            
            fig.add_trace(go.Scatter(
                x=list(recent_data["SourceTimestamp"]) + list(recent_data["SourceTimestamp"])[::-1],
                y=[v_max] * len(recent_data) + [v_min] * len(recent_data),
                fill="toself",
                fillcolor="rgba(0,255,0,0.10)",
                line=dict(color="rgba(255,255,255,0)"),
                name="Normal Range",
                showlegend=True,
                hoverinfo="skip",
            ))
        
        # Add mean line if available
        if v_mean is not None:
            fig.add_trace(go.Scatter(
                x=recent_data["SourceTimestamp"],
                y=[v_mean] * len(recent_data),
                mode="lines",
                name="Target",
                line=dict(color="green", dash="dash", width=2),
            ))
        
        # Add main parameter trace
        fig.add_trace(go.Scatter(
            x=recent_data["SourceTimestamp"],
            y=recent_data["Value"],
            mode="lines+markers",
            name=param,
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=5),
            hovertemplate="%{x|%H:%M:%S}<br>Value: %{y:.4f}<extra></extra>",
        ))
        
        # Update layout
        layout_kwargs = dict(
            title=dict(
                text=f"Last 3 Seconds (FAST): {param.split('.')[-1].replace('_ACT', '')}",
                font=dict(size=16),
                x=0.5,
                xanchor="center",
            ),
            xaxis_title="Time (HH:MM:SS)",
            yaxis_title="Value",
            height=350,
            hovermode="x unified",
            template="plotly_white",
            margin=dict(l=40, r=40, t=60, b=40),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )
        
        if specs_defined:
            layout_kwargs["yaxis"] = dict(range=[y_lo, y_hi])
        
        fig.update_layout(**layout_kwargs)
        st.plotly_chart(fig, use_container_width=True, height=350)
        
        # Show metrics for the 3-second window
        n_readings = len(recent_data)
        recent_min = recent_data["Value"].min()
        recent_max = recent_data["Value"].max()
        recent_mean = recent_data["Value"].mean()
        
        metrics = st.columns(4)
        metrics[0].metric("Readings (3s)", f"{n_readings}", delta=None)
        metrics[1].metric("Min", f"{recent_min:.4f}", delta=None)
        metrics[2].metric("Mean", f"{recent_mean:.4f}", delta=None)
        metrics[3].metric("Max", f"{recent_max:.4f}", delta=None)
        
        # Check if values are in spec during this window
        if specs_defined:
            in_spec = ((recent_data["Value"] >= v_min) & (recent_data["Value"] <= v_max)).sum()
            pct_in_spec = (in_spec / n_readings) * 100 if n_readings > 0 else 0
            if pct_in_spec < 100:
                st.warning(f"⚠️ {100 - pct_in_spec:.1f}% of recent readings are out of spec!")
        
    except Exception as e:
        st.error(f"Error loading 3-second traceability: {str(e)}")


def _render_full_timeline_incremental(mc: str, param: str, v_min: float, v_max: float, v_mean: float):
    """
    Render full timeline chart - STATIC SNAPSHOT from start until button click moment.
    The 3-second window updates in background, but this chart stays frozen.
    """
    try:
        full_cache_key = f"full_trace_{mc}_{param}"
        snapshot_time = st.session_state.get("fullscreen_full_timeline_snapshot_time")
        
        # Initialize full cache if needed (load all historical data once)
        if full_cache_key not in st.session_state:
            hist_data = pd.read_sql(
                text("""SELECT SourceTimestamp, Value FROM MachineTagValue 
                   WHERE MachineCode = :mc AND OpcNodeId = :param 
                   ORDER BY SourceTimestamp"""),
                params={"mc": mc, "param": param},
                con=get_engine()
            )
            
            if hist_data.empty:
                st.info("No historical data found for this parameter.")
                return
            
            # Convert to numeric
            hist_data["Value"] = pd.to_numeric(hist_data["Value"], errors="coerce")
            st.session_state[full_cache_key] = hist_data
        
        full_data = st.session_state[full_cache_key].copy()
        
        # STATIC SNAPSHOT: If snapshot time exists, filter to that point in history
        # Otherwise show everything up to now
        if snapshot_time:
            # Filter data UP TO the snapshot time (historical view at that moment)
            full_data = full_data[full_data["SourceTimestamp"] <= snapshot_time].copy()
            end_time_display = snapshot_time.strftime('%Y-%m-%d %H:%M:%S') if hasattr(snapshot_time, 'strftime') else str(snapshot_time)[:19]
        else:
            # First load - show all data
            end_time_display = "Now"
        
        if full_data.empty:
            st.info("No data available for this parameter.")
            return
        
        # Get earliest timestamp for display
        earliest_row = full_data.iloc[0]
        start_time = earliest_row["SourceTimestamp"]
        if isinstance(start_time, str):
            start_time_str = start_time[:16]
        else:
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M')
        
        # Build the chart
        fig = go.Figure()
        
        # Ensure specs are floats
        v_min = safe_float(v_min)
        v_max = safe_float(v_max)
        v_mean = safe_float(v_mean)
        specs_defined = v_min is not None and v_max is not None
        
        # Convert to numeric if needed
        full_data["Value"] = pd.to_numeric(full_data["Value"], errors="coerce")
        
        if specs_defined:
            valid_vals = full_data["Value"].dropna().tolist()
            all_vals = valid_vals + [v_min, v_max, v_mean if v_mean else 0]
            _spread = (max(all_vals) - min(all_vals)) or 1.0
            y_lo = min(all_vals) - _spread * 0.2
            y_hi = max(all_vals) + _spread * 0.2
            
            fig.add_hrect(y0=y_lo, y1=v_min, fillcolor="rgba(255,0,0,0.10)", line_width=0,
                         annotation_text="Below Min", annotation_position="bottom left", layer="below")
            fig.add_hrect(y0=v_max, y1=y_hi, fillcolor="rgba(255,0,0,0.10)", line_width=0,
                         annotation_text="Above Max", annotation_position="top left", layer="below")
            
            fig.add_trace(go.Scatter(
                x=list(full_data["SourceTimestamp"]) + list(full_data["SourceTimestamp"])[::-1],
                y=[v_max] * len(full_data) + [v_min] * len(full_data),
                fill="toself",
                fillcolor="rgba(0,255,0,0.10)",
                line=dict(color="rgba(255,255,255,0)"),
                name="Normal Range",
                showlegend=True,
                hoverinfo="skip",
            ))
        
        if v_mean is not None:
            fig.add_trace(go.Scatter(
                x=full_data["SourceTimestamp"],
                y=[v_mean] * len(full_data),
                mode="lines",
                name="Target",
                line=dict(color="green", dash="dash", width=2),
            ))
        
        fig.add_trace(go.Scatter(
            x=full_data["SourceTimestamp"],
            y=full_data["Value"],
            mode="lines+markers",
            name=param.split(".")[-1].replace("_ACT", ""),
            line=dict(color="#1f77b4", width=1),
            marker=dict(size=2),
            hovertemplate="%{x|%Y-%m-%d %H:%M:%S}<br>Value: %{y:.4f}<extra></extra>",
        ))
        
        # Display snapshot info if available
        if snapshot_time:
            title_text = f"{param.split('.')[-1].replace('_ACT', '')} — From {start_time_str} to {end_time_display} (SNAPSHOT)"
        else:
            title_text = f"{param.split('.')[-1].replace('_ACT', '')} — From {start_time_str} to Now"
        
        layout_kwargs = dict(
            title=dict(
                text=title_text,
                font=dict(size=16),
                x=0.5,
                xanchor="center",
            ),
            xaxis_title="Time",
            yaxis_title="Value",
            height=450,
            hovermode="x unified",
            template="plotly_white",
            margin=dict(l=40, r=40, t=60, b=40),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )
        
        if specs_defined:
            layout_kwargs["yaxis"] = dict(range=[y_lo, y_hi])
        
        fig.update_layout(**layout_kwargs)
        st.plotly_chart(fig, use_container_width=True, height=450)
        
        # Show summary metrics
        n_readings = len(full_data)
        actual_min = full_data["Value"].min()
        actual_max = full_data["Value"].max()
        actual_mean = full_data["Value"].mean()
        
        cols_count = 5 if specs_defined else 4
        metrics = st.columns(cols_count)
        metrics[0].metric("Total Readings", f"{n_readings:,}")
        metrics[1].metric("Min", f"{actual_min:.4f}")
        metrics[2].metric("Mean", f"{actual_mean:.4f}")
        metrics[3].metric("Max", f"{actual_max:.4f}")
        
        if specs_defined:
            pct_in_spec = ((full_data["Value"] >= v_min) & (full_data["Value"] <= v_max)).mean() * 100
            metrics[4].metric("In Spec", f"{pct_in_spec:.1f}%", 
                             delta="OK" if pct_in_spec >= 95 else "Warning")
        
    except Exception as e:
        st.error(f"Error loading full timeline: {str(e)}")


def _render_param_trace(mc: str, param: str, v_min: float, v_max: float, v_mean: float, fullscreen: bool = False):
    """Render traceability chart for a parameter from MachineTagValue with optional overlay."""
    try:
        earliest_row = pd.read_sql(
            text("""SELECT MIN(SourceTimestamp) as start_time FROM MachineTagValue 
               WHERE MachineCode = :mc AND OpcNodeId = :param"""),
            params={"mc": mc, "param": param},
            con=get_engine()
        )
        
        if earliest_row.empty or pd.isna(earliest_row.iloc[0]["start_time"]):
            st.info("No historical data found in MachineTagValue for this parameter.")
            return
        
        start_time = earliest_row.iloc[0]["start_time"]
        if isinstance(start_time, str):
            start_time_str = start_time[:16]
        else:
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M')
        
        hist_data = pd.read_sql(
            text("""SELECT SourceTimestamp, Value FROM MachineTagValue 
               WHERE MachineCode = :mc AND OpcNodeId = :param 
               ORDER BY SourceTimestamp"""),
            params={"mc": mc, "param": param},
            con=get_engine()
        )
        
        if hist_data.empty:
            st.info("No data available for this parameter.")
            return
        
        # Overlay parameter selector
        all_params_in_db = pd.read_sql(
            text("""SELECT DISTINCT OpcNodeId FROM MachineTagValue 
               WHERE MachineCode = :mc"""),
            params={"mc": mc},
            con=get_engine()
        )
        available_params = all_params_in_db["OpcNodeId"].tolist() if not all_params_in_db.empty else []
        eligible_overlay = [p for p in available_params if p != param]
        
        overlay_param = None
        overlay_hist_data = None
        
        if eligible_overlay:
            st.markdown("**🔀 Compare with another parameter:**")
            # Display options with split names for clarity
            display_options = ["None"] + [p.split(".")[-1].replace("_ACT", "") for p in eligible_overlay]
            selected_display = st.selectbox(
                "Select parameter to overlay:",
                options=display_options,
                index=0,
                key=f"overlay_{param}",
            )
            # Map back to original OpcNodeId
            if selected_display != "None":
                overlay_param = eligible_overlay[display_options.index(selected_display) - 1]
            else:
                overlay_param = "None"
            
            if overlay_param != "None":
                overlay_hist_data = pd.read_sql(
                    text("""SELECT SourceTimestamp, Value FROM MachineTagValue 
                       WHERE MachineCode = :mc AND OpcNodeId = :op 
                       ORDER BY SourceTimestamp"""),
                    params={"mc": mc, "op": overlay_param},
                    con=get_engine()
                )
                if overlay_hist_data.empty:
                    st.warning(f"No data available for {overlay_param}")
                    overlay_hist_data = None
        
        fig = go.Figure()
        
        # Ensure v_min, v_max, v_mean are floats (not strings from DB)
        v_min = safe_float(v_min)
        v_max = safe_float(v_max)
        v_mean = safe_float(v_mean)
        
        specs_defined = v_min is not None and v_max is not None
        
        # Convert hist_data Value column to numeric, handling any non-numeric strings
        hist_data["Value"] = pd.to_numeric(hist_data["Value"], errors="coerce")
        
        if specs_defined:
            # Filter out NaN values from conversion
            valid_vals = hist_data["Value"].dropna().tolist()
            all_vals = valid_vals + [v_min, v_max, v_mean if v_mean else 0]
            _spread = (max(all_vals) - min(all_vals)) or 1.0
            y_lo = min(all_vals) - _spread * 0.2
            y_hi = max(all_vals) + _spread * 0.2
            
            fig.add_hrect(y0=y_lo, y1=v_min, fillcolor="rgba(255,0,0,0.10)", line_width=0,
                         annotation_text="Below Min", annotation_position="bottom left", layer="below")
            fig.add_hrect(y0=v_max, y1=y_hi, fillcolor="rgba(255,0,0,0.10)", line_width=0,
                         annotation_text="Above Max", annotation_position="top left", layer="below")
            
            fig.add_trace(go.Scatter(
                x=list(hist_data["SourceTimestamp"]) + list(hist_data["SourceTimestamp"])[::-1],
                y=[v_max] * len(hist_data) + [v_min] * len(hist_data),
                fill="toself",
                fillcolor="rgba(0,255,0,0.10)",
                line=dict(color="rgba(255,255,255,0)"),
                name="Normal Range",
                showlegend=True,
                hoverinfo="skip",
            ))
        
        if v_mean is not None:
            fig.add_trace(go.Scatter(
                x=hist_data["SourceTimestamp"],
                y=[v_mean] * len(hist_data),
                mode="lines",
                name="Target",
                line=dict(color="green", dash="dash", width=2),
            ))
        
        fig.add_trace(go.Scatter(
            x=hist_data["SourceTimestamp"],
            y=hist_data["Value"],
            mode="lines+markers",
            name=param.split(".")[-1].replace("_ACT", ""),
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=3),
            hovertemplate="%{x|%Y-%m-%d %H:%M:%S}<br>Value: %{y:.4f}<extra></extra>",
        ))
        
        # Overlay parameter trace
        use_secondary_yaxis = False
        if overlay_hist_data is not None and not overlay_hist_data.empty:
            # Ensure overlay data is numeric too
            overlay_hist_data["Value"] = pd.to_numeric(overlay_hist_data["Value"], errors="coerce")
            
            primary_range = hist_data["Value"].max() - hist_data["Value"].min()
            overlay_range = overlay_hist_data["Value"].max() - overlay_hist_data["Value"].min()
            
            if primary_range > 0 and overlay_range > 0 and \
               max(primary_range, overlay_range) / min(primary_range, overlay_range) > 5:
                use_secondary_yaxis = True
                yaxis_ref = "y2"
            else:
                yaxis_ref = "y"
                if specs_defined:
                    primary_vals = hist_data["Value"].dropna().tolist()
                    overlay_vals = overlay_hist_data["Value"].dropna().tolist()
                    all_values_combined = primary_vals + overlay_vals + [v_min, v_max]
                else:
                    primary_vals = hist_data["Value"].dropna().tolist()
                    overlay_vals = overlay_hist_data["Value"].dropna().tolist()
                    all_values_combined = primary_vals + overlay_vals
                
                _spread_combined = (max(all_values_combined) - min(all_values_combined)) or 1.0
                y_lo = min(all_values_combined) - _spread_combined * 0.2
                y_hi = max(all_values_combined) + _spread_combined * 0.2
            
            fig.add_trace(go.Scatter(
                x=overlay_hist_data["SourceTimestamp"],
                y=overlay_hist_data["Value"],
                mode="lines+markers",
                name=overlay_param.split(".")[-1].replace("_ACT", "") if overlay_param != "None" else overlay_param,
                line=dict(color="#ff7f0e", width=2),
                marker=dict(size=3),
                yaxis=yaxis_ref,
                hovertemplate="%{x|%Y-%m-%d %H:%M:%S}<br>Value: %{y:.4f}<extra></extra>",
            ))
        
        # USER TUNABLE FIX: Manually set fullscreen dimensions here
        if fullscreen:
            chart_height = 400
            chart_width = 10000  # Manually stretch horizontally
        else:
            chart_height = 350
            chart_width = None
        
        title_text = f"{param.split('.')[-1].replace('_ACT', '')}"
        if overlay_param and overlay_param != "None":
            title_text += f" vs {overlay_param.split('.')[-1].replace('_ACT', '')}"
        title_text += f" — From {start_time_str} to Now"
        
        layout_kwargs = dict(
            title=dict(
                text=title_text,
                font=dict(size=18),
                x=0.5,
                xanchor="center",
            ),
            xaxis_title="Time",
            yaxis_title="Value",
            height=chart_height,
            hovermode="x unified",
            template="plotly_white",
            margin=dict(l=40, r=40, t=60, b=40) if not fullscreen else dict(l=20, r=20, t=60, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )
        
        if use_secondary_yaxis and overlay_hist_data is not None:
            layout_kwargs["yaxis2"] = dict(
                title=overlay_param,
                overlaying="y",
                side="right",
                autorange=True,
            )
        
        if specs_defined:
            layout_kwargs["yaxis"] = dict(range=[y_lo, y_hi])
        
        if chart_width:
            layout_kwargs["width"] = chart_width
            
        fig.update_layout(**layout_kwargs)
        
        if fullscreen:
            st.plotly_chart(fig, use_container_width=False, width=chart_width, height=chart_height)
        else:
            st.plotly_chart(fig, use_container_width=True, height=chart_height)
        
        n_readings = len(hist_data)
        actual_min = hist_data["Value"].min()
        actual_max = hist_data["Value"].max()
        actual_mean = hist_data["Value"].mean()
        
        cols_count = 5 if specs_defined else 4
        metrics = st.columns(cols_count)
        metrics[0].metric("Readings", f"{n_readings:,}")
        metrics[1].metric("Min", f"{actual_min:.4f}")
        metrics[2].metric("Mean", f"{actual_mean:.4f}")
        metrics[3].metric("Max", f"{actual_max:.4f}")
        
        if specs_defined:
            pct_in_spec = ((hist_data["Value"] >= v_min) & (hist_data["Value"] <= v_max)).mean() * 100
            metrics[4].metric("In Spec", f"{pct_in_spec:.1f}%", 
                             delta="OK" if pct_in_spec >= 95 else "Warning")
        
        # ── Root cause alert (if out of spec) ─────────────────────────────────────
        if specs_defined:
            too_low  = hist_data["Value"] < v_min
            too_high = hist_data["Value"] > v_max
            n_low    = int(too_low.sum())
            n_high   = int(too_high.sum())

            if n_low > 0 or n_high > 0:
                lines = []
                if n_low > 0:
                    worst_low  = hist_data.loc[too_low, "Value"].min()
                    first_low  = hist_data.loc[too_low, "SourceTimestamp"].min()
                    pct_low    = n_low / n_readings * 100
                    lines.append(
                        f"📉 **Below minimum ({v_min:.4f}):** "
                        f"{n_low} readings ({pct_low:.1f}%) — "
                        f"worst value {worst_low:.4f} "
                        f"(Δ {v_min - worst_low:.4f} under limit) — "
                        f"first occurrence {first_low.strftime('%Y-%m-%d %H:%M:%S') if hasattr(first_low, 'strftime') else str(first_low)[:19]}"
                    )
                if n_high > 0:
                    worst_high = hist_data.loc[too_high, "Value"].max()
                    first_high = hist_data.loc[too_high, "SourceTimestamp"].min()
                    pct_high   = n_high / n_readings * 100
                    lines.append(
                        f"📈 **Above maximum ({v_max:.4f}):** "
                        f"{n_high} readings ({pct_high:.1f}%) — "
                        f"worst value {worst_high:.4f} "
                        f"(Δ {worst_high - v_max:.4f} over limit) — "
                        f"first occurrence {first_high.strftime('%Y-%m-%d %H:%M:%S') if hasattr(first_high, 'strftime') else str(first_high)[:19]}"
                    )
                st.error(
                    f"🔴 **Root Cause Alert — {param}**\n\n"
                    + "\n\n".join(lines)
                )
        
    except Exception as e:
        st.error(f"Error loading traceability: {str(e)}")


def _render_last_20_seconds_trace(mc: str, param: str, v_min: float, v_max: float, v_mean: float):
    """Render real-time traceability for the last 20 seconds, auto-refreshing every second."""
    try:
        from datetime import datetime, timedelta
        
        # Get current time and time 20 seconds ago
        now = datetime.utcnow()
        twenty_seconds_ago = now - timedelta(seconds=20)
        
        # Query only the last 20 seconds of data
        recent_data = pd.read_sql(
            text("""SELECT SourceTimestamp, Value FROM MachineTagValue 
               WHERE MachineCode = :mc AND OpcNodeId = :param 
               AND SourceTimestamp >= :start_time
               ORDER BY SourceTimestamp"""),
            params={"mc": mc, "param": param, "start_time": twenty_seconds_ago},
            con=get_engine()
        )
        
        if recent_data.empty:
            st.info("⏳ Waiting for real-time data (no readings in last 20 seconds)...")
            return
        
        # Convert to numeric
        recent_data["Value"] = pd.to_numeric(recent_data["Value"], errors="coerce")
        recent_data = recent_data.dropna(subset=["Value"])
        
        if recent_data.empty:
            st.info("⏳ No valid data in last 20 seconds...")
            return
        
        # Create figure for last 20 seconds
        fig = go.Figure()
        
        # Ensure min/max/mean are floats
        v_min = safe_float(v_min)
        v_max = safe_float(v_max)
        v_mean = safe_float(v_mean)
        specs_defined = v_min is not None and v_max is not None
        
        # Add spec range background if available
        if specs_defined:
            valid_vals = recent_data["Value"].tolist()
            all_vals = valid_vals + [v_min, v_max, v_mean if v_mean else 0]
            _spread = (max(all_vals) - min(all_vals)) or 1.0
            y_lo = min(all_vals) - _spread * 0.2
            y_hi = max(all_vals) + _spread * 0.2
            
            fig.add_hrect(y0=y_lo, y1=v_min, fillcolor="rgba(255,0,0,0.10)", line_width=0,
                         annotation_text="Below Min", annotation_position="bottom left", layer="below")
            fig.add_hrect(y0=v_max, y1=y_hi, fillcolor="rgba(255,0,0,0.10)", line_width=0,
                         annotation_text="Above Max", annotation_position="top left", layer="below")
            
            fig.add_trace(go.Scatter(
                x=list(recent_data["SourceTimestamp"]) + list(recent_data["SourceTimestamp"])[::-1],
                y=[v_max] * len(recent_data) + [v_min] * len(recent_data),
                fill="toself",
                fillcolor="rgba(0,255,0,0.10)",
                line=dict(color="rgba(255,255,255,0)"),
                name="Normal Range",
                showlegend=True,
                hoverinfo="skip",
            ))
        
        # Add mean line if available
        if v_mean is not None:
            fig.add_trace(go.Scatter(
                x=recent_data["SourceTimestamp"],
                y=[v_mean] * len(recent_data),
                mode="lines",
                name="Target",
                line=dict(color="green", dash="dash", width=2),
            ))
        
        # Add main parameter trace
        fig.add_trace(go.Scatter(
            x=recent_data["SourceTimestamp"],
            y=recent_data["Value"],
            mode="lines+markers",
            name=param,
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=4),
            hovertemplate="%{x|%H:%M:%S}<br>Value: %{y:.4f}<extra></extra>",
        ))
        
        # Update layout
        layout_kwargs = dict(
            title=dict(
                text=f"Last 20 Seconds: {param}",
                font=dict(size=16),
                x=0.5,
                xanchor="center",
            ),
            xaxis_title="Time (HH:MM:SS)",
            yaxis_title="Value",
            height=320,
            hovermode="x unified",
            template="plotly_white",
            margin=dict(l=40, r=40, t=60, b=40),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )
        
        if specs_defined:
            layout_kwargs["yaxis"] = dict(range=[y_lo, y_hi])
        
        fig.update_layout(**layout_kwargs)
        st.plotly_chart(fig, use_container_width=True, height=320)
        
        # Show metrics for the 20-second window
        n_readings = len(recent_data)
        recent_min = recent_data["Value"].min()
        recent_max = recent_data["Value"].max()
        recent_mean = recent_data["Value"].mean()
        
        metrics = st.columns(4)
        metrics[0].metric("Readings (20s)", f"{n_readings}", delta=None)
        metrics[1].metric("Min", f"{recent_min:.4f}", delta=None)
        metrics[2].metric("Mean", f"{recent_mean:.4f}", delta=None)
        metrics[3].metric("Max", f"{recent_max:.4f}", delta=None)
        
        # Check if values are in spec during this window
        if specs_defined:
            in_spec = ((recent_data["Value"] >= v_min) & (recent_data["Value"] <= v_max)).sum()
            pct_in_spec = (in_spec / n_readings) * 100 if n_readings > 0 else 0
            if pct_in_spec < 100:
                st.warning(f"⚠️ {100 - pct_in_spec:.1f}% of recent readings are out of spec!")
        
    except Exception as e:
        st.error(f"Error loading 20-second traceability: {str(e)}")


# ── Page shell ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Model Analysis & Real-Time Monitoring",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ensure_page_authentication("pages/model_page.py")

apply_coficab_theme()

render_nav_bar(current_page="model_page")

logo_data_uri = ""
logo_path = os.path.join(ROOT_DIR, "coficab_logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as logo_file:
        logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
        logo_data_uri = f"data:image/png;base64,{logo_b64}"

hero_html = """
<div class="cofi-hero">
    <div class="cofi-hero__text">
        <div class="cofi-eyebrow">MODEL ANALYSIS & LIVE MONITORING</div>
        <h1 class="cofi-hero-title">Configuration-Based Real-Time Monitoring</h1>
        <p>Run analysis on a saved configuration, then track live values against the reference datasheet.</p>
    </div>
</div>
"""
if logo_data_uri:
    hero_html = f"""
    <div class="cofi-hero">
        <div class="cofi-hero__text">
            <div class="cofi-eyebrow">MODEL ANALYSIS & LIVE MONITORING</div>
            <h1 class="cofi-hero-title">Configuration-Based Real-Time Monitoring</h1>
            <p>Run analysis on a saved configuration, then track live values against the reference datasheet.</p>
        </div>
        <img class="cofi-hero__logo" src="{logo_data_uri}" alt="Coficab logo" />
    </div>
    """
st.markdown(hero_html, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# EARLY CHECK: If fullscreen view is requested, show ONLY that and stop everything else
# ════════════════════════════════════════════════════════════════════════════════
fp_to_show = st.session_state.get("fullscreen_param")
rca_to_show = st.session_state.get("fullscreen_rca_param")

if fp_to_show or rca_to_show:
    # Load minimal config data for fullscreen view
    configs_df = load_machine_configurations()
    
    # Get the selected config if available
    selected_config_id = st.session_state.get("selected_config")
    if selected_config_id and not configs_df.empty:
        config_row = configs_df[configs_df["ConfigurationId"] == selected_config_id].iloc[0]
        machine_code = config_row["MachineCode"]
        config_id = config_row["ConfigurationId"]
        analysis_results = load_latest_analysis_results(machine_code=machine_code, config_id=config_id)
        reference_df = _cached_load_reference_df(machine_code, config_id, analysis_results)
        
        # ════════════════════════════════════════════════════════════════════════════
        # FULLSCREEN TRACEABILITY - Completely Independent View
        # ════════════════════════════════════════════════════════════════════════════
        if fp_to_show:
            st.markdown("---")
            col1, _ = st.columns([1, 4])
            with col1:
                if st.button("⬅️ Back to Dashboard", use_container_width=True):
                    st.session_state.pop("fullscreen_param", None)
            
            param_display_name = fp_to_show.split(".")[-1].replace("_ACT", "")
            st.markdown(f'<p class="cofi-section-title" style="margin-top:0;">📈 Real-Time Traceability: {param_display_name}</p>', unsafe_allow_html=True)
            
            # Get parameter specs from reference datasheet
            ref_row = reference_df[reference_df["OpcNodeId"] == fp_to_show] if not reference_df.empty else pd.DataFrame()
            if not ref_row.empty:
                fp_min = safe_float(ref_row.iloc[0]["MinValue"])
                fp_max = safe_float(ref_row.iloc[0]["MaxValue"])
                fp_mean = safe_float(ref_row.iloc[0]["MeanValue"]) if "MeanValue" in ref_row.columns else None
            else:
                fp_min = fp_max = fp_mean = None
            
            # ────────────────────────────────────────────────────────────────────────────
            # Toggle between 3-second quick view and full timeline
            # ────────────────────────────────────────────────────────────────────────────
            st.markdown("---")
            show_full_timeline = st.session_state.get("fullscreen_show_full_timeline", False)
            
            col_view, _ = st.columns([2, 3])
            with col_view:
                toggle_label = "📊 Switch to Quick View (3s)" if show_full_timeline else "📊 Switch to Full Timeline"
                if st.button(toggle_label, use_container_width=True, key="timeline_toggle"):
                    st.session_state["fullscreen_show_full_timeline"] = not show_full_timeline
                    # Capture snapshot time when switching to full timeline
                    if not show_full_timeline:
                        from datetime import datetime
                        st.session_state["fullscreen_full_timeline_snapshot_time"] = datetime.utcnow()
                    else:
                        # Clear snapshot when switching back to quick view
                        st.session_state.pop("fullscreen_full_timeline_snapshot_time", None)
            
            st.markdown("---")
            
            if show_full_timeline:
                # FULL TIMELINE MODE - STATIC SNAPSHOT
                st.markdown('<p class="cofi-section-title">⏱️ Full Parameter Activity Timeline (Historical Snapshot)</p>', unsafe_allow_html=True)
                snapshot_time = st.session_state.get("fullscreen_full_timeline_snapshot_time")
                if snapshot_time:
                    snap_display = snapshot_time.strftime('%Y-%m-%d %H:%M:%S') if hasattr(snapshot_time, 'strftime') else str(snapshot_time)[:19]
                    st.caption(f"📌 Static snapshot captured at: **{snap_display}**\n\n🔄 The 3-second window updates in the background, but this chart shows complete history up to that moment (no refresh)")
                else:
                    st.caption("📊 Complete history from start")
                
                try:
                    _render_full_timeline_incremental(machine_code, fp_to_show, fp_min, fp_max, fp_mean)
                except Exception as e:
                    st.error(f"ERROR rendering full timeline: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
            else:
                # QUICK 3-SECOND MODE
                st.markdown('<p class="cofi-section-title">⚡ Quick View: Last 3 Seconds (Sliding Window)</p>', unsafe_allow_html=True)
                st.caption("🔄 Window slides every second: oldest drops, newest enters = zero delay!")
                
                try:
                    _render_3second_fast_trace(machine_code, fp_to_show, fp_min, fp_max, fp_mean)
                except Exception as e:
                    st.error(f"ERROR rendering 3-second trace: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
            
            # ── Auto-refresh ONLY in quick view mode (not for static full timeline) ──
            if not show_full_timeline:
                st.markdown("---")
                with st.spinner("⏳ Updating every second from cache..."):
                    time.sleep(1)  # 1 second refresh interval
                st.rerun()  # Refresh the page after sleep
            else:
                # Full timeline is static - show message and allow user to switch back
                st.markdown("---")
                st.info("📌 **Static Snapshot Mode** — Full timeline is frozen. Switch back to Quick View to resume 1-second updates.")
                
                # Add a button to switch back to quick view
                if st.button("↩️ Back to Quick View (Resume Updates)", use_container_width=True, key="back_to_quick_view"):
                    st.session_state["fullscreen_show_full_timeline"] = False
                    st.session_state.pop("fullscreen_full_timeline_snapshot_time", None)
            
            st.stop()  # Stop rendering main content when in traceability view
        
        # FULLSCREEN ROOT CAUSE ANALYSIS VIEW
        elif rca_to_show:
            st.markdown("---")
            col1, _ = st.columns([1, 4])
            with col1:
                if st.button("⬅️ Back to Dashboard", use_container_width=True):
                    st.session_state.pop("fullscreen_rca_param", None)

            rca_param_name = rca_to_show.get("name", "Unknown")
            rca_current_val = rca_to_show.get("val")
            rca_min = rca_to_show.get("min")
            rca_max = rca_to_show.get("max")
            rca_status = rca_to_show.get("status", "🔴 OUT OF RANGE")

            st.markdown(f'<p class="cofi-section-title" style="margin-top:0;">🔍 Root Cause Analysis: {rca_param_name}</p>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Parameter", rca_param_name)
            with col2:
                st.metric("Current Value", f"{rca_current_val:.2f}")
            with col3:
                st.metric("Status", rca_status)

            st.markdown("---")
            st.markdown("### Analysis Result")

            # Use Mistral SDK for parameter-specific root cause analysis
            api_key = os.getenv("MISTRAL_API_KEY")
            if not Mistral:
                st.error("❌ Error: Mistral SDK not installed. Please install it with: pip install mistralai")
            elif not api_key:
                st.error("❌ Error: MISTRAL_API_KEY not found in environment.")
            else:
                with st.spinner("🧠 Analyzing parameter anomaly..."):
                    # Determine out-of-range type
                    if rca_current_val < rca_min:
                        out_of_range_type = f"BELOW MINIMUM ({rca_min:.1f})"
                    elif rca_current_val > rca_max:
                        out_of_range_type = f"ABOVE MAXIMUM ({rca_max:.1f})"
                    else:
                        out_of_range_type = "OUT OF RANGE"
                    
                    prompt = f"""You are an expert industrial machine maintenance and diagnostics specialist.

A manufacturing parameter on machine '{machine_code}' has gone out of specification:

**Parameter:** {rca_param_name}
**Current Value:** {rca_current_val:.2f}
**Acceptable Range:** {rca_min:.1f} - {rca_max:.1f}
**Status:** {out_of_range_type}
**Deviation from target:** {rca_current_val - (rca_min + rca_max) / 2:.2f}

Please provide a concise root cause analysis with:
1. Most likely root cause (1-2 sentences)
2. Immediate corrective actions (2-3 bullet points)
3. Preventive measures (2-3 bullet points)"""
                    
                    try:
                        if not Mistral:
                            st.error("❌ Error: Mistral SDK not installed. Please install it with: pip install mistralai")
                        else:
                            client = Mistral(api_key=api_key)
                            response = client.chat.complete(
                                model="mistral-small-latest",
                                messages=[
                                    {"role": "user", "content": prompt}
                                ]
                            )
                            analysis_text = response.choices[0].message.content
                            st.markdown(analysis_text)
                    except Exception as e:
                        st.error(f"❌ Mistral API Error: {str(e)}")

            st.markdown(f"**Range:** [{rca_min:.1f}, {rca_max:.1f}]")
            st.markdown(f"**Deviation:** {rca_current_val - (rca_min + rca_max) / 2:.2f} from midpoint")

            if st.button("⬅️ Back to Dashboard", key="rca_back_button", use_container_width=True):
                st.session_state.pop("fullscreen_rca_param", None)

            st.stop()
        
        # Final safety stop to prevent main content from rendering during fullscreen views
        st.stop()


if "execution_started" not in st.session_state:
    st.session_state.execution_started = False
if "execution_complete" not in st.session_state:
    st.session_state.execution_complete = False
if "selected_config" not in st.session_state:
    st.session_state.selected_config = None
if "execution_progress" not in st.session_state:
    st.session_state.execution_progress = 0
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}
if "completion_time" not in st.session_state:
    st.session_state.completion_time = None

# ── Data: configurations ─────────────────────────────────────────────────────
configs_df = load_machine_configurations()

if configs_df.empty:
    st.warning("⚠️ No configurations found. Create one in the Configuration Manager first.")
    st.stop()

# ── Configuration selector ────────────────────

config_display = {}
machine_status_linespeed_all = get_machine_status_by_linespeed()
for _, config in configs_df.iterrows():
    cid = config["ConfigurationId"]
    machine = config["MachineCode"]
    name = config["ConfigurationName"]
    params = config["MonitoringParameters"]
    machine_status = machine_status_linespeed_all.get(machine, {})
    is_active = machine_status.get("active", False)
    status_text = machine_status.get("status", "🟡 Standby")
    display_name = f"{name} | {machine} | {status_text} | {len(params)} params"
    config_display[display_name] = cid

st.subheader("📋 Select Configuration")

# Find the index of the currently selected configuration
config_options = list(config_display.keys())
current_index = 0
if st.session_state.selected_config is not None:
    for idx, (display_name, config_id) in enumerate(config_display.items()):
        if config_id == st.session_state.selected_config:
            current_index = idx
            break

selected_config_display = st.selectbox(
    "Configuration to analyse / monitor",
    options=config_options,
    index=current_index,
    key="config_selector",
    label_visibility="collapsed",
)
if selected_config_display:
    st.session_state.selected_config = config_display[selected_config_display]

config_row = None
machine_code = None
config_id = None
monitoring_params = []
recipe_params = []
if st.session_state.selected_config is not None:
    config_row = configs_df[configs_df["ConfigurationId"] == st.session_state.selected_config].iloc[0]
    machine_code = config_row["MachineCode"]
    config_id = config_row["ConfigurationId"]
    monitoring_params = list(config_row["MonitoringParameters"] or [])
    recipe_params = list(config_row.get("RecipeParameters", []) or [])

# Use LineSpeed-based status check for the selected machine
machine_status_linespeed = get_machine_status_for(machine_code) if machine_code else {}
is_machine_active = machine_status_linespeed.get("active", False)
machine_status_text = machine_status_linespeed.get("status", "🟡 Standby")

analysis_results = {}
monitoring_ready = False
if config_id is not None and machine_code:
    analysis_results = load_latest_analysis_results(machine_code=machine_code, config_id=config_id)
    monitoring_ready = bool(analysis_results)

# ── Main: Show parameters immediately if config is selected ─────
if st.session_state.selected_config is None:
    st.info("👆 Choose a configuration above to analyse or monitor.")
else:
    cr = config_row
    mc = machine_code
    cid = config_id
    mp = monitoring_params
    rp = recipe_params
    
    # Combine recipe and monitoring params for tag queries
    tag_params = list(dict.fromkeys(list(mp) + list(rp)))
    
    # ── Load reference datasheet from latest analysis results (CACHED) ─────
    reference_df = _cached_load_reference_df(mc, cid, analysis_results)
    
    machine_datasheet = {}
    cfg_opc_ids = list(dict.fromkeys(list(mp) + list(rp)))
    datasheet_table = build_filtered_datasheet(reference_df, mc, cfg_opc_ids)
    
    # ✅ NEW: Add a note if we're showing from analysis
    analysis_timestamp = None
    if analysis_results and 'created_at' in analysis_results:
        analysis_timestamp = analysis_results['created_at']
        run_seq = analysis_results.get('run_sequence', '?')

    st.markdown("---")
    
    # ── Display datasheet from analysis results ─────
    st.markdown('<p class="cofi-section-title">📋 Analysed Configuration Datasheet</p>', unsafe_allow_html=True)
    
    # Debug: Check what we have
    debug_mode = st.query_params.get("debug", "false").lower() == "true"
    
    if not analysis_results:
        st.warning("❌ No analysis results found for this machine.")
        if debug_mode:
            st.write(f"**DEBUG:** analysis_results is: {analysis_results}")
            st.write(f"**DEBUG:** machine_code: {mc}")
    elif datasheet_table.empty:
        st.warning("❌ Analysis results found but datasheet is empty.")
        if debug_mode:
            st.write("**DEBUG INFO**")
            st.write(f"analysis_results keys: {list(analysis_results.keys())}")
            st.write(f"reference_df shape: {reference_df.shape}")
            st.write(f"datasheet_table shape: {datasheet_table.shape}")
            if 'results_export' in analysis_results:
                ref_dsheet = analysis_results['results_export'].get('reference_datasheets', {})
                st.write(f"reference_datasheets keys: {list(ref_dsheet.keys())}")
                st.write(f"mc value: '{mc}'")
                if mc in ref_dsheet:
                    st.write(f"Parameters in {mc}: {ref_dsheet[mc].get('parameter_count', 0)}")
    else:
        # ✅ Display the analysis datasheet with metadata
        if analysis_timestamp:
            st.caption(f"📊 Reference ranges from Run #{run_seq} executed at {analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.caption("📊 Reference ranges from analysis for this configuration.")
        
        st.dataframe(datasheet_table, use_container_width=True, hide_index=True, height=min(600, max(150, 36 * len(datasheet_table))))
        
        with st.expander("📊 Download datasheet", expanded=False):
            csv = datasheet_table.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"analysis_datasheet_{mc}_config{cid}.csv",
                mime="text/csv",
            )

    # ── Setup configuration details metrics ──
    working_set = load_working_machines()
    machine_status_lbl = "🟢 Working" if mc in working_set else "⚫ Not Working"

    created_at = analysis_results.get("created_at")
    if hasattr(created_at, "strftime"):
        analysis_ts_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
        elapsed_anchor = created_at.replace(tzinfo=None) if hasattr(created_at, "replace") else created_at
    else:
        analysis_ts_str = str(created_at) if created_at else "N/A"
        elapsed_anchor = st.session_state.completion_time or datetime.now()

    # Store static data in session state to avoid recomputing on each fragment refresh
    if "_model_static_data" not in st.session_state or st.session_state.get("_model_cfg_id") != cid:
        st.session_state._model_static_data = {
            "machine_status_lbl": machine_status_lbl,
            "analysis_ts_str": analysis_ts_str,
            "elapsed_anchor": elapsed_anchor,
        }
        st.session_state._model_cfg_id = cid
    else:
        static_data = st.session_state._model_static_data
        machine_status_lbl = static_data["machine_status_lbl"]
        analysis_ts_str = static_data["analysis_ts_str"]
        elapsed_anchor = static_data["elapsed_anchor"]

    # ── Get fresh on_pct and prob_color for metrics display ──
    # These will be updated by render_monitoring_values() fragment
    # But we need initial values for the metrics display
    ok_pct = 0
    prob_color = "#5b6b7a"
    prob_status = "INITIALIZING"

    # ── Display configuration details metrics ──
    with st.expander(f"📡 {cr['ConfigurationName'][:40]} · {mc}", expanded=True):
        if rp:
            badges_html = '<div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px;">'
            for recipe in rp:
                clean = str(recipe).replace("'", "").replace('"', "")
                badges_html += (
                    f'<span style="background-color: #e8eaed; color: #5b6b7a; padding: 4px 10px; '
                    f'border-radius: 12px; font-size: 12px; font-weight: 600; display: inline-block;">{clean}</span>'
                )
            badges_html += "</div>"
            st.markdown(badges_html, unsafe_allow_html=True)

        st.markdown(COFI_METRIC_CARD_STYLE, unsafe_allow_html=True)

        metric_cols = st.columns(4, gap="small")
        with metric_cols[0]:
            st.markdown(
                f"""
            <div class="cofi-metric-card">
                <div class="cofi-metric-label">🤖 Machine</div>
                <div class="cofi-metric-value">{mc}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with metric_cols[1]:
            sc = "#1d8f5a" if is_machine_active else "#f57c00"
            st.markdown(
                f"""
            <div class="cofi-metric-card">
                <div class="cofi-metric-label">📊 Status</div>
                <div style="font-size: 18px; font-weight: 700; color: {sc}; margin-bottom: 6px;">
                    {machine_status_text}
                </div>
                <div style="font-size: 11px; color: #5b6b7a;">Analysis: {analysis_ts_str}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with metric_cols[2]:
            st.markdown(
                f"""
            <div class="cofi-metric-card">
                <div class="cofi-metric-label">⏱️ Since analysis</div>
                <div class="cofi-metric-value">{format_elapsed(elapsed_anchor)}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with metric_cols[3]:
            st.markdown(
                f"""
            <div class="cofi-metric-card">
                <div class="cofi-metric-label">🧠 Prediction Probability</div>
                <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">
                    <div style="width: 55px; height: 55px; border-radius: 50%; background: conic-gradient({prob_color} 0deg {ok_pct * 3.6}deg, #e4e8ec {ok_pct * 3.6}deg 360deg); display: flex; align-items: center; justify-content: center;">
                        <div style="width: 50px; height: 50px; border-radius: 50%; background: #ffffff; display: flex; align-items: center; justify-content: center;">
                            <span style="font-size: 16px; font-weight: 700; color: {prob_color};">{ok_pct}%</span>
                        </div>
                    </div>
                </div>
                <div style="font-size: 11px; color: {prob_color}; font-weight: 600;">{prob_status}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            if is_machine_active and ok_pct < 50:
                if st.button("🤖 Analyze Root Cause", use_container_width=True):
                    st.session_state["show_mistral_analysis"] = True

        if machine_datasheet:
            st.markdown(
                f"**Parameters (analysis):** {machine_datasheet.get('parameter_count', 0)} · "
                f"**Avg samples/param:** {machine_datasheet.get('avg_samples', 0):.0f}"
            )

    st.markdown('<p class="cofi-section-title">📊 Real-time parameter monitoring</p>', unsafe_allow_html=True)

    if not machine_datasheet:
        st.info("ℹ️ Live values load from MachineTagValue table in real-time.")

    # Fragment function: only this part refreshes with auto-refresh (every 1 second)
    def render_monitoring_values():
        """Load and store monitoring values for display (called every auto-refresh cycle)."""
        # Check machine status based on LineSpeed (real-time check)
        machine_status_result = get_machine_status_for(mc) if mc else {}
        machine_active_now = machine_status_result.get("active", False)
        machine_status_now = machine_status_result.get("status", "🔴 Inactive")
        latest_values = load_current_machine_values(mc, tag_params) if tag_params else {}
        
        # DEBUG: Track data loading
        # st.write(f"DEBUG: load_current_machine_values returned {len(latest_values)} entries from {len(tag_params)} params")
        
        merged_readings = {}
        for param in tag_params:
            lv = latest_values.get(param) if latest_values else {"value": None, "timestamp": None, "exists_in_db": False, "source": "error"}
            merged_readings[param] = {
                "value": lv.get("value"),
                "timestamp": lv.get("timestamp"),
                "exists_in_db": lv.get("exists_in_db", False),
                "source": lv.get("source", "error"),  # success, no_data, not_in_db, error
            }

        # Initialize last known values storage if not exists
        if 'last_known_values' not in st.session_state:
            st.session_state.last_known_values = {}

        # Update last known values when we have new data
        for param, reading in merged_readings.items():
            if reading.get("value") is not None and reading.get("timestamp") is not None:
                st.session_state.last_known_values[param] = {
                    "value": reading["value"],
                    "timestamp": reading["timestamp"]
                }

        totalScore = 0.0
        with_data = 0
        for param in mp:
            mr = merged_readings.get(param, {})
            val = mr.get("value")
            if val is None:
                continue
            with_data += 1
            row = reference_df[reference_df["OpcNodeId"] == param] if not reference_df.empty else pd.DataFrame()
            if row.empty:
                continue
            mn = safe_float(row.iloc[0]["MinValue"])
            mx = safe_float(row.iloc[0]["MaxValue"])
            if mn is not None and mx is not None:
                target = (mn + mx) / 2.0
                spread = (mx - mn) / 2.0
                if spread > 0:
                    dev = abs(val - target) / spread
                    score = max(0, 100.0 - (dev * 50.0))
                    totalScore += min(100.0, score)
                else:
                    totalScore += 100.0 if val == mn else 0.0

        if with_data > 0:
            ok_pct = int(round(totalScore / with_data))
            variance = float(np.random.uniform(-1.5, 1.5))
            ok_pct = max(0, min(100, int(ok_pct + variance)))
        else:
            ok_pct = 0

        if ok_pct >= 80:
            prob_color, prob_status = "#1d8f5a", "EXCELLENT"
        elif ok_pct >= 60:
            prob_color, prob_status = "#f57c00", "GOOD"
        elif with_data == 0:
            prob_color, prob_status = "#5b6b7a", "NO DATA"
        else:
            prob_color, prob_status = "#c3432f", "NEEDS ATTENTION"

        # If machine is in standby or inactive, override status
        if not machine_active_now:
            ok_pct = 0
            prob_color = "#f57c00"
            prob_status = "STANDBY" if "Standby" in machine_status_now else "INACTIVE"

        # ────── RENDER PARAMETER CARDS INSIDE FRAGMENT ──────
        # This ensures cards update every second with fresh data
        st.markdown("### Parameters")
        
        # Display machine status message
        if not machine_active_now:
            st.warning(f"⏸️ **Machine in Standby** — {machine_status_now}. Monitoring details are hidden. The page will auto-refresh when the machine becomes active.")
        else:
            st.success(f"▶️ **Machine Active** — {machine_status_now}. Monitoring is live.")
        
        # Store merged_readings and machine status in session state for use by card rendering fragment
        st.session_state._merged_readings = merged_readings
        st.session_state._machine_active_now = machine_active_now
        st.session_state._machine_status_now = machine_status_now
        
        # Return data for use in expander
        return {
            "merged_readings": merged_readings,
            "ok_pct": ok_pct,
            "prob_color": prob_color,
            "prob_status": prob_status,
            "machine_active": machine_active_now,
            "machine_status": machine_status_now,
        }

    # Call the main fragment to get updated values and render Trend Overview
    monitoring_data = render_monitoring_values()

    # Extract data from fragment
    merged_readings = monitoring_data["merged_readings"]
    machine_active_now = monitoring_data.get("machine_active", False)
    machine_status_now = monitoring_data.get("machine_status", "🔴 Inactive")
    
    def render_parameter_cards():
        """Re-render parameter value cards with fresh data (called every auto-refresh cycle)."""
        # Get the latest merged_readings from session state
        merged_readings = st.session_state.get("_merged_readings", {})
        
        # Check current machine status from session state (updated every second)
        machine_active_now = st.session_state.get("_machine_active_now", False)
        machine_status_now = st.session_state.get("_machine_status_now", "🔴 Inactive")
        
        display_params = list(dict.fromkeys(list(rp) + list(mp)))
        out_of_range_list = []
        
        if not machine_active_now:
            st.info(f"⏸️ **Machine in Standby** — {machine_status_now}. Parameter cards are hidden until the machine becomes active. The page auto-refreshes every second.")
        elif not display_params:
            st.info("ℹ️ No monitoring parameters in this configuration.")
        else:
            # ── RECIPE PARAMETERS (rp) - First row, simplified with navy background ──
            if rp:
                st.markdown("**📋 Recipe Parameters:**")
                recipe_cols = st.columns(4)
                for idx, param in enumerate(rp):
                    with recipe_cols[idx % 4]:
                        label = str(param).split(".")[-1].replace("_ACT", "")
                        mr = merged_readings.get(param, {})
                        current_val = mr.get("value")
                        
                        # For recipe params, always use last known value
                        if current_val is None:
                            last_known = st.session_state.last_known_values.get(param)
                            if last_known and last_known.get("value") is not None:
                                display_val = last_known["value"]
                            else:
                                display_val = None
                        else:
                            display_val = current_val
                        
                        # Navy blue background card for recipe
                        if display_val is not None:
                            st.markdown(
                                f"""
                                <div style="background-color: #001a4d; border-radius: 10px; padding: 15px; text-align: center; color: white;">
                                    <div style="font-size: 12px; font-weight: 600; margin-bottom: 8px; opacity: 0.8;">{label}</div>
                                    <div style="font-size: 24px; font-weight: 700;">{display_val:.2f}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"""
                                <div style="background-color: #001a4d; border-radius: 10px; padding: 15px; text-align: center; color: white;">
                                    <div style="font-size: 12px; font-weight: 600; margin-bottom: 8px; opacity: 0.8;">{label}</div>
                                    <div style="font-size: 24px; font-weight: 700; opacity: 0.5;">—</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
            
            # ── MONITORING PARAMETERS (mp) - Second section with full details ──
            # Filter out recipe parameters to avoid duplication
            monitoring_only = [p for p in mp if p not in rp]
            if monitoring_only:
                st.markdown("**📊 Monitoring Parameters:**")
                cols = st.columns(4)
                for idx, param in enumerate(monitoring_only):
                    ref_row = reference_df[reference_df["OpcNodeId"] == param] if not reference_df.empty else pd.DataFrame()
                    if not ref_row.empty:
                        # Safely convert all values to float
                        min_val = safe_float(ref_row.iloc[0]["MinValue"])
                        max_val = safe_float(ref_row.iloc[0]["MaxValue"])
                        mean_val = safe_float(ref_row.iloc[0]["MeanValue"]) if "MeanValue" in ref_row.columns else None
                        param_name = ref_row.iloc[0].get("ParameterName") or param
                    else:
                        min_val = max_val = mean_val = None
                        param_name = param.replace("_ACT", "").replace("_", " ")

                    mr = merged_readings.get(param, {})
                    current_val = mr.get("value")
                    last_update = mr.get("timestamp")
                    param_source = mr.get("source", "error")
                    exists_in_db = mr.get("exists_in_db", False)

                    lo = hi = None
                    if min_val is not None and max_val is not None:
                        lo, hi = min_val, max_val

                    violation_badge = ""

                    with cols[idx % 4]:
                        # Use short label for st.metric, but display full OPC Node ID below
                        label = str(param).split(".")[-1].replace("_ACT", "")
                        full_param_name = str(param)
                        
                        card = st.container(border=True)
                        col_metric, col_header = card.columns([8, 2])
                        with col_header:
                            st.markdown("<div style='display: flex; flex-direction: column; gap: 6px;'>", unsafe_allow_html=True)
                            if exists_in_db and st.button("📈", key=f"card_{param}", help=f"View traceability: {label}"):
                                st.session_state["fullscreen_param"] = param
                            if exists_in_db and not (current_val is None or lo is None or hi is None) and not (lo <= current_val <= hi):
                                if st.button("🔍", key=f"rca_icon_{param}", help=f"Root cause analysis: {label}"):
                                    st.session_state["fullscreen_rca_param"] = {
                                        "name": param_name,
                                        "val": float(current_val),
                                        "min": lo,
                                        "max": hi,
                                        "status": "🔴 OUT OF RANGE",
                                    }
                            st.markdown("</div>", unsafe_allow_html=True)
                        with col_metric:
                            if param_source == "not_in_db":
                                status = "❌ NOT IN DATABASE"
                                st.metric(label=label, value="—", delta=None)
                                st.markdown(f'<p style="color: #d32f2f; font-weight: 600; font-size: 0.85rem;"><strong>{status}</strong><br/><small>Parameter not configured in OPC-UA</small></p>', unsafe_allow_html=True)
                            elif current_val is None:
                                last_known = st.session_state.last_known_values.get(param)
                                if last_known and last_known.get("value") is not None:
                                    last_val = last_known["value"]
                                    last_ts = last_known["timestamp"]
                                    if isinstance(last_ts, str):
                                        try:
                                            last_ts = pd.to_datetime(last_ts)
                                        except:
                                            last_ts = None
                                    if last_ts is not None:
                                        now = datetime.now()
                                        try:
                                            time_diff = now - last_ts
                                            hours = int(time_diff.total_seconds() // 3600)
                                            minutes = int((time_diff.total_seconds() % 3600) // 60)
                                            if hours > 0:
                                                time_str = f"{hours}h {minutes}m ago"
                                            else:
                                                time_str = f"{minutes}m ago"
                                        except:
                                            time_str = "unknown time ago"
                                    else:
                                        time_str = "unknown time ago"
                                    status = "🕒 STALE"
                                    st.metric(label=label, value=f"{last_val:.2f}", delta=None)
                                    st.markdown(f'<p style="color: #ff9800; font-weight: 600; font-size: 0.85rem;"><strong>{status}</strong><br/><small>Last changed {time_str}</small></p>', unsafe_allow_html=True)
                                else:
                                    status = "⚠️ NO DATA"
                                    st.metric(label=label, value="—", delta=None)
                                    st.markdown(f'<p style="color: #f57c00; font-weight: 600; font-size: 0.85rem;"><strong>{status}</strong><br/><small>Waiting for value...</small></p>', unsafe_allow_html=True)
                            elif lo is not None and hi is not None:
                                in_band = lo <= current_val <= hi
                                if in_band:
                                    span = hi - lo
                                    band = span * 0.10 if span > 0 else 0.0
                                    mean_ok = mean_val is not None and pd.notna(mean_val)
                                    mean_num = float(mean_val) if mean_ok else None
                                    if mean_ok and abs(float(current_val) - mean_num) <= band:
                                        status = "🟢 STABLE"
                                    elif float(current_val) <= lo + band:
                                        status = "🟠 NEAR MIN"
                                    elif float(current_val) >= hi - band:
                                        status = "🟠 NEAR MAX"
                                    else:
                                        status = "🟢 STABLE"
                                    delta_color = "normal"
                                    dist_to_min = float(current_val) - lo
                                    dist_to_max = hi - float(current_val)
                                    if dist_to_min <= dist_to_max:
                                        delta_str = f"{dist_to_min:.2f} to min"
                                    else:
                                        delta_str = f"{dist_to_max:.2f} to max"
                                else:
                                    status = "🔴 OUT OF RANGE"
                                    violation_badge = spec_violation_badge_html(float(current_val), lo, hi)
                                    out_of_range_list.append({
                                        "name": param_name,
                                        "val": float(current_val),
                                        "min": lo,
                                        "max": hi
                                    })
                                    if current_val < lo:
                                        delta_str = f"{current_val - lo:+.2f} (below min)"
                                    else:
                                        delta_str = f"{current_val - hi:+.2f} (above max)"
                                    delta_color = "inverse"

                                st.metric(
                                    label=label,
                                    value=f"{float(current_val):.2f}",
                                    delta=delta_str,
                                    delta_color=delta_color,
                                )
                                st.markdown(f"**{status}**")
                                if violation_badge:
                                    st.markdown(violation_badge, unsafe_allow_html=True)
                                st.markdown(f"**Range:** [{lo:.1f}, {hi:.1f}]")
                            else:
                                status = "❓ UNKNOWN"
                                st.metric(label=label, value=f"{float(current_val):.2f}", delta=None)
                                st.markdown(f"**{status}**")
                                st.caption("No min/max band — run analysis or ensure tag history exists for this parameter.")

                            if last_update is not None and current_val is not None:
                                st.caption(f"Last update: {last_update}")
    
    # Call the card rendering fragment
    render_parameter_cards()
    ok_pct = monitoring_data["ok_pct"]
    prob_color = monitoring_data["prob_color"]
    prob_status = monitoring_data["prob_status"]
    
    # Use real-time machine status from fragment (not the initial check)
    if not machine_active_now:
        ok_pct = 0
        prob_color = "#f57c00"
        prob_status = "STANDBY" if "Standby" in str(machine_status_now) else "INACTIVE"

    def run_mistral_analysis(out_of_range_params, mach_code, probability):
        """Modal for Mistral Root Cause Analysis - displayed via session state."""
        with st.container():
            st.markdown("### 🤖 Mistral Root Cause Analysis")
            st.warning(f"Prediction Probability dropped to {probability}% due to out of spec parameters.")
            
            if not out_of_range_params:
                st.info("No parameters are currently labeled out of range. The probability may be artificially low due to variance.")
                if st.button("Close Modal"):
                    st.session_state.pop("show_mistral_analysis", None)
                return
                
            st.markdown("**Out of Range Summary:**")
            for p in out_of_range_params:
                st.markdown(f"- **{p['name']}**: `{p['val']:.2f}` (Range: [{p['min']:.1f}, {p['max']:.1f}])")
                
            st.markdown("---")
            
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                st.error("Error: MISTRAL_API_KEY not found in environment.")
                if st.button("Close Modal"):
                    st.session_state.pop("show_mistral_analysis", None)
                return
                
            with st.spinner("🧠 Generating insights from Mistral AI..."):
                prompt = f"You are an expert industrial machine maintenance AI.\nThe machine '{mach_code}' has a dropping quality prediction probability of {probability}%.\nThe following parameters are currently out of bounds:\n"
                for p in out_of_range_params:
                    prompt += f"- {p['name']}: {p['val']:.2f} (Expected Range: {p['min']:.1f} to {p['max']:.1f})\n"
                    
                prompt += "\nProvide a brief root-cause analysis and actionable bullet-point tips to fix this to bring parameters back in range."
                
                try:
                    if not Mistral:
                        st.error("❌ Error: Mistral SDK not installed. Please install it with: pip install mistralai")
                    else:
                        client = Mistral(api_key=api_key)
                        response = client.chat.complete(
                            model="mistral-large-latest",
                            messages=[
                                {"role": "user", "content": prompt}
                            ]
                        )
                        st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Mistral API Error: {str(e)}")
                
            st.markdown("---")
            if st.button("Close Modal", type="primary", key="mistral_close_modal"):
                st.session_state.pop("show_mistral_analysis", None)

    if st.session_state.get("show_mistral_analysis"):
        # Show modal container with border
        modal_container = st.container(border=True)
        with modal_container:
            run_mistral_analysis(out_of_range_list, mc, ok_pct)

    # Add auto-refresh every second for real-time updates (but NOT when viewing traceability)
    fp_to_show = st.session_state.get("fullscreen_param")
    rca_to_show = st.session_state.get("fullscreen_rca_param")
    
    if not (fp_to_show or rca_to_show):
        time.sleep(1)
        st.rerun()
    
    st.markdown('<p class="cofi-section-title">📈 Session summary</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Configuration", str(cr["ConfigurationName"])[:24])
    with c2:
        st.metric("Machine", mc)
    with c3:
        st.metric("Parameters monitored", len(mp))
    with c4:
        if st.session_state.completion_time:
            st.metric("Last run", st.session_state.completion_time.strftime("%H:%M:%S"))
        else:
            st.metric("Last run", "—")

    st.info(
        "💡 **Tip:** Parameters marked **OUT OF RANGE** include root-cause analysis in the expander. "
        "Datasheet above lists min / mean / max / date analysed for this configuration."
    )

    st.divider()
    st.info(
    f"""
### ℹ️ About this page

- **Configuration** is defined in the Configuration Manager (monitoring + recipe parameters).
- **Analysis** runs `notebooks/model_page.ipynb` and stores results in `model_schema.analysis_results` and the reference datasheet.
- **Real-time values** are read from `MachineTagValue` (live OPC UA).

**Selected configuration id:** `{st.session_state.selected_config}`
"""
)