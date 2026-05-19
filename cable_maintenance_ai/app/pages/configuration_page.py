"""
Cable Manufacturing Configuration Management Page
Configure machine parameters to monitor and designate recipe parameters.
Manage configurations with full CRUD operations.
"""

import streamlit as st
import pandas as pd
import os
import sys
import base64
from dotenv import load_dotenv

# Get base directory (2 levels up from this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_DIR = os.path.dirname(BASE_DIR)

# Load environment variables
load_dotenv(os.path.join(BASE_DIR, '.env'))

# MySQL helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_helpers import ensure_page_authentication, render_nav_bar  # noqa: E402
from db_helpers import (
    LINESPEED_FRESHNESS_SECONDS,
    load_all_machines,
    load_all_parameters_for_machine,
    load_machine_configurations,
    add_machine_configuration,
    update_machine_configuration,
    delete_machine_configuration,
    get_machine_configuration_by_id,
    initialize_machine_configuration_table,
    check_machine_active_status,
    get_machine_active_status_dict,
    get_machine_status_by_linespeed,
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
        /* Multiselect - Show full parameter names without truncation */
        [data-testid="stMultiSelect"] [data-baseweb="tag"] {
            max-width: none !important;
            white-space: normal !important;
            word-break: break-word !important;
            display: inline-block;
        }
        [data-testid="stMultiSelect"] [data-baseweb="tag"] > span {
            display: block !important;
            overflow: visible !important;
            text-overflow: unset !important;
            max-width: none !important;
            width: 100% !important;
        }
        [data-baseweb="tag"] span div {
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Machine Configuration",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ensure_page_authentication("pages/configuration_page.py")

apply_coficab_theme()

render_nav_bar(current_page="configuration_page")

logo_data_uri = ""
logo_path = os.path.join(ROOT_DIR, "coficab_logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as logo_file:
        logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
        logo_data_uri = f"data:image/png;base64,{logo_b64}"

hero_inner = """
    <div class="cofi-hero__text">
        <div class="cofi-eyebrow">CONFIGURATION MANAGER</div>
        <h1>Machine &amp; parameter configurations</h1>
        <p>Define monitoring and recipe parameters per machine. Status below reflects MachineTagValue connectivity.</p>
    </div>
"""
if logo_data_uri:
    hero_html = f'<div class="cofi-hero">{hero_inner}<img class="cofi-hero__logo" src="{logo_data_uri}" alt="Coficab logo" /></div>'
else:
    hero_html = f'<div class="cofi-hero">{hero_inner}</div>'
st.markdown(hero_html, unsafe_allow_html=True)

initialize_machine_configuration_table()

# Initialize cache for machine status on first load
if 'cached_machine_status' not in st.session_state:
    st.session_state.cached_machine_status = get_machine_status_by_linespeed()

# Use CACHED machine status for form controls (stable across interactions)
machine_status = st.session_state.cached_machine_status
active_machines = [m for m, info in machine_status.items() if info.get("active")]
has_active_machines = bool(active_machines)

st.markdown('<p class="cofi-section-title">🤖 Machine status</p>', unsafe_allow_html=True)

# Manual refresh button for machine status
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔄 Refresh Status", use_container_width=True, key="refresh_status_btn"):
        st.session_state.cached_machine_status = get_machine_status_by_linespeed()
        st.rerun()

with st.expander("📡 All machines — scrollable table", expanded=True):
    # Get live status for display
    current_status = st.session_state.cached_machine_status
    
    if current_status:
        rows = []
        for machine in sorted(current_status.keys()):
            info = current_status[machine]
            ls_val = info.get('linespeed_value')
            linespeed_display = f"{ls_val:.2f}" if ls_val is not None else "N/A"
            ts = info.get('linespeed_timestamp')
            age = info.get('linespeed_age_seconds')
            age_display = f"{age:.1f}s" if age is not None else "—"
            rows.append(
                {
                    "Machine": machine,
                    "Status": info["status"],
                    "LineSpeed": linespeed_display,
                    "Last Updated": ts or "—",
                    "Age": age_display,
                }
            )
        status_df = pd.DataFrame(rows)
        st.caption(
            f"{len(rows)} machine(s) — 🟢 Working | 🟡 Standby | 🔴 Inactive (stale >{LINESPEED_FRESHNESS_SECONDS}s)"
        )
        st.dataframe(
            status_df,
            use_container_width=True,
            hide_index=True,
            height=min(480, max(240, 36 * len(rows))),
        )
    else:
        st.warning("⚠️ No machines found. Ensure data is flowing into the MachineTagValue table.")

st.markdown("---")

# Initialize session state
if 'refresh_configs' not in st.session_state:
    st.session_state.refresh_configs = False
if 'editing_config_id' not in st.session_state:
    st.session_state.editing_config_id = None

# Show toast notifications from previous rerun
if st.session_state.pop("config_saved_toast", False):
    st.toast("Configuration saved successfully!", icon="✅")
if st.session_state.pop("config_updated_toast", False):
    st.toast("Configuration updated successfully!", icon="✅")
if st.session_state.pop("config_deleted_toast", False):
    st.toast("Configuration deleted successfully!", icon="✅")

# Create tabs for different operations
tab1, tab2, tab3 = st.tabs(["Add Configuration", "View & Edit", "Delete"])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1: Add New Configuration
# ──────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("➕ Add New Machine Configuration")
    st.info("ℹ️ The table above shows current machine status. You can configure any machine listed there.")
    
    all_machines_list = load_all_machines()
    # Create format function that shows machine with status icon
    def format_machine_option(machine):
        status_info = machine_status.get(machine, {})
        active = status_info.get("active", False)
        status_str = status_info.get("status", "🔴 Inactive")
        if active:
            status_icon = "🟢"
        elif "Standby" in status_str:
            status_icon = "🟡"
        else:
            status_icon = "🔴"
        return f"{status_icon} {machine}"
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        config_name = st.text_input(
            "Configuration Name",
            placeholder="e.g., 'Cable_Line_A_Standard'",
            help="Unique name for this configuration"
        )
    
    with col2:
        selected_machine = st.selectbox(
            "Select Machine",
            options=all_machines_list if all_machines_list else [],
            format_func=format_machine_option,
            help="Select a machine to configure (🟢 = Working, 🟡 = Standby, 🔴 = Inactive)"
        )
    
    # Load parameters for selected machine
    if selected_machine:
        parameters = load_all_parameters_for_machine(selected_machine)
        
        if not parameters:
            st.warning(f"⚠️ No parameters found for machine {selected_machine}")
            st.info("Ensure the machine has data in the MachineTagValue table")
        else:
            st.markdown("---")
            st.subheader("📊 Select Parameters to Monitor")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Parameters to Monitor**")
                monitoring_params = st.multiselect(
                    "Select all parameters you want to monitor for this machine:",
                    options=parameters,
                    format_func=lambda x: x.replace('_ACT', '').replace('_', ' '),
                    key="add_monitoring_params",
                    help="These parameters will be tracked and analyzed"
                )
            
            with col2:
                st.markdown("**Recipe Parameters**  \n*(subset of monitoring params)*")
                recipe_params = st.multiselect(
                    "Select which parameters are recipe parameters:",
                    options=monitoring_params if monitoring_params else parameters,
                    format_func=lambda x: x.replace('_ACT', '').replace('_', ' '),
                    key="add_recipe_params",
                    help="Parameters that are part of recipe definitions"
                )
            
            st.markdown("---")
            
            # Description
            description = st.text_area(
                "Configuration Description (Optional)",
                placeholder="Add any notes about this configuration...",
                height=100
            )
            
            # Save button
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button(
                    "💾 Save Configuration",
                    key="save_new_config",
                    use_container_width=True
                ):
                    # Validation
                    if not config_name.strip():
                        st.error("❌ Configuration name is required")
                    elif not selected_machine:
                        st.error("❌ Please select a machine")
                    elif not monitoring_params:
                        st.error("❌ Please select at least one parameter to monitor")
                    else:
                        # Check for invalid recipe parameters
                        invalid_recipes = [p for p in recipe_params if p not in monitoring_params]
                        if invalid_recipes:
                            st.error("❌ Recipe parameters must be a subset of monitoring parameters")
                        else:
                            # Save to database
                            if add_machine_configuration(
                                config_name=config_name,
                                machine_code=selected_machine,
                                monitoring_params=monitoring_params,
                                recipe_params=recipe_params,
                                description=description
                            ):
                                st.balloons()
                                st.session_state.refresh_configs = True
                                st.session_state["config_saved_toast"] = True
                                st.rerun()
                            else:
                                st.error("Failed to save configuration")
            
            with col2:
                if st.button("🔄 Clear Form", key="clear_form", use_container_width=True):
                    st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# TAB 2: View & Edit
# ──────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("📋 View & Edit Configurations")
    
    # Filter by machine
    all_machines = load_all_machines()
    filter_machine = st.selectbox(
        "Filter by Machine (optional)",
        options=["All Machines"] + all_machines,
        key="filter_machine_view"
    )
    
    # Load configurations
    if filter_machine == "All Machines":
        configs_df = load_machine_configurations()
    else:
        configs_df = load_machine_configurations(machine_code=filter_machine)
    
    if configs_df.empty:
        st.info("📭 No configurations found")
    else:
        # Display configurations in a formatted way
        for idx, config in configs_df.iterrows():
            with st.expander(
                f"🔧 {config['ConfigurationName']} | {config['MachineCode']} | "
                f"{'🟢 Configuration Active' if config['IsActive'] else '🔴 ConfigurationInactive'}",
                expanded=False
            ):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**Configuration Details**")
                    st.write(f"**ID:** {config['ConfigurationId']}")
                    st.write(f"**Machine:** {config['MachineCode']}")
                    st.write(f"**Created:** {config['CreatedAt']}")
                    st.write(f"**Updated:** {config['UpdatedAt']}")
                
                with col2:
                    st.markdown("**Parameters**")
                    monitoring = config['MonitoringParameters']
                    recipe = config['RecipeParameters']
                    
                    st.write(f"**Monitoring Parameters:** ({len(monitoring)})")
                    for param in monitoring:
                        is_recipe = "🔷 Recipe" if param in recipe else "📊 Monitor Only"
                        st.write(f"  • {param.replace('_ACT', '').replace('_', ' ')} {is_recipe}")
                
                if config['Description']:
                    st.write(f"**Description:** {config['Description']}")
                
                # Edit button
                if st.button(
                    "✏️ Edit Configuration",
                    key=f"edit_btn_{config['ConfigurationId']}",
                    use_container_width=True
                ):
                    st.session_state.editing_config_id = config['ConfigurationId']
                    st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# Editing Mode (overlaid on Tab 2)
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.editing_config_id is not None:
    st.markdown("---")
    st.subheader("✏️ Edit Configuration")

    config_data = get_machine_configuration_by_id(st.session_state.editing_config_id)

    if config_data:
        col1, col2 = st.columns([1, 1])

        with col1:
            edit_config_name = st.text_input(
                "Configuration Name",
                value=config_data['ConfigurationName'],
                key="edit_config_name"
            )

        with col2:
            edit_machine = st.selectbox(
                "Machine",
                options=all_machines,
                index=all_machines.index(config_data['MachineCode']) if config_data['MachineCode'] in all_machines else 0,
                key="edit_machine"
            )

        # Load parameters for machine
        parameters = load_all_parameters_for_machine(edit_machine)

        if parameters:
            st.markdown("---")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("**Parameters to Monitor**")
                edit_monitoring = st.multiselect(
                    "Select parameters to monitor:",
                    options=parameters,
                    default=config_data['MonitoringParameters'],
                    format_func=lambda x: x.replace('_ACT', '').replace('_', ' '),
                    key="edit_monitoring_params"
                )

            with col2:
                st.markdown("**Recipe Parameters**")
                # Build complete options: include both current monitoring params and any existing recipe params
                # This prevents accidentally dropping recipe params that aren't in the new monitoring selection
                recipe_options = list(dict.fromkeys(
                    (edit_monitoring if edit_monitoring else parameters) +
                    (config_data['RecipeParameters'] or [])
                ))
                edit_recipe = st.multiselect(
                    "Select recipe parameters:",
                    options=recipe_options,
                    default=config_data['RecipeParameters'],
                    format_func=lambda x: x.replace('_ACT', '').replace('_', ' '),
                    key="edit_recipe_params"
                )

            st.markdown("---")

            edit_description = st.text_area(
                "Description",
                value=config_data['Description'] or "",
                height=100,
                key="edit_description"
            )

            edit_is_active = st.checkbox(
                "Active",
                value=config_data['IsActive'],
                key="edit_is_active"
            )

            # Save and Cancel buttons
            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if st.button("💾 Update Configuration", key="update_config", use_container_width=True):
                    # Validation
                    if not edit_config_name.strip():
                        st.error("❌ Configuration name is required")
                    elif not edit_monitoring:
                        st.error("❌ Please select at least one parameter to monitor")
                    else:
                        invalid_recipes = [p for p in edit_recipe if p not in edit_monitoring]
                        if invalid_recipes:
                            st.error("❌ Recipe parameters must be a subset of monitoring parameters")
                        else:
                            if update_machine_configuration(
                                config_id=st.session_state.editing_config_id,
                                config_name=edit_config_name,
                                machine_code=edit_machine,
                                monitoring_params=edit_monitoring,
                                recipe_params=edit_recipe,
                                description=edit_description,
                                is_active=edit_is_active
                            ):
                                st.session_state["config_updated_toast"] = True
                                st.session_state.editing_config_id = None
                                st.rerun()

            with col2:
                if st.button("❌ Cancel", key="cancel_edit", use_container_width=True):
                    st.session_state.editing_config_id = None
                    st.rerun()
    else:
        st.error("❌ Configuration not found")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 3: Delete
# ──────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("🗑️ Delete Configuration")
    st.warning("⚠️ Deletion is permanent and cannot be undone!")
    
    # Filter by machine
    filter_machine_delete = st.selectbox(
        "Filter by Machine",
        options=["All Machines"] + all_machines,
        key="filter_machine_delete"
    )
    
    # Load configurations
    if filter_machine_delete == "All Machines":
        configs_to_delete = load_machine_configurations()
    else:
        configs_to_delete = load_machine_configurations(machine_code=filter_machine_delete)
    
    if configs_to_delete.empty:
        st.info("📭 No configurations found")
    else:
        config_to_delete = st.selectbox(
            "Select configuration to delete:",
            options=configs_to_delete.index,
            format_func=lambda idx: f"{configs_to_delete.loc[idx, 'ConfigurationName']} ({configs_to_delete.loc[idx, 'MachineCode']})",
            key="config_to_delete"
        )
        
        selected_config = configs_to_delete.loc[config_to_delete]
        
        with st.expander("📋 Configuration Details", expanded=True):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write(f"**Name:** {selected_config['ConfigurationName']}")
                st.write(f"**Machine:** {selected_config['MachineCode']}")
                st.write(f"**Created:** {selected_config['CreatedAt']}")
            
            with col2:
                monitoring = selected_config['MonitoringParameters']
                st.write(f"**Monitoring Parameters:** {len(monitoring)}")
                for param in monitoring[:5]:  # Show first 5
                    st.write(f"  • {param.replace('_ACT', '').replace('_', ' ')}")
                if len(monitoring) > 5:
                    st.write(f"  ... and {len(monitoring) - 5} more")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            confirm = st.checkbox(
                "I understand this action is permanent",
                key="delete_confirm"
            )
        
        with col2:
            if st.button(
                "🗑️ Delete Configuration",
                key="delete_config",
                disabled=not confirm,
                use_container_width=True
            ):
                if delete_machine_configuration(selected_config['ConfigurationId']):
                    st.session_state["config_deleted_toast"] = True
                    st.session_state.refresh_configs = True
                    st.rerun()
                else:
                    st.error("❌ Failed to delete configuration")


# Display summary statistics
st.markdown("---")
st.subheader("📊 Configuration Summary")

all_configs = load_machine_configurations()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Configurations", len(all_configs))

with col2:
    active_count = len(all_configs[all_configs['IsActive'] == True]) if not all_configs.empty else 0
    st.metric("Active Configurations", active_count)

with col3:
    unique_machines = all_configs['MachineCode'].nunique() if not all_configs.empty else 0
    st.metric("Machines Configured", unique_machines)