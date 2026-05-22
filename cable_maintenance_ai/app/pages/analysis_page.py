"""
Recipe-Aware Datasheet Generator Page
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import base64
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from sqlalchemy import text


# ─────────────────────────────────────────────────────────────
# ROBUST PROJECT ROOT DETECTION
# ─────────────────────────────────────────────────────────────
def get_project_root() -> Path:
    """Find project root reliably whether running locally or in Docker."""
    current = Path(__file__).resolve()
    
    for _ in range(6):
        if (current / '.env').exists() or \
           (current / 'docker-compose.yml').exists() or \
           (current.name == 'cable_maintenance_ai'):
            return current
        current = current.parent
    
    return Path.cwd()


ROOT_DIR = get_project_root()
load_dotenv(ROOT_DIR / '.env')

# Fallback for old structure
try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    load_dotenv(os.path.join(BASE_DIR, '.env'))
except:
    pass

# Add root to path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from auth_helpers import ensure_page_authentication, render_nav_bar  # noqa: E402
from db_helpers import (
    load_all_machines,
    load_all_parameters_for_machine,
    get_last_10_runs_for_machine_with_recipe,
    filter_runs_by_available_data,
    get_engine,
    get_labeled_samples_from_runs,
    get_runs_in_time_window,
    calculate_recipe_parameter_statistics_from_samples,
    save_recipe_datasheet,
    load_recipe_datasheet,
    get_analysis_result_table_name,
    get_analysis_runs,
    load_analysis_results,
    enhance_parameter_reference_datasheet_table,
    get_datasheet_runs_for_machine,
    save_datasheet_run,
    load_datasheet_by_run_id,
)


def apply_coficab_theme():
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
        [data-testid="stHeader"] { 
            background: transparent;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
        }
        [data-testid="stToolbar"] { display: none !important; }
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
            padding: 8px 24px; margin: 0;
            background: linear-gradient(120deg, #0c1f31 0%, #133657 55%, #1f4a6f 100%);
            box-shadow: 0 14px 32px rgba(7, 18, 30, 0.2);
            position: fixed; top: 0; left: 0; right: 0; z-index: 1000; height: 56px; width: 100%;
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
        /* Ensure only one navbar is displayed (hide duplicates) */
        .cofi-nav:not(:first-of-type) { display: none !important; }
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
    page_title="Recipe Analysis & Datasheet Generator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ensure_page_authentication("pages/analysis_page.py")

apply_coficab_theme()

render_nav_bar(current_page="analysis_page")

logo_data_uri = ""
logo_path = os.path.join(ROOT_DIR, "coficab_logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as logo_file:
        logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
        logo_data_uri = f"data:image/png;base64,{logo_b64}"

hero_inner = """
    <div class="cofi-hero__text">
        <div class="cofi-eyebrow">RECIPE-AWARE ANALYSIS</div>
        <h1>Datasheet Generator</h1>
        <p>Select a machine, pick a recipe, choose a production run, then analyze all parameters with quality correlation.</p>
    </div>
