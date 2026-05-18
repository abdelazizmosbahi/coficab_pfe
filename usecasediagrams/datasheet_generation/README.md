# Datasheet Generation — Low-Level Use Case Decomposition

## Scope

This diagram decomposes the **Recipe-Aware Datasheet Generation** functional area. The Analyst uses a 6-step wizard (UCD4→UCD9) to generate parameter datasheets with quality correlation. Unlike real-time monitoring (which uses pre-computed analysis results), this module lets the Analyst manually select production runs, collect raw samples, and compute recipe-aware statistics split by OK/NOT OK quality labels. Source: `analysis_page.py` (653 lines) + `db_helpers.py`.

## Mapping to General Diagram

| General UC | Title | Sub-Diagram UC |
|---|---|---|
| UC13 | Generate Recipe Datasheet | UCD1 Generate Recipe Datasheet |
| UC14 | View Analysis History | UCD2 View Existing Datasheets + UCD3 View Analysis History |

*Note: The general diagram's UC14 "View Analysis History" is split into two distinct sub-use cases: viewing previously saved datasheets (UCD2) and viewing analysis run history (UCD3). They are independent read-only views on different DB tables.*

## Wizard Steps (UCD4–UCD9)

The 6-step wizard is a **sequential pipeline**: each step REQUIRES the previous step's output as context. All steps are modeled as `<<include>>` by UCD1 because without any single step, the datasheet cannot be generated.

### UCD4 — Select Machine (Step 1)

| | |
|---|---|
| **Goal** | Choose the target machine for datasheet generation |
| **Implementation** | `st.selectbox("Select Machine", load_all_machines())` (`analysis_page.py:226`) |
| **Output** | `selected_machine` stored in session state |
| **DB Helper** | `load_all_machines()` — queries `MachineTagValue` for distinct MachineCode values |

### UCD5 — Pick Recipe Parameters (Step 2)

| | |
|---|---|
| **Goal** | Select OPC Node IDs that define the recipe key (used as recipe identifier for the datasheet) |
| **Implementation** | `st.multiselect("Recipe Parameters (OPC NodeIds)", load_all_parameters_for_machine(selected_machine))` (`analysis_page.py:263`) |
| **Output** | `selected_recipe_params` — list of OPC NodeIds. First 3 used to build `recipe_key = f"custom_{'_'.join(...)}"` |
| **Precondition** | UCD4 must have completed (machine selected) |

### UCD6 — Load & Select Production Run (Step 3)

| | |
|---|---|
| **Goal** | Click a button to load the last 10 production runs for the machine, then select one run |
| **Implementation** | Button "Load Last 10 Runs" → `get_last_10_runs_for_machine(selected_machine)` queries `productionrun` table → `st.selectbox` to pick one run (`analysis_page.py:304`) |
| **Output** | `selected_run` dict with run ID and timestamps |
| **Precondition** | UCD5 must have completed (recipe params selected) |

### UCD7 — Discover Window Parameters (Step 4)

| | |
|---|---|
| **Goal** | Discover ALL distinct OPC NodeIds recorded in `MachineTagValue` during the selected run's time window |
| **Implementation** | `get_all_params_in_time_window(machine, startTs, endTs)` — timestamp-based query on `MachineTagValue` (no `ProductionRunId` dependency) (`analysis_page.py:345`) |
| **Output** | List of discovered parameters displayed in an expander for the Analyst to review |
| **Precondition** | UCD6 must have completed (run selected) |

### UCD8 — Select Sample Collection Runs (Step 5)

| | |
|---|---|
| **Goal** | Select one or more recent runs from which to collect raw samples |
| **Implementation** | `get_recent_runs_for_sample_collection(machine, limit=10)` → `st.multiselect` with the most recent runs (default: first 3 selected) (`analysis_page.py:365`) |
| **Output** | `selected_runs` — list of run dicts to use for sample collection |
| **Precondition** | UCD7 must have completed (parameters discovered) |

### UCD9 — Collect Samples & Compute Statistics (Step 6)

| | |
|---|---|
| **Goal** | The core step: collect up to 5,000 labeled samples per parameter per run, compute statistics, save to DB, and display the datasheet |
| **Button** | "Collect Samples & Generate Datasheet" |
| **Sub-steps** | UCD10 → UCD11 → UCD12 (executed sequentially) |
| **Output** | Datasheet DataFrame displayed with quality correlation summary. Downloadable as CSV via `st.download_button()` |

## Low-Level Use Cases

### UCD10 — Query Labeled Samples
*`<<include>>` by UCD9 (mandatory)*

| | |
|---|---|
| **Goal** | Retrieve up to 5,000 raw samples per parameter per selected run from `MachineTagValue`, labeled with quality status from `ProductionRunQuality` |
| **Implementation** | `get_labeled_samples_from_runs(machine, selected_params, selected_runs, max_samples=5000)` (`analysis_page.py:418`) |
| **Quality Labeling** | JOINs with `ProductionRunQuality` table on `ProductionRunId` to add `IsOk` column (1=OK, 0=NOT OK) |
| **Alternative** | If no matching `ProductionRunQuality` records → warning displayed but samples still collected (statistics without quality split) |

### UCD11 — Calculate Per-Parameter Statistics
*`<<include>>` by UCD9 (mandatory)*

| | |
|---|---|
| **Goal** | Compute MinValue, MaxValue, MeanValue, StdDev, and quality-split counts from the collected labeled samples |
| **Implementation** | `calculate_recipe_parameter_statistics_from_samples(label_df)` — groups by parameter, computes aggregate statistics, splits by OK/NOT OK quality labels (`analysis_page.py:453`) |
| **Output** | DataFrame with per-parameter statistics ready for DB insertion |

