# Configuration Management — Low-Level Use Case Decomposition

## Scope

This diagram decomposes the **Machine Configuration Management** functional area. The Analyst defines and maintains monitoring configurations. Low-level use cases represent the internal DB query and persistence behaviors that the top-level use cases depend on. Source: `configuration_page.py` (681 lines) + `db_helpers.py`.

## Mapping to General Diagram

| General UC | Title | Sub-Diagram UC |
|---|---|---|
| UC03 | View Machine Status | UCC1 View Machine Status |
| UC04 | Create Configuration | UCC2 Create Configuration |
| UC05 | View Configurations | UCC3 View Configurations |
| UC06 | Edit Configuration | UCC4 Edit Configuration |
| UC07 | Delete Configuration | UCC5 Delete Configuration |

## Low-Level Use Cases

### UCC6 — Browse Machine Registry
*`<<include>>` by UCC2, UCC3, UCC4, UCC5 (mandatory for each)*

| | |
|---|---|
| **Goal** | Retrieve the list of all known machine codes from `MachineTagValue` |
| **Implementation** | `load_all_machines()` — `SELECT DISTINCT MachineCode FROM MachineTagValue ORDER BY MachineCode` (`db_helpers`) |
| **Used By** | UCC2: populate machine selectbox in "Add Configuration" form. UCC3: populate machine filter in "View & Edit" tab. UCC4: populate machine selectbox in edit form (auto-selected to current machine). UCC5: populate machine filter in "Delete" tab. |
| **Caching** | `st.cache_data(ttl=300)` via `@st.cache_data` decorator on the function |

### UCC7 — Browse Parameter Catalog
*`<<include>>` by UCC2, UCC4 (mandatory for each)*

| | |
|---|---|
| **Goal** | Retrieve all OPC Node IDs available for a specific machine from `MachineTagValue` |
| **Implementation** | `load_all_parameters_for_machine(machine_code)` — `SELECT DISTINCT OpcNodeId FROM MachineTagValue WHERE MachineCode = :mc ORDER BY OpcNodeId` |
| **Used By** | UCC2: populate "Parameters to Monitor" multiselect. UCC4: repopulate multiselect with current selections as defaults. |
| **Relevance** | This is NOT used by UCC3 (View) because the view only displays saved configuration JSON; it does not reload all parameters from the DB. |

### UCC8 — Insert Configuration
*`<<include>>` by UCC2 (mandatory)*

| | |
|---|---|
| **Goal** | Persist a new configuration to `model_schema.machine_configuration` |
| **Implementation** | `add_machine_configuration(name, machine_code, monitoring_params, recipe_params, description)` — `INSERT INTO machine_configuration (...) VALUES (...)` |
| **Validation** | Before calling: name must be non-empty, machine must be selected, monitoring_params must be non-empty, recipe_params must be a subset of monitoring_params |
| **Post-action** | `st.balloons()`, set `st.session_state.refresh_configs = True`, `st.rerun()` |

### UCC9 — Fetch Configuration By ID
*`<<include>>` by UCC4 (mandatory)*

| | |
|---|---|
| **Goal** | Load a single configuration's full data from `model_schema.machine_configuration` by primary key |
| **Implementation** | `get_machine_configuration_by_id(config_id)` — `SELECT * FROM machine_configuration WHERE ConfigurationId = :id` |
| **Precondition** | User clicked "Edit" on a configuration in UCC3's view |
| **Output** | Dictionary with: ConfigurationId, ConfigurationName, MachineCode, MonitoringParameters (JSON string), RecipeParameters (JSON string), Description, IsActive, CreatedAt, UpdatedAt |

### UCC10 — Update Configuration
*`<<include>>` by UCC4 (mandatory)*

| | |
|---|---|
| **Goal** | Update an existing configuration's fields in the database |
| **Implementation** | `update_machine_configuration(config_id, name, machine_code, monitoring_params, recipe_params, description, is_active)` — `UPDATE machine_configuration SET ... WHERE ConfigurationId = :id` |
| **Validation** | Same rules as UCC8: name required, >=1 monitoring param, recipe subset of monitoring |

### UCC11 — Delete Configuration Record
*`<<include>>` by UCC5 (mandatory)*

| | |
|---|---|
| **Goal** | Permanently remove a configuration from the database |
| **Implementation** | `delete_machine_configuration(config_id)` — `DELETE FROM machine_configuration WHERE ConfigurationId = :id` |
| **Irreversible** | The Analyst must check "I understand this action is permanent" checkbox before the DELETE button is enabled |
| **Post-action** | `st.session_state.refresh_configs = True`, `st.success()` toast |

