"""
Recipe-Aware Datasheet Generator Page

Flow:
1. Select Machine
2. Select Recipe Identifier
3. Select RunId from last 10 runs for that recipe
4. Discover ALL params in that run's time window (timestamp-based)
5. Select one or more recent runs for sample collection
6. Collect 5,000 samples per param per selected run → Generate datasheet
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import base64
from dotenv import load_dotenv
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_DIR = os.path.dirname(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_helpers import ensure_page_authentication, render_nav_bar  # noqa: E402
from db_helpers import (
    load_all_machines,
    load_all_parameters_for_machine,
    get_last_10_runs_for_machine_with_recipe,
    get_all_params_in_time_window,
    get_labeled_samples_from_runs,
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

# ── Step 2: Select Recipe Parameters ────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="cofi-section-title">Step 2: Select Recipe Parameters</p>', unsafe_allow_html=True)
st.caption("Pick parameters that define your recipe. These are used as a reference key — the datasheet will cover ALL parameters found in the selected run.")

all_parameters = load_all_parameters_for_machine(selected_machine)
if not all_parameters:
    st.warning(f"No parameters found for machine {selected_machine}.")
    st.stop()

selected_recipe_params = st.multiselect(
    "Select recipe parameters (OPC NodeIds):",
    options=all_parameters,
    format_func=lambda x: x.replace('_ACT', '').replace('_', ' '),
    key="analysis_recipe_multiselect",
)

if not selected_recipe_params:
    st.info("Select at least one parameter to continue.")
    st.stop()

# Update session state when recipe params change
if selected_recipe_params != st.session_state.analysis_recipe_params_selected:
    st.session_state.analysis_recipe_params_selected = selected_recipe_params
    st.session_state.analysis_step = 2
    # Clear downstream session state
    if "analysis_runs" in st.session_state:
        del st.session_state["analysis_runs"]
    if "analysis_sample_runs" in st.session_state:
        del st.session_state["analysis_sample_runs"]
    if "analysis_sample_run_ids" in st.session_state:
        del st.session_state["analysis_sample_run_ids"]
    if "analysis_run_sequence_selector" in st.session_state:
        del st.session_state["analysis_run_sequence_selector"]

# ── Step 3: Select Production Run (last 10) ─────────────────────────────────
st.markdown("---")
st.markdown('<p class="cofi-section-title">Step 3: Select Production Run</p>', unsafe_allow_html=True)
st.caption(f"Last 10 production runs for {selected_machine} with selected recipe parameters. Choose which run to analyze.")

if st.button(
    "Load Last 10 Runs",
    use_container_width=True,
    type="primary",
    key="btn_load_runs"
):
    runs_df = get_last_10_runs_for_machine_with_recipe(selected_machine, selected_recipe_params)

    if runs_df.empty:
        st.error(f"No production runs found for {selected_machine} with the selected recipe parameters.")
        st.stop()

    st.session_state["analysis_runs"] = runs_df
    st.session_state.analysis_step = 3

if "analysis_runs" not in st.session_state:
    st.stop()

runs_df = st.session_state["analysis_runs"]

run_display = runs_df.copy()
run_display["StartTs"] = run_display["StartTs"].dt.strftime("%Y-%m-%d %H:%M")
run_display["EndTs"] = run_display["EndTs"].dt.strftime("%Y-%m-%d %H:%M")

selected_run_label = st.selectbox(
    "Select a production run to analyze",
    options=run_display["RunId"].tolist(),
    key="analysis_run_selector",
    label_visibility="collapsed",
)

selected_run_row = run_display[run_display["RunId"] == selected_run_label].iloc[0]
selected_run_id = runs_df[runs_df["RunId"] == selected_run_row["RunId"]].iloc[0]

run_info_cols = st.columns(3)
with run_info_cols[0]:
    st.metric("Run ID", selected_run_row["RunId"])
with run_info_cols[1]:
    st.metric("Start Time", selected_run_row["StartTs"])
with run_info_cols[2]:
    st.metric("End Time", selected_run_row["EndTs"])

# ── Step 4: Discover Parameters ─────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="cofi-section-title">Step 4: Discover Parameters</p>', unsafe_allow_html=True)
st.caption("Finding all parameters recorded during this run's time window (timestamp-based, no ProductionRunId dependency).")

discovered_params = get_all_params_in_time_window(
    selected_machine,
    selected_run_id["StartTs"],
    selected_run_id["EndTs"]
)

if not discovered_params:
    st.warning("No parameters found in the selected run's time window.")
    st.stop()

st.info(f"Discovered **{len(discovered_params)}** parameters in the run window")

with st.expander("View discovered parameters", expanded=False):
    st.dataframe(pd.DataFrame({"OpcNodeId": discovered_params}), use_container_width=True, hide_index=True, height=300)

# ── Step 5: Select Runs for Sample Collection ────────────────────────────────
st.markdown("---")
st.markdown('<p class="cofi-section-title">Step 5: Select Runs for Sample Collection</p>', unsafe_allow_html=True)
st.caption("Select from the filtered production runs (last 10 for machine with recipe) to collect samples.")

# Use the filtered runs from Step 3 instead of fetching all recent runs
recent_runs = st.session_state.get("analysis_runs", pd.DataFrame())

if recent_runs.empty:
    st.error(f"No production runs available. Please reload the runs in Step 3.")
    st.stop()

recent_run_ids = recent_runs["RunId"].tolist()
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

# ── Step 6: Collect Samples & Generate Datasheet ─────────────────────────────
st.markdown("---")
st.markdown('<p class="cofi-section-title">Step 6: Collect Samples & Generate Datasheet</p>', unsafe_allow_html=True)

if st.button(
    "Collect Samples & Generate Datasheet",
    use_container_width=True,
    type="primary",
    key="btn_generate_datasheet"
):
    with st.spinner(f"Collecting up to 5,000 samples × {run_count} runs for {len(discovered_params)} parameters..."):
        try:
            labeled_samples, quality_info = get_labeled_samples_from_runs(
                selected_machine,
                selected_runs,
                discovered_params,
                samples_per_run=5000
            )

            if labeled_samples.empty:
                st.error("No parameter samples collected. Ensure data exists in the run time windows.")
            else:
                total_samples = len(labeled_samples)
                ok_count = int((labeled_samples['IsOk'] == 1).sum())
                not_ok_count = total_samples - ok_count

                with st.expander("Quality Diagnostics", expanded=True):
                    q_map = quality_info.get("quality_map", {})
                    st.markdown(f"**ProductionRunQuality lookup results:**")
                    st.markdown(f"- RunIds queried: {len(selected_runs)}")
                    st.markdown(f"- RunIds found in ProductionRunQuality: {len(quality_info.get('matched_runs', []))}")
                    st.markdown(f"- RunIds NOT found: {len(quality_info.get('missing_runs', []))}")
                    st.markdown(f"- Quality map: `{q_map}`")
                    st.markdown(f"- All IsOk values are 0: `{quality_info.get('all_zero', True)}`")

                    if quality_info.get("missing_runs"):
                        st.warning(f"RunIds not found in ProductionRunQuality: `{quality_info['missing_runs']}`")

                    if quality_info.get("all_zero"):
                        st.warning("All matched runs have IsOk=0. Check if the ProductionRunQuality table has correct data.")

                    if not q_map:
                        st.error("ProductionRunQuality table returned NO matching records. The table may be empty or RunId formats don't match.")

                st.info(f"Collected **{total_samples:,}** total samples ({ok_count:,} OK / {not_ok_count:,} NOT OK)")

                with st.spinner("Calculating statistics from labeled samples..."):
                    statistics_df = calculate_recipe_parameter_statistics_from_samples(labeled_samples)

                if statistics_df.empty:
                    st.error("No valid statistics computed from collected samples.")
                else:
                    recipe_key = f"custom_{'_'.join(p.split('.')[-1] for p in selected_recipe_params[:3])}"
                    if len(recipe_key) > 255:
                        recipe_key = recipe_key[:255]

                    # Save the datasheet run with execution timestamp
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
                            statistics_df
                        )

                        if success:
                            st.session_state["analysis_results"] = {
                                "machine": selected_machine,
                                "recipe_key": recipe_key,
                                "selected_run_id": selected_run_id["RunId"],
                                "recipe_params": selected_recipe_params,
                                "discovered_param_count": len(discovered_params),
                                "run_count": run_count,
                                "total_samples": total_samples,
                                "ok_samples": ok_count,
                                "not_ok_samples": not_ok_count,
                                "parameter_count": len(statistics_df),
                                "timestamp": datetime.now(),
                                "datasheet_run_id": datasheet_run_id,
                                "statistics": statistics_df
                            }
                            st.success(f"Datasheet generated and saved as Run #{datasheet_run_id}! {len(statistics_df)} parameters from {total_samples:,} samples across {run_count} selected runs.")
                        else:
                            st.error("Failed to save datasheet to database.")
                    else:
                        st.error("Failed to create datasheet run entry.")
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            import traceback
            st.error(traceback.format_exc())

# ── Display Results ──────────────────────────────────────────────────────────
if st.session_state.get("analysis_results"):
    results = st.session_state["analysis_results"]
    st.markdown("---")
    st.markdown('<p class="cofi-section-title">Generated Datasheet</p>', unsafe_allow_html=True)

    machine_label = results.get("machine", "—")
    recipe_label = results.get("recipe_key", "—")
    recipe_params_display = results.get("recipe_params", [])
    if recipe_params_display:
        recipe_label = ", ".join(p.split(".")[-1].replace("_ACT", "") for p in recipe_params_display[:3])
        if len(recipe_params_display) > 3:
            recipe_label += f" (+{len(recipe_params_display)-3})"

    meta_cols = st.columns(4)
    with meta_cols[0]:
        st.metric("Machine", machine_label)
    with meta_cols[1]:
        st.metric("Recipe Params", recipe_label)
    with meta_cols[2]:
        st.metric("Parameters", results["parameter_count"])
    with meta_cols[3]:
        if results.get("total_samples", 0) > 0:
            st.metric("Samples", f"{results['total_samples']:,}")
        elif results["timestamp"]:
            st.metric("Generated At", results["timestamp"].strftime("%Y-%m-%d %H:%M"))
        else:
            st.metric("Status", "Loaded (Existing)")

    if results.get("total_samples", 0) > 0:
        sample_cols = st.columns(3)
        with sample_cols[0]:
            st.metric("OK Samples", f"{results.get('ok_samples', 0):,}")
        with sample_cols[1]:
            st.metric("NOT OK Samples", f"{results.get('not_ok_samples', 0):,}")
        with sample_cols[2]:
            total = results.get("total_samples", 0)
            ok = results.get("ok_samples", 0)
            pct = (ok / total * 100) if total > 0 else 0
            st.metric("OK Percentage", f"{pct:.1f}%")

    st.markdown("---")

    stats_df = results["statistics"].copy()

    if "MachineCode" not in stats_df.columns:
        stats_df["MachineCode"] = results.get("machine", "")
    if "RecipeIdentifier" not in stats_df.columns:
        stats_df["RecipeIdentifier"] = results.get("recipe_key", "")

    # Display columns: MachineCode, RecipeIdentifier, OpcNodeId, and other statistics
    # Note: ParameterName is excluded since OpcNodeId provides the necessary identification
    first_cols = ["MachineCode", "RecipeIdentifier", "OpcNodeId"]
    other_cols = [c for c in stats_df.columns if c not in first_cols and c != "ParameterName"]
    stats_df = stats_df[first_cols + other_cols]

    for col in ["MinValue", "OptimalValue", "MaxValue", "MeanValue", "StdDev"]:
        if col in stats_df.columns:
            stats_df[col] = stats_df[col].apply(lambda x: f"{float(x):.4f}" if pd.notna(x) else "—")

    display_df = stats_df.copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=min(600, 36 * len(display_df) + 50)
    )

    with st.expander("Download Datasheet", expanded=False):
        csv = stats_df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"datasheet_{results['machine']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("**Quality Correlation Summary:**")

        if "QualityOkCount" in stats_df.columns and "QualityNotOkCount" in stats_df.columns:
            total_ok = stats_df["QualityOkCount"].sum()
            total_not_ok = stats_df["QualityNotOkCount"].sum()
            total_samples = total_ok + total_not_ok

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("OK Run Samples", f"{int(total_ok):,}")
            with col2:
                st.metric("NOT OK Run Samples", f"{int(total_not_ok):,}")
            with col3:
                ok_pct = (total_ok / total_samples * 100) if total_samples > 0 else 0
                st.metric("OK Percentage", f"{ok_pct:.1f}%")

            st.caption(
                f"Statistics calculated from {results.get('total_samples', 0):,} labeled samples across {results['run_count']} recent runs. "
                f"Up to 5,000 samples collected per run per parameter. "
                f"Optimal values are medians of OK-run samples."
            )
