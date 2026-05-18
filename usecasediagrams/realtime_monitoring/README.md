# Real-Time Monitoring — Low-Level Use Case Decomposition

## Scope

This diagram decomposes the **Real-Time Monitoring & Quality Prediction** functional area — the most complex module (2382 lines in `model_page.py`). It encompasses notebook-based analysis, live parameter monitoring with 1-second auto-refresh, and historical traceability charts.

## Mapping to General Diagram

| General UC | Title | Sub-Diagram UC |
|---|---|---|
| UC08 | Execute Configuration Analysis | UCM1 Execute Config Analysis |
| UC09 | View Reference Datasheet | UCM2 View Reference Datasheet |
| UC10 | Monitor Real-Time Parameters | UCM3 Monitor Real-Time Parameters |
| UC11 | View Parameter Traceability | UCM4 View Parameter Traceability |

## Low-Level Use Cases

### UCM5 — Launch Papermill Notebook
*`<<include>>` by UCM1 (mandatory)*

| | |
|---|---|
| **Goal** | Execute `model_page.ipynb` with the selected configuration's ID via the Papermill library |
| **Implementation** | `pm.execute_notebook('notebooks/model_page.ipynb', temp_path, parameters=dict(configuration_id=config_id))` with 600-second timeout (`model_page.py:127`) |
| **Output** | An executed `.ipynb` file saved to a temp path with results in the last cell |
| **Alternative** | If notebook not found → `st.error("Analysis notebook not found at path: notebooks/model_page.ipynb")` |

### UCM6 — Extract Notebook Results
*`<<include>>` by UCM1 (mandatory)*

| | |
|---|---|
| **Goal** | Parse the executed notebook to extract the `results_export` JSON dict from the last cell's outputs |
| **Implementation** | `extract_results_from_notebook(notebook_path)` — reads `.ipynb` via `nbformat.read()`, iterates cells, finds the last code cell's `text/plain` output, parses with `json.loads()` (`model_page.py:59-86`) |
| **Output** | Dict with `reference_datasheets: {machine_code: {parameters: [...]}}`, `analysis_id`, `results_table`, etc. |

### UCM7 — Store Analysis Results to DB
*`<<include>>` by UCM1 (mandatory)*

| | |
|---|---|
| **Goal** | Persist the extracted analysis results into `model_schema.analysis_results` and `analysis_results_[MACHINE_CODE]` tables |
| **Implementation** | `store_analysis_results(results_export)` — inserts summary into `analysis_results` and per-parameter stats into `analysis_results_[MACHINE_CODE]` |
| **Precondition** | Notebook must have been executed successfully (UCM5) and results extracted (UCM6) |

### UCM8 — Load Reference Datasheet
*`<<include>>` by UCM2 (mandatory)*

| | |
|---|---|
| **Goal** | Load pre-computed parameter statistics (Min, Mean, Max, StdDev, SampleCount) from the latest analysis results for the current machine+config pair |
| **Implementation** | `_cached_load_reference_df(mc, config_id, analysis_results)` with `@st.cache_data(ttl=300)` → queries the analysis results table or falls back to `parameter_reference_datasheet` table (`model_page.py:687-724`) |
| **Output** | DataFrame with: OpcNodeId, MinValue, MeanValue, MaxValue, StdDev, SampleCount, Date_Analysed |
| **Post-action** | Data is filtered by config's monitoring parameters via `build_filtered_datasheet()` → displayed as a Datasheet table |

### UCM9 — Load Current Values from DB
*`<<include>>` by UCM3 (mandatory)*

| | |
|---|---|
| **Goal** | Fetch the latest value for each monitoring/recipe parameter from `MachineTagValue` |
| **Implementation** | `load_current_machine_values(mc, tag_params)` — queries `MachineTagValue` for the most recent timestamped value of each OPC NodeId for the given machine (`db_helpers:1551`) |
| **Frequency** | Called every 1 second inside `@st.fragment(run_every=1)` decorator on `render_monitoring_values()` (`model_page.py:1943`) |

### UCM10 — Compute Quality Score
*`<<include>>` by UCM3 (mandatory)*

| | |
|---|---|
| **Goal** | Aggregate per-parameter deviations into a single quality prediction percentage (0–100%) |
| **Implementation** | For each parameter: per-param score = `max(0, 100 - |deviation|/spread*50)`. Final score = average of all per-param scores + random variance (±1.5%). Thresholds: ≥80 🟢 EXCELLENT, ≥60 🟠 GOOD, <60 🔴 NEEDS ATTENTION (`model_page.py:1993-2025`) |
| **Location** | Inside `render_monitoring_values()` fragment, after `load_current_machine_values()` |

### UCM11 — Evaluate Per-Parameter Spec Status
*`<<include>>` by UCM3 (mandatory)*

| | |
|---|---|
| **Goal** | For each parameter, compare current value against the reference datasheet spec range and assign a status label |
| **Implementation** | STABLE (within range), NEAR MIN (within 5% of min), NEAR MAX (within 5% of max), OUT OF RANGE (beyond [min,max]) (`model_page.py:2131-2244`) |
| **Output** | Status badge displayed on each parameter card. If OUT OF RANGE, violation badge shows "% below min" or "% above max" |
| **Extension Points** | OUT OF RANGE parameters show 🔍 button → sets `st.session_state["fullscreen_rca_param"]` (triggers Root Cause Analysis diagram). All parameters show 📈 button → sets `st.session_state["fullscreen_param"]` (triggers UCM4) |

### UCM12 — Fetch Sliding-Window Data
*`<<include>>` by UCM4 (mandatory)*