### UCC12 — Read Machine Status Data
*`<<include>>` by UCC1 (mandatory)*

| | |
|---|---|
| **Goal** | Determine operational status of all machines based on linespeed data freshness |
| **Implementation** | `get_machine_status_by_linespeed()` queries latest linespeed value per machine from `MachineTagValue`, classifies: 🟢 Working (data <3s old), 🟡 Standby (>3s), 🔴 Inactive (no data) |
| **Output** | Dict of `{MachineCode: {"value": float, "timestamp": datetime, "active": bool, "status_label": str, "age": str}}` |
| **Refresh** | Manual "Refresh Status" button calls this and `st.cache_data.clear()` |

### UCC13 — Load Configuration List
*`<<include>>` by UCC3 (mandatory)*

| | |
|---|---|
| **Goal** | Retrieve all saved configurations, optionally filtered by machine |
| **Implementation** | `load_machine_configurations(machine_code=None)` — `SELECT * FROM machine_configuration [WHERE MachineCode=:mc] ORDER BY CreatedAt DESC` |
| **Used By** | UCC3 only (populates the expander list) |

## Relationship Justification

| Source | Target | Type | Rationale |
|---|---|---|---|
| UCC1 | UCC12 | `<<include>>` | View Machine Status REQUIRES querying `MachineTagValue` for linespeed data. Without this, no status can be displayed. |
| UCC2 | UCC6 | `<<include>>` | Create Configuration REQUIRES listing machines so the Analyst can select one. |
| UCC2 | UCC7 | `<<include>>` | Create Configuration REQUIRES loading parameters for the selected machine so the Analyst can choose monitoring params. |
| UCC2 | UCC8 | `<<include>>` | Create Configuration REQUIRES persisting to DB after form validation. |
| UCC3 | UCC6 | `<<include>>` | View Configurations REQUIRES machine list for the optional filter dropdown. |
| UCC3 | UCC13 | `<<include>>` | View Configurations REQUIRES loading saved configs from DB. |
| UCC4 | UCC6 | `<<include>>` | Edit Configuration REQUIRES machine list in case Analyst wants to change the machine. |
| UCC4 | UCC7 | `<<include>>` | Edit Configuration REQUIRES loading parameters (parameters could have changed since creation). |
| UCC4 | UCC9 | `<<include>>` | Edit Configuration REQUIRES fetching the existing config by ID to pre-fill the form. |
| UCC4 | UCC10 | `<<include>>` | Edit Configuration REQUIRES updating the DB record after form validation. |
| UCC5 | UCC6 | `<<include>>` | Delete Configuration REQUIRES machine list for the filter dropdown. |
| UCC5 | UCC11 | `<<include>>` | Delete Configuration REQUIRES deleting the DB record. |

### Why No `<<extend>>`?

All variant flows in configuration management are error/validation paths within the same use case (e.g., "name is empty" → `st.error()` within UCC2), not independent optional behaviors. The `<<extend>>` relationship is reserved for cases where the extension is a standalone optional use case that inserts behavior at an explicit extension point — no such pattern exists in this functional area.

## Authentication Prerequisite

All top-level use cases in this diagram `<<include>>` the **Authenticate** use case (UCAUTH) as a mandatory prerequisite. The Analyst must be authenticated before performing any configuration management action. The system enforces this via `ensure_page_authentication()` at the top of `configuration_page.py:176`, which checks for a valid `auth_user_id` and `auth_token` in session state. If the check fails, the user is redirected to the Authentication page. This is a universal precondition documented in every use case table above.

### Relationship Detail

| Source | Target | Type | Rationale |
|---|---|---|---|
| UCC1–UCC5 | UCAUTH | `<<include>>` | Every configuration management action requires an authenticated session. The `<<include>>` captures the mandatory dependency — none of these use cases can execute without the Analyst being logged in. |

## Key Implementation Details

| Aspect | Detail |
|---|---|
| **Source Table** | `model_schema.machine_configuration` |
| **Key Columns** | ConfigurationId, ConfigurationName, MachineCode, MonitoringParameters (JSON), RecipeParameters (JSON), Description, IsActive, CreatedAt, UpdatedAt |
| **Machine Status Source** | `MachineTagValue` — linespeed-based freshness detection |
| **Status Threshold** | 3 seconds (configured via `LINESPEED_FRESHNESS_SECONDS`) |
| **Caching** | `st.cache_data(ttl=300)` for config list; manual "Refresh Status" button |
| **Source File** | `cable_maintenance_ai/app/pages/configuration_page.py` (681 lines) |