### UCD12 — Save Datasheet to DB
*`<<include>>` by UCD9 (mandatory)*

| | |
|---|---|
| **Goal** | Persist the computed statistics to `model_schema.parameter_reference_datasheet` |
| **Implementation** | `save_recipe_datasheet(machine, recipe_key, params_df)` — inserts rows into the datasheet table with machine code, recipe key, and per-parameter stats (`analysis_page.py:462`) |

### UCD13 — Load Datasheet from DB
*`<<include>>` by UCD2 (mandatory)*

| | |
|---|---|
| **Goal** | Load a previously saved recipe datasheet for the current machine+recipe key combination |
| **Implementation** | `load_recipe_datasheet(machine, recipe_key)` — SELECT from `parameter_reference_datasheet` WHERE MachineCode=:mc AND RecipeKey=:rk (`analysis_page.py:498`) |
| **Automatic** | Rendered automatically on every page load when `selected_recipe_params` is non-empty (no user action needed) |

### UCD14 — Load Analysis Run List
*`<<include>>` by UCD3 (mandatory)*

| | |
|---|---|
| **Goal** | Retrieve the list of analysis run sequences for the selected machine |
| **Implementation** | `get_analysis_runs(machine)` — queries `analysis_results_[MACHINE_CODE]` for distinct `RunSequence` values (`analysis_page.py:510`) |

### UCD15 — Load Run Details
*`<<include>>` by UCD3 (mandatory)*

| | |
|---|---|
| **Goal** | Load detailed per-parameter statistics for a specific analysis run sequence |
| **Implementation** | `get_analysis_result_table_name(machine)` → `load_analysis_results(table_name, run_sequence)` — SELECT from machine-specific analysis results table (`analysis_page.py:526-527`) |
| **Display** | DataFrame with: RunSequence, AnalysisTimestamp, ConfigurationName, OpcNodeId, MinValue, MeanValue, MaxValue, StdDev, SampleCount |

## Relationship Justification

### UCD4–UCD9 as `<<include>>` by UCD1

The 6 wizard steps are modeled as `<<include>>` because:
- Each step is mandatory — skipping any step leaves the datasheet incomplete
- Each step produces output consumed by the next step
- They represent the sequential decomposition of the generation workflow

**Caveat:** Unlike classic `<<include>>` (which implies independently reusable behavior), these steps are tightly coupled and context-dependent. Step 4 (UCD7) requires Step 3's run timestamps; Step 6 (UCD9) requires Step 5's selected runs. This is a "local decomposition" pattern, valid for illustrating internal flow within a single complex use case.

### UCD9 → UCD10 + UCD11 + UCD12

The sample collection step is further decomposed because:
- UCD10 (query samples) is a distinct DB-intensive operation with its own error path
- UCD11 (calculate statistics) is a pure computation step with no DB dependency
- UCD12 (save to DB) is a persistence step

These three sub-steps form a mini-pipeline within Step 6. All are mandatory — no alternative paths exist.

### Why No `<<extend>>`?

- CSV download is provided via `st.download_button()` within both UCD1 and UCD2 results (`analysis_page.py:623-631`), but it is a trivial one-liner (`df.to_csv()`) — not a complex behavioral extension worth modeling.
- The "No production runs" / "No parameters in window" alternative flows are error conditions within the wizard steps (UCD6, UCD7), not separate extension use cases.

### Why No Relationships Between UCD1, UCD2, UCD3?

These three are **independent display modes** on the same page:
- UCD1 generates NEW datasheets (write + read)
- UCD2 views EXISTING datasheets (read only, from `parameter_reference_datasheet`)
- UCD3 views past ANALYSIS runs (read only, from `analysis_results_[MACHINE_CODE]`)

They share no behavioral dependency. They are co-located on the same Streamlit page for analyst convenience, but each loads its own data through independent function calls.

## Authentication Prerequisite

All top-level use cases in this diagram `<<include>>` the **Authenticate** use case (UCAUTH) as a mandatory prerequisite. The Analyst must be authenticated before generating datasheets or viewing history. The system enforces this via `ensure_page_authentication()` at the top of `analysis_page.py:182`, which checks for a valid `auth_user_id` and `auth_token` in session state. If the check fails, the user is redirected to the Authentication page.

### Relationship Detail

| Source | Target | Type | Rationale |
|---|---|---|---|
| UCD1–UCD3 | UCAUTH | `<<include>>` | All datasheet generation and history viewing operations require an authenticated session. The Analyst cannot access the Analysis page without being logged in. |

## Key Implementation Details

| Aspect | Detail |
|---|---|
| **Machine Selection** | `load_all_machines()` from `MachineTagValue` |
| **Recipe Parameters** | Manual Analyst selection from available OPC Node IDs |
| **Production Runs** | `get_last_10_runs_for_machine()` — queries `productionrun` table |
| **Parameter Discovery** | `get_all_params_in_time_window()` — timestamp-based |
| **Sample Collection** | `get_labeled_samples_from_runs()` — ≤5,000 samples/param/run |
| **Quality Labeling** | `ProductionRunQuality` table — `IsOk` column (1=OK, 0=NOT OK) |
| **Statistics Engine** | `calculate_recipe_parameter_statistics_from_samples()` |
| **Storage** | `save_recipe_datasheet()` → `model_schema.parameter_reference_datasheet` |
| **Source File** | `cable_maintenance_ai/app/pages/analysis_page.py` (653 lines) |