| | |
|---|---|
| **Goal** | Retrieve the last ~3-4 seconds of MachineTagValue data for a single parameter, optimized with session state caching for zero-delay between refreshes |
| **Implementation** | `_get_cached_3second_data(mc, param)` — queries `MachineTagValue` for data > (now-4s), merges with `_3s_window_cache` in session state, trims to keep only most recent 3 seconds (`model_page.py:726-771`) |
| **Caller** | Called by UCM4's default "Quick View" rendering path |

### UCM13 — Fetch Full Historical Data
*`<<extend>>` UCM4 (conditional — triggered when Analyst toggles "Full Timeline" checkbox)*

| | |
|---|---|
| **Goal** | Load ALL historical MachineTagValue data for a parameter up to the toggle moment, cached in session state |
| **Implementation** | Queries `MachineTagValue` for all rows of the parameter, ordered by timestamp. Data is cached in `st.session_state["_full_timeline_cache"]` after first load (`model_page.py:887-1040`) |
| **Condition** | Only invoked when `st.session_state.get("fullscreen_show_full_timeline", False)` is True |
| **Extension Point** | The toggle checkbox is at `model_page.py:1539-1548`. When checked → `_render_full_timeline_incremental()` is called instead of `_render_3second_fast_trace()` |

### UCM14 — Render Traceability Chart
*`<<include>>` by UCM4 (mandatory)*

| | |
|---|---|
| **Goal** | Render a Plotly chart with actual values, spec range band, target mean line, and violation highlights |
| **Implementation** | Uses `plotly.graph_objects.Figure` with `add_trace(go.Scatter)` for data, `add_hrect` for spec range (green) and violation zones (red), `add_hline` for target mean (green dashed) (`model_page.py:774-1040` depending on view mode) |
| **Extension Point** | "Compare Parameters" — checkbox to overlay a second parameter on the same chart. If value ranges differ >5×, a secondary Y-axis is automatically created (`model_page.py:1084-1114`) |

## Relationship Justification

| Source | Target | Type | Rationale |
|---|---|---|---|
| UCM1 | UCM5 | `<<include>>` | Execute Analysis REQUIRES launching the Papermill notebook — the entire analysis derives from notebook execution |
| UCM1 | UCM6 | `<<include>>` | Results must be extracted from the notebook JSON output — no alternative path |
| UCM1 | UCM7 | `<<include>>` | Results must be persisted to DB for later viewing by UCM2 and UCM3 |
| UCM2 | UCM8 | `<<include>>` | Viewing the datasheet REQUIRES loading from analysis results DB table |
| UCM3 | UCM9 | `<<include>>` | Monitoring REQUIRES loading current values from MachineTagValue — without this, no data to display |
| UCM3 | UCM10 | `<<include>>` | Monitoring REQUIRES computing the quality score — it is always displayed |
| UCM3 | UCM11 | `<<include>>` | Monitoring REQUIRES evaluating each parameter's spec status — always performed |
| UCM4 | UCM12 | `<<include>>` | Traceability REQUIRES loading at least some data for the chart (default: 3-second window) |
| UCM4 | UCM14 | `<<include>>` | Traceability REQUIRES rendering a Plotly chart — both Quick View and Full Timeline modes call a chart renderer |
| UCM13 | UCM4 | `<<extend>>` | Full Timeline is an **optional alternative** to the default 3-second Quick View. The base UCM4 (which always loads 3-second data via UCM12) is complete without it. The extension fires only when the Analyst explicitly toggles the "Full Timeline" checkbox (`model_page.py:1539-1548`) |

### Why No `<<include>>` Between UCM1 and UCM2/UCM3?

Analysis execution (UCM1) is **not mandatory** for monitoring (UCM3). When no analysis results exist, monitoring still displays raw values without spec ranges (`model_page.py:1789-1807`). Similarly, UCM2 (View Datasheet) is a passive read-only view of pre-computed stats — it does not invoke UCM1.

## Authentication Prerequisite

All top-level use cases in this diagram `<<include>>` the **Authenticate** use case (UCAUTH) as a mandatory prerequisite. The Analyst must be authenticated before performing any monitoring or analysis action. The system enforces this via `ensure_page_authentication()` at the top of `model_page.py:1680`, which checks for a valid `auth_user_id` and `auth_token` in session state. If the check fails, the user is redirected to the Authentication page. This applies to every use case in this diagram.

### Relationship Detail

| Source | Target | Type | Rationale |
|---|---|---|---|
| UCM1–UCM4 | UCAUTH | `<<include>>` | All real-time monitoring and analysis operations require an authenticated session. The Analyst cannot access the Realtime page without being logged in. Monitoring, analysis, datasheet viewing, and traceability all depend on the authenticated identity for session management and page access control. |

## Key Implementation Details

| Aspect | Detail |
|---|---|
| **Auto-refresh** | `@st.fragment(run_every=1)` — only fragments rerun, not the full page |
| **Data Source** | `MachineTagValue` table (live OPC UA sensor data) |
| **Quality Score** | Average of per-param `max(0, 100 - \|deviation\|/spread*50)` + ±1.5% random variance |
| **3-Second Window** | Sliding window with session state cache (`_3s_window_cache`), drops oldest each refresh |
| **Full Timeline** | Static snapshot, loads all historical data once, cached in `_full_timeline_cache` |
| **Charting** | Plotly `go.Figure` with `add_hrect` for spec range highlighting |
| **Machine Detection** | Linespeed-based: <3s = 🟢 Working, stale = 🟡 Standby, absent = 🔴 Inactive |
| **Source File** | `cable_maintenance_ai/app/pages/model_page.py` (2382 lines) |