"""

if logo_data_uri:
    hero_html = f'<div class="cofi-hero">{hero_inner}<img class="cofi-hero__logo" src="{logo_data_uri}" alt="Coficab logo" /></div>'
else:
    hero_html = f'<div class="cofi-hero">{hero_inner}</div>'

st.markdown(hero_html, unsafe_allow_html=True)

enhance_parameter_reference_datasheet_table()

# Initialize session state for flow preservation
if 'analysis_step' not in st.session_state:
    st.session_state.analysis_step = 1
if 'analysis_machine_selected' not in st.session_state:
    st.session_state.analysis_machine_selected = None
if 'analysis_monitoring_params_selected' not in st.session_state:
    st.session_state.analysis_monitoring_params_selected = None
if 'analysis_recipe_params_selected' not in st.session_state:
    st.session_state.analysis_recipe_params_selected = None
if 'analysis_machine_options' not in st.session_state:
    st.session_state.analysis_machine_options = []

# ── Step 1: Select Machine ───────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="cofi-section-title">Step 1: Select Machine</p>', unsafe_allow_html=True)

machines = load_all_machines()
if machines:
    st.session_state.analysis_machine_options = machines
else:
    machines = st.session_state.get("analysis_machine_options", [])

if not machines:
    st.error("No machines found in database.")
    st.stop()

selected_machine = st.selectbox(
    "Select a machine to analyze",
    options=machines,
    key="analysis_machine_selector",
    label_visibility="collapsed",
)

# Update session state when machine changes
if selected_machine != st.session_state.analysis_machine_selected:
    st.session_state.analysis_machine_selected = selected_machine
    st.session_state.analysis_step = 1
    st.session_state.analysis_recipe_params_selected = None
    # Clear downstream session state
    if "analysis_runs" in st.session_state:
        del st.session_state["analysis_runs"]
    if "analysis_sample_runs" in st.session_state:
        del st.session_state["analysis_sample_runs"]
    if "analysis_sample_run_ids" in st.session_state:
        del st.session_state["analysis_sample_run_ids"]
    if "analysis_run_sequence_selector" in st.session_state:
        del st.session_state["analysis_run_sequence_selector"]

# ── Previous Datasheet Runs ──────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="cofi-section-title">Previous Datasheet Runs</p>', unsafe_allow_html=True)

previous_runs = get_datasheet_runs_for_machine(selected_machine)
if not previous_runs.empty:
    st.caption(f"Browse and select from {len(previous_runs)} previous analysis run(s) for {selected_machine}")
    
    # Initialize session state for selected previous run
    if 'selected_previous_run_id' not in st.session_state:
        st.session_state.selected_previous_run_id = None
    if 'show_previous_datasheet' not in st.session_state:
        st.session_state.show_previous_datasheet = False
    
    # Create dropdown with formatted labels
    run_options = {}
    for idx, row in previous_runs.iterrows():
        run_timestamp = row['ExecutionTimestamp'].strftime("%Y-%m-%d %H:%M:%S") if pd.notna(row['ExecutionTimestamp']) else "Unknown"
        ok_pct = (row['OkCount'] / row['SampleCount'] * 100) if row['SampleCount'] > 0 else 0
        recipe_label = row['RecipeIdentifier'] if pd.notna(row['RecipeIdentifier']) else "N/A"
        label = f"Run #{int(row['DatasheetRunId'])} - {run_timestamp} - {recipe_label} ({int(row['SampleCount']):,} samples, {ok_pct:.1f}% OK)"
        run_options[int(row['DatasheetRunId'])] = {
            'label': label,
            'row': row
        }
    
    selected_run_id = st.selectbox(
        "Select a previous run to view",
        options=list(run_options.keys()),
        format_func=lambda x: run_options[x]['label'],
        key="previous_run_selector"
    )
    
    if selected_run_id:
        selected_run_row = run_options[selected_run_id]['row']
        
        # Display run metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Parameters", int(selected_run_row['ParameterCount']) if pd.notna(selected_run_row['ParameterCount']) else 0)
        with col2:
            st.metric("Total Samples", int(selected_run_row['SampleCount']) if pd.notna(selected_run_row['SampleCount']) else 0)
        with col3:
            st.metric("OK Samples", int(selected_run_row['OkCount']) if pd.notna(selected_run_row['OkCount']) else 0)
        with col4:
            ok_pct = (selected_run_row['OkCount'] / selected_run_row['SampleCount'] * 100) if selected_run_row['SampleCount'] > 0 else 0
            st.metric("OK %", f"{ok_pct:.1f}%")
        
        # Button to toggle datasheet visibility
        col_show, col_spacer = st.columns([1, 4])
        with col_show:
            if st.button(f"{'Hide' if st.session_state.show_previous_datasheet else 'Show'} Datasheet", use_container_width=True):
                st.session_state.show_previous_datasheet = not st.session_state.show_previous_datasheet
        
        # Display datasheet if toggled on
        if st.session_state.show_previous_datasheet:
            with st.expander("📊 Datasheet Details", expanded=True):
                datasheet_df = load_datasheet_by_run_id(selected_machine, selected_run_id)
                
                if not datasheet_df.empty:
                    # Select columns to display
                    display_cols = [col for col in [
                        'OpcNodeId',
                        'MinValue',
                        'OptimalValue',
                        'MaxValue',
                        'MeanValue',
                        'StdDev',
                        'SampleCount',
                        'QualityOkCount',
                        'QualityNotOkCount'
                    ] if col in datasheet_df.columns]
                    
                    # Format numeric columns
                    display_df = datasheet_df[display_cols].copy()
                    for col in ['MinValue', 'OptimalValue', 'MaxValue', 'MeanValue', 'StdDev']:
                        if col in display_df.columns:
                            display_df[col] = display_df[col].apply(lambda x: f"{float(x):.4f}" if pd.notna(x) else "—")
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        height=min(600, 36 * len(display_df) + 50)
                    )
                else:
                    st.warning("No datasheet parameters found for this run.")
else:
    st.info(f"No previous datasheet runs found for {selected_machine}. Generate your first datasheet to get started!")

# ── Step 2: Select Parameters to Analyse ────────────────────────────────────
st.markdown("---")
st.markdown('<p class="cofi-section-title">Step 2: Select Parameters to Analyse</p>', unsafe_allow_html=True)
st.caption("Pick the parameters to analyze and designate which are recipe parameters.")

all_parameters = load_all_parameters_for_machine(selected_machine)
if not all_parameters:
    st.warning(f"No parameters found for machine {selected_machine}.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Parameters to Analyse**")
    selected_monitoring_params = st.multiselect(
        "Select parameters to analyze:",
        options=all_parameters,
        format_func=lambda x: x.replace('_ACT', '').replace('_', ' '),
        key="analysis_monitoring_multiselect",
        help="These parameters will be collected and analyzed"
    )

with col2:
    st.markdown("**Recipe Parameters**  \n*(subset of monitoring params)*")
    selected_recipe_params = st.multiselect(
        "Select which parameters define the recipe:",
        options=selected_monitoring_params if selected_monitoring_params else all_parameters,
        format_func=lambda x: x.replace('_ACT', '').replace('_', ' '),
        key="analysis_recipe_multiselect",
        help="Parameters that define the recipe (used as recipe key)"
    )

if not selected_monitoring_params:
    st.info("Select at least one parameter to analyse to continue.")
    st.stop()

# Validate recipe params are a subset of monitoring params
invalid_recipes = [p for p in selected_recipe_params if p not in selected_monitoring_params]
if invalid_recipes:
    st.error("Recipe parameters must be a subset of monitoring parameters.")
    st.stop()

# Update session state when params change
if (selected_monitoring_params != st.session_state.analysis_monitoring_params_selected or
    selected_recipe_params != st.session_state.analysis_recipe_params_selected):
    st.session_state.analysis_monitoring_params_selected = selected_monitoring_params
    st.session_state.analysis_recipe_params_selected = selected_recipe_params
    st.session_state.analysis_step = 2
    # Clear downstream session state
    for key in ["analysis_runs", "analysis_sample_runs", "analysis_sample_run_ids", "analysis_run_sequence_selector"]:
        st.session_state.pop(key, None)

# ── Analysis Mode Selector ──────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="cofi-section-title">Analysis Mode</p>', unsafe_allow_html=True)

analysis_mode = st.radio(
    "Choose analysis mode",
    options=["Production Run-based", "Time Window-based"],
    key="analysis_mode",
    horizontal=True,
    label_visibility="collapsed",
)

if analysis_mode != st.session_state.get("analysis_prev_mode"):
    st.session_state["analysis_prev_mode"] = analysis_mode
    for key in ["analysis_runs", "analysis_sample_runs", "analysis_sample_run_ids", "analysis_run_sequence_selector"]:
        st.session_state.pop(key, None)

# ── Step 3: Data Source ─────────────────────────────────────────────

if analysis_mode == "Time Window-based":
    if "analysis_runs" not in st.session_state:
        st.markdown('<p class="cofi-section-title">Step 3: Select Time Window</p>', unsafe_allow_html=True)
        st.caption("Choose a time range with sensor data to analyze. No production run required.")

        try:
            with get_engine().connect() as c:
                bounds = pd.read_sql(
                    text("""
                        SELECT
                            MIN(SourceTimestamp) as oldest_data,
                            MAX(SourceTimestamp) as newest_data
                        FROM MachineTagValue WITH (NOLOCK)
                        WHERE MachineCode = :machine
                    """),
                    c,
                    params={"machine": selected_machine}
                )
                if not bounds.empty and not pd.isna(bounds['oldest_data'].iloc[0]):
                    db_start = pd.to_datetime(bounds['oldest_data'].iloc[0])
                    db_end = pd.to_datetime(bounds['newest_data'].iloc[0])
                    st.caption(f"Available sensor data range: {db_start} to {db_end}")
                else:
                    st.error("No sensor data found for this machine.")
                    st.stop()
        except Exception as e:
            st.error(f"Could not determine data range: {e}")
            st.stop()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Start**")
            start_date = st.date_input("Date", value=db_start.date(), key="tw_start_date", label_visibility="collapsed")
            start_time = st.time_input("Time", value=db_start.time(), key="tw_start_time", label_visibility="collapsed")
            window_start = datetime.combine(start_date, start_time)
        with col2:
            st.markdown("**End**")
            end_date = st.date_input("Date", value=db_end.date(), key="tw_end_date", label_visibility="collapsed")
            end_time = st.time_input("Time", value=db_end.time(), key="tw_end_time", label_visibility="collapsed")
            window_end = datetime.combine(end_date, end_time)

        if window_start >= window_end:
            st.warning("Start time must be before end time.")
            st.stop()

        if st.button("Load Time Window", use_container_width=True, type="primary", key="btn_load_time_window"):
            with st.spinner("Searching for production runs in time window..."):
                runs_df = get_runs_in_time_window(
                    selected_machine,
                    window_start,
                    window_end
                )

                if runs_df.empty:
                    st.error("❌ No production runs found in the selected time window.")
                    st.markdown(f"""
                    The time window **{window_start}** to **{window_end}** contains **no production runs**.

                    **Suggestions:**
                    - Try a wider time range
                    - Switch to **Production Run-based** mode to see when runs exist
                    - Wait for new production runs to be created
                    """)
                    st.stop()

                with st.spinner("Checking sensor data availability..."):
                    filtered_runs_df = filter_runs_by_available_data(selected_machine, runs_df)

                if filtered_runs_df.empty:
                    st.error("❌ Production runs found but no overlapping sensor data.")
                    st.stop()

                st.success(f"✅ Found {len(filtered_runs_df)} production runs with available sensor data!")
                st.session_state["analysis_runs"] = filtered_runs_df
                st.session_state.analysis_step = 3
                st.rerun()

        st.stop()
    else:
        st.caption(f"✅ {len(st.session_state['analysis_runs'])} production runs loaded in time window")

elif analysis_mode == "Production Run-based":
    st.markdown('<p class="cofi-section-title">Step 3: Select Production Run</p>', unsafe_allow_html=True)
    st.caption(f"All production runs for {selected_machine} with selected recipe parameters. Choose which run to analyze.")

    if st.button(
        "Load Runs",
        use_container_width=True,
        type="primary",
        key="btn_load_runs"
    ):
        with st.spinner("Loading production runs..."):
            runs_df = get_last_10_runs_for_machine_with_recipe(selected_machine, selected_recipe_params, limit=None)

            if runs_df.empty:
                st.error(f"❌ No production runs found for {selected_machine}")
                st.stop()
            
            # Filter to only show runs with available sensor data
            with st.spinner("Checking data availability..."):
                filtered_runs_df = filter_runs_by_available_data(selected_machine, runs_df)
            
            if filtered_runs_df.empty:
                st.error(f"❌ Data Gap: No production runs have corresponding sensor data")

                # Query database boundaries once for dynamic messaging
                db_info = {}
                try:
                    with get_engine().connect() as c:
                        bounds = pd.read_sql(
                            text("""
                                SELECT
                                    MIN(SourceTimestamp) as oldest_data,
                                    MAX(SourceTimestamp) as newest_data,
                                    COUNT(*) as total_rows
                                FROM MachineTagValue WITH (NOLOCK)
                                WHERE MachineCode = :machine
                            """),
                            c,
                            params={"machine": selected_machine}
                        )
                        if not bounds.empty and not pd.isna(bounds['oldest_data'].iloc[0]):
                            db_info['sensor_start'] = str(bounds['oldest_data'].iloc[0])
                            db_info['sensor_end'] = str(bounds['newest_data'].iloc[0])
                            db_info['sensor_count'] = int(bounds['total_rows'].iloc[0])

                        prod_runs = pd.read_sql(
                            text("""
                                SELECT
                                    MIN(StartTs) as oldest_run,
                                    MAX(EndTs) as newest_run,
                                    COUNT(*) as total_runs
                                FROM productionrun WITH (NOLOCK)
                                WHERE MachineCode = :machine
                            """),
                            c,
                            params={"machine": selected_machine}
                        )
                        if not prod_runs.empty and not pd.isna(prod_runs['oldest_run'].iloc[0]):
                            db_info['run_start'] = str(prod_runs['oldest_run'].iloc[0])
                            db_info['run_end'] = str(prod_runs['newest_run'].iloc[0])
                            db_info['run_count'] = int(prod_runs['total_runs'].iloc[0])
                except Exception as e:
                    db_info['error'] = str(e)

                sensor_start = db_info.get('sensor_start', 'N/A')
                sensor_end = db_info.get('sensor_end', 'N/A')
                run_start = db_info.get('run_start', 'N/A')
                run_end = db_info.get('run_end', 'N/A')

                st.markdown(f"""
                ### Why This Happened

                The production runs in the database span from **{run_start}** to **{run_end}**, but sensor data collection covers **{sensor_start}** to **{sensor_end}**. This means:

                - ✅ The database HAS production run records
                - ✅ The database HAS sensor data
                - ❌ But they don't overlap in time

                ### What to Do

                **Option 1: Use Recent Runs**
                - Check if there are any production runs from **{sensor_start}** onwards
                - Those runs would have corresponding sensor data

                **Option 2: Backfill Historical Data**
                - Import sensor data from before {sensor_start}
                - Then older production runs can be analyzed

                **Option 3: Check Back Later**
                - New production runs will be created in the future
                - When they are, there will be sensor data available
                """)

                with st.expander("📊 Database Time Range"):
                    if 'error' in db_info:
                        st.warning(f"Could not load database info: {db_info['error']}")
                    else:
                        st.info(f"**Sensor data available:** {sensor_start} to {sensor_end}")
                        st.info(f"**Total sensor records:** {db_info.get('sensor_count', 0):,}")
                        st.info(f"**Production runs available:** {run_start} to {run_end}")
                        st.info(f"**Total production runs:** {db_info.get('run_count', 0):,}")

                st.stop()
            
            st.success(f"✅ Loaded {len(filtered_runs_df)} production runs with available data!")
            st.session_state["analysis_runs"] = filtered_runs_df
            st.session_state.analysis_step = 3
            st.rerun()

# ── Continue only if runs are loaded ─────────────────────────────────────
if "analysis_runs" not in st.session_state:
    if st.session_state.get("analysis_mode") == "Time Window-based":
        st.info("👆 Click **'Load Time Window'** to continue.")
    else:
        st.info("👆 Click **'Load Runs'** to continue.")
    st.stop()

runs_df = st.session_state["analysis_runs"]

# Display runs nicely
run_display = runs_df.copy()
run_display["StartTs"] = run_display["StartTs"].dt.strftime("%Y-%m-%d %H:%M")
run_display["EndTs"] = run_display["EndTs"].dt.strftime("%Y-%m-%d %H:%M")

st.dataframe(
    run_display[["RunId", "StartTs", "EndTs", "RecipeIdentifier", "Status"]],
    use_container_width=True,
    hide_index=True
)



# ── Step 4: Select Runs for Sample Collection ────────────────────────────────
st.markdown("---")
st.markdown('<p class="cofi-section-title">Step 4: Select Runs for Sample Collection</p>', unsafe_allow_html=True)
is_time_window = st.session_state.get("analysis_mode") == "Time Window-based"
st.caption("Select from available data sources to collect samples." if is_time_window else "Select from the filtered production runs to collect samples.")

recent_runs = st.session_state.get("analysis_runs", pd.DataFrame())

if recent_runs.empty:
    st.error("No data source loaded. Please reload in Step 3.")
    st.stop()

recent_run_ids = recent_runs["RunId"].tolist()

select_all_runs = st.checkbox("Select All Runs", value=True, key="analysis_select_all")

if select_all_runs:
    selected_run_ids = recent_run_ids
    st.caption(f"✅ All **{len(selected_run_ids)}** runs will be used for sampling")
else:
    default_run_ids = [run_id for run_id in st.session_state.get("analysis_sample_run_ids", recent_run_ids[:3]) if run_id in recent_run_ids]
    selected_run_ids = st.multiselect(
        "Choose one or more runs for sample collection",
        options=recent_run_ids,
        default=default_run_ids,
        key="analysis_sample_run_ids",
        help="Select the runs that should contribute samples for the datasheet.",
    )

selected_runs = recent_runs[recent_runs["RunId"].isin(selected_run_ids)].copy()

if selected_runs.empty:
    if "analysis_sample_runs" in st.session_state:
        del st.session_state["analysis_sample_runs"]
    st.warning("Select at least one run before continuing with sample collection.")
    st.stop()

st.session_state["analysis_sample_runs"] = selected_runs

if "analysis_sample_runs" not in st.session_state:
    st.stop()

selected_runs = st.session_state["analysis_sample_runs"]
run_count = len(selected_runs)

selected_runs_display = selected_runs[["RunId", "StartTs", "EndTs", "RecipeIdentifier"]].copy()
selected_runs_display["StartTs"] = selected_runs_display["StartTs"].dt.strftime("%Y-%m-%d %H:%M")
selected_runs_display["EndTs"] = selected_runs_display["EndTs"].dt.strftime("%Y-%m-%d %H:%M")
st.dataframe(selected_runs_display, use_container_width=True, hide_index=True, height=min(150, 36 * run_count + 50))

# ── Step 5: Collect Samples & Generate Datasheet ─────────────────────────────
st.markdown("---")
st.markdown('<p class="cofi-section-title">Step 5: Collect Samples & Generate Datasheet</p>', unsafe_allow_html=True)
st.caption("Collect all parameter samples from the selected production runs and calculate statistics for the datasheet.")

if st.button(
    "Collect Samples & Generate Datasheet",
    use_container_width=True,
    type="primary",
    key="btn_generate_datasheet"
):
    # Samples per run: 1200 is optimal for historical analysis
    samples_per_run = 1200
    
    with st.spinner(f"Collecting {len(selected_monitoring_params)} parameters from {run_count} runs (max {samples_per_run:,} samples/run)..."):
        labeled_samples, quality_info = get_labeled_samples_from_runs(
            selected_machine,
            selected_runs,
            selected_monitoring_params,
            samples_per_run=samples_per_run
        )

    if labeled_samples.empty:
        st.error("❌ Sample collection failed")
        st.stop()
    
    # Show results
    total_samples = len(labeled_samples)
    ok_count = int((labeled_samples['IsOk'] == 1).sum())
    not_ok_count = total_samples - ok_count
    coll_stats = quality_info.get("collection_stats", {})

    # Metrics row
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Total Samples", f"{total_samples:,}")
    with metric_cols[1]:
        st.metric("Good (IsOk=1)", f"{ok_count:,}")
    with metric_cols[2]:
        st.metric("Not OK (IsOk=0)", f"{not_ok_count:,}")
    with metric_cols[3]:
        st.metric("Parameters Found", coll_stats.get('params_found', '?'))

    st.success(f"✅ **{total_samples:,} samples** ready for analysis")

    with st.spinner("Calculating parameter statistics from samples..."):
        statistics_df = calculate_recipe_parameter_statistics_from_samples(labeled_samples)

    # Exclude recipe parameters from datasheet (only analyse parameters)
    if not selected_recipe_params:
        pass
    else:
        removed_count = statistics_df['OpcNodeId'].isin(selected_recipe_params).sum()
        statistics_df = statistics_df[~statistics_df['OpcNodeId'].isin(selected_recipe_params)]
        if removed_count > 0:
            st.info(f"ℹ️ Excluded {removed_count} recipe parameter(s) from datasheet: {', '.join(selected_recipe_params)}")

    if statistics_df.empty:
        st.error("❌ No valid statistics computed from samples")
        st.stop()
    
    # Save datasheet
    recipe_key = f"custom_{'_'.join(p.split('.')[-1] for p in selected_recipe_params[:3])}"
    if len(recipe_key) > 255:
        recipe_key = recipe_key[:255]

    datasheet_run_id = save_datasheet_run(
        selected_machine,
        recipe_key,
        parameter_count=len(statistics_df),
        sample_count=total_samples,
        ok_count=ok_count,
        not_ok_count=not_ok_count
    )

    if datasheet_run_id is not None:
        success = save_recipe_datasheet(
            selected_machine,
            recipe_key,
            statistics_df,
            datasheet_run_id=datasheet_run_id
        )

        if success:
            st.session_state["analysis_results"] = {
                "machine": selected_machine,
                "recipe_key": recipe_key,
                "recipe_params": selected_recipe_params,
                "selected_param_count": len(selected_monitoring_params),
                "run_count": run_count,
                "total_samples": total_samples,
                "ok_samples": ok_count,
                "not_ok_samples": not_ok_count,
                "parameter_count": len(statistics_df),
                "timestamp": datetime.now(),
                "datasheet_run_id": datasheet_run_id,
                "statistics": statistics_df
            }
            st.success(f"🎉 Datasheet generated and saved as Run #{datasheet_run_id}!")

            st.markdown(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Add column showing which parameters are tagged as recipe
            recipe_params_str = ', '.join(selected_recipe_params) if selected_recipe_params else '—'
            statistics_df['RecipeParameters'] = recipe_params_str

            display_cols = [col for col in [
                'OpcNodeId', 'RecipeParameters', 'MinValue', 'OptimalValue',
                'MaxValue', 'MeanValue', 'StdDev', 'SampleCount',
                'QualityOkCount', 'QualityNotOkCount'
            ] if col in statistics_df.columns]

            display_df = statistics_df[display_cols].copy()
            for col in ['MinValue', 'OptimalValue', 'MaxValue', 'MeanValue', 'StdDev']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"{float(x):.4f}" if pd.notna(x) else "—")

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=min(600, 36 * len(display_df) + 50)
            )
        else:
            st.error("Failed to save datasheet to database.")
    else:
        st.error("Failed to create datasheet run entry.")